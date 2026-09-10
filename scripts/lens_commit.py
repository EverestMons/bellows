#!/usr/bin/env python3
"""lens_commit — commits one lens in the correct order.

Usage:
    lens_commit.py <draft> --register <path> --walk <N> --lens <N> --desc <text>
                           [--dry] [--allow-yield-rising]

Steps:
    0. record       — in HEAD, diff facts (draft / register / cycle-only / vacuity /
                      duplicate); every record FAIL fires here
    1. baseline     — fold_check --save-baseline on draft
    2. lint         — walk_register_lint gate (SHAPE-OK, no COVERAGE: INCOMPLETE)
    2b. lint        — plan_lint WARN/FAIL echo (never refuses; gate stays with step 3)
    3. cycle        — cycle_check BAR_MET gate (yield-rising handling)
    4. assert       — subject lens name checked against internal table
    5. commit       — git add draft + register + baseline; --dry writes the DRY line
                      when the register is unchanged; a fold without a register row refuses
"""

import argparse
import os
import re
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

# Cycle-Log-only shapes a dry lens may change (panel D1 census of 235 dry commits).
# A content line is cycle-only if, after its diff sign, it is blank or matches one
# of these three patterns.
_CYCLE_LINE_RE = re.compile(
    r"^(?:"
    r"- (?:Weak spots|Destruction|Vulnerabilities|Integration-record|ACID):"
    r"|\*\*Walk \d+ — "   # em-dash
    r"|walks: \d+$"
    r")"
)


