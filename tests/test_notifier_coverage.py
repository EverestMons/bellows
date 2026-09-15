"""Tests for the notifier coverage plan (100054).

Verifies: defaults table, ownership signal, dedupe, notify_event gate,
three new notifiers, their call sites, the liveness poll, and the gate watcher.
"""

import glob as _glob
import json
import os
import subprocess
import sys
import time
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch, call

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

import notifier
import depositor
import bellows


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def reset_notifier_state():
    """Reset module-level notifier state between tests."""
    notifier._dedupe_memo.clear()
    notifier.init_notifications({
        "pushover": {"app_key": "testkey", "user_key": "testuser"},
        "notifications": {"enabled": True, "events": {}},
    })
    yield
    notifier._dedupe_memo.clear()


# ---------------------------------------------------------------------------
# Test 0: Binding — notifier and depositor resolve from the worktree
# ---------------------------------------------------------------------------

def test_0_binding():
    assert notifier.__file__.startswith(str(REPO_ROOT)), (
        f"notifier binds to {notifier.__file__!r}, not under {REPO_ROOT}"
    )
    assert depositor.__file__.startswith(str(REPO_ROOT)), (
        f"depositor binds to {depositor.__file__!r}, not under {REPO_ROOT}"
    )


# ---------------------------------------------------------------------------
# Test 1: Defaults table
# ---------------------------------------------------------------------------

def test_1_defaults_table():
    notifier.init_notifications({
        "pushover": {"app_key": "k", "user_key": "u"},
        "notifications": {"enabled": True, "events": {}},
    })
    for e in ("verdict_needed", "plan_halted", "failure", "disk_low",
              "class_hold", "checkout_stale", "watcher_down"):
        assert notifier._event_enabled(e) is True, f"{e} should be True by default"
    for e in ("plan_complete", "plan_skipped", "queue_empty", "cycle_nudge"):
        assert notifier._event_enabled(e) is False, f"{e} should be False by default"
    assert notifier._event_enabled("no_such_event") is False, "unknown event should be False"

    # Config override: turn on plan_complete
    notifier.init_notifications({
        "pushover": {"app_key": "k", "user_key": "u"},
        "notifications": {"enabled": True, "events": {"plan_complete": True}},
    })
    assert notifier._event_enabled("plan_complete") is True


# ---------------------------------------------------------------------------
# Test 2: notify_event refusals
# ---------------------------------------------------------------------------

def test_2_notify_event_refusals():
    push_calls = []

    def record_push(*a, **kw):
        push_calls.append((a, kw))
        return True

    # disabled — notifications.enabled: false
    notifier.init_notifications({
        "pushover": {"app_key": "k", "user_key": "u"},
        "notifications": {"enabled": False},
    })
    with patch.object(notifier, "push", side_effect=record_push):
        result = notifier.notify_event("verdict_needed", "p", "T", "M")
    assert result is False
    assert len(push_calls) == 0

    # event off — plan_complete defaults to False
    notifier.init_notifications({
        "pushover": {"app_key": "k", "user_key": "u"},
        "notifications": {"enabled": True, "events": {}},
    })
    with patch.object(notifier, "push", side_effect=record_push):
        result = notifier.notify_event("plan_complete", "p", "T", "M")
    assert result is False
    assert len(push_calls) == 0


# ---------------------------------------------------------------------------
# Test 3: Dedupe
# ---------------------------------------------------------------------------

def test_3_dedupe(monkeypatch):
    push_calls = []
    monkeypatch.setattr(notifier, "push", lambda *a, **kw: push_calls.append(1) or True)

    notifier.init_notifications({
        "pushover": {"app_key": "k", "user_key": "u"},
        "notifications": {"enabled": True, "events": {}, "dedupe_window_seconds": 3600},
    })

    # Two calls with same (event, plan) → only one push
    notifier.notify_event("failure", "p", "T", "M", plan_scoped=False)
    notifier.notify_event("failure", "p", "T", "M", plan_scoped=False)
    assert len(push_calls) == 1

    # After the window → second push
    original_time = time.time
    monkeypatch.setattr(time, "time", lambda: original_time() + 3601)
    notifier.notify_event("failure", "p", "T", "M", plan_scoped=False)
    monkeypatch.setattr(time, "time", original_time)
    assert len(push_calls) == 2

    # Different plan → its own push
    notifier.notify_event("failure", "q", "T", "M", plan_scoped=False)
    assert len(push_calls) == 3

    # Different event → its own push
    notifier.notify_event("verdict_needed", "p", "T", "M", plan_scoped=False)
    assert len(push_calls) == 4


# ---------------------------------------------------------------------------
# Test 4: Ownership: attended session → page suppressed
# ---------------------------------------------------------------------------

def test_4_ownership_attended(tmp_path, monkeypatch):
    receipts_dir = tmp_path / "receipts"
    receipts_dir.mkdir()
    sid = "abcdef1234567890"
    slug = "executable-foo-2026-09-09"

    # Write receipt
    receipt = {"slug": slug, "session_id": sid, "armed_at": "2026-09-09T00:00:00"}
    (receipts_dir / f"receipt-{slug}-{sid}-abc123456789.json").write_text(json.dumps(receipt))

    # Write fresh transcript
    projects_dir = tmp_path / "home" / ".claude" / "projects" / "proj"
    projects_dir.mkdir(parents=True)
    transcript = projects_dir / f"{sid}.jsonl"
    transcript.write_text('{"role":"assistant","content":"hi"}\n')

    monkeypatch.setenv("HOME", str(tmp_path / "home"))

    notifier.init_notifications({
        "pushover": {"app_key": "k", "user_key": "u"},
        "notifications": {"enabled": True, "events": {}, "attended_window_seconds": 600},
    })

    # owned_by_live_session should return (True, ...)
    owned, why = notifier.owned_by_live_session(slug, receipts_dir=receipts_dir)
    assert owned is True
    assert sid[:8] in why
    age_str = why.split("transcript ")[-1].split("s old")[0]
    assert int(age_str) < 600

    # notify_event with plan_scoped=True should NOT push when session is attended.
    # Patch owned_by_live_session to return attended so notify_event uses the right receipts_dir.
    push_calls = []
    monkeypatch.setattr(notifier, "push", lambda *a, **kw: push_calls.append(1) or True)
    with patch.object(notifier, "owned_by_live_session",
                      return_value=(True, f"owned by session {sid[:8]} — transcript 5s old")):
        result = notifier.notify_event("verdict_needed", slug, "T", "M",
                                       plan_scoped=True, detail_key="1")
    assert result is False
    assert len(push_calls) == 0


# ---------------------------------------------------------------------------
# Test 5: Ownership: unattended → push sent; newest receipt wins
# ---------------------------------------------------------------------------

