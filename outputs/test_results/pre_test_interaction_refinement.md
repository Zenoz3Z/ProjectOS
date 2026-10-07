# Pre-test interaction refinement: verification record

Date: 5 October 2026

Baseline: `781f94d` — Initial ProjectOS research prototype

Working branch: `ui-pilot-polish`; changes remain uncommitted and unpushed.

## Scope

The participant interface now presents an introduction, one section at a time, optional evidence details, conditional correction input, save-and-continue navigation and a completion page. The six-section schema, source documents, retrieval, summary prompts and model, review JSON schema and participant file isolation remain unchanged. Development mode retains the full technical view.

## Automated checks

All 32 tests passed across the following runs in the existing Python 3.11 `projectos` environment:

- 23 existing brief, review-store and summariser tests.
- 4 participant-flow tests: schema order, progress/completion, action mapping and restoration of saved values.
- 5 Streamlit AppTest checks: conditional inputs and draft protection; completion, reopening and isolation; insufficient evidence; failed-save recovery; partial-generation recovery.

`python -m py_compile src/streamlit_app.py` passed. `python -m pip check` reported no broken requirements. No dependencies were added or upgraded.

AppTest uses temporary review files and offline summary fixtures. These are technical tests, not observations of participants or evidence of summary quality.

## Browser smoke checks

The browser check used the actual document loader, chunking and cached local embedding model over the four existing demonstration records. The testing process did not have `OPENAI_API_KEY`, so summary responses were fixed, explicitly labelled offline fixtures. A local harness redirected every review write into an ignored, separate smoke-test directory. It did not write to the actual participant review directories.

| Check | Result |
| --- | --- |
| Enter P00 and open the start page | Passed; description, three steps and Start review displayed. |
| One section at a time | Passed; section number, question and overall progress displayed. |
| Evidence disclosure | Passed; filenames and unchanged excerpts appear first, source details are secondary. |
| Conditional update field | Passed; appears only for the update choice. |
| Unsaved input | Passed; warning shown and Previous/Next disabled until save or explicit discard. |
| Saving and navigation | Passed; saves advance to the next pending section, Previous/Next revisit saved sections. |
| Action mapping | Test JSON contains `correct`, `confirm`, `reject`, `confirm`, `confirm`, `confirm` in section order. |
| Completion statistics | Passed; 6 reviewed, 1 corrected, 1 rejected. These are synthetic smoke-test counts, not P00 pilot findings. |
| Refresh and reopen P00 | Passed; completion and saved reviews restored from disk. |
| P01 isolation | Passed; starts at 0/6, with no P00 correction or selected response. |
| Development mode | Passed; all six sections and the technical-details toggle remain available. |
| Final presentation changes | Checked after restarting the test server; shorter participant titles and secondary session button displayed. |

The initial test server emitted file-watcher warnings while examining optional Transformers vision modules. The text retrieval and interface still operated. The restarted smoke server used `--server.fileWatcherType none` to avoid that unrelated module scan. No project configuration or dependencies were changed for this workaround.

## Limits and next check

The browser check does not verify live API credentials, model access, generated-summary accuracy or whether the new interaction reduces participant effort. The 10–15 minute start-screen estimate refers to the review activity and is not a measured pilot duration.

Run the actual application with `OPENAI_API_KEY` available in its launching environment, then rehearse the revised participant workflow with a designated rehearsal code. Check a correction, an unsupported summary, draft protection, all-six completion, and restoration after refreshing and reopening that code. Keep rehearsal data separate from the formal sample. Existing code histories reopen without being reset.

The anonymous pilot account is recorded separately in `project_knowledge/feedback/user_testing/iteration_1/pilot_p00_summary.md`. No conclusions about participants are inferred from these software checks.
