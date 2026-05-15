# Bellows Incident — QA Plan Stranded on Move-to-Done
**Date:** 2026-04-14 | **Plan:** `executable-forge-cleanup-duplicate-effectiveness-audit-QA-2026-04-14.md` | **Severity:** Low (work was complete, only housekeeping missing)

## What happened

Bellows ran the QA plan for the duplicate effectiveness audit cleanup fix. The agent:
- Created the evidence directory
- Wrote all 5 required evidence files (grep_deliverables.txt, pytest_targeted.txt, pytest_full.txt, cycle_smoke.txt, experiment_count.txt)
- Wrote the QA report at `forge/knowledge/qa/forge-cleanup-duplicate-effectiveness-audit-qa-2026-04-14.md`
- Ran the Rule 20 self-check, which printed `PASSED` and was captured in the QA report
- Reported "step complete" to Bellows

Bellows then independently checked `decisions/Done/` for the plan filename and did not find it. Bellows stranded the plan with the message:

> `⚠️ STRANDED — executable-forge-cleanup-duplicate-effectiveness-audit-QA-2026-04-14.md reported step complete but plan file not in Done/`

This is correct Bellows behavior — the strand caught a real gap between the agent's self-report and the filesystem state.

## What was actually missing

When the Planner inspected the post-strand state:

1. **PROJECT_STATUS.md milestone entry** for the audit cleanup — NOT added
2. **Feedback log entries** for both the DEV plan and the QA plan — NOT added
3. **`shutil.move` of the QA plan from `in-progress-` to `Done/`** — NOT executed
4. **Final commit** for the housekeeping changes — NOT made

The actual code fix (commit `5ea88e1`) had landed correctly during the DEV plan run hours earlier. The QA work (verification, tests, smoke check, Rule 20) was all complete and correct on disk. The strand was strictly on the housekeeping tail of the prompt.

## Working theory of the failure point

The QA plan prompt asked the agent to perform these steps in order, after the Rule 20 self-check passed:

1. Update `PROJECT_STATUS.md` — add a milestone entry, bump `Last Updated`
2. Move plan from `decisions/` to `Done/` via `shutil.move`
3. Commit with a chore message
4. Append feedback entry to `agent-prompt-feedback.md`

All four steps are missing. The most likely failure point is **step 1 (PROJECT_STATUS update)** because:

- The instruction said "add a completed milestone entry" with quoted text but did NOT give the agent an exact anchor line to use as the `edit_block`/`str_replace` target. The agent had to choose where to insert the new entry on its own.
- `PROJECT_STATUS.md` is a long file with a "completed milestones" section that has many similar bullet entries. Picking the wrong anchor or having a near-match collision would cause `edit_block` to fail.
- When `edit_block` fails, the agent typically retries or attempts a workaround (rewrite the whole section, use a different tool). Each retry burns turns. If the agent ran out of turns or hit a parser error mid-retry, it would report "step complete" optimistically (because the work it cares about — verification — IS done) without realizing the filesystem state hasn't updated.

The failures of steps 2–4 are downstream of step 1 failing — the agent appears to have abandoned the rest of the housekeeping after the PROJECT_STATUS update went sideways.

## Why Bellows correctly stranded the plan

This is a feature, not a bug. Bellows' independent check of `Done/` after agent self-report is exactly the kind of structural verification gate the Planner-Bellows collaboration project (separate backlog note: `planner-bellows-collaboration-2026-04-14.md`) is meant to formalize. The agent's "step complete" is a self-report; Bellows' filesystem check is structural verification. They disagreed, Bellows refused to mark the plan DONE, and the disagreement surfaced to the Planner for resolution.

**Without Bellows' verification gate, the plan would have been silently marked DONE with broken housekeeping**, and the Planner would have discovered the gap days later when reading PROJECT_STATUS.md and finding it stale. The strand caught the problem in the same session.

## Lesson for Planner: anchor PROJECT_STATUS edits with exact line targets

The Planner has been writing PROJECT_STATUS update instructions as "add a completed milestone entry: <quoted text>" without specifying an anchor line for `edit_block`/`str_replace` to target. This is the third or fourth time this kind of edit has been brittle. The fix is to make the edit instruction specify:

1. The exact line to replace (an existing milestone entry as the anchor) OR
2. The exact line to insert AFTER (with content quoted verbatim from the current PROJECT_STATUS.md)

Future Planner QA prompts that update PROJECT_STATUS.md should read the current file via `Filesystem:read_text_file` BEFORE writing the prompt, identify the most recent milestone entry as the anchor, and write the prompt as: "Use `edit_block` to replace the line `<exact existing line>` with that line followed by `<new line>`." Same pattern for the `Last Updated` line.

This is a **Planner discipline change** that prevents the failure mode at the prompt-design level. The Planner has filesystem read access to PROJECT_STATUS.md (it's in the allowed read scope per Rule 22) and was not using it to anchor edits precisely.

## Lesson for Bellows: surface the strand reason in the recovery flow

Bellows' strand message ("reported step complete but plan file not in Done/") was specific and actionable. This made root-causing fast. Future Bellows enhancements should keep this kind of structural-check messaging — vague strand messages would have made this incident much harder to investigate.

A future enhancement could optionally emit a "what's missing" diff at strand time: list the things the plan asked the agent to do that Bellows can independently verify (file moves, file existence, directory state) and flag which ones didn't happen. This would close the loop between strand detection and Planner recovery work, eliminating the manual investigation step.

## What the Planner did to recover

1. Read the QA report, all 5 evidence files, and the dev log via `Filesystem:read_text_file` to confirm the actual work was complete and correct
2. Moved the stranded plan from `in-progress-` to `Done/` via `Filesystem:move_file` (allowed under Rule 22 — file rename within decisions/)
3. Wrote this incident note
4. Will write a recovery executable that updates PROJECT_STATUS.md with the missing milestone AND appends the two missing feedback entries — single DEV-only plan, runs through Bellows like normal work, no Planner-side writes outside the allowed scope

## Open question for next session

Should PROJECT_STATUS.md updates be removed from QA plan responsibility entirely and consolidated into a separate "session wrap" agent that runs at the end of each session against all completed plans? Reasoning: PROJECT_STATUS edits are brittle, they're orthogonal to QA work, and batching them at session wrap means one carefully-anchored edit per session instead of N brittle edits per N plans. Tradeoff: PROJECT_STATUS drifts from reality between plan completion and session wrap, but the Planner is reading every plan's QA report anyway during Rule 22 verification — the drift is bounded by session length.

Defer this question to the Planner-Bellows collaboration session.
