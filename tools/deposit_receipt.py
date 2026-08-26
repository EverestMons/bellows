#!/usr/bin/env python3
"""Deposit receipt writer — attests the watcher was armed at deposit time.

Run by the Planner BEFORE staging the plan as ready-<slug>.md.
Writes a slug-keyed receipt file to bellows/receipts/.

Ordering contract: receipt BEFORE staging. The daemon claims within seconds
of a file becoming claimable; writing the receipt first ensures no claim can
precede attestation.
"""

import argparse
import hashlib
import subprocess
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path

_HERE = os.path.dirname(os.path.abspath(__file__))
_BELLOWS_ROOT = os.path.dirname(_HERE)
_RECEIPTS_DIR = os.path.join(_BELLOWS_ROOT, "receipts")
_VALID_SESSION_ID = re.compile(r"^[A-Za-z0-9-]+$")


def _fail(msg):
    print(f"ERROR: {msg}", file=sys.stderr)
    return False


def _watched_decisions_dirs():
    try:
        cfg_path = os.path.join(_BELLOWS_ROOT, "config.json")
        with open(cfg_path) as f:
            cfg = json.load(f)
        paths = cfg.get("watched_projects", [])
        if isinstance(paths, list):
            return [str(p) for p in paths if isinstance(p, str)]
    except Exception:
        pass
    return []


def _is_in_watched_tree(plan_path, watched_dirs):
    abs_plan = os.path.abspath(plan_path)
    for d in watched_dirs:
        abs_d = os.path.abspath(d)
        if abs_plan.startswith(abs_d + os.sep) or os.path.dirname(abs_plan) == abs_d:
            return True
    return False


def _spawn_watcher(claimable_name):
    """Spawn the session-independent gate watcher, detached. Returns pid or None."""
    watcher = os.path.join(_HERE, "gate_watcher.py")
    try:
        p = subprocess.Popen(
            [sys.executable, watcher, claimable_name],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            start_new_session=True,
        )
        return p.pid
    except Exception:
        return None


def write_receipt(plan_path, session_id, spawn_watcher=True):
    if not os.path.exists(plan_path):
        return _fail(f"plan file does not exist: {plan_path}")

    if not session_id or not isinstance(session_id, str):
        return _fail("session_id missing or invalid (must match [A-Za-z0-9-]+)")
    session_id = session_id.strip()
    if not _VALID_SESSION_ID.match(session_id):
        return _fail("session_id missing or invalid (must match [A-Za-z0-9-]+)")

    basename = os.path.basename(plan_path)
    slug = basename
    if slug.startswith("ready-"):
        slug = slug[len("ready-"):]
    elif slug.startswith("hold-"):
        slug = slug[len("hold-"):]
    if slug.endswith(".md"):
        slug = slug[:-len(".md")]
    if not slug:
        return _fail(f"could not derive slug from filename: {basename}")

    plan_bytes = Path(plan_path).read_bytes()
    content_hash = hashlib.sha256(plan_bytes).hexdigest()
    hash12 = content_hash[:12]

    abs_plan = os.path.abspath(plan_path)
    watched = _watched_decisions_dirs()
    if watched and not _is_in_watched_tree(plan_path, watched):
        print(f"Note: {abs_plan} is outside watched project trees (informational — proceeding)")

    os.makedirs(_RECEIPTS_DIR, exist_ok=True)

    # Duplicate check: same slug+hash in ACTIVE receipts/ only (not archived/)
    for existing in os.listdir(_RECEIPTS_DIR):
        existing_path = os.path.join(_RECEIPTS_DIR, existing)
        if os.path.isdir(existing_path) or not existing.endswith(".json"):
            continue
        try:
            with open(existing_path) as f:
                data = json.load(f)
            if data.get("slug") == slug and data.get("content_hash") == content_hash:
                return _fail(f"receipt already exists for slug={slug} hash={hash12} — duplicate deposit")
        except Exception:
            continue

    receipt_name = f"receipt-{slug}-{session_id}-{hash12}.json"
    receipt_path = os.path.join(_RECEIPTS_DIR, receipt_name)

    watcher_note = "gate-watcher armed in depositing session"
    if spawn_watcher:
        pid = _spawn_watcher(slug + ".md")
        if pid is not None:
            watcher_note = f"gate_watcher.py spawned detached (pid {pid}); log: logs/watch/{slug}.md.log"

    receipt = {
        "slug": slug,
        "content_hash": content_hash,
        "session_id": session_id,
        "armed_at": datetime.now().isoformat(),
        "watcher": watcher_note,
        "attestation_boundary": (
            "This receipt proves the watcher was ARMED at write time. "
            "It does NOT prove the watcher stayed alive. Liveness of a "
            "session-local monitor is not externally verifiable."
        ),
    }

    with open(receipt_path, "w") as f:
        json.dump(receipt, f, indent=2)
        f.write("\n")

    print(f"Receipt written: {os.path.abspath(receipt_path)} — watcher armed (not a liveness claim)")
    return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Write a deposit watcher receipt")
    parser.add_argument("plan_path", help="path to the plan file (draft or ready-)")
    parser.add_argument("session_id", help="depositing session's id ([A-Za-z0-9-]+)")
    parser.add_argument("--no-spawn", action="store_true",
                        help="skip spawning the detached gate watcher")
    args = parser.parse_args()
    success = write_receipt(args.plan_path, args.session_id,
                            spawn_watcher=not args.no_spawn)
    sys.exit(0 if success else 1)
