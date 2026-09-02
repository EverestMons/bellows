# bellows — executable: propagation_check reads the pin table every plan actually writes — the plain-backtick and row-id forms, hex and dates excluded — and its NOT-RUN state becomes loud: a run_check mode, a manifest field, and a tier-2 suite over the corpus's own cell forms (thread 90)

**Date:** 2026-09-02 | **Project:** bellows | **Tier:** Small | **Dispatch Mode:** bellows | **cycle_tier:** T1 | **Test Scope:** full (the new `tests/test_propagation_check.py` and `tests/test_run_check.py` targeted first, then the whole bellows suite in the worktree) | **Execution:** Step 1 (DEV) → Step 2 (QA) | **qa_steps:** 2 | **pause_for_verdict:** always | **known_failures:** 0 | **Priority:** 2

**auto_close:** false

**Slug:** `propagation-check-pin-forms-2026-09-02`

**Depends on:** the CEO, 2026-09-02 ("Let's draft this up now so we can save it"); tuyere thread 90; `Done/…` the `checker-defects-2026-09-02` plan (HELD today — the clone origin by kind: a checker fix with committed fixtures, a corpus canary, a tier-2 state space and a kill map; this plan runs AFTER it closes because both edit `scripts/cycle_check.py`, and the depositor's write-set hold enforces the order); PLANNER_TEMPLATE Rule 104 (lands tonight via plan C: a detector that cannot state its own denominator is unmeasured, not quiet — this plan is that rule applied to `propagation_check`'s own silence); LESSONS 2026-08-13 (an attestation written from intention — the class this tool's exit 2 produced in three registers on 2026-09-02). Walk register: `/Users/marklehn/Developer/eluvian-governance/governance/knowledge/research/walk-register-propagation-check-pin-forms-2026-09-02.md`.

**Tier computed, not judged (§1):** **T-8 fires** (a clone by kind of `checker-defects`). T-1 no (one subsystem: `bellows/scripts`, `bellows/tools`, their tests). T-6 — the precedent ruling (473/474, `checker-defects`): the checkers are conformance instruments, not the ten step gates; doctrine untouched. T-2/T-3/T-5 no. → **T1: five-lens walk, no panel.**

## Why this exists — measured 2026-09-02

`propagation_check.py`'s `declared_values` parses a pin row only when the row carries a bold-backticked symbol AND a bold numeral (`**`SYM`**` … `**NN**`; `propagation_check.py:80–81`). Across the six plans drafted on 2026-09-02 there are **51** pin rows: 34 carry the symbol form and 17 use the row id (`M1`…) as their only name; the VALUE cells are plain-backtick in 32 rows, plain text in 8, bold in 9; 11 cells carry a hex digest, 4 a date. On that population the tool parsed **zero** declarations in four plans (exit 2 — "could not run") and one or two accidental ones in the other two (a lone `**6**`, a lone `**1**`) — a "CLEAN" over one symbol. The Planner grepped its output for CLEAN, saw nothing, and wrote CLEAN into three registers and two plan blocks; retracted the same afternoon (plan C's capstone CP-2). The tool's own docstring names this exact failure ("a clean report over ZERO parsed declarations … the failure mode this tool exists to prevent") and its exit 2 is the honest signal — but nothing in the toolchain READS that exit: `run_check.py` has no propagation mode, the manifest's `validation:` field does not carry it, and a grep for CLEAN is silent on both outcomes. Rule 104's class: a detector that cannot state its own denominator presents as healthy silence.

## What this plan does

**F1 — `scripts/propagation_check.py`, `declared_values`:**
- the SYMBOL is the bold-backticked name if the row has one, else the row id in the first cell (`| P3 |`, `| M12 |`) — so a table of `Mn`/`Pn` rows declares `Mn`/`Pn`;
- the VALUES are every numeral of two or more digits (commas allowed) in the row's VALUE cell (the third cell), one symbol → a list — EXCLUDING numerals inside a hex token of twelve or more `[0-9a-f]` characters, inside a date (`YYYY-MM-DD`) or a time (`HH:MM:SS`), and the `256` of `sha-256` / `-a 256`; the legacy bold-numeral form still parses (the positive control);
- the report line becomes `declared symbols: N (values: M)` followed by the map; the exit contract is unchanged — 0 clean, 1 divergences, 2 could not run — and detector (1) runs over every value of every symbol.

