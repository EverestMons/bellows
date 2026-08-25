#!/usr/bin/env python3
"""Gated clear tool — releases held plans back into the depositor lane.

Default path: renames hold-<name>.md to ready-<name>.md for re-evaluation by
the LIVE daemon's depositor (D-5(b) re-entry).

--release-class-hold: the deliberate human release act for class-held plans.
RULINGS fork 4: shop-infra never auto-clears — a human runs this flag as the
release act. RULINGS fork 2: the gated clear tool re-runs depositor gates —
this arm re-runs cycle_check (BAR_MET required) and plan_lint (0 non-benign
FAIL, the depositor's own filter), then writes the clearance row itself
(cleared_by='clear_tool' — the DDL enum arm built for exactly this) and
renames hold- -> the bare claimable name, removing the sidecar.

--override-gate: override a gate failure for a specific (plan, step, gate)
triple. The deliberate human act that brings gate_events.overridden alive.

Residuals, stated: collision/disk checks are not re-run — the daemon's
claim-time re-check still gates hash and clearance; the clearance INSERT is
the one sanctioned out-of-daemon lifecycle.db write (human-invoked, single
row, its own short connection).
"""

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path

_HERE = os.path.dirname(os.path.abspath(__file__))
_BELLOWS_ROOT = os.path.dirname(_HERE)
_BENIGN_LINT_CHECK_LETTERS = {"c", "d"}


def _fail(msg):
    print(f"ERROR: {msg}", file=sys.stderr)
    return False


def _validate_hold(hold_path):
    """Shared preconditions. Returns (filename, hold_json) or None."""
    if not os.path.exists(hold_path):
        _fail(f"file does not exist: {hold_path}")
        return None
    filename = os.path.basename(hold_path)
    if not filename.startswith("hold-"):
        _fail(f"file does not start with 'hold-': {filename}")
        return None
    if not filename.endswith(".md"):
        _fail(f"file does not end with '.md': {filename}")
        return None
    hold_json = os.path.splitext(hold_path)[0] + ".hold.json"
    if not os.path.exists(hold_json):
        _fail(f"sidecar does not exist: {hold_json}")
        return None
    return filename, hold_json


def clear_plan(hold_path):
    """Validate preconditions and rename hold- -> ready- for depositor re-evaluation."""
    v = _validate_hold(hold_path)
    if v is None:
        return False
    filename, hold_json = v

    ready_name = "ready-" + filename[len("hold-"):]
    ready_path = os.path.join(os.path.dirname(hold_path), ready_name)
    os.rename(hold_path, ready_path)
    os.remove(hold_json)

    print(f"Renamed to ready- state: {ready_name}")
    print("Daemon will re-evaluate within 30 seconds.")
    return True


def release_class_hold(hold_path):
    """The deliberate human release act for class-held plans (RULINGS forks 2+4)."""
    v = _validate_hold(hold_path)
    if v is None:
        return False
    filename, hold_json = v
    claimable_name = filename[len("hold-"):]

    sys.path.insert(0, os.path.join(_BELLOWS_ROOT, "scripts"))
    import cycle_check
    verdict, _ = cycle_check.run_check(Path(hold_path))
    if verdict != "BAR_MET":
        return _fail(f"cycle_check gate: {verdict} (BAR_MET required) — file left held")

    lint = subprocess.run(
        [sys.executable, os.path.join(_BELLOWS_ROOT, "scripts", "plan_lint.py"), hold_path],
        capture_output=True, text=True, timeout=60,
    )
    if lint.returncode != 0:
        fail_lines = [ln for ln in lint.stdout.splitlines() if ln.startswith("FAIL:")]
        non_benign = []
        for fl in fail_lines:
            m = re.search(r"\(([a-z])\)", fl)
            if m and m.group(1) in _BENIGN_LINT_CHECK_LETTERS:
                continue
            non_benign.append(fl)
        if non_benign:
            for fl in non_benign:
                print(fl, file=sys.stderr)
            return _fail(f"plan_lint gate: {len(non_benign)} non-benign FAIL — file left held")

    with open(hold_path, "rb") as fh:
        plan_bytes = fh.read()
    m = re.search(r"^class:\s*(\S+)\s*$",
                  plan_bytes.decode("utf-8", errors="replace"), re.MULTILINE)
    if not m:
        return _fail("no Cycle Manifest `class:` line — refuse, never guess")
    assigned_class = m.group(1)

    content_hash = hashlib.sha256(plan_bytes).hexdigest()

    sys.path.insert(0, _BELLOWS_ROOT)
    import lifecycle
    lifecycle.write_clearance(claimable_name, content_hash, assigned_class, "clear_tool")

    bare_path = os.path.join(os.path.dirname(hold_path), claimable_name)
    os.rename(hold_path, bare_path)
    os.remove(hold_json)

    print(f"Released class hold: {claimable_name}")
    print(f"Clearance written: cleared_by=clear_tool class={assigned_class} hash={content_hash[:12]}")
    print("Deliberate human release act (RULINGS fork 4). Collision/disk checks "
          "not re-run; the daemon's claim-time re-check gates hash+clearance.")
    print("Daemon will claim within 30 seconds.")
    return True


