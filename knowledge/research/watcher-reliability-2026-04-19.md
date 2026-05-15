# Filesystem Watcher Reliability — Diagnostic Findings

**Date:** 2026-04-19 | **Plan:** diagnostic-watcher-reliability-2026-04-19
**Purpose:** Characterize why Bellows's existing filesystem watcher misses Planner-originated filename changes.

---

## Q1 — Watchdog Event Subscriptions

### FileSystemEventHandler subclass: `PlanHandler`

```python
# bellows.py lines 435-484
435: class PlanHandler(FileSystemEventHandler):
436:     def __init__(self, orchestrator):
437:         super().__init__()
438:         self.orchestrator = orchestrator
439:         self._seen = set()
440:         self._pending_groups: dict = {}  # group prefix → first-seen timestamp (float)
441:
442:     def collect_group(self, decisions_path: str, group: str) -> list:
443:         files = os.listdir(decisions_path)
444:         result = []
445:         for fname in files:
446:             if fname.startswith(group + "-") and is_runnable_plan(fname):
447:                 full_path = os.path.join(decisions_path, fname)
448:                 if full_path not in self._seen:
449:                     result.append(full_path)
450:         return result
451:
452:     def _handle(self, path: str, from_rescan: bool = False):
453:         filename = os.path.basename(path)
454:         if not is_runnable_plan(filename) or path in self._seen:
455:             return
456:         group = extract_parallel_group(filename)
457:         if group:
458:             if not from_rescan:
459:                 # Defer parallel dispatch to the rescan settle-window check.
460:                 if group not in self._pending_groups:
461:                     self._pending_groups[group] = time.time()
462:                 return
463:             # from_rescan=True: if group is still pending, let the settle-window
464:             # check in _rescan handle it; don't dispatch prematurely.
465:             if group in self._pending_groups:
466:                 return
467:             decisions_path = str(pathlib.Path(path).parent)
468:             siblings = self.collect_group(decisions_path, group)
469:             all_paths = [p for p in siblings if p not in self._seen]
470:             [self._seen.add(p) for p in all_paths]
471:             print(f"Bellows: parallel group {group} — {len(all_paths)} plans")
472:             self.orchestrator.handle_parallel_group(all_paths)
473:         else:
474:             self._seen.add(path)
475:             print(f"Bellows: detected plan {filename}")
476:             self.orchestrator.handle_new_plan(path)
477:
478:     def on_created(self, event):
479:         if not event.is_directory:
480:             self._handle(event.src_path)
481:
482:     def on_modified(self, event):
483:         if not event.is_directory:
484:             self._handle(event.src_path)
```

**Overridden methods:** Exactly 2 — `on_created` (line 478) and `on_modified` (line 482).

**NOT overridden:** `on_moved`, `on_deleted`, `on_any_event`, `on_closed`.

**Event attributes read:** Both handlers read `event.is_directory` and `event.src_path` only. Neither reads `event.dest_path` or `event.event_type`.

### Observer.schedule() call

```python
# bellows.py lines 678-679
678:         for decisions_path in self.config.get("watched_projects", []):
679:             observer.schedule(handler, decisions_path, recursive=False)
```

Watches each project's `knowledge/decisions/` directory (from `config.json` `watched_projects` list). `recursive=False` — only the immediate directory, not subdirectories like `Done/`.

---

## Q2 — Rename Detection

**On macOS (FSEvents backend), a same-directory rename fires `on_moved`** with `event.src_path` = old name and `event.dest_path` = new name. The watchdog FSEvents observer synthesizes `MovedEvent` from the native FSEvents rename notification.

**`PlanHandler` does NOT override `on_moved`.** The default `FileSystemEventHandler.on_moved()` is a no-op — it does nothing.

This is the primary bug. When the Planner renames `verdict-pending-foo.md` → `executable-foo.md`:

1. FSEvents fires a move/rename notification
2. watchdog translates this to a `MovedEvent` and calls `handler.on_moved(event)`
3. `PlanHandler.on_moved` is inherited from `FileSystemEventHandler` — a no-op
4. **The event is silently dropped**

The handler methods that ARE overridden would handle the renamed file correctly if they fired:

```python
# bellows.py lines 478-484
478:     def on_created(self, event):
479:         if not event.is_directory:
480:             self._handle(event.src_path)
481:
482:     def on_modified(self, event):
483:         if not event.is_directory:
484:             self._handle(event.src_path)
```

If `on_created` fired for the destination `executable-foo.md`, `_handle` would:
- Call `is_runnable_plan("executable-foo.md")` → True (line 454)
- Check `path in self._seen` → False, because the old `verdict-pending-*` path was never added to `_seen` (`is_runnable_plan` rejects that prefix at line 425)
- Dispatch the plan (line 476)

