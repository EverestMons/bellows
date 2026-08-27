# bellows — executable: the mutation runner mutates ITSELF — `knowledge/mutants/mutation_check.json` (thread 24's self-application fork, prototyped against the live tool)

**Date:** 2026-08-27 | **Project:** bellows | **Tier:** Small | **Dispatch Mode:** bellows | **cycle_tier:** T1 | **Test Scope:** targeted (the manifest run) + full suite at QA | **Execution:** Step 1 (DEV) → Step 2 (QA) | **qa_steps:** 2 | **pause_for_verdict:** always

**auto_close:** false

**Depends on:** exec-575 (the mutation runner, shipped and proven 2 killed / 0 survived on `gate_watcher`); the self-application open fork recorded in that plan; memory `mechanize-to-reserve-reasoning`; exec-574 (HALTED — the bytecode-isolation defect one of these mutants reproduces).

## Why this exists

The runner answers "would this suite catch the bug?" for every other target. Nothing yet asks it of the runner. Its own guards — only-exit-1-is-KILLED, the green-baseline control, the bytecode isolation — are currently protected by tests **I wrote from the same model that wrote the guards**, which is the exact circularity exec-572 demonstrated is worthless.

This plan closes that with a manifest that mutates `mutation_check.py` itself. The regress stops here and the plan says so rather than pretending otherwise: something must be trusted at the bottom, and it should be the smallest, most-examined thing.

## ⚠️ Prototyped against the LIVE tool before authoring — all four results measured, not predicted

| mutant | mutation | result | meaning |
|---|---|---|---|
| `score-any-nonzero-as-killed` | `if exit_code == 1:` → `if exit_code != 0:` | **KILLED** | the scoring arm's core claim IS protected — reached via the TIMEOUT path (`exit_code == -1`), which is genuinely reachable past a green baseline |
| `drop-baseline-control` | `if baseline_exit != 0:` → `if False:` | **KILLED** | the green-baseline positive control is real |
| `drop-bytecode-isolation` | `env["PYTHONDONTWRITEBYTECODE"] = "1"` → `env.pop(…, None)` | **KILLED** | exec-574's defect is genuinely caught by its regression test — the fix is not decorative |
| `score-exit5-as-killed` | `if exit_code == 1:` → `if exit_code in (1, 5):` | **SURVIVED** | ⚠️ see below — a real finding, and a BENIGN one |

**The survivor, diagnosed rather than alarmed at.** `test_empty_selector_is_error_not_killed` uses a nonsense node id, so pytest returns non-zero on the **BASELINE** run; the runner reports `ERROR: baseline not green` and `continue`s at `tools/mutation_check.py:177-186`, never reaching the scoring block at `:201`. Mutating the scoring block therefore cannot change that test's outcome. **This is not a protection hole:** a bad selector is caught by the baseline control (whose own mutant KILLS), and exit 5 cannot reach the scoring arm past a green baseline, because a selector that collects tests unmutated collects them mutated too. The exit-5 clause at `:201` is unreachable-in-practice defence in depth.

**Consequence for this plan:** the shipped manifest carries the THREE killing mutants. `score-exit5-as-killed` is NOT shipped, because the tool exits 1 on any survivor and a manifest with a permanent known survivor would make every run red — a check that always fails teaches nothing and gets ignored. Its finding is recorded instead, in the plan, in a code comment, and as the now-motivated open fork for an `expect: survived` CONTROL-mutant feature.

## What this plan does NOT do

- **No change to `tools/mutation_check.py` behavior.** The only edit is a COMMENT at the scoring block recording why the exit-5 clause is unreachable given the baseline control, so a later reader does not delete it as dead code nor write a test that cannot pass.
- **No `expect: survived` feature.** That is the CONTROL-mutant fork — now motivated by a measured case rather than speculation, and deferred to its own plan.
- **No memory writes** (sandbox-denied to agents; the Planner records at close).

## Numbers discipline

⚠️ **Measured 2026-08-27 by the Planner against the LIVE tool; RE-DERIVE each pre-flight — yours supersede and you say so; mismatch on a load-bearing pin → HALT.**

