# Formal Study Readiness — Assigned Participant Projects

Date: 7 October 2026\
Branch: `ui-pilot-polish`\
Baseline commit: `781f94d`\
Status: local implementation and synthetic technical QA; no commit or push.

## Scope and preservation

This work continues the existing progressive participant UI. Before editing, the 13 already changed/untracked files were copied into ignored private backup storage with a hash manifest. No existing work was reset, stashed, checked out, deleted or discarded. Research questions, six section definitions, original review JSON schema, demonstration records, model/prompt implementation, requirements and existing information/consent forms remain unchanged.

The proposed formal study now uses the participant's own creative project after at least one to two weeks away. Echo Field teaches the interaction through one section. This technical implementation does **not** establish ethics approval or authorise recruitment/data collection under the revised workflow. P00 remains excluded from the formal sample; the P97 exercise below is synthetic QA, not participant research.

## Implementation

| Area | Result |
| --- | --- |
| Runtime context | `ProjectContext` carries project ID, display name, data directory, review file, summary cache file, role and optional participant code. Echo Field defaults remain compatible. |
| Assignment | Ignored `data/study_config/participant_assignments.json`; public example in `config/`. Distinct IDs and non-overlapping project directories are required. |
| Path boundary | Strict ASCII codes (`P` followed by two or three digits); traversal, absolute assignment paths, unexpected separators, linked files and Windows junctions are rejected. Review/cache locations are validated against code and project ID. |
| Session isolation | Researcher CLI binds a loopback server to one code and hides Development mode. Entering another code cannot select another project. This is supervised local operation, not password authentication or OS-level file isolation. |
| Flow | Code → introduction → one-section Echo Field tutorial → assigned readiness → Start my project review → six sections → completion. Tutorial responses are temporary and never counted or written as formal review events. |
| Readiness | Assignment, directory, supported files, extractable chunks, category filenames and all six cache entries. Missing categories are allowed; no usable text or stale/missing caches blocks formal review with a generic assistance message. |
| Preparation | `validate`, `prepare` and `serve` researcher commands. Validation prints filenames/counts without document bodies. Preparation reports each section, hits/misses and logical generation attempts; errors omit provider payloads. |
| Durable cache | Project/section/model/prompt-schema/evidence identity plus source-content and pipeline fingerprints. Source or prompt changes invalidate it. Partial successful preparation can be resumed. Tutorial cache is shared; assigned caches are separate. |
| Review persistence | Existing schema version 1 and event semantics; filenames include participant code and project ID. Corrections, notes and evidence annotations do not change the prepared cache. |
| Participant performance | Cache reads verify freshness without retrieval/inference. Previous, Next and Save make no API calls. The served process receives no OpenAI API key. |

## Automated validation

Environment: existing `projectos`, Python 3.11.16, Streamlit 1.64.0. No dependencies added or upgraded.

```text
python -m py_compile src/streamlit_app.py src/participant_flow.py src/study_project_manager.py
PASS (project_context.py and study_cache.py were compiled as well)

python -m pytest -v
74 passed in 39.02s; no skipped tests

python -m pip check
No broken requirements found.
```

Coverage includes the original 23 brief/review/summary tests, existing progressive-flow checks, valid/invalid codes, traversal and linked-path rejection (Windows junction exercised), absent assignments/directories/materials, incomplete categories, participant/project review and cache separation, cache hits without retrieval/generation, source/model/prompt invalidation, partial preparation recovery, tutorial separation, keyless review, missing-cache blocking, draft/save/restore behaviour, Development compatibility and removal of the API key from the study child process.

Automated tests use temporary non-personal data, mock retrieval and mock structured summaries. They do not evaluate factual accuracy or make live OpenAI requests.

## Local P97 smoke test

An ignored QA workspace contained four small synthetic documents (four chunks) for `qa_project_p97`, an independent P98 assignment, and a copy of the existing Echo Field tutorial archive. Preparation used the real locally cached `all-MiniLM-L6-v2` retriever and fixed offline summary fixtures. No private participant data or live API request was used.

