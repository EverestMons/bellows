# bellows — extract_primary_deposit Rule 26 Block Awareness
**Date:** 2026-04-19 | **Tier:** Small | **Test Scope:** targeted | **Execution:** Step 1 (DEV) → Step 2 (QA)

## CEO Context

Closes the parser-gap window noted in Rule 26's text and observed in the rule-26-gate-smoke-test-2026-04-19 verdict file (`Deposit: none` despite a declared block). `extract_primary_deposit` in `verdict.py` currently uses three legacy regexes that do not match the Rule 26 bulleted `- \`path\`` form — so verdict request files show `Deposit: none` for Rule 26-compliant plans. This executable adds block-form matching as the highest-priority pattern. Returns the first `.md` path in the block, or None if the block contains only `- none` or non-`.md` entries (directories, non-markdown files). Legacy regexes preserved as fallback for plans without a `**Deposits:**` block. Test scope is targeted because this is a single-function change in a file with its own test bucket (test_verdict.py) and no cross-bucket regression risk.

## How to Run This Plan

**Bootstrap:**
```
Read the plan at bellows/knowledge/decisions/executable-extract-primary-deposit-block-aware-2026-04-19.md. Execute Step 1 ONLY. After completing Step 1, STOP and wait for my confirmation. Do NOT proceed to Step 2 or move the plan to Done.
```

---
---

## STEP 1 — Bellows Developer

---

