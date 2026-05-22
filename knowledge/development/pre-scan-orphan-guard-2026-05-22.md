# Pre-Scan Orphan Guard — Dev Log

**Date:** 2026-05-22
**Plan:** executable-pre-scan-orphan-guard-2026-05-22
**Authority:** `knowledge/research/pre-scan-orphan-warn-flood-2026-05-22.md` (SA diagnostic)

---

## 1. Before/After Snippet — Pre-Scan Loop

### Before (bellows.py:1127-1141)

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

### After (bellows.py:1129-1162)

```python
        # Pre-scan: normalize processed-verdict-* to verdict-* (Planner write-time naming mismatch).
        # Files named processed-verdict-* at write time are structurally identical to already-consumed
        # verdicts and would be silently skipped by the main filter. Rename to canonical form so the
        # main loop can process them. See bellows/knowledge/architecture/consume-verdicts-drain-failure-2026-05-21.md.
        for fname in os.listdir(resolved_dir):
            if fname.startswith("processed-verdict-") and fname.endswith(".md"):
                # Orphan check (fires BEFORE collision guard): only rename if a
                # verdict-pending-* plan exists in a watched decisions/ directory.
                # Plans in Done/ or halted-* are terminal — leave as processed-*.
                slug_match = re.match(r"^processed-verdict-(.+)-step-(\d+)\.md$", fname)
                if slug_match:
                    plan_slug = slug_match.group(1)
                    has_paired_plan = False
                    for decisions_path in self.config.get("watched_projects", []):
                        if not os.path.isdir(decisions_path):
                            continue
                        for pname in os.listdir(decisions_path):
                            if pname.startswith("verdict-pending-") and plan_slug in pname:
                                has_paired_plan = True
                                break
                        if has_paired_plan:
                            break
                    if not has_paired_plan:
                        if fname not in _prescan_orphan_logged:
                            _log("INFO", f"pre-scan: skipping orphan {fname} — no active verdict-pending plan")
                            _prescan_orphan_logged.add(fname)
                        continue
                canonical = fname[len("processed-"):]
                canonical_path = os.path.join(resolved_dir, canonical)
                if os.path.exists(canonical_path):
                    _log("WARN", f"cannot normalize {fname} — canonical {canonical} already exists; skipping rename")
                    continue
                shutil.move(os.path.join(resolved_dir, fname), canonical_path)
                _log("WARN", f"normalized write-time processed- prefix: {fname} → {canonical}")
```

## 2. Module-Level Dedup Set

`_prescan_orphan_logged: set = set()` initialized at **line 33** of `bellows.py`, in the module-level constants section between `MISPLACED_VERDICT_SCAN_VERBOSE` and the terminal output infrastructure block.

## 3. Migration Script Output

Script: `scripts/migrate_orphan_verdicts.py` (one-shot, not permanent code).

```
  REMOVED duplicate canonical (processed- form already exists): verdict-action-queue-aggregation-2026-05-07-step-3.md
  REMOVED duplicate canonical (processed- form already exists): verdict-aggregated-queue-carrier-customer-display-2026-05-07-step-1.md
  REMOVED duplicate canonical (processed- form already exists): verdict-aggregated-queue-customer-display-2026-05-07-step-2.md
  REMOVED duplicate canonical (processed- form already exists): verdict-billto-csv-header-resilience-2026-05-14-step-2.md
  REMOVED duplicate canonical (processed- form already exists): verdict-diagnostic-action-queue-aggregation-2026-05-07-step-1.md
  SKIP (no slug match): verdict-half-up-currency-rounding-2026-05-06-step-1 2.md
  REMOVED duplicate canonical (processed- form already exists): verdict-parallel-1-parse-diff-stat-fix-2026-04-16-step-1.md
  REMOVED duplicate canonical (processed- form already exists): verdict-parallel-1-verdict-readme-2026-04-16-step-1.md
  REMOVED duplicate canonical (processed- form already exists): verdict-qa-report-rule-20-banner-fix-2026-05-07-step-2.md
  REMOVED duplicate canonical (processed- form already exists): verdict-session-wrap-action-queue-aggregation-2026-05-07-step-1.md

--- Migration Summary ---
Orphans found:       9
Orphans renamed:     9
Skipped (collision): 0
Skipped (no slug):   1
```

**Counts:** 9 orphans found (all had both canonical and processed- forms due to ping-pong cycle), 9 canonical duplicates removed, 1 file skipped (malformed filename with space: `verdict-half-up-currency-rounding-2026-05-06-step-1 2.md`).

## 4. Summary

The 2026-05-22 pre-scan orphan WARN flood diagnostic identified that the pre-scan loop at `bellows.py:1131-1139` unconditionally renamed every `processed-verdict-*.md` file to canonical `verdict-*.md` form, regardless of whether a paired `verdict-pending-*` plan still existed. This produced ~8,823 rename events and ~10,827 stale-verdict events per day across 313 stale plan slugs. The fix adds an orphan-check guard that extracts the plan slug from each `processed-verdict-*` filename and scans all watched `decisions/` directories for an active `verdict-pending-*` match before allowing the rename. Files with no paired plan are left in `processed-*` form with a one-shot INFO log (deduplicated by daemon lifetime). A one-shot migration cleaned up 9 existing canonical orphans in `verdicts/resolved/`.

---
## Output Receipt
**Agent:** Bellows Developer
**Step:** 1
**Status:** Complete

### What Was Done
Added orphan-check guard to the pre-scan loop in `_consume_verdicts` that skips rename when no paired `verdict-pending-*` plan exists. Added module-level dedup set for INFO log suppression. Ran one-shot migration to clean 9 orphan canonical verdict files from `verdicts/resolved/`.

### Files Deposited
- `knowledge/development/pre-scan-orphan-guard-2026-05-22.md` — this dev log
- `knowledge/development/pre-scan-orphan-migration-output-2026-05-22.txt` — migration script output

### Files Created or Modified (Code)
- `bellows.py` — added `_prescan_orphan_logged` set (line 33) and orphan-check guard in pre-scan loop (lines 1135-1155)

### Decisions Made
- Migration handled collision case (both forms exist) by removing the duplicate canonical form, since diff confirmed they were identical content from the ping-pong cycle
- 1 malformed file (`verdict-half-up-currency-rounding-2026-05-06-step-1 2.md`) left untouched — filename has embedded space, doesn't match regex

### Flags for CEO
- None

### Flags for Next Step
- The malformed file `verdict-half-up-currency-rounding-2026-05-06-step-1 2.md` remains in `resolved/` — QA may want to note this as a known anomaly
- Migration script at `scripts/migrate_orphan_verdicts.py` is one-shot; not permanent code
