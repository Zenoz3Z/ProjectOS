# Current production retrieval baseline — Phase 2

Date: 25 October 2026

Gold: `phase_1_gold_v1`. Production checkpoint: `03d58f773a2fe0f7b4c1302368a5f720ae35b6a6`. One baseline run, no alternative method or tuning.

## Scope and interpretation

This is the current production semantic retrieval baseline on frozen, single-researcher-confirmed gold. Echo Field is public demonstration material, Signal Loom is entirely synthetic, and P96 is a researcher-owned archive. Formal participant projects were not accessed. Inter-rater agreement was not assessed. These results do not estimate performance on participant projects or creative projects generally. Diagnostic results do not enter primary metrics. Retrieval-only evaluation cannot establish final summary accuracy, support classification, applicability classification or abstention correctness.

The original [frozen protocol](../../../project_knowledge/process/experiments/temporal_state_retrieval/experiment_protocol.md), [adapter/scoring description](../../../experiments/temporal_state_retrieval/README.md), [aggregate results](aggregate_results.json) and [run manifest](run_manifest.json) provide the evaluation contract and audit trail. The manifest records dependency versions, model snapshot and file hashes, source code hashes, frozen-gold commitments, queries and runtime counters. Private case-level traces and explanations are held only in the ignored researcher archive.

## Production behavior and fixed procedure

`load_documents` and `create_chunks` retain 120-word windows with 30-word overlap. `SemanticRetriever` retains all-MiniLM-L6-v2, normalised local embeddings, NumPy cosine ranking and original tie behavior. `get_section_queries`, `select_evidence`, `retrieve_diverse_evidence` and `create_excerpt` are called directly: each section uses its two configured queries, the existing category filter, all view chunks as candidates, ordered deduplicated selection of two, and the 1,200-character excerpt limit. Canonical questions and diagnostic labels never replace those queries.

A path-like adapter restricts loader enumeration to frozen eligible records. Signal Loom historical requests exclude its undated sixth and later closure seventh records. Four corpus indices are encoded once and reused. A shared counted wrapper delegates every encode unchanged to one cached, offline model instance. Gold is used for validation and subsequent scoring only. No source, frozen label, production file or existing test was edited.

Timing was fixed before execution: one first query, one warm-up and 30 repetitions per unique view/section in sorted round-robin order. The single baseline has no other arm to alternate. Query timers include encoding, ranking, production selection and production excerpts; source-offset mapping and scoring are excluded. Model load, corpus preparation and document encoding are separate. All eighteen primary cases map to eighteen unique requests; all sixteen diagnostic cases map to fourteen unique requests. The tiers share eight requests. Distinct-request timing summaries remain separate and are not pooled; an all-case-weighted view is reported in the final audit below.

## Primary results: 18 production cases

Primary denominators: 15 supported, 3 insufficient; 14 known-applicability, 3 explicit-negative and 3 required-pair cases. The supported/unclear aim case is included in supported retrieval metrics but excluded from known-applicability coverage.

| Metric | Numerator / denominator = value |
| --- | --- |
| Hit@1 | 6 / 15 = 0.4 |
| Hit@3 | 10 / 15 = 0.666667 |
| MRR | 8.3 / 15 = 0.553333 |
| Required-role coverage@2 (macro) | 8.5 / 15 = 0.566667 |
| All required roles@2 | 8 / 15 = 0.533333 |
| Required pair coverage@2 | 2 / 3 = 0.666667 |
| Temporal mismatch, fully judged top-1 | 0 / 0 = not measurable |
| False-current exposure, judged current-claim cases | 0 / 0 = not measurable |
| Applicability evidence coverage@2 | 8 / 14 = 0.571429 |
| Closure recognition@1 | 1 / 3 = 0.333333 |
| Closure recognition@2 (secondary cutoff) | 2 / 3 = 0.666667 |
| Known false-current exposure / all current-claim cases | 1 / 9 = 0.111111 |
| Final insufficient-preservation accuracy | not measurable / not measurable = not measurable |

MRR numerator is exactly 83/10 (sum of reciprocal ranks), divided by 15. Role coverage numerator is the sum of per-case fractions, not a number of successful cases; raw roles covered are 12/21. Eligible public case IDs, private eligible counts and every exclusion reason are in the JSON. Insufficient cases are excluded from positive-gold hit/MRR/role metrics, not assigned successful abstentions.

