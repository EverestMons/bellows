# bellows — diagnostic: CAN THE CYCLE LOG BE COMPUTED RATHER THAN KEPT — is the body derivable from (walk register ⋈ per-lens commits), and what does the register schema still lack

**Date:** 2026-09-06 | **Project:** bellows | **Tier:** Small | **Dispatch Mode:** manual_bootstrap | **cycle_tier:** T1 | **Test Scope:** none (read-only diagnostic — the instrument is new code with no consumers; this step deposits raw output as `.txt` evidence, which `qa_test_result` cannot certify having no pytest summary to parse: the pre-declared benign gate failure of the gate note below) | **Execution:** Step 1 (DIAGNOSTIC) | **qa_steps:** none | **pause_for_verdict:** always | **known_failures:** 0

**Priority:** 20

**auto_close:** false

---

## ⛔ DISPATCH MODE — `manual_bootstrap`, and why

**CEO direction 2026-09-06.** Executed by pasting the bootstrap prompt into Claude Code; **Bellows is not in the loop.**

⚠️ **The reason is the subject, again.** This plan prices whether the artifact `cycle_check` reads should be COMPUTED. The daemon lane's admission gate IS `cycle_check`, and the drafting cycle's advance signal is under repair (threads 151, 152). ⛔ **Routing a diagnostic about the record `cycle_check` reads through `cycle_check` is the circularity this plan exists to examine** — the same reason `diagnostic-cycle-log-signal` took this mode on 2026-09-05.

⛔ **NOTHING IS OVERRIDDEN.** `manual_bootstrap` is sanctioned: no gate is asked a question it would refuse, no clearance row is written, no override recorded — because none is needed. The plan stays in `drafts/`, which the daemon never scans. ⚠️ **Cost, stated as a choice:** no `Done/` record and no lifecycle plan id. ⛔ **A later plan citing these findings must cite the research note BY PATH.**

**cycle_tier:** T1 — ⛔ **T-7 fires**: a later plan will act on this population without re-verifying it. **T-6 does NOT fire** — it READS `DRAFTING_CYCLE.md`, `cycle_check`, `walk_register_lint` and `lens_order_check` and edits none of them. **T-1 fires** (two repositories). T-8 not fired: clone by kind of `drafts/diagnostic-register-coverage.md`, same shape — read-only census, one instrument, per-question Items.

## How to Run This Plan

```
Read the plan at bellows/knowledge/decisions/drafts/diagnostic-cycle-log-projection.md. Execute Step 1 ONLY. After completing Step 1, STOP and wait for my confirmation. Do NOT proceed further and do NOT move the plan to Done.
```

## What this decides

**Nothing.** ⛔ **PT Rule 82.** Whether the Cycle Log becomes a projection, whether `class` enters the register schema, and what emits the block are three design decisions this plan does not touch. It measures derivability and prices a migration.

## Why this exists

⛔ **TWO HAND-KEPT RECORDS OF ONE SET OF EVENTS ALREADY DISAGREE ON A THIRD OF THE CORPUS.** Measured 2026-09-06 over every plan carrying both a body Cycle Log with walk data and a resolvable register with rows: **47 agree on the walk-set, 24 diverge.** The divergence is systematic, in both directions:

- **body AHEAD of register** — `diagnostic-100032` body `[1-6]` vs register `[1-5]`; `diagnostic-100038` `[1-9]` vs `[1-8]`; `executable-100017` body `[1-9]` vs register `[1,2,3,5,7,8,9]`, missing walks 4 and 6. The last walk's rows were never written.
- ⛔ **body BEHIND register** — `executable-100010` and `executable-100013`, body `[1]` against register `[1,2]`. **That is thread 140/141's failure sitting in the shipped corpus**, undetected.

