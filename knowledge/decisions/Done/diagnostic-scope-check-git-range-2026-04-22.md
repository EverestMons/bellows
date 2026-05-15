# bellows — scope_check git-range mechanism diagnostic
**Date:** 2026-04-22 | **Tier:** Small | **Test Scope:** targeted | **Execution:** Step 1 (SA)

## How to Run This Plan

Paste the bootstrap prompt into Claude Code. The agent reads the full plan file and executes Step 1 ONLY. This is a single-step diagnostic (Rule 22 v4.19) — the agent investigates, deposits findings, reports completion. The Planner performs Rule 22 verification on the deposited findings file and handles housekeeping directly.

**Bootstrap prompt:**
```
Read the plan at bellows/knowledge/decisions/diagnostic-scope-check-git-range-2026-04-22.md. Execute Step 1 ONLY. After completing Step 1, STOP and wait for my confirmation. Do NOT move the plan to Done.
```

---
---

## STEP 1 — Bellows Systems Analyst

---

> **FIRST — before doing anything else, claim this plan:** `import shutil; shutil.move("bellows/knowledge/decisions/diagnostic-scope-check-git-range-2026-04-22.md", "bellows/knowledge/decisions/in-progress-diagnostic-scope-check-git-range-2026-04-22.md")`. You are the Bellows Systems Analyst. Read your specialist file at `bellows/agents/BELLOWS_SYSTEMS_ANALYST.md` first. Skip domain glossary — this is a code-tracing task. **Investigation goal:** map the exact mechanism by which Bellows's `scope_check` gate determines which files are "in scope" for a plan and flags files as out-of-scope. Do NOT propose fixes; report what exists. **Investigation scope:** (a) Locate `scope_check` in the Bellows codebase — it is expected to live in `gates.py` but confirm. Report the file path, function name, and line range. (b) Read the gate implementation in full. Document verbatim: what git command(s) it issues (exact argv or subprocess call), what range spec it passes to git (e.g., `HEAD~N..HEAD`, `--since=<timestamp>`, a specific base SHA, etc.), how it determines the base ref, how it determines the head ref, and how it decides the set of "plan-owned" files to compare against the diff output. (c) Trace where the gate is called from — which callsite invokes `scope_check`, what arguments are passed (plan path, step number, any claim-time metadata), and where the claim-time state (if any) is stored. If the gate uses plan metadata (claim timestamp, initial commit SHA, dispatch-time commit count), document where that metadata is persisted and read from. (d) Identify the "plan-owned files" determination logic. Does the gate compare against a declared scope field in the plan header? Does it derive scope from the agent's actual commits during execution? Does it use some other heuristic? Quote the code that makes this determination. (e) Light incident validation: `git log --oneline --pretty=format:"%h %s" -n 10 bellows/LESSONS.md bellows/knowledge/BACKLOG.md` — confirm the two files flagged by scope_check on `plan-mutation-source-2026-04-19` were last modified by commits made BEFORE 2026-04-19, not during that plan's execution. Report the commit SHAs and dates of the last modifications to those two files. No need to reconstruct the full plan-claim window or enumerate every commit scope_check saw — one-line confirmation that the flagged files were out-of-plan is sufficient. (f) Map the hot/cold paths: is there a cached version of scope_check anywhere (shadow cache, in-memory state), or is it always computed fresh from disk? Document any caching. **Deposit findings** to `bellows/knowledge/research/scope-check-git-range-2026-04-22.md` using the canonical Python file-write pattern: define the findings as a triple-quoted string variable, then `with open("bellows/knowledge/research/scope-check-git-range-2026-04-22.md", "w") as f: f.write(content)`. Structure the findings file with sections: **Mechanism Summary** (2-3 sentence TL;DR of what scope_check actually does), **Location** (file path, function name, line range), **Git Invocation** (verbatim subprocess/argv, quoted from source), **Range Computation** (how base and head refs are determined, with code quotes), **Plan-Owned Files Determination** (how the gate decides what files "belong" to the plan, with code quotes), **Call Sites** (where the gate is invoked, what arguments are passed), **Claim-Time Metadata** (what state is persisted at claim time, where it lives), **Caching** (any hot-path cache or persistent state), **Incident Validation** (one-line confirmation of LESSONS.md and BACKLOG.md commit dates), **Open Questions** (anything the investigation could not resolve — if any). End with an Output Receipt per PLANNER_TEMPLATE format. Standard prompt feedback protocol → `bellows/knowledge/research/agent-prompt-feedback.md`.
>
> **Deposits:**
> - `bellows/knowledge/research/scope-check-git-range-2026-04-22.md`
>
> **STOP. Wait for CEO confirmation before any further action.**
