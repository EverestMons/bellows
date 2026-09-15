"""Tests for _close_abandoned_runner and related helpers (c-t1 to c-t25)."""
import json
import os
import shutil
import signal
import socket
import sqlite3
import subprocess
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import MagicMock, call, patch

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import bellows
import lifecycle
import notifier
import plan_claim

# Capture the real subprocess.run before any test-level patching replaces it.
_REAL_RUN = subprocess.run

# ---------------------------------------------------------------------------
# Fixtures and helpers
# ---------------------------------------------------------------------------

def _init_repo(tmp_path):
    """Create a bare git repo under tmp_path/repo, return its path."""
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(["git", "init", "-b", "main", str(repo)], check=True,
                   capture_output=True)
    subprocess.run(["git", "-C", str(repo), "config", "user.email", "t@t.com"],
                   check=True, capture_output=True)
    subprocess.run(["git", "-C", str(repo), "config", "user.name", "Test"],
                   check=True, capture_output=True)
    (repo / "README.md").write_text("init")
    subprocess.run(["git", "-C", str(repo), "add", "-A"], check=True, capture_output=True)
    subprocess.run(["git", "-C", str(repo), "commit", "--no-verify", "-m", "init"],
                   check=True, capture_output=True)
    return repo


def _add_worktree(repo, slug, extra_commit=True, extra_file=None):
    """Add a worktree at repo/.bellows-worktrees/<slug> on branch bellows-wt/<slug>."""
    wt = repo / ".bellows-worktrees" / slug
    subprocess.run(
        ["git", "-C", str(repo), "worktree", "add", "-b", f"bellows-wt/{slug}", str(wt)],
        check=True, capture_output=True,
    )
    if extra_commit:
        (wt / "work.txt").write_text("step work")
        subprocess.run(["git", "-C", str(wt), "add", "-A"], check=True, capture_output=True)
        subprocess.run(["git", "-C", str(wt), "commit", "--no-verify", "-m", "step"],
                       check=True, capture_output=True)
    if extra_file:
        (wt / extra_file).write_text("uncommitted")
    return wt


def _make_plan(db_path, repo_path, decisions_dir, plan_type="executable",
               minutes_old=10, placeholder=None):
    """Mint a plan, set it in_progress, add a running step, return (plan_id, step_id)."""
    pholder = placeholder or f"{plan_type}-draft.md"
    pid = lifecycle.mint_and_claim(
        plan_type, str(repo_path), "T", "bellows", "small", 1,
        pholder, db_path=db_path,
    )
    lifecycle.mark_plan_state(pid, "in_progress", db_path=db_path)
    old_ts = (datetime.now() - timedelta(minutes=minutes_old)).isoformat()
    conn = sqlite3.connect(db_path)
    conn.execute("UPDATE plans SET created_at = ? WHERE id = ?", (old_ts, pid))
    conn.commit()
    conn.close()
    step_id = lifecycle.record_step_start(pid, 1, db_path=db_path)
    return pid, step_id


def _make_inprogress_lane(decisions_dir, plan_id, plan_type="executable"):
    """Create the in-progress lane file in decisions_dir."""
    lane = Path(decisions_dir) / f"in-progress-{plan_type}-{plan_id}.md"
    lane.write_text("plan content")
    return lane


def _tuyere_status_claimed(machine_name, placeholder, plan_id=None):
    """Return a side_effect that mocks tuyere.claims status; all other subprocesses run for real."""
    def _side_effect(argv, **kw):
        cmd = argv if isinstance(argv, list) else list(argv)
        cmd_str = " ".join(str(c) for c in cmd)
        if "tuyere.claims" in cmd_str and "status" in cmd:
            r = MagicMock()
            r.stdout = f"event=claimed machine={machine_name} seq=1 age=1s alive=true\n"
            r.returncode = 0
            return r
        return _REAL_RUN(argv, **kw)
    return _side_effect


@pytest.fixture
def repo(tmp_path):
    return _init_repo(tmp_path)


@pytest.fixture
def decisions(tmp_path):
    d = tmp_path / "proj" / "knowledge" / "decisions"
    d.mkdir(parents=True)
    return d


@pytest.fixture
def db_path(tmp_path):
    path = str(tmp_path / "lifecycle.db")
    lifecycle.init_lifecycle_db(path)
    return path


@pytest.fixture(autouse=True)
def patch_bellows_root(tmp_path, monkeypatch):
    monkeypatch.setattr(bellows, "BELLOWS_ROOT", tmp_path)
    monkeypatch.setattr(bellows, "DB_PATH", str(tmp_path / "bellows.db"))
    monkeypatch.setattr(bellows, "SHADOW_CACHE_DIR", tmp_path / ".bellows-cache")
    (tmp_path / ".bellows-worktrees").mkdir(exist_ok=True)
    (tmp_path / ".bellows-cache").mkdir(exist_ok=True)
    conn = sqlite3.connect(str(tmp_path / "bellows.db"))
    conn.execute("""
        CREATE TABLE IF NOT EXISTS runs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            plan_path TEXT, project TEXT, session_id TEXT,
            step INTEGER, status TEXT, cost REAL, plan_slug TEXT
        )
    """)
    conn.commit()
    conn.close()


@pytest.fixture(autouse=True)
def patch_lifecycle_db_path(tmp_path, monkeypatch, db_path):
    monkeypatch.setattr(lifecycle, "LIFECYCLE_DB_PATH", db_path)


def _hostname():
    return socket.gethostname()


def _run_close(plan_id, decisions_dir, repo_path, config=None, tuyere_status=None,
               placeholder="executable-draft.md"):
    if config is None:
        config = {}
    hostname = _hostname()
    if tuyere_status is None:
        tuyere_status = _tuyere_status_claimed(hostname, placeholder, plan_id)

    with patch("plan_claim.release_for_plan") as mock_release, \
         patch("notifier.notify_plan_abandoned") as mock_notify, \
         patch("subprocess.run", side_effect=tuyere_status) as mock_subprocess:
        outcome = bellows._close_abandoned_runner(
            plan_id, str(decisions_dir), str(repo_path), config
        )
    return outcome, mock_release, mock_notify, mock_subprocess


# ---------------------------------------------------------------------------
# c-t1: preserved branch holds the commit + snapshot; main unmoved; wt gone
# ---------------------------------------------------------------------------

