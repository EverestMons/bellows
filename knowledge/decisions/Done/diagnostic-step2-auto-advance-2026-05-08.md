# bellows — Diagnostic: Step 2 Auto-Advance Despite "STOP after Step 1"
**Date:** 2026-05-08 | **Tier:** Small | **Test Scope:** N/A (diagnostic) | **Execution:** Step 1 (DEV)

## How to Run This Plan

Paste the bootstrap prompt into Claude Code. The agent reads the full plan file and executes Step 1 ONLY.

**Bootstrap prompt:**
```
Read the plan at bellows/knowledge/decisions/diagnostic-step2-auto-advance-2026-05-08.md. Execute Step 1 ONLY. After completing Step 1, STOP and wait for my confirmation. Do NOT move the plan to Done.
```

## CEO Context

**Twice in one session today (2026-05-08), Bellows ran Step 2 of a multi-step plan WITHOUT pausing for CEO verdict after Step 1, despite the prompt explicitly instructing the agent to stop.** The Planner-issued bootstrap prompt for both runs was:

```
Read the plan at <path>. Execute Step 1 ONLY. After completing Step 1, STOP and wait for my confirmation. Do NOT proceed to Step 2 or move the plan to Done.
```

The Planner's plan file Step 1 also ended with explicit STOP language:
> **STOP. Do NOT proceed to Step 2. Do NOT move the plan to Done. Wait for CEO confirmation before continuing.**

Despite both, Bellows progressed automatically from Step 1 to Step 2 in both cases. Plan slugs:
1. `executable-action-queue-limit-and-contract-name-2026-05-08` (invoice-pulse) — DEV passed gates, then QA ran without verdict pause and gate-failed
2. `executable-bellows-qa-prefix-and-skip-logging-2026-05-08` (bellows) — DEV passed gates, then QA ran without verdict pause and gate-failed

In both cases, the runner output included `gates ... step 1: passed=True, is_qa=False, failures=0` followed shortly by `▶ started ... step 2` (or equivalent runner activity for step 2). There was no `⏸️ PAUSED ... step 1 — waiting for CEO verdict` line between them.

This violates the step-by-step Planner verification model — the entire point of pausing between DEV and QA is for the Planner to read the dev log and confirm before QA begins.

**The CEO is testing whether `pause_for_verdict: after_step_1` in plan headers is the canonical mechanism for this gate.** This diagnostic must answer whether the bootstrap-prompt language alone should suffice, whether the plan must declare a header field, or both.

This is read-only. Do not modify any Bellows code. Do not run Bellows.

---
---

## STEP 1 — DEV

---

> **FIRST — claim this plan:** `import shutil; shutil.move("bellows/knowledge/decisions/diagnostic-step2-auto-advance-2026-05-08.md", "bellows/knowledge/decisions/in-progress-diagnostic-step2-auto-advance-2026-05-08.md")`. You are the Bellows Developer. Read your specialist file before reading source. This is a read-only diagnostic — do NOT modify code, do NOT run Bellows. Investigate why Bellows advanced past Step 1 without pausing, twice, in today's session. Deposit findings to `bellows/knowledge/development/diagnostic-step2-auto-advance-findings-2026-05-08.md`. **Q1 — Map the canonical step-pause decision logic.** Read `bellows.py`. Locate every code path that decides whether to pause-for-verdict between steps. Specifically find the `header_says_pause()` function around line 187 (referenced in earlier context — verify exact location). Report (a) every `pause_for_verdict` value the code recognizes (`always`, `after_step_1`, `after_qa_step`, others?), (b) the function's exact return semantics, (c) every call site of this function with file/line. **Q2 — Identify all step-completion code paths and the pause-decision they make.** When Step 1 finishes (gates pass, runner exits cleanly, deposit verified), what code decides "pause for verdict OR run step 2"? Walk the code path from `gates ... step 1: passed=True` log line to the next-step launch. List every conditional branch that influences the pause-vs-advance decision. The likely path involves `header_says_pause()`, but there may be additional gates: is-final-step check, is-QA-step check, deposit-required check, etc. For each conditional, document: file, line, condition, what each branch does. **Q3 — Test the actual headers from today's two failed plans.** Run grep against the two plan files (now in `Done/`): `grep -i "pause_for_verdict\|^---\|^# " /Users/marklehn/Desktop/GitHub/invoice-pulse/knowledge/decisions/Done/executable-action-queue-limit-and-contract-name-2026-05-08.md | head -20` and same for `/Users/marklehn/Desktop/GitHub/bellows/knowledge/decisions/Done/executable-bellows-qa-prefix-and-skip-logging-2026-05-08.md`. Report: did either plan declare a `pause_for_verdict` header field? If neither did, that is almost certainly the root cause — the bootstrap-prompt language ("STOP. Do NOT proceed to Step 2") is parsed by the agent but does NOT influence Bellows's orchestrator. Bellows decides advance-vs-pause solely from plan-header fields, not from prompt-body language the agent reads at runtime. **Q4 — Confirm or refute the hypothesis with a code citation.** Read the orchestrator's "decide what to do after step N" code and confirm: does it ever inspect the prompt body or the agent's claude -p stdout for STOP language? Or is the decision purely header-based? Cite the exact lines. If the decision is purely header-based, this is a fundamental design mismatch between Planner instructions and Bellows orchestration — the Planner has been writing STOP language thinking it's authoritative, when in fact only `pause_for_verdict: after_step_1` in the plan header has any effect. **Q5 — Audit prior plans for the same omission.** List every plan in `Done/` directories across watched projects that has `>= 2` steps. For each, run `grep -l "pause_for_verdict" <path>` and report which plans DO declare the header field versus which do not. Report counts: plans with header / plans without / total multi-step plans. This shows whether today's two plans are anomalies or whether the Planner has systematically been omitting this field. **Q6 — Fix shape.** Based on findings: (a) if the issue is "Planner omitted required header field" — recommend a PLANNER_TEMPLATE update (file, section to add) plus a Bellows-side defensive default (`pause_for_verdict: after_step_1` should be assumed when not declared, OR a startup-time warning when a multi-step plan is dispatched without an explicit pause directive). (b) if the issue is "Bellows ignored a header that WAS declared" — different root cause, point to the buggy code path. Estimate LOC for the recommended fix(es). State explicitly whether the Planner-side fix (template update) and the Bellows-side fix (defensive default or warning) are independent and can ship separately. Deposit findings using a single-call write (Filesystem:write_file). The findings file MUST end with an Output Receipt: Complete. Standard prompt feedback protocol → `bellows/knowledge/research/agent-prompt-feedback.md`. Commit with message: "docs: bellows step 2 auto-advance diagnostic findings".
>
> **STOP. Do NOT proceed. Do NOT move the plan to Done — that is the Planner's responsibility after Rule 22 verification.**
