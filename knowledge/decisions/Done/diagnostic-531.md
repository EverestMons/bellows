# bellows — diagnostic: rule_22 (c)'s two measured false-positive classes — the quoted-❌ scan and the mixed-table info row — history census + fix shapes

**Date:** 2026-08-25 | **Project:** bellows | **Tier:** Small | **Dispatch Mode:** bellows | **cycle_tier:** T1 | **Test Scope:** none (read-only diagnostic; writes one research doc) | **Execution:** Step 1 (DIAGNOSTIC) | **Priority:** 2

**auto_close:** false
**pause_for_verdict:** after_step_1

**Depends on:** the two CEO `--override-gate` acts of 2026-08-25 (plans 523 and 524, both on `rule_22_verification`), each adjudicated benign after independent substance verification. **The measured defects:** (1) plan 523's QA quoted a grep-target literal `` `❌ worktree teardown failed:` `` inside a table row whose status cell was ✅ — the (c) check's `"❌" in stripped` fires on the ❌ ANYWHERE in the row, code spans included; (2) plan 524's QA carried the plan-MANDATED status-less G8 info row ("Planner's post-close act — out of sandbox reach by design") in a table of ✅ rows — the missing-status defer discards only when a table has NO positive rows, so a mixed table's deliberate info row fires. Each false positive costs a CEO override act plus a Planner verification round.

## Why this exists

The gate is right to be strict — but a strictness that fires on a QA report QUOTING the thing it verified teaches agents to paraphrase probes (the earn-the-gate inversion), and one that refuses deliberate out-of-scope rows teaches them to decorate rows with fake statuses. Two overrides in one day is the recurrence threshold this shop acts on.

## What this plan does NOT do

- **It writes NO code.** One research deposit with a Rule 27 gap table.
- **It does not weaken (c)'s genuine arms** — a real `| test X | ❌ |` failure row must keep firing; the diagnostic's fix shapes are scoping refinements, and every proposal must state its false-NEGATIVE cost explicitly.

## Numbers discipline

⚠️ **Measured 2026-08-25 by the Planner; RE-DERIVE each — yours supersede and you say so.**

| id | pin | value | anchor/probe |
|---|---|---|---|
| C1 | the ❌ scan | gates.py:689 `if "❌" in stripped:` — fires anywhere in the row, backtick spans included, regardless of the status cell | read gates.py:643-706 (the full (c) loop) |
| C2 | the missing-status defer | gates.py:697-703 deferred rows; flushed as failures when `current_table_has_positive_row` — the mixed-table case has no escape | same read |
| C3 | the section scoping + status tokens | Shape 6C (2026-05-24): section-scoped to "verification" headers; `_is_positive_status_row` accepts ✅/PASS/OK/done/complete/verified with bounded cell equality | gates.py:643-651 comment + the helper |
| C4 | incident 1 | plan 523 step 2: evidence `(c) QA verification table row 89: \| 4 \| \`❌ worktree teardown failed:\` count == 2 \| ✅ \|` — a ✅ row flagged for a quoted literal | `verdicts/resolved/processed-verdict-523-step-2.md` + the gate_events row (overridden=1) |
| C5 | incident 2 | plan 524 step 2: evidence `(c) QA verification table row 75 missing status: \| G8 \| ~/.claude memory entry \| Planner's post-close act …` | `verdicts/resolved/processed-verdict-524-step-2.md` + gate_events (overridden=1) |
| C6 | the override catalog | both incidents resolved via `clear_plan.py --override-gate … rule_22_verification` — the E4 override layer working as designed, at real cost | lifecycle.db gate_events `overridden=1` rows for plans 523/524 (mode=ro) |

## MUST-PRESERVE

- ⚠️ **READ-ONLY.** The single deposit is the write set. DB via `mode=ro` only.
- ⚠️ **THE GREP SHIM IS BROKEN (every invocation errors `unknown option '-G'`): `/usr/bin/grep` for ALL probes; zero-match exits 1, never &&-chain; an errored probe is the shim, not an absence.**
- ⚠️ **THE SPLIT-PATH LAW:** `lifecycle.db` and `logs/` are untracked — absolute live-checkout paths; `verdicts/resolved/` IS tracked and present in your worktree.
- ⚠️ **Every claim cites file:line in CURRENT code; absence claims carry positive controls. EVERY DATE IS A FIXED LITERAL. Worktree dispatch; deposit path project-relative.**

## STEP 1 — DIAGNOSTIC: the incidence census, the two fix shapes, the regression fence

**Role:** DIAGNOSTIC.

Produce `/Users/marklehn/Developer/GitHub/bellows/knowledge/research/rule22c-parser-fix-design-2026-08-25.md` (project-relative in your worktree) settling AT LEAST the following, with a Rule 27 gap table:

**R-1 — the incidence census.** Sweep the FULL history: every `rule_22_verification` failure ever recorded — `gate_events` rows (mode=ro; include `overridden`), the `verdicts/ledger.jsonl` entries, and processed verdict files. Classify each occurrence: genuine failure (the gate catching real ❌/hedging/missing verification) vs the C4 class (quoted-❌) vs the C5 class (deliberate status-less row) vs other-false-positive vs indeterminate. The deliverable is the measured TRUE/FALSE-positive ratio — the fix's justification or its refutation. Also sweep the CORPUS of existing QA reports (`knowledge/qa/` + `knowledge/research/*qa*` + the evidence dirs across watched projects, sampled if huge — state the sample) for rows that WOULD fire under current (c): the latent-FP inventory.

