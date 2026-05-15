# bellows — `_cleanup_verdicts_for_slug` Call-Site Gap Diagnostic (Re-run)
**Date:** 2026-05-01 | **Tier:** Small | **Test Scope:** targeted | **Execution:** Step 1 (SA)

## CEO Context

**Test Scope: targeted** — diagnostic only, no production code changes, no test execution. SA reads code, characterizes 51 archived verdict files, identifies the gap.

**Re-run note.** The first attempt (`diagnostic-cleanup-verdicts-call-site-gap-2026-05-01.md`, halted) was killed at 431s by the 300s inactivity timeout while the SA was reasoning between tool calls. That timeout was raised to 1800s via `executable-inactivity-timeout-bump-1800s-2026-05-01.md` (closed); the daemon has been restarted and the new threshold is live. This re-run is identical in scope.

The v9 BACKLOG entry (closed 2026-04-19 via `executable-verdict-lifecycle-coupling-2026-04-19.md`) shipped a `_cleanup_verdicts_for_slug` helper plus 4 terminal-state call sites + a one-time startup sweep. Despite that, today's session found 51 stranded `verdict-request-*` files in `bellows/verdicts/pending/` — files dated as recently as 2026-05-01, well after the v9 fix shipped. CEO archived all 51 to `bellows/verdicts/pending/archived/` (still on disk for inspection).

This diagnostic answers: **why didn't the v9 fix prevent today's accumulation, and what call site (or guard, or restart-discipline gap) is missing?** The diagnostic produces evidence; a follow-up executable will ship the fix.

## How to Run This Plan

Paste the bootstrap prompt into Claude Code. The agent reads the full plan file and executes Step 1 ONLY. After completing Step 1, the agent STOPS — this is a single-step diagnostic; the Planner performs Rule 22 verification and housekeeping after the agent reports Complete.

**Bootstrap:**
```
Read the plan at bellows/knowledge/decisions/diagnostic-cleanup-verdicts-call-site-gap-rerun-2026-05-01.md. Execute Step 1 ONLY. Single-step diagnostic — do NOT move the plan to Done. Stop and report Complete when findings are deposited.
```

---
---

## STEP 1 — BELLOWS SYSTEMS ANALYST

---

