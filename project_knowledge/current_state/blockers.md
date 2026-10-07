---
project: ProjectOS
document_type: open_issues
status: current
date: 2026-10-04
---

# Open issues before participant evaluation

These issues were identified by comparing the implementation and research documents on 4 October 2026. They remain open; documenting them does not resolve them.

**5 October update:** the pre-test interaction refinement adds a per-section summary recovery control, progressive review, unsaved-input protection and completion feedback. The retry issue in the original table below is therefore addressed in the UI. Review-version association and the underlying confirm-after-correct behaviour remain unchanged. The [P00 pilot summary](../feedback/user_testing/iteration_1/pilot_p00_summary.md) records why the interaction was refined; P00 is excluded from the formal sample.

## Prototype behaviour

**7 October update:** assigned-project review now requires six valid prepared summaries. Missing/stale caches stop the review and are repaired by the researcher through the CLI; the participant's generation/retry control has been removed from this workflow. Source/prompt/model changes invalidate the durable project cache. Development mode still uses the older retrieval cache. Additional automated assignment, cache, path and UI checks are documented in the [readiness validation report](../../outputs/test_results/formal_study_readiness.md). Review-version association and confirm-after-correct semantics remain unchanged. The original issue table below describes the earlier implementation.

**Formal-study blocker:** participant-owned project materials and external API excerpts need explicit coverage in revised information and consent materials, plus supervisor confirmation of whether an ethics amendment is necessary. The [new draft](../feedback/user_testing/iteration_1/participant_owned_project_data_protocol_draft.md) is not approval. Timings, participant allocation and withdrawal/retention decisions still need agreement. No real participant project packs were used in technical QA.

| Issue | Consequence for a study | Relevant implementation |
| --- | --- | --- |
| Participant mode has no direct retry control after partial summary generation or evidence invalidation. | A session may contain missing summaries that the participant cannot regenerate. | [Streamlit interface](../../src/streamlit_app.py) |
| Review events are associated with sections, without a durable snapshot of the exact generated summary. | A new interpretation can inherit a review that referred to earlier wording. | [Review storage](../../src/review_store.py) and [brief reconstruction](../../src/reentry_brief.py) |
| A confirmation following a correction clears the correction from the active display, although the event remains in history. | The visible state may no longer reflect the wording the user corrected. | [Brief reconstruction](../../src/reentry_brief.py) |
| Changes to source files do not automatically invalidate cached retrieval resources. | An edited demonstration archive may not appear until the application is restarted. | [Streamlit interface](../../src/streamlit_app.py) |

The 23 existing automated tests cover structure, storage and summary validation. They do not cover the full browser interaction or verify whether summaries faithfully reconstruct the project. JSON storage also lacks concurrent-write coordination and authentication; the current scope is supervised local use.

## Study documents to reconcile

- **Duration:** the [information sheet](../feedback/user_testing/iteration_1/participant_information_sheet.md) estimates 25–35 minutes. The [protocol](../feedback/user_testing/iteration_1/participant_test_protocol.md) states 30–35 minutes, but its six activity estimates total 35–40 minutes. A complete timed rehearsal is needed before setting one duration across the materials.
- **Participant allocation:** the [19 September evaluation plan](evaluation_plan_v0.md) proposes three formative participants followed by five new participants. The [1 October research questions](../feedback/user_testing/iteration_1/research_questions.md) describe approximately five to eight participants for Iteration 1. The intended total and allocation across iterations need supervisor agreement.
- **Rating scale:** the earlier evaluation plan proposes five-point ratings; the current [questionnaire](../feedback/user_testing/iteration_1/post_test_questionnaire_and_interview.md) uses seven-point ratings. Final study materials should identify the chosen instrument consistently while retaining the earlier plan as a dated draft.
- **Participant-facing fields:** researcher and supervisor contacts, withdrawal arrangements and retention details in the blank information sheet and [consent form](../feedback/user_testing/iteration_1/participant_consent_form.md) need completion in the private study copies before use.
- **Observation records:** review events are saved automatically. Evidence-opening behaviour, task duration, questionnaire responses and interviews require separate researcher records; they are not all captured by the application.

## Presentation and evidence limits

The committed screenshots show an earlier command-line brief and an early wireframe, not the current Streamlit interface. A current screenshot should use only demonstration content and be inspected before inclusion.

The [implementation chapter](../../report/drafts/04_design_and_implementation.md) covers Iteration 0. The [Day 7](../process/daily_logs/day_7_llm_reentry_summary.md) and [Day 8](../process/daily_logs/day_8_user_research_preparation.md) logs document later work that still needs to be integrated into the chapter.

No completed ProjectOS participant findings are included in the repository. Technical rehearsals and retrieval results should not be presented as user-study outcomes.
