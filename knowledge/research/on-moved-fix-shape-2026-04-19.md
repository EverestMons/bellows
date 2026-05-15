# on_moved Fix Shape Characterization — 2026-04-19

**Diagnostic:** in-progress-diagnostic-on-moved-fix-shape-2026-04-19.md
**Date:** 2026-04-19
**Investigator:** Systems Analyst (Claude Code)

---

## 1. PlanHandler's Watched-Directory Reference

**PlanHandler class:** bellows.py lines 435–488.

**Attributes:**
- `self.orchestrator` — the Bellows instance (set at L438)
- `self._seen` — set of already-dispatched paths (L439)
- `self._pending_groups` — dict for parallel group settle-window tracking (L440)

**(a) No direct watched-directory attribute.** PlanHandler has no `self.watched_dir`, `self.decisions_path`, or similar attribute.

**(b) Instantiation context:** PlanHandler is created at L681 via `handler = PlanHandler(self)`, where `self` is the Bellows instance. The Bellows instance holds `self.config` (L492), which contains the `watched_projects` list. Therefore, at `on_moved` call time, the handler can access watched directories via:

```python
self.orchestrator.config.get("watched_projects", [])
```

**(c) No module-level or class-level constant** identifies the top-level watched directory. The watched paths exist only in the config dict loaded from config.json at startup (L720). The config paths are absolute (e.g., `/Users/marklehn/Desktop/GitHub/bellows/knowledge/decisions`).

**Observer scheduling (L682–683):**
```python
for decisions_path in self.config.get("watched_projects", []):
    observer.schedule(handler, decisions_path, recursive=False)
```
The same path strings from config are passed to both observer.schedule and are available via the orchestrator reference.

---

## 2. Exact Guard Condition Shape

**Proposed guard (inserted at the start of `on_moved`, L486–488):**

```python
def on_moved(self, event):
    if not event.is_directory:
        # Guard: reject moves whose destination is a subdirectory (e.g., Done/)
        dest_parent = str(Path(event.dest_path).parent)
        watched = self.orchestrator.config.get("watched_projects", [])
        if dest_parent not in watched:
            return
        self._handle(event.dest_path)
```

**Normalization:** The config stores absolute paths without trailing slashes. Watchdog constructs event paths using the observed directory as a prefix, which matches the path passed to `observer.schedule`. Both come from the same config source, so `str(Path(...).parent)` comparison should be exact. For extra safety, both sides could use `Path(...).resolve()` to handle symlinks, but the current codebase does not use symlinks for watched directories, so this is optional.

**Should the guard also check `src_path`?** No. The BACKLOG #4 case (same-directory rename) has both src and dest in the top-level directory:
- src: `/some/decisions/verdict-pending-foo.md`
- dest: `/some/decisions/executable-foo.md`
- dest_parent = `/some/decisions` → in watched_projects → dispatched ✓

The new bug (move to Done/) has dest in a subdirectory:
- dest: `/some/decisions/Done/diagnostic-foo.md`
- dest_parent = `/some/decisions/Done` → NOT in watched_projects → rejected ✓

The guard does NOT block the BACKLOG #4 case. No src_path check needed.

---

## 3. on_created Parallel Path Check

**on_created:** bellows.py lines 478–480.

```python
def on_created(self, event):
    if not event.is_directory:
        self._handle(event.src_path)
```

**Subdirectory vulnerability:** Theoretically yes, same shape as on_moved. If watchdog emits an on_created event for a file inside Done/ (e.g., because macOS FSEvents is tree-based and `recursive=False` is advisory), `_handle` would be called with a path inside Done/. `is_runnable_plan` checks only the filename, so a file named `diagnostic-*.md` inside Done/ would pass.

**Practical risk: LOW.** Files reach Done/ via `shutil.move()`, which triggers on_moved, not on_created. The Planner writes new plans to the top-level directory. A file would only appear in Done/ via creation if someone manually created it there, or if the move implementation on macOS uses create+delete rather than rename. The observed incident was on_moved, not on_created.

