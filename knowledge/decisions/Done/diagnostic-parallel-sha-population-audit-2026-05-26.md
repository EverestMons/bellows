# Diagnostic — Parallel-SHA Teardown Population Audit (Post-v4.47)
**Project:** bellows
**Date:** 2026-05-26
**Author:** Planner
**Dispatch Mode:** bellows
**Total Steps:** 1
**pause_for_verdict:** after_step_1
**auto_close:** false
**qa_steps:** none

---

## CEO Context

The 2026-05-21 BACKLOG entry on parallel-SHA teardown divergence was filed when the root cause was understood to be agent-side `git push` calls from plan step prose (per the 2026-05-21 teardown-git-operations-mapping SA diagnostic findings: Bellows-the-daemon has zero push calls; the pushes came from plan prose). On 2026-05-21 the governance closure shipped via `executable-planner-template-no-push-and-routing-count-2026-05-21` (v4.47), which added explicit prohibitions in Rule 8 mirror and Rule 23(c): "Agents do NOT run `git push` during step execution." Rule 31 (Planner-side submodule push) and Procedure 3 (operator filter-repo push) carve-outs were preserved.

**Hypothesis under test:** the v4.47 prohibition closed the root cause. Post-v4.47 plans should show zero parallel-SHA reproductions. If the audit confirms this, the BACKLOG entry can be closed as superseded by v4.47 and no structural fix is required. If the audit finds residual reproductions, the diagnostic surfaces what's still producing pushes despite the governance prohibition — and that delta drives the next plan.

This is a population audit, not a code-tracing investigation. The SA does not read Bellows source. The SA reads git history and plan files to characterize the audit window.


---

## STEP 1 (SA) — Parallel-SHA Reproduction Audit

Read your specialist file at `agents/BELLOWS_SYSTEMS_ANALYST.md` first. Skip glossary read — this is a git-history audit task with no domain terminology surface. Note: worktree root IS the bellows project root — strip the `bellows/` prefix from any path references in this prompt when running commands.

### Audit window

**Start:** commit landing v4.47 (2026-05-21). Use `git --no-pager log --all --oneline --grep="v4.47" --grep="no-push" -i` to locate the governance commit; if multiple candidates surface, anchor to the bellows submodule pointer bump committed to the governance root on 2026-05-21 (the bellows commit immediately following the v4.47 governance commit).

**End:** today (2026-05-26).

**Scope of plans audited:** every plan that reached `Done/` between the start date and today. Enumerate via `ls -lt knowledge/decisions/Done/ | head -50` and filter by date.

### Investigation procedure

1. **Enumerate post-v4.47 Done/ plans.** Produce a table:
   - Plan filename
   - Plan close date (from filename suffix or git log on the move)
   - Plan type (executable / diagnostic / orchestration)
   - Number of steps (from `**Total Steps:**` header)
   - Whether the plan involved code changes (any step prose containing `git commit`, `git add`, or referencing a code file edit)

   Target population size: estimate ~10-20 plans in the 5-day window. If population is <5, flag it — the audit is underpowered and the disposition recommendation must reflect that.

2. **For each plan in the population, check for parallel-SHA divergence.** A parallel-SHA event has these properties:
   - Local main and origin/main both contain commits for the same step's work
   - The two commits have identical `git diff` output (content-identical) but distinct SHAs
   - The divergence typically appears as `git --no-pager log --oneline origin/main..HEAD` showing N commits AND `git --no-pager log --oneline HEAD..origin/main` showing N parallel commits

   For each plan, run:
   ```
   git --no-pager log --all --oneline --grep="<plan-slug-or-keyword-from-plan>" -20
   ```
   Look for clusters of commits with identical message+date but distinct SHAs. If none present in the post-v4.47 window, that's the expected outcome (hypothesis confirmed).

3. **Cross-reference with the agent-prompt-feedback log.** Read `knowledge/research/agent-prompt-feedback.md` for entries dated 2026-05-22 onward. Search for the strings `parallel-SHA`, `parallel SHA`, `cherry-pick`, `divergence`, `push from worktree`, `committed to origin`. Any post-v4.47 mention of these patterns is a candidate reproduction. Capture the entry's plan reference and date.

