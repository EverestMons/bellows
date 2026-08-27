# bellows — executable: plan_lint (s)+(t) — a DETECTOR-class plan must declare its state space and its mutants (thread 23, warn-first with a measured funnel)

**Date:** 2026-08-27 | **Project:** bellows | **Tier:** Small | **Dispatch Mode:** bellows | **cycle_tier:** T1 | **Test Scope:** targeted (the two new checks) + full suite at QA | **Execution:** Step 1 (DEV) → Step 2 (QA) | **qa_steps:** 2 | **pause_for_verdict:** always

**auto_close:** false

**Depends on:** tuyere thread 23 (CEO-approved 2026-08-27); thread 24 SHIPPED as exec-575 (the mutation runner, 2 killed / 0 survived on real mutants) — this plan makes its manifest a declared artifact rather than an ad-hoc file; exec-573 (`TestPauseStateSpace`, the first tier-2 suite); memory `mechanize-to-reserve-reasoning`.

## Why this exists

Two things currently depend entirely on the plan author remembering them: whether a detector's tests enumerate its state space, and whether anyone ever asks if those tests would catch the bug. Exec-572 shipped a guard past 8 tests and 5 walks because neither question was asked mechanically. Exec-573 answered the first by hand; exec-575 answered the second by hand. This plan makes both **declared and checkable** so the next detector cannot quietly skip them.

## ⚠️ What this can and cannot mechanize — stated up front

**Irreducible:** deciding that a target IS a detector is a judgment. No lint can know that a new module is a guard rather than a formatter. This plan does not pretend otherwise — the author declares `target_class: detector` and that declaration is authored.

**Mechanized:** every CONSEQUENCE of that declaration. Once declared, the plan must name its state-space dimensions and its mutants manifest, and the lint enforces that with no judgment involved. The declaration is one small auditable decision; everything downstream becomes arithmetic.

**The nudge:** check (t) fires when a target's *name* looks like a detector and `target_class` was NOT declared. That is a heuristic, so it is advisory forever and never a FAIL basis — a curated pattern list is invisible when incomplete (a detector named `resolve_state.py` matches nothing). It exists to make the omission visible, not to decide it.

## Measured funnel (the warn-first house law — prototyped BEFORE authoring)

Run against all 321 `Done/executable-*.md` at authoring:

| population | count |
|---|---|
| Done executables | 321 |
| …with a Cycle Manifest `target:` field | 28 |
| …whose target is a `.py` | 25 |
| …whose target BASENAME matches `(check\|guard\|watch\|filter\|dedup\|stale\|detect\|valid\|lint\|verif)` | **12** |
| …declaring `target_class:` today | **0** (the field does not exist yet) |

So **(t) would fire 12 times across 321 plans** — 8 of them in the last fifteen (`561, 562, 563, 565, 569, 571, 573, 575`), i.e. the rule bites exactly where the recent detector work is and is silent on the long tail. **(s) would fire ZERO times today**, because it is gated on a declaration nobody has made yet; it only speaks when an author opts in and then omits the follow-through. That asymmetry is deliberate: (t) creates the pressure, (s) is the follow-through.

## What this plan does NOT do

- **No FAIL arms.** Both checks are WARN. Promotion to FAIL is a LATER plan, earned once the declaration is in use and the funnel is re-measured — the house warn-first law.
- **No changes to any existing check**, to the daemon, or to the gates. `plan_lint`'s exit code is unaffected by both new checks (WARNs are advisory — `run_check.py`'s `judge_lint` reads the exit code as the channel).
- **No retro-fitting of existing plans.**
- **No memory writes** (sandbox-denied to agents; the Planner records at close).

## Numbers discipline

⚠️ **Measured 2026-08-27 by the Planner; RE-DERIVE each pre-flight — yours supersede and you say so; mismatch on a load-bearing pin → HALT.**

