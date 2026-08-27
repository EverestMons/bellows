"""Tests for tools/mutation_check.py — the mutation runner's own tests."""
import hashlib
import json
import os
import subprocess
import sys
import textwrap
from pathlib import Path

RUNNER = Path(__file__).resolve().parent.parent / "tools" / "mutation_check.py"


def _sha256_path(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def _make_repo(tmp_path, files):
    repo = tmp_path / "repo"
    repo.mkdir()
    for rel, content in files.items():
        p = repo / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content)
    subprocess.run(["git", "init", "-b", "main"], cwd=repo,
                   capture_output=True, check=True)
    subprocess.run(["git", "add", "."], cwd=repo,
                   capture_output=True, check=True)
    subprocess.run(
        ["git", "-c", "user.name=test", "-c", "user.email=t@t",
         "commit", "-m", "init"],
        cwd=repo, capture_output=True, check=True,
    )
    return repo


def _run_checker(tmp_path, repo, manifest, extra_args=None):
    mp = tmp_path / "manifest.json"
    mp.write_text(json.dumps(manifest))
    cmd = [sys.executable, str(RUNNER), str(mp), "--repo-root", str(repo)]
    if extra_args:
        cmd.extend(extra_args)
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    return r.returncode, r.stdout


def test_killed_when_mutant_breaks_the_test(tmp_path):
    repo = _make_repo(tmp_path, {
        "target.py": "def add(a, b):\n    return a + b\n",
        "tests/test_target.py": textwrap.dedent("""\
            import sys, os
            sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
            from target import add
            def test_add():
                assert add(1, 2) == 3
        """),
    })
    manifest = {
        "target": "target.py",
        "mutants": [{
            "name": "flip-add",
            "why": "test",
            "anchor": "return a + b",
            "replacement": "return a - b",
            "expect_fail": "tests/test_target.py::test_add",
        }],
    }
    code, out = _run_checker(tmp_path, repo, manifest)
    assert "MUTANT flip-add: KILLED" in out
    assert code == 0


def test_survived_when_suite_cannot_see_the_change(tmp_path):
    repo = _make_repo(tmp_path, {
        "target.py": 'def add(a, b):\n    return a + b\n\nUNUSED = "hello"\n',
        "tests/test_target.py": textwrap.dedent("""\
            import sys, os
            sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
            from target import add
            def test_add():
                assert add(1, 2) == 3
        """),
    })
    manifest = {
        "target": "target.py",
        "mutants": [{
            "name": "invisible-change",
            "why": "test",
            "anchor": 'UNUSED = "hello"',
            "replacement": 'UNUSED = "world"',
            "expect_fail": "tests/test_target.py::test_add",
        }],
    }
    code, out = _run_checker(tmp_path, repo, manifest)
    assert "MUTANT invisible-change: SURVIVED" in out
    assert code == 1


def test_empty_selector_is_error_not_killed(tmp_path):
    repo = _make_repo(tmp_path, {
        "target.py": "VALUE = 42\n",
        "tests/test_target.py": textwrap.dedent("""\
            def test_real():
                assert True
        """),
    })
    manifest = {
        "target": "target.py",
        "mutants": [{
            "name": "bad-selector",
            "why": "test",
            "anchor": "VALUE = 42",
            "replacement": "VALUE = 0",
            "expect_fail": "tests/test_target.py::test_nonexistent",
        }],
    }
    code, out = _run_checker(tmp_path, repo, manifest)
    assert "KILLED" not in out
    assert "MUTANT bad-selector: ERROR" in out
    assert code != 0


def test_baseline_failure_is_error_not_killed(tmp_path):
    repo = _make_repo(tmp_path, {
        "target.py": "VALUE = 42\n",
        "tests/test_target.py": textwrap.dedent("""\
            import sys, os
            sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
            from target import VALUE
            def test_wrong():
                assert VALUE == 999
        """),
    })
    manifest = {
        "target": "target.py",
        "mutants": [{
            "name": "already-red",
            "why": "test",
            "anchor": "VALUE = 42",
            "replacement": "VALUE = 999",
            "expect_fail": "tests/test_target.py::test_wrong",
        }],
    }
    code, out = _run_checker(tmp_path, repo, manifest)
    assert "KILLED" not in out
    assert "MUTANT already-red: ERROR" in out
    assert "baseline not green" in out
    assert code != 0


def test_anchor_not_unique_is_error(tmp_path):
    repo = _make_repo(tmp_path, {
        "target.py": "A = 1\nB = 2\nA = 1\n",
        "tests/test_target.py": "def test_x():\n    assert True\n",
    })
    manifest = {
        "target": "target.py",
        "mutants": [
            {
                "name": "zero-match",
                "why": "test",
                "anchor": "DOES_NOT_EXIST",
                "replacement": "X",
                "expect_fail": "tests/test_target.py::test_x",
            },
            {
                "name": "two-match",
                "why": "test",
                "anchor": "A = 1",
                "replacement": "A = 99",
                "expect_fail": "tests/test_target.py::test_x",
            },
        ],
    }
    code, out = _run_checker(tmp_path, repo, manifest)
    assert "MUTANT zero-match: ERROR — anchor matched 0 times" in out
    assert "MUTANT two-match: ERROR — anchor matched 2 times" in out
    assert "KILLED" not in out
    assert code == 2


