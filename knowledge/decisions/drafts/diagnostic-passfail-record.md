# bellows — diagnostic: THE PASS/FAIL RECORD THAT ALREADY EXISTS — what `gate_events` covers, which checks are outside it, whether it can be read back, and whether it survives leaving this machine

**Date:** 2026-09-04 | **Project:** bellows | **Tier:** Small | **Dispatch Mode:** bellows | **cycle_tier:** T1 | **Test Scope:** none (read-only diagnostic — the instrument is new code with no consumers; this step deposits raw output as `.txt` evidence, which `qa_test_result` will refuse to certify having no pytest summary to parse: the pre-declared benign gate failure of the gate note below) | **Execution:** Step 1 (DIAGNOSTIC) | **pause_for_verdict:** always | **known_failures:** 0

**auto_close:** false

**Depends on:** `Done/diagnostic-100034.md` (the gate fail-open census — this corrects and extends its Q5) and tuyere thread 119 (the CEO ruling this serves). Clone origin: `Done/diagnostic-100034.md` — same kind, one Item per question, read-only, closed 2026-09-04.

## What this decides

**Nothing.** ⛔ **PT Rule 82 — price before build.** Thread 119 requires "a record of pass/fail". This measures the record that ALREADY EXISTS, what it misses, and what closing the gap would cost. It recommends no change and chooses no design.

## Why this exists

⛔ **Plan 100034's Q5 was incomplete, and this plan exists because of it.** That census answered *"can a reader of a closed plan determine whether each check ran?"* by enumerating ARTIFACTS — the manifest, hold sidecars, hook stdout — and concluded `gates.py` (all 24 blocking checks) has "✗ no plan-level record". **Measured 2026-09-04, that is wrong about the system:** `lifecycle.db` carries a `gate_events` table with the row count, gate set, plan coverage and override count pinned at **P1–P3** — a complete pass/fail record for the step gates, at total plan coverage. ⛔ The figures live in the pins and are re-derived at execution; they are deliberately not restated here, because a narrative numeral goes stale while a pin gets re-derived.

⚠️ **The census asked an artifact question and returned an artifact answer.** Both are true and they are not the same: the record EXISTS and is complete for the step gates; it is simply **surfaced in nothing a reader opens**. The ruling's ask therefore splits differently than 100034 implied — this is a SURFACING and COVERAGE problem, not an absence.

| # | pin | value | how to re-derive |
|---|---|---|---|
| P1 | ⛔ the record exists | `lifecycle.db` `gate_events` — `470` rows; cols `step_id, gate_name, result, reason_code, overridden, override_ref` | `PRAGMA table_info(gate_events)`; `SELECT COUNT(*)` |
| P2 | ⛔ its coverage is TOTAL for what it covers | **9** distinct `gate_name` values across **38 of 38** plans; `9` rows with `overridden=1` | group by `gate_name, result`; join `steps` for plan coverage |
| P3 | the 9 gates recorded | `ceo_flags`, `deposit_exists`, `no_errors`, `no_permission_denials`, `qa_test_result`, `receipt_status`, `rule_20_self_check`, `rule_22_verification`, `scope_check` | `SELECT DISTINCT gate_name` |
| P4 | ⛔ what 100034 measured instead | its Q5 concluded `gates.py` has no plan-level record, and `wrap_check`/`mutation_check` none at all. Correct for ARTIFACTS; the DB was not examined | read `gate-fail-open-census-2026-09-04.md` Q5 |
| P5 | the population outside the record | 100034's Q1 inventory — **≈74 checks, split 50 BLOCKING / 24 advisory** — minus P3's 9. ⚠️ Read from that note's Q1 total row, not estimated: an earlier draft of this pin said "~65", carried from this author's own pre-census estimate rather than from the census output | read `gate-fail-open-census-2026-09-04.md` Q1's Total row |
| P5b | ⛔ the anchor question resolves by CALL SITE, not by tracing | `lifecycle.record_gate_events(step_id, gate_result)` is invoked from exactly two sites, both in the daemon's step loop (`bellows.py:1179`, `:1317`) where `_lc_step_id` exists, and it guards `if step_id is None: return` (`lifecycle.py:499`). So a check is recordable today iff the DAEMON invokes it during a step | grep the call sites and read the guard |
| P6 | ⛔ the record is MACHINE-LOCAL | `lifecycle.db` is per-machine; the multi-machine id law (CLAUDE.md) partitions ids precisely because each machine mints from its own DB. A plan executed on the Air records to ITS `gate_events` | read the id-range law; check whether the DB is in git |
| P7 | ⛔ VERIFIED — the corpus is GIT-SHARED, the record is not | `.gitignore:16` carries `lifecycle.db*`, and `git ls-files --error-unmatch lifecycle.db` fails: the DB is ignored AND untracked. `Done/` plans, registers and verdicts travel in git; the pass/fail record does not travel at all | `git check-ignore -v lifecycle.db`; `git ls-files --error-unmatch lifecycle.db` |
| P8 | in-flight | re-derive at execution | `sqlite3 lifecycle.db …` |

