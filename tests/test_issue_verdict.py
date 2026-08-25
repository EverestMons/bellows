"""Tests for tools/issue_verdict.py and the daemon verdict-detector arms (B2/B3)."""
import os
import sys
from io import StringIO
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

TOOLS_DIR = Path(__file__).resolve().parent.parent / "tools"
sys.path.insert(0, str(TOOLS_DIR.parent))

import tools.issue_verdict as iv


@pytest.fixture(autouse=True)
def _isolate_tool(monkeypatch, tmp_path):
    """Redirect the tool's default dirs to tmp_path so no live files are touched."""
    monkeypatch.setattr(iv, "_DEFAULT_PENDING", tmp_path / "pending")
    monkeypatch.setattr(iv, "_DEFAULT_RESOLVED", tmp_path / "resolved")
    (tmp_path / "pending").mkdir()
    (tmp_path / "resolved").mkdir()
    yield


def _request(tmp_path, slug="999", step=1):
    """Create a verdict-request file in pending/."""
    fname = f"verdict-request-{slug}-step-{step}.md"
    (tmp_path / "pending" / fname).write_text("# Verdict Request\n")
    return fname


# ---------- Test 1: happy path ----------

def test_happy_path_continue(tmp_path):
    _request(tmp_path)
    with pytest.raises(SystemExit) as exc:
        iv.issue_verdict("999", 1, "continue", "looks good",
                         pending_dir=str(tmp_path / "pending"),
                         resolved_dir=str(tmp_path / "resolved"))
    assert exc.value.code == 0
    result = (tmp_path / "resolved" / "verdict-999-step-1.md").read_text()
    assert result.startswith("continue\n")
    assert "looks good" in result


def test_happy_path_stop(tmp_path):
    _request(tmp_path)
    with pytest.raises(SystemExit) as exc:
        iv.issue_verdict("999", 1, "stop", "blocking issue found",
                         pending_dir=str(tmp_path / "pending"),
                         resolved_dir=str(tmp_path / "resolved"))
    assert exc.value.code == 0
    result = (tmp_path / "resolved" / "verdict-999-step-1.md").read_text()
    assert result.startswith("stop\n")
    assert "blocking issue found" in result


# ---------- Test 2: id derivation + normalization ----------

def test_slug_normalization_executable_prefix(tmp_path):
    _request(tmp_path, slug="999")
    with pytest.raises(SystemExit) as exc:
        iv.issue_verdict("executable-999", 1, "continue", "normalized",
                         pending_dir=str(tmp_path / "pending"),
                         resolved_dir=str(tmp_path / "resolved"))
    assert exc.value.code == 0
    assert (tmp_path / "resolved" / "verdict-999-step-1.md").exists()


def test_slug_normalization_diagnostic_prefix(tmp_path):
    _request(tmp_path, slug="999")
    with pytest.raises(SystemExit) as exc:
        iv.issue_verdict("diagnostic-999", 1, "continue", "normalized",
                         pending_dir=str(tmp_path / "pending"),
                         resolved_dir=str(tmp_path / "resolved"))
    assert exc.value.code == 0
    assert (tmp_path / "resolved" / "verdict-999-step-1.md").exists()


# ---------- Test 3: zero-match refusal ----------

def test_zero_match_refusal(tmp_path):
    with pytest.raises(SystemExit) as exc:
        iv.issue_verdict("nonexistent", 1, "continue", "reason",
                         pending_dir=str(tmp_path / "pending"),
                         resolved_dir=str(tmp_path / "resolved"))
    assert exc.value.code == 1


def test_zero_match_refusal_lists_available(tmp_path, capsys):
    _request(tmp_path, slug="other-plan", step=2)
    with pytest.raises(SystemExit) as exc:
        iv.issue_verdict("nonexistent", 1, "continue", "reason",
                         pending_dir=str(tmp_path / "pending"),
                         resolved_dir=str(tmp_path / "resolved"))
    assert exc.value.code == 1
    err = capsys.readouterr().err
    assert "verdict-request-other-plan-step-2.md" in err


# ---------- Test 4 (replaced): unique resolution ----------

def test_unique_resolution_two_requests_same_step(tmp_path):
    """Two requests paused at the same step; the arg resolves exactly one."""
    _request(tmp_path, slug="alpha", step=1)
    _request(tmp_path, slug="beta", step=1)
    with pytest.raises(SystemExit) as exc:
        iv.issue_verdict("alpha", 1, "continue", "resolves alpha only",
                         pending_dir=str(tmp_path / "pending"),
                         resolved_dir=str(tmp_path / "resolved"))
    assert exc.value.code == 0
    assert (tmp_path / "resolved" / "verdict-alpha-step-1.md").exists()
    assert not (tmp_path / "resolved" / "verdict-beta-step-1.md").exists()


