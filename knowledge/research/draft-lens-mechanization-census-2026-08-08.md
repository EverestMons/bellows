# Diagnostic: which drafting-cycle findings were check-shaped — a lens-mechanization census over the preserved per-phase commits

**Type:** Diagnostic
**Project:** bellows
**Depends on:** none new. Cites diag-305 (Done, governance — the enforceability-census method this plan generalizes; its deposit `/Users/marklehn/Developer/GitHub/governance/knowledge/research/enforceability-assessment-2026-08-06.md` is REQUIRED READING for the executing agent — the polarity-pair and retraction-control method source) and the shipped per-phase-commit rule (DRAFTING_CYCLE.md §2.7 — codified in v1.5, current version 1.6 verified at authoring) whose artifacts are this plan's corpus.
**Created:** 2026-08-08
**Author:** Planner
**dispatch_mode:** bellows
**pause_for_verdict:** always
**Priority:** 10
**cycle_tier:** T1

⚠️ **ID NOTE — the deposit filename is decided AT DEPOSIT.** Bellows mints the id from `id_sequence` at claim and does not parse the filename. **Re-read `id_sequence` at deposit and re-token every id site** (the 310→311 drift fired live; read 321 at authoring of the HELD sibling draft — treat every number as stale until re-read).

---

## Why this exists — the CEO's question, made measurable

**CEO direction 2026-08-08: explore how the drafting-cycle lenses can be more mechanical code and less prose/reasoning, without shortening the cycle (dry stays the exit).** The lens work decomposes into evidence-gathering, candidate-generation, and judgment; the first two are scriptable in principle. The question this diagnostic answers is **which checks would actually have paid**, measured against the real findings record — not argued from the lens register.

**This is the 315 → 317 arc shape applied to the lenses: measure first, build only what the measurement licenses.** This diagnostic builds nothing permanent and chooses nothing. It classifies, constructs prototypes in `/tmp`, fires them at historical states, and reports.

**The corpus exists and is machine-addressable — verified at authoring (Rule 52; every item is a prediction to re-verify at run, never inherit):**

- §2.7's per-phase-commit rule means each recent T2 cycle preserved its full drafting history as `[draft] … culmination — N folds: <labels>` commits, with the close commit stating the count ("21 drafting commits preserved" — 317's close `253c085`).
- Verified per-cycle at authoring (each a prediction to re-verify): **311** → lessons-forge root, draft `knowledge/research/draft-cycle-run-2026-08-07.md`, **16 commits touch the path (15 `[draft]` + the close)** — ⚠️ **while the close commit `e52275f` claims "30 drafting commits preserved": MEASURED DISCREPANCY, unresolved at authoring. Close-commit counts are unreliable reconciliation anchors; the PATH enumeration is authoritative.** **317** → bellows, draft `knowledge/research/draft-clean-gate-auto-continue-2026-08-08.md` (close `253c085` claims 21). **320** → the shop root repo (governance in-place dispatch), draft `…draft-template-qa-and-terminal-correction-2026-08-08.md` — ⚠️ **its close `74fd2b9` states NO commit count at all.** Absence and mismatch are both reportable states, never smoothed.
- The pre-fold state of any finding is therefore recoverable: `git show <phase-commit>~1:<draft-path>` — **a constructed checker can be RUN against the exact artifact the finding was found in.** The 305 bar ("executed, not argued") is satisfiable here, and this plan requires it. (311's draft path is rename-stable across its whole history — verified with `--follow` at authoring; still run every enumeration with `--follow`, and recover paths with `--name-only`, **never `--stat`, which truncates paths silently** — observed at authoring on 317's.)

⚠️⚠️ **TWO STANDING FIGURES ARE HYPOTHESES HERE, NOT TARGETS.** Doctrine (§2/§2.6) carries "yield stays flat: 11/12/12/12/12" and "roughly a third of each round are the previous round's folds' defects." **This plan re-measures both on this corpus and reports the measured value with the method beside it. Do not force either number; a divergence is a finding, not an error** (4/4 predicted numbers were wrong in one recorded session — the hedge is the protection).