> Skip specialist file and glossary reads — this is a targeted code change in verdict.py. Read `bellows/verdict.py` lines 13–33 first to confirm current shape of the regexes and `extract_primary_deposit`.
>
> **Change — Add block-form matching to `extract_primary_deposit`.** Before the existing per-line regex cascade, add a block-form detection pass that runs ONCE over the full `step_text`. Detect a `**Deposits:**` block using the SAME regex as `gates.py::_extract_plan_required_deposits` (keep them in sync): `r'[> ]*\*\*Deposits:\*\*\s*\n((?:[> ]*-\s+.*\n?)+)'`. If the block matches, iterate bullets using `r'-\s+`([^`]+)`'`, return the first captured path that ends in `.md`. If the block matches but contains no `.md` paths (e.g., only directories, or only `- none`), return None immediately — do NOT fall through to legacy regexes when the block is present and authoritative. If no block matches, preserve the existing legacy cascade (STRICT → BOLD_NOUN → INLINE) unchanged.
>
> **Implementation sketch (agent must write the actual code — this is a reference, not a copy-paste):** Add a module-level constant near the existing ones: `DEPOSITS_BLOCK_RE = re.compile(r'[> ]*\*\*Deposits:\*\*\s*\n((?:[> ]*-\s+.*\n?)+)')` and `BLOCK_BULLET_RE = re.compile(r'-\s+`([^`]+)`')`. At the top of `extract_primary_deposit`, before the `for line in step_text.splitlines()` loop, run `block_match = DEPOSITS_BLOCK_RE.search(step_text)`. If `block_match`, iterate `BLOCK_BULLET_RE.finditer(block_match.group(1))`, return the first path ending in `.md` (after applying the existing `/Desktop/GitHub/` normalization). If block matched but no `.md` path found, return None. If no block match, proceed to the existing legacy loop unchanged. Preserve the absolute-path normalization block — apply it to the returned path in both the new block-form branch and the legacy branch. Add a comment above the block-form pass: `# Rule 26: prefer declared **Deposits:** block when present — block is authoritative, legacy regexes not applied as fallback.` Add a sync comment at the top of the file near the other regex constants: `# DEPOSITS_BLOCK_RE and BLOCK_BULLET_RE duplicated in gates.py::_extract_plan_required_deposits — keep in sync.`
>
> **Write targeted tests** in a new file `bellows/tests/test_extract_primary_deposit_blocks.py` using pytest, inline plan text as Python multi-line strings (no fixture files). The file must define these six tests:
>
> 1. `test_block_single_md_path_returned` — step text with `**Deposits:**` block containing one `.md` bullet; assert return is that path.
> 2. `test_block_multiple_md_first_returned` — block with two `.md` bullets; assert return is the first one.
> 3. `test_block_none_bullet_returns_none` — block with `- none`; assert return is None.
> 4. `test_block_directory_only_returns_none` — block with a single directory bullet (trailing `/`, no `.md`); assert return is None. Block is authoritative — function does NOT fall back to legacy regexes even if the step text contains prose-form deposits elsewhere.
> 5. `test_no_block_falls_back_to_legacy` — step text with no block but with prose "Deposit findings to \`path.md\`"; assert return is `path.md`. Confirms legacy cascade still works.
> 6. `test_block_with_blockquote_prefix_still_matches` — step text with `> ` blockquote prefixes on every line (as in real plan steps); assert block is detected and first `.md` path returned. This is the direct regression test for the `> ` prefix issue the QA agent encountered during the gate fix.
>
> **Run only the new tests and verdict tests:** `cd bellows && pytest tests/test_extract_primary_deposit_blocks.py tests/test_verdict.py -v 2>&1 | tee /tmp/pytest_dev_step.txt`. Report: all 6 new tests pass, zero regressions in test_verdict.py. Do NOT proceed if any previously-passing verdict test fails.
>
> **Deposit development log** to `bellows/knowledge/development/extract-primary-deposit-block-aware-2026-04-19.md` using the canonical Python file write pattern (triple-quoted string assigned to `content` before the `with open(...) as f: f.write(content)` call). Log: function modified, module-level constants added, sync comment added, test count. Append commit message: "feat(verdict): extract_primary_deposit recognizes Rule 26 **Deposits:** blocks". Commit all changes in a single commit.
>
> **Deposits:**
> - `bellows/knowledge/development/extract-primary-deposit-block-aware-2026-04-19.md`
>
> Standard prompt feedback protocol → `bellows/knowledge/research/agent-prompt-feedback.md`.
>
> **STOP. Do NOT proceed to Step 2. Do NOT move the plan to Done. Wait for CEO confirmation before continuing.**

---
---

## STEP 2 — Bellows QA

---

> Before starting, read `bellows/knowledge/development/extract-primary-deposit-block-aware-2026-04-19.md` and check the Output Receipt status. If status is not Complete, stop and report the issue.
>
> Skip specialist file and glossary reads — this is a verification task.
>
> **FIRST — Deliverable Verification (Rule 17).** Read the DEV Output Receipt "Files Created or Modified (Code)" list. Verify every listed file exists on disk and contains the described change. Specifically: (a) `bellows/verdict.py` contains `DEPOSITS_BLOCK_RE` constant (grep for `DEPOSITS_BLOCK_RE =`), (b) `bellows/verdict.py` contains `BLOCK_BULLET_RE` constant (grep for `BLOCK_BULLET_RE =`), (c) `bellows/verdict.py` `extract_primary_deposit` function body contains `DEPOSITS_BLOCK_RE.search` (grep for `DEPOSITS_BLOCK_RE.search`), (d) `bellows/tests/test_extract_primary_deposit_blocks.py` exists and contains all 6 test function names (grep for `def test_block_single_md_path_returned`, `def test_block_multiple_md_first_returned`, `def test_block_none_bullet_returns_none`, `def test_block_directory_only_returns_none`, `def test_no_block_falls_back_to_legacy`, `def test_block_with_blockquote_prefix_still_matches`). Pipe all grep outputs to `bellows/knowledge/qa/evidence/extract-primary-deposit-block-aware-2026-04-19/grep_deliverables.txt`. Produce a verification table: | Deliverable | Expected | Status (✅/❌) | Evidence |. If any ❌, stop and report before running tests.
>
> **Targeted test run:** `cd bellows && pytest tests/test_extract_primary_deposit_blocks.py tests/test_verdict.py tests/test_gates.py tests/test_rule_26_deposit_parser.py -v 2>&1 | tee bellows/knowledge/qa/evidence/extract-primary-deposit-block-aware-2026-04-19/pytest_targeted.txt`. Scope covers: new block tests + verdict bucket + gates bucket + prior Rule 26 tests. Report: total tests, passing, failing, zero regressions expected. If any test that was passing before now fails, stop and report.
>
> **Deposit QA report** to `bellows/knowledge/qa/extract-primary-deposit-block-aware-qa-2026-04-19.md` using the canonical Python file write pattern. Report must include: (a) deliverable verification table (Rule 17), (b) targeted test results with pass/fail per test file, (c) the Rule 20 mandatory self-check Python block output verbatim.
>
> **Mandatory Rule 20 self-check** — execute verbatim and include literal stdout in QA report:
>
> ```python
> # Rule 20 — Mandatory QA Self-Check
> import os, sys
> plan_slug = "executable-extract-primary-deposit-block-aware-2026-04-19"
> qa_report_path = "bellows/knowledge/qa/extract-primary-deposit-block-aware-qa-2026-04-19.md"
> evidence_dir = f"bellows/knowledge/qa/evidence/extract-primary-deposit-block-aware-2026-04-19/"
> required_evidence_files = ["grep_deliverables.txt", "pytest_targeted.txt"]
> hedging_keywords = ["pending", "inferred", "extrapolated", "estimated", "approximate", "skipped", "assumed", "close enough", "should pass", "would pass", "not run"]
> POSITIVE_STATUS_TOKENS = ["✅", "OK", "PASS", "[x]", "done", "complete", "verified"]
> def is_positive_row(line):
>     if "|" not in line:
>         return False
>     cells = [c.strip() for c in line.split("|")]
>     for cell in cells:
>         for token in POSITIVE_STATUS_TOKENS:
>             if token == "✅":
>                 if "✅" in cell:
>                     return True
>             else:
>                 if cell.lower() == token.lower():
>                     return True
>     return False
> failures = []
> if not os.path.isdir(evidence_dir):
>     failures.append(f"CRITICAL: evidence folder missing: {evidence_dir}")
> else:
>     for fname in required_evidence_files:
>         fpath = os.path.join(evidence_dir, fname)
>         if not os.path.isfile(fpath):
>             failures.append(f"CRITICAL: evidence file missing: {fpath}")
>         elif os.path.getsize(fpath) == 0:
>             failures.append(f"CRITICAL: evidence file empty: {fpath}")
> if os.path.isfile(qa_report_path):
>     with open(qa_report_path, "r") as f:
>         report = f.read()
>     for line in report.splitlines():
>         if is_positive_row(line):
>             lower = line.lower()
>             for kw in hedging_keywords:
>                 if kw in lower:
>                     failures.append(f"CRITICAL: hedging keyword '{kw}' in positive-status row: {line.strip()[:120]}")
>                     break
> else:
>     failures.append(f"CRITICAL: QA report not found at {qa_report_path}")
> print("=" * 60)
> print("Rule 20 — QA Self-Check Results")
> print("=" * 60)
> if failures:
>     print(f"FAILED — SELF-CHECK FAILED — {len(failures)} issue(s):")
>     for f in failures:
>         print(f"  - {f}")
>     print("\nPlan CANNOT close. Fix issues and re-run QA.")
>     sys.exit(1)
> else:
>     print("PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.")
>     print(f"Evidence folder: {evidence_dir}")
>     print(f"Files verified: {len(required_evidence_files)}")
> ```
>
> **If Rule 20 self-check prints PASSED:** proceed to housekeeping in Rule 23 order. Step A — append dated entry to `bellows/knowledge/research/agent-prompt-feedback.md` with agent name, prompt summary, unnecessary reads, scope observations, and Pattern review. Step B — update `bellows/PROJECT_STATUS.md` Completed Milestones with a 2026-04-19 entry: `extract_primary_deposit` now recognizes Rule 26 `**Deposits:**` blocks — returns first `.md` path from declared block, block is authoritative (no fallback to legacy regexes when present), 6 targeted tests added. Use anchored edit_block with verbatim old_string (read the current Completed Milestones section first to get the anchor line). Step C — final commit: "test(verdict): add block-aware extract_primary_deposit tests + QA report + status update". Step D — move plan to Done: `import shutil; shutil.move("bellows/knowledge/decisions/in-progress-executable-extract-primary-deposit-block-aware-2026-04-19.md", "bellows/knowledge/decisions/Done/executable-extract-primary-deposit-block-aware-2026-04-19.md")`. Move-to-Done is the absolute last operation.
>
> **Deposits:**
> - `bellows/knowledge/qa/extract-primary-deposit-block-aware-qa-2026-04-19.md`
> - `bellows/knowledge/qa/evidence/extract-primary-deposit-block-aware-2026-04-19/` (grep_deliverables.txt, pytest_targeted.txt)
>
> Standard prompt feedback protocol → `bellows/knowledge/research/agent-prompt-feedback.md`.
