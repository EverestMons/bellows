# Startup Sweep Test Refactor — Investigation Surface

**Date:** 2026-05-05
**Plan:** diagnostic-startup-sweep-test-refactor-2026-05-05
**Investigator:** Bellows Developer (Step 1)

---

## 1. Test Locations and Content

**`test_startup_sweep_removes_done_plan_orphans`** — `tests/test_consume_verdicts.py:213`
Regression test for the cleanup-slug-normalization fix (commit `bc09bb5`, 2026-05-01). Verifies that verdict-request files orphaned by plans moved to `Done/` are removed during startup sweep.

**`test_cleanup_normalizes_prefixed_verdict_slug`** — `tests/test_consume_verdicts.py:39`
Exercises production code directly: constructs a `Bellows` instance, patches `BELLOWS_ROOT` and verdict helpers, then calls `b._consume_verdicts()`. Does NOT replicate production logic inline.

The orphan-removal test (lines 247–271) replicates sweep logic inline:

```python
# Lines 247-271 of tests/test_consume_verdicts.py
with patch("bellows.BELLOWS_ROOT", tmp_path):
    active_slugs = set()
    for dp in config["watched_projects"]:
        if not os.path.isdir(dp):
            continue
        for fname in os.listdir(dp):
            if fname.startswith("in-progress-") or fname.startswith("verdict-pending-"):
                stripped = fname
                for pfx in ("in-progress-", "verdict-pending-"):
                    if stripped.startswith(pfx):
                        stripped = stripped[len(pfx):]
                        break
                active_slugs.add(bellows.verdict.slug_from_path(stripped))
            elif bellows.is_runnable_plan(fname):
                active_slugs.add(bellows.verdict.slug_from_path(fname))
    # NOTE: Done/ loop intentionally absent — this IS the fix being tested
    pd = tmp_path / "verdicts" / "pending"
    orphaned_removed = []
    if pd.is_dir():
        for pf in os.listdir(pd):
            m = re.match(r"^verdict-request-(.+)-step-\d+\.md$", pf)
            if m:
                extracted_slug = m.group(1)
                if extracted_slug not in active_slugs:
                    (pd / pf).unlink()
                    orphaned_removed.append(pf)
```

## 2. Production Sweep Location and Content

The startup sweep lives in `bellows.py:986–1014`, inline within `Bellows.start()`:

```python
# Lines 986-1014 of bellows.py
# One-time startup sweep: remove orphaned verdict requests
active_slugs = set()
for decisions_path in self.config.get("watched_projects", []):
    if not os.path.isdir(decisions_path):
        continue
    for fname in os.listdir(decisions_path):
        if fname.startswith("in-progress-") or fname.startswith("verdict-pending-"):
            stripped = fname
            for pfx in ("in-progress-", "verdict-pending-"):
                if stripped.startswith(pfx):
                    stripped = stripped[len(pfx):]
                    break
            active_slugs.add(verdict.slug_from_path(stripped))
        elif is_runnable_plan(fname):
            active_slugs.add(verdict.slug_from_path(fname))
pending_dir = BELLOWS_ROOT / "verdicts" / "pending"
orphaned_removed = []
if pending_dir.is_dir():
    for pf in os.listdir(pending_dir):
        m = re.match(r"^verdict-request-(.+)-step-\d+\.md$", pf)
        if m:
            extracted_slug = m.group(1)
            if extracted_slug not in active_slugs:
                (pending_dir / pf).unlink()
                orphaned_removed.append(pf)
if orphaned_removed:
    print(f"Bellows: startup cleanup — {len(orphaned_removed)} orphaned verdict requests removed")
    for rm_name in orphaned_removed:
        print(f"  - {rm_name}")
```

## 3. Divergences Enumerated

| # | Aspect | Production (bellows.py) | Test (inline replica) |
|---|--------|------------------------|-----------------------|
| 1 | Config access | `self.config.get("watched_projects", [])` | `config["watched_projects"]` (direct dict access, no default) |
| 2 | `verdict` module reference | `verdict.slug_from_path(...)` | `bellows.verdict.slug_from_path(...)` (qualified, trivial) |
| 3 | `is_runnable_plan` reference | `is_runnable_plan(fname)` | `bellows.is_runnable_plan(fname)` (qualified, trivial) |
| 4 | `pending_dir` path construction | `BELLOWS_ROOT / "verdicts" / "pending"` | `tmp_path / "verdicts" / "pending"` (patched via `BELLOWS_ROOT`) |
| 5 | Print output | Prints summary + per-file removal log | No print output |
| 6 | Variable naming | `pending_dir`, `pf` | `pd`, `pf` |

