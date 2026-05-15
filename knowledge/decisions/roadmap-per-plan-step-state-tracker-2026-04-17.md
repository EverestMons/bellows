# Bellows — Roadmap: Per-Plan Step State Tracker
**Date:** 2026-04-17 (scoped) | **Status:** Not started — queued for future session
**Deposited by:** BrewBuddy Planner (session wrap 2026-04-17)
**Source context:** CEO proposal during BrewBuddy session on 2026-04-17

## The Problem

Bellows currently uses filename-prefix state for plans (`executable-`, `in-progress-`, `verdict-pending-`, moved to `Done/`). This works for single-step plans and linear multi-step progression. It breaks when:

1. A multi-step plan pauses at step N and needs to resume at step N (not N=1).
2. The filename prefix doesn't carry step information, so a "resume" action looks indistinguishable from a "restart" action.
3. The CEO or Planner clears a `verdict-pending-` by renaming — but Bellows picks up the plan fresh and re-runs Step 1 regardless, because the filename alone doesn't tell it where to resume.

This cost ~30 minutes of confusion during BrewBuddy session 2026-04-17 when a plan paused after Step 1 DEV and the Planner manually renamed the file several times trying to get Bellows to resume at Step 2. Plan ultimately required Step 2 to be invoked manually via direct Claude Code bootstrap, bypassing Bellows entirely.

## Proposed Design (CEO's Model)

**Bellows owns step-state centrally. Plan files stay declarative.**

When Bellows discovers a new plan in `decisions/` (or equivalent), it:
1. Parses the plan file to count `## STEP N —` headers (this already happens — "plan has N steps" appears in logs today).
2. Creates a state record in Bellows' own store: `(plan_filename, total_steps, current_step=1, status='queued', last_updated_at)`.
3. When a step starts, sets status='running'.
4. When a step completes successfully, increments `current_step` and sets status='awaiting_verdict' (or 'complete' if last step).
5. When CEO clears the verdict, status → 'queued' (to resume).
6. On next run cycle, Bellows sees `status='queued', current_step=N` → it injects Step N context into the bootstrap prompt, not Step 1.

## Why This Is The Right Shape

- **Plan files stay immutable after deposit.** No progress metadata in the plan. No edits by Planner or Bellows to track state.
- **No per-step file splitting.** Plans remain unified documents.
- **Runner is the source of truth for runner state.** Bellows is the only party that knows exactly what it executed — codifies that as its own state rather than scattering it across filename prefixes.
- **Decouples from filename prefix semantics.** The prefix becomes purely a routing signal (claim, pause, done) — not a step pointer.

## Implementation Sketch

### State Store
- `bellows.db` already exists (SQLite). Add table:
  ```sql
  CREATE TABLE IF NOT EXISTS plan_state (
      plan_filename TEXT PRIMARY KEY,
      total_steps INTEGER NOT NULL,
      current_step INTEGER NOT NULL DEFAULT 1,
      status TEXT NOT NULL DEFAULT 'queued',  -- queued | running | awaiting_verdict | complete
      first_seen_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
      last_updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
      last_gate_result TEXT,
      last_error TEXT
  );
  ```

### Discovery Hook (where Bellows first sees a plan)
- `parser.py` or wherever plan discovery happens — on first sight of a plan, upsert a `plan_state` row with `current_step=1`.
- Subsequent discoveries of the same plan filename read existing state rather than overwriting.

### Step Completion Hook
- After a step's Output Receipt is parsed and status=Complete, increment `current_step`.
- If `current_step > total_steps`, mark status='complete' and let move-to-Done proceed.

### Verdict Cleared Hook
- When a plan transitions from `verdict-pending-` back to `executable-` / `diagnostic-`, Bellows reads `plan_state.current_step` for that plan_filename and runs step N — NOT step 1.

### Bootstrap Injection
- The standard bootstrap prompt says "Execute Step 1 ONLY." For resumes, Bellows overrides this to "Execute Step N ONLY" where N = current_step.
- This means Bellows generates the bootstrap dynamically per invocation rather than relying on a static prompt in the plan file.

## Edge Cases To Design

1. **Plan file modified mid-execution.** What if the CEO edits the plan to add/remove a step between Bellows runs? `total_steps` could drift from the file. Solution: re-parse on every discovery and update `total_steps`, but preserve `current_step` if it's still ≤ new total.

2. **Plan filename changed.** If the CEO or Planner renames a plan mid-flight (not just prefix changes), the state record becomes orphaned. Solution: state records should probably key on a stable plan ID embedded in the plan (e.g., a UUID in the plan header) rather than the filename. This is a larger design change — possibly skip for v1, accept that filename rename breaks state.

3. **Bellows crashes mid-step.** The state record shows `running` but the step didn't complete. Next Bellows startup should either retry or mark as failed. Needs policy.

4. **Step re-run on failure.** If a step fails gates, Bellows currently pauses at `verdict-pending-`. On verdict clear, does it re-run the same step (same current_step) or skip to next? Needs explicit behavior — probably re-run same step, since that's what "resume after fix" means.

5. **Bootstrap format.** The current plan format has `Execute Step 1 ONLY` hardcoded in the "How to Run" section. Changing this to work with dynamic step injection means either: (a) the "How to Run" block is regenerated by Bellows at invoke time, or (b) all plans get rewritten to use a step-agnostic bootstrap ("Execute the current step as directed by Bellows"). Option (b) is simpler going forward; (a) handles backward compatibility with existing plans.

## Scope Estimate

- **Tier:** Medium — schema change + 4-5 hook points in existing Bellows code + bootstrap generation logic
- **Expected agents:** SA (design state machine + schema) → DEV (implement in bellows.py / runner.py / parser.py) → QA (verify with multi-step test plan that intentionally pauses and resumes)
- **Testing:** Create a BrewBuddy test plan with 3 steps, intentionally fail step 2's gate, clear verdict, confirm Bellows resumes at step 2 (not step 1). This replicates the exact failure mode seen on 2026-04-17.

## Pre-Existing Context (Reference)

- The `diagnostic-bellows-claude-p-characterization-2026-04-13.md` plan (in BrewBuddy/knowledge/decisions/Done/) was the Bellows design reference, documenting `claude -p` behavior and establishing the filesystem-as-state-machine model. Worth re-reading before implementation.
- The `bellows-live-test-*` plans in BrewBuddy Done/ were the validation that Bellows works for simple cases. This roadmap addresses the multi-step resume edge case those tests didn't cover.

## Why This Is Worth Building

Every multi-step executable or diagnostic plan is currently at risk of this failure mode. During 2026-04-17 BrewBuddy session, I (Planner) misunderstood Bellows' state model and contributed ~30 minutes of friction trying to unstick a paused plan. The root issue was that the Planner-Bellows contract didn't have a "clear verdict" path that resumed correctly — because Bellows had no notion of "where to resume." This will recur in every project (invoice-pulse, Forge, Anvil, freight-kb, etc.) as soon as those projects use multi-step plans at scale. Fixing it once in Bellows benefits every project.

## Next Steps

1. CEO confirms design direction (this roadmap captures the design at the "we like the direction, haven't committed to details" level).
2. Scoping session in Bellows project — convert this roadmap to an executable with SA → DEV → QA steps.
3. Implement against the 5 edge cases listed above, explicitly deciding behavior for each.
4. Validate with a deliberate multi-step test plan.

This roadmap does not commit to implementation. It captures enough context that a future Bellows session can open with "let's implement per-plan step tracking" instead of "what was that CEO idea from April 17?"
