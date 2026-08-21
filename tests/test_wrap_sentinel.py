"""Per-session sentinel ownership tests (plan 497, Step 1)."""
import json
import os
import shutil
import subprocess
import sys
import time
import uuid
from pathlib import Path

import pytest

HOOKS_DIR = Path(__file__).resolve().parent.parent / "hooks" / "eluvian"


@pytest.fixture(autouse=True)
def _isolate_sentinel_env(monkeypatch, tmp_path):
    """Isolate from real governance root and daemon exemption.

    BELLOWS_DISPATCH deleted — absence is safe (non-exempt).
    ELUVIAN_WRAP_ROOT SET to tmp_path — never deleted, that restores the
    real governance root and this module arms sentinels.
    """
    monkeypatch.delenv("BELLOWS_DISPATCH", raising=False)
    monkeypatch.setenv("ELUVIAN_WRAP_ROOT", str(tmp_path))
    monkeypatch.setenv("ELUVIAN_HOOKS_LOG", str(tmp_path / "hooks.log"))


def _run_hook(script_name, payload=None, env_overrides=None, script_dir=None):
    script = (script_dir or HOOKS_DIR) / script_name
    env = {**os.environ}
    if env_overrides:
        for k, v in env_overrides.items():
            if v is None:
                env.pop(k, None)
            else:
                env[k] = v
    stdin_data = json.dumps(payload) if payload is not None else ""
    return subprocess.run(
        [sys.executable, str(script)],
        input=stdin_data,
        capture_output=True,
        text=True,
        timeout=30,
        env=env,
    )


def _sentinels_in(directory):
    return sorted(
        p.name for p in Path(directory).glob(".wrap-in-progress*") if p.is_file()
    )


def _make_passcheck_dir(tmp_path):
    """Copy wrap_stop_hook.py next to a fake wrap_check that always exits 0.

    CHECK = Path(__file__).with_name("wrap_check.py") resolves to the fake,
    so the hook's pass branch is reachable without touching real repos.
    """
    d = tmp_path / "hooks_passcheck"
    d.mkdir(exist_ok=True)
    (d / "wrap_check.py").write_text(
        "import sys\nprint('wrap_check: OK')\nsys.exit(0)\n"
    )
    shutil.copy2(HOOKS_DIR / "wrap_stop_hook.py", d / "wrap_stop_hook.py")
    return d


# === Per-session arm ===

class TestPerSessionArm:
    def test_arm_creates_per_session_sentinel(self, tmp_path):
        sid = str(uuid.uuid4())
        _run_hook("wrap_arm_hook.py", {"session_id": sid, "prompt": "/wrap"})
        assert (tmp_path / f".wrap-in-progress-{sid}").exists()
        assert not (tmp_path / ".wrap-in-progress").exists()

    def test_arm_no_trigger_no_sentinel(self, tmp_path):
        sid = str(uuid.uuid4())
        _run_hook("wrap_arm_hook.py", {"session_id": sid, "prompt": "hello world"})
        assert not (tmp_path / f".wrap-in-progress-{sid}").exists()


# === Arm/stop round-trip ===

class TestArmStopRoundTrip:
    def test_arm_then_pass_clears_own(self, tmp_path):
        sid = str(uuid.uuid4())
        _run_hook("wrap_arm_hook.py", {"session_id": sid, "prompt": "/wrap"})
        assert (tmp_path / f".wrap-in-progress-{sid}").exists()

        hook_dir = _make_passcheck_dir(tmp_path)
        result = _run_hook("wrap_stop_hook.py", {"session_id": sid}, script_dir=hook_dir)
        assert json.loads(result.stdout) == {}
        assert not (tmp_path / f".wrap-in-progress-{sid}").exists()


# === Disarm defect (THE critical test) ===

class TestDisarmDefect:
    def test_b_cannot_clear_a_on_block(self, tmp_path):
        sid_a, sid_b = str(uuid.uuid4()), str(uuid.uuid4())
        (tmp_path / f".wrap-in-progress-{sid_a}").touch()
        (tmp_path / f".wrap-in-progress-{sid_b}").touch()

        result = _run_hook("wrap_stop_hook.py", {"session_id": sid_b})
        assert json.loads(result.stdout).get("decision") == "block"
        assert (tmp_path / f".wrap-in-progress-{sid_a}").exists()
        assert (tmp_path / f".wrap-in-progress-{sid_b}").exists()

    def test_b_removes_only_own_on_pass(self, tmp_path):
        """The single most important assertion: on pass, B removes only its own."""
        sid_a, sid_b = str(uuid.uuid4()), str(uuid.uuid4())
        (tmp_path / f".wrap-in-progress-{sid_a}").touch()
        (tmp_path / f".wrap-in-progress-{sid_b}").touch()

        hook_dir = _make_passcheck_dir(tmp_path)
        result = _run_hook("wrap_stop_hook.py", {"session_id": sid_b}, script_dir=hook_dir)
        assert json.loads(result.stdout) == {}
        assert (tmp_path / f".wrap-in-progress-{sid_a}").exists(), \
            "session B MUST NOT remove session A's sentinel even on pass"
        assert not (tmp_path / f".wrap-in-progress-{sid_b}").exists()

    def test_a_can_still_clear_own_on_pass(self, tmp_path):
        """A lock that can be armed can still be cleared."""
        sid_a = str(uuid.uuid4())
        (tmp_path / f".wrap-in-progress-{sid_a}").touch()

        hook_dir = _make_passcheck_dir(tmp_path)
        result = _run_hook("wrap_stop_hook.py", {"session_id": sid_a}, script_dir=hook_dir)
        assert json.loads(result.stdout) == {}
        assert not (tmp_path / f".wrap-in-progress-{sid_a}").exists()


