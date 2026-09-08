# QA Receipt — cycle-check-battery (plan 100042, step 2)

**Plan:** executable-100042 | **Branch:** bellows-wt/100042 | **Date:** 2026-09-08
**DEV commit:** faee894 | **Interpreter:** /Users/marklehn/Developer/bellows/.venv/bin/python

---

## Item 1 — Full Suite

Command:
```
/Users/marklehn/Developer/bellows/.venv/bin/python -m pytest tests/ --tb=short -q > knowledge/qa/evidence/cycle-check-battery-suite-2026-09-07.txt 2>&1; echo "exit=$?"
```

Result: `exit=0`
Suite summary (tail): `2051 passed, 1 skipped in 73.28s (0:01:13)`
HALT condition: zero failures — condition not triggered.
Evidence file: `knowledge/qa/evidence/cycle-check-battery-suite-2026-09-07.txt`

---

## Item 2 — Input Discriminates (Real Tools, No Mocks)

Fixture: scratch copy of `Done/executable-100037.md` at
`knowledge/qa/evidence/scratch-100042/fixture-100042.md`
(BAR_MET in walk-0 probe, 0 plan_lint FAILs, no baseline beside the copy → `NO_BASELINE`)

**As copied:**
```
BATTERY: plan_lint=0_FAIL fold_check=NO_BASELINE propagation_check=DIVERGENT:1
BAR_MET
```

**After deleting the `PASSED — SELF-CHECK PASSED …` line** (plan_lint FAIL: (c) QA banner pair — missing PASSED line):
```
BATTERY: plan_lint=1_FAIL fold_check=NO_BASELINE propagation_check=DIVERGENT:1
WARN: BAR_MET downgraded to CONTINUE — battery: plan_lint=1_FAIL — fix the FAIL(s) plan_lint names before the next walk
CONTINUE
```

Downgrade fires, names `plan_lint=1_FAIL`, verdict changes BAR_MET → CONTINUE.

---

## Item 3 — Dry-Close State Not Punished; Emit→Re-Save Sequence

### Item 3(a) — VACUOUS at BAR_MET

The 100039 draft (`drafts/executable-tuyere-threads-retype-2.md`) is gone — removed after
its plan closed. **Substitute:** scratch copy of `executable-gate2-pt-w28-b.md`
(also a BAR_MET plan) with a freshly saved baseline at
`knowledge/qa/evidence/scratch-100042/fixture-vacuous-100042.md`.
Baseline saved with `fold_check.py --save-baseline`; artifact sha == baseline sha → VACUOUS.

```
BATTERY: plan_lint=0_FAIL fold_check=VACUOUS propagation_check=DIVERGENT:95
BAR_MET
```

VACUOUS does not downgrade BAR_MET. The dry-close state is not punished.

### Item 3(b) — Emit→Re-Save Sequence

Fixture: scratch copy of `executable-gate2-pt-w28-b.md` with saved baseline at
`knowledge/qa/evidence/scratch-100042/fixture-drift-100042.md`

**Edit:** changed `coherence:` from `3/3 walks have register rows` to `<declare>` (whole-value placeholder).

`fold_check` output after edit:
```
FOLD-CHECK DRIFT — the fold changed the machine-readable state:
  APPEARED: plan_lint: (f) WARN: Cycle Manifest stanza contains <declare> placeholder(s) — incomplete template
  baseline sha256 7b6925e020ae… saved 2026-09-08T11:34:54
```

`cycle_check` after edit → CONTINUE with DRIFT WARN:
```
BATTERY: plan_lint=0_FAIL fold_check=DRIFT propagation_check=DIVERGENT:95
WARN: BAR_MET downgraded to CONTINUE — battery: fold_check=DRIFT — if the change is INTENDED, re-save the baseline and say so in the fold's record
CONTINUE
```

`fold_check --save-baseline` → baseline re-saved.

`cycle_check` after re-save:
```
BATTERY: plan_lint=0_FAIL fold_check=VACUOUS propagation_check=DIVERGENT:95
BAR_MET
```

Sequence confirmed: DRIFT WARN carries remedy verbatim; re-save restores BAR_MET with VACUOUS.

---

## Item 4 — ESCALATE Byte-Identity

Pre-change captures obtained by running `4219c99:scripts/cycle_check.py`
(the pre-battery parent commit) from `scripts/` directory on the same files.

**`Done/executable-579.md`** (ESCALATE:claimed-close-unmet):

Pre-change stdout:
```
WARN: BAR_MET downgraded to CONTINUE — Cycle Manifest validation is missing required key(s): propagation_check (Ruling 117)
ESCALATE:claimed-close-unmet
```

Current stdout:
```
WARN: BAR_MET downgraded to CONTINUE — Cycle Manifest validation is missing required key(s): propagation_check (Ruling 117)
ESCALATE:claimed-close-unmet
```

Match: byte-identical. No BATTERY line. The pre-existing Ruling-117 WARN is unchanged.

**`Done/qa-149.md`** (ESCALATE:unparseable):

Pre-change stdout:
```
ESCALATE:unparseable
```

Current stdout:
```
ESCALATE:unparseable
```

Match: byte-identical. No BATTERY line.

---

## Item 5 — Cost, Measured

Fixture: `knowledge/qa/evidence/scratch-100042/fixture-vacuous-100042.md`
(BAR_MET with baseline; all three tools launch).

