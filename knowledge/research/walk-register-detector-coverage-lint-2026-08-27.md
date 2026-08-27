# Walk register — `detector-coverage-lint-2026-08-27` (bellows)

**schema_version:** `0.3`

**Plan:** `bellows/knowledge/decisions/drafts/executable-detector-coverage-lint.md`
**Tier:** T1 (Small — two WARN-only checks reusing an existing parsed dict, plus tests; class shop-infra). **Panel: none.**
**Opened:** 2026-08-27

---

## Walk 0 — context pin (REAL, measured 2026-08-27)

1. **Thread 23, CEO-approved.** Two things currently depend on the author remembering them: whether a detector's tests enumerate its state space, and whether anyone asks if those tests would catch the bug. exec-572 shipped a guard past 8 tests and 5 walks because neither was asked mechanically; exec-573 answered the first by hand and exec-575 the second.
2. **The honest division, fixed at walk 0:** deciding a target IS a detector is IRREDUCIBLY authored — no lint knows a guard from a formatter. What is mechanizable is every CONSEQUENCE of the declaration. One small auditable judgment; everything downstream arithmetic.
3. **Funnel MEASURED before authoring** (the warn-first house law), over all 321 `Done/executable-*.md`: 28 carry a Cycle Manifest `target:`, 25 of those are `.py`, **12** have a detector-ish basename, **0** declare `target_class` (the field does not exist yet). So (t) fires 12 times across 321 — 8 of them in the last fifteen plans — and (s) fires zero times today because it is gated on a declaration nobody has made.
4. **Design:** both checks read the `stanza_fields` dict the `(f-stanza)` block at `plan_lint.py:508-547` already builds; no new parser, no new required fields, no exit-code change.
5. **(t) is advisory FOREVER** — a name pattern is invisible when incomplete (a detector called `resolve_state.py` matches nothing), so it may make an omission visible but must never decide it.

⚠️ Walk 0 carries no fold rows. Walks 1+ appended AFTER the draft exists, from real passes.

---

## Walk 1 — five-lens sequential walk (post-draft, real)

