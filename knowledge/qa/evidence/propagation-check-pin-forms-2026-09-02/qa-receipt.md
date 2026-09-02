# QA Receipt — propagation-check-pin-forms-2026-09-02

**Plan:** `executable-100023.md` | **Step:** 2 (QA) | **Date:** 2026-09-02
**Slug:** `propagation-check-pin-forms-2026-09-02`

---

## Verification Table

All evidence raw output in `probes-raw.txt`; full suite in `full-suite-propagation-check-pin-forms.txt`.

### Item 1 — Fail-before / Pass-after (second pair of hands)

Pre-edit modules via `git show HEAD~1:` — shas match P1 (propagation_check.py `ab9aa01d50142b45`, run_check.py `3ebd5aaa048cb768`). Temporarily swapped in; `git checkout HEAD --` to restore.

| File | Exit (pre-edit) | Count | Status |
|---|---|---|---|
| tests/test_propagation_check.py | various | 20 failed | ✅ |
| tests/test_run_check.py | ImportError on judge_propagation | 1 error | ✅ |
| tests/test_cycle_check.py::test_emit_manifest_propagation_field | 1 failed | 1 failed | ✅ |
| tests/test_propagation_check.py + test_run_check.py + test_cycle_check.py (post-edit) | 0 | 39 passed | ✅ |

Fail-before node IDs confirmed (from pre-edit run):
- `test_sixteen_cells[True-True-True-True]` … `[False-False-False-False]` — 16 cells
- `test_row_id_symbol`, `test_detector1_hit`, `test_detector1_qualifier_suppression`, `test_report_line_format`
- `test_run_check.py` — ImportError: cannot import name `judge_propagation`
- `test_cycle_check.py::test_emit_manifest_propagation_field` — `propagation_check=` absent from manifest

### Item 2 — Corpus canary (12 files)

Note: worktree has 6 `Done/executable-100*.md`. Plans 100017–100022 have QA commits but are not in `Done/` in this worktree; Step 1 dev log documents the discrepancy (plan expected 15, actual 12).

#### 2026-09-02 draft plans (6 files)

| File | Exit | Divergences | Status |
|---|---|---|---|
| executable-bellows-bootstrap.md | 1 | 18 | ✅ |
| executable-shop-server-invariant-sketch.md | 1 | 2 | ✅ |
| executable-shop-server-invariant-company.md | 1 | 14 | ✅ |
| executable-gate2-pt-w28-a.md | 1 | 68 | ✅ |
| executable-checker-defects.md | 1 | 6 | ✅ |
| executable-forge-cycle-w29.md (forge_lessons) | 1 | 151 | ✅ |

All six previously exit-2 plans (shop-server-invariant-sketch, gate2-pt-w28-a, checker-defects, forge-cycle-w29) now exit 1 — F1 fix confirmed.

#### Done/executable-100*.md plans (6 files)

| File | Exit | Notes | Status |
|---|---|---|---|
| executable-100005.md | 1 | 1 divergence — P1=44 | ✅ |
| executable-100009.md | 1 | 4 divergences | ✅ |
| executable-100010.md | 2 | T0 plan (Test Scope: none; no Numbers table) — no parseable declarations | ❌ |
| executable-100012.md | 1 | 21 divergences | ✅ |
| executable-100013.md | 2 | T0 plan (Test Scope: none; no Numbers table) — no parseable declarations | ❌ |
| executable-100015.md | 1 | 5 divergences | ✅ |

**Critical finding (pre-documented in Step 1 dev log):** executable-100010.md and executable-100013.md are T0 plans with no Numbers discipline table; the tool's exit 2 is correct behavior for plans with no pin rows. The MUST-PRESERVE condition "no corpus plan exits 2" does not apply to plans that have no pin rows. Finding carried forward to follow-ups for their Planners.

#### Item 2 (cont.) — Legacy-form positive control

| Test | Result | Status |
|---|---|---|
| `| N1 | **\`BATCH\`** | — | **25** |` → BATCH: ['25'] | exit 0, declared symbols: 1 (values: 1) | ✅ |

#### Item 2 (cont.) — Exit-2 path (no numerals in pin rows)

| Test | Result | Status |
|---|---|---|
| Synthetic table with `no-numerals-here` value cells | exit 2 | ✅ |

### Item 2.5 — Kill map (Rule 106) — M1–M4

`propagation-check.json` uses per-mutant `target` fields (multi-target format). `mutation_check.py` requires a single top-level `target`. Run as three per-target manifests.

| Mutant | Target | Result | Status |
|---|---|---|---|
| M1-hex-exclusion-removed | scripts/propagation_check.py | KILLED | ✅ |
| M2-row-id-fallback-removed | scripts/propagation_check.py | KILLED | ✅ |
| M3-judge-propagation-rc2-as-pass | tools/run_check.py | KILLED | ✅ |
| M4-manifest-propagation-pair-dropped | scripts/cycle_check.py | KILLED | ✅ |

4/4 KILLED, 0 survived, 0 error.

### Item 3 — Loud channel

| Check | Result | Status |
|---|---|---|
| `run_check.py propagation <plan>` | `RUN_CHECK: propagation VERDICT=FAIL — 8 divergence(s)` | ✅ |
| `cycle_check.py --emit-manifest <plan>` | `validation: ... propagation_check=DIVERGENT:8` | ✅ |
| `depositor.py:516` compares only `cycle_check=` pair | `val.split("cycle_check=")[1].split(",")[0]` — new pair does not hold | ✅ |

### Item 4 — Full suite

| File | Exit | Count | Status |
|---|---|---|---|
| full-suite-propagation-check-pin-forms.txt | 0 | 1812 passed | ✅ |

---

## Follow-ups (not acted on here)

### Canary divergences in held plans — for their Planners

These findings are the Planners' to read at the next touch; not fixed here.

| Plan | Divergences |
|---|---|
| executable-bellows-bootstrap.md | 18 (SUITE, INTERPRETERS, TOKENS) |
| executable-shop-server-invariant-sketch.md | 2 (TOKENS) |
| executable-shop-server-invariant-company.md | 14 (ANCHORS, COMPANY_SHA) |
| executable-gate2-pt-w28-a.md | 68 (TOKENS, many M-symbols) |
| executable-checker-defects.md | 6 (FIXTURES, CORPUS, LINT row-id parse) |
| executable-forge-cycle-w29.md | 151 (M-symbols) |
| executable-100005.md | 1 (P1=44) |
| executable-100009.md | 4 (SUITE_PASSED_BASELINE, P5) |
| executable-100012.md | 21 (SUITE_PRE repeated) |
| executable-100015.md | 5 (SUITE_POST, HOOK_SUITE_PRE) |

### T0 plans exit 2 — for their Planners

executable-100010.md and executable-100013.md are T0 plans with no Numbers discipline table. The propagation checker exits 2 on these plans (correct behavior — no pin rows to parse). Planners for these plans should note the tool's honest signal.

### Thread 90

Thread 90's closure is a keyboard act — not performed here.

### kill-map manifest format

`propagation-check.json` uses per-mutant `target` fields (multi-target). `mutation_check.py` requires a single top-level `target`. For this QA run, the kill map was exercised via three single-target manifests. Open fork: update either the manifest or the tool to support multi-target format natively.

---

## Rule 20 — QA Self-Check Results

```
============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
Evidence folder: /Users/marklehn/Developer/bellows/.bellows-worktrees/100023/knowledge/qa/evidence/propagation-check-pin-forms-2026-09-02/
Files verified: 2
```
