verdict: stop

Planner verdict on executable-394 step 5 (QA) -> STOP (halt); a QA-process failure + 3 missed version-assertion updates. Corrective plan to follow (Bellows grammar: no redo; stop + re-deposit).

WHY THE GATE FAILED (two things):
1. QA PROCESS FAILURE (root cause of the gate). The QA agent ran `pytest tests/` but launched it as BACKGROUND tasks (transcript 20260813-230705-step.json: tasks 'Run full test suite for QA' + 'Full test suite completion' both status=killed on step-end) and ended its turn before the suite finished — so NO qa report and NO evidence file were written (files_changed=0). deposit_exists/rule_20/rule_22 failed on the missing files, NOT on a test result.
2. 3 STALE VERSION-ASSERTION TESTS Step 1 missed. Planner ran the FULL suite in the foreground (2622 passed, 5 failed, 15m13s). 2 failures are the CLAUDE.md-known pre-existing ones. The other 3 are all `assert version == 21` (DB now stamps 22): tests/test_forge_export_sanitization.py:326, tests/test_fuel_import_conflict.py:266 and :291 — the SAME class as the 7 Step 1 fixed, but 3 files it did not sweep. Not a behavioral regression; the buffer feature itself passes.

STEPS 1-4 ARE COMMITTED AND CORRECT (Planner-verified each gate directly, incl. running targeted suites: schema migrate-existing, activity reroute 12/12, drain 29/29, UI 11/11). They are NOT re-run.

CORRECTIVE PLAN (to be deposited): a small DEV step updating the 3 stale `== 21` assertions to `== 22`, then a QA step running the full suite in the FOREGROUND (explicitly no backgrounding; evidence written FIRST) + Rule 20 banner. Against committed HEAD.
