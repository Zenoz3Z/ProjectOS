"""Public tutorial only: strict cached startup, isolated writes and real UI reuse."""

import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

import pytest
from streamlit.testing.v1 import AppTest

from demo.runtime import (
    CACHE_ASSET, SESSION_CACHE, SOURCE_FILES, DemoError, create_session,
    load_prepared, sha256, verify_assets, verify_session,
)

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def package(tmp_path):
    root = tmp_path / "public_package"
    files = list(SOURCE_FILES) + [CACHE_ASSET, "demo/assets/manifest.json"]
    files += [str(p.relative_to(ROOT)) for p in (ROOT / "demo").glob("*.py")]
    files += [str(p.relative_to(ROOT)) for p in (ROOT / "src").glob("*.py")]
    for relative in files:
        dest = root / relative
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / relative, dest)
    return root


def test_new_sessions_preserve_cache_and_never_share_responses(package):
    first, root1 = create_session(package)
    second, root2 = create_session(package)
    assert first != second and root1 != root2
    context, sections, results, _ = load_prepared(package, first)
    assert len(sections) == len(results) == 6
    assert context.review_file.is_relative_to(root1)
    assert not context.review_file.exists()
    assert sha256(root1 / SESSION_CACHE) == sha256(package / CACHE_ASSET)
    assert sha256(root2 / SESSION_CACHE) == sha256(package / CACHE_ASSET)
    assert verify_session(package, first)[0] == root1


@pytest.mark.parametrize("change", ["missing", "tampered"])
def test_missing_or_changed_cache_never_generates(package, change):
    cache = package / CACHE_ASSET
    if change == "missing":
        cache.unlink()
    else:
        cache.write_text("{}", encoding="utf-8")
    with pytest.raises(DemoError):
        create_session(package)
    assert not (package / ".projectos_demo").exists()


def test_session_cache_cannot_be_replaced_or_silently_reprepared(package):
    session, workspace = create_session(package)
    cache = workspace / SESSION_CACHE
    cache.write_text("{}", encoding="utf-8")
    with pytest.raises(DemoError):
        load_prepared(package, session)
    assert cache.read_text(encoding="utf-8") == "{}"


@pytest.mark.parametrize("session", ["../outside", "P01", "demo_not_a_uuid"])
def test_resume_rejects_non_demo_paths(package, session):
    with pytest.raises(DemoError):
        verify_session(package, session)


def test_strict_production_cache_identity_still_applies(package, monkeypatch):
    import study_cache
    session, _ = create_session(package)
    monkeypatch.setattr(study_cache, "pipeline_signature", lambda: "changed")
    with pytest.raises(study_cache.CacheNotReady):
        load_prepared(package, session)


def test_keyless_subprocess_is_detached_and_makes_no_generation_calls(package):
    env = os.environ.copy()
    for key in list(env):
        if key.startswith(("OPENAI_", "PROJECTOS_")) or key == "PYTHONPATH":
            env.pop(key)
    result = subprocess.run(
        [sys.executable, "-B", "demo/launch.py", "--check"], cwd=package,
        env=env, capture_output=True, text=True, timeout=60,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    info = json.loads(result.stdout.splitlines()[0])
    assert info["sections"] == 6 and info["cache_valid"]
    assert info["guards"] == {"blocked_external_network": 0, "blocked_inference": 0,
                              "blocked_private_or_write_access": 0}


def test_guard_refuses_model_loading_network_and_research_reads(package):
    script = '''
import json, socket
from pathlib import Path
from demo.runtime import create_session, install_guards
root = Path.cwd()
_, workspace = create_session(root)
counts = install_guards(root, workspace)
for action in (
    lambda: socket.getaddrinfo("example.invalid", 443),
    lambda: (root / "data/study_config/participant_assignments.json").read_bytes(),
    lambda: exec(compile("def retrieve(): pass\\nretrieve()", str(root / "src/retrieval.py"), "exec")),
):
    try:
        action()
    except (PermissionError, RuntimeError):
        pass
    else:
        raise AssertionError("Guard did not reject operation")
print(json.dumps(counts))
'''
    result = subprocess.run([sys.executable, "-B", "-c", script], cwd=package,
                            capture_output=True, text=True, timeout=30)
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout) == {"blocked_external_network": 1, "blocked_inference": 1,
                                        "blocked_private_or_write_access": 1}


def test_existing_ui_save_refresh_revisit_and_draft_protection(package, monkeypatch):
    import streamlit_app as ui
    import llm_summarizer
    import study_cache
    import httpx

    def forbidden(*args, **kwargs):
        raise AssertionError("The public tutorial must only read prepared summaries")

    for target, name in [(ui, "generate_cached_summary"), (ui, "generate_all_summaries"),
                         (ui.SemanticRetriever, "__init__"), (llm_summarizer, "OpenAI"),
                         (study_cache, "prepare_project"), (httpx.Client, "send")]:
        monkeypatch.setattr(target, name, forbidden)
    session, workspace = create_session(package)
    _, untouched = create_session(package)
    monkeypatch.setenv("PROJECTOS_DEMO_PACKAGE", str(package))
    monkeypatch.setenv("PROJECTOS_DEMO_SESSION", session)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    cache_before = sha256(workspace / SESSION_CACHE)

    def open_app():
        app = AppTest.from_file(str(ROOT / "demo/app.py"), default_timeout=30).run()
        assert not app.exception
        return app

    def click(app, label):
        next(b for b in app.button if b.label == label).click().run()
        assert not app.exception

    app = open_app()
    assert "Current aim" in [x.value for x in app.title]
    assert any(e.label == "Why did ProjectOS produce this summary?" for e in app.expander)
    response = next(r for r in app.radio if r.label == "Choose your response")
    assert response.options == ["Confirm", "Update", "Reject", "Not applicable"]
    assert response.value is None
    response.set_value("Update").run()
    update = "Fictional demo update: test whether visitors understand movement feedback."
    next(t for t in app.text_area if t.label == "Your updated version").set_value(update).run()
    assert any("unsaved response" in w.value for w in app.warning)
    assert next(b for b in app.button if b.label == "Next").disabled
    click(app, "Save and continue")
    assert "What changed and why" in [t.value for t in app.title]
    context, _, _, _ = load_prepared(package, session)
    events = json.loads(context.review_file.read_text(encoding="utf-8"))["review_events"]
    assert len(events) == 1 and events[0]["action"] == "correct"
    assert events[0]["user_correction"] == update
    refreshed = open_app()
    assert "What changed and why" in [t.value for t in refreshed.title]
    click(refreshed, "Previous")
    assert "Current aim" in [t.value for t in refreshed.title]
    assert next(t for t in refreshed.text_area if t.label == "Your updated version").value == update
    assert sha256(workspace / SESSION_CACHE) == cache_before
    assert not (untouched / "data/reviews/sample_echo_field_reviews.json").exists()
    assert len(json.loads(context.review_file.read_text(encoding="utf-8"))["review_events"]) == 1