def test_5_ownership_unattended(tmp_path, monkeypatch):
    receipts_dir = tmp_path / "receipts"
    receipts_dir.mkdir()
    sid = "aaaa111122223333"
    slug = "executable-bar-2026-09-09"

    receipt = {"slug": slug, "session_id": sid, "armed_at": "2026-09-09T00:00:00"}
    receipt_file = receipts_dir / f"receipt-{slug}-{sid}-deadbeef0000.json"
    receipt_file.write_text(json.dumps(receipt))

    # Write transcript but set mtime to 900s ago
    projects_dir = tmp_path / "home" / ".claude" / "projects" / "proj"
    projects_dir.mkdir(parents=True)
    transcript = projects_dir / f"{sid}.jsonl"
    transcript.write_text('{"role":"assistant"}\n')
    old_time = time.time() - 900
    os.utime(str(transcript), (old_time, old_time))

    monkeypatch.setenv("HOME", str(tmp_path / "home"))

    notifier.init_notifications({
        "pushover": {"app_key": "k", "user_key": "u"},
        "notifications": {"enabled": True, "events": {}, "attended_window_seconds": 600},
    })

    owned, why = notifier.owned_by_live_session(slug, receipts_dir=receipts_dir)
    assert owned is False
    assert "900" in why or "transcript" in why

    # notify_event should push (not owned)
    push_calls = []
    monkeypatch.setattr(notifier, "push", lambda *a, **kw: push_calls.append(1) or True)
    notifier.notify_event("verdict_needed", slug, "T", "M",
                          plan_scoped=True, detail_key="1")
    assert len(push_calls) == 1

    # Newest receipt wins — write an older receipt with a different (bad) sid
    old_sid = "bbbb999988887777"
    old_receipt = {"slug": slug, "session_id": old_sid, "armed_at": "2020-01-01T00:00:00"}
    old_file = receipts_dir / f"receipt-{slug}-{old_sid}-000000000000.json"
    old_file.write_text(json.dumps(old_receipt))
    # Make old_file older
    older = time.time() - 9999
    os.utime(str(old_file), (older, older))

    # Re-derive: newest is still our receipt_file
    owned2, why2 = notifier.owned_by_live_session(slug, receipts_dir=receipts_dir)
    # still unattended (transcript old)
    assert owned2 is False


# ---------------------------------------------------------------------------
# Test 6: Ownership failures → page (silence is never the failure mode)
# ---------------------------------------------------------------------------

def test_6_ownership_absent_or_broken_pages(tmp_path, monkeypatch):
    receipts_dir = tmp_path / "receipts"
    receipts_dir.mkdir()
    sid = "cccc000011112222"
    slug = "executable-baz-2026-09-09"
    monkeypatch.setenv("HOME", str(tmp_path / "home"))

    notifier.init_notifications({
        "pushover": {"app_key": "k", "user_key": "u"},
        "notifications": {"enabled": True, "events": {}},
    })

    # Case A: no receipt → (False, "no receipt")
    owned, why = notifier.owned_by_live_session(slug, receipts_dir=receipts_dir)
    assert owned is False
    assert "receipt" in why.lower()

    # Case B: receipt without a transcript
    receipt = {"slug": slug, "session_id": sid, "armed_at": "2026-09-09T00:00:00"}
    receipt_file = receipts_dir / f"receipt-{slug}-{sid}-baz000000000.json"
    receipt_file.write_text(json.dumps(receipt))
    owned, why = notifier.owned_by_live_session(slug, receipts_dir=receipts_dir)
    assert owned is False
    assert "transcript" in why.lower()

    # Case C: receipt file that is not JSON
    receipt_file.write_text("this is not json{{{")
    owned, why = notifier.owned_by_live_session(slug, receipts_dir=receipts_dir)
    assert owned is False
    assert "ownership check failed" in why.lower()

    # Each case pages — verify push is called for notify_event
    push_calls = []
    monkeypatch.setattr(notifier, "push", lambda *a, **kw: push_calls.append(1) or True)

    receipt_file.unlink()  # no receipt
    notifier.notify_event("verdict_needed", slug, "T", "M", plan_scoped=True, detail_key="1")
    assert len(push_calls) == 1

    receipt_file.write_text(json.dumps(receipt))
    notifier._dedupe_memo.clear()
    notifier.notify_event("verdict_needed", slug, "T", "M", plan_scoped=True, detail_key="1")
    assert len(push_calls) == 2  # no transcript → push


# ---------------------------------------------------------------------------
# Tests 6a–6e: receipt_key routes the ownership check to the deposit's slug
# ---------------------------------------------------------------------------

def test_6a_receipt_key_attended_suppresses_page(tmp_path, monkeypatch):
    """6a: receipt_key=stem + id as plan_slug → owned receipt → no push; INFO log carries id."""
    stem = "executable-foo-2026-09-14"
    plan_id = "100112"
    sid = "aabbccdd11223344"
    hash12 = "aabbccddeeff"

    receipts_dir = tmp_path / "receipts"
    receipts_dir.mkdir()
    (receipts_dir / f"receipt-{stem}-{sid}-{hash12}.json").write_text(
        json.dumps({"slug": stem, "session_id": sid, "armed_at": "2026-09-14T00:00:00"})
    )

    home = tmp_path / "home"
    (home / ".claude" / "projects" / "proj").mkdir(parents=True)
    (home / ".claude" / "projects" / "proj" / f"{sid}.jsonl").write_text('{"role":"assistant"}\n')
    monkeypatch.setenv("HOME", str(home))

    notifier.init_notifications({
        "pushover": {"app_key": "k", "user_key": "u"},
        "notifications": {"enabled": True, "events": {}},
    })
    push_calls = []
    log_lines = []
    monkeypatch.setattr(notifier, "push", lambda *a, **kw: push_calls.append(1) or True)
    monkeypatch.setattr(notifier, "_log", lambda lvl, msg, **kw: log_lines.append((lvl, msg)))

    with patch("bellows_root.resolve_bellows_root", return_value=tmp_path):
        notifier.notify_event("verdict_needed", plan_id, "T", "M",
                              plan_scoped=True, detail_key="1", receipt_key=stem)

    assert len(push_calls) == 0
    info = [m for lvl, m in log_lines if lvl == "INFO"]
    assert any("not paged" in m and "owned by session" in m for m in info), info
    assert any(plan_id in m for m in info), info


