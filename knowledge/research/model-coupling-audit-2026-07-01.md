# Model-Coupling Audit — Bellows × Claude Code

**Date:** 2026-07-01
**Author:** Bellows Systems Analyst (diagnostic 109)
**Scope:** Read-only investigation — no code changes

---

## 1. Dispatch Path

### 1.1 CLI invocation (`runner.py:45–54`)

The runner constructs a `claude -p` subprocess command:

```
claude -p <prompt> --output-format stream-json --verbose --model <model>
    --allowedTools <tools> --append-system-prompt <system_prompt>
```

**Classification: hard-coupled.** The executable name `claude`, every CLI flag (`-p`, `--output-format stream-json`, `--verbose`, `--model`, `--allowedTools`, `--append-system-prompt`), and their value formats are Claude Code-specific. No other runtime uses this CLI interface.

### 1.2 Session continuity (`runner.py:53–54`)

When `session_id` is non-None, the runner appends `--resume <session_id>`. This relies on Claude Code's session persistence model where a UUID identifies a conversation that can be resumed across invocations.

**Classification: hard-coupled.** Session resume is a Claude Code concept. Other runtimes (Codex, Gemini) have no equivalent `--resume` flag or use different session management (e.g., conversation threads, API-level continuations).

### 1.3 Environment variables (`runner.py:19`, `bellows.py:23`)

`DISABLE_AUTOUPDATER=1` is injected via `os.environ.setdefault` to suppress Claude Code's background self-updater during plan execution.

**Classification: hard-coupled** (but harmless to other runtimes). An unknown env var would be silently ignored by a non-Claude runtime, so this is coupled but non-breaking. An adapter would simply omit it.

### 1.4 Bootstrap prompt construction (`bellows.py:516–521`)

The bootstrap prompts are plain-English instructions ("Read the plan at X. Execute Step N.") passed as the `-p` argument. The prompt text itself is model-agnostic — no Claude-specific system prompt or formatting assumed. The system prompt injected via `--append-system-prompt` (`runner.py:24`) is behavioral guardrails text, not Claude-specific.

**Classification: already model-agnostic** (prompt content). The _delivery mechanism_ (`-p` flag) is hard-coupled (see 1.1), but the prompt payload would work with any sufficiently capable LLM.

### 1.5 Authentication model (`bellows.py:1669`)

The daemon staggers thread starts with `time.sleep(2)` to "avoid simultaneous claude -p auth hits." This assumes Claude Code's per-invocation auth handshake model.

**Classification: soft-coupled.** An adapter could replace or remove the stagger based on the target runtime's auth model.

### 1.6 Worktree handling (`bellows.py:909–1017`, `1333–1468`)

Worktree creation/teardown is pure git — `git worktree add`, `git merge`, `git worktree remove`. The daemon creates the worktree and passes `wt_path` as the subprocess `cwd`. The agent itself never manages worktrees.

**Classification: already model-agnostic.** Any runtime that can receive a `cwd` would work. The worktree lifecycle is entirely daemon-owned.

### 1.7 Completion/failure detection (`runner.py:114–173`, `176–208`)

The daemon detects completion via three signals:
- **Process exit code**: `proc.returncode != 0` → failure. This is standard subprocess behavior, but the specific exit codes and their semantics are Claude Code-defined.
- **Inactivity timeout**: Monitors `stdout` output timestamps — no output for `timeout` seconds → kill. This is runtime-agnostic in principle.
- **Transient failure retry** (`runner.py:179–186`): Pattern-matches stderr for `"401"`, `"unauthorized"`, `"429"`, `"rate limit"` — these are Claude Code / Anthropic API-specific error patterns.

**Classification: soft-coupled.** Process-exit and inactivity-timeout are generic. The stderr pattern matching for transient errors is Claude Code-specific but easily adapted to other runtimes' error signatures.

### 1.8 No parallel/legacy dispatch path

There is no `manual_bootstrap` or alternative dispatch mechanism. All plans flow through the single `runner.run_step()` → `claude -p` path. The `_consume_verdicts()` resume path also dispatches through the same `handle_new_plan()` → `run_plan()` → `runner.run_step()` pipeline.

---

## 2. Gate Output Parsing

### 2.1 Gate 1: Receipt Status (`gates.py:239–241`)

