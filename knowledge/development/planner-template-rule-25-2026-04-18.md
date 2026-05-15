# Dev Log — PLANNER_TEMPLATE Rule 25 (Planner Verdict-Polling Discipline)
**Date:** 2026-04-18 | **Plan:** executable-planner-template-rule-25-2026-04-18

## Changes

- **Step A — Version bump:** `**Version:** 4.23` → `**Version:** 4.24`
- **Step B — Last-Updated bump:** `**Last Updated:** 2026-04-18` → `**Last Updated:** 2026-04-18 (v4.24)`
- **Step C — Insert Rule 25:** Added `### 25. Planner polling of Bellows verdict requests` between Rule 24 (Atomic Plan Deposit) and `### Diagnostic Prompt Engineering`. Includes: scan mechanics, pause reason routing table (5 codes), Rule 22 integration, gate-failure guard, physical cleanup note, BACKLOG independence note.
- **Step D — Lessons Learned entry:** Added 2026-04-18 row documenting Rule 25 rationale and design decisions.
- **Step E — Verification:** Confirmed version 4.24, Rule 25 header appears exactly once, Diagnostic Prompt Engineering follows Rule 25 at line 711, `gate_failure` present in pause reason routing table.
- **Step F — Commit:** `a0f51821f58c3fe215b2a5b9ab61c304e80a7970`

## Commit

- Hash: `a0f51821f58c3fe215b2a5b9ab61c304e80a7970`
- Message: `docs(planner): Rule 25 — Planner verdict-polling discipline (v4.24)`

## Files Modified

| File | Lines |
|------|-------|
| `PLANNER_TEMPLATE.md` | Line 5 (version), Line 6 (last-updated), Lines 681-709 (Rule 25 insertion), Line 1063 (Lessons Learned row) |

## Rule 25 — Inserted Text (Audit Reference)

```markdown
### 25. Planner polling of Bellows verdict requests

When the Planner dispatches a plan to Bellows (Layer 1 execution engine), Bellows posts verdict request files to `bellows/verdicts/pending/` whenever a plan pauses — between steps, at gate failures, at QA checkpoints, or at final-step close. The Planner has no automatic notification when these files appear. Without discipline, the Planner only discovers a verdict when the CEO relays a Pushover notification or asks the Planner to check. This breaks Rule 22's verification loop: Rule 22 assumes the Planner reads deposited files after an agent reports Complete, but in the Bellows flow the "agent reports Complete" signal IS a verdict request file the Planner does not see.

Rule 25 closes this loop. Every turn in a conversation where the Planner has at least one plan outstanding in Bellows, the Planner scans `bellows/verdicts/pending/` for verdict request files whose filename contains the slug of a session-dispatched plan. If a matching verdict file is found, the Planner reads it, routes on the `Pause Reason Code` field, and either performs Rule 22 verification on the `Deposit` field or stops and reports to the CEO.

**What counts as a session-dispatched plan:** Any plan the Planner has deposited to `knowledge/decisions/` during the current conversation, AND any plan the Planner has re-authorized during the current conversation (e.g., via manual bootstrap after a Bellows bypass). The Planner tracks these plans internally — by slug — as part of normal conversation state. Verdicts from plans dispatched in prior sessions or by other Planner instances are NOT this Planner's responsibility and should be ignored by Rule 25's scan (the CEO handles those via the normal Bellows notification path).

**Scan mechanics:** Once per conversation turn where an active session-plan exists, the Planner calls `Filesystem:list_directory` on the `bellows/verdicts/pending/` directory (read-only; the Planner has no write access there and does not need any). It filters the listing for filenames matching the pattern `verdict-request-<session-plan-slug>-step-*.md` where `<session-plan-slug>` is any plan the Planner has dispatched this session. For any match, the Planner calls `Filesystem:read_text_file` on the verdict file and extracts four fields: `Plan:`, `Step:`, `Pause Reason Code:`, and `Deposit:`. If the file is missing any of those fields, that is itself a Rule 22 verification failure — the Planner stops and reports the schema violation to the CEO.

**Pause reason routing:** The `Pause Reason Code` field determines whether the Planner auto-proceeds to Rule 22 verification or stops and reports. The routing is deliberately conservative — only two codes authorize auto-proceed, everything else stops:

| Pause Reason Code | Routing |
|---|---|
| `auto_close_disabled` | Auto-proceed to Rule 22 verification on the Deposit field. This is the normal between-step pause for plans with auto_close disabled. |
| `qa_checkpoint` | Auto-proceed to Rule 22 verification on the Deposit field. This is the standard DEV→QA handoff signal. |
| `gate_failure` | Stop and report to CEO. A Bellows gate tripped — the Planner does NOT mechanically approve plans that tripped gates, regardless of whether the Deposit file passes Rule 22. Quote the gate failure text from the verdict file's `## Gate Failures` section in the report. |
| `scope_violation` | Stop and report to CEO. The agent modified files outside the plan's declared scope. Same no-mechanical-approval rule as gate_failure. |
| Any other code (including unknown, missing, or future codes) | Stop and report to CEO. Conservative fallback — the Planner does not guess at the safety of unfamiliar pause reasons. |

