# QA Receipt — lint-warn-to-fail — 2026-09-10

Plan: executable-100064 | QA step 2 | [thread 265]

## DEV numstat (de7dd4f..aeab272 — 10 files)

```
53	0	knowledge/development/dev-log-lint-warn-to-fail-2026-09-10.md
44	0	knowledge/mutants/lint-warn-to-fail.json
17	0	knowledge/mutants/lint-warn-to-fail.run.txt
 8	1	scripts/close_cycle.py
 9	0	scripts/lens_commit.py
 5	3	scripts/plan_lint.py
62	0	tests/test_close_cycle.py
46	0	tests/test_lens_commit.py
 4	1	tests/test_plan_lint.py
13	0	tests/test_plan_lint_qa_steps_none.py
```

## Verification

| Item | Status | Evidence |
|------|--------|----------|
| Item 1 — full suite | ✅ | 2208 passed, 1 live-DB test excluded (test_gate_watcher), 0 failed — last line of `lint-warn-to-fail-suite-2026-09-10.txt` confirms suite duration 90.77s |
| Item 2 — FAIL on real shape | ✅ | executable-100060.md: exit 1 — `FAIL: (y) undeclared QA step — step 2 is QA-labeled but the plan declares no qa_steps — it will NOT be Rule 20/22 gated at dispatch (declare \`qa_steps: 2\`, or \`none\` if it is not a QA step)`; executable-100061.md: exit 1 — same FAIL: (y) row; executable-100062.md: no (y) row, exit 0 |
| Item 3 — echoes on real draft | ✅ | Run 1 (field-less): `LENS-COMMIT: plan_lint FAIL — FAIL: (y) undeclared QA step — step 2 is QA-labeled but the plan declares no qa_steps — it will NOT be Rule 20/22 gated at dispatch (declare \`qa_steps: 2\`, or \`none\` if it is not a QA step)` then `LENS-COMMIT: cycle FAIL — expected BAR_MET, got 'CONTINUE'`, exit 1, no commit (git log count unchanged: 1); Run 2 (with field + `<declare>`): `LENS-COMMIT: plan_lint WARN — (f) WARN: Cycle Manifest stanza contains <declare> placeholder(s) — incomplete template`, next line is `LENS-COMMIT: plan_lint WARN — (t) WARN:` (not a lint refusal); Run 3 (close_cycle --dry-run, field-less): `CLOSE: battery FAIL — plan_lint: exit 1 — FAIL: (y) undeclared QA step — step 2 is QA-labeled but the plan declares no qa_steps — it will NOT be Rule 20/22 gated at dispatch (declare \`qa_steps: 2\`, or \`none\` if it is not a QA step)`; Run 4 (depositor filter): `FAIL: (y) undeclared QA step — step 2 is QA-labeled but the plan declares no qa_steps — it will NOT be Rule 20/22 gated at dispatch (declare \`qa_steps: 2\`, or \`none\` if it is not a QA step)` (the (y) row survives the {c,d} benign filter as non-benign) |
| Item 4 — production writes | ✅ | No production file written outside the two evidence files; scratch dirs removed (`rm -rf "$T"` confirmed at end of each sub-run); no lifecycle import, no lane file edit, no lifecycle row |



---

```
============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
Evidence folder: /Users/marklehn/Developer/bellows/.bellows-worktrees/100064/knowledge/qa/evidence/
Files verified: 1
```
