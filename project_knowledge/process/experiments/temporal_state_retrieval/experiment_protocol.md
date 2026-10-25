# Temporal and project-state-aware retrieval: Phase 1 protocol

Status: **researcher_confirmed — formally frozen gold**

Version: phase_1_gold_v1

Researcher confirmation and freeze: 25 October 2026

Reviewed by: Fuzhe Zhang

Review basis: manual review of case summaries, evidence roles, applicability, temporal scope and ambiguity notes. Assistant-prepared annotations were confirmed by the researcher; this is not independent expert annotation, and inter-rater agreement was not assessed.

Production checkpoint: `6e959e9554701e74355f31b4957db2529d47fb06`

## Purpose and boundary

This is an independent post-study technical extension. It does not reopen the completed participant studies, revise their findings, validate Iteration 3 with new participants, or change the frozen production system or thesis drafts.

Phase 1 supplies a reviewable benchmark with independent support, applicability, temporal and role annotations, a comparison protocol and success criteria. No retrieval comparison has been run. There are no model outputs, performance results, embeddings, generated summaries or participant responses in this package. Source reading and static data validation are distinct from running a retriever.

The permitted corpora are the public Echo Field demonstration, a private researcher-owned self-test archive, and the entirely invented Signal Loom archive. Formal participant materials are not benchmark inputs. Private annotations remain outside versionable files. Existing source files, tests and configuration remain unchanged; the new files under tests are data fixtures, not executable tests.

## Prior work and why a new benchmark is needed

The recoverable local role-selection experiment, commit `322f7e9d956cde8916c3c8d56b972ed80267a761`, added role queries, bounded candidates, deterministic role-first selection and reciprocal-rank-fusion fallback. Its recorded 121 passing engineering tests established mechanics, not semantic acceptance. It did not consistently recover the required evidence. The implementation is not reused here.

The subsequent private structural audit compared fixed windows, heading segmentation, lexical ranking, semantic/lexical fusion and a heading-prefix diagnostic. Some explicit passages became easier to retrieve, but no tested main configuration satisfied all acceptance conditions. Exact-anchor misses also understated some valid alternative evidence. Dates and headings improved provenance in some cases; they did not establish that a historical task remained active.

| Failure class | Operational distinction |
| --- | --- |
| Ranking failure | Suitable evidence is present and eligible but falls below the selected positions. |
| Query mismatch | The query emphasises a different aspect from the case requirement; related text outranks the needed evidence. This is an explanatory diagnosis, not an independent numerical proof. |
| Chunk-boundary problem | Necessary wording, heading scope or date is split or mixed; record content loss separately from context ambiguity. |
| Missing evidence | Complete corpus reading cannot establish the requested claim. Better ranking cannot supply it. |
| Temporal/project-state interpretation | Related text has the wrong applicability, completion status, condition or scope. Relevance is not current-state support. |
| Summariser conservatism | Adequate, correctly scoped evidence reached a summariser but it declined support. Ranking failure alone cannot establish this explanation. |

Earlier diagnostics did not show excerpt truncation or summariser overconservatism as the cause of every failure. They must not be used as blanket explanations. The private review retains source-specific qualifications; this public protocol contains no private excerpts or rankings.

## Benchmark tiers and primary coverage

The frozen gold set has **34 cases: 18 production and 16 diagnostic**, across three projects. Each project has exactly one production case for each of the six canonical ProjectOS sections. The public package contains 23 cases (8 Echo Field, 15 Signal Loom); 11 researcher-archive cases remain private.

Twelve existing cases were canonicalised and six new canonical cases were added. The other sixteen v2 cases retain their diagnostic questions. Keeping 28 would require removing distinct earlier diagnostics or making historical/narrow questions stand in for broad latest-state tasks. No source meaning or case count was adjusted for class balance. candidate_v2_question and case_origin preserve the migration; they are evaluator-only provenance, never retrieval inputs.

| Tier | Inputs and purpose | Use in conclusions |
| --- | --- | --- |
| production | Exact section question from the frozen brief_schema.py; complete eligible latest supplied corpus; six sections per project | Sole primary performance population and success-gate basis |
| diagnostic | Narrow failure probe; explicit latest or historical reference | Secondary failure analysis only; never pooled into primary performance |

