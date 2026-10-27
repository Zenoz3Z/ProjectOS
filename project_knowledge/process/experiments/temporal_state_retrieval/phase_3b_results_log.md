# Phase 3B v1 results and trace-only verification recovery

Date: 27 October 2026. Status: verified mixed/negative experimental result; neither preregistered success criterion set was met.

## Run identity and scope

The frozen implementation was `8b790ea13c6eae236b325b012150e5c06bf524f6`. The public authorisation lock was committed as `7def9334aff4fbc2a487f3dead6d29d205ee41b5`. Run `phase_3b_state_aware_v1_run_20261027` executed once and completed all 34 cases: 18 production cases and 16 diagnostic cases across four frozen corpus views. The authoritative execution state remains `execution_completed`. Its existence makes the run unavailable for another execution, regardless of subsequent verification activity.

The experiment used the unchanged production queries, category filtering, 120-word chunks, 30-word overlap and locally cached all-MiniLM-L6-v2 model. The frozen selector applied record-state rules only to Sections 1, 3 and 5. Sections 2, 4 and 6 retained baseline selection; all 12 corresponding view/section selections matched the saved baseline. Pre-selection candidate identity, order, category and scores passed the frozen equality checks before scoring. No new participant study or production feature change was involved.

## Verification history

The original trace-only recompute attempt reached verification publication but failed with `PermissionError: WinError 5` during the AtomicWriter hard-link operation. No original `verification.json` was published. Read-only inspection before recovery found no remaining temporary verification file. The original failure record, raw trace, aggregate, paired comparison and execution state were preserved.

One separately authorised recovery recompute used a wrapper outside the repository. It called the unchanged frozen `score_case` for all 34 saved cases and the unchanged `result_bundle` once. It did not duplicate scoring formulas or rerun candidate selection. The private recovery file was created exclusively, and all 34 case results, 942 aggregate comparison fields, 88 paired-comparison fields and 78 frozen-baseline comparison fields matched, with zero mismatches.

Before public publication, the existing privacy guard rejected the exact key `summary`, which was being used for a zero-valued activity counter. The public projection uses `summary_calls` instead. It was published from the already saved recovery data, without an additional scoring attempt. Neither the guard nor the private recovery result was changed. Both new verification files used exclusive creation and did not replace original outputs.

This was the second metrics-recompute attempt overall: one original publication failure and one recovery recompute. It was not a second candidate evaluation. Formal execute count remains one. Recovery guards recorded zero model-loader, encode, retrieval, selector, document-loader, OpenAI, LLM, summary, network and protected-source access calls. The [public verification](../../../../outputs/test_results/temporal_state_retrieval_state_aware/verification.json) references the private raw trace only through its hash and retains the original publication-failure history.

## Production and diagnostic results

Production and diagnostic outcomes remain separate. The fractions below use the frozen eligibility denominators; they do not imply that every metric covers all 18 or 16 cases. Macro role coverage is a mean of per-case role fractions, not a count of successful cases.

| Metric | Production baseline to candidate | Diagnostic baseline to candidate |
|---|---|---|
| Hit@1 | 6/15 to 6/15 | 5/14 to 8/14 |
| Hit@3 | 10/15 to 12/15 | 8/14 to 9/14 |
| MRR | 0.5533 to 0.6168 | 0.4964 to 0.6323 |
| Macro role coverage@2 | 0.5667 to 0.7000 | 0.5000 to 0.6071 |
| All-required-role coverage@2 | 8/15 to 9/15 | 6/14 to 8/14 |
| Pair coverage@2 | 2/3 to 1/3 | 1/5 to 3/5 |
| Applicability evidence coverage@2 | 8/14 to 8/14 | 6/13 to 8/13 |
| Closure recognition@1 | 1/3 to 1/3 | 1/2 to 1/2 |
| Closure recognition@2 | 2/3 to 2/3 | 1/2 to 1/2 |
| Known false-current exposure lower bound | 1/9 to 1/9 | 1/11 to 1/11 |

Temporal mismatch, fully judged false-current accuracy and insufficient-preservation accuracy remain not measurable under this retrieval-only annotation and decision boundary. Missing judgments are not evidence of safety or zero error.

