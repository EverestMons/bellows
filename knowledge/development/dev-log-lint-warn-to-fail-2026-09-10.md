# Dev Log — lint-warn-to-fail — 2026-09-10

Plan: executable-100064 | DEV step complete 2026-09-10 | [thread 265]

## Pins re-derived (P1, P3, P4, P8)

P1 (verbatim value cell from plan, the pre-edit (c) arm):

`scripts/plan_lint.py:466–470`: `if not str(qa_steps_raw).strip():` → `_undeclared_qa = [int(sn) for hl, sn in step_headers if "qa" in hl.lower()]` → `print(f"(c) WARN: step {_n} is QA-labeled but the plan declares no qa_steps — it will NOT be Rule 20/22 gated at dispatch (declare `qa_steps: {_n}`, or `none` if it is not a QA step)")`; sibling arms: `:450` (placeholder WARN), `:474` (unparseable WARN); the banner half: `:478–483` (`results.append(("PASS", "(c) QA banner pair", …))`); the exit: `:1261` `return 0 if all_passed else 1`; rows printed as `f"{status}: {check} — {detail}"`

P3 (run_checker seams, both tools): `scripts/close_cycle.py:33–39` and `scripts/lens_commit.py:64–70` both define `def run_checker(script, *args)` returning `(returncode, stdout+stderr)` via subprocess; `close_cycle._run_battery:143–145` called `run_checker("plan_lint.py", ...)`, checked rc, dropped out; `lens_commit` did not call plan_lint at all before this plan.

P4 (test files re-derived): `test_plan_lint_qa_steps_none.py` — 7 tests, `_make_plan(qa_steps_value, step_headers=None, banner=False)` / `_run_lint(plan_text)`; `test_close_cycle.py` — 6 tests, `_make_fixture(tmp_path)` / `_closing_file(tmp_path)`; `test_lens_commit.py` — 14 tests, `_make_lens_fixture(tmp_path)`. Both tool test fixtures' `_INITIAL_PLAN` texts lint to exit 0 with exactly two WARN lines: `WARN: no cycle_tier declared (DRAFTING_CYCLE.md §1/§3)` and `(f) WARN: Cycle Manifest stanza contains <declare> placeholder(s) — incomplete template`. `grep -cF 'WARN:' scripts/plan_lint.py` → 53 (plan pinned 37 at bellows `8ec3815`; the drift is from code added since then, not a mechanism change).

P8 (benign set verbatim): `depositor.py:50` and `tools/clear_plan.py:35` both read `_BENIGN_LINT_CHECK_LETTERS = {"c", "d"}`. Letter `y` is not in `{"c", "d"}` — confirmed by `git log -S'"(y)'` over `scripts/plan_lint.py` returning nothing (no history of a (y) letter). No mechanism mismatch on P1, P3, P4, P8.

## Failing-first (five red, then green)

Five new tests written before the three production edits:
1. `test_plan_lint_qa_steps_none.py::test_absent_qa_steps_with_qa_heading_and_banner_is_FAIL` — RED: lint exits 0 with WARN, not FAIL
2. `test_lens_commit.py::test_l12_plan_lint_warn_echo` — RED: tool prints no `plan_lint WARN —` line
3. `test_lens_commit.py::test_l13_plan_lint_fail_refuses` — RED: tool prints no `plan_lint FAIL —` line
4. `test_close_cycle.py::test_c7_plan_lint_warn_echo` — RED: tool prints no `CLOSE-WARN: plan_lint —` line
5. `test_close_cycle.py::test_c8_plan_lint_fail_battery_refuses` — RED: battery FAIL message has no (y) row text

4b guard (not a failing-first test — it is the guard keeping plan 306 in the suite): `test_plan_lint.py::test_lint_jkl_self_fire_zero_warnings` — assert swapped from `returncode == 0` to `returncode == 1` plus `all(l.startswith("FAIL: (y)") for l in ...)` guard; GREEN after both the assert swap and the plan_lint edit; all 147 other tests in test_plan_lint.py remained green throughout.

All existing tests in the four files remained green while the five new tests were red. After the three production edits (plan_lint.py, lens_commit.py, close_cycle.py): `2208 passed, 1 skipped` — the skip is `test_gate_watcher` (live-DB, skips in worktree). Full run confirmed clean twice (pre-commit check, post-commit verification).

## The corpus count (P7)

56 `executable-*.md` files in `knowledge/decisions/Done/` have a `## STEP N — QA` heading and no `qa_steps` field (measured 2026-09-10 at bellows `9447208`). These pre-date FO-2 and are never re-linted; their Done records stand.

```
cd knowledge/decisions/Done && for f in executable-*.md; do \
  grep -q '^## STEP [0-9]* — QA' "$f" && ! grep -q 'qa_steps' "$f" && echo "$f"; \
done | wc -l
```
Output: 56

## Mutation run

Manifest: `knowledge/mutants/lint-warn-to-fail.json` (5 mutants; HEAD `9447208` after the first DEV commit)

```
MUTANT wrong-letter-c: KILLED — suite caught the defect
MUTANT remove-fail-echo-lens: KILLED — suite caught the defect
MUTANT remove-warn-echo-lens: KILLED — suite caught the defect
MUTANT remove-fail-rows-close: KILLED — suite caught the defect
MUTANT remove-warn-echo-close: KILLED — suite caught the defect

MUTATION: 5 killed, 0 survived, 0 error
```
