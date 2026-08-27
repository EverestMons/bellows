# Walk register — `mutation-self-application-2026-08-27` (bellows)

**schema_version:** `0.3`

**Plan:** `bellows/knowledge/decisions/drafts/executable-mutation-self-application.md`
**Tier:** T1 (Small — one data manifest plus one comment; no behavior change; class shop-infra). **Panel: none.**
**Opened:** 2026-08-27

---

## Walk 0 — context pin (REAL, measured 2026-08-27 — every mutant PROTOTYPED against the live tool before authoring)

1. **The gap:** the runner answers "would this suite catch the bug?" for every other target, and nothing asks it of the runner. Its own guards are protected by tests written from the same model that wrote the guards — the circularity exec-572 proved worthless.
2. **Four mutants prototyped against the LIVE tool, results MEASURED not predicted:** `score-any-nonzero-as-killed` (`if exit_code == 1:` → `if exit_code != 0:`) **KILLED**; `drop-baseline-control` (`if baseline_exit != 0:` → `if False:`) **KILLED**; `drop-bytecode-isolation` (`env[…] = "1"` → `env.pop(…)`) **KILLED**; `score-exit5-as-killed` (`if exit_code == 1:` → `if exit_code in (1, 5):`) **SURVIVED**.
3. **The survivor diagnosed, not alarmed at.** `test_empty_selector_is_error_not_killed` uses a nonsense node id, so pytest returns non-zero on the BASELINE run and the runner reports `ERROR: baseline not green` and continues at `:177-186`, never reaching the scoring block at `:201`. Mutating that block cannot change the test's outcome. **Not a protection hole:** a bad selector is caught by the baseline control (whose own mutant KILLS), and exit 5 cannot reach the scoring arm past a green baseline because a selector that collects unmutated collects when mutated. The exit-5 clause is unreachable-in-practice defence in depth.
4. **Consequence, decided at walk 0:** ship the THREE killing mutants only. A manifest with a permanent known survivor would make every run exit 1 — a check that always fails teaches nothing and gets ignored. The survivor's finding is recorded in the plan, in a code comment, and as the now-MEASURED motivation for the `expect: survived` CONTROL-mutant fork.
5. **⚠️ The Planner's own first prediction was WRONG and is recorded as such:** I expected `score-exit5-as-killed` to KILL, because I had called `test_empty_selector_is_error_not_killed` "the single most important test in the file" when authoring exec-574. The prototype falsified that. The test is real and valuable — it just exercises the BASELINE arm, not the scoring arm.
6. **Anchors verified at authoring:** all three shipped anchors `grep -cF` → 1. Baselines: full suite 1632 collected; `knowledge/mutants/` holds `gate_watcher.json` only.

⚠️ Walk 0 carries no fold rows. Walks 1+ appended AFTER the draft exists, from real passes.

---

## Walk 1 — five-lens sequential walk (post-draft, real)

| id | walk | lens | sub_question | origin | finding | pre_fold_text | resolution |
|---|---|---|---|---|---|---|---|
| — | 1 | Weak spots | — | — | DRY — every pin was measured against the live tool before the draft existed, and Task B makes the agent REPRODUCE both F1 and F2 before writing anything, with a STOP arm if the survivor kills | — | no fold |
| — | 1 | Destruction | — | — | DRY — the tool edit is comment-only, proven by a `git diff` assertion; the runner never writes the live tree and its own sha256 check is verified independently at QA Item 3 | — | no fold |
| w1-1 | 1 | Vulnerabilities | can the comment Task D adds break the manifest it ships alongside? | pre-existing | ⚠️ the comment sits DIRECTLY ABOVE `            if exit_code == 1:` — which is `score-any-nonzero-as-killed`'s anchor — and the runner requires each anchor to occur EXACTLY ONCE. A comment quoting that line in prose would make the count 2, turning the mutant into an ERROR and silently disarming the very check this plan ships. The draft gave no warning against it | `> **Task D — add ONE comment block** at tools/mutation_check.py:201, immediately above if exit_code == 1:, stating: only exit 1 is KILLED; the non-1 arms are defence in depth; the exit-5 arm specifically is unreachable in practice because the baseline control at :177-186 rejects a selector that collects nothing, and a selector that collects at baseline also collects when mutated; therefore a mutant on the exit-5 clause SURVIVES by design and must not be read as a coverage gap. No code change.` | folded: an explicit prohibition on reproducing ANY shipped anchor string inside the comment (refer to the arms in words, never by pasting code), plus a mandatory post-edit assert — `grep -cF` on all three anchors must still return 1, pasted into the dev log |
| — | 1 | Integration-record | — | — | DRY — deposits and scope agree on the six files; the manifest's `mutants:` field names the file this plan writes | — | no fold |
| — | 1 | ACID | — | — | DRY — two pathspec-limited commits (3 files each) with `git show --stat` asserts | — | no fold |

**Walk 1 total: 1 finding (instruction 1 / record 0), folded. Direction verdict: PROCEED.**

---

## Walk 2 — five-lens sequential walk (real)

