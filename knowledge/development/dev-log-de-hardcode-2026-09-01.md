# Dev Log — de-hardcode-governance-root-2026-09-01 (plan 100011)

## A1 — Pins re-derived (2026-09-01, worktree 100011)

All values match the plan's published pins. No HALT.

### P1 — TARGET_SHAS (sha256 first 16 of ten targets)

| file | measured | plan | match |
|---|---|---|---|
| bellows_root.py | 23a3d6657ea97d48 | 23a3d6657ea97d48 | ✓ |
| gates.py | 8c1f6dbf70e692d3 | 8c1f6dbf70e692d3 | ✓ |
| verdict.py | 679097ca744ce8e2 | 679097ca744ce8e2 | ✓ |
| planner.py | 2c411d406f6ba8eb | 2c411d406f6ba8eb | ✓ |
| decisions.py | 6895797bf3da86e3 | 6895797bf3da86e3 | ✓ |
| bellows.py | ef6a0a5f532203d8 | ef6a0a5f532203d8 | ✓ |
| plan_claim.py | a341bc4c5538fad0 | a341bc4c5538fad0 | ✓ |
| scripts/plan_lint.py | 167b219160ff6358 | 167b219160ff6358 | ✓ |
| scripts/migrate_orphan_verdicts.py | 463bde66b2732b33 | 463bde66b2732b33 | ✓ |
| CLAUDE.md | 9cf263c9c16d05b5 | 9cf263c9c16d05b5 | ✓ |

### P2 — BUILDER_SHA

Measured: `c2cbb25b9f034c52` — matches plan (bellows `04f9816`, fifth commit).

### P9 — LITERAL_PRE (`/Users/marklehn/Developer/GitHub` per file, pre-edit)

| file | count |
|---|---|
| bellows_root.py | 0 |
| gates.py | 1 |
| verdict.py | 0 |
| planner.py | 1 |
| decisions.py | 0 |
| bellows.py | 1 |
| plan_claim.py | 1 |
| scripts/plan_lint.py | 1 |
| scripts/migrate_orphan_verdicts.py | 1 |
| CLAUDE.md | 1 |

Total: 7 — matches plan. `/Developer/GitHub/` in verdict.py: 4 lines — matches plan.

### P5 — SUITE_BASELINE (worktree shape, pre-edit)

`9 failed, 1642 passed, 1 skipped`

FAILED names (verbatim from output):
- `tests/test_decisions.py::TestLoadPhrases::test_loads_phrases_from_file`
- `tests/test_decisions.py::TestLoadPhrases::test_includes_known_phrases`
- `tests/test_decisions.py::TestLoadPhrases::test_splits_slash_alternatives`
- `tests/test_decisions.py::TestExtractDecisionBlocks::test_s_class_blocks_from_ground_truth`
- `tests/test_phase4_planner_retry.py::test_planner_retries_on_auth_failure`
- `tests/test_phase4_planner_retry.py::test_planner_falls_back_to_continue_on_persistent_failure`
- `tests/test_planner.py::test_build_consult_file`
- `tests/test_planner.py::test_consult_bad_json`
- `tests/test_planner.py::test_consult_timeout`

The survivor (`test_relative_path_unchanged`) did NOT appear — confirmed worktree shape. Matches plan.

---

## A2 — Builder run

Command: `"$PY" knowledge/decisions/drafts/build-de-hardcode-governance-root.py "$(pwd)" "$S"`

OK line (verbatim):
```
OK — 10 files edited + tests/test_governance_root.py written, 12 edits; combined sha ef54ed624237da4b…
```

P4 `ef54ed624237da4b` matches plan. Exit 0.

---

## A3 — Eleven outputs copied with closure

```
SAME bellows_root.py
SAME gates.py
SAME verdict.py
SAME planner.py
SAME decisions.py
SAME bellows.py
SAME plan_claim.py
SAME scripts/plan_lint.py
SAME scripts/migrate_orphan_verdicts.py
SAME CLAUDE.md
SAME tests/test_governance_root.py
```

py_compile on nine .py targets: exit 0.

---

## A4 — Probes (post-edit)

| probe | expected | measured |
|---|---|---|
| `def resolve_governance_root(` in bellows_root.py | 1 | 1 |
| `def resolve_projects_parent(` in bellows_root.py | 1 | 1 |
| `_rule20_block_path()` in gates.py | 2 | 2 |
| `_strip_projects_parent(path)` in verdict.py | 2 | 2 |
| `from bellows_root import resolve_governance_root` in planner.py | 1 | 1 |
| `from bellows_root import resolve_governance_root` in decisions.py | 1 | 1 |
| `from bellows_root import resolve_governance_root` in scripts/plan_lint.py | 1 | 1 |
| `from bellows_root import resolve_projects_parent` in bellows.py | 1 | 1 |
| `from bellows_root import resolve_projects_parent` in plan_claim.py | 1 | 1 |
| `resolve_bellows_root()` in scripts/migrate_orphan_verdicts.py | 1 | 1 |
| `resolve_projects_parent()` in CLAUDE.md | 1 | 1 |
| `/Users/marklehn/Developer/GitHub` in each of ten targets (post) | 0 each | 0 each |
| `Developer/GitHub` in bellows_root.py (liveness pair) | 1 | 1 |
| `/Developer/GitHub/` in verdict.py (post) | 0 | 0 |

All probes pass.

---

## A5 — Tests

### A5(a) P7 — New test file (12 tests)

Without `ELUVIAN_WRAP_ROOT`: `12 passed in 0.94s`
With `ELUVIAN_WRAP_ROOT=/Users/marklehn/Developer/eluvian-governance`: `12 passed in 0.91s`

### A5(b) Targeted tests

`185 passed in 7.00s` — matches expected (walk 0 measured value). No `FAILED` lines.

### A5(c) Three resolutions both ways

Without `ELUVIAN_WRAP_ROOT`:
```
/Users/marklehn/Developer/eluvian-governance
/Users/marklehn/Developer
/Users/marklehn/Developer/tuyere
```

With `ELUVIAN_WRAP_ROOT=/Users/marklehn/Developer/eluvian-governance`:
```
/Users/marklehn/Developer/eluvian-governance
/Users/marklehn/Developer
/Users/marklehn/Developer/tuyere
```

Identical both ways. No `.bellows-worktrees` in line 2. `RULE_20_SELF_CHECK_BLOCK.md` exists at `<governance root>`.

### A5(d) QA_MANDATE_SUFFIX

Names `/Users/marklehn/Developer/eluvian-governance/RULE_20_SELF_CHECK_BLOCK.md`. Contains no `Developer/GitHub`. Pass.

---

## P8 — DAEMON_ENV note (copied from plan)

Cannot measure from a worktree. Per plan: `ELUVIAN_WRAP_ROOT` occurrences in the running daemon (pid 93535): **0**. The daemon does not carry this variable. The daemon will inject the OLD mandate (pre-fix code) until the CEO restarts it via the dashboard (`r`, `y`) after the cycle closes.
