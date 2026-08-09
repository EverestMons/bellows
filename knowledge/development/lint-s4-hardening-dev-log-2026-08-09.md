# Dev Log: lint-s4-hardening-2026-08-09

**Plan:** executable-332
**Step:** 1 (DEV)
**Date:** 2026-08-09

---

## PRE_EDIT_BLOB

`8288606eefe5a93720aa40017073aa4a52ca2f51`

---

## Task A0(0) — Already-Landed Probe

Probed `scripts/plan_lint.py` for M2 content-check and M3 bounded-gap negation:
- Line 196: cold-panel check is existence-only (no content requirement) → M2 NOT landed
- Line 213: negation strip is `r'\b(?:not|no|never)\s+dry\b'` (adjacent only, no gap) → M3 NOT landed

Fresh run confirmed.

## Task A0 — Pre-Edit State

`git -C /Users/marklehn/Developer/GitHub/bellows status --porcelain -- scripts/plan_lint.py tests/test_plan_lint.py gates.py` → EMPTY. Clean state.

## Task A0(b) — Pre-Edit Blob Pin

`git -C /Users/marklehn/Developer/GitHub/bellows hash-object scripts/plan_lint.py` → `8288606eefe5a93720aa40017073aa4a52ca2f51`

## Task A1 — Warn-First Confirmation

All (f)-family WARNs are bare `print(...)` — none touch `results` or `all_passed`. Return at line 477 is `0 if all_passed else 1`. Confirmed.

---

## M2 — Cold-Panel Content Check (Row 27)

### Before (lines 195-197)

```python
                if tier_num == 2:
                    if not re.search(r'(?:^\*\*cold[\s-]+panel|^-\s*cold[\s-])', dc_block, re.IGNORECASE | re.MULTILINE):
                        print("WARN: T2 plan missing cold-panel line in Drafting Cycle block (DRAFTING_CYCLE.md §3)")
```

### After (lines 195-212)

```python
                if tier_num == 2:
                    cold_bold_re = re.compile(r'^\*\*cold[\s-]+panel', re.IGNORECASE)
                    cold_dash_re = re.compile(r'^-\s*cold[\s-]', re.IGNORECASE)
                    has_cold_content = False
                    for line in dc_block.splitlines():
                        stripped = line.strip()
                        if cold_bold_re.match(stripped):
                            remainder = cold_bold_re.sub('', stripped)
                            remainder = re.sub(r'\([^)]*\)', '', remainder)
                            remainder = remainder.replace(':', '').replace('*', '').strip()
                            if remainder:
                                has_cold_content = True
                                break
                        elif cold_dash_re.match(stripped):
                            remainder = re.sub(r'^-\s*cold[\s-]+\S+', '', stripped, flags=re.IGNORECASE)
                            remainder = re.sub(r'\([^)]*\)', '', remainder)
                            remainder = remainder.replace(':', '').strip()
                            if remainder:
                                has_cold_content = True
                                break
                    if not has_cold_content:
                        print("WARN: T2 plan missing cold-panel line in Drafting Cycle block (DRAFTING_CYCLE.md §3)")
```

---

## M3 — Bounded-Gap Negation (Row 28)

### Before (line 213)

```python
                    cleaned = re.sub(r'\b(?:not|no|never)\s+dry\b', '', ll_lower)
```

### After (line 232)

```python
                    cleaned = re.sub(r'\b(?:not|no|never)\s+(?:\w+\s+)?dry\b', '', ll_lower)
```

---

## Fold-Side Fence (C3) — Both Sites Byte-Identical

### Primary (line 231)

Before: `has_fold = 'fold' in ll_lower`
After: `has_fold = 'fold' in ll_lower`
**Byte-identical.**

### Legacy Fallback (line 240)

Before: `if 'fold' in closing_text and 'dry' not in closing_text:`
After: `if 'fold' in closing_text and 'dry' not in closing_text:`
**Byte-identical.**

### WARN Message Text

`grep -c -F -e "dry lens pass" scripts/plan_lint.py` = **2** (the two print sites, unchanged).

Both WARN messages at lines 235 and 241:
`"WARN: Drafting Cycle closing indicates fold as last event, not a dry lens pass (DRAFTING_CYCLE.md §2)"`
**Byte-identical before and after.**

### Mechanical Fold-Side Gate

`git -C /Users/marklehn/Developer/GitHub/bellows diff -U0 scripts/plan_lint.py | grep -F -e "'fold' in"` → **no output** (nothing changed).

---

## Task D — Existing Test Protection

Baseline (before edit): **97 passed**
After edit: **110 passed** (97 pre-existing + 13 new)

No pre-existing test changed behaviour. No fixture was edited.

---

## Task E — New Tests

### M2 Tests (8 tests)

