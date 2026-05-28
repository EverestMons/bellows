verdict: continue
Rule 22 (d) override — gate failure is a Planner-authoring error, not a substantive QA failure.

Root cause: the executable plan's Step 2 (QA) prompt mandated the wrong Rule 20 banner string. I authored `RULE 20 SELF-CHECK: <PASSED|FAILED>` into the prompt. The gate detector at gates.py:475 requires the canonical banner header `Rule 20 — QA Self-Check Results` followed by a line matching `PASSED — SELF-CHECK PASSED` (regex at gates.py:506). The QA agent faithfully emitted the banner I specified (`RULE 20 SELF-CHECK: PASSED`), which does not contain the canonical header — so the gate correctly fired `rule_20_self_check: no QA deposit contains Rule 20 self-check banner`. The gate is working as designed; my prompt specified a non-canonical banner from memory instead of copying the known-good string.

Substance verification (Rule 22 (b)) — PASS, verified independently:
- Read the QA report directly. All 8 checklist rows PASS with specific line-number evidence (pre-check location, cwd=project_path, fail-open ordering, gate-name visibility, evidence content, 4 new tests green, no existing-test regressions, adjacent suite 122/122).
- Planner independently ran `pytest -k teardown -q`: 9 passed, 0.20s (confirmed at Step 1 verdict).
- QA's adjacent-suite claim (122 passed, 0.83s) is consistent with the targeted run.
- DEV commit 6252f8c verified at Step 1: correct insertion point, correct cwd, correct fail-open exception ordering, gate name embedded in evidence string, both recovery sub-variants + LESSONS pointer present.
- No deviations from SA spec. QA flagged none; I find none.

The banner-string mismatch does not invalidate any verification result — every check the QA performed is sound and independently confirmed. Overriding the mechanical gate failure per Rule 22 (d). Plan completes.

LESSONS candidate (session-wrap): QA-prompt Rule 20 banner must be authored as the canonical `Rule 20 — QA Self-Check Results` / `PASSED — SELF-CHECK PASSED` pair, copied from a known-good QA report, not paraphrased. Third Planner-authoring-from-memory failure this session (header field-line position; this banner; cf. the `### Deposits` shape in the resolved gate-FP verdict). Common root cause: specifying strict Bellows conventions from memory under authoring load rather than copying from a verified artifact.
