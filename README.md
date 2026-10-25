# ProjectOS

**A source-grounded, correctable brief for returning to a creative project.**

ProjectOS is an MSc research prototype that helps creative students revisit a project after an interruption. It retrieves evidence from existing project records and organises it into a six-section Project Re-entry Brief, with short AI-generated summaries and visible supporting excerpts. Users can inspect the evidence and confirm, update, reject or mark a section not applicable. The local Streamlit prototype supports researcher-assigned projects, with Echo Field as a short tutorial. Researchers prepare summaries before a session by sending selected excerpts to the OpenAI API; participant review reads the prepared summaries without calling the API.

## Guide for supervisor review

**Final design response, 25 October 2026:** Iteration 3 adds conditional, section-specific evidence guidance, consistent definitions of the four review actions and an explicit optional evidence reminder. It responds to the two completed study rounds; **there was no third participant study, and these changes have not been evaluated with new participants**. Feature development is now frozen. Remaining work is thesis integration, portfolio preparation and final validation/submission preparation. See [DD-006](project_knowledge/decisions/design_decisions/dd_006_iteration_3_actionable_evidence_absence.md) and the [Iteration 3 validation report](outputs/test_results/iteration_3_evidence_guidance_validation.md), which separates the researcher-reported local test pass from the blocked Codex browser attempt.

**Study closure, 24 October 2026:** Round 1 and Round 2 are complete with four formal participants: P01/P02 and P03/P04, **n=2 per round**. There is no P05 and no further recruitment is planned. Prototype feature development is frozen. The remaining work is final analysis review, thesis integration, final validation and submission preparation. Read the [Round 2 final findings](project_knowledge/feedback/user_testing/iteration_2/round_2_final_findings.md) and [cross-iteration comparison](project_knowledge/feedback/user_testing/iteration_2/cross_iteration_findings.md). These are descriptive findings, not proof of causal benefit, statistical significance or objective reconstruction accuracy. Existing thesis drafts remain unchanged pending reviewed integration.

The 19 October refinement added clearer section wording, Not applicable, evidence-checking guidance and a concise tutorial; it retained the existing direct completion navigation. See [TD-004](project_knowledge/decisions/technical_decisions/td_004_iteration_2_review_semantics.md), [DD-005](project_knowledge/decisions/design_decisions/dd_005_round_1_usability_refinements.md) and the historical [validation report](outputs/test_results/iteration_2_usability_validation.md).

The following Meeting 3 preparation notes record the earlier position, not the current recruitment status.

**Meeting 3 preparation: 15 October 2026, 15:00 (Europe/London). Updated following feedback on 9 October 2026.** Supervisor confirmation received on 9 October 2026: no amendment to the existing ethics approval is required. Participant-facing documents must clearly state what data will be stored, where it will be stored, and for how long.

Participant data-storage wording has been added to the information sheet and consent form. Their status is **Draft for supervisor review — existing ethics approval unchanged; data-storage wording updated following supervisor feedback on 9 October 2026.** Documents remain subject to wording review at Meeting 3. **At the 9 October preparation checkpoint, formal recruitment and P01 had not started.** This records supervisor confirmation about the existing approval, not a new ethics approval.

The prototype supports local, assigned-project rehearsals. In the [P00 pilot](project_knowledge/feedback/user_testing/iteration_1/pilot_p00_summary.md), the participant completed all tasks without technical errors but found the interface complex and the instructions unclear. This motivated the progressive review interface. Automatic retrieval expansion remains frozen. The original Round 1 protocol proposed three adults returning to their own paused creative projects; that proposal is retained as a dated protocol, not an assertion of achieved sample size. P00 is excluded from the formal sample, and one pilot does not establish research conclusions. The documents below can be reviewed without installing the application or supplying an API key.

