# `claude -p` Prompt Suppression Inventory
**Date:** 2026-05-04 | **Agent:** Bellows Systems Analyst | **Diagnostic:** claude-p-prompt-suppression

---

## Executive Summary

Bellows dispatches plans via `claude -p <prompt> --output-format stream-json --verbose --model <model> --allowedTools Read,Edit,Write,Bash`. In non-interactive `-p` mode with `permissionMode: default`, the effective behavior is: (a) tools listed in `--allowedTools` (Read, Edit, Write, Bash) are pre-authorized and never prompt, (b) read-class tools (Glob, Grep, ToolSearch) are auto-approved by the default permission mode without needing explicit listing, (c) write-class tools NOT in the allowed list (WebFetch, WebSearch, NotebookEdit, MCP tools) are available but unapproved — in non-interactive mode with no user to prompt, their behavior if attempted is undetermined from Bellows-side code alone. No `--dangerously-skip-permissions` flag is used. The prior research (2026-04-23) incorrectly stated `--allowedTools` acts as a tool filter; log evidence from 2026-05-04 definitively shows it is a pre-authorization list only — all tools remain available in the system init.

---

## Critical Findings

### 🟡 Minor — `--allowedTools` is NOT a tool filter (contradicts prior research)

The 2026-04-23 research stated: "every Bellows-dispatched agent operates with exactly four tools" and "tools outside [the allowed list] are simply unavailable." This is **incorrect**. Log evidence from all 5 most recent runs (2026-05-04) shows:
- System init event lists ALL tools as available (30+ tools including Glob, Grep, ToolSearch, WebFetch, WebSearch, MCP tools)
- Agents successfully use Glob, Grep, and ToolSearch — none of which are in the `--allowedTools` list
- Zero permission denials in all 5 recent runs

`--allowedTools` is a **pre-authorization list**, not a tool filter. The effective tool availability is governed by `permissionMode: default`, which auto-approves read-class tools regardless of the allowed list.

### 🟡 Minor — Unapproved write-class tools (WebFetch, WebSearch, NotebookEdit) have undetermined non-interactive behavior

These tools are listed as available in system init but are NOT pre-authorized via `--allowedTools`. In interactive mode, using them would trigger a permission prompt. In non-interactive `-p` mode, the behavior if attempted is unknown from Bellows-side code — they may be auto-denied, silently skipped, or have some other fallback. Log evidence shows agents never attempt them, so no empirical data exists.

### 🔵 Advisory — MCP servers with "needs-auth" are silently degraded

Every recent log shows `"claude.ai Google Drive": "needs-auth"` and `"claude.ai Gamma": "needs-auth"` in the system init. These would trigger an OAuth flow in interactive mode. Under `-p` dispatch they are simply listed as "needs-auth" and their tools are presumably non-functional. No gate or signal detects this degradation.

---

## `runner.py` Invocation Reference

### Full argv (runner.py:33-41)

```python
cmd = [
    "claude", "-p", prompt,
    "--output-format", "stream-json",
    "--verbose",
    "--model", model,
    "--allowedTools", allowed_tools,  # default: "Read,Edit,Write,Bash"
]
if session_id is not None:
    cmd += ["--resume", session_id]
```

### Subprocess configuration (runner.py:49-55)

| Aspect | Value | Line |
|---|---|---|
| Full command | `claude -p <prompt> --output-format stream-json --verbose --model <model> --allowedTools Read,Edit,Write,Bash` | 33-38 |
| Optional flag | `--resume <session_id>` (multi-step continuation) | 40-41 |
| `--dangerously-skip-permissions` | **NOT passed** | — |
| `--permission-mode` | **NOT passed** (defaults to `default` per system init) | — |
| Working directory | `cwd=project_path` (target project root) | 54 |
| stdin | Not set (inherited, effectively closed) | — |
| stdout | `subprocess.PIPE` — streaming reader thread | 51 |
| stderr | `subprocess.PIPE` — streaming reader thread | 52 |
| Environment variables | None set — no env manipulation | — |
| Inactivity timeout | `config["step_inactivity_timeout_seconds"]` = 1800s | bellows.py:299 |
| Wall-clock cap | `timeout * 10` = 18000s (5 hours) | runner.py:46 |

