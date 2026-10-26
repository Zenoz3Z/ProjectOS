"""Offline adapter to the unchanged ProjectOS production retrieval pipeline.

Gold is consumed by validation/scoring, never by RetrievalRequest or retrieval.
Run metadata and public output deliberately omit private source/case locators.
"""
from __future__ import annotations

import argparse
from collections import Counter
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import importlib
import importlib.metadata
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
PUBLIC = ROOT / "tests/fixtures/temporal_state_benchmark"
VERSION = "phase_1_gold_v1"
WARM_REPETITIONS = 30


@contextmanager
def production_import_path():
    """Resolve legacy absolute imports only while importing production modules."""
    previous = list(sys.path)
    try:
        source = str(ROOT / "src")
        if source not in sys.path:
            sys.path.insert(0, source)
        yield
    finally:
        sys.path[:] = previous


def production_module(name):
    with production_import_path():
        return importlib.import_module(name)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")


def git(*args):
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True, encoding="utf-8").strip()


def safe_relative(root, relative):
    path = (root / relative).resolve()
    if not path.is_relative_to(root.resolve()):
        raise ValueError("path escapes approved root")
    return path


def verify_manifest(path, root=ROOT):
    data = read_json(path)
    claimed = data["self_digest"].pop("sha256")
    actual = hashlib.sha256(json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()
    data["self_digest"]["sha256"] = claimed
    if actual != claimed or data["version"] != VERSION:
        raise ValueError("freeze manifest self digest/version mismatch")
    for key in ("frozen_files", "private_frozen_files", "unchanged_public_sources", "unchanged_production_fingerprints", "unchanged_legacy_regression"):
        entries = data.get(key, [])
        for entry in ([entries] if isinstance(entries, dict) else entries):
            if sha(safe_relative(root, entry["path"])) != entry["sha256"]:
                raise ValueError("frozen file fingerprint mismatch: " + key)
    if "public_manifest" in data:
        entry = data["public_manifest"]
        if sha(safe_relative(root, entry["path"])) != entry["sha256"]:
            raise ValueError("public manifest commitment mismatch")
    return data


def check_eligibility(case, context, records):
    for field in ("reference_state", "as_of_record", "eligible_record_ids"):
        if case[field] != context[field]:
            raise ValueError("case/context eligibility disagreement")
    if len(set(case["eligible_record_ids"])) != len(case["eligible_record_ids"]):
        raise ValueError("duplicate eligible record")
    anchor = records[case["as_of_record"]]
    if case["as_of_record"] not in case["eligible_record_ids"]:
        raise ValueError("anchor outside eligible corpus")
    for rid in case["eligible_record_ids"]:
        record = records[rid]
        if record["project_id"] != case["project_id"]:
            raise ValueError("cross-project eligibility")
        if case["reference_state"] == "historical_snapshot":
            if record["record_sequence"] > anchor["record_sequence"] or not record["historical_order_established"]:
                raise ValueError("future or unplaced record leakage")
            if record["record_date"] and anchor["record_date"] and record["record_date"] > anchor["record_date"]:
                raise ValueError("future dated record leakage")
    if case["benchmark_tier"] == "production":
        if case["reference_state"] != "latest_project_state":
            raise ValueError("primary historical view")
        expected = {rid for rid, r in records.items() if r["project_id"] == case["project_id"]}
        if set(case["eligible_record_ids"]) != expected:
            raise ValueError("primary corpus is incomplete")


def validate_gold(public, private, root=ROOT):
    from jsonschema import Draft202012Validator
    SECTION_DEFINITIONS = production_module("brief_schema").SECTION_DEFINITIONS
    schema = read_json(PUBLIC / "benchmark.schema.json")
    for data in (public, private):
        Draft202012Validator(schema).validate(data)
    merged = {key: public[key] + private[key] for key in ("contexts", "record_catalog", "passages", "cases")}
    contexts = {c["context_id"]: c for c in merged["contexts"]}
    records = {r["record_id"]: r for r in merged["record_catalog"]}
    passages = {p["passage_id"]: p for p in merged["passages"]}
    cases = merged["cases"]
    assert len({c["case_id"] for c in cases}) == len(cases) == 34
    assert Counter(c["benchmark_tier"] for c in cases) == {"production": 18, "diagnostic": 16}
    questions = {d.section_id: d.question for d in SECTION_DEFINITIONS}
    for project in {c["project_id"] for c in cases}:
        assert Counter(c["section_id"] for c in cases if c["project_id"] == project and c["benchmark_tier"] == "production") == Counter({s: 1 for s in questions})
    # Resolve only the three expressly permitted source roots. Never enumerate
    # participant directories or read a cache/review/assignment.
    approved = {"data/demo_projects/sample_echo_field", "data/study_projects/P96", "tests/fixtures/temporal_state_project/records"}
    source_texts = {}
    for rid, record in records.items():
        if record["source_root"] not in approved:
            raise ValueError("source outside permitted benchmark corpora")
        path = safe_relative(safe_relative(root, record["source_root"]), record["source"])
        if sha(path) != record["sha256"]:
            raise ValueError("source hash mismatch")
        source_texts[rid] = path.read_text(encoding="utf-8")
    for p in passages.values():
        text = source_texts[p["record_id"]]
        for span in [dict(p["locator"], quote=p["quote"]), *p["context_spans"]]:
            if text[span["start_char"]:span["end_char"]] != span["quote"]:
                raise ValueError("gold locator does not match source exactly")
        if p["temporal_status"] == "future_conditional" and "next_action" in p["evidence_role"]:
            raise ValueError("conditional evidence labelled next action")
    for c in cases:
        if c["review_status"] != "researcher_confirmed":
            raise ValueError("unconfirmed label")
        check_eligibility(c, contexts[c["context_id"]], records)
        if c["benchmark_tier"] == "production" and c["question"] != questions[c["section_id"]]:
            raise ValueError("noncanonical primary question")
        if c["section_applicability"] == "not_applicable":
            assert c["expected_support_status"] == "supported"
            assert c["applicability_evidence_sets"]
            assert "closure_or_inapplicability" in c["required_evidence_roles"]
            assert any(c["case_id"] in passages[p]["inapplicability_case_ids"] for p in c["acceptable_gold_passages"])
    return merged


@dataclass(frozen=True)
class RetrievalRequest:
    """Only immutable corpus eligibility and the production section selector."""
    view_id: str
    source_root: str
    sources: tuple[str, ...]
    section_id: str


def make_requests(data):
    contexts = {c["context_id"]: c for c in data["contexts"]}
    records = {r["record_id"]: r for r in data["record_catalog"]}
    requests = {}
    case_keys = {}
    for case in data["cases"]:
        context = contexts[case["context_id"]]
        key = (context["context_id"], case["section_id"])
        request = RetrievalRequest(key[0], context["source_root"], tuple(sorted(records[r]["source"] for r in case["eligible_record_ids"])), key[1])
        if key in requests and requests[key] != request:
            raise ValueError("inconsistent view reuse")
        requests[key] = request
        case_keys[case["case_id"]] = key
    return requests, case_keys


class EligibleRoot(os.PathLike):
    """Path-like enumeration adapter: production loader reads only eligible files."""
    def __init__(self, root, sources):
        self.root, self.sources = Path(root), tuple(sources)

    def __fspath__(self):
        return str(self.root)

    def exists(self):
        return self.root.exists()

    def rglob(self, pattern):
        if pattern != "*":
            raise ValueError("unexpected production enumeration")
        return iter(safe_relative(self.root, s) for s in self.sources)


def visible_evidence(result, raw):
    create_excerpt = production_module("reentry_brief").create_excerpt
    chunk = result.chunk
    tokens = list(re.finditer(r"\S+", raw))
    selected = tokens[chunk.start_word:chunk.end_word]
    if " ".join(t.group() for t in selected) != chunk.content:
        raise ValueError("production chunk cannot be mapped to source tokens")
    excerpt = create_excerpt(chunk.content)
    visible = min(1200, len(chunk.content))
    spans, consumed = [], 0
    for token in selected:
        remaining = visible - consumed
        if remaining <= 0:
            break
        length = min(len(token.group()), remaining)
        spans.append((token.start(), token.start() + length))
        consumed += len(token.group()) + 1
    return {"chunk_id": chunk.chunk_id, "source": chunk.source, "category": chunk.category,
            "score": result.score, "excerpt": excerpt, "start_char": spans[0][0],
            "end_char": spans[-1][1], "visible_token_spans": spans, "context_metadata": []}


class RecordingRetriever:
    def __init__(self, delegate):
        self.delegate, self.calls = delegate, []

    def retrieve(self, query, top_k):
        result = self.delegate.retrieve(query, top_k=top_k)
        self.calls.append((query, result))
        return result


def production_selection(definition, retriever, raw_by_source, chunk_count):
    production = production_module("reentry_brief")
    retrieve_diverse_evidence, create_excerpt = production.retrieve_diverse_evidence, production.create_excerpt
    recorder = RecordingRetriever(retriever)
    started = time.perf_counter()
    selected = retrieve_diverse_evidence(definition, recorder, total_chunks=chunk_count, limit=2)
    excerpts = [create_excerpt(r.chunk.content) for r in selected]
    duration = (time.perf_counter()-started)*1000
    items = [visible_evidence(r, raw_by_source[r.chunk.source]) for r in selected]
    assert [item["excerpt"] for item in items] == excerpts
    return items, recorder.calls, duration


def ordered_trace(selected, calls, definition, raw_by_source):
    """Prespecified scoring tail; actual production selections remain first."""
    select_evidence = production_module("reentry_brief").select_evidence
    best = {}
    query_traces = []
    for query, results in calls:
        eligible = select_evidence(results, definition.preferred_categories, limit=len(results))
        query_traces.append({"query": query, "eligible_results": [visible_evidence(r, raw_by_source[r.chunk.source]) for r in eligible]})
        for result in eligible:
            cid = result.chunk.chunk_id
            if cid not in best or result.score > best[cid].score:
                best[cid] = result
    chosen = {item["chunk_id"] for item in selected}
    tail = sorted((r for cid, r in best.items() if cid not in chosen), key=lambda r: (-r.score, r.chunk.chunk_id))
    return {"selected_evidence": selected, "ordered_evidence": selected + [visible_evidence(r, raw_by_source[r.chunk.source]) for r in tail], "queries": query_traces}


def offline_environment():
    for key in ("HF_HUB_OFFLINE", "TRANSFORMERS_OFFLINE", "HF_HUB_DISABLE_TELEMETRY", "HF_HUB_DISABLE_IMPLICIT_TOKEN"):
        os.environ[key] = "1"
    os.environ.pop("OPENAI_API_KEY", None)


def install_boundary_guard():
    """Process-local deny rules, not OS permissions or a replacement retriever."""
    counts = {"blocked_network_attempts": 0, "blocked_private_access_attempts": 0}
    study = (ROOT / "data/study_projects").resolve()
    allowed_study = study / "P96"
    restricted = [(ROOT / s).resolve() for s in ("data/reviews", "data/summary_cache", "data/study_config")]
    def guard(event, args):
        if event in {"socket.connect", "socket.getaddrinfo"}:
            counts["blocked_network_attempts"] += 1
            raise RuntimeError("network disabled for offline benchmark")
        if event == "open" and isinstance(args[0], (str, bytes, os.PathLike)):
            path = Path(os.fsdecode(args[0])).resolve()
            if (path.is_relative_to(study) and not path.is_relative_to(allowed_study)) or any(path.is_relative_to(p) for p in restricted):
                counts["blocked_private_access_attempts"] += 1
                raise RuntimeError("formal participant/cache/review access forbidden")
    sys.addaudithook(guard)
    return counts


def public_projection(results, private_ids):
    """Whitelist public cases; private case identifiers and explanations excluded."""
    keys = ("case_id", "project_id", "benchmark_tier", "section_id", "expected_support_status", "section_applicability", "metrics", "first_gold_rank", "ordered_list_length", "evidence_coverage_status")
    return [{k: row[k] for k in keys} for row in results if row["case_id"] not in private_ids]


def supplementary_summaries(results, tier, private_ids):
    from .scoring import aggregate
    rows = [r for r in results if r["benchmark_tier"] == tier]
    project_groups = {project: aggregate([r for r in rows if r["project_id"] == project], tier, private_ids) for project in sorted({r["project_id"] for r in rows})}
    section_groups = {section: aggregate([r for r in rows if r["section_id"] == section], tier, private_ids) for section in sorted({r["section_id"] for r in rows})}
    macro = {}
    for metric in next(iter(project_groups.values()))["metrics"]:
        values = [group["metrics"][metric]["value"] for group in project_groups.values() if group["metrics"][metric]["value"] is not None]
        macro[metric] = {"numerator": sum(values), "denominator": len(values), "value": sum(values)/len(values) if values else None, "interpretation": "equal-weight project macro, excluding unmeasurable project values", "excluded_project_count": len(project_groups)-len(values)}
    strata = {app: aggregate([r for r in rows if r["section_applicability"] == app], tier, private_ids) for app in ("applicable", "not_applicable", "unclear") if any(r["section_applicability"] == app for r in rows)}
    contingency = {}
    for support, app in (("insufficient", "unclear"), ("supported", "not_applicable")):
        group = [r for r in rows if r["expected_support_status"] == support and r["section_applicability"] == app]
        contingency[support+"_"+app] = {"case_count": len(group), "evidence_counts": dict(Counter(r["closure_contingency"] for r in group)), "additional_misleading_negative_exposure": sum(r["misleading_negative_exposure"] for r in group), "interpretation": "evidence availability only; unjudged precedence; not classification accuracy"}
    return {"by_project": project_groups, "by_section": section_groups, "project_macro": macro, "by_applicability": strata, "closure_contingency": contingency}


def tier_latency(cases, case_keys, cold, warm, tier):
    """All cases participate; distinguish measured requests from reused samples."""
    from .scoring import latency_stats
    rows = [c for c in cases if c["benchmark_tier"] == tier]
    case_requests = [case_keys[c["case_id"]] for c in rows]
    unique = sorted(set(case_requests))
    for key in unique:
        if key not in cold or key not in warm or len(warm[key]) != WARM_REPETITIONS:
            raise ValueError("missing or incomplete latency execution record")
    return {
        "case_count": len(rows), "unique_requests": len(unique),
        "scope": "distinct measured view/section requests covering every case; no support-status exclusion",
        "first_query": latency_stats([cold[k] for k in unique]),
        "warm": latency_stats([t for k in unique for t in warm[k]]),
        "insufficient_cases_included": sum(c["expected_support_status"] == "insufficient" for c in rows),
        "case_weighted": {
            "case_count": len(rows), "unique_requests": len(unique),
            "first_query": latency_stats([cold[k] for k in case_requests]),
            "warm": latency_stats([t for k in case_requests for t in warm[k]]),
            "interpretation": "all-case weighting of saved request measurements; shared requests are repeated analytically, not independently timed",
        },
    }


def execution_accounting(cases, case_keys, traces, cold, warm, scores):
    """Audit saved execution coverage and derive counters without model access.

    Returned case rows can contain private identifiers: keep them private.
    The accounting summary contains counts only and is safe for the manifest.
    """
    if len({c["case_id"] for c in cases}) != len(cases):
        raise ValueError("duplicate case ID")
    if len({s["case_id"] for s in scores}) != len(scores):
        raise ValueError("duplicate scoring record")
    score_ids = {s["case_id"] for s in scores}
    if score_ids != {c["case_id"] for c in cases}:
        raise ValueError("case/scoring population mismatch")
    rows = []
    for c in cases:
        cid = c["case_id"]
        if cid not in case_keys:
            raise ValueError("case has no retrieval request")
        key = case_keys[cid]
        if key not in traces or key not in cold or key not in warm:
            raise ValueError("case missing execution or latency trace")
        trace = traces[key]
        if not all(k in trace for k in ("ordered_evidence", "selected_evidence", "queries")):
            raise ValueError("incomplete evidence trace")
        if trace["ordered_evidence"][:len(trace["selected_evidence"])] != trace["selected_evidence"]:
            raise ValueError("selected pair does not head ranked trace")
        if len(warm[key]) != WARM_REPETITIONS:
            raise ValueError("incomplete warm repetition trace")
        rows.append({"case_id": cid, "tier": c["benchmark_tier"], "request_key": list(key),
                     "corpus_view": True, "retrieval_execution": True, "ranked_results": True,
                     "selected_evidence": True, "scoring_record": True, "latency_record": True,
                     "warm_samples": len(warm[key]), "query_count": len(trace["queries"])})
    keys = set(case_keys.values())
    if set(traces) != keys or set(cold) != keys or set(warm) != keys:
        raise ValueError("unmapped or missing request trace")
    tiers = {tier: {case_keys[c["case_id"]] for c in cases if c["benchmark_tier"] == tier}
             for tier in ("production", "diagnostic")}
    per_execution_queries = sum(len(traces[k]["queries"]) for k in keys)
    runs_per_request = 1 + 1 + WARM_REPETITIONS
    tier_counts = {}
    for tier, tier_keys in tiers.items():
        tier_counts[tier] = {
            "cases": sum(c["benchmark_tier"] == tier for c in cases),
            "unique_requests": len(tier_keys),
            "request_executions_including_shared": len(tier_keys)*runs_per_request,
            "query_encodes_including_shared": sum(len(traces[k]["queries"]) for k in tier_keys)*runs_per_request,
        }
    shared = tiers["production"] & tiers["diagnostic"]
    return rows, {
        "complete_cases": len(rows), "unique_corpus_views": len({k[0] for k in keys}),
        "unique_requests": len(keys), "query_count_per_request": sorted({len(traces[k]["queries"]) for k in keys}),
        "first_runs": len(keys), "warmup_runs": len(keys),
        "timed_warm_runs": len(keys)*WARM_REPETITIONS,
        "total_request_executions": len(keys)*runs_per_request,
        "derived_query_encode_calls": per_execution_queries*runs_per_request,
        "derived_query_texts": per_execution_queries*runs_per_request,
        "shared_cross_tier_requests": len(shared),
        "shared_query_encodes": sum(len(traces[k]["queries"]) for k in shared)*runs_per_request,
        "tiers": tier_counts,
        "query_embedding_reuse": False,
        "reuse_boundary": "cases sharing a view/section reuse its saved result and timings; every execution re-encodes both queries",
        "query_formula": "sum(queries per unique request) * (1 first + 1 warm-up + 30 timed warm)",
    }


def execute(args):
    offline_environment()
    guard_counts = install_boundary_guard()
    started_at = datetime.now(timezone.utc).isoformat()
    pub_manifest = verify_manifest(PUBLIC / "freeze_manifest.json")
    verify_manifest(args.private_manifest)
    if sha(args.private_labels) != pub_manifest["private_gold_commitment"]["sha256"]:
        raise ValueError("private gold commitment mismatch")
    public, private = read_json(PUBLIC / "public_benchmark.json"), read_json(args.private_labels)
    data = validate_gold(public, private)
    requests, case_keys = make_requests(data)
    private_ids = {c["case_id"] for c in private["cases"]}
    if subprocess.run(["git", "check-ignore", "-q", str(args.private_output)], cwd=ROOT).returncode:
        raise ValueError("private output is not ignored")
    if args.private_output.exists():
        raise ValueError("refusing to overwrite a previous run")
    SECTION_DEFINITIONS = production_module("brief_schema").SECTION_DEFINITIONS
    create_chunks = production_module("chunking").create_chunks
    load_documents = production_module("document_loader").load_documents
    get_section_queries = production_module("reentry_brief").get_section_queries
    retrieval = production_module("retrieval")
    from unittest.mock import patch
    from .scoring import aggregate, score_case, latency_stats
    definitions = {d.section_id: d for d in SECTION_DEFINITIONS}
    model_path = args.model_snapshot.resolve()
    if not (model_path / "modules.json").is_file() or not any((model_path / n).is_file() for n in ("model.safetensors", "pytorch_model.bin")):
        raise ValueError("local model snapshot unavailable; no download permitted")
    counters = {"model_loads": 0, "encode_calls": 0, "encoded_texts": 0, "document_encode_calls": 0, "document_texts": 0, "query_encode_calls": 0, "query_texts": 0, "openai_requests": 0, "llm_calls": 0, "summary_calls": 0, "external_embedding_requests": 0}
    t = time.perf_counter()
    native_model = retrieval.SentenceTransformer(str(model_path), local_files_only=True)
    model_load_ms = (time.perf_counter()-t)*1000
    counters["model_loads"] += 1
    class CountedModel:
        mode = "document"
        def encode(self, texts, **kwargs):
            counters["encode_calls"] += 1
            counters["encoded_texts"] += len(texts)
            counters[self.mode+"_encode_calls"] += 1
            counters[self.mode+"_texts"] += len(texts)
            return native_model.encode(texts, **kwargs)
    counted = CountedModel()
    indices, corpora, view_stats = {}, {}, {}
    for view in sorted({r.view_id for r in requests.values()}):
        request = next(r for r in requests.values() if r.view_id == view)
        root = safe_relative(ROOT, request.source_root)
        t = time.perf_counter()
        documents = load_documents(EligibleRoot(root, request.sources))
        chunks = create_chunks(documents)
        raw = {s: safe_relative(root, s).read_text(encoding="utf-8") for s in request.sources}
        assert all(d.content == raw[d.source].strip() for d in documents)
        preparation_ms = (time.perf_counter()-t)*1000
        t = time.perf_counter()
        with patch.object(retrieval, "SentenceTransformer", lambda name: counted):
            indices[view] = retrieval.SemanticRetriever(chunks)
        embedding_ms = (time.perf_counter()-t)*1000
        corpora[view] = (raw, len(chunks))
        view_stats[view] = {"documents": len(documents), "chunks": len(chunks), "corpus_preparation_ms": preparation_ms, "document_embedding_ms": embedding_ms, "document_embeddings_reused": True}
    counted.mode = "query"
    traces, cold, warm = {}, {}, {key: [] for key in requests}
    for key in sorted(requests):
        view, section = key
        raw, count = corpora[view]
        selected, calls, duration = production_selection(definitions[section], indices[view], raw, count)
        assert [q for q, _ in calls] == list(get_section_queries(definitions[section]))
        traces[key] = ordered_trace(selected, calls, definitions[section], raw)
        cold[key] = duration
        check, _, _ = production_selection(definitions[section], indices[view], raw, count)
        assert check == selected, "non-deterministic warm-up"
    for repeat in range(WARM_REPETITIONS):
        for key in sorted(requests):
            view, section = key
            raw, count = corpora[view]
            selected, _, duration = production_selection(definitions[section], indices[view], raw, count)
            assert selected == traces[key]["selected_evidence"], "non-deterministic repetition"
            warm[key].append(duration)
        print(f"Completed warm repetition {repeat+1}/{WARM_REPETITIONS}", flush=True)
    # Retrieval ends here. Only now is gold made available to metric scoring.
    passage_map = {p["passage_id"]: p for p in data["passages"]}
    results = [score_case(c, passage_map, traces[case_keys[c["case_id"]]]) for c in data["cases"]]
    tiers = {tier: aggregate(results, tier, private_ids) for tier in ("production", "diagnostic")}
    for tier in tiers:
        tiers[tier]["latency"] = tier_latency(data["cases"], case_keys, cold, warm, tier)
        tiers[tier]["breakdowns"] = supplementary_summaries(results, tier, private_ids)
    _, accounting = execution_accounting(data["cases"], case_keys, traces, cold, warm, results)
    if accounting["derived_query_encode_calls"] != counters["query_encode_calls"]:
        raise ValueError("execution trace/query encode counter mismatch")
    aggregate_data = {"benchmark_version": VERSION, "method": "unchanged production semantic retrieval", "tiers": tiers, "public_cases": public_projection(results, private_ids), "private_case_count": len(private_ids)}
    args.private_output.mkdir(parents=True)
    write_json(args.private_output / "raw_trace.json", {"traces": {"|".join(k): v for k, v in traces.items()}, "case_results": results, "case_keys": {cid: list(key) for cid, key in case_keys.items()}, "warm_samples_ms": {"|".join(k): v for k, v in warm.items()}, "first_query_ms": {"|".join(k): v for k, v in cold.items()}, "per_request_warm": {"|".join(k): latency_stats(v) for k, v in warm.items()}})
    manifest = {"benchmark_version": VERSION, "gold_public_sha256": sha(PUBLIC / "public_benchmark.json"), "gold_private_sha256": sha(args.private_labels), "public_freeze_manifest_sha256": sha(PUBLIC / "freeze_manifest.json"), "private_freeze_manifest_sha256": sha(args.private_manifest), "git_commit": git("rev-parse", "HEAD"), "git_branch": git("branch", "--show-current"), "started_utc": started_at, "finished_utc": datetime.now(timezone.utc).isoformat(), "python": sys.version.split()[0], "platform": sys.platform, "dependencies": {n: importlib.metadata.version(n) for n in ("sentence-transformers", "transformers", "torch", "numpy", "huggingface-hub", "jsonschema")}, "model": retrieval.MODEL_NAME, "model_snapshot_revision": model_path.name, "model_load_ms": model_load_ms, "corpus_views": view_stats, "queries": {sid: {"canonical_question": d.question, "queries": list(get_section_queries(d)), "categories": d.preferred_categories} for sid, d in definitions.items()}, "cutoffs": {"chunk_words": 120, "overlap_words": 30, "query_top_k": "all chunks in eligible view", "selected_evidence": 2, "hit_cutoffs": [1, 3], "excerpt_characters": 1200}, "latency_method": "One first query, one warm-up, then 30 repetitions per unique view/section in fixed sorted round-robin order. One baseline arm; no alternating other arm. Timing includes query encoding, selection and visible excerpt mapping; scoring tail excluded.", "warm_repetitions": WARM_REPETITIONS, "activity": counters, "boundary_guard": guard_counts, "offline": True, "document_embeddings_reused": True, "production_files_modified": False}
    write_json(args.public_output / "aggregate_results.json", aggregate_data)
    manifest["latency_method"] = "One first query, one warm-up, then 30 repetitions per unique view/section in fixed sorted round-robin order. One baseline arm; no other arm to alternate. Timing includes query encoding, cosine ranking, production selection and production excerpts. Source-offset mapping, scoring tail and scoring are excluded. Repeated cases share their unique request's samples. Diagnostic and production summaries overlap requests but are never pooled."
    manifest["harness_sha256"] = {p.relative_to(ROOT).as_posix(): sha(p) for p in sorted(Path(__file__).parent.glob("*.py"))}
    manifest["test_sha256"] = sha(ROOT / "tests/test_temporal_state_baseline.py")
    manifest["aggregate_results_sha256"] = sha(args.public_output / "aggregate_results.json")
    manifest["private_raw_trace_sha256"] = sha(args.private_output / "raw_trace.json")
    manifest["device"] = str(native_model.device)
    manifest["logical_cpu_count"] = os.cpu_count()
    import torch
    manifest["torch_threads"] = torch.get_num_threads()
    manifest["model_snapshot_files"] = {p.relative_to(model_path).as_posix(): sha(p) for p in sorted(model_path.rglob("*")) if p.is_file()}
    manifest["gold_case_population"] = {tier: sum(c["benchmark_tier"] == tier for c in data["cases"]) for tier in tiers}
    manifest["execution_accounting"] = accounting
    write_json(args.public_output / "run_manifest.json", manifest)
    verify_manifest(PUBLIC / "freeze_manifest.json")
    verify_manifest(args.private_manifest)
    print(json.dumps({"completed": True, "cases": len(results), "unique_requests": len(requests), "activity": counters, "boundary_guard": guard_counts}))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--private-labels", required=True, type=Path)
    parser.add_argument("--private-manifest", required=True, type=Path)
    parser.add_argument("--private-output", required=True, type=Path)
    parser.add_argument("--model-snapshot", required=True, type=Path)
    parser.add_argument("--public-output", type=Path, default=ROOT / "outputs/test_results/temporal_state_retrieval_baseline")
    execute(parser.parse_args())


if __name__ == "__main__":
    main()
