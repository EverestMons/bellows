# Diagnostic — Gate path-resolution gap post-teardown

**Project:** bellows | **Type:** diagnostic | **Steps:** 1 | **Priority:** 1 | **auto_close:** false

## Context

The `deposit_exists` and `rule_20_self_check` gates have produced false-positive failures on every QA pause in recent invoice-pulse sessions, despite all evidence files and QA reports existing on disk in the main project tree at exactly the paths declared in plans. Reproductions documented in BACKLOG entry `2026-05-07: deposit_exists / rule_20_self_check gate path-resolution gap recurred on action queue aggregation session` (re-affirmed 2026-05-08).

Distinct from BACKLOG closed 2026-05-06 (`deposit_exists` worktree-aware fix shipped via `executable-deposit-exists-worktree-aware-2026-05-06`) which added Strategy 0 (worktree-first) to `_resolve_deposit_path`. Today's failures suggest a different timing window: the QA agent's commit-and-cherry-pick path lands files in main BEFORE Bellows runs the gate check, but Bellows is still resolving paths from `wt_path` (which by then is empty or torn down).

This diagnostic determines the actual root cause and recommends a fix shape. No code changes — read-only investigation, findings deposit only.

## STEP 1 — Systems Analyst: gate path-resolution post-teardown investigation

**Agent:** Bellows Systems Analyst
**Deposits:**
- `bellows/knowledge/research/gate-path-resolution-post-teardown-2026-05-10.md`

**Prompt:**

```
Read agents/BELLOWS_SYSTEMS_ANALYST.md, then PLANNER_TEMPLATE.md (governance root), then COMPANY.md (governance root). You are the Bellows Systems Analyst working on a read-only diagnostic investigation. No code changes. Single deposit: a findings file at bellows/knowledge/research/gate-path-resolution-post-teardown-2026-05-10.md.

CONTEXT
The deposit_exists and rule_20_self_check gates produce false-positive failures on QA-step pauses for plans dispatched to projects that use worktree isolation (i.e., projects with their own .git, not bellows-self). The QA agent commits its evidence files and QA report to a worktree branch, _teardown_worktree cherry-picks those commits to main, the working tree on main now contains the files at the declared paths — yet Bellows reports them as missing.

The 2026-05-06 close added Strategy 0 (worktree-first) to _resolve_deposit_path via executable-deposit-exists-worktree-aware-2026-05-06. That fix solved the case where files exist in the worktree and the gate looked at project_path. Today's failure is the inverse: files exist in project_path (post-cherry-pick) and the gate may be looking at a worktree that no longer exists.

REPRODUCTIONS (live evidence files in bellows/verdicts/pending/ and bellows/verdicts/resolved/)
- verdict-request-action-queue-aggregation-2026-05-07-step-3.md (8 failures: 6 deposit_exists + 2 rule_20_self_check)
- verdict-request-qa-report-rule-20-banner-fix-2026-05-07-step-2.md (1 rule_20_self_check failure)
- Re-affirmed 2026-05-08 across multiple invoice-pulse QA runs

INVESTIGATION QUESTIONS

Q1. Read bellows/gates.py end-to-end. Document the current implementation of:
   (a) _resolve_deposit_path — every strategy it tries, in order. Quote the relevant code.
   (b) _gate_deposit_exists — how it calls _resolve_deposit_path, what it does with wt_path.
   (c) _gate_rule_20_self_check — same questions, plus what content it reads from QA reports.
   Include line numbers for each function.

Q2. Read bellows/bellows.py and locate the call sequence around step completion. Specifically determine the ordering of:
   (a) Agent process exits (subprocess returns)
   (b) git diff capture / scope_check evaluation
   (c) QA agent's commits cherry-picked to main via _teardown_worktree
   (d) gates.check() invocation
   (e) verdict request file written
   (f) _teardown_worktree cleanup (git worktree remove)
   List these in the actual chronological order they execute. Quote the relevant code blocks with line numbers.

Q3. Specifically: when gates.check() runs, has _teardown_worktree already executed?
   - If YES: what value is wt_path at gate evaluation time? (path to a now-removed directory? empty string? still the old path?)
   - If NO: are the QA agent's commits already cherry-picked to main, or are they still only on the worktree branch?
   Quote the exact code that determines this ordering.

Q4. For the 2 verdict-request files cited above, examine them (read the files at bellows/verdicts/pending/ and bellows/verdicts/resolved/ — note the resolved versions contain Planner override verdicts with full diagnosis text). For each gate failure listed, determine:
   (a) The path the gate was checking (worktree-relative or project-relative?)
   (b) Whether the file actually exists at that path on main right now
   (c) Whether _resolve_deposit_path's Strategy 0 (worktree) is being attempted on a path that no longer exists post-teardown

Q5. Trace the lifetime of wt_path across one full step execution. Where is it created? Where is it captured for later use? Where is it passed into gates.check()? When does the directory it points to get removed? Identify the structural seam — the line of code where wt_path becomes stale relative to the gate check.

Q6. Recommend a fix shape. Evaluate these candidates from the BACKLOG entry plus any others that emerge from your investigation:
   (1) Make gate evaluation happen BEFORE _teardown_worktree (so worktree paths still exist).
   (2) After teardown, re-resolve all deposit paths via Strategy 1 (project_path) since cherry-picked files are now there.
   (3) Gate check at TWO points — pre-teardown for worktree paths, post-teardown for project_path paths — fail-fast on first hit.
   (4) Anything else that emerges from your code reading.
   For each, give: estimated LOC, risk level, whether it preserves the 2026-05-06 worktree-first fix, and whether it resolves the rule_20_self_check case in addition to deposit_exists.

Q7. Cross-reference with BACKLOG `2026-05-07: _teardown_worktree cherry-pick fragility`. Specifically: if the cherry-pick fails or only brings forward a single SHA (missing the QA commit), the QA report file may not be on main at all — would that present as the same gate failure pattern as the timing issue you're investigating? How do you distinguish the two failure modes from a verdict-request file alone?

DELIVERABLE
A single findings file at bellows/knowledge/research/gate-path-resolution-post-teardown-2026-05-10.md containing:
- One section per question (Q1–Q7) with answers and code citations
- A "Root cause" section stating the specific structural mechanism (which lines of code, in which order, produce the false positive)
- A "Recommended fix" section identifying the preferred candidate from Q6 with rationale
- A "Confidence" section: high / medium / low, with what evidence would raise confidence

CONSTRAINTS
- Read-only investigation. No edits to bellows/ source. No commits.
- Use bash for cross-project reads if needed (avoid native Read/Grep on cross-project paths to avoid scope_check trips on read-class denials — though read-class denials are now filtered, bash is still the safer pattern per LESSONS.md 2026-04-23).
- Cite line numbers and quote code verbatim where it is load-bearing for the answer.
- If you find evidence that contradicts the BACKLOG hypothesis (e.g., the gate check is actually pre-teardown and the bug is elsewhere), say so explicitly.

RULE 20 SELF-CHECK
End your findings file with the canonical Rule 20 self-check banner and Python block verifying the deposit file exists. The block must execute and print SELF-CHECK PASSED or SELF-CHECK FAILED.

When complete, end with the standard Output Receipt: status, summary of findings, deposit path.
```

**STOP. Do NOT proceed beyond Step 1. This is a single-step diagnostic.**
