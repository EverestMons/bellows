verdict: continue
Rule 22 verification PASSED on `bellows/knowledge/research/deposit-exists-path-form-normalization-2026-05-27.md`. Diagnostic addresses all six questions with code citations, line numbers, and empirical audit of the three 2026-05-23 reproductions.

Substantive findings adopted:
- Root cause is abs-vs-rel path form mismatch, with two intertwined components: (A) missing normalization in `agent_declared` membership check at gates.py:271 and 278; (B) `_resolve_deposit_path` Strategy 0 cannot remap absolute paths to worktree because `os.path.join(wt_path, abs_path)` returns `abs_path` unchanged.
- Order-of-operations is correct: gates.check() runs at bellows.py:485 BEFORE _teardown_worktree at line 514. No race exists. The shop baton's gate-vs-teardown race hypothesis is overturned. Same misconception as 2026-05-10 reproduced.
- Fix shape is (a) pure normalization, ~25 LOC production + ~50 LOC tests, no order-of-operations change required.
- Canonical path form for the fix plan's `**Deposits:**` block is project-prefixed relative (`bellows/...`) to match the form agents declare in their Output Receipts, satisfying the LESSONS 2026-05-19 recursion-risk constraint.

CEO decisions: ship the fix as a combined executable covering both Component A and Component B. Add a LESSONS entry capturing the timing-ordering misconception recurrence pattern.

Authorized by CEO 2026-05-20.
