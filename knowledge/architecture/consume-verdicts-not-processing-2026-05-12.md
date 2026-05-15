# `_consume_verdicts` — Pending Verdicts Not Processing

**Date:** 2026-05-12
**Agent:** Bellows Systems Analyst
**Scope:** Diagnostic — why two Planner-deposited continue verdicts are not being consumed

---

## Q1 — What triggers `_consume_verdicts`?

There is **one call site** for `_consume_verdicts`:

- **`Bellows._rescan()` → line 1025**: `self._consume_verdicts()` is the first operation inside `_rescan()`. `_rescan` is called from the main event loop at **line 1287**, gated by a 30-second interval (`rescan_interval = 30`, line 1279). There is no file-watcher trigger, no startup trigger, and no plan-completion trigger — `_consume_verdicts` runs exclusively on the 30-second rescan tick.

**Conditional guards:** None within `_rescan` itself. The rescan interval check at line 1286 (`time.time() - last_rescan >= rescan_interval`) is the only gate. Inside `_consume_verdicts` (line 1046), the function returns early if `verdicts/resolved/` does not exist as a directory (line 1049). Per-file filters: skip non-`.md` files, skip files not starting with `verdict-`, skip files starting with `verdict-request-` (line 1057), and skip files that don't match the regex `^verdict-(.+)-step-(\d+)\.md$` (line 1060).

**Expected filename pattern:** `verdict-{slug}-step-{N}.md` in the `verdicts/resolved/` directory (line 1048, 1060).

## Q2 — Does the current code match Planner-deposited verdict files?

**No.** The verdict files are in the **wrong directory**.

The two verdict files:
- `verdicts/pending/verdict-bellows-self-exposure-disposition-2026-05-12-step-1.md`
- `verdicts/pending/verdict-bellows-self-exposure-wontfix-close-2026-05-12-step-1.md`

are in `verdicts/pending/`. The consumer at line 1048 scans **`verdicts/resolved/`** exclusively:

```python
resolved_dir = BELLOWS_ROOT / "verdicts" / "resolved"
if not resolved_dir.is_dir():
    return
```

The files are never seen. **The filename pattern is correct** — both filenames match the `^verdict-(.+)-step-(\d+)\.md$` regex and the slugs (`bellows-self-exposure-disposition-2026-05-12`, `bellows-self-exposure-wontfix-close-2026-05-12`) would correctly match the corresponding `verdict-pending-` plan files in `knowledge/decisions/` via the `plan_slug in pname` check at line 1110. The content format (`verdict: continue` on first line) also matches what `check_verdict()` expects (line 168).

**The rejection happens at line 1048-1049** — the function never iterates over `verdicts/pending/`, so these files are invisible to the consumer.

## Q3 — Why didn't startup sweep consume them?

**Answer: (a) — the startup sweep does not call `_consume_verdicts`.**

`_perform_startup_sweep()` (lines 1207–1241) has a single, narrow purpose: remove orphaned verdict-*request* files from `verdicts/pending/` whose slugs no longer match any active plan. It does not scan for verdict response files and does not call `_consume_verdicts`.

The startup sequence in `Bellows.start()` is:
1. **Line 1263:** `time.sleep(3)` — auth settle
2. **Line 1265:** `self._perform_startup_sweep()` — orphaned request cleanup only
3. **Lines 1272–1278:** Scan for runnable plans (`is_runnable_plan`), dispatch via `handler._handle()`
4. **Line 1287:** First `_rescan()` (and thus first `_consume_verdicts()`) fires ~30 seconds after startup

Even when the first `_rescan` fires, `_consume_verdicts` scans `verdicts/resolved/`, not `verdicts/pending/`, so the files remain invisible. The startup sweep is not relevant to this bug — the fundamental issue is directory mismatch (Q2).

## Q4 — Recommendation

**(i) The verdict files need to be moved to the correct directory.**

Move:
- `verdicts/pending/verdict-bellows-self-exposure-disposition-2026-05-12-step-1.md` → `verdicts/resolved/verdict-bellows-self-exposure-disposition-2026-05-12-step-1.md`
- `verdicts/pending/verdict-bellows-self-exposure-wontfix-close-2026-05-12-step-1.md` → `verdicts/resolved/verdict-bellows-self-exposure-wontfix-close-2026-05-12-step-1.md`

After the next 30-second rescan tick, `_consume_verdicts` will find and process both files. No code change, no restart, and no precondition is needed.

**Root cause:** The Planner deposited the verdict response files to `verdicts/pending/` instead of `verdicts/resolved/`. The expected verdict lifecycle is:

1. Bellows posts `verdict-request-{slug}-step-{N}.md` to `verdicts/pending/`
2. Planner reads the request, decides continue/stop, deposits `verdict-{slug}-step-{N}.md` to **`verdicts/resolved/`**
3. Bellows's `_consume_verdicts` finds the file in `verdicts/resolved/`, acts on it, and moves it to `processed-verdict-{slug}-step-{N}.md`

The Planner wrote the response files to step 1's directory (`verdicts/pending/`) rather than step 2's directory (`verdicts/resolved/`). This is a **Layer 3 (Planner) process error**, not a Layer 1 (Bellows) code defect.

### Layer Impact

- **Layer 1 (Bellows):** No code defect. `_consume_verdicts` correctly scans `verdicts/resolved/`. No change needed.
- **Layer 2 (Agents):** Not affected.
- **Layer 3 (Planner):** The Planner's verdict-deposition logic deposited to the wrong directory. The Planner template or process should be checked to ensure verdict response files are always deposited to `verdicts/resolved/`, not `verdicts/pending/`.

---

## Output Receipt
**Agent:** Bellows Systems Analyst
**Step:** 1
**Status:** Complete

### What Was Done
Traced `_consume_verdicts` end-to-end against the two pending verdict files. Identified that the files are in `verdicts/pending/` but the consumer scans `verdicts/resolved/` exclusively. Confirmed filename pattern, slug matching, and content format are all correct — only the directory is wrong. Root cause is a Planner-side deposition error.

### Files Deposited
- `bellows/knowledge/architecture/consume-verdicts-not-processing-2026-05-12.md` — diagnostic findings for Q1–Q4

### Files Created or Modified (Code)
- None — investigation only, no source modifications

### Decisions Made
- Classified as Layer 3 (Planner) process error, not Layer 1 code defect
- Recommended file move as immediate corrective action (no code change needed)

### Flags for CEO
- The two verdict files can be unblocked immediately by moving them from `verdicts/pending/` to `verdicts/resolved/`
- The Planner's verdict-deposition target directory should be verified to prevent recurrence

### Flags for Next Step
- None — single-step diagnostic, no further steps
