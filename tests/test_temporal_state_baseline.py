"""Synthetic unit checks for the experiment; no real model or private corpus."""
import copy
from dataclasses import fields
import hashlib
import json
import subprocess
from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
with pytest.MonkeyPatch.context() as import_scope:
    import_scope.syspath_prepend(str(ROOT))
    from experiments.temporal_state_retrieval import baseline as b
    from experiments.temporal_state_retrieval import scoring as s


def case(**overrides):
    row = dict(case_id="TEST-1", project_id="invented", context_id="test", section_id="current_vs_superseded", benchmark_tier="production", expected_support_status="supported", section_applicability="applicable", required_evidence_roles=["current_direction", "superseded_direction"], acceptable_gold_passages=["now", "old"], required_context_passages=[], expected_temporal_status=["current", "superseded"], role_temporal_requirements={"current_direction": ["current"], "superseded_direction": ["superseded"]}, acceptable_pair_sets=[["now", "old"]], applicability_evidence_sets=[["now"]], boundary_passages=[], excluded_or_misleading_passages=[], current_claim_roles=["current_direction"])
    row.update(overrides)
    return row


def passage(pid, quote, start, role, status="current", **overrides):
    row = dict(passage_id=pid, context_id="test", source="state.md", quote=quote, locator={"start_char": start, "end_char": start+len(quote)}, temporal_status=status, evidence_role=[role], context_spans=[], inapplicability_case_ids=[])
    row.update(overrides)
    return row


def item(quote, start=0, source="state.md"):
    return dict(source=source, excerpt=quote, start_char=start, end_char=start+len(quote), visible_token_spans=[(start, start+len(quote))])


def trace(*items):
    return {"ordered_evidence": list(items), "selected_evidence": list(items[:2])}


@pytest.fixture
def pair():
    return {"now": passage("now", "New", 0, "current_direction"), "old": passage("old", "Old", 10, "superseded_direction", "superseded")}


def test_frozen_public_manifest_and_schema():
    from jsonschema import Draft202012Validator
    manifest = b.verify_manifest(b.PUBLIC / "freeze_manifest.json")
    assert manifest["version"] == "phase_1_gold_v1"
    data = b.read_json(b.PUBLIC / "public_benchmark.json")
    Draft202012Validator(b.read_json(b.PUBLIC / "benchmark.schema.json")).validate(data)
    assert len(data["cases"]) == 23
    assert all(c["review_status"] == "researcher_confirmed" for c in data["cases"])


