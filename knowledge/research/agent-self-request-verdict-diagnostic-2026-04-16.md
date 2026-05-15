# Agent Self-Request Verdict Mechanism — Diagnostic Findings
**Date:** 2026-04-16 | **Status:** Complete

---

## Q1 — Parsed Output Flow: `run_step` and `parser.py`

### What `run_step` returns

`runner.run_step` runs `claude -p <prompt> --output-format json` and pipes the result through `parse()`. The returned dict (from `parse()`) contains:

```python
{
    "session_id":         str | None,
    "is_error":           bool,
    "stop_reason":        str,        # "end_turn", "max_tokens", "", etc.
    "result_text":        str,        # Full text of Claude's conversational response
    "cost_usd":           float,
    "permission_denials": list,
    "receipt_status":     str,        # "Complete", "Partial", "Blocked", "Unknown"
    "ceo_flags":          list[str],  # Extracted from "### Flags for CEO" section
    "escalate":           bool,
}
```

On error paths (timeout, exception, JSON decode failure, parse failure), `run_step` returns a hardcoded dict with the same key shape but `is_error=True`, `escalate=True`.

### What `parse()` extracts from Claude's raw JSON output

Claude Code's `--output-format json` response has top-level fields: `session_id`, `is_error`, `stop_reason`, `result` (the full conversation text), `total_cost_usd`, `permission_denials`.

`parse()` reads all of these from `raw`. The `result_text` field (`raw["result"]`) is the **complete unstructured text output** of the Claude session. The parser already has full access to this text. The `ceo_flags` extraction (regex scan of `result_text` for `### Flags for CEO` bulleted lists) proves the pattern works.

**There is no existing field that carries an agent-initiated pause signal.** A new field would need to be added or extracted from `result_text`.

---

## Q2 — `gates.check`: How the Parsed Dict Flows

### Fields consumed by `gates.check`

`gates.check(parsed, plan_text, step_number, project_path, files_changed, plan_path)` reads these fields from `parsed`:

| Field | Gate | Usage |
|---|---|---|
| `receipt_status` | Gate 1 | Fails if not `"Complete"` |
| `ceo_flags` | Gate 2 | Fails if non-empty |
| `is_error` | Gate 3 | Fails if True |
| `permission_denials` | Gate 4 | Fails if non-empty |
| `result_text` | Gate 5 | Scans `### Files Deposited` section for missing files |

`plan_text` and `step_number` are used by Gates 6 (QA detection), 7 (file audit), 8 (scope check). `parsed` is not used by those gates.

### `_verdict_requested` in full

```python
def _verdict_requested(plan_path, step_number):
    if plan_path is None:
        return (False, None)
    filename = os.path.basename(plan_path)
    for prefix in ("in-progress-", "verdict-pending-", "halted-"):
        if filename.startswith(prefix):
            filename = filename[len(prefix):]
    if filename.endswith(".md"):
        filename = filename[:-3]
    slug = filename
    request_file = os.path.join(VERDICT_REQUEST_DIR, f"request-{slug}-step-{step_number}.md")
    if os.path.isfile(request_file):
        with open(request_file, "r") as f:
            return (True, f.read())
    return (False, None)
```

It derives a `slug` from the plan filename (stripping state prefixes and `.md`), then checks for a file named `request-{slug}-step-{N}.md` in `verdicts/pending/`. Returns `(True, file_contents)` or `(False, None)`.

### How the return value flows into pause decisions

`check()` wraps the result as `"verdict_requested": {"requested": bool, "body": str|None}` in the gate result dict.

In `bellows.py`, both the mid-plan loop and the final-step block check:
```python
gate_result.get("verdict_requested", {}).get("requested", False)
```
If `True`, `_pause_reason = "agent_verdict_request"` and `verdict.post_verdict_request(...)` is called — same pause path as gate failures and QA checkpoints, but labeled distinctly.

---

## Q3 — Design: Text Marker via Parsed Dict

### (a) Viability

**Fully viable.** `parse()` already holds `result_text = raw.get("result", "")` — the complete text of Claude's response. The `ceo_flags` extraction already proves regex scanning of this text works reliably. A `VERDICT_REQUESTED: <reason>` marker on its own line in `result_text` is detectable with a simple regex in `parse()`.

The key structural advantage: `result_text` is the *only* agent-controlled text that flows through the pipeline. `stop_reason`, `is_error`, and `permission_denials` are all set by Claude Code infrastructure, not by the agent's output instructions. The text marker approach is the right layer.

### (b) Minimal change to `parser.py`

Add after the `ceo_flags` extraction block (after line 36, before the `escalate` assignment):

