#!/usr/bin/env python3
"""Sandboxed mutation runner — manifest-driven, exit-1-only KILLED, baseline control.

Applies hand-named mutants from a JSON manifest to a git-archive sandbox,
runs each mutant's expect_fail selector (a pytest node id), and scores:

  KILLED   — pytest exit 1 (tests ran and at least one failed)
  SURVIVED — pytest exit 0 (all tests passed despite the mutation)
  ERROR    — any other outcome (exit 5 = no tests collected, baseline
             failure, anchor mismatch, timeout, etc.)

Only exit code 1 counts as KILLED. pytest exits 5 on "no tests collected",
4 on usage error, 2 on interrupt, 3 on internal error — scoring any of
these as KILLED would manufacture the false confidence this tool exists to
destroy.

The expect_fail field is a pytest NODE ID
(e.g. tests/test_foo.py::TestClass or tests/test_foo.py::TestClass::test_method).

The tool audits COMMITTED code (git archive HEAD). Uncommitted edits to the
target are invisible and warned about.
"""

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile


def _sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def _run_pytest(selector, cwd, timeout):
    # Bytecode is invalidated by (mtime, size) — a same-byte-length mutation
    # written within the same mtime second leaves the cached .pyc valid and
    # the mutant run executes baseline code. The cache location is environment-
    # dependent (sys.pycache_prefix redirects it out of the tree on macOS), so
    # clearing __pycache__ is not a portable substitute.
    env = dict(os.environ)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pytest", selector, "-q"],
            cwd=cwd,
            timeout=timeout,
            capture_output=True,
            text=True,
            env=env,
        )
        return result.returncode
    except subprocess.TimeoutExpired:
        return -1


