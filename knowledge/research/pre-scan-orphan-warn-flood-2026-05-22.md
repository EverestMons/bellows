# Pre-Scan Orphan WARN Flood — SA Findings

**Date:** 2026-05-22
**Diagnostic:** pre-scan-orphan-warn-flood-2026-05-22
**Agent:** Bellows Systems Analyst
**Step:** 1 (SA investigation)

---

## 1. Pre-Scan Anchor

**Function:** `_consume_verdicts` in `bellows.py`
**Line range:** 1131–1139 (pre-scan loop)
**Pattern match:** `fname.startswith("processed-verdict-") and fname.endswith(".md")`
**Rename target:** strips `"processed-"` prefix → canonical `verdict-*` form

**Verbatim with context (lines 1127–1139):**

```python
        # Pre-scan: normalize processed-verdict-* to verdict-* (Planner write-time naming mismatch).
        # Files named processed-verdict-* at write time are structurally identical to already-consumed
        # verdicts and would be silently skipped by the main filter. Rename to canonical form so the
        # main loop can process them. See bellows/knowledge/architecture/consume-verdicts-drain-failure-2026-05-21.md.
        for fname in os.listdir(resolved_dir):
            if fname.startswith("processed-verdict-") and fname.endswith(".md"):
                canonical = fname[len("processed-"):]
                canonical_path = os.path.join(resolved_dir, canonical)
                if os.path.exists(canonical_path):
                    _log("WARN", f"cannot normalize {fname} — canonical {canonical} already exists; skipping rename")
                    continue
                shutil.move(os.path.join(resolved_dir, fname), canonical_path)
                _log("WARN", f"normalized write-time processed- prefix: {fname} → {canonical}")
```

**Collision guard:** Lines 1135–1137 — checks if `canonical_path` already exists; if so, logs WARN and skips the rename to avoid data loss.

**Downstream consumption:** The canonical `verdict-*` form is consumed by the main filter loop at line 1142: `if not fname.startswith("verdict-") or not fname.endswith(".md"): continue`. The regex at line 1147 (`^verdict-(.+)-step-(\d+)\.md$`) extracts `plan_slug` and `step_number` from the canonical filename.

---

## 2. No-Match Branch

**Function:** `_consume_verdicts` in `bellows.py`
**Line range:** 1293–1294
**Predicate:** `plan_matched` is `False` AND `stale` is `False` (lines 1261–1294)

**Verbatim with context (lines 1289–1294):**

```python
                if stale:
                    processed_path = resolved_dir / f"processed-{fname}"
                    shutil.move(str(resolved_dir / fname), str(processed_path))
                    _log("WARN", f"⚠️ stale verdict step {step_number} — plan in Done/ or halted-, moving to processed", slug=plan_slug)
                else:
                    _log("WARN", f"⚠️ no verdict-pending plan found step {step_number} — leaving in resolved/ for retry", slug=plan_slug)
```

**WARN message contains:** `[slug] ⚠️ no verdict-pending plan found step {step_number} — leaving in resolved/ for retry`
- Slug: the `plan_slug` extracted by the regex at line 1152 (e.g., `parallel-1-parse-diff-stat-fix-2026-04-16`)
- Step: integer from filename
- File path: not included in the message itself (slug + step identify it)

**30-second cadence:** The `_rescan` method at line 1070 calls `self._consume_verdicts()`. The rescan interval is set at line 1368:

```python
        rescan_interval = 30
```

This is a hardcoded constant, not a config key. Every 30 seconds, `_consume_verdicts` runs, and the no-match branch re-fires for every orphan verdict-* file still in `resolved/`. The WARN message is emitted with no deduplication.

---

## 3. Plan-Existence Check Surface

### Watched Projects (from `config.json`)

