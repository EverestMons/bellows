# Executable — Dispatch Mode Validator QA Recovery

**Last Updated:** 2026-05-19
**Project:** bellows
**Total Steps:** 1
**Dispatch Mode:** bellows
**auto_close:** false
**pause_for_verdict:** after_each_step

## Execution Map

Step 1 (QA) — single step.

## CEO Context

Recovery for `executable-bellows-dispatch-mode-validator-2026-05-19` halted at QA Step 3 due to Rule 20 self-check gate failure: banner present but PASSED line missing. Root cause: the prior QA agent shipped the Rule 20 Python block as source code without executing it and capturing stdout under an `Output:` heading.

**Substantive work shipped clean.** Validator code is committed at `37edd40` on origin/main. All 9 verification checks reported with evidence files. Both behavioral spot-checks PASS. Full suite regression is zero. The seven evidence files exist at `bellows/knowledge/qa/evidence/dispatch-mode-validator-2026-05-19/`. The only failure is the Rule 20 self-check block was not executed.

**Check 8 disposition (accepted by Planner):** The prior QA correctly identified that the validator fires on the literal phrase `STOP.` inside a quoted example in Step 1's Check (b) rationale. Quotation marks are not in the exclusion scoping (only backticks, fenced blocks, and `**Deposits:**` blocks are excluded). The validator is working as designed — the plan's quoted example is a known authoring imperfection caught honestly by the validator. Disposition is **warn**, not reject. The plan would still claim. This finding is documented and accepted; no validator change warranted.

---

## STEP 1 — QA: Rule 20 self-check re-execution

**Agent:** QA (`bellows/agents/BELLOWS_QA.md`)

### Inputs
- Prior QA report: `bellows/knowledge/qa/dispatch-mode-validator-2026-05-19.md`
- Evidence directory: `bellows/knowledge/qa/evidence/dispatch-mode-validator-2026-05-19/`
- Canonical Rule 20 block: `/Users/marklehn/Developer/GitHub/RULE_20_SELF_CHECK_BLOCK.md`

### Deliverables

Re-deposit the prior QA report at `bellows/knowledge/qa/dispatch-mode-validator-2026-05-19.md` with one structural change: under the `## Rule 20 — QA Self-Check` heading, after the canonical Python block, add an `**Output:**` subsection containing the literal stdout captured from executing the block. All other report content remains unchanged.

**Execution procedure:**

1. Read the canonical block from `/Users/marklehn/Developer/GitHub/RULE_20_SELF_CHECK_BLOCK.md`. Copy verbatim.

2. Fill the four placeholders with these values:
   - `plan_slug`: `dispatch-mode-validator-2026-05-19`
   - `qa_report_path`: `bellows/knowledge/qa/dispatch-mode-validator-2026-05-19.md`
   - `evidence_dir`: `bellows/knowledge/qa/evidence/dispatch-mode-validator-2026-05-19/`
   - `required_evidence_files`: `["dev_pytest.txt", "qa_targeted_pytest.txt", "qa_full_suite_pytest.txt", "reject_repl.txt", "warn_b_repl.txt", "self_consistency_scan.txt", "plan_header_dispatch_mode.txt"]`

3. Run the filled-in block as a Python script from the bellows project root. Capture stdout verbatim.

4. Verify the captured stdout contains the line `PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.` If it does not, halt and report — substantive issues must be addressed before re-deposit.

5. Edit `bellows/knowledge/qa/dispatch-mode-validator-2026-05-19.md`. Locate the `## Rule 20 — QA Self-Check` heading. Replace its contents with:
   - The canonical Python block (filled in with the four values above)
   - An `**Output:**` heading directly after the closing of the Python code fence
   - A fenced code block containing the captured stdout

6. Capture the new QA report's Rule 20 section to evidence file `rule_20_execution.txt`.

7. Do not modify any other section of the QA report. The Check 8 finding stays as-is (accepted per CEO Context above). Verification table, spot-checks, and all other content unchanged.

**Constraint:** Do NOT re-run the full pytest suite. Do NOT re-run the validator spot-checks. Do NOT modify the validator code. The prior QA's substantive verification is accepted; this step only corrects the Rule 20 banner deficiency.

**Deposits:**
- `bellows/knowledge/qa/dispatch-mode-validator-2026-05-19.md`
- `bellows/knowledge/qa/evidence/dispatch-mode-validator-2026-05-19/rule_20_execution.txt`
