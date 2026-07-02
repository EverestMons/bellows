# Bellows — Daemon Startup Auth Preflight (Manual Fix)
**Date:** 2026-07-01 | **Tier:** Small | **Dispatch Mode:** manual_bootstrap | **Test Scope:** targeted | **Execution:** manual run (NOT Bellows-dispatched)

## Why manual, not Bellows-dispatched

This edits `bellows.py`'s own startup path. A running daemon dispatching this plan would be editing the code that governs its own launch, and the fix's core behavior — "refuse to start on bad auth" — cannot be validated by the already-running daemon (it started under working auth). Parser-self-trip class: same handling as the diagnostic-6 coverage fix. Run this manually in Claude Code auto mode against a clean main; validate by unit test, not by live dispatch.

## Precondition

Clean main (`git status --porcelain` empty). If dirty, commit lifecycle artifacts first.

---

## Bootstrap prompt

```
Read and execute the plan at knowledge/development/manual-fix-daemon-auth-preflight-2026-07-01.md in full. Run in auto mode as a single manual session (NOT Bellows-dispatched). Confirm clean main first. Make the code change, add the unit tests, run the full suite to an explicit pass/fail and read the tail, then commit. Report the receipt.
```

---

## The fix

**Problem (evidence: plan 107, 5 halted dispatches).** The daemon has no auth precondition check before it begins claiming plans. If the launch shell lacks working `claude -p` auth, the daemon starts, claims a plan, spawns a child that inherits the unauthenticated context, and the step 401s at ~4s. The plan is burned. Existing `time.sleep` pauses (stagger at ~line 1669, "auth settle" at ~line 1999) assume auth works; nothing verifies it.

**Fix.** Add a one-shot auth preflight probe at daemon startup, immediately after the existing `time.sleep(3)` "auth settle" pause (~line 1999 in `bellows.py`) and BEFORE the startup plan scan. Behavior:

- Run a minimal `claude -p` probe: `claude -p "reply OK" --output-format text` (or the project's canonical minimal invocation — match how `runner.py` builds the CLI call so the probe uses the same auth path the real dispatch uses).
- Timeout the probe (~15s) so a hang doesn't wedge startup.
- On success (exit 0, non-error output): log `INFO` "auth preflight OK — apiKeySource confirmed" and proceed to the startup scan unchanged.
- On failure (non-zero exit, 401, timeout, or error output): log `ERROR` with the specific, actionable message — name the failure, and instruct the operator to run `claude -p "reply OK" --output-format text` in the launch shell to confirm, then `export ANTHROPIC_API_KEY=...` (or re-auth) and relaunch. Then **exit the process without entering the watch loop and without scanning/claiming any plan** (`sys.exit(1)` or equivalent clean shutdown of the already-started response_server/observer).

**Scope constraints.**
- Do NOT change the dispatch path, `runner.py` invocation, or any gate. This is a startup guard only.
- Do NOT probe per-plan or per-step (that is shape (b), explicitly out of scope — the evidence is a startup-state failure, not mid-session auth drop).
- The probe must use the SAME auth mechanism as real dispatch. If `runner.py` sets `DISABLE_AUTOUPDATER` or other env before invoking `claude`, the probe replicates that env so it tests the real path.
- Make the probe suppressible via an env flag (e.g. `BELLOWS_SKIP_AUTH_PREFLIGHT=1`) with `setdefault`-style respect for explicit override, so a developer running the daemon in a test harness without auth can bypass it. Default is ON (probe runs).

## Tests (targeted)

Add unit tests in the appropriate existing test file (`tests/test_bellows.py` or wherever startup is tested):

1. Probe success path: mock the `claude -p` subprocess to return exit 0 / OK → startup proceeds (does not exit).
2. Probe failure path: mock subprocess to return non-zero / 401 → daemon calls `sys.exit(1)` (assert `SystemExit` raised) and does NOT reach the plan scan.
3. Probe timeout path: mock subprocess to raise `TimeoutExpired` → treated as failure, exit.
4. Skip flag: `BELLOWS_SKIP_AUTH_PREFLIGHT=1` set → probe not invoked, startup proceeds.

Run the FULL suite with `timeout 600 pytest tests/` to an explicit pass/fail. Read the tail. Commit with a descriptive message referencing plan-107 evidence.

## Post-run (operator)

Daemon restart required to load the guard (no hot reload). After restart, the preflight runs on every launch — a launch shell with broken auth will now refuse to start with an actionable message instead of burning a plan.

**Deposits:**
- `bellows.py` (startup auth preflight)
- `tests/test_bellows.py` (4 preflight unit tests)
