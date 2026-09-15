"""Tests for the pre-check pass record and commit binding (bellows #100105, thread 333)."""
import io
import json
import os
import shlex
import stat
import subprocess
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

_BELLOWS_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_BELLOWS_ROOT))
sys.path.insert(0, str(_BELLOWS_ROOT / "tools"))
import check_deposit
import runner
import bellows

TOOL_PATH = _BELLOWS_ROOT / "tools" / "check_deposit.py"
HOOKS_DIR = _BELLOWS_ROOT / "hooks" / "git"


# ─── helpers ────────────────────────────────────────────────────────────────


def _git_init(d: Path) -> None:
    d.mkdir(parents=True, exist_ok=True)
    subprocess.run(["git", "init", "--initial-branch=main", str(d)], check=True, capture_output=True)
    subprocess.run(["git", "-C", str(d), "config", "user.email", "t@t.com"], check=True, capture_output=True)
    subprocess.run(["git", "-C", str(d), "config", "user.name", "T"], check=True, capture_output=True)


def _git_commit_all(d: Path, msg: str = "init") -> None:
    subprocess.run(["git", "-C", str(d), "add", "-A"], check=True, capture_output=True)
    subprocess.run(
        ["git", "-C", str(d), "-c", "user.email=t@t.com", "-c", "user.name=T", "commit", "-m", msg],
        check=True, capture_output=True,
    )


def _make_worktree(repo: Path, wt: Path, branch: str = "wt-1") -> None:
    wt.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        ["git", "-C", str(repo), "worktree", "add", str(wt), "-b", branch, "HEAD"],
        check=True, capture_output=True,
    )


def _git_toplevel(d: Path) -> str:
    return subprocess.check_output(
        ["git", "-C", str(d), "rev-parse", "--show-toplevel"], stderr=subprocess.DEVNULL
    ).decode().strip()


def _git_absolute_gitdir(d: Path) -> str:
    return subprocess.check_output(
        ["git", "-C", str(d), "rev-parse", "--absolute-git-dir"], stderr=subprocess.DEVNULL
    ).decode().strip()


def _record_path(wt: Path) -> Path:
    return Path(_git_absolute_gitdir(wt)) / "bellows-precheck-pass.json"


def _make_plan(deposits, step: int = 1, extra_body: str = "", step2_body: str = ""):
    header = "# bellows — test\n\n**Date:** 2026-09-14 | **Project:** bellows\n\n"
    body = f"## STEP {step} — DEV\n\n> **Deposits:**\n"
    for dep in deposits:
        body += f"> - `{dep}`\n"
    body += extra_body
    if step2_body:
        body += f"\n## STEP 2 — QA\n\n{step2_body}\n"
    return header + body


def _binding_env(wt: Path, plan_path: Path, step: int,
                 base_env: dict = None) -> dict:
    if base_env is None:
        base_env = dict(os.environ)
    toplevel = _git_toplevel(wt)
    count = int(base_env.get("GIT_CONFIG_COUNT", "0"))
    return {
        **base_env,
        "GIT_CONFIG_COUNT": str(count + 1),
        f"GIT_CONFIG_KEY_{count}": "core.hooksPath",
        f"GIT_CONFIG_VALUE_{count}": str(HOOKS_DIR),
        "BELLOWS_PRECHECK_WT": toplevel,
        "BELLOWS_PRECHECK_PLAN": str(plan_path),
        "BELLOWS_PRECHECK_STEP": str(step),
        "BELLOWS_PYTHON": sys.executable,
    }


def _git_commit(d: Path, env: dict, msg: str = "test") -> subprocess.CompletedProcess:
    subprocess.run(["git", "-C", str(d), "add", "-A"],
                   check=True, capture_output=True, env=env)
    return subprocess.run(
        ["git", "-C", str(d), "-c", "user.email=t@t.com", "-c", "user.name=T", "commit", "-m", msg],
        capture_output=True, text=True, env=env,
    )


def _run(plan_path: Path, step: int, wt: Path, capsys, extra: tuple = ()) -> tuple:
    argv = [str(plan_path), str(step), "--wt", str(wt)] + list(extra)
    rc = check_deposit.main(argv)
    return rc, capsys.readouterr().out


def _make_mock_popen(stdout_data="", stderr_data="", returncode=0):
    proc = MagicMock()
    proc.stdout = io.StringIO(stdout_data)
    proc.stderr = io.StringIO(stderr_data)
    proc.returncode = returncode
    proc.poll = MagicMock(side_effect=[None, returncode])
    proc.kill = MagicMock()
    return proc


_RESULT_EVENT = json.dumps({
    "type": "result", "subtype": "success", "is_error": False,
    "result": "done", "stop_reason": "end_turn", "session_id": "s1",
    "total_cost_usd": 0.01, "permission_denials": [],
})
_CLEAN_NDJSON = _RESULT_EVENT + "\n"