def override_gate(plan_id_or_slug, step, gate, ref, db_path=None, pending_dir=None):
    """Override a gate failure for a (plan, step, gate) triple."""
    sys.path.insert(0, _BELLOWS_ROOT)
    import lifecycle

    step = int(step)
    id_match = re.fullmatch(r"(?:(?:diagnostic|executable|qa)-)?(\d+)", plan_id_or_slug)

    if id_match:
        plan_id = int(id_match.group(1))
        path = db_path or lifecycle.LIFECYCLE_DB_PATH
        import sqlite3
        conn = sqlite3.connect(path)
        cur = conn.execute(
            """SELECT ge.id FROM gate_events ge
               JOIN steps s ON ge.step_id = s.id
               WHERE s.plan_id = ? AND s.step_number = ?
                 AND ge.gate_name = ? AND ge.result = 'fail'
                 AND ge.overridden = 0""",
            (plan_id, step, gate),
        )
        rows = cur.fetchall()
        if not rows:
            conn.close()
            return _fail(f"no unoverridden fail rows for plan={plan_id} step={step} gate={gate}")
        conn.execute(
            """UPDATE gate_events SET overridden = 1, override_ref = ?
               WHERE id IN (
                   SELECT ge.id FROM gate_events ge
                   JOIN steps s ON ge.step_id = s.id
                   WHERE s.plan_id = ? AND s.step_number = ?
                     AND ge.gate_name = ? AND ge.result = 'fail'
                     AND ge.overridden = 0
               )""",
            (ref, plan_id, step, gate),
        )
        conn.commit()
        updated = conn.total_changes
        conn.close()
        print(f"Overridden {updated} fail row(s) for plan={plan_id} step={step} gate={gate}")
        print(f"override_ref={ref}")
    else:
        resolved_pending_dir = Path(pending_dir) if pending_dir else Path(_BELLOWS_ROOT) / "verdicts" / "pending"
        req_pattern = re.compile(
            rf"^verdict-request-{re.escape(plan_id_or_slug)}-step-{step}\.md$")
        found = None
        if resolved_pending_dir.is_dir():
            for f in os.listdir(resolved_pending_dir):
                if req_pattern.match(f):
                    found = resolved_pending_dir / f
                    break
        if found is None:
            return _fail(f"no pending request file for slug={plan_id_or_slug} step={step} in {resolved_pending_dir}")

        text = found.read_text()
        gate_json = None
        gate_line_idx = None
        for i, line in enumerate(text.splitlines()):
            if line.startswith("**Gate Result JSON:**"):
                try:
                    gate_json = json.loads(line.split(":**", 1)[1].strip())
                    gate_line_idx = i
                except (json.JSONDecodeError, IndexError):
                    pass
        if gate_json is None:
            return _fail(f"no parseable Gate Result JSON in {found}")

        marked = 0
        for f_entry in gate_json.get("failures", []):
            if f_entry.get("gate") == gate and not f_entry.get("overridden", False):
                f_entry["overridden"] = True
                f_entry["override_ref"] = ref
                marked += 1
        if marked == 0:
            return _fail(f"no unoverridden failure for gate={gate} in request file")

        lines = text.splitlines()
        lines[gate_line_idx] = f"**Gate Result JSON:** {json.dumps(gate_json)}"
        found.write_text("\n".join(lines))
        print(f"Marked {marked} failure(s) overridden for slug={plan_id_or_slug} step={step} gate={gate}")
        print(f"override_ref={ref}")
        print(f"Request file: {found}")

    return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("hold_file", nargs="?", default=None,
                        help="path to the hold-*.md file")
    parser.add_argument("--release-class-hold", action="store_true",
                        help="deliberate human release of a class-held plan: "
                             "re-runs cycle_check + plan_lint, writes the "
                             "clearance (cleared_by=clear_tool), renames to "
                             "the bare claimable name")
    parser.add_argument("--override-gate", nargs=3,
                        metavar=("PLAN_ID", "STEP", "GATE"),
                        help="override a gate failure: plan-id-or-slug, step number, gate name")
    parser.add_argument("--ref", help="override justification reference (required with --override-gate)")
    parser.add_argument("--db-path", help="lifecycle DB path (default: repo-resolved)")
    parser.add_argument("--pending-dir", help="pending verdicts directory (default: repo-resolved)")
    args = parser.parse_args()

    if args.override_gate:
        if not args.ref:
            parser.error("--ref is required with --override-gate")
        success = override_gate(args.override_gate[0], args.override_gate[1],
                                args.override_gate[2], args.ref,
                                db_path=args.db_path, pending_dir=args.pending_dir)
    elif args.release_class_hold:
        if not args.hold_file:
            parser.error("hold_file is required with --release-class-hold")
        success = release_class_hold(args.hold_file)
    else:
        if not args.hold_file:
            parser.error("hold_file is required")
        success = clear_plan(args.hold_file)
    sys.exit(0 if success else 1)
