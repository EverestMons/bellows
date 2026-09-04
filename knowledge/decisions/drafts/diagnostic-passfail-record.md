# bellows — diagnostic: THE PASS/FAIL RECORD THAT ALREADY EXISTS — what `gate_events` covers, which checks are outside it, whether it can be read back, and whether it survives leaving this machine

**Date:** 2026-09-04 | **Project:** bellows | **Tier:** Small | **Dispatch Mode:** bellows | **cycle_tier:** T1 | **Test Scope:** none (read-only diagnostic — the instrument is new code with no consumers; this step deposits raw output as `.txt` evidence, which `qa_test_result` will refuse to certify having no pytest summary to parse: the pre-declared benign gate failure of the gate note below) | **Execution:** Step 1 (DIAGNOSTIC) | **pause_for_verdict:** always | **known_failures:** 0

**auto_close:** false

**Depends on:** `Done/diagnostic-100034.md` (the gate fail-open census — this corrects and extends its Q5) and tuyere thread 119 (the CEO ruling this serves). Clone origin: `Done/diagnostic-100034.md` — same kind, one Item per question, read-only, closed 2026-09-04.

## What this decides

**Nothing.** ⛔ **PT Rule 82 — price before build.** Thread 119 requires "a record of pass/fail". This measures the record that ALREADY EXISTS, what it misses, and what closing the gap would cost. It recommends no change and chooses no design.

## Why this exists

⛔ **Plan 100034's Q5 was incomplete, and this plan exists because of it.** That census answered *"can a reader of a closed plan determine whether each check ran?"* by enumerating ARTIFACTS — the manifest, hold sidecars, hook stdout — and concluded `gates.py` (all 24 blocking checks) has "✗ no plan-level record". **Measured 2026-09-04, that is wrong about the system:** `lifecycle.db` carries a `gate_events` table with **470 rows**, columns `step_id, gate_name, result, reason_code, overridden, override_ref`, covering **9 distinct gates across 38 of 38 plans — 100% plan coverage**, including **9 recorded overrides**.

⚠️ **The census asked an artifact question and returned an artifact answer.** Both are true and they are not the same: the record EXISTS and is complete for the step gates; it is simply **surfaced in nothing a reader opens**. The ruling's ask therefore splits differently than 100034 implied — this is a SURFACING and COVERAGE problem, not an absence.

| # | pin | value | how to re-derive |
|---|---|---|---|
| P1 | ⛔ the record exists | `lifecycle.db` `gate_events` — `470` rows; cols `step_id, gate_name, result, reason_code, overridden, override_ref` | `PRAGMA table_info(gate_events)`; `SELECT COUNT(*)` |
| P2 | ⛔ its coverage is TOTAL for what it covers | **9** distinct `gate_name` values across **38 of 38** plans; `9` rows with `overridden=1` | group by `gate_name, result`; join `steps` for plan coverage |
| P3 | the 9 gates recorded | `ceo_flags`, `deposit_exists`, `no_errors`, `no_permission_denials`, `qa_test_result`, `receipt_status`, `rule_20_self_check`, `rule_22_verification`, `scope_check` | `SELECT DISTINCT gate_name` |
| P4 | ⛔ what 100034 measured instead | its Q5 concluded `gates.py` has no plan-level record, and `wrap_check`/`mutation_check` none at all. Correct for ARTIFACTS; the DB was not examined | read `gate-fail-open-census-2026-09-04.md` Q5 |
| P5 | the population outside the record | 100034's Q1 inventory (~65 checks) minus P3's 9 | compare the two lists |
| P6 | ⛔ the record is MACHINE-LOCAL | `lifecycle.db` is per-machine; the multi-machine id law (CLAUDE.md) partitions ids precisely because each machine mints from its own DB. A plan executed on the Air records to ITS `gate_events` | read the id-range law; check whether the DB is in git |
| P7 | the corpus is GIT-SHARED | `Done/` plans, registers and verdicts travel in git; the DB does not | `git check-ignore lifecycle.db` |
| P8 | in-flight | re-derive at execution | `sqlite3 lifecycle.db …` |

## The questions

⛔ **Answer each from the instrument's output, never from prose judgement.** An unanswerable question is a FINDING.

> **Q1 — What does `gate_events` actually record, per gate and per plan?** Coverage, results, reason codes, overrides. ⛔ Verify P2's 100% claim against the plan table rather than assuming it — a join that silently drops rows would read as full coverage.
>
> **Q2 — Which checks are OUTSIDE it, and is that by design or omission?** Take 100034's inventory and subtract P3. For each absent check, determine mechanically whether it runs in a context that HAS a `step_id` to attach to — a step gate does; an authoring-time linter may not. ⚠️ **The answer changes what "extend the record" means:** a check with no step context needs a different anchor, not a missing row.
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
**Walks:** 0 (context pin complete).

**Closing:** NOT CLOSED at walk 0.

## Cycle Manifest

*(to be EMITTED at BAR_MET with `cycle_check --emit-manifest` — ⛔ do not hand-type this stanza; emit BEFORE claiming closure.)*

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
