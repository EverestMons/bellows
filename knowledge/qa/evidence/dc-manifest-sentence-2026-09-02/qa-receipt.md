# QA Receipt — dc-manifest-sentence-2026-09-02 (plan 100027)

**Date:** 2026-09-02 | **Step:** 2 (QA) | **Plan tier:** T2 | **Slug:** dc-manifest-sentence-2026-09-02

**Evidence file:** `probes-raw.txt` — raw probe output for Items 1–4.

---

## Verification

| Item | Check | Status |
|------|-------|--------|
| 1a | Newest commit on `DRAFTING_CYCLE.md` is plan 100027's commit (`d02fa149`) — no foreign DC edit landed between steps | ✅ |
| 1b | `ten REQUIRED fields` count = 1 (new token present) | ✅ |
| 1c | `three OPTIONAL fields` count = 1 (new token present) | ✅ |
| 1d | `one of the FOUR values` count = 1 (new token present) | ✅ |
| 1e | `compares ONLY the declared` count = 1 (new token present) | ✅ |
| 1f | `{read-only, governed-tooling, register-writing}` count = 0 (retired literal absent) | ✅ |
| 1g | `HARD-HOLD` count = 2 (invariant holds — the 2.17 row and the 2.24 row; not the sentence) | ✅ |
| 1h | `HOLD-AND-REPORT` count = 2 (invariant holds — the 2.17 row and the 2.24 row; not the sentence) | ✅ |
| 1i | `**Version:** 2.24 (2026-09-02)` count = 1; `**Version:** 2.23 (2026-09-01)` count = 0 | ✅ |
| 1j | 2.24 History row (`slug dc-manifest-sentence-2026-09-02`) present = 1; 2.23 row (`slug gate2-dc-w28-2026-09-01`) survives = 1 | ✅ |
| 1k | `class: governed-tooling` (whole line) = 0; `class: shop-infra` (whole line) = 1 | ✅ |
| 1l | Four-pair validation line (whole line) = 1 | ✅ |
| 1m | `wc -l` = 370 | ✅ |
| 1n | `git status --porcelain -- DRAFTING_CYCLE.md` = EMPTY (no uncommitted changes) | ✅ |
| 2a | P4: on-disk builder digest `a9e4d099e11f213d` equals blob at its own commit (`f0ab037d`) | ✅ |
| 2b | Builder re-run from pre-edit blob: `BUILT: … edits=5 lines+1 bytes+4669 post=20/20`; `builder_exit=0` | ✅ |
| 2c | `cmp` of re-built output against live file: `BYTE_IDENTICAL` | ✅ |
| 2d | Refusal 1 (out == in): `BUILDER REFUSED: out == in`; exit 1 | ✅ |
| 2e | Refusal 2 (out under forbidden root): `BUILDER REFUSED: out is under a forbidden root …`; exit 1 | ✅ |
| 2f | Refusal 3 (already built): `BUILDER REFUSED: output tokens already present …`; exit 1 | ✅ |
| 2g | Refusal 4 (input missing): `BUILDER REFUSED: input missing: …`; exit 1 | ✅ |
| 3a | S1 — sentence phrase `ten REQUIRED fields` present; `plan_lint.py:552-555` defines `_STANZA_REQUIRED` with exactly ten fields; `:594`, `:596`, `:603` read three optional fields (`target_class`, `state_space`, `mutants`) — agree | ✅ |
| 3b | S2+D2 — sentence phrase `one of the FOUR values` present; `depositor.py:307-314` returns exactly four values (`read-only`, `shop-infra`, `register-writing`, `app-feature`); class_mismatch hold at `:173-178`; shop-infra hold at `:184-186` — agree | ✅ |
| 3c | S2+D2 — `governed-tooling` appears in sentence; `grep -rn governed-tooling --include='*.py'` over bellows → lint set (`:556`) and tests only; no production emitter — agree | ✅ |
| 3d | S4 — sentence phrase `compares ONLY the declared` present; `depositor.py:513-518` compares only `cycle_check=` token in `_rerun_validation`; `collision_type` at `:353` and `:362` (two writes, no reads, no tests name it) — agree | ✅ |
| 4 | P6 re-run on `executable-100026.md`: `plan_lint` exit 0 — PASS 9 / WARN 5 / FAIL 0 / INFO 1 / PIN-CHECK 6; `cycle_check` → `BAR_MET` — matches dev log baseline exactly; gates unchanged | ✅ |

**Gate note (pre-declared):** `qa_test_result` gate will pause — `probes-raw.txt` contains no pytest summary line. This is the pre-declared benign failure (plan 548's precedent, the 2.17 reconcile's own Step 2). The Planner overrides with `tools/clear_plan.py --override-gate 100027 2 qa_test_result`. Items 1–4 verify the substance independently.

---

## Follow-ups

- Threads 72 and 74 next (both target DC §2.7 — Item 1 would have halted if either had landed between the steps).
- The Planner pushes governance after the pause.
- Thread 67 closes at the keyboard on the read-back.

---

## Rule 20 — QA Self-Check Results

```
============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
Evidence folder: /Users/marklehn/Developer/bellows/.bellows-worktrees/100027/knowledge/qa/evidence/dc-manifest-sentence-2026-09-02/
Files verified: 1
```

