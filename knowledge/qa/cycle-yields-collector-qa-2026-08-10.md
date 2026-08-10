# QA Report — cycle-yields-collector-2026-08-10

**Plan slug:** `cycle-yields-collector-2026-08-10`
**Date:** 2026-08-10
**Step:** 2 (QA)

---

## Deliverable Verification

| # | Item | Result | Evidence |
|---|------|--------|----------|
| 1 | Corpus run complete — tool discovery equals independent `find` | OK | Tool: 1694 files, 61 with block. `find`: 1694. Re-run output identical to Step 1 deposit (0 differing rows). |
| 2 | UNPARSEABLE rows honest | OK | 194 UNPARSEABLE rows. Spot-checked: `diagnostic-310.md` uses arrow format (`w1 → v1: 4 folded`) and a bare status-word line — both genuinely unparseable by the v2.0 parser. Count is non-zero; each carries the first 120 chars of the offending line in the note column. |
| 3 | ABSENT is never 0 | OK | Extracted all 342 rows with `origin=ABSENT`. All have `pre_existing=-` and `fold_introduced=-`. Zero violations. |
| 4 | Tool wrote nothing, anywhere | OK | Git status captures (bellows and governance root) before and after re-run are identical. Bellows: only `?? knowledge/decisions/in-progress-executable-335.md` and `?? verdicts/resolved/processed-verdict-335-step-1.md` (plan lifecycle, not tool). Governance root: `M bellows` and `?? scratchpad/` (submodule pointer and scratch, not tool). No delta on any path under `scripts/`, `knowledge/`, or root. Positive control: stdout produced 2170 lines (1 header + 2169 data rows). |
| 5 | Full suite | OK | `960 passed, 1 warning in 24.09s`. Baseline: `lint-s4-hardening-qa-2026-08-09.md` reported 928 passed. Delta: +32 (the 32 new tests in `test_cycle_yields.py`). No drop. |
| 6 | Raw output | OK | See tallies below. |

### Item 1 — re-run detail

```
# Discovery: 1694 files, 61 with Drafting Cycle block
```

Re-run diff against Step 1 `corpus-run.txt`: **empty** (sorted diff, 0 differing rows). Corpus did not change between steps.

Independent count:
```
$ find /Users/marklehn/Developer/GitHub -path '*/knowledge/decisions/Done/*.md' -not -path '*/.*' | wc -l
    1694
```

### Item 2 — UNPARSEABLE sample

```
diagnostic-272.md  - Weak spots: w1 → v1: 3 folded (W1 Q1 enumerate-not-grep; ...
diagnostic-310.md  - Weak spots: w1 → v1: 4 folded (W1 1.3 zero-diff provenance ...
diagnostic-310.md  - Destruction: [bare status word].
```

Verified `diagnostic-310.md` at `/Users/marklehn/Developer/GitHub/invoice-pulse/knowledge/decisions/Done/diagnostic-310.md`: the file uses arrow format (`w1 → v1:`) and carries a bare status-word line (`- Destruction: [word].`). Both are genuinely outside the parser's v2.0 grammar.

### Item 3 — ABSENT origin rows

Extracted all 342 `origin=ABSENT` rows. Assertion: `$7 == "-" && $8 == "-"` for every row. Result: **0 violations**. No ABSENT row carries `0` in `pre_existing` or `fold_introduced`.

### Item 4 — git status captures

**Bellows — before re-run:**
```
?? knowledge/decisions/in-progress-executable-335.md
?? verdicts/resolved/processed-verdict-335-step-1.md
```

**Bellows — after re-run:**
```
?? knowledge/decisions/in-progress-executable-335.md
?? verdicts/resolved/processed-verdict-335-step-1.md
```

**Governance root — before re-run:**
```
 M bellows
?? scratchpad/
```

**Governance root — after re-run:**
```
 M bellows
?? scratchpad/
```

Diff: **empty**. No paths under `scripts/`, `knowledge/`, or root changed. The two untracked files and submodule pointer are plan lifecycle artifacts, not tool output.

### Item 5 — full suite

```
======================= 960 passed, 1 warning in 24.09s ========================
```

Baseline source: `bellows/knowledge/qa/lint-s4-hardening-qa-2026-08-09.md` — 928 passed.
Delta: **+32** (exactly the 32 new tests in `test_cycle_yields.py`). No drop.

### Item 6 — tallies from re-run

**Status tally (enumerated from script):**

| Status | Count |
|---|---|
| OK | 342 |
| NO_BLOCK | 1633 |
| UNPARSEABLE | 194 |
| MULTIPLE_BLOCKS | 0 |

**Origin tally (enumerated from script):**

| Origin | Count |
|---|---|
| ABSENT | 342 |
| N/A | 1827 |
| PRESENT | 0 |
| PARTIAL | 0 |

All values match Step 1's deposit exactly.

---

## Rule 20 — QA Self-Check Results

```
============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
Evidence folder: /Users/marklehn/Developer/GitHub/bellows/.bellows-worktrees/335/knowledge/qa/evidence/cycle-yields-collector-2026-08-10/
Files verified: 1
```