## The questions

⛔ **Answer each from the instrument's output, never from prose judgement.** An unanswerable question is a FINDING.

> **Q1 — What does `gate_events` actually record, per gate and per plan?** Coverage, results, reason codes, overrides. ⛔ Verify P2's 100% claim against the plan table rather than assuming it — a join that silently drops rows would read as full coverage.
>
> **Q2 — Which checks are OUTSIDE it, and is that by design or omission?** Take 100034's inventory (**P5** — report BLOCKING and advisory separately, since the ruling is about gates that block) and subtract the recorded set (**P3**).
> ⛔ **Classify each absent check by its INVOCATION SITE, not by tracing its call path** (P5b). Three classes, and the distinction decides what "extend the record" even means:
> - **daemon-invoked during a step** → a `step_id` exists; a missing row is an OMISSION, cheap to fix.
> - **authoring-time (CLI: `plan_lint`, `cycle_check`, `propagation_check`, `fold_check`)** → no step exists, because no step has run. Needs a different anchor entirely — a plan or a draft revision, not a step.
> - **wrap-time (`wrap_check`)** → no plan exists at all. Needs a session anchor.
> ⚠️ Call-path tracing is overreach and would produce a result nobody can audit; module and call site settle it.
>
> **Q3 — Can the record be READ BACK?** Is there any consumer — tool, report, hook, dashboard — that surfaces `gate_events` to a human? ⛔ If nothing reads it, a complete record has the same practical effect as no record, and that is the finding.
>
> **Q4 — What would it cost to record an absent check?** Per check: is its result already computed and discarded, or would recording require re-running it? ⚠️ Recording a discarded result is nearly free; re-running is not.
>
> **Q5 — Does the record survive leaving this machine?** `gate_events` lives in a per-machine DB while the plan corpus travels in git. For a plan executed on one machine and read on another, what is visible? ⛔ **This bounds every design that assumes the DB is the record's home.**
>
> **Q6 — What do the 9 recorded OVERRIDES look like?** `overridden=1` with `override_ref`. Are they attributable — can a reader tell who overrode what, and against which justification? ⚠️ An override is the point where a gate stops being mandatory; the ruling's force depends on those being visible.
>
> **Q7 — Is `steps` a sufficient anchor?** `gate_events.step_id` joins `steps`, which has `plan_id`. For a check that runs at AUTHORING (before a step exists) or at WRAP (no plan at all), what anchor exists? Report the shape of the gap, not a proposed fix.

## Drafting Cycle

**Tier:** T1 — T-3 fires (the instrument runs where plans are drafted). **T-6 does NOT fire**: read-only; writes no doctrine, no template, no gate, no specialist contract. T-8 not fired: clone by kind of `Done/diagnostic-100034.md`.
**Walk register:** `/Users/marklehn/Developer/eluvian-governance/governance/knowledge/research/walk-register-passfail-record-2026-09-04.md`
**Walks:** 4 (walks 0–4 complete).
- Weak spots:          w1 1 folded — instruction 1 / record 0; w4 dry.
- Destruction:         dry (read-only plan; nothing deleted, no behaviour changed); w4 dry.
- Vulnerabilities:     w2 1 folded — instruction 1 / record 0; w4 dry.
- Integration-record:  w1 1 folded — instruction 1 / record 0; w3 1 folded — instruction 1 / record 0; w4 1 folded — instruction 0 / record 1.
- ACID:                w2 1 folded — instruction 1 / record 0; w4 dry.
**Battery run at EVERY walk** — `plan_lint`, `cycle_check`, `fold_check`, `propagation_check`. `fold_check` CLEAN after every fold, baselined before the first. `propagation_check` found the walk-3 defect that four warm lens passes had missed.

**Walk 4 — DRY on the instruction class.** One record fold: the manifest's authored fields (`class`, `reads`, `writes`, `target`, `open_forks`) were left as `<declare>` by the emitter, which derives only the computed four; filled and re-verified BY PARSING — `_parse_plan` returns **3 writes** and `declared class: shop-infra` matching `_assign_class`'s **shop-infra**. ⛔ **A premature BAR MET claim was retracted here:** the Closing asserted the bar at walk 3 while walk 3 carried a finding, and `cycle_check` correctly refused. `fold_check` baseline re-saved once, reason stated. ⚠️ **The manifest is re-emitted AFTER the dry walk** so `validation:` records the closing state rather than the mid-cycle state it was first emitted in.

