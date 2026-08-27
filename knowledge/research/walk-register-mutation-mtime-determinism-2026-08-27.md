# Walk register — `mutation-mtime-determinism-2026-08-27` (bellows)

**schema_version:** `0.3`

**Plan:** `bellows/knowledge/decisions/drafts/executable-mutation-mtime-determinism.md`
**Tier:** T1 (Small — a two-line invalidation fix plus a measurement-driven manifest edit; class shop-infra). **Panel: none.**
**Opened:** 2026-08-27

---

## Walk 0 — context pin (REAL, measured 2026-08-27 across TWO absolute paths)

1. **The 577 halt was correct and the defect was mine.** `drop-bytecode-isolation` returned KILLED 5/5 on the live checkout and SURVIVED in the agent's worktree, on identical code. The agent stopped rather than retuning, exactly as MUST-PRESERVE instructed.
2. **Root cause:** the env var suppresses bytecode WRITING, but the runner builds its child env from `os.environ` (`tools/mutation_check.py:48`), so the inner mutated runner's `env.pop()` re-enables writing. Whether the baseline's `.pyc` is then still valid depends on CPython's `(source mtime, source size)` rule — a same-byte-length mutation inside the same mtime second leaves it valid — and on `sys.pycache_prefix`'s ABSOLUTE-PATH mirror, which differs between a checkout and a worktree.
3. **MEASURED before authoring — the evidence 577 lacked** (synthetic repo, `return a + b` → `return a - b`, five trials each): no bump, path A → **SURVIVED ×4, KILLED ×1** (flaky, caught in the act); bump, path A → KILLED ×5; bump, **different absolute path B** → KILLED ×5. The env var was NOT set in any trial, so the bump alone is sufficient.
4. **⚠️ The Planner's error at 577, named so it is not repeated:** I flagged this exact flakiness risk when designing the mutant, then measured it five times in ONE directory on ONE machine and treated KILLED as settled. Repetition in a single location cannot establish determinism when the varying axis is the absolute path. The dispatch itself supplied the second environment and I did not anticipate it.
5. **Baselines:** full suite 1632 collected; `import os` already present; the manifest currently holds three mutants.

⚠️ Walk 0 carries no fold rows. Walks 1+ appended AFTER the draft exists, from real passes.

---

## Walk 1 — five-lens sequential walk (post-draft, real)

| id | walk | lens | sub_question | origin | finding | pre_fold_text | resolution |
|---|---|---|---|---|---|---|---|
| w1-1 | 1 | Weak spots | is the new mutant's anchor quoted or described? | pre-existing | `drop-mtime-bump`'s anchor was given as prose — "anchor the two new lines' `os.utime(...)` call" — leaving the agent to reconstruct an exact string including indentation. An anchor written from memory rather than copied from the file is the class that turns a mutant into a silent ERROR, which is the failure this whole tool exists to prevent | `> 1. drop-mtime-bump — anchor the two new lines' os.utime(...) call, replacement a no-op comment line; expect_fail: tests/test_mutation_check.py::test_same_byte_length_mutation_is_killed. **Expected KILLED.**` | folded (**verbatim-ellipsis**: the `...` inside `os.utime(...)` is part of the COMPLETE pre-image bytes — my draft wrote the call that way; nothing is elided): the anchor and replacement quoted EXACTLY at their real indentation, plus an instruction to `grep -cF` the anchor to one BEFORE adding it to the manifest |
| — | 1 | Destruction | — | — | DRY — two lines added inside the existing loop; no scoring arm, baseline control, anchor check or live-tree assertion is touched | — | no fold |
| w1-2 | 1 | Vulnerabilities | can QA's second-path probe actually run? | pre-existing | Item 3 built the second path with `git archive HEAD \| tar -x`, which strips `.git`. The runner resolves its root via `git rev-parse --show-toplevel` and then runs `git archive HEAD` (`:67-85`), so it would ABORT there — and the probe would report a tooling failure dressed as a determinism result, on the very axis that broke 577 | `> **Item 3 — the SECOND-PATH proof (the axis that broke 577).** Copy the repo to a second absolute path and run the manifest there: ALT=$(mktemp -d)/alt; git archive HEAD \| (mkdir -p "$ALT" && tar -x -C "$ALT"), then cd "$ALT" && python3 tools/mutation_check.py knowledge/mutants/mutation_check.json 2>&1 \| /usr/bin/grep -F "MUTATION:" → same result. Paste the resolved $ALT path so the evidence records that it differed.` | folded: `git clone --local --no-hardlinks` so the second path is a REAL repo, with the requirement stated and the runner's line cited, plus cleanup |
| — | 1 | Integration-record | — | — | DRY — deposits and scope agree on the six files | — | no fold |
| — | 1 | ACID | — | — | DRY — two pathspec-limited commits (3 files each) with `git show --stat` asserts | — | no fold |

**Walk 1 total: 2 findings (instruction 2 / record 0), folded. Direction verdict: PROCEED.**

---

## Walk 2 — five-lens sequential walk (real)