### Call sites in bellows.py

- **Line 298**: Initial step — `runner.run_step(bootstrap_prompt, wt_path, model, timeout=...)` — no `allowed_tools` override
- **Line 360**: Continuation steps — `runner.run_step(default_next_prompt, wt_path, model, session_id=..., timeout=...)` — no `allowed_tools` override

Neither call site overrides the default `allowed_tools="Read,Edit,Write,Bash"`.

---

## `config.json` Permission-Related Keys

| Key | Value | Consumed by | Permission relevance |
|---|---|---|---|
| `default_model` | `claude-opus-4-6` | bellows.py (passed to runner as `model`) | Indirectly affects agent capability |
| `step_inactivity_timeout_seconds` | 1800 | bellows.py → runner.py `timeout` param | Controls kill-on-inactivity (prevents hung permission prompts) |
| `step_timeout_seconds` | 2400 | bellows.py (legacy fallback) | Same |
| `watched_projects` | 8 project paths | bellows.py watcher | Determines which projects agents execute in |

No permission-specific keys (no `allowed_tools` override, no `permission_mode`, no `skip_permissions`). All permission behavior is hardcoded in `runner.py:30`.

---

## `parser.py` Prompt-Detection Patterns

| Pattern | Source | What it detects | Line |
|---|---|---|---|
| `permission_denials` field | `raw.get("permission_denials", [])` from result event | Structured list of denied tool invocations | parser.py:12 |
| `### Flags for CEO` section | Regex in `result_text` | Agent-authored escalation flags | parser.py:29-36 |
| `VERDICT_REQUESTED:` marker | Regex in `result_text` | Agent-initiated pause signal | parser.py:39-42 |
| `is_error` field | `raw.get("is_error", False)` | CLI-level errors | parser.py:8 |
| `stop_reason` field | `raw.get("stop_reason", "")` | Abnormal termination (max_tokens, etc.) | parser.py:9 |

### Gates.py permission denial handling (gates.py:106-123)

| Behavior | Detail |
|---|---|
| Input | `parsed["permission_denials"]` — list of dicts with `tool_name`, `tool_use_id`, `tool_input` |
| READ_CLASS_TOOLS exemption | `{"Grep", "Glob", "Read"}` — denials of these tools do NOT block |
| Blocking behavior | Any denial of Bash, Edit, Write, or other tools → gate failure → verdict pause |
| Legacy format | String-form denials (no `tool_name`) default to blocking |

---

## Log Evidence Samples

### Sample 1: Successful multi-tool run (20260504-162702-step.json)

```
System init: permissionMode=default, tools=[30+ tools], mcp_servers=[vexp:connected, Google Drive:needs-auth, Gamma:needs-auth]
Tool usage: Bash(11), Read(5), Edit(2), Write(1)
Result: permission_denials=[], stop_reason=end_turn
```

### Sample 2: Glob/Grep usage outside allowedTools (20260504-134310-step.json)

```
System init: permissionMode=default, tools=[31 tools including Glob, Grep, ToolSearch, WebFetch, etc.]
Tool usage: Bash, Edit, Glob, Read, Write — Glob used successfully despite NOT being in --allowedTools
Result: permission_denials=[], stop_reason=end_turn
```

### Sample 3: Historical permission denial (20260417-195019-step.json)

```json
"permission_denials": [{
  "tool_name": "Bash",
  "tool_use_id": "toolu_01NAMyHuWGvHNJsMDkRTAVbF",
  "tool_input": {"command": "rm -f .git/index.lock 2>/dev/null; git add ..."}
}]
```
This denial was for a specific Bash command (git operations) — tool-level pre-approval does not override per-command permission rules from project `.claude/settings.local.json`.

### Sample 4: MCP auth degradation (20260504-132757-step.json)