**Closing:** BAR MET at walk 4 — the dry pass. Yields 1, 2, 2, 1, 0; **zero fold-introduced** across the cycle.

## Cycle Manifest
tier: T1
target: lifecycle.db gate_events (the pass/fail record); read-only census
class: shop-infra
reads: lifecycle.py, bellows.py, gates.py, scripts/plan_lint.py, scripts/cycle_check.py, /Users/marklehn/Developer/eluvian-governance/governance/knowledge/research/gate-fail-open-census-2026-09-04.md
writes: tools/passfail_record_census.py, /Users/marklehn/Developer/eluvian-governance/governance/knowledge/research/passfail-record-2026-09-04.md, knowledge/development/dev-log-passfail-record-2026-09-04.md
open_forks: none — thread 119's design choice is deliberately left open; this plan prices and does not choose
walks: 4
yields: 2, 2, 1, 0
validation: cycle_check=BAR_MET, plan_lint=0_FAIL, fold_check=N/A, propagation_check=DIVERGENT:4
coherence: 3/4 walks have register rows

## STEP 1 — the census (read-only; decides nothing)

> **Scope:**
> - `tools/passfail_record_census.py`
> - `/Users/marklehn/Developer/eluvian-governance/governance/knowledge/research/passfail-record-2026-09-04.md`
> - `knowledge/development/dev-log-passfail-record-2026-09-04.md`
>
> ⚠️ **TWO REPOSITORIES.** Governance by absolute path with `git -C "$GOV"`, never `cd`; commit it by **EXPLICIT PATHSPEC** — this plan's own walk register lives there and will be dirty. ⛔ Commit bellows LAST.
>
> **Item 1 — re-derive P1–P8 and HALT on mismatch.** ⛔ Re-derive P2's coverage by JOIN, not by trusting the pin — a dropped join reads as full coverage.
>
> **Item 2 — build `tools/passfail_record_census.py`.** ⛔ **READ-ONLY against `lifecycle.db`** — open it in a short connection and never write. ⚠️ The DB is live and the daemon is running; a write or a long-held lock is a production incident, not a measurement.
> ⛔ **State the CONCURRENCY stance, do not leave it implicit.** The daemon writes `gate_events` at two sites in its step loop, so a plan dispatched WHILE the census runs adds rows mid-measurement. Either take the counts in one connection and report the instant they describe, or re-run and report both. ⚠️ Re-derive whether the queue is idle at execution and SAY SO — a count taken during dispatch is a different number from one taken at rest, and a note that does not say which was taken cannot be reproduced.
>
> **Item 3 — Q1: what the record holds**, per gate and per plan, with the join verified.
>
> **Item 4 — Q2: the checks outside it**, each classified by whether a `step_id` anchor exists for it.
>
> **Item 5 — Q3: is anything READING it?** Enumerate consumers mechanically across the repos. ⛔ Absence is the finding — report it plainly rather than softening it.
>
> **Item 6 — Q4: cost to record each absent check** — computed-and-discarded versus needs-re-running.
>
> **Item 7 — Q5: portability.** What a reader on another machine can see for a plan executed here.
>
> **Item 8 — Q6: the 9 overrides**, and whether they are attributable.
>
> **Item 9 — Q7: the anchor gap** for authoring-time and wrap-time checks.
>
> **Item 10 — deposit the research note** with a coverage statement naming what could not be assessed.
>
> **Item 11 — dev-log**, recording the correction to 100034's Q5 and how the DB was missed.
>
> **Item 12 — commit** (message tagged with the plan id); record `numstat` — **TWO commits in two repos**: 1 governance, 2 bellows.
>
> ⚠️ **Pre-declared benign gate failure.** `test_scope` is `none` and this step deposits raw output as `.txt`, so `_gate_qa_test_result` finds no pytest summary and FAILs. Expected, named here, overridden by the Planner with reference to this note — the 100032/100034 precedent.
>
> **Deposits:**
> - `/Users/marklehn/Developer/eluvian-governance/governance/knowledge/research/passfail-record-2026-09-04.md`
> - `bellows/knowledge/development/dev-log-passfail-record-2026-09-04.md`
>
> **Post-conditions:** every question answered from instrument output with its command; P2's coverage verified by join rather than asserted; every check in 100034's inventory classified as recorded / absent-with-anchor / absent-without-anchor; the read-back answer stated plainly whether or not a consumer exists; portability answered for the multi-machine case; ⛔ **no recommendation and no design anywhere in the note** — it prices, it does not choose.
