# Diagnostic: census the predicted-number class and price the hash-pin verification check — the mechanization decision the tally is owed

**Type:** Diagnostic
**Project:** bellows
**Depends on:** `/Users/marklehn/.claude/projects/-Users-marklehn-Developer-GitHub/memory/plan-predicted-numbers-need-verify-clause.md` (the class codification, plans 203–207), `/Users/marklehn/Developer/GitHub/LESSONS.md` (the discipline entry + every tally-bearing entry — grep `-F "predicted"`, do not inherit line numbers), `/Users/marklehn/Developer/GitHub/shop_next_session.md` session-38 wrap blocks (the tally's growth track and the four 2026-08-12 instances), `bellows/knowledge/research/lint-class-census-findings-2026-08-10.md` + `lint-class-recall-findings-2026-08-10.md` (the 336/337 arc — **cited, never recomputed**; class s's HOLD is standing ground), `/Users/marklehn/Developer/GitHub/funnel-mechanization-v0-2026-08-08.md` §4 (a class ships warn-first with a measured FP rate), `/Users/marklehn/Developer/GitHub/governance/knowledge/research/` drafts + walk registers (the primary instance records)
**Created:** 2026-08-12
**Author:** Planner
**Slug:** `predicted-number-pin-census-2026-08-12` (authoring-time; stable across any crash-redo re-deposit)
**dispatch_mode:** bellows
**pause_for_verdict:** always
**Priority:** 5
**cycle_tier:** T1
**qa_steps:** 2

⚠️ **ID NOTE — the deposit filename is decided AT DEPOSIT.** `id_sequence` read at deposit, never at authoring.

---

## Why this exists

The predicted-number class — a Planner-authored number or token asserting a fact not yet measured — has recurred since its codification, and the shop's records tally its growth across session-38 wraps (authoring-time read: roughly seventeen; **re-count, do not inherit — the tally itself is a Planner-authored number and in scope for this census**). Four instances landed on 2026-08-12 alone, by the Planner's own hand, every one caught by a fresh measurement inside a walk — the catches are working; the *authoring* is not improving.

Two of the four are a subclass with a property the 336/337 lint classes never had: **fabricated hash-pin tails** — a full-length hex pin authored by extending a shortened display prefix with invented bytes (`draft-schema02-2026-08-12.md` Vulnerabilities w2; `draft-rule20-inject-2026-08-12.md` w2, which caught BOTH A1 pins). A hash pin has **objective, mechanically checkable ground truth**: a 40-hex git pin either resolves in the named repo or does not (`git cat-file -e`); a 64-hex `shasum -a 256` file pin either matches the named file at deposit time or does not. The 336/337 classes failed because a regex cannot verify *meaning*; a pin-verification check verifies *existence*, which a regex plus one command can do. That distinction is the reason this diagnostic exists — and it is a hypothesis to price, not a conclusion.

**This diagnostic measures and disposes; it builds nothing.** Its findings authorize (or refuse) a warn-first `plan_lint.py` check in a later build plan.

⚠️ **It is deliberately SMALL** (the 336 lesson: growth past the two steps is itself a finding to report, not absorb).

⚠️ **Reflexive constraint:** a plan about unverified numbers must not commit the defect. Every number this plan states is marked authoring-time with a re-count clause, or is measured by the step that uses it. Every hash this plan would pin, it derives at run time instead.

---

## Questions

**"Unknown" is an acceptable answer that must be reported as such.**

