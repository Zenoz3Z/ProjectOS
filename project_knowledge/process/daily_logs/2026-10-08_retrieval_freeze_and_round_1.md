# ProjectOS Daily Log — 2026-10-08

## Record status

Retrospective reconstruction from existing project evidence.

## Focus

Preserve a negative retrieval experiment and redirect the project towards source inspection and user correction.

## Work completed

- Recorded section-specific role queries, deterministic role selection and rank-fusion fallback on a separate local experiment branch.
- The engineering checks passed, but semantic acceptance did not. Preserved the experiment without promoting it into the stable study implementation.
- Compared structural and lexical/semantic approaches in a private read-only audit; improvements were inconsistent across the problem sections.
- Documented the retrieval-expansion freeze and prepared the first-round research protocol, materials gap check and current-state records.

## Validation or evidence

- Experimental commit `322f7e9d956cde8916c3c8d56b972ed80267a761` and study-preparation commit `f8f7d14e6510eab667741433e2cdc437d5ede807` are both dated 8 October 2026.
- The experiment records 121 passing tests; the stable structural audit records 93 passing tests. They apply to different code versions and do not establish semantic acceptance.
- [TD-003](../../decisions/technical_decisions/td_003_freeze_automatic_project_state_inference.md) records the negative semantic outcome and scope decision. P96 remains an excluded researcher self-test.

## Decisions and rationale

- Freeze automatic retrieval expansion before Round 1. Related evidence can be historical, resolved, conditional or misattributed.
- Study how source visibility and user correction help creative practitioners assess a provisional reconstruction.
- Retain temporal metadata as possible explicit interface work or future research, rather than implementing automatic current-state inference.

## Problems or limitations identified

- Passing mechanism tests did not resolve the evidence-selection and project-state interpretation problems.
- The proposed three-person, supervised 40–50 minute study remained a draft, with supervisor/ethics-scope and data-handling questions unresolved at this point.

## Next recorded step

Review the Round 1 materials and outstanding data-handling questions with the supervisor before recruitment or material collection.

## Evidence used

- Commits `322f7e9d956cde8916c3c8d56b972ed80267a761` and `f8f7d14e6510eab667741433e2cdc437d5ede807`, including their actual diffs.
- [TD-003](../../decisions/technical_decisions/td_003_freeze_automatic_project_state_inference.md), 8 October decision; its later 9 October status update is not attributed to this day.
- [Round 1 protocol](../../feedback/user_testing/iteration_1/study_protocol_round_1_draft.md), original version at `f8f7d14`.
- Anonymised record types: dated P96 retrieval diagnosis, experimental validation and structural audit.
