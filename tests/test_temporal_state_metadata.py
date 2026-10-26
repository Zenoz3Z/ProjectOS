"""Static preregistration checks; no retrieval, model, source mutation or private reads."""
import ast
import copy
from datetime import datetime
import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker, ValidationError
import pytest


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "tests/fixtures/temporal_state_metadata"


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def validator():
    return Draft202012Validator(read_json(PACKAGE / "record_metadata.schema.json"), format_checker=FormatChecker())


def validate_package(data, inventory):
    validator().validate(data)
    rows = data["records"]
    ids = [r["record_id"] for r in rows]
    assert len(ids) == len(set(ids)), "duplicate record ID"
    assert len({r["project_id"] for r in rows}) == 1, "mixed projects"
    project = rows[0]["project_id"]
    expected = {r["record_id"]: r for r in inventory if r["project_id"] == project}
    assert set(ids) == set(expected), "record coverage mismatch"
    for row in rows:
        source = expected[row["record_id"]]
        for field in ("project_id", "source_category", "record_date", "sequence_position"):
            assert row[field] == source[field], field


def validate_view(view, inventory):
    records = {r["record_id"]: r for r in inventory if r["project_id"] == view["project_id"]}
    eligible = view["eligible_record_ids"]
    assert len(eligible) == len(set(eligible)), "duplicate eligible ID"
    assert set(eligible) <= records.keys(), "cross-project or missing record"
    assert view["as_of_record"] in eligible, "anchor excluded"
    if view["reference_state"] == "latest_project_state":
        assert set(eligible) == records.keys(), "incomplete latest corpus"
    else:
        cutoff = records[view["as_of_record"]]
        assert cutoff["record_date"] is not None, "undated historical cutoff"
        for rid in eligible:
            record = records[rid]
            assert record["record_date"] is not None, "unproved undated availability"
            assert record["record_date"] <= cutoff["record_date"], "future date"
            assert record["sequence_position"] <= cutoff["sequence_position"], "future ordinal"


@pytest.fixture
def manifest():
    return read_json(PACKAGE / "freeze_manifest.json")


@pytest.fixture
def echo():
    return read_json(PACKAGE / "echo_field.metadata.json")


def test_schema_is_valid_and_requires_only_the_eight_document_fields():
    schema = read_json(PACKAGE / "record_metadata.schema.json")
    Draft202012Validator.check_schema(schema)
    record = schema["$defs"]["record"]
    assert set(record["required"]) == set(record["properties"]) == {
        "record_id", "project_id", "record_state", "record_date", "sequence_position",
        "state_basis", "state_scope", "source_category",
    }
    assert record["additionalProperties"] is False


@pytest.mark.parametrize("name,count", [("echo_field.metadata.json", 4), ("signal_loom.metadata.json", 7)])
def test_public_packages_complete_confirmed_and_source_consistent(name, count, manifest):
    data = read_json(PACKAGE / name)
    validate_package(data, manifest["public_source_inventory"])
    assert len(data["records"]) == count
    assert data["review_status"] == "researcher_confirmed"
    assert data["metadata_version"] == "phase_3a_metadata_v1"
    assert data["reviewed_by"] == "Fuzhe Zhang" and data["review_date"] == "2026-10-26"


@pytest.mark.parametrize("field", [
    "expected_evidence_ids", "evidence_role", "expected_temporal_status", "support_status",
    "section_applicability", "benchmark_pass_fail", "baseline_rank", "case_id",
])
def test_gold_and_result_fields_rejected(field, echo):
    echo["records"][0][field] = "forbidden"
    with pytest.raises(ValidationError):
        validator().validate(echo)


def test_missing_record_field_review_provenance_and_draft_status_rejected(echo):
    missing = copy.deepcopy(echo)
    del missing["records"][0]["state_scope"]
    with pytest.raises(ValidationError):
        validator().validate(missing)
    missing_review = copy.deepcopy(echo)
    del missing_review["reviewed_by"]
    with pytest.raises(ValidationError):
        validator().validate(missing_review)
    echo["review_status"] = "pending_researcher_review"
    with pytest.raises(ValidationError):
        validator().validate(echo)


