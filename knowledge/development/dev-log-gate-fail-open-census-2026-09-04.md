# Dev Log — Gate Fail-Open Census — 2026-09-04

**Plan:** diagnostic-100034 | **Step:** 1 (census, read-only) | **Date:** 2026-09-04

## Inventory method

Each module uses a DIFFERENT identifier convention — deriving from a shared pattern was the
walk-2 probe error (45 vs 0 advisory count discrepancy). The per-module conventions used:

| Module | Convention | Tool extraction |
|---|---|---|
| `gates.py` | `^def _gate_` function names | regex on source |
| `plan_lint.py` | `(x)` labels in results.append/print | regex; f-string labels (b, d, v) required manual inclusion |
| `depositor.py` | `self._hold(path, "literal")` strings | regex on source; dynamic f-string reasons listed separately |
| `cycle_check.py` | `return "VERDICT"` literals | regex; BAR_MET returned via variable, not literal — noted |
| `wrap_check.py` | `[n/name]` tags in fails.append lines | regex on fails.append lines only |
| `walk_register_lint.py` | `^STATUS_\w+` constants | regex on source |

Tool: `tools/gate_failopen_census.py` — mechanical extraction only, no dynamic analysis.

## Checks whose behaviour disagreed with description (or with each other)

1. **`_gate_is_qa_step` (thread 116)** — docstring says "Handle YAML list case"; the list IS handled
   for YAML frontmatter format (`[2]` → Python list). But for bold-markdown format `**qa_steps:** [2]`,
   the value is string `"[2]"` and `int("[2]")` raises ValueError. Fallback keyword detection fires.
   The docstring comment `# Handle YAML list case (e.g., [2, 4])` implies both formats work — they don't.
   The YAML comment is correct for YAML format; the bold-markdown case is the gap.

2. **`cycle_check._manifest_validation_keys` (P3)** — function docstring: "Returns None when: no stanza
   present, no validation field, value is falsy, `<declare>`, or N/A." Behaviour matches docstring.
   But the *caller* (`run_check`) uses this None as a SKIP signal: "if stored is not None ... else
   BAR_MET unchanged." Docstring describes the function correctly; the skip consequence in the caller
   is not stated anywhere — the fail-open is in the call site, not the function.

3. **`plan_lint (c)` `qa_steps: none`** — the check string says "QA plans contain the Rule 20 banner
   pair." It intends to catch plans that declare QA steps but forget banners. When `qa_steps: none`
   (a valid declaration meaning "no QA steps"), the string `"none"` is truthy and the check fires
   as if QA steps were declared. The check and the field's intended semantics disagree.

4. **`diagnostics-100032.md` P3 mismatch** — P3 stated diagnostic-100032 would show
   `{cycle_check, fold_check, plan_lint}` (3 keys) — measured 3 keys confirmed. But P7 stated 13
   compliant plans (4 keys); measured 3. The count discrepancy is growth: newer plans that were
   compliant at P7 time may have been there, or the count was an overcount. Re-derived: 3.

## P4 correction

Diagnostic pin P4 said "plan_lint on 100031 emits **5** `(f)` WARNs and **exit 0, zero FAILs**."
Measured: 10 (f) WARNs (all 10 Cycle Manifest stanza fields are missing or empty from 100031 —
each fires its own (f) WARN). The finding stands: exit 0, zero FAILs. The count was an undercount.

## Census tool limitations noted

- `plan_lint` checks (b), (d), (v) use f-strings in their label strings and are missed by the
  `results.append(("FAIL"/"PASS", "(x) label", ...))` regex. These were added manually to the count.
- `cycle_check.py` `BAR_MET` verdict is assigned via `verdict = "..." else "BAR_MET"` and returned
  as `return verdict, 0`. The literal-return regex (`return "..."`) does not find it. Noted in output.
- `walk_register_lint.py` statuses classify as "blocking" when non-silent in cycle_check's WARN
  arm — but `walk_register_lint` itself is standalone and warn-only. The classification reflects
  downstream impact, not the tool's own behavior.

## Membership test applications (Q3 boundary cases)

**Applied to all 4 founding instances:**

| Thread | Criterion (i) | Criterion (ii) | Criterion (iii) | Verdict |
|---|---|---|---|---|
| 114 (wrap_check [4/memory]) | PASS on non-git memory dir | ✓ | ✗ — demonstrated with `class: banana` (constructed); non-git dir not exercised here | UNVERIFIED |
| 116 (_gate_is_qa_step `[2]`) | ✓ falls back to keyword | ✓ QA gates don't fire | ✓ executive-312.md, -313.md (confirmed `**qa_steps:** [2]`) | CONFIRMED |
| 118 (plan_lint (c) `none`) | ✗ check FAILS (false positive), not PASSES | — | ✓ 4 Done plans | NEAR-MISS (false positive, not fail-open) |
| cycle_check manifest check | ✓ `stored=None` → SKIP | ✓ should require manifest | ✓ halted-100031 (exercised) | CONFIRMED |

**The membership test immediately disqualified founding instance 118 from the fail-open class.**
Thread 118 is a false positive (FAIL when PASS is correct), not a fail-open (PASS when FAIL is correct).
It remains a genuine defect in plan_lint (c) but is not a member of the fail-open census.

## Coverage

- Verified by exercise: cycle_check manifest gate (P3 exercise), _gate_is_qa_step corpus lookup
- Static analysis only: all other gates.py checks, depositor holds, wrap_check steps, walk_register_lint statuses
- Could not assess without environment modification: wrap_check [4/memory] non-git memory mechanism (thread 114)