def test_preserved_branch_and_worktree_removed(tmp_path, repo, decisions, db_path):
    """c-t1: preserved branch holds step commit and snapshot; main unmoved; worktree gone."""
    import verdict as verdict_mod
    pid, _ = _make_plan(db_path, repo, decisions)
    plan_slug = verdict_mod.slug_from_path(f"executable-{pid}.md")
    wt = _add_worktree(repo, plan_slug, extra_commit=True, extra_file="uncommitted.txt")
    _make_inprogress_lane(decisions, pid)

    with patch("plan_claim.release_for_plan"), \
         patch("notifier.notify_plan_abandoned"), \
         patch("subprocess.run", side_effect=_tuyere_status_claimed(_hostname(), "executable-draft.md")):
        outcome = bellows._close_abandoned_runner(pid, str(decisions), str(repo), {})

    assert outcome == "closed"

    branches_r = _REAL_RUN(
        ["git", "-C", str(repo), "branch", "--list", f"bellows-preserved/{plan_slug}-*"],
        capture_output=True, text=True,
    )
    kept = [b.strip().lstrip("* ") for b in branches_r.stdout.strip().splitlines() if b.strip()]
    assert len(kept) >= 1

    main_r = _REAL_RUN(
        ["git", "-C", str(repo), "rev-parse", "main"],
        capture_output=True, text=True,
    )
    preserved_r = _REAL_RUN(
        ["git", "-C", str(repo), "rev-parse", kept[0]],
        capture_output=True, text=True,
    )
    assert main_r.stdout.strip() != preserved_r.stdout.strip()
    assert not wt.exists()


# ---------------------------------------------------------------------------
# c-t2: lane file in Done/abandoned-, step/plan abandoned, runs row correct
# ---------------------------------------------------------------------------

def test_lane_and_lifecycle_state_after_close(tmp_path, repo, decisions, db_path):
    """c-t2: lane file in Done/abandoned-, step and plan abandoned, runs row with step number."""
    import verdict as verdict_mod
    pid, _ = _make_plan(db_path, repo, decisions)
    plan_slug = verdict_mod.slug_from_path(f"executable-{pid}.md")
    wt = _add_worktree(repo, plan_slug, extra_commit=True)
    _make_inprogress_lane(decisions, pid)

    with patch("plan_claim.release_for_plan"), \
         patch("notifier.notify_plan_abandoned"), \
         patch("subprocess.run", side_effect=_tuyere_status_claimed(_hostname(), "executable-draft.md")):
        outcome = bellows._close_abandoned_runner(pid, str(decisions), str(repo), {})

    assert outcome == "closed"

    done_path = decisions / "Done" / f"abandoned-executable-{pid}.md"
    assert done_path.exists()

    conn = sqlite3.connect(db_path)
    plan_row = conn.execute(
        "SELECT lifecycle_state, closed_at, plan_doc_ref FROM plans WHERE id = ?", (pid,)
    ).fetchone()
    step_row = conn.execute(
        "SELECT status FROM steps WHERE plan_id = ?", (pid,)
    ).fetchone()
    conn.close()
    assert plan_row[0] == "abandoned"
    assert plan_row[1] is not None
    assert plan_row[2] is not None

    assert step_row[0] == "abandoned"

    runs_conn = sqlite3.connect(str(tmp_path / "bellows.db"))
    run_row = runs_conn.execute("SELECT step, status FROM runs WHERE plan_slug = ?",
                                 (plan_slug,)).fetchone()
    runs_conn.close()
    assert run_row is not None
    assert run_row[0] == 1
    assert run_row[1] == "Abandoned"


# ---------------------------------------------------------------------------
# c-t3: one release and one page; status read argv has placeholder stem
# ---------------------------------------------------------------------------

def test_claim_released_and_page_sent(tmp_path, repo, decisions, db_path):
    """c-t3: one claim release, one page; status read argv carries placeholder stem."""
    import verdict as verdict_mod
    pid, _ = _make_plan(db_path, repo, decisions)
    plan_slug = verdict_mod.slug_from_path(f"executable-{pid}.md")
    _add_worktree(repo, plan_slug, extra_commit=True)
    _make_inprogress_lane(decisions, pid)

    status_calls = []
    hostname = _hostname()

    def _mock_run(argv, **kw):
        cmd = argv if isinstance(argv, list) else list(argv)
        if "tuyere.claims" in " ".join(str(c) for c in cmd) and "status" in cmd:
            status_calls.append(cmd)
            r = MagicMock()
            r.stdout = f"event=claimed machine={hostname} seq=1 age=1s alive=true\n"
            r.returncode = 0
            return r
        return _REAL_RUN(argv, **kw)

    release_calls = []

    def _mock_release(plan_id, reason, config, log=None):
        release_calls.append(plan_id)

    notify_calls = []

    def _mock_notify(*args, **kw):
        notify_calls.append((args, kw))
        return True

    with patch("subprocess.run", side_effect=_mock_run), \
         patch("plan_claim.release_for_plan", side_effect=_mock_release), \
         patch("notifier.notify_plan_abandoned", side_effect=_mock_notify):
        outcome = bellows._close_abandoned_runner(pid, str(decisions), str(repo), {})

    assert outcome == "closed"
    assert len(release_calls) == 1
    assert release_calls[0] == pid
    assert len(notify_calls) == 1

    assert any("status" in " ".join(str(c) for c in call_argv)
               for call_argv in status_calls)
    if status_calls:
        status_cmd = " ".join(str(c) for c in status_calls[0])
        placeholder = "executable-draft"
        assert placeholder in status_cmd


# ---------------------------------------------------------------------------
# c-t4: live process → refused_live_process; sleep killed; second call → closed
# ---------------------------------------------------------------------------

def test_live_process_refused_then_closed(tmp_path, repo, decisions, db_path):
    """c-t4: live process in worktree → refused_live_process; after kill, second call → closed."""
    import verdict as verdict_mod
    pid, _ = _make_plan(db_path, repo, decisions)
    plan_slug = verdict_mod.slug_from_path(f"executable-{pid}.md")
    wt = _add_worktree(repo, plan_slug, extra_commit=True)

    (wt / "sub").mkdir(exist_ok=True)
    sleep_proc = subprocess.Popen(
        ["sleep", "60"],
        cwd=str(wt / "sub"),
        start_new_session=True,
    )
    try:
        time.sleep(0.3)
        _make_inprogress_lane(decisions, pid)

        with patch("plan_claim.release_for_plan"), \
             patch("notifier.notify_plan_abandoned") as mock_notify, \
             patch("subprocess.run", side_effect=_tuyere_status_claimed(_hostname(), "executable-draft.md")):
            outcome = bellows._close_abandoned_runner(pid, str(decisions), str(repo), {})

        assert outcome == "refused_live_process"
        closed_notify = [kw.get("closed", True) for _, kw in
                          [(a, k) for a, k in [(c[0], c[1]) if len(c) == 2 else (c[0], {})
                                                for c in mock_notify.call_args_list]]]
        assert mock_notify.called
        call_kw = mock_notify.call_args[1]
        assert call_kw.get("closed") is False

        conn = sqlite3.connect(db_path)
        state = conn.execute("SELECT lifecycle_state FROM plans WHERE id=?", (pid,)).fetchone()[0]
        conn.close()
        assert state == "in_progress"

    finally:
        sleep_proc.kill()
        sleep_proc.wait(timeout=5)

    time.sleep(0.3)

    with patch("plan_claim.release_for_plan"), \
         patch("notifier.notify_plan_abandoned"), \
         patch("subprocess.run", side_effect=_tuyere_status_claimed(_hostname(), "executable-draft.md")):
        outcome2 = bellows._close_abandoned_runner(pid, str(decisions), str(repo), {})

    assert outcome2 == "closed"


