# Phase 3B implementation review

Updated: 27 October 2026. Phase 3B2.1 repairs the runner hash contract; the selector, frozen experimental inputs and production files remain byte-identical. Earlier validation records below retain their original scope.

The earlier Phase 3B1 resource-isolation matrix A–G is retained below as historical engineering evidence. Phase 3B2 validation is recorded separately at the end. `execution_authorised=false` and `candidate_evaluation_run=false`: implementation validation does not authorise formal evaluation.

This implementation follows the [frozen Phase 3 preregistration](phase_3_preregistration.md), version `phase_3a_metadata_v1`, at commit `2c3a298be80f21f5f2bd21cd486e1944e154d1d9`. Phase 3B2 starts from implementation commit `25bf8e0c7af38d6c7a395a1e9866de46ecd8d27d` and adds formal read-only preflight, a durable one-shot runner and trace-only verification. It reports synthetic engineering validation only. No production or diagnostic candidate benchmark case has been evaluated, and no improvement, semantic acceptance or Phase 1/Phase 3 success is claimed.

## Components and input boundary

- [Selector](../../../../experiments/temporal_state_retrieval/state_aware_selector.py): deterministic selection with no file, model, corpus or evaluator dependency.
- [Adapter and runner](../../../../experiments/temporal_state_retrieval/state_aware_experiment.py): original production-function replay, minimal projection, isolated worker, formal preflight, execution and verification.
- [Selector tests](../../../../tests/test_state_aware_selector.py): unchanged independently constructed candidates, metadata and manifest fixtures.
- [Runner tests](../../../../tests/test_state_aware_experiment.py): synthetic repositories, dependencies, source records, traces, scores, locks and failures, confined to temporary test directories.
- [Pre-run manifest candidate](../../../../outputs/test_results/temporal_state_retrieval_state_aware/pre_run_manifest_candidate.json): fingerprints and intended scope, not an executed-run manifest or permission to execute.

The serialised request has exactly `section_id`, `ordered_eligible_candidates` (two arrays) and `eligible_record_states`. Each candidate has exactly `chunk_id`, `record_id` and the unchanged `score`. Array position carries original query order. State values are enum strings. The selector returns only ordered chunk IDs, at most two. The trusted adapter supplies a baseline callable during construction; that callable is implementation code and cannot be supplied through the JSON request.

This keeps the stricter frozen interface: no excerpts, source paths, category fields, dates, ordinals, project IDs, rationale, state scope, case IDs, tiers, roles, expected evidence, support/applicability or outcomes cross the worker boundary. Unknown keys and nested complete-metadata objects are rejected before selection. The adapter may inspect complete metadata to build the fresh state-only projection, but the worker never receives that document. No source text is parsed for temporal meaning.

The adapter applies the unchanged production category helper to each original query channel, preserving every surviving occurrence, score and order. It rejects changed queries, records outside the supplied eligible view and unequal full-pool membership across the two channels. The equality guard compares ordered candidates with the original per-query projection; selected-first evaluation rankings are an explicitly rejected input channel. Formal execution additionally compares those original channels with the frozen Phase 2 trace before dispatch. This path is exercised with synthetic dependencies here, never with actual benchmark retrieval.

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

## Phase 3B2 formal runner and lock boundary

Import remains inert: it does not load model libraries, modify the environment, cwd or search path, start a subprocess, write files or enter a runner mode. Preflight, execute and recompute are separate explicit entrypoints. The earlier synthetic dry-plan helpers remain for compatibility with the unchanged selector tests; they do not authorise formal execution.

Formal preflight accepts only the canonical public `pre_run_lock.json`, never the candidate manifest. It checks explicit one-shot authorisation, experiment version, fixed outputs, 18 production and 16 diagnostic cases, the four frozen views, model revision, environment versions and both unchanged criteria objects. It hashes committed inputs without parsing gold. The actual model must already exist locally with the frozen file hashes; no download is permitted.

