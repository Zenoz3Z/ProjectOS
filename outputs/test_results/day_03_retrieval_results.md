---
project: ProjectOS
document_type: experiment_result
experiment: iteration_0_retrieval_baseline
date: 2026-09-16
status: completed
---

# Day 3 Retrieval Baseline Results

## Purpose

The purpose of this experiment was to determine whether a lightweight semantic retrieval pipeline could identify relevant evidence from a small collection of long-term creative project documents.

The test used documents from my previous Echo Field project as a controlled demonstration corpus. This experiment evaluates document retrieval only. It does not yet evaluate generated answers, reflection quality or user experience.

## Technical configuration

- Embedding model: `all-MiniLM-L6-v2`
- Number of source documents: 4
- Number of chunks: 12
- Maximum chunk size: 120 words
- Chunk overlap: 30 words
- Number of retrieved results per query: 3
- Similarity method: cosine similarity using normalised embeddings
- Evaluation set: 6 manually defined project questions

## Source document categories

The demonstration corpus contained:

- current project state;
- design decisions;
- tutor feedback;
- process documentation.

Each retrieved chunk retained its source path, category and unique chunk identifier.

## Results

| ID | Expected source | Expected-source rank | Result |
|---|---|---:|---|
| Q01 | `decisions/design_notes.md` | 1 | Pass |
| Q02 | `current_state/goals.md` | 3 | Pass |
| Q03 | `feedback/tutor_feedback.md` | 1 | Pass |
| Q04 | `process/project_log.md` | 1 | Pass |
| Q05 | `feedback/tutor_feedback.md` | 1 | Pass |
| Q06 | `process/project_log.md` | 2 | Pass |

### Summary metrics

- Hit@1: 4/6 — 66.67%
- Hit@3: 6/6 — 100.00%

## Observations

The system retrieved the expected source within the first three results for all six questions. This indicates that the embedding-based baseline can distinguish between project goals, design decisions, process records and tutor feedback within the demonstration corpus.

The strongest result concerned the decision to replace hand tracking with whole-body movement. The first two retrieved chunks came from the design decision document and contained both the original technical problem and the rationale for the final decision.

Questions about tutor feedback and movement-strength values also returned the expected source as the first result.

## Ranking limitations

Two questions did not return the predefined source at Rank 1.

For Q02, the design decision document ranked above the current-state document. This was not entirely irrelevant because both documents describe the current whole-body interaction method. The result shows that evaluating retrieval using only one expected file can be too restrictive when several project documents contain valid supporting evidence.

For Q06, the current-state document ranked above the process log. The expected process log still appeared at Rank 2. This suggests that the retriever can locate related information but does not yet consistently prioritise detailed historical evidence over current-state summaries.

The similarity score should not be interpreted as factual confidence. It only represents semantic closeness between the question and each chunk.

## Reflection

This experiment demonstrates that a relatively simple retrieval pipeline can reconnect a user with evidence distributed across a long-term creative project. However, successful retrieval is not the same as useful reflective support.

ProjectOS will need to distinguish between current decisions, historical experiments, feedback and superseded directions. It should also show its sources clearly so that the user can inspect and correct the reconstructed project state.

The baseline therefore supports the technical feasibility of the project while also identifying a design challenge: the system must organise retrieved evidence according to its role in the creative process, rather than treating all semantically similar passages as equally useful.

## Limitations

This evaluation used:

- a small demonstration corpus;
- documents written specifically for the technical prototype;
- six developer-authored questions;
- one expected source per question;
- no external participants;
- no answer-generation component.

The results cannot be treated as evidence of user benefit or general retrieval performance. A later iteration should use a larger and less controlled project corpus, relevance judgements and user testing.

## Baseline decision

The current retrieval configuration will be retained as the Iteration 0 baseline:

- 120-word chunks;
- 30-word overlap;
- `all-MiniLM-L6-v2` embeddings;
- Top 3 source-grounded retrieval.

No optimisation will be performed solely to improve these six test scores. Later changes should be justified by observed retrieval failures or user needs.