# ─── tests ───────────────────────────────────────────────────────────────────


class TestB1RecordOnCleanRun:
    """(b1) clean pre-check records plan, step, blobs; in worktree's git dir; prints pass recorded."""

    def test_b1(self, tmp_path, capsys):
        repo = tmp_path / "r"
        _git_init(repo)
        (repo / "tracked.py").write_text("x = 1\n")
        _git_commit_all(repo)
        wt = tmp_path / "wt"
        _make_worktree(repo, wt)

        (wt / "tracked.py").write_text("x = 2\n")
        (wt / "untracked.txt").write_text("new\n")

        plan_path = tmp_path / "plan.md"
        plan_path.write_text(_make_plan(["tracked.py", "untracked.txt"]))

        rc, out = _run(plan_path, 1, wt, capsys)
        assert rc == 0
        assert "PRECHECK: pass recorded — 2 changed path(s)" in out

        rec = _record_path(wt)
        assert rec.exists(), "record must exist in worktree's own git dir"
        data = json.loads(rec.read_text())
        assert data["plan"] == plan_path.name
        assert data["step"] == 1
        assert "tracked.py" in data["files"]
        assert "untracked.txt" in data["files"]

        common_gitdir = Path(subprocess.check_output(
            ["git", "-C", str(wt), "rev-parse", "--path-format=absolute", "--git-common-dir"],
            stderr=subprocess.DEVNULL,
        ).decode().strip())
        assert not (common_gitdir / "bellows-precheck-pass.json").exists()


class TestB2FailingRunRemovesRecord:
    """(b2) a failing pre-check removes the record."""

    def test_b2(self, tmp_path, capsys):
        repo = tmp_path / "r"
        _git_init(repo)
        (repo / "src.py").write_text("x = 1\n")
        _git_commit_all(repo)
        wt = tmp_path / "wt"
        _make_worktree(repo, wt)
        (wt / "src.py").write_text("x = 2\n")

        plan_path = tmp_path / "plan.md"
        plan_path.write_text(_make_plan(["src.py"]))

        rc1, _out1 = _run(plan_path, 1, wt, capsys)
        assert rc1 == 0
        assert _record_path(wt).exists()

        plan_path.write_text(_make_plan(["src.py", "knowledge/development/dev-log.md"]))
        rc2, _out2 = _run(plan_path, 1, wt, capsys)
        assert rc2 == 1
        assert not _record_path(wt).exists(), "failing run must remove the record"


class TestB3CommitRefusedNoRecord:
    """(b3) commit in bound worktree with no record refused; refusal names rerun command."""

    def test_b3(self, tmp_path):
        repo = tmp_path / "r"
        _git_init(repo)
        (repo / "src.py").write_text("x = 1\n")
        _git_commit_all(repo)
        wt = tmp_path / "wt"
        _make_worktree(repo, wt)
        (wt / "src.py").write_text("x = 2\n")

        plan_path = tmp_path / "in-progress-executable-99901.md"
        plan_path.write_text(_make_plan(["src.py", "knowledge/development/dev-log-test.md"]))

        env = _binding_env(wt, plan_path, 1)
        result = _git_commit(wt, env)

        assert result.returncode != 0
        combined = result.stdout + result.stderr
        assert "REFUSED no passing pre-check is recorded" in combined
        assert "PRECOMMIT: refused" in combined
        assert shlex.quote(sys.executable) in combined
        assert shlex.quote(str(TOOL_PATH)) in combined
        assert "--expect-missing" in combined
        assert "uncommitted" in combined.lower()


class TestB4CommitAfterCleanPrecheck:
    """(b4) after a clean pre-check the commit goes through."""

    def test_b4(self, tmp_path, capsys):
        repo = tmp_path / "r"
        _git_init(repo)
        (repo / "src.py").write_text("x = 1\n")
        _git_commit_all(repo)
        wt = tmp_path / "wt"
        _make_worktree(repo, wt)
        (wt / "src.py").write_text("x = 2\n")

        plan_path = tmp_path / "in-progress-executable-99902.md"
        plan_path.write_text(_make_plan(["src.py"]))

        rc, _out = _run(plan_path, 1, wt, capsys)
        assert rc == 0

        env = _binding_env(wt, plan_path, 1)
        result = _git_commit(wt, env)
        assert result.returncode == 0


class TestB5EditedPathRefused:
    """(b5) a path edited after the pre-check is refused as changed."""

    def test_b5(self, tmp_path, capsys):
        repo = tmp_path / "r"
        _git_init(repo)
        (repo / "src.py").write_text("x = 1\n")
        _git_commit_all(repo)
        wt = tmp_path / "wt"
        _make_worktree(repo, wt)
        (wt / "src.py").write_text("x = 2\n")

        plan_path = tmp_path / "in-progress-executable-99903.md"
        plan_path.write_text(_make_plan(["src.py"]))

        rc, _out = _run(plan_path, 1, wt, capsys)
        assert rc == 0

        (wt / "src.py").write_text("x = 99\n")

        env = _binding_env(wt, plan_path, 1)
        result = _git_commit(wt, env)

        assert result.returncode != 0
        combined = result.stdout + result.stderr
        assert "changed since the recorded pre-check" in combined
        assert "PRECOMMIT: refused" in combined


