import html
import json
import os
import re
from pathlib import Path
from types import SimpleNamespace

import streamlit as st

from chunking import create_chunks
from document_loader import DEFAULT_DATA_DIR, load_documents
from llm_summarizer import (
    DEFAULT_MODEL,
    GroundedSummary,
    generate_grounded_summary,
)
from reentry_brief import (
    DEFAULT_REVIEW_FILE,
    PROJECT_ID,
    apply_review_history,
    build_reentry_brief,
)
from retrieval import SemanticRetriever
from project_context import (
    CODE_PATTERN, REPOSITORY_ROOT, ProjectConfigurationError, assigned_context,
    tutorial_context, validate_participant_code,
)
from study_cache import CacheNotReady, read_prepared_project
from study_project_manager import validate_project
from participant_flow import (
    DOCUMENTED_NEXT_STEP_GUIDANCE,
    EVIDENCE_GUIDANCE,
    PARTICIPANT_ACTIONS,
    PARTICIPANT_ACTION_GUIDANCE,
    PARTICIPANT_QUESTIONS,
    PARTICIPANT_TITLES,
    REVIEWED_STATUSES,
    has_completed_reviews,
    latest_review_values,
    next_unreviewed_index,
    review_progress,
)
from review_store import (
    create_review_event,
    load_review_store,
    save_review_event,
)


st.set_page_config(
    page_title="ProjectOS",
    page_icon="📂",
    layout="wide",
)


USER_FACING_TITLES = {
    "current_intention": "What this project is trying to achieve",
    "changes_and_reasons": "What changed and why",
    "current_vs_superseded": "Current and previous directions",
    "relevant_feedback": "Feedback to remember",
    "unresolved_tensions": "Questions and problems still open",
    "possible_next_action": "A possible next step",
}


USER_FACING_QUESTIONS = {
    "current_intention": (
        "Does this still describe what you are trying to achieve?"
    ),
    "changes_and_reasons": (
        "Does this accurately describe the important changes?"
    ),
    "current_vs_superseded": (
        "Does this clearly separate the current direction "
        "from older ideas?"
    ),
    "relevant_feedback": (
        "Is this feedback still relevant to the project?"
    ),
    "unresolved_tensions": (
        "Are these still the main unresolved questions or problems?"
    ),
    "possible_next_action": (
        "Does this seem like an appropriate next step?"
    ),
}


REVIEW_ACTIONS = {
    "Yes, this is correct": "confirm",
    "Update this summary": "correct",
    "This is not accurate": "reject",
}


PARTICIPANT_CODE_PATTERN = CODE_PATTERN


def apply_interface_style() -> None:
    """Apply styling to improve readability."""
    st.markdown(
        """
        <style>
        .block-container {
            max-width: 1100px;
            padding-top: 2rem;
            padding-bottom: 4rem;
        }

        [data-testid="stSidebar"] {
            background-color: #f5f7fa;
        }

        [data-testid="stExpander"] {
            border-radius: 10px;
        }

        .projectos-intro {
            font-size: 1.05rem;
            line-height: 1.65;
            max-width: 850px;
            color: #3f4650;
            margin-bottom: 1rem;
        }

        .projectos-summary-label {
            color: #5f6875;
            font-size: 0.9rem;
            font-weight: 600;
            margin-bottom: 0.3rem;
        }

        .projectos-summary {
            font-size: 1.05rem;
            line-height: 1.7;
            padding: 1rem 1.1rem;
            border-left: 4px solid #4f7cac;
            background: #f7f9fc;
            border-radius: 0 10px 10px 0;
            margin-bottom: 0.75rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


@st.cache_resource(show_spinner=False)
def initialise_retrieval():
    """Load documents, chunks and the embedding model once."""
    documents = load_documents(DEFAULT_DATA_DIR)
    chunks = create_chunks(documents)

    if not documents:
        raise ValueError(
            "No supported project documents were found."
        )

    if not chunks:
        raise ValueError(
            "Documents were loaded, but no chunks were created."
        )

    retriever = SemanticRetriever(chunks)
    return documents, chunks, retriever


@st.cache_data(show_spinner=False)
def generate_cached_summary(
    section_payload: str,
    model: str,
) -> dict:
    """Generate and cache one summary for one evidence payload."""
    payload = json.loads(section_payload)

    evidence = [
        SimpleNamespace(**item)
        for item in payload["evidence"]
    ]

    section = SimpleNamespace(
        section_id=payload["section_id"],
        title=payload["title"],
        question=payload["question"],
        evidence=evidence,
    )

    result = generate_grounded_summary(
        section=section,
        model=model,
    )

    return result.model_dump()


def empty_review_store(project_id: str = PROJECT_ID) -> dict:
    """Return a valid empty review store for a new session."""
    return {
        "schema_version": 1,
        "project_id": project_id,
        "review_events": [],
    }


def load_session_review_store(
    review_file: Path,
    project_id: str = PROJECT_ID,
) -> dict:
    """Load one session's reviews without creating a file."""
    if not review_file.exists():
        return empty_review_store(project_id)

    return load_review_store(
        file_path=review_file,
        project_id=project_id,
    )


def participant_review_file(
    participant_code: str,
) -> Path:
    """Return the isolated review path for one participant."""
    validate_participant_code(participant_code)
    return (
        DEFAULT_REVIEW_FILE.parent
        / "participants"
        / participant_code
        / DEFAULT_REVIEW_FILE.name
    )


def clear_interface_state() -> None:
    """Clear temporary UI state when the session changes."""
    direct_keys = {
        "summary_results",
        "summary_errors",
        "summary_message",
        "review_message",
    }

    widget_prefixes = (
        "action_",
        "correction_",
        "reason_",
        "participant_ui_",
    )

    for key in list(st.session_state.keys()):
        if (
            key in direct_keys
            or key.startswith(widget_prefixes)
        ):
            st.session_state.pop(key, None)


def render_session_setup():
    """Select development or participant-study mode."""
    st.sidebar.header("Session setup")

    if os.getenv("PROJECTOS_STUDY_ONLY") == "1":
        session_mode = "Participant study"
        st.session_state["session_mode"] = session_mode
    else:
        session_mode = st.sidebar.radio(
            "Mode",
            options=("Development", "Participant study"),
            help=(
                "Development uses your existing review history. "
                "Participant study stores each participant separately."
            ),
            key="session_mode",
            on_change=clear_interface_state,
        )

    if session_mode == "Development":
        return {
            "mode": "development",
            "participant_code": None,
            "session_key": "development",
            "review_file": DEFAULT_REVIEW_FILE,
        }

    st.sidebar.caption(
        "Use the anonymous code from the consent form, "
        "for example P01."
    )

    participant_input = st.sidebar.text_input(
        "Participant code",
        placeholder="P01",
        max_chars=4,
        key="participant_code_input",
    )

    start_clicked = st.sidebar.button(
        "Start participant session",
        type="secondary" if st.session_state.get("active_participant_code") else "primary",
        width="stretch",
    )

    if start_clicked:
        if not PARTICIPANT_CODE_PATTERN.fullmatch(
            participant_input
        ):
            st.sidebar.error(
                "Enter a code such as P01, P02 or P100."
            )
        elif not os.getenv("PROJECTOS_STUDY_PARTICIPANT"):
            st.sidebar.error("This study session has not been set up. Please ask the researcher for assistance.")
        elif participant_input != os.getenv("PROJECTOS_STUDY_PARTICIPANT"):
            st.sidebar.error("This code is not available in this study session. Please ask the researcher for assistance.")
        else:
            clear_interface_state()

            st.session_state[
                "active_participant_code"
            ] = participant_input

            st.rerun()

    active_code = st.session_state.get(
        "active_participant_code"
    )

    if active_code:
        if active_code != os.getenv("PROJECTOS_STUDY_PARTICIPANT"):
            clear_interface_state()
            st.session_state.pop("active_participant_code", None)
            st.sidebar.error("Please reopen the study session with your assigned code.")
            return None

        st.sidebar.success(
            f"Active participant: {active_code}"
        )

        end_clicked = st.sidebar.button(
            "End participant session",
            width="stretch",
        )

        if end_clicked:
            clear_interface_state()

            st.session_state.pop(
                "active_participant_code",
                None,
            )

            st.rerun()

        return {
            "mode": "participant",
            "participant_code": active_code,
            "session_key": active_code.lower(),
        }

    st.sidebar.warning(
        "Enter a participant code and start the session."
    )

    return None


def build_current_brief(
    retriever: SemanticRetriever,
    total_chunks: int,
    review_file: Path,
):
    """Build the brief and apply the active reviews."""
    sections = build_reentry_brief(
        retriever=retriever,
        total_chunks=total_chunks,
    )

    stored_data = load_session_review_store(
        review_file
    )

    apply_review_history(
        sections=sections,
        stored_data=stored_data,
    )

    return sections, stored_data


def build_section_payload(section) -> str:
    """Create a stable JSON payload for summary caching."""
    payload = {
        "section_id": section.section_id,
        "title": section.title,
        "question": section.question,
        "evidence": [
            {
                "source": item.source,
                "chunk_id": item.chunk_id,
                "excerpt": (
                    "[Evidence state: superseded]\n"
                    f"{item.excerpt}"
                    if item.is_superseded
                    else item.excerpt
                ),
                "is_superseded": item.is_superseded,
            }
            for item in section.evidence
        ],
    }

    return json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
    )