| id | pin | value | anchor/probe |
|---|---|---|---|
| E1 | the seam | `scripts/plan_lint.py:508-547` — the `(f-stanza)` block already parses the Cycle Manifest into `stanza_fields` (key → value, continuation lines folded) and WARNs on missing required fields. Both new checks read that SAME dict; no new parser | read `:508-547` |
| E2 | required-field list | `_STANZA_REQUIRED = ["tier","target","class","reads","writes","open_forks","walks","yields","validation","coherence"]` — `target_class`, `state_space`, `mutants` are NOT in it and must NOT be added (they are conditional, not universal) | `:538-541` |
| E3 | WARN idiom | advisory checks `print(f"(x) WARN: …")` and never append to `results`; only `results.append(("FAIL", …))` moves the exit code | compare `(f)` at `:542` with `(a)` at `:228` |
| E4 | the funnel | 321 Done executables; 28 with a manifest `target:`; 25 `.py`; **12** matching the detector name pattern; **0** declaring `target_class` | the prototype script in the plan body |
| E5 | full suite baseline | **1623 collected** (1622 passed + 1 skipped at exec-575) | `pytest tests/ -q --collect-only \| tail -1` |
| E6 | mutants dir | `knowledge/mutants/` exists and holds `gate_watcher.json` (exec-574/575) | `ls knowledge/mutants/` |

## MUST-PRESERVE

- ⚠️ **`/usr/bin/grep` for ALL probes (`-F` unless a regex is stated); zero-match exits 1 — never `&&`-chain a probe.**
- ⚠️ **Neither new check may alter `plan_lint`'s exit code.** They print WARNs only. Prove it with a probe: a plan that trips BOTH checks must still exit 0 when it has no FAILs.
- ⚠️ **`target_class`, `state_space` and `mutants` stay OPTIONAL stanza fields** — do not add them to `_STANZA_REQUIRED`, or every existing plan starts WARNing about fields it was never asked for.
- ⚠️ **Check (t) is advisory FOREVER** — a name heuristic is invisible when incomplete and must never become a FAIL basis. Say so in its docstring so a later reader cannot promote it by tidying.
- ⚠️ **The 573/575 detector plans are already CLOSED** — this plan does not edit them, and (t) firing on them retrospectively is expected, not a defect.
- ⚠️ **Worktree dispatch; every claim cites file:line; absence claims carry positive controls; EVERY DATE IS A FIXED LITERAL.**

## STEP 1 — DEV (the two checks + tests + the funnel re-measurement)

