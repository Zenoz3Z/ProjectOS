# Submission preparation validation

Date: 17 November 2026. Baseline: `2b5f110ec7e2593c2d8155023b3c07f0c406f06f`, branch `temporal-state-retrieval-state-aware-v1`. These are local preparation checks, not a participant evaluation, new experiment run or claim that the uncommitted additions are already on GitHub.

## Scope and results

| Check | Actual result |
| --- | --- |
| New public-demo tests | **11 passed in 40.11s.** Covers missing/changed assets, strict production cache identity, unique/resumable isolated sessions, keyless detached startup, rejected network/model/research-data access, real review UI reuse, draft protection and save/refresh recovery. |
| Relevant existing regressions | **120 passed in 76.56s.** Participant flow/UI, evidence guidance, review store, study-project isolation/cache checks and summary validation. Their participant-code examples use synthetic temporary fixtures, not real participant files. No old tests were modified. |
| Initial new-test attempt | 10 passed; the independent-startup test timed out at 60 seconds. The new launcher's per-call guard repeatedly normalised paths. Replacing that work with a precomputed path prefix resolved the timeout; the same assertions then passed. No production code, timeout, dependency or system permission was changed. This was not reported as a Windows socketpair failure. |
| Python compilation | All four new demo modules and the new test module compile without writing bytecode to the repository. |
| Dependencies | `pip check`: no broken requirements. Existing environment only; no installation or version change. |
| Browser interaction | Actual local browser: 0/6; evidence and source details expanded; fictional Update entered; Save and continue; 1/6 and section 2 visible; actual refresh; Previous restored section 1, original summary and saved update. Unsaved-response warning and disabled navigation were visible before saving. |
| Demo persistence | Exactly one browser-created tutorial review event in the source checkout's new ignored demo session. Test events are separate temporary fixtures. No study review was created. |
| Runtime boundaries | No OpenAI request, embedding model initialisation, retrieval, summary generation or experiment execution during demo validation. Fail-closed guards recorded no blocked activity during normal startup/browser use. Separate negative tests intentionally exercised blocked operations before their bodies ran. |
| Thesis | v10 changes only cover status/date from v9. The body and AI acknowledgement match v9 byte-for-byte in Markdown. Extracted Word/PDF body and acknowledgement match the Markdown after formatting normalisation; tables and numbers are included. |
| Word and PDF | 15 pages each. PDF exported directly from the completed Word-compatible document. All 15 rendered pages visually inspected: no clipping, overlapping text, blank pages, isolated headings or table overflow found. Searchable text, four embedded font subsets, nine public web/DOI links; no local absolute hyperlinks. |
| Counts | Body 3,575; AI Use Acknowledgement 225; combined 3,800. Eight references retained. No institutional counting exemption is assumed. |
| Accepted video | v4 MP4 and SRT copied without changes and checked by SHA-256. The researcher previously confirmed full viewing; no new continuous human listening review is claimed here. |
| Independent consent attachment | Existing researcher-confirmed blank Version 1.0, 9 October 2026, retained unchanged. Four pages; researcher name/email are authorised public details. No signed/filled copy included. Questionnaire masters retain their historical draft status. |

The earlier 129-test and 450-test results in historical reports remain historical; they are not this preparation's results. The full experiment suite was not rerun. Iteration 3 still has no new participant validation, and the post-study selector remains separate from the production prototype.

## Privacy and preservation

The candidate uses an explicit list of baseline tracked files plus the inspected submission/demo additions. It does not traverse private directories for packaging. Text checks cover credentials, populated authorization headers, email/contact patterns and private machine paths; flagged historical descriptions and a privacy-scanner regex were inspected as non-secret code/documentation. The only contact details permitted in the separate blank consent PDF are the researcher details explicitly authorised for publication. Historical demo images contain tutorial/illustrative material.

All baseline tracked files other than `.gitignore` and the main README remain byte-identical, including production source, original tests, configuration, frozen benchmark/metadata, algorithms, scoring and results. Ten older full thesis drafts, the existing blank form, original tutorial cache and original external exports/media are checked against their initial public/tutorial-only hashes. No real participant materials, caches, reviews, assignments, signed forms, private research or private P96 files are read, parsed or rehashed. Their exclusion is verified using path rules and the explicit candidate inventory, not by inspecting their content.

The package excludes credentials, `.git`, environments, model weights, private evidence/traces, old full thesis versions, old videos, raw narration, editing intermediates and demo sessions. The tracked historical chapter draft remains because process logs reference it. It is clearly historical and removed from the current-thesis entry.

## Reproduction boundaries

The cache-only demonstration imports the existing application but does not load an embedding model. Original raw-byte cache validation remains active: changing source, prompt, pipeline or newline bytes can invalidate the cache. The candidate ZIP preserves the tested bytes. Dependencies are not bundled; initial installation may need internet access. A fresh operating system or fresh dependency installation is not claimed as tested.

The package's root file manifest records the baseline commit, exact paths, sizes, SHA-256 hashes and uncommitted additions. The delivery reply records the final archive and detached-extraction checks. The local candidate is not represented as identical to the remote branch. The complete private technical experiment cannot be reproduced from public files alone; private gold/evidence/traces and participant records are deliberately omitted. No submission/upload, Git staging, commit, push, merge, rebase or branch change is performed.
