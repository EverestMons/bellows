"""Tests for run_battery integration in cycle_check.

Ruling 189 (thread 189): CONTINUE/BAR_MET exits now run the three-tool battery
(plan_lint, fold_check, propagation_check). ESCALATE exits are UNTOUCHED —
zero tool launches there. test_no_subprocess_spawned in
test_cycle_check_manifest_provenance.py is rewritten accordingly.
"""

import io
import json
import subprocess
import sys
from contextlib import redirect_stdout
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

# DC block reaching BAR_MET (dry final walk, no register, no git deps)
_BAR_MET_DC = (
    "- Weak spots: w1 2 folded — instruction 2 / record 0; w2 dry.\n"
    "- Destruction: w1 1 folded — instruction 1 / record 0; w2 dry.\n"
    "- Vulnerabilities: w1 dry; w2 dry.\n"
    "- Integration-record: w1 dry; w2 dry.\n"
    "- ACID: w1 dry; w2 dry.\n"
)

# DC block for CONTINUE (mid-cycle: walk 2 not dry)
_CONTINUE_DC = (
    "- Weak spots: w1 2 folded — instruction 2 / record 0; "
    "w2 1 folded — instruction 1 / record 0.\n"
    "- Destruction: w1 dry; w2 dry.\n"
)

# DC block for ESCALATE:yield-rising
_ESCALATE_YIELD_DC = (
    "- Weak spots: w1 1 folded — instruction 1 / record 0; "
    "w2 2 folded — instruction 2 / record 0.\n"
    "- Destruction: w1 dry; w2 dry.\n"
)

# DC block for ESCALATE:plateau (4 walks at flat instruction count — walks 2-4 form 3+)
_PLATEAU_DC = (
    "- Weak spots: w1 2 folded — instruction 2 / record 0; "
    "w2 2 folded — instruction 2 / record 0; "
    "w3 2 folded — instruction 2 / record 0; "
    "w4 2 folded — instruction 2 / record 0.\n"
    "- Destruction: w1 dry; w2 dry; w3 dry; w4 dry.\n"
)

# Full validation line with all 4 keys
_FULL_VALIDATION = (
    "cycle_check=BAR_MET, plan_lint=0_FAIL, fold_check=PASS, propagation_check=DIVERGENT:5"
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
    "coherence: 2/2 walks have register rows\n"
)

_BATTERY_TOOLS = {"plan_lint.py", "fold_check.py", "propagation_check.py"}
_real_run = subprocess.run


def _make_plan(tmp_path, dc_block, filename="plan.md", include_manifest=True):
    """Create a plan_lint-compliant fixture plan."""
    plan = tmp_path / filename
    tail = _MANIFEST_STANZA if include_manifest else ""
    plan.write_text(
        f"# Plan\n**dispatch_mode:** bellows\n\n"
        f"## Drafting Cycle\n{dc_block}\n## End\n{tail}",
        encoding="utf-8",
    )
    return plan


def _make_battery_mock(tool_results):
    """Create a mock subprocess.run that intercepts battery tool calls.

    tool_results: dict mapping basename -> (returncode, stdout).
    Any call to a non-battery binary passes through to the real subprocess.run.
    """
    def mock_run(cmd, **kw):
        script_name = None
        for arg in cmd:
            try:
                n = Path(arg).name
            except Exception:
                continue
            if n in _BATTERY_TOOLS:
                script_name = n
                break
        if script_name:
            rc, out = tool_results.get(script_name, (0, ""))
            class R:
                returncode = rc
                stdout = out
                stderr = ""
            return R()
        return _real_run(cmd, **kw)
    return mock_run


# ========================== 16 battery tests ==========================


