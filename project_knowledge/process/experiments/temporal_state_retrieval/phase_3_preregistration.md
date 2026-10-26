# Phase 3A: frozen explicit record-state metadata preregistration

Status: **researcher_confirmed — locally frozen; execution not authorised**

Candidate: `record_state_selection_v1`; freeze version: `phase_3a_metadata_v1`.

Reviewed by Fuzhe Zhang on 26 October 2026. Confirmation follows the researcher's conditional authorisation and the successful candidate-pool, query-order and static method audit. This is researcher confirmation, not independent annotation or inter-rater agreement.

Prepared: 26 October 2026. Starting checkpoint: `e48acc6fc02840382b9d920621c88363f171028d`.

## Question and scope

Does explicit record-level project-state metadata improve retrieval of evidence about current, historical, superseded, closed and unresolved project states, compared with the frozen semantic baseline?

This is a post-study technical experiment on the public Echo Field demonstration, the private researcher-owned archive and synthetic Signal Loom. It does not reopen participant research. It concerns evidence selection, not automatic project understanding, true-state classification, final summary accuracy, recommendations or replacement of user judgement. No source, production component, frozen gold, baseline result or thesis is changed. This package contains a frozen design and metadata, not a selector implementation or new retrieval results.

The [Phase 1 protocol](experiment_protocol.md) and [Phase 2 report](../../../../outputs/test_results/temporal_state_retrieval_baseline/baseline_report.md) remain immutable. The baseline is already visible to the designer: this is an exposed-benchmark prospective candidate comparison, not a blinded or held-out test. Metadata is grounded in source document function, not assigned to make failed cases pass. No independent annotation or inter-rater agreement is claimed.

## Fixed control and one candidate

Control is the frozen Phase 2 production semantic pipeline. Preserve the loader, 120-word windows, 30-word overlap, all-MiniLM-L6-v2 snapshot, normalisation, both configured queries per section, their order, original cosine scores and tie order, category filtering, chunk deduplication, 1,200-character excerpts and at most two selected items. Neither canonical questions nor internal query pairs are rewritten. Phase 2 output is the immutable comparison reference, never an output destination for Phase 3.

Candidate generation is identical. There is exactly one candidate: a deterministic record-state layer operating **only on final selection**, after generation and category filtering. It does not change embeddings, raw rankings, scores, chunk boundaries, source text or semantic query inputs. It has no learned or tunable weight, score threshold, lexical rules, date decay or LLM. No alternative variant is tried in the same registration.

### Candidate pool and ordering contract

For each of the two original queries, `top_k = N`, where N is the number of chunks in that request's frozen eligible corpus view, exactly as in production. All category-eligible results in each returned list are available. There is no added top-5/top-10 truncation or pool expansion. Phase 2 records N as 12 for Echo Field, 49 for the researcher archive, 5 for the Signal Loom historical view and 8 for its latest view; these are existing corpus counts, not new measurements. The union contains each eligible chunk once; selection still returns at most two distinct chunks. Empty pools remain empty.

### Audited distinction: retrieval, selection and evaluation

The [retriever](../../../../src/retrieval.py) has a default top_k of 3 and returns min(top_k, corpus size) results. That default is not used by this baseline. The [production selection function](../../../../src/reentry_brief.py) requires total_chunks, calls retrieve with top_k=total_chunks, and passes the complete returned query_results to select_evidence with limit=total_chunks. The latter helper's default limit=2 is likewise overridden. The outer retrieve_diverse_evidence limit=2 controls the final output, not the candidate input.

The [Phase 2 adapter](../../../../experiments/temporal_state_retrieval/baseline.py) passes the actual len(chunks) through production_selection into total_chunks. RecordingRetriever returns the delegate's list unchanged while retaining it. Only after selection does ordered_trace apply the same category filter to those recorded calls and construct its selected-pair-plus-tail evaluation ranking. There is no deeper retrieval call for evaluation. The [frozen run manifest](../../../../outputs/test_results/temporal_state_retrieval_baseline/run_manifest.json) separately records all-chunk query_top_k and selected_evidence=2.

All 24 saved view/section requests were counted without running retrieval. Each saved query contains category-eligible results only, not a separately persisted unfiltered list. Thus raw returned counts N are established by the actual source call chain and corpus manifest; filtered counts below are directly observed in both query lists. This distinction avoids pretending the trace independently logged a top_k argument that it did not store.

