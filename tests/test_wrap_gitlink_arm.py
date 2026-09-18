"""Tests for the [3/root] gitlink arm — published-tip check (plan 100128).

One test per MUST-PRESERVE observer, in order A–I and L.
"""
import sqlite3
import subprocess
import time
from pathlib import Path

import pytest

BELLOWS_ROOT = Path(__file__).resolve().parent.parent


# ---------------------------------------------------------------------------
# Shared infrastructure
# ---------------------------------------------------------------------------

def _init_lifecycle_db(db_path):
    conn = sqlite3.connect(str(db_path))
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("""CREATE TABLE IF NOT EXISTS id_sequence (
        next_id INTEGER NOT NULL DEFAULT 500)""")
    conn.execute("""CREATE TABLE IF NOT EXISTS clearances (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        plan_filename TEXT NOT NULL,
        content_hash TEXT NOT NULL UNIQUE,
        cleared_by TEXT NOT NULL,
        cleared_at TEXT NOT NULL,
        consumed_at TEXT,
        source TEXT)""")
    conn.commit()
    conn.close()


def _g(root, *args):
    """Run git in root with hermetic identity. Raises on non-zero exit."""
    r = subprocess.run(
        ["git", "-c", "user.name=test", "-c", "user.email=t@t",
         "-C", str(root), *args],
        capture_output=True, text=True,
    )
    if r.returncode != 0:
        raise RuntimeError(f"git {args!r} in {root}: {r.stderr.strip()}")
    return r.stdout.strip()


def _make_source(path):
    """Init a source repo with one commit. Returns HEAD sha (40 chars)."""
    path.mkdir(parents=True, exist_ok=True)
    subprocess.run(["git", "init", str(path)], check=True, capture_output=True)
    (path / "file.txt").write_text("v1")
    _g(path, "add", "file.txt")
    _g(path, "commit", "-m", "init")
    return subprocess.run(
        ["git", "-C", str(path), "rev-parse", "HEAD"],
        capture_output=True, text=True, check=True,
    ).stdout.strip()


def _advance_source(path):
    """Make one more commit in an existing source repo. Returns new HEAD sha."""
    txt = path / "file.txt"
    txt.write_text((txt.read_text() if txt.exists() else "") + "\nv2")
    _g(path, "add", "file.txt")
    _g(path, "commit", "-m", "advance")
    return subprocess.run(
        ["git", "-C", str(path), "rev-parse", "HEAD"],
        capture_output=True, text=True, check=True,
    ).stdout.strip()


def _add_gitlink_and_modules(root, path_name, source_path, sha, sm_name=None):
    """Stage a gitlink and append a .gitmodules entry. Does not commit."""
    (root / path_name).mkdir(exist_ok=True)
    subprocess.run(
        ["git", "-C", str(root), "update-index", "--add", "--cacheinfo",
         f"160000,{sha},{path_name}"],
        check=True, capture_output=True,
    )
    section = sm_name or path_name
    cfg = root / ".gitmodules"
    existing = cfg.read_text() if cfg.exists() else ""
    cfg.write_text(existing + f'\n[submodule "{section}"]\n\tpath = {path_name}\n\turl = {source_path}\n')


def _add_gitlink_only(root, path_name, sha):
    """Stage a gitlink with no .gitmodules entry. Does not commit."""
    (root / path_name).mkdir(exist_ok=True)
    subprocess.run(
        ["git", "-C", str(root), "update-index", "--add", "--cacheinfo",
         f"160000,{sha},{path_name}"],
        check=True, capture_output=True,
    )


def _commit_baseline(root, message="baseline"):
    """Stage .gitmodules (if present) and commit everything staged."""
    if (root / ".gitmodules").exists():
        subprocess.run(
            ["git", "-C", str(root), "add", ".gitmodules"],
            check=True, capture_output=True,
        )
    _g(root, "commit", "-m", message)


# ---------------------------------------------------------------------------
# Fail-list filters
# ---------------------------------------------------------------------------

def _3root_stale(fails):
    return [f for f in fails if "[3/root]" in f and "gitlink is stale" in f]


def _3root_uncommitted(fails):
    return [f for f in fails if "[3/root]" in f and "uncommitted" in f]


def _3root_missing(fails):
    return [f for f in fails if "[3/root]" in f and "no .gitmodules" in f]