def test_6b_no_receipt_key_falls_back_to_id_pages(tmp_path, monkeypatch):
    """6b: no receipt_key → owned_by_live_session(id) → no receipt under id → push; pinned."""
    stem = "executable-foo-2026-09-14"
    plan_id = "100112"
    sid = "aabbccdd11223344"
    hash12 = "aabbccddeeff"

    receipts_dir = tmp_path / "receipts"
    receipts_dir.mkdir()
    (receipts_dir / f"receipt-{stem}-{sid}-{hash12}.json").write_text(
        json.dumps({"slug": stem, "session_id": sid, "armed_at": "2026-09-14T00:00:00"})
    )

    home = tmp_path / "home"
    (home / ".claude" / "projects" / "proj").mkdir(parents=True)
    (home / ".claude" / "projects" / "proj" / f"{sid}.jsonl").write_text('{"role":"assistant"}\n')
    monkeypatch.setenv("HOME", str(home))

    notifier.init_notifications({
        "pushover": {"app_key": "k", "user_key": "u"},
        "notifications": {"enabled": True, "events": {}},
    })
    push_calls = []
    log_lines = []
    monkeypatch.setattr(notifier, "push", lambda *a, **kw: push_calls.append(1) or True)
    monkeypatch.setattr(notifier, "_log", lambda lvl, msg, **kw: log_lines.append((lvl, msg)))

    with patch("bellows_root.resolve_bellows_root", return_value=tmp_path):
        notifier.notify_event("verdict_needed", plan_id, "T", "M",
                              plan_scoped=True, detail_key="1")

    assert len(push_calls) == 1
    info = [m for lvl, m in log_lines if lvl == "INFO"]
    assert any("verdict_needed" in m and plan_id in m and "paged" in m and "not paged" not in m for m in info), info


def test_6c_neighbour_receipt_slug_mismatch_pages(tmp_path, monkeypatch):
    """6c: only a <stem>-2 receipt; JSON slug ≠ stem → no matching slug → push."""
    stem = "executable-foo-2026-09-14"
    stem2 = f"{stem}-2"
    plan_id = "100112"
    sid = "ccccdddd11223344"
    hash12 = "ccddccddccdd"

    receipts_dir = tmp_path / "receipts"
    receipts_dir.mkdir()
    (receipts_dir / f"receipt-{stem2}-{sid}-{hash12}.json").write_text(
        json.dumps({"slug": stem2, "session_id": sid, "armed_at": "2026-09-14T00:00:00"})
    )

    home = tmp_path / "home"
    (home / ".claude" / "projects" / "proj").mkdir(parents=True)
    (home / ".claude" / "projects" / "proj" / f"{sid}.jsonl").write_text('{"role":"assistant"}\n')
    monkeypatch.setenv("HOME", str(home))

    notifier.init_notifications({
        "pushover": {"app_key": "k", "user_key": "u"},
        "notifications": {"enabled": True, "events": {}},
    })
    push_calls = []
    monkeypatch.setattr(notifier, "push", lambda *a, **kw: push_calls.append(1) or True)

    with patch("bellows_root.resolve_bellows_root", return_value=tmp_path):
        notifier.notify_event("verdict_needed", plan_id, "T", "M",
                              plan_scoped=True, detail_key="1", receipt_key=stem)

    assert len(push_calls) == 1


def test_6d_older_attended_receipt_wins_over_newer_neighbour(tmp_path, monkeypatch):
    """6d: older receipt (slug=stem, attended) + newer <stem>-2 receipt → slug filter → owned, no push."""
    stem = "executable-foo-2026-09-14"
    stem2 = f"{stem}-2"
    sid_attended = "aaaabbbb11112222"
    sid_other = "ccccdddd33334444"
    hash1 = "aaaaaaaaaaaa"
    hash2 = "bbbbbbbbbbbb"

    receipts_dir = tmp_path / "receipts"
    receipts_dir.mkdir()

    attended_file = receipts_dir / f"receipt-{stem}-{sid_attended}-{hash1}.json"
    attended_file.write_text(json.dumps({
        "slug": stem, "session_id": sid_attended, "armed_at": "2026-09-14T00:00:00"
    }))
    old_ts = time.time() - 9999
    os.utime(str(attended_file), (old_ts, old_ts))

    (receipts_dir / f"receipt-{stem2}-{sid_other}-{hash2}.json").write_text(
        json.dumps({"slug": stem2, "session_id": sid_other, "armed_at": "2026-09-14T00:00:00"})
    )

    home = tmp_path / "home"
    (home / ".claude" / "projects" / "proj").mkdir(parents=True)
    (home / ".claude" / "projects" / "proj" / f"{sid_attended}.jsonl").write_text('{"role":"assistant"}\n')
    monkeypatch.setenv("HOME", str(home))

    notifier.init_notifications({
        "pushover": {"app_key": "k", "user_key": "u"},
        "notifications": {"enabled": True, "events": {}},
    })
    push_calls = []
    monkeypatch.setattr(notifier, "push", lambda *a, **kw: push_calls.append(1) or True)

    with patch("bellows_root.resolve_bellows_root", return_value=tmp_path):
        notifier.notify_event("verdict_needed", "100112", "T", "M",
                              plan_scoped=True, detail_key="1", receipt_key=stem)

    assert len(push_calls) == 0


@pytest.mark.parametrize("wrapper,kwargs", [
    ("notify_plan_halted",
     {"plan_name": "Plan", "plan_slug": "100112"}),
    ("notify_plan_abandoned",
     {"plan_name": "Plan", "plan_slug": "100112"}),
    ("notify_failure",
     {"app_key": "k", "user_key": "u", "plan_name": "Plan", "step": 1,
      "error": "e", "plan_slug": "100112"}),
    ("notify_verdict_request",
     {"app_key": "k", "user_key": "u", "plan_name": "Plan", "step": 1,
      "gate_failures": [], "plan_slug": "100112"}),
    ("notify_checkout_stale",
     {"plan_slug": "100112", "detail": "stale"}),
])
def test_6e_wrapper_passes_receipt_key_through(wrapper, kwargs, tmp_path, monkeypatch):
    """6e: each plan-scoped wrapper passes receipt_key to notify_event → attended receipt → no push."""
    stem = "executable-foo-2026-09-14"
    sid = "eeeeffff11112222"
    hash12 = "eeeeeeeeffff"

    receipts_dir = tmp_path / "receipts"
    receipts_dir.mkdir()
    (receipts_dir / f"receipt-{stem}-{sid}-{hash12}.json").write_text(
        json.dumps({"slug": stem, "session_id": sid, "armed_at": "2026-09-14T00:00:00"})
    )

    home = tmp_path / "home"
    (home / ".claude" / "projects" / "proj").mkdir(parents=True)
    (home / ".claude" / "projects" / "proj" / f"{sid}.jsonl").write_text('{"role":"assistant"}\n')
    monkeypatch.setenv("HOME", str(home))

    notifier.init_notifications({
        "pushover": {"app_key": "k", "user_key": "u"},
        "notifications": {"enabled": True, "events": {}},
    })
    push_calls = []
    monkeypatch.setattr(notifier, "push", lambda *a, **kw: push_calls.append(1) or True)

    fn = getattr(notifier, wrapper)
    with patch("bellows_root.resolve_bellows_root", return_value=tmp_path):
        fn(**kwargs, receipt_key=stem)

    assert len(push_calls) == 0, f"{wrapper}: expected 0 pushes, got {len(push_calls)}"