# ---------- Test 5: enum refusal ----------

def test_enum_refusal_invalid_outcome(tmp_path, capsys):
    _request(tmp_path)
    with pytest.raises(SystemExit) as exc:
        iv.issue_verdict("999", 1, "maybe", "unsure",
                         pending_dir=str(tmp_path / "pending"),
                         resolved_dir=str(tmp_path / "resolved"))
    assert exc.value.code == 1
    err = capsys.readouterr().err
    assert "continue" in err
    assert "stop" in err


def test_enum_case_insensitive(tmp_path):
    _request(tmp_path)
    with pytest.raises(SystemExit) as exc:
        iv.issue_verdict("999", 1, "CONTINUE", "uppercase ok",
                         pending_dir=str(tmp_path / "pending"),
                         resolved_dir=str(tmp_path / "resolved"))
    assert exc.value.code == 0
    content = (tmp_path / "resolved" / "verdict-999-step-1.md").read_text()
    assert content.startswith("continue\n")


# ---------- Test 6: overwrite refusal ----------

def test_overwrite_refusal(tmp_path, capsys):
    _request(tmp_path)
    (tmp_path / "resolved" / "verdict-999-step-1.md").write_text("continue\n\nold\n")
    with pytest.raises(SystemExit) as exc:
        iv.issue_verdict("999", 1, "stop", "new reason",
                         pending_dir=str(tmp_path / "pending"),
                         resolved_dir=str(tmp_path / "resolved"))
    assert exc.value.code == 1
    err = capsys.readouterr().err
    assert "already exists" in err
    content = (tmp_path / "resolved" / "verdict-999-step-1.md").read_text()
    assert content.startswith("continue\n")


# ---------- Test 7: --force ----------

def test_force_overwrite(tmp_path):
    _request(tmp_path)
    (tmp_path / "resolved" / "verdict-999-step-1.md").write_text("continue\n\nold\n")
    with pytest.raises(SystemExit) as exc:
        iv.issue_verdict("999", 1, "stop", "forced new reason", force=True,
                         pending_dir=str(tmp_path / "pending"),
                         resolved_dir=str(tmp_path / "resolved"))
    assert exc.value.code == 0
    content = (tmp_path / "resolved" / "verdict-999-step-1.md").read_text()
    assert content.startswith("stop\n")
    assert "forced new reason" in content


# ---------- Test 8: atomicity ----------

def test_atomicity_no_tmp_remnant_on_success(tmp_path):
    _request(tmp_path)
    with pytest.raises(SystemExit):
        iv.issue_verdict("999", 1, "continue", "clean write",
                         pending_dir=str(tmp_path / "pending"),
                         resolved_dir=str(tmp_path / "resolved"))
    resolved = tmp_path / "resolved"
    tmp_files = [f for f in os.listdir(resolved) if f.endswith(".tmp")]
    assert tmp_files == []


def test_atomicity_failure_leaves_nothing(tmp_path):
    _request(tmp_path)
    with patch("tools.issue_verdict.tempfile.NamedTemporaryFile", side_effect=OSError("disk full")):
        with pytest.raises(SystemExit) as exc:
            iv.issue_verdict("999", 1, "continue", "will fail",
                             pending_dir=str(tmp_path / "pending"),
                             resolved_dir=str(tmp_path / "resolved"))
    assert exc.value.code == 1
    assert not (tmp_path / "resolved" / "verdict-999-step-1.md").exists()
    tmp_files = [f for f in os.listdir(tmp_path / "resolved") if f.endswith(".tmp")]
    assert tmp_files == []


# ---------- Test 9: self-verify parity with check_verdict ----------

def test_self_verify_parity(tmp_path):
    import verdict
    _request(tmp_path)
    with pytest.raises(SystemExit) as exc:
        iv.issue_verdict("999", 1, "continue", "parity check",
                         pending_dir=str(tmp_path / "pending"),
                         resolved_dir=str(tmp_path / "resolved"))
    assert exc.value.code == 0
    written = (tmp_path / "resolved" / "verdict-999-step-1.md").read_text()
    first_line = written.strip().splitlines()[0].strip()
    assert verdict.VERDICT_FIRST_LINE_RE.match(first_line)
    old_verdicts_dir = verdict.VERDICTS_DIR
    try:
        verdict.VERDICTS_DIR = tmp_path
        result = verdict.check_verdict("999", 1)
    finally:
        verdict.VERDICTS_DIR = old_verdicts_dir
    assert result["found"] is True
    assert result["verdict"] == "continue"


# ---------- Test 10: regex byte-identity ----------

