# Planner-Bellows Collaboration via Pause-and-Review
**Date:** 2026-04-14 | **Type:** Backlog note for future Bellows session | **Priority:** High (architectural gap in core workflow)

## The gap

Today's Planner-Bellows workflow is strictly post-hoc. Bellows runs plans to completion, reports DONE/STRANDED/FAILED, and only then does the Planner (this Claude Project conversation) do Rule 22 verification on the deposited files. If an agent deviates mid-plan, the Planner finds out after the work is committed and the QA agent has already self-verified the deviation.

CEO framing: **Bellows and Planner should be collaborators in the execution of a plan, not sequential handoff partners.** Bellows should be able to pause mid-execution, surface its current state via filename, let the Planner read the in-progress deposits and decide whether to continue or correct, and then resume (either with the original plan or a modified replacement plan).

## Proposed architecture — Filename-state checkpoint pattern

The core insight is that **Bellows does not need to support resumption from an internal checkpoint.** State lives in the filesystem — plan filenames and deposited artifacts. The Planner can always rewrite a plan as a fresh executable that starts from "where the old one left off plus corrections." This means the loop works with minimal Bellows changes.

### Filename state transitions

| State | Filename pattern | Bellows behavior |
|---|---|---|
| Pending | `executable-foo-YYYY-MM-DD.md` | Pick up and execute |
| Currently running | `in-progress-executable-foo-YYYY-MM-DD.md` | Continue executing |
| Paused for review | `paused-after-step-N-executable-foo-YYYY-MM-DD.md` | Skip — do not pick up |
| Approved to continue | `in-progress-executable-foo-YYYY-MM-DD.md` (Planner renames back) | Watcher sees rename, resumes from step N+1 |
| Superseded by replacement | `partial-step-N-complete-executable-foo-YYYY-MM-DD.md` in `Done/` | Planner manually moved; Bellows picks up the replacement plan |
| Complete | `executable-foo-YYYY-MM-DD.md` in `Done/` | Standard end state |

### Plan-declared review gates

Plans declare which steps trigger a pause via a header field:

```
**Review After Steps:** 1, 3
```

Bellows-side change: in the main execution loop, AFTER step N completes and BEFORE calling `planner.consult` for step N+1, check the plan header. If N is in the `Review After Steps` list, rename the file from `in-progress-` to `paused-after-step-N-` and stop. Bellows logs the pause and moves to the next plan in the queue (the queue is not blocked — Bellows can run other plans while one is paused).

### Planner workflow on pause

The Planner sees `paused-after-step-N-` files in the next directory listing. For each paused file:

1. Read the deposited artifacts from step N (dev log, QA evidence, findings file)
2. Verify against the plan's intent — is this what was asked for?
3. Decide one of three outcomes:

**Outcome A — Continue as-is.** Plan was executed correctly. Rename `paused-after-step-N-` back to `in-progress-`. Bellows watcher detects the rename and resumes from step N+1.

**Outcome B — Continue with minor correction (additive).** Original work is correct but needs a small addition for the next step. Edit the existing plan file in place to update the step N+1 prompt with the correction, then rename `paused-after-step-N-` back to `in-progress-`. Bellows resumes with the corrected step.

**Outcome C — Replace plan entirely (work was wrong-shape).** Step N produced something that doesn't match the plan's intent, OR new information surfaced that requires rethinking. Move the paused file to `Done/` renamed as `partial-step-N-complete-executable-foo-YYYY-MM-DD.md` with a header note explaining what was completed and why the plan was replaced. Write a new executable plan that starts from "step 2 of the original plus corrections" and deposit it in `decisions/`. Bellows picks up the new plan via normal queue mechanics.

### Why this design works

- **No new execution state in Bellows.** The only Bellows change is reading the `Review After Steps` header and renaming files. No checkpoint serialization, no polling, no timeouts.
- **Queue is never blocked.** Bellows skips `paused-` files like it skips `in-progress-` files. Other plans in the queue continue running.
- **Planner can take any amount of time.** A `paused-` file sits indefinitely until reviewed. No timeout pressure.
- **Replacement plans use existing dispatch.** Outcome C requires writing a new plan, but plan-writing is the Planner's existing job. No new mechanism.
- **Filesystem-as-state-machine is consistent with existing patterns.** Plans already use `in-progress-` prefix for claiming. Adding `paused-after-step-N-` and `partial-step-N-complete-` extends the same pattern.

