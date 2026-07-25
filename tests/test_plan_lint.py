import os
import subprocess
import sys
import tempfile

BELLOWS_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LINT_SCRIPT = os.path.join(BELLOWS_ROOT, "scripts", "plan_lint.py")


def _run_lint(plan_text):
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write(plan_text)
        f.flush()
        try:
            result = subprocess.run(
                [sys.executable, LINT_SCRIPT, f.name],
                capture_output=True, text=True, timeout=30,
            )
            return result
        finally:
            os.unlink(f.name)


GOOD_PLAN = """\
# Test Plan
**Date:** 2026-07-02 | **Dispatch Mode:** bellows | **qa_steps:** 2 | **pause_for_verdict:** always

## STEP 1 — DEV

> Do the work.
>
> **Deposits:**
> - `knowledge/development/dev-log.md`

## STEP 2 — QA

> Verify deliverables.
>
> Your QA report MUST include the byte-exact banner `Rule 20 — QA Self-Check Results` and a `PASSED — SELF-CHECK PASSED` line.
>
> **Deposits:**
> - `knowledge/qa/qa-report.md`
"""


def test_lint_well_formed_plan_passes():
    """(i) Well-formed fixture plan passes all checks exit 0."""
    result = _run_lint(GOOD_PLAN)
    assert result.returncode == 0, f"Expected exit 0, got {result.returncode}\nstdout: {result.stdout}\nstderr: {result.stderr}"
    assert "FAIL" not in result.stdout


def test_lint_missing_deposits_block_fails():
    """(ii) Missing Deposits block in a deposit-mentioning step -> exit 1 naming check (b)."""
    plan = """\
# Test Plan
**Date:** 2026-07-02 | **Dispatch Mode:** bellows | **pause_for_verdict:** always

## STEP 1 — DEV

> Do the work. Deposit the dev log as inline prose.

"""
    result = _run_lint(plan)
    assert result.returncode == 1, f"Expected exit 1, got {result.returncode}\nstdout: {result.stdout}"
    assert "(b)" in result.stdout


def test_lint_qa_missing_banner_pair_fails():
    """(iii) QA plan missing the banner pair -> exit 1 naming check (c)."""
    plan = """\
# Test Plan
**Date:** 2026-07-02 | **Dispatch Mode:** bellows | **qa_steps:** 2 | **pause_for_verdict:** always

## STEP 1 — DEV

> Do the work.
>
> **Deposits:**
> - `knowledge/development/dev-log.md`

## STEP 2 — QA

> Verify deliverables.
>
> **Deposits:**
> - `knowledge/qa/qa-report.md`
"""
    result = _run_lint(plan)
    assert result.returncode == 1, f"Expected exit 1, got {result.returncode}\nstdout: {result.stdout}"
    assert "(c)" in result.stdout


def test_lint_empty_scope_block_fails():
    """(vi) Present-but-empty Scope block → exit 1 naming check (d)."""
    plan = """\
# Test Plan
**Date:** 2026-07-02 | **Dispatch Mode:** bellows | **pause_for_verdict:** always

## STEP 1 — DEV

> Do the work.
>
> **Scope:**
>
> **Deposits:**
> - `knowledge/development/dev-log.md`

"""
    result = _run_lint(plan)
    assert result.returncode == 1, f"Expected exit 1, got {result.returncode}\nstdout: {result.stdout}"
    assert "(d)" in result.stdout


def test_lint_test_mentioned_no_test_scope_warns():
    """(vii) Step mentions tests but declares no test scope -> WARN fires, exit code unaffected."""
    plan = """\
# Test Plan
**Date:** 2026-07-02 | **Dispatch Mode:** bellows | **pause_for_verdict:** always

## STEP 1 — DEV

> Do the work and run the test suite.
>
> **Scope:**
> - `gates.py`
>
> **Deposits:**
> - `knowledge/development/dev-log.md`

"""
    result = _run_lint(plan)
    assert result.returncode == 0, f"Expected exit 0 (WARN only), got {result.returncode}\nstdout: {result.stdout}"
    assert "WARN" in result.stdout
    assert "test scope" in result.stdout.lower() or "test scope" in result.stdout


def test_lint_unrecognized_dispatch_mode_fails():
    """(iv) Unrecognized dispatch_mode -> exit 1 naming check (a)."""
    plan = """\
# Test Plan
**Date:** 2026-07-02 | **Dispatch Mode:** auto_magical | **pause_for_verdict:** always

## STEP 1 — DEV

> Do the work.

"""
    result = _run_lint(plan)
    assert result.returncode == 1, f"Expected exit 1, got {result.returncode}\nstdout: {result.stdout}"
    assert "(a)" in result.stdout


def test_lint_qa_steps_cross_check_good():
    """(a) Good DEV→QA plan (qa_steps: 2, STEP 2 QA-labeled) emits NO qa_steps WARN, exit 0."""
    plan = """\
# Test Plan
**Date:** 2026-07-02 | **Dispatch Mode:** bellows | **qa_steps:** 2 | **pause_for_verdict:** always

## STEP 1 — DEV

> Do the work.
>
> **Deposits:**
> - `knowledge/development/dev-log.md`

## STEP 2 — QA

> Verify deliverables.
>
> Your QA report MUST include the byte-exact banner `Rule 20 — QA Self-Check Results` and a `PASSED — SELF-CHECK PASSED` line.
>
> **Deposits:**
> - `knowledge/qa/qa-report.md`
"""
    result = _run_lint(plan)
    assert result.returncode == 0, f"Expected exit 0, got {result.returncode}\nstdout: {result.stdout}"
    assert "qa_steps lists step" not in result.stdout
    assert "QA-labeled but absent from qa_steps" not in result.stdout


def test_lint_qa_steps_plan133_trap():
    """(b) Plan-133 shape: qa_steps: 1, STEP 1 DEV / STEP 2 QA → 'gated as QA' WARN, exit 0."""
    plan = """\
# Test Plan
**Date:** 2026-07-02 | **Dispatch Mode:** bellows | **qa_steps:** 1 | **pause_for_verdict:** always

## STEP 1 — DEV

> Do the work.
>
> **Deposits:**
> - `knowledge/development/dev-log.md`

## STEP 2 — QA

> Verify deliverables.
>
> Your QA report MUST include the byte-exact banner `Rule 20 — QA Self-Check Results` and a `PASSED — SELF-CHECK PASSED` line.
>
> **Deposits:**
> - `knowledge/qa/qa-report.md`
"""
    result = _run_lint(plan)
    assert result.returncode == 0, f"Expected exit 0 (WARN only), got {result.returncode}\nstdout: {result.stdout}"
    assert "gated as QA (plan-133 trap)" in result.stdout
    assert "QA-labeled but absent from qa_steps" in result.stdout


def test_lint_qa_steps_qa_labeled_absent():
    """(c) QA-labeled step absent from qa_steps → 'will not be gated' WARN, exit 0."""
    plan = """\
# Test Plan
**Date:** 2026-07-02 | **Dispatch Mode:** bellows | **qa_steps:** 3 | **pause_for_verdict:** always

## STEP 1 — DEV

> Do the work.
>
> **Deposits:**
> - `knowledge/development/dev-log.md`

## STEP 2 — QA

> Verify deliverables.
>
> Your QA report MUST include the byte-exact banner `Rule 20 — QA Self-Check Results` and a `PASSED — SELF-CHECK PASSED` line.
>
> **Deposits:**
> - `knowledge/qa/qa-report.md`
"""
    result = _run_lint(plan)
    assert result.returncode == 0, f"Expected exit 0 (WARN only), got {result.returncode}\nstdout: {result.stdout}"
    assert "will not be Rule 20/22 gated" in result.stdout


