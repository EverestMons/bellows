# Dev Log — plan_lint §4 Drafting-Cycle self-check (warn-first)

**Plan:** 271 | **Step:** 1 (DEV) | **Date:** 2026-07-24

## Implementation

### Task A — the check

Added a new `(f) Drafting Cycle self-check` block to `scripts/plan_lint.py` (after the existing qa_steps cross-check, before results printing), using the same non-blocking WARN mechanism as the test-scope and qa_steps warnings: `print("WARN: ...")` — never touches the `results` list, so `plan_lint` always exits 0.

**Behaviour, per DRAFTING_CYCLE.md §4:**

| Condition | Action |
|---|---|
| No `cycle_tier` in header | `WARN: no cycle_tier declared (DRAFTING_CYCLE.md §1/§3)` |
| `cycle_tier` not T0/T1/T2 | `WARN: cycle_tier {value!r} not recognized (expected T0, T1, or T2)` |
| T1/T2: no `## Drafting Cycle` block | `WARN: {tier} plan has no '## Drafting Cycle' block` |
| T1/T2: missing any of 5 lenses | `WARN: Drafting Cycle block missing lens(es): {names}` — matched case-insensitively: `weak spots`, `destruction`, `vulnerabilit`, `integration`, `acid` |
| T2: no cold-panel line | `WARN: T2 plan missing cold-panel line` — matches `cold panel` or `cold-panel` |
| No `**Closing:**` line in block | `WARN: Drafting Cycle block has no **Closing:** line` |
| Closing indicates fold, no dry | `WARN: Drafting Cycle closing indicates fold as last event, not a dry lens pass` |
| T0 | Only tier declaration checked; no block/lens/closing checks |

**WARN-mechanism confirmation:** every WARN is emitted via `print()`, same as the existing test-scope / qa_steps WARNs. The `results` list (which controls exit code) is never touched. `plan_lint` exits 0 on all WARN cases.

**Degenerate/malformed handling:** if the `## Drafting Cycle` heading exists but the block is empty, the check degrades to WARNs for missing lenses/closing — no crash. Reading is already UTF-8 (existing `read_text(encoding="utf-8")` at line 40).

### Task B — existing test protection (destruction lens)

**One test edit required.** `test_lint_single_step_diagnostic_no_e_fail` (line 348) asserted `"WARN" not in result.stdout` — too broad. Its fixture plan (a single-step diagnostic with no `cycle_tier`) now emits the new `no cycle_tier declared` WARN, breaking the assertion.

**Fix:** replaced `assert "WARN" not in result.stdout` with `assert "consider using uppercase" not in result.stdout`. This preserves the original intent (no step-heading-case WARN) while allowing the new cycle_tier WARN. The test's docstring — "(e-c) Single-step diagnostic (no qa_steps, no step headings) → NO (e) FAIL, NO case WARN, exit 0" — remains accurate: "NO case WARN" refers to the step-heading case warning, which the updated assertion still checks.

No other existing tests broke. All fixture plans without `cycle_tier` now emit the new WARN, but no other assertion checked for `"WARN" not in result.stdout` broadly.

### Task C — tests that observe the effect (vulnerabilities lens)

Six new tests added to `tests/test_plan_lint.py`:

| Test | Fixture | Asserts |
|---|---|---|
| `test_lint_cycle_compliant_t2_no_warn` | Real T2 block from executable-270.md (with Cold panel line added — 270 predates the requirement) | Exit 0, NO drafting-cycle WARN |
| `test_lint_cycle_tierless_warns` | Real header from executable-265.md (no cycle_tier) | Exit 0, `no cycle_tier declared` WARN fires |
| `test_lint_cycle_t1_missing_acid_warns` | Synthetic T1 plan missing ACID lens | Exit 0, WARN names ACID |
| `test_lint_cycle_t0_no_block_warn` | Synthetic T0 plan, tier declaration only | Exit 0, NO block/lens/closing WARN |
| `test_lint_cycle_fold_closing_warns` | Synthetic T1 plan with fold closing | Exit 0, WARN about fold (not dry lens pass) |
| *(all above)* | *(all above)* | `plan_lint` exits 0 on every case |

