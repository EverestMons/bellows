"""Tests for _checkout_is_current, _push_main, and their three wire points.

Fixture: synced_repo(tmp_path) — bare origin ← other (first commit pushed) ← project (clone).
"""
import inspect
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import bellows
import verdict
from bellows import (
    _checkout_is_current,
    _push_main,
    _create_worktree,
    _teardown_worktree,
    _retry_recoverable_teardown,
    WorktreeTeardownError,
)
from tests.conftest import clear_plan_for_test

GIT = ["git", "-c", "user.name=t", "-c", "user.email=t@t"]


@pytest.fixture
def synced_repo(tmp_path):
    """Bare origin ← other (first commit pushed) ← project (clone).

    Returns (project: Path, origin: Path, commit_fn).
    commit_fn(message, where="project"|"other", push=False) -> sha
    Every commit writes a unique file so there are no empty-tree commits.
    """
    origin = tmp_path / "origin.git"
    subprocess.run(
        ["git", "init", "--bare", "-b", "main", str(origin)],
        capture_output=True, text=True, check=True,
    )

    other = tmp_path / "other"
    subprocess.run(
        ["git", "clone", str(origin), str(other)],
        capture_output=True, text=True, check=True,
    )
    subprocess.run(["git", "-C", str(other), "config", "user.name", "t"],
                   capture_output=True, text=True)
    subprocess.run(["git", "-C", str(other), "config", "user.email", "t@t"],
                   capture_output=True, text=True)

    # First commit from other — establishes origin/HEAD and origin/main
    (other / "seed.txt").write_text("seed")
    subprocess.run(["git", "-C", str(other), "add", "seed.txt"],
                   capture_output=True, text=True)
    subprocess.run(GIT + ["-C", str(other), "commit", "-m", "seed"],
                   capture_output=True, text=True, check=True)
    subprocess.run(["git", "-C", str(other), "push", "origin", "main"],
                   capture_output=True, text=True, check=True)

    project = tmp_path / "project"
    subprocess.run(
        ["git", "clone", str(origin), str(project)],
        capture_output=True, text=True, check=True,
    )
    subprocess.run(["git", "-C", str(project), "config", "user.name", "t"],
                   capture_output=True, text=True)
    subprocess.run(["git", "-C", str(project), "config", "user.email", "t@t"],
                   capture_output=True, text=True)

    _counter = [0]

    def commit(message, where="project", push=False):
        repo = project if where == "project" else other
        _counter[0] += 1
        fname = f"f{_counter[0]:04d}.txt"
        (repo / fname).write_text(message)
        subprocess.run(["git", "-C", str(repo), "add", fname],
                       capture_output=True, text=True)
        subprocess.run(GIT + ["-C", str(repo), "commit", "-m", message],
                       capture_output=True, text=True, check=True)
        sha = subprocess.run(
            ["git", "-C", str(repo), "rev-parse", "HEAD"],
            capture_output=True, text=True,
        ).stdout.strip()
        if push:
            subprocess.run(["git", "-C", str(repo), "push", "origin", "main"],
                           capture_output=True, text=True, check=True)
        return sha

    return project, origin, commit


# ---------------------------------------------------------------------------
# Test 1: current → (True, "current")
# ---------------------------------------------------------------------------

def test_checkout_is_current_on_synced_repo(synced_repo):
    project, origin, commit = synced_repo
    ok, detail = _checkout_is_current(str(project))
    assert ok is True
    assert detail == "current"


# ---------------------------------------------------------------------------
# Test 2: behind → (False, detail) with "1 behind / 0 ahead", "pull", "releases itself"
# ---------------------------------------------------------------------------

def test_checkout_behind(synced_repo):
    project, origin, commit = synced_repo
    commit("other pushed commit", where="other", push=True)
    ok, detail = _checkout_is_current(str(project))
    assert ok is False
    assert "1 behind / 0 ahead" in detail
    assert "pull" in detail
    assert "releases itself" in detail