| Review question | Suggested reading |
| --- | --- |
| What is the research trying to establish? | [Current goals](project_knowledge/current_state/goals.md) and [research questions](project_knowledge/feedback/user_testing/iteration_1/research_questions.md) |
| Why this interaction, and how was it built? | [Summary design decision](project_knowledge/decisions/design_decisions/dd_004_user_facing_reentry_summary.md) and [implementation chapter draft](report/drafts/04_design_and_implementation.md) |
| What did the completed study find? | [Round 2 final findings](project_knowledge/feedback/user_testing/iteration_2/round_2_final_findings.md), [cross-iteration comparison](project_knowledge/feedback/user_testing/iteration_2/cross_iteration_findings.md) and [development-log index](project_knowledge/process/daily_logs/README.md) |
| What procedure was originally proposed? | [Round 1 protocol draft](project_knowledge/feedback/user_testing/iteration_1/study_protocol_round_1_draft.md), [materials gap check](project_knowledge/feedback/user_testing/iteration_1/study_materials_gap_check_round_1.md), and [project-pack guide](project_knowledge/feedback/user_testing/iteration_1/participant_project_pack_guide.md) |
| What still needs attention? | [Open issues](project_knowledge/current_state/blockers.md) and [proposed next steps](project_knowledge/current_state/next_steps.md) |

The implementation chapter describes Iteration 0. Later summary generation and participant-session work are documented in the [Day 7](project_knowledge/process/daily_logs/day_7_llm_reentry_summary.md) and Day 8 logs; the chapter has not yet been extended to cover those changes.

## Problem and motivation

Creative projects accumulate goals, experiments, feedback, abandoned ideas and decisions across many files. Returning after a break involves more than finding a document: the practitioner needs to reconstruct what changed, which direction is current, what remains unresolved and what to do next. Relevant text can describe an earlier stage of the project, so retrieving a similar passage does not by itself establish the current state.

## Research focus

> How do source visibility and user correction help creative practitioners assess an AI-generated reconstruction of a long-term project during project re-entry?

The research examines source visibility, evidence absence, correction, control and verification effort. [TD-003](project_knowledge/decisions/technical_decisions/td_003_freeze_automatic_project_state_inference.md) freezes further automatic retrieval expansion after engineering success did not establish semantic acceptance. Automatic temporal reasoning, automatic contradiction detection, self-service upload, public deployment, user accounts and perfect reconstruction accuracy are outside the present scope. Explicit temporal metadata remains future work; prototype feature development is frozen.

## Relationship to general-purpose AI chat tools

ProjectOS uses a fixed project re-entry workflow rather than an open-ended conversation. Its design brings together six recurring project questions, source excerpts and a persistent review history. Corrections appear as the user's current understanding while the original records remain available. These are the prototype's design priorities, not a claim that general-purpose AI tools cannot support similar tasks or that ProjectOS has demonstrated superior performance.

## Current prototype workflow

1. The researcher validates the assigned project, prepares all six summaries and starts a local study server bound to one participant code. The participant enters that code and reads the study introduction.
2. Complete one Echo Field tutorial section: read a provisional summary, optionally inspect source evidence and try one of four responses. Missing evidence can be a valid result; an update records the user's interpretation separately from the original evidence. Tutorial responses are not saved as formal reviews and never enter completion statistics.
3. Check the assigned project's readiness, then choose **Start my project review**. The first review follows the six sections in order, one at a time: each section's question, provisional summary, optional source evidence and response controls. Each section uses up to two evidence excerpts; missing categories may produce an insufficient-evidence summary.
4. Choose **Confirm**, **Update**, **Reject** or **Not applicable**, using the shared definitions below. Not applicable counts as reviewed and remains distinct from confirmation and rejection. An update requires correction text. Older-direction marking is available within the evidence area. Reviews and annotations do not change the prepared system summaries.
5. **Save and continue** records the response and opens the next pending section. Previous/Next allow navigation; unsaved edits must be saved or explicitly discarded first. Saved sections and remaining work are marked.
6. After all six sections have saved reviews, the completion page shows reviewed, corrected, rejected and not-applicable counts and **Review or change a section**. Six buttons show each section's full name and saved status; selecting one opens that section directly. These shortcuts are unavailable until all six sections have been reviewed.

Post-completion editing shows **Editing section X of 6**, with **Previous section**, **Next section** and **Back to completion summary**. Navigation stays within sections 1–6. Unsaved action, correction or note changes block navigation until the user chooses **Stay and save** or **Discard changes and continue**. Saving appends a review event, updates the status and completion counts, and keeps the current section open. The user can return to completion, continue editing or choose another section; existing summaries and evidence remain unchanged.

