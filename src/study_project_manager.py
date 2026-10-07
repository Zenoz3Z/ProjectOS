"""Validate, prepare and locally serve a researcher-assigned project."""

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

from chunking import create_chunks
from document_loader import load_documents
from llm_summarizer import DEFAULT_MODEL
from project_context import (
    CATEGORIES, REPOSITORY_ROOT, ProjectConfigurationError, assigned_context,
    supported_project_files, tutorial_context, validate_participant_code,
)
from study_cache import CacheNotReady, prepare_project, read_prepared_project


def validate_project(context, model: str = DEFAULT_MODEL) -> dict:
    report = {"project_id": context.project_id, "project_role": context.project_role,
              "categories": {name: [] for name in CATEGORIES}, "other_files": [],
              "documents": 0, "chunks": 0, "materials_ready": False,
              "cache_ready": False, "ready": False, "issues": []}
    try:
        files = supported_project_files(context)
        for file in files:
            relative = file.relative_to(context.data_directory)
            category = relative.parts[0] if len(relative.parts) > 1 else "uncategorised"
            report["categories"].get(category, report["other_files"]).append(relative.as_posix())
        if not files:
            report["issues"].append("No supported .md, .txt or .pdf files were found.")
        else:
            documents = load_documents(context.data_directory)
            chunks = create_chunks(documents)
            report.update(documents=len(documents), chunks=len(chunks), materials_ready=bool(chunks))
            if not chunks:
                report["issues"].append("The supported files contain no extractable text/chunks.")
    except (ProjectConfigurationError, OSError, RuntimeError, ValueError):
        report["issues"].append("The project directory/files are missing, unsafe or unreadable.")
    if report["materials_ready"]:
        try:
            read_prepared_project(context, model)
            report["cache_ready"] = True
        except (CacheNotReady, ProjectConfigurationError, OSError):
            report["issues"].append("Six current summaries must be prepared for this project/model/prompt.")
    report["ready"] = report["materials_ready"] and report["cache_ready"]
    return report


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("validate", "prepare", "serve"))
    target = parser.add_mutually_exclusive_group(required=True)
    target.add_argument("--participant")
    target.add_argument("--tutorial", action="store_true")
    parser.add_argument("--root", type=Path, default=REPOSITORY_ROOT,
                        help="Local project workspace root; mainly useful for isolated QA.")
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--port", type=int, default=8501)
    args = parser.parse_args(argv)
    try:
        context = tutorial_context(args.root) if args.tutorial else assigned_context(args.participant, args.root)
        if args.command == "validate":
            report = validate_project(context, args.model)
            print(json.dumps(report, indent=2, ensure_ascii=False))
            return 0 if report["ready"] else 1
        if args.command == "prepare":
            if not os.getenv("OPENAI_API_KEY"):
                print("Preparation requires OPENAI_API_KEY in the launching environment.")
                return 1
            report = validate_project(context, args.model)
            if not report["materials_ready"]:
                print(json.dumps(report, indent=2, ensure_ascii=False))
                return 1
            stats = prepare_project(context, args.model, progress=lambda section, state: print(f"{section}: {state}", flush=True))
            print(json.dumps(stats, indent=2))
            return 0 if stats["ready"] else 1
        if args.tutorial:
            parser.error("serve requires --participant.")
        if not 1024 <= args.port <= 65535:
            parser.error("Choose a port between 1024 and 65535.")
        for project in (tutorial_context(args.root), context):
            if not validate_project(project, args.model)["ready"]:
                print(f"{project.project_id}: not ready. Validate and prepare it before serving.")
                return 1
        env = os.environ.copy()
        env.update(PROJECTOS_STUDY_ROOT=str(args.root.resolve()),
                   PROJECTOS_STUDY_PARTICIPANT=validate_participant_code(args.participant),
                   PROJECTOS_STUDY_ONLY="1", PROJECTOS_SUMMARY_MODEL=args.model)
        env.pop("OPENAI_API_KEY", None)
        print(f"Starting a local study session assigned to {args.participant}. No API key is passed to this server.", flush=True)
        return subprocess.call([
            sys.executable, "-m", "streamlit", "run", str(REPOSITORY_ROOT / "src/streamlit_app.py"),
            "--server.address", "127.0.0.1", "--server.port", str(args.port),
            "--server.headless", "true", "--server.fileWatcherType", "none",
            "--client.showErrorDetails", "none", "--browser.gatherUsageStats", "false",
        ], env=env, cwd=REPOSITORY_ROOT)
    except (ProjectConfigurationError, CacheNotReady) as error:
        print(str(error))
        return 1
    except Exception as error:
        print(f"Project preparation could not complete ({type(error).__name__}). Check local files and configuration.")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