Hit@1 strata: applicable 5/11; explicit-negative 1/3; supported/unclear 0/1. Hit@3 strata: 8/11, 2/3 and 0/1 respectively. Applicability coverage is 6/11 applicable and 2/3 not_applicable; four unclear cases are excluded.

## Primary project and section breakdowns

| Project | Hit@1 | Hit@3 | MRR | Role coverage@2 | Pair coverage@2 |
| --- | --- | --- | --- | --- | --- |
| p96_researcher_archive | 0 / 4 = 0 | 0 / 4 = 0 | 0.466667 / 4 = 0.116667 | 0 / 4 = 0 | 0 / 1 = 0 |
| sample_echo_field | 3 / 6 = 0.5 | 6 / 6 = 1 | 4.333333 / 6 = 0.722222 | 4.5 / 6 = 0.75 | 1 / 1 = 1 |
| signal_loom_synthetic | 3 / 5 = 0.6 | 4 / 5 = 0.8 | 3.5 / 5 = 0.7 | 4 / 5 = 0.8 | 1 / 1 = 1 |

Equal-project macro Hit@1 is (0 + 0.5 + 0.6)/3 = 0.366667; macro Hit@3 is (0 + 1 + 0.8)/3 = 0.6. These are separate from pooled primary-case values. Full project macro metrics are in the JSON.

| Section | Hit@1 | Hit@3 | Role coverage@2 | Pair coverage@2 |
| --- | --- | --- | --- | --- |
| changes_and_reasons | 1 / 3 = 0.333333 | 2 / 3 = 0.666667 | 1.5 / 3 = 0.5 | 0 / 0 = not measurable |
| current_intention | 0 / 3 = 0 | 2 / 3 = 0.666667 | 1 / 3 = 0.333333 | 0 / 0 = not measurable |
| current_vs_superseded | 2 / 3 = 0.666667 | 2 / 3 = 0.666667 | 2 / 3 = 0.666667 | 2 / 3 = 0.666667 |
| possible_next_action | 1 / 2 = 0.5 | 2 / 2 = 1 | 2 / 2 = 1 | 0 / 0 = not measurable |
| relevant_feedback | 1 / 2 = 0.5 | 1 / 2 = 0.5 | 1 / 2 = 0.5 | 0 / 0 = not measurable |
| unresolved_tensions | 1 / 2 = 0.5 | 1 / 2 = 0.5 | 1 / 2 = 0.5 | 0 / 0 = not measurable |

## Public primary case coverage

Pass means only that all frozen required roles and any required direction pair appear in the selected two items. It does not mean an accurate or exhaustive generated answer. An insufficient case is not assigned a classifier pass/fail.

| Case | Section | Evidence-coverage result | First complete gold rank |
| --- | --- | --- | --- |
| EF-01 | current_intention | fail | 3 |
| EF-02 | changes_and_reasons | fail | 2 |
| EF-03 | current_vs_superseded | pass | 1 |
| EF-04 | relevant_feedback | pass | 1 |
| EF-05 | unresolved_tensions | pass | 1 |
| EF-06 | possible_next_action | pass | 2 |
| SY-02 | current_intention | pass | 2 |
| SY-08 | relevant_feedback | fail | absent/not applicable |
| SY-12 | possible_next_action | pass | 1 |
| SY-13 | changes_and_reasons | pass | 1 |
| SY-14 | current_vs_superseded | pass | 1 |
| SY-15 | unresolved_tensions | not a support-classification test | absent/not applicable |

All six private primary cases were evaluated. Their individual rankings, pass/fail details, passage identifiers and excerpts remain private; their contribution to the aggregate project totals is included above.

## Secondary diagnostics: 16 cases

Fourteen supported and two insufficient cases; thirteen known-applicability, two explicit-negative and five direction-pair cases. These secondary results explain failure modes and cannot establish production improvement.

