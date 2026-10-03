---
project: ProjectOS
document_type: daily_log
category: process
date: 2026-10-01
iteration: 1
status: completed_with_follow_up
---

# Day 8 — User Research Preparation and Participant Data Isolation

## Objective

Today I prepared the first iteration of the ProjectOS user study.

The main objective was to translate the supervisor’s recommendations into a practical research procedure. This included defining what the study should investigate, preparing participant-facing documents and ensuring that review data from different participants could not affect each other.

The study focuses on whether creative students and practitioners can understand, inspect and correct a Project Re-entry Brief. It does not attempt to prove that ProjectOS improves creativity or productivity.

## Research design decision

I decided that the number of participants and the number of test projects should be treated separately.

The planned formal study will involve approximately five to eight adult creative students or practitioners. Participants do not each need a different project.

Iteration 1 will use the same `sample_echo_field` demonstration project for all participants. This provides a consistent test condition and avoids requiring participants to upload personal or confidential project files.

A second real project will later be used to test whether the system can transfer beyond Echo Field. A third controlled project containing conflicting, missing and superseded information may be added during the second iteration.

## Research question

The current primary research question is:

> How can a source-grounded and correctable Project Re-entry Brief support creative students in reconstructing project state and deciding what to do next after an interruption?

The supporting questions examine:

- comprehension of the reconstructed project state;
- the effect of visible source evidence;
- user control through confirmation and correction;
- the usefulness of a proposed next action;
- misleading interpretations and additional cognitive effort.

## User research materials created

I created the following Iteration 1 research materials:

- `research_questions.md`;
- `participant_information_sheet.md`;
- `participant_consent_form.md`;
- `participant_test_protocol.md`;
- `post_test_questionnaire_and_interview.md`.

The materials define:

- the purpose of the study;
- participant eligibility;
- voluntary participation and withdrawal;
- the use of generative AI;
- the use of anonymous participant codes;
- the study tasks;
- observation criteria;
- questionnaire items;
- semi-structured interview questions;
- initial qualitative-analysis themes.

The questionnaire uses project-specific exploratory ratings rather than claiming to be a validated standardised scale.

## Participant session problem

Before today’s changes, all review events were stored in one shared JSON file.

This would have caused a serious research problem. For example, a correction created by participant P01 could have appeared in the interface used by participant P02.

This would have:

- exposed a previous participant’s response;
- influenced later participants;
- contaminated the study conditions;
- made it difficult to attribute review events;
- reduced the reliability of the evaluation.

## Participant-session implementation

I updated `src/streamlit_app.py` to support two modes:

### Development mode

Development mode continues to use the existing developer review history.

### Participant-study mode

Participant-study mode requires an anonymous participant code such as:

- `P01`;
- `P02`;
- `P100`.

Each participant receives an independent review-history file.

Example:

`data/reviews/participants/P01/sample_echo_field_reviews.json`

The interface now provides:

- a Development or Participant study mode selector;
- participant-code validation;
- a Start participant session button;
- an End participant session button;
- a visible active-participant indicator;
- participant-specific interface keys;
- participant-specific review loading;
- participant-specific review saving;
- protection against silently resetting an existing participant;
- a message when an existing participant session is reopened.

The system creates the participant directory only when a review event is saved.

## Code cleaning

The uploaded copy of `streamlit_app.py` contained Markdown escape characters such as:

- `\*\*`;
- `\_`;
- `\<style>`.

I removed these characters and restored valid Python, Markdown and CSS syntax while integrating participant-session support.

## Automated validation

I ran a Python syntax check:

`python -m py_compile src/streamlit_app.py`

The command completed without an error.

I then ran the complete existing test suite.

Results:

- 23 tests collected;
- 23 tests passed;
- no tests failed;
- Python 3.11.16;
- test duration: 8.10 seconds.

The update did not break the existing:

- retrieval behaviour;
- Re-entry Brief structure;
- review-event storage;
- review-history reconstruction;
- LLM result validation;
- insufficient-evidence fallback.

## Manual participant-isolation test

I created a test participant session using the code `P01`.

In the unresolved-tensions section, I saved the following user correction:

> Slow movement feedback and lighting instability remain unresolved. Visual fatigue during long viewing sessions also remains a limitation. Multi-person interaction is future work rather than a current blocker.

