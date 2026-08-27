# Dev Log — mutation-self-application (exec-577)

**Date:** 2026-08-27

## Task B — Reproduction (before any edits)

### 3-kill manifest (F1)

```
HEAD: acc085e4f1887c928d9154465f7b2aa3e7290a61
TARGET: tools/mutation_check.py sha256=54752837acf7

MUTANT score-any-nonzero-as-killed: KILLED — suite caught the defect
MUTANT drop-baseline-control: KILLED — suite caught the defect
MUTANT drop-bytecode-isolation: KILLED — suite caught the defect

LIVE-TREE UNCHANGED: 54752837acf7

MUTATION: 3 killed, 0 survived, 0 error
---
exit=0
```

### Survivor manifest (F2)

```
HEAD: acc085e4f1887c928d9154465f7b2aa3e7290a61
TARGET: tools/mutation_check.py sha256=54752837acf7

MUTANT score-exit5-as-killed: SURVIVED — suite does not discriminate this defect

LIVE-TREE UNCHANGED: 54752837acf7

MUTATION: 0 killed, 1 survived, 0 error
SURVIVED means the suite does not discriminate this defect — the tests are decorative for it.
---
exit=1
```

## Pin re-derivation (mine supersede the plan's where they differ)

| pin | plan value | my value | status |
|-----|-----------|----------|--------|
| F1 | 3 killed / 0 survived | 3 killed, 0 survived, 0 error, exit=0 | MATCH |
| F2 | 1 survived (benign) | 0 killed, 1 survived, 0 error, exit=1 | MATCH |
| F3 anchor `if exit_code == 1:` count=1 at :201 | 1 | 1 (grep -cF) | MATCH |
| F3 anchor `if baseline_exit != 0:` count=1 at :177 | 1 | 1 (grep -cF) | MATCH |
| F3 anchor `env["PYTHONDONTWRITEBYTECODE"] = "1"` count=1 at :49 | 1 | 1 (grep -cF) | MATCH |
| F4 exit-code contract (survivor → exit 1, no pipe) | exit 1 | exit=1 (verified without pipe) | MATCH |
| F5 mutants dir contents | gate_watcher.json only | gate_watcher.json only | MATCH |
| F6 full suite collection | 1632 | 1632 tests collected | MATCH |

All pins match. No supersedes needed.

## Task D — comment edit anchor assertions (post-edit)

After adding the scoring-arm comment at :201, anchor uniqueness re-verified:

- `if exit_code == 1:` → count 1 ✓
- `if baseline_exit != 0:` → count 1 ✓
- `env["PYTHONDONTWRITEBYTECODE"] = "1"` → count 1 ✓

## git diff --stat (proving comment-only edit)

```
 tools/mutation_check.py | 8 ++++++++
 1 file changed, 8 insertions(+)
```

All 8 added lines are comment lines (verified via `git diff` — every added line begins with `#`).
