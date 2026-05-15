# Diagnostic: scope_check False Positives on Infrastructure Files
**Date:** 2026-04-16 | **Status:** Complete

---

## Q1 — How does scope_check work?

**Function:** `_gate_scope_check(plan_text, step_number, files_changed, failures)` in `gates.py:136`

**(a) Inputs:**
- `plan_text`: the full plan markdown string (passed from `gates.check()` which receives it from `run_plan()`)
- `step_number`: integer, the step just completed
- `files_changed`: a sorted list of file paths produced by `_parse_diff_stat(post_diff, pre_diff)`
- `failures`: mutable list; failures are appended to it (no return value)

**(b) How it determines "in scope":**
Two mechanisms:

1. **Allowlist** (`gates.py:8–12`): a module-level constant
   ```python
   SCOPE_ALLOWLIST = [
       "agent-prompt-feedback.md",
       "PROJECT_STATUS.md",
       ".gitkeep",
   ]
   ```
   Match is by `os.path.basename(fpath)` — exact basename equality.

2. **Step text substring search** (`gates.py:141–145`): Extracts the step section via
   ```python
   pattern = rf"## STEP {step_number}\b.*?(?=\n## STEP |\Z)"
   match = re.search(pattern, plan_text, re.DOTALL)
   step_text = match.group(0)
   ```
   Then for each file: `fpath in step_text or os.path.basename(fpath) in step_text`.
   This is a plain Python `in` substring check — no word boundaries, no path normalization.

**(c) Out-of-scope determination — literal logic (`gates.py:148–154`):**
```python
out_of_scope = []
for fpath in files_changed:
    basename = os.path.basename(fpath)
    if basename in SCOPE_ALLOWLIST:
        continue
    if fpath in step_text or basename in step_text:
        continue
    out_of_scope.append(fpath)
```
A file is flagged if: basename NOT in `SCOPE_ALLOWLIST` AND (full path NOT in step_text AND basename NOT in step_text).

---

## Q2 — What files trigger false positives and why?

### (a) `verdicts/ledger.jsonl`

**Is it git-tracked?** YES. It is not in `.gitignore`. `git status` shows it as ` M verdicts/ledger.jsonl` (second-column M = unstaged modification), confirming it is tracked.

**Why does it appear in `files_changed`?**
`_capture_git_diff(project_path)` runs `git diff --stat` (working tree vs index) from `project_path`. Since `ledger.jsonl` is tracked and modified (but never staged), it always shows in this output.

`verdict.log_to_ledger()` is called from `_consume_verdicts()` which is called from `_rescan()` in the **main thread**, running **concurrently** with the plan execution thread. So `ledger.jsonl` can be written between the `pre_diff` capture and the `post_diff` capture. `_parse_diff_stat` detects the change in stat line (bytes added) → includes `verdicts/ledger.jsonl` in `files_changed`.

Even when Bellows isn't consuming verdicts, the ledger grows across plan cycles, so its stat line is almost always different at post_diff vs pre_diff.

`ledger.jsonl` is NOT in `SCOPE_ALLOWLIST` and is never mentioned in step text → scope_check flags it on every plan.

### (b) Plan files (`in-progress-*.md`, `verdict-pending-*.md`)

**Are they git-tracked?** YES. `knowledge/decisions/` is not gitignored. Plan files are tracked when committed by agents.

**Why do they appear in `files_changed`?**
The standard agent execution pattern for diagnostics:
1. Agent claims the plan: `shutil.move(diagnostic-foo.md → in-progress-diagnostic-foo.md)` (OS-level, not staged)
2. Agent does all work
3. Agent commits all work (including claiming the in-progress file as tracked)
4. Agent moves plan to Done: `shutil.move(in-progress-diagnostic-foo.md → Done/diagnostic-foo.md)` (OS-level, unstaged)
5. Agent's step ends → Bellows captures `post_diff`

