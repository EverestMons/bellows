# Dev Log — tools-safe-to-invoke — 2026-09-11

## Pins re-derived (P1, P3)

33 files (20 `tools/*.py`, 13 `scripts/*.py`); import-time writes: 2 (`cycle_log_projection_census.py:49`, `register_coverage_census.py:68`); absolute home paths: 5 files, one each (`battery_census.py:37`, `cycle_log_projection_census.py:38`, `cycle_log_signal_census.py:404`, `fold_signal_census.py:55`, `register_coverage_census.py:43`); tools without a parser: 5 (`cycle_log_projection_census`, `cycle_log_signal_census`, `qa_steps_parse_census`, `run_check`, `register_coverage_census`); the 15 tools with a parser all call `parse_args()` before any call that could write (11 inside a function, 4 in the script entry: `clear_plan`, `deposit_receipt`, `issue_verdict`, `link_live_commands`); `run_check.py --help` prints its own usage and exits 2

P1 line numbers confirmed: battery_census.py:37, cycle_log_projection_census.py:38/:49/:418–419, cycle_log_signal_census.py:179/:404, fold_signal_census.py:55/:684–689, register_coverage_census.py:43/:68/:650, qa_steps_parse_census.py:372/:376/:390. No mechanism mismatch.

## Failing-first (red, then green)

Red: `4 failed in 2.00s` — t1: 5 absolute-path hits (battery_census:37, cycle_log_projection:38, cycle_log_signal:404, fold_signal:55, register_coverage:43); t2: 2 import-time open() hits (cycle_log_projection:49, register_coverage:68); t3: 5 static failures (battery, cycle_log_projection, cycle_log_signal, fold_signal, register_coverage) plus qa_steps_parse_census producing no usage line; t4: 2 writers failed static check (listed unrun).

Green: `4 passed in 4.20s` after six tool edits. Full suite: `2299 passed, 2 skipped in 116.27s`.

## The trees before and after

Before red run: `git -C /Users/marklehn/Developer/bellows status --porcelain -- knowledge/qa/evidence` → (empty)

After red run: `git -C /Users/marklehn/Developer/bellows status --porcelain -- knowledge/qa/evidence` → (empty)

## Mutation run

MUTATION: 4 killed, 0 survived, 0 error
