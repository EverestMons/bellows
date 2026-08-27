# bellows — executable: `tools/mutation_check.py` — make "would this suite catch the bug?" a binary result (thread 24, first of the mechanization arc)

**Date:** 2026-08-27 | **Project:** bellows | **Tier:** Small | **Dispatch Mode:** bellows | **cycle_tier:** T1 | **Test Scope:** targeted (the runner's own tests) + full suite at QA | **Execution:** Step 1 (DEV) → Step 2 (QA) | **qa_steps:** 2 | **pause_for_verdict:** always

**auto_close:** false

**Depends on:** tuyere thread 24 (CEO-approved 2026-08-27, sequenced FIRST of the mechanization arc because it audits the others); memory `mechanize-to-reserve-reasoning` (CEO directive: every check that CAN be arithmetic becomes code); LESSONS.md 2026-08-27 "a test written by the author of the code inherits the author's model"; exec-572 (HALTED — the false-premise guard that passed 8 dedicated tests) and exec-573 (its corrected replacement, whose state-space suite this runner will audit).

## Why this exists

A suite's real claim is "this would catch the bug." Today that is answerable only by reasoning — and at exec-572 my reasoning was the thing that was wrong: eight dedicated tests passed while the guard silently swallowed genuine pauses. Mutation converts the claim to arithmetic: reintroduce a defect, require the suite to go RED, and a surviving mutant is a binary FAIL that needs no interpretation.

This runner is deliberately SMALL — a manifest plus a sandboxed apply-and-run loop. No `mutmut`/`cosmic-ray` scale infrastructure, no automatic mutant generation. The mutants are hand-named and earned from real defects, so each one is a claim about a failure mode we have actually suffered.

## ⚠️ The two design points that decide whether this tool is honest

1. **A non-zero pytest exit is NOT proof the mutant was killed.** pytest exits 5 on "no tests collected", 4 on usage error, 2 on interrupt, 3 on internal error. A wrong selector therefore yields non-zero and would be scored KILLED — the tool would manufacture exactly the false confidence it exists to destroy. **Only exit code 1 (tests ran and failed) counts as KILLED.** Every other non-zero code is `ERROR` and fails the run distinctly.
2. **A mutant result is meaningless unless the selector PASSES on unmutated code.** Each mutant gets a BASELINE run on the pristine sandbox first, required to exit 0. A selector that is already failing (or already empty) cannot demonstrate anything. This is the positive control the negative-probe law requires.

## What this plan does NOT do

- **Never mutates the live tree.** All work happens in a `git archive HEAD` extraction under `mktemp -d`. The verification-inside-its-own-blast-radius law: a runner that edits the real file and dies leaves the repo mutated.
- **No plan_lint rule yet, no CI wiring, no daemon integration.** Those come after this proves out on real mutants (thread 24's promote step, and thread 23's lint clause).
- **No automatic mutant generation.** Manifest-driven only.
- **No memory writes** (sandbox-denied to agents; the Planner records results at close).

## Numbers discipline

⚠️ **Measured 2026-08-27 by the Planner; RE-DERIVE each pre-flight — yours supersede and you say so; mismatch on a load-bearing pin → HALT.**

| id | pin | value | anchor/probe |
|---|---|---|---|
| C1 | pytest exit-code semantics | 0=all passed, 1=tests failed, 2=interrupted, 3=internal error, 4=usage error, **5=no tests collected**. Only 1 means KILLED | `python3 -m pytest --help`; verify 5 empirically with a nonsense `-k` selector |
| C2 | sandbox mechanism | `git archive HEAD \| tar -x -C <tmp>` reproduces the tracked tree with no `.git`: **4719 files, ~30.2 MB** — extract ONCE, mutate per-mutant, restore between | `git archive HEAD \| tar -t \| wc -l`; `git archive HEAD \| wc -c` |
| C3 | test import path | `tests/test_gate_watcher.py:10-14` does `sys.path.insert(0, TOOLS_DIR.parent)` then `from tools.gate_watcher import …` — so a sandbox run resolves the SANDBOX copy when pytest's rootdir is the sandbox | read the file head |
| C4 | M1 anchor (exact, 3 lines, indented 16 then 24) | `                live = [h for h in hits if\n                        _step_of(h) is None or\n                        not _verdict_issued(res, plan_id, _step_of(h))]` at `tools/gate_watcher.py:96-98` | read `:86-100` |
| C5 | M2 anchor | `        if state not in TERMINAL:` at `tools/gate_watcher.py:86` | read the file |
| C6 | baselines | `tests/test_gate_watcher.py` collects **46**; full suite **1611 passed + 1 skipped = 1612** | `pytest … --collect-only`; the 573 evidence `.txt` |

## MUST-PRESERVE

- ⚠️ **`/usr/bin/grep` for ALL probes (`-F` unless a regex is stated); zero-match exits 1 — never `&&`-chain a probe.**
- ⚠️ **Anchor discipline:** every substitution asserts its anchor occurs **exactly once** in the sandbox target before writing, and asserts the replacement text is PRESENT after writing. A silently-unmatched anchor produces an unmutated run that scores SURVIVED — a false alarm — or worse, scores KILLED off an unrelated failure.
- ⚠️ **The live tree is never written.** At the end the runner asserts the live target's sha256 is unchanged from the value it read at start, and says so on stdout. This is a positive control, not a comment.
- ⚠️ **Restore between mutants:** the sandbox target is restored from a pristine in-memory copy before each mutant, so mutants cannot compound.
- ⚠️ **Worktree dispatch; every claim cites file:line; absence claims carry positive controls; EVERY DATE IS A FIXED LITERAL.**

## STEP 1 — DEV (the runner + manifest + its own tests)

> **Task A — worktree discipline.** `cd "$(git rev-parse --show-toplevel)" && test -d tools && echo TREE_OK` — HALT unless TREE_OK. Resume probe: `test -f tools/mutation_check.py && echo 1 || echo 0` → 0 = full run; 1 = resume at Task D.
>
> **Task B — verify C1 EMPIRICALLY before building on it** (the pin is a claim): run `python3 -m pytest tests/test_gate_watcher.py -k "zzz_no_such_test" -q; echo "exit=$?"` → expect `exit=5` with "no tests ran"; and `python3 -m pytest tests/test_gate_watcher.py -q; echo "exit=$?"` → `exit=0`. Paste both into the dev log. If 5 is not the empty-selection code on this pytest build, STOP and report — the runner's core discrimination depends on it.
>
> **Task C — write `tools/mutation_check.py`:**
> - CLI: `mutation_check.py <manifest.json> [--repo-root PATH] [--keep-sandbox]`. Exit **0** = every mutant KILLED; **1** = at least one SURVIVED or ERRORed; **2** = usage/manifest/anchor failure.
> - Manifest schema (JSON): `{"target": "<repo-relative .py>", "mutants": [{"name": str, "why": str, "anchor": str, "replacement": str, "expect_fail": str}]}` where `expect_fail` is a pytest selector (node id or `-k` expression — state which form in the docstring and use node ids).
> - ⚠️ **`git archive HEAD` archives the last COMMIT, not the working tree — so the tool audits COMMITTED code.** Uncommitted edits to the target are invisible, and a clean mutation report about code you are not looking at is exactly the false confidence this tool exists to remove. Before extracting, run `git status --porcelain -- <target>`; if it is non-empty, print `WARNING: target has uncommitted changes — this run audits HEAD, not your working tree` and carry that warning into the summary line. State the HEAD sha in the output so every report says which code it judged.
> - Flow: read the live target's sha256; `git archive HEAD | tar -x -C <mktemp -d>` (wrap the whole run in `try/finally` so the sandbox is removed even on an exception); keep a pristine copy of the sandbox target in memory; then per mutant: (1) restore the pristine target; (2) **BASELINE** — run the selector in the sandbox, require exit **0**, else report `ERROR: baseline not green` and continue to the next mutant; (3) assert `sandbox_text.count(anchor) == 1`, else `ERROR: anchor matched N times`; (4) write the substitution and assert the replacement is present; (5) run the selector again; (6) score: exit **1** → `KILLED`; exit **0** → `SURVIVED`; anything else → `ERROR: pytest exit N`.
> - Run tests via `subprocess.run([sys.executable, "-m", "pytest", <selector>, "-q"], cwd=<sandbox>)` with a timeout (default 300s; a timeout is `ERROR`, never `KILLED`).
> - Final: re-read the live target's sha256, assert unchanged, print `LIVE-TREE UNCHANGED: <sha12>`; remove the sandbox unless `--keep-sandbox`.
> - Output: one line per mutant — `MUTANT <name>: KILLED|SURVIVED|ERROR — <detail>` — then a summary `MUTATION: <k> killed, <s> survived, <e> error` and, on any survivor, an explicit line naming what that means: `SURVIVED means the suite does not discriminate this defect — the tests are decorative for it.`
>
> **Task D — write `knowledge/mutants/gate_watcher.json`** with both mutants earned from real defects (use C4/C5 anchors verbatim; `expect_fail` selectors must name the state-space class):
> - **M1 `suppress-all-pending`** — *why:* "reproduces the exec-572 failure MODE: a genuine unresolved pause suppressed. If this survives, the state-space suite does not actually discriminate the defect 572 shipped." Replacement: `                live = []`. `expect_fail`: `tests/test_gate_watcher.py::TestPauseStateSpace`.
> - **M2 `phantom-arm-detection`** — *why:* "reproduces the exec-571 defect: pause detection keyed on plans.lifecycle_state's phantom 'awaiting_verdict' arm, which no writer ever sets, so a pause is never seen." Replacement: `        if state == "awaiting_verdict":`. `expect_fail`: `tests/test_gate_watcher.py::TestPauseStateSpace`.
>
> **Task E — write `tests/test_mutation_check.py`** (the runner's OWN tests — it is a checker, so it gets the treatment it enforces). Use tiny synthetic targets + synthetic test files in `tmp_path`, never the real repo:
> 1. `test_killed_when_mutant_breaks_the_test` — selector passes pristine, fails mutated → `KILLED`, overall exit 0.
> 2. `test_survived_when_suite_cannot_see_the_change` — a mutation the synthetic test does not observe → `SURVIVED`, overall exit 1.
> 3. **`test_empty_selector_is_error_not_killed`** — the tool's own trap: a selector matching NOTHING (pytest exit 5) must score `ERROR`, **never** `KILLED`. ⚠️ This is the single most important test in the file: without it the runner manufactures false confidence.
> 4. `test_baseline_failure_is_error_not_killed` — a selector already RED on pristine code scores `ERROR: baseline not green`, never `KILLED`.
> 5. `test_anchor_not_unique_is_error` — anchor occurring 0 times, and again 2 times → `ERROR` both ways, exit 2, and no test run attempted.
> 6. `test_live_tree_untouched` — after a full run, the live target's sha256 is unchanged and `LIVE-TREE UNCHANGED:` appears in stdout.
> 7. `test_mutants_do_not_compound` — two mutants whose anchors overlap in effect: assert the second runs against a restored pristine target (its baseline is green).
> 8. `test_timeout_is_error_not_killed` — a synthetic test that sleeps past a 1s timeout scores `ERROR`.
> **Targeted run:** `python3 -m pytest tests/test_mutation_check.py -q` → report the collected count from `--collect-only` first, then the pass count. DEV runs NO full suite.
>
> **Task F — dev log** `knowledge/dev-logs/mutation-runner-dev-2026-08-27.md`: the C1 empirical exit-code evidence pasted raw, each pin re-derivation (C1-C6, yours vs the table, say "supersedes" where they differ), the targeted-test tail.
>
> **Task G — commit** (worktree; message `[<id>] mutation-runner: sandboxed mutant apply-and-run; exit-1-only KILLED; baseline control`): `cd "$(git rev-parse --show-toplevel)" && git add tools/mutation_check.py knowledge/mutants/gate_watcher.json tests/test_mutation_check.py knowledge/dev-logs/mutation-runner-dev-2026-08-27.md && git commit`. Verify `git show --stat HEAD | cat` lists exactly those 4 files.
>
> **Deposits:**
> - `tools/mutation_check.py`
> - `knowledge/mutants/gate_watcher.json`
> - `tests/test_mutation_check.py`
> - `knowledge/dev-logs/mutation-runner-dev-2026-08-27.md`
>
> **Scope:**
> - `tools/mutation_check.py`
> - `knowledge/mutants/gate_watcher.json`
> - `tests/test_mutation_check.py`
> - `knowledge/dev-logs/mutation-runner-dev-2026-08-27.md`

## STEP 2 — QA (FULL suite + THE REAL VERDICT: run the mutants against exec-573's suite)

> **Item 1 — full suite.** `cd "$(git rev-parse --show-toplevel)"`; `python3 -m pytest tests/ --tb=short -q 2>&1 | cat | tee knowledge/qa/evidence/mutation-runner-2026-08-27/pytest_full.txt` — 0 failed; record the count and its derivation from the C6 baseline (1612).
> **Item 2 — THE HEADLINE RESULT, raw tail pasted to `probes-raw.txt`:** `python3 tools/mutation_check.py knowledge/mutants/gate_watcher.json 2>&1 | cat; echo "exit=$?"`.
> - Report the outcome **exactly as measured — this plan does NOT require the mutants to be killed.** A `SURVIVED` is a genuine, valuable finding: it would mean exec-573's state-space suite does not discriminate a defect we actually shipped, and the honest act is to report it, not to adjust anything to make it green.
> - ⚠️ **Do NOT edit `tests/test_gate_watcher.py` or `tools/gate_watcher.py` in this step under any circumstance** — they are outside this plan's Scope, and "fixing" a survivor here would destroy the measurement. A survivor is reported and routed, never patched.
> - ⚠️ **Nor may you edit `knowledge/mutants/gate_watcher.json` in this step** — it IS in the plan's Scope, so the prohibition has to be stated rather than relied on. Retuning an anchor, a replacement or a selector until the result turns green is the same corruption through a different door, and it is the more tempting one because it looks like fixing the tool. If a mutant ERRORs on a bad anchor, report the ERROR; the manifest is corrected by a follow-up plan, not inside the measurement.
> - Assert `LIVE-TREE UNCHANGED:` appears in the output and independently verify it: `shasum -a 256 tools/gate_watcher.py` before and after the run must match (paste both).
> **Item 3 — the empty-selector trap, proven live:** copy the manifest to a temp file with M1's `expect_fail` replaced by a nonsense node id, run the tool on it → the mutant must score `ERROR`, NOT `KILLED`, and the run must exit non-zero. Paste raw. This proves on the real tool what test 3 proves synthetically.
> **Item 4 — hygiene + receipt** `knowledge/qa/evidence/mutation-runner-2026-08-27/qa-receipt.md`: numstat vs the DEV commit (4 files); toplevel; reflog `-n 4` → 0 amends; per-item table; **the mutation result stated plainly in a line of its own, killed or survived**; then the Rule 20 block INSIDE a "Verification"-headed section (the 556 placement law).
> **Item 5 — commit the evidence** (message `[<id>] mutation-runner: QA — full suite + first mutant run against the 573 suite`): `git add knowledge/qa/evidence/mutation-runner-2026-08-27/ && git commit`; verify exactly 3 files.
>
> ⚠️ **Gate note:** pytest summary named above — the gate parses; no benign override pre-declared.
>
> **Deposits:**
> - `knowledge/qa/evidence/mutation-runner-2026-08-27/pytest_full.txt`
> - `knowledge/qa/evidence/mutation-runner-2026-08-27/probes-raw.txt`
> - `knowledge/qa/evidence/mutation-runner-2026-08-27/qa-receipt.md`
>
> **Scope:**
> - `knowledge/qa/evidence/mutation-runner-2026-08-27/pytest_full.txt`
> - `knowledge/qa/evidence/mutation-runner-2026-08-27/probes-raw.txt`
> - `knowledge/qa/evidence/mutation-runner-2026-08-27/qa-receipt.md`

Rule 20 banner (byte-exact, inside the QA receipt's VERIFICATION section):

```
============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
```

## Drafting Cycle

**Tier:** T1 — one new read-only-to-the-live-tree tool, a data manifest, and its own tests; no existing behavior changes.

**Walk register:** `bellows/knowledge/research/walk-register-mutation-runner-2026-08-27.md`

**Walks:** walk 0 pinned; **walks 1-3 complete**, genuine sequential five-lens passes — see the register.
**Direction verdict (after walk 1): PROCEED** — the manifest-plus-sandbox shape held.
- Weak spots:          w1 1 folded (git archive audits HEAD, not the working tree — dirty-target warning + HEAD sha in the report); w2 dry; w3 dry
- Destruction:         w1 1 folded (try/finally so the sandbox is removed on an exception); w2 dry; w3 dry
- Vulnerabilities:     w1 1 folded (⚠️ the QA step was barred from editing the target and its tests, but NOT the manifest — which is in scope, making "retune until green" the easier corruption); w2 dry (both mutant anchors verified to match exactly once against the shipped file); w3 dry
- Integration-record:  w1 dry; w2 dry; w3 dry
- ACID:                w1 dry; w2 dry; w3 dry
**Cold panel: NOT convened, decided with reasoning** — T1 additive tooling that never writes the live tree; the 563/569/571/573 precedent.
**Conformance (§5):** recorded at the freeze from actual runs — see the register's conformance block.
**Closing:** **walk 3 confirmed walk 2's dry pass — all five lenses dry twice; BAR MET.** Instruction series **3 → 0 → 0**. Close is MANUAL (CEO-lane verdicts; auto_close false).

## Cycle Manifest
tier: T1
target: bellows/tools/mutation_check.py
class: shop-infra
reads: /Users/marklehn/Developer/GitHub/bellows/tools/gate_watcher.py, /Users/marklehn/Developer/GitHub/bellows/tests/test_gate_watcher.py, /Users/marklehn/Developer/GitHub/bellows/knowledge/decisions/Done/executable-573.md, /Users/marklehn/Developer/GitHub/bellows/knowledge/decisions/halted-executable-572.md
writes: tools/mutation_check.py, knowledge/mutants/gate_watcher.json, tests/test_mutation_check.py, knowledge/dev-logs/mutation-runner-dev-2026-08-27.md, knowledge/qa/evidence/mutation-runner-2026-08-27/pytest_full.txt, knowledge/qa/evidence/mutation-runner-2026-08-27/probes-raw.txt, knowledge/qa/evidence/mutation-runner-2026-08-27/qa-receipt.md
open_forks: a CONTROL mutant (a semantically-neutral edit that SHOULD survive, catching an over-sensitive/brittle suite) — deferred, not decided; the plan_lint clause requiring a mutant for detector-class plans (thread 24 promote step, pairs with thread 23); whether mutants belong per-target or per-plan; SELF-APPLICATION (elegant, deferred to a follow-up) — a `knowledge/mutants/mutation_check.json` whose mutant makes the runner score pytest's exit 5 as KILLED, with `expect_fail` naming `test_empty_selector_is_error_not_killed`: the runner would then prove mechanically that its own most important guard is not decorative. The regress stops there and the plan does not pretend otherwise — something must be trusted at the bottom, and it should be the smallest, most-examined thing.
walks: 3
yields: 3, 0, 0
validation: cycle_check=BAR_MET, plan_lint=0_FAIL, fold_check=CLEAN_x1
coherence: N/A
