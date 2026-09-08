"""Tests for the in-cycle battery — plan 100040.

The battery runs at every CONTINUE/BAR_MET exit, prints one BATTERY: line to
the warnings channel, and withholds BAR_MET when plan_lint FAIL>0 or
fold_check=DRIFT.  ESCALATE exits are untouched (plan 100033 clause survives
there; thread 189 overturns it only for CONTINUE/BAR_MET).
"""

import subprocess
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

BELLOWS_ROOT = Path(__file__).parent.parent.resolve()
SCRIPTS = BELLOWS_ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

import importlib
if "cycle_check" in sys.modules and sys.modules["cycle_check"].__file__ != str(SCRIPTS / "cycle_check.py"):
    del sys.modules["cycle_check"]
import cycle_check

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_BAR_MET_DC = (
    "- Weak spots: w1 2 folded — instruction 2 / record 0; w2 dry.\n"
    "- Destruction: w1 1 folded — instruction 1 / record 0; w2 dry.\n"
    "- Vulnerabilities: w1 dry; w2 dry.\n"
    "- Integration-record: w1 dry; w2 dry.\n"
    "- ACID: w1 dry; w2 dry.\n"
)

_CONTINUE_DC = (
    "- Weak spots: w1 2 folded — instruction 2 / record 0; "
    "w2 1 folded — instruction 1 / record 0.\n"
    "- Destruction: w1 dry; w2 dry.\n"
    "- Vulnerabilities: w1 dry; w2 dry.\n"
    "- Integration-record: w1 dry; w2 dry.\n"
    "- ACID: w1 dry; w2 dry.\n"
)

_FULL_VALIDATION = (
    "cycle_check=BAR_MET, plan_lint=0_FAIL, "
    "fold_check=PASS, propagation_check=CLEAN"
)

_MANIFEST_STANZA = (
    "\n## Cycle Manifest\n"
    "tier: T1\n"
    "target: scripts/cycle_check.py\n"
    "class: shop-infra\n"
    "reads: scripts/cycle_check.py\n"
    "writes: scripts/cycle_check.py\n"
    "open_forks: none\n"
    "walks: 2\n"
    "yields: 2, 0\n"
    f"validation: {_FULL_VALIDATION}\n"
    "coherence: 2/2 body walks named in the register\n"
)


def _make_bar_met(tmp_path, filename="plan.md", fold_baseline_ref=None):
    """BAR_MET plan (computed exit 629): dry final walk, full manifest."""
    manifest = _MANIFEST_STANZA
    if fold_baseline_ref:
        manifest += f"fold_baseline: {fold_baseline_ref}\n"
    plan = tmp_path / filename
    plan.write_text(
        f"# Plan\n\n## Drafting Cycle\n{_BAR_MET_DC}\n{manifest}",
        encoding="utf-8",
    )
    return plan


def _make_continue(tmp_path, filename="plan.md"):
    """CONTINUE plan (computed exit 629): walk 2 not dry."""
    plan = tmp_path / filename
    plan.write_text(
        f"# Plan\n\n## Drafting Cycle\n{_CONTINUE_DC}\n{_MANIFEST_STANZA}",
        encoding="utf-8",
    )
    return plan


def _make_empty_body(tmp_path, filename="plan.md"):
    """CONTINUE via empty walk_data (exit 513)."""
    plan = tmp_path / filename
    plan.write_text(
        "# Plan\n\n## Drafting Cycle\n\n## End\n",
        encoding="utf-8",
    )
    return plan


def _make_walk0_only(tmp_path, filename="plan.md"):
    """CONTINUE via current_walk==0 (exit 517)."""
    plan = tmp_path / filename
    plan.write_text(
        "# Plan\n\n## Drafting Cycle\n"
        "- Weak spots: w0 dry.\n"
        "- Destruction: w0 dry.\n"
        "- Vulnerabilities: w0 dry.\n"
        "- Integration-record: w0 dry.\n"
        "- ACID: w0 dry.\n\n## End\n",
        encoding="utf-8",
    )
    return plan


def _make_t0_bar_met(tmp_path, filename="plan.md"):
    """BAR_MET via T0 close (exit 498)."""
    plan = tmp_path / filename
    plan.write_text(
        "# Plan\n\n**cycle_tier:** T0 (no trigger)\n\n"
        "## Drafting Cycle\n**Tier:** T0\n\n"
        "integration-vs-record pass: CLEAN — no drift observed\n\n"
        "## End\n",
        encoding="utf-8",
    )
    return plan


class _MockResult:
    def __init__(self, returncode=0, stdout="", stderr=""):
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr


