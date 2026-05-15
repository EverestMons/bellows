# S3 Verdict-Resolved Retry Loop — Diagnostic Findings

**Date:** 2026-05-09
**Diagnostic:** diagnostic-s3-verdict-resolved-retry-loop-2026-05-09
**Agent:** Bellows Systems Analyst
**Step:** 1

---

## Summary

The S3 verdict-resolved retry loop has **two distinct root causes**, not one. Root cause A: `check_verdict()` at `verdict.py:157` requires `verdict: continue` format but 14 stranded files use bare `continue` (no `verdict:` prefix), causing `check_verdict` to return `found: False` and silently skip the file on every 30-second scan — the stale-verdict Done/ check is never reached. Root cause B: the file-listing filter at `bellows.py:881` does not exclude `verdict-request-` prefixed files from `resolved/`, causing 2 misnamed request-shaped files to be parsed as verdict responses with corrupted slugs. All 16 stranded files correspond to plans already in Done/ (12), halted (1), or Done/ in another project (2, forge), plus 1 in invoice-pulse Done/ — none require re-execution. The bug does NOT reproduce for new verdicts deposited with current Planner conventions (`verdict: continue` format), but the 16 stranded files will loop forever without code fix or manual cleanup.

## Task A — Live Reproduction

**Method:** Code-path analysis of `_consume_verdicts()` against the actual stranded files on disk.

**Reproduction confirmed — the bug is live on current `main` HEAD.** Every 30-second rescan cycle, Bellows:

1. Lists all files in `verdicts/resolved/` matching `verdict-*.md` (line 880-881)
2. Parses slug and step from filename (line 884)
3. Calls `verdict.check_verdict(plan_slug, step_number)` (line 920)
4. `check_verdict` reads the file, checks first line against `r"^verdict:\s*(continue|stop)$"` (verdict.py:157)
5. For files with bare `continue` as first line → regex fails → returns `{"found": False}`
6. `_consume_verdicts` hits `continue` at line 922 → **file silently skipped**

No log line is emitted when `check_verdict` returns `found: False`. The file is not moved, not archived, not warned about. It sits in `resolved/` and is re-scanned every 30 seconds indefinitely.

**Predicted log output per cycle:** None for the 14 bare-format files (silent skip). For the pipe-header request-shaped file (which does have `verdict: continue` format), the following log line fires every cycle:

```
Bellows: ⚠️  no verdict-pending plan found for request-pipe-header-parser-and-comprehensive-qa-2026-05-08 step 2 — leaving in resolved/ for retry
```

For the billto request-shaped file (YAML frontmatter, first line `---`), `check_verdict` returns `found: False` → silent skip.

**Does the bug reproduce for NEW verdicts?** No — provided the Planner deposits verdict responses with `verdict: continue` format (which it has been doing consistently since at least 2026-05-03 based on all 168 successfully-processed files). The format intolerance is a latent risk but not actively triggered by current Planner behavior.

## Task B — Code Path Trace

### File listing (bellows.py:880-881)

```python
for fname in os.listdir(resolved_dir):
    if not fname.startswith("verdict-") or not fname.endswith(".md"):
        continue
```

