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
    assert "no **closing:**" not in result.stdout.lower()


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



# --- 198 Plan B: Real-log fixtures for plans 277, 278, 284 ---

REAL_LOG_277 = """\
# bellows — plan_lint §4 refinements (189/N5 + 190/N6)
**Date:** 2026-07-30 | **Dispatch Mode:** bellows | **pause_for_verdict:** always | **cycle_tier:** T2

## Drafting Cycle
**Tier:** T2 — triggers fired: T-6 (governance surface — edits the `plan_lint` gate). Structure-clone of 271 (the §4 gate implementation) + authored from diagnostic 276's designs (T-8 does not fire). T-2 does NOT fire (edits code+tests, not data); no daemon coordination (plan_lint is authoring-time, 276-verified).
**Walks:** Walk 1 complete (v0 → v5): 5 folds (W1; D1; V1; R1; A1). Walk 2 (confirming) COMPLETE (v5 → v6): only-minor (WB1); sequential phase done → T2 cold panel.
- Weak spots:          w1 → v1: 1 folded (W1 1.2/1.3 — the 189 parser design [diagnostic's `;`-split "last segment"] assumes a format the REAL logs don't follow [mixed `.`/`→`/`; wN dry`, + cold-panel/Walk-3 multi-lens-line ambiguity]; per WB1 the diagnostic only sketched → Task B now specifies a LENIENT parser [last lens line before Closing via anchored regex incl. `cold`, final-status leniently] + Task D tests on REAL Done-plan blocks [271/274/275/diag-276], not idealized fixtures). Verified clean: Task A 190 regex `\\b` logic sound (matches bare T0/T1/T2 + collapsed T0, rejects T3/T0X); A0 warn-first precondition checkable; Task C fixture edit coherent with the new parser. w2 → v6: 1 minor (WB1 — the 189 regex `weak\\s*spots` missed the hyphenated "Cold weak-spots" cold-panel line → `weak[\\s-]*spots`). Verified: 5 folds hold + cohere (V1's embedded blocks test W1's parser; A1↔DEV edit); Scope↔Deposits match both steps (code files in Scope, dev-log/QA the deposits — 271 pattern).
- Destruction:         w1 → v2: 1 minor folded (D1 2.2 — the 190 `\\b` loosening has a benign side effect: accepts trailing content on ALL tiers [`T2 (governance)` now parses], watering down the old bare-T1/T2 enforcement; documented as intentional [tier still extracted; warn-first; don't over-restrict]). Verified: nothing breaks (2.1 — 190 strictly more permissive, existing T1/T2 parse, malformed T0X/T00/T3 still WARN; 189 strengthening + fallback + real-log tests); existing behaviour guarded (Task C protect-tests, QA rows 6/7/9); 189 doesn't affect T0 (no block check); edits bounded + reversible (Task A0 clean-gate). **w2 dry** — no fold relaxed a guard: WB1 broadens the match (more accurate), V1's embedded blocks preserve real-format coverage, A1 strengthens recovery, D1/R1 documentation; warn-first/protect-existing/no-crash/scope guards intact; harm surface unchanged.
- Vulnerabilities:     w1 → v3: 1 folded (V1 3.1/3.4 — the real-log fixtures span repos [271 bellows / 274,275 LF / diag-276 gov]; a bellows-worktree cross-tree read needs absolute paths + is brittle if plans move → EMBED the real Cycle Log blocks as string literals [self-contained, still proves the parser on real formats]; + a degenerate test [status-less/`[pending]` lens line, empty block → no crash, no false fold-WARN]). Verified clean: (3.2) tests RUN the check on real embedded text (observe-the-effect); (3.1) DRAFTING_CYCLE.md + diagnostic-findings reads use absolute paths (Task A0/reads); (3.3) no cross-repo import binding. **w2 dry** — V1 embedded blocks hold (no cross-tree vacuous risk); WB1's `[\\s-]*` opens no degenerate edge (still anchored by `^-\\s*` + specific keywords); remaining cross-tree reads (doc, findings) absolute; degenerate coverage intact.
- Integration-record:  w1 → v4: 1 folded (R1 4.1 — named the intended doc↔code window: Plan B ships the 189/190 code before Plan A updates §4's text; brief, warn-first-soft, same-intent, closed by Plan A [Depends-on]; diagnostic Q1c/Q6d chose Plan-B-first deliberately). Verified: clones 271 pattern; authors-from diagnostic 276 (Rule 27); §6 doc↔gate satisfied by S2 Depends-on sequencing; no doc/status edit (Plan A owns); Rule 20 M1 form carried from Gate-1 §5; not trivial; T2 right-sized. **w2 dry** — all folds align with the record (W1↔271 observe-the-effect + diagnostic design; D1↔`\\b` choice; V1↔self-contained-test; R1↔§6+Q1c/Q6d; A1↔259/Rule-56; WB1↔real format); §6 satisfied by S2 sequencing; Rule 27 honored; no re-trip.
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
"""

REAL_LOG_278 = """\
# Lessons Forge — Gate 2 Codification (N1–N6 refinements)
**Date:** 2026-07-30 | **Dispatch Mode:** bellows | **pause_for_verdict:** always | **cycle_tier:** T2

## Drafting Cycle
**Tier:** T2 — triggers fired: T-6 (governance surface — edits DRAFTING_CYCLE.md doctrine), T-2 (production-data mutation — flips 187–190 in the LF DB), T-7 (authored-from diagnostic — builds on diag-276's edit map), T-8 (novel — not a byte clone; new edit set).
**Walks:** 3 (2 warm + cold panel + confirming). w1 12 (4+3+2+1+2); w2 5 (2+1+1+1+0); cold 12 (3+2+2+2+3); w3 dry on plan logic (Cycle-Log housekeeping only). Sequential+cold+confirming cycle CLOSED — last event = ACID w3 dry lens pass. ~34 folds total.
- Weak spots:          w1 4 folded (E4 mechanism mismatch [whole-line vs segment, grounded in committed plan_lint.py]; E4/QA-5 committed-code pin; Depends-on-as-prose note; QA-10 proposed>0 diagnosis); w2 2 folded (precision on w1 fold-text: wrap-mismatch "hash reconstructs"→"blueprint reconstructs, hash verifies"; self-conformance "closes with dry"→"contains dry"); w3 dry (plan logic sound — SA→DEV→QA flow, Rule-20 evidence-row mapping, task order, self-conformance all trace clean; cleaned 3 Cycle-Log housekeeping items).
- Destruction:         w1 3 folded (E3 anti-watering-down diff-gate vs :79/:73; :152 in-flight-inherit note; self-conformance recursion — Plan A's own ACID line must close dry). w2 1 folded (pinned E3 gate's (a)/(b) criteria per Rule 57 — E3 confirmed distinct from :79/:73, gate is passable). w3 dry — no fold across the ~29 relaxed a guard (all added or strengthened); E5 optionality is edit-map-ratified; extended the Conflicts ledger to span the full cycle.
- Vulnerabilities:     w1 2 folded (3.1/3.2 UTF-8 + Task-B4 diff-only-intended-hunks [shasum can't catch mojibake in untouched regions]; 3.3 canonical absolute DB path for the flip [gitignored DB + worktree = silent no-op]). w2 1 folded (3.1/3.3 restore-point pinned to a durable main-tree path — a worktree `.backup` is lost on teardown). Verified-holds: `git -C <root>` resolves from any worktree cwd; DEV editing the root doc outside the worktree is the 259 pattern; C0→C has no gate + `AND status='proposed'` atomic guard. w3 dry — no new env/isolation/degenerate vuln from the folds; Rule 20 `evidence_dir` pwd-derived == deposit location (cold-ACID-confirmed); evidence files are governance metadata (no leak, local commit); wrap last-commit re-verify is a clean absolute read.
- Integration-record:  w1 1 folded (CB3/predicted-number: authoring self-check is a verify-clause, not a WARN prediction). Verified-holds: cycle_tier on its own line parses (275 precedent + `_parse_plan_header` docstring — collects consecutive bold lines); 277 in bellows Done/; both deposit dirs exist; SA-query JOIN columns all live in schema; 259 protections all carried; M1/CB1/CI1 session-9 lessons folded (Lenses 1/1/plan). w2 1 folded (⭐ record CORRECTED the Vuln-w2 restore-point guess: 275's proven pattern = `sqlite3 ".backup"` not `cp` [WAL-safe] + `lessons-forge/data/backups/` not `bellows/.bellows-cache/`; gitignored via `*.db`). w3 dry — re-verified load-bearing premises STILL HOLD post-cycle: 187–190 still proposed+codify (count 4); DRAFTING_CYCLE.md still v1.0 (commit 2502159, trailing clause intact, tree clean); nothing in flight. Rule 20 clone faithful to 275; edit-map decisions (S2/fix-i/status/count-pin/load-order) + §6 all honored.
- ACID:                w1 2 folded (clone-drift: restored 259's wrap-mismatch branch [QA→wrap doc-loss window; DB already durable]; Isolation stated — bellows serialization + C0 for DB, A0 commit-pin for doc, nothing-in-flight precondition). Atomicity/Durability verified-holds (load-bearing order + A0 disambiguation + `AND status='proposed'` idempotency + DB backup + committed pre-doc-state + blueprint). w2 dry — folds cohere as a system; restore-point Vuln→Integration was a correction (converged on 275's `.backup` pattern), not oscillation; atomicity/isolation/durability intact + strengthened. w3 dry — ACID-cold F1/F2/F3 cohere; isolation now COMPLETE (F1 closed the concurrent-committed-root-change wrap window); closing state correct (warm ACID line contains "dry" + is the last `^-` lens line before Closing → plan_lint (f) no-WARN, confirmed empirically at §5).
**Conflicts:** none across the full cycle (walks 1–3 + cold panel) — no two lenses' constraints required joint resolution. Both candidate tensions were benign: the restore-point evolution (Vuln→Integration) was a correction from the record, not a ping-pong; and load-order↔wrap-recovery / absolute-path↔own-tree were confirmed COMPLEMENTARY by the cold ACID reader, not conflicting.
**Cold panel (T2):** COMPLETE — 5 cold readers, sequential fresh-context subagents, author-verified; 12 folded (3+2+2+2+3). ⭐ Standout: cold Integration caught the Rule 20 QA step was UNSATISFIABLE (full form mandated, no evidence files → canonical block sys.exit(1) → plan would halt at QA); CEO chose full-form-+-real-evidence. Two clone-drift reversions vs 275 caught (own-tree src-check; and the warm-Walk-2 `.backup`-not-cp). Cold ACID confirmed the whole fold set coheres (no cross-fold conflict; atomicity/consistency/durability guarded not lucky; late Rule 20 fold adds no new hazard).
  - Weak spots (cold): 3 folded — F1 SA query omitted status/route so its "confirm proposed+codify" was unperformable (my 259-adaptation error; added p.status/p.route); F2 QA row 6 had no branch for a permitted E5 omission (added it); F3 E1/E2 "insert item" → clarified inline-append (sub-questions are inline, not bullets). Cold reader independently CONFIRMED: DB-safety chain, E4↔shipped-code (plan_lint HEAD cc0777c), unique anchors, count phrases untouched, cycle_tier parse, gitignored backup.
  - Destruction (cold): 2 folded — ⭐ D-F1 [MEDIUM] M1 whole-line version replacement would DESTROY the ":5 Amended only through the Iteration Protocol (§6)." clause (exists nowhere else; QA-1 + B4 both blind to the within-hunk loss) → surgical date-swap + QA-1 asserts full line; D-F2 2.4 must state the §2.2 skip-condition doesn't apply to diagnostics (edit-map-framed, in 2.4's wording). Cold reader CLEARED the prime suspects: E4 doesn't weaken §2:38's invariant (lives in §2, untouched; plan_lint WARNs cite §2 not §4); E3 distinct from :79/:73; no doc consumer parses the wording at runtime.
  - Vulnerabilities (cold): 2 folded — ⭐ V-F1 [clone-drift] QA row 11 `git -C <main>` src/-check is worktree-VACUOUS (I cloned 259's old form, reverting 275's proven own-tree fix, proposal-184's class) → own-tree `git status --porcelain -- src/`; V-F2 mojibake guard was single-point at DEV-B4 → added QA row 0b independent diff cross-check. Cold reader VERIFIED live: bellows DOES worktree lessons-forge plans (bellows.py:1045), so hardening is load-bearing; DB has no triggers/no status↔route coupling; all cross-repo/DB/backup paths absolute; no false-implemented path exists.
  - Integration (cold): 1 MATERIAL folded (CEO-decided) — ⭐⭐ Rule 20 clone-drift: QA mandated M1's FULL form but supplied no evidence files → the canonical block would sys.exit(1) (unsatisfiable). Verified: enforcement gate needs only banner+PASSED (gates.py); the full block hard-requires evidence_dir + non-empty files (RULE_20_SELF_CHECK_BLOCK.md:66–74,95); 259 [same doc-only class] used the simple banner; 275 used the full form justified by pytest evidence Plan A can't produce. **CEO chose the full form + real evidence** → cloned 275's machinery, evidence set adapted to db-invariants.txt (rows 9–10) + doc-integrity.txt (rows 0/0b/1–8, replacing uncloneable full-suite.txt); own-tree evidence_dir (plan-225), Scope+Deposits+commit-all-three updated. Plus 1 trivial (§2.6 :72→:73). Cleared: Depends-on-prose (correct), DB-isolation-guard (covered), all domain premises HOLD (Plan B shipped, E4↔code, 187–190 proposed, count phrases, self-conformance).
  - ACID (cold): 3 folded (all minor) — F1 wrap adds a prevention-side last-touching-commit re-verify (concurrent committed root change the own-bytes shasum can't see); F2 load-order rationale precision (intra-Step-2 crash vs the transient implemented+uncommitted-doc window — two windows, two guards); F3 extended D-F1's within-hunk preservation to E1/E2 (QA rows 2/3 confirm 2.1–2.3 / 5.1–5.4 survive the inline append). ⭐ CONFIRMED the fold set coheres: load-order↔wrap-recovery complementary, absolute-path↔own-tree = the two halves of E11, DB-flip atomicity + doc↔DB wrap-consistency guarded not lucky, late Rule 20 fold no new hazard.
**Self-conformance (recursion, Destruction w1):** Plan A is T2 and carries this very block, so plan_lint's (f) check runs on Plan A at deposit. It passes iff — all five lens lines present ✓, the `**Cold panel (T2):**` line present ✓, and the **last lens line (ACID) CONTAINS "dry"** (from its closing dry walk) so the whole-line rule (`fold`-token present AND `dry` absent → WARN) does not fire — a line like `w1 2 folded; wN dry` passes because `dry` is present even though `folded` also appears. The closing walk MUST leave ACID dry; verify plan_lint exit 0 on the finalized draft before deposit (§4 authoring self-check).
**Closing:** Walk 3 closed dry (last event = ACID w3 dry lens pass; plan logic dry, only Cycle-Log housekeeping remained). **§5 COMPLETE** — plan_lint on the finalized draft: **exit 0**; the (f) drafting-cycle self-check PASSES (recursion confirmed empirically — cycle_tier T2 parsed, all 5 lens lines found, cold-panel line present, ACID closes "dry", zero (f) WARN); the only WARNs are 3 benign "mentions tests but declares no test scope" (CB3 / `benign-gate-failure-classes` — non-blocking, do NOT add a test file to silence). Checklist-by-scope conformant. **READY TO DEPOSIT** (exactly once, to lessons-forge/knowledge/decisions/).
"""