# === ARM-IF-ANY ===

class TestArmIfAny:
    def test_blocks_on_foreign_sentinel_when_unarmed(self, tmp_path):
        sid_a, sid_b = str(uuid.uuid4()), str(uuid.uuid4())
        (tmp_path / f".wrap-in-progress-{sid_a}").touch()

        result = _run_hook("wrap_stop_hook.py", {"session_id": sid_b})
        assert json.loads(result.stdout).get("decision") == "block"
        assert (tmp_path / f".wrap-in-progress-{sid_a}").exists()

    def test_blocks_on_both_armed(self, tmp_path):
        sid_a, sid_b = str(uuid.uuid4()), str(uuid.uuid4())
        (tmp_path / f".wrap-in-progress-{sid_a}").touch()
        (tmp_path / f".wrap-in-progress-{sid_b}").touch()

        result = _run_hook("wrap_stop_hook.py", {"session_id": sid_b})
        assert json.loads(result.stdout).get("decision") == "block"


# === Legacy bare sentinel ===

class TestBareSentinel:
    def test_bare_still_blocks(self, tmp_path):
        (tmp_path / ".wrap-in-progress").touch()
        result = _run_hook("wrap_stop_hook.py", {"session_id": str(uuid.uuid4())})
        assert json.loads(result.stdout).get("decision") == "block"

    def test_bare_clears_on_pass(self, tmp_path):
        (tmp_path / ".wrap-in-progress").touch()
        hook_dir = _make_passcheck_dir(tmp_path)
        result = _run_hook(
            "wrap_stop_hook.py", {"session_id": str(uuid.uuid4())}, script_dir=hook_dir,
        )
        assert json.loads(result.stdout) == {}
        assert not (tmp_path / ".wrap-in-progress").exists()

    def test_bare_never_renamed_on_block(self, tmp_path):
        sid = str(uuid.uuid4())
        (tmp_path / ".wrap-in-progress").touch()
        _run_hook("wrap_stop_hook.py", {"session_id": sid})
        assert (tmp_path / ".wrap-in-progress").exists()
        assert not (tmp_path / f".wrap-in-progress-{sid}").exists()

    def test_bare_never_renamed_on_pass(self, tmp_path):
        sid = str(uuid.uuid4())
        (tmp_path / ".wrap-in-progress").touch()
        hook_dir = _make_passcheck_dir(tmp_path)
        _run_hook("wrap_stop_hook.py", {"session_id": sid}, script_dir=hook_dir)
        assert not (tmp_path / ".wrap-in-progress").exists()
        assert not (tmp_path / f".wrap-in-progress-{sid}").exists()


# === Session ID fallback ===

class TestSessionIdFallback:
    def test_missing_id_arms_bare(self, tmp_path):
        _run_hook("wrap_arm_hook.py", {"prompt": "/wrap"})
        assert (tmp_path / ".wrap-in-progress").exists()

    def test_empty_id_arms_bare(self, tmp_path):
        _run_hook("wrap_arm_hook.py", {"session_id": "", "prompt": "/wrap"})
        assert (tmp_path / ".wrap-in-progress").exists()
        sents = _sentinels_in(tmp_path)
        assert sents == [".wrap-in-progress"], \
            f"only bare sentinel expected, got {sents}"

    def test_invalid_charset_arms_bare(self, tmp_path):
        _run_hook("wrap_arm_hook.py", {"session_id": "../etc/passwd", "prompt": "/wrap"})
        assert (tmp_path / ".wrap-in-progress").exists()

    def test_missing_id_stop_uses_bare(self, tmp_path):
        (tmp_path / ".wrap-in-progress").touch()
        hook_dir = _make_passcheck_dir(tmp_path)
        result = _run_hook("wrap_stop_hook.py", {}, script_dir=hook_dir)
        assert json.loads(result.stdout) == {}
        assert not (tmp_path / ".wrap-in-progress").exists()

    def test_empty_stdin_arm_does_not_crash(self, tmp_path):
        result = _run_hook("wrap_arm_hook.py", payload=None)
        assert result.returncode == 0

    def test_empty_stdin_stop_does_not_crash(self, tmp_path):
        result = _run_hook("wrap_stop_hook.py", payload=None)
        assert result.returncode == 0


