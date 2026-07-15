# Agent Prompt Feedback

- Plan QA step was well-structured: the five behavior checks mapped cleanly to verifiable assertions in code and tests
- The "cite the new regression test" instruction in check (b) was helpful — it forced traceability between the QA claim and the actual test

- Plan instructions were precise and actionable — the exec-194 log citation made root cause verification trivial
- The "verify backstop is intact" sub-task was efficient: grep + read confirmed the wiring without ambiguity

- None. The plan was clear and correctly scoped; the idempotent UPDATE pattern with `AND outcome IS NULL` guard worked as designed.

- The plan's QA step prompt correctly required verification of all three terminal branches (continue-to-done, halt, stop) — this is a good pattern for lifecycle-write fixes where the same variable feeds multiple downstream sites.

- The `lookup_slug` normalization list (stripping `diagnostic-`, `executable-` but not `qa-`) is a naming inconsistency that should be documented or unified in a follow-up — not a bug per se, since the verdict-request filename uses the unstripped slug for `qa-` plans, but it creates a trap for any code that assumes `lookup_slug` is always a bare slug.

- `session-limit-park-reverify-qa`: When a QA plan explicitly names the Rule 20 self-check banner format in the step prompt, the agent must include it verbatim — the gate enforces byte-level matching on both the section heading (`## Rule 20 — QA Self-Check Results`) and the PASSED line (`**PASSED — SELF-CHECK PASSED**`).

- Session-limit detection logic is clean — separate from transient-retry guard by construction (stderr vs stdout result event), well-tested, no edge-case confusion.

None — Step 2 executed as designed with no deviations or surprises.

None.

The QA step's verification table structure (9 items covering code-level, test, cleanup, and cross-step checks) provided comprehensive coverage with clear pass/fail criteria. The Step 2 dev-log's diff hunks and test table made code-level verification efficient — each claim could be traced directly to source lines and test names. One observation: the QA step's check #8 specifies `ls knowledge/decisions/ | grep halted` should be "empty" but other pre-existing halted files exist outside this plan's scope; the intent is clearly about 136/137/138 specifically. Future plans should scope the grep pattern (e.g., `grep halted.*13[678]`) to avoid ambiguity.

The research document (`plan-double-claim-137-138-2026-07-07.md`) §3 fix list was precise and implementation-ready — each fix had the exact function name, line number, and change shape. The active-state set was explicitly stated with the CHECK constraint reference, eliminating ambiguity. One minor gap: the fix list didn't mention the existing test (`test_lifecycle_meta_and_derivations_at_claim`) that would break due to its use of a shared placeholder name for ID-burning — this was discovered during the test run and trivially fixed.

The plan's premise for Task A ("plan 140 ran in the main checkout with no worktree") was incorrect — plan 140 did get a worktree. The step log files' `cwd` field is the definitive evidence for worktree usage. Future diagnostics investigating worktree anomalies should check `cwd` in step logs as the first probe, not just the presence/absence of the `.bellows-worktrees/<id>` directory (which is removed on successful teardown).

No new prompt feedback. Plan instructions were clear and all verification items matched on first pass. The two-step verification flow (DEV implements, QA verifies at code level) worked well for this single-file change.

No new prompt feedback to record. The plan instructions were clear and the implementation matched on first pass (two test fixture adjustments for pipe-header string semantics were mechanical, not prompt issues).

- The diagnostic scope was clear and the CEO context section provided the right pointers (plan 136 death, stash, single-daemon confirmation). Citing the `_invalidate_seen_on_redeposit` mechanism as the specific gap would have further narrowed the investigation.
- The "ruled OUT by hand" note (two-daemon race) saved investigation time — confirming a negative externally and directing the agent to the claim mechanism was efficient.

No prompt feedback items surfaced during QA verification.

No daemon-owned prompt feedback items surfaced during this implementation.

No feedback items — plan instructions were clear and complete.

None — diagnostic instructions were clear and well-scoped.

No feedback items — plan instructions were clear and complete.

No prompt feedback to report. Step 2 instructions were precise — verification table structure and individual test execution requirements were clear.

No prompt feedback to report. The plan instructions were clear and the existing `_extract_plan_required_deposits` idiom provided a clean template to follow.

No prompt-feedback observations. Plan instructions were clear, verification rows were specific and testable.

No prompt-feedback observations for this step. The plan instructions were clear and the implementation proceeded without ambiguity.

