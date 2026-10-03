---
project: ProjectOS
document_type: design_decision
category: design_decisions
status: provisional
date: 2026-09-17
iteration: pre_iteration
---

# DD-002: Project Re-entry Brief Schema

## Decision

ProjectOS will reconstruct project state through a structured **Project Re-entry Brief** rather than an unrestricted AI chat interface.

The brief is designed to help a creative practitioner return to a long-term project after an interruption. It will retrieve relevant project evidence, organise it into a fixed structure and allow the user to review the reconstructed state.

The first technical version will remain source-grounded and will not use an LLM to generate unsupported project summaries.

## Research question

**How can a source-grounded and correctable Project Re-entry Brief support creative students in reconstructing project state and deciding what to do next after an interruption?**

## Design principles

### 1. Source-grounded

Every reconstructed section must display the source evidence used to support it.

The system should not present an interpretation without showing where the information came from.

### 2. Status-aware

ProjectOS should distinguish between:

- current project directions;
- previous experiments;
- design and technical decisions;
- unresolved questions;
- tutor or participant feedback;
- superseded directions.

This is necessary because similarity-based retrieval alone cannot determine whether a document describes the current project state.

### 3. Correctable

The reconstructed project state should be treated as provisional.

The user must be able to confirm, correct or reject the system’s interpretation.

### 4. Evidence before interpretation

Iteration 0 will display retrieved evidence before introducing AI-generated synthesis.

This allows retrieval quality and source selection to be examined independently from language-model generation.

### 5. User agency

ProjectOS should support reflection and decision-making without claiming authority over the creative project.

The user remains responsible for deciding which evidence is accurate, relevant and current.

## Re-entry Brief sections

The brief will contain six sections in the following order.

### 1. Current intention

**Purpose:** Identify the project’s most recently documented aim, direction or intended outcome.

**Retrieval question:**

> What is the current aim or intended direction of this project?

**Evidence priority:**

1. `current_state`
2. `decisions`

This section should not assume that the newest file automatically contains the correct project intention.

### 2. What changed and why

**Purpose:** Recover important changes in the project and the reasons behind them.

**Retrieval question:**

> What important changes were made to the project, and why were they made?

**Evidence priority:**

1. `decisions`
2. `process`

The section should connect a change with its documented rationale whenever possible.

### 3. Current versus superseded directions

**Purpose:** Separate the current project direction from ideas or approaches that were previously explored but are no longer active.

**Retrieval question:**

> Which project directions are current, and which directions have been replaced or superseded?

**Evidence priority:**

1. `current_state`
2. `decisions`
3. `process`

Iteration 0 will not automatically determine whether two statements contradict each other. It will retrieve relevant evidence and expose the distinction for user review.

### 4. Relevant feedback

**Purpose:** Recover feedback that may influence the present project state.

**Retrieval question:**

> What tutor or user feedback is relevant to the current project direction?

**Evidence priority:**

1. `feedback`
2. `process`

Feedback should remain identifiable as feedback rather than being presented as an accepted project decision.

### 5. Unresolved tensions

**Purpose:** Surface open questions, technical limitations, conflicting directions or issues that have not yet been resolved.

**Retrieval question:**

> What unresolved questions, tensions or limitations remain in the project?

**Evidence priority:**

1. `current_state`
2. `process`
3. `feedback`
4. `decisions`

The system must not invent a tension when no supporting evidence is available.

### 6. Possible next action

**Purpose:** Retrieve documented next steps that may help the user resume work.

**Retrieval question:**

> What is the next documented action or decision that should be addressed?

**Evidence priority:**

1. `current_state`
2. `process`
3. `feedback`

Iteration 0 will retrieve possible next actions from project materials. It will not independently generate or prescribe a new action.

## Section data structure

Each section should use the following structure:

```json
{
  "section_id": "current_intention",
  "title": "Current intention",
  "question": "What is the current aim or intended direction of this project?",
  "evidence_status": "supported",
  "review_status": "unreviewed",
  "evidence": [
    {
      "rank": 1,
      "source": "current_state/goals.md",
      "category": "current_state",
      "chunk_id": "current_state__goals_chunk_001",
      "similarity_score": 0.52,
      "excerpt": "Retrieved source text appears here."
    }
  ],
  "user_correction": null
}
```

