import os
import subprocess
import sys
import tempfile
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import bellows


# ---------------------------------------------------------------------------
# Fixtures — real git diff --stat output captured from an actual git mv
# (provenance: walk-register-diff-stat-rename-normalize-2026-08-26, walk 0)
# ---------------------------------------------------------------------------

# Cross-dir brace form: git mv a/b/f.md c/f.md renders "{a/b => c}/f.md"
BRACE_FORM_LINE = " {a/b => c}/f.md          | 0"

# Top-level bare form: git mv top.md renamed-top.md renders "top.md => renamed-top.md"
BARE_FORM_LINE = " top.md => renamed-top.md | 0"

# A normal (non-rename) line
NORMAL_LINE = " src/utils.py             | 3 ++-"

# Mixed block: brace + bare + normal
MIXED_BLOCK = (
    f"{BRACE_FORM_LINE}\n"
    f"{BARE_FORM_LINE}\n"
    f"{NORMAL_LINE}\n"
    " 3 files changed\n"
)

# Empty-prefix brace: git mv f.md sub/f.md renders "{ => sub}/f.md"
EMPTY_PREFIX_BRACE_LINE = " { => sub}/f.md           | 0"


# ---------------------------------------------------------------------------
# THREE parser-level tests (monkeypatched subprocess)
# ---------------------------------------------------------------------------

def test_brace_form_normalized_to_new_path():
    """Brace-form rename '{a/b => c}/f.md' normalizes to 'c/f.md'."""
    mock_result = MagicMock()
    mock_result.returncode = 0
    mock_result.stdout = f"{BRACE_FORM_LINE}\n 1 file changed\n"
    with patch("bellows.subprocess.run", return_value=mock_result):
        result = bellows._parse_diff_stat("post", "pre", "/any/path")
    assert result == ["c/f.md"]
    assert not any("{" in f for f in result)


def test_bare_form_normalized_to_new_path():
    """Bare-form rename 'top.md => renamed-top.md' normalizes to 'renamed-top.md'."""
    mock_result = MagicMock()
    mock_result.returncode = 0
    mock_result.stdout = f"{BARE_FORM_LINE}\n 1 file changed\n"
    with patch("bellows.subprocess.run", return_value=mock_result):
        result = bellows._parse_diff_stat("post", "pre", "/any/path")
    assert result == ["renamed-top.md"]


def test_mixed_block_all_normalized():
    """Mixed block (brace + bare + normal) — all three entries correct."""
    mock_result = MagicMock()
    mock_result.returncode = 0
    mock_result.stdout = MIXED_BLOCK
    with patch("bellows.subprocess.run", return_value=mock_result):
        result = bellows._parse_diff_stat("post", "pre", "/any/path")
    assert sorted(result) == ["c/f.md", "renamed-top.md", "src/utils.py"]
    assert not any(" => " in f for f in result)
    assert not any("{" in f for f in result)


# ---------------------------------------------------------------------------
# TWO end-to-end real-git tests (no mocks)
# ---------------------------------------------------------------------------

def test_real_git_mv_cross_dir_normalized():
    """Real git mv cross-dir: _parse_diff_stat returns new paths, no arrows, no braces."""
    with tempfile.TemporaryDirectory() as tmpdir:
        run = lambda cmd: subprocess.run(cmd, cwd=tmpdir, capture_output=True, check=True)
        run(["git", "init"])
        run(["git", "config", "user.email", "test@test"])
        run(["git", "config", "user.name", "test"])

        # Create a/b/f.md and top.md, commit
        os.makedirs(os.path.join(tmpdir, "a", "b"), exist_ok=True)
        with open(os.path.join(tmpdir, "a", "b", "f.md"), "w") as fh:
            fh.write("content")
        with open(os.path.join(tmpdir, "top.md"), "w") as fh:
            fh.write("content")
        run(["git", "add", "."])
        run(["git", "commit", "-m", "init"])
        pre_sha = subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=tmpdir, capture_output=True, text=True
        ).stdout.strip()

        # git mv a/b/f.md -> c/f.md and top.md -> renamed-top.md
        os.makedirs(os.path.join(tmpdir, "c"), exist_ok=True)
        run(["git", "mv", "a/b/f.md", "c/f.md"])
        run(["git", "mv", "top.md", "renamed-top.md"])
        run(["git", "commit", "-m", "rename"])
        post_sha = subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=tmpdir, capture_output=True, text=True
        ).stdout.strip()

        result = bellows._parse_diff_stat(post_sha, pre_sha, tmpdir)
        assert "c/f.md" in result
        assert "renamed-top.md" in result
        assert not any(" => " in f for f in result)
        assert not any("{" in f for f in result)


def test_real_git_mv_empty_prefix_brace():
    """Real git mv f.md sub/f.md renders '{ => sub}/f.md' — lstrip guard yields 'sub/f.md'."""
    with tempfile.TemporaryDirectory() as tmpdir:
        run = lambda cmd: subprocess.run(cmd, cwd=tmpdir, capture_output=True, check=True)
        run(["git", "init"])
        run(["git", "config", "user.email", "test@test"])
        run(["git", "config", "user.name", "test"])

        with open(os.path.join(tmpdir, "f.md"), "w") as fh:
            fh.write("content")
        run(["git", "add", "."])
        run(["git", "commit", "-m", "init"])
        pre_sha = subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=tmpdir, capture_output=True, text=True
        ).stdout.strip()

        os.makedirs(os.path.join(tmpdir, "sub"), exist_ok=True)
        run(["git", "mv", "f.md", "sub/f.md"])
        run(["git", "commit", "-m", "move to sub"])
        post_sha = subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=tmpdir, capture_output=True, text=True
        ).stdout.strip()

        result = bellows._parse_diff_stat(post_sha, pre_sha, tmpdir)
        assert "sub/f.md" in result
        assert not any(" => " in f for f in result)
        assert not any("{" in f for f in result)
