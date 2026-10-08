---
project: ProjectOS
document_type: participant_owned_data_protocol
date: 2026-10-08
status: draft_pending_supervisor_ethics_confirmation
---

# Participant-owned project data protocol

**DRAFT — no recruitment, material collection or processing before Anna's supervisor/ethics scope confirmation and any required institutional approval.** This is a preparation plan, not a consent instrument or approval record.

The [Round 1 protocol](study_protocol_round_1_draft.md) is the canonical procedure. The [information sheet](participant_information_sheet.md) and [consent form](participant_consent_form.md) now describe the proposed own-project workflow but remain unapproved drafts.

## Data flow and consent order

1. After the start gate, invite three adults with one paused long-term creative project each. Issue final information and obtain consent before receiving 4–8 self-selected, screened, non-sensitive files.
2. Use the agreed private transfer route. The researcher and participant check rights, unnecessary identifiers, sensitive text, filenames and metadata. If material cannot be made suitable, stop; do not send it to the API.
3. Import using researcher assistance. Assign a pseudonymous code such as P01 and a separate project context. Store code/contact linkage separately. Content can remain identifying even without a name.
4. Extract text, chunk and retrieve locally. Record researcher categorisation, redaction and exclusions privately; preserve source wording and dated context.
5. Prepare summaries by sending selected evidence text and source references to the OpenAI API with the section prompt. The existing code includes source filenames/relative paths and excerpt identifiers. Corrections, reasons and interview records are not inputs to this preparation.
6. Store summaries and retrieved excerpts in the project's private local cache. Keep materials and preparation version fixed within a session. A stale cache is a preparation problem, not permission to regenerate during testing.
7. Collect the independent pre-test account, then run a short Echo Field tutorial and six-section review on the researcher's computer. The participant can Confirm, Update or Reject; tutorial responses do not enter formal review statistics.
8. Save review events locally. Record evidence openings, time, ratings and interviews manually. Use no audio/video/screen recording or participant screenshots in this draft procedure.

Provider handling is disclosed in the information sheet's [external API section](participant_information_sheet.md#external-api-handling), with an official source checked on 8 October 2026. Inspect the actual study account and model settings before use. Do not claim that local testing means offline preparation, that `store=False` enables zero retention, or that a regional processing arrangement is already in place.

## Storage and access plan — must be confirmed

The proposed locations below describe existing separation, not approval of a storage service or device. Agree institutionally acceptable storage, device protection, access and backups before use.

| Record | Proposed handling | Unresolved decision |
| --- | --- | --- |
| Received pack and working copy | Private transfer/storage; researcher-assisted category import under `data/study_projects/` | Transfer route; access; duration/start trigger; deletion of copies |
| Assignment and code linkage | Local assignment under `data/study_config/`; identity linkage separate from content | Who can access each; retention and deletion |
| Summaries and retrieved evidence | Per-project private `data/summary_cache/` | Retention, preparation snapshot record and backups |
| Review/correction/reason history | Per-project private `data/reviews/` | Retention, analysis export and deletion |
| Baseline, observation, ratings and interview notes | Private coded research records, separate from consent | Approved location, access, retention and de-identification |
| Signed consent and contact details | Separate private storage; never a public template | Required retention and independent concerns route |
| Backups and transfer copies | Account for every copy in the agreed schedule | Expiry, deletion procedure and verification |

Use the same retention schedule and withdrawal wording in all issued copies. None of these durations has yet been agreed. Do not substitute a guessed institutional policy.

Raw packs, caches, review histories, signed forms, interviews and participant screenshots must never be uploaded to GitHub or public documentation. Existing ignore rules are a publication safeguard, not encryption or anonymisation. No self-service upload, public hosting or user account system is introduced.

The server is local and bound to one participant context. Codes are not passwords; this does not protect files from someone with access to the researcher's operating-system account. Run one supervised session at a time and close it before opening another participant's context.

## Withdrawal, deletion and inadvertent disclosure

Before consent, agree a request route, deadline, identification method, analysis/publication cut-off and expected response process. Participants may stop or skip without penalty. A coded record is still withdrawable while linkable under the agreed arrangements; do not describe it as already anonymous.

For an eligible request, stop further processing, identify all covered pack/cache/review/notes/export/backup copies, apply the agreed deletion procedure and record completion without retaining withdrawn content. Explain any separate consent-record retention and provider-side limitations. The software has no automatic study-wide deletion feature, and this document does not perform deletion.

If unexpected sensitive content is found, stop preparation or the session, prevent further API transmission, record only the minimum incident information privately and seek the agreed supervisor/institutional response. Do not quietly redact and continue processing without resolving scope and consent.

## Research boundaries

P00 is a pilot and P96 a researcher self-test, neither part of the formal sample. P96 review statistics are not study findings. Formal P01 has not started.

Automatic project-state inference extensions are frozen by [TD-003](../../../decisions/technical_decisions/td_003_freeze_automatic_project_state_inference.md). Source visibility, evidence absence and correction are the research focus; no temporal inference or production changes are proposed here. The [gap check](study_materials_gap_check_round_1.md) lists the remaining release decisions.
