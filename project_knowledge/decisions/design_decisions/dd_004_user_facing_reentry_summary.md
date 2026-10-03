---
project: ProjectOS
document_type: design_decision
category: decisions
status: current
date: 2026-09-30
decision_id: DD-004
---

# DD-004 — User-facing Project Re-entry Summary

## Context

During the second supervisor meeting, the current Streamlit prototype was recognised as technically functional but difficult for a first-time user to understand.

The prototype exposed implementation-oriented terms such as `evidence status`, `retrieved evidence`, `similarity score`, `chunk ID` and `review this reconstruction`. These terms were useful during technical development, but they did not clearly communicate what the system had discovered about the project or what the user was expected to do.

The supervisor suggested presenting the findings in simpler language, creating concise textual summaries and making the interface easier to read before beginning participant testing.

## Design problem

The current interface requires the user to interpret retrieval results before understanding the state of the project.

This reverses the intended hierarchy. A user returning to an interrupted creative project should first understand:

1. what the project is currently trying to achieve;
2. where the work was left;
3. what changed;
4. which directions are no longer current;
5. which problems remain unresolved;
6. what action may come next.

Source evidence should remain available, but it should support the summary rather than dominate the interface.

## Decision

Iteration 1 will introduce a user-facing Project Re-entry Summary.

Each section will present information in the following order:

1. a plain-language section title;
2. a concise project-state summary;
3. a short indication of whether supporting records were found;
4. a clear question asking whether the summary is still accurate;
5. user review controls;
6. supporting project records inside a collapsed optional area.

The underlying retrieval and review mechanisms will remain unchanged where possible.

## User-facing section titles

The six sections will be renamed as follows:

1. `Current intention` becomes `What this project is trying to achieve`
2. `What changed and why` becomes `What changed`
3. `Current versus superseded directions` becomes `Current and previous directions`
4. `Relevant feedback` becomes `Feedback to remember`
5. `Unresolved tensions` becomes `Questions and problems still open`
6. `Possible next action` becomes `A possible next step`

## User-facing language

The interface language will be revised as follows:

- `Evidence status` becomes `Supporting records`
- `Supported` becomes `Records found`
- `Insufficient` becomes `More information may be needed`
- `Conflicting` becomes `The records may describe different project states`
- `Retrieved evidence` becomes `View supporting project records`
- `Review this reconstruction` becomes `Is this still accurate?`
- `Confirm` becomes `Yes, this is correct`
- `Correct` becomes `Update this summary`
- `Reject` becomes `This is not accurate`
- `Mark as superseded` becomes `This belongs to an older direction`
- `User correction` becomes `Your updated understanding`

Technical terms such as similarity score and chunk identifier will not appear in the primary interface. They may remain available inside an optional technical details area for research transparency and debugging.

## Information hierarchy

The primary interface should answer the user’s question:

> Where did I leave this project, and what should I understand before continuing?

The page will contain:

### Project overview

A short explanation of what ProjectOS has done and what the user should do next.

### Re-entry snapshot

The six project-state sections presented as readable summary cards.

### User review

Each card asks whether the reconstructed information still reflects the project.

### Supporting records

Original source excerpts remain accessible in a collapsed area so that the user can inspect the basis of the summary.

## Review interaction

The review mechanism will continue to distinguish system reconstruction from user interpretation.

The user can:

- accept the summary;
- provide a correction;
- reject an inaccurate summary;
- mark individual records as belonging to an older project direction.

A correction must not remove or overwrite the original source evidence. The interface should show that the updated interpretation belongs to the user.

## Research rationale

This redesign does not remove source grounding. It separates two layers:

1. the user-facing project-state interpretation;
2. the underlying records that support or complicate that interpretation.

This separation is important to the research question because ProjectOS is investigating whether a source-grounded and correctable brief can support project re-entry. Participants must be able to understand the brief before they can meaningfully evaluate or correct it.

## Completion criteria

The redesign will be considered successful when:

- a first-time user can identify the purpose of the page without an explanation from the developer;
- every section contains a readable project-state summary;
- implementation terminology is removed from the main reading flow;
- supporting records remain visible on demand;
- the user can clearly accept, update or reject each section;
- saved corrections remain separate from original evidence;
- all existing automated tests continue to pass;
- the prototype is ready for a formative walkthrough before participant testing.

## Non-goals

This iteration will not add:

- unrestricted project chat;
- automatic long-term monitoring;
- cloud deployment;
- a new vector database;
- automatic contradiction detection;
- participant data collection.

These may only be added later if they support an observed research or interaction need.