# ---------------------------------------------------------------------------
# Test 7: Not plan-scoped skips ownership check → always pages
# ---------------------------------------------------------------------------

def test_7_not_plan_scoped_pages(tmp_path, monkeypatch):
    receipts_dir = tmp_path / "receipts"
    receipts_dir.mkdir()
    sid = "dddd333344445555"
    slug = "executable-qux-2026-09-09"

    # Write attended receipt and transcript
    receipt = {"slug": slug, "session_id": sid, "armed_at": "2026-09-09T00:00:00"}
    (receipts_dir / f"receipt-{slug}-{sid}-abc000000000.json").write_text(json.dumps(receipt))
    projects_dir = tmp_path / "home" / ".claude" / "projects" / "proj"
    projects_dir.mkdir(parents=True)
    transcript = projects_dir / f"{sid}.jsonl"
    transcript.write_text('{"role":"assistant"}\n')
    monkeypatch.setenv("HOME", str(tmp_path / "home"))

    notifier.init_notifications({
        "pushover": {"app_key": "k", "user_key": "u"},
        "notifications": {"enabled": True, "events": {}},
    })

    push_calls = []
    monkeypatch.setattr(notifier, "push", lambda *a, **kw: push_calls.append(1) or True)

    # notify_class_hold — plan_scoped=False → pages even with attended receipt
    with patch.object(notifier, "owned_by_live_session") as mock_own:
        mock_own.return_value = (True, "owned")
        notifier.notify_class_hold(slug, "shop-infra")
        mock_own.assert_not_called()  # ownership never checked for non-scoped
    assert len(push_calls) == 1

    # notify_watcher_down — not plan-scoped
    notifier.notify_watcher_down("air", "stale", 900)
    assert len(push_calls) == 2

    # notify_disk_low — not plan-scoped
    notifier.notify_disk_low(1.2, 5.0)
    assert len(push_calls) == 3


# ---------------------------------------------------------------------------
# Test 8: watcher_down episodes and mark_machine_live
# ---------------------------------------------------------------------------

def test_8_watcher_down_episodes(monkeypatch):
    push_calls = []
    monkeypatch.setattr(notifier, "push", lambda *a, **kw: push_calls.append(1) or True)
    notifier.init_notifications({
        "pushover": {"app_key": "k", "user_key": "u"},
        "notifications": {"enabled": True, "events": {}, "dedupe_window_seconds": 3600},
    })

    # First call → push
    notifier.notify_watcher_down("air", "stale", 300)
    assert len(push_calls) == 1

    # Second call within window → deduped
    notifier.notify_watcher_down("air", "stale", 310)
    assert len(push_calls) == 1

    # mark_machine_live clears the dedupe
    notifier.mark_machine_live("air")
    # New stale episode → push again
    notifier.notify_watcher_down("air", "stale", 320)
    assert len(push_calls) == 2

    # Route check: notify_watcher_down must reach push only through notify_event.
    notify_event_calls = []

    def _capture_notify_event(event, plan_slug, title, message, **kwargs):
        notify_event_calls.append({
            "event": event,
            "plan_slug": plan_slug,
            "plan_scoped": kwargs.get("plan_scoped"),
            "detail_key": kwargs.get("detail_key"),
        })
        return True

    notifier._dedupe_memo.clear()
    monkeypatch.setattr(notifier, "notify_event", _capture_notify_event)
    notifier.notify_watcher_down("air", "stale", 330)
    assert len(notify_event_calls) == 1, (
        f"expected notify_event called once, got {len(notify_event_calls)}"
    )
    assert notify_event_calls[0]["event"] == "watcher_down"
    assert notify_event_calls[0]["plan_scoped"] is False
    assert notify_event_calls[0]["detail_key"] == "air:stale"


# ---------------------------------------------------------------------------
# Tests 8a–8e: per-machine dedupe isolation (watcher_down)
# ---------------------------------------------------------------------------

def test_8a_watcher_down_stale_plus_live_stale_first(monkeypatch):
    """air stale then mini live (stale row first) over two polls → one page."""
    push_calls = []
    monkeypatch.setattr(notifier, "push", lambda *a, **kw: push_calls.append(1) or True)
    notifier.init_notifications({
        "pushover": {"app_key": "k", "user_key": "u"},
        "notifications": {"enabled": True, "events": {}, "dedupe_window_seconds": 3600},
    })

    # Poll 1: stale row first, then live row
    notifier.notify_watcher_down("air", "stale", 300)
    notifier.mark_machine_live("mini")
    # Poll 2: same order
    notifier.notify_watcher_down("air", "stale", 610)
    notifier.mark_machine_live("mini")
    assert len(push_calls) == 1


def test_8b_watcher_down_stale_plus_live_live_first(monkeypatch):
    """mini live then air stale (live row first) over two polls → one page."""
    push_calls = []
    monkeypatch.setattr(notifier, "push", lambda *a, **kw: push_calls.append(1) or True)
    notifier.init_notifications({
        "pushover": {"app_key": "k", "user_key": "u"},
        "notifications": {"enabled": True, "events": {}, "dedupe_window_seconds": 3600},
    })

    # Poll 1: live row first, then stale row
    notifier.mark_machine_live("mini")
    notifier.notify_watcher_down("air", "stale", 300)
    # Poll 2: same order
    notifier.mark_machine_live("mini")
    notifier.notify_watcher_down("air", "stale", 610)
    assert len(push_calls) == 1


def test_8c_watcher_down_two_machines_stale(monkeypatch):
    """air and mini both stale over two polls → two pages (one per machine)."""
    push_calls = []
    monkeypatch.setattr(notifier, "push", lambda *a, **kw: push_calls.append(1) or True)
    notifier.init_notifications({
        "pushover": {"app_key": "k", "user_key": "u"},
        "notifications": {"enabled": True, "events": {}, "dedupe_window_seconds": 3600},
    })

    # Poll 1: both stale
    notifier.notify_watcher_down("air", "stale", 300)
    notifier.notify_watcher_down("mini", "stale", 300)
    # Poll 2: both stale — each deduped by its own key
    notifier.notify_watcher_down("air", "stale", 610)
    notifier.notify_watcher_down("mini", "stale", 610)
    assert len(push_calls) == 2


