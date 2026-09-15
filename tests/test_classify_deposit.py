"""Tests for tools/classify_deposit.py — read-only class check tool."""
import importlib.util
import json
import os
import pathlib
import sqlite3
import subprocess
import sys

import pytest

BELLOWS_ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BELLOWS_ROOT))
sys.path.insert(0, str(BELLOWS_ROOT / "scripts"))

import bellows_root as br_mod  # noqa: E402 — path set above

TOOL_PATH = BELLOWS_ROOT / "tools" / "classify_deposit.py"
PYTHON = sys.executable

# ---------------------------------------------------------------------------
# Plan texts
# ---------------------------------------------------------------------------

_PLAN_C1 = """\
# Test plan

## Cycle Manifest
tier: T1
class: shop-infra
writes: tools/x.py, tests/test_x.py
reads: knowledge/research/r.md
"""

_PLAN_C2 = """\
# Test plan

## Cycle Manifest
tier: T1
class: app-feature
writes: tools/x.py, tests/test_x.py
reads: knowledge/research/r.md
"""

_PLAN_C3 = """\
# Test plan

## STEP 1

**Deposits:**
- `tools/y.py`
"""

_PLAN_C4 = """\
# Test plan

## Cycle Manifest
tier: T1
class: shop-infra
writes: tools/x.py,
tests/test_x.py
reads: knowledge/research/r.md
"""

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _load_tool():
    spec = importlib.util.spec_from_file_location("classify_deposit", TOOL_PATH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _write_config(path, data):
    p = pathlib.Path(path)
    p.write_text(json.dumps(data))
    return str(p)


def _plan_file(tmp_path, text, name="plan.md"):
    p = tmp_path / name
    p.write_text(text)
    return str(p)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(autouse=True)
def patch_roots(tmp_path, monkeypatch):
    G = tmp_path / "governance"
    G.mkdir()
    P = tmp_path
    monkeypatch.setattr(br_mod, "resolve_governance_root", lambda _start=None: G)
    monkeypatch.setattr(br_mod, "resolve_projects_parent", lambda _start=None: P)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


def test_c1_match(tmp_path, capsys):
    pr = tmp_path / "bellows"
    pr.mkdir()
    plan = _plan_file(tmp_path, _PLAN_C1)
    cfg = _write_config(tmp_path / "cfg.json", {})
    mod = _load_tool()
    rc = mod.main([plan, "--project-root", str(pr), "--config", cfg])
    out = capsys.readouterr().out
    assert "writes (2) from manifest" in out
    assert "RESULT: MATCH" in out
    assert rc == 0


def test_c2_mismatch(tmp_path, capsys):
    pr = tmp_path / "bellows"
    pr.mkdir()
    plan = _plan_file(tmp_path, _PLAN_C2)
    cfg = _write_config(tmp_path / "cfg.json", {})
    mod = _load_tool()
    rc = mod.main([plan, "--project-root", str(pr), "--config", cfg])
    out = capsys.readouterr().out
    assert "assigned class: shop-infra" in out
    assert "RESULT: MISMATCH" in out
    assert rc == 1


def test_c3_fallback(tmp_path, capsys):
    pr = tmp_path / "bellows"
    pr.mkdir()
    plan = _plan_file(tmp_path, _PLAN_C3)
    cfg = _write_config(tmp_path / "cfg.json", {})
    mod = _load_tool()
    rc = mod.main([plan, "--project-root", str(pr), "--config", cfg])
    out = capsys.readouterr().out
    assert "from fallback" in out
    assert "RESULT: FALLBACK" in out
    assert rc == 3


def test_c4_unparsed_stanza(tmp_path, capsys):
    pr = tmp_path / "bellows"
    pr.mkdir()
    plan = _plan_file(tmp_path, _PLAN_C4)
    cfg = _write_config(tmp_path / "cfg.json", {})
    mod = _load_tool()
    rc = mod.main([plan, "--project-root", str(pr), "--config", cfg])
    out = capsys.readouterr().out
    assert "unparsed stanza lines (1)" in out
    assert "RESULT: UNPARSED-STANZA" in out
    assert rc == 3


def test_c5_no_database(tmp_path, capsys, monkeypatch):
    pr = tmp_path / "bellows"
    pr.mkdir()
    plan = _plan_file(tmp_path, _PLAN_C1)
    cfg = _write_config(tmp_path / "cfg.json", {})

    def _no_connect(*a, **kw):
        raise AssertionError("sqlite3.connect must not be called")

    monkeypatch.setattr(sqlite3, "connect", _no_connect)
    mod = _load_tool()
    rc = mod.main([plan, "--project-root", str(pr), "--config", cfg])
    out = capsys.readouterr().out
    assert "RESULT: MATCH" in out
    assert rc == 0


def test_c6_config(tmp_path, capsys):
    pr = tmp_path / "myinfra"
    pr.mkdir()
    plan = _plan_file(tmp_path, _PLAN_C1)
    cfg_empty = _write_config(tmp_path / "cfg_empty.json", {})
    cfg_infra = _write_config(
        tmp_path / "cfg_infra.json", {"shop_infra_projects": ["myinfra"]}
    )

    mod = _load_tool()
    mod.main([plan, "--project-root", str(pr), "--config", cfg_empty])
    out = capsys.readouterr().out
    assert "assigned class: app-feature" in out

    mod2 = _load_tool()
    mod2.main([plan, "--project-root", str(pr), "--config", cfg_infra])
    out2 = capsys.readouterr().out
    assert "assigned class: shop-infra" in out2


def test_c7_missing_project_root(tmp_path):
    plan = _plan_file(tmp_path, _PLAN_C1)
    result = subprocess.run(
        [PYTHON, str(TOOL_PATH), plan],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 2
    assert "usage" in result.stderr.lower() or "error" in result.stderr.lower()


def test_c8_unreadable_input(tmp_path, capsys):
    pr = tmp_path / "bellows"
    pr.mkdir()
    cfg = _write_config(tmp_path / "cfg.json", {})

    with pytest.raises(SystemExit) as exc1:
        _load_tool().main(
            [str(tmp_path / "nonexistent.md"), "--project-root", str(pr), "--config", cfg]
        )
    assert exc1.value.code == 2
    assert "RESULT:" not in capsys.readouterr().out

    with pytest.raises(SystemExit) as exc2:
        _load_tool().main(
            [
                _plan_file(tmp_path, _PLAN_C1),
                "--project-root", str(pr),
                "--config", str(tmp_path / "nofile.json"),
            ]
        )
    assert exc2.value.code == 2
    assert "RESULT:" not in capsys.readouterr().out

    bad_cfg = tmp_path / "bad.json"
    bad_cfg.write_text("[")
    with pytest.raises(SystemExit) as exc3:
        _load_tool().main(
            [
                _plan_file(tmp_path, _PLAN_C1, name="plan2.md"),
                "--project-root", str(pr),
                "--config", str(bad_cfg),
            ]
        )
    assert exc3.value.code == 2
    assert "RESULT:" not in capsys.readouterr().out


def test_c9_script_run(tmp_path):
    """Tool starts and classifies when invoked as a script with no PYTHONPATH."""
    gov = tmp_path / "governance"
    gov.mkdir(exist_ok=True)
    (gov / "COMPANY.md").write_text("# company\n")

    plan = _plan_file(tmp_path, _PLAN_C1)
    cfg = _write_config(tmp_path / "cfg.json", {})

    env = {k: v for k, v in os.environ.items() if k != "PYTHONPATH"}
    env["ELUVIAN_WRAP_ROOT"] = str(gov)
    env["HOME"] = str(tmp_path)

    result = subprocess.run(
        [
            sys.executable,
            str(TOOL_PATH),
            plan,
            "--project-root",
            str(BELLOWS_ROOT),
            "--config",
            cfg,
        ],
        cwd=str(tmp_path),
        capture_output=True,
        text=True,
        env=env,
    )

    assert "Traceback" not in result.stderr
    assert "writes (2) from manifest" in result.stdout
    assert "RESULT:" in result.stdout
    assert result.returncode in {0, 1, 3}