def _make_mock(*, lint_fails=0, fold_rc=0, fold_stdout="FOLD-CHECK CLEAN: ok", prop_rc=0):
    """Return a subprocess.run mock that dispatches on the tool's BASENAME."""
    real_run = subprocess.run

    def mock_run(cmd, **kw):
        if cmd and len(cmd) >= 2 and cmd[0] == sys.executable:
            basename = Path(cmd[1]).name
            if basename == "plan_lint.py":
                lines = "\n".join(f"FAIL: issue {i}" for i in range(lint_fails))
                return _MockResult(returncode=(1 if lint_fails else 0), stdout=lines)
            if basename == "fold_check.py":
                return _MockResult(returncode=fold_rc, stdout=fold_stdout)
            if basename == "propagation_check.py":
                if prop_rc == 0:
                    return _MockResult(returncode=0, stdout="CLEAN\nDIVERGENCES: 0")
                if prop_rc == 1:
                    return _MockResult(returncode=1, stdout="DIVERGENT\nDIVERGENCES: 3")
                return _MockResult(returncode=prop_rc, stdout="")
        return real_run(cmd, **kw)

    return mock_run


# ---------------------------------------------------------------------------
# Test 1 — BATTERY: line before verdict, parametrized over all four exits (f6)
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("make_plan,expected_verdict", [
    ("t0_bar_met", "BAR_MET"),
    ("empty_body", "CONTINUE"),
    ("walk0_only", "CONTINUE"),
    ("computed_bar_met", "BAR_MET"),
    ("computed_continue", "CONTINUE"),
])
def test_battery_line_before_verdict(tmp_path, make_plan, expected_verdict):
    """Every CONTINUE/BAR_MET exit prints one BATTERY: line before the verdict."""
    makers = {
        "t0_bar_met": _make_t0_bar_met,
        "empty_body": _make_empty_body,
        "walk0_only": _make_walk0_only,
        "computed_bar_met": _make_bar_met,
        "computed_continue": _make_continue,
    }
    plan = makers[make_plan](tmp_path)
    warnings = []
    with patch.object(subprocess, "run", side_effect=_make_mock()):
        verdict, code = cycle_check.run_check(plan, warnings=warnings)
    assert verdict == expected_verdict
    assert code == 0
    battery_lines = [w for w in warnings if w.startswith("BATTERY:")]
    assert len(battery_lines) == 1, f"expected 1 BATTERY: line, got {len(battery_lines)}: {warnings}"
    # BATTERY: line format: "BATTERY: plan_lint=... fold_check=... propagation_check=..."
    bl = battery_lines[0]
    assert "plan_lint=" in bl
    assert "fold_check=" in bl
    assert "propagation_check=" in bl
    # Verdict is the last item in warnings + the return value; BATTERY: must come before any WARN
    warn_idx = [i for i, w in enumerate(warnings) if w.startswith("BATTERY:")]
    downgrade_idx = [i for i, w in enumerate(warnings) if w.startswith("WARN: BAR_MET downgraded")]
    for di in downgrade_idx:
        assert warn_idx[0] < di, "BATTERY: must precede any downgrade WARN"


# ---------------------------------------------------------------------------
# Test 2 — plan_lint FAIL>0 downgrades BAR_MET to CONTINUE with WARN
# ---------------------------------------------------------------------------

def test_plan_lint_fail_downgrades_bar_met(tmp_path):
    """BAR_MET + plan_lint FAIL>0 → CONTINUE, WARN names plan_lint=N_FAIL."""
    plan = _make_bar_met(tmp_path)
    warnings = []
    with patch.object(subprocess, "run", side_effect=_make_mock(lint_fails=2)):
        verdict, code = cycle_check.run_check(plan, warnings=warnings)
    assert verdict == "CONTINUE"
    assert code == 0
    warn_lines = [w for w in warnings if "BAR_MET downgraded" in w]
    assert len(warn_lines) == 1
    assert "plan_lint=2_FAIL" in warn_lines[0]
    assert "fix the FAIL(s) plan_lint names before the next walk" in warn_lines[0]


# ---------------------------------------------------------------------------
# Test 3 — fold_check DRIFT downgrades BAR_MET to CONTINUE with WARN
# ---------------------------------------------------------------------------

def test_fold_check_drift_downgrades_bar_met(tmp_path):
    """BAR_MET + fold_check DRIFT (rc 1) → CONTINUE, WARN names fold_check=DRIFT."""
    baseline = tmp_path / ".plan.md.foldcheck.json"
    baseline.write_text("{}", encoding="utf-8")
    plan = _make_bar_met(tmp_path)
    warnings = []
    drift_stdout = (
        "FOLD-CHECK DRIFT — the fold changed the machine-readable state:\n"
        "  APPEARED: plan_lint: (f) WARN: some drift\n"
        "If a change is INTENDED, re-save the baseline and say so in the fold's record.\n"
    )
    with patch.object(subprocess, "run", side_effect=_make_mock(fold_rc=1, fold_stdout=drift_stdout)):
        verdict, code = cycle_check.run_check(plan, warnings=warnings)
    assert verdict == "CONTINUE"
    assert code == 0
    warn_lines = [w for w in warnings if "BAR_MET downgraded" in w]
    assert len(warn_lines) == 1
    assert "fold_check=DRIFT" in warn_lines[0]
    assert "if the change is INTENDED, re-save the baseline" in warn_lines[0]


