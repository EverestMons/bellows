"""Tests for lens_commit — commits one lens in the correct order.

All fixtures are constructed under tmp_path inside a git init repo.
run_checker is the seam for checker subprocess calls.
"""

import re
import subprocess
import sys
from pathlib import Path

import pytest

BELLOWS_ROOT = Path(__file__).parent.parent.resolve()
SCRIPTS = BELLOWS_ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

import lens_commit  # noqa: E402 — fails until scripts/lens_commit.py exists

# ---- fixture helpers ----

_DC_BLOCK = (
    "**Tier:** T1\n"
    "**Walk register:** `register.md`\n"
    "- Weak spots: w1 dry.\n"
    "- Destruction: w1 dry.\n"
    "- Vulnerabilities: w1 dry.\n"
    "- Integration-record: w1 dry.\n"
    "- ACID: w1 dry.\n"
)

_MANIFEST_BLOCK = (
    "\n## Cycle Manifest\n"
    "tier: T1\n"
    "target: scripts/lens_commit.py\n"
    "class: shop-infra\n"
    "reads: test\n"
    "writes: test\n"
    "open_forks: none\n"
    "walks: <declare>\n"
    "yields: <declare>\n"
    "validation: <declare>\n"
    "coherence: <declare>\n"
    "fold_baseline: .plan.md.foldcheck.json\n"
)

_INITIAL_PLAN = (
    "# Plan\n"
    "**dispatch_mode:** bellows\n"
    "\n"
    "## Drafting Cycle\n"
    + _DC_BLOCK
    + _MANIFEST_BLOCK
)

_REGISTER = (
    "# Walk Register — test\n\n"
    "**schema_version:** `0.3`\n\n"
    "| id | walk | lens | sub_question | origin | finding | pre_fold_text | resolution |\n"
    "|---|---|---|---|---|---|---|---|\n"
)


def _git(repo, *args):
    return subprocess.run(["git", "-C", str(repo), *args],
                          capture_output=True, text=True)


def _make_lens_fixture(tmp_path):
    """Set up a minimal git repo for lens_commit tests (no prior lens commits)."""
    for cmd in [
        ["git", "-C", str(tmp_path), "init"],
        ["git", "-C", str(tmp_path), "config", "user.name", "Test"],
        ["git", "-C", str(tmp_path), "config", "user.email", "test@test.com"],
    ]:
        subprocess.run(cmd, capture_output=True)

    plan = tmp_path / "plan.md"
    plan.write_text(_INITIAL_PLAN, encoding="utf-8")
    register = tmp_path / "register.md"
    register.write_text(_REGISTER, encoding="utf-8")

    _git(tmp_path, "add", ".")
    _git(tmp_path, "commit", "-m", "initial")

    return plan, register


# ---- l1: subject contains correct lens name from table ----


def test_l1_subject_lens_name(tmp_path):
    """--lens 3 produces subject 'draft(plan): walk 1 lens 3 — Vulnerabilities: <desc>'."""
    plan, register = _make_lens_fixture(tmp_path)

    rc = lens_commit.main([
        str(plan), "--register", str(register),
        "--walk", "1", "--lens", "3", "--desc", "test fixture", "--dry",
    ])
    assert rc == 0

    log = _git(tmp_path, "log", "--format=%s", "-1").stdout.strip()
    assert log == "draft(plan): walk 1 lens 3 — Vulnerabilities: test fixture", (
        f"unexpected subject: {log!r}"
    )


# ---- l2: wrong name in table detected via commit subject ----


def test_l2_assert_checks_name(tmp_path, monkeypatch):
    """When LENS_NAMES[3] is patched to a wrong name, the assert refuses before any commit."""
    plan, register = _make_lens_fixture(tmp_path)
    monkeypatch.setitem(lens_commit.LENS_NAMES, 3, "WrongName")

    rc = lens_commit.main([
        str(plan), "--register", str(register),
        "--walk", "1", "--lens", "3", "--desc", "test fixture",
    ])
    assert rc == 1, "script must refuse when table entry returns wrong name"

    # No lens commit must have been made
    log = _git(tmp_path, "log", "--format=%s").stdout
    assert "lens 3" not in log


# ---- l3: yield-rising handling ----


