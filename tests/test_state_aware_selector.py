"""Synthetic selector and dry-run checks; no benchmark evaluation or model use."""
import copy
import hashlib
import itertools
import json
from pathlib import Path
import subprocess
import sys
from types import SimpleNamespace

import pytest
from jsonschema import Draft202012Validator

from experiments.temporal_state_retrieval import state_aware_experiment as adapter
from experiments.temporal_state_retrieval.state_aware_selector import StateAwareSelector, validate_payload


def row(name, record, score):
    return {"chunk_id": "synthetic-" + name, "record_id": "TT-R" + f"{record:02}", "score": score}


def payload(section="current_intention", first=None, second=None, states=None):
    first = first if first is not None else [row("a", 1, .9), row("b", 2, .8), row("c", 3, .7)]
    second = second if second is not None else copy.deepcopy(first)
    records = {r["record_id"] for query in (first, second) for r in query}
    return {"section_id": section, "ordered_eligible_candidates": [first, second],
            "eligible_record_states": states if states is not None else {rid: "historical_record" for rid in records}}


@pytest.fixture(scope="module")
def bridge():
    return adapter.prepare_production_bridge()


@pytest.fixture
def selector(bridge):
    return StateAwareSelector(bridge[1])


@pytest.mark.parametrize("section", ["changes_and_reasons", "relevant_feedback", "possible_next_action"])
@pytest.mark.parametrize("order", list(itertools.permutations(range(3))))
def test_exact_production_baseline_equivalence_and_original_filter(section, order, bridge, monkeypatch):
    production, choose = bridge
    definition = next(d for d in production.SECTION_DEFINITIONS if d.section_id == section)
    values = [row("a", 1, .9), row("b", 2, .9), row("c", 3, .7)]
    def result(item, category):
        return SimpleNamespace(score=item["score"], chunk=SimpleNamespace(
            source=item["record_id"], category=category, chunk_id=item["chunk_id"]))
    queries = production.get_section_queries(definition)
    raw = [[result(values[i], definition.preferred_categories[0]) for i in order],
           [result(values[i], definition.preferred_categories[-1]) for i in reversed(order)]]
    for query in raw:
        query.insert(0, result(row("excluded", 4, 1), "not_an_allowed_category"))
    calls = list(zip(queries, raw))
    class Replay:
        def retrieve(self, query, top_k):
            assert top_k == 4
            return raw[queries.index(query)]
    expected = production.retrieve_diverse_evidence(definition, Replay(), total_chunks=4, limit=2)
    metadata = [{"record_id": f"TT-R{i:02}", "record_state": "current_snapshot"} for i in range(1, 5)]
    data, diagnostics = adapter.project_candidates(section, calls, definition,
        {r["record_id"]: r["record_id"] for r in values + [row("excluded", 4, 1)]}, metadata,
        production=production, eligible_record_ids={f"TT-R{i:02}" for i in range(1, 5)})
    observed = []
    original = production.retrieve_diverse_evidence
    def spy(*args, **kwargs):
        observed.append(True)
        return original(*args, **kwargs)
    monkeypatch.setattr(production, "retrieve_diverse_evidence", spy)
    assert StateAwareSelector(choose).select(data) == [x.chunk.chunk_id for x in expected]
    assert observed == [True] and diagnostics["missing_metadata_count"] == 0
    assert all(r["chunk_id"] != "synthetic-excluded" for q in data["ordered_eligible_candidates"] for r in q)


@pytest.mark.parametrize("section", ["current_intention", "unresolved_tensions"])
@pytest.mark.parametrize("state", ["current_snapshot", "final_snapshot", "closure_record"])
def test_snapshot_promotion_preserves_order_pool_scores_and_inputs(section, state, selector):
    data = payload(section)
    data["eligible_record_states"]["TT-R03"] = state
    original = copy.deepcopy(data)
    assert selector.select(data) == ["synthetic-c", "synthetic-a"]
    assert data == original
    adapter.assert_same_candidates(data, original["ordered_eligible_candidates"], source_channel=adapter.INPUT_CHANNEL)