**F2 — `tools/run_check.py`:** a fourth mode, `propagation` → `judge_propagation(stdout, stderr, rc)`: rc 0 → `PASS — CLEAN over N symbols`; rc 1 → `FAIL — N divergence(s)`; rc 2 → `FAIL — NOT RUN (exit 2: no declarations parsed)`; anything else → `FAIL — checker crashed`. The docstring's channel-facts block gains the propagation row.

**F3 — `scripts/cycle_check.py --emit-manifest`:** the `validation:` field gains a fourth pair, `propagation_check=CLEAN | DIVERGENT:n | NOT_RUN`, computed by running the checker on the plan (the emitter already runs `fold_check` the same way). ⚠️ The depositor's re-run compares only the `cycle_check=` pair (`depositor.py:516`, measured) — the new pair cannot hold a plan; it makes the record honest.

**F4 — tests:** NEW `tests/test_propagation_check.py` — the tier-2 suite: symbol form {bold-backtick, row-id only} × value form {plain-backtick, plain, bold} × {hex present, absent} × {date present, absent}, every cell asserting the parsed value list (the sixteen forms are the ones enumerated from the six drafts' 51 rows — the population, not the author's intuition); the exit-2 path on a table with no numerals; detector (1) hits on a synthetic plan whose prose restates a declared value, and its silence when a QUALIFIER sits within 90 characters. `tests/test_run_check.py` gains the four `judge_propagation` cases from real checker output. `tests/test_cycle_check.py` gains the manifest-field case. **The kill map:** `knowledge/mutants/propagation-check.json` — M1 the hex exclusion removed (a digest's digits become values) → the hex case; M2 the row-id fallback removed → the row-id case; M3 `judge_propagation` scoring rc 2 as PASS → the NOT-RUN case; M4 the emitter's fourth pair dropped → the manifest case.

**F5 —** the corpus canary: the six 2026-09-02 drafts (five in bellows, W=29 in forge_lessons) and the nine `Done/executable-1000*.md` — after F1 every one exits 0 or 1, never 2; the findings are QUOTED, not judged (a divergence the tool reports on a held plan is that plan's Planner's to read at its next touch).

## What this plan does NOT do

- Does not tune detector (1)'s false-positive rate beyond the four exclusions; does not change detectors (2) and (3); does not make `plan_lint` run the propagation checker (the wrapper and the manifest field are the loud channel). Does not fix any divergence the canary reports in other plans. Does not close thread 90 (a keyboard act).
- ⚠️ **Runs AFTER `checker-defects` closes** — both plans write `scripts/cycle_check.py` and `tests/test_cycle_check.py`; the depositor's write-set collision holds this plan until then, and this plan's cycle_check pin is re-derived at claim for that reason.

## MUST-PRESERVE

- **Exit 2 stays exit 2.** A table the parser cannot read still returns "could not run"; the change widens what it CAN read.
- **The legacy form still parses** (the positive control: `| N1 | **`BATCH`** | — | **25** |` → `BATCH: [25]`).
- **No corpus plan may read exit 2 after F1** (the six drafts, the nine Done plans); an exit 2 is a Critical finding.
- **`known_failures: 0`.** From the worktree the suite is `1676 passed, 1 skipped` plus the checker-defects plan's new cases by the time this runs; after this plan, plus its own. Any failure is a HALT/Critical.
- Worktree discipline; `git add` by explicit pathspec; agents do not push; do NOT rename the plan file.

## Numbers discipline — the pins DEV re-derives (measured 2026-09-02 by the Planner at bellows `47130ee`)

| pin | what | value | how |
|---|---|---|---|
| P1 | **`SRC`** — shas, pre-edit | `propagation_check.py` `ab9aa01d50142b45` · `run_check.py` `3ebd5aaa048cb768` · `cycle_check.py` — RE-DERIVE AT CLAIM (the checker-defects plan lands first; state the sha you find and that it postdates `2efd4e2de1a3f9ea`) | `shasum -a 256 <f> \| cut -c1-16` |
| P2 | **`TESTS`** — pre-edit | `tests/test_run_check.py` `9 passed`; `tests/test_propagation_check.py` ABSENT (the tool has no tests today) | `BPY -m pytest tests/test_run_check.py -q -p no:cacheprovider`; `ls tests` |
| P3 | **`POPULATION`** — the pin rows of the six 2026-09-02 drafts | 51 rows; symbol form: bold-backtick 34 / row-id 17; value form: plain-backtick 32 / plain 8 / bold 9; hex present 11; date present 4 | the register's M3 script, re-run |
| P4 | **`CORPUS_BEFORE`** — the tool's exit on the six drafts, unpiped | `bellows-bootstrap` 0 (one accidental symbol) · `shop-server-invariant-sketch` 2 · `shop-server-invariant-company` 0 (one accidental symbol) · `gate2-pt-w28-a` 2 · `checker-defects` 2 · `forge-cycle-w29` 2 | `BPY scripts/propagation_check.py <draft>; echo $?` — the exit read directly, never through a pipe |
| P5 | **`DEPOSITOR`** | `depositor.py:516` compares only the `cycle_check=` pair of `validation:` | `sed -n 516p depositor.py` |
| P6 | **`SUITE`** — from the worktree | `1676 passed, 1 skipped` today; RE-DERIVE (the checker-defects plan adds cases first) | `BPY -m pytest tests -q -p no:cacheprovider` |

## Drafting Cycle

**Tier:** T1 — T-8 fires (a clone by kind of `checker-defects`); T-6 not claimed (the 473/474 ruling); no panel, no scout.

**Walk register:** /Users/marklehn/Developer/eluvian-governance/governance/knowledge/research/walk-register-propagation-check-pin-forms-2026-09-02.md

**Walk 0 (context pin, measured):** the parser's two regexes and the exit contract read at their lines; the six drafts' 51 pin rows enumerated by script into the sixteen-cell population (symbol × value form × hex × date); the tool's exit on each of the six drafts read unpiped (four exit 2, two exit 0 over one accidental symbol each); a crude bold-conversion run that showed WHICH numerals would false-positive (`256` of `sha-256`, `2026` of dates) — the exclusion list's source; the three source shas; `run_check`'s three modes and the emitter's three-pair `validation:` read at source; the depositor's re-run comparing only the `cycle_check=` pair (`depositor.py:516`); the test counts (`test_run_check` 9; no propagation tests); the clone-diff against `checker-defects` and its register; the consumer dry-run (§2.0) — class assigner `shop-infra`, extractor per step with the receipt first, the write-set intersection with `checker-defects` measured (two files — the depositor's collision hold orders this plan after it).