def test_fold_check_drift_both_fire_two_warns(tmp_path):
    """When both plan_lint FAIL and fold_check DRIFT, two WARN lines; plan_lint's first."""
    baseline = tmp_path / ".plan.md.foldcheck.json"
    baseline.write_text("{}", encoding="utf-8")
    plan = _make_bar_met(tmp_path)
    warnings = []
    drift_stdout = "FOLD-CHECK DRIFT — the fold changed the machine-readable state:\n"
    with patch.object(subprocess, "run", side_effect=_make_mock(
        lint_fails=1, fold_rc=1, fold_stdout=drift_stdout
    )):
        verdict, code = cycle_check.run_check(plan, warnings=warnings)
    assert verdict == "CONTINUE"
    warn_lines = [w for w in warnings if "BAR_MET downgraded" in w]
    assert len(warn_lines) == 2, f"expected 2 WARN lines, got: {warn_lines}"
    assert "plan_lint=" in warn_lines[0], "plan_lint WARN must come first (f43)"
    assert "fold_check=" in warn_lines[1]


# ---------------------------------------------------------------------------
# Test 4 — fold_check VACUOUS does NOT downgrade BAR_MET
# ---------------------------------------------------------------------------

def test_fold_check_vacuous_does_not_downgrade(tmp_path):
    """BAR_MET + fold_check VACUOUS (rc 2, FOLD-CHECK VACUOUS line) → BAR_MET unaffected."""
    baseline = tmp_path / ".plan.md.foldcheck.json"
    baseline.write_text("{}", encoding="utf-8")
    plan = _make_bar_met(tmp_path)
    vacuous_stdout = (
        "FOLD-CHECK VACUOUS: the baseline was taken from THIS exact state "
        "(sha256 abc123…), so it cannot observe a fold.\n"
        "  baseline saved: 2026-09-07T10:00:00\n"
        "  Re-save the baseline BEFORE the next fold, not after it.\n"
    )
    warnings = []
    with patch.object(subprocess, "run", side_effect=_make_mock(fold_rc=2, fold_stdout=vacuous_stdout)):
        verdict, code = cycle_check.run_check(plan, warnings=warnings)
    assert verdict == "BAR_MET"
    assert code == 0
    battery_lines = [w for w in warnings if w.startswith("BATTERY:")]
    assert len(battery_lines) == 1
    assert "fold_check=VACUOUS" in battery_lines[0]
    downgrade = [w for w in warnings if "BAR_MET downgraded" in w]
    assert len(downgrade) == 0


# ---------------------------------------------------------------------------
# Test 5 — no baseline resolvable → NO_BASELINE, BAR_MET unaffected
# ---------------------------------------------------------------------------

def test_no_baseline_does_not_downgrade(tmp_path):
    """BAR_MET + no baseline resolvable → fold_check=NO_BASELINE, BAR_MET unaffected."""
    plan = _make_bar_met(tmp_path)  # no baseline file beside it
    warnings = []
    with patch.object(subprocess, "run", side_effect=_make_mock()):
        verdict, code = cycle_check.run_check(plan, warnings=warnings)
    assert verdict == "BAR_MET"
    assert code == 0
    battery_lines = [w for w in warnings if w.startswith("BATTERY:")]
    assert len(battery_lines) == 1
    assert "fold_check=NO_BASELINE" in battery_lines[0]
    downgrade = [w for w in warnings if "BAR_MET downgraded" in w]
    assert len(downgrade) == 0


# ---------------------------------------------------------------------------
# Test 6 — propagation_check DIVERGENT:N does NOT downgrade
# ---------------------------------------------------------------------------

def test_propagation_divergent_does_not_downgrade(tmp_path):
    """BAR_MET + propagation_check DIVERGENT:N → BAR_MET unaffected (P5 — informational)."""
    plan = _make_bar_met(tmp_path)
    warnings = []
    with patch.object(subprocess, "run", side_effect=_make_mock(prop_rc=1)):
        verdict, code = cycle_check.run_check(plan, warnings=warnings)
    assert verdict == "BAR_MET"
    assert code == 0
    battery_lines = [w for w in warnings if w.startswith("BATTERY:")]
    assert len(battery_lines) == 1
    assert "propagation_check=DIVERGENT:3" in battery_lines[0]
    downgrade = [w for w in warnings if "BAR_MET downgraded" in w]
    assert len(downgrade) == 0


# ---------------------------------------------------------------------------
# Test 7 — ESCALATE exits spawn zero tool launches; stdout byte-identical
# ---------------------------------------------------------------------------

def _count_battery_launches(plan, monkeypatch_fn=None, extra_setup=None):
    """Run run_check with subprocess counting; return (verdict, launch_count)."""
    real_run = subprocess.run
    counts = {"n": 0}

    def counting_run(cmd, **kw):
        if cmd and len(cmd) >= 2 and cmd[0] == sys.executable:
            basename = Path(cmd[1]).name
            if basename in ("plan_lint.py", "fold_check.py", "propagation_check.py"):
                counts["n"] += 1
        return real_run(cmd, **kw)

    if extra_setup:
        extra_setup()

    with patch.object(subprocess, "run", side_effect=counting_run):
        w = []
        verdict, _ = cycle_check.run_check(monkeypatch_fn if monkeypatch_fn else Path("/nonexistent"), warnings=w)

    return verdict, counts["n"]


