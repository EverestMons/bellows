verdict: continue

exec-490 step 1 (DEV) — implement plan_lint check-(f) final-walk class-split parse + 5 test rows (honing unit c). Paused on `header_pause` (clean); continue proceeds to STEP 2 (QA).

Gate ALL-PASS (Gate Result Passed: True; failures: []; files_changed: scripts/plan_lint.py, tests/test_plan_lint.py). file_change_audit PASS (2 files); scope_check PASS (within plan scope). No fork.

Planner-verified facts (direct read of the DEV commit `0dbdcd1` + a targeted test run at that commit, not the agent summary):
- **The check-(f) implementation matches diag-489 §3 faithfully:** it now collects ALL lens lines (not just the last); detects class-split via `instruction\s+(\d+)\s*/\s*record\s+(\d+)`; on the class-split path it strips parentheticals (the `(W1 = …)` trap), finds `max_walk` across all lens lines, splits each line into per-walk segments on `;` AND `.\s+(?=w\d)` (the `. ` delimiter 464 uses), sums instruction ONLY on each lens's max-walk segment (with the conservative +1 for a fold lacking a class split, per §3d), and WARNs iff the sum > 0; when NO lens line carries `instruction N` it falls back to the UNCHANGED last-lens heuristic (`lens_lines[-1]`). The WARN message string is retained verbatim and the check stays WARN-first (exit 0). The adjacent no-Closing WARN + checks (g)/(h) are untouched (edit bounded to L365-388 as directed).
- **The 5 test functions exist, 1:1 with the matrix:** `test_lint_cycle_classsplit_{false_clean_now_warns, judged_stop_silent, legacy_arrow_silent, dry_only_silent, multi_segment_regression_silent}`.
- **Targeted suite green at the DEV commit:** `pytest tests/test_plan_lint.py -k cycle` = **27 passed** (22 existing cycle tests + 5 new; 106 deselected) — the fallback preserves the existing surface and the 5 new rows pass.
- DEV committed in the worktree (`0dbdcd1`), targeted-only per [[dev-step-no-full-suite]]; the FULL 133-suite + the corpus-regression scan run in STEP 2 (QA).