4. **Cross-reference with the BACKLOG log.** Read `knowledge/BACKLOG.md` for any Open or Closed entries dated 2026-05-22 onward that reference parallel-SHA, cherry-pick failures, or teardown push behavior. Note: the 2026-05-22 entries on teardown cherry-pick conflicts (`PROJECT_STATUS.md` dirty-tree variant and shared-bookkeeping-file variant) are about cherry-pick CONFLICTS on shared files, not parallel-SHA divergence — distinguish these clearly in your findings. The audit is specifically about content-identical parallel SHAs, not conflict-driven cherry-pick failures.

5. **Determine the push source for any reproductions found.** If any post-v4.47 plan shows parallel-SHA divergence, the next question is: where did the push come from? Three possibilities, mutually exclusive:
   - (a) **Agent-side push from plan prose despite Rule 23(c).** The plan was authored before or in violation of v4.47. Examine the plan's step prose for `git push` instructions.
   - (b) **Bellows-side push from teardown code.** This was ruled out by the 2026-05-21 SA diagnostic (Bellows has zero push calls), but if the audit finds reproductions with no plan-prose source, this hypothesis must be re-examined. Do NOT read Bellows source to investigate — flag it as a follow-up SA diagnostic.
   - (c) **External push source.** CEO-side `git push` during session work, Bellows daemon restart cycle, or other operator-induced push. Identify which.

   For each reproduction, declare (a)/(b)/(c) with one line of evidence supporting the classification.

6. **Disposition recommendation.** Based on the audit, produce one of three findings:
   - **CLOSE-SUPERSEDED:** zero post-v4.47 reproductions found. Recommendation: close the BACKLOG entry as superseded by v4.47, no structural fix required, capture this audit as the closure evidence.
   - **CLOSE-UNDERPOWERED:** fewer than 5 plans in population, zero reproductions. Recommendation: defer the audit re-run until population reaches threshold (~30 days post-v4.47 = approximately 2026-06-20). Keep BACKLOG entry Open.
   - **STRUCTURAL-FIX-NEEDED:** one or more post-v4.47 reproductions found, classification (b) or (a) with persistent pattern. Recommendation: file follow-up SA diagnostic to characterize the residual pathway. Specify the diagnostic shape (what to investigate, what NOT to read).

### Verification Blocks (Rule 39)

The audit's load-bearing claims are population-level. Capture verification blocks for:

- **Block 1:** the post-v4.47 plan count. Command: `ls knowledge/decisions/Done/*.md | wc -l` filtered by date. Expected: N plans. Actual: N plans. Materiality: claim of "zero reproductions" depends on N being large enough to be meaningful.

- **Block 2:** the parallel-SHA event count. Command: enumeration of git log clusters with identical message+content but distinct SHAs in the audit window. Expected: 0 (if hypothesis confirmed) or M>0 (if refuted). Actual: count from audit.

- **Block 3:** the agent-prompt-feedback search results. Command: `grep -i -E "parallel.sha|cherry.pick|push.*worktree" knowledge/research/agent-prompt-feedback.md | head -20`. Expected: zero post-v4.47 hits. Actual: report results.

### Deposits

- `knowledge/research/parallel-sha-population-audit-2026-05-26.md` — findings file with the four sections (enumeration table, per-plan reproduction check, push-source classification, disposition recommendation) plus the three verification blocks

### Output Receipt Format

End the deposit with the standard Output Receipt section per the specialist template. Status: Complete. Files Deposited: the single findings file. Flags for CEO: the disposition recommendation (CLOSE-SUPERSEDED / CLOSE-UNDERPOWERED / STRUCTURAL-FIX-NEEDED) with one-line reasoning.

### Boundary constraints

- **Do NOT read Bellows source code.** This is a population audit using git history, plan files, and agent-prompt-feedback. Source-tracing belongs to a follow-up diagnostic if STRUCTURAL-FIX-NEEDED is the outcome.
- **Do NOT run `git push`** during the audit. The audit reads git state; it does not modify it.
- **Do NOT attempt to reproduce parallel-SHA divergence.** Reproduction would require deliberately running a code-change plan and observing teardown — out of scope for an audit.
- **Do NOT close the BACKLOG entry as part of this plan.** The BACKLOG edit is a Planner-side action that occurs after the CEO reviews the audit findings and accepts the disposition.
