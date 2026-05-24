# Remove Pre-scan `processed-` Prefix Rename — Dev Log (v2)
**Date:** 2026-05-24
**Plan:** `executable-remove-pre-scan-processed-rename-v2-2026-05-24`
**Authority:** `knowledge/architecture/processed-prefix-reconsumption-and-rename-skip-2026-05-24.md`

---

## (a) Pre-edit Verification

**Check (i):** `git status --porcelain bellows.py tests/test_consume_verdicts.py`
```
(no output — both files clean)
```

**Check (ii):** `grep -c '_prescan_orphan_logged' bellows.py`
```
3
```

**Check (iii):** `grep -c 'normalized write-time processed- prefix:' bellows.py`
```
1
```

**Check (iv):** `grep -n '^def test_pre_scan' tests/test_consume_verdicts.py`
```
310:def test_pre_scan_renames_processed_verdict_to_canonical():
373:def test_pre_scan_collision_guard_does_not_overwrite():
430:def test_pre_scan_ignores_non_verdict_processed_files():
515:def test_pre_scan_skips_rename_when_no_paired_plan():
572:def test_pre_scan_renames_when_verdict_pending_plan_exists():
629:def test_pre_scan_treats_done_plan_as_no_paired_plan():
681:def test_pre_scan_collision_guard_fires_regardless_of_paired_plan():
```

**Check (v):** `python3 -c "import bellows"`
```
(clean exit — urllib3 SSL warning only, unrelated to bellows)
```

---

## (b) Before/After Line Counts

| File | Before | After | Delta |
|---|---|---|---|
| `bellows.py` | 1453 | 1415 | -38 |
| `tests/test_consume_verdicts.py` | 737 | 346 | -391 |

---

## (c) Task D — Completeness Verification

**`grep -n '^def test_pre_scan' tests/test_consume_verdicts.py`:**
```
(no output — ZERO matches)
```

**`grep -rn '_prescan_orphan_logged' . --include='*.py'`:**
```
(no output — ZERO matches)
```

**`grep -rn 'normalized write-time processed- prefix' . --include='*.py'`:**
```
(no output — ZERO matches)
```

**`grep -c '# Pre-scan: normalize processed-verdict-' bellows.py`:**
```
0
```

---

## (d) Task E — Preservation Check

**`grep -n 'processed-' bellows.py`:**
```
1252:                processed_path = resolved_dir / f"processed-{fname}"
1275:                    processed_path = resolved_dir / f"processed-{fname}"
```

Two legitimate post-consumption rename sites survive. These are the Bellows-side markers that a verdict has been consumed — they produce `processed-verdict-*` files after successful consumption. Not related to the removed pre-scan write-time normalization.

---

## (e) Task F — Import Smoke Check

**`python3 -c "import bellows"`:**
```
(clean exit — urllib3 SSL warning only, unrelated to bellows)
```

---

## (f) Summary

This plan removes the pre-scan `processed-` prefix rename block from `_consume_verdicts` in `bellows.py` (Shape 1c — full removal), as recommended by the 2026-05-24 diagnostic findings at `knowledge/architecture/processed-prefix-reconsumption-and-rename-skip-2026-05-24.md`. The pre-scan was originally shipped in commits `3c9344f` (2026-05-21) and `d1855ba` (2026-05-22) to handle Planner write-time naming mismatches where verdicts were deposited with a `processed-` prefix. However, PLANNER_TEMPLATE v4.49 Rule 25 now prohibits the `processed-` prefix at write time, making the pre-scan a belt-and-suspenders safety net. The diagnostic's Section B identified that the pre-scan causes a P0 infinite loop on multi-step plans that pause for verdict between steps — a worse bug than the one it prevented. Three prior plans attempted this same fix and were halted: `halted-executable-remove-pre-scan-processed-rename-2026-05-24` (incomplete test enumeration from diagnostic findings), `halted-executable-remove-pre-scan-processed-rename-continuation-2026-05-24` (`cd bellows` path error violating bare-path convention), and `halted-executable-remove-pre-scan-processed-rename-continuation-v2-2026-05-24` (worktree-state assumption error — relied on uncommitted main-repo edits from the first halted DEV).

Removed: the module-level `_prescan_orphan_logged: set = set()` declaration, the 34-line pre-scan block, and all seven pre-scan test functions. Preserved: the main verdict consumption loop, the post-consumption `processed-` rename sites, and all non-pre-scan tests.

---

## Output Receipt
**Agent:** Bellows Developer
**Step:** 1
**Status:** Complete

### What Was Done
Removed the pre-scan `processed-` prefix rename block from `_consume_verdicts` in `bellows.py`, the associated `_prescan_orphan_logged` module-level set declaration, and all seven pre-scan test functions from `tests/test_consume_verdicts.py`. Verified completeness (zero dangling references), preservation of legitimate post-consumption rename sites, and clean import.

### Files Deposited
- `knowledge/development/remove-pre-scan-processed-rename-v2-2026-05-24.md` — this dev log

### Files Created or Modified (Code)
- `bellows.py` — removed `_prescan_orphan_logged` declaration (line 33) and pre-scan block (lines 1129-1162); net -38 lines
- `tests/test_consume_verdicts.py` — removed 7 `test_pre_scan_*` functions and section header; net -391 lines

### Decisions Made
- Removed the `# --- Pre-scan orphan dedup ---` section comment along with the `_prescan_orphan_logged` declaration (both serve only the pre-scan)
- Removed the `# --- Pre-scan orphan guard regression tests (2026-05-22) ---` section header in the test file (headed only the removed tests)
- No fixtures or helpers were exclusive to the pre-scan tests, so none were removed

### Flags for CEO
- None

### Flags for Next Step
- The `test_startup_sweep_removes_done_plan_orphans` test at line 310 (previously 474) is the last test in the file and survives correctly — it is NOT a pre-scan test
