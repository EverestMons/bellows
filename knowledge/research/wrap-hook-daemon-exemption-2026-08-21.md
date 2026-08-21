# Wrap-Hook Daemon Exemption — Diagnostic Findings

**Date:** 2026-08-21 | **Plan:** diagnostic-495 | **Role:** DEV (read-only audit)

---

## Q1 — Channel Characterization

### Three hooks in the enforcement layer

All three are registered at USER scope in `~/.claude/settings.json:14-86`, so they load in **every** Claude Code session on this machine, including daemon-dispatched `claude -p` sessions.

**1. `wrap_debt_hook.py` — SessionStart hook (`settings.json:61-72`)**
- **Gate:** NONE. The hook runs `wrap_check.py` unconditionally at every session start (`wrap_debt_hook.py:56-58`). It never reads `.wrap-in-progress`. Confirmed: `grep -Fc 'wrap-in-progress' wrap_debt_hook.py` → **0** (positive control: `grep -Fc 'wrap-in-progress' wrap_stop_hook.py` → **2**).
- **Emit:** If `wrap_check.py` exits nonzero, injects an `additionalContext` directive via `hookSpecificOutput` containing the full checklist and the phrase "UNWRAPPED SESSION DEBT DETECTED" (`wrap_debt_hook.py:67-75`). If exit 0, emits `{}` (silent). Logs to `hooks.log`: `SessionStart clean` or `SessionStart DEBT-injected`.
- **Daemon reach:** YES — every daemon session hits this. A nonzero `wrap_check` exit is the NORMAL state during working hours (see predicates below), so daemon workers are near-continuously exposed.

**2. `wrap_stop_hook.py` — Stop hook (`settings.json:48-58`)**
- **Gate:** Sentinel-gated. Returns `{}` (allow) immediately if `SENTINEL.exists()` is false (`wrap_stop_hook.py:58-60`), where `SENTINEL = Path("/Users/marklehn/Developer/GitHub") / ".wrap-in-progress"`.
- **Emit:** When armed, runs `wrap_check.py`. If check passes (exit 0): calls `SENTINEL.unlink()`, logs `armed-pass-disarm`, allows. If check fails: logs `armed-BLOCK`, emits `{"decision": "block", "reason": "<checklist>"}` which injects a synthetic "Stop hook feedback" user turn into the session, preventing the turn from ending.
- **Daemon reach:** Only when the sentinel exists. But when it does, the damage is acute: the daemon worker cannot end its turn until it resolves the CEO's wrap checklist — or the step times out.

**3. `wrap_arm_hook.py` — UserPromptSubmit hook (`settings.json:15-27`)**
- **Gate:** Regex match on the user's prompt text (`wrap_arm_hook.py:43-48`). The daemon's prompt is a bootstrap instruction like `"Read the plan at ... Execute Step 1 ONLY..."`, which does not match the trigger pattern (`/wrap`, `session wrap`, etc.).
- **Emit:** If triggered, creates the sentinel file and injects `[wrap-lock ARMED]` context. Otherwise emits `{}`.
- **Daemon reach:** Effectively never — daemon prompts do not match the wrap trigger regex. This hook is not a pollution channel.

### `wrap_check.py` predicates that fire during NORMAL daemon operation

Every `fails.append` site in `wrap_check.py:80-148`:

| Predicate | Line(s) | Ordinary firing condition |
|-----------|---------|--------------------------|
| `[1/project]` uncommitted Done/ files | 86-93 | Any project with completed plans awaiting the next wrap commit — the normal state after a plan closes mid-day |
| `[2/bellows]` uncommitted verdicts/resolved/ | 98-103 | After any verdict is consumed but before the wrap commit |
| `[2/bellows]` unpushed commits | 104-106 | After any daemon activity that commits to bellows (verdicts, logs, etc.) |
| `[3/root]` baton uncommitted | 110-112 | Until the CEO refreshes and commits `shop_next_session.md` |
| `[3/root]` bellows gitlink uncommitted | 113-116 | After any bellows commit bumps the submodule pointer |
| `[3/root]` unpushed root commits | 117-119 | After any governance-root commit |
| `[3b/lessons]` no `Lessons-swept: <today>` | 120-135 | From midnight until the CEO does the daily lessons sweep — fires every day before the wrap |
| `[4/memory]` uncommitted memory changes | 137-141 | After any memory file is written |
| `[4/memory]` unpushed memory | 142-146 | After memory commits before push |