# ---------------------------------------------------------------------------
# Test 3: ahead → (False, ...) with "0 behind / 1 ahead" and "push"
# ---------------------------------------------------------------------------

def test_checkout_ahead(synced_repo):
    project, origin, commit = synced_repo
    commit("unpushed project commit")
    ok, detail = _checkout_is_current(str(project))
    assert ok is False
    assert "0 behind / 1 ahead" in detail
    assert "push" in detail


# ---------------------------------------------------------------------------
# Test 4: no remote → (False, "fetch failed: ...") — fail-closed, no exception
# ---------------------------------------------------------------------------

def test_checkout_no_remote_fails_closed(synced_repo):
    project, origin, commit = synced_repo
    subprocess.run(
        ["git", "-C", str(project), "remote", "remove", "origin"],
        capture_output=True, text=True,
    )
    ok, detail = _checkout_is_current(str(project))
    assert ok is False
    assert detail.startswith("fetch failed:")


# ---------------------------------------------------------------------------
# Test 5: fetch updates only refs/remotes/origin/* — main sha unchanged, tree clean
# ---------------------------------------------------------------------------

def test_fetch_does_not_move_local_branch(synced_repo):
    project, origin, commit = synced_repo
    commit("other advance", where="other", push=True)
    sha_before = subprocess.run(
        ["git", "-C", str(project), "rev-parse", "main"],
        capture_output=True, text=True,
    ).stdout.strip()
    _checkout_is_current(str(project))
    sha_after = subprocess.run(
        ["git", "-C", str(project), "rev-parse", "main"],
        capture_output=True, text=True,
    ).stdout.strip()
    assert sha_before == sha_after
    status = subprocess.run(
        ["git", "-C", str(project), "status", "--porcelain"],
        capture_output=True, text=True,
    ).stdout.strip()
    assert status == ""


# ---------------------------------------------------------------------------
# Test 6: _push_main on a current checkout with one local commit
# ---------------------------------------------------------------------------

def test_push_main_succeeds(synced_repo):
    project, origin, commit = synced_repo
    sha = commit("push test commit")
    ok, _detail = _push_main(str(project), "main")
    assert ok is True
    origin_sha = subprocess.run(
        ["git", "--git-dir", str(origin), "rev-parse", "main"],
        capture_output=True, text=True,
    ).stdout.strip()
    assert origin_sha == sha


# ---------------------------------------------------------------------------
# Test 7: _teardown_worktree → returns sha, worktree removed, origin carries sha
# ---------------------------------------------------------------------------

def test_teardown_pushes_to_origin(synced_repo):
    project, origin, commit = synced_repo
    wt_path = _create_worktree(str(project), "test-7")
    (Path(wt_path) / "wt7.txt").write_text("wt7")
    subprocess.run(["git", "-C", wt_path, "add", "wt7.txt"], capture_output=True)
    subprocess.run(GIT + ["-C", wt_path, "commit", "-m", "wt7 commit"],
                   capture_output=True, text=True, check=True)
    wt_sha = subprocess.run(
        ["git", "-C", wt_path, "rev-parse", "HEAD"],
        capture_output=True, text=True,
    ).stdout.strip()

    shas = _teardown_worktree(str(project), wt_path, "test-7")

    assert wt_sha in shas
    assert not os.path.isdir(wt_path)
    origin_sha = subprocess.run(
        ["git", "--git-dir", str(origin), "rev-parse", "main"],
        capture_output=True, text=True,
    ).stdout.strip()
    project_sha = subprocess.run(
        ["git", "-C", str(project), "rev-parse", "HEAD"],
        capture_output=True, text=True,
    ).stdout.strip()
    assert origin_sha == project_sha
    log_out = subprocess.run(
        ["git", "--git-dir", str(origin), "log", "--format=%H"],
        capture_output=True, text=True,
    ).stdout
    assert wt_sha in log_out


