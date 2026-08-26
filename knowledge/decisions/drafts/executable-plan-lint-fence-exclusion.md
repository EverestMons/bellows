# bellows — executable: the (r) check learns fences — its first measured false-positive class excluded (v2)

**Date:** 2026-08-26 | **Project:** bellows | **Tier:** Small | **Dispatch Mode:** bellows | **cycle_tier:** T1 | **Test Scope:** targeted (the lint tests) + full suite at QA | **Execution:** Step 1 (DEV) → Step 2 (QA) | **qa_steps:** 2 | **pause_for_verdict:** always

**auto_close:** false

**Depends on:** the CEO's "Proceed with batch 3"; the 563 measurement (the (r) check's first live warn was `if code == 0:` inside a fenced block — structural, not a probe; judged via the WARN's own escape clause and recorded as the v2 candidate).

## Why this exists

The funnel refines by measurement: one live false-positive class, one exclusion. Probe expectations live in prose; code lives in fences — the check should read only the former.

## Numbers discipline

⚠️ **Measured 2026-08-26; re-measure pre-flight; mismatch → HALT; counts carry measure-record-supersede.**

| id | pin | value | anchor |
|---|---|---|---|
| F1 | the check | `def _check_bare_constants` count-1; its loop's `in_step` toggle present | `scripts/plan_lint.py` (repo-relative — worktree law) |
| F2 | the fixture | the 563 draft's fired line (`if code == 0:` in a fenced block) — reproduce from `git show` of the 563 draft commit; record the blob ref | the committed 563 draft |

## STEP 1 — DEV (the toggle + tests)

