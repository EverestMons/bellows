# bellows — executable: wrap-phrase equivalence — the armed context routes to the /wrap skill, closing the instruction half

**Date:** 2026-08-25 | **Project:** bellows | **Tier:** Small | **Dispatch Mode:** bellows | **cycle_tier:** T1 | **Test Scope:** bellows suite | **Execution:** Step 1 (DEV) → Step 2 (QA) | **qa_steps:** 2 | **pause_for_verdict:** always

**auto_close:** false

**Depends on:** the CEO directive "ensure that /wrap and 'session wrap' are equivalent actions" + the Planner's measurement 2026-08-25: the ARM half is equivalent (the TRIGGER regex live-tested — all command forms arm, discussion forms don't) and the COMPLETION half is equivalent by construction (same sentinel, same wrap_check), but the INSTRUCTION half is not — `/wrap` loads the canonical vendored ritual while the phrase path's `additionalContext` points at a MEMORY ENTRY (`eluvian-session-wrap-ritual`), leaving the ritual's letter (fetch-first, keyed 3b, 3d sweep, machine arms) to recall. The instruction-vs-mechanism class, closed by one string change.

## Why this exists

A phrase-armed wrap that runs from memory can satisfy wrap_check while missing the ritual's non-checked letter (the 3d sweep's question, the fetch-first law on a multi-machine shop). Routing the armed context to the SAME skill `/wrap` invokes makes the two entry points converge on one canonical instruction source — equivalence by construction, not by recall.

## What this plan does NOT do

- **The TRIGGER regex is UNTOUCHED** — its match policy is measured-correct and is a MUST-PRESERVE (a widened trigger false-arms the hard-block lock; a narrowed one un-arms real requests).
- **Only the `additionalContext` string in `hooks/eluvian/wrap_arm_hook.py` changes, plus its tests.** No other hook, no wrap.md, no wrap_check.

## Numbers discipline

⚠️ **Measured 2026-08-25; re-derive — yours supersede.**

| id | pin | value | anchor |
|---|---|---|---|
| W1 | the context string | wrap_arm_hook.py:106-112 — the `additionalContext` referencing "the /wrap ritual (eluvian-session-wrap-ritual memory)" | the ONLY `additionalContext` in the file |
| W2 | the trigger (context, not an edit target) | the start-anchored TRIGGER at :40-45; live-tested at authoring: 8/8 command forms ARM, 2/2 discussion forms don't | MUST-PRESERVE fence |
| W3 | the test home | tests/test_wrap_hooks.py (the wrap-hook suite; 20 tests at the E3 era — re-count) | the new assertions live here |
| W4 | suite floor | **1453 collected** | `--collect-only -q`; re-derive |
| W5 | the skill name | the live command is the `/wrap` skill — the vendored `hooks/commands/wrap.md`, symlinked live on this machine (R-F1) and one command away on any machine (exec-533) | the message should name the SKILL invocation, not a file path (paths differ per machine; the skill resolves per-machine) |

## MUST-PRESERVE

- ⚠️ **THE GREP SHIM IS BROKEN: `/usr/bin/grep`; zero-match exits 1, never &&-chain.**
- ⚠️ **The TRIGGER regex and every other line of the hook are byte-untouched** — QA proves it: the diff's only hook hunk is the string.
- ⚠️ **The message keeps its two load-bearing clauses:** the cannot-end-turn warning and the disarm instruction (removing the sentinel) — the false-arm escape must survive.
- ⚠️ **Fence:** diff-stat == wrap_arm_hook.py + tests/test_wrap_hooks.py.
- ⚠️ **Worktree dispatch; deposit paths project-relative.**

## STEP 1 — DEV: the string, the tests

**Role:** DEV.

