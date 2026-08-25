# bellows — E5 design: session-id-keyed wrap affirmations + per-project glossary — the 3b fix, the line format, the glossary bootstrap, the ritual step

**Date:** 2026-08-25 | **Project:** bellows | **Tier:** Small | **Dispatch Mode:** bellows | **cycle_tier:** T1 | **Test Scope:** none (read-only design; writes one research doc) | **Execution:** Step 1 (DIAGNOSTIC) | **Priority:** 1

**auto_close:** false
**pause_for_verdict:** after_step_1

**Depends on:** `/Users/marklehn/Developer/GitHub/governance/knowledge/research/eluvian-path-audit-2026-08-24.md` §E5 + bypass (e), `/Users/marklehn/Developer/GitHub/governance/knowledge/research/eluvian-path-rulings-2026-08-24.md` (R2 per-project glossary), both T-7. **The measured defect this closes:** the 3b gate keys on `date.today()` and was discharged by ANOTHER session's same-day line — measured live in SESSION 61 and inherited by every same-day wrap since (at least seven same-day sweep lines rode the hole on 2026-08-24 alone). The LESSONS.md date-key entry fixes the shape: *the newest `Lessons-swept:` line must be one THIS session wrote.* Precedent: 515→516, 517→518 — the fourth run of the design→build shape.

## Why this exists

Bypass (e): a same-day second wrap inherits the prior session's `Lessons-swept:` line — the step the lock exists to make un-skippable is not enforced on exactly the days with multiple sessions, which are exactly the days the shop now has. E3 built the session-id plumbing (`check(session_id)`, both hooks passing validated ids); E5 consumes it for the 3b gate and ships R2's glossary layer. This diagnostic settles both against the live code.

## What this plan does NOT do

- **It writes NO code.** One research deposit with a Rule 27 gap table.
- **It does not re-key history.** The baton's 22 existing date-only `Lessons-swept:` lines stay untouched; only the NEWEST line's form is judged, and only when a session id is available.
- **It does not build a glossary-content gate.** Whether a domain sweep can be mechanically VERIFIED (vs ritually mandated) is a design question (D-4) with an honest boundary, not an assumption.

## Numbers discipline

⚠️ **Measured 2026-08-25 against bellows main post-518 + the activation restart; RE-DERIVE each — yours supersede and you say so.**

| id | pin | value | probe |
|---|---|---|---|
| G1 | the 3b check today | wrap_check.py:142 | `line.strip().lower().startswith("lessons-swept:") and today in line` over the WHOLE baton — ANY line, ANY session, same date discharges it; `today = date.today().isoformat()` |
| G2 | the E3 interface E5 consumes | wrap_check.py:90 | `def check(session_id: str | None = None)` — both hooks already pass validated ids (stop :208-era, debt normalized); the 3b fix needs ZERO new plumbing |
| G3 | glossaries today | **0** across all projects | `ls */knowledge/glossary.md` at the root → no matches (506 fork 7 still true); positive control: `ls */knowledge/decisions` matches 10+ |
| G4 | the baton's historical lines | **22** `Lessons-swept:` lines, all date-keyed, append-only | backward compat: the new form must coexist; the check must not mis-fire on OLD lines when judging the NEWEST |
| G5 | the ritual doc | bellows/hooks/commands/wrap.md — steps 1, 2, 3b, 3, 3c, 4 (blob `3b23291183f4…`) | E5 edits 3b's mandated line format and adds the domain-sweep step; the file also carries the mini-machine arms (3c fallback, gitlink cacheinfo) that must survive |
| G6 | wrap_check blob | `4ac15bfbea14…` | SHARED SUBSTRATE (E3 [2r] group + portability env-overrides live in it); X-pin HALT discipline for the executable |
| G7 | wrap test surface | test_wrap_hooks 20 + test_wrap_sentinel 28 + the E3 receipts tests | the executable's regression floor; count the receipts tests at execution |
| G8 | multi-machine reality | the mini wraps against ITS clone of the same baton (ROOT env-derived post-75cc1b4); session ids are machine-local Claude session UUIDs | the keyed check must behave when the NEWEST line was written by the OTHER machine's session (fetch-lag included — the mini's measured wrap-verdict-freshness lesson) |

