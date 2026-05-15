# Cross-Cutting Pattern Raw Counts

**Date:** 2026-05-12

---

## Per-Artifact Recommendation Distribution

| # | Artifact | Response A (Validator) | Response B (Helper) | Response C (Observability) | Recommended |
|---|---|---|---|---|---|
| 1 | Verdict file content | Yes | No | Yes | A+C |
| 2 | Verdict filename/directory | Yes | No | Yes | A+C |
| 3 | Plan headers | No | No | Yes | C |
| 4 | Step headers | No | No | Yes | C |
| 5 | Deposits blocks | No | No | Yes (existing) | C |
| 6 | Rule 20 banner | No | No | Yes (existing) | C |
| 7 | Agent output markers | No | No | Yes (existing) | C |

## Aggregate Counts

- **Response A (Schema validator):** 2 of 7 artifacts (always combined with C)
- **Response B (Writer helper):** 0 of 7 artifacts
- **Response C (Observability-only):** 7 of 7 artifacts (5 standalone, 2 combined with A)

## Pattern Classification

**Split across two responses** (A+C and C). This is a **per-artifact case-by-case** outcome.

The convergence on C (100%) reflects that all artifacts already have or need observability. The A+C recommendations (29%) target the two verdict-lifecycle artifacts with demonstrated silent-skip failure and operational impact (plans stranded for hours). Zero B recommendations reflects that async Planner authoring sessions have no natural Bellows helper call site.

## LOC Distribution

- Artifacts needing new work: 2 (verdict content: ~35, verdict filename: ~25)
- Artifacts adequately covered: 5 (~0 new LOC each, possibly ~5 for step header edge case)
- **Total new LOC: ~65**
