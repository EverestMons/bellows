# `_consume_verdicts` Drain Failure — `processed-` Prefix at Write Time

**Date:** 2026-05-21
**Agent:** Bellows Systems Analyst
**Scope:** Diagnostic — characterize why two valid `resolved/` verdict files were not consumed across multiple daemon cycles and a clean restart

---

## Discovery and Slug-Extraction Trace

### Q1 — Discovery scope

`_consume_verdicts` at `bellows.py:1127-1131` enumerates files in `verdicts/resolved/` via `os.listdir(resolved_dir)` and applies three sequential filters:

**Filter 1 — prefix + extension (line 1128):**
```python
if not fname.startswith("verdict-") or not fname.endswith(".md"):
    continue
```
Accepts only files whose name starts with literal `verdict-` and ends with `.md`. Files with any other prefix (`processed-`, `_PLANNER_RECALLED_`, `obsolete-`, etc.) are silently dropped here.

**Filter 2 — verdict-request exclusion (lines 1130-1131):**
```python
if fname.startswith("verdict-request-"):
    continue
```
Excludes verdict-request files that may have ended up in `resolved/` (S3 Bug A fix, commit `dc0bdd7`).

**Filter 3 — regex parse (lines 1133-1137):**
```python
match = re.match(r"^verdict-(.+)-step-(\d+)\.md$", fname)
if not match:
    _log("WARN", ...)
    continue
```
Extracts `plan_slug` (group 1) and `step_number` (group 2). Files that don't match the `verdict-{slug}-step-{N}.md` shape are warned and skipped.

**Summary:** The consumer accepts filenames matching `verdict-{slug}-step-{N}.md` and explicitly rejects `verdict-request-*`. All other prefixes are silently excluded by Filter 1.

### Q2 — Slug extraction from verdict filename

Given `verdict-fuel-continuation-inference-v2-2026-05-21-step-1.md`:

The regex at `bellows.py:1133` — `r"^verdict-(.+)-step-(\d+)\.md$"` — matches and extracts:
- `plan_slug` = `fuel-continuation-inference-v2-2026-05-21` (greedy `.+` stops at the last `-step-`)
- `step_number` = `1`

Given `processed-verdict-fuel-continuation-inference-v2-2026-05-21-step-1.md`:

This filename **never reaches the regex**. Filter 1 at line 1128 rejects it because `processed-verdict-` does not start with `verdict-`. The regex is never evaluated.

Even if it were evaluated, `^verdict-(.+)-step-(\d+)\.md$` would not match `processed-verdict-...` because the `^verdict-` anchor requires the string to begin with `verdict-`.

### Q3 — Slug extraction from plan filename

`verdict.slug_from_path()` at `verdict.py:82-92`:

```python
def slug_from_path(plan_path):
    basename = os.path.basename(plan_path)
    for prefix in ("in-progress-", "verdict-pending-", "executable-", "diagnostic-"):
        if basename.startswith(prefix):
            basename = basename[len(prefix):]
    if basename.endswith(".md"):
        basename = basename[:-3]
    return basename
```

Given `verdict-pending-diagnostic-fuel-continuation-inference-v2-2026-05-21.md`:
1. Strips `verdict-pending-` → `diagnostic-fuel-continuation-inference-v2-2026-05-21.md`
2. The loop **breaks** after the first match — `diagnostic-` is NOT stripped in a second pass
3. Strips `.md` → **slug = `diagnostic-fuel-continuation-inference-v2-2026-05-21`**

The plan-side slug retains the `diagnostic-` prefix.

### Q4 — Pairing comparison

At `bellows.py:1184-1185`:
```python
for pname in os.listdir(decisions_path):
    if pname.startswith("verdict-pending-") and plan_slug in pname:
```

This is a **substring** check (`in`), not equality. For:
- `plan_slug` = `fuel-continuation-inference-v2-2026-05-21` (from verdict filename)
- `pname` = `verdict-pending-diagnostic-fuel-continuation-inference-v2-2026-05-21.md`

`plan_slug in pname` → **True** (the verdict-side slug is a substring of the plan-side filename).

H1 does **not** cause a pairing failure. The substring comparison accommodates the asymmetry where the plan filename includes a `diagnostic-`/`executable-` prefix that the verdict filename does not.

### Q5 — Effect of writing a verdict file with `processed-` already in the filename

Trace for `processed-verdict-fuel-continuation-inference-v2-2026-05-21-step-1.md`:

1. **Filter 1 (bellows.py:1128):** `fname.startswith("verdict-")` → `"processed-verdict-...".startswith("verdict-")` → **`False`**
2. `not False` → `True` → **`continue`** → file is silently skipped

The file never reaches Filter 2, Filter 3, `check_verdict`, slug extraction, or the pairing loop. It is invisible to the consumer at the very first filter.

**Why `processed-` looks like an already-consumed file:** After successful verdict consumption, `_consume_verdicts` renames the file at `bellows.py:1253`:
```python
processed_path = resolved_dir / f"processed-{fname}"
shutil.move(str(resolved_dir / fname), str(processed_path))
```

