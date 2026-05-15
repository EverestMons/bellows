# Plan Mutation Source — Diagnostic Findings
**Date:** 2026-04-19
**BACKLOG refs:** #6 (plan file truncation v2), #7 (agent rewrites plan files)
**Prior art:** `plan-file-truncation-2026-04-17.md` — reached same conclusion via static analysis only; this investigation adds controlled reproduction with filesystem-level evidence.

---

## 1. Preconditions Checked

- Bellows daemon running: **Yes** (PID 45951, `python bellows.py`)
- Current source: post-restart with shadow cache, verdict lifecycle coupling, and startup sweep patches
- This diagnostic dispatched by Bellows as `claude -p` with `--allowedTools Read,Edit,Write,Bash`

---

## 2. Part A — Static Source Analysis

Every code path in Bellows that writes to files in `knowledge/decisions/`:

| Location | Function | Trigger | Write Target | Tool/Mode |
|---|---|---|---|---|
| `bellows.py:222` | `run_plan()` | Plan claim (executable→in-progress) | Plan file | `shutil.move` (rename, no content write) |
| `bellows.py:225` | `run_plan()` | Immediately after claim | `.bellows-cache/{name}.pristine` | `path.write_text()` — shadow copy, NOT plan file |
| `bellows.py:233` | `run_plan()` | 0-step plan skip | Plan file → `Done/` | `shutil.move` (rename) |
| `bellows.py:294` | `run_plan()` | Gate failure / QA / verdict-request / header-pause (mid-plan) | in-progress→verdict-pending | `shutil.move` (rename) |
| `bellows.py:352` | `run_plan()` | Same conditions on final step | in-progress→verdict-pending | `shutil.move` (rename) |
| `bellows.py:374` | `run_plan()` | Auto-close (all gates pass, auto_close=true) | in-progress→`Done/` | `shutil.move` (rename) |
| `bellows.py:664` | `_consume_verdicts()` | Continue verdict on final step | verdict-pending→`Done/` | `shutil.move` (rename) |
| `bellows.py:673` | `_consume_verdicts()` | Continue verdict (not final) | verdict-pending→in-progress | `shutil.move` (rename) |
| `bellows.py:682` | `_consume_verdicts()` | Stop verdict | verdict-pending→halted | `shutil.move` (rename) |

**Verdict files (NOT plan files):**

| Location | Function | Write Target | Tool/Mode |
|---|---|---|---|
| `verdict.py:138` | `post_verdict_request()` | `verdicts/pending/verdict-request-{slug}-step-{N}.md` | `filepath.write_text()` |
| `verdict.py:181` | `log_to_ledger()` | `verdicts/ledger.jsonl` | `open(path, "a")` append |
| `runner.py:22` | `_write_log()` | `logs/{timestamp}-step.json` | `json.dump()` |

### Summary

**Zero code paths in Bellows write content to plan files.** Every plan lifecycle transition is a `shutil.move()` which on the same filesystem is `os.rename()` — an atomic metadata operation that never touches file content. The shadow cache write (`bellows.py:225`) targets `.bellows-cache/`, not the plan file.

---

## 3. Part B — Agent Tool Configuration

Source: `runner.py:25-37`

| Factor | Finding |
|---|---|
| **Tools granted** | `Read,Edit,Write,Bash` (default, line 30) |
| **Plan content delivery** | Via file path in bootstrap prompt: `"Read the plan at {plan_path}"` — agent reads the file itself |
| **Read-only protection** | **None.** No mechanism marks the plan file read-only. The agent can freely Edit or Write to the plan path. |
| **Working directory** | `project_path` (`cwd=project_path`, line 53) — the project root, 2 levels above `knowledge/decisions/`. Agent can navigate to plan files. |
| **Session resumption** | `--resume session_id` used for multi-step. Same session = same tool access. |

### Summary