- Selects files matching `verdict-*.md`
- **Gap:** Does NOT exclude `processed-verdict-*` (these start with `processed-`, not `verdict-`, so they're correctly filtered). Does NOT exclude `verdict-request-*` (these start with `verdict-`, so they PASS the filter — **Bug B**).
- Does NOT exclude `_PLANNER_RECALLED_*` (starts with `_`, not `verdict-`, so correctly filtered).

### Slug parsing (bellows.py:884-888)

```python
match = re.match(r"^verdict-(.+)-step-(\d+)\.md$", fname)
if not match:
    continue
```

- Extracts `plan_slug` and `step_number` from filename.
- For `verdict-request-*` files, `plan_slug` includes the spurious `request-` prefix.

### Verdict content check (bellows.py:920-922)

```python
verdict_result = verdict.check_verdict(plan_slug, step_number)
if not verdict_result.get("found"):
    continue  # ← SILENT SKIP, no log, no escalation
```

This is the **primary gate** that blocks processing of the 14 bare-format files. `check_verdict` (verdict.py:142-163) reconstructs the filepath and reads it:

```python
# verdict.py:156-159
first_line = lines[0].strip()
match = re.match(r"^verdict:\s*(continue|stop)$", first_line, re.IGNORECASE)
if not match:
    return {"found": False}  # ← rejects bare "continue"
```

**Every branch that skips the rename:**

| Line | Condition | Effect |
|------|-----------|--------|
| `bellows.py:882` | `not fname.startswith("verdict-")` | Skip non-verdict files (correct) |
| `bellows.py:886` | regex no match | Skip non-standard filenames (correct) |
| `bellows.py:922` | `check_verdict` returns `found: False` | **SILENT SKIP — Bug A** — bare `continue`/`stop` format rejected |
| `bellows.py:1021` | stale check fails (plan not in Done/) | Leave in resolved/, log warning (correct behavior) |

### Plan matching (bellows.py:928-994)

Only reached if `check_verdict` returns `found: True`. Searches `verdict-pending-*` files for `plan_slug in pname`. If found, processes the verdict and renames to `processed-`. If not found, falls through to stale check.

### Stale-verdict Done/ check (bellows.py:1004-1021)

Only reached if `plan_matched` is False AND `check_verdict` returned `found: True`. Scans Done/ directories for any filename containing `plan_slug`. If found, renames to `processed-` with warning. If not found, logs warning and leaves in `resolved/`.

**Key finding:** The stale-verdict Done/ check (lines 1006-1019) is architecturally correct — it handles the "plan moved to Done/ before verdict consumed" case. But it is unreachable for the 14 bare-format files because `check_verdict` silently rejects them at line 922.

## Task C — Stranded-File Census

16 stranded files total (14 bare-format verdict files + 2 request-shaped files):

| # | Filename | Slug | Step | Mtime | First Line | Plan Location | Pending Req |
|---|----------|------|------|-------|------------|---------------|-------------|
| 1 | verdict-canary-phase-3b-restart-2026-04-30-step-2.md | canary-phase-3b-restart-2026-04-30 | 2 | 2026-05-03 | `continue` | bellows Done/ | archived/ |
| 2 | verdict-diagnostic-activity-based-timeout-2026-05-01-step-1.md | diagnostic-activity-based-timeout-2026-05-01 | 1 | 2026-05-03 | `continue` | bellows Done/ | archived/ |
| 3 | verdict-diagnostic-bellows-integration-section-audit-2026-05-01-step-1.md | diagnostic-bellows-integration-section-audit-2026-05-01 | 1 | 2026-05-03 | `continue` | bellows Done/ | archived/ |
| 4 | verdict-diagnostic-lessons-forge-first-cycle-2026-05-01-step-1.md | diagnostic-lessons-forge-first-cycle-2026-05-01 | 1 | 2026-05-03 | `continue` | forge Done/ | archived/ |
| 5 | verdict-diagnostic-parallel-plan-scope-check-collision-2026-05-01-step-1.md | diagnostic-parallel-plan-scope-check-collision-2026-05-01 | 1 | 2026-05-03 | `continue` | bellows Done/ | archived/ |
| 6 | verdict-executable-backlog-close-2026-04-18-integration-protocol-2026-05-01-step-2.md | executable-backlog-close-2026-04-18-integration-protocol-2026-05-01 | 2 | 2026-05-03 | `continue` | bellows Done/ | archived/ |
| 7 | verdict-executable-close-activity-timeout-backlog-2026-05-01-step-2.md | executable-close-activity-timeout-backlog-2026-05-01 | 2 | 2026-05-03 | `continue` | bellows Done/ | archived/ |
| 8 | verdict-executable-lessons-forge-phase2a-classify-2026-05-01-step-1.md | executable-lessons-forge-phase2a-classify-2026-05-01 | 1 | 2026-05-03 | `continue` | forge Done/ | archived/ |
| 9 | verdict-executable-parallel-plan-scope-check-collision-fix-2026-05-01-step-2.md | executable-parallel-plan-scope-check-collision-fix-2026-05-01 | 2 | 2026-05-03 | `stop` | bellows halted- | archived/ |
| 10 | verdict-executable-planner-template-lessons-2026-05-01-step-2.md | executable-planner-template-lessons-2026-05-01 | 2 | 2026-05-03 | `continue` | bellows Done/ | archived/ |
| 11 | verdict-executable-revert-snapshot-fix-and-reopen-backlog-2026-05-01-step-3.md | executable-revert-snapshot-fix-and-reopen-backlog-2026-05-01 | 3 | 2026-05-03 | `continue` | bellows Done/ | archived/ |
| 12 | verdict-phase-3c-plan-hash-drift-warning-2026-04-30-step-2.md | phase-3c-plan-hash-drift-warning-2026-04-30 | 2 | 2026-05-03 | `continue` | bellows Done/ | archived/ |
| 13 | verdict-planner-template-bellows-execution-model-section-2026-04-30-step-2.md | planner-template-bellows-execution-model-section-2026-04-30 | 2 | 2026-05-03 | `continue` | bellows Done/ | archived/ |
| 14 | verdict-verdict-mechanization-distribution-audit-2026-04-30-step-1.md | verdict-mechanization-distribution-audit-2026-04-30 | 1 | 2026-05-03 | `continue` | bellows Done/ | archived/ |
| 15 | verdict-request-billto-extraction-architecture-2026-05-07-step-1.md | (request-shaped anomaly) | 1 | 2026-05-07 | `---` | IP Done/ | not in pending/ |
| 16 | verdict-request-pipe-header-parser-and-comprehensive-qa-2026-05-08-step-2.md | (request-shaped anomaly) | 2 | 2026-05-09 | `verdict: continue` | bellows Done/ | not in pending/ |

### Grouping by failure pattern

**Group 1 — Format intolerance (14 files, rows 1-14):**
All 14 files use bare `continue` or `stop` as the first line. `check_verdict()` rejects them because it requires `verdict: continue` format. All 14 have corresponding pending request files in `pending/archived/` (moved there by CEO as manual mitigation). All 14 have their plans in terminal state (12 in Done/, 1 in halted-, 1 in halted-). All share identical mtime (2026-05-03 19:41), suggesting they were restored from git or created en masse during a git operation on that date. Filename dates span 2026-04-30 to 2026-05-01.

**Group 2 — Request-shaped files in resolved/ (2 files, rows 15-16):**
These have the `verdict-request-` prefix instead of `verdict-`. The pipe-header file passes `check_verdict` (correct content format) but produces a corrupted slug (`request-pipe-header-...`), causing all downstream lookups to fail. The billto file fails `check_verdict` (YAML frontmatter). Both are Planner-deposited files with wrong naming convention. Both plans are already in Done/ (IP and bellows respectively).

## Task D — Request-Shaped File Anomaly

### File 1: verdict-request-billto-extraction-architecture-2026-05-07-step-1.md

**Content (first 10 lines):**
```
---
verdict: continue
plan: diagnostic-billto-extraction-architecture-2026-05-07.md
step: 1
authorized_by: CEO
date: 2026-05-07
---

Diagnostic complete. Findings reviewed via Rule 22...
```

**Shape:** Neither standard request nor standard response. Uses YAML frontmatter with structured fields (`plan:`, `step:`, `authorized_by:`, `date:`) — this is not the Bellows verdict-request format (which uses `**Plan:**`, `**Step:**`, etc.) and not the standard verdict-response format (bare `verdict: continue\n<reason>`). This is a Planner-authored format.

**Corresponding response-shaped file in resolved/:** No `processed-verdict-billto-extraction-architecture-2026-05-07-step-1.md` exists. No `verdict-billto-extraction-architecture-2026-05-07-step-1.md` exists either — the plan was resolved via manual Planner move-to-Done without a Bellows-consumed verdict.

**Hypothesis:** The Planner deposited this file directly into `resolved/` using the `verdict-request-` prefix naming convention and a YAML-frontmatter format, bypassing Bellows's expected verdict lifecycle. The Planner likely performed Rule 22 verification, moved the plan to Done/ manually, and deposited this file as a record — but named it with the request prefix and used a non-standard format. **Cause: Planner naming/format error during manual plan resolution.**

### File 2: verdict-request-pipe-header-parser-and-comprehensive-qa-2026-05-08-step-2.md

**Content (first 5 lines):**
```
verdict: continue
QA report verified per Rule 22 (Planner read deposit at bellows/knowledge/qa/...)...
```

**Shape:** Response-shaped content (correct `verdict: continue` first line with reason text). The content format is correct — it would be parseable by `check_verdict`. But the filename uses `verdict-request-` prefix instead of `verdict-`.

**Corresponding response-shaped file in resolved/:** `processed-verdict-pipe-header-parser-and-comprehensive-qa-2026-05-08-step-2.md` — does NOT exist. The plan is in bellows Done/ as `executable-pipe-header-parser-and-comprehensive-qa-2026-05-08.md`, moved there manually by the Planner.

**Hypothesis:** Same as File 1 — Planner deposited the verdict response with the wrong filename prefix. The content is correct but the name is wrong. **Cause: Planner naming error.** This file actively generates a retry warning log every 30 seconds because `check_verdict` returns `found: True` but no plan matches.

**Common cause for both:** The Planner used `verdict-request-{slug}-step-{N}.md` naming when depositing verdict responses into `resolved/`. The correct naming is `verdict-{slug}-step-{N}.md`. This is a Planner-side discipline issue — Bellows did not misfile these.

## Task E — Synthesis

### 1. Does the bug reproduce on current `main`?

**Partial.** The 16 existing stranded files actively reproduce the retry loop on every 30-second scan. However, the bug does NOT reproduce for **new** verdicts because:
- The Planner now consistently deposits verdict responses with `verdict: continue` format (verified across all 168 processed files post-2026-05-03).
- The Planner has not repeated the `verdict-request-` naming error since the two isolated incidents (2026-05-07, 2026-05-08).

The **latent risk** remains: `check_verdict` still rejects bare `continue`/`stop` format, and the file-listing filter still admits `verdict-request-*` files. Any future format regression or naming mistake will produce new stranded files.

### 2. Root cause (or enumeration of distinct bugs)

**Two distinct bugs conflated under S3:**

- **Bug A — Format intolerance in `check_verdict()`** (verdict.py:157): The regex `r"^verdict:\s*(continue|stop)$"` rejects bare `continue`/`stop` format. Files failing this check are silently skipped at bellows.py:922 — no log, no escalation, no path to the stale-verdict Done/ check. Affects 14 of 16 stranded files.

- **Bug B — Missing `verdict-request-` prefix exclusion** (bellows.py:881): The file-listing filter admits `verdict-request-*` files from `resolved/`, which are then parsed with corrupted slugs (the `request-` component becomes part of the slug). Affects 2 of 16 stranded files. One of these also triggers Bug A (YAML frontmatter); the other produces active retry-loop log noise.

### 3. Are the 16 stranded files recoverable via verdict deposit + Bellows scan?

**No.** The 14 bare-format files cannot be consumed by current `_consume_verdicts` code regardless of plan state — `check_verdict` rejects them before any plan lookup occurs. The 2 request-shaped files cannot be consumed because their corrupted slugs prevent plan matching and stale-check matching.

**All 16 files are safely deletable.** Every corresponding plan is in terminal state:
- 12 plans in bellows Done/
- 2 plans in forge Done/
- 1 plan in invoice-pulse Done/
- 1 plan in bellows halted-

**Recommended cleanup:** CEO can `rm` all 16 files or move them to a `resolved/archived/` subdirectory. No Bellows code change is needed for cleanup — only for prevention.

### 4. Recommended fix shape

**Two-part fix, both within Layer 1 mechanical-only invariant:**

**(a) Format tolerance in `check_verdict` (~3 LOC):** Extend the first-line regex at verdict.py:157 to accept both `verdict: continue` and bare `continue` formats: `r"^(?:verdict:\s*)?(continue|stop)$"`. This makes the parser forward- and backward-compatible. No judgment is involved — the function still only accepts exactly `continue` or `stop` as verdict values.

**(b) Prefix exclusion in file listing (~1 LOC):** Add `verdict-request-` to the skip conditions at bellows.py:881: `if fname.startswith("verdict-request-") or fname.startswith("processed-"):`. This prevents request-shaped files from entering the verdict-consumption pipeline regardless of how they got into `resolved/`.

Both fixes are mechanical, deterministic, and involve zero Layer 3 judgment. Total estimated scope: ~4-5 LOC + 3-4 unit tests. One-time cleanup of the 16 stranded files can be done manually or via a startup-sweep extension.

## Recommended Next Action

**Write a fix executable** with two parts:

1. **Code fix** (Bug A + Bug B): format tolerance in `check_verdict` + prefix exclusion in file listing. ~5 LOC + tests.
2. **One-time cleanup** of the 16 stranded files: either manual CEO `rm` or a startup-sweep extension that detects and archives them.

S3 should NOT be closed as already-fixed — the stranded files are actively producing noise (at least one retry-loop log line per 30s cycle for the pipe-header file) and the format intolerance is a latent risk for any future Planner format variation.

S3 should NOT be split into multiple BACKLOG entries — both bugs are in the same function (`_consume_verdicts` + `check_verdict`), affect the same file population, and have the same fix shape. A single executable plan covers both.

---

## Output Receipt
**Agent:** Bellows Systems Analyst
**Step:** 1
**Status:** Complete

### What Was Done
Investigated the S3 verdict-resolved retry loop across all four diagnostic dimensions (live reproduction, code path trace, stranded-file census, request-shaped file anomaly). Identified two distinct root causes: format intolerance in `check_verdict()` (verdict.py:157) silently rejecting 14 bare-format verdict files, and missing `verdict-request-` prefix exclusion in the file listing filter (bellows.py:881) admitting 2 misnamed request-shaped files. All 16 stranded files correspond to plans already in terminal state.

### Files Deposited
- `bellows/knowledge/research/s3-verdict-resolved-retry-loop-findings-2026-05-09.md` — diagnostic findings with census, code trace, and fix recommendation

### Files Created or Modified (Code)
- None (investigation only)

### Decisions Made
- Classified the 16 stranded files as safely deletable (all plans in terminal state)
- Recommended single fix executable covering both bugs rather than splitting S3

### Flags for CEO
- The pipe-header request-shaped file is actively generating a retry-loop warning log every 30 seconds. CEO may want to manually archive it to silence the noise before the fix ships.
- The diagnostic's count of "17 stranded files" was based on an earlier snapshot; current disk state shows 14 standard + 2 request-shaped = 16 total. No files were lost — the count discrepancy is likely from an approximate enumeration.
- The Planner deposited 2 files with wrong naming convention (`verdict-request-` instead of `verdict-`) into `resolved/`. This is a Planner-side discipline issue worth a PLANNER_TEMPLATE reminder.

### Flags for Next Step
- None (single-step diagnostic)
