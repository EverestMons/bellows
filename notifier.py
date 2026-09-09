"""Pushover push notifications with urgency-gated coalescing.

Urgent events (verdict-needed, failure) push immediately.
Deferred events (plan-complete, plan-skipped, queue-empty) buffer for a
configurable window (default 30s) then send a single digest.
"""

import glob as _glob_module
import json
import os
import socket
import threading
import time
from pathlib import Path
from typing import Optional

import requests

from bellows import _log

PUSHOVER_API_URL = "https://api.pushover.net/1/messages.json"

# --- Module-level config (set by init_notifications()) ---
_config: dict = {}
_app_key: str = ""
_user_key: str = ""

# --- In-process dedupe memo: {key_tuple: last_sent_epoch} ---
_dedupe_memo: dict = {}

# --- Coalescing buffer state ---
_buffer: list[dict] = []
_buffer_lock = threading.Lock()
_timer: Optional[threading.Timer] = None
_timer_lock = threading.Lock()

# --- Ruled event defaults (change 1) ---
_DEFAULT_EVENTS = {
    "verdict_needed": True,
    "plan_halted": True,
    "failure": True,
    "disk_low": True,
    "class_hold": True,
    "checkout_stale": True,
    "watcher_down": True,
    "plan_complete": False,
    "plan_skipped": False,
    "queue_empty": False,
    "cycle_nudge": False,
}


def init_notifications(config: dict) -> None:
    """Initialize notification subsystem with config. Clears dedupe memo on re-init."""
    global _config, _app_key, _user_key
    _config = config.get("notifications", {})
    _app_key = config.get("pushover", {}).get("app_key", "")
    _user_key = config.get("pushover", {}).get("user_key", "")
    _dedupe_memo.clear()


def _notifications_enabled() -> bool:
    return _config.get("enabled", True)


def _event_enabled(event_name: str) -> bool:
    if not _notifications_enabled():
        return False
    events = _config.get("events", {})
    return events.get(event_name, _DEFAULT_EVENTS.get(event_name, False))


def _coalesce_window() -> int:
    return _config.get("coalesce_window_seconds", 30)


# --- Low-level push (unchanged — test_notifier_server.py passes unchanged) ---


def push(app_key: str, user_key: str, title: str, message: str,
         url: str = "", url_title: str = "",
         priority: int = 0, sound: Optional[str] = None) -> bool:
    payload = {
        "token": app_key,
        "user": user_key,
        "title": title,
        "message": message,
    }
    if url:
        payload["url"] = url
    if url_title:
        payload["url_title"] = url_title
    if priority != 0:
        payload["priority"] = priority
    if sound is not None:
        payload["sound"] = sound
    try:
        response = requests.post(PUSHOVER_API_URL, data=payload, timeout=(5, 10))
        return response.status_code == 200
    except requests.RequestException as e:
        _log("ERROR", f"notifier: {e}")
        return False


# --- Coalescing buffer ---


def _enqueue_deferred(event_type: str, **payload) -> None:
    """Buffer a deferred event. Resets the coalesce timer."""
    global _timer
    with _buffer_lock:
        _buffer.append({"event_type": event_type, "payload": payload})

    window = _coalesce_window()
    if window <= 0:
        # Coalescing disabled — flush immediately
        _flush_buffer()
        return

    with _timer_lock:
        if _timer is not None:
            _timer.cancel()
        _timer = threading.Timer(window, _flush_buffer)
        _timer.daemon = True
        _timer.start()


def _flush_buffer() -> None:
    """Drain the buffer and push a single coalesced digest."""
    global _timer
    with _buffer_lock:
        events = list(_buffer)
        _buffer.clear()
    with _timer_lock:
        if _timer is not None:
            _timer.cancel()
        _timer = None

    if not events:
        return

    # Group by event type
    completes = []
    skipped = []
    queue_empty = False
    nudge_events = []

    for e in events:
        et = e["event_type"]
        p = e["payload"]
        if et == "plan_complete":
            completes.append(f"{p['plan_name']} (${p['total_cost']:.4f})")
        elif et == "plan_skipped":
            skipped.append(p["plan_name"])
        elif et == "queue_empty":
            queue_empty = True
        elif et == "cycle_nudge":
            nudge_events.append(p)

    lines = []
    if completes:
        if len(completes) == 1:
            lines.append(f"1 plan complete: {completes[0]}")
        else:
            lines.append(f"{len(completes)} plans complete: {', '.join(completes)}")
    if skipped:
        if len(skipped) == 1:
            lines.append(f"1 plan skipped: {skipped[0]}")
        else:
            lines.append(f"{len(skipped)} plans skipped: {', '.join(skipped)}")
    if nudge_events:
        p = nudge_events[-1]
        lines.append(f"Learning loop nudge: {p['count']} plans closed since last ingestion ({p['since_ts']}).")
    if queue_empty:
        lines.append("Queue empty.")

    digest_message = "\n".join(lines)
    push(_app_key, _user_key, "Bellows — Session Update", digest_message,
         priority=0, sound="none")