| id | walk | lens | sub_question | origin | finding | pre_fold_text | resolution |
|---|---|---|---|---|---|---|---|
| — | 2 | Weak spots | — | — | DRY — the Task-C comment mentions the env var by NAME but never reproduces the full anchor line, so anchor uniqueness survives; the plan requires all three counts pasted anyway | — | no fold |
| — | 2 | Destruction | — | — | DRY | — | no fold |
| w2-1 | 2 | Vulnerabilities | after the fix, can EITHER single-guard mutant still kill? | pre-existing | ⚠️ **NO — and my stated expectation was wrong.** The fix creates TWO INDEPENDENTLY SUFFICIENT mechanisms: the env var suppresses writing, the bump invalidates what gets written. Removing one leaves the other doing the job, so `drop-mtime-bump` SURVIVES just as `drop-bytecode-isolation` does. Only removing BOTH would kill, and the schema carries ONE anchor per mutant, so that is not expressible. The plan had asserted `drop-mtime-bump` would KILL and had hardcoded a `3 killed` expectation in two later steps | `The replacement mutant is drop-mtime-bump — remove the os.utime call — which SHOULD then be the one that kills. If the measurement contradicts either expectation, STOP and report.` | folded in three places: the section rewritten to state the defence-in-depth TRADEOFF honestly (more robust, less mutation-testable) with BOTH mutants expected to survive; Task D extended to three probes with the manifest explicitly following the agent's measurement rather than the plan's prediction; and every hardcoded killed-count removed from Task E and QA Item 2, replaced by "the count is whatever your measurement produced" |
| — | 2 | Integration-record | — | — | DRY | — | no fold |
| — | 2 | ACID | — | — | DRY | — | no fold |

**Walk 2 total: 1 finding (instruction 1 / record 0), folded — and it inverted the plan's expected outcome.**

---

## Walk 3 — five-lens sequential walk (confirming pass, real)

| id | walk | lens | sub_question | origin | finding | pre_fold_text | resolution |
|---|---|---|---|---|---|---|---|
| — | 3 | Weak spots | — | — | DRY — Task B carries a STOP arm for the case where the flakiness does not reproduce on the agent's machine, so the plan cannot proceed on my measurement alone | — | no fold |
| — | 3 | Destruction | — | — | DRY | — | no fold |
| — | 3 | Vulnerabilities | — | — | DRY — the bump is placed AFTER the write (MUST-PRESERVE says why placing it before is inert), and MUST-PRESERVE now names the two-absolute-paths requirement as the specific 577 error | — | no fold |
| — | 3 | Integration-record | does the `_removed_note` field break the parser? | — | DRY, and VERIFIED LIVE rather than assumed: a manifest with an extra top-level key parses fine — exit 0, mutants still run. So Task D's note field is safe | — | no fold |
| — | 3 | ACID | — | — | DRY | — | no fold |

**Walk 3 total: 0 findings — DRY. BAR MET.**

---

## Conformance (§5) — recorded at the freeze from ACTUAL runs

- **Determinism trials (2026-08-27, before authoring):** nobump path A → SURVIVED ×4, KILLED ×1; bump path A → KILLED ×5; bump path B (different absolute path) → KILLED ×5.
- **Parser tolerance verified live:** manifest with an unknown top-level key → exit 0, mutants run.
- **Fold verification (`/usr/bin/grep -cF` on the draft):** w1-1 landed ×1 (`pass  # mtime bump removed by mutant`); w1-2 landed ×1 (`must be a REAL GIT REPO`); w2-1 landed ×2 (`jointly sufficient and individually un-mutation-testable`, `THE MANIFEST FOLLOWS YOUR MEASUREMENT`).
- **Structure:** `grep -cE '^## STEP '` → 2.
- **run_check at the freeze (2026-08-27, all branched-on; lint at the DEPOSIT path via a `lintmirror-` copy):** `lint` -> `VERDICT=PASS — exit 0`; exec-576's `(s)`/`(t)` checks BOTH SILENT (this plan declares `target_class: detector` and names its mutants path); `cycle` -> `VERDICT=PASS — BAR_MET`; `register` -> first run `VERDICT=FAIL` on row w1-1's `truncated_pre_fold_text`, resolved with the sanctioned `verbatim-ellipsis` marker because the `...` inside `os.utime(...)` is genuinely part of the pre-image bytes, then `VERDICT=PASS`. **Fourth encounter with this trap this session — pre-empted twice, missed twice; the pattern is that I catch it when quoting prose and miss it when quoting CODE containing an ellipsis.**
- **fold_check (EARNED, not authored):** v0 reconstructed by reverting the w1-2 Item-3 rewrite, baselined, then the frozen draft diffed against it -> `FOLD-CHECK CLEAN: machine-readable state unchanged (6 signals held)`.

## Closing

**Walks 1-3, yields 2 → 1 → 0. BAR MET on walk 3. Cold panel not convened (T1, a two-line invalidation fix). Close is MANUAL (CEO-lane verdicts; auto_close false). The cycle's real work was w2-1, which INVERTED the plan's expected outcome: I had written that `drop-mtime-bump` would become the killing mutant, and walking the consequence showed that two jointly-sufficient guards make BOTH single-guard mutants survive. Every hardcoded count downstream of that prediction was removed. The pattern is worth naming, because it is the third instance this arc: I keep asserting what a measurement will show and being wrong — at 574 about which test protected which arm, at 577 about determinism from one directory, and here about which mutant would kill. The structural fix is not resolving to predict better; it is writing plans whose instructions carry the measurement and whose STOP arms fire when my prediction and the agent's result diverge.**
