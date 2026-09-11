"""Tests for tools/check_deposit.py — DEV-side pre-check (plan 100060, thread 253).

Tests 1–10 are failing-first: all red before the tool is written (ModuleNotFoundError),
all green after. Tests are driven in-process via check_deposit.main(argv).
"""
import os
import subprocess
import sys

import pytest
from pathlib import Path

_BELLOWS_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_BELLOWS_ROOT))
sys.path.insert(0, str(_BELLOWS_ROOT / "tools"))
import gates
import check_deposit  # ModuleNotFoundError until tools/check_deposit.py is written


# ─── helpers ────────────────────────────────────────────────────────────────


def _make_plan(step_body: str, step: int = 1) -> str:
    return (
        "# bellows — test plan\n\n"
        "**Date:** 2026-09-09 | **Project:** bellows | **Execution:** Step 1 (DEV)\n\n"
        f"## STEP {step} — DEV\n\n"
        f"{step_body}\n"
    )


def _write_plan(tmp_path: Path, step_body: str, step: int = 1) -> Path:
    p = tmp_path / "plan.md"
    p.write_text(_make_plan(step_body, step))
    return p


def _run(plan_path: Path, step: int, wt: Path, capsys, extra: tuple = ()) -> tuple[int, str]:
    argv = [str(plan_path), str(step), "--wt", str(wt)] + list(extra)
    rc = check_deposit.main(argv)
    return rc, capsys.readouterr().out


def _git_init(d: Path) -> None:
    subprocess.run(["git", "init", "--initial-branch=main", str(d)], check=True,
                   capture_output=True)
    subprocess.run(["git", "-C", str(d), "config", "user.email", "t@t.com"],
                   check=True, capture_output=True)
    subprocess.run(["git", "-C", str(d), "config", "user.name", "T"], check=True,
                   capture_output=True)


def _git_commit(d: Path, msg: str = "init") -> None:
    subprocess.run(["git", "-C", str(d), "add", "-A"], check=True, capture_output=True)
    subprocess.run(["git", "-C", str(d), "commit", "-m", msg], check=True,
                   capture_output=True)


# ─── tests ──────────────────────────────────────────────────────────────────


class TestT1DevLogMissingHeading:
    """(t1) dev-log missing ## B → FAIL dev_log_declared_text, exit 1."""

    def test_t1(self, tmp_path, capsys):
        wt = tmp_path / "wt"
        (wt / "knowledge" / "development").mkdir(parents=True)
        (wt / "knowledge" / "development" / "dev-log.md").write_text("## A\n\nSome content.\n")

        plan = _write_plan(
            tmp_path,
            "> **Headings:** `## A`; `## B`\n\n"
            "> **Deposits:**\n"
            "> - `knowledge/development/dev-log.md`\n",
        )
        rc, out = _run(plan, 1, wt, capsys)

        assert rc == 1
        assert "FAIL dev_log_declared_text" in out
        assert "PRECHECK: 1 failure(s)" in out


class TestT2DevLogAllHeadingsPresent:
    """(t2) dev-log has both headings → exit 0, PRECHECK: 0 failure(s)."""

    def test_t2(self, tmp_path, capsys):
        wt = tmp_path / "wt"
        (wt / "knowledge" / "development").mkdir(parents=True)
        (wt / "knowledge" / "development" / "dev-log.md").write_text(
            "## A\n\nContent.\n\n## B\n\nMore.\n"
        )

        plan = _write_plan(
            tmp_path,
            "> **Headings:** `## A`; `## B`\n\n"
            "> **Deposits:**\n"
            "> - `knowledge/development/dev-log.md`\n",
        )
        rc, out = _run(plan, 1, wt, capsys)

        assert rc == 0
        assert "PRECHECK: 0 failure(s)" in out


class TestT3MissingDepositFile:
    """(t3) deposit path absent from worktree → FAIL rule_22_verification."""

    def test_t3(self, tmp_path, capsys):
        wt = tmp_path / "wt"
        wt.mkdir()

        plan = _write_plan(
            tmp_path,
            "> **Deposits:**\n"
            "> - `nonexistent/path/file.md`\n",
        )
        rc, out = _run(plan, 1, wt, capsys)

        assert rc == 1
        assert "FAIL rule_22_verification" in out


