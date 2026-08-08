# Verdict File Format

## Purpose

Bellows pauses plan execution under five conditions. The Planner writes a verdict file to `verdicts/resolved/` to tell Bellows how to proceed. Two additional codes (`auto_close`, `clean_gate_auto`) are recorded transition codes for mechanical advances — they are NOT pauses but exist so the transition is auditable in the `verdicts` table.

| Pause Reason / Code | Trigger |
|---|---|
| `gate_failure` | A step's gate check did not pass |
| `qa_checkpoint` | Plan header marks a step as a QA checkpoint |
| `agent_verdict_request` | The executing agent explicitly requested a verdict |
| `header_pause` | Plan header contains a `pause_for_verdict` mode that matches the current step (e.g. `always`, `after_step_1`, `after_qa_step`, `qa_and_terminal`) |
| `auto_close_disabled` | Auto-close is disabled for the plan |
| `auto_close` | Mechanical terminal auto-close (recorded since plan 313; not a pause) |
| `clean_gate_auto` | Mechanical clean-gate non-terminal advance (not a pause; row exists so the transition is auditable) |

The `qa_and_terminal` header mode pauses at QA steps and at the terminal step. At the terminal step this mode takes precedence over `auto_close: true` — a plan setting both gets the terminal pause. A terminal-step pause under this mode records `pause_reason_code=header_pause` (indistinguishable in the table from an `always` pause).

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
