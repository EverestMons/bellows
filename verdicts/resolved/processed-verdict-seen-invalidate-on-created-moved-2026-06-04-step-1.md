verdict: continue

Step 1 (DEV) verdict. All Bellows gates PASS — failures=[], scope_check clean (tests/test_bellows.py named in Deposits), file_change_audit 4 files, no hidden worktree_teardown failure (teardown succeeded; DEV commit d5fd9c9 landed on main). rule_20/rule_22 N/A (not a QA step). Per Rule 25 the Planner performs the (b) substance check only.

(b) substance check PASS:
- Helper _invalidate_seen_on_redeposit implemented with the lifecycle-prefix guard ("in-progress-", "verdict-pending-", "halted-") verbatim; early-returns on lifecycle, else discards the slug from _seen only when present.
- All three watcher callbacks call the helper before _handle (on_created on src_path, on_modified on src_path, on_moved on dest_path); on_modified refactored to behaviorally identical invalidate-then-handle.
- bellows.py diff is a single hunk confined to the callback region — _handle and the rescan path byte-unchanged, so the rescan-dedup loop risk is avoided.
- Four new tests present (on_created/on_moved x invalidate/lifecycle) all PASS; the two existing on_modified parity tests PASS unchanged.
- pytest 444 -> 448 passed, same 5 carry-over, zero new failures.

Proceed to Step 2 (QA). Not terminal — QA is code-level only and pauses for terminal verdict before Done/.
