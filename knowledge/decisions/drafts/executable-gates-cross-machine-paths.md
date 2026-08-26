# bellows — executable: gates gain the cross-machine path re-root (Strategy 4 in the one resolver every deposit gate shares) — the 560 class closed

**Date:** 2026-08-26 | **Project:** bellows | **Tier:** Small | **Dispatch Mode:** bellows | **cycle_tier:** T1 | **Test Scope:** targeted (gates tests) + full suite at QA | **Execution:** Step 1 (DEV) → Step 2 (QA) | **qa_steps:** 2 | **pause_for_verdict:** always

**auto_close:** false

**Depends on:** the CEO's "Proceed mechanization" (batch 2, item 2); the exec-560 measurement (five artifact rows, all through `_resolve_deposit_path`); the walk-0 call-site census (seven sites, one resolver).

## Why this exists

Cross-machine dispatch is live traffic now (560 was mini-authored, shop-driven; the mini runs its own plans in the 100000 block). Every such plan will re-hit the five-row artifact failure until the ONE resolver learns the other machine's layout shape.

## What this plan does NOT do

- No behavior change for any path that resolves today (Strategy 4 runs LAST, only on absolute-and-missing); no daemon restart (the fix arms at the next restart — stated); no per-machine config (the project basename IS the marker).

## Numbers discipline

⚠️ **Measured 2026-08-26; re-measure pre-flight; mismatch → HALT; every count carries measure-record-supersede.**

| id | pin | value | anchor |
|---|---|---|---|
| G1 | the resolver | `def _resolve_deposit_path` count-1 at gates.py; its final `    return None` count-1 WITHIN the function (locate by grep -nF between the def and the next def; quote the line number in the dev log) | `gates.py` (repo-relative — worktree law) |
| G2 | call sites | 7 (`grep -cF "_resolve_deposit_path(" ` minus the def — record; supersede with derivation) | ibid. |
| G3 | the 560 fixture | declared `/Users/marklehn/Developer/bellows/hooks/eluvian/wrap_check.py` vs executing root `.../GitHub/bellows` — the exact measured shape, reproduced in a test | exec-560's gate evidence |

## STEP 1 — DEV (the strategy + tests)