After a completed session is refreshed or reopened with the same participant code, it returns directly to the completion page without repeating the introduction, tutorial or readiness steps. Navigation, saving and refresh recovery read existing prepared summaries, evidence and saved reviews; they do not call the OpenAI API, regenerate summaries or rebuild embeddings.

Development mode retains the full six-section view, regeneration controls and technical information. The start screen's 10–15 minute estimate refers to the review activity only, not the full study session; the available observations do not establish a validated review-time benchmark.

There is no project picker, file-upload interface, account system or unrestricted chat. The researcher starts a separate session for each participant. Its server accepts only the bound code and hides Development mode, so changing the entered code cannot select another project. Codes are not passwords: this is supervised, loopback-only use on the researcher's computer, not an authenticated multi-user service.

### Six Re-entry Brief sections

Participant wording is independent of the backend section definitions. Section IDs `current_vs_superseded` and `possible_next_action`, retrieval questions, prompts and cache fingerprints are unchanged.

| Section | Purpose |
| --- | --- |
| Current intention | Reconstruct the project's current aim. |
| What changed and why | Revisit documented changes and their reasons. |
| Current direction and replaced ideas | What is the project doing now, and which earlier ideas or approaches are no longer current? |
| Relevant feedback | Recall feedback and any documented response. |
| Unresolved tensions | Identify questions or limitations that may still need attention. |
| Documented next step | Report a next step found in project records; do not invent a recommendation. If none is documented, the user can choose Not applicable or record their own next step using Update. |

## Evidence retrieval and user review

The loader supports Markdown, UTF-8 text and text-based PDFs. It retains relative source paths, file types and directory categories. Documents are split into overlapping chunks of up to 120 whitespace-separated words, with a 30-word overlap. The demonstration archive currently produces 12 chunks from four Markdown documents.

Sentence Transformers creates normalised `all-MiniLM-L6-v2` embeddings. Retrieval uses NumPy similarity ranking, section-specific queries, category filtering and chunk deduplication. Each brief section contains at most two evidence items. The LLM returns a structured summary, support status, project-state classification, source numbers and an assessment note; local validation checks the output structure and source-number bounds.

**Semantic similarity is not factual confidence. Generated summaries are provisional.** A valid citation number does not prove that the interpretation is correct. The retrieval layer's `supported` flag means evidence items were selected; it is separate from the LLM's assessment and from the user's review.

Above supporting records, the participant interface says: “Check the supporting records when a summary seems surprising, outdated or incomplete. You do not need to open every record.” Opening a record remains optional and is not proof of verification.

When the prepared summary's `support_status` is `insufficient`, the interface explains: “ProjectOS could not establish this section from the evidence it selected. The information may be absent, outdated, or not retrieved.” Each section suggests a type of record the user may want to check: a recent overview or goals statement; a decision/process log; current-versus-earlier direction records; attributable feedback or a record of its absence; blockers, limitations or reflection; or a current task, handover or completion statement. These suggestions do not establish that a file is missing, diagnose retrieval failure, rerun retrieval or call a model. Supported summaries do not show absence guidance; conflicting summaries retain their evidence-checking warning. An unavailable summary retains the separate availability message.

The tutorial and review form share these definitions:

- **Confirm** — The reconstruction accurately represents the project.
- **Update** — The reconstruction needs a corrected current interpretation.
- **Reject** — The reconstruction is misleading or unsupported.
- **Not applicable** — This section does not apply to the project's current state.

Confirm means the user has assessed the reconstruction, not left it unchecked. Update records a more accurate current interpretation; Reject can identify an incorrect, misleading or unsupported reconstruction. Not applicable is not a synonym for a system error. These definitions support the user's judgement and do not determine the response. Before selection, the interface says: “You may open the source evidence before deciding. This is optional.” Evidence remains collapsed by default, and opening it is not a requirement for saving.

Review events support `confirm`, `correct`, `not_applicable`, `reject` and `mark_superseded`. They are appended to a local JSON history without rewriting source documents, and existing events load without migration. A later Not applicable review removes any previous correction from the active display while retaining that correction in the append-only history. User corrections are displayed separately from the generated interpretation. Development and participant histories live under `data/reviews/`, which is excluded from Git.