### Targeted test run

```
python3 -m pytest tests/ -k "plan_lint or lint" --tb=short -q 2>&1 | cat
```

```
.....................                                                    [100%]
21 passed, 792 deselected, 1 warning in 1.34s
```

All 21 tests pass (15 existing + 6 new).

### Live run — real plans

**Real T2 plan (executable-270.md):**
```
WARN: T2 plan missing cold-panel line in Drafting Cycle block (DRAFTING_CYCLE.md §3)
PASS: (a) header — parsed
PASS: (a) dispatch_mode — bellows
PASS: (a) pause_for_verdict — always
PASS: (b) step 1 deposits — 1 path(s)
PASS: (b) step 2 deposits — 1 path(s)
PASS: (b) step 3 deposits — 1 path(s)
PASS: (c) QA banner pair — both strings present
exit code: 0
```

Plan 270 correctly gets the cold-panel WARN — it predates the Cold panel requirement (it was the plan that created DRAFTING_CYCLE.md). Exit 0.

**Tier-less plan (executable-265.md):**
```
WARN: no cycle_tier declared (DRAFTING_CYCLE.md §1/§3)
PASS: (a) header — parsed
PASS: (a) dispatch_mode — bellows
PASS: (a) pause_for_verdict — always
PASS: (b) step 1 deposits — 1 path(s)
PASS: (b) step 2 deposits — 1 path(s)
PASS: (c) QA banner pair — both strings present
PASS: (d) step 1 scope — 8 file(s), 0 prefix(es)
PASS: (d) step 2 scope — 1 file(s), 1 prefix(es)
exit code: 0
```

The `no cycle_tier declared` WARN fires. Exit 0.

---

### Ledger Updates

#### Prompt Feedback

- The plan specified "Use the real block in executable-270.md (a genuine T2 Cycle Log) as a fixture input" for the compliant-T2 test, expecting "NO cycle-cycle WARN." However, plan 270 has no `**Cold panel (T2):**` line (it was the first plan with a Cycle Log, predating the Cold panel requirement). The test fixture uses plan 270's real block with the Cold panel line added to make it compliant. The live-run output above shows the WARN correctly firing on the unmodified plan 270.

---
## Output Receipt
**Agent:** Bellows Developer
**Step:** 1
**Status:** Complete

### What Was Done
Added the DRAFTING_CYCLE.md §4 self-check to `plan_lint.py` as a warn-first gate. The check verifies cycle_tier declaration, Drafting Cycle block presence (T1+), five required lenses, cold-panel line (T2), and dry closing — all as non-blocking WARNs. Updated one existing test assertion (Task B) and added six new tests (Task C), all passing.

### Files Deposited
- `knowledge/development/plan-lint-drafting-gate-dev-2026-07-24.md` — this dev log

### Files Created or Modified (Code)
- `scripts/plan_lint.py` — added (f) Drafting Cycle self-check block (warn-first, ~30 lines)
- `tests/test_plan_lint.py` — updated one assertion in `test_lint_single_step_diagnostic_no_e_fail`; added six new tests for the §4 check

### Decisions Made
- Used `plan_text` (not `clean_text`) for Drafting Cycle block search — the heading won't appear in fenced code blocks in real plans, and warn-first posture makes a false match harmless
- Closing-line fold check uses lenient logic: warns only if "fold" is present AND "dry" is absent — per plan instruction to "keep it lenient" and "do NOT over-parse"
- For the compliant-T2 test fixture, used plan 270's real Drafting Cycle block with the Cold panel line added (270 predates the requirement)
- Narrowed the broken test assertion from `"WARN" not in result.stdout` to `"consider using uppercase" not in result.stdout` — preserves the original intent (no step-heading-case WARN) without being broken by the new cycle_tier WARN

### Flags for CEO
- None

### Flags for Next Step
- Plan 270 (the real T2 plan used for live testing) does not have a `**Cold panel (T2):**` line, so it triggers the cold-panel WARN. This is correct behavior — the check is working as designed, reminding future plans to include the line.
