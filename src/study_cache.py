"""Private, project-scoped prepared briefs. Reading never calls an API."""

import hashlib
import inspect
import json
from dataclasses import asdict
from pathlib import Path

import llm_summarizer as summarizer
from brief_schema import SECTION_DEFINITIONS
from project_context import ProjectContext, ProjectConfigurationError, supported_project_files
from reentry_brief import BriefSection, EvidenceItem


CACHE_SCHEMA_VERSION = 1
PROMPT_SCHEMA_VERSION = "grounded-summary-v1"


class CacheNotReady(ValueError):
    pass


def digest(value) -> str:
    encoded = json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def prompt_signature() -> str:
    return digest({
        "version": PROMPT_SCHEMA_VERSION,
        "instructions": summarizer.SYSTEM_INSTRUCTIONS,
        "guidance": summarizer.SECTION_GUIDANCE,
        "schema": summarizer.GroundedSummary.model_json_schema(),
        "source_file": hashlib.sha256(Path(summarizer.__file__).read_bytes()).hexdigest(),
        "implementation": [inspect.getsource(fn) for fn in (
            summarizer.format_evidence, summarizer.build_user_prompt,
            summarizer.validate_result, summarizer.generate_grounded_summary,
        )],
    })


def pipeline_signature() -> str:
    source = Path(__file__).parent
    return digest({name: hashlib.sha256((source / name).read_bytes()).hexdigest() for name in (
        "document_loader.py", "chunking.py", "retrieval.py", "reentry_brief.py", "brief_schema.py",
    )})


def source_fingerprint(context: ProjectContext) -> str:
    files = supported_project_files(context)
    return digest([
        (path.relative_to(context.data_directory).as_posix(), hashlib.sha256(path.read_bytes()).hexdigest())
        for path in files
    ])


def cache_identity(context: ProjectContext, model: str) -> dict:
    return {
        "cache_schema_version": CACHE_SCHEMA_VERSION,
        "project_id": context.project_id,
        "project_role": context.project_role,
        "model": model,
        "prompt_schema_version": PROMPT_SCHEMA_VERSION,
        "prompt_fingerprint": prompt_signature(),
        "pipeline_fingerprint": pipeline_signature(),
        "source_fingerprint": source_fingerprint(context),
    }


def serialise_section(section) -> dict:
    """Allow-list source evidence; no review state, correction or participant note."""
    return {
        "section_id": section.section_id, "title": section.title,
        "question": section.question, "evidence_status": section.evidence_status,
        "evidence": [{key: value for key, value in asdict(item).items() if key != "is_superseded"}
                     for item in section.evidence],
    }


def evidence_fingerprint(section_data: dict) -> str:
    return digest(section_data)


def entry_key(identity: dict, section_data: dict) -> str:
    return digest({**identity, "section_id": section_data["section_id"],
                   "evidence_fingerprint": evidence_fingerprint(section_data)})


def decode_entry(entry: dict, identity: dict, definition) -> tuple:
    data = entry["section"]
    if (set(data) != {"section_id", "title", "question", "evidence_status", "evidence"}
            or data["section_id"] != definition.section_id
            or data["title"] != definition.title or data["question"] != definition.question
            or entry["key"] != entry_key(identity, data)
            or entry["evidence_fingerprint"] != evidence_fingerprint(data)
            or data["evidence_status"] not in {"supported", "insufficient", "conflicting"}
            or not isinstance(data["evidence"], list) or len(data["evidence"]) > 2):
        raise CacheNotReady("A cached section does not match the prepared evidence.")
    evidence = []
    for item in data["evidence"]:
        if set(item) != {"rank", "source", "category", "chunk_id", "similarity_score", "excerpt"}:
            raise CacheNotReady("Unexpected cached evidence fields.")
        evidence.append(EvidenceItem(**item))
    section = BriefSection(
        data["section_id"], data["title"], data["question"], data["evidence_status"],
        "unreviewed", evidence,
    )
    result = summarizer.GroundedSummary.model_validate(entry["result"])
    if any(n < 1 or n > len(evidence) for n in result.source_numbers):
        raise CacheNotReady("Cached source references are invalid.")
    return section, result


