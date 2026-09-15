# dev-log — cycle-check-baseline-368 — 2026-09-15

## Pins re-derived (P1, P4)

P4 (verbatim): `tests/test_cycle_check.py`: 143 tests, 1264 lines, a newline at its end; `_MANIFEST_STANZA` :43 (tier, target, class, reads, writes, open_forks, walks … — no `fold_baseline:` line, so `_make_plan`'s plans are undeclared and resolve beside); `_make_plan` :58; `test_assert_fail_3` :125–140, its mock log `abc1234 [draft] w1 fold` / `abc1235 deposit(cycle-check)`; `test_uncommitted_walk` :359–380; `test_assert_3_baseline_exists` :558–578, the sibling baseline `.plan.md.foldcheck.json`, `check_assert_3(parsed, plan, True)` → `PASS`; the six sibling files `test_cycle_check_battery.py`, `_coherence_basis.py`, `_empty_body_silence.py`, `_manifest_provenance.py`, `_register_resolver.py`, `_t0_close.py`; `tests/test_clear_plan_override.py` (its `test_override_gate_tool_writes_all_matching_rows` fails only under a temporary-directory tree — `clear_plan.py:178–179` refuses a `--ref` under `/tmp`, `/private/tmp` or `/var/folders`; a worktree under the checkout passes it)

P1 re-derived (sed -n '356p;369,379p;527,541p;771,847p' scripts/cycle_check.py against HEAD):
- :356 `pat = re.compile(r"drafting\(|\[draft\]")  # a deposit( commit is not a walk (thread 368)` — CHANGED (was `|deposit\(`)
- :369–379 `check_assert_3` — CHANGED: docstring updated, sibling lookup replaced by `baseline_path, _declared = resolve_fold_baseline(plan_path)` / `if baseline_path is None:`
- :527 `a3 = check_assert_3(parsed, plan_path, a2_git)` — UNCHANGED
- :771–847 `_resolve_register_ref` / `resolve_fold_baseline` — UNCHANGED; `resolve_fold_baseline(plan_path)` appears once in the checker (check_assert_3)

No mechanism mismatch on P1 or P4.

## Failing-first (red, then green)

Red (unedited checker, -k t368): `3 failed, 143 deselected in 0.31s`

Green (after two-site edit):
- Three: `3 passed, 143 deselected in 0.26s`
- File: `146 passed in 6.97s`
- Full suite: `2445 passed, 2 skipped, 9 warnings in 234.48s`

## The gate observed (t1, t2, t3)

```
tests/test_cycle_check.py::test_t368_assert_3_reads_the_declared_baseline PASSED [ 33%]
tests/test_cycle_check.py::test_t368_a_deposit_commit_is_not_walk_history PASSED [ 66%]
tests/test_cycle_check.py::test_t368_a_declared_baseline_that_does_not_resolve_never_falls_back PASSED [100%]
```

## Mutation run

MUTATION: 3 killed, 0 survived, 0 error