Production counts: 15 supported, 3 insufficient; 11 applicable, 3 not_applicable, 4 unclear. Three cases are insufficient/unclear and one is supported/unclear. There are 3 production direction-pair cases and 3 production closure cases. Diagnostic counts: 14 supported, 2 insufficient; 11 applicable, 2 not_applicable, 3 unclear. One retrospective diagnostic is supported/unclear. Diagnostic pair and closure denominators are 5 and 2 respectively. These are researcher-confirmed annotations, not observed performance scores.

Primary evaluation always covers the fixed 18 latest-state cases. No historical production snapshot is included. A future historical production analysis would be a separately declared exploratory population, never part of the eighteen.

## Explicit reference state, record sequence and eligibility

Every case requires benchmark_tier, reference_state, as_of_record and eligible_record_ids. Each source has a stable record ID, sequence, explicit last-included date where available, raw-byte hash and a stated sequence basis in record_catalog. No original source was edited to add metadata.

All current, historical, superseded, completed, future_conditional and unknown labels are interpreted relative to the case/context as_of_record. Current does not mean the experiment date. Record sequence denotes the declared supplied-corpus order; it is not proof of authoring chronology when dates are absent.

| Project/view | Reference | Eligible records | Boundary |
| --- | --- | --- | --- |
| Echo Field latest | EF-R04, explicit Current State record; undated | EF-R01–EF-R04 | Reference authority comes from its current-state designation; undated authoring chronology is unknown. |
| Researcher archive latest | RS-R07, undated final-version overview | RS-R01–RS-R07 | The final-state description anchors the supplied state; neither a closure date nor ongoing work today is inferred. |
| Signal Loom active diagnostic | SY-R05, 12 February 2026 | SY-R01–SY-R05 | Exclude SY-R06 because its availability at the cutoff is unproved; exclude later closure SY-R07. |
| Signal Loom latest | SY-R07, 20 February 2026 closure | SY-R01–SY-R07 | Includes all supplied records, without inventing a date for the fragment. |

Undated Echo and researcher records use explicitly declared manifest sequences. Their anchors are documented state summaries, not asserted latest file-creation times; the researcher accepted this convention on 25 October 2026 without claiming actual creation dates or full authoring chronology. All primary cases use their project's entire latest eligible record set. Existing section category eligibility is retained as a separate production behavior, not used to hide records from the manifest.

Historical snapshots must declare a cutoff and exclude every record after it. An undated record is also excluded unless its availability by that cutoff is explicitly established. Filename sequence alone cannot prove the unplaced fragment existed earlier. Checks compare IDs, sequence, available explicit dates and context membership; no filesystem timestamp is used. SY-01, SY-03, SY-05, SY-06, SY-07, SY-09 and SY-11 are historical diagnostics at SY-R05. SY-04 uses the latest corpus to inspect the undated fragment without asserting past availability.

RS-06 remains a latest-view diagnostic asking retrospectively about the last dated task list (11 June 2026 in RS-R06). Its as_of_record is RS-R07, ongoing temporal status unknown, applicability unclear. It is not a primary current-task success. Canonical production S6 uses the unchanged formal question and requires evidence that a task is still pending at the latest supplied state.

RS-01 retains the diagnostic final-artefact-purpose question. Canonical production S1 (RS-09) is researcher-confirmed supported/unclear: the explicit final-artefact purpose supports aim or intended direction, while present applicability and active development remain unproved. Its expected temporal status is conservatively unknown. Only the explicit purpose is acceptable gold; future possibilities cannot support this aim. The canonical question is not narrowed to avoid that ambiguity. Likewise, explicit resolution of Signal Loom's named drift issue remains a successful narrow diagnostic but does not automatically settle the broad production S5 question about all remaining questions or limitations.

Cases within a project are related probes, not independent project samples. The two tiers, repeated section outputs and historical views must never be combined into one overall improvement score. This is an exposed diagnostic benchmark, not a held-out generalisation or participant study.

## Independent support, applicability, temporal status and evidence role

Support is a case-level judgment about whether the records establish an answer, including an explicit negative answer. Applicability is a separate, mandatory case-level field. Neither is inferred from retrieval output, an empty directory or a non-empty candidate list.