def test_lint_qa_steps_list_form():
    """(d) List-form qa_steps: [2] parses identically — no false WARN."""
    plan = """\
# Test Plan
**Date:** 2026-07-02 | **Dispatch Mode:** bellows | **qa_steps:** [2] | **pause_for_verdict:** always

## STEP 1 — DEV

> Do the work.
>
> **Deposits:**
> - `knowledge/development/dev-log.md`

## STEP 2 — QA

> Verify deliverables.
>
> Your QA report MUST include the byte-exact banner `Rule 20 — QA Self-Check Results` and a `PASSED — SELF-CHECK PASSED` line.
>
> **Deposits:**
> - `knowledge/qa/qa-report.md`
"""
    result = _run_lint(plan)
    assert result.returncode == 0, f"Expected exit 0, got {result.returncode}\nstdout: {result.stdout}"
    assert "qa_steps lists step" not in result.stdout
    assert "QA-labeled but absent from qa_steps" not in result.stdout


def test_lint_qa_steps_malformed():
    """(e) Malformed qa_steps: abc — no crash, no traceback, exits without error."""
    plan = """\
# Test Plan
**Date:** 2026-07-02 | **Dispatch Mode:** bellows | **qa_steps:** abc | **pause_for_verdict:** always

## STEP 1 — DEV

> Do the work.
>
> **Deposits:**
> - `knowledge/development/dev-log.md`
"""
    result = _run_lint(plan)
    assert "Traceback" not in result.stderr
    assert "Traceback" not in result.stdout
    assert "qa_steps lists step" not in result.stdout


def test_lint_qa_steps_absent_no_warn():
    """(f) No qa_steps field → no qa_steps WARN."""
    plan = """\
# Test Plan
**Date:** 2026-07-02 | **Dispatch Mode:** bellows | **pause_for_verdict:** always

## STEP 1 — DEV

> Do the work.
>
> **Deposits:**
> - `knowledge/development/dev-log.md`
"""
    result = _run_lint(plan)
    assert "qa_steps lists step" not in result.stdout
    assert "QA-labeled but absent from qa_steps" not in result.stdout


def test_lint_titlecase_step_headings_with_qa_steps_fails():
    """(e-a) qa_steps: 2 with title-case '## Step N' headings → (e) FAIL, exit 1."""
    plan = """\
# Test Plan
**Date:** 2026-07-13 | **Dispatch Mode:** bellows | **qa_steps:** 2 | **pause_for_verdict:** always

## Step 1 — DEV

> Do the work.
>
> **Deposits:**
> - `knowledge/development/dev-log.md`

## Step 2 — QA

> Verify deliverables.
>
> Your QA report MUST include the byte-exact banner `Rule 20 — QA Self-Check Results` and a `PASSED — SELF-CHECK PASSED` line.
>
> **Deposits:**
> - `knowledge/qa/qa-report.md`
"""
    result = _run_lint(plan)
    assert result.returncode == 1, f"Expected exit 1, got {result.returncode}\nstdout: {result.stdout}"
    assert "(e)" in result.stdout
    assert "vacuous pass" in result.stdout
    assert "uppercase" in result.stdout.lower()


def test_lint_uppercase_step_headings_no_e_fail():
    """(e-b) Correct uppercase '## STEP N' → NO (e) row."""
    result = _run_lint(GOOD_PLAN)
    assert "(e)" not in result.stdout


def test_lint_single_step_diagnostic_no_e_fail():
    """(e-c) Single-step diagnostic (no qa_steps, no step headings) → NO (e) FAIL, NO case WARN, exit 0."""
    plan = """\
# Diagnostic
**Date:** 2026-07-13 | **Dispatch Mode:** bellows | **pause_for_verdict:** always

## Context

Some analysis goes here.
"""
    result = _run_lint(plan)
    assert result.returncode == 0, f"Expected exit 0, got {result.returncode}\nstdout: {result.stdout}"
    assert "(e)" not in result.stdout
    assert "consider using uppercase" not in result.stdout


def test_lint_titlecase_step_no_qa_steps_warns_only():
    """(e-d) No qa_steps, '## Step 1' prose → WARN printed but exit 0."""
    plan = """\
# Diagnostic
**Date:** 2026-07-13 | **Dispatch Mode:** bellows | **pause_for_verdict:** always

## Step 1 — Analysis

> Investigate the issue.
"""
    result = _run_lint(plan)
    assert result.returncode == 0, f"Expected exit 0 (WARN only), got {result.returncode}\nstdout: {result.stdout}"
    assert "WARN" in result.stdout
    assert "uppercase" in result.stdout.lower()
    assert "(e)" not in result.stdout


# --- Drafting Cycle self-check (DRAFTING_CYCLE.md §4) ---

# Compliant T2 fixture — real Drafting Cycle block from executable-270.md
# (governance — Codify the Drafting Cycle), with Cold panel line added.
COMPLIANT_T2_PLAN = """\
# governance — Codify the Drafting Cycle
**Date:** 2026-07-23 | **Dispatch Mode:** bellows | **pause_for_verdict:** always | **cycle_tier:** T2

## Drafting Cycle
**Tier:** T2 — triggers fired: T-6 (governance surface: edits the template + adds a doctrine file), T-8 (novel: first codification of the cycle as a system). Run by the Planner pre-deposit.
**Walks:** 2.
- Weak spots:         w1 1 folded (extraction must be proven complete BEFORE the section is removed); w2 dry.
- Destruction:        w1 1 folded (the shrink deletes ~50 lines of live doctrine incl. `five **named lenses**`); w2 dry.
- Vulnerabilities:    w1 1 folded (3.2 observe-the-effect: QA must confirm the file exists + the pointer resolves + nothing lost); w2 dry.
- Integration-record: w1 dry (RULE_20 / READONLY_AUDIT_CONTRACT precedent — referenced not inlined; CEO-confirmed dedicated file).
- ACID:               w1 1 folded (5.1/5.2: the file write + template edit + staging-file cleanup land atomically); w2 dry.
**Cold panel (T2):** run; 0 material findings.
**Conflicts:** none — the lenses agree (extract carefully, prove nothing lost).
**Closing:** walk 2 dry; last event = lens pass; deposited once.

## CEO Context

The CEO directed tightening the Drafting Cycle.
"""

# Tier-less fixture — real header from executable-265.md (invoice-pulse follow-on scripts).
TIERLESS_PLAN = """\
# invoice-pulse — Scripts channel: 3 follow-on pure-aggregate query scripts (paste_source, email-lookup, source-retention)
**Date:** 2026-07-23 | **Dispatch Mode:** bellows | **pause_for_verdict:** always

## CEO Context

The scripts channel is proven end-to-end.
"""


def test_lint_cycle_compliant_t2_no_warn():
    """(f-a) Compliant T2 plan (real 270 block) → NO drafting-cycle WARN, exit 0."""
    result = _run_lint(COMPLIANT_T2_PLAN)
    assert result.returncode == 0, f"Expected exit 0, got {result.returncode}\nstdout: {result.stdout}"
    assert "cycle_tier" not in result.stdout
    assert "Drafting Cycle" not in result.stdout
    assert "cold-panel" not in result.stdout.lower()
    assert "Closing" not in result.stdout


def test_lint_cycle_t2_missing_cold_panel_warns():
    """(f-h) T2 plan with a full 5-lens block + dry closing but NO cold-panel line → WARN naming cold-panel, exit 0."""
    plan = """\
# Test Plan
**Date:** 2026-07-24 | **Dispatch Mode:** bellows | **pause_for_verdict:** always | **cycle_tier:** T2

## Drafting Cycle
**Tier:** T2 — triggers fired: T-6 (governance surface), T-8 (novel).
**Walks:** 2.
- Weak spots:         w1 dry.
- Destruction:        w1 dry.
- Vulnerabilities:    w1 dry.
- Integration-record: w1 dry.
- ACID:               w1 dry.
**Closing:** walk 1 dry; last event = lens pass; deposited once.
"""
    result = _run_lint(plan)
    assert result.returncode == 0, f"Expected exit 0 (WARN only), got {result.returncode}\nstdout: {result.stdout}"
    # observe-the-effect: the cold-panel WARN actually FIRES (this is the branch under test)
    assert "cold-panel" in result.stdout.lower()
    assert "missing cold-panel" in result.stdout.lower()
    # isolation: the fixture is otherwise-compliant, so NO other (f) WARN fires
    assert "missing lens" not in result.stdout.lower()
    assert "no cycle_tier" not in result.stdout.lower()
    assert "dry lens pass" not in result.stdout.lower()  # no fold-closing WARN