| id | walk | lens | sub_question | origin | finding | pre_fold_text | resolution |
|---|---|---|---|---|---|---|---|
| w1-1 | 1 | Weak spots | is the test file a choice or a pin? | pre-existing | Task D let the agent pick between an existing plan_lint test module and a new one, while the Deposits and Scope blocks hardcoded `tests/test_plan_lint_detector_checks.py`. Any choice but that path fails `deposit_exists` — the branch could only ever be wrong | `**Task D — tests in tests/test_plan_lint.py** (or the existing plan_lint test module — find it first with ls tests/ and use it; if none exists, create tests/test_plan_lint_detector_checks.py and say so):` | folded: PINNED to the new module, with the reason measured at authoring — `tests/` already holds BOTH `test_plan_lint.py` and `test_plan_lint_bare_constants.py` (check (r)'s own module), so the house convention is a separate module per check family, and the plan now says to clone that file's fixture idiom |
| — | 1 | Destruction | — | — | DRY — WARN-only prints; no existing check touched; `_STANZA_REQUIRED` explicitly left alone so no existing plan starts warning about fields it was never asked for | — | no fold |
| w1-2 | 1 | Vulnerabilities | how does QA establish the "before" exit code? | pre-existing | Item 2.3 resolved the pre-change `plan_lint` via `git show HEAD~1:` — the measured cross-terminal interleave class: another terminal's commit landing between steps silently redefines `HEAD~1`, so the comparison would be against the wrong code | `Establish "before" by running the same command on the PREVIOUS commit's plan_lint: git stash is forbidden here — instead git show HEAD~1:scripts/plan_lint.py > /tmp/plan_lint_prev.py and run that. Paste both.` | folded: resolve the DEV commit by its own `[<id>]` tag (`git log --format='%H %s' \| grep -F "[<id>] detector-coverage-lint:"`), then use `${DEV}^`, pasting the resolved sha alongside both exit codes |
| — | 1 | Integration-record | — | — | DRY — manifest reads/writes agree with the deposits and scope blocks | — | no fold |
| — | 1 | ACID | — | — | DRY — two pathspec-limited commits (3 files each) with `git show --stat` asserts | — | no fold |

**Walk 1 total: 2 findings (instruction 2 / record 0), folded. Direction verdict: PROCEED.**

---

## Walk 2 — five-lens sequential walk (real)

| id | walk | lens | sub_question | origin | finding | pre_fold_text | resolution |
|---|---|---|---|---|---|---|---|
| — | 2 | Weak spots | — | — | DRY — QA Item 2.2 is satisfiable: 13 of the 25 `.py`-target plans do NOT match the detector pattern, so a real negative example exists rather than needing a fixture | — | no fold |
| — | 2 | Destruction | — | — | DRY | — | no fold |
| w2-1 | 2 | Vulnerabilities | can the `mutants` field be satisfied without meaning anything? | **fold-introduced (this plan's own manifest)** | ⚠️ a presence-only check accepts ANY prose — including the literal word `DEFERRED`, which is exactly what THIS plan's manifest had written. The field would become a box to tick, which is the failure mode the whole arc exists to remove. Found by self-application: the plan declares `target_class: detector` and its own new check would have passed it | manifest field: `mutants: knowledge/mutants/plan_lint_detector.json — DEFERRED to the follow-up plan, and named here as an open fork rather than a deposit. Declaring a mutants path this plan does not write would be exactly the paper commitment check (s) is built to catch, and self-applying the rule on the plan that introduces it risks circularity; the follow-up promoting (t) to FAIL carries it.` | folded TWICE: (i) the check tightened — WARN unless `mutants` names a path that EITHER exists on disk OR appears in a `**Deposits:**` block, so prose cannot satisfy it; (ii) the manifest rewritten to `mutants: NONE — deferred (open fork)`, and the plan now states that it TRIPS ITS OWN check (s), that the WARN is CORRECT, and that QA must SHOW it firing rather than silence it — the exec-574 refusal to retune an instrument until it agrees |
| — | 2 | Integration-record | — | — | DRY | — | no fold |
| — | 2 | ACID | — | — | DRY | — | no fold |

**Walk 2 total: 1 finding (instruction 1 / record 0), folded — and the most valuable of the cycle: the check was tested against its own author's manifest and failed.**

---

## Walk 3 — five-lens sequential walk (real)

| id | walk | lens | sub_question | origin | finding | pre_fold_text | resolution |
|---|---|---|---|---|---|---|---|
| w3-1 | 3 | Weak spots | can the self-lint probe find the plan file? | fold-introduced (w2-1's new QA item) | the new Item 2.5 named `knowledge/decisions/in-progress-executable-<id>.md`, but the claimed file is renamed through `in-progress-` and `verdict-pending-` as the plan runs, AND the QA agent works in a worktree that does not hold `knowledge/decisions/` at all — the probe would have failed on a missing path and looked like a broken check | `python3 scripts/plan_lint.py knowledge/decisions/in-progress-executable-<id>.md 2>&1 \| /usr/bin/grep -F "(s) WARN"; true` | folded: resolve by GLOB against the LIVE checkout's absolute path (`ls /Users/.../knowledge/decisions/*executable-<id>.md \| head -1`), echoing the resolved path so the evidence records which file was linted |
| — | 3 | Destruction | — | — | DRY | — | no fold |
| — | 3 | Vulnerabilities | — | — | DRY — test 3 is the always-warns negative control, test 9 pins the exit-code invariant, and QA Item 2.6 proves (s) discriminates its two clauses rather than warning wholesale | — | no fold |
| — | 3 | Integration-record | — | — | DRY | — | no fold |
| — | 3 | ACID | — | — | DRY | — | no fold |

**Walk 3 total: 1 finding (instruction 1 / record 0), folded.**

---

## Walk 4 — five-lens sequential walk (confirming pass, real)

| id | walk | lens | sub_question | origin | finding | pre_fold_text | resolution |
|---|---|---|---|---|---|---|---|
| — | 4 | Weak spots | — | — | DRY — Task B makes the agent RE-MEASURE the funnel before building on it, with a STOP arm if the detector count has moved by more than ±3 | — | no fold |
| — | 4 | Destruction | — | — | DRY | — | no fold |
| — | 4 | Vulnerabilities | — | — | DRY — the MUST-PRESERVE forbids promoting (t) to FAIL by tidying, and requires the docstring to say why | — | no fold |
| — | 4 | Integration-record | — | — | DRY — open_forks carries the WARN→FAIL promotion, the deferred plan_lint mutants manifest, and the `target_class` vocabulary question | — | no fold |
| — | 4 | ACID | — | — | DRY | — | no fold |

**Walk 4 total: 0 findings — DRY. BAR MET.**

---

## Conformance (§5) — recorded at the freeze from ACTUAL runs

- **Funnel measured at authoring** (the warn-first justification): 321 Done executables / 28 with a manifest target / 25 `.py` / 12 detector-named / 0 declaring `target_class`.
- **Test-module convention verified:** `ls tests/ | grep -iF plan_lint` → `test_plan_lint.py`, `test_plan_lint_bare_constants.py` — a separate module per check family, which is why the new module is pinned rather than chosen.
- **Fold verification (`/usr/bin/grep -cF` on the draft):** w1-1 landed x1 (`the house convention is a SEPARATE module per check family`); w1-2 landed x1 (`never HEAD-relative`), superseded x0 (`HEAD~1:scripts`); w2-1 landed x2 (`deliberately strict`, `TRIPS ITS OWN check`); w3-1 landed x1 (`resolve the plan file by GLOB`), superseded x0.
- **Structure:** `grep -cE '^## STEP '` → 2.
- **run_check runs at the freeze (2026-08-27, all branched-on; lint at the DEPOSIT path via a `lintmirror-` copy):** `lint` -> `VERDICT=PASS — exit 0`; `cycle` -> `VERDICT=PASS — BAR_MET`; `register` -> `VERDICT=PASS — 1 CONFORMANT, 0 UNCONFORMANT` on the FIRST run (the ellipsis and escaped-pipe traps both pre-empted at authoring this time).
- **fold_check (EARNED, not authored):** v0 reconstructed by reversing the w2-1 manifest arm (anchor asserted x1), baselined, then the frozen draft diffed against it -> `FOLD-CHECK CLEAN: machine-readable state unchanged (6 signals held)`.

## Closing

**Walks 1-4, yields 3 → 1 → 1 → 0. BAR MET on walk 4. Cold panel not convened (T1 advisory-only lint additions; 561/565 precedent). Close is MANUAL (CEO-lane verdicts; auto_close false). The finding that earned the cycle was w2-1, and it came from self-application: this plan declares `target_class: detector`, so its own new check could be run against its own manifest — and the manifest passed while meaning nothing, because a presence-only test accepts the word DEFERRED. The check is now strict enough that this plan HONESTLY TRIPS IT, and QA is required to show the warn firing rather than silence it. A rule whose author exempts himself is not a rule.**