@pytest.mark.parametrize("state", ["superseded", "unresolved", "next_action"])
def test_fragment_states_cannot_be_whole_record_metadata(state, echo):
    echo["records"][0]["record_state"] = state
    with pytest.raises(ValidationError):
        validator().validate(echo)


def test_unknown_remains_valid_without_invented_dates(echo):
    echo["records"][0].update(record_state="unknown", state_basis="unknown", record_date=None)
    validator().validate(echo)


@pytest.mark.parametrize("date,basis", [("2026-02-30", "explicit_heading"), ("2026-10-26", "explicit_heading"), (None, "explicit_date")])
def test_invalid_or_incompatible_date_metadata_rejected(date, basis, echo):
    echo["records"][0].update(record_date=date, state_basis=basis)
    with pytest.raises(ValidationError):
        validator().validate(echo)


def test_duplicate_records_and_missing_records_rejected(echo, manifest):
    inventory = manifest["public_source_inventory"]
    duplicate = copy.deepcopy(echo)
    duplicate["records"].append(copy.deepcopy(duplicate["records"][0]))
    with pytest.raises(AssertionError, match="duplicate"):
        validate_package(duplicate, inventory)
    echo["records"].pop()
    with pytest.raises(AssertionError, match="coverage"):
        validate_package(echo, inventory)


@pytest.mark.parametrize("field,value", [("project_id", "another_project"), ("source_category", "feedback"), ("sequence_position", 99)])
def test_identity_category_and_ordinal_cannot_be_reassigned(field, value, echo, manifest):
    echo["records"][0][field] = value
    with pytest.raises(AssertionError):
        validate_package(echo, manifest["public_source_inventory"])


def test_public_source_hashes_dates_and_category_are_directly_verifiable(manifest):
    for row in manifest["public_source_inventory"]:
        path = ROOT / row["path"]
        assert hashlib.sha256(path.read_bytes()).hexdigest() == row["sha256"]
        assert path.parent.name == row["source_category"]
        text = path.read_text(encoding="utf-8")
        dates = [datetime.strptime(line[6:].strip(), "%d %B %Y").date().isoformat()
                 for line in text.splitlines() if line.startswith("Date: ")]
        assert (dates[-1] if dates else None) == row["record_date"]


def test_public_views_exactly_preserve_frozen_context_boundaries(manifest):
    original = read_json(ROOT / "tests/fixtures/temporal_state_benchmark/public_benchmark.json")
    # Project/context identity only; no case or passage annotations are used.
    fields = ("context_id", "project_id", "reference_state", "as_of_record", "eligible_record_ids")
    expected = [{k: c[k] for k in fields} for c in original["contexts"]]
    assert manifest["public_views"] == expected
    for view in manifest["public_views"]:
        validate_view(view, manifest["public_source_inventory"])


@pytest.mark.parametrize("extra", ["SY-R06", "SY-R07"])
def test_historical_view_rejects_unplaced_or_future_records(extra, manifest):
    view = copy.deepcopy(next(v for v in manifest["public_views"] if v["reference_state"] == "historical_snapshot"))
    view["eligible_record_ids"].append(extra)
    with pytest.raises(AssertionError, match="unproved|future"):
        validate_view(view, manifest["public_source_inventory"])


def test_latest_view_cannot_hide_a_difficult_record(manifest):
    view = copy.deepcopy(next(v for v in manifest["public_views"] if v["context_id"] == "signal_closed"))
    view["eligible_record_ids"].remove("SY-R06")
    with pytest.raises(AssertionError, match="incomplete"):
        validate_view(view, manifest["public_source_inventory"])