## Current features

- Local document loading, overlapping chunks and semantic retrieval.
- Six structured sections with inspectable source excerpts.
- OpenAI summary generation with Pydantic structured output and insufficient-evidence handling.
- Participant controls for confirmation, correction, not-applicable review, rejection and older-evidence marking.
- Conditional evidence guidance for insufficient summaries, consistent action definitions and an optional reminder before choosing a response.
- A validated runtime project context, local assignments, and separate review files keyed by participant code and project ID; the existing review JSON schema is unchanged.
- A single-section Echo Field tutorial followed by assigned-project readiness, progressive review and draft protection; completion unlocks six named section shortcuts and editing with saved-state recovery.
- Researcher CLI commands for validation, preparation and a session bound to one participant.
- Private, durable summary caches checked against project, source content, evidence, model and prompt/schema fingerprints. Participant navigation and saving make no API calls; valid caches work without an API key.
- Unit tests, a small retrieval evaluation set, design decisions and draft study materials.

## Technology stack

Python 3.11 is the tested environment. Direct dependencies are pinned in [requirements.txt](requirements.txt).

| Component | Library |
| --- | --- |
| Interface and application state | Streamlit |
| Local embeddings | Sentence Transformers |
| Similarity calculations | NumPy |
| PDF text extraction | pypdf |
| Summary API client | OpenAI Python SDK |
| Structured summary schema | Pydantic |
| Automated tests | pytest |

The prototype does not require a vector database or a separate web backend.

## Repository structure

```text
ProjectOS/
├── src/                      # Retrieval, brief, summary, review and UI modules
├── tests/                    # Unit tests and retrieval evaluation questions
├── config/                   # Safe assignment example and empty category template
├── data/
│   ├── demo_projects/        # Prepared Echo Field tutorial records
│   ├── study_projects/       # Local project packs; contents ignored except README
│   ├── study_config/         # Local assignments; contents ignored except README
│   ├── summary_cache/        # Private prepared summaries and excerpts; ignored
│   └── reviews/              # Private review histories; ignored
├── project_knowledge/
│   ├── current_state/        # Planning and evaluation documents
│   ├── decisions/            # Design and technical decisions
│   ├── process/daily_logs/   # Development history
│   ├── feedback/user_testing/iteration_1/
│   │                         # Blank study materials, not participant responses
│   └── research/             # Literature notes; downloaded PDFs excluded
├── research/                 # Earlier literature-note tree, retained for provenance
├── outputs/                  # Inspected demo image, wireframe and technical results
├── report/drafts/            # Design and implementation writing
├── requirements.txt
├── pytest.ini
└── README.md
```

The current goals, open issues and next steps provide a reading guide to the present prototype. Dated plans and development records describe the project as it existed at the time; they may differ from later drafts. The two literature-note trees contain duplicate material retained from development. Ignored local files may be present in a working copy but are not part of the repository.

## Installation

Use Python 3.11 and a dedicated environment. With Git and Miniconda installed, run the following in Miniconda Prompt from the folder where you want to keep the project. Access to the private repository is required to clone it.

```bat
git clone https://github.com/Zenoz3Z/ProjectOS.git
cd ProjectOS
conda create -n projectos python=3.11
conda activate projectos
python -m pip install -r requirements.txt
python -m pip check
```

If you already have a checkout, open its root directory and skip the clone step. If the `projectos` environment already exists, activate it instead of creating it again. The first retrieval run may download the embedding model; subsequent runs can use the local model cache. Generating summaries requires network access and an OpenAI API account with access to the configured model, and may incur API charges.

## Environment variables

| Variable | Purpose |
| --- | --- |
| `OPENAI_API_KEY` | Required by `prepare` and Development summary generation. Supply it only through the launching process environment. Prepared participant review needs no key. |
| `PROJECTOS_SUMMARY_MODEL` | Optional model override; the current source default is `gpt-6-luna`. The selected model must support the API options used in `src/llm_summarizer.py`. |
| `PROJECTOS_STUDY_PARTICIPANT` | Code bound by the researcher's `serve` command; participants cannot change this through the UI. |
| `PROJECTOS_STUDY_ONLY` | Set to `1` by `serve` to hide Development mode. |
| `PROJECTOS_STUDY_ROOT` | Data workspace set by `serve`; normally this checkout. `--root` allows an isolated researcher-controlled QA workspace. |