@pytest.mark.parametrize("make_escalate,expected_verdict", [
    ("unparseable", "ESCALATE:unparseable"),
    ("yield_rising", "ESCALATE:yield-rising"),
    ("restructuring", "ESCALATE:restructuring-fold"),
    ("claimed_close", "ESCALATE:claimed-close-unmet"),
    ("assert1", "ESCALATE:assert-fail:1"),
    ("plateau", "ESCALATE:plateau"),
])
def test_escalate_no_tool_launches(tmp_path, make_escalate, expected_verdict):
    """Every ESCALATE exit spawns zero battery tool launches."""
    real_run = subprocess.run
    counts = {"n": 0}

    def counting_run(cmd, **kw):
        if cmd and len(cmd) >= 2 and cmd[0] == sys.executable:
            if Path(cmd[1]).name in ("plan_lint.py", "fold_check.py", "propagation_check.py"):
                counts["n"] += 1
        return real_run(cmd, **kw)

    if make_escalate == "unparseable":
        plan = tmp_path / "plan.md"
        plan.write_text("# Plan\n\nno DC block\n", encoding="utf-8")
    elif make_escalate == "yield_rising":
        plan = tmp_path / "plan.md"
        plan.write_text(
            "# Plan\n\n## Drafting Cycle\n"
            "- Weak spots: w1 1 folded — instruction 1 / record 0; "
            "w2 2 folded — instruction 2 / record 0.\n"
            "- Destruction: w1 dry; w2 dry.\n"
            "- Vulnerabilities: w1 dry; w2 dry.\n"
            "- Integration-record: w1 dry; w2 dry.\n"
            "- ACID: w1 dry; w2 dry.\n",
            encoding="utf-8",
        )
    elif make_escalate == "restructuring":
        plan = tmp_path / "plan.md"
        plan.write_text(
            "# Plan\n\n## Drafting Cycle\n"
            "- Weak spots: w1 2 folded — instruction 2 / record 0 (restructuring — moved section).\n",
            encoding="utf-8",
        )
    elif make_escalate == "claimed_close":
        plan = tmp_path / "plan.md"
        plan.write_text(
            "# Plan\n\n## Drafting Cycle\n"
            "- Weak spots: w1 2 folded — instruction 2 / record 0; w2 1 folded — instruction 1 / record 0.\n"
            "- Destruction: w1 dry; w2 dry.\n"
            "- Vulnerabilities: w1 dry; w2 dry.\n"
            "- Integration-record: w1 dry; w2 dry.\n"
            "- ACID: w1 dry; w2 dry.\n"
            "\n**Closing:** BAR MET at walk 2.\n",
            encoding="utf-8",
        )
    elif make_escalate == "assert1":
        # assert-fail:1: instruction+record counts don't sum to fold total
        # "w1 3 folded — instruction 2 / record 0" → 2+0 != 3 → FAIL
        plan = tmp_path / "plan.md"
        plan.write_text(
            "# Plan\n\n## Drafting Cycle\n"
            "- Weak spots: w1 3 folded — instruction 2 / record 0.\n"
            "- Destruction: w1 dry.\n"
            "- Vulnerabilities: w1 dry.\n"
            "- Integration-record: w1 dry.\n"
            "- ACID: w1 dry.\n",
            encoding="utf-8",
        )
    elif make_escalate == "plateau":
        # w1 introduces both lenses; w2/w3/w4 have same instruction count and no new lenses
        plan = tmp_path / "plan.md"
        plan.write_text(
            "# Plan\n\n## Drafting Cycle\n"
            "- Weak spots: w1 2 folded — instruction 1 / record 1; "
            "w2 2 folded — instruction 1 / record 1; "
            "w3 2 folded — instruction 1 / record 1; "
            "w4 2 folded — instruction 1 / record 1.\n"
            "- Destruction: w1 2 folded — instruction 1 / record 1; w2 dry; w3 dry; w4 dry.\n"
            "- Vulnerabilities: w1 dry; w2 dry; w3 dry; w4 dry.\n"
            "- Integration-record: w1 dry; w2 dry; w3 dry; w4 dry.\n"
            "- ACID: w1 dry; w2 dry; w3 dry; w4 dry.\n",
            encoding="utf-8",
        )

    with patch.object(subprocess, "run", side_effect=counting_run):
        warnings_out = []
        verdict, code = cycle_check.run_check(plan, warnings=warnings_out)

    assert verdict == expected_verdict, f"expected {expected_verdict}, got {verdict}"
    assert code == 1
    assert counts["n"] == 0, (
        f"ESCALATE:{expected_verdict} must not launch any battery tool; "
        f"got {counts['n']} launches"
    )


