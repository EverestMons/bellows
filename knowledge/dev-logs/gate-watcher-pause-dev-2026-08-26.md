# Dev Log — gate-watcher-pause (exec-571, Step 1)

**Date:** 2026-08-27 (plan dated 2026-08-26)

## Diff summary

- **tools/gate_watcher.py**: added `import glob`; extended docstring with pause-detection paragraph; `read_state` gains optional `pending_dir` kwarg; after the `fails` query, non-terminal states glob `verdicts/pending/verdict-request-{plan_id}-step-*.md` — hits → phase `awaiting-verdict` with `pending` list; `judge_transition` appends `pending=…` when present; `main` adds `--pending-dir` argument threaded through both `read_state` call sites.
- **tests/test_gate_watcher.py**: added `TestPauseDetection` class with 7 constructed-state tests (paused plan, foreign-id isolation, terminal-ignores-stray, empty-dir negative control, derived pending dir, transition line format, resume transition).

## Pin re-derivations

| Pin | Plan value | Re-derived value | Notes |
|-----|-----------|-----------------|-------|
| P1 | `abandoned, closed, halted` (+`in_progress` while running); `awaiting_verdict` ABSENT | `abandoned, closed, halted, in_progress` — `awaiting_verdict` ABSENT in `plans.lifecycle_state` | Supersedes: plan said "3 rows at authoring because none was in-flight"; re-derivation shows 4 distinct values (a plan is currently in_progress). Consistent with the pin's core claim. |
| P2 | `bellows.py:1097` and `:1230` write `awaiting_verdict` to `steps.status` only on gate failure; no writer targets `plans.lifecycle_state` | `bellows.py:1097` and `:1230` confirmed; also `:138` (comment only). `lifecycle.py:46` CHECK arm includes `awaiting_verdict` for plans but no writer targets it (phantom). `lifecycle.py:89` CHECK for steps, `:167`/`:195` query arms. | Consistent — the phantom CHECK arm is exactly what the plan describes. |
| P3 | `verdict.py:180-188` writes `verdict-request-{slug}-step-{N}.md`; `slug_from_path` at `:85-95` | `post_verdict_request` at `:181`; `slug_from_path` at `:85`, called at `:186`. Resolved artifacts confirmed in `verdicts/resolved/`. | Supersedes: line numbers shifted by 1 (`181` vs plan's `180`). Core claim holds. |
| P4 | `tools/gate_watcher.py` `read_state()` `:35-65`; `TERMINAL` at `:32`; `judge_transition` `:68-81` | Pre-edit: `read_state` `:35-65`, `TERMINAL` `:32`, `judge_transition` `:68-81`. Exact match. | Consistent. |
| P5 | 9 tests; full suite baseline 1531 passed | 9 baseline tests confirmed (`--collect-only`). Full suite baseline not re-run (DEV scope — plan says "DEV runs NO full suite"). | Consistent on the testable half. |

## Targeted test output (raw)

```
................                                                         [100%]
16 passed, 1 warning in 0.25s
```
