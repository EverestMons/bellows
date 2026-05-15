# Bellows — `_gate_rule_20_self_check` False Positive on 2026-05-12 Won't-Fix Close
**Date:** 2026-05-12 | **Tier:** Diagnostic | **Test Scope:** n/a (investigation) | **Execution:** Step 1 (SA) | **pause_for_verdict:** after_step_1

## How to Run This Plan

Paste the bootstrap prompt into Claude Code. The agent reads the full plan file and executes Step 1 ONLY. After completing Step 1, the agent STOPS and waits for CEO confirmation ("ok") before the Planner advances to closeout.

## CEO Context

The `rule_20_self_check` gate produced a false positive on Step 2 (QA) of `executable-bellows-self-exposure-wontfix-close-2026-05-12`. The verdict request stated `Gate Failures: rule_20_self_check: no QA deposit contains Rule 20 self-check banner`, but direct Rule 22 verification of the QA report shows:

- File exists at `/Users/marklehn/Desktop/GitHub/bellows/knowledge/qa/bellows-self-exposure-wontfix-close-qa-2026-05-12.md`
- Literal banner `Rule 20 — QA Self-Check Results` is present (line 26 of the QA report)
- `PASSED — SELF-CHECK PASSED` line is immediately after the banner (line 27)
- All 5 verification rows in the QA report report PASS
- No hedging keywords in the prose
- Step 1 commit `ca8eb8f` shipped with correct subject and exactly 2 files

The substantive work is correct. The gate is producing a false negative on banner detection. Planner override via Rule 22 has been posted, but the gate behavior is worth understanding.

Three candidate causes the Planner cannot distinguish without reading source:

- **(a) Deposit enumeration parser issue.** The plan's `**Deposits:**` block uses an inline format: two bullets comma-separated on a single line with backtick-wrapped paths. Working historical example (`executable-path-001-hygiene-close-2026-05-11`) uses a multi-line format with each bullet on its own line. The deposit parser may not enumerate the QA report when bullets are inlined, falling through to a different file that legitimately lacks the banner.
- **(b) Fence-strip false negative.** The 2026-05-11 fence-strip close (commit `4d57fd3`) added `strip_fenced_code_blocks()` to four plan-text parsers. If `_gate_rule_20_self_check` also applies fence-stripping when searching for the banner, the search would find no banner — because my QA report (and historical working ones, e.g. `path-001-hygiene-close-qa-2026-05-11.md`) wraps the Rule 20 block in triple-backtick fences.
- **(c) Path resolution drift.** The 2026-05-10 close (RC1, `executable-rule-20-self-check-wt-path-2026-05-10`) made `_gate_rule_20_self_check` worktree-aware. For bellows-self plans (no worktree, `wt_path == project_path`), path resolution should be straightforward, but a regression or edge case may exist.

Investigate which cause is the proximate one for this specific gate trip, and assess whether other recent QA reports with the same Deposits-block inline format would have tripped the same way. The recommendation goes to the Planner; the Planner brings it to the CEO if a code fix or governance edit is warranted.

---
---

## STEP 1 — SA

---

> **FIRST — before doing anything else, claim this plan:** `import shutil; shutil.move("/Users/marklehn/Desktop/GitHub/bellows/knowledge/decisions/diagnostic-rule-20-gate-false-positive-2026-05-12.md", "/Users/marklehn/Desktop/GitHub/bellows/knowledge/decisions/in-progress-diagnostic-rule-20-gate-false-positive-2026-05-12.md")`.
>
> You are the Bellows Systems Analyst. Read your specialist file at `bellows/agents/BELLOWS_SYSTEMS_ANALYST.md` first. Skip the domain glossary — Bellows has no glossary and this is an architectural debugging task. **Investigate four questions and deposit findings. Do not propose plans, do not fix anything, do not modify any source. Do not modify QA reports or gates code.** **Q1 — Trace `_gate_rule_20_self_check` against the specific 2026-05-12 inputs.** Read the current `bellows/gates.py` and identify `_gate_rule_20_self_check`. Walk through the function step-by-step against these inputs: plan file at `/Users/marklehn/Desktop/GitHub/bellows/knowledge/decisions/Done/executable-bellows-self-exposure-wontfix-close-2026-05-12.md` (will be in Done/ by the time you read it; if not yet there, check `verdict-pending-executable-bellows-self-exposure-wontfix-close-2026-05-12.md` in `decisions/`), QA report at `/Users/marklehn/Desktop/GitHub/bellows/knowledge/qa/bellows-self-exposure-wontfix-close-qa-2026-05-12.md`, project_path=`/Users/marklehn/Desktop/GitHub/bellows`, wt_path=`/Users/marklehn/Desktop/GitHub/bellows` (bellows-self, monorepo-detect-and-skip). For each step in the function — deposit enumeration, candidate file resolution, file read, banner search — state (i) the inputs at that step, (ii) the line numbers, (iii) the actual return value or branch taken. Identify the exact line where the function decides the banner is absent. Cite line numbers throughout. **Q2 — Classify the proximate cause.** Given Q1's trace, classify the root cause as one of: (a) Deposit enumeration parser issue — the gate's deposit-list parser does not include the QA report path among its candidates (state why — inline-bullet format, comma-separator, backtick-wrapping, or other), (b) Fence-strip false negative — the gate applies `strip_fenced_code_blocks()` or equivalent before banner search and the banner lives inside a fenced block, (c) Path resolution drift — the gate resolves the QA report to a wrong absolute path that does not exist or contains different content, (d) Other — name the cause. Be specific about which lines implement the failing logic. **Q3 — Population check.** Enumerate the last 10 QA reports in `bellows/knowledge/qa/` (sorted by mtime, newest first) and the last 10 in `invoice-pulse/knowledge/qa/` (same). For each, classify the Rule 20 banner location: (i) inside a triple-backtick fenced code block, (ii) outside any code block (plain markdown). Then classify each plan's `**Deposits:**` block format: (i) multi-line, one bullet per line, (ii) inline-comma-separated, (iii) other. Report counts. This determines whether the failure shape is general (would have tripped historical plans too) or specific to today's plan (proximate cause is unique to the 2026-05-12 plan's structure). **Q4 — Recommendation.** Given Q1–Q3, recommend one of: (i) governance fix — Planner must use multi-line Deposits format / must place Rule 20 banner outside fenced blocks / specific format constraint to document in PLANNER_TEMPLATE (state the exact rule), (ii) code fix in `_gate_rule_20_self_check` — describe the fix shape, do not author it, (iii) accept as Rule 22 override class — document the failure mode and rely on Planner verification (state the trigger conditions for the override), (iv) something else (explain). The recommendation goes to the Planner for routing. Include a "Layer Impact" section per your specialist output convention. Deposit findings to `/Users/marklehn/Desktop/GitHub/bellows/knowledge/architecture/rule-20-gate-false-positive-2026-05-12.md`. **Deposits:**
> - `/Users/marklehn/Desktop/GitHub/bellows/knowledge/architecture/rule-20-gate-false-positive-2026-05-12.md`
>
> Standard prompt feedback protocol → `bellows/knowledge/research/agent-prompt-feedback.md`. Commit with message: `docs: SA findings — rule_20_self_check gate false positive 2026-05-12`.
>
> **STOP. Do NOT proceed to any further step. Do NOT move the plan to Done. Wait for CEO confirmation before continuing.**

---
