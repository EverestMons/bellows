# Bellows Architecture Audit — Findings
**Date:** 2026-04-18 | **Investigator:** Claude agent (generic — no Bellows specialist exists)

---

## Section 1 — Claude Invocation Points

### 1.1 runner.py — Primary Claude CLI invocation

- **File/function:** `runner.py:run_step()` lines 25-241
- **Command shape:** `subprocess.Popen(["claude", "-p", prompt, "--output-format", "json", "--model", model, "--allowedTools", allowed_tools], ...)`
- **Optional flags:** `--resume session_id` when continuing a session
- **Prompt source:** The `prompt` parameter — constructed by `bellows.py:run_plan()` as a bootstrap prompt (e.g., "Read the plan at {plan_path}. Execute Step 1 ONLY...")
- **Response handling:** stdout is captured via streaming reader threads, joined into `result_stdout`, parsed as JSON via `json.loads()`, then passed to `parser.parse()` which extracts structured fields (session_id, receipt_status, cost_usd, ceo_flags, verdict_requested, etc.)
- **Subprocess type:** `subprocess.Popen` (non-blocking, with inactivity timeout monitoring via threaded stream readers)
- **Invocation site:** Called from `bellows.py:run_plan()` at lines 237 and 293

### 1.2 planner.py — Legacy Planner consultation (DEAD CODE)

- **File/function:** `planner.py:consult()` lines 108-178
- **Command shape:** `subprocess.run(["claude", "-p", prompt, "--output-format", "json", "--model", model, "--allowedTools", "Read"], cwd="/tmp", capture_output=True, text=True, timeout=120)`
- **Prompt source:** Builds a consultation file in `/tmp/bellows-consult-{uuid}.md` containing PLANNER_TEMPLATE.md + COMPANY.md + context envelope (plan text, step output, receipt summary). The prompt instructs Claude to return a JSON decision object.
- **Response handling:** Parses stdout as JSON, extracts `raw["result"]`, strips markdown fences, parses inner JSON as `{"decision": "continue|rewrite|escalate", "reason": "...", "next_step_prompt": "..."}`.
- **DEAD CODE STATUS:** `import planner` exists at `bellows.py:27` but `planner.` is never referenced anywhere in `bellows.py`. Phase 7 (2026-04-16) replaced Planner consultation with mechanical gates (`gates.py`). The module is imported but never called. Test files (`test_planner.py`, `test_phase4_planner_retry.py`) still import it.

### 1.3 bellows.py — Git subprocess calls (non-Claude)

Two `subprocess.run` calls that invoke git, NOT Claude:

1. **`bellows.py:_capture_git_diff()`** lines 372-381
   - Command: `["git", "--no-pager", "diff", "--stat"]`
   - Purpose: Captures file change state before/after each step for scope_check gate
   - Response: stdout text passed to `_parse_diff_stat()`

2. **`bellows.py:_source_sha()`** lines 408-421
   - Command: `["git", "log", "-1", "--format=%h", "--", "bellows.py"]`
   - Purpose: Displays source commit SHA in startup banner for staleness detection
   - Response: Short hash string printed at boot

### 1.4 Dependency audit — requirements.txt

```
anthropic    ← LISTED but NEVER imported or used in any .py file (dead dependency)
watchdog     ← used: bellows.py filesystem watcher
flask        ← used: server.py callback server
requests     ← used: notifier.py Pushover HTTP calls
```

**Zero SDK imports found.** No `import anthropic`, no `import openai`, no `ANTHROPIC_API_KEY`, no `api_key` reference in any Python source file. The `anthropic` package in requirements.txt is a dead dependency — likely a holdover from early development before the `claude -p` CLI approach was adopted.

### 1.5 Complete subprocess inventory

| File | Line | Command | Purpose |
|------|------|---------|---------|
| runner.py | 48 | `subprocess.Popen(["claude", "-p", ...])` | Execute plan steps via Claude CLI |
| planner.py | 129 | `subprocess.run(["claude", "-p", ...])` | Legacy Planner consultation (dead code) |
| bellows.py | 375 | `subprocess.run(["git", "diff", ...])` | Pre/post step file change tracking |
| bellows.py | 411 | `subprocess.run(["git", "log", ...])` | Source SHA for startup banner |

