# Diagnostic — Rule 26 Deposits Block Form Acceptance Canary

**Project:** bellows
**Type:** Diagnostic
**Priority:** 5
**Author:** Planner
**Date:** 2026-05-11

## Context

The 2026-05-11 deposit_exists audit confirmed the current gate code uses
`os.path.isfile() or os.path.isdir()` at every resolution strategy, meaning
directories CAN resolve. The 2026-04-19 Lessons entry stating "deposit_exists
gate uses os.path.isfile() which returns False for directory paths" is stale
code knowledge.

PLANNER_TEMPLATE Rule 26 currently contains contradictory guidance: line 738
says "list the evidence directory as a single bullet" while the 2026-04-19
Lesson says "Do NOT list a directory path in the block." This contradiction
must be resolved before authoring the Rule 26 governance edit.

Before resolving the contradiction by writing, verify empirically: does the
current gate accept a directory-only `**Deposits:**` declaration without
tripping Gate 5?

## STEP 1 — Systems Analyst: Verify directory-bullet acceptance

You are the Systems Analyst. Determine whether the current Bellows gate-5
implementation accepts a `**Deposits:**` block containing ONLY a directory
path (no individual files inside it) without triggering a false positive.

**Method:**

1. Read `bellows/gates.py` lines 183-290 to confirm:
   - `_resolve_deposit_path()` uses `isfile() or isdir()` at every strategy
     (lines 192, 201, 205, 209 per the prior audit).
   - `_extract_plan_required_deposits()` does not filter out directory paths
     from the parsed bullet list.
   - `_gate_deposit_exists()` does not apply a separate `isfile()`-only check
     before or after path resolution.

2. Read `bellows/verdict.py:34-62` to confirm:
   - `extract_primary_deposit()` returns `.md`-only paths from the plural
     block, which means a directory bullet does NOT become the primary
     deposit for the verdict request "Deposit:" header — but this does NOT
     affect gate evaluation, which uses `_extract_plan_required_deposits()`
     in gates.py separately.

3. Find a recent post-fix plan in `bellows/knowledge/decisions/Done/` (after
   2026-05-06) whose `**Deposits:**` block declared a directory path and
   trace whether Gate 5 passed for that directory bullet specifically. Use
   `bellows/logs/` JSON step logs to identify the exact gate-5 outcome per
   declared deposit.

4. If no such reproduction exists in the historical record, simulate the
   resolution by manually running `_resolve_deposit_path()` against a
   directory path that exists on disk (e.g.,
   `bellows/knowledge/qa/evidence/`).

**Report:**

Deposit findings as a single markdown file. Structure:

1. **Verdict** — one sentence: does the current gate accept a directory-only
   `**Deposits:**` bullet (YES / NO / CONDITIONAL).
2. **Code evidence** — verbatim lines from `gates.py` confirming or refuting.
3. **Historical evidence** — any post-fix plan with a directory bullet and
   the corresponding gate-5 outcome from the logs.
4. **Simulation** (if no historical evidence) — manual trace of
   `_resolve_deposit_path()` against a real directory path on disk.
5. **Stale-knowledge confirmation** — explicit statement of whether the
   2026-04-19 Lessons entry is stale, and which gate-code change made it
   stale (commit reference if findable via git log).

**Out of scope:**
- Do not propose Rule 26 edits.
- Do not modify any source file.
- Do not write tests.

**Deposits:**
- `bellows/knowledge/research/rule-26-directory-bullet-canary-2026-05-11.md`
