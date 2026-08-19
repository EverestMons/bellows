# bellows — cycle_check CLOSURE_RE false-positive fix (over-matches prose "closed")
**Date:** 2026-08-19 | **Tier:** Small | **Dispatch Mode:** bellows | **cycle_tier:** T1 | **Test Scope:** full | **Execution:** Step 1 (DEV) → Step 2 (QA) | **Priority:** 1

**auto_close:** false
**pause_for_verdict:** after_qa_step

## Context

A corrective fix for a false-positive in the shipped `scripts/cycle_check.py` (executable-464), FOUND BY DOGFOODING cycle_check on the next plan's drafting cycle. The step-8 anti-fabrication guard's `CLOSURE_RE` (`cycle_check.py:37-40`) is compiled with `re.IGNORECASE`, so it matches the bare lowercase word **"closed"** (and **"bar met"**) in ordinary prose — not just the closure STATUS tokens it intends. A `## Drafting Cycle` block whose prose contains "closed" (e.g. a clone-diff note "real closed plans", or "a closed loop") gets a spurious `ESCALATE:claimed-close-unmet` mid-cycle.

**Measured evidence (this session):**
- `CLOSURE_RE.search('real closed plans')` → `True` (false positive)
- `CLOSURE_RE.search('cycle CLOSED')` → `True` (correct)
- The false ESCALATE fired live on the component-2b tooling draft, whose Tier-line reads "--emit-manifest against real closed plans".

**The intent:** closure is detected by a STATUS token, not a prose adjective. Real closures ALWAYS carry a `**Closing:**` line (the unambiguous canonical marker); the `CLOSED`/`CYCLE COMPLETE`/`bar met` alternatives are the status forms, conventionally UPPERCASE. Lowercase prose "closed"/"bar met" must NOT match. This tightens exactly the "convention-token-based, not inferred" discipline the cycle_check build (walk 5) established.

**No new behavior, no doctrine.** Scope is `scripts/cycle_check.py` + `tests/test_cycle_check.py` only.

## Drafting Cycle
**Tier:** T1 — triggers: T-8 (novel corrective). A one-regex fix + regression test to a shipped script; not a T-5/T-6 surface. **cycle_check is NOT dogfooded on this plan** — the bug under repair is closure-detection, and this plan's own DC block necessarily discusses "closed"/closure, so the tool would false-positive on itself until the fix lands; the Planner judges this cycle manually (the QA live canary re-runs the FIXED tool on this very draft as the proof).
**Walk 0 (context pin):** target `scripts/cycle_check.py:37-40` (`CLOSURE_RE`, IGNORECASE) + the step-8 consumer at `:414-415` (`claims_closure and verdict==CONTINUE → ESCALATE:claimed-close-unmet`). 27 existing tests must stay green (one may encode the loose behavior — flip it, 457 pattern). Clone-diff: executable-464 (the same script). Bellows suite baseline green.
**Direction verdict (after walk 1):** **PROCEED** — surgical one-regex fix + regression tests; angle sound, no forcing finding.
**Walks:** 2 (bar MET — walk 2 dry, no restructuring fold). Instruction yields 1 → 0. (cycle_check NOT dogfooded — see Tier note; Planner judged manually. The QA canary re-runs the FIXED tool as the proof.)
- Weak spots (1.4):     w1 dry. w2 dry (verified the fix needs TWO changes — drop IGNORECASE for "closed" AND drop/uppercase the bare `bar met` alternatives; both are in the DEV guidance).
- Destruction (2.4):    w1 1 folded — instruction 1 / record 0 (D1: THE GUARD MUST SURVIVE — add a regression test that a fabricated close (`**Closing:**`/`CLOSED` present + walk NOT dry) STILL fires `ESCALATE:claimed-close-unmet` after the fix; a false-positive repair that weakened the anti-fabrication guard (false negative) is worse than the bug). w2 dry.
- Vulnerabilities (3.1): w1 dry (under-matching claims_closure on a GENUINE close is harmless — BAR_MET is already returned for a dry walk before step 8; only a fabricated non-dry close matters, covered by D1). w2 dry.
- Integration-record:   w1 dry (fix is self-contained; step-8 logic at :414-415 unchanged; QA canary reads the root scratchpad draft by absolute path with a temp-block fallback). w2 dry.
- ACID (5.2):           w1 dry. w2 dry.
**Walk 1 STATUS:** 1 folded — instruction 1 / record 0 — NOT dry.
**Walk 2 STATUS:** 0 folded — full dry walk across all five lenses, no restructuring fold. §2 class bar MET.
**Conflicts:** none.
**§5 Conformance:** `plan_lint` at shape-stability (walk 2) → **0 FAIL**; STEP count = 2. Benign residual WARNs are the location-dependent bellows-in-tree class. Rule 20 banner pair inlined in Step 2 (check (c) byte-match).
**Closing:** full walk 2 dry across all five lenses, no restructuring fold; §5 conformance 0 FAIL; closing-record re-read run (this block), dry; cycle CLOSED. Deposit exactly once (pending CEO go).

