# bellows — executable: plan_lint gains the `(r)` bare-constant WARN — a probe constant without a supersede clause is flagged, warn-first (Rule 73's measured signal, ~10 instances)

**Date:** 2026-08-26 | **Project:** bellows | **Tier:** Small | **Dispatch Mode:** bellows | **cycle_tier:** T1 | **Test Scope:** targeted (plan_lint tests) + full suite at QA | **Execution:** Step 1 (DEV) → Step 2 (QA) | **qa_steps:** 2 | **pause_for_verdict:** always

**auto_close:** false

**Depends on:** the CEO's "proceed as suggested" on the mechanization ledger (batch item 1); the funnel-mechanization contract (prototype against real states, ship warn-first, never mechanize the verdict); the measured tally (~10 instances, the 554 ad-hoc-probe case as the design case).

## Why this exists

Ten measured mispredictions were absorbed only where a supersede clause happened to sit nearby; the one ad-hoc probe line without one (554) hard-failed a correct state. The lint makes the clause's ABSENCE visible at authoring time — advisory only, the verdict stays human.

## What this plan does NOT do

- NEVER a FAIL: `(r)` is a WARN — warn-first is the funnel's law and plan_lint's exit code is unchanged by it.
- No doctrine edits; no gate wiring beyond plan_lint's own output.

## Numbers discipline

⚠️ **Measured 2026-08-26; the agent re-measures pre-flight; mismatch → HALT. Every count below carries the supersede clause this very plan mechanizes: measure, RECORD, supersede with the derivation.**

| id | pin | value | anchor |
|---|---|---|---|
| N1 | plan_lint.py | 782 lines; `def lint(plan_path):` count-1; the `(q)` letter is the last taken (grep `"(r)"` count 0 pre-edit) | `scripts/plan_lint.py` (repo-relative — worktree law) |
| N2 | Done corpus | 694 plans across governance/lessons-forge/bellows Done dirs (re-count; supersede with derivation) | the three `knowledge/decisions/Done` dirs, ABSOLUTE root-anchored reads |
| N3 | prototype sample | the newest **60** by mtime across the three dirs (declared cap — stated, not silent) | ibid. |

## STEP 1 — DEV (the check + tests + the corpus prototype)