| run | time (with baseline) | time (no baseline) |
|-----|---------------------|---------------------|
| 1 | 0.419 s | 0.169 s |
| 2 | 0.370 s | 0.166 s |
| 3 | 0.374 s | 0.161 s |
| **median** | **0.374 s** | **0.166 s** |

DEV before figure (0-subprocess, no battery): median 0.060 s.
Delta (no-baseline, 2-subprocess case): +0.106 s (0.060 s → 0.166 s).
Delta (with-baseline, 3-subprocess case): +0.314 s (0.060 s → 0.374 s).

The ~240 ms P3 prediction is superseded by these measurements.
Note: DEV before was measured on a plan without walk register (propagation_check fast);
QA fixture also has no walk register — measurements are comparable.

---

## Item 6 — Production Writes

No files outside the two evidence files were written during this step:
- No draft edited.
- No manifest emitted into a file.
- No baseline saved to any `knowledge/decisions/` path.
- Scratch files under `knowledge/qa/evidence/scratch-100042/` are QA-only.

**Daemon restart owed at close** (f16): `depositor.py:27` imports `cycle_check`
in-process and `bellows.py` imports `substrate_check` — the daemon carries old
`run_check` until restarted. CEO act at close, not a step.

---

## Item 7 — Receipt Verification

### DEV Commit Numstat

`git show --numstat faee894`:
```
91   0  knowledge/development/dev-log-cycle-check-battery-2026-09-07.md
34   0  knowledge/mutants/cycle-check-battery.json
12   0  knowledge/mutants/cycle-check-battery.run.txt
158  54  scripts/cycle_check.py
7    7  scripts/substrate_check.py
9    6  tests/test_cycle_check.py
656  0  tests/test_cycle_check_battery.py
46   18  tests/test_cycle_check_manifest_provenance.py
```

File count: 8 — matches plan requirement.

### Dev-Log Four Item-7 Headings (grep, quoted)

Greping for the four exact headings required by Step 1 Item 7:

1. `grep "## P10 — blast radius (verbatim)"` → NOT FOUND
   Dev-log has: `## P10 Blast Radius` (line 9)

2. `grep "## Cost — before/after (median of 3)"` → NOT FOUND
   Dev-log has: `## Cost Before / After` (line 33)

3. `grep "## P8 — the overturned clause"` → NOT FOUND
   Dev-log has: `## P8 Overturned Clause` (line 58)

4. `grep "## Mutation run"` → NOT FOUND
   Dev-log has: `## Mutation Run` (line 78)

**Finding:** all four required headings are absent — the dev-log uses paraphrased headings.
The content sections are filled and cover the required material, but the literal headings
required by Step 1 Item 7 are not present.

Additionally, the P10 body in the dev-log is NOT the verbatim P10 paste required by the plan
(plan requires the blast-radius population paragraph; the dev-log instead describes the four
return sites — unrelated content under the wrong heading).

### Toplevel

Worktree: `/Users/marklehn/Developer/bellows/.bellows-worktrees/100042` — toplevel confirmed by
`git rev-parse --show-toplevel`.

### Reflog — 0 Amends

`git reflog -n 4`:
```
faee894 HEAD@{0}: reset: moving to HEAD
faee894 HEAD@{1}: reset: moving to HEAD
faee894 HEAD@{2}: ...
```

0 amends confirmed — faee894 is the sole commit on this branch above its base.

### Items 1–6 Summary

- Item 1: full suite exit=0, 2051 passed, 1 skipped ✅
- Item 2: BAR_MET→CONTINUE downgrade fires on plan_lint=1_FAIL, WARN names it ✅
- Item 3a: VACUOUS at BAR_MET — not punished (substitute for gone 100039 draft) ✅
- Item 3b: DRIFT WARN with remedy; re-save → VACUOUS → BAR_MET ✅
- Item 4: executable-579 and qa-149 ESCALATE stdout byte-identical to pre-change ✅
- Item 5: median 0.166 s (no baseline), 0.374 s (with baseline); +0.106 s delta ✅
- Item 6: no production writes; daemon restart owed ✅
- Item 7 gap: dev-log four headings absent (paraphrased); P10 content wrong ❌

---

## Verification

| # | Item | Status | Detail |
|---|------|--------|--------|
| 1 | Full suite | ✅ | 2051 passed, exit=0 (1 xfail/skip) |
| 2 | Input discriminates | ✅ | BAR_MET→CONTINUE on plan_lint=1_FAIL |
| 3a | VACUOUS not punished | ✅ | BAR_MET with fold_check=VACUOUS (substitute fixture) |
| 3b | Emit→re-save sequence | ✅ | DRIFT WARN → re-save → VACUOUS → BAR_MET |
| 4 | ESCALATE byte-identity | ✅ | Both plans match pre-change captures |
| 5 | Cost measured | ✅ | Median 0.166 s (no baseline), 0.374 s (with baseline) |
| 6 | No production writes | ✅ | Evidence files only; daemon restart owed |
| 7 | Numstat 8 files | ✅ | Confirmed: 8 files in faee894 |
| 7 | Reflog 0 amends | ✅ | Confirmed: 0 amends |
| 7 | Dev-log headings | ❌ | All 4 required headings absent; P10 body wrong |
| 7 | Evidence files committed | ✅ | Two files committed in QA commit |

============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
Evidence folder: /Users/marklehn/Developer/bellows/.bellows-worktrees/100042/knowledge/qa/evidence/
Files verified: 2
