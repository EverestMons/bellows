# QA Report — Per-Plan Model Override + Gate 5 Backtick Fix
**Date:** 2026-04-17 | **Plan:** `executable-model-override-backtick-fix-2026-04-17` | **Step:** 2 (QA)

## Dev Log Check
- **Output Receipt:** Complete
- **Files changed:** `bellows.py`, `gates.py`, `runner.py` (verified, no changes needed)
- **Commits:** `feat: per-plan model override via **Model:** header field` (dfb199f), `fix: gate 5 — strip leading/trailing backticks from deposit paths` (8d8a613)

## Deliverable Verification

| # | Check | File | Status |
|---|-------|------|--------|
| a1 | `_parse_plan_header` strips `**` from keys via `strip("*")` | gates.py:26 | ✅ |
| a2 | `_parse_plan_header` strips `**` from values | gates.py:27 | ✅ |
| a3 | Early header parse in `run_plan` before first `run_step` | bellows.py:203 | ✅ |
| a4 | Model extracted with fallback chain `Model` -> `model` -> `default_model` | bellows.py:204 | ✅ |
| a5 | `model` passed to `runner.run_step` (bootstrap call) | bellows.py:237 | ✅ |
| a6 | `model` passed to `runner.run_step` (continuation loop) | bellows.py:293 | ✅ |
| a7 | Conditional print for model override | bellows.py:224-225 | ✅ |
| b | `runner.run_step` uses `model` parameter in `--model` flag, not hardcoded | runner.py:36 | ✅ |
| c1 | Agent-declared deposit paths strip backticks both ends | gates.py:140 | ✅ |
| c2 | Plan-required deposit paths (Pattern 2) strip backticks | gates.py:171 | ✅ |
| d | Manual test: `'\`invoice-pulse/knowledge/foo.md'.strip('\`')` -> `invoice-pulse/knowledge/foo.md` | python3 -c | ✅ |

## Evidence
- `knowledge/qa/evidence/executable-model-override-backtick-fix-2026-04-17/grep_deliverables.txt`

## Verdict
All 11 checks verified against live code via grep. Manual backtick test passed. Evidence file deposited.