| id | pin | value | anchor/probe |
|---|---|---|---|
| F1 | the three shipping mutants all KILL | prototyped: `score-any-nonzero-as-killed` KILLED, `drop-baseline-control` KILLED, `drop-bytecode-isolation` KILLED | run the manifest |
| F2 | the fourth SURVIVES, benignly | `score-exit5-as-killed` SURVIVED because the baseline arm short-circuits before `:201` | run it separately; read `:177-186` |
| F3 | anchors, each exactly once | `            if exit_code == 1:` (`:201`); `            if baseline_exit != 0:` (`:177`); `    env["PYTHONDONTWRITEBYTECODE"] = "1"` (`:49`) | `/usr/bin/grep -cF` each |
| F4 | exit-code contract holds on a survivor | the prototype run with a survivor exited **1** — verified WITHOUT a pipe (`cmd >/dev/null 2>&1; echo $?`), since `$?` after a pipe is the last command's | rerun that way |
| F5 | mutants dir | `knowledge/mutants/` holds `gate_watcher.json` only | `ls knowledge/mutants/` |
| F6 | full suite baseline | **1632 collected** (1631 passed + 1 skipped at exec-576) | `pytest tests/ -q --collect-only \| tail -1` |

## MUST-PRESERVE

- ⚠️ **`/usr/bin/grep` for ALL probes (`-F` unless a regex is stated); zero-match exits 1 — never `&&`-chain a probe.**
- ⚠️ **NEVER read an exit code through a pipe.** `cmd | tail; echo $?` reports `tail`'s status. Every exit-code assertion in this plan uses `cmd >/dev/null 2>&1; echo "exit=$?"`. (Measured Planner error earlier this session: a rejected `git push` read as success this way.)
- ⚠️ **The runner's BEHAVIOR is not modified** — comment only. Prove it: `git diff` on `tools/mutation_check.py` must show only comment lines added.
- ⚠️ **If any of the three shipping mutants does NOT kill on your run, STOP and report.** Do not adjust the mutant, the selector, or the tests to obtain a kill — that is retuning the instrument until it agrees (the exec-574 refusal).
- ⚠️ **Worktree dispatch; every claim cites file:line; absence claims carry positive controls; EVERY DATE IS A FIXED LITERAL.**

## STEP 1 — DEV (the manifest + the comment + the reproduction)

> **Task A — worktree discipline.** `cd "$(git rev-parse --show-toplevel)" && test -f tools/mutation_check.py && echo TREE_OK` — HALT unless TREE_OK. Resume probe: `test -f knowledge/mutants/mutation_check.json && echo 1 || echo 0` → 0 = full run; 1 = resume at Task D.
>
> **Task B — REPRODUCE F1 AND F2 BEFORE WRITING ANYTHING.** Build both manifests in `$TMPDIR` (the three-mutant one and a separate single-mutant one for `score-exit5-as-killed`), run the LIVE tool on each, and paste both raw outputs into the dev log. Expected: 3 killed / 0 survived, and 1 survived respectively. ⚠️ If `score-exit5-as-killed` KILLS on your run, the F2 diagnosis is wrong — STOP and report, because the shipped manifest's composition depends on it.
>
> **Task C — write `knowledge/mutants/mutation_check.json`** with exactly the three KILLING mutants from the F1 table, each carrying a `why` that names the real defect it reproduces (the 574 bytecode class for the third). Use the F3 anchors verbatim.
>
> **Task D — add ONE comment block** at `tools/mutation_check.py:201`, immediately above `if exit_code == 1:`, stating: only exit 1 is KILLED; the non-1 arms are defence in depth; **the exit-5 arm specifically is unreachable in practice because the baseline control at `:177-186` rejects a selector that collects nothing, and a selector that collects at baseline also collects when mutated**; therefore a mutant on the exit-5 clause SURVIVES by design and must not be read as a coverage gap. No code change.
> ⚠️ **The comment must NOT reproduce any shipped anchor string.** It sits directly above `            if exit_code == 1:`, which is `score-any-nonzero-as-killed`'s anchor, and the manifest requires that anchor to occur EXACTLY ONCE — quoting it in prose would make the count 2 and turn the mutant into an ERROR, silently disarming the very check this plan ships. Refer to the arms in words ("the exit-1 arm", "the exit-5 arm"), never by pasting the code. **After the edit, assert it:** `/usr/bin/grep -cF "            if exit_code == 1:" tools/mutation_check.py` — the count must still be exactly one. This is a STRUCTURAL constant, not a measured one: the runner REQUIRES anchor uniqueness (`tools/mutation_check.py:169-173` errors when the count is anything else), so it cannot drift and supersedes nothing. Re-derive it and paste yours into the dev log; same assert for the other two anchors.
>
> **Task E — dev log** `knowledge/dev-logs/mutation-self-application-dev-2026-08-27.md`: both Task-B raw outputs, each pin re-derivation (F1-F6, yours vs the table, say "supersedes" where they differ), and the `git diff --stat` proving the tool edit is comment-only.
>
> **Task F — commit** (worktree; message `[<id>] mutation-self-application: the runner's own mutants manifest; scoring-arm comment`): `cd "$(git rev-parse --show-toplevel)" && git add knowledge/mutants/mutation_check.json tools/mutation_check.py knowledge/dev-logs/mutation-self-application-dev-2026-08-27.md && git commit`. Verify `git show --stat HEAD | cat` lists exactly those 3 files.
>
> **Deposits:**
> - `knowledge/mutants/mutation_check.json`
> - `tools/mutation_check.py`
> - `knowledge/dev-logs/mutation-self-application-dev-2026-08-27.md`
>
> **Scope:**
> - `knowledge/mutants/mutation_check.json`
> - `tools/mutation_check.py`
> - `knowledge/dev-logs/mutation-self-application-dev-2026-08-27.md`