**R-2 — fix shape A (the quoted-❌).** Settle the scoping rule: strip backtick spans (inline code) from the row before the ❌ scan — a QA report quoting a literal is evidence-of-verification, not an assertion of failure; a GENUINE failure marker sits outside code spans. State: the exact stripping mechanics (paired-backtick regex; the unpaired-backtick degenerate case must fail SAFE, i.e., scan the unstripped row); the false-negative cost (an agent could hide a real ❌ inside backticks — weigh: the (c) gate is one layer, the Planner's Rule 22(b) independent verification is another, and hiding-in-backticks is detectable adversarial conduct rather than the honest-mistake class this gate exists for — SAY this trade explicitly, don't bury it); the alternative shape (require the STATUS CELL to be non-positive before any ❌ fires) with its own costs (a row with ❌ in the status cell AND a trailing ✅ decoration would pass — construct the case).

**R-3 — fix shape B (the mixed-table info row).** Settle the escape for deliberate non-check rows: option (i) accept an explicit bounded-cell `N/A` token (extending `_is_positive_status_row`'s token discipline with a separate `_is_na_status_row` — an N/A row neither fires nor counts as the table's positive row); option (ii) an out-of-band row marker the plan/report must carry; option (iii) keep firing and make plans mandate status cells everywhere (the 527 QA already adapted this way — measure what it did: read `knowledge/qa/evidence/no-receipt-admission-hold/qa-report.md`'s G-row handling as the workaround precedent). Recommend one with the decoration-incentive cost stated (the earn-the-gate lesson is the tiebreaker: a rule that makes agents write fake ✅ or fake N/A is worse than one that makes Planners override occasionally — quantify with R-1's measured rates).

**R-4 — the regression fence.** The fix touches gates.py's hottest verification path. Enumerate: every existing test on `_gate_rule_22_verification` and `_is_positive_status_row` (name the test file and count); the (d) hedging check's interaction (it iterates the same rows — does backtick-stripping belong there too? measure whether (d) has fired on quoted hedge-words historically, same census method); the exact new-test list for both fix shapes including the adversarial arms (❌ hidden in backticks still humanly visible in the report; unpaired backtick; N/A on a row that should have been checked).

**R-5 — the executable's shape.** Small single-DEV+QA bellows plan; the Rule 27 gap table names every change site (gates.py hunks, the test file, nothing else expected — state if the census demands more).

**R-6 — open questions.** Forks needing a ruling — LISTED, never decided silently (candidate: R-3's option choice if the trade is genuine; the R-2 alternative if the census shows adversarial-❌ is a real class).

**Post-conditions:** R-1's census covers every recorded rule_22_verification failure with zero unclassified; C1-C6 re-derived or superseded with measurement shown; every fix shape carries its false-negative cost in its own text; the gap table enumerates the executable's sites.

**Deposits:**
- `/Users/marklehn/Developer/GitHub/bellows/knowledge/research/rule22c-parser-fix-design-2026-08-25.md`

**Scope:**
- `/Users/marklehn/Developer/GitHub/bellows/knowledge/research/rule22c-parser-fix-design-2026-08-25.md`

**Commit:** `git add knowledge/research/rule22c-parser-fix-design-2026-08-25.md && git commit -m "[<id>] diag: rule_22 (c) false positives — incidence census, quoted-marker + info-row fix shapes, regression fence"` in YOUR worktree cwd.

## Drafting Cycle
**Tier:** T1 computed — read-only single-deposit diagnostic.
**Walk register:** `governance/knowledge/research/walk-register-diagnostic-rule22c.md`
**Walks:** walk 0 pinned; **walks 1–2 complete** — five lenses each, BOTH dry (walk 1 carried one verification act — test_gates.py presence — and zero folds).
**Direction verdict (after walk 1): PROCEED.** Tested, not judged.
- Weak spots:          w1 dry; w2 dry
- Destruction:         w1 dry; w2 dry
- Vulnerabilities:     w1 dry (one probe run, no fold); w2 dry
- Integration-record:  w1 dry; w2 dry — close obligations discharged at this freeze
- ACID:                w1 dry; w2 dry
**Cold panel: NOT convened, decided with reasoning** — the E-family rule; read-only diagnostics close on warm walks (515-528 precedent).
**Conformance (§5):** recorded at the freeze from actual runs: walk_register_lint CONFORMANT (verdict channel, branched-on); cycle_check BAR_MET post-finalization (verdict channel, branched-on); plan_lint 0 FAIL at the scratch-mirror path.
**Closing:** **walk 2 met the bar — all five lenses dry.** Instruction series **0 → 0**. Receipt BEFORE staging (structural) → predicted auto-clear (read-only) → claim.

## Cycle Manifest
tier: T1
target: knowledge/research/rule22c-parser-fix-design-2026-08-25.md
class: read-only
reads: /Users/marklehn/Developer/GitHub/bellows/gates.py, /Users/marklehn/Developer/GitHub/bellows/lifecycle.db, /Users/marklehn/Developer/GitHub/bellows/verdicts/ledger.jsonl, /Users/marklehn/Developer/GitHub/bellows/verdicts/resolved/processed-verdict-523-step-2.md, /Users/marklehn/Developer/GitHub/bellows/verdicts/resolved/processed-verdict-524-step-2.md, /Users/marklehn/Developer/GitHub/bellows/tests/test_gates.py, /Users/marklehn/Developer/GitHub/bellows/knowledge/qa/evidence/no-receipt-admission-hold/qa-report.md
writes: knowledge/research/rule22c-parser-fix-design-2026-08-25.md
open_forks: none authored here — R-6 carries any that surface
walks: 2
yields: 0, 0
validation: cycle_check=BAR_MET, plan_lint=0_FAIL, fold_check=N/A
coherence: N/A

## Rule 20 — QA Self-Check Block

This step is DIAGNOSTIC-only; no QA agent runs. The Rule 20 self-check block is N/A for this step. Verification happens at the Planner's Rule 22 substance check after verdict consumption.
