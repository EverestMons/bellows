#!/usr/bin/env python3
"""fold_check — prove a fold did not change an artifact's MACHINE-READABLE state.

A fold is the only mutating act in the drafting cycle with no post-condition
(proposal 347). Its prose is written for a human reader, but plan files are also
read by regexes, so a fold can silently break a machine contract (proposal 348 —
three measured instances in one cycle, all invisible to reading).

This tool runs the readers an artifact is subject to, reduces their output to a
set of stable SIGNALS, and diffs that set against a stored pre-fold baseline.

    fold_check.py --save-baseline <artifact> [--baseline PATH]   # before folding
    fold_check.py <artifact> [--baseline PATH]                   # after folding

Exit 0 = the machine-readable state is unchanged. Exit 1 = drift (reported line
by line). Exit 2 = the check could not run (never read as a pass).

⚠️ Signals are normalized to survive INTENDED edits: line numbers are stripped,
because a fold that adds a paragraph shifts every line number below it without
changing any contract. What remains is the check identity and its message.

Read-only. Standard library only. Runs the readers as subprocesses so their exit
codes and stderr are captured exactly as a gate would see them.
"""

import argparse
import hashlib
import json
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

SCRIPTS_DIR = Path(__file__).parent.resolve()

# Volatile fragments that must NOT count as signal changes.
LINE_NO_RE = re.compile(r"\bline[= ]\d+\b", re.IGNORECASE)
COUNTS_RE = re.compile(r"\b(candidates|excluded|fired)=\d+")
DIGIT_RUN_RE = re.compile(r"\b\d{2,}\b")


def normalize(text):
    """Reduce one reader line to a stable signal string."""
    s = text.strip()
    s = LINE_NO_RE.sub("line=N", s)
    s = COUNTS_RE.sub(lambda m: f"{m.group(1)}=N", s)
    # sha/hex prefixes are stable identity; long decimal runs are not
    s = DIGIT_RUN_RE.sub(lambda m: m.group(0) if re.fullmatch(r"[0-9a-f]{6,}", m.group(0)) else "N", s)
    return s


def is_signal(line):
    """Only lines a gate or reader would ACT on are signals."""
    s = line.strip()
    if not s:
        return False
    return (
        s.startswith("WARN")
        or "WARN:" in s
        or s.startswith("ERROR")
        or s.startswith("PIN-CHECK")
        or s.startswith("FAIL")
    )


class ReaderCrashed(Exception):
    """A reader that did not RUN cannot contribute a zero (proposal 311's rule,
    applied to this tool itself: a silent reader looks identical to a clean one)."""


def run_reader(cmd):
    """Run one reader; return (exit_code, [signal, ...]).

    Raises ReaderCrashed if the reader did not actually produce a verdict — a
    traceback, or no recognizable output at all. Reporting 0 signals for a
    crashed reader would make a broken check indistinguishable from a clean
    artifact, which is the exact failure this tool exists to prevent.
    """
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    except (OSError, subprocess.SubprocessError) as e:
        raise ReaderCrashed(f"{cmd[1]}: could not run ({e})")
    out = (p.stdout or "") + "\n" + (p.stderr or "")
    if "Traceback (most recent call last)" in out:
        tail = [l for l in out.splitlines() if l.strip()][-1:] or ["<no detail>"]
        raise ReaderCrashed(f"{Path(cmd[1]).name}: traceback — {tail[0].strip()}")
    if not any(l.strip() for l in out.splitlines()):
        raise ReaderCrashed(f"{Path(cmd[1]).name}: produced NO output — cannot be read as clean")
    signals = sorted({normalize(l) for l in out.splitlines() if is_signal(l)})
    return p.returncode, signals


def readers_for(artifact):
    """Which readers is this artifact subject to? Explicit, never guessed."""
    name = artifact.name
    readers = []
    if name.startswith("walk-register-"):
        script = SCRIPTS_DIR / "walk_register_lint.py"
        if script.exists():
            readers.append(("walk_register_lint", [sys.executable, str(script), str(artifact)]))
    else:
        script = SCRIPTS_DIR / "plan_lint.py"
        if script.exists():
            readers.append(("plan_lint", [sys.executable, str(script), str(artifact)]))
    return readers


def collect(artifact):
    readers = readers_for(artifact)
    if not readers:
        return None
    state = {}
    for label, cmd in readers:
        code, signals = run_reader(cmd)   # may raise ReaderCrashed
        state[label] = {"exit": code, "signals": signals}
    return state


_META_KEY = "_meta"


def artifact_fingerprint(artifact):
    """sha256 of the artifact's bytes — the state a baseline describes."""
    return hashlib.sha256(artifact.read_bytes()).hexdigest()


