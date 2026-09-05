# bellows — diagnostic: WHERE THE BODY-VS-REGISTER CHECK BELONGS, and what the six unresolvable `walk_register_ref`s are

**Date:** 2026-09-05 | **Tier:** Small | **Dispatch Mode:** bellows | **Test Scope:** none (read-only diagnostic — the instrument is new code with no consumers; this step deposits raw output as `.txt` evidence, which `qa_test_result` will refuse to certify having no pytest summary to parse: the pre-declared benign gate failure of the gate note below) | **Execution:** Step 1 (DIAGNOSTIC) | **qa_steps:** none | **pause_for_verdict:** always

**Priority:** 20

**auto_close:** false

**cycle_tier:** T1 — ⛔ **T-7 fires**: a later plan will build a check on these findings without re-verifying them. T-6 does NOT fire (read-only; edits no doctrine, template, gate or specialist contract — it READS two checkers, which is not editing one). T-3 does not fire. T-8 not fired: clone by kind of `Done/diagnostic-100036.md`.

**Depends on:** tuyere thread **140** (the failure this prices) and thread **133** (its first instance, fixed as `eff3c36`). ⛔ **Read 140 before this plan** — it carries the measurement that licenses it.

## How to Run This Plan

Paste this bootstrap prompt into Claude Code:

```
Read the plan at bellows/knowledge/decisions/diagnostic-cycle-log-signal.md. Execute Step 1 ONLY. After completing Step 1, STOP and wait for my confirmation. Do NOT proceed further and do NOT move the plan to Done.
```

## What this decides

**Nothing.** ⛔ **PT Rule 82.** It prices where a body-vs-register check belongs and enumerates a population; it chooses no remedy and edits no checker.

## Why this exists

⛔ **Measured 2026-09-05 (session `d04ebd33`), on the Planner's own live artifact.** Two walks, 17 findings and a §2.0 direction verdict were recorded in a walk register and NONE in the plan body. `cycle_check` reads only the body. Measured at that moment: `walk_data []`, `instruction_counts {}`, `restructuring_walks set()` — **two walks of `CONTINUE` computed from an empty record.**

⚠️ **It recurred ONE CYCLE after being diagnosed and fixed.** Thread 133 is the same error; it produced the wrong escalation, the CEO resumed past the weaker ruling, and it shipped as `eff3c36` on 2026-09-04. The same author repeated it on 2026-09-05. **Discipline has been tried, with full knowledge, and failed** — which is what licenses a mechanical remedy.

| # | pin | value | how to re-derive |
|---|---|---|---|
| P1 | the corpus | **103** plans in `Done/` + `drafts/` declare a `walk_register_ref` | `cycle_check.parse_block` over both dirs |
| P2 | bodies carrying per-lens walks | **94** | `len(parsed["walk_data"]) > 0` |
| P3 | ⛔ bodies EMPTY | **9 (8%)** — ⚠️ **but this is NOT the defect population** | `walk_data == 0` |
| P4 | ⛔ **the DEFECT is the CONJUNCTION** | body empty **AND** a resolvable register carrying findings rows → **2**, both live drafts, both authored this session: `executable-lessons-destination-v2.md` (4 rows), `executable-memory-destination-and-gate.md` (8 rows) | pair `parse_block` with `walk_register_lint.validate_file` |
| P5 | legitimate walk-0 | **1** — body empty and register empty. ⛔ **An empty Walks block is CORRECT at walk 0**; a check firing on P3 would over-fire ~4× | same pairing |
| P6 | ⛔ **unresolvable refs — the unmeasured population** | **6** plans declare a `walk_register_ref` that does not resolve from the plan's own location. **Invisible to any cross-artifact check by construction** | the resolution attempt that produced P4 |
| P7 | the three silent checks | BASIS emits only on ESCALATE, and an empty ladder cannot escalate · `_compute_coherence` returns `N/A` when `total_walks == 0` · that computation runs only under `--emit-manifest` | read `cycle_check.py` |
| P8 | in-flight | re-derive at execution | `sqlite3 "file:$PWD/lifecycle.db?mode=ro" …` |

## The questions

⛔ **Answer each from the instrument's output. An unanswerable question is a FINDING.**

> **Q1 — What are the six unresolvable refs?** Per plan: the declared ref, what resolution was attempted, and why it failed — wrong root, moved file, never created, or a path shape the resolver does not handle. ⛔ **Classify; do not repair.**
>
> **Q2 — Does the P4 conjunction hold as a discriminator across the whole corpus?** For every plan, report body-walks × register-rows as a 2×2. ⛔ **The question is the FALSE-POSITIVE rate**: how many plans would a conjunction check flag that a reader would judge correct?
>
> **Q3 — Which tool can make the check, and when does it run?** For `plan_lint` and `cycle_check`: does it already resolve the register ref, does it already read the register's rows, and at what cadence is it invoked? ⛔ **Report capability and TIMING separately** — the tool that can make the comparison may not be the tool that runs when it matters.
>
> **Q4 — What would each candidate cost in noise?** Per candidate, the number of plans in the current corpus that would emit a new WARN or FAIL. ⚠️ Thread 117 names habituation as the real cost of checker output; a candidate firing on P3's 9 rather than P4's 2 is the measurable form of that.

