# Participant-owned project data protocol

**DRAFT — REQUIRES SUPERVISOR / ETHICS CONFIRMATION BEFORE FORMAL USE**

Date: 7 October 2026

This draft proposes a change from reviewing an unfamiliar demonstration archive to returning to a participant's own interrupted creative project. The repository does not establish that existing documents or any earlier approval cover this change. Do not use this draft as a completed consent instrument.

## Proposed data flow

1. The participant selects a creative project they genuinely worked on and paused for at least one to two weeks. They provide only non-sensitive materials they are authorised to share and may remove sensitive content before submission.
2. The researcher checks the pack locally, removes unnecessary identifiers with the participant's agreement, and organises files into four categories. Keep a private record of these preparation decisions.
3. A local assignment maps an anonymous participant code to a project directory and project ID. Code-based records are not a guarantee of full anonymity: project content can itself identify a person. Any identity/code list must be stored separately under the agreed study arrangements.
4. Document extraction, chunking and semantic retrieval run locally. **Relevant evidence excerpts retrieved from the participant's files are sent to the OpenAI API** during researcher preparation to generate summaries. This must be disclosed before materials are accepted and processed.
5. The researcher stores the prepared summaries and selected evidence in a private local cache. The summariser uses `store=False`; this does not establish zero provider retention. Confirm relevant provider handling and the institution's requirements before formal use.
6. The participant completes a short Echo Field tutorial, then reviews six prepared sections from the assigned project. Tutorial choices remain in the temporary browser session and are not written to formal review records.
7. Confirmation, correction, rejection and evidence annotations are saved locally under participant code and project ID. Participant corrections and notes are not sent for regeneration and do not enter the summary cache. Navigating and saving do not call the API.

## Content and access boundaries

Participants must not provide client-confidential information, commercial secrets, restricted third-party materials or content they are not authorised to share. Avoid names, contact details and unnecessary personal information in documents, filenames, display names, notes and screenshots.

Project materials, local assignments, summary caches and reviews are excluded from Git and must not be uploaded to GitHub. Ignore rules do not remove already tracked files or make content anonymous; the researcher must inspect repository changes and new outputs.

The study server listens on loopback and is bound by the researcher to one participant code. Participants cannot switch to other assigned projects or to Development mode through this study interface. This is not a login system and does not protect against someone with access to the researcher's operating-system account or local files. It is intended for one supervised local session at a time, not public hosting or concurrent multi-user use.

## Withdrawal, retention and deletion — decisions outstanding

Withdrawal and deletion arrangements must match the final Participant Information Sheet. Do not invent a withdrawal deadline, storage duration, supervisor contact or policy here.

Before formal use, agree who can access the files, where they are stored and backed up, retention periods, the withdrawal route and deadline, and how withdrawal is handled after analysis or anonymisation. Consider original packs, extracted evidence in caches, review histories, screenshots, interview/observation records and any local backups together.

For an eligible withdrawal, the researcher should identify the relevant participant/project records, stop further processing, apply the agreed deletion procedure to all covered local copies, and record completion separately without retaining withdrawn content. Provider-side handling and any limits to deletion must be explained accurately in the approved participant-facing documents. This draft does not perform deletion or promise capabilities the software does not implement.

## Required confirmation before formal use

- Ask the supervisor whether the move to participant-owned materials requires an ethics amendment and follow the applicable process.
- Update and confirm the Participant Information Sheet and Consent Form to cover the material source, local organisation, external API processing, cache/review storage and withdrawal arrangements.
- Confirm the revised test protocol, recruitment/inclusion criteria, time estimate and analysis plan. The existing demo-based protocol remains historical and is not silently replaced by this draft.
- Confirm how potentially identifying project content, third-party rights and sensitive feedback will be screened.
- Record researcher categorisation as a limitation because it influences category-filtered retrieval.
- Rehearse the complete flow with non-personal QA materials before recruiting or accepting real packs under the new protocol.

The research questions and six brief sections are unchanged. Readiness checks are technical safeguards; they do not establish ethical approval, factual summary accuracy or participant benefit.
