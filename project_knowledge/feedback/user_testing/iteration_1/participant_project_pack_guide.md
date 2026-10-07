# Participant project-pack guide

Status: preparation guidance for the proposed participant-owned-project study, 7 October 2026. Read with the [data protocol draft](participant_owned_project_data_protocol_draft.md). This guide does not establish ethics approval.

## Choosing a project

Use a creative project that the participant actually worked on and has paused for at least one to two weeks. Record the approximate interruption and the participant's involvement in private study notes. Echo Field is a short tutorial only; it is not the formal project-re-entry task.

Aim for **4–10 existing documents**, where available. Supported formats are UTF-8 `.md`, `.txt` and text-based `.pdf`. Materials can include a brief, notes, a process log, decisions, feedback and goals. Scanned PDFs need text extraction outside this prototype; OCR is not provided.

The pack need not be complete. Missing, ambiguous or inconsistent records are part of the research situation. Do not ask participants to fabricate a complete archive or manufacture answers for the six sections.

## Before providing materials

- Remove names, contact details and unnecessary identifying information, including in filenames and PDF text.
- Do not provide client-confidential material, commercial secrets, restricted third-party content or material the participant is not authorised to share.
- Participants may remove sensitive portions or withhold documents before submission.
- Materials are for this research project only. Explain that selected evidence excerpts will be sent to the OpenAI API during researcher preparation before accepting a pack.
- Use the agreed Information Sheet and Consent Form after they have been updated and confirmed for this workflow. Do not treat the earlier demo-only forms as covering participant-owned materials.

## Researcher organisation

Keep each pack under `data/study_projects/<participant-code>/` and configure it in the ignored local assignment JSON. Never place participant content in the demonstration archive, public templates or repository documentation.

| Folder | Typical existing material |
| --- | --- |
| `current_state/` | Current goals, brief or next-step notes |
| `decisions/` | Decisions and their reasons, including replaced directions |
| `feedback/` | Feedback the participant is authorised to share |
| `process/` | Process logs, experiments and dated working notes |

Preserve original wording and dates where possible. Record any redaction, renaming or researcher categorisation in private preparation notes. **Categorisation affects retrieval filtering and is a research limitation**: researcher organisation may influence which evidence and summaries a participant sees. Do not silently rewrite the participant's account to fit the prototype.

No category is mandatory. One non-empty supported document is the technical minimum; it is not a claim of adequate research material. Validate the pack, inspect readiness, and prepare all six summaries before the session. Empty-evidence sections may legitimately report insufficient evidence.

## Session preparation

1. Confirm the proposed data workflow and any required ethics amendment with the supervisor.
2. Agree the participant's pack and record preparation actions privately.
3. Run `validate --participant <code>`; check filenames, categories and extraction failures without publishing document text.
4. With `OPENAI_API_KEY` available in the launching environment, run `prepare --tutorial` and `prepare --participant <code>`. Reused valid caches do not make new API requests.
5. Run `serve --participant <code>` for the assigned local session. The server receives no API key and accepts only its bound participant code.
6. Rehearse tutorial, readiness, review, save and reopen. Keep QA codes and records outside the formal sample; P00 remains excluded.