def _flush_buffer_immediate() -> None:
    """Force-flush pending buffer before an urgent push. Called by urgent notifications."""
    _flush_buffer()


# --- Dedupe (change 3) ---


def _dedupe(key: tuple) -> bool:
    """Return True (send) if key is outside the dedupe window; update the memo."""
    window = _config.get("dedupe_window_seconds", 3600)
    now = time.time()
    last = _dedupe_memo.get(key)
    if last is not None and (now - last) < window:
        return False
    _dedupe_memo[key] = now
    return True


def mark_machine_live(machine: str) -> None:
    """Clear the watcher_down dedupe for a machine so a new episode pages once."""
    _dedupe_memo.pop((machine, "-", "watcher_down"), None)


# --- Ownership signal (change 2) ---


def owned_by_live_session(plan_slug: str, receipts_dir=None,
                          window=None) -> tuple:
    """Return (owned: bool, why: str).

    owned=True means the depositing session's transcript is fresh enough
    to suppress a push (the session is attended). Any failure → (False, why)
    so a check that cannot run always pages — silence is never the failure mode.
    """
    try:
        if receipts_dir is None:
            from bellows_root import resolve_bellows_root
            receipts_dir = resolve_bellows_root() / "receipts"
        receipts_dir = Path(receipts_dir)
        if window is None:
            window = _config.get("attended_window_seconds", 600)

        matches = list(receipts_dir.glob(f"receipt-{plan_slug}-*.json"))
        if not matches:
            return (False, "no receipt")

        newest = max(matches, key=lambda p: p.stat().st_mtime)
        try:
            data = json.loads(newest.read_text())
        except Exception as exc:
            return (False, f"ownership check failed: {type(exc).__name__}")

        session_id = data.get("session_id")
        if not session_id:
            return (False, "no session_id in receipt")

        pattern = os.path.expanduser(f"~/.claude/projects/*/{session_id}.jsonl")
        transcripts = _glob_module.glob(pattern)
        if not transcripts:
            return (False, "no transcript")

        age = time.time() - os.path.getmtime(transcripts[0])
        if age <= window:
            return (True, f"owned by session {session_id[:8]} — transcript {int(age)}s old")
        return (False, f"transcript {int(age)}s old")
    except Exception as exc:
        return (False, f"ownership check failed: {type(exc).__name__}")


# --- Central gate (change 4) ---


def notify_event(event: str, plan_slug, title: str, message: str,
                 priority: int = 0, plan_scoped: bool = True,
                 detail_key: str = "") -> bool:
    """The ONE gate every page passes through.

    enabled → _event_enabled → _dedupe → (plan_scoped only) owned_by_live_session → push.
    Every refusal logs exactly one INFO line naming the reason.
    """
    if not _notifications_enabled():
        _log("INFO", f"notifier: {event} {plan_slug} not paged — disabled")
        return False
    events_cfg = _config.get("events", {})
    if not events_cfg.get(event, _DEFAULT_EVENTS.get(event, False)):
        _log("INFO", f"notifier: {event} {plan_slug} not paged — event off")
        return False
    machine = socket.gethostname()
    key = (machine, plan_slug or "-", event, detail_key)
    if not _dedupe(key):
        _log("INFO", f"notifier: {event} {plan_slug} not paged — deduped")
        return False
    if plan_scoped and plan_slug:
        owned, why = owned_by_live_session(plan_slug)
        if owned:
            _log("INFO", f"notifier: {event} {plan_slug} not paged — {why}")
            return False
    _flush_buffer_immediate()
    result = push(_app_key, _user_key, title, message, priority=priority)
    if result:
        _log("INFO", f"notifier: {event} {plan_slug} paged")
    return result


