# QA Report — plan_lint §4 four-defect fix (Plan 286, Step 2)

**Date:** 2026-07-30
**Plan:** 286 (proposal 198, code half — Gate 2 Plan B)
**BELLOWS_TREE:** `/Users/marklehn/Developer/GitHub/bellows/.bellows-worktrees/286`

## Deliverable Verification (Rule 8 / Rule 17)

Output Receipt in dev-log confirmed Complete — all 11 items present.

| Deliverable | Expected | Status | Evidence |
|-------------|----------|--------|----------|
| `scripts/plan_lint.py` | Four fix regions: (a) `vulnerabilit\w*`, (b) negation-aware dry, (c) unconditional Closing-presence, (d) line-anchored cold-panel | verified | Lines 193, 197, 210-211, 221-222 confirmed |
| `tests/test_plan_lint.py` | 8 new test functions (f-r through f-y) + 3 new real-log constants + isolation assertion update to f-h | verified | `grep -c` returns 8 for all new test names; REAL_LOG_277, REAL_LOG_278, REAL_LOG_284 present |
| `knowledge/development/plan-lint-198-four-defects-dev-2026-07-30.md` | Dev-log present and committed | verified | File exists, committed in `a59200b` |

## Drift Check — RULE_20_SELF_CHECK_BLOCK.md

- **Authoring-time hash (CEO Context):** `c90ffb4bea0063e994f4b85e56df80c1653de59cb0124a1bbd982df9d52f8711`
- **Recomputed hash:** `c90ffb4bea0063e994f4b85e56df80c1653de59cb0124a1bbd982df9d52f8711`
- **Verdict:** MATCH — no drift.

## Verification Table

