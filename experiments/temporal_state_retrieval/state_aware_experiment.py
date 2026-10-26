"""Phase 3B1 adapter and fail-closed, non-executing evaluation skeleton.

Import performs no I/O or runtime imports. Only synthetic selection and dry
preflight construction are enabled; there is no retrieval/scoring entrypoint.
"""
from __future__ import annotations

import copy
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
from types import SimpleNamespace

from .state_aware_selector import StateAwareSelector, validate_payload


FREEZE_VERSION = "phase_3a_metadata_v1"
FREEZE_COMMIT = "2c3a298be80f21f5f2bd21cd486e1944e154d1d9"
PUBLIC_FREEZE_SHA256 = "54af74d896f5b95350730c3e67adb1ac34b335fae6d165c371443b8f53acb65b"
PRIVATE_FREEZE_SHA256 = "a536da8b6bf93941ab10778ab2ad5d10e0fb4e18ec8d9b8365f7a2c2f2dba203"
REQUIRED_PUBLIC_PATHS = frozenset((
    "project_knowledge/process/experiments/temporal_state_retrieval/phase_3_preregistration.md",
    "tests/fixtures/temporal_state_benchmark/public_benchmark.json",
    "tests/fixtures/temporal_state_benchmark/freeze_manifest.json",
    "tests/fixtures/temporal_state_metadata/freeze_manifest.json",
    "tests/fixtures/temporal_state_metadata/record_metadata.schema.json",
    "tests/fixtures/temporal_state_metadata/echo_field.metadata.json",
    "tests/fixtures/temporal_state_metadata/signal_loom.metadata.json",
    "experiments/temporal_state_retrieval/baseline.py",
    "experiments/temporal_state_retrieval/scoring.py",
    "outputs/test_results/temporal_state_retrieval_baseline/aggregate_results.json",
    "outputs/test_results/temporal_state_retrieval_baseline/run_manifest.json",
    "src/brief_schema.py", "src/reentry_brief.py", "src/retrieval.py",
    "src/chunking.py", "src/document_loader.py",
    "experiments/temporal_state_retrieval/state_aware_selector.py",
    "experiments/temporal_state_retrieval/state_aware_experiment.py",
    "tests/test_state_aware_selector.py",
))
PRIVATE_LABELS = frozenset(("phase_1_gold", "phase_1_manifest", "record_metadata", "metadata_manifest"))
INPUT_CHANNEL = "production_query_results_after_category_filter"
ONE_SHOT_RULES = (
    "Create an exclusive immutable pre-run lock before formal execution.",
    "The first case-level candidate score consumes v1, regardless of outcome.",
    "A pre-score technical failure is retained and requires manual review; no automatic retry.",
    "Post-run metrics may be checked from saved traces only; never rerun selection to replace results.",
    "An implementation correction preserves v1 and requires a new preregistration/version.",
)
FUTURE_STAGES = (
    "exclusive_pre_run_lock", "exact_phase_2_adapter_and_four_views",
    "assert_original_query_candidates", "isolated_selection", "persist_selection_trace",
    "score_after_selection_separate_tiers", "private_details_public_aggregates",
)


def prepare_production_bridge():
    """Load the existing baseline's production module, never a model instance.

    The bridge replays already-filtered arrays, not semantic retrieval. Minimal
    proxies carry an allowed category solely to make the original category gate
    an identity operation; original corpus categories are checked upstream.
    """
    from . import baseline
    production = baseline.production_module("reentry_brief")
    definitions = {d.section_id: d for d in production.SECTION_DEFINITIONS}

    def choose(section, lists):
        definition = definitions[section]
        queries = production.get_section_queries(definition)
        total = max((len(q) for q in lists), default=0)
        calls = []

        class Replay:
            def retrieve(self, query, top_k):
                index = len(calls)
                if index >= 2 or query != queries[index] or top_k != total:
                    raise ValueError("Production query replay contract changed")
                calls.append(query)
                return [SimpleNamespace(score=row["score"], chunk=SimpleNamespace(
                    chunk_id=row["chunk_id"], category=definition.preferred_categories[0]
                )) for row in lists[index]]

        results = production.retrieve_diverse_evidence(definition, Replay(), total_chunks=total, limit=2)
        return [row.chunk.chunk_id for row in results]

    return production, choose


