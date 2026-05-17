# Executable: Gate 2c Plan B — Post-Restart Bait Canary (Strikes 4 & 5)

**Plan slug:** executable-gate-2c-canary-strikes-4-5-2026-05-19
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

Gate 2c Step 1 fix (commit 30e395c) landed `_filter_transient_paths` and tolerant rule_20 banner matching. Unit tests prove the fix works on synthetic inputs. This canary plan proves the fix is LOADED in the restarted Bellows daemon by deliberately baiting both gates with patterns that previously caused strikes 4 and 5.

**Bait design:**

- **Step 1 (non-QA):** Deposits block mentions a literal `_staging_*` filename in addition to the real deliverable. Pre-fix `deposit_exists` gate would extract the staging path and report it missing; post-fix gate filters `_staging_*` and only validates the real deliverable.

- **Step 2 (QA):** QA report's Rule 20 self-check banner is rendered inside a fenced code block with `===` separator lines bracketing it. Pre-fix `rule_20_self_check` gate would find the banner but fail to find the PASSED line due to the line-by-line scan being confused by `===` lines (or by the PASSED line having unexpected leading whitespace inside the fence); post-fix gate uses `re.search` with `re.MULTILINE` and matches the PASSED line regardless of decoration.

**Pass criterion (binary):**

- Step 1 verdict request: `Pause Reason Code: header_pause`, `Gate Result Passed: True`. ANY failure listing `deposit_exists` means the strike-4 fix is not loaded.
- Step 2 verdict request: `Pause Reason Code: qa_checkpoint`, `Gate Result Passed: True`. ANY failure listing `rule_20_self_check` means the strike-5 fix is not loaded.

The canary's work is intentionally trivial — write two short markdown files. The purpose is to BE bait, not to do work.

---

## STEP 1 — Bait deposit_exists with _staging_ mention

You are the Bellows Developer. Read `bellows/CLAUDE.md`. Operate against `/Users/marklehn/Developer/GitHub/bellows/`.

**Task:** Write a short canary deliverable file. Do nothing else.

Create `bellows/knowledge/research/canary-strike-4-bait-2026-05-19.md` with the following content:

```markdown
# Canary — Strike 4 Bait

This is Plan B Step 1's deliverable. The Deposits block below intentionally
mentions a `_staging_*` filename to verify that the deposit_exists gate
filters it out post-fix.

Pre-fix, the gate would extract `_staging_canary-strike-4-bait-2026-05-19.md`
from the plan text and report it missing. Post-fix, the gate filters
`_staging_*` basenames before checking on disk, so only the real
deliverable (this file) is validated.

If this plan reaches verdict-pending with Gate Result Passed: True, the
strike-4 fix is loaded.
```

No other operations. No git commits. No source modifications.

**Output Receipt:**
- Agent: Bellows Developer
- Step: 1
- Status: Complete (file written, no errors)
- What Was Done: wrote canary deliverable
- Files Deposited: `bellows/knowledge/research/canary-strike-4-bait-2026-05-19.md`
- Files Created or Modified: 1 file (no commit)
- Decisions Made: none
- Flags for CEO: none expected
- Flags for Next Step: gate failures on deposit_exists indicate strike-4 fix not loaded

**Deposits:**
- `bellows/knowledge/research/canary-strike-4-bait-2026-05-19.md`
- `_staging_canary-strike-4-bait-2026-05-19.md`

**STOP.** Do NOT proceed to Step 2.

---

## STEP 2 — QA: Bait rule_20_self_check with decorated banner

You are the Bellows Developer (acting as QA). Read the prior step's deposit at `bellows/knowledge/research/canary-strike-4-bait-2026-05-19.md` and verify it exists.

**Task:** Write a QA report whose Rule 20 self-check banner is intentionally decorated with `===` separator lines (the strike-5 pattern). The post-fix gate should accept this; the pre-fix gate would not.

Write `bellows/knowledge/qa/gate-2c-canary-qa-2026-05-19.md`:

```markdown
# QA Report — Gate 2c Canary (Strikes 4 & 5 Bait Verification)

**Date:** 2026-05-19
**Plan:** executable-gate-2c-canary-strikes-4-5-2026-05-19

## Check 1 — Step 1 deliverable exists

Verified bellows/knowledge/research/canary-strike-4-bait-2026-05-19.md exists.

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

Note the THREE `===` decoration lines: one above the banner title, one between the banner title and the PASSED line, and one below. This is the exact pattern from LESSONS 2026-05-18 strike-5.

To produce the QA report, use `Filesystem:write_file` or equivalent — render the file literally as shown above. Do NOT execute a Python script that prints the banner; just write the markdown directly.

No other operations. No git commits.

**Output Receipt:**
- Agent: Bellows Developer (QA)
- Step: 2
- Status: Complete (file written, no errors)
- What Was Done: wrote decorated-banner QA report
- Files Deposited: `bellows/knowledge/qa/gate-2c-canary-qa-2026-05-19.md`
- Files Created or Modified: 1 file (no commit)
- Decisions Made: none
- Flags for CEO: gate failures on rule_20_self_check indicate strike-5 fix not loaded
- Flags for Next Step: Planner reads verdict request; if both steps show Gate Result Passed: True with no deposit_exists or rule_20_self_check failures, both fixes are verified loaded

**Deposits:**
- `bellows/knowledge/qa/gate-2c-canary-qa-2026-05-19.md`

Standard prompt feedback protocol → `bellows/knowledge/research/agent-prompt-feedback.md`.

---

## How to run

Bellows detects on rescan, dispatches Step 1, pauses at `header_pause`. Planner inspects the verdict request: if it shows `Gate Result Passed: True` with NO `deposit_exists` failure listed (despite the `_staging_*` mention in Deposits), strike-4 fix is verified loaded. Continue verdict deposited. Step 2 runs, pauses at `qa_checkpoint`. Planner inspects: if it shows `Gate Result Passed: True` with NO `rule_20_self_check` failure listed (despite the `===` decoration), strike-5 fix is verified loaded. Continue verdict deposited. Plan moves to Done.

If EITHER step trips its targeted gate, the fix isn't loaded — investigate before proceeding to Gate 2b.
