from __future__ import annotations

import json
import subprocess
import sys


def _run_cli(args: list[str], stdin: str | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "regex_explainer", *args],
        input=stdin,
        text=True,
        capture_output=True,
        check=False,
    )


def test_cli_parses_js_literal_flags_into_output():
    proc = _run_cli([r"/[A-Z]+\d{2,4}/im", "--format=json"])
    assert proc.returncode == 0, proc.stderr
    payload = json.loads(proc.stdout)
    assert payload["pattern"] == r"[A-Z]+\d{2,4}"
    assert payload["flags"] == "im"


def test_cli_stdin_pattern():
    proc = _run_cli(["-", "--format=json"], stdin=r"^hello.*world$")
    assert proc.returncode == 0, proc.stderr
    payload = json.loads(proc.stdout)
    assert payload["pattern"] == r"^hello.*world$"


def test_cli_version_flag():
    proc = _run_cli(["--version"])
    assert proc.returncode == 0, proc.stderr
    assert proc.stdout.strip().startswith("regex-explainer ")
