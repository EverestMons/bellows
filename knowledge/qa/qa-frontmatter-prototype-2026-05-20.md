# QA Report — YAML Frontmatter Prototype for `deposit_exists` Gate

**Date:** 2026-05-20
**Plan:** executable-frontmatter-prototype-deposit-exists-2026-05-20
**Step:** 2 (QA)
**ADR:** ADR-structured-plan-metadata-2026-05-20 (Section 7 — Prototype Scope)

---

## (1) Install Verification

**Environment:** Python 3.9.6 (macOS, system Python)
**pyyaml version:** 6.0.3

```
$ python3 -c "import yaml; print(yaml.__version__)"
6.0.3

$ pip3 list | grep -i pyyaml
PyYAML             6.0.3
```

**Result: PASS** — pyyaml 6.0.3 installed and importable.

---

## (2) Unit Tests

**Command:** `python3 -m pytest tests/test_gates.py -v`
**Result:** 89 passed, 0 failed, 0 errors, 1 warning (urllib3/LibreSSL, unrelated)

### New Test Name Verification

| # | Spec Name (Step 1 (f)) | Actual Name | Match |
|---|------------------------|-------------|-------|
| 1 | `test_parse_plan_header_yaml_frontmatter_returns_deposits_list` | `test_parse_plan_header_yaml_frontmatter_returns_deposits_list` | Exact |
| 2 | `test_parse_plan_header_yaml_frontmatter_returns_nested_qa_dict` | `test_parse_plan_header_yaml_frontmatter_returns_nested_qa_dict` | Exact |
| 3 | `test_parse_plan_header_malformed_yaml_falls_through_to_bold_markdown` | `test_parse_plan_header_malformed_yaml_falls_through_to_bold_markdown` | Exact |
| 4 | `test_gate_deposit_exists_uses_frontmatter_when_present_and_passes_when_file_exists` | `test_gate_deposit_exists_uses_frontmatter_when_present_and_passes_when_file_exists` | Exact |
| 5 | `test_gate_deposit_exists_uses_frontmatter_and_ignores_staging_in_prose` | `test_gate_deposit_exists_uses_frontmatter_and_ignores_staging_in_prose` | Exact |

All 5 test names match the spec exactly. No name drift.

### Existing Test Regression Check

84 pre-existing tests pass. Two tests (`test_parse_plan_header_basic`, `test_parse_plan_header_yaml_still_works`) were updated to assert `auto_close is False` (boolean) instead of `auto_close == "false"` (string), reflecting the `yaml.safe_load` native type change. Both pass.

**Result: PASS** — 89/89 tests pass, zero regressions, all 5 new test names match spec.

Full test output saved to: `knowledge/qa/evidence/frontmatter-prototype-2026-05-20/test-output.txt`

---

## (3) Canary Plan Execution

### Canary Plan Authored

`knowledge/decisions/executable-frontmatter-canary-2026-05-20.md`

Canary plan structure:
- **YAML frontmatter:** `deposits: [bellows/knowledge/research/frontmatter-canary-deposit-2026-05-20.md]`
- **Prose `**Deposits:**` block:** mentions `_staging_frontmatter-canary-deposit-2026-05-20.md` (transient name — strike 4 reproduction bait)
- **Step 1:** Simple DEV step that creates the deposit file

### Execution Method

Programmatic gate simulation via `gates.check()` — daemon dispatch was not available in the worktree context. The simulation used daemon-mode path resolution:
- `project_path`: `/Users/marklehn/Developer/GitHub/bellows` (main project root)
- `wt_path`: worktree root (where the agent writes files)

This matches how the daemon invokes `gates.check()` in production.

### Gate Results

```
passed: True
failures: []
plan_header: {"deposits": ["bellows/knowledge/research/frontmatter-canary-deposit-2026-05-20.md"]}
deposit_exists failures: []
staging failures: []
VERDICT: PASS — frontmatter deposits used, prose _staging_ ignored
```

### Verification