1. `test_lint_m2_hollow_bold_warns` — hollow `**Cold panel (T2):**` → WARN
2. `test_lint_m2_substantive_bold_no_warn` — substantive `**Cold panel (T2):** run; 3 seats, 8 findings.` → no WARN
3. `test_lint_m2_hollow_dash_warns` — hollow `- Cold weak-spots:` → WARN
4. `test_lint_m2_substantive_dash_no_warn` — substantive `- Cold weak-spots: 9 findings, 2 HIGH.` → no WARN
5. `test_lint_m2_dominant_real_corpus_form_no_warn` — `- Cold panel (§2.6), seat 1 (Lens 1 cold): 11 findings` → no WARN
6. `test_lint_m2_hollow_dash_panel_warns` — hollow `- Cold panel (§2.6):` → WARN
7. `test_lint_m2_colonless_no_warn` — colonless `**Cold panel materially changed the draft (CB1 HIGH) → seat 1 findings**` → no WARN
8. `test_lint_m2_accepted_residue_no_warn` — hollow bold + substantive dash lines → no WARN

### M3 Tests (5 tests)

9. `test_lint_m3_not_yet_dry_warns` — `not yet dry` on fold-bearing last lens line → WARN
10. `test_lint_m3_no_longer_dry_warns` — `no longer dry` on fold-bearing last lens line → WARN
11. `test_lint_m3_never_quite_dry_warns` — `never quite dry` on fold-bearing last lens line → WARN
12. `test_lint_m3_legitimate_dry_at_distance_no_warn` — `w1 2 folded, w2 no further findings so dry` → NO WARN (bound control, N>2)
13. `test_lint_m3_adjacent_not_dry_warns` — `not dry` adjacent on fold-bearing last lens line → WARN (286 unchanged)

---

## Targeted Test Results (After Edit)

```
........................................................................ [ 65%]
......................................                                   [100%]
110 passed, 818 deselected, 1 warning in 4.39s
```

---

## Live Run Output

### Real Done/ plan (executable-303.md)

```
WARN: T2 plan missing cold-panel line in Drafting Cycle block (DRAFTING_CYCLE.md §3)
(o1) INFO: candidates=11 excluded=7 fired=0
(p) WARN: C5 has no backtick-quoted command or check: token
PASS: (a) header — parsed
PASS: (a) dispatch_mode — bellows
PASS: (a) pause_for_verdict — always
PASS: (b) step 1 deposits — 3 path(s)
PASS: (b) step 2 deposits — 4 path(s)
PASS: (c) QA banner pair — both strings present
PASS: (d) step 1 scope — 3 file(s), 0 prefix(es)
PASS: (d) step 2 scope — 4 file(s), 0 prefix(es)
EXIT=0
```

### Tripping Fixture: M2 hollow bold (at /var/folders/vf/8nw0z7hj1m34w6z48l5dp54w0000gn/T/tmp.6lwqJqr3nC/m2_hollow_bold.md)

```
WARN: T2 plan missing cold-panel line in Drafting Cycle block (DRAFTING_CYCLE.md §3)
PASS: (a) header — parsed
PASS: (a) dispatch_mode — bellows
PASS: (a) pause_for_verdict — always
EXIT=0
```

### Tripping Fixture: M2 hollow dash (at /var/folders/vf/8nw0z7hj1m34w6z48l5dp54w0000gn/T/tmp.6lwqJqr3nC/m2_hollow_dash.md)

```
WARN: T2 plan missing cold-panel line in Drafting Cycle block (DRAFTING_CYCLE.md §3)
PASS: (a) header — parsed
PASS: (a) dispatch_mode — bellows
PASS: (a) pause_for_verdict — always
EXIT=0
```

### Non-Tripping Fixture: M2 substantive bold (at /var/folders/vf/8nw0z7hj1m34w6z48l5dp54w0000gn/T/tmp.6lwqJqr3nC/m2_substantive_bold.md)

```
PASS: (a) header — parsed
PASS: (a) dispatch_mode — bellows
PASS: (a) pause_for_verdict — always
EXIT=0
```

### Tripping Fixture: M3 not yet dry (at /var/folders/vf/8nw0z7hj1m34w6z48l5dp54w0000gn/T/tmp.6lwqJqr3nC/m3_not_yet_dry.md)

```
WARN: Drafting Cycle closing indicates fold as last event, not a dry lens pass (DRAFTING_CYCLE.md §2)
PASS: (a) header — parsed
PASS: (a) dispatch_mode — bellows
PASS: (a) pause_for_verdict — always
EXIT=0
```

### Non-Tripping Fixture: M3 legitimate dry at distance (at /var/folders/vf/8nw0z7hj1m34w6z48l5dp54w0000gn/T/tmp.6lwqJqr3nC/m3_legit_dry.md)

```
PASS: (a) header — parsed
PASS: (a) dispatch_mode — bellows
PASS: (a) pause_for_verdict — always
EXIT=0
```

### Tripping Fixture: M3 adjacent not dry (at /var/folders/vf/8nw0z7hj1m34w6z48l5dp54w0000gn/T/tmp.6lwqJqr3nC/m3_adjacent_not_dry.md)