```python
# Extract VERDICT_REQUESTED marker — agent-initiated pause signal
verdict_requested = {"requested": False, "reason": None}
vr_match = re.search(r"^VERDICT_REQUESTED:\s*(.+)$", result_text, re.MULTILINE)
if vr_match:
    verdict_requested = {"requested": True, "reason": vr_match.group(1).strip()}
```

Add `"verdict_requested": verdict_requested` to the returned dict.

### (c) Minimal change to `gates.py`

In `check()`, replace line 87:
```python
# OLD (filesystem scan):
requested, request_body = _verdict_requested(plan_path, step_number) if plan_path else (False, None)
```
with:
```python
# NEW (from parsed dict):
vr = parsed.get("verdict_requested", {})
requested = vr.get("requested", False)
request_body = vr.get("reason")
```

The `verdict_requested` key in the returned gate result dict remains structurally identical: `{"requested": bool, "body": str|None}`. No changes needed in `bellows.py` or `verdict.py`.

### (d) Better signal mechanism?

No better mechanism exists in the current code. There are no structured fields in Claude Code's JSON output format (`--output-format json`) that an agent controls through its text responses — only `result` (the text). The alternatives would be:

1. **`ceo_flags` reuse**: The agent could include `### Flags for CEO\n- VERDICT_REQUESTED: reason` in its output. This would set `escalate=True` and trigger a pause, but via Gate 2 failure — labeled as a gate failure rather than a clean agent pause. This conflates "something went wrong" with "I'm deliberately pausing." Not recommended.

2. **Exit code / structured output**: Would require changes to how Claude Code itself emits its JSON — not within Bellows's control.

3. **Filesystem (current broken approach)**: Requires the agent to know the plan slug and conventions, and operate on bellows's filesystem rather than its own working directory. Fundamentally unworkable for agents running in external project paths.

**The text marker approach is optimal:** zero coordination overhead, works with the existing parser architecture, and the agent just emits a human-readable line in its response.

---

## Q4 — Dead Code After Migration

Once `verdict_requested` flows from the parsed dict, the following become dead and should be removed entirely:

| Location | Lines | What |
|---|---|---|
| `gates.py:14` | `VERDICT_REQUEST_DIR = "..."` | Constant — no longer used |
| `gates.py:30-48` | Entire `_verdict_requested()` function | Replaced by `parsed.get("verdict_requested", {})` |
| `gates.py:87` | `requested, request_body = _verdict_requested(...)` | Replaced by dict lookup |

There is no case for keeping the filesystem fallback. The whole point of the migration is that an agent cannot reliably know the plan slug or bellows filesystem paths. Keeping a fallback that never fires adds dead code with no benefit. The `plan_path` parameter to `check()` could also be removed if no other gate uses it — currently only `_verdict_requested` consumes it.

---

## Q5 — Teaching the Agent

**A prompt instruction is sufficient and necessary.** The critical constraint is:

> Agents run with `cwd=project_path` — a watched project directory entirely separate from the bellows filesystem. The bellows `CLAUDE.md` is not loaded by agents. The instruction must be in the plan prompt.

For plans that want to enable agent-initiated pauses, the step prompt should include:

```
If you encounter a condition requiring CEO review before the next step,
output the following on its own line in your response:
VERDICT_REQUESTED: <one-line reason>
```

**Automatic via plan-level boilerplate?** The Planner could add this instruction to every plan that includes agent steps — either as a standard plan header section or as a prepended preamble in `bellows.py` before executing the prompt. A YAML header field like `agent_pause_enabled: true` could control whether bellows appends the instruction to the prompt. This would avoid copy-paste into every plan.

**CLAUDE.md for agent projects?** If a watched project has a `CLAUDE.md` that includes the `VERDICT_REQUESTED` convention, agents running in that project would have it automatically. This is the cleanest long-term mechanism for projects that are frequently orchestrated by Bellows — put the convention in the project's own `CLAUDE.md`.

---

## Summary

| Question | Finding |
|---|---|
| Q1 | `result_text` in parsed dict is the full agent output text; parser has full access |
| Q2 | `_verdict_requested` does a fragile filesystem scan; its result feeds the pause branch in `bellows.py` |
| Q3 | Text marker `VERDICT_REQUESTED: <reason>` extracted in `parser.py` is viable, minimal, and clean |
| Q4 | `VERDICT_REQUEST_DIR`, `_verdict_requested()`, and call site (line 87) are the complete dead code set |
| Q5 | Prompt instruction is required (agents don't see bellows CLAUDE.md); watched-project CLAUDE.md or plan-level boilerplate are the scalable paths |
