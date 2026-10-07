"""Non-personal study fixtures; no network, identity data or real research records."""

import json
from pathlib import Path

from chunking import create_chunks
from document_loader import load_documents
from llm_summarizer import GroundedSummary, insufficient_result
from project_context import assigned_context, tutorial_context
from reentry_brief import build_reentry_brief
from retrieval import SearchResult
from study_cache import prepare_project


class OfflineRetriever:
    def __init__(self, chunks):
        self.chunks = chunks

    def retrieve(self, query, top_k=3):
        return [SearchResult(i + 1, 1.0 - i / 100, chunk)
                for i, chunk in enumerate(self.chunks[:top_k])]


def build_sections(context):
    chunks = create_chunks(load_documents(context.data_directory))
    return build_reentry_brief(OfflineRetriever(chunks), len(chunks))


def offline_summary(section, model):
    if not section.evidence:
        return insufficient_result("No evidence is available in this test fixture.")
    return GroundedSummary(
        support_status="supported", summary=f"Prepared test summary: {section.title}.",
        state_type="current", source_numbers=[1], note="Offline UI test fixture.",
    )


def create_workspace(root: Path, codes=("P00", "P01", "P02", "P97")):
    config = root / "data/study_config/participant_assignments.json"
    config.parent.mkdir(parents=True)
    assignments = {}
    for code in codes:
        directory = root / "data/study_projects" / code
        (directory / "current_state").mkdir(parents=True)
        (directory / "current_state/goals.md").write_text(
            "The current aim is to explore movement and colour in a creative installation. "
            "The next step is to test slow movement. Lighting remains unresolved.", encoding="utf-8",
        )
        assignments[code] = {"project_id": f"participant_project_{code.lower()}",
                             "display_name": "Assigned test project",
                             "relative_path": f"data/study_projects/{code}"}
    config.write_text(json.dumps(assignments), encoding="utf-8")
    tutorial = root / "data/demo_projects/sample_echo_field/current_state"
    tutorial.mkdir(parents=True)
    (tutorial / "goals.md").write_text("Echo Field explores whole-body movement and visual feedback.", encoding="utf-8")
    return root


def prepare_offline(context):
    return prepare_project(context, generate=offline_summary, build_sections=build_sections)


def prepare_workspace(root):
    prepare_offline(tutorial_context(root))
    for code in ("P00", "P01", "P02", "P97"):
        prepare_offline(assigned_context(code, root))