> **Task A — worktree discipline.** `cd "$(git rev-parse --show-toplevel)" && test -f gates.py && echo TREE_OK` — HALT unless TREE_OK. Probes: (i) `/usr/bin/grep -cF -- "Strategy 4 (cross-machine re-root)" gates.py; true`, (ii) `test -f tests/test_gates_cross_machine_paths.py && echo 1 || echo 0`. (0,0) → full run; (1,0) → resume at Task C; (1,1) → Task D commit-check; (0,1) → HALT.
>
> **Task B — the strategy.** In `gates.py`, the edit anchor is the UNIQUE two-line pair closing the resolver (count-1 asserted on the pair — bare `    return None` is not unique file-wide, walk-1 fold):
>
> ```
>         return os.path.abspath(p3)
>     return None
> ```
>
> Replace that pair with the first line kept plus the new strategy, i.e. with EXACTLY:
>
> ```python
>         return os.path.abspath(p3)
> ```
>
> followed by:
>
> ```python
>     # Strategy 4 (cross-machine re-root): an absolute path from ANOTHER
>     # machine's layout that still names this project — re-anchor the part
>     # after the LAST "/<project-name>/" segment onto the local roots
>     # (worktree first, where the agent just wrote). Measured need: exec-560,
>     # a mini-authored plan declared deposits at ~/Developer/bellows/... and
>     # five gate rows failed on layout literals while the work was exact.
>     if os.path.isabs(path):
>         marker = os.sep + os.path.basename(project_path) + os.sep
>         idx = path.rfind(marker)
>         if idx != -1:
>             rel = path[idx + len(marker):]
>             roots = ([wt_path] if wt_path and wt_path != project_path else [])
>             roots.append(project_path)
>             for _root in roots:
>                 cand = os.path.join(_root, rel)
>                 if os.path.isfile(cand) or os.path.isdir(cand):
>                     return os.path.abspath(cand)
>     return None
> ```
>
> Post-probes: `"Strategy 4 (cross-machine re-root)"` == 1; `"rfind(marker)"` == 1; the function still ends `return None` (fail-closed unchanged).
>
> **Task C — tests `tests/test_gates_cross_machine_paths.py`** (new): six tests over `_resolve_deposit_path` with tmp_path layouts: (1) THE 560 SHAPE — file exists at `<tmp>/GitHub/bellows/hooks/eluvian/wrap_check.py`, declared as `/Users/other/Developer/bellows/hooks/eluvian/wrap_check.py` with project_path=`<tmp>/GitHub/bellows` → resolves to the local file; (2) the same declared path with the file ABSENT → None (fail-closed); (3) a foreign absolute path NOT containing the project basename → None; (4) worktree-first: the file in BOTH wt and project → the wt copy returned; (5) the nested-marker case `/x/bellows/backup/bellows/f.py` with `f.py` at the project root → resolves via the LAST marker; (6) a RELATIVE path still resolves exactly as before (Strategy-4 untouched — regression guard). Targeted run: the new file + the existing gates tests (`-k gates or deposit`) — 0 failed (record counts; supersede with derivation).
>
> **Task D — dev log + commit.** `knowledge/dev-logs/gates-cross-machine-paths-dev-2026-08-26.md` (G1's located line number quoted, G2's census with derivation, probe raws, targeted raw). Commit (WORKTREE toplevel): `cd "$(git rev-parse --show-toplevel)" && git add gates.py tests/test_gates_cross_machine_paths.py knowledge/dev-logs/gates-cross-machine-paths-dev-2026-08-26.md && git commit -m "[<id from your plan filename>] gates-cross-machine-paths(gates-cross-machine-paths-2026-08-26): Strategy-4 re-root in the one shared resolver — the 560 class closed at seven call sites" -- gates.py tests/test_gates_cross_machine_paths.py knowledge/dev-logs/gates-cross-machine-paths-dev-2026-08-26.md && git rev-parse HEAD` — **CAPTURE_COMMIT**.
>
> **Deposits:**
> - `gates.py`
> - `tests/test_gates_cross_machine_paths.py`
> - `knowledge/dev-logs/gates-cross-machine-paths-dev-2026-08-26.md`
>
> **Scope:**
> - `gates.py`
> - `tests/test_gates_cross_machine_paths.py`
> - `knowledge/dev-logs/gates-cross-machine-paths-dev-2026-08-26.md`

## STEP 2 — QA (FULL suite + the 560 replay)

> **Item 1 — full suite.** `cd "$(git rev-parse --show-toplevel)"`; `python3 -m pytest tests/ --tb=short -q 2>&1 | cat | tee knowledge/qa/evidence/gates-cross-machine-paths-2026-08-26/pytest_full.txt` — 0 failed (record the count; derivation vs 1503 + 6).
> **Item 2 — THE 560 REPLAY.** A python snippet importing the COMMITTED `_resolve_deposit_path`, calling it with 560's EXACT declared literal `/Users/marklehn/Developer/bellows/hooks/eluvian/wrap_check.py` and project_path `/Users/marklehn/Developer/GitHub/bellows` → the resolved local path returned NON-None (paste raw — the measured incident replayed to green through the shipped code). Extraction probes: the three Task-B probes on `git show`; `cmp` vs live → 0 each. Raw → `knowledge/qa/evidence/gates-cross-machine-paths-2026-08-26/probes-raw.txt`.
> **Item 3 — hygiene + receipt** `knowledge/qa/evidence/gates-cross-machine-paths-2026-08-26/qa-receipt.md`: numstat 3 files; toplevel; reflog `-n 4` → 0 amends; per-item table, then the Rule 20 block INSIDE a "Verification"-headed section; ⚠️ the receipt STATES the daemon-staleness caveat (the running daemon keeps the old resolver until its next restart — the fix arms then; /eluvian surfaces the restart need).
>
> ⚠️ **Gate note:** pytest summary named above — the gate parses; no benign override pre-declared.
>
> **Deposits:**
> - `knowledge/qa/evidence/gates-cross-machine-paths-2026-08-26/pytest_full.txt`
> - `knowledge/qa/evidence/gates-cross-machine-paths-2026-08-26/probes-raw.txt`
> - `knowledge/qa/evidence/gates-cross-machine-paths-2026-08-26/qa-receipt.md`
>
> **Scope:**
> - `knowledge/qa/evidence/gates-cross-machine-paths-2026-08-26/pytest_full.txt`
> - `knowledge/qa/evidence/gates-cross-machine-paths-2026-08-26/probes-raw.txt`
> - `knowledge/qa/evidence/gates-cross-machine-paths-2026-08-26/qa-receipt.md`