**Direction verdict (after walk 1): PROCEED.** Tested: the premise (a tool that could not read 49 of 51 real rows, and a toolchain that read its silence as clean — measured, not recalled), the mechanism (a wider parser proven on the population's forms with a positive control for the legacy form, an exit contract unchanged, two loud channels), the scope (detectors (2) and (3) untouched; the canary's findings in other plans recorded for their Planners, never fixed here).

**Walks:**
- Weak spots:          w1 1 folded — instruction 0 / record 1 (the register's parent-diff said the detector fields were declared "from v0" while the v0 carried no manifest at all — this block and its manifest, with `target_class`, `state_space` and `mutants`, written before walk 1's record so the claim is true when read; the P2 test count corrected from the run, 9 not 8, before the first lint)
- Destruction:         w1 dry — exit 2 stays exit 2; the legacy form still parses (a positive control); no corpus plan may read exit 2 after; detectors (2)/(3) untouched
- Vulnerabilities:     w1 dry — the exclusions come from a measured false-positive run, not a guess; QA's pre-edit modules by `git show HEAD~1:`, never `git stash`; the manifest pair proven harmless at the depositor's comparison line
- Integration-record:  w1 dry — the manifest is the emitter's, spliced at the freeze; the class the assigner measured; the collision with `checker-defects` named in the plan and the register
- ACID:                w1 dry — one DEV commit by explicit pathspec after the suite; QA's commit separate; a HALT before the commit leaves nothing landed
- **Walk 1 total: 1 finding, 1 folded — instruction 0 / record 1; 0 of 1 fold-introduced.**

