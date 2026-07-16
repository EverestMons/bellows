verdict: continue

**Rule 22(b) verified independently by the Planner — not taken on the agent's word.**

## Substance checks performed against the REAL bug (not just the agent's tests)

Re-parsed `git show e57a22b^:LESSONS.md` (pre-corruption state) against current LESSONS.md under the new code — the exact byte delta that caused the corruption:

- **Hash now STABLE across the 7-byte separator delta:** `3ef6407b` == `3ef6407b`. Before the fix this flipped `4ff4c905` -> `b9875afa`. **The root cause is dead.**
- **`raw_content` still stored verbatim** — entry 137's body still ends `...ine`\n\n\n---\n\n`. Normalization did not leak into storage, so the classifier still reads the true body.
- **Real edits are still caught** — a substantive body change still flips the hash. The fix does not blind genuine edits.

## Gates + tests

All 11 mechanical gates PASS; exactly the 3 scoped files touched. Suite **52 -> 61 passed, 0 regressions**. All six required test shapes present, including `test_terminal_status_guard` parametrised across all four terminal statuses and `test_trailing_separator_only_delta_zero_stales` (the catastrophic case asserted directly).

Code inspected directly: `_normalize_for_hash` strips only trailing blank lines and `^[ \t]*-{3,}[ \t]*$` separator lines; the stale UPDATE now carries `AND status NOT IN ('implemented','reference','rejected','superseded')`, and terminal-status proposals on a genuinely-changed entry are collected into `terminal_proposals_flagged` and surfaced through `run_full_lessons_cycle` rather than silently ignored.

## Accepted residual (no action)

The dev-log asserts the `---` pattern "never appears in real lesson prose." A body ending in a fenced code block whose final line is `---` would have it stripped. This is **hash-input only** — storage and classification are untouched — so the blast radius is a missed hash-flip on an exotic trailing-code-fence edit. Acceptable; not worth widening the fix.

## Proceed to Step 2 — WITH THE LOAD-BEARING CONSTRAINT IN FORCE

Step 2 mutates the canonical DB and is the dangerous step. The measured hazard stands: **all 83 parsed entries change hash under normalization, and a naive re-hash would stale 79 proposals (64 `implemented`).** Step 1's terminal-status guard is now a real second line of defence — but it is a backstop, NOT a licence to route the backfill through `ingest_lesson_entries`. Direct SQL on `content_hash` only, per the plan. Back up first (Task A). The Step 3 QA row is explicit: if `implemented` lands anywhere near 33, the constraint was breached — halt loudly.