> **Task A — worktree discipline.** `cd "$(git rev-parse --show-toplevel)" && test -f scripts/plan_lint.py && echo TREE_OK` — HALT unless TREE_OK. Resume probe: `/usr/bin/grep -cF "target_class" scripts/plan_lint.py; true` → 0 = full run; ≥1 = resume at Task D.
>
> **Task B — RE-MEASURE THE FUNNEL FIRST** (E4 is a claim; a warn-first rule shipped on an unverified funnel is the thing this whole arc exists to stop). Run this and paste raw into the dev log:
> ```
> python3 - <<'PY'
> import pathlib, re
> done = sorted(pathlib.Path('knowledge/decisions/Done').glob('executable-*.md'))
> pat = re.compile(r'(check|guard|watch|filter|dedup|stale|detect|valid|lint|verif)', re.I)
> tot=len(done); man=0; py=0; det=[]
> for f in done:
>     t=f.read_text(errors='replace')
>     m=re.search(r'^target:\s*(.+)$', t, re.M)
>     if not m: continue
>     man+=1; tgt=m.group(1).strip()
>     if tgt.endswith('.py'):
>         py+=1
>         if pat.search(pathlib.Path(tgt).name): det.append((f.name, pathlib.Path(tgt).name))
> print(tot, man, py, len(det)); [print(' ', a, '->', b) for a,b in det]
> PY
> ```
> State your four numbers against E4's (321 / 28 / 25 / 12) and say "supersedes" where they differ. If the detector count has moved by more than ±3, STOP and report — the funnel is the justification for shipping this at WARN.
>
> **Task C — add both checks to `scripts/plan_lint.py`**, immediately after the `(f-stanza)` block's field loop so they reuse `stanza_fields` (E1). Recognized detector token is the exact lowercase string `detector`.
> - **(s)** — fires only when `stanza_fields.get("target_class","").strip() == "detector"`. Then: if `state_space` is missing/empty → `print("(s) WARN: target_class=detector but no state_space field — a detector's tests must enumerate its state space from SYSTEM artifacts (SELECT DISTINCT, real filenames, the actual writer), not the author's model; see exec-573 TestPauseStateSpace")`. ⚠️ **The `mutants` condition is deliberately strict, and a plain presence check is NOT enough.** WARN unless `mutants` names a path that EITHER exists on disk OR appears in one of the plan's `**Deposits:**` blocks. A presence-only check would accept the literal word `DEFERRED` — or any prose — and the field would become a box to tick, which is the failure mode this whole arc exists to remove. Message when it fails: `print("(s) WARN: target_class=detector but mutants names no manifest that exists or is promised in Deposits — 'would the suite catch this?' has no mechanical answer; see tools/mutation_check.py (exec-575)")`.
> - **(t)** — fires only when `target_class` is ABSENT/empty AND `target` ends `.py` AND the target BASENAME matches `(check|guard|watch|filter|dedup|stale|detect|valid|lint|verif)` case-insensitively: `print("(t) WARN: target basename looks like a detector but target_class is not declared — declare 'target_class: detector' (and then state_space + mutants), or leave it undeclared deliberately; this heuristic is advisory and cannot decide the question")`.
> - Docstrings on both: (s) states the declaration is authored and only its consequences are mechanized; **(t) states explicitly that a name heuristic is invisible when incomplete and must NEVER become a FAIL basis.**
>
> **Task D — tests in a NEW module `tests/test_plan_lint_detector_checks.py`** — pinned, not a choice. Measured at authoring: `tests/` already holds `test_plan_lint.py` AND `test_plan_lint_bare_constants.py`, the latter being check (r)'s own module, so the house convention is a SEPARATE module per check family and this plan follows it. Clone that file's fixture idiom rather than inventing one. (The Deposits and Scope blocks name this exact path — a branch here would break `deposit_exists`.)
> 1. `test_s_warns_when_detector_omits_state_space` — stanza with `target_class: detector`, `mutants: knowledge/mutants/x.json`, no `state_space` → `(s) WARN` naming state_space; exit code unchanged.
> 2. `test_s_warns_when_detector_omits_mutants` — mirror of 1.
> 3. `test_s_silent_when_detector_declares_both` — both present → NO `(s) WARN`. **The negative control: without it, a check that always warns would pass tests 1 and 2.**
> 4. `test_s_does_not_fire_without_the_declaration` — `target_class` absent entirely → no `(s)` output at all, even with state_space/mutants missing.
> 5. `test_s_warns_on_a_declared_but_absent_mutants_path` — `mutants: knowledge/mutants/nope.json`, path absent from disk AND unmentioned elsewhere in the plan → WARN; and the mirror where the same path IS named in a Deposits block → NO warn.
> 6. `test_t_warns_on_detectorish_name_without_declaration` — `target: tools/foo_check.py`, no `target_class` → `(t) WARN`.
> 7. `test_t_silent_when_target_class_declared` — same target WITH `target_class: detector` → no `(t)` (it defers to the declaration).
> 8. `test_t_silent_on_non_detector_name` — `target: tools/report_builder.py` → no `(t)`.
> 9. **`test_neither_check_changes_exit_code`** — a plan tripping BOTH (s) and (t) with no FAILs exits **0**. The MUST-PRESERVE assertion.
> **Targeted run:** run that module with `-q`; report the `--collect-only` count first, then the pass count. DEV runs NO full suite.
>
> **Task E — dev log** `knowledge/dev-logs/detector-coverage-lint-dev-2026-08-27.md`: the Task-B raw funnel output with the four numbers compared to E4, each pin re-derivation (E1-E6), the targeted-test tail raw.
>
> **Task F — commit** (worktree; message `[<id>] detector-coverage-lint: plan_lint (s)+(t) WARN-only; measured funnel`): `cd "$(git rev-parse --show-toplevel)" && git add scripts/plan_lint.py <the test file> knowledge/dev-logs/detector-coverage-lint-dev-2026-08-27.md && git commit`. Verify `git show --stat HEAD | cat` lists exactly those 3 files.
>
> **Deposits:**
> - `scripts/plan_lint.py`
> - `tests/test_plan_lint_detector_checks.py` (or the existing plan_lint test module — name the one you used)
> - `knowledge/dev-logs/detector-coverage-lint-dev-2026-08-27.md`
>
> **Scope:**
> - `scripts/plan_lint.py`
> - `tests/test_plan_lint_detector_checks.py`
> - `knowledge/dev-logs/detector-coverage-lint-dev-2026-08-27.md`

## STEP 2 — QA (FULL suite + the checks run against REAL plans)