| Metric | Numerator / denominator = value |
| --- | --- |
| Hit@1 | 5 / 14 = 0.357143 |
| Hit@3 | 8 / 14 = 0.571429 |
| MRR | 6.95 / 14 = 0.496429 |
| Required-role coverage@2 (macro) | 7 / 14 = 0.5 |
| All required roles@2 | 6 / 14 = 0.428571 |
| Required pair coverage@2 | 1 / 5 = 0.2 |
| Temporal mismatch, fully judged top-1 | 0 / 0 = not measurable |
| False-current exposure, judged current-claim cases | 0 / 0 = not measurable |
| Applicability evidence coverage@2 | 6 / 13 = 0.461538 |
| Closure recognition@1 | 1 / 2 = 0.5 |
| Closure recognition@2 (secondary cutoff) | 1 / 2 = 0.5 |
| Known false-current exposure / all current-claim cases | 1 / 11 = 0.090909 |
| Final insufficient-preservation accuracy | not measurable / not measurable = not measurable |

MRR numerator is exactly 139/20 divided by 14. Raw diagnostic roles covered are 10/20; the reported macro role mean is 7/14. Applicability strata are 5/11 applicable and 1/2 explicit-negative; three unclear cases are excluded. The seven historical diagnostics retain their fixed cutoff. No diagnostic query was substituted for a formal section query.

| Public diagnostic | Coverage result | First complete gold rank |
| --- | --- | --- |
| EF-07 | pass | 1 |
| EF-08 | not a support-classification test | absent/not applicable |
| SY-01 | pass | 2 |
| SY-03 | pass | 1 |
| SY-04 | not a support-classification test | absent/not applicable |
| SY-05 | fail | 1 |
| SY-06 | fail | 1 |
| SY-07 | fail | absent/not applicable |
| SY-09 | pass | 2 |
| SY-10 | pass | 1 |
| SY-11 | pass | 2 |

## Temporal and applicability judgment boundary

All 18 primary and 16 diagnostic top-1 items have incomplete frozen annotation coverage of their full visible text. Fully judged temporal mismatch denominators are therefore 0/0, with null values, not zero-error performance. The nine primary and eleven diagnostic current-claim cases also lack fully judged selected pairs: judged false-current rates are unmeasurable. Known complete excluded temporal passages expose a lower bound of 1/9 and 1/11 respectively. Unjudged cases cannot be treated as safe negatives. No new temporal labels were inferred from surrounding text.

The missing-versus-inapplicable contingency gives unjudged precedence: all three primary insufficient/unclear and all three primary supported/not_applicable cases remain unjudged at complete-output level. Additional wrong-scope negative passages are visible in 1/3 and 2/3 respectively. The diagnostic equivalents are 2/2 and 2/2 unjudged, with additional wrong-scope exposure in 0/2 and 1/2. This does not override the separately measured complete scoped closure hits. It is evidence availability, not final classification.

Insufficient-preservation accuracy is not measurable at retrieval-only baseline. The public primary insufficient case, SY-15, retrieves a resolved narrow issue/closure context without establishing that all limitations are absent. The two private primary insufficient cases are individually documented in the ignored trace, including boundary/excluded/empty/unjudged flags. All selected pairs are non-empty; no credit is awarded for this. Public diagnostic insufficient cases EF-08 and SY-04 likewise receive no positive-gold success or fabricated not_applicable decision.

A definitive temporal comparison requires resolving unjudged outputs prospectively under the frozen-version rules. No comparison, relabelling or follow-on algorithm is performed here.

## Observed failure types

- EF-01: Ranking/selection miss: complete role-compatible gold is available beyond the selected pair. The full selected text includes unannotated tokens; complete-chunk temporal/closure judgments remain unjudged.
- EF-02: Ranking/selection miss: complete role-compatible gold is available beyond the selected pair. The full selected text includes unannotated tokens; complete-chunk temporal/closure judgments remain unjudged.
- SY-08: Category filter excludes at least one frozen gold alternative: SY-CLOSED-NO-FEEDBACK. The full selected text includes unannotated tokens; complete-chunk temporal/closure judgments remain unjudged.
- SY-05: Ranking/selection miss: complete role-compatible gold is available beyond the selected pair. The selected two items do not contain a complete accepted direction pair. The full selected text includes unannotated tokens; complete-chunk temporal/closure judgments remain unjudged.
- SY-06: Ranking/selection miss: complete role-compatible gold is available beyond the selected pair. The selected two items do not contain a complete accepted direction pair. The full selected text includes unannotated tokens; complete-chunk temporal/closure judgments remain unjudged.
- SY-07: Category filter excludes at least one frozen gold alternative: SY-NO-FEEDBACK. The full selected text includes unannotated tokens; complete-chunk temporal/closure judgments remain unjudged.

