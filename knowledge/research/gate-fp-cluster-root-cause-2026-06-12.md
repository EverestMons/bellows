# Gate False-Positive Cluster Root Cause — scope_check x2 + stop_prose (FORWARD rows 16/17/21)

**Date:** 2026-06-12 | **Agent:** Bellows Systems Analyst | **Plan:** diagnostic-27

---

## Section 1 — Diff-Pipeline Anatomy (rows 16 + 21 share it)

### What is diffed and against what base

The diff pipeline has two functions:

1. **`_capture_git_diff(project_path)`** (`bellows.py:801-822`): Captures the current `HEAD` commit SHA via `git rev-parse HEAD` (run with `cwd=project_path`). Despite its name ("diff"), it returns only a SHA string. The function name is anachronistic — it was refactored from a `git diff --stat` implementation to a SHA-based approach to fix the file_change_audit false-negative (BACKLOG 2026-05-21; diagnostic at `knowledge/research/file-change-audit-false-negative-2026-05-25.md`).

2. **`_parse_diff_stat(post_diff, pre_diff, project_path)`** (`bellows.py:825-878`): Runs `git diff --stat=300 --relative <pre_diff_sha> -- .` with `cwd=project_path`. The `post_diff` parameter is **unused** (retained for call-site signature compatibility). The `--relative` flag scopes output to `project_path`; the `-- .` pathspec limits to the current directory. Returns a sorted list of changed filenames. The diff compares `pre_diff` SHA to the **current working tree state** (not HEAD), so it captures both committed and uncommitted changes since the pre_diff capture point.

### Pre/post-step capture callsites

**First step (initial dispatch):**
- `bellows.py:534`: `pre_diff = _capture_git_diff(wt_path)` — captured immediately after worktree creation, before `runner.run_step()`. Records HEAD at step start.
- `bellows.py:576-577`: `post_diff = _capture_git_diff(wt_path)` + `files_changed = _parse_diff_stat(post_diff, pre_diff, wt_path)` — captured after step completes and `_auto_stage_deposits()` runs (line 572-573).

**Subsequent steps (continuous-run loop):**
- `bellows.py:644`: `pre_diff = _capture_git_diff(wt_path)` — re-captured for each subsequent step, after the prior step's gates pass. This captures the current HEAD, which advances if the agent committed during the prior step.
- `bellows.py:686-687`: Same post-step capture pattern as above.

### Worktree create/teardown and merge

**`_create_worktree(project_path, slug)`** (`bellows.py:881-988`):
- Creates a named-branch worktree at `.bellows-worktrees/<slug>` via `git worktree add <path> -b bellows-wt/<slug> HEAD`.
- Branch starts from `HEAD` of the main working tree at creation time.
- **No-`.git` fallback** (`bellows.py:891-894`): If `project_path` has no project-local `.git` (file or directory), the function logs a WARN and **returns `project_path` as-is**. The caller uses `wt_path == project_path` as the sentinel for "no worktree created." This is the in-place execution mode.

**`_teardown_worktree(project_path, wt_path, slug)`** (`bellows.py:1091-1200+`):
- No-op when `wt_path == project_path` (`bellows.py:1098-1099`) — in-place execution skips teardown entirely.
- When a worktree exists: collects commits via `git log HEAD --not main` in the worktree, merges the worktree branch onto main (ff-only first, then --no-ff fallback), removes worktree and branch.

### Row 21 — Parallel-plan in-place diff contamination (plan 19 → plan 20)

**Mechanism confirmed via 2026-06-12 terminal log** (`bellows-2026-06-12.log`):

Both plans 19 and 20 execute against the `governance` project directory, which has **no project-local `.git`**. Log evidence:
- Line 366: `14:36:32 [WARN] [19] governance has no project-local .git — running in-place without worktree isolation`
- Line 409: `15:00:26 [WARN] [20] governance has no project-local .git — running in-place without worktree isolation`

**Timeline reconstruction:**

