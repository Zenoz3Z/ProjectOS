---
project: ProjectOS
document_type: technical_decision
decision_id: TD-004
date: 2026-10-19
status: implemented_for_researcher_review
---

# TD-004: Clarify review choices without changing reconstruction

## Rationale

The approved post-Round-1 refinement addresses interpretation and review controls. Clearer section language and a distinct way to record non-applicability can make a provisional reconstruction easier to assess. This is an interaction hypothesis, not a demonstrated improvement in reconstruction accuracy. The [findings-to-design record](../design_decisions/dd_005_round_1_usability_refinements.md) summarises the rationale without reproducing participant records.

## Implementation

Participant titles and explanatory questions live in `participant_flow.py`. The section IDs, backend definitions and retrieval questions remain unchanged. The sidebar, section page and completion shortcuts use the same participant titles. Section 6 explicitly distinguishes a recorded next step from a recommendation; an Update is the user's interpretation.

The version-1 review event format accepts the additional `not_applicable` action. It represents absent relevant records or a section that does not apply, rather than confirmation or rejection. Latest-state reconstruction, saved form values, progress and completion recognise it. Completion shows a separate count. Unknown actions remain invalid, and Update still requires correction text.

Review history stays append-only. Replacing an Update with Not applicable removes the older correction from the active display, as other non-correction responses do, but preserves the earlier event. Original evidence and prepared summaries are not rewritten. Existing Confirm, Correct, Reject and evidence-annotation events load without migration.

The first review and completed-section navigation retain their existing behaviour. Saved responses unlock completion; unsaved edits still require saving or explicit discard before section navigation. Tutorial choices remain practice only.

## Cache and scope boundary

No changes were made to the loader, chunker, retriever, backend brief definitions, summary generator or cache implementation. This preserves the existing pipeline and prompt fingerprints. Participant display wording does not enter summary inputs or cache keys. Existing prepared summaries may therefore retain older wording in their text; the interface does not silently rewrite them.

Not applicable is derived in the review layer after cached sections are loaded. The legacy `ReviewStatus` type annotation in `reentry_brief.py` still lists the original states; it is not a runtime validator. It was left untouched because the cache fingerprints that entire module. A future typing/cache maintenance change should address that coupling explicitly rather than invalidate participant caches in a usability refinement.

The [TD-003 retrieval freeze](td_003_freeze_automatic_project_state_inference.md) remains in force. This change adds no temporal reasoning, recommendations, upload flow or participant instrumentation. R1–R7 wording, study procedure and participant records are unchanged.

## Validation and research interpretation

The [validation report](../../../outputs/test_results/iteration_2_usability_validation.md) records automated checks and an isolated browser rehearsal. These establish implementation behaviour only. Tutorial duration, comprehension and verification effort still need participant evaluation. Evidence opening remains optional and manually observed, not proof of verification.

Record the interface version when analysing review actions. The new action changes the available response set, so frequencies from the earlier three-choice interface must not be pooled or retrospectively relabelled without an explicit analytical account.