def _is_cycle_line(rest):
    """True when the content after the diff sign is blank or a cycle-record-only shape."""
    return not rest.strip() or bool(_CYCLE_LINE_RE.match(rest))


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
    ap.add_argument("--dry", action="store_true",
                    help="Attest this is a dry lens; the tool appends the DRY register row")
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

    # Resolve paths used throughout — every step-0 git call takes resolved absolute paths
    slug = draft_path.stem
    draft_resolved = draft_path.resolve()
    register_resolved = register_path.resolve()
    repo_dir = draft_resolved.parent

    # Step 0: record — in HEAD, diff facts; every record FAIL fires here, before any
    # baseline write can mask the author's state (the --allow-yield-rising WARN lands
    # inside step 3; step 0 is earlier, so the facts are clean)
    r_root = subprocess.run(
        ["git", "-C", str(repo_dir), "rev-parse", "--show-toplevel"],
        capture_output=True, text=True,
    )
    if r_root.returncode != 0:
        print(f"LENS-COMMIT: record FAIL — no git repo above {draft_path}")
        return 1
    root = Path(r_root.stdout.strip())

    # (i) both files must be in HEAD — HEAD:<root-relative path>
    draft_rel = os.path.relpath(str(draft_resolved), str(root))
    r = subprocess.run(
        ["git", "-C", str(root), "cat-file", "-e", f"HEAD:{draft_rel}"],
        capture_output=True,
    )
    if r.returncode != 0:
        print(f"LENS-COMMIT: record FAIL — {draft_path.name} is not committed; "
              f"commit the walk-0 state first")
        return 1
    register_rel = os.path.relpath(str(register_resolved), str(root))
    r = subprocess.run(
        ["git", "-C", str(root), "cat-file", "-e", f"HEAD:{register_rel}"],
        capture_output=True,
    )
    if r.returncode != 0:
        print(f"LENS-COMMIT: record FAIL — {register_path.name} is not committed; "
              f"commit the walk-0 state first")
        return 1

    # (ii) diff facts
    r = subprocess.run(
        ["git", "-C", str(repo_dir), "diff", "--quiet", "HEAD", "--",
         str(draft_resolved)],
        capture_output=True,
    )
    if r.returncode not in (0, 1):
        print(f"LENS-COMMIT: record FAIL — git diff --quiet exit {r.returncode} "
              f"on {draft_path.name}")
        return 1
    draft_changed = r.returncode == 1

    r = subprocess.run(
        ["git", "-C", str(repo_dir), "diff", "--quiet", "HEAD", "--",
         str(register_resolved)],
        capture_output=True,
    )
    if r.returncode not in (0, 1):
        print(f"LENS-COMMIT: record FAIL — git diff --quiet exit {r.returncode} "
              f"on {register_path.name}")
        return 1
    register_changed = r.returncode == 1

    # (v) duplicate guard — scoped to THIS draft's slug (governance is a multi-draft repo)
    r_head = subprocess.run(
        ["git", "-C", str(repo_dir), "log", "--format=%s", "-1", "HEAD"],
        capture_output=True, text=True,
    )
    head_subject = r_head.stdout.strip() if r_head.returncode == 0 else ""
    dup_prefix = f"draft({slug}): walk {walk_n} lens {lens_n}"
    reg_text_check = register_path.read_text(encoding="utf-8")
    dup_in_reg = f"**Walk {walk_n} lens {lens_n} —" in reg_text_check
    if head_subject.startswith(dup_prefix) or dup_in_reg:
        print(f"LENS-COMMIT: record FAIL — walk {walk_n} lens {lens_n} is already on the record")
        return 1

    # (iii) parse draft diff for cycle-only check (plumbing flags defeat color.ui/diff.external)
    draft_cycle_only = True
    content_line_parsed = False
    first_offending = ""
    if draft_changed:
        r_diff = subprocess.run(
            ["git", "-C", str(repo_dir),
             "-c", "color.ui=false", "-c", "diff.external=",
             "diff", "--no-color", "--no-ext-diff", "--no-prefix", "-U0",
             "HEAD", "--", str(draft_resolved)],
            capture_output=True, text=True,
        )
        for line in r_diff.stdout.split("\n"):
            if not line:
                continue
            if line[0] not in ("+", "-"):
                continue
            if line.startswith("+++ ") or line.startswith("--- "):
                continue
            content_line_parsed = True
            rest = line[1:]
            if not _is_cycle_line(rest):
                draft_cycle_only = False
                first_offending = rest[:80]
                break

    # (iv) vacuity check
    if draft_changed and not content_line_parsed:
        print("LENS-COMMIT: record FAIL — the draft changed but its diff could not be read")
        return 1

    # Record rule (refusals fire at step 0)
    if args.dry:
        if not draft_cycle_only:
            print(f"LENS-COMMIT: record FAIL — --dry, but the draft changed beyond "
                  f"its cycle record: {first_offending}")
            return 1
    else:
        if not register_changed:
            print(f"LENS-COMMIT: record FAIL — the register carries no row for "
                  f"walk {walk_n} lens {lens_n}; write the fold row (§2.7), "
                  f"or pass --dry for a dry lens")
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

    # Step 2b: plan_lint WARN/FAIL echo — never refuses; gate stays with step 3
    _lint_rc, _lint_out = run_checker("plan_lint.py", str(draft_path))
    for _line in _lint_out.splitlines():
        if re.match(r"^(\([a-z0-9]+\) )?WARN: ", _line.strip()):
            print(f"LENS-COMMIT: plan_lint WARN — {_line}")
        elif _line.startswith("FAIL: "):
            print(f"LENS-COMMIT: plan_lint FAIL — {_line}")

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

    subject = f"draft({slug}): walk {walk_n} lens {lens_n} — {composed_name}: {desc}"

    # Step 5: commit — draft + register + baseline; --dry writes DRY line when register unchanged
    if args.dry and not register_changed:
        dry_line = (f"**Walk {walk_n} lens {lens_n} — {LENS_NAMES[lens_n]}"
                    f" — DRY, basis:** {desc}")
        register_path.write_text(
            register_path.read_text(encoding="utf-8") + dry_line + "\n",
            encoding="utf-8",
        )

    to_add = [str(draft_resolved), str(register_resolved)]
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
