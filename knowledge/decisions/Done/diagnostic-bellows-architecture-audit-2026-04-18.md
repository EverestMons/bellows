# Bellows — Architecture Audit (AI intelligence + plan truncation bug)
**Date:** 2026-04-18 | **Tier:** Medium | **Test Scope:** N/A (read-only diagnostic) | **Execution:** Step 1 (DEV) — single step, Planner verifies via Rule 22 | **Priority:** 1

## CEO Context

Two investigations compose into one diagnostic because they share source-file reads. (A) CEO wants to confirm Bellows is pure routing infrastructure with no hidden AI intelligence — every place Claude gets invoked, every non-deterministic code path, every LLM call if any. (B) Plan truncation bug reproduced today on `diagnostic-forge-scoping-2026-04-18.md` — clean 5,206-byte plan file was mirrored by a 1,418-byte `verdict-pending-*` copy with Step 1 + investigation instructions removed. Prior Bellows backlog items (2026-04-17) identified this pattern but root cause is unclear — may be agent-side Edit tool use OR Bellows-side state progression. Both files now preserved in `forge/knowledge/decisions/Done/` (clean version at canonical name, truncated version with `_truncated-` prefix). Bellows has NO specialist agent file — this diagnostic routes to a generic agent and embeds file paths explicitly.

## How to Run This Plan

Paste the bootstrap prompt into Claude Code. Agent executes Step 1, deposits findings, stops. Planner (in Project conversation) reads findings via direct tool call, performs Rule 22 verification, moves plan to Done directly.

**Bootstrap prompt:**

```
Read the plan at bellows/knowledge/decisions/diagnostic-bellows-architecture-audit-2026-04-18.md. Execute Step 1. After completing Step 1, STOP. Do NOT move the plan to Done — the Planner handles that after verification.
```


---
---

## STEP 1 — GENERIC AGENT (no specialist file — Bellows has no specialist authored)

---

> **FIRST — before doing anything else, claim this plan:** `import shutil; shutil.move("bellows/knowledge/decisions/diagnostic-bellows-architecture-audit-2026-04-18.md", "bellows/knowledge/decisions/in-progress-diagnostic-bellows-architecture-audit-2026-04-18.md")`. No specialist file exists for Bellows — read `bellows/CLAUDE.md` and `bellows/PROJECT_STATUS.md` to establish context. Skip glossary read — this is a code-investigation task. You are investigating four areas and depositing a structured findings file at `bellows/knowledge/research/bellows-architecture-audit-2026-04-18.md`. Do NOT fix anything, do NOT write code, do NOT modify the DB. Read-only investigation. All paths in your deposited findings must be bellows-cwd-relative (`runner.py`, `knowledge/research/...`), never repo-root-prefixed. When writing the findings file, use the canonical Python `with open(...) as f: f.write(content)` pattern — no heredoc. **Do NOT use the Edit or Write tools on any file other than your single deposit target** — specifically, do NOT modify the plan file you are executing. Standard prompt feedback protocol → `bellows/knowledge/research/agent-prompt-feedback.md`. **STOP** after depositing findings. Do NOT move the plan to Done — the Planner handles that.

### Files to Read

Primary source files (`bellows/` repo root):
- `bellows.py` — main entry point / daemon
- `runner.py` — plan execution, Claude CLI invocation (presumed)
- `gates.py` — gate checks
- `parser.py` — plan file parsing
- `verdict.py` — verdict handling
- `planner.py` — (name overlaps with governance "Planner" role — investigate purpose)
- `server.py` — HTTP server?
- `notifier.py` — heartbeat/status notifier?
- `requirements.txt` — dependency audit for anthropic/openai/API libs
- `config.json` and `config.example.json` — configuration shape
- `bellows.db` — schema via `sqlite3.connect('bellows.db')` and `.schema` / `PRAGMA table_info`