But `on_created` does NOT fire for a rename — only `on_moved` does. On some macOS FSEvents configurations, a rename MAY additionally fire `on_modified` for the parent directory or the destination file, but this is unreliable and version-dependent. The only reliable event is `on_moved`.

---

## Q3 — Rescan Loop

### Full function body

```python
# bellows.py lines 538-559
538:     def _rescan(self, handler):
539:         # Check for resolved verdicts
540:         self._consume_verdicts()
541:         # Dispatch pending parallel groups that have passed the 5-second settle window.
542:         now = time.time()
543:         for group in list(handler._pending_groups.keys()):
544:             if now - handler._pending_groups[group] > 5:
545:                 for decisions_path in self.config.get("watched_projects", []):
546:                     if os.path.isdir(decisions_path):
547:                         siblings = handler.collect_group(decisions_path, group)
548:                         if siblings:
549:                             all_paths = [p for p in siblings if p not in handler._seen]
550:                             [handler._seen.add(p) for p in all_paths]
551:                             print(f"Bellows: parallel group {group} — {len(all_paths)} plans (deferred dispatch)")
552:                             self.handle_parallel_group(all_paths)
553:                 del handler._pending_groups[group]
554:         for decisions_path in self.config.get("watched_projects", []):
555:             if os.path.isdir(decisions_path):
556:                 for fname in os.listdir(decisions_path):
557:                     if is_runnable_plan(fname):
558:                         full_path = os.path.join(decisions_path, fname)
559:                         handler._handle(full_path, from_rescan=True)
```

**Trigger:** Timer in the main loop, every 30 seconds:

```python
# bellows.py lines 698-706
698:         rescan_interval = 30
699:         last_rescan = time.time()
700:         last_heartbeat = time.time()
701:         try:
702:             while True:
703:                 time.sleep(1)
704:                 if time.time() - last_rescan >= rescan_interval:
705:                     self._rescan(handler)
706:                     last_rescan = time.time()
```

**What it scans:** All directories in `config["watched_projects"]` (same paths the Observer watches).

**What it does with files:** For each file passing `is_runnable_plan(fname)`, constructs the full path and calls `handler._handle(full_path, from_rescan=True)`.

**Can the rescan catch a `verdict-pending-*` → `executable-*` rename?**

Yes, in theory. Tracing the path:
1. `os.listdir(decisions_path)` at line 556 — lists the directory, finds `executable-foo.md`
2. `is_runnable_plan("executable-foo.md")` at line 557 — returns True
3. `handler._handle(full_path, from_rescan=True)` at line 559
4. Inside `_handle`: `is_runnable_plan(filename)` → True; `path in self._seen` → False (the old `verdict-pending-*` path was never in `_seen`)
5. Non-parallel → `self._seen.add(path)` + `self.orchestrator.handle_new_plan(path)` at lines 474-476

**The rescan SHOULD pick up the renamed file within 30 seconds.** The `_seen` set stores full absolute paths, and the new `executable-*` path differs from the old `verdict-pending-*` path, so it won't be filtered out.

**Why it may have failed in the 2026-04-18 incident:** The most likely explanation is that `_rescan` was blocked by `_consume_verdicts()` (line 540), which is called first. If a `notifier.push()` call inside `_consume_verdicts` hung (pre-timeout-fix code running on a process that was never restarted after the 2026-04-16 notifier timeout fix), the directory scan at lines 554-559 would never execute. Multiple BACKLOG entries note "REMINDER: restart Bellows manually to load fixes" — if the running process was still on pre-2026-04-16 code, `requests.post()` calls in the notifier had no timeout and could block indefinitely.