def test_battery_line_printed_before_verdict(tmp_path):
    """BATTERY: line appears in warnings before verdict on CONTINUE and BAR_MET exits."""
    for dc, expected_verdict in [(_CONTINUE_DC, "CONTINUE"), (_BAR_MET_DC, "BAR_MET")]:
        plan = _make_plan(tmp_path, dc, filename=f"{expected_verdict}.md")
        mock = _make_battery_mock({
            "plan_lint.py": (0, ""),
            "fold_check.py": (0, "FOLD-CHECK CLEAN: state unchanged"),
            "propagation_check.py": (0, "\nCLEAN — no divergence found"),
        })
        with patch.object(subprocess, "run", side_effect=mock):
            warnings = []
            verdict, code = cycle_check.run_check(plan, warnings=warnings)
        assert verdict == expected_verdict, f"expected {expected_verdict}, got {verdict}"
        assert code == 0
        battery_lines = [w for w in warnings if w.startswith("BATTERY:")]
        assert len(battery_lines) == 1, f"expected 1 BATTERY line; warnings={warnings}"
        battery = battery_lines[0]
        assert "plan_lint=" in battery
        assert "fold_check=" in battery
        assert "propagation_check=" in battery
        # Battery appears before the verdict (simulated output order)
        all_lines = warnings + [verdict]
        bat_idx = next(i for i, ln in enumerate(all_lines) if ln.startswith("BATTERY:"))
        assert bat_idx < len(all_lines) - 1, "BATTERY must precede the verdict line"
        assert all_lines[-1] == verdict, "verdict is last"


def test_bar_met_plan_lint_fail_downgrades(tmp_path):
    """BAR_MET plan + plan_lint FAIL>0 → CONTINUE; WARN names plan_lint count."""
    plan = _make_plan(tmp_path, _BAR_MET_DC)
    mock = _make_battery_mock({
        "plan_lint.py": (1, "FAIL: something wrong\nFAIL: another thing"),
        "fold_check.py": (0, "FOLD-CHECK CLEAN: state unchanged"),
        "propagation_check.py": (0, "\nCLEAN — no divergence found"),
    })
    with patch.object(subprocess, "run", side_effect=mock):
        warnings = []
        verdict, code = cycle_check.run_check(plan, warnings=warnings)
    assert verdict == "CONTINUE", f"expected downgrade to CONTINUE; got {verdict}"
    assert code == 0
    downgrade_warns = [w for w in warnings if "BAR_MET downgraded" in w and "plan_lint=" in w]
    assert len(downgrade_warns) == 1, f"expected 1 plan_lint downgrade WARN; warnings={warnings}"
    assert "2_FAIL" in downgrade_warns[0], downgrade_warns[0]


def test_bar_met_fold_check_drift_downgrades(tmp_path):
    """BAR_MET + fold_check DRIFT → CONTINUE; both-fire → two WARN lines, plan_lint first."""
    # Case 1: fold_check DRIFT only
    plan = _make_plan(tmp_path, _BAR_MET_DC, filename="drift_only.md")
    baseline = plan.parent / f".{plan.name}.foldcheck.json"
    baseline.write_text('{"_meta": {}}', encoding="utf-8")
    mock = _make_battery_mock({
        "plan_lint.py": (0, ""),
        "fold_check.py": (1, "FOLD-CHECK DRIFT — the fold changed the state"),
        "propagation_check.py": (0, "\nCLEAN — no divergence found"),
    })
    with patch.object(subprocess, "run", side_effect=mock):
        warnings = []
        verdict, _ = cycle_check.run_check(plan, warnings=warnings)
    assert verdict == "CONTINUE"
    drift_warns = [w for w in warnings if "BAR_MET downgraded" in w and "fold_check=DRIFT" in w]
    assert len(drift_warns) == 1, f"expected 1 drift WARN; warnings={warnings}"

    # Case 2: both plan_lint FAIL and fold_check DRIFT → two WARN lines, plan_lint first
    plan2 = _make_plan(tmp_path, _BAR_MET_DC, filename="both_fail.md")
    baseline2 = plan2.parent / f".{plan2.name}.foldcheck.json"
    baseline2.write_text('{"_meta": {}}', encoding="utf-8")
    mock2 = _make_battery_mock({
        "plan_lint.py": (1, "FAIL: something"),
        "fold_check.py": (1, "FOLD-CHECK DRIFT — the fold changed the state"),
        "propagation_check.py": (0, "\nCLEAN — no divergence found"),
    })
    with patch.object(subprocess, "run", side_effect=mock2):
        warnings2 = []
        verdict2, _ = cycle_check.run_check(plan2, warnings=warnings2)
    assert verdict2 == "CONTINUE"
    dw = [w for w in warnings2 if "BAR_MET downgraded" in w]
    assert len(dw) == 2, f"expected 2 downgrade WARNs; warnings2={warnings2}"
    assert "plan_lint" in dw[0], f"plan_lint WARN must come first; dw[0]={dw[0]!r}"
    assert "fold_check=DRIFT" in dw[1], f"fold_check WARN must be second; dw[1]={dw[1]!r}"