def test_manifest_rejects_tampering(tmp_path):
    d = {"version": b.VERSION, "frozen_files": [{"path": "record.txt", "sha256": hashlib.sha256(b"before").hexdigest()}], "self_digest": {}}
    d["self_digest"]["sha256"] = hashlib.sha256(json.dumps(d, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()
    (tmp_path / "manifest.json").write_text(json.dumps(d))
    (tmp_path / "record.txt").write_text("after")
    with pytest.raises(ValueError, match="fingerprint"):
        b.verify_manifest(tmp_path / "manifest.json", tmp_path)
    d["version"] = "tampered"
    (tmp_path / "manifest.json").write_text(json.dumps(d))
    with pytest.raises(ValueError, match="self digest"):
        b.verify_manifest(tmp_path / "manifest.json", tmp_path)


def test_request_contains_no_gold_or_diagnostic_query():
    assert {f.name for f in fields(b.RetrievalRequest)} == {"view_id", "source_root", "sources", "section_id"}
    data = b.read_json(b.PUBLIC / "public_benchmark.json")
    before, keys = b.make_requests(data)
    for c in data["cases"]:
        c.update(question="DO NOT USE THIS QUERY", expected_support_status="insufficient", required_evidence_roles=[], acceptable_gold_passages=[])
    after, after_keys = b.make_requests(data)
    assert before == after and keys == after_keys


def test_loader_adapter_preserves_production_and_excludes_future(tmp_path):
    from document_loader import load_documents
    for name in ("state/early.md", "state/future.md"):
        p = tmp_path / name
        p.parent.mkdir(exist_ok=True)
        p.write_text("An invented record.", encoding="utf-8")
    full = load_documents(tmp_path)
    assert load_documents(b.EligibleRoot(tmp_path, ["state/future.md", "state/early.md"])) == full
    assert [d.source for d in load_documents(b.EligibleRoot(tmp_path, ["state/early.md"]))] == ["state/early.md"]
    with pytest.raises(ValueError):
        list(b.EligibleRoot(tmp_path, ["../escaped.md"]).rglob("*"))


@pytest.mark.parametrize("mode", ["future", "undated", "context", "incomplete_primary"])
def test_frozen_eligibility_rejects_leakage(mode):
    records = {"a": dict(project_id="p", record_sequence=1, record_date="2026-01-01", historical_order_established=True), "b": dict(project_id="p", record_sequence=2, record_date="2026-01-02", historical_order_established=True)}
    c = dict(project_id="p", reference_state="historical_snapshot", as_of_record="a", eligible_record_ids=["a"], benchmark_tier="diagnostic")
    context = copy.deepcopy(c)
    b.check_eligibility(c, context, records)
    if mode == "future":
        c["eligible_record_ids"].append("b"); context["eligible_record_ids"].append("b")
    elif mode == "undated":
        records["a"]["historical_order_established"] = False
    elif mode == "context":
        c["eligible_record_ids"].append("b")
    else:
        c.update(benchmark_tier="production", reference_state="latest_project_state")
        context["reference_state"] = "latest_project_state"
    with pytest.raises(ValueError):
        b.check_eligibility(c, context, records)


def test_complete_role_pair_and_historical_partner_not_false_current(pair):
    score = s.score_case(case(), pair, trace(item("New"), item("Old", 10)))
    assert score["metrics"]["role_coverage_at_2"] == 1
    assert score["metrics"]["pair_coverage_at_2"] == 1
    assert score["metrics"]["false_current_judged"] == 0


def test_partial_role_and_no_pair_duplicate_passage_counted_once(pair):
    score = s.score_case(case(), pair, trace(item("New"), item("New")))
    assert score["metrics"]["role_coverage_at_2"] == .5
    assert score["metrics"]["pair_coverage_at_2"] == 0


def test_truncation_wrong_source_and_context_never_fuzzy_match(pair):
    assert s.matched_ids(case(), pair, [item("Ne")]) == set()
    assert s.matched_ids(case(), pair, [item("New", source="other.md")]) == set()
    pair["now"]["context_spans"] = [{"start_char": 20, "end_char": 24, "quote": "Date"}]
    c = case(required_context_passages=["now"])
    assert s.matched_ids(c, pair, [item("New")]) == set()
    assert s.matched_ids(c, pair, [item("New"), item("Date", 20)]) == {"now"}


def test_supported_unclear_gets_support_credit_not_applicability(pair):
    c = case(section_applicability="unclear", applicability_evidence_sets=[], expected_temporal_status=["unknown"], role_temporal_requirements={"current_direction": ["unknown"], "superseded_direction": ["superseded"]})
    pair["now"]["temporal_status"] = "unknown"
    result = s.score_case(c, pair, trace(item("New"), item("Old", 10)))
    assert result["metrics"]["hit_at_1"] == 1
    assert result["metrics"]["applicability_evidence_at_2"] is None


def test_insufficient_not_a_classifier_or_empty_equals_absence(pair):
    c = case(expected_support_status="insufficient", section_applicability="unclear", acceptable_gold_passages=[], acceptable_pair_sets=[], applicability_evidence_sets=[])
    for output in (trace(), trace(item("New"))):
        r = s.score_case(c, pair, output)
        assert r["metrics"]["hit_at_1"] is None
        assert "not measurable" in r["insufficient_detail"]["classification_accuracy"]


def test_not_applicable_requires_scoped_explicit_closure():
    c = case(required_evidence_roles=["closure_or_inapplicability"], acceptable_gold_passages=["closed"], acceptable_pair_sets=[], section_applicability="not_applicable", role_temporal_requirements={"closure_or_inapplicability": ["completed"]}, expected_temporal_status=["completed"], applicability_evidence_sets=[["closed"]], current_claim_roles=[])
    p = {"closed": passage("closed", "Closed", 0, "closure_or_inapplicability", "completed", inapplicability_case_ids=["TEST-1"])}
    assert s.score_case(c, p, trace(item("Closed")))["metrics"]["closure_at_1"] == 1
    p["closed"]["inapplicability_case_ids"] = ["OTHER"]
    assert s.score_case(c, p, trace(item("Closed")))["metrics"]["closure_at_1"] == 0
    assert s.score_case(c, p, trace())["metrics"]["closure_at_1"] == 0


def test_temporal_and_unknown_exclusions_not_invented(pair):
    pair["now"]["temporal_status"] = "historical"
    r = s.score_case(case(), pair, trace(item("New")))
    assert r["metrics"]["temporal_mismatch"] == 1
    assert r["metrics"]["false_current_judged"] == 1
    unjudged = s.score_case(case(), pair, trace(item("Unlabelled text")))
    assert unjudged["metrics"]["temporal_mismatch"] is None
    assert unjudged["metrics"]["false_current_judged"] is None


def test_tier_denominators_and_macro_role_fraction(pair):
    one = s.score_case(case(), pair, trace(item("New")))
    two = s.score_case(case(case_id="TEST-2"), pair, trace(item("New"), item("Old", 10)))
    diag = s.score_case(case(case_id="TEST-D", benchmark_tier="diagnostic"), pair, trace())
    report = s.aggregate([one, two, diag], "production")
    assert report["case_count"] == 2
    assert report["metrics"]["role_coverage_at_2"]["numerator"] == 1.5
    assert report["metrics"]["role_coverage_at_2"]["denominator"] == 2
    assert report["metrics"]["pair_coverage_at_2"]["numerator"] == 1
    assert s.aggregate([one, two, diag], "diagnostic")["case_count"] == 1


def test_private_rows_removed_and_aggregate_ids_redacted(pair):
    public = s.score_case(case(), pair, trace(item("New")))
    private = s.score_case(case(case_id="PRIVATE-CASE"), pair, trace(item("New")))
    private["private_excerpt"] = "SENSITIVE-SENTINEL"
    private_ids = {"PRIVATE-CASE"}
    output = json.dumps({"cases": b.public_projection([public, private], private_ids), "aggregate": s.aggregate([public, private], "production", private_ids)})
    assert "SENSITIVE-SENTINEL" not in output and "PRIVATE-CASE" not in output
    assert "eligible_private_case_count" in output


def test_production_selection_and_tail_ties_direct_call(monkeypatch):
    from brief_schema import SECTION_DEFINITIONS
    from chunking import create_chunks
    from document_loader import Document
    from retrieval import SearchResult
    import reentry_brief
    raw = {f"current_state/{name}.md": name for name in ("alpha", "beta", "gamma", "delta")}
    chunks = create_chunks([Document(v, k, "current_state", ".md") for k, v in raw.items()])
    ranked = [SearchResult(i+1, .5, c) for i, c in enumerate(chunks)]
    class Fake:
        def retrieve(self, query, top_k):
            assert top_k == 4
            return ranked
    original = reentry_brief.retrieve_diverse_evidence
    called = []
    def spy(*a, **kw):
        called.append(True)
        return original(*a, **kw)
    monkeypatch.setattr(reentry_brief, "retrieve_diverse_evidence", spy)
    selected, calls, _ = b.production_selection(SECTION_DEFINITIONS[0], Fake(), raw, 4)
    output = b.ordered_trace(selected, calls, SECTION_DEFINITIONS[0], raw)
    assert called == [True]
    assert [x["source"] for x in selected] == list(raw)[:2]
    assert output["ordered_evidence"][:2] == selected
    assert [x["source"] for x in output["ordered_evidence"][2:]] == sorted(list(raw)[2:])
    assert len(calls) == 2


def test_chunk_source_mapping_and_production_excerpt():
    from document_loader import Document
    from chunking import chunk_document
    from retrieval import SearchResult
    raw = "  Header\n\n" + " ".join(["longword"*3] * 140)
    chunks = chunk_document(Document(raw.strip(), "state.md", "current_state", ".md"))
    result = b.visible_evidence(SearchResult(1, .9, chunks[0]), raw)
    assert result["excerpt"].endswith("...")
    assert len(result["excerpt"]) == 1203
    assert s.normalise(raw[result["start_char"]:result["end_char"]]) == result["excerpt"][:-3]


def test_no_llm_or_summary_entrypoints_in_harness():
    import ast
    tree = ast.parse(Path(b.__file__).read_text(encoding="utf-8"))
    imported = {n.module for n in ast.walk(tree) if isinstance(n, ast.ImportFrom)}
    imported |= {a.name for n in ast.walk(tree) if isinstance(n, ast.Import) for a in n.names}
    assert not ({"openai", "llm_summarizer", "study_cache", "study_project_manager"} & imported)


def test_latency_is_duration_distribution_not_accuracy():
    d = s.latency_stats([10, 20, 30])
    assert d["sample_count"] == 3 and d["median_ms"] == 20
    assert d["minimum_ms"] == 10 and d["maximum_ms"] == 30
    assert d["numerator"] is None


def synthetic_execution_archive():
    production = [(f"view-{v}", f"section-{s}") for v in range(3) for s in range(6)]
    diagnostic_unique = production[:8] + [("view-3", f"section-{s}") for s in range(6)]
    diagnostic = diagnostic_unique + [diagnostic_unique[0], diagnostic_unique[-1]]
    cases, keys = [], {}
    for tier, requests in (("production", production), ("diagnostic", diagnostic)):
        for i, key in enumerate(requests):
            cid = f"{tier}-{i}"
            cases.append({"case_id": cid, "benchmark_tier": tier,
                          "expected_support_status": "insufficient" if i in (2, 3) else "supported"})
            keys[cid] = key
    unique = sorted(set(keys.values()))
    traces = {k: {"ordered_evidence": ["synthetic-item"], "selected_evidence": ["synthetic-item"], "queries": ["query-one", "query-two"]} for k in unique}
    cold = {k: i+1 for i, k in enumerate(unique)}
    warm = {k: [cold[k]+.5]*30 for k in unique}
    scores = [{"case_id": c["case_id"]} for c in cases]
    return cases, keys, traces, cold, warm, scores


def test_latency_covers_insufficient_cases_and_distinguishes_reused_samples():
    cases, keys, _, cold, warm, _ = synthetic_execution_archive()
    report = b.tier_latency(cases, keys, cold, warm, "diagnostic")
    assert report["case_count"] == 16 and report["unique_requests"] == 14
    assert report["insufficient_cases_included"] == 2
    assert report["first_query"]["sample_count"] == 14
    assert report["warm"]["sample_count"] == 420
    assert report["case_weighted"]["first_query"]["sample_count"] == 16
    assert report["case_weighted"]["warm"]["sample_count"] == 480
    # All-case statistics equal direct expansion of the saved mapping, not
    # supported-only filtering or invention of new execution samples.
    diagnostic_keys = [keys[c["case_id"]] for c in cases if c["benchmark_tier"] == "diagnostic"]
    assert report["case_weighted"]["warm"] == s.latency_stats([t for k in diagnostic_keys for t in warm[k]])
    changed = [dict(c, expected_support_status="supported") for c in cases]
    assert b.tier_latency(changed, keys, cold, warm, "diagnostic")["warm"] == report["warm"]


def test_execution_accounting_reconciles_all_34_cases_and_1536_encodes():
    rows, counts = b.execution_accounting(*synthetic_execution_archive())
    assert len(rows) == counts["complete_cases"] == 34
    assert counts["unique_corpus_views"] == 4 and counts["unique_requests"] == 24
    assert counts["first_runs"] == counts["warmup_runs"] == 24
    assert counts["timed_warm_runs"] == 720
    assert counts["total_request_executions"] == 768
    assert counts["derived_query_encode_calls"] == 24*2*(1+1+30) == 1536
    assert counts["derived_query_texts"] == 1536
    p = counts["tiers"]["production"]["query_encodes_including_shared"]
    d = counts["tiers"]["diagnostic"]["query_encodes_including_shared"]
    assert (p, d, counts["shared_query_encodes"]) == (1152, 896, 512)
    assert p+d-counts["shared_query_encodes"] == 1536


@pytest.mark.parametrize("missing", ["cold", "warm", "score"])
def test_audit_rejects_missing_insufficient_case_execution(missing):
    cases, keys, traces, cold, warm, scores = synthetic_execution_archive()
    target = next(c for c in cases if c["benchmark_tier"] == "diagnostic" and c["expected_support_status"] == "insufficient")
    key = keys[target["case_id"]]
    if missing == "cold":
        del cold[key]
    elif missing == "warm":
        warm[key] = warm[key][:-1]
    else:
        scores = [s for s in scores if s["case_id"] != target["case_id"]]
    with pytest.raises(ValueError):
        b.execution_accounting(cases, keys, traces, cold, warm, scores)


def test_harness_import_does_not_mutate_process_or_start_work():
    # A fresh interpreter prevents previously imported libraries hiding effects.
    program = '''
import os, sys, json
sys.path.insert(0, sys.argv[1])
before_path, before_env, before_cwd = list(sys.path), dict(os.environ), os.getcwd()
def deny_mutations(event, args):
    if event in ("os.chdir", "os.putenv", "os.unsetenv", "os.remove", "os.rmdir", "os.mkdir", "os.rename", "socket.connect", "socket.getaddrinfo"):
        raise AssertionError("unexpected import side effect: " + event)
    if event == "open" and (isinstance(args[1], str) and any(c in args[1] for c in "wax+") or isinstance(args[2], int) and args[2] & (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC)):
        raise AssertionError("unexpected file write during import")
sys.addaudithook(deny_mutations)
import experiments.temporal_state_retrieval.baseline
assert sys.path == before_path
assert dict(os.environ) == before_env
assert os.getcwd() == before_cwd
assert not any(name in sys.modules for name in ("retrieval", "sentence_transformers", "openai", "llm_summarizer"))
print("IMPORT_SIDE_EFFECTS_ZERO")
'''
    result = subprocess.run([sys.executable, "-B", "-c", program, str(ROOT)], capture_output=True, text=True, timeout=30)
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == "IMPORT_SIDE_EFFECTS_ZERO"


def test_production_import_path_restores_on_success_and_exception(monkeypatch):
    original = [p for p in sys.path if p != str(ROOT / "src")]
    monkeypatch.setattr(sys, "path", original.copy())
    with b.production_import_path():
        assert sys.path[0] == str(ROOT / "src")
    assert sys.path == original
    with pytest.raises(RuntimeError, match="synthetic import failure"):
        with b.production_import_path():
            raise RuntimeError("synthetic import failure")
    assert sys.path == original