The lock must identify the resulting Phase 3B2.1 implementation commit. That commit must descend from the validated Phase 3B2 commit and be an ancestor of the later lock commit. The only permitted intervening tracked difference is the addition of the public lock. The lock's bytes must match the committed file; the working tracked files and index must be clean. Implementation artifacts, including this review and the runner tests, must satisfy the three-layer hash contract below. Frozen Phase 1/2/3A workspace bytes and the selector must also match their unchanged Phase 3B1 raw-byte commitments. This avoids a circular requirement that HEAD equal the implementation commit after a lock has been committed.

The public lock commits the hash of a separate ignored private lock. The private lock supplies local input bindings, the offline model location and an 18-record identity inventory containing only record ID, project ID, relative source path, source category and SHA-256. It contains no expected passage or target role in that inventory. Public record identities are checked against the frozen public inventory; private source bytes and metadata are checked against frozen private commitments. The private lock does not contain a reciprocal public-lock hash. A final identity join against the frozen gold catalogue occurs only after selection, before scoring. Private paths never enter public output.

Candidate channels are checked against the frozen Phase 2 per-query trace before the selector receives them: query text/order, candidate count, chunk identity/order, original source/category and original cosine score must match. Selected-first evaluation rankings cannot replace those channels. Since no nonzero numerical tolerance was preregistered, the implemented lock requires zero absolute and relative tolerance. Drift stops the run and is retained privately; it does not trigger adjustment or another attempt.

## One-shot execution and persistence

Successful preflight precedes an exclusive durable `execution_started` record. It stores the run identity, experiment version, implementation and lock commits, lock hash, start time and zero scored cases. Any existing state or formal output rejects execution. There is no retry, resume or reset entrypoint, and a no-argument call cannot start evaluation. The real-repository entrypoint rejects synthetic dependency or Git injection.

The future default execution activates process-local offline/access guards, loads one local model and builds four frozen views. Document loading and chunking use the unchanged production functions. The injected index contains precisely the production retriever's chunks, shared model and normalised embeddings, with the same encoding options; its retrieval method is the original production method. This avoids replacing production globals or duplicating its ranking algorithm. The selectors and gold-independent adapter are unchanged. Tests inject synthetic model loaders, document loaders, chunk creators, indexes, adapters, selectors, scoring, clocks and writers instead of accessing actual experiment data.

One persistent selector subprocess receives only the frozen minimal payload. Trusted production imports precede a Python audit boundary denying file/directory access, sockets, subprocess creation and mutation. Responses contain only at most two allowed chunk IDs. Pipes, the response-reader executor, error stream and child process are closed and joined, including timeout/error paths; a nonzero exit is not accepted as successful execution. This is a trusted-code Python boundary, not a claim of an operating-system sandbox against arbitrary native code.

The run covers 24 distinct view/section requests, with one first request, one warm-up and 30 warm repetitions each. Every repeated trace must match its first selection. All selections and timing samples are durably saved before gold is parsed. A future complete run expects one model load, four document encoding calls and 1,536 query encoding calls; no such activity occurred during this implementation phase. Worker startup, model loading and corpus preparation are reported separately. Measured request time includes original retrieval/baseline selection, adapter/IPC/selector overhead and excerpt construction; hash auditing, offset mapping and scoring are excluded. The displayed Phase 3 warm median limit remains 44.03 ms with its exact frozen machine value retained. Environment mismatch prevents a latency-gate success claim.

Each case is scored once after selection. Its trace, score and frozen baseline comparison are published before the durable scored-case count advances. A score consumes v1 immediately, even if publishing that case subsequently fails; the pending score and produced/persisted counts are retained in failure evidence. A zero-score exception becomes `execution_failed_before_scoring`; any produced score leads to `execution_failed_after_partial_scoring`. Failures preserve existing artifacts and do not automatically retry.

