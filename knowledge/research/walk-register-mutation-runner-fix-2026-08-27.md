# Walk register — `mutation-runner-fix-2026-08-27` (bellows)

**schema_version:** `0.3`

**Plan:** `bellows/knowledge/decisions/drafts/executable-mutation-runner.md` (stable slug; corrected re-deposit after the exec-574 halt)
**Tier:** T1 (Small — one subprocess-environment fix plus three tests; class shop-infra). **Panel: none.**
**Opened:** 2026-08-27

---

## Walk 0 — context pin (REAL, measured 2026-08-27)

1. **The defect, and how it surfaced:** exec-574's runner failed its OWN test suite, deterministically 3/3, on `test_killed_when_mutant_breaks_the_test`. The DEV step passed 7/7 gates because DEV does not gate on test results (`qa_test_result` is QA-only), and its dev log recorded `8 passed` against a tree that is `1 failed, 7 passed`.
2. **Mechanism, diagnosed with a positive control:** CPython invalidates bytecode by `(source mtime, source size)`. The synthetic mutant swaps `return a + b` for `return a - b` — IDENTICAL byte length — so when both writes land in the same mtime second the cached `.pyc` stays valid and the mutant run executes BASELINE code, scoring SURVIVED.
3. **⚠️ The arm the 574 verdict could NOT explain, now resolved — and it changes the fix.** Clearing `__pycache__` did nothing because there is no `__pycache__`: this machine has `sys.pycache_prefix = /Users/marklehn/Library/Caches/com.apple.python` (the Apple system-Python default), which redirects bytecode OUT of the source tree into a mirror of the ABSOLUTE source path. Measured: after a baseline run, `find . -name __pycache__` returns nothing while `~/Library/Caches/com.apple.python/<abs-src-dir>/target.cpython-39.pyc` exists. Deleting THAT file made the mutated test fail correctly. **The cache location is environment-dependent, so no clearing strategy is portable** — which is why the fix is the env var, not a cleanup step. The 574 verdict flagged this arm as unexplained and prescribed the env var anyway; that caution was correct and is now completed rather than superseded.
4. **The portable fix, verified in BOTH directions before authoring:** `PYTHONDONTWRITEBYTECODE=1` in the pytest subprocess env — unmutated passes, mutated (same length) fails.
5. **Severity priced honestly:** the failure direction is FALSE SURVIVED — a false alarm, never a false KILLED, so no confidence could have been manufactured. But same-length edits are ordinary (operator flips, boolean swaps, digit changes), so the tool is unfit as-is.
6. **Everything else in 574 was built correctly** and is preserved unchanged: exit-1-only KILLED, green-baseline control, anchor-count-1, replacement-present-after-write, live-tree sha256 in `finally`.

⚠️ Walk 0 carries no fold rows. Walks 1+ appended AFTER the draft exists, from real passes.

---

## Walk 1 — five-lens sequential walk (post-draft, real)

