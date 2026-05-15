# Diagnostic — _teardown_worktree reliability cluster

**Project:** bellows | **Type:** diagnostic | **Steps:** 1 | **Priority:** 1 | **auto_close:** false

## Context

Two BACKLOG entries point at the same `_teardown_worktree` reliability surface:

- **2026-05-07 cherry-pick fragility** — two failure modes during teardown of `executable-billto-type-field-mapping-fix-2026-05-07`: (a) stale `.git/index.lock` causing 60s subprocess timeout, (b) single-SHA cherry-pick missing the QA commit. Manual recovery cost ~10 minutes including manual cherry-pick of two SHAs.

- **2026-05-06 cherry-pick reliability gap (population audit needed)** — CEO observed ~20 plan files in invoice-pulse `knowledge/decisions/Done/` showing as Untracked + 5 stale deletions in main checkout. Suggests `_teardown_worktree` is not reliably cherry-picking all changes back to main.

The 2026-05-07 entry explicitly cross-references 2026-05-06: "The two entries should be unified into a single diagnostic when prioritized." This is that diagnostic.

Single SA step, read-only investigation. No code changes; findings-only deposit.

## STEP 1 — Systems Analyst: _teardown_worktree reliability investigation + population audit

**Agent:** Bellows Systems Analyst
**Deposits:**
- `bellows/knowledge/research/teardown-worktree-reliability-2026-05-10.md`

**Prompt:**

