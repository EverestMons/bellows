# Verdict File Format

## Purpose

Bellows pauses plan execution under five conditions. The Planner writes a verdict file to `verdicts/resolved/` to tell Bellows how to proceed.

| Pause Reason | Trigger |
|---|---|
| `gate_failure` | A step's gate check did not pass |
| `qa_checkpoint` | Plan header marks a step as a QA checkpoint |
| `agent_verdict_request` | The executing agent explicitly requested a verdict |
| `header_pause` | Plan header contains `pause_for_verdict: true` |
| `auto_close_disabled` | Auto-close is disabled for the plan |

## Naming

```
verdict-<id>-step-<N>.md
```

`<id>` = the plan's integer id (id-native plans). Legacy plans: `<plan-slug>` = plan filename with leading prefix (`in-progress-`, `verdict-pending-`, `executable-`, `diagnostic-`) and `.md` stripped — dual-format tolerance accepts both. In all cases the mechanical rule: copy the verdict-request filename and replace `verdict-request-` with `verdict-`.

Example: `diagnostic-foo-bar-2026-04-16.md` → `verdict-foo-bar-2026-04-16-step-1.md`

## Format

First line **must** match `^verdict:\s*(continue|stop)$` (case-insensitive). All subsequent lines are freeform reason text.

- `continue` — proceed to next step (or move plan to `Done/` if final step)
- `stop` — halt the plan; Bellows renames plan file with `halted-` prefix

## Where to Write

Drop files in `bellows/verdicts/resolved/`. Bellows scans every 30 s via `_consume_verdicts()` and renames consumed files with a `processed-` prefix.

## Worked Example

`verdicts/resolved/verdict-foo-bar-2026-04-16-step-1.md`:
```
verdict: continue
Gate passed on manual review. Proceeding to Step 2.
```
