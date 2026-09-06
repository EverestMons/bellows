#!/usr/bin/env python3
"""lens_order_check — the OBSERVER §2.7 appointed and nobody built.

DRAFTING_CYCLE.md §2.7 makes the per-lens commit the mechanism that renders
sequential execution PROVABLE, in its own words:

    "…PROVABLE from the record (one commit per lens), where the sequential-fold
     rule's wording alone was measurably unable to prevent batched walks (a rule
     that names its own rationalization was read, cited, and broken twice in one
     cycle — THE GAP IS AN OBSERVER, NOT WORDING)."

⛔ That observer was never built. Measured 2026-09-06: `cycle_check` contains no
`git log`, no `rev-list`, no `--count` — no commit counting of any kind — and
`check_assert_3`, whose docstring reads "Fold happened — baseline exists", checks
only that a `.foldcheck.json` FILE EXISTS. Nothing read fold ORDER. The law has
been carried by wording since, and it failed at least once undetected: finding
CR-4 of the 2026-09-04 closing-record re-read caught a FALSE ATTESTATION — the
`**Walks:**` line claimed one commit per lens for walks 1-6 and 8-12, while walks
8-12 have ONE commit each and walk 12 applied its lens-1 and lens-4 folds in a
single edit. A human found that. This tool is what should have.

⚠️ WHAT THIS MEASURES IS THE RECORD, NOT THE WORK. A walk that ran five lenses
honestly and committed once leaves no per-lens evidence, and this tool will say
so. That is the point of §2.7, not a false positive: the claim being checked is
"sequential execution is provable from the record", never "the lenses ran".

Verdicts:
    BATCHED       one commit names two or more lenses — a direct §2.7 violation
    OUT-OF-ORDER  lens numbers do not ascend within a walk
    INCOMPLETE    a CLOSED walk is missing lenses its tier requires
    UNPROVEN      a declared walk has no per-lens commits at all

Tier-aware (§1): T0 runs Lens 4 ONLY; T1 and T2 run all five. Hardcoding five
would fail every T0 plan.

Mid-cycle safe (§2.7 requires the battery runnable while rows are being added):
the highest-numbered declared walk is IN PROGRESS and is never INCOMPLETE.

    lens_order_check.py <plan-path> [--repo <dir>] [--json]

Exit 0 = the record proves compliance, or the cycle is legitimately mid-flight.
Exit 1 = a violation the record proves.
Exit 2 = the check could not run — NEVER read as a pass.
"""

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import cycle_check  # noqa: E402
import gates  # noqa: E402

# Required lens set by tier — DRAFTING_CYCLE.md §1.
#   T0 "run the integration-vs-record pass only (Lens 4, §2.4), then deposit"
#   T1 "run the full five-lens walk (§2.1–§2.5)"
#   T2 "run T1 plus the cold-reader panel (§2.6)"  — same warm lens set
REQUIRED_LENSES = {
    "T0": frozenset({4}),
    "T1": frozenset({1, 2, 3, 4, 5}),
    "T2": frozenset({1, 2, 3, 4, 5}),
}

_WALK_RE = re.compile(r"\bwalk\s+(\d+)\b", re.IGNORECASE)
_LENS_RE = re.compile(r"\blens\s+(\d+)", re.IGNORECASE)

OK = "OK"
BATCHED = "BATCHED"
OUT_OF_ORDER = "OUT-OF-ORDER"
INCOMPLETE = "INCOMPLETE"
UNPROVEN = "UNPROVEN"


def commit_record(plan_path, repo):
    """(walk, [lens...], sha, subject) per commit touching the plan, OLDEST FIRST.

    --follow because a plan is renamed twice on its way through the pipeline
    (drafts/<p>.md -> <p>.md -> Done/<p>.md), and a record that stops at the
    rename proves nothing about the walks before it.
    """
    try:
        rel = os.path.relpath(str(plan_path), str(repo))
        out = subprocess.run(
            ["git", "-C", str(repo), "log", "--follow", "--reverse",
             "--format=%H%x09%s", "--", rel],
            capture_output=True, text=True, timeout=60,
        )
    except Exception as e:
        raise RuntimeError(f"git log failed: {e}")
    if out.returncode != 0:
        raise RuntimeError(f"git log exit {out.returncode}: {out.stderr.strip()[:200]}")

    rows = []
    for line in out.stdout.strip().split("\n"):
        if "\t" not in line:
            continue
        sha, subject = line.split("\t", 1)
        w = _WALK_RE.search(subject)
        lenses = [int(x) for x in _LENS_RE.findall(subject)]
        if w and lenses:
            rows.append((int(w.group(1)), lenses, sha[:7], subject))
    return rows


def declared_walks(plan_text):
    """Walk numbers the Cycle Log itself declares — cycle_check's own parser."""
    blocks = cycle_check.extract_dc_blocks(plan_text)
    if len(blocks) != 1:
        return None
    parsed = cycle_check.parse_block(blocks[0])
    return set(parsed["walk_data"]) | set(parsed["walk_status"])


def tier_of(plan_text):
    header = gates._parse_plan_header(plan_text)
    raw = (header or {}).get("cycle_tier", "") or ""
    m = re.match(r"^(T[012])\b", str(raw).strip())
    return m.group(1) if m else None