def test_l3_yield_rising(tmp_path, monkeypatch):
    """ESCALATE:yield-rising refuses without flag; with --allow-yield-rising --walk 4 appends WARN."""
    plan, register = _make_lens_fixture(tmp_path)

    _real = lens_commit.run_checker

    def fake_run_checker(script, *args):
        if script == "cycle_check.py" and "--emit-manifest" not in args:
            return 1, "ESCALATE:yield-rising\n"
        return _real(script, *args)

    monkeypatch.setattr(lens_commit, "run_checker", fake_run_checker)

    # Without flag: refuses
    rc = lens_commit.main([
        str(plan), "--register", str(register),
        "--walk", "4", "--lens", "1", "--desc", "test", "--dry",
    ])
    assert rc == 1

    # With --allow-yield-rising: appends WARN and commits
    rc = lens_commit.main([
        str(plan), "--register", str(register),
        "--walk", "4", "--lens", "1", "--desc", "test",
        "--allow-yield-rising", "--dry",
    ])
    assert rc == 0
    reg_text = register.read_text(encoding="utf-8")
    assert "**WARN (walk 4):**" in reg_text


# ---- l4: --allow-yield-rising --walk 7 refuses ----


def test_l4_yield_rising_walk7_refused(tmp_path, monkeypatch):
    """--allow-yield-rising is refused when --walk >= 7 (CEO ruling)."""
    plan, register = _make_lens_fixture(tmp_path)

    _real = lens_commit.run_checker

    def fake_run_checker(script, *args):
        if script == "cycle_check.py" and "--emit-manifest" not in args:
            return 1, "ESCALATE:yield-rising\n"
        return _real(script, *args)

    monkeypatch.setattr(lens_commit, "run_checker", fake_run_checker)

    rc = lens_commit.main([
        str(plan), "--register", str(register),
        "--walk", "7", "--lens", "1", "--desc", "test",
        "--allow-yield-rising", "--dry",
    ])
    assert rc == 1


# ---- l5: register lint COVERAGE: INCOMPLETE refuses ----


def test_l5_incomplete_coverage_refuses(tmp_path, monkeypatch):
    """walk_register_lint COVERAGE: INCOMPLETE causes refusal."""
    plan, register = _make_lens_fixture(tmp_path)

    _real = lens_commit.run_checker

    def fake_run_checker(script, *args):
        if script == "walk_register_lint.py":
            return 0, f"{register.name}\tSHAPE-OK\tCOVERAGE: INCOMPLETE — w1 rows=0 declared=2\n"
        return _real(script, *args)

    monkeypatch.setattr(lens_commit, "run_checker", fake_run_checker)

    rc = lens_commit.main([
        str(plan), "--register", str(register),
        "--walk", "1", "--lens", "1", "--desc", "test",
    ])
    assert rc == 1


# ---- l6: --dry with a cycle-record-only change commits all three files ----


def test_l6_dry_lens_appends_row_and_commits_three_files(tmp_path, capsys):
    """--dry with a Cycle-Log-only change: DRY row appended, draft+register+baseline committed."""
    plan, register = _make_lens_fixture(tmp_path)
    text = plan.read_text(encoding="utf-8")
    plan.write_text(
        text.replace("- Destruction: w1 dry.", "- Destruction: w1 dry; w2 dry."),
        encoding="utf-8",
    )
    rc = lens_commit.main([
        str(plan), "--register", str(register),
        "--walk", "1", "--lens", "2", "--desc", "dry", "--dry",
    ])
    assert rc == 0
    reg_text = register.read_text(encoding="utf-8").rstrip()
    assert reg_text.endswith("**Walk 1 lens 2 — Destruction — DRY, basis:** dry")
    shown = _git(tmp_path, "show", "--name-only", "--format=", "HEAD").stdout.split()
    assert "plan.md" in shown
    assert "register.md" in shown
    assert ".plan.md.foldcheck.json" in shown


# ---- l7: fold without a register row refuses at step 0 ----


def test_l7_fold_without_row_refuses(tmp_path, capsys):
    """Non-dry commit with no register row refuses; no commit made."""
    plan, register = _make_lens_fixture(tmp_path)
    plan.write_text(plan.read_text(encoding="utf-8") + "\nextra fold line\n", encoding="utf-8")
    count_before = int(_git(tmp_path, "rev-list", "--count", "HEAD").stdout.strip())
    rc = lens_commit.main([
        str(plan), "--register", str(register),
        "--walk", "1", "--lens", "2", "--desc", "fold",
    ])
    assert rc == 1
    out = capsys.readouterr().out
    assert "LENS-COMMIT: record FAIL" in out
    count_after = int(_git(tmp_path, "rev-list", "--count", "HEAD").stdout.strip())
    assert count_after == count_before