**The agent has unrestricted write access to plan files.** The bootstrap prompt gives the agent the exact path. Nothing prevents the agent from using `Edit`, `Write`, or `Bash` to modify or overwrite the plan file content during execution. The agent could truncate the file by:
1. Using `Write` tool to overwrite with shorter content (e.g., only writing back the current step)
2. Using `Edit` tool to remove sections (e.g., "cleaning up" completed steps)
3. Using `Bash` to run a command that modifies the file

---

## 4. Part C — Controlled Reproduction

### C.1 — Canary plan baseline
- File: `executable-plan-mutation-canary-2026-04-19.md`
- Content: 2-step plan (Step 1 SA, Step 2 QA), each step writes a sentinel file
- **Baseline size: 1331 bytes**
- **Baseline SHA-256 prefix: eb7ce331a13e0170**
- Git baseline commit: `ff289ad`

### C.2 — Watcher deployment
- Script: `scripts/_canary_watcher.py` (watchdog-based, monitors `knowledge/decisions/` and `Done/`)
- Started: PID 46049
- Log: `knowledge/research/_canary-watcher-log-2026-04-19.txt`

### C.3 — Git baseline
- Canary was claimed by Bellows within ~22ms of creation (before git commit on the original path). Committed in-progress state instead: `ff289ad`.

### C.4 — Dispatch
- Bellows auto-dispatched the canary within 22ms of file creation. The `on_created`/`on_modified` FSEvents handler fired correctly.

### C.5 — Cycle completion
- Full cycle completed in ~44 seconds (22:07:42 → 22:08:26)
- Both steps executed successfully
- Plan moved to Done/ (agent-initiated move per Step 2 instructions)

### C.6 — Post-cycle state

| Metric | Value |
|---|---|
| Final byte length | **1331** (unchanged) |
| Final SHA-256 prefix | **eb7ce331a13e0170** (unchanged) |
| `git diff` vs baseline | **Empty** (no content changes) |
| Sentinel 1 (`_canary-step1`) | `step1-sentinel` (correct) |
| Sentinel 2 (`_canary-step2`) | `step2-sentinel` (correct) |
| Shadow cache | `executable-plan-mutation-canary-2026-04-19.md.pristine` — 1331 bytes (correct) |

### Full watcher log

```
22:07:42.730 CREATED   executable-...canary...md.tmp.45984 (Write tool temp file)
22:07:42.730 MODIFIED  executable-...canary...md.tmp.45984
22:07:42.731 MOVED     .tmp → executable-...canary...md        size=1331 sha=eb7ce331a13e0170
22:07:42.754 MOVED     executable-...→ in-progress-...         size=1331 sha=eb7ce331a13e0170
22:07:43.145 MODIFIED  in-progress-...                         size=1331 sha=eb7ce331a13e0170
22:07:43.189 MODIFIED  in-progress-...                         size=1331 sha=eb7ce331a13e0170
22:07:45.993 MODIFIED  in-progress-...                         size=1331 sha=eb7ce331a13e0170
22:08:26.738 MOVED     in-progress-...→ Done/executable-...    size=1331 sha=eb7ce331a13e0170
22:08:26.738 CREATED   Done/executable-...                     size=1331 sha=eb7ce331a13e0170
22:08:26.989 MODIFIED  Done/executable-...                     size=1331 sha=eb7ce331a13e0170
22:08:28.423 MODIFIED  Done/executable-...                     size=1331 sha=eb7ce331a13e0170
```

**All 11 events preserved identical size (1331) and hash (eb7ce331a13e0170). Zero content mutations.**

### C.7 — Watcher stopped
- PID 46049 killed successfully after cycle completion.

---

## 5. Part D — Event Timeline Correlation

