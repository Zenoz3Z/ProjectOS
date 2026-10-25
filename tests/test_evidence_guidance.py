"""Iteration 3 presentation checks using only isolated, synthetic study records."""

import json

import pytest
from streamlit.testing.v1 import AppTest

from participant_flow import (
    GENERIC_EVIDENCE_GUIDANCE,
    INSUFFICIENT_EXPLANATION,
    OPTIONAL_EVIDENCE_REMINDER,
    PARTICIPANT_ACTIONS,
    PARTICIPANT_ACTION_CLARIFICATION,
    PARTICIPANT_ACTION_DEFINITIONS,
    PARTICIPANT_ACTION_GUIDANCE,
    SECTION_EVIDENCE_GUIDANCE,
    SECTION_IDS,
    insufficient_evidence_guidance,
)
from project_context import assigned_context, tutorial_context
from review_store import create_review_event, save_review_event
from study_cache import prepare_project, read_prepared_project
from study_fixtures import create_workspace, prepare_offline
from study_project_manager import validate_project
from test_participant_ui import ui, click, response, start


EXPECTED_RECORD_TYPES = (
    ("current_intention", "recent project overview, current-goals note, or final project statement"),
    ("changes_and_reasons", "decision log or process record explaining what changed and why"),
    ("current_vs_superseded", "distinguishes the current direction from earlier or abandoned directions"),
    ("relevant_feedback", "tutor feedback, user feedback, critique notes"),
    ("unresolved_tensions", "current blockers, limitations, unresolved questions, or a final reflection"),
    ("possible_next_action", "current task list, next-step note, handover record"),
)


@pytest.mark.parametrize("section_id,record_types", EXPECTED_RECORD_TYPES)
def test_insufficient_guidance_is_section_specific_and_visible(section_id, record_types):
    assert set(SECTION_EVIDENCE_GUIDANCE) == set(SECTION_IDS)
    explanation, guidance = insufficient_evidence_guidance(section_id, "insufficient")
    assert "absent, outdated, or not retrieved" in explanation
    assert guidance.startswith("You may want to check")
    assert record_types in guidance
    # Deliberately disagree with the retrieval status: only summary support controls this UI.
    at = AppTest.from_string(f'''
from types import SimpleNamespace
import streamlit_app as app
section = SimpleNamespace(section_id={section_id!r}, user_correction=None, evidence_status="supported")
result = app.GroundedSummary(support_status="insufficient", summary="Provisional fixture.",
    state_type="unclear", source_numbers=[], note="Synthetic test.")
app.render_participant_summary(section, result)
''').run()
    assert not at.exception
    assert explanation in [m.value for m in at.markdown]
    assert guidance in [c.value for c in at.caption]


@pytest.mark.parametrize("status", ["supported", "conflicting", None, "unknown"])
def test_other_support_statuses_do_not_receive_absence_guidance(status):
    assert insufficient_evidence_guidance("current_intention", status) == ()


def test_unknown_section_has_safe_non_prescriptive_fallback():
    assert insufficient_evidence_guidance("future_section", "insufficient") == (
        INSUFFICIENT_EXPLANATION, GENERIC_EVIDENCE_GUIDANCE,
    )
    assert "may want to check" in GENERIC_EVIDENCE_GUIDANCE


@pytest.mark.parametrize("status", ["supported", "conflicting", None])
def test_summary_rendering_does_not_confuse_retrieval_absence_with_summary_support(status):
    at = AppTest.from_string(f'''
from types import SimpleNamespace
import streamlit_app as app
section = SimpleNamespace(section_id="current_intention", user_correction=None, evidence_status="insufficient")
status = {status!r}
result = None if status is None else app.GroundedSummary(support_status=status,
    summary="Existing prepared result.", state_type="current", source_numbers=[1], note="Synthetic test.")
app.render_participant_summary(section, result)
''').run()
    assert not at.exception
    assert INSUFFICIENT_EXPLANATION not in [m.value for m in at.markdown]
    assert not set(SECTION_EVIDENCE_GUIDANCE.values()).intersection(c.value for c in at.caption)
    if status is not None:
        assert "Existing prepared result." in [m.value for m in at.markdown]


def test_review_definitions_have_requested_order_and_distinct_meanings():
    assert list(PARTICIPANT_ACTIONS) == list(PARTICIPANT_ACTION_DEFINITIONS) == [
        "Confirm", "Update", "Reject", "Not applicable",
    ]
    assert PARTICIPANT_ACTION_DEFINITIONS == {
        "Confirm": "The reconstruction accurately represents the project.",
        "Update": "The reconstruction needs a corrected current interpretation.",
        "Reject": "The reconstruction is misleading or unsupported.",
        "Not applicable": "This section does not apply to the project’s current state.",
    }
    assert "left it unchecked" in PARTICIPANT_ACTION_CLARIFICATION
    assert "Not applicable is not a synonym for a system error" in PARTICIPANT_ACTION_CLARIFICATION
    assert "own judgement" in PARTICIPANT_ACTION_CLARIFICATION


