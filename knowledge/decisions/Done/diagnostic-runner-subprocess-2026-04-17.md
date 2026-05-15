# Diagnostic — Bellows Runner Subprocess Management
**Date:** 2026-04-17 | **Type:** Diagnostic | **Priority:** 3 | **Status:** ✅ Complete

## Purpose

Before writing an activity-based timeout fix, need to understand how `runner.py` manages the `claude -p` subprocess. Specifically: how it captures stdout, whether it uses `subprocess.run` (blocking) or `Popen` (streaming), and what hooks exist for monitoring output in real-time.

---

## STEP 1 — Bellows Developer

---

> **FIRST — claim this plan:** `import shutil; shutil.move("bellows/knowledge/decisions/diagnostic-runner-subprocess-2026-04-17.md", "bellows/knowledge/decisions/in-progress-diagnostic-runner-subprocess-2026-04-17.md")`. Read `bellows/runner.py` in full. **3 questions, 5 minutes max.**
>
> **Q1 — Subprocess launch pattern.** Does `run_step` use `subprocess.run` (blocking, waits for completion) or `subprocess.Popen` (non-blocking, can monitor)? What are the exact arguments (stdout, stderr, timeout, etc.)? Paste the subprocess call verbatim.
>
> **Q2 — Output capture.** How is the agent's stdout captured? Is it captured all-at-once after completion, or streamed line-by-line? Is there any existing mechanism to read partial output before the subprocess finishes?
>
> **Q3 — Timeout mechanism.** How does the current timeout work? Is it `subprocess.run(timeout=N)` which raises `TimeoutExpired`, or a manual timer? What happens to the subprocess when it times out — is it killed, or does it keep running?
>
> **Deposit findings** to `bellows/knowledge/research/runner-subprocess-2026-04-17.md` using `with open("/Users/marklehn/Desktop/GitHub/bellows/knowledge/research/runner-subprocess-2026-04-17.md", "w") as f: f.write(content)`. Commit: `"docs: diagnostic — runner subprocess management"`. Standard prompt feedback protocol.
>
> **STOP. Do NOT proceed further. Wait for CEO confirmation.**
