# bellows — Next Session Baton

**Created:** 2026-05-19 (rewritten 2026-05-20)
**Carry-forward owner:** Planner

This file exists when bellows has work to carry into the next session. Delete it when all items here close. If bellows is not the focus of the next session, leave it untouched.

---

## Stale redirect content (priority 1 — quick fix)

**Surfaced:** 2026-05-20 (IP NEXT_SESSION.md creation, fuel continuation inference session)

This very file previously contained:

> **This file is superseded by the governance-root NEXT_SESSION.md.**
> The canonical "next session" file lives at: `/Users/marklehn/Developer/GitHub/NEXT_SESSION.md`

That governance-root file does NOT exist. The redirect was stale guidance from an earlier session-tracking model. Per the 2026-05-20 design decisions captured in userMemory ("**per-project NEXT_SESSION.md model — file exists when there's a baton to carry, deleted when work closes**; shop-level `shop_next_session.md` at governance root for shop-meta batons"), the per-project model is the current intent.

**What was changed today:** This file rewritten to follow the per-project baton model. The stale redirect text is gone.

**What remains to verify in next session:**
1. Does `bellows-specific tooling` or any agent prompt still reference `/Users/marklehn/Developer/GitHub/NEXT_SESSION.md` as a path it expects to read? Search the bellows repo and any specialist files for that path: `grep -rn "NEXT_SESSION" /Users/marklehn/Developer/GitHub/bellows /Users/marklehn/Developer/GitHub/PLANNER_TEMPLATE.md`. If any prompt or tool expects the root file, decide: (a) update those references to the per-project model, or (b) recreate the root file as a `shop_next_session.md`-style cross-project index.
2. Audit other projects (`forge`, `lessons-forge`, `anvil`) for stale `NEXT_SESSION.md` files containing similar redirects.

---

## Bellows-specific known gaps (priority 2 — capture only, no action required)

These came up during 2026-05-20 sessions and are worth surfacing in a future Bellows feature/cleanup plan. Not blockers — Bellows ships clean today; these are sharp-edges to consider.

### `pause_for_verdict` header field accepts only single enum value
`header_says_pause()` at `bellows.py:301-309` does exact-string match against `"always" | "after_step_1" | "after_qa_step"`. Comma-separated lists (e.g., `after_step_1, after_step_4`) silently match nothing. Bellows logs `WARN dispatch-validator: pause_for_verdict_value — unrecognized` at deposit but applies the defensive default. Captured in `invoice-pulse/knowledge/research/LESSONS.md` as a Planner-discipline issue. Possible Bellows-side enhancement: parse comma-separated values, or extend the enum to support `after_step_N` for arbitrary N, or hard-fail on unrecognized values instead of defaulting silently.

### Verdict prose directive is not actionable
Bellows reads only the first line (`verdict: continue|stop`) of verdict files. Prose in the body — even when written as directives ("create LESSONS.md with this content, then complete remaining tasks") — is unread. A `continue` verdict on a paused final step is irreversible plan closure regardless of body content. Possible Bellows-side enhancement: optional `redo: true` field in verdict header that re-runs the same step with the body as additional guidance. Out of scope today; captured for design.

### `**Deposits:**` gate doesn't parse parenthetical qualifiers
Per Rule 37, every path in the block must be resolvable. Markers like `(optional)` are prose, not parsed structure. The `deposit_exists` gate refuses the step on a missing path even when the Planner intended it as optional. Possible Bellows-side enhancement: recognize `(optional)` as a parse marker that downgrades the gate to a soft warning. Out of scope today; current mitigation is Planner discipline ("don't list optional deliverables in the Deposits block — describe them in step prose instead"), which is captured in IP LESSONS.md.

### Stale verdict step warning when plan is already in Done/halted
Log lines like `WARN [defer-validation-bulk-ingest-2026-05-20] ⚠️ stale verdict step 3 — plan in Done/ or halted-, moving to processed` fire when a verdict file lingers in `pending/` after the plan has terminated. Cleanup is automatic but the WARN is repetitive. Possible enhancement: rate-limit the warning per plan slug, or move it to INFO level.

---

## Definition of Done for this file

Delete this file when:
1. Stale-redirect priority-1 item is verified clean across all projects (grep audit completed, no remaining `/Users/marklehn/Developer/GitHub/NEXT_SESSION.md` references)
2. Priority-2 items have been either: (a) promoted to a Bellows feature/cleanup plan, (b) promoted to `shop_backlog.md` at governance root, or (c) explicitly declined

Items can be migrated to `shop_backlog.md` (governance root) if they're worth tracking but not work for the immediate next Bellows session.
