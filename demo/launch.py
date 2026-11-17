"""Start or resume a local, pre-generated Echo Field tutorial."""

import argparse
import json
import os
from pathlib import Path
import sys

PACKAGE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PACKAGE))
from demo.runtime import DemoError, create_session, install_guards, load_prepared, verify_session


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=8501)
    parser.add_argument("--session", help="Resume an existing demo identifier; omission creates a new session.")
    parser.add_argument("--check", action="store_true", help="Validate cache-only startup without starting a server.")
    args = parser.parse_args()
    if not 1024 <= args.port <= 65535:
        parser.error("Choose a local port between 1024 and 65535.")
    try:
        if args.session:
            workspace, _ = verify_session(PACKAGE, args.session)
            session_id = args.session
        else:
            session_id, workspace = create_session(PACKAGE)
        counts = install_guards(PACKAGE, workspace)
        sys.path.insert(0, str(PACKAGE / "src"))
        os.environ.update(PROJECTOS_DEMO_PACKAGE=str(PACKAGE), PROJECTOS_DEMO_SESSION=session_id)
        context, sections, _, identity = load_prepared(PACKAGE, session_id)
        print(json.dumps({"session": session_id, "sections": len(sections), "cache_valid": True,
                          "pre_generated": True, "guards": counts}), flush=True)
        if args.check:
            return 0
        print(f"Open http://127.0.0.1:{args.port} | Stop with Ctrl+C | Resume using --session {session_id}", flush=True)
        from streamlit.web import cli
        sys.argv = ["streamlit", "run", str(PACKAGE / "demo/app.py"),
                    "--server.address", "127.0.0.1", "--server.port", str(args.port),
                    "--server.headless", "true", "--server.fileWatcherType", "none",
                    "--browser.gatherUsageStats", "false", "--client.showErrorDetails", "none",
                    "--secrets.files", str(workspace / "no_credentials.toml")]
        return cli.main()
    except (DemoError, OSError, ValueError) as error:
        print(f"Tutorial unavailable: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
