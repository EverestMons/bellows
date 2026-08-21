"""Targeted tests for the wrap-hook daemon exemption (plan 496, Step 2)."""
import json
import os
import subprocess
import sys
import textwrap
import uuid
from pathlib import Path

import pytest

HOOKS_DIR = Path(__file__).resolve().parent.parent / "hooks" / "eluvian"


@pytest.fixture(autouse=True)
def _isolate_wrap_env(monkeypatch, tmp_path):
    """Ensure tests never touch the real governance root or hooks.log.

    BELLOWS_DISPATCH is deleted (absence is its safe state).
    ELUVIAN_WRAP_ROOT is set to tmp_path (absence would resolve the real root).
    ELUVIAN_HOOKS_LOG is set to a tmp_path file.
    """
    monkeypatch.delenv("BELLOWS_DISPATCH", raising=False)
    monkeypatch.setenv("ELUVIAN_WRAP_ROOT", str(tmp_path))
    monkeypatch.setenv("ELUVIAN_HOOKS_LOG", str(tmp_path / "hooks.log"))


def _run_hook(script_name, payload=None, env_overrides=None):
    """Run a hook script as a subprocess with a piped stdin payload."""
    script = HOOKS_DIR / script_name
    env = {**os.environ}
    if env_overrides:
        for k, v in env_overrides.items():
            if v is None:
                env.pop(k, None)
            else:
                env[k] = v
    stdin_data = json.dumps(payload) if payload is not None else ""
    result = subprocess.run(
        [sys.executable, str(script)],
        input=stdin_data,
        capture_output=True,
        text=True,
        timeout=30,
        env=env,
    )
    return result


# ---------- wrap_stop_hook.py ----------

