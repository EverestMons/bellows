# Dev Log — Three Drafting-Cycle Checks in plan_lint (Plans 302 + 303, Step 1)

**Date:** 2026-08-06
**Plans:** executable-302 (initial implementation), executable-303 (false-positive fix)
**Files edited:** `scripts/plan_lint.py`, `tests/test_plan_lint.py`

---

## A0-PRE Verification (Plan 303)

Commit `cc5f0e8` from plan 302 is present in `scripts/plan_lint.py` history. All three checks verified present and WARN-only:

- **(g)** Lines 224–232: bare `print(f"WARN: ...")`. Does NOT touch `results` or `all_passed`.
- **(h)** Lines 234–248: bare `print("WARN: ...")`. Does NOT touch `results` or `all_passed`.
- **(i)** Lines 250–267: bare `print(f"WARN: ...")` / `print("WARN: ...")`. Does NOT touch `results` or `all_passed`.

Mechanism confirmed: `grep` of each check block for `results.append`, `results =`, and `all_passed` returns empty.

---

## A0-FIX: Check (i) False Positive on Executables (Plan 303)

### The defect

Running `plan_lint` against plan 303 (an executable) produced:
```
WARN: plan id `277` in questions region but absent from halt-routing
```

Plan 303 references plan `277` in its machinery description ("cloned from `277`"), but as an executable it has no questions region and no halt-routing concept. Three defects in one firing:

1. **It applies to plan classes that have no halt routing.** Halt-routing is diagnostic-specific; executables have steps, not questions.
2. **Prose matches the directive regex.** The matched line is a table row describing the defect class, not a routing directive.
3. **First match wins** (`break`), so a description early in the file shadows a real routing line later.

### The fix (defect 1 — the one that fires on every executable)

Gated check (i) on `re.search(r'^## Questions\b', pre_dc_text, re.MULTILINE)`. When the plan has no `## Questions` heading, check (i) skips silently. Comment explains why: halt-routing is a diagnostic concept; executables have steps, not questions.

**Before:**
```python
plan_id_pat = re.compile(r'`(\d{3})`')
pre_dc_text = plan_text[:dc_match.start()]
pre_dc_ids = set(plan_id_pat.findall(pre_dc_text))
# ... (always runs)
```

**After:**
```python
pre_dc_text = plan_text[:dc_match.start()]
has_questions_region = bool(re.search(r'^## Questions\b', pre_dc_text, re.MULTILINE))
if has_questions_region:
    plan_id_pat = re.compile(r'`(\d{3})`')
    pre_dc_ids = set(plan_id_pat.findall(pre_dc_text))
    # ... (only runs for diagnostics with a questions region)
```

### Defects 2 and 3 — reported, not fixed

**Defect 2 (prose matches the directive regex):** The halt-routing search `re.search(r'halt[\s-]*rout', ln, re.IGNORECASE)` matches any line containing "halt-rout" or "halt rout", including prose descriptions of the defect class (e.g., table rows in the Drafting Cycle section or plan body). A tighter regex or a structural anchor (e.g., matching only bold-prefix lines like `**Halt routing:**`) would reduce false matches but risks missing legitimate variant phrasings. **Recommendation:** tighten to require a leading `**` or start-of-line bold pattern in a future plan.

**Defect 3 (first match wins / `break`):** The `break` on the first halt-routing line match means a prose description appearing before the actual routing directive shadows it. If defect 2 were fixed (prose no longer matches), this becomes moot. Otherwise, removing the `break` and using the LAST match, or filtering for structural markers, would address it. **Recommendation:** address jointly with defect 2.

### Fixture edits (preserving intent)

Three existing test fixtures for (i) were diagnostics without a `## Questions` heading. The gate added by A0-FIX caused them to skip silently, failing the tests. Fixed by adding `## Questions` sections to each fixture, making them internally consistent diagnostics:

- **test_lint_halt_routing_missing_id_warns (i-a):** Added `## Questions` heading with `Q1. Check whether \`245\` and \`302\` are affected.` Moved plan-id text from bare body into the questions section. Halt-routing line stays in the pre-questions body. **Intent preserved:** test still verifies that `302` absent from halt-routing fires the WARN.
- **test_lint_halt_routing_full_coverage_no_warn (i-b):** Same structural change. **Intent preserved:** test still verifies full coverage produces no WARN.
- **test_lint_no_halt_routing_line_warns (i-c):** Added `## Questions` with plan ids but no halt-routing line. **Intent preserved:** test still verifies missing halt-routing line fires the WARN.

No other fixtures needed edits. test_lint_no_plan_ids_no_halt_routing_no_warn (i-d) correctly has no plan ids and needs no questions region.

### Regression test added

**test_lint_executable_with_plan_ids_no_i_warn (i-e):** An executable fixture with backtick-quoted plan ids (`277`, `140`) in its body but no `## Questions` heading. Asserts check (i) does NOT fire. Directly exercises the false-positive scenario from plan 303.

---

## Warn-first Confirmation (Task A0, Plan 302)

Before editing (plan 302), confirmed every `(f)` WARN in `plan_lint.py` is a bare `print(...)` that never appends to `results` and never sets `all_passed = False`. The return at line 272 is `0 if all_passed else 1`. All three new checks follow the same pattern — WARN-only, never blocking.

---

## Before/After per Check (Plan 302, verified at Plan 303)

