"""Tests for tools/link_live_commands.py — all via --commands-dir on tmp dirs."""
import os
import sys
from pathlib import Path

import pytest

TOOLS_DIR = Path(__file__).resolve().parent.parent / "tools"
sys.path.insert(0, str(TOOLS_DIR.parent))

import tools.link_live_commands as llc

_REPO_VENDORED = Path(__file__).resolve().parent.parent / "hooks" / "commands"


@pytest.fixture
def vendored(tmp_path):
    """Create a vendored dir with two command files."""
    vdir = tmp_path / "vendored"
    vdir.mkdir()
    (vdir / "wrap.md").write_text("# wrap content\nline two\n")
    (vdir / "eluvian.md").write_text("# eluvian content\n")
    return vdir


@pytest.fixture
def cmd_dir(tmp_path):
    """Return a commands dir path (exists)."""
    d = tmp_path / "commands"
    d.mkdir()
    return d


# ---------- Test 1: fresh dir — absent targets ----------

def test_fresh_dir_both_linked(vendored, cmd_dir):
    with pytest.raises(SystemExit) as exc:
        llc.link_commands(str(cmd_dir), str(vendored))
    assert exc.value.code == 0
    for name in ("wrap.md", "eluvian.md"):
        target = cmd_dir / name
        assert target.is_symlink()
        assert target.resolve() == (vendored / name).resolve()
        assert target.read_bytes() == (vendored / name).read_bytes()


# ---------- Test 2: idempotent second run ----------

def test_idempotent_no_new_backups(vendored, cmd_dir, capsys):
    with pytest.raises(SystemExit):
        llc.link_commands(str(cmd_dir), str(vendored))
    existing_files = set(os.listdir(cmd_dir))

    with pytest.raises(SystemExit) as exc:
        llc.link_commands(str(cmd_dir), str(vendored))
    assert exc.value.code == 0
    out = capsys.readouterr().out
    assert "OK" in out
    assert set(os.listdir(cmd_dir)) == existing_files


# ---------- Test 3: plain files backed up ----------

def test_plain_files_backed_up(vendored, cmd_dir):
    original_wrap = b"original wrap"
    original_eluvian = b"original eluvian"
    (cmd_dir / "wrap.md").write_bytes(original_wrap)
    (cmd_dir / "eluvian.md").write_bytes(original_eluvian)

    with pytest.raises(SystemExit) as exc:
        llc.link_commands(str(cmd_dir), str(vendored))
    assert exc.value.code == 0

    for name in ("wrap.md", "eluvian.md"):
        target = cmd_dir / name
        assert target.is_symlink()
        assert target.resolve() == (vendored / name).resolve()

    assert (cmd_dir / "wrap.md.pre-symlink").read_bytes() == original_wrap
    assert (cmd_dir / "eluvian.md.pre-symlink").read_bytes() == original_eluvian


# ---------- Test 4: backup collision — timestamped variant ----------

def test_backup_collision_timestamped(vendored, cmd_dir):
    (cmd_dir / "wrap.md").write_bytes(b"first version")
    (cmd_dir / "wrap.md.pre-symlink").write_bytes(b"prior backup")
    (cmd_dir / "eluvian.md").write_bytes(b"first eluvian")

    with pytest.raises(SystemExit) as exc:
        llc.link_commands(str(cmd_dir), str(vendored))
    assert exc.value.code == 0

    assert (cmd_dir / "wrap.md.pre-symlink").read_bytes() == b"prior backup"

    timestamped = [f for f in os.listdir(cmd_dir)
                   if f.startswith("wrap.md.pre-symlink.")]
    assert len(timestamped) == 1
    assert (cmd_dir / timestamped[0]).read_bytes() == b"first version"


# ---------- Test 5: foreign symlink — refusal ----------

def test_foreign_symlink_refusal(vendored, cmd_dir, tmp_path):
    foreign = tmp_path / "foreign.md"
    foreign.write_text("foreign")
    os.symlink(str(foreign), str(cmd_dir / "wrap.md"))

    with pytest.raises(SystemExit) as exc:
        llc.link_commands(str(cmd_dir), str(vendored))
    assert exc.value.code == 1

    assert (cmd_dir / "wrap.md").is_symlink()
    assert (cmd_dir / "wrap.md").resolve() == foreign.resolve()
    assert not (cmd_dir / "eluvian.md").exists()


# ---------- Test 6: missing vendored file — refusal before action ----------

def test_missing_vendored_file_refusal(cmd_dir, tmp_path):
    bad_vendored = tmp_path / "bad_vendored"
    bad_vendored.mkdir()
    (bad_vendored / "wrap.md").write_text("only wrap")

    with pytest.raises(SystemExit) as exc:
        llc.link_commands(str(cmd_dir), str(bad_vendored))
    assert exc.value.code == 1
    assert len(os.listdir(cmd_dir)) == 0


# ---------- Test 7: dry-run — no filesystem changes ----------

def test_dry_run_no_changes(vendored, cmd_dir, capsys):
    llc.link_commands(str(cmd_dir), str(vendored), dry_run=True)
    out = capsys.readouterr().out
    assert "WOULD LINK" in out
    assert not (cmd_dir / "wrap.md").exists()
    assert not (cmd_dir / "eluvian.md").exists()


# ---------- Test 8: missing commands dir — created and linked ----------

def test_missing_commands_dir_created(vendored, tmp_path):
    new_dir = tmp_path / "deep" / "nested" / "commands"
    assert not new_dir.exists()

    with pytest.raises(SystemExit) as exc:
        llc.link_commands(str(new_dir), str(vendored))
    assert exc.value.code == 0

    assert new_dir.is_dir()
    for name in ("wrap.md", "eluvian.md"):
        target = new_dir / name
        assert target.is_symlink()
        assert target.resolve() == (vendored / name).resolve()
