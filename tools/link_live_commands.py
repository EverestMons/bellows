#!/usr/bin/env python3
"""Symlink vendored command files into ~/.claude/commands/.

Idempotent, backup-first, self-verifying. Derives the vendored source
from its own location so it works on any machine that has the repo.
"""

import argparse
import os
import sys
import time
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_VENDORED_DIR = _HERE.parent / "hooks" / "commands"
_TARGETS = ("wrap.md", "eluvian.md")


def _fail(msg):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(1)


def _backup_name(commands_dir, name):
    base = commands_dir / f"{name}.pre-symlink"
    if not base.exists():
        return base
    ts = time.strftime("%Y%m%d%H%M%S")
    return commands_dir / f"{name}.pre-symlink.{ts}"


def link_commands(commands_dir, vendored_dir, dry_run=False):
    commands_dir = Path(commands_dir)
    vendored_dir = Path(vendored_dir)

    for name in _TARGETS:
        src = vendored_dir / name
        if not src.exists():
            _fail(f"vendored file missing: {src} — run git pull to update your checkout")

    if dry_run:
        for name in _TARGETS:
            src = vendored_dir / name
            target = commands_dir / name
            if target.is_symlink():
                resolved = target.resolve()
                if resolved == src.resolve():
                    print(f"OK {name}: already linked → {resolved}")
                else:
                    print(f"WOULD REFUSE {name}: symlink → {resolved} (expected {src.resolve()})")
            elif target.exists():
                bk = _backup_name(commands_dir, name)
                print(f"WOULD LINK {name}: backup {target} → {bk.name}, then symlink → {src}")
            else:
                print(f"WOULD LINK {name}: symlink → {src}")
        return

    commands_dir.mkdir(parents=True, exist_ok=True)

    results = {}

    for name in _TARGETS:
        src = vendored_dir / name
        target = commands_dir / name

        if target.is_symlink():
            resolved = target.resolve()
            if resolved == src.resolve():
                results[name] = "OK"
                continue
            else:
                print(f"REFUSED {name}: symlink → {resolved} (expected {src.resolve()})")
                results[name] = "REFUSED"
                break
        elif target.exists():
            bk = _backup_name(commands_dir, name)
            os.rename(str(target), str(bk))
            os.symlink(str(src), str(target))
            results[name] = "LINKED"
        else:
            os.symlink(str(src), str(target))
            results[name] = "LINKED"

    if "REFUSED" in results.values():
        sys.exit(1)

    for name in _TARGETS:
        if name not in results:
            sys.exit(1)
        target = commands_dir / name
        src = vendored_dir / name
        if not target.is_symlink():
            _fail(f"self-verify failed: {target} is not a symlink")
        if target.resolve() != src.resolve():
            _fail(f"self-verify failed: {target} resolves to {target.resolve()}, expected {src.resolve()}")
        if target.read_bytes() != src.read_bytes():
            _fail(f"self-verify failed: byte mismatch for {name}")
        print(f"{results[name]} {name}: {target} → {src}")

    sys.exit(0)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Symlink vendored command files into ~/.claude/commands/")
    parser.add_argument("--commands-dir",
                        default=str(Path.home() / ".claude" / "commands"),
                        help="target commands directory (default: ~/.claude/commands)")
    parser.add_argument("--vendored-dir",
                        default=str(_VENDORED_DIR),
                        help="vendored source directory (default: derived from tool location)")
    parser.add_argument("--dry-run", action="store_true",
                        help="print the plan without acting")
    args = parser.parse_args()
    link_commands(args.commands_dir, args.vendored_dir, dry_run=args.dry_run)