## What this does NOT do

- ⛔ It does not edit `plan_lint`, `cycle_check`, or any doctrine file.
- ⛔ It does not repair the two P4 plans or the six P6 refs — classifying them is the deliverable.
- It does not decide where the check belongs; Q3 and Q4 price that and thread 140 carries the decision.

## Drafting Cycle

**Tier:** T1 — T-7 fires (a later plan builds a check on these findings without re-verifying them).
**Walk register:** `/Users/marklehn/Developer/eluvian-governance/governance/knowledge/research/walk-register-cycle-log-signal-2026-09-05.md`
**Walks:** 0 — ⛔ **v0. No lens has walked it; no §2.0 direction verdict issued.**
⚠️ **The Walks block above is the artifact this plan is about. Keep it current PER LENS** — `cycle_check` reads it and nothing else.

**Closing:** ⛔ NOT CLOSED.

## Cycle Manifest

*(to be EMITTED at BAR_MET — ⛔ this placeholder must not survive the freeze; an unemitted manifest reclassified plan 100031 and dispatched it past its class hold.)*

---
---

## STEP 1 — DIAGNOSTIC

---

> **FIRST — before any reads or work: post a short visible message to chat (1–2 sentences) confirming you are starting this plan and stating your immediate next action.**
>
> **Scope:**
> - `tools/cycle_log_signal_census.py`
> - `/Users/marklehn/Developer/eluvian-governance/governance/knowledge/research/cycle-log-signal-2026-09-05.md`
> - `knowledge/development/dev-log-cycle-log-signal-2026-09-05.md`
> - `knowledge/qa/evidence/cycle-log-signal-2026-09-05/census-raw.txt`
>
> **Item 0 — ROOTS, same invocation as every use.** `GOV=/Users/marklehn/Developer/eluvian-governance`; `BPY=/Users/marklehn/Developer/bellows/.venv/bin/python`; then `test -f "$GOV/PLANNER_TEMPLATE.md"` before proceeding. ⚠️ Hardcoded to this machine; the Air keeps governance under `~/Developer/GitHub` and this block FAILS CLOSED there, which is the safe direction.
>
> **Item 1 — re-derive P1–P7 and HALT only on P7's failure.** ⛔ If `_compute_coherence` no longer returns `N/A` on `total_walks == 0`, or BASIS now emits outside an ESCALATE, the premise has changed and this plan must be re-derived before proceeding. Every other pin mismatch is a FINDING.
>
> **Item 2 — build `tools/cycle_log_signal_census.py`.** ⛔ **Import `cycle_check` and `walk_register_lint` and CALL them — `parse_block`, `validate_file`, `extract_tables`. Do not re-implement either.** Two readers of one format diverge; diagnostic 100032's walk 4 rejected exactly that, and five hand-written parses failed on this corpus in one session. ⚠️ **POSITIVE CONTROL before any corpus run:** on `executable-lessons-destination-v2.md` the instrument must report body-walks 0 AND register-rows 4. An empty result must be proven, never assumed.
>
> **Item 3 — Q1: the six unresolvable refs**, classified per plan.
>
> **Item 4 — Q2: the 2×2** over all 103, with the false-positive count named.
>
> **Item 5 — Q3: capability × timing** for `plan_lint` and `cycle_check`, reported as separate columns.
>
> **Item 6 — Q4: noise cost per candidate**, as a count of plans newly emitting.
>
> **Item 7 — deposit the research note** with a coverage statement naming anything unassessable.
>
> **Item 8 — dev-log**, recording that the failure recurred one cycle after being fixed.
>
> **Item 9 — commit** (message tagged with the plan id); record `numstat` — ⛔ **TWO commits in two repos**: governance by explicit pathspec first, bellows LAST.
>
> ⚠️ **Pre-declared benign gate failure.** `test_scope` is `none` and this step deposits raw output as `.txt`, so `_gate_qa_test_result` finds no pytest summary and FAILs. Expected, named here, overridden by the Planner with reference to this note — the 100032/100034/100036 precedent. ⛔ Commit the override justification BEFORE the override; `--override-gate` is write-once.
>
> **Deposits:**
> - `/Users/marklehn/Developer/eluvian-governance/governance/knowledge/research/cycle-log-signal-2026-09-05.md`
> - `knowledge/development/dev-log-cycle-log-signal-2026-09-05.md`
> - `knowledge/qa/evidence/cycle-log-signal-2026-09-05/census-raw.txt`
> - `tools/cycle_log_signal_census.py`
>
> **Post-conditions:** all six unresolvable refs classified with the failed resolution named; the 2×2 complete over 103 plans with a false-positive count; capability and timing reported as separate columns per tool; a noise cost per candidate; ⛔ **no recommendation and no checker edit anywhere** — it prices, it does not choose.
>
> **STOP. Do NOT proceed further. Do NOT move the plan to Done. Wait for CEO confirmation.**