| View | Corpus N / actual top_k / input to select_evidence, per query | Category-eligible count E per query, S1–S6 | Cross-query occurrences before / unique after deduplication | Evaluation-only ranked count, S1–S6 |
| --- | --- | --- | --- | --- |
| Echo Field latest | 12 / 12 / 12 | 6, 6, 9, 6, 12, 9 | 2E / E | 6, 6, 9, 6, 12, 9 |
| Researcher archive latest | 49 / 49 / 49 | 21, 44, 49, 28, 49, 33 | 2E / E | 21, 44, 49, 28, 49, 33 |
| Signal Loom historical | 5 / 5 / 5 | 2, 4, 5, 3, 5, 4 | 2E / E | 2, 4, 5, 3, 5, 4 |
| Signal Loom latest | 8 / 8 / 8 | 4, 5, 8, 4, 8, 7 | 2E / E | 4, 5, 8, 4, 8, 7 |

Both query lists have the same eligible chunk-ID set but can have different scores/order. There are no within-query duplicates. Every final baseline selection has two distinct chunks. The evaluation-only list has E unique items because it is a reordered union of the same eligible results. Equal membership does not make its selected-first ordering a valid selector input. Candidate construction must take the original per-query channel, never ordered_evidence or its deeper positions. The manifest preserves counts and code/raw-trace hash commitments; no private excerpt, filename, chunk ID or case outcome is published.

Within each query list, retain descending cosine order and the original production tie order. Do not alphabetically sort sources, record IDs or dates to break ties. A state preference is a stable partition of that original list. Query 1 contributes its highest-ranked eligible unused item, then query 2 contributes its highest-ranked eligible unused item. If fewer than two are selected, use the production maximum-score union fill, retaining its first-encounter tie order. For the state-preference rule, apply the same two-level stable partition to this fill. The first equal-score occurrence of a chunk remains its representative, matching production; the layer cannot invent a different score.

The snapshot family is `{current_snapshot, final_snapshot, closure_record}`. These are document functions, not assertions that every sentence remains current, that all work is closed, or that a later dated record supersedes another. The three states have equal priority. Other states are not removed. There is no numeric score bonus.

### Six fixed section rules

| Section ID | Preregistered candidate selection |
| --- | --- |
| current_intention | Apply the two-level stable preference: snapshot-family records first, all other records second; then use the query-by-query selection and union fill above. Closure may provide evidence about absence of an active aim, but the selector emits no such conclusion. Historical fallbacks retain their historical provenance and are never relabelled current. |
| changes_and_reasons | Keep baseline selection exactly. A record-level state cannot establish a change, its cause or which two passages explain it. No latest-only preference is permitted. |
| current_vs_superseded | If the category-eligible union contains both a snapshot-family record and a distinct historical_record, choose query 1's highest-ranked snapshot-family chunk, then query 2's highest-ranked historical_record chunk from a different record. Both lists retrieve the full eligible corpus, so both groups are available when this condition holds. Preserve each list's cosine/tie order. Otherwise keep the entire baseline pair; do not partially rewrite it. This is a cross-document-function pair, not proof of replacement or authoring chronology. |
| relevant_feedback | Keep baseline selection exactly. A closure record can remain eligible only under the original category filter; it receives no special promotion. Whole-record closure cannot establish whether a passage explicitly denies feedback, and absence of feedback files proves nothing about external feedback. |
| unresolved_tensions | Apply the same two-level snapshot-family preference as S1. A current/final overview or closure may offer a later state description, but a closure/repair is not evidence that every issue is resolved. No issue is labelled unresolved or resolved by the selector. An older active snapshot can still be selected; this known limitation is evaluated, not silently repaired using gold. |
| possible_next_action | Keep baseline selection exactly. Metadata cannot distinguish a confirmed task from a conditional possibility or an obsolete task within one record. No undated task or future possibility is promoted into a current commitment. The layer creates neither action labels nor recommendations. |

The baseline-preserving rules for S2, S4 and S6 are deliberate boundaries of record-level information. S1/S5 promotion can still select irrelevant or outdated passages from a useful document; S3 can pair records without the required replacement assertion. These are possible negative outcomes, not grounds for adding a semantic classifier, selecting a more favourable rule or modifying metadata after execution.

### S3 query-order evidence

For the current_vs_superseded definition, get_section_queries returns these configured strings in this order:

1. What project direction or interaction method is explicitly described as current or still in use?
2. What project direction is explicitly described as superseded, replaced, no longer current or future work?

The exact text is pinned against the production syntax tree, Phase 2 manifest and saved query strings. Query 1 has an explicit current/still-in-use focus; it does not literally say final. Query 2 explicitly addresses replaced/non-current directions, but also includes future work: it is not a pure historical query. They are not two interchangeable generic relevance questions. The S3 query-order rule is retained on this textual basis, not on gold roles. A final_snapshot is a document function and a historical_record is not proof of replacement; neither a conditional future nor merely older text receives a superseded label. Category membership, cosine order and the fallback baseline pair remain unchanged.