def project_candidates(section, calls, definition, source_records, metadata_records, *, production, eligible_record_ids):
    """Fresh allowlist projection of the actual production query channel.

    Full metadata is confined to this adapter. No gold object is accepted. A
    missing state is explicitly unknown here, but formal preflight requires
    complete metadata. Return missing IDs only as adapter-side diagnostics.
    """
    if section != definition.section_id or len(calls) != 2:
        raise ValueError("Section or query count mismatch")
    expected_queries = production.get_section_queries(definition)
    state_map = {}
    for record in metadata_records:
        rid = record["record_id"]
        if rid in state_map:
            raise ValueError("Duplicate metadata identity")
        state_map[rid] = record["record_state"]
    lists = []
    for index, (query, results) in enumerate(calls):
        if query != expected_queries[index]:
            raise ValueError("Original query order/text mismatch")
        if any(source_records[item.chunk.source] not in eligible_record_ids for item in results):
            raise ValueError("Candidate outside the frozen eligible view")
        eligible = production.select_evidence(results, definition.preferred_categories, limit=len(results))
        lists.append([{"chunk_id": item.chunk.chunk_id,
                       "record_id": source_records[item.chunk.source], "score": item.score}
                      for item in eligible])
    ids = {row["record_id"] for rows in lists for row in rows}
    missing = sorted(ids - state_map.keys())
    payload = {"section_id": section, "ordered_eligible_candidates": lists,
               "eligible_record_states": {rid: state_map.get(rid, "unknown") for rid in sorted(ids)}}
    assert_same_candidates(payload, lists, source_channel=INPUT_CHANNEL)
    return payload, {"missing_metadata_count": len(missing), "missing_record_ids": missing}


def assert_same_candidates(payload, original_query_projection, *, source_channel):
    validate_payload(payload)
    if source_channel != INPUT_CHANNEL:
        raise ValueError("Evaluation-only rankings are not a candidate channel")
    if payload["ordered_eligible_candidates"] != original_query_projection:
        raise ValueError("Candidate identity, score or order changed")
    # Full eligible retrieval has identical membership in both query channels.
    first, second = original_query_projection
    if {r["chunk_id"] for r in first} != {r["chunk_id"] for r in second}:
        raise ValueError("The full eligible query pools differ")


def install_worker_boundary():
    """After trusted code loading, deny file/directory/network/process access."""
    def guard(event, args):
        if event == "open" or event.startswith("socket.") or event in {
            "os.listdir", "os.scandir", "os.remove", "os.rmdir", "os.rename",
            "os.mkdir", "subprocess.Popen", "os.system", "os.chdir", "os.putenv",
        }:
            raise PermissionError("Selector worker I/O boundary")
    sys.addaudithook(guard)


def run_isolated(payload, *, timeout=45, probe_boundary=False):
    validate_payload(payload)
    env = os.environ.copy()
    env.pop("OPENAI_API_KEY", None)
    env.update(PYTHONDONTWRITEBYTECODE="1", HF_HUB_OFFLINE="1", TRANSFORMERS_OFFLINE="1")
    command = [sys.executable, "-B", "-m", __name__, "--selector-worker"]
    if probe_boundary:
        command.append("--probe-boundary")
    result = subprocess.run(command, input=json.dumps(payload), text=True, encoding="utf-8",
                            capture_output=True, timeout=timeout, check=True,
                            cwd=Path(__file__).resolve().parents[2], env=env)
    ids = json.loads(result.stdout)
    pool = {r["chunk_id"] for q in payload["ordered_eligible_candidates"] for r in q}
    if type(ids) is not list or len(ids) > 2 or len(set(ids)) != len(ids) or not set(ids) <= pool:
        raise ValueError("Invalid worker output")
    return ids


def _self_digest_valid(data):
    value = copy.deepcopy(data)
    claimed = value["self_digest"].pop("sha256")
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest() == claimed


def _git_state(root):
    def git(*args):
        return subprocess.check_output(["git", *args], cwd=root, text=True).strip()
    return git("rev-parse", "HEAD"), git("branch", "--show-current")


def _has_freeze_ancestor(root, head):
    return subprocess.run(["git", "merge-base", "--is-ancestor", FREEZE_COMMIT, head],
                          cwd=root, capture_output=True).returncode == 0