> **Task A — worktree discipline.** `cd "$(git rev-parse --show-toplevel)" && test -f scripts/plan_lint.py && echo TREE_OK` — HALT unless TREE_OK. Probes: (i) `/usr/bin/grep -cF -- "in_fence" scripts/plan_lint.py; true`, (ii) `/usr/bin/grep -cF -- "def test_fence" tests/test_plan_lint_bare_constants.py; true`. (0,0) → full run; (1,0) → resume at Task C; (1,1) → Task D commit-check; (0,1) → HALT.
>
> **Task B — the toggle.** In `_check_bare_constants`'s loop, add a fence state symmetric with `in_step` (anchor the loop's opening `    for i, line in enumerate(lines):` within the function, count-1 in its span): initialize `in_fence = False` beside `in_step`; at the TOP of the loop body, before any other test: a line whose lstrip() starts with three backticks TOGGLES `in_fence` and `continue`s; and the existing skip condition gains `or in_fence`. Update the docstring's final sentence to name the exclusion: fenced code is never scanned — the 563-measured false-positive class (structural constants in code blocks). Post-probes: `"in_fence"` count >= 4; the docstring mentions `563` == 1.
>
> **Task C — tests appended to `tests/test_plan_lint_bare_constants.py`** (two new): (1) `test_fence_excludes_structural_constants` — a STEP block whose fenced python contains `if code == 0:` and `x == 3` fires ZERO warns (the 563 fixture, provenance-commented with the blob ref); (2) `test_fence_toggle_reopens` — the same constants AFTER the closing fence in prose fire normally (the toggle closes correctly — the symmetric trap). Targeted run: the lint test files — 0 failed (record counts; supersede with derivation).
>
> **Task D — dev log + commit.** `knowledge/dev-logs/plan-lint-fence-exclusion-dev-2026-08-26.md` (F2's blob ref, probe raws, targeted raw). Commit (WORKTREE toplevel): `cd "$(git rev-parse --show-toplevel)" && git add scripts/plan_lint.py tests/test_plan_lint_bare_constants.py knowledge/dev-logs/plan-lint-fence-exclusion-dev-2026-08-26.md && git commit -m "[<id from your plan filename>] plan-lint-fence-exclusion(plan-lint-fence-exclusion-2026-08-26): (r) v2 — fenced code excluded, the 563-measured FP class" -- scripts/plan_lint.py tests/test_plan_lint_bare_constants.py knowledge/dev-logs/plan-lint-fence-exclusion-dev-2026-08-26.md && git rev-parse HEAD` — **CAPTURE_COMMIT**.
>
> **Deposits:**
> - `scripts/plan_lint.py`
> - `tests/test_plan_lint_bare_constants.py`
> - `knowledge/dev-logs/plan-lint-fence-exclusion-dev-2026-08-26.md`
>
> **Scope:**
> - `scripts/plan_lint.py`
> - `tests/test_plan_lint_bare_constants.py`
> - `knowledge/dev-logs/plan-lint-fence-exclusion-dev-2026-08-26.md`

## STEP 2 — QA (FULL suite + the 563 replay)

> **Item 1 — full suite.** `cd "$(git rev-parse --show-toplevel)"`; `python3 -m pytest tests/ --tb=short -q 2>&1 | cat | tee knowledge/qa/evidence/plan-lint-fence-exclusion-2026-08-26/pytest_full.txt` — 0 failed (record the count; derivation vs 1509 + 2).
> **Item 2 — the 563 replay.** Run the committed plan_lint against the 563 draft blob (extract via `git show` to scratch): the (r) warn that fired at its deposit now does NOT fire (paste both the old evidence citation and the new clean output); AND run it against a scratch plan with a bare prose constant → still fires (the check's teeth intact, proven side-by-side). `cmp` extractions vs live → 0.
> **Item 3 — hygiene + receipt** `knowledge/qa/evidence/plan-lint-fence-exclusion-2026-08-26/qa-receipt.md`: numstat 3 files; toplevel; reflog `-n 4` → 0 amends; per-item table, then the Rule 20 block INSIDE a "Verification"-headed section.
>
> ⚠️ **Gate note:** pytest summary named above — the gate parses; no benign override pre-declared.
>
> **Deposits:**
> - `knowledge/qa/evidence/plan-lint-fence-exclusion-2026-08-26/pytest_full.txt`
> - `knowledge/qa/evidence/plan-lint-fence-exclusion-2026-08-26/probes-raw.txt`
> - `knowledge/qa/evidence/plan-lint-fence-exclusion-2026-08-26/qa-receipt.md`
>
> **Scope:**
> - `knowledge/qa/evidence/plan-lint-fence-exclusion-2026-08-26/pytest_full.txt`
> - `knowledge/qa/evidence/plan-lint-fence-exclusion-2026-08-26/probes-raw.txt`
> - `knowledge/qa/evidence/plan-lint-fence-exclusion-2026-08-26/qa-receipt.md`

Rule 20 banner (byte-exact, inside the QA receipt's VERIFICATION section):

```
============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
```

## Drafting Cycle

**Tier:** T1 — one toggle + two tests; the measured-FP-to-exclusion loop is the funnel operating on its own product.

**Walk register:** `bellows/knowledge/research/walk-register-plan-lint-fence-exclusion-2026-08-26.md`

**Walk 0 (context pin, measured):** the 563 FP line as the fixture (blob-ref'd); the in_step toggle as the symmetry model; the teeth-intact side-by-side in QA.

**Walks:**
- Weak spots:          w1 dry — the toggle-then-continue ordering means fence DELIMITER lines are never scanned either (correct — a delimiter carries no probe); test 2 guards the symmetric reopen trap; the teeth-intact side-by-side keeps the v2 honest.
- Destruction:         w1 dry — three-arm resume; one commit.
- Vulnerabilities:     w1 dry — the exclusion narrows fire surface only (a WARN-only check cannot fail-open anything by warning less; the funnel's measured-class rule governs the narrowing).
- Integration-record:  w1 dry — the FP's provenance blob-ref'd into the test file; the 563 replay is the QA spine.
- ACID:                w1 dry — counts clause-clothed.
- **Walk 1 total: 0 findings — all five lenses dry.**
- Weak spots:          w2 dry.
- Destruction:         w2 dry.
- Vulnerabilities:     w2 dry.
- Integration-record:  w2 dry.
- ACID:                w2 dry.
- **Walk 2 total: 0 findings — all five lenses dry.**

**Closing:** ✅ **BAR MET at walk 2 — dry confirming pass, all five lenses.** T1 two-walk form; no direction-class finding; close is MANUAL (CEO-lane verdicts).

**Fold-and-deposit exactly once.**

## Cycle Manifest
tier: T1
target: bellows/scripts/plan_lint.py
class: shop-infra
reads: /Users/marklehn/Developer/GitHub/bellows/scripts/plan_lint.py, /Users/marklehn/Developer/GitHub/bellows/tests/test_plan_lint_bare_constants.py
writes: scripts/plan_lint.py, tests/test_plan_lint_bare_constants.py, knowledge/dev-logs/plan-lint-fence-exclusion-dev-2026-08-26.md, knowledge/qa/evidence/plan-lint-fence-exclusion-2026-08-26/pytest_full.txt, knowledge/qa/evidence/plan-lint-fence-exclusion-2026-08-26/probes-raw.txt, knowledge/qa/evidence/plan-lint-fence-exclusion-2026-08-26/qa-receipt.md
open_forks: batch-3 items 2-3 (reconcile_plan.py; the rename fix in _parse_diff_stat) — SERIAL; the 23-row re-queue triage at batch close
walks: 2
yields: 0, 0
validation: cycle_check=BAR_MET, plan_lint=0_FAIL, fold_check=N/A
coherence: N/A
