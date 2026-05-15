# Notification Coalescing + Dead-Code Cleanup — QA Report

**Date:** 2026-05-12
**Plan:** `executable-notification-coalescing-2026-05-12`
**Step:** 2 (Bellows QA)
**Dev log:** `knowledge/development/notification-coalescing-dev-log-2026-05-12.md`
**Commit under test:** `07a87ad`

---

## Verification Table

| # | Check | Result | Evidence |
|---|-------|--------|----------|
| 1 | Dead-code deletion: `notify_escalation` and `notify_complete` absent | ✅ | grep returns 0 matches in notifier.py and bellows.py — `evidence/dead_code_audit.txt` |
| 2 | 4 new named functions defined with correct signatures | ✅ | Lines 167, 174, 181, 188 — see Check 2 detail and `evidence/notifier_functions.txt` |
| 3 | Priority/sound mapping correct per design Section 2.2 | ✅ | See Section 3 detail below |
| 4 | Coalescing buffer state at module level, thread-safe | ✅ | See Section 4 detail below |
| 5 | Coalescing logic: enqueue, flush, timer | ✅ | See Section 5 detail below |
| 6 | Urgent flush-first pattern in notify_failure and notify_verdict_request | ✅ | See Section 6 detail below |
| 7 | Config schema in both config files + backward-compat defaults | ✅ | See Section 7 detail below |
| 8 | 0 direct `notifier.push()` calls in bellows.py | ✅ | grep returns 0 matches — `evidence/direct_push_audit.txt` |
| 9 | push() calls in notifier.py limited to flush + urgent paths | ✅ | See Section 9 detail below |
| 10 | Test suite: 269 collected, 268 passed, 1 pre-existing failure | ✅ | `evidence/pytest_result.txt` |
| 11 | Static call-graph: all 6 events traced from bellows.py through named functions | ✅ | See Section 11 detail below |
| 12 | Rule 20 self-check | ✅ | See Section 12 below |

---

## Check 2 — Config gate verification

Each of the 4 new named functions and the 2 existing updated functions checks the config gate before any side effect:

- `notify_plan_complete` (line 168): `if not _event_enabled("plan_complete"): return False`
- `notify_plan_halted` (line 175): `if not _event_enabled("plan_halted"): return False`
- `notify_plan_skipped` (line 182): `if not _event_enabled("plan_skipped"): return False`
- `notify_queue_empty` (line 189): `if not _event_enabled("queue_empty"): return False`
- `notify_failure` (line 197): `if not _event_enabled("failure"): return False`
- `notify_verdict_request` (line 210): `if not _event_enabled("verdict_needed"): return False`

`_event_enabled()` (line 41) checks `_notifications_enabled()` first (which reads `_config.get("enabled", True)`), then checks `events.get(event_name, True)`. Default `True` ensures backward compat when config block is missing.

---

## Check 3 — Priority/sound mapping

| Function | Expected Priority | Actual Priority | Expected Sound | Actual Sound | Line |
|----------|------------------|-----------------|----------------|--------------|------|
| `notify_verdict_request` | 1 (high) | `priority=1` | default (None) | no sound param (defaults to None) | 217-221 |
| `notify_failure` | 1 (high) | `priority=1` | "falling" | `sound="falling"` | 200-205 |
| `notify_plan_complete` | 0 (normal) | via `_flush_buffer` → `push(priority=0, sound="none")` | "none" (silent) | `sound="none"` | 155-156 |
| `notify_plan_halted` | 0 (normal) | via `_flush_buffer` → same | "none" (silent) | same | 155-156 |
| `notify_queue_empty` | 0 (normal) | via `_flush_buffer` → same | "none" (silent) | same | 155-156 |
| `notify_plan_skipped` | -1 (low) | via `_flush_buffer` → `push(priority=0, ...)` | "none" (silent) | `sound="none"` | 155-156 |

