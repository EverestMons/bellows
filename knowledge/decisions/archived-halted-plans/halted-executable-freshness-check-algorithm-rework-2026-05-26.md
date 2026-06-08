# Bellows — Freshness-Check Algorithm Rework
**Date:** 2026-05-26 | **Tier:** small-build | **Dispatch Mode:** bellows | **Test Scope:** targeted | **Execution:** Step 1 (SA) → Step 2 (DEV) → Step 3 (QA) | **qa_steps:** 3 | **pause_for_verdict:** after_step_1

## How to Run This Plan

Deposit into `bellows/knowledge/decisions/`. Bellows dispatches Step 1 (SA) to redesign the matching-distinctiveness logic. Plan pauses for CEO review. After continue verdict, Step 2 (DEV) edits the existing script and reruns it. Step 3 (QA) verifies parity with the v1 implementation plan structure.

## Context

V1 implementation at `bellows/scripts/check_backlog_freshness.py` (239 LOC) ran successfully but produced 6/6 false-positive flag rate against the 6 currently-Open BACKLOG entries. V1 blueprint at `bellows/knowledge/research/leftover-after-ship-tooling-blueprint-2026-05-26.md`. V1 live output at `bellows/knowledge/research/backlog-freshness-check-2026-05-26.md`. V1 dev log at `bellows/knowledge/development/leftover-after-ship-tooling-implementation-2026-05-26.md` documents the implementation and the 4 ground-truth traces that DO pass.

**The failure mode is matching distinctiveness, not parsing or scoring count.** Generic shared-vocabulary terms (`project`, `status`, `output`, `files`, `match`, `verdict`, `diagnostic`, `teardown`, `parser`, `deposits`) appear in nearly every Bellows-domain entry. Two such terms co-occurring is the norm, not the signal. The 4 ground-truth cases all had at least one *highly distinctive* term: full function name (`_extract_plan_required_deposits`), full executable slug, or unique compound noun (`step-state-resume`, `precondition-failure`).