class TestB6UnreadPathRefused:
    """(b6) a path the pre-check never read is refused."""

    def test_b6(self, tmp_path, capsys):
        repo = tmp_path / "r"
        _git_init(repo)
        (repo / "src.py").write_text("x = 1\n")
        _git_commit_all(repo)
        wt = tmp_path / "wt"
        _make_worktree(repo, wt)
        (wt / "src.py").write_text("x = 2\n")

        plan_path = tmp_path / "in-progress-executable-99904.md"
        plan_path.write_text(_make_plan(["src.py"]))

        rc, _out = _run(plan_path, 1, wt, capsys)
        assert rc == 0

        (wt / "extra.py").write_text("y = 1\n")

        env = _binding_env(wt, plan_path, 1)
        result = _git_commit(wt, env)

        assert result.returncode != 0
        combined = result.stdout + result.stderr
        assert "the recorded pre-check did not read" in combined
        assert "PRECOMMIT: refused" in combined


class TestB7WrongStepRecordRefused:
    """(b7) another step's record is refused."""

    def test_b7(self, tmp_path, capsys):
        repo = tmp_path / "r"
        _git_init(repo)
        (repo / "src.py").write_text("x = 1\n")
        _git_commit_all(repo)
        wt = tmp_path / "wt"
        _make_worktree(repo, wt)
        (wt / "src.py").write_text("x = 2\n")

        plan_path = tmp_path / "in-progress-executable-99905.md"
        plan_path.write_text(_make_plan(["src.py"]))

        rc, _out = _run(plan_path, 1, wt, capsys)
        assert rc == 0

        env = _binding_env(wt, plan_path, 2)
        result = _git_commit(wt, env)

        assert result.returncode != 0
        combined = result.stdout + result.stderr
        assert "REFUSED" in combined
        assert "PRECOMMIT: refused" in combined


class TestB8OtherRepoGoesThrough:
    """(b8) with the binding set, a commit in another repository goes through."""

    def test_b8(self, tmp_path, capsys):
        repo = tmp_path / "r"
        _git_init(repo)
        (repo / "src.py").write_text("x = 1\n")
        _git_commit_all(repo)
        wt = tmp_path / "wt"
        _make_worktree(repo, wt)

        plan_path = tmp_path / "plan.md"
        plan_path.write_text(_make_plan(["src.py"]))

        other = tmp_path / "other"
        _git_init(other)
        (other / "file.py").write_text("y = 1\n")
        _git_commit_all(other)
        (other / "file.py").write_text("y = 2\n")

        env = _binding_env(wt, plan_path, 1)
        result = _git_commit(other, env)
        assert result.returncode == 0


class TestB9RepoOwnHookRuns:
    """(b9) the repository's own pre-commit runs after a passing check; refusing hook refuses commit."""

    def test_b9(self, tmp_path, capsys):
        repo = tmp_path / "r"
        _git_init(repo)
        (repo / "src.py").write_text("x = 1\n")
        _git_commit_all(repo)
        wt = tmp_path / "wt"
        _make_worktree(repo, wt)
        (wt / "src.py").write_text("x = 2\n")

        plan_path = tmp_path / "in-progress-executable-99906.md"
        plan_path.write_text(_make_plan(["src.py"]))

        # Relative path form
        hooks_dir = tmp_path / "custom-hooks"
        hooks_dir.mkdir()
        refusing_hook = hooks_dir / "pre-commit"
        refusing_hook.write_text("#!/bin/sh\necho 'own-hook-refused'; exit 1\n")
        refusing_hook.chmod(0o755)
        rel_hooks = os.path.relpath(str(hooks_dir), str(repo))
        subprocess.run(["git", "-C", str(repo), "config", "core.hooksPath", rel_hooks],
                       check=True, capture_output=True)

        rc, _out = _run(plan_path, 1, wt, capsys)
        assert rc == 0

        env = _binding_env(wt, plan_path, 1)
        result = _git_commit(wt, env)
        assert result.returncode != 0
        assert "own-hook-refused" in result.stdout + result.stderr

        # ~ path form
        fake_home = tmp_path / "home"
        hooks_dir2 = fake_home / "my-hooks"
        hooks_dir2.mkdir(parents=True)
        (hooks_dir2 / "pre-commit").write_text("#!/bin/sh\necho 'tilde-hook-refused'; exit 1\n")
        (hooks_dir2 / "pre-commit").chmod(0o755)
        subprocess.run(["git", "-C", str(repo), "config", "core.hooksPath", "~/my-hooks"],
                       check=True, capture_output=True)

        rc2, _out2 = _run(plan_path, 1, wt, capsys)
        assert rc2 == 0

        env2 = {**_binding_env(wt, plan_path, 1), "HOME": str(fake_home)}
        result2 = _git_commit(wt, env2)
        assert result2.returncode != 0
        assert "tilde-hook-refused" in result2.stdout + result2.stderr


