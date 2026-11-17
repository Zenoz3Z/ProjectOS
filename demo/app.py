"""Thin adapter to the unchanged production six-section review UI."""

import os
from pathlib import Path
import streamlit as st

from demo.runtime import DemoError, load_prepared
from study_cache import CacheNotReady


def main():
    if not os.getenv("PROJECTOS_DEMO_PACKAGE") or not os.getenv("PROJECTOS_DEMO_SESSION"):
        st.error("Start this tutorial with python -B demo/launch.py from the repository root.")
        st.stop()
    package = Path(os.environ["PROJECTOS_DEMO_PACKAGE"])
    try:
        context, sections, results, _ = load_prepared(package, os.environ["PROJECTOS_DEMO_SESSION"])
    except (DemoError, CacheNotReady) as error:
        st.error(f"The prepared tutorial is missing or incompatible: {error}. No automatic generation is available.")
        st.stop()
    import streamlit_app as ui
    from participant_flow import has_completed_reviews, next_unreviewed_index
    stored = ui.load_session_review_store(context.review_file, context.project_id)
    ui.apply_review_history(sections, stored)
    st.set_page_config(page_title="ProjectOS tutorial", layout="centered")
    ui.apply_interface_style()
    st.title("ProjectOS")
    st.caption("Echo Field · Tutorial example · Pre-generated summaries")
    st.caption("Demo responses are saved only in this local tutorial session, separately from the original records and summaries. No participant data is shown.")
    st.session_state.setdefault("participant_ui_flow", {
        "stage": "complete" if has_completed_reviews(stored) else "review",
        "index": next_unreviewed_index(sections) or 0, "prepare": False,
    })
    if message := st.session_state.pop("review_message", None):
        st.success(message)
    ui.render_participant_flow(sections, stored, {
        "project_context": context, "participant_code": "Tutorial", "project_role": "tutorial",
        "review_file": context.review_file, "session_key": "demo_echo_field",
    }, results)


if __name__ == "__main__":
    main()