Writes use a same-directory temporary file, flush and fsync, followed by atomic exclusive publication. Existing results cannot be replaced. Only the private execution-state file may be atomically replaced. Completion publishes production and diagnostic aggregates separately, paired gains/losses and metric deltas, latency/call counts, private case results, completion status and final output hashes. Multi-file publication is not an all-or-nothing filesystem transaction: a late failure can leave completed individual output files. The private execution state and retained failure log are authoritative; incomplete or inconsistent output sets must not be treated as a successful run or overwritten.

Public outputs are constructed from aggregate/identifier allowlists and checked for source-bearing keys, private identifiers, locators and credential/contact patterns before writing. Private case details, excerpts, gold and source mappings remain in the ignored run directory. Pattern checks are defence in depth, not a proof that arbitrary prose can be de-identified automatically.

## Trace-only verification

Recompute accepts a saved completed one-shot run in the ignored run directory. It checks the saved lock/scorer commitments and output hashes, including missing files. It then uses only the saved gold/trace data and frozen scorer to reproduce case results and every aggregate numerator, denominator and value. It also checks paired results. It does not construct runtime dependencies, load a model, retrieve candidates or invoke the selector.

Verification writes a new private JSON file without replacing the original aggregates or traces. A mismatch is recorded as `validation_failed`, with the private execution state updated accordingly; it is not silently corrected. New tests cover both altered and missing output files. Formal execution remains unauthorised. No actual lock, execution state, raw trace or candidate result has been created.

## Historical Phase 3B1 engineering validation

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

### Historical Phase 3B1 commit boundary

At Phase 3B1, the candidate manifest recorded implementation parent HEAD `2c3a298be80f21f5f2bd21cd486e1944e154d1d9` and the validated source hashes. It is not a formal pre-run lock. After the implementation commit, a formal lock must be regenerated under separate authorisation and bind the new implementation commit; this parent-HEAD candidate must not be used as that lock. The existing synthetic dry-preflight validator accepts the earlier review-plan state only and does not treat the post-validation publication status as an executable preflight plan. The Phase 3B1 formal evaluation entrypoint remained disabled; Phase 3B2 supersedes that implementation boundary as described in this review.

Phase 1, Phase 2 and Phase 3A frozen bytes, production source, existing tests/configuration, the protected researcher self-test sources/metadata and five thesis drafts remain protected. Formal participant files were not read, parsed or rehashed. Real OpenAI/LLM requests, model construction, embedding/encode, semantic retrieval and summary generation were zero. The new tests replayed synthetic selection inputs; existing mocked or synthetic tests did not operate on participant data. No formal case-level candidate result, score or pre-run lock was produced.

This review concerns implementation readiness only. It supplies no case-level ranking, candidate score, predicted metric or result analysis, and does not authorise formal execution.

## Historical Phase 3B2 validation and publication boundary

Status: **runner_validated_pending_lock**. `validation_gate_passed=true`, `formal_runner_implemented=true`, `execution_authorised=false`, `candidate_evaluation_run=false`, `intended_run_count=1`. The candidate manifest is a publication record, not the formal lock. A separately authorised lock must bind the resulting implementation commit before execution can occur.

| Validation | Observed result |
|---|---|
| Focused runner/selector/Phase 3A check before final edge-case additions | 260 passed in 73.15s (0:01:13) |
| Final runner tests, including revised implementation commitments and missing verification inputs | 71 passed in 19.26s |
| Complete suite on the final Python implementation | 420 passed in 249.24s (0:04:09) |
| Final suite composition | 71 runner, 119 selector, 73 Phase 3A static and 157 other existing tests |
| Python compilation | 31 Python files compiled in memory; no bytecode publication |
| Dependency check | No broken requirements found |
| Import and read-only preflight | No import side effects; synthetic valid lock succeeds without writes; real candidate path is rejected before private input access |
| Protected inputs | 87 recorded hashes unchanged, including frozen inputs, selector, old tests/configuration and five thesis drafts |
| Local links and diff whitespace | All six local Markdown links resolve; diff checks pass |
| Privacy | No real credential, contact detail, private absolute path or participant source content in the four publication files |

