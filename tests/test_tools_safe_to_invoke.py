"""Test that every tool and script in the bellows repo is safe to invoke.

Four properties, pinned by static analysis and subprocess observation:
  t1 — no absolute /Users/ paths baked into source
  t2 — no import-time file or subprocess writes
  t3 — --help exits with a usage line and leaves no knowledge/ files modified
  t4 — the two census writers refuse without --out (exit 2, --out in stderr)
"""

import ast
import os
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]

_WRITE_NAMES = frozenset({
    "open", "write_text", "write_bytes", "mkdir", "makedirs",
    "connect", "run", "Popen", "call", "check_call", "check_output", "system",
})

_WRITERS = [
    ROOT / "tools" / "cycle_log_projection_census.py",
    ROOT / "tools" / "register_coverage_census.py",
]


# ── helpers ───────────────────────────────────────────────────────────────────

def _py_files():
    return sorted(ROOT.glob("tools/*.py")) + sorted(ROOT.glob("scripts/*.py"))


def _abs_home_paths(path):
    """Return list of 'path:line: repr(value)' for string constants containing /Users/<name>/...."""
    hits = []
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except SyntaxError:
        return hits
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            idx = node.value.find("/Users/")
            if idx >= 0 and len(node.value) > idx + len("/Users/"):
                hits.append(f"{path}:{node.lineno}: {node.value!r}")
    return hits


def _call_name(node):
    """Extract bare or attribute call name from a Call node's func."""
    if isinstance(node.func, ast.Name):
        return node.func.id
    if isinstance(node.func, ast.Attribute):
        return node.func.attr
    return None


def _import_time_writes(path):
    """Return list of 'path:line: name()' for write calls at module level outside safe blocks."""
    hits = []
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except SyntaxError:
        return hits
    for stmt in tree.body:
        if isinstance(stmt, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef,
                              ast.Import, ast.ImportFrom)):
            continue
        if isinstance(stmt, ast.If):
            test = stmt.test
            if (isinstance(test, ast.Compare)
                    and isinstance(test.left, ast.Name)
                    and test.left.id == "__name__"
                    and len(test.ops) == 1
                    and isinstance(test.ops[0], ast.Eq)
                    and len(test.comparators) == 1
                    and isinstance(test.comparators[0], ast.Constant)
                    and test.comparators[0].value == "__main__"):
                continue
        for node in ast.walk(stmt):
            if isinstance(node, ast.Call):
                name = _call_name(node)
                if name in _WRITE_NAMES:
                    hits.append(f"{path}:{node.lineno}: {name}()")
    return hits


def _static_ok(path):
    return not _abs_home_paths(path) and not _import_time_writes(path)


def _snapshot(roots):
    """Return set of (rel_path_str, size, mtime_ns) for knowledge/ files, excluding decisions/."""
    result = set()
    for root in roots:
        knowledge = root / "knowledge"
        if not knowledge.is_dir():
            continue
        decisions = knowledge / "decisions"
        for fp in knowledge.rglob("*"):
            if not fp.is_file():
                continue
            try:
                fp.relative_to(decisions)
                continue
            except ValueError:
                pass
            try:
                rel = fp.relative_to(root)
                st = fp.stat()
                result.add((str(rel), st.st_size, st.st_mtime_ns))
            except (OSError, ValueError):
                pass
    return result


# ── t1 ────────────────────────────────────────────────────────────────────────

def test_no_absolute_home_paths():
    hits = []
    for p in _py_files():
        hits.extend(_abs_home_paths(p))
    assert hits == [], "Absolute /Users/ paths found:\n" + "\n".join(hits)


# ── t2 ────────────────────────────────────────────────────────────────────────

def test_no_import_time_writes():
    hits = []
    for p in _py_files():
        hits.extend(_import_time_writes(p))
    assert hits == [], "Import-time writes found:\n" + "\n".join(hits)


# ── t3 ────────────────────────────────────────────────────────────────────────