No `os.system` calls found anywhere.

---

## Section 2 — Non-deterministic / AI-shaped Code Audit

### 2.1 gates.py — Pure Layer 1 (mechanical/deterministic)

All 8 gates use deterministic logic:

| Gate | Function | Implementation | Layer |
|------|----------|---------------|-------|
| 1 — receipt_status | `_gate_receipt_status()` | String equality check (`== "Complete"`) | Layer 1 |
| 2 — ceo_flags | `_gate_ceo_flags()` | List emptiness check | Layer 1 |
| 3 — no_errors | `_gate_no_errors()` | Boolean check (`is_error`) | Layer 1 |
| 4 — no_permission_denials | `_gate_no_permission_denials()` | List emptiness check | Layer 1 |
| 5 — deposit_exists | `_gate_deposit_exists()` | `os.path.isfile()` checks + regex path extraction | Layer 1 |
| 6 — qa_step_detection | `_gate_is_qa_step()` | Regex match on step header (`"qa" in match.group(0).lower()`) | Layer 1 |
| 7 — file_change_audit | `_gate_file_change_audit()` | Pass-through (informational) | Layer 1 |
| 8 — scope_check | `_gate_scope_check()` | String containment check (`fpath in step_text or basename in step_text`) | Layer 1 |

Helper `_parse_plan_header()` (lines 17-28): Regex-based YAML frontmatter parser. Splits on `:`, strips whitespace and `*` chars. No LLM involvement.

Helper `_extract_plan_required_deposits()` (lines 157-177): Three regex patterns to find deposit paths in plan text. Pure string matching.

**Classification: 100% Layer 1. No non-deterministic behavior. No LLM calls.**

### 2.2 parser.py — Pure Layer 1 (mechanical/deterministic)

- `parse()` (lines 6-57): Extracts structured fields from Claude CLI JSON output. Uses `dict.get()` for field extraction and regex for two specific patterns:
  - CEO flags: `re.search(r"### Flags for CEO\s*\n(.*?)(?=\n##|\Z)", ...)` — regex match on agent output text
  - Verdict requested: `re.search(r"^VERDICT_REQUESTED:\s*(.+)$", ...)` — regex match on agent output text
  - Receipt status: Inferred from `stop_reason` field (string comparison: `"end_turn"` → Complete, `"max_tokens"` → Partial)
- `is_clean()` (lines 60-65): Boolean composition of parsed fields

**Classification: 100% Layer 1. All regex-based text extraction from structured JSON. No LLM calls.**

### 2.3 verdict.py — Pure Layer 1 (mechanical/deterministic)

- `_slug_from_path()` (lines 13-23): String prefix stripping
- `post_verdict_request()` (lines 26-77): Template-based markdown file generation (string concatenation). No LLM involvement — the content is purely derived from gate_result dict fields.
- `check_verdict()` (lines 80-101): File existence check + regex match (`r"^verdict:\s*(continue|stop)$"`)
- `log_to_ledger()` (lines 104-120): JSON line append to ledger file

**Classification: 100% Layer 1. File I/O + regex + string templates. No LLM calls.**

### 2.4 planner.py — Contains LLM invocation (LEGACY / DEAD)

- `build_system_prompt()` (lines 18-29): File reads (PLANNER_TEMPLATE.md + COMPANY.md)
- `build_context_envelope()` (lines 32-65): String template construction
- `build_consult_file()` (lines 68-84): Writes consultation prompt to `/tmp/`
- `consult()` (lines 108-178): **Invokes Claude via `claude -p` subprocess.** This is the only file that performs LLM-shaped reasoning — it asks Claude to make a continue/rewrite/escalate decision based on step output.

**Classification: Layer 3 (LLM-shaped reasoning). However, this module is DEAD CODE as of Phase 7 — `bellows.py` imports it but never calls any of its functions. The Planner consultation was replaced by mechanical gates in `gates.py`.**

### 2.5 bellows.py — Pure Layer 1 orchestration

Key functions and their determinism:

- `extract_step_number()` (line 79-83): Regex on result text — Layer 1
- `extract_total_steps()` (line 86-87): Regex count of `## STEP` headers — Layer 1
- `header_says_pause()` (lines 157-166): String comparison on header dict — Layer 1
- `is_runnable_plan()` (lines 424-427): Regex match on filename — Layer 1
- `run_plan()` (lines 173-369): Orchestration loop — file reads, subprocess dispatch, gate checks, file renames. All deterministic control flow based on gate results.
- `_consume_verdicts()` (lines 561-667): File scanning + regex matching + file renames. Layer 1.

**No LLM-shaped logic in the orchestrator.** All decisions (continue/pause/halt/auto-close) are made by mechanical checks on gate results, header fields, and verdict files.

### 2.6 server.py — Pure Layer 1

Flask HTTP endpoint. Receives POST JSON, puts it in a queue. No LLM involvement.

### 2.7 notifier.py — Pure Layer 1

HTTP POST to Pushover API. Template-based message construction. No LLM involvement.

### 2.8 ADR-001 Three-Layer Summary

| Component | Layer | Notes |
|-----------|-------|-------|
| bellows.py | Layer 1 | Pure orchestration/routing |
| runner.py | Layer 1 | Dispatches to Claude CLI but does not interpret results with AI |
| gates.py | Layer 1 | All 8 gates are regex/boolean/string checks |
| parser.py | Layer 1 | Regex extraction from structured JSON |
| verdict.py | Layer 1 | File I/O + templates |
| server.py | Layer 1 | HTTP endpoint |
| notifier.py | Layer 1 | HTTP POST to Pushover |
| planner.py | Layer 3 (DEAD) | Contains LLM consultation via claude -p but is never called from bellows.py |

**Conclusion: Bellows is pure Layer 1 infrastructure.** The only LLM-shaped code (`planner.py:consult()`) is dead code — imported but never invoked. All plan execution decisions are mechanical. Claude CLI is invoked as a tool (Layer 1 dispatch) but Bellows never interprets results using AI — it uses regex/boolean gates exclusively.

---

## Section 3 — Plan Lifecycle Trace (Truncation Investigation)

### 3.1 Complete file-system operations on plan files

Every filesystem operation Bellows performs on plan files, in execution order:

**Initial claim (bellows.py:208-212):**
```
1. plan_text = load_file(plan_path)              # READ content at original path (line 181)
2. shutil.move(plan_path, inprogress_path)        # RENAME: foo.md → in-progress-foo.md (line 209)
3. _write_shadow(plan_filename, plan_text)         # WRITE: .bellows-cache/foo.md.pristine (line 212)
```

**Zero-step skip (bellows.py:220):**
```
4. shutil.move(plan_path, Done/plan_filename)      # RENAME: in-progress-foo.md → Done/foo.md
5. _delete_shadow(plan_filename)                    # DELETE: .bellows-cache/foo.md.pristine
```

**Mid-plan verdict pause (bellows.py:279-281):**
```
6. shutil.move(inprogress_path, verdict_pending_path)  # RENAME: in-progress-foo.md → verdict-pending-foo.md
```

**Final-step verdict pause (bellows.py:337-339):**
```
7. shutil.move(inprogress_path, verdict_pending_path)  # RENAME: (same as #6)
```

**Auto-close (bellows.py:358-361):**
```
8. shutil.move(source, done_path)                  # RENAME: in-progress-foo.md → Done/foo.md
9. _delete_shadow(plan_filename)                    # DELETE shadow
```

**Verdict continue — non-final step (bellows.py:642-648):**
```
10. shutil.move(full_plan_path, inprogress_path)   # RENAME: verdict-pending-foo.md → in-progress-foo.md
    → handle_new_plan(inprogress_path, resume_step=N+1)  # RE-DISPATCH
```

**Verdict continue — final step (bellows.py:634-637):**
```
11. shutil.move(full_plan_path, done_path)         # RENAME: verdict-pending-foo.md → Done/foo.md
12. _delete_shadow(original_name)                   # DELETE shadow
```

**Verdict stop (bellows.py:651-654):**
```
13. shutil.move(full_plan_path, halted_path)       # RENAME: verdict-pending-foo.md → halted-foo.md
14. _delete_shadow(original_name)                   # DELETE shadow
```

### 3.2 Critical finding: Bellows NEVER modifies plan file content

**Bellows performs zero writes to plan file content.** Every plan file operation is a rename via `shutil.move()`. The file content passes through Bellows untouched — it is read once (line 181) for metadata extraction and shadow caching, then the file is only renamed throughout its lifecycle.

