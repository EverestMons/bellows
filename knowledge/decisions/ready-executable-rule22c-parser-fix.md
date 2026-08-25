# bellows — executable: rule_22 (c) scoping fix — backtick-strip the ❌ scan, bounded N/A rows — the 531 build

**Date:** 2026-08-25 | **Project:** bellows | **Tier:** Small | **Dispatch Mode:** bellows | **cycle_tier:** T1 | **Test Scope:** bellows suite | **Execution:** Step 1 (DEV) → Step 2 (QA) | **Priority:** 2

**auto_close:** false
**pause_for_verdict:** always
**qa_steps:** 2

**Depends on:** `knowledge/research/rule22c-parser-fix-design-2026-08-25.md` (diagnostic-531 — BINDING: the R-5 gap table S1-S5, the R-4 test list A1-A5/B1-B5, and the settled shapes). **Options applied (the standing recommended-options directive):** shape A = backtick-stripping (strictly dominant per the census — 945 events, zero adversarial-❌ ever; the fail-safe rule: an UNPAIRED backtick leaves the row scanned unstripped); shape B = the bounded-cell `N/A` token via a new `_is_na_status_row` (an N/A row neither fires nor counts as the table's positive row); the (d) hedging check is deliberately UNCHANGED (zero (d)-class failures in history — prophylaxis refused, the census rules).

## Why this exists

The (c) check's two measured false-positive classes each cost a CEO override act (plans 523/524, the only two FPs in 945 events). The fix scopes the gate to what it means: a QA report QUOTING a failure marker inside backticks is evidence, not failure; a deliberate out-of-scope row marked `N/A` is disclosure, not omission. Genuine `❌` rows and genuinely missing statuses keep firing.

## What this plan does NOT do

- **Only gates.py + tests/test_gates.py change** (S5's fence). No bellows.py, runner.py, depositor.py, or any other module.
- **No (d) change** — census-refused.
- **No weakening of genuine arms:** the A/B test lists include the still-fires cases; the false-negative trade (❌ hidden in backticks) is accepted per 531's stated reasoning — the Planner's independent Rule 22(b) layer covers the adversarial class the mechanical gate does not.

## Numbers discipline

⚠️ **Measured by 531 and re-verified at authoring; line numbers are hints — re-locate by ANCHOR via `/usr/bin/grep`, assert count==1.**

| id | pin | value | anchor |
|---|---|---|---|
| X1 | the ❌ scan site | gates.py:689 | `if "❌" in stripped:` inside the (c) loop — the ONLY such line in the verification-section branch |
| X2 | the defer branch | gates.py:695-703 | the `elif _is_positive_status_row(line):` / else-defer pair — the N/A branch inserts BETWEEN them |
| X3 | the helper home | the `_is_positive_status_row` definition region | `_is_na_status_row` + its `NA_STATUS_TOKENS` constant live beside it, same bounded-cell-equality discipline |
| X4 | the existing fence | tests/test_gates.py (2323 lines) — 15 existing rule_22 tests incl. the (c)+(d) interaction pair | run them ALL in DEV |
| X5 | suite floor | **1435 collected** (post-530 era) | `python3 -m pytest tests/ --collect-only -q`; re-derive — yours supersedes |
| X6 | the reproduction rows | C4: a ✅ row quoting `` `❌ …` `` (523's row 89 text); C5: the status-less G8 row (524's row 75 text) | BOTH become passing under the new code — the A1/B-class tests reproduce them verbatim from the processed verdicts |

## MUST-PRESERVE

- ⚠️ **THE GREP SHIM IS BROKEN: `/usr/bin/grep` for all probes; zero-match exits 1, never &&-chain.**
- ⚠️ **The S5 fence:** `git diff HEAD~1 --stat` at QA shows EXACTLY gates.py + tests/test_gates.py.
- ⚠️ **Fail-safe stripping:** the backtick regex removes PAIRED spans only; a row with an unpaired backtick is scanned UNSTRIPPED (fail toward firing, never toward silence). Test A-class covers it.
- ⚠️ **N/A discipline mirrors `_is_positive_status_row`:** bounded CELL equality against `NA_STATUS_TOKENS` (`N/A`, `n/a` — keep the token set minimal; every added token widens the decoration surface), never substring; an N/A row must NOT set `current_table_has_positive_row`.
- ⚠️ **Anchor-based editing; NO daemon restart (the change is gate-time code, live for the NEXT plan's gates after the restart the CEO times).**
- ⚠️ **Worktree dispatch; deposit paths project-relative.**

## STEP 1 — DEV: the three hunks, the ten tests

**Role:** DEV.

**S1 (X1):** before the ❌ scan, strip paired inline-code spans and scan the stripped copy. The regex, described fence-free because its literal contains backticks (531's S1 row carries the exact form): a raw-string pattern of BACKTICK, one-or-more non-backtick chars, BACKTICK, substituted with the empty string via re.sub over `stripped` into a `scan_target`; then the ❌ membership test runs on `scan_target`. The unpaired-backtick fail-safe holds by construction (an unpaired backtick never completes the pattern, so its text stays in the scanned copy) — state that in a comment, don't re-implement it.
**S2 (X2):** insert the N/A branch between the positive-status branch and the defer: `elif _is_na_status_row(line): pass` — the row neither fires, nor counts positive, nor defers.
**S3 (X3):** `NA_STATUS_TOKENS` + `_is_na_status_row` beside `_is_positive_status_row`, same bounded-cell mechanics (split on `|`, strip, compare case-insensitively against the token set).
**S4 (X4):** the ten tests from 531's R-4 list, named as specified (A1-A5: the C4 reproduction verbatim; genuine ❌ outside backticks still fires; ❌ in an unpaired-backtick row still fires; backtick-stripped row with non-positive status still defers; multiple code spans. B1-B5: the C5 reproduction verbatim; N/A-only table discards defers; N/A does not count positive; genuine missing-status still fires in a mixed table; N/A is cell-bounded — `N/A-ish prose` does not match). Run the FULL rule_22 test set (the 15 existing + 10 new) targeted; zero regressions.

**Deposits:**
- `/Users/marklehn/Developer/GitHub/bellows/gates.py`
- `/Users/marklehn/Developer/GitHub/bellows/tests/test_gates.py`

**Scope:**
- `/Users/marklehn/Developer/GitHub/bellows/gates.py`
- `/Users/marklehn/Developer/GitHub/bellows/tests/test_gates.py`

**Commit:** `git add gates.py tests/test_gates.py && git commit -m "[<id>] gates: rule_22(c) scoping — backtick-strip the failure-marker scan, bounded N/A rows (531 shapes A+B)"` in YOUR worktree cwd.

## STEP 2 — QA: full suite + the reproduction proof

**Role:** QA.

**Q1 — full suite.** `python3 -m pytest tests/ -q` from the repo root; RAW output to `knowledge/qa/evidence/rule22c-parser-fix/pytest_full.txt`; self-contained accounting vs X5; zero failures.
**Q2 — the reproduction proof.** Feed the C4 and C5 rows (X6, verbatim from the processed verdicts) through `_gate_rule_22_verification` in a scratch harness: both now produce ZERO failures; then the inverted controls — a genuine `| test | ❌ |` row and a genuinely status-less check row in a mixed table BOTH still fire. Raw transcript in the report.
**Q3 — the fence.** `git diff HEAD~1 --stat` == exactly the two files; the three gates.py hunks named.
**Q4 — QA report.** `knowledge/qa/evidence/rule22c-parser-fix/qa-report.md` with Q1-Q3 and the S1-S5 coverage row.

> **QA SELF-CHECK — Rule 20.** Post the block from `/Users/marklehn/Developer/GitHub/RULE_20_SELF_CHECK_BLOCK.md` verbatim, under the banner **`Rule 20 — QA Self-Check Results`**, and close with **`PASSED — SELF-CHECK PASSED`** only if every check genuinely passed. ⚠️ Both literals are matched by `plan_lint` check (c) and neither may be paraphrased. Rule 20 block + Q results in the `.md`; raw suite output in `pytest_full.txt` — the two QA gates scan DIFFERENT extensions.

**Deposits:**
- `/Users/marklehn/Developer/GitHub/bellows/knowledge/qa/evidence/rule22c-parser-fix/pytest_full.txt`
- `/Users/marklehn/Developer/GitHub/bellows/knowledge/qa/evidence/rule22c-parser-fix/qa-report.md`

**Scope:**
- `/Users/marklehn/Developer/GitHub/bellows/knowledge/qa/evidence/rule22c-parser-fix/`

**Commit:** `git add knowledge/qa/evidence/rule22c-parser-fix/ && git commit -m "[<id>] qa: rule_22(c) scoping fix — full suite + reproduction proof"` in YOUR worktree cwd.

## Drafting Cycle
**Tier:** T1 computed — a three-hunk scoping fix in one gate function, census-justified, with the reproduction rows as ground truth; panel not convened with reasoning (the change is small, the 531 census + the A/B test lists bound it tighter than a panel's yield at this size; the QA's inverted controls guard the false-negative edge).
**Walk register:** `governance/knowledge/research/walk-register-executable-rule22c-fix.md`
**Walks:** walk 0 pinned; **walks 1–2 complete** — five lenses each; walk 1 folded 1 (S1's self-demonstrating nested-backtick corruption), walk 2 dry across all five lenses.
**Direction verdict (after walk 1): PROCEED.** Tested, not judged.
- Weak spots:          w1 1 folded — instruction 1 / record 0; w2 dry
- Destruction:         w1 dry; w2 dry
- Vulnerabilities:     w1 dry; w2 dry
- Integration-record:  w1 dry; w2 dry — close obligations discharged at this freeze
- ACID:                w1 dry; w2 dry
**Conformance (§5):** recorded at the freeze from actual runs: walk_register_lint CONFORMANT (verdict channel, branched-on); cycle_check BAR_MET post-finalization (verdict channel, branched-on); plan_lint 0 FAIL at the scratch-mirror path.
**Closing:** **walk 2 met the bar — all five lenses dry.** Instruction series **1 → 0**. Receipt BEFORE staging (structural) → shop-infra hold → release under the CEO's directive → claim.

## Cycle Manifest
tier: T1
target: gates.py
class: shop-infra
reads: /Users/marklehn/Developer/GitHub/bellows/gates.py, /Users/marklehn/Developer/GitHub/bellows/tests/test_gates.py, /Users/marklehn/Developer/GitHub/bellows/knowledge/research/rule22c-parser-fix-design-2026-08-25.md, /Users/marklehn/Developer/GitHub/bellows/verdicts/resolved/processed-verdict-523-step-2.md, /Users/marklehn/Developer/GitHub/bellows/verdicts/resolved/processed-verdict-524-step-2.md
writes: gates.py, tests/test_gates.py, knowledge/qa/evidence/rule22c-parser-fix/pytest_full.txt, knowledge/qa/evidence/rule22c-parser-fix/qa-report.md
open_forks: none — 531's R-6 soft fork resolved by the standing recommended-options directive (N/A token)
walks: 2
yields: 1, 0
validation: cycle_check=BAR_MET, plan_lint=0_FAIL, fold_check=N/A
coherence: N/A

## Rule 20 — QA Self-Check Block

Step 2 is the QA step; the block is posted there per its mandate. Step 1 is DEV-only.