| Time | Event | Effect on shared directory |
|------|-------|---------------------------|
| 14:59:01 | Plan 19 resumes step 2 | Agent runs in governance/ |
| 14:59:46 | Plan 19 step 2 gates PASS | files_changed=1 |
| 15:00:26 | Plan 20 step 1 starts | `pre_diff = _capture_git_diff(governance/)` captures HEAD SHA at this moment (call it `SHA_A`) |
| 15:00:28 | Plan 20 step 1 agent starts running | Both agents now concurrently modify governance/ |
| 15:01:03 | Plan 19 resumes step 3 | Agent runs in same governance/ |
| 15:04:34 | Plan 19 step 3 gates PASS, files_changed=5 | Plan 19's agent committed ~5 files to the shared directory. Teardown is a **no-op** (in-place mode) |
| 15:05:06 | Plan 19 verdict continue-to-done | Plan 19 closes. Its commits remain in the shared repo |
| 15:10:52 | Plan 20 step 1 gates run | `_parse_diff_stat` runs `git diff --stat SHA_A -- .` in governance/. This captures ALL changes since SHA_A — including plan 19's step 3 commits. **files_changed=7** (mix of plan 20's own changes + plan 19's artifacts) |

**The exact operation that pulled foreign files into the diff:** `_parse_diff_stat` at `bellows.py:852-854` runs `git diff --stat=300 --relative <SHA_A> -- .` with `cwd=governance/`. Since both plans operate in-place (no worktree isolation), plan 19's commits between `SHA_A` (15:00:26) and the diff evaluation (15:10:52) are visible as changes from plan 20's baseline. The teardown no-op at `bellows.py:1098-1099` means plan 19's commits land directly on the shared branch, permanently visible to any concurrent plan's diff.

**Key distinction from the FORWARD row title:** The title says "worktree diff contamination" but the actual mechanism is **in-place (no-worktree) diff contamination**. Worktree-isolated plans would NOT have this problem — each worktree has its own branch, and `_parse_diff_stat` runs with `cwd=wt_path`, scoped to the worktree's own state. The contamination arises specifically because `_create_worktree` falls back to returning `project_path` when there's no project-local `.git`.

### Row 16 — Continuous-run multi-step accumulation

**Mechanism per archive entry (2026-06-08):** In a continuous-run multi-step plan (SA→DEV→QA in one worktree, no pause between steps), the scope_check at the terminal step flagged earlier steps' deposits as out-of-scope. The archive entry from 2026-06-08 states: "scope_check evaluates the CUMULATIVE worktree diff against only the FINAL step's prompt context."

**Current code status:** The scope_check union-text fix was shipped 2026-06-10 (commit `706fbe7 feat(gates): scope_check union-of-all-step-texts fix`). The current `_gate_scope_check` at `gates.py:701-709` builds a union of all step texts from step 1 through `step_number`:

```python
all_step_texts = []
for s in range(1, step_number + 1):
    st = _extract_step_text(plan_text, s)
    if st:
        all_step_texts.append(st)
union_text = "\n".join(all_step_texts)
```

**Diff accumulation side:** In the continuous-run path, `pre_diff` is re-captured at `bellows.py:644` between steps. If the agent committed during the prior step, `git rev-parse HEAD` returns the agent's latest commit SHA, and the next step's diff is properly baselined to only show new changes. If the agent did NOT commit (only edited files), HEAD doesn't advance, and the diff accumulates both steps' uncommitted changes. The `_auto_stage_deposits` at `bellows.py:572-573` / `682-683` mitigates this for declared deposits but not for undeclared file changes.

**Net assessment for row 16:** The scope_check side is FIXED (union text, 2026-06-10). The diff accumulation side is a latent issue that requires the agent to not commit — mitigated by `_auto_stage_deposits` for declared files and by standard agent behavior (agents typically commit during steps). FORWARD row 16 is architecturally addressed by the union-text fix; residual diff-accumulation is a narrow edge case.

---

## Section 2 — scope_check Semantics

### Gate logic (`gates.py:697-748`)

`_gate_scope_check` evaluates whether files in `files_changed` are "in scope" for the current plan step:

1. **Union text construction** (`gates.py:701-709`): Builds a union of all step texts from step 1 through `step_number` (post-2026-06-10 fix).

2. **Per-file evaluation** (`gates.py:714-741`):
   - **Allowlist bypass** (`gates.py:717-720`): Files matching `SCOPE_ALLOWLIST` basenames (`agent-prompt-feedback.md`, `PROJECT_STATUS.md`, `.gitkeep`) or `SCOPE_ALLOWLIST_PREFIXES` (`in-progress-`, `verdict-pending-`, `halted-`) are always accepted.
   - **Text mention** (`gates.py:721`): `if fpath in union_text or basename in union_text: continue` — accepts files whose full path or basename appears anywhere in the union of step texts.
   - **Directory-mention authorization** (`gates.py:723-739`): Accepts a file when an ancestor directory path (with trailing slash, at least 2 segments deep) appears in the union text. Added by commit `ee2bb4c` (2026-05-28 scope_check FP).

