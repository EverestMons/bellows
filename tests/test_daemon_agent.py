"""Tests for the launchd daemon agent — plist template, installer, restart path."""

import os
import plistlib
import subprocess
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# dashboard imports bellows internally; import it first so the worktree path
# wins before bellows.py adds the main checkout to sys.path
import dashboard
import bellows

_TEMPLATE = Path(__file__).parent.parent / "scripts" / "com.eluvian.bellows-daemon.plist.template"
_INSTALLER = Path(__file__).parent.parent / "scripts" / "install-daemon-agent.sh"
_LABEL = "com.eluvian.bellows-daemon"


def _render_template(root: Path, home: Path) -> str:
    text = _TEMPLATE.read_text()
    text = text.replace("__BELLOWS_ROOT__", str(root))
    text = text.replace("__HOME__", str(home))
    return text


# t1 -------------------------------------------------------------------------
def test_t1_template_parses(tmp_path):
    root = tmp_path / "bellows"
    home = tmp_path / "home"
    rendered = _render_template(root, home)
    data = plistlib.loads(rendered.encode())
    assert data["Label"] == _LABEL
    assert data["ProgramArguments"][0].endswith(".venv/bin/python")
    assert data["KeepAlive"] == {"SuccessfulExit": False}
    assert data["ExitTimeOut"] > bellows._DRAIN_TIMEOUT
    path_val = data["EnvironmentVariables"]["PATH"]
    assert path_val.startswith(str(home) + "/.local/bin")


# t2 -------------------------------------------------------------------------
def test_t2_plutil_lint(tmp_path):
    root = tmp_path / "bellows"
    home = tmp_path / "home"
    rendered = _render_template(root, home)
    plist_path = tmp_path / "rendered.plist"
    plist_path.write_text(rendered)
    result = subprocess.run(
        ["/usr/bin/plutil", "-lint", str(plist_path)],
        capture_output=True, text=True,
    )
    assert result.returncode == 0, result.stderr


# t3 -------------------------------------------------------------------------
def test_t3_restart_agent_loaded():
    kickstart = MagicMock(return_value=(True, "kickstarted"))
    popen = MagicMock()
    with patch.object(bellows, "_agent_loaded", return_value=True):
        with patch.object(bellows, "_kickstart", kickstart):
            with patch("bellows.subprocess.Popen", popen):
                bellows._perform_restart()
    kickstart.assert_called_once()
    popen.assert_not_called()


# t4 -------------------------------------------------------------------------
def test_t4_restart_no_agent():
    kickstart = MagicMock(return_value=(True, "kickstarted"))
    popen = MagicMock()
    with patch.object(bellows, "_agent_loaded", return_value=False):
        with patch.object(bellows, "_kickstart", kickstart):
            with patch("bellows.subprocess.Popen", popen):
                bellows._perform_restart()
    kickstart.assert_not_called()
    popen.assert_called_once()
    assert popen.call_args.kwargs.get("start_new_session") is True


# t5 -------------------------------------------------------------------------
def test_t5_spawn_child_agent_loaded(tmp_path):
    # widening: _agent_root patch is added so the new _agent_owns_root condition
    # passes; before the production edit the patch is ignored and t5 stays green
    (tmp_path / "config.json").write_text("{}")
    shell = dashboard.CursesShell(bellows_root=tmp_path)
    kickstart = MagicMock(return_value=(True, "ok"))
    with patch.object(bellows, "_agent_loaded", return_value=True):
        with patch.object(bellows, "_agent_root", return_value=str(tmp_path), create=True):
            with patch.object(bellows, "_kickstart", kickstart):
                shell._spawn_child()
    assert shell.child is None
    kickstart.assert_called_once()


# t6 -------------------------------------------------------------------------
def test_t6_quit_viewer_no_kill(tmp_path):
    (tmp_path / "config.json").write_text("{}")
    shell = dashboard.CursesShell(bellows_root=tmp_path)
    shell.child = None
    kill_calls = []
    with patch("os.kill", side_effect=lambda pid, sig: kill_calls.append((pid, sig))):
        shell._do_quit()
    assert kill_calls == []


# t7 -------------------------------------------------------------------------
def test_t7_installer(tmp_path):
    import shutil

    root_dir = tmp_path / "bellows"
    home_dir = tmp_path / "home"

    # Minimal structure the installer checks for
    (root_dir / ".venv" / "bin").mkdir(parents=True)
    py = root_dir / ".venv" / "bin" / "python"
    py.write_text("#!/bin/sh\n")
    py.chmod(0o755)
    (root_dir / "config.json").write_text("{}")
    (root_dir / "scripts").mkdir()
    shutil.copy(str(_TEMPLATE), str(root_dir / "scripts" / _TEMPLATE.name))
    shutil.copy(str(_INSTALLER), str(root_dir / "scripts" / _INSTALLER.name))

    # launchctl stub
    stub_bin = tmp_path / "bin"
    stub_bin.mkdir()
    calls_file = tmp_path / "calls.txt"
    launchctl_stub = stub_bin / "launchctl"
    launchctl_stub.write_text(
        f'#!/bin/sh\necho "launchctl-stub $*" >> {str(calls_file)!r}\n'
    )
    launchctl_stub.chmod(0o755)

    # claude stub at $HOME/.local/bin/claude (the plist's hardcoded PATH)
    local_bin = home_dir / ".local" / "bin"
    local_bin.mkdir(parents=True)
    claude_stub = local_bin / "claude"
    claude_stub.write_text("#!/bin/sh\n")
    claude_stub.chmod(0o755)

    env = dict(os.environ)
    env["HOME"] = str(home_dir)
    env["PATH"] = str(stub_bin) + ":" + env.get("PATH", "")

    result = subprocess.run(
        ["/bin/bash", str(root_dir / "scripts" / _INSTALLER.name)],
        env=env,
        capture_output=True, text=True,
    )
    assert result.returncode == 0, result.stderr + result.stdout

    plist_path = home_dir / "Library" / "LaunchAgents" / "com.eluvian.bellows-daemon.plist"
    assert plist_path.exists()
    content = plist_path.read_text()
    assert "__BELLOWS_ROOT__" not in content
    assert "__HOME__" not in content

    calls = calls_file.read_text()
    assert "bootout" in calls
    assert "bootstrap" in calls

    # --- No claude: exit 1, plist not written ---
    no_claude_home = tmp_path / "home2"
    no_claude_home.mkdir()
    result2 = subprocess.run(
        ["/bin/bash", str(root_dir / "scripts" / _INSTALLER.name)],
        env={**os.environ, "HOME": str(no_claude_home), "PATH": str(stub_bin)},
        capture_output=True, text=True,
    )
    assert result2.returncode == 1
    no_plist = (
        no_claude_home / "Library" / "LaunchAgents" / "com.eluvian.bellows-daemon.plist"
    )
    assert not no_plist.exists()


