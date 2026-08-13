# Diagnostic: price four candidate lint classes — frequency, re-finding rate, FP surface, and whether a matcher fires on real pre-fold states

**Type:** Diagnostic
**Project:** bellows
**Depends on:** `funnel-mechanization-v0-2026-08-08.md` §4 (five stages, no skips — this is stages 2 and 3), `drafting-cycle-v2-specimen-1-2026-08-10.md` (where the four classes were recorded), diagnostic-322 (the prior census, which touches these classes only glancingly — measured)
**Created:** 2026-08-10
**Author:** Planner
**Slug:** `lint-class-census-2026-08-10` (authoring-time; stable across any crash-redo re-deposit)
**dispatch_mode:** bellows
**pause_for_verdict:** always
**Priority:** 5
**cycle_tier:** T1
**qa_steps:** 3

⚠️ **ID NOTE — the deposit filename is decided AT DEPOSIT.** `id_sequence` read at deposit, never at authoring.

---

## Why this exists

A build plan for four warn-first `plan_lint` checks was drafted and **withdrawn before deposit** — it skipped funnel stages 2 (census) and 3 (prototype against real pre-fold states). The funnel forbids exactly what that plan did: *"mechanizing from a single occurrence, from plausibility, or from convenience; and any check whose FP surface was never measured on the corpus."* **It was built from convenience** — the classes were fresh from a session that had just been bitten by them, and vividness is not pricing.

⚠️⚠️ **SCALE, re-measured by plan 335 after this diagnostic was drafted — and the authoring figure was wrong.** `Done/` holds **1694 `.md` files**, of which **61** carry a `## Drafting Cycle` block. The draft said 63, taken with a two-level glob that misses nested paths. **The matchers run over 1694 files, not 63** — a 60-match cap is a completely different instrument at that scale, and Task **C.3**'s cap must be decided against 1694. ⚠️ **Stratify every Q1/Q3 number by block-carrying vs not:** 1633 of the 1694 never went through a drafting cycle at all, so a match in one of those says nothing about the cycle's defect classes and must not be averaged in with one that does.

⚠️ **Pin the corpus.** Record each repo's `HEAD` and the file count at Step 1 and re-assert at Step 2 — the corpus grows continuously, and it is now growing with artifacts that discuss these four classes at length. A census run a week later measures a different population.

**Measured: the existing census does not cover them.** `diagnostic-322` mentions `grep -F`, non-ASCII and "tally" once each, with no per-class frequency, re-finding rate, or FP surface (control: `M3` present).

