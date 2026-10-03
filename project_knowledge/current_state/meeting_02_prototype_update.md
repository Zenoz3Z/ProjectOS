---
project: ProjectOS
document_type: meeting_preparation
category: current_state
status: current
date: 2026-09-19
meeting: supervisor_meeting_02
---

# ProjectOS — Prototype Update for Supervisor Meeting 2

## Current research question

**How can a source-grounded and correctable Project Re-entry Brief support creative students in reconstructing project state and deciding what to do next after an interruption?**

## Current position

ProjectOS has been narrowed from a general RAG-based project assistant to a specific project re-entry interaction.

The current prototype is designed for creative students returning to a long-term project after an interruption.

It does not attempt to manage every part of a creative project or provide unrestricted AI chat. Instead, it reconstructs a provisional project state from visible source evidence and asks the user to review that reconstruction.

## Why this is not general file question answering

General AI tools can search, summarise and answer questions about uploaded documents.

However, returning to a long-term creative project requires the user to distinguish between:

- current intentions;
- previous experiments;
- implemented feedback;
- unresolved blockers;
- superseded directions;
- and possible next actions.

A semantically relevant document may still describe an outdated or already resolved project state.

ProjectOS therefore treats retrieval as evidence rather than as a final answer.

## Project Re-entry Brief

The prototype organises retrieved evidence into six sections:

1. Current intention
2. What changed and why
3. Current versus superseded directions
4. Relevant feedback
5. Unresolved tensions
6. Possible next action

Each section displays:

- evidence status;
- review status;
- source path;
- source category;
- chunk identifier;
- semantic similarity score;
- and a source excerpt.

## Correctable interaction

The user can:

- confirm a reconstruction;
- correct a reconstruction;
- reject a reconstruction;
- or identify evidence as superseded.

Review actions are stored as an append-only history.

The original evidence remains visible after a correction. The user correction is displayed as a separate layer rather than silently replacing the system output.

## Current technical prototype

The prototype currently includes:

- Markdown, text and PDF document loading;
- overlapping document chunking;
- sentence-transformer embeddings;
- semantic retrieval;
- category-aware evidence filtering;
- a six-section Re-entry Brief;
- local JSON review history;
- command-line output;
- and a Streamlit interface.

The current sample project contains:

- 4 project documents;
- 12 evidence chunks;
- 6 Re-entry Brief sections;
- and 2 saved review events.

The current automated test suite contains:

- 17 passing tests.

The initial retrieval evaluation produced:

- Hit@1: 4/6, or 66.67%;
- Hit@3: 6/6, or 100%.

## Key prototype finding

The most important finding was that higher semantic similarity did not always produce a more accurate reconstruction of project state.

For the Unresolved Tensions section, the retrieval system selected highly similar tutor-feedback chunks. However, some of this feedback had already been addressed.

A lower-ranked chunk explicitly documented the current blockers but was not selected.

This exposed a limitation of similarity-based retrieval:

> Semantic relevance does not establish whether evidence is current, resolved, historical or superseded.

The user corrected the section to state:

> Slow movement feedback and lighting instability remain unresolved. Multi-person interaction is future work rather than a current blocker.

The correction was saved and restored during the next project re-entry while the original evidence remained visible.

## Current research argument

The current prototype suggests that the problem is not only retrieving relevant project material.

The research problem is how AI-supported reconstruction should represent uncertainty, evidence status and user judgement when a person returns to a long-term creative project.

The prototype therefore explores a relationship between:

- retrieval;
- reflective judgement;
- project memory;
- and user agency.

## What the project is not currently claiming

The prototype does not claim to:

- understand the complete project automatically;
- detect every contradiction;
- determine factual confidence from similarity;
- replace the user’s reflective judgement;
- or provide a finished project-management platform.

The current interface is a research prototype used to investigate project re-entry.

## Proposed next iteration

Subject to supervisor feedback, Iteration 1 would focus on:

1. improving how current and superseded evidence are represented;
2. refining the review interaction;
3. testing whether the six-section brief is understandable;
4. observing where users accept, correct or reject reconstruction;
5. and recording whether the brief helps users identify a next action.

The priority would be interaction quality and research evidence rather than adding broad AI features.

## Proposed evaluation direction

A small formative study could involve creative students using a prepared project archive or their own documented project.

Participants would:

1. inspect a project archive after a simulated interruption;
2. review the generated Re-entry Brief;
3. confirm, correct or reject individual sections;
4. identify the project’s current state;
5. and decide on a next action.

Possible evaluation areas include:

- perceived clarity;
- trust in the reconstruction;
- usefulness of visible evidence;
- effort required to correct the system;
- ability to distinguish current and superseded directions;
- and perceived readiness to resume the project.

No participant testing will begin until the scope and method have been confirmed.

## Questions for supervisor

### 1. Research scope

Is the narrowed focus on a source-grounded and correctable Project Re-entry Brief sufficiently specific for the final project?

### 2. Research contribution

Is it appropriate to frame the contribution around the difference between semantic relevance and project-state accuracy?

### 3. Evaluation

Should the study use participants’ own creative project archives, a prepared common archive, or a combination of both?

### 4. Comparison

Would a comparison with a conventional file-summary workflow strengthen the evaluation, or would a qualitative formative study be more appropriate for the available time?

### 5. Iteration priority

Should Iteration 1 prioritise:

- state and metadata handling;
- the correctable review interaction;
- or interface clarity?

### 6. Final scope

Which features should remain explicitly outside the final prototype to keep the research manageable?

## Three-minute demonstration sequence

### Step 1 — State the problem

Explain that project files contain mixed states: current aims, historical experiments, implemented feedback and unresolved issues.

### Step 2 — Show the six-section brief

Show how the system organises retrieved evidence into a structured project re-entry view.

### Step 3 — Open the evidence

Show the source, category, chunk identifier and similarity score.

Explain that similarity is visible but is not presented as factual confidence.

### Step 4 — Show the retrieval failure

Open the Unresolved Tensions section and explain that the system retrieved relevant feedback but confused resolved feedback with current blockers.

### Step 5 — Show the correction

Show the saved user correction while keeping the original evidence visible.

### Step 6 — Show persistence

Show that the interface restores the correction after reopening the project.

### Step 7 — Ask for direction

Ask the supervisor to confirm the research scope, evaluation method and priority for Iteration 1.