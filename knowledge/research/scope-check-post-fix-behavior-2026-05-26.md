# Scope_Check Post-Fix Behavior Characterization

**Date:** 2026-05-26 | **Agent:** Bellows Systems Analyst
**Plan:** diagnostic-scope-check-post-fix-behavior-2026-05-26
**Step:** 1 (SA)

---

## Q1 — `_gate_scope_check` Current Code Shape

### `_gate_scope_check` (gates.py lines 600–625)

```python
def _gate_scope_check(plan_text, step_number, files_changed, failures):
    if not files_changed:
        return

    # Extract the step's section from the plan
    step_text = _extract_step_text(plan_text, step_number)
    if not step_text:
        return

    out_of_scope = []
    for fpath in files_changed:
        basename = os.path.basename(fpath)
        if basename in SCOPE_ALLOWLIST:
            continue
        if any(basename.startswith(p) for p in SCOPE_ALLOWLIST_PREFIXES):
            continue
        if fpath in step_text or basename in step_text:
            continue
        out_of_scope.append(fpath)

    if out_of_scope:
        context = step_text[:200]
        failures.append({
            "gate": "scope_check",
            "evidence": f"out-of-scope files: {', '.join(out_of_scope)} | plan step context: {context}",
        })
```

#### (a) How it determines what's in-scope

Three exemption tiers, evaluated in order:
1. **Basename in `SCOPE_ALLOWLIST`** (line 612): exact-match against `["agent-prompt-feedback.md", "PROJECT_STATUS.md", ".gitkeep"]`
2. **Basename prefix in `SCOPE_ALLOWLIST_PREFIXES`** (line 614): starts-with match against `("in-progress-", "verdict-pending-", "halted-")`
3. **Text mention** (line 616): `fpath in step_text or basename in step_text` — the full relative path OR the basename must appear verbatim in the extracted step text

If none of the three tiers match, the file is flagged as out-of-scope.

#### (b) Data consumed

- `plan_text` — full plan file content (used to extract step text via `_extract_step_text`)
- `step_number` — current step index
- `files_changed` — list of relative file paths from `_parse_diff_stat`
- `failures` — mutable list to append gate failure dicts

#### (c) Exemptions

- `SCOPE_ALLOWLIST` (line 23–27): three exact basenames
- `SCOPE_ALLOWLIST_PREFIXES` (line 30): three lifecycle prefixes — `in-progress-`, `verdict-pending-`, `halted-`
- Text-mention fallback: any file whose path or basename appears in the step's prose

**Notable absences from SCOPE_ALLOWLIST_PREFIXES:** `executable-`, `diagnostic-`, `qa-` prefixes are NOT exempted. These are pre-claim prefixes that shouldn't appear in `files_changed` under normal operation because plan files are not committed to git.

### Post-fix `_capture_git_diff` (bellows.py lines 678–699)

```python
def _capture_git_diff(project_path: str) -> str:
    """Capture the current HEAD commit SHA, scoped to the directory at project_path.
    ...
    """
    try:
        result = subprocess.run(
            ["git", "--no-pager", "rev-parse", "HEAD"],
            cwd=project_path, capture_output=True, text=True, timeout=10,
        )
        if result.returncode != 0:
            return ""
        return result.stdout.strip()
    except Exception:
        return ""
```

Post-fix: returns **HEAD SHA** (a commit hash string), not diff output. Prior implementation returned `git diff --stat` output which was blind to committed changes.

### Post-fix `_parse_diff_stat` (bellows.py lines 702–755)

```python
def _parse_diff_stat(post_diff: str, pre_diff: str, project_path: Optional[str] = None) -> list:
    """Return list of files changed between pre_diff (HEAD SHA before step) and the
    current working-tree state, scoped to project_path.

    Uses `git diff --stat --relative <pre_diff> -- .` (run with cwd=project_path)
    which captures BOTH committed and uncommitted changes since pre_diff.
    ...
    """
    if not pre_diff:
        return []
    cwd = project_path if project_path else None
    try:
        result = subprocess.run(
            ["git", "--no-pager", "diff", "--stat", "--relative", pre_diff, "--", "."],
            cwd=cwd, capture_output=True, text=True, timeout=10,
        )
    except Exception:
        return []
    if result.returncode != 0:
        return []

    changed = []
    for line in result.stdout.strip().splitlines():
        line = line.strip()
        if "|" not in line:
            continue
        filename, _stat = line.split("|", 1)
        filename = filename.strip()
        if not filename:
            continue
        changed.append(filename)

    if project_path is not None:
        changed = [
            f for f in changed
            if ".." not in os.path.normpath(f).split(os.sep)
        ]

    return sorted(changed)
```

