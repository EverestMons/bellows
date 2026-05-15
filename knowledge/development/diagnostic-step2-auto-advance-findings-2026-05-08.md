# Diagnostic: Step 2 Auto-Advance Despite "STOP after Step 1"

**Date:** 2026-05-08 | **Status:** Complete

---

## Q1 — Canonical Step-Pause Decision Logic

The `header_says_pause()` function is at `bellows.py:188-197`:

```python
def header_says_pause(header: dict, current_step: int, total_steps: int, is_qa_step: bool) -> bool:
    """Return True if plan header's pause_for_verdict field matches current step."""
    pv = header.get("pause_for_verdict", "")
    if pv == "always":
        return True
    if pv == "after_step_1":
        return current_step == 1
    if pv == "after_qa_step":
        return is_qa_step
    return False
```

**(a) Recognized `pause_for_verdict` values:**
- `"always"` — pause after every step
- `"after_step_1"` — pause only after step 1
- `"after_qa_step"` — pause only after QA-flagged steps
- Any other value (including empty string or missing) — **returns False** (no pause)

**(b) Return semantics:** Returns `True` if the orchestrator should pause for CEO verdict at the current step. Returns `False` otherwise (no pause; advance automatically).

**(c) Call sites (4 total, all in `bellows.py`):**

| Call Site | File:Line | Context |
|-----------|-----------|---------|
| While-loop guard | `bellows.py:348` | Mid-plan: decides pause-vs-advance between non-final steps |
| Final-step check | `bellows.py:431` | Post-final-step: decides pause-vs-auto-close |
| Final-step reason | `bellows.py:440` | Sets `_pause_reason = "header_pause"` when header triggers |
| Auto-close guard | `bellows.py:467` | Prevents auto-close when header says pause |

---

## Q2 — Step-Completion Code Paths and Pause Decision

After Step 1 completes (runner returns at `bellows.py:298`), the code:

1. Records the run (`bellows.py:305-309`)
2. Runs Mode A detection (`bellows.py:314-326`)
3. Runs gates (`bellows.py:329-338`)
4. Enters the **while loop** at `bellows.py:343`:

```python
while not is_final_step(current_step, total_steps):
```

For a 2-step plan: `is_final_step(1, 2)` = `1 >= 2` = `False`, so the loop body executes.

**Inside the loop, the pause-vs-advance conditional at `bellows.py:344-348`:**

| # | Condition | File:Line | What triggers it |
|---|-----------|-----------|------------------|
| 1 | `not gate_result["passed"]` | :345 | Any gate failure (receipt, errors, scope, etc.) |
| 2 | `gate_result["is_qa_step"]` | :346 | Step header contains "QA" (case-insensitive) |
| 3 | `gate_result.get("verdict_requested", {}).get("requested", False)` | :347 | Agent explicitly deposited a verdict-request file |
| 4 | `header_says_pause(header, current_step, total_steps, gate_result["is_qa_step"])` | :348 | Plan header `pause_for_verdict` field matches |

**If ANY condition is True:** orchestrator pauses, posts verdict request, renames to `verdict-pending-`, returns.

**If ALL conditions are False:** falls through to `bellows.py:377-388`, which immediately launches Step 2 with a new `runner.run_step()` call. No pause, no verdict, no notification.

**Critical insight:** The bootstrap prompt ("STOP. Do NOT proceed to Step 2") is sent to the Claude agent inside `runner.run_step()`. The agent may obey the instruction and report "Complete" at the end of Step 1. But Bellows's orchestrator does not parse the agent's stdout for STOP language. The advance decision is made entirely by the 4-condition check above.

---

## Q3 — Headers from Today's Two Failed Plans

**Plan 1:** `invoice-pulse/knowledge/decisions/Done/executable-action-queue-limit-and-contract-name-2026-05-08.md`

```
# invoice-pulse — Action Queue: Remove LIMIT 200 and Add contract_name to Display
**Date:** 2026-05-08 | **Tier:** Small | **Test Scope:** targeted + full-suite | **Execution:** Step 1 (DEV) → Step 2 (QA)
```

**No YAML frontmatter. No `pause_for_verdict` field.**

**Plan 2:** `bellows/knowledge/decisions/Done/executable-bellows-qa-prefix-and-skip-logging-2026-05-08.md`

```
# bellows — Add `qa-` Prefix to Dispatch Whitelist + Log Silent Skips
```

**No YAML frontmatter. No `pause_for_verdict` field.**

Neither plan declares `pause_for_verdict`. With this field absent, `header.get("pause_for_verdict", "")` returns `""`, and `header_says_pause()` returns `False`. Combined with passing gates and non-QA Step 1, all 4 pause conditions evaluate to `False`, and Bellows advances directly to Step 2.

---

## Q4 — Hypothesis Confirmation: Decision is Purely Header-Based

**Confirmed: the orchestrator NEVER inspects the bootstrap prompt text or agent stdout for STOP language.**

The bootstrap prompt is constructed by Bellows at `bellows.py:274-278`:
```python
bootstrap_prompt = f"Read the plan at {shadow_prompt_path}. Execute Step 1 ONLY. ..."
```

This string is passed to `runner.run_step()` at `bellows.py:298`. The agent receives it, executes, and returns a parsed result. The parsed result is checked only for:
- `receipt_status` (gate 1)
- `ceo_flags` (gate 2)
- `is_error` (gate 3)
- `permission_denials` (gate 4)
- `verdict_requested` (agent-initiated verdict request)