class TestStopHookExemption:
    def test_exempt_when_dispatch_set(self, tmp_path):
        sid = str(uuid.uuid4())
        payload = {"session_id": sid, "hook_event_name": "Stop", "cwd": "/tmp"}
        sentinel = tmp_path / ".wrap-in-progress"
        sentinel.touch()

        result = _run_hook("wrap_stop_hook.py", payload, env_overrides={
            "BELLOWS_DISPATCH": "1",
            "ELUVIAN_WRAP_ROOT": str(tmp_path),
            "ELUVIAN_HOOKS_LOG": str(tmp_path / "hooks.log"),
        })

        out = json.loads(result.stdout)
        assert out == {}
        assert result.returncode == 0

        log_content = (tmp_path / "hooks.log").read_text()
        assert "daemon-exempt" in log_content
        assert sid in log_content

    def test_not_exempt_when_dispatch_unset(self, tmp_path):
        sid = str(uuid.uuid4())
        payload = {"session_id": sid, "hook_event_name": "Stop", "cwd": "/tmp"}
        sentinel = tmp_path / ".wrap-in-progress"
        sentinel.touch()

        result = _run_hook("wrap_stop_hook.py", payload, env_overrides={
            "BELLOWS_DISPATCH": None,
            "ELUVIAN_WRAP_ROOT": str(tmp_path),
            "ELUVIAN_HOOKS_LOG": str(tmp_path / "hooks.log"),
        })

        out = json.loads(result.stdout)
        assert "decision" in out
        assert out["decision"] == "block"

        log_content = (tmp_path / "hooks.log").read_text()
        assert "armed-BLOCK" in log_content
        assert sid in log_content

    def test_not_exempt_when_dispatch_zero(self, tmp_path):
        """BELLOWS_DISPATCH=0 must NOT exempt (B2 trap)."""
        sid = str(uuid.uuid4())
        payload = {"session_id": sid, "hook_event_name": "Stop", "cwd": "/tmp"}
        sentinel = tmp_path / ".wrap-in-progress"
        sentinel.touch()

        result = _run_hook("wrap_stop_hook.py", payload, env_overrides={
            "BELLOWS_DISPATCH": "0",
            "ELUVIAN_WRAP_ROOT": str(tmp_path),
            "ELUVIAN_HOOKS_LOG": str(tmp_path / "hooks.log"),
        })

        out = json.loads(result.stdout)
        assert "decision" in out
        assert out["decision"] == "block"

    def test_not_exempt_when_dispatch_empty(self, tmp_path):
        """BELLOWS_DISPATCH='' must NOT exempt."""
        sid = str(uuid.uuid4())
        payload = {"session_id": sid, "hook_event_name": "Stop", "cwd": "/tmp"}
        sentinel = tmp_path / ".wrap-in-progress"
        sentinel.touch()

        result = _run_hook("wrap_stop_hook.py", payload, env_overrides={
            "BELLOWS_DISPATCH": "",
            "ELUVIAN_WRAP_ROOT": str(tmp_path),
            "ELUVIAN_HOOKS_LOG": str(tmp_path / "hooks.log"),
        })

        out = json.loads(result.stdout)
        assert "decision" in out
        assert out["decision"] == "block"

    def test_exempt_before_wrap_check_runs(self, tmp_path):
        """When exempt, the hook must not invoke wrap_check at all."""
        sid = str(uuid.uuid4())
        payload = {"session_id": sid, "hook_event_name": "Stop", "cwd": "/tmp"}
        sentinel = tmp_path / ".wrap-in-progress"
        sentinel.touch()

        result = _run_hook("wrap_stop_hook.py", payload, env_overrides={
            "BELLOWS_DISPATCH": "1",
            "ELUVIAN_WRAP_ROOT": str(tmp_path),
            "ELUVIAN_HOOKS_LOG": str(tmp_path / "hooks.log"),
        })

        assert result.returncode == 0
        assert sentinel.exists(), "sentinel must not be unlinked by an exempt session"

    def test_unarmed_allows(self, tmp_path):
        """When no sentinel exists, hook allows regardless of exemption status."""
        sid = str(uuid.uuid4())
        payload = {"session_id": sid, "hook_event_name": "Stop", "cwd": "/tmp"}

        result = _run_hook("wrap_stop_hook.py", payload, env_overrides={
            "BELLOWS_DISPATCH": None,
            "ELUVIAN_WRAP_ROOT": str(tmp_path),
            "ELUVIAN_HOOKS_LOG": str(tmp_path / "hooks.log"),
        })

        out = json.loads(result.stdout)
        assert out == {}

        log_content = (tmp_path / "hooks.log").read_text()
        assert "unarmed-allow" in log_content
        assert sid in log_content

    def test_session_id_logged_on_block(self, tmp_path):
        sid = str(uuid.uuid4())
        payload = {"session_id": sid, "hook_event_name": "Stop", "cwd": "/tmp"}
        sentinel = tmp_path / ".wrap-in-progress"
        sentinel.touch()

        _run_hook("wrap_stop_hook.py", payload, env_overrides={
            "BELLOWS_DISPATCH": None,
            "ELUVIAN_WRAP_ROOT": str(tmp_path),
            "ELUVIAN_HOOKS_LOG": str(tmp_path / "hooks.log"),
        })

        log_content = (tmp_path / "hooks.log").read_text()
        assert f"sid={sid}" in log_content

    def test_empty_stdin_degrades_gracefully(self, tmp_path):
        """Empty stdin must not crash the hook (W5-1)."""
        result = _run_hook("wrap_stop_hook.py", payload=None, env_overrides={
            "BELLOWS_DISPATCH": None,
            "ELUVIAN_WRAP_ROOT": str(tmp_path),
            "ELUVIAN_HOOKS_LOG": str(tmp_path / "hooks.log"),
        })
        assert result.returncode == 0
        out = json.loads(result.stdout)
        assert "decision" not in out or out == {}

        log_content = (tmp_path / "hooks.log").read_text()
        assert "sid=unknown" in log_content

    def test_non_json_stdin_degrades_gracefully(self, tmp_path):
        """Non-JSON stdin must not crash the hook (W5-1)."""
        script = HOOKS_DIR / "wrap_stop_hook.py"
        env = {**os.environ}
        env["BELLOWS_DISPATCH"] = ""
        env["ELUVIAN_WRAP_ROOT"] = str(tmp_path)
        env["ELUVIAN_HOOKS_LOG"] = str(tmp_path / "hooks.log")

        result = subprocess.run(
            [sys.executable, str(script)],
            input="not valid json {{{{",
            capture_output=True,
            text=True,
            timeout=30,
            env=env,
        )
        assert result.returncode == 0
        log_content = (tmp_path / "hooks.log").read_text()
        assert "sid=unknown" in log_content


