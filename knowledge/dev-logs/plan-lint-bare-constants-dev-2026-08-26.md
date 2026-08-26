# Dev Log: plan-lint-bare-constants — (r) WARN check

**Date:** 2026-08-26
**Plan:** executable-561

## Wiring anchor

Line 804 (post-edit): `for status, check, detail in results:` — the `_check_bare_constants(plan_text)` call inserted immediately before this line, after the (q) pin verification block.

## Function insertion

`_check_bare_constants` and its module-level constants (`_BARE_CONSTANT_RE`, `_CLAUSE_MARKERS`) inserted before `def lint(plan_path):` at line 178 (pre-edit). The function reads the same `plan_text` variable used by all neighboring checks.

## Targeted tests

```
139 passed, 0 failed in 5.48s
```

Tests: `tests/test_plan_lint_bare_constants.py` (5 tests) + `tests/test_plan_lint.py` (134 tests). Derivation: 134 existing + 5 new = 139 total; 0 failed; supersedes with this derivation.

## Prototype table (60 newest Done plans by mtime)

```
fires	path
0	bellows/Done/executable-560.md
1	governance/Done/executable-559.md
0	lessons-forge/Done/executable-557.md
0	lessons-forge/Done/executable-556.md
0	bellows/Done/executable-555.md
0	bellows/Done/executable-554.md
3	governance/Done/executable-553.md
1	governance/Done/executable-552.md
1	bellows/Done/executable-548.md
1	bellows/Done/executable-543.md
1	governance/Done/executable-550.md
1	lessons-forge/Done/executable-549.md
0	governance/Done/executable-547.md
0	governance/Done/executable-546.md
0	governance/Done/executable-545.md
0	lessons-forge/Done/executable-544.md
16	governance/Done/executable-542.md
7	governance/Done/executable-541.md
14	governance/Done/executable-540.md
12	governance/Done/executable-539.md
11	governance/Done/executable-538.md
0	lessons-forge/Done/executable-537.md
0	lessons-forge/Done/executable-536.md
0	bellows/Done/executable-535.md
0	bellows/Done/executable-534.md
0	bellows/Done/executable-533.md
0	bellows/Done/executable-532.md
0	bellows/Done/diagnostic-531.md
1	lessons-forge/Done/executable-530.md
0	lessons-forge/Done/executable-529.md
0	lessons-forge/Done/diagnostic-528.md
0	bellows/Done/executable-527.md
0	bellows/Done/diagnostic-526.md
0	governance/Done/executable-525.md
0	bellows/Done/executable-524.md
0	bellows/Done/executable-523.md
0	bellows/Done/diagnostic-522.md
0	bellows/Done/diagnostic-521.md
0	bellows/Done/executable-520.md
0	bellows/Done/diagnostic-519.md
0	bellows/Done/executable-518.md
0	bellows/Done/diagnostic-517.md
0	bellows/Done/executable-516.md
0	bellows/Done/diagnostic-515.md
0	bellows/Done/executable-514.md
0	governance/Done/diagnostic-512.md
0	bellows/Done/diagnostic-511.md
4	governance/Done/executable-510.md
0	governance/Done/diagnostic-509.md
0	lessons-forge/Done/executable-507.md
0	lessons-forge/Done/diagnostic-506.md
0	governance/Done/executable-505.md
0	lessons-forge/Done/diagnostic-504.md
0	lessons-forge/Done/diagnostic-503.md
0	governance/Done/executable-502.md
1	lessons-forge/Done/diagnostic-501.md
1	lessons-forge/Done/executable-500.md
0	lessons-forge/Done/diagnostic-498.md
0	bellows/Done/executable-497.md
0	bellows/Done/executable-496.md
```

**TOTAL: 76 across 60 plans (corpus: 694 total)**

Average: ~1.27 warns/plan. Well under the 600 tuning threshold (>10/plan average = noise territory). No tuning STOP triggered.

Top-firing plans: governance 542 (16), governance 540 (14), governance 539 (12), governance 538 (11), governance 541 (7) — all in the governance/Done cluster, likely the Drafting Cycle plans with heavy numeric content (§-reference-heavy governance executable series 538–542).