| section_applicability | Meaning |
| --- | --- |
| applicable | The section question applies at the documented reference state: for example a current purpose, remaining issue, attributed feedback or confirmed next task is evidenced. |
| not_applicable | A source explicitly establishes that the scoped question does not currently apply, such as closure with no active aim or next task, no external feedback, an explicitly non-existent direction, or resolution of the named issue. |
| unclear | The available records do not establish whether the scoped question applies. Missing retrieval results do not establish inapplicability. |

Every case records applicability_scope and applicability_rationale. The scope is the section question as constrained by that case and its reference point, not a blanket verdict about every question in that section. A named issue's resolution does not prove all issues resolved; an absent implementation commitment does not invalidate other documented next tasks. EF-08 remains unclear because a final-scope deferral and an undated scope-decision task do not settle the narrow implementation question. RS-06 is supported retrospectively but unclear as an ongoing next-action question. Their stated boundaries were confirmed by the researcher; neither uncertainty was silently resolved.

Each passage has one temporal status, one or more evidence roles, a source-relative locator, exact text, rationale and any required pairing. Longer mixed statements are split by focal assertion where practicable. A label is relative to its explicit context, not globally assigned to a filename.

| temporal_status | Meaning |
| --- | --- |
| current | Explicitly current in the documented reference state; not a claim about today. |
| historical | A previous intention, event, reason or observation without an active present commitment. |
| superseded | Explicitly replaced in the relevant scope; retained comparison material is not automatically discarded. |
| completed | The described task, issue or project is explicitly finished or resolved. |
| future_conditional | Optional, tentative or conditional; never an agreed next_action. |
| unknown | The record cannot establish the relevant ongoing status. Missing dates alone do not make every statement unknown. |

The evidence_role vocabulary is current_intention, change, reason, current_direction, superseded_direction, feedback, unresolved_issue, next_action, contextual_only and **closure_or_inapplicability**. Roles describe focal assertions independently of their temporal status. A completed former task may retain next_action as a retrospective role but cannot meet a current-only task requirement. A future_conditional passage must not have next_action, including as a secondary role.

closure_or_inapplicability is reserved for passages directly answering applicability in the cases listed by inapplicability_case_ids. It can establish completed/closed status with no active work, no further task, no recorded or collected external feedback, or explicit inapplicability of the named issue. Completed evidence is not automatically closure evidence: a repair, delivered feature or completed test does not close every section or the whole project. Four passages carry this role for five cases across both tiers; all are synthetic. Three cases are production and two are diagnostic; their results must remain separate. They do not become feedback, unresolved_issue or next_action.

Feedback requires external attribution. Self-reflection is not external feedback. An explicit no-feedback statement is negative applicability evidence, not a feedback quotation. Unknown is evidential uncertainty, not a synonym for an unlabelled retrieval result.

expected_temporal_status and role_temporal_requirements specify admissible evidence for the requested claim. On an insufficient case they are target requirements, not assertions that qualifying evidence exists. Actual annotated passages retain their own temporal_status. applicability_evidence_sets lists alternative complete passage sets establishing a known applicability label; unclear cases have no such set. These sets are evaluation annotations, never retrieval inputs.

## Support/applicability combination rules

1. **Explicit closure:** supported + not_applicable; temporal status is usually completed; required_evidence_roles includes closure_or_inapplicability. Only closure that directly answers the scoped question qualifies.
2. **No relevant record:** insufficient + unclear. Do not fabricate a not_applicable conclusion.
3. **Explicitly no external feedback received/collected:** supported + not_applicable with closure_or_inapplicability. A statement limited to no feedback recorded supports only that narrower archive claim.
4. **Empty feedback directory alone:** insufficient + unclear. File absence cannot prove feedback never occurred.
5. **Conditional future direction:** for possible_next_action, affirmative task support depends on a confirmed task. A possibility alone establishes neither applicable nor a next_action role. Inapplicability requires independent explicit negative evidence; possibility alone also does not prove closure.
6. **Completed project with subsequent tasks:** do not automatically label not_applicable. Read whether the later task is a current commitment or future_conditional. A dated task with unresolved ongoing status is not silently made current.

These rules distinguish absent evidence, a later retrieval miss of existing gold, and evidenced inapplicability. No retrieval failure is diagnosed in this phase because no retrieval is run. No algorithm can receive gold applicability or roles as input.

## Researcher confirmation and immutable freeze