```
Read agents/BELLOWS_SYSTEMS_ANALYST.md, then PLANNER_TEMPLATE.md (governance root), then bellows/knowledge/BACKLOG.md (entries 2026-05-07 cherry-pick fragility and 2026-05-06 cherry-pick reliability gap). You are the Bellows Systems Analyst running a unified diagnostic across two related BACKLOG entries.

Read-only investigation. No code changes. Single deposit: a findings file at bellows/knowledge/research/teardown-worktree-reliability-2026-05-10.md.

CONTEXT
The 2026-05-07 entry captures a live failure: cherry-pick timed out after 60s due to stale `.git/index.lock` in invoice-pulse, AND the cherry-pick command was scoped to a single SHA when the worktree branch had two commits (DEV commit + QA commit). Manual recovery required `git cherry-pick 2d39d0a6 b618279e` to bring both forward. The 2026-05-06 entry captures a population-level symptom: ~20 Done/ plan files showing as Untracked in invoice-pulse + 5 stale deletions, suggesting cherry-pick may not be reliably bringing all changes back to main.

These two entries likely share a root cause. The 2026-05-07 entry recommends unifying them into a single diagnostic.

INVESTIGATION QUESTIONS

Q1. CODE AUDIT — read bellows/bellows.py and document the current implementation of `_teardown_worktree` and its callers. Quote the relevant code with line numbers. Specifically answer:
   (a) What is the exact cherry-pick command shape? (single SHA, range, or other?)
   (b) Which SHA(s) does it target? (first commit on wt branch, last commit, HEAD, range, all?)
   (c) Does it detect or handle `.git/index.lock` in the project repo before cherry-pick?
   (d) What is the subprocess timeout value? Where is it set?
   (e) On cherry-pick failure, what happens? Is the worktree left alive? Is a verdict written?
   (f) On cherry-pick success, what cleanup runs? Does it remove the worktree directory? Does it prune?
   (g) Is there a copy-back path for uncommitted files in the worktree, separate from the cherry-pick path? When does it run?

Q2. CALLER AUDIT — find every call site of `_teardown_worktree` in `bellows.py`. For each, document:
   (a) Line number and surrounding context
   (b) What state the worktree is in when teardown fires (clean exit, gate failure, error path, etc.)
   (c) Whether `_teardown_worktree` is wrapped in try/except — and if so, what happens to errors

Q3. POPULATION AUDIT — invoice-pulse Done/ entries from 2026-05-03 onward. The post-worktree-migration window starts at commit 36b2bba (2026-05-03 daemon restart) per `bellows/knowledge/research/backlog-1-reproduction-audit-2026-05-05.md`. For each plan file in `/Users/marklehn/Desktop/GitHub/invoice-pulse/knowledge/decisions/Done/` whose filename contains a date 2026-05-03 or later, check:
   (a) Is the plan file tracked by git? Run from /Users/marklehn/Desktop/GitHub/invoice-pulse: `git ls-files knowledge/decisions/Done/<plan-name>.md` — empty output means untracked.
   (b) Are the plan's expected commits on main? Search for the plan slug in commit messages: `git --no-pager log --all --oneline | grep "<plan-slug-fragment>"`. Note presence/absence.
   (c) Classify each plan into one of:
      - (i) shipped cleanly — file tracked + commits on main
      - (ii) commits landed but plan file untracked
      - (iii) plan file tracked but commits missing
      - (iv) other anomaly (describe)

   Use bash for ALL invoice-pulse access (per LESSONS.md 2026-04-23, native Read/Grep/Glob trip scope_check on cross-project paths). Example:
   ```
   cd /Users/marklehn/Desktop/GitHub/invoice-pulse
   ls knowledge/decisions/Done/ | grep -E '2026-05-(0[3-9]|[12][0-9]|3[01])|2026-0[6-9]|2026-1[0-2]' | while read f; do
     tracked=$(git ls-files "knowledge/decisions/Done/$f" 2>/dev/null)
     echo "FILE: $f"
     echo "TRACKED: $tracked"
     slug=$(echo "$f" | sed 's/\.md$//')
     # match commits referencing the slug fragment
     commits=$(git --no-pager log --all --oneline | grep -F "$slug" | head -5)
     echo "COMMITS: $commits"
     echo "---"
   done
   ```
   Capture output and include it (or a structured summary table) in the findings.

Q4. POPULATION AUDIT — bellows Done/ entries from 2026-05-03 onward, same methodology as Q3. Run from /Users/marklehn/Desktop/GitHub/bellows. Note: bellows-self plans run in-place without worktree per the 2026-05-04 detect-and-skip close, so bellows Done/ entries may show different patterns than invoice-pulse. Flag any cross-classify anomalies.

Q5. FAILURE MODE CHARACTERIZATION — for the 2026-05-07 billto incident (manual recovery commit `5daf671e`, agent commits `2d39d0a6` + `b618279e`), trace through what happened step by step. Read the recovery commit if available. Determine:
   (a) Did the cherry-pick subprocess actually start, or was it blocked from acquiring index? (Failure 1 hypothesis is the lock; the timeout is a symptom.)
   (b) If the cherry-pick had succeeded, would it have brought b618279e along? (Failure 2 hypothesis is the single-SHA scope.)
   (c) Are these two failure modes independent, or does one trigger the other? (E.g., does the lock leftover come from a prior partial teardown that itself was a single-SHA bug?)

Q6. ADDITIONAL OBSERVATION VECTORS — beyond the 2026-05-07 incident:
   (a) From the Q3/Q4 population audit, are there silent-stranding patterns (commits stranded on worktree branches that never made it back to main)? Look for plan slugs with NO commits on main but plan file in Done/.
   (b) Search recent bellows logs for any `WorktreeTeardownError` or cherry-pick failure messages. Logs at /Users/marklehn/Desktop/GitHub/bellows/logs/. `grep -r -l "cherry-pick" /Users/marklehn/Desktop/GitHub/bellows/logs/ 2>/dev/null | head -10` then read the matching log fragments.
   (c) Are there `.git/index.lock` files currently present in any watched project? Run `find /Users/marklehn/Desktop/GitHub -path '*/Library' -prune -o -name 'index.lock' -print 2>/dev/null` and report.

Q7. FIX SHAPE EVALUATION — evaluate the BACKLOG-listed candidates plus any that emerge from your investigation:
   (1) Cherry-pick the full range from inside the worktree: `git cherry-pick main..HEAD` — brings every commit on the branch.
   (2) Replace cherry-pick with `git merge --ff-only <wt-branch>` from main, when the worktree branch is strictly ahead. Compare the two: which is more robust against rebase situations? Which preserves git history more cleanly?
   (3) Detect `.git/index.lock` before cherry-pick — wait briefly with backoff, or remove if older than N seconds. Addresses Failure 1 specifically.
   (4) Anything else that emerges (e.g., `git rebase` instead of cherry-pick, `git diff --binary | git apply` patch-based integration, etc.).

   For each candidate:
   - Estimated LOC
   - Risk level (low / medium / high)
   - Whether it closes Failure 1 (lock) and/or Failure 2 (multi-SHA)
   - Whether it preserves the 2026-05-04 detect-and-skip behavior for bellows-self plans
   - Edge cases (concurrent CEO commits to main during teardown, divergent branches, conflicts)

Q8. PRECEDENCE QUESTION — if multiple fixes are needed, what is the order of operations? Should Failure 1 (lock) and Failure 2 (multi-SHA) be shipped in a single executable plan or two? Does one logically precede the other? Are there interactions where fixing one without the other introduces new failure modes?

DELIVERABLE
A single findings file at bellows/knowledge/research/teardown-worktree-reliability-2026-05-10.md containing:
- One section per question (Q1–Q8) with answers and code citations
- A "Population audit summary" subsection inside Q3/Q4 with structured tables: counts by classification, list of stranded plans (if any)
- A "Root cause(s)" section: are the 2026-05-06 and 2026-05-07 entries truly the same root cause, or are they distinct failure modes that happen to manifest near the same code?
- A "Recommended fix" section: identify the preferred candidate(s) with rationale and a one-paragraph justification for the precedence answer (Q8)
- A "Confidence" section: high / medium / low per major claim, with what evidence would raise confidence

CONSTRAINTS
- Read-only investigation. No edits to bellows/, invoice-pulse/, or any project source. No commits.
- For ALL cross-project reads (anything outside bellows/), use bash exclusively. Native Read/Grep/Glob trip scope_check on cross-project paths.
- Cite line numbers and quote code verbatim where it is load-bearing for the answer.
- Cite git commit SHAs verbatim where they appear in the analysis.
- If you find evidence that contradicts the BACKLOG hypotheses (e.g., the 2026-05-06 untracked-files pattern is not actually caused by `_teardown_worktree`), say so explicitly and explain what the actual cause is.

RULE 20 SELF-CHECK
End your findings file with the canonical Rule 20 self-check banner and Python block verifying the deposit file exists. ACTUALLY EXECUTE THE BLOCK and include the output (must print "RULE 20 SELF-CHECK PASSED" verbatim if the deposit file exists). Use absolute paths.

When complete, end with the standard Output Receipt: status, summary of findings, deposit path.
```

**STOP. Do NOT proceed beyond Step 1. This is a single-step diagnostic.**