**on_modified (L482–484):** Same vulnerability shape — calls `_handle(event.src_path)` without directory filtering. Lower risk than on_created since modifications to files already in Done/ would need to match `is_runnable_plan`, and lifecycle-prefixed files (`in-progress-`, `verdict-pending-`, `halted-`) are rejected. But a file in Done/ with a bare `diagnostic-` or `executable-` prefix could trigger.

**Fix scope recommendation:** If fixing on_moved only (Candidate A), note that on_created and on_modified remain theoretically vulnerable. If the fix is applied in `_handle` instead (Candidate B), all three handlers are covered simultaneously.

---

## 4. Other Dispatch Paths That Could Reach Done/

| # | Path | Line(s) | Recursive? | Can reach Done/? |
|---|------|---------|-----------|-----------------|
| 1 | `on_created` | 478–480 | via watchdog (recursive=False) | Theoretically yes (see §3) |
| 2 | `on_modified` | 482–484 | via watchdog (recursive=False) | Theoretically yes (see §3) |
| 3 | `on_moved` | 486–488 | via watchdog (recursive=False) | **YES — confirmed bug** |
| 4 | Startup scan | 696–701 | `os.listdir(decisions_path)` — non-recursive | **No** — only top-level |
| 5 | `_rescan` | 558–563 | `os.listdir(decisions_path)` — non-recursive | **No** — only top-level |
| 6 | `_consume_verdicts` | 565–676 | `os.listdir(decisions_path)` at L616 | **No** — constructs paths from top-level listing |
| 7 | `_check_queue_drain` | 508–527 | `os.listdir(d)` | **No** — counting only, no dispatch |
| 8 | `collect_group` | 442–450 | `os.listdir(decisions_path)` | **No** — called from `_handle`/`_rescan` with top-level path |

**Summary:** Non-watchdog paths (startup scan, _rescan, _consume_verdicts) are structurally safe because they use non-recursive `os.listdir`. Only watchdog event handlers (on_created, on_modified, on_moved) can receive subdirectory paths, dependent on platform FSEvents behavior. The observed incident was through on_moved.

**Is Candidate A (fix on_moved only) structurally sufficient?** It fixes the confirmed trigger. The on_created and on_modified paths are theoretically vulnerable but have not been observed to fire for Done/ subdirectory files. Candidate B (guard in `_handle` or `is_runnable_plan`) would provide belt-and-suspenders protection against all three watchdog handlers. Since the guard logic is the same either way, placing it in `_handle` (or even in `on_moved` + `on_created` + `on_modified`) has minimal additional cost.

---

## 5. Existing Tests for on_moved

### BACKLOG #4 tests (shipped 2026-04-19)

**Test 1:** `test_on_moved_dispatches_for_non_directory_event` (tests/test_bellows.py L1020–1033)
- Verifies: on_moved calls `_handle(event.dest_path)` for non-directory events
- Fixture: MagicMock orchestrator, patches `handler._handle`
- dest_path: `"/some/decisions/executable-foo.md"`
- **Impact of guard:** This test patches `_handle`, so the guard in `on_moved` executes before the patched method. `MagicMock().config.get("watched_projects", [])` returns a MagicMock (not a list), and `str(Path(dest_path).parent) not in <MagicMock>` evaluates to **True** (MagicMock.\_\_contains\_\_ returns False). The guard would return early, and `mock_handle.assert_called_once_with(...)` would **FAIL**. **This test must be updated** to set `mock_orch.config = {"watched_projects": ["/some/decisions"]}`.

**Test 2:** `test_on_moved_ignores_directory_events` (tests/test_bellows.py L1036–1049)
- Verifies: on_moved does NOT call `_handle` for directory events (`event.is_directory = True`)
- **Impact of guard:** None. The `is_directory` check at L487 fires before the guard. This test **passes unchanged**.

### Other PlanHandler tests

