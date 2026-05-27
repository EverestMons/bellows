# Bellows — Leftover-After-Ship Tooling Implementation
**Date:** 2026-05-26 | **Tier:** small-build | **Dispatch Mode:** bellows | **Test Scope:** targeted | **Execution:** Step 1 (DEV) → Step 2 (QA) | **qa_steps:** 2 | **pause_for_verdict:** after_step_1

## How to Run This Plan

Deposit into `bellows/knowledge/decisions/`. Bellows claims and dispatches Step 1 (DEV) — agent implements the script per the SA blueprint and runs it against the live repo, capturing the produced report. Plan pauses for CEO review of the implementation and output. After continue verdict, Step 2 (QA) verifies the script's correctness.

## Context

SA blueprint shipped at `bellows/knowledge/research/leftover-after-ship-tooling-blueprint-2026-05-26.md`. Blueprint covers four matching sources (BACKLOG Open, BACKLOG Closed, PROJECT_STATUS Completed, git log) with source-specific thresholds and a length-guard on Closed-section matching. Ground-truth trace verifies all 4 recurrence cases catch with zero false positives against the 6 currently-Open entries. Script target: `bellows/scripts/check_backlog_freshness.py`, Python stdlib only, 150-250 LOC, read-only.

CEO scope decisions locked from prior plans: v1 covers code-shipped pattern (4 ground-truth recurrences) plus the Closed-duplicate variant the SA discovered; output destination is `knowledge/research/backlog-freshness-check-<DATE>.md`; no pytest, hand-test against 4 ground-truth cases.

---
---

## STEP 1 — DEV

---

> **FIRST — before doing anything else, claim this plan:** `import shutil; shutil.move("bellows/knowledge/decisions/executable-leftover-after-ship-tooling-implementation-2026-05-26.md", "bellows/knowledge/decisions/in-progress-executable-leftover-after-ship-tooling-implementation-2026-05-26.md")`. Read your specialist file and domain glossary first. Read the SA blueprint at `bellows/knowledge/research/leftover-after-ship-tooling-blueprint-2026-05-26.md` and check the Output Receipt status field. If status is not Complete, stop and report the issue before proceeding. **Task:** implement `bellows/scripts/check_backlog_freshness.py` literally per the blueprint — constants from Section 1, parsing per Section 2 (all four sources: BACKLOG Open, BACKLOG Closed, PROJECT_STATUS Completed, git log), matching algorithm per Section 3 with the final thresholds from Section 7, output format per Section 4, CLI per Section 5. Style: match `bellows/scripts/migrate_config.py` — shebang `#!/usr/bin/env python3`, module-level docstring, module-level constants, single `main()` entry, `if __name__ == "__main__": main()` guard. Target 150-250 LOC; stay within range. **After implementing**, run the script: `cd bellows && python scripts/check_backlog_freshness.py`. The script will deposit the report at `bellows/knowledge/research/backlog-freshness-check-2026-05-26.md`. Read the produced report. **Manual ground-truth trace:** the script is being run against current state where the 4 ground-truth recurrences are already Closed, so the report shouldn't surface them as candidates against current Open entries. Instead, hand-trace the algorithm by reading the 4 ground-truth cases from the blueprint Section 6 and confirming the implementation matches the traced behavior for each. Document this trace in the dev log. **Constraints:** Python stdlib only — `pathlib`, `re`, `subprocess`, `argparse`, `datetime`. No requests, no yaml, no rich. No mutations to BACKLOG.md, PROJECT_STATUS.md, or any source file. All git commands use `git --no-pager`. Idempotent. Exit 0 always. **Deposits:**
> - `bellows/knowledge/development/leftover-after-ship-tooling-implementation-2026-05-26.md` — dev log per `SPECIALIST_TEMPLATE.md` with implementation notes, the script's actual produced output excerpted (header summary + 2-3 sample Open-entry sections), and the manual ground-truth trace confirming each of the 4 cases would be caught
>
> The freshness report file (`bellows/knowledge/research/backlog-freshness-check-2026-05-26.md`) is a side effect of running the script, created by the script itself, and is NOT listed as a deposit.
>
> Standard prompt feedback protocol → `bellows/knowledge/research/agent-prompt-feedback.md`.

