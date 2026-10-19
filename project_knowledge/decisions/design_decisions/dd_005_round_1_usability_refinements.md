---
project: ProjectOS
document_type: design_decision
decision_id: DD-005
date: 2026-10-19
status: implemented_not_yet_participant_evaluated
---

# DD-005: Round 1 findings to Iteration 2 interaction changes

The approved implementation brief identifies several interpretation problems in the first research round. This record captures their design implications without reproducing quotes, project content, participant-level counts or private research records. It is not a new analysis of the underlying data.

| Interpretation problem in the brief | Interface response | What remains to evaluate |
| --- | --- | --- |
| Abstract terminology makes the current/older-direction distinction difficult to understand. | Section 3 uses “Current direction and replaced ideas” and a plain-language question about what is current and what has been replaced. | Whether users can explain the section without researcher assistance. |
| Absent relevant records can lead to inconsistent use of Confirm and Reject. | A separate Not applicable response records absence or non-applicability and counts as reviewed. | Whether users distinguish this from accepting or rejecting a reconstruction. |
| Sources being visible does not ensure that users know when to inspect them. | Short guidance suggests checking surprising, outdated or incomplete summaries without requiring every record to be opened. | When checking helps and whether the burden is proportionate. |
| A next-action label can imply advice beyond the source material. | “Documented next step” explains the boundary between a recorded action and the user's own Update. | Whether the boundary is clear without implying improved actionability. |
| Independent use may require clearer instruction. | The concise Echo Field tutorial explains four choices, provisional summaries, evidence absence and separation of updates from evidence. | Comprehension, assistance and tutorial duration. |

The six internal section identities, retrieval and summary behaviour remain unchanged. No recommendation mode is introduced. Source absence is a legitimate result, not proof that the real project lacks a relevant event or decision.

Keep Round 1 records and frozen ratings intact. Compare interaction versions explicitly; do not reinterpret historical responses using the new action. Existing results-integrated report drafts remain working documents until later evaluation and comparative analysis are available.

See [TD-004](../technical_decisions/td_004_iteration_2_review_semantics.md) for persistence/cache decisions and the [validation report](../../../outputs/test_results/iteration_2_usability_validation.md) for engineering evidence. No new recruitment or data collection is reported here.
