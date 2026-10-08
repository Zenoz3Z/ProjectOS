---
project: ProjectOS
document_type: study_protocol
iteration: 1
date: 2026-10-08
status: draft_pending_supervisor_ethics_confirmation
proposed_participants: 3
estimated_session_duration: 40-50 minutes
---

# Round 1 study protocol — draft

**Review copy only. No recruitment, collection of materials or formal P01 setup yet.** Anna must confirm the supervisor/ethics scope, and any required institutional approval must be in place before the study begins. This document does not imply approval.

## Research question and boundaries

> How do source visibility and user correction help creative practitioners assess an AI-generated reconstruction of a long-term project during project re-entry?

The study investigates source visibility, evidence absence, correction, clarity, control, verification effort and misleading reconstruction. The stable six-section prototype is frozen under [TD-003](../../../decisions/technical_decisions/td_003_freeze_automatic_project_state_inference.md).

Non-goals: automatic temporal reasoning, automatic contradiction detection, self-service upload, public deployment, user accounts and perfect reconstruction accuracy. No heading-aware, hybrid or other retrieval expansion is introduced for this round.

## Start gate

All of the following must be resolved before recruitment or receipt of project packs:

- Anna's documented scope review and any required institutional ethics confirmation/amendment.
- Agreed three-adult eligibility and voluntary recruitment arrangements.
- Final information and consent forms with actual contact routes, per-data-type retention, withdrawal/deletion and independent concerns route.
- Agreed private transfer, protected storage, authorised access and backup arrangements.
- Confirmation of external API processing, actual study account/model settings and institutional acceptability.
- A consistent 40–50 minute procedure, manual measurement plan and timed rehearsal with non-personal material.

The [gap check](study_materials_gap_check_round_1.md) records what remains open. Do not collect project files as an informal rehearsal while these gates remain unresolved.

## Participants and preparation

Propose **three adults aged 18 or over**, creative students or practitioners, each with one long-term creative project they genuinely worked on and have paused. An interruption of one to two weeks or longer is proposed for scope discussion; Anna must confirm the operational threshold. No AI expertise is required.

P00 is an excluded pilot. P96 is an excluded researcher self-test. Neither contributes to the three-person sample or formal findings. Formal P01 has not started.

After authorisation and consent, each participant supplies **4–8 self-selected, screened, non-sensitive existing files** using the [pack guide](participant_project_pack_guide.md). The researcher assists with import and records redactions, filenames/categories and exclusions privately. Missing categories are allowed; never fabricate feedback or material to make every section answerable. If fewer than four safe records exist, discuss eligibility rather than making filler records.

Prepare summaries before the session under the [data protocol](participant_owned_project_data_protocol_draft.md). Keep received source material, prepared cache and reviewed version fixed during the session. Record stable code version, pack/preparation identifiers and any assistance in private notes; do not publish project content. Do not tune queries, switch models or regenerate to improve a participant's apparent outcome.

Pack selection, consent and preparation occur beforehand and are additional to the supervised session. The time burden of pack preparation is an open feasibility item to confirm.

## Setting

One participant at a time on the researcher's computer, using the assigned local session. No public deployment or remote self-service upload. Close unrelated windows and other participant sessions. Codes such as P01 are pseudonymous identifiers, not authentication or anonymity guarantees.

Navigation, review saving and completed-session restoration read prepared local state without OpenAI requests. The researcher must resolve a stale/missing cache before the session rather than generating while the participant is using the brief.

## Session schedule

| Stage | Minutes | Procedure and record |
| --- | --- | --- |
| Welcome and consent recheck | 5 | Confirm previously issued information/consent, questions, right to stop and permission choices. No new files accepted before consent. |
| Pre-test questions and independent written account | 6 | Ask the three background prompts; participant writes current understanding before seeing tutorial or brief. Keep this separate and do not rewrite it afterwards. |
| Echo Field tutorial and readiness | 4 | Use the existing one-section tutorial. Check review controls and assigned readiness; tutorial actions are excluded from formal data. |
| Assigned-project six-section review | 11–16 | Observe sequential review, sources opened, Confirm / Update / Reject and optional post-completion revisions. Record elapsed time, breaks and help. |
| Short ratings | 3 | Seven exploratory seven-point items, including N/A/cannot judge. |
| Semi-structured interview | 10–15 | Use five core questions with optional probes relevant to what happened. |
| Close | 1 | Reconfirm withdrawal/contact information and next steps; thank the participant. |
| **Total supervised session** | **40–50** | Preparation beforehand is separate. Do not rush or compel completion to achieve this estimate. |