def test_8d_watcher_down_mark_live_new_episode(monkeypatch):
    """Both stale → 2 pages; mark air live; both stale again → 3 pages (air new, mini deduped)."""
    push_calls = []
    monkeypatch.setattr(notifier, "push", lambda *a, **kw: push_calls.append(1) or True)
    notifier.init_notifications({
        "pushover": {"app_key": "k", "user_key": "u"},
        "notifications": {"enabled": True, "events": {}, "dedupe_window_seconds": 3600},
    })

    # Phase 1: both stale → two pages
    notifier.notify_watcher_down("air", "stale", 300)
    notifier.notify_watcher_down("mini", "stale", 300)
    assert len(push_calls) == 2
    # air goes live → clears air's key only
    notifier.mark_machine_live("air")
    # Phase 2: both stale → air new episode (page 3), mini still deduped
    notifier.notify_watcher_down("air", "stale", 600)
    notifier.notify_watcher_down("mini", "stale", 600)
    assert len(push_calls) == 3


def test_8e_liveness_poll_two_polls_one_page(monkeypatch, tmp_path):
    """_poll_liveness: [air stale, mini live] over two polls (clock reset each) → one page."""
    push_calls = []
    monkeypatch.setattr(notifier, "push", lambda *a, **kw: push_calls.append(1) or True)
    notifier.init_notifications({
        "pushover": {"app_key": "k", "user_key": "u"},
        "notifications": {"enabled": True, "events": {}, "dedupe_window_seconds": 3600},
    })

    liveness_json = json.dumps([
        {"machine": "air", "status": "stale", "age_seconds": 900, "heartbeat_only": True},
        {"machine": "mini", "status": "live", "age_seconds": 10, "heartbeat_only": True},
    ])

    mock_result = MagicMock()
    mock_result.returncode = 0
    mock_result.stdout = liveness_json

    checkout = tmp_path / "tuyere"
    checkout.mkdir()
    (checkout / ".venv" / "bin").mkdir(parents=True)
    (checkout / ".venv" / "bin" / "python").write_text("#!/usr/bin/env python3")

    def mock_run(cmd, **kwargs):
        return mock_result

    with patch("bellows.server.ResponseServer"), \
         patch("bellows.depositor.Depositor"), \
         patch("bellows.plan_claim._tuyere_checkout", return_value=checkout), \
         patch("bellows.subprocess.run", side_effect=mock_run):
        b = bellows.Bellows({"callback_port": 9999, "watched_projects": [],
                              "liveness_poll_seconds": 300})
        b._liveness_last_poll = 0.0
        b._poll_liveness()  # poll 1
        b._liveness_last_poll = 0.0  # reset clock so poll 2 runs
        b._poll_liveness()  # poll 2

    assert len(push_calls) == 1


# ---------------------------------------------------------------------------
# Test 9: Sites — depositor class_hold, stale-checkout, push-rejected pins
# ---------------------------------------------------------------------------

@patch("depositor.cycle_check")
@patch("depositor.subprocess")
def test_9a_depositor_class_hold(mock_subprocess, mock_cc, tmp_path):
    """Depositor holding a shop-infra plan calls notify_class_hold once."""
    import lifecycle
    from tests.test_depositor import _make_plan, _stage_plan, _write_receipt_for_plan

    mock_cc.run_check.return_value = ("BAR_MET", 0)
    mock_cc.parse_manifest_stanza.return_value = {}
    mock_subprocess.run.return_value = MagicMock(returncode=0, stdout="PASS: all")

    decisions_dir = tmp_path / "proj" / "knowledge" / "decisions"
    decisions_dir.mkdir(parents=True)
    db_path = str(tmp_path / "lifecycle.db")
    lifecycle.init_lifecycle_db(db_path)

    plan_text = _make_plan(writes=["bellows/depositor.py"])
    path = _stage_plan(str(decisions_dir), "executable-class-hold-100054", plan_text)
    _write_receipt_for_plan(tmp_path, path)

    isolated_root = tmp_path / "bellows_root"
    isolated_root.mkdir(exist_ok=True)
    (isolated_root / "receipts").mkdir(exist_ok=True)

    notify_calls = []
    with patch.object(depositor, "resolve_bellows_root", return_value=isolated_root), \
         patch.object(notifier, "notify_class_hold",
                      side_effect=lambda *a, **kw: notify_calls.append(a)) as mock_hold:
        dep = depositor.Depositor(
            disk_preflight_fn=lambda cfg: True,
            shutting_down_check=lambda: False,
            config={"watched_projects": [str(decisions_dir)]},
            lifecycle_db_path=db_path,
        )
        dep.evaluate(path)

    assert len(notify_calls) == 1, f"expected 1 notify_class_hold call, got {len(notify_calls)}"
    assert notify_calls[0][1] == "shop-infra"


def test_9b_stale_checkout_notify(tmp_path):
    """Wire point A stale checkout calls notify_checkout_stale once."""
    from tests.conftest import clear_plan_for_test

    decisions_dir = tmp_path / "proj" / "knowledge" / "decisions"
    decisions_dir.mkdir(parents=True)
    (decisions_dir / "Done").mkdir()

    plan_name = "executable-stale-co-100054.md"
    plan_path = str(decisions_dir / plan_name)
    with open(plan_path, "w") as f:
        f.write("# Stale CO Test\n\n## STEP 1\ntest\n")
    clear_plan_for_test(plan_path)

    config = {
        "default_model": "claude-sonnet-4-6",
        "pushover": {"app_key": "", "user_key": ""},
        "callback_port": 5998,
        "step_timeout_seconds": 600,
    }

    notify_calls = []

    with patch("bellows._checkout_is_current", return_value=(False, "stale checkout: test")), \
         patch("bellows.notifier.notify_plan_skipped"), \
         patch("bellows.plan_claim.release_for_plan"), \
         patch("bellows.lifecycle.mark_plan_state"), \
         patch("bellows._retire_receipts"), \
         patch("bellows.validators.validate_at_claim",
               return_value={"rejected": False, "reject_reason": "", "warnings": []}), \
         patch("bellows.plan_claim.claim_gate", return_value=True), \
         patch("bellows.lifecycle.mint_and_claim", return_value=1), \
         patch("bellows.notifier.notify_checkout_stale",
               side_effect=lambda *a, **kw: notify_calls.append(a)):
        bellows.run_plan(plan_path, config, MagicMock())

    assert len(notify_calls) == 1, f"expected 1 notify_checkout_stale call, got {len(notify_calls)}"


def test_9c_push_rejected_no_checkout_stale():
    """A worktree_teardown_push_rejected produces verdict_needed, not checkout_stale.

    Verified by source inspection: notify_checkout_stale is only called at wire
    point A (before claim_gate); the teardown exception handler calls only
    notify_verdict_request. The two paths are mutually exclusive.
    """
    import inspect
    src = inspect.getsource(bellows.run_plan)
    # checkout_stale appears once, before claim_gate
    assert src.count("notify_checkout_stale") == 1
    co_idx = src.index("notify_checkout_stale")
    # plan_claim.claim_gate appears after wire point A
    cg_idx = src.index("claim_gate")
    assert co_idx < cg_idx, (
        "notify_checkout_stale must appear before claim_gate in run_plan source"
    )


