# bellows — diagnostic: PRICE THE IN-CYCLE BATTERY BEFORE WIDENING IT — what `fold_check` actually runs, what its normalization discards, and what a count-delta channel would have caught across the committed corpus

**Date:** 2026-09-04 | **Project:** bellows | **Tier:** Small | **Dispatch Mode:** bellows | **cycle_tier:** T1 | **Test Scope:** none (read-only diagnostic — the instrument is new code with no consumers; QA deposits its raw output as `.txt` evidence, which `qa_test_result` will refuse to certify having no pytest summary to parse: the pre-declared benign gate failure of Step 1's gate note) | **Execution:** Step 1 (DIAGNOSTIC) | **pause_for_verdict:** always | **known_failures:** 0

**auto_close:** false

**Depends on:** `Done/diagnostic-100032.md` (the drafting-battery-cost diagnostic — this is its successor and reuses its census method) and tuyere thread 117 (the CEO ruling that the battery runs in-cycle and the emitter is NOT extended). Clone origin: `Done/diagnostic-100032.md` — same kind, same shape, same read-only contract, closed 2026-09-03.

## What this decides

**Nothing.** It is a diagnostic. It answers seven questions with measurements and recommends no change. ⛔ **PT Rule 82 — price before build.** The CEO has ruled that the battery runs in-cycle; this prices the specific mechanism before a line of it is written.

## Why this exists

Thread 117 ruled: run the battery in-cycle. Investigating how, three facts emerged that make the obvious implementation wrong:

1. ⛔ **The per-fold runner already exists.** `fold_check`'s docstring: *"This tool runs the readers an artifact is subject to, reduces their output to a set of stable SIGNALS, and diffs that set against a stored pre-fold baseline."* It has the baseline/sidecar mechanism (`--save-baseline`, `.{name}.foldcheck.json`) already built.
2. ⛔ **It runs ONE reader.** "Readers" is plural in the docstring; `scripts/fold_check.py:101-103` appends exactly `plan_lint`. The tool built to run the battery per fold runs one sixth of it.
3. ⛔ **Its normalization discards the only true positive we have.** `DIGIT_RUN_RE = \b\d{2,}\b` maps both `DIVERGENCES: 58` and `DIVERGENCES: 60` to `DIVERGENCES: N`. Plan 100032's Q3 found exactly one measured instance of a battery tool detecting fold damage — `propagation_check` rising 58→60 after a fold-introducing commit — and `fold_check` is designed to suppress it.

⚠️ **Fact 3 is a DELIBERATE design decision, not a defect.** *"Signals are normalized to survive INTENDED edits: line numbers are stripped, because a fold that adds a paragraph shifts every line number below it without changing any contract."* Suppressing counts kills false positives. The question this diagnostic exists to answer is whether it also kills enough true positives to be worth changing — **and that is not answerable by reading.**

| # | pin | value | how to re-derive |
|---|---|---|---|
| P1 | the runner exists | `scripts/fold_check.py` — `--save-baseline` before a fold, diff after; sidecar at `.{artifact.name}.foldcheck.json` (`:118-121`) | read `:1-24` and `:118-121` |
| P2 | ⛔ it runs ONE reader | `:101-103` appends only `plan_lint`; no other battery tool appears in its reader set | `grep -nF "readers.append" scripts/fold_check.py` |
| P3 | ⛔ normalization discards counts | `LINE_NO_RE`, `COUNTS_RE`, `DIGIT_RUN_RE` (`:35-38`). Measured: `DIVERGENCES: 58` and `DIVERGENCES: 60` both → `DIVERGENCES: N` | apply the three regexes to those two strings |
| P4 | the one measured true positive | 100032's Q3: `propagation_check` 58 → 60 across a fold-introducing commit in `u-qa-predicate-align` walk 2 lens 1 (commit `5ec0274`); `plan_lint` and `cycle_check` showed **no change** at the same commit | read `drafting-battery-cost-2026-09-03.md` Q3 |
| P5 | battery cost | `propagation_check` 30ms · `plan_lint` 60ms · `fold_check` 78ms · `mutation_check` **3589ms** (4 mutants, pytest each) | time each on a real plan |
| P6 | recording rates, 164 registers | `fold_check` recorded 29%, quoted **verbatim 0%** — it has never once been quoted verbatim in the corpus | `tools/battery_census.py` |
| P7 | the ruled constraint | thread 117: the emitter's key set is CLOSED at four. This diagnostic must not propose extending it | read thread 117 |
| P8 | in-flight | re-derive at execution | `sqlite3 lifecycle.db …` |

## The questions

⛔ **Answer each from the instrument's output, never from prose judgement.** State coverage honestly: if a question is unanswerable on the available corpus, say so and say why — an unanswerable question is a finding, not a gap to paper over.

> **Q1 — What does `fold_check` actually run, against what it claims?** Enumerate its reader set mechanically. Compare with the six battery tools. Report the delta.
>
> ⚠️ **A confound that binds Q2, Q3 and Q5, and must be stated in the note's coverage section:** the instrument runs TODAY's checkers over HISTORICAL plan revisions. It therefore measures what today's battery would have said, not what the author saw — `plan_lint`'s check set has grown (checks (u), (v) and the 100033 gate all post-date most of the corpus). ⛔ This does NOT invalidate Q2–Q5, which are controlled comparisons: the same tool version is applied to both sides of every fold, so a delta is attributable to the fold and not to tool drift. It DOES mean no number here may be described as "what the cycle would have caught at the time." Say so in the note rather than leaving a reader to infer it.
>
> **Q2 — How much signal does normalization discard?** For every committed plan revision pair (a fold), compute the signal set with and without each of the three normalizing regexes. How many folds change a NORMALIZED signal (caught today) versus change only a count (discarded today)?
>
> **Q3 — Of the counts-only changes, how many correspond to a REAL fold defect?** Cross-reference against the walk registers: a fold-introduced finding recorded at walk N+1 is ground truth that walk N's fold broke something. ⚠️ **This is the load-bearing question.** A count delta that never coincides with a recorded fold-introduced finding is noise; one that reliably precedes them is the signal `fold_check` is throwing away.
>
> **Q4 — What is the false-positive rate of a count-delta channel?** How often does a count move across a fold that produced NO fold-introduced finding? Express as a rate, and give the distribution — a channel that fires on 90% of folds is unusable regardless of its true-positive rate.
>
> **Q5 — Which of the six tools would contribute signal, and which only noise?** Per tool, the count-delta rate across folds and its coincidence with recorded fold-introduced findings. ⚠️ Expect `mutation_check` to be unanswerable on most plans (only 7 `Done` plans declare mutants) — report that rather than inventing a number.
>
> ⛔ **The CANDIDATE DESIGNS, named here so Q6 and Q7 measure the same things and the agent invents nothing:**
> - **C0 — today.** `fold_check` runs `plan_lint` only; signals normalized; counts discarded.
> - **C1 — widened readers.** `fold_check` runs the three cheap tools (`plan_lint`, `propagation_check`, `fold_check`'s own reduction over each); normalization UNCHANGED, so counts are still discarded.
> - **C2 — C1 plus a count-delta channel.** Counts tracked SEPARATELY from the normalized signal set, so a count move is reported without reintroducing the false positives normalization exists to prevent.
>   ⛔ **C2's hardest problem is telling a COUNT from a POSITION, and it is not optional.** Measured at walk 4, the tools spell numbers three ways and one is a trap: `propagation_check` emits `DIVERGENCES: 12`; `plan_lint` emits `candidates=12`, `excluded=10`, `fired=0` — **and also `line=50`.** A line number is a POSITION: it shifts whenever a fold adds a paragraph, changing nothing. Treat it as a count and C2 fires on nearly every fold, which is exactly the false-positive flood `LINE_NO_RE` exists to stop — and why `fold_check` strips positions and counts with SEPARATE regexes rather than one.
>   ⛔ **Derive the count vocabulary from each tool's ACTUAL output, per tool, not from a shared pattern.** A single regex over three formats is a fourth reader of three contracts and will diverge from all of them (thread 102's defect class). ⚠️ `fold_check`'s own count form was NOT captured at walk 4 — the probe's pattern missed it — so the instrument must measure it rather than inherit this plan's silence on it.
>   ⚠️ If counts and positions cannot be separated reliably per tool, **that is a finding that kills C2**, and the note must say so rather than reporting a rate built on a leaky extractor.
>
> ⛔ **`ReaderCrashed` MUST BE COUNTED, NEVER SWALLOWED.** Historical revisions are often mid-draft and malformed, so readers will legitimately fail on some. `fold_check.run_reader` already refuses to paper over this — it raises rather than returning zero signals, because *"reporting 0 signals for a crashed reader would make a broken check indistinguishable from a clean artifact."* The census inherits that contract: catching the exception and SKIPPING the revision silently shrinks the population and biases every rate; counting it as a signal change manufactures a delta. **Report crashed-reader revisions as their own tallied category**, per tool, and state the count in the note beside each population size. ⚠️ A rate computed over a population that silently lost its malformed revisions is not the rate it claims to be.
> ⛔ `mutation_check` is in NO candidate: 3589ms per run and only 7 `Done` plans declare mutants (P5, Q5). Report its numbers for completeness, but do not price a design around it.
>
> **Q6 — What would widening the reader set COST per fold?** Measured wall-time for **C0, C1 and C2**, per fold and per cycle, against the corpus's observed walk counts.
>
> **Q7 — What is the OUTPUT VOLUME a reader would face?** Lines emitted per walk under **C0, C1 and C2** over Population A. ⚠️ **This prices habituation, which is the real risk** — the 2026-09-03 diagnostic measured this author ignoring standing `plan_lint` WARNs three times in one night, and plan 100033 shipped as a gate rather than a warning for exactly that reason. A design that emits noise will be ignored no matter how correct it is.

## Drafting Cycle

**Tier:** T1 — T-3 fires (the instrument runs where plans are drafted). **T-6 does NOT fire**: read-only, writes no doctrine, no template, no gate, no specialist contract. T-8 not fired: clone by kind of `Done/diagnostic-100032.md`, the immediately preceding diagnostic of the same shape.
**Walk register:** `/Users/marklehn/Developer/eluvian-governance/governance/knowledge/research/walk-register-in-cycle-battery-2026-09-04.md`
**Walks:** 9 (walks 0–9 complete).
- Weak spots:          w0 dry; w1 1 folded — instruction 1 / record 0; w2 1 folded — instruction 1 / record 0; w3 1 folded — instruction 1 / record 0; w4 dry; w5 dry; w6 dry; w7 dry; w8 dry; w9 dry.
- Destruction:         w0 1 folded — instruction 1 / record 0; w1 dry; w2 dry; w3 dry; w4 dry; w5 dry; w6 dry; w7 dry; w8 1 folded — instruction 1 / record 0; w9 dry.
- Vulnerabilities:     w0 dry; w1 1 folded — instruction 1 / record 0; w2 1 folded — instruction 1 / record 0; w3 dry; w4 1 folded — instruction 1 / record 0; w5 dry; w6 dry; w7 1 folded — instruction 1 / record 0; w8 dry; w9 dry.
- Integration-record:  w0 dry; w1 dry; w2 dry; w3 dry; w4 dry; w5 1 folded — instruction 1 / record 0; w6 1 folded — instruction 1 / record 0; w7 dry; w8 dry; w9 dry.
- ACID:                w0 dry; w1 1 folded — instruction 1 / record 0; w2 dry; w3 dry; w4 dry; w5 dry; w6 dry; w7 dry; w8 dry; w9 dry.
**Yields 1, 3, 2, 1, 1 — falling, and ZERO fold-introduced across all five walks.** Every finding was pre-existing in v0 and found by asking what a CONSUMER would do: what `fold_check` exposes as importable functions, what git history can support as a population, what `plan_lint` check (o1) verifies, and what the tools actually print.
**⛔ `propagation_check` run at every walk — DIVERGENT:5 throughout**, all classified: pin values cited correctly at their use sites (plan ids `100032`/`100033`, `DC:253`). Zero real restatement divergences. Run because the 2026-09-03 diagnostic measured this detector at 18% recording and this author at 0% across three cycles.
**Walks 5–9 — 4 findings (instruction 4 / record 0); 1 fold-introduced.** w5: clone-diff found the origin gives ONE ITEM PER QUESTION (its Items 3–8 = Q1–Q6) while v0 bundled all seven into one — split, so no question can be answered thinly without it showing. w6: ⛔ **this cycle's own fold damage** — walk 2 split the corpus into two populations and the Post-conditions still said "the fold population" singular; propagated, and a claim-sweep confirmed no other site. w7: `ReaderCrashed` must be COUNTED, never swallowed — historical revisions are often malformed, and silently skipping them biases every rate. w8: two conformance WARNs in the plan's own text — a literal `grep` without `-F`, and an unprefixed Deposits entry. ⚠️ **The (o2) fix went to the WRONG SITE first** — Scope uses repo-relative paths and Deposits project-prefixed ones; prefixing Scope would have broken `scope_check`. Caught by reading the context rather than assuming.
**⚠️ A lapse in this cycle's own conduct, recorded rather than hidden:** `fold_check` had **no baseline** until walk 7, so it could not verify seven folds — in the cycle drafting a diagnostic ABOUT `fold_check`. That is LESSONS 414's unrun-detector class recurring in the plan that studies it. Baseline established at walk 7; re-saved after walk 8 with the drift declared (`VANISHED:` the two WARNs, exactly the intended effect).
**Walk 9 — DRY.** `plan_lint` 0 FAIL · `cycle_check` CONTINUE · `propagation_check` DIVERGENT:6, all classified, zero real (plan ids and `fold_check.py:101-103` cited with their files) · `fold_check` drift = the two intended WARN removals only · counts reconcile: 13 items, 7 questions, 3 Scope entries.
**Yields 1, 3, 2, 1, 1, 1, 1, 1, 2, 0** — falling to dry, with **1 fold-introduced of 12 findings (8%)**.
**Closing — BAR MET at walk 9**, on a dry lens pass. Every finding but w6-1 was pre-existing in v0 and found by asking what a CONSUMER would do.

## Cycle Manifest
tier: T1
target: scripts/fold_check.py
class: shop-infra
reads: scripts/fold_check.py, scripts/plan_lint.py, scripts/propagation_check.py, scripts/cycle_check.py, tools/battery_census.py, knowledge/decisions/Done/diagnostic-100032.md, eluvian-governance/governance/knowledge/research/drafting-battery-cost-2026-09-03.md
writes: tools/fold_signal_census.py, /Users/marklehn/Developer/eluvian-governance/governance/knowledge/research/in-cycle-battery-2026-09-04.md, knowledge/development/dev-log-in-cycle-battery-2026-09-04.md
open_forks: thread 118 (plan_lint (c) reads qa_steps presence not value — filed at walk 0, not folded); C2 carries a stated KILL CONDITION if counts cannot be separated from positions per tool
walks: 9
yields: 3, 2, 1, 1, 1, 1, 1, 1, 0
validation: cycle_check=BAR_MET, plan_lint=0_FAIL, fold_check=PASS, propagation_check=DIVERGENT:6
coherence: 9/9 walks have register rows

## STEP 1 — the census (read-only; decides nothing)

> **Scope:**
> - `tools/fold_signal_census.py`
> - `/Users/marklehn/Developer/eluvian-governance/governance/knowledge/research/in-cycle-battery-2026-09-04.md`
> - `knowledge/development/dev-log-in-cycle-battery-2026-09-04.md`
>
> **Item 1 — re-derive P1–P8 and HALT on mismatch.** ⛔ Re-derive P2's reader set mechanically, not by reading the docstring — the docstring says "readers" plural and the code appends one, which is the discrepancy this diagnostic starts from.
>
> **Item 2 — build `tools/fold_signal_census.py`.** ⛔ **Import `fold_check`'s own normalizing regexes and signal reducer; do NOT re-implement them.** Verified importable at walk 1 — `fold_check` exposes `normalize`, `is_signal`, `run_reader`, `readers_for`, `collect` and `diff_state` as module-level functions, so `collect()` and `diff_state()` are reusable directly and nothing needs copying. Two readers of one format diverge — thread 102's defect, and the class this shop has paid for repeatedly. Likewise reuse `tools/battery_census.py`'s `detect_battery` where recording rates are needed. The instrument must be re-runnable and deterministic.
>
> **Item 3 — define TWO fold populations, because the questions need different granularities.** ⛔ Do not use one over-strict definition; measured at walk 2, that would discard most of the corpus for no reason.
> - **POPULATION A — commit-level.** Any commit that modifies a plan file; a fold boundary is the pair (revision N, revision N+1). **Measured: 20 plans qualify.** No walk linkage is needed, so this answers **Q2, Q4, Q6, Q7** across the whole corpus.
> - **POPULATION B — walk-linked.** Plans with enough commits to attribute a fold to a walk. **Measured: 8 plans carry ≥5 commits.** Needed only for **Q3 and Q5**, which require the register's `origin` column (`fold-introduced (wN-M)`, which names the earlier fold) as ground truth.
> ⚠️ **Why this is not 100032's dead end:** that diagnostic's Q3 needed PER-LENS commits (five per walk) and was answerable on exactly ONE cycle. Fold-level attribution needs only a commit boundary, which is why Population A is 20 rather than 1.
> ⛔ **Derive both populations from git history, not from the registers' prose**, and state each size in the note. If Population B again collapses to a handful, say so plainly as a finding — but do not let that outcome suppress Q2/Q4/Q6/Q7, which do not depend on it.
>
> ⛔ **Item 3b — the extraction location is part of the measurement.** Running today's readers over a historical revision requires that revision on disk. `plan_lint` check (o1) verifies INPUT-PATH EXISTENCE, so a plan extracted to a scratch directory will emit path WARNs that are artifacts of the extraction, not of the fold — and those would enter the signal set as false deltas. ⚠️ This is the recorded probe-LOCATION class (a proof that runs in the wrong place measures the wrong thing). **Extract in a shape that preserves the paths the plan references, or exclude `(o1)` from the signal set and SAY SO** — and state which was chosen, because the choice changes the numbers.
>
> ⛔ **ONE ITEM PER QUESTION, following the clone origin.** `Done/diagnostic-100032.md` gives Items 3–8 to Q1–Q6 individually; v0 of this plan bundled all seven into one item, which lets an agent answer some thinly with nothing to catch it. Each item below states its question, the command, and its literal output. ⛔ Quote verdicts VERBATIM — `fold_check` has been quoted verbatim ZERO times in 164 registers (P6), and this diagnostic is about `fold_check`.
>
> **Item 4 — Q1: what does `fold_check` actually run, against what it claims?** Enumerate its reader set mechanically; compare with the six battery tools; report the delta.
>
> **Item 5 — Q2: how much signal does normalization discard?** Over Population A, the signal set with and without each of the three normalizing regexes; folds changing a normalized signal (caught today) versus folds changing only a count (discarded today).
>
> **Item 6 — Q3: of the counts-only changes, how many are REAL fold defects?** Over Population B, cross-referenced against the registers' `origin` column. ⚠️ **The load-bearing question.** State the population size first; if B collapses, say so and answer the rest anyway.
>
> **Item 7 — Q4: the false-positive rate of a count-delta channel.** Over Population A: how often a count moves across a fold that produced NO fold-introduced finding. Give the rate AND the distribution — a channel firing on 90% of folds is unusable whatever its true-positive rate.
>
> **Item 8 — Q5: which tools contribute signal, and which only noise?** Per tool, the count-delta rate and its coincidence with recorded fold-introduced findings. ⚠️ `mutation_check` will be unanswerable on most plans (7 declare mutants) — report that rather than inventing a number.
>
> **Item 9 — Q6: cost of C0, C1, C2** per fold and per cycle, against observed walk counts.
>
> **Item 10 — Q7: output volume** a reader faces under C0, C1, C2 over Population A. ⚠️ This prices habituation, the real risk.
>
> **Item 11 — deposit the research note** at the governance path in Scope, with a coverage statement: which questions the corpus could answer, which it could not, and the population behind every number.
>
> **Item 12 — dev-log**, recording the instrument's construction, the count-vocabulary contract it derived per tool, and any question that proved unanswerable.
>
> **Item 13 — commit** (message tagged with the plan id); record `numstat` — **TWO commits in two repos**, not one: 1 file in `eluvian-governance` (the research note) and 2 in `bellows` (the instrument, the dev-log). ⛔ **Commit the governance file by EXPLICIT PATHSPEC** — this plan's own walk register lives in that repo and will be dirty at execution, so a bare `commit -a` sweeps it into the wrong commit (the 100027 discipline, the half of it that applies here). ⚠️ The full A0 re-entry ladder is deliberately NOT carried: 100027 needed it because it EDITED a shared doctrine file and a half-landed edit is indistinguishable from a foreign one; this plan CREATES a new note, so there is no such state. Recorded so the omission reads as a decision, not a drop.
>
> ⚠️ **Pre-declared benign gate failure.** `test_scope` is `none` (read-only diagnostic) and this step deposits raw output as `.txt`, so `_gate_qa_test_result` will find no pytest summary to parse and FAIL. Expected, named here, overridden by the Planner with reference to this note — the 100032 precedent, and the case `plan_lint` check (v) exists to make authors declare.
>
> **Deposits:**
> - `/Users/marklehn/Developer/eluvian-governance/governance/knowledge/research/in-cycle-battery-2026-09-04.md`
> - `bellows/knowledge/development/dev-log-in-cycle-battery-2026-09-04.md`
>
> **Post-conditions:** all seven questions answered from instrument output with commands and literal results, **one Item per question**; **BOTH populations stated with their sizes and derivations** (A commit-level, B walk-linked) and each question attributed to the one it used; the **extraction choice named** (paths preserved, or `(o1)` excluded) with the reason, since it changes the numbers; the **count vocabulary recorded per tool**, derived from actual output, with `fold_check`'s own form measured rather than inherited from this plan's silence; every unanswerable question named as such with its reason; the instrument re-runnable and deterministic; ⛔ **no recommendation and no decision anywhere in the note** — this diagnostic prices, it does not choose.
