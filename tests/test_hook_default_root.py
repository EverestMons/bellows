"""Tests for hook _default_root() — the marker-verified fallback (plan hooks-de-hardcode, 2026-09-02)."""
from __future__ import annotations

import importlib.util
import inspect
from pathlib import Path

import pytest

HOOKS_DIR = Path(__file__).parent.parent / "hooks" / "eluvian"
HOOK_NAMES = ["wrap_arm_hook", "wrap_stop_hook", "wrap_check", "eluvian_align_hook"]


def _load_hook(name):
    """Load a hook module fresh by its file path; caller sets env and Path.home before calling."""
    path = HOOKS_DIR / f"{name}.py"
    spec = importlib.util.spec_from_file_location(f"_test_{name}", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_a_eluvian_governance_marker(tmp_path, monkeypatch):
    """(a) With eluvian-governance/COMPANY.md present, all four hooks return that root."""
    gov = tmp_path / "Developer" / "eluvian-governance"
    gov.mkdir(parents=True)
    (gov / "COMPANY.md").write_text("marker")
    monkeypatch.delenv("ELUVIAN_WRAP_ROOT", raising=False)
    monkeypatch.delenv("ELUVIAN_WRAP_BELLOWS", raising=False)
    monkeypatch.delenv("ELUVIAN_WRAP_TUYERE", raising=False)
    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    for name in HOOK_NAMES:
        mod = _load_hook(name)
        assert mod._default_root() == gov, f"{name}: expected {gov}, got {mod._default_root()}"


def test_b_github_marker(tmp_path, monkeypatch):
    """(b) With only GitHub/COMPANY.md present, all four hooks return that root."""
    github = tmp_path / "Developer" / "GitHub"
    github.mkdir(parents=True)
    (github / "COMPANY.md").write_text("marker")
    monkeypatch.delenv("ELUVIAN_WRAP_ROOT", raising=False)
    monkeypatch.delenv("ELUVIAN_WRAP_BELLOWS", raising=False)
    monkeypatch.delenv("ELUVIAN_WRAP_TUYERE", raising=False)
    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    for name in HOOK_NAMES:
        mod = _load_hook(name)
        assert mod._default_root() == github, f"{name}: expected {github}, got {mod._default_root()}"


def test_c_no_marker(tmp_path, monkeypatch):
    """(c) With neither marker present, all four hooks return eluvian-governance and never raise."""
    monkeypatch.delenv("ELUVIAN_WRAP_ROOT", raising=False)
    monkeypatch.delenv("ELUVIAN_WRAP_BELLOWS", raising=False)
    monkeypatch.delenv("ELUVIAN_WRAP_TUYERE", raising=False)
    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    expected = tmp_path / "Developer" / "eluvian-governance"
    for name in HOOK_NAMES:
        mod = _load_hook(name)
        result = mod._default_root()
        assert result == expected, f"{name}: expected {expected}, got {result}"


def test_d_four_bodies_identical(monkeypatch):
    """(d) The _default_root source is identical across all four hooks."""
    monkeypatch.delenv("ELUVIAN_WRAP_ROOT", raising=False)
    monkeypatch.delenv("ELUVIAN_WRAP_BELLOWS", raising=False)
    monkeypatch.delenv("ELUVIAN_WRAP_TUYERE", raising=False)
    modules = [_load_hook(name) for name in HOOK_NAMES]
    sources = [inspect.getsource(mod._default_root) for mod in modules]
    for i, src in enumerate(sources[1:], 1):
        assert src == sources[0], (
            f"_default_root source mismatch: {HOOK_NAMES[0]} vs {HOOK_NAMES[i]}"
        )


def test_e_wrap_twin_shop_shape(tmp_path, monkeypatch):
    """(e) Shop shape: ROOT/bellows/status.py + ROOT/tuyere/.venv/bin/python → tuyere checkout is ROOT/tuyere."""
    root = tmp_path / "root"
    bellows = root / "bellows"
    tuyere = root / "tuyere"
    bellows.mkdir(parents=True)
    (bellows / "status.py").write_text("")
    (tuyere / ".venv" / "bin").mkdir(parents=True)
    (tuyere / ".venv" / "bin" / "python").write_text("")
    monkeypatch.setenv("ELUVIAN_WRAP_ROOT", str(root))
    monkeypatch.delenv("ELUVIAN_WRAP_BELLOWS", raising=False)
    monkeypatch.delenv("ELUVIAN_WRAP_TUYERE", raising=False)
    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    mod = _load_hook("wrap_check")
    result = mod._tuyere_checkout()
    assert result == tuyere, f"Expected {tuyere}, got {result}"


def test_f_wrap_twin_mini_shape(tmp_path, monkeypatch):
    """(f) Mini shape: env root is gov, bellows is sibling, tuyere is projects parent — not gov/tuyere."""
    gov = tmp_path / "gov"
    gov.mkdir(parents=True)
    bellows = tmp_path / "bellows"
    bellows.mkdir(parents=True)
    (bellows / "status.py").write_text("")
    tuyere = tmp_path / "tuyere"
    (tuyere / ".venv" / "bin").mkdir(parents=True)
    (tuyere / ".venv" / "bin" / "python").write_text("")
    monkeypatch.setenv("ELUVIAN_WRAP_ROOT", str(gov))
    monkeypatch.delenv("ELUVIAN_WRAP_BELLOWS", raising=False)
    monkeypatch.delenv("ELUVIAN_WRAP_TUYERE", raising=False)
    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    mod = _load_hook("wrap_check")
    result = mod._tuyere_checkout()
    assert result == tuyere, f"Expected {tuyere} (projects parent), got {result}"


def test_g_env_precedence(tmp_path, monkeypatch):
    """(g) ELUVIAN_WRAP_ROOT set to a markerless dir — wrap_check.ROOT is that dir (env wins)."""
    override = tmp_path / "no-marker-here"
    override.mkdir()
    monkeypatch.setenv("ELUVIAN_WRAP_ROOT", str(override))
    monkeypatch.delenv("ELUVIAN_WRAP_BELLOWS", raising=False)
    monkeypatch.delenv("ELUVIAN_WRAP_TUYERE", raising=False)
    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    mod = _load_hook("wrap_check")
    assert mod.ROOT == override, f"Expected {override}, got {mod.ROOT}"