| Check | Observed result |
| --- | --- |
| Cache preparation | Tutorial and P97 each prepared six entries. Each repeat reported six cache hits, zero misses and zero generation calls. Initial six attempted generations per project were mock calls, not live API traffic. |
| Actual CLI validation | P97: four supported documents, four chunks, category filenames listed, materials/cache ready, no issues. |
| Bound server | Actual `serve --participant P97` on `127.0.0.1:8502`; process launched without an API key. No Development selector appeared. |
| Guessing another code | P98 was refused; its project content was not shown and no P98 review file was created. |
| Tutorial | One Echo Field section, evidence expansion and a practice correction completed. Neither tutorial nor formal review files existed at the readiness gate. |
| Formal completion | Six saved events: confirm, correct, reject, confirm, confirm, confirm. Completion displayed 6 reviewed, 1 corrected, 1 rejected. Stored project ID was `qa_project_p97`, schema version 1. |
| Refresh/reopen | Re-entering P97, completing the tutorial and reopening the assigned review restored completion and the saved correction. Revisit did not append events or change the review file hash. |
| Summary separation | Cache hash after corrections/reopen matched the pre-review hash. |
| Participant presentation | Expanded evidence/source details showed no absolute disk path, other project content or Development control. |
| Development | Separate AppTest with real local retrieval, isolated review path and no key showed all six sections, the research-details toggle and no exception. No review file was written. |

For the four-document P97 fixture, 30 cache reads plus freshness checks had a median of **31.49 ms** (27.26–37.53 ms). One browser Next, one Previous and six Save transitions took **394–657 ms** from automation action to the expected view. These small local samples include automation overhead and are not a benchmark of large projects or initial process startup. Imports/model initialisation can still delay startup. No inference occurred during participant navigation.

The private QA workspace retains preparation statistics, timing samples, review/cache hash checks and completion screenshots. These artifacts remain ignored and are not published as study findings.

## Git and privacy checks

`git check-ignore -v` confirmed exclusion of participant project paths, summary caches, participant reviews, local assignment JSON and private QA screenshots. Safe READMEs, assignment examples, empty templates and the two preparation documents remain versionable. No tracked file matched an ignore rule. No ignored data was staged.

The final versionable-text scan found no OpenAI/Hugging Face/GitHub credential patterns or email-address patterns. This pattern check is not a guarantee of complete anonymisation; real materials still require researcher inspection. All root README local links resolved. `git diff --check` passed. The 13 pre-existing changed files still exist and their private backup hashes remain intact.

The branch remains `ui-pilot-polish`, latest commit `781f94d`; the index is empty. The working tree intentionally contains the existing and new local changes. No commit, push, reset, stash or branch switch was performed.

Final `git status --short --untracked-files=all`: eight modified tracked files and 21 untracked files (including the five already untracked before this task). No deleted files. The existing origin remains `https://github.com/Zenoz3Z/ProjectOS.git`.

Files created for this task:

- `src/project_context.py`, `src/study_cache.py`, `src/study_project_manager.py`.
- `tests/study_fixtures.py`, `tests/test_study_projects.py`.
- `config/participant_assignments.example.json` and four empty category `.gitkeep` files.
- `data/study_config/README.md`, `data/study_projects/README.md`, `data/summary_cache/README.md`.
- `participant_project_pack_guide.md` and `participant_owned_project_data_protocol_draft.md` under the Iteration 1 study-material directory.
- This validation report.

Existing local work extended in this task: `.gitignore`, root `README.md`, `src/streamlit_app.py`, `tests/test_participant_ui.py`, and the three current-state reading guides. Earlier paper READMEs, the P00 summary, interaction report, `participant_flow.py` and its pure-flow tests were preserved.

## Remaining research preparation

1. Obtain supervisor confirmation of the new scope and whether an ethics amendment is required. The new data protocol is explicitly a draft.
2. Update the Participant Information Sheet and Consent Form to cover participant-owned material, local organisation, external API excerpts, caches/reviews and withdrawal. Agree contacts, retention and withdrawal arrangements; no values are invented here.
3. Confirm inclusion criteria, participant numbers, task protocol, rating scale and full-session duration. Record researcher categorisation as an influence on retrieval.
4. Run the production preparation command with a privately configured API key on approved non-sensitive rehearsal material. Live API access, model availability and summary quality were not verified by this offline smoke test.
5. Keep materials/model fixed during sessions. Review events still lack a durable link to the exact summary version; confirmation after a correction retains the historical event but clears the active correction, as before. These limitations were documented, not silently migrated.

For the first local test project, follow **Prepare an assigned local project** in the root README: copy the empty template into a new P01 directory, create or extend the local assignment file without overwriting it, add non-personal text, validate, prepare tutorial and P01, then serve P01. Do not collect real project packs until the revised study arrangements are confirmed.
