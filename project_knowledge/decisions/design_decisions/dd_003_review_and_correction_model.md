---
project: ProjectOS
document_type: design_decision
category: design_decisions
status: provisional
date: 2026-09-17
phase: pre_iteration_exploration
---

# DD-003: Review and Correction Model

## Decision

ProjectOS will store user review actions as a local, append-only event history.

The system will not overwrite the original retrieved evidence when a user confirms, corrects or rejects a reconstructed section.

This means that ProjectOS will preserve three separate layers:

1. the original project documents;
2. the evidence retrieved by the system;
3. the user’s interpretation and correction of that evidence.

## Purpose

The Project Re-entry Brief currently displays retrieved evidence, but every section begins as `unreviewed`.

The next prototype needs to represent what happens when the user reviews the reconstruction.

The purpose of this model is to make the Project Re-entry Brief genuinely correctable rather than only displaying a correction button without preserving its effect.

## Review levels

ProjectOS will distinguish between section-level review and evidence-level review.

### Section-level review

The following actions apply to an entire Re-entry Brief section:

- `confirm`
- `correct`
- `reject`

### Evidence-level review

The following action applies to an individual evidence chunk:

- `mark_superseded`

This distinction is necessary because a section may contain several evidence items. One item may be outdated while the rest of the section remains useful.

## Review actions

### Confirm

The user accepts the section as an adequate reconstruction of the project state.

The original evidence remains visible.

The resulting section review status becomes:

`confirmed`

### Correct

The user provides a corrected interpretation of the section.

A correction must contain non-empty user-written text.

The system must preserve:

- the retrieved evidence;
- the original reconstruction state;
- and the user correction.

The resulting section review status becomes:

`corrected`

The correction should not be silently inserted into the original source documents.

### Reject

The user decides that the section is misleading, irrelevant or unsupported.

The original evidence remains available for inspection.

The resulting section review status becomes:

`rejected`

The user may optionally record a reason.

### Mark as superseded

The user identifies an individual evidence chunk as historically relevant but no longer representative of the current project state.

This action requires a valid `chunk_id`.

The evidence is not deleted.

The action records that the evidence belongs to project history rather than the current project state.

## Append-only event history

Review actions will initially be stored as an append-only list of events.

A new event is added whenever the user reviews a section or evidence item.

Earlier review events will not be deleted or overwritten automatically.

This provides a visible record of how the user’s interpretation of the project changes over time.

## Proposed event structure

Each review event should contain:

- `event_id`
- `project_id`
- `timestamp`
- `section_id`
- `action`
- `user_correction`
- `reason`
- `target_chunk_id`

Example fields:

- `event_id`: a unique identifier;
- `project_id`: the project being reviewed;
- `timestamp`: when the action occurred;
- `section_id`: the Re-entry Brief section;
- `action`: confirm, correct, reject or mark_superseded;
- `user_correction`: required for a correction;
- `reason`: optional explanation;
- `target_chunk_id`: required when evidence is marked as superseded.

## Validation rules

The prototype should enforce the following rules:

1. `section_id` must match one of the six Re-entry Brief sections.
2. `action` must be one of the four supported actions.
3. `correct` requires non-empty `user_correction` text.
4. `mark_superseded` requires a non-empty `target_chunk_id`.
5. `confirm` does not require a correction.
6. `reject` may include an optional reason.
7. existing review events must remain unchanged when a new event is added.

## Local storage

The first version will store review events in a local JSON file.

Suggested location:

`data/reviews/sample_echo_field_reviews.json`

The file should contain:

- a schema version;
- a project identifier;
- and an ordered list of review events.

JSON is sufficient for the current prototype because:

- the dataset is small;
- the structure remains inspectable;
- no database setup is required;
- and the saved review history can be shown during prototype evaluation.

A database may be considered later only if the research prototype requires it.

## Relationship to evidence status

Review status and evidence status must remain separate.

For example:

- a section can have `supported` evidence but still be `rejected`;
- a section can have `conflicting` evidence and later be `corrected`;
- a section with `insufficient` evidence may require the user to add a correction.

The user’s review does not change the original semantic similarity score.

## Why evidence must remain visible

Removing evidence after a correction would hide why the system made its original reconstruction.

Keeping the evidence visible supports:

- transparency;
- comparison;
- reflective judgement;
- error analysis;
- and later evaluation of the prototype.

This is especially important because the Day 4 retrieval test showed that highly similar evidence may still describe a resolved or historical project state.

## Non-goals

This version will not include:

- user accounts;
- cloud storage;
- collaborative editing;
- participant data;
- automatic rewriting of source documents;
- automatic acceptance of corrections as factual truth;
- or a polished graphical review interface.

## Completion criteria

The review model is successfully implemented when:

- a valid review event can be created;
- a correction without text is rejected;
- a superseded action without a chunk identifier is rejected;
- events are saved to JSON;
- adding an event does not remove earlier events;
- the saved file can be loaded again;
- and automated tests verify the validation rules.

## Research rationale

The review model operationalises the idea of reflective AI.

Instead of presenting project reconstruction as a finished AI answer, ProjectOS treats it as a proposal that the user must inspect.

The user’s correction becomes part of the reflective process rather than being treated only as system feedback.

This supports the wider research question because returning to a creative project involves interpretation, judgement and negotiation between current intentions and historical evidence.

## Status

This model is provisional and belongs to pre-iteration technical exploration.

It may be revised after supervisor feedback and interaction testing.