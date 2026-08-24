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

Residuals, stated: collision/disk checks are not re-run — the daemon's
claim-time re-check still gates hash and clearance; the clearance INSERT is
the one sanctioned out-of-daemon lifecycle.db write (human-invoked, single
row, its own short connection).

BOOTSTRAP NOTE (2026-08-24): this release arm is the declared ONE-TIME manual
patch that releases executable-eluvian-e3-receipts — the plan whose DEV step
supersedes this file with the authored version (see that plan's Deposit
ritual and open fork 4). The 513 shape: a sanctioned bypass retired by the
very plan it releases.
"""

import argparse
import hashlib
import os
import re
import subprocess
import sys
from pathlib import Path

_HERE = os.path.dirname(os.path.abspath(__file__))
_BELLOWS_ROOT = os.path.dirname(_HERE)
_BENIGN_LINT_CHECK_LETTERS = {"c", "d"}  # mirrors depositor.py's filter


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

    # Gate 1: cycle_check — BAR_MET required (read the verdict channel).
    sys.path.insert(0, os.path.join(_BELLOWS_ROOT, "scripts"))
    import cycle_check
    verdict, _ = cycle_check.run_check(Path(hold_path))
    if verdict != "BAR_MET":
        return _fail(f"cycle_check gate: {verdict} (BAR_MET required) — file left held")

    # Gate 2: plan_lint — 0 NON-BENIGN FAIL (the depositor's own filter).
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

    # Class from the plan's own Cycle Manifest — refuse, never guess (S3-6).
    with open(hold_path, "rb") as fh:
        plan_bytes = fh.read()
    m = re.search(r"^class:\s*(\S+)\s*$",
                  plan_bytes.decode("utf-8", errors="replace"), re.MULTILINE)
    if not m:
        return _fail("no Cycle Manifest `class:` line — refuse, never guess")
    assigned_class = m.group(1)

    content_hash = hashlib.sha256(plan_bytes).hexdigest()

    # The one sanctioned out-of-daemon lifecycle.db write: basename, raw-bytes
    # hash — every claim-path consumer keys on the basename (S2-5).
    sys.path.insert(0, _BELLOWS_ROOT)
    import lifecycle
    lifecycle.write_clearance(claimable_name, content_hash, assigned_class, "clear_tool")

    bare_path = os.path.join(os.path.dirname(hold_path), claimable_name)
    os.rename(hold_path, bare_path)
    os.remove(hold_json)  # both release paths dispose of the sidecar (S2-6)

    print(f"Released class hold: {claimable_name}")
    print(f"Clearance written: cleared_by=clear_tool class={assigned_class} hash={content_hash[:12]}")
    print("Deliberate human release act (RULINGS fork 4). Collision/disk checks "
          "not re-run; the daemon's claim-time re-check gates hash+clearance.")
    print("Daemon will claim within 30 seconds.")
    return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("hold_file", help="path to the hold-*.md file")
    parser.add_argument("--release-class-hold", action="store_true",
                        help="deliberate human release of a class-held plan: "
                             "re-runs cycle_check + plan_lint, writes the "
                             "clearance (cleared_by=clear_tool), renames to "
                             "the bare claimable name")
    args = parser.parse_args()
    if args.release_class_hold:
        success = release_class_hold(args.hold_file)
    else:
        success = clear_plan(args.hold_file)
    sys.exit(0 if success else 1)
