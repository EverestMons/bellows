# bellows — Phase 3b/3c DB Step-State-Resume Mechanism & Cost-Benefit Diagnostic
**Date:** 2026-05-01 | **Tier:** Small | **Test Scope:** targeted | **Execution:** Step 1 (SA)

## CEO Context

**Test Scope: targeted** — diagnostic only, no production code changes, no test execution. SA reads code, inspects `bellows.db`, characterizes the actual mechanism that triggered the phantom-resume bug observed during today's session-wrap v1 dispatch.

**The observation.** During today's session, the `executable-bellows-session-wrap-2026-05-01.md` plan (v1) dispatched and Bellows reported `DB resume — last completed step 2, resuming at 3`, followed by `⚠️ plan content changed since last step — shadow=0b32403e5789 current=c64d9688fd4e`, then `using cached plan content (2 steps)`. Step 3 then failed `deposit_exists` because Step 1 and Step 2 deliverables (session-wrap-dev-log-2026-05-01.md, PROJECT_STATUS edits, PLANNER_TEMPLATE lessons, BACKLOG entries) were never produced on disk. v1 was halted via verdict; v2 with a unique slug (`...-v2-...`) ran cleanly through 3 steps.

**The Planner's working hypothesis (NOT to be assumed correct).** A prior plan with the same slug `bellows-session-wrap-2026-05-01` left orphan DB step-state showing "step 2 complete." When v1 was deposited, Phase 3b's `_get_last_completed_step` queried by slug, found the orphan row, and triggered phantom resume at Step 3. Phase 3c's plan-hash drift warning fired (correctly) but is non-blocking, so resume happened anyway. **This hypothesis is plausible but unverified — confirm or refute against actual DB state and code paths.**

**The diagnostic answers six questions and ends with a fix-shape recommendation.** The recommendation must be evidence-driven (per the 2026-05-01 lesson on snapshot-fix selection-by-reasoning). Candidate fix shapes to evaluate include patches (key by slug+hash, clear DB on terminal), simplifications (make Phase 3c warning blocking), and removal (Phase 3b/3c may not be load-bearing if the manual-rename resume path it was built for is now unsupported per Rule 25 / verdict-only resume protocol).

## How to Run This Plan

Paste the bootstrap into Claude Code. Single-step diagnostic — Planner performs Rule 22 verification after the agent reports Complete.

**Bootstrap:**
```
Read the plan at bellows/knowledge/decisions/diagnostic-phase-3b-mechanism-and-cost-benefit-2026-05-01.md. Execute Step 1 ONLY. Single-step diagnostic — do NOT move the plan to Done. Stop and report Complete when findings are deposited.
```

---
---

## STEP 1 — BELLOWS SYSTEMS ANALYST

---

