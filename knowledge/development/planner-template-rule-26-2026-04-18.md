# Dev Log — PLANNER_TEMPLATE Rule 26 (Deposits Field Convention)
**Date:** 2026-04-18 | **Plan:** executable-planner-template-rule-26-2026-04-18.md | **Tier:** Small

## Summary

Single-step governance documentation edit adding Rule 26 (Deposits field convention) to PLANNER_TEMPLATE.md.

## Steps Completed

- **Step A — Version bump:** `**Version:** 4.24` → `**Version:** 4.25`
- **Step B — Last-Updated bump:** `**Last Updated:** 2026-04-18 (v4.24)` → `**Last Updated:** 2026-04-18 (v4.25)`
- **Step C — Insert Rule 26:** Inserted `### 26. Deposits field convention` between Rule 25's operational note and `### Diagnostic Prompt Engineering`. Rule 26 appears at line 711; Diagnostic Prompt Engineering follows at line 739.
- **Step D — Lessons Learned entry:** Added row documenting Rule 26's rationale, the parser gap, and the governance-first ship pattern.
- **Step E — Verification:** All checks passed — version reads 4.25, Rule 26 header appears exactly once, Diagnostic Prompt Engineering header appears exactly once after Rule 26, `**Deposits:**` field name appears in the Rule 26 body, `- none` case is described.
- **Step F — Commit:** `b934ebbb2b775bbabdcb30b94d27e39190e99426`

## Commit

```
b934ebbb2b775bbabdcb30b94d27e39190e99426
docs(planner): Rule 26 — Deposits field convention (v4.25)
```

## Rule 26 — Inserted Text (Audit Reference)

```markdown
### 26. Deposits field convention

Every step in every executable and diagnostic plan MUST declare its deposits via a `**Deposits:**` field. The field lists every file the step will create or write to — deposit files, dev logs, QA reports, evidence files, specialist syncs, any file the step is responsible for producing. The list is the canonical enumeration; anything not on it is not a deposit of that step.

**Why this rule exists:** Prior plans referenced deposits inside the prose of each step ("deposit findings to `path/to/file.md`", "write the QA report to `path/to/report.md`"), which forced Bellows's `deposit_exists` gate to keyword-scan the entire step text for path-like strings. That scan has tripped repeatedly on non-deposit paths — specialist-file content embedded inside plans, test-fixture strings embedded inside QA smoke tests, documentation examples referencing paths they don't create. Every false positive stranded a plan in `verdict-pending-*` state and required manual CEO bootstrap to resume. BACKLOG #6 enumerates the failure class. Rule 26 establishes a declarative field so future plans have a single unambiguous source of truth for deposits; a subsequent Bellows-side plan will extend the deposit parser to read the declared field and ignore prose-embedded paths.

**Field format and placement:** The field lives inside the step prompt, near the end, separated from surrounding prose by the bold marker `**Deposits:**` followed by a bulleted list. The format is:

    **Deposits:**
    - `path/to/first/deposit.md`
    - `path/to/second/deposit.md`

Each bullet holds exactly one path wrapped in backticks. Paths are project-relative (e.g., `bellows/knowledge/qa/my-report.md`) unless the deposit target is an absolute governance-root path (e.g., `/Users/marklehn/Desktop/GitHub/PLANNER_TEMPLATE.md`) — the absolute-path case is rare and reserved for governance edits. The list is complete: every file the step writes to MUST appear. Evidence files (Rule 18) do NOT need individual bullets — list the evidence directory as a single bullet, because the Rule 20 self-check already enumerates the individual evidence filenames.

**The "no deposits" case:** If a step makes no deposits at all — pure diagnostic investigation reported in conversation, pure housekeeping with no file writes, etc. — the field is still present, with a single bullet `- none`. Omission of the field is NOT permitted.

**Relationship to Bellows's current deposit parser:** The `extract_primary_deposit()` function currently reads `**Deposit:**` (singular) and does NOT recognize the plural-list form. Known parser gap to be closed by a future gates.py plan.

**Planner behavior during the parser-gap window:** Planner reads the plan's `**Deposits:**` block directly instead of relying on the verdict request's `Deposit` field.

**Retroactive application:** NEW plans only. Existing plans do not require amendment.

**Migration scope:** Governance convention only. Bellows-side parser extension is a separate future plan.
```

## Notes

- Rule 20 self-check does not apply — this is a single-step Documentation Agent governance edit, not a QA step.
- Step E serves as verification for this plan type.

## Output Receipt

| Field | Value |
|---|---|
| Status | Complete |
| Commit | `b934ebbb2b775bbabdcb30b94d27e39190e99426` |
| Files Changed | `PLANNER_TEMPLATE.md` (version bump, Rule 26 insert, Lessons Learned row) |