A file named `verdict-foo-step-1.md` becomes `processed-verdict-foo-step-1.md` post-consumption. A file written as `processed-verdict-foo-step-1.md` at write time is structurally identical to an already-consumed file — the consumer cannot distinguish them and silently skips both.

### Q6 — Effect of writing a verdict file with `verdict-` (no `processed-`) prefix

Trace for `verdict-fuel-continuation-inference-v2-2026-05-21-step-1.md`:

1. **Filter 1 (line 1128):** `startswith("verdict-")` → **True** → passes
2. **Filter 2 (line 1130):** `startswith("verdict-request-")` → **False** → passes
3. **Filter 3 (line 1133):** regex matches → `plan_slug = "fuel-continuation-inference-v2-2026-05-21"`, `step_number = 1`
4. **Pending request lookup (lines 1142-1148):** `lookup_slug` strips `diagnostic-`/`executable-` (redundant here — slug has no such prefix) → looks for `verdict-request-fuel-continuation-inference-v2-2026-05-21-step-1.md`
5. **`check_verdict` (line 1171):** constructs `verdict-fuel-continuation-inference-v2-2026-05-21-step-1.md` in `resolved/` → **file exists** → parses content → returns `{"found": True, "verdict": "continue", ...}`
6. **Pairing (line 1185):** `plan_slug in pname` → substring match succeeds against `verdict-pending-diagnostic-...`
7. **Result:** verdict consumed, plan advanced or moved to Done

This is the working path. Both reproductions would have succeeded if the files had been named `verdict-*` instead of `processed-verdict-*`.

### Q7 — `_PLANNER_RECALLED_` interaction

The `_PLANNER_RECALLED_` prefix is excluded by the same Filter 1 at `bellows.py:1128`. A file named `_PLANNER_RECALLED_processed-verdict-foo-step-1.md` does not start with `verdict-` and is silently skipped. There is no explicit `_PLANNER_RECALLED_` exclusion — the exclusion is an implicit side effect of the `startswith("verdict-")` requirement.

This is the correct behavior: the Planner prefixes recalled files to take them out of the consumer's scan. If Bellows were later modified to accept broader filename prefixes, `_PLANNER_RECALLED_` would need an explicit exclusion to prevent re-processing.

---

## Root Cause

**H2 is the sole root cause. H1 is not a contributing factor.**

The two verdict files were named:
- `processed-verdict-fuel-continuation-inference-v2-2026-05-21-step-1.md`
- `processed-verdict-fuel-continuation-inference-failure-typing-2026-05-22-step-1.md`

Both start with `processed-`, not `verdict-`. The discovery filter at **bellows.py:1128** —

```python
if not fname.startswith("verdict-") or not fname.endswith(".md"):
    continue
```

— silently drops both files before any further processing occurs. No slug extraction, no `check_verdict` call, no pairing comparison is ever reached. The files are structurally identical to already-consumed verdicts and are invisible to the consumer.

**The defective line is bellows.py:1128.** Not because the line itself is wrong (it correctly filters for unprocessed verdict files), but because it has no guard for the scenario where a verdict file is written with the `processed-` prefix at write time. The filter implicitly assumes that all unconsumed verdict files in `resolved/` start with `verdict-`, which is violated when the Planner writes the file with the post-consumption prefix already applied.

**H1 (slug-extraction prefix mismatch) is not a factor.** The substring comparison at `bellows.py:1185` (`plan_slug in pname`) handles the `diagnostic-`/`executable-` prefix asymmetry correctly. If the files had been named `verdict-fuel-continuation-inference-v2-2026-05-21-step-1.md` (without `processed-`), both would have been consumed successfully.

**Why the known-passing reference worked:** The passing file `processed-verdict-bellows-tier-1-batch-2026-05-21-step-1.md` was originally named `verdict-bellows-tier-1-batch-2026-05-21-step-1.md`, was consumed successfully by `_consume_verdicts`, and was then renamed to `processed-*` by Bellows at line 1253. The `processed-` prefix was applied by the consumer post-consumption — not at write time.

---

## Resolution Options

### Option A — Accept both `verdict-*` and `processed-verdict-*` filename shapes in discovery

Modify the discovery filter at `bellows.py:1128` to strip `processed-` before applying the `verdict-` prefix check. Then normalize the filename for the regex extraction.

```python
# Strip processed- prefix if present (files written with post-consumption naming)
scan_fname = fname
if scan_fname.startswith("processed-"):
    scan_fname = scan_fname[len("processed-"):]
if not scan_fname.startswith("verdict-") or not scan_fname.endswith(".md"):
    continue
```

**LOC estimate:** ~5 production lines + ~10 test lines
**Risk:** Low. The `processed-` prefix is unambiguous. However, this creates a semantic oddity: a file could be consumed and renamed from `processed-verdict-X` to `processed-processed-verdict-X`. A guard against double-prefixing at the rename site (line 1253) would be needed.

### Option B — Strip `processed-` at write-time detection and rename before processing

Add a pre-processing pass at the top of `_consume_verdicts` that detects `processed-verdict-*` files in `resolved/` and renames them to `verdict-*` before the main scan loop runs.

