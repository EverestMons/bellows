# Phase 3 Diagnostic: Reproduce Bellows Bugs
**Date:** 2026-04-15 | **Type:** Reproduction investigation | **Phase:** 3 of 4

---

## Q1 — Log Inspection (Hypothesis B: "Unknown" Status)

### Log inventory

30 log files in `logs/`, ranging from Apr 13 (earliest named logs) to Apr 15 09:09 (most recent timestamped log). Mix of manually-named logs (e.g., `scaffold-step1.json`) and Bellows-generated timestamped logs (e.g., `20260415-090926-step.json`).

### JSON structure

All log files share the same `claude -p --output-format json` structure:

```json
{
  "type": "result",
  "subtype": "success",
  "is_error": false,
  "duration_ms": ...,
  "num_turns": ...,
  "result": "...",          // ← agent's final conversational text
  "stop_reason": "end_turn",
  "session_id": "...",
  "total_cost_usd": ...,
  "modelUsage": { ... },
  "permission_denials": []
}
```

### `result` field inspection

Scanned all 30 log files for `**Status:** Complete` in the `result` field:

| File | has `**Status:**`? | Model | `stop_reason` |
|------|-------------------|-------|---------------|
| runner-parser-step1.json | **YES** | claude-sonnet-4-6 | end_turn |
| runner-parser-step2.json | **YES** | claude-sonnet-4-6 | end_turn |
| All other 28 files | **NO** | mixed | end_turn |

**Only 2 of 30 log files** contain `**Status:** Complete` in the `result` field. These are the earliest runs (runner-parser, Apr 13). All subsequent agents write the Output Receipt to deposited markdown files only — their conversational `result` text says things like "Step 1 complete" or "**Complete.**" without the formatted `**Status:** Complete` pattern.

### Verbatim examples

**Most recent log (20260415-090926-step.json):**
```
"result": "Step 1 complete. Marker file written to `knowledge/research/bellows-sanity-check-2026-04-15.md`. Waiting for your confirmation to proceed to Step 2."
"stop_reason": "end_turn"
```
No `**Status:** Complete` present.

**Source-SHA Step 2 (20260414-160502-step.json):**
```
"result": "Step 2 complete. Summary:\n\n**QA Results — all green:**\n| Check | Result |\n..."
"stop_reason": "end_turn"
```
No `**Status:** Complete` present.

**runner-parser Step 1 (the only file WITH the pattern):**
```
"result": "---\n\n**Step 1 complete.**\n\n## Output Receipt\n**Agent:** Claude Sonnet 4.6\n**Step:** 1 (DEV)\n**Status:** Complete\n..."
```
`**Status:** Complete` IS present — this agent included the full Output Receipt in its spoken output.

### Conclusion

**Hypothesis B CONFIRMED.** The parser at `parser.py:14-19` searches `result_text` for `**Status:** Complete`, but 28/30 agents never include this pattern in their conversational output. Only the very earliest runs (runner-parser, Apr 13) included the Output Receipt in their spoken response. All subsequent agents evolved to write the receipt only in deposited files.

`stop_reason` is `"end_turn"` for ALL normal completions — a reliable signal for Phase 4's parser fix.

---

## Q2 — Minimal Reproduction Plan

Created `/tmp/bellows-repro-test-2026-04-15.md` with:
- Standard diagnostic header
- `## STEP 1 — Reproduction Agent`
- Task A: write marker file (`REPRO_OK` to `/tmp/bellows-repro-marker.txt`)
- Task B: move plan to `/tmp/bellows-repro-done/` (move-to-Done)
- Claim-first instruction (rename to `in-progress-` prefix)

Also created `/tmp/bellows-repro-done/` directory.

---

## Q3 — Reproduce Hypothesis A (Standard Bootstrap)

### Test 1: Default model (claude-opus-4-6[1m])

Bootstrap prompt: `"Read the plan at /tmp/bellows-repro-test-2026-04-15.md and execute Step 1. Execute it fully — this is a single-step investigation. Deposit your findings and report Complete when done."`

