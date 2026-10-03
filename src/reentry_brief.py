from dataclasses import dataclass
from typing import Literal

from brief_schema import (
    BriefSectionDefinition,
    SECTION_DEFINITIONS,
)
from chunking import create_chunks
from document_loader import DEFAULT_DATA_DIR, load_documents
from retrieval import SemanticRetriever
from review_store import (
    get_latest_section_correction,
    get_latest_section_status,
    get_superseded_chunk_ids,
    load_review_store,
)


EvidenceStatus = Literal[
    "supported",
    "conflicting",
    "insufficient",
]

ReviewStatus = Literal[
    "unreviewed",
    "confirmed",
    "corrected",
    "rejected",
]

PROJECT_ID = DEFAULT_DATA_DIR.name

DEFAULT_REVIEW_FILE = (
    DEFAULT_DATA_DIR.parents[1]
    / "reviews"
    / f"{PROJECT_ID}_reviews.json"
)


SECTION_RETRIEVAL_QUERIES = {
    "current_intention": (
        (
            "What is explicitly described as the current project "
            "aim, current interaction method or present direction?"
        ),
        (
            "What is the project currently trying to achieve, "
            "excluding superseded and future directions?"
        ),
    ),
    "changes_and_reasons": (
        (
            "What project method, interaction or direction was "
            "changed or replaced?"
        ),
        (
            "Why was the project changed, and what practical "
            "problem did the change address?"
        ),
    ),
    "current_vs_superseded": (
        (
            "What project direction or interaction method is "
            "explicitly described as current or still in use?"
        ),
        (
            "What project direction is explicitly described as "
            "superseded, replaced, no longer current or future work?"
        ),
    ),
    "relevant_feedback": (
        (
            "What tutor or user feedback was given about the "
            "project?"
        ),
        (
            "How did the project respond to, implement, resolve "
            "or defer the tutor or user feedback?"
        ),
    ),
    "unresolved_tensions": (
        (
            "Which technical problems, limitations, blockers or "
            "unclear behaviours remain unresolved after testing?"
        ),
        (
            "What current project notes describe work that still "
            "needs attention, correction or validation?"
        ),
    ),
    "possible_next_action": (
        (
            "What actions are explicitly listed under the "
            "project's next steps?"
        ),
        (
            "What current test, comparison or decision should "
            "be completed next?"
        ),
    ),
}


@dataclass(slots=True)
class EvidenceItem:
    rank: int
    source: str
    category: str
    chunk_id: str
    similarity_score: float
    excerpt: str
    is_superseded: bool = False


@dataclass(slots=True)
class BriefSection:
    section_id: str
    title: str
    question: str
    evidence_status: EvidenceStatus
    review_status: ReviewStatus
    evidence: list[EvidenceItem]
    user_correction: str | None = None


def create_excerpt(
    text: str,
    maximum_length: int = 1200,
) -> str:
    """Create a readable, single-line evidence excerpt."""
    cleaned_text = " ".join(text.split())

    if len(cleaned_text) <= maximum_length:
        return cleaned_text

    return cleaned_text[:maximum_length].rstrip() + "..."


def select_evidence(
    results,
    preferred_categories: tuple[str, ...],
    limit: int = 2,
):
    """
    Select the highest-scoring evidence from relevant categories.

    This function remains available for tests and simple
    single-query retrieval.
    """
    eligible_results = [
        result
        for result in results
        if result.chunk.category in preferred_categories
    ]

    return eligible_results[:limit]


def get_section_queries(
    definition: BriefSectionDefinition,
) -> tuple[str, ...]:
    """Return the complementary retrieval queries for a section."""
    configured_queries = SECTION_RETRIEVAL_QUERIES.get(
        definition.section_id
    )

    if configured_queries:
        return configured_queries

    return (definition.question,)


def retrieve_diverse_evidence(
    definition: BriefSectionDefinition,
    retriever: SemanticRetriever,
    total_chunks: int,
    limit: int = 2,
):
    """
    Retrieve complementary evidence for one brief section.

    Each query first contributes its strongest eligible result that
    has not already been selected. Remaining positions are filled
    from the strongest unused candidates across all queries.
    """
    if limit <= 0:
        return []

    queries = get_section_queries(definition)

    selected_results = []
    selected_chunk_ids = set()
    candidate_by_chunk_id = {}

    for query in queries:
        query_results = retriever.retrieve(
            query=query,
            top_k=total_chunks,
        )

        eligible_results = select_evidence(
            results=query_results,
            preferred_categories=(
                definition.preferred_categories
            ),
            limit=total_chunks,
        )

        for result in eligible_results:
            chunk_id = result.chunk.chunk_id
            existing_result = candidate_by_chunk_id.get(
                chunk_id
            )

            if (
                existing_result is None
                or result.score > existing_result.score
            ):
                candidate_by_chunk_id[chunk_id] = result

        best_unused_result = next(
            (
                result
                for result in eligible_results
                if (
                    result.chunk.chunk_id
                    not in selected_chunk_ids
                )
            ),
            None,
        )

        if best_unused_result is not None:
            selected_results.append(best_unused_result)
            selected_chunk_ids.add(
                best_unused_result.chunk.chunk_id
            )

        if len(selected_results) >= limit:
            return selected_results[:limit]

    remaining_candidates = sorted(
        candidate_by_chunk_id.values(),
        key=lambda result: result.score,
        reverse=True,
    )

    for result in remaining_candidates:
        if len(selected_results) >= limit:
            break

        chunk_id = result.chunk.chunk_id

        if chunk_id in selected_chunk_ids:
            continue

        selected_results.append(result)
        selected_chunk_ids.add(chunk_id)

    return selected_results[:limit]


