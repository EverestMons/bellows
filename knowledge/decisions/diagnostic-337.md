# Diagnostic: measure RECALL of the four lint classes against a labelled positive set — the half diag-336 could not reach

**Type:** Diagnostic
**Project:** bellows
**Depends on:** `bellows/knowledge/research/lint-class-census-findings-2026-08-10.md` (diag-336 and its second-reader addendum A1-A6, whose open question this answers), `governance/knowledge/research/walk-register-group4-rescope-2026-08-10.md` at pinned commit `a7077ca` (the **primary** record of the instances — the specimen record and the undeposited post-fold draft are secondary sources, see Task C.3), `bellows` FORWARD rows **48** (this measurement is owed) and **49** (no fold-granular draft history), `LESSONS.md` **242**, `funnel-mechanization-v0-2026-08-08.md` §4 (a class ships warn-first with a measured FP rate)
**Created:** 2026-08-10
**Author:** Planner
**Slug:** `lint-class-recall-2026-08-10` (authoring-time; stable across any crash-redo re-deposit)
**dispatch_mode:** bellows
**pause_for_verdict:** always
**Priority:** 5
**cycle_tier:** T1
**qa_steps:** 2

⚠️ **ID NOTE — the deposit filename is decided AT DEPOSIT.** `id_sequence` read at deposit, never at authoring.

---

## Why this exists

Diag-336 priced four candidate lint classes and rejected all four: **zero true positives, 376 false.** Its second-reader addendum found the measurement was aimed at a population that could not contain a positive.

| | |
|---|---|
| **The gap** | 336's covered set — 10 drafts, 139 commits — excludes **both** cycles that generated the hypothesis: the v2.0 specimen-1 cycle and the 335 collector cycle. |
| **Why, mechanically** | `draft-group4-rescope-2026-08-10-UNDEPOSITED.md` has **exactly one commit** (the session wrap). A method that infers folds from per-commit count deltas has no pre-fold revisions to read there. |
| **What 336 therefore measured** | **Precision only.** `Done/` is post-fold by construction, so its only retained instances are the ones no reader caught. Precision over a population with no positives is unfalsifiable: every matcher scores zero, including a correct one. |
| **What is missing** | **Recall against known positives.** The instances exist and are recorded by name in the walk register, twice matching the withdrawn build plan's wording verbatim. |

⚠️ **The register is the PRIMARY record, not the only one.** An earlier drafting called it "the only surviving record", which contradicts Task C.3's own list of candidate sources — the specimen record and the post-fold undeposited draft are secondary and are read too. **An overstated scarcity claim would license treating a gap in the register as a gap in the record.**

**This diagnostic supplies the missing half and nothing else.** It does not re-run 336's census, does not re-open its precision figures, and does not build a check.

⚠️ **It is deliberately SMALL.** 336 spent 220+ lines to price four regexes and its own findings recorded that cost as a funnel datum. A successor that repeats the size repeats the mistake. If this plan grows past its two steps, that growth is itself a finding to report rather than absorb.

⚠️ **Growth is measured in WORDS against 336's plan, never in lines, and the figures live in the walk register rather than here.** On a breach: cut each fold note to the constraint it establishes; the reasoning goes to the register. *(Why lines fail, and the metric's own three-walk error: LESSONS 243.)*

---

## Questions

**"Unknown" is an acceptable answer that must be reported as such.**

