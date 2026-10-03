from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class BriefSectionDefinition:
    section_id: str
    title: str
    question: str
    preferred_categories: tuple[str, ...]


SECTION_DEFINITIONS = (
    BriefSectionDefinition(
        section_id="current_intention",
        title="Current intention",
        question=(
            "What is the current aim or intended direction "
            "of this project?"
        ),
        preferred_categories=("current_state", "decisions"),
    ),
    BriefSectionDefinition(
        section_id="changes_and_reasons",
        title="What changed and why",
        question=(
            "What important changes were made to the project, "
            "and why were they made?"
        ),
        preferred_categories=("decisions", "process"),
    ),
    BriefSectionDefinition(
        section_id="current_vs_superseded",
        title="Current versus superseded directions",
        question=(
            "Which project directions are current, and which "
            "directions have been replaced or superseded?"
        ),
        preferred_categories=(
            "current_state",
            "decisions",
            "process",
        ),
    ),
    BriefSectionDefinition(
        section_id="relevant_feedback",
        title="Relevant feedback",
        question=(
            "What tutor or user feedback is relevant to the "
            "current project direction?"
        ),
        preferred_categories=("feedback", "process"),
    ),
    BriefSectionDefinition(
        section_id="unresolved_tensions",
        title="Unresolved tensions",
        question=(
            "What unresolved questions, tensions or limitations "
            "remain in the project?"
        ),
        preferred_categories=(
            "current_state",
            "process",
            "feedback",
            "decisions",
        ),
    ),
    BriefSectionDefinition(
        section_id="possible_next_action",
        title="Possible next action",
        question=(
            "What is the next documented action or decision "
            "that should be addressed?"
        ),
        preferred_categories=(
            "current_state",
            "process",
            "feedback",
        ),
    ),
)


VALID_SECTION_IDS = {
    definition.section_id
    for definition in SECTION_DEFINITIONS
}