REAL_LOG_284 = """\
# Lessons Forge — Gate 1 Route Disposition 2026-07-29
**Date:** 2026-07-30 | **Dispatch Mode:** bellows | **pause_for_verdict:** always | **cycle_tier:** T2

## Drafting Cycle

**This section is a RECORD of the drafting cycle, NOT instructions for any step.** Nothing here modifies the steps above. ⚠️ It sits inside the final step's extracted span (`gates.py:449` runs the final step's match to end-of-file with no later step to stop at) — a parsing artifact, not scope. Per §3 "compact" and proposal 197 (which this plan routes), the per-fold narrative is NOT here.

**Tier:** T2 — trigger fired: **T-2** (production-data mutation — writes `route` on 8 canonical proposals). T-6 does NOT fire (routing metadata, no doctrine edit — that is Gate 2). Proven clone of 282, so T-8 does not fire; T-2 sets the floor. The corpus holds a parked non-terminal pair (191/192) this plan must not touch, so the cold panel is not skippable.
**Walks:** v0 → v15. **Walk 1 COMPLETE** (all five lenses folded, 11); cold panel in progress. Destruction run first (entry 186 — aim the walk at the step that MUTATES).
- Weak spots:          w1 3 folded (the derived-id command from Destruction's own fold produces MULTI-LINE GARBAGE on two in-progress matches — found by EXECUTING it, not reading it; and A00 runs BEFORE the isolation check that would catch that, so A00 carries its own single-match HALT. Row 5 asserted a flat "both still proposed", which false-`❌`s a legitimate Gate-2 ship for 191/192 inside the Step-1→Step-2 approval window → directional rule. `set_proposal_route:256` re-verified live, citation accurate).
- Destruction:         w1 3 folded (B3/row-3 asserted a `+8` DELTA that false-FAILs the partial resume A0-pre explicitly tolerates — 282 used "rose by ≤N"; replaced with the resume-invariant IDENTITY total == outside-range + 8; swept BOTH sites. Backup filename hardcoded a guessed plan id the Planner cannot know — now derived from the in-progress filename with a HALT on an empty derivation).
- Vulnerabilities:     w1 2 folded. cold 6 (1 rejected). **confirming 2 folded — NOT dry, both from the PREVIOUS pass's own fold.** (a) Destruction added before-item **(4b)** and anchored three consumers to it, but **never added a Receipt deposit slot for it** — so QA row 5's fail-closed clause ("if the Receipt does not report item (4b), mark `❌`") would have fired on EVERY clean run, false-failing the guard the fold existed to install. Receipt item 4b added; sweep re-verified across all consumers (C4, row 5, row 7 condition (a), the halt-durability before-item list). (b) The 4b block was inserted BEFORE its anchor, so A0-snap enumerated `1, 2, 3, 4b, 4` — out of order, with 4b forward-referencing numbering that came after it. Reordered to `1, 2, 3, 4, 4b`. **Both are the add-the-capture-but-not-the-deposit shape; the guard is only as real as its slot.** **cold 6 folded, 1 REJECTED.** ⚠️ **The worst was found by EXECUTION, not reading:** the `?mode=ro` fallback path leaves a **0-BYTE file** at `$BK`, and because shell state does not persist between agent commands the re-run recomputes `$(date)` into a NEW filename — so an empty corpse and a real backup both match the glob, the corpse has the earlier stamp, and Receipt item 6's "lexicographically-first = PRISTINE, roll back to THIS" rule hands the CEO **an empty file as the sole recovery artefact for a production mutation**. Compounded by a second tension: if recovery is a fresh deposit rather than a re-dispatch, bellows mints a NEW id (`bellows.py:378`), so the `<PLAN_ID>`-scoped glob cannot see the first run's pristine backup at all — the id-scoping hardening and the earliest-stamp rule are each right alone and wrong together. **Both were resolved by selecting PRISTINE on CONTENT** (pre-mutation iff `route IS NULL` on 193-200 reads 8 inside the candidate) — ⚠️ **and that machinery was later TRIMMED by the cold integration lens** on four enumerated premises, because it selected between whole-DB restore candidates the plan forbids using. **The surviving hazard controls are A00's `rm` of the 0-byte corpse and the one-line earlier-stamp rule in item 6.** Noted here so a clone does not hunt for content-probe machinery and re-add it (entry 189: sweep the body for citations the log no longer explains). Also: the plan-file regex accepted only 2 of bellows' FOUR live lifecycle prefixes, so every resume of a **halted** or rate-limit-**parked** step would HALT at the first command reporting the wrong cause; `db-invariants.txt`'s single `PORCELAIN-EXIT=` marker was vacuous for 8 of 9 rows (it comes from an unconditional `echo`) → per-row `ROW-<n>:` markers with a counted assertion; row 5b's helper needed an explicit read-only handle in a declared no-writes step; the shasum pins were truncated with no comparison rule, which would manufacture a `❌` on a clean tree. **REJECTED with evidence:** the reader placed `set_proposal_route` at `:257`; it is at **`:256`** as cited. **The weak-spots fold broke on its own edge, twice, both found by EXECUTION:** it accepted only `in-progress-` (false-HALTs a re-dispatch sitting at `verdict-pending-`), and the two-glob `ls` form fails under zsh, where an unmatched glob errors the WHOLE command — so the ORDINARY single-file case returned empty and HALTed. Replaced with a glob-free `grep -E` match; all four states (in-progress / verdict-pending / two / none) executed at authoring. Also: `set_proposal_route` never checks `rowcount`, so a bad id is a SILENT no-op — B1's read-back is the only effect-observation and is now stated as non-redundant with A0-pre.
- Integration-record:  w1 1 folded (the PLAN_ID/backup-filename apparatus had no stated WHY — nothing in this plan reads the backup back and the Receipt already records its absolute path, so it is a cheap hedge on ONE narrow window [death after backup, before deposit], not a mechanism; bounded and marked do-not-grow, so a clone inherits the reason rather than the machinery — the Rule 56 pattern from 283). Citations re-opened and confirmed: `set_proposal_route:256`, Rule 46 `:1012` ("reject daemon-bug workaround proposals"), Rule 35 `:892`, Checklist #29, and the claim that 282 carries the manual bootstrap block Rule 35 says to omit. Premise re-measured at this pass: 62 / 62 / proposed 10 — unchanged.
- ACID:                w1 2 folded. cold 6. **confirming 2 folded — NOT dry.** (a) IC1's scope fix created an UNDECLARED tension with the rest of Rule 21: its `targeted` clause also says the QA step *"must NOT run the full suite"*, and row 6's `pytest src/` IS the whole module — so targeted and full are the same command and the same 55 tests, and the prohibition is not satisfiable as a distinction here. Declared explicitly, since the alternatives are worse (no regression evidence, or two byte-identical files). **A fix in one clause of a rule left the plan crosswise with another clause of the SAME rule.** (b) Before-item (4b) had no resume anchor — a resume re-reads it live, so a pair already moved by a concurrent actor would be recorded as "before" and C4/row 5 would compare it to itself and PASS, invisible exactly when a resume is happening. Now prefers the prior dispatch's recorded value; severity bounded because this plan cannot itself stale a proposal (`set_proposal_route` writes only `route`) and a concurrent cycle is forbidden. **cold 6 folded, and the HIGH is the one that matters: row 5 BLESSES an event row 7 then FAILS.** Gate 2 *is* codification into the target artifact, and 191 targets `DRAFTING_CYCLE.md` while 192 targets `PLANNER_TEMPLATE.md` — **both pinned by row 7** — so the blessed in-window Gate-2 ship necessarily mismatches two pins while leaving porcelain empty, and row 7 declared that `❌` unadjudicatable and Critical. Identical to the walk-1 row-2 defect, unswept to row 7; a direct CL3 violation. Fixed with one narrow, closed reconciliation (row-5 transition recorded AND the commit identified by `git log`), everything else absolutist. Also: Task C4 kept the flat `proposed`-only assertion the ledger's CL1 amendment retired — and it runs AFTER the commit with no pre-write catch, so a correct run would write, then false-HALT, then fail all nine QA rows; the gitignored backup `.db` was in scope for row 0's "is committed" check, manufacturing a Critical `❌` on a clean run; a resume's A0-snap labelled post-write values "(pre-write)" and invited a drift-halt; the ledger's C1/C2/C3 names collided with Task C's post-trim C2/C3/C4, so a clone applying a ledger line to the like-named check would "fix" a sound guard; and the Cycle Log still advertised the trimmed PRISTINE machinery as live. **Original w1 finding retained:** two fold-interactions no single lens could see. **(1) Row 2 CONTRADICTED row 5:** the weak-spots fold blessed a CEO Gate-2 ship for 191/192 in the Step-1→Step-2 window as `✅`, but that moves two rows `proposed → implemented` and row 2 still asserted the distribution byte-identical — so the plan marked `❌` and `✅` on the same event. Split into (a) a hard assertion over THIS plan's 8 targets and (b) a reconciliation for the rest, quoting row 5 so the two agree. **(2)** B3 and row 3 anchored the total-count identity to a BEFORE value, mixing now with then; made same-instant so one fault produces one failing row and the blast-radius question stays localized — swept BOTH sites.
**Cold panel (T2):** COMPLETE — all 5 lenses run as sequential fresh-context readers, each on the prior's folded draft; every finding author-verified before folding., sequential fresh-context readers; every finding author-verified before folding.
- Cold weak-spots: → v6: 9 folded, **all clone-drift — guards the parent carried that this clone silently dropped.** ⚠️ **The two worst:** (1) Step 1, the MUTATING step, had NO halt-durability clause — 282's "IF YOU HALT AFTER `conn.commit()`, YOU MUST STILL DEPOSIT AND COMMIT" was gone, so a halt at B or C left a mutated corpus with the four before-snapshots existing only in the agent's context and the `Partial — HALTED` receipt value unreachable. (2) Row 7 kept 282's absolutist "this row IS the guard" language while **dropping the `shasum` content pins that make it true for a COMMITTED edit** — the same guard, third consecutive plan, third distinct failure mode (282 had it; 283 weakened it and the cold walk restored it; here the language survived and the mechanism did not). Also: the Step-2 opener contradicted its own halt rule and ignored that `pause_for_verdict: always` means the CEO already authorised the continue; Receipt item (3) had no downstream consumer (new row 5b); "this ONE declared deviation" was false, there were three (now enumerated); no `?mode=ro` fallback in either step (latent false-HALT at task one); the `src/` untouched check and its scope prohibition both dropped; the Step-1 deposit unnamed by path; the restore-point VERIFICATION result never deposited. ⭐ Reader independently re-verified the full backbone — all 8 disposition rows, 62/62, 200 proposals, `set_proposal_route:256` with no rowcount check, 55 tests, and every doctrine citation — plus the three dedup claims and the un-codified-parent flag.
**Conflicts (CL-prefixed throughout, to avoid colliding with Task C's C2/C3/C4 sub-checks — a collision the C1 trim created):**
CL1 — the parked pair 191/192 must survive unchanged on `route` and `target_artifact`, and on `status` EXCEPT a CEO-driven terminal transition, which must be recorded (destruction w1; amended by weak spots w1 for the approval-window case; enforced at BOTH Task C4 and QA row 5 after cold ACID found only row 5 carried it).
CL2 — no assertion may be a delta where a resume can legitimately move the starting point; prefer resume-invariant identities (destruction w1).
CL3 — every cross-row assertion must agree with every other on the SAME event: a check that blesses an outcome obliges its siblings to bless it too (ACID w1; violated twice — row 2 vs row 5, then row 7 vs row 5 — and repaired both times).
**Ledger status at confirming-walk close — re-checked against the instructions as they now stand:** **CL1 SATISFIED** — enforced at BOTH Task C4 and QA row 5, each anchored to before-item (4b), which now has a Receipt slot and a resume preference. **CL2 SATISFIED** — B3 and row 3 are same-instant identities, row 4 anchors to the resume-invariant item (4), and (4b)'s live-re-read residue is closed. **CL3 SATISFIED** — rows 2(b), 4, 5, 5b and 7 now all agree on the blessed in-window Gate-2 ship. ⚠️ **CL1 and CL3 were each found VIOLATED by the plan's own instructions during the cold panel and repaired** — the third consecutive plan in this lineage where the ledger recorded a constraint the instructions did not honour, which is itself the argument for keeping the ledger.
**Closing:** NOT REACHED — walk 1 complete (11 folds); **cold panel COMPLETE, all 5 lenses, +36 folds incl. 2 subtractive trims, with 2 cold findings rejected on evidence.** **Confirming walk COMPLETE — all five lenses run, all five folded (1/1/2/1/2 = 7).** Per §3's Cycle-Log template the last event before deposit must be a lens pass, and the last event is a fold, so §2's closing condition is NOT met. **Cycle totals: 54 folds** — walk 1: 11 · cold panel: 36 (incl. 2 subtractive trims, 2 findings rejected on evidence) · confirming walk: 7. **Not deposit-ready on §2's test; the disposition is the CEO's, on the same fail-closed standard 283 shipped under.**  Per §3's Cycle-Log template (and §2.7's sequential-fold rule) the last event must be a lens pass; the last event is a fold. Not deposit-ready.
"""


