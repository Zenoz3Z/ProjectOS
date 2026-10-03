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


PARTICIPANT_CODE_PATTERN = re.compile(r"^P\d{2,3}$")


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


def empty_review_store() -> dict:
    """Return a valid empty review store for a new session."""
    return {
        "schema_version": 1,
        "project_id": PROJECT_ID,
        "review_events": [],
    }


def load_session_review_store(
    review_file: Path,
) -> dict:
    """Load one session's reviews without creating a file."""
    if not review_file.exists():
        return empty_review_store()

    return load_review_store(
        file_path=review_file,
        project_id=PROJECT_ID,
    )


def participant_review_file(
    participant_code: str,
) -> Path:
    """Return the isolated review path for one participant."""
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

    session_mode = st.sidebar.radio(
        "Mode",
        options=(
            "Development",
            "Participant study",
        ),
        help=(
            "Development uses your existing review history. "
            "Participant study stores each participant separately."
        ),
        key="session_mode",
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
    ).strip().upper()

    start_clicked = st.sidebar.button(
        "Start participant session",
        type="primary",
        use_container_width=True,
    )

    if start_clicked:
        if not PARTICIPANT_CODE_PATTERN.fullmatch(
            participant_input
        ):
            st.sidebar.error(
                "Enter a code such as P01, P02 or P100."
            )
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
        active_review_file = participant_review_file(
            active_code
        )

        st.sidebar.success(
            f"Active participant: {active_code}"
        )

        if active_review_file.exists():
            st.sidebar.caption(
                "This participant code already has saved data. "
                "The session has been reopened rather than reset."
            )

        end_clicked = st.sidebar.button(
            "End participant session",
            use_container_width=True,
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
            "review_file": active_review_file,
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
) -> None:
    """Save one section-level review event."""
    correction_to_save = None

    if action == "correct":
        correction_to_save = correction

    event = create_review_event(
        project_id=PROJECT_ID,
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
) -> None:
    """Mark one record as belonging to an older direction."""
    event = create_review_event(
        project_id=PROJECT_ID,
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


def main() -> None:
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

    session_context = (
        render_session_setup()
    )

    if session_context is None:
        st.warning(
            "A participant study session "
            "has not started. Enter the "
            "participant code in the sidebar "
            "and select "
            "'Start participant session'."
        )

        st.stop()

    review_message = (
        st.session_state.pop(
            "review_message",
            None,
        )
    )

    if review_message:
        st.success(review_message)

    summary_message = (
        st.session_state.pop(
            "summary_message",
            None,
        )
    )

    if summary_message:
        st.success(summary_message)

    try:
        with st.spinner(
            "Preparing the project records..."
        ):
            documents, chunks, retriever = (
                initialise_retrieval()
            )

        sections, stored_data = (
            build_current_brief(
                retriever=retriever,
                total_chunks=len(chunks),
                review_file=(
                    session_context[
                        "review_file"
                    ]
                ),
            )
        )

    except Exception as error:
        st.error(
            "ProjectOS could not prepare "
            "the project records."
        )

        st.exception(error)
        st.stop()

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
            use_container_width=False,
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