# Bellows — Next Session

**As of:** 2026-06-11 (end of second session)

## State

Daemon on 4667e0b with lifecycle.db live. Plans 4 and 5 (governance codification) executed and closed clean under the new conventions — the full id-native loop is now both shipped AND codified: PLANNER_TEMPLATE v4.62, COMPANY.md, SPECIALIST_TEMPLATE.md, verdicts/README.md all current.

Conventions in force and documented: `<type>-draft-<HHMMSS>.md` deposits → mint-at-claim → `in-progress-<type>-<id>.md` → id-native verdicts (`verdict-<id>-step-N.md`) → `Done/<type>-<id>.md`; `[id]` commit tags; integer-only `implements diagnostic <id>` derivations citation; Planner lifecycle-DB read protocol (read-only URI, DB-as-index/filesystem-ground-truth, 4 canonical queries).

## Open items (priority order)

1. **steps-table coverage observation (NEW — investigate before Reporting Phase 2):** session-wrap roll-up returned COUNT=1 step row per 2-step plan and `turns` NULL (plans 4, 5). Either a write-surface gap at a transition boundary, a log-and-continue silent failure, or column semantics differ from assumption. Diagnostic-before-executable applies.
2. Reliability BACKLOG: isinstance asymmetry (bellows.py:505/594), config.json gitignore, `Bash(git:*)` breadth, partial-output persist on inactivity-timeout kill, plus remaining ~6 items in `knowledge/BACKLOG.md`.
3. Trivial rider for next README touch: add an id-form example to verdicts/README.md L23 (legacy-only example survives, coherent but incomplete).

## Reference

Plans 4/5 cost via the new roll-up query: plan 4 $3.62 / 694s; plan 5 $1.05 / 266s (1 step row each — see item 1).