# --- Named notification functions ---


def notify_plan_complete(plan_name: str, total_cost: float) -> bool:
    if not _event_enabled("plan_complete"):
        return False
    _enqueue_deferred("plan_complete", plan_name=plan_name, total_cost=total_cost)
    return True


def notify_plan_halted(plan_name: str, plan_slug=None) -> bool:
    return notify_event(
        "plan_halted", plan_slug, "Bellows — Plan Halted",
        f"Plan: {plan_name}",
        priority=0, plan_scoped=True,
    )


def notify_plan_skipped(plan_name: str) -> bool:
    if not _event_enabled("plan_skipped"):
        return False
    _enqueue_deferred("plan_skipped", plan_name=plan_name)
    return True


def notify_queue_empty() -> bool:
    if not _event_enabled("queue_empty"):
        return False
    _enqueue_deferred("queue_empty")
    return True


def notify_failure(app_key: str, user_key: str, plan_name: str,
                   step: int, error: str, plan_slug=None) -> bool:
    return notify_event(
        "failure", plan_slug, "Bellows — Failed",
        f"Plan: {plan_name}\nStep: {step}\nError: {error}",
        priority=1, plan_scoped=True, detail_key=str(step),
    )


def notify_cycle_nudge(count: int, since_ts: str) -> bool:
    if not _event_enabled("cycle_nudge"):
        return False
    _enqueue_deferred("cycle_nudge", count=count, since_ts=since_ts)
    return True


def notify_verdict_request(app_key: str, user_key: str, plan_name: str,
                           step: int, gate_failures: list,
                           plan_slug=None) -> bool:
    if gate_failures:
        failure_text = ", ".join(f["gate"] for f in gate_failures)
    else:
        failure_text = "QA checkpoint (all gates passed)"
    return notify_event(
        "verdict_needed", plan_slug, "Bellows — Verdict Needed",
        f"Plan: {plan_name}\nStep: {step}\nGate failures: {failure_text}",
        priority=1, plan_scoped=True, detail_key=str(step),
    )


# --- New notifiers (change 5) ---


def notify_class_hold(plan_slug: str, assigned_class: str) -> bool:
    """Page when the depositor holds a plan awaiting CEO class-hold release."""
    return notify_event(
        "class_hold", plan_slug, "Bellows — Hold: Class Review",
        f"Plan: {plan_slug}\nClass: {assigned_class} — awaiting release",
        priority=1, plan_scoped=False,
    )


def notify_checkout_stale(plan_slug: str, detail: str) -> bool:
    """Page when wire point A holds a plan due to a stale checkout."""
    return notify_event(
        "checkout_stale", plan_slug, "Bellows — Hold: Stale Checkout",
        f"Plan: {plan_slug}\n{detail}",
        priority=0, plan_scoped=True,
    )


def notify_disk_low(free_gb: float, threshold_gb: float) -> bool:
    """Page when free disk space is below the configured threshold."""
    return notify_event(
        "disk_low", None, "Bellows — Disk Low",
        f"Free: {free_gb:.2f} GB, threshold: {threshold_gb} GB — claims paused",
        priority=0, plan_scoped=False,
    )


def notify_watcher_down(machine: str, status: str, age_seconds: float) -> bool:
    """Page when tuyere's liveness poll finds a watcher stale or down.

    Uses a machine-keyed 3-tuple dedupe; mark_machine_live() clears it so
    each new stale episode pages exactly once.
    """
    event = "watcher_down"
    if not _notifications_enabled():
        _log("INFO", f"notifier: {event} {machine} not paged — disabled")
        return False
    events_cfg = _config.get("events", {})
    if not events_cfg.get(event, _DEFAULT_EVENTS.get(event, False)):
        _log("INFO", f"notifier: {event} {machine} not paged — event off")
        return False
    key = (machine, "-", "watcher_down")
    if not _dedupe(key):
        _log("INFO", f"notifier: {event} {machine} not paged — deduped")
        return False
    result = push(
        _app_key, _user_key,
        f"Bellows — Watcher {status.title()}",
        f"Machine: {machine}\nStatus: {status}\nAge: {int(age_seconds)}s",
        priority=1,
    )
    if result:
        _log("INFO", f"notifier: {event} {machine} paged")
    return result