The researcher-owned archive contributes four supported primary misses at the selected-pair cutoff. The private analysis retains ranking positions, context loss, non-visible alternatives and excluded evidence separately. A strict full-assertion miss is not equivalent to a total lack of semantically relevant wording. No summariser ran, so summariser overconservatism cannot be diagnosed.

The earlier Echo Field source-level reference (Hit@1 4/6, Hit@3 6/6) was not rerun or overwritten. This run uses passage-level frozen gold and production multi-query selection; its Echo Field 3/6 and 6/6 results are different measures and must not be presented as a measured regression or improvement against that historical reference.

## Timing and local model activity: distinct measured requests

Single model load: 402.783 ms, device cpu, 14 Torch threads, 20 logical CPUs. The manifest records exact versions and cached model revision. No dependencies or model files were changed.

| View | Documents | Chunks | Corpus/chunk preparation ms | Document encoding ms |
| --- | --- | --- | --- | --- |
| echo_documented_snapshot | 4 | 12 | 6.176 | 290.655 |
| p96_final_documented | 7 | 49 | 17.186 | 881.880 |
| signal_active | 5 | 5 | 12.242 | 81.872 |
| signal_closed | 7 | 8 | 17.040 | 111.009 |

Preparation timings are one observation per view, so each per-view minimum, median and maximum equals the displayed value (n=1). Model loading is likewise n=1. Document embeddings are reused for every request and repetition in that view.

| Tier / distinct-request timing | Median ms | Min ms | Max ms | p95 ms | n |
| --- | --- | --- | --- | --- | --- |
| production / first_query | 21.731 | 20.935 | 24.240 | 22.933 | 18 |
| production / warm | 22.014 | 20.676 | 28.350 | 23.339 | 540 |
| diagnostic / first_query | 21.607 | 20.871 | 22.384 | 22.174 | 14 |
| diagnostic / warm | 21.993 | 20.569 | 28.350 | 23.577 | 420 |

Each unique request has 30 warm samples; per-request distributions and raw samples are retained in the ignored trace. Public-case request summaries are provided below. Latency is a duration distribution, not an accuracy numerator; the sample count is its denominator. Primary warm median is below the prospective 300 ms target for this machine and run, not a general latency guarantee.

| Public view / section | Median ms | Min ms | Max ms | p95 ms | n |
| --- | --- | --- | --- | --- | --- |
| echo_documented_snapshot / current_intention | 21.999 | 21.415 | 23.364 | 22.854 | 30 |
| echo_documented_snapshot / changes_and_reasons | 21.933 | 21.271 | 27.750 | 23.014 | 30 |
| echo_documented_snapshot / current_vs_superseded | 22.233 | 21.635 | 23.839 | 23.243 | 30 |
| echo_documented_snapshot / relevant_feedback | 21.914 | 21.378 | 26.931 | 22.986 | 30 |
| echo_documented_snapshot / unresolved_tensions | 22.321 | 21.552 | 23.863 | 23.609 | 30 |
| echo_documented_snapshot / possible_next_action | 21.554 | 20.904 | 23.357 | 22.822 | 30 |
| signal_active / current_intention | 22.025 | 21.211 | 27.381 | 23.589 | 30 |
| signal_closed / current_intention | 22.230 | 21.187 | 25.629 | 23.510 | 30 |
| signal_active / changes_and_reasons | 21.735 | 21.083 | 28.223 | 23.917 | 30 |
| signal_closed / changes_and_reasons | 21.799 | 20.676 | 23.037 | 22.860 | 30 |
| signal_active / current_vs_superseded | 22.268 | 21.507 | 23.784 | 23.633 | 30 |
| signal_active / relevant_feedback | 22.023 | 21.364 | 27.830 | 23.520 | 30 |
| signal_closed / relevant_feedback | 22.033 | 20.852 | 25.046 | 24.176 | 30 |
| signal_active / unresolved_tensions | 22.232 | 21.355 | 24.715 | 23.641 | 30 |
| signal_closed / unresolved_tensions | 22.277 | 21.645 | 28.350 | 24.408 | 30 |
| signal_active / possible_next_action | 21.671 | 20.569 | 27.555 | 22.990 | 30 |
| signal_closed / possible_next_action | 21.624 | 20.822 | 24.058 | 22.650 | 30 |
| signal_closed / current_vs_superseded | 22.328 | 21.326 | 25.564 | 24.106 | 30 |

