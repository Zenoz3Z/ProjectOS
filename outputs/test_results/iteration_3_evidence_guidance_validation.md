# Iteration 3 evidence guidance validation

Date: 25 October 2026. Branch: `iteration-3-evidence-guidance`. Implementation base commit: `82f76b49bb70603a2d66c706989cd0df8c5ba23b`.

Status: final prototype checkpoint. The researcher supplied the native full-suite result and confirmed that manual UI inspection passed on 2026-10-25. The Codex automated browser smoke remained incomplete because its isolated runtime blocked before interaction; this was not a product functionality failure. **Iteration 3 has not been evaluated with new participants.** See [DD-006](../../project_knowledge/decisions/design_decisions/dd_006_iteration_3_actionable_evidence_absence.md).

## Implementation boundary

The participant renderer reads `GroundedSummary.support_status`. Only `insufficient` displays the new uncertainty explanation and section-specific guidance; supported/conflicting/unavailable results do not receive absence guidance. Conflicting and unavailable results retain their existing messages. Unknown section IDs have a generic, non-prescriptive fallback.

The tutorial and review form share Confirm, Update, Reject and Not applicable definitions and an optional source-evidence reminder. Evidence remains collapsed by default, without new required fields, save gates or telemetry. Internal action values are unchanged. Navigation, draft protection, append-only persistence, correction/source separation and project isolation retain their existing implementations.

No changes were made to retrieval, chunking, embedding configuration, prompts, summary generation, cache schemas or fingerprints, assignments, review JSON schemas, dependency versions or production runtime configuration. This final verification did not change the event-loop policy, system permissions, firewall or temporary-directory mechanism. Earlier diagnostic attempts used process-local temporary directories; they did not change production code or tests to bypass the environment.

## Changed files

Twelve public implementation, test and documentation files belong to this iteration; the three pre-existing untracked thesis drafts are excluded.

| Category | Files | Purpose |
| --- | --- | --- |
| Production presentation (2 modified) | [participant_flow.py](../../src/participant_flow.py), [streamlit_app.py](../../src/streamlit_app.py) | Pure text/mapping helper and participant/tutorial rendering. |
| Tests (1 modified, 1 new) | [test_participant_ui.py](../../tests/test_participant_ui.py), [test_evidence_guidance.py](../../tests/test_evidence_guidance.py) | Two wording/order expectations updated; 24 new parametrized cases. No old test was deleted or weakened. |
| Overview (1 modified) | [README](../../README.md) | Current interaction, study closure and validation provenance. |
| Current state (3 modified) | [goals](../../project_knowledge/current_state/goals.md), [blockers](../../project_knowledge/current_state/blockers.md), [next steps](../../project_knowledge/current_state/next_steps.md) | Final design response, feature freeze and submission work; dated historical sections retained. |
| Decision (1 new) | [DD-006](../../project_knowledge/decisions/design_decisions/dd_006_iteration_3_actionable_evidence_absence.md) | Evidence basis, scope and limits. |
| Development record (1 new, 1 modified) | [25 October log](../../project_knowledge/process/daily_logs/2026-10-25_iteration_3_evidence_guidance.md), [log index](../../project_knowledge/process/daily_logs/README.md) | Dated implementation and validation record, separate from the backfill. |
| Validation (1 new) | This report | Results, provenance and remaining browser limitation. |

## Automated validation

| Check | Result and provenance |
| --- | --- |
| Full pytest suite | User-provided native pytest result: **129 passed in 145.16s (0:02:25)**, reported by the researcher after restarting Windows and running in a fresh local Command Prompt with `projectos` activated. Codex did not repeat the full suite. |
| Researcher manual UI inspection | Passed on **2026-10-25**, as reported by the researcher; scope is recorded separately below. This is not new-participant evaluation. |
| Python compilation | All 21 source/test Python files compiled successfully. Bytecode was directed outside the repository. |
| Dependency consistency | No broken requirements found. No dependencies were changed. |
| Diff whitespace | Passed. |
| Markdown local links | All 123 local links in the eight changed/new Markdown documents resolve, including the previously missing validation-report targets. |
| Privacy and credentials | All 12 candidate public files inspected for credentials, populated Authorization headers, email/phone contacts and private machine paths; no scan findings. Manual review found no participant quotations or private project-source excerpts. |
| Protected files | All 3,392 pre-existing files under protected data/research paths and the three thesis-draft paths matched their initial SHA-256 hashes. This count includes prior local diagnostic/test records, not 3,392 participant records. Materials, caches, reviews, assignments, P00/P96, private records, research findings and frozen study templates remain unchanged. |
| Commit boundary | The final checkpoint is limited to the 12 public files listed above. Private data and the three untracked thesis drafts are excluded; main is unchanged. |