def test_regex_byte_identity(tmp_path):
    import verdict
    assert iv._VERDICT_RE.pattern == verdict.VERDICT_FIRST_LINE_RE.pattern
    assert iv._VERDICT_RE.flags == verdict.VERDICT_FIRST_LINE_RE.flags


# ---------- Test 11: reason sources ----------

def test_reason_via_flag(tmp_path):
    _request(tmp_path)
    with pytest.raises(SystemExit) as exc:
        iv.issue_verdict("999", 1, "continue", "inline reason",
                         pending_dir=str(tmp_path / "pending"),
                         resolved_dir=str(tmp_path / "resolved"))
    assert exc.value.code == 0
    content = (tmp_path / "resolved" / "verdict-999-step-1.md").read_text()
    assert "inline reason" in content


def test_reason_via_file(tmp_path):
    _request(tmp_path)
    reason_file = tmp_path / "reason.txt"
    reason_file.write_text("reason from file")
    with pytest.raises(SystemExit) as exc:
        iv.issue_verdict("999", 1, "continue", reason_file.read_text(),
                         pending_dir=str(tmp_path / "pending"),
                         resolved_dir=str(tmp_path / "resolved"))
    assert exc.value.code == 0
    content = (tmp_path / "resolved" / "verdict-999-step-1.md").read_text()
    assert "reason from file" in content


def test_empty_reason_refused(tmp_path):
    _request(tmp_path)
    with pytest.raises(SystemExit) as exc:
        iv.issue_verdict("999", 1, "continue", "   ",
                         pending_dir=str(tmp_path / "pending"),
                         resolved_dir=str(tmp_path / "resolved"))
    assert exc.value.code == 1


# ---------- Test 12: processed- collision ----------

def test_processed_collision_warns_but_proceeds(tmp_path, capsys):
    _request(tmp_path)
    (tmp_path / "resolved" / "processed-verdict-999-step-1.md").write_text("continue\n\nold\n")
    with pytest.raises(SystemExit) as exc:
        iv.issue_verdict("999", 1, "continue", "new verdict",
                         pending_dir=str(tmp_path / "pending"),
                         resolved_dir=str(tmp_path / "resolved"))
    assert exc.value.code == 0
    err = capsys.readouterr().err
    assert "prior consumed verdict exists" in err
    assert (tmp_path / "resolved" / "verdict-999-step-1.md").exists()


# ---------- Test: explicitly-passed nonexistent dir refused ----------

def test_nonexistent_pending_dir_refused(tmp_path):
    with pytest.raises(SystemExit) as exc:
        iv.issue_verdict("999", 1, "continue", "reason",
                         pending_dir=str(tmp_path / "nope"),
                         resolved_dir=str(tmp_path / "resolved"))
    assert exc.value.code == 1


def test_nonexistent_resolved_dir_refused(tmp_path):
    with pytest.raises(SystemExit) as exc:
        iv.issue_verdict("999", 1, "continue", "reason",
                         pending_dir=str(tmp_path / "pending"),
                         resolved_dir=str(tmp_path / "nope"))
    assert exc.value.code == 1


# ---------- Test: race arm — consumed during self-verify ----------

def test_race_arm_consumed_during_verify(tmp_path, capsys):
    _request(tmp_path)
    target = tmp_path / "resolved" / "verdict-999-step-1.md"
    processed = tmp_path / "resolved" / "processed-verdict-999-step-1.md"
    original_read_text = Path.read_text

    def _mock_read_text(self, *args, **kwargs):
        if self == target and not processed.exists():
            os.rename(str(target), str(processed))
            raise FileNotFoundError(str(target))
        return original_read_text(self, *args, **kwargs)

    with patch.object(Path, "read_text", _mock_read_text):
        with pytest.raises(SystemExit) as exc:
            iv.issue_verdict("999", 1, "continue", "race test",
                             pending_dir=str(tmp_path / "pending"),
                             resolved_dir=str(tmp_path / "resolved"))
    assert exc.value.code == 0
    out = capsys.readouterr().out
    assert "consumed by the daemon during self-verify" in out


# ==================== Daemon tests ====================

import bellows


def _make_config():
    return {
        "watched_projects": [],
        "default_model": "claude-sonnet-4-6",
        "pushover": {"app_key": "test-app", "user_key": "test-user"},
        "callback_port": 5999,
    }


# ---------- Test 13: auto-move moves parse-valid + EVENT logged ----------