def generate_all_summaries(
    sections,
    force_refresh: bool = False,
) -> None:
    """Generate all summaries and retain them across reruns."""
    if force_refresh:
        generate_cached_summary.clear()

    summary_results = {}
    summary_errors = {}

    progress = st.progress(
        0.0,
        text="Preparing your project re-entry summary...",
    )

    for position, section in enumerate(
        sections,
        start=1,
    ):
        payload = build_section_payload(section)

        progress.progress(
            (position - 1) / len(sections),
            text=(
                f"Summarising {position} of "
                f"{len(sections)}: "
                f"{friendly_section_title(section)}"
            ),
        )

        try:
            result_data = generate_cached_summary(
                section_payload=payload,
                model=DEFAULT_MODEL,
            )
        except Exception as error:
            summary_errors[
                section.section_id
            ] = (
                f"{type(error).__name__}: {error}"
            )
            continue

        summary_results[section.section_id] = {
            "payload": payload,
            "result": result_data,
        }

    progress.progress(
        1.0,
        text="Your re-entry summary is ready.",
    )

    progress.empty()

    st.session_state[
        "summary_results"
    ] = summary_results

    st.session_state[
        "summary_errors"
    ] = summary_errors


def get_summary_result(
    section,
) -> GroundedSummary | None:
    """Return a summary if its evidence still matches."""
    stored_results = st.session_state.get(
        "summary_results",
        {},
    )

    stored_entry = stored_results.get(
        section.section_id
    )

    if not stored_entry:
        return None

    current_payload = build_section_payload(
        section
    )

    if (
        stored_entry.get("payload")
        != current_payload
    ):
        return None

    try:
        return GroundedSummary.model_validate(
            stored_entry["result"]
        )
    except Exception:
        return None


def get_summary_error(
    section,
) -> str | None:
    """Return a saved generation error."""
    errors = st.session_state.get(
        "summary_errors",
        {},
    )

    return errors.get(section.section_id)


def save_section_review(
    section_id: str,
    action: str,
    correction: str,
    reason: str,
    review_file: Path,
    project_id: str = PROJECT_ID,
) -> None:
    """Save one section-level review event."""
    correction_to_save = None

    if action == "correct":
        correction_to_save = correction

    event = create_review_event(
        project_id=project_id,
        section_id=section_id,
        action=action,
        user_correction=correction_to_save,
        reason=reason,
    )

    review_file.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    save_review_event(
        event=event,
        file_path=review_file,
    )


def save_superseded_evidence(
    section_id: str,
    chunk_id: str,
    review_file: Path,
    project_id: str = PROJECT_ID,
) -> None:
    """Mark one record as belonging to an older direction."""
    event = create_review_event(
        project_id=project_id,
        section_id=section_id,
        action="mark_superseded",
        user_correction=None,
        reason=(
            "The user marked this supporting record as "
            "belonging to an older project direction."
        ),
        target_chunk_id=chunk_id,
    )

    review_file.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    save_review_event(
        event=event,
        file_path=review_file,
    )


