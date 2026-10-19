---
project: ProjectOS
document_type: open_issues
status: iteration_2_implementation_for_review
date: 2026-10-19
---

# Current limitations and review gates — Iteration 2

Updated 19 October 2026. The approved implementation brief records Round 1 as complete. The earlier preparation checklist below is retained as history, not a statement that P01 has yet to start.

- Clearer wording and Not applicable need participant evaluation; technical checks do not establish comprehension or reduced verification effort.
- Retrieval can still surface historical, resolved or conditional records. Source visibility does not prove currentness, and missing evidence does not prove that an event never occurred.
- Not applicable is separate from confirmation and rejection. Comparisons of review frequencies must account for the added action; do not reinterpret older responses or pool them silently.
- Evidence opening and assistance remain manual observations. The system does not record a complete interaction log.
- Consent, retention and external-service wording are unchanged. Check the applicable participant-facing materials before any further study activity; this implementation makes no new ethics claim.
- Continue one supervised session at a time. Keep source packs and prepared summaries fixed, retain private records outside Git, and preserve corrections as user interpretations rather than source evidence.

See [Iteration 2 validation](../../outputs/test_results/iteration_2_usability_validation.md). The retrieval freeze and non-goals in [TD-003](../decisions/technical_decisions/td_003_freeze_automatic_project_state_inference.md) remain in force.

## Historical Round 1 preparation record — 8–9 October 2026

The dated text below is preserved for context; it does not describe the current study stage.


# Open issues before Round 1

The prototype is frozen for study preparation. Engineering tests and a researcher's successful navigation rehearsal do not establish semantic accuracy or permission to collect participant-owned material.

Supervisor confirmation received on 9 October 2026: no amendment to the existing ethics approval is required. Participant-facing documents must clearly state what data will be stored, where it will be stored, and for how long. This confirmation concerns the existing approval; it is not a new ethics approval.

## Remaining checks before recruitment and collection

| Open decision | Required resolution |
| --- | --- |
| Supervisor feedback recorded | No ethics amendment is required. Meeting 3 on 15 October 2026 at 15:00 (Europe/London) will review the revised wording; do not describe this as a new approval. |
| Information and consent | Review the revised drafts, including 4–8 files, text processing, external excerpts, possible identifying content and no public upload. Complete private contact and independent-concerns routes. |
| Storage and access | Restricted UAL OneDrive is specified; necessary temporary preparation/session copies use the password-protected computer. Check folder permissions, transfer method, authorised access and deletion of all working/backup copies. Git exclusion alone is not secure storage. |
| Retention implementation | Source files, extracted text and temporary copies: permanently delete within 7 calendar days after the session. De-identified records and separately stored signed consent: retain until 30 November 2027, then permanently delete. Check that the manual deletion procedure covers every copy. |
| Withdrawal wording and contact | Identifiable data may be withdrawn within 7 calendar days; delete separate identity linkage after that period. After link deletion and aggregation, withdrawal may no longer be possible. Complete the contact route and session-specific deadline in issued copies. |
| API account settings | Check actual account/model settings, data sharing and processing location. Names/contact details will not deliberately be sent; abuse-monitoring logs may remain up to 30 days. Do not assume zero retention or regional processing. |
| Study practicality | Confirm the 40–50 minute schedule, [R1-R7, Round 1 v1](../feedback/user_testing/iteration_1/round_1_templates/post_test_ratings_template.md) custom exploratory ratings, manual observations and no recording/screenshots. Rehearse with non-personal material after document review. |

See the [ten-point materials gap check](../feedback/user_testing/iteration_1/study_materials_gap_check_round_1.md). All participant-facing forms and the [Round 1 protocol](../feedback/user_testing/iteration_1/study_protocol_round_1_draft.md) remain draft. Formal P01 has not started.

## Known prototype limits to disclose and observe

- Related evidence may be historical, resolved, conditional or wrongly attributed. Currentness is not inferred reliably; an absent source does not prove that the real project lacks feedback or a decision.
- P96 exposed retrieval weaknesses, especially in current/superseded directions, unresolved tensions and next action. P96 is a researcher self-test, not a participant result. [TD-003](../decisions/technical_decisions/td_003_freeze_automatic_project_state_inference.md) freezes further automatic retrieval extensions.
- Review events are not durably linked to exact generated-summary snapshots. Keep source packs and prepared summaries fixed within a session, and record the reviewed version privately.
- A later confirmation can remove a correction from the active display while retaining its event history. Observe this and explain only if needed; do not change it during the study or silently treat it as participant intent.
- The application saves review actions, correction text and reasons when supplied. Evidence expansions, timings, baseline accounts, ratings and interview notes need manual research records. There is no complete telemetry system.
- JSON storage has no concurrent-write coordination or user authentication. Use one supervised loopback-only session at a time, stop it between participants, and never overwrite previous records.
- Missing or stale prepared caches block participant review. Preparation is a researcher task after consent; do not regenerate while the participant is reviewing.

## Interpretation and presentation limits

Three purposively selected cases cannot establish statistical significance, population accuracy, productivity gains or a causal effect of evidence visibility. Self-selected packs, researcher categorisation, the baseline writing task, think-aloud and assistance can influence responses. Record these limitations.

The [P00 pilot summary](../feedback/user_testing/iteration_1/pilot_p00_summary.md) remains unchanged and excluded from the formal sample. Historical documents describe different sample sizes, durations and an Echo Field task; the new protocol is the canonical Round 1 proposal. The implementation chapter and old screenshots remain historical, not current study evidence.
