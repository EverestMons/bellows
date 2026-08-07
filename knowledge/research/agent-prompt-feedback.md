# Agent Prompt Feedback

None — the plan's specifications were unambiguous and the implementation followed them directly.

Now let me commit all the QA artifacts.
Step 2 (QA) complete. Committed as `e22f0a8`.

- Task Q0's re-pin requirement (confirm Step 1 commit + pin corpus HEADs) added value — the bellows HEAD had moved past the Step 1 commit (docs regeneration at `399c01b`), and without the pin this would have been invisible.
- The plan's instruction to confirm WARN-only by mechanism (grep for `results`/`all_passed` references) rather than by symptom (exit code alone) caught the string-literal false positive in the mechanism grep itself — the word "results" appears in check (h)'s print message. The programmatic verification excluding the string literal was necessary for a clean assertion.

None — the plan was executed as written with no ambiguity requiring feedback.

None — the plan was executed as written with no ambiguity requiring feedback.

(none)

The plan's verification structure was thorough and well-calibrated. The row 3 `sed` extraction with `$d` on both sides worked correctly even with the new class adjacent — the plan's specific warning about this being required proved accurate. The single-item byte-identity test (row 5) required loading the pre-change module via `importlib` with `PYTHONPATH` set, matching plan 286's countermeasure. The threshold discriminator (test 1 in task D) is the strongest guard — it is the only test that distinguishes `>=2` from `>=1`, and its absence would let a guard-inverting implementation pass the entire suite.

The diagnostic's §Q4 implementation was directly usable as written — the 8-line sanitizer dropped into the module with only the routing change in `_append_forward_row` needed to integrate it. The plan's explicit mandate to NOT strip bullet markers and to ship §Q4 verbatim prevented a byte-for-byte-unchanged violation that an earlier draft would have introduced. The threshold discriminator test (Task D item 1) is the strongest guard in the set — without it, a `>=1` implementation passes every other test while inverting plan 62's guard.

The diagnostic's corpus-sweep method (grep for `#### Forward Register` across all watched projects, then extract and classify each block) was well-designed. The plan's mandatory positive and negative controls (plan 62 fixture + plan 288/289 multi-item blocks) caught a wrapped-prose weakness in the first candidate tested. The explicit instruction to report per-block results rather than aggregates forced transparent evidence. The requirement to test in `/tmp` prevented accidental edits to the live system. The only factual error in the diagnostic was the plan 288 vs. 289 attribution of the six-item block, which the corpus sweep corrected.

- The plan's three-numbering-system warning (CEO Context) was respected throughout QA — gap-map rows, dev-log items, and QA verification rows are distinct.
- Row 9's three-sub-claim structure (9a/9b/9c) was valuable — each tests a different failure mode (lost commit vs foreign interference vs scope violation) and requires different escalation.
- The drift-check row (10) requiring both literal hashes prevents a vacuous "match" assertion — the check is reproducible from the report alone.
- The mutual exclusivity test for row 4 required a custom fixture with dry lens lines AND fold-mentioning Closing prose — the plan's instruction to test this specifically was essential, since an unchecked unconditional status path would have silently re-created CB1's false-WARN class.

- The plan's three-numbering-system warning (CEO Context) was valuable — gap-map rows, dev-log items, and QA rows are indeed distinct.
- The fixture-isolation requirement (plan 280's f-h discipline) was correctly extended to include the fifth marker (`no **Closing:** line`) now that fix (c) makes the missing-Closing WARN reachable. This was stated in the plan and was not an oversight.
- The DESIGN FORK on (b) was correctly resolved by the negation-aware whole-line rule. The plan's correction about plan 275 being the real counterexample to the `;`-split design was verified by execution.
- The wrapper-vs-content distinction for real-log fixtures was important: the DC block content is verbatim, but the header wrapper must be constructed to avoid triggering blocking checks (e) and (c) that are irrelevant to the `(f)` checks being tested. The existing fixtures (271, 274, 275, diag-276) already followed this pattern.

No prompt feedback. Plan was clear; the verification rows were well-specified and unambiguous. The dev-log provided all necessary raw output for cross-checking.

No prompt feedback to report. Plan was clear and unambiguous; test text was verbatim-applicable; insertion point and scope were well-specified.

- The dev-log stated "13 new tests added" but the actual count is 12 new test functions (the `_fold_closing_warns` edit was a fixture change to an existing test, not a new test). Minor dev-log inaccuracy — the tests themselves are correct and comprehensive.
- The CB1 safe rule (fold-token AND no-dry) correctly prevents false fold-WARNs on all 4 real-log embedded fixtures (271/274/275/diag-276), which contain the `→ dry. N folds cohere` pattern that would have false-WARNed under the diagnostic's naive `;`-split approach.
- The `\b` regex fix for 190 is clean — confirmed a single occurrence at line 165, accepts bare T0/T1/T2 + collapsed T0 form, rejects T3/T0X.

- The CB1 safe rule (fold-token AND no-dry) is the decisive design contribution of the cold panel — the warm walks' naive `;`-split "last segment" approach would have false-WARNed on every real Walk-3 ACID line containing `dry. N folds cohere`. The plan correctly embedded CB1 into Task B's specification.
- The diagnostic's §Q2 sketch (`;`-split last segment) was correctly flagged as WB1 (sketched, not final) — the DEV-authored parser uses a whole-line regex + SAFE rule instead. Rule 27 honored (diagnostic designs referenced, not blindly copied).
- Task C's fixture-only edit worked cleanly because the WARN message was preserved (CB2) — no assertion changes needed.
- The real-log embedded fixtures (V1) are high-value — they catch parser regressions against the actual mixed formats (`.`/`→`/`; wN dry`/cold-panel lines) that idealized fixtures would miss.

- Verification item 2 says "plan_lint on Done/executable-270.md emits NO drafting-cycle WARN" — but plan 270 legitimately emits the cold-panel WARN because it predates the Cold panel requirement. The DEV step correctly flagged this. The test fixture (COMPLIANT_T2_PLAN) uses 270's real block with the Cold panel line added, which does pass clean. Consider adjusting the plan's verification wording to reference the test fixture rather than the raw 270 file, since 270 is not fully compliant by current standards.

- The plan specified "Use the real block in executable-270.md (a genuine T2 Cycle Log) as a fixture input" for the compliant-T2 test, expecting "NO cycle-cycle WARN." However, plan 270 has no `**Cold panel (T2):**` line (it was the first plan with a Cycle Log, predating the Cold panel requirement). The test fixture uses plan 270's real block with the Cold panel line added to make it compliant. The live-run output above shows the WARN correctly firing on the unmodified plan 270.

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