- **Q1 — Is the pre-fold source text RECOVERABLE?** For each instance the register names, classify: **RECOVERABLE-VERBATIM** (the original offending line survives somewhere readable), **RECOVERABLE-RECONSTRUCTED** (the register describes it precisely enough to rebuild the line, and the reconstruction is marked as such), or **UNRECOVERABLE**. ⚠️⚠️ **This is the load-bearing question and a large UNRECOVERABLE count is a FINDING, not a failure.** The register records defects as *descriptions* — "the version literal carried a section sign" — not necessarily as the lines that carried them. **If most instances are unrecoverable, then no lint class can be priced against THIS cycle from THIS record, and saying so is worth more than a recall figure over the remainder.** ⚠️ **Scoped deliberately, and walk 2 tightened it:** the earlier phrasing said "retires the whole approach", the same over-claim **walk 1's** Destruction lens struck from Q4 while leaving this site standing. Unrecoverability here is a property of a cycle committed once at wrap, not of the method. ⚠️ *(The clause misattributed that strike to walk 2's Destruction lens, which had not yet run when the sentence was written — corrected by that lens on its own pass.)*
- **Q2 — Recall of the four matchers AS WRITTEN** against the recoverable set. Per class: of N labelled positives, how many does the matcher fire on? ⚠️ **Report as a COUNT with its denominator, never as a percentage** — the set is small (**authoring-time read of the register: roughly eight instances across the cited lines; re-count, do not inherit this number**), and a rate over single digits reads as precision the measurement does not have. ⚠️⚠️ **N is the RECOVERABLE count, not the register-named count, and BOTH are reported** — as `k of N recoverable, of T named`. Scoring an UNRECOVERABLE instance as a miss blames the matcher for the record's gap; hiding it inflates the denominator's apparent authority. ⚠️⚠️ **A class with N = 0 reports "NOT MEASURABLE (N=0)", never "0 of 0".** A measured zero and an unmeasurable zero are different inputs to Q4 and **336's whole defect was the two being written the same way.** ⚠️⚠️ **And the count is reported SPLIT — verbatim rows and reconstructed rows separately, never pooled** (the rule and its reasoning are stated once, in Task D). This question is what a later reader cites, and it carried an unsplit denominator for a full walk after the split was mandated in the step.
- **Q3 — Recall of the REDESIGNED matchers** for `m` and `q` — the operand-parsing variants 336 §(vi) names — against the same set. ⚠️ **`r` and `s` are NOT redesigned here.** `r`'s redesign direction is shell-aware pipe detection and no instance justifies building it yet; `s` is HOLD on grounds a redesign cannot touch (a regex reading "Record all four" cannot know the list has five items). ⚠️⚠️ **What is closed is 336's GROUND — that a regex cannot verify a count — not the class.** If Q1 surfaces an `s` instance detectable by a mechanism 336 never considered (a numeral whose enumeration is a machine-countable list in the same block, say), **that is a finding to REPORT, not to suppress.** A "do not re-litigate" clause that silences new evidence is a guard that has become a gag.
- **Q4 — Revised disposition per class, stating precision and recall AS A PAIR.** SHIP-warn / HOLD / REDESIGN / **RETIRE-PENDING-INSTRUMENTATION**. ⚠️ **A disposition citing one of precision or recall without the other is incomplete and is a FAIL.**
  ⚠️⚠️ **RETIRE IS SCOPED TO THE RECORD AS IT EXISTS TODAY, AND THE NAME CARRIES THE SCOPE.** The earlier drafting of this question said a class whose positives are unrecoverable "cannot be priced by any future census either" — **that is false and it is the most destructive sentence this plan could ship.** Unrecoverable *from a cycle that was committed once at wrap* is not unrecoverable in principle: **bellows FORWARD row 49 is being fixed right now, and this plan's own draft is being committed per phase from walk 0**, so the very next cycle will carry the fold-granular history specimen 1 lacked. A downstream plan reading a bare `RETIRE` would permanently close a class that the instrumentation already in flight makes measurable.
  ⚠️⚠️ **N = 0 does NOT imply RETIRE.** A class with no labelled positives is `NOT MEASURABLE` (Q2), and mapping "we could not measure it" onto "it does not occur" **is diag-336's exact defect committed a second time, one level up.**
  ⚠️ **A SHIP-warn disposition states its denominator IN THE DISPOSITION LINE** — `SHIP-warn (recall 4 of 4 recoverable, of 5 named)`. A build plan must not be able to read a strong-looking verdict without seeing how few instances stand behind it.
  ⚠️⚠️ **EACH DISPOSITION NAMES WHAT IT AUTHORIZES, because that is the only thing a downstream plan actually reads** (§2.2's diagnostic clause — a diagnostic is not pure-additive in effect). **SHIP-warn** authorizes a warn-first build plan for that class and nothing else. **REDESIGN** authorizes a matcher rewrite, **not** a shipped check. **HOLD** and **RETIRE-PENDING-INSTRUMENTATION** authorize **no build work at all** — they route to bellows FORWARD row 49, the fold-granular history that would make a real measurement possible. ⚠️⚠️ **Row 49 is a candidate with no plan behind it, so "routes to FORWARD 49" is not yet a destination.** If any class lands there, **the findings name the concrete successor — an instrumentation plan for fold-granular draft history — as the owed artifact**, and say so in the findings' own closing. **An inconclusive diagnostic that routes nowhere is read as a dead end, and the shop rebuilds the guess instead.** ⚠️ **An inconclusive result is an acceptable outcome of this diagnostic and is NOT licence to build on judgement.** Two diagnostics concluding "the record cannot answer this" is a finding about the record, and the shop's next move is then instrumentation, not a check.

---

## Method + boundaries

- **READ-ONLY over every repo except this plan's own deposits.** No edit to `plan_lint.py`, no test file, no corpus write, no doctrine. Needing any other write means the premise failed → HALT.
- ⚠️ **The deposit-under-`knowledge/` premise is VERIFIED, not assumed** (§2.7 subtractive-trim: verify the subsumption against live data). Checked 2026-08-10: `plan_lint.py` treats `knowledge` only as a path-root token for project-root resolution and collects no `.py` under it; no test collects from `knowledge/`. **Depositing `.py` evidence therefore cannot be picked up as code.** 336's choice to keep the matchers outside every repo was tidiness, not a guard — the §2.6 inverse question (has a sibling already deleted this machinery, and why) is answered.
- ⚠️⚠️ **THE MATCHERS ARE DEPOSITED THIS TIME — a deliberate departure from 336's C1.** 336 kept them in a `mktemp -d` outside every repo and they survived only by luck; they were found still present in `/var/folders/...` and copied to session scratch before reaping. **A measurement whose instrument is destroyed cannot be re-run, and that is why this diagnostic exists at all.** The matchers land under `knowledge/qa/evidence/`, **never** under `scripts/` or `tests/` — depositing evidence is not installing a check.
- **HALT ROUTING — the inputs each step reads; if any is missing or unreadable, HALT the step that needs it and name it.** Step 1 reads this plan, `governance/knowledge/research/walk-register-group4-rescope-2026-08-10.md`, `governance/knowledge/research/draft-group4-rescope-2026-08-10-UNDEPOSITED.md`, `bellows/knowledge/research/lint-class-census-findings-2026-08-10.md` (including its addendum), and the preserved matcher sources. Step 2 reads Step 1's deposits and `/Users/marklehn/Developer/GitHub/RULE_20_SELF_CHECK_BLOCK.md`. **Re-derive this list from the steps as written before running.**
- ⚠️ **THE MATCHER SOURCES: prefer the deposited copy, fall back to the findings.** `m`, `q` and `r` are reproducible verbatim from findings §(i). **`s` is NOT** — its ~70-element `ENUM_NOUNS` list lives only in `census-matchers.py`, **which is now committed at bellows `9b8c56b`, so C1 REQUIRES its presence and this fallback is not a routine branch.** ⚠️⚠️ *(Reconciled at walk 2, Vulnerabilities — a conflict the Destruction lens had just created: C1 was tightened to require the file, while this bullet still read as though its absence were an ordinary path. Both cannot be true.)* **The fallback applies only where C1 has already failed** — a damaged or restored tree: then **state that `s`'s matcher is unreproducible and report Q2 for `s` as unknown** rather than rebuilding a noun list that would not be the measured one.
- ⚠️ **Every git command that stages or commits carries `-C /Users/marklehn/Developer/GitHub/bellows`, and each step asserts `git -C /Users/marklehn/Developer/GitHub/bellows rev-parse --show-toplevel` equals that path immediately before its commit.** The shell's cwd resets between calls and the shop has landed three drafting commits in the wrong repository while every command printed success.
- ⚠️ **Reads against the governance root name their own `-C`** — the register and the draft live at the root while this plan's commits target bellows.
- ⚠️⚠️ **PIN — read the register from its COMMIT, not the working tree.** `git -C /Users/marklehn/Developer/GitHub show a7077ca:governance/knowledge/research/walk-register-group4-rescope-2026-08-10.md`. Every line number this plan cites is as of that blob. **A verdict gate puts arbitrary wall-clock between the two steps and the root repo is written continuously**, so a working-tree read would let the register shift underneath a labelled set that cites it by line. ⚠️⚠️ **`a7077ca` is an AUTHORING-TIME read, to be VERIFIED and not inherited.** Step 1 **re-derives** the register's last-touching commit (`git -C ... log -1 -- <the register path>`), records it, and **reports any difference from `a7077ca` as a finding** — the cited line numbers are then re-derived rather than trusted. Step 2 asserts that recorded pin unchanged. *(Re-verified at walk 2: still `a7077ca`; four root commits since have touched other files.)*
- ⚠️⚠️ **THE REGISTER IS A MARKDOWN TABLE, AND ITS CELL DELIMITER IS THE PIPE.** Findings live in table rows, so an offending line quoted inside a cell has had its own pipes escaped or dropped by the table format. **Extracting `text_or_reconstruction` from a cell without saying so can silently truncate the very construct being labelled** — and class `r` is defined by a pipe. **Any row sourced from a table cell is marked as such**, and a truncation that cannot be repaired is `RECOVERABLE-RECONSTRUCTED` at best, never `RECOVERABLE-VERBATIM`.
- **Negative results are not evidence on their own:** every absence claim pairs with a positive control, and every literal search uses `grep -F`.
- ⚠️ **No non-ASCII and none of the `q` character set (backtick, dollar sign, unescaped exclamation) inside any `-F` literal this plan mandates** — this diagnostic must not exhibit the classes it prices.
- ⚠️ **T-7 fires and that is why this is T1:** a build plan will act on these findings. Every finding states its own confidence and its covered population.

---

## Required deposit structure

`lint-class-recall-findings-2026-08-10.md` carries **one section per class**, each with:

**(i)** the matcher source used, and whether it came from the deposited copy or the findings · **(ii)** the labelled positives for that class, **each with its register line citation and its Q1 recoverability mark** · **(iii)** Q2 recall as a count over its denominator · **(iv)** Q3 recall for `m` and `q`, or an explicit "not redesigned" for `r` and `s` · **(v)** the Q4 disposition, **stating precision (from 336) and recall (from here) as a pair** · **(vi)** the case against that disposition.

**Plus one section the class sections cannot hold: `## Instances covered by no class`** — every register instance C.2b judged to be a real defect that none of the four classes describes, with its `instance_id` and why no class covers it. ⚠️⚠️ **C.2b mandates this outcome and the one-section-per-class structure has nowhere to put it**, so it would be dropped by the shape of the deliverable rather than by a decision. **It is also the most interesting possible result** — a defect the reader caught that the class set cannot see is an argument about the class set, which is the question behind the question.

⚠️ **The 336 findings and these must compose**, or the shop has two measurements of one class in different units.

---

## Conflict Ledger

Planner-run at each culmination. ⚠️ `plan_lint` check (p) reads only inside the `## Drafting Cycle` block, so this section is invisible to it (bellows FORWARD row 44).

- **C1 — nothing is INSTALLED, but the instrument IS preserved.** Check: `git -C /Users/marklehn/Developer/GitHub/bellows status --porcelain -- scripts/ tests/` is empty at every step boundary, AND **both** `matchers/census-matchers.py` (pre-seeded) and `matchers/redesigned-m-q.py` (written by Task D) exist under `knowledge/qa/evidence/lint-class-recall-2026-08-10/` at Step 1's end. ⚠️ **Both halves are required** — 336 satisfied the first and lost the instrument. ⚠️⚠️ *(second half re-specified at walk 2, Destruction: the preempt had committed the pre-seeded matchers, so a check reading "the matcher sources exist under `knowledge/qa/evidence/`" was **satisfied before the plan ran and could no longer fail.** A guard relaxed to vacuity by an external event is worse than no guard, because it still reads as one.)* *(opened at authoring)*
- **C2 — label BEFORE matching, and the ordering must be OBSERVABLE.** ⚠️⚠️ **Check: `labelled-positives.txt` is committed in its OWN commit, and the findings document is absent from that commit's tree.** *(opened at authoring; made observable at walk 1, lens 3)* The row first read "its commit precedes any recorded matcher output" — **but Step 1 is one step and would naturally make one commit, in which case the ordering leaves no trace and the guard certifies nothing it can see.** That is §2.7's observe-the-effect defect: a check that confirms the call exists rather than that it happened. **Two commits inside Step 1 are therefore mandatory, and the first one is the guard.** ⚠️ This is the same ordering guard 336's C.2 placed on its rubric, and it is worthless if it happens after: a set labelled while matcher fires are visible is labelled to fit them.
- **C3 — recall is a COUNT, never a rate.** Check: every Q2/Q3 figure appears either as `k of N recoverable, of T named` **or** as the literal `NOT MEASURABLE (N=0)`. A bare percentage over a single-digit denominator is a FAIL. *(opened at authoring; second form added at walk 1 ACID, joint-resolving a conflict with the zero-denominator fold — walk register.)*
- **C4 — precision is never restated, only cited.** Check: no number from 336 is recomputed here; each is quoted with its source. ⚠️ Re-deriving 336's figures would produce a second set that silently disagrees. *(opened at authoring)*
- **C5 — an unrecoverable instance is reported, not dropped.** Check: Q1's three marks partition the full register-named set; the count of each is stated. **An instance quietly excluded because no matcher could see it inverts the whole measurement.** *(opened at authoring)*
- **C6 — every mandate names its observer INLINE, and the observer is proven able to fail.** Check: every Step-1 mandate carries a parenthetical naming its QA item id; every such item tests **the effect, not the presence of an artifact**; and at least one item has been exercised by constructing the violation. ⚠️⚠️ **ESCALATED TO THE STRUCTURAL FORM at the confirming pass**, on this row's own trigger: the class fired three more times — no-normalization, C.2b's justification, and multi-class linking all had no observer — **for a total of seven, three of them under a ledger row written to prevent exactly this.** Naming the id inline is what makes an unpaired mandate visible when it is written rather than a walk later. *(opened walk 3; escalated at the confirming pass — bellows FORWARD 52, LESSONS 245.)*

---

## How to Run This Plan

**Bootstrap prompt:**
```
Read the diagnostic at knowledge/decisions/in-progress-diagnostic-<id>.md (the daemon renames the deposited placeholder on claim). Execute Step 1 ONLY. After completing Step 1, STOP and wait for my confirmation.
```

---

## STEP 1 — DEV (labelled set, then recall)

> **FIRST — post a short visible chat message (1-2 sentences) confirming you are starting this diagnostic.** Do NOT rename this file.
>
> ⚠️⚠️ **EXECUTE STEP 1 ONLY, THEN STOP.** `pause_for_verdict: always` is a header contract the runtime does not police (bellows FORWARD row 46): plan 336's agent ran all three steps in one dispatch while the daemon recorded one, which destroyed QA independence and would have made a `continue` verdict overwrite committed evidence. **Committing Step 1 and continuing into Step 2 is a step-contract violation, not efficiency.**
>
> **Task A0 — branches, each with its condition stated.**
> **(1) NOT-INSTALLED guard:** `git -C /Users/marklehn/Developer/GitHub/bellows status --porcelain -- scripts/ tests/` must be empty (C1).
> **(1b) CLEANLINESS of this plan's own write paths:** `git -C /Users/marklehn/Developer/GitHub/bellows status --porcelain -- knowledge/qa/ knowledge/research/ knowledge/development/` must be empty.
> **(2) RE-ENTRY key:** `git -C /Users/marklehn/Developer/GitHub/bellows log --oneline -- knowledge/qa/evidence/lint-class-recall-2026-08-10/labelled-positives.txt` for a commit whose subject names the slug. ⚠️⚠️ **The probe names THIS PLAN'S OWN FIRST WRITE, not the evidence directory** — the directory is **pre-seeded** (see the PRE-SEEDED branch), so a directory-level probe would read a fresh run as a re-entry and license overwriting work that was never done.
> **THE FOUR BRANCHES, each with its condition, and the catch-all LAST.**
>
> - **FRESH** = (1) and (1b) empty AND (2) no such commit → proceed at Task B.
> - **RE-ENTRY-A** = (1) and (1b) empty AND (2) present AND **no findings document AND no matcher output** exists → **Task C is DONE; resume at Task D against the COMMITTED labels and do not re-label.** Re-labelling here would destroy the only artifact proving labels preceded matching.
> - **RE-ENTRY-B** = (1) and (1b) empty AND (2) present AND a findings document exists → a full re-run is permitted, but **the prior matcher output must be discarded before any re-labelling**, or C2's ordering is violated by a set labelled with the old fires in view.
> - **NONE-MATCH** = anything not matching the three above → **HALT quoting every measurement taken.**
> ⚠️⚠️ **(3) PRE-SEEDED — expected, not an anomaly.** `knowledge/qa/evidence/lint-class-recall-2026-08-10/matchers/` **already exists and is already committed** (bellows `9b8c56b`), deposited ahead of this plan on CEO direction because 336's instrument was about to be lost to temp-dir reaping. **Its presence satisfies Task B and is NOT a re-entry signal.** An A0 that treated it as one would read every fresh dispatch as a resumption.
>
> **Task B — VERIFY the PRE-SEEDED instrument, and copy only if absent.** Confirm `knowledge/qa/evidence/lint-class-recall-2026-08-10/matchers/census-matchers.py` is present and contains the class-`s` noun-list identifier, and **record which source supplied each matcher.** ⚠️⚠️ **This task checks the pre-seeded file ONLY — C1's full two-file condition is Task F's, at step end**, because `redesigned-m-q.py` does not exist until Task D. ⚠️ **Only if the pre-seeded file is absent or unreadable**, fall back in this order: (1) the `mktemp -d` path recorded in **336's step-2 dev log, Task S2-C** — read the path from there, do not guess it — (2) findings §(i), which reproduces `m`, `q`, `r` verbatim. **If `s`'s noun list is nowhere, say so and carry `s` as unreproducible into Q2** (see the Method bullet).
>
> **Task C — build the labelled positive set, and do it BEFORE running anything (C2).**
> **C.1 — Read the walk register in full.** Do not grep for the class names; **read it.** ⚠️ 336's own cycle recorded that a probe matching one representation of a rule missed another, and the register describes defects in prose that no fixed token spans.
> **C.2 — Enumerate every instance of the four classes it records.** Authoring-time read found instances at register lines **19, 22, 25, 87, 136, 270, 361 and 414** — ⚠️ **that list is a starting point from one reader, not a specification; find the ones it missed and report any it names in error.** ⚠️ **Line numbers are as of the register's pinned commit `a7077ca`** (see the Method pin); re-derive them if the pin has moved.
> ⚠️⚠️ **C.2b — JUSTIFY each instance's class assignment against the MATCHER's own definition, and "not an instance of any of the four" is a legitimate outcome that must be reported.** *(Observed by QA Item 10.)* The register describes defects in a reader's words; the classes are defined by regexes. **These are not the same vocabulary and the mapping is an assumption, not a given** — a section sign in a version pin is only a class-`m` instance if it sits inside a `-F` operand, which is precisely what `m`'s matcher was redesigned to test. **An instance the register calls a defect but no class covers is a finding about the CLASS SET, not a labelling error to resolve by force.**
> **C.3 — For each instance, answer Q1** — RECOVERABLE-VERBATIM, RECOVERABLE-RECONSTRUCTED, or UNRECOVERABLE — **naming where the text was found.** The candidate sources are the register's own quoted fragments, the post-fold `draft-group4-rescope-2026-08-10-UNDEPOSITED.md`, and the specimen record. ⚠️ **A reconstruction is marked as a reconstruction on its row**, always.
> **C.4 — Deposit the labelled set in its OWN COMMIT and STATE that no matcher has been run yet** (C2). *(Observed by QA Item 2.)* ⚠️⚠️ **This is the first of Step 1's two commits and it is the ordering guard itself — commit `labelled-positives.txt` alone, with no findings document in the tree, before running anything.** A single end-of-step commit would leave the label-before-match ordering unobservable, which is the guard failing silently rather than the guard working. **Do not proceed to Task D until this commit exists.**
>
> **Task D — Q2 and Q3: run the matchers against the labelled set.** As-written for all four; the operand-parsing redesigns for `m` and `q` only. ⚠️ **Write the redesigned matchers here and paste their source into the findings** — a recall figure without its matcher is unreproducible.
>
> ⚠️⚠️ **VALIDATE EACH REDESIGNED MATCHER ON A POSITIVE CONTROL BEFORE RUNNING IT ON THE LABELLED SET, and deposit the control with its output.** Construct one line that unambiguously contains the defect and one that unambiguously does not, and confirm the matcher separates them. ⚠️⚠️ **THE CONTROL MUST PASS BEFORE THE RECALL RUN, AND A FAILING CONTROL HALTS IT.** *(Observed by QA Item 8.)* Depositing a control that shows the matcher failing to separate satisfies a presence check and proves the opposite of what the control exists to prove — **report the failure and stop; do not run the labelled set through a matcher known to be broken and then publish its recall.** **The redesign is "parse the command to find the `-F` operand" — a real parser over shell quoting, and a naive one silently under-fires.** Without the control, **a low recall figure is indistinguishable between "the class does not occur" and "the parser is broken", and the whole diagnostic turns on telling those apart.** (§2.7: negative results are not evidence on their own.)
>
> ⚠️ **Run them ONLY against RECOVERABLE rows.** An UNRECOVERABLE instance has no text to match and scoring it as a miss would blame the matcher for the record's gap.
>
> ⚠️⚠️ **REPORT RECALL SPLIT BY RECOVERABILITY — verbatim rows and reconstructed rows counted separately, never pooled.** *(Observed by QA Item 8.)* A reconstructed line is text **a reader wrote from a description**, so a matcher firing on it measures the reconstructor's phrasing, not the matcher. **Pooled, that is indistinguishable from a real catch, and a build plan would read it as one.** ⚠️⚠️ **A SHIP-warn disposition requires AT LEAST ONE VERBATIM hit, and the verbatim count appears in the disposition line.** "May not rest on reconstructed rows alone" was the walk-2 wording and it sets no floor — **1 verbatim plus 3 reconstructed and 0 verbatim plus 4 reconstructed both satisfy it under one reading and neither under another.** A downstream build plan reads the disposition, not this clause; if the floor is not in the line, it is not in the decision.
>
> **Task E — Q4: revised dispositions,** each stating precision (cited from 336) and recall (measured here) as a pair, each with its case against. ⚠️ **`s` keeps 336's HOLD on 336's GROUND — that a regex cannot verify a count — and that ground is not re-argued here. But a mechanism 336 never considered is REPORTABLE, exactly as Q3 says.**
>
> **Task F — assert C1 in full before the second commit.** Both matcher files named in C1 are present, and `git -C /Users/marklehn/Developer/GitHub/bellows status --porcelain -- scripts/ tests/` is empty. *(Observed by QA Item 1.)*
>
> **LABEL FORMAT — one illustrative row, shape only. ⚠️ This is TASK C's output spec and it is printed here, three tasks later; read it before starting C.3.**
>
> ```
> instance_id	class	register_line	instance	recoverability	source	from_table_cell	reconstruction_basis	text_or_reconstruction
> i3	q	22	P7 literal carrying backticks through a blockquote and a shell	RECOVERABLE-VERBATIM	register quoted fragment	yes	-	<the line, tabs and newlines replaced with single spaces>
> ```
>
> ⚠️⚠️ **`instance_id` was MANDATED at walk 2 and was missing from the very format block that mandates it** until walk 3 — the drawn row is the specification, and a column named only in the prose beneath it does not exist. **Sketch one real block and confirm it holds everything the plan requires (§2.7)**; the sketch is what an agent copies.
>
> ⚠️⚠️ **ONE INSTANCE MAY CARRY MORE THAN ONE CLASS, and it gets ONE ROW PER CLASS sharing an `instance_id`.** *(Observed by QA Item 11.)* A single `-F` literal holding both a non-ASCII character and a backtick is an `m` instance **and** a `q` instance. **With one `class` column and no link, such an instance is either counted twice as two unrelated positives or silently dropped from one class's denominator** — and every recall figure in this diagnostic is a count over that denominator. Add `instance_id` as the first column.
>
> ⚠️ **`reconstruction_basis` is mandatory on every RECOVERABLE-RECONSTRUCTED row and is a dash elsewhere** — it names what the reconstruction was built from and what was inferred. **ACID durability-as-record, walk 1: without it a later author reads a reconstructed line as a quotation** and cannot tell which characters were measured and which were supplied by a reader. `from_table_cell` carries the Method's pipe-truncation hazard onto the row that suffers it.
>
> ⚠️ **`text_or_reconstruction` is copied out of another document and MUST have tabs and newlines replaced with single spaces before emitting** — a tab inside it splits one row into two columns, corrupting the TSV on exactly the rows that describe what matched.
>
> ⚠️⚠️ **NO OTHER NORMALIZATION. Preserve every byte, and state the file's encoding.** *(Observed by QA Item 9.)* Do not straighten quotes, do not convert an em-dash to a hyphen, do not strip a section sign. **Class `m` IS the non-ASCII character** — a reconstruction that tidies the text destroys the instance and then reports the matcher as having missed it. The tab-and-newline substitution above is the single permitted exception and it exists only because the format cannot carry them.
>
> **Deposits:**
> - `bellows/knowledge/qa/evidence/lint-class-recall-2026-08-10/labelled-positives.txt` — ⚠️⚠️ **COMMIT 1, ALONE. Task C.4's own commit, made before any matcher runs; nothing else may be in it (C2).** This bullet's ordering is the guard, not a note about it.
> - `bellows/knowledge/qa/evidence/lint-class-recall-2026-08-10/positive-controls.txt` — COMMIT 2. The constructed defect-present and defect-absent lines for each redesigned matcher, with the matcher's output on each.
> - `bellows/knowledge/qa/evidence/lint-class-recall-2026-08-10/matchers/redesigned-m-q.py` — COMMIT 2. The operand-parsing redesigns written in Task D. ⚠️ **The pre-seeded `census-matchers.py` is verified by Task B, NOT re-deposited** — an unchanged committed file can never appear in this step's changed-file set, so declaring it would be a deposit check that cannot fire.
> - `bellows/knowledge/research/lint-class-recall-findings-2026-08-10.md` — **structure mandated by the `## Required deposit structure` section; a findings document not in that shape is a FAIL**
> - `bellows/knowledge/development/lint-class-recall-dev-log-step-1-2026-08-10.md`

---

## STEP 2 — QA

> ⚠️⚠️ **PRECONDITION 1 — assert the register has not moved.** Re-derive the blob id Step 1 recorded for `governance/knowledge/research/walk-register-group4-rescope-2026-08-10.md` and confirm it is unchanged; **a commit-hash comparison is NOT sufficient**, because the root repo gains commits continuously and the question is whether this one file moved. **ACID isolation, walk 1: a verdict gate puts arbitrary wall-clock between the steps**, so QA's line-number spot-checks would otherwise read a different file than the one Step 1 labelled.
>
> ⚠️⚠️ **PRECONDITION 2 — assert Step 1 ran as its own dispatch.** `git -C /Users/marklehn/Developer/GitHub/bellows log --oneline -- knowledge/qa/evidence/lint-class-recall-2026-08-10/` shows a Step-1 commit made before this step began, and this step's context did not produce it. **If this step is running in the same context that produced Step 1, say so plainly in the QA report and mark the independence gap** rather than reporting a clean QA (FORWARD row 46; LESSONS 240-241).
>
> **(A) Rule 20 self-check block** — emit the canonical block from `/Users/marklehn/Developer/GitHub/RULE_20_SELF_CHECK_BLOCK.md` (absolute operand, read live, never recalled). The receipt carries the canonical header `Rule 20 — QA Self-Check Results` and, when every item passes, the canonical verdict line `PASSED — SELF-CHECK PASSED`. ⚠️ **This plan deposits real evidence files, so the FULL canonical block applies.** ⚠️⚠️ **`required_evidence_files` is NOT restated here — it is the evidence-directory subset of `## Scope`, read from there.** **`## Scope` is the authority for the write-set; each step's Deposits block carries only its own subset, derived from Scope (the gate requires literal paths there); all prose references Scope.** *(ACID w2; reasoning in the walk register.)*
>
> **(B) Deliverable verification (Rule 8 / Rule 17):**
> - **Item 1 — nothing installed, instrument preserved.** No change under `scripts/` or `tests/`, AND **C1's second half holds as C1 states it** — both named matcher files present. ⚠️ **Read C1, do not restate it.**
> - **Item 2 — labelling preceded matching, proven from git and not from narration.** `git -C /Users/marklehn/Developer/GitHub/bellows log --oneline -- knowledge/qa/evidence/lint-class-recall-2026-08-10/labelled-positives.txt` names a commit, and `git show --stat` on it shows the labelled set **alone** with no findings document (**C2**).
> - **Item 3 — recall is a count.** Every Q2/Q3 figure reads **either** `k of N recoverable, of T named` **or** `NOT MEASURABLE (N=0)` (**C3**).
> - **Item 4 — precision is cited, not recomputed.** Every 336 number carries its source (**C4**).
> - **Item 5 — the unrecoverable set is named.** Q1's three marks partition the full register-named set and each count is stated (**C5**).
> - **Item 6 — spot-check three labelled positives** by reading the register **at the pinned blob Precondition 1 asserted**, not the working tree, at the named line, and confirming the instance and its recoverability mark. ⚠️ **The source was unstated until walk 3 — and Precondition 1 exists precisely because the two can differ**, so a check that silently reads the working copy defeats the pin it sits beneath. A mark that does not survive the reader is a FAIL.
> - **Item 7 — raw output.** Every count in the receipt is the command's own stdout, pasted.
> - **Item 9 — labelled text was NOT normalized.** The deposit states its encoding, and **three rows carrying non-ASCII are byte-compared against the register blob** — any straightened quote, hyphenated em-dash or stripped section sign is a FAIL. *(Observes Task C's no-normalization mandate. Constructed violation: tidy one em-dash and confirm this item reports it.)*
> - **Item 10 — class assignments are justified, and the no-class section exists or is explicitly empty.** Every labelled row carries C.2b's justification against the matcher's own definition, and `## Instances covered by no class` is present with its rows or a stated zero. *(Observes C.2b.)*
> - **Item 11 — multi-class instances are LINKED, not duplicated or dropped.** Any `instance_id` appearing on more than one row is the same instance under different classes, and each class's denominator counts it once. *(Observes the instance_id mandate.)*
> - **Item 8 — the recall split is present, and the control's HALT was honoured.** Each class's recall is reported **separately for verbatim and reconstructed rows**; the deposited control output shows **separation**; and ⚠️ **where a control did NOT separate, confirm NO recall figure was published for that matcher** — that is this item's reachable failure, since a non-separating control otherwise halts Step 1 before QA runs.
>
> **Deposits:**
> - `bellows/knowledge/qa/lint-class-recall-qa-2026-08-10.md`
> - `bellows/knowledge/development/lint-class-recall-dev-log-step-2-2026-08-10.md`

---

## Scope

```
bellows/knowledge/qa/evidence/lint-class-recall-2026-08-10/matchers/redesigned-m-q.py
bellows/knowledge/qa/evidence/lint-class-recall-2026-08-10/positive-controls.txt
bellows/knowledge/qa/evidence/lint-class-recall-2026-08-10/labelled-positives.txt
bellows/knowledge/research/lint-class-recall-findings-2026-08-10.md
bellows/knowledge/qa/lint-class-recall-qa-2026-08-10.md
bellows/knowledge/development/lint-class-recall-dev-log-step-1-2026-08-10.md
bellows/knowledge/development/lint-class-recall-dev-log-step-2-2026-08-10.md
```

---

## Drafting Cycle

**Tier:** T1 — **T-7 fires** (a build plan will act on these findings without re-deriving them). T-6 does NOT fire: nothing installs into a gate. T-2/T-5 do not fire — read-only outside this plan's own deposits. **Not self-escalated:** the artifact is a measurement and its blast radius is a document.

**Walks:** 4. ⚠️ **Every "walk register" pointer in this plan resolves to `governance/knowledge/research/walk-register-lint-class-recall-2026-08-10.md`, committed from walk 3** — this plan deposits into bellows, so an unqualified pointer would dangle across repositories. Committing it matches shop practice (specimen 1's register is committed at `a7077ca`); the divergence from §3's ephemeral-scratchpad wording is **bellows FORWARD row 51**, not resolved here.

- Weak spots:          w1 5 — 5 pre / 0 fold; w2 5 — 0/5; w3 5 — 1/4; w4 2 — 1/1.
- Destruction:         w1 2 — 1 pre / 1 fold; w2 4 — 2/2; w3 3 — 2/1; w4 1 — 0/1.
- Vulnerabilities:     w1 3 — 3 pre / 0 fold; w2 4 — 2/2; w3 3 — 2/1; w4 1 — 0/1.
- Integration-record:  w1 4 — 3 pre / 1 fold, 2 record-decay; w2 3 — 2/1, 1 rd; w3 2 — 0/2, 1 rd; w4 1 — 0/1, 1 rd.
- ACID:                w1 4 — 1 pre / 3 fold; w2 3 — 0/3; w3 2 — 0/2; w4 2 folded — 0/2.

⚠️ **RETRACTION (§2.7).** The walk-4 ACID entry first recorded a no-findings result, written before the lens ran; struck rather than quietly corrected. The lens then ran and folded two. ⚠️ **The retraction's first wording silenced the §4 gate by reproducing the status token it was retracting** — caught by conformance, reworded to describe rather than reproduce. *(bellows FORWARD 50; LESSONS 244.)*
- Trim (w4 opener):    1 — the growth metric itself: measured in lines for three walks, blind to within-line prose.

**Conformance (§5):** run at walk 0 at shape-stability and re-run after the walk-1 folds. ⚠️⚠️ **The post-fold run exited 1 and caught a defect the walk introduced** — the vulnerabilities fold restructured a deposit list into commit-grouped sub-headings, which the extractor could not read, so the step declared deposits and yielded no paths. Repaired and re-run. **Last run: walk 1 post-fold-repair, exit code 0.** ⚠️ This is §5's own argument in evidence: five adversarial lenses read that restructure and none of them saw it, because RIGHT and ADMISSIBLE are disjoint classes and only one of them costs a command. ⚠️ **The exit code was written into this log as 0 BEFORE the run** and was wrong; corrected from the command's output rather than left standing. **Walk 2 post-fold: exit code 0**, two WARNs, both expected — the closing fold-as-last-event (earned: the bar is unmet) and one unresolved path that is a **location artifact**, since linting from the governance root resolves `project_root` to `governance` while the plan's paths resolve at its bellows deposit site. ⚠️ **Expected lint state is declared from the DEPOSIT resolution, not from where the draft currently sits.**

**Conflicts:** C1-C5 opened at authoring. **C3 vs the lens-1 zero-denominator form — joint-resolved in one move at ACID, w1** (the count-form check would have rejected the output the other fold requires). Recorded on C3.

**Closing:** ⚠️⚠️ **NOT REACHED — walk 4 misses §2's bar by ONE finding and the cycle is OPEN.** Totals: **w1 18 folded (5 fold-introduced) · w2 19 (13) · w3 15 (10) · w4 8 (6), plus 1 from the trim.**

- **Condition 2 — predominantly fold-introduced: MET.** 6 of 8, the third consecutive walk on the right side of the split.
- **Condition 1 — record-class only: FAILS BY ONE.** Seven of eight walk-4 findings change only what the record says; **one changes execution** (QA Item 8 had no reachable failing state, now folded).

⚠️⚠️ **CONFIRMING PASS: NOT DRY — 3 non-record-class, 2 record-class.** All three non-record-class findings were **the same class, and C6's own trigger fired**: `NO OTHER NORMALIZATION`, C.2b's justification, and multi-class `instance_id` linking each imposed a Step-1 mandate with **no QA item that could fail.** Instances five, six and seven — three of them under a ledger row written to prevent exactly this. **Resolved structurally rather than by a fourth patch:** QA Items 9/10/11 added, and **every Step-1 mandate now carries its observer's item id inline** (7 pairings), which is what makes an unpaired mandate visible when written. **C6 escalated to that form; bellows FORWARD 52's candidate is now demonstrated on a live artifact rather than proposed.** ⚠️ The pairing cost words and put the plan back over 336 (figures in the register, per this plan's own rule) — **but the growth is instruction, not commentary**, which is the distinction LESSONS 243 draws and the only kind worth paying for.

⚠️⚠️ **WALK 5 WAS NOT RUN. A HARVEST RAN INSTEAD — CEO decision, 2026-08-10, and the reasoning is recorded because it is a deviation from §2's re-open clause.** Findings were classified by the surface they touch: **walk 3 changed instructions in ~10 of 15; walk 4 in 2 of 8.** The instruction surface had converged while the commentary surface had not and structurally cannot, since every fold adds explanation the next walk can then review. **Five of this cycle's highest-value findings were about the DRAFTING CYCLE, not about this plan** — and the cycle has no channel for those, so they accumulated as fold commentary here, which is also why this artifact outgrew the one its own Why section cites as the cautionary case. **The growth problem and the findings-about-the-cycle problem were the same problem.** Harvested to **bellows FORWARD 50-53** and **LESSONS 243-245**, via §6's corpus path and Rule 42 — neither of which requires a drafting cycle. The corresponding commentary was then stripped from this plan.

⚠️ **What the deviation does NOT waive:** the outstanding non-record-class finding is folded, and **one confirming pass over the stripped artifact is still owed before deposit.**

⚠️ **Both §2.8 signals progressed:** the stale-consuming-site class did not recur at walk 4, and C6's fifth-instance trigger did not fire.

⚠️⚠️ **DEPOSITED BY CEO DECISION WITH §2's BAR UNMET — a DECLARED DEVIATION, not a judged stop.** A judged stop requires a last event that is a dry lens pass or a stop whose residue meets the bar; the last event here was a **fold**, and the confirming pass that produced it was not dry. **The deviation is recorded rather than dressed up**, following the 336 precedent (deposited at walk 7 on the same grounds).

**The reasoning:** four walks plus a confirming pass; the instruction surface converged at walk 4 and the confirming pass's three non-record-class findings were one class, resolved structurally rather than patched. **The genuine open question — whether the register preserves matchable text — is answerable only by running this, not by drafting it.**

⚠️ **Two record-class findings are carried into dispatch, not resolved:** the growth condition is stated two ways (one citing the retired line metric), and Q1 carries stacked walk-attribution notes the strip should have taken. Neither changes what an executing agent does.

⚠️⚠️ **Walk 1's sequential-fold compliance was PARTIAL, and the record says so rather than claiming the walk was clean.** Folds landed in lens order, but candidate findings for lenses 2-5 were generated from the pre-fold draft — the batched fork §2.7 forbids, in its analysis half. **Six findings (7, 11, 15, 16, 17, 19) could not have existed before the folds that produced them and are genuine sequential catches; the other thirteen were reachable from the walk-0 draft.** Walk 2 reads for lens N only after lens N-1's folds are in the file. (ACID sharing a turn with the other four is not itself the defect — the control is the fold order, not the turn boundary.)