Validation used separate processes and fresh short temporary directories, with UTF-8 enabled for the frozen documents. The first external test-output wrapper failed before collection because its stream proxy lacked `isatty`; only the external wrapper was corrected. An intermediate focused run then passed 258 checks before a frozen static test attempted to decode its UTF-8 protocol using the Windows GBK default. That invocation had omitted the UTF-8 process option used by the earlier validation environment. Restoring that option produced the 260-pass focused run; no old test, frozen document, system setting or dependency was changed. The final runner additions and complete suite subsequently passed as recorded above.

No Windows PermissionError, socketpair exhaustion or other unexplained resource failure recurred in Phase 3B2, so the conditional requirement for two consecutive complete reruns was not triggered. The historical Phase 3B1 root cause remains unconfirmed. No assertions were weakened and there were no skipped or xfailed tests.

The full-suite boundary guard recorded zero attempts to access actual protected input directories, actual model-weight files or external network endpoints. P01–P04 were not read, parsed or rehashed. Private research source checks were limited to previously authorised integrity hashing. Source/category/ID literals and negative-test strings in the new code are implementation contracts or explicitly synthetic fixtures, not participant statements. The privacy scanner's path-pattern hit was the defensive regular expression itself, not an actual local path.

Real activity throughout Phase 3B2: OpenAI 0; LLM 0; embedding model loads 0; encode 0; semantic retrieval 0; summary generation 0; formal candidate case scores 0. Synthetic tests exercised scoring and lifecycle writes only on invented cases in temporary repositories. The actual public output directory still contains no formal lock or candidate evaluation result. Implementation is ready for the separately authorised lock stage; no benchmark outcome or future improvement is asserted.

## Phase 3B2.1 cross-platform hash contract

The attempted pre-commit lock audit found that ten frozen production Python files had CRLF worktree bytes and LF committed blobs. Their raw workspace hashes still matched the frozen manifests, and their content was equivalent under Git's existing clean/EOL rules. The previous formal preflight incorrectly required a single SHA-256 to describe both representations. No evaluation, model loading or scoring had started. This was a runner validation defect, not a changed source corpus or an experimental result.

The old uncommitted public lock and its corresponding private lock were moved intact into ignored diagnostic storage. Their original SHA-256 values are respectively `8f01bbd80ab91bfb22c3d4d4a26f7932bd6df870fbc9945a7b323c49841d6073` and `31a72788c18192752246f028c2aee2baf6ef175f0b2c2e90a80e18271e0300c0`. The private archive records `invalidated_before_commit`, the validation-bug reason, archive time, zero scored cases, no execution state and no consumed one-shot. Archived bytes were not rewritten. The canonical public lock path is absent, and the archive cannot authorise execution.

Hash contract version 2 separates three checks:

1. **Frozen workspace-byte integrity:** SHA-256 of unmodified raw worktree bytes must equal both the explicit workspace commitment and the applicable frozen raw-byte hash. CRLF is not normalised for this check. Existing manifests retain their original values.
2. **Committed-blob integrity:** the regular-file blob OID is resolved from the specified implementation commit, the blob's raw bytes are read, and its SHA-256 and OID must match the separate lock commitments. Neither value is inferred from a workspace hash.
3. **Worktree-to-commit equivalence:** Git computes the worktree blob OID using the repository's actual clean/EOL rules and the repository-relative path. This must equal the implementation blob OID. Object-writing mode is never used. Generic whitespace removal and manual newline replacement are not substitutes for this check.