def build_brief_section(
    definition: BriefSectionDefinition,
    retriever: SemanticRetriever,
    total_chunks: int,
) -> BriefSection:
    """Retrieve and organise evidence for one brief section."""
    selected_results = retrieve_diverse_evidence(
        definition=definition,
        retriever=retriever,
        total_chunks=total_chunks,
        limit=2,
    )

    evidence_items = []

    for position, result in enumerate(
        selected_results,
        start=1,
    ):
        chunk = result.chunk

        evidence_items.append(
            EvidenceItem(
                rank=position,
                source=chunk.source,
                category=chunk.category,
                chunk_id=chunk.chunk_id,
                similarity_score=result.score,
                excerpt=create_excerpt(chunk.content),
            )
        )

    evidence_status: EvidenceStatus

    if evidence_items:
        evidence_status = "supported"
    else:
        evidence_status = "insufficient"

    return BriefSection(
        section_id=definition.section_id,
        title=definition.title,
        question=definition.question,
        evidence_status=evidence_status,
        review_status="unreviewed",
        evidence=evidence_items,
    )


def build_reentry_brief(
    retriever: SemanticRetriever,
    total_chunks: int,
) -> list[BriefSection]:
    """Build all six sections in the required order."""
    return [
        build_brief_section(
            definition=definition,
            retriever=retriever,
            total_chunks=total_chunks,
        )
        for definition in SECTION_DEFINITIONS
    ]


def apply_review_history(
    sections: list[BriefSection],
    stored_data: dict,
) -> None:
    """
    Apply saved user review events to the generated brief.

    Retrieved evidence remains unchanged. Review status and user
    correction are displayed as a separate layer.
    """
    superseded_chunk_ids = get_superseded_chunk_ids(
        stored_data
    )

    for section in sections:
        section.review_status = get_latest_section_status(
            stored_data=stored_data,
            section_id=section.section_id,
        )

        section.user_correction = (
            get_latest_section_correction(
                stored_data=stored_data,
                section_id=section.section_id,
            )
        )

        for evidence_item in section.evidence:
            if (
                evidence_item.chunk_id
                in superseded_chunk_ids
            ):
                evidence_item.is_superseded = True


def print_reentry_brief(
    sections: list[BriefSection],
    document_count: int,
    chunk_count: int,
    review_event_count: int,
) -> None:
    """Print the Project Re-entry Brief in the terminal."""
    divider = "=" * 76
    evidence_divider = "-" * 76

    print()
    print(divider)
    print("PROJECTOS - PROJECT RE-ENTRY BRIEF")
    print(divider)
    print(f"Documents loaded: {document_count}")
    print(f"Chunks available: {chunk_count}")
    print(f"Sections created: {len(sections)}")
    print(f"Review events loaded: {review_event_count}")
    print()

    for section_number, section in enumerate(
        sections,
        start=1,
    ):
        print(divider)
        print(
            f"SECTION {section_number}: "
            f"{section.title}"
        )
        print(divider)
        print(f"Section ID: {section.section_id}")
        print(f"Question: {section.question}")
        print(
            f"Evidence status: "
            f"{section.evidence_status}"
        )
        print(
            f"Review status: "
            f"{section.review_status}"
        )

        if section.user_correction:
            print(
                "User correction: "
                f"{section.user_correction}"
            )

        print()

        if not section.evidence:
            print("No relevant evidence was retrieved.")
            print()
            continue

        for item in section.evidence:
            print(f"Evidence {item.rank}")
            print(evidence_divider)
            print(f"Source: {item.source}")
            print(f"Category: {item.category}")
            print(f"Chunk ID: {item.chunk_id}")

            if item.is_superseded:
                print("Evidence state: superseded")

            print(
                "Similarity score: "
                f"{item.similarity_score:.4f}"
            )
            print(f"Excerpt: {item.excerpt}")
            print()

    print(divider)
    print("END OF RE-ENTRY BRIEF")
    print(divider)
    print()
    print(
        "Note: similarity scores represent semantic similarity, "
        "not factual confidence."
    )
    print(
        "Retrieved evidence and user review are displayed as "
        "separate layers."
    )


def main() -> None:
    documents = load_documents(DEFAULT_DATA_DIR)
    chunks = create_chunks(documents)

    if not documents:
        raise ValueError(
            "No supported documents were found in "
            f"{DEFAULT_DATA_DIR}"
        )

    if not chunks:
        raise ValueError(
            "Documents were loaded, but no chunks were created."
        )

    print(f"Loading {len(documents)} document(s)...")
    print(f"Preparing {len(chunks)} chunk(s)...")

    retriever = SemanticRetriever(chunks)

    sections = build_reentry_brief(
        retriever=retriever,
        total_chunks=len(chunks),
    )

    review_event_count = 0

    if DEFAULT_REVIEW_FILE.exists():
        stored_data = load_review_store(
            file_path=DEFAULT_REVIEW_FILE,
            project_id=PROJECT_ID,
        )

        review_event_count = len(
            stored_data["review_events"]
        )

        apply_review_history(
            sections=sections,
            stored_data=stored_data,
        )

    print_reentry_brief(
        sections=sections,
        document_count=len(documents),
        chunk_count=len(chunks),
        review_event_count=review_event_count,
    )


if __name__ == "__main__":
    main()