- `test_rescan_preserves_seen` (L86): Tests _rescan, not on_moved. Unaffected.
- `test_handle_parallel_from_watchdog_adds_pending_not_dispatched` (L754): Tests `_handle`, not on_moved directly. Unaffected.
- `test_nonparallel_plan_dispatches_immediately_from_handle` (L819): Tests `_handle` directly. Unaffected.

---

## 6. Test-Surface Proposal

### Minimum tests to verify the guard + no BACKLOG #4 regression

**(a) `test_on_moved_dispatches_for_top_level_dest`**
- Fixture: MagicMock orchestrator with `config = {"watched_projects": ["/proj/knowledge/decisions"]}`. Create event with `dest_path = "/proj/knowledge/decisions/executable-foo.md"`, `is_directory = False`.
- Assert: `_handle` called once with `dest_path`.
- Purpose: Confirms legitimate plan deposits (temp-then-move per Rule 24) are dispatched.

**(b) `test_on_moved_rejects_subdirectory_dest`**
- Fixture: Same orchestrator config. Create event with `dest_path = "/proj/knowledge/decisions/Done/diagnostic-foo.md"`, `is_directory = False`.
- Assert: `_handle` NOT called.
- Purpose: Directly tests the re-run cascade fix.

**(c) `test_on_moved_dispatches_same_directory_rename`**
- Fixture: Same orchestrator config. Create event with `src_path = "/proj/knowledge/decisions/verdict-pending-foo.md"`, `dest_path = "/proj/knowledge/decisions/executable-foo.md"`, `is_directory = False`.
- Assert: `_handle` called once with `dest_path`.
- Purpose: Regression guard for BACKLOG #4 (same-directory rename).

**(d) `test_on_moved_ignores_directory_events`**
- Already exists (L1036). No changes needed.

### Existing test updates required

`test_on_moved_dispatches_for_non_directory_event` (L1020) must be updated to provide `mock_orch.config = {"watched_projects": ["/some/decisions"]}`. After update, it becomes functionally equivalent to test (a) above and can be merged/replaced.

---

## 7. Cheap Sanity Check on Hypothesis

**Is Candidate A (fix on_moved only) sufficient to stop the re-run cascade?** Yes, for the observed failure mode. The DB evidence conclusively shows the re-run was triggered by on_moved (the only code path that could produce a `decisions/Done/in-progress-*` plan_path). Non-watchdog paths (startup scan, _rescan) are structurally safe due to non-recursive os.listdir.

**Single strongest evidence FOR:** DB row 333 records `plan_path = decisions/Done/in-progress-diagnostic-*` — the re-run was claimed from inside Done/, which only on_moved could deliver to `_handle` (startup scan and _rescan use non-recursive os.listdir).

**Single strongest evidence AGAINST:** on_created and on_modified share the same vulnerability shape (no subdirectory guard). If macOS FSEvents ever emits those events for Done/ files (unlikely but platform-dependent), the bug would recur through a different handler. Placing the guard in `_handle` instead of `on_moved` alone would eliminate this class of bug entirely at the cost of one extra parent-directory check per `_handle` invocation.

---

## Implementation Ready

The executable plan needs to specify:

1. **Guard insertion point:** bellows.py L486–488 (`on_moved` method), or L452 (start of `_handle` method — broader protection).
2. **Exact guard condition (on_moved approach):**
   ```python
   dest_parent = str(Path(event.dest_path).parent)
   watched = self.orchestrator.config.get("watched_projects", [])
   if dest_parent not in watched:
       return
   ```
3. **Alternative guard condition (_handle approach):**
   ```python
   path_parent = str(Path(path).parent)
   watched = self.orchestrator.config.get("watched_projects", [])
   if path_parent not in watched:
       return
   ```
4. **Test file:** tests/test_bellows.py — update existing test at L1020 and add 2 new tests (subdirectory rejection + same-directory rename regression).
5. **Existing test breakage:** `test_on_moved_dispatches_for_non_directory_event` (L1020) must be updated to provide `mock_orch.config` with a valid `watched_projects` list matching the test's dest_path parent.