⚠️ **The shop has already ruled on this shape elsewhere:** two records of one fact diverge unless one is a PROJECTION of the other. `LESSONS.md`'s `[status:]` markers project the forge DB's `lesson_proposals.status`, stamped by `project_status_markers.py --apply`; the Cycle Manifest's `walks`, `yields`, `validation`, `coherence` are COMPUTED and never hand-typed (DC:253). The Cycle Log is the remaining hand-kept copy.

| # | pin | value | how to re-derive |
|---|---|---|---|
| P1 | the register population | **173** in the directory today. ⚠️ This plan's own register makes **174**, and the CENSUSED population is **173** — its own excluded by exact name | `ls "$GOV/governance/knowledge/research"/walk-register-*.md \| wc -l` |
| P2 | ⛔ **the disagreement** | **47 agree / 24 diverge** on walk-set, over plans carrying both | the Item 2 instrument |
| P3 | the missing field | `class` is a column in **5 of 173** registers; `instruction N / record N` appears as PROSE **463×** in registers and **652×** in plan bodies | `grep -l '^\| id \| .*class'`; `grep -ho 'instruction [0-9]* / record [0-9]*'` |
| P4 | what the observer carries | `walk N` and `lens N` — **nothing else**. `_WALK_RE`, `_LENS_RE`, `_CONT_RE` | `grep -nE 'compile' scripts/lens_order_check.py` |
| P5 | observer adoption | **75 of 593** commits touching `knowledge/decisions/` carry a lens token; DC v2.25 measured **18 of 19** plans at the bar NO-RECORD, zero clean | `git log --oneline --since=2026-07-01 -- knowledge/decisions/ \| grep -ciE 'lens [0-9]'` |
| P6 | the projection precedent | manifest `walks`/`yields`/`validation`/`coherence` COMPUTED (DC:253); `LESSONS.md` markers project the forge DB | GLOSSARY `Cycle Manifest`; `[[lessons-corpus-two-records]]` |
| P7 | in-flight | re-derive at execution | `sqlite3 "file:$PWD/lifecycle.db?mode=ro" …` |

## The questions

> **Q1 — Is the body's `walk_data` DERIVABLE from the register today, per plan and per lens?** Not the walk-set only (P2 measured that): reproduce each walk's per-LENS fold count by grouping register rows on `walk × lens`, diff against `cycle_check.parse_block`'s `walk_data`, and classify each plan **exact / derivable-with-gap / not-derivable**, naming the cause. ⛔ **Report the direction of every mismatch** — body-ahead and body-behind are different failures with different remedies.
>
> **Q2 — What does the Cycle Log carry that the register CANNOT supply?** Enumerate every field `parse_block` returns (`walk_data`, `walk_status`, the instruction/record split, `restructuring_walks`, `claims_closure`, `walk_register_ref`) and classify each: **derivable** from register rows · **present as prose** but unstructured · **absent entirely**. ⛔ **The instruction/record split is the convergence signal** — DC: *"the cycle is DONE when a full walk's findings … are all record-class"* — so if it is not derivable, the bar itself is not derivable and the projection cannot carry the verdict.
>
> **Q3 — What would a `class` column cost?** Registers affected, rows affected, and what `walk_register_lint` returns for each once `class` joins `REQUIRED_COLUMNS`. ⛔ **Report the LEGACY_SCHEMA path's effect explicitly** — `_apply_version_status` demotes a non-conformant older-declared register rather than failing it, so the migration's real cost may be a status change, not a wave of failures. ⚠️ Also report what `cycle_check`'s register WARN would emit at that status, since it reaches the verdict path.
>
> **Q4 — Can the OBSERVER reconstruct the sequence the body claims?** Per plan, rebuild the walk/lens series from the commit record alone and compare to the body's. ⛔ **Report coverage separately from agreement**: a plan whose commits carry no lens tokens is NO-RECORD, not a disagreement, and P5 says most of the corpus is exactly that. ⚠️ **This bounds the projection**: a Cycle Log computed from an observer 13% of commits follow would be emitted mostly empty.
>
> **Q5 — Is thread 152 a true blocker?** State precisely what a check would have to compare to prove a PROJECTION is current, then measure whether `_compute_coherence` could do it as written. ⛔ **Answer from the function, not from the claim** — it returns `N/A` at `total_walks == 0` and its `\bwN\b` matches Gate-2 week tokens. ⛔ **If the answer is that no current check can verify a projection, say so plainly**: that makes 152 a precondition rather than an adjacent fix, and this plan must not soften it.

