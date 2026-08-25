# bellows — E5: session-id-keyed 3b + domain-sweep ritual — the keyed predicate, the caller plumbing, the wrap.md law

**Date:** 2026-08-25 | **Project:** bellows | **Tier:** Medium | **Dispatch Mode:** bellows | **cycle_tier:** T2 | **Test Scope:** full suite (bellows) | **Execution:** Step 1 (DEV) → Step 2 (QA) | **qa_steps:** 2 | **known_failures:** 0 | **Priority:** 1

**auto_close:** false
**pause_for_verdict:** always

**Depends on:** `knowledge/research/e5-wrap-keying-glossary-design-2026-08-25.md` — sha256 `6b476c676e2c750bb259aeb3908e360c65376bc03fdb0b3e19afc2e3b29fc90b` — **the DESIGN (diagnostic-519), consumed T-7: this plan BINDS its 8 in-scope gap rows; where a build-time correction and the design differ, the correction governs.** Audit §E5 + bypass (e); the LESSONS date-key entry. Precedent: the fourth build of the E-family shape (513, 516, 518); every prior build's full cold panel earned its cost, so this freeze convenes it.

## Why this exists

Bypass (e), measured live: same-day wraps inherit each other's `Lessons-swept:` lines — the most-skipped step's lock does not discriminate on multi-session days, which are now every day. The design settles the fix on E3's plumbing: the NEWEST sweep line must carry THIS session's id (stop-hook arm), with the debt hook's opposite polarity ruled as law, plus the domain-sweep ritual step and the `[sid:]` line format. Design bonus inherited: the current predicate MISSES blockquote-prefixed sweep lines entirely (SESSION 63's line, measured) — the new predicate fixes it in both arms.

## What this plan does NOT do

