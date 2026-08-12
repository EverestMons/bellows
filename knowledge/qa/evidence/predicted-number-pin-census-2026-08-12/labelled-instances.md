# Predicted-Number Class — Labelled Instance Census

**Diagnostic:** 369
**Slug:** `predicted-number-pin-census-2026-08-12`
**Census date:** 2026-08-12
**Source families:** memory `plan-predicted-numbers-need-verify-clause.md`, `LESSONS.md` (grep -F "predicted" + grep -F "fabricat"), `shop_next_session.md` session-38 wrap blocks, governance research drafts (`draft-schema02-2026-08-12.md`, `draft-rule20-inject-2026-08-12.md`), 336/337 findings (cited, never recomputed)

---

## Discovery Commands

| Command | Hit-file list |
|---------|--------------|
| `grep -rn -F "predicted" /Users/marklehn/Developer/GitHub/LESSONS.md` | Lines 1652, 1654, 1656, 1776, 2413, 3294, 3753 |
| `grep -rn -F "fabricat" /Users/marklehn/Developer/GitHub/LESSONS.md` | Lines 19, 1760, 1949, 2277, 2500 |
| `grep -rn -F "tally" /Users/marklehn/Developer/GitHub/LESSONS.md` | Lines 2455, 3581 (no class-relevant hits) |
| `grep -rn -F "FABRICATED TAIL" /Users/marklehn/Developer/GitHub/LESSONS.md` | 0 hits |
| `grep -n -F "predicted" /Users/marklehn/Developer/GitHub/shop_next_session.md` | Lines 9, 21, 35, 51, 74, 105, 127, 152, 177, 207, 218, 232, 250, 340, 504, 594, 863, 1179, 1443, 1899, 1942, 2155, 2161 |
| `grep -n -F "fabricat" /Users/marklehn/Developer/GitHub/shop_next_session.md` | Lines 9, 105, 851, 1743, 1820, 2163 |
| `grep -n -F "tally" /Users/marklehn/Developer/GitHub/shop_next_session.md` | Lines 9, 74, 105, 127, 177, 207, 218 |
| `grep -n -F "FABRICATED TAIL" /Users/marklehn/Developer/GitHub/shop_next_session.md` | 0 hits |
| `grep -rn -F "predicted" governance/knowledge/research/draft-schema02-2026-08-12.md` | Line 64 |
| `grep -rn -F "predicted" governance/knowledge/research/draft-rule20-inject-2026-08-12.md` | Line 73 |
| `grep -rn -F "fabricat" governance/knowledge/research/draft-schema02-2026-08-12.md` | Line 64 |
| `grep -rn -F "fabricat" governance/knowledge/research/draft-rule20-inject-2026-08-12.md` | Line 63 |
| `cat /Users/marklehn/.claude/projects/-Users-marklehn-Developer-GitHub/memory/plan-predicted-numbers-need-verify-clause.md` | full file (the class codification) |
| `git -C /Users/marklehn/Developer/GitHub log --all --oneline -- governance/knowledge/research/draft-schema02-2026-08-12.md` | 1 commit: `fe3685d` |
| `git -C /Users/marklehn/Developer/GitHub log --all --oneline -- governance/knowledge/research/draft-rule20-inject-2026-08-12.md` | 1 commit: `f7c8777` |

---

## Subclass Taxonomy (authoring-time hypothesis)

- **(A)** fabricated hash-tail — a full-length hex pin authored by extending a shortened display prefix with invented bytes
- **(B)** predicted count/split — a number asserting a count, split, or magnitude not yet measured
- **(C)** stale baseline — a number that was true at some prior state and was inherited without re-measurement
- **(D)** arithmetic — a number derived from calculation on other numbers, where the calculation was wrong
- **(E)** inherited label — a token (not necessarily numeric) inherited from a prior context without re-verification

---

## Instances

### CODIFICATION SET (2026-07-16, plans 203–207)

Source: memory `plan-predicted-numbers-need-verify-clause.md` + `LESSONS.md:1652–1656` + `shop_next_session.md:2155`