| id | walk | lens | sub_question | origin | finding | pre_fold_text | resolution |
|---|---|---|---|---|---|---|---|
| — | 2 | Weak spots | — | — | DRY — the exit-code assertions all use the no-pipe form, and MUST-PRESERVE names the measured Planner error (a rejected `git push` read as success through a pipe earlier this session) so the reason survives | — | no fold |
| — | 2 | Destruction | — | — | DRY | — | no fold |
| — | 2 | Vulnerabilities | — | — | DRY — the "unreachable" claim was pressure-tested rather than assumed: a mutation of a SOURCE file cannot change which node ids a selector matches, and an import break yields a collection error (exit 2), not exit 5; the claim is stated as unreachable-in-practice-given-the-baseline, not unreachable-absolutely | — | no fold |
| — | 2 | Integration-record | does exec-576's new rule accept this plan? | — | DRY, and VERIFIED LIVE rather than reasoned: `plan_lint` on this draft prints NO `(s)` and NO `(t)` WARN. This plan declares `target_class: detector` and names `knowledge/mutants/mutation_check.json` in a Deposits block, which is exactly the condition (s) requires. **The rule shipped one plan ago is satisfied by the next real plan, not merely by its own fixtures** | — | no fold |
| — | 2 | ACID | — | — | DRY | — | no fold |

**Walk 2 total: 0 findings — DRY.**

---

## Walk 3 — five-lens sequential walk (confirming pass, real)

| id | walk | lens | sub_question | origin | finding | pre_fold_text | resolution |
|---|---|---|---|---|---|---|---|
| — | 3 | Weak spots | — | — | DRY — QA Item 4 re-runs the `gate_watcher` manifest to prove the comment edit caused no regression in the tool's other consumer | — | no fold |
| — | 3 | Destruction | — | — | DRY — QA Item 3 independently hashes the target before and after, which matters more here than anywhere else: this is the one target where a sandbox-escape bug would corrupt the very tool doing the checking | — | no fold |
| — | 3 | Vulnerabilities | — | — | DRY — MUST-PRESERVE forbids adjusting a mutant, selector or test to obtain a kill (the exec-574 refusal to retune an instrument until it agrees) | — | no fold |
| — | 3 | Integration-record | — | — | DRY — open_forks carries the now-measured CONTROL-mutant feature, plan_lint's own deferred manifest, and thread 25's BLOCKED status per thread 27 | — | no fold |
| — | 3 | ACID | — | — | DRY | — | no fold |

**Walk 3 total: 0 findings — DRY. Two consecutive dry walks — BAR MET.**

---

## Conformance (§5) — recorded at the freeze from ACTUAL runs

- **Prototype runs (2026-08-27, against the LIVE tool, before the draft existed):** three-mutant manifest → `3 killed, 0 survived, 0 error`; single-mutant `score-exit5-as-killed` manifest → `1 survived`. Exit code on the survivor run verified WITHOUT a pipe → `1`, confirming the tool's contract.
- **Anchor verification:** all three shipped anchors `grep -cF` → 1 each.
- **exec-576 integration verified live:** `plan_lint` on this draft emits no `(s)` and no `(t)` WARN.
- **Fold verification (`/usr/bin/grep -cF` on the draft):** w1-1 landed ×1 (`must NOT reproduce any shipped anchor string`).
- **fold_check (EARNED, and it CAUGHT something):** v0 reconstructed by excising the w1-1 block, baselined, then the folded draft diffed against it → first run reported **DRIFT**: `APPEARED: plan_lint: (r) WARN: probe constant without a supersede-class clause`. My fold had introduced a bare `must still be 1` inside a STEP block, which is exactly what check (r) exists to catch. Reworded to state the constant is STRUCTURAL (the runner requires anchor uniqueness at `:169-173`, so it cannot drift and supersedes nothing) with a re-derive instruction; re-run → `FOLD-CHECK CLEAN: machine-readable state unchanged (7 signals held)`. Recorded because the drift was real and mine: a fold that silently adds a WARN is the class fold_check was built for.
- **Structure:** `grep -cE '^## STEP '` → 2.
- **run_check at the freeze:** `lint` → `VERDICT=PASS — exit 0`; `cycle` → first run `VERDICT=FAIL — CONTINUE (bar not met)` because the cycle block still read TBD, then `VERDICT=PASS — BAR_MET` after the walks were recorded. Recorded because it is the checker working correctly on an incomplete artifact, not a defect.

## Closing

**Walks 1-3, yields 1 → 0 → 0. BAR MET on walk 3. Cold panel not convened (T1 data file plus a comment). Close is MANUAL (CEO-lane verdicts; auto_close false). The cycle's real work happened at walk 0, before the draft existed: prototyping all four mutants against the live tool falsified the Planner's own prediction. I had called `test_empty_selector_is_error_not_killed` "the single most important test in the file" when authoring exec-574 — and it does not protect the arm I believed it protected. The protection is real but comes from the baseline control instead. That is precisely what self-application is for, and it is the second time in this arc that running a tool against itself found something reading it could not.**
