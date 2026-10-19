from types import SimpleNamespace

from brief_schema import SECTION_DEFINITIONS
from participant_flow import (
    PARTICIPANT_ACTIONS,
    has_completed_reviews,
    latest_review_values,
    next_unreviewed_index,
    review_progress,
)


def test_not_applicable_counts_once_without_becoming_confirmed_or_rejected():
    sections = sections_with("confirmed", "corrected", "rejected", "not_applicable", "not_applicable", "confirmed")
    assert review_progress(sections + [sections[3]]) == {
        "confirmed": 2, "corrected": 1, "rejected": 1, "not_applicable": 2,
        "reviewed": 6, "total": 6, "complete": True,
    }
    assert next_unreviewed_index(sections) is None
    store = {"review_events": [
        {"section_id": s.section_id, "action": "not_applicable"} for s in sections
    ]}
    assert has_completed_reviews(store)
    assert latest_review_values(store, "relevant_feedback") == ("not_applicable", "", "")
    assert not has_completed_reviews({"review_events": store["review_events"][:-1]})


def sections_with(*statuses):
    return [
        SimpleNamespace(section_id=section.section_id, review_status=status)
        for section, status in zip(SECTION_DEFINITIONS, statuses)
    ]


def test_navigation_follows_schema_order_and_returns_to_skipped_sections():
    sections = sections_with("unreviewed", "confirmed", "unreviewed", "corrected", "rejected", "confirmed")
    assert next_unreviewed_index(list(reversed(sections))) == 0
    assert next_unreviewed_index(sections, 0) == 2
    assert next_unreviewed_index(sections, 5) == 0


def test_progress_counts_saved_sections_once_and_requires_all_six():
    sections = sections_with("confirmed", "corrected", "rejected", "unreviewed", "unreviewed", "confirmed")
    progress = review_progress(sections + [sections[0]])
    assert progress == {"confirmed": 2, "corrected": 1, "rejected": 1, "not_applicable": 0, "reviewed": 4, "total": 6, "complete": False}
    completed = sections_with("confirmed", "corrected", "rejected", "confirmed", "confirmed", "confirmed")
    assert review_progress(completed)["complete"]
    assert next_unreviewed_index(completed) is None
    assert not review_progress(completed[:5])["complete"]


def test_participant_choices_keep_existing_persistence_actions():
    assert PARTICIPANT_ACTIONS == {
        "Confirm": "confirm",
        "Update": "correct",
        "Not applicable": "not_applicable",
        "Reject": "reject",
    }


def test_reopened_form_uses_latest_section_review_not_evidence_event():
    store = {"review_events": [
        {"section_id": "current_intention", "action": "confirm"},
        {"section_id": "current_intention", "action": "correct", "user_correction": "Updated aim.", "reason": "The source changed."},
        {"section_id": "current_intention", "action": "mark_superseded"},
    ]}
    assert latest_review_values(store, "current_intention") == ("correct", "Updated aim.", "The source changed.")
    assert latest_review_values(store, "relevant_feedback") == (None, "", "")
