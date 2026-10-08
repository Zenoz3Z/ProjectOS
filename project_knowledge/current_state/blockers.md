---
project: ProjectOS
document_type: open_issues
status: current
date: 2026-10-08
---

# Open issues before Round 1

The prototype is frozen for study preparation. Engineering tests and a researcher's successful navigation rehearsal do not establish semantic accuracy or permission to collect participant-owned material.

## Decisions that block recruitment and collection

| Open decision | Required resolution |
| --- | --- |
| Supervisor/ethics scope | Anna must confirm the move to participant-owned projects, three adults, external API preparation and any necessary amendment/approval route. A supervisor discussion alone must not be recorded as institutional approval. |
| Information and consent | Review the revised drafts, including 4–8 files, text processing, external excerpts, possible identifying content and no public upload. Complete private contact and independent-concerns routes. |
| Storage and access | Agree an approved transfer method, storage location, authorised access, device protection and backup handling. Git exclusion alone is not secure storage. |
| Retention | Set a duration, start trigger and deletion method for raw packs, caches/summaries, review/correction data, baseline notes, ratings/interviews, consent/code linkage and backups. No period has been invented. |
| Withdrawal | Agree contact route, deadline, what can be removed, analysis/publication cut-off and provider-side limits. Put the same decisions in all issued copies. |
| API account and policy | Confirm the institution accepts this external processor and the actual account/model settings, including data sharing, retention and processing location. Do not assume zero retention or regional processing. |
| Study practicality | Confirm the 40–50 minute schedule, seven-point exploratory ratings, manual observations and no recording/screenshots. Rehearse with non-personal material after document review. |

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