@pytest.mark.parametrize("section", ["current_intention", "unresolved_tensions", "current_vs_superseded"])
@pytest.mark.parametrize("state", ["historical_record", "undated_record", "unknown"])
def test_no_snapshot_falls_back_exactly(section, state, selector, bridge):
    data = payload(section)
    data["eligible_record_states"] = {rid: state for rid in data["eligible_record_states"]}
    assert selector.select(data) == bridge[1](section, data["ordered_eligible_candidates"])


def test_s3_different_record_pair_without_text_or_roles(selector):
    data = payload("current_vs_superseded")
    data["eligible_record_states"]["TT-R03"] = "final_snapshot"
    assert selector.select(data) == ["synthetic-c", "synthetic-a"]


def test_s3_no_historical_record_uses_whole_baseline_pair(selector, bridge):
    data = payload("current_vs_superseded")
    data["eligible_record_states"] = {"TT-R01": "undated_record", "TT-R02": "unknown", "TT-R03": "closure_record"}
    assert selector.select(data) == bridge[1](data["section_id"], data["ordered_eligible_candidates"])


@pytest.mark.parametrize("section", ["current_intention", "current_vs_superseded", "unresolved_tensions"])
def test_duplicate_chunk_and_duplicate_record_different_chunk(section, selector):
    data = payload(section, [row("a", 1, .9), row("a", 1, .9), row("b", 1, .8), row("c", 2, .7)],
                   [row("a", 1, .95), row("b", 1, .8), row("c", 2, .7)],
                   {"TT-R01": "current_snapshot", "TT-R02": "historical_record"})
    assert selector.select(data) == (["synthetic-a", "synthetic-c"] if section == "current_vs_superseded" else ["synthetic-a", "synthetic-b"])


def test_stable_snapshot_ties_use_query_order_not_record_id(selector):
    data = payload(first=[row("z", 3, .8), row("a", 1, .8), row("b", 2, .8)],
                   states={"TT-R01": "final_snapshot", "TT-R02": "closure_record", "TT-R03": "current_snapshot"})
    assert selector.select(data) == ["synthetic-z", "synthetic-a"]


def test_union_fill_uses_state_partition_after_max_score_and_original_ties(selector):
    data = payload(first=[row("a", 1, .9), row("z", 3, .7), row("b", 2, .7)], second=[],
                   states={"TT-R01": "historical_record", "TT-R02": "final_snapshot", "TT-R03": "current_snapshot"})
    assert selector.select(data) == ["synthetic-z", "synthetic-b"]
    data["eligible_record_states"]["TT-R02"] = "historical_record"
    assert selector.select(data) == ["synthetic-z", "synthetic-a"]


@pytest.mark.parametrize("first,second", [([], []), ([row("a", 1, .2)], [row("a", 1, .8)]),
    ([row("a", 1, .2), row("a", 1, .2)], []), ([], [row("b", 2, -.2)])])
def test_empty_short_duplicate_inputs_bounded_and_deterministic(first, second, selector):
    data = payload(first=first, second=second)
    original = copy.deepcopy(data)
    outputs = [selector.select(data) for _ in range(5)]
    assert all(value == outputs[0] for value in outputs)
    assert len(outputs[0]) <= 2 and len(set(outputs[0])) == len(outputs[0])
    assert set(outputs[0]) <= {r["chunk_id"] for q in (first, second) for r in q}
    assert data == original


FORBIDDEN = ("case_id", "benchmark_tier", "expected_evidence_ids", "evidence_roles",
             "expected_temporal_status", "expected_support_status", "section_applicability",
             "baseline_pass_fail", "gold_labels", "rationale", "record_date",
             "sequence_position", "state_basis", "state_scope", "excerpt", "project_id")


