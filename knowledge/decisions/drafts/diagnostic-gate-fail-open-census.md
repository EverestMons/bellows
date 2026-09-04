# bellows — diagnostic: EVERY GATE'S FAIL-OPEN PATHS — enumerate each check's inputs, find every path where missing or malformed input yields a PASS, and price fail-closed against the live corpus

**Date:** 2026-09-04 | **Project:** bellows | **Tier:** Small | **Dispatch Mode:** bellows | **cycle_tier:** T1 | **Test Scope:** none (read-only diagnostic — the instrument is new code with no consumers; this step deposits raw output as `.txt` evidence, which `qa_test_result` will refuse to certify having no pytest summary to parse: the pre-declared benign gate failure of the gate note below) | **Execution:** Step 1 (DIAGNOSTIC) | **pause_for_verdict:** always | **known_failures:** 0

**auto_close:** false

**Depends on:** tuyere thread 119 (the CEO ruling this prices) and threads 114, 116, 118 (three of the four measured instances). Clone origin: `Done/diagnostic-100032.md` — same kind, same read-only contract, one Item per question; closed 2026-09-03.

## What this decides

**Nothing.** ⛔ **PT Rule 82 — price before build.** The CEO has ruled that gates are not optional; this measures how far the shop is from that today and what closing the gap would cost. It recommends no change and chooses no fix.

## Why this exists

CEO ruling, 2026-09-04 (thread 119): *"I don't want there to be optional gates, only a record of pass/fail… so that drafting cycle is a confirmation of a validation process, not just an optional suggestion."*

⚠️ **Four instances were found INCIDENTALLY in three days**, each a check returning a confident answer when its input is missing or malformed. None was sought; all four surfaced while doing other work. **That is why a census is warranted: the population size is unknown, and incidental discovery at that rate implies it is not four.**

| thread | check | the fail-open path |
|---|---|---|
| 114 | `wrap_check` `[4/memory]` | `if "class:" not in _head` — a substring over 600 bytes; accepts `class: banana` |
| 116 | `gates._gate_is_qa_step` | declares `[2]` malformed, silently falls back to keyword detection; right only when a step is titled "QA" |
| 118 | `plan_lint` (c) | `qa_steps: none` is a truthy STRING, so declaring NO QA steps demands a QA banner |
| — | `cycle_check` manifest check | `if stored is not None` — no parseable stanza, no check |

⛔ **The fourth is this author's own, shipped the day before as plan 100033**, and it misses the failure that motivated it: `halted-executable-100031` yields `stored=None` and is SKIPPED, while `diagnostic-100032` (the lesser failure) is caught.

| # | pin | value | how to re-derive |
|---|---|---|---|
| P1 | the ruling | thread 119, 2026-09-04 — no optional gates; a pass/fail record; the cycle confirms a validation process | read thread 119 |
| P2 | ⛔ the shipped gate's skip path | `cycle_check.py` — `if verdict == "BAR_MET": stored = _manifest_validation_keys(text); if stored is not None and not MANIFEST_VALIDATION_KEYS.issubset(stored): verdict = "CONTINUE"` | read the block; re-derive its line number |
| P3 | ⛔ it misses its own motivating case | `_manifest_validation_keys` on `halted-executable-100031.md` → **None** (SKIPPED); on `Done/diagnostic-100032.md` → `{cycle_check, fold_check, plan_lint}` (CAUGHT) | call the function on both files |
| P4 | ⛔ the boundary's justification does not hold | the plan said a stanza-less plan is "check (f)'s business". Measured: `plan_lint` on `100031` emits **5** `(f)` WARNs and **exit 0, zero FAILs** | run `plan_lint` on that file, read exit and FAIL count |
| P5 | two kinds of optional | **in code** (a skip path) and **in practice** (never invoked). `propagation_check` is recorded in **18%** of 164 registers, and this Planner ran it **zero** times across three cycles on 2026-09-03 | `tools/battery_census.py`; the 100032 research note |
| P6 | the legitimate fail-open | `wrap_check.py` — *"Committed files are exempt until touched — gradual backfill by design; the first post-ship wrap must not detonate."* A declared grace, though with no expiry | read the comment above the `[4/memory]` class check |
| P7 | corpus scale (why fail-closed is not free) | `knowledge/decisions/Done/` carries **546** plans; 81 have a `validation:` line; **13** are compliant under the current 4-key gate | count them |
| P8 | ⛔ the population's SCALE, and how it is discoverable | each module carries its own identifier convention, measured 2026-09-04: `plan_lint` **22** check letters · `gates.py` **11** `_gate_*` functions · `depositor` **9** `_hold(path, "...")` reasons · `cycle_check` **8** verdict strings · `wrap_check` **7** `[n/name]` steps · `walk_register_lint` **6** `STATUS_*` constants. **≈63 checks.** ⚠️ Sizes re-derived at execution; the conventions, not the counts, are the finding | grep each convention per module |
| P9 | in-flight | re-derive at execution | `sqlite3 lifecycle.db …` |

## The questions

⛔ **Answer each from the instrument's output, never from prose judgement.** An unanswerable question is a FINDING; name it and say why.

