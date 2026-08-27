# bellows — executable: mutation runner — isolate bytecode caching so a SAME-BYTE-LENGTH mutant cannot survive (corrected re-deposit after the 574 halt)

**Date:** 2026-08-27 | **Project:** bellows | **Tier:** Small | **Dispatch Mode:** bellows | **cycle_tier:** T1 | **Test Scope:** targeted (the runner's own tests) + full suite at QA | **Execution:** Step 1 (DEV) → Step 2 (QA) | **qa_steps:** 2 | **pause_for_verdict:** always

**auto_close:** false

**Depends on:** the exec-574 HALT (`knowledge/decisions/halted-executable-574.md` — its own test suite refused to certify it; this is the corrected re-deposit under the stable slug per the no-redo verdict grammar); tuyere thread 24; memory `mechanize-to-reserve-reasoning`.

## Why this exists

Exec-574 built the runner correctly in every design respect the plan named — exit-1-only KILLED, green-baseline control, anchor-count-1, replacement-present-after-write, live-tree sha256 in a `finally` — and then failed its own test suite, deterministically (3/3), on `test_killed_when_mutant_breaks_the_test`.

**Root cause, now COMPLETELY diagnosed (the 574 verdict named the mechanism but could not explain one arm; that arm is resolved here):** the mutant run re-imports the target while a stale `.pyc` is still valid. CPython invalidates bytecode by `(source mtime, source size)`. The synthetic mutant swaps `return a + b` for `return a - b` — **identical byte length** — so when both writes land in the same mtime second the cached bytecode stays valid and the mutant run executes BASELINE code. The suite passes and the mutant scores SURVIVED.

**Why "just clear `__pycache__`" is NOT the fix, measured on this machine:** `sys.pycache_prefix` is set to `/Users/marklehn/Library/Caches/com.apple.python` (the Apple system-Python default), so bytecode is redirected OUT of the source tree into a mirror of the absolute source path. No `__pycache__` directory is ever created next to the source; clearing it removes nothing, which is exactly what was observed. Deleting the redirected `.pyc` did make the mutated test fail correctly — confirming the mechanism — but **the cache LOCATION is environment-dependent and no clearing strategy is portable.**

**The portable fix, verified in BOTH directions before this plan was written:** `PYTHONDONTWRITEBYTECODE=1` in the pytest subprocess environment. With it, the unmutated target passes and the mutated target fails, correctly. It is independent of `pycache_prefix`, of the platform, and of mtime granularity.

⚠️ **Severity, priced honestly:** the failure direction is FALSE SURVIVED — a false alarm, never a false KILLED, so the tool could not have manufactured confidence. But same-byte-length edits are not exotic (flip a comparison operator, swap a boolean, change one digit), and a mutation runner that silently misses them is not fit for the job it exists to do.

## What this plan does NOT do

- **No redesign.** The 574 implementation is kept; this plan changes the subprocess environment, adds one guard, and adds tests. Do not restructure `mutation_check.py`.
- **Does NOT rely on deleting `__pycache__`** — see above; that arm is measured useless in this environment. (Belt-and-braces removal is permitted but must never be the ONLY isolation.)
- **No plan_lint rule, no CI wiring, no daemon integration** (thread 24's promote step).
- **No memory writes** (sandbox-denied to agents; the Planner records at close).

## Numbers discipline

⚠️ **Measured 2026-08-27 by the Planner; RE-DERIVE each pre-flight — yours supersede and you say so; mismatch on a load-bearing pin → HALT.**

| id | pin | value | anchor/probe |
|---|---|---|---|
| D1 | the failing test, deterministic | `python3 -m pytest tests/test_mutation_check.py -q` → **1 failed, 7 passed**; the failure is `test_killed_when_mutant_breaks_the_test`, reproduced 3/3 | run it |
| D2 | the cache is REDIRECTED here | `python3 -c "import sys; print(sys.pycache_prefix)"` → `/Users/marklehn/Library/Caches/com.apple.python`; `sys.dont_write_bytecode` → `False`; no `PYTHON*` env vars set | run it |
| D3 | the stale artifact's real location | `~/Library/Caches/com.apple.python/<ABSOLUTE-SOURCE-DIR>/target.cpython-39.pyc` — measured present after a baseline run while `find . -name __pycache__` returns NOTHING | `ls` the mirrored path |
| D4 | the fix works BOTH ways | with `PYTHONDONTWRITEBYTECODE=1`: unmutated → `1 passed`; mutated (same byte length) → `1 failed` | the standalone scratch repro |
| D5 | the seam | `tools/mutation_check.py:42-53` `_run_pytest` — `subprocess.run([sys.executable, "-m", "pytest", selector, "-q"], cwd=cwd, timeout=timeout, capture_output=True, text=True)`; **no `env=` argument today**, so the child inherits the parent environment | read the file |
| D6 | baselines, and ⚠️ **the full suite is CURRENTLY RED** | `tests/test_mutation_check.py` collects **8** (1 of them FAILING — D1); `tests/test_gate_watcher.py` collects **46**; full suite **1620 collected** — 574's DEV commit landed before its halt, so its 8 runner tests are in tree. Expected AFTER this plan: 1620 + 3 new = **1623 collected, 0 failed** (the D1 failure turns green via the Task-C fix). QA Item 1 gates on 0 failed, so this derivation is load-bearing — re-derive and show your arithmetic | `pytest tests/ -q --collect-only \| tail -1` |

## MUST-PRESERVE

- ⚠️ **`/usr/bin/grep` for ALL probes (`-F` unless a regex is stated); zero-match exits 1 — never `&&`-chain a probe.**
- ⚠️ **Every existing design property of the runner stays intact:** exit-1-only KILLED (`:193-205`), green-baseline control (`:167-177`), anchor-count==1 (`:160`), replacement-present-after-write (`:183-188`), live-tree sha256 in `finally`. Re-assert each with a probe after your edit.
- ⚠️ **`PYTHONDONTWRITEBYTECODE=1` must reach BOTH pytest invocations** — the baseline run and the mutant run — because a baseline that writes a `.pyc` is precisely what poisons the mutant run. Setting it for one and not the other reproduces the bug.
- ⚠️ **Build the child env from a COPY of `os.environ`** (`env = dict(os.environ); env["PYTHONDONTWRITEBYTECODE"] = "1"`), never a bare dict — a stripped environment loses `PATH`/`HOME` and pytest may not resolve.
- ⚠️ **Worktree dispatch; every claim cites file:line; absence claims carry positive controls; EVERY DATE IS A FIXED LITERAL.**

## STEP 1 — DEV (the isolation fix + the same-length regression test)

> **Task A — worktree discipline.** `cd "$(git rev-parse --show-toplevel)" && test -f tools/mutation_check.py && echo TREE_OK` — HALT unless TREE_OK. Resume probe: `/usr/bin/grep -cF "PYTHONDONTWRITEBYTECODE" tools/mutation_check.py; true` → 0 = full run; ≥1 = resume at Task D.
>
> **Task B — REPRODUCE D1 BEFORE FIXING** (a fix whose defect you have not observed is a guess): run `python3 -m pytest tests/test_mutation_check.py -q 2>&1 | tail -3` and paste it raw into the dev log; it must show `1 failed, 7 passed` with `test_killed_when_mutant_breaks_the_test` named. If the suite is GREEN on your tree, STOP and report — the premise of this plan does not hold and the cause is environment-dependent in a way we must understand before proceeding.
>
> **Task C — the fix in `_run_pytest`** (`tools/mutation_check.py:42-53`, anchored, asserted unique):
> - Build `env = dict(os.environ)`; set `env["PYTHONDONTWRITEBYTECODE"] = "1"`; pass `env=env` to `subprocess.run`. Add `import os` if absent.
> - Extend the docstring with WHY, so the next reader cannot "tidy" it away: bytecode is invalidated by `(mtime, size)`, so a same-byte-length mutation written within the same mtime second leaves the cached `.pyc` valid and the mutant run executes baseline code; and the cache LOCATION is environment-dependent (`sys.pycache_prefix` redirects it entirely out of the tree on this machine), so clearing `__pycache__` is not a portable substitute.
> - The single `_run_pytest` helper serves BOTH the baseline and mutant calls — verify that by probe (`/usr/bin/grep -cF "_run_pytest(" tools/mutation_check.py` → expect 3: one definition, two call sites; re-derive and state yours).
>
> **Task D — tests in `tests/test_mutation_check.py`** (keep all 8 existing; do not weaken any assertion):
> 1. **`test_same_byte_length_mutation_is_killed`** — the regression test for THIS defect, and the one that must be impossible to satisfy by accident. Synthetic repo, mutation `return a + b` → `return a - b` (**assert in the test body that `len(anchor) == len(replacement)`**, so the property under test cannot silently drift), run the checker → `KILLED`, exit 0. ⚠️ Without the length assertion a later edit could change the strings and the test would keep passing while no longer testing the condition.
> 2. **`test_bytecode_isolation_env_is_set`** — structural: read `tools/mutation_check.py` source and assert `PYTHONDONTWRITEBYTECODE` appears AND that `_run_pytest` passes an `env=` argument. Guards against the isolation being removed by a later tidy.
> 3. **`test_consecutive_same_length_mutants_are_both_killed`** — a genuinely DISTINCT property from test 1, not a rename of it. Test 1 proves ONE same-length mutant is killed; this proves the SECOND one in the same run is too. Manifest with two mutants on the same target, each an equal-length change to a different line, each with its own `expect_fail`; assert BOTH score `KILLED`. The failure it guards is cache carry-over ACROSS mutants: mutant 1's run leaves bytecode that mutant 2's baseline-then-mutant sequence could import, which the single-mutant test cannot see. ⚠️ If you cannot construct two independent equal-length mutations on one synthetic target, say so and drop the test rather than weakening it into a copy of test 1.
> **Targeted run:** `python3 -m pytest tests/test_mutation_check.py -q` → **11 passed, 0 failed** (8 existing now green + 3 new; re-derive the count with `--collect-only` first and state it). ⚠️ The previously-failing `test_killed_when_mutant_breaks_the_test` must now PASS — name it explicitly in the dev log as the before/after.
>
> **Task E — dev log** `knowledge/dev-logs/mutation-runner-fix-dev-2026-08-27.md`: the Task-B raw before-state, each pin re-derivation (D1-D6, yours vs the table, say "supersedes" where they differ), the after-state raw tail, and the five preserved-property probes.
>
> **Task F — commit** (worktree; message `[<id>] mutation-runner-fix: PYTHONDONTWRITEBYTECODE isolation; same-length mutant regression test`): `cd "$(git rev-parse --show-toplevel)" && git add tools/mutation_check.py tests/test_mutation_check.py knowledge/dev-logs/mutation-runner-fix-dev-2026-08-27.md && git commit`. Verify `git show --stat HEAD | cat` lists exactly those 3 files.
>
> **Deposits:**
> - `tools/mutation_check.py`
> - `tests/test_mutation_check.py`
> - `knowledge/dev-logs/mutation-runner-fix-dev-2026-08-27.md`
>
> **Scope:**
> - `tools/mutation_check.py`
> - `tests/test_mutation_check.py`
> - `knowledge/dev-logs/mutation-runner-fix-dev-2026-08-27.md`

## STEP 2 — QA (FULL suite + the real mutants against exec-573's suite)

> **Item 1 — full suite.** `cd "$(git rev-parse --show-toplevel)"`; `python3 -m pytest tests/ --tb=short -q 2>&1 | cat | tee knowledge/qa/evidence/mutation-runner-fix-2026-08-27/pytest_full.txt` — 0 failed; record the count and derive it from the D6 baseline.
> **Item 2 — THE HEADLINE RESULT, raw tail to `probes-raw.txt`:** `python3 tools/mutation_check.py knowledge/mutants/gate_watcher.json 2>&1 | cat; echo "exit=$?"`.
> - Report the outcome **exactly as measured. This plan does NOT require the mutants to be killed.** A `SURVIVED` is a genuine and valuable finding: it would mean exec-573's state-space suite does not discriminate a defect we actually shipped, and the honest act is to report it and let the Planner route it.
> - ⚠️ **Do NOT edit `tools/gate_watcher.py`, `tests/test_gate_watcher.py`, or `knowledge/mutants/gate_watcher.json` in this step under any circumstance.** The first two are outside Scope; the manifest is the INSTRUMENT, and retuning an anchor or selector until the result turns green is the same corruption through an easier door because it looks like fixing the tool. A survivor is reported, never patched.
> - Assert `LIVE-TREE UNCHANGED:` appears, and verify it INDEPENDENTLY: `shasum -a 256 tools/gate_watcher.py` before and after, both pasted.
> **Item 3 — the empty-selector trap, proven live on the real tool:** copy the manifest to a temp file with M1's `expect_fail` replaced by a nonsense node id; run the tool on it → that mutant must score `ERROR`, **not** `KILLED`, and the run must exit non-zero. Paste raw.
> **Item 4 — the same-length trap, proven end-to-end on the real tool binary, against a SYNTHETIC target.** Build a temp git repo: `target.py` containing `def add(a, b):` / `    return a + b`, and `tests/test_target.py` importing it and asserting `add(1, 2) == 3`; commit it. Write a manifest mutating `return a + b` to `return a - b` (equal length, semantically real) with `expect_fail` naming that test. Run `python3 tools/mutation_check.py <that manifest> --repo-root <that repo>` → must score **KILLED**, exit 0. Paste the raw output, and paste the byte length of both strings to show they are equal.
> ⚠️ **The target here is synthetic, and the receipt must label it so rather than presenting it as a live-target probe.** The reason is a property of the real target, not a shortcut: `tools/gate_watcher.py` offers no equal-length mutation that is both semantically meaningful and non-crashing — an identifier swap raises `NameError` (which the suite would catch for the wrong reason, a false KILL) and the `TERMINAL` inversion changes byte length. Verifying this property therefore requires a constructed target, which is legitimate precisely so long as it is labelled.
> **Item 5 — hygiene + receipt** `knowledge/qa/evidence/mutation-runner-fix-2026-08-27/qa-receipt.md`: numstat vs the DEV commit (3 files); toplevel; reflog `-n 4` → 0 amends; per-item table; **the mutation result on the real manifest stated plainly in its own line, killed or survived**; then the Rule 20 block INSIDE a "Verification"-headed section (the 556 placement law).
> **Item 6 — commit the evidence** (message `[<id>] mutation-runner-fix: QA — full suite + first real mutant run`): `git add knowledge/qa/evidence/mutation-runner-fix-2026-08-27/ && git commit`; verify exactly 3 files.
>
> ⚠️ **Gate note:** pytest summary named above — the gate parses; no benign override pre-declared.
>
> **Deposits:**
> - `knowledge/qa/evidence/mutation-runner-fix-2026-08-27/pytest_full.txt`
> - `knowledge/qa/evidence/mutation-runner-fix-2026-08-27/probes-raw.txt`
> - `knowledge/qa/evidence/mutation-runner-fix-2026-08-27/qa-receipt.md`
>
> **Scope:**
> - `knowledge/qa/evidence/mutation-runner-fix-2026-08-27/pytest_full.txt`
> - `knowledge/qa/evidence/mutation-runner-fix-2026-08-27/probes-raw.txt`
> - `knowledge/qa/evidence/mutation-runner-fix-2026-08-27/qa-receipt.md`

Rule 20 banner (byte-exact, inside the QA receipt's VERIFICATION section):

```
============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
```

## Drafting Cycle

**Tier:** T1 — a one-call environment fix plus three tests; no redesign, no behavior change to any scoring arm.

**Walk register:** `bellows/knowledge/research/walk-register-mutation-runner-fix-2026-08-27.md`

**Walks:** walk 0 pinned; **walks 1-4 complete**, genuine sequential five-lens passes — see the register.
**Direction verdict (after walk 1): PROCEED** — the env-isolation fix is the whole change; no redesign warranted.
- Weak spots:          w1 1 folded (QA Item 4 carried the Planner's own deliberation instead of an instruction); w2 1 folded (D6 did not say the suite is CURRENTLY RED, and QA Item 1 gates on 0 failed); w3 dry; w4 dry
- Destruction:         w1 dry; w2 dry; w3 dry; w4 dry
- Vulnerabilities:     w1 1 folded (test 3 was a rename of test 1 dressed as a distinct property); w2 dry; w3 dry; w4 dry
- Integration-record:  w1 dry; w2 dry; w3 dry; w4 dry
- ACID:                w1 dry; w2 dry; w3 dry; w4 dry
**Cold panel: NOT convened, decided with reasoning** — T1, one subprocess-env change to a tool that never writes the live tree.
**Conformance (§5):** recorded at the freeze from actual runs — see the register's conformance block.
**Closing:** **walks 3 and 4 both dry — BAR MET.** Instruction series **2 → 1 → 0 → 0**. Close is MANUAL (CEO-lane verdicts; auto_close false).

## Cycle Manifest
tier: T1
target: bellows/tools/mutation_check.py
class: shop-infra
reads: /Users/marklehn/Developer/GitHub/bellows/tools/mutation_check.py, /Users/marklehn/Developer/GitHub/bellows/tests/test_mutation_check.py, /Users/marklehn/Developer/GitHub/bellows/knowledge/mutants/gate_watcher.json, /Users/marklehn/Developer/GitHub/bellows/knowledge/decisions/halted-executable-574.md
writes: tools/mutation_check.py, tests/test_mutation_check.py, knowledge/dev-logs/mutation-runner-fix-dev-2026-08-27.md, knowledge/qa/evidence/mutation-runner-fix-2026-08-27/pytest_full.txt, knowledge/qa/evidence/mutation-runner-fix-2026-08-27/probes-raw.txt, knowledge/qa/evidence/mutation-runner-fix-2026-08-27/qa-receipt.md
open_forks: whether the runner should also assert the sandbox is free of pre-existing bytecode before the baseline (defence in depth, not needed once the env var lands); the self-application mutant (make the runner score exit 5 as KILLED, expect test_empty_selector_is_error_not_killed to fail); the CONTROL mutant that SHOULD survive; thread 24's plan_lint promote step
walks: 4
yields: 2, 1, 0, 0
validation: cycle_check=BAR_MET, plan_lint=0_FAIL, fold_check=CLEAN_x1
coherence: N/A
