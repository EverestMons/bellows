"""Tests for _repo_sync — real temp git repos, no mocks."""
import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

HOOKS_DIR = Path(__file__).resolve().parent.parent / "hooks" / "eluvian"
sys.path.insert(0, str(HOOKS_DIR))

from eluvian_align_hook import _repo_sync  # noqa: E402

HOOK_FILE = HOOKS_DIR / "eluvian_align_hook.py"

_SYNTHETIC_CONTENT = (
    "# Standing constraints — synthetic test fixture\n"
    "**Version:** 1.0 (synthetic)\n"
    "\n"
    "## Standing constraints\n"
    "\n"
    "1. One commit per lens, the subject naming the lens\n"
    "2. cd first for every repo command\n"
    "3. Deposit order: receipt BEFORE ready-\n"
    "4. Verdicts only through tools/issue_verdict.py\n"
    "5. Never run the daemon from a session\n"
    "6. Write a record AFTER the act\n"
    "7. A lint WARN is read, not counted\n"
    "8. Every deposit is written in THIS worktree\n"
    "9. The wrap is /wrap, never memory\n"
)


def _fresh_hook():
    """Load eluvian_align_hook by file path with hooks/eluvian on sys.path."""
    spec = importlib.util.spec_from_file_location("_h_fresh", HOOK_FILE)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _iso_env(tmp_path, include_constraints=True):
    """Build a fully-isolated env dict for subprocess hook tests."""
    root = tmp_path / "root"
    root.mkdir(parents=True)
    if include_constraints:
        (root / "STANDING_CONSTRAINTS.md").write_text(_SYNTHETIC_CONTENT)
    bellows = root / "bellows"
    bellows.mkdir()
    (bellows / "status.py").write_text('print("● stub")\n')
    lf = tmp_path / "lf"
    lf.mkdir()
    subprocess.run(["git", "init", "-q", str(lf)], check=True)
    tuyere = tmp_path / "tuyere"
    tuyere.mkdir()
    subprocess.run(["git", "init", "-q", str(tuyere)], check=True)
    mem = tmp_path / "mem"
    mem.mkdir()
    return {
        "ELUVIAN_WRAP_ROOT": str(root),
        "ELUVIAN_WRAP_LESSONS_FORGE": str(lf),
        "ELUVIAN_WRAP_TUYERE": str(tuyere),
        "ELUVIAN_WRAP_MEMORY": str(mem),
        "ELUVIAN_HOOKS_LOG": str(tmp_path / "hooks.log"),
    }


def _git(cwd, *args):
    subprocess.run(
        ["git", "-C", str(cwd)] + list(args),
        capture_output=True, text=True, check=True,
    )


def _commit(cwd, msg="c"):
    (cwd / "f.txt").write_text(msg)
    _git(cwd, "add", "f.txt")
    _git(cwd, "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-m", msg)


@pytest.fixture()
def repo_pair(tmp_path):
    """Bare origin + working clone, one initial commit."""
    origin = tmp_path / "origin.git"
    clone = tmp_path / "clone"
    subprocess.run(["git", "init", "--bare", str(origin)],
                    capture_output=True, check=True)
    subprocess.run(["git", "clone", str(origin), str(clone)],
                    capture_output=True, check=True)
    _commit(clone, "init")
    _git(clone, "push")
    return origin, clone


def test_current(repo_pair):
    _, clone = repo_pair
    label, state = _repo_sync("test", clone)
    assert label == "test"
    assert state == "current"


def test_behind(repo_pair, tmp_path):
    origin, clone = repo_pair
    pusher = tmp_path / "pusher"
    subprocess.run(["git", "clone", str(origin), str(pusher)],
                    capture_output=True, check=True)
    _commit(pusher, "remote-only")
    _git(pusher, "push")
    _, state = _repo_sync("x", clone)
    assert state == "BEHIND 1"


def test_ahead(repo_pair):
    _, clone = repo_pair
    _commit(clone, "local-only")
    _, state = _repo_sync("x", clone)
    assert state == "ahead 1 (unpushed)"


def test_diverged(repo_pair, tmp_path):
    origin, clone = repo_pair
    pusher = tmp_path / "pusher"
    subprocess.run(["git", "clone", str(origin), str(pusher)],
                    capture_output=True, check=True)
    _commit(pusher, "remote-side")
    _git(pusher, "push")
    _commit(clone, "local-side")
    _, state = _repo_sync("x", clone)
    assert state == "DIVERGED (ahead 1, behind 1)"


def test_no_upstream(repo_pair):
    _, clone = repo_pair
    _git(clone, "branch", "--unset-upstream")
    _, state = _repo_sync("x", clone)
    assert state == "no upstream"


def test_fetch_failed(repo_pair):
    _, clone = repo_pair
    _git(clone, "remote", "set-url", "origin", "/nonexistent/path")
    _, state = _repo_sync("x", clone)
    assert state.startswith("fetch FAILED")


# ---- a1: synthetic file -------------------------------------------------------