At step 5: `in-progress-diagnostic-foo.md` is **tracked** (was committed in step 3) but **deleted from disk** (moved to Done/ in step 4). This is an unstaged deletion — `git diff --stat` shows it as a modified file (deletion). `Done/diagnostic-foo.md` is untracked (`??`) and does NOT appear in `git diff --stat`.

So `in-progress-diagnostic-foo.md` lands in `files_changed` as a deletion. Its basename (`in-progress-...`) is NOT in `SCOPE_ALLOWLIST` and is typically not mentioned in step text → scope_check flags it.

The same mechanism applies to `verdict-pending-*` renames that happen WITHIN a subsequent step's execution window.

### (c) `knowledge/research/agent-prompt-feedback.md`

**Current status: already handled.** `SCOPE_ALLOWLIST` includes `"agent-prompt-feedback.md"`. Its basename matches, so it is skipped before the step-text check. This was presumably a false positive source before the allowlist was added — it is no longer a false positive with the current code.

The `agent-prompt-feedback.md` file IS in git status as ` M` (unstaged modification), and it WOULD appear in `files_changed`, but the allowlist catches it correctly.

---

## Q3 — Fix approaches

### Option A: Allowlist in scope_check (pattern-based)

Extend `SCOPE_ALLOWLIST` to support glob patterns for infrastructure files:
```python
SCOPE_ALLOWLIST_PATTERNS = [
    "agent-prompt-feedback.md",
    "PROJECT_STATUS.md",
    ".gitkeep",
    "ledger.jsonl",           # verdict audit log
]
SCOPE_ALLOWLIST_PREFIXES = [
    "in-progress-",
    "verdict-pending-",
    "halted-",
]
```
Then in `_gate_scope_check`, skip any file whose basename matches a pattern or prefix.

- **Lines of code:** ~8–10 lines added/changed in gates.py
- **Future-proofing:** NEW infrastructure files require a manual update to the allowlist. Pattern-based matching (prefixes) handles the family of renamed plan files without listing each one.
- **Suppression risk:** Low. Patterns are specific to known infrastructure naming conventions. A real scope violation using `in-progress-` as a filename is essentially impossible.

### Option B: Filter in `_parse_diff_stat`

Strip infrastructure files from the list before returning:
```python
INFRA_BASENAMES = {"ledger.jsonl"}
INFRA_PREFIXES = ("in-progress-", "verdict-pending-", "halted-")

def _parse_diff_stat(post_diff, pre_diff):
    ...
    changed = [f for f, s in post_map.items() if pre_map.get(f) != s]
    changed = [f for f in changed
               if os.path.basename(f) not in INFRA_BASENAMES
               and not os.path.basename(f).startswith(INFRA_PREFIXES)]
    return sorted(changed)
```