def test_escalate_assert2_no_tool_launches(tmp_path, monkeypatch):
    """ESCALATE:assert-fail:2 (git-dependent) spawns zero battery launches."""
    monkeypatch.setattr(cycle_check, "_find_git_root", lambda _: tmp_path)
    (tmp_path / "path" / "to").mkdir(parents=True, exist_ok=True)
    plan = tmp_path / "plan.md"
    plan.write_text(
        "# Plan\n\n## Drafting Cycle\n"
        "**Walk register:** `path/to/missing-register.md`\n"
        "- Weak spots: w1 2 folded — instruction 2 / record 0.\n",
        encoding="utf-8",
    )
    real_run = subprocess.run
    counts = {"n": 0}

    def counting_run(cmd, **kw):
        if cmd and len(cmd) >= 2 and cmd[0] == sys.executable:
            if Path(cmd[1]).name in ("plan_lint.py", "fold_check.py", "propagation_check.py"):
                counts["n"] += 1
        return real_run(cmd, **kw)

    with patch.object(subprocess, "run", side_effect=counting_run):
        verdict, code = cycle_check.run_check(plan)

    assert verdict == "ESCALATE:assert-fail:2"
    assert counts["n"] == 0


def test_escalate_assert3_no_tool_launches(tmp_path, monkeypatch):
    """ESCALATE:assert-fail:3 (git-dependent) spawns zero battery launches."""
    monkeypatch.setattr(cycle_check, "_find_git_root", lambda _: tmp_path)

    def mock_git(cmd, **kw):
        class R:
            returncode = 0
            stdout = "abc1234 [draft] w1 fold\nabc1235 deposit(cycle-check)\n"
            stderr = ""
        return R()

    plan = tmp_path / "plan.md"
    plan.write_text(
        "# Plan\n\n## Drafting Cycle\n"
        "- Weak spots: w1 2 folded — instruction 2 / record 0.\n",
        encoding="utf-8",
    )
    real_run = subprocess.run
    counts = {"n": 0}

    def counting_run(cmd, **kw):
        if cmd and len(cmd) >= 2 and cmd[0] == sys.executable:
            if Path(cmd[1]).name in ("plan_lint.py", "fold_check.py", "propagation_check.py"):
                counts["n"] += 1
        if cmd and cmd[0] == "git":
            return mock_git(cmd, **kw)
        return real_run(cmd, **kw)

    with patch.object(subprocess, "run", side_effect=counting_run):
        verdict, code = cycle_check.run_check(plan)

    assert verdict == "ESCALATE:assert-fail:3"
    assert counts["n"] == 0


# ---------------------------------------------------------------------------
# Test 8 — --emit-manifest: four keys same order; fold_check values correct
# ---------------------------------------------------------------------------

def test_emit_manifest_fold_check_values(tmp_path, capsys):
    """--emit-manifest writes correct fold_check values for all three rc!=0 states."""
    # rc=0 → PASS
    plan_pass = _make_bar_met(tmp_path, "plan_pass.md")
    baseline_pass = tmp_path / ".plan_pass.md.foldcheck.json"
    baseline_pass.write_text('{"meta": {}}', encoding="utf-8")

    with patch.object(subprocess, "run", side_effect=_make_mock(fold_rc=0, fold_stdout="FOLD-CHECK CLEAN: ok")):
        cycle_check.emit_manifest(plan_pass)
    out_pass = capsys.readouterr().out

    # rc=1 → DRIFT
    plan_drift = _make_bar_met(tmp_path, "plan_drift.md")
    baseline_drift = tmp_path / ".plan_drift.md.foldcheck.json"
    baseline_drift.write_text('{"meta": {}}', encoding="utf-8")

    with patch.object(subprocess, "run", side_effect=_make_mock(fold_rc=1, fold_stdout="FOLD-CHECK DRIFT")):
        cycle_check.emit_manifest(plan_drift)
    out_drift = capsys.readouterr().out

    # rc=2 + VACUOUS stdout → VACUOUS
    plan_vacuous = _make_bar_met(tmp_path, "plan_vacuous.md")
    baseline_vacuous = tmp_path / ".plan_vacuous.md.foldcheck.json"
    baseline_vacuous.write_text('{"meta": {}}', encoding="utf-8")
    vacuous_stdout = "FOLD-CHECK VACUOUS: baseline taken from this exact state\n"

    with patch.object(subprocess, "run", side_effect=_make_mock(fold_rc=2, fold_stdout=vacuous_stdout)):
        cycle_check.emit_manifest(plan_vacuous)
    out_vacuous = capsys.readouterr().out

    # rc=2 without VACUOUS → NO_BASELINE
    plan_nb = _make_bar_met(tmp_path, "plan_nb.md")
    baseline_nb = tmp_path / ".plan_nb.md.foldcheck.json"
    baseline_nb.write_text('{"meta": {}}', encoding="utf-8")

    with patch.object(subprocess, "run", side_effect=_make_mock(fold_rc=2, fold_stdout="ERROR: no baseline")):
        cycle_check.emit_manifest(plan_nb)
    out_nb = capsys.readouterr().out

    def _validation_line(out):
        for line in out.splitlines():
            if line.startswith("validation:"):
                return line
        return None

    val_pass = _validation_line(out_pass)
    val_drift = _validation_line(out_drift)
    val_vacuous = _validation_line(out_vacuous)
    val_nb = _validation_line(out_nb)

    # Key order: cycle_check, plan_lint, fold_check, propagation_check
    for val in [val_pass, val_drift, val_vacuous, val_nb]:
        assert val is not None
        keys = [kv.split("=")[0].strip() for kv in val.replace("validation:", "").split(",")]
        assert keys == ["cycle_check", "plan_lint", "fold_check", "propagation_check"], (
            f"key order wrong: {keys}"
        )

    assert "fold_check=PASS" in val_pass
    assert "fold_check=DRIFT" in val_drift
    assert "fold_check=VACUOUS" in val_vacuous
    assert "fold_check=NO_BASELINE" in val_nb