---
---

## STEP 2 — QA

---

> Before starting, read `bellows/knowledge/development/leftover-after-ship-tooling-implementation-2026-05-26.md` and check the Output Receipt status field. If status is not Complete or Partial with known acceptable scope, stop and report the issue before proceeding. Read your specialist file and domain glossary first. **Verification checks:**
>
> 1. **Script exists, executable, in target LOC range** — `ls -la bellows/scripts/check_backlog_freshness.py` shows the file; `wc -l bellows/scripts/check_backlog_freshness.py` shows 150-250 lines; `head -5` shows canonical shebang `#!/usr/bin/env python3` and a module docstring opening.
> 2. **Stdlib-only** — `grep -E "^import |^from " bellows/scripts/check_backlog_freshness.py` shows only stdlib modules. Any third-party import is FAIL.
> 3. **Idempotency** — run the script twice with a sleep in between; capture both outputs and diff them. Byte-identical output is PASS.
> 4. **No mutations** — `git status` after running the script shows only the deposited freshness report file as modified or untracked. Any other modified file (BACKLOG.md, PROJECT_STATUS.md, scripts/ source) is FAIL.
> 5. **Ground-truth trace** — read the dev log's Section on the manual ground-truth trace. Confirm each of the 4 recurrences (set→list, precondition-failure-field, Phase 3b read-side, mcp\_\_vexp\_\_) is traced through the implemented algorithm with evidence that the implementation matches the blueprint's Section 6 trace. PASS only if all 4 traces are coherent and the implementation behavior matches.
> 6. **False-positive review** — read the freshness report produced by the live run. For each Open entry that the script flagged as `investigate-as-shipped`, manually verify by reading the cited evidence whether the candidate match is plausible or a false positive. Document each flagged entry's verdict in the QA report. PASS = zero false positives. PARTIAL = false positives surfaced but all 4 ground-truth traces still valid.
> 7. **Report file shape** — the produced freshness report has the header summary line (window, entries scanned, candidates surfaced, no-match counts), one `## Entry N` section per Open entry in BACKLOG order, candidate subsections cite source type with evidence excerpts, and entries with no candidates show "(no candidates found)".
> 8. **CLI smoke** — `python bellows/scripts/check_backlog_freshness.py --window-days 30` runs without error and produces a report. `python bellows/scripts/check_backlog_freshness.py --help` prints usage.
>
> Run the full canonical Rule 20 self-check block from `RULE_20_SELF_CHECK_BLOCK.md` with these context values: `plan_slug = executable-leftover-after-ship-tooling-implementation-2026-05-26`, `qa_report_path = bellows/knowledge/qa/executable-leftover-after-ship-tooling-implementation-2026-05-26.md`, `evidence_dir = bellows/knowledge/qa/evidence/executable-leftover-after-ship-tooling-implementation-2026-05-26/`, `required_evidence_files = [check1_script_inspect.txt, check2_imports.txt, check3_idempotency_diff.txt, check4_git_status.txt, check5_ground_truth_trace.md, check6_false_positive_review.md, check7_report_shape.txt, check8_cli_smoke.txt]`.
>
> Update `bellows/PROJECT_STATUS.md` with a Completed entry for this plan as a side effect — NOT listed in deposits.
>
> **Deposits:**
> - `bellows/knowledge/qa/executable-leftover-after-ship-tooling-implementation-2026-05-26.md` — QA report including all 8 verification checks with PASS/FAIL/PARTIAL per check, the Rule 20 self-check banner block, and the standard Output Receipt
>
> Standard prompt feedback protocol → `bellows/knowledge/research/agent-prompt-feedback.md`.