> **FIRST — before doing anything else, claim this plan:** `import shutil; shutil.move("bellows/knowledge/decisions/diagnostic-cleanup-verdicts-call-site-gap-rerun-2026-05-01.md", "bellows/knowledge/decisions/in-progress-diagnostic-cleanup-verdicts-call-site-gap-rerun-2026-05-01.md")`.
>
> You are the Bellows Systems Analyst. Skip specialist file and glossary reads — this is a code-tracing and evidence-characterization task. **Read the prior v9 diagnostic at `bellows/knowledge/research/verdict-lifecycle-coupling-2026-04-19.md`** — it enumerates the v9 design (3 terminal call sites + startup sweep, slug rules, race analysis). Your job is to identify why the v9 fix isn't holding.
>
> **Investigate four questions and deposit findings.**
>
> **Q1 — Verify the v9 code actually shipped and is current.** Open `bellows/bellows.py`. Confirm `_cleanup_verdicts_for_slug` function exists; capture its current signature and full body. Then locate every call site (use `grep -n _cleanup_verdicts_for_slug bellows/bellows.py`). For each call site report: line number, enclosing function, what plan-state transition it precedes, and whether the call is gated by any conditional. Compare the call-site set against the v9 diagnostic's recommended set (auto-close in `run_plan`, continue-to-done in `_consume_verdicts`, halt in `_consume_verdicts`, plus startup sweep). Report: matches, missing, extra, or drifted (e.g., call site exists but moved to a different function).
>
> **Q2 — Characterize the 51 archived files.** List every file at `bellows/verdicts/pending/archived/` (use `ls -la`). For each file extract: filename, mtime, slug (apply the same `_slug_from_path`-equivalent logic — strip `verdict-request-` prefix and `-step-N.md` suffix), step number. **Then for each unique slug, locate its corresponding plan file.** Search `bellows/knowledge/decisions/Done/`, `bellows/knowledge/decisions/halted-*`, and any active-state plan files (`in-progress-*`, `verdict-pending-*`, raw `executable-*`/`diagnostic-*`). Cross-project search if needed (CEO confirmed bellows is the only watched project hitting this — but verify). Produce a table: `| Verdict file | mtime | Slug | Step | Plan state (Done/halted/active/missing) | Plan path |`. Bucket the 51 files by plan-state outcome — this tells us which transition path the slug took (or didn't take).
>
> **Q3 — Identify the gap.** Cross-reference Q1 (call sites that exist) and Q2 (plan-state outcomes for stranded slugs). For each plan-state bucket in Q2 (Done, halted, missing, etc.), trace which `_cleanup_verdicts_for_slug` call site SHOULD have fired during that plan's lifecycle. Compute the gap: which transition path produced stranded files despite a call site allegedly covering it? Candidate hypotheses to evaluate against the evidence (do NOT pre-commit; let the data choose):
>
> **(H1)** v9 call sites fire BEFORE `shutil.move`, but the move silently fails or is skipped on some path (e.g., orphaned `in-progress-` plan that auto-closes via a path that bypasses the cleanup). Test by checking whether any stranded slugs correspond to plans whose mtime differs from typical close-paths.
>
> **(H2)** A 4th transition path exists that doesn't go through any of the 3 terminal sites. Candidates: stale-verdict consumption (verdict consumed when plan already in Done/, see `_consume_verdicts` line ~617's `plan_matched=False` path), or auto-close via the gate-pass-without-pause path (see `run_plan` lines 348–365 in v9, may have drifted).
>
> **(H3)** The startup sweep in `Bellows.start()` exists but doesn't cover the cases that produced these files (e.g., sweep only handles slugs matching Done/ files but not slugs that were never in Done/ in the first place, or sweep matches by slug-substring with prefix-collision).
>
> **(H4)** Bellows hasn't been restarted since the v9 fix shipped, so the running daemon executes pre-fix code. Test by checking `bellows/restart-log` (if it exists) or by inspecting the v9 fix commit date against last Bellows restart timestamp the CEO can confirm.
>
> **(H5)** None of the above — some other gap. Describe what you find.
>
> **Q4 — Propose minimal fix shape (do NOT implement).** Based on Q3's identified gap, propose the smallest fix shape that closes the bucket containing the most stranded files. The BACKLOG entry suggests two candidate shapes: (a) fire `_cleanup_verdicts_for_slug` on every successful verdict consumption regardless of transition type (i.e., from `_consume_verdicts` outer loop after the verdict-to-processed rename completes), or (b) add a 4th call site at the specific gap identified in Q3. Evaluate both against the Q3 findings: which one closes more stranded buckets, which has lower blast radius (fewer LOC, fewer existing tests affected), which is more defensible against future drift. Recommend ONE; explain the tradeoff. Do NOT write code — the recommendation feeds the executable plan that follows.
>
> **Deposit findings** to `bellows/knowledge/research/cleanup-verdicts-call-site-gap-2026-05-01.md` using the canonical Python file write pattern: `with open("/Users/marklehn/Desktop/GitHub/bellows/knowledge/research/cleanup-verdicts-call-site-gap-2026-05-01.md", "w") as f: f.write(content)` where `content` is the findings as a triple-quoted string defined before the open call. The file should contain four sections matching Q1–Q4, each with the evidence and reasoning for that question. Include the verbatim Q2 table — it's load-bearing for the executable that follows.
>
> **Standard prompt feedback protocol** → `bellows/knowledge/research/agent-prompt-feedback.md`.
>
> **Commit** with: `cd /Users/marklehn/Desktop/GitHub && git add bellows/knowledge/research/cleanup-verdicts-call-site-gap-2026-05-01.md bellows/knowledge/research/agent-prompt-feedback.md && git commit -m "diag: cleanup_verdicts call-site gap findings (BACKLOG #3)"`.
>
> **Deposits:**
> - `bellows/knowledge/research/cleanup-verdicts-call-site-gap-2026-05-01.md`
> - `bellows/knowledge/research/agent-prompt-feedback.md`