# ---------------------------------------------------------------------------
# Autouse fixture — mirrors test_wrap_3b_keyed.py's wc_env shape, plus git init
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def wc_env(monkeypatch, tmp_path):
    root = tmp_path / "root"
    root.mkdir()
    subprocess.run(["git", "init", str(root)], check=True, capture_output=True)
    subprocess.run(["git", "-C", str(root), "config", "user.name", "test"],
                   check=True, capture_output=True)
    subprocess.run(["git", "-C", str(root), "config", "user.email", "t@t"],
                   check=True, capture_output=True)

    bellows = root / "bellows"
    bellows.mkdir()
    receipts = bellows / "receipts"
    db_path = bellows / "lifecycle.db"
    _init_lifecycle_db(db_path)
    memory = tmp_path / "memory"
    memory.mkdir()

    monkeypatch.setenv("ELUVIAN_WRAP_ROOT", str(root))
    monkeypatch.setenv("ELUVIAN_WRAP_MEMORY", str(memory))

    # The venv is rooted at the main checkout, so sys.path has the main checkout
    # before this worktree.  Both have a hooks/eluvian/wrap_check.py; the namespace
    # package merges their paths and the main copy wins.  Fix: prepend the worktree
    # and evict the cached (wrong) namespace package entries so the fresh import
    # walks sys.path from the front and finds the worktree's module first.
    import sys
    monkeypatch.syspath_prepend(str(BELLOWS_ROOT))
    for _k in ("hooks", "hooks.eluvian", "hooks.eluvian.wrap_check"):
        monkeypatch.delitem(sys.modules, _k, raising=False)
    import hooks.eluvian.wrap_check as wc
    monkeypatch.setattr(wc, "ROOT", root)
    monkeypatch.setattr(wc, "BELLOWS", bellows)
    monkeypatch.setattr(wc, "RECEIPTS", receipts)
    monkeypatch.setattr(wc, "LIFECYCLE_DB", db_path)
    monkeypatch.setattr(wc, "MEMORY", memory)
    monkeypatch.setattr(wc, "BATON", root / "shop_next_session.md")
    return wc


# ---------------------------------------------------------------------------
# Test 1 — Observer A: a stale pointer fails
# ---------------------------------------------------------------------------

def test_stale_pointer_fails(wc_env, tmp_path):
    """A: stale gitlink fails; message carries the full 40-char published sha.

    Provenance: anvil stood at caf7efcc against published cfd6fd92; lessons-forge
    at dacccbb0 against a1ebf458 — six days adrift before a person noticed (P9).
    """
    root = wc_env.ROOT
    src = tmp_path / "anvil_src"
    sha_old = _make_source(src)
    sha_new = _advance_source(src)  # published tip

    _add_gitlink_and_modules(root, "anvil", src, sha_old)
    _commit_baseline(root)

    # positive control: fixture enumerated exactly what we placed
    assert set(p for p, _ in wc_env._tracked_gitlinks(root)) == {"anvil"}

    fails = wc_env.check(session_id=None, caller="debt")
    stale = _3root_stale(fails)
    assert len(stale) == 1, f"expected 1 stale fail, got: {stale}"
    assert sha_new in stale[0], f"full published sha {sha_new!r} missing from {stale[0]!r}"


# ---------------------------------------------------------------------------
# Test 2 — Observer B: a current pointer passes
# ---------------------------------------------------------------------------

def test_current_pointer_passes(wc_env, tmp_path):
    """B: gitlink at published tip produces no [3/root] stale fail."""
    root = wc_env.ROOT
    src = tmp_path / "mod_src"
    sha = _make_source(src)

    _add_gitlink_and_modules(root, "mod", src, sha)
    _commit_baseline(root)

    assert set(p for p, _ in wc_env._tracked_gitlinks(root)) == {"mod"}

    fails = wc_env.check(session_id=None, caller="debt")
    assert _3root_stale(fails) == [], f"unexpected stale: {_3root_stale(fails)}"


# ---------------------------------------------------------------------------
# Test 3 — Observer C: unreadable tip passes with advisory; stale still fails
# ---------------------------------------------------------------------------