| # | Watched `decisions/` Path | `Done/` Path |
|---|---|---|
| 1 | `/Users/marklehn/Developer/GitHub/invoice-pulse/knowledge/decisions` | `.../decisions/Done/` |
| 2 | `/Users/marklehn/Developer/GitHub/BrewBuddy/knowledge/decisions` | `.../decisions/Done/` |
| 3 | `/Users/marklehn/Developer/GitHub/study/knowledge/decisions` | `.../decisions/Done/` |
| 4 | `/Users/marklehn/Developer/GitHub/ai-career-digest/knowledge/decisions` | `.../decisions/Done/` |
| 5 | `/Users/marklehn/Developer/GitHub/freight-kb/knowledge/decisions` | `.../decisions/Done/` |
| 6 | `/Users/marklehn/Developer/GitHub/forge/knowledge/decisions` | `.../decisions/Done/` |
| 7 | `/Users/marklehn/Developer/GitHub/anvil/knowledge/decisions` | `.../decisions/Done/` |
| 8 | `/Users/marklehn/Developer/GitHub/bellows/knowledge/decisions` | `.../decisions/Done/` |
| 9 | `/Users/marklehn/Developer/GitHub/lessons-forge/knowledge/decisions` | `.../decisions/Done/` |
| 10 | `/Users/marklehn/Developer/GitHub/governance/knowledge/decisions` | `.../decisions/Done/` |

### Check Semantics

The existence check should look **ONLY in `decisions/`** for `verdict-pending-*` files (active plan — rename is correct). It should **NOT** look in `Done/` or for `halted-*` files.

**Reasoning:** A `processed-verdict-*` file paired to a plan that has moved to `Done/` or `halted-*` is a legitimately consumed verdict whose plan reached terminal state. Renaming it back to `verdict-*` forces the main loop's stale-check branch to re-process it (renaming it back to `processed-*`), creating a pointless ping-pong cycle. The only scenario where rename is correct is when a `verdict-pending-*` plan still exists in `decisions/` — meaning the verdict is pending re-evaluation.

The distinction is binary:
- `verdict-pending-*` exists in `decisions/` → **rename** (pre-scan repair is needed)
- No `verdict-pending-*` exists → **skip** (plan is terminal or gone, file is correctly `processed-`)

---

## 4. Slug Extraction

**Function:** `verdict.slug_from_path()` in `verdict.py`, lines 82–92.

```python
def slug_from_path(plan_path):
    """Extract a slug from a plan path for use in verdict filenames."""
    basename = os.path.basename(plan_path)
    # Strip common prefixes
    for prefix in ("in-progress-", "verdict-pending-", "executable-", "diagnostic-"):
        if basename.startswith(prefix):
            basename = basename[len(prefix):]
    # Strip .md extension
    if basename.endswith(".md"):
        basename = basename[:-3]
    return basename
```

**Output format:** e.g., `slug_from_path("executable-foo-2026-05-01.md")` → `"foo-2026-05-01"`.

### Slug Matching for the Pre-Scan Guard

The pre-scan guard does NOT need `slug_from_path()` directly. The flow is:

1. **Pre-scan file:** `processed-verdict-<plan_slug>-step-N.md`
2. **Strip `processed-`:** → `verdict-<plan_slug>-step-N.md`
3. **Apply main-loop regex:** `^verdict-(.+)-step-(\d+)\.md$` → group(1) = `plan_slug`
4. **Search decisions dirs:** look for files matching `verdict-pending-*` that contain `plan_slug`

The `plan_slug` extracted at step 3 may include a plan-type prefix (e.g., `diagnostic-foo-2026-05-21`). The `verdict-pending-` filenames have the form `verdict-pending-diagnostic-foo-2026-05-21.md`. The existing main-loop check at line 1199 uses substring matching:

```python
if pname.startswith("verdict-pending-") and plan_slug in pname:
```

This same substring match works for the new guard — no normalization step is needed. The `plan_slug` from the verdict filename directly substring-matches against `verdict-pending-*` plan filenames.

---

## 5. Orphan Census

### Current State (2026-05-22)

10 files in canonical `verdict-*` form exist in `verdicts/resolved/`:

