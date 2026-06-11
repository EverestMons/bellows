# tests/conftest.py
import pytest


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
