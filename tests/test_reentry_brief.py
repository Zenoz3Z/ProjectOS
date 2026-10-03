import sys
from dataclasses import dataclass
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))


from reentry_brief import (  # noqa: E402
    SECTION_DEFINITIONS,
    apply_review_history,
    build_brief_section,
    build_reentry_brief,
    select_evidence,
)


EXPECTED_SECTION_IDS = [
    "current_intention",
    "changes_and_reasons",
    "current_vs_superseded",
    "relevant_feedback",
    "unresolved_tensions",
    "possible_next_action",
]


@dataclass(slots=True)
class FakeChunk:
    content: str
    source: str
    category: str
    chunk_id: str


@dataclass(slots=True)
class FakeSearchResult:
    rank: int
    score: float
    chunk: FakeChunk


class FakeRetriever:
    """Test retriever that avoids loading an embedding model."""

    def __init__(self, results):
        self.results = results

    def retrieve(self, query: str, top_k: int = 3):
        return self.results[:top_k]


def make_result(
    rank: int,
    score: float,
    category: str,
    chunk_id: str,
) -> FakeSearchResult:
    return FakeSearchResult(
        rank=rank,
        score=score,
        chunk=FakeChunk(
            content=f"Example evidence from {category}.",
            source=f"{category}/example.md",
            category=category,
            chunk_id=chunk_id,
        ),
    )


def make_standard_results():
    return [
        make_result(
            rank=1,
            score=0.90,
            category="current_state",
            chunk_id="current_state_chunk_001",
        ),
        make_result(
            rank=2,
            score=0.80,
            category="decisions",
            chunk_id="decisions_chunk_001",
        ),
        make_result(
            rank=3,
            score=0.70,
            category="feedback",
            chunk_id="feedback_chunk_001",
        ),
        make_result(
            rank=4,
            score=0.60,
            category="process",
            chunk_id="process_chunk_001",
        ),
    ]


def build_test_brief():
    results = make_standard_results()
    retriever = FakeRetriever(results)

    return build_reentry_brief(
        retriever=retriever,
        total_chunks=len(results),
    )


def test_six_sections_exist_in_required_order():
    section_ids = [
        definition.section_id
        for definition in SECTION_DEFINITIONS
    ]

    assert len(SECTION_DEFINITIONS) == 6
    assert section_ids == EXPECTED_SECTION_IDS


def test_select_evidence_uses_only_allowed_categories():
    results = [
        make_result(
            rank=1,
            score=0.90,
            category="research",
            chunk_id="research_chunk_001",
        ),
        make_result(
            rank=2,
            score=0.80,
            category="decisions",
            chunk_id="decisions_chunk_001",
        ),
        make_result(
            rank=3,
            score=0.70,
            category="current_state",
            chunk_id="current_state_chunk_001",
        ),
    ]

    selected = select_evidence(
        results=results,
        preferred_categories=("current_state", "decisions"),
        limit=2,
    )

    assert len(selected) == 2
    assert selected[0].chunk.category == "decisions"
    assert selected[1].chunk.category == "current_state"

    assert all(
        result.chunk.category != "research"
        for result in selected
    )


def test_section_contains_no_more_than_two_evidence_items():
    results = [
        make_result(
            rank=1,
            score=0.90,
            category="current_state",
            chunk_id="current_state_chunk_001",
        ),
        make_result(
            rank=2,
            score=0.80,
            category="decisions",
            chunk_id="decisions_chunk_001",
        ),
        make_result(
            rank=3,
            score=0.70,
            category="current_state",
            chunk_id="current_state_chunk_002",
        ),
    ]

    retriever = FakeRetriever(results)

    section = build_brief_section(
        definition=SECTION_DEFINITIONS[0],
        retriever=retriever,
        total_chunks=len(results),
    )

    assert len(section.evidence) == 2
    assert section.evidence_status == "supported"
    assert section.review_status == "unreviewed"