**Exposure window in plain terms:** A daemon worker is NOT exposed to channel 1 only in the narrow window after a successful wrap completes (all four repos clean, baton refreshed with today's `Lessons-swept:` line, everything pushed) and before the NEXT daemon commit or CEO action dirties any repo. In practice this window is minutes to low single-digit hours. For the rest of the working day — typically 8-16 hours — every daemon session start receives the debt injection.

---

## Q2 — Historical Blast Radius Census

### Method

Scanned all 58 step log files in `bellows/logs/` (range: `20260819-123604` through `20260821-121654`). Each file was loaded with `json.load()`, the `raw_output` field extracted, and occurrences counted with `str.count()` — not `grep -c`, which would undercount because a step log's `raw_output` is a single line of NDJSON.

### Controls (reproduced before trusting counts)

| Control | File | Ch1 hits | Ch2 hits | Expected | Pass |
|---------|------|----------|----------|----------|------|
| Positive | `20260821-105713-step.json` | 2 | 2 | >0 both | YES |
| Negative | `20260819-164902-step.json` | 0 | 0 | 0 both | YES |

### Census table

Plan mapping derived from `lifecycle.db` (opened read-only: `file:<abs>?mode=ro`), table `steps`, joined on `step_started_at` timestamp. `bellows.db` (also `mode=ro`) cross-referenced for `plan_slug` and `plan_path`.

| Log file | Plan ID | Plan slug | Step | Project | Ch1 occ. | Ch2 occ. |
|----------|---------|-----------|------|---------|----------|----------|
| 20260820-211125 | 486 | invoice-pulse — Contract-merge Phase 2b | 1 | invoice-pulse | 2 | 0 |
| 20260821-000632 | 487 | governance — DRAFTING_CYCLE.md honing (a) | 1 | bellows* | 2 | 0 |
| 20260821-090228 | 488 | governance — seat-contract honing (b) | 1 | bellows* | 2 | 0 |
| 20260821-094310 | 489 | bellows — plan_lint check-(f) diagnostic | 1 | bellows | 2 | 0 |
| 20260821-100913 | 490 | bellows — plan_lint check-(f) executable | 1 | bellows | 2 | 0 |
| 20260821-101730 | 491 | bellows — plan_lint check-(f) diagnostic | 1 | bellows | 2 | 0 |
| 20260821-101814 | 490 | bellows — plan_lint check-(f) executable | 2 | bellows | 2 | 0 |
| 20260821-103718 | 492 | bellows — check-(f) corrective | 1 | bellows | 2 | 0 |
| 20260821-104122 | 492 | bellows — check-(f) corrective | 2 | bellows | 2 | 0 |
| **20260821-105713** | **493** | **invoice-pulse — Dispute-outcome reconciliation Phase 2** | **1** | **invoice-pulse** | **2** | **2** |
| 20260821-121654 | 494 | invoice-pulse — Dispute-outcome reconciliation Phase 3 | 1 | invoice-pulse | 2 | 0 |

*Plans 487/488 are deposited in `bellows/knowledge/decisions/` but their work targets the governance root.

**Earliest hit:** `20260820-211125-step.json` (plan 486, 2026-08-20 21:11:25). The 41 pre-hook step logs (all 20260819-* and earlier 20260820-*) return 0 hits for both tokens, confirming hooks went live on **2026-08-20**.

**11 of 58 step logs** (19%) are affected. **All 11** have channel-1 injection; **only 1** (exec-493 step 1) has channel-2 blocks.

### Out-of-scope git operations in affected steps

Scanned every hit file's NDJSON stream for `tool_use` blocks with `name: "Bash"` containing `git push`, `git commit`, or `git add` commands targeting repos outside the plan's project path.

**Exec-493 step 1 — three out-of-scope `git push` commands (wrap-debt-induced):**

| Command | Target | Plan project | Out-of-scope |
|---------|--------|-------------|-------------|
| `GIT_TERMINAL_PROMPT=0 git -C /Users/marklehn/Developer/GitHub push` | governance root | invoice-pulse | YES |
| `GIT_TERMINAL_PROMPT=0 git -C /Users/marklehn/Developer/GitHub/bellows push` | bellows | invoice-pulse | YES |
| `GIT_TERMINAL_PROMPT=0 git -C /Users/marklehn/Developer/GitHub/study push` | study | invoice-pulse | YES |

These pushes were triggered by the channel-1 debt injection ("resolve this BEFORE starting new work") combined with channel-2 Stop-blocks that prevented the turn from ending until the wrap verified. The worker iterated through the wrap checklist, found repos with unpushed commits, and pushed them — including `study`, an unrelated repository it discovered by scanning directories.

**All other hit files (10 of 11):** No `git push` commands found. Plans 487 and 488 have `git commit` commands targeting the governance root, but these are their **planned operations** (titles start with "governance —"), not wrap-debt-induced actions.

**Conclusion:** Exec-493's three pushes are the **only** out-of-scope `git push` commands in the entire corpus. However, every channel-1-hit step received the directive to resolve wrap debt "BEFORE starting new work" — any of them could have acted on it had they not completed their planned work first.

### Hooks.log corroboration

`hooks.log` is append-only, one `<iso-ts>\t<event>\t<detail>` line per hook firing, local time. It carries **no session id**, so every attribution below is **INFERRED** via timestamp join.

**Exec-493 step 1 window (lifecycle.db: step_started_at `2026-08-21T10:57:13`, step_ended_at `2026-08-21T11:06:38`):**

| hooks.log timestamp | Event | Detail | Attribution |
|---------------------|-------|--------|-------------|
| 2026-08-21T10:57:13 | SessionStart | DEBT-injected | INFERRED: matches step_started_at exactly |
| 2026-08-21T10:57:16 through 2026-08-21T11:06:16 | Stop | armed-BLOCK | INFERRED: 12 entries within the step window |
| 2026-08-21T11:06:37 | Stop | armed-pass-disarm | INFERRED: 1s before step_ended_at, no other session ending in this window |

The step log records only **2** `[wrap-lock] This turn is blocked` occurrences and **2** `Stop hook feedback` user turns, while hooks.log shows **12** `armed-BLOCK` entries in the same window. The discrepancy is expected: hooks.log records every Stop hook invocation (every turn-end attempt), but only some result in synthetic user turns visible in the NDJSON stream. The CEO's interactive session was likely also hitting the Stop hook during this window (the wrap was armed at `10:48:11` by the CEO), contributing to the hooks.log count — but without session IDs, this attribution is **ambiguous**.

**Disarm confirmation (INFERRED):** The `armed-pass-disarm` at `11:06:37` is attributed to exec-493's session by a two-source join: (1) the step ran `10:57:13→11:06:38.9` per lifecycle.db, and (2) the disarm falls ~2s before the step ended, with no other session's turn-end in that window. Immediately after: `SessionStart clean` at `11:06:39` and `UserPromptSubmit-arm ARMED` at `11:16:33` — the CEO re-arming the wrap that the daemon worker had disarmed.

---

## Q3 — Detection Mechanism Measurement

### Q3(a) — Does a hook subprocess inherit env vars set on the `claude -p` process?

**Sentinel precheck:** `/Users/marklehn/Developer/GitHub/.wrap-in-progress` does NOT exist (verified `ls` → "No such file or directory"). Probe is safe to run.

**Setup:** Created a scratch directory at `/tmp/bellows-q3-probe-43219/` (outside every git repository). Placed `.claude/settings.json` with SessionStart and Stop hooks pointing to Python scripts that write `os.environ.get("BELLOWS_DISPATCH")` and the full `sys.stdin.read()` payload to files.

**Command:**
```
(cd /tmp/bellows-q3-probe-43219 && BELLOWS_DISPATCH=1 claude -p "reply OK" --output-format text --max-turns 1)
```

**Result — env_result.txt (SessionStart hook):**
```
BELLOWS_DISPATCH=1
BELLOWS_DISPATCH_type=present
```

**Result — stop_env_result.txt (Stop hook):**
```
BELLOWS_DISPATCH=1
```

**MEASUREMENT: YES — hooks inherit env vars from the `claude -p` process.** The env var set in the calling shell propagates through the Claude CLI to hook subprocesses. Both SessionStart and Stop hooks see `BELLOWS_DISPATCH=1`.

The full environment also shows `DISABLE_AUTOUPDATER=1` (confirming the existing `setdefault` precedent works end-to-end) and `CLAUDE_CODE_CHILD_SESSION=1` (a Claude-set env var indicating this is a child session).

**Live hooks also fired** during the probe: `hooks.log` shows `SessionStart DEBT-injected` and `Stop unarmed-allow` at `12:34:40`/`12:34:46`, confirming the diagnostic's premise that user-scope hooks load in every session — the probe's project-local hooks ran alongside the live enforcement hooks.

### Q3(b) — Hook stdin payload contents

**SessionStart payload:**
```json
{
  "session_id": "07e9e9c4-720b-49fb-9d63-9fec8207e162",
  "transcript_path": "/Users/marklehn/.claude/projects/-private-tmp-bellows-q3-probe-43219/07e9e9c4-720b-49fb-9d63-9fec8207e162.jsonl",
  "cwd": "/private/tmp/bellows-q3-probe-43219",
  "hook_event_name": "SessionStart",
  "source": "startup"
}
```

**Stop payload:**
```json
{
  "session_id": "07e9e9c4-720b-49fb-9d63-9fec8207e162",
  "transcript_path": "/Users/marklehn/.claude/projects/-private-tmp-bellows-q3-probe-43219/07e9e9c4-720b-49fb-9d63-9fec8207e162.jsonl",
  "cwd": "/private/tmp/bellows-q3-probe-43219",
  "permission_mode": "default",
  "effort": {"level": "high"},
  "hook_event_name": "Stop",
  "stop_hook_active": false,
  "last_assistant_message": "OK",
  "background_tasks": [],
  "session_crons": []
}
```

**No field in either payload directly indicates daemon vs. interactive dispatch.** The `source` field is `"startup"` (not informative). The `cwd` field carries the project path, which is `.bellows-worktrees/<slug>` for worktree-dispatched sessions — but in-place dispatch (governance plans) sets cwd to the project root, making a cwd heuristic insufficient. The `permission_mode` is available but the daemon doesn't set a distinct mode.

**Conclusion:** The env var approach (Q3(a)) is the reliable detection mechanism. A payload-based predicate via `cwd` is a partial fallback but cannot cover in-place dispatch.

---

## Q4 — Spawn Site Enumeration

### Positive control
Searched with `/usr/bin/grep -rn '"claude"' /Users/marklehn/Developer/GitHub/bellows/*.py`. The known site at `runner.py:202` (`"claude", "-p", prompt, ...`) was found. Control passes.

### All spawn sites

| # | File:Line | Command | Context | Needs marker? |
|---|-----------|---------|---------|---------------|
| 1 | `runner.py:201-208` | `["claude", "-p", prompt, "--output-format", "stream-json", "--verbose", "--model", model, "--allowedTools", allowed_tools, "--append-system-prompt", BELLOWS_AGENT_SYSTEM_PROMPT]` | Main step execution. `subprocess.Popen(..., cwd=project_path)` at line 218-223. No `env=` parameter. | **YES** — this is the primary channel. Every plan step runs through this. |
| 2 | `bellows.py:1995-2000` | `["claude", "-p", "reply OK", "--output-format", "text"]` | Auth preflight probe at daemon startup. `subprocess.run(...)`, no `cwd=`, no `env=`. Short-lived (15s timeout). | **YES** — this spawns a `claude -p` session that triggers SessionStart (debt injection). It's a probe, not a plan step, so the injection is pure noise. |
| 3 | `planner.py:129-131` | `["claude", "-p", prompt, "--output-format", "json", "--model", model, "--allowedTools", "Read"]` | Planner consultation. `subprocess.run(..., cwd="/tmp", ...)`. No `env=`. | **YES** — same channel-1 exposure. cwd is `/tmp`, so it won't interact with project hooks, but the USER-scope wrap hooks still fire. |

**Conclusion:** Three spawn sites, not one. All three are `subprocess.Popen`/`subprocess.run` calls that inherit the daemon's environment and receive no `env=` override. All three need the `BELLOWS_DISPATCH` marker.

---

## Q5 — Exemption Predicate Design

### The predicate

Check `os.environ.get("BELLOWS_DISPATCH")` in the hooks. If truthy, skip enforcement.

### Setter: `env=` on the spawn, NOT `os.environ.setdefault`

**The leak path of `setdefault`:** `os.environ.setdefault("BELLOWS_DISPATCH", "1")` at module import (the `DISABLE_AUTOUPDATER` pattern) marks the daemon's OWN process environment. Every descendant inherits it — including an interactive `claude` the CEO might launch from the same shell, from `dashboard.py`'s terminal pane, or from any subprocess of the daemon process tree. That interactive session would then be treated as daemon-dispatched and would silently lose the wrap lock.

**The `env=` approach scopes the marker to spawned sessions only:**

```python
# In runner.py, bellows.py, planner.py — at each Popen/run call:
env = {**os.environ, "BELLOWS_DISPATCH": "1"}
proc = subprocess.Popen(cmd, ..., env=env)
```

This sets `BELLOWS_DISPATCH` only on the child process. The daemon's own environment stays clean — an interactive `claude` launched from the same process tree does NOT inherit the marker.

### Failure directions

| Direction | Scenario | Consequence | Acceptable? |
|-----------|----------|-------------|-------------|
| **False negative** (daemon not detected) | `BELLOWS_DISPATCH` not set on a spawn | Degrades to today's behavior: hooks fire, worker gets debt-injected and possibly Stop-blocked | YES — this is the current state, not a new failure |
| **False positive** (interactive treated as daemon) | An interactive session inherits `BELLOWS_DISPATCH` | The CEO's wrap lock is silently disabled — the Stop hook allows without checking, the SessionStart hook stays silent about debt | **NO — this is worse than the defect** |

The `env=` approach prevents the false-positive direction by construction: the marker never enters the daemon's own environment.

### Edit set

**Site 1 — `runner.py:218-223`** (step execution):
```python
# Before:
proc = subprocess.Popen(cmd, stdout=..., stderr=..., text=True, cwd=project_path)
# After:
_daemon_env = {**os.environ, "BELLOWS_DISPATCH": "1"}
proc = subprocess.Popen(cmd, stdout=..., stderr=..., text=True, cwd=project_path, env=_daemon_env)
```

**Site 2 — `bellows.py:1995-2000`** (auth preflight):
```python
# Before:
result = subprocess.run(["claude", "-p", "reply OK", ...], capture_output=True, text=True, timeout=15)
# After:
_daemon_env = {**os.environ, "BELLOWS_DISPATCH": "1"}
result = subprocess.run(["claude", "-p", "reply OK", ...], capture_output=True, text=True, timeout=15, env=_daemon_env)
```

**Site 3 — `planner.py:129-131`** (planner consultation):
```python
# Before:
result = subprocess.run(["claude", "-p", prompt, ...], cwd="/tmp", capture_output=True, text=True, timeout=120)
# After:
_daemon_env = {**os.environ, "BELLOWS_DISPATCH": "1"}
result = subprocess.run(["claude", "-p", prompt, ...], cwd="/tmp", capture_output=True, text=True, timeout=120, env=_daemon_env)
```

**Site 4 — `~/.claude/eluvian/wrap_debt_hook.py:50-75`** (SessionStart hook):
```python
def main():
    try:
        sys.stdin.read()
    except Exception:
        pass
    # NEW: daemon exemption
    if os.environ.get("BELLOWS_DISPATCH"):
        hooklog("SessionStart", "daemon-exempt")
        emit(None)
    # ... rest unchanged
```

**Site 5 — `~/.claude/eluvian/wrap_stop_hook.py:51-91`** (Stop hook):
```python
def main():
    try:
        sys.stdin.read()
    except Exception:
        pass
    # NEW: daemon exemption (before sentinel check)
    if os.environ.get("BELLOWS_DISPATCH"):
        hooklog("Stop", "daemon-exempt")
        allow()
    if not SENTINEL.exists():
        # ... rest unchanged
```

**Site 6 — `wrap_arm_hook.py`:** NO edit needed. The daemon's prompts never match the trigger regex, so this hook never arms in a daemon session. Adding an exemption would be defensive but functionally redundant.

**Site 7 — `~/.claude/eluvian/wrap_stop_hook.py:26`** (sentinel path override for canary — see Q8):
```python
# Before:
SENTINEL = ROOT / ".wrap-in-progress"
# After:
SENTINEL = Path(os.environ.get("WRAP_SENTINEL_PATH", str(ROOT / ".wrap-in-progress")))
```

### Channel coverage

The exemption covers BOTH channels:
- **Channel 1 (SessionStart injection):** The debt hook checks `BELLOWS_DISPATCH` and stays silent.
- **Channel 2 (Stop-lock capture):** The stop hook checks `BELLOWS_DISPATCH` and allows unconditionally.

**What is LOST by exempting each:**
- Channel 1: Daemon workers no longer see wrap-debt warnings. They were never the right audience — the CEO resolves wrap debt.
- Channel 2: Daemon workers can never be held by the wrap lock. This means a daemon step can end while a wrap is armed — which is the correct behavior (the daemon's step scope is unrelated to the CEO's wrap ritual).

---

## Q6 — Interaction with the Per-Session Sentinel Fix

The per-session sentinel fix (recorded in [[wrap-completion-lock]]) would scope `wrap_check` to the wrapping session's own commits and consider a per-session sentinel, so session A's wrap cannot be disarmed by session B passing the check.

**Relationship:** The daemon exemption and the per-session sentinel are **orthogonal**.

- The daemon exemption prevents daemon workers from ever ENTERING the hook logic — they never reach `wrap_check`, never reach `SENTINEL.unlink()`, never see the block.
- The per-session sentinel prevents one INTERACTIVE session from disarming another INTERACTIVE session's wrap.

**Does shipping the exemption alone close the "daemon worker disarmed CEO's wrap" path?**

YES. With the exemption, the daemon worker's Stop hook hits the `BELLOWS_DISPATCH` check and calls `allow()` before reaching the sentinel check (`wrap_stop_hook.py:58`). It never runs `wrap_check.py`, never reaches the `returncode == 0` branch at line 76-81, and never calls `SENTINEL.unlink()`. The disarm path (`wrap_stop_hook.py:78`) is structurally unreachable from a daemon session.

**Shipping order recommendation:** Ship the daemon exemption FIRST. It is simpler (env var + guard clause), urgent (actively causing harm — the census shows 11 affected steps in <48 hours), and independently sufficient to close the daemon-disarm path. The per-session sentinel is a separate, harder fix (requires rethinking what `wrap_check` evaluates) that closes a different path (interactive-session-A disarms interactive-session-B) — ship it second, in its own plan.

**One executable or two:** TWO. The daemon exemption edits `runner.py`, `bellows.py`, `planner.py` (versioned, in bellows/) and `wrap_debt_hook.py`, `wrap_stop_hook.py` (unversioned, in `~/.claude/eluvian/`). The per-session sentinel edits `wrap_check.py`, `wrap_stop_hook.py`, and possibly `wrap_arm_hook.py` — different files, different design work, different test matrix.

---

## Q7 — The Versioning Gap

### Confirmation

`git rev-parse --show-toplevel` under `~/.claude/` → `fatal: not a git repository`. A `find /Users/marklehn/Developer/GitHub -maxdepth 4` for `wrap_check.py`, `wrap_stop_hook.py`, `wrap_debt_hook.py`, `wrap_arm_hook.py` → **no results**. The enforcement layer exists only at `~/.claude/eluvian/` with no git repository, no diff, and no revert path.

### Options

| Option | Mechanism | Canonical location | Diff/revert | Trade-offs |
|--------|-----------|-------------------|-------------|------------|
| **A: Vendor into bellows/** | Copy files to `bellows/hooks/eluvian/`, settings.json hook commands point to the vendored copy | `bellows/hooks/eluvian/` | YES — full git history | Settings.json still at `~/.claude/`, must reference the bellows path. Two things to keep in sync. Bellows already has the daemon code. |
| **B: Vendor into governance root** | Copy to `governance/hooks/`, settings point there | `governance/hooks/` | YES | Governance root is the enforcement layer's logical home (wrap is a governance ritual). But governance has no `.git` of its own — it IS the git root. |
| **C: Symlink from `~/.claude/eluvian/` to a repo** | `~/.claude/eluvian/*.py` are symlinks to `bellows/hooks/` or `governance/hooks/` | Repo dir | YES (if target is in a repo) | Fragile: symlinks break if repo moves; `settings.json` still at `~/.claude/`. |
| **D: Init a git repo under `~/.claude/`** | `git init ~/.claude/eluvian/` | `~/.claude/eluvian/` | YES | Isolated from the project structure. Easy to lose (no remote). Pollutes `~/.claude/` with git metadata. |
| **E: Leave in place, track via explicit CHANGELOG** | No move; maintain a CHANGELOG in governance | `~/.claude/eluvian/` (unchanged) | NO — still no diff/revert | Lowest friction but highest risk. |

### Recommendation

**Option A (vendor into bellows/)** is the strongest fit:
- Bellows already owns the daemon side of this fix (`runner.py`, `bellows.py`, `planner.py`).
- The executable needs to edit both sides atomically — having both in one repo makes the PR reviewable.
- The `settings.json` hook commands would change from `/Users/marklehn/.claude/eluvian/wrap_*.py` to `/Users/marklehn/Developer/GitHub/bellows/hooks/eluvian/wrap_*.py`.

**This is a CEO fork** — the options differ materially in where the canonical copy of the enforcement layer lives. Option A centralizes in bellows; Option B centralizes in governance. The choice affects which repo's PRs carry enforcement-layer changes, which CI pipeline gates them, and who reviews them.

### Q5 edit set restated for Option A (vendored in bellows/)

If the CEO chooses Option A, the Q5 edits to `wrap_debt_hook.py` and `wrap_stop_hook.py` target `bellows/hooks/eluvian/` instead of `~/.claude/eluvian/`. The `settings.json` hook commands must also be updated to point to the new paths. The executable must:
1. Copy `~/.claude/eluvian/*.py` to `bellows/hooks/eluvian/`
2. Apply the exemption edits to the bellows copies
3. Update `~/.claude/settings.json` to point to the bellows paths
4. Commit the bellows changes

If the CEO chooses to leave in place (Option E), the edits target `~/.claude/eluvian/` directly with no diff or revert.

---

## Q8 — Acceptance Canary Specification

### Testability constraint

`wrap_stop_hook.py:26` hardcodes `SENTINEL = ROOT / ".wrap-in-progress"`. There is no mechanism to use a scratch sentinel for testing. A canary that needs to arm-and-disarm the lock can only arm the ONE shared sentinel, which the MUST-PRESERVE block forbids and which would trap any concurrent interactive terminal.

**Resolution:** The fix must make the sentinel path overridable via environment variable (edit included in Q5's edit set as Site 7):
```python
SENTINEL = Path(os.environ.get("WRAP_SENTINEL_PATH", str(ROOT / ".wrap-in-progress")))
```

This allows the canary to arm a scratch sentinel at e.g. `/tmp/test-wrap-sentinel` without touching the shared one.

### Live canary specification

**Setup:**
1. Create a scratch sentinel: `touch /tmp/test-wrap-sentinel`
2. Set env vars for the test: `BELLOWS_DISPATCH=1` and `WRAP_SENTINEL_PATH=/tmp/test-wrap-sentinel`

**Assertion 1 — Daemon session takes the exempt branch:**
```
BELLOWS_DISPATCH=1 WRAP_SENTINEL_PATH=/tmp/test-wrap-sentinel \
  claude -p "reply OK" --output-format text --max-turns 1
```
Expected in `hooks.log`: `Stop daemon-exempt` (the new log token from the exemption guard).
Expected NOT in `hooks.log`: `armed-BLOCK` or `armed-pass-disarm`.
The scratch sentinel must still exist after the session (no `SENTINEL.unlink()` reached).

**Assertion 2 — Interactive session still gets blocked:**
```
WRAP_SENTINEL_PATH=/tmp/test-wrap-sentinel \
  claude -p "reply OK" --output-format text --max-turns 2
```
(No `BELLOWS_DISPATCH` set.)
Expected in `hooks.log`: `armed-BLOCK` (the stop hook sees the scratch sentinel, runs wrap_check, which fails, blocks).
The session will be held by the block; terminate after observing the first `armed-BLOCK` in hooks.log.

**Teardown:**
- `rm /tmp/test-wrap-sentinel`

### What a FAILING canary looks like

| Assertion | Failing signal | Meaning |
|-----------|----------------|---------|
| 1 | `hooks.log` shows `armed-BLOCK` or `armed-pass-disarm` instead of `daemon-exempt` | The exemption predicate didn't fire — `BELLOWS_DISPATCH` not reaching the hook, or the guard clause is wrong |
| 1 | Scratch sentinel deleted after session | The exempt branch was NOT taken; the hook reached `SENTINEL.unlink()` |
| 2 | `hooks.log` shows `unarmed-allow` instead of `armed-BLOCK` | The sentinel path override didn't work — the hook is reading the hardcoded path, which has no sentinel |
| 2 | `hooks.log` shows `daemon-exempt` | `BELLOWS_DISPATCH` is leaking into the interactive session — the `env=` scoping failed |

### Canary ownership

The daemon-exempt half (Assertion 1) is fully automatable — it can run in CI or as a post-deploy check. The interactive-block half (Assertion 2) requires manually terminating the blocked session; it could be automated with a timeout but the key observation is the `armed-BLOCK` token in hooks.log, which can be asserted by a watcher script.

---

## What could not be measured

| Question | Part | Status | What blocked measurement | What would unblock |
|----------|------|--------|--------------------------|-------------------|
| Q2 | hooks.log session attribution | INFERRED | `hooks.log` carries no session ID; attributing `armed-BLOCK` entries to exec-493 vs. the CEO's concurrent interactive session relies on a timestamp join across two data sources (lifecycle.db step times in local/UTC and hooks.log in local time) | Adding `session_id` to hooks.log output |
| Q2 | Exact block count for exec-493 | INFERRED | The step log shows 2 `[wrap-lock]` block tokens, but hooks.log shows 12 `armed-BLOCK` entries in the same time window. Without session IDs, the true per-session count is ambiguous (the CEO's session was likely contributing to the hooks.log count) | Session ID in hooks.log |
| Q2 | exec-493 three-push attribution to wrap debt | INFERRED | The three pushes are in the step's NDJSON stream and are clearly outside the plan's project scope, but the causal chain (debt injection → worker resolves wrap → pushes repos) is inferred from the sequence, not from an explicit "I am resolving wrap debt" marker in the output | N/A — the causal chain is self-evident from the transcript |

All Q1, Q3, Q4, Q5, Q6, Q7, Q8 answers rest on MEASUREMENT or structural analysis of source code, not inference.

---

## Open Forks

### Fork 1 — Canonical location of the enforcement layer (Q7)

**Decision:** Where should the canonical copy of `wrap_check.py`, `wrap_debt_hook.py`, `wrap_stop_hook.py`, `wrap_arm_hook.py`, and `commands/wrap.md` live?

**Options:**
- **A: `bellows/hooks/eluvian/`** — co-located with the daemon code, full git history, reviewable PRs. Recommended.
- **B: `governance/hooks/`** — governance is the logical owner of the wrap ritual.
- **E: Leave at `~/.claude/eluvian/`** — no change, no diff/revert.

**Recommendation:** Option A. The enforcement layer's most urgent consumer is the daemon exemption (this fix), and bellows already owns the daemon side.

**Impact:** If the CEO chooses A or B, the executable must first vendor the files, then apply edits. If E, edits are applied in-place with no version control. The edit set in Q5 above is stated for both scenarios.

---

## Recommended Executable Scope

**Tier:** T2 — triggers: T-6 (governance/enforcement surface — the wrap hooks ARE the enforcement layer, and this edits them) + T-5 (not cleanly revertible — edits to `~/.claude/eluvian/` have no git revert unless vendoring is done first).

**Scope of the downstream executable:**
1. Apply `BELLOWS_DISPATCH=1` via `env=` at all three spawn sites (`runner.py:218`, `bellows.py:1995`, `planner.py:129`)
2. Add daemon-exemption guard to `wrap_debt_hook.py` and `wrap_stop_hook.py`
3. Make sentinel path overridable in `wrap_stop_hook.py` (for canary testability)
4. If vendoring (Fork 1): copy enforcement layer to repo, update `settings.json` hook paths
5. Run the acceptance canary (both assertions)
6. Commit all changes

**What it does NOT include:**
- Per-session sentinel fix (Q6 — separate plan, different design surface)
- Any changes to `wrap_arm_hook.py` (not needed — daemon prompts don't trigger it)
- Any changes to `wrap_check.py` (not needed for the exemption; needed later for per-session sentinel)