A secondary possibility: if the renamed file was picked up but `run_plan()` restarted from Step 1 (because step state doesn't persist — BACKLOG #5), the user may have perceived this as "not detected" when the actual issue was "detected but wrong step."

---

## Q4 — Heartbeat Mechanism

```python
# bellows.py lines 707-709
707:                 if time.time() - last_heartbeat >= 60:
708:                     print(f"Bellows: heartbeat — {datetime.now().strftime('%H:%M:%S')}")
709:                     last_heartbeat = time.time()
```

**The heartbeat is a pure print statement.** It does NOT trigger a rescan, inbox poll, filesystem operation, or any other side effect. It prints the current time every 60 seconds as a liveness canary.

The rescan is triggered by a SEPARATE timer on the same main loop (30-second interval, lines 704-706). The heartbeat and rescan timers are independent — neither triggers the other.

**BACKLOG's speculation — "existing heartbeat was thought to function as a file-scanner refresh" — is confirmed incorrect.** The heartbeat is exclusively a liveness indicator. However, the rescan IS running on its own 30s timer, so the BACKLOG's implied conclusion ("the scanner doesn't run between heartbeats") is also incorrect — the scanner runs twice per heartbeat interval.

---

## Q5 — Startup Scan

```python
# bellows.py lines 690-697
690:         # Scan for plans already on disk at startup
691:         for decisions_path in self.config.get("watched_projects", []):
692:             if os.path.isdir(decisions_path):
693:                 for fname in os.listdir(decisions_path):
694:                     if is_runnable_plan(fname):
695:                         full_path = os.path.join(decisions_path, fname)
696:                         print(f"Bellows: startup scan found {fname}")
697:                         handler._handle(full_path)
```

**The startup scan lists every file in every watched directory** and passes each through `is_runnable_plan()` → `handler._handle()`. This runs once, at boot, after the Observer is scheduled (line 679-680) and after a 3-second auth settle pause (line 689).

**When Bellows is restarted after a Planner rename:** The startup scan handles the renamed file. The `_seen` set is empty at boot (line 439: `self._seen = set()`), so all runnable plans are dispatched. This confirms the workaround: restarting Bellows forces a full directory scan with a clean `_seen` set.

**Why restart works but in-flight detection fails:** The in-flight watchdog missed the rename event because `on_moved` isn't overridden (Q2). The 30s rescan should have caught it as a fallback (Q3), but may have been blocked by pre-timeout-fix notifier calls or by the BACKLOG #5 step-state issue masking a successful detection as a failure.

---

## Root Cause Summary

The primary bug is that `PlanHandler` overrides only `on_created` and `on_modified` but NOT `on_moved`. On macOS (FSEvents), a same-directory rename fires `on_moved` exclusively — it does not fire `on_created` for the destination file. When the Planner renames `verdict-pending-*` → `executable-*`, the event is delivered to the default no-op `on_moved` handler and silently dropped. The 30-second rescan loop (`_rescan`) should catch the renamed file as a fallback since it does a full `os.listdir` scan, but the rescan calls `_consume_verdicts()` first, which may have been blocked by pre-timeout-fix notifier calls in the 2026-04-18 incident. The heartbeat is a pure print statement — not a rescan trigger — confirming the BACKLOG's speculation was incorrect.

---

## Fix Options

**Option A — Add `on_moved` handler (minimal, recommended)**

Add an `on_moved` override to `PlanHandler` that calls `self._handle(event.dest_path)`. This makes the watchdog aware of renames. The destination path will be checked by `is_runnable_plan` and the `_seen` set as usual. ~3 lines of code.

```python
def on_moved(self, event):
    if not event.is_directory:
        self._handle(event.dest_path)
```

Pros: Directly fixes the root cause. Renames are detected in real-time, no 30s delay. Minimal change.
Cons: Does not address BACKLOG #5 (step state persistence) — the renamed file will still restart from Step 1 unless the proper verdict flow is used.

**Option B — Shorten rescan interval + Option A**

Reduce `rescan_interval` from 30 to 10 seconds. Combined with Option A, this provides defense-in-depth: watchdog catches renames in real-time, rescan catches anything the watchdog misses (e.g., files dropped by network sync or manual copy that don't fire OS events). ~4 lines changed.

Pros: Belt-and-suspenders approach. Catches edge cases where FSEvents coalesces or drops events.
Cons: Slightly more I/O from `os.listdir` every 10s (negligible for small directories).

**Option C — Redirect to verdict flow instead of direct rename**

Document that the correct resume protocol is depositing a verdict file in `verdicts/resolved/`, NOT renaming the plan file directly. This is already how `_consume_verdicts` works. The BACKLOG incident used the wrong protocol.

Pros: No code change needed — the infrastructure already works. The 30s rescan calls `_consume_verdicts` which handles the full resume lifecycle including step state.
Cons: Requires Planner discipline, not enforceable by code. Does not fix the real `on_moved` gap for cases where files ARE legitimately renamed (e.g., new plans dropped by filesystem sync).

**Recommended approach:** Option A (immediate fix) + Option C (protocol documentation). Option B is a nice-to-have but not strictly necessary if `on_moved` is handling renames.

---

## Output Receipt
**Agent:** Bellows Developer
**Step:** 1
**Status:** Complete

### What Was Done
Read bellows.py end-to-end and traced all five code paths requested. Identified the root cause: `PlanHandler` does not override `on_moved`, so macOS FSEvents rename events are silently dropped. Confirmed the 30s rescan should catch renames as fallback but may have been blocked by pre-timeout-fix notifier calls in the 2026-04-18 incident. Confirmed heartbeat is a pure print, not a rescan trigger. Ranked three fix options.

### Files Deposited
- `bellows/knowledge/research/watcher-reliability-2026-04-19.md` — this findings file

### Files Created or Modified (Code)
- None (read-only investigation)

### Decisions Made
- None (diagnostic only)

### Flags for CEO
- None

### Flags for Next Step
- None — this diagnostic does not have a Step 2