def test_unreadable_remote_passes_with_advisory(wc_env, tmp_path, capsys):
    """C: nonexistent-path URL passes (advisory); genuinely stale submodule fails."""
    root = wc_env.ROOT

    src_stale = tmp_path / "stale_src"
    sha_old = _make_source(src_stale)
    _advance_source(src_stale)  # advance published tip past sha_old

    _add_gitlink_and_modules(root, "mod_stale", src_stale, sha_old)
    # Unreadable: nonexistent local path — rc 128 in ~14 ms, no ssh, no DNS
    fake = tmp_path / "does_not_exist"
    _add_gitlink_and_modules(root, "mod_unreadable", fake, "a" * 40)
    _commit_baseline(root)

    assert set(p for p, _ in wc_env._tracked_gitlinks(root)) == {"mod_stale", "mod_unreadable"}

    fails = wc_env.check(session_id=None, caller="debt")
    out = capsys.readouterr().out

    # mod_unreadable: zero stale fails, advisory in stdout
    unreadable_stale = [f for f in fails if "[3/root]" in f and "mod_unreadable" in f and "stale" in f]
    assert unreadable_stale == [], f"mod_unreadable should not be stale: {unreadable_stale}"
    assert "mod_unreadable" in out, f"advisory for mod_unreadable missing from stdout: {out!r}"
    assert "unreadable" in out

    # mod_stale: exactly one stale fail
    stale = [f for f in fails if "[3/root]" in f and "mod_stale" in f and "stale" in f]
    assert len(stale) == 1, f"expected 1 stale fail for mod_stale, got: {stale}"


# ---------------------------------------------------------------------------
# Test 4 — Observer D: uncommitted changes each reported exactly once
# ---------------------------------------------------------------------------

def test_uncommitted_change_reports_once(wc_env, tmp_path):
    """D: staged bump, addition, removal each fail once; initialized ` M` does not."""
    root = wc_env.ROOT

    src_bump = tmp_path / "bump_src"
    sha_bump_old = _make_source(src_bump)
    sha_bump_new = _advance_source(src_bump)  # published tip

    src_removed = tmp_path / "removed_src"
    sha_removed = _make_source(src_removed)

    src_added = tmp_path / "added_src"
    sha_added = _make_source(src_added)

    src_init = tmp_path / "init_src"
    _make_source(src_init)  # sha1 (older)
    sha_init_tip = _advance_source(src_init)  # sha2 (published tip)

    # Baseline: mod_bump at old sha, mod_removed committed
    _add_gitlink_and_modules(root, "mod_bump", src_bump, sha_bump_old)
    _add_gitlink_and_modules(root, "mod_removed", src_removed, sha_removed)
    _commit_baseline(root)

    # Initialized submodule: gitlink at published tip (sha_init_tip)
    subprocess.run(
        ["git", "-c", "protocol.file.allow=always",
         "-c", "user.name=test", "-c", "user.email=t@t",
         "-C", str(root),
         "submodule", "add", str(src_init), "mod_initialized"],
        check=True, capture_output=True,
    )
    _g(root, "commit", "-m", "add mod_initialized")

    # Move mod_initialized worktree to older sha (produces ` M` — worktree changed,
    # nothing staged; gitlink in index = sha_init_tip = published tip)
    sha_init_older = subprocess.run(
        ["git", "-C", str(src_init), "rev-parse", "HEAD~1"],
        capture_output=True, text=True, check=True,
    ).stdout.strip()
    subprocess.run(
        ["git", "-C", str(root / "mod_initialized"), "checkout", sha_init_older],
        check=True, capture_output=True,
    )

    # Stage: bump mod_bump to current published tip
    subprocess.run(
        ["git", "-C", str(root), "update-index", "--cacheinfo",
         f"160000,{sha_bump_new},mod_bump"],
        check=True, capture_output=True,
    )
    # Stage: remove mod_removed
    subprocess.run(
        ["git", "-C", str(root), "rm", "--cached", "mod_removed"],
        check=True, capture_output=True,
    )
    # Stage: add mod_added (no .gitmodules needed — arm short-circuits on 'A')
    (root / "mod_added").mkdir(exist_ok=True)
    subprocess.run(
        ["git", "-C", str(root), "update-index", "--add", "--cacheinfo",
         f"160000,{sha_added},mod_added"],
        check=True, capture_output=True,
    )

    # positive control
    tracked = set(p for p, _ in wc_env._tracked_gitlinks(root))
    assert "mod_bump" in tracked
    assert "mod_added" in tracked
    assert "mod_removed" in tracked
    assert "mod_initialized" in tracked

    fails = wc_env.check(session_id=None, caller="debt")
    uncommitted = _3root_uncommitted(fails)
    assert len(uncommitted) == 3, f"expected 3 uncommitted fails, got: {uncommitted}"

    bump_f = [f for f in uncommitted if "mod_bump" in f]
    assert len(bump_f) == 1 and "bump" in bump_f[0].lower(), f"bump fail: {bump_f}"

    add_f = [f for f in uncommitted if "mod_added" in f]
    assert len(add_f) == 1 and "addition" in add_f[0].lower(), f"addition fail: {add_f}"

    rem_f = [f for f in uncommitted if "mod_removed" in f]
    assert len(rem_f) == 1 and "removal" in rem_f[0].lower(), f"removal fail: {rem_f}"

    assert not any("mod_initialized" in f for f in uncommitted), \
        f"mod_initialized must not be reported as uncommitted; fails: {uncommitted}"