**Production behavior the test does NOT replicate:**
- The print-based logging (divergence #5) — cosmetic, not behavioral.
- No other behavioral divergence. The core logic (active-slug collection → orphan removal) is identical line-for-line.

## 4. Refactor Sketch

### Proposed signature

```python
def _perform_startup_sweep(self) -> list[str]:
    """Remove orphaned verdict-request files. Returns list of removed filenames."""
```

### Dependencies accessed via `self.*`

- `self.config.get("watched_projects", [])` — already an instance attribute.

### Dependencies accessed via module globals

- `BELLOWS_ROOT` — module-level constant (already patchable in tests).
- `verdict.slug_from_path()` — module import.
- `is_runnable_plan()` — module-level function.
- `re` — stdlib import.
- `os` — stdlib import.

No additional attributes or parameters needed. All dependencies are already available.

### Production call site (`start()`)

Lines 986–1014 become:

```python
# One-time startup sweep: remove orphaned verdict requests
orphaned_removed = self._perform_startup_sweep()
if orphaned_removed:
    print(f"Bellows: startup cleanup — {len(orphaned_removed)} orphaned verdict requests removed")
    for rm_name in orphaned_removed:
        print(f"  - {rm_name}")
```

Or even simpler (move prints into the method):

```python
self._perform_startup_sweep()
```

The sweep has NO dependency on the observer, handler, or `time.sleep(3)` that precedes it. The observer is already started before the sweep (line 976), but the sweep reads from disk and does not interact with observer state. Extraction is clean — no mid-sweep observer-setup steps.

### Test call site

```python
b = bellows.Bellows(config)
with patch("bellows.BELLOWS_ROOT", tmp_path):
    orphaned_removed = b._perform_startup_sweep()
```

This is a direct single-line invocation. No mocking of observer, server, or event loop required. The `Bellows` constructor does try to prune git worktrees for each `watched_projects` entry, but since the test points `watched_projects` at a temp dir, the `git worktree prune` call in `__init__` will simply fail silently (already wrapped in try/except).

## 5. LOC Estimate (Revised)

| Change | LOC |
|--------|-----|
| New `_perform_startup_sweep` method (def + docstring + body) | ~20 LOC (the existing sweep logic moved + return statement) |
| `start()` call site replacement (remove 28 lines, add 5) | –23 LOC net |
| Test refactor (remove 24 inline lines, add 3) | –21 LOC net |
| **Net change** | **~–24 LOC** (code shrinks) |

The BACKLOG estimate of "~10 LOC refactor" undercounts: the new method is ~20 LOC (it's moving existing code, not writing new code), but the net effect is a ~24 LOC reduction because both the test and `start()` get simpler. The refactor itself is straightforward — the "~10 LOC" likely referred to the diff size of new code written, which is more like ~3 LOC (the def line, the return, and the call site).

## 6. Test-Side Migration Cost

**Low.** The test already:
- Constructs a `Bellows` instance (line 241).
- Patches `BELLOWS_ROOT` (line 246).
- Has the exact fixture setup needed (temp dirs, orphan files).

Migration requires:
1. Delete lines 247–271 (the inline replica).
2. Replace with `orphaned_removed = b._perform_startup_sweep()`.
3. Keep existing assertions (lines 273–276) unchanged.

The `Bellows.__init__` constructor runs `git worktree prune` on each `watched_projects` path, but this is already handled by the existing try/except in `__init__` — the test already constructs `Bellows(config)` successfully on line 241 today.

No additional mocking or fixture changes needed.

## 7. Risks and Unanticipated Complications

1. **Constructor side effects:** `Bellows.__init__` calls `git worktree prune` for each watched project. This already runs in the test (line 241) and fails silently. No new risk.

2. **`ResponseServer` construction:** `Bellows.__init__` creates `server.ResponseServer(config["callback_port"])`. The test already handles this (port 5999 in config). If the server binds the port, parallel test runs could conflict — but this is a pre-existing issue, not introduced by the refactor.

3. **Print output in method:** If prints are moved into `_perform_startup_sweep`, tests that capture stdout will see startup-sweep output. This is actually desirable for observability. If undesirable, keep prints in `start()` and have the method return `orphaned_removed`.

4. **No `start()`-preceding dependency:** The sweep does NOT depend on `self.response_server.start()`, the observer, or the `time.sleep(3)`. It only reads `self.config` and module globals. Extraction is genuinely clean.

5. **No risks beyond what the BACKLOG entry anticipated.** The refactor surface is simple and well-bounded.

## 8. Recommendation

**Proceed with refactor.** Rationale:

- The inline test replica is a maintenance liability: any future change to the startup sweep logic must be mirrored in the test, with risk of divergence.
- The `test_cleanup_normalizes_prefixed_verdict_slug` test (line 39) already demonstrates the preferred pattern — call production code with patched dependencies.
- The extraction is clean: no observer/event-loop entanglement, no constructor complications beyond what the test already handles.
- Net code reduction of ~24 LOC with improved test fidelity.
- Risk profile is minimal — the only moving parts are `self.config` and `BELLOWS_ROOT`, both already patched in the existing test.
