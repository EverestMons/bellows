# Dev Log: plan-lint-fence-exclusion — 2026-08-26

## F2 blob ref

The 563 draft's fired line (`if code == 0:` inside a fenced block):
- Commit: `68b5288`
- File: `knowledge/decisions/ready-executable-run-check-wrapper.md`
- Blob: `155110df5d23a61ce4ebe95ffbac25f557561b89`

## Pre-probes (Task A)

```
$ cd "$(git rev-parse --show-toplevel)" && test -f scripts/plan_lint.py && echo TREE_OK
TREE_OK

$ /usr/bin/grep -cF -- "in_fence" scripts/plan_lint.py; true
0

$ /usr/bin/grep -cF -- "def test_fence" tests/test_plan_lint_bare_constants.py; true
0
```

Resume arm: (0,0) → full run.

## Post-probes (Task B)

```
$ /usr/bin/grep -cF -- "in_fence" scripts/plan_lint.py
3

$ /usr/bin/grep -cF -- "563" scripts/plan_lint.py
1
```

`in_fence` appears on 3 lines (init, toggle, skip condition). Docstring mentions 563 once.

## Targeted run (Task C)

```
$ python3 -m pytest tests/test_plan_lint_bare_constants.py tests/test_plan_lint.py -v
141 passed, 0 failed (0 warnings besides urllib3 NotOpenSSLWarning)
```

Derivation: 134 prior lint tests + 5 existing bare-constant tests + 2 new fence tests = 141.
