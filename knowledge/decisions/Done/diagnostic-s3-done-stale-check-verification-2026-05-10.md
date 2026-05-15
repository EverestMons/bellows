# Diagnostic — verify S3 retry loop (Done/ target) shipped state

**Project:** bellows | **Type:** diagnostic | **Steps:** 1 | **Priority:** 1 | **auto_close:** false

## Context

BACKLOG entry `2026-05-08: S3 — verdict-resolved retry loop when target plan in Done/` reports that when a verdict-resolved file's plan was moved to Done/ before the resolved file was processed, Bellows can't find the corresponding `verdict-pending-` plan and retries the resolved file indefinitely. Hit twice on 2026-05-08. Recommended fix shape: extend `_consume_verdicts` plan-search loop to recognize Done/ as a terminal state.

**Planner code reading on 2026-05-10** found the current `_consume_verdicts()` code already contains a Done/ stale-check:

```python
else:
    # No match — check if plan is already in Done/ OR halted in decisions/ (stale verdict)
    stale = False
    for decisions_path in search_dirs:
        done_dir = os.path.join(decisions_path, "Done")
        if os.path.isdir(done_dir):
            for dname in os.listdir(done_dir):
                if plan_slug in dname:
                    stale = True
                    break
```

This appears to be the exact fix shape the BACKLOG entry recommended. Two possibilities:

1. The Done/ stale-check was added between 2026-05-08 and 2026-05-10 (likely as part of the 2026-05-09 S3 Bug A/B fix in commit `dc0bdd7`/`5136326`), making the 2026-05-08 BACKLOG entry stale.
2. The check has been there all along but does not trigger for some reason — possibly a slug-matching issue, a code path that bypasses it, or an interaction with verdict-request file lifecycle.

This diagnostic determines which case applies before closing or keeping the entry open. Read-only investigation, single SA step, no QA. Mirrors the 2026-05-10 plan-filename-rename diagnostic shape — verify shipped state per LESSONS.md 2026-05-05 ("verify shipped state before designing follow-up").

## STEP 1 — Systems Analyst: S3 Done/ stale-check verification

**Agent:** Bellows Systems Analyst
**Deposits:**
- `bellows/knowledge/research/s3-done-stale-check-verification-2026-05-10.md`

**Prompt:**

```
Read agents/BELLOWS_SYSTEMS_ANALYST.md, then PLANNER_TEMPLATE.md Phase 1.5 sources for any related lessons or research, including LESSONS.md (governance root) for entries tagged `bellows-architecture` or `planner-discipline` from the last ~14 days. Then read bellows/knowledge/BACKLOG.md (the 2026-05-08 S3 retry loop Done/ target entry).

Read-only investigation. No code changes. Single deposit at bellows/knowledge/research/s3-done-stale-check-verification-2026-05-10.md.

CONTEXT
The 2026-05-08 BACKLOG entry recommended fix shape: extend _consume_verdicts to recognize Done/ as a terminal state. Current code already has a Done/ stale-check at the end of the per-verdict-file loop. Determine whether this check was added between 2026-05-08 and 2026-05-10 (BACKLOG stale, close as superseded) or whether it was always there and the bug has another root cause (open follow-up needed).

INVESTIGATION QUESTIONS

Q1. CURRENT CODE STATE — quote the Done/ stale-check verbatim with line numbers from `bellows/bellows.py` `_consume_verdicts()`. Identify the exact branch and slug-matching logic. Document what filename pattern it matches (`if plan_slug in dname` — substring match, position-independent).

Q2. GIT HISTORY — find what changed on this code path between 2026-05-07 and 2026-05-10. Run from `/Users/marklehn/Desktop/GitHub/bellows`:
   ```
   git --no-pager log --since=2026-05-07 --until=2026-05-11 --oneline -- bellows.py
   ```
   For each commit, run `git --no-pager show <sha> -- bellows.py` and check whether it added or modified the `# No match — check if plan is already in Done/` block. Specifically check:
   - `e5188fa` (2026-05-08, qa-prefix dispatch)
   - `afc8523` (2026-05-08, pipe-header-parser)
   - `dc0bdd7` (2026-05-09, S3 Bug A/B fix)
   - `5136326` (2026-05-09, related)
   - `8eac4c3` (2026-05-10, teardown lock detection)
   - Plus any commits today's S3 Bug C fix produced

   Determine: did any of these introduce or modify the Done/ stale-check block? Report which commit and date.