- Weak spots:          w2 dry — instruction 0 / record 0 — F1's exclusion list re-read against the M4 false-positive run; the QA items re-read as an agent would run them; the Cycle Log covered
- Destruction:         w2 dry — instruction 0 / record 0 — unchanged
- Vulnerabilities:     w2 dry — instruction 0 / record 0 — unchanged
- Integration-record:  w2 dry — instruction 0 / record 0 — the manifest emitted at the freeze and spliced; `propagation_check` recorded as it ran on this plan (exit 2 — the defect under repair)
- ACID:                w2 dry — instruction 0 / record 0 — unchanged
- **Walk 2 total: 0 findings — instruction 0 / record 0, ALL FIVE LENSES DRY.** Instruction series 0 → 0 (walk 1's fold was record-class).

**Conformance (§5):** first run at walk 0 (on v0) and re-run after walk 1 and at the freeze: `plan_lint` exit 0 / 0 FAIL at the faithful mirror — expected WARN set (o2)×8 plus the advisory "step 2 mentions tests" line; (s)/(t) silent with the detector fields declared; `cycle_check` BAR_MET; `fold_check` re-baselined at each intended change with a note; **`propagation_check` NOT RUN on this plan — exit 2, the very defect the plan repairs: its pin rows are in the plain-backtick form the parser cannot read until F1 lands.**

**Closing:** ✅ **BAR MET — walk 2 dry (all five lenses) after walk 1's one record fold; T1, no panel owed, none convened.** Substrate present (the register's rows entered at each phase from captured output and committed at the freeze; `fold_check` baseline). The closing-record re-read (§2.7) ran against this block, the register and the emitted manifest at the freeze.

**Fold-and-deposit exactly once.**

## Cycle Manifest
tier: T1
target: scripts/propagation_check.py, tools/run_check.py, scripts/cycle_check.py
class: shop-infra
target_class: detector
state_space: symbol form {bold-backtick name / row-id only} × value-cell form {plain-backtick / plain / bold} × {hex digest present / absent} × {date present / absent} — sixteen cells, the dimensions read from the SYSTEM (the six 2026-09-02 drafts' 51 pin rows enumerated by script; the parser's own two regexes), every cell asserting its parsed value list, with a completeness assertion over the cross product; plus the exit-2 path (no numerals) and the legacy-form positive control
mutants: knowledge/mutants/propagation-check.json
reads: /Users/marklehn/Developer/bellows/scripts/propagation_check.py, /Users/marklehn/Developer/bellows/tools/run_check.py, /Users/marklehn/Developer/bellows/scripts/cycle_check.py, /Users/marklehn/Developer/bellows/depositor.py, /Users/marklehn/Developer/bellows/knowledge/decisions/drafts/executable-checker-defects.md
writes: scripts/propagation_check.py, tools/run_check.py, scripts/cycle_check.py, tests/test_propagation_check.py, tests/test_run_check.py, tests/test_cycle_check.py, knowledge/mutants/propagation-check.json, knowledge/development/dev-log-propagation-check-pin-forms-2026-09-02.md, knowledge/qa/evidence/propagation-check-pin-forms-2026-09-02/qa-receipt.md, knowledge/qa/evidence/propagation-check-pin-forms-2026-09-02/probes-raw.txt, knowledge/qa/evidence/propagation-check-pin-forms-2026-09-02/full-suite-propagation-check-pin-forms.txt
open_forks: tuning detector (1)'s false-positive rate on the corpus after the canary's findings are read; whether plan_lint should itself invoke the propagation checker at deposit (a fourth channel) or the manifest pair suffices; the divergences the canary reports in the six held plans — their Planners' to read at the next touch
walks: 2
yields: 0, 0
validation: cycle_check=BAR_MET, plan_lint=0_FAIL, fold_check=PASS
coherence: 2/2 walks have register rows


---

## STEP 1 — DEV