## Record metadata contract

Use the [closed schema](../../../../tests/fixtures/temporal_state_metadata/record_metadata.schema.json). Every record has exactly eight fields: record_id, project_id, record_state, record_date, sequence_position, state_basis, state_scope and source_category. Envelope fields identify package version, confirmed review status, reviewer, date and review basis; they do not enter the selector. Stable record IDs are joins to existing source records, not evidence or chunk IDs. Source filenames and hashes remain in the source inventory, outside selector payloads.

| record_state | Document-level meaning |
| --- | --- |
| historical_record | A retrospective event/test/repair report or dated diary compilation. This does not assert that all its claims are obsolete or that its authoring date precedes the snapshot. |
| current_snapshot | A document explicitly presented as a current/active state overview at its supplied reference. It need not describe today's activity and remains this document type after a later closure. |
| final_snapshot | An explicit final-version overview; neither present-day development nor project closure follows automatically. |
| closure_record | A document explicitly dedicated to closure/archive status. It cannot settle every section or every limitation. |
| undated_record | No record date and no unambiguous whole-document snapshot, closure or retrospective-report designation. Mixed ongoing/history records and unplaced fragments remain here. |
| unknown | Document function is not established, or runtime metadata is missing. |

`state_basis` is one of explicit_heading, explicit_source_statement, explicit_date, supplied_manifest or unknown. A date alone does not prove historical/current status. `state_scope` records a short source-grounded justification and limits for human review; the selector must not parse this free text. `record_date` is an explicitly stated record date, or the last included dated entry in a compilation, never a filesystem date. Missing dates are null. `sequence_position` is the existing supplied-catalogue ordinal, not a proved chronology, and is never a ranking feature. Same-day records are not ordered by guessed times.

Metadata contains no gold evidence IDs, roles, temporal annotations, support/applicability labels, case outcomes, rankings, score-based rationales or section-specific exceptions. There is no whole-record superseded, unresolved or next_action state: these archives mix assertions whose scope must remain visible in the source. The undated Current State and Final Overview functions justify their types, not their true creation order. Imported provenance headers identify copies; they are not source-state evidence.

Missing metadata maps to unknown in the design and preserves semantic fallback order. Completeness validation must nevertheless fail before an authorised experimental run if an expected record lacks metadata; missing annotations must not silently change the registered experiment. Multiple records of the same state remain in cosine/tie order without a newest-first rule. Closure and final/current snapshots are equal-priority document functions; no conflict is automatically resolved. The selector does not read dates or ordinals, so a dated old record gains no priority merely for having a date.

## Fourteen audited design decisions

| Question | Fixed proposal |
| --- | --- |
| 1. How large is the candidate pool? | All N chunks per original query, followed by the unchanged category filter; no new numeric k. |
| 2. Ranking or selection? | Final two-item selection only; raw cosine rankings remain unchanged. |
| 3. Missing metadata? | Unknown semantic fallback in the contract, but fail experiment preflight until expected-record completeness is restored prospectively. |
| 4. Multiple same-state records? | Original per-query cosine order and original ties; no newest-first or record-name preference. |
| 5. Closure and final snapshot together? | Equal snapshot-family priority; original semantic order decides. No state conflict is declared resolved. |
| 6. Equal cosine scores? | Retain each query's production order and the production union's first-encounter tie order. The evaluator's frozen tail has its separate chunk-ID tie rule. |
| 7. Old record with a date? | Dates and catalogue ordinals are not selector features, so their presence cannot promote it. |
| 8. Newer but less direct change/reason? | S2 remains exactly baseline, without state/date preference. |
| 9. S3 pairing without inventing supersession? | One snapshot-function and one retrospective-function record when both exist; no assertion, role or replaced label is emitted. |
| 10. No gold exposure? | Strict selector payload projection and file/network isolation; evaluation joins frozen annotations only afterwards. |
| 11. Proof of pre-run freeze? | Researcher decision and versioned checksums are now recorded locally. A committed freeze ancestor is still required before any authorised execution. |
| 12. Historical exclusion? | Filter chunks and metadata by the frozen eligible-record allowlist before selection; exclude the unplaced and future records. |
| 13. Category changes? | None; rejected categories cannot be rescued by a state tag. |
| 14. top-k or evidence-count changes? | None; N remains the full eligible corpus per query and output remains at most two distinct chunks. |


## Four corpus views and temporal boundaries