def test_lint_cycle_tierless_warns():
    """(f-b) Tier-less plan (real 265 header) → cycle_tier WARN, exit 0."""
    result = _run_lint(TIERLESS_PLAN)
    assert result.returncode == 0, f"Expected exit 0 (WARN only), got {result.returncode}\nstdout: {result.stdout}"
    assert "no cycle_tier declared" in result.stdout


def test_lint_cycle_t1_missing_acid_warns():
    """(f-c) T1 plan missing ACID lens → WARN naming ACID, exit 0."""
    plan = """\
# Test Plan
**Date:** 2026-07-24 | **Dispatch Mode:** bellows | **pause_for_verdict:** always | **cycle_tier:** T1

## Drafting Cycle
**Tier:** T1 — triggers fired: T-8 (novel).
**Walks:** 1.
- Weak spots:         w1 dry.
- Destruction:        w1 dry.
- Vulnerabilities:    w1 dry.
- Integration-record: w1 dry.
**Closing:** walk 1 dry; last event = lens pass; deposited once.
"""
    result = _run_lint(plan)
    assert result.returncode == 0, f"Expected exit 0 (WARN only), got {result.returncode}\nstdout: {result.stdout}"
    assert "ACID" in result.stdout
    assert "missing lens" in result.stdout.lower()


def test_lint_cycle_t0_no_block_warn():
    """(f-d) T0 plan with just tier declaration → NO block/lens/closing WARN, exit 0."""
    plan = """\
# Test Plan
**Date:** 2026-07-24 | **Dispatch Mode:** bellows | **pause_for_verdict:** always | **cycle_tier:** T0
"""
    result = _run_lint(plan)
    assert result.returncode == 0, f"Expected exit 0, got {result.returncode}\nstdout: {result.stdout}"
    assert "Drafting Cycle" not in result.stdout
    assert "cycle_tier" not in result.stdout
    assert "Closing" not in result.stdout


def test_lint_cycle_fold_closing_warns():
    """(f-e) Plan whose closing line is a fold → WARN about fold, exit 0."""
    plan = """\
# Test Plan
**Date:** 2026-07-24 | **Dispatch Mode:** bellows | **pause_for_verdict:** always | **cycle_tier:** T1

## Drafting Cycle
**Tier:** T1 — triggers fired: T-8 (novel).
**Walks:** 1.
- Weak spots:         w1 1 folded.
- Destruction:        w1 dry.
- Vulnerabilities:    w1 dry.
- Integration-record: w1 dry.
- ACID:               w1 1 folded.
**Closing:** walk 1 1 folded; deposited once.
"""
    result = _run_lint(plan)
    assert result.returncode == 0, f"Expected exit 0 (WARN only), got {result.returncode}\nstdout: {result.stdout}"
    assert "fold" in result.stdout.lower()
    assert "dry lens pass" in result.stdout.lower()


# --- 189/N5: Real-log fixtures (embedded Drafting Cycle blocks from Done plans) ---

REAL_LOG_271 = """\
# bellows — plan_lint §4 self-check
**Date:** 2026-07-24 | **Dispatch Mode:** bellows | **pause_for_verdict:** always | **cycle_tier:** T2

## Drafting Cycle
**Tier:** T2 — triggers fired: T-6 (governance surface: edits a gate, `plan_lint`), T-8 (novel: first implementation of the §4 self-check). Run by the Planner pre-deposit.
**Walks:** 2.
- Weak spots:         w1 1 folded (the closing-line "dry vs fold" parse is fuzzy → keep it lenient; warn-first tolerates a false reminder); w2 dry.
- Destruction:        w1 1 folded (the new WARN must not break existing plan_lint tests that assert output on tier-less plans — DEV updates any, preserving intent, in the SAME step); w2 dry.
- Vulnerabilities:    w1 1 folded (3.2 observe-the-effect: tests must RUN the check on real plan text and assert the WARN actually fires, not just that the function imports; 3.4 degenerate: tier-less / block-less / malformed-block plans must WARN, never crash; read plan files as UTF-8); w2 dry.
- Integration-record: w1 dry (DRAFTING_CYCLE.md §4 is the authority [Rule 27]; the check is an additive sibling to plan_lint's existing (a)-(e) checks, using the same non-blocking WARN mechanism as the test-scope / qa_steps warnings).
- ACID:               w1 dry (stateless lint check; no multi-step schedule).
**Conflicts:** none.
**Cold panel (T2):** NOT separately run — bounded, warn-ONLY change (it can never wrongly block a deposit), and the Step-2 QA agent is an independent cold read of the deliverable. ⚠️ Iteration candidate for DRAFTING_CYCLE.md: a warn-only gate edit may warrant T1, not T2 — noted for a future lesson, not acted on here.
**Closing:** walk 2 dry; last event = lens pass; deposited once.
"""

