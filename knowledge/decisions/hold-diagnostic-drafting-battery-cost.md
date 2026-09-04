# bellows — diagnostic: PRICE THE DRAFTING LOOP BEFORE MECHANIZING IT — over the 162 committed walk registers, how often the Planner-run battery was skipped, late, or misread, whether the per-lens commit rule is followed at all, what that cost in later findings, and what a daemon-driven loop would and would not have caught (deciding nothing)

**Date:** 2026-09-03 | **Project:** bellows | **Tier:** Small | **Dispatch Mode:** bellows | **cycle_tier:** T1 | **Test Scope:** none (read-only diagnostic; writes one research doc and the instrument's output files) | **Execution:** Step 1 (DIAGNOSTIC) | **pause_for_verdict:** always | **known_failures:** 0 | **Priority:** 1

**auto_close:** false

**Depends on:** tuyere thread 81 (open since 2026-09-01) — this IS its named FIRST ACT: *"a diagnostic over the committed walk registers pricing how often the Planner-run battery … was skipped, late, or misread, and the cost in later findings — price before build (PT Rule 82)."* Clone origin: `Done/diagnostic-100024.md` (2026-09-02, the PT/DC enforcement census — same kind: read-only, one instrument, one research doc, deciding nothing).

## CEO Context

CEO, 2026-09-03, after a day in which four drafting cycles ran at ~13× the previous day's self-damage rate and one plan dispatched past a class hold: *"there's a breakdown here where you keep asking to move on with the drafting cycle … this means drafting cycle is not mechanized the way it should be."*

⛔ **The gap this diagnostic prices.** `cycle_check` already returns `CONTINUE` / `ESCALATE` / `BAR_MET` — the **verdict** is mechanized. Nothing **drives the loop**: the verdict is advisory to whoever holds the pen, so the cadence depends on the Planner's discipline. Thread 81 proposes the daemon drive it. PT Rule 82 says price before build. This decides nothing and builds nothing.

## Numbers discipline — measured 2026-09-03 by the Planner (bellows `6490cfe`)

The agent RE-DERIVES each and states both figures on a mismatch. ⛔ Every one of these is an authoring pin, not a result.

| # | pin | value | how to re-derive |
|---|---|---|---|
| P1 | corpus size | **162** files matching `walk-register-*.md` in `eluvian-governance/governance/knowledge/research/` | `ls …/walk-register-*.md \| wc -l` |
| P2 | ⛔ schema is NOT uniform — **NINE distinct header shapes** | measured over all 162: **135** carry the canonical `id\|walk\|lens\|sub_question\|origin\|finding\|pre_fold_text\|resolution`; **19 have NO finding table at all**; 2 use `sub_q` for `sub_question`; 1 uses an entirely different shape (`id\|lens/source\|class\|origin\|finding`); and **6 registers put `origin` somewhere other than index 4 or omit it entirely** — `qa-predeclaration-2026-09-03` (3), `per-project-lessons-glossary-2026-08-14` (3), `auto-confirm-on-agreement-2026-08-11` (5), and three with no `origin` column: `doctrine-manifest-reconcile-2026-08-31`, `cycle-ingest-residual-bucket-2026-08-14`, `lessons-glossary-channels-v2-2026-08-14`. ⛔ **Parse by HEADER NAME, and report the tableless 19 as a population, not as zeroes.** ⚠️ v0 of this pin said "at least one register" — it understated by six, and the Planner's own analysis of 2026-09-03 parsed position 5 throughout | build the shape histogram first, before any counting |
| P3 | fold-introduced rate by session — ⛔ **computable for only 14% of the corpus** | `1663ee38` 55 rows/4 fold = 7%; `a9cd0af4` 56/1 = 2%; `22366c52` 11/3 = 27%; `42ce7e32` 65/33 = 51%. ⚠️ Measured: only **23 of 162** registers carry a session id at all. Session grouping therefore describes a 14% slice, and the four figures above come from the most recent, most heavily-instrumented days — the least representative end of the corpus. **Group by DATE (from the filename) as the primary axis and by session only where present, stating the coverage both times** | grep each register for a session id before grouping; report coverage as a number |
| P4 | a fresh author reproduces the rate | a fresh-context agent, same model, same doctrine, same work class drafted thread 102: 17 walks, 89 rows, **57%** fold-introduced, 710k tokens, 102 min. ⚠️ Its walk count is INFLATED — the brief told it to reach BAR MET and it pushed through six `cycle_check` escalations with no CEO reachable | `walk-register-u-qa-predicate-align-2026-09-03.md` |
| P5 | halt rate by work class | INSTRUMENT plans (those modifying the verification machinery) 3 halts of 7 = 42.9%; everything else 0 of 11 = 0.0%, over 100014–100031 | `lifecycle.db` `plans` joined to the instrument set by target |
| P6 | throughput by workflow | batched-and-ordered (100017–100027): 11 plans, 65% daemon utilization, 1.36 plans/hour. Serial (100028–100031): 4 plans, 39% utilization, 0.59 plans/hour | `created_at`/`closed_at` spans vs sum of execution time |
| P7 | doctrine growth | `DRAFTING_CYCLE.md` 20,731 → 25,773 words (+24%) between 09-01 09:36 and 09-02 21:53, bullets 163 → 173 (+6%) — density 127 → 148 words/bullet. `PLANNER_TEMPLATE.md` 67,325 → 70,162 on 09-02, bullets flat at 202 | `git show <c>:<file> \| wc -w` across each file's own commits — ⛔ use `${c}:` with braces, zsh eats `$c:P` as a path modifier |
| P8 | ⛔ fold rate does NOT predict outcome | the 48% and 56% cycles both closed CLEAN; the two halts had causes unrelated to drafting churn (a design error about where to place a fix; an unemitted Cycle Manifest). **This diagnostic must not treat fold rate as a quality proxy** | join each register to its plan's `lifecycle_state` |

## MUST-PRESERVE

- ⛔ **This decides nothing and builds nothing.** It prices. Any sentence recommending a build belongs in thread 81's plan, not here.
- ⛔ **Parse registers by header NAME.** P2 is the trap and it already caught the Planner once tonight.
- ⛔ **Separate COST from QUALITY.** P8 is measured: high fold rate co-occurs with clean closes. A finding that conflates them is wrong even if the arithmetic is right.
- **Do not hand-type any enumeration.** Derive the register list, the battery-tool list, and the session grouping mechanically in the same run that uses them.
- **Disclosed, not folded:** `walk_register_lint.normalize_column` does not map the live `sub_q` variant to `sub_question` — a defect in a shipped instrument, found at walk 4. Fixing it changes what the validator accepts across 162 registers and needs its own plan; the census shims around it and records the gap.
- **Report absence as absence.** A register that records no battery run may have run it and not said so; "not recorded" is the measurement, never "not run."

## Drafting Cycle

**Tier:** T1 — T-3 fires (the finding will steer a change to the loop every machine drafts under). T-6 NOT fired: this writes one research doc and touches no doctrine, no template, no gate — verified against the trigger as quoted, not paraphrased. T-8 not fired: clone by kind of `Done/diagnostic-100024.md`.
**Walk register:** `/Users/marklehn/Developer/eluvian-governance/governance/knowledge/research/walk-register-drafting-battery-cost-2026-09-03.md`
**Walks:** 6 (walks 0–6 complete). **BAR MET at walk 6.**
- Weak spots:          w1 dry; w2 2 folded — instruction 2 / record 0; w3 dry; w4 dry; w5 1 folded — instruction 1 / record 0; w6 dry.
- Destruction:         w1 1 folded — instruction 1 / record 0; w2 dry; w3 dry; w4 dry; w5 dry; w6 dry.
- Vulnerabilities:     w1 1 folded — instruction 1 / record 0; w2 dry; w3 dry; w4 dry; w5 dry; w6 dry.
- Integration-record:  w1 dry; w2 1 folded — instruction 1 / record 0; w3 dry; w4 2 folded — instruction 1 / record 1; w5 dry; w6 dry.
- ACID:                w1 dry; w2 dry; w3 1 folded — instruction 1 / record 0; w4 dry; w5 dry; w6 dry.
- Record sweep:        w3 1 folded — instruction 0 / record 1.
**Walk 1 — 2 findings (instruction 2 / record 0); 0 fold-introduced.** ⛔ P2 was measured and falsified: nine header shapes, not one irregularity — 6 registers misplace or omit `origin` and 19 carry no table at all, so a positional parser is wrong on 25 files. `plan_lint` FAILed (b): step 1 named deposits with no **Deposits:** block.

**Walk 2 — 3 findings (instruction 3 / record 0); 0 fold-introduced.** ⛔ P3's session axis covers 23 of 162 registers (14%), so the headline rates describe the corpus's most recent tail, not the corpus — date becomes the primary axis. ⛔ Q3's method needs per-lens commits to resolve a fold to a revision, and they are 2–5 per cycle where the rule implies 35–45 — the addressable population must be reported before any lateness cost. And that gap became its own question (Q4b): per-lens commit compliance differs 14-fold between the Planner and a fresh agent under identical doctrine.
**Walk 3 — 2 findings (instruction 1 / record 1); both fold-introduced by walk 2.** ⛔ Q6 priced the loop against OBSERVED commits, which walk 2 had just measured as 2–5 against a mandated 35–45 — pricing thread 81's enforced loop at today's non-compliance understates it by about an order of magnitude; both products are now required. And walk 2's new Q4b left the title, the step heading, Item 9 and the post-condition all saying "six questions" — reconciled to seven.
**Walk 4 — 2 findings (instruction 1 / record 1); the record one is walk 1's own fold damage.** ⛔ Item 2 would have written a SECOND parser for a format `walk_register_lint` already parses — two readers of one format diverge, which is thread 102's defect verbatim, and a diagnostic seeding the class it measures is worthless; the census now imports the shipped parser and may only shim around it. And P2's "nine shapes" was eight plus a tableless category counted as a shape. ⚠️ This walk's own fold then failed partway — an anchor from a DIFFERENT plan's text aborted the script after three of six edits, leaving the record lagging the practice until repaired. The recurring incomplete-fold class, caught by re-running the gates rather than by reading.
**Walk 5 — 1 finding (instruction 1 / record 0); fold-introduced by walk 2.** ⛔ Walk 2 added the per-lens-commit addressability caveat to Q3 and not to Q5, which depends on it identically — the incomplete-propagation class, and the third time this cycle a fold reached one site and not its twin. Q5's method is now concrete (diff the battery's output across the introducing revision) and both questions share one stated denominator. Recorded with it: the battery is least able to see semantic incompleteness, which is the most common fold-introduced class in the very registers this diagnostic reads — a limit on thread 81's central claim that must not be buried.
**Walk 6 — DRY, BAR MET.** Every pin re-derived: corpus 162, shapes 8, tableless 19, questions 7/7, Scope 3 against numstat 3. ⛔ **The check plan 100031 failed, run deliberately:** `depositor._parse_plan` on the emitted manifest returns **3 writes** matching Scope, and the declared class equals `_assign_class`'s (`shop-infra`) — verified by CALLING the consumer's entry point, never by reading the plan or hand-typing a write list. Before emission it returned only 2, omitting the instrument: the same fallback that dispatched 100031 past its class hold.
**Cycle shape:** 10 findings across 6 walks, 4 fold-introduced (40%). Three of those four were INCOMPLETE PROPAGATION — a fold reaching one site and missing its twin — which is also the class the battery is least able to detect, and therefore the sharpest limit on thread 81's premise this plan can state before it runs.
**Closing:** **BAR MET at walk 6.** FROZEN pending deposit authority.