Evidence files from today's truncation reproduction:
- `forge/knowledge/decisions/Done/diagnostic-forge-scoping-2026-04-18.md` (5,206 bytes — complete, original content)
- `forge/knowledge/decisions/Done/_truncated-verdict-pending-diagnostic-forge-scoping-2026-04-18.md` (1,418 bytes — truncated after agent execution)

### Investigation Sections

**Section 1 — Claude invocation points.** Find every place in Bellows source that invokes Claude or any LLM. For each: (a) file and function name with line range, (b) exact command or API call shape, (c) what prompt is passed, (d) what the caller does with the response (stdout parsing, JSON extraction, etc.). Specifically grep for: `claude -p`, `claude -c`, `subprocess` calls with claude, `anthropic.` (SDK), `openai.`, `ANTHROPIC_API_KEY`, `api_key`. Report every hit. If you find zero SDK imports in `requirements.txt`, note that too. Also enumerate every `subprocess.run`, `subprocess.Popen`, and `os.system` call — some of these may be non-Claude invocations (git commands, shell utilities) and are in-scope to document.

**Section 2 — Non-deterministic / AI-shaped code audit.** Beyond explicit Claude invocations, inventory any code that exhibits non-deterministic behavior or could plausibly use an LLM in the future. For each: (a) file and function, (b) current implementation (regex? LLM? classifier?), (c) purpose it serves, (d) classification per ADR-001 three-layer model — is this currently Layer 1 (mechanical/deterministic), Layer 2 (governance prose that agents read), or Layer 3 (LLM-shaped reasoning)? Specifically examine: `gates.py` (how gate outcomes are classified), `verdict.py` (how verdicts are consumed/generated), `parser.py` (how plan files are parsed — regex vs LLM?), `planner.py` (what this file does — its name overlaps with the governance "Planner" role and needs explicit disambiguation from the CEO's Planner role). If any file uses LLM-based logic, that's a finding that affects ADR-001's clean Layer 1 framing of Bellows.

**Section 3 — Plan lifecycle trace (truncation investigation).** Walk a plan file through Bellows's complete lifecycle. Document every file-system operation (read/write/rename) Bellows performs on plan files. Specifically answer: (a) when a plan is first claimed, what filename prefix changes occur and where in the code? (b) when a step completes, what modifications does Bellows make to the plan file itself (content modification, not just renames)? (c) when gate checks fail, what happens to the plan file? (d) when `verdict-pending-*` is transitioned back to clean state, what happens? For the 2026-04-18 reproduction: a 5,206-byte plan became a 1,418-byte `verdict-pending-*` file with Step 1 + investigation instructions removed — trace exactly where in the Bellows code that truncation could occur. Identify whether truncation is (i) Bellows writing a truncated version itself, (ii) the agent's Edit tool modifying the plan file, or (iii) some third mechanism. Cite specific line ranges.

**Section 4 — State persistence mechanisms.** Does Bellows cache plan content anywhere before dispatching to the agent? Query `bellows.db` schema with `PRAGMA table_info` for each table and document what Bellows persists. Specifically: is there a table that stores plan text, plan step content, or plan metadata (total_steps, current_step)? Is there any in-memory cache in `bellows.py` that survives across runs? If no shadow copy exists today, note that — the Bellows backlog already flags this as a proposed fix for the truncation bug, and confirming absence is useful. Also check: does `.bellows-cache/` directory contain anything relevant? (Briefly inspect, don't deep-dive.)

### Output Format

Deposit findings to `bellows/knowledge/research/bellows-architecture-audit-2026-04-18.md` with section/subsection numbering from above. Each subsection is a distinct markdown heading. Cite file paths with line numbers (`runner.py:142-158` format). Include an Output Receipt at the end using the standard format.

### Critical Guardrail

**Do NOT modify this plan file or any other file except your single deposit target.** The truncation bug is currently under investigation — any Edit/Write tool use on files other than your deposit would contaminate the evidence of whether the bug is agent-side or Bellows-side. If you find yourself needing to modify a file to complete investigation, STOP and report it — the Planner will decide whether the modification is warranted.

**STOP** after depositing. Do NOT move the plan to Done.
