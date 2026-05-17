# Executable: Gate 2c Plan B (rerun) — Post-Restart Bait Canary

**Plan slug:** executable-gate-2c-canary-rerun-2026-05-19
**Plan type:** executable
**Project:** bellows
**Specialist:** Bellows Developer
**Auto-close:** false
**Pause for verdict:** after_step_1
**Priority:** 1
**Depends on:** none
**Created:** 2026-05-19

---

## Context

First Plan B canary (`executable-gate-2c-canary-strikes-4-5-2026-05-19`) was processed by a stale pre-fix daemon (PID 16753, started 2026-05-15) that was still running alongside the post-restart daemon (PID 20785). PID 16753 has been killed. This rerun deposits the same bait against the surviving post-fix daemon.

**Pass criterion (binary):**

- Step 1 verdict request: `Gate Result Passed: True`, no `deposit_exists` failure listed.
- Step 2 verdict request: `Gate Result Passed: True`, no `rule_20_self_check` failure listed.

Any failure on the targeted gate means the fix isn't loaded in the surviving daemon either, which would indicate the restart was incomplete and the post-fix daemon also has stale code somehow.

---

## STEP 1 — Bait deposit_exists with _staging_ mention

You are the Bellows Developer. Read `bellows/CLAUDE.md`. Operate against `/Users/marklehn/Developer/GitHub/bellows/`.

**Task:** Write a short canary deliverable file. Do nothing else.

Create `bellows/knowledge/research/canary-rerun-strike-4-bait-2026-05-19.md` with the following content:

```markdown
# Canary Rerun — Strike 4 Bait

This is Plan B (rerun) Step 1's deliverable. The Deposits block below intentionally
mentions a `_staging_*` filename to verify that the deposit_exists gate filters it
out post-fix.

If this plan reaches verdict-pending with Gate Result Passed: True, the strike-4
fix is verified loaded in the surviving daemon (PID 20785).
```

No other operations. No git commits. No source modifications.

**Output Receipt:**
- Agent: Bellows Developer
- Step: 1
- Status: Complete
- What Was Done: wrote canary deliverable
- Files Deposited: `bellows/knowledge/research/canary-rerun-strike-4-bait-2026-05-19.md`
- Files Created or Modified: 1 file (no commit)
- Decisions Made: none
- Flags for CEO: none expected
- Flags for Next Step: gate failures on deposit_exists indicate strike-4 fix not loaded in surviving daemon

**Deposits:**
- `bellows/knowledge/research/canary-rerun-strike-4-bait-2026-05-19.md`
- `_staging_canary-rerun-strike-4-bait-2026-05-19.md`

**STOP.** Do NOT proceed to Step 2.

---

## STEP 2 — QA: Bait rule_20_self_check with decorated banner

You are the Bellows Developer (acting as QA). Read the prior step's deposit at `bellows/knowledge/research/canary-rerun-strike-4-bait-2026-05-19.md` and verify it exists.

**Task:** Write a QA report whose Rule 20 self-check banner is intentionally decorated with `===` separator lines.

Write `bellows/knowledge/qa/gate-2c-canary-rerun-qa-2026-05-19.md`:

```markdown
# QA Report — Gate 2c Canary Rerun (Strikes 4 & 5 Bait Verification)

**Date:** 2026-05-19
**Plan:** executable-gate-2c-canary-rerun-2026-05-19

## Check 1 — Step 1 deliverable exists

Verified bellows/knowledge/research/canary-rerun-strike-4-bait-2026-05-19.md exists.

**Result: PASS**

## Rule 20 Self-Check

```
============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
============================================================
```
```

Note the three `===` decoration lines bracketing the banner — this is the exact strike-5 pattern.

Use `Filesystem:write_file` or equivalent to write the file literally as shown. Do NOT execute a Python script that prints the banner; write the markdown directly.

No other operations. No git commits.

**Output Receipt:**
- Agent: Bellows Developer (QA)
- Step: 2
- Status: Complete
- What Was Done: wrote decorated-banner QA report
- Files Deposited: `bellows/knowledge/qa/gate-2c-canary-rerun-qa-2026-05-19.md`
- Files Created or Modified: 1 file (no commit)
- Decisions Made: none
- Flags for CEO: gate failures on rule_20_self_check indicate strike-5 fix not loaded
- Flags for Next Step: Planner reads verdict request; both fixes verified loaded if no targeted-gate failures

**Deposits:**
- `bellows/knowledge/qa/gate-2c-canary-rerun-qa-2026-05-19.md`

Standard prompt feedback protocol → `bellows/knowledge/research/agent-prompt-feedback.md`.

---

## How to run

Bellows detects on rescan, dispatches Step 1 against the surviving post-fix daemon (PID 20785), pauses at `header_pause`. Planner inspects verdict request: if `Gate Result Passed: True` with NO `deposit_exists` failure, strike-4 fix is verified loaded. Continue verdict. Step 2 runs, pauses at `qa_checkpoint`. Planner inspects: if `Gate Result Passed: True` with NO `rule_20_self_check` failure, strike-5 fix is verified loaded. Continue verdict. Plan moves to Done.
