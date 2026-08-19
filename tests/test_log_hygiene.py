import os
import sys
import time
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import bellows


# --- Prune tests ---


def test_prune_deletes_old_json_only(tmp_path):
    """Old .json files are deleted; fresh .json, non-json, and terminal/ survive."""
    logs_dir = tmp_path / "logs"
    logs_dir.mkdir()

    # Old .json (should be pruned)
    old1 = logs_dir / "step-001.json"
    old1.write_text("{}")
    old2 = logs_dir / "step-002.json"
    old2.write_text("{}")
    cutoff_mtime = time.time() - 31 * 86400
    os.utime(old1, (cutoff_mtime, cutoff_mtime))
    os.utime(old2, (cutoff_mtime, cutoff_mtime))

    # Fresh .json (should survive)
    fresh = logs_dir / "step-003.json"
    fresh.write_text("{}")

    # Non-json file (should survive)
    txt = logs_dir / "daemon-nohup.log"
    txt.write_text("log line")

    # terminal/ subdir (should survive, never touched)
    terminal = logs_dir / "terminal"
    terminal.mkdir()
    term_file = terminal / "session.log"
    term_file.write_text("terminal log")

    config = {"log_retention_days": 30}
    with patch.object(bellows, "BELLOWS_ROOT", tmp_path), \
         patch.object(bellows, "_log"):
        bellows._prune_old_logs(config)

    assert not old1.exists()
    assert not old2.exists()
    assert fresh.exists()
    assert txt.exists()
    assert terminal.is_dir()
    assert term_file.exists()


def test_prune_uses_config_retention_days(tmp_path):
    """Respects a custom retention_days value from config."""
    logs_dir = tmp_path / "logs"
    logs_dir.mkdir()

    # File 10 days old — survives with default 30, pruned with 5
    target = logs_dir / "step-old.json"
    target.write_text("{}")
    mtime = time.time() - 10 * 86400
    os.utime(target, (mtime, mtime))

    config = {"log_retention_days": 5}
    with patch.object(bellows, "BELLOWS_ROOT", tmp_path), \
         patch.object(bellows, "_log"):
        bellows._prune_old_logs(config)

    assert not target.exists()


def test_prune_exception_does_not_crash(tmp_path):
    """An unreadable/undeletable file logs WARN and continues (C1)."""
    logs_dir = tmp_path / "logs"
    logs_dir.mkdir()

    old = logs_dir / "step-bad.json"
    old.write_text("{}")
    cutoff_mtime = time.time() - 31 * 86400
    os.utime(old, (cutoff_mtime, cutoff_mtime))

    config = {"log_retention_days": 30}
    log_mock = MagicMock()
    with patch.object(bellows, "BELLOWS_ROOT", tmp_path), \
         patch.object(bellows, "_log", log_mock), \
         patch("os.remove", side_effect=PermissionError("denied")):
        bellows._prune_old_logs(config)

    warn_calls = [c for c in log_mock.call_args_list if c[0][0] == "WARN"]
    assert len(warn_calls) >= 1


def test_prune_no_logs_dir(tmp_path):
    """Missing logs/ dir is a no-op, not a crash."""
    config = {"log_retention_days": 30}
    with patch.object(bellows, "BELLOWS_ROOT", tmp_path), \
         patch.object(bellows, "_log"):
        bellows._prune_old_logs(config)


# --- Preflight tests ---


def _make_statvfs_result(free_gb):
    """Build a fake statvfs result with the given free space in GB."""
    mock = MagicMock()
    mock.f_frsize = 4096
    mock.f_bavail = int(free_gb * (1024 ** 3) / 4096)
    return mock


def test_preflight_passes_above_threshold():
    config = {"disk_min_free_gb": 2}
    bellows._disk_low_notified = False
    with patch("os.statvfs", return_value=_make_statvfs_result(10.0)), \
         patch.object(bellows, "_log"):
        assert bellows._disk_preflight(config) is True


def test_preflight_fails_below_threshold():
    config = {"disk_min_free_gb": 2}
    bellows._disk_low_notified = False
    with patch("os.statvfs", return_value=_make_statvfs_result(1.0)), \
         patch.object(bellows, "_log"):
        assert bellows._disk_preflight(config) is False