⚠️ **A "JUDGMENT-ONLY" CLASSIFICATION IS A REAL ANSWER AND THIS PLAN IS BUILT TO RETURN MANY.** The lens core questions are judgment by design; mechanizing them would be the Goodhart failure §3 names. The census exists to find the check-shaped MINORITY and price it honestly — **the reason a finding is classified judgment-only must be stated per finding, because the reason for not mechanizing is itself a claim.**

---

## The candidate-check taxonomy — fixed at authoring, extended only explicitly

Every finding is classified into exactly one primary bucket (secondary allowed where genuinely dual):

| id | candidate check | mechanizes |
|---|---|---|
| **M1** | anchor liveness — every quoted anchor/path in the draft `grep -F`-verified against the live target file | lens 1.1 / Rule 22(a) |
| **M2** | R/W window enumeration — per-step Scope+Deposits parsed to read/write sets; cross-gate W-R/R-W/W-W overlaps listed | lens 5.3 |
| **M3** | mandated-command harness — extract mandated commands; run each; confirm stated success/failure outputs exist and differ; flag non-`-F` literal greps | §2.7 execute-against-real-data |
| **M4** | executable ledger constraints + post-fold battery — a `C<n>` entry carrying a runnable `check:`; the battery re-run after every fold | §2.8 record-without-prevent |
| **M5** | clone structural diff — machinery blocks present in origin/newest-same-class but absent in the clone, listed | §2.6 |
| **M6** | consumer census — all reference forms (incl. attribute-style like `data-*-endpoint`) of every touched surface, enumerated | lens 2.1/2.2 evidence half |
| **M7** | guard-relaxation diff — deleted/weakened assertions, lowered thresholds, removed test asserts in a diff | lens 2.2 |
| **M8** | environment probes — non-ASCII scan for CEO-run scripts; `from X import <patched-name>` isolation-bypass lint | lens 3.1/3.3 |
| **R** | record-class — already covered by a SHIPPED plan_lint check ((f)–(l)) or by the HELD rows-25/27/28 batch ((m), panel-content, negation-gap). **Name which check per finding.** | §3/§4 |
| **J** | judgment-only — no mechanical form exists; **state the reason per finding** | — |
| **O** | other-mechanizable — none of M1–M8 fits but a mechanical form exists; **propose it precisely enough to implement** | — |

⚠️ **The taxonomy is seeded from the Planner's session-27 analysis and is itself under test — a bucket with zero measured coverage is a finding against the Planner's table, and O-bucket entries that cluster are the discovery this plan exists to make. Neither direction is preferred.**

---

## Questions

**Q1 — Corpus assembly (the census floor).** For each REQUIRED cycle — **311 (lessons-forge), 317 (bellows), 320 (shop root)** — derive the population MECHANICALLY:

1. Locate the cycle's close commit (`git log --oneline` filtered `-F "close(<N>)"`) and recover the deleted draft path from it with `--name-only` (**not `--stat` — it truncates**).
2. Enumerate `git log --follow --oneline --name-only -- <draft-path>`: **every commit touching the draft path is a census row.** The `[draft]` message prefix is a LABEL to record, **never the filter** — a prefix-grep and the path population have already diverged once at authoring. ⚠️ **Take each commit's draft path FROM the `--name-only` output of that commit — never assume the final path holds across history (a rename breaks `git show <early-sha>:<late-path>`); on a "path does not exist in <sha>" error, re-derive the path at that commit rather than skipping the row.**
3. Per row record: SHA, phase label (v0/w1/a1/seat-N/cc/aC/re-token…), declared fold count **or NONE**, files touched. ⚠️ **Rows with no declared fold count (v0, re-token, record-sync commits) are 0-finding census rows, kept in the table — they are themselves Q4-relevant data (record maintenance has a wall-clock cost the do-nothing column needs).** Degenerate rows, handled not skipped: **a MERGE commit's pre-state is `<sha>^1` and the row is merge-flagged; a commit touching the draft among unrelated files (a session-wrap sweep) is flagged NON-PHASE.** **Every finding diff is computed path-restricted — `git show <sha> -- <draft-path>` — so an unrelated co-committed file can never contribute hunks.**

