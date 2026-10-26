# Phase 3A researcher review and final method audit

Status: **researcher_confirmed — locally frozen as phase_3a_metadata_v1**.

Reviewer: Fuzhe Zhang. Review date: 26 October 2026. The researcher accepted the document-function labels and authorised confirmation only after the final pool/query/interface audit passed. That condition was satisfied; no independent annotation or inter-rater agreement is claimed. Execution remains unauthorised.

The frozen package includes the [preregistration](phase_3_preregistration.md), [metadata schema](../../../../tests/fixtures/temporal_state_metadata/record_metadata.schema.json), [Echo Field metadata](../../../../tests/fixtures/temporal_state_metadata/echo_field.metadata.json), [Signal Loom metadata](../../../../tests/fixtures/temporal_state_metadata/signal_loom.metadata.json) and [freeze manifest](../../../../tests/fixtures/temporal_state_metadata/freeze_manifest.json). The seven confirmed researcher-owned records and their private manifest remain in ignored storage; this document discloses neither source text nor private paths.

## Public record review

All ordinals below are stable catalogue positions, not inferred creation times. Null dates are intentional. Source headings and statements justify document function only.

| Record | Category | Confirmed state | Date | Ordinal | Basis | Source-grounded rationale and limit |
| --- | --- | --- | --- | --- | --- | --- |
| EF-R01 | decisions | undated_record | null | 1 | explicit_heading | Design Decisions mixes initial ideas, reasons and a Current status subsection. Its status field does not make the entire narrative an explicit state snapshot. |
| EF-R02 | feedback | historical_record | null | 2 | explicit_source_statement | Context says feedback was received after a rehearsal; responses are recorded. This report function does not make the feedback irrelevant now. |
| EF-R03 | process | undated_record | null | 3 | explicit_heading | Project Log mixes initial experiments, completed changes and Unresolved questions, with ongoing status. No pure historical or snapshot scope is assumed. |
| EF-R04 | current_state | current_snapshot | null | 4 | explicit_heading | Current State explicitly supplies goals, completed work, blockers and next steps, without proving a creation date. |
| SY-R01 | process | historical_record | 2026-02-01 | 1 | explicit_heading | Concept note and Original intention document the early design; no passage is automatically declared obsolete. |
| SY-R02 | decisions | historical_record | 2026-02-05 | 2 | explicit_source_statement | Revision decision records changes and reasons as an event, not a complete latest-state overview. |
| SY-R03 | process | historical_record | 2026-02-08 | 3 | explicit_heading | Repair log describes completed repairs, which do not establish whole-project closure. |
| SY-R04 | process | historical_record | 2026-02-11 | 4 | explicit_heading | Working notes record reflection and a conditional extension, not an agreed task or external review. |
| SY-R05 | current_state | current_snapshot | 2026-02-12 | 5 | explicit_heading | Active snapshot describes that dated state. Its pending task cannot automatically remain pending in a later view. |
| SY-R06 | process | undated_record | null | 6 | explicit_source_statement | Unplaced fragment explicitly lacks date and approval. Ordinal 6 does not prove historical availability. |
| SY-R07 | current_state | closure_record | 2026-02-20 | 7 | explicit_heading | Closure record explicitly documents completion/archiving, without answering every possible remaining limitation. |

No public record currently needs the unknown state. Three are undated_record; five public record dates are null, including the undated current-state overview and retrospective feedback record. A function label and date availability are separate dimensions. Missing runtime metadata is defined as unknown, but completeness failure blocks an experiment run.

## Confirmed decisions and audit conditions

- [x] All 18 document-function labels, dates, ordinals, bases and limitations are unchanged; eleven public and seven private records are confirmed under the researcher's conditional authorisation.
- [x] Mixed records, retrospective diary function and final-overview/closure distinctions remain explicit. No record type labels a chunk as current, superseded, unresolved or next_action.
- [x] Source signatures, actual call arguments and all 24 saved request counts establish the full original per-query pool. The evaluation-only selected-first ranking is not permitted as an input channel.
- [x] Production query text supports S3's query-order rule; Query 2 also includes future work, so historical is not automatically superseded. S2/S4/S6 remain exactly baseline.
- [x] The closed runtime schema exposes only the minimal state mapping and candidate identity/score lists, rejecting complete metadata and gold/result fields at every object boundary. Future implementation must validate the actual process boundary before execution.
- [x] Phase 1 original criteria and Phase 3 improvement criteria are separately preserved. The displayed latency threshold is 44.03 ms, sourced from twice the frozen baseline production median of approximately 22.01445 ms; exact arithmetic remains in JSON.
- [x] Static method checks passed before confirmation. Public/private hashes, unchanged sources and historical exclusion were checked again after the local freeze.

The selection contract deliberately ignores dates, ordinals, free-text rationale, corpus outcome labels and project-specific exceptions. The evaluator alone may use frozen gold after output is fixed. Source annotation and target evidence annotation must remain separate. Prior knowledge of baseline results is disclosed; no blind or independent annotation is claimed.

## Freeze result and execution gate

The schema now requires phase_3a_metadata_v1, researcher_confirmed and the recorded review provenance. A predecessor checksum identifies the reviewed candidate. The public manifest is named freeze_manifest.json; the ignored private metadata retains its existing filename. Version/status fields identify the frozen contents, with no change to metadata or registered rules. The public manifest covers the public package and commits to private metadata; the private manifest references the public raw-byte hash and private record checksum.

The future results report must independently state whether Phase 3 improvement criteria and the complete original Phase 1 criteria are met. Both are currently not evaluated. Meeting the former may only be described as "met the preregistered Phase 3 improvement criteria"; it does not establish reliable state understanding or full original-benchmark success.

The frozen design is ready for publication after final validation. A committed freeze ancestor and separately authorised, tested implementation remain prerequisites for execution. No selector, candidate result, model load, API request or participant validation is part of this package. Phase 3A stops after publication of this design; Phase 3B execution is not authorised.