I then ended the P01 session and created a second session using `P02`.

The P02 session showed:

- `Active participant: P02`;
- `0 of 6 summary sections reviewed`;
- `Your review: Needs your review`;
- an empty correction field;
- no correction written by P01.

This confirmed that the participants’ review histories were isolated.

## Manual persistence test

I ended the P02 session and reopened P01.

The interface restored:

- `Active participant: P01`;
- the message that saved participant data had been reopened;
- `Your review: Updated by you`;
- the saved P01 correction;
- the user-authored interpretation as the current understanding.

This confirmed that participant review data remained available after leaving and reopening the session.

## Evidence captured

The following screenshots were saved as research evidence:

- `outputs/screenshots/user_testing/p01_review_persistence.png`;
- `outputs/screenshots/user_testing/p02_review_isolation.png`.

The first screenshot demonstrates persistent user correction.

The second screenshot demonstrates that a new participant does not inherit the earlier participant’s review state.

## Technical issue encountered

When Streamlit was restarted in a new terminal, the application displayed:

`OPENAI_API_KEY is not configured in this terminal.`

The API key had previously been configured only in another terminal session.

I resolved this by setting `OPENAI_API_KEY` in the terminal used to launch Streamlit. The key was not written into the source code or committed to the project repository.

This reinforced the importance of separating credentials from application code.

## Important limitation discovered

Participant review histories are stored persistently, but generated LLM summaries currently remain session-scoped.

When P01 was reopened:

- the user correction remained available;
- the review status remained available;
- the generated-summary counter returned to zero until summaries were generated again.

This means that the durable user-review layer and the temporary generation layer are currently separate.

This is acceptable for the planned single-session participant study, but it should be documented as a limitation. A future iteration may store the exact generated-summary snapshot associated with each review event if a persistent audit trail becomes necessary.

The interface may also need clearer language so users understand the difference between a saved review and a temporarily generated summary.

## Reflection

Today’s work moved ProjectOS from a single-user demonstration towards a research-ready prototype.

The participant-session feature is not simply an administrative addition. It protects the independence of participant responses and supports a more credible evaluation.

The manual test also revealed an important design distinction between AI-generated interpretations and user-authored project understanding. The AI summary may be temporary and regenerated, while the user’s correction represents a durable decision about the project state.

This distinction supports the reflective-AI position of ProjectOS: the system should assist reconstruction without silently replacing the practitioner’s interpretation.

## Ethics and privacy

The current study design includes the following safeguards:

- anonymous participant codes;
- separate consent and research-response records;
- no requirement to upload personal project files;
- a non-sensitive demonstration dataset;
- visible disclosure of OpenAI API use;
- instructions not to enter personal or sensitive information;
- optional permission for anonymised quotations and screenshots;
- the right to pause, skip questions or withdraw.

The participant documents remain drafts. Contact details, withdrawal deadline and the UAL data-retention period must be completed before recruitment.

## Progress status

| Task | Status | Evidence |
|---|---|---|
| Define research questions | Done | `research_questions.md` |
| Prepare information sheet | Done as draft | `participant_information_sheet.md` |
| Prepare consent form | Done as draft | `participant_consent_form.md` |
| Prepare test protocol | Done | `participant_test_protocol.md` |
| Prepare questionnaire and interview | Done | `post_test_questionnaire_and_interview.md` |
| Add participant data isolation | Done | Updated `src/streamlit_app.py` |
| Run automated tests | Done | 23 tests passed |
| Validate participant isolation | Done | P01 and P02 screenshots |
| Validate review persistence | Done | P01 reopened successfully |
| Conduct full timed rehearsal | Partial | Technical flow tested, full 35-minute procedure still required |
| Recruit formal participants | Not started | Recruitment must follow final document review |

## Next step

The next step is to complete one full timed rehearsal of the participant protocol from information sheet to closing interview.

Before formal recruitment, I must also complete the remaining placeholders in the participant documents:

- researcher email;
- supervisor surname and email;
- withdrawal deadline;
- UAL data-retention period.

## Day status

The core Day 8 objective is complete.

The user-research pack, participant-session isolation and technical validation are complete. Formal recruitment has not started, and one complete timed rehearsal is still required.