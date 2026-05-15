# bellows — Plan Truncation Fix v2 (Cache total_steps)
**Date:** 2026-04-17 | **Type:** Executable | **Priority:** 1

## How to Run This Plan

**Bootstrap:** `Read the plan at bellows/knowledge/decisions/executable-plan-truncation-fix-v2-2026-04-17.md. Execute it fully. Deposit your development log and report Complete when done.`

---

## STEP 1 — DEV

---

> **FIRST — claim this plan:** `import shutil; shutil.move("bellows/knowledge/decisions/executable-plan-truncation-fix-v2-2026-04-17.md", "bellows/knowledge/decisions/in-progress-executable-plan-truncation-fix-v2-2026-04-17.md")`. Read `bellows/bellows.py` in full. **The problem:** Claude Code agents rewrite the plan file during execution via Write/Edit tools. When Bellows re-reads the file for step counting (during verdict consumption at line ~565), it sees a truncated file with fewer `## STEP` headers and treats the plan as complete prematurely. **The fix has 2 parts:**
>
> **(1) Store `total_steps` in the verdict-request file.** In `verdict.py`, `post_verdict_request`: add `**Total Steps:** {total_steps}` to the verdict-request content. The function needs a new `total_steps` parameter. Update both call sites in `bellows.py` (the while-loop pause and the final-step pause) to pass `total_steps` to `post_verdict_request`.
>
> **(2) Read `total_steps` from verdict-request during consumption.** In `bellows.py`, `_consume_verdicts`: where the code currently does `plan_text_c = load_file(full_plan_path)` followed by `total_steps_c = 1 if is_diag else extract_total_steps(plan_text_c)` — replace this with reading `total_steps` from the pending verdict-request file. The verdict-request file path is already known at that point (`pending_req_file`). Parse the `**Total Steps:**` line from it. Fall back to the current `extract_total_steps` behavior only if the verdict-request file doesn't have the field (backward compat with old verdict files).
>
> **(3) Defensive: also cache `plan_text` in `run_plan`.** At the top of `run_plan`, `plan_text = load_file(plan_path)` already caches the content. Ensure that ALL uses of `total_steps` within `run_plan` use the variable computed at line ~154 — never re-read and re-compute. Grep for any other `extract_total_steps` or `load_file` calls within `run_plan` that might re-read the plan after the agent has modified it.
>
> Run any existing tests. Commit: `fix: cache total_steps in verdict metadata — prevent agent truncation from breaking step count`. **Deposit dev log** to `bellows/knowledge/development/plan-truncation-fix-v2-2026-04-17.md` using canonical Python file write. Standard prompt feedback protocol → `bellows/knowledge/research/agent-prompt-feedback.md`.
>
> **STOP. Do NOT proceed further. Wait for CEO confirmation.**