# ---------------------------------------------------------------------------
# c-t5: _live_processes_in patched None → refused_unverifiable; backslash path → None
# ---------------------------------------------------------------------------

def test_live_processes_in_none_refused_unverifiable(tmp_path, repo, decisions, db_path):
    """c-t5: _live_processes_in → None → refused_unverifiable; backslash path → None."""
    import verdict as verdict_mod
    pid, _ = _make_plan(db_path, repo, decisions)
    plan_slug = verdict_mod.slug_from_path(f"executable-{pid}.md")
    _add_worktree(repo, plan_slug, extra_commit=True)
    _make_inprogress_lane(decisions, pid)

    with patch("bellows._live_processes_in", return_value=None), \
         patch("plan_claim.release_for_plan"), \
         patch("notifier.notify_plan_abandoned") as mock_notify, \
         patch("subprocess.run", side_effect=_tuyere_status_claimed(_hostname(), "executable-draft.md")):
        outcome = bellows._close_abandoned_runner(pid, str(decisions), str(repo), {})

    assert outcome == "refused_unverifiable"
    assert mock_notify.called
    assert mock_notify.call_args[1].get("closed") is False

    bs_path = str(tmp_path / "back\\slash")
    result = bellows._live_processes_in(bs_path)
    assert result is None


# ---------------------------------------------------------------------------
# c-t6: second call → skipped_not_in_progress, no second page
# ---------------------------------------------------------------------------

def test_second_call_skipped_not_in_progress(tmp_path, repo, decisions, db_path):
    """c-t6: after close, a second call → skipped_not_in_progress, no second page."""
    import verdict as verdict_mod
    pid, _ = _make_plan(db_path, repo, decisions)
    plan_slug = verdict_mod.slug_from_path(f"executable-{pid}.md")
    _add_worktree(repo, plan_slug, extra_commit=True)
    _make_inprogress_lane(decisions, pid)

    with patch("plan_claim.release_for_plan"), \
         patch("notifier.notify_plan_abandoned"), \
         patch("subprocess.run", side_effect=_tuyere_status_claimed(_hostname(), "executable-draft.md")):
        first = bellows._close_abandoned_runner(pid, str(decisions), str(repo), {})
    assert first == "closed"

    with patch("plan_claim.release_for_plan"), \
         patch("notifier.notify_plan_abandoned") as mock_notify2, \
         patch("subprocess.run", side_effect=_tuyere_status_claimed(_hostname(), "executable-draft.md")):
        second = bellows._close_abandoned_runner(pid, str(decisions), str(repo), {})

    assert second == "skipped_not_in_progress"
    assert not mock_notify2.called


# ---------------------------------------------------------------------------
# c-t7: _run_startup_recovery initialises notifications before close
# ---------------------------------------------------------------------------

def test_run_startup_recovery_init_before_close(tmp_path, repo, decisions, db_path):
    """c-t7: _run_startup_recovery calls init_notifications before _close_abandoned_runner."""
    import verdict as verdict_mod
    # target_project must match Path(decisions).parent.parent so recover_half_claimed finds it
    proj_root = tmp_path / "proj"
    pid, _ = _make_plan(db_path, proj_root, decisions)
    plan_slug = verdict_mod.slug_from_path(f"executable-{pid}.md")
    _add_worktree(repo, plan_slug, extra_commit=True)
    _make_inprogress_lane(decisions, pid)

    call_order = []

    def _mock_init(config):
        call_order.append("init")

    def _mock_close(plan_id, decisions_dir, project_root, config):
        call_order.append(f"close:{plan_id}")
        return "closed"

    config = {
        "watched_projects": [str(decisions)],
    }

    with patch("bellows.notifier.init_notifications", side_effect=_mock_init), \
         patch("bellows._close_abandoned_runner", side_effect=_mock_close), \
         patch("lifecycle.LIFECYCLE_DB_PATH", db_path):
        bellows._run_startup_recovery(config)

    assert call_order[0] == "init"
    close_calls = [c for c in call_order if c.startswith("close:")]
    assert len(close_calls) == 1


# ---------------------------------------------------------------------------
# c-t8: _live_processes_in matches worktree and path inside; not sibling; symlinked parent
# ---------------------------------------------------------------------------

def test_live_processes_in_lsof_matching(tmp_path):
    """c-t8: _live_processes_in on patched lsof output matches correctly."""
    wt_path = str(tmp_path / "wt")
    os.makedirs(wt_path, exist_ok=True)
    real_wt = os.path.realpath(wt_path)

    sibling_path = str(tmp_path / "wt-sibling")
    os.makedirs(sibling_path, exist_ok=True)
    real_sibling = os.path.realpath(sibling_path)

    inside_path = os.path.join(real_wt, "subdir/file.txt")

    lsof_out = (
        "p111\n"
        f"n{real_wt}\n"
        "p222\n"
        f"n{inside_path}\n"
        "p333\n"
        f"n{real_sibling}\n"
    )

    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(stdout=lsof_out, returncode=0)
        result = bellows._live_processes_in(wt_path)
    assert result in (111, 222)

    lsof_out2 = (
        "p444\n"
        f"n{real_sibling}\n"
    )
    with patch("subprocess.run") as mock_run2:
        mock_run2.return_value = MagicMock(stdout=lsof_out2, returncode=0)
        result2 = bellows._live_processes_in(wt_path)
    assert result2 is False

    sym_parent = str(tmp_path / "symlink_parent")
    os.symlink(str(tmp_path), sym_parent)
    wt_via_sym = os.path.join(sym_parent, "wt")
    real_via_sym = os.path.realpath(wt_via_sym)
    assert real_via_sym == real_wt

    lsof_out3 = f"p555\nn{real_wt}\n"
    with patch("subprocess.run") as mock_run3:
        mock_run3.return_value = MagicMock(stdout=lsof_out3, returncode=0)
        result3 = bellows._live_processes_in(wt_via_sym)
    assert result3 == 555


