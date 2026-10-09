# Round 1 data collection and initial analysis templates

Status: **Draft — pending Anna/supervisor and ethics confirmation.** These are blank public masters that can be versioned on GitHub. Creating them does not authorise recruitment, project import or data collection.

## Privacy and use

Do not save real participant answers, project files, signed forms, names, emails, contact details or identifying project titles in this directory. Never fill in these public masters. First copy the required templates, including the CSV, to a Git-ignored private research directory and verify that the copies are ignored.

Use anonymous participant codes such as P01 or P02 and a non-identifying project pseudonym in research records. Codes alone do not guarantee anonymity: screen free text for identifiers and identifying combinations of details. Any consent/contact mapping must remain separate from coded answers and materials. Store signed Consent Forms separately from research answers and project materials.

The approved storage location, access arrangements, retention periods for each data type, withdrawal deadline and deletion procedure remain **pending Anna/ethics confirmation**. Do not invent dates or approval. Follow the draft [participant data protocol](../participant_owned_project_data_protocol_draft.md) and [Round 1 protocol](../study_protocol_round_1_draft.md); resolve outstanding arrangements before recruitment or collecting materials.

P96 is a researcher self-test and is excluded from the formal participant sample and cross-participant analysis. No P96 source material, saved reviews or results belong in these templates. The OpenAI request option `store=False` must not be described as zero data retention; it does not settle all provider processing or retention arrangements.

## Template sequence and purpose

| Template | Use |
| --- | --- |
| [Session record](participant_session_record_template.md) | Coded session context, document versions, timing, assistance and deviations. |
| [Pre-test project state](pre_test_project_state_template.md) | An independent written account before both the Echo Field tutorial and formal ProjectOS review; mapping is researcher-only after the session. |
| [Section review observation](section_review_observation_template.md) | Neutral manual observations for the six formal sections, kept separate from saved review events. |
| [Post-test ratings](post_test_ratings_template.md) | Seven custom exploratory items and three short optional reflections. |
| [Interview notes](interview_notes_template.md) | Five main questions, optional neutral probes and clearly separated notes/quotations. |
| [Initial codebook](analysis_codebook_v0.md) | Thirteen provisional deductive codes and blank analytic memos. |
| [Cross-participant matrix](cross_participant_matrix_template.csv) | One row per formal participant in a private copy, after authorised collection. The public file contains only a header and a placeholder. |

For participant-facing use, prepare only the participant portion of the pre-test sheet. Do not display its six-section researcher mapping before the formal task. Leave public templates blank; an unchecked consent field is not consent.

## Instrument version and interpretation

The sole formal Round 1 post-test ratings instrument is [ProjectOS Round 1 Post-test Ratings — Round 1 v1](post_test_ratings_template.md): R1-R7, wording frozen on **2026-10-08**, status **Draft pending supervisor/ethics confirmation**. Use that file as the authoritative wording; do not rewrite items in other forms.

The [question and observation guide](../post_test_questionnaire_and_interview.md) directs formal scoring to R1-R7 and retains L1-L7 explicitly as a historical draft. These instruments are not interchangeable. Do not administer L1-L7 for formal Round 1, pool L and R responses, convert scores between them or relabel historical responses as new data. The P00 record does not establish that L1-L7 was used in that pilot; no such use is inferred here.

This audit selects the formal ratings version without changing the open pre-test prompt, interview templates or session procedure. Supervisor/ethics confirmation is still required before formal use. Selection and wording freeze do not imply approval.

The protocol's three adults, 40-50 minute session and research question remain unchanged. Its approval gates still apply. These templates are preparation materials, not findings.

- Participant-assessed alignment represents the participant's understanding at that time. It is not objective accuracy or ground truth.
- Evidence opening is **researcher observation**, not a complete system interaction log. An observed opening does not establish reading, understanding or trust.
- The seven-point ratings are **custom exploratory items**, not a validated psychometric scale. Report individual responses descriptively with qualitative findings; do not claim statistical significance.
- R6 measures verification burden in the negative direction: a higher score means more effort than expected. Keep it separate; do not silently add it to positive items or create an overall score.
- Saved ProjectOS actions/corrections are the authoritative review records. Confirm does not prove correctness, and Update does not automatically mean system failure. Tutorial reviews are excluded.

## Matrix definitions

Copy the CSV to the private, ignored research area **before** entering any real data. The public row uses `participant_code=PXX` and `row_type=example_placeholder_not_data`; every outcome field is blank. Exclude that placeholder from analysis. In an authorised private copy, use one row per formal participant and a documented `row_type` such as `formal_participant`. No participants have been created by this template.

| Columns | Recording rule |
| --- | --- |
| `participant_code`, `row_type` | Coded identifier and explicit row purpose; never a name or contact identifier. |
| `project_type`, `file_count`, `pause_length` | Broad practice type, number of supplied files, and approximate pause with unit in this text field. Do not include actual titles or filenames. |
| `reviewed_sections` | Number of the six formal sections with a saved review at the recorded session endpoint; not event count. |
| `confirm_count`, `update_count`, `reject_count` | Count the latest saved action for each reviewed section at that same endpoint. ProjectOS `correct` maps to Update. Counts sum to `reviewed_sections`; revisions are retained separately in saved events, not added as extra sections. |
| `observed_evidence_open_count` | Number of distinct formal sections with an evidence opening observed (0-6), not all clicks or repeat openings. Derive only when all section observations are determinate; otherwise leave blank and preserve partial Yes/No/Uncertain notes. |
| `task_duration_minutes` | Active formal review time from assigned-review start to first completion summary or stopping point, excluding tutorial, breaks and technical delays. Keep wall-clock time, exclusions, incomplete status and optional later revisions in the private session record. |
| `clarity_rating` | R1, clarity. |
| `alignment_rating` | R2, participant-assessed alignment. |
| `source_visibility_rating` | R3, source visibility. |
| `correction_control_rating` | R4, correction and control. |
| `reentry_helpfulness_rating` | R5, project re-entry. |
| `verification_burden_rating` | R6, negative-direction verification burden. |
| `evidence_absence_clarity_rating` | R7, evidence absence clarity. |
| `main_theme_1`, `main_theme_2` | Provisional, case-supported analytic summaries after coding; leave blank until supported. These two slots do not limit themes kept in private analysis notes. |
| `critical_incident`, `iteration_implication` | De-identified incident summary and tentative implication linked to private evidence. Do not paste project source text or identifying quotations into the matrix. |

Numeric fields stay blank for missing or unavailable data. Record the reason (for example not answered, N/A, not observable or incomplete timing) in the associated private form. Do not substitute zero or a neutral rating. A real observed zero is valid only when coverage is complete. Retain revision history and observation uncertainty instead of silently flattening them into counts. With three planned cases, show denominators and negative or inconsistent cases alongside descriptive summaries.
