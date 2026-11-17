"""Isolated, cache-only tutorial sessions. No production functions are replaced."""

import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import stat
import sys
import threading
import uuid


SESSION_PATTERN = re.compile(r"demo_[0-9a-f]{32}\Z")
SOURCE_FILES = (
    "data/demo_projects/sample_echo_field/current_state/goals.md",
    "data/demo_projects/sample_echo_field/decisions/design_notes.md",
    "data/demo_projects/sample_echo_field/feedback/tutor_feedback.md",
    "data/demo_projects/sample_echo_field/process/project_log.md",
)
CACHE_ASSET = "demo/assets/tutorial_summaries.json"
SESSION_CACHE = "data/summary_cache/tutorial/sample_echo_field_summaries.json"


class DemoError(ValueError):
    """The frozen tutorial cannot be used safely; generation is not available."""


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def contained(root, relative):
    root = Path(root).resolve()
    candidate = root / relative
    if Path(relative).is_absolute() or ".." in Path(relative).parts:
        raise DemoError("Only paths inside the demo workspace are allowed.")
    walk = root
    for part in Path(relative).parts:
        walk = walk / part
        if walk.exists() or walk.is_symlink():
            info = walk.lstat()
            if stat.S_ISLNK(info.st_mode) or getattr(info, "st_file_attributes", 0) & stat.FILE_ATTRIBUTE_REPARSE_POINT:
                raise DemoError("Linked demo paths are not allowed.")
    if not candidate.resolve().is_relative_to(root):
        raise DemoError("Demo path escapes its workspace.")
    return candidate


def verify_assets(package):
    package = Path(package).resolve()
    try:
        manifest = json.loads(contained(package, "demo/assets/manifest.json").read_text(encoding="utf-8"))
        if (manifest["schema_version"] != 1 or manifest["project_id"] != "sample_echo_field"
                or set(manifest["source_files"]) != set(SOURCE_FILES)
                or manifest["cache_file"] != CACHE_ASSET):
            raise DemoError("Unexpected tutorial asset manifest.")
        for relative, expected in {**manifest["source_files"], CACHE_ASSET: manifest["cache_sha256"]}.items():
            if sha256(contained(package, relative)) != expected:
                raise DemoError("A public tutorial asset is missing or changed. Restore the supplied files; no summary will be generated.")
        return manifest
    except (OSError, KeyError, TypeError, json.JSONDecodeError) as error:
        raise DemoError("Public tutorial assets are missing or invalid. Restore the supplied files; no summary will be generated.") from error


def session_directory(package, session_id):
    if not SESSION_PATTERN.fullmatch(session_id):
        raise DemoError("Use a session identifier printed by this launcher.")
    return contained(package, f".projectos_demo/sessions/{session_id}")


def create_session(package):
    package = Path(package).resolve()
    manifest = verify_assets(package)
    session_id = "demo_" + uuid.uuid4().hex
    workspace = session_directory(package, session_id)
    workspace.mkdir(parents=True, exist_ok=False)
    for relative in SOURCE_FILES:
        destination = workspace / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(contained(package, relative), destination)
    destination = workspace / SESSION_CACHE
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(contained(package, CACHE_ASSET), destination)
    (workspace / "demo_session.json").write_text(json.dumps({
        "session_id": session_id, "project_id": "sample_echo_field", "model": manifest["model"],
        "synthetic_demo": True, "participant_research_data": False,
    }, indent=2), encoding="utf-8")
    verify_session(package, session_id)
    return session_id, workspace


def verify_session(package, session_id):
    manifest = verify_assets(package)
    workspace = session_directory(package, session_id)
    try:
        record = json.loads(contained(workspace, "demo_session.json").read_text(encoding="utf-8"))
        if record != {"session_id": session_id, "project_id": "sample_echo_field", "model": manifest["model"],
                      "synthetic_demo": True, "participant_research_data": False}:
            raise DemoError("This is not a recognised tutorial session.")
        for relative, expected in manifest["source_files"].items():
            if sha256(contained(workspace, relative)) != expected:
                raise DemoError("The session's tutorial source copy has changed.")
        if sha256(contained(workspace, SESSION_CACHE)) != manifest["cache_sha256"]:
            raise DemoError("The session's prepared cache has changed. Automatic regeneration is disabled.")
    except (OSError, ValueError, TypeError) as error:
        raise DemoError("Tutorial session missing or incompatible. No generation or replacement is attempted.") from error
    return workspace, manifest


