# dev-log — scope-step-fail — 2026-09-14

## Pins re-derived (P1, P2, P3, P4, P5)

`lifecycle.record_gate_events` :717 writes a `fail` row per failure with `reason_code` its evidence (:728–740), skips `scope_step` among the standard gates' pass rows (:755–763), and writes the `scope_step` pass row, `reason_code` `earlier-step-only: …` or NULL, only when `scope_step` is not among the failures (:764–777) — so a failed step gets exactly one scope_step row, the fail row

P1 re-derived: `SCOPE_ALLOWLIST` :24, `SCOPE_ALLOWLIST_PREFIXES` :29; `def _gate_scope_check(plan_text, step_number, files_changed, failures, project_path=None, warnings=None):` :1129; the step union :1133–1141; the `declared` flag :1143–1152; Scope ∪ Deposits :1154–1162; the P14 normalization :1164–1174; the allowlist arms :1182–1185; the union's match :1187–1204; the legacy arms :1205–1221; the `scope_check` failure :1225–1231; the per-step reading :1233–1279 — `if declared and step_number > 1 and warnings is not None:` :1236, its copied set build :1237–1255, its copied match :1265–1278, `warnings.append({"gate": "scope_step", "evidence": fpath})` :1279, all 47 lines by `543b5f5` (#100074). No `_declared_paths` or `_matches_declared` in gates.py; no `scope_step` FAIL branch in verdict.py's scope_step arm; `record_gate_events` writes the scope_step pass row only when `scope_step` not in `failure_gates` — no mismatch on any pin.

P2 re-derived: `verdict._build_verification_results_table` :105; `_KNOWN_GATES` :112–129, `("scope_step", None, None)` :121; the `scope_step` branch :152–160 reads `gate_result.get("warnings")` alone — a `scope_step` failure prints nowhere; the standard gates' FAIL rows from `failures_by_gate` :179–181.

P3 re-derived (verbatim above): `sed -n '717,790p lifecycle.py'` confirmed — `scope_step` skipped in standard pass rows; pass row written only when `scope_step` not in failure_gates.

P4 re-derived: `tools/replay_scope_check.py` :102–105 calls `_gate_scope_check(plan_text, step_number, files, now_failures, project_path=…)` with no `warnings` — union-only caller confirmed.

P5 re-derived: `tests/test_scope_step.py` t1–t12, 236 lines before this plan's changes; t2 and t12 asserted WARN, `passed True`; `tests/test_gate_transaction_mechanization.py` `STANDARD_GATES` :15–32, comment at :30 said "pass row always". Both tracked plan files confirmed: `git ls-files --error-unmatch knowledge/decisions/Done/executable-100061.md knowledge/decisions/Done/executable-100037.md` → BOTH TRACKED.

## Failing-first (red, then green)

Red (t1–t22 on base code, before gate edits):
`8 failed, 14 passed in 0.34s`

Green (test file alone, after gate edits):
`22 passed in 0.19s`

Green (gate files — tests/test_scope_step.py tests/test_gate_transaction_mechanization.py tests/test_gates.py tests/test_gates_verdict_pause.py tests/test_gates_evidence_correspondence.py tests/test_verdict.py tests/test_step_files_record.py):
`303 passed in 2.44s`

Green (full suite):
`2406 passed, 2 skipped, 9 warnings in 229.57s (0:03:49)`

## The arm observed (t2, t15, t16, t17, t21, t22)

```
tests/test_scope_step.py::TestScopeStepArm::test_t2_step2_earlier_step_file_fails PASSED [ 16%]
tests/test_scope_step.py::TestScopeStepFail::test_t15_multiple_earlier_step_files_one_failure PASSED [ 33%]
tests/test_scope_step.py::TestScopeStepFail::test_t16_table_scope_step_fail_row PASSED [ 50%]
tests/test_scope_step.py::TestScopeStepFail::test_t17_ledger_scope_step_fail_row PASSED [ 66%]
tests/test_scope_step.py::TestScopeStepFail::test_t21_recorded_100061_step2_scope_step_fails PASSED [ 83%]
tests/test_scope_step.py::TestScopeStepFail::test_t22_recorded_100037_step2_scope_check_and_scope_step PASSED [100%]
```

## Mutation run

`MUTATION: 12 killed, 0 survived, 0 error`
