# Phase 3B1 implementation review

Date: 26 October 2026. Status: **implementation_validated_pending_commit**.

**Validation gate: passed.** The resource-isolation matrix A–G passed, including two consecutive complete regression passes in separate processes and fresh short temporary directories. `validation_gate_passed=true`, `execution_authorised=false`, `candidate_evaluation_run=false`. This is implementation validation, not authorisation for formal evaluation.

This implementation follows the [frozen Phase 3 preregistration](phase_3_preregistration.md), version `phase_3a_metadata_v1`, at commit `2c3a298be80f21f5f2bd21cd486e1944e154d1d9`. It implements final evidence selection and a non-executing runner skeleton. It reports synthetic engineering validation only. No production or diagnostic benchmark case has been evaluated, and no improvement, semantic acceptance or Phase 1/Phase 3 success is claimed.

## Components and input boundary

- [Selector](../../../../experiments/temporal_state_retrieval/state_aware_selector.py): deterministic selection with no file, model, corpus or evaluator dependency.
- [Adapter and runner skeleton](../../../../experiments/temporal_state_retrieval/state_aware_experiment.py): original production-function replay, minimal projection, isolated worker and dry preflight validation.
- [Synthetic tests](../../../../tests/test_state_aware_selector.py): independently constructed candidates, metadata and manifest fixtures.
- [Pre-run manifest candidate](../../../../outputs/test_results/temporal_state_retrieval_state_aware/pre_run_manifest_candidate.json): fingerprints and intended scope, not an executed-run manifest or permission to execute.

The serialised request has exactly `section_id`, `ordered_eligible_candidates` (two arrays) and `eligible_record_states`. Each candidate has exactly `chunk_id`, `record_id` and the unchanged `score`. Array position carries original query order. State values are enum strings. The selector returns only ordered chunk IDs, at most two. The trusted adapter supplies a baseline callable during construction; that callable is implementation code and cannot be supplied through the JSON request.

This keeps the stricter frozen interface: no excerpts, source paths, category fields, dates, ordinals, project IDs, rationale, state scope, case IDs, tiers, roles, expected evidence, support/applicability or outcomes cross the worker boundary. Unknown keys and nested complete-metadata objects are rejected before selection. The adapter may inspect complete metadata to build the fresh state-only projection, but the worker never receives that document. No source text is parsed for temporal meaning.

The adapter applies the unchanged production category helper to each original query channel, preserving every surviving occurrence, score and order. It rejects changed queries, records outside the supplied eligible view and unequal full-pool membership across the two channels. The equality guard compares ordered candidates with the original per-query projection; selected-first evaluation rankings are an explicitly rejected input channel. Formal execution must additionally compare those original channels with the frozen Phase 2 trace before dispatch. That integration is not executed here.

Missing metadata becomes `unknown` in the adapter and increments an adapter-side missing-record diagnostic; it never removes a candidate. Extra metadata records are not projected. Duplicate record annotations and a chunk assigned to conflicting record IDs are rejected. The frozen formal metadata must remain complete at preflight: this defensive path is not permission to run an incomplete experiment.

## Exact baseline reuse

S2, S4 and S6, and all complete-pair fallback paths, invoke the existing `reentry_brief.retrieve_diverse_evidence` function obtained through the Phase 2 adapter's production module loader. No second baseline algorithm is implemented.

The function receives an in-memory replay of the two already-filtered arrays. This replay performs no semantic search and uses the original production query strings. Minimal compatibility proxies expose the original chunk ID and score plus an allowed category so that the already-completed category gate is an identity operation. They do not alter the original records' categories or objects. The replay upper bound is the larger filtered-list length, sufficient to preserve both entire lists; upstream semantic retrieval still requires the frozen full-corpus `top_k=N`. This replay bound is not a new retrieval cutoff.

Synthetic equivalence tests compare this bridge with a direct call to the original production function on unfiltered synthetic results, including excluded categories, repeated scores and six input-order permutations for each unchanged section. A spy verifies that the actual production function is called. Selection IDs match exactly. Input objects, their scores and pool membership remain unchanged.

## Frozen selection pseudocode

Snapshot family is exactly `{current_snapshot, final_snapshot, closure_record}`. No member has priority over another.

### S1 and S5

```text
If neither query contains a snapshot-family candidate:
    return the complete production baseline selection.
Build a union keyed by chunk ID from original Q1 then original Q2:
    keep the highest-score occurrence; on equal score keep the first;
    retain first-encounter key order for union ties.
For Q1, then Q2:
    stably partition its original order into snapshot family, then others;
    append its first not-yet-selected chunk, if present.
If fewer than two were selected:
    stably order union representatives by descending original score;
    stably partition that order into snapshot family, then others;
    append unused chunks until two, or until the pool is exhausted.
Return selected chunk IDs in selection order.
```