| # | Source | Recorded text | Date | Subclass | Caught by | Recoverability |
|---|--------|---------------|------|----------|-----------|----------------|
| 1 | Plan 203 | `status_updated_by` value `'ceo-plan-203-recovery'` — CHECK constraint allows only `planner`/`ceo`/`auto` | 2026-07-16 | B | verify clause + halt-on-mismatch | RECOVERABLE-VERBATIM (plan text in Done/) |
| 2 | Plan 204 | Suite baseline 52 — stale the moment the prior step added 9 tests | 2026-07-16 | C | verify clause + halt-on-mismatch | RECOVERABLE-VERBATIM (plan text in Done/) |
| 3 | Plan 207 | Route-count expectation `before=0, after=3` — actually 15→18, prior Gate 1 had already routed 15 | 2026-07-16 | B | verify clause + halt-on-mismatch | RECOVERABLE-VERBATIM (plan text in Done/) |
| 4 | Plan 207 | Test arithmetic 54 — actually 55; hitting 54 required silently dropping coverage | 2026-07-16 | D | verify clause: "any number other than 54 needs explaining, not accepting" | RECOVERABLE-VERBATIM (plan text in Done/) |

### POST-CODIFICATION INSTANCES (pre-session-36)

Source: `LESSONS.md:2500` (2026-08-03 cold panel entry)

| # | Source | Recorded text | Date | Subclass | Caught by | Recoverability |
|---|--------|---------------|------|----------|-----------|----------------|
| 5 | Cold panel (plan ~289 era) | "fabricated placeholder hashes written in as authoring pins" — stated as measured, not measured | 2026-08-03 | A | cold panel seats — "read the claim rather than re-running it" was the pass that MISSED them | RECOVERABLE-RECONSTRUCTED (LESSONS entry describes the defect; original plan text in Done/) |

### SESSION 36 — PLAN 345 (2026-08-11)

Source: `shop_next_session.md:250`