## STEP 2 — QA (FULL suite + both manifests run)

> **Item 1 — full suite.** `cd "$(git rev-parse --show-toplevel)"`; `python3 -m pytest tests/ --tb=short -q 2>&1 | cat | tee knowledge/qa/evidence/mutation-self-application-2026-08-27/pytest_full.txt` — 0 failed; derive from F6 (1632). No new tests, so expect the same count.
> **Item 2 — the SELF-APPLICATION run, raw tail to `probes-raw.txt`:** `python3 tools/mutation_check.py knowledge/mutants/mutation_check.json 2>&1 | cat`, then SEPARATELY `python3 tools/mutation_check.py knowledge/mutants/mutation_check.json >/dev/null 2>&1; echo "exit=$?"` → expect `3 killed, 0 survived, 0 error` and `exit=0`. ⚠️ Two invocations deliberately: the exit code must NOT be read through the pipe.
> **Item 3 — the runner did not corrupt itself:** it mutates its OWN file, so verify the live target independently: `shasum -a 256 tools/mutation_check.py` BEFORE and AFTER the Item-2 run, both pasted, and confirm the tool's own `LIVE-TREE UNCHANGED:` line agrees with them. ⚠️ This is the one target where a sandbox-escape bug would corrupt the very tool doing the checking — the independent hash is not ceremony here.
> **Item 4 — the gate_watcher manifest still passes** (no regression from the comment edit): `python3 tools/mutation_check.py knowledge/mutants/gate_watcher.json >/dev/null 2>&1; echo "exit=$?"` → `exit=0`; paste the summary line too.
> **Item 5 — hygiene + receipt** `knowledge/qa/evidence/mutation-self-application-2026-08-27/qa-receipt.md`: numstat vs the DEV commit (3 files); toplevel; reflog `-n 4` → 0 amends; per-item table; **the self-application result stated plainly in its own line**; then the Rule 20 block INSIDE a "Verification"-headed section (the 556 placement law).
> **Item 6 — commit the evidence** (message `[<id>] mutation-self-application: QA — full suite + self-run`): `git add knowledge/qa/evidence/mutation-self-application-2026-08-27/ && git commit`; verify exactly 3 files.
>
> ⚠️ **Gate note:** pytest summary named above — the gate parses; no benign override pre-declared.
>
> **Deposits:**
> - `knowledge/qa/evidence/mutation-self-application-2026-08-27/pytest_full.txt`
> - `knowledge/qa/evidence/mutation-self-application-2026-08-27/probes-raw.txt`
> - `knowledge/qa/evidence/mutation-self-application-2026-08-27/qa-receipt.md`
>
> **Scope:**
> - `knowledge/qa/evidence/mutation-self-application-2026-08-27/pytest_full.txt`
> - `knowledge/qa/evidence/mutation-self-application-2026-08-27/probes-raw.txt`
> - `knowledge/qa/evidence/mutation-self-application-2026-08-27/qa-receipt.md`

