# bellows — diagnostic: RE-PRICE THE DRAFTING LOOP AFTER THE BATTERY MOVED INTO THE VERDICT — over the 188 committed walk registers and the 96 Done plans of August–September, how much of what diagnostic 100032 priced on 2026-09-03 (skipped, late, restated, non-compliant) is still open now that `cycle_check` carries the battery, `lens_order_check` guards every walk close and the manifest records the result — and what a daemon-driven draft lane would still ADD (deciding nothing; thread 81's second act)

**Date:** 2026-09-09 | **Project:** bellows | **Tier:** Small | **Dispatch Mode:** bellows | **cycle_tier:** T1 | **Test Scope:** none (read-only diagnostic; writes one research doc, one census TSV and a dev-log) | **Execution:** Step 1 (DIAGNOSTIC) | **pause_for_verdict:** always | **known_failures:** 0 | **Priority:** 1 | **Discharges:** none — thread 81 stays open; this is its second act

**auto_close:** false

**Post-close:** no restart, no doctrine. The research doc is the input to the CEO's next ruling on thread 81 (build parts 1–2, or park); this plan recommends nothing.

**Depends on:** the CEO's ruling of 2026-09-09 (session d04ebd33): re-price before building. Its predecessor `Done/diagnostic-100032.md` (2026-09-03, T1) — the clone origin BY KIND and BY LAYOUT (one DIAGNOSTIC step, seven questions, one exercised instrument, a research doc that decides nothing). What moved since 100032: bellows plan 100042 (`faee894`, DC v2.29 — `cycle_check` runs `plan_lint`, `fold_check` and `propagation_check` on every CONTINUE/BAR_MET exit and prints a `BATTERY:` line; the manifest's `validation:` line records the result at close); the §2.7 observer `lens_order_check` (`efcf7bd`/`458955a`, 2026-09-06; NO-RECORD held at deposit since DC v2.26); plan 100053 (the register lint's COVERAGE verdict, 2026-09-09); plan 100052 (`dev_log_declared_text`, 2026-09-09). `clone-origin` threads naming 100032: none open (DC v2.33 query at walk 0).

**Tier computed (§1):** **T1** — T-1 fires (a corpus read across governance and bellows records); T-6 does not (no doctrine or instrument changes; `battery_census.py` is extended read-only); T-2 does not.

## CEO Context

Thread 81 (2026-09-01) sketched Bellows as the drafting cycle's executor and named a pricing diagnostic as its first act. That act ran as 100032 and found: the Planner-run battery recorded in 5–59% of registers by tool; verdicts restated more often than quoted; per-lens commit compliance author-dependent (a fresh-context agent 80%, the Planner 8–20%); the battery ~350 ms; the cost-of-lateness population one cycle. Six days later three other plans absorbed part of the sketch by other means. The CEO's 2026-09-09 ruling: re-price before building — so the build, if any, is priced against TODAY's gap, not 09-03's.

## Numbers discipline — measured 2026-09-09 by the Planner (bellows `56a3aa0`)

| # | pin | value | how to re-derive |
|---|---|---|---|
| P1 | ⛔ the register census today | `tools/battery_census.py --registers <governance>/governance/knowledge/research` → 188 rows (163 on 09-03), 16 tableless; September (51 registers): `plan_lint` verbatim 22 / paraphrase 22 / not recorded 7; `cycle_check` 5 / 38 / 8; `fold_check` 0 / 44 / 7; `propagation_check` 14 / 20 / 17; `walk_register_lint` 4 / 12 / 35; `mutation_check` 0 / 14 / 37; corpus-wide not-recorded: 73 / 121 / 118 / 143 / 153 / 174 of 188; September mean fold_rate 0.19 | run the tool |
| P2 | ⛔ the manifest record 100032 could not see | Done plans carrying `validation: cycle_check=…`: August 41 of 63, September 33 of 33 — the battery's result is recorded by the emitter at close since v2.29, whatever the register says | `grep -l '^validation: cycle_check=' Done/*.md` by `**Date:**` |
| P3 | ⛔ compliance, mechanical | `scripts/lens_order_check.py` over every Done plan naming a `**Walk register:**` (84 of 561): LENS-ORDER OK 10, NO-RECORD 68, BATCHED 2, INCOMPLETE 2, N/A 2; the four 2026-09-09 cycles carry 15–40 lens commits each (100% per-lens); 100032's Q4b counted commits by hand (Planner 8–20%) | the replay in the register |
| P4 | ⛔ restatement, the highest-value column | September `cycle_check` verdicts: 5 verbatim, 38 paraphrase — the class 100032 called highest-value (a restatement can invert) is still the dominant record form in registers, while the manifest line (P2) is verbatim by construction | P1's columns |
| P5 | the predecessor | `Done/diagnostic-100032.md` STEP 1 Items 1–10; its research doc `drafting-battery-cost-2026-09-03.md` (249 lines, sections Q1, Q2, Q3, Q4, Q4b, Q5, Q6, "What this does not establish"); its instrument `tools/battery_census.py` (`--registers`, `--db`, `--json`) | read |
| P6 | the sketch's five parts vs today | (1) draft lane — unbuilt: drafts live in `<governance>/governance/knowledge/decisions/drafts/`, a directory no daemon watches, and `is_runnable_plan` (`bellows.py:2532`) admits only `executable-`/`diagnostic-`/`qa-`; (2) commits as clock — half built: the verdict carries the battery, the observer runs at walk close, but the PLANNER invokes both; (3) scratch executions as steps — unbuilt; (4) cold seats as steps — unbuilt (seats are subagents launched by the Planner; the panel incident of 2026-09-09, row 100051, is the read-only-contract hazard the sketch names); (5) fold/verdict/close in the session — as designed | the sketch; grep |
| P7 | in-flight; class | none; daemon pid 26364 on `56a3aa0`; the plan WRITES `tools/battery_census.py` (three columns) → class shop-infra (the assigner reads the writes, not the tier) — HOLDS at admission, the CEO releases; the diagnostic's READS are the read-only part | `status.py` |

## MUST-PRESERVE

- ⛔ **Read-only.** No lane file, no lifecycle row, no doctrine, no instrument behaviour change beyond an added column; every number in the doc is the instrument's or a quoted tool output.
- ⛔ **No recommendation.** The doc answers the questions and ends with "what this does not establish"; the ruling is the CEO's.
- ⛔ **Both denominators stated** wherever a rate is given: the corpus and September, never one.

## Drafting Cycle

**Tier:** **T1** — T-1 fires. **Walk register:** /Users/marklehn/Developer/eluvian-governance/governance/knowledge/research/walk-register-drafting-battery-reprice-2026-09-09.md
**Walks:** walk 0 pinned (P1–P7 measured on bellows `56a3aa0`; clone-diff against `Done/diagnostic-100032.md` run: FACTS, ARTEFACTS, STRUCTURE); `fold_check --save-baseline` ARMED on v0 before any fold; re-saved after every intended edit, emit after the re-save (v2.30). ⛔ **One commit per lens** (§2.7); `lens_order_check` runs with `cycle_check` at every walk close.

**Closing:** WARM close after walk 2 — thread 81's second act, a judged stop. Two walks: instruction 2 → 0 (walk 1 folded four: two method, two class); T1, no panel. Deposit via `ready-`; HOLDS on class shop-infra (the plan writes a tool), the CEO releases. Close acts: the Planner commits the two governance research deposits at the wrap; the CEO's next ruling on thread 81 reads the doc.
- Weak spots:          w1 2 folded — instruction 2 / record 0
- Destruction:         w1 dry
- Vulnerabilities:     w1 dry
- Integration-record:  w1 2 folded — instruction 0 / record 2
- ACID:                w1 dry
- Weak spots:          w2 dry
- Destruction:         w2 dry
- Vulnerabilities:     w2 dry
- Integration-record:  w2 dry
- ACID:                w2 dry
**Walk 2 — DRY, all five lenses, one commit per lens. Instruction 0 on a full pass: the WARM close meets the bar (§2) — a judged stop (5 findings over one walk: instruction 2 / record 2 plus f0; yield 2 → 0). T1: no panel owed.**

## Cycle Manifest
tier: T1
target: tools/battery_census.py
class: shop-infra
reads: tools/battery_census.py, scripts/lens_order_check.py, scripts/cycle_check.py, knowledge/decisions/Done/diagnostic-100032.md, knowledge/decisions/Done/*.md, governance/knowledge/research/walk-register-*.md, governance/knowledge/research/drafting-battery-cost-2026-09-03.md, governance/knowledge/research/bellows-drafting-stage-design-sketch-2026-09-01.md
writes: tools/battery_census.py, knowledge/development/dev-log-drafting-battery-reprice-2026-09-09.md, governance/knowledge/research/drafting-battery-reprice-2026-09-09.md, governance/knowledge/research/drafting-battery-reprice-2026-09-09.tsv
open_forks: 1. the build (parts 1–2 of the sketch) if the doc's Q7 shows a gap the verdict cannot close; 2. parts 3–4 (dispatched scratch executions and cold seats) as tuyere actions (threads 240/242) rather than daemon steps
walks: 2
yields: 2, 0
validation: cycle_check=BAR_MET, plan_lint=0_FAIL, fold_check=VACUOUS, propagation_check=DIVERGENT:42
coherence: 2/2 body walks named in the register (5 register rows; walk-token match, NOT row coverage)
fold_baseline: governance/knowledge/decisions/drafts/.diagnostic-bellows-drafting-battery-reprice.md.foldcheck.json

---

## STEP 1 — DIAGNOSTIC: the seven questions again, over today's corpus, plus the one 100032 could not ask

> ⛔ **Every item starts by re-establishing the root** — `cd "$(git rev-parse --show-toplevel)" && test -f tools/battery_census.py && echo TREE_OK` — HALT unless TREE_OK. ⛔ **The interpreter is `/Users/marklehn/Developer/bellows/.venv/bin/python`, ABSOLUTE.** ⛔ **Read-only:** never run the daemon, `run_plan`, a claim, `gates.check`, or any tool with a live file as an OUTPUT argument; never import `lifecycle`; `git show <sha>:<path>` and `git log` are the only git verbs. The governance checkout is `/Users/marklehn/Developer/eluvian-governance` (read by absolute path; nothing is written there except the two research deposits, which are committed BY THE PLANNER at the wrap — the DEV commits only the bellows files).
>
> **Scope:**
> - `tools/battery_census.py`
> - `knowledge/development/dev-log-drafting-battery-reprice-2026-09-09.md`
>
> **Item 1 — re-derive P1–P4 and state both figures on any mismatch** (P5–P7 are records). Paste the census header and the six per-tool September distributions.
> **Item 2 — extend `tools/battery_census.py` read-only with three columns:** `lens_order` (the `lens_order_check` verdict token for the plan the register's `Draft:`/plan line resolves to — `OK`/`NO-RECORD`/`BATCHED`/`INCOMPLETE`/`N/A`/`unresolved`), `validation_line` (`yes`/`no`: the resolved Done plan carries `validation: cycle_check=`), `coverage` (the register lint's COVERAGE token). Existing columns and their values are byte-identical — asserted by running the PRE-EDIT tool (`git show HEAD:tools/battery_census.py > /private/tmp/battery_census_old.py`, executed with the same interpreter and `--registers`) and the edited tool over the same directory, dropping the three new columns from the new output, and `diff`-ing the two TSVs → empty; paste the diff command and its empty result. Write the TSV to `<governance>/governance/knowledge/research/drafting-battery-reprice-2026-09-09.tsv`.
> **Item 3 — Q1: recorded, by month, TWO records.** The register record (P1's categories) AND the manifest record (P2): per month, the share of cycles whose battery result exists ANYWHERE the tools can read it. State plainly which register-side "not recorded" rows have a manifest line.
> **Item 4 — Q2: restated vs quoted, by month.** The verbatim/paraphrase ratio per tool per month; name the tool whose verdict is most often paraphrased (P4 says `cycle_check`, 38:5 in September) and quote three paraphrases beside the verbatim line the tool prints, so the CEO can see whether a paraphrase can invert.
> **Item 5 — Q4b: compliance, mechanical, by month.** `lens_order_check` over every Done plan naming a register (P3's replay, re-run), per month and per author class (session-attributed Planner cycles vs fresh-context agent cycles, as 100032 grouped them); the four 2026-09-09 cycles as the current rate.
> **Item 6 — Q3/Q5 over the NOW-addressable population.** 100032 had one addressable cycle; today every `LENS-ORDER OK` plan is addressable. For each fold-introduced finding in the September registers whose plan reads OK (P3: at least the four 09-09 cycles), `git -C <governance> show <sha>:<plan path>` and `<sha>:<register path>` for the fold's commit and the commit before into a scratch pair per revision (`/private/tmp/reprice/<sha>/`), rewrite the scratch plan's `**Walk register:**` line to its scratch register (so `cycle_check`'s assert 2 and the coverage read see the SAME revision), run `cycle_check` (with its battery) and `walk_register_lint` on each pair, and diff the two outputs: a line the tools would have surfaced counts as "caught"; report caught / not-caught with equal prominence and name the not-caught classes (semantic incompleteness, a fold that fixed one site and missed a sibling).
> **Item 7 — Q6: cost, re-measured.** Wall-time of one `cycle_check` run (which now carries three tools), `lens_order_check`, `walk_register_lint`, `mutation_check` on `executable-100053.md`'s draft revisions; multiply by the rule's cadence (walks × lenses, from P3's OK plans) and by the observed cadence; state both.
> **Item 8 — Q7 (new): what would a daemon-driven draft lane still ADD?** For each of the sketch's five parts (P6), state from the measurements which of 100032's three failure classes (skipped, late, restated) it would close that the verdict-carried battery has NOT closed — with the number from Q1/Q2/Q4b that shows the residue — and what it would cost (Q6). ⛔ Descriptive: "the residue is N cycles of M" — never "therefore build". Include the one hazard the sketch names that 2026-09-09 measured live (a cold seat minted a production row: the read-only contract must be enforced by the daemon's sandbox, not promised).
> **Item 9 — write the research doc** `<governance>/governance/knowledge/research/drafting-battery-reprice-2026-09-09.md` answering Q1, Q2, Q4b, Q3/Q5, Q6, Q7, each section opening with the instrument's or the tool's raw line it rests on; end with "What this does not establish". No recommendation.
> **Item 10 — dev-log** with the headings declared below (the 196 gate reads them); `## Pins re-derived` opens with P3's value cell pasted verbatim. **Commit** the two bellows files (message tagged with the plan id and `thread 81`), gated on the FULL suite (the census is imported by nothing, but the rule is the rule), path-scoped; `numstat` → exactly 2 files.
> **Headings:** `## Pins re-derived (P1–P4)`; `## Instrument extension (three columns, byte-identical elsewhere)`; `## Q1–Q7 in one table`; `## What the doc does not establish`
> **Verbatim:** `## Pins re-derived (P1–P4)` ← P3
>
> **Deposits:**
> - `knowledge/development/dev-log-drafting-battery-reprice-2026-09-09.md`
> - `/Users/marklehn/Developer/eluvian-governance/governance/knowledge/research/drafting-battery-reprice-2026-09-09.md`
> - `/Users/marklehn/Developer/eluvian-governance/governance/knowledge/research/drafting-battery-reprice-2026-09-09.tsv`
>
> **Post-conditions:** the research doc answers seven questions with both denominators and ends without a recommendation; the TSV has 188 rows and three new columns; the dev-log's four headings present with P3's cell; two bellows files in one commit; nothing written under any lane.
