#!/usr/bin/env python3
"""Guard (a) — the LESSONS.md corpus freeze — made mechanical and re-takeable.

PLANNER_TEMPLATE.md:2094 states guard (a) as: "The wrap CHECKS for deposited
plans before any append." That check is point-in-time, and nothing re-takes it.
⛔ The window between the check and the write is UNBOUNDED WALL-CLOCK, and for a
plan paused at a verdict it spans the whole pause (thread 137, cold-panel
CAPSTONE 2026-09-04, corroborated by two live incidents the same day: this
machine appended entries 419-423, then another machine appended 424-425 and
pushed, rejecting this machine's commits — both pins went stale).

This tool makes the guard re-takeable, so it can be taken again immediately
before the write rather than once at the top of the sweep:

    pin                  → refuse if the corpus is frozen; else emit LESSONS.md's sha
    verify --sha <sha>   → refuse if the corpus froze OR the sha moved since the pin

⚠️ `verify` must be the LAST act before the write. It shrinks the window from
unbounded wall-clock to the gap between two adjacent acts; it does not remove it.
It catches writer classes 1 (this machine's session) and 2 (another machine's,
arriving as a push). It does NOT sequence writer class 3, the wrap's own
`project_status_markers.py --apply` in-place marker rewrite — that one carries
its own `prove_inert` guard, measured 2026-09-05 as covering ~98% of its window
(a concurrent append landing in the residual 0.7ms is silently lost). Class 3 is
left to thread 137's remaining forks.

⛔ ROOTED AT THE SHOP, NOT THE GOVERNANCE REPO. Guard (a)'s doctrine text names
one `decisions/` lane; the corpus is shop-wide across TWELVE, three of them
daemon-watched. wrap_check.py's own enumeration is rooted at $ELUVIAN_WRAP_ROOT
(the governance repo) and so can see exactly ONE. This tool globs from the shop
root at both depths, because the governance lane is nested one level deeper than
every other repo's.
"""

import argparse
import hashlib
import os
import re
import sys
from pathlib import Path

# A plan file's KIND. Only these are cycle plans; roadmap-, runbook-, reporting-
# and sa-blueprint- documents share the lane but are not plans and never freeze.
_KIND = r"(?:executable|diagnostic|qa)"

# Lifecycle prefixes that are DEPOSITED-BUT-UN-RUN, so they freeze the corpus.
# `in-progress-` is here on doctrine's explicit word ("an in-progress-* plan DOES
# freeze — its pin is live"); `verdict-pending-` because a plan paused at a
# verdict is precisely the unbounded window thread 137 names.
# ⚠️ This is deliberately NOT bellows.is_runnable_plan(): that predicate answers
# "can the daemon CLAIM this?" and returns False for in-progress- and
# verdict-pending-, which is the opposite of what the freeze needs.
_FREEZING_RE = re.compile(
    rf"^(?:parallel-\d+-)?(?:hold-|ready-|in-progress-|verdict-pending-)?{_KIND}-.*\.md$"
)

# PARKED, not pending: doctrine says a halted-* artifact does not freeze, and its
# own resume re-verifies the batch pin. parked-/obsolete- are parked by name.
_PARKED_PREFIXES = ("halted-", "parked-", "obsolete-")


def shop_root() -> Path:
    """The shop root — the parent of the repos, not the governance repo itself."""
    env = os.environ.get("ELUVIAN_SHOP_ROOT")
    if env:
        return Path(env)
    gov = os.environ.get("ELUVIAN_WRAP_ROOT")
    if gov:
        return Path(gov).parent
    return Path.home() / "Developer"


def decision_lanes(root: Path) -> list[Path]:
    """Every knowledge/decisions lane in the shop, at BOTH depths.

    The governance repo nests its lane one level deeper
    (eluvian-governance/governance/knowledge/decisions), so a single-depth glob
    silently misses it — or, rooted at governance, misses all eleven others.
    """
    found = set(root.glob("*/knowledge/decisions")) | set(root.glob("*/*/knowledge/decisions"))
    return sorted(p for p in found if p.is_dir() and "/.git/" not in str(p))


def freezing_plans(root: Path) -> list[Path]:
    """Deposited-but-un-run cycle plans sitting in any lane. Empty = not frozen.

    Only files sitting DIRECTLY in the lane count — Done/ is complete and
    drafts/ is not deposited.
    """
    out = []
    for lane in decision_lanes(root):
        for f in sorted(lane.glob("*.md")):
            name = f.name
            if name.startswith(_PARKED_PREFIXES):
                continue
            if _FREEZING_RE.match(name):
                out.append(f)
    return out


def lessons_path() -> Path:
    env = os.environ.get("ELUVIAN_LESSONS")
    if env:
        return Path(env)
    gov = os.environ.get("ELUVIAN_WRAP_ROOT")
    base = Path(gov) if gov else (shop_root() / "eluvian-governance")
    return base / "LESSONS.md"


def sha_of(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _report_frozen(plans: list[Path], root: Path) -> None:
    print(f"FROZEN — {len(plans)} deposited-but-un-run cycle plan(s):", file=sys.stderr)
    for p in plans:
        print(f"  {p.relative_to(root)}", file=sys.stderr)
    print(
        "Guard (a): never append to LESSONS.md while one sits in decisions/. "
        "Dispatch the cycle to completion first, or HOLD the lessons for the next "
        "batch and RECORD the hold in the baton.",
        file=sys.stderr,
    )


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("pin", help="refuse if frozen; else emit LESSONS.md's sha")
    v = sub.add_parser("verify", help="refuse if the corpus froze or the sha moved")
    v.add_argument("--sha", required=True, help="the sha emitted by `pin`")
    args = ap.parse_args(argv)

    root = shop_root()
    lessons = lessons_path()
    if not lessons.is_file():
        print(f"no LESSONS.md at {lessons}", file=sys.stderr)
        return 3

    lanes = decision_lanes(root)
    plans = freezing_plans(root)
    if plans:
        _report_frozen(plans, root)
        return 2

    now = sha_of(lessons)
    if args.cmd == "pin":
        print(f"lanes: {len(lanes)}  frozen: no")
        print(now)
        return 0

    if now != args.sha:
        print(
            f"REFUSED — LESSONS.md moved since the pin.\n  pinned: {args.sha}\n  now   : {now}\n"
            "Another writer (this machine's session, or another machine's push) "
            "changed the file. Re-read it and re-take the pin before appending.",
            file=sys.stderr,
        )
        return 2
    print(f"lanes: {len(lanes)}  frozen: no  sha: unchanged — safe to write NOW")
    return 0


if __name__ == "__main__":
    sys.exit(main())