# --- 198 Plan B: Real-log regression tests for 277, 278 (dry) and 284 (fold-closing) ---

def test_lint_cycle_real_log_277_no_fold_warn():
    """(f-r) Real 277 block (bellows, T2, Walk 3 dry ACID) → NO fold WARN, exit 0."""
    result = _run_lint(REAL_LOG_277)
    assert result.returncode == 0, f"Expected exit 0, got {result.returncode}\nstdout: {result.stdout}"
    assert "PASS:" in result.stdout
    assert "fold as last event" not in result.stdout.lower()
    assert "missing lens" not in result.stdout.lower()
    assert "no **closing:**" not in result.stdout.lower()
    assert "cold-panel" not in result.stdout.lower()


def test_lint_cycle_real_log_278_no_fold_warn():
    """(f-s) Real 278 block (lessons-forge, T2, Walk 3 dry ACID) → NO fold WARN, exit 0."""
    result = _run_lint(REAL_LOG_278)
    assert result.returncode == 0, f"Expected exit 0, got {result.returncode}\nstdout: {result.stdout}"
    assert "PASS:" in result.stdout
    assert "fold as last event" not in result.stdout.lower()
    assert "missing lens" not in result.stdout.lower()
    assert "no **closing:**" not in result.stdout.lower()
    assert "cold-panel" not in result.stdout.lower()


def test_lint_cycle_real_log_284_fold_warn():
    """(f-t) Real 284 block (lessons-forge, T2, NOT REACHED closing) → fold WARN fires, exit 0."""
    result = _run_lint(REAL_LOG_284)
    assert result.returncode == 0, f"Expected exit 0 (WARN only), got {result.returncode}\nstdout: {result.stdout}"
    assert "PASS:" in result.stdout
    assert "fold" in result.stdout.lower()
    assert "dry lens pass" in result.stdout.lower()
    assert "missing lens" not in result.stdout.lower()
    assert "no **closing:**" not in result.stdout.lower()


# --- 198 Plan B: Negative controls for defects (a), (b), (c), (d) ---

def test_lint_control_a_vuln_last_folded():
    """(f-u) Control (a)+(a×b): Vulnerabilities LAST and folded → fold-WARN fires (pre-fix: NO MATCH on Vulnerabilities)."""
    plan = """\
# Test Plan — control (a)
**Date:** 2026-07-30 | **Dispatch Mode:** bellows | **pause_for_verdict:** always | **cycle_tier:** T1

## Drafting Cycle
**Tier:** T1 — triggers fired: T-8 (novel).
**Walks:** 1.
- Weak spots:         w1 dry.
- Destruction:        w1 dry.
- Integration-record: w1 dry.
- ACID:               w1 dry.
- Vulnerabilities:    w1 1 folded.
**Closing:** walk 1 complete; deposited once.
"""
    result = _run_lint(plan)
    assert result.returncode == 0, f"Expected exit 0 (WARN only), got {result.returncode}\nstdout: {result.stdout}"
    assert "fold" in result.stdout.lower()
    assert "dry lens pass" in result.stdout.lower()
    # Isolation: no other (f) WARN fires
    assert "missing lens" not in result.stdout.lower()
    assert "no cycle_tier" not in result.stdout.lower()
    assert "no **closing:**" not in result.stdout.lower()


def test_lint_control_b_not_dry():
    """(f-v) Control (b): ACID 'NOT dry; folded elsewhere' → fold-WARN fires (pre-fix: substring 'dry' suppresses)."""
    plan = """\
# Test Plan — control (b)
**Date:** 2026-07-30 | **Dispatch Mode:** bellows | **pause_for_verdict:** always | **cycle_tier:** T1

## Drafting Cycle
**Tier:** T1 — triggers fired: T-8 (novel).
**Walks:** 1.
- Weak spots:         w1 dry.
- Destruction:        w1 dry.
- Vulnerabilities:    w1 dry.
- Integration-record: w1 dry.
- ACID:               w1 NOT dry; folded elsewhere.
**Closing:** walk 1 NOT dry; deposited once.
"""
    result = _run_lint(plan)
    assert result.returncode == 0, f"Expected exit 0 (WARN only), got {result.returncode}\nstdout: {result.stdout}"
    assert "fold" in result.stdout.lower()
    assert "dry lens pass" in result.stdout.lower()
    # Isolation: no other (f) WARN fires
    assert "missing lens" not in result.stdout.lower()
    assert "no cycle_tier" not in result.stdout.lower()
    assert "no **closing:**" not in result.stdout.lower()


def test_lint_control_c_no_closing():
    """(f-w) Control (c): all lenses dry, NO Closing line → missing-Closing WARN fires (pre-fix: unreachable)."""
    plan = """\
# Test Plan — control (c)
**Date:** 2026-07-30 | **Dispatch Mode:** bellows | **pause_for_verdict:** always | **cycle_tier:** T1

## Drafting Cycle
**Tier:** T1 — triggers fired: T-8 (novel).
**Walks:** 1.
- Weak spots:         w1 dry.
- Destruction:        w1 dry.
- Vulnerabilities:    w1 dry.
- Integration-record: w1 dry.
- ACID:               w1 dry.
"""
    result = _run_lint(plan)
    assert result.returncode == 0, f"Expected exit 0 (WARN only), got {result.returncode}\nstdout: {result.stdout}"
    assert "no **Closing:**" in result.stdout
    # Isolation: no other (f) WARN fires
    assert "missing lens" not in result.stdout.lower()
    assert "no cycle_tier" not in result.stdout.lower()
    assert "dry lens pass" not in result.stdout.lower()


def test_lint_control_d_cold_panel_prose():
    """(f-x) Control (d): T2 with cold-panel only in Tier-line prose → missing-cold-panel WARN fires (pre-fix: prose satisfies)."""
    plan = """\
# Test Plan — control (d)
**Date:** 2026-07-30 | **Dispatch Mode:** bellows | **pause_for_verdict:** always | **cycle_tier:** T2

## Drafting Cycle
**Tier:** T2 — triggers fired: T-6 (cold panel required).
**Walks:** 1.
- Weak spots:         w1 dry.
- Destruction:        w1 dry.
- Vulnerabilities:    w1 dry.
- Integration-record: w1 dry.
- ACID:               w1 dry.
**Closing:** walk 1 dry; last event = lens pass; deposited once.
"""
    result = _run_lint(plan)
    assert result.returncode == 0, f"Expected exit 0 (WARN only), got {result.returncode}\nstdout: {result.stdout}"
    assert "cold-panel" in result.stdout.lower()
    assert "missing cold-panel" in result.stdout.lower()
    # Isolation: no other (f) WARN fires
    assert "missing lens" not in result.stdout.lower()
    assert "no cycle_tier" not in result.stdout.lower()
    assert "dry lens pass" not in result.stdout.lower()
    assert "no **closing:**" not in result.stdout.lower()


def test_lint_cycle_status_mutual_exclusivity():
    """(f-y) Dry last lens line + fold-prose in Closing → NO fold-WARN (status checks mutually exclusive)."""
    plan = """\
# Test Plan — mutual exclusivity
**Date:** 2026-07-30 | **Dispatch Mode:** bellows | **pause_for_verdict:** always | **cycle_tier:** T1

## Drafting Cycle
**Tier:** T1 — triggers fired: T-8 (novel).
**Walks:** 1.
- Weak spots:         w1 dry.
- Destruction:        w1 dry.
- Vulnerabilities:    w1 dry.
- Integration-record: w1 dry.
- ACID:               w1 dry.
**Closing:** walk 1 ended on a fold; not really dry.
"""
    result = _run_lint(plan)
    assert result.returncode == 0, f"Expected exit 0, got {result.returncode}\nstdout: {result.stdout}"
    # The primary check runs (dry ACID lens line), the legacy fallback does NOT run
    # despite fold-prose in the Closing line
    assert "fold as last event" not in result.stdout.lower()
    assert "dry lens pass" not in result.stdout.lower()


# --- (g) Ledger ordering tests ---

# Negative control: ascending ledger from diagnostic-301 (C16-C25 in order)
ASCENDING_LEDGER_PLAN = """\
# governance — diagnostic
**Date:** 2026-08-06 | **Dispatch Mode:** bellows | **pause_for_verdict:** always | **cycle_tier:** T2

## Drafting Cycle
**Tier:** T2 — self-escalated from T1 by CEO decision.
**Walks:** 3.
- Weak spots:          w1 4 raised; w2 2 raised; w3 1 raised.
- Destruction:         w1 2 raised; w2 dry; w3 1 raised.
- Vulnerabilities:     w1 4 raised; w2 dry; w3 dry.
- Integration-record:  w1 3 raised; w2 3 raised; w3 6 raised.
- ACID:                a1 6 raised; a2 5 raised; a3 5 raised.
**Conflicts:** inherited C1–C15.
- **C16** — every population figure keyed on self-declared provenance is a FLOOR.
- **C17** — a firing question is unanswerable until a candidate wording is named.
- **C18** — a corpus root is enumerated, never reached by indirection.
- **C19** — a gate line is phrased so it cannot match until the condition is true.
- **C20** — every firing figure carries its instrument.
- **C21** — a mandated deposit section is written on the halt path too.
- **C22** — a population taken from an upstream table is re-read row by row.
- **C23** — adding a QUESTION is a fold with its own consumer set.
- **C24** — the Cycle Log is a REGION and is walked like one.
- **C25** — ONE quantity, TWO legitimate opposed values, NO verdicts in the questions.
**Cold panel (T2):** NOT run.
**Closing:** judged stop by CEO direction.
"""


def test_lint_ledger_ascending_no_warn():
    """(g-a) Ascending ledger (diagnostic-301 C16-C25) → NO ledger WARN, exit 0."""
    result = _run_lint(ASCENDING_LEDGER_PLAN)
    assert result.returncode == 0, f"Expected exit 0, got {result.returncode}\nstdout: {result.stdout}"
    assert "ledger out of order" not in result.stdout.lower()


def test_lint_ledger_out_of_order_warns():
    """(g-b) Out-of-order ledger (C3 before C2) → WARN naming C3/C2, exit 0."""
    plan = """\
# Test Plan
**Date:** 2026-08-06 | **Dispatch Mode:** bellows | **pause_for_verdict:** always | **cycle_tier:** T1

## Drafting Cycle
**Tier:** T1 — triggers fired: T-8 (novel).
**Walks:** 1.
- Weak spots:         w1 dry.
- Destruction:        w1 dry.
- Vulnerabilities:    w1 dry.
- Integration-record: w1 dry.
- ACID:               w1 dry.
**Conflicts:**
- **C3** — some constraint.
- **C2** — another constraint.
- **C4** — yet another.
**Closing:** walk 1 dry; last event = lens pass; deposited once.
"""
    result = _run_lint(plan)
    assert result.returncode == 0, f"Expected exit 0 (WARN only), got {result.returncode}\nstdout: {result.stdout}"
    assert "C3" in result.stdout and "C2" in result.stdout
    assert "ledger out of order" in result.stdout.lower()


def test_lint_ledger_no_entries_no_warn():
    """(g-c) No ledger entries → no crash, no false WARN, exit 0."""
    result = _run_lint(COMPLIANT_T2_PLAN)
    assert result.returncode == 0, f"Expected exit 0, got {result.returncode}\nstdout: {result.stdout}"
    assert "ledger out of order" not in result.stdout.lower()


# --- (h) Stale closing disclaimer tests ---

def test_lint_stale_closing_warns():
    """(h-a) Lens lines with walk results + Closing claims no lens has read → WARN, exit 0."""
    plan = """\
# Diagnostic
**Date:** 2026-08-06 | **Dispatch Mode:** bellows | **pause_for_verdict:** always | **cycle_tier:** T1

## Drafting Cycle
**Tier:** T1 — triggers fired: T-7.
**Walks:** 1.
- Weak spots:         w1 2 raised.
- Destruction:        w1 dry.
- Vulnerabilities:    w1 dry.
- Integration-record: w1 dry.
- ACID:               w1 dry.
**Closing:** no lens has read this artifact.
"""
    result = _run_lint(plan)
    assert result.returncode == 0, f"Expected exit 0 (WARN only), got {result.returncode}\nstdout: {result.stdout}"
    assert "no lens has read" in result.stdout.lower()
    assert "lens results are recorded" in result.stdout.lower()


def test_lint_closing_unread_no_results_no_warn():
    """(h-b) Closing claims no lens has read, but lenses are [pending] → no WARN (neither alone)."""
    plan = """\
# Diagnostic
**Date:** 2026-08-06 | **Dispatch Mode:** bellows | **pause_for_verdict:** always | **cycle_tier:** T1

## Drafting Cycle
**Tier:** T1 — triggers fired: T-7.
**Walks:** 0.
- Weak spots:         [pending]
- Destruction:        [pending]
- Vulnerabilities:    [pending]
- Integration-record: [pending]
- ACID:               [pending]
**Closing:** no lens has read this artifact.
"""
    result = _run_lint(plan)
    assert result.returncode == 0, f"Expected exit 0, got {result.returncode}\nstdout: {result.stdout}"
    assert "lens results are recorded" not in result.stdout.lower()


def test_lint_lens_results_normal_closing_no_warn():
    """(h-c) Lens results recorded + normal closing → no WARN (neither alone)."""
    result = _run_lint(ASCENDING_LEDGER_PLAN)
    assert result.returncode == 0, f"Expected exit 0, got {result.returncode}\nstdout: {result.stdout}"
    assert "lens results are recorded" not in result.stdout.lower()