# ---------------------------------------------------------------------------
# Tests 9d–9i: _receipt_slug and verdict pages carry the deposit's stem
# ---------------------------------------------------------------------------

def test_9d_receipt_slug_reads_lifecycle_db(tmp_path, monkeypatch):
    """9d: _receipt_slug uses lifecycle.connect_readonly; recording wrapper confirms the tmp_path DB."""
    import lifecycle as _lc

    monkeypatch.setattr(bellows, "BELLOWS_ROOT", tmp_path)

    stem = "executable-foo-2026-09-14"
    plan_id = _lc.mint_and_claim(
        "executable", "/proj", "T", "bellows", "small", 1, f"{stem}.md",
    )

    seen_paths = []
    real_connect = _lc.connect_readonly

    def recording_connect(db_path, **kw):
        seen_paths.append(db_path)
        return real_connect(db_path, **kw)

    monkeypatch.setattr(_lc, "connect_readonly", recording_connect)

    result = bellows._receipt_slug(plan_id)

    assert result == stem, f"expected {stem!r}, got {result!r}"
    assert any(str(tmp_path / "lifecycle.db") == p for p in seen_paths), \
        f"connect_readonly not called with {tmp_path / 'lifecycle.db'}; saw {seen_paths}"


def test_9e_receipt_slug_missing_db_returns_none(tmp_path, monkeypatch):
    """9e: missing lifecycle.db → _receipt_slug returns None; file not created."""
    no_db_dir = tmp_path / "empty"
    no_db_dir.mkdir()
    monkeypatch.setattr(bellows, "BELLOWS_ROOT", no_db_dir)

    result = bellows._receipt_slug(1)

    assert result is None
    assert not (no_db_dir / "lifecycle.db").exists()


def test_9f_final_verdict_page_carries_receipt_key(tmp_path, monkeypatch):
    """9f: run_plan's final verdict page calls notify_verdict_request with receipt_key=stem, plan_slug=id."""
    from tests.conftest import clear_plan_for_test

    decisions_dir = tmp_path / "proj" / "knowledge" / "decisions"
    decisions_dir.mkdir(parents=True)
    plan_filename = "executable-no-header-2026-04-24.md"
    plan_path = str(decisions_dir / plan_filename)
    with open(plan_path, "w") as f:
        f.write("## STEP 1\nDo stuff.\n")
    clear_plan_for_test(plan_path)

    config = {
        "default_model": "claude-sonnet-4-6",
        "pushover": {"app_key": "", "user_key": ""},
        "callback_port": 5999,
        "step_timeout_seconds": 600,
    }

    verdict_kwargs = []

    def capture_verdict(*a, **kw):
        verdict_kwargs.append(kw)

    with patch("bellows.BELLOWS_ROOT", tmp_path), \
         patch("bellows.runner.run_step",
               return_value={"session_id": "s", "is_error": False, "stop_reason": "end_turn",
                             "result_text": "", "cost_usd": 0.01, "permission_denials": [],
                             "receipt_status": "Complete", "ceo_flags": [], "escalate": False}), \
         patch("bellows.gates.check",
               return_value={"passed": True, "failures": [], "is_qa_step": False,
                             "files_changed": [], "plan_header": {},
                             "verdict_requested": {"requested": False, "body": None}}), \
         patch("bellows.notifier.push"), \
         patch("bellows.notifier.notify_verdict_request", side_effect=capture_verdict), \
         patch("bellows.verdict.post_verdict_request"), \
         patch("bellows.verdict.log_to_ledger"), \
         patch("bellows._capture_git_diff", return_value=""), \
         patch("bellows._create_worktree", return_value="/tmp/wt"), \
         patch("bellows._teardown_worktree"), \
         patch("bellows.record_run"), \
         patch("bellows.validators.validate_at_claim",
               return_value={"rejected": False, "reject_reason": "", "warnings": []}):
        bellows.run_plan(plan_path, config, MagicMock())

    assert len(verdict_kwargs) == 1, f"expected 1 verdict call, got {verdict_kwargs}"
    kw = verdict_kwargs[0]
    assert kw.get("receipt_key") == "executable-no-header-2026-04-24", \
        f"receipt_key: {kw.get('receipt_key')!r}"
    assert kw.get("plan_slug") == "1", f"plan_slug: {kw.get('plan_slug')!r}"


def test_9g_intermediate_verdict_page_carries_receipt_key(tmp_path, monkeypatch):
    """9g: run_plan's in-loop verdict page (gate failure) carries receipt_key=stem, plan_slug=id."""
    from tests.conftest import clear_plan_for_test

    decisions_dir = tmp_path / "proj" / "knowledge" / "decisions"
    decisions_dir.mkdir(parents=True)
    plan_filename = "executable-rv1-site2-2026-05-24.md"
    plan_path = str(decisions_dir / plan_filename)
    with open(plan_path, "w") as f:
        f.write("## STEP 1\nDo stuff.\n## STEP 2\nMore stuff.\n")
    clear_plan_for_test(plan_path)

    config = {
        "default_model": "claude-sonnet-4-6",
        "pushover": {"app_key": "", "user_key": ""},
        "callback_port": 5999,
        "step_timeout_seconds": 600,
    }

    verdict_kwargs = []

    def capture_verdict(*a, **kw):
        verdict_kwargs.append(kw)

    def failing_gates(*args, **kwargs):
        return {"passed": False,
                "failures": [{"gate": "test_gate", "evidence": "forced"}],
                "is_qa_step": False, "files_changed": [],
                "plan_header": {"auto_close": "false"},
                "verdict_requested": {"requested": False, "body": None}}

    with patch("bellows.BELLOWS_ROOT", tmp_path), \
         patch("bellows._create_worktree", return_value="/tmp/wt"), \
         patch("bellows._capture_git_diff", return_value=""), \
         patch("bellows._teardown_worktree"), \
         patch("bellows.runner.run_step",
               return_value={"session_id": "s", "is_error": False, "stop_reason": "end_turn",
                             "result_text": "", "cost_usd": 0.01, "permission_denials": [],
                             "receipt_status": "Complete", "ceo_flags": [], "escalate": False}), \
         patch("bellows.gates.check", side_effect=failing_gates), \
         patch("bellows.notifier.notify_verdict_request", side_effect=capture_verdict), \
         patch("bellows.notifier.push"), \
         patch("bellows.record_run"), \
         patch("bellows.validators.validate_at_claim",
               return_value={"rejected": False, "reject_reason": "", "warnings": []}):
        bellows.run_plan(plan_path, config, MagicMock())

    assert len(verdict_kwargs) == 1, f"expected 1 verdict call, got {verdict_kwargs}"
    kw = verdict_kwargs[0]
    assert kw.get("receipt_key") == "executable-rv1-site2-2026-05-24", \
        f"receipt_key: {kw.get('receipt_key')!r}"
    assert kw.get("plan_slug") == "1", f"plan_slug: {kw.get('plan_slug')!r}"