> **FIRST — before doing anything else, claim this plan:** `import shutil; shutil.move("bellows/knowledge/decisions/diagnostic-phase-3b-mechanism-and-cost-benefit-2026-05-01.md", "bellows/knowledge/decisions/in-progress-diagnostic-phase-3b-mechanism-and-cost-benefit-2026-05-01.md")`.
>
> You are the Bellows Systems Analyst. Skip specialist file and glossary reads — this is code-tracing, schema inspection, and historical-data characterization. Read the prior closure entries for Phase 3b (`bellows.py` `runs.plan_slug` column + `_get_last_completed_step` helper, shipped 2026-04-28) and Phase 3c (`runs.plan_hash` column + drift warning, shipped 2026-04-30) — search the BACKLOG.md "Closed" section for the verbatim closure text and capture it. Do NOT assume the closure description matches the actual implementation; verify against current code.
>
> **Investigate six questions and deposit findings.**
>
> **Q1 — Characterize the orphan DB state.** Open `bellows.db` (path: `bellows/bellows.db` or wherever the daemon writes it — check `bellows.py` for the canonical path constant). Run `sqlite3 bellows.db ".schema runs"` and capture the schema. Then run `sqlite3 bellows.db "SELECT * FROM runs WHERE plan_slug = 'bellows-session-wrap-2026-05-01';"` and dump every column for every matching row. For each row: the row's `plan_slug`, `step_number`, `plan_hash` (if column exists), `started_at`/`completed_at` (whatever timestamp columns exist), and any other fields. Compare timestamps against today's session timeline (the v1 wrap was deposited around 20:1X local, the prior orphan verdict-request `verdict-request-bellows-session-wrap-2026-05-01-step-2.md` had mtime 16:46:56). **The hypothesis is that one or more rows are from a plan deposited BEFORE 16:46 and never cleared.** Confirm or refute by inspecting timestamps. If the rows are all from this session's v1 plan, the hypothesis is wrong and the bug is something else.
>
> **Q2 — Trace `_get_last_completed_step` end-to-end.** Read `bellows.py`. Locate the `_get_last_completed_step` function (or whatever name Phase 3b uses) and capture its full body. Identify: what columns does the WHERE clause filter on? Is it `plan_slug` only, or `(plan_slug, plan_hash)`, or some other key? Then locate every call site of this function and the surrounding code that consumes its return value. Specifically: where does the "DB resume — last completed step N, resuming at N+1" log line originate? What conditional gates the resume? Map the full path from "Bellows sees executable-X.md" → "claim renames to in-progress-X.md" → "compute plan_hash from current file" → "query runs table" → "decide to resume vs start fresh." Report every decision point in this chain.
>
> **Q3 — Trace Phase 3c hash-drift handling.** Read the same code area. When the current plan_hash differs from the most recent runs row's plan_hash, what happens? Is the warning logged-only, or does it block resume? The observed behavior was "warning fires, resume proceeds" — confirm whether that's intentional or a bug. Report the exact conditional, the print/log statement, and the path-after-warning. Also: what is "shadow cache" here — is the `0b32403e5789` hash from `runs.plan_hash`, from the on-disk shadow file (`.bellows-cache/*.pristine`), or from somewhere else? Map the hash sources and confirm which one drove the warning.
>
> **Q4 — Map the full code-path from claim to dispatch.** Walk through what Bellows does when a `verdict-resolved/verdict-X-step-2.md continue` verdict is consumed AND a `decisions/in-progress-X.md` exists. Specifically: where in the lifecycle is `_get_last_completed_step` called? Is it called when claiming a fresh `executable-` file (the case the diagnostic is investigating), only on resume after pause, or both? If both, are there different code paths for fresh-claim vs resume-after-pause that converge on the same DB query? This question is critical because the v1 wrap was a FRESH deposit (no prior in-progress state), but Bellows treated it as a resume — so the DB query must be running on fresh claims, not just on pause-resume. Confirm and document the call-site pattern.
>
> **Q5 — Characterize DB orphan accumulation.** Run `sqlite3 bellows.db "SELECT plan_slug, MAX(step_number), COUNT(*), MAX(completed_at) FROM runs GROUP BY plan_slug;"` (adapt SQL to actual schema) to enumerate every distinct slug in `runs`. For each slug, check whether a corresponding plan file exists in any watched project's `decisions/` (active or Done/) — same cross-project search you did for the cleanup-verdicts diagnostic Q2. **Bucket the rows:** (a) slug has matching active-state plan (in-progress, verdict-pending), (b) slug has matching Done/ plan, (c) slug has matching halted- plan, (d) slug has NO matching plan anywhere — pure orphan. Count rows in each bucket. The bug class scales with bucket (d). Report total rows + bucket counts.
>
> **Q6 — Cost-benefit of Phase 3b/3c.** Now that the mechanism and orphan rate are characterized, evaluate whether Phase 3b/3c is load-bearing. Concrete questions:
>
> **(6a)** What was the original failure mode Phase 3b/3c was designed to prevent? Read the original closure entries (BACKLOG closed 2026-04-28 / 2026-04-30) and the shipping plans (`executable-step-state-resume-phase-3b-2026-04-28.md`, `executable-phase-3c-plan-hash-drift-warning-2026-04-30.md`) in `Done/`. Capture verbatim what they say about the failure mode being prevented.
>
> **(6b)** Is that failure mode still possible? Per Rule 25's "Resume Protocol — Verdict-Only" subsection, manual rename of `verdict-pending-*` → `executable-*` is documented as unsupported. The supported resume path is verdict-based (deposit a continue verdict in `resolved/`). If the manual-rename path is no longer used, Phase 3b/3c may be guarding against a path that no longer exists. Verify: in the last 30 days of `runs` rows, are there any rows whose corresponding plan went through a manual rename (vs verdict-based resume)? You can probably distinguish by inspecting the verdict-pending-* file mtimes vs runs-row started_at timestamps if the data supports it; if not, just note the inability to distinguish and move on.
>
> **(6c)** What's the bug rate of Phase 3b/3c? Today's session produced one phantom-resume bug. Are there other observable failures? Search ledger.jsonl, prior QA reports in `bellows/knowledge/qa/`, and recent session wraps for any mention of "DB resume" producing wrong behavior. Also check whether v2 of the wrap (which I shipped successfully) accidentally consumed the orphan DB row, or whether the row is still there.
>
> **(6d)** Three candidate fix shapes — evaluate each against the evidence:
>
> **(F1) Patch:** Key DB step-state by `(slug, plan_hash)` instead of slug alone. Different plans with the same slug can never collide. Estimated LOC: 5-15 (column already exists per Phase 3c). Side effect: legitimate same-plan edits resume cleanly only if the hash is recomputed pre-claim. Risk: hash sensitivity to whitespace or trivial edits could prevent legitimate resume.
>
> **(F2) Simplify:** Make Phase 3c hash-drift warning BLOCKING — if hash mismatch, refuse to resume and start fresh. Estimated LOC: 2-5. Side effect: legitimate edits between sessions force fresh start. Pro: simpler than F1; con: forces re-execution of completed steps when plan content drifts.
>
> **(F3) Remove:** Revert Phase 3b/3c entirely. Estimated LOC: ~30 (remove function, column, callers). Acceptable IF (6b) shows the manual-rename path is no longer used AND (6a) shows that's the only failure mode Phase 3b/3c was designed to prevent. Side effect: a failure mode that's now structurally prevented by Rule 25 instead of code.
>
> **(F4) Other:** if the evidence in Q1–Q5 reveals a different mechanism than the slug-collision hypothesis, propose the appropriate fix shape from the evidence.
>
> Recommend ONE fix shape; explain the tradeoffs. The recommendation feeds the executable plan that follows. Do NOT write code.
>
> **Deposit findings** to `bellows/knowledge/research/phase-3b-mechanism-and-cost-benefit-2026-05-01.md` using the canonical Python file write pattern: `with open("/Users/marklehn/Desktop/GitHub/bellows/knowledge/research/phase-3b-mechanism-and-cost-benefit-2026-05-01.md", "w") as f: f.write(content)` where `content` is the findings as a triple-quoted string defined before the open call. The file should contain six sections matching Q1–Q6, each with verbatim evidence (SQL output, code snippets, log lines) and reasoning. Q5's bucket table and Q1's full row dump are load-bearing for the executable that follows.
>
> **Standard prompt feedback protocol** → `bellows/knowledge/research/agent-prompt-feedback.md`.
>
> **Commit** with: `cd /Users/marklehn/Desktop/GitHub && git add bellows/knowledge/research/phase-3b-mechanism-and-cost-benefit-2026-05-01.md bellows/knowledge/research/agent-prompt-feedback.md && git commit -m "diag: Phase 3b/3c mechanism + cost-benefit findings"`.
>
> **Deposits:**
> - `bellows/knowledge/research/phase-3b-mechanism-and-cost-benefit-2026-05-01.md`
> - `bellows/knowledge/research/agent-prompt-feedback.md`