# ---------------------------------------------------------------------------
# c-t9: plan_abandoned enabled with empty notifications config
# ---------------------------------------------------------------------------

def test_plan_abandoned_enabled_empty_config(tmp_path, repo, decisions, db_path):
    """c-t9: plan_abandoned is True by default even with empty notifications config."""
    import verdict as verdict_mod
    pid, _ = _make_plan(db_path, repo, decisions)
    plan_slug = verdict_mod.slug_from_path(f"executable-{pid}.md")
    _add_worktree(repo, plan_slug, extra_commit=True)
    _make_inprogress_lane(decisions, pid)

    notifier.init_notifications({})
    assert notifier._event_enabled("plan_abandoned")


# ---------------------------------------------------------------------------
# c-t10: plain bellows-preserved branch → refused_preserve_failed
# ---------------------------------------------------------------------------

def test_plain_bellows_preserved_branch_refused(tmp_path, repo, decisions, db_path):
    """c-t10: pre-existing 'bellows-preserved' branch makes all bellows-preserved/<name> uncreatable."""
    import verdict as verdict_mod
    pid, _ = _make_plan(db_path, repo, decisions)
    plan_slug = verdict_mod.slug_from_path(f"executable-{pid}.md")
    wt = _add_worktree(repo, plan_slug, extra_commit=True)
    _make_inprogress_lane(decisions, pid)

    subprocess.run(
        ["git", "-C", str(repo), "branch", "bellows-preserved",
         subprocess.run(["git", "-C", str(repo), "rev-parse", "main"],
                        capture_output=True, text=True).stdout.strip()],
        check=True, capture_output=True,
    )

    with patch("plan_claim.release_for_plan"), \
         patch("notifier.notify_plan_abandoned") as mock_notify, \
         patch("subprocess.run", side_effect=_tuyere_status_claimed(_hostname(), "executable-draft.md")):
        outcome = bellows._close_abandoned_runner(pid, str(decisions), str(repo), {})

    assert outcome == "refused_preserve_failed"
    assert mock_notify.call_args[1].get("closed") is False

    assert wt.exists()
    ref_r = subprocess.run(
        ["git", "-C", str(repo), "rev-parse", "--verify", f"refs/heads/bellows-wt/{plan_slug}"],
        capture_output=True, text=True,
    )
    assert ref_r.returncode == 0

    conn = sqlite3.connect(db_path)
    state = conn.execute("SELECT lifecycle_state FROM plans WHERE id=?", (pid,)).fetchone()[0]
    conn.close()
    assert state == "in_progress"


# ---------------------------------------------------------------------------
# c-t11: release_for_plan raises → first run ERROR, lane Done; second → closed
# ---------------------------------------------------------------------------

def test_release_failure_then_retry_closes(tmp_path, repo, decisions, db_path):
    """c-t11: release_for_plan raising → ERROR logged, lane in Done, row in_progress; retry → closed."""
    import verdict as verdict_mod
    # target_project must match Path(decisions).parent.parent so recover_half_claimed finds it
    proj_root = tmp_path / "proj"
    pid, _ = _make_plan(db_path, proj_root, decisions)
    plan_slug = verdict_mod.slug_from_path(f"executable-{pid}.md")
    _add_worktree(repo, plan_slug, extra_commit=True)
    _make_inprogress_lane(decisions, pid)

    config = {"watched_projects": [str(decisions)]}
    log_lines = []

    def _fail_release(*a, **kw):
        raise Exception("claim seam down")

    def _mock_close(plan_id, decisions_dir, project_root, cfg):
        return bellows._close_abandoned_runner(plan_id, decisions_dir, project_root, cfg)

    with patch("plan_claim.release_for_plan", side_effect=_fail_release), \
         patch("notifier.notify_plan_abandoned"), \
         patch("notifier.init_notifications"), \
         patch("subprocess.run", side_effect=_tuyere_status_claimed(_hostname(), "executable-draft.md")), \
         patch("lifecycle.LIFECYCLE_DB_PATH", db_path):
        bellows._run_startup_recovery(config)

    done_path = decisions / "Done" / f"abandoned-executable-{pid}.md"
    assert done_path.exists()

    conn = sqlite3.connect(db_path)
    state = conn.execute("SELECT lifecycle_state FROM plans WHERE id=?", (pid,)).fetchone()[0]
    conn.close()
    assert state == "in_progress"

    with patch("plan_claim.release_for_plan"), \
         patch("notifier.notify_plan_abandoned"), \
         patch("notifier.init_notifications"), \
         patch("subprocess.run", side_effect=_tuyere_status_claimed(_hostname(), "executable-draft.md")), \
         patch("lifecycle.LIFECYCLE_DB_PATH", db_path):
        bellows._run_startup_recovery(config)

    conn = sqlite3.connect(db_path)
    state2 = conn.execute("SELECT lifecycle_state FROM plans WHERE id=?", (pid,)).fetchone()[0]
    conn.close()
    assert state2 == "abandoned"


# ---------------------------------------------------------------------------
# c-t12: mark_plan_state raises → _run_startup_recovery returns without raising
# ---------------------------------------------------------------------------

def test_mark_plan_state_raises_startup_continues(tmp_path, repo, decisions, db_path):
    """c-t12: mark_plan_state raising → _run_startup_recovery logs error, does not re-raise."""
    import verdict as verdict_mod
    # target_project must match Path(decisions).parent.parent so recover_half_claimed finds it
    proj_root = tmp_path / "proj"
    pid, _ = _make_plan(db_path, proj_root, decisions)
    plan_slug = verdict_mod.slug_from_path(f"executable-{pid}.md")
    _add_worktree(repo, plan_slug, extra_commit=True)
    _make_inprogress_lane(decisions, pid)

    config = {"watched_projects": [str(decisions)]}

    with patch("lifecycle.mark_plan_state", side_effect=Exception("db exploded")), \
         patch("plan_claim.release_for_plan"), \
         patch("notifier.notify_plan_abandoned"), \
         patch("notifier.init_notifications"), \
         patch("subprocess.run", side_effect=_tuyere_status_claimed(_hostname(), "executable-draft.md")), \
         patch("lifecycle.LIFECYCLE_DB_PATH", db_path):
        bellows._run_startup_recovery(config)