The interface's earlier 10–15 minute estimate refers only to review activity, not the complete study. If the participant pauses, skips or cannot finish, record actual time and incomplete sections. Do not pressure them to finish six saved reviews.

## Task administration

Use the [existing question/observation guide](post_test_questionnaire_and_interview.md) for all pre-test prompts, tasks, ratings, interview questions and observation fields. Do not create a separate competing questionnaire.

The participant first writes an independent account of the project's aim/direction, important changes, unresolved issues and intended next step, marking uncertainty. This is a baseline account of their understanding, not an objective answer key.

Then use the existing six sections in order:

1. Current intention.
2. What changed and why.
3. Current versus superseded directions.
4. Relevant feedback.
5. Unresolved tensions.
6. Possible next action.

Ask participants to inspect sources when useful and choose the response they consider appropriate:

| Research term | Existing interface wording | Saved action |
| --- | --- | --- |
| Confirm | Looks accurate | confirm |
| Update | I want to update it | correct |
| Reject | This is not supported | reject |

An update requires correction text in the existing interface. A reason/note is useful but can be omitted; do not coerce disclosure. Do not tell participants which section is known to fail, require an update/rejection, or mark every confirmation as proof of accuracy. Evidence absence may be an accurate representation of this pack; ask about its meaning without claiming the real project has no such evidence.

After all six have saved responses, named shortcuts allow direct revision. Previous/Next and Back to completion summary work in post-completion editing; unsaved changes remain protected. Revisions are optional. Do not force navigation tests or introduce new code.

## Researcher conduct and exceptions

Allow quiet review or light think-aloud; continuous speech is not required. Record neutral assistance using the guide. Never defend a summary, supply the intended project state or pre-announce P96 findings.

If an error prevents progress, stop the timer for active review, record the problem without private screenshots, and ask whether the participant wishes to continue. One local restart may be appropriate if the existing prepared state is intact; do not clear reviews, alter sources, regenerate, or switch to another project. If still blocked, end the affected task and record it as incomplete. Preserve data under the agreed arrangements.

For withdrawal or unexpected sensitive content, stop processing and follow the agreed [data protocol](participant_owned_project_data_protocol_draft.md). Do not silently delete or overwrite records outside that procedure.

## Measurement and analysis

| Construct/data | Collection method | Interpretation limit |
| --- | --- | --- |
| Review action | Existing timestamped review events; report final saved action per section and revision events separately | Up to six sections per person are not independent participants; missing actions stay missing |
| Correction and reason | Saved text/reason when supplied; interview explanation distinguished from event data | A correction may use memory or new knowledge, not prove source support |
| Evidence expansion | Manual observation by section: opened/not opened/not observable; event tally and prompted/spontaneous label | No automatic telemetry; opening is not proof of reading, comprehension or trust |
| Completion time | Manual timestamps/stopwatch: start assigned review to completion summary or stopping point; breaks, technical delays and assistance logged | Report wall-clock and active time separately; tutorial and full-session time are separate |
| Clarity, control, help and effort | Seven-point item responses, N/A retained | Exploratory items, not a validated scale or an accuracy score |
| Historical state, absence and misleading risks | Written baseline plus interview/observation notes | Participant recollection and researcher interpretation can both be uncertain |

Use descriptive statistics: per-participant final action counts, number of revisions, section coverage, observed openings, individual ratings with median/range, and actual times. Show denominators and missing values. Do not combine all ratings into a total score or treat 18 section decisions as 18 participants. Do not calculate inferential significance.

Use thematic analysis of correction reasons and notes: familiarise with each case, code examples around sources/absence, correction/control, re-entry, checking effort and misleading historical attribution; revise codes from the data; compare cases, retain negative cases and document interpretation decisions. These starting concepts are not predetermined findings. Optional quotations must be accurately recorded, permitted and screened for identification.

Compare the participant's initial account with their later explanation to explore what changed and why, not to compute a causal improvement score. This design has no control condition or objective ground-truth benchmark. Self-selected packs, researcher categorisation, baseline priming, assistance and three cases limit transferability.

## After each authorised session

Check the participant's saved records without regenerating. Keep signed consent separately; store coded notes privately; distinguish observation from inference and mark missing entries. Close the server before another participant. Do not overwrite prior data or put completed templates into Git. No recordings, participant screenshots or raw material are published.

The [P00 summary](pilot_p00_summary.md) remains an unchanged historical pilot record. The [earlier demo-only procedure](participant_test_protocol.md) is retained for provenance and must not be administered as the Round 1 script.
