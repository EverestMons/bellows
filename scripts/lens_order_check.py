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

# ⛔ `lens 1/4` is TWO lenses in one commit, not lens 1. The corpus uses the slash
# form (measured 2026-09-06: `lens 1/4` x2, `lens 3/5` x1), and reading only the
# first number turned a BATCHED commit into a compliant single-lens one — the exact
# breach this tool exists to catch, hidden by its own parser.
_LENS_RE = re.compile(r"\blens\s+(\d+(?:\s*/\s*\d+)*)", re.IGNORECASE)

# `lens 3 (cont)` continues the SAME pass across two commits. §2 says "one pass per
# lens per walk"; a continuation is one pass, so it is not a repeat — but it is
# recorded, because a fold set spanning commits is what the observer must not
# silently smooth over.
_CONT_RE = re.compile(r"\(cont\.?\)|\bcontinued\b", re.IGNORECASE)

OK = "OK"
BATCHED = "BATCHED"
OUT_OF_ORDER = "OUT-OF-ORDER"
INCOMPLETE = "INCOMPLETE"
UNPROVEN = "UNPROVEN"
REPEATED = "REPEATED"


def commit_record(plan_path, repo, source="plan"):
    """(walk, [lens...], sha, subject) per commit touching the plan, OLDEST FIRST.

    --follow because a plan is renamed twice on its way through the pipeline
    (drafts/<p>.md -> <p>.md -> Done/<p>.md), and a record that stops at the
    rename proves nothing about the walks before it.
    """
    try:
        rel = os.path.relpath(str(plan_path), str(repo))
        out = subprocess.run(
            ["git", "-C", str(repo), "log", "--follow", "--reverse",
             "--format=%H%x09%cI%x09%s", "--", rel],
            capture_output=True, text=True, timeout=60,
        )
    except Exception as e:
        raise RuntimeError(f"git log failed: {e}")
    if out.returncode != 0:
        raise RuntimeError(f"git log exit {out.returncode}: {out.stderr.strip()[:200]}")

    rows = []
    for line in out.stdout.strip().split("\n"):
        if line.count("\t") < 2:
            continue
        sha, when, subject = line.split("\t", 2)
        w = _WALK_RE.search(subject)
        lenses = []
        for group in _LENS_RE.findall(subject):
            lenses.extend(int(x) for x in re.split(r"\s*/\s*", group))
        if w and lenses:
            rows.append((int(w.group(1)), lenses, sha[:7], subject, when, sha, source))
    return rows


def commit_record_paths(repo, paths):
    """ONE git log over several paths in ONE repo — git's own order, exact.

    Used when the plan and its walk register live in the same repo, which is every
    standard-pipeline plan while it is being drafted. No merge, so no tie-breaking:
    the first real run after the register became the record (thread NNN) showed a
    register-only lens 3 and a plan-only lens 4 committed in the same second, and
    the time-merge's insertion-order tie-break put 4 before 3 — a false breach the
    depositor would have held on. `--follow` is not accepted with several paths;
    renames happen only at deposit, when the plan changes repo anyway.
    """
    rels = [os.path.relpath(str(p), str(repo)) for p in paths]
    out = subprocess.run(
        ["git", "-C", str(repo), "log", "--reverse", "--format=%H%x09%cI%x09%s", "--", *rels],
        capture_output=True, text=True, timeout=60,
    )
    if out.returncode != 0:
        raise RuntimeError(f"git log exit {out.returncode}: {out.stderr.strip()[:200]}")
    rows = []
    for line in out.stdout.strip().split("\n"):
        if line.count("\t") < 2:
            continue
        sha, when, subject = line.split("\t", 2)
        w = _WALK_RE.search(subject)
        lenses = []
        for group in _LENS_RE.findall(subject):
            lenses.extend(int(x) for x in re.split(r"\s*/\s*", group))
        if w and lenses:
            rows.append((int(w.group(1)), lenses, sha[:7], subject, when, sha, "plan+register"))
    return rows


def _merge_by_time(plan_rows, reg_rows):
    """Cross-repo merge. Same-source ties keep that source's own order (git's, exact);
    a tie between DIFFERENT sources carries no ordering evidence and is ordered by lens
    — the benign reading — so it can never manufacture a breach. executable-507's 16
    same-second commits, all one source, keep their true [1, 4, 3, 5] and still fault."""
    seen=set(); a=[r for r in plan_rows if not (r[5] in seen or seen.add(r[5]))]
    b=[r for r in reg_rows if not (r[5] in seen or seen.add(r[5]))]
    out=[]; i=j=0
    while i < len(a) and j < len(b):
        if a[i][4] < b[j][4]:   out.append(a[i]); i+=1
        elif b[j][4] < a[i][4]: out.append(b[j]); j+=1
        else:                    # cross-source tie: lower lens first
            if min(a[i][1]) <= min(b[j][1]): out.append(a[i]); i+=1
            else:                              out.append(b[j]); j+=1
    return out + a[i:] + b[j:]