---
---

## STEP 1 — BELLOWS DEVELOPER

---

> **Identity:** You are fixing a false-positive in `scripts/cycle_check.py`'s closure detection. Minimal, surgical: the regex + a regression test.
>
> **The bug.** `CLOSURE_RE` (`cycle_check.py:37-40`) is `re.IGNORECASE`, so `\bCLOSED\b` matches lowercase "closed" and `\bbar\s+met\b` matches lowercase "bar met" in ordinary prose. Step 8 (`:414-415`) then fires `ESCALATE:claimed-close-unmet` on a mid-cycle plan whose block merely mentions the word. Verified: `CLOSURE_RE.search('real closed plans')` is `True`.
>
> **The fix.** Make closure detection match STATUS tokens, not prose adjectives. Keep `**Closing:**` (case-sensitive, canonical). Make `CLOSED` and `CYCLE COMPLETE` match UPPERCASE only. The lowercase-prone `bar met` / `§2 bar met` alternatives: prefer to REMOVE them (real closures carry `**Closing:**`, so they are redundant) OR require the uppercase status form (`bar MET`) — your call, but a lowercase prose "bar met" must NOT match after the fix. Simplest correct approach: drop `re.IGNORECASE` from `CLOSURE_RE` and drop/uppercase the bare `bar met` alternatives; verify `**Closing:**` (literal) and the uppercase status tokens still match. Do NOT change step-8's logic (`:414-415`) — only what `claims_closure` detects.
>
> **Verify the fix does not under-match (real closures still detected).** Confirm against real closed plans: `knowledge/decisions/Done/executable-464.md` and `diagnostic-460.md` both carry `**Closing:**` + `cycle CLOSED`; `claims_closure` must stay `True` for them.
>
> **Regression test (`tests/test_cycle_check.py`).** Add: (1) a mid-cycle block (walk 1, not dry) whose prose contains "closed"/"bar met" but has NO `**Closing:**`/uppercase status → `claims_closure` False → verdict `CONTINUE`, exit 0 (NOT claimed-close-unmet); (2) a genuinely-closed block (`**Closing:**` + `cycle CLOSED`, walk dry) → still detected/`BAR_MET`; **(3) THE GUARD MUST SURVIVE — a FABRICATED close: `**Closing:**` / `cycle CLOSED` PRESENT but the current walk NOT dry (instruction folds) → must STILL fire `ESCALATE:claimed-close-unmet` (exit 1).** A false-positive fix that weakened the anti-fabrication guard would be worse than the bug — a false NEGATIVE lets a fabricated close through; this is the guard's whole purpose. **If an existing test encodes the loose lowercase behavior, FLIP it to the status-token form** ("this test asserted the bug" — 457 pattern) rather than preserving it. Preserve the other tests.
>
> **DEV discipline:** `python3 -m pytest tests/test_cycle_check.py -q 2>&1 | cat` — all pass. Commit `fix(bellows): cycle_check closure detection matches status tokens, not prose "closed" [<id>]`. Deposit a short dev log with the before/after `CLOSURE_RE.search` results on the false-positive input.
>
> **Deposits:**
> - `scripts/cycle_check.py`
> - `tests/test_cycle_check.py`
> - `knowledge/development/cycle-check-closure-fp-fix-2026-08-19.md`
>
> End with an Output Receipt recording Status AND the DEV commit sha (QA reads it). Standard prompt-feedback protocol.

