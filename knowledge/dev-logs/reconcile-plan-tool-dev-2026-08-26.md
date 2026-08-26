# Dev Log: reconcile-plan-tool — 2026-08-26

## Plan
executable-566 Step 1 — three-surface orphan recovery mechanized.

## Probes (pre-flight)
- `tools/`: 5 entries (clear_plan.py, deposit_receipt.py, issue_verdict.py, link_live_commands.py, run_check.py) — reconcile_plan.py ABSENT
- C2 pointer: `"see the reconciliation runbook "` count-1 at issue_verdict.py:91
- C3 schema: plans(lifecycle_state, closed_at, plan_doc_ref); verdicts(outcome, decided_by, disposition_summary); state vocab: claimed|in_progress|awaiting_verdict|closed|halted|abandoned

## Deposits
- `tools/reconcile_plan.py` — three-surface orphan recovery tool (plans row + verdicts + pending files), refusal-first for in_progress, one transaction, WAL law docstring
- `tools/issue_verdict.py` — pointer fix: "reconciliation runbook in CLAUDE.md" replaced with "run tools/reconcile_plan.py ... (see its --help)"
- `tests/test_reconcile_plan.py` — 6 tests: full reconcile, in_progress refusal, killed-verified override, zero null-outcome verdicts, terminal verdict untouched, bad state vocab

## Post-probes
- `"reconcile_plan.py"` in issue_verdict.py: 1 (>= 1)
- `"in CLAUDE.md for manual orphan-recovery"` in issue_verdict.py: 0 (== 0)
- `"killed-verified"` in reconcile_plan.py: 4 (>= 2)
- `"outcome IS NULL"` in reconcile_plan.py: 2 (>= 1)

## Targeted test run
6 passed, 0 failed (tests/test_reconcile_plan.py)
