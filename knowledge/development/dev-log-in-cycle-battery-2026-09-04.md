# Dev Log — in-cycle-battery-2026-09-04 (plan 100038)

**Instrument:** `tools/fold_signal_census.py`
**Date:** 2026-09-04
**Author:** bellows worktree 100038

---

## Instrument construction

### Design decisions

**Import, do not re-implement.** `fold_check.py` exposes `normalize`, `is_signal`, `ReaderCrashed`, and the three normalizing regexes (`LINE_NO_RE`, `COUNTS_RE`, `DIGIT_RUN_RE`) as module-level names.  The instrument imports them directly.  `normalize_without()` applies the same regexes selectively (skipping one at a time) using the imported regex objects — it is a variant application, not a re-implementation.  `battery_census.detect_battery` is also importable; not used in the census but available.

**Extraction choice.** Historical revisions are written to a tempdir at the same relative path (`<tmpdir>/knowledge/decisions/drafts/<name>.md`).  (o1) signals are excluded from both sides of every fold pair.  Alternative considered: placing the revision at the actual worktree path (overwrite/restore).  Rejected as destructive.  The (o1) exclusion is stated in the research note and applies symmetrically to both sides.

**ReaderCrashed.** Handled as a tallied category, never swallowed.  The `run_tool()` function raises on traceback or empty output; the census counts crashed-before and crashed-after separately and excludes the pair from rate computation.  46 after-crashes were observed: plans deleted from `drafts/` when deposited produce a `git show` failure for the "after" revision.  This is expected behavior.

**Count vocabulary.** Derived per tool from actual output, not from shared patterns:
- `plan_lint`: `(candidates|excluded|fired)=\d+` in INFO lines (not signals)
- `propagation_check`: `DIVERGENCES:\s+\d+` in summary line (not a signal)
- `cycle_check`: no count fields

Position fields excluded (reason: shift on every fold):
- `plan_lint`: `line[= ]\d+` in WARN lines
- `propagation_check`: `L\d+:` in finding bodies

**fold_check's own count form.** Not captured at walk 4 per the plan; measured here from source:
- `readers={N} signals={N}` in `--save-baseline` output (`:167-168`)
- `{label}: exit={code} signals={N}` per reader (`:169`)
- `FOLD-CHECK CLEAN: machine-readable state unchanged ({N} signals held)` (`:185`)

None of these match `is_signal()`.

### Population derivation

`build_populations()` uses `git log --format=%H --name-only -- 'knowledge/decisions/drafts/*.md'` and parses the raw output (SHA, empty line, file list, next SHA immediately following).  The parsing loop advances past the empty line after each SHA and collects files until the next SHA.

Population A: 62 plan files, 321 fold pairs.
Population B: 23 plan files (≥5 commits).

The diagnostic's walk-2 measurement said "20 plans, 8 plans ≥5 commits."  Re-derivation gives larger counts because the corpus has grown (the `u-qa-predicate-align` cycle added 75 commits; the wrap-hook and eluvian-stage cycles added 20+ each).

### Timing methodology

`measure_timing_sample()` runs the first 20 fold pairs.  Of those, 6 produced usable timing results (14 had after-crashes — plans deposited during that batch).  C2 overhead measured as the difference between C2-with-count-extraction and C1-without; result: 0.2ms per fold check.  Conclusion: C2 adds negligible cost.

---

## Questions that proved unanswerable and why

**Q3 (full answer):** Partially unanswerable.  Walk registers record `origin = "fold-introduced (wN-M)"` at the walk level, not at the commit level.  Linking a count-delta commit pair to a register's fold-introduced finding requires mapping walk numbers to commit SHAs — achievable by parsing commit messages ("walk 2 lens 1"), but the mapping is approximate (commits may cover multiple lens passes) and was not implemented.  The one verified instance (5ec0274) was found by looking up the commit in the plan's own history, confirming it was a walk-2 commit.

**Q4 (false-positive rate):** Unanswerable.  Requires Q3's mapping.  The fire rate (26.6% for propagation_check) is measurable; the fraction that is true-positive is not.  Even an upper bound is uncomputable without the mapping.

**Suppression by normalizing regexes:** Zero across all tools and pairs.  This was initially surprising; the reason is structural: count-valued fields that change across folds (`DIVERGENCES`, `candidates/excluded/fired`) live in non-signal lines that `is_signal()` already filters.  The normalizing regexes suppress changes within the signal set; since the signal set doesn't contain those lines, there's nothing to suppress.

---

## Corpus anomalies observed

1. **46 after-crashes** — plans deleted from `drafts/` on deposit.  Expected; counted as crashed, not usable.
2. **4 before-crashes** — older revisions where `git show` returned non-zero (likely a plan that was renamed or moved before the current path was established).
3. **cycle_check: 0 signal changes** — cycle_check's output (`CONTINUE`, `BAR_MET`, `ESCALATE:*`) does not match `is_signal()`.  Adding cycle_check to fold_check's reader set adds zero detections.  This was measured, not assumed.
4. **propagation_check: 3 signal changes** — all from ERROR lines (`ERROR: cannot read` or similar from malformed historical revisions), not from DIVERGENCES detection.

---

## Run command and literal output summary

```
python tools/fold_signal_census.py
```

Key output (literal from the run):
```
Population A: 62 plan files, 321 fold pairs
Population B: 23 plan files
C0 (plan_lint only): 105.4ms/fold-check mean
C1 (all 3 tools):    236.2ms/fold-check mean
C2 (C1+count delta): 236.4ms/fold-check mean

Q2 — normalization impact:
  Signal changed (C0 catches):            83  (30.6%)
  Count changed in full output:           89  (32.8%)
  Count-only change (signal UNCHANGED):   51  (18.8%)
  Neither changed:                       137

Q5 — plan_lint:          signal 80/271 = 29.5%,  count 27/271 = 10.0%
Q5 — propagation_check:  signal  3/271 =  1.1%,  count 72/271 = 26.6%
Q5 — cycle_check:        signal  0/271 =  0.0%,  count  0/271 =  0.0%

Q7: C0=24.8 lines/rev, C1=123.7 lines/rev, C2=123.7 lines/rev
```

P4 verified by separate run against commit `5ec0274`:
```
propagation_check BEFORE: DIVERGENCES: 58
propagation_check AFTER:  DIVERGENCES: 60
plan_lint BEFORE = plan_lint AFTER (same normalized signal set)
cycle_check: CONTINUE on both sides
```