- **Q1 — THE CENSUS.** Enumerate every *recorded* instance of the class from the source families in **Depends on**. Per instance: source file + the recorded text, date, the subclass, what caught it, and a recoverability mark reusing 337's three — **RECOVERABLE-VERBATIM / RECOVERABLE-RECONSTRUCTED / UNRECOVERABLE** (cite the marks, do not redefine them). Subclass taxonomy, authoring-time hypothesis the census may refine: **(A)** fabricated hash-tail; **(B)** predicted count/split; **(C)** stale baseline; **(D)** arithmetic; **(E)** inherited label. ⚠️ Report the total against the wrap-tally track and treat any divergence as a finding about the tally, never a number to reconcile toward.
- **Q2 — PRECISION of the pin-verification matchers, against a corpus that can contain true positives and true negatives.** Two matchers, deposited as the instrument:
  - **Token rule for both matchers: a token is a MAXIMAL hex run** — a 64-hex run is one M2 token and never an M1 match inside it; a run of any other length ≥12 is counted and reported but matched by neither (the prefix population, context for the findings).
  - **M1 (git-object pins):** extract 40-hex tokens from plan text; attempt resolution (`git cat-file -e`) against the scanned plan's own **Project** repo (read from its header), the root repo, and the other corpus repo — **record WHICH repo resolved; a pin resolving only outside its stated repo is its own cell (CROSS-REPO), not TRUE.**
  - **M2 (sha256 file pins):** extract 64-hex tokens on the same line as — or the line immediately before or after — a `shasum`/`sha256` invocation naming a path; recompute against the named file.
  - **Corpus:** the `.md` files sitting DIRECTLY in `knowledge/decisions/` and `knowledge/decisions/Done/` of bellows and lessons-forge — no other subdirectory (`drafts/`, `archived-halted-plans/` are out; an unstated boundary makes the denominator unreproducible). The findings state the boundary and the resulting file count. ⚠️⚠️ **A fire on `Done/` is not a positive by itself — Done pins were true at THEIR deposit time.** Classify every non-resolving fire: **STALE** (the ever-true test passes — the object exists in history / some committed revision of the pinned file carries that sha256) vs **NEVER-TRUE-SURVIVING** (no surviving witness that the pin was ever true — ⚠️ **NOT proof of fabrication**: a gc can prune a once-real unreachable object, and the shop runs gc on bellows; the findings state this caveat wherever the label appears, and every such fire is cross-checked against the walk-record catches before any disposition cites it) vs **AMBIGUOUS** (the test cannot run — file gone, repo unclear). Report each cell as a count with its denominator, never a bare percentage.