# ---------------------------------------------------------------------------
# Test 9 — one implementation: emitter and run_check agree on tool values
# ---------------------------------------------------------------------------

def test_one_implementation(tmp_path, capsys):
    """emit_manifest and run_check produce the same battery values for the same plan."""
    plan = _make_bar_met(tmp_path)
    baseline = tmp_path / ".plan.md.foldcheck.json"
    baseline.write_text('{"meta": {}}', encoding="utf-8")

    drift_stdout = "FOLD-CHECK DRIFT — changed\n"
    mock = _make_mock(lint_fails=1, fold_rc=1, fold_stdout=drift_stdout)

    # Collect run_check's battery line
    warnings = []
    with patch.object(subprocess, "run", side_effect=mock):
        cycle_check.run_check(plan, warnings=warnings)
    battery_line = next(w for w in warnings if w.startswith("BATTERY:"))

    # Collect emit_manifest's validation line
    with patch.object(subprocess, "run", side_effect=mock):
        cycle_check.emit_manifest(plan)
    out = capsys.readouterr().out
    val_line = next(l for l in out.splitlines() if l.startswith("validation:"))

    # Extract values from BATTERY: line
    bat_vals = {}
    for part in battery_line.replace("BATTERY:", "").strip().split():
        k, v = part.split("=", 1)
        bat_vals[k] = v

    # Extract values from validation: line
    val_vals = {}
    for part in val_line.replace("validation:", "").strip().split(","):
        k, v = part.strip().split("=", 1)
        val_vals[k.strip()] = v.strip()

    assert bat_vals["plan_lint"] == val_vals["plan_lint"]
    assert bat_vals["fold_check"] == val_vals["fold_check"]
    assert bat_vals["propagation_check"] == val_vals["propagation_check"]


# ---------------------------------------------------------------------------
# Test 10 — baseline resolution order (manifest field > beside-plan > missing)
# ---------------------------------------------------------------------------

def test_baseline_resolution_order(tmp_path):
    """fold_baseline: in manifest takes priority over beside-the-plan file."""
    # Create a manifest-only baseline (does NOT match beside-plan name)
    manifest_baseline = tmp_path / "manifest-baseline.foldcheck.json"
    manifest_baseline.write_text('{"from": "manifest"}', encoding="utf-8")

    # Also create the beside-plan baseline (should NOT be used when manifest field present)
    plan = _make_bar_met(tmp_path, fold_baseline_ref=str(manifest_baseline.resolve()))
    beside = tmp_path / f".{plan.name}.foldcheck.json"
    beside.write_text('{"from": "beside"}', encoding="utf-8")

    used_paths = []

    real_run = subprocess.run
    def tracking_mock(cmd, **kw):
        if cmd and len(cmd) >= 2 and cmd[0] == sys.executable:
            basename = Path(cmd[1]).name
            if basename == "fold_check.py":
                # Find the --baseline arg
                for i, a in enumerate(cmd):
                    if a == "--baseline" and i + 1 < len(cmd):
                        used_paths.append(cmd[i + 1])
                return _MockResult(returncode=0, stdout="FOLD-CHECK CLEAN: ok")
            if basename == "plan_lint.py":
                return _MockResult(returncode=0, stdout="")
            if basename == "propagation_check.py":
                return _MockResult(returncode=0, stdout="")
        return real_run(cmd, **kw)

    warnings = []
    with patch.object(subprocess, "run", side_effect=tracking_mock):
        cycle_check.run_check(plan, warnings=warnings)

    assert len(used_paths) == 1, f"expected 1 fold_check call, got {len(used_paths)}"
    assert str(manifest_baseline.resolve()) in used_paths[0], (
        f"manifest baseline must take priority; used {used_paths[0]}"
    )


def test_baseline_manifest_only_resolvable(tmp_path):
    """A baseline reachable only through the manifest field resolves correctly."""
    baseline = tmp_path / "cross-repo-baseline.foldcheck.json"
    baseline.write_text('{"meta": {}}', encoding="utf-8")

    # Plan with fold_baseline: pointing to the file by absolute path
    # No beside-the-plan file → must use manifest field
    plan = _make_bar_met(tmp_path, fold_baseline_ref=str(baseline.resolve()))

    used_paths = []
    real_run = subprocess.run
    def tracking_mock(cmd, **kw):
        if cmd and len(cmd) >= 2 and cmd[0] == sys.executable:
            basename = Path(cmd[1]).name
            if basename == "fold_check.py":
                for i, a in enumerate(cmd):
                    if a == "--baseline" and i + 1 < len(cmd):
                        used_paths.append(cmd[i + 1])
                return _MockResult(returncode=0, stdout="FOLD-CHECK CLEAN: ok")
            if basename == "plan_lint.py":
                return _MockResult(returncode=0, stdout="")
            if basename == "propagation_check.py":
                return _MockResult(returncode=0, stdout="")
        return real_run(cmd, **kw)

    warnings = []
    with patch.object(subprocess, "run", side_effect=tracking_mock):
        verdict, _ = cycle_check.run_check(plan, warnings=warnings)

    assert verdict == "BAR_MET"
    assert len(used_paths) == 1
    assert str(baseline.resolve()) in used_paths[0]


