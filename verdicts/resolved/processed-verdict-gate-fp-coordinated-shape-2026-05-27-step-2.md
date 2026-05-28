verdict: continue
Rule 22 (d) override — gate failure was a Planner-authoring error, not a substantive QA failure.

Root cause: the plan's Step 1 and Step 2 Deposits blocks were authored with `### Deposits` markdown h3 headers instead of the Rule 26-mandated `**Deposits:**` bold-colon format. The `_extract_plan_required_deposits` regex at `gates.py:418` matches only the bold-colon form; with no match, `md_paths` is empty for the QA step and `_gate_rule_20_self_check` at `gates.py:471` fires the documented "deposits block declares no .md paths" failure (gate signal correctly identifies the Planner-authoring failure mode per the 2026-05-26 evidence-string disambiguation ship).

Plan file corrected on disk: both Step 1 and Step 2 Deposits blocks rewritten to `**Deposits:**` form via Desktop Commander edit on `verdict-pending-executable-gate-fp-coordinated-shape-2026-05-27.md`. Edit is safe per `is_runnable_plan()` at `bellows.py:967` — files with `verdict-pending-*` prefix return False, so the `on_modified` handler's `_handle(path)` call bails before dispatch, and the lifecycle-prefix guard at `bellows.py:1043` prevents `_seen` invalidation. No re-dispatch trigger fired (verified by tailing bellows log immediately after edit — no new events).

Substance verification (Rule 22(b)):
- QA report at `bellows/knowledge/qa/executable-gate-fp-coordinated-shape-2026-05-27.md` shows all 5 deliverables ✅: code shape verification, 3 per-fix FP reproduction tests, 3 per-fix counter-tests, 133-test adjacent suite (0 failed in 0.17s), Rule 20 self-check banner present with `RULE 20 SELF-CHECK: PASSED` line.
- DEV's two flagged existing-test fixtures (`test_rule_22_qa_hedging_keyword`, `test_rule_22_qa_both_fail_and_hedging`) updated per the DEV log's prediction. No additional fixture modifications surfaced.
- No deviations from spec; no divergence from diagnostic predictions.

All three BACKLOG FP entries closed by this ship:
- `ceo_flags` null-declaration FP — closed via `_is_null_flag_declaration` at `gates.py:73`.
- `rule_22_verification` (c) row-status FP — closed via defer-and-discard pattern at `gates.py:558-611`.
- Hedging-detector domain-term FP — closed via `_hedging_in_status_vicinity` at `gates.py:94` plus `in_verification_section_d` scoping at `gates.py:614-620`.

Pattern note for session-wrap:
- Second Planner-authoring failure today (first was staging file at sandbox path instead of governance root). LESSONS candidate: pre-deposit `**Deposits:**` format check — the canonical regex is strict (bold-colon-newline), and the visual similarity between `### Deposits` and `**Deposits:**` makes the failure mode latent until a QA step trips Rule 20.
- This run's authoring error was caught at the right moment (gate failure surfaced on QA step) by the 2026-05-26 evidence-string disambiguation ship — exactly the design intent of distinguishing line 441 (Planner-authoring failure) from line 464 (QA-agent banner failure). Validation of that earlier ship.

Daemon restart REQUIRED after this plan moves to Done/ to load the new `gates.py` symbols. Surfacing in session-wrap operational notes.
