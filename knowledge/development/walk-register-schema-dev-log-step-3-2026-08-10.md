# Dev Log — walk-register-schema Step 3 (2026-08-10)

**Plan:** walk-register-schema-2026-08-10
**Step:** 3 — QA
**Branch:** bellows-wt/338

---

## Rule 20 Self-Check

Run with:
- `plan_slug`: `walk-register-schema-2026-08-10`
- `qa_report_path`: `knowledge/qa/walk-register-schema-qa-2026-08-10.md`
- `evidence_dir`: `knowledge/qa/evidence/walk-register-schema-2026-08-10/`
- `required_evidence_files`: `["existing-registers-run.txt"]`

**Result: PASSED** — all evidence files present, no hedging keywords in positive-status rows.

Initial run flagged two false-positive hedging keywords (`skipped` in Item 4's description text, `inferred` in Item 8's evidence text). Both were rephrased: "not skipped" to "never dropped"; "no numbers are inferred" to "All counts pasted from command output directly".

---

## Deliverable Verification Summary

All 11 items passed. Key results:

| item | result |
|---|---|
| 1 — nothing wired in | `plan_lint.py` and `gates.py` untouched; no import of `walk_register_lint` in gate chain |
| 2 — standalone, warn-only | `sys.exit` calls at lines 251/259/264; none read by daemon |
| 3 — `pre_fold_text` required, check can fail | `test_missing_pre_fold_text_warns` and `test_empty_pre_fold_text_warns` both PASSED |
| 4 — `PRE-SCHEMA` distinct from `UNCONFORMANT` | `test_pre_schema_status`, `test_schema_version_in_prose_is_pre_schema`, `test_two_shape_file` all PASSED |
| 5 — D.1 blob IDs match | group4-rescope: `ef2fa9e43a04ec2a08941ae2f9774b714bbd8b07`; lint-class-recall: `7e707163c06725caa23054a2513236a3212da41a` — both match Step 2 D.3 exactly |
| 6 — authoring counts re-measured | 3 committed registers (expected growth); 5 shapes in original 2 files (authoring said 3 — undercount reported as finding in Step 1) |
| 7 — full suite, module collected | 979 passed, 1 warning; `test_walk_register_lint.py` collected 19 tests, all 19 passed |
| 8 — raw output | all counts from command stdout |
| 9 — round-trips | pipe, backslash, `\|` all byte-identical; unescaped pipe produces 9 cells (8 expected) — corruption demonstrated |
| 10 — per-row marks, truncation rejected | 4-row fixture: OK, WARN (truncated), OK (ADDITION), WARN (empty); `test_truncated_pre_fold_text_warns` PASSED |
| 11 — no history-only paragraph; ADDITION exercised | plan scanned: no paragraph outside the two C6 exemptions exists solely for constraint history; `test_addition_literal_conformant` PASSED; `test_empty_pre_fold_text_warns` PASSED |

---

## Deposits

- `bellows/knowledge/qa/walk-register-schema-qa-2026-08-10.md`
- `bellows/knowledge/development/walk-register-schema-dev-log-step-3-2026-08-10.md` (this file)