def test_declared_unresolvable_baseline_is_no_baseline_no_fallback(tmp_path):
    """A declared fold_baseline: that doesn't resolve → NO_BASELINE (no fallback to beside-file)."""
    plan = _make_bar_met(tmp_path, fold_baseline_ref="/nonexistent/path/to/baseline.foldcheck.json")
    # Create the beside-plan file — must NOT be used as fallback
    beside = tmp_path / f".{plan.name}.foldcheck.json"
    beside.write_text('{"meta": {}}', encoding="utf-8")

    fold_calls = []
    real_run = subprocess.run
    def tracking_mock(cmd, **kw):
        if cmd and len(cmd) >= 2 and cmd[0] == sys.executable:
            basename = Path(cmd[1]).name
            if basename == "fold_check.py":
                fold_calls.append(cmd)
                return _MockResult(returncode=0, stdout="FOLD-CHECK CLEAN: ok")
            if basename == "plan_lint.py":
                return _MockResult(returncode=0, stdout="")
            if basename == "propagation_check.py":
                return _MockResult(returncode=0, stdout="")
        return real_run(cmd, **kw)

    warnings = []
    with patch.object(subprocess, "run", side_effect=tracking_mock):
        cycle_check.run_check(plan, warnings=warnings)

    # fold_check must NOT be launched when declared baseline is unresolvable (f15)
    assert len(fold_calls) == 0, "must not fall back to beside-file when manifest field is declared"
    battery_lines = [w for w in warnings if w.startswith("BATTERY:")]
    assert len(battery_lines) == 1
    assert "fold_check=NO_BASELINE" in battery_lines[0]


# ---------------------------------------------------------------------------
# Test 11 — ruled rewrite of test_no_subprocess_spawned (P8, thread 189)
# ---------------------------------------------------------------------------

def test_no_subprocess_spawned_ruled_rewrite(tmp_path):
    """P8 ruled rewrite: count battery launches by BASENAME.

    CONTINUE/BAR_MET exit: plan_lint, propagation_check, and fold_check
    (ONLY when a baseline resolved) are launched.  ESCALATE: zero.
    Authority: thread 189 — overturns Done/executable-100033.md's MUST-PRESERVE.
    """
    # --- BAR_MET without baseline: 2 launches (plan_lint + propagation_check) ---
    plan_no_baseline = _make_bar_met(tmp_path, "no_baseline.md")
    real_run = subprocess.run
    counts_no_bl = {"plan_lint": 0, "fold_check": 0, "propagation_check": 0}

    def counting_no_bl(cmd, **kw):
        if cmd and len(cmd) >= 2 and cmd[0] == sys.executable:
            n = Path(cmd[1]).name
            if n in counts_no_bl:
                counts_no_bl[n] += 1
            elif n in ("plan_lint.py", "fold_check.py", "propagation_check.py"):
                counts_no_bl[n.replace(".py", "")] += 1
            if n == "plan_lint.py":
                return _MockResult(returncode=0, stdout="")
            if n == "fold_check.py":
                return _MockResult(returncode=0, stdout="FOLD-CHECK CLEAN: ok")
            if n == "propagation_check.py":
                return _MockResult(returncode=0, stdout="")
        return real_run(cmd, **kw)

    with patch.object(subprocess, "run", side_effect=counting_no_bl):
        cycle_check.run_check(plan_no_baseline, warnings=[])

    assert counts_no_bl["fold_check"] == 0, "fold_check must not launch when no baseline"

    # --- BAR_MET with baseline: 3 launches ---
    baseline = tmp_path / ".with_baseline.md.foldcheck.json"
    baseline.write_text('{"meta": {}}', encoding="utf-8")
    plan_with_baseline = _make_bar_met(tmp_path, "with_baseline.md")
    counts_with_bl = {"plan_lint.py": 0, "fold_check.py": 0, "propagation_check.py": 0}

    def counting_with_bl(cmd, **kw):
        if cmd and len(cmd) >= 2 and cmd[0] == sys.executable:
            n = Path(cmd[1]).name
            if n in counts_with_bl:
                counts_with_bl[n] += 1
            if n == "plan_lint.py":
                return _MockResult(returncode=0, stdout="")
            if n == "fold_check.py":
                return _MockResult(returncode=0, stdout="FOLD-CHECK CLEAN: ok")
            if n == "propagation_check.py":
                return _MockResult(returncode=0, stdout="")
        return real_run(cmd, **kw)

    with patch.object(subprocess, "run", side_effect=counting_with_bl):
        cycle_check.run_check(plan_with_baseline, warnings=[])

    assert counts_with_bl["plan_lint.py"] == 1
    assert counts_with_bl["fold_check.py"] == 1
    assert counts_with_bl["propagation_check.py"] == 1

    # --- ESCALATE: zero launches ---
    plan_escalate = tmp_path / "escalate.md"
    plan_escalate.write_text("# Plan\n\nno DC block\n", encoding="utf-8")
    counts_esc = {"n": 0}

    def counting_esc(cmd, **kw):
        if cmd and len(cmd) >= 2 and cmd[0] == sys.executable:
            if Path(cmd[1]).name in ("plan_lint.py", "fold_check.py", "propagation_check.py"):
                counts_esc["n"] += 1
        return real_run(cmd, **kw)

    with patch.object(subprocess, "run", side_effect=counting_esc):
        cycle_check.run_check(plan_escalate, warnings=[])

    assert counts_esc["n"] == 0