## Cycle Manifest

tier: T1
target: /Users/marklehn/Developer/eluvian-governance/governance/knowledge/research/drafting-battery-cost-2026-09-03.md
target_class: research
state_space: battery tool (6: plan_lint, cycle_check, fold_check, propagation_check, walk_register_lint, mutation_check) x recording state (recorded-and-quoted / recorded-but-paraphrased / not recorded) x register shape (8 header shapes + the 19 tableless) x addressability (per-lens commits resolve a fold to a revision / do not) — every axis read from SYSTEM artifacts: the shapes from the corpus's own header histogram, the recording state from each register's text, the addressability from `git log` per plan slug. Cells enumerated as Q1-Q6 in STEP 1
mutants: none — read-only diagnostic, no branch ships; the instrument's correctness is established by re-deriving P1-P8 and stating both figures on mismatch
class: shop-infra
reads: /Users/marklehn/Developer/eluvian-governance/governance/knowledge/research/, /Users/marklehn/Developer/eluvian-governance/DRAFTING_CYCLE.md, /Users/marklehn/Developer/eluvian-governance/PLANNER_TEMPLATE.md, scripts/walk_register_lint.py, scripts/plan_lint.py, scripts/cycle_check.py, scripts/fold_check.py, tools/mutation_check.py, lifecycle.db
writes: /Users/marklehn/Developer/eluvian-governance/governance/knowledge/research/drafting-battery-cost-2026-09-03.md, tools/battery_census.py, knowledge/development/dev-log-drafting-battery-cost-2026-09-03.md
open_forks: whether the 09-02 doctrine growth or the author-session explains the fold-rate shift — the two moved together and this diagnostic cannot separate them (thread 111); whether `walk_register_lint.normalize_column` should absorb the `sub_q` variant (disclosed at walk 4, its own plan)
walks: 6
yields: 2, 3, 2, 2, 1, 0
validation: cycle_check=BAR_MET, plan_lint=0_FAIL, fold_check=PASS
coherence: 6/6 walks have register rows

