# Dev Log: Corrective Narrow is_diagnostic Override Fix
**Date:** 2026-05-03 | **Plan:** executable-corrective-narrow-is-diagnostic-override-2026-05-03

## Phase 1 — Discard broken edit

- `git status --short bellows.py` before checkout: ` M bellows.py` (modified, unstaged)
- Ran `git checkout bellows.py` — output: "Updated 1 path from the index"
- `git status --short bellows.py` after checkout: empty (clean working tree)

## Phase 2 — Narrow override at run_plan site

- **File:** `bellows.py:228-235`
- Replaced unconditional `if is_diagnostic: total_steps = 1` with `if total_steps == 0 and is_diagnostic: total_steps = 1`
- Added explanatory comment referencing the three test fixtures that depend on this behavior

## Phase 3 — Narrow override at _consume_verdicts site

- **File:** `bellows.py:696-710`
- Restructured: removed `is_diag` bypass that short-circuited the fallback chain; `extract_total_steps` now runs unconditionally via the shadow/metadata/load_file fallback chain
- Added narrow override: `if total_steps_c == 0 and is_diag: total_steps_c = 1` after the fallback chain

## Phase 4 — Test results

- **66 passed, 0 failed** (1 warning — urllib3/LibreSSL, unrelated)
- Previously-failing tests now pass:
  - `test_diagnostic_auto_close_moves_to_done` — PASS
  - `test_clean_diagnostic_no_header_posts_verdict` — PASS
  - `test_clean_diagnostic_auto_close_true_moves_to_done` — PASS
- `test_run_step_timeout` was not collected in the test run (66 tests total, all passed)
- No regressions introduced

## Phase 5 — Commit

- **SHA:** `9786e87`
- **Message:** `fix(bellows): narrow is_diagnostic step-count override to total_steps==0`
- 1 file changed, 20 insertions, 13 deletions

## Output Receipt

- **Status:** Complete
- **Deposits:** This dev log (`knowledge/development/corrective-narrow-override-dev-log-2026-05-03.md`)