# ---------------------------------------------------------------------------
# Test 8: _teardown_worktree when origin/main advanced → push rejected, error raised
# ---------------------------------------------------------------------------

def test_teardown_push_rejected_raises(synced_repo):
    project, origin, commit = synced_repo
    wt_path = _create_worktree(str(project), "test-8")
    (Path(wt_path) / "wt8.txt").write_text("wt8")
    subprocess.run(["git", "-C", wt_path, "add", "wt8.txt"], capture_output=True)
    subprocess.run(GIT + ["-C", wt_path, "commit", "-m", "wt8 commit"],
                   capture_output=True, text=True, check=True)
    wt_sha = subprocess.run(
        ["git", "-C", wt_path, "rev-parse", "HEAD"],
        capture_output=True, text=True,
    ).stdout.strip()
    # Advance origin behind project's back
    commit("origin advance for 8", where="other", push=True)

    with pytest.raises(WorktreeTeardownError) as exc_info:
        _teardown_worktree(str(project), wt_path, "test-8")

    err = str(exc_info.value)
    assert "worktree_teardown_push_rejected" in err
    assert "push rejected" in err
    assert "git merge origin/main" in err
    # Worktree and branch still exist
    assert os.path.isdir(wt_path)
    r = subprocess.run(
        ["git", "-C", str(project), "rev-parse", "--verify", "refs/heads/bellows-wt/test-8"],
        capture_output=True,
    )
    assert r.returncode == 0
    # Local main contains the worktree sha
    project_sha = subprocess.run(
        ["git", "-C", str(project), "rev-parse", "HEAD"],
        capture_output=True, text=True,
    ).stdout.strip()
    assert project_sha == wt_sha


# ---------------------------------------------------------------------------
# Test 9: wire point A — stale checkout holds the plan; current proceeds
# ---------------------------------------------------------------------------

def test_wire_point_a_stale_checkout():
    # Scenario 1: stale checkout → hold pair written, claim_gate NOT called
    with tempfile.TemporaryDirectory() as tmp:
        decisions_dir = os.path.join(tmp, "proj", "knowledge", "decisions")
        os.makedirs(os.path.join(decisions_dir, "Done"))
        plan_name = "executable-wire-a-2026-09-09.md"
        plan_path = os.path.join(decisions_dir, plan_name)
        with open(plan_path, "w") as f:
            f.write("# Wire A Test\n\n## STEP 1\ntest\n")
        clear_plan_for_test(plan_path)
        config = {
            "default_model": "claude-sonnet-4-6",
            "pushover": {"app_key": "", "user_key": ""},
            "callback_port": 5999,
            "step_timeout_seconds": 600,
        }
        claim_gate_mock = MagicMock(return_value=True)
        mint_mock = MagicMock(return_value=1)
        log_calls = []

        with patch("bellows._checkout_is_current", return_value=(False, "stale checkout: test")), \
             patch("bellows.notifier.notify_plan_skipped"), \
             patch("bellows.plan_claim.release_for_plan"), \
             patch("bellows.lifecycle.mark_plan_state"), \
             patch("bellows._retire_receipts"), \
             patch("bellows.validators.validate_at_claim",
                   return_value={"rejected": False, "reject_reason": "", "warnings": []}), \
             patch("bellows.plan_claim.claim_gate", claim_gate_mock), \
             patch("bellows.lifecycle.mint_and_claim", mint_mock), \
             patch("bellows._log",
                   side_effect=lambda level, msg, *a, **kw: log_calls.append((level, msg))):
            bellows.run_plan(plan_path, config, MagicMock())

        claim_gate_mock.assert_not_called()
        mint_mock.assert_not_called()
        hold_path = os.path.join(decisions_dir, f"hold-{plan_name}")
        sidecar_path = os.path.splitext(hold_path)[0] + ".hold.json"
        assert os.path.exists(hold_path), f"hold file missing: {hold_path}"
        assert not os.path.exists(plan_path), "bare plan file should be gone"
        with open(sidecar_path) as f:
            data = json.load(f)
        assert data["hold_reason"] == "stale-checkout"
        assert data["detail"] == "stale checkout: test"
        hold_logs = [m for level, m in log_calls if "HOLD" in m]
        assert len(hold_logs) == 1

    # Scenario 2: current checkout → existing flow proceeds (claim_gate called)
    with tempfile.TemporaryDirectory() as tmp2:
        decisions_dir2 = os.path.join(tmp2, "proj", "knowledge", "decisions")
        os.makedirs(os.path.join(decisions_dir2, "Done"))
        plan_name2 = "executable-wire-a-current-2026-09-09.md"
        plan_path2 = os.path.join(decisions_dir2, plan_name2)
        with open(plan_path2, "w") as f:
            f.write("# Wire A Current\n\n")  # no STEP headers → zero-step skip
        clear_plan_for_test(plan_path2)
        config2 = {
            "default_model": "claude-sonnet-4-6",
            "pushover": {"app_key": "", "user_key": ""},
            "callback_port": 5999,
            "step_timeout_seconds": 600,
        }
        claim_gate_mock2 = MagicMock(return_value=True)
        mint_mock2 = MagicMock(return_value=1)

        with patch("bellows._checkout_is_current", return_value=(True, "current")), \
             patch("bellows.notifier.notify_plan_skipped"), \
             patch("bellows.plan_claim.release_for_plan"), \
             patch("bellows.lifecycle.mark_plan_state"), \
             patch("bellows._retire_receipts"), \
             patch("bellows.validators.validate_at_claim",
                   return_value={"rejected": False, "reject_reason": "", "warnings": []}), \
             patch("bellows.plan_claim.claim_gate", claim_gate_mock2), \
             patch("bellows.lifecycle.mint_and_claim", mint_mock2):
            bellows.run_plan(plan_path2, config2, MagicMock())

        claim_gate_mock2.assert_called()


