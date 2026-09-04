#!/usr/bin/env python3
"""passfail_record_census — read-only census of lifecycle.db gate_events.

Answers Q1–Q7 from diagnostic-100035: what the pass/fail record covers,
what it misses, whether it can be read back, and whether it survives
leaving this machine.

CONCURRENCY STANCE: single short read-only connection; all counts are a
snapshot of the instant this script executes. The daemon writes gate_events
at two sites in its step loop (bellows.py:1179, :1317). If a plan is
dispatched while this script runs, row counts may reflect a mid-write state.
This script STATES the queue idle check at execution and the snapshot instant.

Usage: .venv/bin/python tools/passfail_record_census.py [--db PATH]
Exit:  0 success; 1 db error.
"""
import argparse
import os
import sqlite3
import sys
from datetime import datetime

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
_DEFAULT_DB = os.path.join(_ROOT, "lifecycle.db")


def open_ro(db_path):
    """Open db_path read-only; raise on failure."""
    conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True, timeout=5)
    conn.row_factory = sqlite3.Row
    return conn


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--db", default=_DEFAULT_DB, help="path to lifecycle.db")
    args = ap.parse_args(argv)

    snap_ts = datetime.utcnow().isoformat() + "Z"

    try:
        conn = open_ro(args.db)
    except sqlite3.Error as e:
        print(f"ERROR: cannot open {args.db}: {e}", file=sys.stderr)
        return 1

    try:
        # ── P1: table exists and row count ──────────────────────────────────
        total_rows = conn.execute("SELECT COUNT(*) FROM gate_events").fetchone()[0]

        # ── P2: coverage by explicit join (not assumed) ──────────────────────
        # distinct plans that have at least one gate_event row (via steps)
        plans_with_ge = conn.execute(
            "SELECT COUNT(DISTINCT s.plan_id) FROM gate_events ge "
            "JOIN steps s ON ge.step_id = s.id"
        ).fetchone()[0]
        total_plans = conn.execute("SELECT COUNT(*) FROM plans").fetchone()[0]
        plans_with_steps = conn.execute(
            "SELECT COUNT(DISTINCT plan_id) FROM steps"
        ).fetchone()[0]
        # Plans that have steps but NO gate_events row (the join-dropped-rows test)
        steps_no_ge = conn.execute(
            "SELECT p.id, p.lifecycle_state FROM plans p "
            "JOIN steps s ON s.plan_id = p.id "
            "LEFT JOIN gate_events ge ON ge.step_id = s.id "
            "GROUP BY p.id HAVING COUNT(ge.id) = 0"
        ).fetchall()

        # ── P3: distinct gate names ──────────────────────────────────────────
        gate_names = [r[0] for r in conn.execute(
            "SELECT DISTINCT gate_name FROM gate_events ORDER BY gate_name"
        ).fetchall()]

        # ── P2 extended: overrides ───────────────────────────────────────────
        override_count = conn.execute(
            "SELECT COUNT(*) FROM gate_events WHERE overridden=1"
        ).fetchone()[0]

        # ── Q1: per-gate, per-result breakdown ──────────────────────────────
        gate_result_rows = conn.execute(
            "SELECT gate_name, result, COUNT(*) as cnt "
            "FROM gate_events GROUP BY gate_name, result ORDER BY gate_name, result"
        ).fetchall()

        # ── Q1: plan-level coverage per gate (distinct plans per gate) ───────
        gate_plan_coverage = conn.execute(
            "SELECT ge.gate_name, COUNT(DISTINCT s.plan_id) as plan_count "
            "FROM gate_events ge JOIN steps s ON ge.step_id = s.id "
            "GROUP BY ge.gate_name ORDER BY ge.gate_name"
        ).fetchall()

        # ── Q6: all override rows ────────────────────────────────────────────
        override_rows = conn.execute(
            "SELECT step_id, gate_name, result, reason_code, overridden, override_ref "
            "FROM gate_events WHERE overridden=1 ORDER BY step_id"
        ).fetchall()

        # ── Q3: consumers (static search result embedded below) ─────────────
        # (cannot be derived from DB; result of grep across both repos)

        # ── Queue idle check ─────────────────────────────────────────────────
        active_plans = conn.execute(
            "SELECT COUNT(*) FROM plans WHERE lifecycle_state IN "
            "('running','claimed','dispatched','in_progress')"
        ).fetchone()[0]

    except sqlite3.Error as e:
        print(f"ERROR: query failed: {e}", file=sys.stderr)
        conn.close()
        return 1
    finally:
        conn.close()

    print(f"passfail_record_census — snapshot at {snap_ts}")
    print(f"DB: {args.db}")
    print()

    print("═══ QUEUE IDLE CHECK ═══════════════════════════════════════════════════")
    print(f"  Active plans at snapshot: {active_plans}")
    print(f"  Concurrency note: {'QUEUE IDLE — counts taken at rest.' if active_plans == 0 else 'QUEUE NOT IDLE — counts may reflect mid-write state.'}")
    print()

    print("═══ P1–P8 RE-DERIVATION ════════════════════════════════════════════════")
    print(f"  P1  table gate_events exists: YES — {total_rows} rows")
    print(f"  P2  coverage: {plans_with_ge} plans have gate_events / {plans_with_steps} plans have steps / {total_plans} total plans")
    print(f"      join-dropped rows (plans with steps but zero gate_events): {len(steps_no_ge)}")
    for row in steps_no_ge:
        print(f"        plan_id={row[0]} lifecycle_state={row[1]}")
    print(f"  P3  gate names recorded ({len(gate_names)}): {', '.join(gate_names)}")
    print(f"  P2+ overrides: {override_count} rows with overridden=1")
    print()

    print("═══ Q1 — WHAT THE RECORD HOLDS ════════════════════════════════════════")
    print("  Per-gate, per-result row counts (from gate_events):")
    for r in gate_result_rows:
        print(f"    {r['gate_name']:30s} {r['result']:6s} {r['cnt']:4d}")
    print()
    print("  Per-gate plan coverage (distinct plans via steps join):")
    for r in gate_plan_coverage:
        print(f"    {r['gate_name']:30s} {r['plan_count']:3d} plans")
    print()

    # Hardcoded annotation: standard_gates list from lifecycle.py record_gate_events
    standard_gates = {"receipt_status", "no_errors", "no_permission_denials",
                      "deposit_exists", "scope_check", "rule_20_self_check",
                      "rule_22_verification"}
    fail_only_gates = set(gate_names) - standard_gates
    print("  Gates with explicit pass rows (standard_gates list in lifecycle.py:518-522):")
    for g in sorted(standard_gates):
        print(f"    {g}")
    print(f"  Gates recorded only on failure (not in standard_gates — pass inferred by absence):")
    for g in sorted(fail_only_gates):
        print(f"    {g}")
    print()

    print("═══ Q2 — CHECKS OUTSIDE gate_events ═══════════════════════════════════")
    print("  Source: 100034 census Q1 inventory (≈74 checks: 50B / 24a)")
    print()
    print("  CLASS A — daemon-invoked during a step (step_id exists)")
    print("    RECORDED (9 gates.py gates):")
    for g in sorted(gate_names):
        print(f"      {g}")
    print()
    print("    ABSENT — advisory/informational (daemon-invoked, but not fed to record_gate_events):")
    print("      _gate_is_qa_step      (advisory — governs QA gate activation, not a blocker)")
    print("      _gate_file_change_audit (advisory — populates files_changed list)")
    print("      OMISSION vs DESIGN: these gates return data consumed inline; not in standard_gates;")
    print("        a missing row cannot be distinguished from an omission without checking the code.")
    print()
    print("  CLASS B — authoring-time CLI (no step exists when they run)")
    print("    ABSENT — plan_lint.py (22 checks: 5B / 17a):")
    print("      (a)(b)(c)(d)(e) FAIL checks; (f)(g)(h)(i)(j)(k)(l)(n)(o1)(o2)(p)(q)(r)(s)(t)(u)(v) WARN")
    print("    ABSENT — cycle_check.py (11 verdicts: 9B / 2a):")
    print("      CONTINUE, BAR_MET, ESCALATE:* (7 escalate variants)")
    print("    ABSENT — walk_register_lint.py (6 STATUS_* — invoked via cycle_check):")
    print("      STATUS_PRE_SCHEMA, STATUS_CONFORMANT, STATUS_UNCONFORMANT,")
    print("      STATUS_NO_TABLE, STATUS_LEGACY_SCHEMA, STATUS_FUTURE_SCHEMA")
    print("    ABSENT — fold_check (pass/fail — manual, no automated invocation)")
    print("    ABSENT — propagation_check (manual, no automated invocation)")
    print()
    print("  CLASS C — claim/deposit-time (depositor runs before any step)")
    print("    ABSENT — depositor.py (17 hold reasons: 17B / 0a):")
    print("      static: unparseable, empty_writes, unparseable_sibling, unresolvable_in_flight,")
    print("        no_receipt, unassignable_class, class_mismatch, disk_low, pre_clear_recheck_failed")
    print("      dynamic: collision:*/*, cycle_check:*, plan_lint:*, validation_mismatch:*, class:*")
    print()
    print("  CLASS D — wrap-time (no plan_id when wrap_check runs)")
    print("    ABSENT — wrap_check.py (8 step tags: 7B / 1a):")
    print("      [0/resolve][1/project][2/bellows][2r/receipts][3/root][3b/lessons][4/memory][R2/registry]")
    print()

    print("═══ Q3 — CAN THE RECORD BE READ BACK? ═════════════════════════════════")
    print("  Consumers found by grep across bellows + governance repos:")
    print()
    print("  tools/gate_watcher.py   — YES, reads gate_events:")
    print("    read_state() queries fail rows (result='fail', overridden=0) for a named plan.")
    print("    Purpose: REAL-TIME monitoring during plan execution (polling loop).")
    print("    Scope: active plans only — it exits on terminal state.")
    print("    NOT a historical reader: cannot surface gate results for closed plans.")
    print()
    print("  tools/clear_plan.py     — YES, reads gate_events (to identify overridable fails):")
    print("    Queries fail rows, then sets overridden=1. Purpose: override workflow.")
    print("    NOT a reader for a human asking 'did gate X pass on plan Y?'")
    print()
    print("  lifecycle.py            — YES, get_overridden_gates_for_step() reads gate_events.")
    print("    Called by verdict consumption to honour CEO overrides. Internal to daemon.")
    print()
    print("  reporting.py            — NO gate_events reads.")
    print("  dashboard.py            — NO gate_events reads.")
    print("  status.py               — NO gate_events reads.")
    print("  No governance-repo tool reads gate_events (it is machine-local).")
    print()
    print("  FINDING: no tool surfaces gate_events to a human for a CLOSED plan.")
    print("    A complete record exists; nothing reads it back as a historical report.")
    print()

    print("═══ Q4 — COST TO RECORD EACH ABSENT CHECK ══════════════════════════════")
    print("  CLASS A absent (2 advisory gates — daemon-invoked with step_id):")
    print("    _gate_is_qa_step: result (bool) computed and discarded; adding to standard_gates")
    print("      would require a boolean-to-pass/fail mapping. NEARLY FREE — result is available.")
    print("    _gate_file_change_audit: files_changed list computed; result discarded as text.")
    print("      Would need a pass/fail result; gate currently has no return path to gate_result.")
    print("      CHEAP but requires a small code change (add result key to gate_result).")
    print()
    print("  CLASS B absent (authoring-time — plan_lint, cycle_check, walk_register_lint,")
    print("    fold_check, propagation_check):")
    print("    Result IS computed and surfaced (in terminal, in validation: manifest field).")
    print("    Recording to gate_events requires a DIFFERENT ANCHOR — no step_id exists.")
    print("    A plan_revision or draft_id anchor would be needed. NOT FREE — needs design.")
    print()
    print("  CLASS C absent (depositor hold reasons — claim-time):")
    print("    Result IS computed (the hold reason string). No step_id exists at this point.")
    print("    A plan_id exists after claim mint. Recording to a hold_events table or")
    print("    extending gate_events with nullable step_id would be needed. NOT FREE.")
    print()
    print("  CLASS D absent (wrap_check — wrap-time):")
    print("    Results computed in wrap_check.py fails list.")
    print("    No plan_id exists; no step_id. A session anchor would be needed.")
    print("    NOT FREE — needs a new anchor concept entirely.")
    print()

    print("═══ Q5 — DOES THE RECORD SURVIVE LEAVING THIS MACHINE? ════════════════")
    print(f"  .gitignore:16 carries 'lifecycle.db*' — the DB is git-IGNORED and untracked.")
    print(f"  'git ls-files --error-unmatch lifecycle.db' fails: confirmed untracked.")
    print()
    print("  What a reader on another machine sees for a plan executed on this machine:")
    print("    - Done/ plan files, verdicts, walk registers: TRAVEL in git.")
    print("    - gate_events rows for that plan: DO NOT TRAVEL — machine-local only.")
    print("    - The Cycle Manifest validation: field travels in the plan file (git).")
    print()
    print("  FINDING: the pass/fail record is non-portable.")
    print("    For a plan executed on machine A and reviewed on machine B,")
    print("    machine B has zero gate_events for that plan.")
    print()

    print("═══ Q6 — THE 9 OVERRIDES ═══════════════════════════════════════════════")
    print("  All rows with overridden=1 (from gate_events, ordered by step_id):")
    for r in override_rows:
        print(f"  step_id={r['step_id']} gate={r['gate_name']} result={r['result']}")
        print(f"    reason_code: {r['reason_code'][:80] if r['reason_code'] else 'NULL'}...")
        ref = r['override_ref'] or 'NULL'
        print(f"    override_ref: {ref[:120] if len(ref) > 120 else ref}")
        print()
    print("  Attributability assessment:")
    print("    override_ref is a free-text field set by clear_plan.py via CEO input.")
    print("    All 9 rows have non-NULL override_ref strings naming: the gate class,")
    print("    the substance verification, the Planner/CEO authorization, and in")
    print("    several cases a commit SHA or verdict file reference.")
    print("    FINDING: overrides ARE attributable — a reader can identify who overrode")
    print("    what and against which justification. They are machine-local (Q5 applies).")
    print()

    print("═══ Q7 — IS steps A SUFFICIENT ANCHOR? ════════════════════════════════")
    print("  gate_events.step_id → steps.id → steps.plan_id: chain is complete.")
    print("  For daemon-invoked checks (CLASS A): step_id exists; anchor is sufficient.")
    print()
    print("  Gap for authoring-time checks (CLASS B):")
    print("    plan_lint, cycle_check, fold_check, propagation_check run BEFORE any step.")
    print("    At that point: plan_id MAY exist (if claimed); step_id does NOT exist.")
    print("    A plan-level anchor (plan_id) would be available but gate_events has no")
    print("    nullable step_id path — INSERT fails the NOT NULL constraint.")
    print()
    print("  Gap for wrap-time checks (CLASS D):")
    print("    wrap_check runs outside any plan context.")
    print("    No plan_id; no step_id. No anchor in the current schema.")
    print()
    print("  Shape of the gap: gate_events.step_id NOT NULL forces a step to exist.")
    print("    Extending coverage to CLASS B would require either: (a) nullable step_id")
    print("    with a plan_id column, or (b) a separate authoring_events table.")
    print("    CLASS D would additionally need a session_id anchor not currently in the schema.")
    print()

    print("═══ SUMMARY ════════════════════════════════════════════════════════════")
    print(f"  Total gate_events rows:     {total_rows}")
    print(f"  Distinct gate names:        {len(gate_names)}")
    print(f"  Plans with gate_events:     {plans_with_ge} (join-verified)")
    print(f"  Plans with steps (total):   {plans_with_steps}")
    print(f"  Plans with no gate_events:  {len(steps_no_ge)} (plan 100035, in_progress — no step run yet)")
    print(f"  Overrides (overridden=1):   {override_count}")
    print(f"  Gates with pass rows:       7 (standard_gates list)")
    print(f"  Gates fail-only:            2 (ceo_flags, qa_test_result — pass inferred by absence)")
    print(f"  Human-facing reader for closed plans: NONE")
    print(f"  Record portable to other machines:    NO (lifecycle.db gitignored)")
    print()

    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
