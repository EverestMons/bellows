# bellows — executable: /wrap ⊇ the old "session wrap" — the two dropped clauses restored, the project-push law enforced

**Date:** 2026-08-25 | **Project:** bellows | **Tier:** Small | **Dispatch Mode:** bellows | **cycle_tier:** T1 | **Test Scope:** bellows suite | **Execution:** Step 1 (DEV) → Step 2 (QA) | **qa_steps:** 2 | **pause_for_verdict:** always

**auto_close:** false

**Depends on:** the CEO's clarified directive ("this was also an assurance to make sure that /wrap contains all that 'session wrap' was previously doing") + the Planner's superset diff 2026-08-25 of the three instruction sources (the `eluvian-session-wrap-ritual` memory = the old phrase-era ritual; the vendored `hooks/commands/wrap.md` = the canonical /wrap; `wrap_check.py` = the enforced set). **The measured gaps:** (G1) the memory's 3b guard "classes-not-narratives, no duplicating recorded classes" is ABSENT from wrap.md's 3b; (G2) the memory's closing law "Push each repo" is present in wrap.md for steps 2/3/4 but ABSENT from step 1 (project repos) — AND unenforced: wrap_check's `[1/project]` checks Done/ porcelain only, while bellows/root/memory all have `unpushed_count` arms. Everything else in the old ritual is present in wrap.md, several parts strengthened (fetch-first, machine scoping, keyed 3b, 3d — all post-memory additions).

## Why this exists

The equivalence 534 shipped is only complete if the canonical ritual is a SUPERSET of what the phrase era did from memory — otherwise routing the phrase to /wrap silently DROPS the two clauses the memory carried. G1 is a content guard on the register's quality; G2 is the multi-machine shop's freshness law with a measured teeth-gap (a project repo can wrap with unpushed commits today).

## What this plan does NOT do

- **It does not modify the memory entry** — that refresh (retiring its stale pre-524 verdict-format line, pointing at wrap.md as canonical) is the Planner's own post-close act, out of the sandbox by design.
- **It does not change the arm/stop/debt hooks, the TRIGGER, or the 3b/3d predicates** — only wrap.md's prose (two clauses) and wrap_check's `[1/project]` arm (+ tests).

## Numbers discipline

⚠️ **Measured 2026-08-25; re-derive — yours supersede.**

| id | pin | value | anchor |
|---|---|---|---|
| S1 | wrap.md step 1 | ends `Leave unrelated pre-existing untracked files alone.` — no push clause | the step-1 bullet in hooks/commands/wrap.md |
| S2 | wrap.md 3b guard list | `(house format; not while a lessons-forge cycle plan sits un-run; verify the prior last entry intact after append)` — lacks the classes clause | the parenthetical in the 3b block |
| S3 | wrap_check [1/project] | iterates `project_done_dirs()`, Done/ porcelain only (wrap_check.py:110-120); NO unpushed arm | contrast the bellows arm at :134-136 |
| S4 | unpushed_count semantics | returns None when no upstream (fail-open skip) — wrap_check.py:74-75 | the new arm inherits this: no-upstream projects never block |
| S5 | test homes | tests/test_wrap_sentinel.py + tests/test_wrap_hooks.py (the wrap_check harness lives in the sentinel suite — read both, use the existing fixture pattern) | re-count at execution |
| S6 | suite floor | **1465 collected** | `--collect-only -q`; re-derive |

## MUST-PRESERVE

- ⚠️ **THE GREP SHIM IS BROKEN: `/usr/bin/grep`; zero-match exits 1, never &&-chain.**
- ⚠️ **Fence:** diff == hooks/commands/wrap.md + hooks/eluvian/wrap_check.py + the touched test file(s), nothing else; wrap.md's diff is the TWO clause insertions only (every other line byte-identical); wrap_check's diff is the ONE new arm inside the existing [1/project] loop.
- ⚠️ **The new arm inherits fail-open on no-upstream (S4)** and reports per-repo like the bellows arm's message shape.
- ⚠️ **This machine's live command files are SYMLINKS to the vendored wrap.md (R-F1)** — the edit lands live at merge with no sync step; say nothing about syncing.
- ⚠️ **Worktree dispatch; deposit paths project-relative.**

## STEP 1 — DEV: two clauses, one arm, tests

**Role:** DEV.