## Drafting Cycle
**Tier:** T1 computed — T-7 fires twice over. Read-only.
**Walk register:** `governance/knowledge/research/walk-register-diagnostic-eluvian-e5-design.md`
**Walks:** walk 0 pinned; walks 1–n OWED — five lenses each, sequential, v2.13 auto-advance, cycle_check branched after each walk. Rewritten at the close from the register's actual rows, never ahead of them.
**Direction verdict (after walk 1):** owed.
**Cold panel:** owed — decided at the freeze with reasoning (the E-family rule puts the panel on the EXECUTABLE: 46/33/31-finding yields on the three builds).
**Conformance (§5):** owed per lens; recorded at the close from actual runs.
**Closing:** owed. The deposit travels the lane with the receipt ritual → auto-clear (read-only) → claim. ⚠️ **This plan's CLOSE is the E3 retirement canary:** its receipt should move to `receipts/archived/` when the daemon closes it — the first close under the restarted daemon — and the depositing session records the observation either way.

## Cycle Manifest
tier: T1
target: knowledge/research/e5-wrap-keying-glossary-design-2026-08-25.md
class: read-only
reads: /Users/marklehn/Developer/GitHub/bellows/hooks/eluvian/wrap_check.py, /Users/marklehn/Developer/GitHub/bellows/hooks/eluvian/wrap_stop_hook.py, /Users/marklehn/Developer/GitHub/bellows/hooks/eluvian/wrap_debt_hook.py, /Users/marklehn/Developer/GitHub/bellows/hooks/commands/wrap.md, /Users/marklehn/Developer/GitHub/shop_next_session.md, /Users/marklehn/Developer/GitHub/bellows/tests/test_wrap_hooks.py, /Users/marklehn/Developer/GitHub/bellows/tests/test_wrap_sentinel.py, /Users/marklehn/Developer/GitHub/ELUVIAN_PATH.md, /Users/marklehn/Developer/GitHub/governance/knowledge/research/eluvian-path-audit-2026-08-24.md, /Users/marklehn/Developer/GitHub/governance/knowledge/research/eluvian-path-rulings-2026-08-24.md
writes: knowledge/research/e5-wrap-keying-glossary-design-2026-08-25.md
open_forks: none authored here — R2 and the audit govern; anything needing a NEW ruling (e.g. glossary bootstrap breadth) lands in D-7
walks: 0
yields: none
validation: pending
coherence: N/A

## MUST-PRESERVE

- ⚠️ **READ-ONLY.** The single deposit is the write set.
- ⚠️ **Every design decision cites file:line in CURRENT code**; absence claims carry positive controls.
- ⚠️ **The keyed check must not create a NEW trap class:** a wrap that genuinely swept but wrote its line milliseconds before another session appended must not hard-block forever — the design states the newest-line rule's exact tie-breaking and its escape (the affirmation-discriminates lesson, applied without inventing a lock that traps the compliant).
- ⚠️ **The 22 historical lines are DATA, not violations** — no retro-keying, no rewriting the baton.
- ⚠️ **EVERY DATE IS A FIXED LITERAL.** **`grep` is ugrep: `-F` for literals.**
- ⚠️ **Worktree dispatch; deposit path project-relative.**

## STEP 1 — DIAGNOSTIC: settle the design, emit the document

**Role:** DIAGNOSTIC.

Produce `/Users/marklehn/Developer/GitHub/bellows/knowledge/research/e5-wrap-keying-glossary-design-2026-08-25.md` (project-relative in your worktree) settling AT LEAST the following, each grounded in file:line, with a Rule 27 gap table:

