# QA Report — walk-register-schema-2026-08-10

**Plan:** walk-register-schema-2026-08-10
**Step:** 3 — QA
**Branch:** bellows-wt/338

---

## Deliverable Verification

| # | item | status | evidence |
|---|---|---|---|
| 1 | Nothing wired in — `plan_lint.py` and `gates.py` unchanged, no gate chain imports validator | ✅ | `git status --porcelain -- scripts/plan_lint.py gates.py` empty; `git diff -- scripts/plan_lint.py gates.py` empty; `grep -rn "walk_register_lint\|walk_register" gates.py scripts/plan_lint.py` returns NO MATCHES |
| 2 | Validator is standalone and warn-only — no code path alters any exit code the daemon reads | ✅ | `sys.exit` calls at lines 251 (no args → exit 0), 259 (no files → exit 0), 264 (target not found → exit 1); none of these are read by the daemon; the validator emits TSV to stdout and status to stderr only |
| 3 | `pre_fold_text` is required and the check can FAIL — schema states it required; constructed missing-field test exercised and WARN fires | ✅ | `test_missing_pre_fold_text_warns` PASSED: constructed row with empty `pre_fold_text` cell produces `WARN` with `missing=pre_fold_text, note=missing_fields`; `test_empty_pre_fold_text_warns` PASSED: same assertion path; schema line 42 states `pre_fold_text` **yes** required |
| 4 | Dialects are reported, never dropped; `PRE-SCHEMA` is distinct from `UNCONFORMANT` — unconformant file names actual columns; two-shape file names both; file with no `schema_version` declaration returns `PRE-SCHEMA` | ✅ | `test_pre_schema_status` PASSED: file with fold table but no declaration returns `PRE-SCHEMA`; `test_schema_version_in_prose_is_pre_schema` PASSED: `schema_version` only in prose returns `PRE-SCHEMA`; `test_two_shape_file` PASSED: file with 8-column and 3-column fold tables returns `UNCONFORMANT` with 2 shapes reported; existing-registers-run.txt shows both D.1 files as `PRE-SCHEMA` while this cycle's register is `UNCONFORMANT` |
| 5 | Baseline registers were measured, not edited — D.1 blob IDs match Step 2's recorded values | ✅ | `git hash-object` on current files: `walk-register-group4-rescope-2026-08-10.md` = `ef2fa9e43a04ec2a08941ae2f9774b714bbd8b07`; `walk-register-lint-class-recall-2026-08-10.md` = `7e707163c06725caa23054a2513236a3212da41a`; both match D.3's recorded blob IDs exactly; raw run deposited at `knowledge/qa/evidence/walk-register-schema-2026-08-10/existing-registers-run.txt` |
| 6 | Authoring-time counts re-measured — Task B figures stated against the Why section | ✅ | Re-enumeration via `git log --all --name-only --format="" \| grep -F "walk-register" \| sort -u` returns 4 paths (3 registers + 1 draft); Step 1 Task B found the same. Authoring said 2 committed (+ this cycle's = 3); measured 3 confirmed. Authoring said 3 shapes; Step 1 re-measured 5 distinct fold-table shapes in the original two files (authoring missed 2). This was reported as a finding in Step 1 — shape population is larger than stated, strengthening the rationale |
| 7 | Full suite passes with `test_walk_register_lint.py` collected | ✅ | `python3 -m pytest`: 979 passed, 1 warning in 25.31s; `tests/test_walk_register_lint.py` collected 19 tests, all 19 passed |
| 8 | Raw output — every count in this receipt is the command's own stdout | ✅ | All counts pasted from command output directly |
| 9 | Pipe AND backslash round-trip — `\|`, `\\`, and `\\|` each byte-compared; unescaped corruption shown | ✅ | `test_pipe_escape_round_trip` PASSED: `foo\|bar` escaped to `foo\\|bar`, unescaped back byte-identical; `test_backslash_escape_round_trip` PASSED: `foo\\bar` escaped to `foo\\\\bar`, unescaped back byte-identical; `test_backslash_pipe_escape_round_trip` PASSED: `foo\\|bar` escaped to `foo\\\\\\|bar`, unescaped back byte-identical; `test_unescaped_pipe_corrupts_row` PASSED: escaped row has 8 cells, unescaped has 9 (corrupted) |
| 10 | Per-row conformance emitted and truncation rejected | ✅ | Constructed 4-row fixture: row 1 (verbatim bytes) = `OK`; row 2 (ellipsis `...` in `pre_fold_text`) = `WARN` with `truncated_pre_fold_text`; row 3 (`ADDITION`) = `OK`; row 4 (empty `pre_fold_text`) = `WARN` with `missing_fields`. Per-row marks emitted, not per-file only. `test_truncated_pre_fold_text_warns` PASSED: fixture with `the exact bytes... more` in `pre_fold_text` marked `WARN` with `truncated_pre_fold_text` |
| 11 | Plan carries no history-only paragraph; `ADDITION` exercised | ✅ | Scanned the plan: `## Why this exists` and `## Drafting Cycle` are the two stated C6 exemptions. No other paragraph exists solely to record how a constraint arrived — every paragraph outside those sections states a constraint, a boundary, or an instruction. `test_addition_literal_conformant` PASSED: `ADDITION` literal in `pre_fold_text` returns `OK`, `CONFORMANT`; `test_empty_pre_fold_text_warns` PASSED: empty field returns `WARN`, `UNCONFORMANT` |

---

## Rule 20 — QA Self-Check Results

*(Run after the verification table above is complete — see next section for raw output.)*

---

## Rule 20 Self-Check Raw Output

```
============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
Evidence folder: /Users/marklehn/Developer/GitHub/bellows/.bellows-worktrees/338/knowledge/qa/evidence/walk-register-schema-2026-08-10/
Files verified: 1
```