Future formal artifacts require `workspace_raw_sha256`, `committed_blob_sha256` and `git_blob_oid`. The top-level modes are `hash_contract_version=2`, `worktree_hash_mode=raw_bytes_sha256`, `committed_hash_mode=git_blob_bytes_sha256` and `equivalence_mode=git_clean_filtered_blob_oid`. A legacy lock or ambiguous single-hash artifact is rejected rather than silently upgraded. The ancestry guard remains mandatory and is anchored to Phase 3B2 commit `5e433a591183f84471c2081e8522e19d9b1e4cc6`; unchanged frozen input hashes remain anchored to their earlier commitments.

Each validated tracked artifact reports its relative path, workspace/frozen raw hashes, implementation commit, actual committed OID and SHA-256, cleaned worktree OID, all three boolean checks, detected EOL representation and validation status. Failure reports retain the layer reached and a rejection reason. Missing files or commit entries, failed Git commands, incorrect commitments, path escapes, symlinks/reparse points and unexpected filters fail closed. External clean filters, working-tree encoding conversions and ident expansion are not authorised. Binary data cannot be forced through text-EOL conversion or silently transformed. File extensions do not exempt an artifact from validation.

The publication candidate remains non-executable. Unchanged artifact blob commitments are read from the current commit. For the three modified implementation artifacts, prospective blob commitments can be recorded only when Git's cleaned and unfiltered worktree OIDs are identical, making the current raw bytes the exact prospective blob bytes. A later authorised lock must still derive every blob commitment from the resulting implementation commit. The candidate is neither that lock nor proof of a completed formal preflight.

### Phase 3B2.1 validation

Status: **runner_hash_contract_v2_validated_pending_lock**. The validation gate passed. Execution remains unauthorised, no new formal lock exists, no execution state was created and the one-shot remains unconsumed.

| Check | Result |
|---|---|
| New hash-contract tests, final path guards included | 30 passed, 71 deselected in 7.60s |
| Runner, selector and Phase 3A checks before the final two path cases | 291 passed in 79.41s (0:01:19) |
| Complete suite on final Python implementation | 450 passed in 197.39s (0:03:17) |
| Final full-suite composition | 101 runner checks, 119 unchanged selector checks, 73 unchanged Phase 3A checks and 157 other existing tests |
| Production/source integrity | All ten originally affected production files remain byte-identical and pass all three layers |
| Broader integrity audit | 88 protected raw hashes unchanged; all 66 tracked protected files pass the three-layer audit against the parent implementation commit |
| EOL audit | 21 of those 66 files have CRLF worktrees and LF blobs, including all ten original blockers |
| Compilation and dependencies | 31 Python files compiled in memory; no broken requirements found |
| Documentation and privacy | Six local links resolve; final diff checks and public-content scans pass |

The new checks use small temporary Git repositories. They verify LF/LF and CRLF/LF equivalence, reject changed characters and trailing spaces as well as added/deleted lines, and exercise wrong commitments, missing files/commit entries, Git failures, binary handling, unexpected clean transformations, absolute/drive-relative/traversal paths and a real Windows junction. File and object-database snapshots confirm that validation does not rewrite inputs or publish Git objects. Existing lifecycle, ancestry, dry-preflight and import-isolation checks remain in place; their fixtures now provide explicit v2 commitments without removing or reducing assertions.

No intermittent resource failure occurred, so the conditional second complete pass was not needed. The external test guard observed zero actual protected-directory, model-weight or external-network access attempts. Temporary Git identities and attributes belong only to synthetic fixtures. The ProjectOS repository/global Git configuration and repository attributes were not changed. A temporary extra blank line in this document was removed before final diff validation.

The candidate manifest records the 66 tracked-file reports, including every requested hash, OID, match flag and EOL field. Private/untracked protected inputs are represented only by integrity counts or existing commitments. P01–P04 were not accessed, parsed or rehashed; researcher self-test sources/metadata, frozen Phase 1/2/3A files, the selector and five thesis drafts retain their bytes. No production or old UI test was edited. Real OpenAI, LLM, model load, encode, retrieval, summary and candidate scoring counts are all zero. Synthetic lifecycle/scoring fixtures do not constitute benchmark execution.