---
---

## STEP 2 — BELLOWS QA ANALYST

---

> **Identity:** You are QA for the closure false-positive fix. Evidence is RAW output.
>
> **(1) Targeted suite passes.** `python3 -m pytest tests/test_cycle_check.py -v 2>&1 | cat` → evidence `knowledge/qa/evidence/executable-cycle-check-closure-fp-fix-2026-08-19/test_cycle_check.txt`. Confirm the two new regression cases are present and pass.
>
> **(2) LIVE CANARY — the fix on the exact plan that exposed the bug.** Capture raw stdout+exit to `.../live_canary.txt`:
> - `python3 scripts/cycle_check.py /Users/marklehn/Developer/GitHub/scratchpad/draft-executable-cycle-manifest-tooling-2026-08-19.md` → must now be `CONTINUE` (exit 0), NOT `ESCALATE:claimed-close-unmet`. (This scratchpad draft's block contains "real closed plans"; it is mid-cycle. If the file is absent at QA time, reproduce with a temp block containing a "closed" prose word + walk-1 non-dry data.)
> - `python3 scripts/cycle_check.py knowledge/decisions/Done/executable-464.md` → still `BAR_MET` (a genuine close still detected).
> - `python3 scripts/cycle_check.py knowledge/decisions/Done/diagnostic-460.md` → still `BAR_MET`.
> **Any real close now reading CONTINUE (under-match), or the false positive persisting, is a FAIL.**
>
> **(3) Full suite — Rule 21.** `python3 -m pytest tests/ -q -rf 2>&1 | cat` → `.../full_suite.txt`. FAILED node-id set must be empty.
>
> **(4) Scope.** `git diff --stat` shows only `scripts/cycle_check.py`, `tests/test_cycle_check.py`, `knowledge/`.
>
> **(5) Rule 20 self-check** — run the canonical block from `/Users/marklehn/Developer/GitHub/RULE_20_SELF_CHECK_BLOCK.md` with `plan_slug: executable-cycle-check-closure-fp-fix-2026-08-19`, the qa report path, the evidence dir, and `required_evidence_files: ["test_cycle_check.txt", "live_canary.txt", "full_suite.txt"]`. Prints `Rule 20 — QA Self-Check Results` and on success `PASSED — SELF-CHECK PASSED` (verbatim). If `FAILED — SELF-CHECK FAILED`, halt. `qa_test_result`: `full_suite.txt` + `test_cycle_check.txt` named in Deposits proactively.
>
> **Deposits:**
> - `knowledge/qa/2026-08-19-cycle-check-closure-fp-fix-qa.md`
> - `knowledge/qa/evidence/executable-cycle-check-closure-fp-fix-2026-08-19/`
> - `knowledge/qa/evidence/executable-cycle-check-closure-fp-fix-2026-08-19/test_cycle_check.txt`
> - `knowledge/qa/evidence/executable-cycle-check-closure-fp-fix-2026-08-19/live_canary.txt`
> - `knowledge/qa/evidence/executable-cycle-check-closure-fp-fix-2026-08-19/full_suite.txt`
>
> End with an Output Receipt (Status). Standard prompt-feedback protocol.
