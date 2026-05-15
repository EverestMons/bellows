"""Tests for _scan_misplaced_verdicts directory validator."""
import os
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import bellows


def _make_config():
    return {
        "watched_projects": [],
        "default_model": "claude-sonnet-4-6",
        "pushover": {"app_key": "test-app", "user_key": "test-user"},
        "callback_port": 5999,
    }


def test_scan_misplaced_verdicts_warns_on_verdict_in_pending(tmp_path, capsys):
    """Misplaced verdict file triggers WARN and Pushover push."""
    bellows._NOTIFIED_MISPLACED.clear()
    pending = tmp_path / "pending"
    pending.mkdir()
    (pending / "verdict-some-slug-step-1.md").write_text("continue\n")

    config = _make_config()
    b = bellows.Bellows(config)

    with patch("bellows.notifier.push", return_value=True) as mock_push:
        b._scan_misplaced_verdicts(pending)

    out = capsys.readouterr().out
    assert "[WARN]" in out
    assert "verdict-some-slug-step-1.md" in out
    assert "expected location: verdicts/resolved/" in out
    mock_push.assert_called_once()
    assert "Bellows — Misplaced Verdict" in mock_push.call_args[0][2]


def test_scan_misplaced_verdicts_ignores_verdict_request_files(tmp_path, capsys):
    """verdict-request- files are legitimate in pending/ and must not trigger WARN."""
    bellows._NOTIFIED_MISPLACED.clear()
    pending = tmp_path / "pending"
    pending.mkdir()
    (pending / "verdict-request-some-slug-step-1.md").write_text("# Verdict Request\n")

    config = _make_config()
    b = bellows.Bellows(config)

    with patch("bellows.notifier.push") as mock_push:
        b._scan_misplaced_verdicts(pending)

    out = capsys.readouterr().out
    assert "[WARN]" not in out
    mock_push.assert_not_called()


def test_scan_misplaced_verdicts_ignores_non_md_files(tmp_path, capsys):
    """Non-.md files must not trigger WARN even if name starts with verdict-."""
    bellows._NOTIFIED_MISPLACED.clear()
    pending = tmp_path / "pending"
    pending.mkdir()
    (pending / "verdict-something.txt").write_text("data")

    config = _make_config()
    b = bellows.Bellows(config)

    with patch("bellows.notifier.push") as mock_push:
        b._scan_misplaced_verdicts(pending)

    out = capsys.readouterr().out
    assert "[WARN]" not in out
    mock_push.assert_not_called()


def test_scan_misplaced_verdicts_pushover_deduped_per_file(tmp_path, capsys):
    """Second scan of same misplaced file must not re-push."""
    bellows._NOTIFIED_MISPLACED.clear()
    pending = tmp_path / "pending"
    pending.mkdir()
    (pending / "verdict-dedup-test-step-1.md").write_text("continue\n")

    config = _make_config()
    b = bellows.Bellows(config)

    with patch("bellows.notifier.push", return_value=True) as mock_push:
        b._scan_misplaced_verdicts(pending)
        b._scan_misplaced_verdicts(pending)

    assert mock_push.call_count == 1


def test_scan_misplaced_verdicts_pushover_failure_swallowed(tmp_path, capsys):
    """Pushover failure must not propagate; WARN still fires."""
    bellows._NOTIFIED_MISPLACED.clear()
    pending = tmp_path / "pending"
    pending.mkdir()
    (pending / "verdict-fail-push-step-1.md").write_text("continue\n")

    config = _make_config()
    b = bellows.Bellows(config)

    with patch("bellows.notifier.push", side_effect=RuntimeError("push failed")):
        b._scan_misplaced_verdicts(pending)

    out = capsys.readouterr().out
    assert "[WARN]" in out
    assert "verdict-fail-push-step-1.md" in out


def test_scan_misplaced_verdicts_invoked_from_consume_verdicts(tmp_path, capsys):
    """_consume_verdicts must invoke _scan_misplaced_verdicts."""
    bellows._NOTIFIED_MISPLACED.clear()
    pending = tmp_path / "verdicts" / "pending"
    pending.mkdir(parents=True)
    resolved = tmp_path / "verdicts" / "resolved"
    resolved.mkdir(parents=True)
    (pending / "verdict-integration-test-step-1.md").write_text("continue\n")

    config = _make_config()
    b = bellows.Bellows(config)

    with patch("bellows.BELLOWS_ROOT", tmp_path), \
         patch("bellows.notifier.push", return_value=True) as mock_push:
        b._consume_verdicts()

    out = capsys.readouterr().out
    assert "[WARN]" in out
    assert "verdict-integration-test-step-1.md" in out
    mock_push.assert_called_once()


def test_scan_misplaced_verdicts_empty_pending_directory(tmp_path, capsys):
    """Empty pending directory: no warnings, no pushes, no errors."""
    bellows._NOTIFIED_MISPLACED.clear()
    pending = tmp_path / "pending"
    pending.mkdir()

    config = _make_config()
    b = bellows.Bellows(config)

    with patch("bellows.notifier.push") as mock_push:
        b._scan_misplaced_verdicts(pending)

    out = capsys.readouterr().out
    assert "[WARN]" not in out
    mock_push.assert_not_called()