# ---------------------------------------------------------------------------
# Test 10: no --force, rebase, or reset in _checkout_is_current or _push_main
# ---------------------------------------------------------------------------

def test_no_force_rebase_reset_in_helpers():
    src_check = inspect.getsource(_checkout_is_current)
    src_push = inspect.getsource(_push_main)
    for name, src in [("_checkout_is_current", src_check), ("_push_main", src_push)]:
        assert "--force" not in src, f"--force found in {name}"
        assert "rebase" not in src, f"rebase found in {name}"
        assert "reset" not in src, f"reset found in {name}"
    # Push argv explicitly: "push" present, "--force" absent
    assert '"push"' in src_push or "'push'" in src_push
    assert '"--force"' not in src_push
    assert "'--force'" not in src_push


# ---------------------------------------------------------------------------
# Test 11: no .git dir → (True, "not a git repo — in-place"), no subprocess.run
# ---------------------------------------------------------------------------

def test_no_git_dir_returns_in_place(tmp_path):
    project = tmp_path / "no_git_project"
    project.mkdir()
    called = []

    with patch("subprocess.run", side_effect=lambda *a, **kw: called.append(a) or MagicMock(returncode=0, stdout="", stderr="")):
        ok, detail = _checkout_is_current(str(project))

    assert ok is True
    assert detail == "not a git repo — in-place"
    assert not called, f"subprocess.run was called: {called}"


# ---------------------------------------------------------------------------
# Test 12: helpers never raise; diverged → "1 behind / 1 ahead"
# ---------------------------------------------------------------------------

def test_helpers_never_raise_and_diverged(synced_repo):
    project, origin, commit = synced_repo

    # TimeoutExpired → (False, "fetch failed: ...")
    with patch("subprocess.run", side_effect=subprocess.TimeoutExpired(["git"], 30)):
        ok, detail = _checkout_is_current(str(project))
    assert ok is False
    assert "fetch failed" in detail

    # TimeoutExpired → (False, "push failed: ...")
    with patch("subprocess.run", side_effect=subprocess.TimeoutExpired(["git"], 60)):
        ok, detail = _push_main(str(project), "main")
    assert ok is False
    assert "push failed" in detail

    # Diverged: other pushes AND project commits (both behind and ahead)
    commit("other diverge", where="other", push=True)
    commit("project diverge")
    ok, detail = _checkout_is_current(str(project))
    assert ok is False
    assert "1 behind / 1 ahead" in detail


