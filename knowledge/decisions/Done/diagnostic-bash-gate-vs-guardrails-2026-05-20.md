# Diagnostic — Bash Gate vs GUARDRAILS.md `rm -f .git/index.lock` Contradiction

**Project:** bellows
**Dispatch Mode:** bellows
**Plan Type:** diagnostic
**Date:** 2026-05-20
**Source:** `shop_backlog.md` entry `guardrails-vs-bash-gate-contradiction-git-locks` (captured 2026-05-19, trigger: Plan A.7 Step 3 QA gate_failure)
**Specialist:** Bellows Systems Analyst

## Context

`governance/GUARDRAILS.md` lines 51–58 (Development section, "Git Operations (Mandatory)") prescribe `rm -f .git/index.lock .git/"index "*.lock .git/"index "[0-9]* 2>/dev/null` as the standard stale-lock recovery before every git command. Bellows' Bash gate denies all Bash calls writing to `.git/`, producing `gate_failure` on otherwise-clean agent runs (Plan A.7, 2026-05-21, third instance in this failure class). The backlog entry proposes two framings: **(a)** narrow the Bash gate to allow the specific guardrail-prescribed `rm -f .git/index.lock …` pattern, or **(b)** replace the guardrail's `rm -f` recovery with a method that doesn't touch `.git/`. The fix choice is binary; this diagnostic establishes the evidence needed to choose between them.

## Scope

Narrow: single documented contradiction (`rm -f .git/index.lock` ↔ Bash gate). Other potential GUARDRAILS-vs-gate collisions are NOT in scope. The Planner has declined to sweep the meta-pattern until a second collision surfaces.

## STEP 1

You are the Bellows Systems Analyst. Read your specialist file at `bellows/agents/BELLOWS_SYSTEMS_ANALYST.md` first. This is a read-only diagnostic — do NOT propose, author, or apply any fix. Investigate the contradiction between `governance/GUARDRAILS.md` (Development → Git Operations Mandatory section) and the Bellows Bash-tool gate that denies `.git/` writes. Answer the following questions concretely and produce findings in a Gap Assessment table per Rule 13: **Q1. Bash gate location and current logic.** Locate the code that denies Bash calls touching `.git/`. It is NOT in `bellows/gates.py` (those are post-step gates); it is a dispatch-time tool-permission scope. Search `bellows/*.py` for the `.git/` denial logic. Identify the file, the function, and the exact denial pattern (regex, substring match, etc.). Quote the relevant lines verbatim. **Q2. Frequency of historical fires.** Search `bellows/logs/`, `bellows/feedback.log`, and `bellows/.bellows-cache/` for prior instances of the bash-gate denying `.git/` writes. Enumerate: how many times has this gate fired against the GUARDRAILS-prescribed `rm -f .git/index.lock` pattern specifically? How many times has it fired against other `.git/` writes (which may be legitimate denials)? Report counts and dates. **Q3. Framing (b) recovery viability.** Evaluate `git gc --auto` and `git update-index --refresh` as replacements for `rm -f .git/index.lock`. Specifically: do either of these handle the failure mode the guardrail was authored to address (truly orphaned `.git/index.lock` left by a killed process — where the lock file exists but no process holds it)? Read `governance/GUARDRAILS.md` lines 51–58 verbatim and identify the exact recovery scenario the prescription handles. Then test (read-only — describe behavior from documentation, do not execute against a live repo) whether the proposed replacements address the same scenario. If neither replacement is functionally equivalent, framing (b) is non-viable and framing (a) becomes the only path. **Q4. Framing (a) gate-tightening conflict surface.** Check whether other in-flight bellows-side fix work touches the Bash gate or the broader gate infrastructure. Specifically read `shop_next_session.md` Thread 3 (bellows-side `_gate_deposit_exists` normalization fix) and confirm whether it modifies the same file/function the Bash gate lives in. If the Bash gate fix would touch the same module, identify the conflict and the recommended sequencing. **Output format:** Deposit findings to `bellows/knowledge/research/bash-gate-vs-guardrails-diagnostic-2026-05-20.md`. Findings MUST include a Gap Assessment table with columns `| Gap | Current State | Proposed State | Change Required |` covering each of the four questions, plus a recommendation section that names the recommended framing (a or b) with one-paragraph justification grounded in Q1–Q4 evidence. Standard prompt feedback protocol → `bellows/knowledge/research/agent-prompt-feedback.md`.

**Deposits:**
- `bellows/knowledge/research/bash-gate-vs-guardrails-diagnostic-2026-05-20.md`
- `bellows/knowledge/research/agent-prompt-feedback.md`