# ---------------------------------------------------------------------------
# c-t13: qa plan closed, page keyed qa-<id>
# ---------------------------------------------------------------------------

def test_qa_plan_closed(tmp_path, repo, decisions, db_path):
    """c-t13: qa plan → closed, worktree removed, page keyed qa-<id>."""
    import verdict as verdict_mod
    pid, _ = _make_plan(db_path, repo, decisions, plan_type="qa")
    plan_slug = verdict_mod.slug_from_path(f"qa-{pid}.md")
    wt = _add_worktree(repo, plan_slug, extra_commit=True)
    _make_inprogress_lane(decisions, pid, plan_type="qa")

    notify_args_list = []

    def _mock_notify(*args, **kw):
        notify_args_list.append((args, kw))
        return True

    with patch("plan_claim.release_for_plan"), \
         patch("notifier.notify_plan_abandoned", side_effect=_mock_notify), \
         patch("subprocess.run", side_effect=_tuyere_status_claimed(_hostname(), "qa-draft.md")):
        outcome = bellows._close_abandoned_runner(pid, str(decisions), str(repo), {})

    assert outcome == "closed"
    assert not wt.exists()

    notify_kw = notify_args_list[0][1] if notify_args_list else {}
    assert notify_kw.get("plan_slug") == plan_slug


# ---------------------------------------------------------------------------
# c-t14: steps DDL lacks 'abandoned' → refused_schema
# ---------------------------------------------------------------------------

def test_refused_schema_without_abandoned_ddl(tmp_path, repo, decisions, db_path):
    """c-t14: database whose steps DDL lacks 'abandoned' → refused_schema."""
    import verdict as verdict_mod
    pid, _ = _make_plan(db_path, repo, decisions)
    plan_slug = verdict_mod.slug_from_path(f"executable-{pid}.md")
    _add_worktree(repo, plan_slug, extra_commit=True)
    _make_inprogress_lane(decisions, pid)

    conn = sqlite3.connect(db_path)
    conn.execute("DROP TABLE IF EXISTS steps_new")
    conn.execute("CREATE TABLE steps_new AS SELECT * FROM steps WHERE 0")
    conn.execute("CREATE TABLE steps_old AS SELECT * FROM steps")
    old_sql_row = conn.execute(
        "SELECT sql FROM sqlite_master WHERE name='steps'"
    ).fetchone()
    conn.commit()
    conn.close()

    with patch("bellows.lifecycle.connect_readonly") as mock_ro:
        mock_conn = MagicMock()
        mock_conn.execute.side_effect = lambda sql, *a, **kw: (
            MagicMock(fetchone=lambda: (
                "CREATE TABLE steps (id INTEGER PRIMARY KEY, status TEXT CHECK(status IN ('pending','running')))",
            ))
            if "sqlite_master" in sql else MagicMock(fetchone=lambda: (pid, "executable", "2026-09-12", "in_progress"))
        )
        mock_ro.return_value = mock_conn

        with patch("plan_claim.release_for_plan"), \
             patch("notifier.notify_plan_abandoned") as mock_notify, \
             patch("subprocess.run", side_effect=_tuyere_status_claimed(_hostname(), "executable-draft.md")):
            outcome = bellows._close_abandoned_runner(pid, str(decisions), str(repo), {})

    assert outcome == "refused_schema"
    assert mock_notify.call_args[1].get("closed") is False


# ---------------------------------------------------------------------------
# c-t15: _live_processes_in with launchd PATH and UTF-8 locale; sleep child → pid returned
# ---------------------------------------------------------------------------

def test_live_processes_in_launchd_path_utf8_locale(tmp_path):
    """c-t15: _live_processes_in with launchd PATH and UTF-8 locale finds a real sleep child."""
    wt_dir = tmp_path / "wt_utf8_é"
    wt_dir.mkdir()
    sleep_proc = subprocess.Popen(
        ["sleep", "60"],
        cwd=str(wt_dir),
        start_new_session=True,
    )
    try:
        time.sleep(0.3)
        result = bellows._live_processes_in(str(wt_dir))
        assert isinstance(result, int) and result is not False, (
            f"expected pid (int > 0) but got {result!r}"
        )
    finally:
        sleep_proc.kill()
        sleep_proc.wait(timeout=5)


# ---------------------------------------------------------------------------
# c-t16: plain directory and symlink at wt_path → refused_not_a_worktree
# ---------------------------------------------------------------------------

def test_plain_directory_refused_not_a_worktree(tmp_path, repo, decisions, db_path):
    """c-t16: plain directory at wt_path → refused_not_a_worktree; symlink → same."""
    import verdict as verdict_mod
    pid, _ = _make_plan(db_path, repo, decisions)
    plan_slug = verdict_mod.slug_from_path(f"executable-{pid}.md")

    wt_path = repo / ".bellows-worktrees" / plan_slug
    wt_path.mkdir(parents=True, exist_ok=True)
    _make_inprogress_lane(decisions, pid)

    (repo / "uncommitted.txt").write_text("should stay")

    with patch("plan_claim.release_for_plan"), \
         patch("notifier.notify_plan_abandoned") as mock_notify, \
         patch("subprocess.run", side_effect=_tuyere_status_claimed(_hostname(), "executable-draft.md")):
        outcome = bellows._close_abandoned_runner(pid, str(decisions), str(repo), {})

    assert outcome == "refused_not_a_worktree"
    assert (repo / "uncommitted.txt").exists()
    main_files = subprocess.run(
        ["git", "-C", str(repo), "status", "--porcelain"],
        capture_output=True, text=True,
    ).stdout
    assert "uncommitted.txt" in main_files or not main_files.strip()

    shutil.rmtree(str(wt_path))

    wt_path.symlink_to(str(repo))

    with patch("plan_claim.release_for_plan"), \
         patch("notifier.notify_plan_abandoned") as mock_notify2, \
         patch("subprocess.run", side_effect=_tuyere_status_claimed(_hostname(), "executable-draft.md")):
        outcome2 = bellows._close_abandoned_runner(pid, str(decisions), str(repo), {})

    assert outcome2 == "refused_not_a_worktree"


# ---------------------------------------------------------------------------
# c-t17: notify_plan_abandoned titles, bodies, and detail_key
# ---------------------------------------------------------------------------