def _repo_of(path):
    """Nearest ancestor holding a .git, or None."""
    d = Path(path).resolve()
    d = d if d.is_dir() else d.parent
    while d != d.parent:
        if (d / ".git").exists():
            return d
        d = d.parent
    return None


def _draft_from_fold_baseline(plan_path):
    """Derive the drafting-repo draft from the plan's fold_baseline: pointer.

    Returns (draft, None) when draft.is_file(),
            (None, note) when the baseline resolves but the derived draft is missing,
            (None, None) when nothing resolved or the baseline name does not match.

    The note text is already in the form 'draft <path> not used (<reason>)' so
    callers can print 'NOTE: fold_baseline resolved; {note}' directly.
    """
    try:
        bl, _declared = cycle_check.resolve_fold_baseline(plan_path)
    except Exception:
        return None, None
    if bl is None:
        return None, None
    m = re.match(r"^\.(.*?)\.foldcheck\.json$", bl.name)
    if not m:
        return None, None
    draft = bl.parent / m.group(1)
    if not draft.is_file():
        return None, f"draft {draft} not used (missing)"
    return draft, None


def register_commit_record(plan_text, plan_path):
    """Lens commits recorded against the plan's WALK REGISTER, in ITS repo.

    ⛔ THE REGISTER IS THE RECORD, and reading only the plan file lost it twice.
    (1) A DRY lens folds nothing into the plan, so it leaves no plan commit — the
    observer reported INCOMPLETE for a walk that genuinely ran all five lenses, and
    since BAR_MET requires a dry walk it was blind to precisely the closing walk a
    fabricated close would imitate (thread 165). (2) The standard pipeline drafts in
    governance and deposits into a project, so a deposited plan's lens commits live
    in ANOTHER REPO and `git log` over the deposited path returns nothing — measured
    2026-09-07 at 28 commits in eluvian-governance against 0 in tuyere, which is why
    lens order was provable for 0 of 19 plans at the bar (thread 163).

    The register ref survives BOTH: it is a field in the plan, it points at the
    drafting repo, and a dry lens still appends its row to it. Resolution reuses
    `cycle_check._resolve_register_ref` — the ONE resolver — rather than growing a
    second, which is the defect class this shop has already paid for twice.
    """
    blocks = cycle_check.extract_dc_blocks(plan_text or "")
    if len(blocks) != 1:
        return [], None
    ref = cycle_check.parse_block(blocks[0]).get("walk_register_ref")
    if not ref:
        return [], None
    resolved = cycle_check._resolve_register_ref(ref, Path(plan_path))
    if not resolved:
        return [], None
    repo = _repo_of(resolved)
    if not repo:
        return [], None
    try:
        return commit_record(resolved, repo, source="register"), resolved
    except RuntimeError:
        return [], resolved


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

    for walk, lenses, sha, subject, *_meta in rows:
        per_walk.setdefault(walk, []).append((lenses, sha, subject))
        if len(lenses) > 1:
            findings.append((
                BATCHED, walk,
                f"{sha} names lenses {lenses} in ONE commit — §2.7 requires one "
                f"commit per lens: {subject[:70]}",
            ))

    for walk, entries in per_walk.items():
        seq = [l for lenses, _, _ in entries for l in lenses]

        # §2: "one pass per lens per walk … Re-run a lens only on a SUBSEQUENT walk."
        # A `(cont)` commit continues one pass and is not a repeat.
        counted = [l for lenses, _, subj in entries
                   for l in lenses if not _CONT_RE.search(subj)]
        repeats = sorted({l for l in counted if counted.count(l) > 1})
        if repeats:
            findings.append((
                REPEATED, walk,
                f"lens {repeats} passed more than once in one walk — §2 allows one "
                f"pass per lens per walk, and a re-run belongs on a SUBSEQUENT walk",
            ))

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
    # ⛔ THE UNION, not the declared set (thread 164). This loop used to read
    # `sorted(walks or per_walk)`, so a declared-walks set took precedence and the
    # commit record was never consulted for WHICH walks to check. Measured on a real
    # plan: deleting one walk's STATUS bullet from the Cycle Log returned NO FINDINGS
    # while the commits proving that walk ran sat untouched in history — Ruling 119's
    # "a gate reading a declaration is defeated by silence", inside the observer built
    # to enforce lens order. The correct union was already computed one line above and
    # used only for the in-progress boundary.
    for walk in sorted(seen_walks):
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
        # ⛔ UNION the plan's record with the WALK REGISTER's (threads 163 + 165).
        # Deduplicated by FULL SHA — a commit touching both files appears in both
        # logs and would otherwise read as a REPEATED lens — then ordered by commit
        # TIME, so a merged sequence across two repos still reflects the order the
        # passes actually happened in rather than the order the logs were read.
        reg_rows, reg_path = register_commit_record(plan_path.read_text(errors="replace"),
                                                   plan_path)
        if reg_rows:
            reg_repo = _repo_of(reg_path) if reg_path else None
            if reg_repo and reg_repo.resolve() == Path(repo).resolve():
                rows = commit_record_paths(repo, [plan_path, reg_path])   # ONE log, git's order
                record_src = f"plan+register, one log ({reg_path.name})"
            else:
                # Cross-repo: try to reach the drafting-repo's one log via fold_baseline:
                record_src = f"plan+register, merged by time ({reg_path.name})"
                rows = _merge_by_time(rows, reg_rows)
                draft = None
                note = None
                try:
                    draft, note = _draft_from_fold_baseline(plan_path)
                    if draft:
                        draft_repo = _repo_of(draft)
                        if draft_repo and draft_repo.resolve() == reg_repo.resolve():
                            draft_text = draft.read_text(errors="replace")
                            draft_blocks = cycle_check.extract_dc_blocks(draft_text)
                            plan_blocks = cycle_check.extract_dc_blocks(text)
                            if len(draft_blocks) == 1 and len(plan_blocks) == 1:
                                draft_ref = cycle_check.parse_block(
                                    draft_blocks[0]).get("walk_register_ref")
                                plan_ref = cycle_check.parse_block(
                                    plan_blocks[0]).get("walk_register_ref")
                                if draft_ref and plan_ref and draft_ref == plan_ref:
                                    rows = commit_record_paths(
                                        reg_repo, [draft, reg_path])
                                    record_src = (
                                        f"draft+register, one log via fold_baseline"
                                        f" ({draft.name})"
                                    )
                                    note = None
                                else:
                                    note = (f"draft {draft.name} not used "
                                            f"(register ref differs)")
                            else:
                                note = f"draft {draft} not used (unreadable)"
                        else:
                            note = f"draft {draft.name} not used (other repo)"
                except OSError:
                    note = (f"draft {draft.name if draft is not None else '<unresolved>'}"
                            f" not used (unreadable)")
                if note:
                    print(f"NOTE: fold_baseline resolved; {note}", file=sys.stderr)
        else:
            record_src = "plan only — no resolvable walk register"
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
        # ⛔ NO-RECORD HOLDS — CEO ruling 2026-09-07 (thread 177), DRAFTING_CYCLE v2.26.
        # This used to exit 2 and hold nothing, on the ratified reasoning that of the
        # 19 plans at the bar 18 were NO-RECORD and "holding on absence would stop
        # every deposit". That premise was measured while the observer was INERT —
        # it read only the plan file, and the record lived in the drafting repo — so
        # NO-RECORD then meant "cannot see", not "nothing there". Since the register
        # became the record (thread 163) it means what it says: the plan declares lens
        # walks and NO commit anywhere proves one. That is the fabricated-close shape,
        # and it is held UNCONDITIONALLY — no date key, no register key, nothing to
        # declare one's way past (Ruling 119). Measured at the ruling: 12 of the 13
        # plans clearing the bar that day would hold; live lanes held 0, so the cost
        # fell on re-deposits only. Pre-walk plans (no lens walk declared) and T0
        # still return N/A above and are untouched. Exit 1 is what the depositor
        # holds on; the verdict word is kept so the reason stays legible.
        print(f"BASIS: source=none tier={tier or 'undeclared->T1'} "
              f"declared_walks={sorted(walks)} lens_commits=0")
        print("NO-RECORD: the plan declares lens walks but NO commit in the plan's "
              "repo or its walk register names a lens — sequential execution is "
              "unproven, and since DRAFTING_CYCLE v2.26 that HOLDS (thread 177).")
        return 1

    findings, per_walk = analyse(rows, walks or set(), tier)
    basis = (f"source={record_src} "
             f"tier={tier or 'undeclared->T1'} "
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
