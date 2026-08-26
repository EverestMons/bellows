"""Tests for the [4/memory] class-frontmatter gate and WARN-first advisories."""
import subprocess
import textwrap
from pathlib import Path

import pytest

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "hooks" / "eluvian"))
import wrap_check


def _git(repo, *args):
    subprocess.run(["git", "-C", str(repo), *args],
                   capture_output=True, text=True, check=True)


def _init_memory_repo(tmp_path):
    """Create a minimal git-initialised memory directory with a MEMORY.md."""
    mem = tmp_path / "memory"
    mem.mkdir()
    _git(mem, "init")
    _git(mem, "config", "user.email", "test@test")
    _git(mem, "config", "user.name", "test")
    idx = mem / "MEMORY.md"
    idx.write_text("- [entry](entry.md) — hook\n")
    _git(mem, "add", "MEMORY.md")
    _git(mem, "commit", "-m", "init")
    return mem


@pytest.fixture()
def fake_env(tmp_path, monkeypatch):
    """Isolate wrap_check from the real filesystem."""
    root = tmp_path / "root"
    root.mkdir()
    bellows = root / "bellows"
    bellows.mkdir()
    (bellows / "receipts").mkdir()
    mem = _init_memory_repo(tmp_path)
    monkeypatch.setattr(wrap_check, "ROOT", root)
    monkeypatch.setattr(wrap_check, "BELLOWS", bellows)
    monkeypatch.setattr(wrap_check, "RECEIPTS", bellows / "receipts")
    monkeypatch.setattr(wrap_check, "LIFECYCLE_DB", bellows / "lifecycle.db")
    monkeypatch.setattr(wrap_check, "MEMORY", mem)
    monkeypatch.setattr(wrap_check, "BATON", root / "shop_next_session.md")
    baton = root / "shop_next_session.md"
    baton.write_text("")
    _git(root, "init")
    _git(root, "config", "user.email", "test@test")
    _git(root, "config", "user.name", "test")
    _git(root, "add", ".")
    _git(root, "commit", "-m", "init")
    return mem


def test_new_entry_without_class_fails(fake_env):
    mem = fake_env
    entry = mem / "no-class.md"
    entry.write_text("---\nname: no-class\n---\nSome content.\n")
    (mem / "MEMORY.md").write_text(
        "- [entry](entry.md) — hook\n- [no-class](no-class.md) — test\n"
    )
    fails = wrap_check.check(session_id=None, caller="stop")
    class_fails = [f for f in fails if "missing" in f and "class:" in f]
    assert len(class_fails) == 1
    assert "no-class.md" in class_fails[0]


def test_new_entry_with_class_no_fail(fake_env):
    mem = fake_env
    entry = mem / "has-class.md"
    entry.write_text("---\nname: has-class\nclass: codify\n---\nContent.\n")
    (mem / "MEMORY.md").write_text(
        "- [entry](entry.md) — hook\n- [has-class](has-class.md) — test\n"
    )
    fails = wrap_check.check(session_id=None, caller="stop")
    class_fails = [f for f in fails if "missing" in f and "class:" in f]
    assert len(class_fails) == 0


def test_memory_md_edit_alone_no_class_fail(fake_env):
    mem = fake_env
    (mem / "MEMORY.md").write_text(
        "- [entry](entry.md) — hook\n- extra line\n"
    )
    fails = wrap_check.check(session_id=None, caller="stop")
    class_fails = [f for f in fails if "missing" in f and "class:" in f]
    assert len(class_fails) == 0


def test_committed_classless_entry_clean_tree_no_fail(fake_env):
    mem = fake_env
    entry = mem / "old-entry.md"
    entry.write_text("---\nname: old-entry\n---\nNo class field.\n")
    (mem / "MEMORY.md").write_text(
        "- [entry](entry.md) — hook\n- [old-entry](old-entry.md) — legacy\n"
    )
    _git(mem, "add", ".")
    _git(mem, "commit", "-m", "add old entry")
    fails = wrap_check.check(session_id=None, caller="stop")
    class_fails = [f for f in fails if "missing" in f and "class:" in f]
    assert len(class_fails) == 0


def test_committed_orphan_warns_but_no_fail(fake_env, capsys):
    mem = fake_env
    orphan = mem / "orphan-entry.md"
    orphan.write_text("---\nname: orphan\n---\nNot in index.\n")
    _git(mem, "add", ".")
    _git(mem, "commit", "-m", "add orphan")
    fails = wrap_check.check(session_id=None, caller="stop")
    class_fails = [f for f in fails if "missing" in f and "class:" in f]
    assert len(class_fails) == 0
    captured = capsys.readouterr()
    assert "WARN (advisory)" in captured.out
    assert "orphan-entry.md" in captured.out


def test_oversized_memory_md_warns_but_no_fail(fake_env, capsys):
    mem = fake_env
    lines = ["- [entry](entry.md) — hook\n"] + [
        f"- [item{i}](item{i}.md) — filler\n" for i in range(150)
    ]
    (mem / "MEMORY.md").write_text("".join(lines))
    _git(mem, "add", "MEMORY.md")
    _git(mem, "commit", "-m", "big index")
    fails = wrap_check.check(session_id=None, caller="stop")
    class_fails = [f for f in fails if "missing" in f and "class:" in f]
    assert len(class_fails) == 0
    captured = capsys.readouterr()
    assert "WARN (advisory)" in captured.out
    assert "exceeds the 140 cap" in captured.out
