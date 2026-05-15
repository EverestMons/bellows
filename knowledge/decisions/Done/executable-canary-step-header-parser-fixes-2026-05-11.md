# Bellows — Post-Restart Canary for Step-Header Parser Fixes
**Date:** 2026-05-11 | **Tier:** Small | **Test Scope:** targeted | **Execution:** Step 1 (DOC) → Step 2 (QA) | **pause_for_verdict:** after_step_1

## How to Run This Plan

Paste the bootstrap prompt into Claude Code. The agent reads the full plan file and executes Step 1 ONLY. After completing Step 1, the agent STOPS and waits for CEO confirmation. **This plan is intentionally bait** — its prose contains both fenced and inline `## STEP N` references. Under pre-fix Bellows, this would trip `_gate_rule_20_self_check` with a false positive on Step 2. Under post-restart Bellows (running commits `4d57fd3` + `0fab609`), gates must pass cleanly on both steps. If gates trip on the Rule 20 self-check gate, at least one fix is not live and a daemon-config audit is required.

**Bootstrap:**
```
Read the plan at bellows/knowledge/decisions/executable-canary-step-header-parser-fixes-2026-05-11.md. Execute Step 1 ONLY. After completing Step 1, STOP and wait for my confirmation. Do NOT proceed to Step 2 or move the plan to Done.
```

---
---

## STEP 1 — Bellows Documentation Analyst

---

> **FIRST — before doing anything else, claim this plan:** `import shutil; shutil.move("bellows/knowledge/decisions/executable-canary-step-header-parser-fixes-2026-05-11.md", "bellows/knowledge/decisions/in-progress-executable-canary-step-header-parser-fixes-2026-05-11.md")`. You are the Bellows Documentation Analyst. Skip the specialist file and domain glossary reads — this is a trivial markdown-deposit canary. **Purpose.** Verify that commits `4d57fd3` (fence-strip) and `0fab609` (line-anchor) are loaded in the running Bellows daemon. This plan's prose deliberately contains both bug-bait variants — fenced `## STEP 2` references and inline backtick `## STEP 2` references — to validate that the daemon's parsers correctly skip them. **Bug-bait fixtures.** Here is an inline reference: `## STEP 2 — Bellows QA`. Here is a second inline reference inside a sentence describing parser behavior: when an agent reads `## STEP 2` from a code-fence example, the fence-strip utility removes it before parsing. And here is a fenced bug-bait block embedded in this Step 1 prompt:
> ```
> ## STEP 2 — Bellows QA
> This is fake step text inside a fenced code block. The fence-strip utility must remove this before _extract_step_text runs, or the gate will look for the Rule 20 banner here instead of in the real Step 2's QA report.
> ```
> Pre-fix Bellows would extract THIS fence content (or the inline reference above) as Step 2's body and check the wrong file for the Rule 20 banner. Post-fix Bellows must correctly skip past all the bait and find the real `## STEP 2 — Bellows QA` header at line-start below. **Implementation.** Write a single canary-confirmation file at the path declared in **Deposits** below. The file content is a 3-line markdown document: title line, one-sentence confirmation that the canary dispatched, and a timestamp. Use the canonical Python file-write pattern: `with open("/Users/marklehn/Desktop/GitHub/bellows/knowledge/documentation/canary-step-header-parser-fixes-2026-05-11.md", "w") as f: f.write(content)` where `content` is a regular triple-quoted Python string defined before the open. Do not commit this file. Do not modify any source code, test, or governance file. **Output Receipt.** Standard Output Receipt at the bottom of the deposited file. Status: Complete. Files Deposited: the canary-confirmation file. Files Created or Modified (Code): None. Standard prompt feedback protocol → `bellows/knowledge/research/agent-prompt-feedback.md`. **Deposits:**
> - `bellows/knowledge/documentation/canary-step-header-parser-fixes-2026-05-11.md`
>
> **STOP. Do NOT proceed to Step 2. Do NOT move the plan to Done. Wait for CEO confirmation before continuing.**