def test_preflight_onset_flag_dedupes_notifier():
    """First low-disk call notifies; second call with same condition does not."""
    config = {
        "disk_min_free_gb": 2,
        "pushover": {"app_key": "ak", "user_key": "uk"},
    }
    bellows._disk_low_notified = False
    push_mock = MagicMock()
    with patch("os.statvfs", return_value=_make_statvfs_result(0.5)), \
         patch.object(bellows, "_log"), \
         patch.object(bellows.notifier, "push", push_mock):
        bellows._disk_preflight(config)
        bellows._disk_preflight(config)

    assert push_mock.call_count == 1


def test_preflight_onset_flag_resets_on_recovery():
    """Flag resets when disk recovers, allowing re-notification on next onset."""
    config = {
        "disk_min_free_gb": 2,
        "pushover": {"app_key": "ak", "user_key": "uk"},
    }
    bellows._disk_low_notified = True
    with patch("os.statvfs", return_value=_make_statvfs_result(10.0)), \
         patch.object(bellows, "_log"):
        bellows._disk_preflight(config)

    assert bellows._disk_low_notified is False


def test_preflight_statvfs_failure_degrades_to_allow():
    """A statvfs failure logs WARN and returns True (C1 — degraded guard)."""
    config = {"disk_min_free_gb": 2}
    bellows._disk_low_notified = False
    log_mock = MagicMock()
    with patch("os.statvfs", side_effect=OSError("disk error")), \
         patch.object(bellows, "_log", log_mock):
        result = bellows._disk_preflight(config)

    assert result is True
    warn_calls = [c for c in log_mock.call_args_list if c[0][0] == "WARN"]
    assert len(warn_calls) >= 1


# --- Config default tests ---


def test_config_defaults_log_retention_days():
    """log_retention_days defaults to 30 when absent from config."""
    config = {}
    assert config.get("log_retention_days", 30) == 30


def test_config_defaults_disk_min_free_gb():
    """disk_min_free_gb defaults to 5 when absent from config."""
    config = {}
    assert config.get("disk_min_free_gb", 5) == 5


# --- Mid-session hygiene helper tests ---


def test_hygiene_skips_before_interval():
    """Before the interval elapses, _maybe_run_hygiene is a no-op."""
    prune_mock = MagicMock()
    rotate_mock = MagicMock()
    last = 1000.0
    now = 1000.0 + 3600  # 1h < 6h interval
    interval = 6 * 3600
    with patch.object(bellows, "_prune_old_logs", prune_mock), \
         patch.object(bellows, "_rotate_logs", rotate_mock):
        result = bellows._maybe_run_hygiene({}, last, now, interval)
    assert result == last
    assert prune_mock.call_count == 0
    assert rotate_mock.call_count == 0


def test_hygiene_runs_after_interval():
    """After the interval elapses, both callees fire and timestamp advances."""
    prune_mock = MagicMock()
    rotate_mock = MagicMock()
    last = 1000.0
    interval = 6 * 3600
    now = last + interval  # exactly at interval
    with patch.object(bellows, "_prune_old_logs", prune_mock), \
         patch.object(bellows, "_rotate_logs", rotate_mock):
        result = bellows._maybe_run_hygiene({}, last, now, interval)
    assert result == now
    assert prune_mock.call_count == 1
    assert rotate_mock.call_count == 1


def test_hygiene_tick_prunes_old_log(tmp_path):
    """Integration: the hygiene helper reaches the real prune and deletes old logs."""
    logs_dir = tmp_path / "logs"
    logs_dir.mkdir()

    old = logs_dir / "step-ancient.json"
    old.write_text("{}")
    cutoff_mtime = time.time() - 31 * 86400
    os.utime(old, (cutoff_mtime, cutoff_mtime))

    fresh = logs_dir / "step-recent.json"
    fresh.write_text("{}")

    interval = 6 * 3600
    with patch.object(bellows, "BELLOWS_ROOT", tmp_path), \
         patch.object(bellows, "_log"):
        bellows._maybe_run_hygiene(
            {"log_retention_days": 30},
            last_hygiene=0.0, now=interval + 1, interval=interval,
        )

    assert not old.exists()
    assert fresh.exists()


def test_hygiene_swallows_callee_error():
    """A callee error must not propagate — the run loop has no guard."""
    log_mock = MagicMock()
    interval = 6 * 3600
    now = interval + 1
    with patch.object(bellows, "_prune_old_logs", side_effect=RuntimeError("boom")), \
         patch.object(bellows, "_log", log_mock):
        result = bellows._maybe_run_hygiene({}, last_hygiene=0.0, now=now, interval=interval)
    assert result == now
    warn_calls = [c for c in log_mock.call_args_list if c[0][0] == "WARN"]
    assert len(warn_calls) >= 1