Reads `parsed["receipt_status"]` which is **computed by `parser.py:15–23`** from the `stop_reason` field in the Claude Code stream-JSON result event. The mapping is:
- `is_error` → `"Blocked"`
- `stop_reason == "end_turn"` → `"Complete"`
- `stop_reason == "max_tokens"` → `"Partial"`
- else → `"Unknown"`

**Classification: hard-coupled.** `end_turn` and `max_tokens` are Claude Code / Anthropic API stop-reason enums. Other runtimes use different completion signals (e.g., Codex uses `stop` / `length`; Gemini uses `STOP` / `MAX_TOKENS`). An adapter would need to normalize stop reasons.

### 2.2 Gate 2: CEO Flags (`gates.py:245–248`)

Reads `parsed["ceo_flags"]`, which is extracted from the **agent's output text** by `parser.py:29–37` via regex: `### Flags for CEO\s*\n(.*?)`. This is an **Output Receipt** convention — the agent is instructed (via the plan and system prompt) to include this section in its output.

**Classification: soft-coupled.** The section heading is a Bellows convention, not a Claude Code format. Any LLM following the Output Receipt format would produce it. However, the reliability of this extraction depends on the agent consistently formatting its output — a different LLM might format differently. The gate falls back cleanly (no flags → no failure).

### 2.3 Gate 3: No Errors (`gates.py:251–254`)

Reads `parsed["is_error"]` which comes from the Claude Code stream-JSON `is_error` field.

**Classification: hard-coupled.** This field is part of Claude Code's output schema. An adapter would need to map the target runtime's error signaling into this boolean.

### 2.4 Gate 4: No Permission Denials (`gates.py:259–282`)

Reads `parsed["permission_denials"]`, which comes directly from Claude Code's stream-JSON `permission_denials` array. The gate inspects:
- `d["tool_name"]` — matches against `READ_CLASS_TOOLS` set (`Grep`, `Glob`, `Read`, `mcp__vexp__*`)
- `d["tool_input"]["command"]` — for Bash exemption pattern matching

**Classification: hard-coupled.** Permission denials are a Claude Code runtime concept (its permission-prompt system). The tool names (`Grep`, `Glob`, `Read`, `Bash`, `Write`, `Edit`) are Claude Code built-in tool names. The `tool_input.command` payload schema is Claude Code-specific. Other runtimes either have no permission system or use different tool taxonomies. An adapter would need to either translate denial events or suppress this gate entirely.

### 2.5 Gate 5: Deposit Exists (`gates.py:371–415`)

Reads `parsed["result_text"]` to extract the `### Files Deposited` section (agent narration), then checks files on disk. Also reads plan text for `**Deposits:**` blocks.

**Classification: soft-coupled.** The `### Files Deposited` section heading is an Output Receipt convention, not Claude Code format — any LLM instructed to follow the Output Receipt will produce it. The disk-existence check is fully model-agnostic. However, the regex parsing of the agent's narrated receipt text (`### Files Deposited\s*\n`) is fragile against format variation.

### 2.6 Gate 6: QA Step Detection (`gates.py:666–686`)

Reads plan header (`qa_steps` field) or falls back to keyword detection in `## STEP N` header text. Reads the **plan text**, not agent output.

**Classification: already model-agnostic.** Reads deposited plan files on disk.

### 2.7 Gate 6b: Rule 20 Self-Check (`gates.py:494–542`)

Reads the **deposited QA report file** on disk. Scans for a specific banner string `"Rule 20 — QA Self-Check Results"` and a `PASSED — SELF-CHECK PASSED` line.

**Classification: already model-agnostic.** Reads on-disk artifacts. The banner text is a Bellows governance convention, not Claude Code format. Any agent following governance rules would produce it.

### 2.8 Gate 6c: Rule 22 Verification (`gates.py:545–663`)

Reads the **deposited QA report file** on disk. Checks for:
- (a) Plan-declared deposits exist on disk
- (c) Verification table format (no ❌ rows)
- (d) No hedging keywords in positive-status rows

**Classification: already model-agnostic.** Reads on-disk artifacts and plan text. The verification table is a governance convention.

### 2.9 Gate 7: File Change Audit (`gates.py:689–692`)

Informational gate. Passes through the `files_changed` list computed by the daemon via `git diff`.

**Classification: already model-agnostic.** Pure git operation.

### 2.10 Gate 8: Scope Check (`gates.py:695–746`)

Compares `files_changed` against mentions in plan step text.

**Classification: already model-agnostic.** Reads plan text and git diff output.

