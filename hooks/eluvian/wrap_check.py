#!/usr/bin/env python3
"""
Eluvian session-wrap verifier — the single source of truth for "is the wrap done?"

Used by two hooks:
  - Stop hook (wrap_stop_hook.sh): while a wrap is in progress, HARD-BLOCKS the
    turn from ending until every check below passes.
  - SessionStart hook (wrap_debt_hook.sh): at the start of a new session, reports
    leftover wrap debt from a prior (un-wrapped) session.

Design principles (mirroring the memory lessons this is meant to enforce):
  - FAIL-OPEN on checker error: a bug in THIS script must never trap a session.
    Any unexpected exception -> exit 0 with a printed warning.
  - FAIL-CLOSED on genuine incompleteness: if the ritual is verifiably not done,
    exit 1 with a precise, actionable checklist.
  - Checks assert the ritual's DELTAS, not full repo cleanliness (the root carries
    unrelated untracked files by design — see the wrap ritual memory).

Exit codes:
  0  = wrap complete (or fail-open on internal error)
  1  = wrap incomplete; stdout lists exactly what remains

Ritual reference: eluvian-session-wrap-ritual memory. Four repos:
  1. project repos  — untracked knowledge/decisions/Done/ plan files committed
  2. bellows        — verdicts/resolved/ committed AND pushed
  3. governance root— baton refreshed+committed, bellows gitlink bumped, 3b done
  4. memory repo    — committed AND pushed (if touched)
"""
from __future__ import annotations

import datetime
import json
import os
import re
import sqlite3
import subprocess
import sys
from datetime import datetime as dt
from pathlib import Path

# Machine layouts differ (shop machine: ~/Developer/GitHub; Mac mini:
# ~/Developer/eluvian-governance). Same override names as the arm/stop hooks.
ROOT = Path(os.environ.get("ELUVIAN_WRAP_ROOT")
            or "/Users/marklehn/Developer/GitHub")
BELLOWS = ROOT / "bellows"
RECEIPTS = BELLOWS / "receipts"
LIFECYCLE_DB = BELLOWS / "lifecycle.db"
MEMORY = Path(os.environ.get("ELUVIAN_WRAP_MEMORY")
              or "/Users/marklehn/.claude/projects/-Users-marklehn-Developer-GitHub/memory")
BATON = ROOT / "shop_next_session.md"


def git(repo: Path, *args) -> str:
    """Run a git command in `repo`, return stdout stripped. '' on any failure."""
    try:
        out = subprocess.run(
            ["git", "-C", str(repo), *args],
            capture_output=True, text=True, timeout=30,
        )
        return out.stdout.strip()
    except Exception:
        return ""


def porcelain(repo: Path, pathspec: str | None = None) -> list[str]:
    """Lines of `git status --porcelain` (optionally scoped to a pathspec)."""
    args = ["status", "--porcelain"]
    if pathspec:
        args += ["--", pathspec]
    out = git(repo, *args)
    return [ln for ln in out.splitlines() if ln.strip()]


def unpushed_count(repo: Path) -> int | None:
    """Commits ahead of upstream. None if no upstream configured (can't tell)."""
    up = git(repo, "rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}")
    if not up:
        return None
    n = git(repo, "rev-list", "--count", "@{u}..HEAD")
    try:
        return int(n)
    except ValueError:
        return None


def project_done_dirs() -> list[Path]:
    """Every <repo>/knowledge/decisions/Done directory under the root."""
    return sorted(ROOT.glob("*/knowledge/decisions/Done"))


def _find_newest_sweep_line(baton_text):
    for line in baton_text.splitlines():
        stripped = line.strip().lstrip(">").strip()
        if stripped.lower().startswith("lessons-swept:"):
            return stripped
    return None


def _extract_sid(sweep_line):
    m = re.search(r'\[sid:\s*([A-Za-z0-9-]+)\]', sweep_line)
    return m.group(1) if m else None


