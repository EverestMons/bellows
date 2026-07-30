# Dev Log — plan_lint §4 four-defect fix (Plan 286, Step 1)

**Date:** 2026-07-30
**Plan:** 286 (proposal 198, code half — Gate 2 Plan B)

## 1. BELLOWS_TREE and Harness Resolution

- `BELLOWS_TREE=/Users/marklehn/Developer/GitHub/bellows/.bellows-worktrees/286`
- Harness `LINT_SCRIPT` resolves to: `/Users/marklehn/Developer/GitHub/bellows/.bellows-worktrees/286/scripts/plan_lint.py` — confirmed inside `$BELLOWS_TREE`.

## 2. Task A0(ii) — Idempotency + Cleanliness

- **Tag lookup:** `git log --grep='\[286\]' --oneline` — no output (no prior `[286]` commits). CLEAR.
- **Content check:** `grep -Fc 'vulnerabilit\w*' scripts/plan_lint.py` printed `0` (exit status 1 — expected, since `grep -c` exits 1 when count is zero). CLEAR — fixes not yet applied.
- **Cleanliness:** `git status --porcelain -- scripts/plan_lint.py tests/test_plan_lint.py` — empty. CLEAN.

## 3. Task A0(iii) — Warn-first Precondition

RAW output from a blocking-clean fixture with ACID `w1 1 folded`:
```
WARN: Drafting Cycle closing indicates fold as last event, not a dry lens pass (DRAFTING_CYCLE.md §2)
PASS: (a) header — parsed
PASS: (a) dispatch_mode — bellows
PASS: (a) pause_for_verdict — always
PASS: (b) step 1 deposits — 1 path(s)
PASS: (d) step 1 scope — 1 file(s), 0 prefix(es)
exit_status=0
```
WARN fires AND exit 0. Source reading confirmed: all `(f)` WARNs are bare `print(...)`, none appends to `results`, none sets `all_passed = False`, return is `0 if all_passed else 1`.

## 4. The Four Edits

### (a) Vulnerabilities regex — `scripts/plan_lint.py:197`
**Before:** `r'^-\s*(?:cold[\s-]+)?(?:weak[\s-]*spots|destruction|vulnerabilit|integration|acid)\b'`
**After:** `r'^-\s*(?:cold[\s-]+)?(?:weak[\s-]*spots|destruction|vulnerabilit\w*|integration|acid)\b'`

Grep-confirmed: no other `vulnerabilit\b` occurrence remains in the lens-line pattern. The required-lens check at `:184` still uses bare `r'vulnerabilit'` — unchanged and correct.

### (b) Closing status parse — `scripts/plan_lint.py:209-211`
**Before:**
```python
has_fold = 'fold' in ll_lower
has_dry = 'dry' in ll_lower
```
**After:**
```python
has_fold = 'fold' in ll_lower
cleaned = re.sub(r'\b(?:not|no|never)\s+dry\b', '', ll_lower)
has_dry = bool(re.search(r'\bdry\b', cleaned))
```

**Rationale:** Negation-aware whole-line rule per 277's CB1. A `dry` occurrence immediately preceded by `not`/`no`/`never` is removed before checking. Uses `\bdry\b` word boundary (not whitespace-split) to handle punctuation-attached tokens (`dry.`, `dry**`).

**Three declared bounds:**
- (i) `dry` matches as a WORD token (`\bdry\b`); the fold side is LEFT EXACTLY AS-IS — the plain substring `'fold' in ll_lower`. No word-tokenisation, no stemming on the fold side.
- (ii) The negation window is the IMMEDIATELY preceding word only — `not dry` is negated, `not entirely dry` reads as dry.
- (iii) UTF-8 text handled — real lens lines contain `→`, `·`, and em-dashes.

### (c) Closing-presence reachability — `scripts/plan_lint.py:214-222`
**Before:** Missing-`**Closing:**` check inside the `else` branch (unreachable when lens lines exist).
**After:** Missing-`**Closing:**` check OUTSIDE the if/else, using the already-computed `closing_pos` variable. Runs unconditionally. The closing-prose STATUS check stays inside the `else` — only the PRESENCE check became unconditional.

### (d) Cold-panel structural anchoring — `scripts/plan_lint.py:193`
**Before:** `re.search(r'cold[\s-]panel', dc_block, re.IGNORECASE)`
**After:** `re.search(r'(?:^\*\*cold[\s-]+panel|^-\s*cold[\s-])', dc_block, re.IGNORECASE | re.MULTILINE)`

Accepts two structural forms: `**Cold panel …` line and `- Cold <lens> …` cold lens-result line. Prose mentions in Tier or Walks lines no longer satisfy it.

## 5. Task A — Regex Probe (RAW)

```
=== BEFORE (old regex) ===
'- Vulnerabilities:    w1 dry.' -> NO MATCH
'- ACID:               w1 dry.' -> MATCH
'- Weak spots:         w1 dry.' -> MATCH

=== AFTER (new regex) ===
'- Vulnerabilities:    w1 dry.' -> MATCH
'- ACID:               w1 dry.' -> MATCH
'- Weak spots:         w1 dry.' -> MATCH
```

## 6. Task B — Parser RAW Run Against Real-Log Fixtures

All four DRY-closing fixtures (271, 277, 278, 275) produce NO fold-WARN under the negation-aware parser. Plan 284 (fold-closing) correctly WARNs under both pre-fix and post-fix linters.

Specifically for `\bdry\b` vs `.split()`: plan 275's ACID line contains `→ dry. All 11 folds cohere` — the `dry` carries a trailing period. `\bdry\b` correctly matches; a naive `.split()` would yield token `dry.` and miss it.

## 7. Embedded Done Plans