def test_full_pool_and_six_section_contract_without_running_selection(manifest):
    contract = manifest["selection_contract"]
    assert contract["query_top_k"] == "total_chunks_in_frozen_eligible_view"
    assert contract["max_selected"] == 2
    assert contract["category_filter"] == "unchanged_production"
    assert contract["rule_by_section"] == {
        "current_intention": "snapshot_family_preference",
        "changes_and_reasons": "baseline_unchanged",
        "current_vs_superseded": "cross_document_function_pair_or_baseline",
        "relevant_feedback": "baseline_unchanged",
        "unresolved_tensions": "snapshot_family_preference",
        "possible_next_action": "baseline_unchanged",
    }
    tree = ast.parse((ROOT / "src/reentry_brief.py").read_text(encoding="utf-8"))
    queries = next(ast.literal_eval(n.value) for n in tree.body if isinstance(n, ast.Assign)
                   and any(isinstance(t, ast.Name) and t.id == "SECTION_RETRIEVAL_QUERIES" for t in n.targets))
    assert set(queries) == set(contract["rule_by_section"])
    assert all(len(q) == 2 for q in queries.values())
    assert contract["selector_input_fields"] == ["section_id", "ordered_eligible_candidates", "eligible_record_states"]


def test_latency_threshold_is_saved_baseline_times_two(manifest):
    baseline = read_json(ROOT / "outputs/test_results/temporal_state_retrieval_baseline/aggregate_results.json")
    median = baseline["tiers"]["production"]["latency"]["warm"]["median_ms"]
    assert manifest["success_gate"]["production_warm_median_limit_ms"] == 2 * median
    assert manifest["success_gate"]["all_required_roles_minimum"] == [10, 15]
    assert manifest["success_gate"]["allowed_lost_baseline_passes"] == 0


def test_frozen_manifest_covers_public_files_and_has_valid_self_digest(manifest):
    data = copy.deepcopy(manifest)
    claimed = data["self_digest"].pop("sha256")
    encoded = json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    assert hashlib.sha256(encoded).hexdigest() == claimed
    assert manifest["status"] == "researcher_confirmed"
    assert manifest["version"] == "phase_3a_metadata_v1"
    assert manifest["formally_frozen"] is True
    assert manifest["execution_authorised"] is False
    for record in manifest["public_files"] + manifest["immutable_inputs"]:
        assert hashlib.sha256((ROOT / record["path"]).read_bytes()).hexdigest() == record["sha256"]
    assert len(manifest["public_files"]) == 7
    assert set(manifest["private_metadata_commitment"]) == {"sha256", "record_count"}
    assert manifest["private_metadata_commitment"]["record_count"] == 7


def test_metadata_has_no_selector_code_or_hidden_case_fields():
    for name in ("echo_field.metadata.json", "signal_loom.metadata.json"):
        data = read_json(PACKAGE / name)
        assert set(data) == {"metadata_version", "review_status", "records", "reviewed_by", "review_date", "review_basis"}
        for row in data["records"]:
            assert all(not isinstance(value, (dict, list)) for value in row.values())
            assert not any(term in row["state_scope"] for term in ("gold", "Hit@", "baseline rank", "pass/fail"))


def function(tree, name):
    return next(n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name == name)


def call_keyword(call, name):
    return next(k.value for k in call.keywords if k.arg == name)