def invalidate_section_summary(
    section_id: str,
) -> None:
    """Remove a summary whose evidence state changed."""
    summary_results = st.session_state.get(
        "summary_results",
        {},
    )

    summary_results.pop(
        section_id,
        None,
    )

    summary_errors = st.session_state.get(
        "summary_errors",
        {},
    )

    summary_errors.pop(
        section_id,
        None,
    )


def normalise_status(status) -> str:
    """Convert a status into a simple string value."""
    value = str(status).strip().lower()

    if "." in value:
        value = value.split(".")[-1]

    return value


def friendly_evidence_status(
    status,
) -> str:
    """Return user-facing evidence-status language."""
    status_value = normalise_status(status)

    labels = {
        "supported": (
            "Supporting records were found"
        ),
        "insufficient": (
            "More information may be needed"
        ),
        "conflicting": (
            "The records may describe "
            "different project stages"
        ),
    }

    return labels.get(
        status_value,
        "The available records need to be reviewed",
    )


def friendly_review_status(
    status,
) -> str:
    """Return user-facing review-status language."""
    status_value = normalise_status(status)

    labels = {
        "unreviewed": "Needs your review",
        "confirmed": "Confirmed by you",
        "corrected": "Updated by you",
        "not_applicable": "Not applicable",
        "rejected": "Marked as inaccurate",
    }

    return labels.get(
        status_value,
        status_value.replace(
            "_",
            " ",
        ).title(),
    )


def friendly_section_title(
    section,
) -> str:
    """Return the user-facing section title."""
    return USER_FACING_TITLES.get(
        section.section_id,
        section.title,
    )


def render_generated_summary(
    result: GroundedSummary,
    show_research_details: bool,
) -> None:
    """Display one structured LLM summary safely."""
    escaped_summary = html.escape(
        result.summary
    )

    if result.support_status == "supported":
        st.markdown(
            '<div class="projectos-summary-label">'
            "WHAT PROJECTOS FOUND"
            "</div>",
            unsafe_allow_html=True,
        )

        st.markdown(
            '<div class="projectos-summary">'
            f"{escaped_summary}"
            "</div>",
            unsafe_allow_html=True,
        )

    elif result.support_status == "conflicting":
        st.warning(
            "The available records may describe "
            "different project states. Review the "
            "evidence before continuing.\n\n"
            f"{result.summary}"
        )

    else:
        st.warning(result.summary)

    if show_research_details:
        source_numbers = ", ".join(
            str(number)
            for number in result.source_numbers
        )

        st.caption(
            "Generated summary details · "
            f"Support: {result.support_status} · "
            f"State: {result.state_type} · "
            f"Records used: "
            f"{source_numbers or 'none'}"
        )

        st.caption(
            f"Assessment: {result.note}"
        )


def render_summary(
    section,
    result: GroundedSummary | None,
    summary_error: str | None,
    show_research_details: bool,
) -> bool:
    """Display a user correction or generated summary."""
    review_status = normalise_status(
        section.review_status
    )

    summary_available = result is not None

    if section.user_correction:
        st.markdown(
            "#### Your current understanding"
        )

        st.success(
            section.user_correction
        )

        if result is not None:
            with st.expander(
                "View the earlier ProjectOS summary",
                expanded=False,
            ):
                render_generated_summary(
                    result=result,
                    show_research_details=(
                        show_research_details
                    ),
                )

    elif result is not None:
        render_generated_summary(
            result=result,
            show_research_details=(
                show_research_details
            ),
        )

    elif summary_error:
        st.error(
            "ProjectOS could not generate this "
            "section. The supporting records "
            "remain available below."
        )

        if show_research_details:
            st.caption(summary_error)

    else:
        st.info(
            "Generate the re-entry summary above "
            "to create a source-grounded "
            "interpretation of this section."
        )

    if review_status == "confirmed":
        st.success(
            "You previously confirmed this section."
        )

    if review_status == "rejected":
        st.warning(
            "You previously marked this summary "
            "as inaccurate. The supporting records "
            "remain available below."
        )

    if (
        result is not None
        or section.user_correction
    ):
        st.caption(
            "This is a provisional interpretation "
            "of your project records. Please check "
            "it before relying on it."
        )

    return (
        summary_available
        or bool(section.user_correction)
    )


def render_evidence(
    section,
    show_research_details: bool,
    review_file: Path,
    session_key: str,
) -> None:
    """Display supporting project records."""
    st.markdown(
        "#### Supporting project records"
    )

    st.caption(
        "Open these records if you want to "
        "check where the summary came from."
    )

    if not section.evidence:
        st.warning(
            "No relevant project records were "
            "found for this section."
        )
        return

    for item in section.evidence:
        expander_title = (
            f"Record {item.rank} · {item.source}"
        )

        with st.expander(
            expander_title,
            expanded=False,
        ):
            if item.is_superseded:
                st.info(
                    "You marked this record as "
                    "belonging to an older "
                    "project direction."
                )

            st.markdown(
                f"**Source:** `{item.source}`"
            )

            st.write(item.excerpt)

            if show_research_details:
                st.divider()

                st.caption(
                    "Research details · "
                    f"Category: {item.category} · "
                    f"Chunk: {item.chunk_id} · "
                    "Similarity: "
                    f"{item.similarity_score:.4f}"
                )

            if not item.is_superseded:
                superseded_clicked = st.button(
                    "This belongs to an older direction",
                    key=(
                        f"supersede_{session_key}_"
                        f"{section.section_id}_"
                        f"{item.chunk_id}"
                    ),
                )

                if superseded_clicked:
                    try:
                        save_superseded_evidence(
                            section_id=(
                                section.section_id
                            ),
                            chunk_id=item.chunk_id,
                            review_file=review_file,
                        )

                    except ValueError as error:
                        st.error(str(error))

                    else:
                        invalidate_section_summary(
                            section.section_id
                        )

                        st.session_state[
                            "review_message"
                        ] = (
                            "The supporting record was "
                            "marked as belonging to an "
                            "older direction. Regenerate "
                            "the summary to apply the change."
                        )

                        st.rerun()


