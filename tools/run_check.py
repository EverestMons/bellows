#!/usr/bin/env python3
"""run_check — one wrapper, every checker's verdict as a REAL exit code.

usage: run_check.py cycle <plan.md> [--accept-continue]
       run_check.py lint <plan.md>
       run_check.py propagation <plan.md>
       run_check.py register <path>

Exit 0 = the checker's OWN verdict channel says clean; 1 = it says failed;
2 = usage error or the checker itself crashed. The final line is always
`RUN_CHECK: <mode> VERDICT=PASS|FAIL — <reason>` on stdout.

Channel facts (read from the checkers' source, 2026-08-26 / 2026-09-02):
- cycle_check: verdict is the LAST STDOUT LINE (BAR_MET / CONTINUE /
  ESCALATE:*); its exit code is 0 for both BAR_MET and CONTINUE.
- plan_lint: the exit code IS the channel; WARN lines are advisory.
- walk_register_lint: per-file verdicts print on STDERR as
  `<name>\t<CONFORMANT|UNCONFORMANT>\t…`; the lint path ALWAYS exits 0.
  A PASS here additionally requires at least one CONFORMANT line — the
  positive control: absence of UNCONFORMANT alone can mean nothing was
  scanned (the negative-probe law, mechanized).
- propagation_check: exit 0 = CLEAN (no divergence found); exit 1 =
  divergence(s) reported; exit 2 = could not run (no symbol declarations
  parsed — NOT a clean result, never read as a pass).
"""
import re
import subprocess
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"


def judge_cycle(stdout, stderr, code, accept_continue=False):
    last = stdout.strip().splitlines()[-1].strip() if stdout.strip() else ""
    if last == "BAR_MET":
        return "PASS", "BAR_MET"
    if last == "CONTINUE" and accept_continue:
        return "PASS", "CONTINUE (accepted by flag)"
    if last == "CONTINUE":
        return "FAIL", "CONTINUE — bar not met (pass --accept-continue for mid-cycle use)"
    return "FAIL", f"verdict line: {last!r} (exit {code})"


def judge_lint(stdout, stderr, code):
    if code == 0:
        return "PASS", "exit 0 (WARNs, if any, are advisory)"
    return "FAIL", f"exit {code}"


def judge_propagation(stdout, stderr, rc):
    if rc == 0:
        m = re.search(r'declared symbols:\s*(\d+)', stdout)
        n = m.group(1) if m else '?'
        return "PASS", f"CLEAN over {n} symbols"
    if rc == 1:
        m = re.search(r'DIVERGENCES:\s*(\d+)', stdout)
        n = m.group(1) if m else '?'
        return "FAIL", f"{n} divergence(s)"
    if rc == 2:
        return "FAIL", "NOT RUN (exit 2: no declarations parsed)"
    return "FAIL", f"checker crashed (exit {rc})"


def judge_register(stdout, stderr, code):
    bad = [ln for ln in stderr.splitlines() if "\tUNCONFORMANT" in ln or "\tNO_TABLE" in ln]
    good = [ln for ln in stderr.splitlines() if "\tCONFORMANT" in ln]
    if bad:
        statuses = sorted({ln.split("\t")[1] for ln in bad if len(ln.split("\t")) > 1})
        label = "/".join(statuses) if statuses else "bad"
        return "FAIL", f"{len(bad)} {label} file(s): " + "; ".join(
            ln.split("\t")[0] for ln in bad)
    if not good:
        return "FAIL", ("no CONFORMANT line seen — nothing was scanned, or the "
                        "verdict channel moved (positive control failed)")
    return "PASS", f"{len(good)} file(s) CONFORMANT, 0 bad"


def main(argv):
    if len(argv) < 3:
        print(__doc__)
        return 2
    mode, target = argv[1], argv[2]
    flags = argv[3:]
    script = {"cycle": "cycle_check.py", "lint": "plan_lint.py",
              "propagation": "propagation_check.py",
              "register": "walk_register_lint.py"}.get(mode)
    if script is None:
        print(f"RUN_CHECK: unknown mode {mode!r}")
        return 2
    try:
        out = subprocess.run(
            [sys.executable, str(SCRIPTS / script), target],
            capture_output=True, text=True, timeout=120,
        )
    except Exception as e:
        print(f"RUN_CHECK: {mode} VERDICT=FAIL — checker crashed: {e}")
        return 2
    sys.stdout.write(out.stdout)
    sys.stderr.write(out.stderr)
    if mode == "cycle":
        verdict, reason = judge_cycle(out.stdout, out.stderr, out.returncode,
                                      accept_continue="--accept-continue" in flags)
    elif mode == "lint":
        verdict, reason = judge_lint(out.stdout, out.stderr, out.returncode)
    elif mode == "propagation":
        verdict, reason = judge_propagation(out.stdout, out.stderr, out.returncode)
    else:
        verdict, reason = judge_register(out.stdout, out.stderr, out.returncode)
    print(f"RUN_CHECK: {mode} VERDICT={verdict} — {reason}")
    return 0 if verdict == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