Post-fix: runs `git diff --stat --relative <pre_SHA> -- .` with `cwd=wt_path`, capturing both committed and uncommitted changes since the pre-step SHA. This is the fix for the file_change_audit false-negative documented in `knowledge/research/file-change-audit-false-negative-2026-05-25.md`.

**What `files_changed` now contains:** A sorted list of project-relative file paths changed between the pre-step HEAD SHA and the current worktree state (including committed changes). The `--relative` flag ensures paths are relative to the worktree root. The `..` filter excludes files outside the project.

---

## Q2 — Post-Restart Dispatch Population

### Accessible verdict files

**Finding: Zero 2026-05-26 verdict files are accessible from this worktree.**

The worktree is checked out from HEAD (`f746e83`). Verdict files for the 2026-05-26 dispatches are runtime artifacts created by the Bellows daemon in the main repo's working directory. They are not committed to git and exist only in the main repo's filesystem at `verdicts/resolved/`.

### Evidence from git history

Two plans dispatched since the daemon restart have committed artifacts:

| # | Plan | Commit | Artifact | Type |
|---|---|---|---|---|
| 1 | `diagnostic-parallel-sha-population-audit-2026-05-26` | `abc0241` | `knowledge/research/parallel-sha-population-audit-2026-05-26.md` | Research file (201 lines) |
| 2 | `executable-planner-template-rule-21-contract-change-2026-05-26` | `f746e83` | `knowledge/development/planner-template-rule-21-contract-change-2026-05-26.md` | Dev log (52 lines) |

**Scope_check trip data — NOT verifiable.** The CEO Context states the Rule 21 plan "tripped scope_check at Step 1 (DOC)." I cannot independently verify this claim because:
- No `processed-verdict-*-2026-05-26-*` files exist in this worktree
- No halted plan files for 2026-05-26 exist in `knowledge/decisions/Done/`
- The verdict files are in the main repo's uncommitted working directory

**Audit window assessment:** With only 2 plans dispatched and 0 accessible verdict files, the audit window is **too narrow to characterize population behavior**. Recommend a future-rerun trigger after a session with 5+ plans dispatched post-fix, with verdict files committed via session-wrap.

### Indirect evidence from the file-change-audit-fix verdict (pre-fix)

The Step 2 QA verdict for `executable-file-change-audit-fix-2026-05-25` (accessible at `verdicts/resolved/processed-verdict-file-change-audit-fix-2026-05-25-step-2.md`) confirms:
- Pre-fix: `file_change_audit` always reported `0 files modified`
- Pre-fix: `_gate_scope_check` short-circuited on every step (`if not files_changed: return`)
- Post-fix: `files_changed` is now non-empty for steps with real changes
- Post-fix: `_gate_scope_check` will run on every code-edit step

---

## Q3 — What Does scope_check Consider In-Scope?

### The in-scope predicate (gates.py lines 610–617)

```python
for fpath in files_changed:
    basename = os.path.basename(fpath)
    if basename in SCOPE_ALLOWLIST:          # Tier 1: exact basename match
        continue
    if any(basename.startswith(p) for p in SCOPE_ALLOWLIST_PREFIXES):  # Tier 2: prefix match
        continue
    if fpath in step_text or basename in step_text:  # Tier 3: text mention
        continue
    out_of_scope.append(fpath)
```

### Q3 sub-questions answered

**Does scope_check read the plan's `**Deposits:**` block?**
No. It reads the *entire step text* extracted by `_extract_step_text(plan_text, step_number)` (line 605). The Deposits block is included because it's part of the step text, but scope_check does not parse it structurally — it performs a raw substring match (`fpath in step_text or basename in step_text`).