@pytest.mark.parametrize("field", FORBIDDEN)
@pytest.mark.parametrize("boundary", ["root", "candidate", "state_mapping"])
def test_forbidden_fields_rejected_before_baseline(field, boundary):
    data = payload()
    if boundary == "root": data[field] = "sentinel"
    elif boundary == "candidate": data["ordered_eligible_candidates"][0][0][field] = "sentinel"
    else: data["eligible_record_states"]["TT-R01"] = {"record_state": "current_snapshot", field: "sentinel"}
    def forbidden(*args): raise AssertionError("Baseline must not receive leaked data")
    with pytest.raises(ValueError): StateAwareSelector(forbidden).select(data)


def test_chunk_cannot_change_record_identity(selector):
    data = payload()
    data["ordered_eligible_candidates"][1][0]["record_id"] = "TT-R02"
    with pytest.raises(ValueError, match="multiple records"): selector.select(data)


@pytest.mark.parametrize("score", [float("nan"), float("inf"), True])
def test_invalid_score_rejected(score):
    data = payload();data["ordered_eligible_candidates"][0][0]["score"] = score
    with pytest.raises(ValueError): validate_payload(data)


@pytest.mark.parametrize("change", ["score", "order", "delete", "add", "evaluation_channel"])
def test_adapter_rejects_candidate_pool_mutation(change):
    data = payload();original = copy.deepcopy(data["ordered_eligible_candidates"])
    channel = adapter.INPUT_CHANNEL
    if change == "score": data["ordered_eligible_candidates"][0][0]["score"] = .01
    elif change == "order": data["ordered_eligible_candidates"][0].reverse()
    elif change == "delete": data["ordered_eligible_candidates"][0].pop()
    elif change == "add": data["ordered_eligible_candidates"][0].append(row("d", 3, .1))
    else: channel = "ordered_evidence"
    with pytest.raises(ValueError): adapter.assert_same_candidates(data, original, source_channel=channel)


def test_missing_metadata_becomes_unknown_without_candidate_removal_and_conflicts_rejected(bridge):
    production, _ = bridge
    definition = production.SECTION_DEFINITIONS[2]
    result = SimpleNamespace(score=.5, chunk=SimpleNamespace(source="synthetic-source", category="process", chunk_id="synthetic-a"))
    calls = [(q, [result]) for q in production.get_section_queries(definition)]
    kwargs = dict(production=production, eligible_record_ids={"TT-R01"})
    data, notes = adapter.project_candidates(definition.section_id, calls, definition, {"synthetic-source": "TT-R01"}, [], **kwargs)
    assert data["eligible_record_states"] == {"TT-R01": "unknown"}
    assert notes == {"missing_metadata_count": 1, "missing_record_ids": ["TT-R01"]}
    assert len(data["ordered_eligible_candidates"][0]) == 1
    # A single record cannot validly be both snapshot and historical. Do not
    # manufacture that impossible S3 input; reject conflicting annotation rows.
    records = [{"record_id": "TT-R01", "record_state": s} for s in ("current_snapshot", "historical_record")]
    with pytest.raises(ValueError, match="Duplicate metadata"):
        adapter.project_candidates(definition.section_id, calls, definition, {"synthetic-source": "TT-R01"}, records, **kwargs)
    kwargs["eligible_record_ids"] = set()
    with pytest.raises(ValueError, match="eligible view"):
        adapter.project_candidates(definition.section_id, calls, definition, {"synthetic-source": "TT-R01"}, [], **kwargs)


def test_runtime_payload_matches_frozen_closed_schema():
    root = Path(__file__).resolve().parents[1]
    schema = json.loads((root / "tests/fixtures/temporal_state_metadata/record_metadata.schema.json").read_text())
    schema["$ref"] = "#/$defs/selector_input"
    schema = {k: schema[k] for k in ("$schema", "$defs", "$ref")}
    Draft202012Validator(schema).validate(payload())