- Prompt was well-scoped: the HARD CONSTRAINT on bucket (B) prevented false inflation of the mechanizable count by catching checks that look mechanical but require judgment beneath the surface.
- The specific instruction to check for existing-code overlap was valuable — it revealed the shift-left dimension (pre-deposit vs post-execution enforcement) that pure classification would have missed.
- The 22-item scope was correctly bounded. PLANNER_TEMPLATE.md also contains 46 "Orchestration Plan Rules" (a separate section) that are conceptual rules, not deposit-time checks. The diagnostic correctly scoped to the checklist section.

Plan 64, Step 2 (QA): The plan's verification checks were well-scoped and evidence-producing. The `dogfood_check` required checking both git-show on main and the lifecycle.db — the daemon had written the PROJECT_STATUS milestone in a commit (`c1f1441`) that existed on main but the worktree's working copy hadn't updated, so `git show main:PROJECT_STATUS.md` was the correct verification path rather than reading the file directly. No issues encountered; all four checks passed on first attempt.
Step 2 complete. All four verifications passed:

Plan 64, Step 1 (Documentation Agent). The session-wrap documentation step ran cleanly. The plan's E1–E3 instructions were clear and well-structured; the explicit "read the last two entries to match structure" guidance for LESSONS.md was effective. The governance-root commit instruction correctly anticipated the `forge` gitignore issue would be harmless (no forge changes). One minor note: the commit message template used `[<your plan id>]` placeholder — future plans could pre-fill this to `[64]` since the plan id is known at authoring time.

Plan 60 Step 2 executed cleanly. The QA step instructions were well-structured with clear evidence file names and verification checkpoints. The Rule 20 self-check block reference path in the specialist file (`/Users/marklehn/Desktop/GitHub/`) differs from the actual location (`/Users/marklehn/Developer/GitHub/`) — the glob fallback found it but the canonical path should be corrected. Dev log was accurate and complete, making verification straightforward.
Step 2 (QA) complete. Summary:

- **Full suite**: 684 passed, 0 failed, 8 new tests matching dev log
- **G1**: Write/Edit `tool_use` content captured into `_all_assistant_text`; plan-57 repro extracts forward register
- **G2**: `_all_assistant_text` propagated in parsed dict; defense WARN fires on tool-content-only unparsed case
- **No regression**: bare-text, multi-turn, all 3 extraction channels, ceo_flags, verdict_requested all pass
- **Scope**: only in-scope files (runner.py, parser.py, 3 test files, dev log)
- **Rule 20**: PASSED — all 5 evidence files present, no hedging keywords

**Flags for CEO:**
1. DAEMON RESTART REQUIRED — do not restart until plan closes
2. RE-CANARY — fresh FORWARD canary after restart must land row #23
3. Fix hardens all three channels against tool-buried receipts

Commit: `c9f8e35`. Stopping and waiting for confirmation.

### Ledger Updates

**2026-06-14 — ledger-toolcontent-capture (DEV Step 1)**

1. The tool_use event shape confirmed: `block["input"]["content"]` for Write and `block["input"]["new_string"]` for Edit — matching the diagnostic's prediction.
2. The `ledger_source` variable in parser.py already held the correct value (`raw.get("_all_assistant_text") or result_text`), so G2 was a single-line addition to the return dict.
3. All changes strictly within the 5-file scope specified by the plan.

---

Stopping here. Ready for your confirmation before proceeding to Step 2.
Step 1 complete. Here's what was done:

**G1 (runner.py):** Extended the assistant-event content loop to also capture text from `Write` (`input.content`) and `Edit` (`input.new_string`) `tool_use` blocks — fixing the plan-57 root cause where an Output Receipt emitted inside a file-write was invisible to `_all_assistant_text`.

**G2 (parser.py):** Added `_all_assistant_text: ledger_source` to the `parse()` return dict, so `bellows.py:1138`'s defense WARN now reads the full text (tool content included) instead of falling back to `result_text`.

**8 new tests** (2 in test_runner, 4 in test_parser, 2 in test_bellows). Full suite: **684 passed, 0 failed**.

**Deposit:** `knowledge/development/ledger-toolcontent-capture-dev-log-2026-06-14.md`

---

### Ledger Updates

CANARY-FEEDBACK3-153330 — feedback via channel; agent column must populate.
Complete.

---

CANARY-FEEDBACK-124753 — feedback emitted via Output Receipt channel, daemon should record to prompt_feedback DB and regenerate the md.

