import sys
from pathlib import Path

import pytest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))


from review_store import (  # noqa: E402
    create_review_event,
    get_latest_section_status,
    get_superseded_chunk_ids,
    load_review_store,
    save_review_event,
)


def test_valid_confirm_event_can_be_created():
    event = create_review_event(
        project_id="sample_echo_field",
        section_id="current_intention",
        action="confirm",
        timestamp="2026-09-17T12:00:00+00:00",
        event_id="review_test_confirm",
    )

    assert event.project_id == "sample_echo_field"
    assert event.section_id == "current_intention"
    assert event.action == "confirm"
    assert event.user_correction is None
    assert event.target_chunk_id is None


def test_correct_requires_non_empty_text():
    with pytest.raises(
        ValueError,
        match="requires non-empty user_correction",
    ):
        create_review_event(
            project_id="sample_echo_field",
            section_id="current_intention",
            action="correct",
            user_correction="   ",
        )


def test_mark_superseded_requires_chunk_id():
    with pytest.raises(
        ValueError,
        match="requires a target_chunk_id",
    ):
        create_review_event(
            project_id="sample_echo_field",
            section_id="current_vs_superseded",
            action="mark_superseded",
        )


def test_unknown_section_is_rejected():
    with pytest.raises(
        ValueError,
        match="Unknown section_id",
    ):
        create_review_event(
            project_id="sample_echo_field",
            section_id="imaginary_section",
            action="confirm",
        )


def test_save_appends_without_removing_previous_events(
    tmp_path,
):
    review_file = tmp_path / "reviews.json"

    first_event = create_review_event(
        project_id="sample_echo_field",
        section_id="current_intention",
        action="confirm",
        timestamp="2026-09-17T12:00:00+00:00",
        event_id="review_event_001",
    )

    second_event = create_review_event(
        project_id="sample_echo_field",
        section_id="unresolved_tensions",
        action="correct",
        user_correction=(
            "Lighting instability remains the main blocker."
        ),
        timestamp="2026-09-17T12:05:00+00:00",
        event_id="review_event_002",
    )

    save_review_event(
        event=first_event,
        file_path=review_file,
    )

    stored_data = save_review_event(
        event=second_event,
        file_path=review_file,
    )

    reloaded_data = load_review_store(
        file_path=review_file,
        project_id="sample_echo_field",
    )

    assert review_file.exists()
    assert len(stored_data["review_events"]) == 2
    assert len(reloaded_data["review_events"]) == 2

    assert (
        reloaded_data["review_events"][0]["event_id"]
        == "review_event_001"
    )

    assert (
        reloaded_data["review_events"][1]["event_id"]
        == "review_event_002"
    )

    assert (
        reloaded_data["review_events"][1][
            "user_correction"
        ]
        == "Lighting instability remains the main blocker."
    )


def test_latest_section_status_ignores_evidence_actions():
    stored_data = {
        "schema_version": 1,
        "project_id": "sample_echo_field",
        "review_events": [
            {
                "section_id": "current_intention",
                "action": "confirm",
            },
            {
                "section_id": "current_intention",
                "action": "mark_superseded",
                "target_chunk_id": "old_chunk_001",
            },
            {
                "section_id": "current_intention",
                "action": "correct",
                "user_correction": (
                    "The current intention has changed."
                ),
            },
        ],
    }

    status = get_latest_section_status(
        stored_data=stored_data,
        section_id="current_intention",
    )

    assert status == "corrected"


def test_superseded_chunk_ids_are_reconstructed():
    stored_data = {
        "schema_version": 1,
        "project_id": "sample_echo_field",
        "review_events": [
            {
                "section_id": "current_vs_superseded",
                "action": "mark_superseded",
                "target_chunk_id": "old_chunk_001",
            },
            {
                "section_id": "current_vs_superseded",
                "action": "mark_superseded",
                "target_chunk_id": "old_chunk_002",
            },
            {
                "section_id": "current_intention",
                "action": "confirm",
                "target_chunk_id": None,
            },
        ],
    }

    superseded_ids = get_superseded_chunk_ids(
        stored_data
    )

    assert superseded_ids == {
        "old_chunk_001",
        "old_chunk_002",
    }


def test_review_file_cannot_be_loaded_for_wrong_project(
    tmp_path,
):
    review_file = tmp_path / "reviews.json"

    event = create_review_event(
        project_id="sample_echo_field",
        section_id="current_intention",
        action="confirm",
    )

    save_review_event(
        event=event,
        file_path=review_file,
    )

    with pytest.raises(
        ValueError,
        match="belongs to project",
    ):
        load_review_store(
            file_path=review_file,
            project_id="different_project",
        )