Among production cases eligible for affirmative evidence coverage, two cases gained a pass, one lost a baseline pass, seven remained passes and five remained failures. Three insufficient-boundary cases are reported separately. Selection changed in eight of all 18 production cases. Diagnostic results had two gains, no losses, six unchanged passes and six unchanged failures, with two insufficient-boundary cases reported separately. Selection changed in nine of all 16 diagnostic cases. Private case identities and excerpts remain outside public outputs.

Production first-request median increased from 21.73 to 24.87 ms; warm median increased from 22.01 to 25.26 ms, remaining below the preregistered 44.03 ms threshold. Median selector overhead was 0.543 ms. Diagnostic first-request median increased from 21.61 to 24.78 ms; warm median increased from 21.99 to 25.35 ms, with median selector overhead of 0.493 ms. Diagnostic timing covers 14 independent view/section requests shared by 16 cases; case-weighted timing is not additional independent measurement.

## Interpretation against the two frozen criteria sets

Record-level metadata improved some broad retrieval measures in this benchmark: production Hit@3, MRR and macro role coverage increased, and several diagnostic measures improved. Latency stayed within the Phase 3 threshold.

These observations did not constitute success under the [preregistration](phase_3_preregistration.md). All-required-role coverage reached only 9/15, below 10/15; one baseline pass was lost; and production pair coverage fell from 2/3 to 1/3. Closure recognition and the known false-current exposure lower bound did not improve. Phase 3 v1 did not meet the preregistered Phase 3 improvement criteria.

The original Phase 1 criteria were evaluated independently and were also not met. Failed checks included first-task completeness, strict pair improvement, the cross-project role-improvement requirement and complete explicit-closure coverage. The Phase 3 thresholds do not replace the Phase 1 criteria. The [saved report](../../../../outputs/test_results/temporal_state_retrieval_state_aware/phase_3b_report.md) and [aggregate results](../../../../outputs/test_results/temporal_state_retrieval_state_aware/candidate_aggregate_results.json) retain both decisions.

The outcome is mixed/negative. In these frozen cases, the method did not reliably preserve or improve evidence-role pairing. Document-level current/historical labels are too coarse, on their own, to establish statement-level supersession. This is a bounded interpretation of the observed pairing regression, not evidence of generally improved model understanding, solved temporal reasoning or improved participant projects. Diagnostic improvements do not establish overall success. No v2 was implemented or run, and no original result was adjusted after inspection.

## Activity and preservation

The sole formal execution recorded one local model load, four document encodes and 1,536 query encodes, for 1,540 encode calls in total. Saved traces account for 1,536 retrieval calls and 768 selector requests across the first, warm-up and 30 warm measurements for 24 distinct view/section requests. Formal scoring covered 34 cases. OpenAI, LLM, summary, external embedding API and model-download calls were zero. Recovery added only trace-based scoring and reporting, with no model, retrieval or selector activity.

The original state, lock, raw trace, aggregate, paired comparison and failure evidence remain unchanged. The runner, selector, scoring, metadata, gold, baseline, success criteria, production code and thesis drafts were not edited. Formal participant inputs were not accessed or rehashed. Verification recovery did not reopen the consumed one-shot.

## Post-run validation

| Check | Result |
|---|---|
| Runner, selector and Phase 3A static tests | 293 passed in 107.66s (0:01:47) |
| Complete regression suite | 450 passed in 295.84s (0:04:55) |
| Python compilation | 31 tracked Python files compiled in memory; no bytecode written |
| Dependency consistency | No broken requirements found |
| Markdown links | Four local links resolved |
| Public privacy scan | Eight public files checked; no credentials, contact details, private paths or private case identifiers found |
| Whitespace | Git diff check and checks of the new untracked files passed |
| Original execution outputs | All 44 saved output hashes matched the original private run manifest |

Tests used new isolated temporary directories and synthetic fixtures. The focused and complete runs each recorded zero attempts to access actual protected research directories, actual model weights or external networks. Synthetic selector and lifecycle tests do not constitute a new formal selection or candidate run. No test was skipped or weakened, and no temporary-resource failure or repeat full-suite run occurred. The original verification publication failure remains part of the audit history.

The result files, recovery verification and this log remain for local review. No results were committed or pushed, and no algorithm, schema or thesis revision followed the outcome.
