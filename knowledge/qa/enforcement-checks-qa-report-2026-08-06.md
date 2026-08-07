# QA Report — Plan 306: Three warn-first enforcement checks (j), (k), (l)

**Plan:** executable-306
**Step:** 2 (QA)
**Date:** 2026-08-07

---

## Task Q0 — State Re-pin

### Q0.1 — Most recent commit touching plan_lint / tests / gates

```
$ git -C /Users/marklehn/Developer/GitHub/bellows log -1 --oneline -- scripts/plan_lint.py tests/test_plan_lint.py gates.py
d845483 [306] feat: add warn-first checks (j) inherited-premise, (k) clone-claim, (l) clone-mutation down-tier
```

This is Step 1's commit. No foreign commit detected. **PASS.**

### Q0.2 — Corpus pins

| Root | HEAD at pin |
|---|---|
| anvil | `da17272ee00c82f987052953660940d18b59c1e0` |
| bellows | `3aad1c92bcda092bc4f55c4f04dbad86015aea6e` |
| governance | `3f624499ae7c6734bde8b7bac8448b5585e3e800` |
| invoice-pulse | `f83c244d914cccbac1d14447054fa7a456a77236` |
| lessons-forge | `b9fd5f152b35e13bae941cb9198924b7de154535` |

### Q0.3 — Post-sweep pin verification

All five HEADs re-verified after the final sweep. All match their pins. No re-pin required.

| Root | HEAD after sweep | Match |
|---|---|---|
| anvil | `da17272ee00c82f987052953660940d18b59c1e0` | ✅ |
| bellows | `3aad1c92bcda092bc4f55c4f04dbad86015aea6e` | ✅ |
| governance | `3f624499ae7c6734bde8b7bac8448b5585e3e800` | ✅ |
| invoice-pulse | `f83c244d914cccbac1d14447054fa7a456a77236` | ✅ |
| lessons-forge | `b9fd5f152b35e13bae941cb9198924b7de154535` | ✅ |

---

## Item 1 — Test Suites

### Full test suite

```
868 passed, 1 warning in 21.52s
```

Raw output in `full-suite.txt`.

### Targeted plan_lint tests

```
71 passed, 797 deselected, 1 warning in 2.80s
```

Raw output in `targeted-tests.txt`.

---

## Item 2 — Corpus Sweep

Sweep glob: `Done/*.md` across all five roots. 1,366 total files. All exit statuses captured; zero crashers. Per-file exits identical between pre-edit and current sweeps (all EXIT=1 files are pre-existing failures from checks (a)–(d), not from new checks).

### (j) Inherited-premise marker — 10 WARN lines across 3 files

All in `lessons-forge`:

| File | WARN lines | Details |
|---|---|---|
| `executable-289.md` | 3 | line 134 (plan 284), line 169 (plan 284), line 169 (plan 284) |
| `executable-297.md` | 2 | line 252 (plan 289/284), line 263 (plan 289) |
| `executable-298.md` | 5 | line 11 (plan 291), line 12 (plan 297), line 13 (plan 297), line 14 (plan 297), line 15 (plan 246) |

**Context from 305:** 3 files at 305's pin, all true positives. **Fresh measurement: 3 files, 10 WARN lines.** The file count matches; the WARN-line count is higher because each file contains multiple markers (305 counted files, not lines).

Other roots: anvil 0, bellows 0, governance 0, invoice-pulse 0.

### (k) Clone-claim — 8 fires across 8 files

| Root | File | Fire count |
|---|---|---|
| bellows | `executable-277.md` | 1 |
| bellows | `executable-286.md` | 1 |
| governance | `diagnostic-285.md` | 1 |
| governance | `diagnostic-301.md` | 1 |
| lessons-forge | `executable-274.md` | 1 |
| lessons-forge | `executable-275.md` | 1 |
| lessons-forge | `executable-287.md` | 1 |
| lessons-forge | `executable-291.md` | 1 |

Other roots: anvil 0, invoice-pulse 0.

**Context from 305:** 19 at 305's pin (whole-body prototype key). **Fresh measurement: 8** (the key changed at each revision: 19 → 10 → 8; tier-line-only scope + case-insensitive suppressor + full literal set produce this count).

### (l) Clone-mutation down-tier — 0 fires

Zero fires across all 1,366 files. **Expected and correct:** no down-tiered T-2 population exists until the §1 executable moves T-2 into T1. The check is shipped inert; its mechanical soundness is proven by the fixture tests (7 tests, including the mandatory plural+hyphenated control).

---

## Item 3 — All counts are measured

Every count above was produced by the corpus sweep command:

```
for root in anvil bellows governance invoice-pulse lessons-forge; do
  dir="/Users/marklehn/Developer/GitHub/${root}/knowledge/decisions/Done"
  for f in "$dir"/*.md; do
    python3 scripts/plan_lint.py "$f"
  done
done
```

Per-check attribution was extracted by a Python script scanning the sweep output for `(j) WARN:`, `(k) WARN:`, `(l) WARN:` lines, tracked by the preceding `=== root: file ===` header.

---

## Item 4 — (k) fire annotation against instruction date

The newest-same-class discipline entered doctrine at **v1.2, 2026-07-30**, commit `3c327e3`:

```
$ git -C /Users/marklehn/Developer/GitHub/governance log --oneline --format="%H %ai %s" 3c327e3 -1
3c327e3513712783ab4525b6e2942daa9895eb4e 2026-07-30 18:46:27 -0500 [287] Step 2: codify proposals 191–200 into three doctrine files
```

### Three bands

| Band | IDs | First-commit dates |
|---|---|---|
| **Clearly predate** (before 2026-07-30) | 274, 275, 277, 285 | 2026-07-24, 2026-07-25, 2026-07-25, 2026-07-29 |
| **Same-day boundary** (2026-07-30) | 286, 287 | 2026-07-30 13:55 (before commit 18:46), 2026-07-30 19:30 (287 IS the codification plan) |
| **Postdate** (after 2026-07-30) | 291, diagnostic-301 | 2026-08-03, 2026-08-06 |

**4 clearly predate** the instruction (baseline). **2 same-day boundary** — 286 was committed 5 hours before the codification, 287 is the codification plan itself. **2 postdate** — 291 and diagnostic-301 are post-instruction fires. Weighing the postdating fires is the CEO's.

---

## Item 5 — Sweep-diff proof

Pre-edit script materialized from PRE_EDIT_HASH `8e085fa`:

```
$ git -C /Users/marklehn/Developer/GitHub/bellows show 8e085fa:scripts/plan_lint.py > /tmp/plan_lint_pre.py
```

Invoked via `PYTHONPATH=/Users/marklehn/Developer/GitHub/bellows python3 /tmp/plan_lint_pre.py <plan>` (to resolve `import gates`). Confirmed working on one plan before sweeping.

### Diff result (29 lines, NON-EMPTY)

The diff shows ONLY added `(j)` and `(k)` WARN lines:
- 8 added `(k) WARN:` lines (one per firing file)
- 10 added `(j) WARN:` lines (across 3 files)
- 0 `(l)` lines (expected — check is inert)
- **Zero `(a)`–`(h)` lines changed or lost**

Full diff in `sweep-diff.txt`. Reconciliation: 8 `(k)` + 10 `(j)` = 18 added lines, matching the line-count difference (10,059 − 10,041 = 18). The diff is non-empty and consistent with item 2's counts.

---

## Item 6 — WARN-only confirmation

### By mechanism

```
$ grep -n "results\|all_passed" scripts/plan_lint.py | grep -E "^(2[5-9][0-9]|3[01][0-9]):"
(no output, exit 1)
```

Lines 250–318 (the (j)/(k)/(l) blocks) contain **zero** references to `results` or `all_passed`.

Positive control: `results` and `all_passed` appear in earlier lines (41, 42, 47, 48, 50, etc.).

### By symptom

```
$ python3 scripts/plan_lint.py /tmp/trip_all_three.md
(j) WARN: line 9 carries an inherited-premise marker from plan 291
(k) WARN: clone-framed plan does not name its newest same-class comparison (§2.6 :75)
(l) WARN: clone-framed plan firing T-2 declares tier < T2 — §2.6: clone framing is not licence to down-tier; consider self-escalation to the cold panel
PASS: (a) header — parsed
PASS: (a) dispatch_mode — bellows
PASS: (a) pause_for_verdict — always
PASS: (b) step 1 deposits — 1 path(s)
$ echo $?
0
```

All three fire, exit 0. **Both mechanism and symptom confirm WARN-only.**

---

## Item 7 — QA Verification Receipt

### Verification table

| # | Item | Status | Evidence |
|---|---|---|---|
| Q0 | State re-pin | ✅ | Most recent commit is Step 1's `d845483`; all 5 HEADs match pre/post sweep |
| 1 | Full test suite | ✅ | 868 passed, 1 warning (`full-suite.txt`) |
| 1 | Targeted tests | ✅ | 71 passed, 797 deselected, 1 warning (`targeted-tests.txt`) |
| 2 | Corpus sweep (j) | ✅ | 10 WARN lines / 3 files, all lessons-forge (`corpus-sweep.txt`) |
| 2 | Corpus sweep (k) | ✅ | 8 fires / 8 files across bellows/governance/lessons-forge (`corpus-sweep.txt`) |
| 2 | Corpus sweep (l) | ✅ | 0 fires — expected, no down-tiered T-2 population (`corpus-sweep.txt`) |
| 3 | Measured counts | ✅ | All counts from sweep command, context figures cited beside fresh measurements |
| 4 | (k) date annotation | ✅ | 4 predate / 2 same-day / 2 postdate against 2026-07-30 (commit `3c327e3` verified) |
| 5 | Sweep-diff proof | ✅ | Only (j)/(k) lines added, zero (a)–(h) changed, non-empty (`sweep-diff.txt`) |
| 6 | WARN-only (mechanism) | ✅ | Zero `results`/`all_passed` in lines 250–318 |
| 6 | WARN-only (symptom) | ✅ | EXIT=0 on fixture tripping all three |

### Rule 20 Self-Check

```
============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
Evidence folder: /Users/marklehn/Developer/GitHub/bellows/.bellows-worktrees/306/knowledge/qa/
Files verified: 4
```

---

## Evidence Files

- `targeted-tests.txt` — 71 passed, 797 deselected, 1 warning
- `full-suite.txt` — 868 passed, 1 warning
- `corpus-sweep.txt` — 10,059 lines, all 1,366 files across 5 roots
- `sweep-diff.txt` — 29-line diff, only (j)/(k) lines added
