---
project: ProjectOS
document_type: test_result
category: prototype_evaluation
status: completed
date: 2026-09-17
prototype: reentry_brief_cli_v0
dataset: sample_echo_field
---

# Day 4 Re-entry Brief Retrieval Results

## Test purpose

This test examined whether the Iteration 0 retrieval pipeline could organise project evidence into the six sections of the proposed Project Re-entry Brief.

The test focused on:

- structural completeness;
- source visibility;
- category-aware retrieval;
- semantic relevance;
- and limitations in reconstructing the current project state.

The prototype did not generate summaries or make automatic project-state claims.

## Test configuration

- Documents loaded: 4
- Chunks created: 12
- Embedding model: `all-MiniLM-L6-v2`
- Maximum evidence items per section: 2
- Interface: command line
- Review status: `unreviewed`
- Test project: Echo Field

The four source categories were:

- `current_state`
- `decisions`
- `feedback`
- `process`

## Structural result

The command-line prototype successfully produced all six sections in the required order:

1. Current intention
2. What changed and why
3. Current versus superseded directions
4. Relevant feedback
5. Unresolved tensions
6. Possible next action

Each evidence item displayed:

- source path;
- document category;
- chunk identifier;
- semantic similarity score;
- and a source excerpt.

The output also kept `evidence_status` separate from `review_status`.

## Evidence-selection experiment

### Initial approach

The first version attempted to select one evidence item from each preferred source category.

This increased source diversity but sometimes forced weak evidence into the brief.

Examples included:

- Section 4 selecting a process chunk with a similarity score of `0.1277`;
- Section 6 selecting a process chunk with a similarity score of `0.1106`.

These chunks were technically from allowed categories, but they were not the strongest evidence for their sections.

### Revised approach

The selection rule was changed so that:

1. irrelevant source categories were excluded;
2. semantic ranking was preserved within the eligible categories;
3. the two highest-ranking eligible chunks were selected;
4. source diversity was no longer forced.

This improved several sections.

## Before-and-after observations

| Section | Initial selection | Revised selection | Observation |
|---|---|---|---|
| What changed and why | Decision and process evidence | Two decision chunks | The revised result provided a clearer change and rationale |
| Relevant feedback | `0.5016` and `0.1277` | `0.5016` and `0.3399` | The weak process result was replaced by directly relevant tutor feedback |
| Possible next action | `0.2353` and `0.1106` | `0.2353` and `0.1617` | The second result improved, although it may still describe historical feedback rather than a current action |
| Unresolved tensions | Included an explicit current blocker | Selected higher-scoring feedback chunks | Higher similarity did not produce a more accurate representation of unresolved project state |

## Manual assessment by section

### 1. Current intention

**Result: Partial pass**

The highest-ranked evidence clearly described the Echo Field project aim and its focus on visual feedback, body movement, control and engagement.

However, the second result mixed:

- future actions;
- unresolved scope questions;
- and a superseded hand-tracking direction.

It was related to the project’s current state but did not directly answer the question about current intention.

### 2. What changed and why

**Result: Pass**

The retrieved decision evidence described:

- the transition from hand tracking to whole-body movement;
- the instability of hand-gesture detection;
- and the rationale for choosing a more stable and understandable interaction method.

The evidence was relevant to both the change and its reasoning.

### 3. Current versus superseded directions

**Result: Pass**

The evidence successfully distinguished between:

- whole-body movement as the current interaction method;
- and hand-gesture recognition as a superseded direction.

This section provided the strongest example of successful project-state reconstruction.

### 4. Relevant feedback

**Result: Pass**

Both retrieved chunks came from tutor feedback.

The evidence covered:

- connecting colour changes to movement;
- explaining the change from hand gestures to whole-body movement;
- and considering multiple participants.

The revised selection was substantially stronger than the initial result.

### 5. Unresolved tensions

**Result: Partial pass**

The retrieved chunks were semantically related to questions and limitations in the project.

However, one chunk described feedback that had already been addressed, while another described multi-person interaction as possible future work.

The retrieval system did not select the explicit `Current blockers` section, even though it contained clearer unresolved issues.

This indicates that semantic similarity alone cannot reliably distinguish between:

- an unresolved problem;
- historical feedback;
- an implemented response;
- and future work.

### 6. Possible next action

**Result: Partial pass**

The first evidence item included documented actions such as:

- comparing intended and actual movement values;
- recording sudden changes caused by lighting;
- and deciding whether multi-person interaction belonged in the current scope.

The second result contained relevant tutor feedback but did not clearly represent a current next action.

The section therefore contained usable evidence but still required user review.

## Overall result

**Structural implementation: Pass**

**Semantic project-state reconstruction: Partial pass**

The prototype successfully created a source-grounded Project Re-entry Brief without generating unsupported summaries.

However, retrieval relevance alone was insufficient for determining whether evidence represented:

- the current project state;
- a resolved issue;
- historical feedback;
- a superseded direction;
- or a possible future investigation.

## Key finding

A higher semantic similarity score did not always produce a more accurate project-state interpretation.

The most important example occurred in the `Unresolved tensions` section. Higher-scoring feedback chunks were selected instead of the lower-scoring chunk that explicitly documented current blockers.

This demonstrates that semantic similarity should not be treated as factual confidence or project-state confidence.

## Design implication

ProjectOS should not rely only on vector similarity when reconstructing project state.

Later versions should investigate a combination of:

- document categories;
- explicit status metadata;
- temporal information;
- section headings;
- user confirmation;
- correction and rejection controls;
- and potentially LLM-assisted interpretation with visible citations.

The user must remain able to correct the reconstructed state.

## Research significance

This limitation helps distinguish ProjectOS from general-purpose file question-answering systems.

A generic RAG system can retrieve text that resembles a question. However, long-term creative project support requires the system to reason carefully about the role and lifecycle of that evidence.

Project re-entry depends not only on finding relevant information, but also on distinguishing what is:

- current;
- historical;
- resolved;
- unresolved;
- superseded;
- or still awaiting a decision.

## Decision

The revised similarity-ranked category filtering will remain as the Iteration 0 baseline.

No arbitrary similarity threshold will be introduced at this stage.

The observed failure cases will be retained for comparison with later metadata-aware and user-correctable versions.

## Next step

Add automated structural tests for the Re-entry Brief.

The tests should verify that:

- exactly six sections are created;
- the sections remain in the required order;
- no section contains more than two evidence items;
- every evidence item includes its source and chunk identifier;
- every section begins with `unreviewed`;
- and missing evidence can be represented as `insufficient`.