**Results:**
| Check | Result |
|-------|--------|
| Marker file exists? | **YES** — contains `REPRO_OK` |
| Plan moved to Done? | **YES** — at `/tmp/bellows-repro-done/bellows-repro-test-2026-04-15.md` |
| Original/in-progress leftover? | **NO** — both cleaned up |
| `stop_reason` | `end_turn` |
| `has **Status:** Complete`? | **NO** (confirms Hypothesis B even in repro) |
| `result` text | `"Complete. Both tasks executed: - **Task A:** Wrote REPRO_OK... - **Task B:** Plan moved..."` |

**Hypothesis A NOT reproduced.** Agent completed all tasks including move-to-Done.

### Test 2: Sonnet model (claude-sonnet-4-6) — matching Bellows production config

Same bootstrap prompt, `--model claude-sonnet-4-6`.

**Results:**
| Check | Result |
|-------|--------|
| Marker file exists? | **YES** — contains `REPRO_OK` |
| Plan moved to Done? | **YES** — at `/tmp/bellows-repro-done/bellows-repro-test-2026-04-15.md` |
| Original/in-progress leftover? | **NO** — both cleaned up |
| `stop_reason` | `end_turn` |
| `has **Status:** Complete`? | **NO** |
| `result` text | `"Complete. - Task A: /tmp/bellows-repro-marker.txt written with REPRO_OK - Task B: Plan moved..."` |

**Hypothesis A NOT reproduced with sonnet either.** Both models complete simple plans including move-to-Done.

### Note: Transient auth failure

The FIRST attempt to run `claude -p --model claude-sonnet-4-6` returned a **401 authentication error**: `"Invalid authentication credentials"`. A subsequent attempt (minutes later) succeeded. This demonstrates that `--model claude-sonnet-4-6` auth can fail intermittently — a critical finding for the planner consultation path (see Q6).

---

## Q4 — Emphatic Bootstrap Prompt

Bootstrap: `"Read the plan at /tmp/bellows-repro-test-2026-04-15.md and execute Step 1 to completion. CRITICAL: the very last operation in the plan is to move the plan file to Done/. You MUST execute this move-to-Done as your final action. Do NOT report complete until the move is executed. Verify the file is in Done/ before reporting complete."`

**Results:**
| Check | Result |
|-------|--------|
| Marker file exists? | **YES** |
| Plan moved to Done? | **YES** |
| `stop_reason` | `end_turn` |
| `result` text | `"Verified. Plan file is in /tmp/bellows-repro-done/... Step 1 complete — marker written and plan moved to Done."` |

**No difference from Q3.** The emphatic prompt adds a verification step but the agent was already completing the move-to-Done without emphasis. The standard bootstrap is sufficient for simple plans.

---

## Q5 — Are the Bugs Independent?

### Hypothesis B (Unknown status) — independent of stranding

The parser bug exists for ALL runs regardless of strand status:
- 28/30 log files show `has_status=False` — including both stranded AND non-stranded runs
- The two files with `has_status=True` (runner-parser) are among the earliest non-stranded runs
- The parser bug is a data-source mismatch (looking in `result_text` instead of deposited file), completely orthogonal to whether the agent completes its work

### Hypothesis A (strand) — independent of status recording

The strand reproductions (Q3/Q4) showed no stranding but DID show the parser bug (`has_status=False`). Stranding and status recording operate on different code paths (`run_plan()`'s post-loop check vs `parser.parse()`'s text scan).

**CONFIRMED: both bugs are independent.** Fixing one does not fix the other.

---

## Q6 — Phase 4 Fix Recommendations

### REVISED ROOT CAUSE FOR STRANDING

Phase 2 hypothesized agent early termination as the strand cause. Phase 3 reproduction **REFUTED this for simple plans** — both opus and sonnet complete all tasks including move-to-Done.

Analysis of production logs revealed the ACTUAL strand mechanism:

**Multi-step plans strand because the planner consultation fails, triggering an escalation-timeout-halt cycle:**

1. Agent completes step 1 normally (all step-1 logs show successful completion)
2. Bellows calls `planner.consult()` which runs `claude -p --model claude-sonnet-4-6`
3. If the planner subprocess fails (auth error, invalid JSON, timeout), `consult()` returns `decision = "escalate"`
4. Bellows sends a Pushover escalation notification and calls `response_server.wait_for_response(timeout=3600)`
5. If the CEO doesn't respond within 1 hour, `response` is `None` and `run_plan()` returns early (bellows.py line 195)
6. **This early return BYPASSES the strand check at lines 218-223** — no STRANDED notification is sent
7. The plan file stays as `in-progress-*` forever — a silent strand