| id | walk | lens | sub_question | origin | finding | pre_fold_text | resolution |
|---|---|---|---|---|---|---|---|
| w1-1 | 1 | Weak spots | is QA Item 4 an instruction or a transcript? | pre-existing | the item contained the Planner's own DELIBERATION — it proposed an identifier swap, rejected it mid-sentence ("no: that raises NameError"), considered the TERMINAL inversion, rejected that on length, and only then arrived at a synthetic target. An agent reading it must re-derive the conclusion from the argument, and may pick one of the rejected branches | `**Item 4 — the same-length trap, proven live on the real tool:** copy the manifest to a temp file adding a mutant whose anchor and replacement have EQUAL length and whose change is semantically real — use _verdict_issued(res, plan_id, _step_of(h)) -> _verdict_issued(res, plan_id, _step_OF(h))... **no**: that raises NameError rather than passing. Instead use M2's line with an equal-length inversion: anchor `        if state not in TERMINAL:` -> replacement `        if state in TERMINAL:` is NOT equal length, so pad is impossible — therefore construct this probe on a SYNTHETIC target instead: create a temp repo (target.py with return a + b, a test asserting 3), a manifest mutating to return a - b, and run the tool -> must score KILLED. Paste raw. State plainly in the receipt that this probe uses a synthetic target because the real target has no equal-length semantic mutation available — do not dress a synthetic probe as a live one.` (complete pre-image bytes, no ellipsis) | folded (**verbatim-ellipsis**: the `...` inside pre_fold_text is part of the COMPLETE pre-image bytes — the Planner's own draft contained those three dots mid-sentence; nothing is elided here): rewritten as a flat instruction that builds the synthetic repo, names the mutation, states the expected KILLED, and requires the receipt to LABEL the target synthetic — with the reason (the real target has no equal-length, semantically-real, non-crashing mutation) stated as a fact rather than derived in front of the reader |
| — | 1 | Destruction | — | — | DRY — the change is one `env=` argument; the tool still never writes the live tree, and the sha256 assertion in `finally` is listed in MUST-PRESERVE with a re-assert probe | — | no fold |
| w1-2 | 1 | Vulnerabilities | does test 3 test anything test 1 does not? | pre-existing | `test_baseline_does_not_poison_the_mutant_run` was described as "test 1's sibling at the sequence level" but its construction was identical — one synthetic repo, one same-length mutation, assert KILLED. A duplicate presented as distinct coverage inflates the apparent test count without adding discrimination | `**test_baseline_does_not_poison_the_mutant_run** — the mechanism stated directly: a synthetic repo where the baseline run and the mutant run use the SAME target file and a same-length mutation; assert KILLED. This is test 1's sibling at the sequence level rather than the string level — if the baseline's bytecode leaked, this is what would catch it.` | folded: replaced with `test_consecutive_same_length_mutants_are_both_killed` — TWO mutants in one run, each an equal-length change to a different line, both required KILLED. It guards cache carry-over ACROSS mutants, which the single-mutant test structurally cannot see, and carries an instruction to DROP it rather than weaken it into a copy if two independent equal-length mutations cannot be constructed |
| — | 1 | Integration-record | — | — | DRY — manifest reads include the halted 574 plan; deposits and scope agree on the six files | — | no fold |
| — | 1 | ACID | — | — | DRY — two pathspec-limited commits (3 files each) with `git show --stat` asserts | — | no fold |

**Walk 1 total: 2 findings (instruction 2 / record 0), folded. Direction verdict: PROCEED.**

---

## Walk 2 — five-lens sequential walk (real)

| id | walk | lens | sub_question | origin | finding | pre_fold_text | resolution |
|---|---|---|---|---|---|---|---|
| w2-1 | 2 | Weak spots | does the plan admit the suite is currently RED? | pre-existing | D6 gave the exec-573 numbers (1612 collected) with a vague aside to re-derive, but never said that 574's DEV commit LANDED before its halt, that its 8 tests are therefore in tree, that one of them FAILS, and hence that the full suite is red right now. QA Item 1 gates on `0 failed`, so an agent working from the stale baseline could mis-derive its target and either panic at a red suite or accept a wrong number | `D6 row, verbatim, pipes written as SLASH: baselines SLASH tests/test_mutation_check.py collects **8**; tests/test_gate_watcher.py collects **46**; full suite **1612 collected** (1611 passed + 1 skipped at exec-573) — note 574's 8 runner tests are IN tree, so re-derive SLASH pytest --collect-only` (complete pre-image bytes; the source row's table pipes are transcribed as the word SLASH so this cell cannot break its own column alignment — nothing elided) | folded: D6 now states the suite is CURRENTLY RED, gives the measured 1620 collected, explains why (574's DEV commit landed pre-halt), and states the expected post-plan arithmetic 1620 + 3 = 1623 with 0 failed, flagged as load-bearing for the QA gate |
| — | 2 | Destruction | — | — | DRY | — | no fold |
| — | 2 | Vulnerabilities | — | — | DRY — Task B requires REPRODUCING the failure before fixing, with a STOP arm if the tree is green (a fix for an unobserved defect is a guess); Task D forbids weakening any of the 8 existing assertions | — | no fold |
| — | 2 | Integration-record | — | — | DRY — the `_run_pytest(` occurrence pin verified live at authoring: **3** (one definition, two call sites), matching the plan's stated expectation | — | no fold |
| — | 2 | ACID | — | — | DRY | — | no fold |

**Walk 2 total: 1 finding (instruction 1 / record 0), folded.**

---

## Walk 3 — five-lens sequential walk (real)

| id | walk | lens | sub_question | origin | finding | pre_fold_text | resolution |
|---|---|---|---|---|---|---|---|
| — | 3 | Weak spots | — | — | DRY — `import os` confirmed already present in the module, so Task C's "add if absent" is a no-op rather than a conflicting instruction | — | no fold |
| — | 3 | Destruction | — | — | DRY | — | no fold |
| — | 3 | Vulnerabilities | — | — | DRY — the env is built from a COPY of `os.environ` (MUST-PRESERVE), so `PATH`/`HOME` survive and pytest still resolves; the env var is required to reach BOTH invocations, with the reason stated (a baseline that writes bytecode is what poisons the mutant run) | — | no fold |
| — | 3 | Integration-record | — | — | DRY | — | no fold |
| — | 3 | ACID | — | — | DRY | — | no fold |

**Walk 3 total: 0 findings — DRY.**

---

## Walk 4 — five-lens sequential walk (confirming pass, real)

| id | walk | lens | sub_question | origin | finding | pre_fold_text | resolution |
|---|---|---|---|---|---|---|---|
| — | 4 | Weak spots | — | — | DRY — the five preserved-property probes have a named home in the dev log (Task E) rather than being asserted into the air | — | no fold |
| — | 4 | Destruction | — | — | DRY | — | no fold |
| — | 4 | Vulnerabilities | — | — | DRY — QA may not edit the target, its tests, or the manifest; the manifest is outside this plan's Scope as well, so the prohibition is belt-and-braces rather than the only guard | — | no fold |
| — | 4 | Integration-record | — | — | DRY — open_forks carries the self-application mutant, the CONTROL mutant, the pre-baseline bytecode assertion, and thread 24's plan_lint promote step | — | no fold |
| — | 4 | ACID | — | — | DRY | — | no fold |

**Walk 4 total: 0 findings — DRY. Two consecutive dry walks — BAR MET.**

---

## Conformance (§5) — recorded at the freeze from ACTUAL runs

- **Root-cause verification (2026-08-27), the reason this plan's fix differs from the 574 verdict's prescription:** `sys.pycache_prefix` → `/Users/marklehn/Library/Caches/com.apple.python`; `find . -name __pycache__` → nothing after a baseline run; the mirrored `.pyc` present at the absolute-path mirror; deleting it makes the mutated test fail. `PYTHONDONTWRITEBYTECODE=1` verified in both directions (unmutated pass, mutated fail).
- **Pins verified live at authoring:** `_run_pytest(` occurrences → 3; full suite → 1620 collected; `tests/test_mutation_check.py` → 1 failed, 7 passed, 3/3 deterministic.
- **Fold verification (`/usr/bin/grep -cF` on the draft):** w1-1 landed ×1 (`legitimate precisely so long as it is labelled`), superseded ×0 (`no**: that raises NameError`); w1-2 landed ×1 (`test_consecutive_same_length_mutants_are_both_killed`), superseded ×0 (`test_baseline_does_not_poison`); w2-1 landed ×1 (`1623 collected, 0 failed`).
- **Structure:** `grep -cE '^## STEP '` → 2.
- **run_check runs at the freeze (2026-08-27, all branched-on; lint at the DEPOSIT path via a `lintmirror-` copy):** `lint` -> `VERDICT=PASS — exit 0`; `cycle` -> `VERDICT=PASS — BAR_MET`; `register` -> FAILED TWICE before passing, and the two failures had DIFFERENT causes worth recording because I mis-diagnosed the second: (1) row w1-1's `pre_fold_text` carries a genuine `...` that is part of the pre-image bytes — the sanctioned fix is the `verbatim-ellipsis` marker in the resolution cell (`walk_register_lint.py:181-191`), not rewriting the quote; (2) row w2-1 had NO ellipsis at all — its escaped table pipes (`\|`) inside the cell broke column alignment so the checker read a different column entirely. I removed ellipses first and re-ran expecting green; it failed again, which is what sent me to READ the detector (`TRUNCATION_RE = r"\.\.\.|…"` plus the marker escape) instead of guessing a third time. Fixed by transcribing the source row's pipes as the word SLASH.
- **fold_check (EARNED, not authored):** v0 reconstructed by reversing the w1-2 test-differentiation fold (anchor asserted x1), baselined, then the frozen draft diffed against it -> `FOLD-CHECK CLEAN: machine-readable state unchanged (7 signals held)`.

## Closing

**Walks 1-4, yields 2 → 1 → 0 → 0. BAR MET on walk 4. Cold panel not convened (T1, one subprocess-env change to a tool that never writes the live tree). Close is MANUAL (CEO-lane verdicts; auto_close false). The walk that earned its keep was w1-1: QA Item 4 had been written as a transcript of the Planner's own reasoning — proposing a mutation, rejecting it mid-sentence, trying another, rejecting that too — leaving the agent to re-derive a conclusion from an argument containing two explicitly wrong branches. A plan step is an instruction, not a record of how the instruction was reached; the reasoning belongs in the register, which is where it now lives.**