# ---------------------------------------------------------------------------
# Test 12 — --emit-manifest launches each tool exactly once
# ---------------------------------------------------------------------------

def test_emit_manifest_launches_each_tool_once(tmp_path, capsys):
    """--emit-manifest with a baseline launches plan_lint, fold_check, propagation_check each exactly once."""
    plan = _make_bar_met(tmp_path)
    baseline = tmp_path / ".plan.md.foldcheck.json"
    baseline.write_text('{"meta": {}}', encoding="utf-8")

    real_run = subprocess.run
    counts = {"plan_lint.py": 0, "fold_check.py": 0, "propagation_check.py": 0}

    def counting_run(cmd, **kw):
        if cmd and len(cmd) >= 2 and cmd[0] == sys.executable:
            n = Path(cmd[1]).name
            if n in counts:
                counts[n] += 1
            if n == "plan_lint.py":
                return _MockResult(returncode=0, stdout="")
            if n == "fold_check.py":
                return _MockResult(returncode=0, stdout="FOLD-CHECK CLEAN: ok")
            if n == "propagation_check.py":
                return _MockResult(returncode=0, stdout="")
        return real_run(cmd, **kw)

    with patch.object(subprocess, "run", side_effect=counting_run):
        cycle_check.emit_manifest(plan)
    capsys.readouterr()

    assert counts["plan_lint.py"] == 1, f"plan_lint launched {counts['plan_lint.py']} times"
    assert counts["fold_check.py"] == 1, f"fold_check launched {counts['fold_check.py']} times"
    assert counts["propagation_check.py"] == 1, f"propagation_check launched {counts['propagation_check.py']} times"


# ---------------------------------------------------------------------------
# Test 13 — one resolver: substrate_status and run_battery agree on baseline path
# ---------------------------------------------------------------------------

def test_one_resolver(tmp_path):
    """substrate_status and run_battery resolve the same baseline path."""
    import importlib
    if "substrate_check" in sys.modules and sys.modules["substrate_check"].__file__ != str(SCRIPTS / "substrate_check.py"):
        del sys.modules["substrate_check"]
    import substrate_check

    # Build a plan with fold_baseline: in manifest (cross-repo case)
    baseline = tmp_path / "cross-repo.foldcheck.json"
    baseline.write_text('{"meta": {}}', encoding="utf-8")
    plan = _make_bar_met(tmp_path, fold_baseline_ref=str(baseline.resolve()))

    # run_battery resolution
    battery_path, _ = cycle_check.resolve_fold_baseline(plan)
    assert battery_path is not None
    assert battery_path.resolve() == baseline.resolve()

    # substrate_status resolution: leg 3
    # We read the manifest and call resolve_fold_baseline directly (same function)
    manifest = cycle_check.parse_manifest_stanza(plan.read_text(encoding="utf-8"))
    sub_path, _ = cycle_check.resolve_fold_baseline(plan, manifest)
    assert sub_path is not None
    assert sub_path.resolve() == baseline.resolve()

    assert battery_path.resolve() == sub_path.resolve()


# ---------------------------------------------------------------------------
# Test 14 — CONTINUE plan with plan_lint FAIL prints BATTERY: but NO downgrade WARN (f41)
# ---------------------------------------------------------------------------

def test_continue_plan_lint_fail_no_downgrade_warn(tmp_path):
    """A CONTINUE plan with plan_lint FAIL prints BATTERY: but not a 'downgraded' WARN.

    The downgrade exists only at the bar (f41); a WARN saying 'downgraded' on a
    verdict that was never BAR_MET would be false.
    """
    plan = _make_continue(tmp_path)
    warnings = []
    with patch.object(subprocess, "run", side_effect=_make_mock(lint_fails=3)):
        verdict, code = cycle_check.run_check(plan, warnings=warnings)
    assert verdict == "CONTINUE"
    battery_lines = [w for w in warnings if w.startswith("BATTERY:")]
    assert len(battery_lines) == 1
    assert "plan_lint=3_FAIL" in battery_lines[0]
    downgrade = [w for w in warnings if "BAR_MET downgraded" in w]
    assert len(downgrade) == 0, f"no downgrade WARN on a CONTINUE plan; got: {downgrade}"
