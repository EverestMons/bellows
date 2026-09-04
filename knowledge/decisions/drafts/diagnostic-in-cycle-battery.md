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
| P2 | ⛔ it runs ONE reader | `:101-103` appends only `plan_lint`; no other battery tool appears in its reader set | `grep -n "readers.append" scripts/fold_check.py` |
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
> **Q2 — How much signal does normalization discard?** For every committed plan revision pair (a fold), compute the signal set with and without each of the three normalizing regexes. How many folds change a NORMALIZED signal (caught today) versus change only a count (discarded today)?
>
> **Q3 — Of the counts-only changes, how many correspond to a REAL fold defect?** Cross-reference against the walk registers: a fold-introduced finding recorded at walk N+1 is ground truth that walk N's fold broke something. ⚠️ **This is the load-bearing question.** A count delta that never coincides with a recorded fold-introduced finding is noise; one that reliably precedes them is the signal `fold_check` is throwing away.
>
> **Q4 — What is the false-positive rate of a count-delta channel?** How often does a count move across a fold that produced NO fold-introduced finding? Express as a rate, and give the distribution — a channel that fires on 90% of folds is unusable regardless of its true-positive rate.
>
> **Q5 — Which of the six tools would contribute signal, and which only noise?** Per tool, the count-delta rate across folds and its coincidence with recorded fold-introduced findings. ⚠️ Expect `mutation_check` to be unanswerable on most plans (only 7 `Done` plans declare mutants) — report that rather than inventing a number.
>
> **Q6 — What would widening the reader set COST per fold?** Measured wall-time for the reader set as it stands, and for each candidate widening. Report the per-fold and per-cycle totals against the corpus's observed walk counts.
>
> **Q7 — What is the OUTPUT VOLUME a reader would face?** Lines emitted per walk under each candidate design. ⚠️ **This prices habituation, which is the real risk** — the 2026-09-03 diagnostic measured this author ignoring standing `plan_lint` WARNs three times in one night, and plan 100033 shipped as a gate rather than a warning for exactly that reason. A design that emits noise will be ignored no matter how correct it is.

## Drafting Cycle

**Tier:** T1 — T-3 fires (the instrument runs where plans are drafted). **T-6 does NOT fire**: read-only, writes no doctrine, no template, no gate, no specialist contract. T-8 not fired: clone by kind of `Done/diagnostic-100032.md`, the immediately preceding diagnostic of the same shape.
**Walk register:** `/Users/marklehn/Developer/eluvian-governance/governance/knowledge/research/walk-register-in-cycle-battery-2026-09-04.md`
**Walks:** 0 (context pin complete).

**Closing:** NOT CLOSED at walk 0.

## Cycle Manifest

*(to be EMITTED at BAR_MET with `cycle_check --emit-manifest` — ⛔ **do not hand-type this stanza.** DC:253 names `validation` a computed field, and plan 100033 now gates BAR_MET on the emitter's key set, so a hand-typed stanza cannot reach the bar.)*

## STEP 1 — the census (read-only; decides nothing)

> **Scope:**
> - `tools/fold_signal_census.py`
> - `/Users/marklehn/Developer/eluvian-governance/governance/knowledge/research/in-cycle-battery-2026-09-04.md`
> - `knowledge/development/dev-log-in-cycle-battery-2026-09-04.md`
>
> **Item 1 — re-derive P1–P8 and HALT on mismatch.** ⛔ Re-derive P2's reader set mechanically, not by reading the docstring — the docstring says "readers" plural and the code appends one, which is the discrepancy this diagnostic starts from.
>
> **Item 2 — build `tools/fold_signal_census.py`.** ⛔ **Import `fold_check`'s own normalizing regexes and signal reducer; do NOT re-implement them.** Two readers of one format diverge — thread 102's defect, and the class this shop has paid for repeatedly. Likewise reuse `tools/battery_census.py`'s `detect_battery` where recording rates are needed. The instrument must be re-runnable and deterministic.
>
> **Item 3 — define the fold corpus mechanically.** A "fold" is a commit that modifies a plan file between two walk boundaries. ⛔ **Derive the population from git history, not from the registers' prose** — and state the population size, because 100032 measured per-lens commit compliance at 8–20% for Planner-authored cycles and 80% for one fresh-context cycle. ⚠️ **If the addressable population is again a handful of cycles, that is the headline finding, not a footnote** — 100032's Q3 was answerable on exactly one cycle, and this diagnostic must say so plainly if it repeats.
>
> **Item 4 — answer Q1–Q7 from the instrument's output**, each with the command and its literal output. ⛔ Quote verdicts VERBATIM; `fold_check` has been quoted verbatim zero times in 164 registers (P6) and this diagnostic is about `fold_check`.
>
> **Item 5 — deposit the research note** at the governance path in Scope, with a coverage statement: which questions the corpus could answer, which it could not, and the population behind each number.
>
> **Item 6 — dev-log**, recording the instrument's construction and any question that proved unanswerable.
>
> **Item 7 — commit** (message tagged with the plan id); record `numstat` — exactly 3 files.
>
> ⚠️ **Pre-declared benign gate failure.** `test_scope` is `none` (read-only diagnostic) and this step deposits raw output as `.txt`, so `_gate_qa_test_result` will find no pytest summary to parse and FAIL. Expected, named here, overridden by the Planner with reference to this note — the 100032 precedent, and the case `plan_lint` check (v) exists to make authors declare.
>
> **Deposits:**
> - `/Users/marklehn/Developer/eluvian-governance/governance/knowledge/research/in-cycle-battery-2026-09-04.md`
> - `knowledge/development/dev-log-in-cycle-battery-2026-09-04.md`
>
> **Post-conditions:** all seven questions answered from instrument output with commands and literal results; the fold population stated with its size and derivation; every unanswerable question named as such with its reason; the instrument re-runnable and deterministic; ⛔ **no recommendation and no decision anywhere in the note** — this diagnostic prices, it does not choose.
