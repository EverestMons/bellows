# Rule 22(c) Parser False Positives — Incidence Census, Fix Shapes, Regression Fence

**Date:** 2026-08-25 | **Plan:** 531 (diagnostic) | **Author:** Agent (step 1)

---

## R-1 — Incidence Census

### Source: lifecycle.db gate_events (mode=ro)

**Total rule_22_verification gate events:** 945 (across 520 distinct plans)
**Pass:** 890 | **Fail:** 55

### Classification of 55 failures

| Class | Count | Event IDs | Description |
|---|---|---|---|
| Genuine (a) — deposit missing | 36 | 1143,1158,1189,1197,1205,1213,1221,1525,1581,1824,1943,2116–2118,2293,2390,2628,2945,3727,4092,4451–4452,4485–4489,5000–5001,5157,5338–5339,5672,5801,5868,6143 | Plan-declared deposit file not found on disk. The gate doing its job. |
| Genuine (c) — real ❌ in status cell | 5 | 4063,4093,4094,4962,6389 | QA reported actual test failures with ❌ in the status cell. Correctly blocked. |
| C5-class FP — data/info rows in verification-section tables | 10 | 1691,1946,2963,3670,4205–4207,5499–5501 | Non-verification rows (test data, progression summaries, category counts, NOTE markers) inside `## *Verification*` sections. No status cell because the row is not an assertion. Fired because `current_table_has_positive_row` was True from sibling ✅ rows. |
| Formatting FP — verification rows with non-standard status | 2 | 1988,1989 | Rows like `| (a) grep ... | ZERO HITS | No references remain |` — genuine verification assertions using descriptive status instead of ✅/PASS/OK. Arguable whether this is an FP or a formatting discipline issue. |
| C4-class FP — quoted-❌ (overridden) | 1 | 6495 | Plan 523 step 2: `| 4 | \`❌ worktree teardown failed:\` count == 2 | ✅ |` — a ✅ row flagged because ❌ appeared inside a backtick-quoted grep literal. CEO override. |
| C5-class FP — deliberate status-less info row (overridden) | 1 | 6509 | Plan 524 step 2: `| G8 | ~/.claude memory entry | Planner's post-close act — out of sandbox reach by design |` — a mandated out-of-scope marker in a gap table. CEO override. |

### Measured ratios

- **True positives:** 43 (36 deposit-missing + 5 real-❌ + 2 formatting-arguable)
- **False positives:** 12 (1 C4-class + 1 C5-class-overridden + 10 C5-class-unoverridden)
- **FP rate of failures:** 12/55 = 21.8%
- **FP rate of total events:** 12/945 = 1.27%
- **Override cost:** 2 CEO override acts + 2 Planner verification rounds (2026-08-25)
- **Non-overridden FP cost:** 10 instances where the gate fired on data rows; these either auto-closed (auto_close: true plans) or were subsumed by other blocking failures in the same step

### Supersession note

The Planner's pin values C1–C6 are re-derived above with measured counts from the database. My census supersedes the Planner's 2026-08-25 values where they differ.

### Latent FP inventory (corpus scan)

**Scope:** 283 QA reports + 210 research documents under `knowledge/qa/` and `knowledge/research/` in the bellows checkout (sampled: all bellows files scanned; watched-project QA reports reachable via gate_events only — their evidence dirs are not in this worktree).

**C4-class latent (quoted-❌ in ✅ rows):**
- `knowledge/qa/evidence/teardown-recording-precheck/qa-report.md:89` — the C4 incident row itself (already fired, overridden)
- `knowledge/qa/evidence/teardown-recording-precheck/qa-report.md:38` — second row in same report: `| \`❌ worktree teardown failed:\` | 2 (X1+X2) | 2 | ... |` — no ✅ in this row, so (c) would fire as "missing status" if the table has a positive sibling. Currently inside a "## Verification" section. **Would fire under current (c).** Latent FP.
- `knowledge/qa/phase2a-qa-2026-04-14.md:21` — `| \`❌ FAILED\` in bellows.py | Present | ✅ | grep line 211 |` — a verification table row checking for the presence of an error-path string. **Would fire under current (c) if the section header contains "verification"** (pre-section-scoping report from 2026-04-14; section heading needs manual check).

