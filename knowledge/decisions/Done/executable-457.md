# bellows — resolve_bellows_root() sentinel fix (no stray lifecycle.db)
**Date:** 2026-08-19 | **Tier:** Small | **Dispatch Mode:** bellows | **cycle_tier:** T1 | **Test Scope:** full | **Execution:** Step 1 (DEV) → Step 2 (QA) | **Priority:** 1

**auto_close:** false
**pause_for_verdict:** after_step_1

## Context

Implements the Rule 27 Gap Assessment from **diagnostic-455** (`knowledge/research/bellows-root-fallback-stray-2026-08-19.md`). `resolve_bellows_root()` (`bellows_root.py:27–28`) silently `return start` when no `config.json` ancestor exists, so any resolution from a non-bellows tree lands a stray `lifecycle.db` in a watched project (invoice-pulse, lessons-forge — both since deleted).

**Fix:** add a TRACKED secondary sentinel `bellows.py`. Walk for `config.json` first (unchanged — preserves worktree-safety), then a SECOND walk for `bellows.py` (handles CI/fresh-clone where the gitignored `config.json` is absent), then **raise** `ValueError` if neither is found (a loud failure beats a stray DB in the wrong repo). Extends `1ecf898`'s anchor intent; does not revert it.

## Drafting Cycle
**Tier:** T1 — triggers fired: T-1 (blast radius: 5 call sites depend on this resolver), T-7 (authored from diag-455 per Rule 27), T-8 (novel). NOT T-6 (engine code, not doctrine/gates — per diag-455 F9). Self-escalation to T2/cold-panel is available given core-infra blast radius; running T1 with a full regression-matrix test as the mitigation.
**Walk 0 (context pin):** `bellows_root.py` sha `dfdc656f8afb` (30 lines; the walk is lines 21–29). Sentinel `bellows.py` confirmed present at bellows root AND git-tracked (so present in every worktree). Existing test file `tests/test_bellows_root.py` (1428 B, from the clone-diff parent) — EXTEND, do not recreate. Clone-diff target: `Done/executable-bellows-root-helper-runner-conversion-2026-06-08.md` (the plan that created `bellows_root.py` + the config.json anchor) — the fix must not undo its worktree-safety. 5 call sites (all use the default `__file__` start; none pass `_start` in production, per diag-455 Q2).
**Direction verdict (after walk 1):** **PROCEED** — the diagnostic's design is sound; folds sharpen implementation correctness, none invalidate the approach.
**Walks:** 3 (bar MET — walk 3 record-class only, zero instruction-class, no restructuring fold).
- Weak spots:         w1 2 folded (1.1, 1.3); w2 1 folded (1.1 F7); w3 1 folded (F9 raise-message f-string — RECORD-class) — w3 instruction 0 / record 1.
- Destruction:        w1 1 folded (2.1); w2 dry; w3 dry.
- Vulnerabilities:    w1 1 folded (3.1); w2 dry; w3 dry.
- Integration-record: w1 1 folded (4.1 docstring); w2 1 folded (4.1 F8 tests-vs-existing-file); w3 dry.
- ACID:               w1 dry (1 record note 5.2); w2 dry; w3 dry.
**Conflicts:** none.
**Origin split (diagnostic):** w2 2 of 2 pre-existing (zero fold-damage); w3 F9 record-only. Instruction trend 5→2→0.
**§5 Conformance:** `plan_lint` run at shape-stability (walk 3) → **0 FAIL**. (c) QA banner pair PASSES (banner inlined proactively — plan-452 lesson); `full_suite.txt` named in the Deposits block proactively (plan-452 qa_test_result lesson). Only benign warn: no-Closing (cleared by this block).
**Closing:** walk 3 returned record-class only (1 record fold F9, 0 instruction), no restructuring fold — bar met (a confirming pass returning record-only is the signature the artifact converged before its account of itself; §2). §5 conformance clean (0 FAIL); closing-record re-read run (this block), dry; cycle CLOSED. Deposit exactly once (pending CEO go).

---
---

## STEP 1 — BELLOWS DEVELOPER

---

