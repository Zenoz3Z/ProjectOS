---
project: ProjectOS
document_type: open_issues
status: iteration_3_validation_and_review
date: 2026-10-25
---

# Current limitations and final review gates

Updated 25 October 2026. Both participant rounds are closed with four formal participants, n=2 per round. P00/P96 remain excluded, there is no P05 and no further recruitment is planned.

- Iteration 3 is a final design response to the completed study, not participant-validated improvement. Technical checks and synthetic browser use cannot establish comprehension or greater evidence checking.
- The researcher reported **129 passed in 145.16s** in the local environment after restarting Windows. The Codex synthetic browser attempt remained blocked at asyncio/socketpair during Streamlit startup; its interaction checklist remains unverified in this attempt. This is an isolated-environment limitation, not an observed product assertion failure.
- Insufficient summary support cannot identify whether records are absent, outdated or missed. The new static guidance suggests types to check; it neither diagnoses missing files nor changes retrieval.
- Confirm remains a user's assessment, not independently verified truth. Not applicable describes current relevance, while Reject concerns misleading or unsupported reconstruction. Wording alone cannot guarantee consistent interpretation.
- The rounds used different participants, projects and response sets. Round 2 projects were complete or largely complete. No causal effect or generalisable accuracy is established.
- Round 1 lacks independent baselines and one opening observation. One session's timing conflicts with saved timestamps. P03 R6 remains ambiguous; no composite or inferential analysis is supported.
- Evidence opening and assistance are manually observed, not complete interaction logs. Saved reviews lack a durable link to exact viewed-summary snapshots.
- Feature development is frozen after this final design response. Remaining work is thesis integration, portfolio preparation, final validation and submission preparation; automatic retrieval expansion and temporal reasoning remain out of scope.
- Existing consent, storage and withdrawal obligations remain unchanged. Study closure does not establish document issuance, deletion completion or new ethics approval.

See [DD-006](../decisions/design_decisions/dd_006_iteration_3_actionable_evidence_absence.md), [Iteration 3 validation](../../outputs/test_results/iteration_3_evidence_guidance_validation.md) and the preserved [cross-iteration findings](../feedback/user_testing/iteration_2/cross_iteration_findings.md). Earlier preparation gates below remain dated history.

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