def check(session_id: str | None = None, caller: str = "stop") -> list[str]:
    """Return a list of failure messages. Empty list == wrap complete."""
    fails: list[str] = []
    today = datetime.date.today().isoformat()

    # --- Step 1: project repos — no UNTRACKED completed plans in Done/ ----------
    for done in project_done_dirs():
        repo = done.parents[2]  # <repo>/knowledge/decisions/Done -> <repo>
        # untracked (??) or modified files scoped to the Done/ dir
        rel = "knowledge/decisions/Done"
        dirty = porcelain(repo, rel)
        if dirty:
            fails.append(
                f"[1/project] {repo.name}: {len(dirty)} uncommitted file(s) in "
                f"{rel}/ — commit completed plan files."
            )

    # --- Step 2: bellows — verdicts committed AND pushed -----------------------
    v_dirty = porcelain(BELLOWS, "verdicts/resolved")
    if v_dirty:
        fails.append(
            f"[2/bellows] {len(v_dirty)} uncommitted file(s) under "
            f"verdicts/resolved/ — commit consumed verdicts."
        )
    r_dirty = porcelain(BELLOWS, "receipts")
    if r_dirty:
        fails.append(
            f"[2/bellows] {len(r_dirty)} uncommitted file(s) under "
            f"receipts/ — commit receipts."
        )
    b_ahead = unpushed_count(BELLOWS)
    if b_ahead:
        fails.append(f"[2/bellows] {b_ahead} commit(s) not pushed — push bellows.")

    # --- Step 3: governance root — baton + gitlink + 3b lessons sweep ----------
    # baton must be committed (not sitting modified/untracked)
    baton_dirty = porcelain(ROOT, "shop_next_session.md")
    if baton_dirty:
        fails.append("[3/root] shop_next_session.md is uncommitted — commit the refreshed baton.")
    # bellows gitlink must be committed (not a dangling submodule bump)
    gitlink_dirty = porcelain(ROOT, "bellows")
    if gitlink_dirty:
        fails.append("[3/root] bellows gitlink is uncommitted — `git add bellows` and commit the bump.")
    r_ahead = unpushed_count(ROOT)
    if r_ahead:
        fails.append(f"[3/root] {r_ahead} commit(s) not pushed — push governance root.")
    # 3b: the MOST-SKIPPED step. Force an explicit affirmation in today's baton.
    try:
        baton_text = BATON.read_text(errors="replace") if BATON.exists() else ""
    except Exception:
        baton_text = ""
    if caller == "debt" or not session_id:
        swept_ok = any(
            line.strip().lstrip(">").strip().lower().startswith("lessons-swept:")
            and today in line
            for line in baton_text.splitlines()
        )
        if not swept_ok:
            fails.append(
                f"[3b/lessons] No `Lessons-swept: {today}` line in the baton. Do the 3b "
                f"transferable-lessons sweep AS ITS OWN ACT (distinct from the arc note), "
                f"then add a `Lessons-swept: {today} [sid: <session-prefix-8>] — "
                f"<delta, or 'none'>` line to shop_next_session.md and commit."
            )
    else:
        newest = _find_newest_sweep_line(baton_text)
        if newest is None:
            fails.append(
                f"[3b/lessons] No Lessons-swept: line found in the baton. Do the 3b "
                f"transferable-lessons sweep AS ITS OWN ACT (distinct from the arc note), "
                f"then add a `Lessons-swept: {today} [sid: {session_id[:8]}] — "
                f"<delta, or 'none'>` line to shop_next_session.md and commit."
            )
        else:
            sid_in_line = _extract_sid(newest)
            if sid_in_line and session_id.startswith(sid_in_line) and len(sid_in_line) >= 8:
                pass
            elif sid_in_line:
                fails.append(
                    f"[3b/lessons] The newest Lessons-swept: line belongs to session "
                    f"{sid_in_line}, not this session ({session_id[:8]}). Do the 3b "
                    f"transferable-lessons sweep AS ITS OWN ACT (distinct from the arc "
                    f"note), then add a `Lessons-swept: {today} [sid: {session_id[:8]}] "
                    f"— <delta, or 'none'>` line to shop_next_session.md and commit."
                )
            else:
                fails.append(
                    f"[3b/lessons] The newest Lessons-swept: line has no session-id key "
                    f"(historical format). Do the 3b transferable-lessons sweep AS ITS "
                    f"OWN ACT (distinct from the arc note), then add a "
                    f"`Lessons-swept: {today} [sid: {session_id[:8]}] — <delta, or "
                    f"'none'>` line to shop_next_session.md and commit."
                )

    # --- Step 4: memory repo — committed AND pushed (if touched) ---------------
    m_dirty = porcelain(MEMORY)
    if m_dirty:
        fails.append(
            f"[4/memory] {len(m_dirty)} uncommitted change(s) in the memory repo — "
            f"commit memories + MEMORY.md."
        )
    m_ahead = unpushed_count(MEMORY)
    if m_ahead:
        fails.append(f"[4/memory] {m_ahead} commit(s) not pushed — push the memory repo.")

    # --- Step 2r: deposit receipts — every own-session deposit attested --------
    _check_receipts(session_id, fails)

    return fails


