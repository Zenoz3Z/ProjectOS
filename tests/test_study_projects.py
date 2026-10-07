import json
import os
import subprocess
from dataclasses import replace
from pathlib import Path

import pytest

import llm_summarizer
import study_project_manager as manager
from project_context import (
    ProjectConfigurationError, assigned_context, load_assignments,
    supported_project_files, tutorial_context, validate_participant_code,
)
from review_store import create_review_event, load_review_store, save_review_event
from study_cache import CacheNotReady, prepare_project, read_prepared_project
from study_fixtures import build_sections, create_workspace, offline_summary, prepare_offline


@pytest.fixture
def workspace(tmp_path):
    return create_workspace(tmp_path)


@pytest.mark.parametrize("code", ["P01", "P02", "P03", "P97", "P100"])
def test_valid_participant_codes(code):
    assert validate_participant_code(code) == code


@pytest.mark.parametrize("code", ["../", "P01/../P02", "P01\\P02", "C:\\P01", "/P01", " P01", "P01 ", "P 01", "p01", "P1", "P0001", "P０１", "P01\n", "", None])
def test_invalid_participant_codes(code):
    with pytest.raises(ProjectConfigurationError):
        validate_participant_code(code)


def edit_assignment(root, value):
    file = root / "data/study_config/participant_assignments.json"
    assignments = json.loads(file.read_text())
    assignments["P01"].update(value)
    file.write_text(json.dumps(assignments), encoding="utf-8")


@pytest.mark.parametrize("relative", ["../outside", "data/study_projects/../private", "/outside", "C:/outside", "data/study_projects", "data/study_projects/P01/../../P02", "data/study_projects/P01\\..\\P02"])
def test_assignment_rejects_traversal_and_absolute_paths(workspace, relative):
    edit_assignment(workspace, {"relative_path": relative})
    with pytest.raises(ProjectConfigurationError):
        assigned_context("P01", workspace)


def test_assignment_and_review_paths_are_scoped_by_participant_and_project(workspace):
    first = assigned_context("P01", workspace, allowed_participant="P01")
    second = assigned_context("P02", workspace, allowed_participant="P02")
    assert first.project_id == "participant_project_p01"
    assert first.data_directory == workspace / "data/study_projects/P01"
    assert first.review_file == workspace / "data/reviews/participants/P01/participant_project_p01_reviews.json"
    assert first.summary_cache_file != second.summary_cache_file
    with pytest.raises(ProjectConfigurationError, match="not available"):
        assigned_context("P02", workspace, allowed_participant="P01")
    first.review_file.parent.mkdir(parents=True)
    save_review_event(create_review_event(first.project_id, "current_intention", "confirm"), first.review_file)
    assert load_review_store(second.review_file, second.project_id)["review_events"] == []
    with pytest.raises(ValueError, match="belongs to project"):
        load_review_store(first.review_file, second.project_id)


def test_missing_assignment_and_config_are_reported(workspace, tmp_path):
    with pytest.raises(ProjectConfigurationError, match="No project has been assigned"):
        assigned_context("P99", workspace)
    with pytest.raises(ProjectConfigurationError, match="No local participant assignments"):
        load_assignments(tmp_path / "unconfigured")


def test_duplicate_or_overlapping_assignments_are_rejected(workspace):
    edit_assignment(workspace, {"relative_path": "data/study_projects/P02"})
    with pytest.raises(ProjectConfigurationError, match="distinct"):
        load_assignments(workspace)
    edit_assignment(workspace, {"relative_path": "data/study_projects/P02/nested"})
    with pytest.raises(ProjectConfigurationError, match="distinct"):
        load_assignments(workspace)


def test_missing_directory_empty_files_and_partial_categories(workspace):
    edit_assignment(workspace, {"relative_path": "data/study_projects/not_created"})
    context = assigned_context("P01", workspace)
    assert not manager.validate_project(context)["materials_ready"]
    context.data_directory.mkdir()
    (context.data_directory / "ignored.csv").write_text("not a supported document", encoding="utf-8")
    assert not manager.validate_project(context)["materials_ready"]
    (context.data_directory / "empty.txt").write_text("  ", encoding="utf-8")
    assert not manager.validate_project(context)["materials_ready"]
    (context.data_directory / "current_state").mkdir()
    (context.data_directory / "current_state/goals.md").write_text("Current aim: explore colour.", encoding="utf-8")
    report = manager.validate_project(context)
    assert report["materials_ready"] and report["documents"] == 1 and report["chunks"] > 0
    assert report["categories"]["decisions"] == []
    assert report["categories"]["current_state"] == ["current_state/goals.md"]
    assert not report["ready"]  # Cache preparation is a separate requirement.
    prepare_offline(context)
    assert manager.validate_project(context)["ready"]


def test_linked_document_cannot_escape_project_root(workspace, tmp_path):
    outside = tmp_path / "outside.txt"
    outside.write_text("Must not be loaded.", encoding="utf-8")
    context = assigned_context("P01", workspace)
    link = context.data_directory / "escape.txt"
    try:
        link.symlink_to(outside)
    except OSError:
        if os.name != "nt":
            pytest.skip("Symbolic links are unavailable on this host.")
        # Directory junctions do not require Windows symbolic-link privilege.
        outside_directory = tmp_path / "outside_directory"
        outside_directory.mkdir()
        (outside_directory / "private.txt").write_text("Must not be loaded.", encoding="utf-8")
        link = context.data_directory / "escape_directory"
        result = subprocess.run(["cmd", "/c", "mklink", "/J", str(link), str(outside_directory)], capture_output=True)
        if result.returncode:
            pytest.skip("This Windows account cannot create a test junction.")
    with pytest.raises(ProjectConfigurationError):
        supported_project_files(context)