The only files Bellows writes content to are:
- `.bellows-cache/*.pristine` — shadow copies (bellows.py:105)
- `logs/*.json` — step output logs (runner.py:21)
- `verdicts/pending/verdict-request-*.md` — verdict request files (verdict.py:76)
- `verdicts/ledger.jsonl` — verdict audit log (verdict.py:119)
- `/tmp/bellows-consult-*.md` — legacy planner consultation files (planner.py:83, dead code)

### 3.3 Truncation evidence analysis — forge-scoping reproduction

**File sizes:**
- Clean plan (preserved in Done/): 5,206 bytes — full content with CEO Context + How to Run + STEP 1 section
- Truncated version (\_truncated-verdict-pending-\*): 1,418 bytes — only CEO Context + How to Run, missing the `---\n---` separator and entire STEP 1 section
- Shadow cache (.bellows-cache/diagnostic-forge-scoping-2026-04-18.md.pristine): **1,418 bytes** — matches truncated version exactly

**Critical implication of shadow cache size:** The shadow cache is written at `bellows.py:212`, which executes BEFORE `runner.run_step()` at line 237. This means the shadow was created from `plan_text` which was read at line 181 — BEFORE the agent was dispatched. Therefore:

**The plan file was already 1,418 bytes when Bellows first read it.**

This rules out the hypothesis that the agent's Edit tool caused the truncation. The file was truncated BEFORE Bellows processed it.

### 3.4 Root cause identification

The truncation is **NOT caused by Bellows-side code** (Bellows never writes plan content) and **NOT caused by agent-side Edit tool use** (shadow cache proves file was already truncated at claim time).

**Most likely root cause: Planner multi-write race condition.**

This matches the documented pattern in `knowledge/research/session-lessons-2026-04-16.md` Lesson 8: "Planner multi-chunk writes race against Bellows watcher."

Sequence of events:
1. The Planner begins writing the plan file — first write deposits the header/CEO Context/How to Run section (1,418 bytes)
2. Bellows watchdog fires on file creation/modification
3. Bellows reads the partial file (1,418 bytes), claims it (renames to `in-progress-*`), writes shadow (1,418 bytes)
4. The Planner's second write (the `---\n---` separator + STEP 1 section) targets the original path — but that file no longer exists (it was moved)
5. Result: the `in-progress-*` file contains only the first 1,418 bytes; the STEP 1 content is lost

