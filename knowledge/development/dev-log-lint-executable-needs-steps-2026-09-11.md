# Dev Log — lint-executable-needs-steps-2026-09-11

**Plan:** 100078 | **Thread:** 13 | **Date:** 2026-09-11

## Pins re-derived (P1, P2, P3)

P4 (verbatim): "an executable with H3 '### Step' headers and no qa_steps field lints CLEAN at exit 0 (fixture-measured both ways)"; PT `:445` "The `## STEP N — AGENT` header is ALL CAPS"; PT `:449` `qa_steps` is required only for plans WITH QA steps

P1 re-derived (`sed -n 414,428p scripts/plan_lint.py` on pre-edit, now at `:434–452`): `step_headers = re.findall(r'^(## STEP (\d+)\b[^\n]*)', clean_text, re.MULTILINE)` at `:434`; the new arm `if not step_headers and _is_executable(plan_path, header):` at `:438`; the existing `qa_steps` arm unchanged below it; `_LIFECYCLE_PREFIX_RE` at `:31`; `_is_executable` at `:382`. No mechanism mismatch — the pre-edit arm fired only when `qa_steps` was declared; that condition is unchanged in the existing arm; the new arm is independent.

P2 re-derived (test file): `(e-a)` at `:306` (title-case headings with `qa_steps: 2` → FAIL), `(e-b)` at `:335` (uppercase → no row), `(e-c)` at `:341` (single-step diagnostic, no `qa_steps`, no headings → no row, exit 0). Four new tests added at `:372`–`:456`: (e-e) executable H3 headings → FAIL, (e-f) executable uppercase → no (e), (e-g) diagnostic with Execution field → no (e), (e-h) ready-executable no headings → FAIL.

P3 re-derived (`grep -nF 'total_steps_c == 0 and is_diag' bellows.py`): `:3319` — `if total_steps_c == 0 and is_diag: total_steps_c = 1`. Tolerance unchanged. An executable with zero headings still has zero steps and runs nothing (the new FAIL fires at admission; the daemon's path is not reached).

## Failing-first (red, then green)

Red (t1 and t4 failing before the edit): `2 failed, 2 passed, 148 deselected in 0.54s`

Green (full suite after the edit): `2266 passed, 1 skipped in 100.15s (0:01:40)`

## Mutation run

`MUTATION: 3 killed, 0 survived, 0 error`