def render_review_form(
    section,
    review_file: Path,
    session_key: str,
) -> None:
    """Display the review controls."""
    st.markdown(
        "#### Is this still accurate?"
    )

    review_question = USER_FACING_QUESTIONS.get(
        section.section_id,
        "Does this still reflect the current project?",
    )

    st.write(review_question)

    with st.form(
        key=(
            f"review_form_{session_key}_"
            f"{section.section_id}"
        ),
        clear_on_submit=False,
    ):
        selected_label = st.radio(
            "Choose one response",
            options=tuple(
                REVIEW_ACTIONS.keys()
            ),
            index=None,
            horizontal=True,
            key=(
                f"action_{session_key}_"
                f"{section.section_id}"
            ),
        )

        correction = st.text_area(
            (
                "Your updated version "
                "(only needed if you choose "
                "'Update this summary')"
            ),
            value=(
                section.user_correction
                or ""
            ),
            placeholder=(
                "Describe the current project "
                "state in your own words."
            ),
            help=(
                "Your update will be stored "
                "separately. The original "
                "supporting records will remain "
                "visible."
            ),
            key=(
                f"correction_{session_key}_"
                f"{section.section_id}"
            ),
        )

        reason = st.text_input(
            "Optional note",
            placeholder=(
                "Why did you accept, update or "
                "reject this summary?"
            ),
            key=(
                f"reason_{session_key}_"
                f"{section.section_id}"
            ),
        )

        submitted = st.form_submit_button(
            "Save my response",
            type="primary",
        )

    if not submitted:
        return

    if selected_label is None:
        st.warning(
            "Choose one response before saving."
        )
        return

    selected_action = REVIEW_ACTIONS[
        selected_label
    ]

    if (
        selected_action == "correct"
        and not correction.strip()
    ):
        st.warning(
            "Write your updated version "
            "before saving."
        )
        return

    try:
        save_section_review(
            section_id=section.section_id,
            action=selected_action,
            correction=correction,
            reason=reason,
            review_file=review_file,
        )

    except ValueError as error:
        st.error(str(error))
        return

    section_title = friendly_section_title(
        section
    )

    st.session_state["review_message"] = (
        f"Your response for "
        f"'{section_title}' was saved."
    )

    st.rerun()


def render_section(
    section,
    section_number: int,
    show_research_details: bool,
    review_file: Path,
    session_key: str,
) -> None:
    """Render one summary section."""
    section_title = friendly_section_title(
        section
    )

    summary_result = get_summary_result(
        section
    )

    summary_error = get_summary_error(
        section
    )

    with st.container(border=True):
        st.subheader(
            f"{section_number}. "
            f"{section_title}"
        )

        status_left, status_right = st.columns(
            2
        )

        status_left.caption(
            "Supporting records: "
            f"{friendly_evidence_status(section.evidence_status)}"
        )

        status_right.caption(
            "Your review: "
            f"{friendly_review_status(section.review_status)}"
        )

        reviewable = render_summary(
            section=section,
            result=summary_result,
            summary_error=summary_error,
            show_research_details=(
                show_research_details
            ),
        )

        render_evidence(
            section=section,
            show_research_details=(
                show_research_details
            ),
            review_file=review_file,
            session_key=session_key,
        )

        if reviewable:
            st.divider()

            render_review_form(
                section=section,
                review_file=review_file,
                session_key=session_key,
            )


def format_project_name(
    project_id: str,
) -> str:
    """Convert a project ID into a readable name."""
    return project_id.replace(
        "_",
        " ",
    ).title()


def count_current_summaries(
    sections,
) -> int:
    """Count current cached summaries."""
    return sum(
        1
        for section in sections
        if get_summary_result(section)
        is not None
    )


def render_project_sidebar(
    session_context: dict,
    documents,
    chunks,
    sections,
    stored_data: dict,
    current_summary_count: int,
    reviewed_sections: int,
) -> bool:
    """Render project information in the sidebar."""
    st.sidebar.divider()
    st.sidebar.header("Your project")

    st.sidebar.subheader(
        format_project_name(PROJECT_ID)
    )

    if (
        session_context["mode"]
        == "participant"
    ):
        st.sidebar.caption(
            "Study session · "
            f"{session_context['participant_code']}"
        )
    else:
        st.sidebar.caption(
            "Development session"
        )

    st.sidebar.metric(
        "Project records",
        len(documents),
    )

    st.sidebar.metric(
        "Generated summaries",
        (
            f"{current_summary_count} "
            f"/ {len(sections)}"
        ),
    )

    if sections:
        st.sidebar.progress(
            reviewed_sections
            / len(sections)
        )

    st.sidebar.caption(
        f"{reviewed_sections} "
        f"of {len(sections)} "
        "summary sections reviewed"
    )

    st.sidebar.divider()

    show_research_details = (
        st.sidebar.toggle(
            "Show research details",
            value=False,
            help=(
                "Displays technical retrieval "
                "and generation details used "
                "during prototype development."
            ),
            key=(
                "show_research_details_"
                f"{session_context['session_key']}"
            ),
        )
    )

    if show_research_details:
        st.sidebar.markdown(
            "#### Research details"
        )

        st.sidebar.metric(
            "Text chunks",
            len(chunks),
        )

        st.sidebar.metric(
            "Review events",
            len(
                stored_data[
                    "review_events"
                ]
            ),
        )

        st.sidebar.markdown(
            "**Summary model**"
        )

        st.sidebar.code(
            DEFAULT_MODEL,
            language=None,
        )

        st.sidebar.markdown(
            "**Project ID**"
        )

        st.sidebar.code(
            PROJECT_ID,
            language=None,
        )

        st.sidebar.markdown(
            "**Review history file**"
        )

        st.sidebar.code(
            str(
                session_context[
                    "review_file"
                ]
            ),
            language=None,
        )

    return show_research_details


def participant_flow_state() -> dict:
    """Keep navigation separate from persisted research data."""
    return st.session_state.setdefault(
        "participant_ui_flow",
        {"stage": "start", "index": 0, "prepare": False},
    )


