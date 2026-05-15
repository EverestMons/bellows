# Bellows — bellows-self Concurrent-Activity Exposure: Disposition Diagnostic
**Date:** 2026-05-12 | **Tier:** Diagnostic | **Test Scope:** n/a (investigation) | **Execution:** Step 1 (SA) | **pause_for_verdict:** after_step_1

## How to Run This Plan

Paste the bootstrap prompt into Claude Code. The agent reads the full plan file and executes Step 1 ONLY. After completing Step 1, the agent STOPS and waits for CEO confirmation ("ok") before the Planner advances to closeout. The agent must never skip steps, auto-chain, or move the plan to Done — the Planner performs Rule 22 verification and the Done/ move.

## CEO Context

The Bellows BACKLOG has one open item: the 2026-05-05 `bellows-self parallel/concurrent activity exposure` entry, captured as a known constraint / accepted tradeoff after the 2026-05-04 monorepo detect-and-skip close (commit `06aa938`). The deferred fix path is option (b) — governance-root-worktree with subdirectory cwd, estimated 50–80 LOC, flagged as potentially confusing to agents expecting absolute paths.

A week has passed since the entry was authored. The cost estimate, reproduction count, and risk surface assessment are stale. Before deciding whether to ship option (b), close as won't-fix, or pick a different option, the Planner needs a current re-evaluation.

This diagnostic answers four questions. The SA's recommendation comes back to the Planner; the Planner brings the recommendation to the CEO and the disposition is decided then.

Test Scope: n/a — investigation only. No code change, no test execution.

---
---

## STEP 1 — SA

---

> **FIRST — before doing anything else, claim this plan:** `import shutil; shutil.move("/Users/marklehn/Desktop/GitHub/bellows/knowledge/decisions/diagnostic-bellows-self-exposure-disposition-2026-05-12.md", "/Users/marklehn/Desktop/GitHub/bellows/knowledge/decisions/in-progress-diagnostic-bellows-self-exposure-disposition-2026-05-12.md")`.
>
> You are the Bellows Systems Analyst. Read your specialist file at `bellows/agents/BELLOWS_SYSTEMS_ANALYST.md` first. Skip the domain glossary — Bellows has no glossary and this is an architecture/audit task. **Investigate four questions and deposit findings. Do not propose plans, do not fix anything, do not modify any source.** **Q1 — Has the bellows-self exposure recurred since 2026-05-05?** Enumerate every scope_check failure in `bellows/verdicts/resolved/` and `bellows/ledger.jsonl` with timestamp between 2026-05-05 and today. For each, classify as (a) bellows-self exposure (project_path is the bellows/ directory or governance root, scope_check tripped on files the agent demonstrably did not touch), (b) real-`.git` post-fix gap (project_path is a project with its own `.git`, post-2026-05-03 worktree fix shipped), or (c) other class — name the class. Report counts per class and a one-line summary of each (a) and (c) entry. If counts are zero, say so explicitly. Cross-reference against `bellows/knowledge/research/backlog-1-reproduction-audit-2026-05-05.md` so the new audit is comparable to the prior one. **Q2 — Re-validate the option (b) LOC and risk estimate.** Read `bellows/bellows.py` `_create_worktree` and `_teardown_worktree` and every call site for both, plus the `cwd=` argument threading through `runner.py` and any subprocess invocations that pass project paths to agent commands. Produce: (i) an updated LOC delta estimate for option (b) — governance-root-worktree creation with subdirectory cwd — broken down by function with current line numbers; (ii) an enumeration of every subprocess.run / Popen call that takes a `cwd=` argument or that constructs an absolute path from project_path, with a one-line risk note per call site stating whether subdirectory cwd would break it, work transparently, or require a separate fix; (iii) any new risk surface that did not exist on 2026-05-05 — code shipped in the past week that adds new project_path / cwd dependencies. **Q3 — Are the alternative fixes from the original BACKLOG #1 entry cheaper now?** The original entry enumerated three fix candidates: option (a) per-plan git worktree (shipped 2026-05-03 with monorepo detect-and-skip 2026-05-04 — closes real-`.git` projects), option (b) governance-root-worktree with subdirectory cwd, option (c) process-filtered file-touch tracking, plus a fourth class — commit-message slug scoping. For each of (c) and commit-message slug scoping: (i) a one-paragraph description of how it would work mechanically against the current code, (ii) LOC delta estimate, (iii) the risk surface compared to option (b), (iv) whether anything has shifted in the past week (new abstractions, new helpers, new gate composition) that changes the comparison. **Q4 — Recommendation.** Given Q1–Q3, recommend one of: (i) close as won't-fix (formally accept the exposure as a permanent constraint, document the mitigations as standing workflow), (ii) ship option (b) — governance-root-worktree with subdirectory cwd, (iii) ship option (c) — process-filtered file-touch tracking, (iv) ship commit-message slug scoping, (v) defer further with a specific revisit trigger (state what condition would re-open this). Give a one-paragraph rationale. The recommendation goes to the Planner for verification and the CEO decides; you are not authorizing anything. Also include a "Layer Impact" section per your specialist output convention stating which of layers 1/2/3 are affected by your recommendation. Deposit findings to `/Users/marklehn/Desktop/GitHub/bellows/knowledge/architecture/bellows-self-exposure-disposition-2026-05-12.md`. **Deposits:** `- /Users/marklehn/Desktop/GitHub/bellows/knowledge/architecture/bellows-self-exposure-disposition-2026-05-12.md`. Standard prompt feedback protocol → `bellows/knowledge/research/agent-prompt-feedback.md`. Commit with message: `docs: SA findings — bellows-self exposure disposition diagnostic 2026-05-12`.
>
> **STOP. Do NOT proceed to any further step. Do NOT move the plan to Done. Wait for CEO confirmation before continuing.**

---
