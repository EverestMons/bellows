# bellows — CORRECTIVE to 513: teach the pre-existing test fixtures the admission law

**Date:** 2026-08-24 | **Project:** bellows | **Tier:** Small | **Dispatch Mode:** bellows | **cycle_tier:** T1 | **Test Scope:** full suite (bellows) | **Execution:** Step 1 (DEV) → Step 2 (QA) | **qa_steps:** 2 | **known_failures:** 0 | **Priority:** 1

**auto_close:** false
**pause_for_verdict:** always

**Depends on:** halted `513` (stop verdict `verdict-513-step-3.md`) — DEV-A `4fdf55a` + DEV-B `936ef5e` stay committed and UNREVERTED on main (`8375058`); this plan repairs the SUITE, not the code. The 40-failure census: `knowledge/research/pytest_full.txt` sha `20765e662442b96eaec08978a20e3319cbbc330b193dfeb1c0093e957dafccc8` — 38 in `tests/test_bellows.py`, 1 each in `tests/test_consume_verdicts.py` and `tests/test_gate_transaction_mechanization.py`, all one diagnosis: fixtures deposit claimable-named plans and expect dispatch with NO clearance record. Corrective precedent: 507/509 (same-day, same grammar).

## Why this exists
The admission flip is the law now; 40 pre-existing tests predate it. Their refusals are the code WORKING — the fixtures must obey the law the way real deposits do, not the law bend for them.

## What this plan does NOT do
- **No production-code change.** `bellows.py`/`depositor.py`/`lifecycle.py`/`gates.py`/`plan_lint.py`/`tools/` are byte-stable — asserted by diff in QA.
- **No blanket auto-clear in tests.** ⚠️⚠️ The helper is OPT-IN at explicit call sites; an autouse fixture that clears everything would silently gut the flip's own negative tests (no_clearance refusals, drift, replay) — the CONTROL arm below proves it didn't happen.
- **No re-litigation of 513's design.** The corrections stand; the daemon stays on old code until the post-close activation.

## Numbers discipline
| id | pin | value | probe |
|---|---|---|---|
| F1 | failures BEFORE | **40** (38/1/1 by file) | pytest_full.txt (sha above); RE-RUN the three suites first and confirm the same set — yours supersede |
| F2 | suite totals BEFORE | 40 failed / 1248 passed | same file, tail line |
| F3 | bellows main | `8375058` | `git rev-parse`; HALT on mismatch |
| F4 | flip negative tests | test_admission_flip.py contains the refusal cases (no-record, drift, consumed, replay) | `grep -c` them; they are the control arm and must remain UNTOUCHED and passing |

## Drafting Cycle
**Tier:** T1 — corrective, tests-only. **Walks:** walk 0 pinned; walk 1 under v2.13; close at dry.
**Direction verdict (after walk 1):** owed.
**Cold panel: DECLINED with reasoning** — tests-only corrective implementing an enumerated stop verdict; the control arm is mechanical; the highest-risk failure (blanket auto-clear) has a named detector.
**Conformance (§5):** per lens from walk 1.

## Cycle Manifest
tier: T1
target: tests/test_bellows.py
class: governed-tooling
reads: /Users/marklehn/Developer/GitHub/bellows/knowledge/research/pytest_full.txt, /Users/marklehn/Developer/GitHub/bellows/lifecycle.py
writes: tests/conftest.py, tests/test_bellows.py, tests/test_consume_verdicts.py, tests/test_gate_transaction_mechanization.py
open_forks: none
walks: 0
yields: (owed)
validation: (owed)
coherence: N/A — the emitter's sentinel; NOT hand-filled
N/A

## MUST-PRESERVE
- ⚠️ **OPT-IN helper only** — `clear_plan_for_test(path, db_path)` in conftest: raw `read_bytes` hash, `lifecycle.write_clearance(...)` storing the CLAIMABLE path, `cleared_by='test'`. Called explicitly at deposit points; NEVER autouse, NEVER inside a shared fixture that the negative tests also use.
- ⚠️ Tests stay in tmp dirs/DBs; no real watched path.
- ⚠️ **EVERY DATE IS A FIXED LITERAL.** grep is ugrep: `-F`.
- ⚠️ DEV runs the three affected suites only; the full suite belongs to QA.