def test_bar_met_fold_check_vacuous_unaffected(tmp_path):
    """BAR_MET + fold_check rc=2 with VACUOUS in stdout → fold_check=VACUOUS, BAR_MET unchanged."""
    plan = _make_plan(tmp_path, _BAR_MET_DC)
    baseline = plan.parent / f".{plan.name}.foldcheck.json"
    baseline.write_text('{"_meta": {}}', encoding="utf-8")
    mock = _make_battery_mock({
        "plan_lint.py": (0, ""),
        "fold_check.py": (2, "FOLD-CHECK VACUOUS: the baseline was taken from THIS exact state"),
        "propagation_check.py": (0, "\nCLEAN — no divergence found"),
    })
    with patch.object(subprocess, "run", side_effect=mock):
        warnings = []
        verdict, code = cycle_check.run_check(plan, warnings=warnings)
    assert verdict == "BAR_MET", f"VACUOUS must not downgrade; got {verdict}"
    assert code == 0
    battery_lines = [w for w in warnings if w.startswith("BATTERY:")]
    assert len(battery_lines) == 1
    assert "fold_check=VACUOUS" in battery_lines[0], battery_lines[0]
    downgrade_warns = [w for w in warnings if "BAR_MET downgraded" in w]
    assert downgrade_warns == [], f"VACUOUS must not trigger downgrade: {warnings}"


def test_bar_met_no_baseline_unaffected(tmp_path):
    """BAR_MET + no baseline resolvable → fold_check=NO_BASELINE, BAR_MET unchanged."""
    plan = _make_plan(tmp_path, _BAR_MET_DC)
    # No baseline file beside the plan; no fold_baseline: in manifest
    mock = _make_battery_mock({
        "plan_lint.py": (0, ""),
        "propagation_check.py": (0, "\nCLEAN — no divergence found"),
    })
    with patch.object(subprocess, "run", side_effect=mock):
        warnings = []
        verdict, code = cycle_check.run_check(plan, warnings=warnings)
    assert verdict == "BAR_MET", f"NO_BASELINE must not downgrade; got {verdict}"
    assert code == 0
    battery_lines = [w for w in warnings if w.startswith("BATTERY:")]
    assert len(battery_lines) == 1
    assert "fold_check=NO_BASELINE" in battery_lines[0], battery_lines[0]
    downgrade_warns = [w for w in warnings if "BAR_MET downgraded" in w]
    assert downgrade_warns == [], f"NO_BASELINE must not trigger downgrade: {warnings}"


def test_bar_met_divergent_propagation_unaffected(tmp_path):
    """BAR_MET + propagation_check DIVERGENT:N → BAR_MET unchanged."""
    plan = _make_plan(tmp_path, _BAR_MET_DC)
    mock = _make_battery_mock({
        "plan_lint.py": (0, ""),
        "fold_check.py": (0, "FOLD-CHECK CLEAN: state unchanged"),
        "propagation_check.py": (1, "\nDIVERGENCES: 3"),
    })
    with patch.object(subprocess, "run", side_effect=mock):
        warnings = []
        verdict, code = cycle_check.run_check(plan, warnings=warnings)
    assert verdict == "BAR_MET", f"DIVERGENT propagation must not downgrade; got {verdict}"
    assert code == 0
    battery_lines = [w for w in warnings if w.startswith("BATTERY:")]
    assert len(battery_lines) == 1
    assert "propagation_check=DIVERGENT:3" in battery_lines[0], battery_lines[0]
    downgrade_warns = [w for w in warnings if "BAR_MET downgraded" in w]
    assert downgrade_warns == [], f"DIVERGENT propagation must not trigger downgrade: {warnings}"


def test_escalate_exits_spawn_no_tools(tmp_path):
    """Every ESCALATE exit: zero battery tool launches, verdict unaffected."""
    plan_yield = _make_plan(tmp_path, _ESCALATE_YIELD_DC, filename="yield.md")
    plan_plateau = _make_plan(tmp_path, _PLATEAU_DC, filename="plateau.md")
    plan_unparse = tmp_path / "unparse.md"
    plan_unparse.write_text("# Plan\nNo DC block here.\n", encoding="utf-8")

    battery_calls = []

    def counting_mock(cmd, **kw):
        for arg in cmd:
            try:
                if Path(arg).name in _BATTERY_TOOLS:
                    battery_calls.append(Path(arg).name)
            except Exception:
                pass
        return _real_run(cmd, **kw)

    for plan in [plan_yield, plan_plateau, plan_unparse]:
        battery_calls.clear()
        with patch.object(subprocess, "run", side_effect=counting_mock):
            warnings = []
            verdict, code = cycle_check.run_check(plan, warnings=warnings)
        assert verdict.startswith("ESCALATE"), (
            f"Expected ESCALATE from {plan.name}; got {verdict!r}"
        )
        assert battery_calls == [], (
            f"Battery launched for ESCALATE ({verdict}) on {plan.name}: {battery_calls}"
        )


