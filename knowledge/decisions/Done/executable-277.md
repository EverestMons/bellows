# bellows — plan_lint §4 refinements: last-lens-line status (189/N5) + T0 regex fix (190/N6)
**Date:** 2026-07-25 | **Tier:** Small | **Dispatch Mode:** bellows | **Test Scope:** both | **Execution:** Step 1 (DEV) → Step 2 (QA) | **qa_steps:** 2 | **pause_for_verdict:** always | **cycle_tier:** T2

## CEO Context

**Gate 2, Plan B (the bellows half of the S2 split — ships FIRST).** Gate 1 (plan 275) routed proposals 187–190 all `codify`. Diagnostic 276 (Done) scoped Gate 2 → **S2 (split by repo)**, CEO-confirmed: **Plan B** (this — bellows `plan_lint` + tests for 189/N5 and 190/N6) ships first; **Plan A** (governance doc codification of all four + version bump + status advancement) `Depends on` this plan. This plan makes NO doc edit and NO status change — Plan A owns those.

**⚠️ Doc↔code window (intended, not a defect):** Plan B ships the 189/190 plan_lint CODE before Plan A updates §4's TEXT (which still reads "the closing line asserts a dry lens pass"; 189 reads the last LENS line instead). This is a brief, warn-first-SOFT wording mismatch — the INTENT is identical (check the last event is a dry pass), only the mechanism differs — closed immediately when Plan A (`Depends on` this plan) updates §4. The diagnostic (Q1c/Q6d) chose Plan-B-first deliberately: Plan B is standalone, and Plan A's QA verifies the §4 text matches this shipped code.

**Author from diagnostic 276's findings (Rule 27 — do NOT re-derive):** `/Users/marklehn/Developer/GitHub/governance/knowledge/research/gate2-architecture-edit-map-2026-07-25.md` §Q2 (the exact plan_lint edit designs) + §Q3 (the test changes). The authority for the §4 behaviour is `DRAFTING_CYCLE.md` §4 (read it, Rule 27) — but this plan only changes HOW two checks read their input, not what §4 mandates (that wording is Plan A's).