## STEP 1 — DEV
**Role:** DEV. `<id>` from your plan filename.
**A0:** assert F1–F4 (re-run the three suites; the failing set must match the census — yours supersede with a statement). Three-way start: 40 failing → proceed; 0 failing with the helper present → ALREADY APPLIED no-op success; else → STOP with inventory.
**A1:** add the conftest helper per MUST-PRESERVE; apply at each failing test's fixture/deposit point — prefer the SHARED deposit helpers the 38 flow through (read the fixtures first; edit the fewest sites that cover all 40). Where a test's SUBJECT is admission refusal, do not touch it (F4).
**A2:** run the three suites; paste raw; expect the 40 green and the admission-flip suite untouched-and-green.
**A3 commit** (worktree): `git add tests/ && git commit -m "[<id>] fixtures learn the admission law: opt-in clear_plan_for_test at deposit points"`
⚠️ Failure disposition: no commit, no revert, no retry; report + Flags.
**Deposits:**
- `/Users/marklehn/Developer/GitHub/bellows/tests/conftest.py`
- `/Users/marklehn/Developer/GitHub/bellows/tests/test_bellows.py`
- `/Users/marklehn/Developer/GitHub/bellows/tests/test_consume_verdicts.py`
- `/Users/marklehn/Developer/GitHub/bellows/tests/test_gate_transaction_mechanization.py`

**Scope:**
- `/Users/marklehn/Developer/GitHub/bellows/tests/conftest.py`
- `/Users/marklehn/Developer/GitHub/bellows/tests/test_bellows.py`
- `/Users/marklehn/Developer/GitHub/bellows/tests/test_consume_verdicts.py`
- `/Users/marklehn/Developer/GitHub/bellows/tests/test_gate_transaction_mechanization.py`

## STEP 2 — QA
**Role:** QA. Fresh agent; re-measure.
**B1:** full suite; RAW to `pytest_full.txt` — ⚠️ **FIRST copy the 513 census aside as `pytest_full_513_red.txt` in the same dir and commit it with your deposits: the overwrite is intended (rolling truth) but F1's sha-pinned census must survive as evidence, and an overwrite without the copy destroys the halted plan's primary exhibit.** Then assert **0 failed / 0 errors**, report the total (1288 collected at 513's baseline growth).
**B2:** production byte-stability: `git diff <F3>..HEAD -- bellows.py depositor.py lifecycle.py gates.py scripts/plan_lint.py tools/` is EMPTY.
**B3 — the CONTROL arm:** the flip's negative tests each still PASS as refusals — name them from F4's grep and quote their pass lines; then prove the helper is opt-in: `grep -c "autouse" tests/conftest.py` unchanged from F3's value, and `clear_plan_for_test` absent from every negative test's body.

> **QA SELF-CHECK — Rule 20.** Post the block from `/Users/marklehn/Developer/GitHub/RULE_20_SELF_CHECK_BLOCK.md` verbatim, under the banner **`Rule 20 — QA Self-Check Results`**, and close with **`PASSED — SELF-CHECK PASSED`** only if every check genuinely passed. ⚠️ Both literals are matched by `plan_lint` check (c). Results in the `.md`; raw suite in `pytest_full.txt`.

**Deposits:**
- `/Users/marklehn/Developer/GitHub/bellows/knowledge/research/e2-fixtures-qa-2026-08-24.md`
- `/Users/marklehn/Developer/GitHub/bellows/knowledge/research/pytest_full.txt`
- `/Users/marklehn/Developer/GitHub/bellows/knowledge/research/pytest_full_513_red.txt`

**Scope:**
- `/Users/marklehn/Developer/GitHub/bellows/knowledge/research/e2-fixtures-qa-2026-08-24.md`
- `/Users/marklehn/Developer/GitHub/bellows/knowledge/research/pytest_full.txt`
- `/Users/marklehn/Developer/GitHub/bellows/knowledge/research/pytest_full_513_red.txt`
**Commit:** `git add knowledge/research/e2-fixtures-qa-2026-08-24.md knowledge/research/pytest_full.txt knowledge/research/pytest_full_513_red.txt && git commit -m "[<id>] qa: fixture corrective — suite green"`