## STEP 1 — DIAGNOSTIC: seven questions, one exercised instrument

> **Scope:**
> - `/Users/marklehn/Developer/eluvian-governance/governance/knowledge/research/drafting-battery-cost-2026-09-03.md`
> - `tools/battery_census.py`
> - `knowledge/development/dev-log-drafting-battery-cost-2026-09-03.md`
>
> **Item 1 — re-derive P1–P8 and state both figures on any mismatch.** ⛔ **Build the header-shape histogram FIRST** and confirm it reproduces P2's nine shapes; a different count means the corpus moved and every downstream number is against a different population. Report the 19 tableless registers as their own population throughout — they are not zeroes, and a mean taken over them is wrong.
>
> **Deposits:**
> - `/Users/marklehn/Developer/eluvian-governance/governance/knowledge/research/drafting-battery-cost-2026-09-03.md`
> - `knowledge/development/dev-log-drafting-battery-cost-2026-09-03.md`
>
> **Item 2 — build `tools/battery_census.py`**, a read-only instrument that walks the register corpus and emits one row per register: slug, authoring session, walk count, finding rows, fold-introduced count and rate, which battery tools are RECORDED as run (`plan_lint`, `cycle_check`, `fold_check`, `propagation_check`, `walk_register_lint`, `mutation_check`), whether a verdict is quoted verbatim or paraphrased, and the plan's terminal `lifecycle_state` where one exists. ⛔ Index table columns by HEADER NAME (P2). ⚠️ The instrument is the deliverable as much as the numbers — thread 81's build will re-run it.
>
> **Item 3 — Q1: how often is the battery RECORDED at all?** Per tool, across the corpus and by month. Report "not recorded" as distinct from "recorded as failed."
>
> **Item 4 — Q2: how often was a verdict RESTATED rather than quoted?** A register that paraphrases a tool's verdict cannot be audited against the tool. ⚠️ This is the highest-value column: the Planner's own recorded failure class is that a restatement can invert while reading as authoritative, and it recurred twice on 2026-09-03 (a `plan_lint` warning about QA steps, and a tier trigger read as "step gates" when it says "gates").
>
> **Item 5 — Q3: what did lateness cost?** For each register, find findings whose `origin` names an earlier walk's fold and ask whether a battery tool run at that earlier walk would have surfaced it. ⛔ Answer this from the tool's ACTUAL output on the artifact at that revision — `git show` the plan at the fold's commit and run the tool — never from judgement about what it would have said.
> ⛔ **This method depends on per-lens commits EXISTING, and they largely do not.** Measured over four recent cycles: `u-qa-predicate-align` 72 drafting commits, `mutation-per-mutant-target` 5, `qa-predeclaration` 4, `register-validate-first` 2 — against roughly 35–45 per-lens commits a 7-to-9-walk five-lens cycle would produce under DC §2.7. **Report the addressable population first** (cycles whose commit count can actually resolve a fold to a revision), answer Q3 over that population only, and state what fraction of the corpus it excludes. ⚠️ A mean over cycles that cannot be addressed is not a lateness cost, it is a measurement of who committed diligently.
>
> **Item 6 — Q4: the cost curve.** Fold-introduced rate, walk count and finding count per cycle over time, grouped by authoring session and by whether the plan is INSTRUMENT class (P5). ⛔ State plainly whether the 09-02→09-03 shift survives controlling for work class, and name every confound the data cannot separate — at minimum: the doctrine changes of 09-02 (P7) and the author-session, which moved together.
>
> **Item 6b — Q4b: per-lens commit COMPLIANCE, as its own number.** DC §2.7 mandates a commit per lens; §2.6's record-coherence check (register rows ↔ per-phase commits, both directions) depends on them. Measure the ratio of drafting commits to (walks × lenses) per cycle across the corpus. ⚠️ The Planner's own recent cycles run 2–5 commits where the rule implies 35–45, while a fresh-context agent on the same doctrine produced 72 — so compliance is not a property of the doctrine but of who is holding the pen, which is precisely thread 81's claim. ⛔ Report it as compliance, not as effort, and do not infer quality from either direction.
>
> **Item 7 — Q5: what would a daemon-driven loop have caught?** For each finding classified as fold-introduced, run the battery against the revision that introduced it and the revision before, and diff the outputs: a finding the tools would have surfaced shows as a new line. This is thread 81's central claim; price it, do not assume it. ⛔ Report the fraction it would NOT have caught with equal prominence — semantic incompleteness (a fold that fixed one site and missed another that says the same thing in different words) is the class the battery is LEAST able to see, and it is the most common fold-introduced class in the 2026-09-03 registers.
> ⛔ **Q5 inherits Q3's addressability limit** (Item 5): both need a per-lens commit to resolve a finding to a revision, and those run 2–5 per cycle against a mandated 35–45. Answer both over the SAME addressable population, state it once, and do not recompute it — Q3 asks what lateness cost, Q5 asks what the loop would have caught, and they share a method and a denominator.
>
> **Item 8 — Q6: what would it have COST?** Battery wall-time per invocation, measured by running each tool over a sample of committed plan revisions. ⛔ **Multiply by the count the RULE implies (walks × lenses), NOT by observed commits.** Q4b measures that observed commits run 2–5 where the rule implies 35–45; thread 81's loop would enforce the rule, so pricing it against today's non-compliance would understate the cost by roughly an order of magnitude. State both products — cost at observed cadence and cost at mandated cadence — and label which is the proposition. A loop that adds ten minutes per lens to a seventeen-walk five-lens cycle is a different proposition from one that adds ten seconds.
>
> **Item 9 — write the research doc** answering all seven (Q1, Q2, Q3, Q4, Q4b, Q5, Q6) with the instrument's raw output deposited beside it. ⛔ End with an explicit "what this does not establish" section. No recommendation.
>
> **Item 10 — dev-log**, and **commit** (message tagged with the plan id); record `numstat` — exactly 3 files.
>
> **Post-conditions:** all seven questions answered from the instrument's output, never from prose judgement; every authoring pin re-derived with both figures stated on mismatch; the register parser proven against the P2 irregular file specifically; zero recommendations in the research doc; `numstat` exactly 3.