def render_participant_start() -> None:
    st.title("Review your project re-entry brief")
    st.write(
        "First, practise with a short Echo Field example. Then review six parts "
        "of your own assigned project, which you previously worked on and paused. "
        "Check the source evidence when needed and tell us whether each summary is accurate."
    )
    with st.container(border=True):
        st.markdown(
            "1. **Read the summary**\n"
            "2. **Check the source evidence**\n"
            "3. **Confirm, update, mark not applicable or reject**"
        )
    st.markdown(
        "- There are six short sections.\n"
        "- The review normally takes around 10–15 minutes.\n"
        "- Your review is saved separately under your participant code."
    )
    st.caption(
        "Summaries are provisional. The researcher prepares them in advance by "
        "sending selected project excerpts to the OpenAI API. Your review does "
        "not trigger new summary requests. Tutorial responses do not count toward your study review."
    )
    if st.button("Start tutorial", type="primary", key="participant_ui_start"):
        participant_flow_state().update(stage="tutorial", prepare=False)
        st.rerun()


def render_participant_summary(section, result) -> bool:
    """Display a prepared summary; participant actions never generate content."""
    with st.container(border=True):
        st.markdown("#### What ProjectOS found")
        if result is not None:
            if result.support_status == "insufficient":
                st.write(
                    "ProjectOS could not find enough clear evidence to summarise this section."
                )
            else:
                st.write(result.summary)
                if result.support_status == "conflicting":
                    st.caption("The records may describe different project states. Check the evidence below.")
            st.caption("This summary is provisional. You can disagree with it.")
        elif section.user_correction:
            st.caption("The generated summary is not loaded in this session. Your saved update is below.")
        else:
            st.info("This summary is not available yet. You can still inspect the source evidence below.")
    if section.user_correction:
        st.markdown("**Your saved update**")
        st.write(section.user_correction)
    return result is not None or bool(section.user_correction)


def render_participant_evidence(section, session_context: dict) -> None:
    st.caption(EVIDENCE_GUIDANCE)
    with st.expander("Why did ProjectOS produce this summary?", expanded=False):
        st.caption("These excerpts come from the project files used to create the summary.")
        if not section.evidence:
            st.write("No relevant source evidence was found for this section.")
        for item in section.evidence:
            st.markdown(f"**{Path(item.source).name}**")
            st.write(item.excerpt)
            if item.is_superseded:
                st.caption("Marked as belonging to an older direction.")
            with st.expander(f"Source details · {Path(item.source).name}", expanded=False):
                st.caption(f"Category: {item.category} · Chunk ID: {item.chunk_id}")
                st.caption(f"Similarity score: {item.similarity_score:.4f}")
                st.caption("Similarity indicates textual relevance, not factual confidence.")
                if session_context.get("project_role") != "tutorial" and not item.is_superseded and st.button(
                    "This belongs to an older direction",
                    key=f"participant_ui_older_{section.section_id}_{item.chunk_id}",
                ):
                    try:
                        session_context["project_context"].validate_paths()
                        save_superseded_evidence(
                            section.section_id, item.chunk_id, session_context["review_file"],
                            project_id=session_context["project_context"].project_id,
                        )
                    except (ValueError, OSError):
                        st.error("The evidence review could not be saved. Please try again or ask the researcher.")
                    else:
                        st.session_state["review_message"] = (
                            "Evidence review saved. Your annotation is separate from the prepared summary."
                        )
                        st.rerun()


def reset_participant_draft(prefix: str, saved: tuple) -> None:
    """Reset widget values before the next render, only on explicit discard."""
    action, correction, reason = saved
    labels = {value: label for label, value in PARTICIPANT_ACTIONS.items()}
    st.session_state[f"{prefix}_action"] = labels.get(action)
    st.session_state[f"{prefix}_correction"] = correction
    st.session_state[f"{prefix}_reason"] = reason


def initialise_participant_draft(section, stored_data: dict, session_context: dict) -> tuple:
    saved = latest_review_values(stored_data, section.section_id)
    prefix = f"participant_ui_{session_context['session_key']}_{section.section_id}"
    labels = {value: label for label, value in PARTICIPANT_ACTIONS.items()}
    st.session_state.setdefault(f"{prefix}_action", labels.get(saved[0]))
    st.session_state.setdefault(f"{prefix}_correction", saved[1])
    st.session_state.setdefault(f"{prefix}_reason", saved[2])
    return prefix, saved


def participant_draft_values(prefix: str) -> tuple:
    """Read live widget values inside navigation callbacks, including unblurred edits."""
    action = PARTICIPANT_ACTIONS.get(st.session_state.get(f"{prefix}_action"))
    correction = st.session_state.get(f"{prefix}_correction", "") if action == "correct" else ""
    reason = st.session_state.get(f"{prefix}_reason", "")
    return action, correction.strip(), reason.strip()


def navigate_completed_review(target: dict, prefix: str | None = None, saved: tuple | None = None) -> None:
    """Queue a destination instead of losing an unsaved response."""
    flow = participant_flow_state()
    if prefix is not None and participant_draft_values(prefix) != saved:
        flow["pending_navigation"] = target
    else:
        flow.update(target, pending_navigation=None, edit_saved=False)


def discard_completed_draft(prefix: str, saved: tuple) -> None:
    """Reset widgets before rendering, then follow the explicitly requested destination."""
    flow = participant_flow_state()
    target = flow.get("pending_navigation")
    if target is not None:
        reset_participant_draft(prefix, saved)
        flow.update(target, pending_navigation=None, edit_saved=False)


def render_completed_section_links(sections, location: str,
                                   prefix: str | None = None, saved: tuple | None = None) -> None:
    if not review_progress(sections)["complete"]:
        return
    labels = {"confirmed": "Confirmed", "corrected": "Updated / Corrected",
              "not_applicable": "Not applicable", "rejected": "Rejected"}
    for index, section in enumerate(sections):
        st.button(
            f"{index + 1}. {PARTICIPANT_TITLES[section.section_id]} — {labels[section.review_status]}",
            key=f"participant_ui_jump_{location}_{section.section_id}", width="stretch",
            disabled=location == "editing" and index == participant_flow_state()["index"],
            on_click=navigate_completed_review,
            args=({"stage": "editing", "index": index}, prefix, saved),
        )


