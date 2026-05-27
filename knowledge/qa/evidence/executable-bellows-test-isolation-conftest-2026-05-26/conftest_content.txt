# tests/conftest.py
import pytest


@pytest.fixture(autouse=True)
def isolate_verdicts_dir(monkeypatch, tmp_path):
    """Redirect verdict.VERDICTS_DIR to tmpdir so tests never write to production verdicts/pending/."""
    import verdict
    monkeypatch.setattr(verdict, "VERDICTS_DIR", tmp_path / "verdicts")
