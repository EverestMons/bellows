# tests/conftest.py
import hashlib
import os
from pathlib import Path

import pytest


def clear_plan_for_test(path, db_path=None):
    import lifecycle
    raw_bytes = Path(path).read_bytes()
    content_hash = hashlib.sha256(raw_bytes).hexdigest()
    basename = os.path.basename(path)
    lifecycle.write_clearance(basename, content_hash, "governed-tooling", "depositor", db_path)


@pytest.fixture(autouse=True)
def isolate_verdicts_dir(monkeypatch, tmp_path):
    """Redirect verdict.VERDICTS_DIR to tmpdir so tests never write to production verdicts/pending/."""
    import verdict
    monkeypatch.setattr(verdict, "VERDICTS_DIR", tmp_path / "verdicts")


@pytest.fixture(autouse=True)
def isolate_runner_logs_dir(monkeypatch, tmp_path):
    import runner
    monkeypatch.setattr(runner, "LOGS_DIR", tmp_path / "logs")


@pytest.fixture(autouse=True)
def isolate_lifecycle_db(monkeypatch, tmp_path):
    """Redirect lifecycle.LIFECYCLE_DB_PATH to tmpdir so tests never touch production lifecycle.db."""
    import lifecycle
    db_path = str(tmp_path / "lifecycle.db")
    monkeypatch.setattr(lifecycle, "LIFECYCLE_DB_PATH", db_path)
    lifecycle.init_lifecycle_db(db_path)


@pytest.fixture(autouse=True)
def _clear_notifier_dedupe():
    # Added by plan 100054; declared here by plan 100055.
    import notifier
    notifier._dedupe_memo.clear()
    yield
    notifier._dedupe_memo.clear()


@pytest.fixture(autouse=True)
def isolate_watcher_spawn(monkeypatch):
    import tools.deposit_receipt as _dr

    def _stub_spawn_watcher(claimable_name):
        _dr._SPAWN_CALLS.append(claimable_name)
        return -1

    monkeypatch.setattr(_dr, "_SPAWN_CALLS", [], raising=False)
    monkeypatch.setattr(_dr, "_spawn_watcher", _stub_spawn_watcher)
    yield
