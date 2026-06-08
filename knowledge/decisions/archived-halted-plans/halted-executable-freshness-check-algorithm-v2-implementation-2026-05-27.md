# Bellows — Freshness-Check Algorithm V2 Implementation
**Date:** 2026-05-27 | **Tier:** small-build | **Dispatch Mode:** bellows | **Test Scope:** targeted | **Execution:** Step 1 (DEV) → Step 2 (QA) | **qa_steps:** 2 | **pause_for_verdict:** after_step_1

## How to Run This Plan

Deposit into `bellows/knowledge/decisions/`. Bellows dispatches Step 1 (DEV) — agent edits `bellows/scripts/check_backlog_freshness.py` per the v2 blueprint Section 5, runs the script, captures the new live report. Plan pauses for CEO review. After continue verdict, Step 2 (QA) verifies parity with the implementation plan structure used for v1.

## Context

V2 blueprint at `bellows/knowledge/research/freshness-check-algorithm-v2-blueprint-2026-05-27.md`. CEO-accepted scope and dispositions:
- v2 ships as a candidate surfacer, not a closure detector — algorithm cannot achieve zero FPs due to inherent limits of term matching across same-function-different-bug entries
- v2 reduces FP entries from 6/6 to 4/6, candidates from 39 to 15 (~60% noise reduction)
- All 4 ground-truth recurrences still catch
- Algorithm-only change: `extract_fingerprint()` and `find_candidates()` only; remove `STOPWORDS` constant
- Parsing, output format, CLI, helper utilities, regexes all unchanged

V1 implementation at `bellows/scripts/check_backlog_freshness.py` (239 LOC). V1 live output at `bellows/knowledge/research/backlog-freshness-check-2026-05-26.md` (will be overwritten by v2 run). V1 dev log at `bellows/knowledge/development/leftover-after-ship-tooling-implementation-2026-05-26.md`.

---
---

## STEP 1 — DEV

---

> **FIRST — before doing anything else, claim this plan:** `import shutil; shutil.move("bellows/knowledge/decisions/executable-freshness-check-algorithm-v2-implementation-2026-05-27.md", "bellows/knowledge/decisions/in-progress-executable-freshness-check-algorithm-v2-implementation-2026-05-27.md")`. Read your specialist file and domain glossary first. Read the v2 blueprint at `bellows/knowledge/research/freshness-check-algorithm-v2-blueprint-2026-05-27.md`, especially Section 5 which contains the line-level edit guidance and the exact Python code to use. Check the Output Receipt status field; if not Complete, stop and report. **Task:** apply Section 5's edits to `bellows/scripts/check_backlog_freshness.py`. Specifically: (a) rewrite the body of `extract_fingerprint()` per the code in Section 5 — 4 extraction rules (backtick ≥ 5, hyphenated ≥ 12, underscore ≥ 8 with ≥ 2 underscores, executable slugs), title-word matching removed. (b) modify `find_candidates()` per the code in Section 5 — git threshold ≥ 1, PS slug-token floor ≥ 6 chars with threshold ≥ 1, BACKLOG Closed rule with long-term-or-backtick-match condition. (c) delete the `STOPWORDS` constant. (d) leave EVERYTHING ELSE unchanged: parsing functions, regexes, utilities (`score_overlap`, `tokenize_slug`), `generate_report`, `main`, CLI argparse, constants (`BELLOWS_ROOT`, `BACKLOG_PATH`, etc.), shebang, module docstring, `__main__` guard. **Before running the script**, preserve the v1 output: `cp bellows/knowledge/research/backlog-freshness-check-2026-05-26.md /tmp/v1-freshness-report.md`. Then run: `cd bellows && python scripts/check_backlog_freshness.py`. The script overwrites the report with v2 output. **Validation:** read the new live report. Compare candidate counts against v1: blueprint predicts 6/6 → 4/6 FP entries and 39 → 15 candidates. Confirm the directional change matches; small numerical differences are acceptable (e.g., 14 or 16 candidates) but a wild deviation (e.g., still 30+ or under 10) implies an implementation error. **Manual ground-truth re-trace:** for each of the 4 recurrences from blueprint Section 4, confirm by reading the implementation that the algorithm path traced in the blueprint matches the code. **Constraints:** Python stdlib only. Read-only outside the script edit and the report overwrite. All git commands `--no-pager`. Final LOC should be approximately 234 (≈ -5 from v1's 239). **Deposits:**
> - `bellows/knowledge/development/freshness-check-algorithm-v2-implementation-2026-05-27.md` — dev log per `SPECIALIST_TEMPLATE.md`: summary of code changes (functions modified, constants removed, what stayed), v1-vs-v2 output comparison (header summary counts + 2-3 sample entries showing reduction), manual ground-truth re-trace confirming all 4 cases still catch in the implementation
>
> The freshness report (`bellows/knowledge/research/backlog-freshness-check-2026-05-26.md`) is a side effect of running the script and is NOT listed as a deposit.
>
> Standard prompt feedback protocol → `bellows/knowledge/research/agent-prompt-feedback.md`.