> **Q1 — What is the full gate population?** Enumerate every check that can refuse, hold, warn or fail: `gates.py` step gates, `plan_lint` checks (a)–(v), `cycle_check`'s verdict arms, `fold_check`, `propagation_check`, `walk_register_lint`, `mutation_check`, `wrap_check`'s numbered steps, and the depositor's hold reasons. ⛔ **Derive the list mechanically from the code, not from doctrine's description of it** — the four known instances were all found where a check's behaviour and its description disagreed.
>
> **Q2 — For each check, what are its INPUTS and what happens when each is missing, empty, or malformed?** Build the truth table. ⚠️ "Malformed" must include the shapes actually seen in the corpus (a YAML list where an int was expected, the string `none`, an unparsed placeholder), not invented ones.
>
> **Q3 — Which paths yield a PASS on missing or malformed input?** This is the fail-open census and the headline number. Report per check, with the exact conditional.
> ⛔ **PRIORITISE BLOCKING CHECKS.** The ruling is about gates, and a check that can only WARN is already optional by construction — so a fail-open path in a blocking check is strictly worse than one in an advisory. Measured 2026-09-04, blocking emission sites: `gates.py` **24** · `wrap_check` **17** · `plan_lint` **9** · `depositor` **9** · `cycle_check` **6** — **≈65**. Answer Q3 for every blocking check FIRST and completely; cover advisories only after, and say plainly if they were not reached. ⚠️ An advisory's fail-open path is still a finding — thread 118's `(c)` is advisory and still pressures an author into fabricating evidence — but it is not what the ruling is about.
>
> **Q4 — Which checks are optional IN PRACTICE?** Per tool, invocation rate across the committed register corpus (**P5**) and the `Done` corpus (**P7**) — ⛔ re-derive both sizes at execution rather than trusting any figure written here; both grow. ⚠️ A gate nobody runs is as optional as one that skips; both count against the ruling.
>
> **Q5 — Is there a pass/fail RECORD at all?** For each check, can a reader of a closed plan determine whether it ran and what it said? The manifest's `validation:` line covers four tools; what covers the rest? ⚠️ **This is the question closest to the ruling's actual ask** — "only a record of pass/fail" presumes a record exists.
>
> **Q6 — What would fail-closed COST, per check?** For each fail-open path, how many of the `Done` plans (**P7**) and registers (**P5**) would fail if the default flipped — sizes re-derived at execution. ⛔ Report the blast radius per check, not in aggregate — a check with radius 3 and one with radius 500 are different decisions.
>
> **Q7 — Which fail-open paths carry a DECLARED grace, and which are silent?** P6 shows one check that states its permissiveness and why. How many others do? ⚠️ A declared, expiring grace and a silent default are different things and must not be counted together.

## Drafting Cycle

**Tier:** T1 — T-3 fires (the instrument runs where plans are drafted). **T-6 does NOT fire**: read-only; writes no doctrine, no template, no gate, no specialist contract. ⚠️ It READS every gate, which is not the same as editing one — stated because this plan's subject is gates and the trigger is about editing them. T-8 not fired: clone by kind of `Done/diagnostic-100032.md`.
**Walk register:** `/Users/marklehn/Developer/eluvian-governance/governance/knowledge/research/walk-register-gate-fail-open-census-2026-09-04.md`
**Walks:** 2 (walks 0–2 complete).
- Weak spots:          w0 dry; w1 1 folded — instruction 1 / record 0; w2 1 folded — instruction 1 / record 0.
- Destruction:         w0 dry; w1 1 folded — instruction 1 / record 0; w2 dry.
- Vulnerabilities:     w0 dry; w1 1 folded — instruction 1 / record 0; w2 1 folded — instruction 1 / record 0.
- Integration-record:  w0 1 folded — instruction 1 / record 0; w1 dry; w2 dry.
- ACID:                w0 dry; w1 dry; w2 dry.
**⛔ The battery ran at EVERY walk, and earned it twice.** `propagation_check` at walk 0 found the corpus sizes restated as bare numerals in three instruction sites while both are declared pins (10 → 4 after the fold). `fold_check` at walk 1 caught the fold itself introducing a `plan_lint` (v) WARN — `APPEARED:`, found by the tool, not by reading. ⚠️ This is the detector this Planner ran ZERO times across three cycles on 2026-09-03.
**⚠️ Walk 2 found the author committing this diagnostic's own subject while writing it:** two probes disagreed on the advisory count (45 versus 0) because one shared pattern was applied across modules that do not share an emission form.
**Closing:** NOT CLOSED at walk 2 — yields 1, 3, 2; 1 fold-introduced of 6 (17%), caught within its own walk.

## Cycle Manifest

*(to be EMITTED at BAR_MET with `cycle_check --emit-manifest` — ⛔ **do not hand-type this stanza**, and ⛔ **emit BEFORE claiming closure**: emitting while a closure claim stands records the escalation into `validation:` itself, measured 2026-09-04.)*

## STEP 1 — the census (read-only; decides nothing)

