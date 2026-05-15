# Parallel Group Collection Bug — Diagnostic Findings
**Date:** 2026-04-16 | **Status:** Complete

---

## Q1 — `extract_parallel_group` logic

```python
def extract_parallel_group(filename: str) -> Optional[str]:
    match = re.match(r"^(parallel-\d+)-", filename)
    return match.group(1) if match else None
```

Regex: `^(parallel-\d+)-` — anchored at start, captures `parallel-` + one-or-more digits, requires trailing `-`.

| Filename | Match? | Returns |
|---|---|---|
| `parallel-1-executable-forge-evaluation-annotation-2026-04-16.md` | Yes | `"parallel-1"` |
| `parallel-1-executable-forge-budget-correction-2026-04-16.md` | Yes | `"parallel-1"` |

**Both return `"parallel-1"` — the same group identifier.** The extraction is correct.

---

## Q2 — `collect_group` logic

```python
def collect_group(self, decisions_path: str, group: str) -> list:
    files = os.listdir(decisions_path)
    result = []
    for fname in files:
        if fname.startswith(group + "-") and is_runnable_plan(fname):
            full_path = os.path.join(decisions_path, fname)
            if full_path not in self._seen:
                result.append(full_path)
    return result
```

Given `group = "parallel-1"`, it checks `fname.startswith("parallel-1-")`.

- `parallel-1-executable-forge-evaluation-annotation-2026-04-16.md` → startswith `"parallel-1-"` → **True** ✓
- `parallel-1-executable-forge-budget-correction-2026-04-16.md` → startswith `"parallel-1-"` → **True** ✓

The matching logic is correct. The function **will** find both siblings — but only if both exist on disk at the moment `os.listdir` is called, and neither is already in `self._seen`.

---

## Q3 — `_handle` dispatch path for parallel plans

```python
def _handle(self, path: str):
    filename = os.path.basename(path)
    if not is_runnable_plan(filename) or path in self._seen:
        return
    group = extract_parallel_group(filename)
    if group:
        decisions_path = str(pathlib.Path(path).parent)
        siblings = self.collect_group(decisions_path, group)
        all_paths = [p for p in siblings if p not in self._seen]
        [self._seen.add(p) for p in all_paths]
        print(f"Bellows: parallel group {group} — {len(all_paths)} plans")
        self.orchestrator.handle_parallel_group(all_paths)
```

(a) **Does it call `collect_group` to find ALL siblings before dispatching?** Yes — but `collect_group` is a snapshot of what is on disk *at that instant*. If sibling files haven't landed yet, they won't be found.

(b) **Does it add ALL siblings to `self._seen`?** Yes — it adds every path returned by `collect_group` to `_seen` atomically before dispatching.

(c) **Or does it process them one at a time as `on_created` fires for each file?** This is exactly what happens when there is a race — see Q4.

---

## Q4 — Root cause: confirmed race condition

**Hypothesis confirmed.** The exact sequence:

1. Forge calls `Filesystem:move_file` for **file A** (`parallel-1-executable-forge-evaluation-annotation-…`).
2. Watchdog fires `on_created` for file A → `_handle(file_A)` called.
3. `extract_parallel_group` → `"parallel-1"`.
4. `collect_group` calls `os.listdir` — **file B has not been moved into the directory yet**.
5. Result: `all_paths = [file_A]`. `_seen.add(file_A)`. `handle_parallel_group([file_A])` fires.
6. Log: `"parallel group parallel-1 — 1 plans"`. Thread started for file A.

7. Forge calls `Filesystem:move_file` for **file B** (`parallel-1-executable-forge-budget-correction-…`).
8. Watchdog fires `on_created` for file B → `_handle(file_B)` called.
9. Guard check: `file_B in self._seen`? → **No** (only file_A is in `_seen`). Passes guard.
10. `extract_parallel_group` → `"parallel-1"`.
11. `collect_group` calls `os.listdir` — file A is on disk but **already in `_seen`**, so filtered out. Only file B is returned.
12. Result: `all_paths = [file_B]`. `_seen.add(file_B)`. `handle_parallel_group([file_B])` fires.
13. Log: `"parallel group parallel-1 — 1 plans"`. Thread started for file B.