def test_lint_degenerate_empty_block_new_checks_no_crash():
    """(ghi-degen) Empty DC block → no crash, no false WARN from (g)/(h)/(i), exit 0."""
    plan = """\
# Test Plan
**Date:** 2026-08-06 | **Dispatch Mode:** bellows | **pause_for_verdict:** always | **cycle_tier:** T1

## Drafting Cycle

## CEO Context

The CEO directed this.
"""
    result = _run_lint(plan)
    assert result.returncode == 0, f"Expected exit 0, got {result.returncode}\nstdout: {result.stdout}"
    assert "Traceback" not in result.stderr
    assert "ledger out of order" not in result.stdout.lower()
    assert "lens results are recorded" not in result.stdout.lower()
    assert "halt-routing" not in result.stdout


# --- (j) Inherited-premise marker tests ---

def test_lint_j_active_numeric_marker_warns():
    """(j-a) Active inherited marker with numeric id in body prose → WARN naming the line, exit 0."""
    plan = """\
# Test Plan
**Date:** 2026-08-07 | **Dispatch Mode:** bellows | **pause_for_verdict:** always

Some body text.
**[INHERITED FROM 291 — NOT RE-EXECUTED]** This was inherited.
More text.
"""
    result = _run_lint(plan)
    assert result.returncode == 0, f"Expected exit 0, got {result.returncode}\nstdout: {result.stdout}"
    assert "(j) WARN" in result.stdout
    assert "line 5" in result.stdout
    assert "291" in result.stdout


def test_lint_j_code_span_marker_warns():
    """(j-b) Active marker inside an inline code span (298:11 shape) → WARN (code spans NOT excluded), exit 0."""
    plan = """\
# Test Plan
**Date:** 2026-08-07 | **Dispatch Mode:** bellows | **pause_for_verdict:** always

- **`[INHERITED FROM 291 — NOT RE-EXECUTED]`** `291:428` — Gate 2 commits every doctrine edit BEFORE touching the DB. *Reason: it describes a shipped plan’s task ordering, observable only by reading that plan, which is what C4 encodes.*
"""
    result = _run_lint(plan)
    assert result.returncode == 0, f"Expected exit 0, got {result.returncode}\nstdout: {result.stdout}"
    assert "(j) WARN" in result.stdout
    assert "291" in result.stdout


def test_lint_j_compound_id_warns():
    """(j-c) Compound id 289/284 (297:252 shape) → WARN, exit 0."""
    plan = """\
# Test Plan
**Date:** 2026-08-07 | **Dispatch Mode:** bellows | **pause_for_verdict:** always

> ⚠️ **Do NOT inline `$(date …)` between single-quoted parts of the `.backup` argument** — sqlite3 misparses it and writes NO backup. **[INHERITED FROM 289/284 — NOT RE-EXECUTED]** (reproducing it means deliberately issuing a malformed command).
"""
    result = _run_lint(plan)
    assert result.returncode == 0, f"Expected exit 0, got {result.returncode}\nstdout: {result.stdout}"
    assert "(j) WARN" in result.stdout
    assert "289/284" in result.stdout


def test_lint_j_placeholder_no_warn():
    """(j-d) Placeholder forms (<plan>) → no WARN, exit 0."""
    plan = """\
# Test Plan
**Date:** 2026-08-07 | **Dispatch Mode:** bellows | **pause_for_verdict:** always

Template: [INHERITED FROM <plan> — NOT RE-EXECUTED]
"""
    result = _run_lint(plan)
    assert result.returncode == 0, f"Expected exit 0, got {result.returncode}\nstdout: {result.stdout}"
    assert "(j) WARN" not in result.stdout


def test_lint_j_fenced_block_no_warn():
    """(j-e) Numeric-id marker inside a fenced block → no WARN, exit 0."""
    plan = """\
# Test Plan
**Date:** 2026-08-07 | **Dispatch Mode:** bellows | **pause_for_verdict:** always

```
**[INHERITED FROM 291 — NOT RE-EXECUTED]** This is inside a fence.
```
"""
    result = _run_lint(plan)
    assert result.returncode == 0, f"Expected exit 0, got {result.returncode}\nstdout: {result.stdout}"
    assert "(j) WARN" not in result.stdout


def test_lint_j_no_marker_no_warn():
    """(j-f) No inherited marker → no WARN, exit 0."""
    plan = """\
# Test Plan
**Date:** 2026-08-07 | **Dispatch Mode:** bellows | **pause_for_verdict:** always

Just a normal plan with no inherited markers.
"""
    result = _run_lint(plan)
    assert result.returncode == 0, f"Expected exit 0, got {result.returncode}\nstdout: {result.stdout}"
    assert "(j) WARN" not in result.stdout


def test_lint_j_fenced_above_exact_line_number():
    """(j-g) Multi-line fenced block ABOVE a marker → WARN reports exact ORIGINAL line number, exit 0.
    A stripped-text numbering bug would report line 5 instead of line 11."""
    plan = """\
# Test Plan
**Date:** 2026-08-07 | **Dispatch Mode:** bellows | **pause_for_verdict:** always

```
fenced line 1
fenced line 2
fenced line 3
fenced line 4
fenced line 5
```
**[INHERITED FROM 291 — NOT RE-EXECUTED]** After the fence.
"""
    result = _run_lint(plan)
    assert result.returncode == 0, f"Expected exit 0, got {result.returncode}\nstdout: {result.stdout}"
    assert "(j) WARN" in result.stdout
    assert "line 11" in result.stdout
    assert "291" in result.stdout


def test_lint_j_double_marker_two_fires():
    """(j-h) Line with two markers → two distinct WARN fires consumed in order, exit 0."""
    plan = """\
# Test Plan
**Date:** 2026-08-07 | **Dispatch Mode:** bellows | **pause_for_verdict:** always

**[INHERITED FROM 289 — NOT RE-EXECUTED]** first marker **[INHERITED FROM 284 — NOT RE-EXECUTED]** second marker
"""
    result = _run_lint(plan)
    assert result.returncode == 0, f"Expected exit 0, got {result.returncode}\nstdout: {result.stdout}"
    lines = [l for l in result.stdout.splitlines() if "(j) WARN" in l]
    assert len(lines) == 2, f"Expected 2 (j) WARN lines, got {len(lines)}: {lines}"
    assert "289" in lines[0]
    assert "284" in lines[1]
    assert "line 4" in lines[0]
    assert "line 4" in lines[1]


def test_lint_j_unclosed_fence_marker_survives():
    """(j-i) Unclosed fence before marker → marker survives (reuse stripper requires closing
    fence), WARN fires, no crash, exit 0. Errs toward false positive (visible warn on
    malformed plan), the acceptable direction for a WARN."""
    plan = """\
# Test Plan
**Date:** 2026-08-07 | **Dispatch Mode:** bellows | **pause_for_verdict:** always

```
this fence is never closed
**[INHERITED FROM 291 — NOT RE-EXECUTED]** inside unclosed fence
"""
    result = _run_lint(plan)
    assert result.returncode == 0, f"Expected exit 0, got {result.returncode}\nstdout: {result.stdout}"
    assert "Traceback" not in result.stderr
    assert "(j) WARN" in result.stdout
    assert "291" in result.stdout


# --- (k) Clone-claim check tests ---

def test_lint_k_clone_no_newest_warns():
    """(k-a) Clone-framed tier line with no 'newest same-class' anywhere → WARN, exit 0."""
    plan = """\
# Test Plan
**Date:** 2026-08-07 | **Dispatch Mode:** bellows | **pause_for_verdict:** always | **cycle_tier:** T2

## Drafting Cycle
**Tier:** T2 — trigger fired: T-6. Proven clone of 277.
**Cold panel (T2):** run; 0 findings.
**Closing:** walk 1 dry; deposited once.
"""
    result = _run_lint(plan)
    assert result.returncode == 0, f"Expected exit 0, got {result.returncode}\nstdout: {result.stdout}"
    assert "(k) WARN" in result.stdout
    assert "newest same-class" in result.stdout


def test_lint_k_clone_with_newest_no_warn():
    """(k-b) Clone-framed AND naming 'newest same-class' → no WARN, exit 0."""
    plan = """\
# Test Plan
**Date:** 2026-08-07 | **Dispatch Mode:** bellows | **pause_for_verdict:** always | **cycle_tier:** T2

## Drafting Cycle
**Tier:** T2 — trigger fired: T-6. Clone of 277; diffed against 304 (newest same-class).
**Cold panel (T2):** run; 0 findings.
**Closing:** walk 1 dry; deposited once.
"""
    result = _run_lint(plan)
    assert result.returncode == 0, f"Expected exit 0, got {result.returncode}\nstdout: {result.stdout}"
    assert "(k) WARN" not in result.stdout


def test_lint_k_no_clone_no_warn():
    """(k-c) No clone framing on tier line → no WARN, exit 0."""
    plan = """\
# Test Plan
**Date:** 2026-08-07 | **Dispatch Mode:** bellows | **pause_for_verdict:** always | **cycle_tier:** T2

## Drafting Cycle
**Tier:** T2 — trigger fired: T-6 (governance surface), T-8 (novel).
**Cold panel (T2):** run; 0 findings.
**Closing:** walk 1 dry; deposited once.
"""
    result = _run_lint(plan)
    assert result.returncode == 0, f"Expected exit 0, got {result.returncode}\nstdout: {result.stdout}"
    assert "(k) WARN" not in result.stdout


def test_lint_k_clone_in_body_not_tier_line_no_warn():
    """(k-d) Clone literal in body prose but NOT on the tier line → no WARN, exit 0.
    The tier-line-only scope is deliberate — a whole-body scan fires on every plan
    that DISCUSSES clones."""
    plan = """\
# Test Plan
**Date:** 2026-08-07 | **Dispatch Mode:** bellows | **pause_for_verdict:** always | **cycle_tier:** T2

## Drafting Cycle
**Tier:** T2 — trigger fired: T-6 (governance surface), T-8 (novel).
This plan discusses proven clone methodology but is not itself a clone.
**Cold panel (T2):** run; 0 findings.
**Closing:** walk 1 dry; deposited once.
"""
    result = _run_lint(plan)
    assert result.returncode == 0, f"Expected exit 0, got {result.returncode}\nstdout: {result.stdout}"
    assert "(k) WARN" not in result.stdout


# --- (l) Clone-mutation down-tier warn tests ---

def test_lint_l_clone_t2_firing_tier_t1_warns():
    """(l-a) Clone-framed + trigger fired: T-2 + cycle_tier T1 → WARN, exit 0.
    Uses the 289:441 shape with cycle_tier lowered to T1."""
    plan = """\
# Test Plan
**Date:** 2026-08-07 | **Dispatch Mode:** bellows | **pause_for_verdict:** always | **cycle_tier:** T1

## Drafting Cycle
**Tier:** T1 — trigger fired: **T-2** (production-data mutation — writes route on 6 proposals). A proven clone of 282.
- Weak spots: w1 dry.
- Destruction: w1 dry.
- Vulnerabilities: w1 dry.
- Integration-record: w1 dry.
- ACID: w1 dry.
**Closing:** walk 1 dry; deposited once.
"""
    result = _run_lint(plan)
    assert result.returncode == 0, f"Expected exit 0, got {result.returncode}\nstdout: {result.stdout}"
    assert "(l) WARN" in result.stdout
    assert "cold panel" in result.stdout
    assert "cold-panel" not in result.stdout


def test_lint_l_plural_hyphenated_form_warns():
    """(l-b) PLURAL 'triggers fired:' + hyphenated 'proven-clone' + cycle_tier T1 → WARN, exit 0.
    The mandatory cold-reader-3 control: a singular-only or unhyphenated-only
    implementation FAILS this fixture. Uses the 281:190 shape."""
    plan = """\
# Test Plan
**Date:** 2026-08-07 | **Dispatch Mode:** bellows | **pause_for_verdict:** always | **cycle_tier:** T1

## Drafting Cycle
**Tier:** T1 — triggers fired: T-2 (production-data mutation — writes lesson_entries + lesson_proposals to the canonical lessons corpus, which has a documented silent-corruption history [the hash-trap bug], CEO-confirmed class). Also a proven-clone of cycles 274/257/247 (T-8 does not fire) but T-2 sets the floor.
- Weak spots: w1 dry.
- Destruction: w1 dry.
- Vulnerabilities: w1 dry.
- Integration-record: w1 dry.
- ACID: w1 dry.
**Closing:** walk 1 dry; deposited once.
"""
    result = _run_lint(plan)
    assert result.returncode == 0, f"Expected exit 0, got {result.returncode}\nstdout: {result.stdout}"
    assert "(l) WARN" in result.stdout
    assert "cold panel" in result.stdout


def test_lint_l_clone_t2_firing_tier_t2_no_warn():
    """(l-c) Clone-framed + T-2 firing but cycle_tier T2 → no WARN, exit 0."""
    plan = """\
# Test Plan
**Date:** 2026-08-07 | **Dispatch Mode:** bellows | **pause_for_verdict:** always | **cycle_tier:** T2

## Drafting Cycle
**Tier:** T2 — trigger fired: **T-2** (production-data mutation). A proven clone of 282.
**Cold panel (T2):** run; 0 findings.
**Closing:** walk 1 dry; deposited once.
"""
    result = _run_lint(plan)
    assert result.returncode == 0, f"Expected exit 0, got {result.returncode}\nstdout: {result.stdout}"
    assert "(l) WARN" not in result.stdout


def test_lint_l_t2_in_negation_list_no_warn():
    """(l-d) Clone-framed + T-2 in negation list after fired segment (303:154 shape) → no WARN, exit 0."""
    plan = """\
# Test Plan
**Date:** 2026-08-07 | **Dispatch Mode:** bellows | **pause_for_verdict:** always | **cycle_tier:** T1

## Drafting Cycle
**Tier:** T1 — trigger fired: T-6. Clone of 277. T-2, T-3, T-4, T-5 do not fire.
- Weak spots: w1 dry.
- Destruction: w1 dry.
- Vulnerabilities: w1 dry.
- Integration-record: w1 dry.
- ACID: w1 dry.
**Closing:** walk 1 dry; deposited once.
"""
    result = _run_lint(plan)
    assert result.returncode == 0, f"Expected exit 0, got {result.returncode}\nstdout: {result.stdout}"
    assert "(l) WARN" not in result.stdout


