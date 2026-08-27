"""Tests for plan_claim — fork-1 claim shim."""

import importlib
import os
import subprocess
import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest

import lifecycle
import plan_claim


@pytest.fixture(autouse=True)
def reset_memos():
    plan_claim._reset_memo()
    yield
    plan_claim._reset_memo()


def _make_log():
    calls = []
    def log(level, msg, **kwargs):
        calls.append((level, msg, kwargs))
    log.calls = calls
    return log


# ---------------------------------------------------------------------------
# (1) Off-mode no-op (claim side)
# ---------------------------------------------------------------------------

class TestOffModeNoOp:
    def test_claim_gate_no_key(self, monkeypatch):
        monkeypatch.setattr(subprocess, "run", MagicMock(side_effect=AssertionError("seam touched")))
        log = _make_log()
        assert plan_claim.claim_gate("test-plan.md", "abc123", {}, log) is True

    def test_claim_gate_off_key(self, monkeypatch):
        monkeypatch.setattr(subprocess, "run", MagicMock(side_effect=AssertionError("seam touched")))
        log = _make_log()
        assert plan_claim.claim_gate("test-plan.md", "abc123", {"plan_claim_lock": "off"}, log) is True

    def test_claim_for_deposit_off(self, monkeypatch):
        monkeypatch.setattr(subprocess, "run", MagicMock(side_effect=AssertionError("seam touched")))
        outcome, detail = plan_claim.claim_for_deposit("test-plan.md", "abc123", {"plan_claim_lock": "off"})
        assert outcome == "proceed"
        assert "mode-off" in detail

    def test_release_off_mode_with_checkout_attempts(self, monkeypatch, tmp_path):
        """Release is NOT mode-gated — in off mode with a resolvable checkout, it DOES attempt."""
        tuyere = tmp_path / "tuyere"
        (tuyere / ".venv" / "bin").mkdir(parents=True)
        (tuyere / ".venv" / "bin" / "python").touch()
        monkeypatch.setenv("ELUVIAN_WRAP_TUYERE", str(tuyere))

        db_path = str(tmp_path / "lifecycle.db")
        lifecycle.init_lifecycle_db(db_path)
        monkeypatch.setattr(lifecycle, "LIFECYCLE_DB_PATH", db_path)
        conn = __import__("sqlite3").connect(db_path)
        conn.execute("UPDATE id_sequence SET next_id = 100")
        conn.commit()
        conn.close()
        plan_id = lifecycle.mint_and_claim("executable", "/tmp", "test", "", "", 1,
                                           "test-plan.md", db_path)

        run_mock = MagicMock(return_value=MagicMock(returncode=0, stdout="released\n", stderr=""))
        monkeypatch.setattr(subprocess, "run", run_mock)
        log = _make_log()
        plan_claim.release_for_plan(plan_id, "test", {"plan_claim_lock": "off"}, log)
        assert run_mock.called

    def test_release_off_mode_checkout_unresolvable(self, monkeypatch, tmp_path):
        """Release with checkout unresolvable returns after one quiet line, no subprocess."""
        monkeypatch.delenv("ELUVIAN_WRAP_TUYERE", raising=False)
        monkeypatch.delenv("ELUVIAN_WRAP_ROOT", raising=False)
        monkeypatch.setattr(Path, "home", lambda: tmp_path / "nohome")
        run_mock = MagicMock(side_effect=AssertionError("seam touched"))
        monkeypatch.setattr(subprocess, "run", run_mock)

        db_path = str(tmp_path / "lifecycle.db")
        lifecycle.init_lifecycle_db(db_path)
        monkeypatch.setattr(lifecycle, "LIFECYCLE_DB_PATH", db_path)
        plan_id = lifecycle.mint_and_claim("executable", "/tmp", "test", "", "", 1,
                                           "test-plan.md", db_path)

        log = _make_log()
        plan_claim.release_for_plan(plan_id, "test", {"plan_claim_lock": "off"}, log)
        assert not run_mock.called
        assert any("unresolvable" in msg for _, msg, _ in log.calls)


