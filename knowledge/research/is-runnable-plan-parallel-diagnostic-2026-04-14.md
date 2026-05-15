# Diagnostic: is_runnable_plan Parallel Prefix Bug
**Date:** 2026-04-14 | **Status:** Complete

---

## (1) is_runnable_plan — Exact Implementation

**File:** `bellows/bellows.py`, lines 221–226

```python
def is_runnable_plan(filename: str) -> bool:
    return (
        (filename.startswith("executable-") or filename.startswith("diagnostic-"))
        and not filename.startswith("in-progress-")
        and filename.endswith(".md")
    )
```

The function requires the filename to start with `executable-` or `diagnostic-` (and end with `.md`, and not start with `in-progress-`). There is no allowance for the `parallel-N-` prefix.

---

## (2) Test Results for 6 Filenames

Literal output of the python3 test command:

```
'executable-foo-2026-04-14.md' -> True
'diagnostic-bar-2026-04-14.md' -> True
'parallel-1-executable-foo-2026-04-14.md' -> False
'parallel-2-diagnostic-bar-2026-04-14.md' -> False
'in-progress-executable-foo-2026-04-14.md' -> False
'foo.md' -> False
```

Both parallel-prefixed filenames (`parallel-1-executable-foo-2026-04-14.md` and `parallel-2-diagnostic-bar-2026-04-14.md`) return **False** — the bug is confirmed at the function level.

---

## (3) All Call Sites of is_runnable_plan

`grep -n "is_runnable_plan" bellows/bellows.py` output:

```
221:def is_runnable_plan(filename: str) -> bool:
244:            if fname.startswith(group + "-") and is_runnable_plan(fname):
252:        if not is_runnable_plan(filename) or path in self._seen:
300:                pending.extend([f for f in os.listdir(d) if is_runnable_plan(f)])
322:                    if is_runnable_plan(fname):
350:                    if is_runnable_plan(fname):
```

**Context for each:**

**Line 244** (inside `collect_group`):
```python
        for fname in files:
            if fname.startswith(group + "-") and is_runnable_plan(fname):  # ← called on full parallel filename
                full_path = os.path.join(decisions_path, fname)
```
Called on the full parallel filename (e.g. `parallel-1-executable-foo-2026-04-14.md`). Returns False — secondary bug.

**Line 252** (inside `_handle` — PRIMARY BUG SITE):
```python
    def _handle(self, path: str):
        filename = os.path.basename(path)
        if not is_runnable_plan(filename) or path in self._seen:  # ← early return HERE
            return
        group = extract_parallel_group(filename)
```
Called on the raw filename before any parallel-group detection. Returns False for parallel plans → early return at line 253. `extract_parallel_group` is never reached.

**Line 300** (inside `_check_queue_drain`):
```python
        pending.extend([f for f in os.listdir(d) if is_runnable_plan(f)])
```
Scans watched directories for remaining plans. Parallel plans are invisible here — queue drain fires prematurely if only parallel plans remain.

**Line 322** (inside `_rescan`):
```python
                for fname in os.listdir(decisions_path):
                    if is_runnable_plan(fname):
                        full_path = os.path.join(decisions_path, fname)
                        handler._handle(full_path)
```
Rescan loop pre-filters with `is_runnable_plan` before calling `_handle`. Parallel plans are never passed to `_handle` here.

**Line 350** (inside `start`, startup scan):
```python
                for fname in os.listdir(decisions_path):
                    if is_runnable_plan(fname):
                        full_path = os.path.join(decisions_path, fname)
                        handler._handle(full_path)
```
Startup scan also pre-filters. Parallel plans on disk at startup are silently skipped.

---

## (4) extract_parallel_group, collect_group, handle_parallel_group

### extract_parallel_group (lines 229–231)
```python
def extract_parallel_group(filename: str) -> Optional[str]:
    match = re.match(r"^(parallel-\d+)-", filename)
    return match.group(1) if match else None
```
Does NOT call `is_runnable_plan` internally.

### collect_group (lines 240–248)
```python
def collect_group(self, decisions_path: str, group: str) -> list:
    files = os.listdir(decisions_path)
    result = []
    for fname in files:
        if fname.startswith(group + "-") and is_runnable_plan(fname):
```
**SECONDARY BUG:** `collect_group` calls `is_runnable_plan(fname)` on the **full parallel filename** (e.g. `parallel-1-executable-foo-2026-04-14.md`), not on the suffix after the group prefix. This returns False for all parallel plans. Even if `_handle`'s early-return bug were fixed, `collect_group` would return an empty list and no plans would be dispatched.