**No field in the parsed result captures "did the agent say STOP?" or "did the prompt instruct the agent to stop?"** The `runner.run_step()` return value has no field for this. The orchestrator never reads `parsed["result_text"]` for STOP-like language.

**Code citation:** The advance decision happens at `bellows.py:343-388`. The only variables consulted are `gate_result` (from `gates.check()`) and `header` (from `gates._parse_plan_header()`). Neither gates.py nor bellows.py contains any code that searches for "STOP", "Do NOT proceed", "wait for confirmation", or similar patterns in the agent output or prompt text.

**This is a fundamental design mismatch:** The Planner writes STOP language in both the bootstrap prompt and the plan body, believing it is authoritative. The Claude agent obeys this instruction and stops after Step 1. But Bellows does not care whether the agent stopped — it only checks gate results and header fields. The STOP language is purely cosmetic from the orchestrator's perspective.

---

## Q5 — Audit of Prior Plans

**Scope:** All `Done/` directories across 8 watched projects.

| Metric | Count |
|--------|-------|
| Total multi-step plans (>= 2 `## STEP` headers) | **631** |
| Plans WITH `pause_for_verdict` header | **4** |
| Plans WITHOUT `pause_for_verdict` header | **627** |

**The 4 plans with `pause_for_verdict` are ALL from bellows, ALL from 2026-04-16 (the day the Phase 8 verdict layer was initially implemented):**
1. `executable-bellows-phase8-verdict-layer-redesign-2026-04-16.md`
2. `executable-bellows-phase8-1-final-step-pause-fix-2026-04-16.md`
3. `executable-verdict-request-pause-reason-2026-04-16.md`
4. `parallel-1-executable-verdict-readme-2026-04-16.md`

These were the hand-crafted test plans used during the initial Phase 8 development. The Planner has **never** emitted `pause_for_verdict` in any production plan across any project.

**The PLANNER_TEMPLATE.md (v4.34) does not mention `pause_for_verdict` anywhere.** The template was designed for the interactive CEO workflow (paste bootstrap prompt, agent stops, CEO types "ok"), not for Bellows orchestration. The template's "How to Run" section describes STOP-and-wait semantics that only work when a human is in the loop — Bellows replaced the human loop with an automated orchestrator that consults header fields, but the template was never updated to emit those fields.

**Breakdown by project (multi-step plans without header / total multi-step):**
- invoice-pulse: ~300+ / ~300+
- bellows: ~80 / ~84
- forge: 66 / 66
- study: 33 / 33
- BrewBuddy: 26 / 26
- anvil: 21 / 21
- ai-career-digest: 8 / 8
- freight-kb: 7 / 7

---

## Q6 — Fix Shape

### Root Cause

**The issue is "Planner omitted required header field."** The `pause_for_verdict` mechanism works correctly in Bellows — the 4 plans that declared it all paused as expected. The Planner has never been instructed to emit this field because the PLANNER_TEMPLATE predates Bellows orchestration and assumes a human-in-the-loop workflow.

### Recommended Fixes

**Fix A — PLANNER_TEMPLATE update (Planner-side):**

File: `/Users/marklehn/Desktop/GitHub/PLANNER_TEMPLATE.md`

In the Output Format section (around line 328-329), where the plan header format is specified, add `pause_for_verdict: after_step_1` to the standard header. The header line template currently reads:

```markdown
**Date:** YYYY-MM-DD | **Tier:** [tier] | **Test Scope:** [targeted | full-suite | both] | **Execution:** Step 1 (AGENT) → Step 2 (AGENT)
```

Should become:

```markdown
**Date:** YYYY-MM-DD | **Tier:** [tier] | **Test Scope:** [targeted | full-suite | both] | **Execution:** Step 1 (AGENT) → Step 2 (AGENT) | **pause_for_verdict:** after_step_1
```

Additionally, add a brief rule in the Bellows Execution Model section explaining the recognized values (`always`, `after_step_1`, `after_qa_step`) and that this field is required for multi-step plans.

**Estimated LOC:** ~5-10 lines added to PLANNER_TEMPLATE.md.

**Fix B — Bellows defensive default (Bellows-side):**

File: `bellows/bellows.py`

In `header_says_pause()` (line 188-197), change the default behavior when `pause_for_verdict` is not declared. Currently:

```python
pv = header.get("pause_for_verdict", "")
# ... if no match ...
return False  # ← auto-advance by default
```

Proposed: when `pause_for_verdict` is not declared AND the plan has multiple steps, default to pausing after Step 1:

```python
pv = header.get("pause_for_verdict", "")
if not pv:
    # Defensive default: pause after step 1 for multi-step plans
    # unless auto_close is explicitly true
    return current_step == 1
```

Alternatively, emit a startup-time warning when a multi-step plan is dispatched without `pause_for_verdict`:

```python
if total_steps > 1 and not header.get("pause_for_verdict"):
    print(f"Bellows: WARNING — {plan_name} has {total_steps} steps but no pause_for_verdict header. Defaulting to after_step_1.")
```

**Estimated LOC:** 3-8 lines in `bellows.py`.

### Independence

**Fix A and Fix B are fully independent and can ship separately.** Fix A prevents future occurrences by ensuring the Planner always emits the field. Fix B prevents the failure mode even when the Planner omits it. Both should ship, but Fix B is the higher-priority defensive layer — it eliminates the entire class of bugs regardless of Planner behavior.

---

## Output Receipt: Complete