# ---------------------------------------------------------------------------
# (2) Decision table: claim_gate bool + logged text
# ---------------------------------------------------------------------------

class TestDecisionTable:
    @pytest.fixture
    def setup_claim(self, monkeypatch, tmp_path):
        db_path = str(tmp_path / "lifecycle.db")
        lifecycle.init_lifecycle_db(db_path)
        monkeypatch.setattr(lifecycle, "LIFECYCLE_DB_PATH", db_path)
        lifecycle.write_clearance("test-plan.md", "hash1", "shop-infra", "depositor", db_path)

        tuyere = tmp_path / "tuyere"
        (tuyere / ".venv" / "bin").mkdir(parents=True)
        (tuyere / ".venv" / "bin" / "python").touch()
        monkeypatch.setenv("ELUVIAN_WRAP_TUYERE", str(tuyere))
        return db_path

    def _run_gate(self, monkeypatch, rc, stdout="", stderr="", mode="advisory",
                  timeout=False, exception=None):
        if timeout:
            monkeypatch.setattr(subprocess, "run",
                                MagicMock(side_effect=subprocess.TimeoutExpired("cmd", 10)))
        elif exception:
            monkeypatch.setattr(subprocess, "run",
                                MagicMock(side_effect=exception))
        else:
            monkeypatch.setattr(subprocess, "run",
                                MagicMock(return_value=MagicMock(returncode=rc, stdout=stdout, stderr=stderr)))
        log = _make_log()
        config = {"plan_claim_lock": mode}
        result = plan_claim.claim_gate("test-plan.md", "hash1", config, log)
        return result, log

    def test_advisory_rc0(self, monkeypatch, setup_claim):
        result, log = self._run_gate(monkeypatch, 0, stdout="claimed slug seq=1 machine=mini\n", mode="advisory")
        assert result is True

    def test_required_rc0(self, monkeypatch, setup_claim):
        result, log = self._run_gate(monkeypatch, 0, stdout="claimed slug seq=1 machine=mini\n", mode="required")
        assert result is True

    def test_advisory_rc3(self, monkeypatch, setup_claim):
        result, log = self._run_gate(monkeypatch, 3, stdout="held by machine=shop\n", mode="advisory")
        assert result is False
        assert any("declined" in msg and "exit 3" in msg for _, msg, _ in log.calls)
        assert any("self-strand" in msg for _, msg, _ in log.calls)

    def test_required_rc3(self, monkeypatch, setup_claim):
        result, log = self._run_gate(monkeypatch, 3, stdout="held by machine=shop\n", mode="required")
        assert result is False
        assert any("self-strand" in msg for _, msg, _ in log.calls)

    def test_advisory_rc4_stderr_reason(self, monkeypatch, setup_claim):
        result, log = self._run_gate(monkeypatch, 4, stdout="", stderr="class not eligible\n", mode="advisory")
        assert result is False
        assert any("exit 4" in msg and "class not eligible" in msg for _, msg, _ in log.calls)

    def test_required_rc4(self, monkeypatch, setup_claim):
        result, log = self._run_gate(monkeypatch, 4, stdout="", stderr="class not eligible\n", mode="required")
        assert result is False

    def test_advisory_rc5(self, monkeypatch, setup_claim):
        result, log = self._run_gate(monkeypatch, 5, stderr="internal error\n", mode="advisory")
        assert result is True
        assert any("ADVISORY-ERROR" in msg for _, msg, _ in log.calls)

    def test_required_rc5(self, monkeypatch, setup_claim):
        result, log = self._run_gate(monkeypatch, 5, stderr="internal error\n", mode="required")
        assert result is False
        assert any("blocked" in msg for _, msg, _ in log.calls)

    def test_advisory_timeout(self, monkeypatch, setup_claim):
        result, log = self._run_gate(monkeypatch, 0, mode="advisory", timeout=True)
        assert result is True
        assert any("ADVISORY-ERROR" in msg for _, msg, _ in log.calls)

    def test_required_timeout(self, monkeypatch, setup_claim):
        result, log = self._run_gate(monkeypatch, 0, mode="required", timeout=True)
        assert result is False

    def test_advisory_class_none(self, monkeypatch, tmp_path):
        db_path = str(tmp_path / "lifecycle.db")
        lifecycle.init_lifecycle_db(db_path)
        monkeypatch.setattr(lifecycle, "LIFECYCLE_DB_PATH", db_path)

        tuyere = tmp_path / "tuyere"
        (tuyere / ".venv" / "bin").mkdir(parents=True)
        (tuyere / ".venv" / "bin" / "python").touch()
        monkeypatch.setenv("ELUVIAN_WRAP_TUYERE", str(tuyere))

        run_mock = MagicMock(side_effect=AssertionError("seam touched"))
        monkeypatch.setattr(subprocess, "run", run_mock)
        log = _make_log()
        result = plan_claim.claim_gate("test-plan.md", "nohash", {"plan_claim_lock": "advisory"}, log)
        assert result is True
        assert any("ADVISORY-ERROR" in msg for _, msg, _ in log.calls)
        assert not run_mock.called

    def test_required_class_none(self, monkeypatch, tmp_path):
        db_path = str(tmp_path / "lifecycle.db")
        lifecycle.init_lifecycle_db(db_path)
        monkeypatch.setattr(lifecycle, "LIFECYCLE_DB_PATH", db_path)

        tuyere = tmp_path / "tuyere"
        (tuyere / ".venv" / "bin").mkdir(parents=True)
        (tuyere / ".venv" / "bin" / "python").touch()
        monkeypatch.setenv("ELUVIAN_WRAP_TUYERE", str(tuyere))

        log = _make_log()
        result = plan_claim.claim_gate("test-plan.md", "nohash", {"plan_claim_lock": "required"}, log)
        assert result is False
        assert any("blocked" in msg for _, msg, _ in log.calls)

    def test_advisory_checkout_none(self, monkeypatch, tmp_path):
        db_path = str(tmp_path / "lifecycle.db")
        lifecycle.init_lifecycle_db(db_path)
        monkeypatch.setattr(lifecycle, "LIFECYCLE_DB_PATH", db_path)
        lifecycle.write_clearance("test-plan.md", "hash1", "shop-infra", "depositor", db_path)

        monkeypatch.delenv("ELUVIAN_WRAP_TUYERE", raising=False)
        monkeypatch.delenv("ELUVIAN_WRAP_ROOT", raising=False)
        monkeypatch.setattr(Path, "home", lambda: tmp_path / "nohome")

        log = _make_log()
        result = plan_claim.claim_gate("test-plan.md", "hash1", {"plan_claim_lock": "advisory"}, log)
        assert result is True
        assert any("ADVISORY-ERROR" in msg for _, msg, _ in log.calls)

    def test_required_checkout_none(self, monkeypatch, tmp_path):
        db_path = str(tmp_path / "lifecycle.db")
        lifecycle.init_lifecycle_db(db_path)
        monkeypatch.setattr(lifecycle, "LIFECYCLE_DB_PATH", db_path)
        lifecycle.write_clearance("test-plan.md", "hash1", "shop-infra", "depositor", db_path)

        monkeypatch.delenv("ELUVIAN_WRAP_TUYERE", raising=False)
        monkeypatch.delenv("ELUVIAN_WRAP_ROOT", raising=False)
        monkeypatch.setattr(Path, "home", lambda: tmp_path / "nohome")

        log = _make_log()
        result = plan_claim.claim_gate("test-plan.md", "hash1", {"plan_claim_lock": "required"}, log)
        assert result is False