### handle_parallel_group (lines 313–316)
```python
def handle_parallel_group(self, paths: list):
    threads = [threading.Thread(target=self._run_tracked, args=(p,), daemon=True) for p in paths]
    [t.start() for t in threads]
    print(f"Bellows: ▶ started {len(threads)} parallel threads")
```
Does NOT call `is_runnable_plan` internally. Purely a thread launcher.

---

## (5) PlanHandler._handle — Full Method

Lines 250–265:

```python
def _handle(self, path: str):
    filename = os.path.basename(path)
    if not is_runnable_plan(filename) or path in self._seen:   # line 252 — PRIMARY BUG
        return
    group = extract_parallel_group(filename)
    if group:
        decisions_path = str(pathlib.Path(path).parent)
        siblings = self.collect_group(decisions_path, group)
        all_paths = [p for p in siblings if p not in self._seen]
        [self._seen.add(p) for p in all_paths]
        print(f"Bellows: parallel group {group} — {len(all_paths)} plans")
        self.orchestrator.handle_parallel_group(all_paths)
    else:
        self._seen.add(path)
        print(f"Bellows: detected plan {filename}")
        self.orchestrator.handle_new_plan(path)
```

At line 252, `filename` is the **full basename** of the path — e.g. `parallel-1-executable-foo-2026-04-14.md`. `is_runnable_plan` returns False for this, so `_handle` returns at line 253. The parallel-group detection at line 254 is never reached.

---

## (6) Tests for is_runnable_plan with Parallel-Prefixed Input

**No such test exists.**

`test_bellows.py` line 33–35:
```python
def test_is_runnable_plan_diagnostic():
    assert bellows.is_runnable_plan("diagnostic-foo-2026-04-14.md") is True
    assert bellows.is_runnable_plan("in-progress-diagnostic-foo.md") is False
```
Only tests `diagnostic-` and `in-progress-` prefixes. No test for `parallel-N-executable-*` or `parallel-N-diagnostic-*` input.

Tests for `extract_parallel_group` do exist (lines 38–45) and correctly confirm that `extract_parallel_group("parallel-1-executable-foo-2026-04-14.md") == "parallel-1"` — but this function is never reached in practice due to the `_handle` early return.

---

## (7) Bug Verdict and Full Call Chain

### Primary Bug — Confirmed (REAL)

**Parallel plans are silently dropped.** The call chain:

1. A `parallel-1-executable-foo-2026-04-14.md` file appears in the watched directory.
2. The filesystem watcher fires `on_created` → `_handle(path)`.
3. `_handle` line 252: `is_runnable_plan("parallel-1-executable-foo-2026-04-14.md")` → **False**.
4. `_handle` returns immediately at line 253. Parallel group detection is never reached.
5. The plan is never added to `_seen`, never dispatched, never executed.

The same drop occurs at:
- **Startup scan** (line 350): `is_runnable_plan` pre-filters before calling `_handle` — parallel plans on disk at boot are invisible.
- **Rescan loop** (line 322): same pre-filter — parallel plans are never re-tried.
- **Queue drain check** (line 300): parallel plans not counted as pending — premature "queue empty" notification possible.

### Secondary Bug — Confirmed (ALSO REAL)

Even if the `_handle` early-return were fixed (i.e., `is_runnable_plan` were made parallel-aware), **`collect_group` has its own bug**: it calls `is_runnable_plan(fname)` on the full parallel filename (line 244), which also returns False. So `collect_group` would return an empty list, and `handle_parallel_group` would be called with `[]` — starting zero threads.

The fix requires changes in at least two places:
1. `_handle` line 252: must not gate on `is_runnable_plan` for filenames that match `extract_parallel_group`.
2. `collect_group` line 244: must strip the group prefix before calling `is_runnable_plan`, or use a different check (e.g., check that the suffix after the group prefix starts with `executable-` or `diagnostic-`).

Additionally, the startup scan, rescan, and queue-drain loops all pre-filter with `is_runnable_plan` — these must also be made parallel-aware or must pass all parallel filenames through to `_handle`.

### No fix applied (read-only diagnostic per instructions).