def read_cache(context: ProjectContext, identity: dict) -> dict:
    context.validate_paths()
    try:
        data = json.loads(context.summary_cache_file.read_text(encoding="utf-8"))
        if data.get("identity") != identity or not isinstance(data.get("sections"), dict):
            raise CacheNotReady("Summary cache is stale or belongs to a different project/model/prompt.")
        return data
    except (OSError, ValueError, TypeError, AttributeError) as error:
        raise CacheNotReady("Summary cache is missing, unreadable or stale. Run prepare.") from error


def read_prepared_project(context: ProjectContext, model: str = summarizer.DEFAULT_MODEL) -> tuple:
    """Verify source freshness, then return six fresh objects without inference."""
    identity = cache_identity(context, model)
    cache = read_cache(context, identity)
    sections, results = [], {}
    try:
        for definition in SECTION_DEFINITIONS:
            section, result = decode_entry(cache["sections"][definition.section_id], identity, definition)
            sections.append(section)
            results[definition.section_id] = result
    except (KeyError, TypeError, ValueError) as error:
        raise CacheNotReady("All six valid summaries must be prepared before the study.") from error
    return sections, results, identity


def write_cache(context: ProjectContext, cache: dict) -> None:
    context.validate_paths()
    path = context.summary_cache_file
    path.parent.mkdir(parents=True, exist_ok=True)
    context.validate_paths()
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(cache, ensure_ascii=False, indent=2), encoding="utf-8")
    temporary.replace(path)


def prepare_project(context: ProjectContext, model: str = summarizer.DEFAULT_MODEL,
                    generate=None, build_sections=None, progress=None) -> dict:
    """Researcher-only preparation; dependency injection keeps tests offline."""
    from chunking import create_chunks
    from document_loader import load_documents
    from reentry_brief import build_reentry_brief
    from retrieval import SemanticRetriever

    identity = cache_identity(context, model)
    try:
        old = read_cache(context, identity)
    except CacheNotReady:
        old = {"identity": identity, "sections": {}}
    valid = {}
    for definition in SECTION_DEFINITIONS:
        try:
            decode_entry(old["sections"][definition.section_id], identity, definition)
            valid[definition.section_id] = old["sections"][definition.section_id]
        except (KeyError, TypeError, ValueError):
            pass
    stats = {"cache_hits": len(valid), "cache_misses": len(SECTION_DEFINITIONS) - len(valid),
             "api_calls": 0, "errors": [], "ready": False}
    if len(valid) == len(SECTION_DEFINITIONS):
        for definition in SECTION_DEFINITIONS:
            if progress:
                progress(definition.section_id, "cache hit")
        stats["ready"] = True
        return stats
    if build_sections is None:
        documents = load_documents(context.data_directory)
        chunks = create_chunks(documents)
        if not documents or not chunks:
            raise ProjectConfigurationError("The project needs at least one non-empty supported document.")
        sections = build_reentry_brief(SemanticRetriever(chunks), len(chunks))
    else:
        sections = build_sections(context)
    generate = generate or summarizer.generate_grounded_summary
    cache = {"identity": identity, "sections": dict(valid)}
    for section in sections:
        if section.section_id in valid:
            if progress:
                progress(section.section_id, "cache hit")
            continue
        if progress:
            progress(section.section_id, "preparing")
        try:
            # An empty-evidence fallback returns locally without an API request.
            if section.evidence:
                stats["api_calls"] += 1
            result = generate(section=section, model=model)
            data = serialise_section(section)
            entry = {"key": entry_key(identity, data), "evidence_fingerprint": evidence_fingerprint(data),
                     "section": data, "result": result.model_dump()}
            definition = next(d for d in SECTION_DEFINITIONS if d.section_id == section.section_id)
            decode_entry(entry, identity, definition)
            cache["sections"][section.section_id] = entry
            # Keep successful sections if a later API request fails.
            write_cache(context, cache)
        except Exception as error:
            stats["errors"].append(f"{section.section_id}: preparation failed ({type(error).__name__}).")
    if source_fingerprint(context) != identity["source_fingerprint"]:
        stats["errors"].append("Source files changed during preparation. Run prepare again.")
    stats["ready"] = len(cache["sections"]) == len(SECTION_DEFINITIONS) and not stats["errors"]
    return stats