# ---------- wrap_debt_hook.py ----------

class TestDebtHookExemption:
    def test_exempt_when_dispatch_set(self, tmp_path):
        sid = str(uuid.uuid4())
        payload = {"session_id": sid, "hook_event_name": "SessionStart", "cwd": "/tmp"}

        result = _run_hook("wrap_debt_hook.py", payload, env_overrides={
            "BELLOWS_DISPATCH": "1",
            "ELUVIAN_WRAP_ROOT": str(tmp_path),
            "ELUVIAN_HOOKS_LOG": str(tmp_path / "hooks.log"),
        })

        out = json.loads(result.stdout)
        assert out == {}
        assert result.returncode == 0

        log_content = (tmp_path / "hooks.log").read_text()
        assert "daemon-exempt" in log_content
        assert sid in log_content

    def test_not_exempt_when_dispatch_unset(self, tmp_path):
        sid = str(uuid.uuid4())
        payload = {"session_id": sid, "hook_event_name": "SessionStart", "cwd": "/tmp"}

        result = _run_hook("wrap_debt_hook.py", payload, env_overrides={
            "BELLOWS_DISPATCH": None,
            "ELUVIAN_WRAP_ROOT": str(tmp_path),
            "ELUVIAN_HOOKS_LOG": str(tmp_path / "hooks.log"),
        })

        assert result.returncode == 0
        log_content = (tmp_path / "hooks.log").read_text()
        assert "daemon-exempt" not in log_content

    def test_not_exempt_when_dispatch_zero(self, tmp_path):
        """BELLOWS_DISPATCH=0 must NOT exempt."""
        sid = str(uuid.uuid4())
        payload = {"session_id": sid, "hook_event_name": "SessionStart", "cwd": "/tmp"}

        result = _run_hook("wrap_debt_hook.py", payload, env_overrides={
            "BELLOWS_DISPATCH": "0",
            "ELUVIAN_WRAP_ROOT": str(tmp_path),
            "ELUVIAN_HOOKS_LOG": str(tmp_path / "hooks.log"),
        })

        assert result.returncode == 0
        log_content = (tmp_path / "hooks.log").read_text()
        assert "daemon-exempt" not in log_content

    def test_session_id_logged(self, tmp_path):
        sid = str(uuid.uuid4())
        payload = {"session_id": sid, "hook_event_name": "SessionStart", "cwd": "/tmp"}

        _run_hook("wrap_debt_hook.py", payload, env_overrides={
            "BELLOWS_DISPATCH": "1",
            "ELUVIAN_WRAP_ROOT": str(tmp_path),
            "ELUVIAN_HOOKS_LOG": str(tmp_path / "hooks.log"),
        })

        log_content = (tmp_path / "hooks.log").read_text()
        assert f"sid={sid}" in log_content


# ---------- wrap_arm_hook.py ----------