class TestB10RecordedDeletionCommits:
    """(b10) a recorded deletion commits."""

    def test_b10(self, tmp_path, capsys):
        repo = tmp_path / "r"
        _git_init(repo)
        (repo / "to-delete.py").write_text("x = 1\n")
        _git_commit_all(repo)
        wt = tmp_path / "wt"
        _make_worktree(repo, wt)
        (wt / "to-delete.py").unlink()

        plan_path = tmp_path / "in-progress-executable-99907.md"
        plan_path.write_text(_make_plan([]))

        rc, out = _run(plan_path, 1, wt, capsys)
        assert rc == 0

        data = json.loads(_record_path(wt).read_text())
        assert data["files"]["to-delete.py"] is None, "deleted file must have null blob"

        env = _binding_env(wt, plan_path, 1)
        result = _git_commit(wt, env)
        assert result.returncode == 0


class TestB11HookIsExecutable:
    """(b11) hooks/git/pre-commit is committed executable."""

    def test_b11(self):
        hook = HOOKS_DIR / "pre-commit"
        assert hook.exists(), f"hooks/git/pre-commit not found at {hook}"
        assert hook.stat().st_mode & stat.S_IXUSR, "hook must be user-executable"


class TestB12ExtraEnvReachesAgent:
    """(b12) run_step's extra_env reaches the agent's environment beside BELLOWS_DISPATCH."""

    def test_b12(self):
        proc = _make_mock_popen(stdout_data=_CLEAN_NDJSON)
        with patch("runner.subprocess.Popen", return_value=proc) as mock_popen, \
             patch("runner.time.sleep"):
            runner.run_step("test", "/tmp", "claude-haiku-4-5-20251001",
                            extra_env={"TEST_BINDING_KEY": "test_val"})

        env = mock_popen.call_args[1]["env"]
        assert env.get("TEST_BINDING_KEY") == "test_val"
        assert env.get("BELLOWS_DISPATCH") == "1"


class TestB13PreCheckEnvReturnsRightKeys:
    """(b13) _precheck_env returns seven keys for a step naming check_deposit.py; {} for one that doesn't."""

    def test_b13(self, tmp_path):
        repo = tmp_path / "r"
        _git_init(repo)
        (repo / "init.py").write_text("# init\n")
        _git_commit_all(repo, "init")
        wt = tmp_path / "wt"
        _make_worktree(repo, wt)

        bound_text = "## STEP 1 — DEV\n\n> Run `check_deposit.py` lane step --wt wt\n"
        unbound_text = "## STEP 1 — DEV\n\n> Just do something.\n"
        lane_path = tmp_path / "in-progress-executable-99908.md"
        lane_path.write_text(bound_text)

        env_bound = bellows._precheck_env(bound_text, 1, str(wt), str(lane_path))
        assert set(env_bound.keys()) == {
            "GIT_CONFIG_COUNT", "GIT_CONFIG_KEY_0", "GIT_CONFIG_VALUE_0",
            "BELLOWS_PRECHECK_WT", "BELLOWS_PRECHECK_PLAN", "BELLOWS_PRECHECK_STEP",
            "BELLOWS_PYTHON",
        }
        assert env_bound["GIT_CONFIG_VALUE_0"] == str(HOOKS_DIR)
        assert env_bound["BELLOWS_PRECHECK_STEP"] == "1"

        env_unbound = bellows._precheck_env(unbound_text, 1, str(wt), str(lane_path))
        assert env_unbound == {}


class TestB14EmptyEnvForOldGitAndNonLinkedWt:
    """(b14) {} where git predates 2.31, and where the step's directory is not a linked worktree."""

    def test_b14(self, tmp_path):
        repo = tmp_path / "r"
        _git_init(repo)
        (repo / "init.py").write_text("# init\n")
        _git_commit_all(repo, "init")
        wt = tmp_path / "wt"
        _make_worktree(repo, wt)

        plan_text = "## STEP 1 — DEV\n\n> Run check_deposit.py lane step --wt wt\n"
        lane_path = tmp_path / "in-progress-executable-99909.md"
        lane_path.write_text(plan_text)

        # Old git: returns {}
        with patch("bellows._git_version", return_value=(2, 30)):
            env = bellows._precheck_env(plan_text, 1, str(wt), str(lane_path))
        assert env == {}

        # Plain directory inside repo (no .git file): returns {}
        plain_dir = repo / "subdir"
        plain_dir.mkdir()
        env2 = bellows._precheck_env(plan_text, 1, str(plain_dir), str(lane_path))
        assert env2 == {}

        # Main checkout (has .git directory, not file): returns {}
        env3 = bellows._precheck_env(plan_text, 1, str(repo), str(lane_path))
        assert env3 == {}