# === Anti-hijack message ===

class TestAntiHijackMessage:
    def test_names_foreign_sentinel(self, tmp_path):
        sid_a, sid_b = str(uuid.uuid4()), str(uuid.uuid4())
        (tmp_path / f".wrap-in-progress-{sid_a}").touch()
        (tmp_path / f".wrap-in-progress-{sid_b}").touch()

        result = _run_hook("wrap_stop_hook.py", {"session_id": sid_b})
        reason = json.loads(result.stdout).get("reason", "")
        assert f".wrap-in-progress-{sid_a}" in reason

    def test_includes_age(self, tmp_path):
        sid_a, sid_b = str(uuid.uuid4()), str(uuid.uuid4())
        sentinel_a = tmp_path / f".wrap-in-progress-{sid_a}"
        sentinel_a.touch()
        old_time = time.time() - 300
        os.utime(str(sentinel_a), (old_time, old_time))
        (tmp_path / f".wrap-in-progress-{sid_b}").touch()

        result = _run_hook("wrap_stop_hook.py", {"session_id": sid_b})
        reason = json.loads(result.stdout).get("reason", "")
        assert "age:" in reason

    def test_instructs_waiting(self, tmp_path):
        sid_a, sid_b = str(uuid.uuid4()), str(uuid.uuid4())
        (tmp_path / f".wrap-in-progress-{sid_a}").touch()
        (tmp_path / f".wrap-in-progress-{sid_b}").touch()

        result = _run_hook("wrap_stop_hook.py", {"session_id": sid_b})
        reason = json.loads(result.stdout).get("reason", "")
        assert "wait" in reason.lower()
        assert "Do NOT" in reason

    def test_unarmed_b_sees_a_message(self, tmp_path):
        sid_a, sid_b = str(uuid.uuid4()), str(uuid.uuid4())
        (tmp_path / f".wrap-in-progress-{sid_a}").touch()

        result = _run_hook("wrap_stop_hook.py", {"session_id": sid_b})
        reason = json.loads(result.stdout).get("reason", "")
        assert f".wrap-in-progress-{sid_a}" in reason


# === Stale reaper ===

class TestStaleReaper:
    def test_reaps_stale_foreign_sentinel(self, tmp_path):
        sid_me, sid_old = str(uuid.uuid4()), str(uuid.uuid4())
        stale = tmp_path / f".wrap-in-progress-{sid_old}"
        stale.touch()
        old_time = time.time() - 14401
        os.utime(str(stale), (old_time, old_time))

        result = _run_hook("wrap_stop_hook.py", {"session_id": sid_me})
        assert not stale.exists(), "stale foreign sentinel should be reaped"
        assert json.loads(result.stdout) == {}, "should allow after reaping sole sentinel"

    def test_does_not_reap_fresh_foreign(self, tmp_path):
        sid_me, sid_fresh = str(uuid.uuid4()), str(uuid.uuid4())
        fresh = tmp_path / f".wrap-in-progress-{sid_fresh}"
        fresh.touch()

        _run_hook("wrap_stop_hook.py", {"session_id": sid_me})
        assert fresh.exists(), "fresh foreign sentinel must not be reaped"

    def test_does_not_reap_own(self, tmp_path):
        sid = str(uuid.uuid4())
        own = tmp_path / f".wrap-in-progress-{sid}"
        own.touch()
        old_time = time.time() - 14401
        os.utime(str(own), (old_time, old_time))

        _run_hook("wrap_stop_hook.py", {"session_id": sid})
        assert own.exists(), "own sentinel must not be reaped even if stale"

    def test_does_not_reap_bare(self, tmp_path):
        sid = str(uuid.uuid4())
        bare = tmp_path / ".wrap-in-progress"
        bare.touch()
        old_time = time.time() - 14401
        os.utime(str(bare), (old_time, old_time))

        _run_hook("wrap_stop_hook.py", {"session_id": sid})
        assert bare.exists(), "bare sentinel must never be reaped"


# === Module import (Python 3.9.6 compat) ===

class TestModuleImport:
    def test_stop_hook_imports(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "wrap_stop_hook", str(HOOKS_DIR / "wrap_stop_hook.py"),
        )
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        assert hasattr(mod, "main")

    def test_arm_hook_imports(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "wrap_arm_hook", str(HOOKS_DIR / "wrap_arm_hook.py"),
        )
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        assert hasattr(mod, "main")
