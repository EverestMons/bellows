# Bellows — Canary for Reliability Bugs 1-3
**Date:** 2026-04-24 | **Tier:** Small | **Test Scope:** targeted | **Execution:** Step 1 (DEV)

## How to Run This Plan

This canary verifies that commit `c7f69f3` reliability fixes are loaded in the running Bellows daemon. The plan deliberately uses lowercase `## Step 1` as its step header — under pre-fix code, `extract_total_steps` returns 0 and Bellows silently moves the plan to Done without dispatching. Under post-fix code, `re.IGNORECASE` counts the header correctly, the agent dispatches, a canary deposit file is written, and a verdict request is posted (disable-auto-close model).

Deposit this plan to `knowledge/decisions/` and wait. Bellows's watcher should pick it up automatically. Success signal: a canary deposit file appears at `bellows/knowledge/research/canary-bugs-1-3-2026-04-24.txt`. Failure signal: plan file silently lands in `decisions/Done/` with no agent dispatch and no canary file.

---
---

## Step 1 — BELLOWS DEVELOPER

---

> You are the Bellows Developer. Skip specialist file and glossary reads — this is a trivial canary deposit to verify reliability fixes are live.
>
> Write a single canary file at `bellows/knowledge/research/canary-bugs-1-3-2026-04-24.txt` containing one line: `canary dispatch confirmed 2026-04-24 commit c7f69f3`.
>
> Do NOT commit. Do NOT run tests. Do NOT update any other file. This is a pure dispatch-and-deposit canary — the goal is to prove the agent was dispatched at all.
>
> **Deposits:**
> - `bellows/knowledge/research/canary-bugs-1-3-2026-04-24.txt`
>
> **STOP. Planner handles terminal housekeeping after Rule 22 verification.**