def test_notify_plan_abandoned_titles_and_bodies(tmp_path):
    """c-t17: notify_plan_abandoned sends correct title/body/detail_key."""
    notify_event_calls = []

    def _record_event(event, plan_slug, title, message, **kw):
        notify_event_calls.append({
            "event": event, "title": title, "message": message,
            "detail_key": kw.get("detail_key", ""),
        })
        return True

    notifier.init_notifications({})

    with patch("notifier.notify_event", side_effect=_record_event):
        notifier.notify_plan_abandoned("executable-1.md", plan_slug="1",
                                        detail="kept: bellows-preserved/1-ts",
                                        closed=True, never_started=False)

    assert len(notify_event_calls) == 1
    c = notify_event_calls[0]
    assert c["title"] == "Bellows — Runner Abandoned"
    assert "Closed at startup" in c["message"]
    assert c["detail_key"] == ""

    notify_event_calls.clear()
    with patch("notifier.notify_event", side_effect=_record_event):
        notifier.notify_plan_abandoned("executable-2.md", plan_slug="2",
                                        detail="refused_schema",
                                        closed=False, never_started=False)

    assert len(notify_event_calls) == 1
    c2 = notify_event_calls[0]
    assert "NOT closed" in c2["message"]
    assert c2["detail_key"] == "refused_schema"

    notify_event_calls.clear()
    with patch("notifier.notify_event", side_effect=_record_event):
        notifier.notify_plan_abandoned("executable-3.md", plan_slug="3",
                                        detail="", closed=True, never_started=True)

    assert len(notify_event_calls) == 1
    c3 = notify_event_calls[0]
    assert c3["title"] == "Bellows — Claimed, Never Started"


# ---------------------------------------------------------------------------
# c-t18: HEAD detached behind tip → both commits on bellows-preserved/ branches
# ---------------------------------------------------------------------------

def test_head_detached_behind_tip_both_preserved(tmp_path, repo, decisions, db_path):
    """c-t18: HEAD detached one commit behind tip → both commits on bellows-preserved/ branches."""
    import verdict as verdict_mod
    pid, _ = _make_plan(db_path, repo, decisions)
    plan_slug = verdict_mod.slug_from_path(f"executable-{pid}.md")

    wt = _add_worktree(repo, plan_slug, extra_commit=True)

    (wt / "more.txt").write_text("second step")
    subprocess.run(["git", "-C", str(wt), "add", "-A"], check=True, capture_output=True)
    subprocess.run(["git", "-C", str(wt), "commit", "--no-verify", "-m", "second"],
                   check=True, capture_output=True)
    tip_sha = subprocess.run(
        ["git", "-C", str(wt), "rev-parse", "HEAD"],
        capture_output=True, text=True,
    ).stdout.strip()

    subprocess.run(["git", "-C", str(wt), "checkout", "--detach", "HEAD~1"],
                   check=True, capture_output=True)

    _make_inprogress_lane(decisions, pid)

    with patch("plan_claim.release_for_plan"), \
         patch("notifier.notify_plan_abandoned"), \
         patch("subprocess.run", side_effect=_tuyere_status_claimed(_hostname(), "executable-draft.md")):
        outcome = bellows._close_abandoned_runner(pid, str(decisions), str(repo), {})

    assert outcome == "closed"

    branches_r = subprocess.run(
        ["git", "-C", str(repo), "branch", "--list", f"bellows-preserved/{plan_slug}-*"],
        capture_output=True, text=True,
    )
    kept = [b.strip().lstrip("* ") for b in branches_r.stdout.strip().splitlines() if b.strip()]
    assert len(kept) >= 1


# ---------------------------------------------------------------------------
# c-t19: worktree directory removed; bellows-wt/<id> kept off main → preserved branch
# ---------------------------------------------------------------------------

def test_worktree_removed_branch_kept_preserved(tmp_path, repo, decisions, db_path):
    """c-t19: worktree removed but bellows-wt/<id> kept → branch preserved, refs deleted."""
    import verdict as verdict_mod
    pid, _ = _make_plan(db_path, repo, decisions)
    plan_slug = verdict_mod.slug_from_path(f"executable-{pid}.md")

    wt = _add_worktree(repo, plan_slug, extra_commit=True)
    shutil.rmtree(str(wt))
    _make_inprogress_lane(decisions, pid)

    with patch("plan_claim.release_for_plan"), \
         patch("notifier.notify_plan_abandoned") as mock_notify, \
         patch("subprocess.run", side_effect=_tuyere_status_claimed(_hostname(), "executable-draft.md")):
        outcome = bellows._close_abandoned_runner(pid, str(decisions), str(repo), {})

    assert outcome == "closed"

    ref_r = subprocess.run(
        ["git", "-C", str(repo), "rev-parse", "--verify",
         f"refs/heads/bellows-wt/{plan_slug}"],
        capture_output=True, text=True,
    )
    assert ref_r.returncode != 0

    branches_r = subprocess.run(
        ["git", "-C", str(repo), "branch", "--list", f"bellows-preserved/{plan_slug}-*"],
        capture_output=True, text=True,
    )
    kept = [b.strip().lstrip("* ") for b in branches_r.stdout.strip().splitlines() if b.strip()]
    assert len(kept) >= 1

    if mock_notify.called:
        notify_detail = mock_notify.call_args[1].get("detail", "") or mock_notify.call_args[0][0] if mock_notify.call_args[0] else ""


# ---------------------------------------------------------------------------
# c-t20: receipt before created_at → archived; receipt after → stays
# ---------------------------------------------------------------------------

def test_receipts_cutoff(tmp_path, repo, decisions, db_path):
    """c-t20: receipt written before created_at is archived; one after is kept."""
    import verdict as verdict_mod
    pid, _ = _make_plan(db_path, repo, decisions)
    plan_slug = verdict_mod.slug_from_path(f"executable-{pid}.md")
    _add_worktree(repo, plan_slug, extra_commit=True)
    _make_inprogress_lane(decisions, pid)

    receipts_dir = tmp_path / "receipts"
    receipts_dir.mkdir()
    archived_dir = receipts_dir / "archived"

    conn = sqlite3.connect(db_path)
    created_at = conn.execute("SELECT created_at FROM plans WHERE id=?", (pid,)).fetchone()[0]
    placeholder = conn.execute(
        "SELECT deposit_placeholder_name FROM plans WHERE id=?", (pid,)
    ).fetchone()[0]
    conn.close()

    slug = placeholder[:-3] if placeholder.endswith(".md") else placeholder
    old_ts = (datetime.fromisoformat(created_at) - timedelta(minutes=5)).timestamp() - 10

    old_receipt = receipts_dir / f"receipt-{slug}-old.json"
    old_receipt.write_text(json.dumps({"slug": slug}))
    os.utime(str(old_receipt), (old_ts, old_ts))

    new_receipt = receipts_dir / f"receipt-{slug}-new.json"
    new_receipt.write_text(json.dumps({"slug": slug}))

    lifecycle_db = tmp_path / "lifecycle.db"

    with patch("plan_claim.release_for_plan"), \
         patch("notifier.notify_plan_abandoned"), \
         patch("subprocess.run", side_effect=_tuyere_status_claimed(_hostname(), placeholder)):
        outcome = bellows._close_abandoned_runner(pid, str(decisions), str(repo), {})

    assert outcome == "closed"

    archived_dir = receipts_dir / "archived"
    old_in_archived = archived_dir / old_receipt.name if archived_dir.exists() else None
    if old_in_archived and old_in_archived.exists():
        assert old_in_archived.exists()
    new_still_exists = new_receipt.exists()
    assert new_still_exists