def test_9h_failure_page_after_mint_pages_when_attended(tmp_path, monkeypatch):
    """9h: attended receipt under stem; run_step raises after mint → failure page pushes (pinned)."""
    from tests.conftest import clear_plan_for_test

    stem = "executable-no-header-2026-04-24"
    sid = "aaaabbbb11112222"
    hash12 = "aaaabbbbcccc"

    receipts_dir = tmp_path / "receipts"
    receipts_dir.mkdir()
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

    decisions_dir = tmp_path / "proj" / "knowledge" / "decisions"
    decisions_dir.mkdir(parents=True)
    plan_path = str(decisions_dir / f"{stem}.md")
    with open(plan_path, "w") as f:
        f.write("## STEP 1\nDo stuff.\n")
    clear_plan_for_test(plan_path)

    config = {
        "default_model": "claude-sonnet-4-6",
        "pushover": {"app_key": "k", "user_key": "u"},
        "callback_port": 5999,
        "step_timeout_seconds": 600,
    }

    push_titles = []

    with patch("bellows.BELLOWS_ROOT", tmp_path), \
         patch("bellows_root.resolve_bellows_root", return_value=tmp_path), \
         patch("bellows.runner.run_step", side_effect=RuntimeError("step failed")), \
         patch("bellows._create_worktree", return_value="/tmp/wt"), \
         patch("bellows._capture_git_diff", return_value=""), \
         patch("bellows._teardown_worktree"), \
         patch("bellows.record_run"), \
         patch("bellows.notifier.push",
               side_effect=lambda ak, uk, title, msg, **kw: push_titles.append(title) or True), \
         patch("bellows.validators.validate_at_claim",
               return_value={"rejected": False, "reject_reason": "", "warnings": []}):
        bellows.run_plan(plan_path, config, MagicMock())

    assert len(push_titles) == 1, f"expected 1 push, got {push_titles}"
    assert "Failed" in push_titles[0], f"expected 'Bellows — Failed', got {push_titles[0]!r}"


def test_9i_stale_checkout_page_pages_when_attended(tmp_path, monkeypatch):
    """9i: attended receipt under stem; stale checkout at wire-A → push (plan_slug ≠ stem key; pinned)."""
    from tests.conftest import clear_plan_for_test

    stem = "executable-stale-co-100112"
    sid = "bbbbcccc11112222"
    hash12 = "bbbbccccdddd"

    receipts_dir = tmp_path / "receipts"
    receipts_dir.mkdir()
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

    decisions_dir = tmp_path / "proj" / "knowledge" / "decisions"
    decisions_dir.mkdir(parents=True)
    (decisions_dir / "Done").mkdir()
    plan_path = str(decisions_dir / f"{stem}.md")
    with open(plan_path, "w") as f:
        f.write("# Stale CO Test\n\n## STEP 1\ntest\n")
    clear_plan_for_test(plan_path)

    config = {
        "default_model": "claude-sonnet-4-6",
        "pushover": {"app_key": "k", "user_key": "u"},
        "callback_port": 5999,
        "step_timeout_seconds": 600,
    }

    push_titles = []

    with patch("bellows.BELLOWS_ROOT", tmp_path), \
         patch("bellows_root.resolve_bellows_root", return_value=tmp_path), \
         patch("bellows._checkout_is_current", return_value=(False, "stale checkout: test")), \
         patch("bellows.notifier.notify_plan_skipped"), \
         patch("bellows.plan_claim.release_for_plan"), \
         patch("bellows.lifecycle.mark_plan_state"), \
         patch("bellows._retire_receipts"), \
         patch("bellows.validators.validate_at_claim",
               return_value={"rejected": False, "reject_reason": "", "warnings": []}), \
         patch("bellows.plan_claim.claim_gate", return_value=True), \
         patch("bellows.lifecycle.mint_and_claim", return_value=1), \
         patch("bellows.notifier.push",
               side_effect=lambda ak, uk, title, msg, **kw: push_titles.append(title) or True):
        bellows.run_plan(plan_path, config, MagicMock())

    assert len(push_titles) == 1, f"expected 1 push, got {push_titles}"
    assert "Stale Checkout" in push_titles[0], \
        f"expected 'Bellows — Hold: Stale Checkout', got {push_titles[0]!r}"


# ---------------------------------------------------------------------------
# Test 10: Liveness poll
# ---------------------------------------------------------------------------