class TestB15EntryAppendedAfterExisting:
    """(b15) the hook's entry is appended after the environment's existing GIT_CONFIG_* entries."""

    def test_b15(self, tmp_path, monkeypatch):
        repo = tmp_path / "r"
        _git_init(repo)
        (repo / "init.py").write_text("# init\n")
        _git_commit_all(repo, "init")
        wt = tmp_path / "wt"
        _make_worktree(repo, wt)

        plan_text = "## STEP 1 — DEV\n\n> Run check_deposit.py lane step --wt wt\n"
        lane_path = tmp_path / "in-progress-executable-99912.md"
        lane_path.write_text(plan_text)

        monkeypatch.setenv("GIT_CONFIG_COUNT", "2")
        monkeypatch.setenv("GIT_CONFIG_KEY_0", "user.name")
        monkeypatch.setenv("GIT_CONFIG_VALUE_0", "ExistingUser")
        monkeypatch.setenv("GIT_CONFIG_KEY_1", "user.email")
        monkeypatch.setenv("GIT_CONFIG_VALUE_1", "existing@test.com")

        env = bellows._precheck_env(plan_text, 1, str(wt), str(lane_path))
        assert env.get("GIT_CONFIG_COUNT") == "3"
        assert env.get("GIT_CONFIG_KEY_0") == "user.name"
        assert env.get("GIT_CONFIG_KEY_1") == "user.email"
        assert env.get("GIT_CONFIG_KEY_2") == "core.hooksPath"
        assert env.get("GIT_CONFIG_VALUE_2") == str(HOOKS_DIR)


class TestB16SpacedPathsAndStageFlag:
    """(b16) worktree/lane under directory with space; dev-log with space; refusal command runs verbatim."""

    def test_b16(self, tmp_path, capsys):
        spaced = tmp_path / "my repo"
        repo = spaced / "r"
        _git_init(repo)
        (repo / "src.py").write_text("x = 1\n")
        _git_commit_all(repo)
        wt = spaced / "wt"
        _make_worktree(repo, wt)
        (wt / "src.py").write_text("x = 2\n")

        devlog_name = "knowledge/development/dev-log-fixture 2026-09-14.md"
        plan_path = spaced / "in-progress-executable-99913.md"
        plan_path.write_text(_make_plan(["src.py", devlog_name]))

        env = _binding_env(wt, plan_path, 1)
        result = _git_commit(wt, env)

        assert result.returncode != 0
        combined = result.stdout + result.stderr
        assert "--expect-missing" in combined
        assert "PRECOMMIT: refused" in combined

        lines = combined.splitlines()
        cmd_line = next(
            (ln.strip() for ln in lines if ln.strip().startswith(shlex.quote(sys.executable))),
            None,
        )
        assert cmd_line is not None, f"no command line in: {combined}"

        tokens = shlex.split(cmd_line)
        rc_rerun = subprocess.run(tokens, capture_output=True, text=True)
        assert rc_rerun.returncode == 0

        result2 = _git_commit(wt, env)
        assert result2.returncode == 0


class TestB17MainCheckoutRefused:
    """(b17) with binding set, commit in the bound worktree's repository's main checkout is refused."""

    def test_b17(self, tmp_path):
        repo = tmp_path / "r"
        _git_init(repo)
        (repo / "src.py").write_text("x = 1\n")
        _git_commit_all(repo)
        wt = tmp_path / "wt"
        _make_worktree(repo, wt)

        plan_path = tmp_path / "in-progress-executable-99914.md"
        plan_path.write_text(_make_plan(["src.py"]))

        (repo / "src.py").write_text("x = 99\n")
        env = _binding_env(wt, plan_path, 1)
        result = _git_commit(repo, env)

        assert result.returncode != 0
        combined = result.stdout + result.stderr
        assert "REFUSED" in combined
        assert "main checkout" in combined