def analyse(rows, walks, tier):
    """Return (findings, per_walk). findings is a list of (verdict, walk, detail)."""
    required = REQUIRED_LENSES.get(tier, REQUIRED_LENSES["T1"])
    per_walk = {}
    findings = []

    for walk, lenses, sha, subject in rows:
        per_walk.setdefault(walk, []).append((lenses, sha, subject))
        if len(lenses) > 1:
            findings.append((
                BATCHED, walk,
                f"{sha} names lenses {lenses} in ONE commit — §2.7 requires one "
                f"commit per lens: {subject[:70]}",
            ))

    for walk, entries in per_walk.items():
        seq = [l for lenses, _, _ in entries for l in lenses]
        if seq != sorted(seq):
            findings.append((
                OUT_OF_ORDER, walk,
                f"lens commits land in order {seq}, which does not ascend — a later "
                f"lens read the draft before an earlier lens folded",
            ))

    # A walk is IN PROGRESS if it is the furthest walk SEEN — in the Cycle Log or in
    # the commit record, whichever reaches higher. Taking only the declared maximum
    # mis-sets the boundary whenever the record runs ahead of the log, which it does:
    # register-coverage declares walks [1,2] while its commits reach walk 3.
    seen_walks = set(walks or set()) | set(per_walk)
    in_progress = max(seen_walks) if seen_walks else None
    for walk in sorted(walks or per_walk):
        if walk == 0:
            continue          # walk 0 is the context pin, not a lens walk
        if walk == in_progress:
            continue
        seen = {l for lenses, _, _ in per_walk.get(walk, []) for l in lenses}
        if not seen:
            findings.append((UNPROVEN, walk, "no per-lens commit — sequential "
                                             "execution is not provable from the record"))
        elif not required.issubset(seen):
            missing = sorted(required - seen)
            findings.append((INCOMPLETE, walk,
                             f"closed walk proves lenses {sorted(seen)}; "
                             f"{tier or 'T1'} requires {sorted(required)} — missing {missing}"))
    return findings, per_walk


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("plan")
    ap.add_argument("--repo", default=None, help="git repo holding the plan")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)

    plan_path = Path(args.plan).resolve()
    if not plan_path.is_file():
        print(f"LENS-ORDER UNRUNNABLE: no such plan {plan_path}", file=sys.stderr)
        return 2
    repo = Path(args.repo).resolve() if args.repo else plan_path.parent
    while repo != repo.parent and not (repo / ".git").exists():
        repo = repo.parent
    if not (repo / ".git").exists():
        print("LENS-ORDER UNRUNNABLE: no git repo above the plan", file=sys.stderr)
        return 2

    text = plan_path.read_text(errors="replace")
    tier = tier_of(text)
    try:
        rows = commit_record(plan_path, repo)
    except RuntimeError as e:
        print(f"LENS-ORDER UNRUNNABLE: {e}", file=sys.stderr)
        return 2
    walks = declared_walks(text)

    # ⛔ VACUITY REFUSAL. With zero lens commits there is nothing to order, and the
    # OK message ("the record proves one commit per lens, in order") would be FALSE
    # while reading as a pass — a vacuous verdict, the class this shop already named
    # (GLOSSARY `vacuous verdict`). The per-lens convention is recent: measured
    # 2026-09-06, only 75 of 653 commits touching decisions/ name a lens at all, so
    # most historical plans land here. NO-RECORD is exit 2 — could not run — never a
    # pass, following fold_check's convention.
    lens_walks = {w for w in (walks or set()) if w != 0}
    if not rows and not lens_walks:
        # Pre-walk: the Cycle Log declares no lens walk yet, so there is nothing to
        # order. N/A, and it must NOT print the OK sentence, which asserts a proof.
        print(f"BASIS: tier={tier or 'undeclared->T1'} declared_walks="
              f"{sorted(walks) if walks else '[]'} lens_commits=0")
        print("LENS-ORDER N/A — no lens walk declared and no lens commit; nothing to order yet")
        return 0
    if not rows and lens_walks:
        print(f"BASIS: tier={tier or 'undeclared->T1'} "
              f"declared_walks={sorted(walks)} lens_commits=0")
        print("LENS-ORDER NO-RECORD: the plan declares walks but NO commit names a "
              "lens, so sequential execution is neither proven nor disproven. §2.7's "
              "observer has nothing to read.", file=sys.stderr)
        return 2

    findings, per_walk = analyse(rows, walks or set(), tier)
    basis = (f"tier={tier or 'undeclared->T1'} "
             f"declared_walks={sorted(walks) if walks is not None else 'UNPARSEABLE'} "
             f"lens_commits={len(rows)} walks_with_lens_commits={sorted(per_walk)}")

    if args.json:
        print(json.dumps({"verdict": OK if not findings else "VIOLATION",
                          "basis": basis,
                          "findings": [{"verdict": v, "walk": w, "detail": d}
                                       for v, w, d in findings]}, indent=2))
    else:
        print(f"BASIS: {basis}")
        if not findings:
            print(f"LENS-ORDER OK — {len(rows)} lens commit(s) across walks "
                  f"{sorted(per_walk)}; each names one lens, ascending, and every "
                  f"closed walk carries its tier's full set")
        for v, w, d in sorted(findings, key=lambda f: (f[1], f[0])):
            print(f"{v}: walk {w} — {d}")
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
