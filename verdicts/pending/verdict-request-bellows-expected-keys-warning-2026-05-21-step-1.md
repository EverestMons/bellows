# Verdict Request

**Plan:** /Users/marklehn/Developer/GitHub/bellows/knowledge/decisions/in-progress-diagnostic-bellows-expected-keys-warning-2026-05-21.md
**Project:** /Users/marklehn/Developer/GitHub/bellows
**Step:** 1
**Log:** /Users/marklehn/Developer/GitHub/bellows/logs
**Timestamp:** 2026-05-21T11:35:51.034113
**Pause Reason:** Header pause (pause_for_verdict)
**Pause Reason Code:** header_pause
**Deposit:** bellows/knowledge/research/bellows-expected-keys-warning-2026-05-21.md
**Gate Result Passed:** True
**Total Steps:** 1

## Pause Reason

The plan header specifies `pause_for_verdict`. This step is complete;
CEO review is required before the next step begins.

## Verification Results

| Check | Result | Detail |
|---|---|---|
| receipt_status | PASS | Status: Complete |
| ceo_flags | PASS | No flags raised by agent |
| errors | PASS | No errors reported in step output |
| permission_denials | PASS | No blocking permission denials |
| deposit_exists | PASS | All agent-declared deposits present on disk |
| qa_step_detection | PASS | Not a QA step |
| file_change_audit | PASS | 0 files modified |
| scope_check | PASS | All changes within plan scope |
| rule_20_self_check | PASS | N/A (not a QA step) |
| rule_22_verification | PASS | Plan-declared deposits present on disk |
| intermediate_decisions | INFORMATIONAL | 1 phrase-matched blocks |

## Planner-Only Checks Remaining

Bellows verified mechanical pass/fail. The Planner still verifies:
- (b) Does the deposited content actually answer the original question or fix the original bug?
- Substance of any FAIL rows above — Bellows surfaces the failure but does not interpret it.
- Plan-shape considerations not encoded in gates (e.g., recursion-risk constraints from LESSONS).

## Files Changed


## Intermediate Decisions Detected

1 phrase-matched blocks. Review for agent decisions narrated mid-step:

- **Event 153:** Complete.

**Summary of findings:** The `expected_keys` warning at `bellows.py:416-419` treats 5 header keys equally, but only 1 is safety-critical at runtime:

- **`pause_for_verdict`** — safety-critical: controls pause/auto-advance routing via `header_says_pause()`.
- **`project`, `date`, `author`, `total_steps`** — all cosmetic: zero runtime consumers. `project_path` is derived from filesystem, step count from `## STEP N` headers, and `date`/`author` are pure metadata.

The warning fires on ~ _(matched: actually)_
