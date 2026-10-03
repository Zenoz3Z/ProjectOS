from types import SimpleNamespace

from llm_summarizer import (
    GroundedSummary,
    build_user_prompt,
    generate_grounded_summary,
    insufficient_result,
    validate_result,
)


def make_evidence(
    source: str = "current_state/goals.md",
    chunk_id: str = "current_state__goals_chunk_001",
    excerpt: str = "The current interaction uses body movement.",
):
    return SimpleNamespace(
        source=source,
        chunk_id=chunk_id,
        excerpt=excerpt,
        is_superseded=False,
    )


def make_section(
    section_id: str = "current_intention",
    evidence=None,
):
    if evidence is None:
        evidence = [make_evidence()]

    return SimpleNamespace(
        section_id=section_id,
        title="Test section",
        question="What is the current project direction?",
        evidence=evidence,
    )


def test_insufficient_result_uses_safe_fallback():
    result = insufficient_result(
        "The supplied records do not answer the question."
    )

    assert result.support_status == "insufficient"
    assert result.state_type == "unclear"
    assert result.source_numbers == []
    assert "More information is needed" in result.summary


def test_validate_result_removes_invalid_source_numbers():
    result = GroundedSummary(
        support_status="supported",
        summary="  A grounded summary.  ",
        state_type="current",
        source_numbers=[2, 99, 1, 2],
        note="The records support the summary.",
    )

    validated = validate_result(
        result=result,
        evidence_count=2,
        section_id="current_intention",
    )

    assert validated.support_status == "supported"
    assert validated.source_numbers == [1, 2]
    assert validated.summary == "A grounded summary."


def test_validate_result_rejects_missing_valid_sources():
    result = GroundedSummary(
        support_status="supported",
        summary="An unsupported summary.",
        state_type="current",
        source_numbers=[8, 9],
        note="No valid source was cited.",
    )

    validated = validate_result(
        result=result,
        evidence_count=2,
        section_id="current_intention",
    )

    assert validated.support_status == "insufficient"
    assert validated.state_type == "unclear"
    assert validated.source_numbers == []


def test_current_vs_superseded_is_normalised_to_mixed():
    result = GroundedSummary(
        support_status="supported",
        summary=(
            "Whole-body movement is current. "
            "Hand gestures are superseded."
        ),
        state_type="current",
        source_numbers=[1, 2],
        note="Both project states are documented.",
    )

    validated = validate_result(
        result=result,
        evidence_count=2,
        section_id="current_vs_superseded",
    )

    assert validated.support_status == "supported"
    assert validated.state_type == "mixed"
    assert validated.source_numbers == [1, 2]


def test_user_prompt_contains_section_and_evidence():
    section = make_section(
        section_id="current_vs_superseded",
        evidence=[
            make_evidence(
                excerpt=(
                    "Whole-body movement is current. "
                    "Hand gestures are superseded."
                )
            )
        ],
    )

    prompt = build_user_prompt(section)

    assert "current_vs_superseded" in prompt
    assert "state_type must be mixed" in prompt
    assert '<evidence number="1">' in prompt
    assert "Whole-body movement is current" in prompt
    assert "</evidence>" in prompt


def test_no_evidence_returns_insufficient_without_api_call():
    section = make_section(
        section_id="unresolved_tensions",
        evidence=[],
    )

    result = generate_grounded_summary(section)

    assert result.support_status == "insufficient"
    assert result.state_type == "unclear"
    assert result.source_numbers == []
    assert "No evidence records" in result.note