# t8 -------------------------------------------------------------------------
def test_t8_agent_root_parses_working_directory(tmp_path):
    """_agent_root prefers working directory line; falls back to program path."""
    sample_wd = str(tmp_path / "bellows")
    launchctl_output = (
        f"path = /Users/test/Library/LaunchAgents/com.eluvian.bellows-daemon.plist\n"
        f"program = {sample_wd}/.venv/bin/python\n"
        f"arguments = {{\n"
        f"    {sample_wd}/.venv/bin/python,\n"
        f"    bellows.py\n"
        f"}}\n"
        f"working directory = {sample_wd}\n"
        f"runs = 3\n"
        f"pid = 12345\n"
    )
    from unittest.mock import MagicMock
    # Case 1: working directory line present → use it directly
    with patch("bellows.subprocess.run", return_value=MagicMock(returncode=0, stdout=launchctl_output)):
        assert bellows._agent_root() == sample_wd
    # Case 2: working directory line absent → fall back to program path (three dirname calls)
    output_no_wd = "\n".join(
        l for l in launchctl_output.splitlines() if "working directory" not in l
    ) + "\n"
    with patch("bellows.subprocess.run", return_value=MagicMock(returncode=0, stdout=output_no_wd)):
        assert bellows._agent_root() == sample_wd
    # Case 3: non-zero exit → None
    with patch("bellows.subprocess.run", return_value=MagicMock(returncode=1, stdout="")):
        assert bellows._agent_root() is None


# t9 -------------------------------------------------------------------------
def test_t9_agent_owns_root_compares_realpath(tmp_path):
    """_agent_owns_root uses realpath comparison; same basename, different parent → False."""
    agent_dir = tmp_path / "bellows"
    agent_dir.mkdir()
    other_dir = tmp_path / "other" / "bellows"
    other_dir.mkdir(parents=True)
    with patch.object(bellows, "_agent_root", return_value=str(agent_dir)):
        assert bellows._agent_owns_root(agent_dir) is True
        assert bellows._agent_owns_root(other_dir) is False
    with patch.object(bellows, "_agent_root", return_value=None):
        assert bellows._agent_owns_root(agent_dir) is False


# t10 -------------------------------------------------------------------------
def test_t10_spawn_child_foreign_root_spawns_a_child(tmp_path):
    """_spawn_child uses the old branch (Popen) when the agent owns a different root."""
    (tmp_path / "config.json").write_text("{}")
    shell = dashboard.CursesShell(bellows_root=tmp_path)
    kickstart = MagicMock()
    popen = MagicMock()
    with patch.object(bellows, "_agent_loaded", return_value=True):
        with patch.object(bellows, "_agent_root", return_value=str(tmp_path / "elsewhere")):
            with patch.object(bellows, "_kickstart", kickstart):
                with patch("dashboard.subprocess.Popen", popen):
                    shell._spawn_child()
    kickstart.assert_not_called()
    popen.assert_called_once()
    assert popen.call_args.kwargs.get("cwd") == str(tmp_path)
    assert shell.child is popen.return_value


# t11 -------------------------------------------------------------------------
def test_t11_spawn_child_own_root_kickstarts_without_replace(tmp_path):
    """_spawn_child kickstarts with replace=False when the agent owns this root."""
    (tmp_path / "config.json").write_text("{}")
    shell = dashboard.CursesShell(bellows_root=tmp_path)
    kickstart = MagicMock(return_value=(True, "ok"))
    popen = MagicMock()
    with patch.object(bellows, "_agent_loaded", return_value=True):
        with patch.object(bellows, "_agent_root", return_value=str(tmp_path)):
            with patch.object(bellows, "_kickstart", kickstart):
                with patch("dashboard.subprocess.Popen", popen):
                    shell._spawn_child()
    kickstart.assert_called_once_with("com.eluvian.bellows-daemon", replace=False)
    popen.assert_not_called()
    assert shell.child is None


# t12 -------------------------------------------------------------------------
def test_t12_kickstart_replace_flag():
    """_kickstart with replace=False omits -k; default (replace=True) includes -k."""
    captured = []

    def fake_run(argv, **kwargs):
        captured.append(list(argv))
        return MagicMock(returncode=0, stdout="ok", stderr="")

    with patch("bellows.subprocess.run", side_effect=fake_run):
        bellows._kickstart("L", replace=False)
        bellows._kickstart("L")
    uid = os.getuid()
    assert captured[0] == ["launchctl", "kickstart", f"gui/{uid}/L"]
    assert captured[1] == ["launchctl", "kickstart", "-k", f"gui/{uid}/L"]
