---
project: ProjectOS
document_type: participant_owned_data_protocol
date: 2026-10-08
status: draft_for_supervisor_review_existing_ethics_approval_unchanged
---

# Participant-owned project data protocol

**Status:** Draft for supervisor review — existing ethics approval unchanged; data-storage wording updated following supervisor feedback on 9 October 2026.

Supervisor confirmation received on 9 October 2026: no amendment to the existing ethics approval is required. Participant-facing documents must clearly state what data will be stored, where it will be stored, and for how long. This is a preparation plan under the existing approval, not a new ethics approval or a completed consent record. Formal recruitment and P01 have not started; the wording is for Meeting 3 review on 15 October 2026 at 15:00 (Europe/London).

The [Round 1 protocol](study_protocol_round_1_draft.md) is the canonical procedure. The [information sheet](participant_information_sheet.md) and [consent form](participant_consent_form.md) describe the unchanged own-project workflow and the storage schedule below; they remain drafts for wording review.

## Data flow and consent order

1. After the start gate, invite three adults with one paused long-term creative project each. Issue final information and obtain consent before receiving 4–8 self-selected, screened, non-sensitive files.
2. Use the agreed private transfer route. The researcher and participant check rights, unnecessary identifiers, sensitive text, filenames and metadata. If material cannot be made suitable, stop; do not send it to the API.
3. Import using researcher assistance. Assign a pseudonymous code such as P01 and a separate project context. Store code/contact linkage separately. Content can remain identifying even without a name.
4. Extract text, chunk and retrieve locally. Record researcher categorisation, redaction and exclusions privately; preserve source wording and dated context.
5. Prepare summaries by sending selected evidence text and source references to the OpenAI API with the section prompt. The existing code includes source filenames/relative paths and excerpt identifiers. Corrections, reasons and interview records are not inputs to this preparation.
6. Store summaries and retrieved excerpts in the project's private local cache. Keep materials and preparation version fixed within a session. A stale cache is a preparation problem, not permission to regenerate during testing.
7. Collect the independent pre-test account, then run a short Echo Field tutorial and six-section review on the researcher's computer. The participant can Confirm, Update or Reject; tutorial responses do not enter formal review statistics.
8. Save review events locally. Record evidence openings, time, [ratings (Round 1 v1)](round_1_templates/post_test_ratings_template.md) and interviews manually. Use no audio/video/screen recording or participant screenshots in this draft procedure.

Provider handling is disclosed in the information sheet's [external AI service section](participant_information_sheet.md#external-ai-service-handling), with an official source checked on 8 October 2026. Inspect the actual study account and model settings before use. Do not claim that local testing means offline preparation, that `store=False` enables zero retention, or that a regional processing arrangement is already in place.

## Storage and deletion schedule — for wording review

Use restricted UAL OneDrive for retained study records. Use the researcher's password-protected computer only where necessary for preparation or the supervised session. The existing local folders below are temporary operational locations, not an additional long-term store. Check folder permissions, transfer and backup-copy deletion before issue of the final participant documents.