**The four candidate classes — FIXED AT AUTHORING, extended only explicitly** (diag-322's clause, adopted because it solved this exact problem there). ⚠️ **An agent that adds a fifth interesting class mid-run has measured something nobody asked for**, and its frequency is then incomparable with the four that were priced. A new candidate is recorded as a finding for a future census, never folded into this one's numbers. ⚠️ **One arrived during this cycle and the rule was honoured: a DASH-LEADING search pattern parses as an OPTION** (`grep -c -F "-C /path"` → ugrep read `-C` as the context flag, exit 2). It is a real class, adjacent to `q`, and it is **recorded here for a future census — NOT added to the four**, because the taxonomy is fixed at authoring and a fifth class priced mid-run is incomparable with the four that were.

⚠️⚠️ **CORRECTED at walk 2 by reading 322 rather than recalling it: there is no single `M` bucket.** The taxonomy is **M1–M8, R, J, O**, and the four map unevenly — `m` is nearest **M8** ("non-ASCII scan", though M8 is scoped to CEO-run scripts, not `-F` literals); `r` is adjacent to **M3** (which already flags non-`-F` greps) but not the same check; `q` and `s` fit no bucket and belong in **O** ("other-mechanizable — propose it precisely enough to implement"). **The findings must state the mapping per class**, and an uneven fit is itself a result: a class with no bucket may be genuinely new, or may be a symptom of one that exists.

⚠️⚠️ **THE ID `(m)` MAY NOT BE FREE, and the code is the wrong place to check.** 322's **R** bucket names `(m)` as one of the HELD rows-25/27/28 batch. **Verify against BOTH the source and the Forward Register before claiming any id** — an id absent from `plan_lint.py` can still be reserved by an unshipped design.

⭐ **The precedent that gives this census its teeth — bellows FORWARD row 25:** a section-4 check was **designed, MEASURED against the corpus, and CUT before shipping (plan 332, CEO decision) because 1379 of 1390 plans would have fired it.** **Cutting a check on its measured fire rate is a shipped shop decision, not a hypothetical** — which is precisely the outcome Q5 must be willing to reach.

| id | class |
|---|---|
| **m** | non-ASCII inside a `-F` literal |
| **q** | a shell metacharacter inside a `-F` literal — **the set is exactly** backtick, `$`, and unescaped `!`; fixed at authoring like the classes themselves |
| **r** | `grep -c` piped into another command, masking the exit code |
| **s** | a numeral asserting the size of an enumeration |

⚠️⚠️ **The load-bearing design point, and the reason this cannot be done by grepping `Done/` alone:** a plan in `Done/` is a **post-fix** artifact. Its defects were folded out; what remains is the *correction*, which usually quotes the defect. **So `Done/` is where the FALSE-positive surface lives, and it systematically UNDER-represents true positives** — most were folded out before the plan closed. ⚠️ **Not "none": a live defect that no lens noticed survives into `Done/` and is a TRUE match there** — which is exactly what Q3's TRUE verdict records, so an absolute claim here would contradict Q3. The population that shows a check catching things **as they were being made** is the **pre-fold states** the per-phase commits supply. That is why the funnel says "prototyped against real pre-fold states," and it is the whole content of Q4.

---

## Questions

Each is answerable from here, and **"unknown" is an acceptable answer that must be reported as such** rather than papered over.

- **Q1 — Frequency, reported as (matcher, frequency) PAIRS and STRATIFIED.** Per class, **reported separately for the block-carrying stratum and the rest**, the partition taken from plan 335's capture at its named commit (**61 / 1633 at `efae953`** — re-measure; the corpus grows and these two numbers will be stale): how many contain at least one match, and how many matches in total? Report the distribution as **matches-per-plan for every plan with at least one**, plus the count of plans with none — not a mean, which hides whether a class is one plan's habit or the corpus's. ⚠️ **A frequency without the matcher that produced it is void** — two reasonable matchers for `s` differ by an order of magnitude, so the matcher source is part of the answer, not context for it.
- **Q2 — Re-finding rate, and the answer is a LOWER BOUND.** Per class: within a single cycle, how often did the class recur *after* being folded once? ⚠️⚠️ **Per-phase commits are per WALK or per CULMINATION, not per FOLD** — one commit can hold five folds, so a class folded and re-introduced inside a single commit is **invisible to this measurement.** **Q2 systematically under-counts, and its figure must be reported as a lower bound, never a rate** — a build plan reading it as a rate would under-price the class it most needs to price. ⚠️ **Answerable only over the covered population (see Method's DEFINITION bullet)** — never from `Done/` alone. **Report the covered and uncovered sets explicitly; do not extrapolate.**
- **Q3 — False-positive surface.** Per class, over final `Done/` states — **stratified using plan 335's deposited capture (`corpus-run.txt`, read at a named commit) rather than a partition recomputed here**, and with fenced matches marked: classify **every** match as TRUE (a live defect), FALSE (prose describing, correcting, or specifying the defect), or **AMBIGUOUS** — **or, where a class exceeds the cap Step 1's Task **C.3/C.5** sets, a stride sample with its stride and remainder named.** ⚠️ **C5's first run caught this:** this question promised exhaustive classification while Task C permitted a capped sample — **the definition and the Task contradicted each other**, and a verdict judged against the question would have failed a Task-compliant run. ⚠️⚠️ **The third verdict is load-bearing and is the main guard on this whole diagnostic.** A forced binary biases toward TRUE — the classifier is the same person hoping the class ships, and every genuinely unclear match resolves in favour of the hypothesis. **AMBIGUOUS counts AGAINST shipping**, not toward it. ⚠️ **A rate is not the deliverable — the classified list is.** Expect `s` to carry the most FALSE. ⚠️⚠️ **The classifier wrote the matchers, and that is the largest bias in this design.** The same agent authors the regex and then judges whether its fires are true — there is no second reader inside a single step. **Mitigation, and it must happen in this order: write the TRUE/FALSE/AMBIGUOUS rubric BEFORE looking at any match, deposit it in the findings, and classify against it.** A rubric written after the matches are visible is a rationalisation of them.
- **Q4 — Does a matcher fire where the defect really was?** Over **the covered population (see Method's DEFINITION bullet)**, reconstruct pre-fold revisions and run each matcher against them. **A class with no VERIFIED true positive on a pre-fold state has not been shown to catch anything** — that is a hold, not a ship. ⚠️ "Measured" was the earlier word and it is too weak: a raw fire is a **candidate**, and only a diff-read confirms the disappearance was a fold of that defect. Q5's bar reads *verified*; this question now matches it.
- **Q5 — Disposition per class:** SHIP / HOLD / REDESIGN, each with the numbers behind it. ⚠️⚠️ **Q5's bar is evaluated on the BLOCK-CARRYING stratum only.** That is the population a shipped check would police; the 1633 non-cycle files are context. **A class that looks frequent because documents which never ran a cycle mention it would ship a gate that fires constantly on non-plan text** — frequency in the wrong stratum is not evidence for a check, it is evidence against one. ⚠️ **Four classes were proposed; four surviving is not the expected outcome and must not be the default one.** ⚠️ **A SHIP disposition does NOT carry an id assignment.** The letters `m`/`q`/`r`/`s` are this diagnostic's internal labels; **`(m)` is named in 322's R bucket as part of a held batch**, so id allocation is an open question for the build plan to settle against both the source and the Forward Register — never inherited from these labels.

---

## Method + boundaries

- **READ-ONLY. This diagnostic writes only its own findings.** No edit to `plan_lint.py`, no test file, no corpus write, no doctrine. The matchers are **prototypes in a `mktemp -d` directory outside every repo, named in the dev log** (per C1), never installed. ⚠️ "The diagnostic's own scratch space" was vague enough to permit a file inside `bellows/`, which C1's own `status --porcelain` check would then flag. Needing any repo write outside the declared deposits means the premise failed → HALT.
- **HALT ROUTING — the inputs each step reads.** Step 1 reads this plan and every `*.md` under any `knowledge/decisions/Done/`. Step 2 reads Step 1's findings, **the commit history of the covered population (see the DEFINITION bullet below)**, and `/Users/marklehn/Developer/GitHub/RULE_20_SELF_CHECK_BLOCK.md`. **Re-derive this list from the steps as written before running.**
- ⚠️⚠️ **DEFINITION — THE COVERED POPULATION. Stated once here; every other site REFERENCES this bullet and restates nothing.**
  **Pre-fold states come from DRAFTS, not deposited plans.** A deposited plan carries 0-1 commits (**measured 2026-08-10**: 332: 0, 330: 0, 324: 0, 329: 1). Per-phase drafting commits touch `draft-<slug>-<date>.md` at the **governance root**, are deleted at close, and numbered **159 in the root repo when measured 2026-08-10 — re-measure; this grows with every cycle.** Find them with `git log --all -F --grep="draft("` plus `--name-only`, grouped by draft filename. **The join key to a deposited plan is the SLUG** — never the date or title. Drafts written into untracked `scratchpad/` produce **no** per-phase commits, and this session's own cycles are in that category. Worked example: `cc65f2e` / `draft-lint-s4-hardening-2026-08-09.md`.
  ⚠️ **VERIFY THIS COLLAPSE BY READING, NOT BY GREPPING A FILENAME.** The collapse was first checked by counting `draft-<slug>-<date>.md` occurrences, which fell to 1 while a bare *"covered plan"* survived in Task C — **a probe that matched one representation of the rule and missed another.** The check is: read every site that names the population and confirm it says **draft** or references this bullet. ⚠️ **This rule drifted across four walks at these sites: Q2, Q4, Task B, the HALT ROUTING, and Task C's bare "covered plan".** ⚠️ **The sentence that stood here said FIVE and then listed FOUR** — a numeral contradicting its own enumeration, **which is exactly the `s` class this census exists to price**, occurring in the clause that documents collapsing a different class. Enumerate; never tally. **Collapsed to one statement at walk 4 rather than patched again** (§2.8): a rule with N copies has N chances to be wrong and no mechanism keeping them equal.
- ⚠️ **Bound the traversal: skip any path component beginning with `.`** — the root carries a `.git-DAMAGED` tree and live `.git` dirs.
- ⚠️ **Every git command that stages or commits carries `-C /Users/marklehn/Developer/GitHub/bellows`, and each step asserts `git -C /Users/marklehn/Developer/GitHub/bellows rev-parse --show-toplevel` equals that path immediately before its commit.**
- **Negative results are not evidence on their own** (§2.7's (D) clause): every absence claim pairs with a positive control, and every literal search uses `grep -F`.
- ⚠️ **No non-ASCII, and none of the `q` character set (backtick, `$`, unescaped `!`), inside any `-F` literal this plan mandates** — this diagnostic must not exhibit the classes it prices. ⚠️ **The rule read "no shell metacharacter", which is BROADER than the `q` class it enforces** — and under that broad reading this plan violated itself at `git log --all -F --grep="draft("`. A parenthesis is inert under fixed-strings; the rule now names the same set `q` does, so the plan's self-application and its own class definition agree.
- ⚠️ **T-7 fires and that is why this is T1:** a later build plan will act on these findings. **Every finding therefore states its own confidence and its covered population**, so the build plan inherits a measurement rather than an impression.

---

## Required deposit structure — the answers are not the deliverable, the CONTRACT is

⚠️ **Promoted to a top-level section at walk 7, matching diag-322**, whose clauses this diagnostic adopts. It had lived as a parenthetical on a deposit line, where **an agent scanning section headings never sees it** — and it is one of the two contracts a verdict is judged against.

`lint-class-census-findings-2026-08-10.md` carries **one section per class**, each with:

**(i)** the matcher source verbatim · **(ii)** Q1 as (matcher, frequency), stratified, with the distribution · **(iii)** Q3's TRUE / FALSE / AMBIGUOUS **totals**, a pointer to `final-state-matches.txt` for the row-level data, and **every AMBIGUOUS row in full with its `rubric_ref`** — ⚠️ **not every row**: reproducing a 200 KB evidence file inside the findings duplicates raw data the deposit already holds, and the AMBIGUOUS rows are the ones that decide the disposition · **(iv)** Q2's re-find count, **stated as a lower bound**, with covered and uncovered sets named · **(v)** Q4's candidate and **verified** true positives · **(vi)** the Q5 disposition with the case against it · **(vii)** the class's mapping to diag-322's taxonomy bucket (M1–M8 / R / J / O).

⚠️ **Structural comparability is the point:** 322's findings and these must compose, or the shop has two censuses in different units and no way to read them together.

---

## Conflict Ledger

Planner-run at each culmination. ⚠️ `plan_lint` check (p) reads only inside the `## Drafting Cycle` block, so this section is invisible to it (bellows FORWARD row 44).

- **C1 — nothing is installed.** Check: `git -C /Users/marklehn/Developer/GitHub/bellows status --porcelain -- scripts/ tests/` is empty at every step boundary. ⚠️ **The prototype matchers live OUTSIDE every repo — in a `mktemp -d` directory named in the dev log — and are pasted into the findings, never into `plan_lint.py`.** The constraint said only "in scratch", which is unsatisfiable as a check: a scratch file inside `bellows/` would show in the very `status` this row asserts is empty. *(opened at authoring; location named at destruction, walk 1)*
- **C2 — `Done/` measures FP, pre-fold states measure TP, and the two are never merged.** Check: every reported number names which population it came from. A single blended "accuracy" figure is the defect. *(opened at authoring)*
- **C3 — a classification is a list, never a rate.** Check: Q3's deliverable enumerates **every classified match** by plan and mark — **the full set where uncapped, the stride sample plus its named remainder where capped**; a bare percentage is a FAIL. ⚠️ This row demanded *every* match one lens after Q3 and Task C were reconciled to permit a stride sample — **the SAME rule, drifting in its THIRD copy.** *(opened at authoring; aligned at ACID, walk 2)*
- **C4 — an unanswerable question is answered "unknown" with its reason.** Check: Q2's covered population is named, and any plan outside it is listed as uncovered rather than assumed clean. *(opened at authoring)*
- **C5 — state a rule ONCE and reference it.** Where a rule genuinely must appear in two places, **the executing Task is normative** and the definition section is the contract a verdict is judged against.
  **Check — a READ, not a grep:** at each culmination, list every rule folded this pass and open every site that could state it, confirming exactly one states it and the rest reference that one.
  ⚠️⚠️ **This row was rewritten clean at walk 5 after three walks of amendments left it self-contradictory:** its title said *state a rule once* while its check still demanded the phrase appear in **BOTH** the definition and the Task — **an agent following the check would have re-introduced the duplication the walk-4 collapse removed.** It also prescribed `grep -F` as the instrument, the exact probe that missed a bare "covered plan" while the filename pattern read clean.
  ⚠️ **History, kept because the class is the census's own subject:** the classification rule drifted across Q3, Task C and C3; the population rule across Q2, Q4, Task B, the HALT ROUTING and Task C. Every one landed in the definition and not the Task, or the reverse. **Chasing copies does not scale; removing them does.** *(opened walk 2; amended walk 4; rewritten walk 5)*
- **C6 — every identifier in this plan is unambiguous.** Ledger rows are `C1`-`C6`; Task C's sub-steps are `C.1`-`C.6` **and are always written with the dot**; Step 1's tasks are `A0/B/C`, Step 2's are `S2-A0`...`S2-E`. ⚠️ **Ledger `C3` and sub-step `C.3` are distinct strings a grep separates, but a human reading "C3" in a dev log cannot** — the same ambiguity this row was opened for, recurring between the ledger and a task rather than between two steps. **Record-class, not behaviour-changing** — an agent following the plan text is unaffected; a reader of the record is. *(ACID, walk 4; extended ACID, walk 6)* Task letters are unique ACROSS steps. Step 1 uses `A0/B/C`; Step 2 uses `S2-A0/S2-B/S2-C/S2-D/S2-E`. ⚠️ Both steps previously had a "Task B" and a "Task C" — **a dev log, verdict or QA item citing "Task C" named two different things**, and this plan's own Q3 referenced "the cap Task C sets" without saying which. *(ACID, walk 4)*

---

## How to Run This Plan

**Bootstrap prompt:**
```
Read the diagnostic at knowledge/decisions/in-progress-diagnostic-<id>.md (the daemon renames the deposited placeholder on claim). Execute Step 1 ONLY. After completing Step 1, STOP and wait for my confirmation.
```

---

## STEP 1 — DEV (census over final states: Q1 and Q3)

> **FIRST — post a short visible chat message (1–2 sentences) confirming you are starting this diagnostic.** Do NOT rename this file.
>
> **Task A0 — branches, each with its condition stated.**
> **(1) NOT-INSTALLED guard:** `git -C /Users/marklehn/Developer/GitHub/bellows status --porcelain -- scripts/ tests/` must be empty — this proves nothing was installed (C1).
> **(1b) CLEANLINESS of the paths this diagnostic actually WRITES:** `git -C /Users/marklehn/Developer/GitHub/bellows status --porcelain -- knowledge/qa/ knowledge/research/ knowledge/development/` must be empty. ⚠️ **(1) alone guarded a surface this diagnostic never touches and left its own deposit paths unguarded** — C1 forbids writing to `scripts/`/`tests/` at all, so a dirty `knowledge/research/` from a crashed prior run would have passed A0 unnoticed.
> **(2) RE-ENTRY key:** `git -C /Users/marklehn/Developer/GitHub/bellows log --oneline -- knowledge/qa/evidence/lint-class-census-2026-08-10/` for a commit whose subject names the slug.
> **FRESH** = (1) and (1b) empty AND (2) no such commit. **RE-ENTRY** = (1) and (1b) empty AND (2) present — re-run and overwrite, noting the re-entry. **NONE-MATCH** = anything else → **HALT quoting every measurement taken.** ⚠️ The branches were once named without their conditions, which made the catch-all unevaluable — a branch table nobody can apply.
>
> **Task B — write the four prototype matchers** in a `mktemp -d` directory outside every repo, named in the dev log (C1), as a single throwaway script. Paste each matcher's source verbatim into the findings — **the matcher IS part of the measurement; a number without the matcher that produced it is unreproducible.**
>
> **Task PIN — take the corpus pins BEFORE anything else.** Record in the dev log: the `Done/` `*.md` file count, and `git rev-parse HEAD` for **each** repo under the shop root. ⚠️ **Step 2's precondition asserts against these pins and no Step-1 task took them** — a guard measured against a value that was never captured, the same defect folded in plan 335's cycle.
>
> **Task C — Q1 and Q3. Six ordered sub-steps; do them in this order.**
>
> **C.1 — Take the stratum from plan 335, do not recompute it.** `git -C /Users/marklehn/Developer/GitHub/bellows show efae953:knowledge/qa/evidence/cycle-yields-collector-2026-08-10/corpus-run.txt` — ⚠️ **the path after the colon is relative to the BELLOWS repo, not the shop root**; writing it as `bellows/knowledge/...` fails, the same path-form mismatch that broke a union comparison in plan 335. ⚠️ **Severity, measured rather than inherited: the wrong form fails LOUDLY** — `fatal: path ... does not exist in 'efae953'`, non-zero exit — so an agent would HALT, not proceed on bad data. 335's version failed silently by never matching. **Same class, different severity; do not carry 335's urgency across.** (335 closed 2026-08-10; the working tree is not a citation). Its `status` column partitions every `Done/` file: `OK` or `UNPARSEABLE` = **BLOCK-CARRYING**, `NO_BLOCK` = not. If it cannot be read, recompute and **state the partition is this diagnostic's own, not 335's**.
>
> **C.2 — Write the rubric BEFORE seeing any match, and deposit it.** The TRUE / FALSE / AMBIGUOUS criteria (Q3). ⚠️ **This ordering is the only guard against the classifier having written the matchers, and it is worthless if it happens after.**
>
> **C.3 — Decide the cap POLICY (no numbers yet).** Read `bellows/knowledge/research/lens-mechanization-census-2026-08-08.md` and record how many findings diag-322 classified by hand. **If its population turns out comparable to this one's, the shop's precedent is exhaustive classification and the cap should be dropped.** Do not inherit 60 from this plan's prose. Record the decision — cap or no cap — and its justification, **before any match is counted.**
>
> **C.4 — Run the matchers over every `Done/` file and record each match** with **every field the CAPTURE FORMAT names except `verdict` and `rubric_ref`**, which C.6 fills: class, file name, line number, stratum, fenced-or-not, matched text. **Now the totals exist**, per class and per stratum.
>
> **C.5 — If C.3 chose to cap, apply it now:** stride **N = ceil(total / 60) within each stratum** so the smaller one is never drowned; state total, N and remainder. ⚠️ A prefix sample biases by repository — directory-walk order clusters one project's plans together.
>
> **C.6 — Classify each selected match against the C.2 rubric** as TRUE, FALSE or AMBIGUOUS. **AMBIGUOUS counts against shipping.**
>
> ⚠️⚠️ **C.3 previously computed the stride from `total`, which C.4 had not yet produced — an ordering the collapse made visible and the prose had hidden.** Policy is decidable up front; the stride is not. Splitting them is what makes the sequence executable.
>
> ⚠️ **Task C was one ~900-word paragraph carrying eight instructions, after five folds across five walks — collapsed at walk 6** (§2.8). An agent reads a wall like that and acts on a subset; the ordering of C.2 before C.4 is load-bearing and was invisible inside the prose.
> ⚠️ **`UNPARSEABLE` means DIALECTAL, not junk** — 194 of 536 block-derived rows (36%). 335 established three Cycle Log forms: canonical (`w1 2 folded`), arrow (`w1 → v1: 4 folded`), bare status (`Destruction: pending.`). **A file whose log cannot be parsed still WENT THROUGH a cycle** and belongs in the block-carrying stratum — the partition is about having a cycle, not parse success. Parser widening is a Forward Register item.
>
> **CAPTURE FORMAT — one real row, drawn:**
>
> ```
> class	plan_file	line	stratum	fenced	verdict	rubric_ref	matched_text
> s	executable-330.md	142	BLOCK	no	FALSE	R2	three enumerations, corrected in the same clause
> m	executable-329.md	71	BLOCK	no	TRUE	R1	-F "## Group 4 - DRAFTING_CYCLE surgical batch"
> s	executable-311.md	88	BLOCK	yes	AMBIGUOUS	R4	four steps, each with its own gate
> r	action-queue-auto-resolution-2026-03-18.md	44	NO_BLOCK	no	FALSE	R3	prose about a piped count, in a doc that never ran a cycle
> ```
>
> ⚠️⚠️ **Every verdict names the rubric criterion it rests on — column `rubric_ref`.** The rubric-before-matches ordering (C.2) is this diagnostic's main guard, and **without a per-row criterion nobody can check the rubric was applied at all** — the verdict becomes unfalsifiable row by row, the same defect plan 335's cycle folded twice. **This also forces the rubric to be CRITERION-SHAPED (`R1`, `R2`, …) rather than a paragraph**, which is what makes it citable. A verdict with no `rubric_ref` is a FAIL.
> ⚠️⚠️ **Record whether each match is INSIDE A FENCED BLOCK — column `fenced`.** 335's tool learned to strip fences before counting, because plans quote doctrine and quote each other constantly; a `-F` literal inside a ``` example is not a literal the plan mandates. **A census that counts fenced examples measures how often plans DISCUSS a class, not how often they COMMIT it** — and that distinction is the whole difference between a check worth shipping and one that fires on documentation. ⚠️ **`stratum` was mandated one lens before this format carried a column for it** — the third artifact this session to require a field its own output shape could not express. ⚠️ **`matched_text` is copied verbatim out of a plan and MUST have tabs and newlines replaced with single spaces before emitting.** A tab inside it splits one row into two columns — TSV corrupted by its own payload, on exactly the rows describing what matched.
>
> **Deposits:**
> - `bellows/knowledge/qa/evidence/lint-class-census-2026-08-10/classification-rubric.md` — ⚠️ **the C.2 rubric, deposited BEFORE any match is seen.** It was mandated from walk 2 and had **no declared deposit path until walk 7** — a required artifact with no home, which `scope_check` would have flagged at the gate.
> - `bellows/knowledge/qa/evidence/lint-class-census-2026-08-10/final-state-matches.txt`
> - `bellows/knowledge/development/lint-class-census-dev-log-step-1-2026-08-10.md`

---

## STEP 2 — DEV (pre-fold states and re-finding: Q2, Q4, Q5)

> **Task S2-A0.** Step 1's deposits exist and its commit names the slug; otherwise HALT. ⚠️ **Read the rubric from `bellows/knowledge/qa/evidence/lint-class-census-2026-08-10/classification-rubric.md` — Step 1's deposited rubric file — and state that it is unchanged.** ⚠️ This said "Step 1's findings", which **does not exist at this point**: the findings document is a STEP 2 deposit, and the rubric became its own file one lens ago — Q5's disposition applies the same standard Step 1 classified under, and a rubric re-derived here would judge Step 1's marks by a bar they were never measured against. ⚠️⚠️ **Assert the corpus has not moved:** Step 1's Task PIN records the `Done/` file count and each repo's `HEAD`; Step 2 re-measures both and **reports any delta as corpus movement rather than absorbing it silently.** A verdict gate puts arbitrary wall-clock between these steps and plans close into `Done/` continuously — one may well close during this diagnostic's own run — so Step 2's population is not Step 1's unless checked.
>
> **Task S2-B — enumerate the covered population** exactly as the Method's DEFINITION bullet specifies, and **name the covered set and the uncovered set explicitly.** ⚠️ **If the covered set is fewer than three drafts, that is the finding**: report stage 3 as unsatisfiable from the current corpus rather than computing a rate over two drafts.
>
> **Task S2-C — Q4: run each matcher against pre-fold revisions.** For each covered **DRAFT** (see the DEFINITION bullet), `git -C /Users/marklehn/Developer/GitHub show <commit>:<draft-filename>` for each drafting commit, run the four matchers, and record whether each fires. ⚠️ **`-C` names the ROOT repo, not bellows** — the drafting commits live at the governance root while this plan's staging and commits target bellows; a read against another repo must name its own path. ⚠️ **This task said "covered plan" one lens after the collapse declared the population is DRAFTS** — the fifth site, and it survived because the collapse was verified by grepping the filename pattern rather than the word. ⚠️ **A fire on a pre-fold state that disappears by the final state is a CANDIDATE true positive** — the defect plausibly existed and was folded out, and that is the signal `Done/` cannot show. ⚠️ **It is only a CANDIDATE because text disappears for reasons unrelated to the defect** — a section rewritten, a bullet deleted, a whole task restructured. **Spot-verify a sample by reading the diff** and confirm the disappearance corresponds to a fold of that defect; report the verified fraction, not the raw count.
>
> **Task S2-D — Q2: re-finding, with a mechanical definition.** A **re-find** is: a match present at revision N, **absent at N+1**, and **present again at N+2 or later, within one draft's history.** ⚠️ A fold event is not directly observable from commits, so this definition is the operational stand-in and must be stated in the findings as such. ⚠️⚠️ **THE DETECTION FLOOR, and it must be reported with the number: per-phase commits are per WALK or per CULMINATION, not per FOLD.** A single commit can contain five folds, so **a class folded and re-introduced inside one commit is invisible to this measurement.** **Q2 therefore systematically UNDER-counts re-finds**, and the figure is a lower bound — never a rate. A build plan reading it as a rate would under-price the class it most needs to price. Within each covered draft, count re-finds per class. Report per draft; **no cross-draft average unless the covered set exceeds five drafts**, and say so either way.
>
> **Task S2-E — Q5: disposition.** Per class, SHIP / HOLD / REDESIGN with the numbers. **A class may be recommended SHIP only if BOTH hold:** (a) **at least one VERIFIED candidate true positive on a pre-fold state** — a check that has never been shown to catch anything has not been shown to work; and (b) **the FALSE and AMBIGUOUS lists contain no pattern the matcher cannot distinguish** — if the false fires share a shape the regex cannot exclude, the class is REDESIGN, not SHIP. ⚠️ **No numeric threshold is set here deliberately** — a predicted cutoff written before the data is the shape of a Goodhart target. The bar above is structural, and **if the data cannot justify a bar at all, the answer is HOLD.** ⚠️ **State the case AGAINST each class you recommend shipping** — a census that recommends everything it was asked to price has measured nothing.
>
> ⚠️ **Write the findings document LAST, after both evidence files exist, and assert all three are present before committing.** A partially written findings doc committed alongside complete evidence reads as a complete answer.
>
> **Deposits:**
> - `bellows/knowledge/qa/evidence/lint-class-census-2026-08-10/pre-fold-matches.txt`
> - `bellows/knowledge/research/lint-class-census-findings-2026-08-10.md` — **structure mandated by the `## Required deposit structure` section; a findings document not in that shape is a FAIL.**
> - `bellows/knowledge/development/lint-class-census-dev-log-step-2-2026-08-10.md`

---

## STEP 3 — QA

> **(A) Rule 20 self-check block** — emit the canonical block from `/Users/marklehn/Developer/GitHub/RULE_20_SELF_CHECK_BLOCK.md` (absolute operand, read live, never recalled). The receipt carries the canonical header `Rule 20 — QA Self-Check Results` and, when every item passes, the canonical verdict line `PASSED — SELF-CHECK PASSED`.
>
> **(B) Deliverable verification (Rule 8 / Rule 17):**
> - **Item 1 — nothing was installed.** `git -C /Users/marklehn/Developer/GitHub/bellows status --porcelain` shows no change under `scripts/` or `tests/`, and `git diff` over this diagnostic's commits touches only the declared deposits (**C1**).
> - **Item 2 — populations are never blended.** Every number in the findings names the population it came from; no single figure spans final states and pre-fold states (**C2**).
> - **Item 3 — Q3 is a list.** Spot-check five classified matches by opening the named plan at the named line and confirming the verdict. A verdict that does not survive the reader is a FAIL.
> - **Item 4 — the uncovered set is named.** Q2 and Q4 list the plans they could not cover, not merely those they could (**C4**).
> - **Item 5 — the case against is present.** Every SHIP recommendation carries its counter-argument (Task S2-E).
> - **Item 6 — raw output.** Every count in the receipt is the command's own stdout, pasted.
>
> **Deposits:**
> - `bellows/knowledge/qa/lint-class-census-qa-2026-08-10.md`
> - `bellows/knowledge/development/lint-class-census-dev-log-step-3-2026-08-10.md`

---

## Scope

```
bellows/knowledge/qa/evidence/lint-class-census-2026-08-10/classification-rubric.md
bellows/knowledge/qa/evidence/lint-class-census-2026-08-10/final-state-matches.txt
bellows/knowledge/qa/evidence/lint-class-census-2026-08-10/pre-fold-matches.txt
bellows/knowledge/research/lint-class-census-findings-2026-08-10.md
bellows/knowledge/qa/lint-class-census-qa-2026-08-10.md
bellows/knowledge/development/lint-class-census-dev-log-step-1-2026-08-10.md
bellows/knowledge/development/lint-class-census-dev-log-step-2-2026-08-10.md
bellows/knowledge/development/lint-class-census-dev-log-step-3-2026-08-10.md
```

---

## Drafting Cycle

**Tier:** T1 — **T-7 fires** (a build plan will act on these findings without re-deriving them). T-6 does NOT fire: nothing installs into a gate, and the matchers are prototypes in scratch. T-2/T-5 do not fire — read-only throughout. **Not self-escalated:** the artifact is a measurement, its blast radius is a document, and a T2 panel on a read-only census would buy less than running the census.

**Walks:** 1 complete — read before each lens, folds applied between lenses, ACID last on the fully folded artifact. Detail in `scratchpad/walk-register-lint-class-census-2026-08-10.md` (session-local, created before walk 1). **w1: 19 (13/6) · w2: 18 (6/12) · w3: 17 (5/12) · w4: 8 (4/4) · w5: 8 (4/4) · w6: 7 (2/5) · w7: 8 (4/4).**
- Weak spots:          w1 6 (6/0); w2 6 (4/2); w3 4 (2/2); w4 3 (1/2); w5 3 (2/1); w6 2 (0/2); w7 3 (2/1) — **the C.2 rubric was mandated from walk 2 and had no declared deposit path until now**; and no verdict named the criterion it rested on, leaving every classification unfalsifiable row by row (`rubric_ref` added).
- Destruction:         w1 4 (3/1); w2 4 (1/3); w3 4 (0/4); w4 2 (0/2); w5 1 (0/1); w6 1 (0/1); w7 1 (0/1) — the rubric deposit added one lens earlier **was absent from the Scope block**, which `scope_check` would have failed at the gate: the fold landed in Deposits and not in Scope.
- Vulnerabilities:     w1 5 (3/2); w2 3 (0/3); w3 3 (1/2); w4 2 (2/0); w5 1 (1/0); w6 2 (1/1); w7 2 (1/1) — S2-A0 read the rubric from "Step 1's findings", **which does not exist at that point**; and it asserted corpus pins **no Step-1 task was ever told to take** (Task PIN added).
- Integration-record:  w1 2 (2/0); w2 2 (1/1); w3 2 (2/0); w4 not run; w5 2 (1/1); w6 1 (1/0); w7 1 (1/0) — **322 elevates the required deposit structure to a top-level section; this diagnostic had it as a parenthetical on a deposit line**, invisible to anyone scanning headings, despite explicitly adopting 322's clauses.
- ACID:                w1 4 (2/2); w2 3 (0/3); w3 4 (0/4); w4 1 (1/0); w5 1 (0/1); w6 1 (0/1); w7 1 (0/1) — the promoted section mandated reproducing **every** classified row inside the findings, duplicating a 200 KB evidence file the deposit already holds.
**Conformance (§5):** run after every fold at the deposit path resolution — **exit 0, zero WARNs**, last run. Caught the plan-133 trap (qa_steps 2 on a three-step plan) before any lens.
**Conflicts:** C1-C4 opened at authoring; C1's scratch location named at destruction. None in conflict.
**Closing:** ⚠️⚠️ **DEPOSITED AT WALK 7 ON CEO DECISION, WITH §2's BAR UNMET. This is a declared deviation, NOT a judged stop** — a judged stop requires findings that are record-class and predominantly fold-introduced, and **roughly six of walk 7's eight were neither**: two would have failed `scope_check` at the gate, two pointed at artifacts that do not exist when read, one left every classification unfalsifiable.

**Yield by walk: 19 · 18 · 17 · 8 · 8 · 7 · 8.** The count flattened at walk 4 and then stopped falling. **Walks 6 and 7 were restructuring passes — each bought correctness and opened fresh surface — and the walks were not draining it.** Seven walks on a T1 read-only census of four classes is past proportionate; the decision to stop is a cost judgement, not a claim the artifact is finished.

**RESIDUALS — named, because a deposit that hides them is worse than one that does not.**

1. **Unconverged.** No walk has returned record-class-only findings. **Assume defects of the same shape remain** — most likely: a guard asserting against a value no task captures, a mandated artifact missing from Scope, or a reference to something that does not exist at the point it is read. All three classes recurred at walk 7 after being folded in a sibling plan.
2. **The dash-leading-pattern class is REFUSED, not missing.** `grep -c -F "-C /path"` parses `-C` as an option (exit 2, empty stdout) — a real class, adjacent to `q`, encountered during this cycle. The taxonomy is **fixed at authoring**, so it is recorded for a future census and deliberately excluded from these four. Folding it in would make its frequency incomparable with the priced set.
3. **Arrow-dialect parser widening is a Forward Register item, not this diagnostic's business.** 335 measured 194 of 536 block-derived rows (36%) as dialectal. This census inherits 335's partition and treats `UNPARSEABLE` as block-carrying, which is correct — but any successor computing yields from Cycle Logs must handle the dialects or knowingly under-report by about a third.
4. **Ledger `C3` versus sub-step `C.3` remains ambiguous to a human reader** — accepted with reason at walk 6 ACID rather than triggering a rename cascade. A grep separates them; a dev log entry does not.
5. **Proportionality.** This artifact is 220+ lines to price four regexes. If the census's answer is "hold three of four", the drafting cost will have exceeded the finding's value — which is itself a datum for the funnel, and should be reported alongside the dispositions.

**What is sound:** the question set, the stratification, the rubric-before-matches ordering, the fixed taxonomy, the C.1–C.6 sequence, and the pins. The defects this cycle kept finding were in the *scaffolding* around those, never in the measurement design.