def test_help_does_no_work(tmp_path):
    from bellows_root import resolve_bellows_root
    roots = {ROOT}
    try:
        canonical = resolve_bellows_root()
        if canonical != ROOT:
            roots.add(canonical)
    except ValueError:
        pass

    before = _snapshot(roots)
    failures = []
    for tool in sorted(ROOT.glob("tools/*.py")):
        if not _static_ok(tool):
            failures.append(f"{tool.name}: failed static check")
            continue
        try:
            r = subprocess.run(
                [sys.executable, str(tool), "--help"],
                cwd=str(tmp_path),
                env={**os.environ, "HOME": str(tmp_path)},
                capture_output=True,
                text=True,
                timeout=60,
            )
        except subprocess.TimeoutExpired:
            failures.append(f"{tool.name}: timed out after 60 s")
            continue
        combined = (r.stdout + r.stderr).lower()
        if "usage" not in combined:
            failures.append(f"{tool.name}: --help produced no usage line")

    assert failures == [], "tool --help failures:\n" + "\n".join(failures)
    after = _snapshot(roots)
    assert after == before, "knowledge/ files changed during --help runs"


# ── t4 ────────────────────────────────────────────────────────────────────────

def test_writers_refuse_without_out(tmp_path):
    from bellows_root import resolve_bellows_root
    roots = {ROOT}
    try:
        canonical = resolve_bellows_root()
        if canonical != ROOT:
            roots.add(canonical)
    except ValueError:
        pass

    before = _snapshot(roots)
    failures = []
    for writer in _WRITERS:
        if not _static_ok(writer):
            failures.append(f"{writer.name}: failed static check")
            continue
        try:
            r = subprocess.run(
                [sys.executable, str(writer)],
                cwd=str(tmp_path),
                env={**os.environ, "HOME": str(tmp_path)},
                capture_output=True,
                text=True,
                timeout=60,
            )
        except subprocess.TimeoutExpired:
            failures.append(f"{writer.name}: timed out after 60 s")
            continue
        if r.returncode != 2:
            failures.append(f"{writer.name}: expected exit 2, got {r.returncode}")
        if "--out" not in r.stderr:
            failures.append(f"{writer.name}: '--out' not in stderr")

    assert failures == [], "writer refusal failures:\n" + "\n".join(failures)
    after = _snapshot(roots)
    assert after == before, "knowledge/ files changed during writer refusal check"


# ── t5 ────────────────────────────────────────────────────────────────────────

def test_every_module_parses_under_python39():
    OLD = "/usr/bin/python3"
    if not Path(OLD).exists():
        pytest.skip(f"{OLD} not found")
    ver_r = subprocess.run(
        [OLD, "-c", "import sys; print(sys.version_info[:2])"],
        capture_output=True, text=True, timeout=10,
    )
    ver = ast.literal_eval(ver_r.stdout.strip())
    if ver >= (3, 12):
        pytest.skip(f"{OLD} reports {ver}, not below (3, 12)")

    files = (
        _py_files()
        + sorted(ROOT.glob("*.py"))
        + sorted(ROOT.glob("hooks/eluvian/*.py"))
    )

    script = "\n".join([
        "import ast, sys",
        "from pathlib import Path",
        "ROOT = Path(sys.argv[1])",
        "hits = []",
        "for p in sys.argv[2:]:",
        "    path = Path(p)",
        "    try:",
        "        ast.parse(path.read_text(encoding='utf-8'))",
        "    except SyntaxError as e:",
        "        rel = path.relative_to(ROOT)",
        "        hits.append(f'{rel}:{e.lineno}:{e.msg}')",
        "print('\\n'.join(hits), end='')",
    ])

    result = subprocess.run(
        [OLD, "-c", script, str(ROOT)] + [str(f) for f in files],
        capture_output=True, text=True, timeout=60,
    )
    output = result.stdout.strip()
    assert output == "", f"Files that do not parse under {OLD}:\n{output}"


# ── t6 ────────────────────────────────────────────────────────────────────────