def main():
    parser = argparse.ArgumentParser(description="Sandboxed mutation runner")
    parser.add_argument("manifest", help="Path to mutant manifest JSON")
    parser.add_argument("--repo-root", default=None,
                        help="Repository root (default: git rev-parse --show-toplevel)")
    parser.add_argument("--keep-sandbox", action="store_true",
                        help="Keep sandbox directory after run")
    parser.add_argument("--timeout", type=int, default=300,
                        help="Per-pytest timeout in seconds (default: 300)")
    args = parser.parse_args()

    if args.repo_root:
        repo_root = os.path.abspath(args.repo_root)
    else:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True, text=True,
        )
        if result.returncode != 0:
            print("ERROR: not in a git repository")
            sys.exit(2)
        repo_root = result.stdout.strip()

    head_result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        capture_output=True, text=True, cwd=repo_root,
    )
    head_sha = head_result.stdout.strip() if head_result.returncode == 0 else "UNKNOWN"

    try:
        with open(args.manifest) as f:
            manifest = json.load(f)
    except (json.JSONDecodeError, FileNotFoundError, OSError) as e:
        print(f"ERROR: cannot load manifest: {e}")
        sys.exit(2)

    target = manifest.get("target")
    mutants = manifest.get("mutants", [])
    if not target or not mutants:
        print("ERROR: manifest must have 'target' and non-empty 'mutants'")
        sys.exit(2)

    live_target = os.path.join(repo_root, target)
    if not os.path.isfile(live_target):
        print(f"ERROR: target not found: {live_target}")
        sys.exit(2)

    status_result = subprocess.run(
        ["git", "status", "--porcelain", "--", target],
        capture_output=True, text=True, cwd=repo_root,
    )
    if status_result.stdout.strip():
        print("WARNING: target has uncommitted changes "
              "— this run audits HEAD, not your working tree")

    live_sha_before = _sha256(live_target)
    print(f"HEAD: {head_sha}")
    print(f"TARGET: {target} sha256={live_sha_before[:12]}")
    print()

    sandbox = tempfile.mkdtemp(prefix="mutation_check_")
    killed = 0
    survived = 0
    errors = 0
    manifest_errors = 0

    try:
        archive = subprocess.run(
            ["git", "archive", "HEAD"],
            capture_output=True, cwd=repo_root,
        )
        if archive.returncode != 0:
            print("ERROR: git archive failed")
            sys.exit(2)

        tar = subprocess.run(
            ["tar", "-x", "-C", sandbox],
            input=archive.stdout,
        )
        if tar.returncode != 0:
            print("ERROR: tar extraction failed")
            sys.exit(2)

        sandbox_target = os.path.join(sandbox, target)
        if not os.path.isfile(sandbox_target):
            print(f"ERROR: target not in archive: {target}")
            sys.exit(2)

        with open(sandbox_target, "r") as f:
            pristine = f.read()

        for mutant in mutants:
            name = mutant.get("name", "unnamed")
            anchor = mutant.get("anchor")
            replacement = mutant.get("replacement")
            selector = mutant.get("expect_fail")

            if not all([anchor is not None, replacement is not None, selector]):
                print(f"MUTANT {name}: ERROR — missing required fields")
                manifest_errors += 1
                continue

            with open(sandbox_target, "w") as f:
                f.write(pristine)

            count = pristine.count(anchor)
            if count != 1:
                print(f"MUTANT {name}: ERROR — anchor matched {count} times"
                      " (expected 1)")
                manifest_errors += 1
                continue

            baseline_exit = _run_pytest(selector, sandbox, args.timeout)
            if baseline_exit != 0:
                if baseline_exit == -1:
                    detail = "baseline timed out"
                elif baseline_exit == 5:
                    detail = "baseline: no tests collected (bad selector?)"
                else:
                    detail = f"baseline not green (pytest exit {baseline_exit})"
                print(f"MUTANT {name}: ERROR — {detail}")
                errors += 1
                continue

            mutated = pristine.replace(anchor, replacement, 1)
            with open(sandbox_target, "w") as f:
                f.write(mutated)

            # Force bytecode invalidation by the mechanism CPython actually
            # uses: it validates a cached .pyc by (source mtime, source size).
            # A same-byte-length mutation written inside the same mtime second
            # leaves the baseline's .pyc valid, so the mutant run would execute
            # BASELINE code and score a false SURVIVED. Measured flaky 4-of-5
            # before this bump (exec-577). PYTHONDONTWRITEBYTECODE remains set
            # as defence in depth; this line is what makes it deterministic.
            _st = os.stat(sandbox_target)
            os.utime(sandbox_target, (_st.st_atime, _st.st_mtime + 1))

            with open(sandbox_target, "r") as f:
                written = f.read()
            if replacement not in written:
                print(f"MUTANT {name}: ERROR — replacement not found after write")
                manifest_errors += 1
                continue

            exit_code = _run_pytest(selector, sandbox, args.timeout)

            # Scoring: only the exit-1 arm is KILLED; the non-1 arms below
            # are defence in depth. The exit-5 arm specifically is unreachable
            # in practice: the baseline control at :177-186 rejects any
            # selector that collects nothing, and a selector that collects
            # tests at baseline also collects them when mutated — so exit 5
            # cannot reach this block past a green baseline. A mutant on the
            # exit-5 clause therefore SURVIVES by design and must not be read
            # as a coverage gap.
            if exit_code == 1:
                print(f"MUTANT {name}: KILLED — suite caught the defect")
                killed += 1
            elif exit_code == 0:
                print(f"MUTANT {name}: SURVIVED "
                      "— suite does not discriminate this defect")
                survived += 1
            elif exit_code == -1:
                print(f"MUTANT {name}: ERROR — timeout after {args.timeout}s")
                errors += 1
            else:
                print(f"MUTANT {name}: ERROR — pytest exit {exit_code}")
                errors += 1

    finally:
        live_sha_after = _sha256(live_target)
        if live_sha_after == live_sha_before:
            print(f"\nLIVE-TREE UNCHANGED: {live_sha_after[:12]}")
        else:
            print(f"\nERROR: LIVE TREE CHANGED! "
                  f"before={live_sha_before[:12]} after={live_sha_after[:12]}")

        if not args.keep_sandbox:
            shutil.rmtree(sandbox, ignore_errors=True)
        else:
            print(f"Sandbox kept at: {sandbox}")

    total_errors = errors + manifest_errors
    print(f"\nMUTATION: {killed} killed, {survived} survived, "
          f"{total_errors} error")
    if survived > 0:
        print("SURVIVED means the suite does not discriminate this defect "
              "— the tests are decorative for it.")

    if manifest_errors > 0:
        sys.exit(2)
    elif survived > 0 or errors > 0:
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
