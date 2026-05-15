# Dev Log — PLANNER_TEMPLATE Lessons: Bellows Step Parser Is 1-Indexed

**Date:** 2026-04-23
**Plan:** executable-planner-template-lessons-step-numbering-2026-04-23
**Step:** 1 (Documentation Agent)
**Status:** Complete

## Anchor Row Found

Verbatim anchor (line 1100 of PLANNER_TEMPLATE.md):

```
| 2026-04-20 | v4.26 governance sweep: six edits derived from a diagnostic pass over BACKLOG items deferred since v4.18 — (1) Rule 20 `[x]` dead code removal from POSITIVE_STATUS_TOKENS list; (2) Plan File Structure: commit-repo-location rule for governance-root edits; (3) Rule 14 state-transition enumeration extension; (4) Rule 13 fourth anchoring technique for UI placement; (5) Lessons entry codifying Position A (no markdown-only QA carve-out, immediately above); (6) this summary row. The sweep followed the v4.18 lesson: the focused diagnostic of PLANNER_TEMPLATE.md ran BEFORE the executable, producing a contradictions-and-duplications scan for each proposed change — no contradictions found, one partial overlap (Rule 13's existing UXD anchoring language) which the fourth-technique addition extends rather than duplicates. **Meta-lesson:** the Planner's scan-for-contradictions pass at plan-authoring time (formalized after the v4.18 Rule 22/Rule 8 contradiction) is doing its job — it let this sweep ship five rule changes in a single plan without the kind of downstream-contradiction failure that caused v4.18 to ship a conflict. The diagnostic-before-executable pattern for governance plans should now be considered standard, not optional. |
```

## New Row Appended

Verbatim new row (line 1101 of PLANNER_TEMPLATE.md):

```
| 2026-04-23 | Bellows' step parser is positional and 1-indexed — every `## STEP N —` header in a plan becomes Bellows step 1, 2, 3, ... regardless of the value of N. A plan that opens with `## STEP 0 —` still has its first header counted as step 1 for Bellows' purposes. This surfaced during `forge-cycle-12-2026-04-23`: the plan used STEP 0 as a pre-scan sync preface and numbered the rest 1–5, but Bellows dispatched "step 1" which hit the author's STEP 1 (Ingest) — a step whose prior-step-verification instruction expected STEP 0's deposit, which had not been created because Bellows never ran it. The gate tripped on Step 1's downstream missing deposit; the root cause was in the header numbering. **Lesson:** plan step headers start at `## STEP 1 —`. The N in "STEP N" is a positional label that must match Bellows' step index, not a free-form convention. A "pre-flight" or "setup" step either gets numbered `STEP 1` like everything else or is done outside the plan (CEO-side shell command, git pull in the bootstrap, etc.). Using non-1-indexed headers produces silent off-by-one dispatch failures where the gate trips far from the actual authoring bug. |
```

## Tail-Read Confirmation

Lines 1099–1105 after edit:
- Line 1099: `| 2026-04-20 | CEO decision (Position A): no QA carve-out ...`
- Line 1100: `| 2026-04-20 | v4.26 governance sweep: ...` (anchor row)
- Line 1101: `| 2026-04-23 | Bellows' step parser is positional and 1-indexed ...` (NEW ROW — final row in Lessons Learned table)
- Line 1102: (blank)
- Line 1103: `---`
- Line 1104: (blank)
- Line 1105: `## Forge Observations`

New row confirmed as final line in Lessons Learned table.

## Issues Encountered

- Plan file was already claimed (in-progress prefix already present) — skipped the shutil.move claim step.
- No other issues.

## Files Created or Modified

- `/Users/marklehn/Desktop/GitHub/PLANNER_TEMPLATE.md` — appended new Lessons Learned row at line 1101
- `/Users/marklehn/Desktop/GitHub/bellows/knowledge/development/planner-template-lessons-step-numbering-dev-log-2026-04-23.md` — this file

## Output Receipt

**Status:** Complete
**Deliverables:** PLANNER_TEMPLATE.md updated, dev log deposited