# ---------------------------------------------------------------------------
# (3) Unknown mode → behaves as required + WARN
# ---------------------------------------------------------------------------

class TestUnknownMode:
    def test_unknown_mode_treated_as_required(self, monkeypatch, tmp_path):
        db_path = str(tmp_path / "lifecycle.db")
        lifecycle.init_lifecycle_db(db_path)
        monkeypatch.setattr(lifecycle, "LIFECYCLE_DB_PATH", db_path)
        lifecycle.write_clearance("test-plan.md", "hash1", "shop-infra", "depositor", db_path)

        tuyere = tmp_path / "tuyere"
        (tuyere / ".venv" / "bin").mkdir(parents=True)
        (tuyere / ".venv" / "bin" / "python").touch()
        monkeypatch.setenv("ELUVIAN_WRAP_TUYERE", str(tuyere))

        monkeypatch.setattr(subprocess, "run",
                            MagicMock(return_value=MagicMock(returncode=5, stdout="", stderr="err\n")))
        log = _make_log()
        config = {"plan_claim_lock": "bogus_value"}
        result = plan_claim.claim_gate("test-plan.md", "hash1", config, log)
        assert result is False
        assert any("blocked" in msg for _, msg, _ in log.calls)

    def test_unknown_mode_warn_logged(self, caplog):
        import logging
        with caplog.at_level(logging.WARNING, logger="bellows"):
            plan_claim._mode({"plan_claim_lock": "bogus_value"})
        assert any("unrecognized" in r.message for r in caplog.records)


