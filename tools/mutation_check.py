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

A mutant may carry its own "target" key to override the manifest's top-level
target for that mutant only; the sandbox is a git archive of HEAD, so only
committed paths are valid targets.

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

_KNOWN_MUTANT_KEYS = {"name", "why", "anchor", "replacement", "expect_fail", "target"}


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


def _validate_target(t, repo_root, where):
    """Refuse a manifest target that leaves the repo root (thread 105).

    `os.path.join` DISCARDS its prefix when the second argument is absolute, so
    an absolute target collapses `live_target` and `sandbox_target` onto the SAME
    real file: the tool mutates it outside the sandbox while pytest runs unchanged
    code, and scores every mutant a false SURVIVED. A `..` traversal escapes
    differently — the two joins yield DIFFERENT paths, both outside their intended
    roots — so the per-target live-sha guard, which observes the collapse, does not
    cover it. Refuse both, loudly, naming where the bad target came from.
    """
    if os.path.isabs(t):
        print(f"ERROR: {where}: target must be repo-relative, got absolute path: {t}")
        sys.exit(2)
    resolved = os.path.normpath(os.path.join(repo_root, t))
    root = os.path.normpath(repo_root)
    if resolved != root and not resolved.startswith(root + os.sep):
        print(f"ERROR: {where}: target escapes the repo root: {t} -> {resolved}")
        sys.exit(2)


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

    _validate_target(target, repo_root, "manifest target")

    live_target = os.path.join(repo_root, target)
    if not os.path.isfile(live_target):
        print(f"ERROR: target not found: {live_target}")
        sys.exit(2)

    # Collect all distinct targets (top-level + any per-mutant overrides) for
    # uncommitted-changes warnings and the live-sha guard.
    # Per-mutant targets are LIVE (see the mutant loop below), so every mutant is
    # an independent path entry point — validate each before any join uses it.
    for _m in mutants:
        _mt = _m.get("target")
        if _mt:
            _validate_target(_mt, repo_root, f"mutant {_m.get('name', 'unnamed')!r}")

    all_targets = sorted(set(
        [target] + [m.get("target") for m in mutants if m.get("target")]
    ))

    for t in all_targets:
        lt = os.path.join(repo_root, t)
        if not os.path.isfile(lt):
            continue  # per-mutant target existence is validated inside the loop
        status_result = subprocess.run(
            ["git", "status", "--porcelain", "--", t],
            capture_output=True, text=True, cwd=repo_root,
        )
        if status_result.stdout.strip():
            print(f"WARNING: {t} has uncommitted changes "
                  "— this run audits HEAD, not your working tree")

    # Record live sha for every distinct target that exists before the run.
    live_shas_before = {}
    for t in all_targets:
        lt = os.path.join(repo_root, t)
        if os.path.isfile(lt):
            live_shas_before[t] = _sha256(lt)

    print(f"HEAD: {head_sha}")
    for t in all_targets:
        sha_prefix = live_shas_before[t][:12] if t in live_shas_before else "MISSING"
        print(f"TARGET: {t} sha256={sha_prefix}")
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

        sandbox_top = os.path.join(sandbox, target)
        if not os.path.isfile(sandbox_top):
            print(f"ERROR: target not in archive: {target}")
            sys.exit(2)

        # Per-target pristine cache. Populated lazily on first use of each
        # target path; prevents a mutant targeting file B from receiving
        # file A's contents as its pristine baseline.
        pristines = {}

        for mutant in mutants:
            name = mutant.get("name", "unnamed")

            # Refuse unknown keys (underscore-prefixed keys are commentary).
            unknown = [k for k in mutant
                       if not k.startswith("_") and k not in _KNOWN_MUTANT_KEYS]
            if unknown:
                key_list = ", ".join(repr(k) for k in sorted(unknown))
                print(f"MUTANT {name}: ERROR — unknown key(s) {key_list}"
                      f" (prefix with _ to mark as commentary)")
                manifest_errors += 1
                continue

            anchor = mutant.get("anchor")
            replacement = mutant.get("replacement")
            selector = mutant.get("expect_fail")
            mutant_target = mutant.get("target") or target

            if not all([anchor is not None, replacement is not None, selector]):
                print(f"MUTANT {name}: ERROR — missing required fields")
                manifest_errors += 1
                continue

            # Load pristine content for this target on first encounter.
            sandbox_target = os.path.join(sandbox, mutant_target)
            if mutant_target not in pristines:
                if not os.path.isfile(sandbox_target):
                    print(f"MUTANT {name}: ERROR — target not in archive: {mutant_target}")
                    manifest_errors += 1
                    continue
                with open(sandbox_target, "r") as f:
                    pristines[mutant_target] = f.read()

            # Restore ALL previously-touched sandbox targets to pristine so
            # this mutant's baseline runs against a clean tree.
            for pt, pc in pristines.items():
                sp = os.path.join(sandbox, pt)
                if os.path.isfile(sp):
                    with open(sp, "w") as f:
                        f.write(pc)

            pristine = pristines[mutant_target]

            count = pristine.count(anchor)
            if count != 1:
                print(f"MUTANT {name}: ERROR — anchor matched {count} times"
                      f" (expected 1) in {mutant_target}")
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
            # in practice: the baseline control rejects any selector that
            # collects nothing, and a selector that collects tests at baseline
            # also collects them when mutated — so exit 5 cannot reach this
            # block past a green baseline. A mutant on the exit-5 clause
            # therefore SURVIVES by design and must not be read as a coverage gap.
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
        # Live-sha guard covers every distinct target, not just the top-level
        # one. An absolute per-mutant target collapses live and sandbox paths
        # onto the same real file; extending the guard here ensures mutations
        # outside the sandbox are observed and flagged.
        print()
        for t in sorted(live_shas_before.keys()):
            lt = os.path.join(repo_root, t)
            sha_after = _sha256(lt)
            sha_before = live_shas_before[t]
            if sha_after == sha_before:
                print(f"LIVE-TREE UNCHANGED: {t} sha256={sha_after[:12]}")
            else:
                print(f"ERROR: LIVE TREE CHANGED! {t} "
                      f"before={sha_before[:12]} after={sha_after[:12]}")

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