**Evidence:**
- Log analysis shows multi-step plans stopped getting step 2 after session `1123f612` (~18:48 on Apr 14). All subsequent multi-step runs (62-68) show step 1 only. Diagnostic plans (no planner consultation) continued working fine.
- Transient `--model claude-sonnet-4-6` auth failure was observed during this investigation (401 error on first attempt, succeeded on retry). The planner uses the same model and auth path.
- The planner consultation result is NOT logged — failures are invisible.

**Diagnostic plans (single step) do NOT strand at the agent level.** The 20260414-170512 log shows a diagnostic completing all four phases including move-to-Done. Diagnostics skip the planner consultation entirely (the while loop is never entered when `total_steps = 1`).

---

### Fix 1: Parser bug (SMALL — `parser.py` only)

**Recommended fix:** Infer status from `stop_reason` and `is_error` instead of scanning for a formatted string:

```python
# Replace parser.py lines 14-19 with:
if is_error:
    receipt_status = "Blocked"
elif stop_reason == "end_turn":
    receipt_status = "Complete"
elif stop_reason == "max_tokens":
    receipt_status = "Partial"
else:
    receipt_status = "Unknown"
```

**Why this approach:** `stop_reason` is consistently `"end_turn"` for all normal completions across 30 log files. It's set by the `claude -p` runtime, not by the agent's text output, so it can't drift. This is more reliable than any text-parsing approach and doesn't require plan template changes.

### Fix 2: Strand bug (MEDIUM — `bellows.py` + `planner.py`)

**Fix 2a: Add strand check to the escalation-halt path (bellows.py).**
The `return` at line 195 (escalation timeout) bypasses the strand check. Refactor so that ALL exits from `run_plan()` pass through the strand check. This ensures silent strands become visible.

**Fix 2b: Make planner consultation resilient (planner.py).**
- Add retry-on-auth-failure (1 retry with 5s delay)
- Fall back to `decision = "continue"` instead of `"escalate"` when the failure is clearly transient (auth error, not a judgment failure)
- Log the consultation result to a file for debugging

**Fix 2c: Add planner consultation logging (bellows.py).**
After `planner.consult()` returns, log the decision to stdout: `print(f"Bellows: Planner decision for {plan_name} step {current_step}: {decision} — {reason}")`. This makes the escalation-strand path visible in terminal output.

### Fix priority

| Fix | Scope | Impact |
|-----|-------|--------|
| Fix 1 (parser) | Small — 5 lines in parser.py | Correct status recording for ALL runs |
| Fix 2a (strand check) | Small — ~10 lines in bellows.py | Make silent strands visible |
| Fix 2b (planner resilience) | Medium — ~15 lines in planner.py | Prevent transient failures from halting plans |
| Fix 2c (logging) | Small — 1 line in bellows.py | Debugging visibility |

**Recommended Phase 4 scope:** All four fixes. Total: ~30 lines of changes across 3 files. Tests needed for the parser fix and the planner retry logic.

---

## Cleanup

All temp files removed:
- `/tmp/bellows-repro-test-2026-04-15.md`
- `/tmp/bellows-repro-marker.txt`
- `/tmp/bellows-repro-output.json`
- `/tmp/bellows-repro-output-emphatic.json`
- `/tmp/bellows-repro-output-sonnet.json`
- `/tmp/bellows-repro-done/`

---

## Output Receipt

- **Status:** Complete
- **Files Deposited:** `knowledge/research/bellows-reproduce-bugs-2026-04-15.md`
- **Files Created or Modified (Code):** `[]` (read-only / reproduction only)
- **Decisions Made:** Revised root cause hypothesis — stranding is caused by planner consultation failure → escalation → timeout → silent halt, NOT by agent early termination. Parser bug confirmed as data-source mismatch. Both bugs independent. Phase 4 scope: 4 fixes across 3 files (~30 lines).
- **Flags for CEO:** Phase 4 is a SMALL-to-MEDIUM fix scope. The parser fix is 5 lines. The strand fix is ~25 lines across bellows.py and planner.py. Total estimated: 30 lines of changes + tests. Recommend bundling all 4 fixes in a single Phase 4 plan.
