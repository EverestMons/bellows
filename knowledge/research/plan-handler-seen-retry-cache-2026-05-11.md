# PlanHandler._seen Retry Cache Diagnostic — Findings

**Date:** 2026-05-11
**Source SHA:** `4d57fd332c3a7009a9ae6171f31e881c68216350`
**bellows.py:** 1180 LOC at time of read

---

## Q1 — Current state map

Every `_seen` reference in `bellows.py`:

| Line | Operation | Function | Purpose |
|------|-----------|----------|---------|
| 782 | declare | `PlanHandler.__init__` | Initializes `_seen` as empty `set()` |
| 791 | read (filter) | `PlanHandler.collect_group` | Excludes previously-seen paths from parallel group collection |
| 804 | read | `PlanHandler._handle` | Checks if non-dispatchable `.md` file was already logged as skipped |
| 806 | add | `PlanHandler._handle` | Marks non-dispatchable `.md` file as seen (prevents duplicate skip warnings) |
| 808 | read | `PlanHandler._handle` | Guards against double-dispatch of runnable plans |
| 824 | add (bulk) | `PlanHandler._handle` | Marks all parallel group plan paths as seen before group dispatch |
| 828 | add | `PlanHandler._handle` | Marks single plan path as seen before dispatch |
| 919 | read (filter) | `Bellows._rescan` | Filters previously-seen paths during deferred parallel group dispatch |
| 920 | add (bulk) | `Bellows._rescan` | Marks deferred parallel group plans as seen after dispatch |
| 929 | indirect | `Bellows._rescan` | Calls `handler._handle(full_path, from_rescan=True)` which reads/adds `_seen` |

**BACKLOG line-number drift:** The BACKLOG entry cites lines 677, 686-687, 696, 807-808. All references are still present but have shifted due to code growth since the entry was written (2026-05-06):

| BACKLOG cited | Current line | Reference |
|---------------|-------------|-----------|
| 677 | 782 | `self._seen = set()` declaration |
| 686-687 | 791 | `_seen` filter in `collect_group` |
| 696 | 808 | `_seen` check in `_handle` |
| 807-808 | 919-920 | `_seen` add in `_rescan` |

**Total references:** 10 (including 1 indirect via `_handle` delegation at line 929).

---

## Q2 — Race-window characterization

The dispatch-window race exists as the BACKLOG entry asserts. Step-by-step trace:

1. **FSEvent arrives** — `PlanHandler.on_created`/`on_modified`/`on_moved` (lines 832-842) calls `self._handle(path)`.
2. **Line 808** — `if path in self._seen: return` — guard check passes (path not yet seen).
3. **Line 828** — `self._seen.add(path)` — path marked as seen **in the watchdog thread**.
4. **Line 830** — `self.orchestrator.handle_new_plan(path)` — calls `Bellows.handle_new_plan`.
5. **Line 896** — `threading.Thread(target=self._run_tracked, args=(path,), daemon=True)` — daemon thread spawned.
6. **Line 898** — `time.sleep(2)` — 2-second stagger delay.
7. **Line 899** — `handle_new_plan` prints and **returns to the watchdog thread**. The plan file is still at its original path.
8. **(daemon thread)** Line 868 — `run_plan(path, ...)` begins.
9. **(daemon thread)** Line 282-284 — `if not plan_filename.startswith("in-progress-"): shutil.move(plan_path, inprogress_path)` — **this is when the file exits `is_runnable_plan() == True`** (line 768 returns False for `in-progress-` prefix).

**Race window:** Between step 3 (line 828, `_seen.add`) and step 9 (line 283, `shutil.move`). During this window:
- The plan file is still at its original path on disk.
- `is_runnable_plan(filename)` returns `True` for that filename.
- `_rescan` (line 908, runs every 30s from the main thread) calls `handler._handle(full_path, from_rescan=True)` at line 929, which would re-dispatch the plan.
- **`_seen` is the only guard** that prevents double-dispatch during this window.

The window duration is at minimum 2 seconds (the `time.sleep(2)` stagger at line 898), plus thread scheduling latency and `run_plan` setup (~5-10 lines of synchronous work before `shutil.move`).

**Confirmation:** The race window is real and load-bearing. `_seen` is the sole dispatch-window guard.

---

## Q3 — Lifecycle terminal events and `cleanup_slug` call sites

Every `cleanup_slug` computation and cleanup-for-slug call site:

| Line | Function | Lifecycle event | Current cleanup operation |
|------|----------|----------------|--------------------------|
| 527 | `run_plan` | Auto-close (gates pass + `auto_close: true`) | `_cleanup_verdicts_for_slug(verdict.slug_from_path(plan_path))` — removes pending verdict-request files, then moves plan to `Done/` (line 529) and deletes shadow (line 530) |
| 999 | `_consume_verdicts` | Slug computation (shared) | `cleanup_slug = verdict.slug_from_path(original_name)` — computed once, used at lines 1027 and 1047 |
| 1027 | `_consume_verdicts` | Continue-to-done (final-step continue verdict) | `_cleanup_verdicts_for_slug(cleanup_slug)` — removes pending verdict-request files, then moves plan to `Done/` (line 1028) and deletes shadow (line 1029) |
| 1047 | `_consume_verdicts` | Halt (stop verdict) | `_cleanup_verdicts_for_slug(cleanup_slug)` — removes pending verdict-request files, then moves plan to `halted-` prefix (line 1048) and deletes shadow (line 1049) |

**BACKLOG assertion check:** "three call sites in `_consume_verdicts` (continue-to-done, halt) and in `run_plan` (auto-close)." The count is correct (3 total) but the distribution phrasing is ambiguous. Precise distribution: **2 in `_consume_verdicts`** (continue-to-done at line 1027, halt at line 1047) + **1 in `run_plan`** (auto-close at line 527) = **3 total.** The BACKLOG entry's "three call sites" count is accurate.

**Note:** The continue-to-next-step path in `_consume_verdicts` (lines 1033-1041) does NOT call `_cleanup_verdicts_for_slug` because it is not a terminal event — the plan continues execution.

---

## Q4 — Plumbing option (A): pass `handler` reference into `Bellows` and stash on `self`

**(a) PlanHandler construction:** Line 1131 inside `Bellows.start()`: `handler = PlanHandler(self)`. Arguments: `orchestrator` (the `Bellows` instance). `handler` is a local variable — not stashed on `self`.

**(b) Arguments received:** Single argument: `orchestrator` (the `Bellows` instance), stored as `self.orchestrator` (line 781).

**(c) Does Bellows have a reference to PlanHandler today?** No. `handler` is created as a local in `start()` and passed to `_rescan(handler)` as a parameter (line 1166). No `self.handler` exists.

**(d) Methods that would need `self.handler._seen.discard(...)`:**

| Site | Function | What changes |
|------|----------|-------------|
| Line 1131 | `Bellows.start()` | Add `self.handler = handler` after construction |
| Line 1027 | `_consume_verdicts` continue-to-done | Add `self.handler._seen.discard(slug)` |
| Line 1047 | `_consume_verdicts` halt | Add `self.handler._seen.discard(slug)` |
| Line 527 | `run_plan` auto-close | **Problem:** `run_plan` is a module-level function. Needs access to `handler._seen`. Requires either (i) passing `bellows_instance` as parameter, then `bellows_instance.handler._seen.discard(slug)`, or (ii) making `run_plan` a method on `Bellows`. |
| Line 868 | `Bellows._run_tracked` | Update call: `run_plan(path, self.config, self.response_server, bellows=self, ...)` |
| Lines 782, 791, 804, 806, 808, 824, 828, 919, 920 | Various | Re-key from full path to slug (separate from plumbing — required by both options) |

**LOC delta estimate:** ~18-22 LOC (1 stash + 2 discards in `_consume_verdicts` + 2 signature/call-site changes for `run_plan` + ~10 re-keying changes + 1 declaration adjustment). Creates bidirectional coupling: PlanHandler holds `self.orchestrator` (Bellows), Bellows holds `self.handler` (PlanHandler).

---

## Q5 — Plumbing option (B): move `_seen` ownership onto `Bellows`

**(a) All PlanHandler._seen access sites that would change:**

| Current line | Current code | New code |
|-------------|-------------|----------|
| 782 | `self._seen = set()` | Remove from PlanHandler; add `self._seen = set()` to `Bellows.__init__` (after line 850) |
| 791 | `if full_path not in self._seen` | `if full_path not in self.orchestrator._seen` |
| 804 | `and path not in self._seen` | `and path not in self.orchestrator._seen` |
| 806 | `self._seen.add(path)` | `self.orchestrator._seen.add(path)` |
| 808 | `if path in self._seen` | `if path in self.orchestrator._seen` |
| 824 | `[self._seen.add(p) for p in all_paths]` | `[self.orchestrator._seen.add(p) for p in all_paths]` |
| 828 | `self._seen.add(path)` | `self.orchestrator._seen.add(path)` |
| 919 | `if p not in handler._seen` | `if p not in self._seen` |
| 920 | `handler._seen.add(p)` | `self._seen.add(p)` |

