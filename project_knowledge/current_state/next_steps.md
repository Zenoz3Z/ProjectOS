---
project: ProjectOS
document_type: next_steps
status: iteration_3_review_and_submission
date: 2026-10-25
---

# Current next steps — final prototype review and submission

Updated 25 October 2026. The participant study is complete with P01/P02 and P03/P04, four formal participants. There is no P05, no third participant round and no further recruitment.

1. **Review the final design response.** Inspect [DD-006](../decisions/design_decisions/dd_006_iteration_3_actionable_evidence_absence.md) and the [technical validation report](../../outputs/test_results/iteration_3_evidence_guidance_validation.md). Iteration 3 adds conditional evidence guidance, consistent action definitions and an optional evidence reminder. No new participant validation is claimed.
2. **Maintain the feature freeze.** Keep retrieval, prompts, cache fingerprints, schemas, project isolation and participant records fixed. No further features, source-pack changes or summary regeneration are planned.
3. **Integrate reviewed evidence into the thesis.** Distinguish completed Round 1/Round 2 findings from the later, untested design response. Preserve n=2 per round, rating and timing ambiguities and missing observations. The three existing thesis drafts remain unchanged in this implementation task.
4. **Prepare the portfolio and final submission.** Review implementation evidence, documentation links, privacy exclusions and deliverables. Preserve the distinction between the researcher-reported local test pass and the browser attempt blocked by the Codex runtime; any later manual interface check needs its own record. Continue consent/retention obligations without inferring compliance from study closure.

The [Round 2 findings](../feedback/user_testing/iteration_2/round_2_final_findings.md) and [cross-iteration comparison](../feedback/user_testing/iteration_2/cross_iteration_findings.md) remain historical study evidence, not an evaluation of Iteration 3. R1-R7 remain frozen. Automatic temporal reasoning, new retrieval algorithms, self-service upload and public deployment remain out of scope.

## Historical Round 1 preparation record — 8–9 October 2026

The dated text below is preserved for context; it does not describe the current study stage.


# Proposed next steps

The next priority is a reviewable first-round study package, not another retrieval implementation. The core question concerns source visibility and user correction during project re-entry. Follow [TD-003](../decisions/technical_decisions/td_003_freeze_automatic_project_state_inference.md) and retain the stable production code.

1. **Review wording at Meeting 3, 15 October 2026 at 15:00 (Europe/London).** Use the [Round 1 protocol](../feedback/user_testing/iteration_1/study_protocol_round_1_draft.md), [materials gap check](../feedback/user_testing/iteration_1/study_materials_gap_check_round_1.md) and [data protocol](../feedback/user_testing/iteration_1/participant_owned_project_data_protocol_draft.md). Supervisor confirmation received on 9 October 2026: no amendment to the existing ethics approval is required. Participant-facing documents must clearly state what data will be stored, where it will be stored, and for how long.
2. **Complete the release checks.** Review the added restricted UAL OneDrive/password-protected computer wording, seven-day source deletion and withdrawal period, and 30 November 2027 retention deadline for de-identified records and separate consent forms. Complete contact routes and verify transfer/access, backup deletion and actual API settings. The three-adult, 40–50 minute procedure is unchanged. Prepare consistent final information and consent copies after wording review.
3. **Rehearse the approved procedure with non-personal material.** Time the independent baseline, tutorial, six-section review, ratings and interview. Use the existing [question/observation guide](../feedback/user_testing/iteration_1/post_test_questionnaire_and_interview.md) and only [R1-R7, Round 1 v1](../feedback/user_testing/iteration_1/round_1_templates/post_test_ratings_template.md) for formal ratings; L1-L7 remains historical. Record assistance and missing observations; do not add instrumentation or tune retrieval to produce agreeable answers.
4. **Only after the start gate is satisfied, recruit and receive consented packs.** Ask for 4–8 self-selected non-sensitive files for one paused long-term creative project. Screen and import with the participant's agreement, log researcher preparation decisions, then prepare and freeze summaries. Do not create formal participant assignments before authorisation.
5. **Conduct the three agreed sessions and analyse them.** Separate automatic review events from manual observations, exclude tutorial/P00/P96 records, retain negative and mixed cases, and report descriptive statistics and themes without significance claims.
6. **Decide the next design step from findings.** Consider source presentation, correction and evidence absence first. Explicit temporal metadata could become a user-facing mechanism or future work; no automatic temporal or contradiction reasoning is scheduled.

Supervisor confirmation about the unchanged existing approval is recorded; it is not a new ethics approval. Formal recruitment, material collection and P01 have not begun. Earlier development priorities remain documented in dated logs and Git history; they are not current instructions to modify the prototype.
