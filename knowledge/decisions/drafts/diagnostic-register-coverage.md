# bellows — diagnostic: WHAT IS THE ORPHAN-ID POPULATION IN THE WALK REGISTERS — how many findings a register NAMES but carries no schema row for, across every id convention and schema state

**Date:** 2026-09-04 | **Project:** bellows | **Tier:** Small | **Dispatch Mode:** bellows | **cycle_tier:** T1 | **Test Scope:** none (read-only diagnostic — the instrument is new code with no consumers; this step deposits raw output as `.txt` evidence, which `qa_test_result` will refuse to certify having no pytest summary to parse: the pre-declared benign gate failure of the gate note below) | **Execution:** Step 1 (DIAGNOSTIC) | **pause_for_verdict:** always | **known_failures:** 0

**auto_close:** false

**Depends on:** tuyere thread **135** (the filing — `walk_register_lint` attests row SHAPE, not coverage) and **127** (why 135 carries no annotation: an open thread cannot be annotated). Clone origin: `Done/diagnostic-100036.md` — same kind, read-only, one Item per question, closed 2026-09-04. ⚠️ **Read that parent's failure too**: its final question was answered from a RESTATEMENT rather than its instrument, and its coverage statement claimed nothing was unassessable while that question said "not re-derivable".

## What this decides

**Nothing.** ⛔ **PT Rule 82.** Whether panel findings belong in the schema table, whether the lint needs a coverage assertion, and whether a shop-wide id convention is worth imposing are three design questions this plan does not touch. It produces the population and chooses nothing.

## Why this exists

⛔ **FIVE hand-probes have failed to measure this, each on a DIFFERENT structural assumption, and each produced a plausible number that could have been reported.** Measured 2026-09-04 by the author, in order:

1. hardcoded `len(cells) >= 8` → excluded every row of the 0.2 schema, which has 5-cell rows. Reported "39 of 70 registers orphaned".
2. switched to `walk_register_lint.validate_file` but read `r.get("id")` → that key does not exist; the returned rows are LINT REPORT rows (`file, line, table, row_status, …`), not the register's findings. Reported "70 of 70 orphaned".
3. inspected the structure and found the lint has **no notion of finding identity at all** — `"id"` is a name it checks for PRESENCE and never reads.
4. shape-aware header parse keyed on the header's own `id` column → still reported 100% orphan for registers that plainly have rows.
5. the cause of (4): the **id CONVENTION varies** — `d1`, `w1-1`, `W1-1`, `S1-5` all observed — and a regex accepting two of them silently drops the rest.

⚠️ **THAT IS THE LICENSING ARGUMENT.** Five readings of the same corpus, five different wrong answers, every one from the author imposing a shape the corpus does not have. The only approach not yet tried is an instrument that derives the conventions from the corpus instead of assuming them.

**The harm being sized:** `walk_register_lint` returned CONFORMANT over a register holding schema rows for **14 of 48** findings, and that verdict was quoted upward as evidence the register was in order (thread 135).

