"""Exercise the real UI with offline summaries and isolated review files."""

import json

import httpx
import pytest
from streamlit.testing.v1 import AppTest

import streamlit_app as app
import llm_summarizer
from brief_schema import SECTION_DEFINITIONS
from test_reentry_brief import FakeRetriever, make_standard_results
from project_context import assigned_context, tutorial_context
from review_store import create_review_event, save_review_event
from study_fixtures import create_workspace, prepare_workspace, prepare_offline


@pytest.fixture
def ui(monkeypatch, tmp_path):
    results = make_standard_results()
    create_workspace(tmp_path, codes=("P00", "P01", "P02", "P96", "P97"))
    prepare_workspace(tmp_path)
    prepare_offline(assigned_context("P96", tmp_path))
    monkeypatch.setenv("PROJECTOS_STUDY_ROOT", str(tmp_path))
    monkeypatch.setenv("PROJECTOS_STUDY_PARTICIPANT", "P00")
    monkeypatch.delenv("PROJECTOS_STUDY_ONLY", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.setattr(app, "DEFAULT_REVIEW_FILE", tmp_path / "data/reviews/development.json")
    monkeypatch.setattr(app, "initialise_retrieval", lambda: (
        [object()], results, FakeRetriever(results),
    ))
    def forbidden_api(*args, **kwargs):
        raise AssertionError("Participant navigation must never generate summaries.")
    monkeypatch.setattr(app, "generate_cached_summary", forbidden_api)
    monkeypatch.setattr(app, "generate_all_summaries", forbidden_api)
    monkeypatch.setattr(llm_summarizer, "OpenAI", forbidden_api)
    monkeypatch.setattr(httpx.Client, "send", forbidden_api)
    monkeypatch.setattr(app.SemanticRetriever, "__init__", forbidden_api)
    at = AppTest.from_string("import streamlit_app as app\napp.main()", default_timeout=20).run()
    return at, tmp_path


def click(at, label):
    next(button for button in at.button if button.label == label).click().run()
    assert not at.exception
    return at


def start(at, code="P00"):
    at.radio(key="session_mode").set_value("Participant study").run()
    at.text_input(key="participant_code_input").set_value(code).run()
    click(at, "Start participant session")
    if at.title[0].value == "Review complete":
        return at
    assert at.title[0].value == "Review your project re-entry brief"
    click(at, "Start tutorial")
    at.radio(key="participant_ui_tutorial_action").set_value("Confirm").run()
    click(at, "Finish tutorial")
    click(at, "Start my project review")
    return at


def response(at):
    return next(widget for widget in at.radio if widget.label == "Choose your response")


def test_single_section_validation_draft_protection_and_auto_advance(ui):
    at, root = ui
    start(at)
    assert [title.value for title in at.title] == ["Current aim"]
    assert not at.text_area
    assert any(e.label == "Why did ProjectOS produce this summary?" for e in at.expander)
    click(at, "Save and continue")
    assert any("Choose one response" in w.value for w in at.warning)
    response(at).set_value("Update").run()
    assert at.text_area[0].label == "Your updated version"
    click(at, "Save and continue")
    assert any("Write your updated version" in w.value for w in at.warning)
    at.text_area[0].set_value("A participant correction.").run()
    assert next(b for b in at.button if b.label == "Next").disabled
    assert any("unsaved response" in w.value for w in at.warning)
    # Hiding and showing the conditional field must retain the draft.
    response(at).set_value("Confirm").run()
    assert not at.text_area
    response(at).set_value("Update").run()
    assert at.text_area[0].value == "A participant correction."
    click(at, "Save and continue")
    assert at.title[0].value == "What changed and why"
    events = json.loads(assigned_context("P00", root).review_file.read_text())["review_events"]
    assert events[-1]["action"] == "correct"
    assert events[-1]["user_correction"] == "A participant correction."
    click(at, "Previous")
    assert at.text_area[0].value == "A participant correction."
    assert next(b for b in at.button if b.label == "Save and continue").disabled
    click(at, "Next")
    assert at.title[0].value == "What changed and why"


def test_completion_reload_isolation_and_development_view(ui, monkeypatch):
    at, root = ui
    start(at)
    choices = ["Confirm", "Update", "Reject"] + ["Confirm"] * 3
    for number, choice in enumerate(choices):
        assert f"Section {number + 1} of 6" in [c.value for c in at.caption]
        response(at).set_value(choice).run()
        if choice == "Update":
            at.text_area[0].set_value("Updated direction.").run()
        click(at, "Save and continue")
    assert at.title[0].value == "Review complete"
    assert {m.label: m.value for m in at.metric} == {
        "Reviewed sections": "6", "Corrected sections": "1", "Rejected sections": "1", "Not applicable sections": "0",
    }
    path = assigned_context("P00", root).review_file
    before = path.read_bytes()
    assert [e["action"] for e in json.loads(before)["review_events"]] == [
        "confirm", "correct", "reject", "confirm", "confirm", "confirm",
    ]
    at.button(key="participant_ui_jump_completion_current_intention").click().run()
    click(at, "Next section")
    assert at.text_area[0].value == "Updated direction."
    click(at, "Back to completion summary")
    assert path.read_bytes() == before
    # A new browser session has no in-memory progress or summaries.
    reopened = AppTest.from_string("import streamlit_app as app\napp.main()", default_timeout=20).run()
    start(reopened)
    assert reopened.title[0].value == "Review complete"
    click(reopened, "End participant session")
    # A guessed code cannot change the server-bound participant.
    reopened.text_input(key="participant_code_input").set_value("P01").run()
    click(reopened, "Start participant session")
    assert any("not available" in e.value for e in reopened.error)
    assert path.read_bytes() == before
    # Simulate the researcher restarting/binding a separate study session.
    monkeypatch.setenv("PROJECTOS_STUDY_PARTICIPANT", "P01")
    start(reopened, "P01")
    assert reopened.title[0].value == "Current aim"
    assert response(reopened).value is None
    assert path.read_bytes() == before
    assert not assigned_context("P01", root).review_file.exists()
    reopened.radio(key="session_mode").set_value("Development").run()
    assert len([h for h in reopened.subheader if h.value[:1].isdigit()]) == 6
    assert any(t.label == "Show research details" for t in reopened.toggle)
    assert not reopened.exception


def test_insufficient_summary_is_reviewable_without_error_and_details_are_hidden(ui, monkeypatch):
    at, root = ui
    start(at)
    # Only current_state has files; the feedback section legitimately has none.
    for _ in range(3):
        click(at, "Next")
    assert not at.error
    assert "ProjectOS could not find enough clear evidence to summarise this section." in [m.value for m in at.markdown]
    assert not at.toggle
    assert not at.code
    response(at).set_value("Reject").run()
    click(at, "Save and continue")
    assert at.title[0].value == "Open questions"


def test_failed_save_keeps_input_and_hides_private_exception(ui, monkeypatch):
    at, root = ui
    start(at)
    response(at).set_value("Update").run()
    at.text_area[0].set_value("Keep this draft.").run()

    def fail(*args, **kwargs):
        raise OSError("private-path-for-test")

    monkeypatch.setattr(app, "save_section_review", fail)
    click(at, "Save and continue")
    assert at.text_area[0].value == "Keep this draft."
    assert any("could not be saved" in e.value for e in at.error)
    assert all("private-path-for-test" not in e.value for e in at.error)
    assert not at.exception
    assert not assigned_context("P00", root).review_file.exists()


def test_missing_cache_blocks_review_without_trying_api(ui):
    at, root = ui
    context = assigned_context("P00", root)
    context.summary_cache_file.write_text("{}", encoding="utf-8")
    at.radio(key="session_mode").set_value("Participant study").run()
    at.text_input(key="participant_code_input").set_value("P00").run()
    click(at, "Start participant session")
    click(at, "Start tutorial")
    at.radio(key="participant_ui_tutorial_action").set_value("Confirm").run()
    click(at, "Finish tutorial")
    assert not at.exception
    assert any(app.STUDY_NOT_READY == message.value for message in at.info)
    assert not any(b.label == "Start my project review" for b in at.button)
    assert not any(str(root) in m.value for m in at.markdown)
    prepare_offline(context)
    at.run()
    click(at, "Start my project review")
    assert at.title[0].value == "Current aim"
    assert not response(at).disabled
    assert not context.review_file.exists()


def test_tutorial_practice_never_writes_formal_reviews_or_changes_cache(ui):
    at, root = ui
    context = assigned_context("P00", root)
    before = context.summary_cache_file.read_bytes()
    at.radio(key="session_mode").set_value("Participant study").run()
    at.text_input(key="participant_code_input").set_value("P00").run()
    click(at, "Start participant session")
    click(at, "Start tutorial")
    at.radio(key="participant_ui_tutorial_action").set_value("Update").run()
    at.text_area[0].set_value("Practice wording only.").run()
    click(at, "Finish tutorial")
    assert not context.review_file.exists()
    assert not tutorial_context(root).review_file.exists()
    click(at, "Start my project review")
    assert response(at).value is None
    response(at).set_value("Update").run()
    at.text_area[0].set_value("A formal correction.").run()
    click(at, "Save and continue")
    assert context.summary_cache_file.read_bytes() == before
    assert len(json.loads(context.review_file.read_text())["review_events"]) == 1


def test_study_server_hides_development_and_rejects_other_codes(ui, monkeypatch):
    at, root = ui
    monkeypatch.setenv("PROJECTOS_STUDY_ONLY", "1")
    at.run()
    assert not any(widget.label == "Mode" for widget in at.radio)
    at.text_input(key="participant_code_input").set_value("P02").run()
    click(at, "Start participant session")
    assert any("not available" in e.value for e in at.error)
    assert not any("Assigned test project" in m.value for m in at.markdown)


def seed_completed_reviews(root, code="P00", count=6):
    """Persist realistic saved state; the UI must derive completion from the store."""
    context = assigned_context(code, root)
    for index, definition in enumerate(SECTION_DEFINITIONS[:count]):
        action = "correct" if index == 3 else "reject" if index == 5 else "confirm"
        save_review_event(create_review_event(
            context.project_id, definition.section_id, action,
            user_correction="Saved feedback correction." if action == "correct" else None,
            reason="Saved feedback note." if index == 3 else None,
        ), context.review_file)
    return context


@pytest.fixture
def completed_ui(ui, monkeypatch):
    at, root = ui
    context = seed_completed_reviews(root)
    calls = []

    def forbidden(*args, **kwargs):
        calls.append("generation, API or embedding construction")
        raise AssertionError("Completed navigation must only use prepared data.")

    for name in ("generate_cached_summary", "generate_all_summaries", "generate_grounded_summary"):
        monkeypatch.setattr(app, name, forbidden)
    # Keep the generator source intact: its fingerprint validates the prepared cache.
    # UI entry points, the SDK and HTTP transport still fail if called.
    monkeypatch.setattr(llm_summarizer, "OpenAI", forbidden)
    monkeypatch.setattr(httpx.Client, "send", forbidden)
    monkeypatch.setattr(app.SemanticRetriever, "__init__", forbidden)
    start(at)
    assert at.title[0].value == "Review complete"
    yield at, root, context
    assert calls == []


@pytest.mark.parametrize("saved_count", [0, 5])
def test_direct_navigation_is_locked_until_all_six_are_saved(ui, saved_count):
    at, root = ui
    seed_completed_reviews(root, count=saved_count)
    start(at)
    assert not any((b.key or "").startswith("participant_ui_jump_") for b in at.button)
    assert not any("Editing section" in c.value for c in at.caption)
    assert any(b.label == "Save and continue" for b in at.button)
    assert not tutorial_context(root).review_file.exists()


@pytest.mark.parametrize("number", [4, 6])
def test_completion_has_named_status_links_and_jumps_directly(completed_ui, number):
    at, root, context = completed_ui
    before_review, before_cache = context.review_file.read_bytes(), context.summary_cache_file.read_bytes()
    links = [b for b in at.button if (b.key or "").startswith("participant_ui_jump_completion_")]
    assert len(links) == 6
    for index, (link, definition) in enumerate(zip(links, SECTION_DEFINITIONS), 1):
        assert link.label.startswith(f"{index}. {app.PARTICIPANT_TITLES[definition.section_id]} — ")
    assert links[3].label.endswith("Updated / Corrected")
    assert links[5].label.endswith("Rejected")
    links[number - 1].click().run()
    assert not at.exception
    assert f"Editing section {number} of 6" in [c.value for c in at.caption]
    assert at.title[0].value == app.PARTICIPANT_TITLES[SECTION_DEFINITIONS[number - 1].section_id]
    assert at.session_state["participant_ui_flow"]["index"] == number - 1
    if number == 4:
        assert at.text_area[0].value == "Saved feedback correction."
        assert next(t.value for t in at.text_input if t.label == "Optional note") == "Saved feedback note."
    else:
        assert next(b for b in at.button if b.label == "Next section").disabled
    click(at, "Back to completion summary")
    at.button(key="participant_ui_jump_completion_current_intention").click().run()
    assert next(b for b in at.button if b.label == "Previous section").disabled
    assert context.review_file.read_bytes() == before_review
    assert context.summary_cache_file.read_bytes() == before_cache


def test_post_completion_save_stays_updates_statistics_and_survives_refresh(completed_ui):
    at, root, context = completed_ui
    before_cache = context.summary_cache_file.read_bytes()
    at.button(key="participant_ui_jump_completion_relevant_feedback").click().run()
    response(at).set_value("Reject").run()
    next(t for t in at.text_input if t.label == "Optional note").set_value("Revised feedback judgement.").run()
    click(at, "Save changes")
    assert "Editing section 4 of 6" in [c.value for c in at.caption]
    assert any("Section 4 saved" in s.value for s in at.success)
    assert "Reject" == response(at).value
    assert any("0 updated / corrected · 2 rejected" in c.value for c in at.caption)
    assert any(b.label == "Return to completion summary" for b in at.button)
    assert any(b.label == "Continue editing this section" for b in at.button)
    assert any(e.label == "Go to another section" for e in at.expander)
    click(at, "Continue editing this section")
    assert "Editing section 4 of 6" in [c.value for c in at.caption]
    click(at, "Back to completion summary")
    assert {m.label: m.value for m in at.metric} == {
        "Reviewed sections": "6", "Corrected sections": "0", "Rejected sections": "2", "Not applicable sections": "0",
    }
    assert at.button(key="participant_ui_jump_completion_relevant_feedback").label.endswith("Rejected")
    saved = json.loads(context.review_file.read_text())["review_events"]
    assert len(saved) == 7 and saved[-1]["action"] == "reject"
    assert saved[-1]["reason"] == "Revised feedback judgement."
    assert saved[3]["user_correction"] == "Saved feedback correction."
    reopened = AppTest.from_string("import streamlit_app as app\napp.main()", default_timeout=20).run()
    start(reopened)
    assert reopened.title[0].value == "Review complete"
    assert not any(b.label in {"Start tutorial", "Start my project review"} for b in reopened.button)
    reopened.button(key="participant_ui_jump_completion_relevant_feedback").click().run()
    assert response(reopened).value == "Reject"
    assert next(t.value for t in reopened.text_input if t.label == "Optional note") == "Revised feedback judgement."
    assert context.summary_cache_file.read_bytes() == before_cache
    assert len(json.loads(context.review_file.read_text())["review_events"]) == 7


@pytest.mark.parametrize("destination", ["summary", "previous", "next", "direct"])
@pytest.mark.parametrize("field", ["action", "correction", "note"])
def test_unsaved_edits_guard_every_completed_navigation_and_discard(completed_ui, destination, field):
    at, root, context = completed_ui
    before = context.review_file.read_bytes()
    at.button(key="participant_ui_jump_completion_relevant_feedback").click().run()
    if field == "action":
        response(at).set_value("Confirm").run()
    elif field == "correction":
        at.text_area[0].set_value("Unsaved correction.").run()
    else:
        next(t for t in at.text_input if t.label == "Optional note").set_value("Unsaved note.").run()
    if destination == "direct":
        at.button(key="participant_ui_jump_editing_possible_next_action").click().run()
    else:
        click(at, {"summary": "Back to completion summary", "previous": "Previous section", "next": "Next section"}[destination])
    assert "Editing section 4 of 6" in [c.value for c in at.caption]
    assert any("unsaved changes" in w.value for w in at.warning)
    assert any(b.label == "Stay and save" for b in at.button)
    if field == "action":
        assert response(at).value == "Confirm"
    elif field == "correction":
        assert at.text_area[0].value == "Unsaved correction."
    else:
        assert next(t.value for t in at.text_input if t.label == "Optional note") == "Unsaved note."
    assert context.review_file.read_bytes() == before
    click(at, "Discard changes and continue")
    if destination == "summary":
        assert at.title[0].value == "Review complete"
        at.button(key="participant_ui_jump_completion_relevant_feedback").click().run()
    else:
        target = {"previous": 3, "next": 5, "direct": 6}[destination]
        assert f"Editing section {target} of 6" in [c.value for c in at.caption]
        at.button(key="participant_ui_jump_editing_relevant_feedback").click().run()
    assert response(at).value == "Update"
    assert at.text_area[0].value == "Saved feedback correction."
    assert next(t.value for t in at.text_input if t.label == "Optional note") == "Saved feedback note."
    assert context.review_file.read_bytes() == before


def test_stay_and_save_preserves_editing_and_validates_correction(completed_ui):
    at, root, context = completed_ui
    at.button(key="participant_ui_jump_completion_relevant_feedback").click().run()
    at.text_area[0].set_value("").run()
    click(at, "Next section")
    click(at, "Stay and save")
    assert any("Write your updated version" in w.value for w in at.warning)
    assert len(json.loads(context.review_file.read_text())["review_events"]) == 6
    at.text_area[0].set_value("Saved revised feedback.").run()
    click(at, "Stay and save")
    assert "Editing section 4 of 6" in [c.value for c in at.caption]
    assert at.session_state["participant_ui_flow"]["pending_navigation"] is None
    assert len(json.loads(context.review_file.read_text())["review_events"]) == 7
    assert next(t.value for t in at.text_input if t.label == "Optional note") == "Saved feedback note."
    note = next(t for t in at.text_input if t.label == "Optional note")
    note.set_value("Temporary note.").run()
    click(at, "Next section")
    next(t for t in at.text_input if t.label == "Optional note").set_value("Saved feedback note.").run()
    click(at, "Stay and save")
    assert at.session_state["participant_ui_flow"]["pending_navigation"] is None
    assert len(json.loads(context.review_file.read_text())["review_events"]) == 7
    click(at, "Return to completion summary")
    assert at.title[0].value == "Review complete"


def test_completed_p96_isolated_from_other_projects_and_tutorial(ui, monkeypatch):
    at, root = ui
    p96 = seed_completed_reviews(root, "P96")
    other = seed_completed_reviews(root, "P01")
    other_bytes = other.review_file.read_bytes()
    tutorial_cache = tutorial_context(root).summary_cache_file.read_bytes()
    monkeypatch.setenv("PROJECTOS_STUDY_PARTICIPANT", "P96")
    start(at, "P96")
    at.button(key="participant_ui_jump_completion_current_vs_superseded").click().run()
    response(at).set_value("Update").run()
    at.text_area[0].set_value("P96 self-test revision.").run()
    click(at, "Save changes")
    assert len(json.loads(p96.review_file.read_text())["review_events"]) == 7
    assert other.review_file.read_bytes() == other_bytes
    assert tutorial_context(root).summary_cache_file.read_bytes() == tutorial_cache
    assert not tutorial_context(root).review_file.exists()
    click(at, "End participant session")
    at.text_input(key="participant_code_input").set_value("P01").run()
    click(at, "Start participant session")
    assert any("not available" in e.value for e in at.error)
    assert not any((b.key or "").startswith("participant_ui_jump_") for b in at.button)


def test_not_applicable_full_flow_refresh_isolation_and_cache_reuse(ui):
    from study_cache import read_prepared_project, prepare_project
    at, root = ui
    context = assigned_context("P00", root)
    other = seed_completed_reviews(root, "P01")
    other_before = other.review_file.read_bytes()
    cache_before = context.summary_cache_file.read_bytes()
    sections_before, _, identity_before = read_prepared_project(context)
    start(at)
    for index, definition in enumerate(SECTION_DEFINITIONS):
        assert response(at).options == ["Confirm", "Update", "Not applicable", "Reject"]
        assert app.EVIDENCE_GUIDANCE in [c.value for c in at.caption]
        if index == 2:
            assert at.title[0].value == "Current direction and replaced ideas"
            assert app.PARTICIPANT_QUESTIONS[definition.section_id] in [m.value for m in at.markdown]
        if index == 5:
            assert at.title[0].value == "Documented next step"
            assert app.DOCUMENTED_NEXT_STEP_GUIDANCE in [m.value for m in at.markdown]
        assert not any((b.key or "").startswith("participant_ui_jump_") for b in at.button)
        response(at).set_value("Not applicable").run()
        click(at, "Save and continue")
    assert at.title[0].value == "Review complete"
    assert {m.label: m.value for m in at.metric} == {
        "Reviewed sections": "6", "Corrected sections": "0", "Rejected sections": "0",
        "Not applicable sections": "6",
    }
    links = [b for b in at.button if (b.key or "").startswith("participant_ui_jump_completion_")]
    assert len(links) == 6 and all(b.label.endswith("Not applicable") for b in links)
    at.button(key="participant_ui_jump_completion_current_vs_superseded").click().run()
    assert response(at).value == "Not applicable"
    response(at).set_value("Update").run()
    at.text_area[0].set_value("My own synthetic interpretation.").run()
    click(at, "Next section")
    assert "Editing section 3 of 6" in [c.value for c in at.caption]
    assert any("unsaved changes" in w.value for w in at.warning)
    click(at, "Stay and save")
    assert "My own synthetic interpretation." in [m.value for m in at.markdown]
    response(at).set_value("Not applicable").run()
    click(at, "Save changes")
    assert "My own synthetic interpretation." not in [m.value for m in at.markdown]
    assert any("6 not applicable" in c.value for c in at.caption)
    # A fresh UI session restores only persisted values, without repeating tutorial.
    reopened = AppTest.from_string("import streamlit_app as app\napp.main()", default_timeout=20).run()
    start(reopened)
    assert reopened.title[0].value == "Review complete"
    reopened.button(key="participant_ui_jump_completion_current_vs_superseded").click().run()
    assert response(reopened).value == "Not applicable"
    events = json.loads(context.review_file.read_text())["review_events"]
    assert len(events) == 8
    assert events[-2]["user_correction"] == "My own synthetic interpretation."
    assert events[-1]["action"] == "not_applicable" and events[-1]["user_correction"] is None
    sections_after, _, identity_after = read_prepared_project(context)
    assert identity_after == identity_before
    assert sections_after == sections_before
    assert context.summary_cache_file.read_bytes() == cache_before
    assert other.review_file.read_bytes() == other_before
    assert not tutorial_context(root).review_file.exists()
    def forbidden(*args, **kwargs):
        pytest.fail("A valid cache must not rebuild evidence or generate summaries.")
    stats = prepare_project(context, generate=forbidden, build_sections=forbidden)
    assert stats["cache_hits"] == 6 and stats["cache_misses"] == 0 and stats["api_calls"] == 0
    assert context.summary_cache_file.read_bytes() == cache_before


@pytest.mark.parametrize("destination", ["Back to completion summary", "Previous section", "Next section", "direct"])
def test_not_applicable_unsaved_selection_blocks_completed_navigation(completed_ui, destination):
    at, root, context = completed_ui
    before = context.review_file.read_bytes()
    at.button(key="participant_ui_jump_completion_relevant_feedback").click().run()
    response(at).set_value("Not applicable").run()
    if destination == "direct":
        at.button(key="participant_ui_jump_editing_possible_next_action").click().run()
    else:
        click(at, destination)
    assert "Editing section 4 of 6" in [c.value for c in at.caption]
    assert response(at).value == "Not applicable"
    assert any("unsaved changes" in w.value for w in at.warning)
    click(at, "Discard changes and continue")
    assert context.review_file.read_bytes() == before
    assert at.title[0].value != "Relevant feedback"


def test_tutorial_explains_four_actions_and_absence_without_formal_review(ui):
    at, root = ui
    at.radio(key="session_mode").set_value("Participant study").run()
    at.text_input(key="participant_code_input").set_value("P00").run()
    click(at, "Start participant session")
    click(at, "Start tutorial")
    assert app.PARTICIPANT_ACTION_GUIDANCE in [m.value for m in at.markdown]
    assert app.EVIDENCE_GUIDANCE in [c.value for c in at.caption]
    assert any("summary is provisional" in c.value for c in at.caption)
    assert any("Missing evidence can be a valid result" in c.value and "does not rewrite" in c.value for c in at.caption)
    at.radio(key="participant_ui_tutorial_action").set_value("Not applicable").run()
    click(at, "Finish tutorial")
    click(at, "Start my project review")
    assert response(at).value is None
    assert not tutorial_context(root).review_file.exists()
    assert not assigned_context("P00", root).review_file.exists()