Actual activity: one model load; 1,540 encode calls; 1,610 encoded texts. Four document encode calls cover 74 chunk texts across views; 1,536 query encode calls cover 1,536 query texts (24 unique requests × two queries × 32 runs, including first query and warm-up). OpenAI requests, LLM calls, summary generation, external embedding requests, model downloads, blocked network attempts and protected-data access attempts: all 0.

## Validation and integrity

The first sandbox unit run produced 19 passes and two setup errors because pytest could not create its numbered temporary directory. It did not fail a product assertion. With unchanged tests in a normal local user process and a new repository-external temporary directory, all 21 new tests passed (14.21 s). The full suite then passed: **150 passed in 160.71s (0:02:40)**. A final focused check after timing-boundary/manifest instrumentation passed **21 tests in 11.84s**. The test runner blocked external networking and real participant/cache/review access; both attempted-access counters were zero. Existing tests were not changed or weakened.

Python compilation passed for 18 source/harness/test files without writing bytecode. pip check reported no broken requirements. Frozen manifests/schema/source locators passed before and after the baseline. Final allowlist hash, Markdown-link, public privacy and diff checks are recorded in the Phase 2 experiment log. Real participant materials were neither opened nor rehashed; the integrity allowlist covers only authorised sources, frozen packages, existing code/config/tests and the five thesis drafts.

The gold and sources remain immutable. There is no Phase 3 implementation, production integration, commit, push or participant-study claim.

## Final saved-trace audit — 26 October 2026

**No baseline, retrieval or embedding rerun was needed.** All 34 frozen case IDs were reconciled against corpus view, request execution, ranked results, selected evidence, scoring record and first/warm timing records. Coverage is 18/18 production and 16/16 diagnostic. A metric exclusion never removes the case record. The full 34-ID checklist remains private; the 23 public cases are listed below.

### Why diagnostic latency has 14 distinct requests

The discrepancy is request reuse, not supported-only timing. SY-05 and SY-06 share one historical view/section request; one pair of private diagnostics shares another request. Sixteen diagnostic cases therefore map to fourteen unique requests. Both insufficient diagnostics, EF-08 and SY-04, have a stored ranked result, selected pair, scoring record, first-query duration and 30 warm measurements. They were excluded only from positive-gold hit/MRR/role metrics, not latency. All three production insufficient cases similarly retain their timing records. Production has no within-tier request duplication.

The distinct-request table above remains numerically unchanged. The following additional view weights every case once, expanding shared request measurements through the frozen case mapping. It covers all cases but does not claim 480 independent timed executions.

| Tier / all-case-weighted timing | Median ms | Min ms | Max ms | p95 ms | Contributions | Distinct requests |
| --- | --- | --- | --- | --- | --- | --- |
| production / first_query | 21.731 | 20.935 | 24.240 | 22.933 | 18 | 18 |
| production / warm | 22.014 | 20.676 | 28.350 | 23.339 | 540 | 18 |
| diagnostic / first_query | 21.607 | 20.871 | 22.384 | 22.142 | 16 | 14 |
| diagnostic / warm | 22.075 | 20.569 | 28.350 | 23.577 | 480 | 14 |

Diagnostic distinct-request first/warm sample counts are 14/420; all-case-weighted contributions are 16/480. Production is 18/540 under both scopes. The diagnostic warm median changes from 21.993 ms (request weighting) to 22.075 ms (case weighting) solely because the shared measurements receive different weights. No stored latency, ranking, accuracy value or principal conclusion changed.

### Exact model and encode accounting

