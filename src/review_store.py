import argparse
import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal
from uuid import uuid4

from brief_schema import VALID_SECTION_IDS


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_REVIEW_DIR = PROJECT_ROOT / "data" / "reviews"

ReviewAction = Literal[
    "confirm",
    "correct",
    "reject",
    "mark_superseded",
]

VALID_ACTIONS = {
    "confirm",
    "correct",
    "reject",
    "mark_superseded",
}


@dataclass(slots=True)
class ReviewEvent:
    event_id: str
    project_id: str
    timestamp: str
    section_id: str
    action: ReviewAction
    user_correction: str | None = None
    reason: str | None = None
    target_chunk_id: str | None = None


def normalise_optional_text(value: str | None) -> str | None:
    """Remove surrounding whitespace from optional text."""
    if value is None:
        return None

    cleaned_value = value.strip()

    if not cleaned_value:
        return None

    return cleaned_value


def create_review_event(
    project_id: str,
    section_id: str,
    action: ReviewAction,
    user_correction: str | None = None,
    reason: str | None = None,
    target_chunk_id: str | None = None,
    timestamp: str | None = None,
    event_id: str | None = None,
) -> ReviewEvent:
    """Validate input and create one review event."""
    project_id = project_id.strip()
    user_correction = normalise_optional_text(user_correction)
    reason = normalise_optional_text(reason)
    target_chunk_id = normalise_optional_text(target_chunk_id)

    if not project_id:
        raise ValueError("project_id must not be empty.")

    if section_id not in VALID_SECTION_IDS:
        valid_sections = ", ".join(sorted(VALID_SECTION_IDS))
        raise ValueError(
            f"Unknown section_id: {section_id}. "
            f"Valid sections are: {valid_sections}."
        )

    if action not in VALID_ACTIONS:
        valid_actions = ", ".join(sorted(VALID_ACTIONS))
        raise ValueError(
            f"Unknown review action: {action}. "
            f"Valid actions are: {valid_actions}."
        )

    if action == "correct" and user_correction is None:
        raise ValueError(
            "The correct action requires non-empty "
            "user_correction text."
        )

    if action == "mark_superseded" and target_chunk_id is None:
        raise ValueError(
            "The mark_superseded action requires a "
            "target_chunk_id."
        )

    if timestamp is None:
        timestamp = datetime.now(timezone.utc).isoformat()

    if event_id is None:
        event_id = f"review_{uuid4().hex}"

    return ReviewEvent(
        event_id=event_id,
        project_id=project_id,
        timestamp=timestamp,
        section_id=section_id,
        action=action,
        user_correction=user_correction,
        reason=reason,
        target_chunk_id=target_chunk_id,
    )


def create_empty_store(project_id: str) -> dict:
    """Create the initial JSON structure for one project."""
    return {
        "schema_version": 1,
        "project_id": project_id,
        "review_events": [],
    }


def load_review_store(
    file_path: Path,
    project_id: str,
) -> dict:
    """Load an existing review store or create an empty one."""
    if not file_path.exists():
        return create_empty_store(project_id)

    try:
        stored_data = json.loads(
            file_path.read_text(encoding="utf-8")
        )
    except json.JSONDecodeError as error:
        raise ValueError(
            f"The review file contains invalid JSON: {file_path}"
        ) from error

    if not isinstance(stored_data, dict):
        raise ValueError(
            "The review store must contain a JSON object."
        )

    if stored_data.get("schema_version") != 1:
        raise ValueError(
            "Unsupported or missing review schema version."
        )

    stored_project_id = stored_data.get("project_id")

    if stored_project_id != project_id:
        raise ValueError(
            "The review file belongs to project "
            f"'{stored_project_id}', not '{project_id}'."
        )

    review_events = stored_data.get("review_events")

    if not isinstance(review_events, list):
        raise ValueError(
            "The review_events field must contain a list."
        )

    return stored_data


