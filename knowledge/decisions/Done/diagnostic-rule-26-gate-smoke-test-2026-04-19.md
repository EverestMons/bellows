# bellows — Rule 26 Gate Smoke Test
**Date:** 2026-04-19 | **Tier:** diagnostic | **Execution:** Step 1 (Investigation Agent)

## Purpose

Smoke test the Rule 26 `**Deposits:**` block-preference logic in the live Bellows gate. This plan's Step 1 contains BOTH a declared `**Deposits:**` block AND a prose path (`bellows/knowledge/research/not-a-real-deposit.md`) that would have been flagged by the pre-fix gate. Expected result: gate passes with `Gate Result Passed: True`, verdict file shows the declared deposit only.

If the gate trips on the prose path, the new gates.py code is not loaded (Bellows restart issue).

## How to Run This Plan

**Bootstrap:**
```
Read the plan at bellows/knowledge/decisions/diagnostic-rule-26-gate-smoke-test-2026-04-19.md. Execute Step 1 ONLY. After completing Step 1, STOP.
```

---
---

## STEP 1 — Investigation Agent

---

> Skip specialist file and glossary reads — this is a one-shot gate smoke test. Write a one-paragraph note confirming you read this prompt. The note should say: "Rule 26 gate smoke test executed. The purpose of this plan is to verify the Bellows daemon is running the updated `_extract_plan_required_deposits` code from the 2026-04-19 Rule 26 fix. This step's prompt mentions `bellows/knowledge/research/not-a-real-deposit.md` — a prose-style path embedded in instruction text. If the gate is using new code, it will ignore this prose path and only validate the declared `**Deposits:**` block below. If the gate is using old code, it will flag the prose path as a missing deposit and the verdict will show Gate Result Passed: False."
>
> Deposit the note using the canonical Python file write pattern with `open("bellows/knowledge/research/rule-26-gate-smoke-2026-04-19.md", "w") as f: f.write(content)` where `content` is a triple-quoted string.
>
> **Deposits:**
> - `bellows/knowledge/research/rule-26-gate-smoke-2026-04-19.md`
>
> Standard prompt feedback protocol → `bellows/knowledge/research/agent-prompt-feedback.md`.
>
> **STOP.**