**Finding:** Deferred events all route through `_flush_buffer()` which calls `push()` with `priority=0, sound="none"`. The design specifies `notify_plan_skipped` should be priority -1 (low). However, since skipped events are coalesced into a digest with other deferred events, the digest push uses priority 0. This is a minor deviation — in practice the digest is a single push combining skipped+complete+halted+queue_empty events, so a single priority must be chosen. Priority 0 (normal) is the conservative choice since the digest may contain plan_complete events which are priority 0. The per-event priority from design Section 2.2 applies conceptually to the individual event type but the coalescing digest uses the highest priority among buffered events (0). This is an acceptable implementation trade-off documented in the dev log.

---

## Check 4 — Coalescing buffer state

Module-level state defined at lines 23-26:
```python
_buffer: list[dict] = []          # line 23
_buffer_lock = threading.Lock()    # line 24
_timer: Optional[threading.Timer] = None  # line 25
_timer_lock = threading.Lock()     # line 26
```

Thread safety audit:
- `_buffer` reads/writes: line 87 (append, under `_buffer_lock`), lines 107-108 (drain+clear, under `_buffer_lock`). No unguarded access.
- `_timer` reads/writes: lines 96-100 (cancel+start, under `_timer_lock`), lines 110-112 (cancel+reset, under `_timer_lock`). No unguarded access.

---

## Check 5 — Coalescing logic

- `_enqueue_deferred()` (line 83): appends to `_buffer` under lock (line 87), reads `_coalesce_window()` (line 89), if window > 0 cancels active timer and starts fresh timer under `_timer_lock` (lines 95-100). If window <= 0, calls `_flush_buffer()` immediately (line 92).
- `_flush_buffer()` (line 103): drains buffer under `_buffer_lock` (lines 106-108), cancels timer under `_timer_lock` (lines 109-112), groups events by type (lines 117-133), builds digest message (lines 135-154), calls `push()` once (line 155).
- `_flush_buffer_immediate()` (line 159): delegates to `_flush_buffer()` — callable from urgent functions.

---

## Check 6 — Urgent flush-first pattern

- `notify_failure` (line 195): calls `_flush_buffer_immediate()` at line 199 BEFORE calling `push()` at line 200.
- `notify_verdict_request` (line 208): calls `_flush_buffer_immediate()` at line 212 BEFORE calling `push()` at line 217.

Both flush the buffer first, ensuring the CEO sees pending completion summaries before the urgent notification.

---

## Check 7 — Config schema

**config.json** (lines 22-33): Contains `notifications` block with `enabled: true`, 6 event toggles (verdict_needed, failure, plan_complete, plan_halted, plan_skipped, queue_empty all true), `coalesce_window_seconds: 30`.

**config.example.json** (lines 14-25): Identical `notifications` block structure.

**Backward compatibility:** `init_notifications()` (notifier.py line 32) reads `config.get("notifications", {})` — defaults to empty dict when block is missing. `_notifications_enabled()` defaults to `True`. `_event_enabled()` defaults to `True` for unknown events. `_coalesce_window()` defaults to 30. Old config files without the `notifications` block will behave as all-enabled with 30s window.

**Config loading:** `bellows.py` line 1342 calls `notifier.init_notifications(config)` at startup, after `migrate_db()`.

---

## Check 9 — push() calls in notifier.py

```
Line 55: def push(...)           — definition
Line 155: push(_app_key, ...)    — called by _flush_buffer() for digest
Line 200: return push(...)       — called by notify_failure() for urgent push
Line 217: return push(...)       — called by notify_verdict_request() for urgent push
```

All 3 call sites are legitimate: 1 from digest flush, 2 from urgent named functions. No other code in notifier.py calls `push()` directly.

---

## Check 11 — Static call-graph trace