def render_completed_navigation(sections, prefix: str, saved: tuple) -> bool:
    flow = participant_flow_state()
    index = flow["index"]
    st.caption(f"Editing section {index + 1} of {len(sections)}")
    with st.container(horizontal=True):
        st.button("Back to completion summary", key="participant_ui_back_summary",
                  on_click=navigate_completed_review, args=({"stage": "complete"}, prefix, saved))
        st.button("Previous section", key="participant_ui_edit_previous", disabled=index == 0,
                  on_click=navigate_completed_review,
                  args=({"stage": "editing", "index": index - 1}, prefix, saved))
        st.button("Next section", key="participant_ui_edit_next", disabled=index == len(sections) - 1,
                  on_click=navigate_completed_review,
                  args=({"stage": "editing", "index": index + 1}, prefix, saved))
    if flow.get("pending_navigation") is not None:
        st.warning("You have unsaved changes. Stay and save, or discard them before leaving this section.")
        stay_and_save = st.button("Stay and save", key="participant_ui_stay_save", type="primary")
        st.button("Discard changes and continue", key="participant_ui_discard_continue",
                  on_click=discard_completed_draft, args=(prefix, saved))
        return stay_and_save
    return False


def render_participant_review(section, sections, stored_data: dict,
                              session_context: dict, reviewable: bool, save_requested: bool = False) -> None:
    flow = participant_flow_state()
    index = flow["index"]
    editing = flow["stage"] == "editing" and review_progress(sections)["complete"]
    prefix, saved = initialise_participant_draft(section, stored_data, session_context)

    st.markdown("#### How does this summary fit your project?")
    st.caption(PARTICIPANT_ACTION_GUIDANCE)
    selected = st.radio(
        "Choose your response", tuple(PARTICIPANT_ACTIONS), index=None,
        label_visibility="collapsed", key=f"{prefix}_action",
        persist_state="session", disabled=not reviewable,
    )
    action = PARTICIPANT_ACTIONS.get(selected)
    correction = ""
    if action == "correct":
        correction = st.text_area(
            "Your updated version", key=f"{prefix}_correction",
            persist_state="session", disabled=not reviewable,
            placeholder="Describe what this section should say.",
        )
    with st.expander("Add an optional note", expanded=False):
        reason = st.text_input(
            "Optional note", key=f"{prefix}_reason",
            persist_state="session", disabled=not reviewable,
        )
    values = (action, correction.strip(), reason.strip())
    dirty = values != saved
    st.session_state["participant_ui_dirty"] = dirty
    if dirty:
        st.warning("You have an unsaved response. Save it or discard your changes before moving to another section.")
    elif saved[0]:
        st.caption("Your response is saved. You can move on without submitting again.")
    if not reviewable:
        st.caption("Prepare the summary before reviewing it. Your existing saved response is retained.")

    with st.container(horizontal=True, vertical_alignment="center"):
        save = st.button(
            "Save changes" if editing else "Save and continue", type="primary", key="participant_ui_save",
            disabled=not reviewable or (bool(saved[0]) and not dirty),
        )
        previous = following = False
        if not editing:
            previous = st.button("Previous", key="participant_ui_previous", disabled=index == 0 or dirty)
            following = st.button("Next", key="participant_ui_next", disabled=index == len(sections) - 1 or dirty)
    if dirty:
        st.button(
            "Discard unsaved changes", key="participant_ui_discard",
            on_click=reset_participant_draft, args=(prefix, saved),
        )
    st.caption("Only saved responses survive a refresh or a change of participant session.")

    if save_requested and not dirty:
        # The user may have restored the saved values while the prompt was open.
        flow["pending_navigation"] = None
        st.rerun()
    if save or save_requested:
        if action is None:
            st.warning("Choose one response before saving.")
        elif action == "correct" and not correction.strip():
            st.warning("Write your updated version before saving.")
        else:
            try:
                session_context["project_context"].validate_paths()
                save_section_review(
                    section.section_id, action, correction, reason,
                    session_context["review_file"],
                    project_id=session_context["project_context"].project_id,
                )
            except (ValueError, OSError):
                st.error("Your response could not be saved. Your input is still here. Please try again or ask the researcher.")
            else:
                updated_store = load_session_review_store(
                    session_context["review_file"], session_context["project_context"].project_id,
                )
                apply_review_history(sections, updated_store)
                if editing:
                    flow.update(edit_saved=True, pending_navigation=None)
                else:
                    next_index = next_unreviewed_index(sections, index)
                    flow.update(
                        stage="complete" if next_index is None else "review",
                        index=next_index if next_index is not None else index,
                    )
                st.session_state["participant_ui_dirty"] = False
                st.session_state["review_message"] = f"Section {index + 1} saved."
                st.rerun()
    if not dirty and (previous or following):
        flow["index"] = index + (1 if following else -1)
        st.rerun()
    if editing:
        if flow.get("edit_saved") and not dirty:
            with st.container(horizontal=True):
                st.button("Return to completion summary", key="participant_ui_saved_return",
                          on_click=navigate_completed_review, args=({"stage": "complete"}, prefix, saved))
                st.button("Continue editing this section", key="participant_ui_keep_editing",
                          on_click=flow.update, kwargs={"edit_saved": False})
        with st.expander("Go to another section", expanded=False):
            render_completed_section_links(sections, "editing", prefix, saved)