class TestT4QuotedNodeMissing:
    """(t4) deposit quotes tests/test_x.py::test_gone which is absent → FAIL quoted_test_nodes_exist."""

    def test_t4(self, tmp_path, capsys):
        wt = tmp_path / "wt"
        (wt / "knowledge" / "development").mkdir(parents=True)
        (wt / "tests").mkdir(parents=True)
        # Deposit exists; references a node that is NOT in the test file
        (wt / "knowledge" / "development" / "dev-log.md").write_text(
            "## Notes\n\nSee `tests/test_x.py::test_gone` for details.\n"
        )
        (wt / "tests" / "test_x.py").write_text("def test_other(): pass\n")

        plan = _write_plan(
            tmp_path,
            "> **Deposits:**\n"
            "> - `knowledge/development/dev-log.md`\n",
        )
        rc, out = _run(plan, 1, wt, capsys)

        assert rc == 1
        assert "FAIL quoted_test_nodes_exist" in out


class TestT5MutationSurvivor:
    """(t5) run file reports 1 survived → FAIL mutation_result."""

    def test_t5(self, tmp_path, capsys):
        wt = tmp_path / "wt"
        (wt / "knowledge" / "mutants").mkdir(parents=True)
        (wt / "knowledge" / "mutants" / "check.run.txt").write_text(
            "some output\nMUTATION: 3 killed, 1 survived, 0 error\n"
        )

        plan = _write_plan(
            tmp_path,
            "> **Deposits:**\n"
            "> - `knowledge/mutants/check.run.txt`\n",
        )
        rc, out = _run(plan, 1, wt, capsys)

        assert rc == 1
        assert "FAIL mutation_result" in out


class TestT6GatesIdentity:
    """(t6) GATES is exactly the five gate function objects in order."""

    def test_t6(self):
        assert check_deposit.GATES == (
            gates._gate_rule_22_verification,
            gates._gate_quoted_test_nodes_exist,
            gates._gate_mutation_result,
            gates._gate_qa_nodes_match_suite,
            gates._gate_dev_log_declared_text,
        )


class TestT7ParsedSynthesisRoundTrip:
    """(t7) synthesised parsed["result_text"] round-trips through _extract_agent_declared_deposits."""

    def test_t7(self):
        deposits = ["a.md", "b.txt"]
        parsed = check_deposit._make_parsed(deposits)
        assert gates._extract_agent_declared_deposits(parsed) == ["a.md", "b.txt"]


class TestT8DependentsWarn:
    """(t8) working-tree edit to helper → WARN dependents: helper → use.py, exit 0."""

    def test_t8(self, tmp_path, capsys):
        wt = tmp_path / "wt"
        _git_init(wt)
        (wt / "mod.py").write_text("def helper():\n    pass\n")
        (wt / "use.py").write_text("from mod import helper\nhelper()\n")
        _git_commit(wt)

        # Working-tree edit to helper (uncommitted)
        (wt / "mod.py").write_text("def helper():\n    return 42\n")

        plan = _write_plan(tmp_path, "> Do something.\n")
        rc, out = _run(plan, 1, wt, capsys, extra=("--dependents",))

        assert rc == 0
        assert "WARN dependents: helper → use.py" in out


class TestT9GenericCapOver25:
    """(t9) name referenced from >25 files → (generic, N files) form."""

    def test_t9(self, tmp_path, monkeypatch, capsys):
        wt = tmp_path / "wt"
        _git_init(wt)
        (wt / "mod.py").write_text("def big_func():\n    pass\n")
        _git_commit(wt)

        # Working-tree edit so big_func appears in diff
        (wt / "mod.py").write_text("def big_func():\n    return 1\n")

        many_files = [f"file_{i}.py" for i in range(26)]
        monkeypatch.setattr(
            check_deposit,
            "find_referencing_files",
            lambda names, wt_path: {"big_func": many_files},
        )

        plan = _write_plan(tmp_path, "> Do something.\n")
        rc, out = _run(plan, 1, wt, capsys, extra=("--dependents",))

        assert rc == 0
        assert "WARN dependents: big_func → (generic, 26 files)" in out


class TestT10FindReferencingFilesSwappable:
    """(t10) find_referencing_files is module-level callable; monkeypatching changes WARN lines only."""

    def test_t10(self, tmp_path, monkeypatch, capsys):
        wt = tmp_path / "wt"
        _git_init(wt)
        (wt / "mod.py").write_text("def alpha():\n    pass\n")
        _git_commit(wt)
        # Working-tree edit
        (wt / "mod.py").write_text("def alpha():\n    return 0\n")

        monkeypatch.setattr(
            check_deposit,
            "find_referencing_files",
            lambda names, wt_path: {"alpha": ["consumer.py"]},
        )

        plan = _write_plan(tmp_path, "> Do something.\n")
        rc, out = _run(plan, 1, wt, capsys, extra=("--dependents",))

        # Exit code unaffected by WARN
        assert rc == 0
        # WARN line changed by the mock
        assert "WARN dependents: alpha → consumer.py" in out
        # No FAIL lines (gates all pass on the empty-deposit plan)
        assert "FAIL" not in out


