import json
from pathlib import Path

from chunking import create_chunks
from document_loader import (
    DEFAULT_DATA_DIR,
    load_documents,
)
from retrieval import SemanticRetriever


PROJECT_ROOT = Path(__file__).resolve().parents[1]

EVALUATION_FILE = (
    PROJECT_ROOT
    / "tests"
    / "evaluation_queries.json"
)


def load_evaluation_queries(
    file_path: Path,
) -> list[dict[str, str]]:
    """Load the fixed retrieval evaluation questions."""

    if not file_path.exists():
        raise FileNotFoundError(
            f"Evaluation file not found: {file_path}"
        )

    with file_path.open(
        "r",
        encoding="utf-8",
    ) as file:
        queries = json.load(file)

    if not queries:
        raise ValueError(
            "The evaluation set is empty."
        )

    return queries


def main() -> None:
    documents = load_documents(DEFAULT_DATA_DIR)

    chunks = create_chunks(
        documents=documents,
        max_words=120,
        overlap_words=30,
    )

    retriever = SemanticRetriever(chunks)

    evaluation_queries = load_evaluation_queries(
        EVALUATION_FILE
    )

    top_1_hits = 0
    top_3_hits = 0

    print("\nRunning retrieval evaluation...\n")

    for test_case in evaluation_queries:
        query_id = test_case["id"]
        query = test_case["query"]
        expected_source = test_case["expected_source"]

        results = retriever.retrieve(
            query=query,
            top_k=3,
        )

        retrieved_sources = [
            result.chunk.source
            for result in results
        ]

        hit_at_1 = (
            retrieved_sources[0] == expected_source
        )

        hit_at_3 = (
            expected_source in retrieved_sources
        )

        if hit_at_1:
            top_1_hits += 1

        if hit_at_3:
            top_3_hits += 1

        status = "PASS" if hit_at_3 else "MISS"

        print(f"{query_id}: {status}")
        print(f"Query: {query}")
        print(f"Expected: {expected_source}")

        for result in results:
            print(
                f"  Rank {result.rank}: "
                f"{result.chunk.source} "
                f"(score={result.score:.4f})"
            )

        print("-" * 70)

    total_queries = len(evaluation_queries)

    hit_at_1_score = (
        top_1_hits / total_queries
    )

    hit_at_3_score = (
        top_3_hits / total_queries
    )

    print("\nEvaluation summary")
    print(
        f"Hit@1: {top_1_hits}/{total_queries} "
        f"({hit_at_1_score:.2%})"
    )
    print(
        f"Hit@3: {top_3_hits}/{total_queries} "
        f"({hit_at_3_score:.2%})"
    )


if __name__ == "__main__":
    main()