The following Done-plan Drafting Cycle blocks are embedded as test fixtures:
- 271 (REAL_LOG_271 — existing)
- 274 (REAL_LOG_274 — existing)
- 275 (REAL_LOG_275 — existing, reused with own fixture file and liveness proof)
- diag-276 (REAL_LOG_DIAG_276 — existing)
- 277 (REAL_LOG_277 — new)
- 278 (REAL_LOG_278 — new)
- 284 (REAL_LOG_284 — new, positive control)

## 8. Per-Plan Blast Radius

### (d) cold-panel — all four plans have structural cold-panel lines:
| Plan | Has `**Cold panel` or `- Cold <lens>` | New WARN? |
|------|---------------------------------------|-----------|
| 271  | `**Cold panel (T2):**` line           | No        |
| 277  | `**Cold panel (T2):**` line           | No        |
| 278  | `**Cold panel (T2):**` line           | No        |
| 284  | `**Cold panel (T2):**` + `- Cold weak-spots:` | No |

**Measured radius: ZERO.**

### (c) missing-Closing — all four plans have `**Closing:**` lines:
| Plan | Has `**Closing:**` | New WARN? |
|------|--------------------|-----------|
| 271  | Yes                | No        |
| 277  | Yes                | No        |
| 278  | Yes                | No        |
| 284  | Yes                | No        |

**Measured radius: ZERO.**

### (b) re-derived blast radius against the actual parser:
Ran the negation-aware parser (post-fix) and the pre-fix linter against:
- All 7 embedded fixtures: **0 WARN-outcome changes** (284 WARNs under both — correct)
- All 429 Done/ plans in-tree: **0 fold-WARN outcome changes**

**Re-derived radius: ZERO.**

## 9. Task E — Existing Test Results

All 34 existing `plan_lint` tests pass with all four fixes applied. No fixture edits needed.

## 10. Task F — Pre-fix / Post-fix Captures

Pre-fix baseline: `HEAD=059d85c51cf97f9a49833a3197cf3e7371f869e0`
Extracted to: temp file via `git show HEAD:scripts/plan_lint.py` (10826 bytes, non-empty confirmed).

### Positive control (284):
- PRE-FIX: `WARN: Drafting Cycle closing indicates fold as last event, not a dry lens pass` — PRESENT
- POST-FIX: same WARN — PRESENT
- Confirms the pre-fix linter is alive.

### Control (a) — Vulnerabilities LAST, folded:
- PRE-FIX: fold-WARN **ABSENT** (exit 0)
- POST-FIX: `WARN: Drafting Cycle closing indicates fold as last event, not a dry lens pass` — **PRESENT** (exit 0)

### Control (b) — ACID `w1 NOT dry; folded elsewhere`:
- PRE-FIX: fold-WARN **ABSENT** (exit 0)
- POST-FIX: `WARN: Drafting Cycle closing indicates fold as last event, not a dry lens pass` — **PRESENT** (exit 0)

### Control (c) — all lenses dry, no Closing line:
- PRE-FIX: missing-Closing WARN **ABSENT** (exit 0)
- POST-FIX: `WARN: Drafting Cycle block has no **Closing:** line` — **PRESENT** (exit 0)

### Control (d) — T2, cold-panel only in Tier-line prose:
- PRE-FIX: cold-panel WARN **ABSENT** (exit 0)
- POST-FIX: `WARN: T2 plan missing cold-panel line in Drafting Cycle block` — **PRESENT** (exit 0)

## 11. Targeted Test Output

```
42 passed, 792 deselected, 1 warning in 1.61s
```

All 42 tests pass (34 existing + 8 new). The 8 new tests are:
- `test_lint_cycle_real_log_277_no_fold_warn` (f-r)
- `test_lint_cycle_real_log_278_no_fold_warn` (f-s)
- `test_lint_cycle_real_log_284_fold_warn` (f-t)
- `test_lint_control_a_vuln_last_folded` (f-u)
- `test_lint_control_b_not_dry` (f-v)
- `test_lint_control_c_no_closing` (f-w)
- `test_lint_control_d_cold_panel_prose` (f-x)
- `test_lint_cycle_status_mutual_exclusivity` (f-y)

## Output Receipt

### Files Created or Modified (Code)
| File | Change |
|------|--------|
| `scripts/plan_lint.py` | Four fixes: (a) `vulnerabilit\w*` in lens_line_re, (b) negation-aware dry detection, (c) unconditional Closing-presence check, (d) line-anchored cold-panel pattern |
| `tests/test_plan_lint.py` | 8 new tests (f-r through f-y) + 3 new real-log constants (REAL_LOG_277, REAL_LOG_278, REAL_LOG_284) + isolation assertion added to f-h |
| `knowledge/development/plan-lint-198-four-defects-dev-2026-07-30.md` | This dev-log |

### Ledger Updates

#### Prompt Feedback

- The plan's three-numbering-system warning (CEO Context) was valuable — gap-map rows, dev-log items, and QA rows are indeed distinct.
- The fixture-isolation requirement (plan 280's f-h discipline) was correctly extended to include the fifth marker (`no **Closing:** line`) now that fix (c) makes the missing-Closing WARN reachable. This was stated in the plan and was not an oversight.
- The DESIGN FORK on (b) was correctly resolved by the negation-aware whole-line rule. The plan's correction about plan 275 being the real counterexample to the `;`-split design was verified by execution.
- The wrapper-vs-content distinction for real-log fixtures was important: the DC block content is verbatim, but the header wrapper must be constructed to avoid triggering blocking checks (e) and (c) that are irrelevant to the `(f)` checks being tested. The existing fixtures (271, 274, 275, diag-276) already followed this pattern.