CEO scope decisions for v2:
- Keep BACKLOG Closed-section matching (Case 2's only signal)
- Lean algorithm: match only on high-distinctiveness terms — backtick identifiers, hyphenated compounds, function-call signatures, executable slugs
- Drop title-word matching entirely
- Preserve all other v1 logic: parsing of 4 sources, output format, CLI, constants
- Edit v1 script in place, not rewrite

---
---

## STEP 1 — SA

---

> **FIRST — before doing anything else, claim this plan:** `import shutil; shutil.move("bellows/knowledge/decisions/executable-freshness-check-algorithm-rework-2026-05-26.md", "bellows/knowledge/decisions/in-progress-executable-freshness-check-algorithm-rework-2026-05-26.md")`. Read your specialist file and domain glossary first. Read three files: v1 blueprint at `bellows/knowledge/research/leftover-after-ship-tooling-blueprint-2026-05-26.md`, v1 dev log at `bellows/knowledge/development/leftover-after-ship-tooling-implementation-2026-05-26.md`, v1 live output at `bellows/knowledge/research/backlog-freshness-check-2026-05-26.md`. **After reading, before drafting, post a 3-5 line plan-of-attack** sketching how you intend to redesign the distinctiveness logic. Liveness signal AND early steering. **Then draft a blueprint addendum.** The addendum redesigns the matching-distinctiveness logic only — it MUST NOT change parsing logic for any of the 4 sources, MUST NOT change output format, MUST NOT change CLI, MUST NOT change constants. Specifically: **(1) High-distinctiveness term extraction.** Replace the current `extract_fingerprint()` function. Keep only: backtick-delimited identifiers (length ≥ 5), hyphenated compounds (length ≥ 12 chars total), underscore identifiers (length ≥ 8 chars, ≥ 2 underscores), executable slugs cited in the entry text. DROP: title-word matching entirely. State the regex shapes literally. **(2) Per-source matching rules.** Git log: require `≥ 1` high-distinctiveness term overlap (down from score ≥ 2 of mixed-quality terms; one strong term beats two weak ones). PROJECT_STATUS: require `≥ 1` slug-token overlap where the slug token is itself ≥ 6 chars (drops generic 3-letter tokens like `mcp`, `set`, `api`). BACKLOG Closed: require `≥ 1` high-distinctiveness term overlap where that term is ≥ 12 chars OR the term is the same backticked identifier in both entries. **(3) False-positive validation against the 6 currently-Open entries.** Read v1 live output carefully. For each of the 6 Open entries, list every v1-flagged candidate, then apply the v2 rules and state whether v2 would still flag it. Target: zero false positives. If any v1 false positive survives v2 rules, identify it and propose a further refinement. **(4) Ground-truth re-validation.** For each of the 4 recurrences (set→list, precondition-failure-field, Phase 3b read-side, mcp\_\_vexp\_\_), trace v2 rules and confirm the catch still works. State which terms qualify as high-distinctiveness in each fingerprint and which candidate sources still trigger. PASS only if all 4 still catch. **(5) Implementation-edit guidance.** State what code changes are needed in `scripts/check_backlog_freshness.py` — which functions to modify, which constants to change, what stays identical. The DEV agent should be able to apply your guidance as a targeted edit, not a rewrite. **Constraints:** No new dependencies (still Python stdlib only). Algorithm-only change — same parsing, same output, same CLI. Keep edit scope minimal. **Deposits:**
> - `bellows/knowledge/research/freshness-check-algorithm-rework-blueprint-2026-05-26.md` — addendum per (1)-(5) above
>
> Standard prompt feedback protocol → `bellows/knowledge/research/agent-prompt-feedback.md`.

---
---

## STEP 2 — DEV

---

> Before starting, read `bellows/knowledge/research/freshness-check-algorithm-rework-blueprint-2026-05-26.md` and check the Output Receipt status field. If status is not Complete, stop and report the issue before proceeding. Read your specialist file and domain glossary first. **Task:** edit `bellows/scripts/check_backlog_freshness.py` in place per the SA addendum. Apply Section (1) to replace `extract_fingerprint()`. Apply Section (2) to update per-source matching rules in their respective scoring sites. Do not modify parsing functions, output formatting, CLI, or constants unless the addendum's Section (5) explicitly calls for it. Before running the script, preserve a copy of the v1 report: `cp bellows/knowledge/research/backlog-freshness-check-2026-05-26.md /tmp/v1-freshness-report.md`. Then run the script: `cd bellows && python scripts/check_backlog_freshness.py`. The script overwrites the report. **Validation:** read the new live report. Confirm (a) the candidates-surfaced count dropped substantially from 6/6 and (b) for any remaining flagged entry, the cited match is plausibly the actual closure event, not topic-adjacent noise. Compare with `/tmp/v1-freshness-report.md` and document the diff in the dev log. **Manual ground-truth re-trace:** confirm each of the 4 recurrences would still be caught by tracing through the edited code paths. **Constraints:** Python stdlib only. Read-only outside the script edit and the report deposit. All git commands `--no-pager`. Final LOC should still be in the 150-250 range — significantly above implies scope creep. **Deposits:**
> - `bellows/knowledge/development/freshness-check-algorithm-rework-2026-05-26.md` — dev log: diff summary of code changes, v1-vs-v2 output comparison (counts and a few sample entries), manual ground-truth re-trace confirming all 4 cases still catch
>
> The freshness report (`bellows/knowledge/research/backlog-freshness-check-2026-05-26.md`) is a side effect of running the script and is NOT listed as a deposit.
>
> Standard prompt feedback protocol → `bellows/knowledge/research/agent-prompt-feedback.md`.

---
---

## STEP 3 — QA

---

> Before starting, read `bellows/knowledge/development/freshness-check-algorithm-rework-2026-05-26.md` and check the Output Receipt status field. If status is not Complete or Partial with known acceptable scope, stop and report the issue before proceeding. Read your specialist file and domain glossary first. **Verification checks:**
>
> 1. **Script LOC within range** — `wc -l bellows/scripts/check_backlog_freshness.py` shows 150-250 lines. Above 250 implies scope creep beyond algorithm tightening.
> 2. **Stdlib-only preserved** — `grep -E "^import |^from " bellows/scripts/check_backlog_freshness.py` shows only stdlib modules. Any third-party import is FAIL.
> 3. **Idempotency** — run the script twice with a sleep between; diff both outputs. Byte-identical is PASS.
> 4. **No mutations outside scope** — `git status` after running shows only the script file and the freshness report file as modified. Any other modified file is FAIL.
> 5. **Ground-truth still catches all 4 cases** — read the dev log's ground-truth re-trace section. Confirm each of the 4 recurrences (set→list, precondition-failure-field, Phase 3b read-side, mcp\_\_vexp\_\_) is traced through the v2 algorithm and the catch still works. PASS only if all 4 still trigger.
> 6. **False-positive reduction verified** — read the v2 freshness report. Compare candidate counts: v1 was 6/6 entries flagged. v2 must show substantial reduction. For each v2-flagged entry, manually verify the cited match is plausibly the actual closure event, not topic-adjacent noise. Document each flagged entry's verdict in the QA report. PASS = zero false positives. PARTIAL = some false positives remain but ≥ 50% reduction from v1 and all 4 ground-truth still trigger.
> 7. **Scope-fence check** — confirm parsing logic for the 4 sources, output format, CLI argument shape, and module-level constants are unchanged from v1. Inspect the script and dev log diff; any change outside `extract_fingerprint()` and per-source matching rules is FAIL unless the SA addendum's Section (5) explicitly authorized it.
> 8. **CLI smoke** — `python bellows/scripts/check_backlog_freshness.py --window-days 30` runs without error. `--help` prints usage.
>
> Run the full canonical Rule 20 self-check block from `RULE_20_SELF_CHECK_BLOCK.md` with these context values: `plan_slug = executable-freshness-check-algorithm-rework-2026-05-26`, `qa_report_path = bellows/knowledge/qa/executable-freshness-check-algorithm-rework-2026-05-26.md`, `evidence_dir = bellows/knowledge/qa/evidence/executable-freshness-check-algorithm-rework-2026-05-26/`, `required_evidence_files = [check1_loc.txt, check2_imports.txt, check3_idempotency_diff.txt, check4_git_status.txt, check5_ground_truth_retrace.md, check6_false_positive_verdicts.md, check7_scope_fence.md, check8_cli_smoke.txt]`.
>
> Update `bellows/PROJECT_STATUS.md` with a Completed entry for this plan as a side effect — NOT listed in deposits.
>
> **Deposits:**
> - `bellows/knowledge/qa/executable-freshness-check-algorithm-rework-2026-05-26.md` — QA report with all 8 verification checks (PASS/FAIL/PARTIAL per check), the Rule 20 self-check banner block, and the standard Output Receipt
>
> Standard prompt feedback protocol → `bellows/knowledge/research/agent-prompt-feedback.md`.
