Reading Notes — Gao et al. (2024)

Reference

Gao, Y., et al. (2024). Retrieval-Augmented Generation for Large Language Models: A Survey. arXiv:2312.10997, version 5, 27 March 2024. https://arxiv.org/abs/2312.10997v5

Purpose and contribution

This survey organizes RAG research into Naive, Advanced, and Modular paradigms. It examines retrieval, generation, augmentation processes, and evaluation. It provides a taxonomy of existing approaches rather than a single controlled comparison establishing a universally superior architecture.

Relevant technical concepts

Chunking, metadata, query optimization, hybrid retrieval, and reranking offer potential ways to improve access to relevant evidence. For ProjectOS, preserving document context and recording dates and sources may be especially useful when project materials contain revisions and changing decisions.

Evaluation framework

The survey distinguishes context relevance, answer faithfulness, and answer relevance. It also discusses noise robustness, rejection when evidence is insufficient, information integration, and counterfactual robustness. These distinctions can guide technical testing, while faithfulness to a source must remain separate from whether that source is current or correct.

Application to ProjectOS

An initial prototype could establish a retrieval-and-generation baseline with inspectable sources. Subsequent changes should address observed failures, such as missing relevant feedback or confusing old and current plans. Comparing versions on a shared test set would help explain the effects of these changes.

Critical limitations

The survey reflects the literature available in its March 2024 version. Its architectural categories are not a required development sequence, and its evaluation discussion does not establish benefits for creative practice. Technical reliability and support for project continuity therefore require separate evidence.