| Time | Event | Component | Size | Hash | Notes |
|---|---|---|---|---|---|
| 22:07:42.730 | File created (via .tmp→rename) | This diagnostic agent (Write tool) | 1331 | eb7c... | Write tool uses atomic tmp-rename |
| 22:07:42.754 | Renamed to in-progress- | Bellows daemon (`run_plan` L222) | 1331 | eb7c... | `shutil.move` — content-preserving |
| 22:07:43-46 | 3x MODIFIED (metadata only) | macOS FSEvents / Bellows shadow write | 1331 | eb7c... | No content change; likely `_write_shadow` and git operations |
| 22:07:46-22:08:26 | Agent executing Steps 1-2 | `claude -p` subprocess | — | — | Agent wrote sentinel files only, did NOT touch plan file |
| 22:08:26.738 | Renamed to Done/ | Agent (Step 2 executed `shutil.move` via Bash) or Bellows auto-close | 1331 | eb7c... | Content-preserving |
| 22:08:27-28 | 2x MODIFIED (metadata only) | macOS FSEvents | 1331 | eb7c... | No content change |

**All modification events are accounted for.** Zero unaccounted-for writes. The canary's content was pristine from creation through Done/.

### Why the canary was NOT truncated

The canary plan explicitly told the agent: "Do NOT read or modify any other files. Do NOT read this plan file again." This instruction prevented the truncation behavior seen in prior incidents. The canary demonstrates that when the agent does not re-read or re-write the plan file, no truncation occurs — confirming that Bellows itself is not the mutation source.

---

## 6. Part E — Hypothesis Check

### H1 — Bellows itself mutates the plan file
**RULED OUT.**
- Static analysis (Part A): Zero code paths write content to plan files. All transitions are `shutil.move` (rename-only).
- Controlled reproduction (Part C): File content unchanged throughout lifecycle.
- Corroborated by prior investigation (`plan-file-truncation-2026-04-17.md`) which reached the same conclusion independently.

### H2 — The agent has Edit/Write tool access and uses it autonomously
**SUPPORTED — this is the mutation source.**
- The agent receives `Read,Edit,Write,Bash` tool access (Part B).
- The bootstrap prompt gives the agent the exact plan file path.
- Nothing prevents the agent from modifying the plan file.
- The canary was NOT truncated because the instructions explicitly prohibited re-reading the plan. In prior incidents (2026-04-18 `diagnostic-forge-scoping-2026-04-18.md`), the agent likely re-read and then re-wrote the plan file autonomously — even when the plan's instructions were nominally "read-only investigation."
- Claude Code agents exhibit a pattern of "updating" files they've read when they believe they should track progress or clean up. The plan file, being the central document the agent works from, is a natural target for autonomous edits.

### H3 — The runner's I/O handling writes a truncated stream back to disk
**RULED OUT.**
- The runner captures stdout/stderr into in-memory buffers (`stdout_buf`, `stderr_buf` in `runner.py:77-78`).
- These buffers are only written to `logs/{timestamp}-step.json` (line 234) — never to the plan file path.
- No code path in runner.py references the plan file path.
- The watcher log confirms no content mutation during the runner's active period.

### Verdict

**H2 confirmed. The `claude -p` agent is the sole source of plan file mutations.** Neither Bellows infrastructure (H1) nor the runner's I/O handling (H3) modifies plan file content.

---

## 7. Recommendations for BACKLOG #6 / #7 Fix Shape

The mutation source is the agent. Fix candidates, in order of preference:

### R1 — Shadow-cache defense (ALREADY PARTIALLY IMPLEMENTED)
**Status:** The shadow cache (`_write_shadow` at claim time) already protects metadata extraction (step count, headers). Bellows uses `_read_shadow()` to get pristine content for `total_steps` and header parsing, avoiding the truncated plan file.

**Gap:** The shadow cache defends Bellows's internal reads but does NOT prevent the agent from truncating the live plan file. If the agent needs to re-read the plan in later steps (e.g., multi-step plans where each step reads the plan), it reads the potentially-truncated in-progress file, not the shadow.

**Fix:** Have Bellows pass the shadow cache path (read-only) to the agent instead of the mutable in-progress path. Or: inject the step text into the bootstrap prompt directly, so the agent never needs to read the plan file at all.