# ---- l7b: --dry over a real fold refuses and quotes the offending line ----


def test_l7b_dry_over_fold_refuses(tmp_path, capsys):
    """--dry but draft changed beyond cycle record: refuses and quotes the offending line."""
    plan, register = _make_lens_fixture(tmp_path)
    plan.write_text(plan.read_text(encoding="utf-8") + "\nextra fold line\n", encoding="utf-8")
    rc = lens_commit.main([
        str(plan), "--register", str(register),
        "--walk", "1", "--lens", "2", "--desc", "fold", "--dry",
    ])
    assert rc == 1
    out = capsys.readouterr().out
    assert "record FAIL — --dry, but the draft changed beyond its cycle record:" in out
    assert "extra fold line" in out


# ---- l7c: plumbing flags make the diff readable regardless of git config ----


@pytest.mark.parametrize("config_key,config_val", [
    ("color.ui", "always"),
    ("diff.external", "/usr/bin/true"),
])
def test_l7c_env_plumbing_reads_diff(tmp_path, capsys, config_key, config_val):
    """color.ui=always or diff.external do not defeat the plumbing-flag diff read.
    The refusal is l7b's 'beyond its cycle record', never the vacuity message."""
    plan, register = _make_lens_fixture(tmp_path)
    _git(tmp_path, "config", config_key, config_val)
    plan.write_text(plan.read_text(encoding="utf-8") + "\nextra fold line\n", encoding="utf-8")
    rc = lens_commit.main([
        str(plan), "--register", str(register),
        "--walk", "1", "--lens", "2", "--desc", "fold", "--dry",
    ])
    assert rc == 1
    out = capsys.readouterr().out
    assert "record FAIL — --dry, but the draft changed beyond its cycle record:" in out
    assert "the draft changed but its diff could not be read" not in out


# ---- l6b: walk-closing shape (per-walk summary + walks: N) is admitted ----


def test_l6b_walk_closing_shape_admitted(tmp_path):
    """The walk-closing ACID dry lens shape passes the cycle-only guard."""
    plan, register = _make_lens_fixture(tmp_path)
    # First: commit walks: 0 as the walk-0 state (panel E2)
    text = plan.read_text(encoding="utf-8")
    plan.write_text(text.replace("walks: <declare>", "walks: 0"), encoding="utf-8")
    _git(tmp_path, "add", "plan.md")
    _git(tmp_path, "commit", "-m", "walk-0 state: walks: 0")
    # Walk-closing edit: Destruction line + per-walk summary + walks: 0 → 1
    text = plan.read_text(encoding="utf-8")
    text = text.replace("- Destruction: w1 dry.", "- Destruction: w1 dry; w2 dry.")
    text = text.replace("walks: 0", "walks: 1")
    text = text.replace(
        "- ACID: w1 dry.\n\n## Cycle Manifest\n",
        "- ACID: w1 dry.\n**Walk 1 — dry.**\n\n## Cycle Manifest\n",
    )
    plan.write_text(text, encoding="utf-8")
    rc = lens_commit.main([
        str(plan), "--register", str(register),
        "--walk", "1", "--lens", "5", "--desc", "walk-close", "--dry",
    ])
    assert rc == 0


# ---- l8: fold with a register row commits all three files ----


def test_l8_fold_with_row_commits_three_files(tmp_path):
    """A non-dry commit with a register row: draft + register + baseline in HEAD after commit."""
    plan, register = _make_lens_fixture(tmp_path)
    plan.write_text(plan.read_text(encoding="utf-8") + "\nextra fold line\n", encoding="utf-8")
    register.write_text(
        register.read_text(encoding="utf-8")
        + "| f1 | 1 | 2 | q | v0 | finding | text | folded |\n",
        encoding="utf-8",
    )
    rc = lens_commit.main([
        str(plan), "--register", str(register),
        "--walk", "1", "--lens", "2", "--desc", "fold",
    ])
    assert rc == 0
    shown = _git(tmp_path, "show", "--name-only", "--format=", "HEAD").stdout.split()
    assert "plan.md" in shown
    assert "register.md" in shown
    assert ".plan.md.foldcheck.json" in shown