def _def_time_unions(path):
    """Return 'path:line' for PEP 604 unions in def-time annotations without future import."""
    hits = []
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except SyntaxError:
        return hits
    for node in tree.body:
        if isinstance(node, ast.ImportFrom) and node.module == "__future__":
            for alias in node.names:
                if alias.name == "annotations":
                    return hits

    def _has_union(annotation):
        for n in ast.walk(annotation):
            if isinstance(n, ast.BinOp) and isinstance(n.op, ast.BitOr):
                return True
        return False

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            all_args = (
                node.args.posonlyargs
                + node.args.args
                + node.args.kwonlyargs
            )
            if node.args.vararg:
                all_args = all_args + [node.args.vararg]
            if node.args.kwarg:
                all_args = all_args + [node.args.kwarg]
            for arg in all_args:
                if arg.annotation and _has_union(arg.annotation):
                    hits.append(f"{path}:{arg.annotation.lineno}")
            if node.returns and _has_union(node.returns):
                hits.append(f"{path}:{node.returns.lineno}")

    def _check_stmts(stmts, evaluated):
        # evaluated: True at module/class scope, False inside a function body
        for stmt in stmts:
            if isinstance(stmt, ast.AnnAssign) and evaluated and _has_union(stmt.annotation):
                hits.append(f"{path}:{stmt.annotation.lineno}")
            elif isinstance(stmt, ast.ClassDef):
                _check_stmts(stmt.body, True)
            elif isinstance(stmt, (ast.FunctionDef, ast.AsyncFunctionDef)):
                _check_stmts(stmt.body, False)
            else:
                for field in ("body", "orelse", "finalbody"):
                    block = getattr(stmt, field, None)
                    if block:
                        _check_stmts(block, evaluated)
                for handler in getattr(stmt, "handlers", ()):
                    _check_stmts(handler.body, evaluated)
                for case in getattr(stmt, "cases", ()):
                    _check_stmts(case.body, evaluated)

    _check_stmts(tree.body, True)

    return hits


def test_no_def_time_union_without_future_import():
    files = (
        _py_files()
        + sorted(ROOT.glob("*.py"))
        + sorted(ROOT.glob("hooks/eluvian/*.py"))
        + sorted((ROOT / "tests").rglob("*.py"))
    )
    hits = []
    for p in files:
        hits.extend(_def_time_unions(p))
    assert hits == [], (
        "Definition-time PEP 604 unions without future import:\n"
        + "\n".join(hits)
    )


def _module(tmp_path, source):
    p = tmp_path / "m.py"
    p.write_text(source, encoding="utf-8")
    return p


@pytest.mark.parametrize("src,line", [
    pytest.param("if True:\n    x: int | None = None\n", 2, id="if"),
    pytest.param(
        "if False:\n    pass\nelif True:\n    x: int | None = None\n", 4, id="elif"
    ),
    pytest.param(
        "if False:\n    pass\nelse:\n    x: int | None = None\n", 4, id="else"
    ),
    pytest.param("for _ in []:\n    x: int | None = None\n", 2, id="for"),
    pytest.param(
        "for _ in []:\n    pass\nelse:\n    x: int | None = None\n", 4, id="for-else"
    ),
    pytest.param("while True:\n    x: int | None = None\n", 2, id="while"),
    pytest.param("with f:\n    x: int | None = None\n", 2, id="with"),
    pytest.param(
        "try:\n    x: int | None = None\nexcept Exception:\n    pass\n", 2, id="try"
    ),
    pytest.param(
        "try:\n    pass\nexcept Exception:\n    x: int | None = None\n", 4, id="except"
    ),
    pytest.param(
        "try:\n    pass\nexcept Exception:\n    pass\nelse:\n    x: int | None = None\n",
        6,
        id="try-else",
    ),
    pytest.param(
        "try:\n    pass\nfinally:\n    x: int | None = None\n", 4, id="finally"
    ),
    pytest.param(
        "def f():\n    class C:\n        x: int | None = None\n",
        3,
        id="class-in-function",
    ),
    pytest.param(
        "if True:\n    class C:\n        x: int | None = None\n",
        3,
        id="class-in-if",
    ),
    pytest.param(
        "match x:\n    case _:\n        y: int | None = None\n",
        3,
        id="match",
        marks=pytest.mark.skipif(
            sys.version_info < (3, 10), reason="match needs 3.10"
        ),
    ),
])
def test_t6_reads_every_evaluated_scope(tmp_path, src, line):
    p = _module(tmp_path, src)
    assert f"{p}:{line}" in _def_time_unions(p)


@pytest.mark.parametrize("src", [
    pytest.param("def f():\n    x: int | None = None\n", id="function-local"),
    pytest.param(
        "def f():\n    if True:\n        x: int | None = None\n",
        id="block-in-function",
    ),
    pytest.param(
        "if True:\n    def f():\n        x: int | None = None\n",
        id="function-in-if",
    ),
    pytest.param(
        "from __future__ import annotations\nx: int | None = None\n",
        id="future-import",
    ),
])
def test_t6_passes_over_unevaluated_scopes(tmp_path, src):
    p = _module(tmp_path, src)
    assert _def_time_unions(p) == []