# ---------------------------------------------------------------------------
# Test 5 — Observer E: gitlink with no .gitmodules entry fails
# ---------------------------------------------------------------------------

def test_missing_gitmodules_entry_fails(wc_env, tmp_path):
    """E: a gitlink with no .gitmodules entry fails naming the path."""
    root = wc_env.ROOT

    _add_gitlink_only(root, "orphan", "b" * 40)
    _commit_baseline(root)

    assert set(p for p, _ in wc_env._tracked_gitlinks(root)) == {"orphan"}

    fails = wc_env.check(session_id=None, caller="debt")
    missing = _3root_missing(fails)
    assert len(missing) == 1, f"expected 1 missing-entry fail, got: {missing}"
    assert "orphan" in missing[0], f"path 'orphan' not in {missing[0]!r}"


# ---------------------------------------------------------------------------
# Test 6 — Observer F: enumeration by path, not section name
# ---------------------------------------------------------------------------

def test_enumeration_is_derived_not_listed(wc_env, tmp_path):
    """F: unusual name is judged; .gitmodules section name != path is found by path."""
    root = wc_env.ROOT

    # Case 1: unusual submodule name not resembling any real governance submodule
    src_foo = tmp_path / "foo_src"
    sha_foo = _make_source(src_foo)
    _add_gitlink_and_modules(root, "totally_unique_xyz", src_foo, sha_foo)
    _commit_baseline(root, "baseline with unusual name")

    # Case 2: initialized submodule whose .gitmodules NAME differs from its PATH
    src_bar = tmp_path / "bar_src"
    _make_source(src_bar)
    # git submodule add --name gives a different section name than the path
    subprocess.run(
        ["git", "-c", "protocol.file.allow=always",
         "-c", "user.name=test", "-c", "user.email=t@t",
         "-C", str(root),
         "submodule", "add", "--name", "different_section_name",
         str(src_bar), "mypath"],
        check=True, capture_output=True,
    )
    _g(root, "commit", "-m", "add mypath with differing section name")

    # positive control
    tracked = set(p for p, _ in wc_env._tracked_gitlinks(root))
    assert "totally_unique_xyz" in tracked
    assert "mypath" in tracked

    fails = wc_env.check(session_id=None, caller="debt")

    # Neither should fail as missing entry
    missing = _3root_missing(fails)
    assert "totally_unique_xyz" not in str(missing), f"unexpected missing: {missing}"
    assert "mypath" not in str(missing), f"unexpected missing: {missing}"

    # Neither should be stale (gitlinks equal their published tips)
    stale = _3root_stale(fails)
    assert "totally_unique_xyz" not in str(stale), f"unexpected stale: {stale}"
    assert "mypath" not in str(stale), f"unexpected stale: {stale}"


# ---------------------------------------------------------------------------
# Test 7 — Observer G: arm writes nothing
# ---------------------------------------------------------------------------

def test_arm_writes_nothing(wc_env, tmp_path):
    """G: git status --porcelain of ROOT is byte-identical before and after check()."""
    root = wc_env.ROOT
    src = tmp_path / "src"
    sha = _make_source(src)
    _add_gitlink_and_modules(root, "mod", src, sha)
    _commit_baseline(root)

    assert set(p for p, _ in wc_env._tracked_gitlinks(root)) == {"mod"}

    def _porcelain():
        return subprocess.run(
            ["git", "-C", str(root), "status", "--porcelain"],
            capture_output=True, text=True, check=True,
        ).stdout

    before = _porcelain()
    wc_env.check(session_id=None, caller="debt")
    after = _porcelain()
    assert before == after, f"arm wrote to the tree: before={before!r} after={after!r}"