**The existing 5,206-byte clean version in Done/** was likely manually restored by the CEO after discovering the truncation.

### 3.5 Why the plan still executed despite truncation

Despite the STEP 1 section being missing from the file, Bellows still dispatched the agent because:
1. `is_diagnostic = True` (filename starts with "diagnostic-") at bellows.py:198
2. `total_steps = 1` is hardcoded for diagnostics at bellows.py:201
3. The bootstrap prompt (`bellows.py:228`) says "Read the diagnostic at {plan_path}. Execute it fully" — it doesn't embed the plan content, it tells the agent to read the file
4. The agent reads the truncated file and finds no STEP 1 section — behavior depends on what the agent does with missing instructions

---

## Section 4 — State Persistence Mechanisms

### 4.1 bellows.db schema

Single table: `runs`

| cid | name | type | notnull | default | pk |
|-----|------|------|---------|---------|-----|
| 0 | id | INTEGER | 0 | None | 1 |
| 1 | plan_path | TEXT | 0 | None | 0 |
| 2 | project | TEXT | 0 | None | 0 |
| 3 | session_id | TEXT | 0 | None | 0 |
| 4 | step | INTEGER | 0 | None | 0 |
| 5 | status | TEXT | 0 | None | 0 |
| 6 | cost_usd | REAL | 0 | None | 0 |
| 7 | started_at | TEXT | 0 | None | 0 |
| 8 | completed_at | TEXT | 0 | None | 0 |
| 9 | timestamp | TEXT | 0 | None | 0 |
| 10 | cost | REAL | 0 | None | 0 |

**302 rows** as of audit time.

**No plan text or step content is stored in the database.** The `runs` table records only operational metadata (path, step number, status, cost). There is no table for plan content, plan checksums, or step text.

Note: columns `cost_usd` and `cost` appear to be duplicates (historical migration artifact). Columns `started_at` and `completed_at` exist in the schema but the current `record_run()` function at `bellows.py:123-150` only writes to `timestamp`, `plan_path`, `project`, `session_id`, `step`, `status`, `cost` — it does not write `cost_usd`, `started_at`, or `completed_at`.

### 4.2 Shadow cache (.bellows-cache/)

The `.bellows-cache/` directory contains shadow copies of plan files:

- **Location:** `BELLOWS_ROOT / ".bellows-cache"` (bellows.py:18)
- **Filename convention:** `{canonical_plan_name}.pristine` (bellows.py:98)
- **Write point:** `_write_shadow()` at bellows.py:101-105 — called once per plan, at claim time (line 212)
- **Read point:** `_read_shadow()` at bellows.py:108-113 — called at plan start (line 192) and in `_consume_verdicts` continue path (line 619)
- **Delete point:** `_delete_shadow()` at bellows.py:116-120 — called on auto-close (line 361), continue-to-done (line 637), and halt (line 654)
- **Current contents:** 25 `.pristine` files representing plans that have passed through Bellows but not yet had their shadow deleted (verdict-pending or in-progress plans)

**Purpose:** Shadow copies preserve pristine plan content so that metadata (total_steps, header fields) can be read from the original plan even if the agent modifies the plan file during execution. Introduced as part of the truncation bug mitigation.

**Limitation found during this audit:** The shadow is written from `plan_text` which is read at line 181 — if the source file is partially written at read time (Planner multi-write race), the shadow preserves the TRUNCATED content, not the clean content. The shadow cache does NOT protect against the Planner write-race — it only protects against post-claim agent modifications.

### 4.3 In-memory state

- `plan_text` — local variable in `run_plan()`, does not survive across runs
- `Bellows._active_count` — thread counter, ephemeral
- `PlanHandler._seen` — set of seen plan paths, ephemeral (lost on restart)
- `PlanHandler._pending_groups` — dict of pending parallel groups, ephemeral
- `ResponseServer._response_queue` — queue.Queue for HTTP callback responses, ephemeral

**No in-memory cache of plan content persists across runs.** The only durable plan content store is the `.bellows-cache/` shadow directory.

### 4.4 config.json shape

```json
{
  "watched_projects": ["<absolute paths to knowledge/decisions/ dirs>"],
  "default_model": "claude-opus-4-6",
  "planner_model": "claude-sonnet-4-6",
  "pushover": {"app_key": "...", "user_key": "..."},
  "step_timeout_seconds": 2400,
  "callback_port": 5000,
  "tailscale_ip": "..."
}
```

Note: `step_inactivity_timeout_seconds` is checked first (bellows.py:239), falling back to `step_timeout_seconds`. Only `step_timeout_seconds` exists in config.json. `planner_model` exists but is unused (planner.py is dead code).

---

## Output Receipt

### Status: Complete
### Files Deposited
- `knowledge/research/bellows-architecture-audit-2026-04-18.md`

### Summary
Read-only architecture audit of Bellows. Four sections investigated:
1. **Claude invocations:** Two callsites — `runner.py:run_step()` (active, dispatches plan steps via `claude -p` subprocess) and `planner.py:consult()` (dead code, never called from bellows.py since Phase 7). Two git subprocess calls for diff tracking and SHA display. `anthropic` in requirements.txt is a dead dependency (never imported).
2. **AI-shaped code:** Bellows is 100% Layer 1 (mechanical/deterministic). The only Layer 3 code (`planner.py`) is dead — imported but never called. All 8 gates are regex/boolean/string checks. No SDK imports.
3. **Plan truncation:** Root cause identified as **Planner multi-write race condition**, NOT agent Edit tool and NOT Bellows-side code. Shadow cache evidence (1,418 bytes = truncated size) proves the plan was already truncated when Bellows first read it. Bellows never writes plan file content — only renames. The shadow cache does not protect against write-races (it preserves whatever content exists at claim time).
4. **State persistence:** Single DB table (`runs`, 302 rows) stores operational metadata only — no plan content. Shadow cache (`.bellows-cache/`) stores pristine plan copies but is vulnerable to the same write-race that caused the truncation. No in-memory caches survive across runs.