| Filename | Slug | Paired Plan Location | First Observed |
|---|---|---|---|
| `verdict-action-queue-aggregation-2026-05-07-step-3.md` | `action-queue-aggregation-2026-05-07` | none | 2026-05-21 (mass rename) |
| `verdict-aggregated-queue-carrier-customer-display-2026-05-07-step-1.md` | `aggregated-queue-carrier-customer-display-2026-05-07` | none | 2026-05-21 (mass rename) |
| `verdict-aggregated-queue-customer-display-2026-05-07-step-2.md` | `aggregated-queue-customer-display-2026-05-07` | none | 2026-05-21 (mass rename) |
| `verdict-billto-csv-header-resilience-2026-05-14-step-2.md` | `billto-csv-header-resilience-2026-05-14` | Done (invoice-pulse) | 2026-05-21 (mass rename) |
| `verdict-diagnostic-action-queue-aggregation-2026-05-07-step-1.md` | `diagnostic-action-queue-aggregation-2026-05-07` | none | 2026-05-21 (mass rename) |
| `verdict-half-up-currency-rounding-2026-05-06-step-1 2.md` | `half-up-currency-rounding-2026-05-06` | Done (invoice-pulse) | pre-2026-05-21 (Finder duplicate) |
| `verdict-parallel-1-parse-diff-stat-fix-2026-04-16-step-1.md` | `parallel-1-parse-diff-stat-fix-2026-04-16` | none | 2026-05-21 (mass rename) |
| `verdict-parallel-1-verdict-readme-2026-04-16-step-1.md` | `parallel-1-verdict-readme-2026-04-16` | none | 2026-05-21 (mass rename) |
| `verdict-qa-report-rule-20-banner-fix-2026-05-07-step-2.md` | `qa-report-rule-20-banner-fix-2026-05-07` | none | 2026-05-21 (mass rename) |
| `verdict-session-wrap-action-queue-aggregation-2026-05-07-step-1.md` | `session-wrap-action-queue-aggregation-2026-05-07` | none | 2026-05-21 (mass rename) |