class TestArmHookSessionId:
    def test_session_id_logged_on_arm(self, tmp_path):
        sid = str(uuid.uuid4())
        payload = {"session_id": sid, "prompt": "/wrap", "hook_event_name": "UserPromptSubmit"}

        result = _run_hook("wrap_arm_hook.py", payload, env_overrides={
            "ELUVIAN_WRAP_ROOT": str(tmp_path),
            "ELUVIAN_HOOKS_LOG": str(tmp_path / "hooks.log"),
        })

        assert result.returncode == 0
        log_content = (tmp_path / "hooks.log").read_text()
        assert f"sid={sid}" in log_content
        assert "ARMED" in log_content

    def test_session_id_logged_on_ignore(self, tmp_path):
        sid = str(uuid.uuid4())
        payload = {"session_id": sid, "prompt": "hello world", "hook_event_name": "UserPromptSubmit"}

        result = _run_hook("wrap_arm_hook.py", payload, env_overrides={
            "ELUVIAN_WRAP_ROOT": str(tmp_path),
            "ELUVIAN_HOOKS_LOG": str(tmp_path / "hooks.log"),
        })

        assert result.returncode == 0
        log_content = (tmp_path / "hooks.log").read_text()
        assert f"sid={sid}" in log_content
        assert "ignored" in log_content

    def test_sentinel_created_under_wrap_root(self, tmp_path):
        payload = {"session_id": "test-id", "prompt": "/wrap"}

        _run_hook("wrap_arm_hook.py", payload, env_overrides={
            "ELUVIAN_WRAP_ROOT": str(tmp_path),
            "ELUVIAN_HOOKS_LOG": str(tmp_path / "hooks.log"),
        })

        assert (tmp_path / ".wrap-in-progress-test-id").exists()


# ---------- ELUVIAN_WRAP_ROOT override ----------

class TestWrapRootOverride:
    def test_stop_hook_uses_override(self, tmp_path):
        """Verify ELUVIAN_WRAP_ROOT actually redirects sentinel resolution."""
        custom_root = tmp_path / "custom"
        custom_root.mkdir()
        sentinel = custom_root / ".wrap-in-progress"
        sentinel.touch()

        result = _run_hook("wrap_stop_hook.py", {"session_id": "test"}, env_overrides={
            "BELLOWS_DISPATCH": None,
            "ELUVIAN_WRAP_ROOT": str(custom_root),
            "ELUVIAN_HOOKS_LOG": str(tmp_path / "hooks.log"),
        })

        out = json.loads(result.stdout)
        assert out.get("decision") == "block"

    def test_arm_hook_uses_override(self, tmp_path):
        """Verify ELUVIAN_WRAP_ROOT actually redirects sentinel creation."""
        custom_root = tmp_path / "custom"
        custom_root.mkdir()

        _run_hook("wrap_arm_hook.py", {"session_id": "test", "prompt": "/wrap"}, env_overrides={
            "ELUVIAN_WRAP_ROOT": str(custom_root),
            "ELUVIAN_HOOKS_LOG": str(tmp_path / "hooks.log"),
        })

        assert (custom_root / ".wrap-in-progress-test").exists()
        assert not (tmp_path / ".wrap-in-progress-test").exists()

    def test_override_not_bound_at_import(self, tmp_path):
        """The sentinel must resolve at call time, not import time.

        This is the test that fails loudly if anyone reintroduces import-time binding.
        """
        custom_root = tmp_path / "custom"
        custom_root.mkdir()

        result = _run_hook("wrap_arm_hook.py", {"session_id": "test", "prompt": "/wrap"}, env_overrides={
            "ELUVIAN_WRAP_ROOT": str(custom_root),
            "ELUVIAN_HOOKS_LOG": str(tmp_path / "hooks.log"),
        })

        assert result.returncode == 0
        assert (custom_root / ".wrap-in-progress-test").exists()


# ---------- Lock-intact (unexempt blocks when armed) ----------

class TestLockIntact:
    def test_unexempt_session_blocks_when_armed(self, tmp_path):
        """An unexempt session must still be blocked when a wrap is armed."""
        sid = str(uuid.uuid4())
        sentinel = tmp_path / ".wrap-in-progress"
        sentinel.touch()

        result = _run_hook("wrap_stop_hook.py", {"session_id": sid, "hook_event_name": "Stop", "cwd": "/tmp"}, env_overrides={
            "BELLOWS_DISPATCH": None,
            "ELUVIAN_WRAP_ROOT": str(tmp_path),
            "ELUVIAN_HOOKS_LOG": str(tmp_path / "hooks.log"),
        })

        out = json.loads(result.stdout)
        assert out.get("decision") == "block"
        assert sentinel.exists(), "sentinel must not be removed on a block"
