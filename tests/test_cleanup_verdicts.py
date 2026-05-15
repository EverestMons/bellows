"""Unit tests for _cleanup_verdicts_for_slug helper."""

import os
import tempfile
from pathlib import Path

import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from bellows import _cleanup_verdicts_for_slug


class TestCleanupVerdictsForSlug:
    def test_cleanup_removes_all_step_files_for_slug(self, tmp_path):
        pending = tmp_path / "pending"
        pending.mkdir()
        (pending / "verdict-request-foo-2026-04-19-step-1.md").write_text("")
        (pending / "verdict-request-foo-2026-04-19-step-2.md").write_text("")
        (pending / "verdict-request-foo-2026-04-19-step-3.md").write_text("")

        result = _cleanup_verdicts_for_slug("foo-2026-04-19", verdicts_root=pending)

        assert result == 3
        assert not (pending / "verdict-request-foo-2026-04-19-step-1.md").exists()
        assert not (pending / "verdict-request-foo-2026-04-19-step-2.md").exists()
        assert not (pending / "verdict-request-foo-2026-04-19-step-3.md").exists()

    def test_cleanup_noop_when_no_matches(self, tmp_path):
        pending = tmp_path / "pending"
        pending.mkdir()

        result = _cleanup_verdicts_for_slug("nonexistent-slug", verdicts_root=pending)

        assert result == 0

    def test_cleanup_respects_slug_boundary(self, tmp_path):
        pending = tmp_path / "pending"
        pending.mkdir()
        (pending / "verdict-request-foo-2026-04-19-step-1.md").write_text("")
        (pending / "verdict-request-foo-bar-2026-04-19-step-1.md").write_text("")

        result = _cleanup_verdicts_for_slug("foo-2026-04-19", verdicts_root=pending)

        assert result == 1
        assert not (pending / "verdict-request-foo-2026-04-19-step-1.md").exists()
        assert (pending / "verdict-request-foo-bar-2026-04-19-step-1.md").exists()

    def test_cleanup_ignores_resolved_directory(self, tmp_path):
        pending = tmp_path / "pending"
        pending.mkdir()
        resolved = tmp_path / "resolved"
        resolved.mkdir()
        (resolved / "verdict-request-foo-2026-04-19-step-1.md").write_text("")

        result = _cleanup_verdicts_for_slug("foo-2026-04-19", verdicts_root=pending)

        assert result == 0
        assert (resolved / "verdict-request-foo-2026-04-19-step-1.md").exists()