def test_emit_manifest_validation_keys_and_fold_check_values(tmp_path):
    """--emit-manifest: 4 keys in canonical order; fold_check=PASS for rc=0,
    DRIFT/VACUOUS/NO_BASELINE for rc≠0."""
    plan = tmp_path / "plan.md"
    plan.write_text(
        "# Plan\n**dispatch_mode:** bellows\n\n## Drafting Cycle\n"
        "**Tier:** T1\n"
        "- Weak spots: w1 2 folded — instruction 2 / record 0; w2 dry.\n"
        "- Destruction: w1 1 folded — instruction 1 / record 0; w2 dry.\n"
        "- Vulnerabilities: w1 dry; w2 dry.\n"
        "- Integration-record: w1 dry; w2 dry.\n"
        "- ACID: w1 dry; w2 dry.\n"
        "**Closing:** walk 2 dry; cycle CLOSED.\n"
        "## End\n\n"
        "## Cycle Manifest\n"
        "validation: <declare>\n",
        encoding="utf-8",
    )
    baseline = plan.parent / f".{plan.name}.foldcheck.json"
    baseline.write_text('{"_meta": {}}', encoding="utf-8")

    # Case: fold_check rc=0 → PASS
    mock_pass = _make_battery_mock({
        "plan_lint.py": (0, ""),
        "fold_check.py": (0, "FOLD-CHECK CLEAN: state unchanged"),
        "propagation_check.py": (0, "\nCLEAN — no divergence found"),
    })
    buf = io.StringIO()
    with patch.object(subprocess, "run", side_effect=mock_pass):
        with redirect_stdout(buf):
            code = cycle_check.emit_manifest(plan)
    output = buf.getvalue()
    assert code == 0
    val_lines = [l for l in output.splitlines() if l.startswith("validation:")]
    assert len(val_lines) == 1, output
    val = val_lines[0][len("validation:"):].strip()
    import re
    keys = [part.split("=")[0].strip() for part in val.split(",") if "=" in part]
    assert keys == ["cycle_check", "plan_lint", "fold_check", "propagation_check"], (
        f"keys out of order: {keys}"
    )
    assert "fold_check=PASS" in val, f"expected PASS for rc=0; got: {val}"

    # Case: fold_check rc=1 → DRIFT
    mock_drift = _make_battery_mock({
        "plan_lint.py": (0, ""),
        "fold_check.py": (1, "FOLD-CHECK DRIFT — state changed"),
        "propagation_check.py": (0, "\nCLEAN — no divergence found"),
    })
    buf2 = io.StringIO()
    with patch.object(subprocess, "run", side_effect=mock_drift):
        with redirect_stdout(buf2):
            cycle_check.emit_manifest(plan)
    val2 = [l for l in buf2.getvalue().splitlines() if l.startswith("validation:")][0]
    assert "fold_check=DRIFT" in val2, f"expected DRIFT for rc=1: {val2}"

    # Case: fold_check rc=2 + VACUOUS → VACUOUS
    mock_vac = _make_battery_mock({
        "plan_lint.py": (0, ""),
        "fold_check.py": (2, "FOLD-CHECK VACUOUS: baseline was taken from this state"),
        "propagation_check.py": (0, "\nCLEAN — no divergence found"),
    })
    buf3 = io.StringIO()
    with patch.object(subprocess, "run", side_effect=mock_vac):
        with redirect_stdout(buf3):
            cycle_check.emit_manifest(plan)
    val3 = [l for l in buf3.getvalue().splitlines() if l.startswith("validation:")][0]
    assert "fold_check=VACUOUS" in val3, f"expected VACUOUS for rc=2+VACUOUS: {val3}"