Rule 20 banner (byte-exact, inside the QA receipt's VERIFICATION section):

```
============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
```

## Drafting Cycle

**Tier:** T1 — one data manifest, one comment, no behavior change; every result prototyped against the live tool before authoring.

**Walk register:** `bellows/knowledge/research/walk-register-mutation-self-application-2026-08-27.md`

**Walks:** walk 0 pinned; **walks 1-3 complete**, genuine sequential five-lens passes — see the register.
**Direction verdict (after walk 1): PROCEED** — the manifest is data; every result was prototyped before authoring.
- Weak spots:          w1 dry; w2 dry; w3 dry
- Destruction:         w1 dry; w2 dry; w3 dry
- Vulnerabilities:     w1 1 folded (⚠️ the comment Task D adds sits directly above a shipped ANCHOR — quoting the line in prose would make its count 2 and silently disarm the mutant); w2 dry; w3 dry
- Integration-record:  w1 dry; w2 dry (VERIFIED LIVE: exec-576's new (s)/(t) checks are both SILENT on this plan — it declares target_class:detector and names its mutants path in Deposits, so the rule shipped one plan ago is satisfied by the next real plan rather than only by fixtures); w3 dry
- ACID:                w1 dry; w2 dry; w3 dry
**Cold panel: NOT convened, decided with reasoning** — T1, a data file plus a comment; the tool's behavior is untouched.
**Conformance (§5):** recorded at the freeze from actual runs — see the register's conformance block.
**Closing:** **walks 2 and 3 both dry — BAR MET.** Instruction series **1 → 0 → 0**. Close is MANUAL (CEO-lane verdicts; auto_close false).

## Cycle Manifest
tier: T1
target: bellows/tools/mutation_check.py
target_class: detector
state_space: exit-code arms x reachability-past-baseline — dimensions read from the SYSTEM (pytest's own documented exit codes, and the runner's actual control flow at :177-186 and :201), not from the author's model. The arms are enumerated in the F1/F2 tables with their measured reachability: exit 1 (KILLED, tested), exit 0 (SURVIVED, tested), exit -1 timeout (ERROR, tested — and the path by which the scoring arm is reachable at all), exit 5 (ERROR, UNREACHABLE past a green baseline — measured, documented, deliberately not shipped as a mutant).
mutants: knowledge/mutants/mutation_check.json
class: shop-infra
reads: /Users/marklehn/Developer/GitHub/bellows/tools/mutation_check.py, /Users/marklehn/Developer/GitHub/bellows/tests/test_mutation_check.py, /Users/marklehn/Developer/GitHub/bellows/knowledge/mutants/gate_watcher.json, /Users/marklehn/Developer/GitHub/bellows/knowledge/decisions/halted-executable-574.md
writes: knowledge/mutants/mutation_check.json, tools/mutation_check.py, knowledge/dev-logs/mutation-self-application-dev-2026-08-27.md, knowledge/qa/evidence/mutation-self-application-2026-08-27/pytest_full.txt, knowledge/qa/evidence/mutation-self-application-2026-08-27/probes-raw.txt, knowledge/qa/evidence/mutation-self-application-2026-08-27/qa-receipt.md
open_forks: the CONTROL-mutant feature (`expect: survived` in the manifest schema) — now motivated by the MEASURED `score-exit5-as-killed` case rather than speculation, and the mechanism by which a permanently-benign survivor could ship without making every run red; whether a mutants manifest should be REQUIRED for plan_lint itself (thread 23's deferred fork); thread 25 remains BLOCKED per thread 27's measurement
walks: 3
yields: 1, 0, 0
validation: cycle_check=BAR_MET, plan_lint=0_FAIL, fold_check=CLEAN_x1
coherence: N/A
