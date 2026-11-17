# Public Echo Field tutorial

This is a cache-only submission demonstration of the existing ProjectOS review UI. It uses four public Echo Field records and their unchanged, pre-generated six-section cache. It does not use participant assignments, participant caches, the experimental selector, retrieval or summary generation.

## Start and revisit

Install the repository's [pinned dependencies](../requirements.txt) in Python 3.11, then run from the repository or extracted candidate root:

```bat
python -B demo/launch.py --port 8501
```

Open the printed local URL. Use another port if needed. The launcher creates a fresh session every time, without overwriting prior sessions. Stop the server with Ctrl+C in its own terminal. To resume, use the identifier printed at startup:

```bat
python -B demo/launch.py --session demo_<identifier> --port 8501
```

Replace `demo_<identifier>` with the complete existing identifier. `python -B demo/launch.py --check` validates a new isolated session without starting a server. It still performs the original strict cache checks.

On Windows with Miniconda installed under the current profile, activate in Command Prompt first:

```bat
call "%USERPROFILE%\miniconda3\Scripts\activate.bat" projectos
```

Dependency installation may require internet access. Review itself requires no API key or model weights. The launcher removes OpenAI credentials from its own process, disables model-download/telemetry settings, and rejects external connections and inference calls before they execute. These are demonstration guards, not an operating-system security boundary or a public multi-user deployment.

## What to try

Start at 0/6. Expand the evidence and source details, choose Update, and enter an explicitly fictional correction in **Your updated version**. Save and continue; the display should show 1/6. Refresh, then use Previous to revisit the first section and its saved update. Unsaved edits block navigation until saved or explicitly discarded. After all six responses, direct section revisiting is available through the existing completion page.

Responses use the unchanged append-only review functions and remain separate from source evidence and prepared summaries. They are demonstration events, not study data. Saving neither rewrites the original records nor updates the cached reconstruction. Refresh restores saved responses; it cannot recover an unsaved draft.

## Files and compatibility

- [Asset manifest](assets/manifest.json) records the exact public source/cache hashes and the baseline commit. [Prepared cache](assets/tutorial_summaries.json) contains only Echo Field tutorial material.
- Session copies and responses are under `.projectos_demo/sessions/`, excluded by the repository's ignore rules. No real participant directory is read or copied.
- Cache validity still depends on raw source, prompt and pipeline bytes and the original schema. No check has been relaxed. Git newline conversion, editing sources or code, or missing files can make this prepared cache incompatible. The candidate ZIP preserves the tested bytes. Restore the supplied package if validation fails; the launcher will not generate replacement summaries.
- The existing cache records `gpt-6-luna` as its historical model identifier. Demonstration playback does not request that model or imply that it is available to another API account.
- The launcher imports the existing application and its libraries; it does not instantiate an embedding model. No study or technical experiment is started.

See the [current validation record](../submission/validation.md). Earlier research and engineering reports describe their own historical versions.