Fuzhe Zhang manually reviewed all 34 case summaries, evidence roles, applicability, temporal scope and ambiguity notes and confirmed them on 25 October 2026. The assistant prepared the source-read annotations. This is researcher confirmation, not independent expert annotation or an inter-rater agreement study. Every case records reviewed_by, review_date and review_basis and has review_status researcher_confirmed.

The final decisions accept EF-R04 and RS-R07 as semantic latest-supplied-state anchors without invented dates or claims of proved creation chronology. RS-09 is supported/unclear: the final purpose answers aim or intended direction, but ongoing status remains unknown. A narrowly located purpose assertion is recorded separately for this gold use so the original diagnostic purpose annotation is not relabelled. SY-15 remains insufficient/unclear: named-issue resolution and closure cannot establish absence of all limitations. All other case semantics, tiers, cutoffs and eligible record IDs remain unchanged.

Locators use zero-based, end-exclusive Unicode offsets and one-based lines in UTF-8 text with universal LF newlines; source hashes use raw bytes. Context spans preserve required headings, dates or scope. No new analytical schema dimension was added at freeze; only required review provenance and confirmed/version validation were updated.

**phase_1_gold_v1 is immutable after freeze.** Baseline outcomes must never cause silent gold edits, exclusions, query rewrites or denominator changes. A necessary correction requires a new explicit version, a complete reason, preserved predecessor hashes and a renewed prospective review before comparison. Retain failed cases and negative results. Unknown/unjudged outputs require documented treatment; do not retrospectively change this gold set to make a method succeed.

The public manifest hashes all twelve other public files and provides a documented canonical-JSON self digest; the private manifest additionally records the public manifest's raw-byte SHA-256. This avoids an impossible raw-byte self-reference while covering all thirteen public files. Only a SHA-256 commitment to the private labels is public; private content and paths are not copied into the public manifest. The private manifest covers the private review package.

Confirmation authorises this freeze and publication. No baseline, retrieval, embedding, LLM or summary run is authorised or performed as part of this phase. Future algorithm work requires a separate instruction.

## Canonical questions and comparison conditions for a later phase

Production question fields are byte-for-text equal to the six strings in the unchanged [brief schema](../../../../src/brief_schema.py). Schema constants and a static AST check enforce this. No production question may be replaced with its old diagnostic wording, a case-specific answer cue or an easier subquery.

The current production system internally maps each section to two configured retrieval queries in reentry_brief.py. Preserve and report that existing behavior in a future production-baseline comparison; canonical question wording defines the task, while the unchanged internal query mapping defines the actual baseline mechanism. This distinction does not authorise rewriting either. A single-canonical-question retriever would be a different, separately declared method, not silently called the production baseline.

**A — frozen production baseline.** Preserve loader, 120-word windows, 30-word overlap, model, normalisation, configured section queries, category eligibility, selection order, deduplication, two-item limit and excerpts. Use all eligible records in the case's declared view. The existing non-empty flag is not a support or applicability classification.

**B — hybrid.** Same eligible corpus, chunks, model, canonical tasks, configured section queries, categories and evidence budget. Lexical tokenisation, fusion, constants, candidate budget and tie rules must be prospectively frozen before any comparison.

**C — state-aware.** Same frozen hybrid generator, with source-derived metadata and reranking. No gold roles, labels, case IDs, expected passages, private filenames or project-specific rules may become features. Reference-view membership is fixed input shared by all arms, not a learned date filter. Extraction and state rules require separate authorisation before implementation.

Diagnostic questions are specific evaluative probes, not substitutions for the primary task. Default failure analysis inspects the unchanged section-query output for the diagnostic view. Any later query-conditioned diagnostic search must be explicitly marked secondary, prospectively specified and kept outside primary scores. Better results from a specific detector, colour or multi-person question cannot conceal failure of a formal ProjectOS section.

The historic Echo Field [six-query evaluation](../../../../tests/evaluation_queries.json) remains a separate source-level regression, with its original Hit@1 4/6 and Hit@3 6/6 reference. It is neither a new result nor a replacement for the eighteen passage-level primary cases. No baseline or other method is run in Phase 1.

## Scoring contract and reproducibility

This phase designs **retrieval-evidence evaluation only**. It does not implement or evaluate final support/applicability classification. The next authorised phase must emit ordered_evidence, selected_evidence (at most two), source spans, actually visible excerpts/context metadata and latency_ms, without generating summaries. An item identifies source, start_char, end_char, excerpt and source-located context spans. A non-empty pair is not automatically supported; an empty pair is neither proof of missing evidence nor proof of not_applicable. Do not create a decision using the gold label or treat a legacy non-empty flag as a classifier.