def load_prepared(package, session_id):
    workspace, manifest = verify_session(package, session_id)
    # Imports use the existing validation; source/prompt/pipeline fingerprints are not bypassed.
    from project_context import tutorial_context
    from study_cache import read_prepared_project
    context = tutorial_context(workspace)
    sections, results, identity = read_prepared_project(context, manifest["model"])
    return context, sections, results, identity


def install_guards(package, workspace):
    """Process-only fail-closed limits, installed before importing the review UI."""
    package, workspace = Path(package).resolve(), Path(workspace).resolve()
    sys.dont_write_bytecode = True
    for key in list(os.environ):
        if key.startswith("OPENAI_") or key.startswith("PROJECTOS_"):
            os.environ.pop(key)
    os.environ.update(HF_HUB_OFFLINE="1", TRANSFORMERS_OFFLINE="1", HF_HUB_DISABLE_TELEMETRY="1",
                      STREAMLIT_BROWSER_GATHER_USAGE_STATS="false", PYTHONDONTWRITEBYTECODE="1")
    counts = {"blocked_external_network": 0, "blocked_inference": 0, "blocked_private_or_write_access": 0}

    def blocked(kind):
        counts[kind] += 1
        with (workspace / "blocked_activity.jsonl").open("a", encoding="utf-8") as stream:
            stream.write(json.dumps({"blocked": kind}) + "\n")

    def in_root(path, root):
        try:
            return Path(os.path.abspath(os.fsdecode(path))).is_relative_to(root)
        except (ValueError, TypeError, OSError):
            return False

    def audit(event, args):
        if event in {"socket.connect", "socket.getaddrinfo"}:
            address = args[1] if event == "socket.connect" else args[0]
            host = address[0] if isinstance(address, tuple) else address
            if host not in {"127.0.0.1", "localhost", "::1", None}:
                blocked("blocked_external_network")
                raise PermissionError("The tutorial allows loopback connections only.")
        if event == "open" and isinstance(args[0], (str, bytes, os.PathLike)):
            path = Path(os.path.abspath(os.fsdecode(args[0])))
            mode, flags = args[1:3]
            writing = (isinstance(mode, str) and any(c in mode for c in "wax+")) or (
                isinstance(flags, int) and flags & (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC | os.O_APPEND))
            if path.name in {".env", "secrets.toml"} or path.name.startswith(".env."):
                raise PermissionError("Credential files are not available to the tutorial.")
            if in_root(path, package) and not in_root(path, workspace):
                relative = path.relative_to(package).as_posix()
                private = relative.startswith(("private_data/", "data/study_projects/", "data/study_config/",
                                               "data/summary_cache/", "data/reviews/"))
                if writing or private:
                    blocked("blocked_private_or_write_access")
                    raise PermissionError("The tutorial cannot access research data or change package files.")
        if event in {"os.remove", "os.rename", "os.rmdir", "os.mkdir"}:
            for value in args[:2]:
                if isinstance(value, (str, bytes, os.PathLike)) and in_root(value, package) and not in_root(value, workspace):
                    blocked("blocked_private_or_write_access")
                    raise PermissionError("Only this isolated demo session may be changed.")

    experiment_prefix = str(package / "experiments").replace("\\", "/").lower() + "/"

    def profile(frame, event, arg):
        if event != "call":
            return
        filename = frame.f_code.co_filename.replace("\\", "/").lower()
        name = frame.f_code.co_name
        forbidden = (
            filename.endswith("/src/retrieval.py") and name in {"__init__", "retrieve"}
            or filename.endswith("/src/llm_summarizer.py") and name == "generate_grounded_summary"
            or filename.endswith("/src/study_cache.py") and name in {"prepare_project", "write_cache"}
            or filename.endswith("/src/reentry_brief.py") and name in {"build_reentry_brief", "retrieve_diverse_evidence"}
            or "/sentence_transformers/" in filename and name in {"encode", "encode_query", "encode_document"}
            or "/sentence_transformers/" in filename and name == "__init__" and type(frame.f_locals.get("self")).__name__ in {"SentenceTransformer", "CrossEncoder"}
            or filename.startswith(experiment_prefix)
        )
        if forbidden:
            blocked("blocked_inference")
            raise RuntimeError("Model loading, retrieval, generation and experiments are disabled in this demo.")

    sys.addaudithook(audit)
    sys.setprofile(profile)
    threading.setprofile(profile)
    return counts