class TestB18RunPlanPassesBindingPerStep:
    """(b18) run_plan passes each dispatch the binding for the step it dispatches."""

    def test_b18(self, tmp_path):
        # Create a real git repo + worktree so _precheck_env sees a .git file
        repo = tmp_path / "r18"
        _git_init(repo)
        (repo / "init.py").write_text("# init\n")
        _git_commit_all(repo, "init")
        wt = tmp_path / "wt"
        _make_worktree(repo, wt)

        decisions_dir = tmp_path / "proj" / "knowledge" / "decisions"
        decisions_dir.mkdir(parents=True)
        plan_filename = "in-progress-executable-99915.md"
        plan_path = str(decisions_dir / plan_filename)
        plan_text = (
            "# bellows — test\n\n"
            "**Date:** 2026-09-14 | **Project:** bellows | **Execution:** Step 1 (DEV)\n\n"
            "## STEP 1 — DEV\n\n"
            "> Run check_deposit.py lane step --wt wt\n\n"
            "> **Deposits:**\n> - `src.py`\n\n"
            "## STEP 2 — QA\n\n"
            "> Run check_deposit.py lane step --wt wt\n\n"
            "> **Deposits:**\n> - `qa.md`\n"
        )
        with open(plan_path, "w") as f:
            f.write(plan_text)

        from tests.conftest import clear_plan_for_test
        clear_plan_for_test(plan_path)

        config = {"default_model": "claude-haiku-4-5-20251001",
                  "pushover": {"app_key": "", "user_key": ""}}

        captured_calls = []
        call_count = [0]

        step1_parsed = {
            "is_error": False, "escalate": False, "receipt_status": "OK",
            "ceo_flags": [], "cost_usd": 0.01, "stop_reason": "end_turn",
            "result_text": "### Files Deposited\n- `src.py`\n",
            "permission_denials": [],
            "verdict_requested": {"requested": False, "reason": None},
            "session_id": "sess1", "intermediate_decisions": [],
        }
        step2_parsed = {**step1_parsed,
                        "result_text": "### Files Deposited\n- `qa.md`\n",
                        "verdict_requested": {"requested": True, "reason": "step done", "body": "done"}}
        clean_gates = {
            "passed": True, "failures": [], "files_changed": [],
            "plan_header": {
                "Date": "2026-09-14", "Project": "bellows", "Execution": "Step 1 (DEV)",
            },
            "verdict_requested": {"requested": False, "reason": None},
            "is_qa_step": False,
        }

        def mock_run_step(prompt, project_path, model, session_id=None, allowed_tools=None,
                          timeout=300, plan_slug=None, step_num=None,
                          _retry_attempted=False, extra_env=None):
            captured_calls.append({"step_num": step_num, "extra_env": extra_env})
            call_count[0] += 1
            return step1_parsed if call_count[0] == 1 else step2_parsed

        with patch("bellows.runner.run_step", side_effect=mock_run_step), \
             patch("bellows.gates.check", return_value=clean_gates), \
             patch("bellows.notifier.notify_plan_complete"), \
             patch("bellows.verdict.log_to_ledger"), \
             patch("bellows._capture_git_diff", return_value=""), \
             patch("bellows._create_worktree", return_value=str(wt)), \
             patch("bellows._teardown_worktree"), \
             patch("bellows.record_run"), \
             patch("bellows.validators.validate_at_claim",
                   return_value={"rejected": False, "reject_reason": "", "warnings": []}):
            response_server = MagicMock()
            try:
                bellows.run_plan(plan_path, config, response_server)
            except Exception:
                pass

        step1_calls = [c for c in captured_calls if c["step_num"] == 1]
        step2_calls = [c for c in captured_calls if c["step_num"] == 2]
        assert step1_calls and step1_calls[0]["extra_env"] is not None, "step 1 must have extra_env"
        assert step2_calls and step2_calls[0]["extra_env"] is not None, "step 2 must have extra_env"
        assert step2_calls[0]["extra_env"].get("BELLOWS_PRECHECK_STEP") == "2", \
            "step 2's binding must carry step 2"


class TestB19RetryCarriesExtraEnv:
    """(b19) the transient-401 retry carries extra_env."""

    def test_b19(self):
        fail_proc = _make_mock_popen(stdout_data="", stderr_data="401 Unauthorized", returncode=1)
        success_proc = _make_mock_popen(stdout_data=_CLEAN_NDJSON, returncode=0)

        captured_envs = []
        call_count = [0]

        def mock_popen(cmd, *args, **kwargs):
            captured_envs.append(kwargs.get("env", {}))
            call_count[0] += 1
            return fail_proc if call_count[0] == 1 else success_proc

        with patch("runner.subprocess.Popen", side_effect=mock_popen), \
             patch("runner.time.sleep"):
            result = runner.run_step("test", "/tmp", "claude-haiku-4-5-20251001",
                                     extra_env={"BINDING_KEY": "binding_val"})

        assert len(captured_envs) == 2, "retry must have happened"
        assert captured_envs[0].get("BINDING_KEY") == "binding_val"
        assert captured_envs[1].get("BINDING_KEY") == "binding_val"
        assert result["is_error"] is False


class TestB20SymlinkRecordedByTargetPath:
    """(b20) a symlink is recorded by its target's path, as git stages it, and commits."""

    def test_b20(self, tmp_path, capsys):
        repo = tmp_path / "r"
        _git_init(repo)
        (repo / "target.py").write_text("x = 1\n")
        _git_commit_all(repo)
        wt = tmp_path / "wt"
        _make_worktree(repo, wt)
        (wt / "mylink.py").symlink_to("target.py")

        plan_path = tmp_path / "in-progress-executable-99916.md"
        plan_path.write_text(_make_plan(["mylink.py"]))

        rc, out = _run(plan_path, 1, wt, capsys)
        assert rc == 0

        data = json.loads(_record_path(wt).read_text())
        assert "mylink.py" in data["files"]
        assert data["files"]["mylink.py"] is not None

        env = _binding_env(wt, plan_path, 1)
        result = _git_commit(wt, env)
        assert result.returncode == 0