def _check_receipts(session_id: str | None, fails: list[str]) -> None:
    """[2r/receipts] group: blocking arm (own session) + warning arm (24h)."""
    # SKIP: receipts dir absent or unreadable
    if not RECEIPTS.is_dir():
        print("[2r/receipts] SKIPPED — receipts directory absent.")
        return
    try:
        receipt_files = list(RECEIPTS.iterdir())
    except OSError:
        print("[2r/receipts] SKIPPED — receipts directory unreadable.")
        return

    # Load all receipt data (active + archived for warning arm)
    active_receipts = []
    for p in receipt_files:
        if p.is_dir() or not p.suffix == ".json":
            continue
        try:
            data = json.loads(p.read_text())
            if not isinstance(data, dict):
                print(f"[2r/receipts] WARNING: malformed receipt file {p.name} — skipped (not a failure).")
                continue
            # Field validation: slug, content_hash, session_id, armed_at must be present and parseable
            r_slug = data.get("slug")
            r_hash = data.get("content_hash")
            r_sid = data.get("session_id")
            r_armed = data.get("armed_at")
            if not all(isinstance(v, str) and v for v in [r_slug, r_hash, r_sid]):
                print(f"[2r/receipts] WARNING: malformed receipt file {p.name} — skipped (not a failure).")
                continue
            if r_armed:
                try:
                    dt.fromisoformat(r_armed)
                except (ValueError, TypeError):
                    print(f"[2r/receipts] WARNING: malformed receipt file {p.name} — skipped (not a failure).")
                    continue
            active_receipts.append(data)
        except (json.JSONDecodeError, OSError):
            print(f"[2r/receipts] WARNING: malformed receipt file {p.name} — skipped (not a failure).")

    # Also load archived receipts (for warning arm only)
    archived_receipts = []
    archived_dir = RECEIPTS / "archived"
    if archived_dir.is_dir():
        try:
            for p in archived_dir.iterdir():
                if p.is_dir() or not p.suffix == ".json":
                    continue
                try:
                    data = json.loads(p.read_text())
                    if isinstance(data, dict) and data.get("content_hash"):
                        archived_receipts.append(data)
                except Exception:
                    pass
        except OSError:
            pass

    all_receipt_hashes = {r.get("content_hash") for r in active_receipts + archived_receipts if r.get("content_hash")}

    # Open lifecycle.db read-only for clearance cross-check
    db_available = False
    db_conn = None
    try:
        db_conn = sqlite3.connect(f"file:{LIFECYCLE_DB}?mode=ro", uri=True)
        db_available = True
    except Exception:
        print("[2r/receipts] SKIPPED — lifecycle.db not readable for clearance cross-check.")

    # --- Hold sidecars: slug set from all watched project trees ---
    hold_slugs = set()
    try:
        for sidecar in ROOT.glob("*/knowledge/decisions/*.hold.json"):
            name = sidecar.name
            if name.startswith("hold-") and name.endswith(".hold.json"):
                hold_slug = name[len("hold-"):-len(".hold.json")]
                if hold_slug:
                    hold_slugs.add(hold_slug)
    except OSError:
        pass

    # --- BLOCKING arm: own-session receipts vs clearances/hold-sidecars ---
    if session_id:
        own_receipts = [r for r in active_receipts if r.get("session_id") == session_id]
        matchless_count = 0
        for r in own_receipts:
            r_hash = r.get("content_hash", "")
            r_slug = r.get("slug", "")
            r_armed = r.get("armed_at", "")
            matched = False
            # Check clearance: SELECT 1 FROM clearances WHERE content_hash = ? (NO consumed_at filter)
            if db_available and db_conn and r_hash:
                try:
                    row = db_conn.execute(
                        "SELECT 1 FROM clearances WHERE content_hash = ?",
                        (r_hash,),
                    ).fetchone()
                    if row:
                        matched = True
                except Exception:
                    pass
            # Check hold sidecar
            if not matched and r_slug in hold_slugs:
                matched = True
            if not matched:
                # Pending-evaluation grace: armed_at younger than 10 minutes → note, not failure
                grace = False
                if r_armed:
                    try:
                        armed_dt = dt.fromisoformat(r_armed)
                        age_seconds = (dt.now() - armed_dt).total_seconds()
                        if age_seconds < 600:
                            grace = True
                    except (ValueError, TypeError):
                        pass
                if grace:
                    print(f"[2r/receipts] Note: receipt for {r_slug} is pending evaluation "
                          f"(armed <10 min ago) — not blocking.")
                else:
                    matchless_count += 1
        if matchless_count > 0:
            fails.append(
                f"[2r/receipts] {matchless_count} receipt(s) from this session match no "
                f"clearance or hold — stale, mistyped, or abandoned deposit. If the deposit "
                f"was deliberately abandoned, remove the receipt file — that is the sanctioned disarm."
            )
        elif own_receipts:
            print(f"[2r/receipts] OK — {len(own_receipts)} own-session receipt(s), all matched.")
        else:
            print(f"[2r/receipts] OK — no deposits in this session (session {session_id}).")
    else:
        print("[2r/receipts] SKIPPED (blocking arm) — no session_id provided; "
              "receipt check requires session context.")

    # --- WARNING arm: 24h lookback, any-session, non-blocking ---
    if db_available and db_conn:
        try:
            cutoff = (dt.now() - datetime.timedelta(hours=24)).isoformat()
            rows = db_conn.execute(
                "SELECT content_hash FROM clearances WHERE cleared_at > ?",
                (cutoff,),
            ).fetchall()
            unattested = [row[0] for row in rows if row[0] not in all_receipt_hashes]
            if unattested:
                print(f"[2r/receipts] WARNING: {len(unattested)} cleared deposit(s) in the "
                      f"last 24h without a receipt — arm a watcher and write a receipt at every deposit.")
        except Exception:
            pass

    if db_conn:
        try:
            db_conn.close()
        except Exception:
            pass


def main() -> int:
    session_id = sys.argv[1] if len(sys.argv) > 1 and sys.argv[1] else None
    caller = sys.argv[2] if len(sys.argv) > 2 and sys.argv[2] else "stop"
    try:
        fails = check(session_id, caller)
    except Exception as exc:  # FAIL-OPEN — a broken checker must never trap
        print(f"wrap_check: internal error, failing open (allowing): {exc}")
        return 0
    if not fails:
        print("wrap_check: OK — all four repos wrapped.")
        return 0
    print("SESSION WRAP INCOMPLETE — the following steps are not verifiably done:\n")
    for f in fails:
        print(f"  ✗ {f}")
    print("\nComplete these, then this lock clears automatically.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
