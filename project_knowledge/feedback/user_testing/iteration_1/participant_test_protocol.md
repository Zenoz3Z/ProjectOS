---
project: ProjectOS
document_type: participant_test_protocol
category: user_testing
iteration: 1
date: 2026-10-01
status: historical_draft_superseded_for_round_1
estimated_duration: 30-35 minutes
---

# ProjectOS Iteration 1 Participant Test Protocol

> **Historical demo-only draft (1 October 2026), retained for provenance. Do not administer this procedure for Round 1.** Its Echo Field task, generation step, timings and consent checks are superseded by the [Round 1 protocol draft](study_protocol_round_1_draft.md). Anna confirmed on 9 October 2026 that no amendment to the existing ethics approval is required; current participant storage wording remains for Meeting 3 review. Formal recruitment and P01 have not started. The original procedure below is unchanged.

Formal ratings use only [R1-R7, Round 1 v1](round_1_templates/post_test_ratings_template.md). Do not combine any ratings associated with this historical procedure with formal Round 1 results or relabel pilot responses.

## Study purpose

This session investigates how creative students and practitioners understand, inspect and correct a Project Re-entry Brief generated from project records.

The session evaluates:

- clarity of the reconstructed project state;
- visibility and usefulness of source evidence;
- understanding of current and superseded directions;
- perceived control over AI-generated interpretations;
- usefulness of the proposed next action;
- confusion, effort and misleading outputs.

This is an exploratory usability and perception study. It does not attempt to prove that ProjectOS improves creativity or productivity.

## Participant profile

Participants should:

- be at least 18 years old;
- be a creative student or practitioner;
- have experience with projects continuing across multiple sessions;
- be able to provide informed consent.

No technical or AI experience is required.

## Test material

The participant will use the prepared `sample_echo_field` demonstration project.

Participants will not upload their own files during Iteration 1.

## Session duration

Expected duration: 30–35 minutes.

Suggested structure:

1. Introduction and consent — 5 minutes
2. Background questions — 3 minutes
3. Scenario and task introduction — 2 minutes
4. Prototype tasks — 12–15 minutes
5. Post-test questionnaire — 5 minutes
6. Short interview — 8–10 minutes

## Materials required

Before the session, prepare:

- Participant Information Sheet;
- Participant Consent Form;
- participant code;
- ProjectOS prototype;
- `sample_echo_field` demonstration project;
- observation sheet;
- post-test questionnaire;
- interview questions;
- a working browser and local Streamlit server.

## Prototype preparation

Before each session:

- activate the `projectos` environment;
- launch the Streamlit prototype;
- confirm that the demonstration project loads correctly;
- confirm that all six Re-entry Brief sections can be generated;
- use a clean participant-specific review history;
- ensure that corrections from previous participants are not visible;
- confirm that no personal or sensitive information is present;
- close unrelated windows and notifications;
- assign a participant code such as `P01`.

The researcher must not silently delete previous participant data. Each participant’s review data should be stored separately using the assigned participant code.

## Researcher behaviour

During the session, the researcher should:

- read the same instructions to each participant;
- avoid explaining the intended answer before a task;
- avoid describing a summary as correct or incorrect;
- allow the participant time to explore;
- provide help only when the participant cannot continue;
- record any help given;
- avoid defending the prototype;
- remind the participant that the system, rather than the participant, is being evaluated.

## Opening script

Thank you for taking part in this study.

Today you will use a prototype called ProjectOS. It is designed to help creative practitioners return to a long-term project by reconstructing its current state from existing project records.

The prototype may produce incomplete or incorrect interpretations. I am interested in how understandable the output is, whether the supporting evidence helps you assess it, and whether you feel able to correct it.

This is a test of the prototype, not a test of you. There are no penalties for making mistakes or asking for help.

Please explain what you are thinking while you complete the tasks where possible. You may pause, skip a question or stop the session at any time.

Before we begin, do you have any questions?

## Consent check

Before continuing, confirm:

- [ ] The participant has read the Participant Information Sheet.
- [ ] The participant has had an opportunity to ask questions.
- [ ] The Participant Consent Form has been completed.
- [ ] The participant has been assigned a participant code.
- [ ] The participant understands that no personal project files are required.

Do not begin the prototype test until these conditions are met.

## Background questions

Ask the participant:

1. What type of creative practice or course are you involved in?
2. How often do you work on projects that continue over several weeks or months?
3. Have you ever found it difficult to return to a project after an interruption?
4. What do you normally use to remember project decisions, feedback and next steps?
5. How often do you use generative AI tools in your creative or academic work?

Record brief notes without collecting unnecessary personal information.

## Scenario

Read the following scenario to the participant:

Imagine that you previously worked on a creative technology project called Echo Field. The project uses body movement to control responsive visual feedback.

You have not worked on the project for several weeks. The project folder contains goals, process notes, design decisions and tutor feedback. You now need to understand the current project state and decide what to do next.

ProjectOS has used these records to prepare a Project Re-entry Brief.

Please use the brief as if you were returning to this project after an interruption.

## Think-aloud instruction

While using the prototype, please say what you are looking at, what you think it means and anything you find confusing.

You do not need to speak continuously. I may occasionally ask, “What are you thinking at this point?” but I will avoid telling you what an item means unless you cannot continue.

## Prototype tasks

### Task 1 — Generate the brief