def test_live_tree_untouched(tmp_path):
    repo = _make_repo(tmp_path, {
        "target.py": "def add(a, b):\n    return a + b\n",
        "tests/test_target.py": textwrap.dedent("""\
            import sys, os
            sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
            from target import add
            def test_add():
                assert add(1, 2) == 3
        """),
    })
    live_target = repo / "target.py"
    sha_before = _sha256_path(live_target)

    manifest = {
        "target": "target.py",
        "mutants": [{
            "name": "flip-add",
            "why": "test",
            "anchor": "return a + b",
            "replacement": "return a - b",
            "expect_fail": "tests/test_target.py::test_add",
        }],
    }
    code, out = _run_checker(tmp_path, repo, manifest)

    sha_after = _sha256_path(live_target)
    assert sha_before == sha_after
    assert "LIVE-TREE UNCHANGED:" in out


def test_mutants_do_not_compound(tmp_path):
    repo = _make_repo(tmp_path, {
        "target.py": "A = 10\nB = 20\n\ndef total():\n    return A + B\n",
        "tests/test_target.py": textwrap.dedent("""\
            import sys, os
            sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
            from target import total
            def test_total():
                assert total() == 30
        """),
    })
    manifest = {
        "target": "target.py",
        "mutants": [
            {
                "name": "zero-A",
                "why": "test",
                "anchor": "A = 10",
                "replacement": "A = 0",
                "expect_fail": "tests/test_target.py::test_total",
            },
            {
                "name": "zero-B",
                "why": "test",
                "anchor": "B = 20",
                "replacement": "B = 0",
                "expect_fail": "tests/test_target.py::test_total",
            },
        ],
    }
    code, out = _run_checker(tmp_path, repo, manifest)
    assert "MUTANT zero-A: KILLED" in out
    assert "MUTANT zero-B: KILLED" in out
    assert code == 0


def test_timeout_is_error_not_killed(tmp_path):
    repo = _make_repo(tmp_path, {
        "target.py": (
            "import time\nDELAY = 0\n\n"
            "def compute():\n    time.sleep(DELAY)\n    return 42\n"
        ),
        "tests/test_target.py": textwrap.dedent("""\
            import sys, os
            sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
            from target import compute
            def test_compute():
                assert compute() == 42
        """),
    })
    manifest = {
        "target": "target.py",
        "mutants": [{
            "name": "slow-mutant",
            "why": "test",
            "anchor": "DELAY = 0",
            "replacement": "DELAY = 10",
            "expect_fail": "tests/test_target.py::test_compute",
        }],
    }
    code, out = _run_checker(tmp_path, repo, manifest, extra_args=["--timeout", "1"])
    assert "KILLED" not in out
    assert "MUTANT slow-mutant: ERROR" in out
    assert "timeout" in out.lower()
    assert code != 0


def test_same_byte_length_mutation_is_killed(tmp_path):
    repo = _make_repo(tmp_path, {
        "target.py": "def add(a, b):\n    return a + b\n",
        "tests/test_target.py": textwrap.dedent("""\
            import sys, os
            sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
            from target import add
            def test_add():
                assert add(1, 2) == 3
        """),
    })
    anchor = "return a + b"
    replacement = "return a - b"
    assert len(anchor) == len(replacement), "test precondition: same byte length"
    manifest = {
        "target": "target.py",
        "mutants": [{
            "name": "same-len-flip",
            "why": "regression: same-byte-length mutant must not survive via stale bytecache",
            "anchor": anchor,
            "replacement": replacement,
            "expect_fail": "tests/test_target.py::test_add",
        }],
    }
    code, out = _run_checker(tmp_path, repo, manifest)
    assert "MUTANT same-len-flip: KILLED" in out
    assert code == 0


def test_bytecode_isolation_env_is_set():
    source = Path(os.path.join(
        os.path.dirname(__file__), "..", "tools", "mutation_check.py"
    )).resolve().read_text()
    assert "PYTHONDONTWRITEBYTECODE" in source
    lines = source.splitlines()
    in_run_pytest = False
    found_env_arg = False
    for line in lines:
        if "def _run_pytest" in line:
            in_run_pytest = True
        elif in_run_pytest and line and not line[0].isspace():
            break
        if in_run_pytest and "env=" in line:
            found_env_arg = True
    assert found_env_arg, "_run_pytest must pass env= to subprocess.run"


def test_consecutive_same_length_mutants_are_both_killed(tmp_path):
    repo = _make_repo(tmp_path, {
        "target.py": textwrap.dedent("""\
            def add(a, b):
                return a + b

            def mul(a, b):
                return a * b
        """),
        "tests/test_target.py": textwrap.dedent("""\
            import sys, os
            sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
            from target import add, mul
            def test_add():
                assert add(1, 2) == 3
            def test_mul():
                assert mul(3, 4) == 12
        """),
    })
    anchor1 = "return a + b"
    replace1 = "return a - b"
    anchor2 = "return a * b"
    replace2 = "return a / b"
    assert len(anchor1) == len(replace1), "test precondition: same byte length (mutant 1)"
    assert len(anchor2) == len(replace2), "test precondition: same byte length (mutant 2)"
    manifest = {
        "target": "target.py",
        "mutants": [
            {
                "name": "flip-add",
                "why": "consecutive same-length regression (1 of 2)",
                "anchor": anchor1,
                "replacement": replace1,
                "expect_fail": "tests/test_target.py::test_add",
            },
            {
                "name": "flip-mul",
                "why": "consecutive same-length regression (2 of 2)",
                "anchor": anchor2,
                "replacement": replace2,
                "expect_fail": "tests/test_target.py::test_mul",
            },
        ],
    }
    code, out = _run_checker(tmp_path, repo, manifest)
    assert "MUTANT flip-add: KILLED" in out
    assert "MUTANT flip-mul: KILLED" in out
    assert code == 0