This structure separates retrieved evidence from the user’s review of that evidence.

## Evidence status

Each section will use one of three evidence states.

### Supported

At least one relevant piece of source evidence was retrieved for the section.

A supported status means that evidence exists. It does not guarantee that the evidence is factually correct or still current.

### Conflicting

Retrieved evidence appears to describe incompatible project states, decisions or directions.

Iteration 0 will not claim to detect semantic contradictions automatically. A conflicting status may initially be assigned through:

- explicit document metadata;
- simple comparison rules;
- or manual user review.

### Insufficient

No evidence from the relevant source categories was retrieved for the section.

The system should display the absence of evidence instead of generating a plausible-sounding answer.

A low similarity score alone will not automatically prove that evidence is incorrect. Similarity thresholds must be tested rather than assumed.

## Review interaction

The later interface should provide the following review controls for each section.

### Confirm

The user accepts the reconstructed section as an accurate representation of the project.

The review status becomes:

`confirmed`

### Correct

The user adds a corrected interpretation.

The original retrieved evidence remains visible so that the correction does not erase the system’s earlier reconstruction.

The review status becomes:

`corrected`

### Reject

The user marks the reconstruction as misleading, irrelevant or unsupported.

The review status becomes:

`rejected`

### Mark as superseded

The user indicates that a retrieved direction was previously relevant but is no longer part of the current project state.

The evidence remains in the project history but should not be treated as the current direction.

The default review status for every section is:

`unreviewed`

## Iteration 0 output

The command-line version will display:

1. the section title;
2. the retrieval question;
3. the evidence status;
4. up to two relevant evidence chunks;
5. the source of each chunk;
6. the category of each source;
7. the chunk identifier;
8. the similarity score;
9. a short source excerpt;
10. the default review status `unreviewed`.

The command-line version will not yet save user corrections.

## Non-goals for this version

The Day 4 prototype will not include:

- unrestricted AI chat;
- LLM-generated project summaries;
- automatic semantic contradiction detection;
- automatic confidence claims;
- a vector database;
- a polished web interface;
- participant data;
- final evaluation measures.

These features should only be added when they support an observed research or interaction need.

## Completion criteria

The schema is successfully implemented when:

- all six sections appear in the correct order;
- each section runs its own retrieval question;
- each section retrieves up to two evidence chunks;
- every evidence item displays its source;
- every evidence item displays its category and chunk identifier;
- missing evidence is explicitly represented as `insufficient`;
- semantic similarity is not described as factual confidence;
- retrieved evidence is kept separate from user review;
- every section begins with the review status `unreviewed`;
- no unsupported project claims are generated.

## Rationale

This structure differentiates ProjectOS from general file question-answering tools.

General AI assistants can search files, summarise documents and answer questions. However, returning to a long-term creative project requires more than retrieving similar text. The user needs to reconstruct what the project is currently trying to achieve, understand why important changes were made, distinguish active decisions from abandoned directions and identify unresolved work.

The Project Re-entry Brief therefore treats project state as provisional, evidence-based and correctable.

This supports the research focus on how AI-assisted reconstruction may help, distort or increase the effort involved in returning to long-term creative work.

## Limitations

The initial schema depends on the quality and structure of the project documentation.

Relevant evidence may be missed when:

- documents use ambiguous language;
- categories are assigned incorrectly;
- important decisions were never recorded;
- different documents describe the same decision using unrelated terms;
- or retrieval ranks semantically similar but outdated evidence too highly.

These limitations should be recorded during prototype testing rather than hidden.

## Status

This schema is provisional and belongs to pre-iteration design and technical exploration.

It may be revised after:

- supervisor feedback;
- retrieval testing;
- prototype observation;
- and the first formal design iteration.

Changes to the schema should be recorded as new design decisions rather than silently replacing the reasoning documented here.