- `plan_header["deposits"]` is a Python list containing the single frontmatter path — confirms `yaml.safe_load` extracted the list correctly.
- Zero `deposit_exists` failures — the frontmatter path was resolved via worktree Strategy 0.
- Zero staging-related failures — the prose `_staging_frontmatter-canary-deposit-2026-05-20.md` was NOT extracted because the frontmatter-first branch skipped `_extract_plan_required_deposits` entirely.
- The dev log confirms no `deposit_source` instrumentation field was added in this prototype. Verification is indirect: the gate did not log any `plan-required deposit missing` failure for the `_staging_*` name, confirming frontmatter was used as the authoritative source.

**Result: PASS** — frontmatter-first branch used, prose `_staging_*` ignored (strike 4 reproduction defense confirmed).

Canary simulation output saved to: `knowledge/qa/evidence/frontmatter-prototype-2026-05-20/canary-simulation.txt`

**Note:** Canary plan at `knowledge/decisions/executable-frontmatter-canary-2026-05-20.md` remains in decisions/ — the Planner moves it to Done/ after verification. The daemon was not dispatched (worktree context); full daemon dispatch requires CEO to restart the daemon post-pyyaml install.

---

## (4) Regression Check — Gate 2c Canary

### Method

Ran all 13 Rule 20 tests via `python3 -m pytest tests/test_gates.py -v -k "rule_20"`.

### Results

```
13 passed, 76 deselected in 0.03s
```

All Rule 20 gate tests pass:
- `test_rule_20_self_check_passes_with_valid_banner_and_passed_line` — PASS
- `test_rule_20_self_check_fails_when_banner_missing` — PASS
- `test_rule_20_self_check_fails_when_banner_without_passed_line` — PASS
- `test_rule_20_self_check_fails_when_deposit_unreadable` — PASS
- `test_rule_20_self_check_skipped_on_non_qa_step` — PASS
- `test_rule_20_self_check_passes_when_passed_line_after_banner_in_multi_section_report` — PASS
- `test_rule_20_self_check_resolves_via_worktree_path` — PASS
- `test_rule_20_banner_in_fenced_block` — PASS (strike 5)
- `test_rule_20_banner_with_decoration` — PASS (strike 5)
- `test_rule_20_banner_with_shell_prompt_prefix` — PASS (strike 3)
- `test_rule_20_passed_line_with_indentation` — PASS (strike 5 variant)
- `test_rule_20_no_banner` — PASS (strike 6)
- `test_rule_20_banner_without_passed` — PASS

The frontmatter changes touched `_parse_plan_header`, `_gate_deposit_exists`, and `check()` only. The `_gate_rule_20_self_check` function was not modified. Zero regression.

### Prior Canary Confirmation

The last gate-2c canary rerun (`knowledge/qa/gate-2c-canary-rerun-qa-2026-05-19.md`) passed on 2026-05-19 with the Rule 20 self-check banner verified.

**Result: PASS** — Rule 20 code path unaffected by frontmatter changes.

---

## Implementation Review — ADR Section 7 Compliance

| ADR Section 7 Requirement | Implementation | Verified |
|--------------------------|----------------|----------|
| `_parse_plan_header` Strategy 1: extract `deposits` as list | `yaml.safe_load(match.group(1))` returns native list | Yes — test 1 |
| `_gate_deposit_exists`: frontmatter-first branch | `plan_header.get("deposits")` checked before prose extraction | Yes — tests 4, 5 |
| `_gate_deposit_exists`: skip `_extract_plan_required_deposits` when frontmatter present | `elif` structure ensures prose fallback only without frontmatter | Yes — test 5 |
| `check()`: pass `plan_header` to `_gate_deposit_exists` | `header` computed at line 123, passed at line 134 | Yes — code review |
| `_extract_plan_required_deposits`: NOT modified | Function unchanged (prose fallback preserved) | Yes — 4 existing staging filter tests pass |
| `_gate_rule_20_self_check`: NOT modified | Function unchanged | Yes — 13 Rule 20 tests pass |
| Dual-mode Phase 1: plans without frontmatter use prose | `elif` branch falls through to existing code | Yes — all 84 pre-existing tests pass |

