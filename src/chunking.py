from dataclasses import dataclass
from pathlib import Path

from document_loader import (
    DEFAULT_DATA_DIR,
    Document,
    load_documents,
)


@dataclass(slots=True)
class Chunk:
    """A searchable section of a source document."""

    content: str
    source: str
    category: str
    chunk_id: str
    start_word: int
    end_word: int


def chunk_document(
    document: Document,
    max_words: int = 120,
    overlap_words: int = 30,
) -> list[Chunk]:
    """
    Split one document into overlapping word-based chunks.

    Overlap preserves context between neighbouring chunks.
    """

    if max_words <= 0:
        raise ValueError("max_words must be greater than zero.")

    if overlap_words < 0 or overlap_words >= max_words:
        raise ValueError(
            "overlap_words must be between 0 and max_words - 1."
        )

    words = document.content.split()

    if not words:
        return []

    chunks = []
    start_word = 0
    chunk_number = 1

    source_key = (
        Path(document.source)
        .with_suffix("")
        .as_posix()
        .replace("/", "__")
    )

    while start_word < len(words):
        end_word = min(
            start_word + max_words,
            len(words),
        )

        chunk_content = " ".join(
            words[start_word:end_word]
        ).strip()

        chunk_id = (
            f"{source_key}_chunk_{chunk_number:03d}"
        )

        chunks.append(
            Chunk(
                content=chunk_content,
                source=document.source,
                category=document.category,
                chunk_id=chunk_id,
                start_word=start_word,
                end_word=end_word,
            )
        )

        if end_word == len(words):
            break

        start_word = end_word - overlap_words
        chunk_number += 1

    return chunks


def create_chunks(
    documents: list[Document],
    max_words: int = 120,
    overlap_words: int = 30,
) -> list[Chunk]:
    """Create chunks for every loaded document."""

    all_chunks = []

    for document in documents:
        document_chunks = chunk_document(
            document=document,
            max_words=max_words,
            overlap_words=overlap_words,
        )

        all_chunks.extend(document_chunks)

    return all_chunks


def main() -> None:
    documents = load_documents(DEFAULT_DATA_DIR)

    chunks = create_chunks(
        documents=documents,
        max_words=120,
        overlap_words=30,
    )

    print(f"\nCreated {len(chunks)} chunk(s)\n")

    for chunk in chunks:
        preview = chunk.content[:100].replace(
            "\n",
            " ",
        )

        print(f"Chunk ID: {chunk.chunk_id}")
        print(f"Source: {chunk.source}")
        print(f"Category: {chunk.category}")
        print(
            f"Word range: "
            f"{chunk.start_word}–{chunk.end_word}"
        )
        print(f"Preview: {preview}...")
        print("-" * 60)


if __name__ == "__main__":
    main()