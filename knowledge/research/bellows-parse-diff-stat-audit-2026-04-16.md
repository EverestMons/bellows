# `_parse_diff_stat` Audit Findings
**Date:** 2026-04-16 | **Source plan:** diagnostic-bellows-parse-diff-stat-audit-2026-04-16.md

## Summary

`_parse_diff_stat` has a confirmed OR-semantics bug: it unions filenames from both `pre_diff` and `post_diff`, so any file that was already dirty before a step runs will always appear in the output — even if the step made no changes to it. This is exactly what caused the four false-positive scope flags during Phase 8's own rollout. The fix is to switch to diff-of-diffs semantics: compare the per-file stat lines between pre and post, and only report a file when its stat line changed (or it appeared new in post).

---

## Q1 — Current Implementation

```python
# bellows.py lines 306–316
def _parse_diff_stat(post_diff: str, pre_diff: str) -> list:
    """Parse git diff --stat output to extract changed file paths."""
    files = set()
    for diff_text in (post_diff, pre_diff):
        for line in diff_text.strip().splitlines():
            line = line.strip()
            if "|" in line:
                filename = line.split("|")[0].strip()
                if filename:
                    files.add(filename)
    return sorted(files)
```

**Verdict: OR-semantics confirmed.** The function iterates over `(post_diff, pre_diff)` and adds filenames from both to a single set. Any file present in *either* diff is returned. There is no computation of what changed *between* pre and post — it is a pure union.

---

## Q2 — Call Sites

Both call sites pass arguments in `(post_diff, pre_diff)` order, matching the function signature:

```python
# bellows.py line 191
post_diff = _capture_git_diff(project_path)
files_changed = _parse_diff_stat(post_diff, pre_diff)

# bellows.py line 240
post_diff = _capture_git_diff(project_path)
files_changed = _parse_diff_stat(post_diff, pre_diff)
```

The argument order is not reversed at either call site. The bug is entirely inside the function body — it ignores the semantic distinction between the two arguments and treats them identically.

---

## Q3 — Minimal Test Case

**Setup:**

```
pre_diff  = "foo.py | 2 +-\n 1 file changed, 1 insertion(+), 1 deletion(-)"
post_diff = "foo.py | 2 +-\n 1 file changed, 1 insertion(+), 1 deletion(-)"
```

`foo.py` was dirty before the step started (2 lines changed from HEAD). The step ran and made no new changes to it. The post-step diff is identical.

**What `_parse_diff_stat(post_diff, pre_diff)` returns today:**

```python
["foo.py"]
```

The function finds `foo.py` in both diffs, adds it to the set, and returns it. The gates then flag `foo.py` as a file "changed during this step."

**What it SHOULD return:**

```python
[]
```

The step modified nothing. `foo.py` was already dirty and remained at the same dirty state. The correct answer is an empty list.

---

## Q4 — Fix Sketch

### Option A — Set difference (files in post NOT in pre)

Return filenames that appear in `post_diff` but not in `pre_diff`.

- **Handles:** new files created during the step.
- **Misses:** files that were already dirty AND had *additional* modifications made during the step. A pre-existing dirty `foo.py | 2 +-` that grows to `foo.py | 5 +++--` after the step would NOT be reported, because `foo.py` appears in pre_diff and therefore gets excluded.

### Option B — Diff-of-diffs: compare per-file stat lines

Build a `{filename: stat_line}` dict for both pre and post. Report a filename when:
1. It appears in `post_diff` and not in `pre_diff` (new modification), OR
2. It appears in both, but the stat line content differs (step added more changes to an already-dirty file).

**Recommended: Option B.**

**Justification:** `git diff --stat` reports the *cumulative* diff from HEAD. If `foo.py | 2 +-` appears in both pre and post, the file's modification count is identical — the step did nothing to it. If post shows `foo.py | 5 +++--` vs pre's `foo.py | 2 +-`, the step made 3 additional changes. Option B catches both cases correctly:
- Pre-existing dirty, untouched → same stat line → not reported. ✓
- Pre-existing dirty, further modified → different stat line → reported. ✓
- New file created during step → absent in pre, present in post → reported. ✓

Option A fails case 2. Since scope_check is meant to detect what the agent *actually did*, Option B is semantically precise and is the right approach.

**Sketch of corrected implementation:**

```python
def _parse_diff_stat(post_diff: str, pre_diff: str) -> list:
    """Return files whose git diff --stat line changed between pre and post."""
    def parse_stat_map(diff_text):
        result = {}
        for line in diff_text.strip().splitlines():
            line = line.strip()
            if "|" in line:
                filename, stat = line.split("|", 1)
                filename = filename.strip()
                if filename:
                    result[filename] = stat.strip()
        return result

    pre_map = parse_stat_map(pre_diff)
    post_map = parse_stat_map(post_diff)
    changed = [f for f, s in post_map.items() if pre_map.get(f) != s]
    return sorted(changed)
```

---

## Output Receipt

| Field | Value |
|---|---|
| Status | Complete |
| Questions answered | Q1, Q2, Q3, Q4 |
| Findings file | knowledge/research/bellows-parse-diff-stat-audit-2026-04-16.md |
| Fix implemented | No — diagnostic only, per plan instructions |
| Root cause confirmed | Yes — OR-semantics union in `_parse_diff_stat` lines 306–316 |