- **It does not scaffold glossary files.** D-3 ruled scaffold-on-first-use at wrap time; the wrap.md instruction carries the template. Glossary breadth is D-7's CEO fork, not this dispatch's.
- **It does not touch the baton.** The 21 historical date-only lines are data; the first keyed wrap writes the first `[sid:]` line and the check transitions (design arm 3: a historical-format newest line FAILS a keyed stop-hook check — the transition is one honest sweep away, this session's own wrap).
- **It does not edit ELUVIAN_PATH.md.** Gap row 9 stays routed to the follow-up doc plan (now carrying three lines: E3's two + E5's).
- **It does not change the [2r/receipts] group, the portability overrides, or any other wrap_check group** — the shared file's other tenants are byte-identical outside the 3b block and the two signature/argv sites.

## Numbers discipline

⚠️ **Measured 2026-08-25 against bellows main post-519; RE-DERIVE each — yours supersede and you say so.**

| id | pin | value | probe |
|---|---|---|---|
| X1 | design doc sha256 | `6b476c676e2c750bb259aeb3908e360c65376bc03fdb0b3e19afc2e3b29fc90b` | HALT on mismatch |
| X2 | target blob SHA-1s BEFORE | wrap_check.py `4ac15bfbea14…`, wrap_stop_hook.py `52589ac268fa…`, wrap_debt_hook.py `091bf588c7b1…`, hooks/commands/wrap.md `3b23291183f4…` | `git hash-object` in YOUR worktree; HALT on mismatch — wrap_check is triple-shared substrate |
| X3 | **`T`** — tests collected BEFORE | measure at A0 from the bellows cwd (was 1339 at 518's QA; 519 added none) | `python3 -m pytest tests/ --collect-only -q` FROM THE BELLOWS REPO ROOT (wrong cwd → false-error signal, measured) |
| X4 | failability proofs | `tests/test_wrap_3b_keyed.py` **absent**; `_find_newest_sweep_line` **absent** from wrap_check.py (`grep -cF` = 0) | positive control: `[2r/receipts]` present in wrap_check.py |
| X5 | the 3b block + signature + argv sites | wrap_check.py :136-151 (predicate), :90 (`check(session_id)`), :325-326 (argv parse); stop hook ~:207; debt hook ~:87 | anchored by shapes; relocate by context |
| X6 | the historical-line surface | 21 real sweep lines in the baton (22 grep matches minus 1 prose); 1 blockquote-prefixed (SESSION 63) | the design's G4 supersession — the new predicate must strip `>` before matching |
| X7 | wrap test floor | 20 + 28 + 26 + 11 = **85** | must pass unchanged; E5 only adds |

## Drafting Cycle
**Tier:** T2 computed — the wrap lock is live Tier-3 enforcement and the hook half of this change activates AT MERGE (the E3 precedent: the next wrap on this machine runs the new predicate — including THE WRAP THAT CLOSES THIS SESSION, whose newest sweep line is historical-format until that wrap writes its own keyed line). **Cold panel: MANDATED at the freeze (full form, four seats).**
**Walk register:** `governance/knowledge/research/walk-register-executable-eluvian-e5.md`
**Walks:** walk 0 pinned; walks 1–n OWED — five lenses each, sequential, v2.13 auto-advance, cycle_check branched after each walk. Rewritten at the close from the register's actual rows, never ahead of them.
**Direction verdict (after walk 1):** owed.
**Conformance (§5):** owed per lens; recorded at the close from actual runs.
**Closing:** owed. The deposit travels the lane with the receipt ritual → expected HOLD `class:shop-infra` → the CEO's `--release-class-hold` act → claim.

## Cycle Manifest
tier: T2
target: hooks/eluvian/wrap_check.py
class: shop-infra
reads: /Users/marklehn/Developer/GitHub/bellows/knowledge/research/e5-wrap-keying-glossary-design-2026-08-25.md, /Users/marklehn/Developer/GitHub/shop_next_session.md, /Users/marklehn/Developer/GitHub/governance/knowledge/research/eluvian-path-rulings-2026-08-24.md
writes: hooks/eluvian/wrap_check.py, hooks/eluvian/wrap_stop_hook.py, hooks/eluvian/wrap_debt_hook.py, hooks/commands/wrap.md, tests/test_wrap_3b_keyed.py, knowledge/research/e5-qa-2026-08-25.md, knowledge/research/pytest_full.txt
open_forks: (1) D-7's glossary-breadth CEO fork (active-only recommended) — the wrap.md instruction ships with the recommendation and the fork stays open; (2) D-7's degrade-arm posture (date-fallback recommended and built; hard-fail is the alternative ruling); (3) gap row 9 (ELUVIAN_PATH.md lines) rides the follow-up doc plan
walks: 0
yields: none
validation: pending
coherence: N/A

## MUST-PRESERVE

- ⚠️⚠️ **ACTIVATION AT MERGE, and the FIRST subject is THIS SESSION'S OWN WRAP.** The stop-hook keyed arm will find a historical-format newest line and FAIL 3b until this session performs its own sweep and writes the first `[sid:]` line — that is the check WORKING, not a trap; the failure message must therefore be the actionable one from design arm 2/3, and the QA report states this first-wrap behavior explicitly so the wrap operator is not surprised.
- ⚠️⚠️ **The debt hook's arm is DATE-FALLBACK by design (arm 5)** — a current-sid-keyed debt check would fail every fresh session start; the asymmetry (stop keyed, debt date) is the intended law and is tested as such.
- ⚠️ **The blockquote-prefix fix applies to BOTH arms** — strip a leading `>` (and surrounding whitespace) before the `lessons-swept:` match; SESSION 63's line is the regression fixture.
- ⚠️ **FAIL-OPEN discipline unchanged:** the new helpers handle their own errors; an unparseable baton degrades to the old date arm with a printed note, never an unhandled raise (main()'s catch would silently allow the whole wrap).
- ⚠️ **The shared file's other tenants are untouched:** the `[2r/receipts]` group, the env-override constants, every other group's message literals — byte-identical, proven by targeted diff in QA.
- ⚠️ **Historical lines are DATA:** no baton writes, no retro-keying.
- ⚠️ **EVERY DATE IS A FIXED LITERAL.** **`grep` is ugrep: `-F`; `--` before dash-leading literals.**
- ⚠️ **DEV targeted tests only; the full suite belongs to QA (bellows cwd).**

## STEP 1 — DEV: the keyed predicate, the caller plumbing, the ritual law

**Role:** DEV. `<id>` from your plan filename.

**A0 — preconditions.** Assert X1–X7 (X1/X2 HALT; X5 relocates by context; X3 measured and reported). Three-way start: pins as stated → proceed; substrate already present (`_find_newest_sweep_line` + `caller` param + test file) → ALREADY APPLIED no-op success; else partial → STOP with inventory.

**A1 — implement the design's gap rows 1–7, the design governing:**
- **Rows 1–3** — `hooks/eluvian/wrap_check.py`: `_find_newest_sweep_line(baton_text)` (first match top-to-bottom — the baton PREPENDS, measured; strip leading `>` + whitespace before the `lessons-swept:` startswith) and `_extract_sid(line)` (the design's `\[sid:\s*([A-Za-z0-9-]+)\]` form); `check(session_id=None, caller="stop")`; `main()` parses argv[2] as caller (default "stop"); the 3b block replaced with the SIX ARMS as designed — keyed pass / keyed fail (foreign sid, the actionable message) / historical-format fail (same message) / no-sid date-fallback / caller="debt" date-fallback / the unparseable-baton degrade with printed note. Every other group byte-identical.
- **Rows 4–5** — the two hooks append their caller literal as argv[2] (`"stop"` / `"debt"`); the debt hook's existing sid normalization is untouched.
- **Rows 6–7** — `hooks/commands/wrap.md`: 3b's mandated line format gains `[sid: <session-id>]` with the where-to-find-your-id pointer (the receipts README precedent); the new domain-sweep step (3d) with the design's question, the scaffold-on-first-use instruction, and the glossary template (DEFINITION / RUNBOOK / TRAP→CODE discriminator) inline or referenced; the mini-machine arms (3c fallback, cacheinfo gitlink) survive verbatim.
- **Row 8** — `tests/test_wrap_3b_keyed.py`: the design's 13 arms — keyed pass; foreign-sid fail; historical-format fail; no-sid date-fallback (hit and miss); debt-caller date-fallback (hit and miss); blockquote-prefixed line FOUND (the SESSION 63 regression fixture, verbatim); prose-line non-match (the G4 false-count fixture); prepend-ordering (newest wins over an older same-day keyed line); unparseable-baton degrade; empty baton; missing baton file. All tmp-path batons; no real baton reads.

**A2 — verify before committing:** new tests green (paste raw); the X7 floor green targeted (`python3 -m pytest tests/test_wrap_hooks.py tests/test_wrap_sentinel.py tests/test_wrap_receipts.py tests/test_deposit_receipt.py -q`); `py_compile` the three hook files; the X4 absences now present (grep both, `--` for dash literals).

**A3 — commit** (worktree): `git add hooks/eluvian/wrap_check.py hooks/eluvian/wrap_stop_hook.py hooks/eluvian/wrap_debt_hook.py hooks/commands/wrap.md tests/test_wrap_3b_keyed.py && git commit -m "[<id>] E5: session-id-keyed 3b (six arms, blockquote fix) + caller plumbing + domain-sweep ritual (ACTIVE AT MERGE for the next wrap)"`

⚠️ **IF ANY A2 CHECK FAILS: no commit, no revert, no retry — leave the worktree as evidence, report, raise `### Flags for CEO`.**

**Deposits:**
- `/Users/marklehn/Developer/GitHub/bellows/hooks/eluvian/wrap_check.py`
- `/Users/marklehn/Developer/GitHub/bellows/hooks/eluvian/wrap_stop_hook.py`
- `/Users/marklehn/Developer/GitHub/bellows/hooks/eluvian/wrap_debt_hook.py`
- `/Users/marklehn/Developer/GitHub/bellows/hooks/commands/wrap.md`
- `/Users/marklehn/Developer/GitHub/bellows/tests/test_wrap_3b_keyed.py`

**Scope:**
- `/Users/marklehn/Developer/GitHub/bellows/hooks/eluvian/wrap_check.py`
- `/Users/marklehn/Developer/GitHub/bellows/hooks/eluvian/wrap_stop_hook.py`
- `/Users/marklehn/Developer/GitHub/bellows/hooks/eluvian/wrap_debt_hook.py`
- `/Users/marklehn/Developer/GitHub/bellows/hooks/commands/wrap.md`
- `/Users/marklehn/Developer/GitHub/bellows/tests/test_wrap_3b_keyed.py`

## STEP 2 — QA

**Role:** QA. ⚠️ Fresh agent: re-measure; the DEV report is not evidence.

**Q1 — full suite.** `python3 -m pytest tests/ -q` **from the bellows repo root as cwd**; deposit RAW output as `pytest_full.txt`; **self-contained accounting (the DEV report is not evidence): report the total, the new file's own count (`pytest tests/test_wrap_3b_keyed.py --collect-only -q`), and their difference as the inherited baseline**; zero failures.
**Q2 — change-set vs the gap table:** rows 1–8 present at their sites; row 9 verifiably ABSENT (no file outside the five declared; no ELUVIAN_PATH.md edit); the shared file's other tenants byte-identical — targeted diff shows the 3b block, the signature, the argv parse, AND the two new helper definitions as the ONLY wrap_check hunks (the helpers are additional hunks by construction — a diff-is-empty-elsewhere assertion that forgets them is unsatisfiable); the six existing group literals plus `[2r/receipts]` all survive; the wrap.md mini-machine arms survive verbatim.
**Q3 — behavioral spot-probes on tmp batons:** the six arms driven through `check()` directly (tmp baton files, both callers, sid present/absent); the SESSION 63 blockquote fixture found by the new predicate AND missed by the old one (the regression demonstrated both directions); the prepend-ordering probe.
**Q4 — activation, stated honestly:** hook half LIVE AT MERGE — the next `/wrap` on this machine runs the keyed arm and WILL FAIL 3b until the wrap writes its first `[sid:]` line (the arm-2/3 actionable message is the operator's instruction); reproduce the first-wrap walkthrough (sweep → line with `[sid:]` → re-check passes) as the QA report's operator sheet; state the daemon is NOT involved (pure hook-side change; no restart needed).

> **QA SELF-CHECK — Rule 20.** Post the block from `/Users/marklehn/Developer/GitHub/RULE_20_SELF_CHECK_BLOCK.md` verbatim, under the banner **`Rule 20 — QA Self-Check Results`**, and close with **`PASSED — SELF-CHECK PASSED`** only if every check genuinely passed. ⚠️ Both literals are matched by `plan_lint` check (c) and neither may be paraphrased. Rule 20 block + Q1–Q4 results in the `.md`; raw suite output in `pytest_full.txt` — the two QA gates scan DIFFERENT extensions.

**Deposits:**
- `/Users/marklehn/Developer/GitHub/bellows/knowledge/research/e5-qa-2026-08-25.md`
- `/Users/marklehn/Developer/GitHub/bellows/knowledge/research/pytest_full.txt`

**Scope:**
- `/Users/marklehn/Developer/GitHub/bellows/knowledge/research/e5-qa-2026-08-25.md`
- `/Users/marklehn/Developer/GitHub/bellows/knowledge/research/pytest_full.txt`

**Commit:** `git add knowledge/research/e5-qa-2026-08-25.md knowledge/research/pytest_full.txt && git commit -m "[<id>] qa: E5 keyed 3b — full suite + evidence"`

## Deposit ritual

The E3 contract: receipt against the DRAFT bytes first, then stage as `ready-executable-eluvian-e5-keying.md`. **Expected: HOLD `class:shop-infra`; release = the CEO's `--release-class-hold` act.** The depositing session arms a slug-keyed watcher before the receipt.