For baseline diagnostics, ranks 1–2 remain its actual selected evidence in order. Remaining eligible chunks may be appended by maximum cosine across the unchanged queries, with chunk ID as deterministic tie-break. This extension supplies rank 3 and MRR; it does not replace the first two choices. B and C must expose their own frozen final list with selected evidence at its head. No such ranking has been executed in Phase 1.

A passage matches only when its complete quote survives in evidence from the same source/span, with whitespace-only normalisation. Negations, dates and conditions cannot be dropped. Prefix-only headings are not body evidence. If a matched passage appears in required_context_passages, its context spans must be visible in the same top-k evidence or attached source-traceable metadata. An unused alternative passage's context is not required. Merely citing a file does not qualify.

Duplicate or overlapping chunks count each passage once. A current/superseded pair may be in one chunk if both assertions are complete. Case-specific role_temporal_requirements control role credit. acceptable_gold_passages includes positive claims and explicit negative answers, with different roles. closure_or_inapplicability counts only for its listed case IDs. Applicability sets must reference acceptable gold in the same context; each listed alternative must be fully covered. An unclear case has no established applicability evidence set, even when some retrospective information is supported.

Boundary passages explain uncertainty but do not receive support credit unless explicitly promoted to acceptable gold in a versioned revision. The preceding v2 revision promoted five scoped negative-answer cases before any algorithm run; v3 preserves their claims while separating their evaluation tiers. Exclusions receive no positive credit for the excluded inference. An unmatched or ambiguously scoped selected passage is unjudged, not silently assigned a status. A definitive comparison cannot proceed with unresolved top-two judgments.

## Primary and secondary reporting contract

Primary reports contain exactly 18 production/latest-state cases, one case per project/section. Secondary reports contain the 16 diagnostics and identify latest versus historical snapshots separately. Do not publish a combined performance average, use diagnostic gains as production evidence, or let repeated questions inflate the main denominator.

For primary metrics, S = 15 supported, I = 3 insufficient, K = 14 known-applicability, N = 3 explicit-negative and P = 3 pair cases. Diagnostic equivalents are S = 14, I = 2, K = 13, N = 2, P = 5, but their summaries serve explanation only. These confirmed denominators are frozen; changing them requires a new explicitly justified gold version.

T denotes the ordered evidence; T2 is the actual selected pair. Gold matching requires full source-located assertions, correct reference context, required heading/date spans and role/status compatibility. An insufficient case's desired temporal status is a requirement for missing evidence, not proof such evidence exists. Context-only information is not automatically an affirmative answer.

| Required primary metric | Prespecified interpretation |
| --- | --- |
| Hit@1 | Over primary S, full eligible gold in T's first item. Report applicable versus explicit-negative strata. |
| Hit@3 | Same, over the first three items; retain actual production choices in positions 1–2. |
| MRR | Over primary S, reciprocal rank of first complete eligible gold, zero if absent; report candidate-list length. |
| Required-role coverage@2 | Over primary S, fraction of required roles covered in T2; also report all-roles coverage. Broader canonical questions admit documented alternatives, not only the old narrow target. A change and its reason must not be presented as a causal pair unless their source supports that connection. |
| Pair coverage@2 | Over primary P only, a complete accepted current/superseded pair in T2. The five secondary pair probes do not augment this denominator. |
| Temporal mismatch | Mismatched focal role/status in fully judged non-empty top-1 evidence, divided by fully judged top-1 cases. Report unknown and unjudged separately. Evaluate relative to as_of_record, not today. Valid closure has its own allowed status. |
| False-current evidence exposure | Primary current-claim cases exposing an excluded historical, superseded, completed or conditional passage instead of required current evidence. Valid historical partners in a direction pair are exempt. Report all-case and judged-non-empty denominators, plus unknown/unjudged. This is an exposure proxy, not a generated false statement. |
| Insufficient preservation | Report all primary I cases individually, including boundary-only, excluded, empty and unjudged outputs and any false-current/false-closure exposure. No positive gold exists for these cases. Final support/abstention preservation accuracy is **not assessable from retrieval alone** and must be reported as not assessed, not invented from empty/non-empty output. A separately authorised decision trace would be needed for that stronger metric. |
| Applicability evidence coverage@2 | Over primary K, complete coverage of any applicability_evidence_sets alternative. Report applicable and not_applicable separately. Unclear cases receive neither automatic credit nor a failure score. |
| Closure recognition rate | Over primary N, top-1 complete scoped closure_or_inapplicability evidence. Report @2 as a separate diagnostic. Completed status alone does not qualify. |
| Missing-versus-not-applicable distinction | Primary evidence contingency comparing insufficient/unclear (3) with supported/not_applicable (3): valid scoped closure, only wrong-scope/excluded negative evidence, no closure, unjudged. Unjudged takes precedence; then valid closure, with extra misleading exposure separately counted. This is evidence availability, not final applicability classification. |
| Retrieval latency | In a later authorised comparison: warm median and p95 per unique primary request, including query encoding, ranking, selection and excerpts. Report cold preparation separately; one warm-up and 30 alternating-arm repetitions on the recorded machine. Historical/diagnostic timing is separate. No model load or timing experiment is performed now. |