**(b) Orchestrator-side reference to `Bellows` in `PlanHandler`:** Yes — `self.orchestrator` (line 781). Established at construction: `PlanHandler(self)` where `self` is the `Bellows` instance. This reference already exists and is used for `self.orchestrator.handle_new_plan(path)` (line 830) and `self.orchestrator.handle_parallel_group(all_paths)` (line 826). No new coupling required.

**(c) Threading-safety concerns:**

Mutation sources for `_seen` under option (B):
- **Watchdog thread:** `PlanHandler._handle` → `self.orchestrator._seen.add(...)` (lines 806, 824, 828)
- **Main thread:** `Bellows._rescan` → `self._seen.add(...)` (line 920); `Bellows._consume_verdicts` → `self._seen.discard(...)` (new)
- **Daemon threads:** `run_plan` auto-close → `bellows._seen.discard(...)` (new, requires plumbing)

Python's GIL makes `set.add()` and `set.discard()` atomic at the bytecode level. No lock is needed. This is **identical to the current threading profile** — `_seen` is already mutated from the watchdog thread (PlanHandler) and the main thread (_rescan via `handler._seen`). Option (B) adds daemon-thread mutation only at the auto-close terminal event, which is a safe atomic `discard()`.

**Surgical edit sites:**

| Site | Change |
|------|--------|
| `Bellows.__init__` (after line 850) | Add `self._seen = set()` |
| `PlanHandler.__init__` line 782 | Remove `self._seen = set()` |
| Lines 791, 804, 806, 808, 824, 828 | `self._seen` → `self.orchestrator._seen` (6 sites in PlanHandler) |
| Lines 919-920 | `handler._seen` → `self._seen` (2 sites in Bellows._rescan) |
| Line 1027 | Add `self._seen.discard(slug)` (continue-to-done) |
| Line 1047 | Add `self._seen.discard(slug)` (halt) |
| Line 527 | Add `bellows._seen.discard(slug)` (auto-close — requires plumbing) |
| `run_plan` signature (line 227) | Add `bellows=None` parameter |
| `_run_tracked` call (line 868) | Pass `bellows=self` |

**LOC delta estimate:** ~15-17 LOC (1 add to Bellows.__init__, 1 remove from PlanHandler.__init__, 6 reference changes in PlanHandler, 2 reference changes in _rescan, 2 discards in _consume_verdicts, 2 signature/call-site changes for run_plan, plus ~10 re-keying changes from path→slug shared with option A).

---

## Q6 — Recommendation

**Recommended: Option (B) — move `_seen` ownership onto `Bellows`.**

**Axis 1 — Surgical scope:** Option (B) is marginally smaller (~15-17 LOC vs ~18-22 LOC). Both touch only `bellows.py`. Option (B) has more individual line edits (8 PlanHandler reference changes) but they are mechanical find-and-replace; option (A) introduces a new structural member (`self.handler`) and the same `run_plan` plumbing.

**Axis 2 — Threading safety:** Identical between options. Both options share the same mutation profile: watchdog thread (add), main thread (add + discard), daemon threads (discard at auto-close). Python GIL makes `set.add()`/`set.discard()` bytecode-atomic. No lock is needed in either option.

**Axis 3 — Layer 1 invariant fit:** Option (B) is strictly better. Lifecycle terminal events that must clear `_seen` (Done/, halted-, auto-close) are all Bellows-orchestrator-side operations inside `_consume_verdicts` and `run_plan`. Placing `_seen` on the orchestrator aligns data ownership with the lifecycle code that mutates it. PlanHandler continues to access `_seen` through its existing unidirectional `self.orchestrator` reference — no new coupling is introduced. Option (A) would create a **bidirectional** Bellows <-> PlanHandler coupling (`self.orchestrator` + `self.handler`), blurring the event-router/orchestrator separation that the current design maintains.

**Shared plumbing constraint (both options):** The `run_plan` auto-close path (line 527) is a module-level function that needs access to `_seen` regardless of which object owns it. The minimal plumbing is: add `bellows=None` parameter to `run_plan`, pass `self` from `_run_tracked` (line 868), call `bellows._seen.discard(slug)` at line 527. This is 3 LOC in either option.

---

## Prompt feedback

No prompt feedback to report. The diagnostic was well-scoped: single-file code trace with focused empirical questions. The line-number starting set from the BACKLOG entry was stale (code has grown ~100 lines since the entry was written 2026-05-06) but the references were easily relocated via grep. Q1-Q6 structure provided a natural investigation order with no wasted reads.
