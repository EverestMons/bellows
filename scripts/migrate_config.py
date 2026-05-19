#!/usr/bin/env python3
"""One-shot migration: split config.json into operational + secrets files.

Usage:  cd bellows && python scripts/migrate_config.py

Idempotency: safe to run multiple times. If config.json already contains
only operational keys and config.secrets.json exists, the script is a no-op.
"""

import json
import sys
from pathlib import Path

BELLOWS_ROOT = Path(__file__).parent.parent.resolve()
CONFIG_PATH = BELLOWS_ROOT / "config.json"
SECRETS_PATH = BELLOWS_ROOT / "config.secrets.json"

SECRET_KEYS = {"pushover", "tailscale_ip"}


def migrate():
    if not CONFIG_PATH.exists():
        print(f"ERROR: {CONFIG_PATH} not found")
        sys.exit(1)

    with open(CONFIG_PATH, "r") as f:
        original = json.load(f)

    secret_keys_present = SECRET_KEYS & set(original.keys())

    if not secret_keys_present and SECRETS_PATH.exists():
        print("Already migrated — config.json has no secret keys and config.secrets.json exists. No-op.")
        return

    if not secret_keys_present and not SECRETS_PATH.exists():
        print("WARNING: config.json has no secret keys but config.secrets.json does not exist.")
        print("Creating empty config.secrets.json.")
        secrets = {}
        with open(SECRETS_PATH, "w") as f:
            json.dump(secrets, f, indent=2, sort_keys=True)
            f.write("\n")
        return

    # Split keys
    operational = {}
    secrets = {}
    for key in sorted(original.keys()):
        if key in SECRET_KEYS:
            secrets[key] = original[key]
        else:
            operational[key] = original[key]

    # If config.secrets.json already exists, merge new secrets into it
    if SECRETS_PATH.exists():
        with open(SECRETS_PATH, "r") as f:
            existing_secrets = json.load(f)
        existing_secrets.update(secrets)
        secrets = existing_secrets

    # Write operational config
    with open(CONFIG_PATH, "w") as f:
        json.dump(operational, f, indent=2, sort_keys=True)
        f.write("\n")

    # Write secrets config
    with open(SECRETS_PATH, "w") as f:
        json.dump(secrets, f, indent=2, sort_keys=True)
        f.write("\n")

    print(f"Migration complete.")
    print(f"  Operational keys in config.json: {sorted(operational.keys())}")
    print(f"  Secret keys in config.secrets.json: {sorted(secrets.keys())}")


if __name__ == "__main__":
    migrate()