| # | pin | value | how to re-derive (⛔ `$GOV`-rooted; assert non-empty OUTPUT, never `rc`) |
|---|---|---|---|
| P1 | the register population | **172** files matching `walk-register-*.md` | `ls "$GOV/governance/knowledge/research"/walk-register-*.md \| wc -l` |
| P2 | schema states, FOUR not one | `0.3` ×119 · `0.1` ×15 · `0.2` ×13 · **undeclared ×21** | `grep -h -oE 'schema_version:\*\* \`?[0-9.]+'` over the population, plus a count of files with no such line |
| P3 | the lint's contract — ⛔ **PINNED, because this pin is a claim about a FILE's contents** (lens 1, 1.3): `scripts/walk_register_lint.py` sha256 `e50b63a1bd403375f423e20ae08d3509c35c674721f7c06e3264714a12838aec` — without it P3 goes stale silently the next time that file is edited, and this plan's whole premise rests on it | `REQUIRED_COLUMNS = ["id","walk","lens","sub_question","origin","finding","pre_fold_text","resolution"]` — ⛔ **`"id"` is a name checked for PRESENCE; the cell's VALUE is never read** | `sed -n '31,34p' scripts/walk_register_lint.py` |
| P4 | the lint's status vocabulary | `PRE-SCHEMA`, `CONFORMANT`, `UNCONFORMANT`, `NO_TABLE`, `LEGACY_SCHEMA`, `FUTURE_SCHEMA` | `grep -oE 'STATUS_[A-Z_]+ = "[A-Z_-]+"' scripts/walk_register_lint.py` |
| P5 | ⛔ id conventions — **OBSERVED, NOT ENUMERATED** | `d1` · `w1-1` · `W1-1` · `S1-5` seen in a 3-register sample. ⚠️ **This pin BOUNDS the shape of the answer and is NOT the answer.** 100036's P6 shipped a partial hand count as a population and walk 5 caught it; Q1 must derive the set mechanically | read the id column of a sample, then let the instrument enumerate |
| P6 | ⛔ what makes this hard, and it is not carelessness | rows may carry **unescaped pipes inside inline code spans** — the register pre-commit hook warns that this restores the cell count while shifting every field one place left, so a row passes carrying scrambled data | the hook's own failure text |
| P6b | ⛔ **MULTI-TABLE IS THE MAJORITY CASE, NOT AN EDGE** | **117 of 172 registers (68%) carry MORE THAN ONE `\| id \|` header table.** Every one of the five failed probes assumed a single table per file. ⚠️ Consequences the instrument must handle: a file's tables may differ in shape; an id may appear in more than one table; and a parser that binds one header and resets on the first non-table line will silently read only the first block | `grep -c "^\| id \|"` over the population |
| P6c | the other degenerate populations, measured | **2** registers are `NO_TABLE`; **21** declare no `schema_version` at all. ⛔ These are DIFFERENT AXES — a file may have tables and no version, or a version and no table — and collapsing them loses which is which | the lint's status per file; a `schema_version` grep |
| P7 | in-flight | re-derive at execution | `sqlite3 "file:$PWD/lifecycle.db?mode=ro" …` |

## MUST-PRESERVE

- ⛔ **The instrument DERIVES the id convention from each table's own header and rows — it never matches a hardcoded pattern.** That assumption is what failed five times.
- ⛔ **Read-only. No register is edited, and no `knowledge/decisions/` directory receives a plan-shaped file.**
- ⛔ **Deposits keep all three paths** — with only the dev-log, `_parse_plan`'s fallback yields one path under `knowledge/` and `_assign_class` returns `app-feature`, which AUTO-CLEARS (measured 2026-09-04).
- **Report per SCHEMA STATE.** A single corpus-wide percentage over four schema states is the shape of answer this plan exists to avoid.

## ⛔ What this population would AUTHORIZE — priced here, because a diagnostic's findings license downstream change (lens 2, 2.4)

⚠️ **A number this plan produces could license two changes, each with a 172-register blast radius, and neither is a decision this plan may make:**

1. **Imposing a shop-wide id convention.** At least four are in use (P5). "Normalize them" reads as tidying and is a rewrite of **172 committed registers**, every one an append-only walk record whose rows are cited by plan bodies and panel reports. ⛔ **A convention change is a corpus migration, not a lint fix.**
2. **Promoting orphan rows to `UNCONFORMANT`.** `walk_register_lint`'s status is read as "this register is in order" and is quoted in freeze records. Flipping the verdict on an unknown share of 172 registers would invalidate closing records already relied on — ⛔ **the same shape as thread 117's measured 13-compliant→0, which is why the emitter key set is a versioned interface.**

⛔ **This plan therefore reports the population and its DISTRIBUTION and prices neither change.** ⚠️ A later plan acting on these findings must measure its own blast radius against the 172 — the count alone does not license either move, and this note must not be cited as if it did.