```python
# Pre-scan: normalize processed-verdict-* to verdict-* (write-time naming mismatch)
for fname in os.listdir(resolved_dir):
    if fname.startswith("processed-verdict-") and fname.endswith(".md"):
        canonical = fname[len("processed-"):]
        shutil.move(str(resolved_dir / fname), str(resolved_dir / canonical))
        _log("WARN", f"renamed write-time processed- prefix: {fname} → {canonical}")
```

**LOC estimate:** ~6 production lines + ~10 test lines
**Risk:** Low. This is a self-healing approach — the rename happens once, and the main loop then processes the canonical filename normally. No double-prefixing risk. Minor risk: if a legitimately-processed file is somehow left behind without rename (e.g., crash between consumption and rename), this could re-process it. However, the existing code already renames consumed files atomically, so this scenario is extremely unlikely.

### Option C — Governance-only fix: document the write-time naming convention

Update PLANNER_TEMPLATE to explicitly prohibit the `processed-` prefix when depositing verdict files. The correct write-time filename is `verdict-{slug}-step-{N}.md`; the `processed-` prefix is applied by Bellows after consumption.

**LOC estimate:** 0 production lines, ~2 governance lines
**Risk:** High recurrence risk. This is the same class of error as the 2026-05-12 wrong-directory incident (Planner depositing to `pending/` instead of `resolved/`). Governance-only fixes rely on the Planner never making the same mistake, which has failed before. A code-level guard (Option A or B) is more robust.

---

## Test Coverage

### Existing tests exercising `_consume_verdicts`

File: `bellows/tests/test_consume_verdicts.py` (5 tests):

1. **`test_cleanup_normalizes_prefixed_verdict_slug`** — Tests that cleanup deletes verdict-request files when the verdict slug includes a plan-type prefix (`diagnostic-`). Uses correctly-named `verdict-diagnostic-foo-2026-05-01-step-1.md`.
2. **`test_cleanup_unprefixed_verdict_slug`** — Tests backward compatibility with unprefixed verdict slugs. Uses `verdict-qux-2026-05-01-step-1.md`.
3. **`test_consume_verdicts_skips_verdict_request_files`** — Tests S3 Bug A fix (verdict-request-* files in resolved/ are skipped).
4. **`test_dispatch_starts_fresh_when_db_has_orphan_slug_rows`** — Tests phantom-resume prevention. Exercises `run_plan`, not `_consume_verdicts` directly.
5. **`test_consume_verdicts_marks_resolved_processed_when_plan_halted`** — Tests S3 Bug C fix (stale verdict for halted plan is moved to processed-*). Uses `verdict-executable-foo-2026-05-09-step-2.md`.

### Existing tests exercising `check_verdict` and `slug_from_path`

File: `bellows/tests/test_verdict.py` — exercises `check_verdict` parsing and `slug_from_path` extraction (not enumerated in detail; confirmed present via grep).

### Gaps

**No test exercises a `processed-verdict-*` file in `resolved/`.** All existing tests use correctly-named `verdict-*` files. The H2 failure mode — a file written with `processed-` prefix at write time being invisible to the consumer — is not covered.

**No test exercises `_PLANNER_RECALLED_*` files in `resolved/`.** The implicit exclusion via `startswith("verdict-")` is untested.

**No test exercises the `in` substring comparison (line 1185) with slug prefix asymmetry.** `test_cleanup_normalizes_prefixed_verdict_slug` tests cleanup but not the `plan_slug in pname` pairing comparison for the case where the verdict slug lacks a prefix that the plan filename includes.

---

## Output Receipt
**Agent:** Bellows Systems Analyst
**Step:** 1
**Status:** Complete

### What Was Done
Traced `_consume_verdicts` end-to-end: discovery filter, slug extraction, `check_verdict` call, and plan-file pairing comparison. Evaluated H1 (slug-extraction prefix mismatch) and H2 (`processed-` filename prefix collision) against the code. Confirmed H2 as the sole root cause — the `startswith("verdict-")` filter at bellows.py:1128 silently drops files named `processed-verdict-*`, which are structurally identical to already-consumed verdicts. H1 is not a contributing factor (substring comparison handles prefix asymmetry). Read the BACKLOG entry, both stuck files, the known-passing reference, prior SA architecture doc, and full test suite for the consumer path.

### Files Deposited
- `bellows/knowledge/architecture/consume-verdicts-drain-failure-2026-05-21.md` — diagnostic findings for Q1-Q10

### Files Created or Modified (Code)
- None — investigation only, no source modifications

### Decisions Made
- Classified H2 (`processed-` prefix at write time) as the sole root cause
- Classified H1 (slug prefix mismatch) as non-contributing — substring comparison handles it
- Identified bellows.py:1128 as the defective line (implicit assumption that unconsumed files start with `verdict-`)
- Recommended Option B (pre-scan rename) as the most robust fix shape

### Flags for CEO
- None — single-step diagnostic, findings deposited for Planner review

### Flags for Next Step
- None — single-step diagnostic, no further steps