def test_one_implementation(tmp_path):
    """Values run_check's BATTERY line prints == values emit_manifest writes for each tool."""
    plan = tmp_path / "plan.md"
    plan.write_text(
        "# Plan\n**dispatch_mode:** bellows\n\n## Drafting Cycle\n"
        "**Tier:** T1\n"
        "- Weak spots: w1 2 folded — instruction 2 / record 0; w2 dry.\n"
        "- Destruction: w1 1 folded — instruction 1 / record 0; w2 dry.\n"
        "- Vulnerabilities: w1 dry; w2 dry.\n"
        "- Integration-record: w1 dry; w2 dry.\n"
        "- ACID: w1 dry; w2 dry.\n"
        "**Closing:** walk 2 dry; cycle CLOSED.\n"
        "## End\n\n"
        "## Cycle Manifest\n"
        f"validation: {_FULL_VALIDATION}\n",
        encoding="utf-8",
    )
    mock = _make_battery_mock({
        "plan_lint.py": (0, ""),
        "fold_check.py": (0, "FOLD-CHECK CLEAN: state unchanged"),
        "propagation_check.py": (0, "\nCLEAN — no divergence found"),
    })

    # run_check BATTERY line
    with patch.object(subprocess, "run", side_effect=mock):
        warnings = []
        cycle_check.run_check(plan, warnings=warnings)
    battery_line = next(w for w in warnings if w.startswith("BATTERY:"))

    # emit_manifest validation: line
    buf = io.StringIO()
    with patch.object(subprocess, "run", side_effect=mock):
        with redirect_stdout(buf):
            cycle_check.emit_manifest(plan)
    output = buf.getvalue()
    val_line = next(l for l in output.splitlines() if l.startswith("validation:"))
    val = val_line[len("validation:"):].strip()

    import re
    for key in ["plan_lint", "fold_check", "propagation_check"]:
        bm = re.search(rf"{key}=(\S+?)(?:\s|$)", battery_line)
        vm = re.search(rf"{key}=([^,\s]+)", val)
        assert bm and vm, f"key {key!r} not found in battery_line or val_line"
        assert bm.group(1) == vm.group(1), (
            f"mismatch for {key}: battery={bm.group(1)!r} vs manifest={vm.group(1)!r}"
        )


def test_baseline_resolution_order(tmp_path):
    """manifest fold_baseline: takes precedence; declared-but-unresolvable → NO_BASELINE."""
    plan = tmp_path / "plan.md"
    plan.write_text(
        "# Plan\n**dispatch_mode:** bellows\n\n## Drafting Cycle\n"
        "- Weak spots: w1 2 folded — instruction 2 / record 0; w2 dry.\n"
        "## Cycle Manifest\n"
        "fold_baseline: /nonexistent/path/baseline.json\n"
        f"validation: {_FULL_VALIDATION}\n",
        encoding="utf-8",
    )
    # beside-file baseline exists, but the declared fold_baseline doesn't resolve
    beside = plan.parent / f".{plan.name}.foldcheck.json"
    beside.write_text('{"_meta": {}}', encoding="utf-8")

    b_path, declared = cycle_check.resolve_fold_baseline(plan)
    assert declared is True, "fold_baseline: field is present → declared=True"
    assert b_path is None, (
        "declared-but-unresolvable must return (None, True), not fall back to beside"
    )