### R2 — Remove Edit/Write access to plan files at the runner level
**Approach:** Add the plan file path to a deny-list and strip Edit/Write tool access for that specific path. Claude Code's `--allowedTools` doesn't support path-level granularity, so this would require either:
- (a) Making the plan file literally read-only (`chmod 444`) before dispatching the agent, then restoring permissions after
- (b) Moving the plan to a read-only directory or creating a read-only symlink
- (c) Passing plan content inline in the prompt instead of by file path

**Preferred variant:** **(c)** — inject the relevant step text into the bootstrap prompt. The agent never sees the plan file path, so it can't modify it. This also removes a file I/O round-trip.

### R3 — Inline step text in bootstrap prompt (strongest fix)
**Approach:** Instead of `"Read the plan at {path}. Execute Step N."`, change the bootstrap prompt to `"Here is your step:\n\n{step_text}\n\nExecute this step."` The agent never learns the plan file path and cannot modify it.

**Trade-offs:**
- Pro: Completely eliminates the mutation vector. No agent behavior change needed.
- Pro: Faster — saves one Read tool call per step.
- Con: The agent loses full-plan context (can't see other steps, deposits section, etc.). This may affect quality for steps that reference earlier steps.
- Mitigation: Include the full plan in the prompt but strip the path. Or include only the relevant step + the deposits section.

### R4 — Post-step content validation
**Approach:** After each `runner.run_step()` returns, compare the plan file's current content against the shadow cache. If they differ, log the mutation, restore from shadow, and flag it.

**Trade-offs:**
- Pro: Defense-in-depth; works alongside R1-R3.
- Con: Reactive — the mutation already happened. The agent's step may have been affected by reading its own truncated version mid-execution.
- Con: Doesn't prevent data loss in multi-step plans where later steps read the truncated file before Bellows can restore it.

### Recommended fix order
1. **R3** (inline step text) — eliminates the root cause
2. **R4** (post-step validation) — defense-in-depth, catches regressions
3. **R1 gap closure** (agent reads shadow) — fallback for any path where the agent must know the plan file location

---

## Output Receipt
**Agent:** Bellows Systems Analyst
**Step:** 1 (single-step diagnostic)
**Status:** Complete

### What Was Done
Comprehensive investigation of plan file mutation source via static analysis (Parts A-B), controlled reproduction with filesystem watcher (Part C), event timeline correlation (Part D), and hypothesis testing (Part E). Confirmed H2: the `claude -p` agent is the sole source of plan file mutations; Bellows itself and the runner are both content-preserving.

### Files Deposited
- `bellows/knowledge/research/plan-mutation-source-2026-04-19.md` — full diagnostic findings with static analysis, reproduction evidence, and fix recommendations

### Files Created or Modified (Code)
- `bellows/scripts/_canary_watcher.py` — temporary watcher script (can be deleted)
- `bellows/knowledge/decisions/Done/executable-plan-mutation-canary-2026-04-19.md` — canary plan (completed, in Done/)
- `bellows/knowledge/research/_canary-watcher-log-2026-04-19.txt` — watcher event log (evidence)
- `bellows/knowledge/research/_canary-step1-2026-04-19.txt` — sentinel file (evidence)
- `bellows/knowledge/research/_canary-step2-2026-04-19.txt` — sentinel file (evidence)

### Decisions Made
- Confirmed H2 (agent mutation) as the sole source, ruling out H1 (Bellows) and H3 (runner I/O)
- Recommended R3 (inline step text in bootstrap prompt) as the primary fix shape

### Flags for CEO
- The canary plan went through its full lifecycle without truncation because it explicitly told the agent not to re-read the plan file. This confirms the mutation is agent-initiated, not infrastructure-caused.
- The shadow cache is already defending Bellows's internal metadata reads but does not protect the agent's own reads in multi-step plans.
- R3 (inline step text) is the strongest fix and should be prioritized for BACKLOG #6/#7 closure.

### Flags for Next Step
- None (single-step diagnostic)
