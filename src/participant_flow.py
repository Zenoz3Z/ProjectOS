"""Presentation-only helpers for the participant review flow."""

from brief_schema import SECTION_DEFINITIONS


PARTICIPANT_ACTIONS = {
    "Confirm": "confirm",
    "Update": "correct",
    "Not applicable": "not_applicable",
    "Reject": "reject",
}

PARTICIPANT_ACTION_GUIDANCE = (
    "**Confirm** — This matches my current understanding.\n\n"
    "**Update** — This is partly useful but needs correction or additional information.\n\n"
    "**Not applicable** — There are no relevant records, or this section does not apply to my project.\n\n"
    "**Reject** — This reconstruction is misleading or incorrect."
)

EVIDENCE_GUIDANCE = (
    "Check the supporting records when a summary seems surprising, outdated or incomplete. "
    "You do not need to open every record."
)

# Presentation only: backend questions remain unchanged for retrieval and cache reuse.
PARTICIPANT_QUESTIONS = {
    "current_vs_superseded": (
        "What is the project doing now, and which earlier ideas or approaches are no longer current?"
    ),
    "possible_next_action": "What next step is documented in your project records?",
}

DOCUMENTED_NEXT_STEP_GUIDANCE = (
    "This section reports a next step found in your project records. It does not invent a recommendation. "
    "If no next step was documented, you can mark this section Not applicable or use Update "
    "to record what you would do next."
)

PARTICIPANT_TITLES = {
    "current_intention": "Current aim",
    "changes_and_reasons": "What changed and why",
    "current_vs_superseded": "Current direction and replaced ideas",
    "relevant_feedback": "Relevant feedback",
    "unresolved_tensions": "Open questions",
    "possible_next_action": "Documented next step",
}

SECTION_IDS = tuple(section.section_id for section in SECTION_DEFINITIONS)
REVIEWED_STATUSES = frozenset({"confirmed", "corrected", "not_applicable", "rejected"})


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
