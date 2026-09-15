# QA Receipt — classify-deposit-script (2026-09-14)

Plan: #100102 — `tools/classify_deposit.py` sys.path setup (thread 329)
Base commit: `41f529a7` | DEV commits: `16c3730e`, `4c1655ec`

---

## DEV diff summary

### numstat (`41f529a7..4c1655ec`)

```
34	0	knowledge/development/dev-log-classify-deposit-script-2026-09-14.md
19	0	knowledge/mutants/classify-deposit-script.json
10	0	knowledge/mutants/classify-deposit-script.run.txt
36	0	tests/test_classify_deposit.py
 4	0	tools/classify_deposit.py
```

Five files; four lines added to the tool, none removed.

### Tool diff (`41f529a7..4c1655ec -- tools/classify_deposit.py`)

```diff
diff --git a/tools/classify_deposit.py b/tools/classify_deposit.py
index b5ce10b2..7322e707 100644
--- a/tools/classify_deposit.py
+++ b/tools/classify_deposit.py
@@ -5,6 +5,10 @@ import os
 import re
 import sys
 
+_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
+sys.path.insert(0, os.path.join(_ROOT, "scripts"))
+sys.path.insert(0, _ROOT)
+
 
 def _find_unparsed_stanza_lines(plan_text):
     """Return stanza lines the manifest parser skips (non-blank, not field, not continuation)."""
```

Four lines added (three path lines and the blank line below them); none removed.

### Test file hunk headers

Base file line count: `git show "41f529a7:tests/test_classify_deposit.py" | wc -l` → `241`

`git diff -U0 41f529a7..4c1655ec -- tests/test_classify_deposit.py | grep -F '@@'`:

```
@@ -3,0 +4 @@ import json
@@ -241,0 +243,35 @@ def test_c8_unreadable_input(tmp_path, capsys):
```

Both hunks add lines and remove none. First hunk adds `import os` after base line 3 (`import json`). Second hunk adds c9's 35 lines after base line 241 (the file's last line). No hunk touches c1–c8.

---

## Item 2 — Script runs (no PYTHONPATH)

### Plan: `knowledge/decisions/Done/executable-100073.md` (shop-infra declared and assigned → MATCH)

**From worktree root:**
```
plan: knowledge/decisions/Done/executable-100073.md
manifest: parsed (12 fields)
writes (11) from manifest
  1. lifecycle.py
  2. bellows.py
  3. tools/reconcile_steps.py
  4. tests/test_lifecycle.py
  5. tests/test_consume_verdicts.py
  6. tests/test_reconcile_steps.py
  7. knowledge/mutants/step-status-transition.json
  8. knowledge/mutants/step-status-transition.run.txt
  9. knowledge/development/dev-log-step-status-transition-2026-09-11.md
  10. knowledge/qa/evidence/step-status-transition-qa-receipt-2026-09-11.md
  11. knowledge/qa/evidence/step-status-transition-suite-2026-09-11.txt
unparsed stanza lines (0)
reads (9)
  bellows.py
  lifecycle.py
  tests/test_lifecycle.py
  tests/test_consume_verdicts.py
  tests/conftest.py
  tools/mutation_check.py
  tools/check_deposit.py
  knowledge/decisions/Done/executable-100070.md
  knowledge/mutants/no-test-spawns-a-watcher.json
declared class: shop-infra
assigned class: shop-infra
RESULT: MATCH
```
exit: 0

**From `/tmp`:**
```
plan: /Users/marklehn/Developer/bellows/.bellows-worktrees/100102/knowledge/decisions/Done/executable-100073.md
manifest: parsed (12 fields)
writes (11) from manifest
  1. lifecycle.py
  2. bellows.py
  3. tools/reconcile_steps.py
  4. tests/test_lifecycle.py
  5. tests/test_consume_verdicts.py
  6. tests/test_reconcile_steps.py
  7. knowledge/mutants/step-status-transition.json
  8. knowledge/mutants/step-status-transition.run.txt
  9. knowledge/development/dev-log-step-status-transition-2026-09-11.md
  10. knowledge/qa/evidence/step-status-transition-qa-receipt-2026-09-11.md
  11. knowledge/qa/evidence/step-status-transition-suite-2026-09-11.txt
unparsed stanza lines (0)
reads (9)
  bellows.py
  lifecycle.py
  tests/test_lifecycle.py
  tests/test_consume_verdicts.py
  tests/conftest.py
  tools/mutation_check.py
  tools/check_deposit.py
  knowledge/decisions/Done/executable-100070.md
  knowledge/mutants/no-test-spawns-a-watcher.json
declared class: shop-infra
assigned class: shop-infra
RESULT: MATCH
```
exit: 0