def test_actual_production_calls_override_defaults_with_the_same_full_pool():
    retrieval = ast.parse((ROOT / "src/retrieval.py").read_text())
    retrieve = function(retrieval, "retrieve")
    assert ast.literal_eval(retrieve.args.defaults[-1]) == 3
    result_count = next(n for n in ast.walk(retrieve) if isinstance(n, ast.Assign)
                        and any(isinstance(t, ast.Name) and t.id == "result_count" for t in n.targets))
    assert ast.unparse(result_count.value) == "min(top_k, len(self.chunks))"
    production = ast.parse((ROOT / "src/reentry_brief.py").read_text())
    select = function(production, "select_evidence")
    assert ast.literal_eval(select.args.defaults[-1]) == 2
    assert ast.unparse(select.body[-1].value) == "eligible_results[:limit]"
    diverse = function(production, "retrieve_diverse_evidence")
    retrieve_call = next(n for n in ast.walk(diverse) if isinstance(n, ast.Call)
                         and isinstance(n.func, ast.Attribute) and n.func.attr == "retrieve")
    assert ast.unparse(call_keyword(retrieve_call, "top_k")) == "total_chunks"
    select_call = next(n for n in ast.walk(diverse) if isinstance(n, ast.Call)
                       and isinstance(n.func, ast.Name) and n.func.id == "select_evidence")
    assert ast.unparse(call_keyword(select_call, "results")) == "query_results"
    assert ast.unparse(call_keyword(select_call, "limit")) == "total_chunks"
    baseline = ast.parse((ROOT / "experiments/temporal_state_retrieval/baseline.py").read_text())
    adapter = function(baseline, "production_selection")
    call = next(n for n in ast.walk(adapter) if isinstance(n, ast.Call)
                and isinstance(n.func, ast.Name) and n.func.id == "retrieve_diverse_evidence")
    assert ast.unparse(call_keyword(call, "total_chunks")) == "chunk_count"
    assert ast.literal_eval(call_keyword(call, "limit")) == 2
    execute = ast.unparse(function(baseline, "execute"))
    assert "corpora[view] = (raw, len(chunks))" in execute
    assert "raw, count = corpora[view]" in execute
    assert "production_selection(definitions[section], indices[view], raw, count)" in execute
    recorder = next(n for n in baseline.body if isinstance(n, ast.ClassDef) and n.name == "RecordingRetriever")
    recorder_text = ast.unparse(function(recorder, "retrieve"))
    assert "self.delegate.retrieve(query, top_k=top_k)" in recorder_text
    assert "self.calls.append((query, result))" in recorder_text
    assert "return result" in recorder_text


def test_saved_pool_audit_separates_raw_filtered_deduplicated_and_evaluation_counts(manifest):
    original = read_json(ROOT / "outputs/test_results/temporal_state_retrieval_baseline/run_manifest.json")
    audit = manifest["production_pool_audit"]
    assert audit["raw_trace_sha256"] == original["private_raw_trace_sha256"]
    assert audit["candidate_source_channel"] == "production_query_results_after_category_filter"
    assert audit["forbidden_source_channel"] == "ordered_evidence"
    rows = audit["rows"]
    assert len(rows) == 24
    assert len({(x["view"], x["section_id"]) for x in rows}) == 24
    for row in rows:
        n = original["corpus_views"][row["view"]]["chunks"]
        assert row["eligible_corpus_chunks"] == n
        assert row["production_top_k_per_query"] == row["select_evidence_input_per_query"] == [n, n]
        first, second = row["category_eligible_per_query"]
        assert first == second <= n
        assert row["before_cross_query_dedup"] == first + second
        assert row["after_cross_query_dedup"] == row["evaluation_ranked_count"] == first
        assert row["selected_count"] == 2


def selector_fixture():
    a = {"chunk_id": "synthetic-a", "record_id": "TT-R01", "score": 0.9}
    b = {"chunk_id": "synthetic-b", "record_id": "TT-R02", "score": 0.8}
    return {"section_id": "current_vs_superseded",
            "ordered_eligible_candidates": [[a, b], [dict(b, score=0.95), dict(a, score=0.7)]],
            "eligible_record_states": {"TT-R01": "current_snapshot", "TT-R02": "historical_record"}}


def validate_selector_payload(payload, production_query_lists, source_channel):
    # Contract validation only; no scoring, ranking or evidence selection.
    schema = read_json(PACKAGE / "record_metadata.schema.json")
    runtime_schema = {"$schema": schema["$schema"], "$defs": schema["$defs"], "$ref": "#/$defs/selector_input"}
    Draft202012Validator(runtime_schema).validate(payload)
    assert source_channel == "production_query_results_after_category_filter", "evaluation-only input forbidden"
    assert payload["ordered_eligible_candidates"] == production_query_lists, "query channel order, scores or membership changed"
    ids = {c["record_id"] for q in production_query_lists for c in q}
    assert set(payload["eligible_record_states"]) == ids, "metadata must be the minimal eligible projection"


def test_minimal_selector_payload_validates_without_algorithm_execution():
    data = selector_fixture()
    validate_selector_payload(data, copy.deepcopy(data["ordered_eligible_candidates"]), "production_query_results_after_category_filter")