### (g) Ledger ordering

**Before:** No check. Out-of-order constraint entries (e.g., C23 inserted above C22) caught only by manual sweep.

**After (lines 224–232):** Regex `\*\*C(\d+)\*\*\s*—` extracts constraint integers from `dc_block`. If two or more entries exist and the sequence is not strictly ascending, WARNs naming the first offending pair. Zero entries: skip silently (not a failure, stated in comment).

### (h) Stale closing disclaimer

**Before:** No check. A `**Closing:**` line asserting "no lens has read this artifact" after lenses had run caught only by manual sweep.

**After (lines 234–248):** Contradiction check using the same `lens_line_re` that `(f)` builds. If ANY lens line contains a walk indicator (`[wa]\d+`) AND the `**Closing:**` line contains "no lens has read", WARNs. Neither condition alone fires.

### (i) Halt-routing plan-id coverage (with A0-FIX gate)

**Before:** No check. A fold adding a new plan-id reference that the halt-routing never learned about caught only by ACID, one phase late.

**After (lines 250–270):** Gated on `## Questions` heading (A0-FIX). If present: collects backtick-quoted three-digit plan ids from the pre-DC text. Searches the same region for a halt-routing line. WARNs for each id present in body but absent from halt-routing. WARNs if plan ids exist but no halt-routing line. Skips silently if no plan ids or no questions region.

---

## Existing Test Protection (Task D)

53 existing tests ran before the A0-FIX edit and all passed. After the edit, 2 initially failed (i-a, i-c) because their fixtures lacked `## Questions` headings. Fixtures updated to be internally consistent diagnostics (see "Fixture edits" above). After fixture edits, all 53 original tests pass. Intent preserved in every case.

---

## New Tests (Plan 303 total: 12 tests, Plans 302 + 303)

### (g) Ledger ordering
- **(g-a)** Ascending ledger (C16–C25, from diagnostic-301) → NO ledger WARN
- **(g-b)** Out-of-order ledger (C3 before C2) → WARN naming C3/C2
- **(g-c)** No ledger entries (COMPLIANT_T2_PLAN) → no false WARN

### (h) Stale closing disclaimer
- **(h-a)** Lens lines with walk results + Closing claims no lens has read → WARN
- **(h-b)** Closing claims unread, but lenses [pending] → no WARN (neither alone)
- **(h-c)** Lens results recorded + normal closing → no WARN (neither alone)

### (i) Halt-routing plan-id coverage
- **(i-a)** Plan id `302` in body, absent from halt-routing → WARN naming `302`
- **(i-b)** Full coverage (all ids in halt-routing) → no WARN
- **(i-c)** Plan ids in body, no halt-routing line → WARN
- **(i-d)** No plan ids in body → no WARN even without halt-routing
- **(i-e)** Executable with plan ids but no questions region → NO (i) WARN (regression test for A0-FIX)

### Degenerate
- **(ghi-degen)** Empty DC block → no crash, no false WARN from any of (g)/(h)/(i)

---

## Targeted Test Output (Plan 303, after A0-FIX)

```
$ python3 -m pytest tests/ -k "plan_lint or lint" --tb=short -q 2>&1 | cat
......................................................                   [100%]
54 passed, 797 deselected, 1 warning in 2.10s
```

---

## Live Run Output (Plan 303, after A0-FIX)

### Plan 303 itself (the false-positive regression target)

```
$ python3 scripts/plan_lint.py /Users/marklehn/Developer/GitHub/bellows/.bellows-cache/executable-303.md.pristine
WARN: T2 plan missing cold-panel line in Drafting Cycle block (DRAFTING_CYCLE.md §3)
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

No `(i)` WARN fires. The `(f)` cold-panel WARN is earned (Closing says "NOT REACHED").

### Compliant plan (diagnostic-139, real Done plan)

```
$ python3 scripts/plan_lint.py /Users/marklehn/Developer/GitHub/bellows/knowledge/decisions/Done/diagnostic-139.md
WARN: no cycle_tier declared (DRAFTING_CYCLE.md §1/§3)
PASS: (a) header — parsed
PASS: (a) dispatch_mode — bellows
PASS: (a) pause_for_verdict — always
PASS: (b) step 1 deposits — 1 path(s)
PASS: (d) step 1 scope — 1 file(s), 0 prefix(es)
EXIT=0
```

### Tripping fixture (exercises all three new checks)

```
$ python3 scripts/plan_lint.py /tmp/tripping-fixture.md
WARN: Drafting Cycle ledger out of order: C3 before C2
WARN: Drafting Cycle Closing claims no lens has read the artifact, but lens results are recorded
WARN: no halt-routing line found
PASS: (a) header — parsed
PASS: (a) dispatch_mode — bellows
PASS: (a) pause_for_verdict — always
EXIT=0
```

All three new checks fire correctly. Exit 0 confirmed — none sets `all_passed = False` or appends to `results`.

### WARN-only mechanism verification

```
$ python3 -c "..." (extracted check blocks (g)/(h)/(i) and grepped for results/all_passed)
(g): results_touched=False, all_passed_touched=False
(h): results_touched=False, all_passed_touched=False
(i): results_touched=False, all_passed_touched=False
```

---

### Ledger Updates

#### Prompt Feedback

None — the plan was executed as written with no ambiguity requiring feedback.