# ---------------------------------------------------------------------------
# Test 8 — Observer H: two stale submodules both named
# ---------------------------------------------------------------------------

def test_two_stale_submodules_both_named(wc_env, tmp_path):
    """H: two simultaneously stale submodules — both names appear, count is 2."""
    root = wc_env.ROOT

    src1 = tmp_path / "src1"
    sha1_old = _make_source(src1)
    _advance_source(src1)

    src2 = tmp_path / "src2"
    sha2_old = _make_source(src2)
    _advance_source(src2)

    _add_gitlink_and_modules(root, "mod1", src1, sha1_old)
    _add_gitlink_and_modules(root, "mod2", src2, sha2_old)
    _commit_baseline(root)

    assert set(p for p, _ in wc_env._tracked_gitlinks(root)) == {"mod1", "mod2"}

    fails = wc_env.check(session_id=None, caller="debt")
    stale = _3root_stale(fails)
    assert len(stale) == 2, f"expected 2 stale fails, got: {stale}"
    combined = " ".join(stale)
    assert "mod1" in combined
    assert "mod2" in combined


# ---------------------------------------------------------------------------
# Test 9 — Observer I: reads are bounded, concurrent and non-interactive
# ---------------------------------------------------------------------------

def test_remote_reads_are_bounded_and_batch(wc_env, tmp_path, monkeypatch):
    """I: concurrent reads finish in <1.0 s; ssh constant has BatchMode and ConnectTimeout."""
    root = wc_env.ROOT

    # Half 2 (cheap): transport constants present before any I/O
    assert "BatchMode=yes" in wc_env._GIT_SSH, \
        f"_GIT_SSH missing BatchMode=yes: {wc_env._GIT_SSH!r}"
    assert "ConnectTimeout=" in wc_env._GIT_SSH, \
        f"_GIT_SSH missing ConnectTimeout=: {wc_env._GIT_SSH!r}"

    # Half 1: concurrency — three submodules, slow reader, assert finishes in <1.0 s
    url_to_sha = {}
    for i in range(3):
        src = tmp_path / f"src{i}"
        sha = _make_source(src)
        _add_gitlink_and_modules(root, f"mod{i}", src, sha)
        url_to_sha[str(src)] = sha
    _commit_baseline(root)

    assert len(list(wc_env._tracked_gitlinks(root))) == 3

    def slow_reader(url):
        time.sleep(0.5)
        return url_to_sha.get(url, "0" * 40)

    monkeypatch.setattr(wc_env, "_published_tip", slow_reader)

    t0 = time.monotonic()
    wc_env.check(session_id=None, caller="debt")
    elapsed = time.monotonic() - t0

    assert elapsed < 1.0, (
        f"reads took {elapsed:.2f}s — expected concurrent (<1.0 s); "
        f"a sequential implementation would take ≥1.5 s"
    )


# ---------------------------------------------------------------------------
# Test 10 — Observer L: arm failure is confined to the arm
# ---------------------------------------------------------------------------

def test_arm_failure_is_confined_to_the_arm(wc_env, tmp_path, monkeypatch, capsys):
    """L (stop path): raising tip reader → advisory printed, [3b/lessons] still returned."""
    root = wc_env.ROOT
    src = tmp_path / "src"
    sha = _make_source(src)
    _add_gitlink_and_modules(root, "mod", src, sha)
    _commit_baseline(root)

    assert set(p for p, _ in wc_env._tracked_gitlinks(root)) == {"mod"}

    def raising_reader(url):
        raise RuntimeError("simulated tip-reader failure")

    monkeypatch.setattr(wc_env, "_published_tip", raising_reader)

    # STOP path, with session id — baton absent → [3b/lessons] fails
    sid = "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
    fails = wc_env.check(session_id=sid, caller="stop")  # must not raise

    out = capsys.readouterr().out
    assert "[3/root]" in out, f"arm advisory missing from stdout: {out!r}"
    assert "gitlink arm error" in out, f"advisory text missing: {out!r}"

    lessons_fails = [f for f in fails if "[3b/lessons]" in f]
    assert len(lessons_fails) >= 1, \
        f"[3b/lessons] fail must survive past the arm error; fails: {fails}"
