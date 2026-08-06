# Dev Log — Three Drafting-Cycle Checks in plan_lint (Plan 302, Step 1)

**Date:** 2026-08-06
**Plan:** executable-302 (three mechanical drafting-cycle checks)
**Files edited:** `scripts/plan_lint.py`, `tests/test_plan_lint.py`

---

## Warn-first Confirmation (Task A0)

Before editing, confirmed every `(f)` WARN in `plan_lint.py` is a bare `print(...)` that never appends to `results` and never sets `all_passed = False`. The return at line 227 is `0 if all_passed else 1`. All three new checks follow the same pattern — WARN-only, never blocking.

`git status --porcelain -- scripts/plan_lint.py tests/test_plan_lint.py` was clean (no dirty files).

---

## Before/After per Check

### (g) Ledger ordering

**Before:** No check. Out-of-order constraint entries (e.g., C23 inserted above C22) caught only by manual sweep.

**After (lines 224–232):** Regex `\*\*C(\d+)\*\*\s*—` extracts constraint integers from `dc_block`. If two or more entries exist and the sequence is not strictly ascending, WARNs naming the first offending pair. Zero entries → skip silently (not a failure, stated in comment).

### (h) Stale closing disclaimer

**Before:** No check. A `**Closing:**` line asserting "no lens has read this artifact" after lenses had run caught only by manual sweep.

**After (lines 234–248):** Contradiction check using the same `lens_line_re` that `(f)` builds. If ANY lens line contains a walk indicator (`[wa]\d+`) AND the `**Closing:**` line contains "no lens has read", WARNs. Neither condition alone fires — this is a conjunction, not a keyword check.

### (i) Halt-routing plan-id coverage

**Before:** No check. A fold adding a new plan-id reference that the halt-routing never learned about caught only by ACID, one phase late.

**After (lines 250–265):** Collects backtick-quoted three-digit plan ids (`\`(\d{3})\``) from the plan body before the `## Drafting Cycle` block. Searches the same pre-DC text for a halt-routing line (`halt[\s-]*rout`, case-insensitive). If plan ids exist and halt-routing is present, WARNs for each id in the body but absent from the halt-routing line. If plan ids exist but no halt-routing line, WARNs that it is absent. If no plan ids exist, skips silently. Scoped to the mechanical backtick-quoted class only — prose references and non-id three-digit numbers are outside scope.

---

## Existing Test Protection (Task D)

42 existing tests ran before the edit and all 42 passed. After the edit, all 42 still pass — no fixture edits needed. None of the existing fixtures contain:
- `**C\d+** —` ledger entries (so (g) skips silently)
- "no lens has read" in a Closing line (so (h) doesn't fire)
- Backtick-quoted three-digit plan ids in pre-DC text (so (i) doesn't fire)

---

## New Tests (Task E)

11 new tests added, all asserting exit 0 (WARN-only):

### (g) Ledger ordering
- **(g-a)** Ascending ledger (C16–C25, from diagnostic-301) → NO ledger WARN ✓
- **(g-b)** Out-of-order ledger (C3 before C2) → WARN naming C3/C2 ✓
- **(g-c)** No ledger entries (COMPLIANT_T2_PLAN) → no false WARN ✓

### (h) Stale closing disclaimer
- **(h-a)** Lens lines with walk results + Closing claims no lens has read → WARN ✓
- **(h-b)** Closing claims unread, but lenses [pending] → no WARN (neither alone) ✓
- **(h-c)** Lens results recorded + normal closing → no WARN (neither alone) ✓

### (i) Halt-routing plan-id coverage
- **(i-a)** Plan id `302` in body, absent from halt-routing → WARN naming `302` ✓
- **(i-b)** Full coverage (all ids in halt-routing) → no WARN ✓
- **(i-c)** Plan ids in body, no halt-routing line at all → WARN ✓
- **(i-d)** No plan ids in body → no WARN even without halt-routing ✓

### Degenerate
- **(ghi-degen)** Empty DC block → no crash, no false WARN from any of (g)/(h)/(i) ✓

---

## Targeted Test Output

```
$ python3 -m pytest tests/ -k "plan_lint or lint" --tb=short -q 2>&1 | cat
.....................................................                    [100%]
53 passed, 797 deselected, 1 warning in 2.61s
```

---

## Live Run Output

### Compliant plan (diagnostic-301, real Done plan)

```
$ python3 scripts/plan_lint.py /Users/marklehn/Developer/GitHub/governance/knowledge/decisions/Done/diagnostic-301.md
WARN: T2 plan missing cold-panel line in Drafting Cycle block (DRAFTING_CYCLE.md §3)
WARN: Drafting Cycle closing indicates fold as last event, not a dry lens pass (DRAFTING_CYCLE.md §2)
WARN: plan id `273` in questions region but absent from halt-routing
WARN: plan id `274` in questions region but absent from halt-routing
WARN: plan id `279` in questions region but absent from halt-routing
WARN: plan id `280` in questions region but absent from halt-routing
WARN: plan id `281` in questions region but absent from halt-routing
WARN: plan id `283` in questions region but absent from halt-routing
WARN: plan id `284` in questions region but absent from halt-routing
WARN: plan id `289` in questions region but absent from halt-routing
PASS: (a) header — parsed
PASS: (a) dispatch_mode — bellows
PASS: (a) pause_for_verdict — always
EXIT=0
```

The two `(f)` WARNs are earned and documented in the plan's own Closing line. The `(i)` WARNs fire because the diagnostic references many plan ids in its body but has no halt-routing line. All WARN-only; exit 0.

### Tripping fixture (exercises all three new checks)

```
$ python3 scripts/plan_lint.py /tmp/tripping_fixture.md
WARN: Drafting Cycle ledger out of order: C3 before C2
WARN: Drafting Cycle Closing claims no lens has read the artifact, but lens results are recorded
WARN: plan id `302` in questions region but absent from halt-routing
PASS: (a) header — parsed
PASS: (a) dispatch_mode — bellows
PASS: (a) pause_for_verdict — always
EXIT=0
```

All three new checks fire correctly. Exit 0 confirmed — none sets `all_passed = False` or appends to `results`.

---

### Ledger Updates

#### Prompt Feedback

None — the plan was executed as written with no ambiguity requiring feedback.
