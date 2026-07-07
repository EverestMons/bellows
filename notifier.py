"""Pushover push notifications with urgency-gated coalescing.

Urgent events (verdict-needed, failure) push immediately.
Deferred events (plan-complete, plan-halted, plan-skipped, queue-empty)
buffer for a configurable window (default 30s) then send a single digest.
"""

import threading
from typing import Optional

import requests

from bellows import _log

PUSHOVER_API_URL = "https://api.pushover.net/1/messages.json"

# --- Module-level config (set by init_notifications()) ---
_config: dict = {}
_app_key: str = ""
_user_key: str = ""

# --- Coalescing buffer state ---
_buffer: list[dict] = []
_buffer_lock = threading.Lock()
_timer: Optional[threading.Timer] = None
_timer_lock = threading.Lock()


def init_notifications(config: dict) -> None:
    """Initialize notification subsystem with config. Call once at startup."""
    global _config, _app_key, _user_key
    _config = config.get("notifications", {})
    _app_key = config.get("pushover", {}).get("app_key", "")
    _user_key = config.get("pushover", {}).get("user_key", "")


def _notifications_enabled() -> bool:
    return _config.get("enabled", True)


def _event_enabled(event_name: str) -> bool:
    if not _notifications_enabled():
        return False
    events = _config.get("events", {})
    return events.get(event_name, True)


def _coalesce_window() -> int:
    return _config.get("coalesce_window_seconds", 30)


# --- Low-level push ---


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
    halted = []
    skipped = []
    queue_empty = False
    nudge_events = []

    for e in events:
        et = e["event_type"]
        p = e["payload"]
        if et == "plan_complete":
            completes.append(f"{p['plan_name']} (${p['total_cost']:.4f})")
        elif et == "plan_halted":
            halted.append(p["plan_name"])
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
    if halted:
        if len(halted) == 1:
            lines.append(f"1 plan halted: {halted[0]}")
        else:
            lines.append(f"{len(halted)} plans halted: {', '.join(halted)}")
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


# --- Named notification functions ---


def notify_plan_complete(plan_name: str, total_cost: float) -> bool:
    if not _event_enabled("plan_complete"):
        return False
    _enqueue_deferred("plan_complete", plan_name=plan_name, total_cost=total_cost)
    return True


def notify_plan_halted(plan_name: str) -> bool:
    if not _event_enabled("plan_halted"):
        return False
    _enqueue_deferred("plan_halted", plan_name=plan_name)
    return True


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
                   step: int, error: str) -> bool:
    if not _event_enabled("failure"):
        return False
    _flush_buffer_immediate()
    return push(
        app_key, user_key,
        title="Bellows — Failed",
        message=f"Plan: {plan_name}\nStep: {step}\nError: {error}",
        priority=1, sound="falling",
    )


def notify_cycle_nudge(count: int, since_ts: str) -> bool:
    if not _event_enabled("cycle_nudge"):
        return False
    _enqueue_deferred("cycle_nudge", count=count, since_ts=since_ts)
    return True


def notify_verdict_request(app_key: str, user_key: str, plan_name: str,
                           step: int, gate_failures: list) -> bool:
    if not _event_enabled("verdict_needed"):
        return False
    _flush_buffer_immediate()
    if gate_failures:
        failure_text = ", ".join(f["gate"] for f in gate_failures)
    else:
        failure_text = "QA checkpoint (all gates passed)"
    return push(
        app_key, user_key,
        title="Bellows — Verdict Needed",
        message=f"Plan: {plan_name}\nStep: {step}\nGate failures: {failure_text}",
        priority=1,
    )