def test_lint_l_no_trigger_fired_literal_no_warn():
    """(l-e) Clone-framed tier line with neither 'trigger fired:' nor 'triggers fired:' →
    no WARN, silent skip, exit 0."""
    plan = """\
# Test Plan
**Date:** 2026-08-07 | **Dispatch Mode:** bellows | **pause_for_verdict:** always | **cycle_tier:** T1

## Drafting Cycle
**Tier:** T1 — (T-7 only). Clone of 277.
- Weak spots: w1 dry.
- Destruction: w1 dry.
- Vulnerabilities: w1 dry.
- Integration-record: w1 dry.
- ACID: w1 dry.
**Closing:** walk 1 dry; deposited once.
"""
    result = _run_lint(plan)
    assert result.returncode == 0, f"Expected exit 0, got {result.returncode}\nstdout: {result.stdout}"
    assert "(l) WARN" not in result.stdout


def test_lint_l_t2_firing_not_clone_no_warn():
    """(l-f) T-2 firing but NOT clone-framed → no WARN, exit 0."""
    plan = """\
# Test Plan
**Date:** 2026-08-07 | **Dispatch Mode:** bellows | **pause_for_verdict:** always | **cycle_tier:** T1

## Drafting Cycle
**Tier:** T1 — trigger fired: T-2 (production-data mutation). Novel pattern.
- Weak spots: w1 dry.
- Destruction: w1 dry.
- Vulnerabilities: w1 dry.
- Integration-record: w1 dry.
- ACID: w1 dry.
**Closing:** walk 1 dry; deposited once.
"""
    result = _run_lint(plan)
    assert result.returncode == 0, f"Expected exit 0, got {result.returncode}\nstdout: {result.stdout}"
    assert "(l) WARN" not in result.stdout


def test_lint_l_fenced_tier_line_ignored():
    """(l-g) A **Tier:** line inside a fenced block + a real one outside → real one wins
    (stripped-text scan, first line-start match), exit 0."""
    plan = """\
# Test Plan
**Date:** 2026-08-07 | **Dispatch Mode:** bellows | **pause_for_verdict:** always | **cycle_tier:** T1

```
**Tier:** T1 — trigger fired: T-2 (production-data mutation). Clone of 277.
```

## Drafting Cycle
**Tier:** T1 — trigger fired: T-6. Not a clone.
- Weak spots: w1 dry.
- Destruction: w1 dry.
- Vulnerabilities: w1 dry.
- Integration-record: w1 dry.
- ACID: w1 dry.
**Closing:** walk 1 dry; deposited once.
"""
    result = _run_lint(plan)
    assert result.returncode == 0, f"Expected exit 0, got {result.returncode}\nstdout: {result.stdout}"
    assert "(l) WARN" not in result.stdout
    assert "(k) WARN" not in result.stdout


# --- (j)/(k)/(l) degenerate tests ---

def test_lint_jkl_degenerate_empty_no_crash():
    """(jkl-degen) Minimal plan → no crash, no false WARN from (j)/(k)/(l), exit 0."""
    plan = """\
# Test Plan
**Date:** 2026-08-07 | **Dispatch Mode:** bellows | **pause_for_verdict:** always
"""
    result = _run_lint(plan)
    assert result.returncode == 0, f"Expected exit 0, got {result.returncode}\nstdout: {result.stdout}"
    assert "Traceback" not in result.stderr
    assert "(j) WARN" not in result.stdout
    assert "(k) WARN" not in result.stdout
    assert "(l) WARN" not in result.stdout


# --- Self-fire regression test (j)/(k)/(l) ---