| Row | Claim | Status | Evidence |
|-----|-------|--------|----------|
| 1 | Warn-first preserved | verified | All `(f)` checks are bare `print(...)` (grep confirmed: lines 175, 190, 194, 213, 219, 222 — none appends to `results` or sets `all_passed = False`). Tier-less plan: `WARN: cycle_tier 'T-NONE' not recognized` + exit 0. T1 missing Integration: `WARN: Drafting Cycle block missing lens(es): Integration` + exit 0. |
| 2 | (a) fixed — Vulnerabilities regex | verified | `lens_line_re` at :197 contains `vulnerabilit\w*`. Required-lens check at :184 is UNCHANGED — bare `r'vulnerabilit'`. Dev-log regex probe shows `- Vulnerabilities: w1 dry.` goes NO MATCH (pre-fix) to MATCH (post-fix). |
| 3a | (b) NOT dry control WARNs | verified | `test_lint_control_b_not_dry` passes — `- ACID: w1 NOT dry; folded elsewhere.` triggers fold-WARN. |
| 3b | (b) DRY fixtures 271, 277, 278 do NOT WARN | verified | `test_lint_cycle_real_log_277_no_fold_warn` and `test_lint_cycle_real_log_278_no_fold_warn` pass. 271 is verified via existing REAL_LOG_271 fixture (no fold-WARN). 275 also passes (existing REAL_LOG_275). |
| 3c | (b) 284 positive control DOES WARN | verified | `test_lint_cycle_real_log_284_fold_warn` passes — 284's fold-closing line correctly triggers fold-WARN. |
| 3d | (b) re-derived blast radius present | verified | Dev-log section 8 reports: 7 embedded fixtures — 0 WARN-outcome changes; 429 Done/ plans in-tree — 0 fold-WARN outcome changes. Re-derived radius: ZERO. |
| 4 | (c) fixed, status checks mutually exclusive | verified | Code: Closing-PRESENCE check (line 221-222) is OUTSIDE the if/else. Closing-prose STATUS check (lines 215-219) stays INSIDE the `else`. `test_lint_control_c_no_closing` passes — structured lens lines, all dry, no Closing line triggers `WARN: Drafting Cycle block has no **Closing:** line`. `test_lint_cycle_status_mutual_exclusivity` passes — dry last lens line + fold Closing prose produces NO fold-WARN. Confirmed by live fixture: `/tmp/qa_row4_mutual_excl.md` with dry ACID + fold-Closing prose exits 0 with no fold-WARN. |
| 5 | (d) fixed, blast radius measured | verified | `test_lint_control_d_cold_panel_prose` passes — T2 block with cold-panel only in Tier-line prose triggers WARN. Structural forms (`**Cold panel` and `- Cold <lens>`) do not WARN. Plan 280's f-h test (`test_lint_cycle_t2_missing_cold_panel_warns`) still passes. Dev-log section 8 reports per-plan blast radius for (d) cold-panel AND (c) missing-Closing across 271, 277, 278, 284 — all ZERO. Matches Planner's stated bound. |
| 6 | No crash on degenerate input | verified | Empty DC block: WARNs for missing lenses and no Closing line, exit 0, no crash. |
| 7 | Existing behaviour intact | verified | 42 targeted plan_lint tests pass (34 existing + 8 new). Dev-log reports: "No fixture edits needed" (matching §Q5(b) prediction). |
| 8 | Compliant real plan clean | verified | `plan_lint` on `$BELLOWS_TREE/knowledge/decisions/Done/executable-277.md`: all PASS, no Drafting Cycle WARN, exit 0. |
| 9a | Commit identified and in this tree | verified | `git log --all --grep='\[286\]' --oneline -- scripts/plan_lint.py tests/test_plan_lint.py` returns exactly one row: `a59200b`. `git merge-base --is-ancestor a59200b HEAD` exits 0 — reachable from HEAD. |
| 9b | Nothing landed after it | verified | `git log --oneline a59200b..HEAD -- scripts/plan_lint.py tests/test_plan_lint.py` is EMPTY — no intervening commits on code files during the verdict window. |
| 9c | Scope limited, daemon modules unchanged | verified | `git show --stat a59200b` touches ONLY: `scripts/plan_lint.py` (14 +/- 6), `tests/test_plan_lint.py` (241 +), `knowledge/development/plan-lint-198-four-defects-dev-2026-07-30.md` (191 +). `git diff a59200b -- bellows.py gates.py runner.py` is EMPTY — all three daemon modules UNCHANGED. No doc edit, no DB change. |
| 10 | Rule 20 block drift check | verified | Authoring-time hash: `c90ffb4bea0063e994f4b85e56df80c1653de59cb0124a1bbd982df9d52f8711`. Recomputed: `c90ffb4bea0063e994f4b85e56df80c1653de59cb0124a1bbd982df9d52f8711`. MATCH — no drift. |
| 11 | Full suite | verified | 834 passed, 1 warning in 20.38s. Baseline: 825 (plan-lint-189-190, 2026-07-25). Delta: +9 (8 new from this plan + 1 from plan 280's f-h). No new failures. |

## Rule 20 Self-Check

```
============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
Evidence folder: /Users/marklehn/Developer/GitHub/bellows/.bellows-worktrees/286/knowledge/qa/evidence/plan-lint-198-four-defects-2026-07-30/
Files verified: 2
```

## Evidence Files

- `knowledge/qa/evidence/plan-lint-198-four-defects-2026-07-30/targeted-tests.txt` — 42 passed, 792 deselected, 1 warning
- `knowledge/qa/evidence/plan-lint-198-four-defects-2026-07-30/full-suite.txt` — 834 passed, 1 warning

### Ledger Updates

#### Project Status
- plan_lint §4's four defects fixed — Vulnerabilities lens-line selection, negation-aware closing status, reachable missing-Closing check, structurally-anchored cold-panel check; warn-first preserved; Gate 2 Plan B complete, Plan A unblocked.

#### Prompt Feedback
- The plan's three-numbering-system warning (CEO Context) was respected throughout QA — gap-map rows, dev-log items, and QA verification rows are distinct.
- Row 9's three-sub-claim structure (9a/9b/9c) was valuable — each tests a different failure mode (lost commit vs foreign interference vs scope violation) and requires different escalation.
- The drift-check row (10) requiring both literal hashes prevents a vacuous "match" assertion — the check is reproducible from the report alone.
- The mutual exclusivity test for row 4 required a custom fixture with dry lens lines AND fold-mentioning Closing prose — the plan's instruction to test this specifically was essential, since an unchecked unconditional status path would have silently re-created CB1's false-WARN class.
