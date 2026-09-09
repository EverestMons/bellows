# dev-log — closure claim and register coverage — 2026-09-09

Plan 100053: thread 213 (cycle_check closure check above empty-walk CONTINUE) and thread 215 (walk_register_lint COVERAGE verdict + SHAPE-OK/SHAPE-FAIL rename, closing thread 135). T1, three commits.

## Pins re-derived (P1, P2, P3, P6)

**P1 — cycle_check empty-walk branch** (`scripts/cycle_check.py` at bellows `612d6fe`):

```
463: if not walk_data:
488: [UNRESOLVABLE WARN — 28a08e5, stays]
499: _t0_ok, _t0_detail = _t0_close(text, blocks[0] if blocks else None)
513: # state-space cells that ratified the gap are flipped in the same commit.
514: if parsed["claims_closure"] and not parsed["has_unparseable"]:
517: _nw_verdict, _ = _apply_battery(plan_path, "CONTINUE", warnings, battery=battery)
518: return _nw_verdict, 0
632: if parsed["claims_closure"] and verdict == "CONTINUE" and not parsed["has_unparseable"]:
```

After Item 3 (213 implementation): the closure check at :514 is inserted AFTER the T0 arm (:499) and BEFORE the `_nw_verdict` CONTINUE return (:517). The `:513` comment replaces the old "DELIBERATELY LEFT OPEN / RATIFIED" block (8 state-space cells). The original check at :632 is unchanged (non-empty-walk path).

**P2 — state-space table** (`tests/test_cycle_check.py`):

```
787: _WALK_DIM = [
788:     "none",  # no walk lines — CONTINUE unless closure claimed (ruling 213)
812: #  2. none walk + claim close → ESCALATE:claimed-close-unmet (ruling 213)
813: #     none walk + non-claim close → CONTINUE
```

143 tests collected in test_cycle_check.py (80 parametrized state-space cells + standalone tests). `test_state_space_table_complete` verifies all 80 cells present. The 8 cells `_w == "none" and _c in claims` flipped from CONTINUE to ESCALATE:claimed-close-unmet.

`grep -rn 'split("\\t")' scripts/ tools/ tests/ | grep -i regist` — result:

```
tests/test_register_coverage.py:277:# Test 9 — stderr line format: SHAPE-OK, COVERAGE field, split("\t")[1]
tests/test_register_coverage.py:295:    parts = lines[0].split("\t")
tests/test_register_coverage.py:313:    assert lines2[0].split("\t")[1] == "SHAPE-FAIL", lines2[0]
```

No test asserts the field COUNT of the stderr line. `split("\t")[1]` appears in `run_check` only (reading the status column — unaffected by the new COVERAGE field at position 3).

**P3 — the lint and its consumers:**

Token constants in `scripts/walk_register_lint.py`:
```
18: STATUS_CONFORMANT = "SHAPE-OK"
19: STATUS_UNCONFORMANT = "SHAPE-FAIL"
20: STATUS_SHAPE_OK = STATUS_CONFORMANT    # alias for new code
21: STATUS_SHAPE_FAIL = STATUS_UNCONFORMANT
```

Consumers of the token (by effect):
- `tools/run_check.py:65-76` — `judge_register`: `"\tSHAPE-FAIL"`, `"\tNO_TABLE"`, `"\tCOVERAGE: INCOMPLETE"` on stderr; `split("\t")[1]` for the label
- `scripts/substrate_check.py:80` — compares to `walk_register_lint.STATUS_CONFORMANT`; `:117` says "SHAPE-OK"
- `scripts/cycle_check.py:29,33` — imports `STATUS_CONFORMANT as _REG_CONFORMANT`; comment re-worded to "SHAPE-OK"
- `.githooks/pre-commit` — reads stdout column 4 (`$4!="OK"`), comments only; hook unchanged

**P6 — tests:**

| file | def test_ count | collected |
|------|----------------|-----------|
| tests/test_walk_register_lint.py | 45 | 45 |
| tests/test_run_check.py | 18 | 18 |
| tests/test_substrate_check.py | 8 | 8 |
| tests/test_cycle_check_register_resolver.py | 6 | 6 |
| **total** | **77** | **77** |

## Failing-first (the sibling and the two rewritten files red, then green)

**Item 2 — 213 tests written first (red before Item 3):**

`tests/test_cycle_check_empty_body_silence.py`: the existing `test_claiming_closure_with_an_empty_body_stays_CONTINUE_by_RATIFIED_precedence` was REWRITTEN as `test_claiming_closure_with_an_empty_body_ESCALATES_by_ruling_213` (expects `ESCALATE:claimed-close-unmet`; was CONTINUE). New test `test_T0_claiming_closure_without_a_result_ESCALATES` added (T0 + closure claim + no result → ESCALATE; T0 + closure claim + result → BAR_MET).