Publish project and section numerators/denominators for the primary set, with project macro and pooled primary-case summaries separately. Never use the pooled 34-case set as a performance denominator. A broader question's acceptable alternatives can contain different valid answers; role coverage alone does not establish exhaustive reconstruction or correct causal explanation.

All metrics are retrieval-evidence measures. Non-empty output is not supported classification, empty output is not evidence absence, and neither determines applicability. No gold-derived oracle may create an abstention or status decision. Unjudged evidence must be reviewed before a definitive comparison; no inference about participant agreement or production reliability follows from this benchmark.

## Success and stopping criteria

Existing privacy, source integrity, context preservation, multi-project, leakage, latency and negative-result safeguards remain. Metric denominators and success claims now explicitly use the primary tier.

1. A new method must improve the **18 production cases**. Improvement only on secondary diagnostics is not experimental success.
2. Preserve the separate original Echo Field regression, including Hit@3 6/6, complete first task and current/superseded distinction. Keep historical Hit@1 4/6 visible without claiming a new run.
3. Primary pair coverage@2 must strictly exceed A on the three primary pair cases. Primary required-role coverage@2 must strictly exceed A, improve in at least two projects and not regress in the third. If a strict gate is unattainable because A is already at ceiling, do not silently change it after results; report no qualifying improvement under this protocol.
4. Preserve the primary insufficient/unclear versus supported/not_applicable evidence boundary. All three primary explicit-negative cases must expose valid closure evidence in T2. Missing records must not earn invented inapplicability. Automatic insufficient/applicability classification remains outside this experiment.
5. Primary applicability coverage and closure recognition must not regress against A. False-current exposure must not increase; future_conditional never earns next_action credit. The historical task-list diagnostic cannot count as a successful primary next action.
6. Primary and secondary results must be separately reported. The earlier private failure targets remain secondary explanations; gains on them cannot substitute for formal section performance. Specific diagnostic queries never replace primary queries.
7. Historical views must contain no future record or undated record with unproved cutoff availability. Latest production views must contain the complete declared latest corpus. Changing eligibility to hide difficult evidence invalidates comparison.
8. No source edits for balance, gold leakage, case removal, project-specific rules, retrospective query tuning or algorithm switching. All labels are researcher-confirmed and frozen; no algorithm work is authorised here.
9. Keep the prospective warm median latency target below 300 ms per primary request; report preparation and p95. No latency has been measured in Phase 1.
10. Preserve inconsistent or negative outcomes. Even success justifies further technical investigation, not production integration, final state understanding or new participant-validation claims.

## Frozen package

- [Public benchmark and annotation guide](../../../../tests/fixtures/temporal_state_benchmark/README.md)
- [Public gold labels](../../../../tests/fixtures/temporal_state_benchmark/public_benchmark.json)
- [Annotation schema](../../../../tests/fixtures/temporal_state_benchmark/benchmark.schema.json)
- [Synthetic source archive](../../../../tests/fixtures/temporal_state_project/README.md)
- [Gold checksum manifest](../../../../tests/fixtures/temporal_state_benchmark/freeze_manifest.json)

The separate ignored researcher-archive package contains private gold labels, the qualified prior-experiment review, researcher confirmation and integrity records. It is not linked or copied into this public fixture.
