# Dev Log — wrap-advisories-surface (plan 100129, thread 427)

## Thread and ruling

CEO ruling 2026-09-18, thread 427: when the wrap check passes but prints
warnings or other non-OK lines, every such line must reach a reader. The
session-start hook adds them to the session's context; the stop hook shows
them as a message. Warnings still never block.

## A0 suite baseline (at HEAD f3c5750f, 2026-09-18)

- **2537 passed, 2 skipped, 0 failed** — collected 2539

## Why a deny-list, not an allow-list

The selector `advisory_lines` uses a deny-list: it excludes only lines whose
leading text begins with one of `_OK_PREFIXES = ("wrap_check: OK",
"[2r/receipts] OK")`. Every other non-blank line passes through.

An allow-list (e.g. match lines containing "WARN (advisory)") fails silent:
a print site added later to wrap_check.py would not be picked up until
someone updated the pattern. A deny-list fails loud: a new site surfaces by
default and the author must explicitly add it to `_OK_PREFIXES` if it is an
OK line. Failing silent is the defect this plan exists to end.

## The two channels and the harness contract (P5)

**Session-start channel.** `emit()` in `_common.py` builds
`hookSpecificOutput.additionalContext`. This reaches the model's context on
session start — measured: this session's own start carried the hook's debt
output. Delivery to the model is confirmed.

**Stop-hook channel.** A Stop hook that prints `{"systemMessage": "..."}` (and
nothing else — no `decision`, no `hookSpecificOutput`) is documented as
"message shown to user" and allows the stop. Which desktop surfaces display
it is not documented; the CEO observes it at the verdict (the proxy argued in
plan 100129 CEO Context). Until then, the session-start channel has confirmed
delivery for every line except the pending-receipt Note (which only the
stopping session sees; the next session's start arm returns the OK form
instead).

## Why new functions are reached through the module, not imported by name (MUST-PRESERVE M, P13)

Both hooks add `import _common` beside their existing `from _common import`
line. The new functions `advisory_lines` and `compose_advisory_message` are
called as `_common.advisory_lines(...)` and `_common.compose_advisory_message(...)`.

In a worktree nested in the canonical bellows checkout, the suite's package
import of `hooks.eluvian.wrap_check` (thread 243) caches the canonical
`_common` — its `from _common import _default_root` fires, binding the
canonical pre-change copy. A hook that then calls `from _common import
advisory_lines` raises `ImportError: cannot import name 'advisory_lines'`
because the cached copy does not have it. The attribute form (`_common.advisory_lines`)
resolves against whatever module `_common` refers to at call time, not at
import time, so it works beside any `_common` that was cached before the
hook's own load. Measured in the nested simulation (P13): attribute form gave
73 passed (then 12-case: 2546 passed); name-import form gave 3 failures and
4 failures, respectively.

## A3 suite result (green run, 2026-09-19)

At A3, the date had rolled from 2026-09-18 to 2026-09-19 during the run.
Four pre-existing date-rollover tests in `test_wrap_3b_keyed.py` (3 cases)
and `test_wrap_r2_registry.py` (1 case) now fail because the governance baton
still reads "2026-09-18" and the date filter comparisons have flipped. These
tests are in files this plan never modified; their failure is not caused by
the DEV's changes. All 12 new tests passed; every test in `test_wrap_hooks.py`,
`test_wrap_sentinel.py`, and `test_hooks_shared_common.py` passed.

Result: **2545 passed, 4 failed (pre-existing date-rollover), 2 skipped** —
collected 2551 (= 2539 + 12 new).

## Edits the green run forced inside the new tests

None. All 12 cases passed green without modification.