class TestB21CallerDirRestoredAfterCheck:
    """(b21) pre-check from directory holding deposit worktree lacks fails as from worktree;
    caller's directory is restored."""

    def test_b21(self, tmp_path, capsys):
        repo = tmp_path / "r"
        _git_init(repo)
        (repo / "src.py").write_text("x = 1\n")
        _git_commit_all(repo)
        wt = tmp_path / "wt"
        _make_worktree(repo, wt)

        # The deposit is only in the caller's dir, not in the worktree
        plan_path = tmp_path / "in-progress-executable-99917.md"
        plan_path.write_text(_make_plan(["knowledge/development/dev-log-test.md"]))

        caller_dir = tmp_path / "caller"
        caller_dir.mkdir()
        (caller_dir / "knowledge" / "development").mkdir(parents=True)
        (caller_dir / "knowledge" / "development" / "dev-log-test.md").write_text("## A\n\n")

        orig_cwd = os.getcwd()
        try:
            os.chdir(str(caller_dir))
            rc, out = _run(plan_path, 1, wt, capsys)
        finally:
            os.chdir(orig_cwd)

        assert rc == 1, "must fail because deposit is not in the worktree"
        assert "FAIL" in out
        assert os.getcwd() == orig_cwd


class TestB22MutationSurvivorRefusalAndRecovery:
    """(b22) survivor run file → refusal prints rm + rerun; recovery works; last commit clean."""

    def test_b22(self, tmp_path, capsys):
        spaced = tmp_path / "my wt dir"
        repo = spaced / "r"
        _git_init(repo)
        (repo / "src.py").write_text("x = 1\n")
        _git_commit_all(repo)
        wt = spaced / "wt"
        _make_worktree(repo, wt)
        (wt / "src.py").write_text("x = 2\n")

        run_file = "knowledge/mutants/test.run.txt"
        devlog = "knowledge/development/dev-log spaced.md"
        plan_path = spaced / "in-progress-executable-99918.md"
        plan_path.write_text(_make_plan(["src.py", run_file, devlog]))

        (wt / "knowledge" / "mutants").mkdir(parents=True)
        run_file_path = wt / "knowledge" / "mutants" / "test.run.txt"
        run_file_path.write_text("MUTATION: 1 killed, 1 survived, 0 error\n")

        # First commit attempt: run file present with survivor → refused
        env = _binding_env(wt, plan_path, 1)
        result = _git_commit(wt, env)
        assert result.returncode != 0
        combined = result.stdout + result.stderr
        assert "rm -f" in combined
        assert "PRECOMMIT: refused" in combined

        lines = [ln.strip() for ln in combined.splitlines()]
        rm_line = next((ln for ln in lines if ln.startswith("rm -f")), None)
        cmd_line = next(
            (ln for ln in lines if ln.startswith(shlex.quote(sys.executable))),
            None,
        )
        assert rm_line is not None, f"rm -f line not found in: {combined}"
        assert cmd_line is not None, f"command line not found in: {combined}"
        assert "--expect-missing" in cmd_line
        assert "rm" not in cmd_line, "rm must not appear in rerun command"

        # Run rm then rerun
        subprocess.run(shlex.split(rm_line), check=True)
        rc_rerun = subprocess.run(shlex.split(cmd_line), capture_output=True, text=True)
        assert rc_rerun.returncode == 0

        # Retry commit → goes through
        result2 = _git_commit(wt, env)
        assert result2.returncode == 0

        # Last commit scenario: run file clean, all deposits present
        repo2 = tmp_path / "r2"
        _git_init(repo2)
        (repo2 / "src.py").write_text("x = 1\n")
        _git_commit_all(repo2)
        wt2 = tmp_path / "wt2"
        _make_worktree(repo2, wt2)
        (wt2 / "src.py").write_text("x = 2\n")

        plan2 = tmp_path / "in-progress-executable-99919.md"
        plan2.write_text(_make_plan(["src.py", run_file, "knowledge/development/dev-log-test.md"]))

        (wt2 / "knowledge" / "mutants").mkdir(parents=True)
        (wt2 / "knowledge" / "mutants" / "test.run.txt").write_text(
            "MUTATION: 5 killed, 0 survived, 0 error\n")
        (wt2 / "knowledge" / "development").mkdir(parents=True)
        (wt2 / "knowledge" / "development" / "dev-log-test.md").write_text("## A\n\n## B\n\n")

        env2 = _binding_env(wt2, plan2, 1)
        result3 = _git_commit(wt2, env2)
        assert result3.returncode != 0
        combined3 = result3.stdout + result3.stderr
        assert "rm -f" not in combined3, "no rm line at last commit"

        lines3 = [ln.strip() for ln in combined3.splitlines()]
        cmd3 = next(
            (ln for ln in lines3 if ln.startswith(shlex.quote(sys.executable))),
            None,
        )
        assert cmd3 is not None
        assert "--expect-missing" not in cmd3, "no stage flag at last commit"

        rc3 = subprocess.run(shlex.split(cmd3), capture_output=True, text=True)
        assert rc3.returncode == 0

        result4 = _git_commit(wt2, env2)
        assert result4.returncode == 0