## The question

⛔ **ONE question, deliberately.** 100036 asked seven and answered its last from a restatement.

> **Q1 — For every walk register, how many finding-ids does the file NAME that carry no schema row?** Report per register and per schema state: ids mentioned, ids with a row, orphans, and the id convention(s) the file uses. ⛔ **Derive the convention from the table's own header and cells; never match a fixed pattern.** ⛔ **AND HANDLE EVERY TABLE IN THE FILE (P6b): 68% of registers carry more than one.** Bind a header per table, not per file; report an id found in more than one table rather than counting it twice; and ⛔ **classify `NO_TABLE` and `no schema_version` as SEPARATE axes (P6c)**, never merged into one "unclassifiable" bucket. ⛔ **A register with NO table is not an orphan case — classify it separately**, or the count conflates "findings not rowed" with "no table exists". ⚠️ **Report rows the lint would MISS for a reason other than absence** — a shifted row from an unescaped pipe is present-but-unreadable, which is a third state, not a fourth kind of orphan. ⛔ **DETECTION METHOD, or the state is unanswerable (lens 1, 1.4):** a shifted row has MORE cells than its table's header while still parsing as a row; compare each data row's cell count against its own header's, and report a mismatch as `unreadable` rather than guessing which cell holds the id. ⚠️ **If that count-comparison proves insufficient — a pipe inside a code span may be balanced by another — say the state is UNMEASURABLE and report the count of rows it could not classify.** An unanswerable sub-question is a FINDING; the parent plan's coverage statement claimed zero unassessable while one question was unanswered.

## Drafting Cycle

**Tier:** T1 — **T-7 fires** (a later plan will act on this population without re-verification). **T-6 does NOT fire**: read-only; it READS `walk_register_lint`, which is not editing it. **T-8 not fired**: clone by kind of `Done/diagnostic-100036.md`.
⚠️ **This cycle is also a TEST of the six drafting-cycle fixes shipped 2026-09-04** (`fold_check` VACUOUS refusal · `cycle_check` BASIS on escalation · `plan_lint` (q) pin resolution · `propagation_check` id/line-ref masking). Baselines from the cycle those fixes came out of: `propagation_check` ran 164/52/69/89 divergences, **100% hand-classified false positive**; `fold_check` reported CLEAN three times **vacuously**; `cycle_check` returned the weaker of two escalations silently. ⛔ **Record this cycle's equivalents per walk so the comparison is measured, not felt.** `mutation_check`'s two fixes are NOT exercised by a read-only diagnostic — claim no coverage there.
**Walk register:** `/Users/marklehn/Developer/eluvian-governance/governance/knowledge/research/walk-register-register-coverage-2026-09-04.md`
**Walks:** walk 0 complete (context pin). ⛔ **v0 — NO LENS HAS WALKED IT and NO DIRECTION VERDICT has been issued.**

## Cycle Manifest

*(to be EMITTED at BAR_MET — ⛔ this placeholder must not survive the freeze)*

## STEP 1 — the census (read-only; decides nothing)