# ---- l9: register not in HEAD — in-HEAD check refuses ----


def test_l9_register_not_committed_refuses(tmp_path, capsys):
    """Register git-added but never committed: in-HEAD check refuses."""
    for cmd in [
        ["git", "-C", str(tmp_path), "init"],
        ["git", "-C", str(tmp_path), "config", "user.name", "Test"],
        ["git", "-C", str(tmp_path), "config", "user.email", "test@test.com"],
    ]:
        subprocess.run(cmd, capture_output=True)
    plan = tmp_path / "plan.md"
    plan.write_text(_INITIAL_PLAN, encoding="utf-8")
    _git(tmp_path, "add", "plan.md")
    _git(tmp_path, "commit", "-m", "initial — plan only")
    register = tmp_path / "register.md"
    register.write_text(_REGISTER, encoding="utf-8")
    _git(tmp_path, "add", "register.md")   # staged, never committed
    rc = lens_commit.main([
        str(plan), "--register", str(register),
        "--walk", "1", "--lens", "2", "--desc", "test", "--dry",
    ])
    assert rc == 1
    out = capsys.readouterr().out
    assert "record FAIL" in out
    assert "is not committed" in out


# ---- l10: duplicate --dry run refused on second invocation ----


def test_l10_duplicate_dry_run_refuses(tmp_path, capsys):
    """Running --dry twice for the same walk/lens refuses on the second run."""
    plan, register = _make_lens_fixture(tmp_path)
    text = plan.read_text(encoding="utf-8")
    plan.write_text(
        text.replace("- Destruction: w1 dry.", "- Destruction: w1 dry; w2 dry."),
        encoding="utf-8",
    )
    rc1 = lens_commit.main([
        str(plan), "--register", str(register),
        "--walk", "1", "--lens", "2", "--desc", "dry", "--dry",
    ])
    assert rc1 == 0
    capsys.readouterr()
    rc2 = lens_commit.main([
        str(plan), "--register", str(register),
        "--walk", "1", "--lens", "2", "--desc", "dry", "--dry",
    ])
    assert rc2 == 1
    out = capsys.readouterr().out
    assert "record FAIL — walk 1 lens 2 is already on the record" in out
    reg_text = register.read_text(encoding="utf-8")
    assert reg_text.count("**Walk 1 lens 2 —") == 1


# ---- l11: mode-change-only diff → vacuity refusal ----


def test_l11_mode_change_vacuity_refuses(tmp_path, capsys):
    """chmod with core.filemode=true: diff shows changed but no content lines → vacuity fails."""
    plan, register = _make_lens_fixture(tmp_path)
    _git(tmp_path, "config", "core.filemode", "true")
    plan.chmod(0o755)
    rc = lens_commit.main([
        str(plan), "--register", str(register),
        "--walk", "1", "--lens", "2", "--desc", "test", "--dry",
    ])
    assert rc == 1
    out = capsys.readouterr().out
    assert "record FAIL — the draft changed but its diff could not be read" in out


# ---- l12: plan_lint WARN lines echoed; exit unchanged ----


def test_l12_plan_lint_warn_echo(tmp_path, capsys):
    """Unedited fixture with --dry: plan_lint WARN lines echoed; exit 0 and commit OK."""
    plan, register = _make_lens_fixture(tmp_path)
    rc = lens_commit.main([
        str(plan), "--register", str(register),
        "--walk", "1", "--lens", "1", "--desc", "echo-test", "--dry",
    ])
    out = capsys.readouterr().out
    warn_lines = [l for l in out.splitlines() if "plan_lint WARN — (f) WARN:" in l]
    assert warn_lines, f"Expected LENS-COMMIT: plan_lint WARN — (f) WARN: line, got:\n{out}"
    assert rc == 0, f"Expected exit 0, got {rc}:\n{out}"
    assert any("commit OK" in l for l in out.splitlines()), f"Expected commit OK, got:\n{out}"


# ---- l13: plan_lint FAIL echoed; step-3 gate refuses; no commit ----