**Reconcile three independently-produced numbers and report every mismatch rather than smoothing it:** (a) the path-enumeration commit count vs the close commit's claimed count — **which may be absent (320) or wrong (311: claims 30, path says 16, measured at authoring — do not resolve this by argument; report what the enumeration shows)**; (b) the per-phase declared fold counts vs the plan's Cycle Log per-lens lines. Close commits count COMMITS; Cycle Logs count FOLDS — never reconcile one against the other's column.

The finding unit is one fold; its ground truth is the commit DIFF, its label the commit-message clause. ⚠️ **Segmentation rule: when a commit declares N folds and its message clauses or diff hunks segment into a different number, the DECLARED count governs the census row, the discrepancy is recorded in the table, and per-finding rows from that commit carry a LOW-CONFIDENCE mark on their hunk attribution.** Report the full table (cycle × phase × finding-id × one-line label).

**Q2 — Classification.** Classify every Q1 finding into the taxonomy. Per finding: primary bucket, the diff hunk(s) it rests on, and — for J — the stated reason no mechanical form exists. Report per-bucket totals **per cycle and overall**, and per-bucket the finding-ids (no aggregate-only claims). **AMBIGUOUS is an honest cell; use it rather than forcing a bucket, and count it separately.** ⚠️⚠️ **The classification FREEZES before any Q3 prototype runs — and the freeze is a COMMIT, not an intention: when Q1+Q2 are written, commit the deposit file (same explicit pathspec) BEFORE starting Q3; the final commit lands at completion, and the verdict reader can diff the two.** A bucket change after seeing a prototype's misses is a post-hoc correction: allowed only as a struck-through original + new bucket + reason, never a silent move — **the two-commit form is what makes a silent move visible.** A census that re-sorts itself to flatter its prototypes has measured nothing.

**Q3 — Construct and fire the top candidates.** Take the **three** M/O buckets with the highest Q2 coverage (**chosen by the measurement, not pre-announced — this plan names no expected winner; a tie at rank 3 includes every tied bucket, with the expanded count reported**). For each: build a minimal prototype in `/tmp`, then run it against the **pre-fold state** (`git show <phase-commit>~1:<draft-path>`, path per the Q1 per-commit rule) of **every finding classified to that bucket**. Two construction rules:
- ⚠️⚠️ **POSITIVE CONTROL FIRST: before any real-case run counts, the prototype must fire on a constructed synthetic fixture known to contain its defect. A prototype that cannot fire on its own synthetic case is BROKEN, and its misses are evidence of nothing** — without this, a silently-broken checker reads as "the check is weak" across every real case (the (D) standard, applied to the instrument).
- **A prototype that parses plan structure (headers, step text, the Drafting Cycle block, fenced code) imports the REAL helpers — `PYTHONPATH=/Users/marklehn/Developer/GitHub/bellows` then `import gates` — never a hand-rolled re-parser, so the measured false-positive load reflects the substrate a shipped check would actually run on** (the 306 blockquoted-fence lesson: parser divergence IS the false-positive story). A hand-rolled parser is allowed only where no helper exists, and the deposit says so per prototype.

Report the polarity pair per 305:
- **fires on its own case:** per-finding fires/doesn't table. ⚠️ **A fire counts ONLY if the prototype's output LOCATES the defect within the hunk(s) that finding's fold edited** — a checker that fires somewhere else in the same file is a miss on this finding plus a false positive, not a hit; without this rule a noisy checker "catches" everything trivially. **On LOW-CONFIDENCE rows (the Q1 segmentation rule), a located fire counts ONCE at COMMIT granularity, flagged — never attributed to two findings from the same commit.** A bucket whose prototype fires on under half its own findings was misclassified or the check is weaker than the census claims; report it as such;
- **false-positive load:** run the prototype against (a) the three cycles' FINAL deposited plan texts, (b) at least two unrelated `Done/` plans per repo, and (c) **the retraction control — text that DESCRIBES or RETRACTS the defect without committing it** (305 walk-3: a checker that matches the record of a defect overstates nothing so much as its own precision). Report counts with the command beside each.

