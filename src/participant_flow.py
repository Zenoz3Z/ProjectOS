"""Presentation-only helpers for the participant review flow."""

from brief_schema import SECTION_DEFINITIONS


PARTICIPANT_ACTIONS = {
    "Looks accurate": "confirm",
    "I want to update it": "correct",
    "This is not supported": "reject",
}

PARTICIPANT_TITLES = {
    "current_intention": "Current aim",
    "changes_and_reasons": "What changed and why",
    "current_vs_superseded": "Current and earlier directions",
    "relevant_feedback": "Relevant feedback",
    "unresolved_tensions": "Open questions",
    "possible_next_action": "Possible next step",
}

SECTION_IDS = tuple(section.section_id for section in SECTION_DEFINITIONS)
REVIEWED_STATUSES = frozenset({"confirmed", "corrected", "rejected"})


def review_progress(sections) -> dict:
    """Count each defined section once, using its latest saved review."""
    statuses = {section.section_id: section.review_status for section in sections}
    counts = {
        status: sum(statuses.get(section_id) == status for section_id in SECTION_IDS)
        for status in REVIEWED_STATUSES
    }
    reviewed = sum(counts.values())
    return {
        **counts,
        "reviewed": reviewed,
        "total": len(SECTION_IDS),
        "complete": reviewed == len(SECTION_IDS),
    }


def next_unreviewed_index(sections, current_index: int = -1) -> int | None:
    """Find the next pending section in schema order, wrapping skipped sections."""
    statuses = {section.section_id: section.review_status for section in sections}
    for offset in range(1, len(SECTION_IDS) + 1):
        index = (current_index + offset) % len(SECTION_IDS)
        if statuses.get(SECTION_IDS[index]) not in REVIEWED_STATUSES:
            return index
    return None


def latest_review_values(stored_data: dict, section_id: str) -> tuple:
    """Return saved form values, ignoring evidence-only review events."""
    for event in reversed(stored_data["review_events"]):
        if (event.get("section_id") == section_id
                and event.get("action") in PARTICIPANT_ACTIONS.values()):
            return (
                event["action"],
                event.get("user_correction") or "",
                event.get("reason") or "",
            )
    return None, "", ""


def has_completed_reviews(stored_data: dict) -> bool:
    """Unlock revisiting only after every defined section has a saved response."""
    return all(latest_review_values(stored_data, section_id)[0] in PARTICIPANT_ACTIONS.values()
               for section_id in SECTION_IDS)