def test_lint_jkl_self_fire_zero_warnings():
    """(jkl-self) Plan 306 own text produces zero (j)/(k)/(l) warnings, exit 0.
    Embedded as a raw string literal at DEV time. The plan file path mutates
    across lifecycle (in-progress to Done); a path read would break after archival."""
    plan = r'''# Executable: three warn-first enforcement checks in plan_lint — (j) inherited-premise, (k) clone-claim, (l) clone-mutation down-tier

**Type:** Executable
**Project:** bellows
**Depends on:** **diagnostic-305** (Done — the enforceability assessment; every mechanism this plan ships was constructed and fire-tested there) and **diagnostic-301** (Done — the C5(b) classification that named the three defect classes). Precedent machinery: **executable-303** (clone origin — shipped `(g)`/`(h)`/`(i)`) and **executable-304** (newest same-class — removed `(i)`; its hardenings are carried, see the provenance section).
**Created:** 2026-08-06
**Author:** Planner
**dispatch_mode:** bellows
**pause_for_verdict:** always
**Priority:** 10
**cycle_tier:** T2

⚠️ **ID NOTE — the deposit filename is decided AT DEPOSIT.** Bellows mints the id from `id_sequence` at claim (`lifecycle.py:199`) and does not parse the filename. **Read `id_sequence` at deposit.**

---

## Why this exists — four CEO decisions, taken together on 2026-08-06, and this plan is their first durable record

The executable re-scoping §1 is **held until enforcement exists** for the three defect classes diag-301 named (clone-drift, subtractive-trim, inherited-premise). Diag-305 measured what is mechanizable; the CEO then lowered the bar to the **detectable surface** and, in one sitting, settled the residual cost together with 305's three open decisions:

| decision | CEO call (2026-08-06) |
|---|---|
| **Residual cost** — the T-2 move removes the panel from the proven-clone/data-mutation class | **(c) warn-prompted panel path.** No new §1 trigger (option C stands). A warn-first lint check surfaces the down-tier at drafting time; the panel arrives via prompted self-escalation. **That check is `(l)` in this plan.** |
| **Decision 1** — inherited-premise | **Ship warn-first.** The marker check — 305 measured it firing on its own case (`289`), 3/1365 corpus fires, all true positives. **That is `(j)`.** |
| **Decision 2** — clone-drift | **Both.** Ship the claim check warn-first (**`(k)`**) AND retain the cold panel as the content verifier — 305 proved the content check is not constructible (282's drift was panel-fixed pre-commit). |
| **Decision 3** — subtractive-trim | **Mechanizable-forward + codify per-phase commits.** No check ships here (no surface — the absence of a check is invisible by definition). The class stays panel-and-instruction; the panel path for its motivating population is `(l)`'s warn. The per-phase-commit codification is a DOCTRINE edit and belongs to the §1 executable, **not** this plan. |

⚠️⚠️ **THE SEQUENCING THIS PLAN SERVES: the hold lifts on mechanisms that are SHIPPED and running — warn-first counts; 305's `/tmp` prototypes do not.** When this plan closes, inherited-premise and clone-drift have shipped surface checks, and subtractive-trim's population keeps a warn-prompted panel path. **The §1 executable is unblocked by THIS plan's close, not by 305's verdict.**

⚠️ **The half-complete state, stated rather than accidental (ACID 5.1):** a halt after Step 1 leaves three WARN-only checks live with their corpus load UNMEASURED — this plan's keys differ from 305's prototypes (numeric-id discrimination, tier-line scope, segment bound), so 305's counts do not transfer. **That state is acceptable ONLY because a warn cannot block anything — and the hold does NOT lift in it. The hold lifts when Step 2's measurement closes, not when the code lands.**

⚠️ **Letter note: `(i)` is retired, not free.** 304 removed `(i)` (halt-routing) after it measured 11 fires / 8 false. Reusing the letter would shadow the record of its failure. **The three new checks are `(j)`, `(k)`, `(l)`.**

---

## Clone provenance — origin AND newest same-class (§2.6 `:75`)

- **Origin: `executable-303`** — the shipped add-checks-to-plan_lint plan. Machinery cloned: the WARN-only mechanical invariant (from 140 via 277), A0 pre-edit cleanliness + warn-first precondition, quoted-anchor insertion, embedded-fixture tests (no cross-tree reads — 277's V1), targeted-tests-only in DEV, Task Q0 re-pin at the DEV→QA gate, per-check corpus sweep with pinned roots and per-root zeros.
- **Newest same-class: `executable-304`** — the remove-`(i)` plan. Hardenings carried, not dropped:
  1. **The sweep-diff proof, not a warning count** — any corpus-sweep comparison must diff sweep OUTPUT lines, because a count cannot see one check's line silently lost while another's changed (§2.7: assert the PRESENCE of retained material).
  2. **`(i)`'s lesson as a design bound:** a check requiring entity extraction from prose fails; narrowing to a mechanical token moves the boundary rather than solving it. **Every check in this plan is keyed to a fixed literal or a declared field — none extracts entities from free prose.** Where a check's key is a declared framing (see `(k)`, `(l)`), the check is declaration-keyed and its under-declaration floor is stated in the code comment, exactly as 301's census instrument was.

---

## What each check is — and, per the polarity rule, what it cannot see

**All three are WARN-only advisory (the 140/277/303 invariant): bare `print(...)`, never touch `results`, never set `all_passed`, never raise; malformed or absent input skips silently with a comment saying why.** ⚠️ **Every WARN line BEGINS with its check letter — the canonical composed form is `(j) WARN: <message>` (cold reader 5: stated once so the quoted WARN texts below, which are the `<message>` part, are not copied letterless) — UNLIKE the existing checks' bare `WARN:` prints, DELIBERATELY (cold reader 4 corrected the earlier "matching" claim: no existing WARN carries a letter): the sweep-diff and the per-check attribution key on that letter, not on message-substring guessing (cold reader 3). Do not "conform" the letter away to match the older style.** ⚠️ **The self-fire regression test embeds this plan's text as a RAW string literal delimited by THREE SINGLE QUOTES (apostrophes) — the delimiter is deliberately spelled in words, not glyphs (cold reader 5): an EARLIER version of this body carried the double-quote triple as a glyph — inside this very mandate — and the embed would have terminated early (a SyntaxError); spelling either triple here re-plants the bomb. ⚠️ **The occurrence count is a MOVING property of the text (the confirming pass measured both triples at ZERO after this rewording — the claim "exactly once" died with the glyph it counted): COUNT both triples in the plan text AT DEV TIME and use a delimiter with zero occurrences;** embed byte-exact — never escape or drop content to fit a delimiter (that silently alters the text C4's fidelity depends on). The raw form is required because the body carries regex fragments that are invalid escapes in a non-raw literal on Python 3.12+ (cold reader 3).**

### (j) Inherited-premise marker (Decision 1)

**Key — corrected at walk 1 against the three true-positive files, which broke the v0 spec twice:**

```
[INHERITED FROM <id> — NOT RE-EXECUTED]   where <id> is NUMERIC (digits, optionally
                                          slash-compound like 289/284), outside
                                          FENCED code blocks only.
```

- **A NUMERIC id is REQUIRED to fire.** The convention-declaration and template forms use `<plan>` or `…` placeholders (`289:15`, `297:116`, `298:8`, diag-305's fire-test table) — no digits, never fire. **This, not table-row detection, is the mechanical discrimination.**
- ⚠️ **Inline code spans are NOT excluded — measured: `298`'s five ACTIVE markers (`298:11`–`:15`) are backtick-wrapped.** A code-span exclusion silently kills a true-positive file (one of 305's three).
- ⚠️ **Compound ids fire — measured: `297:252` carries `289/284`.** The id pattern must accept `\d+(/\d+)*`.
- ⚠️ **Accepted, documented per-LINE false positive:** a retraction narrating a marker verbatim with a real id (`289:134`) fires at line level. Per FILE the result stays a true positive (289's active markers at `:169` are real). **State this FP class in the code comment; do not add semantic retraction detection — that is `(i)`'s entity-extraction trap.**

**WARN:** name each firing line number and the plan id(s) it inherits from. ⚠️ **Line numbers are computed against the ORIGINAL text, not the stripped text — cold reader 1 measured a 6-line offset on this very draft after fence removal.** Detect on the stripped text, then re-locate each fired marker in the original, **consuming original lines IN ORDER (cold reader 2: `289:169` carries the marker TWICE — an unordered fragment-search attributes every fire to every matching line).**
**Cannot see:** whether the re-run was actually priced. **The check flags the SITE; the panel judges the quality** — 305's Construction B proved cost-keyword proximity produces false negatives and is NOT attempted here.
**Measured basis (305, cited not re-derived):** fires on `289` (its own case); 3/1365 corpus-wide at 305's pin, all true positives. ⚠️ **The QA sweep MEASURES the count fresh at its own pin — 305's figure is context, never the expected value** (a predicted number invites the run to be read as confirming it).

### (k) Clone-claim check (Decision 2)

**Key:** declaration-keyed, two literals — the plan declares clone framing **on its Cycle Log tier line ONLY (the line beginning `**Tier:**`)** — the line contains `proven clone` / **`proven-clone`** (⚠️ **hyphenated form added at cold reader 3: `281:190` writes "proven-clone of cycles 274/257/247" and `288`/`296` write "A proven-clone framing" — the unhyphenated-only set missed all three**) or `Clone of` / `structure-clone` / `clone of`, all case-insensitive — **and** the plan text nowhere names a newest-same-class comparison (**literal `newest same-class`, matched CASE-INSENSITIVELY — cold reader 3: `284:11` writes "the NEWEST same-class plan", and the casing decides whether 284 fires falsely; it does name its comparison**). ⚠️ **Both `(k)` and `(l)` scan the STRIPPED text (same stripper as `(j)`) and take the FIRST line-start `**Tier:**` match — a fenced tier-line quote must not match, and multiplicity is settled by rule, not accident (cold reader 3; zero multi-tier-line files exist today, which is exactly why the ambiguity would ship invisibly).** ⚠️ **The tier-line-only scope was settled at ACID: "tier line or header" was under-specified (which header?), and a whole-body scan fires on every plan that DISCUSSES clones (301, 305, this one). Verified against every measured declaration site: `282:213` ("Clone of"), `289:441` ("proven clone"), `303:154` ("structure-for-structure clone") — all on the tier line.** `(l)`'s clone-framing test inherits this same scope. **Measured against the live formats at walk 1:** `282`'s tier line reads *"Clone of **275** … diffed against **281** (newest same-class)"* → correctly no WARN; `303`'s reads *"structure-for-structure clone of 277"* and names its *"newest same-class"* → correctly no WARN.
⚠️ **Documented false-NEGATIVE directions (three, all accepted for the same reason — no entity extraction):** **(1)** the literal `newest same-class` appearing in DISCUSSION text suppresses the fire (305 measured this on its own text); **(2)** a tier line without a clone literal skips even when the plan IS a clone that never declared; **(3)** **a plan declaring provenance only in a dedicated section off the tier line (the `289:11` "Clone lineage" paragraph shape, found at cold reader 1) is invisible to `(k)` and `(l)`.** A claim check keyed on declared literals cannot see undeclared or elsewhere-declared framing; each miss errs toward silence, the acceptable direction for a WARN. **The canonical declaration site is the tier line — this plan's own tier line declares there, per its own rule.**
**WARN:** "clone-framed plan does not name its newest same-class comparison (§2.6 `:75`)".
**Cannot see:** whether the diff was actually performed (a claim, not the work — 305 E4), nor which plan IS the newest same-class (semantic classification no gate performs). **The panel remains the content verifier by CEO decision.**
**Measured basis — CORRECTED at cold reader 2, RE-MEASURED at the reader-3 culmination under the FINAL key (stripped text, tier-line-only, case-insensitive suppressor, full literal set):** **8 fires — `274`, `275`, `277`, `285` (4, clearly predating the instruction), `286`/`287` (same-day boundary — `287` IS the codification plan), and `291` + `diagnostic-301` (2, POSTDATING it).** `284`, `288`, `296` are correctly suppressed (each names its comparison, variously cased). ⚠️⚠️ **THE INSTRUCTION DATE, CORRECTED AT COLD READER 4 BY RE-EXECUTION: the newest-same-class discipline entered doctrine at v1.2, 2026-07-30 (commit `3c327e3` — the COMMIT message names plan 287, "[287] Step 2: codify…"; the changelog row itself names proposal 191, not 287 — attribution corrected at cold reader 5) — NOT "2026-08-03 / v1.4", which was 305's claim, inherited here unexecuted. An inherited-premise error in the plan shipping the inherited-premise check, caught cold and priced exactly as §2.7 `:90` demands: the re-run was one `git log -S`.** ⚠️ **Each key revision moved this number (19 → 10 → 8): the count is a property of the KEY, not the corpus — QA measures fresh at its own pin with the shipped key and reports any difference from this figure.** ⚠️ **The v1 claim "all fires predate the instruction" was 305's whole-body prototype figure and is FALSE for this key — do not carry it into the code comment.** **QA reports the fresh count with the date split measured, presuming neither.** ⚠️ **A fourth documented direction (cold reader 2): the canonical tier-line format ITSELF places clone literals on tier lines inside T-8-does-not-fire rationales** (301:138's shape) — such fires are REPORTABLE, their §2.6 applicability is ambiguous (305 flagged the diagnostic-cloning-methodology question), and **weighing them is the CEO's, not the check's or the QA agent's.**

### (l) Clone-mutation down-tier warn (Residual cost, option (c))

**Key:** declaration-keyed, three fields all in the file under test — the plan declares clone framing (as in `(k)`), its Cycle Log tier line records `T-2` as FIRING, and its declared `cycle_tier` is below T2.

⚠️⚠️ **THE FIRING TEST IS SEGMENT-BOUNDED, NOT LINE-CONTAINS — corrected at walk 1, RE-CORRECTED at cold reader 3.** Tier lines carry NEGATIONS on the same line: `289:441` says *"T-6 does NOT fire"* mid-line, and `303:154` ends *"T-2, T-3, T-4, T-5 do not fire"* — a negation LIST that defeats token-level negation matching. **The mechanical bound:** on the tier line, `T-2` counts as firing **iff it appears in the segment immediately after the literal `trigger fired:` OR `triggers fired:` and before the first `.` or `(`.**
⚠️⚠️ **BOTH FORMS ARE MANDATORY — the PLURAL is the MAJORITY format (cold reader 3: 19 vs 10 files containing each literal anywhere; cold reader 4 re-instrumented on first-tier-line-only — the scope `(l)` actually scans — 17 vs 10; the majority claim holds under both instruments), and 7 of the 11 T-2-firing clone-framed Done plans use it — including `281:190` (*"triggers fired: T-2 (production-data mutation …"*), THE MOTIVATING PLAN OF THIS ARC.** ⚠️ **Walk 1's "verified against every measured format" rested on a three-site sample (282/289/303) that was all-singular by accident — the singular-only key would have missed `281` itself.** Verified firing: `289:441`, `282:213` (singular), `281:190` (plural); not firing: `303:154`.
⚠️ **Documented under-match floor:** a tier line with NEITHER form (some diagnostics use *"(T-7 only)"* parentheticals) skips silently, with a code comment saying so.
**WARN:** "clone-framed plan firing T-2 declares tier < T2 — §2.6: clone framing is not licence to down-tier; consider self-escalation to the cold panel". ⚠️ **The WARN text spells `cold panel` UNHYPHENATED, as written here — three existing tests assert `"cold-panel" not in stdout` and a hyphenated spelling breaks them (cold reader 2). Forewarning for Task D: the four embedded real-log fixtures (274/275/277/284) will newly print `(k)` WARNs during EXISTING tests — stdout noise on untouched tests, not failures (49/49 measured passing); do not edit real Done-plan fixture text to silence it.**
**Cannot see:** actual mutation behaviour (only the declared trigger), and it is inert on plans that under-declare T-2. **This is the warn-prompted panel path the CEO chose over scoping the §1 executable — it surfaces the down-tier; it does not force the panel.**
⚠️ **Sequencing note:** `(l)` only has a population to fire on AFTER the §1 executable moves T-2 into T1 (today a T-2-firing plan computes T2 and the tier comparison never triggers). **Shipping it now, inert, is deliberate: the guard must exist before the population does.** The QA sweep on today's corpus is expected to show its mechanical soundness, not fires — **and a zero must be reported as a zero with the reason, never silently.**
⚠️ **Dependency on the §1 executable, stated so it cannot be silently broken:** `(l)`'s key reads the trigger-recording convention (§1: *"Record the tier and the firing trigger(s) in the Cycle Log"*). The re-scope moves T-2 between lists but does not touch that convention — **the §1 executable must not drop it, and SHOULD consider standardizing a machine-readable fired-list format (305's E4 recommendation), which would let `(l)` shed the segment-bound heuristic. That option is ROUTED to the §1 executable's drafting; this plan does not decide it.**

---

## How to Run This Plan

**Bootstrap prompt:**
```
Read the plan at knowledge/decisions/in-progress-executable-<id>.md (the daemon renames the deposited placeholder on claim). Execute Step 1 ONLY. After completing Step 1, STOP and wait for my confirmation.
```

---
---

## STEP 1 — DEV

> **FIRST — post a short visible chat message (1–2 sentences) confirming you are starting this plan and your immediate next action.** Do NOT rename this plan file. Read your Bellows Developer specialist file, then `scripts/plan_lint.py` (the `(f)`/`(g)`/`(h)` blocks and the WARN mechanism), and — for the authoritative behaviour — `/Users/marklehn/Developer/GitHub/DRAFTING_CYCLE.md` §2.6/§2.7 (ABSOLUTE path; repo root, outside this worktree). **All commands run from `/Users/marklehn/Developer/GitHub/bellows`.** ⚠️ **Worktree note (cold reader 5):** the daemon executes each step inside a worktree overlay of this repo; "the bellows tree" in this plan means the tree the step runs in — relative paths resolve against it, edits land on main at step-end teardown (bellows.py:757–760), and 303/304 ran clean under the identical sentence.
>
> **Task A0 — pre-edit cleanliness + warn-first precondition (303/277).** `git -C /Users/marklehn/Developer/GitHub/bellows status --porcelain -- scripts/plan_lint.py tests/test_plan_lint.py` must be empty. **If DIRTY — resume disambiguation (Rule 56):** ⚠️⚠️ **enumerate the hunks first — `git diff -- scripts/plan_lint.py tests/test_plan_lint.py` — and attribute EVERY hunk to this plan's own edits (the `(j)`/`(k)`/`(l)` check comments, the new test names). A presence-grep is NOT sufficient — it proves this plan's edits are IN the dirty files, not that nothing else is (cold reader 2), and `git restore` destroys every uncommitted hunk including a coexisting foreign one.** All hunks attributable → `git restore` both files and reapply from scratch (**NEVER hand-patch a partial apply**). Any unattributable hunk → **HALT, do NOT restore.**
> ⚠️⚠️ **Then confirm HEAD is 304's state:** `(i)` must be ABSENT from `plan_lint.py` — `grep -F "halt-routing" scripts/plan_lint.py` prints nothing and exits 1 (⚠️ **run the grep BARE, never through a pipe — `$?` after a pipe reports the LAST command's exit, which this session measured reading `head`'s 0 as grep's answer**; pair it with a positive control such as `grep -F "(g)" scripts/plan_lint.py` printing the `(g)` comment) — and every `(f)`/`(g)`/`(h)` WARN must be a bare `print(...)` never touching `results`/`all_passed`, return `0 if all_passed else 1`. **Record the hash of this verified state — expected `8e085fa`, but READ it, do not trust this figure — as `PRE_EDIT_HASH` in the dev log; Step 2's sweep-diff keys on it.** **If `(i)` is present or any check has flipped to blocking, HALT and report — the premise of this plan's anchors has moved.**
>
> **Anchor — the insertion point is quoted, not described (Rule 23(a) — ⚠️ cold reader 4: the origin 303:66 cites "Rule 22(a)" for this discipline, a mis-citation this clone initially reproduced; 22 is the Planner's deposited-file check).** The three checks go **immediately after the `(h)` block, before the results-printing loop.** ⚠️ **Read the file and locate the verbatim line that currently ends `(h)`; insert after it. Grep-confirm the edit landed and that no duplicate check label was introduced.** ⚠️ **Placement note:** `(g)`/`(h)` operate inside the `(f)` `dc_block` scope; **`(j)` and `(k)` read the WHOLE plan text and `(l)` reads plan text + the Cycle Log tier/trigger lines — put them at the correct scope level, not inside the `dc_block` conditional**, and say in the code comment why the scope differs from `(g)`/`(h)`.
>
> **Implement `(j)`, `(k)`, `(l)` exactly as specified in `## What each check is` above — including each check's fenced-block exclusion, declaration keys, skip conditions, and code comments stating what the check cannot see.** For fenced-block stripping, reuse or factor the existing stripping the file already performs if present; do not build a second parser beside an existing one.
>
> **Task D — PROTECT THE EXISTING TESTS (303 Task D).** Grep `tests/test_plan_lint.py` for the existing `(f)`/`(g)`/`(h)` tests and **run them before and after the edit.** ⚠️ **If any changes behaviour, preserve the test's INTENT rather than weakening the new check** — make the fixture internally consistent and report every fixture edit explicitly. **Do NOT weaken a check to avoid a test edit.**
>
> **Task E — new observe-the-effect tests, one positive and one negative control per check, each also asserting exit 0.**
> ⚠️⚠️ **EMBED FIXTURES AS STRING LITERALS. DO NOT READ PLANS CROSS-TREE** (277's V1; 303 carried it; carried again here). **The (j)/(l) fixtures encode walk 1's measured formats — the REAL lines are embedded VERBATIM in the COLUMN-0 fenced block below; copy them from here into the test strings rather than inventing shapes or reading cross-tree.** ⚠️ **The fence sits at COLUMN 0, outside this blockquote, DELIBERATELY: cold reader 1 measured that the reuse stripper (`gates.strip_fenced_code_blocks`) only strips column-0 fences — a blockquoted fence is INVISIBLE to it, and the self-fire guard fails.** **A fold moving this block back into the quote re-breaks the guard.**

```
298:11  - **`[INHERITED FROM 291 — NOT RE-EXECUTED]`** `291:428` — Gate 2 commits every doctrine edit BEFORE touching the DB. *Reason: it describes a shipped plan's task ordering, observable only by reading that plan, which is what C4 encodes.*
297:252 > ⚠️ **Do NOT inline `$(date …)` between single-quoted parts of the `.backup` argument** — sqlite3 misparses it and writes NO backup. **[INHERITED FROM 289/284 — NOT RE-EXECUTED]** (reproducing it means deliberately issuing a malformed command).
289:441 **Tier:** T2 — trigger fired: **T-2** (production-data mutation — writes `route` on 6 canonical proposals). T-6 does NOT fire (routing metadata, no doctrine edit — that is Gate 2). **T-8 does not fire on novelty**, but the tier is NOT reduced on clone provenance: a proven clone is where cold-panel value is highest, and this clone deletes an entire subsystem of its parent, which is the highest-risk edit a clone can make.
282:213 **Tier:** T2 — trigger fired: **T-2** (production-data mutation — writes `route` on the canonical lessons-forge corpus). T-6 does NOT fire (DB routing metadata, no doctrine edit — that is Gate 2). Clone of **275** (prior Gate 1); machinery additionally diffed against **281** (newest same-class), per the discipline proposal 191 routes.
303:154 (tail) T-2, T-3, T-4, T-5 do not fire.
281:190 **Tier:** T2 — triggers fired: T-2 (production-data mutation — writes lesson_entries + lesson_proposals to the canonical lessons corpus, which has a documented silent-corruption history [the hash-trap bug], CEO-confirmed class). Also a proven-clone of cycles 274/257/247 (T-8 does not fire) but T-2 sets the floor at T2. Down-tiering a 2-entry batch to skip the cold panel is precisely the trap entry (a) of THIS batch names — so T2 stands.
```

⚠️⚠️ **`281:190` is the MANDATORY plural + hyphenated positive control (cold reader 3): PLURAL `triggers fired:` and hyphenated `proven-clone` — the majority formats a singular/unhyphenated-only key silently misses, on the arc's own motivating plan.**

> ⚠️ **`303:154`'s head reads, verbatim: *"**Tier:** T2 — **computed, trigger fired: T-6.**"* (cold reader 5 repaired this pointer — an earlier version cited a quote "in the `(l)` spec above" that folding had removed, and dropped the word "computed"). The embedded tail is the negation-list shape. If a fixture needs the full line, read it ONCE from `knowledge/decisions/Done/executable-303.md` (**worktree-relative — the same tree the step runs in; cold reader 3 caught the earlier `bellows/…`-prefixed form resolving nowhere from the stated cwd**).**
> ⚠️⚠️ **STRIP THE `NNN:LLL ` CITATION PREFIX when copying a line into a fixture (cold reader 2).** The prefixes above are labels, not content: a verbatim copy does not begin `**Tier:**`, the line-start anchor never matches, and the positive controls fail. **The WRONG response to that failure is loosening the anchor to a contains-match — which then fires on any plan QUOTING a tier line and breaks C4. The anchor stays line-start; fix the fixture, not the scope.**
> - **(j)** an active marker with a numeric id in body prose → **WARN naming the line**; an active marker **inside an inline code span** (the `298:11` shape) → **WARN** (code spans are not excluded); a **compound id** `289/284` (the `297:252` shape) → **WARN**; the placeholder forms (`<plan>`, `…`) → **no WARN**; the same numeric-id literal inside a **fenced block** → **no WARN**; no marker → **no WARN**.
> - **(k)** a plan whose TIER LINE declares `proven clone` with no `newest same-class` anywhere → **WARN**; clone-framed AND naming `newest same-class` → **no WARN**; no clone framing → **no WARN**; ⚠️ **clone literal in BODY PROSE but not on the tier line → no WARN (the tier-line-only scope is deliberate — a fixture placing the literal off the tier line tests the SKIP, and a failing "positive" there means the fixture is wrong, not the scope).**
> - **(l)** clone-framed ON THE TIER LINE + `trigger fired: **T-2** (…` in the same line + `cycle_tier: T1` → **WARN**; ⚠️ **the PLURAL + HYPHENATED form — the `281:190` fixture line with `cycle_tier` lowered to T1 — → WARN (the mandatory cold-reader-3 control; a singular-only or unhyphenated-only implementation FAILS this fixture)**; same but `cycle_tier: T2` → **no WARN**; clone-framed + tier line where T-2 appears ONLY in a negation list after the fired segment (the `303:154` shape) → **no WARN**; tier line with NEITHER `trigger fired:` nor `triggers fired:` → **no WARN, silent skip**; T-2 firing + not clone-framed → **no WARN**; ⚠️ **a `**Tier:**` line inside a fenced block + a real one → the real one wins (stripped-text scan, first line-start match)**.
> - ⚠️⚠️ **Two fixtures that must be able to FAIL on a wrong `(j)` implementation (cold reader 3 — the mandated hardenings had no failing-capable test):** a fixture with a multi-line fenced block ABOVE a marker → the test asserts the **exact original line number** (a stripped-text numbering bug reports it 6 lines off); and the `289:169` double-marker line → the test asserts **two distinct fires consumed in order** (an unordered fragment-search attributes both to every matching line).
> - **Degenerate:** empty file, no Cycle Log, malformed tier line → **no crash, no false WARN.** **An UNCLOSED fence before a marker (the 302 runs-to-EOF class): under the reuse stripper the content SURVIVES — the regex requires a closing fence — so the marker REMAINS VISIBLE and fires.** ⚠️ **Corrected at cold reader 1: the v1 spec said "treated as fenced," which contradicts the mandated reuse implementation.** The surviving-content behaviour errs toward a false POSITIVE (a visible warn on a malformed plan), which is the acceptable direction for a WARN; **the test asserts no-crash and documents this direction — do NOT modify `gates.py` or build a second stripper to change it.**
> - ⚠️⚠️ **Regression test — the self-fire guard (`(i)`-on-303's lesson):** run all three checks against THIS plan's own text; it must produce **zero `(j)`/`(k)`/`(l)` warnings**. ⚠️⚠️ **INPUT SOURCE (cold reader 2): EMBED THIS PLAN'S FULL TEXT AS A STRING LITERAL at DEV time — the test may read NO plan-file path.** The plan file's path mutates across its lifecycle (`in-progress-executable-<id>.md` → `Done/executable-<id>.md`): a test reading the in-progress path passes QA and then **breaks the NEXT plan's full suite after archival** — a delayed time bomb; a `Done/` path fails during this plan's own run. The sanctioned one-time read of `executable-303.md` is a DEV-time fixture copy, not a licence for runtime path reads. ⚠️ **This plan's body keeps every marker literal bearing a numeric id inside COLUMN-0 fenced blocks** (the reuse stripper strips only those — cold reader 1's finding). **Verify with the check itself, not by reading — cold reader 1 proved by execution that the blockquoted-fence version DID fire (j) on its own lines.**
>
> **Run targeted tests only:** `python3 -m pytest tests/ -k "plan_lint or lint" --tb=short -q 2>&1 | cat`. ⚠️ **Do NOT run the full suite in this step — that is Step 2's job.** Then run `plan_lint` live against a real compliant plan and a deliberately-tripping fixture; **paste the RAW output UNTRUNCATED — never through `head` — and `echo $?` = 0 on each.**
>
> **Scope:**
> - `scripts/plan_lint.py`
> - `tests/test_plan_lint.py`
> - `knowledge/development/enforcement-checks-dev-log-2026-08-06.md`
>
> **Deposit the dev log** with the exact before/after lines per check, the warn-first confirmation (exit 0 on all cases), every fixture edit with intent preserved, and the RAW targeted-test and live-run output. **Canonical Python/MCP file-write — NO heredoc. Commit all (NO push).** `#### Prompt Feedback` in `### Ledger Updates`.
>
> **STOP. Do NOT proceed to Step 2. Wait for CEO verdict.**

**Deposits:**
- `bellows/scripts/plan_lint.py`
- `bellows/tests/test_plan_lint.py`
- `bellows/knowledge/development/enforcement-checks-dev-log-2026-08-06.md`

---
---

## STEP 2 — QA

⚠️⚠️ **THE FALSE-POSITIVE MEASUREMENT IS THE POINT OF THIS STEP.** `(i)` shipped with 11 fires / 8 false and was dropped; these three must show their loads before the hold is treated as lifted.

> **Task Q0 — RE-PIN THE STATE (303's Q0, earned on first use when the bellows HEAD moved between steps).**
> 1. `git -C /Users/marklehn/Developer/GitHub/bellows log -1 --oneline -- scripts/plan_lint.py tests/test_plan_lint.py gates.py` — **the most recent commit touching plan_lint.py or the tests must be Step 1's; `gates.py` is in the pathspec because all three checks key on its stripper (cold reader 5 — a foreign `gates.py` commit in the verdict window would otherwise pass Q0 undetected and Step 2 would sweep under a stripper Step 1 never tested). A foreign commit touching ANY of the three → HALT and report.**
> 2. **Pin the corpus:** `git -C <root> rev-parse HEAD` for each of the five roots — `/Users/marklehn/Developer/GitHub/{anvil,bellows,governance,invoice-pulse,lessons-forge}` — recorded verbatim in the QA report, each beside its counts.
> 3. ⚠️ **Close the pin-vs-sweep window (ACID 5.3): AFTER the final sweep of item 5, re-run `rev-parse HEAD` on all five roots and confirm each equals its pin.** The `Done/` trees move continuously (a plan closed into one mid-session twice this arc); a sweep over a tree that moved after pinning reports counts the pin does not describe. **If any HEAD moved: re-pin, re-run the affected sweeps, and say so in the report.**
>
> 1. **Run the full `bellows` test suite** (→ `full-suite.txt`) **and re-run the targeted subset** `python3 -m pytest tests/ -k "plan_lint or lint" --tb=short -q 2>&1 | cat` (→ `targeted-tests.txt`). Record each raw summary line verbatim — **not a summary of it.** ⚠️ **The targeted re-run exists because `targeted-tests.txt` is a required evidence file with no other producer in this step — an orphan this plan's origin (303) carried and cold reader 1 caught.**
> 2. **Run `plan_lint` against every `*.md` plan in all five `knowledge/decisions/Done/` trees — the sweep glob is `Done/*.md`, PINNED (cold reader 5: `invoice-pulse/…/Done/files.zip` has sat in-tree since April and CRASHES the lint with UnicodeDecodeError, and `.gitkeep` FAILs — an unpinned `Done/*` glob reports a "new" crasher that is four months old and a file count disagreeing with every cited corpus figure)** — addressed ABSOLUTELY (a bellows worktree resolves relative paths against the worktree). Report **per check `(j)`/`(k)`/`(l)`, per root, including zeros**: fire count and ids. ⚠️ **Capture each file's exit status in the sweep — a file that crashes the lint contributes zero WARN lines indistinguishably from a clean file (cold reader 3). Any nonzero exit is reported per file; the `*.md` corpus measured zero crashers, so any crasher is NEW and worth naming.**
> 3. ⚠️⚠️ **Every count is a MEASURED number with the command that produced it. This plan predicts no figure.** Context figures from 305 (3 for the marker, 19 for the claim, at 305's pin) are cited beside the fresh measurement as context ONLY — **if a fresh count differs from a context figure, report the difference; do not reconcile it silently.**
> 4. ⚠️ **`(k)`'s fires: annotate each id against the instruction's TRUE entry date — 2026-07-30, v1.2, commit `3c327e3` (cold reader 4 corrected this from "2026-08-03", an unexecuted inheritance from 305; re-verify the commit, do not trust either date from prose).** Report three bands: clearly-predate / same-day / postdate. **Predating fires are baseline; POSTDATING fires (at authoring: `291`, `diagnostic-301`) are reportable as post-instruction — weighing them is the CEO's.** **`(l)`'s expected-inert result: report the zero AND the reason (no down-tiered T-2 population exists until the §1 executable lands).**
> 5. ⚠️⚠️ **The sweep-diff proof (304's hardening, carried):** run the corpus sweep with the three checks present, and with the PRE-EDIT `plan_lint` — **materialized from the `PRE_EDIT_HASH` the dev log records (`git show <PRE_EDIT_HASH>:scripts/plan_lint.py > /tmp/plan_lint_pre.py`), NEVER `HEAD~1`, which silently points at the wrong state if Step 1 landed more than one commit** — and **diff the two sweep outputs**. ⚠️⚠️ **The materialized script CANNOT run bare — `plan_lint.py` derives `BELLOWS_ROOT` from its own path and `import gates` fails from `/tmp` (cold reader 1, verified). Invoke it as `PYTHONPATH=/Users/marklehn/Developer/GitHub/bellows python3 /tmp/plan_lint_pre.py <plan>`, and confirm it runs on one plan BEFORE sweeping (its failure mode is an ImportError on every file, which a careless sweep reads as zero warnings).** The diff must show ONLY added `(j)`/`(k)`/`(l)` lines — **zero `(a)`–`(h)` lines changed or lost** — and it must be **NON-EMPTY, reconciling with item 2's counts (cold reader 5: an empty diff — both sweeps accidentally running the same script — vacuously satisfies "only added lines"; `(j)` and `(k)` measurably fire today, so a clean-and-empty diff is a broken comparison, not a pass).** A count cannot see a line silently lost; the diff is the presence assertion at value level.
> 6. ⚠️⚠️ **Confirm WARN-only by the MECHANISM, not the symptom:** grep the three new checks and show **none appends to `results` and none assigns `all_passed`**; then show `echo $?` = 0 on a plan tripping all three. **Both.**
> 7. **Emit the QA Receipt with the canonical Rule 20 self-check block**, a verification row per numbered item above with its raw evidence.
>    - `required_evidence_files`: `[targeted-tests.txt, full-suite.txt, corpus-sweep.txt, sweep-diff.txt]`
>    - ⚠️ **These basenames intentionally SUPERSEDE 303/304's working-tree QA deposits (cold reader 4) — the shipped convention (304 overwrote 303's `full-suite.txt`; git history preserves every prior version). Finding the files already present is NOT foreign work and NOT a reason to halt or rename.**
>    - ⚠️ **Deposit all four evidence files BEFORE running the block** — it `sys.exit(1)`s if any is missing or empty.
>    - ⚠️⚠️ **Include the block's literal stdout. The banner `Rule 20 — QA Self-Check Results` and the `PASSED — SELF-CHECK PASSED` line must appear BYTE-EXACT (em-dash U+2014). If it prints FAILED, HALT.**
>    - **Evidence rule:** deposit **RAW command output** (≥ last 200 lines including the pytest summary line), **never a summary.**
>
> **Scope:**
> - `knowledge/qa/enforcement-checks-qa-report-2026-08-06.md`
> - `knowledge/qa/targeted-tests.txt`
> - `knowledge/qa/full-suite.txt`
> - `knowledge/qa/corpus-sweep.txt`
> - `knowledge/qa/sweep-diff.txt`
>
> **STOP. Wait for CEO verdict.**

**Deposits:**
- `bellows/knowledge/qa/enforcement-checks-qa-report-2026-08-06.md`
- `bellows/knowledge/qa/targeted-tests.txt`
- `bellows/knowledge/qa/full-suite.txt`
- `bellows/knowledge/qa/corpus-sweep.txt`
- `bellows/knowledge/qa/sweep-diff.txt`

---

## Method + boundaries

- **Scope is `plan_lint` only.** No doctrine file is edited (the §1 re-scope and the per-phase-commit codification are the FOLLOW-ON executable's, unblocked by this plan's close). No check is blocking. `(i)` is not restored.
- ⚠️ **HALT ROUTING:** if `scripts/plan_lint.py`, `tests/test_plan_lint.py`, any of the five corpus roots, `/Users/marklehn/Developer/GitHub/DRAFTING_CYCLE.md`, **`gates.py` (imported by `plan_lint.py:21` — every lint invocation in both steps dies without it), the Bellows Developer specialist file, `knowledge/decisions/Done/executable-303.md` (the sanctioned fixture read), `/Users/marklehn/Developer/GitHub/RULE_20_SELF_CHECK_BLOCK.md` (Step 2 item 7's block source), or — for Step 2 — the Step-1 dev log carrying `PRE_EDIT_HASH`** is unreadable, HALT the step that needs it and name it in the dev/QA log. ⚠️⚠️ **This list went stale FOUR times inside this one plan (ACID · reader 1 · reader 2 · reader 4), making this the FOURTH consecutive plan carrying the halt-routing staleness class (301 · 302 · 305 · here) — counts reconciled at cold reader 5, which found THREE live statements of this figure disagreeing. Re-derive this list from the steps as written before running; do not trust it as written.**
- ⚠️ **`grep -F` mandatory for literals** (ugrep shim; a non-`-F` pattern can exit 1 silently on a present line). **State what each verification command prints on success and on failure and confirm the two differ.**
- **Gate the FINAL text, UNTRUNCATED, BEFORE the `cp` to `decisions/`** — the 302 lesson; the daemon claims within seconds of deposit.
- ⚠️ **Every `**Deposits:**` filename in this plan is the DECLARED deposit, matched by basename. Do NOT re-date any of them at run time** — a run on a later date keeps the authored date (the resume-glob UTC lesson: derive nothing from the wall clock).

---

## Drafting Cycle

**Tier:** T2 — trigger fired: **T-6** (`plan_lint` is gate machinery; matches 303's declaration). T-7 also fires (authored from diagnostics 301/305); T-6 governs. Structure-for-structure clone of **303**; machinery additionally diffed against **304** (newest same-class).

⚠️ **The tier line above is CANONICAL FORMAT (`**Tier:**` at line start, `trigger fired:` segment, clone declared ON the line) — corrected at cold reader 1, which measured the v1 line as the only format deviant among 73 canonical `Done/` tier lines, in the very plan shipping tier-line-keyed checks.** Self-application: `(k)` sees the clone framing and finds `newest same-class` present → no WARN; `(l)`'s fired segment is `T-6` → no WARN.

⚠️ **Same known consequence as 303/304 (note restored at cold reader 1 — the clone had dropped it):** T2 wants a cold panel gated on a dry walk, a condition no plan has reached in five attempts. **An earned `plan_lint` WARN on this plan's own cycle record is expected and is not a reason to declare a lower tier.**

**Conflict Ledger (§2.8):**
- **C1** — every check stays WARN-only: bare `print(...)`, never touches `results`/`all_passed`, never raises (140/277/303; verified by mechanism AND symptom in Step 2 item 6)
- **C2** — no check extracts entities from free prose; keys are fixed literals, declared fields, or segment-bounded matches on declared lines ((i)'s lesson, walk 1)
- **C3** — every count is measured at its own pin; 305's figures are context, never expected values (walk 1)
- **C4** — this plan's own deposited text produces zero (j)/(k)/(l) warnings; numeric-id marker literals live only in COLUMN-0 fenced blocks — a blockquoted fence is invisible to the reuse stripper (walk 1; corrected at cold reader 1, which proved the blockquoted version fired by executing the check)
- **C5** — the halt-routing list must name every input a step reads; it is known to go stale on folds — re-derive at run time (stale FOUR times in this plan: ACID · reader 1 · reader 2 · reader 4; fourth consecutive plan carrying the class; counts reconciled at cold reader 5 after this very entry decayed)
- **C6** — this plan's own cycle record parses by the checks it ships: canonical tier line, clone declared on it, earned-WARN note present (cold reader 1)

- Lens 1 (weak spots), walk 1: **5 findings, 2 overturning check specs against measured data** — (j)'s exclusion rule was semantic and would have killed a true positive (298's code-spanned active markers) and missed compound ids (297); (l)'s key was negation-vulnerable (303's negation list) → segment-bounded `trigger fired:` key, verified against all three measured formats; sweep-diff pre-edit reference re-pinned by hash, not `HEAD~1`; A0's absence-grep given its literal + a no-pipe rule (a broken probe was caught live this walk reading `head`'s exit as grep's); self-fire regression test added ((i)-on-303's class), draft verified un-firing by running the key against it.
- Lens 2 (destruction), walk 1: **no guard relaxed** — additive checks; existing-test protection (Task D) and the sweep-diff presence assertion carried from 303/304; the A0 restore path stays bounded by the attributability HALT. One fold: fixture lines embedded fenced in-plan so DEV needs no cross-tree read.
- Lens 3 (vulnerabilities), walk 1: **2 findings** — unclosed-fence degenerate case added (302's runs-to-EOF class); (k)'s discussion-text suppression documented as the acceptable false-negative direction. ⚠️ **SUPERSEDED IN PART at cold reader 1 (annotation, not silent rewrite — cold reader 2 caught the stale record):** this line originally recorded the unclosed-fence behaviour as "treated as fenced, false-negative direction"; **execution showed the reuse stripper leaves the content VISIBLE — false-POSITIVE direction. Task E's corrected bullet is authoritative; this record preserves what walk 1 believed.**
- Lens 4 (integration-vs-record), walk 1: **2 findings folded** — deposits no-re-date note added (305's convention, resume-glob UTC lesson); (l)'s dependency on §1's trigger-recording convention stated, with the machine-readable fired-list option ROUTED to the §1 executable rather than decided here. Letters (j)/(k)/(l) measured unused in `plan_lint.py` (grep with positive control); Deposits blocks, DEV-no-full-suite, raw-evidence, and measured-not-predicted conventions all checked against the register.
- Lens 5 (ACID), walk 1: **5 findings** — (5.1) the halt-after-Step-1 state made a stated invariant (warn-only + hold does not lift until Step 2's measurement closes; this plan's keys differ from 305's prototypes so 305's loads do not transfer); (5.2) (k)/(l)'s clone-framing scope was under-specified ("tier line or header") → tier-line-only, verified against all three measured declaration sites; (5.3) the pin-vs-sweep window closed with a post-sweep HEAD re-verification per root; (5.4) the Step-1 dev log (PRE_EDIT_HASH carrier) was MISSING from halt routing — a walk-1 fold created the dependency and the list never learned: **fourth consecutive plan on which this class fired, caught only at ACID, matching the recurrence C5 records**; Conflict Ledger C1–C5 added.
- Cold panel (§2.6), reader 1 (Lens 1 cold): **9 findings, all author-verified, 1 CRITICAL** — the self-fire guard failed as authored (blockquoted fence invisible to the reuse stripper; the reader proved it by EXECUTING the check against this draft) → fixtures moved to a column-0 fence; the materialized pre-edit lint could not import `gates` from `/tmp` → `PYTHONPATH` invocation specified with a one-plan liveness check; the unclosed-fence degenerate spec contradicted the reuse mandate → inverted to the measured surviving-content behaviour; `(j)` line numbers re-located against the original text; this plan's own tier line was the corpus's only format deviant → canonical, clone declared on it, earned-WARN note restored; the off-tier-line declaration floor documented as `(k)`/`(l)`'s third accepted miss; `targeted-tests.txt` given a producer (an orphan inherited from 303); fixture bullets pinned to tier-line placement; halt routing gained two entries (fifth consecutive staleness occurrence, twice in this plan).
- Cold panel (§2.6), reader 2 (Lens 2 cold): **8 findings, all author-verified** — the self-fire regression test had no durable input source (lifecycle path mutation = a delayed time bomb in the NEXT plan's QA) → plan text embedded as a string literal at DEV time; the fixture citation prefixes would break the tier-line anchor on verbatim copy, tempting the contains-match loosening that breaks C4 → strip-prefix instruction, anchor pinned; **(k)'s "all fires predate §2.6" was FALSE for this key — reader executed it: 10 fires, 9 predate, 301 does not** → measured-basis corrected, fourth direction documented (T-8-rationale clone literals on canonical tier lines); A0's restore guard given hunk enumeration (presence-grep cannot see a coexisting foreign hunk); the stale Lens-3 record annotated (record-decay class); (l)'s WARN spelling pinned + Task D stdout forewarning; halt routing gained the Rule 20 block source (stale thrice in this plan); (j) relocation consumes lines in order. **Held under execution: C4 self-fire zero, (l) inert 0/1,366, sweep-diff clean, 49/49 existing tests, no plan_lint output consumers.**
- Cold panel (§2.6), reader 3 (Lens 3 cold): **8 findings, all author-verified, 1 HIGH that gutted (l)'s coverage as spec'd** — the singular-only `trigger fired:` literal missed the PLURAL majority format (19 vs 10 corpus-wide) and the unhyphenated-only clone set missed `proven-clone`: **combined, (l) missed `281:190` — the arc's motivating plan — on both axes; walk 1's three verified sites were all-singular by accident** → both forms mandatory, `281:190` embedded as the mandatory positive control; the (k) suppressor casing pinned case-insensitive (`284` decides); (k)/(l) scan stripped text, first line-start tier match (fenced quotes and multiplicity settled by rule); two failing-capable (j) fixtures added (exact line number, in-order double-marker); QA sweep captures per-file exit status; the 303 fixture path made worktree-relative; WARN lines begin with their check letter; the embedded plan literal made raw. **Measured under the FINAL key: (k) fires 8; 284/288/296 correctly suppressed — the count moved 19 → 10 → 8 with each key revision; it is a property of the key. ⚠️ SUPERSEDED at reader 4 (annotation per this plan's own convention, cold reader 5): the "7 predate, 301 does not" banding recorded here was computed against the wrong instruction date; the corrected banding is 4 predate / 2 same-day / 2 postdate (291 AND 301) — the (k) spec's measured-basis paragraph is authoritative.** **Held under execution: (j) exactly 3/1,366 with zero format variants corpus-wide; C4 self-fire zero via real plan_lint at exit 0; DEV→QA pin premise proven at bellows.py:757–760; test-harness style matches Task E.**
- Cold panel (§2.6), reader 4 (Lens 4 cold): **6 findings, all author-verified, 1 HIGH** — **(k)'s baseline date was an INHERITED-PREMISE ERROR from 305, un-re-executed, in the plan shipping the inherited-premise check: the newest-same-class instruction entered doctrine at v1.2 / 2026-07-30 (`3c327e3`, plan 287's codification), not 2026-08-03/v1.4** → both sites corrected, QA now annotates three bands against the re-verified commit (291 and 301 POSTDATE; QA as previously written would have labelled a post-instruction violation "baseline"); Rule 22(a) → 23(a) (mis-citation cloned from 303:66 — the read-the-cited-rule class, reproduced by cloning exactly as recorded); `gates.py` added to halt routing (stale a FOURTH time in this plan); the "matching existing style" claim for WARN letter-prefixes inverted to "deliberate departure" (no existing WARN carries a letter — measured); plural-majority count paired with both instruments (19v10 file-level, 17v10 tier-line-scoped); QA evidence basename supersession acknowledged. **Held: the full measured basis reproduced independently by execution; every corpus citation verbatim-verified; all doctrine citations correct incl. T-2-still-in-T2; 305/301 characterizations match their deposits except the corrected date; LESSONS.md re-trip scan clean.**
- Cold panel (§2.6), reader 5 (ACID cold): **10 findings, all author-verified, 1 HIGH** — the raw-literal delimiter mandate was spec-impossible against its own content (the body carries the double-quote triple once — INSIDE the mandate itself; a fold-created defect: reader 2 mandated the embed, reader 3 the raw form, neither checked delimiter against content) → **the fix names the delimiter in WORDS, not glyphs — the reader's own proposed glyph fix would have re-planted the bomb, caught at author-verify**; C5 had itself decayed (three live staleness counts disagreeing) → reconciled to four-times-in-this-plan / fourth-consecutive-plan; the sweep glob pinned to `Done/*.md` (files.zip crashes the lint, in-tree since April — "zero crashers" was an `*.md`-only truth); the reader-3 log banding annotated superseded; `gates.py` added to Q0's pathspec (the one open isolation window); five minors (dead pointer repaired verbatim, commit-vs-changelog attribution, worktree note, canonical `(j) WARN:` composed form, sweep-diff non-empty + reconciled). **Held: every measured figure reproduced under all four instruments; C4/C6 self-application zero fires, live lint exit 0; Atomicity clean incl. crash-after-commit into `bellows-preserved/`; Cycle Log ↔ body fully reconciled.**

**Panel complete: five seats, counts 9 · 8 · 6 · 10 (readers 2–5) after walk-1's 9 and ACID-1's 5. No decay — as §2.6 predicts.**

- Confirming pass (closing lens pass, §2): **ran after the reader-5 culmination; found ONE fold-created descriptive error and closed dry after correcting it.** The delimiter-in-words fold's sentence claimed the double-quote triple appears "exactly once" — but the fold itself had removed the glyph it counted (measured: both triples now ZERO; the third instance this cycle of a fix breaking its own description). The correction changes no agent behaviour (the operative mandate — count at DEV time — was already in place); by the composition standard it is not material and does not re-open the walk. **The pass then re-ran in full: all 15 post-condition assertions PASS (both triples zero · (j)/(k)/(l) self-fire zero · ledger C1–C6 ascending · every reader-5 fold present by literal), and the live `plan_lint` gates the final text untruncated at exit 0, all 8 PASS lines.** The last events of the cycle are these measurements — a lens pass, not a fold.

**Closing:** the cycle ran walk 1 (lenses 1–4, 9 findings), ACID 1 (5), the full five-seat sequential cold panel (9 · 8 · 8 · 6 · 10 — all author-verified, no decay), and a confirming pass that closed dry after one descriptive correction. §2's dry condition is NOT claimed — this is a judged stop at panel completion, the stop every plan in this arc has closed on. The record above is the evidence.
'''
    result = _run_lint(plan)
    assert result.returncode == 0, f"Expected exit 0, got {result.returncode}\nstdout: {result.stdout}"
    j_warns = [l for l in result.stdout.splitlines() if "(j) WARN" in l]
    k_warns = [l for l in result.stdout.splitlines() if "(k) WARN" in l]
    l_warns = [l for l in result.stdout.splitlines() if "(l) WARN" in l]
    assert len(j_warns) == 0, f"Expected 0 (j) WARNs, got {len(j_warns)}: {j_warns}"
    assert len(k_warns) == 0, f"Expected 0 (k) WARNs, got {len(k_warns)}: {k_warns}"
    assert len(l_warns) == 0, f"Expected 0 (l) WARNs, got {len(l_warns)}: {l_warns}"