**Q4 — The re-finding decomposition (prices the post-fold battery).** For every Q1 finding, classify: **novel** vs **introduced-by-a-prior-fold** (evidence: the commit narrative — messages like "the a1's Q0 class", "fold-residue" — plus diff-overlap with prior phase hunks; **state the method and mark low-confidence rows**). Then: of the prior-fold-introduced set, what fraction classified R or M1–M8/O. ⚠️ **That fraction is a CEILING for a fold-time battery, not a catch prediction — most of those checks do not exist yet and a classification is not a fire. Report it as the ceiling, labeled as such.** **Except the slice that CAN be executed: for every R-bucket finding whose named check is SHIPPED ((f)–(l)), run the current `plan_lint` against that finding's pre-fold state and report fires/doesn't per finding — that slice moves from ceiling to MEASURED, and the held-check R slice stays ceiling-marked.** ⚠️ **Population match before comparison: doctrine's "roughly a third" and 11/12/12/12/12 describe COLD-PANEL rounds, not whole cycles. Report the re-finding rate TWICE — whole-cycle, and restricted to panel-seat rounds — and compare ONLY the panel-round slice against doctrine's figure, with the whole-cycle rate reported as this census's own new number.** State the divergence, if any, plainly.

**Q5 — Extension census (explicitly optional, never silent).** Repeat Q1+Q2 (classification only, no prototypes) for **306 (bellows, 9 commits)** and **309 (shop root, 31 commits)**. ⚠️ **If not reached, the deposit says "NOT REACHED" for Q5 with the reason — an explicit cut, never a silent one.**

**Q6 — The ranking, framed for CEO choice.** A table: candidate check × measured coverage (Q2/Q3) × fires-on-own-case rate × false-positive load × constructibility note (prototype LOC, inputs needed, where it would live — plan_lint §4 check vs standalone drafting-harness script vs fold-time battery). ⚠️ **Fire-rate and false-positive cells exist only for the buckets Q3 prototyped; constructibility cells for unprototyped buckets are marked ESTIMATE — never let an estimated cell sit unmarked beside a measured one.** ⚠️⚠️ **Coverage is CLASSIFICATION evidence, not catch evidence — a coverage count says the Planner-agent judged those findings check-shaped; only a Q3/Q4 fire-rate says a check caught them. Label the columns so a downstream build plan cannot read "coverage 14" as "catches 14" — that over-claim is exactly what this lens exists to prevent a later plan acting on.** **A recommendation with its cost, framed so the CEO can choose — including the do-nothing column: what the same findings cost in walk-phases when caught by prose.** No build is authorized by this plan.

---

## Method + boundaries