## What this does NOT do

- ⛔ It does not edit `cycle_check`, `walk_register_lint`, `lens_order_check`, `plan_lint`, the register schema, or any doctrine file.
- ⛔ It does not design the emitter, choose the schema version, or propose a migration order.
- ⛔ It does not repair the 24 diverging plans — classifying them IS the deliverable.
- It does not decide whether the Cycle Log becomes a projection. Q3 and Q5 price that; the decision is the CEO's.

## Drafting Cycle

**Tier:** T1 — T-7 fires · T-6 does not (reads four checkers and doctrine, edits none) · T-1 fires (two repositories). T-8 not fired: clone by kind of `drafts/diagnostic-register-coverage.md`.
**Walk register:** `/Users/marklehn/Developer/eluvian-governance/governance/knowledge/research/walk-register-cycle-log-projection-2026-09-06.md`
**Walks:**
⛔ **v0 — no lens has walked it and no §2.0 direction verdict has been issued.** The five lens lines are added at walk 1, each carrying its own `wN N folded — instruction N / record N` token; ⚠️ **a restructuring fold is declared in THIS BLOCK, not only in the register** — `cycle_check` reads the body, and a restructuring declared only in the register produced the WRONG escalation on thread 133.

⚠️ **This plan's own Cycle Log is an instance of its subject.** If it is walked, its body and its register become the 48th agreeing or 25th diverging pair. ⛔ **The instrument must EXCLUDE `walk-register-cycle-log-projection-2026-09-06.md` BY THAT EXACT NAME and report the exclusion** — the population moves 172 → 173 the moment it is created, and its rows change at every fold.

**Closing:** ⛔ **NOT CLOSED — v0.**

## Cycle Manifest

*(to be EMITTED at BAR_MET — ⛔ this placeholder must not survive the freeze; an unemitted manifest reclassified plan 100031 and dispatched it past its class hold.)*

---
---

## STEP 1 — DIAGNOSTIC

---

