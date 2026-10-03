from dataclasses import dataclass

import numpy as np
from sentence_transformers import SentenceTransformer

from chunking import Chunk, create_chunks
from document_loader import (
    DEFAULT_DATA_DIR,
    load_documents,
)


MODEL_NAME = "all-MiniLM-L6-v2"


@dataclass(slots=True)
class SearchResult:
    """One ranked semantic-search result."""

    rank: int
    score: float
    chunk: Chunk


class SemanticRetriever:
    """Retrieve project evidence using semantic similarity."""

    def __init__(
        self,
        chunks: list[Chunk],
        model_name: str = MODEL_NAME,
    ) -> None:
        if not chunks:
            raise ValueError(
                "The retriever requires at least one chunk."
            )

        self.chunks = chunks

        print(f"Loading embedding model: {model_name}")

        self.model = SentenceTransformer(model_name)

        print("Creating chunk embeddings...")

        self.chunk_embeddings = self.model.encode(
            [chunk.content for chunk in chunks],
            convert_to_numpy=True,
            normalize_embeddings=True,
            show_progress_bar=False,
        )

    def retrieve(
        self,
        query: str,
        top_k: int = 3,
    ) -> list[SearchResult]:
        """Return the chunks most similar to the query."""

        query = query.strip()

        if not query:
            raise ValueError("Query cannot be empty.")

        if top_k <= 0:
            raise ValueError(
                "top_k must be greater than zero."
            )

        query_embedding = self.model.encode(
            [query],
            convert_to_numpy=True,
            normalize_embeddings=True,
            show_progress_bar=False,
        )[0]

        similarity_scores = np.dot(
            self.chunk_embeddings,
            query_embedding,
        )

        result_count = min(
            top_k,
            len(self.chunks),
        )

        top_indices = np.argsort(
            similarity_scores
        )[::-1][:result_count]

        results = []

        for rank, chunk_index in enumerate(
            top_indices,
            start=1,
        ):
            results.append(
                SearchResult(
                    rank=rank,
                    score=float(
                        similarity_scores[chunk_index]
                    ),
                    chunk=self.chunks[chunk_index],
                )
            )

        return results


def print_results(
    query: str,
    results: list[SearchResult],
) -> None:
    """Print ranked results with source information."""

    print(f"\nQuery: {query}")
    print(f"Retrieved: {len(results)} result(s)\n")

    for result in results:
        excerpt = result.chunk.content[:500]

        print(f"Rank: {result.rank}")
        print(f"Score: {result.score:.4f}")
        print(f"Source: {result.chunk.source}")
        print(f"Category: {result.chunk.category}")
        print(f"Chunk ID: {result.chunk.chunk_id}")
        print(f"Evidence: {excerpt}")
        print("-" * 70)


def main() -> None:
    documents = load_documents(DEFAULT_DATA_DIR)

    chunks = create_chunks(
        documents=documents,
        max_words=120,
        overlap_words=30,
    )

    retriever = SemanticRetriever(chunks)

    test_query = (
        "Why was hand tracking replaced "
        "with whole-body movement?"
    )

    results = retriever.retrieve(
        query=test_query,
        top_k=3,
    )

    print_results(
        query=test_query,
        results=results,
    )


if __name__ == "__main__":
    main()