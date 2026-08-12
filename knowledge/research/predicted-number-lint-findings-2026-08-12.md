# Predicted-Number Lint Findings — 2026-08-12

**Diagnostic:** 369
**Slug:** `predicted-number-pin-census-2026-08-12`
**Census date:** 2026-08-12
**Corpus boundary:** `.md` files sitting DIRECTLY in `knowledge/decisions/` and `knowledge/decisions/Done/` of bellows and lessons-forge — no subdirectory (`drafts/`, `archived-halted-plans/` are out). File count: **543** (bellows decisions/ 4 + bellows Done/ 450 + lessons-forge decisions/ 2 + lessons-forge Done/ 87; re-count mark — the matchers' CORPUS line is the authoritative measurement).
**Predecessor diagnostics:** 336 (lint-class-census-2026-08-10, precision only), 337 (lint-class-recall-2026-08-10, recall against reconstructed positives). Figures from 336/337 are cited below with their original denominators; none are recomputed.

---

## Q1 — THE CENSUS

### Instance count

**16 instances** enumerated from the Depends-on source families. Full per-instance data in `labelled-instances.md` (committed in its own commit before the matchers ran — git shows `labelled-instances.md` alone in commit `8f0a849`, no findings document in that tree).

### Subclass distribution

| Subclass | Count | Instances |
|----------|------:|-----------|
| A (fabricated hash-tail) | 4 | #5, #14, #15, #16 |
| B (predicted count/split) | 7 | #1, #3, #6, #7, #8, #10, #12 |
| C (stale baseline) | 2 | #2, #13 |
| D (arithmetic) | 1 | #4 |
| E (inherited label) | 2 | #9, #11 |

### Recoverability partition

| Mark | Count |
|------|------:|
| RECOVERABLE-VERBATIM | 9 of 16 |
| RECOVERABLE-RECONSTRUCTED | 4 of 16 |
| UNRECOVERABLE | 3 of 16 |

The 3 UNRECOVERABLE instances are all subclass-A fabricated sha-pin tails (#14, #15, #16) — never committed to git. Each governance draft has exactly one commit (the post-correction deposit); no pre-fold revision exists. Recovery probe: `git -C /Users/marklehn/Developer/GitHub log --all --oneline -- governance/knowledge/research/draft-schema02-2026-08-12.md` → 1 commit (`fe3685d`); `…draft-rule20-inject-2026-08-12.md` → 1 commit (`f7c8777`).

### Census total vs. wrap-tally track

| Wrap point | Tally stated | Census count | Delta |
|------------|-------------|-------------|-------|
| Plan 346 (2026-08-11) | SIX | 8 | +2 |
| Plan 348 (2026-08-11) | 9+ | 8 | unclear |
| Plan 353 (2026-08-12) | ~11 | 9 | +2 |
| Session 37 pause | ~13 | 11 | +2 |
| Plan 364 (2026-08-12) | ~15 | 13 | +2 |
| Session 38 final | ~17 | 16 | +1 |

**Finding about the tally:** the wrap-tally track itself is a predicted number (subclass C — a stale baseline carried forward with `~` marks, never re-derived from a fresh count). The consistent +2 offset at multiple waypoints, and the absence of a single re-counted total in any wrap, is evidence of the class's own thesis: inherited numbers drift. The tally may also include instances this census could not identify from the grep markers — the "9+" inflection at plan 348's wrap implies instances during the 348 arc that this census's sources did not explicitly tag as belonging to the class.

⚠️ The total **16** is this census's enumeration, not the tally reconciled toward. The divergence is a finding, not an error to fix.

---

## Q2 — PRECISION OF THE PIN-VERIFICATION MATCHERS

### M1 (git-object pins — 40-hex tokens)

**Corpus:** 543 files. **Repos checked:** bellows, root (`/Users/marklehn/Developer/GitHub`), lessons-forge.

| Cell | Count | Denominator |
|------|------:|-------------|
| RESOLVES-NOW | 1 | 1 of 543 files fired |
| STALE | 0 | — |
| NEVER-TRUE-SURVIVING | 0 | — |
| CROSS-REPO | 0 | — |
| AMBIGUOUS | 0 | — |
| **Total M1 fires** | **1** | **of 543 files** |

The single RESOLVES-NOW fire is `executable-341.md:129`, token `0958b1660084343d...`, resolving in the PROJECT repo (bellows). This is a git commit hash cited in the plan text as a reference — it resolves because it names a real commit, not because it is fabricated. A RESOLVES-NOW fire is not a positive; it is a pin that still works.

⚠️ **A fire resolving today does not prove it resolved when authored** — this caveat is stated once here and applies to all RESOLVES-NOW cells.

**Prefix population (non-M1, non-M2 hex runs ≥ 12 chars):** 25 tokens (14 × 12-hex, 11 × 16-hex). These are the display-prefix population — shortened hash references in plan text.

### M2 (sha256 file pins — 64-hex tokens adjacent to shasum/sha256 invocations)

**Corpus:** 543 files.

| Cell | Count | Denominator |
|------|------:|-------------|
| RESOLVES-NOW | 0 | — |
| STALE | 11 | 11 of 24 fires |
| NEVER-TRUE-SURVIVING | 0 | — |
| AMBIGUOUS | 13 | 13 of 24 fires |
| **Total M2 fires** | **24** | **of 543 files** |

**STALE fires (11 of 24):** every one of these is a sha256 pin on a live file (`DRAFTING_CYCLE.md`, `PLANNER_TEMPLATE.md`, `RULE_20_SELF_CHECK_BLOCK.md`, `walk-register-schema.md`) that was true at the plan's deposit time. The file has since been updated, so the hash no longer matches the current content, but the ever-true test passes (a committed revision of the pinned file carries that sha256). These are NOT positives — they are pins working as designed, now stale because their target files have been amended by later plans.

⚠️ **The gc caveat (per Q2's NEVER-TRUE-SURVIVING label):** the shop runs gc on bellows. An object pruned by gc would appear as NEVER-TRUE-SURVIVING even if it was once reachable. No NEVER-TRUE-SURVIVING fires were observed in this run, so the caveat does not apply to any fire, but it constrains the interpretation of that label if it appears in a future run.

**AMBIGUOUS fires (13 of 24):** the M2 matcher found a 64-hex token near a `shasum`/`sha256` invocation but could not extract a named file path. Causes: (a) the sha256 hash appears in plan text without a directly adjacent path (the hash is stated, the file is named elsewhere in the step); (b) the path reference uses backtick-markdown formatting that the extractor does not fully parse. These fires cannot be classified without manual path resolution.

**64-hex tokens NOT fired by M2:** 56 total 64-hex tokens were found in the corpus; M2 fired on 24 of them (those with shasum/sha256 context). The remaining 32 are 64-hex tokens with no adjacent shasum invocation and are outside M2's scope.

### Precision summary

| Matcher | Fires | RESOLVES-NOW | STALE | NEVER-TRUE-SURVIVING | CROSS-REPO | AMBIGUOUS |
|---------|------:|-------------|-------|---------------------|------------|-----------|
| M1 | 1 of 543 files | 1 | 0 | 0 | 0 | 0 |
| M2 | 24 of 543 files | 0 | 11 | 0 | 0 | 13 |

**No fabricated pin was detected by either matcher.** All M1 fires resolve (not a positive); all M2 fires are STALE (true at deposit time) or AMBIGUOUS (cannot test). The matchers have zero detected true positives over 543 files. This is not evidence that the corpus is clean — it is evidence that the matchers cannot see the defect in this population (see Q3).

---

## Q3 — RECALL OF M1/M2 AGAINST THE LABELLED SUBCLASS-A INSTANCES

**`NOT MEASURABLE (N=0)`**

Of T=4 named subclass-A instances (#5, #14, #15, #16):
- Instances #14, #15, #16 are UNRECOVERABLE: the fabricated sha-pin tails were corrected before the governance drafts were committed. Each draft has exactly one commit (the post-correction deposit). The original fabricated hex bytes do not exist in any git-reachable object.
- Instance #5 (LESSONS.md:2500 "fabricated placeholder hashes") names the class but not the specific hex strings. The originating plan is not identified by number in the LESSONS entry. No bytes to test.

N=0 recoverable original bytes exist for any subclass-A instance. M1/M2 recall against subclass A is therefore not measurable — a measured zero and an unmeasurable zero are different inputs (per Q5's standing distinction).

**Why N=0:** the fabricated pins were authored, caught by a walk-2 measurement, and corrected — all before the draft was committed to git. The drafting cycle's per-phase commits (the instrumentation bellows FORWARD row 49 would provide) do not yet exist for these files. This diagnostic's inability to produce N>0 is itself the strongest argument for fold-granular draft-history instrumentation — the same finding 337 reached for its 14 RECOVERABLE-RECONSTRUCTED instances.

---

## Q4 — BARE-NUMBER SUBCLASSES (B–E): THE VERIFY-CLAUSE-PROXIMITY HEURISTIC

**336's ground on class s (HOLD — a regex cannot verify a count) is not re-litigated.** (cited: 336 findings §vi, 337 findings §v; class s fire rate 54/54 BLOCK files, 0/153 sampled TRUE, 566 total fires, 2/9 recall as-written)

### The heuristic

Flag a bare integer in a QA row that carries no verify/re-count/halt-on-mismatch clause in the same row. A QA row is a line inside a step the scanned plan's `qa_steps` header names, or whose `## STEP` heading contains `QA`.

### Results

| Metric | Value |
|--------|-------|
| Files with QA steps | 321 of 543 |
| Total QA lines | 14468 |
| Heuristic fires | 4973 of 14468 QA lines (34%) |

### Hand-classification (all 20 fires from a stride-~250 sample, selection: every 250th fire)

| # | File | Verdict | Reason |
|---|------|---------|--------|
| 1 | diagnostic-337.md | FALSE | date components (2026, 08, 10), rule reference |
| 2 | executable-294.md | FALSE | item ordinal ("8. Scope") |
| 3 | executable-332.md | FALSE | date in file path |
| 4 | executable-backlog-…md | FALSE | date in commit message |
| 5 | executable-bellows-phase8-…md | FALSE | count threshold in verification code (`>= 3`) — line IS a check |
| 6 | executable-bellows-worktree-…md | FALSE | formatting constant in Python code |
| 7 | executable-disable-auto-close-…md | FALSE | date in file path |
| 8 | executable-lessons-verdict-…md | AMBIGUOUS | "3 new rows" — a predicted count in a QA check. The count is the expected value being checked; the check itself is the verification |
| 9 | executable-planner-…md | FALSE | plan slug string |
| 10 | executable-rule-20-…md | FALSE | step number in table |
| 11 | executable-session-wrap-…md | FALSE | date in file path |
| 12 | halted-executable-…md | AMBIGUOUS | "grep count = 1" — a count assertion. The line specifies what the count SHOULD be, which is the predicted-number class; but "count = 1" is also the verify clause |
| 13 | executable-134.md | FALSE | date in file path |
| 14 | executable-274.md | FALSE | date in file path |
| 15 | executable-284.md | FALSE | rule reference ("Rule 20") |
| 16 | executable-291.md | FALSE | walk finding counts (measurements, not predictions) |
| 17 | executable-311.md | FALSE | checklist/row references |
| 18 | executable-342.md | FALSE | walk counts (measured) |
| 19 | executable-346.md | FALSE | proposal reference numbers |
| 20 | executable-gate-2a-…md | FALSE | date in file path |

**Result:** 0 TRUE of 20 sampled, 2 AMBIGUOUS, 18 FALSE. The AMBIGUOUS fires are lines where the predicted count and its verification are co-located on the same line — the absence of verify-words is misleading because the line IS the verification command.

### Q4 finding

The verify-clause-proximity heuristic **does not escape 336's ground that a regex cannot verify a count.** The heuristic fires at 34% of QA lines because:
1. **Dates** (2026, 08, 10, 12) appear in file paths, dates, and reference strings on nearly every QA line
2. **Structural numbers** (item ordinals, rule references, plan IDs, proposal numbers) are ubiquitous
3. **The verify-word vocabulary** ("verify", "re-count", etc.) does not capture inline code checks, count assertions in different phrasings, or verify-by-construction patterns

A heuristic that fires on 34% of all QA lines with 0/20 true positives in a hand-classified sample is unshippable at any threshold. The problem is the same as class s: the regex identifies the presence of a number but cannot determine whether it is a prediction, a measurement, a reference, or a structural identifier.

**Class s's HOLD stands. No disposition change offered.**

---

## Q5 — DISPOSITION PER SUBCLASS

### Subclass A (fabricated hash-tail)

**Precision:** M1: 0 of 1 fires TRUE, of 543 files; M2: 0 of 24 fires TRUE (11 STALE, 13 AMBIGUOUS), of 543 files. No NEVER-TRUE-SURVIVING fire in either matcher.
**Recall:** `NOT MEASURABLE (N=0)` — 0 of 0 recoverable, of 4 named. All 4 subclass-A instances have original bytes that are UNRECOVERABLE (3) or untraceable (1).

**Disposition: HOLD.**

Neither precision nor recall can support SHIP-warn:
- Precision is clean (no false positives), but it is clean because no positive exists in the corpus — the same unfalsifiable-precision problem 336's A3 addendum identified. A matcher scoring zero over a population with no positives proves nothing.
- Recall is not measurable. The original fabricated bytes were never committed. Until fold-granular draft-history instrumentation makes pre-fold pin text recoverable, no matcher can be priced against the instances that define this class.

HOLD does not mean the class is unreal. The 4 instances exist and were caught. The gap is in the MEASUREMENT INSTRUMENT, not in the defect. The concrete successor is:
1. **Fold-granular draft-history instrumentation** (bellows FORWARD row 49) — per-phase commits of governance drafts would make pre-fold pin text git-recoverable, enabling a recall measurement for any future matcher.
2. **Deposit-time pin-verification hook** — a check that runs `git cat-file -e` / `shasum -a 256` on every 40-hex and 64-hex token at deposit, BEFORE the fabricated tail is corrected by a walk. This would catch the defect at its origin rather than in the corpus post-correction.

The deposit-time hook is the stronger candidate: it operates on the text the Planner authors, at the moment of authoring, before any correction. A lint check over Done/ plans can never see a fabricated pin because the fabrication was corrected before deposit. **The right instrument for this class is a deposit-time check, not a corpus lint check.**

### Subclasses B–E (predicted count/split, stale baseline, arithmetic, inherited label)

**Precision:** the verify-clause-proximity heuristic fires at 4973 of 14468 QA lines (34%), with 0 of 20 sampled TRUE and 2 AMBIGUOUS.
**Recall:** not measured (subclasses B–E are not pin-shaped; M1/M2 do not apply; the heuristic's fire rate makes recall measurement uninformative).

**Disposition: HOLD (class s's HOLD extended — 336's ground unchanged).**

336's finding is confirmed: a regex/heuristic cannot distinguish a predicted count from a date, a reference, or a structural identifier. The verify-clause-proximity heuristic does not escape this ground — it merely demonstrates the same limitation on a different matching surface. No redesign within text-matching fixes the fundamental problem.

The concrete successors for B–E remain:
1. **Fold-granular history** (FORWARD row 49) — would enable the machine-countable-enumeration approach 337 identified (a tool that finds the enumeration and counts its items), which is not a regex.
2. **Authoring-time verify-clause enforcement** — a `plan_lint.py` check that ensures every QA row containing a bare integer also contains a verify clause. This was the original candidate and its pricing is now complete: at a 34% fire rate with ~0% true positive rate, it is unshippable. The fire rate would need to drop below ~5% before warn-first is viable, and that requires separating dates/references from predictions — a problem no regex solves.

---

## Closing

This diagnostic measured and disposed; it built nothing.

### What was measured
1. The predicted-number class has **16 recorded instances** across 5 subclasses — 4 fabricated-hash-tail, 7 predicted-count, 2 stale-baseline, 1 arithmetic, 2 inherited-label.
2. The wrap-tally track (~17) diverges from the census (16) by +1, with a consistent +2 offset at earlier waypoints — the tally itself is a predicted number.
3. M1/M2 precision over 543 files: 0 true positives (1 RESOLVES-NOW, 11 STALE, 13 AMBIGUOUS). No fabricated pin survives into Done/.
4. M1/M2 recall against subclass A: NOT MEASURABLE (N=0). The fabricated bytes were never committed.
5. The verify-clause-proximity heuristic fires at 34% of QA lines with 0/20 true positives sampled.

### What is disposed
- **Subclass A:** HOLD — pending deposit-time pin-verification hook or fold-granular draft history.
- **Subclasses B–E:** HOLD — class s's ground (336) unchanged; the heuristic pricing confirms it.

### What authorizes the Hold
HOLD routes to two concrete successor artifacts:
1. **Bellows FORWARD row 49** — fold-granular draft-history instrumentation. This is the load-bearing prerequisite for any recall measurement against subclass A, and for the machine-countable-enumeration approach to subclasses B–E.
2. **A deposit-time pin-verification hook** — the only instrument that can see fabricated pins before they are corrected by walks. This is a NEW candidate not in FORWARD; the evidence is this diagnostic's finding that no corpus-time matcher can see the defect.

⚠️ **N=0 does not imply RETIRE.** The class is real (16 instances, 4 from subclass A in one day). What is missing is the measurement instrument, not the defect.

#### Prompt Feedback
NONE

#### Forward Register:
NONE