def split_meta(loaded):
    """Separate provenance from reader state. Returns (readers, meta_or_None).

    Baselines saved before provenance recording have no _meta; they load as
    readers-only and their provenance is UNKNOWN, never assumed good.
    """
    meta = loaded.get(_META_KEY)
    readers = {k: v for k, v in loaded.items() if k != _META_KEY}
    return readers, meta


def baseline_path(artifact, explicit):
    if explicit:
        return Path(explicit)
    return artifact.parent / f".{artifact.name}.foldcheck.json"


def diff_state(before, after):
    """Return (appeared, vanished, exit_changes)."""
    appeared, vanished, exit_changes = [], [], []
    for label in sorted(set(before) | set(after)):
        b = before.get(label, {"exit": None, "signals": []})
        a = after.get(label, {"exit": None, "signals": []})
        bs, as_ = set(b.get("signals", [])), set(a.get("signals", []))
        appeared += [f"{label}: {s}" for s in sorted(as_ - bs)]
        vanished += [f"{label}: {s}" for s in sorted(bs - as_)]
        if b.get("exit") != a.get("exit"):
            exit_changes.append(f"{label}: exit {b.get('exit')} -> {a.get('exit')}")
    return appeared, vanished, exit_changes


def main(argv=None):
    ap = argparse.ArgumentParser(description="Diff an artifact's machine-readable state across a fold.")
    ap.add_argument("artifact")
    ap.add_argument("--baseline", default=None)
    ap.add_argument("--save-baseline", action="store_true")
    args = ap.parse_args(argv)

    artifact = Path(args.artifact)
    if not artifact.is_file():
        print(f"ERROR: artifact not found: {artifact}", file=sys.stderr)
        return 2

    try:
        state = collect(artifact)
    except ReaderCrashed as e:
        print(f"ERROR: {e}", file=sys.stderr)
        print("A reader that did not run cannot be read as a pass.", file=sys.stderr)
        return 2
    if state is None:
        print(f"ERROR: no reader applies to {artifact.name} — cannot verify", file=sys.stderr)
        return 2

    bpath = baseline_path(artifact, args.baseline)

    if args.save_baseline:
        payload = dict(state)
        payload[_META_KEY] = {
            "artifact_sha256": artifact_fingerprint(artifact),
            "saved_at": datetime.now().isoformat(timespec="seconds"),
        }
        bpath.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
        total = sum(len(v["signals"]) for v in state.values())
        print(f"BASELINE SAVED: {bpath}")
        print(f"readers={len(state)} signals={total}")
        for label in sorted(state):
            print(f"  {label}: exit={state[label]['exit']} signals={len(state[label]['signals'])}")
        return 0

    if not bpath.is_file():
        print(f"ERROR: no baseline at {bpath} — run --save-baseline BEFORE folding", file=sys.stderr)
        return 2

    try:
        loaded = json.loads(bpath.read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        print(f"ERROR: baseline unreadable ({e})", file=sys.stderr)
        return 2

    before, meta = split_meta(loaded)

    # A baseline taken from the state it is being compared against cannot observe
    # a fold: the comparison is self-referential and any CLEAN verdict is vacuous.
    # Measured 2026-09-04 (thread 134): across four fold rounds the baseline was
    # re-saved in the same commit as the folds, and CLEAN was reported three times
    # and quoted as evidence the folds changed nothing.
    if meta and meta.get("artifact_sha256"):
        if meta["artifact_sha256"] == artifact_fingerprint(artifact):
            print("FOLD-CHECK VACUOUS: the baseline was taken from THIS exact state "
                  f"(sha256 {meta['artifact_sha256'][:12]}…), so it cannot observe a fold.")
            print(f"  baseline saved: {meta.get('saved_at', 'unknown')}")
            print("  Re-save the baseline BEFORE the next fold, not after it.")
            return 2
        provenance = f"baseline sha256 {meta['artifact_sha256'][:12]}… saved {meta.get('saved_at', 'unknown')}"
    else:
        provenance = ("baseline provenance UNKNOWN — saved before provenance recording; "
                      "a CLEAN verdict from it is not evidence that a fold was observed")

    appeared, vanished, exit_changes = diff_state(before, state)

    if not (appeared or vanished or exit_changes):
        total = sum(len(v["signals"]) for v in state.values())
        print(f"FOLD-CHECK CLEAN: machine-readable state unchanged ({total} signals held)")
        print(f"  {provenance}")
        return 0

    print("FOLD-CHECK DRIFT — the fold changed the machine-readable state:")
    for s in appeared:
        print(f"  APPEARED: {s}")
    for s in vanished:
        print(f"  VANISHED: {s}")
    for s in exit_changes:
        print(f"  EXIT:     {s}")
    print(f"  {provenance}")
    print("\nIf a change is INTENDED, re-save the baseline and say so in the fold's record.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
