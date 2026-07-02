# Bellows — `__file__`-Relative Root Resolution Audit (row 15, convert-with-proof)
**Date:** 2026-07-02 | **Tier:** Small | **Dispatch Mode:** bellows | **Test Scope:** targeted | **Execution:** Step 1 (SA) | **pause_for_verdict:** always

## CEO Context

FORWARD row 15 (added 2026-06-06, CEO-deferred with audit-first disposition): latent `BELLOWS_ROOT = Path(__file__).parent`-style root resolution. Row cites 3 instances (`bellows.py`, `planner.py`, `verdict.py`); the lessons-forge baton cites 4 (adds `runner.py:20`) — the counts disagree, so ENUMERATE from current code, do not trust either citation. The hazard: if any of these modules ever executes from a file physically located inside a `.bellows-worktrees/` copy, `__file__`-relative resolution points at the worktree, not the canonical bellows root — misrouting DB paths, logs, or verdict dirs. The CEO disposition is convert-with-proof of worktree-reachability, NOT blanket conversion: an instance only warrants converting if a real execution path can reach it from a worktree copy. This diagnostic is READ-ONLY — it produces per-instance proofs and dispositions; a follow-up executable performs any conversions.

## How to Run This Plan

Paste the bootstrap prompt into Claude Code. Single-step plan — the agent executes Step 1 and the daemon pauses for verdict at completion.

**Bootstrap prompt:**
```
Read the plan at bellows/knowledge/decisions/diagnostic-file-relative-roots-audit-2026-07-02.md. Execute Step 1. Do NOT move the plan to Done until Step 1 is fully complete.
```

---
---

## STEP 1 — SA

---

> **FIRST — before any reads or work: post a short visible message to chat (1-2 sentences) confirming you are starting this plan and stating your immediate next action.** Do NOT rename the plan file.
>
> You are the Bellows Systems Analyst. Read your specialist file at `bellows/agents/BELLOWS_SYSTEMS_ANALYST.md` first. Skip the domain glossary — this is a code-path reachability audit. All commands run from `/Users/marklehn/Developer/GitHub/bellows`. **READ-ONLY: no code changes, no commits except the deposit.**
>
> **Scope:**
> - `knowledge/research/file-relative-roots-audit-2026-07-02.md`
>
> **Task 1 — enumerate.** `grep -n "__file__" *.py scripts/*.py` — list EVERY `__file__`-derived path expression (root constants, sys.path inserts, log/db path builds). Record file:line and the expression verbatim. Reconcile against the two prior citations (row 15's three; the lessons-forge baton's four incl. runner.py:20) and note discrepancies — instances may have moved or been removed since 2026-06-06.
>
> **Task 2 — per-instance worktree-reachability proof.** For each instance answer with evidence: (a) is this module ever copied into a plan worktree (is it under the repo root that `_create_worktree` snapshots — i.e., IS bellows itself ever a watched target project whose worktrees include these .py files)? Cite how bellows-targeted plans run (worktrees under `bellows/.bellows-worktrees/` DO contain the .py files — confirm by inspecting `_create_worktree` and the .gitignore); (b) can the module EXECUTE from that copy — trace who imports/invokes it (daemon process imports from the canonical root; `claude -p` agent subprocesses run shell commands with cwd inside the worktree — could an agent's `python3 -c "import gates"` or a test run import the WORKTREE copy via cwd-relative import precedence? pytest runs inside worktrees do exactly this); (c) if it executes from the copy, which concrete paths misresolve (DB? logs? verdicts?) and what is the blast radius — worktree-local garbage (benign) vs cross-contamination of canonical state (dangerous).
>
> **Task 3 — disposition per instance.** One of: `convert` (reachable + dangerous — specify the exact replacement, e.g. env-var override with canonical-root fallback, or the marker-file walk-up the baton mentions), `keep-as-is` (unreachable or benign, with the proof), or `convert-opportunistically` (benign today but cheap insurance — state the cost). End with a summary table (instance | reachable? | blast radius | disposition) and, if any `convert` rows exist, a ready-to-author fix list for the follow-up executable.
>
> **Deposit:** `knowledge/research/file-relative-roots-audit-2026-07-02.md` — enumeration, per-instance proofs, summary table, follow-up fix list (or "none"), and an Output Receipt with status. Use the canonical Python file-write pattern — no heredoc. Commit the deposit: `git add knowledge/research/file-relative-roots-audit-2026-07-02.md && git commit -m "docs(bellows): __file__-relative roots audit — per-instance reachability proofs (row 15)"`. In `### Ledger Updates` include `#### Prompt Feedback` only (no Project Status — diagnostic).
>
> **Deposits:**
> - `bellows/knowledge/research/file-relative-roots-audit-2026-07-02.md`
>
> On full completion, move the plan file to `bellows/knowledge/decisions/Done/` as the absolute last operation.
