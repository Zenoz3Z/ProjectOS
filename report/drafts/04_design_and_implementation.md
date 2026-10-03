# 4. Design and Implementation

## 4.1 Iteration 0: Retrieval Feasibility Prototype

Before developing the complete ProjectOS interface, I created a small technical prototype to test whether project documents could be retrieved according to a user’s re-entry question. The purpose of this iteration was to isolate the retrieval process from language-model generation and interface design. This allowed me to determine whether the underlying evidence could be found before attempting to generate a fluent Project Re-entry Brief.

### 4.1.1 Demonstration corpus

I constructed a controlled demonstration corpus from my previous creative computing project, Echo Field. The corpus contained four Markdown documents representing different roles within a long-term creative project: current state, design decisions, tutor feedback and process documentation. This structure reflected the types of information that may become distributed or difficult to recall over the duration of a project.

The corpus was created specifically for initial technical testing and cannot be considered representative of all creative projects. However, using a project that I already understood allowed me to judge whether the retrieved evidence was relevant.

### 4.1.2 Document loading and chunking

I implemented a Python document loader supporting Markdown, plain-text and PDF files. Each loaded document retained its source path, file type and project category. Maintaining this metadata was necessary because ProjectOS is intended to present inspectable evidence rather than unsupported summaries.

The four demonstration documents were divided into 12 chunks. Each chunk contained a maximum of 120 words, with a 30-word overlap between neighbouring chunks. The overlap was introduced to reduce the risk of separating a design decision from its surrounding explanation. This was used as an initial, interpretable configuration rather than an optimised value.

### 4.1.3 Semantic retrieval

Each chunk was converted into a vector using the `all-MiniLM-L6-v2` sentence-transformer model. The embeddings were normalised, and similarity was calculated using a NumPy dot product, which is equivalent to cosine similarity for normalised vectors. For each question, the system returned the three most similar chunks together with their similarity scores, source paths, categories and chunk identifiers.

I did not introduce LangChain, a vector database or a generative language model during this iteration. At the current scale, direct NumPy comparison was sufficient, and the smaller implementation made the retrieval process easier to inspect. Separating retrieval from generation also reduced the risk that fluent output would conceal irrelevant or unsupported evidence.

### 4.1.4 Baseline evaluation

I evaluated the prototype using six fixed questions covering design decisions, current interaction state, tutor feedback, movement values and user-testing problems. The expected document appeared within the first three results for all six questions, producing a Hit@3 score of 100%. Four of the six expected documents appeared as the first result, producing a Hit@1 score of 66.67%.

The two lower-ranked cases revealed an important limitation. Information about the same project issue could appear in more than one valid document. For example, the current interaction method was described in both the design decision record and the current-state document. Therefore, exact source matching alone may classify useful evidence as incorrect. Later evaluations should judge the relevance and usefulness of the evidence, rather than relying only on one predefined file path.

These results demonstrate the technical feasibility of retrieving source-grounded evidence from a small creative-project archive. They do not yet demonstrate that ProjectOS improves reflection, project understanding or creative decision-making. Those questions require the later interface prototype and user evaluation.