> **Item 1 — full suite.** `cd "$(git rev-parse --show-toplevel)"`; `python3 -m pytest tests/ --tb=short -q 2>&1 | cat | tee knowledge/qa/evidence/detector-coverage-lint-2026-08-27/pytest_full.txt` — 0 failed; derive the count from E5 (1623) plus your new tests.
> **Item 2 — run the REAL lint over REAL plans, raw tails to `probes-raw.txt`:**
> 1. **(t) on a closed detector plan:** `python3 scripts/plan_lint.py knowledge/decisions/Done/executable-573.md 2>&1 | /usr/bin/grep -F "(t) WARN"; true` → expect the WARN (573's manifest declares `target: bellows/tools/gate_watcher.py` and no `target_class`). This is the retrospective fire the plan predicts, not a defect.
> 2. **(t) silent on a non-detector:** pick a closed plan whose manifest `target` is a `.py` NOT matching the pattern — find one with the Task-B script's output — and show `(t) WARN` count 0. ⚠️ If no such plan exists, SAY SO and construct a fixture instead; do not report a vacuous zero from a plan that has no manifest at all.
> 3. **Exit code unaffected:** `python3 scripts/plan_lint.py knowledge/decisions/Done/executable-573.md >/dev/null 2>&1; echo "exit=$?"` → same value as before this plan. Establish "before" from the commit that PRECEDES THIS PLAN'S OWN DEV COMMIT, identified by its `[<id>]` commit tag — never HEAD-relative (the measured cross-terminal interleave class: another terminal's commit can land between your steps and silently redefine `HEAD~1`). Resolve it explicitly: `DEV=$(git log --format='%H %s' | /usr/bin/grep -F "[<id>] detector-coverage-lint:" | head -1 | cut -d' ' -f1)` then `git show ${DEV}^:scripts/plan_lint.py > "$TMPDIR/plan_lint_prev.py"` and run that copy. Paste the resolved sha and both exit codes. `git stash` is forbidden here.
> 4. **(s) end-to-end on a constructed plan:** write a temp plan file declaring `target_class: detector` with neither `state_space` nor `mutants`; run the lint; show BOTH `(s) WARN` lines and `exit=0`.
> 5. **(s) firing on THIS VERY PLAN — show it, do not avoid it:** ⚠️ resolve the plan file by GLOB against the LIVE checkout, never by a hardcoded name: the claimed file is renamed through `in-progress-` and `verdict-pending-` as it runs, and your worktree does not hold it. `P=$(ls /Users/marklehn/Developer/GitHub/bellows/knowledge/decisions/*executable-<id>.md | head -1); echo "resolved: $P"; python3 scripts/plan_lint.py "$P" 2>&1 | /usr/bin/grep -F "(s) WARN"; true` → expect the mutants WARN, because this plan declares `target_class: detector` and ships no mutants manifest. ⚠️ **That WARN is the correct answer and must be recorded as a PASS of the check, not a defect of the plan.** Do not edit the manifest to silence it. If it does NOT fire, the check is broken — HALT and report, because a check that stays quiet on a known-positive case is the vacuous-check class.
> 6. Also confirm the state_space clause does NOT warn for this plan (it declares one), proving (s) discriminates between its two clauses rather than warning wholesale.
> **Item 3 — hygiene + receipt** `knowledge/qa/evidence/detector-coverage-lint-2026-08-27/qa-receipt.md`: numstat vs the DEV commit (3 files); toplevel; reflog `-n 4` → 0 amends; per-item table; **the re-measured funnel numbers stated plainly**; then the Rule 20 block INSIDE a "Verification"-headed section (the 556 placement law).
> **Item 4 — commit the evidence** (message `[<id>] detector-coverage-lint: QA — full suite + real-plan lint probes`): `git add knowledge/qa/evidence/detector-coverage-lint-2026-08-27/ && git commit`; verify exactly 3 files.
>
> ⚠️ **Gate note:** pytest summary named above — the gate parses; no benign override pre-declared.
>
> **Deposits:**
> - `knowledge/qa/evidence/detector-coverage-lint-2026-08-27/pytest_full.txt`
> - `knowledge/qa/evidence/detector-coverage-lint-2026-08-27/probes-raw.txt`
> - `knowledge/qa/evidence/detector-coverage-lint-2026-08-27/qa-receipt.md`
>
> **Scope:**
> - `knowledge/qa/evidence/detector-coverage-lint-2026-08-27/pytest_full.txt`
> - `knowledge/qa/evidence/detector-coverage-lint-2026-08-27/probes-raw.txt`
> - `knowledge/qa/evidence/detector-coverage-lint-2026-08-27/qa-receipt.md`

