#!/usr/bin/env python3
"""lens_commit — commits one lens in the correct order.

Usage:
    lens_commit.py <draft> --register <path> --walk <N> --lens <N> --desc <text>
                           [--allow-yield-rising]

Steps:
    1. baseline     — fold_check --save-baseline on draft
    2. lint         — walk_register_lint gate (SHAPE-OK, no COVERAGE: INCOMPLETE)
    3. cycle        — cycle_check BAR_MET gate (yield-rising handling)
    4. assert       — subject lens name checked against internal table
    5. commit       — git add register + baseline, commit with composed subject
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path

SCRIPTS = Path(os.path.dirname(os.path.abspath(__file__)))

LENS_NAMES = {
    1: "Weak spots",
    2: "Destruction",
    3: "Vulnerabilities",
    4: "Integration-record",
    5: "ACID",
}

# Separate dict for the assert step — tests patch LENS_NAMES; _NAMES stays fixed
_NAMES = {
    1: "Weak spots",
    2: "Destruction",
    3: "Vulnerabilities",
    4: "Integration-record",
    5: "ACID",
}

_YIELD_RISING_WALK_CEILING = 6  # walk >= 7 refuses even with --allow-yield-rising


def run_checker(script, *args):
    """Seam: run a checker subprocess. Returns (returncode, combined_output)."""
    result = subprocess.run(
        [sys.executable, str(SCRIPTS / script), *args],
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
    )
    return result.returncode, result.stdout


def _baseline_path(draft_path):
    p = Path(draft_path)
    return p.parent / f".{p.name}.foldcheck.json"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[1].strip())
    ap.add_argument("draft", help="Path to the draft plan file")
    ap.add_argument("--register", required=True, help="Walk register path")
    ap.add_argument("--walk", required=True, type=int, help="Walk number")
    ap.add_argument("--lens", required=True, type=int, help="Lens number (1-5)")
    ap.add_argument("--desc", required=True, help="Short description suffix for the subject")
    ap.add_argument("--allow-yield-rising", action="store_true",
                    help="Allow lens commit when yield-rising detected (walk <= 6 only)")
    args = ap.parse_args(argv)

    draft_path = Path(args.draft)
    register_path = Path(args.register)
    walk_n = args.walk
    lens_n = args.lens
    desc = args.desc

    if not draft_path.is_file():
        print(f"ERROR: draft not found: {draft_path}", file=sys.stderr)
        return 1
    if not register_path.is_file():
        print(f"ERROR: register not found: {register_path}", file=sys.stderr)
        return 1
    if lens_n not in LENS_NAMES:
        print(f"ERROR: lens {lens_n} not in table (1–5)", file=sys.stderr)
        return 1

    # Step 1: fold_check --save-baseline
    rc, out = run_checker("fold_check.py", "--save-baseline", str(draft_path))
    if rc != 0:
        print(f"LENS-COMMIT: baseline FAIL — fold_check exit {rc}: {out.strip()}")
        return 1

    # Step 2: walk_register_lint gate
    rc, out = run_checker("walk_register_lint.py", str(register_path),
                          "--plan", str(draft_path))
    if "SHAPE-OK" not in out:
        print(f"LENS-COMMIT: lint FAIL — walk_register_lint not SHAPE-OK")
        return 1
    if "COVERAGE: INCOMPLETE" in out:
        print(f"LENS-COMMIT: lint FAIL — COVERAGE: INCOMPLETE")
        return 1

    # Step 3: cycle_check gate
    rc, out = run_checker("cycle_check.py", str(draft_path))
    if "ESCALATE:yield-rising" in out:
        if not args.allow_yield_rising:
            print("LENS-COMMIT: cycle FAIL — yield-rising; pass --allow-yield-rising to override")
            return 1
        if walk_n > _YIELD_RISING_WALK_CEILING:
            print(f"LENS-COMMIT: cycle FAIL — yield-rising at walk {walk_n} > {_YIELD_RISING_WALK_CEILING} not allowed")
            return 1
        warn = f"\n**WARN (walk {walk_n}):** yield-rising detected, lens commit allowed by override\n"
        register_path.write_text(
            register_path.read_text(encoding="utf-8") + warn, encoding="utf-8"
        )
    else:
        last = out.strip().split("\n")[-1] if out.strip() else ""
        if not last.startswith("BAR_MET"):
            print(f"LENS-COMMIT: cycle FAIL — expected BAR_MET, got {last!r}")
            return 1

    # Step 4: compose + assert subject
    composed_name = LENS_NAMES[lens_n]
    expected_name = _NAMES[lens_n]
    if composed_name != expected_name:
        print(f"LENS-COMMIT: assert FAIL — LENS_NAMES[{lens_n}]={composed_name!r} != expected {expected_name!r}")
        return 1

    slug = draft_path.stem
    subject = f"draft({slug}): walk {walk_n} lens {lens_n} — {composed_name}: {desc}"

    # Step 5: commit
    repo_dir = draft_path.parent
    to_add = [str(register_path.resolve())]
    bpath = _baseline_path(draft_path)
    if bpath.is_file():
        to_add.append(str(bpath.resolve()))

    r = subprocess.run(
        ["git", "-C", str(repo_dir), "add"] + to_add,
        capture_output=True, text=True,
    )
    if r.returncode != 0:
        print(f"LENS-COMMIT: commit FAIL — git add: {r.stderr.strip()}")
        return 1

    r = subprocess.run(
        ["git", "-C", str(repo_dir), "commit", "-m", subject],
        capture_output=True, text=True,
    )
    if r.returncode != 0:
        print(f"LENS-COMMIT: commit FAIL — git commit: {r.stderr.strip()}")
        return 1

    print(f"LENS-COMMIT: commit OK — {subject}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