def test_l13_plan_lint_fail_refuses(tmp_path, capsys):
    """QA section + no qa_steps: plan_lint FAIL echoed; the downgraded CONTINUE is accepted; one commit."""
    plan, register = _make_lens_fixture(tmp_path)
    log_before = _git(tmp_path, "log", "--oneline").stdout.strip().count("\n")
    banner = "Rule 20 — QA Self-Check Results\nPASSED — SELF-CHECK PASSED\n"
    plan.write_text(
        plan.read_text(encoding="utf-8") + f"\n## STEP 1 — QA\n\n> Do the work.\n\n{banner}",
        encoding="utf-8",
    )
    register.write_text(
        register.read_text(encoding="utf-8")
        + "| f1 | 1 | 1 | q | v0 | finding | text | folded |\n",
        encoding="utf-8",
    )
    rc = lens_commit.main([
        str(plan), "--register", str(register),
        "--walk", "1", "--lens", "1", "--desc", "fail-test",
    ])
    out = capsys.readouterr().out
    fail_lines = [l for l in out.splitlines() if "plan_lint FAIL — FAIL: (y) undeclared QA step" in l]
    assert fail_lines, f"Expected LENS-COMMIT: plan_lint FAIL — FAIL: (y)... line, got:\n{out}"
    assert any(
        "cycle WARN — WARN: BAR_MET downgraded to CONTINUE" in l for l in out.splitlines()
    ), f"Expected cycle WARN echo, got:\n{out}"
    assert any("cycle OK — CONTINUE" in l for l in out.splitlines()), (
        f"Expected 'cycle OK — CONTINUE', got:\n{out}"
    )
    assert rc == 0, f"Expected exit 0, got {rc}:\n{out}"
    log_after = _git(tmp_path, "log", "--oneline").stdout.strip().count("\n")
    assert log_after == log_before + 1, f"Expected one new commit, got:\n{_git(tmp_path, 'log', '--oneline').stdout}"


# ---- l14: folding walk returns CONTINUE — accepted, cycle OK — CONTINUE printed ----


def test_l14_continue_accepted_on_folding_walk(tmp_path, capsys):
    """Folding walk: cycle_check returns CONTINUE; cycle OK — CONTINUE printed; commit made."""
    plan, register = _make_lens_fixture(tmp_path)
    plan.write_text(
        plan.read_text(encoding="utf-8").replace(
            "- Weak spots: w1 dry.",
            "- Weak spots: w1 1 folded — instruction 1 / record 0.",
        ),
        encoding="utf-8",
    )
    register.write_text(
        register.read_text(encoding="utf-8")
        + "| f1 | 1 | 1 | q | v0 | finding | text | folded |\n",
        encoding="utf-8",
    )
    rc = lens_commit.main([
        str(plan), "--register", str(register),
        "--walk", "1", "--lens", "1", "--desc", "folded",
    ])
    out = capsys.readouterr().out
    assert rc == 0, f"Expected exit 0, got {rc}:\n{out}"
    assert any("cycle OK — CONTINUE" in l for l in out.splitlines()), (
        f"Expected 'cycle OK — CONTINUE' in output:\n{out}"
    )
    assert any("commit OK" in l for l in out.splitlines()), (
        f"Expected 'commit OK' in output:\n{out}"
    )
    shown = _git(tmp_path, "show", "--name-only", "--format=", "HEAD").stdout.split()
    assert "plan.md" in shown
    assert "register.md" in shown
    assert ".plan.md.foldcheck.json" in shown


# ---- l15: ESCALATE:* still refuses (pins today's refusal of escalation) ----


def test_l15_escalation_still_refuses(tmp_path, capsys, monkeypatch):
    """ESCALATE:assert-fail is not CONTINUE or BAR_MET; cycle gate still refuses (pins today's refusal)."""
    plan, register = _make_lens_fixture(tmp_path)

    _real = lens_commit.run_checker

    def fake_run_checker(script, *args):
        if script == "cycle_check.py" and "--emit-manifest" not in args:
            return 1, "ESCALATE:assert-fail:2\n"
        return _real(script, *args)

    monkeypatch.setattr(lens_commit, "run_checker", fake_run_checker)

    rc = lens_commit.main([
        str(plan), "--register", str(register),
        "--walk", "1", "--lens", "1", "--desc", "escalation", "--dry",
    ])
    out = capsys.readouterr().out
    assert rc == 1, f"Expected exit 1, got {rc}:\n{out}"
    assert "cycle FAIL" in out, f"Expected cycle FAIL refusal, got:\n{out}"
    assert "ESCALATE:assert-fail:2" in out, f"Expected escalation named in refusal, got:\n{out}"