## Bellows changes required

1. **Parse the `**Review After Steps:**` header field in plan files.** Add to `parser.py`. Default: empty list (no pauses, behaves as today).
2. **Honor the pause list in the execution loop.** In `bellows.py:run_plan`, after step N completes, check if N is in the pause list. If yes, rename file to `paused-after-step-N-` and exit the run_plan function. If no, call `planner.consult` as normal.
3. **Skip `paused-` files in the queue scanner.** In whatever function lists pending plans, exclude any file matching `paused-*.md`. (Same treatment as `in-progress-*.md`.)
4. **Detect rename events on `paused-` → `in-progress-` transitions.** This may already work — Bellows uses watchdog for filesystem events. Verify that a rename from `paused-` to `in-progress-` triggers a re-scan and resumption from step N+1. If not, add the watcher hook.
5. **Resume from the correct step on watcher trigger.** When Bellows picks up an `in-progress-` file that was previously paused, it needs to know which step to start from. Two options: (a) parse the prior `paused-after-step-N-` rename history from `bellows.db:runs` (last successfully completed step + 1), or (b) include the current step in the filename itself (e.g., rename to `in-progress-from-step-2-executable-foo.md`). Option (b) is simpler.

## Planner changes required

1. **Update PLANNER_TEMPLATE.md** with a new rule (Rule 23 or similar) covering pause-and-review protocol. Specifically: when the Planner sees `paused-after-step-N-` files in a `decisions/` listing, treat them as work-in-progress that requires Planner action. Include the Outcome A/B/C decision tree.
2. **Update plan-writing convention** to include `**Review After Steps:**` in the header for plans where mid-flight verification is wanted. CEO-controlled per-plan — high-stakes plans get pauses, mechanical plans don't.
3. **Update the post-step verification protocol.** Reading a `paused-after-step-N-` plan's artifacts is a verification action that may produce a new plan deposit (Outcome C). This is a shift from "verification is a passive check" to "verification can produce work."

## Estimated scope

- **Bellows side:** half-day session. Parser change, queue scanner change, run_plan loop change, watcher rename handling, tests for each.
- **Planner side:** brief PLANNER_TEMPLATE.md update, no code changes (the Planner conversation is the actor, not a script). 30 minutes.
- **Total:** half-day to one-day for the soft version. The hard version (Bellows polling Planner verdicts in real time) is no longer needed — this filename-state approach replaces it.

## Why this matters

Today I caught a DEV agent refactoring literal commits into a `range(5)` loop in the Anvil fix. Caught it at QA time via evidence file reading, but only because I was disciplined about reading the full QA evidence. A less-attentive read would have missed it. The next deviation might not be caught.

The current workaround is "shorter plans with more checkpoints." It works but it's slow and brittle. Pause-and-review is the structural fix — the Planner gets eyes on intermediate state at exactly the points the plan declares are high-stakes, without the round-trip overhead of writing many tiny plans.

## Recommended next-session structure

1. **Diagnostic on Bellows execution flow.** Read `bellows.py:run_plan` and `parser.py` in full. Confirm the hook points for header parsing, file renaming, and watcher rename detection. Confirm that rename events trigger re-scans (this is the riskiest assumption).
2. **Design session.** Lock down the filename conventions (`paused-after-step-N-`, `in-progress-from-step-N-`, `partial-step-N-complete-`), the header field syntax, and the resumption mechanism (option a vs option b above).
3. **Implementation.** Ship the Bellows changes in a single executable plan with thorough QA on the rename and watcher behavior.
4. **Protocol update.** Update PLANNER_TEMPLATE.md with Rule 23 and the Outcome A/B/C decision tree.
5. **Validation run.** Throwaway 2-step plan with `**Review After Steps:** 1` to verify the full pause-rename-review-resume cycle works end-to-end.

## Interim mitigation for current sessions

Until pause-and-review ships, Planner should:
- Continue post-hoc verification via deposited files
- Tighten reading discipline on QA evidence files (not just QA reports)
- For high-stakes plans, prefer writing more, smaller plans with explicit verification gaps between them — this approximates pause-and-review with current Bellows mechanics
- Accept slower throughput on high-risk work in exchange for visibility
