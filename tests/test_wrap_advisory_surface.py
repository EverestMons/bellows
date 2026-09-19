"""Tests for wrap-hook advisory surfacing (plan 100129, thread 427)."""
from __future__ import annotations

import ast
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import types
import uuid
from pathlib import Path

import pytest

HOOKS_DIR = Path(__file__).resolve().parent.parent / "hooks" / "eluvian"
HARNESS_PY = "/usr/bin/python3"

_CRASH_LINE = "wrap_check: internal error, failing open (allowing): boom"

# Case 2 / 5 stub output: two OK lines interleaved with two non-OK lines
_CASE2_OUTPUT = (
    "[2r/receipts] OK — no deposits in this session (session x).\n"
    "[3/root] WARN (advisory): anvil — published tip unreadable; gitlink not judged.\n"
    "[2r/receipts] WARNING: malformed receipt file r.json — skipped (not a failure).\n"
    "wrap_check: OK — all four repos wrapped.\n"
)
_CASE2_NON_OK = [
    "[3/root] WARN (advisory): anvil — published tip unreadable; gitlink not judged.",
    "[2r/receipts] WARNING: malformed receipt file r.json — skipped (not a failure).",
]

# Case 3 / 6 stub output: only OK lines plus the P6 short form
_CLEAN_PASS_OUTPUT = (
    "[2r/receipts] OK — no deposits in this session (session x).\n"
    "wrap_check: OK — all four repos wrapped.\n"
    "wrap_check: OK\n"
)