def test_import_is_side_effect_free_without_runtime_dependencies(tmp_path):
    script = '''
import sys, os, json
before=(list(sys.path),os.getcwd(),dict(os.environ))
def audit(event,args):
 if event=='open' and isinstance(args[1],str) and any(v in args[1] for v in 'wax+'):raise AssertionError('write')
 if event=='import' and args[0].split('.')[0] in ('retrieval','sentence_transformers','torch','openai','llm_summarizer'):raise AssertionError('runtime import')
sys.addaudithook(audit)
import experiments.temporal_state_retrieval.state_aware_selector
import experiments.temporal_state_retrieval.state_aware_experiment
assert before==(list(sys.path),os.getcwd(),dict(os.environ))
assert not any(k in sys.modules for k in ('retrieval','sentence_transformers','openai','llm_summarizer'))
print('IMPORT_OK')
'''
    result = subprocess.run([sys.executable, "-B", "-c", script], text=True, capture_output=True, check=True)
    assert result.stdout.strip() == "IMPORT_OK"


@pytest.mark.parametrize("section", ["current_vs_superseded", "changes_and_reasons"])
def test_actual_isolated_worker_denies_metadata_file_and_network_access(section, selector):
    data = payload(section);data["eligible_record_states"]["TT-R03"] = "final_snapshot"
    assert adapter.run_isolated(data, probe_boundary=True) == selector.select(data)


def digest(raw): return hashlib.sha256(raw).hexdigest()


def freeze_bytes(data):
    data["self_digest"] = {"method": "synthetic canonical check"}
    data["self_digest"]["sha256"] = digest(json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode())
    return (json.dumps(data, indent=2) + "\n").encode()


@pytest.fixture
def dry_fixture(tmp_path, monkeypatch):
    # Opaque, deliberately invalid JSON gold: validation may hash but not parse it.
    private = tmp_path / "private_data";private.mkdir()
    bindings = {}
    for label in adapter.PRIVATE_LABELS:
        p = private / (label + ".json");p.write_bytes(b"synthetic opaque bytes")
        bindings[label] = p
    manifest_path = "tests/fixtures/temporal_state_metadata/freeze_manifest.json"
    public = {"version": adapter.FREEZE_VERSION, "status": "researcher_confirmed",
              "private_metadata_commitment": {"sha256": digest(bindings["record_metadata"].read_bytes())},
              "phase_1_original_benchmark_criteria": {"synthetic": 1},
              "phase_3_candidate_improvement_criteria": {"synthetic": 2}}
    for name in adapter.REQUIRED_PUBLIC_PATHS:
        p = tmp_path / name;p.parent.mkdir(parents=True, exist_ok=True);p.write_bytes(b"synthetic opaque bytes")
    (tmp_path / manifest_path).write_bytes(freeze_bytes(public))
    views = {f"synthetic-{i}": {"documents": 1, "chunks": 2} for i in range(4)}
    (tmp_path / "outputs/test_results/temporal_state_retrieval_baseline/run_manifest.json").write_text(json.dumps({"corpus_views": views}))
    public_hash = digest((tmp_path / manifest_path).read_bytes())
    private_data = {"version": adapter.FREEZE_VERSION, "status": "researcher_confirmed", "public_manifest": {"sha256": public_hash}}
    bindings["metadata_manifest"].write_bytes(freeze_bytes(private_data))
    monkeypatch.setattr(adapter, "PUBLIC_FREEZE_SHA256", public_hash)
    monkeypatch.setattr(adapter, "PRIVATE_FREEZE_SHA256", digest(bindings["metadata_manifest"].read_bytes()))
    plan = {"HEAD": adapter.FREEZE_COMMIT, "freeze_commit": adapter.FREEZE_COMMIT, "branch": "synthetic-branch", "freeze_version": adapter.FREEZE_VERSION,
            "status": "implementation_ready_pending_review", "execution_authorised": False,
            "metadata_manifest_path": manifest_path, "one_shot_rules": list(adapter.ONE_SHOT_RULES),
            "public_artifacts": [{"path": n, "sha256": digest((tmp_path / n).read_bytes())} for n in sorted(adapter.REQUIRED_PUBLIC_PATHS)],
            "private_commitments": {label: digest(path.read_bytes()) for label, path in bindings.items()},
            "phase_1_original_benchmark_criteria": public["phase_1_original_benchmark_criteria"],
            "phase_3_candidate_improvement_criteria": public["phase_3_candidate_improvement_criteria"],
            "intended_views": views,
            "intended_case_counts": {"production": 18, "diagnostic": 16}}
    monkeypatch.setattr(adapter, "_git_state", lambda root: (adapter.FREEZE_COMMIT, "synthetic-branch"))
    monkeypatch.setattr(adapter, "_has_freeze_ancestor", lambda root, head: True)
    return tmp_path, plan, bindings