Rule 20 banner (byte-exact, inside the QA receipt's VERIFICATION section):

```
============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
```

## Drafting Cycle

**Tier:** T1 — one strategy, one resolver, seven surfaces; the 560 incident replayed to green in QA; daemon staleness stated, never worked around.

**Walk register:** `bellows/knowledge/research/walk-register-gates-cross-machine-paths-2026-08-26.md`

**Walk 0 (context pin, measured):** the resolver + its seven call sites censused; the rfind-last-marker decision with its nested-path reason; Strategy-4 runs LAST on absolute-and-missing only (today's resolutions untouched — test 6 the regression guard); the staleness law.

**Walks:**
- Weak spots:          w1 1 folded — `    return None` is NOT unique file-wide: the edit anchor is the unique two-line pair (the p3 abspath return + the closing return None), quoted in Task B as the replacement target; count-1 asserted on the PAIR.
- Destruction:         w1 dry — Strategy 4 runs last, absolute-and-missing only; every miss still ends None (fail-closed unchanged, test 2 + test 6 the guards).
- Vulnerabilities:     w1 dry — the rfind-last-marker nested case tested; worktree-first order matches the resolver's existing Strategy-0 priority.
- Integration-record:  w1 dry — the daemon-staleness caveat stated in the plan, the receipt, and the register; the restart stays a deliberate act.
- ACID:                w1 dry — counts clause-clothed; one pathspec-limited commit.
- **Walk 1 total: one finding, folded.**
- Weak spots:          w2 dry — the pair anchor verified unique against the live file.
- Destruction:         w2 dry.
- Vulnerabilities:     w2 dry.
- Integration-record:  w2 dry.
- ACID:                w2 dry.
- **Walk 2 total: 0 findings — all five lenses dry.**

**Closing:** ✅ **BAR MET at walk 2 — dry confirming pass, all five lenses.** T1 two-walk form; no direction-class finding; close is MANUAL (CEO-lane verdicts).

**Fold-and-deposit exactly once.**

## Cycle Manifest
tier: T1
target: bellows/gates.py
class: shop-infra
reads: /Users/marklehn/Developer/GitHub/bellows/gates.py
writes: gates.py, tests/test_gates_cross_machine_paths.py, knowledge/dev-logs/gates-cross-machine-paths-dev-2026-08-26.md, knowledge/qa/evidence/gates-cross-machine-paths-2026-08-26/pytest_full.txt, knowledge/qa/evidence/gates-cross-machine-paths-2026-08-26/probes-raw.txt, knowledge/qa/evidence/gates-cross-machine-paths-2026-08-26/qa-receipt.md
open_forks: the remaining ledger (reconcile_plan.py; scope_check rename; the 23 CODE rows; the (r) lint's fenced-code false-positive refinement) — future batches at the CEO's call; the daemon restart that arms this fix (surfaced by /eluvian, performed deliberately)
walks: 2
yields: 1, 0
validation: cycle_check=BAR_MET, plan_lint=0_FAIL, fold_check=N/A
coherence: N/A
