# Day 2 — From Task Resumption Research to an Initial Interaction Flow

**Date:** 15 September 2026
**Project:** ProjectOS
**Status:** Completed

## Aim

My aim today was to investigate what happens when people return to interrupted or long-term work and translate the research findings into a more focused direction for ProjectOS. I wanted to understand whether project re-entry is simply an information-retrieval problem or whether it also involves reconstructing goals, decisions and unfinished thinking.

## Literature reviewed

I examined three sources from task-resumption and Personal Information Management research:

* Czerwinski, Horvitz and Wilhite (2004), *A Diary Study of Task Switching and Interruptions*
* Iqbal and Horvitz (2007), *Disruption and Recovery of Computing Tasks*
* Jones et al. (2017), *Personal Information Management*

For each paper, I recorded its research context, key findings, limitations and implications for ProjectOS. I also wrote a cross-paper reflection connecting the findings from the two task-resumption studies.

A Design Rationale source that I initially considered was not accessible without payment. I therefore excluded it rather than relying on an incomplete secondary account. It has not been used as evidence in today’s conclusions.

## Key findings

The task-resumption studies show that returning to work is not equivalent to reopening an application. Returned-to tasks are often longer, involve more documents and require users to reconstruct their mental context. Recovery can also continue after the user has reopened the relevant window because they may not yet remember their intention or partially completed reasoning.

Personal Information Management research extends this problem by showing that relevant information is often fragmented across files, messages, web pages and applications. Saving information does not guarantee that it will later be found, understood or used. Organising this information can also create a “clerical tax” that consumes time and attention.

These findings suggest that ProjectOS should not be framed as another file-management or document-search tool. Its more specific opportunity is to explore how source-grounded AI might help a creative practitioner reconstruct and critically reassess project context after time away.

## Design translation

I translated the literature into several initial design requirements:

* ProjectOS should reconstruct project-level context across multiple records.
* It should distinguish between locating information and recovering the meaning of earlier work.
* It should make goals, decisions, feedback and unresolved questions visible.
* Important generated statements should be connected to their sources.
* Users should be able to correct or reject the system’s interpretation.
* Previous decisions should be identifiable as current, outdated, uncertain or misinterpreted.
* Reflective prompts should remain optional.
* The system should work with existing project records and minimise additional documentation work.

This process narrowed the first prototype from a broad AI project-management platform to a more focused interaction: the **Project Re-entry Brief**.

## Initial interaction flow

I developed a four-screen low-fidelity flow:

1. **Project Home** — the user selects a project and reviews the imported records.
2. **Re-entry Request** — the user chooses or writes a question about the project.
3. **Project Re-entry Brief** — the system reconstructs the current aim, recent decisions, supporting reasons, feedback, unresolved questions and a possible next action.
4. **Evidence and Correction** — the user inspects the supporting passage and marks the interpretation as correct, outdated, uncertain or misinterpreted.

The correction screen returns to the Project Re-entry Brief, creating a review loop rather than treating the AI output as final.

The content shown in the wireframe is illustrative and has not been produced through user testing. The flow is an exploratory design proposal that will remain open to revision after supervisor feedback.

## Reflection

Today’s work changed my understanding of the role of RAG in ProjectOS. I initially thought of RAG mainly as a method for asking questions about uploaded project documents. The literature suggests that retrieval alone is not a sufficient contribution. A user might find the correct document while still being unable to remember why a decision was made or whether it remains relevant.

I now see RAG as a mechanism for evidence-grounded project reconstruction. The system should reconnect earlier records with the user’s present need while preserving access to the original evidence. The generated account should remain provisional and correctable because creative project records may be incomplete, contradictory or outdated.

Focusing on the Project Re-entry Brief also makes the project more achievable within the available development period. It provides one clear interaction to prototype and evaluate while leaving full project planning, autonomous agents and external integrations outside the first prototype.

## Evidence produced

* `literature/Day_2_Activity_Resumption_and_PIM_Notes.md`
* `research/Day_2_Design_Translation.md`
* `outputs/wireframes/project_reentry_flow_v0.png`

## Use of assistance

Generative AI assistance was used to help structure the literature notes, refine written expression and produce the initial low-fidelity flow. I selected the project scope, evaluated the relevance of the research findings and will continue to verify academic claims against the original papers.

## Progress record

| Field     | Record                                                                                              |
| --------- | --------------------------------------------------------------------------------------------------- |
| Day/date  | Day 2 — 15 September 2026                                                                           |
| Planned   | Study task resumption and translate the findings into design requirements                           |
| Completed | Literature notes, cross-paper reflection, design requirements and four-screen interaction flow      |
| Evidence  | Markdown research notes and exported wireframe                                                      |
| Problem   | One Design Rationale source was paywalled and was excluded                                          |
| Learning  | Project re-entry requires reconstruction and reassessment, not only document retrieval              |
| Next      | Build an exploratory document-ingestion and retrieval pipeline using a small set of project records |

## Current project statement

**ProjectOS uses source-grounded RAG to generate a correctable Project Re-entry Brief for long-term creative projects.**
