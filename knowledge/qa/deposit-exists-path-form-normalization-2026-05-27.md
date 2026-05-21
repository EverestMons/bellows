# QA Report — deposit_exists Path-Form Normalization

**Date:** 2026-05-27 | **Plan:** executable-deposit-exists-path-form-normalization-2026-05-27 | **Step:** 2

---

## Summary

Verified Step 1's implementation of two components fixing the abs-vs-rel path-form mismatch in `_gate_deposit_exists` (RC3, per diagnostic `deposit-exists-path-form-normalization-2026-05-27.md`). Component A adds `_normalize_deposit_path` helper and normalizes all three membership-check call sites. Component B adds absolute-path-to-worktree remap in `_resolve_deposit_path` Strategy 0. All deliverables verified on disk, all 6 new tests pass, full suite confirms +6 delta with zero new failures, REPL smoke tests confirm correct behavior across all four path forms.

---

## Findings by Severity

**Critical:** None
**Major:** None
**Minor:** None
**Informational:**
- Daemon restart is required for the new gate code to take effect in production (noted in Step 1 dev log).

---

## Testing Coverage

| Function | Tests | Edge Cases |
|----------|-------|------------|
| `_normalize_deposit_path` | 3 unit tests | abs-under-project, project-prefixed-rel, already-rel |
| `_gate_deposit_exists` (normalization) | 2 integration tests | cross-form abs-vs-rel (positive), actually-missing (negative) |
| `_resolve_deposit_path` Strategy 0 | 1 unit test | absolute-path worktree remap |

Total new tests: 6. All pass. Pre-existing test_gates.py tests: 93. All pass.

---

## Deliverable Verification Table

| Deliverable | Expected | Status | Evidence |
|-------------|----------|--------|----------|
| (a) `gates.py` contains `_normalize_deposit_path` with four-form handling | Function at lines 216-236 with abs-under-project, abs-under-dirname, project-prefixed, already-relative branches | ✅ | grep `def _normalize_deposit_path` at line 216; docstring lists four forms; body has `os.path.isabs`, `startswith(prefix)`, `startswith(parent_prefix)`, `startswith(project_basename)` branches |
| (b) `_gate_deposit_exists` calls `_normalize_deposit_path` at 3 sites | `agent_declared.add` (line 295), frontmatter check (line 303), prose-block check (line 310) | ✅ | grep `_normalize_deposit_path` in gates.py returns 4 hits: definition + 3 call sites at lines 295, 303, 310 |
| (c) `_resolve_deposit_path` Strategy 0 has absolute-path remap branch | `os.path.isabs(path)` check at line 254 with prefix-strip and worktree join | ✅ | grep `os.path.isabs(path)` in Strategy 0 block (line 254); `path.startswith(prefix)` at 257; `wt_candidate = os.path.join(wt_path, path[len(prefix):])` at 258 |
| (d) `test_gates.py` contains all 6 new test functions | 6 function names present | ✅ | grep confirms: `test_normalize_deposit_path_abs_to_rel` (1204), `test_normalize_deposit_path_prefixed_to_rel` (1212), `test_normalize_deposit_path_already_rel` (1219), `test_gate_deposit_exists_cross_form_abs_vs_rel` (1226), `test_gate_deposit_exists_actually_missing` (1252), `test_resolve_deposit_path_absolute_worktree_remap` (1274) |

---

## Behavioral Verification Results

### 1. Targeted pytest (`tests/test_gates.py`)

**Result:** 99 passed, 0 failed, 1 warning.

All 6 new tests pass. Zero regressions in 93 pre-existing tests.

Evidence: `pytest_test_gates_v.txt`

### 2. Full suite (`tests/`)

**Result:** 367 passed, 5 failed, 1 warning. Total: 372 tests.

Test count delta: +6 (from 366 to 372). Matches Step 1 claim.

5 failures are all pre-existing:
- `test_decisions.py::TestLoadPhrases::test_loads_phrases_from_file`
- `test_decisions.py::TestLoadPhrases::test_includes_known_phrases`
- `test_decisions.py::TestLoadPhrases::test_splits_slash_alternatives`
- `test_decisions.py::TestExtractDecisionBlocks::test_s_class_blocks_from_ground_truth`
- `test_runner_parser.py::test_run_step_timeout`

Zero NEW failures.

Evidence: `pytest_full_suite.txt`

### 3. Cross-form normalize REPL smoke test

Called `_normalize_deposit_path` with each of the four forms:

| Input Form | Input | Output | Expected | Status |
|------------|-------|--------|----------|--------|
| Absolute under project | `/tmp/.../bellows/knowledge/research/foo.md` | `knowledge/research/foo.md` | `knowledge/research/foo.md` | ✅ |
| Absolute under dirname (sibling) | `/tmp/.../other/knowledge/foo.md` | `other/knowledge/foo.md` | `other/knowledge/foo.md` | ✅ |
| Project-prefixed relative | `bellows/knowledge/research/foo.md` | `knowledge/research/foo.md` | `knowledge/research/foo.md` | ✅ |
| Already project-relative | `knowledge/research/foo.md` | `knowledge/research/foo.md` | `knowledge/research/foo.md` | ✅ |

All 4 forms normalize correctly.

Evidence: `normalize_repl.txt`

### 4. Regression smoke test (2026-05-23 reproduction shape)

Constructed synthetic inputs matching the 2026-05-23 Step 2 failure:
- Plan-required path: absolute (`/tmp/.../bellows/scripts/migrate_config.py`)
- Agent-declared path: relative (`bellows/scripts/migrate_config.py`)
- File exists at the project location

Result: `deposit_exists` is NOT in the failures list. Gate passed correctly.

Evidence: `regression_smoke_repl.txt`

---

## Rule 20 Self-Check

```
============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
Evidence folder: knowledge/qa/evidence/deposit-exists-path-form-normalization-2026-05-27/
Files verified: 4
```

---

## Recommendation

**Pass.** All deliverables verified, all behavioral tests pass, regression smoke test confirms the 2026-05-23 failure mode is resolved. Daemon restart required for production effect.

---

## Output Receipt
**Agent:** Bellows QA
**Step:** 2
**Status:** Complete

### What Was Done
Verified Step 1's implementation of path-form normalization in `_gate_deposit_exists` and `_resolve_deposit_path`. All 4 deliverables confirmed on disk. All 6 new tests pass with zero regressions. REPL smoke tests confirm correct normalization across all four path forms and regression fix for the 2026-05-23 abs-vs-rel failure. Updated PROJECT_STATUS.md with completed milestone.

### Files Deposited
- `bellows/knowledge/qa/deposit-exists-path-form-normalization-2026-05-27.md` — this QA report
- `bellows/knowledge/qa/evidence/deposit-exists-path-form-normalization-2026-05-27/` — evidence directory (4 files)
- `bellows/PROJECT_STATUS.md` — prepended completed milestone
- `bellows/knowledge/research/agent-prompt-feedback.md` — appended QA feedback

### Files Created or Modified (Code)
- None (QA verification only)

### Decisions Made
- All deliverables verified; no fixes required
- Pre-existing 5 test failures confirmed as documented in prior QA reports

### Flags for CEO
- None

### Flags for Next Step
- Daemon restart required for the new gate code to take effect in production