> **FIRST — post a short visible chat message (1–2 sentences).** Do NOT rename this file. You are the bellows Developer. `cd "$(git rev-parse --show-toplevel)" && [ -f scripts/propagation_check.py ] && [ -f tools/run_check.py ] && echo TREE_OK` — HALT unless TREE_OK. `BPY=/Users/marklehn/Developer/bellows/.venv/bin/python` (re-derive per compound).
>
> ⛔ **A1 — re-derive P1 (state the claim-time `cycle_check.py` sha), P2, P3 (re-run the register's population script over the six drafts — the counts), P4 (six exits, each read unpiped), P5, P6. Mismatch → HALT quoting both.**
>
> **A2 — F1–F3.** Prove each post-condition can fail BEFORE the edit: run the new tests against the pre-edit code (they FAIL — quote the node ids), then edit, then run them (they PASS). Then the corpus canary (F5): fifteen files, each exit quoted unpiped, each 0 or 1; for every exit 1 quote the tool's `DIVERGENCES: n` line and the first three `L…:` lines — the findings are evidence about THOSE plans, recorded, not acted on here.
>
> **A3 — F4 and the kill map:** `tests/test_propagation_check.py` (the sixteen-cell table with a completeness assertion over the cross product; the exit-2 path; the detector-(1) hit and qualifier cases; the legacy-form positive control), the `judge_propagation` cases, the manifest-field case; `knowledge/mutants/propagation-check.json` (M1–M4, each a one-anchor revert with its `expect_fail` node id). Targeted run: `tests/test_propagation_check.py tests/test_run_check.py tests/test_cycle_check.py` → all pass; state the new count.
>
> **A4 — full suite + dev log + commit.** `"$BPY" -m pytest tests -q -p no:cacheprovider` → `<P6 + new> passed, 1 skipped`, exit 0. `knowledge/development/dev-log-propagation-check-pin-forms-2026-09-02.md`: the pins, the fail-before/pass-after node ids, the fifteen canary lines with their exits and quoted findings, the suite line. `git add scripts/propagation_check.py tools/run_check.py scripts/cycle_check.py tests/test_propagation_check.py tests/test_run_check.py tests/test_cycle_check.py knowledge/mutants/propagation-check.json knowledge/development/dev-log-propagation-check-pin-forms-2026-09-02.md && git commit -m "[<id from your plan filename>] propagation-check-pin-forms-2026-09-02: declared_values reads the plain-backtick and row-id forms (hex, dates, sha-256 excluded); run_check propagation mode; manifest validation carries propagation_check; tier-2 suite + kill map (thread 90)" -- scripts/propagation_check.py tools/run_check.py scripts/cycle_check.py tests/test_propagation_check.py tests/test_run_check.py tests/test_cycle_check.py knowledge/mutants/propagation-check.json knowledge/development/dev-log-propagation-check-pin-forms-2026-09-02.md`. `git status --short` → empty. STOP.
>
> **Deposits:**
> - `knowledge/development/dev-log-propagation-check-pin-forms-2026-09-02.md`
> - `knowledge/mutants/propagation-check.json`
> - `scripts/propagation_check.py`
> - `tools/run_check.py`
> - `scripts/cycle_check.py`
> - `tests/test_propagation_check.py`
> - `tests/test_run_check.py`
> - `tests/test_cycle_check.py`
>
> **Scope:**
> - `knowledge/development/dev-log-propagation-check-pin-forms-2026-09-02.md`
> - `knowledge/mutants/propagation-check.json`
> - `scripts/propagation_check.py`
> - `tools/run_check.py`
> - `scripts/cycle_check.py`
> - `tests/test_propagation_check.py`
> - `tests/test_run_check.py`
> - `tests/test_cycle_check.py`

## STEP 2 — QA

> **Step 1's Receipt status must be `Status: Complete`.** Anything else → HALT. **FIRST — post a short visible chat message.** You are the bellows QA agent. `cd "$(git rev-parse --show-toplevel)"`; `BPY=/Users/marklehn/Developer/bellows/.venv/bin/python` — re-derive per compound.
>
> **(A) Rule 20 self-check** — the canonical block at the path the dispatcher's mandate names (this machine's `RULE_20_SELF_CHECK_BLOCK.md`; quote the path you were handed). Run with:
> - `plan_slug`: `propagation-check-pin-forms-2026-09-02`
> - `qa_report_path`: `"$(pwd)/knowledge/qa/evidence/propagation-check-pin-forms-2026-09-02/qa-receipt.md"`
> - `evidence_dir`: `"$(pwd)/knowledge/qa/evidence/propagation-check-pin-forms-2026-09-02"`
> - `required_evidence_files`: `["probes-raw.txt", "full-suite-propagation-check-pin-forms.txt"]`
>
> **(B) Items — raw output appended to `probes-raw.txt`:**
> - **Item 1 — fail-before / pass-after, by a second pair of hands:** `git show HEAD~1:scripts/propagation_check.py` (and `tools/run_check.py`, `scripts/cycle_check.py`) into `/tmp/pc-qa/`; the new tests against those modules FAIL (node ids quoted); against `scripts/` and `tools/` they PASS. `git stash` is FORBIDDEN.
> - **Item 2 — the corpus canary:** the fifteen files → fifteen exits, each 0 or 1, read unpiped; the legacy-form positive control → parses; one synthetic table with no numerals → exit 2 (the exit-2 path survives).
> - **Item 2.5 — the kill map (Rule 106):** `"$BPY" tools/mutation_check.py knowledge/mutants/propagation-check.json` → every mutant `KILLED`, `SURVIVED` 0, `ERROR` 0 (each scoring line quoted). A survivor is a missing test, a Critical finding.
> - **Item 3 — the loud channel:** `"$BPY" tools/run_check.py propagation <a scratch copy of THIS plan under a lintmirror- name in /tmp>` → `RUN_CHECK: propagation VERDICT=…` with the checker's exit named; `"$BPY" scripts/cycle_check.py --emit-manifest <the same copy>` → the `validation:` line carries `propagation_check=…`; and the depositor's re-run on a stanza carrying the new pair does not hold (`depositor.py:516` — quote the line).
> - **Item 4 — the full-suite file:** `"$BPY" -m pytest tests -q -p no:cacheprovider > knowledge/qa/evidence/propagation-check-pin-forms-2026-09-02/full-suite-propagation-check-pin-forms.txt 2>&1; echo "exit=$?" >> knowledge/qa/evidence/propagation-check-pin-forms-2026-09-02/full-suite-propagation-check-pin-forms.txt` → the file carries `exit=0` and a summary with 0 failed.
>
> **(C) The report** `qa-receipt.md`: the verification table — status cells carry the glyph only, and NO positive row quotes a probe token or an output line carrying a Rule 20 hedging keyword (`hedging_keywords` in the canonical block; the suite summary line is out; rows name the FILE, the exit and a count) — the follow-ups (the divergences the canary reported in other plans, listed by file and count for their Planners; thread 90's closure at the keyboard), the Rule 20 stdout APPENDED. Commit: `git add knowledge/qa/evidence/propagation-check-pin-forms-2026-09-02/ && git commit -m "[<id>] QA: propagation_check pin forms — fail-before/pass-after, 15/15 corpus exits 0|1, kill map, the loud channel" -- knowledge/qa/evidence/propagation-check-pin-forms-2026-09-02/`. STOP.
>
> **Deposits:**
> - `knowledge/qa/evidence/propagation-check-pin-forms-2026-09-02/qa-receipt.md`
> - `knowledge/qa/evidence/propagation-check-pin-forms-2026-09-02/probes-raw.txt`
> - `knowledge/qa/evidence/propagation-check-pin-forms-2026-09-02/full-suite-propagation-check-pin-forms.txt`
>
> **Scope:**
> - `knowledge/qa/evidence/propagation-check-pin-forms-2026-09-02/qa-receipt.md`
> - `knowledge/qa/evidence/propagation-check-pin-forms-2026-09-02/probes-raw.txt`
> - `knowledge/qa/evidence/propagation-check-pin-forms-2026-09-02/full-suite-propagation-check-pin-forms.txt`

Rule 20 banner (byte-exact, produced by RUNNING the canonical block — never hand-authored):

```
============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
```
