#!/usr/bin/env python3
"""Gated clear tool — renames hold-<name>.md to ready-<name>.md for re-evaluation.

D-5(b) re-entry: the tool validates preconditions and renames; the LIVE
daemon's depositor re-evaluates via the existing ready- path.
"""

import os
import sys


def clear_plan(hold_path):
    """Validate preconditions and rename hold- -> ready- for depositor re-evaluation."""
    if not os.path.exists(hold_path):
        print(f"ERROR: file does not exist: {hold_path}", file=sys.stderr)
        return False

    filename = os.path.basename(hold_path)
    if not filename.startswith("hold-"):
        print(f"ERROR: file does not start with 'hold-': {filename}", file=sys.stderr)
        return False

    if not filename.endswith(".md"):
        print(f"ERROR: file does not end with '.md': {filename}", file=sys.stderr)
        return False

    hold_json = os.path.splitext(hold_path)[0] + ".hold.json"
    if not os.path.exists(hold_json):
        print(f"ERROR: sidecar does not exist: {hold_json}", file=sys.stderr)
        return False

    ready_name = "ready-" + filename[len("hold-"):]
    ready_path = os.path.join(os.path.dirname(hold_path), ready_name)
    os.rename(hold_path, ready_path)
    os.remove(hold_json)

    print(f"Renamed to ready- state: {ready_name}")
    print("Daemon will re-evaluate within 30 seconds.")
    return True


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <path-to-hold-file>", file=sys.stderr)
        sys.exit(1)
    success = clear_plan(sys.argv[1])
    sys.exit(0 if success else 1)