- Four unique corpus views each supply six section requests: `4 * 6 = 24` unique requests for 34 cases.
- Each request executes once initially, once for warm-up and 30 timed times: `24 * 32 = 768` request executions.
- Each execution uses two unchanged queries with one text per encode: `24 * 2 * (1 + 1 + 30) = 1536` query encode calls and **1536 query texts**.
- Equivalent timing-phase accounting: `48 first + 48 warm-up + 1440 timed warm = 1536` query encodes.
- Production attribution: `18 * 32 = 576` executions, or `18 * 2 * 32 = 1152` query encodes.
- Diagnostic attribution: `14 * 32 = 448` executions, or `14 * 2 * 32 = 896` query encodes.
- Eight cross-tier shared requests contribute `8 * 32 = 256` shared executions / `8 * 2 * 32 = 512` shared query encodes. Union: `576 + 448 - 256 = 768` executions; `1152 + 896 - 512 = 1536` encodes.
- One cached local model instance; four document encode calls with `12 + 49 + 5 + 8 = 74` document texts. Total encode calls: `4 + 1536 = 1540`. Total encoded texts: `74 + 1536 = 1610`.
- Document embeddings are reused; saved results/timings are reused between matching cases. Query embeddings are **not** reused between first, warm-up or timed executions.

The observed counters match these formulas exactly. The manifest retains execution-time source/test hashes and separately records the audited reporting artifact hashes; the original raw trace remains byte-identical.

### Denominator audit

The immutable Phase 1 Scoring contract / Primary and secondary reporting contract already specifies supported-only Hit@1, Hit@3, MRR and required-role/all-role coverage. Excluding insufficient cases was prespecified, not selected after results. Pair, applicability, closure and current-claim metrics have their own frozen eligibility rules.

| Metric family | Production denominator | Diagnostic denominator | Exclusion basis |
| --- | --- | --- | --- |
| Hit@1 / Hit@3 / MRR / macro role / all-required-role coverage | 15 | 14 | 3 / 2 insufficient cases have no affirmative gold |
| Required pair coverage | 3 | 5 | No required direction pair |
| Applicability evidence coverage | 14 | 13 | 4 / 3 unclear applicability cases |
| Closure recognition@1 and @2 | 3 | 2 | Not an explicit scoped inapplicability case |
| Known false-current exposure lower bound | 9 | 11 | 9 / 5 cases make no affirmative current claim |
| Fully judged temporal / false-current rate | 0 | 0 | Unjudged outputs; not measurable, not zero error |

All metric numerators, denominators, eligibility/exclusion details, case scores and project/section/stratum breakdowns were independently recomputed from the saved trace and matched the pre-audit results. No gold, source or production behavior was changed.

| Public case | Tier | View / section | Execution, rankings, selection, score, latency | Warm n |
| --- | --- | --- | --- | --- |
| EF-01 | production | echo_documented_snapshot / current_intention | all present | 30 |
| EF-02 | production | echo_documented_snapshot / changes_and_reasons | all present | 30 |
| EF-03 | production | echo_documented_snapshot / current_vs_superseded | all present | 30 |
| EF-04 | production | echo_documented_snapshot / relevant_feedback | all present | 30 |
| EF-05 | production | echo_documented_snapshot / unresolved_tensions | all present | 30 |
| EF-06 | production | echo_documented_snapshot / possible_next_action | all present | 30 |
| EF-07 | diagnostic | echo_documented_snapshot / current_vs_superseded | all present | 30 |
| EF-08 | diagnostic | echo_documented_snapshot / possible_next_action | all present | 30 |
| SY-01 | diagnostic | signal_active / current_intention | all present | 30 |
| SY-02 | production | signal_closed / current_intention | all present | 30 |
| SY-03 | diagnostic | signal_active / changes_and_reasons | all present | 30 |
| SY-04 | diagnostic | signal_closed / changes_and_reasons | all present | 30 |
| SY-05 | diagnostic | signal_active / current_vs_superseded | all present | 30 |
| SY-06 | diagnostic | signal_active / current_vs_superseded | all present | 30 |
| SY-07 | diagnostic | signal_active / relevant_feedback | all present | 30 |
| SY-08 | production | signal_closed / relevant_feedback | all present | 30 |
| SY-09 | diagnostic | signal_active / unresolved_tensions | all present | 30 |
| SY-10 | diagnostic | signal_closed / unresolved_tensions | all present | 30 |
| SY-11 | diagnostic | signal_active / possible_next_action | all present | 30 |
| SY-12 | production | signal_closed / possible_next_action | all present | 30 |
| SY-13 | production | signal_closed / changes_and_reasons | all present | 30 |
| SY-14 | production | signal_closed / current_vs_superseded | all present | 30 |
| SY-15 | production | signal_closed / unresolved_tensions | all present | 30 |