def validate_preflight(root, plan, private_inputs):
    """Verify byte commitments only; never parse or score benchmark gold."""
    root = Path(root).resolve()
    if plan["status"] != "implementation_ready_pending_review" or plan["freeze_version"] != FREEZE_VERSION:
        raise ValueError("Unreviewed implementation plan/version mismatch")
    if plan["freeze_commit"] != FREEZE_COMMIT or _git_state(root) != (plan["HEAD"], plan["branch"]) or not _has_freeze_ancestor(root, plan["HEAD"]):
        raise ValueError("Git checkpoint mismatch")
    if plan["execution_authorised"] is not False or plan["one_shot_rules"] != list(ONE_SHOT_RULES):
        raise ValueError("Execution policy mismatch")
    artifact_paths = [item["path"] for item in plan["public_artifacts"]]
    if len(set(artifact_paths)) != len(artifact_paths) or not REQUIRED_PUBLIC_PATHS <= set(artifact_paths):
        raise ValueError("Missing or duplicate required public commitment")
    for item in plan["public_artifacts"]:
        path = (root / item["path"]).resolve()
        relative = Path(item["path"])
        forbidden_roots = ("private_data", "data/study_projects", "data/summary_cache", "data/reviews", "data/study_config")
        if (not path.is_relative_to(root) or ".." in relative.parts
                or any(relative.as_posix() == prefix or relative.as_posix().startswith(prefix + "/") for prefix in forbidden_roots)):
            raise ValueError("Invalid public artifact path")
        if hashlib.sha256(path.read_bytes()).hexdigest() != item["sha256"]:
            raise ValueError("Public artifact hash mismatch")
    if set(private_inputs) != set(plan["private_commitments"]) or set(private_inputs) != PRIVATE_LABELS:
        raise ValueError("Incomplete private hash bindings")
    for label, expected in plan["private_commitments"].items():
        path = Path(private_inputs[label]).resolve()
        if not path.is_relative_to(root / "private_data"):
            raise ValueError("Private commitments must use approved isolated storage")
        if hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            raise ValueError("Private artifact hash mismatch")
    public = json.loads((root / plan["metadata_manifest_path"]).read_text(encoding="utf-8"))
    private = json.loads(Path(private_inputs["metadata_manifest"]).read_text(encoding="utf-8"))
    if hashlib.sha256((root / plan["metadata_manifest_path"]).read_bytes()).hexdigest() != PUBLIC_FREEZE_SHA256:
        raise ValueError("Public freeze ancestor mismatch")
    if plan["private_commitments"]["metadata_manifest"] != PRIVATE_FREEZE_SHA256:
        raise ValueError("Private freeze ancestor mismatch")
    for manifest in (public, private):
        if not _self_digest_valid(manifest) or manifest["version"] != FREEZE_VERSION or manifest["status"] != "researcher_confirmed":
            raise ValueError("Metadata freeze is not valid and confirmed")
    if private["public_manifest"]["sha256"] != hashlib.sha256((root / plan["metadata_manifest_path"]).read_bytes()).hexdigest():
        raise ValueError("Private-to-public freeze link mismatch")
    if public["private_metadata_commitment"]["sha256"] != plan["private_commitments"]["record_metadata"]:
        raise ValueError("Private metadata commitment mismatch")
    if any(plan[key] != public[key] for key in ("phase_1_original_benchmark_criteria", "phase_3_candidate_improvement_criteria")):
        raise ValueError("Frozen success criteria changed")
    baseline_manifest = json.loads((root / "outputs/test_results/temporal_state_retrieval_baseline/run_manifest.json").read_text(encoding="utf-8"))
    views = {key: {field: value[field] for field in ("documents", "chunks")}
             for key, value in baseline_manifest["corpus_views"].items()}
    if plan["intended_case_counts"] != {"production": 18, "diagnostic": 16} or len(views) != 4 or plan["intended_views"] != views:
        raise ValueError("Frozen evaluation population mismatch")
    return {"validated": True, "execution_authorised": False}


def dry_construction(root, plan, private_inputs):
    validated = validate_preflight(root, plan, private_inputs)
    return {**validated, "stages": list(FUTURE_STAGES), "intended_views": copy.deepcopy(plan["intended_views"]),
            "intended_case_counts": copy.deepcopy(plan["intended_case_counts"]), "lock_written": False}


class RunLifecycle:
    """Synthetic-testable one-shot state machine; does not write locks/results."""
    def __init__(self):
        self.state = "not_started"

    def lock_created(self):
        if self.state != "not_started":
            raise RuntimeError("No automatic retry; manual review or a new version is required")
        self.state = "locked_no_scores"

    def first_case_score(self):
        if self.state != "locked_no_scores":
            raise RuntimeError("A locked, unused run is required")
        self.state = "consumed"

    def technical_failure(self):
        if self.state == "locked_no_scores":
            self.state = "stopped_before_scores_requires_review"
        elif self.state != "consumed":
            raise RuntimeError("No run is in progress")


def execute_evaluation(*args, **kwargs):
    raise RuntimeError("Formal evaluation is disabled in Phase 3B1")


def _worker():
    payload = json.loads(sys.stdin.read())
    validate_payload(payload)
    _, baseline_choose = prepare_production_bridge()
    selector = StateAwareSelector(baseline_choose)
    # Import the probe dependency before closing access; no socket is connected.
    if "--probe-boundary" in sys.argv:
        import socket
    install_worker_boundary()
    if "--probe-boundary" in sys.argv:
        for operation in (lambda: open("forbidden_metadata.json"), lambda: socket.socket()):
            try:
                operation()
            except PermissionError:
                pass
            else:
                raise RuntimeError("Worker isolation failed")
    print(json.dumps(selector.select(payload)))


if __name__ == "__main__":
    if "--selector-worker" in sys.argv:
        _worker()
    else:
        execute_evaluation()