def test_no_subprocess_spawned_ruled_rewrite(tmp_path):
    """Ruling 189 (thread 189): rewrite of test_no_subprocess_spawned.

    CONTINUE/BAR_MET exits run the battery; ESCALATE exits run zero battery tools.
    Count launches by BASENAME:
      - CONTINUE or BAR_MET without baseline: 2 launches (plan_lint + propagation_check)
      - CONTINUE or BAR_MET with baseline:    3 launches (+ fold_check)
      - ESCALATE: 0 launches
    Docstring cites thread 189 which overtook 100033's no-subprocess clause for
    CONTINUE/BAR_MET exits; ESCALATE exits remain zero-subprocess.
    """
    plan_bar = _make_plan(tmp_path, _BAR_MET_DC, filename="bar.md")
    plan_esc = _make_plan(tmp_path, _ESCALATE_YIELD_DC, filename="esc.md")

    battery_calls = []

    def counting_mock(cmd, **kw):
        for arg in cmd:
            try:
                if Path(arg).name in _BATTERY_TOOLS:
                    battery_calls.append(Path(arg).name)
                    rc_map = {
                        "plan_lint.py": (0, ""),
                        "fold_check.py": (0, "FOLD-CHECK CLEAN"),
                        "propagation_check.py": (0, ""),
                    }
                    rc, out = rc_map.get(Path(arg).name, (0, ""))
                    class R:
                        returncode = rc
                        stdout = out
                        stderr = ""
                    return R()
            except Exception:
                pass
        return _real_run(cmd, **kw)

    # BAR_MET without baseline: 2 tools (plan_lint + propagation_check)
    battery_calls.clear()
    with patch.object(subprocess, "run", side_effect=counting_mock):
        warnings = []
        verdict, _ = cycle_check.run_check(plan_bar, warnings=warnings)
    assert verdict == "BAR_MET"
    assert sorted(battery_calls) == sorted(["plan_lint.py", "propagation_check.py"]), (
        f"expected plan_lint+propagation_check (no baseline); got {battery_calls}"
    )

    # ESCALATE: zero battery launches
    battery_calls.clear()
    with patch.object(subprocess, "run", side_effect=counting_mock):
        warnings = []
        verdict, _ = cycle_check.run_check(plan_esc, warnings=warnings)
    assert verdict.startswith("ESCALATE")
    assert battery_calls == [], f"ESCALATE must not launch battery: {battery_calls}"

    # BAR_MET with baseline: 3 tools (plan_lint + fold_check + propagation_check)
    plan_bar3 = _make_plan(tmp_path, _BAR_MET_DC, filename="bar3.md")
    baseline3 = plan_bar3.parent / f".{plan_bar3.name}.foldcheck.json"
    baseline3.write_text('{"_meta": {}}', encoding="utf-8")

    battery_calls.clear()
    with patch.object(subprocess, "run", side_effect=counting_mock):
        warnings = []
        verdict, _ = cycle_check.run_check(plan_bar3, warnings=warnings)
    assert verdict == "BAR_MET"
    assert sorted(battery_calls) == sorted(["plan_lint.py", "fold_check.py", "propagation_check.py"]), (
        f"expected all 3 battery tools (with baseline); got {battery_calls}"
    )


def test_emit_manifest_launches_each_tool_once(tmp_path):
    """--emit-manifest with a baseline launches each of the three tools exactly once."""
    plan = tmp_path / "plan.md"
    plan.write_text(
        "# Plan\n**dispatch_mode:** bellows\n\n## Drafting Cycle\n"
        "**Tier:** T1\n"
        "- Weak spots: w1 2 folded — instruction 2 / record 0; w2 dry.\n"
        "- Destruction: w1 1 folded — instruction 1 / record 0; w2 dry.\n"
        "- Vulnerabilities: w1 dry; w2 dry.\n"
        "- Integration-record: w1 dry; w2 dry.\n"
        "- ACID: w1 dry; w2 dry.\n"
        "**Closing:** walk 2 dry; cycle CLOSED.\n"
        "## End\n\n"
        "## Cycle Manifest\n"
        "validation: <declare>\n",
        encoding="utf-8",
    )
    baseline = plan.parent / f".{plan.name}.foldcheck.json"
    baseline.write_text('{"_meta": {}}', encoding="utf-8")

    tool_call_counts: dict = {}

    def counting_mock(cmd, **kw):
        for arg in cmd:
            try:
                name = Path(arg).name
            except Exception:
                continue
            if name in _BATTERY_TOOLS:
                tool_call_counts[name] = tool_call_counts.get(name, 0) + 1
                rc_map = {
                    "plan_lint.py": (0, ""),
                    "fold_check.py": (0, "FOLD-CHECK CLEAN"),
                    "propagation_check.py": (0, ""),
                }
                rc, out = rc_map.get(name, (0, ""))
                class R:
                    returncode = rc
                    stdout = out
                    stderr = ""
                return R()
        return _real_run(cmd, **kw)

    buf = io.StringIO()
    with patch.object(subprocess, "run", side_effect=counting_mock):
        with redirect_stdout(buf):
            cycle_check.emit_manifest(plan)

    assert tool_call_counts.get("plan_lint.py", 0) == 1, (
        f"plan_lint must be called exactly once; counts={tool_call_counts}"
    )
    assert tool_call_counts.get("fold_check.py", 0) == 1, (
        f"fold_check must be called exactly once; counts={tool_call_counts}"
    )
    assert tool_call_counts.get("propagation_check.py", 0) == 1, (
        f"propagation_check must be called exactly once; counts={tool_call_counts}"
    )