**Rule 22 routing on auto-proceed codes:** When the Pause Reason Code authorizes auto-proceed, the Planner takes the path in the verdict file's `Deposit:` field and applies Rule 22's (a)–(e) checks to that path. If the Deposit field is `none` (no deposit declared for that step), the Planner reports the verdict to the CEO for judgment — "none" is not a failure but it is not a Rule 22 pass either, and the CEO decides whether the step should have declared a deposit. If Rule 22 passes, the Planner reports the pass to the CEO ("Step N QA verification passed, safe to close Bellows verdict") and the CEO resolves the verdict via the normal Bellows workflow. If Rule 22 fails at any of (a)–(e), the Planner reports the failure in full per Rule 22's existing escalation language.

**Gate-failure guard (load-bearing):** Rule 25 is designed to MECHANIZE routine verification, not to automate approval. The pause-reason taxonomy is the safety layer. If Bellows reports a gate failure or scope violation, that is a signal the plan did something unexpected — the Planner treats it as a halt-and-report condition no matter how clean the Deposit file looks. The CEO is the authority on whether a gate failure is a false positive (e.g., BACKLOG #6's deposit-path parser false positives observed on Plan B's QA step) or a genuine problem. The Planner does NOT decide this unilaterally.

**Relationship to Rule 22:** Rule 25 is a TRIGGER and ROUTER for Rule 22, not a replacement. Rule 22 still defines the verification checks (a)–(e) that the Planner applies to any deposited file. Rule 25 adds the Bellows-dispatched discovery path: when the deposit reference comes from a verdict request file (not an inline CEO "done" signal), Rule 25 is how the Planner finds the deposit; Rule 22 is how the Planner verifies it.

**Physical cleanup is CEO responsibility:** The Planner does not rename, delete, or otherwise modify files in `bellows/verdicts/pending/`. Read-only access. Physical cleanup of stranded verdict files is a CEO `rm` action (see BACKLOG #1 scope_check race for the broader cleanup-automation discussion).

**Operational note — this rule is not blocked by BACKLOG #4 or #5:** The Bellows-side reliability items (filesystem watcher reliability, step state across re-claim) operate on the Bellows dispatch side. Rule 25 operates on the Planner's read side — it scans files Bellows has already written. The two are structurally independent. Rule 25 can be adopted immediately and will continue to work correctly as BACKLOG #4 and #5 are resolved.
```

## Output Receipt

```
Step:                 1
Plan:                 executable-planner-template-rule-25-2026-04-18
Total Steps:          1
Status:               Complete

Deliverables:
  - PLANNER_TEMPLATE.md v4.24 — Rule 25 inserted, version bumped, Lessons Learned updated
  - bellows/knowledge/development/planner-template-rule-25-2026-04-18.md (this file)

Sources:
  - bellows/knowledge/decisions/executable-planner-template-rule-25-2026-04-18.md (plan file)

Timestamp:            2026-04-18
```