Q3. PRE-FIX STATE — using `git --no-pager show <sha-just-before-introduction>:bellows.py | sed -n '/_consume_verdicts/,/def [a-z]/p'`, show what `_consume_verdicts` looked like BEFORE the Done/ stale-check was added. Confirm that pre-fix, a verdict file matching a plan in Done/ would fall through to the retry-loop log message `no verdict-pending plan found for {slug} step {N} — leaving in resolved/ for retry`.

Q4. SLUG MATCHING ANALYSIS — the Done/ stale-check uses `if plan_slug in dname` (substring match). Verify this works correctly for:
   (a) The standard case: `plan_slug = "executable-foo-2026-05-08"`, `dname = "executable-foo-2026-05-08.md"` — should match
   (b) The `cleanup_slug` case: the `cleanup_slug` is computed from `original_name` (which has lifecycle prefix stripped), but `plan_slug` here is parsed from the verdict filename `verdict-{plan_slug}-step-{N}.md`. These may differ. Specifically, if a verdict file is `verdict-executable-foo-2026-05-08-step-2.md`, then `plan_slug = "executable-foo-2026-05-08"`. The plan in Done/ is named `executable-foo-2026-05-08.md` (no lifecycle prefix). So `"executable-foo-2026-05-08" in "executable-foo-2026-05-08.md"` is True. ✓
   (c) Edge case: what if Done/ contains both `executable-foo-2026-05-08.md` and `executable-foo-extended-2026-05-08.md`? The substring match would match BOTH. Is this a problem?
   (d) Edge case: what if `plan_slug` contains regex-special characters? Substring `in` is not regex; this should be safe. Confirm.

Q5. EMPIRICAL DATA — check `bellows/verdicts/resolved/` and `bellows/verdicts/pending/` directories for current state. Are there any verdict files for plans whose slugs match plans in any project's Done/? If yes, those would be candidates for stale-detection — they should NOT be in resolved/ if Bellows has restarted recently and consumed them. Also check whether any of the 2026-05-08 reproduction files mentioned in the BACKLOG entry (the entry doesn't name specific files, but may reference them implicitly) still exist in resolved/.

Q6. RECOMMENDATION — based on Q1–Q5, classify the BACKLOG entry into one of:
   (i) **Structurally fixed (close as superseded).** The Done/ stale-check was added as part of an intervening fix; BACKLOG entry was stale. Specify the commit and date.
   (ii) **Latent gap (keep open with sharpened scope).** The Done/ stale-check exists but doesn't catch all cases the BACKLOG describes. Specify the gap.
   (iii) **Inconclusive.** Cannot determine from code reading alone. Specify what observation criteria would resolve.

   For (i) provide the closure citation. For (ii) provide a sharpened repro recipe. For (iii) provide explicit observation criteria.

DELIVERABLE
A single findings file at `bellows/knowledge/research/s3-done-stale-check-verification-2026-05-10.md` containing:
- One section per question (Q1–Q6) with answers and code/git citations
- A "Verdict" section stating which classification (i/ii/iii) applies
- A "Confidence" section per major claim with evidence that would raise it

CONSTRAINTS
- Read-only investigation. No edits to bellows/.
- Use bash for git operations (per LESSONS.md 2026-04-23, native tools trip scope_check on cross-project paths).
- Cite line numbers and quote code verbatim where load-bearing.
- For Q4(c)(d), explain WHY the substring match is or isn't a problem. Do not handwave.

RULE 20 SELF-CHECK
End the findings file with the canonical Rule 20 self-check Python block from PLANNER_TEMPLATE Rule 20 with these substitutions:
- plan_slug = "diagnostic-s3-done-stale-check-verification-2026-05-10"
- qa_report_path = "bellows/knowledge/research/s3-done-stale-check-verification-2026-05-10.md"
- evidence_dir = "bellows/knowledge/research/"
- required_evidence_files = ["s3-done-stale-check-verification-2026-05-10.md"]

USE THE VERBATIM TEMPLATE — the literal banner string `Rule 20 — QA Self-Check Results` (em-dash U+2014) and PASSED line `PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.` are load-bearing strings the Bellows gate enforces. ACTUALLY EXECUTE the block (use python3 inline) and include the literal stdout in the findings file.

When complete, end with the standard Output Receipt: status, summary of findings, deposit path.
```

**STOP. Do NOT proceed beyond Step 1. This is a single-step diagnostic.**