# ---------------------------------------------------------------------------
# Test 13: wire point C — retry admits worktree_teardown_push_rejected
# ---------------------------------------------------------------------------

def test_wire_point_c_retry_admits_push_rejected(synced_repo):
    project, origin, commit = synced_repo

    # Reproduce the test-8 scenario
    wt_path = _create_worktree(str(project), "test-13")
    (Path(wt_path) / "wt13.txt").write_text("wt13")
    subprocess.run(["git", "-C", wt_path, "add", "wt13.txt"], capture_output=True)
    subprocess.run(GIT + ["-C", wt_path, "commit", "-m", "wt13 commit"],
                   capture_output=True, text=True, check=True)
    wt_sha = subprocess.run(
        ["git", "-C", wt_path, "rev-parse", "HEAD"],
        capture_output=True, text=True,
    ).stdout.strip()
    commit("origin advance for 13", where="other", push=True)

    with pytest.raises(WorktreeTeardownError) as exc_info:
        _teardown_worktree(str(project), wt_path, "test-13")
    assert "worktree_teardown_push_rejected" in str(exc_info.value)

    # Hand fix: fetch and merge origin/main in project (simulates CEO recovery)
    subprocess.run(["git", "-C", str(project), "fetch", "origin"],
                   capture_output=True, text=True)
    subprocess.run(GIT + ["-C", str(project), "merge", "origin/main", "--no-edit"],
                   capture_output=True, text=True)

    gate_result = {
        "failures": [{"gate": "worktree_teardown",
                      "evidence": "worktree_teardown_push_rejected"}]
    }
    shas = _retry_recoverable_teardown(gate_result, str(project), wt_path, "test-13")

    assert isinstance(shas, list)
    log_out = subprocess.run(
        ["git", "--git-dir", str(origin), "log", "--format=%H"],
        capture_output=True, text=True,
    ).stdout
    assert wt_sha in log_out
    assert gate_result["failures"] == []

    # Negative: evidence = worktree_teardown_content_conflict → returns [], logs "not retrying"
    # Use a fresh temp dir as wt_path so the isdir check passes and the evidence check fires
    import tempfile as _tf
    with _tf.TemporaryDirectory() as _fake_wt:
        gate_result2 = {
            "failures": [{"gate": "worktree_teardown",
                          "evidence": "worktree_teardown_content_conflict"}]
        }
        log_calls = []
        with patch("bellows._log", side_effect=lambda *a, **kw: log_calls.append(a)):
            result2 = _retry_recoverable_teardown(
                gate_result2, str(project), _fake_wt, "test-13-neg")
        assert result2 == []
        assert any("not retrying" in str(a) for a in log_calls)
        assert len(gate_result2["failures"]) == 1


# ---------------------------------------------------------------------------
# Test 14: HEAD not on <b> → (False, "stale checkout: HEAD is on <x>, not main")
# ---------------------------------------------------------------------------

def test_head_not_on_main_branch(synced_repo):
    project, origin, commit = synced_repo
    subprocess.run(
        ["git", "-C", str(project), "checkout", "-b", "side"],
        capture_output=True, text=True,
    )
    ok, detail = _checkout_is_current(str(project))
    assert ok is False
    assert "HEAD is on side, not main" in detail


# ---------------------------------------------------------------------------
# Test 15: wire point A′ — _rescan self-releases stale-checkout holds
# ---------------------------------------------------------------------------