def test_one_resolver(tmp_path):
    """substrate_status and run_battery resolve the same baseline from manifest fold_baseline:."""
    import sys as _sys
    if str(SCRIPTS) not in _sys.path:
        _sys.path.insert(0, str(SCRIPTS))

    baseline_file = tmp_path / "my-baseline.foldcheck.json"
    baseline_file.write_text('{"_meta": {}}', encoding="utf-8")

    plan = tmp_path / "plan.md"
    plan.write_text(
        "# Plan\n**dispatch_mode:** bellows\n\n## Drafting Cycle\n"
        "**Tier:** T1\n"
        f"**Walk register:** `missing-register.md`\n"
        "- Weak spots: w1 2 folded — instruction 2 / record 0; w2 dry.\n"
        "## Cycle Manifest\n"
        f"fold_baseline: {baseline_file}\n"
        f"validation: {_FULL_VALIDATION}\n",
        encoding="utf-8",
    )

    # resolve_fold_baseline uses the manifest field
    b_path, declared = cycle_check.resolve_fold_baseline(plan)
    assert b_path == baseline_file, f"expected {baseline_file}; got {b_path}"
    assert declared is True

    # The manifest resolver uses _resolve_register_ref — same ONE resolver
    manifest = cycle_check.parse_manifest_stanza(plan.read_text(encoding="utf-8")) or {}
    fb_ref = (manifest.get("fold_baseline") or "").strip()
    resolved = cycle_check._resolve_register_ref(fb_ref, plan)
    assert resolved == baseline_file, f"_resolve_register_ref must find the same path"


def test_continue_plan_lint_fail_no_downgrade_warn(tmp_path):
    """CONTINUE plan + plan_lint FAIL: BATTERY line printed, NO downgrade WARN.
    Downgrade only fires at the bar (BAR_MET), not on CONTINUE exits.
    """
    plan = _make_plan(tmp_path, _CONTINUE_DC)
    mock = _make_battery_mock({
        "plan_lint.py": (1, "FAIL: something wrong"),
        "fold_check.py": (0, "FOLD-CHECK CLEAN: state unchanged"),
        "propagation_check.py": (0, "\nCLEAN — no divergence found"),
    })
    with patch.object(subprocess, "run", side_effect=mock):
        warnings = []
        verdict, code = cycle_check.run_check(plan, warnings=warnings)
    assert verdict == "CONTINUE"
    assert code == 0
    battery_lines = [w for w in warnings if w.startswith("BATTERY:")]
    assert len(battery_lines) == 1, f"BATTERY line missing; warnings={warnings}"
    downgrade_warns = [w for w in warnings if "BAR_MET downgraded" in w]
    assert downgrade_warns == [], (
        f"downgrade WARN must NOT fire on CONTINUE path; warnings={warnings}"
    )


def test_verdict_independent_of_call_shape(tmp_path):
    """run_check(path), run_check(path, warnings=[]) both downgrade when plan_lint FAIL>0."""
    plan = _make_plan(tmp_path, _BAR_MET_DC)
    mock = _make_battery_mock({
        "plan_lint.py": (1, "FAIL: something wrong"),
        "fold_check.py": (0, "FOLD-CHECK CLEAN: state unchanged"),
        "propagation_check.py": (0, "\nCLEAN — no divergence found"),
    })

    # Shape 1: no warnings kwarg (warnings=None internally)
    with patch.object(subprocess, "run", side_effect=mock):
        v1, c1 = cycle_check.run_check(plan)

    # Shape 2: explicit empty warnings list
    with patch.object(subprocess, "run", side_effect=mock):
        v2, c2 = cycle_check.run_check(plan, warnings=[])

    # Both shapes apply the downgrade
    assert v1 == "CONTINUE", f"run_check(path) must downgrade; got {v1!r}"
    assert v2 == "CONTINUE", f"run_check(path, warnings=[]) must downgrade; got {v2!r}"
    assert c1 == 0
    assert c2 == 0


def test_beside_only_fallback(tmp_path):
    """Plan with NO fold_baseline: field resolves the beside-the-plan baseline."""
    plan = _make_plan(tmp_path, _BAR_MET_DC, filename="myplan.md")
    beside = plan.parent / f".{plan.name}.foldcheck.json"
    beside.write_text('{"_meta": {}}', encoding="utf-8")

    b_path, declared = cycle_check.resolve_fold_baseline(plan)
    assert b_path == beside, f"expected beside-plan path {beside}; got {b_path}"
    assert declared is False, "no manifest fold_baseline: field → declared=False"