### 2.11 Verdict Requested (`parser.py:40–43`)

Scans `result_text` for `VERDICT_REQUESTED:` marker.

**Classification: soft-coupled.** This is an Output Receipt convention. Any agent following the format would produce it. The extraction is a regex on agent narration.

---

## 3. Step-Log Parsing

### 3.1 NDJSON stream parsing (`runner.py:214–276`)

The runner parses `stdout` as newline-delimited JSON. It expects:
- Events with `{"type": "result", ...}` — the terminal result event
- Events with `{"type": "assistant", "message": {"content": [...]}}` — intermediate assistant turns
- Content blocks with `{"type": "text", "text": "..."}` or `{"type": "tool_use", "name": "Write"/"Edit", "input": {...}}`

**Classification: hard-coupled.** This is Claude Code's `--output-format stream-json` schema. The event types (`result`, `assistant`), message structure (`message.content[]`), content block types (`text`, `tool_use`), and tool-use payload shapes (`name`, `input.content`, `input.new_string`) are all Claude Code-specific. Other runtimes produce completely different output formats. An adapter would need to normalize any runtime's output into this event schema.

### 3.2 Result event field access (`parser.py:7–12`)

The parser reads from the result event:
- `raw["session_id"]` — Claude Code session UUID
- `raw["is_error"]` — Claude Code error flag
- `raw["stop_reason"]` — Claude Code stop reason enum
- `raw["result"]` — final assistant text
- `raw["total_cost_usd"]` — Claude Code cost tracking
- `raw["num_turns"]` — Claude Code turn counter
- `raw["permission_denials"]` — Claude Code permission system

**Classification: hard-coupled.** Every field name and its semantics are defined by Claude Code's stream-JSON output schema. An adapter normalizing to this shape would need to provide: session identity, error status, completion signal, final text, cost, turn count, and permission events.

### 3.3 Step log JSON files (`runner.py:308–313`)

Written to `logs/<timestamp>-step.json` with structure:
```json
{
  "success": true,
  "raw_output": "<full stdout>",
  "stderr": "<stderr>",
  "parsed": { ... }
}
```

The `parsed` key contains the output of `parser.py:parse()`, which holds all the Claude Code-derived fields (session_id, cost_usd, turns, stop_reason, etc.).

**Classification: soft-coupled.** The log file format is daemon-defined, not Claude Code-defined. However, the `parsed` sub-object embeds Claude Code-specific field names. Consumers reading `d["parsed"]["cost_usd"]` or `d["parsed"]["turns"]` would get `None`/0 from a different runtime unless an adapter populates them.

### 3.4 Cost and turn tracking (`bellows.py:560`, `604`, `675`, `717`)

The daemon reads `parsed["cost_usd"]` and `parsed.get("turns")` to record in the lifecycle DB and compute `total_cost`. These values originate from Claude Code's `total_cost_usd` and `num_turns` result event fields.

**Classification: hard-coupled** on field origin, **soft-coupled** on consumption. The fields are optional in practice (gated with `or 0.0`, `.get()`), so a runtime that doesn't provide cost/turns would degrade to `0.0`/`None` rather than crash. But cost tracking would be silently lost.

### 3.5 Dashboard log reading

The dashboard (`dashboard.py`) does **not** read step-log JSON files from `logs/`. It reads lifecycle state from `lifecycle.db` via `status.py` query helpers. The lifecycle DB stores cost_usd, turns, and duration_s per step, but these are written by the daemon from parsed fields (see 3.4), not read from raw logs.

**Classification: already model-agnostic** at the dashboard level. The coupling is upstream in the daemon's write path, not the dashboard's read path.

---

## Summary Table

