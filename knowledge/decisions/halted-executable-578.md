# bellows — executable: mutation runner — force bytecode invalidation by MTIME, making same-length mutants deterministic (corrected re-deposit after the 577 halt)

**Date:** 2026-08-27 | **Project:** bellows | **Tier:** Small | **Dispatch Mode:** bellows | **cycle_tier:** T1 | **Test Scope:** targeted (the runner's own tests) + full suite at QA | **Execution:** Step 1 (DEV) → Step 2 (QA) | **qa_steps:** 2 | **pause_for_verdict:** always

**auto_close:** false

**Depends on:** the exec-577 HALT (`knowledge/decisions/halted-executable-577.md` — the agent halted CORRECTLY on a surviving mutant; the defect was in the Planner's manifest, not the agent's work); exec-575 (the runner); exec-574 (HALTED — the original bytecode defect).

## Why this exists

Exec-577's `drop-bytecode-isolation` mutant returned **KILLED 5/5 on the live checkout and SURVIVED in the agent's worktree, on identical code.** The agent halted rather than retuning, exactly as instructed. The mutant was nondeterministic, and a mutation runner whose mutants are nondeterministic is worse than one with fewer mutants: it manufactures false alarms and trains readers to ignore red.

**Root cause:** `PYTHONDONTWRITEBYTECODE=1` suppresses bytecode WRITING, but the runner inherits its env from the parent (`tools/mutation_check.py:48`), so when the inner mutated runner pops that variable, writing is re-enabled and the outcome then depends on whether the baseline's `.pyc` is still considered valid. CPython validates by `(source mtime, source size)`, and a same-byte-length mutation written within the same mtime second leaves it valid. Whether that happens varies with filesystem timing and with `sys.pycache_prefix`'s absolute-path mirror — which differs between a checkout and a worktree.

**MEASURED, and this is the evidence exec-577 lacked** (synthetic repo, `return a + b` → `return a - b`, five trials each):

| condition | result |
|---|---|
| no mtime bump, path A | **SURVIVED, SURVIVED, SURVIVED, SURVIVED, KILLED** — flaky, caught in the act |
| mtime bump, path A | KILLED ×5 |
| mtime bump, DIFFERENT absolute path B | KILLED ×5 |

**The fix:** after writing each mutant, advance the file's mtime with `os.utime`. That invalidates the cached bytecode by the mechanism CPython actually uses, independent of env vars, `pycache_prefix`, platform, and second-granularity. Verified above WITHOUT the env var set at all — the bump alone is sufficient.

## ⚠️ The fix makes the code MORE robust and LESS mutation-testable — a real tradeoff, stated plainly

After the bump lands there are TWO INDEPENDENTLY SUFFICIENT invalidation mechanisms: the env var suppresses bytecode WRITING, and the mtime bump invalidates any bytecode that does get written. Either alone prevents a stale `.pyc`.

**The consequence follows directly, and it is not what I first assumed.** Removing just one mechanism leaves the other doing the job, so the outcome is unchanged and the mutant SURVIVES. That is true of BOTH single-guard mutants:

- `drop-bytecode-isolation` (remove the env var) → the bump still invalidates → **expected SURVIVE**
- `drop-mtime-bump` (remove the `os.utime` call) → the env var still suppresses writing → **expected SURVIVE**

Only removing BOTH would kill, and the manifest schema carries ONE anchor per mutant, so "both" is not expressible today. **So the invalidation guards become jointly sufficient and individually un-mutation-testable.** That is the honest price of defence-in-depth here, and it is worth paying: determinism is the property we actually need, and a redundant guard is a feature rather than a gap.

⚠️ **All of that is a PREDICTION, and my predictions have been wrong repeatedly this session — including the one that produced the 577 halt.** Task D MEASURES all three conditions and the manifest's final composition follows the measurement, not this section. Every expectation below carries a STOP arm.

## What this plan does NOT do

- **Does not remove `PYTHONDONTWRITEBYTECODE`.** It stays as defence-in-depth; belt AND braces, since the two mechanisms fail independently.
- **No change to any scoring arm, the baseline control, anchor checking, or the live-tree hash assertion.**
- **No `expect: survived` CONTROL-mutant feature** (still the open fork; this plan is exactly the case that motivates it, since a redundant-guard mutant is a legitimate expected-survivor).
- **No memory writes** (sandbox-denied to agents; the Planner records at close).

## Numbers discipline

⚠️ **Measured 2026-08-27 by the Planner; RE-DERIVE each pre-flight — yours supersede and you say so; mismatch on a load-bearing pin → HALT.**

| id | pin | value | anchor/probe |
|---|---|---|---|
| G1 | the flakiness is REAL | 5 trials without a bump → 4 SURVIVED, 1 KILLED on identical inputs | the trial script in the dev log |
| G2 | the bump fixes it, ACROSS PATHS | 5 trials with a bump at path A → KILLED ×5; 5 trials at a different absolute path B → KILLED ×5; **the env var was NOT set in any of these trials** | same |
| G3 | the write site | `tools/mutation_check.py:188-190` — `mutated = pristine.replace(anchor, replacement, 1)` then `with open(sandbox_target, "w") as f: f.write(mutated)`; the replacement-present re-read follows at `:192-194` | read it |
| G4 | `import os` already present | yes — no new import needed | `/usr/bin/grep -cE "^import os"` → 1 |
| G5 | current manifest | `knowledge/mutants/mutation_check.json` holds three mutants: `score-any-nonzero-as-killed`, `drop-baseline-control`, `drop-bytecode-isolation` | read it |
| G6 | full suite baseline | **1632 collected** (unchanged by exec-577, whose DEV commit added no tests) | `pytest tests/ -q --collect-only \| tail -1` |

## MUST-PRESERVE

- ⚠️ **`/usr/bin/grep` for ALL probes (`-F` unless a regex is stated); zero-match exits 1 — never `&&`-chain a probe.**
- ⚠️ **NEVER read an exit code through a pipe** — `cmd >/dev/null 2>&1; echo "exit=$?"`.
- ⚠️ **The bump must happen AFTER the mutated write and BEFORE the mutant pytest run.** Placing it before the write is inert (the write resets mtime).
- ⚠️ **Determinism must be shown ACROSS AT LEAST TWO ABSOLUTE PATHS, not merely repeated in one.** This is the exact error that produced the 577 halt: I measured 5/5 in one directory and called it settled, while the agent's worktree — a different absolute path, hence a different `pycache_prefix` mirror — disagreed. Repetition in one location does not establish determinism.
- ⚠️ **Do not adjust a mutant, selector, or test to obtain a desired result.** Report what you measure (the exec-574 refusal).
- ⚠️ **Worktree dispatch; every claim cites file:line; absence claims carry positive controls; EVERY DATE IS A FIXED LITERAL.**

## STEP 1 — DEV (the mtime bump + the measurement that decides the manifest)

> **Task A — worktree discipline.** `cd "$(git rev-parse --show-toplevel)" && test -f tools/mutation_check.py && echo TREE_OK` — HALT unless TREE_OK. Resume probe: `/usr/bin/grep -cF "os.utime" tools/mutation_check.py; true` → 0 = full run; ≥1 = resume at Task D.
>
> **Task B — REPRODUCE G1 AND G2 BEFORE FIXING** (a fix for an unobserved defect is a guess, and the 577 halt came from under-measuring). Write the trial script below to `$TMPDIR`, run all three conditions, and paste the raw results into the dev log. ⚠️ **Run the two bump conditions in TWO DIFFERENT absolute paths** — that axis is the one that varied at 577.
> ```
> #!/bin/zsh
> # $1 = dir, $2 = bump|nobump
> D="$1"; MODE="$2"
> rm -rf "$D" && mkdir -p "$D/tests"
> printf 'def add(a, b):\n    return a + b\n' > "$D/target.py"
> printf 'import sys, os\nsys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))\nfrom target import add\ndef test_add():\n    assert add(1, 2) == 3\n' > "$D/tests/test_target.py"
> cd "$D"
> python3 -m pytest tests/test_target.py -q >/dev/null 2>&1
> printf 'def add(a, b):\n    return a - b\n' > target.py
> if [ "$MODE" = "bump" ]; then
>   python3 -c "import os; st=os.stat('target.py'); os.utime('target.py',(st.st_atime, st.st_mtime+1))"
> fi
> python3 -m pytest tests/test_target.py -q >/dev/null 2>&1
> [ $? -eq 1 ] && echo "KILLED" || echo "SURVIVED"
> ```
> Expect: nobump mixed (flaky), bump KILLED at both paths. If nobump comes back KILLED 5/5 on your machine, the flakiness premise does not reproduce there — STOP and report rather than proceeding on my measurement.
>
> **Task C — add the bump to `tools/mutation_check.py`** immediately after the mutated write (G3), before the replacement-present re-read:
> ```python
>             # Force bytecode invalidation by the mechanism CPython actually
>             # uses: it validates a cached .pyc by (source mtime, source size).
>             # A same-byte-length mutation written inside the same mtime second
>             # leaves the baseline's .pyc valid, so the mutant run would execute
>             # BASELINE code and score a false SURVIVED. Measured flaky 4-of-5
>             # before this bump (exec-577). PYTHONDONTWRITEBYTECODE remains set
>             # as defence in depth; this line is what makes it deterministic.
>             _st = os.stat(sandbox_target)
>             os.utime(sandbox_target, (_st.st_atime, _st.st_mtime + 1))
> ```
> ⚠️ Do not reproduce any shipped ANCHOR string in the comment — `            if exit_code == 1:`, `            if baseline_exit != 0:` and the env line must each still `grep -cF` to exactly one afterwards (structural: the runner requires anchor uniqueness at `:169-173`, so this cannot drift and supersedes nothing). Paste all three counts.
>
> **Task D — MEASURE the manifest consequence, then set the manifest to match.** Run all three probe mutants against the fixed runner, separately, and paste every raw output:
> 1. `drop-mtime-bump` — anchor EXACTLY `            os.utime(sandbox_target, (_st.st_atime, _st.st_mtime + 1))` (the single call line, at the indent it occupies in the loop body), replacement EXACTLY `            pass  # mtime bump removed by mutant`; `expect_fail`: `tests/test_mutation_check.py::test_same_byte_length_mutation_is_killed`. **Expected KILLED.** Assert the anchor `grep -cF`s to one before adding it to the manifest — an anchor written from memory rather than from the file is the class that turns a mutant into a silent ERROR.
> 2. the existing `drop-bytecode-isolation` — **expected to now SURVIVE** (the bump covers for it).
> 3. Both together are not expressible as one mutant (single anchor per mutant), so do NOT attempt it — record that as the reason the individual guards are un-mutation-testable.
> **Expected outcome: probes 1 and 2 BOTH SURVIVE.** Then set `knowledge/mutants/mutation_check.json` to carry exactly the mutants that KILL — on this prediction that is `score-any-nonzero-as-killed` and `drop-baseline-control` — REMOVING `drop-bytecode-isolation`, and NOT adding `drop-mtime-bump`, with a one-line `_removed_note` in the JSON recording that both invalidation guards are jointly sufficient and therefore individually un-mutation-testable under a single-anchor schema, pending the `expect: survived` feature.
> ⚠️ **THE MANIFEST FOLLOWS YOUR MEASUREMENT, NOT MY PREDICTION.** If `drop-mtime-bump` KILLS, include it and say the prediction was wrong. If `drop-bytecode-isolation` still KILLS, include it and say so. If either result is one I did not anticipate at all, STOP and report. Never reshape a mutant, selector or test to match this section — that is the exec-574 refusal, and this plan exists because I under-measured once already.
>
> **Task E — targeted run:** `python3 -m pytest tests/test_mutation_check.py -q` → all pass, 0 failed; report `--collect-only` first. Then run the FINAL manifest as you composed it in Task D: `python3 tools/mutation_check.py knowledge/mutants/mutation_check.json 2>&1 | cat`, and separately `python3 tools/mutation_check.py knowledge/mutants/mutation_check.json >/dev/null 2>&1; echo "exit=$?"` → every listed mutant KILLED, `0 survived, 0 error`, and `exit=0`. ⚠️ State the killed-count you actually get rather than a number from this plan: the manifest's size is decided by YOUR Task-D measurement, so a count is not predictable here. DEV runs NO full suite.
>
> **Task F — dev log** `knowledge/dev-logs/mutation-mtime-determinism-dev-2026-08-27.md`: Task-B raw results for all three conditions with the two paths named; the three anchor counts; Task-D's two raw mutant outputs; each pin re-derivation (G1-G6, yours vs the table, "supersedes" where they differ).
>
> **Task G — commit** (worktree; message `[<id>] mutation-mtime-determinism: force bytecode invalidation by mtime; manifest follows the measurement`): `cd "$(git rev-parse --show-toplevel)" && git add tools/mutation_check.py knowledge/mutants/mutation_check.json knowledge/dev-logs/mutation-mtime-determinism-dev-2026-08-27.md && git commit`. Verify `git show --stat HEAD | cat` lists exactly those 3 files.
>
> **Deposits:**
> - `tools/mutation_check.py`
> - `knowledge/mutants/mutation_check.json`
> - `knowledge/dev-logs/mutation-mtime-determinism-dev-2026-08-27.md`
>
> **Scope:**
> - `tools/mutation_check.py`
> - `knowledge/mutants/mutation_check.json`
> - `knowledge/dev-logs/mutation-mtime-determinism-dev-2026-08-27.md`

## STEP 2 — QA (FULL suite + determinism proven the way 577 failed to)

> **Item 1 — full suite.** `cd "$(git rev-parse --show-toplevel)"`; `python3 -m pytest tests/ --tb=short -q 2>&1 | cat | tee knowledge/qa/evidence/mutation-mtime-determinism-2026-08-27/pytest_full.txt` — 0 failed; derive from G6 (1632) plus any test you added.
> **Item 2 — THE DETERMINISM PROOF, raw to `probes-raw.txt`.** Run the full shipped manifest **five times**, pasting every run's summary line: `for i in 1 2 3 4 5; do python3 tools/mutation_check.py knowledge/mutants/mutation_check.json 2>&1 | /usr/bin/grep -F "MUTATION:"; done` → expect the SAME line five times, with `0 survived, 0 error`. ⚠️ The killed-count is whatever DEV's Task-D measurement produced — do not expect a specific number from this plan; what is being tested is that the five lines are IDENTICAL. ⚠️ A single green run is exactly the evidence exec-577 shipped on; five is the minimum that speaks to determinism at all, and even five in ONE location does not prove it — hence Item 3.
> **Item 3 — the SECOND-PATH proof (the axis that broke 577).** ⚠️ The copy must be a REAL GIT REPO: the runner resolves its root with `git rev-parse --show-toplevel` and then runs `git archive HEAD` (`tools/mutation_check.py:67-85`), so a `git archive`-extracted tree — which has no `.git` — makes it abort, and the probe would report a tooling failure rather than a determinism result. Use a local clone: `ALT="$(mktemp -d)/alt"; git clone --local --no-hardlinks "$(git rev-parse --show-toplevel)" "$ALT" >/dev/null 2>&1`, then `cd "$ALT" && python3 tools/mutation_check.py knowledge/mutants/mutation_check.json 2>&1 | /usr/bin/grep -F "MUTATION:"` → same result. Paste the resolved `$ALT` path so the evidence records that it differed from the primary, and `rm -rf` it afterwards. ⚠️ If the second path disagrees with the first, the fix is incomplete — HALT and report; do not average the runs.
> **Item 4 — live-tree integrity, independently:** `shasum -a 256 tools/mutation_check.py` before and after Item 2, both pasted, agreeing with the tool's own `LIVE-TREE UNCHANGED:` line.
> **Item 5 — the other consumer still passes:** `python3 tools/mutation_check.py knowledge/mutants/gate_watcher.json >/dev/null 2>&1; echo "exit=$?"` → `exit=0`; paste its summary line too.
> **Item 6 — hygiene + receipt** `knowledge/qa/evidence/mutation-mtime-determinism-2026-08-27/qa-receipt.md`: numstat vs the DEV commit (3 files); toplevel; reflog `-n 4` → 0 amends; per-item table; **the five-run determinism result and the second-path result each stated plainly on their own line**; then the Rule 20 block INSIDE a "Verification"-headed section (the 556 placement law).
> **Item 7 — commit the evidence** (message `[<id>] mutation-mtime-determinism: QA — full suite + five-run and second-path determinism`): `git add knowledge/qa/evidence/mutation-mtime-determinism-2026-08-27/ && git commit`; verify exactly 3 files.
>
> ⚠️ **Gate note:** pytest summary named above — the gate parses; no benign override pre-declared.
>
> **Deposits:**
> - `knowledge/qa/evidence/mutation-mtime-determinism-2026-08-27/pytest_full.txt`
> - `knowledge/qa/evidence/mutation-mtime-determinism-2026-08-27/probes-raw.txt`
> - `knowledge/qa/evidence/mutation-mtime-determinism-2026-08-27/qa-receipt.md`
>
> **Scope:**
> - `knowledge/qa/evidence/mutation-mtime-determinism-2026-08-27/pytest_full.txt`
> - `knowledge/qa/evidence/mutation-mtime-determinism-2026-08-27/probes-raw.txt`
> - `knowledge/qa/evidence/mutation-mtime-determinism-2026-08-27/qa-receipt.md`

Rule 20 banner (byte-exact, inside the QA receipt's VERIFICATION section):

```
============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
```

## Drafting Cycle

**Tier:** T1 — two lines of behavior plus a manifest edit; the fix and its determinism were measured across two paths before authoring.

**Walk register:** `bellows/knowledge/research/walk-register-mutation-mtime-determinism-2026-08-27.md`

**Walks:** walk 0 pinned; **walks 1-3 complete**, genuine sequential five-lens passes — see the register.
**Direction verdict (after walk 1): PROCEED** — the mtime bump is the whole fix; the measurement decides the manifest.
- Weak spots:          w1 1 folded (`drop-mtime-bump`'s anchor was described rather than quoted — an anchor written from memory is the class that silently ERRORs a mutant); w2 dry; w3 dry
- Destruction:         w1 dry; w2 dry; w3 dry
- Vulnerabilities:     w1 1 folded (QA Item 3's second path used `git archive`, which strips `.git` — the runner needs a REAL repo and would have aborted, reporting a tooling failure as a determinism result); w2 1 folded (⚠️ the fix creates TWO jointly-sufficient guards, so NEITHER single-guard mutant can kill — my expectation that `drop-mtime-bump` would KILL was wrong, and every predicted count was removed from the plan); w3 dry
- Integration-record:  w1 dry; w2 dry; w3 dry (VERIFIED LIVE: the runner tolerates an unknown top-level manifest key, so the `_removed_note` field Task D writes will not break parsing — exit 0, mutants still run)
- ACID:                w1 dry; w2 dry; w3 dry
**Cold panel: NOT convened, decided with reasoning** — T1, a two-line invalidation fix to a tool that never writes the live tree.
**Conformance (§5):** recorded at the freeze from actual runs — see the register's conformance block.
**Closing:** **walk 3 dry, confirming walk 2's folds clear — BAR MET.** Instruction series **2 → 1 → 0**. Close is MANUAL (CEO-lane verdicts; auto_close false).

## Cycle Manifest
tier: T1
target: bellows/tools/mutation_check.py
target_class: detector
state_space: bump-present x same-byte-length x absolute-path — dimensions read from the SYSTEM (CPython's documented `(mtime, size)` invalidation rule, the measured `sys.pycache_prefix` absolute-path mirror, and the runner's actual write site at :188-190), not from the author's model. Cells exercised as the Task-B trial matrix (nobump/bump x two paths, five trials each) and re-proven at QA Items 2 and 3.
mutants: knowledge/mutants/mutation_check.json
class: shop-infra
reads: /Users/marklehn/Developer/GitHub/bellows/tools/mutation_check.py, /Users/marklehn/Developer/GitHub/bellows/tests/test_mutation_check.py, /Users/marklehn/Developer/GitHub/bellows/knowledge/mutants/mutation_check.json, /Users/marklehn/Developer/GitHub/bellows/knowledge/decisions/halted-executable-577.md
writes: tools/mutation_check.py, knowledge/mutants/mutation_check.json, knowledge/dev-logs/mutation-mtime-determinism-dev-2026-08-27.md, knowledge/qa/evidence/mutation-mtime-determinism-2026-08-27/pytest_full.txt, knowledge/qa/evidence/mutation-mtime-determinism-2026-08-27/probes-raw.txt, knowledge/qa/evidence/mutation-mtime-determinism-2026-08-27/qa-receipt.md
open_forks: the `expect: survived` CONTROL-mutant feature — now motivated TWICE by measured cases (`score-exit5-as-killed`, unreachable past the baseline; and `drop-bytecode-isolation`, redundant once the bump lands), which together are the argument for shipping it; whether the runner should assert the sandbox holds no pre-existing bytecode before the baseline; thread 25 remains BLOCKED per thread 27
walks: 3
yields: 2, 1, 0
validation: cycle_check=BAR_MET, plan_lint=0_FAIL, fold_check=CLEAN_x1
coherence: N/A
