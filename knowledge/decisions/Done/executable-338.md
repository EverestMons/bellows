# Executable: a walk-register schema and a warn-first validator — make fold text machine-readable while the corpus is two files

**Type:** Executable
**Project:** bellows
**Depends on:** `bellows/knowledge/research/lint-class-recall-findings-2026-08-10.md` (diag-337 — all 14 instances RECOVERABLE-RECONSTRUCTED, zero verbatim; the finding this plan acts on), `bellows` FORWARD rows **49** (drafts carry no fold-granular history — this plan is its remedy's first half), **51** (§3 doctrine/practice divergence, deferred here), **47** (the single-dialect Cycle Log parser, whose failure mode this plan exists to prevent recurring), `LESSONS.md` **243**, DRAFTING_CYCLE §3 and §6
**Created:** 2026-08-10
**Author:** Planner
**Slug:** `walk-register-schema-2026-08-10` (authoring-time; stable across any crash-redo re-deposit)
**dispatch_mode:** bellows
**pause_for_verdict:** always
**Priority:** 5
**cycle_tier:** T1
**qa_steps:** 3

⚠️ **ID NOTE — the deposit filename is decided AT DEPOSIT.** `id_sequence` read at deposit, never at authoring.

---

## Why this exists

**Diagnostic 337 asked whether the shop's fold record preserves the text of the defects it records. It does not.** All 14 labelled instances came back `RECOVERABLE-RECONSTRUCTED` — a reader's rendering of a description — and **zero came back verbatim.** Every recall figure it produced therefore measured the reconstructor's phrasing rather than the matcher, and no lint class could be priced. Two diagnostics, 336 and 337, ended at the same wall: **the record describes folds in prose a reader can follow and no tool can join.**

**The window is now, and it is narrow.** Measured 2026-08-10 (**re-measure at Step 1; these numbers are an authoring-time read**):

- **Two** walk registers had ever been committed when this was measured, both dated 2026-08-10 — **three including this plan's own cycle register, committed at walk 0.** ⚠️ *(Stated precisely rather than left as "two": the count was already stale when the draft was committed, and Task B must not report that growth as a discrepancy. The signal is a new SHAPE, not a new file.)*
- **Three** distinct column shapes already exist across them — `| # | sub-q | finding | fold |`, `| # | finding | fold |`, `| # | sub | finding | resolution |` — **two of them inside a single file.**
- A third register sits in an untracked scratch directory and will not survive its session.

**The dialect problem row 47 records for Cycle Logs is already present in walk registers at n = 2.** 335's parser reports 36% of Cycle Log rows unparseable across a corpus that grew for months before anyone defined its shape. **This plan defines the shape while the corpus is two files and the cost of conforming them is an afternoon.**

⚠️ **This is the GATE half of a §6 doctrine-and-gate pair, shipped first — the v1.5 precedent, where plan 306 shipped the gate side ahead of the doctrine.** The doctrine half (DRAFTING_CYCLE §3, which still calls the walk register session-local and ephemeral) is **deferred to the corpus path and carried at FORWARD row 51.** This plan changes no doctrine, and says so where a reader would otherwise assume it had.

---

## Method + boundaries

- **Scope boundary: this plan writes exactly THREE files and modifies NONE.** A new schema document, a new standalone validator, and its tests. ⚠️⚠️ **`scripts/plan_lint.py` and `gates.py` are NOT touched, and the validator is NOT wired into any gate chain.** *(Observed by QA Item 1.)* Needing any other write means the premise failed → HALT.
- ⚠️⚠️ **WARN-ONLY, AND NOT WIRED IN. The validator is a standalone script run by hand.** A schema proven on two files has not earned a gate, and **this session's own record is the argument**: four candidate checks were built on an unmeasured premise, fired 376 times, and caught nothing. **The validator earns its wiring by being run against real registers and reporting a measured false-positive rate — not here.** *(Observed by QA Item 2.)*
- ⚠️⚠️ **THE SCHEMA'S ONE LOAD-BEARING FIELD IS `pre_fold_text`, and it carries BYTES, not a description.** This is diagnostic 337's entire finding expressed as a column. **Its four rules are stated ONCE, at Task C.3** — not restated here. *(Observed by QA Item 3.)*
- **HALT ROUTING — the inputs each step reads; if any is missing or unreadable, HALT the step that needs it and name it.** Step 1 reads this plan, **every committed walk register Task B enumerates — three at authoring, not two** — and `bellows/knowledge/research/lint-class-recall-findings-2026-08-10.md`. Step 2 reads Step 1's deposits, the two registers named at D.1, **and this cycle's own register named at D.2**. Step 3 reads both dev logs, the deposited evidence, and `/Users/marklehn/Developer/GitHub/RULE_20_SELF_CHECK_BLOCK.md`. **Re-derive this list from the steps as written before running.**
- ⚠️ **Every walk register THIS PLAN READS lives at the GOVERNANCE ROOT; this plan's commits target BELLOWS.** (The untracked one Task B also enumerates sits in the shop-root scratch directory, not under `governance/`.) Reads against the root name their own `-C`. Every command that stages or commits carries `-C /Users/marklehn/Developer/GitHub/bellows`, and each step asserts `git -C /Users/marklehn/Developer/GitHub/bellows rev-parse --show-toplevel` equals that path immediately before its commit. **The shop has landed three drafting commits in the wrong repository while every command printed success.**
- **Negative results are not evidence on their own:** every absence claim pairs with a positive control, and every literal search uses `grep -F`.
- ⚠️ **No non-ASCII and no backtick, dollar sign or unescaped exclamation inside any `-F` literal this plan mandates.**
- ⚠️ **T-8 fires (novel pattern) and that is why this is T1.** T-6 does **not** fire: no doctrine, template, gate or specialist contract is edited — see the deferral above. T-2/T-5 do not fire.

---

## Conflict Ledger

Planner-run at each culmination. ⚠️ `plan_lint` check (p) reads only inside the `## Drafting Cycle` block, so this section is invisible to it (bellows FORWARD row 44).

- **C1 — nothing is wired in.** Check: `git -C /Users/marklehn/Developer/GitHub/bellows diff` touches neither `scripts/plan_lint.py` nor `gates.py`, and no gate chain imports the validator. *(authoring; QA Item 1)*
- **C2 — `pre_fold_text` is REQUIRED, never optional.** Check: the schema states it required, and the validator WARNs on any fold row lacking it; **a constructed row with the field removed must produce that WARN.** *(authoring; QA Item 3)*
- **C3 — dialects are REPORTED, not rejected, and `PRE-SCHEMA` is a distinct status from `UNCONFORMANT`.** Check: an unrecognised shape is reported with its actual columns named, never skipped; a file with no `schema_version` **declaration** is `PRE-SCHEMA`. ⚠️ **A declaration is a header line of the form `**schema_version:** <value>` before the first table — NOT the token appearing anywhere in the file**, and the validator's fixtures include a file whose only occurrence is prose. *(authoring, amended w1/w2; QA Item 4)*
- **C4 — the two named registers are MEASURED, not conformed.** Check: this plan reports what they contain and edits neither. One of them is diagnostic 337's pinned primary source. *(authoring; QA Item 5)*
- **C5 — no predicted number stands unverified.** Check: every count in the Why section is re-measured at Step 1 and any difference reported as a finding rather than absorbed. *(authoring; QA Item 6)*
- **C6 — the PLAN carries the constraint; the REGISTER carries the history.** Check: **no paragraph in this plan exists only to record how a constraint came to be** — this ledger included. ⚠️ **Two stated exemptions, or the row is unsatisfiable:** the `## Why this exists` section (which records why the PLAN exists, not how a constraint arrived) and the `## Drafting Cycle` block (which §3 mandates as the record). ⚠️ **A justification that tells a future editor NOT to re-break a constraint is a constraint, not history** — A0's do-not-re-add note is the worked example. *(opened w4, applied to itself and bounded w5; QA Item 11)*

---

## How to Run This Plan

**Bootstrap prompt:**
```
Read the plan at knowledge/decisions/in-progress-executable-<id>.md (the daemon renames the deposited placeholder on claim). Execute Step 1 ONLY. After completing Step 1, STOP and wait for my confirmation.
```

---

## STEP 1 — DEV (measure the population, then write the schema)

> **FIRST — post a short visible chat message (1-2 sentences) confirming you are starting this plan.** Do NOT rename this file.
>
> ⚠️⚠️ **EXECUTE STEP 1 ONLY, THEN STOP.** `pause_for_verdict: always` is a header contract the runtime does not police (bellows FORWARD row 46).
>
> **Task A0 — branches, each with its condition stated, catch-all LAST.**
> **(1) NOT-WIRED guard:** `git -C /Users/marklehn/Developer/GitHub/bellows status --porcelain -- scripts/plan_lint.py gates.py` must be empty (C1).
> **(1b) CLEANLINESS of this plan's own write paths — and ONLY those:** `git -C /Users/marklehn/Developer/GitHub/bellows status --porcelain -- scripts/ tests/ knowledge/architecture/ knowledge/qa/ knowledge/development/` must be empty. ⚠️⚠️ **`knowledge/decisions/` is DELIBERATELY EXCLUDED and must not be added back.** The daemon renames plan files on claim and moves them to `Done/` on close **without committing**, so that directory is dirty as a matter of routine — measured at authoring, with a plan closed minutes earlier leaving `D knowledge/decisions/<plan>.md` and an untracked `Done/` copy. **A guard covering it would take the NONE-MATCH branch and HALT on essentially every real dispatch.** *(Weak spots, walk 1. The over-broad probe was inherited from the plan this A0 was cloned from, where it took a different form — a clone reproduces the shape of a defect, not only its text.)*
> **(2) RE-ENTRY key:** `git -C /Users/marklehn/Developer/GitHub/bellows log --oneline -- knowledge/architecture/walk-register-schema.md` for a commit naming the slug.
>
> - **FRESH** = (1) and (1b) empty AND (2) no such commit → proceed at Task B.
> - **RE-ENTRY** = (1) and (1b) empty AND (2) present → re-run and overwrite, noting the re-entry in the dev log.
> - **NONE-MATCH** = anything not matching the two above → **HALT quoting every measurement taken.**
>
> **Task B — MEASURE the population before designing for it (C5).** Enumerate every committed walk register (`git -C /Users/marklehn/Developer/GitHub log --all --name-only --format="" | grep -F "walk-register"`), every one present on disk including untracked ones, and **for each, its actual table header lines verbatim.** ⚠️ **Report the counts against this plan's authoring-time read — two committed, three shapes, one untracked — and state any difference as a finding.** ⚠️⚠️ **EXPECT the committed count to have GROWN by at least one, and do not report that as a discrepancy:** this cycle's own register is committed from walk 0 and any later cycle adds more. **The finding is a change in the SHAPE population, not in the file count** — a fourth distinct column shape is the signal worth reporting; a third file in a shape already recorded is not. *(Observed by QA Item 6.)*
>
> **Task C — write the schema document. Five ordered items; it defines these and nothing else — no process, no doctrine, no cadence.**
>
> **C.1 — The CONTAINER.** A walk register is a markdown document whose fold rows live in pipe-delimited tables, one or more per file, each preceded by a header row naming its columns. Both existing registers use that container — **measured, not assumed**. **A field list with no container is unparseable by anything.**
> **C.2 — The FILE-NAMING convention, and what a tool globs for.** Not optional detail: a validator has to be pointed at files, and the two existing registers are already inconsistent — one is `walk-register-<plan-slug>.md` and this cycle's carries a doubled prefix because its slug begins with the same words.
> **C.3 — The REQUIRED fields:** `id`, `walk`, `lens`, `sub_question`, `origin` (pre-existing or fold-introduced), `finding`, `pre_fold_text`, `resolution`. **`pre_fold_text` is the load-bearing one and has four rules:**
>   - **(a) VERBATIM ALWAYS** — the exact bytes the fold replaced. **No elision, no truncation, no length escape.** *(Observed by QA Item 10.)*
>   - **(b) A fold too large to write verbatim is TOO LARGE TO ATTRIBUTE — split it.** State the remedy, not only the prohibition: a rule that forbids without prescribing gets worked around, and the workaround is a paraphrase, which is the defect this schema exists to end. Two folds each carrying their own bytes beat one carrying neither.
>   - **(c) ESCAPE THE PIPE** (`|` as `\|`, and a literal backslash as `\\`, restored on read). ⚠️ **Both, or the round-trip is ambiguous:** `pre_fold_text` carries plan bytes that already contain backslashes, so escaping only the pipe makes `\|` in the source indistinguishable from an escaped pipe. A markdown table's delimiter is the pipe and `pre_fold_text` carries arbitrary plan bytes; an unescaped one silently truncates **precisely the rows this schema exists to preserve**, and class `r` is itself defined by a pipe. **The validator round-trips it byte-identical.**
>   - **(d) A pure ADDITION** records the literal `ADDITION`, so absence and addition stay distinguishable. Tabs and newlines escaped; **no other normalization.**
>
> *(All four observed by QA Item 3. The history behind (a) and (b) — an elision rule folded three times and then deleted on a measured premise — is in the walk register, not here.)*
>
> **C.4 — The `schema_version` DECLARATION form** (see the Conflict Ledger's C3): a header line before the first table, not the token appearing anywhere in the file.
> **C.5 — The ENCODING**, stated for the file and used explicitly by the validator rather than left to locale default.
>
> ⚠️⚠️ **The schema document states its own COST honestly, in a section a reader cannot miss:** capturing `pre_fold_text` means every fold's author copies the pre-edit bytes before editing. **That is a real authoring burden and this plan does not pretend otherwise** — it is the price of the record being joinable, and diagnostic 337 is what the alternative costs.
>
> **Deposits:**
> - `bellows/knowledge/architecture/walk-register-schema.md` — the schema, its required fields, its cost section, and the measured dialect table from Task B
> - `bellows/knowledge/development/walk-register-schema-dev-log-step-1-2026-08-10.md`

---

## STEP 2 — DEV (the validator and its tests)

> **Task S2-A0.** Step 1's deposits exist and its commit names the slug; otherwise HALT. Re-assert A0's (1) and (1b) guards.
>
> **Task S2-B — write the validator. Four ordered items.**
>
> **B.0 — Say what the validator is POINTED AT.** It accepts either a single register path or a directory to glob using C.2's naming rule, and **states which in its usage line.**
> **B.1 — CLONE THE SHAPE of `scripts/cycle_yields.py` (plan 335); read it FIRST.** The shop's shipped precedent for this exact pattern: parse a record format out of the corpus, emit TSV, carry a per-file status, and **report unparseable input rather than skipping it.** Matching its shape is what lets the two compose into one view of a cycle. ⚠️ **Read it for what it already DECIDED** (§2.6's inverse question) — its `STATUS_*` and dialect handling are prior art to inherit, not re-derive.
> **B.2 — Emit one row per fold row, with a per-ROW conformance mark, plus a per-file status.** *(Observed by QA Item 10.)* ⚠️ **Per-row is not decoration: without it a 90%-compliant and a 0%-compliant register are both just `UNCONFORMANT` and an author fixing rows sees no movement.** A binary verdict on a format with a real authoring cost is a verdict authors route around — **which is how a check earns the 100% fire rate that killed the four classes this session priced.**
> **B.3 — Name what did not parse.** An unconformant file names its **actual columns** in the output (C3); a file carrying more than one table shape names **both** — measured: one of the two existing registers does exactly this, so single-shape-per-file is already false at n = 2.
> **B.4 — STATUS PRECEDENCE: `PRE-SCHEMA` is evaluated FIRST.** A file with no `schema_version` declaration is `PRE-SCHEMA` **whatever its shapes**, and its shape analysis is reported as detail on that row. ⚠️ **Both existing registers are PRE-SCHEMA and one is multi-shape — under unordered rules that file carries two statuses at once.** *(Observed by QA Item 4.)*
>
> **Task S2-C — tests, and one of them constructs the violation.** Cover: a conformant row; a row missing `pre_fold_text`; a file with two shapes; a file with no table at all; a file with no `schema_version` (expect `PRE-SCHEMA`). ⚠️⚠️ **Every test uses a FIXTURE it constructs, never the live registers at the governance root.** A test reading a live register fails the moment that register gains a row — **breaking the full suite for every unrelated plan that runs QA afterwards**, and the registers are edited on every walk of every cycle by design. ⚠️⚠️ **The missing-`pre_fold_text` test must CONSTRUCT that row and assert the WARN fires** — a test asserting the validator runs without error proves nothing, and this plan's own session recorded three checks that passed by existing rather than by working. *(Observed by QA Item 3.)*
>
> **Task S2-D — run the validator against the corpus. Four ordered items.** (C4 — measure, do not edit.)
>
> **D.1 — The PRE-SCHEMA baseline, two files, named:** `governance/knowledge/research/walk-register-group4-rescope-2026-08-10.md` and `governance/knowledge/research/walk-register-lint-class-recall-2026-08-10.md`.
> **D.2 — This cycle's own register, reported SEPARATELY** — it declares a `schema_version` and is the schema's test subject, not part of the baseline.
> **D.3 — Record each file's BLOB ID beside its result.** A verdict gate puts arbitrary wall-clock before QA and any concurrent cycle edits its own register by design, so an unpinned baseline does not describe the bytes QA reads. Step 3 asserts D.1's two blob ids unchanged.
> **D.4 — Report whichever status each returns; do not steer toward the expected one.** The author expects UNCONFORMANT for the baseline — **but a CONFORMANT result would mean the schema was written to match what exists rather than to fix it, which is a finding about the SCHEMA and outranks the baseline.** *(Observed by QA Item 5.)*
>
> ⚠️ **Targeted tests only in this step — the full suite runs in QA.**
>
> **Deposits:**
> - `bellows/scripts/walk_register_lint.py`
> - `bellows/tests/test_walk_register_lint.py`
> - `bellows/knowledge/qa/evidence/walk-register-schema-2026-08-10/existing-registers-run.txt`
> - `bellows/knowledge/development/walk-register-schema-dev-log-step-2-2026-08-10.md`

---

## STEP 3 — QA

> **(A) Rule 20 self-check block** — emit the canonical block from `/Users/marklehn/Developer/GitHub/RULE_20_SELF_CHECK_BLOCK.md` (absolute operand, read live, never recalled). The receipt carries the canonical header `Rule 20 — QA Self-Check Results` and, when every item passes, the canonical verdict line `PASSED — SELF-CHECK PASSED`. **This plan deposits real evidence files, so the FULL canonical block applies.** ⚠️ **`required_evidence_files` is NOT restated here — it is the evidence-directory subset of `## Scope`, read from there.**
>
> **(B) Deliverable verification (Rule 8 / Rule 17):**
> - **Item 1 — nothing wired in.** `plan_lint.py` and `gates.py` unchanged; no gate chain imports the validator (**C1**).
> - **Item 2 — the validator is standalone and warn-only.** No code path alters any exit code the daemon reads.
> - **Item 3 — `pre_fold_text` is required and the check can FAIL.** The schema states it required, and **the constructed missing-field test is exercised and its WARN shown in the receipt** (**C2**).
> - **Item 4 — dialects are reported, not skipped, and `PRE-SCHEMA` is distinct from `UNCONFORMANT`.** An unconformant file names its actual columns; a two-shape file names both; **a file with no `schema_version` declaration returns `PRE-SCHEMA` and is shown doing so** (**C3**).
> - **Item 5 — the baseline registers were measured, not edited.** The **two registers named at D.1** have blob ids matching those Task S2-D recorded, and the raw run is deposited (**C4**). ⚠️ **Scoped to those two files, NOT to `governance/knowledge/research/`** — that directory holds this cycle's own register, edited every walk by design.
> - **Item 6 — the authoring-time counts were re-measured.** Task B's figures are stated against the Why section, with any difference named (**C5**).
> - **Item 7 — full suite, and `tests/test_walk_register_lint.py` is in it.** `python3 -m pytest` over the bellows suite, with the raw summary line pasted, **plus the collected count for that module specifically** — a suite that passes without collecting the new module proves nothing about it. ⚠️ **Report both counts; predict neither here.**
> - **Item 8 — raw output.** Every count in the receipt is the command's own stdout, pasted.
> - **Item 9 — the pipe AND the backslash round-trip.** Fixtures whose `pre_fold_text` contains a `|`, a `\`, and the sequence `\|` are each written, read back and **byte-compared**; the constructed unescaped case is shown corrupting the row. **All three, because `\|` in real plan bytes is what makes a pipe-only escape ambiguous.**
> - **Item 10 — per-row conformance is emitted, and truncation is REJECTED.** The output carries a conformance mark **per fold row**, not only per file; and a fixture whose `pre_fold_text` is a paraphrase or carries an ellipsis rather than the replaced bytes is **marked non-conformant**.
> - **Item 11 — the plan carries no history-only paragraph, and `ADDITION` is exercised.** A read of this plan finds no paragraph existing solely to record a constraint's origin (**C6**); and a fixture whose fold is a pure addition records the literal `ADDITION` and is marked conformant, while an empty field is not.
>
> **Deposits:**
> - `bellows/knowledge/qa/walk-register-schema-qa-2026-08-10.md`
> - `bellows/knowledge/development/walk-register-schema-dev-log-step-3-2026-08-10.md`

---

## Scope

```
bellows/knowledge/architecture/walk-register-schema.md
bellows/scripts/walk_register_lint.py
bellows/tests/test_walk_register_lint.py
bellows/knowledge/qa/evidence/walk-register-schema-2026-08-10/existing-registers-run.txt
bellows/knowledge/qa/walk-register-schema-2026-08-10.md
bellows/knowledge/development/walk-register-schema-dev-log-step-1-2026-08-10.md
bellows/knowledge/development/walk-register-schema-dev-log-step-2-2026-08-10.md
bellows/knowledge/development/walk-register-schema-dev-log-step-3-2026-08-10.md
```

---

## Drafting Cycle

**Tier:** T1 — **T-8 fires** (novel pattern: no shipped plan defines a record schema plus a standalone validator for it). **T-6 does NOT fire** — no doctrine, template, gate or specialist contract is edited; the §3 amendment is deferred to FORWARD row 51 and the corpus path. T-1/T-2/T-5 do not fire.

**Walks:** 1. Register at `governance/knowledge/research/walk-register-walk-register-schema-2026-08-10.md`, committed per phase from walk 0 and written in the schema this plan proposes — **the schema's first test subject; if the shape proves unworkable that is a finding about the schema, reported rather than dropped.**

- Weak spots:          w1 4 — 4 pre / 0 fold; w2 3 — 2/1; w3 3 — 0/3; w4 2 — 0 pre / 2 fold.
- Destruction:         w1 2 — 2 pre / 0 fold; w2 2 — 1/1; w3 1 — 0/1; w4 dry (subsumption verified).
- Vulnerabilities:     w1 3 — 2 pre / 1 fold; w2 2 — 0/2; w3 1 — 0/1; w4 1 — 0 pre / 1 fold.
- Integration-record:  w1 2 — 1 pre / 1 fold (record-decay); w2 1 — 1/0; w3 1 — 0/1; w4 1 — 0 pre / 1 fold (structural).
- ACID:                w1 2 — 2 pre / 0 fold; w2 1 — 0/1; w3 joint with Integration; w4 1 — 0/1; w5 1 — 0/1; w6 1 — 0/1; w7 dry.
  (w7 by lens: Weak spots 2 — 0/2 · Destruction 1 — 0/1 · Vulnerabilities dry, swept mechanically · Integration dry · ACID dry.)
  (w5 by lens: Weak spots 2 — 0/2 · Destruction dry, subsumption verified · Vulnerabilities 1 — 0/1 · Integration 1 — 0/1, routed to bellows FORWARD 54 rather than folded here.)
  (w6 by lens: Weak spots 2 — 0/2 · Destruction dry, subsumption verified · Vulnerabilities/ACID 1 — 0/1 joint, verified mechanically · Integration 1 — 0/1.)

**Conformance (§5):** run at walk 0 and re-run after the walk-1 folds. ⚠️ **The post-fold run raised a NEW WARN the lenses had not seen** — walk 1's folds made Step 3 mention tests while declaring no test scope, so QA Item 7 now names the module it verifies and requires its collected count separately. **Last run: walk 1 post-fold, exit code 0**; remaining WARNs are the earned fold-as-last-event and two path artifacts of linting from the governance root. *(Word counts live in the walk register.)*

**Conflicts:** C1-C5 opened at authoring; C3 rewritten at walk 1 (Destruction) to split `PRE-SCHEMA` from `UNCONFORMANT`. None in conflict.

**Closing:** ⚠️⚠️ **§2's BAR IS MET AT WALK 7 — recorded as a JUDGED STOP with its residue enumerated, and with the one judgement call stated so it can be overridden.**

**Yields:** w1 13 folded (2 fold-introduced) · w2 9 (5) · w3 6 (6) · w4 5 (5) · w5 5 (5) · w6 4 (4) · **w7 3 (3).**

- **Condition 2 — predominantly fold-introduced: MET, 3 of 3.** Five consecutive walks with **zero pre-existing defects**; unbroken since walk 2.
- **Condition 1 — record-class only: MET, 3 of 3.** Residue by class: **one stale-count sweep** (HALT ROUTING and the Method bullet said "two registers" where there are three), **one precision correction** (not every register sits under `governance/`), **one C6 violation** (`B.0` carried a history-only parenthetical).

⚠️⚠️ **THE JUDGEMENT CALL, stated rather than buried.** The stale-count finding sits on HALT ROUTING, which is an instruction — and at walk 6 a HALT ROUTING finding was classed **non**-record-class. **The two differ:** walk 6's omitted a file Step 2 depends on entirely, so nothing would have halted for it; walk 7's undercounts a set **Task B enumerates by glob regardless**, so the agent's behaviour is unchanged and only the prose was wrong. **If the CEO reads that as execution-changing, the bar is not met and walk 8 is owed.**

⚠️ **The sweep was mechanical, not by eye** — the previous walk fixed one site of this class and missed another, so walk 7 enumerated every site by pattern before folding. Two sites remained and were verified correct in place.

⚠️ **Closing-record re-read (§2.7): run, and it produced this paragraph.** Verified mechanically at the close: **zero dangling item references, nine mandates carrying inline observer ids, `plan_lint` FAIL count 0.**

**Deposited once, after this close.** ⚠️ This artifact is **UNDEPOSITED** until then.