@pytest.mark.parametrize("field", [
    "expected_evidence_ids", "evidence_role", "support_status", "section_applicability",
    "rationale", "record_date", "sequence_position", "state_basis", "state_scope", "case_id", "baseline_result",
])
@pytest.mark.parametrize("level", ["root", "candidate", "record_mapping"])
def test_runtime_interface_rejects_all_non_state_metadata(field, level):
    data = selector_fixture()
    expected = copy.deepcopy(data["ordered_eligible_candidates"])
    if level == "root":
        data[field] = "forbidden"
    elif level == "candidate":
        data["ordered_eligible_candidates"][0][0][field] = "forbidden"
    else:
        data["eligible_record_states"]["TT-R01"] = {"record_state": "current_snapshot", field: "forbidden"}
    with pytest.raises(ValidationError):
        validate_selector_payload(data, expected, "production_query_results_after_category_filter")


def test_evaluation_ranked_list_cannot_replace_the_query_channel():
    data = selector_fixture()
    expected = copy.deepcopy(data["ordered_eligible_candidates"])
    with pytest.raises(AssertionError, match="evaluation-only"):
        validate_selector_payload(data, expected, "ordered_evidence")
    # Even relabelling the source cannot disguise a selected-first reordering.
    data["ordered_eligible_candidates"][0].reverse()
    with pytest.raises(AssertionError, match="order, scores or membership"):
        validate_selector_payload(data, expected, "production_query_results_after_category_filter")


def test_metadata_mapping_rejects_extra_historical_view_records():
    data = selector_fixture()
    data["eligible_record_states"]["TT-R03"] = "closure_record"
    with pytest.raises(AssertionError, match="minimal eligible"):
        validate_selector_payload(data, copy.deepcopy(data["ordered_eligible_candidates"]), "production_query_results_after_category_filter")


def test_s3_order_is_pinned_to_real_query_text_not_gold_roles(manifest):
    tree = ast.parse((ROOT / "src/reentry_brief.py").read_text())
    queries = next(ast.literal_eval(n.value) for n in tree.body if isinstance(n, ast.Assign)
                   and any(isinstance(t, ast.Name) and t.id == "SECTION_RETRIEVAL_QUERIES" for t in n.targets))
    exact = ["What project direction or interaction method is explicitly described as current or still in use?",
             "What project direction is explicitly described as superseded, replaced, no longer current or future work?"]
    original = read_json(ROOT / "outputs/test_results/temporal_state_retrieval_baseline/run_manifest.json")
    assert list(queries["current_vs_superseded"]) == original["queries"]["current_vs_superseded"]["queries"] == exact
    assert manifest["selection_contract"]["s3_query_order_basis"] == exact
    assert manifest["selection_contract"]["rule_by_section"]["current_vs_superseded"] == "cross_document_function_pair_or_baseline"
    for section in ("changes_and_reasons", "relevant_feedback", "possible_next_action"):
        assert manifest["selection_contract"]["rule_by_section"][section] == "baseline_unchanged"


def test_phase_1_and_phase_3_success_criteria_are_separate_and_not_claimed(manifest):
    old = manifest["phase_1_original_benchmark_criteria"]
    path = ROOT / old["source"]
    assert hashlib.sha256(path.read_bytes()).hexdigest() == old["source_sha256"]
    actual = path.read_text().split("## Success and stopping criteria\n", 1)[1].split("## Frozen package", 1)[0].strip()
    assert old["verbatim_success_section"] == actual
    new = manifest["phase_3_candidate_improvement_criteria"]
    assert old["candidate_outcome"] == new["candidate_outcome"] == "not_evaluated"
    assert new["permitted_success_claim"] == "met the preregistered Phase 3 improvement criteria"
    assert len(manifest["required_separate_result_statements"]) == 2
    assert all(new[k] == value for k, value in manifest["success_gate"].items())


def test_markdown_latency_uses_readable_threshold_with_exact_json_origin(manifest):
    protocol = (ROOT / "project_knowledge/process/experiments/temporal_state_retrieval/phase_3_preregistration.md").read_text()
    assert "44.03 ms" in protocol and "22.01445 ms" in protocol
    assert "44.028899996192195" not in protocol
    assert manifest["phase_3_candidate_improvement_criteria"]["latency_display_ms"] == 44.03