> **Identity:** You are the Bellows Developer. Read `bellows_root.py` and `tests/test_bellows_root.py` before editing. Read the diag-455 Gap Assessment (`knowledge/research/bellows-root-fallback-stray-2026-08-19.md`) Q5/Q6 as the authoritative design.
>
> **Task:** Fix `resolve_bellows_root()` in `bellows_root.py` and extend `tests/test_bellows_root.py`. Single production file changed.
>
> **The fix (folded — walk 1 F1, the critical correctness point):** implement as **TWO sequential walks**, NOT a combined check:
> 1. Walk up from `start` for `config.json` — return the first ancestor that has it. **Change line 28 (walk 2 F7): the loop's terminal `return start` IS the bug — remove it; when the walk reaches filesystem root without finding `config.json`, fall through to walk 2 (do NOT return start).** This walk MUST run to exhaustion first, because a bellows worktree CONTAINS a tracked `bellows.py`; a combined "config.json OR bellows.py" check would stop at the worktree and return it instead of canonical, **regressing worktree-safety**.
> 2. Only if no `config.json` ancestor exists, walk up again from `start` for `bellows.py` — return the first ancestor that has it (handles CI/fresh-clone where the gitignored `config.json` is absent but `bellows.py` is tracked-present).
> 3. If NEITHER sentinel is found in any ancestor, raise with the ACTUAL start path interpolated (f-string, not a literal placeholder — walk 3 F9): `raise ValueError(f"resolve_bellows_root: no bellows sentinel (config.json or bellows.py) found in any ancestor of {start}")` — do NOT `return start`. (The guard test matches on `"no bellows sentinel"`.)
>
> **Docstring (folded — walk 1 F4):** update lines 13–19 — they currently claim "falls back to the start dir … preserves current behavior in CI/fresh-clone." That is now FALSE. Rewrite to describe the two-sentinel behavior and the raise.
>
> **Tests (folded — walk 2 F8, reconciled against the EXISTING file — read it first).** `tests/test_bellows_root.py` ALREADY has `test_resolves_to_dir_with_config` (canonical) and `test_walks_up_to_config` (worktree→canonical). Do NOT duplicate them. Make exactly these changes, asserting the RETURNED path (observe the effect):
> - **UPDATE `test_falls_back_when_no_config`** — it currently asserts the OLD buggy fallback (`resolve_bellows_root(_start=<no-anchor>) == deep`). That behavior is exactly what this fix REMOVES. Flip it to `pytest.raises(ValueError, match="no bellows sentinel")` (its `a/b/c` tree has neither sentinel). Rename appropriately (e.g. `test_non_bellows_tree_raises`). **"Keep existing tests passing" does NOT apply to this one — it encodes the bug.**
> - **STRENGTHEN `test_walks_up_to_config`** — add a tracked-style `bellows.py` INSIDE the `wt1/` worktree dir. Under the correct two-walk order the result is still `canonical` (config.json wins); a wrong combined-check implementation would return `wt1`. This turns the existing test into a real guard for the two-walk ORDER (walk 1 F1).
> - **ADD a fresh-clone test** — a temp tree with `bellows.py` at root and NO `config.json` → resolves to that root (this case is genuinely new).
> - `test_resolves_to_dir_with_config` (canonical) stays as-is — it still passes.
> Net: 1 test updated (flip to raise), 1 strengthened (bellows.py in wt1), 1 added (fresh-clone), 1 unchanged.
>
> **Production-safety check (folded — walk 1 F1.3):** confirm the change does NOT make any production import-time resolution raise — `lifecycle.py:21` and `runner.py:23` resolve at import from the canonical `__file__`, which finds `config.json`; a quick `python3 -c "import lifecycle, runner"` from the bellows root must succeed without raising.
>
> **Targeted run + commit:** `python3 -m pytest tests/test_bellows_root.py -q 2>&1 | cat` — all pass. Commit `fix(bellows): resolve_bellows_root() bellows.py sentinel + raise on no-anchor — no stray lifecycle.db [<id>]`. Deposit dev log `knowledge/development/bellows-root-sentinel-fix-2026-08-19.md` (the two-walk rationale, the 4-env test results, the import-safety check output). End with an Output Receipt recording **Status AND the DEV commit sha** (QA check-3 reads it).
>
> **Deposits:**
> - `bellows_root.py`
> - `tests/test_bellows_root.py`
> - `knowledge/development/bellows-root-sentinel-fix-2026-08-19.md`

---
---

## STEP 2 — BELLOWS QA ANALYST

---

> **Identity:** You are the Bellows QA Analyst. Read the Step 1 dev log; if its Output Receipt is not Complete, stop and report.
>
> **(1) Guard-test file passes + covers 4 environments.** `python3 -m pytest tests/test_bellows_root.py -v 2>&1 | cat` → evidence file `knowledge/qa/evidence/executable-bellows-root-sentinel-fix-2026-08-19/test_bellows_root.txt`. Confirm the four env tests (canonical, worktree→canonical, fresh-clone, non-bellows-raises) are present and pass.
>
> **(2) Full suite — Rule 21.** `python3 -m pytest tests/ -q -rf 2>&1 | cat` → evidence file `.../full_suite.txt`. Extract FAILED node-ids via `grep -F 'FAILED ' <out> | awk '{print $2}'`; assert the set is empty (bellows suite baseline is green — any failure is a regression). Record raw tail + the node-id set.
>
> **(3) No unintended production change (scope).** Read the DEV commit sha from the Step-1 dev log Output Receipt, then `git --no-pager show --name-only --format= <DEV_COMMIT>` → assert only `bellows_root.py`, `tests/test_bellows_root.py`, and `knowledge/` paths. Evidence file `.../scope.txt`.
>
> **(4) QA report** to `knowledge/qa/2026-08-19-bellows-root-sentinel-fix-qa.md` with a `| Check | Expected | Status | Evidence |` table (rows 1–3). Do NOT mark a ❌ row ✅; hedging keywords auto-fail.
>
> **(5) Rule 20 self-check** — run the canonical block from `/Users/marklehn/Developer/GitHub/RULE_20_SELF_CHECK_BLOCK.md` with `plan_slug: executable-bellows-root-sentinel-fix-2026-08-19`, the qa report path, the evidence dir, and `required_evidence_files: ["test_bellows_root.txt", "full_suite.txt", "scope.txt"]`. The block prints the banner `Rule 20 — QA Self-Check Results` and, on success, a line beginning `PASSED — SELF-CHECK PASSED` (both verbatim, em-dashes — the gate byte-matches); include the literal stdout under a heading containing "verification". If it prints `FAILED — SELF-CHECK FAILED`, halt.
>
> **Deposits:**
> - `knowledge/qa/2026-08-19-bellows-root-sentinel-fix-qa.md`
> - `knowledge/qa/evidence/executable-bellows-root-sentinel-fix-2026-08-19/`
> - `knowledge/qa/evidence/executable-bellows-root-sentinel-fix-2026-08-19/full_suite.txt`