Configure the API key privately in the launching environment. No key value is provided in this document. The application does not load `.env` or Streamlit secrets files. Do not put a key in source code, documentation, screenshots or Git commits. API model access depends on the account; this repository does not guarantee that its default model is available to every user.

On Windows, one option is to add `OPENAI_API_KEY` through the user Environment Variables settings. Open a new terminal afterwards, activate `projectos` and launch the application from that terminal.

To check presence without printing the key:

```bat
python -c "import os; print('OPENAI_API_KEY configured' if os.getenv('OPENAI_API_KEY') else 'OPENAI_API_KEY missing')"
```

## Run the Streamlit prototype

With `projectos` active and the terminal in the repository root:

```bat
python -m streamlit run src/streamlit_app.py
```

For a Windows Miniconda installation under the current user's profile, run the following in **Command Prompt** from the ProjectOS repository root. Adjust the activation path if Miniconda is installed elsewhere.

```bat
REM Run these commands from the ProjectOS repository root
call "%USERPROFILE%\miniconda3\Scripts\activate.bat" projectos
python -m streamlit run src\streamlit_app.py
```

Open the local URL printed by Streamlit. Development mode is sufficient for a demonstration. The application loads records from `data/demo_projects/sample_echo_field/`; it does not index this repository's research notes or downloaded papers. Without an API key, evidence inspection is available, but new LLM summaries cannot be generated. Review controls are shown when a summary or a saved user correction is available.

For a short demonstration, select Development mode, generate the brief, inspect a section's evidence, then save a correction and revisit the section. This writes a local review history under the ignored `data/reviews/` directory. Use demonstration text only. Start participant sessions with the preparation workflow below.

### Prepare an assigned local project — historical study setup

The commands below document the existing study setup for reproducibility, not a plan to create new participants. Both rounds are closed; do not overwrite completed participant packs, caches or reviews. Use non-personal synthetic material for any separately authorised final validation.