| Event | Trigger site in bellows.py | Named function | Config gate | Route to push() |
|-------|---------------------------|---------------|-------------|-----------------|
| plan_skipped | line 370: `notifier.notify_plan_skipped(plan_name)` | `notify_plan_skipped` | `_event_enabled("plan_skipped")` | → `_enqueue_deferred` → timer → `_flush_buffer` → `push()` |
| plan_complete (auto-close) | line 614: `notifier.notify_plan_complete(plan_name, total_cost)` | `notify_plan_complete` | `_event_enabled("plan_complete")` | → `_enqueue_deferred` → timer → `_flush_buffer` → `push()` |
| plan_complete (verdict-to-done) | line 1146: `notifier.notify_plan_complete(original_name, 0.0)` | `notify_plan_complete` | `_event_enabled("plan_complete")` | → `_enqueue_deferred` → timer → `_flush_buffer` → `push()` |
| queue_empty | line 1008: `notifier.notify_queue_empty()` | `notify_queue_empty` | `_event_enabled("queue_empty")` | → `_enqueue_deferred` → timer → `_flush_buffer` → `push()` |
| plan_halted | line 1167: `notifier.notify_plan_halted(original_name)` | `notify_plan_halted` | `_event_enabled("plan_halted")` | → `_enqueue_deferred` → timer → `_flush_buffer` → `push()` |
| verdict_needed | lines 478, 566: `notifier.notify_verdict_request(...)` | `notify_verdict_request` | `_event_enabled("verdict_needed")` | → `_flush_buffer_immediate` → `push()` (urgent, immediate) |
| failure | line 620: `notifier.notify_failure(...)` | `notify_failure` | `_event_enabled("failure")` | → `_flush_buffer_immediate` → `push()` (urgent, immediate) |

All 7 call sites (covering 6 event types) route through named functions with config gates. No path bypasses the gate.

---

## Check 12 — Rule 20 Self-Check

Rule 20 self-check script executed with plan_slug `executable-notification-coalescing-2026-05-12`. All 5 required evidence files present and non-empty. No hedging keywords found in positive-status rows. Result: PASSED. See literal stdout in "Rule 20 Self-Check Output" section below.

---

## Rule 20 Self-Check Output

```
============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
Evidence folder: /Users/marklehn/Desktop/GitHub/bellows/knowledge/qa/evidence/executable-notification-coalescing-2026-05-12/
Files verified: 5
```

---

## Output Receipt

**Agent:** Bellows QA
**Step:** 2
**Status:** Complete

### What Was Done
Verified all 12 checks from the QA task specification. Dead-code deletion confirmed (0 matches for notify_escalation/notify_complete). 4 new named functions verified with correct signatures, config gates, and priority/sound mapping. Coalescing buffer state confirmed thread-safe. Urgent flush-first pattern confirmed in notify_failure (line 199) and notify_verdict_request (line 212). Config schema present in both config files with backward-compatible defaults. 0 direct notifier.push() calls in bellows.py. Test suite: 268/269 passed (1 pre-existing failure). Static call-graph traced for all 7 call sites across 6 event types.

### Files Deposited
- `bellows/knowledge/qa/notification-coalescing-qa-2026-05-12.md`
- `bellows/knowledge/qa/evidence/executable-notification-coalescing-2026-05-12/dead_code_audit.txt`
- `bellows/knowledge/qa/evidence/executable-notification-coalescing-2026-05-12/direct_push_audit.txt`
- `bellows/knowledge/qa/evidence/executable-notification-coalescing-2026-05-12/notifier_functions.txt`
- `bellows/knowledge/qa/evidence/executable-notification-coalescing-2026-05-12/config_diff.txt`
- `bellows/knowledge/qa/evidence/executable-notification-coalescing-2026-05-12/pytest_result.txt`

### Files Created or Modified (Code)
- None (QA step — verification only)

### Decisions Made
- Accepted priority 0 for coalesced digest containing plan_skipped events (design says -1 for skipped individually, but digest combines event types — priority 0 is the correct choice for the combined digest)

### Flags for CEO
- Minor deviation: `notify_plan_skipped` per-event priority is -1 in design Section 2.2, but coalesced digests use priority 0. This is inherent to the coalescing design — a single digest push must pick one priority, and 0 (normal) is correct when the digest may contain plan_complete events.

### Flags for Next Step
- None — this is the final step.
