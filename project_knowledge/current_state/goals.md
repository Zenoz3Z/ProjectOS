---
project: ProjectOS
document_type: current_goals
status: iteration_3_final_design_response
date: 2026-10-25
---

# Current goals — final design response and submission

Updated 25 October 2026. Round 1 and Round 2 are complete with four formal participants, n=2 per round. P00 and P96 are excluded; there is no P05 and no further recruitment is planned. Iteration 3 is the final prototype design response, not a third participant study.

The research question remains: “How do source visibility and user correction help creative practitioners assess an AI-generated reconstruction of a long-term project during project re-entry?”

[DD-006](../decisions/design_decisions/dd_006_iteration_3_actionable_evidence_absence.md) responds to the [Round 2 findings](../feedback/user_testing/iteration_2/round_2_final_findings.md) with conditional evidence guidance, clearer review definitions and an optional source-checking reminder. These changes have not been evaluated with new participants. Their implementation does not establish better comprehension, verification or reconstruction accuracy.

Feature development is frozen after this final design response. Remaining work is reviewed thesis integration, portfolio preparation, final validation and submission preparation. The researcher reported a local full-suite result of **129 passed in 145.16s**; the Codex synthetic browser attempt was blocked during runtime startup and is not a browser pass. See the [validation report](../../outputs/test_results/iteration_3_evidence_guidance_validation.md), [limitations](blockers.md) and [next steps](next_steps.md).

Preserve the frozen R1-R7 wording, source packs, caches, append-only reviews, research findings and three existing thesis drafts. Automatic temporal reasoning, retrieval extensions, uploads and deployment remain outside this iteration. Conditional document-type suggestions do not diagnose why evidence is insufficient.

## Historical Round 1 preparation record — 8–9 October 2026

The dated text below is preserved for context; it does not describe the current study stage.


# Current research goals

> How do source visibility and user correction help creative practitioners assess an AI-generated reconstruction of a long-term project during project re-entry?

The technical exploration phase is closed for the first research round. The stable prototype is the study instrument, not a claim of accurate automatic project-state inference. See [TD-003](../decisions/technical_decisions/td_003_freeze_automatic_project_state_inference.md).

## Research priorities

1. Observe how people use visible sources, including absent or inadequate evidence, to assess a provisional reconstruction.
2. Understand when and why people Confirm, Update or Reject it, and whether correction gives them useful control.
3. Examine clarity, project re-entry value, verification effort and the risk of misleading interpretations.
4. Use descriptive statistics and thematic analysis to inform a later design iteration, without claims of statistical significance or improved reconstruction accuracy.

## Round 1 proposal — not approved

Three adults would each return to one of their own long-term creative projects after a pause. They would select 4–8 non-sensitive existing files, consent before providing them, and attend a supervised 40–50 minute session on the researcher's computer. The researcher would screen and import the pack and prepare summaries before the session. An independent written account of the project's current state would precede the tutorial and generated brief.

Echo Field remains a short interaction tutorial. The assigned project is reviewed in six sections; completion unlocks direct section editing. Navigation and saving use prepared summaries and do not call the API. This study adds no production feature.

Formal P01 has not started. P00 is an excluded usability pilot; P96 is an excluded researcher self-test. Neither is part of the proposed three-person sample, and P96 review statistics are not formal research findings.

## Non-goals

- Automatic temporal reasoning.
- Automatic contradiction detection.
- Self-service upload.
- Public deployment.
- User accounts.
- Perfect reconstruction accuracy.

Retrieval extensions are frozen. Explicit, user-visible temporal metadata may be considered after user testing or as future work; it is not currently implemented.

## Start gate and reading

Supervisor confirmation received on 9 October 2026: no amendment to the existing ethics approval is required. Participant-facing documents must clearly state what data will be stored, where it will be stored, and for how long.

The storage schedule has been added. Information and consent materials remain drafts for wording review at Meeting 3 on 15 October 2026 at 15:00 (Europe/London), with contact fields to complete before issue. Formal recruitment and P01 have not started; this documentation update does not collect project packs or process participant materials.

- [Round 1 protocol](../feedback/user_testing/iteration_1/study_protocol_round_1_draft.md).
- [Research questions](../feedback/user_testing/iteration_1/research_questions.md) and [question/observation guide](../feedback/user_testing/iteration_1/post_test_questionnaire_and_interview.md).
- [Formal post-test ratings: R1-R7, Round 1 v1](../feedback/user_testing/iteration_1/round_1_templates/post_test_ratings_template.md), wording and freeze date unchanged; review-draft status reflects the 9 October supervisor feedback.
- [Materials gap check](../feedback/user_testing/iteration_1/study_materials_gap_check_round_1.md).
- [Open blockers](blockers.md) and [next steps](next_steps.md).

This current-state update supersedes the prepared-archive and larger-sample proposals in earlier plans. Dated logs, the earlier evaluation plan and the P00 pilot record remain historical records; earlier document versions are retained in Git.
