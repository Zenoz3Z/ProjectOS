"""Validated local project assignments; participant codes are not file paths."""

import json
import os
import re
import stat
from dataclasses import dataclass
from pathlib import Path, PureWindowsPath
from typing import Literal


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
CODE_PATTERN = re.compile(r"P[0-9]{2,3}\Z", re.ASCII)
PROJECT_PATTERN = re.compile(r"[a-z][a-z0-9_]{0,63}\Z", re.ASCII)
CATEGORIES = ("current_state", "decisions", "feedback", "process")


class ProjectConfigurationError(ValueError):
    """A configuration is missing, ambiguous or outside its allowed location."""


def validate_participant_code(code: str) -> str:
    if not isinstance(code, str) or not CODE_PATTERN.fullmatch(code):
        raise ProjectConfigurationError("Use a participant code such as P01 or P97.")
    return code


def safe_path(root: Path, candidate: Path) -> Path:
    """Reject traversal, symlinks and Windows junctions, including output paths."""
    root = Path(root).resolve()
    candidate = Path(candidate)
    if not candidate.is_absolute():
        candidate = root / candidate
    if ".." in candidate.parts:
        raise ProjectConfigurationError("Parent-directory references are not allowed.")
    try:
        parts = candidate.relative_to(root).parts
        resolved = candidate.resolve()
        resolved.relative_to(root)
    except (ValueError, OSError, RuntimeError) as error:
        raise ProjectConfigurationError("A project path is outside its allowed root.") from error
    walk = root
    for part in parts:
        walk = walk / part
        try:
            info = walk.lstat()
        except FileNotFoundError:
            continue
        if stat.S_ISLNK(info.st_mode) or getattr(info, "st_file_attributes", 0) & stat.FILE_ATTRIBUTE_REPARSE_POINT:
            raise ProjectConfigurationError("Linked project or storage paths are not allowed.")
    return resolved


@dataclass(frozen=True)
class ProjectContext:
    project_id: str
    display_name: str
    data_directory: Path
    review_file: Path
    summary_cache_file: Path
    project_role: Literal["tutorial", "participant"]
    participant_code: str | None
    repository_root: Path

    def validate_paths(self) -> None:
        root = self.repository_root.resolve()
        if not PROJECT_PATTERN.fullmatch(self.project_id):
            raise ProjectConfigurationError("Invalid project ID.")
        if self.project_role == "participant":
            code = validate_participant_code(self.participant_code)
            data_root = safe_path(root, root / "data/study_projects")
            data = safe_path(data_root, self.data_directory)
            if data == data_root:
                raise ProjectConfigurationError("An assignment must name one project directory.")
            expected_review = root / "data/reviews/participants" / code / f"{self.project_id}_reviews.json"
            expected_cache = root / "data/summary_cache/participants" / code / f"{self.project_id}_summaries.json"
        elif self.project_role == "tutorial" and self.participant_code is None and self.project_id == "sample_echo_field":
            expected_data = root / "data/demo_projects/sample_echo_field"
            if safe_path(root, self.data_directory) != safe_path(root, expected_data):
                raise ProjectConfigurationError("Invalid tutorial directory.")
            expected_review = root / "data/reviews/sample_echo_field_reviews.json"
            expected_cache = root / "data/summary_cache/tutorial/sample_echo_field_summaries.json"
        else:
            raise ProjectConfigurationError("Invalid project role.")
        for actual, expected in ((self.review_file, expected_review), (self.summary_cache_file, expected_cache)):
            if safe_path(root, actual) != safe_path(root, expected):
                raise ProjectConfigurationError("Project storage does not match its assignment.")
            safe_path(root, actual.with_suffix(actual.suffix + ".tmp"))


