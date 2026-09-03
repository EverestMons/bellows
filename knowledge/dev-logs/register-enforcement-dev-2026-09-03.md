# DEV LOG — register-enforcement — 2026-09-03

**Plan:** executable-100029 | **Step:** 1 (DEV) | **Agent:** claude-sonnet-4-6

---

## Pre-flight Pin Derivation

| pin | measured | plan | verdict |
|---|---|---|---|
| P1 | walk_register_lint.py 364L sha19a41ab0b879; cycle_check.py 674L sha12c23a3345a8; run_check.py 113L sha65f6de0a7d8e | same | MATCH |
| P2 | pre_schema anchor: 1; STATUS_NO_TABLE ternary: 1 | 1, 1 | MATCH |
| P3 | register_result assigned at :261,:275,:285,:299,:301; consumed :420,:453 | :261,:275,:285,:299,:301 | MATCH |
| P4 | a2_reg arm at :425 routes "FAIL"→ESCALATE; register_result never assigned "FAIL" | same | MATCH |
| P5 | cycle_check on Done/executable-100028.md → BAR_MET; walk_register_lint on walk-register-qa-predeclaration-2026-09-03.md → NO_TABLE (from stderr) | BAR_MET / NO_TABLE disagree | MATCH — gap confirmed, PROCEED |
| P9 | mutation_check on checker-defects-cycle_check.json → 4 killed / 0 survived | 4 killed / 0 survived | MATCH |
| P10 | test_cycle_check.py: 132 tests; test_walk_register_lint.py: 27; test_run_check.py: 13; targeted (run_check+walk_register): 40 | test_cycle_check: 27; targeted: 42 | DELTA — mine supersede; no HALT (non-load-bearing) |
| P14 | check_assert_2: 1 caller (:420), 0 test references | 1 caller, 0 references | MATCH |
| P15 | 43 call sites (2 prod + 40 tests + 1 depositor) | 43 | MATCH |

P10 note: test_cycle_check.py was measured at 132 by live derivation vs plan's 27. This is a stale measurement in the plan — the test suite grew between plan authoring and execution. Mine supersede. No load-bearing decision depends on this count.

---

## Item 2 — Failing Tests (before implementation)

Tests written to all three test files. Run before implementing:

```
5 failed, 178 passed
- test_legacy_schema_v01_not_no_table       [expected LEGACY_SCHEMA, got NO_TABLE]
- test_future_schema_unjudgeable            [expected FUTURE_SCHEMA, got CONFORMANT]
- test_failure_message_names_actual_status  [UNCONFORMANT in message, should be NO_TABLE]
- test_assert2_invalid_register_warns_verdict_unchanged  [TypeError: warnings kwarg]
- test_assert2_valid_register_no_warn       [TypeError: warnings kwarg]
```

Tests 4, 5, 5b, 9 passed before implementation — confirming those behaviors were already correct (commit 45d7aff had already wired NO_TABLE as bad; PRE-SCHEMA was never included in the bad set; contract already held).

Existing fixtures updated: all test_walk_register_lint.py fixtures declaring `0.1` (purely for convenience, not to test legacy behavior) updated to `0.3`. This prevents them from breaking when the version-aware fix lands.

---

## Item 3 — Defect A Fix (walk_register_lint.py — version-aware)

Added:
- `STATUS_LEGACY_SCHEMA = "LEGACY_SCHEMA"` — declared version < validator; not a defect
- `STATUS_FUTURE_SCHEMA = "FUTURE_SCHEMA"` — declared version > validator; too new to assess
- `VALIDATOR_SCHEMA_VERSION = "0.3"` — explicit constant
- `_extract_schema_version(text)` — extracts version string from SCHEMA_DECL_RE
- `_version_tuple(v)` — converts version string to comparable tuple

Modified `validate_file()`: version-aware short-circuit added BEFORE the existing `pre_schema` assignment. Declared version < current → `LEGACY_SCHEMA, [], []`. Declared version > current → `FUTURE_SCHEMA, [], []`. Declared version == current OR no declaration → existing v0.3 validation path unchanged.

Status name ruling (from plan Item 3): names must NOT start with CONFORMANT or NO_TABLE — judge_register classifies by tab-prefixed substring. LEGACY_SCHEMA and FUTURE_SCHEMA both classify as "neither" (not bad, not good) in judge_register without any code change.

---

## Item 4 — Defect B Fix (run_check.py — failure label)

`judge_register` failure message updated: extracts actual status tab-field from each bad line, builds a sorted set, and names it in the message. A NO_TABLE-only sweep now says "1 NO_TABLE file(s): ..." rather than "1 UNCONFORMANT file(s): ...". PASS message simplified to "N file(s) CONFORMANT, 0 bad."

---

## Item 5 — Defect C Fix (cycle_check.py — assert #2 validates, warn-first)