def test_cache_hit_avoids_generation_and_retrieval_without_key(workspace, monkeypatch):
    context = assigned_context("P01", workspace)
    prepare_offline(context)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    def forbidden(*args, **kwargs):
        raise AssertionError("A valid cache must not generate or retrieve.")

    stats = prepare_project(context, generate=forbidden, build_sections=forbidden)
    assert stats == {"cache_hits": 6, "cache_misses": 0, "api_calls": 0, "errors": [], "ready": True}
    sections, results, identity = read_prepared_project(context)
    assert len(sections) == len(results) == 6


def test_cache_isolated_by_project_and_invalidated_by_evidence_model_prompt(workspace, monkeypatch):
    first, second = assigned_context("P01", workspace), assigned_context("P02", workspace)
    prepare_offline(first)
    with pytest.raises(CacheNotReady):
        read_prepared_project(second)
    prepare_offline(second)
    before = second.summary_cache_file.read_bytes()
    (first.data_directory / "current_state/goals.md").write_text("A changed project aim and next action.", encoding="utf-8")
    with pytest.raises(CacheNotReady):
        read_prepared_project(first)
    stats = prepare_offline(first)
    assert stats["cache_misses"] == 6
    assert second.summary_cache_file.read_bytes() == before
    with pytest.raises(CacheNotReady):
        read_prepared_project(first, model="different-test-model")
    monkeypatch.setattr(llm_summarizer, "SYSTEM_INSTRUCTIONS", llm_summarizer.SYSTEM_INSTRUCTIONS + "\nChanged test instruction.")
    with pytest.raises(CacheNotReady):
        read_prepared_project(first)
    assert prepare_offline(first)["cache_misses"] == 6


def test_tutorial_cache_is_shared_but_formal_reviews_and_notes_are_separate(workspace):
    tutorial, formal = tutorial_context(workspace), assigned_context("P01", workspace)
    prepare_offline(tutorial)
    prepare_offline(formal)
    before = formal.summary_cache_file.read_bytes()
    save_review_event(create_review_event(formal.project_id, "current_intention", "correct",
                                         user_correction="A private correction.", reason="A private participant note."), formal.review_file)
    assert formal.summary_cache_file.read_bytes() == before
    assert "private correction" not in before.decode()
    assert "private participant note" not in before.decode()
    assert tutorial.summary_cache_file == tutorial_context(workspace).summary_cache_file
    assert not tutorial.review_file.exists()
    assert tutorial.summary_cache_file != formal.summary_cache_file


def test_prepare_recovers_partial_failure_and_reports_attempts_without_error_text(workspace):
    context = assigned_context("P01", workspace)
    calls = []

    def flaky(section, model):
        calls.append(section.section_id)
        if section.section_id == "current_intention":
            raise RuntimeError("DO_NOT_PRINT_PROVIDER_DETAIL")
        return offline_summary(section, model)

    first = prepare_project(context, generate=flaky, build_sections=build_sections)
    assert not first["ready"] and first["cache_misses"] == 6
    assert "DO_NOT_PRINT_PROVIDER_DETAIL" not in json.dumps(first)
    with pytest.raises(CacheNotReady):
        read_prepared_project(context)
    second = prepare_offline(context)
    assert second["ready"] and second["cache_hits"] == 5 and second["cache_misses"] == 1
    assert second["api_calls"] == 1


def test_validate_cli_does_not_call_api_or_print_private_content(workspace, monkeypatch, capsys):
    marker = "PRIVATE_DOCUMENT_CONTENT_MUST_NOT_PRINT"
    (workspace / "data/study_projects/P01/current_state/goals.md").write_text(marker, encoding="utf-8")
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    assert manager.main(["validate", "--participant", "P01", "--root", str(workspace)]) == 1
    output = capsys.readouterr().out
    assert marker not in output and '"documents": 1' in output
    assert manager.main(["prepare", "--participant", "P01", "--root", str(workspace)]) == 1
    assert "requires OPENAI_API_KEY" in capsys.readouterr().out


def test_invalid_cache_or_project_identity_is_not_reviewable(workspace):
    context = assigned_context("P01", workspace)
    prepare_offline(context)
    cache = json.loads(context.summary_cache_file.read_text())
    cache["identity"]["project_id"] = "participant_project_p02"
    context.summary_cache_file.write_text(json.dumps(cache), encoding="utf-8")
    with pytest.raises(CacheNotReady):
        read_prepared_project(context)


def test_context_rejects_cross_participant_output_paths(workspace):
    first, second = assigned_context("P01", workspace), assigned_context("P02", workspace)
    for changed in (replace(first, review_file=second.review_file),
                    replace(first, summary_cache_file=second.summary_cache_file)):
        with pytest.raises(ProjectConfigurationError):
            changed.validate_paths()


def test_serve_binds_one_code_and_does_not_pass_api_key(workspace, monkeypatch):
    prepare_offline(tutorial_context(workspace))
    prepare_offline(assigned_context("P01", workspace))
    # An inert marker tests environment filtering without a real credential.
    monkeypatch.setenv("OPENAI_API_KEY", "inert-test-marker")
    calls = []

    def launch(command, env, cwd):
        calls.append(command)
        assert env["PROJECTOS_STUDY_PARTICIPANT"] == "P01"
        assert env["PROJECTOS_STUDY_ONLY"] == "1"
        assert env["PROJECTOS_STUDY_ROOT"] == str(workspace.resolve())
        assert "OPENAI_API_KEY" not in env
        assert command[command.index("--server.address") + 1] == "127.0.0.1"
        return 0

    monkeypatch.setattr(manager.subprocess, "call", launch)
    assert manager.main(["serve", "--participant", "P01", "--root", str(workspace)]) == 0
    assert len(calls) == 1