def render_participant_flow(sections, stored_data: dict, session_context: dict, results: dict) -> None:
    flow = participant_flow_state()
    progress = review_progress(sections)
    if flow["stage"] == "editing" and not progress["complete"]:
        flow.update(stage="review", index=next_unreviewed_index(sections) or 0,
                    pending_navigation=None, edit_saved=False)
    st.sidebar.caption(f"{session_context['project_context'].display_name} · {session_context['participant_code']}")
    st.sidebar.markdown("**Sections**")
    for number, section in enumerate(sections, 1):
        marker = "✓" if section.review_status in REVIEWED_STATUSES else "○"
        label = f"{marker} {number}. {PARTICIPANT_TITLES[section.section_id]}"
        if flow["stage"] in {"review", "editing"} and number - 1 == flow["index"]:
            label = f"**{label}**"
        st.sidebar.markdown(label)

    st.progress(
        progress["reviewed"] / progress["total"],
        text=f"{progress['reviewed']} of {progress['total']} sections reviewed · "
             f"{progress['total'] - progress['reviewed']} remaining",
    )
    if flow["stage"] == "complete" and progress["complete"]:
        st.title("Review complete")
        columns = st.columns(4)
        columns[0].metric("Reviewed sections", progress["reviewed"])
        columns[1].metric("Corrected sections", progress["corrected"])
        columns[2].metric("Rejected sections", progress["rejected"])
        columns[3].metric("Not applicable sections", progress["not_applicable"])
        st.success("Your reviews have been saved under your participant code.")
        st.write("You can close this page, or return to check your saved responses. You do not need to submit them again.")
        st.subheader("Review or change a section")
        render_completed_section_links(sections, "completion")
        return

    section = sections[flow["index"]]
    save_requested = False
    if flow["stage"] == "editing":
        prefix, saved = initialise_participant_draft(section, stored_data, session_context)
        save_requested = render_completed_navigation(sections, prefix, saved)
        st.caption(f"Saved reviews: {progress['confirmed']} confirmed · {progress['corrected']} updated / corrected · "
                   f"{progress['rejected']} rejected · {progress['not_applicable']} not applicable")
    else:
        st.caption(f"Section {flow['index'] + 1} of {len(sections)}")
    st.title(PARTICIPANT_TITLES[section.section_id])
    st.write(PARTICIPANT_QUESTIONS.get(section.section_id, USER_FACING_QUESTIONS[section.section_id]))
    if section.section_id == "possible_next_action":
        st.write(DOCUMENTED_NEXT_STEP_GUIDANCE)
    if section.review_status in REVIEWED_STATUSES:
        st.caption(f"✓ Reviewed · {friendly_review_status(section.review_status)}")
    reviewable = render_participant_summary(section, results[section.section_id])
    render_participant_evidence(section, session_context)
    render_participant_review(section, sections, stored_data, session_context, reviewable, save_requested)


STUDY_NOT_READY = "This project is not ready for the study session. Please ask the researcher for assistance."


def study_root() -> Path:
    return Path(os.getenv("PROJECTOS_STUDY_ROOT") or REPOSITORY_ROOT).resolve()


def render_tutorial() -> None:
    st.title("Try the Echo Field example")
    st.write(
        "Echo Field is a short demonstration project used to explain how ProjectOS works. "
        "You do not need to understand its technical implementation."
    )
    try:
        sections, results, _ = read_prepared_project(tutorial_context(study_root()), DEFAULT_MODEL)
    except (CacheNotReady, ProjectConfigurationError, OSError):
        st.info(STUDY_NOT_READY)
        return
    section = sections[0]
    st.caption("Practice only · this does not count toward your study review")
    st.subheader("1. Read the summary")
    render_participant_summary(section, results[section.section_id])
    st.subheader("2. Check the source evidence")
    render_participant_evidence(section, {"project_role": "tutorial"})
    st.subheader("3. Try a response")
    st.markdown(PARTICIPANT_ACTION_GUIDANCE)
    st.caption(
        "Missing evidence can be a valid result; it does not prove that nothing happened. "
        "Your update records your interpretation separately and does not rewrite the original source evidence."
    )
    choice = st.radio(
        "How does this summary fit the project?", tuple(PARTICIPANT_ACTIONS), index=None,
        key="participant_ui_tutorial_action", persist_state="session",
    )
    correction = ""
    if PARTICIPANT_ACTIONS.get(choice) == "correct":
        correction = st.text_area("Your practice update", key="participant_ui_tutorial_correction", persist_state="session")
    if st.button("Finish tutorial", type="primary"):
        if choice is None:
            st.warning("Try one response before continuing.")
        elif PARTICIPANT_ACTIONS.get(choice) == "correct" and not correction.strip():
            st.warning("Write a practice update before continuing.")
        else:
            participant_flow_state()["stage"] = "readiness"
            st.rerun()


def render_study_session(session_context: dict) -> None:
    """Resolve only the server-bound assignment; no retrieval/API work on navigation."""
    flow = participant_flow_state()
    if flow["stage"] == "start":
        # Completed sessions reopen at the summary; first-time sessions keep their tutorial.
        try:
            project = assigned_context(session_context["participant_code"], study_root(),
                                       allowed_participant=os.getenv("PROJECTOS_STUDY_PARTICIPANT"))
            stored_data = load_session_review_store(project.review_file, project.project_id)
            completed = has_completed_reviews(stored_data)
        except (ProjectConfigurationError, OSError, ValueError):
            completed = False
        if not completed:
            render_participant_start()
            return
        flow.update(stage="complete")
    if flow["stage"] == "tutorial":
        render_tutorial()
        return
    try:
        project = assigned_context(
            session_context["participant_code"], study_root(),
            allowed_participant=os.getenv("PROJECTOS_STUDY_PARTICIPANT"),
        )
        sections, results, identity = read_prepared_project(project, DEFAULT_MODEL)
        stored_data = load_session_review_store(project.review_file, project.project_id)
        apply_review_history(sections, stored_data)
    except (ProjectConfigurationError, CacheNotReady, OSError, ValueError):
        st.info(STUDY_NOT_READY)
        st.caption("The researcher needs to check your assignment, project files and prepared summaries.")
        return
    binding = (project.project_id, str(project.data_directory), identity)
    previous_binding = st.session_state.get("participant_ui_binding")
    if previous_binding is not None and previous_binding != binding:
        clear_interface_state()
        st.info("The project preparation has changed. Please reopen your study session with the researcher.")
        return
    st.session_state["participant_ui_binding"] = binding
    if flow["stage"] == "readiness":
        # Parse the actual files once at this gate; navigation only verifies hashes.
        readiness = validate_project(project, DEFAULT_MODEL)
        if not readiness["ready"]:
            st.info(STUDY_NOT_READY)
            return
        st.title("Your project is ready")
        st.write(project.display_name)
        st.write("All six summaries are prepared. Review them against what you remember and the source evidence.")
        st.caption("Your tutorial response is not part of this review. Missing information may appear as insufficient evidence.")
        if st.button("Start my project review", type="primary"):
            next_index = next_unreviewed_index(sections)
            flow.update(stage="complete" if next_index is None else "review", index=next_index or 0)
            st.rerun()
        return
    for key in ("review_message", "summary_message"):
        message = st.session_state.pop(key, None)
        if message:
            st.success(message)
    formal_session = {
        **session_context, "project_context": project, "project_role": "participant",
        "review_file": project.review_file,
        "session_key": f"{session_context['session_key']}_{project.project_id}",
    }
    render_participant_flow(sections, stored_data, formal_session, results)