3. **Failure recording** (`gates.py:743-748`): Any files not authorized by the above checks are collected as `out_of_scope` and recorded as a scope_check gate failure.

### Census of 2026-06-12 incidents

**Plan 10 (executable-draft-124247, id 10) — TRUE positive, authoring-caused:**
- Step 1: `files_changed=6`, gates PASS, paused for verdict (12:49:15)
- Step 2: verdict continue (12:52:36), resumed in new worktree from current main HEAD
- Step 2: `files_changed=10`, scope_check FAIL (12:57:44)
- CEO override: continue-to-done (12:59:39)
- **Classification:** TRUE positive by current semantics. The plan's step text union (steps 1+2) does not mention all 10 files the agent produced in step 2. No diff contamination — step 2 ran in a fresh worktree after step 1's teardown merged to main. The 10 files are genuinely step 2's output.
- **Fix layer:** Plan authoring — step text must enumerate or directory-reference all expected outputs. No change to scope_check or diff-capture needed.

**Plan 20 (executable-draft-145929, id 20) — FALSE positive, mechanism-caused:**
- Step 1 starts (15:00:26), pre_diff captured from governance/ (in-place, no worktree)
- Concurrent plan 19 runs step 3 (15:01:03-15:04:34) and commits 5 files to the same governance/ directory
- Plan 20 step 1 completes (15:10:52), `files_changed=7` — includes plan 19's artifacts
- scope_check fires on plan 19's files, which don't appear in plan 20's step text
- CEO override: continue (15:12:09)
- **Classification:** FALSE positive, mechanism-caused. Files from a foreign plan contaminated the diff.
- **Fix layer:** Diff capture — must exclude foreign changes. scope_check semantics are correct; they correctly identified that foreign files don't appear in the plan text. The issue is that foreign files should never have been in `files_changed` in the first place.

---

## Section 3 — stop_prose Anatomy (row 17)

### Validator implementation (`validators.py:12-118`)

**Patterns** (`validators.py:12-16`):
```python
STOP_PROSE_PATTERNS = [
    re.compile(r"STOP\.", re.IGNORECASE),          # Pattern 0
    re.compile(r"wait for confirmation", re.IGNORECASE),  # Pattern 1
    re.compile(r"do not proceed", re.IGNORECASE),  # Pattern 2
]
```