- **READ-ONLY on every repo.** Prototypes live in `/tmp` only. Do NOT edit any plan, any script, any test, any ledger; do not restart the daemon. The ONLY writes are the deposit file and its commit. ⚠️⚠️ **NO HEAD-moving command in ANY repo — `git checkout`, `switch`, `restore`, `stash`, `reset` are all forbidden; a historical state is materialized ONLY as `git show <sha>:<path> > /tmp/<name>` and read from there.** The deposit commit uses an explicit pathspec naming the deposit file alone — **never `git add -A`** (the worktree may carry the live cycle draft or stray artifacts that are not this plan's to commit).
- **Execute against the real corpus.** Every "would fire" claim is backed by pasted output from a run against the recovered historical state — a reasoned prediction is not a finding (305's bar).
- ⚠️ **`grep` here is a ugrep shim: `-F` mandatory for literals, `--` before leading-dash patterns; a non-`-F` search can exit 1 SILENTLY on a present line.** ⚠️ **A negative result (empty search, exit-code-read-as-absent, file-not-found) never supports a finding on its own — pair it with a positive control, a second independently-constructed probe, or a read of the implementation site (the (D) standard).**
- **Per-finding results, not aggregates.** "M1 covers 14 findings" is not reportable without the 14 ids and their per-id fire results.
- **Report per-cycle results including zeros.** Pin each repo's HEAD (`git -C <root> rev-parse HEAD`) in the deposit beside every count — the corpus moves. **Bookend the run: re-run the same three pins as the LAST act before the Receipt and report both sets; a delta is concurrent activity — name it in the deposit and never force internal numbers to reconcile across it** (315's bookend rule, adapted from the live DB to live repos). The shell is zsh: an unmatched glob aborts the command — use `find … -name '…'`, never a bare glob.
- **Output-volume discipline — the deposit must stay readable and the step inside its context.** The census table is compact (one row per finding); diffs are REFERENCED by SHA + hunk header with only the decisive lines pasted; prototype output is trimmed to the firing/non-firing evidence lines plus counts — full raw output is mandatory only for the Q3 false-positive/control runs and the Q4 executed slice. **Write the deposit file incrementally as each question completes, in order — never hold six answers in flight for one final write.**
- The three cycles span three repos, addressed ABSOLUTELY (a bellows worktree's relative paths resolve against the worktree): **311 → `/Users/marklehn/Developer/GitHub/lessons-forge` · 317 → `/Users/marklehn/Developer/GitHub/bellows` · 320 → `/Users/marklehn/Developer/GitHub` (the shop root; its log also carries OTHER cycles' `[draft]` commits — 309, codify-d — which is why the population filter is the draft PATH, never the message prefix).** Extension roots (Q5): 306 → bellows, 309 → the shop root. **Re-derive each draft path per the Q1 recipe; never assume the authoring-time examples still hold.**
- If a question cannot be answered from here, say so in `## Unresolved` rather than guessing.
- **The half-complete state, stated (§2.5): if the step dies mid-run, no repo state was mutated (read-only + no-HEAD-moving) — the loss is wall-clock only, and the two-commit deposit form bounds it: a death after the Q2 freeze commit preserves the census on the step branch.** Acceptable on both counts; nothing else to guard.

## Required deposit structure — the answers are not the deliverable, the CONTRACT is

`knowledge/research/lens-mechanization-census-2026-08-08.md`, containing:

1. **The Q1 census table** — every phase commit, every finding, with the reconciliation mismatches called out.
2. **The Q2 classification** — per-finding bucket + evidence, per-bucket totals per cycle, AMBIGUOUS counted separately, J reasons per finding.
3. **The Q3 prototype results** — each prototype's source (inline or /tmp path + pasted content), the per-finding fires/doesn't table, and the three-part false-positive run with raw output.
4. **The Q4 decomposition** — measured re-finding rate beside doctrine's figure, method stated, low-confidence rows marked.
5. **Q5 or its explicit NOT REACHED.**
6. **The Q6 ranking table with the recommendation-for-choice.**
7. **`## Unresolved`** — every question not settled from evidence, or the word NONE.

**Scope:**
- `knowledge/research/lens-mechanization-census-2026-08-08.md`

**Deposits:**
- `bellows/knowledge/research/lens-mechanization-census-2026-08-08.md`

### Output Receipt

Close with `### Status` (**Complete**), `### Deposits` (the findings file), and `### Ledger Updates` containing `#### Prompt Feedback`. **No Forward Register block — this diagnostic enqueues nothing; the follow-on routing (the build decision, and any defect found in passing, which belongs in the findings/`## Unresolved`) is the Planner's, from the findings** (315's convention; the channel's measured failure modes are not risked for zero items).

---

## Drafting Cycle

**This section is a RECORD, not instructions.** Gate-matching strings are described here, never quoted.

**Tier:** T1 — computed. **T-7 fires** (a build executable will act on these findings without re-verification — that is the arc's whole point). **T-8 also recorded as firing under the if-unsure rule (315 precedent):** the census shape follows 305 and the skeleton follows 315, but the multi-repo commit-archaeology + prototype-firing mechanics are not a structure-for-structure clone of either. T-2/T-6 do not fire (nothing mutated, no governance surface edited). ⚠️ **An earlier draft recorded T-4 "per the 292 precedent" — read against §1, T-4 is the MONEY-AFFECTING-PATH trigger; 292's own tier line mis-names it ("a change to a mechanism other plans depend on"), a record defect corrected here rather than propagated.** Highest demand: T1. Diagnostic-mode sub-questions 1.4 / 2.4 / 5.5 apply.

**Clone comparison (§2.6 discipline, applied though the tier is T1):** method origin = diag-305's enforceability census; newest same-class shipped diagnostic = `diagnostic-315` (bellows `Done/`), whose skeleton conventions this draft follows — no bootstrap section, no Forward Register block, bookend pins, quoted-anchor-not-line-number citations.

**Expected lint:** NOT FINAL — set at cycle close; at minimum the standing benign WARNs a T1 diagnostic carries, finalized after the §5 conformance pass.

**Walks:** 1 in progress — four lenses + ACID a1 complete, each phase its own turn under CEO direction, per-phase committed. ⚠️ This header itself went stale once (still read "no lens has run" after 26 folds) and was caught by a1's record read — the cycle's second live specimen of the record-decay class, after the 292 T-4 mis-cite.

- Weak spots:          w1 8 folded (population-by-path not prefix + close-count unreliability measured live 16-vs-30; commits-vs-folds reconciliation columns separated; 0-fold census rows; N-fold segmentation rule; Q3 fire-attribution-to-hunk; absolute roots; Q6 ESTIMATE marks; authoring claims re-based on measured paths/counts).
- Destruction:         w1 5 folded (2.4-aimed: no-HEAD-moving-commands guard — checkout/stash forbidden, git-show-to-/tmp only; Q2 classification freeze vs post-hoc re-sort; pathspec-only deposit commit; Q6 coverage≠catch column labeling; Q4 ceiling-vs-measured split with the shipped-check slice EXECUTED via current plan_lint).
- Vulnerabilities:     w1 5 folded (3.1 per-commit path from --name-only vs rename-broken git show; 3.2 per-prototype synthetic positive control — a broken instrument must not read as a weak check; 3.3 prototypes import real gates helpers via PYTHONPATH, no divergent re-parsers; 3.4 merge-commit ^1 + NON-PHASE sweep flags + path-restricted diffs; rank-3 tie rule).
- Integration-record:  w1 8 folded (4.1/4.4 CRITICAL: tier line's T-4 cite was 292's own mis-record cloned — corrected to T-7 + if-unsure T-8 against §1 read live, clone-comparison line added; skeleton re-based to 315 conventions: bootstrap section DROPPED, Forward block DROPPED for the enqueues-nothing form; bookend HEAD pins; zsh glob note; §2.7 version cite precision v1.5-codified/v1.6-current; 305 deposit named required reading; 4.3 output-volume discipline + incremental deposit writing).
- ACID:                a1 5 folded, apart (5.2 Q2-freeze mechanized as an intermediate pathspec commit — silent re-sorts made diff-visible; low-confidence fires count once at commit granularity; Q4 population-matched dual-slice vs doctrine's panel-round figures; 5.1 half-complete state stated — wall-clock-only loss, census preserved past the freeze commit; record read caught the Walks-header staleness, specimen 2 of the class).

**Conflicts:** C1 — the fire-attribution rule (lens 3) and the segmentation low-confidence rule (lens 1) met at ambiguous hunks and were joint-resolved in one move: commit-granularity counting, flagged, never double-attributed (a1). Constraints append at the END as earned, never inserted above an existing entry.

**Closing:** NOT REACHED — walk 1 complete (four lenses + a1, ACID apart), all folds landed. §2's closing condition (a pass returning dry over a previously unexamined region, last event a lens pass) is UNMET and NOT CLAIMED — a1 folded, so a confirming pass is owed.