> **Scope:**
> - `tools/gate_failopen_census.py`
> - `/Users/marklehn/Developer/eluvian-governance/governance/knowledge/research/gate-fail-open-census-2026-09-04.md`
> - `knowledge/development/dev-log-gate-fail-open-census-2026-09-04.md`
>
> ⚠️ **TWO REPOSITORIES.** Reach governance by absolute path with `git -C "$GOV"`, never `cd`; commit it by **EXPLICIT PATHSPEC** — this plan's own walk register lives there and will be dirty, so a bare `commit -a` sweeps it in. ⛔ Commit bellows LAST.
>
> **Item 1 — re-derive P1–P9 and HALT on mismatch.** ⛔ Re-derive P2's line numbers by grep, never from this plan — `cycle_check.py` gained 34 lines on 2026-09-04 and every pin into it has already moved once.
>
> **Item 2 — build `tools/gate_failopen_census.py`.** ⛔ **Derive the check inventory from the CODE, by each module's OWN identifier convention** (P8), not by parsing conditionals — AST analysis of control flow is overreach and would produce a result nobody can audit. The conventions are: `plan_lint`'s `# (x)` comment letters, `gates.py`'s `_gate_*` function names, `depositor`'s `_hold(path, "reason")` literals, `cycle_check`'s verdict strings, `wrap_check`'s `[n/name]` step tags, `walk_register_lint`'s `STATUS_*` constants. ⛔ **Emission forms DIFFER PER MODULE — derive them per module, never by a shared pattern.** Measured: `plan_lint` uses `results.append(("FAIL", ...))`, `gates.py` uses `failures.append`, `depositor` uses `_hold(path, "reason")`, `wrap_check` uses `fails.append`, `cycle_check` returns verdict strings. ⚠️ Two probes written by this author during walk 2 disagreed with each other on the advisory counts (45 versus 0) precisely because one shared pattern was applied across modules that do not share one — the same defect this diagnostic exists to find, committed while looking for it. ⛔ Read docstrings LAST and only to compare — all four known instances are cases where behaviour and description disagreed, so a description is a hypothesis to test, never evidence. ⚠️ Where a check's fail-open path cannot be determined statically, **exercise it**: construct the missing/malformed input and record what the check actually returns. A static reading that cannot be exercised is reported as UNVERIFIED, never as a pass.
>
> **Item 3 — Q1: the gate population**, enumerated mechanically with each check's module and identifier.
>
> **Item 4 — Q2: the input truth table** per check, using malformed shapes drawn from the CORPUS (a YAML list for an int, the string `none`, an unparsed placeholder), not invented ones.
>
> **Item 5 — Q3: the fail-open census** — every path yielding a PASS on missing or malformed input, with its exact conditional quoted. The headline number.
>
> **Item 6 — Q4: optional in practice** — invocation rates across the register corpus (P5) and the `Done` corpus (P7), per tool, both sizes re-derived at execution.
>
> **Item 7 — Q5: is there a pass/fail record?** Per check, whether a reader of a closed plan can tell it ran and what it said.
>
> **Item 8 — Q6: blast radius of fail-closed**, per check, against the live corpus. ⛔ Per check, never aggregated.
>
> **Item 9 — Q7: declared graces versus silent defaults**, counted separately.
>
> **Item 10 — deposit the research note** with a coverage statement: which checks were verified by exercise, which only statically, and which could not be assessed.
>
> **Item 11 — dev-log**, recording the inventory method and every check whose behaviour disagreed with its description.
>
> **Item 12 — commit** (message tagged with the plan id); record `numstat` — **TWO commits in two repos**: 1 governance, 2 bellows.
>
> ⚠️ **Pre-declared advisory: `plan_lint` (v) fires here as a FALSE POSITIVE.** Step 1's prose uses "test" in the sense of *examine a hypothesis*, not *run pytest*; (v) keyword-matches and warns that the step "mentions tests but declares no test scope". The declaration is correct as written — `test_scope: none`, this is a read-only diagnostic that runs no suite. ⛔ **The wording is NOT changed to dodge the check.** Rewording prose so a keyword check falls silent is the token-gaming class the corpus records, and it would leave the check's real limitation undocumented. Declared here so the WARN reads as known, and so (v)'s negation-blindness has one more recorded instance (thread 102's neighbourhood).
>
> ⚠️ **Pre-declared benign gate failure.** `test_scope` is `none` and this step deposits raw output as `.txt`, so `_gate_qa_test_result` finds no pytest summary and FAILs. Expected, named here, overridden by the Planner with reference to this note — the 100032 precedent, and the case `plan_lint` check (v) exists to make authors declare.
>
> **Deposits:**
> - `/Users/marklehn/Developer/eluvian-governance/governance/knowledge/research/gate-fail-open-census-2026-09-04.md`
> - `bellows/knowledge/development/dev-log-gate-fail-open-census-2026-09-04.md`
>
> **Post-conditions:** every check in the inventory has an input truth table; every fail-open path quoted with its exact conditional; each blast radius stated per check against the live corpus; declared graces counted separately from silent defaults; every check assessed only statically marked UNVERIFIED rather than passed; ⛔ **no recommendation and no decision anywhere in the note** — this diagnostic prices, it does not choose.