**D-1 — the keyed 3b rule.** The exact predicate replacing G1, built on the LESSONS fix-shape (*the NEWEST `Lessons-swept:` line must be one THIS session wrote*): how "newest" is determined in an append-only baton whose blocks are PREPENDED at the top while sweep lines live inside blocks (measure the real ordering — is last-in-file oldest or newest? The baton's structure decides, not an assumption); how the line carries the id (D-2's format); the arms — session id present + newest line carries it → PASS; session id present + newest line is another session's → FAIL with the actionable message; **no session id (manual run, debt hook's new-session case) → the degrade arm, chosen with reasons** (date-fallback preserves the old hole exactly when unattended — name what each choice costs); G8's cross-machine case (the newest line legitimately belongs to the other machine's finished wrap — the rule must not demand the impossible).
**D-2 — the line format.** How the session id rides the line: a trailing `[sid: <full-or-prefix>]` token vs embedding in the prose. Full UUID vs a prefix (the receipts precedent uses the full id in filenames; the baton line is human-read — weigh legibility); the parse must be `-F`-greppable and collision-safe against the 22 historical lines (which contain dates and arbitrary prose); the wrap.md 3b instruction text updated to mandate the format; ELUVIAN_PATH.md Stage 5's "(with session-id key after E5)" line satisfied — cite it.
**D-3 — the glossary bootstrap (R2).** Which projects get `knowledge/glossary.md` (all 10 watched? active-only?); the scaffold template carrying the DEFINITION / RUNBOOK / TRAP→CODE discriminator (the 58-era banked decision — cite the baton block); whether the bootstrap is THIS executable's write set (10 files across 10 repos — enumerate the dispatch mechanics: which repos have their own .git vs live in the root repo, since a bellows-worktree dispatch cannot commit into sibling repos — this may split the executable or route per-repo) or a scaffold-on-first-use rule in the ritual doc instead; state the cost of each.
**D-4 — the domain-sweep ritual step.** The wrap.md addition (step 3d or a 3b extension): the sweep's question ("what domain knowledge did this session surface that belongs in the project's glossary?"), where it lands, and the HONEST enforcement boundary — wrap_check can verify a glossary file EXISTS or was TOUCHED this session (porcelain probes) but cannot verify the sweep was thought about; state what is checked (if anything), what is ritual-only, and why a touched-file gate would incentivize decoration (the earn-the-gate lesson) — the design may legitimately conclude ritual-only with visibility, but must SAY so.
**D-5 — coordination.** wrap_check.py is shared substrate (the E3 [2r] group, the portability env-overrides, this 3b edit — all in one file now); the mini machine's wrap flows (G5's machine arms; the fetch-freshness lesson: a keyed check judges the LOCAL baton — state the stale-clone behavior); the wrap.md edit rides in bellows (shop-infra, fine) but ELUVIAN_PATH.md's Stage 5 line and any root-doc glossary references are ROOT-repo writes — route them (the E3/E4 precedent: the still-unshipped doc follow-up plan — fold these lines INTO it or carry separately; name the choice).
**D-6 — test plan.** The keyed-check arms (newest-mine pass, newest-foreign fail, no-sid degrade, historical-lines inert, cross-machine newest); wrap.md is doc (no tests); glossary scaffolds (existence tests only if bootstrapped by the executable); the regression floor G7 unchanged; consumer sweep of the 3b failure message (test fixtures asserting on its text).
**D-7 — open questions.** Anything needing a NEW CEO ruling — glossary breadth (all projects vs active), and the degrade-arm choice if it genuinely changes enforcement posture — LISTED, never decided silently.

**Post-conditions:** D-1 through D-6 each with ≥1 file:line citation; D-7 present, exempt exactly when truthfully empty; the LESSONS fix-shape sentence quoted once; G1's predicate and G3's zero-glossary absence re-derived with positive controls; a Rule 27 gap table enumerating every change site the executable will touch.

**Deposits:**
- `/Users/marklehn/Developer/GitHub/bellows/knowledge/research/e5-wrap-keying-glossary-design-2026-08-25.md`

**Scope:**
- `/Users/marklehn/Developer/GitHub/bellows/knowledge/research/e5-wrap-keying-glossary-design-2026-08-25.md`

**Commit:** `git add knowledge/research/e5-wrap-keying-glossary-design-2026-08-25.md && git commit -m "[<id>] design: E5 wrap keying + glossary — 3b predicate, line format, bootstrap mechanics, ritual step"` in YOUR worktree cwd. `<id>` from your plan filename.