# ---------------------------------------------------------------------------
# (4) Resolver twin drift guard
# ---------------------------------------------------------------------------

class TestResolverTwin:
    def _import_wrap_check(self):
        wrap_check_path = os.path.join(os.path.dirname(__file__), "..", "hooks", "eluvian", "wrap_check.py")
        wrap_check_path = os.path.abspath(wrap_check_path)
        import importlib.util
        spec = importlib.util.spec_from_file_location("wrap_check", wrap_check_path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod

    def test_env_tuyere_override(self, monkeypatch, tmp_path):
        tuyere = tmp_path / "custom_tuyere"
        (tuyere / ".venv" / "bin").mkdir(parents=True)
        (tuyere / ".venv" / "bin" / "python").touch()
        monkeypatch.setenv("ELUVIAN_WRAP_TUYERE", str(tuyere))
        monkeypatch.delenv("ELUVIAN_WRAP_ROOT", raising=False)

        result_shim = plan_claim._tuyere_checkout()
        wc = self._import_wrap_check()
        result_wc = wc._tuyere_checkout()
        assert result_shim == result_wc
        assert result_shim == tuyere

    def test_home_developer_tuyere(self, monkeypatch, tmp_path):
        monkeypatch.delenv("ELUVIAN_WRAP_TUYERE", raising=False)
        monkeypatch.delenv("ELUVIAN_WRAP_ROOT", raising=False)
        home = tmp_path / "fakehome"
        (home / "Developer" / "tuyere" / ".venv" / "bin").mkdir(parents=True)
        (home / "Developer" / "tuyere" / ".venv" / "bin" / "python").touch()
        monkeypatch.setattr(Path, "home", lambda: home)

        result_shim = plan_claim._tuyere_checkout()
        wc = self._import_wrap_check()
        result_wc = wc._tuyere_checkout()
        assert result_shim == result_wc
        assert result_shim == home / "Developer" / "tuyere"

    def test_root_env_tuyere(self, monkeypatch, tmp_path):
        monkeypatch.delenv("ELUVIAN_WRAP_TUYERE", raising=False)
        root = tmp_path / "myroot"
        (root / "tuyere" / ".venv" / "bin").mkdir(parents=True)
        (root / "tuyere" / ".venv" / "bin" / "python").touch()
        monkeypatch.setenv("ELUVIAN_WRAP_ROOT", str(root))
        monkeypatch.setattr(Path, "home", lambda: tmp_path / "nohome")

        result_shim = plan_claim._tuyere_checkout()
        wc = self._import_wrap_check()
        result_wc = wc._tuyere_checkout()
        assert result_shim == result_wc
        assert result_shim == root / "tuyere"

    def test_both_none(self, monkeypatch, tmp_path):
        monkeypatch.delenv("ELUVIAN_WRAP_TUYERE", raising=False)
        monkeypatch.delenv("ELUVIAN_WRAP_ROOT", raising=False)
        monkeypatch.setattr(Path, "home", lambda: tmp_path / "nohome")

        result_shim = plan_claim._tuyere_checkout()
        assert result_shim is None

    def test_shim_reads_env_at_call_time(self, monkeypatch, tmp_path):
        """plan_claim reads env at CALL time — no reload needed (unlike wrap_check)."""
        monkeypatch.delenv("ELUVIAN_WRAP_TUYERE", raising=False)
        monkeypatch.delenv("ELUVIAN_WRAP_ROOT", raising=False)
        monkeypatch.setattr(Path, "home", lambda: tmp_path / "nohome")
        assert plan_claim._tuyere_checkout() is None

        tuyere = tmp_path / "late_tuyere"
        (tuyere / ".venv" / "bin").mkdir(parents=True)
        (tuyere / ".venv" / "bin" / "python").touch()
        monkeypatch.setenv("ELUVIAN_WRAP_TUYERE", str(tuyere))
        assert plan_claim._tuyere_checkout() == tuyere


# ---------------------------------------------------------------------------
# (5) Release best-effort
# ---------------------------------------------------------------------------

class TestReleaseBestEffort:
    @pytest.fixture
    def setup_release(self, monkeypatch, tmp_path):
        db_path = str(tmp_path / "lifecycle.db")
        lifecycle.init_lifecycle_db(db_path)
        monkeypatch.setattr(lifecycle, "LIFECYCLE_DB_PATH", db_path)
        plan_id = lifecycle.mint_and_claim("executable", "/tmp", "test", "", "", 1,
                                           "test-plan.md", db_path)
        tuyere = tmp_path / "tuyere"
        (tuyere / ".venv" / "bin").mkdir(parents=True)
        (tuyere / ".venv" / "bin" / "python").touch()
        monkeypatch.setenv("ELUVIAN_WRAP_TUYERE", str(tuyere))
        return plan_id

    def test_subprocess_raises_no_exception_escapes(self, monkeypatch, setup_release):
        monkeypatch.setattr(subprocess, "run",
                            MagicMock(side_effect=OSError("boom")))
        log = _make_log()
        plan_claim.release_for_plan(setup_release, "test", {}, log)
        assert any("ERROR" == lv and "boom" in msg for lv, msg, _ in log.calls)

    def test_timeout_no_exception_escapes(self, monkeypatch, setup_release):
        monkeypatch.setattr(subprocess, "run",
                            MagicMock(side_effect=subprocess.TimeoutExpired("cmd", 10)))
        log = _make_log()
        plan_claim.release_for_plan(setup_release, "test", {}, log)
        assert any("timeout" in msg for _, msg, _ in log.calls)

    def test_nonzero_no_exception_escapes(self, monkeypatch, setup_release):
        monkeypatch.setattr(subprocess, "run",
                            MagicMock(return_value=MagicMock(returncode=1, stdout="", stderr="db error\n")))
        log = _make_log()
        plan_claim.release_for_plan(setup_release, "test", {}, log)
        assert any("ERROR" == lv for lv, _, _ in log.calls)

    def test_loud_once_per_process(self, monkeypatch, setup_release):
        monkeypatch.setattr(subprocess, "run",
                            MagicMock(side_effect=OSError("boom")))
        log = _make_log()
        plan_claim.release_for_plan(setup_release, "test", {}, log)
        error_count_1 = sum(1 for lv, _, _ in log.calls if lv == "ERROR")
        assert error_count_1 == 1

        log2 = _make_log()
        plan_claim.release_for_plan(setup_release, "test", {}, log2)
        error_count_2 = sum(1 for lv, _, _ in log2.calls if lv == "ERROR")
        assert error_count_2 == 0

    def test_loud_again_after_success(self, monkeypatch, setup_release):
        monkeypatch.setattr(subprocess, "run",
                            MagicMock(side_effect=OSError("boom")))
        log = _make_log()
        plan_claim.release_for_plan(setup_release, "test", {}, log)
        assert sum(1 for lv, _, _ in log.calls if lv == "ERROR") == 1

        monkeypatch.setattr(subprocess, "run",
                            MagicMock(return_value=MagicMock(returncode=0, stdout="ok\n", stderr="")))
        log2 = _make_log()
        plan_claim.release_for_plan(setup_release, "test", {}, log2)

        monkeypatch.setattr(subprocess, "run",
                            MagicMock(side_effect=OSError("boom2")))
        log3 = _make_log()
        plan_claim.release_for_plan(setup_release, "test", {}, log3)
        assert sum(1 for lv, _, _ in log3.calls if lv == "ERROR") == 1

    def test_rc3_benign_info(self, monkeypatch, setup_release):
        monkeypatch.setattr(subprocess, "run",
                            MagicMock(return_value=MagicMock(returncode=3, stdout="no active claim\n", stderr="")))
        log = _make_log()
        plan_claim.release_for_plan(setup_release, "test", {}, log)
        assert any("INFO" == lv and "rc=3" in msg for lv, msg, _ in log.calls)
        assert not any(lv == "ERROR" for lv, _, _ in log.calls)

    def test_placeholder_none_early_return(self, monkeypatch, tmp_path):
        db_path = str(tmp_path / "lifecycle.db")
        lifecycle.init_lifecycle_db(db_path)
        monkeypatch.setattr(lifecycle, "LIFECYCLE_DB_PATH", db_path)

        run_mock = MagicMock(side_effect=AssertionError("seam touched"))
        monkeypatch.setattr(subprocess, "run", run_mock)
        log = _make_log()
        plan_claim.release_for_plan(99999, "test", {}, log)
        assert not run_mock.called

    def test_config_none_early_return(self, monkeypatch):
        run_mock = MagicMock(side_effect=AssertionError("seam touched"))
        monkeypatch.setattr(subprocess, "run", run_mock)
        log = _make_log()
        plan_claim.release_for_plan(1, "test", None, log)
        assert not run_mock.called


# ---------------------------------------------------------------------------
# (5b) Decline-log dedupe
# ---------------------------------------------------------------------------

class TestDeclineDedupe:
    @pytest.fixture
    def setup_dedupe(self, monkeypatch, tmp_path):
        db_path = str(tmp_path / "lifecycle.db")
        lifecycle.init_lifecycle_db(db_path)
        monkeypatch.setattr(lifecycle, "LIFECYCLE_DB_PATH", db_path)
        lifecycle.write_clearance("test-plan.md", "hash1", "shop-infra", "depositor", db_path)
        tuyere = tmp_path / "tuyere"
        (tuyere / ".venv" / "bin").mkdir(parents=True)
        (tuyere / ".venv" / "bin" / "python").touch()
        monkeypatch.setenv("ELUVIAN_WRAP_TUYERE", str(tuyere))
        return db_path

    def test_consecutive_declines_one_warn(self, monkeypatch, setup_dedupe):
        monkeypatch.setattr(subprocess, "run",
                            MagicMock(return_value=MagicMock(returncode=3, stdout="held\n", stderr="")))
        log1 = _make_log()
        plan_claim.claim_gate("test-plan.md", "hash1", {"plan_claim_lock": "required"}, log1)
        assert sum(1 for lv, _, _ in log1.calls if lv == "WARN") == 1

        log2 = _make_log()
        plan_claim.claim_gate("test-plan.md", "hash1", {"plan_claim_lock": "required"}, log2)
        assert sum(1 for lv, _, _ in log2.calls if lv in ("WARN", "ERROR")) == 0

    def test_outcome_change_logs_anew(self, monkeypatch, setup_dedupe):
        monkeypatch.setattr(subprocess, "run",
                            MagicMock(return_value=MagicMock(returncode=3, stdout="held\n", stderr="")))
        log1 = _make_log()
        plan_claim.claim_gate("test-plan.md", "hash1", {"plan_claim_lock": "required"}, log1)
        assert sum(1 for lv, _, _ in log1.calls if lv == "WARN") == 1

        monkeypatch.setattr(subprocess, "run",
                            MagicMock(return_value=MagicMock(returncode=5, stdout="", stderr="err\n")))
        log2 = _make_log()
        plan_claim.claim_gate("test-plan.md", "hash1", {"plan_claim_lock": "required"}, log2)
        assert sum(1 for lv, _, _ in log2.calls if lv == "ERROR") == 1

    def test_repeated_after_change_silent(self, monkeypatch, setup_dedupe):
        monkeypatch.setattr(subprocess, "run",
                            MagicMock(return_value=MagicMock(returncode=3, stdout="held\n", stderr="")))
        plan_claim.claim_gate("test-plan.md", "hash1", {"plan_claim_lock": "required"}, _make_log())

        monkeypatch.setattr(subprocess, "run",
                            MagicMock(return_value=MagicMock(returncode=5, stdout="", stderr="err\n")))
        plan_claim.claim_gate("test-plan.md", "hash1", {"plan_claim_lock": "required"}, _make_log())

        log3 = _make_log()
        plan_claim.claim_gate("test-plan.md", "hash1", {"plan_claim_lock": "required"}, log3)
        assert sum(1 for lv, _, _ in log3.calls if lv in ("WARN", "ERROR")) == 0

    def test_advisory_error_logs_every_time(self, monkeypatch, setup_dedupe):
        monkeypatch.setattr(subprocess, "run",
                            MagicMock(side_effect=subprocess.TimeoutExpired("cmd", 10)))
        log1 = _make_log()
        plan_claim.claim_gate("test-plan.md", "hash1", {"plan_claim_lock": "advisory"}, log1)
        assert any("ADVISORY-ERROR" in msg for _, msg, _ in log1.calls)

        log2 = _make_log()
        plan_claim.claim_gate("test-plan.md", "hash1", {"plan_claim_lock": "advisory"}, log2)
        assert any("ADVISORY-ERROR" in msg for _, msg, _ in log2.calls)

        log3 = _make_log()
        plan_claim.claim_gate("test-plan.md", "hash1", {"plan_claim_lock": "advisory"}, log3)
        assert any("ADVISORY-ERROR" in msg for _, msg, _ in log3.calls)


# ---------------------------------------------------------------------------
# (6) Slug parity (Z11)
# ---------------------------------------------------------------------------

class TestSlugParity:
    def test_slug_derivation_matches_depositor(self):
        for name in ["executable-x.md", "diagnostic-y.md"]:
            shim_slug = name[:-3]
            dep_slug = name
            if dep_slug.startswith("ready-"):
                dep_slug = dep_slug[len("ready-"):]
            if dep_slug.endswith(".md"):
                dep_slug = dep_slug[:-len(".md")]
            assert shim_slug == dep_slug


# ---------------------------------------------------------------------------
# (7) Helpers — lifecycle
# ---------------------------------------------------------------------------

class TestLifecycleHelpers:
    def test_active_clearance_class(self, tmp_path):
        db_path = str(tmp_path / "lifecycle.db")
        lifecycle.init_lifecycle_db(db_path)
        lifecycle.write_clearance("plan.md", "hash1", "shop-infra", "depositor", db_path)
        assert lifecycle.active_clearance_class("hash1", "plan.md", db_path) == "shop-infra"

    def test_active_clearance_class_none_when_consumed(self, tmp_path):
        db_path = str(tmp_path / "lifecycle.db")
        lifecycle.init_lifecycle_db(db_path)
        lifecycle.write_clearance("plan.md", "hash1", "shop-infra", "depositor", db_path)
        lifecycle.consume_clearance("hash1", "plan.md", db_path)
        assert lifecycle.active_clearance_class("hash1", "plan.md", db_path) is None

    def test_active_clearance_class_none_when_absent(self, tmp_path):
        db_path = str(tmp_path / "lifecycle.db")
        lifecycle.init_lifecycle_db(db_path)
        assert lifecycle.active_clearance_class("nope", "nope.md", db_path) is None

    def test_deposit_placeholder_roundtrip(self, tmp_path):
        db_path = str(tmp_path / "lifecycle.db")
        lifecycle.init_lifecycle_db(db_path)
        plan_id = lifecycle.mint_and_claim("executable", "/tmp", "test", "", "", 1,
                                           "my-plan.md", db_path)
        assert lifecycle.deposit_placeholder(plan_id, db_path) == "my-plan.md"

    def test_deposit_placeholder_none(self, tmp_path):
        db_path = str(tmp_path / "lifecycle.db")
        lifecycle.init_lifecycle_db(db_path)
        assert lifecycle.deposit_placeholder(99999, db_path) is None