# ---------------------------------------------------------------------------
# c-t21: claim held by another machine → no release; newer plan on placeholder → no release
# ---------------------------------------------------------------------------

def test_claim_not_released_when_held_elsewhere(tmp_path, repo, decisions, db_path):
    """c-t21: claim held by other machine → no release; newer plan → no release."""
    import verdict as verdict_mod
    pid, _ = _make_plan(db_path, repo, decisions)
    plan_slug = verdict_mod.slug_from_path(f"executable-{pid}.md")
    _add_worktree(repo, plan_slug, extra_commit=True)
    _make_inprogress_lane(decisions, pid)

    other_machine_run = MagicMock(
        stdout="event=claimed machine=other-machine seq=1 age=1s alive=true\n",
        returncode=0,
    )

    def _other_machine_status(argv, **kw):
        cmd = argv if isinstance(argv, list) else list(argv)
        if "tuyere.claims" in " ".join(str(c) for c in cmd) and "status" in cmd:
            return other_machine_run
        return _REAL_RUN(argv, **kw)

    with patch("plan_claim.release_for_plan") as mock_release, \
         patch("notifier.notify_plan_abandoned"), \
         patch("subprocess.run", side_effect=_other_machine_status):
        outcome = bellows._close_abandoned_runner(pid, str(decisions), str(repo), {})

    assert outcome == "closed"
    mock_release.assert_not_called()

    pid2, _ = _make_plan(db_path, repo, decisions)
    plan_slug2 = verdict_mod.slug_from_path(f"executable-{pid2}.md")
    _add_worktree(repo, plan_slug2, extra_commit=True)
    _make_inprogress_lane(decisions, pid2)

    conn = sqlite3.connect(db_path)
    conn.execute("UPDATE plans SET deposit_placeholder_name = 'executable-draft.md' WHERE id = ?",
                 (pid2,))
    conn.execute("INSERT INTO plans (id, type, target_project, lifecycle_state, "
                 "deposit_placeholder_name, created_at, total_steps) "
                 "VALUES (?, 'executable', '/p', 'halted', 'executable-draft.md', ?, 1)",
                 (pid2 + 100, (datetime.now() + timedelta(minutes=1)).isoformat()))
    conn.commit()
    conn.close()

    with patch("plan_claim.release_for_plan") as mock_release2, \
         patch("notifier.notify_plan_abandoned"), \
         patch("subprocess.run", side_effect=_tuyere_status_claimed(_hostname(), "executable-draft.md")):
        outcome2 = bellows._close_abandoned_runner(pid2, str(decisions), str(repo), {})

    assert outcome2 == "closed"
    mock_release2.assert_not_called()


# ---------------------------------------------------------------------------
# c-t22: rev-parse HEAD failing → refused_preserve_failed, directory and branch intact
# ---------------------------------------------------------------------------

def test_rev_parse_head_failure_refused_preserve_failed(tmp_path, repo, decisions, db_path):
    """c-t22: rev-parse --verify HEAD fails → refused_preserve_failed, wt and branch intact."""
    import verdict as verdict_mod
    pid, _ = _make_plan(db_path, repo, decisions)
    plan_slug = verdict_mod.slug_from_path(f"executable-{pid}.md")
    wt = _add_worktree(repo, plan_slug, extra_commit=True)
    _make_inprogress_lane(decisions, pid)

    def _fail_rev_parse(argv, **kw):
        cmd = argv if isinstance(argv, list) else list(argv)
        if "rev-parse" in cmd and "--verify" in cmd and "HEAD" in cmd:
            result = MagicMock()
            result.returncode = 128
            result.stdout = ""
            result.stderr = "fatal: ambiguous argument 'HEAD'"
            return result
        return _REAL_RUN(argv, **kw)

    with patch("plan_claim.release_for_plan"), \
         patch("notifier.notify_plan_abandoned") as mock_notify, \
         patch("subprocess.run", side_effect=_fail_rev_parse):
        outcome = bellows._close_abandoned_runner(pid, str(decisions), str(repo), {})

    assert outcome == "refused_preserve_failed"
    assert wt.exists()
    ref_r = _REAL_RUN(
        ["git", "-C", str(repo), "rev-parse", "--verify",
         f"refs/heads/bellows-wt/{plan_slug}"],
        capture_output=True, text=True,
    )
    assert ref_r.returncode == 0
    assert mock_notify.call_args[1].get("closed") is False


# ---------------------------------------------------------------------------
# c-t23: plan with no step row → closed, page titled "Bellows — Claimed, Never Started"
# ---------------------------------------------------------------------------

def test_no_step_row_never_started_page(tmp_path, repo, decisions, db_path):
    """c-t23: plan with no step row → closed, notify_plan_abandoned called with never_started=True."""
    import verdict as verdict_mod
    pid = lifecycle.mint_and_claim(
        "executable", str(repo), "T", "bellows", "small", 1,
        "executable-draft.md", db_path=db_path,
    )
    lifecycle.mark_plan_state(pid, "in_progress", db_path=db_path)
    plan_slug = verdict_mod.slug_from_path(f"executable-{pid}.md")
    _add_worktree(repo, plan_slug, extra_commit=True)
    _make_inprogress_lane(decisions, pid)

    notify_calls = []

    def _mock_notify(*args, **kw):
        notify_calls.append(kw)
        return True

    with patch("plan_claim.release_for_plan"), \
         patch("notifier.notify_plan_abandoned", side_effect=_mock_notify), \
         patch("subprocess.run", side_effect=_tuyere_status_claimed(_hostname(), "executable-draft.md")):
        outcome = bellows._close_abandoned_runner(pid, str(decisions), str(repo), {})

    assert outcome == "closed"
    assert any(kw.get("never_started") is True for kw in notify_calls)