REAL_LOG_274 = """\
# lessons-forge — Gate 1 batch ingest
**Date:** 2026-07-24 | **Dispatch Mode:** bellows | **pause_for_verdict:** always | **cycle_tier:** T2

## Drafting Cycle
**Tier:** T2 — triggers fired: T-2 (production-data mutation — writes lesson_entries + lesson_proposals to the canonical lessons corpus, which has a documented silent-corruption history [the hash-trap bug], CEO-confirmed 2026-07-24). Also a proven-clone of cycles 257/247 (T-8 does not fire) but T-2 sets the floor at T2.
**Walks:** Walk 1 complete (v0 → v4). Walk 2 complete (v4 → v5): only-minor (WB1 at Lens 1; lenses 2–5 dry) → diminishing returns reached, sequential-walk phase DONE. T2 cold panel next, then §5.
- Weak spots:          w1 → v1: 2 folded (W1 G2 reframed — clean-porcelain is THE gate, HEAD is audit-only; W4 insert_proposal signature corrected — `entry_id` is a required arg, SIX not "four", verified src/lessons_forge.py:202). Verified clean (no fold): W2 parse-split (exactly 4 `## ` headings); W3 target_artifact (unconstrained free TEXT). w2 → v5: 1 minor (WB1 line-11 redundancy from A1 fold-layering consolidated; W4 signature + WB3 Step-1 target-reference re-checked clean).
- Destruction:         w1 dry — clones 257's proven corpus-mutation guards (restore-point `.backup`; G1 non-destructive fresh-run; plan-204 terminal-status guard + G4 hash-trap watch on id 178; ingest-committed-before-classify resume ladder). Verified the W1 G2 reframe did NOT weaken provenance (G4 `updated_count` + G6 work-list catch any content change regardless of HEAD). QA row 7 STRENGTHENED vs 257 (adds DRAFTING_CYCLE.md + plan_lint.py to the unchanged-check). w2 dry (no Walk-1/2 fold relaxed a guard — A1 tightened target-setting, A2 added a concurrency guard, WB1's consolidation verified to drop no substance; corpus safety intact).
- Vulnerabilities:     w1 → v2: 1 minor folded (V1 3.1 — sharpen commit-LESSONS-before-deposit ordering vs the daemon's instant-claim). Verified complete/no-fold: vacuous-git-check discipline (G2 + row 7 use `git -C` root/bellows); guards observe effects not existence (G4/row4/row9 measure actuals); degenerate cases guarded (G4 updated_count, G6 work-list, no-hand-duplicate); no new encoding risk (existing corpus has same char classes). w2 dry (V1 + vacuous-git-check intact; A2 concurrency accurate — daemon serialization already closes the window; no fold introduced a new surface).
- Integration-record:  w1 → v3: 1 minor folded (R1 4.1 — authoring self-check note: plan_lint exit 0 + the benign QA-tests WARN, per 257's convention + the benign-gate memory). Verified: clones 257→258→259 (no-split justified for 4≪12); memories honored (batch-pin append-before-deposit, hash-trap G4, deposit-once, qa-raw-output); §6-aligned (target DRAFTING_CYCLE.md, codify at Gate 2); re-trips nothing (207/204 used not re-litigated); T2 not over-built; premise (DRAFTING_CYCLE.md single-source) holds. w2 dry (R1 plan_lint claim RE-VERIFIED on v5 — exit 0, all PASS, §4 T2-block validates, only the benign QA-tests WARN; the 6 prose folds broke no structural check).
- ACID:                w1 → v4: 2 folded (A1 5.2 — category left open but row 3 requires target set + only governance_rule value specified → lean N5/N6 doc-primary governance_rule/DRAFTING_CYCLE.md, specify instrumentation fallback target='plan_lint.py'; A2 5.3 — between-step window: a concurrent ingest could stale this cycle's non-terminal 'proposed' proposals → concurrency note + row-3 count==4 detection). 5.1 atomicity (ingest-committed-before-classify resume) + 5.4 durability sound. w2 dry (A1 both branches land all-fields-set + schema-valid; A2 clean vs resume/E0-P0; no systemic requirement conflict from the accumulated folds).
**Cold panel (T2):** lens-by-lens, fresh-context reader subagents (each on the prior's folded draft), author-verified.
- Cold weak-spots:      → v6: 2 folded (CB1 `RULE_20_SELF_CHECK_BLOCK.md` bare-named → absolute root path — the cross-tree vacuous-read trap the plan warns about, applied to the block ref; CB2 G6 asymmetric HALT → symmetric ≠4). ⭐ Fresh reader independently RE-VERIFIED the whole numeric/behavioral backbone vs live DB/code (E0/P0, ingested=4, hash-trap live+stable, insert_proposal 6-arg sig, schema CHECK literals, run_full_lessons_cycle behavior) — all confirmed correct.
- Cold destruction:     → v7: 1 folded (CD1 — QA row 4 dropped 257's `if missing, HALT (unverifiable)` fail-closed clause AT AUTHORING; the cold reader diffed v0 vs the 257 clone and caught it — my warm passes compared FOLDS, not the clone source, so missed it). Restored. Verified SAFE vs live: ingest 0 would-UPDATE, G1 0 non-terminal, `.backup` integrity_check ok, classification INSERT-only. Cleared (not a defect): G4's `updated_count==0` is an inferential proxy for stale-count (sound this run — staling shares the `updated_count` branch).
- Cold vulnerabilities: → v8: 4 folded. CV1 (MEDIUM-HIGH) — my own CB2 cold-fold BROKE the resume path: symmetric G6 false-HALTs a legitimate smaller resume work-list → added a run-type resume carve-out mirroring G1/G5 (§2.7: the accommodation broke on its own edge, caught by a cold reader). CV2 (MEDIUM) — `generate_lessons_report` is whole-corpus (date = filename only); accuracy rests on G1 → tightened QA row 5 to verify the report surfaces EXACTLY `entry_id>178` and no others. CV3 — G6 derive `E0+1..E0+4` not literal 179–182 (`sqlite_sequence`-gap safety). CV4 — report write lacks `encoding=` → Forward Register note. CV5 cleared (row-9 LCS is presence-of-quote, can't enforce provenance — inherent; 257 identical). Verified clean: cross-tree vacuous-read surface now fully closed, all 6 refs absolute; hash-trap live; G1 holds; ingested_count==4 sound.
- Cold integration:     → v9: 3 folded. CI1 (MEDIUM) — my A1 fallback mis-paired `instrumentation`+`structure`; specialist taxonomy (FORGE_LESSONS_AGENT.md:67-68) + ADR-002 tree (line 77) says a plan_lint.py code change is `structural`→`structure` (VERIFIED myself) → fixed. CI2 — "257→258→259 ran this shape" over-attributes: only 257 ran the cycle, 258/259 are its Gate 1/Gate 2 → tightened. CI3 — 3rd dropped 257 clause (G5b "re-generate deposits from committed DB") → restored. Confirmed HOLDS: §6/target-override correct (§6:143 "into this file"); CB1/CD1 restorations verified present; all live premises re-verified (E0/P0/G1/hash-trap/get_unclassified empty/6-arg sig); right-sized T2.
- Cold ACID:            → v10: 6 folded. CA1 (MED) G1 resume-exemption was CIRCULAR (deferred on a post-ingest signal but HALTs pre-ingest) → replaced with a pre-ingest entry_id check (baseline non-terminal all `>E0` → resume PASS; any `≤E0` → HALT). CA2 (MED) "classify all 4" vs `get_unclassified` binding → made `get_unclassified` explicitly authoritative (the anti-double-insert mechanism). CA3 (MED) my A2 fold named the WRONG detector (staling is UPDATE not DELETE → `COUNT` monotonic, can't drop) → fixed to QA rows 2+4. CA4 E0/P0 resume fallback to stated constants (deposit absent mid-crash). CA5/CA6 minor resume-symmetry (Step-2 report carve-out; pre-cycle backup id). ⭐ Verified: re-running Step 1 does NOT double-insert (UNIQUE key + dup-guard + get_unclassified). **The resume subsystem is the plan's complex region — the cold panel found 4 distinct gaps there (CV1+CA1+CA2+CA4) → joint coherence re-check owed on the warm confirming walk.**
**Cold panel COMPLETE (16 cold folds total).** Materially changed the draft → warm confirming Walk 3 (below) before §5, then the closing dry pass.
**Walk 3 (warm confirming, on v10+):**
- Weak spots:          → v11: 1 minor (WC1 — G1-vs-G5 run-type label disagreement in the narrow ingested-but-unclassified resume edge; clarified). ⭐ Resume ladder VERIFIED coherent by scenario-tracing (normal resume / fresh / the edge — all gates PASS appropriately, `get_unclassified` prevents double-insert).
- Destruction:         → dry. Cold/CA folds relaxed NO guard: CD1 strengthened (restored fail-closed clause); CA1's G1-resume-permissiveness (PASS on this-cycle's-own `>E0` non-terminal) is BACKSTOPPED by G4 (`updated_count==0` catches any real staling; a resume ingest over unchanged entries is a verified no-op); CA2 strengthened (anti-double-insert); CA3 corrected a wrong detector. Non-destruction holds (G1-permissive + G4-verifies).
- Vulnerabilities:     → dry. Cold CV1-4 + CA resume folds add no new surface: cross-tree paths all absolute (CB1 fix holds, confirmed); CA1's entry_id check HALTs correctly on a mixed/`≤E0` baseline; CA2 handles the resume fewer-than-4 degenerate; CV3 the `sqlite_sequence`-gap; CA4's constant-fallback safe (same-dispatch, verified 178/186); detectors observe effects (CA3 → rows 2/4).
- Integration-record:  → v12: 1 minor (WR1 — CI1 fixed the instruction but QA row 3 under-verified the taxonomy → added the `structural`→`structure` coherence check). Verified: CI1/CI2/CI3 read correctly + align with specialist taxonomy / §6 / 257.
- ACID:                → dry. The 6 CA folds cohere AS A SYSTEM — traced every half-complete state (mid-ingest / ingested-but-0-classified / mid-classify / all-classified-no-deposit / Step-2-report-no-deposit / QA-rerun) → each handled (G1 safety + G5 work-detection + G6 reconciliation + `get_unclassified` authoritative + CA4 E0/P0-fallback + CA5/CA6). No contradictory gate verdicts; invariants consistent; isolation guarded (CA3 rows 2/4); durable (CA4/CA6).
**Closing:** Walk 3 (warm confirming) closed on a dry Lens-5 (ACID) pass — last event is a lens pass, not a fold. Adversarial phase COMPLETE: Walk 1 (6 folds) → Walk 2 (1 minor) → Cold panel (16 folds; backbone independently re-verified by all 5 cold readers) → Walk 3 (2 minor; resume-ladder coherence confirmed). 12 draft revisions. OWED before deposit: §5 mechanical conformance (plan_lint on v12 + Rules/Checklist), then commit LESSONS.md (fills G2's root HEAD), then deposit.
"""

