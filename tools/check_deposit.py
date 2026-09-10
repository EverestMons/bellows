#!/usr/bin/env python3
"""DEV-side pre-check: run the five deposit-reading gates over a plan step before committing.

Usage: check_deposit.py <plan-path> <step> [--wt <path>] [--base <ref>] [--dependents]

Read-only: opens no files for writing. Exit 1 on any gate failure, 0 on clean.
WARN lines (from --dependents) never affect the exit code.
"""
import argparse
import ast
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import gates

GATES = (
    gates._gate_rule_22_verification,
    gates._gate_quoted_test_nodes_exist,
    gates._gate_mutation_result,
    gates._gate_qa_nodes_match_suite,
    gates._gate_dev_log_declared_text,
)


def _make_parsed(deposits):
    """Synthesise the receipt the pause would have from the step's declared deposit list."""
    result_text = "### Files Deposited\n" + "".join(f"- `{p}`\n" for p in deposits)
    return {"result_text": result_text}


def find_referencing_files(names, wt_path):
    """Return {name: [referencing .py file paths]} via git grep. Swappable for anvil-backed impl."""
    result = {}
    for name in names:
        try:
            raw = subprocess.check_output(
                ["git", "grep", "-wl", name, "--", "*.py"],
                cwd=wt_path,
                stderr=subprocess.DEVNULL,
            ).decode(errors="replace").splitlines()
            result[name] = [f for f in raw if f]
        except subprocess.CalledProcessError:
            result[name] = []
    return result


def _run_git(args, cwd):
    try:
        return subprocess.check_output(args, cwd=cwd, stderr=subprocess.DEVNULL).decode(
            errors="replace"
        ).splitlines()
    except subprocess.CalledProcessError:
        return []


def _parse_hunk_ranges(diff_lines):
    ranges = []
    diff_text = "\n".join(diff_lines)
    for m in re.finditer(r"^@@ -\d+(?:,\d+)? \+(\d+)(?:,(\d+))? @@", diff_text, re.MULTILINE):
        start = int(m.group(1))
        count = int(m.group(2)) if m.group(2) is not None else 1
        if count > 0:
            ranges.append((start, start + count - 1))
    return ranges


def _hunk_ranges_for_file(rel_file, wt_path, base):
    ranges = []
    for args in (
        ["git", "diff", "-U0", f"{base}..HEAD", "--", rel_file],
        ["git", "diff", "-U0", "HEAD", "--", rel_file],
    ):
        ranges.extend(_parse_hunk_ranges(_run_git(args, wt_path)))
    return ranges


def _top_level_names_in_ranges(abs_file, hunk_ranges):
    try:
        with open(abs_file, encoding="utf-8", errors="replace") as f:
            src = f.read()
    except OSError:
        return []
    try:
        tree = ast.parse(src)
    except SyntaxError:
        return []
    names = []
    for node in ast.iter_child_nodes(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            start = node.lineno
            end = getattr(node, "end_lineno", node.lineno)
            if any(s <= end and start <= e for s, e in hunk_ranges):
                names.append(node.name)
        elif isinstance(node, ast.Assign):
            start = node.lineno
            end = getattr(node, "end_lineno", node.lineno)
            if any(s <= end and start <= e for s, e in hunk_ranges):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id.isupper():
                        names.append(target.id)
    return names


def _dependents_warns(wt_path, base):
    """Return WARN strings for changed top-level names that have external consumers."""
    all_changed = set()
    for args in (
        ["git", "diff", "--name-only", f"{base}..HEAD", "--", "*.py"],
        ["git", "diff", "--name-only", "HEAD", "--", "*.py"],
        ["git", "diff", "--name-only", "--", "*.py"],
    ):
        all_changed.update(_run_git(args, wt_path))

    py_changed = [f for f in all_changed if f.endswith(".py")]
    if not py_changed:
        return []

    changed_names = []
    for rel_file in py_changed:
        abs_file = os.path.join(wt_path, rel_file)
        hunk_ranges = _hunk_ranges_for_file(rel_file, wt_path, base)
        if not hunk_ranges:
            continue
        changed_names.extend(_top_level_names_in_ranges(abs_file, hunk_ranges))

    if not changed_names:
        return []

    ref_map = find_referencing_files(changed_names, wt_path)

    warns = []
    for name in changed_names:
        external = [f for f in ref_map.get(name, []) if f not in all_changed]
        if not external:
            continue
        if len(external) > 25:
            warns.append(f"WARN dependents: {name} → (generic, {len(external)} files)")
        else:
            listed = external[:10]
            warns.append(f"WARN dependents: {name} → {', '.join(listed)}")
    return warns


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="DEV-side pre-check: run deposit-reading gates before committing."
    )
    parser.add_argument("plan_path", help="Path to the plan file")
    parser.add_argument("step", type=int, help="Step number to check")
    parser.add_argument("--wt", help="Worktree root (default: git rev-parse --show-toplevel)")
    parser.add_argument("--base", default="main", help="Base ref for dependents diff (default: main)")
    parser.add_argument("--dependents", action="store_true", help="Emit WARN lines for changed names' consumers")
    args = parser.parse_args(argv)

    if args.wt:
        wt_path = os.path.abspath(args.wt)
    else:
        try:
            wt_path = subprocess.check_output(
                ["git", "rev-parse", "--show-toplevel"], stderr=subprocess.DEVNULL
            ).decode().strip()
        except subprocess.CalledProcessError:
            wt_path = os.getcwd()

    project_path = wt_path

    with open(args.plan_path, encoding="utf-8") as f:
        plan_text = f.read()

    step_text = gates._extract_step_text(plan_text, args.step)
    deposits = gates._extract_plan_required_deposits(step_text) if step_text else []
    parsed = _make_parsed(deposits)

    failures = []
    is_qa_step = gates._gate_is_qa_step(plan_text, args.step)

    gates._gate_rule_22_verification(
        is_qa_step, plan_text, args.step, project_path, parsed, failures, wt_path=wt_path
    )
    gates._gate_quoted_test_nodes_exist(
        is_qa_step, plan_text, args.step, project_path, parsed, failures, wt_path=wt_path
    )
    gates._gate_mutation_result(plan_text, args.step, project_path, parsed, failures, wt_path=wt_path)
    gates._gate_qa_nodes_match_suite(
        is_qa_step, plan_text, args.step, project_path, parsed, failures, wt_path=wt_path
    )
    gates._gate_dev_log_declared_text(plan_text, args.step, project_path, parsed, failures, wt_path=wt_path)

    warn_lines = _dependents_warns(wt_path, args.base) if args.dependents else []

    for w in warn_lines:
        print(w)
    for fail in failures:
        print(f"FAIL {fail['gate']}: {fail['evidence']}")

    plan_basename = os.path.basename(args.plan_path)
    print(f"PRECHECK: {len(failures)} failure(s) — {plan_basename} step {args.step}")

    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