**Does it use the step prose to extract path references?**
No structured extraction. It uses raw `in` substring matching against the full step text. This means a file matches if its full relative path OR its basename appears ANYWHERE in the step text — including inside prose descriptions, code examples, or comments.

**Does it have a hardcoded list of always-exempt patterns?**
Yes: `SCOPE_ALLOWLIST` (3 exact basenames) and `SCOPE_ALLOWLIST_PREFIXES` (3 lifecycle prefixes). These are defined at module level (lines 23–30) and apply regardless of step text content.

**Does it cross-reference against `Files Created or Modified` in agent output receipts?**
No. Scope_check does not read the agent's output at all. It only reads `plan_text` (the Planner's instructions) and `files_changed` (the git diff). This is intentional per the Layer 1 / Layer 3 boundary: Bellows does not interpret agent output, only mechanical file-system state.

### Key observation: the text-mention predicate is coarse

The predicate `fpath in step_text or basename in step_text` has two consequences:
1. **False negatives (under-flagging):** A file path appearing in unrelated prose (e.g., "do not modify `foo.py`") exempts the file even if it wasn't supposed to be modified.
2. **False positives (over-flagging):** A legitimate deposit whose path is NOT mentioned anywhere in the step text (e.g., because the Deposits block uses a different path form) gets flagged as out-of-scope.

---

## Q4 — Plan-File Rename: Structurally Exempt or Not?

### Critical finding: the plan-file rename does NOT appear in `files_changed`

The CEO Context hypothesis — that `files_changed` contains the plan-file rename — is **structurally impossible** under the current architecture:

1. **Plan files are never committed to git.** `git log --all -- "knowledge/decisions/*planner-template-rule-21*"` returns zero results. Plan files are lifecycle artifacts managed as untracked files in the main repo's working directory.

2. **The rename happens outside the worktree.** The claim rename at `bellows.py:402` (`shutil.move(plan_path, inprogress_path)`) operates on the main repo's `knowledge/decisions/` directory. The worktree is created AFTER the rename at `bellows.py:433` and has its own separate checkout.

3. **`_parse_diff_stat` runs `git diff --stat --relative <SHA> -- .` with `cwd=wt_path`.** This captures changes in the WORKTREE only. Untracked file renames in the main repo are invisible to this command.

4. **Even if the rename WERE visible**, `SCOPE_ALLOWLIST_PREFIXES` already covers `in-progress-*`. Tests confirm this: `test_scope_check_prefix_allowlist_in_progress` (test_gates.py:387–391) passes.

### What DID trip scope_check?

Based on code analysis, the file that likely tripped scope_check for the Rule 21 plan is:

**`knowledge/development/planner-template-rule-21-contract-change-2026-05-26.md`**

This is the dev log deposit committed by the agent. Its basename `planner-template-rule-21-contract-change-2026-05-26.md` visually resembles the plan filename (minus the `executable-` prefix), which likely caused the CEO Context to describe it as "the plan file's own claim rename."

The scope_check would flag this file if the step text does not contain either:
- The full path `knowledge/development/planner-template-rule-21-contract-change-2026-05-26.md`
- The basename `planner-template-rule-21-contract-change-2026-05-26.md`

**Cannot definitively confirm** without access to the pristine plan file (not committed to git, not in shadow cache of this worktree). However, this is the only plausible explanation given the architecture analysis.

### Existing exemptions searched