> **Task A — worktree discipline.** `cd "$(git rev-parse --show-toplevel)" && test -f scripts/plan_lint.py && echo TREE_OK` — HALT unless TREE_OK. Probes: (i) `/usr/bin/grep -cF -- "(r) WARN" scripts/plan_lint.py; true`, (ii) `test -f tests/test_plan_lint_bare_constants.py && echo 1 || echo 0`. (0,0) → full run; (1,0) → resume at Task C; (1,1) → Task D commit-check; (0,1) → HALT.
>
> **Task B — the check.** Insert into `scripts/plan_lint.py` (before `def lint(` — anchor `def lint(plan_path):` count-1) the function EXACTLY:
>
> ```python
> _BARE_CONSTANT_RE = re.compile(r"(==|>=|<=)\s*\*{0,2}\d+\*{0,2}")
> _CLAUSE_MARKERS = ("supersede", "re-derive", "rederive", "yours ", "recorded",
>                    "record", "measured", "measure and")
>
>
> def _check_bare_constants(plan_text):
>     """(r) WARN-FIRST: a probe constant (== / >= / <= N) inside a STEP block
>     with no supersede-class clause on the line or within 2 lines either side.
>     The global Numbers-discipline banner deliberately does NOT satisfy this
>     check: the gap being closed is the ad-hoc probe line outside the banner's
>     reach (the 554 case). Advisory only — never a FAIL; the verdict on
>     whether a constant is genuinely load-bearing stays with the reader."""
>     lines = plan_text.splitlines()
>     in_step = False
>     warns = []
>     for i, line in enumerate(lines):
>         if line.startswith("## STEP "):
>             in_step = True
>         elif line.startswith("## ") and not line.startswith("## STEP "):
>             in_step = False
>         if not in_step or not _BARE_CONSTANT_RE.search(line):
>             continue
>         window = " ".join(lines[max(0, i - 2):i + 3]).lower()
>         if not any(m in window for m in _CLAUSE_MARKERS):
>             warns.append(i + 1)
>     for n in warns:
>         print(f"(r) WARN: line {n} probe constant without a supersede-class "
>               f"clause within 2 lines — a wrong authored number here HARD-FAILS "
>               f"a correct state (the 554 class); add measure-record-supersede "
>               f"language or verify the constant is structural")
>     return len(warns)
> ```
>
> Wire the call inside `lint()` after the existing checks (anchor a stable late line in `lint()` — locate with `grep -nF`, count-1, quote it in the dev log): `_check_bare_constants(plan_text)` using the same plan-text variable the neighboring checks read (READ the function to bind the real variable name — never assume it).
>
> **Task C — tests `tests/test_plan_lint_bare_constants.py`** (new): five tests over `_check_bare_constants` directly: (1) a bare `== 3` probe line inside a STEP block fires (returns 1); (2) the same line with "measured supersedes" within 2 lines → 0; (3) the same constant OUTSIDE any STEP block → 0; (4) `>= 2` with "RECORDED" nearby → 0 (case-insensitive); (5) three bare lines → 3. Targeted run: `python3 -m pytest tests/test_plan_lint_bare_constants.py tests/test_plan_lint.py --tb=short -q 2>&1 | cat` → all pass, 0 failed (record the count; supersede with derivation).
>
> **Task C2 — THE PROTOTYPE (the funnel's measurement stage).** Run the NEW check over the newest 60 Done plans by mtime across `/Users/marklehn/Developer/GitHub/{governance,lessons-forge,bellows}/knowledge/decisions/Done/*.md` (absolute reads — these lanes are outside the worktree): a python loop importing `_check_bare_constants`, printing per-plan `<fires> <path>` plus the TOTAL. RECORD the raw table in the dev log. ⚠️ Tuning law: if the total exceeds **600** across the sample (an average >10 warns/plan — noise territory), STOP and report the distribution with the top-firing lines quoted — the CEO prices the marker set; NEVER silently widen `_CLAUSE_MARKERS` beyond the declared set to make the number small.
>
> **Task D — dev log + commit.** `knowledge/dev-logs/plan-lint-bare-constants-dev-2026-08-26.md` (the wiring anchor quoted, targeted-test raw, THE PROTOTYPE TABLE + total). Commit (WORKTREE toplevel): `cd "$(git rev-parse --show-toplevel)" && git add scripts/plan_lint.py tests/test_plan_lint_bare_constants.py knowledge/dev-logs/plan-lint-bare-constants-dev-2026-08-26.md && git commit -m "[<id from your plan filename>] plan-lint-bare-constants(plan-lint-bare-constants-2026-08-26): (r) WARN, warn-first, prototype-measured over 60 Done plans" -- scripts/plan_lint.py tests/test_plan_lint_bare_constants.py knowledge/dev-logs/plan-lint-bare-constants-dev-2026-08-26.md && git rev-parse HEAD` — **CAPTURE_COMMIT**.
>
> **Deposits:**
> - `scripts/plan_lint.py`
> - `tests/test_plan_lint_bare_constants.py`
> - `knowledge/dev-logs/plan-lint-bare-constants-dev-2026-08-26.md`
>
> **Scope:**
> - `scripts/plan_lint.py`
> - `tests/test_plan_lint_bare_constants.py`
> - `knowledge/dev-logs/plan-lint-bare-constants-dev-2026-08-26.md`

## STEP 2 — QA (FULL suite + behavior probes)

> **Item 1 — full suite.** `cd "$(git rev-parse --show-toplevel)"`; `python3 -m pytest tests/ --tb=short -q 2>&1 | cat | tee knowledge/qa/evidence/plan-lint-bare-constants-2026-08-26/pytest_full.txt` — 0 failed (record the passed count with the derivation vs the 1483 baseline + 5 new).
> **Item 2 — behavior probes.** Run the committed plan_lint against TWO real Done plans from the prototype table — one that fired and one that did not — and paste both outputs: the firing one shows `(r) WARN` lines, the quiet one shows none, and BOTH exit with the same code they had pre-change (warn-first proven live: `(r)` never moves the exit). Extraction probes: `"(r) WARN"` in the committed plan_lint >= 1; `"def test_"` count == 5 in the test file; `cmp` vs live → 0 each.
> **Item 3 — hygiene + receipt** `knowledge/qa/evidence/plan-lint-bare-constants-2026-08-26/qa-receipt.md`: numstat 3 files; toplevel; reflog `-n 4` → 0 amends; per-item table, then the Rule 20 block INSIDE a section whose heading contains "Verification" (the 556 placement law).
>
> ⚠️ **Gate note:** this QA HAS a pytest summary (named above) — the gate parses; no benign override pre-declared.
>
> **Deposits:**
> - `knowledge/qa/evidence/plan-lint-bare-constants-2026-08-26/pytest_full.txt`
> - `knowledge/qa/evidence/plan-lint-bare-constants-2026-08-26/probes-raw.txt`
> - `knowledge/qa/evidence/plan-lint-bare-constants-2026-08-26/qa-receipt.md`
>
> **Scope:**
> - `knowledge/qa/evidence/plan-lint-bare-constants-2026-08-26/pytest_full.txt`
> - `knowledge/qa/evidence/plan-lint-bare-constants-2026-08-26/probes-raw.txt`
> - `knowledge/qa/evidence/plan-lint-bare-constants-2026-08-26/qa-receipt.md`

Rule 20 banner (byte-exact, inside the QA receipt's VERIFICATION section):

```
============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
```

## Drafting Cycle

**Tier:** T1 — one warn-first check + tests + the funnel's own measurement stage inside the plan; the verdict is never mechanized (the WARN text says so).

**Walk register:** `bellows/knowledge/research/walk-register-plan-lint-bare-constants-2026-08-26.md`

**Walk 0 (context pin, measured):** plan_lint 782 lines, `(q)` last letter taken, `(r)` count 0; corpus 694, sample 60 declared; the 554 design case + the ~10 tally; the banner-does-not-satisfy decision stated with its reason; the >600 tuning STOP with the never-silently-widen law.

**Walks:**
- Weak spots:          w1 dry — the IRONY CHECK passes (this plan's own probe constants each carry the clause it mechanizes); the regex traced against real shapes (`.timeout 5000`, `-n 4`, `x=3`, `3→0` all non-matching; `== 1`/`>= 2` matching as intended); marker-set substring redundancy noted harmless.
- Destruction:         w1 dry — three-arm resume; one commit; the prototype reads Done lanes read-only, absolute-anchored (outside the worktree by design, declared).
- Vulnerabilities:     w1 dry — warn-first proven three ways (the function returns a count and prints, never raises; the exit code untouched; QA Item 2 proves it LIVE on real plans); self-application on future deposits is advisory by construction.
- Integration-record:  w1 dry — the funnel's stages named at their sites; the >600 STOP prices noise to the CEO with the never-silently-widen law; the banner-does-not-satisfy decision carries its reason.
- ACID:                w1 dry — every stated count clause-clothed; one pathspec-limited pinned commit.
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
reads: /Users/marklehn/Developer/GitHub/bellows/scripts/plan_lint.py, /Users/marklehn/Developer/GitHub/governance/knowledge/decisions/Done, /Users/marklehn/Developer/GitHub/lessons-forge/knowledge/decisions/Done, /Users/marklehn/Developer/GitHub/bellows/knowledge/decisions/Done
writes: scripts/plan_lint.py, tests/test_plan_lint_bare_constants.py, knowledge/dev-logs/plan-lint-bare-constants-dev-2026-08-26.md, knowledge/qa/evidence/plan-lint-bare-constants-2026-08-26/pytest_full.txt, knowledge/qa/evidence/plan-lint-bare-constants-2026-08-26/probes-raw.txt, knowledge/qa/evidence/plan-lint-bare-constants-2026-08-26/qa-receipt.md
open_forks: batch item 2 (the wrap_check [4/memory] class gate) — the SERIAL sibling, deposits after this closes
walks: 2
yields: 0, 0
validation: cycle_check=BAR_MET, plan_lint=0_FAIL, fold_check=N/A
coherence: N/A
