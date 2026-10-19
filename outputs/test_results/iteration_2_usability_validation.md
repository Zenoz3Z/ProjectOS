# Iteration 2 usability validation

Date: 19 October 2026. Branch: `iteration-2-usability-refinement`. Base commit: `bab8061b2dbb5b428d239fd4f1d7b2630068e24d`.

Status: implemented and technically checked; awaiting researcher review. No Iteration 2 participant evaluation is claimed. See [TD-004](../../project_knowledge/decisions/technical_decisions/td_004_iteration_2_review_semantics.md) and [DD-005](../../project_knowledge/decisions/design_decisions/dd_005_round_1_usability_refinements.md).

## Scope checked

Participant wording for sections 3 and 6, four review choices including Not applicable, evidence guidance and the concise tutorial were checked. Backend section IDs and questions, retrieval, chunking, embeddings, prompts, summary generation and cache implementation remain unchanged. No AI recommendation mode was added.

## Automated results

| Check | Result |
| --- | --- |
| Full pytest suite | **105 passed in 49.16 seconds**, including the existing 93 cases and 12 additional cases; no skipped tests. |
| Python compilation | `python -m compileall -q src tests` passed. |
| Dependencies | `python -m pip check`: no broken requirements. No dependency versions changed. |
| Whitespace/diff | `git diff --check` passed. |
| Markdown local links | All local links in changed/new documentation resolve. |
| Privacy scan | No credentials, email addresses, private machine paths or populated Authorization headers found in the 13 implementation/documentation/test files. |
| Protected data | 1,462 pre-existing protected files unchanged by SHA-256 comparison, including 377 P01/P02 path-labelled files. |
| Frozen materials | All eight Round 1 template files unchanged, including the R1–R7 wording and freeze date. |
| Existing work | All three pre-existing untracked report drafts unchanged. |
| Staging | Empty; no commit or push performed. |

New tests cover Not applicable validation, append-only persistence, latest-state reconstruction, old schema-1 Confirm/Correct/Reject records, separate completion counts, tutorial separation, all four choices, wording, reload, navigation guards, project isolation and unchanged cache bytes. API/HTTP/model entry points are blocked during UI tests. A valid cache returns six hits without rebuilding retrieval or summaries.

The initial sandbox run failed to create temporary files. A subsequent run reached 104 passes with one Windows file-replacement permission error in a temporary fixture. The complete suite was rerun unchanged in the project environment and passed all 105 cases. No test was removed or weakened to obtain that result. Diagnostic logs remain local and ignored.

## Browser rehearsal

The real Streamlit interface ran on loopback in a separate synthetic workspace, bound to synthetic code P998. The tutorial and project used fixed offline fixtures; no participant cache was regenerated or used for this rehearsal. Credentials were removed and SDK, HTTP, summary-generation and embedding entry points were guarded.

- The tutorial showed all four action meanings, provisional-summary guidance, evidence absence and separation of updates from evidence. A practice Not applicable response did not create a formal review.
- Six sections were reviewed in order using Confirm, Update, Not applicable and Reject. Section 3 showed the new title/question; section 6 explained that it reports recorded steps rather than inventing advice.
- Supporting-record guidance appeared above the closed evidence area. No evidence expansion was required to save. Opening an excerpt later showed the original synthetic source text.
- An unsaved first-pass Update disabled Previous/Next. After completion, an unsaved change to Not applicable blocked return to the summary; explicit discard allowed navigation without adding an event.
- Saving a subsequent Not applicable change retained the older correction in history, updated the visible status and completion counts, and kept the section open.
- Refresh and reopening the same code returned directly to completion without repeating the tutorial. Final displayed counts were six reviewed, zero corrected, one rejected and four not applicable; the remaining section was confirmed. These are synthetic engineering checks, not research findings.
- Another synthetic code, P999, was refused by the bound session. Its review file remained absent.
- A measured direct section jump took approximately 282 ms from browser command to the target heading being visible. This single local observation includes automation overhead and is not a benchmark or participant timing.

Guard counters after rehearsal: **0 API attempts, 0 summary-generation attempts, 0 embedding-construction attempts**. The synthetic review history contained seven events, including the preserved earlier update. Tutorial review storage remained absent.

Screenshots of the tutorial, choices, documented-next-step section and completion state are retained in ignored local validation storage. They show synthetic records only and have not been published. The temporary smoke server was stopped after validation.

## Privacy and integrity boundary

The final review covers the 13 changed/new implementation files, not publication approval for the three existing report drafts. No real project packs, assignments, cached summaries, review histories, signed forms, private reports or participant screenshots enter this change. Existing ignore rules remain intact. Private diagnostics, synthetic fixtures, temporary test files and screenshots remain ignored.

SHA-256 comparison found no unexpected changes in the pre-existing protected set. The loader, chunker, retriever, backend brief schema, re-entry builder, LLM summarizer and cache module are byte-for-byte unchanged; participant wording therefore does not invalidate their fingerprints. Configuration files and demonstration project records are unchanged.

The legacy review-status type-annotation limitation and its cache coupling are recorded in TD-004. Technical validation does not establish comprehension, a three-minute tutorial duration, factual accuracy or improved re-entry outcomes. Those require subsequent participant evaluation. No recruitment, new formal assignments or real data collection occurred during implementation.
