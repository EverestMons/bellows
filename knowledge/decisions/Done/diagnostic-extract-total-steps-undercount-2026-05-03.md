# Bellows — extract_total_steps() Regex Undercount Diagnostic
**Date:** 2026-05-03 | **Tier:** Diagnostic | **Test Scope:** targeted | **Execution:** Step 1 (BELLOWS DEVELOPER)

## How to Run This Plan

Paste the bootstrap prompt into Claude Code. The agent reads the plan file and executes Step 1. After completing, the agent STOPS and waits for CEO confirmation. The Planner moves the plan to Done after Rule 22 verification passes.

**Bootstrap prompt:**
```
Read the plan at bellows/knowledge/decisions/diagnostic-extract-total-steps-undercount-2026-05-03.md. Execute Step 1. After completing, STOP and wait for my confirmation. Do NOT move the plan to Done.
```

**Background context (read before executing):** Twice today (2026-05-03), Bellows reported `plan has 1 steps` for plans that contained multiple `## STEP N — AGENT` headers. The two affected plans:

- `bellows/knowledge/decisions/Done/diagnostic-parallel-scope-check-collision-2026-05-03.md` — has `## STEP 1 — BELLOWS DEVELOPER` and `## STEP 2 — BELLOWS SYSTEMS ANALYST` (two step headers)
- `bellows/knowledge/decisions/Done/diagnostic-worktree-implementation-surface-2026-05-03.md` — has `## STEP 1`, `## STEP 2`, `## STEP 3` (three step headers)

Both were dispatched as 1-step plans by Bellows. The agent ran only Step 1 (in the second case; in the first case, the agent ran Steps 1 and 2 in one execution window, but Bellows still reported 1-step). The 2026-04-24 fix to `extract_total_steps()` was supposed to handle this — it added `re.IGNORECASE` and tightened the regex to `^##\s+step\s+\d+`. Despite that fix, the count is wrong on these plans. Suspected causes (from BACKLOG entry 2026-05-03): (a) interaction with `**Execution:** Step 1 (...) → Step 2 (...) → Step 3 (...)` line in metadata header, (b) em-dash separator (`## STEP 1 — BELLOWS DEVELOPER`) mismatch, (c) shadow cache vs. live file content divergence, (d) something else.

**This diagnostic identifies the cause only.** The fix is a separate executable plan after the cause is known.

---
---

## STEP 1 — BELLOWS DEVELOPER

---

