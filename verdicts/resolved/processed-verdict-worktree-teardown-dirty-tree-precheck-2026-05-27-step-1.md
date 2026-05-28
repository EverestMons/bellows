verdict: continue
Rule 22 (b) substance check PASS on Step 1 (DEV). Verified by reading the commit diff (6252f8c) directly and running the targeted suite.

Production (bellows.py, +41):
- Pre-check inserted at (b2), between index.lock cleanup and the (c) cherry-pick loop. Correct location — last point before any cherry-pick attempt.
- cwd=project_path (main checkout, NOT wt_path). Correct — this is the primary regression risk and it is implemented right.
- Dirty predicate: returncode == 0 and stdout.strip() non-empty. Correct per decision (1a).
- fail-open implemented correctly with non-obvious ordering: `except WorktreeTeardownError: raise` precedes `except Exception: log+proceed`, so the intentional dirty-tree raise is not swallowed by the fail-open catch. A naive single except would have eaten the raise. Good.
- Evidence string leads with `worktree_teardown_dirty_tree:` so the distinct gate code surfaces in the verdict request without modifying the three caller sites — the simpler approved approach. Contains dirty-file listing, 10-line truncation, both recovery sub-variants, LESSONS.md 2026-05-27 pointer.

Tests (tests/test_bellows.py, +107, 4 new):
- test_teardown_pauses_when_local_main_dirty, test_teardown_proceeds_when_local_main_clean, test_teardown_dirty_tree_evidence_contains_recovery_commands, plus the optional test_teardown_proceeds_when_git_status_errors (fail-open coverage).
- Planner ran `pytest -k teardown -q`: 9 passed (4 new + 5 existing), 113 deselected, 0.20s. Existing teardown tests survived the pre-check (their stdout="" fixtures read as clean, as SA predicted).

LOC came in at 148 total (41 prod + 107 test) vs SA's ~65 estimate — the overage is entirely test thoroughness, not production scope. Acceptable.

Proceed to Step 2 (QA) for independent verification + adjacent-suite run.