def tutorial_context(root: Path = REPOSITORY_ROOT) -> ProjectContext:
    root = Path(root).resolve()
    context = ProjectContext(
        "sample_echo_field", "Echo Field", root / "data/demo_projects/sample_echo_field",
        root / "data/reviews/sample_echo_field_reviews.json",
        root / "data/summary_cache/tutorial/sample_echo_field_summaries.json",
        "tutorial", None, root,
    )
    context.validate_paths()
    return context


def load_assignments(root: Path = REPOSITORY_ROOT) -> dict[str, ProjectContext]:
    root = Path(root).resolve()
    path = safe_path(root, root / "data/study_config/participant_assignments.json")
    if not path.is_file():
        raise ProjectConfigurationError("No local participant assignments are configured.")

    def unique_keys(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ProjectConfigurationError("Assignment keys must be unique.")
            result[key] = value
        return result

    try:
        values = json.loads(path.read_text(encoding="utf-8-sig"), object_pairs_hook=unique_keys)
    except (OSError, json.JSONDecodeError) as error:
        raise ProjectConfigurationError("The local assignment file cannot be read.") from error
    if not isinstance(values, dict):
        raise ProjectConfigurationError("Assignments must be a JSON object.")
    contexts = {}
    for code, value in values.items():
        validate_participant_code(code)
        if not isinstance(value, dict) or set(value) != {"project_id", "display_name", "relative_path"}:
            raise ProjectConfigurationError("Each assignment needs project_id, display_name and relative_path.")
        project_id, name, relative = (value[k] for k in ("project_id", "display_name", "relative_path"))
        if not isinstance(project_id, str) or not PROJECT_PATTERN.fullmatch(project_id) or project_id == "sample_echo_field":
            raise ProjectConfigurationError("Use a unique, safe participant project ID.")
        if not isinstance(name, str) or not name.strip() or len(name) > 80 or any(ord(c) < 32 for c in name):
            raise ProjectConfigurationError("Use a short, non-sensitive display name.")
        if (not isinstance(relative, str) or PureWindowsPath(relative).drive
                or Path(relative).is_absolute() or "\\" in relative
                or not re.fullmatch(r"data/study_projects/[A-Za-z0-9_-]+(?:/[A-Za-z0-9_-]+)*", relative)):
            raise ProjectConfigurationError("Assignment paths must be relative directories under data/study_projects.")
        context = ProjectContext(
            project_id, name.strip(), safe_path(root, root / relative),
            root / "data/reviews/participants" / code / f"{project_id}_reviews.json",
            root / "data/summary_cache/participants" / code / f"{project_id}_summaries.json",
            "participant", code, root,
        )
        context.validate_paths()
        for other in contexts.values():
            if (project_id == other.project_id or context.data_directory == other.data_directory
                    or context.data_directory in other.data_directory.parents
                    or other.data_directory in context.data_directory.parents):
                raise ProjectConfigurationError("Participants must have distinct project IDs and non-overlapping directories.")
        contexts[code] = context
    return contexts


def assigned_context(code: str, root: Path = REPOSITORY_ROOT,
                     allowed_participant: str | None = None) -> ProjectContext:
    validate_participant_code(code)
    if allowed_participant is not None and code != validate_participant_code(allowed_participant):
        raise ProjectConfigurationError("This code is not available in this study session.")
    assignments = load_assignments(root)
    if code not in assignments:
        raise ProjectConfigurationError("No project has been assigned to this participant code.")
    return assignments[code]


def supported_project_files(context: ProjectContext) -> list[Path]:
    """Inspect the tree before the existing document loader is allowed to read it."""
    from document_loader import SUPPORTED_EXTENSIONS

    context.validate_paths()
    directory = context.data_directory
    if not directory.is_dir():
        raise ProjectConfigurationError("The assigned project directory is missing.")
    files = []
    for parent, folders, names in os.walk(directory, followlinks=False):
        for name in folders + names:
            safe_path(directory, Path(parent) / name)
        files.extend(Path(parent) / name for name in names if Path(name).suffix.lower() in SUPPORTED_EXTENSIONS)
    return sorted(files)