REAL_LOG_275 = """\
# lessons-forge — Gate 1 proposal routing
**Date:** 2026-07-25 | **Dispatch Mode:** bellows | **pause_for_verdict:** always | **cycle_tier:** T2

## Drafting Cycle
**Tier:** T2 — triggers fired: T-2 (production-data mutation — writes the `route` column of the canonical lessons-forge corpus, the same DB with a documented silent-corruption history). Structure-clone of Gate 1 258 (route disposition) + the 274 cycle_tier/block format. (T-8 arguable — route-only is a simplification/subset of 258's route+status, not clearly novel — but IMMATERIAL: T-2 fixes the floor at T2 regardless, and the full cold panel is running.) T-6 does NOT fire — this gate sets DB routing metadata and touches no doctrine file (that is Gate 2).
**Walks:** Walk 1 complete (v0 → v4): 6 folds (W1; V1, V2; R1; A1, A2). Walk 2 (confirming) COMPLETE — all 5 lenses dry (v4 stable). Sequential phase done → T2 cold panel.
- Weak spots:          w1 → v1: 1 folded (W1 1.1/1.2 — Task C(2) + QA row 4 mis-derived the outside-range route-NOT-NULL invariant as `52 = 56−4`; correct is **56, unchanged** — the four targets are route-NULL and already excluded from the 56, so the bad number would false-HALT a clean run). Verified clean (no fold): route delta 56→60 (B3); status-distribution identity (B2); precondition mapping + HALT-on-drift; restore-point + isolation logic. **w2 dry** — re-checked all 6 Walk-1 folds hold + introduced no new weak spot (§2.7); category-assertion judged a defensible drift-canary, not a defect; `Tier: Small` vs `cycle_tier: T2` orthogonal.
- Destruction:         w1 dry — clones 258's proven corpus-mutation guards (restore-point `.backup`; scoped `set_proposal_route` WHERE-id write; precondition HALT-on-route-drift). The one dangerous 258 op (hand-SQL `UPDATE … SET status`) is REMOVED (route-only) → smaller harm surface. (2.1) nothing breaks — route NULL→codify is a forward transition, orthogonal to `get_unclassified` (keys on status). (2.2) no guard relaxed vs 258 — QA row 3's full-distribution identity is a GLOBAL status guard subsuming 258's scoped `id<172` status check; W1 tightened the blast-radius check. (2.3) bounded (4 literal ids) + proven ours (precondition verifies the 274 batch) + fully reversible (restore point + revertible metadata); no reset/delete/rewrite. **w2 dry** — no Walk-1 fold relaxed a guard: W1/V1/A1 STRENGTHENED (correct blast-radius anchor / own-tree src-check / right detectors), A2 additive (concurrency guard), V2 correctly SCOPES the staling check to this gate's delta without harmful relaxation (A0 still verifies the 4 targets clean); no fold added a destructive op.
- Vulnerabilities:     w1 → v2: 2 folded (V1 3.1/3.3 — QA row 7's `git -C <main> status -- src/` is worktree-vacuous → OWN-TREE `git status --porcelain -- src/`, scope_check still primary for committed changes; V2 3.4 — `get_unclassified` hardcoded `[]` → anchored to the A0 before-snapshot [before==after], no false-FAIL on a pre-existing non-quiescent corpus). Verified clean: rest of the cross-tree surface closed (DB absolute, row-6 `git -C root/bellows` non-vacuous, RULE_20 block absolute, backup main-tree absolute); guards observe DB-state effects not non-throw; resume idempotent; no cp1252/interpreter risk (local governance write). **w2 dry** — re-ran V1/V2 on their fixes (§2.7): own-tree src-check holds on in-place + worktree-per-step (committed → scope_check, uncommitted → porcelain); `get_unclassified` is `ORDER BY id` so before==after is order-stable; no fold added a vacuous cross-tree ref (A2's row-refs are internal); degenerate ids doubly guarded (precondition HALT + WHERE-id affects 0 rows).
- Integration-record:  w1 → v3: 1 minor folded (R1 4.1 — authoring self-check now names the benign Step-2 QA-runs-pytest plan_lint WARN [memory `benign-gate-failure-classes`; do NOT add a test file to scope] + runs on the FINAL post-cycle draft; deposit-once strengthened to grep-first). Verified: routing dedup re-confirmed (188/N4 not explicit in §2:38 → codify stands, all four hold); memories honored (predicted-number verify-clauses incl. W1, qa-raw-output, deposits-block); §6-aligned (target DRAFTING_CYCLE.md, codify→Gate 2); re-trips nothing (batch-pin is cycle-only; V2 covers corpus-drift); NOT trivial (T2 right-sized — anti-under-escalation); premises hold + A0 runtime-re-verifies. ⚠️ OWED to cold panel: a line-level clause diff vs `executable-258` — warm passes miss clone-drift (memory `cold-panel-catches-clone-drift`; 274's cold panel found 3 dropped 257 clauses). **w2 dry** — R1's benign-WARN claim accurate (actual plan_lint run correctly deferred to §5 execute-against-real-data); A2 matches 274's note (mine broader: "plan" not just "cycle"); the V1 own-tree src-check is an INTENTIONAL improvement on 258's `-C <main>` (traceable when the cold panel diffs vs 258 — not clone-drift). CARRY to §5: run plan_lint on the final draft, confirm §4 passes + only the benign WARN.
- ACID:                w1 → v4: 2 folded (A1 5.3 — A0 parenthetical cited the WRONG staling detector [said "rows 2+6"; row 6 is doctrine-unchanged] → corrected to rows 2/3/5 [the CA3 class from 274]; A2 5.3 — added the dispatch-time concurrency note [no other lessons plan in flight] mirroring 274, since this gate routes non-terminal `proposed` proposals a concurrent ingest could stale). Sound: 5.1 atomicity (single-commit boundary + idempotent resume), 5.2 consistency (each gap has a stated invariant), 5.4 durability (committed DB + restore point; resume-before is ≤4/before-anchored). **w2 dry** — A1/A2 hold; folds cohere as a system (atomicity intact — all folds are reads/docs, one write-txn unchanged; consistency strengthened; isolation gives complete temporal staling coverage [Task C3 intra-Step1 + row 5 Step1→Step2]; durability intact). Ledger C1 holds; no fold re-violates another; resume coheres. **Walk 2 ALL-DRY → sequential phase done.**
**Cold panel (T2):** lens-by-lens, fresh-context reader subagents (each on the prior's folded draft), author-verified. Carries the R1 line-level clause diff vs `executable-258`.
- Cold weak-spots:      → v5: 1 minor (CB1 — restored 258's dropped "`get_unclassified` is NOT the quiescence signal" clarification, now more relevant since V2 added a get_unclassified ref to A0). ⭐ Fresh reader INDEPENDENTLY re-verified the whole numeric backbone vs live DB — **0 mismatches** (187–190 mapping/status/route/targets; route-NOT-NULL 56→60 [dist NULL 134/codify 49/ref 5/backlog 2]; outside-range 56 unchanged — W1's folded value CONFIRMED correct; distribution 190; `set_proposal_route` no self-commit; `get_unclassified` status-keyed=[]; §4 regex; all DRAFTING_CYCLE.md line refs land). Verified NOT drift: the `id NOT BETWEEN` predicate is a correct improvement on 258's `id<172` (MAX(id)=190, nothing above range).
- Cold destruction:     dry (0 folds) — exhaustive guard-by-guard diff vs 258: every fail-closed/HALT/restore-point/precondition/blast-radius clause PRESERVED (many strengthened) or correctly-dropped-with-its-op (the hand-SQL status guards G6/QA-R3, gone with the status change). Top dropped-guard suspect (258's scoped `status='reference' AND id<172`==6) RESOLVED — R3 full-distribution byte-identity strictly SUBSUMES it (no auto-un-stale path → no compensating pair). Numbers re-verified live AGAIN (0 mismatches; W1's 56-unchanged reconfirmed); `set_proposal_route` scoped+reversible; restore-point fail-closed. ⭐ Discharges the guard-diff half of the R1/258 debt.
- Cold vulnerabilities: → v6: 2 folded, both LOW (CV1 F1 — A0 isolation self-signal's worktree behavior rested on an implicit "marker is main-tree" assumption → made explicit [daemon claims in main `decisions/` before any worktree spin]; kept the fail-closed HALT, did NOT soften it; CV2 F2 — QA row 4's "before-count of 56" is clean-run-only → made dynamic like B3 [56 clean / higher on resume], removing a resume false-FAIL for a literal QA agent — the W1 class). ⭐ Full worktree×resume trace: every path correct in BOTH modes (abs DB / abs backup / abs RULE_20 / `git -C` root+bellows non-vacuous / own-tree src); resume sound at all 3 extremes (0/partial/all-4 pre-routed). Numbers re-verified a 3rd time (0 mismatches); no `from config import`-class isolation bypass (DB via `conn`); no cp1252/path-sep (local ASCII write).
- Cold integration:     → v7: 2 folded (CI1 LOW — 188's dedup/Gate-2 note omitted the NEAREST cumulation clauses §2.7:79 + §2.6:73; added the cross-ref + a "extend-don't-compete" Gate-2 instruction per 258's 178/184 convention [codify still stands: those forbid CONCURRENT lenses, N4 forbids BATCHING one un-folded draft]; CI2 INFO — softened "proven-clone→structure-clone", noted T-8 arguable but immaterial [T-2 sets T2]). ⭐ Convention diff vs 258/274: NO convention mis-copied/dropped (the route-only inversion + QA-row re-map are conscious, correct). **DECISIVE dedup proof:** DRAFTING_CYCLE.md is v1.0 with ZERO amendment rows since extraction → no refinement CAN be pre-codified → all 4 `codify` right, none `reference`. plan_lint couplings verified in code (`:201` fold/dry heuristic [189], `:165` `^T([012])$` [190]); taxonomy coherent; §6 aligned; no re-trip. Numbers confirmed live (4th).
- Cold ACID:            dry (0 material folds) — full system analysis: (5.1) all 5 crash points resumable, no double-apply/false-HALT/false-PASS (single-commit rollback confirmed via sqlite3 default isolation; atomicity is defense-in-depth, not load-bearing — the 4 route writes are independent NULL→codify transitions); (5.3) every isolation window guarded, incl. the lock-impossible verdict-gate window — a `proposed` target staling is TRIPLY detected (rows 2/3/5), independently confirmed VALID (each target entry has exactly 1 proposal → staling makes get_unclassified non-empty); (5.4) durable + reconstructable from the `.backup` diff. ⭐ Fold-coherence: CV2/V2/B3 cohere across all 3 completion extremes (0/partial/all-4 pre-routed); no fold conflict; C1 consistent. ⭐ Consistency UPGRADE: status-identity is GUARANTEED not just stated — `set_proposal_route` writes route only + ZERO triggers on lesson_proposals + no route↔status CHECK coupling (all verified live) → mechanically incapable of moving a status.
**Cold panel COMPLETE — 5 cold folds (CB1, CV1, CV2, CI1, CI2; all minor/low/info).** Independent value delivered: the numeric backbone re-verified 4× (0 mismatches every time), the guard-by-guard diff vs 258 (0 dropped guards), the convention diff (0 dropped conventions), the full worktree×resume trace (sound in both modes, all 3 extremes), and the ACID system analysis (clean). Cold panel materially touched the draft → warm confirming **Walk 3** owed before §5.
**Walk 3 (warm confirming, on v7):**
- Weak spots:          → dry. The 5 cold folds introduce no new weak spot + are internally consistent (CB1 refs V2's A0 before-snapshot item 3; CV2 mirrors B3; CI1/CI2 are routing-rationale/Gate-2-guidance with no Step-1/2 exec logic). Scope↔Deposits match in both steps.
- Destruction:         → dry. No cold fold relaxed a guard: CB1 RESTORED a clause, CV1 KEPT the fail-closed HALT (+reinforced "write nothing"), CV2 removed a false-FAIL without weakening the real guard (row 1 still catches an under-write; `≤4` is resume-tolerance not a hole), CI1/CI2 are documentation. Harm surface unchanged (route-only, scoped, reversible); no cold fold added a destructive op.
- Vulnerabilities:     → dry. CV1 is documentation (worst case if its daemon-order assumption were wrong = a fail-closed HALT, not a hole; the HALT is preserved); CV2's dynamic anchor opens no degenerate edge (a route-removal is caught by outside-range=56; the all-4-pre-routed extreme was verified by cold ACID). Cross-tree surface unchanged by the cold folds (no path touched); the cold Vulnerabilities worktree×resume trace stands.
- Integration-record:  → dry. CI1 accurate (§2.7:79 + §2.6:73 verified present; "extend-don't-compete" matches 258's 178/184 convention; reaffirms codify — 188 distinct from the concurrent-lens clauses) + consistent with the routing; CI2 accurate (T-2→T2 regardless of T-8). All 5 cold folds align with record/memories/§6; routing unchanged, re-confirmed decisively (v1.0 doc, 0 amendments).
- ACID:                → dry. All 11 folds cohere as a system: atomicity/isolation/durability untouched by the cold folds; CB1 is CONSISTENT with A2/row5 (get_unclassified is not the A0 quiescence signal but IS the row-5 before/after staling detector — different roles); CV2/V2/B3 coherence verified by cold ACID; C1 holds. No fold conflict.
**Conflicts:** none (§2.8 ledger: C1 — outside-range route-NOT-NULL count is 56 and must stay unchanged; the four targets were NULL, no −4; C1 re-confirmed consistent by every cold reader).
**Closing:** last event before deposit = the dry M1 confirming pass (a lens pass, not a fold). **Adversarial phase COMPLETE:** Walk 1 (6) → Walk 2 (dry) → cold panel (5; numbers re-verified 4×) → Walk 3 (dry) → §5 (M1) → M1 confirming (dry). **12 folds, 8 revisions (v0→v8).** Ready to deposit once (pending CEO approval); the closing dry lens pass stands.
"""