> **FIRST — before any reads or work: post a short visible message to chat (1–2 sentences) confirming you are starting this plan and stating your immediate next action.**
>
> **Scope:**
> - `bellows/tools/cycle_log_projection_census.py`
> - `/Users/marklehn/Developer/eluvian-governance/governance/knowledge/research/cycle-log-projection-2026-09-06.md`
> - `bellows/knowledge/development/dev-log-cycle-log-projection-2026-09-06.md`
> - `bellows/knowledge/qa/evidence/cycle-log-projection-2026-09-06/census-raw.txt`
>
> **Item 0 — ROOTS.** `GOV=/Users/marklehn/Developer/eluvian-governance`; `BPY=/Users/marklehn/Developer/bellows/.venv/bin/python`; then `test -f "$GOV/GLOSSARY.md"` before proceeding. ⚠️ Hardcoded to this machine and FAILS CLOSED elsewhere, which is the safe direction. ⛔ **This is a KNOWN invariant breach, not a design choice** — CEO 2026-09-06: every machine operates identically and the mini is special ONLY in holding the tuyere database. Threads 89, 113, 145, 146, 99 carry the debt; this plan inherits it and does not fix it.
>
> **Item 1 — re-derive P1–P6 and HALT only on P4's failure.** ⛔ If `lens_order_check` now parses more than `walk` and `lens` from a commit, the observer's content has changed, Q4's premise is void, and this plan must be re-derived. Every other pin mismatch is a FINDING.
>
> **Item 2 — build `tools/cycle_log_projection_census.py`.** ⛔ **Import the shipped parsers and CALL them** — `cycle_check.parse_block`, `cycle_yields.extract_dc_blocks`, `walk_register_lint.extract_tables` / `normalize_column` / `is_fold_table` / `validate_file`, and `lens_order_check`'s own commit parser. **Do not re-implement any of them.** Diagnostic 100032's walk 4 forbade a second reader for a format the lint already parses, and five hand-written parses failed on this corpus in one session. ⚠️ **TWO POSITIVE CONTROLS, both directions, named so they are runnable:** `Done/executable-100030.md` (body `[1-7]`, register 9 rows — an AGREEING pair) and `Done/executable-100017.md` (body `[1-9]`, register `[1,2,3,5,7,8,9]` — a DIVERGING pair, walks 4 and 6 absent). ⛔ **The instrument must report agreement on the first and the exact missing walks on the second before any corpus run.** One control proves only that it reads the case it was written for.
>
> **Item 3 — Q1: the per-lens derivability table**, every plan carrying both records, with the direction of each mismatch named.
>
> **Item 4 — Q2: the field-by-field classification** of what the register can and cannot supply, with the instruction/record split called out as the convergence signal.
>
> **Item 5 — Q3: the migration cost** of a `class` column, with the LEGACY_SCHEMA effect and the `cycle_check` WARN reported separately.
>
> **Item 6 — Q4: observer reconstruction**, coverage reported separately from agreement.
>
> **Item 7 — Q5: whether 152 blocks**, answered from `_compute_coherence`'s source and behaviour, not from its docstring.
>
> **Item 8 — deposit the research note** with a coverage statement naming everything unassessable. ⛔ **If a plan or register cannot be read, SAY SO** — the 100036 parent asserted zero unassessable questions while one was unanswered.
>
> **Item 9 — dev-log**, recording that two hand-kept records of one fact already disagree on a third of the corpus, and that both directions of drift occur.
>
> **Item 10 — commit.** ⛔ **TWO commits in two repos: governance by EXPLICIT PATHSPEC first, bellows LAST.** Record `numstat`.
>
> ⛔ **WRITE INCREMENTALLY.** Create the raw `.txt` FIRST and append each measurement AS IT IS ESTABLISHED, before any note or dev-log is written. ⚠️ Measured 2026-09-04: a cold-panel seat's task died after finishing its work and its findings survived only because its template mandates appending as established.
>
> ⚠️ **Pre-declared benign gate failure.** `test_scope` is `none` and this step deposits raw output as `.txt`, so `_gate_qa_test_result` finds no pytest summary and FAILs. ⛔ **Under `manual_bootstrap` no gate actually runs and there is no plan id to override** — stated so a later reader does not attempt the override act (thread 154).
>
> **Deposits:**
> - `bellows/tools/cycle_log_projection_census.py`
> - `/Users/marklehn/Developer/eluvian-governance/governance/knowledge/research/cycle-log-projection-2026-09-06.md`
> - `bellows/knowledge/development/dev-log-cycle-log-projection-2026-09-06.md`
> - `bellows/knowledge/qa/evidence/cycle-log-projection-2026-09-06/census-raw.txt`
>
> **Post-conditions:** every plan carrying both records classified exact / derivable-with-gap / not-derivable with the mismatch direction named · every `parse_block` field classified derivable / prose / absent · the `class` migration priced with the LEGACY_SCHEMA effect separated from the failure count · observer coverage reported apart from observer agreement · Q5 answered from the function · the self register excluded by exact name and the exclusion reported · ⛔ **no checker, schema or doctrine edited, and no remedy chosen** — it measures, it does not decide.
>
> **STOP. Do NOT proceed further. Do NOT move the plan to Done. Wait for CEO confirmation.**
