---
project: ProjectOS
document_type: daily_log
category: process
date: 2026-10-01
iteration: 1
status: completed
---

# Day 7 — Source-grounded LLM Summary and Correctable Interface

## Objective

Today I focused on responding to the supervisor’s feedback that the prototype should present its findings in a clearer and more accessible way.

The previous interface exposed retrieved chunks and similarity scores, but it still resembled a developer-facing debugging tool. My objective was therefore to introduce concise AI-generated summaries while preserving source visibility, uncertainty and user control.

## Work completed

### 1. Improved evidence retrieval

I revised the retrieval process so that each Re-entry Brief section can use more than one focused retrieval question.

The system now:

- uses section-specific retrieval queries;
- selects complementary rather than duplicated evidence;
- retrieves no more than two evidence chunks per section;
- preserves source paths, chunk identifiers and similarity scores;
- keeps category restrictions for different brief sections.

I also increased the maximum evidence excerpt length from 420 to 1,200 characters. Important information, such as documented next steps, sometimes appeared near the end of a chunk and was previously removed before being passed to the language model.

### 2. Added source-grounded LLM summaries

I implemented `llm_summarizer.py` using the OpenAI Responses API and Pydantic structured outputs.

Each generated section includes:

- a concise user-facing summary;
- an assessment note;
- a support status;
- a project-state classification;
- the identifiers of the evidence sources used.

The possible support states are:

- `supported`;
- `conflicting`;
- `insufficient`.

The possible project-state types are:

- `current`;
- `historical`;
- `superseded`;
- `future`;
- `mixed`;
- `unclear`.

The summariser is instructed to use only the retrieved evidence and to return an insufficient-evidence response when the records do not support a reliable conclusion.

### 3. Added local validation and failure-safe behaviour

Structured output ensures that the model response follows the required data schema, but it does not guarantee that the interpretation is correct.

I therefore added local validation that:

- rejects invalid source identifiers;
- removes unsupported source references;
- prevents a supported result without valid evidence;
- returns a safe fallback when the API request fails;
- enforces a mixed state for the section comparing current and superseded directions.

This creates a separation between valid output structure and valid project interpretation.

### 4. Redesigned the Streamlit interface

I integrated the summaries into a more user-facing Streamlit interface.

The interface now provides:

- a clear introduction to the Re-entry Brief;
- a manual “Generate my re-entry summary” action;
- six concise summary sections;
- visible support and project-state labels;
- collapsed supporting project records;
- clearer review actions;
- a regeneration option;
- optional technical details;
- an explanation of what project material is sent to the OpenAI API.

Generated summaries are cached so that ordinary interface interactions do not repeatedly call the API.

### 5. Preserved user review and correction

The generated summary remains provisional until reviewed by the user.

The user can:

- confirm a reconstruction;
- update it in their own words;
- reject it;
- mark individual evidence as superseded.

When a correction is saved, the interface presents it as “Your current understanding”. The earlier AI summary and the original source evidence remain available rather than being overwritten.

This preserves a visible distinction between:

1. source evidence;
2. AI interpretation;
3. user interpretation.

## Validation results

The complete automated test suite passed:

- 23 tests passed;
- no tests failed;
- retrieval, review storage and LLM validation were covered;
- the dependency check returned `No broken requirements found`.

The interface successfully generated all six Re-entry Brief sections:

- generated summaries: 6 / 6;
- failed sections: 0.

## Important finding

During interface testing, the AI summary for “Unresolved tensions” treated multi-person interaction as a current blocker.

However, the project records described multi-person interaction as possible future work outside the present scope.

I corrected the section to:

> Slow movement feedback and lighting instability remain unresolved. Visual fatigue during long viewing sessions also remains a limitation. Multi-person interaction is future work rather than a current blocker.

The original AI summary, retrieved evidence and user correction remained visible.

This is not only a technical error. It is also an important research observation. A generated summary can sound coherent and plausible while still combining project states incorrectly. Source grounding alone does not remove the need for human interpretation.

The correction interaction therefore demonstrates the purpose of ProjectOS: the system reconstructs a provisional project state, but the creative practitioner remains responsible for confirming or correcting that reconstruction.

## Reflection

Today’s work clarified that ProjectOS should not compete with general AI tools by producing more fluent summaries.

Its value comes from the structure surrounding the summary:

- evidence remains inspectable;
- project states are distinguished;
- uncertainty can be represented;
- unsupported conclusions can be withheld;
- users can correct the interpretation;
- corrections are stored without deleting the previous reconstruction.

This positions ProjectOS as a reflective project re-entry tool rather than a general file-chat assistant.

The incorrect classification of multi-person interaction also showed why the project’s research question is relevant. Reconstructing a long-term creative project is not only an information-retrieval problem. It requires interpreting whether information is current, historical, superseded, unresolved or intended for future work.

## Ethics and privacy note

The prototype now sends selected project excerpts to the OpenAI API when the user requests generated summaries.

The interface explains this before generation. Personal or sensitive participant data should not be placed into the prototype until the participant information sheet, consent form and data-handling procedure have been finalised.

## Evidence and artefacts

The main artefacts produced or updated today were:

- `src/reentry_brief.py`;
- `src/llm_summarizer.py`;
- `src/streamlit_app.py`;
- `tests/test_llm_summarizer.py`;
- `requirements.txt`;
- screenshots of the generated brief;
- screenshot of the corrected unresolved-tensions section;
- automated test output showing 23 passed tests;
- dependency check showing no broken requirements.

## Next step

The next stage is to prepare the user research materials requested by the supervisor:

- research questions;
- participant information sheet;
- consent form;
- participant task script;
- interview and usability-testing questions.

## Day status

Completed.