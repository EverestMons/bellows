"""Tests for notifier.py and server.py."""

import time
from unittest.mock import MagicMock, patch

import requests

import notifier
from server import ResponseServer


def test_push_success():
    mock_response = MagicMock()
    mock_response.status_code = 200
    with patch("requests.post", return_value=mock_response):
        result = notifier.push("app", "user", "title", "msg")
    assert result is True


def test_push_passes_timeout():
    """requests.post must be called with timeout=(5, 10)."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    with patch("requests.post", return_value=mock_response) as mock_post:
        notifier.push("app", "user", "title", "msg")
    _, kwargs = mock_post.call_args
    assert kwargs.get("timeout") == (5, 10)


def test_push_timeout_exception_handled_gracefully():
    """A requests.Timeout must return False without raising."""
    with patch("requests.post", side_effect=requests.Timeout):
        result = notifier.push("app", "user", "title", "msg")
    assert result is False


def test_no_stranded_check_in_run_plan():
    """Dead code block (stranded-check call site in run_plan) must be absent."""
    import pathlib
    bellows_src = (pathlib.Path(__file__).parent.parent / "bellows.py").read_text()
    # The removed block was the only place that pushed "Bellows — STRANDED Plan"
    assert "STRANDED Plan" not in bellows_src


def test_push_failure():
    mock_response = MagicMock()
    mock_response.status_code = 400
    with patch("requests.post", return_value=mock_response):
        result = notifier.push("app", "user", "title", "msg")
    assert result is False


def test_server_respond():
    s = ResponseServer(port=15432)
    s.start()
    time.sleep(0.5)  # give Flask a moment to bind
    requests.post("http://localhost:15432/respond", json={"decision": "continue"})
    result = s.wait_for_response(timeout=3)
    assert result is not None
    assert result["decision"] == "continue"