**C5-class latent:** Not practically enumerable from the corpus alone — requires running (c) against each report's verification-section tables to find status-less data rows mixed with ✅ rows. The 10 historical instances from gate_events are the measured population. Pattern: agents that embed test-result tables, category breakdowns, or progression summaries inside `## *Verification*` sections.

---

## R-2 — Fix Shape A: The Quoted-❌

### The defect

`gates.py:689` — `if "❌" in stripped:` fires on ANY occurrence of the ❌ character anywhere in the row, including inside backtick-delimited inline code spans. A QA report quoting `\`❌ worktree teardown failed:\`` as evidence-of-verification (the row's status cell is ✅) is flagged as a failure.

### Proposed scoping rule: strip backtick spans before ❌ scan

**Mechanics:** Before the `"❌" in stripped` check at `gates.py:689`, strip paired backtick spans from the row text:
```python
import re
scan_text = re.sub(r'`[^`]+`', '', stripped)
```
Then check `if "❌" in scan_text:` instead of `if "❌" in stripped:`.

**Unpaired-backtick degenerate case:** If the row contains an odd number of backticks (unpaired), the regex `\`[^`]+\`` consumes from the first to the second backtick, leaving the third (and any content after it) unstripped. This **fails safe**: the unstripped remainder still gets scanned for ❌. A row like `| check \`foo | ❌ bar\` |` (unpaired) would NOT strip the ❌ — the scan proceeds on the full row. No false-negative risk from malformed backticks.

### False-negative cost (explicit)

An agent could hide a real ❌ inside backticks: `| test_foo | \`❌\` | evidence |`. This would bypass the (c) scanner.

**Weighed trade:** The (c) gate is one layer. The Planner's Rule 22(b) independent verification is a second, stronger layer — the Planner re-reads the QA report and checks substance. Hiding-in-backticks is detectable adversarial conduct (the Planner would see `\`❌\`` in a status cell and flag it), not the honest-mistake class this gate exists for. The gate catches formatting errors and overlooked failures; it was never designed to resist deliberate obfuscation. A ❌ inside backticks in a status cell is visually prominent and humanly readable — the Planner layer catches it.

**Conclusion:** The false-negative cost is acceptable. The backtick-stripping scoping rule is RECOMMENDED.

### Alternative shape: require non-positive status cell before ❌ fires

Instead of stripping backticks, only fire the ❌ check when the row does NOT pass `_is_positive_status_row(line)`.

**Cost:** A row with ❌ in a non-status cell AND ✅ in the status cell would pass. This is the exact C4 case — so it solves the incident. But: a row with `| test | ❌ | ✅ decoration |` (❌ in status cell, trailing ✅ in a description cell) would ALSO pass because `_is_positive_status_row` returns True on any cell containing ✅. Constructing this case requires a ✅ emoji somewhere in the row alongside a ❌ in the status cell — unlikely in practice but architecturally unsound (the ❌ should override the ✅, not the reverse).

**Conclusion:** The backtick-stripping shape is cleaner — it scopes to the actual problem (quoted literals) without creating the ❌-overridden-by-stray-✅ hole. The alternative is NOT recommended.

---

## R-3 — Fix Shape B: The Mixed-Table Info Row

### The defect

`gates.py:697–703` — rows without a positive-status token are deferred; deferred rows are flushed as failures when `current_table_has_positive_row` is True. A deliberate status-less row (info marker, out-of-scope note, data row) in a table that also has ✅ rows fires as "missing status."

### Option (i): Accept `N/A` as a neutral token

Extend the token discipline with a `_is_na_status_row` helper. Cells containing bounded `N/A` (case-insensitive, cell equality) mark the row as explicitly exempt — it neither fires as missing-status nor counts as a positive row.

**Implementation:** Add `NA_STATUS_TOKENS = ["N/A", "n/a", "NA"]` and a `_is_na_status_row(line)` function parallel to `_is_positive_status_row`. In the (c) loop, after the ❌ check and the positive-status check, check N/A before deferring:
```python
elif _is_na_status_row(line):
    pass  # explicit neutral — skip
else:
    current_table_failures.append(...)
```

**Decoration-incentive cost:** Agents learn to stamp `N/A` on rows they don't want checked. If an agent puts `N/A` on a row that SHOULD have been verified, the gate stays silent. This is the earn-the-gate inversion: the fix teaches agents to decorate rather than verify.

However: the N/A token is bounded (cell equality, not substring) and semantically clear. An agent writing `| G8 | ~/.claude memory | N/A |` is making an explicit assertion ("this row is not checkable") that the Planner's Rule 22(b) review can audit. The token is honest: it says "not applicable", not "passed". The Planner sees N/A and decides whether the row genuinely shouldn't be checked.

### Option (ii): Out-of-band row marker

The plan or report carries a marker (e.g., `<!-- no-gate -->` HTML comment, or a frontmatter list of exempt row indices). The (c) scanner reads the marker and skips those rows.

**Cost:** Adds complexity to both plan authoring and the scanner. Markers can get out of sync with row indices if the table is edited. No existing precedent in the codebase.

**Not recommended.** Excessive mechanism for the problem size.

### Option (iii): Keep firing; mandate status cells everywhere

Plans must include status cells on every row in verification-section tables, including info rows. The 527 QA report (plan `executable-527`, `knowledge/qa/evidence/no-receipt-admission-hold/qa-report.md`) demonstrates this workaround: the G-row handling in its verification tables gives every row a ✅ or explicit status. There are no status-less rows in its `## G1–G3 Coverage Verification Table` or `## Extended Verification Table`.

**Cost:** Works for tables where every row is checkable. Fails for gap tables that must carry deliberate out-of-scope rows (the C5 incident) — forcing a ✅ on an unchecked row is a lie, and forcing "PASS" on an info row is meaningless. The 527 workaround succeeds because its tables are pure verification tables — no mixed data.

**Measured rate:** 10 C5-class FPs in 945 events = 1.06% of total. Overrides cost 2 CEO acts. The 10 unoverridden ones indicate the system is already absorbing the cost (auto-close or subsumption by other failures).

### Recommendation: Option (i) — N/A token

**Tiebreaker reasoning (the earn-the-gate lesson):**
- Option (iii) — mandating status everywhere — teaches agents to write fake ✅ on unchecked rows. This is worse than Option (i) because a fake ✅ is indistinguishable from a real one.
- Option (i) — N/A — teaches agents to write an honest neutral marker. The Planner can audit N/A usage. An N/A on a row that should be ✅ or ❌ is a detectable omission, not a counterfeit pass.
- Option (ii) is over-engineered for 1% FP rate.
- The 10 unoverridden C5-class FPs show the problem is recurring but low-frequency. N/A brings it to zero without creating perverse incentives.

---

## R-4 — Regression Fence

### Existing test inventory

**File:** `tests/test_gates.py` (2323 lines, as read)

**Tests on `_gate_rule_22_verification`:** 15 tests
| # | Test name | Line | Coverage |
|---|---|---|---|
| 1 | test_rule_22_non_qa_all_deposits_present | 1462 | (a) non-QA pass |
| 2 | test_rule_22_non_qa_deposit_missing | 1473 | (a) non-QA deposit missing |
| 3 | test_rule_22_qa_all_pass | 1484 | (c) all-✅ table passes |
| 4 | test_rule_22_qa_fail_row | 1502 | (c) real ❌ row fires |
| 5 | test_rule_22_qa_missing_status | 1522 | (c) missing status fires |
| 6 | test_rule_22_qa_hedging_keyword | 1543 | (d) hedging keyword fires |
| 7 | test_rule_22_qa_both_fail_and_hedging | 1563 | (c) + (d) both fire |
| 8 | test_rule_22_qa_report_missing | 1584 | (a) QA report missing |
| 9 | test_rule_22_verification_c_skips_non_verification_section_tables | 1690 | Section scoping |
| 10 | test_rule_22_verification_c_accepts_text_pass_status | 1716 | PASS token |
| 11 | test_rule_22_verification_c_flags_genuine_missing_status_in_verification_table | 1740 | Missing status positive control |
| 12 | test_rule_22_c_enumerative_table_inside_verification_section_passes | 1838 | No-positive-row table skipped |
| 13 | test_rule_22_d_pending_in_description_cell_passes | 1861 | Cell-scoped hedging |
| 14 | test_rule_22_c_genuine_missing_status_still_fires | 1898 | Counter-test |
| 15 | test_rule_22_d_pending_in_status_cell_still_fires | 1919 | Counter-test |

**Tests on `_is_positive_status_row`:** 0 direct tests; tested indirectly through tests 3, 9, 10, 11, 12 above.

### (d) hedging check interaction

The (d) check at `gates.py:707–723` iterates the same rows and calls `_is_positive_status_row(line)` before scanning for hedging keywords.

**Does backtick-stripping belong in (d) too?** Census: zero (d)-class failures in the entire gate_events history. The (d) check has never fired on quoted hedge-words (e.g., `\`pending\`` in a code span). This makes sense: HEDGING_KEYWORDS are English words ("pending", "assumed", "estimated") that appear in natural prose, not in code-span quotations of technical identifiers. Backtick-stripping for (d) would be prophylactic, not measured-need-driven. **Recommendation: do NOT add backtick-stripping to (d).** If a future incident arises, the fix shape is identical and can be added then.

### New test list for fix shape A (quoted-❌ stripping)

| # | Test name | What it covers |
|---|---|---|
| A1 | test_rule_22_c_quoted_failure_marker_in_passing_row_passes | C4 reproduction: `| check | \`❌ teardown\` count | ✅ |` — the backtick-quoted ❌ is stripped, ✅ status passes |
| A2 | test_rule_22_c_unquoted_failure_marker_still_fires | Positive control: `| check | ❌ | evidence |` — bare ❌ still fires |
| A3 | test_rule_22_c_failure_marker_in_unpaired_backtick_still_fires | Adversarial arm: `| check \`foo | ❌ bar |` — unpaired backtick, ❌ not inside a complete span, still fires (fail-safe) |
| A4 | test_rule_22_c_failure_marker_hidden_in_backticks_bypasses | Documented false-negative: `| check | \`❌\` | evidence |` — ❌ hidden inside backticks, scanner does NOT fire. Confirms the known trade-off. |
| A5 | test_rule_22_c_multiple_backtick_spans_stripped | Multiple spans: `| \`foo ❌\` bar \`baz ❌\` | ✅ |` — both spans stripped, ✅ passes |

### New test list for fix shape B (N/A token)

| # | Test name | What it covers |
|---|---|---|
| B1 | test_rule_22_c_na_status_row_skipped_in_mixed_table | C5 reproduction: table with ✅ rows and one `| G8 | info | N/A |` row — N/A row does not fire |
| B2 | test_rule_22_c_na_row_does_not_count_as_positive | N/A-only table (no ✅ rows) — N/A rows do not make `current_table_has_positive_row` True; deferred rows are discarded |
| B3 | test_rule_22_c_na_case_insensitive | `| check | n/a |` — lowercase accepted |
| B4 | test_rule_22_c_na_not_substring_match | `| check | N/A but should be checked |` — cell is not bounded N/A, fires as missing-status |
| B5 | test_rule_22_c_genuine_missing_status_still_fires_with_na_present | Counter-test: table has ✅ rows and N/A rows AND one row with no status — the no-status row still fires |

---

## R-5 — Executable Shape

**Size:** Small single-DEV+QA bellows plan.

### Rule 27 Gap Table

| Site | File | Hunk description |
|---|---|---|
| S1 | `gates.py` | Line ~689: add `re.sub(r'\`[^\`]+\`', '', stripped)` before ❌ scan |
| S2 | `gates.py` | Lines ~695–702: add `_is_na_status_row(line)` check branch between positive-status and defer |
| S3 | `gates.py` | Lines ~58–65 area: add `NA_STATUS_TOKENS` constant and `_is_na_status_row` helper function |
| S4 | `tests/test_gates.py` | Add 10 new tests (A1–A5, B1–B5) per R-4 |
| S5 | No other files expected | The fix is confined to gates.py and its test file. No changes to bellows.py, runner.py, depositor.py, or any other module. |

### Step structure

- **Step 1 (DEV):** Implement S1–S4. Run full test suite to confirm zero regressions on the existing 15 rule_22 tests + pass on the 10 new tests.
- **Step 2 (QA):** Verify all 10 new tests pass, existing 15 tests unaffected, full suite green. Verify the C4 and C5 reproduction rows would now pass under the new code.

---

## R-6 — Open Questions

1. **R-3 option choice:** Option (i) (N/A token) is recommended with reasoning. If the CEO prefers Option (iii) (mandate status everywhere, accepting the 527 workaround pattern), the only cost is continued overrides on gap-table plans — measured at 1.06% of total events, 2 CEO acts to date. The recommendation stands unless the CEO rules otherwise.

2. **R-2 alternative (status-cell-first ❌):** The census shows zero adversarial-❌ incidents in 945 events. The hidden-in-backticks false-negative is theoretical, not measured. The backtick-stripping shape is recommended over the status-cell-first alternative because backtick-stripping scopes to the actual parser defect without creating the stray-✅-overrides-❌ hole. No fork requiring a ruling — the backtick-stripping shape is strictly dominant.

3. **No ruling needed on (d) backtick-stripping:** Zero (d)-class FPs in history. Prophylactic addition is deferred.

---

## C-pin Re-derivation Summary

| Pin | Planner value (2026-08-25) | Re-derived value | Delta |
|---|---|---|---|
| C1 | `gates.py:689 if "❌" in stripped:` fires anywhere | **Confirmed.** `gates.py:689` — the `re.sub` approach is the scoping fix. | None |
| C2 | `gates.py:697–703` defer/flush on `current_table_has_positive_row` | **Confirmed.** Lines 697–703 are the defer path; the N/A branch inserts at ~695–696. | None |
| C3 | Shape 6C section-scoping + `_is_positive_status_row` | **Confirmed.** `gates.py:643–651` comment, `gates.py:665` section check, `gates.py:77–90` helper. `POSITIVE_STATUS_TOKENS` at line 65. | None |
| C4 | Plan 523 step 2 — quoted-❌ in ✅ row | **Confirmed.** gate_events id=6495, overridden=1, override_ref cites "benign rule_22(c) parser false-positive". Evidence row at qa-report.md line 89. | None |
| C5 | Plan 524 step 2 — status-less G8 info row | **Confirmed.** gate_events id=6509, overridden=1, override_ref cites "benign rule_22(c) parser class". Evidence row at qa-report.md line 75. | None |
| C6 | Override catalog: both via `clear_plan.py --override-gate` | **Confirmed.** Both rows have `overridden=1` in gate_events. These are the only 2 overridden rule_22_verification events in the entire history. | None |

---

## Post-condition Checklist

- [x] R-1 census covers every recorded rule_22_verification failure: 55/55 classified, 0 unclassified
- [x] C1–C6 re-derived with measurement shown (table above)
- [x] Fix shape A carries false-negative cost in its own text (R-2, "False-negative cost" section)
- [x] Fix shape B carries decoration-incentive cost in its own text (R-3, Option (i) subsection)
- [x] Gap table enumerates executable sites (R-5, S1–S5)
