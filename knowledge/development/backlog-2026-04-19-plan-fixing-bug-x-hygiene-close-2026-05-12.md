# Dev Log — Hygiene Close of 2026-04-19 BACKLOG Entry: Plan Fixing Bug X Tripped Bug X

**Date:** 2026-05-12
**Plan:** executable-backlog-2026-04-19-plan-fixing-bug-x-hygiene-close-2026-05-12
**Commit:** a825c4e

## What changed

`bellows/knowledge/BACKLOG.md`:
- Removed the 2026-04-19 entry "plan fixing bug X tripped bug X during its own close" from the `## Open` section.
- Added a hygiene-close bullet at the top of the `## Closed` section recording the partial supersession by PLANNER_TEMPLATE v4.38 and the explicit scope-narrowing.

## Why

The 2026-04-19 entry's own text flagged "May warrant promotion to a PLANNER_TEMPLATE Lessons Learned entry at next governance pass." PLANNER_TEMPLATE v4.38 (2026-05-11, governance-root commit `4e54c02`) shipped a Restart Discipline paragraph and a Lessons row that document the parser-fix subset of this pattern. The general close-path pattern (broader than the parser subset) remains procedurally documented in the original entry's own mitigation text, so moving the entry to Closed with a scope-narrowing note preserves the historical reference while clearing the Open list.

## Scope

- No code changes.
- No tests added or modified.
- No daemon restart required.
- BACKLOG `## Open` count: 2 → 1.

## References

- PLANNER_TEMPLATE.md v4.38 Restart Discipline subsection, line 882
- PLANNER_TEMPLATE.md v4.38 Lessons Learned row, line 1227 (2026-05-11)
- Governance-root commit `4e54c02`