`tests/test_cycle_check.py`: rule 2 of `_EXPECTED` rewritten — 8 cells flipped from CONTINUE to ESCALATE:claimed-close-unmet.

Red before Item 3: the rewritten characterisation test and the new T0 test FAILED; the 8 flipped cells FAILED. 10 failures.

After Item 3 (the empty-walk closure check inserted): all 143 tests in test_cycle_check.py and all 4 in test_cycle_check_empty_body_silence.py green.

**Item 6a — 215 tests written first (red before Item 6):**

`tests/test_register_coverage.py` (new sibling, 11 tests for `coverage_verdict`): tests 1–9 and 11–12 RED before Item 6's implementation. Test 10 (stdout byte-identity) GREEN by construction — it was built from `main`'s actual output on the fixture after Item 5's commit.

Token literal edits in `tests/test_walk_register_lint.py` (28 literals: CONFORMANT → SHAPE-OK, UNCONFORMANT → SHAPE-FAIL) and `tests/test_run_check.py` (20 literals) turned both files RED before Item 6.

After Item 6 (215 implementation): `tests/test_register_coverage.py`, `tests/test_walk_register_lint.py`, and `tests/test_run_check.py` all green. Full suite: 2144 passed, 1 skipped.

After fixup commit (M8 kill target `test_judge_register_new_token_logic` added): 2145 passed, 1 skipped.

## Mutation runs (three manifests)

**Manifest A** (`target: scripts/cycle_check.py`, HEAD `54e8b850`, run immediately after Item 5 commit):

```
MUTANT M1-delete-ruling-213-check: KILLED — suite caught the defect
MUTANT M2-check-before-T0-arm: KILLED — suite caught the defect
MUTATION: 2 killed, 0 survived, 0 error
```

**Manifest B** (`target: scripts/walk_register_lint.py`, HEAD `410bcd0b`, run immediately after Item 7 commit):

```
MUTANT M3-rows-must-equal-declared: KILLED — suite caught the defect
MUTANT M4-highest-walk-judged: KILLED — suite caught the defect
MUTANT M5-undeclared-becomes-covered: KILLED — suite caught the defect
MUTANT M6-status-conformant-reverted: KILLED — suite caught the defect
MUTANT M7-panel-rows-counted-as-walk-1: KILLED — suite caught the defect
MUTATION: 5 killed, 0 survived, 0 error
```

**Manifest C** (`target: tools/run_check.py`, HEAD `df6acd35`, run after M8 kill target added):

```
MUTANT M8-judge-register-ignores-incomplete: KILLED — suite caught the defect
MUTATION: 1 killed, 0 survived, 0 error
```

All eight mutants killed; 0 survived, 0 error across three manifests.

## Corpus replay

P5 (pre-change measurement): of 193 plans with a Drafting Cycle block (bellows Done, governance drafts and Done), ONE has a closure claim with empty `walk_data`: `executable-432.md`, already `ESCALATE:unparseable` (the unparseable check precedes the new one). Thread 158's "0 plans" holds: the change flips nothing live.

**213 replay (post-change):** 400 plans scanned (bellows Done + governance drafts and Done), 125 with a DC block. Plans with closure claim + empty `walk_data`:

```
executable-432.md (already ESCALATE:unparseable)
```

Confirms: the new check fires for 0 net plans. `executable-432.md` was already ESCALATE; no plan in the corpus reaches the new check.

**215 replay (post-change):** 186 registers in governance/knowledge/research scanned by `coverage_verdict`.

```
COVERED:    22  (register has a resolvable plan with lens lines; all completed walks ≥ declared folds)
INCOMPLETE:  3  (real coverage gaps detected: walk-register-gate2-347-2026-08-14.md w1 rows=0 declared=1;
                  walk-register-threads-retype-2026-09-07.md w0 rows=0 declared=4;
                  walk-register-threads-retype-2-2026-09-07.md w0 rows=0 declared=5)
UNDECLARED: 161 (no Draft: line, plan not resolvable, or plan declares no lens walks)
```

The 3 INCOMPLETE registers are genuine coverage gaps — the tool correctly identifies them. The pre-change P4 measurement (walk 0 of this plan) found "every completed walk COVERED" over the 9 that resolved at that time; the corpus grew between walk 0 and the replay. None of the COVERED registers are newly broken.

## Cost

Largest September register: `walk-register-cycle-check-battery-2026-09-07.md` (24,880 bytes, 7 completed walks, 44 fold rows).

Three runs with `coverage_verdict` monkeypatched to stub ("UNDECLARED") vs three runs with real implementation:

| mode | run 1 | run 2 | run 3 | median |
|------|-------|-------|-------|--------|
| before (stub) | 5.6 ms | 5.6 ms | 4.9 ms | **5.6 ms** |
| after  (real) | 4.7 ms | 4.6 ms | 4.4 ms | **4.6 ms** |

Delta: −1.0 ms (within noise; plan resolution and fold-table scan add negligible overhead on a 24 KB register). No performance regression.