**E1 (S1):** wrap.md step 1 gains, after the leave-alone sentence: `Then push each touched project repo — the push-each law covers ALL FOUR repo classes, not just bellows/root/memory.`
**E2 (S2):** the 3b parenthetical gains two items: `; classes-not-narratives — record the transferable CLASS, never the session's story; never duplicate an already-recorded class` (keeping the existing three guards verbatim).
**E3 (S3):** inside the `[1/project]` loop, after the porcelain check: an `unpushed_count(repo)` arm — non-None and >0 → `[1/project] {repo.name}: {n} commit(s) not pushed — push {repo.name}.` (the bellows arm's message shape, per-project).
**E4 (S5):** tests: (1) a project repo with unpushed commits fails [1/project] with the new message; (2) a project repo with no upstream is SKIPPED (fail-open pinned); (3) clean-and-pushed passes; (4) the two wrap.md clauses present — a doc test greping the vendored file for both literals (`push each touched project repo`; `classes-not-narratives`), keeping the ritual file's letter pinned henceforth. Targeted run.

**Deposits:**
- `/Users/marklehn/Developer/GitHub/bellows/hooks/commands/wrap.md`
- `/Users/marklehn/Developer/GitHub/bellows/hooks/eluvian/wrap_check.py`
- `/Users/marklehn/Developer/GitHub/bellows/tests/test_wrap_sentinel.py`

**Scope:**
- `/Users/marklehn/Developer/GitHub/bellows/hooks/commands/wrap.md`
- `/Users/marklehn/Developer/GitHub/bellows/hooks/eluvian/wrap_check.py`
- `/Users/marklehn/Developer/GitHub/bellows/tests/`

**Commit:** `git add hooks/commands/wrap.md hooks/eluvian/wrap_check.py tests/ && git commit -m "[<id>] wrap: /wrap superset of the old ritual — classes-clause + project-push law restored, [1/project] push arm enforced"` in YOUR worktree cwd.

## STEP 2 — QA

**Role:** QA.

**Q1 — full suite.** `python3 -m pytest tests/ -q`; RAW output to `knowledge/qa/evidence/wrap-ritual-superset/pytest_full.txt`; accounting vs S6; zero failures.
**Q2 — the fence.** Diff-stat == the named files; wrap.md's diff shows exactly the two insertions (quote both hunks); wrap_check's diff is confined to the [1/project] loop (quote the hunk).
**Q3 — report.** `knowledge/qa/evidence/wrap-ritual-superset/qa-report.md` with Q1-Q2; failure-marker mentions in backticks.

> **QA SELF-CHECK — Rule 20.** Post the block from `/Users/marklehn/Developer/GitHub/RULE_20_SELF_CHECK_BLOCK.md` verbatim, under the banner **`Rule 20 — QA Self-Check Results`**, and close with **`PASSED — SELF-CHECK PASSED`** only if every check genuinely passed. ⚠️ Both literals are matched by `plan_lint` check (c) and neither may be paraphrased. Rule 20 block + Q results in the `.md`; raw suite output in `pytest_full.txt` — the two QA gates scan DIFFERENT extensions.

**Deposits:**
- `/Users/marklehn/Developer/GitHub/bellows/knowledge/qa/evidence/wrap-ritual-superset/pytest_full.txt`
- `/Users/marklehn/Developer/GitHub/bellows/knowledge/qa/evidence/wrap-ritual-superset/qa-report.md`

**Scope:**
- `/Users/marklehn/Developer/GitHub/bellows/knowledge/qa/evidence/wrap-ritual-superset/`

**Commit:** `git add knowledge/qa/evidence/wrap-ritual-superset/ && git commit -m "[<id>] qa: wrap ritual superset — full suite + two-hunk fence"` in YOUR worktree cwd.

## Drafting Cycle
**Tier:** T1 computed — two prose clauses + one loop arm cloning an adjacent arm's shape; panel not convened with reasoning (the arm is a copy of the thrice-proven bellows/root/memory shape with fail-open pinned by test; the prose edits gain their own pinning doc test).
**Walk register:** `governance/knowledge/research/walk-register-executable-wrap-superset.md`
**Walks:** walk 0 = the three-source superset diff; **walks 1–2 complete** — five lenses each, BOTH dry (zero folds).
**Direction verdict (after walk 1): PROCEED.** Tested, not judged.
- Weak spots:          w1 dry; w2 dry
- Destruction:         w1 dry; w2 dry
- Vulnerabilities:     w1 dry; w2 dry
- Integration-record:  w1 dry; w2 dry — close obligations discharged at this freeze
- ACID:                w1 dry; w2 dry
**Conformance (§5):** recorded at the freeze from actual runs: walk_register_lint CONFORMANT (verdict channel, branched-on); cycle_check BAR_MET post-finalization (verdict channel, branched-on); plan_lint 0 FAIL at the scratch-mirror path.
**Closing:** **walk 2 met the bar — all five lenses dry.** Instruction series **0 → 0**. Receipt BEFORE staging (structural) → shop-infra hold → release under the CEO's directive → claim. Activation: wrap.md live at merge (R-F1 symlinks); the wrap_check arm live at the next wrap invocation (subprocess-read from disk).

## Cycle Manifest
tier: T1
target: hooks/eluvian/wrap_check.py
class: shop-infra
reads: /Users/marklehn/Developer/GitHub/bellows/hooks/commands/wrap.md, /Users/marklehn/Developer/GitHub/bellows/hooks/eluvian/wrap_check.py, /Users/marklehn/Developer/GitHub/bellows/tests/test_wrap_sentinel.py, /Users/marklehn/Developer/GitHub/bellows/tests/test_wrap_hooks.py
writes: hooks/commands/wrap.md, hooks/eluvian/wrap_check.py, tests/test_wrap_sentinel.py, knowledge/qa/evidence/wrap-ritual-superset/pytest_full.txt, knowledge/qa/evidence/wrap-ritual-superset/qa-report.md
open_forks: none — the superset diff found exactly two gaps; both close here; the memory refresh is the Planner's post-close act
walks: 2
yields: 0, 0
validation: cycle_check=BAR_MET, plan_lint=0_FAIL, fold_check=N/A
coherence: N/A

## Rule 20 — QA Self-Check Block

Step 2 is the QA step; the block is posted there per its mandate. Step 1 is DEV-only.