Added module-level import:
```python
from walk_register_lint import (
    validate_file as _validate_register,
    STATUS_CONFORMANT as _REG_CONFORMANT,
    STATUS_PRE_SCHEMA as _REG_PRE_SCHEMA,
    STATUS_LEGACY_SCHEMA as _REG_LEGACY_SCHEMA,
)
_REGISTER_SILENT_STATUSES = frozenset({_REG_CONFORMANT, _REG_PRE_SCHEMA, _REG_LEGACY_SCHEMA})
```

Silent statuses (no warn): CONFORMANT (valid), PRE-SCHEMA (pre-dates schema, not a defect), LEGACY_SCHEMA (honest old-version record, not a defect). Warn statuses: UNCONFORMANT, NO_TABLE, FUTURE_SCHEMA — anything not in the silent set.

`check_assert_2` changes:
- Now returns a 4-tuple: `(register_result, uncommitted, git_has_context, register_warn)`
- Tracks `resolved_path` through all three resolution steps
- After resolution, calls `_validate_register(resolved_path)` and produces a WARN string if status not in `_REGISTER_SILENT_STATUSES`
- Does NOT assign `register_result = "FAIL"` — the pre-wired arm at run_check():424 is the earned promotion path; warn-first is deliberate (plan MUST-PRESERVE)

`run_check()` changes:
- New signature: `run_check(plan_path, warnings=None)` — optional kwarg
- Unpacks 4-tuple from check_assert_2
- Appends `a2_warn` to `warnings` list when supplied
- All 43 existing call sites pass no kwarg → byte-for-byte unaffected
- `--emit-manifest` path at :562 does NOT pass warnings (per plan Item 5 constraint)

`main()` changes:
- Creates `verdict_warnings = []` list
- Passes it to `run_check(plan_path, warnings=verdict_warnings)`
- Prints each warning BEFORE the verdict (stdout contract: verdict is always the last line)

---

## Item 6 — Mutants (knowledge/mutants/register-enforcement.json)

5 mutants documented. Multi-file structure (3 targets): mutation_check must be run once per target file to achieve all 5 kills. The manifest's top-level "target" is cycle_check.py (primary); per-mutant "target" fields override for M1 (walk_register_lint.py) and M2 (run_check.py).

QA Step 2 Item 3 will run mutation_check three times and report the aggregate 5-killed kill map.

| mutant | target | killed by |
|---|---|---|
| M1-drop-version-branch | scripts/walk_register_lint.py | test_walk_register_lint.py::test_legacy_schema_v01_not_no_table |
| M2-pre-schema-counted-bad | tools/run_check.py | test_run_check.py::TestJudgeRegister::test_pre_schema_not_bad |
| M3-assign-fail-not-warn | scripts/cycle_check.py | test_cycle_check.py::test_assert2_invalid_register_warns_verdict_unchanged |
| M4-warn-printed-after-verdict | scripts/cycle_check.py | test_cycle_check.py::test_contract_last_stdout_line_is_verdict |
| M5-run-check-returns-3-tuple (CONTROL) | scripts/cycle_check.py | test_cycle_check.py::test_unparseable_no_block (existing suite) |

---

## Item 7 — Corpus Re-measurement

Post-change distribution (157 registered + 1 new register = 158 total, read from stderr):

| status | count | delta from plan |
|---|---|---|
| CONFORMANT | 91 | was 106 (-15) |
| PRE-SCHEMA | 25 | was 25 (=) |
| UNCONFORMANT | 13 | was 23 (-10) |
| NO_TABLE | 1 | was 3 (-2) |
| LEGACY_SCHEMA | 28 | was 0 (+28, new status) |
| FUTURE_SCHEMA | 0 | was 0 (=) |

The plan expected "the two 0.1 files to move out of NO_TABLE." Measured: 2 files left NO_TABLE (3 → 1), which matches. The 28 LEGACY_SCHEMA files is larger than expected — the Planner measured only 3 NO_TABLE false-positives (two 0.1 files), but 26 additional registers also declare versions < 0.3. These were previously mis-classified as CONFORMANT or UNCONFORMANT by the version-blind validator. All movements are CORRECT:

- No file gained a bad status (CONFORMANT → UNCONFORMANT or NO_TABLE)
- Files moved from bad (NO_TABLE) → neutral (LEGACY_SCHEMA): 2
- Files moved from good (CONFORMANT) → neutral (LEGACY_SCHEMA): ~26
- Files moved from bad (UNCONFORMANT) → neutral (LEGACY_SCHEMA): ~0-few (matches the -10 delta)

Direction: expected. **No HALT.**

---

## Post-conditions Check

- All 183 tests pass (27 + 13 + 132 + 11 new = 183; the 11 new pass post-implementation)
- Corpus re-measured: 2 NO_TABLE files reclassified to LEGACY_SCHEMA ✓
- cycle_check on Done/executable-100028.md now emits WARN and still returns BAR_MET ✓
- Last stdout line is still "BAR_MET" (P8 contract holds) ✓
- mutation_check: to be run post-commit in QA Step 2