REAL_LOG_DIAG_276 = """\
# governance — Gate 2 architecture diagnostic
**Date:** 2026-07-25 | **Dispatch Mode:** bellows | **pause_for_verdict:** always | **cycle_tier:** T1

## Drafting Cycle
**Tier:** T1 — triggers fired: **T-7** (authored-from diagnostic — Gate 2's execution plan(s) build on these findings without re-verifying). Supporting: T-1 (reads three subsystems) and T-8 (novel cross-repo doc↔gate scoping) noted; tier is T1 either way. No T-2/T-5/T-6 fires (read-only, reversible, edits no governance surface — it READS the doc, does not change it) → not T2.
**Walks:** Walk 1 complete (v0 → v5): 7 folds (W1, W2; D1; V1; R1; A1, A2). Walk 2 (confirming) complete (v5 → v8): WB1 (minor) + VB1 (real, load-bearing vacuous-read) + A3 (minor) — not fully dry, so a confirming Walk 3 is owed. T1 → no cold panel.
- Weak spots:          w1 → v1: 2 folded (W1 1.4 — Q1 can't experimentally prove S1's cross-repo scope_check safety read-only → made "unknown about S1 ⇒ recommend the conservative split" an explicit decision-driving answer; W2 1.1/1.3 — Q4 said "draft the candidate text", overstepping the Gate-2 SA's authoring role + the 259 "no pre-drafted wording" discipline → Q4 now delivers edit-points + constraints + a NON-FINAL feasibility sketch, SA authors final). Verified clean (1.4): Q2/Q3/Q4/Q5 all answerable from the dev box (code + doc reads); 189's parseable-last-lens format tension already surfaced to Q6(b). w2 → v6: 1 minor (WB1 — extended W2's "diagnostic scopes, SA authors" boundary uniformly across Q2/Q3/Q4 via a Method deliverable-scope note; §2.7 sibling-accommodation). Verified: all 7 folds hold + cohere (V1 paths cover A1's daemon grep; A2 consistent with W2); questions complete (wrap-commit + split-sequencing in Q1c/Q5/Q6d).
- Destruction:         w1 → v2: skip on the diagnostic itself (read-only, touches no behaviour) + 1 folded (D1 — the eventual 189 plan_lint change is a behavioral gate change; required the design to stay warn-first-lenient toward the legacy freeform last-lens format [271/274/275 logs] + test both formats — the 271-W1 lenient-parse principle). Verified surfaced for the eventual plan: append-never-renumber (Q4, preserves lesson citations + 5 lenses), 271 protect-existing-tests (Q3), parameterised-UPDATE + restore-point + doc-before-status order (Q5). **w2 dry** — no fold relaxed a guard: D1/V1/A1 STRENGTHENED (legacy-log lenience / vacuous-read close / claim-2 positive-verify-with-collapse), W1 pushes to the CONSERVATIVE split, rest additive/discipline; harm surface unchanged; diagnostic stays read-only.
- Vulnerabilities:     w1 → v3: 1 folded (V1 3.1/3.4 — VERIFIED the cross-tree structure: governance is part of the ROOT repo [no own .git], watched at `governance/knowledge/decisions`, but DRAFTING_CYCLE.md is at the REPO ROOT not inside governance/; plan_lint/gates/tests are the bellows submodule. v2 mislabeled it "governance root" AND Q4's read-to-re-verify-absence was vacuous-read-exposed → pinned each artifact's absolute path + submodule + made an empty DRAFTING_CYCLE.md read a WRONG-PATH signal not "absent" [Rule 55]; deposit own-tree governance/knowledge/research/). Verified clean: (3.2) N/A read-only; (3.3) DB read is ?mode=ro absolute; (3.4) other questions not vacuous-exposed. w2 → v7: 1 folded (VB1 — A1's daemon-grep [verifying the LOAD-BEARING claim 2] re-introduced V1's vacuous-read trap: a relative grep from the governance tree reads empty → falsely confirms "no plan_lint invocation" → falsely validates the premise; required absolute bellows paths + validate-empty-as-real-read [Rule 55]). The §2.7 recursion — the A1 fold introduced a new read with the same trap V1 closed.
- Integration-record:  w1 → v4: 1 folded (R1 4.1 — Q1 under-used 259: it already PROVES a 2-repo cross pattern [root-doc + lessons-forge-DB, closed clean], so the open increment is narrowly the bellows plan_lint+tests 3rd repo + test run; sharpened Q1 to that + require naming each shape's dispatch project [259=LF/260=gov/271=bellows] + cite scope_check's known basename/ancestor limit). Verified: premises hold (plan_lint authoring-time re-checked; 259/271/260 patterns accurate; READONLY_AUDIT_CONTRACT matches 250/251); §6 route respected; no prior gate2-arch diagnostic to duplicate; W2's "don't pre-draft wording" honored; not trivial; T1 right-sized. **w2 dry** — VB1 aligns with the vacuous-check lesson (proposal 184 / Rule 55, same class as V1); WB1 aligns with §6 + 259's no-pre-draft + Rule 27; §6 route + 259/271/260 precedents intact; Depends-on complete (259 covers status-advancement); no re-trip.
- ACID:                w1 → v5: 2 folded (A1 5.2 — claim 2 [plan_lint authoring-time] is the architecture's LOAD-BEARING premise → require POSITIVE daemon-path verification [grep bellows.py/runner.py/gates.py], collapse-if-daemon-invokes; A2 5.2 minor — LOCATE the "five lenses" count phrase for the Gate 2 verify row, 259 E5 pattern). Sound: 5.1 atomicity (one read-only deposit, resume re-deposits) + 5.4 durability; 5.3 near-empty (single-step read-only — proposal 187/N1-N3's own point). w2 → v8: 1 minor (A3 5.2 — D1's "soft mis-WARN" safety is load-bearing on §4 being warn-first → confirm plan_lint still exits 0 at HEAD, else 189's back-compat becomes HARD). Folds cohere: V1+VB1 same Rule-55 class; VB1 completes A1; WB1 generalizes W2; no conflict. Load-bearing premises now all explicit + verified (claim 2 via A1/VB1; 5-lens count via A2; warn-first via A3).
**Walk 3 (confirming, on v8):**
- Weak spots:          → dry. VB1/A3 hold + cohere (VB1 completes A1's grep; A3 confirms D1's warn-first dependency; V1+VB1 same Rule-55 class); no new weak spot; question set complete + answerable; the Cycle block conforms to the §4 T1 check (5 lens lines, no cold-panel line needed).
- Destruction:         → dry. VB1/A3 both STRENGTHEN verification (vacuous-check close; D1 warn-first dependency explicit) — neither relaxes a guard; harm surface unchanged; diagnostic read-only.
- Vulnerabilities:     → dry. VB1 fully covers the vacuous-read surface — both sites (V1 = DRAFTING_CYCLE.md read; VB1 = daemon grep); swept the OTHER reads (DB ?mode=ro absolute; bellows/LF submodule files + 259/271 pinned absolute; 260 own-tree) — none vacuous-exposed; no new edge.
- Integration-record:  → dry. WB1/VB1/A3 align with the record (§6+259+Rule 27; proposal-184/Rule-55; 271 warn-first); §6 route + 259/271/260 precedents intact; no re-trip; all load-bearing premises carry a verification path.
- ACID:                → dry. All 10 folds cohere (V1+VB1, A1+VB1, D1+A3, W2+WB1 reinforce; no conflict); load-bearing-premise set COMPLETE + each verified (claim 2 A1/VB1; 259 2-repo R1; four-absent V1; 5-lens A2; warn-first A3; doc-before-status Q5); no new soft premise.
**Conflicts:** none (no cross-lens conflict across all walks).
**Closing:** Walk 3 (confirming) closed on a dry ACID (Lens 5) pass — last event a lens pass, not a fold. **Adversarial phase COMPLETE:** Walk 1 (7 folds) → Walk 2 (3 folds incl. the load-bearing VB1) → Walk 3 (dry). **10 folds, 9 revisions (v0→v8).**
"""