# Case 4 stub output
_DEBT_FAIL_BLOCK = (
    "SESSION WRAP INCOMPLETE — the following steps are not verifiably done:\n\n"
    "  ✗ [3/root] 2 commit(s) not pushed — push governance root.\n"
    "\nComplete these, then this lock clears automatically.\n"
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_hook_dir(base: Path, stub_output: str, stub_exit: int) -> Path:
    """Copy the three hook files beside a configurable stub checker.

    Asserts every copied file's source is under the expected hooks tree first.
    """
    d = base / "hooks"
    d.mkdir(parents=True, exist_ok=True)
    expected_tree = str(HOOKS_DIR.resolve())
    for name in ("wrap_debt_hook.py", "wrap_stop_hook.py", "_common.py"):
        src = HOOKS_DIR / name
        assert str(src.resolve()).startswith(expected_tree + os.sep), (
            f"source {src} not under expected tree {expected_tree}"
        )
        shutil.copy2(src, d / name)
    _write_stub(d, stub_output, stub_exit)
    return d


def _write_stub(d: Path, output: str, exit_code: int) -> None:
    """Write a stub wrap_check.py into d."""
    (d / "wrap_check.py").write_text(
        f"import sys\nsys.stdout.write({output!r})\nsys.exit({exit_code})\n"
    )


def _run_hook_script(
    hook_dir: Path,
    script: str,
    payload: dict,
    root: Path,
    hooks_log: Path,
    tuyere: Path,
    interpreter: str = None,
) -> subprocess.CompletedProcess:
    """Run a hook script from hook_dir with an isolated environment."""
    interp = interpreter or sys.executable
    env = {**os.environ}
    env["ELUVIAN_WRAP_ROOT"] = str(root)
    env["ELUVIAN_HOOKS_LOG"] = str(hooks_log)
    env["ELUVIAN_WRAP_TUYERE"] = str(tuyere)
    env.pop("BELLOWS_DISPATCH", None)
    return subprocess.run(
        [interp, str(hook_dir / script)],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        timeout=60,
        env=env,
    )


def _load_module_from_path(path: Path, name: str = None):
    """Load a Python module from a file path."""
    mod_name = name or ("_test_" + path.stem + "_" + str(uuid.uuid4())[:8])
    spec = importlib.util.spec_from_file_location(mod_name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _extract_leading_literal(node: ast.expr) -> str:
    """Extract the leading literal string from a print call's first argument.

    Constant → its value; JoinedStr → text before first placeholder;
    BinOp → left operand recursively. Any other form raises AssertionError.
    """
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    elif isinstance(node, ast.JoinedStr):
        text = ""
        for val in node.values:
            if isinstance(val, ast.Constant) and isinstance(val.value, str):
                text += val.value
            else:
                break
        return text
    elif isinstance(node, ast.BinOp):
        return _extract_leading_literal(node.left)
    else:
        raise AssertionError(
            f"Unclassified print argument AST form: {ast.dump(node)!r}"
        )


# ---------------------------------------------------------------------------
# Cases
# ---------------------------------------------------------------------------

def test_selector_drops_exactly_the_ok_lines(tmp_path):
    """H. The selector is a deny-list of exactly the OK status lines, derived from source."""
    hook_dir = _make_hook_dir(tmp_path, "", 0)
    common_path = hook_dir / "_common.py"
    common = _load_module_from_path(common_path)
    assert str(Path(common.__file__).resolve()).startswith(str(hook_dir.resolve())), (
        f"_common.__file__ {common.__file__!r} not under hook_dir {hook_dir}"
    )

    wrap_check_src = (HOOKS_DIR / "wrap_check.py").read_text()
    tree = ast.parse(wrap_check_src)

    dropped, placeholder, kept = [], [], []
    for node in ast.walk(tree):
        if (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id == "print"
            and node.args
        ):
            leading = _extract_leading_literal(node.args[0])
            if not leading.strip():
                placeholder.append(leading)
            elif common.advisory_lines(leading):
                kept.append(leading)
            else:
                dropped.append(leading)

    # Dropped: exactly the three OK-prefix sites — pinned by text
    assert set(dropped) == {
        "[2r/receipts] OK — ",
        "[2r/receipts] OK — no deposits in this session (session ",
        "wrap_check: OK — all four repos wrapped.",
    }
    # Placeholder: exactly :498 — pinned by text
    assert set(placeholder) == {"  "}
    # Kept: positive controls — the sites this plan exists for
    assert any("[3/root] WARN (advisory)" in l for l in kept)
    assert any("[4/memory] WARN (advisory)" in l for l in kept)
    assert any("wrap_check: internal error, failing open (allowing):" in l for l in kept)
    # P6: short fake form is dropped
    assert common.advisory_lines("wrap_check: OK") == []
    # Crash line is kept
    assert common.advisory_lines(_CRASH_LINE)


def test_debt_hook_surfaces_advisories_on_pass(tmp_path):
    """A. A passing check's non-OK lines reach the session's context."""
    hook_dir = _make_hook_dir(tmp_path, _CASE2_OUTPUT, 0)
    root = tmp_path / "root"
    root.mkdir()
    hooks_log = tmp_path / "hooks.log"
    sid = "sid2-" + str(uuid.uuid4())[:8]

    result = _run_hook_script(
        hook_dir, "wrap_debt_hook.py", {"session_id": sid},
        root, hooks_log, tmp_path / "no-tuyere",
    )
    out = json.loads(result.stdout)
    hso = out["hookSpecificOutput"]
    assert hso["hookEventName"] == "SessionStart"
    ctx = hso["additionalContext"]

    # Both non-OK lines present, in order
    assert ctx.index(_CASE2_NON_OK[0]) < ctx.index(_CASE2_NON_OK[1])
    # Neither OK line present
    assert "[2r/receipts] OK — " not in ctx
    assert "wrap_check: OK — " not in ctx
    # Ordinary header: no "debt", "/wrap", or "nothing is owed"
    header = ctx[: ctx.index(_CASE2_NON_OK[0])]
    assert "debt" not in header.lower()
    assert "/wrap" not in header.lower()
    assert "nothing is owed" not in header.lower()
    # Exactly one log line: clean sid=<sid>
    log_lines = [l for l in hooks_log.read_text().splitlines() if l.strip()]
    assert len(log_lines) == 1
    assert f"clean sid={sid}" in log_lines[0]


def test_debt_hook_clean_pass_emits_nothing(tmp_path):
    """C. A passing check that printed only OK lines — debt hook emits {}."""
    hook_dir = _make_hook_dir(tmp_path, _CLEAN_PASS_OUTPUT, 0)
    root = tmp_path / "root"
    root.mkdir()
    hooks_log = tmp_path / "hooks.log"
    sid = "sid3-" + str(uuid.uuid4())[:8]

    result = _run_hook_script(
        hook_dir, "wrap_debt_hook.py", {"session_id": sid},
        root, hooks_log, tmp_path / "no-tuyere",
    )
    assert json.loads(result.stdout) == {}
    # Positive control: log has exactly one clean line
    log_lines = [l for l in hooks_log.read_text().splitlines() if l.strip()]
    assert len(log_lines) == 1
    assert f"clean sid={sid}" in log_lines[0]


def test_debt_hook_debt_path_unchanged(tmp_path):
    """D. The debt path is unchanged: additionalContext == _compose_debt_message(stdout)."""
    hook_dir = _make_hook_dir(tmp_path, _DEBT_FAIL_BLOCK, 1)
    root = tmp_path / "root"
    root.mkdir()
    hooks_log = tmp_path / "hooks.log"
    sid = "sid4-" + str(uuid.uuid4())[:8]

    result = _run_hook_script(
        hook_dir, "wrap_debt_hook.py", {"session_id": sid},
        root, hooks_log, tmp_path / "no-tuyere",
    )
    ctx = json.loads(result.stdout)["hookSpecificOutput"]["additionalContext"]

    # Load _compose_debt_message from the hook's own module by path
    debt_mod = _load_module_from_path(hook_dir / "wrap_debt_hook.py")
    expected = debt_mod._compose_debt_message(_DEBT_FAIL_BLOCK.strip())
    assert ctx == expected
    # Referent independent of that function: starts with today's debt header
    assert ctx.startswith("⚠️ UNWRAPPED SESSION DEBT DETECTED.")


def test_stop_hook_armed_pass_shows_message_and_disarms(tmp_path):
    """B. Armed pass: stop hook emits systemMessage with non-OK lines and disarms."""
    hook_dir = _make_hook_dir(tmp_path, _CASE2_OUTPUT, 0)
    root = tmp_path / "root"
    root.mkdir()
    hooks_log = tmp_path / "hooks.log"
    sid = "sid5-" + str(uuid.uuid4())[:8]
    sentinel = root / f".wrap-in-progress-{sid}"
    sentinel.touch()
    assert sentinel.exists()

    result = _run_hook_script(
        hook_dir, "wrap_stop_hook.py", {"session_id": sid},
        root, hooks_log, tmp_path / "no-tuyere",
    )
    out = json.loads(result.stdout)
    # Exactly {"systemMessage"} — no decision, no hookSpecificOutput
    assert set(out.keys()) == {"systemMessage"}
    msg = out["systemMessage"]
    # Both non-OK lines present, neither OK line
    assert _CASE2_NON_OK[0] in msg
    assert _CASE2_NON_OK[1] in msg
    assert "[2r/receipts] OK — " not in msg
    assert "wrap_check: OK — " not in msg
    # Sentinel removed
    assert not sentinel.exists()
    # Exactly one log line: armed-pass-disarm
    log_lines = [l for l in hooks_log.read_text().splitlines() if l.strip()]
    assert len(log_lines) == 1
    assert f"armed-pass-disarm sid={sid}" in log_lines[0]


def test_stop_hook_armed_clean_pass_unchanged(tmp_path):
    """C. Armed clean pass: stop hook emits {}, disarms."""
    hook_dir = _make_hook_dir(tmp_path, _CLEAN_PASS_OUTPUT, 0)
    root = tmp_path / "root"
    root.mkdir()
    hooks_log = tmp_path / "hooks.log"
    sid = "sid6-" + str(uuid.uuid4())[:8]
    sentinel = root / f".wrap-in-progress-{sid}"
    sentinel.touch()
    assert sentinel.exists()

    result = _run_hook_script(
        hook_dir, "wrap_stop_hook.py", {"session_id": sid},
        root, hooks_log, tmp_path / "no-tuyere",
    )
    assert json.loads(result.stdout) == {}
    assert not sentinel.exists()
    log_lines = [l for l in hooks_log.read_text().splitlines() if l.strip()]
    assert len(log_lines) == 1
    assert f"armed-pass-disarm sid={sid}" in log_lines[0]


def test_stop_hook_block_path_unchanged(tmp_path):
    """E. Armed fail: stop hook blocks with the checker's output."""
    fail_output = (
        "SESSION WRAP INCOMPLETE — steps missing.\n"
        "  ✗ [3/root] push\n"
        "\nComplete these.\n"
    )
    hook_dir = _make_hook_dir(tmp_path, fail_output, 1)
    root = tmp_path / "root"
    root.mkdir()
    hooks_log = tmp_path / "hooks.log"
    sid = "sid7-" + str(uuid.uuid4())[:8]
    (root / f".wrap-in-progress-{sid}").touch()

    result = _run_hook_script(
        hook_dir, "wrap_stop_hook.py", {"session_id": sid},
        root, hooks_log, tmp_path / "no-tuyere",
    )
    out = json.loads(result.stdout)
    assert out.get("decision") == "block"
    assert fail_output.strip() in out.get("reason", "")


def test_stop_hook_unarmed_never_runs_checker(tmp_path):
    """F. Unarmed stop hook never runs the checker; positive control shows the stub fires when armed."""
    marker = tmp_path / "checker-ran"
    hook_dir = _make_hook_dir(tmp_path, "", 0)
    (hook_dir / "wrap_check.py").write_text(
        f"import sys\n"
        f"open({str(marker)!r}, 'w').write('ran')\n"
        f"sys.stdout.write('WARN (advisory): marker written\\n')\n"
        f"sys.exit(0)\n"
    )
    root = tmp_path / "root"
    root.mkdir()
    hooks_log = tmp_path / "hooks.log"
    sid = "sid8-" + str(uuid.uuid4())[:8]

    # Unarmed: no sentinel — checker must NOT run
    result = _run_hook_script(
        hook_dir, "wrap_stop_hook.py", {"session_id": sid},
        root, hooks_log, tmp_path / "no-tuyere",
    )
    assert json.loads(result.stdout) == {}
    assert not marker.exists()

    # Positive control: arm sentinel — checker MUST run
    (root / f".wrap-in-progress-{sid}").touch()
    _run_hook_script(
        hook_dir, "wrap_stop_hook.py", {"session_id": sid},
        root, hooks_log, tmp_path / "no-tuyere",
    )
    assert marker.exists()


def test_crash_line_is_surfaced_by_both_hooks(tmp_path):
    """H. The crash line is surfaced under the UNVERIFIED header; case-2 output uses the ordinary header."""
    hook_dir = _make_hook_dir(tmp_path, _CRASH_LINE + "\n", 0)
    root = tmp_path / "root"
    root.mkdir()
    hooks_log = tmp_path / "hooks.log"
    sid = "sid9-" + str(uuid.uuid4())[:8]

    # Load _common.py from the tree under test; assert __file__ is under that tree (J)
    common_path = hook_dir / "_common.py"
    common = _load_module_from_path(common_path)
    assert str(Path(common.__file__).resolve()).startswith(str(hook_dir.resolve())), (
        f"_common.__file__ {common.__file__!r} not under hook_dir {hook_dir}"
    )

    # Derive both headers from compose_advisory_message (same run, same loaded module)
    crash_full = common.compose_advisory_message([_CRASH_LINE])
    _probe_line = "[4/memory] WARN (advisory): test-probe-line"
    ordinary_full = common.compose_advisory_message([_probe_line])
    unverified_header = crash_full[: crash_full.index(_CRASH_LINE)]
    ordinary_header = ordinary_full[: ordinary_full.index(_probe_line)]

    assert unverified_header != ordinary_header
    assert "debt" not in unverified_header.lower()
    assert "/wrap" not in unverified_header.lower()

    # Debt hook (crash stub): context carries crash line under UNVERIFIED header
    debt_result = _run_hook_script(
        hook_dir, "wrap_debt_hook.py", {"session_id": sid},
        root, hooks_log, tmp_path / "no-tuyere",
    )
    ctx_debt = json.loads(debt_result.stdout)["hookSpecificOutput"]["additionalContext"]
    assert _CRASH_LINE in ctx_debt
    assert unverified_header.strip() in ctx_debt
    assert ordinary_header.strip() not in ctx_debt

    # Stop hook (armed, crash stub): message carries crash line under UNVERIFIED header
    hooks_log.unlink(missing_ok=True)
    sentinel = root / f".wrap-in-progress-{sid}"
    sentinel.touch()
    stop_result = _run_hook_script(
        hook_dir, "wrap_stop_hook.py", {"session_id": sid},
        root, hooks_log, tmp_path / "no-tuyere",
    )
    msg_stop = json.loads(stop_result.stdout)["systemMessage"]
    assert _CRASH_LINE in msg_stop
    assert unverified_header.strip() in msg_stop
    assert ordinary_header.strip() not in msg_stop

    # Contrast: case 2's debt hook output carries the ordinary header, not the UNVERIFIED one
    hooks_log.unlink(missing_ok=True)
    _write_stub(hook_dir, _CASE2_OUTPUT, 0)
    sid2 = "sid9b-" + str(uuid.uuid4())[:8]
    debt2 = _run_hook_script(
        hook_dir, "wrap_debt_hook.py", {"session_id": sid2},
        root, hooks_log, tmp_path / "no-tuyere",
    )
    ctx2 = json.loads(debt2.stdout)["hookSpecificOutput"]["additionalContext"]
    assert ordinary_header.strip() in ctx2
    assert unverified_header.strip() not in ctx2

    # Contrast: case 2's stop hook output carries the ordinary header, not the UNVERIFIED one
    hooks_log.unlink(missing_ok=True)
    root2 = tmp_path / "root2"
    root2.mkdir()
    sentinel2 = root2 / f".wrap-in-progress-{sid2}"
    sentinel2.touch()
    stop2 = _run_hook_script(
        hook_dir, "wrap_stop_hook.py", {"session_id": sid2},
        root2, tmp_path / "hooks2.log", tmp_path / "no-tuyere",
    )
    msg2 = json.loads(stop2.stdout)["systemMessage"]
    assert ordinary_header.strip() in msg2
    assert unverified_header.strip() not in msg2


def test_hooks_surface_under_harness_interpreter(tmp_path):
    """I. Cases 2, 3, 5, 6, 9 under /usr/bin/python3 (harness interpreter)."""
    if not Path(HARNESS_PY).exists():
        pytest.skip(f"{HARNESS_PY} absent on this machine")

    tuyere = tmp_path / "no-tuyere"
    sid = "sid10-" + str(uuid.uuid4())[:8]

    # Case 2: ordinary advisory pass — debt hook
    hd2 = _make_hook_dir(tmp_path / "c2", _CASE2_OUTPUT, 0)
    root2 = tmp_path / "root2"
    root2.mkdir()
    r2 = _run_hook_script(hd2, "wrap_debt_hook.py", {"session_id": sid},
                          root2, tmp_path / "log2.log", tuyere, interpreter=HARNESS_PY)
    out2 = json.loads(r2.stdout)
    assert out2["hookSpecificOutput"]["hookEventName"] == "SessionStart"
    ctx2 = out2["hookSpecificOutput"]["additionalContext"]
    assert _CASE2_NON_OK[0] in ctx2
    assert _CASE2_NON_OK[1] in ctx2

    # Case 3: clean pass — debt hook emits {}
    hd3 = _make_hook_dir(tmp_path / "c3", _CLEAN_PASS_OUTPUT, 0)
    root3 = tmp_path / "root3"
    root3.mkdir()
    r3 = _run_hook_script(hd3, "wrap_debt_hook.py", {"session_id": sid},
                          root3, tmp_path / "log3.log", tuyere, interpreter=HARNESS_PY)
    assert json.loads(r3.stdout) == {}

    # Case 5: ordinary advisory pass — stop hook (armed)
    hd5 = _make_hook_dir(tmp_path / "c5", _CASE2_OUTPUT, 0)
    root5 = tmp_path / "root5"
    root5.mkdir()
    sentinel5 = root5 / f".wrap-in-progress-{sid}"
    sentinel5.touch()
    r5 = _run_hook_script(hd5, "wrap_stop_hook.py", {"session_id": sid},
                          root5, tmp_path / "log5.log", tuyere, interpreter=HARNESS_PY)
    out5 = json.loads(r5.stdout)
    assert set(out5.keys()) == {"systemMessage"}
    assert _CASE2_NON_OK[0] in out5["systemMessage"]
    assert not sentinel5.exists()

    # Case 6: clean pass — stop hook (armed) emits {}
    hd6 = _make_hook_dir(tmp_path / "c6", _CLEAN_PASS_OUTPUT, 0)
    root6 = tmp_path / "root6"
    root6.mkdir()
    sentinel6 = root6 / f".wrap-in-progress-{sid}"
    sentinel6.touch()
    r6 = _run_hook_script(hd6, "wrap_stop_hook.py", {"session_id": sid},
                          root6, tmp_path / "log6.log", tuyere, interpreter=HARNESS_PY)
    assert json.loads(r6.stdout) == {}
    assert not sentinel6.exists()

    # Case 9: crash line surfaced by both hooks
    hd9 = _make_hook_dir(tmp_path / "c9", _CRASH_LINE + "\n", 0)
    root9 = tmp_path / "root9"
    root9.mkdir()
    r9d = _run_hook_script(hd9, "wrap_debt_hook.py", {"session_id": sid},
                           root9, tmp_path / "log9d.log", tuyere, interpreter=HARNESS_PY)
    ctx9 = json.loads(r9d.stdout)["hookSpecificOutput"]["additionalContext"]
    assert _CRASH_LINE in ctx9

    sentinel9 = root9 / f".wrap-in-progress-{sid}"
    sentinel9.touch()
    r9s = _run_hook_script(hd9, "wrap_stop_hook.py", {"session_id": sid},
                           root9, tmp_path / "log9s.log", tuyere, interpreter=HARNESS_PY)
    msg9 = json.loads(r9s.stdout)["systemMessage"]
    assert _CRASH_LINE in msg9


def test_new_code_fails_open(tmp_path):
    """G. An exception in the selector allows both hooks and never blocks."""
    hook_dir = _make_hook_dir(tmp_path, "non-OK line\n", 0)
    root = tmp_path / "root"
    root.mkdir()
    hooks_log = tmp_path / "hooks.log"
    sid = "sid11-" + str(uuid.uuid4())[:8]

    # Positive control: with the real _common.py, debt hook surfaces the non-OK line
    r_pos = _run_hook_script(
        hook_dir, "wrap_debt_hook.py", {"session_id": sid},
        root, hooks_log, tmp_path / "no-tuyere",
    )
    pos_out = json.loads(r_pos.stdout)
    assert "non-OK line" in pos_out.get("hookSpecificOutput", {}).get("additionalContext", "")

    # Install a raising advisory_lines (appended after the real one — overrides it)
    original = (hook_dir / "_common.py").read_text()
    (hook_dir / "_common.py").write_text(
        original + "\ndef advisory_lines(s):\n    raise RuntimeError('selector-raised')\n"
    )

    # Debt hook: fail-open → {} on error
    hooks_log.unlink(missing_ok=True)
    r_debt = _run_hook_script(
        hook_dir, "wrap_debt_hook.py", {"session_id": sid},
        root, hooks_log, tmp_path / "no-tuyere",
    )
    assert json.loads(r_debt.stdout) == {}
    assert r_debt.returncode == 0

    # Stop hook (armed): fail-open error handler — systemMessage only, sentinel gone
    hooks_log.unlink(missing_ok=True)
    sentinel = root / f".wrap-in-progress-{sid}"
    sentinel.touch()
    r_stop = _run_hook_script(
        hook_dir, "wrap_stop_hook.py", {"session_id": sid},
        root, hooks_log, tmp_path / "no-tuyere",
    )
    assert r_stop.returncode == 0
    out_stop = json.loads(r_stop.stdout)
    assert set(out_stop.keys()) == {"systemMessage"}
    assert "selector-raised" in out_stop["systemMessage"]
    assert "allowing" in out_stop["systemMessage"]
    assert not sentinel.exists()


def test_hooks_load_beside_a_stale_common(tmp_path, monkeypatch):
    """M. Hooks load even when sys.modules['_common'] lacks advisory_lines (attribute form required)."""
    hook_dir = _make_hook_dir(tmp_path, "", 0)
    common_path = hook_dir / "_common.py"
    assert str(common_path.resolve()).startswith(str(hook_dir.resolve())), (
        f"_common.py not under hook_dir {hook_dir}"
    )
    common = _load_module_from_path(common_path)

    # Build a stale module: today's names only, no advisory_lines
    stale = types.ModuleType("_common")
    for name in (
        "_DEFAULT_LOG", "_VALID_SESSION_ID", "_default_root",
        "_log_path", "hooklog", "emit", "_validate_session_id",
    ):
        setattr(stale, name, getattr(common, name))
    assert not hasattr(stale, "advisory_lines")

    # Install the stale module so both hooks' from-imports use it
    monkeypatch.setitem(sys.modules, "_common", stale)

    debt_mod = _load_module_from_path(hook_dir / "wrap_debt_hook.py", "_debt_stale_test")
    stop_mod = _load_module_from_path(hook_dir / "wrap_stop_hook.py", "_stop_stale_test")
    assert hasattr(debt_mod, "main")
    assert hasattr(stop_mod, "main")