Ask the participant:

Please generate the Project Re-entry Brief and describe your first impression of the result.

Observe:

- whether the generation button is easy to find;
- whether the purpose of the page is understood;
- whether the participant notices that the output is provisional;
- whether the participant waits for generation successfully;
- first comments about clarity or information density.

Do not explain the six sections unless the participant cannot continue.

### Task 2 — Identify the current intention

Ask the participant:

In your own words, what is the current aim of Echo Field?

Observe:

- whether the participant uses the generated summary;
- whether the summary is interpreted accurately;
- whether the participant opens the supporting evidence;
- whether current and historical information are confused.

### Task 3 — Identify an important change

Ask the participant:

What important interaction change was made during the project, and why was it made?

Observe:

- whether the participant identifies the move from hand gestures to whole-body movement;
- whether the practical reason for the change is understood;
- whether the participant distinguishes the earlier experiment from the current method.

### Task 4 — Distinguish current and superseded directions

Ask the participant:

Which interaction direction is current, and which direction has been superseded?

Observe:

- whether the project-state label is noticed;
- whether the word “superseded” is understood;
- whether supporting evidence is required;
- whether the participant expresses uncertainty.

Do not define “superseded” immediately. If the participant cannot continue, record that help was required before explaining that it means a previous direction that has been replaced.

### Task 5 — Inspect the supporting evidence

Ask the participant:

Choose one section and inspect its supporting project records. Do the records appear to support the summary?

Follow up with:

What made you decide that the summary was or was not supported?

Observe:

- whether evidence controls are discoverable;
- which section is selected;
- whether source names and excerpts are understandable;
- whether similarity information is useful or distracting;
- whether the participant treats the AI summary as automatically correct.

### Task 6 — Identify unresolved tensions

Ask the participant:

According to the brief, what issues remain unresolved in the project?

Observe:

- whether current limitations are distinguished from future possibilities;
- whether multi-person interaction is interpreted as a current blocker or future work;
- whether the participant notices any misleading combination of project states;
- whether the evidence is opened before answering.

The researcher must not tell the participant in advance that this section previously produced a misleading interpretation.

### Task 7 — Identify the next action

Ask the participant:

What does the brief suggest should be addressed next? Does this appear actionable?

Observe:

- whether the next action is found quickly;
- whether it is understood as documented rather than automatically correct;
- whether the participant considers it specific enough to act on;
- whether the source evidence is inspected.

### Task 8 — Review a reconstruction

Ask the participant:

Choose one section. Confirm it if you agree with it, update it if you think it is incomplete or misleading, or reject it if you do not think it should be used.

Observe:

- which review action is selected;
- whether the difference between Confirm, Update and Reject is understood;
- whether the participant can enter and save a correction;
- whether the interface clearly distinguishes the user’s interpretation from the AI summary;
- whether the previous AI summary and source evidence remain accessible.

Do not instruct the participant which section or review action to choose.

### Task 9 — Relate the experience to personal practice

Ask the participant:

Thinking about your own creative work, when might a brief like this be useful, and when might it create additional work or confusion?

This question concerns the participant’s experience. Do not ask them to reveal confidential details or upload their own files.

## Researcher observation prompts

During the tasks, record:

- task completed: yes, partial or no;
- approximate completion time;
- whether help was required;
- evidence opened: yes or no;
- review action used;
- visible hesitation or confusion;
- notable participant comments;
- unexpected behaviour;
- technical errors.

## Help protocol

If a participant cannot continue:

1. wait briefly to allow independent exploration;
2. ask, “What would you expect to happen here?”;
3. provide the smallest necessary hint;
4. record the hint in the observation notes;
5. avoid explaining the intended interpretation unless required to continue.

Suggested help levels:

- Level 0 — no help;
- Level 1 — general prompt;
- Level 2 — interface location indicated;
- Level 3 — direct instruction provided;
- Level 4 — researcher completes the action.

## Technical failure procedure

If the prototype fails:

1. record the section and action that caused the failure;
2. save any visible error message without including participant identity;
3. restart the prototype once if appropriate;
4. continue with screenshots or a prepared demonstration only if the participant agrees;
5. label affected tasks as incomplete due to technical failure;
6. do not describe technical failure as participant error.

## Post-task transition

After the prototype tasks, say:

Thank you. You have completed the prototype tasks. I will now ask you to complete a short questionnaire and then discuss your experience. Your feedback can be positive, negative or mixed. I am interested in what actually happened rather than what you think I would prefer to hear.

## Closing script

Thank you for taking part.

Your responses will be associated with your participant code rather than your name. Please remember that you may contact me before the stated withdrawal deadline if you would like your identifiable research data removed.

Do you have any final questions or comments about the study?

## After-session procedure

After the participant leaves:

- confirm that the consent form is stored separately from study responses;
- label notes using the participant code only;
- save the participant’s review events separately;
- remove names or identifying details from written notes;
- record any technical problem;
- write a short researcher reflection;
- reset the prototype for the next participant;
- do not overwrite the previous participant’s data.

## Completion criteria

The protocol is ready for pilot testing when:

- the information sheet and consent form are complete;
- all placeholders have been filled;
- participant-specific review storage is available;
- the questionnaire and interview guide are complete;
- the researcher has completed one full rehearsal;
- the session can be completed within approximately 35 minutes;
- no participant is required to provide personal project data.