The frozen eligible-record allowlist is applied before loading/chunking and before attaching metadata. All six primary sections in a project use its full latest supplied corpus. Echo Field has its four records; the researcher archive has its seven permitted records. Their snapshot anchors are semantic supplied-state conventions, not proven authoring dates. Signal Loom latest includes its seven records; its historical view ends at the active snapshot and includes only records 01–05. The undated fragment 06 and closure 07 are absent from both historical chunks and historical metadata payloads. No later metadata, closure flag or record count can enter that historical selector invocation.

Task-context projection may contain view ID, project ID, section ID, as-of record and eligible record IDs. These are fixed corpus boundaries shared by control and candidate, not target annotations. State preferences are not retuned per view or per case. Historical/diagnostic questions never replace production section queries. Unknown dates remain unknown; sequence alone does not prove historical availability. The [freeze manifest](../../../../tests/fixtures/temporal_state_metadata/freeze_manifest.json) records the public view boundary contract and source hashes; private source locations remain private.

## Gold-leakage boundary and prospective freeze

Source metadata was drafted by directly reading the approved records' headings, stated dates and document-level descriptions. The old record catalogue supplies stable identity/source mapping only. Source hashes check that these readings concern unchanged originals. The disclosed prior exposure to benchmark results cannot be undone; this is not a blind annotation exercise.

In a later authorised implementation, retrieval and selection must be separated from evaluation. The selector receives only section ID, the original ordered category-filtered candidate lists (opaque chunk IDs, record IDs and scores, with tie order preserved by array position), and the record_state projection for eligible records. It receives no excerpts for semantic parsing, free-text state_scope, source paths, dates, ordinals, case IDs, tier, gold, expected roles or result files. Candidate output is chunk IDs/order only. A restricted selector process must have no file/network access; the evaluator joins excerpts and frozen gold only after selection is final. A process contract test must reject extra payload fields before any run. Merely promising not to use an in-memory gold object is insufficient.

The runtime input is now a closed JSON Schema definition, selector_input, inside the metadata schema. It accepts exactly section_id, two ordered_eligible_candidates arrays of {chunk_id, record_id, score}, and eligible_record_states as a record_id-to-enum-string mapping. The mapping contains exactly the record IDs represented in those category-eligible candidate lists, with no extra records. Array position preserves ties; source categories are checked upstream and are not passed into the selector. Additional properties are rejected at every object boundary. Full metadata objects, rationale, state_basis, state_scope, record_date, sequence_position, project IDs, evidence roles, support/applicability, expected evidence and case IDs cannot be embedded in the mapping or candidates. No automatic ignoring of a leaked object is allowed.

Static contract tests exercise accepted payloads and rejection at each nested boundary, and distinguish the per-query source channel from ordered_evidence. They validate data shapes and provenance, not a selection algorithm. A future adapter must construct a fresh allowlisted payload, validate it against selector_input, and assert exact candidate IDs, scores and order against the production query channel before dispatch. The isolated selector cannot open the complete metadata JSON or evaluator files. Phase 3B requires an integration test of that actual adapter/process boundary before execution; the present schema does not claim to test an implementation that does not yet exist.

The only existing source-to-ID mapping is the corpus identity join. Metadata and view projection are allowlisted at the adapter boundary, not passed by serialising the benchmark object. The same request serves cases sharing a view/section; no case-specific selection occurs. Category membership and project identity must match the source inventory, or validation fails. Formal participant materials, reviews, caches and assignments are forbidden inputs. Thesis/study results are not training or parameter-selection data.

All 18 records are now **researcher_confirmed**, with their eight record fields unchanged from the reviewed candidate. Confirmation is recorded at package level and applies to every contained record. The local freeze is phase_3a_metadata_v1. The public manifest hashes the other seven public files, adds a canonical-JSON self digest with the digest value omitted, and commits to the private metadata without exposing its path/content. The private manifest hashes the private metadata and public manifest and retains protected-input commitments. Both pin the prior candidate checksums. The public manifest uses the final filename freeze_manifest.json; the ignored private metadata retains its existing filename. This naming change does not alter metadata or the registered design.

Publication of the frozen design is authorised following final validation; implementation and execution remain unauthorised. A later authorised execution must refer to a committed freeze ancestor, verify hashes and first pass the actual adapter/process-isolation contract tests. Any post-result correction requires a new preregistration and new version preserving its predecessor; no silent overwrite or same-version retuning is permitted.

## Evaluation and fixed success gate