def render_study_preparation_panel() -> None:
    with st.sidebar.expander("Assigned project preparation", expanded=False):
        code = st.text_input("Researcher: participant code", key="development_study_code")
        if st.button("Check assigned project"):
            try:
                project = assigned_context(code, study_root())
                st.json(validate_project(project, DEFAULT_MODEL))
            except (ProjectConfigurationError, OSError) as error:
                st.warning(str(error))
        st.caption("This check does not call the API or display document contents. Use study_project_manager.py to prepare summaries.")


def main() -> None:
    session_context = render_session_setup()
    participant_mode = st.session_state.get("session_mode") == "Participant study"
    if participant_mode:
        st.set_page_config(layout="centered")
        st.caption("ProjectOS · Participant study")
        if session_context is None:
            st.title("Welcome to ProjectOS")
            st.write("Enter your participant code in the sidebar, then select Start participant session.")
            return
        try:
            render_study_session(session_context)
        except Exception:
            st.info(STUDY_NOT_READY)
        return
    else:
        st.set_page_config(layout="wide")

    if not participant_mode:
        render_development_intro()
        render_study_preparation_panel()

    for message_key in ("review_message", "summary_message"):
        message = st.session_state.pop(message_key, None)
        if message:
            st.success(message)

    try:
        with st.spinner("Preparing the project records..."):
            documents, chunks, retriever = initialise_retrieval()
        sections, stored_data = build_current_brief(
            retriever, len(chunks), session_context["review_file"],
        )
    except Exception as error:
        st.error("ProjectOS could not prepare the project records.")
        if not participant_mode:
            st.exception(error)
        else:
            st.caption("Please ask the researcher for help. Saved reviews have not been reset.")
        return

    render_development_flow(session_context, documents, chunks, sections, stored_data)


def render_development_intro() -> None:
    apply_interface_style()

    st.title("ProjectOS")

    st.subheader(
        "Pick up where you left off"
    )

    st.markdown(
        """
        <div class="projectos-intro">
        ProjectOS uses your existing project records to help you
        remember what changed, what remains unresolved and what you
        may do next. Read each section and tell the system whether
        its interpretation is still accurate.
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.info(
        "You remain in control: accepting, "
        "updating or rejecting a summary "
        "does not remove the original "
        "project records."
    )


def render_development_flow(session_context, documents, chunks, sections, stored_data) -> None:
    """Retain the full technical overview and development controls."""
    current_summary_count = (
        count_current_summaries(
            sections
        )
    )

    has_any_summary = (
        current_summary_count > 0
    )

    participant_mode = (
        session_context["mode"]
        == "participant"
    )

    st.markdown(
        "### Create your project overview"
    )

    st.write(
        "ProjectOS will create six short "
        "summaries from the supporting "
        "records shown below."
    )

    generate_clicked = False

    if (
        participant_mode
        and has_any_summary
    ):
        st.success(
            "The re-entry summary has been "
            "generated for this participant "
            "session."
        )

    else:
        action_label = (
            "Regenerate re-entry summary"
            if has_any_summary
            else "Generate my re-entry summary"
        )

        generate_clicked = st.button(
            action_label,
            type="primary",
            width="content",
            key=(
                "generate_summary_"
                f"{session_context['session_key']}"
            ),
        )

    st.caption(
        "Generating summaries sends the "
        "selected project excerpts to the "
        "OpenAI API. Avoid including personal "
        "or sensitive information in test "
        "documents."
    )

    if generate_clicked:
        if not os.getenv(
            "OPENAI_API_KEY"
        ):
            st.error(
                "OPENAI_API_KEY is not "
                "configured in this terminal."
            )

        else:
            force_refresh = (
                has_any_summary
                and not participant_mode
            )

            generate_all_summaries(
                sections=sections,
                force_refresh=force_refresh,
            )

            generated_count = len(
                st.session_state.get(
                    "summary_results",
                    {},
                )
            )

            failed_count = len(
                st.session_state.get(
                    "summary_errors",
                    {},
                )
            )

            st.session_state[
                "summary_message"
            ] = (
                f"Generated {generated_count} "
                "summary sections. "
                f"Failed sections: "
                f"{failed_count}."
            )

            st.rerun()

    reviewed_sections = sum(
        1
        for section in sections
        if normalise_status(
            section.review_status
        )
        != "unreviewed"
    )

    show_research_details = (
        render_project_sidebar(
            session_context=(
                session_context
            ),
            documents=documents,
            chunks=chunks,
            sections=sections,
            stored_data=stored_data,
            current_summary_count=(
                current_summary_count
            ),
            reviewed_sections=(
                reviewed_sections
            ),
        )
    )

    st.divider()

    st.markdown(
        "## Your re-entry summary"
    )

    st.write(
        "Review the six sections below "
        "before continuing your project."
    )

    for section_number, section in enumerate(
        sections,
        start=1,
    ):
        render_section(
            section=section,
            section_number=section_number,
            show_research_details=(
                show_research_details
            ),
            review_file=(
                session_context[
                    "review_file"
                ]
            ),
            session_key=(
                session_context[
                    "session_key"
                ]
            ),
        )

    st.caption(
        "Iteration 1 prototype · "
        "Project summaries remain "
        "provisional, source-grounded "
        "and correctable."
    )


if __name__ == "__main__":
    main()
