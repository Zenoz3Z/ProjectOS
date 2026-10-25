# DD-006 — Actionable evidence absence and clearer review semantics

Date: 25 October 2026. Status: final prototype design response, for local review. **Not evaluated with new participants.**

## Evidence and scope

The [completed Round 2 findings](../../feedback/user_testing/iteration_2/round_2_final_findings.md) concern two participants with complete or largely complete projects. Evidence panels were observed opened in 2/12 sections; Not applicable was used in 9/12. P03 requested an explanation of which kinds of information or records might help when a section was insufficient. This paraphrased need is not a request documented from both participants.

The [cross-iteration findings](../../feedback/user_testing/iteration_2/cross_iteration_findings.md) distinguish genuine absence, missed evidence and historical states that no longer apply. Low opening frequency does not prove that participants ignored or misunderstood evidence. Frequent Not applicable responses do not establish interface improvement. The study remains four formal participants, n=2 per round, with P00/P96 excluded and no P05.

## Decision

Make three presentation changes in the participant flow and tutorial:

1. When the prepared summary's support status is insufficient, explain that ProjectOS could not establish the section from its selected evidence. Information may be absent, outdated or not retrieved. Add a short section-specific suggestion about records the user may want to check. An unknown section receives generic wording; other support statuses receive no absence guidance.
2. Share four definitions, ordered Confirm, Update, Reject, Not applicable. Confirm expresses assessed alignment; Update supplies a corrected current interpretation; Reject identifies misleading or unsupported reconstruction; Not applicable concerns the project's current state. Clarify that leaving something unchecked is not confirmation and non-applicability is not a synonym for system error. These definitions inform the user's judgement without determining the response.
3. Before selecting an action, offer an explicit optional reminder to open source evidence. Keep evidence collapsed by default, with no required checkbox, extra field, logging or save gate.

The record suggestions cover project overviews/goals, decision/process logs, current-versus-earlier directions, attributable feedback, blockers/reflections and documented next steps/completion. They are conditional aids, not a diagnosis that a file is missing. No upload, automatic search, generated recommendation or model request is added.

## Implementation boundary

The UI reads `GroundedSummary.support_status` returned by `study_cache.read_prepared_project`. It does not substitute the section's retrieval `evidence_status`, review action or presence of evidence items. Those fields answer different questions. Pure presentation helpers and constants live in `participant_flow.py`; the Streamlit renderer consumes them without modifying cached results.

Stored values remain `confirm`, `correct`, `reject` and `not_applicable`. Summary, review and assignment schemas remain unchanged. Corrections and notes stay separate from source evidence and do not affect summary fingerprints. First-pass navigation, completion shortcuts, draft protection, append-only events, refresh recovery and project isolation remain unchanged.

Retrieval, chunking, prompts, summary generation and cache fingerprint code are outside scope. Changing them would change the evidence pathway and exceed this final interface response; these messages cannot repair missing retrieval coverage or infer currentness. [TD-003](../technical_decisions/td_003_freeze_automatic_project_state_inference.md) remains in force.

## Study closure and limitations

No further recruitment is planned: both study rounds are closed, and this implementation is a bounded response for the final submission. There is no third participant round. Feature development is frozen after this final design response; remaining work is thesis integration, portfolio preparation, final validation and submission preparation.

The [validation report](../../../outputs/test_results/iteration_3_evidence_guidance_validation.md) distinguishes the researcher-reported local automated result from the synthetic browser attempt, which was blocked during Codex runtime startup. No browser-interaction pass or new participant evaluation is claimed. Technical checks cannot establish that the wording improves comprehension, increases evidence checking or reduces burden. Suggested record types may not suit every creative project. Existing timing, R6 and interpretation ambiguities remain in the unchanged study findings. No thesis text or participant record is rewritten to support this iteration.
