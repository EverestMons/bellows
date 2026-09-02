#!/usr/bin/env python3
"""matcher.py — the drafting-stage pricing diagnostic's instrument (thread 81, first act).

Reads every committed walk register under a governance research directory and emits,
per register, the mechanical facts the diagnostic classifies:
  date (filename date, else the file's first-commit date from git), schema version,
  the plan it belongs to, its declared tier, the number of `## Walk N` headers,
  seat rows, finding rows (by lens column), and for each battery tool —
  plan_lint, cycle_check, fold_check, propagation_check, walk_register_lint —
  whether it is mentioned, the first walk section that mentions it, and how many
  lines pair the tool with a MEASURED-RUN proxy (exit / ran / BAR_MET / CONTINUE /
  CLEAN / PASS / 0 FAIL).

Then a per-tool summary against the mandate dates (DC History rows, fixed literals
below — re-derive them from DRAFTING_CYCLE.md before believing them):
  in-population = registers dated ON/AFTER the tool's mandate date;
  RECORDED = mentioned with >=1 measured-run proxy line;
  MENTIONED-UNMEASURED = mentioned, no proxy line (an attestation, not a run);
  SKIPPED = never mentioned;
  LATE = recorded/mentioned, first appearing in walk >= 1 (doctrine names walk 0
         for plan_lint's shape-stability run and the walk-0 consumer dry-run).

Usage: matcher.py <registers-dir> <out-dir>
Writes <out-dir>/registers.csv and <out-dir>/summary.txt; prints the summary.
Read-only on the registers; stdlib only; git is invoked read-only for dates.
"""
import csv
import glob
import os
import re
import subprocess
import sys
from collections import Counter

TOOLS = ["plan_lint", "cycle_check", "fold_check", "propagation_check", "walk_register_lint"]
# DC History rows that first mandate each tool (version, date) — FIXED LITERALS, re-derive.
MANDATE = {
    "plan_lint": "2026-07-23",          # v1.0
    "walk_register_lint": "2026-08-12", # v2.6
    "fold_check": "2026-08-14",         # v2.11
    "cycle_check": "2026-08-19",        # v2.12
    "propagation_check": "2026-08-21",  # v2.14
}
BIRTH = {  # first commit adding the script to bellows — FIXED LITERALS, re-derive
    "plan_lint": "2026-07-02", "walk_register_lint": "2026-08-10", "fold_check": "2026-08-14",
    "propagation_check": "2026-08-18", "cycle_check": "2026-08-19",
}
HDR = re.compile(r'^(?:#{2,3}\s*Walk\s*(\d+)\b)', re.M)
PROXY = re.compile(r'(plan_lint|cycle_check|fold_check|propagation_check|walk_register_lint)'
                   r'[^\n|]{0,80}(exit|ran|BAR_MET|CONTINUE|CLEAN|PASS|0 FAIL)')
ROW = re.compile(r'^\|\s*([A-Za-z0-9-]+)\s*\|\s*([A-Za-z0-9-]+)\s*\|\s*([^|]+?)\s*\|', re.M)
SEAT = re.compile(r'^\|\s*(scout|disc|exec|cap|seat)[^|]*\|', re.M | re.I)


def git_add_date(path):
    d = os.path.dirname(path)
    try:
        out = subprocess.run(["git", "-C", d, "log", "--diff-filter=A", "--format=%ad", "--date=short",
                              "--follow", "--", os.path.basename(path)],
                             capture_output=True, text=True, timeout=30).stdout.strip().splitlines()
        return out[-1] if out else ""
    except Exception:
        return ""


def analyse(path):
    t = open(path, encoding="utf-8", errors="replace").read()
    name = os.path.basename(path)
    dm = re.search(r'(2026-\d{2}-\d{2})', name)
    date = dm.group(1) if dm else git_add_date(path)
    date_src = "filename" if dm else "git-add"
    sm = re.search(r'schema_version:\*\*\s*`?([0-9.]+)', t)
    schema = sm.group(1) if sm else ""
    pm = re.search(r'\*\*Plan:\*\*\s*`?([^`\n]+)', t)
    plan = pm.group(1).strip() if pm else ""
    tm = re.search(r'\*\*Tier:\*\*\s*([^\n]{0,40})', t)
    tier = tm.group(1).strip() if tm else ""
    walks = [int(x) for x in HDR.findall(t)]
    rec = {"register": name, "date": date, "date_src": date_src, "schema": schema, "plan": plan,
           "tier": tier, "walk_headers": len(walks), "max_walk": max(walks) if walks else "",
           "seat_rows": len(SEAT.findall(t))}
    lens = Counter()
    for m in ROW.finditer(t):
        rid, walk, lensname = m.group(1), m.group(2), m.group(3)
        if rid.lower() in ("id", "#", "pin", "item") or set(rid) <= {"-"}:
            continue  # header row or the |---| separator row
        lens[lensname.strip()[:20]] += 1
    rec["finding_rows"] = sum(lens.values())
    rec["integration_rows"] = sum(v for k, v in lens.items() if k.lower().startswith("integration"))
    for tool in TOOLS:
        idx = t.find(tool)
        if idx < 0:
            rec[f"{tool}_first"] = ""
        else:
            before = HDR.findall(t[:idx])
            rec[f"{tool}_first"] = before[-1] if before else ("pre" if walks else "nohdr")
        rec[f"{tool}_mentions"] = t.count(tool)
        rec[f"{tool}_proxy"] = sum(1 for m in PROXY.finditer(t) if m.group(1) == tool)
    return rec


def main():
    if len(sys.argv) != 3:
        raise SystemExit("usage: matcher.py <registers-dir> <out-dir>")
    src, out = sys.argv[1], sys.argv[2]
    files = sorted(glob.glob(os.path.join(src, "walk-register-*.md")))
    if not files:
        raise SystemExit(f"no walk-register-*.md under {src}")
    os.makedirs(out, exist_ok=True)
    recs = [analyse(f) for f in files]
    cols = list(recs[0].keys())
    with open(os.path.join(out, "registers.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(recs)
    lines = [f"registers: {len(recs)}  (filename-dated {sum(1 for r in recs if r['date_src']=='filename')}, "
             f"git-dated {sum(1 for r in recs if r['date_src']=='git-add')}, undated {sum(1 for r in recs if not r['date'])})"]
    for tool in TOOLS:
        pop = [r for r in recs if r["date"] and r["date"] >= MANDATE[tool]]
        recorded = [r for r in pop if r[f"{tool}_proxy"] > 0]
        mentioned = [r for r in pop if r[f"{tool}_mentions"] > 0 and r[f"{tool}_proxy"] == 0]
        skipped = [r for r in pop if r[f"{tool}_mentions"] == 0]
        late = [r for r in pop if r[f"{tool}_first"] not in ("", "pre", "0", 0, "nohdr")]
        pre = [r for r in recs if r["date"] and r["date"] < MANDATE[tool] and r[f"{tool}_mentions"] > 0]
        lines.append(f"{tool:20s} mandate {MANDATE[tool]} (born {BIRTH[tool]}): in-population {len(pop):3d} | "
                     f"RECORDED {len(recorded):3d} | MENTIONED-UNMEASURED {len(mentioned):3d} | SKIPPED {len(skipped):3d} | "
                     f"LATE(first walk>=1) {len(late):3d} | pre-mandate mentions {len(pre)}")
    summary = "\n".join(lines)
    open(os.path.join(out, "summary.txt"), "w").write(summary + "\n")
    print(summary)


if __name__ == "__main__":
    main()
