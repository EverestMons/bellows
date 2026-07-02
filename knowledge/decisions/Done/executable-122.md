# Bellows — Tier-2 Batch: FORWARD rows 1, 3, 14 (three small independent fixes)
**Date:** 2026-07-02 | **Tier:** Small | **Dispatch Mode:** bellows | **Test Scope:** both | **Execution:** Step 1 (DEV) → Step 2 (QA) | **qa_steps:** 2 | **pause_for_verdict:** always

## CEO Context

CEO-approved 2026-07-02 sweep of the remaining small bellows FORWARD rows, batched per the tier-1 precedent (`Done/executable-bellows-tier-1-batch-2026-05-21.md`). **(A) Row 1** — `_extract_step_text` (gates.py:432) matches only uppercase `## STEP N`; mixed-case `## Step N` headers silently bypass step extraction. The archived collision concern (lowercase "step 1" in prose) is neutralized by the `^## ` header anchor — prose cannot match a line-anchored header pattern; DEV confirms via scope analysis. A sibling extractor `_extract_step_text_from_plan` exists at verdict.py:39 — sweep ALL `## STEP` header regexes for consistent case handling. **(B) Row 3** — the deposits parsers capture parenthetical qualifiers written inside backticks (`` `knowledge/foo.md (volunteered)` ``) into the path string, tripping `deposit_exists`. Fix per the archived recommendation: strip a trailing ` (...)` group from extracted paths at every extraction site in gates.py (the `**Deposits:**` block parser, the legacy prose patterns, and the agent-receipt extraction in `_extract_agent_declared_deposits`). **(C) Row 14** — cosmetic mojibake: `knowledge/qa/preserve-unlanded-commits-on-stranded-cleanup-2026-06-01.md` line 16, verification-table row 3's Status cell holds three U+FFFD replacement chars instead of ✅; one-cell edit, plan long closed. NOTE for CEO: gates.py/verdict.py changes need a daemon restart to load.

## How to Run This Plan

Paste the bootstrap prompt into Claude Code. The agent executes Step 1 ONLY, then STOPS for verdict before Step 2. The agent must never skip steps, auto-chain, or move the plan to Done without completing all steps including QA.

**Bootstrap prompt:**
```
Read the plan at bellows/knowledge/decisions/executable-bellows-tier-2-batch-2026-07-02.md. Execute Step 1 ONLY. After completing Step 1, STOP and wait for confirmation. Do NOT proceed to Step 2 or move the plan to Done.
```

---
---

## STEP 1 — DEV

---