---
---

## STEP 2 — QA

---

> Before starting, read `bellows/knowledge/development/freshness-check-algorithm-v2-implementation-2026-05-27.md` and check the Output Receipt status field. If status is not Complete or Partial with known acceptable scope, stop and report. Read your specialist file and domain glossary first. **Verification checks:**
>
> 1. **Script LOC within range** — `wc -l bellows/scripts/check_backlog_freshness.py` shows approximately 230-240 lines (v1 was 239; v2 net delta ≈ -5).
> 2. **Stdlib-only preserved** — `grep -E "^import |^from " bellows/scripts/check_backlog_freshness.py` shows only stdlib modules. Any third-party import is FAIL.
> 3. **STOPWORDS removed** — `grep -n "STOPWORDS" bellows/scripts/check_backlog_freshness.py` returns no matches.
> 4. **Idempotency** — run the script twice with a sleep between; diff both outputs. Byte-identical is PASS.
> 5. **No mutations outside scope** — `git status` after running shows only the script file and the freshness report file as modified. Any other modified file is FAIL.
> 6. **FP reduction achieved** — read the v2 freshness report header summary. Confirm candidate count is materially reduced from v1 (v1 was 39 candidates across 6/6 entries; blueprint predicts 15 across 4/6). Acceptable range: 10-20 candidates total, 3-5 entries flagged as `investigate-as-shipped`. Anything outside this range is FAIL (PARTIAL acceptable if all 4 ground-truth cases still trace).
> 7. **Ground-truth still catches all 4 cases** — read the dev log's ground-truth re-trace section. Confirm each of the 4 recurrences is traced through the v2 implementation and the catch path is verified. PASS only if all 4 still trigger.
> 8. **Scope-fence check** — confirm parsing, output format, CLI, helper utilities, regexes, and module-level constants are unchanged from v1. Inspect git diff of the script (`git --no-pager diff bellows/scripts/check_backlog_freshness.py`); changes outside `extract_fingerprint()`, `find_candidates()`, and the `STOPWORDS` removal are FAIL unless explicitly justified in the dev log.
> 9. **CLI smoke** — `python bellows/scripts/check_backlog_freshness.py --window-days 30` runs without error. `--help` prints usage.
>
> Run the full canonical Rule 20 self-check block from `RULE_20_SELF_CHECK_BLOCK.md` with these context values: `plan_slug = executable-freshness-check-algorithm-v2-implementation-2026-05-27`, `qa_report_path = bellows/knowledge/qa/executable-freshness-check-algorithm-v2-implementation-2026-05-27.md`, `evidence_dir = bellows/knowledge/qa/evidence/executable-freshness-check-algorithm-v2-implementation-2026-05-27/`, `required_evidence_files = [check1_loc.txt, check2_imports.txt, check3_stopwords_grep.txt, check4_idempotency_diff.txt, check5_git_status.txt, check6_fp_reduction.md, check7_ground_truth_retrace.md, check8_scope_fence_diff.md, check9_cli_smoke.txt]`.
>
> Update `bellows/PROJECT_STATUS.md` with a Completed entry for this plan as a side effect — NOT listed in deposits.
>
> **Deposits:**
> - `bellows/knowledge/qa/executable-freshness-check-algorithm-v2-implementation-2026-05-27.md` — QA report with all 9 verification checks (PASS/FAIL/PARTIAL per check), the Rule 20 self-check banner block, and the standard Output Receipt
>
> Standard prompt feedback protocol → `bellows/knowledge/research/agent-prompt-feedback.md`.