The other 11 researcher-archive case records (six production and five diagnostic) passed the same checklist and remain private. Gold is single-researcher-confirmed with no inter-rater agreement estimate. This audit neither classifies final support/applicability nor extends the benchmark to formal participant projects.

### Initial audit validation gate

On 26 October 2026, the updated baseline audit suite passed: **26 passed in 20.95s**. The required full suite did not pass: **4 failed, 151 passed in 85.64s (0:01:25)**. All four failures are the existing `test_four_synthetic_project_contexts_preserve_cache_validation_and_append_only_reviews` parameter cases in `tests/test_evidence_guidance.py`, at line 158. They raised FileNotFoundError when reading an expected cache file inside the newly created repository-external synthetic workspace. These are synthetic fixtures, not real participant records. The root cause has not been established; this report does not classify it as a production regression or silently dismiss it as an environment issue.

During that initial audit, no existing test or production file was changed, no failing test was skipped, and no retry or baseline rerun was performed after the failure. Compilation passed for 18 files and pip check found no broken requirements. Both test-run boundary counters were zero. Accuracy/ranking reconciliation passed, but the all-tests-pass commit condition was then unmet. Staging, commit and push were stopped. The earlier successful test results above describe the 25 October session and do not replace this failed initial audit validation.

## UI failure follow-up and final validation — 26 October 2026

The four original FileNotFoundError failures did not recur in the authorised isolation matrix. Each process used a new ignored temporary directory, with its own basetemp and process-local temporary environment. Existing tests and production code were unchanged. No assertions were weakened, and no tests were skipped or marked xfail.

| Step | Scope | Pytest result | Exit | Process seconds |
| --- | --- | --- | --- | --- |
| A | Evidence-guidance file only | 24 passed in 65.71s (0:01:05) | 0 | 66.297 |
| B | Four previously failing nodes only | 4 passed in 41.50s | 0 | 42.129 |
| C | Existing suite, excluding the new baseline tests | 129 passed in 154.48s (0:02:34) | 0 | 154.974 |
| D | Baseline then evidence guidance | 52 passed in 69.61s (0:01:09) | 0 | 70.192 |
| E | Evidence guidance then baseline | 52 passed in 67.82s (0:01:07) | 0 | 68.422 |
| F1 | Complete suite, first consecutive run | 157 passed in 182.29s (0:03:02) | 0 | 182.947 |
| F2 | Complete suite, second consecutive run | 157 passed in 170.76s (0:02:50) | 0 | 171.392 |

At the cache-read boundary in all valid matrix runs, the synthetic files and their parent directories existed and preparation had returned ready. Observed removal events affected pytest's setup-time `current` links, not the synthetic project directories. The four parameter labels refer only to freshly created synthetic workspaces; no real participant files were read or rehashed.

A separate filesystem-only probe reproduced FileNotFoundError for a 260-character temporary filename while a 259-character filename succeeded. The original cache's reconstructed final and temporary path lengths were 256 and 260 characters. This supports a path-length explanation, but **root cause unconfirmed** remains the finding for the original run: its complete traceback and preparation-time write exception were not retained. Missing evidence has not been reconstructed as fact. The first instrumented A attempt also exposed a KeyError in the external diagnostic observer; that attempt was retained as invalid instrumentation, and A was rerun after fixing only the observer. It was not another product failure.

The read-only audit separately found that importing the new baseline module and collecting its tests left additions in `sys.path`. The new harness now scopes its production imports and restores the path; test bootstrap uses a restoring monkeypatch context. Two added regression tests verify import-time absence of writes, environment/cwd changes, network activity and model imports, and path restoration after success or exception. This corrects import hygiene without claiming it caused the original cache failures. No model, query, selection, ranking or scoring behavior was changed.

The final baseline suite contains 28 tests. D and E each passed all 52 baseline/evidence-guidance tests; both consecutive complete runs passed all 157 tests. In-memory compilation passed for 18 files, and pip check found no broken requirements. Saved rankings, all 34 case results, aggregate accuracy metrics, frozen gold and the original trace remain unchanged. Execution-time hashes remain in the manifest alongside separate final artifact hashes. This follow-up did not rerun the baseline or perform real retrieval, embedding, LLM, summary or OpenAI calls; existing offline fixture doubles were used only by tests. Full diagnostic outputs remain private. No Phase 3 method was implemented.