**⭐ WARN-FIRST is preserved (271's design point).** Both edits keep every `(f)` check a non-blocking WARN — `plan_lint` still exits 0; the `(f)` checks never append to `results` / never set `all_passed=False` (verified: plan_lint.py return is `0 if all_passed else 1`, line ~207). A mis-parse is a soft reminder, never a blocked deposit.

**The two edits (per diagnostic 276 §Q2):**
- **189/N5 — last-lens-line status (primary) + closing-line fallback.** Current `(f)` closing check (`plan_lint.py:196–202`) is the fuzzy `'fold' in closing_text and 'dry' not in closing_text`. New: read the **last lens line's last walk segment** (the structured `- <Lens>: … ; wN dry|folded` lines — ACID is always last for T1+; split on `;`, check the final segment for `dry` vs `folded`). **Keep the closing-line heuristic as a FALLBACK** when no structured lens lines are parseable (legacy/degenerate) — this preserves back-compat with legacy-format logs (load-bearing on warn-first: a legacy mis-WARN is soft). The structured format is ALREADY in use (271/274/275/diag-276), so no plan's format changes.
- **190/N6 — loosen the T0 regex.** Current `plan_lint.py:165` `re.match(r'^T([012])$', cycle_tier_raw)` rejects §3's collapsed T0 form (`T0 (no trigger); …`). Change `$` → `\b`: `re.match(r'^T([012])\b', cycle_tier_raw)`. Accepts bare `T0`/`T1`/`T2` (all existing plans) AND the collapsed form. One-character change; no back-compat concern (bare forms match `\b` too).

**Scope discipline:** edits `scripts/plan_lint.py` + `tests/test_plan_lint.py` ONLY. No other bellows module; no doc edit (Plan A); no DB/status change; **no daemon behaviour change** (plan_lint is Planner-authoring-time, NOT daemon-dispatch — diagnostic 276 verified 0 `plan_lint` invocations across `bellows.py`/`runner.py`/`gates.py`; NO daemon restart needed). **Deposit-once** (grep `knowledge/decisions/` first).

**⚠️ §4-flip watch (from diagnostic 276 A3):** the `(f)` checks must STAY warn-first (exit 0) at HEAD — confirm before editing; the flip-to-blocking is a separate future plan, not this one.

**Authoring self-check:** run `bellows/scripts/plan_lint.py` on the FINAL post-cycle draft — expect exit 0, (a)-(d) PASS, §4 check passes (bare `cycle_tier: T2` + full block), and **NO WARN** (⭐ CB3 — verified by a live run: Step 2's text contains `pytest tests/`, which sets `has_test_in_text` at `plan_lint.py:~149` and SUPPRESSES the "mentions tests but declares no test scope" WARN; do NOT expect that WARN — the earlier prediction of "one benign WARN" was empirically wrong, the predicted-number class).

## How to Run This Plan

**Bootstrap prompt:**
```
Read the plan at knowledge/decisions/in-progress-executable-<id>.md (daemon renames the deposited placeholder on claim). Execute Step 1 ONLY. After completing Step 1, STOP and wait for my confirmation.
```

---
---

## STEP 1 — DEV

---

> **FIRST — post a short visible chat message (1-2 sentences) confirming you are starting this plan and your immediate next action.** Do NOT rename this plan file. Read your Bellows Developer specialist file, then `scripts/plan_lint.py` (the current `(f)` Drafting-Cycle check, lines ~163–202, + the WARN mechanism) and — for the authoritative behaviour — `/Users/marklehn/Developer/GitHub/DRAFTING_CYCLE.md` §4 (ABSOLUTE path, it lives at the REPO root outside this worktree) and the diagnostic findings `/Users/marklehn/Developer/GitHub/governance/knowledge/research/gate2-architecture-edit-map-2026-07-25.md` §Q2/§Q3 (ABSOLUTE path — the design to apply).
>
> You are the Bellows Developer. Two edits to `plan_lint.py`'s `(f)` check, BOTH warn-first (exit 0 preserved).
>
> **Task A0 — pre-edit cleanliness + warn-first precondition.** `git -C /Users/marklehn/Developer/GitHub/bellows status --porcelain -- scripts/plan_lint.py tests/test_plan_lint.py` empty. **If DIRTY — resume disambiguation (259 / Rule 56):** grep the dirty `plan_lint.py`/test file for THIS plan's own edits (the `^T([012])\b` regex; the last-lens-line parser; the new test names). All present + attributable to this plan → `git -C <bellows> restore scripts/plan_lint.py tests/test_plan_lint.py` then reapply from scratch (NEVER hand-patch a partial apply). Any unattributable/foreign hunk → HALT, do NOT restore. **Confirm the `(f)` checks are warn-first at HEAD** (diagnostic 276 A3): read `plan_lint.py` and verify every `(f)` WARN is a bare `print(...)` that never appends to `results` and never sets `all_passed=False`; the return is `0 if all_passed else 1`. If any `(f)` check already FAILs (flipped to blocking), HALT and report — the back-compat reasoning changes.
>
> **Task A — 190/N6 (the one-char regex fix).** Change `re.match(r'^T([012])$', cycle_tier_raw)` (line ~165) to `re.match(r'^T([012])\b', cycle_tier_raw)`. Grep-confirm the edit landed and no other `^T([012])$` occurrence exists. **Deliberate side effect (document, do NOT over-restrict):** `\b` accepts trailing content after the digit on ALL tiers, not just the intended T0 collapsed form — e.g. `T2 (governance)` now parses as T2 where `$` would have WARNed. This is BENIGN (the tier number is still correctly extracted, the block is still validated per tier; §3 specifies bare T1/T2 by convention, not enforced, and warn-first means bare-enforcement is not load-bearing). Do NOT try to restrict the regex to "T0-collapsed only" — that adds complexity for no safety gain.
>
> **Task B — 189/N5 (last-lens-line primary + closing fallback).** Per diagnostic 276 §Q2 — but the diagnostic only SKETCHED the approach (WB1); YOU author the parser against the REAL log formats, which vary. **(1) primary** — find the **last lens result line before the `**Closing:**` line** in the `## Drafting Cycle` block: the last line matching `^-\s*(cold[\s-]+)?(weak[\s-]*spots|destruction|vulnerabilit|integration|acid)` (case-insensitive; `[\s-]` matches both "weak spots" and the hyphenated "Cold weak-spots"; this correctly picks the final warm/cold/Walk-3 lens line, whichever ran last). Determine its status with the **SAFE rule** (⭐ CB1 — the naive "final mention / trailing portion" reading MISPARSES real Walk-3 ACID lines such as `→ dry. 11 folds cohere` or `w2 dry — 6 folds cohere`, where the prose "folds" follows "dry" → a false fold-WARN on a plan that closed DRY, including Plan B's OWN block): **WARN iff the last lens line contains a fold-family token (`fold`/`folded`) AND does NOT contain the word `dry` anywhere in that line.** Rationale: a lens line that mentions `dry` anywhere asserts a dry pass (the trailing `N folds cohere` is a count, not the last event); only a line with a fold token and NO `dry` ended on a fold. This matches the convention plan 275's §5 note documents verbatim ("passes §4 ONLY because 'dry' co-occurs with 'fold'"). Do NOT parse "final segment / trailing portion" — the whole-line `dry`-presence test is the robust one. **(2) fallback** — if NO lens line matches, fall back to the existing closing-line keyword check (back-compat for legacy/degenerate blocks). Keep it LENIENT (warn-first tolerates a false reminder; do NOT over-parse — a false reminder is soft). Read the plan file as UTF-8; never crash on a missing/empty/malformed block → degrade to a WARN or silent pass, never an exception.
>
> **Task C — protect existing tests (destruction, 271 Task B).** Grep `tests/test_plan_lint.py` for the existing `(f)` tests (diagnostic 276 §Q3 enumerated five: `test_lint_cycle_compliant_t2_no_warn`, `_tierless_warns`, `_t1_missing_acid_warns`, `_t0_no_block_warn`, `_fold_closing_warns`). Run them. **`test_lint_cycle_fold_closing_warns` will change behaviour** (its fixture has ACID's last walk `dry` but a fold-closing line; the new primary reads the lens line = dry → no WARN): per diagnostic 276 §Q3, make the fixture internally consistent (ACID's lens line contains a fold token AND no `dry`) so the test still expects a fold WARN — **preserving the test's INTENT** (a fold-as-last-event WARNs). Report each edit explicitly. Do NOT weaken the new check to avoid a test edit. **⭐ CB2 — keep the new fold-WARN message text containing BOTH `fold` and `dry lens pass`** (the existing message `Drafting Cycle closing indicates fold as last event, not a dry lens pass` already does): the retained `_fold_closing_warns` asserts both substrings (`test_plan_lint.py:~475-476`), so reusing the message keeps this a FIXTURE-only edit (QA row 7's "only the fixture changed"). If the message MUST change, that is a permitted second edit — state it explicitly so QA row 7 verifies fixture + message rather than HALTing on "fixture-only".
>
> **Task D — new observe-the-effect tests (vulnerabilities, 271 Task C; diagnostic 276 §Q3).** Add tests that RUN the check on real plan text and assert the WARN fires / does not fire, each also asserting **exit 0**:
> - **⭐ REAL-LOG fixtures (W1 — prove the lenient parser against ACTUAL formats, not idealized ones):** **EMBED** the `## Drafting Cycle` blocks of real Done plans as string literals in the test (copy verbatim from `executable-271.md`, `executable-274.md`, the just-shipped Gate-1 plan's block, and diag-276's — capturing the mixed `.`/`→`/`; wN dry` formats + the cold-panel + Walk-3 multi-lens-line structure). **Embed, do NOT read the files cross-tree** (V1: a bellows worktree reading lessons-forge/governance plans needs absolute paths and is brittle if the plans ever move; a self-contained string fixture is robust). Assert each parses to a DRY last event → NO fold WARN (they all closed dry).
> - **Degenerate (V1/3.4):** a lens line with NO dry/fold status (e.g. `- ACID: [pending]`), a status-less block, and an empty block → no crash, no false fold-WARN (lenient — warn-first).
> - ACID last-walk `w3 dry` (synthetic) → NO closing WARN (primary reads dry).
> - ACID last-walk `w1 1 folded` + a benign closing line → fold WARN fires (primary reads folded).
> - a legacy block with NO structured lens lines but a fold-closing prose line → fallback fires the WARN (back-compat).
> - **190:** a T0 plan with the collapsed form `**cycle_tier:** T0 (no trigger); integration-vs-record pass: dry.` → NO cycle_tier WARN (regex now accepts it). (This currently WARNs — it is the fix.)
> - a compliant real T2 block (use `/Users/marklehn/Developer/GitHub/governance/knowledge/decisions/Done/executable-270.md` or a current T2) → NO drafting-cycle WARN.
>
> **Run targeted tests:** `python3 -m pytest tests/ -k "plan_lint or lint" --tb=short -q 2>&1 | cat`. Then run `plan_lint` live against a real compliant T2 plan and a collapsed-T0 fixture; paste the RAW output showing the new behaviour + `echo $?` = 0 on each.
>
> **Scope:**
> - `scripts/plan_lint.py`
> - `tests/test_plan_lint.py`
> - `knowledge/development/plan-lint-189-190-dev-2026-07-25.md`
>
> **Deposit:** `knowledge/development/plan-lint-189-190-dev-2026-07-25.md` — the two edits (with the exact before/after lines), the warn-first confirmation (exit 0 on all cases), the `_fold_closing_warns` fixture edit with intent preserved, the new tests, and the RAW targeted-test + live-run output. Canonical Python/MCP file-write — NO heredoc. Commit all (NO push). `#### Prompt Feedback` in `### Ledger Updates`.
>
> **Deposits:**
> - `knowledge/development/plan-lint-189-190-dev-2026-07-25.md`
>
> **STOP. Do NOT proceed to Step 2. Wait for CEO verdict.**

---
---

## STEP 2 — QA

---

> **Before starting, read the Step-1 dev-log + confirm its Output Receipt is Complete; else halt and report.** Post a short visible chat message confirming you are starting Step 2 (QA). You are Bellows QA. Verification + reporting only — no code edits. If a check fails, report it; do NOT fix it. Do NOT use Monitor.
>
> **MANDATORY — Rule 20 self-check (canonical block, Checklist #4 — the exact template with all four placeholders filled, NOT a paraphrase).** Run the canonical Rule 20 self-check from `/Users/marklehn/Developer/GitHub/RULE_20_SELF_CHECK_BLOCK.md` (ABSOLUTE path — governance root, outside this worktree). Fill the four placeholders:
> - `plan_slug`: `plan-lint-189-190-2026-07-25`
> - `qa_report_path`: `<your-own-tree-abs>/knowledge/qa/plan-lint-189-190-qa-2026-07-25.md`
> - `evidence_dir`: `<your-own-tree-abs>/knowledge/qa/evidence/plan-lint-189-190-2026-07-25/` — derive from `pwd` (own tree), NOT a hardcoded path.
> - `required_evidence_files`: `[targeted-tests.txt, full-suite.txt]`
>
> Deposit both evidence files BEFORE running the block (it `sys.exit(1)`s if either is missing/empty). Include the block's literal stdout; the banner `Rule 20 — QA Self-Check Results` + `PASSED — SELF-CHECK PASSED` line must appear byte-exact (em-dash U+2014). If it prints FAILED, halt. End with a self-grep confirming the banner.
>
> **Evidence rule:** deposit RAW command output (≥ last 200 lines incl. the pytest summary line), never a summary.
>
> **Scope:**
> - `knowledge/qa/plan-lint-189-190-qa-2026-07-25.md`
> - `knowledge/qa/evidence/plan-lint-189-190-2026-07-25/targeted-tests.txt`
> - `knowledge/qa/evidence/plan-lint-189-190-2026-07-25/full-suite.txt`
>
> Verification table, one row per claim (HALT on any FAIL). **Write the raw targeted-test output to `targeted-tests.txt` and the full-suite output to `full-suite.txt`** (the two `required_evidence_files`):
> 1. **Warn-first preserved** — run `plan_lint` on a tier-less plan and a T1 plan missing a lens; each prints the WARN AND exits 0 (paste WARN + `echo $?`). The `(f)` checks can never block a deposit.
> 2. **190 fixed** — a T0 plan with the collapsed form `**cycle_tier:** T0 (no trigger); …` emits NO cycle_tier WARN + exit 0. Confirm the regex is `^T([012])\b`.
> 3. **189 primary reads the last lens line** — a plan whose ACID last segment is `dry` (but with a fold-mentioning closing prose) → NO fold WARN; a plan whose ACID last segment is `folded` → fold WARN fires. Both exit 0.
> 4. **189 fallback intact** — a legacy block with no structured lens lines + a fold-closing line → the fallback fires the WARN (back-compat), exit 0.
> 5. **Compliant real plan clean** — `plan_lint` on a current compliant T2 plan emits NO drafting-cycle WARN.
> 6. **No crash on degenerate input** — empty/malformed `## Drafting Cycle` block WARNs or passes, never raises.
> 7. **Existing behaviour intact** — every prior `plan_lint` test passes; confirm the ONLY test edit was `_fold_closing_warns`'s fixture (Step-1 Task C), intent preserved.
> 8. **Scope** — `git -C /Users/marklehn/Developer/GitHub/bellows --no-pager diff --stat` limited to `scripts/plan_lint.py` + `tests/test_plan_lint.py`; no other module.
> 9. **Full suite** — `python3 -m pytest tests/ --tb=short -q 2>&1 | cat`, foreground; RAW tail incl. summary. Baseline: the prior bellows suite pass count (compute from `--collect-only` + reconcile against the most recent prior bellows QA); any new failure beyond the new tests is a regression.
>
> **Deposit:** the QA report + the two evidence files. Canonical Python/MCP file-write — NO heredoc. Commit all (NO push). In `### Ledger Updates` include `#### Project Status` (one milestone: plan_lint §4 refined — 189/N5 reads the last lens line's status [closing-line fallback for legacy logs], 190/N6 T0 regex loosened to `^T([012])\b`; warn-first preserved; Gate 2 Plan B complete, Plan A [doc codification + status] unblocked) and `#### Prompt Feedback`.
>
> **Deposits:**
> - `knowledge/qa/plan-lint-189-190-qa-2026-07-25.md`
> - `knowledge/qa/evidence/plan-lint-189-190-2026-07-25/targeted-tests.txt`
> - `knowledge/qa/evidence/plan-lint-189-190-2026-07-25/full-suite.txt`
>
> **Do NOT move this plan to `Done/`.** The close path is owned by Bellows on continue-verdict consumption (Rule 8) — never by the agent.

---

## Drafting Cycle
**Tier:** T2 — triggers fired: T-6 (governance surface — edits the `plan_lint` gate). Structure-clone of 271 (the §4 gate implementation) + authored from diagnostic 276's designs (T-8 does not fire). T-2 does NOT fire (edits code+tests, not data); no daemon coordination (plan_lint is authoring-time, 276-verified).
**Walks:** Walk 1 complete (v0 → v5): 5 folds (W1; D1; V1; R1; A1). Walk 2 (confirming) COMPLETE (v5 → v6): only-minor (WB1); sequential phase done → T2 cold panel.
- Weak spots:          w1 → v1: 1 folded (W1 1.2/1.3 — the 189 parser design [diagnostic's `;`-split "last segment"] assumes a format the REAL logs don't follow [mixed `.`/`→`/`; wN dry`, + cold-panel/Walk-3 multi-lens-line ambiguity]; per WB1 the diagnostic only sketched → Task B now specifies a LENIENT parser [last lens line before Closing via anchored regex incl. `cold`, final-status leniently] + Task D tests on REAL Done-plan blocks [271/274/275/diag-276], not idealized fixtures). Verified clean: Task A 190 regex `\b` logic sound (matches bare T0/T1/T2 + collapsed T0, rejects T3/T0X); A0 warn-first precondition checkable; Task C fixture edit coherent with the new parser. w2 → v6: 1 minor (WB1 — the 189 regex `weak\s*spots` missed the hyphenated "Cold weak-spots" cold-panel line → `weak[\s-]*spots`). Verified: 5 folds hold + cohere (V1's embedded blocks test W1's parser; A1↔DEV edit); Scope↔Deposits match both steps (code files in Scope, dev-log/QA the deposits — 271 pattern).
- Destruction:         w1 → v2: 1 minor folded (D1 2.2 — the 190 `\b` loosening has a benign side effect: accepts trailing content on ALL tiers [`T2 (governance)` now parses], watering down the old bare-T1/T2 enforcement; documented as intentional [tier still extracted; warn-first; don't over-restrict]). Verified: nothing breaks (2.1 — 190 strictly more permissive, existing T1/T2 parse, malformed T0X/T00/T3 still WARN; 189 strengthening + fallback + real-log tests); existing behaviour guarded (Task C protect-tests, QA rows 6/7/9); 189 doesn't affect T0 (no block check); edits bounded + reversible (Task A0 clean-gate). **w2 dry** — no fold relaxed a guard: WB1 broadens the match (more accurate), V1's embedded blocks preserve real-format coverage, A1 strengthens recovery, D1/R1 documentation; warn-first/protect-existing/no-crash/scope guards intact; harm surface unchanged.
- Vulnerabilities:     w1 → v3: 1 folded (V1 3.1/3.4 — the real-log fixtures span repos [271 bellows / 274,275 LF / diag-276 gov]; a bellows-worktree cross-tree read needs absolute paths + is brittle if plans move → EMBED the real Cycle Log blocks as string literals [self-contained, still proves the parser on real formats]; + a degenerate test [status-less/`[pending]` lens line, empty block → no crash, no false fold-WARN]). Verified clean: (3.2) tests RUN the check on real embedded text (observe-the-effect); (3.1) DRAFTING_CYCLE.md + diagnostic-findings reads use absolute paths (Task A0/reads); (3.3) no cross-repo import binding. **w2 dry** — V1 embedded blocks hold (no cross-tree vacuous risk); WB1's `[\s-]*` opens no degenerate edge (still anchored by `^-\s*` + specific keywords); remaining cross-tree reads (doc, findings) absolute; degenerate coverage intact.
- Integration-record:  w1 → v4: 1 folded (R1 4.1 — named the intended doc↔code window: Plan B ships the 189/190 code before Plan A updates §4's text; brief, warn-first-soft, same-intent, closed by Plan A [Depends-on]; diagnostic Q1c/Q6d chose Plan-B-first deliberately). Verified: clones 271 pattern; authors-from diagnostic 276 (Rule 27); §6 doc↔gate satisfied by S2 Depends-on sequencing; no doc/status edit (Plan A owns); Rule 20 M1 form carried from Gate-1 §5; not trivial; T2 right-sized. **w2 dry** — all folds align with the record (W1↔271 observe-the-effect + diagnostic design; D1↔`\b` choice; V1↔self-contained-test; R1↔§6+Q1c/Q6d; A1↔259/Rule-56; WB1↔real format); §6 satisfied by S2 sequencing; Rule 27 honored; no re-trip.
- ACID:                w1 → v5: 1 folded (A1 5.1 — Task A0's resume disambiguation too terse for a code edit → spelled out the 259/Rule-56 dirty-tree handling [own-edit-check → restore+reapply; foreign → HALT, never hand-patch]). Sound: 5.3 isolation near-empty (code edit, daemon serializes + doesn't invoke plan_lint per 276); 5.2 consistency (invariants stated; doc↔code closed at Plan A's QA); 5.4 durability (git-committed; Plan A gets linted by Plan B's improved gate — benign recursion). **w2 dry** — 6 folds cohere (W1+V1 reinforce, WB1 refines W1's regex, A1↔DEV edit); no soft premise (warn-first verified at HEAD, plan_lint authoring-time 276-verified, real-log format V1-tested).
**Cold panel (T2):** RUN — FOCUSED (1 comprehensive fresh reader: guard-diff vs 271 + code-correctness of 189/190 vs live plan_lint.py + parser-on-real-logs), given the bounded warn-only change (271's precedent) + the highest-value angles; logged as focused, not a full 5-lens panel. → v7: 3 folded. ⭐ **CB1 (HIGH — the warm walks MISSED it, exactly the clone-drift value):** the 189 parser wording misparsed real Walk-3 ACID lines (`→ dry. N folds cohere` — "folds" after "dry" → false fold-WARN on a DRY close, incl. Plan B's OWN block) → pinned the SAFE rule (fold token AND `dry` absent anywhere in the line). CB2 (MED) `_fold_closing_warns` message coupling could force a 2nd test edit → keep the message's `fold`+`dry lens pass` substrings. CB3 (LOW) the "one benign WARN" self-check note is empirically false (Step 2's `pytest tests/` suppresses it) → corrected to NO WARN. **Guard-diff vs 271: 0 dropped guards** (28 preserved/strengthened); 190 code claims EXACT vs live (line 165, one occurrence). ⚠️ N2 (pre-existing gap, NOT folded — outside 189/190 scope): the "T2 missing cold-panel → WARN" sub-rule has no regression test — a Forward Register note for a future plan.
**Cold panel materially changed the draft (CB1 HIGH) → warm confirming Walk 3 owed before §5.**
**Walk 3 (warm confirming, on v7):**
- Weak spots:          → dry. CB1 safe rule holds + robust (dry-present-anywhere → no WARN covers all real Walk-3 formats incl. Plan B's own block; fold-token-no-dry → WARN for genuine fold-closes; degenerate `[pending]`/no-token → lenient). CB2/CB3 cohere; V1's embedded real-log tests are the safety net for CB1. No new weak spot.
- Destruction:         → dry. No fold relaxed a guard: CB1 CORRECTS a false-WARN (still WARNs genuine fold-closes; the "dry anywhere → no WARN" is the SAME residual-trust §4 always had, by design; reading the structured lens line is net-more-reliable than the old closing prose), CB2 protects the retained test, CB3 corrects a note. Harm surface unchanged.
- Vulnerabilities:     → dry. CB1 whole-line rule degenerate-safe (empty line → lenient no-WARN; no lens line → closing fallback; UTF-8 read handles `→` arrows, `dry`/`fold` checks are ASCII). V1's embedded tests prove it on all real formats; remaining cross-tree reads (doc, findings) absolute. No new edge.
- Integration-record:  → dry. CB1 codifies the `dry`-co-occurs-`fold` convention 275's §5 note + the diagnostic documented; CB2↔271 protect-existing; CB3↔predicted-number lesson. CB1's deviation from the diagnostic's `;`-split sketch is Rule-27-consistent (WB1: diagnostic sketched, DEV authors the correct parser; the sketch was buggy). No re-trip.
- ACID:                → dry. All 9 folds cohere (W1+WB1+CB1 build the correct parser; V1+CB1 reinforce — embedded tests are CB1's safety net; CB2↔Task C↔row 7; A1↔DEV edit); no soft premise (warn-first HEAD-verified, plan_lint authoring-time 276-verified, real-log format V1-tested + CB1-corrected).
**Conflicts:** none (no cross-lens conflict across all walks).
**Closing:** Walk 3 (warm confirming) closed on a dry ACID (Lens 5) pass — last event a lens pass, not a fold. **Adversarial phase COMPLETE:** Walk 1 (5 folds) → Walk 2 (only-minor WB1) → focused cold panel (3 folds incl. the HIGH CB1 the warm walks MISSED) → Walk 3 (dry). **9 folds, 8 revisions (v0→v7).** **§5 mechanical conformance DONE:** plan_lint exit 0, all (a)-(d) PASS, **NO WARN — CB3 CONFIRMED** (Step 2's `pytest tests/` suppresses the test-scope WARN; the "one benign WARN" prediction was wrong); §4 check passes (cycle_tier T2 + block + cold-panel line + dry closing — Plan B linted clean by the CURRENT §4, a recursion). Rules/Checklist clean (Rule 20 M1 full form carried from Gate-1 §5; #29 predicted-number fixed by CB3; #32 observe-the-effect in Task D; Checklist #3 STOP-prose tolerated per 271). §5 clean → Walk 3 stands as the closing pass. Ready to deposit once (pending CEO go).