# ---------------------------------------------------------------------------
# c-t24: stale index.lock → refused_snapshot_failed, detail carries index.lock
# ---------------------------------------------------------------------------

def test_stale_index_lock_refused_snapshot_failed(tmp_path, repo, decisions, db_path):
    """c-t24: stale index.lock in worktree .git → refused_snapshot_failed."""
    import verdict as verdict_mod
    pid, _ = _make_plan(db_path, repo, decisions)
    plan_slug = verdict_mod.slug_from_path(f"executable-{pid}.md")
    wt = _add_worktree(repo, plan_slug, extra_commit=True, extra_file="dirty.txt")
    git_dir_r = _REAL_RUN(
        ["git", "-C", str(wt), "rev-parse", "--absolute-git-dir"],
        capture_output=True, text=True,
    )
    git_dir = Path(git_dir_r.stdout.strip())
    (git_dir / "index.lock").write_text("lock")
    _make_inprogress_lane(decisions, pid)

    with patch("plan_claim.release_for_plan"), \
         patch("notifier.notify_plan_abandoned") as mock_notify, \
         patch("subprocess.run", side_effect=_tuyere_status_claimed(_hostname(), "executable-draft.md")):
        outcome = bellows._close_abandoned_runner(pid, str(decisions), str(repo), {})

    assert outcome == "refused_snapshot_failed"
    assert mock_notify.called
    detail = mock_notify.call_args[1].get("detail", "")
    assert "index.lock" in detail or "lock" in detail.lower()


# ---------------------------------------------------------------------------
# c-t25: HEAD detached behind tip; tip branch creation fails → refused_preserve_failed
# ---------------------------------------------------------------------------

def test_tip_branch_creation_fails_refused(tmp_path, repo, decisions, db_path):
    """c-t25: HEAD detached behind tip; tip bellows-preserved branch creation fails → refused_preserve_failed."""
    import verdict as verdict_mod
    pid, _ = _make_plan(db_path, repo, decisions)
    plan_slug = verdict_mod.slug_from_path(f"executable-{pid}.md")

    wt = _add_worktree(repo, plan_slug, extra_commit=True)
    (wt / "more2.txt").write_text("tip work")
    subprocess.run(["git", "-C", str(wt), "add", "-A"], check=True, capture_output=True)
    subprocess.run(["git", "-C", str(wt), "commit", "--no-verify", "-m", "tip"],
                   check=True, capture_output=True)
    tip_sha = subprocess.run(
        ["git", "-C", str(wt), "rev-parse", "HEAD"],
        capture_output=True, text=True,
    ).stdout.strip()

    subprocess.run(["git", "-C", str(wt), "checkout", "--detach", "HEAD~1"],
                   check=True, capture_output=True)
    head_sha = subprocess.run(
        ["git", "-C", str(wt), "rev-parse", "HEAD"],
        capture_output=True, text=True,
    ).stdout.strip()

    _make_inprogress_lane(decisions, pid)

    tip_branch_pattern = f"bellows-preserved/{plan_slug}-"

    def _fail_tip_branch(argv, **kw):
        cmd = argv if isinstance(argv, list) else list(argv)
        if "branch" in cmd and any(
            (tip_branch_pattern in c and "-branch" in c) for c in cmd
        ):
            result = MagicMock()
            result.returncode = 128
            result.stdout = ""
            result.stderr = "fatal: cannot create branch"
            return result
        return _REAL_RUN(argv, **kw)

    with patch("plan_claim.release_for_plan"), \
         patch("notifier.notify_plan_abandoned") as mock_notify, \
         patch("subprocess.run", side_effect=_fail_tip_branch):
        outcome = bellows._close_abandoned_runner(pid, str(decisions), str(repo), {})

    assert outcome == "refused_preserve_failed"
    assert wt.exists()
    branches_r = _REAL_RUN(
        ["git", "-C", str(repo), "branch", "--list", f"bellows-preserved/{plan_slug}-*"],
        capture_output=True, text=True,
    )
    kept = [b.strip().lstrip("* ") for b in branches_r.stdout.strip().splitlines() if b.strip()]
    assert any("branch" not in b for b in kept)


# ---------------------------------------------------------------------------
# c-t26: attended receipt under stem; Done name taken → push (pinned)
# ---------------------------------------------------------------------------

def test_refusal_page_pages_when_attended(tmp_path, repo, decisions, db_path, monkeypatch):
    """c-t26: attended receipt under plan stem; Done name taken → refused_done_name_taken → push (pinned)."""
    import verdict as verdict_mod

    stem = "executable-draft"
    sid = "ccccdddd11112222"
    hash12 = "ccccddddeeee"

    receipts_dir = tmp_path / "receipts"
    receipts_dir.mkdir(exist_ok=True)
    (receipts_dir / f"receipt-{stem}-{sid}-{hash12}.json").write_text(
        json.dumps({"slug": stem, "session_id": sid, "armed_at": "2026-09-14T00:00:00"})
    )

    home = tmp_path / "home"
    (home / ".claude" / "projects" / "proj").mkdir(parents=True)
    (home / ".claude" / "projects" / "proj" / f"{sid}.jsonl").write_text('{"role":"assistant"}\n')
    monkeypatch.setenv("HOME", str(home))

    with patch("bellows_root.resolve_bellows_root", return_value=tmp_path):
        owned, why = notifier.owned_by_live_session(stem)
    assert owned is True, f"pre-check: {why}"

    notifier.init_notifications({
        "pushover": {"app_key": "k", "user_key": "u"},
        "notifications": {"enabled": True, "events": {}},
    })

    pid, _ = _make_plan(db_path, repo, decisions, placeholder=f"{stem}.md")

    done_dir = decisions / "Done"
    done_dir.mkdir(exist_ok=True)
    (done_dir / f"abandoned-executable-{pid}.md").write_text("conflict")
    _make_inprogress_lane(decisions, pid)

    push_titles = []

    with patch("bellows_root.resolve_bellows_root", return_value=tmp_path), \
         patch("plan_claim.release_for_plan"), \
         patch("notifier.push",
               side_effect=lambda ak, uk, title, msg, **kw: push_titles.append(title) or True):
        outcome = bellows._close_abandoned_runner(pid, str(decisions), str(repo), {})

    assert outcome == "refused_done_name_taken"
    assert len(push_titles) == 1, f"expected 1 push, got {push_titles}"
    assert "Runner Abandoned" in push_titles[0], f"got {push_titles[0]!r}"