- **Q3 — RECALL of M1/M2 against the labelled subclass-A instances.** Recover the fabricated pins' original bytes via `git -C /Users/marklehn/Developer/GitHub log -p` over the draft files (the root repo, where the governance drafts commit per phase; the pre-fold revisions should carry them — Task B's probe). Report **`k of N recoverable, of T named`**, or **`NOT MEASURABLE (N=0)`** — a measured zero and an unmeasurable zero are different inputs to Q5.
- **Q4 — the bare-number subclasses (B–E): does any mechanism escape 336's ground that a regex cannot verify a count?** Class s's HOLD stands and is not re-litigated. One candidate is priced: the **verify-clause-proximity heuristic** (flag a bare integer in a QA row that carries no verify/re-count/halt-on-mismatch clause in the same row) — **a QA row is a line inside a step the scanned plan's `qa_steps` header names, or whose `## STEP` heading contains `QA` (the same detection `plan_lint.py` uses)** — run it over the Q2 corpus's QA rows and report its fire count with denominator plus a hand-classified sample. A new mechanism is a finding to report either way; a disposition change for s is not on offer here.
- **Q5 — DISPOSITION per subclass, stating precision and recall AS A PAIR, each naming what it authorizes.** **SHIP-warn** authorizes a warn-first `plan_lint.py` check build plan for that matcher and nothing else, and states its denominators in the disposition line. **REDESIGN** authorizes a matcher rewrite, not a shipped check. **HOLD** and **RETIRE-PENDING-INSTRUMENTATION** authorize no build work and name the concrete successor artifact they route to — for this class the known candidates are the fold-granular draft-history instrumentation (bellows FORWARD row 49, the 336/337 dispositions' route) and a deposit-time pin-verification hook; name whichever the evidence supports, or state plainly that none exists so the findings' closing says where the class goes instead of dead-ending. ⚠️ **N=0 does not imply RETIRE** — that is 336's defect one level up. An inconclusive result is acceptable and is not licence to build on judgement.

---

## Method + boundaries

- **READ-ONLY over every repo except this plan's own deposits.** No edit to `scripts/`, `tests/`, doctrine, corpus, or any DB. Needing any other write means the premise failed → HALT.
- ⚠️⚠️ **THE WORKTREE RULE — every git command in this plan runs from the step's own cwd (the dispatched checkout), never `-C` into another checkout for a WRITE.** Bellows dispatches steps into a plan worktree; a write forced into the main tree escapes plan isolation. Assert the tree's shape ONCE at A0: `git rev-parse --show-toplevel` prints a path whose tree contains `knowledge/decisions` (the main tree and a plan worktree both qualify). READ-ONLY probes of **other repositories** (the root repo for the governance drafts, lessons-forge for its corpus, and M1's resolution targets) use explicit `git -C <repo>` and are sanctioned — the prohibition is any WRITE outside cwd and any use of a second bellows checkout.
- **The matchers are DEPOSITED** (337's precedent: a measurement whose instrument is destroyed cannot be re-run). They land under `knowledge/qa/evidence/`, never under `scripts/` or `tests/` — depositing evidence is not installing a check.
- **HALT ROUTING:** Step 1 reads this plan, the **Depends on** sources, and git history of the governance draft files; Step 2 reads Step 1's deposits and `/Users/marklehn/Developer/GitHub/RULE_20_SELF_CHECK_BLOCK.md`. If any input is missing or unreadable, HALT the step that needs it and name it. **Re-derive this list from the steps as written before running.**

---

## Ledger

Planner-run at each culmination.

- **C1 — nothing installed, instrument preserved.** `git status --porcelain -- scripts/ tests/` (from the step's cwd) empty at every step boundary, AND both matcher files exist under the evidence directory at Step 1's end. *(observer: QA Item 1)*
- **C2 — the census is labelled BEFORE the matchers run, and the ordering is OBSERVABLE.** `labelled-instances.md` is committed in its OWN commit, findings document absent from that commit's tree. A set labelled with matcher fires in view is labelled to fit them. *(observer: QA Item 2)*
- **C3 — every figure is a count with its denominator**, or the literal `NOT MEASURABLE (N=0)`. A bare percentage over a small denominator is a FAIL. *(observer: QA Item 3)*
- **C4 — 336/337 figures are cited, never recomputed.** *(observer: QA Item 4)*
- **C5 — an unrecoverable instance is reported, not dropped**; Q1's marks partition the full named set, each count stated. *(observer: QA Item 5)*
- **C6 — reflexive clean hands.** Every number and hash in the findings' own text is either a step-measured output quoted from raw evidence or carries an explicit authoring-time/re-count mark. *(observer: QA Item 6)*

---

## How to Run This Plan

**Bootstrap prompt:**
```
Read the diagnostic at knowledge/decisions/in-progress-diagnostic-<id>.md (the daemon renames the deposited placeholder on claim). Execute Step 1 ONLY. After completing Step 1, STOP and wait for my confirmation.
```

---

## Scope

**The authority for the write-set; each step's Deposits block carries only its own subset.**

- `bellows/knowledge/qa/evidence/predicted-number-pin-census-2026-08-12/labelled-instances.md`
- `bellows/knowledge/qa/evidence/predicted-number-pin-census-2026-08-12/matcher-m1-git-pins.py`
- `bellows/knowledge/qa/evidence/predicted-number-pin-census-2026-08-12/matcher-m2-file-pins.py`
- `bellows/knowledge/qa/evidence/predicted-number-pin-census-2026-08-12/precision-raw.txt`
- `bellows/knowledge/research/predicted-number-lint-findings-2026-08-12.md`
- `bellows/knowledge/qa/evidence/predicted-number-pin-census-2026-08-12/qa-receipt.md`

---

## STEP 1 — DEV (census, then matchers, then measurement)

> **FIRST — post a short visible chat message (1-2 sentences) confirming you are starting this diagnostic.** Do NOT rename this file.
>
> ⚠️⚠️ **EXECUTE STEP 1 ONLY, THEN STOP.** `pause_for_verdict: always` is a header contract the runtime does not police: running into Step 2 destroys QA independence and is a step-contract violation, not efficiency.
>
> **Task A0 — branches, each with its condition, catch-all LAST.**
> **(0) TREE SHAPE (the Worktree Rule's assert):** `git rev-parse --show-toplevel` from cwd prints a path whose tree contains `knowledge/decisions`. Not bellows-shaped → HALT.
> **(1) CLEANLINESS — scoped to THIS plan's write paths plus the install surface, so unrelated parallel-terminal dirt cannot false-HALT:** `git status --porcelain -- scripts/ tests/ knowledge/qa/evidence/predicted-number-pin-census-2026-08-12/ knowledge/research/predicted-number-lint-findings-2026-08-12.md` must be empty.
> **(2) RE-ENTRY key:** `git log --oneline -- knowledge/qa/evidence/predicted-number-pin-census-2026-08-12/labelled-instances.md` (from cwd) for a commit whose subject names the slug.
>
> - **FRESH** = (1) empty AND (2) no commit → proceed at Task B.
> - **RE-ENTRY-A** = (1) empty AND (2) present AND no findings document exists → the census is DONE; resume at Task C against the COMMITTED labels; **do not re-label** (re-labelling destroys the only artifact proving labels preceded matching).
> - **RE-ENTRY-B** = (1) empty AND (2) present AND a findings document exists → full re-run permitted, but the prior matcher output must be discarded before any re-labelling (C2's ordering otherwise breaks).
> - **NONE-MATCH** = anything else → **HALT quoting every measurement taken.**
>
> **Task B — the census (Q1).** Read the **Depends on** sources. **Discovery is grep-driven with `-F` (fixed-string) literals** — the shop's grep is a ugrep shim where a non-`-F` search can exit 1 silently on a present line. Markers at minimum: `predicted`, `fabricat`, `tally`, `FABRICATED TAIL`; **record every discovery command and its file-hit list in `labelled-instances.md`** so the census's coverage is auditable. Enumerate instances into `labelled-instances.md` (one row per instance: source, recorded text, date, subclass, caught-by, recoverability mark). For subclass-A instances, recover original bytes via `git -C /Users/marklehn/Developer/GitHub log -p --` over the named governance draft files and record the recovering commit per instance (or the mark UNRECOVERABLE). **Commit `labelled-instances.md` ALONE** from the step's own cwd (the Worktree Rule; A0's shape assert already ran), subject carrying `[<id from your plan filename>]` + the slug — this commit is C2's guard.
>
> **Task C — the instrument (Q2).** Write `matcher-m1-git-pins.py` and `matcher-m2-file-pins.py` under the evidence directory. Run them over the corpus **as Q2 defines it** (the boundary and file count go in the findings — restating the boundary here is how two sites diverge). Classify every fire (RESOLVES-NOW / STALE / NEVER-TRUE-SURVIVING / CROSS-REPO / AMBIGUOUS — RESOLVES-NOW, not "true at deposit": a pin resolving today does not prove it resolved when authored, and the findings say so once where the cell is defined; with the ever-true test's raw output); write all raw output to `precision-raw.txt`. ⚠️ Verify rather than assume every count; report the actual numbers.
>
> **Task D — recall + the Q4 heuristic.** Run M1/M2 against the labelled subclass-A set (Q3 form: `k of N recoverable, of T named` or `NOT MEASURABLE (N=0)`). Price the verify-clause-proximity heuristic over the corpus's QA rows (Q4); hand-classify ALL fires when the count permits within the step, otherwise a sample of at least 20 with the selection method stated.
>
> **Task E — findings.** Write `predicted-number-lint-findings-2026-08-12.md` answering Q1–Q5 (dispositions in Q5's exact form). Close with `#### Prompt Feedback` and `#### Forward Register:` (rows or the literal `NONE`). Commit the remaining deposits from the step's own cwd (the Worktree Rule) with a pathspec naming exactly the deposit paths, then STOP.
>
> **Deposits:**
> - `bellows/knowledge/qa/evidence/predicted-number-pin-census-2026-08-12/labelled-instances.md`
> - `bellows/knowledge/qa/evidence/predicted-number-pin-census-2026-08-12/matcher-m1-git-pins.py`
> - `bellows/knowledge/qa/evidence/predicted-number-pin-census-2026-08-12/matcher-m2-file-pins.py`
> - `bellows/knowledge/qa/evidence/predicted-number-pin-census-2026-08-12/precision-raw.txt`
> - `bellows/knowledge/research/predicted-number-lint-findings-2026-08-12.md`
>
> **Scope:**
> - `bellows/knowledge/qa/evidence/predicted-number-pin-census-2026-08-12/labelled-instances.md`
> - `bellows/knowledge/qa/evidence/predicted-number-pin-census-2026-08-12/matcher-m1-git-pins.py`
> - `bellows/knowledge/qa/evidence/predicted-number-pin-census-2026-08-12/matcher-m2-file-pins.py`
> - `bellows/knowledge/qa/evidence/predicted-number-pin-census-2026-08-12/precision-raw.txt`
> - `bellows/knowledge/research/predicted-number-lint-findings-2026-08-12.md`

---

## STEP 2 — QA

> ⚠️⚠️ **PRECONDITION — assert Step 1 ran as its own dispatch.** `git log --oneline -- knowledge/qa/evidence/predicted-number-pin-census-2026-08-12/` (from cwd) shows Step-1 commits made before this step began, and this step's context did not produce them. If this step is running in the same context that produced Step 1, say so plainly in the QA report and mark the independence gap rather than reporting a clean QA.
>
> **(A) Rule 20 self-check block** — emit the canonical block from `/Users/marklehn/Developer/GitHub/RULE_20_SELF_CHECK_BLOCK.md` (absolute operand, read live, never recalled). The receipt carries the canonical header `Rule 20 — QA Self-Check Results` and, when every item passes, the canonical verdict line `PASSED — SELF-CHECK PASSED`. This plan deposits real evidence files, so the FULL canonical block applies; `required_evidence_files` is the evidence-directory subset of `## Scope`, read from there.
>
> **(B) Deliverable verification:**
> - **Item 1 — C1:** porcelain empty on `scripts/ tests/`; both matcher files present under the evidence directory.
> - **Item 2 — C2 from git, not narration:** `git show --stat` on the labelled-set commit shows `labelled-instances.md` alone, no findings document in that tree.
> - **Item 3 — C3:** every Q2/Q3/Q4 figure reads as a count with denominator or the literal `NOT MEASURABLE (N=0)`.
> - **Item 4 — C4:** every 336/337 number carries its citation; none recomputed.
> - **Item 5 — C5:** Q1's marks partition the named set; each count stated.
> - **Item 6 — C6:** sweep the findings document for bare numerals and hex literals; each is either quoted from `precision-raw.txt`/step output or carries an authoring-time/re-count mark. Report violations as FAIL.
> - **Item 7 — spot-check three labelled instances** against their recorded sources at the recovering commits Task B named; a mark that does not survive the reader is a FAIL.
> - **Item 8 — raw output.** Every count in the receipt is the command's own stdout, pasted.
>
> **Deposits:**
> - `bellows/knowledge/qa/evidence/predicted-number-pin-census-2026-08-12/qa-receipt.md`
>
> **Scope:**
> - `bellows/knowledge/qa/evidence/predicted-number-pin-census-2026-08-12/qa-receipt.md`

---

## Drafting Cycle

**Tier:** T1 — **T-7 fires** (a build plan will act on these findings without re-deriving them). T-2/T-5/T-6 do not fire: read-only outside this plan's own deposits, nothing installs into a gate. Not self-escalated: the artifact is a measurement and its blast radius is a document.

**Walk register:** `governance/knowledge/research/walk-register-predicted-number-pin-census-2026-08-12.md` (schema 0.2), committed per phase; the Deviations line's commit range ends with the open tail, closing commit named at wrap.

**Walks:** 4. Fold trajectory 11 → 6 → 2 → 0; walk 3's two folds were both the cycle's own fold damage (f18 a stale corpus shorthand f15 left behind, f19 a register schema-(d) violation), and walk 4 ran every lens dry.

- Weak spots:      w1 4 — 4 pre / 0 fold; w2 2 — 2/0; w3 1 — 0/1; w4 0.
- Destruction:     w1 2 — 2/0; w2 1 — 1/0; w3 0; w4 0.
- Vulnerabilities: w1 3 — 3/0; w2 2 — 2/0; w3 0; w4 0.
- Integration:     w1 2 — 1/1 (f11 caught f10's own over-narrow wording same-lens); w2 0; w3 0; w4 0.
- ACID:            w1 0; w2 1 — 1/0; w3 1 — 0/1 (record-class); w4 0.

**Conformance:** register validator (`bellows/scripts/walk_register_lint.py`) run at walk 3 and at close — CONFORMANT both runs. `plan_lint` runs at the staged deposit mirror at freeze; its result is recorded in the deposit commit, not predicted here.

**Closing:** walk 4 DRY — **instruction 0 / record 0**, no residue to enumerate; the last event before deposit is a dry lens pass (§2.8 bar met without the judged-stop relaxation).
