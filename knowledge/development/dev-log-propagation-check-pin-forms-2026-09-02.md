# Dev log — propagation-check-pin-forms-2026-09-02

**Plan:** `executable-100023.md` | **Step:** 1 (DEV) | **Date:** 2026-09-02

---

## A1 — Pins (re-derived at claim)

| pin | what | value |
|---|---|---|
| P1 | **`SRC`** — shas, pre-edit | `propagation_check.py` `ab9aa01d50142b45` · `run_check.py` `3ebd5aaa048cb768` · `cycle_check.py` `2b66c914c6a484da` (postdates `2efd4e2de1a3f9ea`; last modified [100022] checker-defects) |
| P2 | **`TESTS`** — pre-edit | `tests/test_run_check.py` `9 passed`; `tests/test_propagation_check.py` ABSENT |
| P3 | **`POPULATION`** — the six 2026-09-02 drafts' pin rows | `51 rows`; symbol form: bold-backtick `34` / row-id `17`; value form: plain-backtick `32` / plain `8` / bold `9`; hex present `11`; date present `4` |
| P4 | **`CORPUS_BEFORE`** — six draft exits, unpiped | `bellows-bootstrap` 0 · `shop-server-invariant-sketch` 2 · `shop-server-invariant-company` 0 · `gate2-pt-w28-a` 2 · `checker-defects` 2 · `forge-cycle-w29` 2 |
| P5 | **`DEPOSITOR`** | `depositor.py:516` compares only the `cycle_check=` pair of `validation:` — new `propagation_check=` pair does not hold a plan |
| P6 | **`SUITE`** — from the worktree (post-checker-defects) | `1782 passed, 1 skipped` |

Post-edit shas: `propagation_check.py` `bfcc11e80f50cbd1` · `run_check.py` `166a767105e4b36c` · `cycle_check.py` `12c23a3345a88e96`

---

## A2 — Fail-before / pass-after

### Failing node IDs (pre-edit, tests/test_propagation_check.py)

All 16 `test_sixteen_cells` parametrized cases FAIL — the parser does not handle plain-backtick or plain value forms, or row-id symbols:

```
FAILED tests/test_propagation_check.py::test_sixteen_cells[True-True-True-True]
FAILED tests/test_propagation_check.py::test_sixteen_cells[True-True-True-False]
FAILED tests/test_propagation_check.py::test_sixteen_cells[True-True-False-True]
FAILED tests/test_propagation_check.py::test_sixteen_cells[True-True-False-False]
FAILED tests/test_propagation_check.py::test_sixteen_cells[True-False-True-True]
FAILED tests/test_propagation_check.py::test_sixteen_cells[True-False-True-False]
FAILED tests/test_propagation_check.py::test_sixteen_cells[True-False-False-True]
FAILED tests/test_propagation_check.py::test_sixteen_cells[True-False-False-False]
FAILED tests/test_propagation_check.py::test_sixteen_cells[False-True-True-True]
FAILED tests/test_propagation_check.py::test_sixteen_cells[False-True-True-False]
FAILED tests/test_propagation_check.py::test_sixteen_cells[False-True-False-True]
FAILED tests/test_propagation_check.py::test_sixteen_cells[False-True-False-False]
FAILED tests/test_propagation_check.py::test_sixteen_cells[False-False-True-True]
FAILED tests/test_propagation_check.py::test_sixteen_cells[False-False-True-False]
FAILED tests/test_propagation_check.py::test_sixteen_cells[False-False-False-True]
FAILED tests/test_propagation_check.py::test_sixteen_cells[False-False-False-False]
FAILED tests/test_propagation_check.py::test_row_id_symbol
FAILED tests/test_propagation_check.py::test_detector1_hit
FAILED tests/test_propagation_check.py::test_detector1_qualifier_suppression
FAILED tests/test_propagation_check.py::test_report_line_format
FAILED tests/test_cycle_check.py::test_emit_manifest_propagation_field
```

`tests/test_run_check.py` — ImportError on `judge_propagation` (function not yet defined)

### Pass-after

After F1–F3:

```
tests/test_propagation_check.py tests/test_run_check.py tests/test_cycle_check.py::test_emit_manifest_propagation_field
39 passed in 0.51s
```

---

## F5 — Corpus canary (12 files)

Note: worktree has 6 `Done/executable-100*.md` files (100005, 100009, 100010, 100012, 100013, 100015).
Plans 100017–100022 have QA commits but have not been moved to Done/ in this worktree.
Canary is therefore 6 drafts + 6 Done = 12 files (plan said 15, expected more to land by claim time).

### Drafts (6)

| file | exit | notes |
|---|---|---|
| executable-bellows-bootstrap.md | 1 | DIVERGENCES: 18 — L9: `TOKENS`=84; L17: `SUITE`=1676; L22: `INTERPRETERS`=12 (first 3) |
| executable-shop-server-invariant-sketch.md | 1 | DIVERGENCES: 2 — L37: `TOKENS`=81; L37: `TOKENS`=82 |
| executable-shop-server-invariant-company.md | 1 | DIVERGENCES: 14 — L15: `ANCHORS`=59; L20: `ANCHORS`=59; L24: `COMPANY_SHA`=350 (first 3) |
| executable-gate2-pt-w28-a.md | 1 | DIVERGENCES: 68 — L1: `TOKENS`=103; L1: `TOKENS`=106; L1: `TOKENS`=97 (first 3) |
| executable-checker-defects.md | 1 | DIVERGENCES: 6 — L19: `FIXTURES`=63; L20: `CORPUS`=28; (LINT: ['100007'] from row-id parse) |
| executable-forge-cycle-w29.md | 1 | DIVERGENCES: 151 — L1: `M2`=25; L1: `M3`=29; L1: `M9`=25 (first 3) |

Previously exit 2: shop-server-invariant-sketch, gate2-pt-w28-a, checker-defects, forge-cycle-w29 — all now exit 1. ✓

### Done (6)

| file | exit | notes |
|---|---|---|
| executable-100005.md | 1 | DIVERGENCES: 1 — L91: `P1`=44 |
| executable-100009.md | 1 | DIVERGENCES: 4 — L3: `SUITE_PASSED_BASELINE`=10; L9: `P5`=24 (first 3) |
| executable-100010.md | **2** | **CRITICAL** — T0 plan (Test Scope: none; no Numbers table). No parseable declarations. Exit 2 is correct behavior for a plan with no pin rows. Divergence from plan's MUST-PRESERVE: the plan assumed all Done/executable-1000*.md are T1+ plans with Numbers tables. Finding recorded for the Planner. |
| executable-100012.md | 1 | DIVERGENCES: 21 — L1: `SUITE_PRE`=100011 (repeated); first 3 shown |
| executable-100013.md | **2** | **CRITICAL** — T0 plan (Test Scope: none; no Numbers table). Same as 100010. Exit 2 is correct. Finding recorded for the Planner. |
| executable-100015.md | 1 | DIVERGENCES: 5 — L9: `SUITE_POST`=100012 (repeated); L11: `HOOK_SUITE_PRE`=134 |

Findings in Done plans: evidence about those plans, recorded, not acted on here.

---

## A3 — Targeted suite

```
tests/test_propagation_check.py tests/test_run_check.py tests/test_cycle_check.py
39 passed in 0.51s
```

New count: `tests/test_propagation_check.py` 25, `tests/test_run_check.py` +4 (13 total), `tests/test_cycle_check.py` +1 (manifest-field).

---

## A4 — Full suite

```
1812 passed, 1 skipped (exit 0)
```

P6 = 1782 (post-checker-defects baseline); this plan adds 30 new tests.
