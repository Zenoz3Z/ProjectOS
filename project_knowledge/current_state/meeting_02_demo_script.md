---
project: ProjectOS
document_type: presentation_script
category: current_state
status: current
date: 2026-09-19
meeting: supervisor_meeting_02
estimated_duration: 3_minutes
---

# ProjectOS — Three-Minute Prototype Demonstration

## Opening

Since the previous meeting, I have narrowed ProjectOS from a general RAG-based project assistant to a specific project re-entry tool.

My current research question is:

**How can a source-grounded and correctable Project Re-entry Brief support creative students in reconstructing project state and deciding what to do next after an interruption?**

The problem I am focusing on is that a long-term creative project contains different types of information.

Some documents describe the current direction, while others describe previous experiments, implemented feedback, unresolved problems or ideas that are no longer active.

A general AI assistant may retrieve relevant text, but relevant text does not always represent the current project state.

## Show the interface

This is the current Streamlit prototype.

It uses a sample archive from my Echo Field project.

The prototype currently contains four documents, twelve evidence chunks and six Re-entry Brief sections.

The sections are:

1. Current intention
2. What changed and why
3. Current versus superseded directions
4. Relevant feedback
5. Unresolved tensions
6. Possible next action

The purpose of this structure is to support project re-entry rather than unrestricted conversation.

## Open one evidence item

Each section displays the evidence used by the system.

The user can inspect the source file, document category, chunk identifier, similarity score and original excerpt.

The similarity score only represents semantic relevance. I am not presenting it as factual confidence.

## Show the retrieval failure

The Unresolved Tensions section produced an important failure case.

The retrieval system selected tutor feedback that was semantically related to problems and limitations.

However, some of that feedback had already been addressed.

At the same time, a lower-ranked source explicitly described the current blockers.

This showed that semantic similarity alone cannot reliably distinguish between something that is current, resolved, historical or superseded.

## Show the correction

The user can therefore correct the reconstructed section.

In this example, I corrected the section to say:

**Slow movement feedback and lighting instability remain unresolved. Multi-person interaction is future work rather than a current blocker.**

The correction is saved in a review history.

When the project is opened again, the corrected state is restored, but the original retrieved evidence remains visible.

The correction does not silently replace the evidence.

## Research position

This is the main distinction between ProjectOS and general file question answering.

The system does not treat retrieval as a final answer.

It treats retrieval as evidence that the user must inspect, confirm, correct or reject.

The current prototype is intentionally limited. It does not yet include unrestricted chat, automatic contradiction detection or LLM-generated project summaries.

## Questions for supervisor

Before beginning formal Iteration 1, I would like to confirm three decisions.

First, is the narrowed focus on a correctable Project Re-entry Brief sufficiently specific?

Second, should the evaluation use participants’ own creative projects, a prepared common archive, or both?

Third, should Iteration 1 prioritise project-state metadata, the review interaction or interface clarity?

I would like to confirm these points before expanding the prototype or beginning participant testing.