def test_rescan_self_release(tmp_path):
    def make_scenario(idx):
        d = tmp_path / f"s{idx}" / "proj" / "knowledge" / "decisions"
        d.mkdir(parents=True)
        cfg = {"watched_projects": [str(d)], "callback_port": 5999}
        b = bellows.Bellows(cfg)
        mock_orc = MagicMock()
        mock_orc.config = cfg
        mock_orc._seen = set()
        handler = bellows.PlanHandler(mock_orc)
        return d, b, handler

    def make_hold(d, name, held_at):
        hf = d / f"hold-{name}.md"
        sc = d / f"hold-{name}.hold.json"
        hf.write_text(f"# {name}\n")
        sc.write_text(json.dumps({"hold_reason": "stale-checkout", "held_at": held_at}))
        return hf, sc

    # --- Scenario 1: (True, "current") → hold released ---
    d1, b1, h1 = make_scenario(1)
    hf1, sc1 = make_hold(d1, "exec-release-2026-09-09", "2026-09-09T10:00:00")
    bare1 = d1 / "exec-release-2026-09-09.md"
    calls1 = [0]

    def fake_current_s1(proj, slug=None, fetch_timeout=30):
        calls1[0] += 1
        assert fetch_timeout == 10
        return (True, "current")

    with patch("bellows._checkout_is_current", side_effect=fake_current_s1), \
         patch.object(b1, "_consume_verdicts"), \
         patch.object(b1, "_resume_parked"), \
         patch("bellows._log"):
        b1._rescan(h1)

    assert calls1[0] == 1
    assert not hf1.exists(), "hold file should be removed on release"
    assert not sc1.exists(), "sidecar should be removed on release"
    assert bare1.exists(), "bare plan file should appear after release"

    # --- Scenario 2: (False, ...) → pair untouched ---
    d2, b2, h2 = make_scenario(2)
    hf2, sc2 = make_hold(d2, "exec-keep-2026-09-09", "2026-09-09T11:00:00")

    with patch("bellows._checkout_is_current", return_value=(False, "still stale")), \
         patch.object(b2, "_consume_verdicts"), \
         patch.object(b2, "_resume_parked"), \
         patch("bellows._log"):
        b2._rescan(h2)

    assert hf2.exists(), "hold file must stay on False"
    assert sc2.exists(), "sidecar must stay on False"

    # --- Scenario 3: two held pairs → only oldest checked (exactly one call) ---
    d3, b3, h3 = make_scenario(3)
    make_hold(d3, "exec-old-2026-09-09", "2026-09-09T08:00:00")
    make_hold(d3, "exec-new-2026-09-09", "2026-09-09T09:00:00")
    checked3 = []

    def fake_track_s3(proj, slug=None, fetch_timeout=30):
        checked3.append(fetch_timeout)
        return (False, "still stale")

    with patch("bellows._checkout_is_current", side_effect=fake_track_s3), \
         patch.object(b3, "_consume_verdicts"), \
         patch.object(b3, "_resume_parked"), \
         patch("bellows._log"):
        b3._rescan(h3)

    assert len(checked3) == 1, f"expected 1 check, got {len(checked3)}"
    assert checked3[0] == 10

    # --- Scenario 4: bare file already present → pair untouched, WARN logged ---
    d4, b4, h4 = make_scenario(4)
    hf4, sc4 = make_hold(d4, "exec-conflict-2026-09-09", "2026-09-09T12:00:00")
    (d4 / "exec-conflict-2026-09-09.md").write_text("# already here\n")
    warn_logs = []

    def capture_warn(level, msg, *a, **kw):
        if "WARN" in str(level):
            warn_logs.append(msg)

    with patch("bellows._checkout_is_current", return_value=(True, "current")), \
         patch.object(b4, "_consume_verdicts"), \
         patch.object(b4, "_resume_parked"), \
         patch("bellows._log", side_effect=capture_warn):
        b4._rescan(h4)

    assert hf4.exists(), "hold file must stay when bare already exists"
    assert sc4.exists(), "sidecar must stay when bare already exists"
    assert warn_logs, f"expected at least one WARN; got: {warn_logs}"