Searched `gates.py` for `in-progress-`, `verdict-pending-`, `executable-`, `diagnostic-`, and lifecycle prefix patterns:
- `SCOPE_ALLOWLIST_PREFIXES` at line 30: `("in-progress-", "verdict-pending-", "halted-")` — covers post-claim lifecycle prefixes
- No exemption for `executable-`, `diagnostic-`, or `qa-` prefixes (pre-claim prefixes that shouldn't appear in `files_changed`)
- No exemption for `knowledge/development/` directory paths
- No exemption for deposit paths that match the plan slug

---

## Q5 — Other Lifecycle Artifacts at Risk

| Artifact | Owner | Timing | In worktree? | In `files_changed`? | Risk |
|---|---|---|---|---|---|
| Plan rename (`executable-*` → `in-progress-*`) | Bellows | Pre-step (line 402) | No — main repo only, untracked | **No** — untracked, outside worktree | None |
| Plan rename (`in-progress-*` → `verdict-pending-*`) | Bellows | Post-step (line 528) | No — main repo only | **No** — after gates run | None |
| Verdict request files | Bellows | Post-step (via `verdict.post_verdict_request`) | No — written to `verdicts/pending/` in main repo | **No** — after gates run | None |
| Processed-verdict renames | Bellows | During `_consume_verdicts` | No — `verdicts/resolved/` in main repo | **No** — separate poll cycle | None |
| Shadow cache writes (`.bellows-cache/`) | Bellows | At claim (line 404–405) | No — `.bellows-cache/` in main repo | **No** — `.bellows-cache/` not in worktree checkout | None |
| Agent commits (code changes, deposits) | Agent | During step | **Yes** — worktree is agent's workspace | **Yes** — this is the intended population | Scope_check validates these |
| `agent-prompt-feedback.md` | Agent | During step | Yes | Yes, but **allowlisted** | None |
| Dev log deposits (`knowledge/development/*`) | Agent | During step | Yes | **Yes** — must pass text-mention predicate | **At risk** if step text omits the path |
| Research deposits (`knowledge/research/*`) | Agent | During step | Yes | **Yes** — must pass text-mention predicate | **At risk** if step text omits the path |

### Summary

The only lifecycle artifacts at risk of false-positive scope_check trips are **agent-deposited knowledge files** whose paths are not mentioned in the plan step text. This is NOT a lifecycle-prefix issue — `SCOPE_ALLOWLIST_PREFIXES` already handles all three post-claim lifecycle prefixes. The risk surface is:

1. **Dev logs** (`knowledge/development/*.md`) — created by DOC steps per Rule 8 split-commit pattern
2. **Research findings** (`knowledge/research/*.md`) — created by SA diagnostic steps
3. **Architecture decisions** (`knowledge/architecture/*.md`) — created by SA design steps

All of these should be declared in the step's `**Deposits:**` block, which would make them appear in the step text and pass the text-mention predicate. If the Planner omits the deposit path from the step text, scope_check flags it.

---

## Q6 — Fix-Shape Options

### Fix Shape A — Exempt `knowledge/` subtree from scope_check

```python
# In _gate_scope_check, after SCOPE_ALLOWLIST_PREFIXES check:
SCOPE_ALLOWLIST_DIRS = ("knowledge/",)

# ...inside the loop:
if any(fpath.startswith(d) for d in SCOPE_ALLOWLIST_DIRS):
    continue
```

- **LOC:** ~4 lines (constant + conditional)
- **Blast radius:** Low. Only affects scope_check. Could mask truly out-of-scope writes to `knowledge/` (e.g., agent writing to a different plan's research dir).
- **Trade-off:** Broadest exemption. Simple but sacrifices scope_check coverage for the entire knowledge tree.

### Fix Shape B — Exempt deposit paths extracted from the step's `**Deposits:**` block

```python
# In _gate_scope_check, extract deposits and normalize:
deposit_paths = _extract_plan_required_deposits(step_text)
deposit_basenames = {os.path.basename(p) for p in deposit_paths}
deposit_set = set(deposit_paths) | deposit_basenames

# ...inside the loop:
if fpath in deposit_set or basename in deposit_set:
    continue
```

- **LOC:** ~6 lines
- **Blast radius:** Low. Reuses existing `_extract_plan_required_deposits`. Only exempts files the plan explicitly declared as deposits.
- **Trade-off:** Tightest exemption — only plan-declared deposits are exempt. But if the Planner omits a deposit from the block, it still trips. Also creates a coupling between scope_check and deposit_exists (they'd both parse the same block).

### Fix Shape C — Exempt files whose basename matches the plan slug

```python
# Derive plan slug from plan filename:
plan_slug = _derive_slug_from_plan_text(plan_text)  # or pass as parameter

# ...inside the loop:
if plan_slug and plan_slug in basename:
    continue
```

- **LOC:** ~5 lines (slug derivation + conditional)
- **Blast radius:** Medium. Could suppress legitimate flags for files that happen to share the plan slug substring (e.g., an agent creating `plan-slug-extra.py`).
- **Trade-off:** Addresses the specific case where the deposit basename matches the plan slug (the Rule 21 scenario). But slug-substring matching is fragile and could over-exempt.

### Fix Shape D — Ensure plan step text always contains deposit paths (governance fix, not code)

No code change. Instead, update PLANNER_TEMPLATE to require every `**Deposits:**` block to list the full project-relative path. The scope_check text-mention predicate already passes when the path appears in step text.

- **LOC:** 0 (governance documentation only)
- **Blast radius:** None to code. Requires Planner compliance.
- **Trade-off:** Addresses root cause (Planner omitting deposit path from step text) rather than adding exemptions. But cannot be mechanically enforced — relies on Planner authoring discipline. If the Planner already does this consistently, this fix is redundant and the trip has a different root cause.

---

## Q7 — Disposition Recommendation

### **DESIGN-INTENT-AUDIT-NEEDED**

**Rationale:** The CEO Context hypothesis — that the plan-file rename trips scope_check — is **structurally incorrect**. Plan-file renames do not appear in `files_changed` because:
1. Plan files are untracked (never committed to git)
2. The rename happens in the main repo, not the worktree
3. `SCOPE_ALLOWLIST_PREFIXES` already exempts `in-progress-*` basenames

The actual trip cause is almost certainly the **dev log deposit** (`knowledge/development/planner-template-rule-21-contract-change-2026-05-26.md`) not passing the text-mention predicate in scope_check. This is either:
- **(a) A plan-authoring gap:** the Planner omitted the deposit path from the step text, causing scope_check to flag a legitimate deposit
- **(b) A scope_check design gap:** deposits declared in `**Deposits:**` blocks should be automatically exempt, but scope_check doesn't parse that block structurally

Determining which requires a follow-up diagnostic that:
1. Accesses the pristine plan file for the Rule 21 plan (from the main repo's shadow cache or the Planner's memory)
2. Examines whether the step text contains the dev log path
3. If it does: investigate why the text-mention predicate failed (path form mismatch? encoding issue?)
4. If it doesn't: determine whether this is a Planner authoring pattern that should be changed (Shape D) or a scope_check structural gap that should be closed (Shape B)

**Recommended follow-up shape:** SA diagnostic, scoped to the Rule 21 plan's pristine step text analysis. Requires access to the main repo's `.bellows-cache/` directory. If the plan text IS available from the main repo, the diagnostic could be completed in a single step. If not, recommend waiting until the next session-wrap commits the plan lifecycle artifacts, then re-running.

---

## Verification Blocks (Rule 39)

### Block 1 — Post-fix `_capture_git_diff` return shape

**Command (equivalent):** `grep -A 15 "def _capture_git_diff" bellows.py`

**Expected:** Function returns HEAD SHA + commit-range diff output.

**Actual:** Function returns HEAD SHA ONLY (via `git rev-parse HEAD`). It does NOT return diff output — the function name is anachronistic per the docstring: "diff in the name is now anachronistic but the contract change is necessary." The diff is computed separately by `_parse_diff_stat`, which takes the SHA as input and runs `git diff --stat --relative <SHA> -- .`.

**Materiality:** CONFIRMED. `files_changed` is populated from `_parse_diff_stat(post_diff, pre_diff, wt_path)` where `pre_diff` is the pre-step HEAD SHA. The diff captures all committed AND uncommitted changes in the worktree since the pre-step SHA.

### Block 2 — `_gate_scope_check` in-scope predicate

**Command (equivalent):** `grep -B 2 -A 30 "def _gate_scope_check" gates.py`

**Expected:** Function with in-scope predicate.

**Actual:** Full function body quoted in Q1 above (lines 600–625). The predicate is a three-tier cascade:
1. `basename in SCOPE_ALLOWLIST` (line 612)
2. `any(basename.startswith(p) for p in SCOPE_ALLOWLIST_PREFIXES)` (line 614)
3. `fpath in step_text or basename in step_text` (line 616)

**Materiality:** CONFIRMED. The predicate is clear and mechanically verifiable. The text-mention tier is the only dynamic predicate — it depends on plan step content authored by the Planner.

### Block 3 — Post-restart scope_check trip count

**Command:** List every `processed-verdict-*-2026-05-26-step-*.md` file in `verdicts/resolved/` AND any `halted-*-2026-05-26-*.md` files in `knowledge/decisions/Done/`.

**Expected:** Trip count = N (from audit).

**Actual:** **Trip count = INDETERMINATE.** Zero `processed-verdict-*2026-05-26*` files found in this worktree's `verdicts/resolved/`. Zero `halted-*2026-05-26*` files found in `knowledge/decisions/Done/`. The 2026-05-26 verdict files are runtime artifacts in the main repo's working directory, not committed to git and not accessible from this worktree.

**Indirect evidence:** The CEO Context states 1 trip (Rule 21 plan). The parallel-SHA diagnostic plan (`abc0241`) completed successfully (its research file was committed with no scope_check-related issues noted). The Rule 21 plan also completed (dev log committed at `f746e83`), suggesting the Planner overrode the scope_check failure with a `continue` verdict.

**Materiality:** PARTIAL. Cannot independently verify the trip count. The CEO Context claim of 1 trip is consistent with the indirect evidence but unverified.

---

## Side-Findings

### Side-finding 1: CEO Context hypothesis is structurally incorrect

The diagnostic's framing question assumes `files_changed` contains the plan-file rename. This is impossible given the architecture:
- Plan files are untracked filesystem artifacts, invisible to `git diff`
- The rename operates on the main repo, not the worktree where `git diff` runs
- `SCOPE_ALLOWLIST_PREFIXES` already handles `in-progress-*` basenames

The actual trip mechanism is the **text-mention predicate** failing for a legitimate deposit, not a lifecycle prefix gap. This reframes the fix from "add more lifecycle prefixes" to "ensure deposits are always text-mentioned or structurally exempt."

### Side-finding 2: `SCOPE_ALLOWLIST_PREFIXES` already provides comprehensive lifecycle coverage

The prefix tuple `("in-progress-", "verdict-pending-", "halted-")` covers all three post-claim lifecycle states. Tests exist for all three (test_gates.py lines 387–413). No additional lifecycle prefix exemptions are needed.

### Side-finding 3: `knowledge/development/` deposits are a recurring scope_check risk

DOC steps (Rule 8 split-commit pattern) always deposit to `knowledge/development/`. If the Planner's step text doesn't mention this path, scope_check will flag it on every DOC step. This is a systemic pattern, not a one-off incident.

---

## Output Receipt

**Agent:** Bellows Systems Analyst
**Step:** 1
**Status:** Complete

### What Was Done

Comprehensive characterization of `_gate_scope_check` post-fix behavior. Analyzed the gate's code shape, traced the data flow from `_capture_git_diff` through `_parse_diff_stat` to `files_changed`, enumerated all lifecycle artifacts that could trigger false-positive scope_check trips, proposed four fix shapes, and discovered that the CEO Context hypothesis (plan-file rename in `files_changed`) is structurally impossible — the actual trip cause is the text-mention predicate failing for a deposit file.

### Files Deposited

- `knowledge/research/scope-check-post-fix-behavior-2026-05-26.md` — findings file with seven Q&A sections, code citations, fix-shape proposals, three verification blocks, and three side-findings

### Files Created or Modified (Code)

- None (characterization audit, no source changes)

### Decisions Made

- Classified disposition as DESIGN-INTENT-AUDIT-NEEDED based on the finding that the root cause is ambiguous (plan-authoring gap vs. scope_check structural gap) without access to the pristine plan file
- Identified the actual trip mechanism (text-mention predicate on deposit path) rather than the hypothesized mechanism (lifecycle prefix gap)

### Flags for CEO

- **DESIGN-INTENT-AUDIT-NEEDED** — The plan-file rename does NOT trip scope_check (structurally impossible). The actual trip is the dev log deposit failing the text-mention predicate. A follow-up SA diagnostic is needed to examine the pristine plan step text (from main repo's shadow cache) to determine whether this is a Planner authoring gap or a scope_check design gap (Fix Shape B vs D).
- **Side-finding:** `knowledge/development/` deposits from DOC steps are a systemic scope_check risk if the Planner doesn't include the deposit path in step text. This will recur on every DOC step post-fix.

### Flags for Next Step

- None (single-step diagnostic)