class TestB23ScrubFromOutside:
    """(b23) binding keys absent inside the test, observed from a subprocess."""

    def probe_b23_binding_keys_scrubbed(self, monkeypatch):
        for key in ["GIT_CONFIG_COUNT", "BELLOWS_PRECHECK_WT",
                    "BELLOWS_PRECHECK_PLAN", "BELLOWS_PRECHECK_STEP", "BELLOWS_PYTHON"]:
            assert key not in os.environ, f"{key} must be scrubbed by autouse fixture"

    def test_b23(self, tmp_path):
        binding_keys = {
            "GIT_CONFIG_COUNT": "1",
            "GIT_CONFIG_KEY_0": "core.hooksPath",
            "GIT_CONFIG_VALUE_0": "/tmp/fake",
            "BELLOWS_PRECHECK_WT": "/tmp/wt",
            "BELLOWS_PRECHECK_PLAN": "/tmp/plan.md",
            "BELLOWS_PRECHECK_STEP": "1",
            "BELLOWS_PYTHON": sys.executable,
        }
        env = {**os.environ, **binding_keys}
        result = subprocess.run(
            [sys.executable, "-m", "pytest",
             __file__ + "::TestB23ScrubFromOutside::probe_b23_binding_keys_scrubbed",
             "-o", "python_classes=TestB23ScrubFromOutside",
             "-o", "python_functions=probe_b23_*",
             "-q"],
            env=env, capture_output=True, text=True, cwd=str(_BELLOWS_ROOT),
        )
        assert result.returncode == 0, f"probe failed:\n{result.stdout}\n{result.stderr}"


class TestB24WtNotDirectory:
    """(b24) --wt that does not exist or is a file → exit 2; pre-check from removed dir works."""

    def test_b24(self, tmp_path, capsys):
        plan_path = tmp_path / "plan.md"
        plan_path.write_text(_make_plan(["src.py"]))

        # Non-existent path → exit 2
        rc1 = check_deposit.main([str(plan_path), "1", "--wt", str(tmp_path / "no-such-dir")])
        assert rc1 == 2

        # File as --wt → exit 2
        a_file = tmp_path / "afile.txt"
        a_file.write_text("data\n")
        rc2 = check_deposit.main([str(plan_path), "1", "--wt", str(a_file)])
        assert rc2 == 2

        # Removed cwd with absolute --wt: gates run, record written
        repo = tmp_path / "r"
        _git_init(repo)
        (repo / "src.py").write_text("x = 1\n")
        _git_commit_all(repo)
        wt = tmp_path / "wt"
        _make_worktree(repo, wt)
        (wt / "src.py").write_text("x = 2\n")

        plan_path2 = tmp_path / "plan2.md"
        plan_path2.write_text(_make_plan(["src.py"]))

        vanished = tmp_path / "vanished"
        vanished.mkdir()
        orig_cwd = os.getcwd()
        try:
            os.chdir(str(vanished))
            vanished.rmdir()
            argv = [str(plan_path2), "1", "--wt", str(wt)]
            rc3 = check_deposit.main(argv)
            out3 = capsys.readouterr().out
            assert "PRECHECK: pass recorded" in out3
        finally:
            os.chdir(orig_cwd)


class TestB25LiteralPathspecForGlob:
    """(b25) staged a[1].py beside tracked a1.py — --literal-pathspecs prevents glob match."""

    def test_b25(self, tmp_path, capsys):
        repo = tmp_path / "r"
        _git_init(repo)
        (repo / "a1.py").write_text("# a1\n")
        _git_commit_all(repo)
        wt = tmp_path / "wt"
        _make_worktree(repo, wt)
        (wt / "a[1].py").write_text("# bracket\n")

        plan_path = tmp_path / "in-progress-executable-99920.md"
        plan_path.write_text(_make_plan(["a[1].py"]))

        rc, out = _run(plan_path, 1, wt, capsys)
        assert rc == 0

        env = _binding_env(wt, plan_path, 1)
        result = _git_commit(wt, env)
        assert result.returncode == 0
        combined = result.stdout + result.stderr
        assert "PRECOMMIT: verified" in combined
