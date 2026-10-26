# Phase 2 experiment log: current production retrieval baseline

Date: 25 October 2026

Branch: temporal-state-retrieval-experiment

Baseline execution HEAD: `03d58f773a2fe0f7b4c1302368a5f720ae35b6a6`

## Purpose and boundary

Measured the unchanged production semantic retriever against phase_1_gold_v1: 18 primary production cases and 16 separately reported diagnostics. The permitted inputs were public Echo Field records, synthetic Signal Loom records and a researcher-owned private archive. Formal participant materials, caches, reviews and assignments were not accessed or rehashed. This technical experiment is not another participant study and does not change the thesis or frozen application.

The starting branch, commit, empty index and five existing untracked thesis drafts matched the requested state. Both freeze manifests, all source locators and the confirmed gold population passed validation. All frozen files and source materials remained unchanged. No gold status, query, corpus membership, retrieval behavior or parameter was adjusted in response to results.

## Implementation and run

Added an independent [baseline harness and scoring description](../../../../experiments/temporal_state_retrieval/README.md) plus 21 focused unit tests. The harness directly reuses production loading, chunking, embedding, cosine ranking, category filtering, two-query selection and excerpts. Its path-like adapter enumerates eligible files only. Historical Signal Loom excludes records six and seven. Gold does not enter retrieval requests; diagnostic questions do not replace the existing section queries.

Four frozen corpus views produced 24 unique view/section requests. One locally cached model instance encoded each corpus once. Fixed timing used one first query, one warm-up and 30 round-robin repetitions per request. No model download, dependency change or production modification occurred.

The [baseline report](../../../../outputs/test_results/temporal_state_retrieval_baseline/baseline_report.md) and its linked JSON/manifest contain full denominators, exclusions, project/section breakdowns, timing, model hashes and run provenance. Private case rankings, excerpts, per-request timing samples and failure analysis remain in ignored storage.

## Observations

Primary Hit@1 was 6/15 and Hit@3 was 10/15; MRR was 8.3/15 = 0.553333. Macro required-role coverage was 8.5/15 = 0.566667, with all roles covered in 8/15 supported cases. Required direction-pair coverage was 2/3, applicability evidence coverage was 8/14, and scoped closure recognition was 1/3 at rank one and 2/3 at the selected-pair cutoff.

Secondary Hit@1 was 5/14, Hit@3 was 8/14 and MRR was 6.95/14 = 0.496429. Macro role coverage was 7/14, pair coverage 1/5, applicability coverage 6/13 and closure recognition 1/2. These diagnostic cases did not enter primary performance denominators.

Full selected chunks contained text outside the frozen passage annotations. Therefore no fully judged top-1 temporal denominator was available: temporal mismatch and judged false-current rates are unmeasurable, not zero. Complete annotated exclusions establish only known-exposure lower bounds of 1/9 primary current-claim cases and 1/11 diagnostic current-claim cases. Final support, applicability and abstention classification remain outside retrieval-only evaluation. Resolving unjudged outputs for a definitive future comparison would require prospective review under the freeze rules; no such revision was made here.

Observed misses include ranking/selection gaps, category exclusions, missing role-pair coverage and loss of complete assertion/context visibility. A related excerpt is not automatically complete, current, role-compatible gold. No summariser ran, so these results cannot establish summariser conservatism or generated-answer accuracy. No alternative algorithm or repair was implemented.

## Timing and activity

Primary warm median was 22.014 ms (minimum 20.676, maximum 28.350, p95 23.339; 540 samples across 18 requests). Diagnostic warm median was 21.993 ms (minimum 20.569, maximum 28.350, p95 23.577; 420 samples across 14 requests). Eight requests are shared across the tier summaries; samples are not pooled into an overall score. Model loading was 402.783 ms, separately measured. Corpus preparation and document encoding are separately listed in the report.

Actual model activity: one model load; 1,540 encode calls and 1,610 encoded texts. Four document encode calls covered 74 chunk texts across views; 1,536 calls encoded the unchanged queries. Document embeddings were reused. OpenAI requests, LLM calls, summary generation, external embedding requests and network attempts were all zero.

## Validation and final review

