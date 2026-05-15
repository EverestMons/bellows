# Permission Prompt Substrate — Diagnostic Findings
**Date:** 2026-04-23 | **Agent:** Bellows Systems Analyst | **Diagnostic:** permission-prompt-substrate

---

## 1. Executive Summary

Permission prompts went quiet under Bellows because of **explanation (3) — `claude -p` non-interactive mode handles permissions differently** — combined with Bellows's explicit `--allowedTools` flag. Bellows passes `--allowedTools Read,Edit,Write,Bash` on every invocation, which pre-authorizes exactly those four tools at the CLI level. Since `-p` mode is non-interactive (no TTY, no user to prompt), tools in the allowed list are auto-approved and tools outside it are simply unavailable. Bellows does not suppress output (explanation 2 is false) and does not pass `--dangerously-skip-permissions` or any auto-approve flag (explanation 1 is false). The `permission_denials` field exists in `claude -p` JSON output and Bellows's Gate 4 checks it — but it is structurally empty because the `--allowedTools` pre-authorization means denials never occur for permitted tools and unpermitted tools are never attempted.

---

## 2. Q5a — What does `claude -p` do with permission prompts?

### Evidence: CLI help output

From `claude --help`:

- **`-p, --print`**: "Print response and exit (useful for pipes). Note: The workspace trust dialog is skipped when Claude is run with the -p mode. Only use this flag in directories you trust."
- **`--permission-mode <mode>`**: Choices: `acceptEdits`, `bypassPermissions`, `default`, `dontAsk`, `plan`, `auto`. Bellows does **not** pass this flag.
- **`--allowedTools <tools...>`**: "Comma or space-separated list of tool names to allow (e.g. 'Bash(git:*) Edit')". Bellows passes `Read,Edit,Write,Bash`.
- **`--dangerously-skip-permissions`**: "Bypass all permission checks. Recommended only for sandboxes with no internet access." Bellows does **not** pass this flag.

### Mechanism

The `-p` flag creates a non-interactive session with no TTY. `--allowedTools` acts as both a **tool filter** (only listed tools are available) and a **permission pre-authorization** (listed tools are approved without prompts). This is the designed behavior — the help text warns users to "only use this flag in directories you trust" precisely because permission prompts are bypassed.

The default `--permission-mode` for `-p` mode (when not explicitly set) appears to be effectively `default`, but this is moot when `--allowedTools` is specified — the allowed tools are pre-approved regardless of permission mode.

### Empirical branch: NOT REQUIRED

The documentation is clear and Q5b confirms Bellows passes `--allowedTools` on every invocation. The reading-first path resolves the question definitively.

---

## 3. Q5b — Bellows's exact invocation of `claude -p`

### Source: `runner.py:25-41`

```python
def run_step(
    prompt: str,
    project_path: str,
    model: str,
    session_id: Optional[str] = None,
    allowed_tools: str = "Read,Edit,Write,Bash",
    timeout: int = 300,
) -> dict:
    cmd = [
        "claude", "-p", prompt,
        "--output-format", "json",
        "--model", model,
        "--allowedTools", allowed_tools,
    ]
    if session_id is not None:
        cmd += ["--resume", session_id]
```

### Subprocess invocation: `runner.py:48-54`

```python
    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        cwd=project_path,
    )
```

### Findings

| Aspect | Value |
|---|---|
| Command | `claude -p <prompt> --output-format json --model <model> --allowedTools Read,Edit,Write,Bash` |
| Optional flags | `--resume <session_id>` (when resuming a session) |
| Permission-related flags | **None** — no `--permission-mode`, no `--dangerously-skip-permissions` |
| Permissions config file written before invoke | **No** — no `.claude/permissions.json` or equivalent is created |
| Environment variables set | **None** — no env manipulation before subprocess |
| Working directory | `cwd=project_path` (the parent project, e.g. `/Users/marklehn/Desktop/GitHub/invoice-pulse`) |
| stdin | Not set — defaults to inherited (effectively closed in daemon thread context) |
| stdout | `subprocess.PIPE` — captured via streaming reader thread |
| stderr | `subprocess.PIPE` — captured via streaming reader thread |

### Key observation

The `allowed_tools` parameter defaults to `"Read,Edit,Write,Bash"` (runner.py:31). No call site in `bellows.py` overrides this default. This means **every Bellows-dispatched agent operates with exactly four tools**: Read, Edit, Write, Bash. Tools like Glob, Grep, Agent, WebFetch, WebSearch, and all MCP tools are unavailable to dispatched agents — they must use Bash equivalents (`find`, `grep`, `curl`) for those capabilities.

The `.claude/settings.local.json` file in the Bellows repo contains permission entries, but these are for **interactive sessions in the Bellows project itself** (manual debugging/development), not for the `claude -p` subprocesses Bellows dispatches. Dispatched processes run with `cwd=project_path` (the target project), not the Bellows directory.

---

## 4. Q5c — Signal observability

### Output format

Bellows uses `--output-format json`, which returns a **single JSON object after completion**. The alternative `--output-format stream-json` (with optional `--include-partial-messages`) would provide **real-time streaming events** but Bellows does not use it.

### JSON output fields consumed by Bellows (via `parser.py`)

| Field | Used by |
|---|---|
| `session_id` | Session resume across steps |
| `is_error` | Error detection, receipt_status inference |
| `stop_reason` | Receipt status inference (end_turn → Complete, max_tokens → Partial) |
| `result` | Text output — parsed for Output Receipt, CEO flags, VERDICT_REQUESTED marker |
| `total_cost_usd` | Cost tracking and reporting |
| `permission_denials` | Gate 4 check (structurally empty — see explanation above) |