> **Scope:**
> - `tools/register_coverage_census.py`
> - `/Users/marklehn/Developer/eluvian-governance/governance/knowledge/research/register-coverage-2026-09-04.md`
> - `knowledge/development/dev-log-register-coverage-2026-09-04.md`
>
> **Item 0 — ROOTS, same invocation as every use.** `GOV=/Users/marklehn/Developer/eluvian-governance`; ⚠️ **hardcoded to THIS machine (lens 3, 3.1)** — the shop Air keeps governance under `~/Developer/GitHub` (threads 89, 113), so this block FAILS CLOSED there, which is the safe direction; the plan is `shop-infra` and holds for a human release on the machine that releases it. ⛔ Stated, not fixed: resolving the root as `bellows_root.py` does belongs in a plan that can test both machines. `test -n "${GOV:-}"` then `test -f "$GOV/GLOSSARY.md"` before proceeding. ⛔ Governance by absolute path with `git -C "$GOV"`, never `cd`; commit by EXPLICIT PATHSPEC; bellows LAST.
>
> **Item 1 — re-derive P1–P6 and HALT only on P3's failure.** If `walk_register_lint` now READS the id cell's value, the tool has gained a notion of finding identity, this plan's premise is void, and the correct outcome is a HALT. Every other mismatch is a finding.
>
> **Item 2 — build `tools/register_coverage_census.py`.** ⛔ **Import `walk_register_lint` and call it for the STATUS; do not re-implement its validation.** ⛔ **Derive each table's `id` column index from its own header row, and the id convention from the values found there** — no fixed pattern. ⚠️ **POSITIVE CONTROL before any corpus run, on a NAMED register (lens 1, 1.2 — an unnamed control is not runnable):** `walk-register-qa-steps-parsing-2026-09-04.md`, whose id column carries `w1-1 … w5-1` under schema `0.3`, and `walk-register-dc-coldfront-2026-08-13.md`, whose ids are `d1 …` under schema `0.2`. ⛔ **Two controls, two conventions and two schema states** — one register would prove only that the instrument reads the convention it was written for, which is exactly how probe 5 failed. Confirm a non-empty rowed-id set from BOTH before any corpus run. Five probes failed by returning plausible empties; an empty result must be proven, never assumed.
>
> **Item 3 — Q1: the per-register table**, with per-schema-state subtotals, the conventions found, and the three states kept apart: no-table · rowed · named-but-unrowed.
>
> **Item 4 — deposit the research note** with a coverage statement naming anything unassessable. ⛔ **If a register cannot be read, SAY SO** — the parent's coverage statement asserted zero unassessable questions while one was unanswered.
>
> **Item 5 — dev-log**, recording the five failed hand-probes and the assumption each imposed.
>
> **Item 6 — record THIS CYCLE'S battery numbers per walk** against the baselines in the Drafting Cycle block, so the fixes' effect is measured.
>
> **Item 7 — commit** (message tagged with the plan id); `numstat` — **TWO commits in two repos**: 1 governance, 2 bellows.
>
> ⚠️ **Pre-declared benign gate failure.** `test_scope` is `none` and this step deposits raw output as `.txt`, so `_gate_qa_test_result` finds no pytest summary and FAILs. Named here, overridden by the Planner with reference to this note — the 100032/100034/100036 precedent. The override act is `tools/clear_plan.py --override-gate <id> 1 qa_test_result --ref <committed path>`; ⛔ commit the justification BEFORE the override, which is write-once.
>
> **Deposits:**
> - `/Users/marklehn/Developer/eluvian-governance/governance/knowledge/research/register-coverage-2026-09-04.md`
> - `bellows/knowledge/development/dev-log-register-coverage-2026-09-04.md`
> - `tools/register_coverage_census.py`
> - `knowledge/qa/evidence/register-coverage-2026-09-04/census-raw.txt`
>
> ⛔ **The `.txt` is listed DELIBERATELY (lens 2, 2.1).** The gate note above pre-declares that this step "deposits raw output as `.txt` evidence" and that `qa_test_result` will refuse to certify it — but the Deposits block listed no `.txt`, so the pre-declaration described an artifact that would never exist and the benign failure could not fire for its stated reason. ⚠️ **Measured on plan 100038 the same day:** its header carried the identical pre-declaration, `qa_step_detection` read the step as not-QA, the gate never ran, no `.txt` landed, and its numbers became reproducible only by re-running the census. ⛔ **Raw output is the evidence; a note that summarises it is not.**
>
> **Post-conditions:** every register in P1's population classified; per-schema-state subtotals reported; id conventions DERIVED and listed; no-table, rowed, named-but-unrowed and present-but-unreadable kept as distinct states; this cycle's battery numbers recorded against the stated baselines; ⛔ **no recommendation and no design anywhere in the note** — it sizes, it does not choose.