| # | Coupling Point | Surface | Classification | Adapter Seam |
|---|---|---|---|---|
| 1.1 | CLI invocation (`claude -p` + flags) | Dispatch | **Hard** | Runtime adapter: build command for target CLI |
| 1.2 | Session resume (`--resume`) | Dispatch | **Hard** | Session adapter: map session semantics |
| 1.3 | `DISABLE_AUTOUPDATER` env var | Dispatch | **Hard** (harmless) | Omit for non-Claude runtimes |
| 1.4 | Bootstrap prompt content | Dispatch | Agnostic | — |
| 1.5 | Auth stagger (`sleep(2)`) | Dispatch | **Soft** | Configurable per-runtime stagger |
| 1.6 | Worktree lifecycle | Dispatch | Agnostic | — |
| 1.7 | Completion detection (exit + stderr patterns) | Dispatch | **Soft** | Per-runtime error pattern config |
| 2.1 | `stop_reason` → `receipt_status` mapping | Gate | **Hard** | Normalize stop reasons in parser adapter |
| 2.2 | `### Flags for CEO` section | Gate | **Soft** | Output Receipt convention — LLM-trainable |
| 2.3 | `is_error` flag | Gate | **Hard** | Map target runtime's error signal |
| 2.4 | `permission_denials` + tool names | Gate | **Hard** | Translate or suppress for non-Claude runtimes |
| 2.5 | `### Files Deposited` section | Gate | **Soft** | Output Receipt convention — LLM-trainable |
| 2.6 | QA step detection | Gate | Agnostic | — |
| 2.7 | Rule 20 self-check banner | Gate | Agnostic | — |
| 2.8 | Rule 22 verification table | Gate | Agnostic | — |
| 2.9 | File change audit | Gate | Agnostic | — |
| 2.10 | Scope check | Gate | Agnostic | — |
| 2.11 | `VERDICT_REQUESTED` marker | Gate | **Soft** | Output Receipt convention |
| 3.1 | NDJSON stream-json event schema | Step-log | **Hard** | Output normalizer: translate stream format |
| 3.2 | Result event field names | Step-log | **Hard** | Field-mapping adapter layer |
| 3.3 | Step log `parsed` sub-object | Step-log | **Soft** | Consumers degrade gracefully on missing fields |
| 3.4 | Cost/turn tracking | Step-log | **Soft** | Optional — degrades to 0/None |

### Hard-Coupled Points (8)

These would **break** on swap: CLI invocation (1.1), session resume (1.2), autoupdater env (1.3), stop_reason mapping (2.1), is_error flag (2.3), permission_denials (2.4), NDJSON schema (3.1), result event fields (3.2).

### Soft-Coupled Points (7)

These assume a format that could be **normalized behind an adapter**: auth stagger (1.5), completion detection patterns (1.7), Output Receipt sections (2.2, 2.5, 2.11), step log parsed fields (3.3), cost/turn tracking (3.4).

### Already Model-Agnostic (7)

These read **deposited files on disk** or **plan text**, indifferent to producer: prompt content (1.4), worktree lifecycle (1.6), QA detection (2.6), Rule 20 check (2.7), Rule 22 check (2.8), file change audit (2.9), scope check (2.10).

### Abstraction Seam Requirements

A runtime adapter would need to normalize three layers:

1. **Command builder**: Construct the target runtime's CLI invocation from (prompt, model, cwd, session_id, allowed_tools, system_prompt). This replaces `runner.py:45–54`.

2. **Output normalizer**: Parse the target runtime's stdout stream into the canonical `{session_id, is_error, stop_reason, result, total_cost_usd, num_turns, permission_denials}` shape. This replaces `runner.py:214–276` and `parser.py:parse()`.

3. **Permission translator**: Either map the target runtime's permission/denial events to the `{tool_name, tool_input}` schema gates expect, or suppress Gate 4 for runtimes without a permission system.

---

## Output Receipt

**Agent:** Bellows Systems Analyst
**Step:** 1 (standalone diagnostic)
**Status:** Complete

### What Was Done
Audited all three coupling surfaces (dispatch path, gate output parsing, step-log parsing) across bellows.py, runner.py, parser.py, gates.py, verdict.py, decisions.py, status.py, and dashboard.py. Classified 22 coupling points as hard-coupled (8), soft-coupled (7), or already model-agnostic (7). Identified the three abstraction seams required for multi-model dispatch.

### Files Deposited
- `knowledge/research/model-coupling-audit-2026-07-01.md` — full coupling audit with classification table

### Files Created or Modified (Code)
- None (read-only investigation)

### Decisions Made
- Scoped dashboard analysis to lifecycle DB reads (dashboard does not read step-log JSON files)
- Classified `DISABLE_AUTOUPDATER` as hard-coupled but harmless (unknown env vars are silently ignored)
- Classified Output Receipt sections (Flags for CEO, Files Deposited, VERDICT_REQUESTED) as soft-coupled rather than hard-coupled because they are Bellows conventions trainable into any LLM, not Claude Code format requirements

### Flags for CEO
- None

### Flags for Next Step
- None
