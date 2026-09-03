# QA Receipt — register-validate-first-2026-09-03

**Plan:** 100030 — validate BEFORE exempting (corrective for 100029)
**Step:** 2 (QA)
**Date:** 2026-09-03
**Worktree:** /Users/marklehn/Developer/bellows/.bellows-worktrees/100030
**Commit at QA:** 24056aa

---

## Restored Counts (supersede authoring pins)

| Metric | Oracle (7349c89) | HEAD (post-fix) | Delta |
|---|---|---|---|
| CONFORMANT registers | 108 | 108 | +17 vs 100029 defect state (91) |
| fold rows (stdout, excl. header) | 2836 | 2836 | +424 vs 100029 defect state (2412) |
| Oracle-disagreement set size | — | **0** | EMPTY — post-condition MET |

Corpus: 160 files in `/Users/marklehn/Developer/eluvian-governance/governance/knowledge/research/`, 159 walk-register files (1 draft- prefix excluded from register set).

CONFORMANT rises vs 100029 defect state: 91 → 108 (+17). Fold rows rise: 2412 → 2836 (+424). Both invariants met.

All 12 HEAD LEGACY_SCHEMA registers are UNCONFORMANT or NO_TABLE under the oracle — no register that genuinely conforms is exempted.

---

## Verification

| # | Item | Status |
|---|---|---|
| 1 | Full suite from worktree — 1841 passed, 1 pytest-marked exclusion, 0 failed; no config.json at root | ✅ |
| 2.1 | BEFORE/AFTER corpus pair — CONFORMANT 108→108, rows 2836→2836; oracle-disagreement set EMPTY (0) | ✅ |
| 2.2 | walk-register-classify-307-318-2026-08-11.md (declares 0.1, v0.3 shape) → CONFORMANT, 7 rows | ✅ |
| 2.3 | Wrong-shaped legacy register (walk-register-auto-confirm-on-agreement-2026-08-11.md) → LEGACY_SCHEMA | ✅ |
| 2.4 | Negative control (walk-register-bellows-bootstrap-2026-09-02.md, v0.3) → CONFORMANT, 14 rows | ✅ |
| 2.5 | run_check register — VERDICT=FAIL (14 pre-existing UNCONFORMANT/NO_TABLE); LEGACY_SCHEMA not counted | ✅ |
| 3 | mutation_check all 3 manifests — 6 killed, 0 survived, 0 ERROR | ✅ |
| 4 | Hygiene — numstat 6 files, 0 amends in reflog | ✅ |
| 5 | Evidence commit — 3 files (qa-receipt.md, probes-raw.txt, pytest_full.txt) | ✅ |

---

## Kill Maps (Item 3)

### register-enforcement-wrl.json (scripts/walk_register_lint.py)

```
HEAD: 24056aa578c650b8af1ff93fb655ea767a74efaf
TARGET: scripts/walk_register_lint.py sha256=e50b63a1bd40
MUTANT M1-drop-legacy-schema-branch: KILLED — suite caught the defect
MUTANT M6-revert-to-pre-validation-short-circuit: KILLED — suite caught the defect
LIVE-TREE UNCHANGED: e50b63a1bd40
MUTATION: 2 killed, 0 survived, 0 error
```

### register-enforcement-cycle_check.json (scripts/cycle_check.py)

```
HEAD: 24056aa578c650b8af1ff93fb655ea767a74efaf
TARGET: scripts/cycle_check.py sha256=e04881ecae12
MUTANT M3-assign-fail-not-warn: KILLED — suite caught the defect
MUTANT M4-warn-printed-after-verdict: KILLED — suite caught the defect
MUTANT M5-run-check-returns-3-tuple: KILLED — suite caught the defect
LIVE-TREE UNCHANGED: e04881ecae12
MUTATION: 3 killed, 0 survived, 0 error
```

### register-enforcement-run_check.json (tools/run_check.py)

```
HEAD: 24056aa578c650b8af1ff93fb655ea767a74efaf
TARGET: tools/run_check.py sha256=31a01b4c6cd5
MUTANT M2-pre-schema-counted-bad: KILLED — suite caught the defect
LIVE-TREE UNCHANGED: 31a01b4c6cd5
MUTATION: 1 killed, 0 survived, 0 error
```

**Total: 6 killed, 0 survived, 0 ERROR.**

---

## Hygiene

**numstat (HEAD~2..HEAD, both DEV commits):**
```
119  0  knowledge/dev-logs/register-validate-first-dev-2026-09-03.md
  1 17  knowledge/mutants/{register-enforcement.json => register-enforcement-cycle_check.json}
 13  0  knowledge/mutants/register-enforcement-run_check.json
 20  0  knowledge/mutants/register-enforcement-wrl.json
 21  9  scripts/walk_register_lint.py
124  0  tests/test_walk_register_lint.py
6 files changed, 298 insertions(+), 26 deletions(-)
```

Files: 2 modified (walk_register_lint.py, test module), 1 deleted (register-enforcement.json via rename), 4 added (3 manifests + dev log). Total 7 file-level changes as specified.

**Reflog (-n 4):**
```
24056aa HEAD@{0}: reset: moving to HEAD
24056aa HEAD@{1}: [commit: Step 1 follow-up]
```
0 amends.

---

## Rule 20 — QA Self-Check

============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
Evidence folder: /Users/marklehn/Developer/bellows/.bellows-worktrees/100030/knowledge/qa/evidence/register-validate-first-2026-09-03/
Files verified: 3
