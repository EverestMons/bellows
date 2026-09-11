#!/usr/bin/env python3
"""DEV-side pre-check: run the five deposit-reading gates over a plan step before committing.

Usage: check_deposit.py <plan-path> <step> [--wt <path>] [--base <ref>] [--dependents]
       check_deposit.py <plan-path> <step> --expect-missing PATH [PATH ...] [--wt <path>]

Read-only: opens no files for writing. Exit 1 on any gate failure, 0 on clean.
WARN lines (from --dependents) never affect the exit code.

--expect-missing PATH [PATH ...]:
    Declare deposit paths this commit does not write yet.  Rule 22 (a) skips exactly
    those paths; the mutation-result and dev-log-declared-text gates go N/A when their
    file is named; a named path that EXISTS in the worktree fails immediately so the
    flag cannot be carried to the second commit.  A named path not declared as a
    Deposit of the step also fails.  Paths are normalised with os.path.normpath and
    de-duplicated; the summary line gains "(expecting M missing)" when M > 0.
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


def _remove_deposit_bullets(plan_text, step_number, expect_missing_norm):
    """Return plan_text with the expect_missing_norm paths' bullets removed from step N's body.

    Targets the step section only (## STEP N ... ## STEP N+1 or EOF).  Bullets are
    matched on the backtick-quoted path, allowing a trailing parenthetical, the same
    way _extract_plan_required_deposits reads them.
    """
    step_pat = rf"(?m)^## STEP {step_number}\b"
    step_m = re.search(step_pat, plan_text, re.IGNORECASE)
    if not step_m:
        return plan_text
    nxt = re.search(r"(?m)^## STEP ", plan_text[step_m.end():], re.IGNORECASE)
    step_end = step_m.end() + nxt.start() if nxt else len(plan_text)
    step_body = plan_text[step_m.start():step_end]
    modified = step_body
    for path in expect_missing_norm:
        escaped = re.escape(path)
        modified = re.sub(
            r"^[> ]*-\s+`" + escaped + r"(?:[^`\n]*)`[^\n]*\n?",
            "",
            modified,
            flags=re.MULTILINE,
        )
    return plan_text[: step_m.start()] + modified + plan_text[step_end:]


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
    parser.add_argument(
        "--expect-missing", nargs="+", default=[], metavar="PATH", dest="expect_missing",
        help="Deposit paths this commit does not write yet; rule 22 (a) skips exactly these.",
    )
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

    # De-duplicate and normalise expected-missing paths
    expect_missing = list(dict.fromkeys(os.path.normpath(p) for p in args.expect_missing))

    failures = []

    # --- --expect-missing routing (three rules + guard, before the gates run) ---
    if expect_missing:
        all_deposits = gates._extract_plan_required_deposits(step_text) if step_text else []
        all_deposits_norm = {os.path.normpath(p) for p in all_deposits}
        for p in expect_missing:
            # (c) A named path that EXISTS in the worktree fails
            if os.path.exists(os.path.join(wt_path, p)):
                failures.append({
                    "gate": "expect_missing",
                    "evidence": f"{p} is present in the worktree — drop it from --expect-missing",
                })
            # A named path not declared as a Deposit of this step fails
            if p not in all_deposits_norm:
                failures.append({
                    "gate": "expect_missing",
                    "evidence": f"{p} is not a Deposit of step {args.step}",
                })

    # (a) Build plan_text_for_gates with expected-missing bullets removed from step's Deposits block
    if expect_missing:
        plan_text_for_gates = _remove_deposit_bullets(plan_text, args.step, set(expect_missing))
    else:
        plan_text_for_gates = plan_text

    step_text_for_gates = gates._extract_step_text(plan_text_for_gates, args.step)
    deposits = gates._extract_plan_required_deposits(step_text_for_gates) if step_text_for_gates else []
    parsed = _make_parsed(deposits)

    is_qa_step = gates._gate_is_qa_step(plan_text_for_gates, args.step)

    # (b) Identify gates to skip (N/A) when their file is expected missing
    run_missing = [p for p in expect_missing if re.search(r"knowledge/mutants/.*\.run\.txt$", p)]
    devlog_missing = [p for p in expect_missing if re.search(r"knowledge/development/dev-log-[^/]*\.md$", p)]

    na_lines = []
    if run_missing:
        na_lines.append(
            f"PRECHECK: mutation_result N/A — run file expected missing ({run_missing[0]})"
        )
    if devlog_missing:
        na_lines.append(
            f"PRECHECK: dev_log_declared_text N/A — dev-log expected missing ({devlog_missing[0]})"
        )

    gates._gate_rule_22_verification(
        is_qa_step, plan_text_for_gates, args.step, project_path, parsed, failures, wt_path=wt_path
    )
    gates._gate_quoted_test_nodes_exist(
        is_qa_step, plan_text_for_gates, args.step, project_path, parsed, failures, wt_path=wt_path
    )
    if not run_missing:
        gates._gate_mutation_result(plan_text_for_gates, args.step, project_path, parsed, failures, wt_path=wt_path)
    gates._gate_qa_nodes_match_suite(
        is_qa_step, plan_text_for_gates, args.step, project_path, parsed, failures, wt_path=wt_path
    )
    if not devlog_missing:
        gates._gate_dev_log_declared_text(plan_text_for_gates, args.step, project_path, parsed, failures, wt_path=wt_path)

    warn_lines = _dependents_warns(wt_path, args.base) if args.dependents else []

    for w in warn_lines:
        print(w)
    for line in na_lines:
        print(line)
    for fail in failures:
        print(f"FAIL {fail['gate']}: {fail['evidence']}")

    plan_basename = os.path.basename(args.plan_path)
    m = len(expect_missing)
    suffix = f" (expecting {m} missing)" if m > 0 else ""
    print(f"PRECHECK: {len(failures)} failure(s) — {plan_basename} step {args.step}{suffix}")

    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