def test_lint_cycle_real_log_271_no_fold_warn():
    """(f-f) Real 271 block (bellows, mixed format, w2 dry) → NO fold WARN, exit 0."""
    result = _run_lint(REAL_LOG_271)
    assert result.returncode == 0, f"Expected exit 0, got {result.returncode}\nstdout: {result.stdout}"
    assert "fold as last event" not in result.stdout.lower()


def test_lint_cycle_real_log_274_no_fold_warn():
    """(f-g) Real 274 block (lessons-forge, cold panel, Walk 3 dry ACID) → NO fold WARN, exit 0."""
    result = _run_lint(REAL_LOG_274)
    assert result.returncode == 0, f"Expected exit 0, got {result.returncode}\nstdout: {result.stdout}"
    assert "fold as last event" not in result.stdout.lower()


def test_lint_cycle_real_log_275_no_fold_warn():
    """(f-h) Real 275 block (lessons-forge, Walk 3 dry, M1 confirming) → NO fold WARN, exit 0."""
    result = _run_lint(REAL_LOG_275)
    assert result.returncode == 0, f"Expected exit 0, got {result.returncode}\nstdout: {result.stdout}"
    assert "fold as last event" not in result.stdout.lower()


def test_lint_cycle_real_log_diag_276_no_fold_warn():
    """(f-i) Real diag-276 block (T1, Walk 3 dry ACID) → NO fold WARN, exit 0."""
    result = _run_lint(REAL_LOG_DIAG_276)
    assert result.returncode == 0, f"Expected exit 0, got {result.returncode}\nstdout: {result.stdout}"
    assert "fold as last event" not in result.stdout.lower()


