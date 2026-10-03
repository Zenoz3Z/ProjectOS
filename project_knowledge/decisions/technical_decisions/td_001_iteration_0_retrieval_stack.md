---
project: ProjectOS
document_type: technical_decision
decision_id: TD-001
date: 2026-09-16
status: accepted_for_iteration_0
---

# TD-001: Iteration 0 Retrieval Stack

## Decision

For the Iteration 0 technical prototype, I will use a small and transparent semantic retrieval pipeline consisting of:

- Python 3.11;
- recursive loading of Markdown, text and PDF files;
- word-based chunks of 120 words;
- an overlap of 30 words;
- `all-MiniLM-L6-v2` sentence embeddings;
- normalised embedding vectors;
- NumPy dot-product similarity;
- Top 3 retrieved chunks;
- explicit source, category and chunk identifiers.

I will not introduce a vector database, LangChain or an answer-generating large language model at this stage.

## Context

ProjectOS is intended to support people returning to long-term creative projects. Its core technical requirement is not simply to generate fluent text. It must first recover relevant evidence from distributed project materials, including design decisions, process logs, feedback and current-state documents.

Before developing the interface or generative features, I need to establish whether semantic retrieval is technically feasible on a small creative-project corpus.

A minimal retrieval pipeline makes this behaviour visible and testable. It also allows retrieval failures to be separated from later failures in prompt design or language-model generation.

## Rationale

### Transparent implementation

The current pipeline exposes each main operation:

1. load source documents;
2. divide them into chunks;
3. convert chunks into embeddings;
4. compare a query with those embeddings;
5. rank the results;
6. display the original source evidence.

This makes the prototype easier to inspect, explain and debug than a framework-based implementation with several hidden abstractions.

### Appropriate scale

The current demonstration corpus contains four documents and twelve chunks. At this scale, NumPy similarity search is sufficient. A persistent vector database would introduce additional configuration without currently solving an observed problem.

### Local and lightweight embeddings

`all-MiniLM-L6-v2` was selected because it is a relatively compact sentence-transformer model suitable for semantic similarity. It can run locally after its initial download and does not require project documents to be sent to a commercial language-model API.

This supports rapid prototyping and reduces unnecessary privacy exposure during early development.

### Source-grounded output

Every chunk retains:

- its original file path;
- its document category;
- its unique chunk identifier;
- its position in the original document.

This metadata is important because ProjectOS is intended to produce inspectable and correctable project re-entry support. A user should be able to see where reconstructed information came from.

## Alternatives considered

### Keyword search only

Keyword search would be simple and transparent, but it may fail when a user’s question uses different language from the source document. It was therefore not selected as the only retrieval method.

Keyword search may later be combined with semantic retrieval if the evaluation reveals problems with names, exact values or technical terms.

### FAISS or Chroma

FAISS and Chroma can provide efficient storage and retrieval for larger collections. They were deferred because the current corpus is too small to justify a separate vector-store layer.

They may become appropriate when ProjectOS needs persistent indexing, metadata filtering or substantially larger project archives.

### LangChain

LangChain could simplify integration between document loaders, retrievers and language models. It was deferred because the first prototype needs to expose the retrieval logic clearly.

Introducing it now would make it harder to determine which part of the system caused a retrieval error. It may be reconsidered if later orchestration becomes sufficiently complex.

### Large language model generation

An LLM could transform retrieved chunks into a fluent project summary or re-entry brief. It was deliberately excluded from Iteration 0 because fluent generation could conceal weak retrieval or unsupported claims.

Generation should only be added after the evidence-retrieval baseline has been documented and tested.

## Baseline evaluation

The initial retrieval evaluation used:

- 4 Echo Field source documents;
- 12 overlapping chunks;
- 6 fixed project questions;
- Top 3 retrieval.

The results were:

- Hit@1: 4/6 — 66.67%;
- Hit@3: 6/6 — 100.00%.

The expected source was retrieved within the first three results for every question. However, two expected sources were not ranked first.

These results support the feasibility of semantic retrieval while showing that source ranking still needs investigation.

## Consequences

### Positive consequences

- The pipeline is small enough for me to understand and explain.
- Retrieval behaviour can be evaluated independently.
- Source evidence remains visible.
- The prototype runs locally.
- The baseline can be compared with later iterations.
- The implementation is suitable for demonstrating technical reasoning in my portfolio.

### Negative consequences

- Embeddings are recreated every time the program runs.
- The current approach will not scale efficiently to a very large corpus.
- Word-based chunking does not follow every semantic or document boundary.
- NumPy search does not provide persistent indexing or advanced metadata filtering.
- Semantic similarity alone may rank a related summary above more detailed historical evidence.
- The current system retrieves evidence but does not yet create a Project Re-entry Brief.

## Risks

The main risk is treating semantic similarity as if it were factual confidence. A high similarity score only indicates that a chunk is linguistically related to the query.

Another risk is that several documents may contain valid answers to the same question. Evaluation based on one expected file may therefore classify a relevant result as incorrect.

Future evaluation should consider the relevance of the evidence itself, rather than relying only on exact source matching.

## Conditions for revisiting this decision

I will reconsider the retrieval stack if one or more of the following occurs:

- the corpus grows to hundreds of chunks;
- embedding creation causes noticeable startup delay;
- persistent storage becomes necessary;
- metadata filtering becomes part of the interface;
- exact technical terms or numerical details are repeatedly missed;
- user testing shows that the returned evidence is not sufficiently relevant;
- answer generation requires more complex retrieval orchestration.

## Relationship to the research direction

This decision keeps the technical work aligned with the research aim. ProjectOS is not being developed as a general chatbot. The purpose of retrieval is to help reconstruct the state and history of a long-term creative project.

The current prototype provides the technical foundation for a source-grounded and correctable Project Re-entry Brief. Later iterations can investigate how retrieved evidence should be organised to support reflection, orientation and the user’s next creative action.