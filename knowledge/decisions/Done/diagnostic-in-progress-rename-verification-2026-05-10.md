# Diagnostic — verify in-progress→verdict-pending rename status

**Project:** bellows | **Type:** diagnostic | **Steps:** 1 | **Priority:** 1 | **auto_close:** false

## Context

BACKLOG entry `2026-05-08: Plan filename not flipped from in-progress- to verdict-pending- on pause` reports that Bellows leaves the plan filename as `in-progress-foo.md` instead of renaming to `verdict-pending-foo.md` on pause. Observed multiple times on 2026-05-08; recommended fix shape: investigate the pause-handling rename in `run_plan()` for silent control-flow skip.

**Empirical contradiction from 2026-05-10 session.** Five plans dispatched today, seven pause events total (Step 1 pauses on multi-step plans + final-step pauses), zero observed failures of the rename. Every plan was found at `verdict-pending-` prefix when the Planner went to close it. Suggests three possibilities: (1) shipped fix between 2026-05-08 and 2026-05-10 not tracked in BACKLOG, (2) intermittent bug we didn't trigger today, (3) edge-case bug requiring specific path-construction conditions.

This diagnostic determines which case applies before closing or keeping the entry open. Read-only investigation, single SA step, no QA. Per LESSONS.md 2026-05-05 ("verify shipped state before designing follow-up") and the 2026-05-03 entry pattern ("BACKLOG entries should be authored AFTER scanning Done/ for same-day corrective activity").

## STEP 1 — Systems Analyst: rename verification

**Agent:** Bellows Systems Analyst
**Deposits:**
- `bellows/knowledge/research/in-progress-rename-verification-2026-05-10.md`

**Prompt:**

