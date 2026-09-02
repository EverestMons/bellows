# bellows — diagnostic: the PT/DC enforcement census — every rule, checklist item, wrap step, trigger, lens sub-question and §2.7 bullet joined to the check that enforces it, the corpus weight it carries, and its home under a by-enforcer reorganization (deciding nothing)

**Date:** 2026-09-02 | **Project:** bellows | **Tier:** Small | **Dispatch Mode:** bellows | **cycle_tier:** T1 | **Test Scope:** none (read-only diagnostic; writes one research doc and the instrument's output files) | **Execution:** Step 1 (DIAGNOSTIC) | **pause_for_verdict:** always | **known_failures:** 0 | **Priority:** 2

**auto_close:** false

**Slug:** `pt-dc-census-2026-09-02`

**Depends on:** the CEO, 2026-09-02 (afternoon): *"why planner template cannot be run like a bellows system of gates and tests to ensure template is upheld"* → the by-enforcer shape agreed (*"I agree with this shape. Let's draft it now"*): one PLAN STANDARD (DRAFTING_CYCLE plus the Template's rules and checklist, each rule tagged with its enforcer or marked unenforced), one small PLANNER ROLE document, the execution models with bellows; `Done/diagnostic-100014.md` (the clone origin and the newest same-class plan: a committed instrument with a positive control, questions answered from data with denominators, a table that decides nothing); the instrument `knowledge/qa/evidence/pt-dc-census-2026-09-02/census.py` (committed `348b736` with its walk-0 summary and its zero-population control); threads 67, 72, 74 (the DC §2.7 refactor already underway — this census is their input), 76 (Gate 2 tranche two lands before any reorganization), 91 (the memory destination in step 7 — its legitimate scope is this census's conversational set). Walk register: `/Users/marklehn/Developer/eluvian-governance/governance/knowledge/research/walk-register-pt-dc-census-2026-09-02.md`.

**Tier computed, not judged (§1):** **T-7 fires** (a diagnostic whose findings a reorganization plan will build on) and **T-8** (a clone by kind of 100014). T-1 no (one write set: the evidence dir and one research doc). T-2/T-3/T-5/T-6 no (read-only over doctrine; writes nothing into it). → **T1: five-lens walk, no panel.**

## CEO Context

The Template and the Drafting Cycle overlap on the plan ARTIFACT — anchors, pins, probes, post-conditions, positive controls, clones — and the checkers that enforce doctrine do not respect the file boundary: `plan_lint` cites DRAFTING_CYCLE nine times and Template rules three times; the step gates cite Template rules twelve times; `cycle_check` names neither. A rule becomes a gate the moment its act produces an artifact a checker consumes; the rules that produce no artifact were, until today, routed to the Planner's memory — a fallback for exactly the rules with no consumer. The CEO retired that fallback (thread 91). This census measures the map the reorganization needs: for every unit of doctrine, WHICH check enforces it, what CORPUS weight it carries, and which HOME it takes under the by-enforcer split. It decides nothing.

⚠️ **The deposit act IS the release.** The depositor assigns this plan `app-feature` (measured on its write set) and auto-clears that class — the daemon claims within seconds of the `ready-` file appearing (100014 was claimed inside its staging compound's six-second wait). So the frozen draft is committed and receipted today and STAGED only after plan C closes — eighth in the release order. ⚠️ **The census runs on PLANNER_TEMPLATE v4.97** — plan `gate2-pt-w28-a` lands Rules 103–106 tonight before this plan is released; the instrument enumerates from the file, so the rule population becomes 106 and P2/P7 are re-derived at claim (the Planner's walk-0 numbers below are v4.96's, stated as such).

## Numbers discipline — measured 2026-09-02 by the Planner (bellows `348b736`; PT v4.96 `c471d3afee3f9094`; DC v2.23 `3a84137ed3669de1`); the agent re-derives each and states both on a mismatch

| id | pin | value | how |
|---|---|---|---|
| P1 | the instrument | `census.py` sha `9c52011935a17137`, committed with `summary-walk0-2026-09-02.txt` and `control-empty-pt.txt` beside it | `shasum -a 256 knowledge/qa/evidence/pt-dc-census-2026-09-02/census.py \| cut -c1-16` |
| P2 | the population (v4.96) | **224** units — rules 102 · checklist 33 · wrap steps 8 · triggers 8 · lens sub-questions 21 · §2.7 bullets 52; at v4.97 the rules become **106** (228 units) | the instrument's first summary line |
| P3 | the citation floor (v4.96) | rules cited by a checker **8** of 102 · checklist **0** of 33 · wrap steps **4** of 8 · triggers **1** of 8 · sub-questions **0** of 21 · §2.7 bullets checker-cited **0**, section-cited (`§2.7` named somewhere in code) 52 of 52 | the per-kind summary lines |
| P4 | the corpus weight | rules corpus-cited **22** (18 of them uncited by any checker) · checklist 9 (9 uncited) · wrap steps 3 (0 uncited) · triggers 1 · sub-questions 4 (4 uncited); `LESSONS.md` at 401 entries carries 94 lines naming `Rule N` and 42 naming a `§L.n` unit | the per-kind lines; `grep -c` on the register |
| P5 | the controls | positive: `rule-20` → `gates.py;scripts/plan_lint.py`, corpus 47; `rule-26` → `gates.py;verdict.py`, corpus 6; negative: `rule-63` → no checker, corpus 0; `wrap-7` → no checker (the sweep itself is unchecked — `wrap_check` verifies its Lessons-swept LINE, not the sweep); zero-population: an empty PT → exit 2 "a population parsed to zero units" | the instrument run on the live files and on `control-empty-pt` |
| P6 | the checker surfaces (the CALLEE enumeration for Q-2) | `plan_lint` 18 lettered check ids (some multi-part: 38 distinct messages) · `gates.py` 11 `_gate_` functions · `wrap_check.py` 7 arms · the depositor's holds (class, collision, validation mismatch) · `cycle_check` (the bar, the asserts, the manifest) · `fold_check` · `propagation_check` · `walk_register_lint` · the register pre-commit hook · the align/debt/arm/stop hooks · `RULE_20_SELF_CHECK_BLOCK.md` · `tools/mutation_check.py` | `grep -c '^def _gate_' gates.py`; `grep -oE '"\([a-z][0-9]?\)' scripts/plan_lint.py \| sort -u \| wc -l`; `grep -oE '\[[0-9][a-z]?/[a-z_]+\]' hooks/eluvian/wrap_check.py \| sort -u` |
| P7 | code files the instrument scans | 56 (`.py` under the bellows root, `scripts/`, `hooks/eluvian/`, `tools/`, tests excluded) | the summary's second line |

## MUST-PRESERVE

- ⚠️ **READ-ONLY except the deposits.** The documents are read by ABSOLUTE path under `/Users/marklehn/Developer/eluvian-governance/` (another repo — never `cd` into it; `git -C` for its shas, read-only). The instrument writes only into your evidence dir.
- ⚠️ **A citation is the FLOOR, not the finding.** The instrument finds units a checker NAMES. A check can enforce a rule without naming it (plan_lint's Deposits-block check enforces Rule 26's form; the QA test gate enforces the header's `known_failures`) and can name a rule it does not enforce. Q-2's map is built by READING each checker from the callee side — every check enumerated, then joined to the unit(s) it actually tests — and the join is what the report carries. Where the reading and the citation disagree, say which and why.
- ⚠️ **Every count carries its denominator and the predicate that produced it.** "18 uncited" is meaningless without "of the 22 corpus-cited rules, by the `Rule N` predicate over `LESSONS.md`".
- ⚠️ **"Unknown" is an acceptable answer.** A unit whose enforcement cannot be settled by reading the checker, or whose home is genuinely arguable, goes in an UNRESOLVED bucket, counted, never forced — a forced classification is a finding the reorganization plan would act on.
- ⚠️ **Every absence claim carries a positive control** (P5). Run the instrument on the live files and confirm P5's rows before believing any zero.
- ⚠️ **`/usr/bin/grep -F` for every literal probe; `--` before dash-leading patterns; a zero-count grep exits 1 — never `&&`-chain a probe.** zsh: explicit arrays for any list you iterate. **No pytest run is required or wanted** — every row is a measurement over document and code TEXT and the instrument's output.

## Drafting Cycle

**Tier:** T1 — T-7 (a diagnostic a reorganization plan builds on), T-8 (a clone by kind of 100014) fire; no panel.

**Walk register:** /Users/marklehn/Developer/eluvian-governance/governance/knowledge/research/walk-register-pt-dc-census-2026-09-02.md

**Walk 0 (context pin, measured):** the two documents' sizes, sections and cross-references; the checkers' citation forms counted across 56 code files; the instrument written and EXECUTED on the live documents and code (224 units by kind; the citation floor per kind; the corpus weight per kind), with its three controls (two positive units, one negative, the zero-population exit) — three instrument defects found by the controls and fixed before commit; the checker surfaces enumerated (18 lint ids, 11 gates, 7 wrap arms, the depositor's holds); the clone-diff against 100014 and its register; the consumer dry-run (§2.0) — class assigner `app-feature` (auto-clears: the deposit is the release), extractor four paths, the report first.

**Direction verdict (after walk 1): PROCEED.** Tested: the premise (the checkers do not respect the file boundary and the memory fallback covered exactly the rules with no consumer — both measured), the mechanism (a committed instrument for the floor, a callee-side reading for the map, a home rule applied mechanically, denominators throughout, deciding nothing), the scope (no doctrine written; the reorganization is a later T2; tranche two lands first).

**Walks:**
- Weak spots:          w1 2 folded — instruction 2 / record 0 (the commit's pathspec was a placeholder — spelled out; the plan did not say that its class auto-clears, so a staging tonight in the wrong order would have run it at once — the deposit-is-the-release fact stated with its measurement)
- Destruction:         w1 dry — read-only over doctrine; writes only its four deposits; the control runs in `/tmp`, never in the evidence dir
- Vulnerabilities:     w1 dry — absolute paths into the other repo, `git -C` read-only; the instrument's exit read directly; the version found stated and the population re-derived either way
- Integration-record:  w1 dry — the manifest is the emitter's, spliced at the freeze; the class the assigner measured
- ACID:                w1 dry — one commit by explicit pathspec at the end of the single step; a HALT leaves nothing landed
- **Walk 1 total: 2 findings, 2 folded — instruction 2 / record 0; 0 of 2 fold-introduced.**

- Weak spots:          w2 dry — instruction 0 / record 0 — the two folded sites re-read; Q-0 through Q-7 read as an agent would run them (the control first, the version stated, the callee-side enumeration before the join); the Cycle Log covered
- Destruction:         w2 dry — instruction 0 / record 0 — unchanged
- Vulnerabilities:     w2 dry — instruction 0 / record 0 — unchanged
- Integration-record:  w2 dry — instruction 0 / record 0 — the manifest emitted at the freeze and spliced; `propagation_check` recorded as it ran (exit 2 — this plan's pin table is in the form thread 90 repairs)
- ACID:                w2 dry — instruction 0 / record 0 — unchanged
- **Walk 2 total: 0 findings — instruction 0 / record 0, ALL FIVE LENSES DRY.** Instruction series 2 → 0.

**Conformance (§5):** first run at walk 0 (on v0) and re-run after walk 1's folds and at the freeze: `plan_lint` exit 0 / 0 FAIL at the faithful mirror — expected WARN set (o2)×4 (worktree-relative deposits); `cycle_check` BAR_MET; `fold_check` re-baselined at each intended change with a note; **`propagation_check` NOT RUN — exit 2 ("no symbol declarations parsed"): this plan's pin table has no bold `**VALUE**` rows; the class it detects is unmeasured here (thread 90).**

**Closing:** ✅ **BAR MET — walk 2 dry (all five lenses) after walk 1's two folds; T1, no panel owed, none convened.** Substrate present (the register's rows entered at each phase from captured output and committed at the freeze; `fold_check` baseline). The closing-record re-read (§2.7) ran against this block, the register and the emitted manifest at the freeze.

**Fold-and-deposit exactly once.**

## Cycle Manifest
tier: T1
target: knowledge/research/pt-dc-census-2026-09-02.md
class: app-feature
reads: /Users/marklehn/Developer/eluvian-governance/PLANNER_TEMPLATE.md, /Users/marklehn/Developer/eluvian-governance/DRAFTING_CYCLE.md, /Users/marklehn/Developer/eluvian-governance/LESSONS.md, /Users/marklehn/Developer/bellows/gates.py, /Users/marklehn/Developer/bellows/depositor.py, /Users/marklehn/Developer/bellows/scripts/plan_lint.py, /Users/marklehn/Developer/bellows/scripts/cycle_check.py, /Users/marklehn/Developer/bellows/hooks/eluvian/wrap_check.py, /Users/marklehn/Developer/bellows/knowledge/qa/evidence/pt-dc-census-2026-09-02/census.py, /Users/marklehn/Developer/forge_lessons/lessons-forge.db
writes: knowledge/research/pt-dc-census-2026-09-02.md, knowledge/qa/evidence/pt-dc-census-2026-09-02/units.csv, knowledge/qa/evidence/pt-dc-census-2026-09-02/enforcers.csv, knowledge/qa/evidence/pt-dc-census-2026-09-02/summary.txt
open_forks: the reorganization itself (a T2 doctrine plan on the standard / role / execution-model split — after tranche two and this census); whether the instrument's citation floor should become a standing wrap-check arm ("every new Template rule names its enforcer or is marked unenforced"); the CONVERSATIONAL set as thread 91's memory scope
walks: 2
yields: 2, 0
validation: cycle_check=BAR_MET, plan_lint=0_FAIL, fold_check=PASS
coherence: 2/2 walks have register rows


---

## STEP 1 — DIAGNOSTIC: seven questions, one exercised instrument

> **FIRST — post a short visible chat message (1–2 sentences).** Do NOT rename this file. You are the bellows Diagnostic agent. `cd "$(git rev-parse --show-toplevel)" && [ -f knowledge/qa/evidence/pt-dc-census-2026-09-02/census.py ] && echo TREE_OK` — HALT unless TREE_OK. `GOV=/Users/marklehn/Developer/eluvian-governance; EV="$(pwd)/knowledge/qa/evidence/pt-dc-census-2026-09-02"; BPY=/Users/marklehn/Developer/bellows/.venv/bin/python` — re-derive per compound.
>
> **Q-0 — Does the instrument fire?** Re-derive P1. Run the zero-population control (`: > /tmp/ptdc-empty.md; "$BPY" "$EV/census.py" /tmp/ptdc-empty.md "$GOV/DRAFTING_CYCLE.md" "$GOV/LESSONS.md" scripts --out /tmp/ptdc-empty-out; echo "exit=$?"` — exit 2, the message quoted; scratch, never inside the evidence dir). Then the live run: `"$BPY" "$EV/census.py" "$GOV/PLANNER_TEMPLATE.md" "$GOV/DRAFTING_CYCLE.md" "$GOV/LESSONS.md" . scripts hooks/eluvian tools --out "$EV"; echo "exit=$?"` → exit 0; it writes `units.csv` and `summary.txt` there — both are deposits. Confirm P5's rows in `units.csv` (`rule-20`, `rule-26`, `rule-63`, `wrap-7`) before any other count is believed. State `shasum -a 256 "$GOV/PLANNER_TEMPLATE.md" "$GOV/DRAFTING_CYCLE.md"` and the Template's `**Version:**` line — v4.97 expected; if v4.96, say so and continue (the population is then 224, not 228).
>
> **Q-1 — The population, dated.** Re-derive P2 from `summary.txt`. State the six kinds with counts, the Template version, and the delta from the Planner's v4.96 pin (the four new rules by id and title, read from `units.csv`).
>
> **Q-2 — The enforcement map, from the CALLEE side.** Enumerate every check surface in P6 by reading its source: for `plan_lint`, each lettered check and what it tests; for `gates.py`, each `_gate_` function and what it reads; `cycle_check`'s asserts and verdicts; `fold_check`, `propagation_check`, `walk_register_lint`; the depositor's three hold reasons; `wrap_check`'s seven arms and the four hooks; the Rule 20 block; `mutation_check`. For EACH check write one row into `"$EV/enforcers.csv"` — `check_id, file, what_it_tests, units_enforced (ids), units_named (ids from the instrument), agreement (named=enforced | names-more | enforces-more | neither)`. Then join back: for every unit in `units.csv`, `enforced_by` = the checks whose reading names it. Report per kind: enforced (by reading) / cited-only / neither, with denominators; and the disagreement count between the citation floor and the reading, both directions, each named.
>
> **Q-3 — The unenforced set, classified — the deciding question, and it is a JUDGMENT stated as one.** For every unit with no enforcer by reading: **MECHANIZABLE** — name the ARTIFACT the rule's act produces or could be made to produce, and the existing check that could consume it (a `run_check` mode, a register field, a wrap-check arm, a lint letter, a gate) — or **CONVERSATIONAL** — the act produces no artifact and none can be made without changing what the rule is for (state why in one clause) — or **UNRESOLVED**. Counts per class per kind. The CONVERSATIONAL set is the legitimate scope of the Planner's memory (thread 91); list it whole.
>
> **Q-4 — The corpus weight.** Re-derive P4. For every unit: its corpus citation count; then the ranked list of the top twenty units by corpus weight with their Q-2 status — the mechanization backlog's natural order is "corpus-cited and unenforced, most-cited first". State the in-population caveat: a rule cited in the corpus is one whose violation was RECORDED, which measures recording as much as violation.
>
> **Q-5 — The home map (the reorganization's input).** For every unit, its home under the by-enforcer split, by ONE rule applied mechanically: **STANDARD** if any check enforces it (Q-2) or could (Q-3 MECHANIZABLE); **ROLE** if CONVERSATIONAL; **EXECUTION-MODEL** if the unit lives in the Template's Bellows or Manual execution sections regardless of enforcement (state those two sections' line ranges); UNRESOLVED otherwise. Counts per home per source document; the units that would MOVE (a Template rule to the standard beside DC; a DC bullet that is conversational). Name the §2.7 bullets that duplicate a Template rule on the same subject (anchors, pins, probes, post-conditions, positive controls, clones — the pairs), by id, with the sentence from each — the pairs are what a merge folds.
>
> **Q-6 — What the three open DC threads cover.** Read threads 67, 72, 74 from `tuyere` (`/Users/marklehn/Developer/tuyere/.venv/bin/python -m tuyere.threads show <id>`, read-only) and state which units each names; whether the by-enforcer reorganization would supersede or fold each; and which Gate-2-accepted proposals (thread 76's remaining eight — read their `target_artifact` and `suggested_action` from the lessons DB READ-ONLY: `sqlite3 -readonly /Users/marklehn/Developer/forge_lessons/lessons-forge.db`) would land in a unit that moves.
>
> **Q-7 — The table, deciding nothing.** `units.csv` extended with the Q-2 `enforced_by`, Q-3 class and artifact, Q-4 weight, Q-5 home; `enforcers.csv`; `summary.txt`; and the report `knowledge/research/pt-dc-census-2026-09-02.md` carrying Q-0 through Q-6 with every count's denominator and predicate, the UNRESOLVED buckets, the top-twenty backlog, the pairs, and NO recommendation column — the reorganization plan's Planner and the CEO decide.
>
> **Deposits:**
> - `knowledge/research/pt-dc-census-2026-09-02.md`
> - `knowledge/qa/evidence/pt-dc-census-2026-09-02/units.csv`
> - `knowledge/qa/evidence/pt-dc-census-2026-09-02/enforcers.csv`
> - `knowledge/qa/evidence/pt-dc-census-2026-09-02/summary.txt`
>
> **Scope:**
> - `knowledge/research/pt-dc-census-2026-09-02.md`
> - `knowledge/qa/evidence/pt-dc-census-2026-09-02/units.csv`
> - `knowledge/qa/evidence/pt-dc-census-2026-09-02/enforcers.csv`
> - `knowledge/qa/evidence/pt-dc-census-2026-09-02/summary.txt`
>
> **Commit:** `git add knowledge/research/pt-dc-census-2026-09-02.md knowledge/qa/evidence/pt-dc-census-2026-09-02/units.csv knowledge/qa/evidence/pt-dc-census-2026-09-02/enforcers.csv knowledge/qa/evidence/pt-dc-census-2026-09-02/summary.txt && git commit -m "[<id from your plan filename>] diag: PT/DC enforcement census — <N> units, enforced/mechanizable/conversational by reading, corpus weight, the by-enforcer home map" -- knowledge/research/pt-dc-census-2026-09-02.md knowledge/qa/evidence/pt-dc-census-2026-09-02/units.csv knowledge/qa/evidence/pt-dc-census-2026-09-02/enforcers.csv knowledge/qa/evidence/pt-dc-census-2026-09-02/summary.txt`. `git status --short` → empty. STOP.