**Summary:** 8 orphans with no paired plan anywhere. 2 orphans with plans in `Done/` (stale check should catch these but they persist because the pre-scan re-creates them each cycle). The BACKLOG entry cited 8 specific orphans on 2026-05-21 — these are the same 8 "no plan anywhere" files. 2 additional files exist: `billto-csv-header-resilience` and `half-up-currency-rounding` (the latter is a Finder duplicate with a space in the filename — `step-1 2.md` — which won't match the main-loop regex and is permanently inert).

**Note on `verdict-half-up-currency-rounding-2026-05-06-step-1 2.md`:** The space before `2.md` means this file does NOT match `^verdict-(.+)-step-(\d+)\.md$` and is silently skipped by the main loop. It is not contributing to the WARN flood but is clutter.

---

## 6. Population Audit — Rename Event Classification

### Log Data (2026-05-22)

| Metric | Count |
|---|---|
| Total pre-scan rename events (`normalized write-time processed-`) | 8,823 |
| Unique files renamed per cycle | 402 |
| Total stale verdict events (`stale verdict step N`) | 10,827 |
| Unique stale verdict slugs | 313 |
| Total no-match WARN events (`no verdict-pending plan found`) | 176 |
| Unique no-match slugs | 8 |
| Collision guard events (`cannot normalize`) | ~22 cycles × 10 files = ~220 |
| Estimated cycles running | ~22 (176 WARN / 8 unique slugs) |

### Classification by Paired-Plan State

| Class | Description | Count (unique files) | Behavior |
|---|---|---|---|
| **(a) Active plan in `decisions/` as `verdict-pending-*`** | Legitimate rename — pre-scan repair works as designed | **0 observed on 2026-05-22** | Correctly renamed, consumed by main loop |
| **(b) Plan in `Done/`** | Orphan creation — pre-scan causes stale-check ping-pong | **~313** | Renamed → stale check moves back → repeats every 30s |
| **(c) Plan in `halted-*`** | Orphan creation under terminal state | **included in (b) count** | Same ping-pong behavior |
| **(d) No paired plan anywhere** | Orphan creation, plan long gone | **8** | Renamed → no-match WARN → stays as `verdict-*` → no further pre-scan action |

**Dominant class today: (b) — stale-check ping-pong.** 313 unique slugs are being renamed every 30 seconds, only to be immediately moved back to `processed-*` by the stale check. This accounts for 8,823 renames and 10,827 stale-verdict log entries in a single day. Class (a) — the legitimate use case — has **zero** instances on 2026-05-22. The pre-scan is currently doing no useful work.

### Historical Note (2026-05-21)

The pre-scan was introduced by `executable-consume-verdicts-prefix-fix-2026-05-21`. The mass-rename event at 21:31:34 on 2026-05-21 was the first cycle after deployment. 10,061 WARN floods were recorded on 2026-05-21 from the initial 8 orphans.

---

## 7. Edge Case — Collision Guard Interaction

The existing collision guard (lines 1135–1137) fires when both `processed-verdict-X.md` and `verdict-X.md` coexist. This protects against overwriting a canonical file that may be in active consumption by the main loop.

### Guard Composition

The new "skip rename when no paired plan" guard and the existing collision guard **compose without conflict**. Recommended evaluation order: **orphan-check first, then collision**.

```
for each processed-verdict-* file:
    1. [NEW] Extract plan_slug. Check if verdict-pending-*{plan_slug}* exists in any decisions/.
       If NOT found → skip rename (orphan). Log once at INFO. Continue to next file.
    2. [EXISTING] Check if canonical verdict-* already exists.
       If EXISTS → skip rename (collision). Log WARN. Continue to next file.
    3. Both guards passed → rename processed-verdict-* to verdict-*.
```

**Reasoning for orphan-check-first order:**
- Efficiency: the orphan check eliminates ~99.7% of files (402 total, ~0 legitimate) before the filesystem collision check runs.
- Correctness: an orphan file should never be renamed regardless of collision state. Checking orphan first avoids a misleading "collision" WARN for files that shouldn't be renamed at all.
- No regression: the collision guard still fires for the (currently zero) legitimate rename cases where both forms happen to coexist.

---

## 8. Recommendation — Gap Assessment

| Gap | Current State | Proposed State | Change Required |
|---|---|---|---|
| **(a) Pre-scan unconditional rename** | All `processed-verdict-*` files renamed to `verdict-*` every 30s (402 files/cycle, 8,823 renames/day) | Only rename when a `verdict-pending-*{plan_slug}*` file exists in at least one watched `decisions/` directory | `bellows.py` lines 1131–1139: add plan-existence guard before `shutil.move`. Extract `plan_slug` via regex, scan `self.config["watched_projects"]` for `verdict-pending-*` match. ~15 LOC. |
| **(b) Plan-existence check helper** | No existing function does this check | Inline loop in pre-scan or new helper function `_has_active_plan(plan_slug, watched_projects)` | `bellows.py`: new helper (~8 LOC) or inline in pre-scan. Reuses the same `plan_slug in pname` substring match as line 1199. |
| **(c) Log line for skipped orphan** | No logging for skipped files | One-shot INFO per skipped orphan per daemon lifetime, suppressed on subsequent cycles | Use a module-level `_prescan_orphan_logged: set` to deduplicate. Log at INFO: `"pre-scan: skipping orphan {fname} — no active verdict-pending plan"`. Not WARN (it's expected state). ~5 LOC. |
| **(d) Cleanup of existing orphans in `resolved/`** | 10 orphan `verdict-*` files exist; 8 have no paired plan; 2 have plans in `Done/` | The new guard suppresses future orphan creation. Existing `verdict-*` orphans are handled by the main loop's stale check (2 files) or no-match branch (8 files). The 8 true orphans need a **one-shot migration** in the executable: rename them back to `processed-verdict-*` so the pre-scan (with the new guard) correctly skips them going forward. Without this, the 8 files remain as `verdict-*` and the no-match WARN continues for them. | Executable one-shot: for each `verdict-*` in `resolved/` with no paired plan, rename to `processed-verdict-*`. ~10 LOC in the executable's migration section. Alternative: add the same orphan check to the main loop's no-match branch to move orphans to `processed-*` when detected. |

### File and LOC Summary

| File | Change | Approx LOC |
|---|---|---|
| `bellows.py` lines 1131–1139 | Add plan-existence guard to pre-scan loop | +15–20 |
| `bellows.py` (module level) | Add `_prescan_orphan_logged` dedup set | +1 |
| `bellows.py` (one-shot migration) | Rename existing `verdict-*` orphans to `processed-*` | +10 (executable, not permanent code) |
| `tests/test_consume_verdicts.py` | New regression tests (see Q9) | +80–100 |

---

## 9. Daemon Restart and Test Coverage

### Daemon Restart

Yes, the proposed change requires a daemon restart to load. Like every Bellows-side code change, `bellows.py` is loaded once at daemon startup. Hot-reload is not supported.

### Existing Test File

`tests/test_consume_verdicts.py` — full read completed. 505 lines, 8 existing tests.

### Existing Test Fixtures

The existing tests use a consistent pattern:

```python
with tempfile.TemporaryDirectory() as tmp:
    tmp_path = Path(tmp)
    decisions_dir = tmp_path / "proj" / "knowledge" / "decisions"
    decisions_dir.mkdir(parents=True)
    done_dir = decisions_dir / "Done"
    done_dir.mkdir()
    verdicts_resolved = tmp_path / "verdicts" / "resolved"
    verdicts_resolved.mkdir(parents=True)
    pending_dir = tmp_path / "verdicts" / "pending"
    pending_dir.mkdir(parents=True)

    config = {
        "watched_projects": [str(decisions_dir)],
        "default_model": "claude-sonnet-4-6",
        "pushover": {"app_key": "", "user_key": ""},
        "callback_port": 5999,
    }
    b = bellows.Bellows(config)
    with patch("bellows.BELLOWS_ROOT", tmp_path), ...:
        b._consume_verdicts()
```

Key fixture elements:
- `tempfile.TemporaryDirectory` for isolation
- `decisions_dir` with `Done/` subdirectory
- `verdicts_resolved` and `pending_dir`
- `config` with single watched project
- `patch("bellows.BELLOWS_ROOT", tmp_path)` to redirect BELLOWS_ROOT
- Patches for `verdict.check_verdict`, `verdict.log_to_ledger`, `notifier.push`

### Proposed Regression Tests (4 tests)

**(a) `test_pre_scan_skips_rename_when_no_paired_plan`**
- Setup: `processed-verdict-foo-2026-05-22-step-1.md` in `resolved/`. No plan file anywhere in `decisions/` or `Done/`.
- Assert: `processed-verdict-*` file is NOT renamed to `verdict-*`. File stays as `processed-*`.
- Assert: INFO log emitted (not WARN).

**(b) `test_pre_scan_renames_when_verdict_pending_plan_exists`**
- Setup: `processed-verdict-foo-2026-05-22-step-1.md` in `resolved/`. `verdict-pending-diagnostic-foo-2026-05-22.md` in `decisions/`.
- Assert: file renamed to `verdict-foo-2026-05-22-step-1.md` (existing behavior preserved).
- Mirror: `test_pre_scan_renames_processed_verdict_to_canonical` (line 310).

**(c) `test_pre_scan_treats_done_plan_as_no_paired_plan`**
- Setup: `processed-verdict-foo-2026-05-22-step-1.md` in `resolved/`. Plan in `Done/` only (e.g., `Done/diagnostic-foo-2026-05-22.md`). No `verdict-pending-*` in `decisions/`.
- Assert: `processed-verdict-*` file is NOT renamed. `Done/` plan does not count as a paired plan.

**(d) `test_pre_scan_collision_guard_fires_regardless_of_paired_plan`**
- Setup: Both `processed-verdict-foo-step-1.md` and `verdict-foo-step-1.md` exist. `verdict-pending-diagnostic-foo.md` exists in `decisions/` (paired plan IS present).
- Assert: collision guard still fires (skip rename), WARN emitted. The paired-plan guard does NOT bypass the collision guard.
- Mirror: `test_pre_scan_collision_guard_does_not_overwrite` (line 373).

---

## Output Receipt

**Agent:** Bellows Systems Analyst
**Step:** 1 (SA investigation)
**Status:** Complete

### What Was Done
Traced the pre-scan rename loop in `_consume_verdicts`, characterized the no-match WARN flood mechanism, performed orphan census, classified 8,823 daily rename events by paired-plan state, and produced a gap assessment with exact line anchors for a future executable.

### Files Deposited
- `bellows/knowledge/research/pre-scan-orphan-warn-flood-2026-05-22.md` — SA findings (this file)

### Files Created or Modified (Code)
- None (read-only investigation)

### Decisions Made
- Guard evaluation order: orphan-check first, then collision (efficiency + correctness)
- Log level for skipped orphans: INFO (not WARN — orphan state is expected, not anomalous)
- One-shot migration needed for 8 existing orphan verdict-* files

### Flags for CEO
- None

### Flags for Next Step
- The `verdict-half-up-currency-rounding-2026-05-06-step-1 2.md` file (Finder duplicate with space in name) is permanently inert — it never matches the main-loop regex. It should be manually deleted as part of the one-shot migration or left as harmless clutter.
- The 402-file-per-cycle rename churn (class b: stale ping-pong) is the largest I/O cost. The new guard eliminates this entirely since none of those 402 files have active `verdict-pending-*` plans.
