"""Presentation-only helpers for the participant review flow."""

from brief_schema import SECTION_DEFINITIONS


PARTICIPANT_ACTIONS = {
    "Confirm": "confirm",
    "Update": "correct",
    "Reject": "reject",
    "Not applicable": "not_applicable",
}

PARTICIPANT_ACTION_DEFINITIONS = {
    "Confirm": "The reconstruction accurately represents the project.",
    "Update": "The reconstruction needs a corrected current interpretation.",
    "Reject": "The reconstruction is misleading or unsupported.",
    "Not applicable": "This section does not apply to the project’s current state.",
}

PARTICIPANT_ACTION_GUIDANCE = "\n\n".join(
    f"**{label}** — {definition}"
    for label, definition in PARTICIPANT_ACTION_DEFINITIONS.items()
)

PARTICIPANT_ACTION_CLARIFICATION = (
    "Confirm means you have assessed the reconstruction, not simply left it unchecked. "
    "Use Update when you can give a more accurate current interpretation. "
    "Reject covers incorrect, misleading or unsupported reconstructions; "
    "Not applicable is not a synonym for a system error. Choose according to your own judgement."
)

OPTIONAL_EVIDENCE_REMINDER = (
    "You may open the source evidence before deciding. This is optional."
)

INSUFFICIENT_EXPLANATION = (
    "ProjectOS could not establish this section from the evidence it selected. "
    "The information may be absent, outdated, or not retrieved."
)

SECTION_EVIDENCE_GUIDANCE = {
    "current_intention": (
        "You may want to check a recent project overview, current-goals note, or final project statement."
    ),
    "changes_and_reasons": (
        "You may want to check a decision log or process record explaining what changed and why."
    ),
    "current_vs_superseded": (
        "You may want to check a record that distinguishes the current direction from earlier or abandoned directions."
    ),
    "relevant_feedback": (
        "You may want to check tutor feedback, user feedback, critique notes, or a record stating that no external feedback exists."
    ),
    "unresolved_tensions": (
        "You may want to check current blockers, limitations, unresolved questions, or a final reflection."
    ),
    "possible_next_action": (
        "You may want to check a current task list, next-step note, handover record, or a statement that the project is complete."
    ),
}

GENERIC_EVIDENCE_GUIDANCE = (
    "You may want to check a recent project record relevant to this section."
)


def insufficient_evidence_guidance(section_id: str, support_status: str | None) -> tuple[str, ...]:
    """Presentation only: use the summary assessment, never infer a cause of absence."""
    if support_status != "insufficient":
        return ()
    return INSUFFICIENT_EXPLANATION, SECTION_EVIDENCE_GUIDANCE.get(section_id, GENERIC_EVIDENCE_GUIDANCE)


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