- First sandbox unit run: 19 passed, two setup errors in pytest temporary-directory creation. No failing product assertion was observed.
- Unchanged new tests in the normal local user process: 21 passed in 14.21s.
- Full suite: **150 passed in 160.71s (0:02:40)**, including the 129 existing tests.
- Final focused check after timing/manifest instrumentation: 21 passed in 11.84s.
- External network and protected participant-data access attempts in the guarded test runs: zero.
- In-memory Python compilation: 18 files passed; no bytecode files written. pip check: no broken requirements.
- Both frozen manifests, gold schema, source locators and 64-file protected allowlist hashes passed. Existing code, configuration, tests, synthetic sources, researcher source records, private labels and all five thesis drafts remained byte-identical.
- Local Markdown links, public credential/contact/absolute-path scans, private-quote checks, tracked diff checks and untracked-file whitespace checks passed.
- One trailing empty line in the new scoring module was removed during final whitespace checking. Its AST is unchanged; the manifest preserves both execution-time and final artifact hashes. No results were regenerated or adjusted.
- At the end of the 25 October baseline session, the index was empty and all new work remained local and untracked. That session made no commit, push, merge, branch switch, main change or Phase 3 implementation.

## Final reporting audit — 26 October 2026

All 34 case IDs were reconciled against their saved view/request, ranked and selected evidence, scoring and first/warm timing records: 18/18 production and 16/16 diagnostic. The full case checklist remains private. No baseline, model encoding or retrieval was rerun.

Diagnostic latency previously reported 14 distinct requests, not 14 supported cases. Two pairs of diagnostic cases share a view/section request; both insufficient diagnostics retain full timing records. The distinct-request statistics (14 first / 420 warm measurements) remain unchanged. An additional all-case-weighted view uses 16 first / 480 warm contributions from those same saved measurements, with an explicit warning that shared contributions are not independent new timings. Its warm median is 22.075 ms, compared with 21.993 ms under request weighting. Production remains 18 first / 540 warm under both scopes.

Exact query accounting is `4 views * 6 sections * 2 queries * (1 first + 1 warm-up + 30 warm) = 1536` query encodes/texts. Cross-tier accounting is `1152 production + 896 diagnostic - 512 shared = 1536`. One model instance serves four document encodes; document texts are `12 + 49 + 5 + 8 = 74`. Total encode calls are 1,540 and total texts 1,610. Query embeddings are not reused across repetitions; only document embeddings and matching cases' stored results/timings are reused.

All accuracy metrics, denominators, breakdowns, rankings and principal conclusions are unchanged. The immutable protocol already prespecified the positive-gold denominator exclusions. Unjudged temporal metrics remain not measurable, and false-current exposure remains a known lower bound. Original raw trace and execution-time hashes are retained; final reporting hashes are separately recorded. The audit adds reporting/count reconciliation and five tests, with no retrieval algorithm change.

Initial audit validation: 26 baseline tests passed in 20.95s. The full suite returned **4 failed, 151 passed in 85.64s (0:01:25)**. The four existing synthetic project-context UI cases raised FileNotFoundError at `tests/test_evidence_guidance.py:158` when reading an expected temporary cache. Real participant files were not accessed. Root cause is undetermined; neither production nor old tests were modified, weakened or skipped. No retry was attempted during that initial audit. Compile passed for 18 files and pip check passed. The commit gate was blocked; no staging, commit or push occurred during that initial audit.

## Authorised UI isolation follow-up — 26 October 2026

The evidence-guidance file passed 24 tests, the four previously failing nodes passed individually as a group, and the unchanged old suite passed 129 tests. Both orderings of baseline and evidence-guidance tests passed 52 tests. After correcting import-path hygiene only in the new harness and its tests, two consecutive complete runs passed: **157 passed in 182.29s (0:03:02)** and **157 passed in 170.76s (0:02:50)**. Each process used a different ignored temporary directory. There were no skips, xfails or weakened assertions.

The original FileNotFoundError did not recur. A filesystem probe failed at a 260-character temporary path but succeeded at 259; the original temporary cache path had 260 characters. This is supporting evidence, not retrospective proof: **root cause unconfirmed**. The original complete traceback was unavailable. An initial external observer KeyError was retained as an invalid diagnostic attempt and corrected outside the repository before rerunning A. Complete matrix outputs and runtime-path observations remain private; the [baseline report](../../../../outputs/test_results/temporal_state_retrieval_baseline/baseline_report.md) records the validation boundaries.

The confirmed import-path side effect is now restored by scoped imports and normal monkeypatch cleanup; it has not been established as the cause of the cache failure. Two new regression tests cover import side effects and restoration. Compilation of 18 files and pip check passed. Gold, raw rankings, the 34 saved case results, aggregate accuracy, production code, old fixtures/tests, configuration and five thesis drafts are unchanged. Real participant files were neither read nor rehashed. No baseline rerun, real retrieval, embedding, LLM, summary or OpenAI call occurred. The required repeated full-suite gate is satisfied; this does not authorise another experiment phase.