```
Read agents/BELLOWS_SYSTEMS_ANALYST.md, then bellows/knowledge/BACKLOG.md (the 2026-05-08 entry on plan filename not flipped on pause). Read PLANNER_TEMPLATE.md Phase 1.5 sources for any related lessons or research, including LESSONS.md (governance root) for entries tagged `bellows-architecture` or `planner-discipline` from the last ~14 days.

Read-only investigation. No code changes. Single deposit at bellows/knowledge/research/in-progress-rename-verification-2026-05-10.md.

CONTEXT
The BACKLOG entry says Bellows leaves filenames at `in-progress-` instead of renaming to `verdict-pending-` on pause. Multiple reproductions on 2026-05-08. The 2026-05-10 session ran 5 plans with 7 total pause events, all of which correctly produced `verdict-pending-` prefixed filenames at the time the Planner went to close them. Determine whether the rename is now structurally correct (BACKLOG entry stale) or whether 2026-05-10 just didn't trigger the bug.

INVESTIGATION QUESTIONS

Q1. CURRENT CODE STATE — read bellows/bellows.py and document the pause-handling rename logic. Specifically:
   (a) Locate the section of `run_plan()` that constructs `verdict_pending_path` and renames the plan file from `in-progress-*` to `verdict-pending-*`. Quote the relevant code with line numbers.
   (b) Document EVERY path-construction site for the rename. The 2026-04-24 reliability bugs fix (BACKLOG closed 2026-04-24, commit `c7f69f3`) introduced `base_filename` canonicalization at 5 sites in `run_plan()` per the closure entry — verify all 5 sites are still present and using the canonicalized name.
   (c) Document the control flow that leads to each rename site. Is there a guard (`if os.path.exists(...)`, `if pause_condition:`, etc.) that could skip the rename silently?
   (d) Are there any code paths where `_teardown_worktree` runs BEFORE the rename and could affect path validity? (Cross-reference today's earlier diagnostic which established gates.check() runs before _teardown_worktree at bellows.py:333 vs 362.)

Q2. GIT HISTORY — find what changed in this code between 2026-05-08 and 2026-05-10. Run from /Users/marklehn/Desktop/GitHub/bellows:
   ```
   git --no-pager log --since=2026-05-07 --until=2026-05-11 --oneline -- bellows.py
   ```
   For each commit, run `git --no-pager show <sha> -- bellows.py` and check whether it touched any of the rename sites identified in Q1. Specifically look at commits from the 2026-05-08 reliability triple-ship (`executable-bellows-qa-prefix-and-skip-logging-2026-05-08`, `executable-step2-auto-advance-fix-2026-05-08`, `executable-pipe-header-parser-and-comprehensive-qa-2026-05-08`) and the 2026-05-09 S3 fix.

Q3. SESSION 2026-05-08 REPRODUCTION CONDITIONS — reconstruct what failed on 2026-05-08. Read the 2026-05-08 PROJECT_STATUS.md entry and any related research/QA files in bellows/knowledge/. What plans paused that day and at what filename prefix did the Planner find them? If the BACKLOG entry was authored from observation of specific plan files, identify them by name and check their final state in Done/.

Q4. SESSION 2026-05-10 EMPIRICAL DATA — the 2026-05-10 session dispatched these plans (all in Done/ now):
   - diagnostic-gate-path-resolution-post-teardown-2026-05-10
   - executable-rule-20-self-check-wt-path-2026-05-10
   - diagnostic-teardown-worktree-reliability-2026-05-10
   - executable-teardown-worktree-lock-cleanup-2026-05-10
   - executable-phase-1-5-lessons-source-d-2026-05-10
   
   For each, check the verdict files in bellows/verdicts/resolved/ (or processed-* if Bellows already moved them) for filenames matching `verdict-{slug}-step-N.md`. Verify each verdict references a `verdict-pending-` prefixed plan path in the resolved verdict's content (the verdict request the Planner read at close time was at `verdict-pending-` prefix). This confirms the rename happened correctly across all 7 pause events.

Q5. EDGE-CASE TRIGGER ANALYSIS — given the 0/7 reproduction rate today vs multiple-times-on-2026-05-08, what conditions might trigger the bug?
   (a) Was 2026-05-08 a pre-pipe-header-parser day? Did the rename code depend on header parsing that was broken? Cross-reference the 2026-05-08 `executable-pipe-header-parser-and-comprehensive-qa-2026-05-08` commit.
   (b) Did 2026-05-08 dispatch plans with parallel-N- prefixes or other unusual filename shapes? The `base_filename` canonicalization may handle simple `in-progress-` prefix but fail on parallel-N or compound prefixes.
   (c) Did 2026-05-08 see crashes mid-step that left plans in unexpected states? The 2026-05-09 S3 work captured several state-machine corruption modes.
   (d) Was the 2026-05-08 daemon running pre-2026-05-09 code? If yes, the BACKLOG observation may have been against code that has since been replaced.

Q6. RECOMMENDATION — based on Q1–Q5, classify the BACKLOG entry into one of:
   (i) **Structurally fixed (close as superseded).** The rename code is correct in current production code; no observed reproduction since some intervening fix; BACKLOG entry was stale.
   (ii) **Latent bug present (keep open with sharpened scope).** The rename code has a real bug not triggered by today's plans; specify the trigger condition based on Q5 analysis.
   (iii) **Inconclusive (keep open with explicit observation request).** Cannot determine from code reading alone; CEO should observe the next 5+ paused plans and report whether the rename fires correctly.
   
   For (i) provide the commit/date the fix landed. For (ii) provide a sharpened reproduction recipe. For (iii) provide explicit observation criteria.

DELIVERABLE
A single findings file at bellows/knowledge/research/in-progress-rename-verification-2026-05-10.md containing:
- One section per question (Q1–Q6) with answers and code/git citations
- A "Verdict" section stating which classification (i/ii/iii) applies
- A "Confidence" section per major claim with evidence that would raise it

CONSTRAINTS
- Read-only investigation. No edits to bellows/.
- Use bash for git operations (per LESSONS.md 2026-04-23, native tools trip scope_check on cross-project paths even when read-class denials are filtered).
- Cite line numbers and quote code verbatim where load-bearing.
- For Q4, the verdict files for today's plans may be in `bellows/verdicts/resolved/` (renamed to `processed-*`) or `bellows/verdicts/processed/` depending on timing. Check both.

RULE 20 SELF-CHECK
End the findings file with the canonical Rule 20 self-check Python block from PLANNER_TEMPLATE Rule 20 with these substitutions:
- plan_slug = "diagnostic-in-progress-rename-verification-2026-05-10"
- qa_report_path = "bellows/knowledge/research/in-progress-rename-verification-2026-05-10.md"
- evidence_dir = "bellows/knowledge/research/"
- required_evidence_files = ["in-progress-rename-verification-2026-05-10.md"]

Use the verbatim template — the literal banner string `Rule 20 — QA Self-Check Results` (em-dash U+2014) and PASSED line `PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.` are load-bearing strings the Bellows gate enforces. ACTUALLY EXECUTE the block (use python3 inline) and include the literal stdout in the findings file. Do NOT just include the script.

When complete, end with the standard Output Receipt: status, summary of findings, deposit path.
```

**STOP. Do NOT proceed beyond Step 1. This is a single-step diagnostic.**