- **Lines of code:** ~8–10 lines in bellows.py
- **Future-proofing:** Same manual maintenance needed. Keeps scope_check itself clean.
- **Suppression risk:** Same as A. Moves filtering upstream and hides it from the gate log entirely (files won't appear in `gate_result["files_changed"]` at all).

### Option C: `.gitignore` for `ledger.jsonl`

`verdicts/ledger.jsonl` is operational data, not source. It can be safely untracked:
```bash
git rm --cached verdicts/ledger.jsonl
echo "verdicts/ledger.jsonl" >> .gitignore
```

After this, `ledger.jsonl` is untracked → never appears in `git diff --stat` → never in `files_changed`. No code changes needed. For plan files (`knowledge/decisions/`), gitignoring would be wrong — those ARE project artifacts and their moves should be tracked.

- **Lines of code:** 0 (a config change, not a code change)
- **Future-proofing:** Handles `ledger.jsonl` permanently without any code maintenance. New infrastructure files still need handling separately.
- **Suppression risk:** Zero — no code logic changed.

### Recommendation

**Option C for `ledger.jsonl` + Option A for plan files.**

`ledger.jsonl` should not be git-tracked — it is runtime operational data (like `bellows.db` which IS already gitignored). Untracking it + gitignoring it is the correct structural fix with zero code changes.

Plan files (`in-progress-*`, `verdict-pending-*`) require a pattern-based allowlist in `SCOPE_ALLOWLIST` (Option A) because they legitimately belong in git history. The pattern is stable (all renamed plans follow these prefixes, enforced by `is_runnable_plan()`), so there is no maintenance burden beyond new prefix types (which would require updating `is_runnable_plan` too, at which point the allowlist update is obvious).

Combined, the two fixes eliminate all three false positive sources with ~6 lines of code change and one gitignore entry.

---

## Q4 — Could scope_check be smarter about step context?

**(a) Recognizing `agent-prompt-feedback.md` as standard protocol:** Already handled by `SCOPE_ALLOWLIST`. No change needed.

**(b) Files outside the project directory:** `_capture_git_diff(project_path)` runs `git diff --stat` with `cwd=project_path`. Only files within that git repo appear. For Bellows plans, `project_path` IS the bellows root, so bellows' own infrastructure files (`verdicts/ledger.jsonl`, plan files in `knowledge/decisions/`) appear. For plans targeting external projects, bellows files would not appear. The problem is structural: Bellows plans run against the Bellows repo, making Bellows' own operational files subject to scope checking.

**(c) Distinguishing "agent modified this file" vs "Bellows modified it between pre/post diff":**

The diff-of-diffs approach in `_parse_diff_stat` was designed to exclude pre-existing dirty files, but it cannot distinguish WHO made a change during the execution window — only THAT a change occurred.

**Could Bellows track its own writes?** Yes, precisely:
```python
bellows_written = set()
bellows_written.add("verdicts/ledger.jsonl")  # logged before _rescan writes it
```
Then pass `bellows_written` to `gates.check()` and exclude those paths in `_gate_scope_check`. This is architecturally cleaner than a static allowlist but requires threading a new parameter through several function signatures.

The concurrent write problem is fundamental: `_rescan()` (main thread) can write `ledger.jsonl` at any point during a step execution. There is no signal from the main thread to the gate check saying "I wrote this file." The cleanest resolution is structural: **untrack `ledger.jsonl`** so it never appears in `git diff --stat`, removing the problem at its source rather than filtering at the gate level.

---

## Q5 — What's in `.gitignore` today?

Full contents of `/Users/marklehn/Desktop/GitHub/bellows/.gitignore`:
```
bellows.db
*.db-shm
*.db-wal
logs/
.DS_Store
__pycache__/
*.pyc
.venv/
config.json
.env
```

**Specific checks:**
| Path | In .gitignore? | Git-tracked? | Shows in `git diff --stat`? |
|------|---------------|--------------|----------------------------|
| `verdicts/ledger.jsonl` | **NO** | YES (` M` in git status) | **YES** — false positive source |
| `verdicts/pending/` | **NO** | NO (`??` in git status) | NO — untracked dir |
| `verdicts/resolved/` | **NO** | NO (`??` in git status) | NO — untracked dir |
| `bellows.db` | YES | NO | NO |
| `knowledge/decisions/` | **NO** | YES (plan files tracked) | YES for tracked files that are deleted/modified |

**Key finding:** `verdicts/ledger.jsonl` is the only infrastructure FILE that is both git-tracked and persistently modified. It is the largest false positive source by volume (triggers on every plan, every verdict cycle). The `verdicts/pending/` and `verdicts/resolved/` directories contain verdict queue files that are untracked and never appear in diffs. `bellows.db` is correctly gitignored.

**`knowledge/decisions/` is tracked**, meaning every plan file rename (claim → in-progress, in-progress → verdict-pending, in-progress → Done/) that involves a tracked file can show up in `git diff --stat` as an unstaged deletion.

---

## Files Deposited

- `/Users/marklehn/Desktop/GitHub/bellows/knowledge/research/scope-check-infra-files-diagnostic-2026-04-16.md`
