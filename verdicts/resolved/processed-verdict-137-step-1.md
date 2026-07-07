verdict: stop

Duplicate dispatch. Plan 137 is byte-identical to plan 138 (same deposit, `executable-plan-lint-qa-steps-cross-check-2026-07-07.md`) — one authored plan claimed under two IDs. Keeping 138 as the survivor; stopping 137 to avoid two worktrees (wt/137, wt/138) racing to merge the same files into main. Not a quality issue — 137's DEV step completed clean. The double-claim mechanism itself is being characterized by a dispatched diagnostic (single daemon confirmed: bellows.py is dashboard.py's lock-protected child, so this is not a two-daemon race).