# ─── --expect-missing tests (t11–t14) ───────────────────────────────────────

_EM_DEV_LOG = "knowledge/development/dev-log-foo-2026-09-10.md"
_EM_RUN_FILE = "knowledge/mutants/foo.run.txt"
_EM_MANIFEST = "knowledge/mutants/foo.json"
_EM_SRC = "tools/src.py"

_EM_STEP_BODY = (
    "> **Headings:** `## A`\n\n"
    "> **Scope:**\n"
    f"> - `{_EM_SRC}`\n"
    f"> - `{_EM_MANIFEST}`\n\n"
    "> **Deposits:**\n"
    f"> - `{_EM_SRC}`\n"
    f"> - `{_EM_DEV_LOG}`\n"
    f"> - `{_EM_MANIFEST}`\n"
    f"> - `{_EM_RUN_FILE}`\n"
)


def _setup_em_wt(wt: Path) -> None:
    """Worktree with source file and manifest present; dev-log and run file absent."""
    (wt / "tools").mkdir(parents=True)
    (wt / "tools" / "src.py").write_text("# source\n")
    (wt / "knowledge" / "mutants").mkdir(parents=True)
    (wt / "knowledge" / "mutants" / "foo.json").write_text(
        '{"target": "tools/src.py", "mutants": []}\n'
    )


class TestT11ExpectMissingFirstCommit:
    """(t11) first-commit shape: dev-log and run file expected missing → rc 0, N/A lines, no FAIL."""

    def test_t11(self, tmp_path, capsys):
        wt = tmp_path / "wt"
        _setup_em_wt(wt)
        plan = _write_plan(tmp_path, _EM_STEP_BODY)
        rc, out = _run(plan, 1, wt, capsys, extra=("--expect-missing", _EM_DEV_LOG, _EM_RUN_FILE))

        assert rc == 0
        assert "PRECHECK: 0 failure(s)" in out
        assert "(expecting 2 missing)" in out
        assert "mutation_result N/A" in out
        assert "dev_log_declared_text N/A" in out
        assert "FAIL" not in out


class TestT12ExpectMissingGuard:
    """(t12) present-path guard: dev-log exists in worktree → FAIL expect_missing, rc 1."""

    def test_t12(self, tmp_path, capsys):
        wt = tmp_path / "wt"
        _setup_em_wt(wt)
        # Write the dev-log — it now EXISTS
        (wt / "knowledge" / "development").mkdir(parents=True)
        (wt / "knowledge" / "development" / "dev-log-foo-2026-09-10.md").write_text(
            "## A\n\nContent.\n"
        )
        plan = _write_plan(tmp_path, _EM_STEP_BODY)
        rc, out = _run(plan, 1, wt, capsys, extra=("--expect-missing", _EM_DEV_LOG, _EM_RUN_FILE))

        assert rc == 1
        assert f"FAIL expect_missing: {_EM_DEV_LOG} is present" in out


class TestT13ExpectMissingControl:
    """(t13) control (flagless): t11 tree without --expect-missing → the two rule_22 FAILs."""

    def test_t13(self, tmp_path, capsys):
        wt = tmp_path / "wt"
        _setup_em_wt(wt)
        plan = _write_plan(tmp_path, _EM_STEP_BODY)
        rc, out = _run(plan, 1, wt, capsys)  # no --expect-missing

        assert rc == 1
        assert f"FAIL rule_22_verification: (a) Plan-declared deposit missing: {_EM_DEV_LOG}" in out
        assert f"FAIL rule_22_verification: (a) Plan-declared deposit missing: {_EM_RUN_FILE}" in out


class TestT14ExpectMissingUndeclared:
    """(t14) undeclared path in --expect-missing → FAIL expect_missing, rc 1."""

    def test_t14(self, tmp_path, capsys):
        wt = tmp_path / "wt"
        wt.mkdir()
        plan = _write_plan(tmp_path, "> Do something.\n")
        rc, out = _run(plan, 1, wt, capsys, extra=("--expect-missing", "knowledge/x.md"))

        assert rc == 1
        assert "FAIL expect_missing: knowledge/x.md is not a Deposit of step 1" in out