Different chunks from one record remain distinct candidates. Snapshot promotion does not attach a current-evidence label. Dates and record ordinals never break ties. The union-fill path is tested defensively with sparse synthetic channels; normal full-corpus channels have equal membership. A one-unique-chunk pool remains a one-item result.

### S3

```text
first = Q1's first snapshot-family candidate in original order.
second = Q2's first historical_record candidate from a different record.
If both exist: return [first.chunk_id, second.chunk_id].
Otherwise: return the complete production baseline selection.
```

The original Q1 current/still-in-use focus and Q2 replaced/non-current/future-work focus are not rewritten. Historical record function is not a superseded-evidence label; no text or gold role is inspected. Whether the pair covers the target roles remains a later scoring question.

Under a single-valued record-to-state mapping, one record cannot simultaneously be snapshot-family and historical. The different-record condition remains explicit. Tests reject conflicting duplicate metadata rows instead of manufacturing that invalid state, and separately cover same-record/different-chunk retention, duplicate chunks, normal cross-record pairs and all fallback categories. This is a representational constraint, not an unresolved choice of selection rule.

## Isolation and runner readiness

New-module import does not import runtime/model libraries, change environment, cwd or sys.path, or write files. Production bridge preparation subsequently imports the original production modules and their library definitions, but never constructs a model or retriever. In the dedicated worker, trusted imports complete before an audit boundary denies file/directory, socket, subprocess and mutation access. Synthetic worker probes verify that file opening and socket creation fail and that valid selection still succeeds. This is an audited Python process boundary for trusted selector code, not a claim of an operating-system sandbox against arbitrary native code.

The worker uses stdin/stdout only for the closed request and chunk-ID response. The synthetic isolation wrapper starts a fresh worker per invocation; its startup cost is not a measured retrieval latency. No latency claim is made. Any later runner must disclose preparation and include actual selection/interface overhead in the frozen warm timing boundary, without silently excluding costs or relaxing the 44.03 ms displayed threshold.

Dry preflight checks the actual Git branch/HEAD and freeze ancestor, required public artifact hashes, four named private hash commitments, public/private freeze self-digests, the private-to-public link, the frozen private metadata commitment, both separate success-criteria objects and the four corpus-view sizes. It hashes gold bytes but does not parse gold or perform scoring. Private locations are supplied locally at runtime; the public manifest stores only private artifact labels and SHA-256 commitments.

The runner records the future stage order: exclusive pre-run lock; exact Phase 2 generation using the same four views and query encoding; original-candidate assertion; isolated selection; durable selection trace; subsequent scoring with production/diagnostic separation; private details and public aggregates. These are dry construction stages, not an implemented evaluation loop. The formal entrypoint deliberately raises an error. No lock or formal result writer is enabled in Phase 3B1.

## One-shot execution policy

Before a later authorised formal run, create an exclusive immutable pre-run manifest. Once any case-level candidate score exists, v1 is consumed regardless of outcome. Unfavourable results cannot trigger another run or rule adjustment. A technical failure before any case score must retain its failure evidence and stop for manual review, without an automatic retry. After a run, metrics may only be audited from saved traces; selection cannot be re-executed to replace results. An implementation correction must preserve v1 and use a new preregistration/version.

The synthetic lifecycle tests cover locked/no-score, consumed and pre-score-failure states. They create no actual run lock or case score. Both original Phase 1 and Phase 3 improvement criteria remain unchanged and unevaluated. Metadata confirmation remains researcher confirmation, not independent annotation.

## Engineering validation

The focused check passed 192 tests in 32.28s: 119 new synthetic checks and all 73 frozen Phase 3A static checks. Coverage includes original-baseline equivalence, state promotion, S3 pairing/fallback, unknown/undated states, duplicate identities, stable ties, unchanged pools/scores/inputs, bounded and repeatable output, nested prohibited fields, isolated worker access denial, import hygiene, dry preflight drift rejection and one-shot state transitions.

### Retained failures and resource audit

Before this audit, the first complete run had 348 passed and one existing UI failure in 179.32s: `tests/test_participant_ui.py::test_completed_p96_isolated_from_other_projects_and_tutorial`, with PermissionError [WinError 5] during replacement of a synthetic review file. That test passed alone in a fresh process (1 passed in 21.65s). The second complete run had 348 passed and one existing UI setup error in 176.00s: `tests/test_participant_ui.py::test_direct_navigation_is_locked_until_all_six_are_saved[5]`, with WinError 10055 in the Windows asyncio socketpair path.