### Plan: `knowledge/decisions/Done/executable-100098.md` (app-feature declared and assigned → MATCH)

**From worktree root:**
```
plan: knowledge/decisions/Done/executable-100098.md
manifest: parsed (11 fields)
writes (4) from manifest
  1. knowledge/development/dev-log-abandoned-runner-close-2026-09-12.md
  2. knowledge/development/dev-log-abandoned-runner-close-2026-09-13.md
  3. knowledge/qa/evidence/abandoned-runner-close-qa-receipt-2026-09-12.md
  4. knowledge/qa/evidence/abandoned-runner-close-suite-2026-09-12.txt
unparsed stanza lines (0)
reads (14)
  knowledge/decisions/halted-executable-100097.md
  logs/20260913-174007-step.json
  lifecycle.py
  bellows.py
  notifier.py
  tools/reconcile_steps.py
  tools/check_deposit.py
  tests/test_lifecycle.py
  tests/test_abandoned_runner_close.py
  tests/test_reconcile_steps.py
  tests/test_stop_path.py
  tests/conftest.py
  knowledge/mutants/abandoned-runner-close.run.txt
  knowledge/decisions/Done/executable-100055.md
declared class: app-feature
assigned class: app-feature
RESULT: MATCH
```
exit: 0

**From `/tmp`:**
```
plan: /Users/marklehn/Developer/bellows/.bellows-worktrees/100102/knowledge/decisions/Done/executable-100098.md
manifest: parsed (11 fields)
writes (4) from manifest
  1. knowledge/development/dev-log-abandoned-runner-close-2026-09-12.md
  2. knowledge/development/dev-log-abandoned-runner-close-2026-09-13.md
  3. knowledge/qa/evidence/abandoned-runner-close-qa-receipt-2026-09-12.md
  4. knowledge/qa/evidence/abandoned-runner-close-suite-2026-09-12.txt
unparsed stanza lines (0)
reads (14)
  knowledge/decisions/halted-executable-100097.md
  logs/20260913-174007-step.json
  lifecycle.py
  bellows.py
  notifier.py
  tools/reconcile_steps.py
  tools/check_deposit.py
  tests/test_lifecycle.py
  tests/test_abandoned_runner_close.py
  tests/test_reconcile_steps.py
  tests/test_stop_path.py
  tests/conftest.py
  knowledge/mutants/abandoned-runner-close.run.txt
  knowledge/decisions/Done/executable-100055.md
declared class: app-feature
assigned class: app-feature
RESULT: MATCH
```
exit: 0

### Plan: `knowledge/decisions/Done/executable-worktree-precheck-hardening-2026-05-29.md` (no Cycle Manifest → FALLBACK)

**From worktree root:**
```
plan: knowledge/decisions/Done/executable-worktree-precheck-hardening-2026-05-29.md
manifest: absent
writes (4) from fallback
  1. bellows/knowledge/development/worktree-precheck-hardening-2026-05-29.md
  2. bellows/knowledge/research/agent-prompt-feedback.md
  3. bellows/bellows.py
  4. bellows/tests/test_worktree.py
unparsed stanza lines (0)
reads (0)
declared class: none
assigned class: shop-infra
RESULT: FALLBACK
```
exit: 3

**From `/tmp`:**
```
plan: /Users/marklehn/Developer/bellows/.bellows-worktrees/100102/knowledge/decisions/Done/executable-worktree-precheck-hardening-2026-05-29.md
manifest: absent
writes (4) from fallback
  1. bellows/knowledge/development/worktree-precheck-hardening-2026-05-29.md
  2. bellows/knowledge/research/agent-prompt-feedback.md
  3. bellows/bellows.py
  4. bellows/tests/test_worktree.py
unparsed stanza lines (0)
reads (0)
declared class: none
assigned class: shop-infra
RESULT: FALLBACK
```
exit: 3

---

## Verification

| Item | What was verified | Status |
|------|-------------------|--------|
| 1 | Full suite: 2378 passed, two skips (test_gate_watcher live-DB; test_fallback_live_wal_window version gate) | ✅ |
| 2 | Six script runs (three plans × worktree root + /tmp): 100073 MATCH exit 0, 100098 MATCH exit 0, worktree-precheck FALLBACK exit 3; no tracebacks | ✅ |
| 3 | No production writes outside the two evidence files; `grep -n -E 'sqlite3|\.connect\(' tools/classify_deposit.py` prints nothing | ✅ |

---

============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
Evidence folder: /Users/marklehn/Developer/bellows/.bellows-worktrees/100102/knowledge/qa/evidence/
Files verified: 1