| # | Source | Recorded text | Date | Subclass | Caught by | Recoverability |
|---|--------|---------------|------|----------|-----------|----------------|
| 6 | Plan 345 QA row 10 | Predicted numbers 28/167 — measurement corrected to 30/137 | 2026-08-11 | B | verify clause (Checklist #29 class — the exact rule the batch itself codified) | RECOVERABLE-VERBATIM (plan text in Done/) |

### SESSION 36 — PLAN 346 (2026-08-11)

Source: `shop_next_session.md:218`

| # | Source | Recorded text | Date | Subclass | Caught by | Recoverability |
|---|--------|---------------|------|----------|-----------|----------------|
| 7 | Plan 346 QA row 6 | "171 pre-flip" (population blend: implemented\|codify 82 + implemented\|NULL 89 = 171) — true value 156 | 2026-08-11 | B | verify clause: report-with-delta instead of halting | RECOVERABLE-VERBATIM (plan text in Done/) |
| 8 | Plan 346 QA row 10 | `###` census constant 13 — true value 11==11 (the row asserted UNCHANGED invariant, which held) | 2026-08-11 | B | UNCHANGED invariant assertion | RECOVERABLE-VERBATIM (plan text in Done/) |

### SESSION 36 — PLAN 353 (2026-08-12 early)

Source: `shop_next_session.md:114,127`

| # | Source | Recorded text | Date | Subclass | Caught by | Recoverability |
|---|--------|---------------|------|----------|-----------|----------------|
| 9 | Plan 353 panel seat 1 | Inherited category pin `instrumentation` (should be `governance_rule`) for proposal 315 — inherited from a prior cycle, never re-verified | 2026-08-12 | E | panel register-plain seat (sixth consecutive HIGH), proven by scratch flip | RECOVERABLE-VERBATIM (plan/wrap text in Done/) |

### SESSION 37–38 — GATE2-PT3 CYCLE (2026-08-12)

Source: `shop_next_session.md:92,105`

| # | Source | Recorded text | Date | Subclass | Caught by | Recoverability |
|---|--------|---------------|------|----------|-----------|----------------|
| 10 | Gate2-pt3 cycle walk 2 | "recalled-2-against-printed-1" — recalled a count of 2 when printed output showed 1 (the "same-output fabrication") | 2026-08-12 | B | walk-2 measurement | RECOVERABLE-RECONSTRUCTED (described in wrap; original text corrected in-session) |
| 11 | Gate2-pt3 cycle walk 0 | "recalled tail-literal claim" — a literal claimed from recall rather than measurement (struck) | 2026-08-12 | E | walk-0 measurement; struck in register | RECOVERABLE-RECONSTRUCTED (described in wrap; original text corrected in-session) |

### SESSION 38 — 2026-08-12 (THE FOUR TODAY)

Source: `shop_next_session.md:9`, governance drafts

| # | Source | Recorded text | Date | Subclass | Caught by | Recoverability |
|---|--------|---------------|------|----------|-----------|----------------|
| 12 | Plan 360 walk 2 | Assumed 15+1 route split — measured 9+7 (the Gate-1 routing rehearsal) | 2026-08-12 | B | walk-2 rehearsal measurement | RECOVERABLE-VERBATIM (plan text in halted-360) |
| 13 | Plan 356 seat 5 | `total post = 1` staleness — a stale baseline value | 2026-08-12 | C | panel seat 5 (ACID capstone) | RECOVERABLE-RECONSTRUCTED (described in wrap text) |
| 14 | Draft-schema02 walk 2 | A1 sha pin: prefix `66c4da1e` (20-char display prefix) extended with invented hex bytes to form a full 64-hex sha256 pin — corrected to measured `66c4da1e77aba74a1daa2508867aaa752cdb18db2712ecd709073740e8c96418` | 2026-08-12 | A | walk-2 vulnerabilities lens; fresh `shasum -a 256` measurement | UNRECOVERABLE (never committed; only one commit `fe3685d` contains the corrected version) |
| 15 | Draft-rule20-inject walk 2 | A1 sha pin for `gates.py`: prefix `27c8b779` (16-char display prefix) extended with invented hex bytes — corrected to measured `27c8b7796ac1ce2dc1b5c961ed951f4240be2f98acb0d97f4b2205bade45e36d` | 2026-08-12 | A | walk-2 vulnerabilities lens; fresh `shasum -a 256` measurement | UNRECOVERABLE (never committed; only one commit `f7c8777` contains the corrected version) |
| 16 | Draft-rule20-inject walk 2 | A1 sha pin for `bellows.py`: prefix `e5ed3450` (16-char display prefix) extended with invented hex bytes — corrected to measured `e5ed34508104764aa0e5a18575a239dfbc130aa579e8243a51a6deab475e67fb` | 2026-08-12 | A | walk-2 vulnerabilities lens; fresh `shasum -a 256` measurement | UNRECOVERABLE (never committed; only one commit `f7c8777` contains the corrected version) |

---

## Recoverability Partition

| Mark | Count |
|------|------:|
| RECOVERABLE-VERBATIM | 9 |
| RECOVERABLE-RECONSTRUCTED | 4 |
| UNRECOVERABLE | 3 |
| **Total** | **16** |

---

## Subclass Distribution

| Subclass | Count | Instances |
|----------|------:|-----------|
| A (fabricated hash-tail) | 4 | #5, #14, #15, #16 |
| B (predicted count/split) | 7 | #1, #3, #6, #7, #8, #10, #12 |
| C (stale baseline) | 2 | #2, #13 |
| D (arithmetic) | 1 | #4 |
| E (inherited label) | 2 | #9, #11 |
| **Total** | **16** | — |

---

## Census Total vs. Wrap-Tally Track

The `shop_next_session.md` session-38 wrap blocks carry a growth track for the tally:

| Wrap point | Tally stated | Census count to that point | Divergence |
|------------|-------------|---------------------------|------------|
| Plan 346 wrap (2026-08-11) | SIX | 8 (instances 1–8) | +2 |
| Plan 348 wrap (2026-08-11) | 9+ | 8 (no new instances identified 347–348) | −1 to −∞ |
| Plan 353 wrap (2026-08-12 early) | ~11 | 9 (instance 9 added) | +2 |
| Session 37 pause (2026-08-12) | ~13 | 11 (instances 10–11 added) | +2 |
| Plan 356 wrap (2026-08-12) | ~13 | 11 (unchanged) | +2 |
| Plan 364 wrap (2026-08-12) | ~15 | 13 (instances 12–13 added) | +2 |
| Session 38 final (2026-08-12) | ~17 | 16 (instances 14–16 added; wrap counts rule20-inject's 2 pins as 1 incident → "four today") | +1 |

**Finding about the tally:** The tally is itself a Planner-authored number carried forward across wraps with approximate marks (`~`). This census finds **16** recorded instances from the named sources. The tally's stated ~17 is consistent with a per-PLAN-INCIDENT counting (rule20-inject = 1 incident despite 2 pins) where one additional instance was counted that this census could not locate in the source texts, OR a ±1 rounding on the `~` approximation. The divergence at earlier waypoints (consistently +2) suggests two instances exist in the record that this census's grep markers did not surface — the "9+" inflection in particular names more instances than this census found between plans 346–348.

⚠️ **THE TALLY ITSELF IS A PREDICTED NUMBER (subclass C: stale baseline carried forward with `~` marks).** Each wrap's tally inherits the prior wrap's number and adds new instances observed since. The `~` acknowledges imprecision but the number is never re-derived from scratch — it is a running count that the census was designed to verify. The consistent +2 offset at multiple waypoints, and the absence of a single re-counted total in any wrap, confirms the class's own thesis: inherited numbers drift.