Both original full tracebacks and test orders were preserved privately. Neither failure was preceded by a Phase 3B test call in that process; this rules out those new test calls as an earlier action in those runs, but does not establish a general root cause or exclude collection/import effects. Original failure-time process, handle and thread snapshots were unavailable. Environment and temporary-directory settings were reconstructed from the preserved runner and identified as reconstructed. The reported replacement path was 153 characters, so a 260-character path-limit explanation is not established by that failure evidence.

The audit examined the two new implementation modules and new test module. Process creation uses synchronous, context-managed `subprocess.run` or `check_output`. The installed Python implementation communicates, closes pipes and waits; on a Windows timeout, `run` kills the child, communicates again and re-raises. This timeout path was inspected, not newly forced. No direct process pool, executor, explicit event loop, background service or unfinished future is created by these three files. The existing worker timeout was not changed. The one-shot checks only change in-memory state and create no actual lock or case score. Synthetic temporary files are not deleted while in use.

In each B–G process, all three observed subprocesses exited with code 0, every present stdin/stdout/stderr pipe was closed, and the corresponding Popen objects were collected. No test-owned child remained in the post-test or final snapshots. Unrelated Python processes were neither attributed to the tests nor terminated. Python-level active thread count was one at the final snapshot. Native-library threads and process handles increased when existing production dependencies were imported; that increase is reported rather than treated as zero resource growth.

For isolated subset C, handles were 165 before pytest, 183 after collection and 539 after pytest; native thread counts were 4, 4 and 41. The first worker test started after fixture preparation at 541 handles and ended at 542; the second worker and one-shot tests remained at 542, with no continuing per-worker increase. C retained zero temporary files and four empty directories deliberately for audit. All original failed directories were preserved. These observations provide no confirmed resource-leak evidence; they do not prove that an intermittent operating-system issue is impossible.

Parent cwd and sys.path were restored. No environment difference remained except pytest's own `PYTEST_CURRENT_TEST` phase marker. No existing sys.modules entry was removed or replaced during the observed new test calls. Explicit production bridge preparation can retain ordinary imported modules and native library state; the audit does not claim wholesale removal of Python's import cache. The separate import-only check confirmed that importing the new modules did not start a runner, load model libraries, mutate cwd/environment/sys.path or write files.

### Fresh-process isolation matrix

Each row used a distinct short basetemp and separate Python process; no pytest runs overlapped. Full stdout/stderr, node order, long tracebacks where applicable, and resource observations are retained in ignored diagnostic storage. No assertion was reduced and no test was skipped or marked xfail.

| Check | Scope | Pytest result | Exit code |
|---|---|---|---|
| A | All old tests; new test module excluded | 230 passed in 178.83s (0:02:58) | 0 |
| B | All new synthetic tests | 119 passed in 49.79s | 0 |
| C | Import, process-isolation and one-shot subset | 4 passed in 61.37s (0:01:01) | 0 |
| D | New tests, then the two old UI nodes | 121 passed in 79.92s (0:01:19) | 0 |
| E | Two old UI nodes, then new tests | 121 passed in 78.25s (0:01:18) | 0 |
| F | First complete suite | 349 passed in 266.86s (0:04:26) | 0 |
| G | Second consecutive complete suite | 349 passed in 264.64s (0:04:24) | 0 |

The prior errors were not reproduced in this matrix. They are recorded as an unreproduced Windows temporary-resource issue; **root cause unconfirmed**. No implementation or test change was needed for this audit, and no production code, existing test, system permission, event-loop policy, dependency, timeout or cleanup mechanism was changed to obtain these passes.

### Commit boundary and deferred formal lock

The candidate manifest records implementation parent HEAD `2c3a298be80f21f5f2bd21cd486e1944e154d1d9` and the validated source hashes. It is not a formal pre-run lock. After the implementation commit, a formal lock must be regenerated under separate authorisation and bind the new implementation commit; this parent-HEAD candidate must not be used as that lock. The existing synthetic dry-preflight validator accepts the earlier review-plan state only and does not treat the post-validation publication status as an executable preflight plan. The formal evaluation entrypoint remains disabled.

Phase 1, Phase 2 and Phase 3A frozen bytes, production source, existing tests/configuration, the protected researcher self-test sources/metadata and five thesis drafts remain protected. Formal participant files were not read, parsed or rehashed. Real OpenAI/LLM requests, model construction, embedding/encode, semantic retrieval and summary generation were zero. The new tests replayed synthetic selection inputs; existing mocked or synthetic tests did not operate on participant data. No formal case-level candidate result, score or pre-run lock was produced.

This review concerns implementation readiness only. It supplies no case-level ranking, candidate score, predicted metric or result analysis, and does not authorise formal execution.