The 24 added cases cover six section-specific hints, the unknown-ID fallback, summary-support versus retrieval-status separation, absence of hints for other statuses, consistent action definitions, optional evidence checking, saving all four actions, tutorial separation and synthetic project isolation with append-only correction/note persistence and cache reuse. Existing UI cases retain completion navigation, draft guards and refresh recovery coverage. These are engineering checks, not semantic accuracy or participant-benefit measurements.

The first Codex full-suite attempt reported 78 passed, 9 failed, 41 errors and 1 skipped; the unsuccessful UI cases encountered Windows temporary-file PermissionError. A later isolated retry reached an asyncio/socketpair startup stall. A pure-Python diagnostic reproduced that stall before importing Streamlit or ProjectOS. The researcher subsequently confirmed local asyncio success and the full 129-test pass. These earlier attempts are recorded as Codex isolated-environment limitations, not Iteration 3 product failures; their private diagnostic outputs remain preserved.

## Browser smoke attempt

One attempt was made with synthetic code P998 in a new ignored workspace, without using real participant materials, caches, assignments or reviews. The existing offline fixture mechanism prepared six tutorial and six synthetic-project results. Both supported and insufficient states were present. These 12 fixture callbacks were not API requests or regenerated participant summaries.

The loopback Streamlit process was guarded against OpenAI requests, embedding model construction/encoding and external network connections. During startup, its stack stalled in the default Windows asyncio event loop's local socketpair `accept`. The diagnostic parent process detected the stall after approximately **26.37 seconds**, terminated only this attempt's process and made no further browser attempt. The server never reached readiness.

| Requested browser observation | Actual outcome |
| --- | --- |
| Supported/insufficient messages and section-specific guidance | Not reached; prepared fixture states were checked, but browser rendering was not observed. |
| Four action definitions and optional evidence reminder | Not reached in a browser. |
| Save Confirm/Update/Reject/Not applicable | Not reached; no synthetic review events created. |
| Refresh recovery, unsaved-change protection and section navigation | Not reached in a browser; no browser pass claimed. |
| Real participant isolation | No real participant workspace used; protected file hashes checked separately. |
| Temporary server cleanup | Attempt process terminated and recorded as stopped. |

Preparation and server guards recorded **0 OpenAI attempts/requests, 0 embedding model-load attempts, 0 embedding encode attempts and 0 external network attempts**. Python library imports do not constitute loading an embedding model. No model downloads, real participant summary generation or participant review creation occurred. These counters describe the instrumented Codex preparation/startup, not separately collected telemetry from the researcher's local pytest run or manual UI inspection. Final record preparation did not call OpenAI or load/generate embeddings.

## Researcher manual UI inspection

The researcher reported that manual UI inspection passed in the normal local environment on **2026-10-25**. The reported scope was:

- The insufficient-evidence explanation displayed correctly.
- Section-specific evidence guidance displayed correctly.
- The optional source-evidence reminder displayed correctly.
- Confirm, Update, Reject and Not applicable definitions were clear.
- No problems were found with page layout, navigation or interaction.

This records the researcher's reported experience within that scope. It does not convert the incomplete Codex automated browser smoke into a pass or claim additional tests. The automated startup block remains an isolated-execution limitation, not a product failure. This inspection was not a third participant study and does not constitute validation by new participants.

## Privacy, integrity and research status

Synthetic fixtures and diagnostic outputs remain ignored by Git. No raw participant responses, project excerpts, identities, signed forms, private absolute paths or credentials are copied into the public implementation or documentation. Ignore rules, production data schemas and the frozen R1-R7 wording/date remain unchanged. The three thesis drafts remain untracked and unchanged; they are not iteration deliverables. Existing Round 1/Round 2 findings are preserved as design evidence, not rewritten as validation of Iteration 3.

Both formal rounds are complete, with four participants in total and n=2 per round. P00 and P96 are excluded; there is no P05, no third participant round and no further recruitment. **No participant-validation claim is made for Iteration 3.** Feature development is frozen after this final design response. Remaining work is thesis integration, portfolio preparation, final validation and submission preparation.

Conditional record suggestions cannot diagnose missing files, recover omitted evidence, establish currentness or guarantee consistent action interpretation. The browser checklist remains unverified in this Codex attempt. Existing timing, R6, Not applicable interpretation and study-comparison limits remain. Neither the automated pass nor the design response establishes increased evidence checking, reduced burden or causal usability improvement.