@pytest.mark.parametrize("choice", ["Confirm", "Update", "Reject", "Not applicable"])
def test_optional_reminder_does_not_gate_any_response_to_insufficient_summary(ui, choice):
    at, root = ui
    start(at)
    for _ in range(3):
        click(at, "Next")
    assert INSUFFICIENT_EXPLANATION in [m.value for m in at.markdown]
    assert SECTION_EVIDENCE_GUIDANCE["relevant_feedback"] in [c.value for c in at.caption]
    assert OPTIONAL_EVIDENCE_REMINDER in [c.value for c in at.caption]
    assert OPTIONAL_EVIDENCE_REMINDER.endswith("This is optional.")
    evidence = next(e for e in at.expander if e.label == "Why did ProjectOS produce this summary?")
    assert not evidence.proto.expanded
    assert not at.checkbox
    response(at).set_value(choice).run()
    if choice == "Update":
        at.text_area[0].set_value("A synthetic current interpretation.").run()
    click(at, "Save and continue")
    events = json.loads(assigned_context("P00", root).review_file.read_text())["review_events"]
    assert len(events) == 1 and events[0]["action"] == PARTICIPANT_ACTIONS[choice]


def test_tutorial_and_form_share_definitions_and_optional_reminder(ui):
    at, root = ui
    at.radio(key="session_mode").set_value("Participant study").run()
    at.text_input(key="participant_code_input").set_value("P00").run()
    click(at, "Start participant session")
    click(at, "Start tutorial")
    assert PARTICIPANT_ACTION_GUIDANCE in [m.value for m in at.markdown]
    assert PARTICIPANT_ACTION_CLARIFICATION in [c.value for c in at.caption]
    assert OPTIONAL_EVIDENCE_REMINDER in [c.value for c in at.caption]
    assert at.radio(key="participant_ui_tutorial_action").options == list(PARTICIPANT_ACTIONS)
    at.radio(key="participant_ui_tutorial_action").set_value("Not applicable").run()
    click(at, "Finish tutorial")
    click(at, "Start my project review")
    assert PARTICIPANT_ACTION_GUIDANCE in [c.value for c in at.caption]
    assert PARTICIPANT_ACTION_CLARIFICATION in [c.value for c in at.caption]
    assert OPTIONAL_EVIDENCE_REMINDER in [c.value for c in at.caption]
    assert INSUFFICIENT_EXPLANATION not in [m.value for m in at.markdown]
    assert not tutorial_context(root).review_file.exists()
    assert not assigned_context("P00", root).review_file.exists()


@pytest.mark.parametrize("code", ["P01", "P02", "P03", "P04"])
def test_four_synthetic_project_contexts_preserve_cache_validation_and_append_only_reviews(ui, monkeypatch, code):
    # These codes label newly built temporary fixtures, never real participant files.
    _, parent = ui
    codes = ("P01", "P02", "P03", "P04")
    root = create_workspace(parent / "four_synthetic_projects", codes=codes)
    prepare_offline(tutorial_context(root))
    contexts = {c: assigned_context(c, root) for c in codes}
    for context in contexts.values():
        prepare_offline(context)
        save_review_event(create_review_event(context.project_id, "current_intention", "confirm"), context.review_file)
    review_before = {c: context.review_file.read_bytes() for c, context in contexts.items()}
    cache_before = {c: context.summary_cache_file.read_bytes() for c, context in contexts.items()}
    monkeypatch.setenv("PROJECTOS_STUDY_ROOT", str(root))
    monkeypatch.setenv("PROJECTOS_STUDY_PARTICIPANT", code)
    at = AppTest.from_string("import streamlit_app as app\napp.main()", default_timeout=20).run()
    start(at, code)
    click(at, "Previous")  # The saved first section is preserved; revisit it from section two.
    response(at).set_value("Update").run()
    at.text_area[0].set_value("Only this synthetic project changes.").run()
    next(t for t in at.text_input if t.label == "Optional note").set_value("Synthetic note.").run()
    assert next(b for b in at.button if b.label == "Next").disabled
    click(at, "Save and continue")
    for c, context in contexts.items():
        assert context.summary_cache_file.read_bytes() == cache_before[c]
        if c != code:
            assert context.review_file.read_bytes() == review_before[c]
    events = json.loads(contexts[code].review_file.read_text())["review_events"]
    assert events[0] == json.loads(review_before[code])["review_events"][0]
    assert len(events) == 2 and events[-1]["action"] == "correct"
    assert events[-1]["user_correction"] == "Only this synthetic project changes."
    assert events[-1]["reason"] == "Synthetic note."
    assert validate_project(contexts[code])["ready"]
    sections, _, _ = read_prepared_project(contexts[code])
    assert all(s.user_correction is None for s in sections)
    def forbidden(*args, **kwargs):
        pytest.fail("A valid cache must not retrieve or generate.")
    stats = prepare_project(contexts[code], generate=forbidden, build_sections=forbidden)
    assert stats["cache_hits"] == 6 and stats["cache_misses"] == stats["api_calls"] == 0
    assert not tutorial_context(root).review_file.exists()