# ---- l16: WARN: lines from cycle_check echoed as LENS-COMMIT: cycle WARN — <line> ----


def test_l16_downgrade_warn_echoed(tmp_path, capsys, monkeypatch):
    """WARN: lines from cycle_check output echoed as 'LENS-COMMIT: cycle WARN — <line>'."""
    plan, register = _make_lens_fixture(tmp_path)

    _real = lens_commit.run_checker

    def fake_run_checker(script, *args):
        if script == "cycle_check.py" and "--emit-manifest" not in args:
            return 0, (
                "BATTERY: plan_lint=1_FAIL fold_check=VACUOUS propagation_check=NOT_RUN\n"
                "WARN: BAR_MET downgraded to CONTINUE — battery: plan_lint=1_FAIL"
                " — fix the FAIL(s) plan_lint names before the next walk\n"
                "CONTINUE\n"
            )
        return _real(script, *args)

    monkeypatch.setattr(lens_commit, "run_checker", fake_run_checker)

    rc = lens_commit.main([
        str(plan), "--register", str(register),
        "--walk", "1", "--lens", "1", "--desc", "echo-test", "--dry",
    ])
    out = capsys.readouterr().out
    assert rc == 0, f"Expected exit 0, got {rc}:\n{out}"
    assert any(
        "cycle WARN — WARN: BAR_MET downgraded to CONTINUE" in l for l in out.splitlines()
    ), f"Expected WARN echo, got:\n{out}"
    assert any("cycle OK — CONTINUE" in l for l in out.splitlines()), (
        f"Expected 'cycle OK — CONTINUE', got:\n{out}"
    )


# ---- l17: --desc naming a lens token is refused ----


def test_l17_desc_with_lens_token_refused(tmp_path, capsys):
    """--desc "QA lens 2" with --dry refuses before any commit; assert FAIL message emitted."""
    plan, register = _make_lens_fixture(tmp_path)
    count_before = _git(tmp_path, "rev-list", "--count", "HEAD").stdout.strip()

    rc = lens_commit.main([
        str(plan), "--register", str(register),
        "--walk", "1", "--lens", "1", "--desc", "QA lens 2", "--dry",
    ])
    out = capsys.readouterr().out
    assert rc == 1, f"Expected exit 1, got {rc}:\n{out}"
    assert any(
        "assert FAIL — --desc must not name a lens or walk number" in l
        for l in out.splitlines()
    ), f"Expected assert FAIL message, got:\n{out}"
    count_after = _git(tmp_path, "rev-list", "--count", "HEAD").stdout.strip()
    assert count_before == count_after, "No commit should be made on refusal"


# ---- l18: --desc naming a walk token is refused ----


def test_l18_desc_with_walk_token_refused(tmp_path, capsys):
    """--desc "walk 0 seed" refuses before any commit; same assert FAIL message."""
    plan, register = _make_lens_fixture(tmp_path)
    count_before = _git(tmp_path, "rev-list", "--count", "HEAD").stdout.strip()

    rc = lens_commit.main([
        str(plan), "--register", str(register),
        "--walk", "1", "--lens", "1", "--desc", "walk 0 seed", "--dry",
    ])
    out = capsys.readouterr().out
    assert rc == 1, f"Expected exit 1, got {rc}:\n{out}"
    assert any(
        "assert FAIL — --desc must not name a lens or walk number" in l
        for l in out.splitlines()
    ), f"Expected assert FAIL message, got:\n{out}"
    count_after = _git(tmp_path, "rev-list", "--count", "HEAD").stdout.strip()
    assert count_before == count_after, "No commit should be made on refusal"


# ---- l19: prose with "lenses", "walks", "lens-2" passes (no observer token) ----


def test_l19_desc_prose_without_token_admitted(tmp_path, capsys):
    """--desc with "lenses", "walks", "lens-2" in prose: no observer token, rc 0 and commit OK."""
    plan, register = _make_lens_fixture(tmp_path)

    rc = lens_commit.main([
        str(plan), "--register", str(register),
        "--walk", "1", "--lens", "1", "--desc", "lenses and walks in prose, lens-2 style", "--dry",
    ])
    out = capsys.readouterr().out
    assert rc == 0, f"Expected exit 0, got {rc}:\n{out}"
    assert any("commit OK" in l for l in out.splitlines()), f"Expected commit OK, got:\n{out}"
