"""Tests for hooks/eluvian/_common.py (plan hooks-shared-common, 2026-09-10)."""
from __future__ import annotations

import importlib
import json
import os
import re
import subprocess
import sys
import uuid
from pathlib import Path

import pytest

HOOKS_DIR = Path(__file__).resolve().parent.parent / "hooks" / "eluvian"
HARNESS_PY = "/usr/bin/python3"
_SHARED_NAMES = (
    "_default_root", "_log_path", "hooklog", "emit",
    "_validate_session_id", "_DEFAULT_LOG", "_VALID_SESSION_ID",
)
_HOOK_FILES = [
    "wrap_arm_hook", "wrap_stop_hook", "wrap_check",
    "eluvian_align_hook", "wrap_debt_hook",
]


def test_s1_shared_names_in_common_not_in_hooks():
    """(s1) Every shared name exists in _common; no hook defines any of them locally."""
    common_path = HOOKS_DIR / "_common.py"
    assert common_path.exists(), "_common.py not found"
    common_src = common_path.read_text()
    for name in _SHARED_NAMES:
        assert re.search(
            rf"^(def {re.escape(name)}\b|{re.escape(name)}\s*=)",
            common_src, re.MULTILINE,
        ), f"{name} not defined in _common.py"
    local_pat = re.compile(
        r"^def (_default_root|_log_path|hooklog|emit|_validate_session_id)\(|"
        r"^_DEFAULT_LOG\s*=|^_VALID_SESSION_ID\s*=",
        re.MULTILINE,
    )
    for hook in _HOOK_FILES:
        hook_src = (HOOKS_DIR / f"{hook}.py").read_text()
        found = local_pat.findall(hook_src)
        assert not found, f"{hook}.py defines shared names locally: {found}"


def test_s2_common_imports_under_harness_python():
    """(s2) _common.py imports cleanly under /usr/bin/python3."""
    if not Path(HARNESS_PY).exists():
        pytest.skip(f"{HARNESS_PY} absent on this machine")
    result = subprocess.run(
        [
            HARNESS_PY, "-c",
            f"import sys; sys.path.insert(0, {str(HOOKS_DIR)!r}); import _common; print('ok')",
        ],
        capture_output=True, text=True, timeout=10,
    )
    assert result.returncode == 0, f"_common.py failed to import under {HARNESS_PY}: {result.stderr}"
    assert "ok" in result.stdout


def test_s3_hooklog_writes_and_swallows(monkeypatch, tmp_path):
    """(s3) hooklog writes ts\\tevent\\tdetail to ELUVIAN_HOOKS_LOG; swallows unwritable paths."""
    sys.path.insert(0, str(HOOKS_DIR))
    common = importlib.import_module("_common")
    log_file = tmp_path / "hooks.log"
    monkeypatch.setenv("ELUVIAN_HOOKS_LOG", str(log_file))
    common.hooklog("test-event", "test-detail")
    text = log_file.read_text()
    assert "\ttest-event\ttest-detail\n" in text
    monkeypatch.setenv("ELUVIAN_HOOKS_LOG", "/nonexistent/cannot/write.log")
    common.hooklog("noop")  # must not raise


def test_s4_emit_outputs_json_and_exits():
    """(s4) emit(context) prints hookSpecificOutput/SessionStart JSON; emit(None) prints {}; always exits 0."""
    with_ctx = subprocess.run(
        [
            sys.executable, "-c",
            f"import sys; sys.path.insert(0, {str(HOOKS_DIR)!r}); import _common; _common.emit('hello')",
        ],
        capture_output=True, text=True, timeout=10,
    )
    assert with_ctx.returncode == 0
    data = json.loads(with_ctx.stdout.strip())
    assert data["hookSpecificOutput"]["hookEventName"] == "SessionStart"
    assert data["hookSpecificOutput"]["additionalContext"] == "hello"
    no_ctx = subprocess.run(
        [
            sys.executable, "-c",
            f"import sys; sys.path.insert(0, {str(HOOKS_DIR)!r}); import _common; _common.emit(None)",
        ],
        capture_output=True, text=True, timeout=10,
    )
    assert no_ctx.returncode == 0
    assert json.loads(no_ctx.stdout.strip()) == {}


def test_s5_four_harness_hooks_run(monkeypatch, tmp_path):
    """(s5) All four harness hooks exit 0, print one JSON line, write a non-exempt log line."""
    root = tmp_path / "root"
    root.mkdir()
    (root / "COMPANY.md").write_text("marker")
    (root / "bellows").mkdir()
    (root / "bellows" / "status.py").write_text("print('STOPPED')\n")
    lf_dir = tmp_path / "lf"
    lf_dir.mkdir()
    tuyere_dir = tmp_path / "tuyere"
    tuyere_dir.mkdir()
    mem_dir = tmp_path / "mem"
    mem_dir.mkdir()
    log_file = tmp_path / "hooks.log"

    monkeypatch.delenv("BELLOWS_DISPATCH", raising=False)
    monkeypatch.setenv("ELUVIAN_WRAP_ROOT", str(root))
    monkeypatch.setenv("ELUVIAN_HOOKS_LOG", str(log_file))
    monkeypatch.setenv("ELUVIAN_WRAP_LESSONS_FORGE", str(lf_dir))
    monkeypatch.setenv("ELUVIAN_WRAP_TUYERE", str(tuyere_dir))
    monkeypatch.setenv("ELUVIAN_WRAP_MEMORY", str(mem_dir))

    sid = str(uuid.uuid4())
    hooks = [
        ("wrap_arm_hook.py", {"session_id": sid, "hook_event_name": "UserPromptSubmit", "cwd": str(root)}),
        ("wrap_stop_hook.py", {"session_id": sid, "hook_event_name": "Stop", "cwd": str(root)}),
        ("wrap_debt_hook.py", {"session_id": sid, "hook_event_name": "SessionStart", "cwd": str(root)}),
        ("eluvian_align_hook.py", {"session_id": sid, "hook_event_name": "SessionStart", "cwd": str(root)}),
    ]
    env = {**os.environ}
    for script, payload in hooks:
        result = subprocess.run(
            [sys.executable, str(HOOKS_DIR / script)],
            input=json.dumps(payload),
            capture_output=True, text=True, timeout=30,
            env=env,
        )
        assert result.returncode == 0, f"{script} exited non-zero: {result.stderr}"
        non_empty = [ln for ln in result.stdout.strip().splitlines() if ln.strip()]
        assert len(non_empty) == 1, (
            f"{script} printed {len(non_empty)} output lines, expected 1: {result.stdout!r}"
        )
        json.loads(non_empty[0])  # must parse as JSON

    log_text = log_file.read_text() if log_file.exists() else ""
    assert "daemon-exempt" not in log_text, "unexpected daemon-exempt lines in log"
    assert log_text.strip(), "no log lines written by any hook"