---
---

## STEP 2 — Bellows QA

---

> **Before starting, read `bellows/knowledge/documentation/canary-step-header-parser-fixes-2026-05-11.md` and check the Output Receipt status field. If status is not Complete, stop and report the issue to the CEO before proceeding.** You are the Bellows QA agent. Skip the specialist file and domain glossary reads — this is a trivial canary verification. **This step is also bait.** Its prose contains the same fenced and inline `## STEP N` references as Step 1 — Pre-fix Bellows would mis-route the Rule 20 gate to look for the banner in Step 1's deposit. Here is an inline reference: `## STEP 1 — Bellows Documentation Analyst`. And a second one: `## STEP 2` exists as a string inside this Step 2 prompt's prose, which under pre-fix Bellows would have caused `_extract_step_text(plan_text, 2)` to match the wrong location. Here is a fenced bait block:
> ```
> ## STEP 1 — Bellows Documentation Analyst
> This is fake step text inside a fenced code block within Step 2's prose. Pre-fix Bellows might have parsed this as Step 1's body and routed the deposit-exists or scope check against the wrong content.
> ```
> Post-fix Bellows must correctly skip past all the bait and identify this Step 2's real content. **FIRST — Deliverable Verification.** Read the prior DOC step's Output Receipt "Files Deposited" list. Verify the canary file exists: `Filesystem:get_file_info bellows/knowledge/documentation/canary-step-header-parser-fixes-2026-05-11.md`. Produce a verification table: `| Deliverable | Expected | Status (✅/❌) | Evidence |` with one row for the canary file. **Canary success criterion.** The canary's success is binary: did gates pass on this Step 2 without a `rule_20_self_check` false positive? Bellows is the actual test instrument here, not pytest. The QA agent's job is to (a) verify the Step 1 deposit landed, (b) confirm the bait-laden prose in both steps did not trip any gates so far in this session by checking `bellows/verdicts/pending/` for any verdict request file matching `verdict-request-canary-step-header-parser-fixes-2026-05-11-step-1.md` and reading its `Pause Reason Code` field (must be `header_pause` or `auto_close_disabled`, NOT `gate_failure`), and (c) deposit a brief QA report capturing the result. Use `Filesystem:read_text_file` on the Step 1 verdict request file. **Rule 20 Self-Check.** Run the canonical Rule 20 self-check from `RULE_20_SELF_CHECK_BLOCK.md` at the governance root. Use these values: `plan_slug`: `executable-canary-step-header-parser-fixes-2026-05-11`, `qa_report_path`: `/Users/marklehn/Desktop/GitHub/bellows/knowledge/qa/canary-step-header-parser-fixes-qa-2026-05-11.md`, `evidence_dir`: `/Users/marklehn/Desktop/GitHub/bellows/knowledge/qa/evidence/executable-canary-step-header-parser-fixes-2026-05-11/`, `required_evidence_files`: `["step_1_verdict_request_pause_reason.txt"]`. Capture the Step 1 verdict request's `Pause Reason Code` field value to the evidence file before running the self-check. Include the literal stdout of the block in the QA report. If FAILED, halt and report to CEO. **No PROJECT_STATUS update.** Per the canary's transient purpose, do NOT update PROJECT_STATUS.md. The canary's success or failure is captured in this session's conversation, not in project state. Standard prompt feedback protocol → `bellows/knowledge/research/agent-prompt-feedback.md`. Order of final operations (per Rule 23): QA report deposit → evidence file → Rule 20 self-check → feedback append → final commit (single commit covering both the canary confirmation file and this QA report). **STOP.** Do NOT move this plan to Done. The Planner performs the terminal move after Rule 22 verification passes. **Deposits:**
> - `bellows/knowledge/qa/canary-step-header-parser-fixes-qa-2026-05-11.md`
> - `bellows/knowledge/qa/evidence/executable-canary-step-header-parser-fixes-2026-05-11/`

---