def test_a1_standing_constraints_synthetic(tmp_path):
    (tmp_path / "STANDING_CONSTRAINTS.md").write_text(_SYNTHETIC_CONTENT)
    mod = _fresh_hook()
    result = mod._standing_constraints(tmp_path)
    assert result is not None
    assert result.startswith("## Standing constraints\n")
    assert "1. One commit per lens" in result
    assert "… (" not in result


# ---- a1b: real file (skipped when governance root has no constraints file) ---

def test_a1b_standing_constraints_real():
    raw = os.environ.get("ELUVIAN_WRAP_ROOT")
    if raw:
        real_path = Path(raw)
    else:
        from _common import _default_root  # noqa: PLC0415
        real_path = _default_root()
    sc = real_path / "STANDING_CONSTRAINTS.md"
    if not sc.exists():
        pytest.skip("STANDING_CONSTRAINTS.md not found under governance root")
    mod = _fresh_hook()
    result = mod._standing_constraints(real_path)
    assert result is not None
    assert result.startswith("## Standing constraints\n")
    assert "1. One commit per lens" in result
    assert "… (" not in result


# ---- a2: fail-open (empty root; file is a directory) ------------------------

def test_a2_fail_open(tmp_path):
    mod = _fresh_hook()
    assert mod._standing_constraints(tmp_path) is None
    d = tmp_path / "STANDING_CONSTRAINTS.md"
    d.mkdir()
    assert mod._standing_constraints(tmp_path) is None


# ---- a3: truncation ----------------------------------------------------------

def test_a3_truncation(tmp_path):
    lines = ["# title", "**Version:** 1.0", "", "## Standing constraints", ""]
    for i in range(1, 61):
        lines.append(f"{i}. item {i}")
    (tmp_path / "STANDING_CONSTRAINTS.md").write_text("\n".join(lines))
    mod = _fresh_hook()
    result = mod._standing_constraints(tmp_path)
    assert result is not None
    numbered = [ln for ln in result.splitlines() if ln and ln[0].isdigit()]
    assert len(numbered) == 40
    assert "… (20 more lines not shown)" in result


# ---- a4: _compose_context with constraints -----------------------------------

def test_a4_compose_with_constraints():
    mod = _fresh_hook()
    result = mod._compose_context(
        "D", "S", 0, "Sync: core repos current.", "## Standing constraints\n1. x"
    )
    assert result.splitlines()[0].startswith("Eluvian doctrine:")
    assert "## Standing constraints" in result
    assert "1. x" in result
    assert result.endswith("Type /eluvian for the full alignment pass.")
    assert "Parked" not in result


# ---- a5: _compose_context without constraints --------------------------------

def test_a5_compose_without_constraints():
    mod = _fresh_hook()
    result = mod._compose_context("D", "S", 0, "Sync: core repos current.", None)
    assert "not found under the governance root" in result
    assert "## Standing constraints" not in result


# ---- a6: harness interpreter canary ------------------------------------------

def test_a6_harness_canary(tmp_path):
    if not Path("/usr/bin/python3").exists():
        pytest.skip("/usr/bin/python3 not present")
    (tmp_path / "STANDING_CONSTRAINTS.md").write_text(_SYNTHETIC_CONTENT)
    hooks_dir = str(HOOK_FILE.parent)
    hook_path = str(HOOK_FILE)
    root_str = str(tmp_path)
    code = (
        f"import importlib.util, sys, pathlib; "
        f"sys.path.insert(0, {hooks_dir!r}); "
        f"s = importlib.util.spec_from_file_location('h', {hook_path!r}); "
        f"m = importlib.util.module_from_spec(s); s.loader.exec_module(m); "
        f"print(m._standing_constraints(pathlib.Path({root_str!r})) is not None)"
    )
    r = subprocess.run(["/usr/bin/python3", "-c", code], capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    assert r.stdout.strip() == "True"


# ---- a7: injected context with constraints present ---------------------------

def test_a7_injected_present(tmp_path):
    env = _iso_env(tmp_path)
    r = subprocess.run(
        [sys.executable, str(HOOK_FILE)],
        input="{}", capture_output=True, text=True,
        env={**os.environ, **env},
    )
    assert r.returncode == 0
    ctx = json.loads(r.stdout)["hookSpecificOutput"]["additionalContext"]
    assert "## Standing constraints" in ctx
    assert "1. One commit per lens" in ctx
    assert Path(env["ELUVIAN_HOOKS_LOG"]).exists()


# ---- a8: injected context with constraints absent (fail-open) ----------------
# GREEN before the edit: today's hook already lacks the heading — this test
# pins that fail-open shape.

def test_a8_injected_absent(tmp_path):
    env = _iso_env(tmp_path, include_constraints=False)
    r = subprocess.run(
        [sys.executable, str(HOOK_FILE)],
        input="{}", capture_output=True, text=True,
        env={**os.environ, **env},
    )
    assert r.returncode == 0
    ctx = json.loads(r.stdout)["hookSpecificOutput"]["additionalContext"]
    assert "## Standing constraints" not in ctx