### Signal observability table

| Signal Class | Status | Evidence |
|---|---|---|
| **Tool requests** (which tools were called) | NOT OBSERVED | JSON output contains `result` text only, not structured tool-call events. Would require `stream-json` format. |
| **Permission prompts — granted** | NOT OBSERVED | Never fire due to `--allowedTools` pre-authorization. No structured field in JSON output for granted permissions. |
| **Permission prompts — denied** | OBSERVED AND LOGGED | `permission_denials` array in JSON output → Gate 4 (`_gate_no_permission_denials` in gates.py:101-108). Structurally empty because denied tools are simply unavailable. |
| **Judgment calls / pauses** | OBSERVED AND LOGGED (partial) | `VERDICT_REQUESTED` marker parsed from `result` text (parser.py:39-42). CEO flags parsed from `### Flags for CEO` section. But these are text-convention signals, not structured events. |
| **Commit events** | NOT OBSERVED | No structured commit event in JSON output. Bellows detects file changes via `git diff --stat` before/after (bellows.py:388-433), not from Claude's output. |
| **File writes** | NOT OBSERVED (from Claude output) | Bellows detects files via `git diff --stat` and deposit-path extraction from plan text (gates.py), not from structured write events in Claude output. |

### What `stream-json` would add

The `--output-format stream-json` flag (documented in `claude --help`) would emit real-time events including tool calls, tool results, and partial messages. Combined with `--include-partial-messages`, this would provide:
- Real-time visibility into which tools are being called and when
- Structured permission events (if any were to fire)
- Progress tracking without waiting for completion
- The ability to detect and react to specific tool patterns mid-execution

Switching would require: (1) changing the flag from `json` to `stream-json`, (2) replacing the single `json.loads()` call with a streaming NDJSON parser, (3) accumulating the final result from the stream. This is a moderate refactor of `runner.py` — the streaming reader threads are already in place (runner.py:81-94), so the I/O plumbing exists.

---

## 5. Implications

### Confirmed explanation: (3) — non-interactive mode defaults

The evidence confirms **explanation (3)**: `claude -p` in non-interactive mode, combined with `--allowedTools`, eliminates permission prompts by design. This is not a bug or workaround — it is the intended CLI behavior for automation use cases.

- **Explanation (1) — auto-approve flag**: FALSE. No `--dangerously-skip-permissions`, no `--permission-mode bypassPermissions`, no auto-approve flag is passed.
- **Explanation (2) — output suppression**: FALSE. Bellows captures both stdout and stderr via `subprocess.PIPE` with dedicated reader threads. Nothing is discarded.
- **Explanation (3) — non-interactive defaults**: TRUE. `--allowedTools` pre-authorizes tools; `-p` mode skips workspace trust; no TTY means no interactive prompts possible.

### Implications for verdict-as-structured-log direction

The verdict system is **not** a lossy substitute for permission prompts that used to be real-time. Permission prompts were a signal in **interactive** sessions only. In Bellows's `claude -p` dispatch model, they were never part of the signal path. The Gate 4 `permission_denials` check is correctly designed as a safety net for the unlikely case where a denial occurs (e.g., if `--allowedTools` were misconfigured or Claude attempted a tool outside the allowed set via some escape).

The real observability gap is not about permissions — it's about **tool-call visibility**. Bellows currently has no structured visibility into which tools the agent called, in what order, or with what arguments. It sees only the final `result` text and the `git diff` delta. The `stream-json` output format would close this gap without requiring any permission-mode changes.

---

## 6. Follow-up questions

1. **Should Bellows switch to `stream-json`?** The streaming format would provide real-time tool-call visibility, progress tracking, and structured event parsing. The runner already has streaming reader threads. This could be a separate diagnostic or a backlog item.

2. **Is the `--allowedTools Read,Edit,Write,Bash` set optimal?** Agents currently lack Glob, Grep, Agent, and all MCP tools. They compensate via `Bash(find ...)`, `Bash(grep ...)`, etc. — which works but means the agent can't use the optimized dedicated tools. Adding Glob and Grep to the allowed set would be low-risk and potentially improve agent efficiency.

3. **What is the default `--permission-mode` for `-p` mode?** The CLI help lists choices but doesn't document the default for non-interactive mode. This is academic given the `--allowedTools` pre-authorization, but worth confirming if Bellows ever needs to dispatch without an explicit tool list.

---

## Output Receipt
**Agent:** Bellows Systems Analyst
**Step:** 1 (single-step diagnostic)
**Status:** Complete

### What Was Done
Investigated why permission prompts do not fire during Bellows-dispatched `claude -p` sessions. Traced the mechanism through `runner.py` subprocess invocation, `parser.py` output parsing, and `gates.py` permission denial checking. Confirmed explanation (3): `--allowedTools` pre-authorization combined with non-interactive `-p` mode eliminates prompts by design.

### Files Deposited
- `bellows/knowledge/research/permission-prompt-substrate-2026-04-23.md` — diagnostic findings covering Q5a/Q5b/Q5c with signal observability table

### Files Created or Modified (Code)
- None — investigation only

### Decisions Made
- Empirical branch not required (documentation + code reading was sufficient)

### Flags for CEO
- The `--allowedTools` set (`Read,Edit,Write,Bash`) excludes Glob, Grep, Agent, and MCP tools — dispatched agents operate in a constrained tool environment. This is a deliberate design choice but worth periodic review.
- The `stream-json` output format exists and would provide real-time tool-call visibility — the actual observability gap is tool calls, not permissions.

### Flags for Next Step
- None — single-step diagnostic, no next step
