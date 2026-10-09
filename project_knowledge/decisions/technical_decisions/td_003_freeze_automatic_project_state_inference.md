---
project: ProjectOS
document_type: technical_decision
decision_id: TD-003
date: 2026-10-08
status: accepted_for_scope_freeze
---

# TD-003: Freeze automatic project-state inference expansion

## Decision

Freeze automatic retrieval expansion at the stable participant-review prototype. Do not introduce further query expansion, role-based selection, heading-aware chunking, hybrid ranking or automatic temporal reasoning before the first user research round. The existing retrieval and provisional summary workflow remains available; this decision does not remove it or certify its interpretations as accurate.

The research focus is now:

> How do source visibility and user correction help creative practitioners assess an AI-generated reconstruction of a long-term project during project re-entry?

Round 1 will examine source visibility, evidence absence, user correction and the effort of checking an interpretation. It will not test a claim that the system can automatically determine a project's true current state.

## Evidence and rationale

The P96 researcher self-test exposed a distinction between semantic relevance and project-state accuracy. Related passages can be historical, resolved, conditional or incorrectly attributed. A passage can be useful without supporting the particular claim that a summary makes about the present.

Query expansion and role-based evidence selection passed engineering tests but did not pass P96 semantic acceptance. Subsequent private structural comparisons found local improvements from heading-aware, lexical and hybrid methods, but no consistent improvement across the problem sections sufficient to establish reliable reconstruction. Some valid evidence was recovered; this is not a claim that those methods never help.

P96 is a researcher self-test, excluded from the formal participant sample. Its review counts and automated checks are not user-study findings. This public decision contains no source passages, chunk identifiers, participant records or private diagnostics. The failed experiment remains a recoverable local research record rather than a production upgrade.

Automatically deciding whether a record is still current would require interpreting later decisions, unresolved status, conditional plans and missing context. Developing and validating that capability exceeds the present MSc project's scope. Engineering correctness alone cannot resolve this research question.

## Consequences for the study

- Preserve the stable six-section workflow, visible sources and Confirm / Update / Reject interaction.
- Present generated summaries as provisional; semantic similarity is not factual confidence.
- Treat missing evidence as a legitimate outcome, not a reason to manufacture feedback or fill gaps with guesses.
- Study when participants consult sources, challenge historical or unsupported interpretations, and express their own understanding.
- Keep corrections separate from original evidence. Participant agreement is not an independent accuracy label.
- Freeze source packs and prepared summaries within a session; record researcher assistance and preparation choices.

Temporal metadata remains possible future work after user testing. A later explicit interface could show a documented date or invite a user to mark a record's status, including uncertainty. This is a possible design direction, not an implemented feature or automatic temporal judgment.

## Scope and review point

Non-goals are automatic temporal reasoning, automatic contradiction detection, self-service upload, public deployment, user accounts and perfect reconstruction accuracy.

Current study status, updated following 9 October 2026 feedback: Anna confirmed that no amendment to the existing ethics approval is required. The [Round 1 protocol](../../feedback/user_testing/iteration_1/study_protocol_round_1_draft.md) and participant data-storage wording remain drafts for Meeting 3 wording review. No recruitment or collection of project packs is authorised by this technical decision. Reconsider the freeze after the first agreed research round, using observed checking and correction needs rather than another isolated ranking gain.

See [current goals](../../current_state/goals.md), [open blockers](../../current_state/blockers.md) and the [materials gap check](../../feedback/user_testing/iteration_1/study_materials_gap_check_round_1.md).