```json
"mcp_servers": [
  {"name": "vexp", "status": "connected"},
  {"name": "claude.ai Google Drive", "status": "needs-auth"},
  {"name": "claude.ai Gamma", "status": "needs-auth"}
]
```
OAuth-requiring MCP servers listed as "needs-auth" — no gate detects this; agents proceed without these tools.

### Sample 5: No AskUserQuestion usage ever

Scanned ALL log files in `bellows/logs/`. Zero instances of `AskUserQuestion` tool use across entire history. Agents in `-p` mode never attempt to ask the user a question.

---

## Prompt Category Inventory

| # | Prompt Category | Manual-mode behavior | Bellows-dispatched behavior | CEO judgment risk |
|---|---|---|---|---|
| 1 | **Tool permission — Bash** | Prompts user per command unless allowed in settings | Pre-approved via `--allowedTools "...Bash"` (runner.py:30,38). Per-command rules from `.claude/settings.local.json` in target project still apply (see Sample 3). | Low — per-command rules provide granular control. Risk: destructive commands (rm -rf, git push --force) auto-approved unless a project-level settings file blocks them. |
| 2 | **Tool permission — Edit** | Prompts on first use or per file | Pre-approved via `--allowedTools "...Edit"` (runner.py:30,38). | Low — agents can edit any file without confirmation. Mitigated by scope_check gate (gates.py:233-258) which flags out-of-plan edits. |
| 3 | **Tool permission — Write** | Prompts on first use or per file | Pre-approved via `--allowedTools "...Write"` (runner.py:30,38). | Low — same as Edit. Scope check provides post-hoc detection. |
| 4 | **Tool permission — Glob/Grep/Read** | Auto-approved in default mode | Auto-approved by `permissionMode: default` (system init evidence). If denied, exempted from Gate 4 blocking (gates.py:112, READ_CLASS_TOOLS). | None — read-only operations. |
| 5 | **Tool permission — MCP tool (vexp)** | May prompt on first use | Available when `vexp` MCP server status is "connected". No explicit pre-authorization in `--allowedTools`. Behavior if permission-gated is undetermined. Never observed denied. | Unknown — MCP tool writes could modify external state without gate coverage. |
| 6 | **Tool permission — WebFetch** | Prompts per URL/domain | Listed as available in system init but NOT in `--allowedTools`. Never observed attempted in any log. Non-interactive behavior undetermined. | Unknown — if ever attempted, either auto-denied or auto-approved. Agent currently never tries. |
| 7 | **Tool permission — WebSearch** | Prompts per search | Same as WebFetch — available but not pre-authorized, never attempted. | Unknown — same as above. |
| 8 | **Tool permission — AskUserQuestion** | Sends question to user, waits for response | Available in system init. Never attempted in any log across entire history. In `-p` mode, presumably would fail or return empty. | 🟡 If attempted, agent would either get no response (stalling) or the tool would error. No gate detects this scenario. |
| 9 | **File-overwrite confirmation** | "File already exists, overwrite?" in interactive mode | No such confirmation exists in `-p` mode — Write/Edit tools operate directly. | None — this is a UX feature of interactive mode, not a safety mechanism. |
| 10 | **Authentication / OAuth prompt** | MCP servers prompt for OAuth login | Silently listed as "needs-auth" in system init (Sample 4). No gate detects degraded MCP. Google Drive and Gamma MCP tools are non-functional. | 🔵 Low risk currently (agents don't rely on these). Could become a risk if MCP tools are added to plan prompts that assume connectivity. |
| 11 | **Long-running command confirmation** | Interactive mode may warn before long commands | No confirmation in `-p` mode. Bellows manages timeouts externally (inactivity: 1800s, wall-clock: 18000s — runner.py:46,115-127). | Low — timeout mechanism provides safety. Risk: agent could start a long process that succeeds just before timeout, causing unexpected state. |
| 12 | **Mid-task user-input request (AskUserQuestion)** | Agent asks user a clarifying question | Tool available but never attempted (see #8). If invoked, would presumably fail silently or return no response. | 🟡 Agent might proceed with incorrect assumptions rather than asking. No detection mechanism. But empirically never happens. |
| 13 | **Compaction / context-limit notification** | User sees "context compacted" message | No `context_management` events found in any recent log. Stream format includes the field but it's null/absent. If compaction occurs, it happens transparently. | 🔵 Advisory — long multi-turn sessions (via `--resume`) could compact context without Bellows awareness. Agent might lose earlier instructions. |
| 14 | **Plan mode confirmation** | "Enter plan mode?" prompt | `EnterPlanMode` listed as available tool. Never observed attempted. | None — agents don't need plan mode in execution context. |
| 15 | **Workspace trust dialog** | First-run trust prompt for new directories | Explicitly skipped by `-p` flag per CLI docs: "The workspace trust dialog is skipped when Claude is run with the -p mode." | None — by design. |
| 16 | **Per-command Bash permission (settings-based)** | Project `.claude/settings.local.json` rules approve/deny specific patterns | Still enforced under `-p` mode (Sample 3 confirms Bash denial for specific commands). Results in `permission_denials` entry → Gate 4 catches it. | Low — this mechanism works correctly. Denials are detected and trigger verdict pause. |

---

## Gaps and Unknowns

1. **WebFetch/WebSearch non-interactive behavior**: These tools are available (listed in system init) but not pre-authorized. Never attempted by agents. Cannot determine from Bellows-side code whether they would be auto-denied, auto-approved, or error if attempted.

2. **MCP tool permission behavior**: `mcp__vexp__*` tools are listed as available when vexp server is connected. They are NOT in `--allowedTools`. Whether they require permission prompts in default mode, and how that resolves in non-interactive mode, is undetermined. Agents do occasionally use MCP tools without denial (log evidence shows vexp tools in tool lists) — suggesting they may be auto-approved as "read-class" equivalents, but this is uncertain.

3. **AskUserQuestion failure mode**: Available but never used. Whether it would error, return empty, hang, or be auto-denied in `-p` mode is unknown from Bellows-side code.

4. **Context compaction visibility**: No compaction events observed, but for very long sessions (multi-step plans with `--resume`), compaction could occur invisibly. Whether the stream-json format surfaces this event type is undetermined.

5. **`--allowedTools` semantics under different `--permission-mode` values**: Bellows only uses `default` mode. Whether the pre-authorization vs. filter behavior differs under `bypassPermissions`, `plan`, `auto`, or `dontAsk` modes is out of scope.

6. **Per-command Bash rule source**: The 2026-04-17 denial shows a specific Bash command being denied despite Bash being in `--allowedTools`. This implies per-command rules from the target project's `.claude/settings.local.json` or user-level settings. Bellows has no visibility into what rules exist in target projects — a new rule added to a watched project could start causing unexpected denials.

7. **Agent/Task/EnterWorktree tool behavior**: These tools are listed as available. Whether they work, are permission-gated, or have special handling in `-p` mode is undetermined.

---

## Output Receipt

**Agent:** Bellows Systems Analyst
**Step:** 1 (single-step diagnostic)
**Status:** Complete

### What Was Done
Comprehensive inventory of prompt-shaped interactions in `claude -p` dispatch mode. Traced runner.py invocation, config.json keys, parser.py detection patterns, and gates.py permission handling. Sampled all log evidence for permission denials, tool usage outside allowed set, MCP auth events, AskUserQuestion attempts, and context compaction. Produced 16-category prompt inventory with behavior mapping and CEO judgment risk assessment. Identified critical correction to prior research (2026-04-23): `--allowedTools` is a pre-authorization list, not a tool filter.

### Files Deposited
- `bellows/knowledge/research/claude-p-prompt-suppression-inventory-2026-05-04.md`

### Files Created or Modified (Code)
- None — investigation only

### Decisions Made
- Prior research finding (2026-04-23) that `--allowedTools` is a "tool filter" is contradicted by log evidence; this inventory documents the corrected understanding

### Flags for CEO
- None — no critical-severity findings. Two minor items (prior research correction, unapproved tool behavior) and two advisory items (MCP auth, compaction).

### Flags for Next Step
- None — single-step diagnostic
