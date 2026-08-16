import fcntl
import os
import signal
import sys
import threading
import time
from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from bellows import LockAcquireError, acquire_instance_lock, _DRAIN_TIMEOUT


# ---------------------------------------------------------------------------
# Task A — self-diagnosing lock
# ---------------------------------------------------------------------------

def test_acquire_writes_pid_and_timestamp(tmp_path):
    lock_path = str(tmp_path / ".bellows.lock")
    lock_file = acquire_instance_lock(lock_path)
    try:
        with open(lock_path) as f:
            content = f.read().strip()
        parts = content.split(None, 1)
        assert len(parts) == 2, f"expected 'PID TIMESTAMP', got: {content!r}"
        assert parts[0] == str(os.getpid())
        datetime.fromisoformat(parts[1])
    finally:
        lock_file.close()


def test_failure_includes_holder_pid(tmp_path):
    lock_path = str(tmp_path / ".bellows.lock")
    holder = acquire_instance_lock(lock_path)
    try:
        with pytest.raises(LockAcquireError, match=str(os.getpid())):
            acquire_instance_lock(lock_path)
    finally:
        holder.close()


def test_failure_falls_back_on_empty_file(tmp_path):
    lock_path = str(tmp_path / ".bellows.lock")
    fd = os.open(lock_path, os.O_RDWR | os.O_CREAT, 0o644)
    lock_file = os.fdopen(fd, "r+")
    fcntl.flock(lock_file, fcntl.LOCK_EX | fcntl.LOCK_NB)
    try:
        with pytest.raises(LockAcquireError, match="another Bellows instance holds"):
            acquire_instance_lock(lock_path)
    finally:
        lock_file.close()


def test_second_open_preserves_holder_pid(tmp_path):
    """The acquire path's open mode must NOT truncate the holder's PID.
    This test MUST fail if the open mode is changed back to 'w'."""
    lock_path = str(tmp_path / ".bellows.lock")
    holder = acquire_instance_lock(lock_path)
    try:
        with open(lock_path) as f:
            holder_content = f.read().strip()
        holder_pid = holder_content.split()[0]
        assert holder_pid == str(os.getpid())

        fd2 = os.open(lock_path, os.O_RDWR | os.O_CREAT, 0o644)
        with os.fdopen(fd2, "r+") as f2:
            f2.seek(0)
            assert f2.read().strip() == holder_content
    finally:
        holder.close()


# ---------------------------------------------------------------------------
# Task B — SIGTERM drain handler
# ---------------------------------------------------------------------------

def test_shutting_down_refuses_dispatch():
    import bellows
    config = {
        "watched_projects": [],
        "callback_port": 0,
        "pushover": {},
    }
    with patch.object(bellows.server, "ResponseServer") as mock_rs:
        mock_rs.return_value = MagicMock()
        b = bellows.Bellows(config)
    assert not b._shutting_down
    b._shutting_down = True
    with patch.object(bellows, "run_plan"):
        b.handle_new_plan("/fake/path/executable-999.md")
    assert b._active_count == 0


def test_drain_waits_for_active_count_zero():
    import bellows
    config = {
        "watched_projects": [],
        "callback_port": 0,
        "pushover": {},
    }
    with patch.object(bellows.server, "ResponseServer") as mock_rs:
        mock_rs.return_value = MagicMock()
        b = bellows.Bellows(config)

    b._shutting_down = True
    with b._active_lock:
        b._active_count = 2

    drained = threading.Event()

    def drain_thread():
        deadline = time.time() + 5
        while time.time() < deadline:
            with b._active_lock:
                if b._active_count == 0:
                    drained.set()
                    return
            time.sleep(0.1)

    t = threading.Thread(target=drain_thread, daemon=True)
    t.start()
    time.sleep(0.3)
    assert not drained.is_set()

    with b._active_lock:
        b._active_count = 0
    assert drained.wait(timeout=2)
