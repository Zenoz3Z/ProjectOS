"""Explicit, offline, one-shot evaluation; import never starts a run.

The Phase 3B1 projection/worker contract is retained. Formal preflight,
execution and trace-only verification require separate, explicit entrypoints.
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
from contextlib import contextmanager
from datetime import datetime, timezone
import importlib.metadata
import math
import re
import stat
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor

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


ROOT = Path(__file__).resolve().parents[2]
IMPLEMENTATION_PARENT = "5e433a591183f84471c2081e8522e19d9b1e4cc6"
FROZEN_INPUT_COMMIT = "25bf8e0c7af38d6c7a395a1e9866de46ecd8d27d"
HASH_CONTRACT = {
    "hash_contract_version": 2,
    "worktree_hash_mode": "raw_bytes_sha256",
    "committed_hash_mode": "git_blob_bytes_sha256",
    "equivalence_mode": "git_clean_filtered_blob_oid",
}
EXPERIMENT_VERSION = "phase_3b_state_aware_v1"
PUBLIC_DIRECTORY = "outputs/test_results/temporal_state_retrieval_state_aware"
LOCK_PATH = PUBLIC_DIRECTORY + "/pre_run_lock.json"
RUNNER_PATH = "experiments/temporal_state_retrieval/state_aware_experiment.py"
SELECTOR_PATH = "experiments/temporal_state_retrieval/state_aware_selector.py"
CANDIDATE_PATH = PUBLIC_DIRECTORY + "/pre_run_manifest_candidate.json"
RUNNER_TEST_PATH = "tests/test_state_aware_experiment.py"
PUBLIC_OUTPUTS = ("candidate_aggregate_results.json", "paired_comparison.json",
                  "phase_3b_report.md", "run_manifest.json", "execution_status.json")
SOURCE_ROOTS = ("data/demo_projects/sample_echo_field", "data/study_projects/P96",
                "tests/fixtures/temporal_state_project/records")
VIEW_RECORDS = {
    "echo_documented_snapshot": tuple(f"EF-R{i:02}" for i in range(1, 5)),
    "p96_final_documented": tuple(f"RS-R{i:02}" for i in range(1, 8)),
    "signal_active": tuple(f"SY-R{i:02}" for i in range(1, 6)),
    "signal_closed": tuple(f"SY-R{i:02}" for i in range(1, 8)),
}
VIEW_SIZES = dict(zip(VIEW_RECORDS, ((4, 12), (7, 49), (5, 5), (7, 8))))
SECTIONS = ("current_intention", "changes_and_reasons", "current_vs_superseded",
            "relevant_feedback", "unresolved_tensions", "possible_next_action")
CONFIRM_EXECUTION = "execute-one-shot-phase_3b_state_aware_v1"
TERMINAL_STATES = frozenset(("execution_failed_before_scoring",
    "execution_failed_after_partial_scoring", "execution_completed", "validation_failed"))


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def safe_path(root, value, *, private=False):
    """Check before any stat/open; no participant-directory enumeration."""
    relative = Path(value)
    if relative.is_absolute() or ".." in relative.parts or re.search(r"(^|[/\\])P0[1-4]([/\\]|$)", str(value)):
        raise ValueError("Forbidden or escaping path")
    path = (Path(root) / relative).resolve()
    if not path.is_relative_to(Path(root).resolve()):
        raise ValueError("Path escapes repository")
    if private and not path.is_relative_to((Path(root) / "private_data").resolve()):
        raise ValueError("Private input/output outside ignored research storage")
    if not private and str(value).replace("\\", "/").startswith(("private_data/", "data/study_projects/", "data/reviews/", "data/summary_cache/", "data/study_config/")):
        raise ValueError("Private path in public commitment")
    return path


class GitView:
    def __init__(self, root):
        self.root = Path(root)

    def call(self, *args):
        return subprocess.check_output(["git", *args], cwd=self.root, text=True, encoding="utf-8").strip()

    def blob(self, commit, path):
        return subprocess.check_output(["git", "show", commit + ":" + path], cwd=self.root)

    def tree_entry(self, commit, path):
        raw = subprocess.check_output(["git", "ls-tree", "-z", commit, "--", path], cwd=self.root)
        rows = raw.rstrip(b"\0").split(b"\0") if raw else []
        if len(rows) != 1:
            raise ValueError("Path is absent or ambiguous in implementation commit")
        header, name = rows[0].split(b"\t", 1)
        mode, kind, oid = header.decode("ascii").split()
        if name.decode("utf-8") != path or kind != "blob" or mode not in {"100644", "100755"}:
            raise ValueError("Implementation path must be a regular tracked file")
        return oid

    def object_bytes(self, oid):
        return subprocess.check_output(["git", "cat-file", "blob", oid], cwd=self.root)

    def clean_attributes(self, path):
        names = ("text", "eol", "filter", "working-tree-encoding", "ident")
        raw = subprocess.check_output(["git", "check-attr", "-z", *names, "--", path], cwd=self.root)
        parts = raw.decode("utf-8").rstrip("\0").split("\0")
        if len(parts) != 3 * len(names) or any(parts[i] != path for i in range(0, len(parts), 3)):
            raise ValueError("Unexpected Git attribute response")
        return {parts[i+1]: parts[i+2] for i in range(0, len(parts), 3)}

    def clean_oid(self, path):
        # Deliberately omit -w: Git applies existing attributes/EOL rules read-only.
        return self.call("hash-object", "--path=" + path, "--", path)

    def raw_oid(self, path):
        return self.call("hash-object", "--no-filters", "--", path)

    def ancestor(self, ancestor, head):
        return subprocess.run(["git", "merge-base", "--is-ancestor", ancestor, head],
                              cwd=self.root, capture_output=True, check=False).returncode == 0

    def ignored(self, path):
        return subprocess.run(["git", "check-ignore", "-q", "--", str(path)],
                              cwd=self.root, capture_output=True, check=False).returncode == 0


class HashContractError(ValueError):
    def __init__(self, message, validation):
        super().__init__(message)
        self.validation = dict(validation, validation_status="rejected", reason=message)


def require_hash_contract(lock):
    if any(lock.get(k) != v or type(lock.get(k)) is not type(v) for k, v in HASH_CONTRACT.items()):
        raise ValueError("Hash contract v2 is required; legacy lock fields are not inferred")


def _regular_worktree_file(root, relative):
    normalized = str(relative).replace("\\", "/")
    parts = Path(normalized)
    if parts.is_absolute() or parts.drive or ":" in normalized or ".." in parts.parts or not parts.parts:
        raise ValueError("Escaping or invalid tracked path")
    if re.search(r"(^|/)P0[1-4](/|$)", normalized):
        raise ValueError("Formal participant path forbidden")
    path = root
    for part in parts.parts:
        path = path / part
        info = path.lstat()
        if stat.S_ISLNK(info.st_mode) or getattr(info, "st_file_attributes", 0) & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400):
            raise ValueError("Symlink or reparse-point tracked path forbidden")
    if not path.resolve().is_relative_to(root) or not path.is_file():
        raise ValueError("Tracked path must be a regular workspace file")
    return path, parts.as_posix()


def _eol_representation(data):
    if b"\0" in data:
        return "binary"
    try:
        data.decode("utf-8")
    except UnicodeDecodeError:
        return "binary"
    crlf = data.count(b"\r\n")
    lf, cr = data.count(b"\n") - crlf, data.count(b"\r") - crlf
    kinds = [name for name, count in (("CRLF", crlf), ("LF", lf), ("CR", cr)) if count]
    return kinds[0] if len(kinds) == 1 else "mixed" if kinds else "none"


def validate_tracked_artifact(root, item, implementation, *, git=None, frozen_workspace_sha256=None):
    """Three independent, fail-closed checks; no byte rewriting or Git object writes."""
    root = Path(root).resolve()
    git = git or GitView(root)
    report = dict(repo_relative_path=item.get("path"), workspace_raw_sha256=None,
        frozen_workspace_sha256=frozen_workspace_sha256 or item.get("workspace_raw_sha256"),
        implementation_commit=implementation, committed_blob_oid=None, committed_blob_sha256=None,
        cleaned_worktree_blob_oid=None, workspace_raw_match=False, committed_blob_match=False,
        worktree_equivalent_to_commit=False, eol_representation=None, validation_status="rejected")
    try:
        if set(item) != {"path", "workspace_raw_sha256", "committed_blob_sha256", "git_blob_oid"}:
            raise ValueError("Artifact requires explicit hash contract v2 fields")
        if any(not re.fullmatch(r"[0-9a-f]{64}", item[k]) for k in ("workspace_raw_sha256", "committed_blob_sha256")):
            raise ValueError("Invalid SHA-256 commitment")
        if not re.fullmatch(r"(?:[0-9a-f]{40}|[0-9a-f]{64})", item["git_blob_oid"]):
            raise ValueError("Invalid Git blob OID")
        path, relative = _regular_worktree_file(root, item["path"])
        data = path.read_bytes()
        raw_hash = hashlib.sha256(data).hexdigest()
        report.update(repo_relative_path=relative, workspace_raw_sha256=raw_hash,
            workspace_raw_match=raw_hash == item["workspace_raw_sha256"] == report["frozen_workspace_sha256"])
        if not report["workspace_raw_match"]:
            raise ValueError("Frozen workspace raw hash mismatch")
        oid = git.tree_entry(implementation, relative)
        blob = git.object_bytes(oid)
        blob_hash = hashlib.sha256(blob).hexdigest()
        report.update(committed_blob_oid=oid, committed_blob_sha256=blob_hash,
            committed_blob_match=oid == item["git_blob_oid"] and blob_hash == item["committed_blob_sha256"],
            eol_representation={"workspace": _eol_representation(data), "committed": _eol_representation(blob)})
        if not report["committed_blob_match"]:
            raise ValueError("Committed blob hash or OID mismatch")
        attrs = git.clean_attributes(relative)
        if set(attrs) != {"text", "eol", "filter", "working-tree-encoding", "ident"}:
            raise ValueError("Incomplete Git clean attributes")
        if any(attrs[k] not in {"unspecified", "unset"} for k in ("filter", "working-tree-encoding", "ident")):
            raise ValueError("Unexpected Git filter, encoding or ident transformation")
        if attrs["text"] not in {"unspecified", "unset", "set", "auto"} or attrs["eol"] not in {"unspecified", "unset", "lf", "crlf"}:
            raise ValueError("Unsupported Git text/EOL attributes")
        binary = report["eol_representation"]["workspace"] == "binary"
        if binary and (attrs["text"] == "set" or (attrs["text"] != "unset" and attrs["eol"] in {"lf", "crlf"})):
            raise ValueError("Binary file incorrectly configured for text EOL conversion")
        cleaned = git.clean_oid(relative)
        report.update(cleaned_worktree_blob_oid=cleaned, worktree_equivalent_to_commit=cleaned == oid)
        if binary and cleaned != git.raw_oid(relative):
            raise ValueError("Git clean rules transformed binary bytes")
        if not report["worktree_equivalent_to_commit"]:
            raise ValueError("Clean-filtered worktree blob differs from implementation commit")
        report["validation_status"] = "validated"
        return report
    except (OSError, subprocess.SubprocessError, ValueError, TypeError, KeyError) as error:
        message = "Git command failed" if isinstance(error, subprocess.SubprocessError) else str(error)
        raise HashContractError(message, report) from error


def check_git_lock(git, lock, lock_bytes):
    implementation = lock["implementation_commit"]
    head = git.call("rev-parse", "HEAD")
    if not re.fullmatch(r"[0-9a-f]{40}", implementation) or head == implementation:
        raise ValueError("Lock must follow an identified implementation commit")
    if not git.ancestor(IMPLEMENTATION_PARENT, implementation) or not git.ancestor(implementation, head):
        raise ValueError("Implementation ancestry mismatch")
    if git.call("branch", "--show-current") != "temporal-state-retrieval-state-aware-v1":
        raise ValueError("Wrong execution branch")
    if git.call("diff", "--name-only", "HEAD") or git.call("diff", "--cached", "--name-only"):
        raise ValueError("Tracked or staged changes at execution")
    changes = git.call("diff", "--name-status", implementation, head).splitlines()
    if changes != ["A\t" + LOCK_PATH]:
        raise ValueError("Only the added public lock may follow implementation")
    if git.blob(head, LOCK_PATH) != lock_bytes:
        raise ValueError("Public lock is not the committed lock")
    return head


def preflight(root, lock_path, private_lock_path, *, git=None):
    """Read-only formal validation. Never import runtime, create state or parse gold."""
    root = Path(root).resolve()
    git = git or GitView(root)
    lock_path = Path(lock_path).resolve()
    if lock_path != root / LOCK_PATH:
        raise ValueError("Only pre_run_lock.json can authorise execution")
    lock_bytes = lock_path.read_bytes()
    lock = json.loads(lock_bytes)
    require_hash_contract(lock)
    required = {"status", "execution_authorised", "candidate_evaluation_run", "run_count_allowed",
        "experiment_version", "implementation_commit", "public_artifacts", "private_commitments",
        "private_lock_sha256", "protocol_sha256", "intended_case_counts", "intended_views",
        "intended_embedding_model", "intended_model_snapshot_revision", "python", "dependencies",
        "phase_1_original_benchmark_criteria", "phase_3_candidate_improvement_criteria",
        "outputs", "score_tolerance", "run_id", "authorised_by", "authorisation_date"}
    if not required <= lock.keys():
        raise ValueError("Missing formal lock fields")
    if (lock["status"] != "execution_authorised" or lock["execution_authorised"] is not True
            or lock["candidate_evaluation_run"] is not False or type(lock["run_count_allowed"]) is not int
            or lock["run_count_allowed"] != 1 or lock["experiment_version"] != EXPERIMENT_VERSION):
        raise ValueError("Formal one-shot authorisation mismatch")
    if not re.fullmatch(r"phase_3b_state_aware_v1_run_[0-9]{8}", lock["run_id"]):
        raise ValueError("Invalid run identity")
    if lock["score_tolerance"] != {"absolute": 0, "relative": 0}:
        raise ValueError("No nonzero score tolerance was frozen")
    expected_outputs = {name: PUBLIC_DIRECTORY + "/" + name for name in PUBLIC_OUTPUTS}
    if lock["outputs"] != expected_outputs:
        raise ValueError("Output paths differ from fixed destinations")
    if (root / PUBLIC_DIRECTORY).resolve() != root / PUBLIC_DIRECTORY:
        raise ValueError("Public output directory cannot redirect through a symlink")
    head = check_git_lock(git, lock, lock_bytes)
    trusted = json.loads(git.blob(FROZEN_INPUT_COMMIT, CANDIDATE_PATH))
    artifacts = lock["public_artifacts"]
    paths = [x["path"] for x in artifacts]
    expected = {x["path"] for x in trusted["public_artifacts"]} | {RUNNER_TEST_PATH}
    if len(paths) != len(set(paths)) or set(paths) != expected:
        raise ValueError("Incomplete or additional public commitments")
    # B2 changes the runner and its review together. Both still have to match
    # the committed implementation bytes; all frozen inputs stay pinned to B1.
    implementation_paths = {RUNNER_PATH,
        "project_knowledge/process/experiments/temporal_state_retrieval/phase_3b_implementation_review.md"}
    immutable = {x["path"]: x["sha256"] for x in trusted["public_artifacts"] if x["path"] not in implementation_paths}
    hash_validation = []
    for item in artifacts:
        safe_path(root, item["path"])
        hash_validation.append(validate_tracked_artifact(root, item, lock["implementation_commit"], git=git,
            frozen_workspace_sha256=immutable.get(item["path"], item.get("workspace_raw_sha256"))))
    for key in ("protocol_sha256", "intended_case_counts", "intended_views", "intended_embedding_model",
                "intended_model_snapshot_revision", "phase_1_original_benchmark_criteria", "phase_3_candidate_improvement_criteria"):
        if lock[key] != trusted[key]:
            raise ValueError("Frozen lock specification mismatch: " + key)
    if lock["python"] != sys.version.split()[0] or any(importlib.metadata.version(n) != v for n, v in lock["dependencies"].items()):
        raise ValueError("Execution environment mismatch")
    if lock["dependencies"] != trusted["dependencies"]:
        raise ValueError("Frozen dependency versions changed")
    private_lock_path = Path(private_lock_path).resolve()
    expected_private_lock = root / "private_data/temporal_state_retrieval_experiment/phase_3b" / lock["run_id"] / "private_pre_run_lock.json"
    if private_lock_path != expected_private_lock or not git.ignored(private_lock_path):
        raise ValueError("Private lock is not Git-ignored")
    if digest(private_lock_path) != lock["private_lock_sha256"]:
        raise ValueError("Private lock hash mismatch")
    private = read_json(private_lock_path)
    if private["implementation_commit"] != lock["implementation_commit"] or private["run_id"] != lock["run_id"]:
        raise ValueError("Private lock identity mismatch")
    baseline_manifest = read_json(root / "outputs/test_results/temporal_state_retrieval_baseline/run_manifest.json")
    commitments = dict(trusted["private_commitments"], baseline_trace=baseline_manifest["private_raw_trace_sha256"])
    if lock["private_commitments"] != commitments or set(private["inputs"]) != set(commitments):
        raise ValueError("Private commitment set changed")
    bindings = {}
    for label, relative in private["inputs"].items():
        path = safe_path(root, relative, private=True)
        if not path.is_relative_to(root / "private_data/temporal_state_retrieval_experiment") or not git.ignored(path) or digest(path) != commitments[label]:
            raise ValueError("Private commitment hash mismatch")
        bindings[label] = path
    # Identity inventory is separate from gold. Full gold is read only after selection.
    inventory = private["record_inventory"]
    expected_ids = set().union(*map(set, VIEW_RECORDS.values()))
    if len(inventory) != 18 or {r["record_id"] for r in inventory} != expected_ids:
        raise ValueError("Incomplete record inventory")
    public_freeze = read_json(root / "tests/fixtures/temporal_state_metadata/freeze_manifest.json")
    private_freeze = read_json(bindings["metadata_manifest"])
    protected = {x["path"]: x["sha256"] for x in private_freeze["protected_private_inputs"]}
    public_records = {r["record_id"]: r for r in public_freeze["public_source_inventory"]}
    metadata = []
    for path in (root / "tests/fixtures/temporal_state_metadata/echo_field.metadata.json",
                 root / "tests/fixtures/temporal_state_metadata/signal_loom.metadata.json", bindings["record_metadata"]):
        metadata.extend(read_json(path)["records"])
    annotations = {r["record_id"]: r for r in metadata}
    if len(metadata) != 18 or set(annotations) != expected_ids:
        raise ValueError("Metadata inventory mismatch")
    for row in inventory:
        if set(row) != {"record_id", "project_id", "path", "sha256", "source_category"}:
            raise ValueError("Inventory must contain identity fields only")
        rid, path_text = row["record_id"], row["path"]
        if not any(path_text.startswith(prefix + "/") for prefix in SOURCE_ROOTS) or ".." in Path(path_text).parts:
            raise ValueError("Source outside permitted roots")
        expected_root = SOURCE_ROOTS[0 if rid.startswith("EF") else 1 if rid.startswith("RS") else 2]
        if not path_text.startswith(expected_root + "/"):
            raise ValueError("Record/project root mismatch")
        path = (root / path_text).resolve()
        if not path.is_relative_to(root / expected_root) or digest(path) != row["sha256"]:
            raise ValueError("Source identity/hash mismatch")
        ann = annotations[rid]
        if (row["project_id"], row["source_category"]) != (ann["project_id"], ann["source_category"]):
            raise ValueError("Metadata identity/category mismatch")
        if rid in public_records:
            if any(row[k] != public_records[rid][k] for k in row):
                raise ValueError("Public source inventory changed")
        elif protected.get(path_text) != row["sha256"]:
            raise ValueError("Private source not frozen")
    output = safe_path(root, private["output_root"], private=True)
    expected_private = root / "private_data/temporal_state_retrieval_experiment/phase_3b" / lock["run_id"]
    if output != expected_private or not git.ignored(output / "execution_state.json"):
        raise ValueError("Private output is not the ignored run directory")
    if (output / "execution_state.json").exists():
        raise ValueError("Existing execution state: no retry or resume")
    for p in [*(root / value for value in lock["outputs"].values()),
              *(output / n for n in ("raw_trace.json", "case_traces", "selection_trace.json", "private_run_manifest.json", "p96_case_results.json", "p96_case_analysis.md", "failure_log.json"))]:
        if p.exists():
            raise ValueError("Existing formal output: refusing overwrite")
    model = Path(private["model_snapshot"]).resolve()
    if model.is_relative_to(root) or model.name != lock["intended_model_snapshot_revision"] or not (model / "modules.json").is_file():
        raise ValueError("Local model snapshot unavailable")
    if not any((model / n).is_file() for n in ("model.safetensors", "pytorch_model.bin")):
        raise ValueError("Local model weights unavailable; download forbidden")
    for name, expected_hash in baseline_manifest["model_snapshot_files"].items():
        relative = Path(name)
        target = (model / relative).resolve()
        # HF snapshots may link to the cache's sibling blobs directory. Hash
        # each explicit frozen file, but never follow a model link into the repo.
        if relative.is_absolute() or ".." in relative.parts or target.is_relative_to(root) or digest(target) != expected_hash:
            raise ValueError("Local model snapshot hash mismatch")
    return {"root": root, "lock": lock, "lock_hash": hashlib.sha256(lock_bytes).hexdigest(),
            "private_lock_hash": digest(private_lock_path), "lock_commit": head, "private": private,
            "bindings": bindings, "inventory": inventory, "metadata": metadata,
            "model_snapshot": model, "output": output, "baseline_manifest": baseline_manifest,
            "hash_validation": hash_validation}


def assert_public_safe(value):
    """Reject source-bearing structures and private locators before any public write."""
    forbidden = {"excerpt", "quote", "source", "source_root", "path", "passages", "gold", "gold_labels",
                 "expected_evidence", "private_path", "case_results", "record_inventory", "raw_trace",
                 "summary", "text", "content", "notes", "rationale", "locator", "gold_case", "evidence",
                 "selected_evidence", "required_evidence_roles", "acceptable_gold_passages", "expected_support_status"}
    def visit(obj):
        if isinstance(obj, dict):
            if set(obj) & forbidden:
                raise ValueError("Private/source field in public output")
            for key, child in obj.items():
                visit(key); visit(child)
        elif isinstance(obj, list):
            for child in obj: visit(child)
        elif isinstance(obj, str):
            if re.search(r"(?i)(?:\bP0[1-4]\b|\bP96\b|\bRS-(?:R)?\d+\b|private_data[/\\]|[a-z]:[\\/]|/Users/|/home/|\bsk-(?:proj-)?[\w-]{12,}|[\w.+-]+@[\w.-]+\.[a-z]{2,})", obj):
                raise ValueError("Private locator or identifier in public output")
    visit(value)


class AtomicWriter:
    """Same-directory durable temporary write; publish without replacing existing results."""
    def write(self, path, value, *, replace=False, public=False, text=False):
        path = Path(path)
        if replace and (public or path.name != "execution_state.json"):
            raise ValueError("Only private execution state may be atomically replaced")
        if public: assert_public_safe(value)
        raw = value.encode("utf-8") if text else (json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + "\n").encode("utf-8")
        path.parent.mkdir(parents=True, exist_ok=True)
        fd, temporary = tempfile.mkstemp(prefix="." + path.name + ".", suffix=".tmp", dir=path.parent)
        try:
            with os.fdopen(fd, "wb") as stream:
                stream.write(raw); stream.flush(); os.fsync(stream.fileno())
            if replace:
                os.replace(temporary, path)
            else:
                # A hard-link publication is atomic and fails if destination exists.
                os.link(temporary, path)
        finally:
            if os.path.exists(temporary): os.unlink(temporary)


class ExecutionState:
    def __init__(self, context, writer, clock):
        self.path = context["output"] / "execution_state.json"
        self.writer, self.clock = writer, clock
        lock = context["lock"]
        self.data = {"status": "execution_started", "run_id": lock["run_id"],
            "experiment_version": EXPERIMENT_VERSION, "implementation_commit": lock["implementation_commit"],
            "lock_commit": context["lock_commit"], "lock_hash": context["lock_hash"],
            "started_at": clock.utc(), "scored_case_count": 0, "candidate_evaluation_run": False}

    def start(self):
        self.writer.write(self.path, self.data)  # Exclusive publication; no resume/reset.

    def record(self, trace, result, *, baseline_result, gold_case):
        if self.data["status"] != "execution_started":
            raise RuntimeError("Cannot append to a terminal execution")
        cid = result["case_id"]
        if not re.fullmatch(r"[A-Z]{2,8}-[0-9]{1,4}", cid):
            raise ValueError("Invalid case identity")
        self.writer.write(self.path.parent / "case_traces" / (cid + ".json"),
                          {"trace": trace, "result": result, "baseline_result": baseline_result, "case": gold_case})
        self.data["scored_case_count"] += 1
        self.data["candidate_evaluation_run"] = True
        self.writer.write(self.path, self.data, replace=True)

    def finish(self, status):
        if status not in TERMINAL_STATES:
            raise ValueError("Invalid terminal state")
        self.data.update(status=status, finished_at=self.clock.utc())
        self.writer.write(self.path, self.data, replace=True)


class Clock:
    def tick(self): return time.perf_counter()
    def utc(self): return datetime.now(timezone.utc).isoformat()


class SelectorProcess:
    """Persistent restricted worker; IPC overhead remains in request timing."""
    def __init__(self, *, command=None, timeout=45):
        self.command = command or [sys.executable, "-B", "-m", "experiments.temporal_state_retrieval.state_aware_experiment", "--selector-stream"]
        self.timeout = timeout
        self.process = self.pool = self.errors = None

    def __enter__(self):
        env = os.environ.copy(); env.pop("OPENAI_API_KEY", None)
        env.update(PYTHONDONTWRITEBYTECODE="1", HF_HUB_OFFLINE="1", TRANSFORMERS_OFFLINE="1")
        self.errors = tempfile.TemporaryFile()
        try:
            self.process = subprocess.Popen(self.command, cwd=ROOT, env=env, stdin=subprocess.PIPE,
                stdout=subprocess.PIPE, stderr=self.errors, text=True, encoding="utf-8", bufsize=1)
            self.pool = ThreadPoolExecutor(max_workers=1)
            if self._read() != "READY": raise RuntimeError("Selector worker did not initialise")
            return self
        except BaseException:
            self.__exit__(*sys.exc_info()); raise

    def _read(self):
        try:
            line = self.pool.submit(self.process.stdout.readline).result(timeout=self.timeout)
            if not line: raise RuntimeError("Selector worker exited without response")
            return line.rstrip("\r\n")
        except BaseException:
            self.process.kill(); self.process.wait(); raise

    def select(self, payload):
        validate_payload(payload)
        self.process.stdin.write(json.dumps(payload, allow_nan=False) + "\n"); self.process.stdin.flush()
        ids = json.loads(self._read())
        pool = {r["chunk_id"] for q in payload["ordered_eligible_candidates"] for r in q}
        if type(ids) is not list or len(ids) > 2 or len(set(ids)) != len(ids) or not set(ids) <= pool:
            raise ValueError("Invalid worker selection")
        return ids

    def __exit__(self, *exc):
        try:
            if self.process is not None:
                try:
                    if self.process.stdin and not self.process.stdin.closed:
                        try: self.process.stdin.close()
                        except BrokenPipeError: pass  # Child has already failed; still reap it.
                finally:
                    try: self.process.wait(timeout=self.timeout)
                    except subprocess.TimeoutExpired:
                        self.process.kill(); self.process.wait()
                    finally:
                        if self.process.stdout: self.process.stdout.close()
        finally:
            if self.pool is not None: self.pool.shutdown(wait=True)
            if self.errors is not None: self.errors.close()
        if self.process is not None and self.process.returncode != 0 and (not exc or exc[0] is None):
            raise RuntimeError("Selector worker exited unsuccessfully")


class CandidateMismatch(ValueError):
    def __init__(self, message, actual, expected):
        super().__init__(message)
        self.details = {"actual_query_channels": actual, "frozen_query_channels": expected}


def compare_candidates(current, frozen):
    """Original query channels only; no tolerance or selected-first substitution."""
    if len(current) != len(frozen): raise CandidateMismatch("Query count mismatch", current, frozen)
    for actual, expected in zip(current, frozen):
        if actual["query"] != expected["query"]: raise CandidateMismatch("Query text/order mismatch", current, frozen)
        rows, originals = actual["eligible_results"], expected["eligible_results"]
        if len(rows) != len(originals): raise CandidateMismatch("Candidate count mismatch", current, frozen)
        for row, before in zip(rows, originals):
            if any(row[k] != before[k] for k in ("chunk_id", "source", "category", "score")):
                raise CandidateMismatch("Candidate identity/order/category/score mismatch", current, frozen)


class DefaultDependencies:
    """Lazy frozen production functions. Construction/import never loads a model."""
    synthetic = False
    def __init__(self, *, clock=None, writer=None, candidate_adapter=None):
        self.clock, self.writer = clock or Clock(), writer or AtomicWriter()
        self.candidate_adapter = candidate_adapter or project_candidates
        self.activity = dict.fromkeys(("model_loads", "encode_calls", "document_encode_calls",
            "query_encode_calls", "document_texts", "query_texts", "openai_requests", "llm_calls", "summary_calls"), 0)

    def activate(self, context):
        from . import baseline
        baseline.offline_environment()
        root = context["root"]
        study = root / "data/study_projects"
        forbidden = [root / p for p in ("data/reviews", "data/summary_cache", "data/study_config")]
        def guard(event, args):
            if event in {"socket.connect", "socket.getaddrinfo"}:
                raise RuntimeError("Offline experiment: network denied")
            if event in {"open", "os.listdir", "os.scandir"} and args and isinstance(args[0], (str, bytes, os.PathLike)):
                p = Path(os.fsdecode(args[0])).resolve()
                if (p.is_relative_to(study) and not p.is_relative_to(study / "P96")) or any(p.is_relative_to(x) for x in forbidden):
                    raise RuntimeError("Participant/cache/review enumeration or access forbidden")
        sys.addaudithook(guard)
        self.b = baseline
        self.production, _ = prepare_production_bridge()
        self.retrieval = baseline.production_module("retrieval")
        self.document_loader = baseline.production_module("document_loader").load_documents
        self.chunk_creator = baseline.production_module("chunking").create_chunks
        self.definitions = {d.section_id: d for d in self.production.SECTION_DEFINITIONS}

    def model_loader(self, snapshot):
        self.activity["model_loads"] += 1
        native = self.retrieval.SentenceTransformer(str(snapshot), local_files_only=True)
        owner = self
        class CountedModel:
            mode = "document"
            def encode(self, texts, **kwargs):
                owner.activity["encode_calls"] += 1
                owner.activity[self.mode + "_encode_calls"] += 1
                owner.activity[self.mode + "_texts"] += len(texts)
                t = owner.clock.tick(); result = native.encode(texts, **kwargs)
                owner.encode_ms += (owner.clock.tick() - t) * 1000
                return result
        self.encode_ms = 0
        self.environment = {"device": str(native.device), "logical_cpu_count": os.cpu_count()}
        import torch
        self.environment["torch_threads"] = torch.get_num_threads()
        return CountedModel()

    def retriever_factory(self, chunks, model):
        # Inject the one preloaded model without monkeypatching production globals.
        # These are the unchanged constructor's index fields and encode options;
        # retrieve itself is the original SemanticRetriever method.
        if not chunks: raise ValueError("Empty corpus")
        instance = object.__new__(self.retrieval.SemanticRetriever)
        instance.chunks, instance.model = chunks, model
        instance.chunk_embeddings = model.encode([c.content for c in chunks], convert_to_numpy=True,
            normalize_embeddings=True, show_progress_bar=False)
        return instance

    def prepare_views(self, context, model):
        indexed = {r["record_id"]: r for r in context["inventory"]}
        views, stats = {}, {}
        for view, ids in VIEW_RECORDS.items():
            records = [indexed[rid] for rid in ids]
            prefix = next(p for p in SOURCE_ROOTS if records[0]["path"].startswith(p + "/"))
            sources = tuple(sorted(r["path"][len(prefix)+1:] for r in records))
            directory = context["root"] / prefix
            t = self.clock.tick()
            documents = self.document_loader(self.b.EligibleRoot(directory, sources))
            chunks = self.chunk_creator(documents)
            raw = {s: (directory / s).read_text(encoding="utf-8") for s in sources}
            if (len(documents), len(chunks)) != VIEW_SIZES[view] or any(d.content != raw[d.source].strip() for d in documents):
                raise ValueError("Frozen corpus mismatch")
            prep_ms = (self.clock.tick()-t)*1000
            t = self.clock.tick(); index = self.retriever_factory(chunks, model)
            stats[view] = {"documents": len(documents), "chunks": len(chunks),
                "corpus_preparation_ms": prep_ms, "document_encode_ms": (self.clock.tick()-t)*1000}
            states = [r for r in context["metadata"] if r["record_id"] in ids]
            views[view] = {"index": index, "raw": raw, "count": len(chunks), "metadata": states,
                "source_records": {r["path"][len(prefix)+1:]: r["record_id"] for r in records}, "ids": set(ids)}
        model.mode = "query"
        return views, stats

    def selector(self): return SelectorProcess()

    def frozen_traces(self, context):
        # Baseline outcomes remain outside selector payloads. No gold file is parsed here.
        return read_json(context["bindings"]["baseline_trace"])

    def request(self, view, section, frozen, selector):
        definition = self.definitions[section]
        clock = self.clock
        class TimedRecorder(self.b.RecordingRetriever):
            elapsed_ms = 0
            def retrieve(self, query, top_k):
                start = clock.tick()
                result = super().retrieve(query, top_k)
                self.elapsed_ms += (clock.tick()-start)*1000
                return result
        recorder = TimedRecorder(view["index"])
        query_ms = self.encode_ms
        t = self.clock.tick()
        baseline_selected = self.production.retrieve_diverse_evidence(definition, recorder, total_chunks=view["count"], limit=2)
        retrieval_baseline_ms = (self.clock.tick()-t)*1000
        query_ms = self.encode_ms-query_ms
        channel = [{"query": q, "eligible_results": [{"chunk_id": r.chunk.chunk_id, "source": r.chunk.source,
                    "category": r.chunk.category, "score": r.score} for r in self.production.select_evidence(
                        results, definition.preferred_categories, limit=len(results))]} for q, results in recorder.calls]
        compare_candidates(channel, frozen["queries"])
        if [r.chunk.chunk_id for r in baseline_selected] != [r["chunk_id"] for r in frozen["selected_evidence"]]:
            raise ValueError("Baseline selection changed")
        t = self.clock.tick()
        payload, notes = self.candidate_adapter(section, recorder.calls, definition, view["source_records"], view["metadata"],
            production=self.production, eligible_record_ids=view["ids"])
        if notes["missing_metadata_count"]: raise ValueError("Missing formal metadata")
        ids = selector.select(payload)
        overhead = (self.clock.tick()-t)*1000
        selected = []
        for position, cid in enumerate(ids):
            original = next((r for r in recorder.calls[min(position, 1)][1] if r.chunk.chunk_id == cid), None)
            if original is None: raise ValueError("Selected identity outside its full query channel")
            selected.append(original)
        t = self.clock.tick()
        excerpts = [self.production.create_excerpt(r.chunk.content) for r in selected]
        excerpt_ms = (self.clock.tick()-t)*1000
        visible = [self.b.visible_evidence(r, view["raw"][r.chunk.source]) for r in selected]
        if excerpts != [r["excerpt"] for r in visible]: raise ValueError("Excerpt mapping mismatch")
        trace = self.b.ordered_trace(visible, recorder.calls, definition, view["raw"])
        return trace, {"total_ms": retrieval_baseline_ms+overhead+excerpt_ms,
                       "retrieval_and_baseline_selection_ms": retrieval_baseline_ms,
                       "baseline_selection_ms": retrieval_baseline_ms-recorder.elapsed_ms,
                       "retrieval_ms": recorder.elapsed_ms,
                       "query_encode_ms": query_ms, "selector_overhead_ms": overhead, "excerpt_ms": excerpt_ms}

    def load_gold(self, context):
        public = read_json(context["root"] / "tests/fixtures/temporal_state_benchmark/public_benchmark.json")
        private = read_json(context["bindings"]["phase_1_gold"])
        data = self.b.validate_gold(public, private, context["root"])
        inventory = {r["record_id"]: r for r in context["inventory"]}
        for r in data["record_catalog"]:
            item = inventory[r["record_id"]]
            if item["path"] != r["source_root"]+"/"+r["source"] or item["sha256"] != r["sha256"]:
                raise ValueError("Post-selection identity join disagrees with frozen catalogue")
        return data, {c["case_id"] for c in private["cases"]}

    def scorer(self, case, passages, trace):
        from .scoring import score_case
        return score_case(case, passages, trace)


def result_bundle(data, results, baseline_results, traces, baseline_traces, private_ids, timings, lock, environment_comparable):
    """Deterministic reporting over saved data only; no selector or model access."""
    from . import baseline, scoring
    cases = data["cases"]
    keys = {c["case_id"]: (c["context_id"], c["section_id"]) for c in cases}
    cold = {tuple(k.split("|")): v["first"]["total_ms"] for k, v in timings.items()}
    warm = {tuple(k.split("|")): [r["total_ms"] for r in v["warm"]] for k, v in timings.items()}
    tiers, paired, deltas = {}, {}, {}
    original = {r["case_id"]: r for r in baseline_results}
    if len(original) != len(cases) or set(original) != {r["case_id"] for r in results}:
        raise ValueError("Baseline/candidate case population mismatch")
    for tier in ("production", "diagnostic"):
        tiers[tier] = scoring.aggregate(results, tier, private_ids)
        tiers[tier]["latency"] = baseline.tier_latency(cases, keys, cold, warm, tier)
        reqs = sorted({keys[c["case_id"]] for c in cases if c["benchmark_tier"] == tier})
        tiers[tier]["timing_components"] = {
            component: scoring.latency_stats([row[component] for key in reqs for row in timings["|".join(key)]["warm"]])
            for component in ("selector_overhead_ms", "query_encode_ms", "retrieval_and_baseline_selection_ms", "baseline_selection_ms", "retrieval_ms", "excerpt_ms")}
        prior = scoring.aggregate(baseline_results, tier, private_ids)
        deltas[tier] = {}
        for metric, current in tiers[tier]["metrics"].items():
            before = prior["metrics"][metric]
            deltas[tier][metric] = {name: {"baseline": before[name], "candidate": current[name],
                "delta": None if before[name] is None or current[name] is None else current[name]-before[name]}
                for name in ("numerator", "denominator", "value")}
        buckets = {name: {"count": 0, "public_case_ids": [], "private_case_count": 0} for name in
                   ("gained", "lost", "unchanged_pass", "unchanged_fail", "insufficient_boundary_cases", "selection_changed", "selection_unchanged")}
        for row in (r for r in results if r["benchmark_tier"] == tier):
            cid = row["case_id"]; old = original[cid]
            old_pass, new_pass = old["evidence_coverage_status"] == "pass", row["evidence_coverage_status"] == "pass"
            if row["expected_support_status"] == "insufficient": label = "insufficient_boundary_cases"
            elif old_pass and new_pass: label = "unchanged_pass"
            elif old_pass: label = "lost"
            elif new_pass: label = "gained"
            else: label = "unchanged_fail"
            key = "|".join(keys[cid])
            changed = [x["chunk_id"] for x in traces[key]["selected_evidence"]] != [x["chunk_id"] for x in baseline_traces[key]["selected_evidence"]]
            for name in (label, "selection_changed" if changed else "selection_unchanged"):
                buckets[name]["count"] += 1
                if cid in private_ids: buckets[name]["private_case_count"] += 1
                else: buckets[name]["public_case_ids"].append(cid)
        paired[tier] = buckets
    primary, before = tiers["production"]["metrics"], scoring.aggregate(baseline_results, "production", private_ids)["metrics"]
    criteria = lock["phase_3_candidate_improvement_criteria"]
    def minimum(metric, required):
        m = primary[metric]
        return m["denominator"] == required[1] and m["numerator"] >= required[0]
    def increases(metric):
        a, b = primary[metric]["value"], before[metric]["value"]
        return a is not None and b is not None and a > b
    median = tiers["production"]["latency"]["warm"]["median_ms"]
    gates3 = {
        "all_required_roles": minimum("all_required_roles_at_2", criteria["all_required_roles_minimum"]),
        "preserve_baseline_passes": paired["production"]["lost"]["count"] == 0,
        "hit_at_3": minimum("hit_at_3", criteria["hit_at_3_minimum"]),
        "pair_coverage": minimum("pair_coverage_at_2", criteria["pair_coverage_at_2_minimum"]),
        "closure": minimum("closure_at_2", criteria["closure_at_2_minimum"]),
        "false_current": primary["false_current_all_case_lower_bound"]["denominator"] == criteria["known_false_current_maximum"][1]
            and primary["false_current_all_case_lower_bound"]["numerator"] <= criteria["known_false_current_maximum"][0],
        "future_record_leakage": True,  # exact view allowlists and candidate equality already passed
        "warm_latency": environment_comparable and median <= criteria["production_warm_median_limit_ms"],
        "primary_improvement": increases("all_required_roles_at_2"),
    }
    projects = sorted({c["project_id"] for c in cases if c["benchmark_tier"] == "production"})
    project_changes = []
    for project in projects:
        after = scoring.aggregate([r for r in results if r["project_id"] == project], "production")["metrics"]["role_coverage_at_2"]["value"]
        prior = scoring.aggregate([r for r in baseline_results if r["project_id"] == project], "production")["metrics"]["role_coverage_at_2"]["value"]
        project_changes.append(after-prior)
    echo = [r for r in results if r["project_id"] == "sample_echo_field" and r["benchmark_tier"] == "production"]
    next_cases = [c for c in cases if c["project_id"] == "sample_echo_field" and c["benchmark_tier"] == "production" and c["section_id"] == "possible_next_action"]
    first_task = False
    if len(next_cases) == 1:
        c = next_cases[0]; tr = traces["|".join(keys[c["case_id"]])]
        passage_map = {p["passage_id"]: p for p in data["passages"]}
        matched = scoring.matched_ids(c, passage_map, tr["selected_evidence"][:1])
        roles = set().union(*(scoring.eligible_roles(c, passage_map[p]) for p in matched))
        first_task = set(c["required_evidence_roles"]) <= roles
    gates1 = {
        "echo_hit_at_3": len(echo) == 6 and all(r["metrics"]["hit_at_3"] == 1 for r in echo),
        "echo_first_task_complete": first_task,
        "echo_current_superseded_pair": any(r["section_id"] == "current_vs_superseded" and r["metrics"]["pair_coverage_at_2"] == 1 for r in echo),
        "strict_pair_improvement": increases("pair_coverage_at_2"),
        "strict_role_improvement": increases("role_coverage_at_2") and sum(x > 0 for x in project_changes) >= 2 and all(x >= 0 for x in project_changes),
        "all_explicit_closure": primary["closure_at_2"]["numerator"] == primary["closure_at_2"]["denominator"] == 3,
        "applicability_preserved": primary["applicability_evidence_at_2"]["value"] >= before["applicability_evidence_at_2"]["value"],
        "false_current_preserved": gates3["false_current"],
        "insufficient_boundary_preserved": sum(r["misleading_negative_exposure"] for r in results if r["expected_support_status"] == "insufficient") <= sum(r["misleading_negative_exposure"] for r in baseline_results if r["expected_support_status"] == "insufficient"),
        "warm_latency": environment_comparable and median < 300,
        "frozen_sources_views_labels_and_separate_tiers": True,
    }
    conclusions = {}
    for phase, gates, phrase in (("phase_3", gates3, "the preregistered Phase 3 improvement criteria"),
                                  ("phase_1", gates1, "the original Phase 1 criteria")):
        passed = all(gates.values())
        conclusions[phase] = {"passed": passed, "checks": gates,
            "statement": ("met " if passed else "did not meet ") + phrase,
            "outcome": "passed" if passed else "mixed" if paired["production"]["gained"]["count"] else "failed"}
    return {"experiment_version": EXPERIMENT_VERSION, "tiers": tiers, "deltas": deltas,
            "criteria": conclusions, "environment_comparable": environment_comparable}, paired


def _report(aggregate, paired):
    lines = ["# State-aware retrieval evaluation", "", "One preregistered technical comparison; no participant-validation claim.", ""]
    for tier in ("production", "diagnostic"):
        lines += ["## " + tier.title(), "", "| Metric | Numerator | Denominator | Value |", "|---|---:|---:|---:|"]
        for name, metric in aggregate["tiers"][tier]["metrics"].items():
            lines.append(f"| {name} | {metric['numerator']} | {metric['denominator']} | {metric['value']} |")
        lines += ["", "Warm median (ms): " + str(aggregate["tiers"][tier]["latency"]["warm"]["value"]), "",
                  "Paired gains/losses: " + str(paired[tier]["gained"]["count"]) + "/" + str(paired[tier]["lost"]["count"]), ""]
    lines += ["## Separate criteria", ""] + [v["statement"] + "." for v in aggregate["criteria"].values()]
    lines += ["", "Temporal and insufficient-classification values with no judged denominator remain not measurable.",
              "Known false-current exposure is a lower bound, not a complete error rate.", ""]
    return "\n".join(lines)


def _run_once(context, dependencies):
    """Orchestration seam for synthetic tests; the public entrypoint supplies checked context."""
    deps, output, lock = dependencies, context["output"], context["lock"]
    writer, clock = deps.writer, deps.clock
    state = ExecutionState(context, writer, clock)
    state.start()  # Never catch/reclassify an already-existing state's failure.
    scored = 0
    pending_case = None
    traces, timings = {}, {}
    try:
        deps.activate(context)
        t = clock.tick(); model = deps.model_loader(context["model_snapshot"])
        load_ms = (clock.tick()-t)*1000
        views, view_stats = deps.prepare_views(context, model)
        frozen = deps.frozen_traces(context)
        keys = [view + "|" + section for view in sorted(VIEW_RECORDS) for section in SECTIONS]
        keys.sort()
        if set(frozen["traces"]) != set(keys) or set(views) != set(VIEW_RECORDS):
            raise ValueError("Frozen request/view population mismatch")
        t = clock.tick()
        with deps.selector() as selector:
            worker_ms = (clock.tick()-t)*1000
            for key in keys:
                view, section = key.split("|")
                trace, sample = deps.request(views[view], section, frozen["traces"][key], selector)
                compare_candidates(trace["queries"], frozen["traces"][key]["queries"])
                traces[key] = trace
                timings[key] = {"first": sample, "warmup": None, "warm": []}
                check, sample = deps.request(views[view], section, frozen["traces"][key], selector)
                if check != trace: raise ValueError("Warm-up changed selection or trace")
                timings[key]["warmup"] = sample
            for _ in range(30):
                for key in keys:
                    view, section = key.split("|")
                    check, sample = deps.request(views[view], section, frozen["traces"][key], selector)
                    if check != traces[key]: raise ValueError("Warm repetition changed selection or trace")
                    timings[key]["warm"].append(sample)
        # The complete final selection is durable before any gold parse or score.
        writer.write(output / "selection_trace.json", {"traces": traces, "timings": timings})
        data, private_ids = deps.load_gold(context)
        cases = data["cases"]
        if len(cases) != 34 or len({c["case_id"] for c in cases}) != 34 or {tier: sum(c["benchmark_tier"] == tier for c in cases) for tier in ("production", "diagnostic")} != {"production": 18, "diagnostic": 16}:
            raise ValueError("Frozen case population mismatch")
        passages = {p["passage_id"]: p for p in data["passages"]}
        baseline_by_id = {r["case_id"]: r for r in frozen["case_results"]}
        if set(baseline_by_id) != {c["case_id"] for c in cases}: raise ValueError("Baseline score population mismatch")
        results = []
        for case in cases:
            cid = case["case_id"]; key = case["context_id"] + "|" + case["section_id"]
            if frozen["case_keys"][cid] != key.split("|"): raise ValueError("Case/request mapping changed")
            result = deps.scorer(case, passages, traces[key])
            scored += 1  # Consumption begins at score production, even if persistence fails.
            pending_case = {"case": case, "trace": traces[key], "result": result}
            results.append(result)
            state.record(traces[key], result, baseline_result=baseline_by_id[cid], gold_case=case)
            pending_case = None
        if deps.activity["query_encode_calls"] != 24*32*2 or deps.activity["document_encode_calls"] != 4 or deps.activity["model_loads"] != 1:
            raise ValueError("Runtime activity count mismatch")
        expected = context["baseline_manifest"]
        comparable = all(deps.environment.get(k) == expected.get(k) for k in ("device", "logical_cpu_count", "torch_threads"))
        raw = {"experiment_version": EXPERIMENT_VERSION, "implementation_commit": lock["implementation_commit"],
            "lock_commit": context["lock_commit"], "lock_hash": context["lock_hash"], "data": data,
            "private_ids": sorted(private_ids), "traces": traces, "case_results": results,
            "baseline_results": frozen["case_results"], "baseline_traces": frozen["traces"],
            "timings": timings, "lock_criteria": {k: lock[k] for k in ("phase_1_original_benchmark_criteria", "phase_3_candidate_improvement_criteria")},
            "environment_comparable": comparable}
        writer.write(output / "raw_trace.json", raw)
        aggregate, paired = result_bundle(data, results, frozen["case_results"], traces, frozen["traces"], private_ids, timings, lock, comparable)
        public_dir = context["root"] / PUBLIC_DIRECTORY
        writer.write(public_dir / "candidate_aggregate_results.json", aggregate, public=True)
        writer.write(public_dir / "paired_comparison.json", paired, public=True)
        writer.write(public_dir / "phase_3b_report.md", _report(aggregate, paired), public=True, text=True)
        writer.write(output / "p96_case_results.json", [r for r in results if r["case_id"] in private_ids])
        writer.write(output / "p96_case_analysis.md", "# Private case-level audit\n\n" + "\n".join(
            f"- {r['case_id']}: {r['evidence_coverage_status']}; roles {r['roles_covered']}; excluded-risk passages {r['false_current_passages']}" for r in results if r["case_id"] in private_ids) + "\n", text=True)
        manifest = {"experiment_version": EXPERIMENT_VERSION, "run_id": lock["run_id"],
            "implementation_commit": lock["implementation_commit"], "lock_commit": context["lock_commit"],
            "lock_sha256": context["lock_hash"], "private_lock_sha256": context["private_lock_hash"],
            "candidate_evaluation_run": True, "scored_case_count": scored, "activity": deps.activity,
            "model_load_ms": load_ms, "worker_preparation_ms": worker_ms, "environment": deps.environment,
            "corpus_preparation": {"view_"+str(i+1): view_stats[v] for i,v in enumerate(sorted(view_stats))},
            "timing_method": "first + one warm-up + 30 warm per distinct view/section; query encoding, original selection, projected IPC selection and excerpts included; audit checks, offset mapping and scoring excluded",
            "outputs_sha256": {n: digest(public_dir/n) for n in PUBLIC_OUTPUTS[:3]}}
        writer.write(public_dir / "run_manifest.json", manifest, public=True)
        state.finish("execution_completed")
        writer.write(public_dir / "execution_status.json", {k: state.data[k] for k in (
            "status", "run_id", "experiment_version", "implementation_commit", "lock_commit", "started_at",
            "finished_at", "scored_case_count", "candidate_evaluation_run")}, public=True)
        private_manifest = {"lock_hash": context["lock_hash"], "implementation_commit": lock["implementation_commit"],
            "lock_commit": context["lock_commit"], "output_hashes": {
                p.relative_to(context["root"]).as_posix(): digest(p)
                for p in [*(public_dir/n for n in PUBLIC_OUTPUTS), output/"raw_trace.json", output/"selection_trace.json",
                          output/"p96_case_results.json", output/"p96_case_analysis.md", state.path,
                          *(output/"case_traces"/(c["case_id"]+".json") for c in cases)]}}
        writer.write(output / "private_run_manifest.json", private_manifest)
        return state.data
    except BaseException as error:
        import traceback
        failure = {"error_type": type(error).__name__, "message": str(error), "traceback": traceback.format_exc(),
                   "scored_case_count": scored, "persisted_case_count": state.data["scored_case_count"],
                   "pending_case": pending_case, "partial_selection_traces": traces,
                   "candidate_difference": getattr(error, "details", None), "failed_at": clock.utc()}
        try:
            writer.write(output / "failure_log.json", failure)
        finally:
            state.data["scored_case_count"] = max(scored, state.data["scored_case_count"])
            state.data["candidate_evaluation_run"] = scored > 0
            state.finish("execution_failed_after_partial_scoring" if scored else "execution_failed_before_scoring")
        raise


def execute_evaluation(*, root=None, lock_path=None, private_lock_path=None, experiment_version=None,
                       confirm=None, dependencies=None, git=None):
    if lock_path is None or private_lock_path is None or experiment_version != EXPERIMENT_VERSION or confirm != CONFIRM_EXECUTION:
        raise RuntimeError("Formal evaluation is disabled without explicit execute mode, formal lock, version and confirmation")
    root = Path(root or ROOT).resolve()
    if root == ROOT and (dependencies is not None or git is not None):
        raise ValueError("Synthetic dependency/Git injection is forbidden for the real repository")
    context = preflight(root, lock_path, private_lock_path, git=git)
    return _run_once(context, dependencies or DefaultDependencies())


def recompute(root, private_run, verification_path=None):
    """Trace-only independent calculation: no model, retriever or selector construction."""
    root, private_run = Path(root).resolve(), Path(private_run).resolve()
    parent = root / "private_data/temporal_state_retrieval_experiment/phase_3b"
    if private_run.parent != parent or not re.fullmatch(r"phase_3b_state_aware_v1_run_[0-9]{8}", private_run.name) or not GitView(root).ignored(private_run / "verification.json"):
        raise ValueError("Verification output must remain private and ignored")
    destination = Path(verification_path or private_run / "verification.json").resolve()
    if destination.parent != private_run or destination.name in {"raw_trace.json", "execution_state.json", "private_run_manifest.json"} or destination.exists():
        raise ValueError("Refusing verification overwrite or escaping destination")
    manifest = read_json(private_run / "private_run_manifest.json")
    state = read_json(private_run / "execution_state.json")
    if state["status"] not in {"execution_completed", "validation_failed"} or state["scored_case_count"] != 34:
        raise ValueError("Only a completed one-shot run can be independently verified")
    lock = read_json(root / LOCK_PATH)
    require_hash_contract(lock)
    if digest(root / LOCK_PATH) != manifest["lock_hash"]:
        raise ValueError("Saved lock hash mismatch")
    scoring_path = "experiments/temporal_state_retrieval/scoring.py"
    scoring_item = next(x for x in lock["public_artifacts"] if x["path"] == scoring_path)
    validate_tracked_artifact(root, scoring_item, lock["implementation_commit"])
    from .scoring import score_case
    mismatches = []
    for name, expected in manifest["output_hashes"].items():
        path = (root / name).resolve()
        if not (path.is_relative_to(private_run) or path.is_relative_to(root / PUBLIC_DIRECTORY)):
            raise ValueError("Invalid saved output path")
        if not path.is_file() or digest(path) != expected: mismatches.append(name)
    if mismatches:
        result = {"status": "validation_failed", "reason": "saved output hash mismatch", "mismatched_files": mismatches}
    else:
        raw = read_json(private_run / "raw_trace.json")
        passages = {p["passage_id"]: p for p in raw["data"]["passages"]}
        results = [score_case(c, passages, raw["traces"][c["context_id"]+"|"+c["section_id"]]) for c in raw["data"]["cases"]]
        aggregate, paired = result_bundle(raw["data"], results, raw["baseline_results"], raw["traces"], raw["baseline_traces"],
            set(raw["private_ids"]), raw["timings"], raw["lock_criteria"], raw["environment_comparable"])
        same = (results == raw["case_results"] and aggregate == read_json(root / PUBLIC_DIRECTORY / "candidate_aggregate_results.json")
                and paired == read_json(root / PUBLIC_DIRECTORY / "paired_comparison.json"))
        result = {"status": "verified" if same else "validation_failed", "case_count": len(results),
            "all_numerators_denominators_values_equal": same, "aggregate": aggregate, "paired_comparison": paired}
    writer = AtomicWriter()
    writer.write(destination, result)
    if result["status"] == "validation_failed":
        state = read_json(private_run / "execution_state.json")
        state.update(status="validation_failed", validation_failed_at=Clock().utc())
        writer.write(private_run / "execution_state.json", state, replace=True)
    return result


def _worker():
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
    if "--selector-stream" in sys.argv:
        print("READY", flush=True)
        for line in sys.stdin:
            payload = json.loads(line)
            validate_payload(payload)
            print(json.dumps(selector.select(payload)), flush=True)
    else:
        payload = json.loads(sys.stdin.read())
        validate_payload(payload)
        print(json.dumps(selector.select(payload)))


def main(argv=None):
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("preflight", "execute", "recompute"))
    parser.add_argument("--lock", type=Path)
    parser.add_argument("--private-lock", type=Path)
    parser.add_argument("--experiment-version")
    parser.add_argument("--confirm")
    parser.add_argument("--private-run", type=Path)
    args = parser.parse_args(argv)
    if args.mode == "recompute":
        if args.private_run is None: parser.error("--private-run is required")
        result = recompute(ROOT, args.private_run)
        print(json.dumps({"status": result["status"]}))
        return 0 if result["status"] == "verified" else 1
    if args.lock is None or args.private_lock is None: parser.error("--lock and --private-lock are required")
    if args.mode == "preflight":
        value = preflight(ROOT, args.lock, args.private_lock)
        print(json.dumps({"validated": True, "lock_commit": value["lock_commit"], "execution_started": False}))
        return 0
    value = execute_evaluation(lock_path=args.lock, private_lock_path=args.private_lock,
        experiment_version=args.experiment_version, confirm=args.confirm)
    print(json.dumps({k: value[k] for k in ("status", "run_id", "scored_case_count")}))
    return 0


if __name__ == "__main__":
    if "--selector-worker" in sys.argv or "--selector-stream" in sys.argv:
        _worker()
    else:
        raise SystemExit(main())