The sole primary population remains 18 production cases; 16 diagnostics are secondary and never pooled or used to choose parameters. Preserve Phase 2 exact-match scoring, role/temporal requirements, cutoff denominators and unjudged handling. Selected items occupy evaluation ranks 1–2; the remaining eligible items use the unchanged Phase 2 max-cosine/chunk-ID tail. This evaluation order is distinct from the unchanged raw retrieval ranking. Hit@3 changes can therefore reflect selection promotion, not better embeddings. Null temporal denominators remain not measurable; no new labels resolve unjudged outputs retrospectively.

| Primary gate, all required | Frozen baseline | Candidate requirement |
| --- | --- | --- |
| All-required-role coverage@2 | 8/15 | At least 10/15 |
| Preserve baseline production evidence-coverage passes | Existing frozen pass set | Lose none of the cases that satisfy all required roles and any required pair |
| Hit@3 | 10/15 | At least 10/15 |
| Required-pair coverage@2 | 2/3 | At least 2/3; report 3/3 as a target, not a different denominator |
| Closure recognition@2 | 2/3 | At least 2/3; target 3/3 |
| Known false-current exposure lower bound | 1/9 | No more than 1/9; do not call this a complete error rate |
| Future-record leakage | None allowed | Zero; otherwise the run is invalid |
| Production warm median, distinct-request scope | Approximately 22.01445 ms | At most 44.03 ms, plus absolute timings and environment disclosure |
| Primary improvement | Primary tier only | Diagnostic gains cannot satisfy any primary gate |

The displayed latency threshold is 44.03 ms, twice the frozen production warm median of approximately 22.01445 ms rounded for prose. JSON retains the original machine-readable median and its exact double for the comparison; rounding must not silently relax that boundary. A later authorised run uses the same environment/model and timing boundary, one first query, one warm-up and 30 warm repetitions per unique view/section, in fixed sorted round-robin order. Include candidate selection overhead, exclude scoring, and separately report preparation, selection overhead and p95. Do not substitute selector-only timing for end-to-end retrieval. Phase 2 timings remain untouched. If environment comparability cannot be established, mark the latency gate unassessable and do not claim success. No timing or encoding is performed in Phase 3A.

Report Hit@1, Hit@3, MRR, macro required-role coverage, all-required-role coverage, pair coverage, applicability evidence coverage, closure recognition, temporal mismatch, known false-current exposure, insufficient-preservation boundaries and latency separately by tier. Applicability/abstention classification accuracy remains out of scope. Per-case baseline-to-candidate reporting uses gained, lost, unchanged pass and unchanged fail only for cases with a defined evidence-coverage pass criterion. Insufficient cases are separately reported as evidence-boundary/unjudged cases, not assigned invented pass/fail. Private case-level rows stay private; public output may disclose aggregates and public cases only.

This is a new, explicitly prospective Phase 3 success gate following the disclosed baseline. The earlier Phase 1 comparison-family protocol demanded strict pair improvement, all three closure hits and role gains across at least two projects; its historical criteria are not edited or represented as satisfied by this different gate. Report a separate legacy-criteria audit when results exist. The targets of 3/3 above are not silently substituted for the registered minimums. No new claim of Phase 1 success is justified merely by meeting Phase 3. Fixed category filtering may prevent closure evidence from being eligible; metadata cannot repair that limitation.

The manifest saves Phase 1 original benchmark criteria separately from Phase 3 candidate-improvement criteria. Every future results report must state two distinct outcomes: whether the candidate met the Phase 3 criteria and whether it met the complete original Phase 1 criteria. Both are currently not evaluated because no candidate has run. If all Phase 3 gates pass, the permitted conclusion is only: "met the preregistered Phase 3 improvement criteria". This does not mean it passed the complete Phase 1 benchmark, solved temporal-state retrieval or achieved reliable project-state understanding.

If some gains coexist with losses or other unmet gates, record a mixed experiment; without qualifying gains, record a negative experiment. A one-case gain with a one-case loss is never success. An invalid/leaking/incomplete run remains an invalid run, not a candidate success. No significance tests or generalisation to participant projects are justified.

## Negative outcomes and stop boundary

Preserve every result and failure. Do not edit gold, source text, metadata, priorities or rules after viewing candidate outcomes. Do not run a second corrected candidate under this registration. Any v2 requires an explanation of v1, a new preregistration and separate commit before execution. Either outcome can inform later technical writing, but no thesis is edited in Phase 3A and no outcome is claimed in advance.

This phase stops at publication of the freeze recorded in the [researcher review and method audit](phase_3a_researcher_review.md). No selector, baseline run, embedding model, API, summary or new participant study is authorised. Static schema, identity, completeness, prohibited-field, source-integrity and historical-boundary checks validate this design package. Publication validation also runs the existing offline test suite; it does not execute a candidate or load an embedding model.
