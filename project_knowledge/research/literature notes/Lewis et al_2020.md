Reading Notes — Lewis et al. (2020)

Reference

Lewis, P., et al. (2020). Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks. Advances in Neural Information Processing Systems, 33, 9459–9474. https://arxiv.org/abs/2005.11401

Research focus

The paper investigates how generation models can use external knowledge alongside knowledge stored in their parameters. It addresses limitations concerning knowledge updates, access to supporting information, and factual generation.

Method

The proposed architecture combines a DPR retriever, a Wikipedia passage index, and a BART generator. RAG-Sequence marginalizes over retrieved passages at the sequence level, whereas RAG-Token does so for each output token. During fine-tuning, the query encoder and generator are updated while the document encoder and index remain fixed.

Main findings

The models achieved strong results across several knowledge-intensive tasks. Human evaluation of Jeopardy question generation favored RAG over BART for factuality and specificity. An index replacement experiment also demonstrated that answers could be updated without retraining the model. These findings do not imply that retrieval eliminates factual errors.

Relevance to ProjectOS

The paper provides a technical foundation for using project documents as an external knowledge source. ProjectOS could retrieve relevant drafts, feedback, and logs to support project-related responses. Its implementation would need to be distinguished from the original jointly trained architecture.

Critical limitations and evaluation implications

The experiments do not evaluate creative practice, reflection, or long-term project continuity. Generation diversity is also different from human creativity. ProjectOS should therefore evaluate retrieval relevance and source faithfulness separately from creative support. Missing information, outdated records, and conflicting versions are important cases for prototype testing.