**Outcome:** Two independent "parallel group parallel-1 — 1 plans" dispatches instead of one "parallel group parallel-1 — 2 plans" dispatch. Plans execute as sequential singles in separate threads rather than as a collected parallel group.

This matches exactly the observed behavior from today's session.

---

## Q5 — Rescan path

`_rescan` iterates `os.listdir(decisions_path)` and calls `handler._handle(full_path)` for each file. Suppose both file A and file B are present:

1. `_handle(file_A)` called first.
2. `collect_group` finds both A and B (neither in `_seen`).
3. `all_paths = [file_A, file_B]`. Both added to `_seen`.
4. `handle_parallel_group([file_A, file_B])` — logs "parallel group parallel-1 — 2 plans". ✓
5. `_handle(file_B)` called next — `file_B in self._seen` → returns immediately. ✓

**The rescan path works correctly** when both files are present. The bug only manifests via the `on_created` / `on_modified` path when files arrive in rapid succession with a non-zero inter-arrival gap.

**Edge case:** If file A arrives just before the rescan tick, and the rescan finds only A (B not yet landed), the rescan has the same one-at-a-time race. However, the rescan runs again 30s later and by then B is on disk — but B won't be picked up because it was already added to `_seen` (or was already dispatched via `on_created`). This is a secondary issue but the `on_created` race is the primary cause in practice.

---

## Q6 — Fix options

### Option (a): Short sleep before `collect_group` in `_handle`

Add `time.sleep(N)` (e.g., 2–5 seconds) after detecting a parallel prefix, before calling `collect_group`.

- **Reliability:** Low-to-medium. If siblings always arrive within N seconds, works fine. Under load or slow filesystems, N may need to be larger. Race is reduced but not eliminated.
- **Complexity:** Minimal — one line.
- **Downside:** Adds latency to every parallel dispatch; race window is shrunk but not closed.

### Option (b): Defer parallel dispatch to next rescan tick (recommended)

When `_handle` detects a parallel prefix via `on_created`, do NOT dispatch immediately. Instead, record the group prefix in a `_pending_groups` set. `_rescan` checks `_pending_groups`, calls `collect_group` for each, and dispatches if the group is complete or the file was detected more than N seconds ago (a settle window).

- **Reliability:** High. Rescan is guaranteed to see all files deposited before it runs. With a 30s rescan interval, any parallel group deposited within 30s of each other will be collected together.
- **Complexity:** Moderate — add a `_pending_groups: dict[str, float]` (group → first-seen timestamp), check it in `_rescan`, dispatch and clear after settle window.
- **Downside:** Up to 30s latency before parallel dispatch begins. Acceptable since plans typically run for minutes.

### Option (c): Pending-group buffer with configurable settle window

Similar to (b) but use a background timer or a shorter re-check interval instead of the full rescan. After detecting a parallel file, schedule a collect attempt after `T` seconds (e.g., 5s). On the collect attempt, dispatch all found siblings.

- **Reliability:** High if T > inter-arrival gap. More tunable than (b).
- **Complexity:** Higher — requires a timer mechanism or a mini-scheduler loop.
- **Downside:** More moving parts; harder to reason about concurrency.

### Recommendation

**Option (b)** is the cleanest fix. It reuses the existing rescan infrastructure, eliminates the race entirely, and requires only:
1. A `_pending_groups: dict[str, float]` field on `PlanHandler`.
2. In `_handle` (on_created path): when `group` is detected and path not in `_seen`, add to `_pending_groups` with timestamp, but do **not** dispatch.
3. In `_rescan` (or at start of `_handle` called from rescan): for each group in `_pending_groups`, call `collect_group`, dispatch all found paths, remove from `_pending_groups`.

This ensures the rescan — which sees the full directory state — is always the dispatch trigger for parallel groups, eliminating the single-event race.