> **FIRST — before any reads or work: post a short visible message to chat (1-2 sentences) confirming you are starting this plan and stating your immediate next action.** Do NOT rename the plan file.
>
> You are the Bellows Developer. Read your specialist file at `bellows/agents/BELLOWS_DEVELOPER.md` first. All commands run from `/Users/marklehn/Developer/GitHub/bellows`.
>
> **Scope:**
> - `gates.py`
> - `verdict.py`
> - `tests/test_gates.py`
> - `tests/`
> - `knowledge/qa/preserve-unlanded-commits-on-stranded-cleanup-2026-06-01.md`
> - `knowledge/development/bellows-tier-2-batch-2026-07-02.md`
>
> **Item A — mixed-case step headers.** In `_extract_step_text` (gates.py:432), make the `## STEP N` header pattern case-insensitive while KEEPING the line-start `## ` anchoring (that anchor is what makes prose collision impossible — document this in a one-line comment). Sweep for sibling step-header regexes: `_extract_step_text_from_plan` (verdict.py:39) and any other `## STEP` patterns in gates.py/verdict.py (grep `STEP` across both files); apply the same flag consistently so extraction and boundary detection agree. Scope analysis first: grep the existing test fixtures and 2-3 Done plans for line-anchored lowercase `## step`-shaped lines that would NEWLY match — record findings (expected: none) in the dev log before changing code.
>
> **Item B — parenthetical qualifier strip.** At every deposit-path extraction site in gates.py — the `**Deposits:**` bullet parser, the legacy prose patterns (around gates.py:489-527), and `_extract_agent_declared_deposits` — strip a trailing parenthetical from the captured path: `re.sub(r'\s*\([^)]*\)\s*$', '', path).strip()`. Factor the strip into one tiny helper applied at all sites rather than repeating the regex.
>
> **Item C — mojibake cell.** In `knowledge/qa/preserve-unlanded-commits-on-stranded-cleanup-2026-06-01.md` line 16, replace the three U+FFFD chars in the row-3 Status cell with ✅ (single exact-string edit; the surrounding row text is the anchor). No other change to that file.
>
> **Tests.** In `tests/test_gates.py` (or the conventions-matching test module): (i) `## Step 2` mixed-case header extracts step 2 correctly; (ii) lowercase `step 1` in step PROSE does not create a step boundary (anchor regression); (iii) `` `path.md (volunteered)` `` in a Deposits block extracts as `path.md`; (iv) a parenthetical INSIDE the filename-proper is untouched unless trailing (e.g. `` `notes(v2).md` `` stays intact); (v) agent-receipt path with trailing qualifier is stripped by `_extract_agent_declared_deposits`.
>
> **Self-verify.** Run the FULL suite with `python3 -m pytest tests/ -v --timeout=600` to an explicit pass/fail and READ THE TAIL (use `--timeout`, not the GNU `timeout` binary — absent on this Mac). Confirm the U+FFFD grep on the QA report returns 0 hits and the file diff touches exactly one line.
>
> **Commit** with a descriptive message. Deposit a dev log with: Item A scope-analysis findings, the strip-helper code and its call sites, the one-line QA-report diff, all test names, the full-suite tail verbatim, commit hash, and an Output Receipt with status. In `### Ledger Updates` include `#### Prompt Feedback`.
>
> **Deposits:**
> - `bellows/knowledge/development/bellows-tier-2-batch-2026-07-02.md`
>
> **STOP. Do NOT proceed to Step 2. Do NOT move the plan to Done. Wait for verdict before continuing.**

---
---

## STEP 2 — QA

---

> **Before starting, read the Step 1 dev-log deposit at `bellows/knowledge/development/bellows-tier-2-batch-2026-07-02.md` and check its Output Receipt status. If status is not Complete, halt and report the blocker before proceeding.**
>
> You are Bellows QA. Read your specialist file at `bellows/agents/BELLOWS_QA.md` first.
>
> **Scope:**
> - `knowledge/qa/bellows-tier-2-batch-qa-2026-07-02.md`
>
> **Rule 20 self-check is gate-enforced on this step.** Your QA report MUST include the byte-exact banner `Rule 20 — QA Self-Check Results` and a `PASSED — SELF-CHECK PASSED` line; the verification table below does NOT by itself satisfy the gate — end with a self-grep confirming the banner is present in your deposited report.
>
> Verification table, one row per claim: (1) mixed-case `## Step N` extraction works — run test (i) in isolation; (2) prose-anchor regression holds — test (ii); (3) BOTH step-header extractors (gates.py + verdict.py) carry consistent case handling — quote both patterns; (4) trailing-parenthetical strip works at Deposits-block, legacy-prose, and receipt sites — tests (iii)+(v), quote the shared helper and its call sites; (5) non-trailing parenthetical preserved — test (iv); (6) QA-report mojibake fixed — grep U+FFFD returns 0 in `knowledge/qa/preserve-unlanded-commits-on-stranded-cleanup-2026-06-01.md` and `git log -1` for that file shows a one-line change; (7) Item A scope-analysis findings documented in the dev log; (8) full suite green — re-run `python3 -m pytest tests/ -v --timeout=600` and show the tail. If any row fails, report it and halt — do not pass a broken deliverable.
>
> Deposit the QA report to `knowledge/qa/bellows-tier-2-batch-qa-2026-07-02.md` and commit it. In `### Ledger Updates` include: `#### Project Status` — one milestone paragraph: FORWARD rows 1/3/14 shipped as tier-2 batch (mixed-case step headers, parenthetical-qualifier strip, mojibake cell), daemon restart required; `#### Prompt Feedback` — standard.
>
> **Deposits:**
> - `bellows/knowledge/qa/bellows-tier-2-batch-qa-2026-07-02.md`
>
> On full completion, move the plan file to `bellows/knowledge/decisions/Done/` as the absolute last operation.