The earlier preparation required the [Round 1 start gate](project_knowledge/feedback/user_testing/iteration_1/study_protocol_round_1_draft.md#start-gate) and participant information/consent covering the [data flow and storage schedule](project_knowledge/feedback/user_testing/iteration_1/participant_owned_project_data_protocol_draft.md). Anna's 9 October confirmation concerned the unchanged existing ethics approval. Study closure does not make a new approval or consent-issuance claim.

1. Copy the empty category folders from `config/study_project_template/` to a new `data/study_projects/P01/` directory. Do not overwrite an existing participant pack.
2. If no local assignment file exists, copy `config/participant_assignments.example.json` to `data/study_config/participant_assignments.json`. Otherwise edit the existing local file. Its example maps `P01` to `participant_project_p01`, the display name `My assigned project`, and `data/study_projects/P01`. Use distinct project IDs and non-overlapping directories.
3. Add existing `.md`, UTF-8 `.txt` or text-based `.pdf` files to `current_state/`, `decisions/`, `feedback/` and `process/`. The [pack guide](project_knowledge/feedback/user_testing/iteration_1/participant_project_pack_guide.md) specifies 4–8 self-selected, screened, non-sensitive records, but categories may be empty. A non-empty supported document and resulting chunks are required. Record how the researcher categorised the files.
4. In the activated `projectos` environment, run:

```bat
python src/study_project_manager.py validate --participant P01
python src/study_project_manager.py prepare --tutorial
python src/study_project_manager.py prepare --participant P01
python src/study_project_manager.py validate --participant P01
python src/study_project_manager.py serve --participant P01
```

`validate` needs no key, makes no API calls and prints category filenames, document/chunk counts and readiness, never document bodies. It returns a non-zero exit status until materials and all six cached summaries are ready; this is expected before the first preparation. `prepare` requires an environment key and reports per-section progress, cache hits, misses and logical generation requests. Empty-evidence fallbacks do not call the API. A valid cache is reused; repeated preparation does not regenerate it. The selected model must match across preparation and serving (use the same `--model` option if overriding it).

`serve` checks both tutorial and assigned caches, binds to `127.0.0.1:8501` by default, removes `OPENAI_API_KEY` from the Streamlit child process, and accepts only `P01` for that session. Open the local URL printed in the terminal. Stop the server with Ctrl+C before starting the next participant's session. Use `--port` to choose another local port if needed; do not expose this prototype as a public study service.

Each assigned project has its own private cache and review file, for example `data/summary_cache/participants/P01/participant_project_p01_summaries.json` and `data/reviews/participants/P01/participant_project_p01_reviews.json`. The tutorial cache is shared. Changing source bytes, source filenames, the model, prompt/schema or retrieval implementation invalidates preparation. Re-run `prepare` before the session; do not edit sources or reprepare during an active review. Review corrections and notes never enter the summary cache. Once all six sections have saved reviews, refreshing and reopening the same assigned session restores the completion page directly, without repeating the tutorial or making an API request.

## Run tests and checks

After activating `projectos`, run from the repository root:

```bat
python -m py_compile src/streamlit_app.py src/participant_flow.py src/study_project_manager.py
python -m pytest -v
python -m pip check
```

`pytest.ini` adds `src` to pytest's import path, so a separate `PYTHONPATH` setting is unnecessary. The suite includes brief, review-store, summary, flow, Streamlit AppTest, assignment, path safety, readiness and cache tests. The [Iteration 3 validation report](outputs/test_results/iteration_3_evidence_guidance_validation.md) records **129 passed in 145.16s**, reported by the researcher after running the full suite in a fresh local Command Prompt with `projectos` activated. Codex did not repeat that full run; its earlier temporary-file and asyncio/socketpair failures, and its later blocked browser startup, are recorded as isolated-environment limitations. Tests use temporary non-personal files, mock retrieval and mock summaries; they do not make live OpenAI requests or assess factual accuracy. They cover cache invalidation, keyless review, direct post-completion navigation, save/refresh recovery, unsaved-change protection, tutorial separation, Development compatibility and the new evidence guidance. The [Iteration 2 report](outputs/test_results/iteration_2_usability_validation.md) and [readiness report](outputs/test_results/formal_study_readiness.md) retain their earlier results and browser rehearsal limits.

The separate retrieval evaluation can be run with:

```bat
python src/evaluate_retrieval.py
```

It loads the embedding model and evaluates six developer-authored queries. The [recorded Iteration 0 baseline](outputs/test_results/day_03_retrieval_results.md) reported Hit@1 of 4/6 and Hit@3 of 6/6 on the demonstration archive. These historical figures are not a general accuracy score or evidence of user benefit.

## Current prototype status

The repository contains the Iteration 3 assigned-project prototype, the final design response after the study. Feature development is frozen. Both research rounds are complete: P01/P02 in Round 1 and P03/P04 in Round 2, four formal participants. There is no P05, no third participant round and no further recruitment. Iteration 3 has not been evaluated with new participants. The two Round 2 sessions used complete or largely complete projects; their descriptive findings do not establish a causal interface effect or generalisable accuracy. Remaining work is reviewed thesis integration, portfolio preparation, final validation and submission preparation. See the [final Round 2 account](project_knowledge/feedback/user_testing/iteration_2/round_2_final_findings.md) and [comparison across rounds](project_knowledge/feedback/user_testing/iteration_2/cross_iteration_findings.md).

Historical preparation, pilot and engineering records retain their original dates and scope. Study closure does not alter consent/storage terms or establish a new ethics approval. This is a local research implementation, not a production service.

Iteration 3 has the researcher-reported full-suite pass above, plus compilation and dependency checks. Its isolated synthetic browser attempt stopped during Streamlit startup at asyncio/socketpair; no Iteration 3 browser-interaction pass is claimed. Earlier browser rehearsals used local retrieval, fixed offline summary fixtures and isolated test records. The earlier post-completion browser check used P96's existing prepared summaries and saved reviews, without new OpenAI requests, and verified direct navigation, draft protection, saving and refresh recovery. The researcher also completed that post-completion navigation experience and reported that it passed. These historical checks establish technical behaviour for their recorded versions, not Iteration 3 participant outcomes or summary accuracy; a fresh installation was not tested.

**P96 is a researcher self-test and is excluded from the formal participant sample.** Its review statistics, including automated smoke-test review events, must not be treated as formal research results. P96 project materials, summaries, review histories, screenshots and the detailed self-test report remain private and are not included in the repository.

## Research and evaluation status

Both rounds are complete with **four formal participants, n=2 per round**. Round 1 involved P01/P02; Round 2 involved P03/P04. P00 is an excluded informal pilot and P96 an excluded researcher self-test. There is no P05 and no further recruitment is planned. Prototype feature development is frozen.

The [historical Round 1 protocol](project_knowledge/feedback/user_testing/iteration_1/study_protocol_round_1_draft.md) proposed three adults and supervised 40–50 minute sessions with an independent baseline. Those are proposed procedures, not achieved sample or timing claims. The actual Round 1 cases lacked independent pre-exposure baselines. One opening observation is missing and one session has an unresolved timing conflict; no complete Round 1 opening rate or cross-round timing comparison is reported.

The [research questions](project_knowledge/feedback/user_testing/iteration_1/research_questions.md) and [question/observation guide](project_knowledge/feedback/user_testing/iteration_1/post_test_questionnaire_and_interview.md) frame source visibility, absence, correction, clarity, control, re-entry and verification effort. Saved formal actions match the session records. Evidence openings, assistance, timing, ratings and interviews remain manual research records, not complete telemetry.

The [Round 2 final findings](project_knowledge/feedback/user_testing/iteration_2/round_2_final_findings.md) report 12 reviewed sections, 3 Confirm, 9 Not applicable, no Update or Reject, and evidence opening in 2/12 sections. Approximate total session duration was 36 minutes, averaging 18 minutes. No navigation, terminology or lag problems were reported, and almost no explanation was required. These observations concern two complete/largely complete projects and cannot establish causal usability improvement.

The [cross-iteration comparison](project_knowledge/feedback/user_testing/iteration_2/cross_iteration_findings.md) retains the different action sets: Round 1 had 9 Confirm, 2 Update and 1 Reject; Not applicable was unavailable. Different participants, projects and project states prevent attributing action or rating differences to the interface.

The frozen [ProjectOS Round 1 Post-test Ratings — Round 1 v1](project_knowledge/feedback/user_testing/iteration_1/round_1_templates/post_test_ratings_template.md), R1-R7, remain unchanged from 8 October 2026. These are custom exploratory items, not a validated scale. Only descriptive item ranges are used publicly. R6 is negative-direction and P03's interpretation remains ambiguous; no reverse-scored composite or inferential statistics are used. Participant-assessed alignment is not objective accuracy or ground truth. Historical L1-L7 and pilot responses are not pooled with formal results.

Repository copies of the [information sheet](project_knowledge/feedback/user_testing/iteration_1/participant_information_sheet.md), [consent form](project_knowledge/feedback/user_testing/iteration_1/participant_consent_form.md) and [data protocol](project_knowledge/feedback/user_testing/iteration_1/participant_owned_project_data_protocol_draft.md) retain their historical wording-review status. Closure does not independently verify issued versions or storage compliance. Existing terms remain unchanged: restricted UAL OneDrive storage; source/extracted/temporary copies deleted within seven calendar days after the session; de-identified records and separate signed forms retained until 30 November 2027; separate identity linkage deleted after the seven-day withdrawal period. Necessary temporary local copies use the researcher's password-protected computer. The documents describe OpenAI as an external service, possible abuse-monitoring retention up to 30 days, no deliberate transmission of names/contact details, and no audio/video/photographs. Raw materials, signed forms, mappings, review JSON and interview notes stay outside GitHub. The [materials gap check](project_knowledge/feedback/user_testing/iteration_1/study_materials_gap_check_round_1.md) remains a historical preparation record.

Remaining work is reviewed thesis integration, portfolio preparation, final validation and submission preparation. Iteration 3 implements conditional suggestions about record types to check; automatic diagnosis of missing files or temporal state remains outside scope. No new participant recruitment or automatic retrieval expansion is planned. Earlier [demo-only procedures](project_knowledge/feedback/user_testing/iteration_1/participant_test_protocol.md), design decisions and study proposals remain historical records.

## Limitations

- Iteration 3 is a design response, not a participant-evaluated improvement. Its browser smoke attempt was blocked by the Codex isolated runtime before interaction; conditional guidance does not repair retrieval or establish why evidence is insufficient.
- Published retrieval evaluation uses one small prepared archive; P96 provides excluded researcher self-testing. Four formal participants across two different rounds provide descriptive findings, not generalisable accuracy or causal user-benefit evidence.
- P96 exposed evidence retrieval issues in section 3 (Current versus superseded directions), section 5 (Unresolved tensions) and section 6 (Possible next action). These remain known limitations; successful navigation does not establish that the retrieved evidence or reconstructed project state is accurate.
- Retrieval does not explicitly model chronology or parse state metadata. Related passages can still mix resolved issues, current blockers and future work. No PDF OCR is implemented.
- Generated summaries can omit or misinterpret evidence. Source-number checks do not verify factual entailment.
- Reviews persist, but exact generated-summary snapshots are not durably linked to review events. A regenerated section can inherit an earlier review status.
- A confirmation following a correction currently removes that correction from the active display, while retaining the historical event.
- Missing or stale participant caches block formal review with a non-technical message. The researcher must prepare them again; participants cannot regenerate summaries. Cache validity checks structure and freshness, not truthfulness.
- Assigned-project cache freshness is checked on each rerun without inference. Development mode retains its older in-memory retrieval cache; restart that mode after editing the demonstration archive.
- JSON storage has no concurrent-write coordination. Run one supervised session at a time and keep project materials fixed during it. Server binding blocks code guessing through the participant UI, but does not protect against access to the researcher's operating-system account or an already-open participant session.

## Privacy and repository contents

**Raw participant research data is not included in the repository.** Versioned materials consist of code, prepared demonstration records, development documentation, blank research templates, an anonymous P00 pilot summary, explicitly de-identified study summaries and inspected prototype visuals. The pilot summary contains no names or raw responses. The Echo Field records are a prepared archive, not raw ProjectOS participant data. References within that archive to informal testing concern the Echo Field creative project, not a completed ProjectOS evaluation.

Local assignments, participant project packs, summary caches (which contain excerpts), review histories, signed consent forms, recordings, transcripts, private meeting attachments, downloaded academic PDFs and unapproved screenshots are excluded through `.gitignore`. Participant data directories expose only safe READMEs, with empty templates and a safe assignment example elsewhere. Original local records are retained. Raw study outputs belong in ignored private directories, never in public blank templates; only the explicitly allowlisted de-identified summaries are public. Ignore rules do not anonymise a file or protect a file already committed; inspect staged files before publishing.

Document loading and embedding-based retrieval run locally. On generation, selected excerpts are sent to the OpenAI API with `store=False`; this is not a claim of zero provider-side retention. Do not use personal or confidential material in the demonstration archive. Never publish API credentials or participant data.

## Screenshots and design artifacts

The following inspected images show historical development, not the latest interface or participant study results.

![Iteration 0 command-line brief showing a developer correction and retained source evidence](outputs/screenshots/day_04_corrected_reentry_brief.png.png)

*Earlier command-line prototype: a developer-authored correction remains separate from retrieved evidence.*

![Early Project Re-entry Flow wireframe](outputs/wireframes/project_reentry_flow_v0.png)

*Early design exploration. Upload, project-selection and navigation controls shown in the wireframe are not implemented in the current application.*

## Author and course context

**Zeno Zhang**\
MSc Creative Computing\
UAL Creative Computing Institute\
2026

ProjectOS is an individual graduation research project at the University of the Arts London. It combines software prototyping with reflective design documentation and a completed exploratory two-round study.

## Licensing

This repository uses mixed licensing. Source code created by Zeno Zhang in `src/` and `tests/` is licensed under the [MIT License](LICENSE). The standard MIT text is available from the [Open Source Initiative](https://opensource.org/license/mit).

Research writing, research materials, `project_knowledge/`, interface screenshots and other original documentation and assets are **Copyright © 2026 Zeno Zhang. All Rights Reserved.** They are not covered by the MIT grant. Third-party libraries, models and dependencies remain under their respective licences. See [LICENSE](LICENSE) for the full scope and terms.

Downloaded research papers are excluded, while literature notes retain their source references.