def save_review_event(
    event: ReviewEvent,
    file_path: Path,
) -> dict:
    """
    Append one event and save the complete review history.

    The file is first written to a temporary path and then
    replaced to reduce the chance of a partially written file.
    """
    stored_data = load_review_store(
        file_path=file_path,
        project_id=event.project_id,
    )

    stored_data["review_events"].append(asdict(event))

    file_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    temporary_path = file_path.with_suffix(
        file_path.suffix + ".tmp"
    )

    temporary_path.write_text(
        json.dumps(
            stored_data,
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    temporary_path.replace(file_path)

    return stored_data


def get_latest_section_status(
    stored_data: dict,
    section_id: str,
) -> str:
    """Derive the latest section-level review status."""
    action_to_status = {
        "confirm": "confirmed",
        "correct": "corrected",
        "reject": "rejected",
    }

    for event in reversed(stored_data["review_events"]):
        if event.get("section_id") != section_id:
            continue

        action = event.get("action")

        if action in action_to_status:
            return action_to_status[action]

    return "unreviewed"


def get_latest_section_correction(
    stored_data: dict,
    section_id: str,
) -> str | None:
    """
    Return the correction attached to the latest section review.

    If the latest section-level action is confirm or reject,
    no active correction is returned.
    """
    section_actions = {
        "confirm",
        "correct",
        "reject",
    }

    for event in reversed(stored_data["review_events"]):
        if event.get("section_id") != section_id:
            continue

        action = event.get("action")

        if action not in section_actions:
            continue

        if action == "correct":
            return event.get("user_correction")

        return None

    return None


def get_superseded_chunk_ids(stored_data: dict) -> set[str]:
    """Return every chunk marked as superseded."""
    return {
        event["target_chunk_id"]
        for event in stored_data["review_events"]
        if (
            event.get("action") == "mark_superseded"
            and event.get("target_chunk_id")
        )
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Save a review action for a ProjectOS "
            "Re-entry Brief."
        )
    )

    parser.add_argument(
        "action",
        choices=sorted(VALID_ACTIONS),
        help="Review action to save.",
    )

    parser.add_argument(
        "section_id",
        choices=sorted(VALID_SECTION_IDS),
        help="Re-entry Brief section to review.",
    )

    parser.add_argument(
        "--project-id",
        default="sample_echo_field",
        help="Project identifier.",
    )

    parser.add_argument(
        "--correction",
        help="User correction text for the correct action.",
    )

    parser.add_argument(
        "--reason",
        help="Optional reason for the review action.",
    )

    parser.add_argument(
        "--chunk-id",
        help=(
            "Evidence chunk identifier required by "
            "mark_superseded."
        ),
    )

    parser.add_argument(
        "--output",
        type=Path,
        help="Optional custom JSON output path.",
    )

    return parser


def main() -> None:
    parser = build_parser()
    arguments = parser.parse_args()

    output_path = arguments.output

    if output_path is None:
        output_path = (
            DEFAULT_REVIEW_DIR
            / f"{arguments.project_id}_reviews.json"
        )

    try:
        event = create_review_event(
            project_id=arguments.project_id,
            section_id=arguments.section_id,
            action=arguments.action,
            user_correction=arguments.correction,
            reason=arguments.reason,
            target_chunk_id=arguments.chunk_id,
        )

        stored_data = save_review_event(
            event=event,
            file_path=output_path,
        )
    except ValueError as error:
        parser.error(str(error))

    print()
    print("Review event saved")
    print("-" * 60)
    print(f"Event ID: {event.event_id}")
    print(f"Project: {event.project_id}")
    print(f"Section: {event.section_id}")
    print(f"Action: {event.action}")
    print(f"Timestamp: {event.timestamp}")
    print(f"Output: {output_path}")
    print(
        "Total stored events: "
        f"{len(stored_data['review_events'])}"
    )


if __name__ == "__main__":
    main()