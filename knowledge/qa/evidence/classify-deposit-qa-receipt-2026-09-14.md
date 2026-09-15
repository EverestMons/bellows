# QA Receipt — classify-deposit — 2026-09-14

**Plan:** bellows #100100 — tools/classify_deposit.py (thread 329)
**Step:** QA (Step 2)
**Suite:** 2372 passed, 2 skipped (two skips: test_gate_watcher live-DB; test_fallback_live_wal_window version gate)

## numstat — DEV commits (3d21c30..HEAD)

```
34      0       knowledge/development/dev-log-classify-deposit-2026-09-14.md
54      0       knowledge/mutants/classify-deposit.json
15      0       knowledge/mutants/classify-deposit.run.txt
241     0       tests/test_classify_deposit.py
149     0       tools/classify_deposit.py
```

Five files across two DEV commits (`d1f595c`, `a9d3d05`).

## Item 2 — Tool runs on three tracked plans

**Run 1:** `knowledge/decisions/Done/executable-100073.md` — `--project-root /Users/marklehn/Developer/bellows`

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

Exit: 0

**Run 2:** `knowledge/decisions/Done/executable-100098.md` — `--project-root /Users/marklehn/Developer/bellows`

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

Exit: 0

**Run 3:** `knowledge/decisions/Done/executable-worktree-precheck-hardening-2026-05-29.md` — `--project-root /Users/marklehn/Developer/bellows`

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

Exit: 3

**Note — PYTHONPATH required:** The tool was run with `PYTHONPATH=/Users/marklehn/Developer/bellows:/Users/marklehn/Developer/bellows/scripts`. The tool's source omits the standard `sys.path.insert(0, ...)` setup present in peer Planner-run tools (`check_deposit.py`, `reconcile_steps.py`, `fold_signal_census.py`). Without this setup the tool raises `ModuleNotFoundError: No module named 'bellows_root'` when invoked as a standalone CLI. The t3 test (`test_help_does_no_work`) did not catch this because `--help` exits before the import inside `main()`. The CEO's apply act and the Post-close Air run must supply `PYTHONPATH` or a follow-up plan must add the standard path setup to the tool's module level.

## Item 3 — Production writes

No production writes outside the two evidence files. $T removed. No lane file, no lifecycle row, no daemon act. `grep -n -E 'sqlite3|\.connect\(' tools/classify_deposit.py` prints nothing.

## Verification

| Item | Evidence line | Status |
|------|--------------|--------|
| Item 1 — full suite | `2372 passed`, two skips (test_gate_watcher live-DB; test_fallback_live_wal_window version gate) | ✅ |
| Item 2 — tool on three plans | Run 1: `RESULT: MATCH` exit 0; Run 2: `RESULT: MATCH` exit 0; Run 3: `RESULT: FALLBACK` exit 3 | ✅ |
| Item 3 — no production writes, grep clean | `grep -n -E 'sqlite3|\.connect\(' tools/classify_deposit.py` — no output | ✅ |

============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
Evidence folder: /Users/marklehn/Developer/bellows/.bellows-worktrees/100100/knowledge/qa/evidence/
Files verified: 1