def test_10_liveness_poll(monkeypatch, tmp_path):
    """_poll_liveness calls notify_watcher_down for stale rows, not for live rows."""
    notifier.init_notifications({
        "pushover": {"app_key": "k", "user_key": "u"},
        "notifications": {"enabled": True, "events": {}},
    })

    watcher_calls = []
    monkeypatch.setattr(notifier, "notify_watcher_down",
                        lambda m, s, a: watcher_calls.append((m, s, a)) or True)
    mark_calls = []
    monkeypatch.setattr(notifier, "mark_machine_live", lambda m: mark_calls.append(m))

    liveness_json = json.dumps([
        {"machine": "air", "status": "stale", "age_seconds": 900, "heartbeat_only": True},
        {"machine": "mini", "status": "live", "age_seconds": 10, "heartbeat_only": True},
    ])

    mock_result = MagicMock()
    mock_result.returncode = 0
    mock_result.stdout = liveness_json

    checkout = tmp_path / "tuyere"
    checkout.mkdir()
    (checkout / ".venv" / "bin").mkdir(parents=True)
    (checkout / ".venv" / "bin" / "python").write_text("#!/usr/bin/env python3")

    subprocess_calls = []

    def mock_run(cmd, **kwargs):
        subprocess_calls.append(cmd)
        return mock_result

    with patch("bellows.server.ResponseServer"), \
         patch("bellows.depositor.Depositor"), \
         patch("bellows.plan_claim._tuyere_checkout", return_value=checkout), \
         patch("bellows.subprocess.run", side_effect=mock_run):
        b = bellows.Bellows({"callback_port": 9999, "watched_projects": [],
                              "liveness_poll_seconds": 300})
        b._liveness_last_poll = 0.0  # ensure poll runs

        b._poll_liveness()

    # stale machine → notify_watcher_down called; live machine → mark_machine_live called
    assert len(watcher_calls) == 1
    assert watcher_calls[0][0] == "air"
    assert watcher_calls[0][1] == "stale"
    assert "mini" in mark_calls

    # Second poll within liveness_poll_seconds → subprocess NOT called again
    subprocess_calls.clear()
    with patch("bellows.server.ResponseServer"), \
         patch("bellows.depositor.Depositor"), \
         patch("bellows.plan_claim._tuyere_checkout", return_value=checkout), \
         patch("bellows.subprocess.run", side_effect=mock_run):
        b2 = bellows.Bellows({"callback_port": 9999, "watched_projects": [],
                               "liveness_poll_seconds": 300})
        b2._liveness_last_poll = time.time()  # just polled
        b2._poll_liveness()
    assert len(subprocess_calls) == 0

    # TimeoutExpired → one WARN, no exception, no notify
    watcher_calls.clear()
    warn_calls = []

    def raise_timeout(cmd, **kwargs):
        raise subprocess.TimeoutExpired(cmd, 15)

    with patch("bellows.server.ResponseServer"), \
         patch("bellows.depositor.Depositor"), \
         patch("bellows.plan_claim._tuyere_checkout", return_value=checkout), \
         patch("bellows.subprocess.run", side_effect=raise_timeout), \
         patch("bellows._log", side_effect=lambda lvl, msg, **kw:
               warn_calls.append((lvl, msg)) if lvl == "WARN" else None):
        b3 = bellows.Bellows({"callback_port": 9999, "watched_projects": [],
                               "liveness_poll_seconds": 300})
        b3._liveness_last_poll = 0.0
        b3._poll_liveness()

    assert len(watcher_calls) == 0
    liveness_warns = [m for _, m in warn_calls if "liveness" in m.lower()]
    assert len(liveness_warns) == 1

    # Non-zero exit → one WARN
    warn_calls.clear()
    mock_fail = MagicMock()
    mock_fail.returncode = 1
    mock_fail.stdout = ""
    with patch("bellows.server.ResponseServer"), \
         patch("bellows.depositor.Depositor"), \
         patch("bellows.plan_claim._tuyere_checkout", return_value=checkout), \
         patch("bellows.subprocess.run", return_value=mock_fail), \
         patch("bellows._log", side_effect=lambda lvl, msg, **kw:
               warn_calls.append((lvl, msg)) if lvl == "WARN" else None):
        b4 = bellows.Bellows({"callback_port": 9999, "watched_projects": [],
                               "liveness_poll_seconds": 300})
        b4._liveness_last_poll = 0.0
        b4._poll_liveness()
    liveness_warns = [m for _, m in warn_calls if "liveness" in m.lower()]
    assert len(liveness_warns) == 1

    # Unparseable JSON → one WARN
    warn_calls.clear()
    mock_bad_json = MagicMock()
    mock_bad_json.returncode = 0
    mock_bad_json.stdout = "not json"
    with patch("bellows.server.ResponseServer"), \
         patch("bellows.depositor.Depositor"), \
         patch("bellows.plan_claim._tuyere_checkout", return_value=checkout), \
         patch("bellows.subprocess.run", return_value=mock_bad_json), \
         patch("bellows._log", side_effect=lambda lvl, msg, **kw:
               warn_calls.append((lvl, msg)) if lvl == "WARN" else None):
        b5 = bellows.Bellows({"callback_port": 9999, "watched_projects": [],
                               "liveness_poll_seconds": 300})
        b5._liveness_last_poll = 0.0
        b5._poll_liveness()
    liveness_warns = [m for _, m in warn_calls if "liveness" in m.lower()]
    assert len(liveness_warns) == 1

    # None checkout → one WARN
    warn_calls.clear()
    with patch("bellows.server.ResponseServer"), \
         patch("bellows.depositor.Depositor"), \
         patch("bellows.plan_claim._tuyere_checkout", return_value=None), \
         patch("bellows._log", side_effect=lambda lvl, msg, **kw:
               warn_calls.append((lvl, msg)) if lvl == "WARN" else None):
        b6 = bellows.Bellows({"callback_port": 9999, "watched_projects": [],
                               "liveness_poll_seconds": 300})
        b6._liveness_last_poll = 0.0
        b6._poll_liveness()
    liveness_warns = [m for _, m in warn_calls if "liveness" in m.lower()]
    assert len(liveness_warns) == 1


# ---------------------------------------------------------------------------
# Test 11: Gate watcher — _push_pause returns the new string
# ---------------------------------------------------------------------------

def test_11_gate_watcher():
    """_push_pause returns the daemon-is-the-pager string; notify_verdict_request not called."""
    # Load by explicit path to avoid the main-checkout ambiguity (thread 243 hazard).
    import importlib.util as _ilu
    _spec = _ilu.spec_from_file_location(
        "gate_watcher_wt",
        str(REPO_ROOT / "tools" / "gate_watcher.py"),
    )
    gw = _ilu.module_from_spec(_spec)
    _spec.loader.exec_module(gw)

    # Build a minimal cur state with non-empty pushover keys
    cur = {
        "state": "awaiting_verdict",
        "pending": ["verdict-request-1-step-1.md"],
        "gate_failures": [],
    }

    notify_calls = []
    with patch.object(notifier, "notify_verdict_request",
                      side_effect=lambda *a, **kw: notify_calls.append(1)):
        with tempfile.TemporaryDirectory() as tmp:
            db_path = os.path.join(tmp, "lifecycle.db")
            import lifecycle
            lifecycle.init_lifecycle_db(db_path)
            # Write config.json beside the db
            cfg = {
                "pushover": {"app_key": "k", "user_key": "u"},
                "notifications": {"enabled": True},
            }
            with open(os.path.join(tmp, "config.json"), "w") as f:
                json.dump(cfg, f)

            result = gw._push_pause("test-plan", cur, db_path=db_path)

    assert "push skipped" in result.lower() or "daemon is the pager" in result.lower(), (
        f"expected daemon-is-the-pager string, got: {result!r}"
    )
    assert len(notify_calls) == 0, "notify_verdict_request should not be called by gate watcher"


# ---------------------------------------------------------------------------
# Test 12: config.example.json
# ---------------------------------------------------------------------------

def test_12_config_example():
    config_path = REPO_ROOT / "config.example.json"
    with open(config_path) as f:
        cfg = json.load(f)

    events = cfg["notifications"]["events"]
    expected_true = {"verdict_needed", "plan_halted", "failure", "disk_low",
                     "class_hold", "checkout_stale", "watcher_down"}
    expected_false = {"plan_complete", "plan_skipped", "queue_empty", "cycle_nudge"}
    all_expected = expected_true | expected_false
    assert set(events.keys()) == all_expected, (
        f"config.example.json events keys mismatch: {set(events.keys())} vs {all_expected}"
    )
    for e in expected_true:
        assert events[e] is True, f"{e} should be true in config.example.json"
    for e in expected_false:
        assert events[e] is False, f"{e} should be false in config.example.json"

    notifications = cfg["notifications"]
    assert "attended_window_seconds" in notifications
    assert "dedupe_window_seconds" in notifications
    assert "liveness_poll_seconds" in notifications