# --- 189/N5: Synthetic dry/fold tests ---

def test_lint_cycle_acid_w3_dry_no_warn():
    """(f-j) ACID last-walk w3 dry → primary reads dry → NO closing WARN, exit 0."""
    plan = """\
# Test Plan
**Date:** 2026-07-24 | **Dispatch Mode:** bellows | **pause_for_verdict:** always | **cycle_tier:** T1

## Drafting Cycle
**Tier:** T1 — triggers fired: T-8 (novel).
**Walks:** 3.
- Weak spots:         w1 1 folded; w2 dry; w3 dry.
- Destruction:        w1 dry; w2 dry; w3 dry.
- Vulnerabilities:    w1 dry; w2 dry; w3 dry.
- Integration-record: w1 dry; w2 dry; w3 dry.
- ACID:               w1 1 folded; w2 dry; w3 dry.
**Closing:** walk 3 dry; last event = lens pass; deposited once.
"""
    result = _run_lint(plan)
    assert result.returncode == 0, f"Expected exit 0, got {result.returncode}\nstdout: {result.stdout}"
    assert "fold as last event" not in result.stdout.lower()


def test_lint_cycle_acid_w1_folded_warns():
    """(f-k) ACID last-walk w1 1 folded + benign closing → primary reads folded → fold WARN fires, exit 0."""
    plan = """\
# Test Plan
**Date:** 2026-07-24 | **Dispatch Mode:** bellows | **pause_for_verdict:** always | **cycle_tier:** T1

## Drafting Cycle
**Tier:** T1 — triggers fired: T-8 (novel).
**Walks:** 1.
- Weak spots:         w1 dry.
- Destruction:        w1 dry.
- Vulnerabilities:    w1 dry.
- Integration-record: w1 dry.
- ACID:               w1 1 folded.
**Closing:** walk 1 complete; deposited once.
"""
    result = _run_lint(plan)
    assert result.returncode == 0, f"Expected exit 0 (WARN only), got {result.returncode}\nstdout: {result.stdout}"
    assert "fold" in result.stdout.lower()
    assert "dry lens pass" in result.stdout.lower()


# --- 189/N5: Legacy fallback test ---

def test_lint_cycle_legacy_no_lens_lines_fold_closing_warns():
    """(f-l) Legacy block with no structured lens lines + fold-closing prose → fallback fires WARN, exit 0."""
    plan = """\
# Test Plan
**Date:** 2026-07-24 | **Dispatch Mode:** bellows | **pause_for_verdict:** always | **cycle_tier:** T1

## Drafting Cycle
**Tier:** T1 — triggers fired: T-8 (novel).
**Walks:** 1.
The lenses were walked informally.
**Closing:** walk 1 ended on a fold; deposited once.
"""
    result = _run_lint(plan)
    assert result.returncode == 0, f"Expected exit 0 (WARN only), got {result.returncode}\nstdout: {result.stdout}"
    assert "fold" in result.stdout.lower()
    assert "dry lens pass" in result.stdout.lower()


# --- 189/N5: Degenerate tests ---

def test_lint_cycle_degenerate_pending_lens_no_crash():
    """(f-m) Lens line with no dry/fold status (e.g. [pending]) → no crash, no false fold-WARN, exit 0."""
    plan = """\
# Test Plan
**Date:** 2026-07-24 | **Dispatch Mode:** bellows | **pause_for_verdict:** always | **cycle_tier:** T1

## Drafting Cycle
**Tier:** T1 — triggers fired: T-8 (novel).
**Walks:** 1.
- Weak spots:         [pending]
- Destruction:        [pending]
- Vulnerabilities:    [pending]
- Integration-record: [pending]
- ACID:               [pending]
**Closing:** walk 1 in progress.
"""
    result = _run_lint(plan)
    assert result.returncode == 0, f"Expected exit 0, got {result.returncode}\nstdout: {result.stdout}"
    assert "Traceback" not in result.stderr
    assert "fold as last event" not in result.stdout.lower()


def test_lint_cycle_degenerate_empty_block_no_crash():
    """(f-n) Empty Drafting Cycle block → no crash, no false fold-WARN, exit 0."""
    plan = """\
# Test Plan
**Date:** 2026-07-24 | **Dispatch Mode:** bellows | **pause_for_verdict:** always | **cycle_tier:** T1

## Drafting Cycle

## CEO Context

The CEO directed this.
"""
    result = _run_lint(plan)
    assert result.returncode == 0, f"Expected exit 0, got {result.returncode}\nstdout: {result.stdout}"
    assert "Traceback" not in result.stderr
    assert "fold as last event" not in result.stdout.lower()


def test_lint_cycle_degenerate_statusless_block_no_crash():
    """(f-o) Drafting Cycle block with no walk-status text → no crash, no false fold-WARN, exit 0."""
    plan = """\
# Test Plan
**Date:** 2026-07-24 | **Dispatch Mode:** bellows | **pause_for_verdict:** always | **cycle_tier:** T1

## Drafting Cycle
**Tier:** T1 — triggers fired: T-8 (novel).
**Walks:** 1.
"""
    result = _run_lint(plan)
    assert result.returncode == 0, f"Expected exit 0, got {result.returncode}\nstdout: {result.stdout}"
    assert "Traceback" not in result.stderr
    assert "fold as last event" not in result.stdout.lower()


# --- 190/N6: T0 collapsed form test ---

def test_lint_cycle_t0_collapsed_form_no_warn():
    """(f-p) T0 plan with collapsed form (§3 format) → NO cycle_tier WARN, exit 0."""
    plan = """\
# Test Plan
**Date:** 2026-07-24 | **Dispatch Mode:** bellows | **pause_for_verdict:** always | **cycle_tier:** T0 (no trigger); integration-vs-record pass: dry.
"""
    result = _run_lint(plan)
    assert result.returncode == 0, f"Expected exit 0, got {result.returncode}\nstdout: {result.stdout}"
    assert "cycle_tier" not in result.stdout
    assert "not recognized" not in result.stdout


# --- Compliant T2 from executable-270 (already in COMPLIANT_T2_PLAN fixture, re-verified) ---

def test_lint_cycle_compliant_t2_real_270_no_warn():
    """(f-q) Compliant real T2 plan (270 block, already in COMPLIANT_T2_PLAN) → NO drafting-cycle WARN, exit 0."""
    result = _run_lint(COMPLIANT_T2_PLAN)
    assert result.returncode == 0, f"Expected exit 0, got {result.returncode}\nstdout: {result.stdout}"
    assert "fold as last event" not in result.stdout.lower()
    assert "cycle_tier" not in result.stdout
    assert "Drafting Cycle" not in result.stdout
