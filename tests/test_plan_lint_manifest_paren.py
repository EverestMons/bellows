"""(h) — a parenthetical annotation in a manifest path list (thread 69).

The depositor splits writes:/reads: on COMMA, so
`ELUVIAN_PATH.md (root, absolute, own commit)` parses to
['ELUVIAN_PATH.md (root', 'absolute', 'own commit)'] — the real path MANGLED and two
garbage tokens fed to the collision queries as if they were paths. Measured on
executable-548, SHIPPED 2026-08-26.
"""
import os
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

BELLOWS_ROOT = Path(__file__).resolve().parent.parent
LINT = str(BELLOWS_ROOT / "scripts" / "plan_lint.py")


def _lint(tmp_path, writes, reads="a.py"):
    p = tmp_path / "executable-t.md"
    p.write_text(
        "# t\n\n**Date:** 2026-09-06 | **Project:** bellows\n\n"
        "## Cycle Manifest\n"
        "tier: T1\n"
        f"reads: {reads}\n"
        f"writes: {writes}\n"
        "\n## STEP 1 — do it\n"
    )
    return subprocess.run([sys.executable, LINT, str(p)],
                          capture_output=True, text=True, timeout=60)


def test_a_parenthetical_in_writes_FAILS(tmp_path):
    r = _lint(tmp_path, "ELUVIAN_PATH.md (root, absolute, own commit), b/c.md")
    assert "FAIL: (h) manifest writes" in r.stdout, r.stdout
    assert r.returncode == 1


def test_a_parenthetical_in_reads_FAILS(tmp_path):
    r = _lint(tmp_path, "a/b.md", reads="gates.py (the enforcer)")
    assert "FAIL: (h) manifest reads" in r.stdout, r.stdout


def test_repo_root_paths_are_NOT_flagged(tmp_path):
    """⛔ Thread 69's OTHER proposed half — 'no / and no .md' — was measured at 69 hits
    and ZERO true positives across 1161 corpus entries: gates.py, depositor.py,
    lifecycle.py, bellows.py, lifecycle.db are all legitimate repo-root paths.
    Shipping it would have been a 100%-false-positive rule in a BLOCKING gate."""
    r = _lint(tmp_path, "gates.py, depositor.py, lifecycle.db", reads="bellows.py")
    assert "(h)" not in r.stdout, r.stdout


def test_a_clean_path_list_is_silent(tmp_path):
    r = _lint(tmp_path, "tools/x.py, knowledge/dev-logs/y.md")
    assert "(h)" not in r.stdout, r.stdout


def test_a_declare_placeholder_is_not_flagged(tmp_path):
    """An unemitted field is the manifest check's business, not this one's."""
    r = _lint(tmp_path, "<declare>", reads="<declare>")
    assert "(h)" not in r.stdout, r.stdout


def test_it_FAILS_rather_than_WARNS(tmp_path):
    """⛔ Not a style slip. It silently disarms the two gates that protect the CEO —
    collision detection and class assignment — while every other gate stays green.
    Ruling 119: no optional gates. Zero false positives in 1161 corpus entries, and
    the only affected plan is already shipped, so nothing live is blocked."""
    r = _lint(tmp_path, "a.md (annotated)")
    assert r.returncode == 1, "a corrupting entry must not merely warn"