def test_dry_preflight_hashes_without_parsing_gold_or_writing(dry_fixture):
    root, plan, bindings = dry_fixture
    before = {p: p.read_bytes() for p in root.rglob("*") if p.is_file()}
    result = adapter.dry_construction(root, plan, bindings)
    assert result["validated"] and not result["execution_authorised"] and not result["lock_written"]
    assert result["stages"].index("isolated_selection") < result["stages"].index("score_after_selection_separate_tiers")
    assert before == {p: p.read_bytes() for p in root.rglob("*") if p.is_file()}


@pytest.mark.parametrize("mutation", ["HEAD", "branch", "freeze_version", "public_hash", "private_hash", "missing_commitment", "criteria", "counts", "views", "execution"])
def test_preflight_rejects_drift(dry_fixture, mutation):
    root, plan, bindings = dry_fixture
    if mutation in ("HEAD", "branch", "freeze_version"): plan[mutation] = "wrong"
    elif mutation == "public_hash": (root / plan["public_artifacts"][0]["path"]).write_bytes(b"changed")
    elif mutation == "private_hash": bindings["record_metadata"].write_bytes(b"changed")
    elif mutation == "missing_commitment": plan["public_artifacts"].pop()
    elif mutation == "criteria": plan["phase_3_candidate_improvement_criteria"] = {}
    elif mutation == "counts": plan["intended_case_counts"]["production"] = 1
    elif mutation == "views": plan["intended_views"]["synthetic-0"]["chunks"] = 9
    else: plan["execution_authorised"] = True
    messages = {"HEAD": "Git checkpoint", "branch": "Git checkpoint", "freeze_version": "plan/version",
                "public_hash": "Public artifact hash", "private_hash": "Private artifact hash",
                "missing_commitment": "required public commitment", "criteria": "success criteria",
                "counts": "evaluation population", "views": "evaluation population", "execution": "Execution policy"}
    with pytest.raises(ValueError, match=messages[mutation]): adapter.validate_preflight(root, plan, bindings)


def test_preflight_refuses_private_paths_before_reading(dry_fixture):
    root, plan, bindings = dry_fixture
    plan["public_artifacts"].append({"path": "data/study_projects/forbidden/file.json", "sha256": "0" * 64})
    with pytest.raises(ValueError, match="public artifact path"):
        adapter.validate_preflight(root, plan, bindings)


def test_one_shot_stops_on_pre_score_failure_or_consumption_and_formal_run_disabled():
    for consumed in (False, True):
        lifecycle = adapter.RunLifecycle();lifecycle.lock_created()
        if consumed: lifecycle.first_case_score()
        lifecycle.technical_failure()
        assert lifecycle.state == ("consumed" if consumed else "stopped_before_scores_requires_review")
        with pytest.raises(RuntimeError): lifecycle.lock_created()
    with pytest.raises(RuntimeError, match="disabled"): adapter.execute_evaluation()