**E1 (W1):** replace the `additionalContext` body with (exact text, the deliverable):
`[wrap-lock ARMED] A session wrap was requested; the completion lock is engaged. FIRST invoke the /wrap skill (Skill tool, skill "wrap") — it loads the canonical ritual; a phrase-triggered wrap follows the SAME ritual as /wrap, never memory. You cannot end a turn until wrap_check.py verifies all four repos. If this was not a wrap request, remove {sentinel} to disarm.`
(keep the f-string's `{sentinel}` interpolation exactly as-is).

**E2 (W3):** tests in test_wrap_hooks.py: (1) the armed output's additionalContext contains the literal `invoke the /wrap skill` (case-insensitive) and the literal `wrap_check.py`; (2) it still contains the disarm clause (the sentinel path); (3) the TRIGGER fence — a regression test pinning the measured matrix: the 8 arming forms match, the 2 discussion forms don't (parametrized). ⚠️ Import hazard (measured at authoring): a naive import of the hook module can EXECUTE its main path (stdin read + SystemExit) — use the import pattern the EXISTING test_wrap_hooks.py suite already uses for this hook (read it first; that pattern is the law), never invent a new loader. Run the wrap-hook suite targeted.

**Deposits:**
- `/Users/marklehn/Developer/GitHub/bellows/hooks/eluvian/wrap_arm_hook.py`
- `/Users/marklehn/Developer/GitHub/bellows/tests/test_wrap_hooks.py`

**Scope:**
- `/Users/marklehn/Developer/GitHub/bellows/hooks/eluvian/wrap_arm_hook.py`
- `/Users/marklehn/Developer/GitHub/bellows/tests/test_wrap_hooks.py`

**Commit:** `git add hooks/eluvian/wrap_arm_hook.py tests/test_wrap_hooks.py && git commit -m "[<id>] wrap-arm: phrase path routes to the /wrap skill — instruction equivalence by construction; trigger regex fenced by test"` in YOUR worktree cwd.

## STEP 2 — QA

**Role:** QA.

**Q1 — full suite.** `python3 -m pytest tests/ -q` from the repo root; RAW output to `knowledge/qa/evidence/wrap-phrase-equivalence/pytest_full.txt`; accounting vs W4; zero failures.
**Q2 — the fence.** Diff-stat == the two files; the hook's diff contains EXACTLY ONE hunk and it is the string (quote the hunk header); the TRIGGER regex lines byte-identical (`git diff HEAD~1 -- hooks/eluvian/wrap_arm_hook.py` shows no regex lines).
**Q3 — report.** `knowledge/qa/evidence/wrap-phrase-equivalence/qa-report.md` with Q1-Q2; failure-marker mentions in backticks per the 532 discipline.

> **QA SELF-CHECK — Rule 20.** Post the block from `/Users/marklehn/Developer/GitHub/RULE_20_SELF_CHECK_BLOCK.md` verbatim, under the banner **`Rule 20 — QA Self-Check Results`**, and close with **`PASSED — SELF-CHECK PASSED`** only if every check genuinely passed. ⚠️ Both literals are matched by `plan_lint` check (c) and neither may be paraphrased. Rule 20 block + Q results in the `.md`; raw suite output in `pytest_full.txt` — the two QA gates scan DIFFERENT extensions.

**Deposits:**
- `/Users/marklehn/Developer/GitHub/bellows/knowledge/qa/evidence/wrap-phrase-equivalence/pytest_full.txt`
- `/Users/marklehn/Developer/GitHub/bellows/knowledge/qa/evidence/wrap-phrase-equivalence/qa-report.md`

**Scope:**
- `/Users/marklehn/Developer/GitHub/bellows/knowledge/qa/evidence/wrap-phrase-equivalence/`

**Commit:** `git add knowledge/qa/evidence/wrap-phrase-equivalence/ && git commit -m "[<id>] qa: wrap-phrase equivalence — full suite + string-only fence"` in YOUR worktree cwd.

## Drafting Cycle
**Tier:** T1 computed — one string in one hook + tests; panel not convened with reasoning (the risky surface — the TRIGGER — is explicitly fenced untouched and gains its first pinning regression test; the change is the message, whose two load-bearing clauses are test-asserted).
**Walk register:** `governance/knowledge/research/walk-register-executable-wrap-phrase.md`
**Walks:** walk 0 pinned; **walks 1–2 complete** — five lenses each; walk 1 folded 1 (the import-executes-main hazard on the trigger test), walk 2 dry across all five lenses.
**Direction verdict (after walk 1): PROCEED.** Tested, not judged.
- Weak spots:          w1 dry; w2 dry
- Destruction:         w1 dry; w2 dry
- Vulnerabilities:     w1 1 folded — instruction 1 / record 0; w2 dry
- Integration-record:  w1 dry; w2 dry — close obligations discharged at this freeze
- ACID:                w1 dry; w2 dry
**Conformance (§5):** recorded at the freeze from actual runs: walk_register_lint CONFORMANT (verdict channel, branched-on); cycle_check BAR_MET post-finalization (verdict channel, branched-on); plan_lint 0 FAIL at the scratch-mirror path.
**Closing:** **walk 2 met the bar — all five lenses dry.** Instruction series **1 → 0**. Receipt BEFORE staging (structural) → shop-infra hold → release under the CEO's directive → claim. ⚠️ Activation note: HOOKS run per-invocation from disk — the new context is live for the NEXT prompt after merge, no daemon restart involved.

## Cycle Manifest
tier: T1
target: hooks/eluvian/wrap_arm_hook.py
class: shop-infra
reads: /Users/marklehn/Developer/GitHub/bellows/hooks/eluvian/wrap_arm_hook.py, /Users/marklehn/Developer/GitHub/bellows/tests/test_wrap_hooks.py, /Users/marklehn/Developer/GitHub/bellows/hooks/commands/wrap.md
writes: hooks/eluvian/wrap_arm_hook.py, tests/test_wrap_hooks.py, knowledge/qa/evidence/wrap-phrase-equivalence/pytest_full.txt, knowledge/qa/evidence/wrap-phrase-equivalence/qa-report.md
open_forks: none — the arm and completion halves are measured-equivalent; this closes the instruction half
walks: 2
yields: 1, 0
validation: cycle_check=BAR_MET, plan_lint=0_FAIL, fold_check=N/A
coherence: N/A

## Rule 20 — QA Self-Check Block

Step 2 is the QA step; the block is posted there per its mandate. Step 1 is DEV-only.