**Body scan scoping** (`validators.py:76-117`):
- Only scans lines inside step bodies (after `## STEP N` headers)
- Skips fenced code blocks (````...````)
- Skips `**Deposits:**` blocks (from marker through consecutive bullet lines)
- Strips inline backtick content before matching (`re.sub(r'`[^`]*`', '', line)`)
- Dispatches only for `dispatch_mode == "bellows"` plans

**Severity:** `warn` only — does not reject plans or block dispatch. Informational noise.

### Observed FP classes from terminal log corpus (2026-05-28 through 2026-06-12)

**Class 1: PLANNER_TEMPLATE step-boundary language** (Pattern 0: `STOP\.`)
- Fires on the canonical `**STOP. Do NOT proceed to Step N. Do NOT move the plan to Done. Wait for CEO verdict before continuing.**` block prescribed by PLANNER_TEMPLATE for multi-step Bellows-mode executables.
- **Occurrences:** 16+ across logs from 2026-05-29, 2026-05-31, 2026-06-01, 2026-06-02, 2026-06-04, 2026-06-05, 2026-06-06, 2026-06-08. Most frequent FP class.
- **Why exclusions miss it:** The block is not inside fenced code or `**Deposits:**`. It appears in plain step-body prose. No existing exclusion covers it.
- **Genuinely dangerous under Bellows dispatch?** No. Under Bellows dispatch, the daemon controls step pauses via `pause_for_verdict: always/after_step_1` in the plan header. The STOP prose is advisory text from a legacy manual_bootstrap pattern. Agents under Bellows dispatch cannot act on it — the daemon terminates the session after each step and manages the step sequence.
- Archive context: BACKLOG-ARCHIVE 2026-05-29 (PLANNER_TEMPLATE step-control language), FORWARD row 11.

**Class 2: Error-handling/instructional prose** (Pattern 0: `STOP\.`)
- Fires on sentence-final "stop." in instructional context: "capture the full traceback and STOP." / "Any failure -> flag and stop." / "STOP. Do NOT fix anything."
- **Occurrences:** 2026-06-03 ("flag and stop."), 2026-06-08 ("traceback and STOP."), 2026-06-02 ("STOP. Do NOT fix anything."), 2026-06-05/06 ("Before starting, read... STOP.")
- **Why exclusions miss it:** Same as Class 1 — plain step-body prose, no fence or deposit block.
- **Genuinely dangerous?** No. These are instructions to the agent about error handling, not step-boundary control directives. An agent that encounters an error and stops is working as intended; the `STOP.` is advice on what to do on error, not a directive to halt before starting.
- Archive context: BACKLOG-ARCHIVE 2026-06-08 (`stop_prose WARN on legitimate error-handling prose`), FORWARD row 17.

**Class 3: Rule 20 / QA instructional prose** (Pattern 2: `do not proceed`)
- Fires on "If the block prints FAILED, do not proceed with closure" in Rule 20 evidence instructions, and on instructional prose in QA/diagnostic step bodies like "MANDATORY — READ THIS FIRST" blocks containing "do not proceed."
- **Occurrences:** 2026-05-28 (Rule 20 prose), 2026-06-06 (instructional), 2026-06-11 (x2, MANDATORY blocks), 2026-06-12 (x2, including this diagnostic's own step text matching on "check_stop_prose").
- **Why exclusions miss it:** The `do not proceed` pattern matches substrings with no positional, syntactic, or context awareness. Lines starting with `>` (blockquote-prefixed instructional prose) are not excluded.
- **Genuinely dangerous?** No. These are conditional instructions ("if X fails, do not proceed") or references to the validator itself. Not step-control directives.
- Archive context: BACKLOG-ARCHIVE 2026-05-28, FORWARD row 8.

**Class 4: Self-referencing prose** (Pattern 2: `do not proceed`)
- Fires on this very diagnostic's step text when it references `check_stop_prose` patterns. Observed 2026-06-12 17:29:31 on diagnostic-draft-172855 (this plan).
- **Genuinely dangerous?** Definitionally no — the validator is flagging its own investigation prompt.

### True-positive census

**Has `stop_prose` EVER fired on a genuinely dangerous plan?** No. Across the complete terminal log corpus (2026-05-28 through 2026-06-12, ~26 matches), every single match is a false positive. All matches fall into the four classes above: PLANNER_TEMPLATE step-boundary blocks, error-handling prose, instructional/conditional prose, or self-referencing prose. Zero true positives have been recorded.

**Has Pattern 1 (`wait for confirmation`) ever fired?** No matches found in any terminal log file. The pattern has zero recorded activations, true or false positive.

---

## Section 4 — Fix Shapes

### (a) Row 21 — In-place diff contamination

**Option A: Snapshot merge-base at creation, diff against it.**
When `_create_worktree` falls back to in-place mode, record the current HEAD SHA as a per-plan baseline. At diff time, use this baseline instead of the re-captured HEAD. This isolates each plan's diff to changes since its own start, regardless of concurrent plan commits.

- **Blast radius:** Small — adds a field to the plan execution context; modifies `_capture_git_diff` callsite to use stored baseline in in-place mode.
- **Limitation:** Does NOT isolate the diff from concurrent plan's uncommitted changes. If plan 19 edits files without committing, those edits are visible in plan 20's working tree and would appear in the diff. Only isolates against committed changes.
- **Test strategy:** Unit test with two simulated in-place plans: plan B commits after plan A's pre_diff capture; verify plan A's files_changed excludes plan B's files.

**Option B: Serialize same-repo in-place plans.**
When a project is in in-place mode (no `.git`), only allow one plan to execute at a time. Queue additional plans until the current one completes.

- **Blast radius:** Medium — modifies the plan dispatch logic; reduces parallelism for non-`.git` projects.
- **Limitation:** Eliminates the contamination entirely but at the cost of throughput. Projects without `.git` can't benefit from parallel execution.
- **Test strategy:** Integration test verifying queuing behavior when two plans target the same project without `.git`.

**Option C: Filter files_changed to paths the plan's own agent touched.**
After computing `files_changed`, filter it against `git log <pre_diff_sha>..HEAD --name-only` to keep only files that the current branch (in-place: current agent's commits) actually modified.

- **Blast radius:** Small — adds a filter step to `_parse_diff_stat`.
- **Limitation:** Requires agents to commit their changes. Uncommitted agent changes appear in the diff but not in `git log`, so they'd be filtered OUT as well — false negative. Also, in in-place mode there's no branch distinction; all commits go to the same branch.
- **Test strategy:** Unit test with in-place execution verifying filter correctness.

**Recommendation: Option A** — snapshot the pre_diff SHA at plan start and reuse it consistently, rather than re-capturing HEAD (which advances with concurrent commits). This is the simplest change with the narrowest blast radius and addresses the specific contamination mechanism observed. The limitation (uncommitted concurrent changes still visible) is acceptable because agents under Bellows dispatch commit during step execution as standard practice.

### (b) Row 16 — Continuous-run diff accumulation

The scope_check side of row 16 is already FIXED by the union-text change (commit `706fbe7`, 2026-06-10). The residual diff-accumulation side is a narrow edge case:

**Option A: Reset pre_diff after auto_stage_deposits.**
In the continuous-run path at `bellows.py:644`, move the `pre_diff = _capture_git_diff(wt_path)` call to AFTER `_auto_stage_deposits` (which runs at line 682-683). Currently, pre_diff for the next step is captured before auto_stage_deposits for the current step. If auto_stage_deposits commits files, the pre_diff should reflect that commit.

- **Blast radius:** Minimal — reorders two existing calls.
- **Test strategy:** Unit test with continuous-run plan where step 1 produces uncommitted files; verify step 2's files_changed excludes step 1's files.

**Option B: No change — accept as mitigated.**
The union-text fix handles the scope_check side. The diff-accumulation side only triggers when agents don't commit, which is already mitigated by `_auto_stage_deposits`. The residual case (uncommitted non-deposit files) is rare and the scope_check would pass them anyway (union text covers all steps).

**Recommendation: Option B** — no change needed. The scope_check union-text fix (2026-06-10) addresses the gate FP that FORWARD row 16 describes. The diff-accumulation edge case is mitigated by auto_stage_deposits and standard agent commit behavior. Row 16 can be closed referencing commit `706fbe7`.

### (c) Row 17 — stop_prose false positives

**Option A: Narrow patterns to imperative-at-line-start forms.**
Replace broad patterns with positional variants: `STOP\.` becomes `^\s*(?:>\s*)*\*{0,2}\s*STOP\.` (requires STOP to appear at or near line start, after optional blockquote/bold markers). `do not proceed` becomes `^\s*(?:>\s*)*(?:Do )?[Nn]ot proceed` (imperative form at line start only). This excludes sentence-final "stop." and conditional "if X, do not proceed" constructions.

- **Blast radius:** Small — regex changes in `validators.py:12-16`.
- **Risk:** May miss genuinely dangerous STOP directives that appear mid-sentence. Given zero true positives in the census, this risk is theoretical.
- **Test strategy:** Unit tests covering all 4 FP classes (verify they no longer fire) + a positive test with a genuinely dangerous directive at line start.

**Option B: Add instructional-context exclusions.**
Keep existing patterns but add exclusions: skip lines prefixed with `>` (blockquote), skip lines containing "if" before the pattern (conditional context), skip lines containing known template blocks (the `**STOP. Do NOT proceed to Step N...` canonical form).

- **Blast radius:** Medium — more exclusion logic, higher complexity in `check_stop_prose`.
- **Risk:** Each exclusion is a special case; new FP classes may emerge that require new exclusions.
- **Test strategy:** Unit tests for each exclusion rule.

**Option C: Demote to INFO / remove patterns with zero true positives.**
Given the census shows zero true positives across the entire operational history, either: (C1) demote `stop_prose` from `warn` to a debug-level log, or (C2) remove patterns that have never caught a true positive (all three qualify, but Pattern 1 `wait for confirmation` has zero activations of any kind).

- **Blast radius:** Small — severity change or pattern removal.
- **Risk for C2:** Removing Pattern 0 (`STOP\.`) eliminates the safety net for a class of genuinely dangerous stop directive. However, under Bellows dispatch, the daemon controls step execution; agent-side STOP directives are mechanically irrelevant because the daemon terminates the session after each step regardless.
- **Test strategy:** C1: verify log output level change. C2: verify removed patterns no longer fire.

**Recommendation: Combination of A + C2.** Narrow Patterns 0 and 2 to imperative-at-line-start forms (Option A), and remove Pattern 1 (`wait for confirmation`) which has zero activations of any kind (Option C2). This eliminates all observed FP classes while retaining a meaningful (if narrower) safety net for Patterns 0 and 2. The narrowed patterns would catch a genuine `STOP.` directive at line start (the only position where it could be a step-control command) while excluding the sentence-final and conditional false positives.

### Shipping strategy: one executable or two?

**Recommendation: Two separate executables.**

The diff-pipeline fix (row 21, Option A) touches `bellows.py` — the core execution engine. The validator fix (row 17, Options A+C2) touches `validators.py` — a claim-time validator with no runtime coupling to the diff pipeline. Different files, different risk classes, different test surfaces. Shipping them separately allows independent QA and rollback:

1. **Executable 1:** Row 21 in-place diff contamination fix (`bellows.py` — pre_diff baseline snapshot)
2. **Executable 2:** Row 17 stop_prose pattern narrowing (`validators.py` — pattern regex changes + Pattern 1 removal)

Row 16 requires no executable (scope_check side already fixed; recommend closing the FORWARD entry).

---

## Section 5 — Gap Assessment + Verification Blocks

### Gap Assessment

| Gap | Current State (file:line) | Proposed State | Change Required |
|-----|---------------------------|----------------|-----------------|
| In-place diff contamination (row 21) | `_capture_git_diff` returns live HEAD at each callsite (`bellows.py:534`, `bellows.py:644`); no per-plan baseline isolation | Per-plan baseline SHA stored at dispatch start; reused for all diff captures in in-place mode | Modify `run_plan` to store initial pre_diff and pass to diff capture in in-place mode |
| scope_check union text (row 16) | FIXED: `_gate_scope_check` builds union of all step texts (`gates.py:701-709`, commit `706fbe7`) | Already in proposed state | None — close FORWARD row 16 |
| `STOP\.` pattern FPs (row 17, Class 1+2) | Broad `STOP\.` regex matches anywhere in line (`validators.py:13`) | Narrowed to imperative-at-line-start form | Regex change at `validators.py:13` |
| `do not proceed` pattern FPs (row 17, Class 3+4) | Broad substring match anywhere in line (`validators.py:15`) | Narrowed to imperative-at-line-start form | Regex change at `validators.py:15` |
| `wait for confirmation` pattern (row 17) | Pattern exists, zero activations ever (`validators.py:14`) | Removed — zero signal, only potential noise | Remove pattern at `validators.py:14` |
| FORWARD row 8 (`stop_prose` on Rule 20 prose) | Open, overlaps with row 17 Class 3 | Closed by row 17 fix | Close FORWARD row 8 as subsumed |
| FORWARD row 11 (`stop_prose` on PLANNER_TEMPLATE language) | Open, overlaps with row 17 Class 1 | Closed by row 17 fix | Close FORWARD row 11 as subsumed |

### Verification Blocks

| Claim | Query | Expected Output |
|-------|-------|-----------------|
| `_capture_git_diff` returns HEAD SHA via `git rev-parse HEAD` | `grep -n "rev-parse HEAD" bellows.py` | Line 815: `["git", "--no-pager", "rev-parse", "HEAD"]` |
| Plan 20 ran in-place (no worktree) | `grep "governance has no project-local .git" bellows-2026-06-12.log \| grep "\[20\]"` | `15:00:26 [WARN] [20] governance has no project-local .git — running in-place without worktree isolation` |
| Plan 19 step 3 committed between plan 20's pre_diff and gate | `grep "executable-19.*gates step 3" bellows-2026-06-12.log` | `15:04:34 [EVENT] [executable-19] gates step 3: passed=True, failures=0 (none), files_changed=5` — between 15:00:26 (plan 20 pre_diff) and 15:10:52 (plan 20 gate) |
| Teardown is no-op in in-place mode | `grep -n "wt_path == project_path" bellows.py \| grep teardown` | Line 1098: `if wt_path == project_path:` → return [] |
| scope_check union-text fix shipped | `git log --oneline --grep="union-of-all-step-texts" -- gates.py` | `706fbe7 feat(gates): scope_check union-of-all-step-texts fix` (2026-06-10) |
| `STOP\.` pattern fires on step-boundary blocks | `grep "STOP\\\." bellows-*.log \| grep "Do NOT proceed to Step"` | 16+ matches across 2026-05-29 through 2026-06-08 |
| `do not proceed` pattern fires on Rule 20 prose | `grep "do not proceed" bellows-2026-05-28.log \| grep stop_prose` | 1 match: "do not proceed with closure" |
| `do not proceed` fires on QA instructional prose | `grep "do not proceed" bellows-2026-06-12.log \| grep stop_prose` | 2 matches: "Part A — stands-alone" and "Section 3 — stop_prose anatomy" |
| `wait for confirmation` pattern has zero activations | `grep -r "wait for confirmation" bellows/logs/terminal/*.log \| grep stop_prose` | 0 matches |
| Zero true positives for stop_prose in entire operational history | `grep -c "stop_prose" bellows/logs/terminal/*.log \| awk -F: '{s+=$2}END{print s}'` | ~26 total matches, all FP per class analysis |

### CEO Decision Forks

**Decision 1: Row 21 fix shape**
- **Option A (recommended):** Snapshot pre_diff at plan start, reuse in in-place mode — narrow blast radius, addresses observed mechanism.
- Option B: Serialize same-repo in-place plans — eliminates contamination but reduces throughput.
- Option C: Filter files_changed via git log — fragile in in-place mode (no branch distinction).

**Decision 2: Row 16 disposition**
- **Recommended: Close FORWARD row 16** — scope_check union-text fix (commit `706fbe7`, 2026-06-10) addresses the gate FP described in the row. Residual diff-accumulation edge case is mitigated and not observed post-fix.

**Decision 3: Row 17 fix shape**
- **Recommended: Combination A+C2** — narrow Patterns 0 and 2 to imperative-at-line-start, remove Pattern 1 (zero activations). Eliminates all 4 FP classes, retains meaningful safety net.
- Alternative: Option C1 (demote to INFO) — cheaper but retains log noise.
- Alternative: Option B (add context exclusions) — higher complexity, whack-a-mole risk.

**Decision 4: Rows 8 + 11 disposition**
- **Recommended: Close FORWARD rows 8 and 11** as subsumed by row 17 fix. Row 8 (`stop_prose` on Rule 20 prose = Class 3 FP) and row 11 (`stop_prose` on PLANNER_TEMPLATE language = Class 1 FP) are both instances of the same pattern-broadness problem addressed by the row 17 fix.

**Decision 5: Shipping strategy**
- **Recommended: Two separate executables** — diff-pipeline fix (row 21, `bellows.py`) and validator fix (row 17, `validators.py`) are independent risk surfaces. Ship and QA separately.

---

## Output Receipt
**Agent:** Bellows Systems Analyst
**Step:** 1 (SA)
**Status:** Complete

### What Was Done
Root-cause analysis of three FORWARD-register gate false-positive entries (rows 16/17/21). Traced the diff-capture pipeline, scope_check semantics, and stop_prose validator against live 2026-06-12 incident data and the complete terminal log corpus. Produced fix shape recommendations per problem with verification blocks.

### Files Deposited
- `bellows/knowledge/research/gate-fp-cluster-root-cause-2026-06-12.md` — root-cause diagnostic with 5 sections covering diff-pipeline anatomy, scope_check semantics, stop_prose FP taxonomy, fix shapes, and gap assessment

### Files Created or Modified (Code)
- None (investigation only, per diagnostic scope)

### Decisions Made
- Classified plan 10 (2026-06-12) as TRUE positive, authoring-caused; plan 20 as FALSE positive, mechanism-caused (in-place diff contamination)
- Identified in-place (no-worktree) execution as the contamination vector, distinct from worktree-isolated execution
- Confirmed scope_check union-text fix (commit 706fbe7, 2026-06-10) addresses FORWARD row 16
- Completed true-positive census for stop_prose: zero true positives across entire operational history

### Flags for CEO
- Five decision forks presented in Section 5 requiring CEO disposition

### Flags for Next Step
- None (single-step diagnostic)
