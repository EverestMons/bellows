#!/usr/bin/env python3
"""One-shot migration: rename canonical verdict-*.md orphans back to processed-verdict-*.md.

Run once to clean up existing orphans in verdicts/resolved/ that have no paired
verdict-pending-* plan in any watched decisions/ directory.

Authority: 2026-05-22 pre-scan-orphan-warn-flood diagnostic.
"""

import json
import os
import re
import shutil
from pathlib import Path

# Use the main repo root (config.json and verdicts/ are gitignored, only in main repo)
BELLOWS_ROOT = Path(__file__).parent.parent.resolve()
MAIN_REPO = Path("/Users/marklehn/Developer/GitHub/bellows")
CONFIG_PATH = MAIN_REPO / "config.json"
RESOLVED_DIR = MAIN_REPO / "verdicts" / "resolved"

def main():
    with open(CONFIG_PATH) as f:
        config = json.load(f)
    watched_projects = config.get("watched_projects", [])

    if not RESOLVED_DIR.is_dir():
        print(f"resolved/ directory not found: {RESOLVED_DIR}")
        return

    orphans_found = 0
    orphans_renamed = 0
    skipped_collision = 0
    skipped_no_slug = 0

    for fname in sorted(os.listdir(RESOLVED_DIR)):
        # Only process canonical verdict-*.md (not processed-verdict-*, verdict-request-*, etc.)
        if not fname.startswith("verdict-") or not fname.endswith(".md"):
            continue
        if fname.startswith("verdict-request-"):
            continue

        # Extract slug using main-loop regex
        match = re.match(r"^verdict-(.+)-step-(\d+)\.md$", fname)
        if not match:
            skipped_no_slug += 1
            print(f"  SKIP (no slug match): {fname}")
            continue

        plan_slug = match.group(1)

        # Check for paired verdict-pending-* plan in watched directories
        has_paired_plan = False
        for decisions_path in watched_projects:
            if not os.path.isdir(decisions_path):
                continue
            for pname in os.listdir(decisions_path):
                if pname.startswith("verdict-pending-") and plan_slug in pname:
                    has_paired_plan = True
                    break
            if has_paired_plan:
                break

        if has_paired_plan:
            print(f"  ACTIVE (has paired plan): {fname}")
            continue

        # This is an orphan — rename to processed-verdict-* form
        orphans_found += 1
        processed_name = f"processed-{fname}"
        processed_path = os.path.join(RESOLVED_DIR, processed_name)

        if os.path.exists(processed_path):
            # Both forms exist (ping-pong artifact). Remove the canonical duplicate.
            os.remove(os.path.join(RESOLVED_DIR, fname))
            orphans_renamed += 1
            print(f"  REMOVED duplicate canonical (processed- form already exists): {fname}")
            continue

        shutil.move(os.path.join(RESOLVED_DIR, fname), processed_path)
        orphans_renamed += 1
        print(f"  RENAMED: {fname} → {processed_name}")

    print()
    print(f"--- Migration Summary ---")
    print(f"Orphans found:       {orphans_found}")
    print(f"Orphans renamed:     {orphans_renamed}")
    print(f"Skipped (collision): {skipped_collision}")
    print(f"Skipped (no slug):   {skipped_no_slug}")


if __name__ == "__main__":
    main()
