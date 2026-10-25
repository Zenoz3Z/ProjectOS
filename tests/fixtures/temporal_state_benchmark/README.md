# Temporal-state retrieval benchmark: frozen gold

Version: **phase_1_gold_v1**. Status: **researcher_confirmed**. This is an independent post-study technical extension, not new participant evidence or an approved production capability.

See the [protocol](../../../project_knowledge/process/experiments/temporal_state_retrieval/experiment_protocol.md), [schema](benchmark.schema.json), [public annotations](public_benchmark.json) and [freeze manifest](freeze_manifest.json). All 34 cases were confirmed by Fuzhe Zhang on 25 October 2026 following manual review of case summaries, evidence roles, applicability, temporal scope and ambiguity notes. The assistant prepared the annotations; no independent expert annotation or inter-rater agreement is claimed. No algorithm has run.

## Primary and secondary tiers

The complete frozen set has **18 production cases and 16 diagnostic cases**. Each of three projects contributes exactly six production/latest-state cases. Public annotations contain 8 Echo Field and 15 Signal Loom cases; 11 researcher-owned cases remain private.

Six canonical cases were added so narrower diagnostics and historical snapshots need not be misrepresented as primary tasks. Twelve old cases now use canonical wording; sixteen retain their diagnostic questions. This yields 34 cases, not a pooled 34-case performance population. case_origin and candidate_v2_question record the migration.

Primary labels contain 15 supported and 3 insufficient; applicability is 11 applicable, 3 not_applicable, 4 unclear. Primary combinations are 11 supported/applicable, 3 supported/not_applicable, 1 supported/unclear and 3 insufficient/unclear. Diagnostic labels are unchanged: 14 supported and 2 insufficient; applicability is 11 applicable, 2 not_applicable, 3 unclear. These are separate gold distributions, not measurements.

## Exact production questions

The following strings come from the unchanged [brief schema](../../../src/brief_schema.py). Production case question fields must match them exactly.

| section_id | Canonical question |
| --- | --- |
| current_intention | What is the current aim or intended direction of this project? |
| changes_and_reasons | What important changes were made to the project, and why were they made? |
| current_vs_superseded | Which project directions are current, and which directions have been replaced or superseded? |
| relevant_feedback | What tutor or user feedback is relevant to the current project direction? |
| unresolved_tensions | What unresolved questions, tensions or limitations remain in the project? |
| possible_next_action | What is the next documented action or decision that should be addressed? |

The existing production implementation internally uses configured section-query pairs. A later baseline must preserve and disclose that mechanism; it cannot substitute an easier diagnostic question. Diagnostic questions are explanatory probes, not primary performance evidence.

## Reference time and eligible corpus

Every case requires benchmark_tier, reference_state, as_of_record and eligible_record_ids. record_catalog maps stable IDs to source paths, sequence, explicit dates where available and hashes. Metadata lives in annotations; the seven synthetic records were not edited.

- Echo Field latest: EF-R04, its undated explicit Current State record; all EF-R01–EF-R04 remain eligible.
- Private researcher latest: an undated final-state overview anchors the full permitted archive. Latest supplied state is not proof of present-day activity or document authoring chronology.
- Signal Loom historical: SY-R05, 12 February 2026; only SY-R01–SY-R05. The undated fragment SY-R06 and later closure SY-R07 are excluded.
- Signal Loom latest: SY-R07, 20 February 2026; all seven records. The fragment remains undated and its diagnostic is assessed only in this latest view.

Undated sequences are explicit manifest conventions, not fabricated calendar dates. All temporal labels are relative to the stated anchor. Primary cases all use latest_project_state; historical cases are diagnostic only. No date is inferred from filesystem metadata.

## Evidence and applicability boundaries

Support, section_applicability, temporal_status and evidence_role are independent. Missing feedback files mean insufficient/unclear, not proof of no feedback. Explicit no-feedback or no-next-task records can support not_applicable with a scoped closure_or_inapplicability role. Completion alone is insufficient to label every section inapplicable. future_conditional is never next_action.

The named drift-resolution diagnostic does not automatically establish that every limitation is absent under canonical Signal Loom S5. Likewise, a final artefact's purpose and a dated task list do not prove an ongoing intention or pending next action. The researcher confirmed broad Signal Loom S5 as insufficient/unclear. P96 canonical S1 is supported/unclear: its explicit final purpose supports aim or intended direction, while present applicability and ongoing temporal status remain unknown. Conditional possibilities are excluded. Its retrospective purpose and task-list diagnostics remain separate.

Gold and applicability sets preserve alternative complete assertions and required context. Locators are Unicode offsets with universal LF newlines, zero-based/end-exclusive; line numbers are one-based. Source hashes use raw bytes. Duplicate passages do not create additional roles.

Primary reporting includes Hit@1, Hit@3, MRR, required-role and pair coverage, temporal mismatch, false-current exposure, insufficient evidence-boundary reporting, applicability coverage, closure recognition and latency. Final abstention/classification accuracy is not inferred from retrieval alone. Secondary metrics are failure-analysis material and must never be pooled with primary performance.

The [synthetic archive](../temporal_state_project/README.md), [Echo Field archive](../../../data/demo_projects/sample_echo_field/) and [original regression fixture](../../evaluation_queries.json) remain source inputs/reference evidence, not editable targets for class balance. No source change, model output, summary, participant response or production-schema change is included.

## Freeze and change control

The researcher accepted the undated current-state/final-overview anchors as latest supplied states, without proving creation dates or complete authoring chronology. No calendar date was invented and no original source was changed.

All cases carry researcher_confirmed, reviewed_by, review_date and review_basis. The source-located private purpose gold was narrowed without changing other diagnostic labels. Confirmed uncertainty remains uncertainty; it is not an assertion of active development.

The public manifest records raw SHA-256 hashes for the twelve other public files, plus its own canonical-JSON digest with the self-digest value omitted. The private manifest records the public manifest's raw-byte hash and private package hashes. A public digest commitment identifies the private labels without exposing their content or private path.

Do not modify phase_1_gold_v1 after observing baseline results. Any necessary correction must be a new version with a full reason, preserved predecessor information and renewed prospective review. No silent relabelling or outcome-driven case removal is permitted.
