# Dev Log — Phase 1.5 patch: add Source D (LESSONS.md)

**Plan:** executable-phase-1-5-lessons-source-d-2026-05-10
**Step:** 1
**Date:** 2026-05-10

## Edits Applied to PLANNER_TEMPLATE.md

### Edit 1 — Version bump

**old_text:**
```
**Version:** 4.34
**Last Updated:** 2026-05-05 (v4.34)
```

**new_text:**
```
**Version:** 4.35
**Last Updated:** 2026-05-10 (v4.35)
```

### Edit 2 — Phase 1.5 header sentence: "three" → "four"

**old_text:**
```
Before writing ANY prompt (diagnostic, fix, or orchestration step), the Planner reads three knowledge sources to pick up context that has accumulated outside formal plan files. Informal findings, agent observations, and recent QA notes live in these locations — not in `knowledge/decisions/` plans, which are templates rather than records.
```

**new_text:**
```
Before writing ANY prompt (diagnostic, fix, or orchestration step), the Planner reads four knowledge sources to pick up context that has accumulated outside formal plan files. Three are project-scoped (informal findings, agent observations, and recent QA notes); the fourth is cross-project (governance-root lessons that apply across all projects). These live outside `knowledge/decisions/` plans, which are templates rather than records.
```

### Edit 3 — Insert Source D after Source C, rewrite "This is NOT optional"

**old_text:**
```
QA reports frequently surface Advisory-level findings (🔵) that go beyond the immediate verification scope. These are often useful context the Planner would otherwise miss.

**This is NOT optional.** Skipping any of the three sources means operating with stale context. The feedback log alone is insufficient — findings accumulate across all three locations, and the Planner's "lacks context" failure mode (documented in the Informal Sharing Friction Audit of 2026-04-09) is driven by reading only one of the three.
```

**new_text:**
```
QA reports frequently surface Advisory-level findings (🔵) that go beyond the immediate verification scope. These are often useful context the Planner would otherwise miss.

**Source D — Cross-project lessons:**
- `/Users/marklehn/Desktop/GitHub/LESSONS.md`

Bounded scope to keep read cost cheap as the file grows:
- **All entries from the last ~14 days** (catches recent lessons before they fade)
- **All entries tagged `planner-discipline`** regardless of age (catches discipline rules permanently)

Other tags (`bellows-architecture`, project-specific patterns, etc.) are read on-demand when the current task touches that area, not every session. This is the only cross-project knowledge artifact in the protocol — lessons captured here apply across all projects, and missing one means repeating a known failure on a different project.

**This is NOT optional.** Skipping any of the four sources means operating with stale context. The feedback log alone is insufficient — findings accumulate across all four locations, and the Planner's "lacks context" failure mode (documented in the Informal Sharing Friction Audit of 2026-04-09, expanded 2026-05-10 with the LESSONS.md gap) is driven by reading only a subset.
```

### Edit 4 — "Why three sources" → "Why four sources"

**old_text:**
```
**Why three sources instead of one:** Informal findings from agent work naturally accumulate in whichever knowledge-base location fits best at the moment of capture. Feedback entries land in the feedback log; diagnostic findings land in research; verification-adjacent observations land in QA. The Planner needs all three to reconstruct what has happened across agent sessions since the last planning pass.
```

**new_text:**
```
**Why four sources instead of one:** Informal findings from agent work naturally accumulate in whichever knowledge-base location fits best at the moment of capture. Feedback entries land in the feedback log; diagnostic findings land in research; verification-adjacent observations land in QA; cross-project discipline rules and meta-patterns land in LESSONS.md. The Planner needs all four to reconstruct what has happened across agent sessions since the last planning pass — three project-scoped, one cross-project.
```

## Confirmations

- Version bumped: 4.34 → 4.35
- Only 4 regions changed in `git diff` output — no other lines touched
- LESSONS.md was uncommitted at governance root (modified); included in commit 1

## References

- LESSONS.md 2026-05-10 meta-entry: "Meta-lesson: LESSONS.md not in Phase 1.5 scope is itself the bug"
- LESSONS.md 2026-05-09 entry: Rule 20 banner format recurrence that this patch operationalizes

---
## Output Receipt
**Agent:** Bellows Documentation Analyst
**Step:** 1
**Status:** Complete

### What Was Done
Patched PLANNER_TEMPLATE.md Phase 1.5 (v4.34 → v4.35) to add Source D — LESSONS.md at governance root — as a fourth mandatory context source with bounded read scope (last ~14 days + planner-discipline tags). Created dev log documenting the 4 exact edits applied.

### Files Deposited
- `bellows/knowledge/development/phase-1-5-lessons-source-d-dev-log-2026-05-10.md` — this dev log

### Files Created or Modified (Code)
- `/Users/marklehn/Desktop/GitHub/PLANNER_TEMPLATE.md` — 4 surgical edits adding Source D to Phase 1.5

### Decisions Made
- None beyond plan spec

### Flags for CEO
- None

### Flags for Next Step
- LESSONS.md was uncommitted at governance root; included in commit 1 alongside PLANNER_TEMPLATE.md