def test_evidence_contains_source_and_chunk_identifier():
    results = [
        make_result(
            rank=1,
            score=0.75,
            category="feedback",
            chunk_id="feedback_chunk_001",
        )
    ]

    retriever = FakeRetriever(results)

    section = build_brief_section(
        definition=SECTION_DEFINITIONS[3],
        retriever=retriever,
        total_chunks=len(results),
    )

    assert len(section.evidence) == 1

    evidence = section.evidence[0]

    assert evidence.source == "feedback/example.md"
    assert evidence.category == "feedback"
    assert evidence.chunk_id == "feedback_chunk_001"
    assert evidence.similarity_score == 0.75
    assert evidence.excerpt


def test_missing_evidence_is_marked_insufficient():
    results = [
        make_result(
            rank=1,
            score=0.95,
            category="research",
            chunk_id="research_chunk_001",
        )
    ]

    retriever = FakeRetriever(results)

    section = build_brief_section(
        definition=SECTION_DEFINITIONS[3],
        retriever=retriever,
        total_chunks=len(results),
    )

    assert section.evidence == []
    assert section.evidence_status == "insufficient"
    assert section.review_status == "unreviewed"


def test_complete_brief_preserves_section_order():
    sections = build_test_brief()

    section_ids = [
        section.section_id
        for section in sections
    ]

    assert len(sections) == 6
    assert section_ids == EXPECTED_SECTION_IDS

    for section in sections:
        assert section.review_status == "unreviewed"
        assert len(section.evidence) <= 2


def test_saved_correction_is_applied_to_correct_section():
    sections = build_test_brief()

    stored_data = {
        "schema_version": 1,
        "project_id": "sample_echo_field",
        "review_events": [
            {
                "event_id": "review_correction_001",
                "project_id": "sample_echo_field",
                "timestamp": "2026-09-18T12:00:00+00:00",
                "section_id": "unresolved_tensions",
                "action": "correct",
                "user_correction": (
                    "Lighting instability remains unresolved."
                ),
                "reason": "The retrieved feedback was outdated.",
                "target_chunk_id": None,
            }
        ],
    }

    apply_review_history(
        sections=sections,
        stored_data=stored_data,
    )

    target_section = next(
        section
        for section in sections
        if section.section_id == "unresolved_tensions"
    )

    assert target_section.review_status == "corrected"
    assert (
        target_section.user_correction
        == "Lighting instability remains unresolved."
    )

    other_sections = [
        section
        for section in sections
        if section.section_id != "unresolved_tensions"
    ]

    assert all(
        section.review_status == "unreviewed"
        for section in other_sections
    )


def test_saved_confirmation_is_applied_without_correction():
    sections = build_test_brief()

    stored_data = {
        "schema_version": 1,
        "project_id": "sample_echo_field",
        "review_events": [
            {
                "event_id": "review_confirm_001",
                "project_id": "sample_echo_field",
                "timestamp": "2026-09-18T12:05:00+00:00",
                "section_id": "current_intention",
                "action": "confirm",
                "user_correction": None,
                "reason": "The project aim is accurate.",
                "target_chunk_id": None,
            }
        ],
    }

    apply_review_history(
        sections=sections,
        stored_data=stored_data,
    )

    target_section = next(
        section
        for section in sections
        if section.section_id == "current_intention"
    )

    assert target_section.review_status == "confirmed"
    assert target_section.user_correction is None


def test_superseded_event_marks_matching_evidence():
    sections = build_test_brief()

    stored_data = {
        "schema_version": 1,
        "project_id": "sample_echo_field",
        "review_events": [
            {
                "event_id": "review_superseded_001",
                "project_id": "sample_echo_field",
                "timestamp": "2026-09-18T12:10:00+00:00",
                "section_id": "current_vs_superseded",
                "action": "mark_superseded",
                "user_correction": None,
                "reason": "This direction is no longer current.",
                "target_chunk_id": "decisions_chunk_001",
            }
        ],
    }

    apply_review_history(
        sections=sections,
        stored_data=stored_data,
    )

    matching_evidence = [
        evidence
        for section in sections
        for evidence in section.evidence
        if evidence.chunk_id == "decisions_chunk_001"
    ]

    assert matching_evidence
    assert all(
        evidence.is_superseded
        for evidence in matching_evidence
    )