> **STOP REMINDER (TOP):** This plan has ONE step. Complete it, then STOP and wait for CEO confirmation. Do NOT propose or implement a fix — that is a separate executable plan. Do NOT move the plan to Done — the Planner performs the terminal move after Rule 22 verification passes.
>
> **FIRST — before doing anything else, claim this plan:** `import shutil; shutil.move("bellows/knowledge/decisions/diagnostic-extract-total-steps-undercount-2026-05-03.md", "bellows/knowledge/decisions/in-progress-diagnostic-extract-total-steps-undercount-2026-05-03.md")`.
>
> You are the Bellows Developer. Read your specialist file at `bellows/agents/BELLOWS_DEVELOPER.md` first. Skip glossary read — this is regex tracing.
>
> **Task: identify the literal cause of `extract_total_steps()` undercounting on the two problematic plans from today.** Do NOT propose or implement a fix. The deliverable is a cause-of-undercount finding with literal evidence.
>
> **Phase 1 — Locate and read `extract_total_steps()`.** In `bellows/bellows.py`, find the `extract_total_steps()` function (or wherever step counting happens — it may be inline in `run_plan` rather than a named helper). Document the exact regex pattern, flags (re.IGNORECASE, re.MULTILINE, etc.), function signature, return type, and call site(s). Quote the literal source code with line numbers.
>
> **Phase 2 — Run the regex against the two failing plans.** In a Python REPL or via inline script (use `python3 -c "..."` with embedded triple quotes is BANNED per PLANNER_TEMPLATE Rule 5; use `with open() as f: f.write(...)` to a `/tmp/` script then run it):
>
> 1. Read the literal content of `bellows/knowledge/decisions/Done/diagnostic-parallel-scope-check-collision-2026-05-03.md`.
> 2. Run the exact regex from Phase 1 against that content with the exact flags. Print the count and every match (including line numbers within the file).
> 3. Repeat for `bellows/knowledge/decisions/Done/diagnostic-worktree-implementation-surface-2026-05-03.md`.
>
> Document the literal regex output for each file. Compare against the expected counts (2 for the first plan, 3 for the second).
>
> **Phase 3 — Run the regex against a known-passing multi-step plan.** Find a multi-step plan in `bellows/knowledge/decisions/Done/` that DID dispatch correctly (Bellows reported the right step count). Candidates from recent history: `executable-bellows-reliability-bugs-1-2-3-2026-04-24.md` (likely multi-step DEV+QA), `executable-disable-auto-close-2026-04-24.md`, `executable-deposits-block-regex-blank-line-2026-04-28.md`. Pick one or two, read their content, run the same regex, and document the count. This is the **control case** — what's different about plans that count correctly vs. plans that count wrong?
>
> **Phase 4 — Identify the cause.** Compare the matches and non-matches across the failing and passing plans. The cause is one of:
> - Header line interference: the `**Execution:** Step 1 (...) → Step 2 (...)` metadata line matches the regex when it shouldn't (false positives that confuse counting elsewhere)
> - Em-dash separator: `## STEP 1 — BELLOWS DEVELOPER` (em-dash, U+2014) doesn't match the regex if it expects `--` (hyphen-minus)
> - Regex anchor issue: `re.MULTILINE` flag missing or incorrectly applied, causing only the first occurrence to match
> - Shadow cache divergence: Bellows reads a different file than the live one (the `.bellows-cache/<slug>.pristine` shadow vs. the live `decisions/` file). If the shadow cache content is different from the live file, the regex runs against different content.
> - Something else (document literally)
>
> Identify the specific cause with literal evidence. Cite file content excerpts, regex match output, and line numbers. Do NOT guess — if the cause is ambiguous between two possibilities, document both with what would distinguish them.
>
> **Phase 5 — Cross-check the shadow cache.** Read `bellows/.bellows-cache/diagnostic-parallel-scope-check-collision-2026-05-03.pristine` (if it exists) and `bellows/.bellows-cache/diagnostic-worktree-implementation-surface-2026-05-03.pristine`. Compare against the live files in `Done/`. If the shadow cache content differs, document the differences. This rules in or out cause (d) above.
>
> **Constraints:**
> - Do NOT propose a fix. Do NOT modify production code. Do NOT modify the regex. The deliverable is a cause-of-undercount finding only.
> - Do NOT use `python3 -c "..."` with embedded triple quotes — banned per PLANNER_TEMPLATE Rule 5. Use file-based scripts in `/tmp/`.
> - Do NOT use heredoc syntax. Banned per PLANNER_TEMPLATE Rule 5.
> - Do NOT proceed past Phase 5 even if you have a fix in mind. Phase 5 is the terminal phase.
>
> **Output format:** Single deposit file with five sections (Phase 1–Phase 5). Use code blocks for source code, regex patterns, and regex output. End with a one-paragraph "Cause Identified" summary citing the specific Phase that surfaced the cause.
>
> Standard prompt feedback protocol → `bellows/knowledge/research/agent-prompt-feedback.md`.
>
> **Deposits:**
> - `bellows/knowledge/research/extract-total-steps-undercount-2026-05-03.md`
>
> **STOP REMINDER (BOTTOM):** Step 1 is COMPLETE when the deposit file is written with all five phases. Do NOT propose a fix. Do NOT modify production code. Do NOT move the plan to Done. The Planner reads this deposit, verifies it via Rule 22, and authors a separate executable fix plan after the cause is known. Wait for CEO confirmation before any further action.