```
WARN: Drafting Cycle closing indicates fold as last event, not a dry lens pass (DRAFTING_CYCLE.md §2)
PASS: (a) header — parsed
PASS: (a) dispatch_mode — bellows
PASS: (a) pause_for_verdict — always
EXIT=0
```

---

## Fixture Source Text

### M2 Hollow Bold (`m2_hollow_bold.md`)

```
# Test Plan
**Date:** 2026-08-09 | **Dispatch Mode:** bellows | **pause_for_verdict:** always | **cycle_tier:** T2

## Drafting Cycle
**Tier:** T2 — triggers fired: T-6 (governance surface).
**Walks:** 1.
- Weak spots:         w1 dry.
- Destruction:        w1 dry.
- Vulnerabilities:    w1 dry.
- Integration-record: w1 dry.
- ACID:               w1 dry.
**Cold panel (T2):**
**Closing:** walk 1 dry; last event = lens pass; deposited once.
```

### M2 Hollow Dash (`m2_hollow_dash.md`)

```
# Test Plan
**Date:** 2026-08-09 | **Dispatch Mode:** bellows | **pause_for_verdict:** always | **cycle_tier:** T2

## Drafting Cycle
**Tier:** T2 — triggers fired: T-6 (governance surface).
**Walks:** 1.
- Weak spots:         w1 dry.
- Destruction:        w1 dry.
- Vulnerabilities:    w1 dry.
- Integration-record: w1 dry.
- ACID:               w1 dry.
- Cold weak-spots:
**Closing:** walk 1 dry; last event = lens pass; deposited once.
```

### M2 Substantive Bold (`m2_substantive_bold.md`)

```
# Test Plan
**Date:** 2026-08-09 | **Dispatch Mode:** bellows | **pause_for_verdict:** always | **cycle_tier:** T2

## Drafting Cycle
**Tier:** T2 — triggers fired: T-6 (governance surface).
**Walks:** 1.
- Weak spots:         w1 dry.
- Destruction:        w1 dry.
- Vulnerabilities:    w1 dry.
- Integration-record: w1 dry.
- ACID:               w1 dry.
**Cold panel (T2):** run; 3 seats, 8 findings.
**Closing:** walk 1 dry; last event = lens pass; deposited once.
```

### M3 Not Yet Dry (`m3_not_yet_dry.md`)

```
# Test Plan
**Date:** 2026-08-09 | **Dispatch Mode:** bellows | **pause_for_verdict:** always | **cycle_tier:** T1

## Drafting Cycle
**Tier:** T1 — triggers fired: T-8 (novel).
**Walks:** 1.
- Weak spots:         w1 dry.
- Destruction:        w1 dry.
- Vulnerabilities:    w1 dry.
- Integration-record: w1 dry.
- ACID:               a1 4 folded; not yet dry.
**Closing:** walk 1 complete; deposited once.
```

### M3 Legitimate Dry at Distance (`m3_legit_dry.md`)

```
# Test Plan
**Date:** 2026-08-09 | **Dispatch Mode:** bellows | **pause_for_verdict:** always | **cycle_tier:** T1

## Drafting Cycle
**Tier:** T1 — triggers fired: T-8 (novel).
**Walks:** 2.
- Weak spots:         w1 1 folded; w2 dry.
- Destruction:        w1 dry; w2 dry.
- Vulnerabilities:    w1 dry; w2 dry.
- Integration-record: w1 dry; w2 dry.
- ACID:               w1 2 folded, w2 no further findings so dry.
**Closing:** walk 2 dry; last event = lens pass; deposited once.
```

### M3 Adjacent Not Dry (`m3_adjacent_not_dry.md`)

```
# Test Plan
**Date:** 2026-08-09 | **Dispatch Mode:** bellows | **pause_for_verdict:** always | **cycle_tier:** T1

## Drafting Cycle
**Tier:** T1 — triggers fired: T-8 (novel).
**Walks:** 1.
- Weak spots:         w1 dry.
- Destruction:        w1 dry.
- Vulnerabilities:    w1 dry.
- Integration-record: w1 dry.
- ACID:               w1 1 folded; not dry.
**Closing:** walk 1 complete; deposited once.
```

---

### Ledger Updates

#### Forward Register

- DRAFTING_CYCLE.md §4 describes the T2 panel check as line-anchored-only and enumerates the negation strip as `not dry` / `no dry` / `never dry`; M2 and M3 changed both mechanics, so §4's descriptions are now understatements and owe a governance-root edit (deferred per §6's pair-or-defer-and-say).
- Row 25 remains OPEN and unchanged in scope; this plan attempted its check, measured it, and cut it. 1379 of 1390 corpus plans already emit at least 1 warning (99.2%) and exactly one declares, so the check would have fired approximately 1378 times against check (i)'s eleven; the newest-20 bellows rate is 15/20. Any successor must state its expected firing population as a MEASURED number before authoring.

#### Prompt Feedback

None.