---

## Deliverable Verification

| # | Deliverable | Present | Content Filled | Evidence |
|---|-------------|---------|----------------|----------|
| 1 | `gates.py` — yaml.safe_load in Strategy 1 | Yes | `yaml.safe_load(match.group(1))` at line 52 | Code review |
| 2 | `gates.py` — frontmatter-first branch in `_gate_deposit_exists` | Yes | Lines 248-253 | Code review |
| 3 | `gates.py` — `plan_header` threading in `check()` | Yes | Line 123 (compute), line 134 (pass) | Code review |
| 4 | `requirements.txt` — pyyaml added | Yes | Line 5 | File read |
| 5 | `tests/test_gates.py` — 5 new tests | Yes | Lines 1066-1130 | Test run |
| 6 | `tests/fixtures/sample.md` — test fixture | Yes | 2 lines | File exists |
| 7 | `knowledge/development/dev-log-frontmatter-prototype-2026-05-20.md` — dev log | Yes | 127 lines, complete output receipt | File read |

---

============================================================
Rule 20 — QA Self-Check Results
============================================================

Check 1: QA report file exists at knowledge/qa/qa-frontmatter-prototype-2026-05-20.md
  Result: PASS

Check 2: Evidence directory exists at knowledge/qa/evidence/frontmatter-prototype-2026-05-20/
  Result: PASS

Check 3: Evidence files present
  - test-output.txt: PASS (89 passed, 0 failed)
  - canary-simulation.txt: PASS (canary passed)
  Result: PASS

Check 4: All 89 unit tests pass with zero regressions
  Result: PASS

Check 5: All 5 new test names match Step 1 (f) spec exactly
  Result: PASS

Check 6: Canary plan gates pass with frontmatter-first branch (strike 4 reproduction defense)
  Result: PASS

Check 7: Rule 20 regression check — 13/13 tests pass
  Result: PASS

Check 8: No hedging keywords in QA report
  Result: PASS

PASSED — SELF-CHECK PASSED — all evidence files present, all checks pass, no hedging keywords found.

============================================================

---

## Output Receipt
**Agent:** Bellows QA
**Step:** 2
**Status:** Complete

### What Was Done
Verified the YAML frontmatter prototype implementation against the ADR Section 7 prototype scope and the Step 1 dev log. Four QA areas covered: install verification (pyyaml 6.0.3), unit tests (89/89 pass, 5 new test names match spec), canary plan simulation (frontmatter-first branch passes, prose `_staging_*` ignored), and regression check (13/13 Rule 20 tests pass, gate-2c code path unaffected).

### Files Deposited
- `knowledge/qa/qa-frontmatter-prototype-2026-05-20.md` — this QA report

### Files Created or Modified (Code)
- None (QA is read-only on production code)

### Decisions Made
- Canary execution used programmatic gate simulation (`gates.check()`) rather than full daemon dispatch, since the worktree context does not have a running daemon. The simulation used daemon-mode path resolution (separate `project_path` and `wt_path`), matching production behavior.
- Canary plan left in `knowledge/decisions/` (not moved to Done/) — the Planner handles Done/ moves.

### Flags for CEO
- **Daemon restart required:** The daemon must be restarted after pyyaml install for `import yaml` to take effect. The canary was verified via programmatic simulation; full daemon dispatch awaits daemon restart.
- **Type change risk (carried from Step 1):** `bellows.py:458` calls `.lower()` on `header.get("auto_close", "false")`. If any legacy plan has `auto_close: false` in YAML frontmatter, the `yaml.safe_load` return type (`False` boolean) would crash. New plans per ADR keep `auto_close` in bold-Markdown header. Recommend defensive fix: `str(header.get("auto_close", "false")).lower()`.

### Flags for Next Step
- None (final step)
