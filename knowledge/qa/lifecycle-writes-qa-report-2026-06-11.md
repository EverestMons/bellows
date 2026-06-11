# QA Report — Lifecycle DB Transition Writes (Executable B)

**Date:** 2026-06-11
**Plan:** Reporting Phase 1, Executable B
**Step:** 2 (QA)
**DEV Commit:** 4667e0b

---

## Verification Table

| # | Item | Method | Evidence | Result |
|---|------|--------|----------|--------|
| 1 | Schema completeness + DDL conformance + upgrade-in-place | Created A-era temp DB (id_sequence + plans only, seeded plans row), ran `init_lifecycle_db()`, dumped `sqlite_master`, compared column-by-column against blueprint 3.4 | All 10 tables present (id_sequence, plans, diagnostic_meta, executable_meta, derivations, steps, commits, deposits, verdicts, gate_events). Seeded row intact (title='Seeded Row', state='closed'). id_sequence.next_id preserved at 5. No BLOB columns anywhere. All column names/types match blueprint VERBATIM. `steps.id` is surrogate PK (AUTOINCREMENT). `step_id` FK references confirmed in commits, deposits, gate_events. `UNIQUE(plan_id, step_number)` on steps confirmed. `UNIQUE(executable_id, diagnostic_id)` on derivations confirmed. No composite PK on steps. | **PASS** |
| 2 | Full-lifecycle write integration | (a) Ran DEV's 3 integration tests: `test_lifecycle_writes_auto_close_flow`, `test_lifecycle_writes_verdict_pause_flow`, `test_lifecycle_meta_and_derivations_at_claim` — all passed. (b) Independent scratch simulation: claim→step start→step end→verdict request→verdict consumed→step 2 start→step 2 end→commits→close — all 7 boundaries verified with correct FKs, cost/turns/duration populated in steps, gate_events with reason codes (7 gates per step incl. 'fail' with evidence), deposits with landed flags, verdicts with pending→continue transition, commits with SHAs, plans.closed_at set. | **PASS** |
| 3 | Log-and-continue contract | Pointed `LIFECYCLE_DB_PATH` at read-only DB file (chmod 0o400). Invoked all 9 write helpers: record_step_start, record_step_end, record_gate_events, record_deposits, record_commits, record_verdict_request, record_verdict_outcome, record_meta, record_derivations. All returned without raising; each logged `[WARN] [lifecycle] ... attempt to write a readonly database`. | **PASS** |
| 4 | Derivations parsing | Case 1 (numeric id): `"implements diagnostic 42"` → `[42]`. Case 2 (legacy slug): `"implements diagnostic foo-bar-2026-06-10"` → `[]` (correct — slug not resolvable to int). Case 3 (no citation): `"no diagnostic reference"` → `[]`. | **PASS** |
| 5 | Boundary discipline | Diffed Exec A commit (0f0d4fd) → Exec B commit (4667e0b). All bellows.py removals are: (a) return-value captures for `verdict.post_verdict_request` (now `_vr_path = ...`), (b) `_teardown_worktree` return-type change (`-> None` to `-> list`), (c) `current_step` assignment moved before `run_step` call (reorder, same value). No gate conditions, verdict matching, or file-move control flow altered. verdict.py and runner.py: zero diff. A-era mint/claim tests (TestMintMonotonicity, TestMintAtomicity, TestMarkPlanState, TestRecoverHalfClaimed): all 9 passed unchanged. | **PASS** |
| 6 | Full suite under wall-clock bound | `pytest tests/ --tb=line` — 516 passed, 0 failed, 9s wall-clock. Matches DEV run (516 passed, 9.32s). No new failures. DEV baseline was 480→516 (+36 new tests); QA run confirms 516. | **PASS** |
| 7 | Live-DB safety | Production lifecycle.db at `/Users/marklehn/Developer/GitHub/bellows/lifecycle.db`: mtime=1781210218 (epoch) before and after all QA runs. Row counts: plans=3, next_id=4 — unchanged. Tables in live DB: id_sequence, plans only (A-era; B tables activate on daemon restart). No test or scratch step wrote the production DB. | **PASS** |

---

## Suite Count Reconciliation

| Run | Passed | Failed | Duration |
|-----|--------|--------|----------|
| DEV (Step 1) | 516 | 0 | 9.32s |
| QA (Step 2) | 516 | 0 | 8.96s |

Delta: 0 new failures. Count matches exactly (516 = 480 baseline + 36 new tests from Exec B).

---

## Rule 20 — QA Self-Check Results

PASSED — SELF-CHECK PASSED

Verification items 1–7 all PASS. Schema matches blueprint 3.4 VERBATIM (table names, column names, key strategy including `steps.id` surrogate PK and `step_id` FK indirection). No control-flow changes to dispatch/gating. Log-and-continue contract holds for all 9 write helpers. Full suite green at 516. Live DB untouched.

---

## Output Receipt
**Agent:** Bellows QA
**Step:** 2
**Status:** Complete

### What Was Done
Executed 7 verification items with full evidence capture: schema completeness + DDL conformance, full-lifecycle write integration (DEV tests + independent scratch simulation), log-and-continue contract on read-only DB, derivations parsing (3 cases), boundary discipline diff analysis, full test suite (516 passed), and live-DB safety confirmation.

### Files Deposited
- `bellows/knowledge/qa/lifecycle-writes-qa-report-2026-06-11.md` — this QA report
- `bellows/knowledge/qa/pytest_full_lifecycle_writes_qa.txt` — full pytest output

### Files Created or Modified (Code)
- None (QA verification only — no code edits)

### Decisions Made
- Confirmed DDL matches blueprint 3.4 verbatim — no deviations found
- Confirmed all boundary writes are additive (no existing control flow altered)

### Flags for CEO
- None

### Flags for Next Step
- None
