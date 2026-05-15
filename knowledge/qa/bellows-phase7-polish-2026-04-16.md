# QA Report — Phase 7 Polish: Flag Format Tolerance + Diagnostic Auto-Close

**Plan:** executable-bellows-phase7-polish-2026-04-16.md
**Step:** 2 (QA)
**Date:** 2026-04-16

## Dev Log Verification

Dev log at `/Users/marklehn/Desktop/GitHub/bellows/knowledge/development/bellows-phase7-polish-2026-04-16.md` — Output Receipt Status: Complete. Proceeding with QA.

## Deliverable Verification Table (Rule 17)

| Deliverable | Expected | Status | Evidence |
|---|---|---|---|
| parser.py handles `## CEO Flag` heading | text `## CEO Flag` or `CEO Flag` present in parser.py | ✅ | grep_deliverables.txt row 1 |
| parser.py handles paragraph flag form | `none` exclusion present with `strip` or `n/a` | ✅ | grep_deliverables.txt row 2 |
| bellows.py has diagnostic auto-close branch | `is_diagnostic` and `auto-close` markers | ✅ | grep_deliverables.txt row 3 |
| bellows.py auto-close logs ledger entry | `log_to_ledger` call present | ✅ | grep_deliverables.txt row 4 |
| bellows.py auto-close moves plan to Done | `Done` path and `shutil.move` | ✅ | grep_deliverables.txt row 5 |
| tests/test_runner_parser.py has new flag format tests | ≥ 3 flag format markers | ✅ | 4 markers found |
| tests/test_bellows.py has auto-close test | `auto` + `diagnostic` markers | ✅ | grep_deliverables.txt row 7 |

All 7 deliverable checks → PASS.

## Test Regression

Command: `python3 -m pytest tests/ -v`
Full output: `knowledge/qa/evidence/executable-bellows-phase7-polish-2026-04-16/pytest_full.txt`

Result summary:

| Metric | Value | Status |
|---|---|---|
| Tests collected | 61 | ✅ |
| Tests passed | 61 | ✅ |
| Tests failed | 0 | ✅ |
| Baseline (phase 7 validation gates) | 55 | — |
| New tests this plan | 6 (5 parser + 1 auto-close) | ✅ |

Zero regressions from the parser and bellows.py changes.

## Behavioral Verification — Parser End-to-End

Script output at `knowledge/qa/evidence/executable-bellows-phase7-polish-2026-04-16/parser_behavioral.txt`:

| Case | Expected | Actual | Status |
|---|---|---|---|
| H2_CEO_Flag_paragraph | `['Pattern-to-chunk linking does not distinguish failure chunks.']` | matches expected | ✅ |
| Bold_CEO_Flag | `['RAISED — architectural decision required']` | matches expected | ✅ |
| H3_Flags_for_CEO_bulleted | `['Flag one', 'Flag two']` | matches expected | ✅ |
| H3_Flags_for_CEO_None | `[]` | matches expected | ✅ |
| H2_CEO_Flag_None_paragraph | `[]` | matches expected | ✅ |

Overall: ALL PASS.

## Behavioral Interpretation

- The H2 paragraph form works — agents writing `## CEO Flag\n\n<body>\n---\n` now produce a non-empty ceo_flags list, which means Gate 2 will correctly fail and a verdict request will be posted. The original bug (silent Gate 2 bypass) is resolved.
- The bold inline form (`**CEO Flag:** RAISED — architectural decision required`) extracts the post-marker text. Output Receipts that use this shorthand now correctly escalate.
- Regression cases for the original H3 + bulleted form and H3 + "- None" continue to work — no prior behaviour lost.
- Paragraph-form "None" (agents writing the exemption in prose rather than a bullet) is correctly excluded from ceo_flags.

The diagnostic auto-close branch is covered by `test_diagnostic_auto_close_moves_to_done` in tests/test_bellows.py (part of the 61-test suite). It asserts: plan file moved to Done/, `verdict.log_to_ledger` called with verdict="auto-close", `notifier.push` invoked. End-to-end behavioural verification on a live Bellows run will happen the next time a diagnostic plan passes all gates — the polish is now in place to catch that case before it strands.

## Rule 20 Self-Check

Literal stdout from the self-check script:

```
============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
Files verified: 3
```

## Output Receipt

**Agent:** Bellows QA
**Step:** 2
**Status:** Complete

### Files Deposited
- `/Users/marklehn/Desktop/GitHub/bellows/knowledge/qa/bellows-phase7-polish-2026-04-16.md`
- `/Users/marklehn/Desktop/GitHub/bellows/knowledge/qa/evidence/executable-bellows-phase7-polish-2026-04-16/grep_deliverables.txt`
- `/Users/marklehn/Desktop/GitHub/bellows/knowledge/qa/evidence/executable-bellows-phase7-polish-2026-04-16/pytest_full.txt`
- `/Users/marklehn/Desktop/GitHub/bellows/knowledge/qa/evidence/executable-bellows-phase7-polish-2026-04-16/parser_behavioral.txt`

### Flags for CEO
- None