| Record | Storage and operational handling | Retention and deletion |
| --- | --- | --- |
| Participant-selected source files, extracted text and temporary working copies | Restricted UAL OneDrive; only necessary preparation/session copies on the password-protected computer, including `data/study_projects/` | Permanently delete within 7 calendar days after the session |
| Assignment and temporary identity-to-participant-code mapping | Mapping in restricted UAL OneDrive, separately from research records and signed forms; local `data/study_config/` is temporary operational configuration | Delete mapping after the 7-day withdrawal period; remove identifying temporary local configuration within the same source-copy deletion schedule |
| AI-generated summaries and displayed source excerpts | De-identify and retain in restricted UAL OneDrive; necessary local preparation/session copies in `data/summary_cache/` are temporary | Retain de-identified records until 30 November 2027, then permanently delete; remove temporary local copies within 7 calendar days after the session |
| Review choices, corrections and reasons | De-identified research records in restricted UAL OneDrive; local `data/reviews/` and review JSON stay private and temporary | Retain de-identified records until 30 November 2027, then permanently delete; remove temporary local copies within 7 calendar days after the session |
| Written pre-test account, ratings, interview notes, observation notes and timings | De-identified research records in restricted UAL OneDrive, separate from consent | Retain until 30 November 2027 and then permanently delete |
| Signed consent forms | Restricted UAL OneDrive, separately from research records | Retain until 30 November 2027 and then permanently delete |
| Backups and transfer copies | Apply the relevant record category's schedule to every copy under the researcher's control | Include permanent deletion of working/transfer/backup copies; verify the manual procedure |
| Text sent to the OpenAI API | OpenAI is an external service; names and contact details will not deliberately be sent | Abuse-monitoring logs may be retained for up to 30 days; provider-side limits remain as disclosed in the information sheet |

Use the same schedule and withdrawal wording in all issued copies. These specified dates and locations are included for Meeting 3 wording review following the supervisor feedback, not presented as a newly issued ethics approval or an invented institutional retention rule. De-identification must address indirect identifiers in source excerpts and free text; a participant code alone is not sufficient.

Participant-owned source files, signed forms, identity mappings, review JSON and raw interview notes must never enter GitHub. Raw packs, caches, review histories and participant screenshots also remain excluded from public documentation. No audio, video or photographs will be recorded; no screen recording or participant screenshots are planned. Existing ignore rules are a publication safeguard, not encryption or anonymisation. No self-service upload, public hosting or user account system is introduced.

The server is local and bound to one participant context. Codes are not passwords; this does not protect files from someone with access to the researcher's operating-system account. Run one supervised session at a time and close it before opening another participant's context.

## Withdrawal, deletion and inadvertent disclosure

Before consent, provide the contact route and the session-specific calendar date for the seven-day withdrawal deadline. Identifiable data may be withdrawn within 7 calendar days after the session. Participants may stop or skip without penalty. Keep the identity link available through that period; delete it afterwards. After deletion of the identity link and aggregation, withdrawal may no longer be possible. Do not treat a code alone as anonymity.

For an eligible request, stop further processing, identify all covered pack/cache/review/notes/export/backup copies, apply the agreed deletion procedure and record completion without retaining withdrawn content. Explain any separate consent-record retention and provider-side limitations. The software has no automatic study-wide deletion feature, and this document does not perform deletion.

The schedule governs future formal sessions. This documentation update does not delete or move P00/P96 records, prepare participant records, create storage folders or change application behaviour.

If unexpected sensitive content is found, stop preparation or the session, prevent further API transmission, record only the minimum incident information privately and seek the agreed supervisor/institutional response. Do not quietly redact and continue processing without resolving scope and consent.

## Research boundaries

P00 is a pilot and P96 a researcher self-test, neither part of the formal sample. P96 review statistics are not study findings. Formal P01 has not started.

Automatic project-state inference extensions are frozen by [TD-003](../../../decisions/technical_decisions/td_003_freeze_automatic_project_state_inference.md). Source visibility, evidence absence and correction are the research focus; no temporal inference or production changes are proposed here. The [gap check](study_materials_gap_check_round_1.md) lists the remaining release decisions.

## Researcher consent checks — blank checklist

This checklist is kept in the researcher protocol, separately from the participant-facing consent form. It does not record completed approval or consent.

- [ ] Approval/scope record checked; no unresolved information-sheet fields.
- [ ] Consent received before materials or API processing.
- [ ] Participant received a copy and contact/withdrawal details.
- [ ] Signed form stored separately from coded responses in approved private storage.
- [ ] Consent reconfirmed at the supervised session.

Keep signed forms and code/contact linkage out of Git. Do not use P00 or P96 records as consent or results for a formal participant.