Rule 20 banner (byte-exact, inside the QA receipt's VERIFICATION section):

```
============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
```

## Drafting Cycle

**Tier:** T1 — two WARN-only checks reusing an existing parsed dict, plus tests; no exit-code change, no existing check touched.

**Walk register:** `bellows/knowledge/research/walk-register-detector-coverage-lint-2026-08-27.md`

**Walks:** walk 0 pinned; **walks 1-4 complete**, genuine sequential five-lens passes — see the register.
**Direction verdict (after walk 1): PROCEED** — declaration-authored / consequences-mechanical held.
- Weak spots:          w1 1 folded (the test module was left as a CHOICE while Deposits hardcoded one path — deposit_exists would have failed); w2 dry; w3 1 folded (the self-lint probe named a filename that is renamed mid-run, in a worktree that does not hold it); w4 dry
- Destruction:         w1 dry; w2 dry; w3 dry; w4 dry
- Vulnerabilities:     w1 1 folded (QA Item 2.3 resolved the "before" state via HEAD~1 — the measured cross-terminal interleave class; now resolved by the plan's own `[<id>]` commit tag); w2 1 folded (⚠️ a presence-only `mutants` check would accept the word DEFERRED, turning the field into a box to tick — and this plan's OWN manifest was written that way); w3 dry; w4 dry
- Integration-record:  w1 dry; w2 dry; w3 dry; w4 dry
- ACID:                w1 dry; w2 dry; w3 dry; w4 dry
**Cold panel: NOT convened, decided with reasoning** — T1 advisory-only lint additions; the 561/565 plan_lint precedent.
**Conformance (§5):** recorded at the freeze from actual runs — see the register's conformance block.
**Closing:** **walk 4 dry, confirming walk 3's residue clear — BAR MET.** Instruction series **3 → 1 → 1 → 0**. Close is MANUAL (CEO-lane verdicts; auto_close false).

## Cycle Manifest
tier: T1
target: bellows/scripts/plan_lint.py
target_class: detector
state_space: declaration-present x consequence-fields-present x target-name-matches — dimensions read from the SYSTEM (the `_STANZA_REQUIRED` list at plan_lint.py:538-541 for field names, the 321 Done/ manifests for the name-pattern population), not from the author's intuition; the two checks' cells are enumerated as tests 1-9 in STEP 1 Task D, including the always-warns negative control (test 3) and the exit-code invariant (test 9)
mutants: NONE — deferred to the follow-up plan (open fork). ⚠️ This plan therefore TRIPS ITS OWN check (s) on the mutants clause, and that WARN is CORRECT, not a defect: this plan genuinely ships a detector with no mutants manifest, and the check exists to say so out loud. QA Item 2.5 must SHOW the warn firing on this plan rather than avoiding it — tuning a declaration until the instrument agrees is the corruption exec-574 taught us to refuse.
class: shop-infra
reads: /Users/marklehn/Developer/GitHub/bellows/scripts/plan_lint.py, /Users/marklehn/Developer/GitHub/bellows/tools/run_check.py, /Users/marklehn/Developer/GitHub/bellows/knowledge/decisions/Done/executable-573.md, /Users/marklehn/Developer/GitHub/bellows/knowledge/mutants/gate_watcher.json
writes: scripts/plan_lint.py, tests/test_plan_lint_detector_checks.py, knowledge/dev-logs/detector-coverage-lint-dev-2026-08-27.md, knowledge/qa/evidence/detector-coverage-lint-2026-08-27/pytest_full.txt, knowledge/qa/evidence/detector-coverage-lint-2026-08-27/probes-raw.txt, knowledge/qa/evidence/detector-coverage-lint-2026-08-27/qa-receipt.md
open_forks: promoting (t) from WARN to FAIL once the declaration is in use and the funnel is re-measured (the warn-first house law — a separate plan, with the re-measurement as its justification); the mutants manifest for plan_lint itself (deferred above); whether `target_class` should carry a closed vocabulary beyond `detector`; thread 25's differential runner
walks: 4
yields: 3, 1, 1, 0
validation: cycle_check=BAR_MET, plan_lint=0_FAIL, fold_check=CLEAN_x1
coherence: N/A