def test_auto_move_parse_valid(tmp_path, capsys):
    bellows._NOTIFIED_MISPLACED.clear()
    pending = tmp_path / "pending"
    pending.mkdir(exist_ok=True)
    resolved = tmp_path / "resolved"
    resolved.mkdir(exist_ok=True)
    (pending / "verdict-999-step-1.md").write_text("continue\n\nlooks good\n")
    (pending / "verdict-request-999-step-1.md").write_text("# Verdict Request\n")

    config = _make_config()
    b = bellows.Bellows(config)

    with patch("bellows.notifier.push") as mock_push, \
         patch("bellows.verdict.VERDICTS_DIR", tmp_path):
        b._scan_misplaced_verdicts(pending)

    assert (resolved / "verdict-999-step-1.md").exists()
    assert not (pending / "verdict-999-step-1.md").exists()
    out = capsys.readouterr().out
    assert "[EVENT]" in out
    assert "auto-moved well-formed verdict to resolved/" in out
    mock_push.assert_not_called()


# ---------- Test 13b: stale duplicate NOT moved ----------

def test_stale_duplicate_not_moved(tmp_path, capsys):
    """No matching pending request → condition (iv) fails → WARN, NOT moved."""
    bellows._NOTIFIED_MISPLACED.clear()
    pending = tmp_path / "pending"
    pending.mkdir(exist_ok=True)
    resolved = tmp_path / "resolved"
    resolved.mkdir(exist_ok=True)
    (pending / "verdict-999-step-1.md").write_text("continue\n\nstale\n")

    config = _make_config()
    b = bellows.Bellows(config)

    with patch("bellows.notifier.push", return_value=True) as mock_push, \
         patch("bellows.verdict.VERDICTS_DIR", tmp_path):
        b._scan_misplaced_verdicts(pending)

    assert (pending / "verdict-999-step-1.md").exists()
    assert not (resolved / "verdict-999-step-1.md").exists()
    out = capsys.readouterr().out
    assert "[WARN]" in out
    assert "verdict file in wrong directory" in out


# ---------- Test 14: parse-invalid NOT moved + WARN persists ----------

def test_parse_invalid_not_moved(tmp_path, capsys):
    bellows._NOTIFIED_MISPLACED.clear()
    pending = tmp_path / "pending"
    pending.mkdir(exist_ok=True)
    resolved = tmp_path / "resolved"
    resolved.mkdir(exist_ok=True)
    (pending / "verdict-999-step-1.md").write_text("garbage not a verdict\n")
    (pending / "verdict-request-999-step-1.md").write_text("# Verdict Request\n")

    config = _make_config()
    b = bellows.Bellows(config)

    with patch("bellows.notifier.push", return_value=True) as mock_push, \
         patch("bellows.verdict.VERDICTS_DIR", tmp_path):
        b._scan_misplaced_verdicts(pending)

    assert (pending / "verdict-999-step-1.md").exists()
    assert not (resolved / "verdict-999-step-1.md").exists()
    out = capsys.readouterr().out
    assert "[WARN]" in out
    mock_push.assert_called_once()


# ---------- Test 15: malformed WARN with first-line content ----------

def test_malformed_warn_with_first_line(tmp_path, capsys):
    """B3: verdict file exists in resolved/ but doesn't parse — WARN includes first line."""
    bellows._NOTIFIED_MISPLACED.clear()
    pending = tmp_path / "verdicts" / "pending"
    pending.mkdir(parents=True)
    resolved = tmp_path / "verdicts" / "resolved"
    resolved.mkdir(parents=True)
    (resolved / "verdict-999-step-1.md").write_text("garbage not a verdict\n")

    config = _make_config()
    b = bellows.Bellows(config)

    import verdict
    with patch("bellows.BELLOWS_ROOT", tmp_path), \
         patch("bellows.verdict.VERDICTS_DIR", tmp_path / "verdicts"), \
         patch("bellows.notifier.push", return_value=True):
        b._consume_verdicts()

    out = capsys.readouterr().out
    assert "verdict file exists but does not parse as a verdict" in out
    assert "garbage not a verdict" in out


# ---------- Test 13 variant: auto-move with prefix normalization ----------

def test_auto_move_with_prefix_normalization(tmp_path, capsys):
    """Candidate filename has executable- prefix; request uses normalized slug."""
    bellows._NOTIFIED_MISPLACED.clear()
    pending = tmp_path / "pending"
    pending.mkdir(exist_ok=True)
    resolved = tmp_path / "resolved"
    resolved.mkdir(exist_ok=True)
    (pending / "verdict-executable-999-step-1.md").write_text("stop\n\nreason\n")
    (pending / "verdict-request-999-step-1.md").write_text("# Verdict Request\n")

    config = _make_config()
    b = bellows.Bellows(config)

    with patch("bellows.notifier.push") as mock_push, \
         patch("bellows.verdict.VERDICTS_DIR", tmp_path):
        b._scan_misplaced_verdicts(pending)

    assert (resolved / "verdict-executable-999-step-1.md").exists()
    assert not (pending / "verdict-executable-999-step-1.md").exists()
    out = capsys.readouterr().out
    assert "[EVENT]" in out
    assert "auto-moved" in out
