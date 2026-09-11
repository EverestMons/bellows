#!/usr/bin/env python3
"""close_cycle — runs the close sequence in the correct order.

Usage:
    close_cycle.py <draft> --closing-file <text-file> [--register <path>]
                           [--commit] [--dry-run]

Steps (printed as CLOSE: <step> OK/FAIL):
    1. closing      — replace the **Closing:** line
    2. baseline     — fold_check --save-baseline
    3. emit         — cycle_check --emit-manifest (captured)
    4. splice       — walks/yields/validation/coherence by key
    5. baseline     — fold_check --save-baseline (again)
    6. stored==live — re-emit and compare; one re-splice when only propagation_check moved
    7. battery      — cycle_check BAR_MET, plan_lint 0_FAIL,
                      lens_order_check LENS-ORDER OK, walk_register_lint SHAPE-OK
    8. commit       — git add + commit (or skipped)
"""

import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

SCRIPTS = Path(os.path.dirname(os.path.abspath(__file__)))
_SPLICE_KEYS = ("walks", "yields", "validation", "coherence")


def run_checker(script, *args):
    """Seam: run a checker subprocess. Returns (returncode, combined_output)."""
    result = subprocess.run(
        [sys.executable, str(SCRIPTS / script), *args],
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
    )
    return result.returncode, result.stdout


def after_step(name):
    """Seam: called after each step. No-op in production; tests patch it."""


def _replace_closing_line(text, closing_text):
    """Replace the **Closing:** line. Returns (new_text, error_or_None)."""
    lines = text.splitlines(keepends=True)
    found = [i for i, ln in enumerate(lines) if ln.startswith("**Closing:**")]
    if len(found) == 0:
        return None, "no **Closing:** line found"
    if len(found) > 1:
        return None, f"{len(found)} **Closing:** lines found"
    repl = closing_text if closing_text.endswith("\n") else closing_text + "\n"
    lines[found[0]] = repl
    return "".join(lines), None


def _parse_validation_tokens(line):
    """Parse 'validation: k=v, k=v, …' → {key: full-token-string, …}."""
    if not line:
        return {}
    val = line[len("validation: "):]
    return {p.split("=", 1)[0]: p for p in val.split(", ") if "=" in p}


def _splice_keys(draft_text, emit_stdout):
    """Splice walks/yields/validation/coherence from emitter output into the draft.

    Returns (new_text, error_or_None). The ## Cycle Manifest header line and
    any other emitter lines (tier, target, …) are silently ignored — only the
    four splice keys are written.
    """
    emit_vals = {}
    for line in emit_stdout.splitlines():
        for key in _SPLICE_KEYS:
            if line.startswith(f"{key}: "):
                emit_vals[key] = line
                break

    missing_emit = [k for k in _SPLICE_KEYS if k not in emit_vals]
    if missing_emit:
        return None, f"emitter missing keys: {', '.join(missing_emit)}"

    lines = draft_text.splitlines(keepends=True)
    found = {k: 0 for k in _SPLICE_KEYS}
    new_lines = []
    for ln in lines:
        stripped = ln.rstrip("\n\r")
        spliced = False
        for key in _SPLICE_KEYS:
            if stripped.startswith(f"{key}: "):
                new_lines.append(emit_vals[key] + "\n")
                found[key] += 1
                spliced = True
                break
        if not spliced:
            new_lines.append(ln)

    missing_draft = [k for k, v in found.items() if v == 0]
    if missing_draft:
        return None, f"draft missing keys: {', '.join(missing_draft)}"

    return "".join(new_lines), None


def _strip_field(path, key):
    """Remove lines starting with 'key: ' from path (in-place)."""
    text = path.read_text(encoding="utf-8")
    new_lines = [ln for ln in text.splitlines(keepends=True)
                 if not ln.startswith(f"{key}: ")]
    if len(new_lines) != len(text.splitlines(keepends=True)):
        path.write_text("".join(new_lines), encoding="utf-8")


def _baseline_path(draft_path):
    p = Path(draft_path)
    return p.parent / f".{p.name}.foldcheck.json"


def _compose_subject(draft_path, emit_stdout):
    slug = Path(draft_path).stem
    walks = "?"
    tier = "?"
    for line in emit_stdout.splitlines():
        if line.startswith("walks: "):
            walks = line[len("walks: "):].strip()
        elif line.startswith("tier: "):
            tier = line[len("tier: "):].strip()
    return (
        f"draft({slug}): close — WARM after walk {walks} (BAR_MET; {tier}); "
        f"manifest spliced by key, emitted after the baseline"
    )


def _run_battery(draft_path, register_path, git_plan=None):
    """Run the battery. Returns list of failure strings (empty = pass).

    git_plan: path used for lens_order_check (must be inside a git repo);
              defaults to draft_path. Set to the original plan when dry-running
              on temp copies that have no git repo above them.
    """
    failures = []
    git_plan = git_plan or draft_path

    rc, out = run_checker("cycle_check.py", str(draft_path))
    last = out.strip().split("\n")[-1] if out.strip() else ""
    if not last.startswith("BAR_MET"):
        failures.append(f"cycle_check: expected BAR_MET, got {last!r}")

    rc, out = run_checker("plan_lint.py", str(draft_path))
    for _line in out.splitlines():
        if re.match(r"^(\([a-z0-9]+\) )?WARN: ", _line.strip()):
            print(f"CLOSE-WARN: plan_lint — {_line}")
    if rc != 0:
        fail_rows = [l for l in out.splitlines() if l.startswith("FAIL: ")]
        failures.append(
            f"plan_lint: exit {rc} — {' | '.join(fail_rows)}" if fail_rows
            else f"plan_lint: exit {rc}"
        )

    rc, out = run_checker("lens_order_check.py", str(git_plan))
    if "LENS-ORDER OK" not in out and "LENS-ORDER N/A" not in out:
        failures.append(f"lens_order_check: expected LENS-ORDER OK/N/A, got {out.strip()!r}")

    if register_path:
        rc, out = run_checker("walk_register_lint.py", str(register_path),
                              "--plan", str(draft_path))
        if "SHAPE-OK" not in out:
            failures.append(f"walk_register_lint: expected SHAPE-OK")
        if "COVERAGE: INCOMPLETE" in out:
            failures.append(f"walk_register_lint: COVERAGE: INCOMPLETE")

    return failures


def _run_close(draft_path, closing_text, register_path, do_commit, dry_run, git_plan=None):
    # Step 1: replace **Closing:** line
    text = draft_path.read_text(encoding="utf-8")
    new_text, err = _replace_closing_line(text, closing_text)
    if err:
        print(f"CLOSE: closing FAIL — {err}")
        return 1
    draft_path.write_text(new_text, encoding="utf-8")
    print("CLOSE: closing OK")
    after_step("closing")

    # Step 2: fold_check --save-baseline
    rc, out = run_checker("fold_check.py", "--save-baseline", str(draft_path))
    if rc != 0:
        print(f"CLOSE: baseline FAIL — fold_check exit {rc}")
        return 1
    print("CLOSE: baseline OK")
    after_step("baseline")

    # Step 3: cycle_check --emit-manifest (captured)
    rc, emit_out = run_checker("cycle_check.py", "--emit-manifest", str(draft_path))
    if rc != 0:
        print(f"CLOSE: emit FAIL — cycle_check exit {rc}")
        return 1
    print("CLOSE: emit OK")
    after_step("emit")

    # Step 4: splice by key
    text = draft_path.read_text(encoding="utf-8")
    new_text, err = _splice_keys(text, emit_out)
    if err:
        print(f"CLOSE: splice FAIL — {err}")
        return 1
    draft_path.write_text(new_text, encoding="utf-8")
    print("CLOSE: splice OK")
    after_step("splice")

    # Step 5: fold_check --save-baseline (again)
    rc, out = run_checker("fold_check.py", "--save-baseline", str(draft_path))
    if rc != 0:
        print(f"CLOSE: baseline FAIL — fold_check exit {rc}")
        return 1
    print("CLOSE: baseline OK")
    after_step("baseline")

    # Step 6: STORED == LIVE — re-emit and compare; one re-splice when only propagation_check moved
    rc, live_out = run_checker("cycle_check.py", "--emit-manifest", str(draft_path))
    stored_val = None
    live_val = None
    for ln in draft_path.read_text(encoding="utf-8").splitlines():
        if ln.startswith("validation: "):
            stored_val = ln
            break
    for ln in live_out.splitlines():
        if ln.startswith("validation: "):
            live_val = ln
            break
    if stored_val != live_val:
        s_tok = _parse_validation_tokens(stored_val or "")
        l_tok = _parse_validation_tokens(live_val or "")
        diff_keys = {k for k in (s_tok.keys() | l_tok.keys()) if s_tok.get(k) != l_tok.get(k)}
        if s_tok.keys() == l_tok.keys() and diff_keys == {"propagation_check"}:
            s_pc = s_tok["propagation_check"].split("=", 1)[1]
            l_pc = l_tok["propagation_check"].split("=", 1)[1]
            print(
                f"CLOSE: stored==live NOTE — propagation_check moved {s_pc}→{l_pc}"
                f" (the spliced lines are counted); re-splicing once"
            )
            text = draft_path.read_text(encoding="utf-8")
            new_text, err = _splice_keys(text, live_out)
            if err:
                print(f"CLOSE: stored==live FAIL — re-splice error: {err}")
                return 1
            draft_path.write_text(new_text, encoding="utf-8")
            rc2, _ = run_checker("fold_check.py", "--save-baseline", str(draft_path))
            if rc2 != 0:
                print(f"CLOSE: stored==live FAIL — baseline after re-splice exit {rc2}")
                return 1
            rc2, live_out2 = run_checker("cycle_check.py", "--emit-manifest", str(draft_path))
            stored_val2 = None
            live_val2 = None
            for ln in draft_path.read_text(encoding="utf-8").splitlines():
                if ln.startswith("validation: "):
                    stored_val2 = ln
                    break
            for ln in live_out2.splitlines():
                if ln.startswith("validation: "):
                    live_val2 = ln
                    break
            if stored_val2 != live_val2:
                print(f"CLOSE: stored==live FAIL — stored {stored_val2!r} != live {live_val2!r}")
                return 1
        else:
            print(f"CLOSE: stored==live FAIL — stored {stored_val!r} != live {live_val!r}")
            return 1
    print("CLOSE: stored==live OK")
    after_step("stored==live")

    # Step 7: battery
    failures = _run_battery(draft_path, register_path, git_plan=git_plan)
    if failures:
        for f in failures:
            print(f"CLOSE: battery FAIL — {f}")
        return 1
    print("CLOSE: battery OK")
    after_step("battery")

    # Compose subject from the stored emitter output (step 3)
    subject = _compose_subject(draft_path, emit_out)

    # Step 8: commit (or skip)
    if do_commit and not dry_run:
        # Seal the register with a closing marker so it appears in the commit tree
        if register_path:
            walks = "?"
            tier = "?"
            for ln in emit_out.splitlines():
                if ln.startswith("walks: "):
                    walks = ln[len("walks: "):].strip()
                elif ln.startswith("tier: "):
                    tier = ln[len("tier: "):].strip()
            seal = f"\n<!-- cycle-close: WARM walk {walks} ({tier}) -->\n"
            register_path.write_text(
                register_path.read_text(encoding="utf-8") + seal, encoding="utf-8"
            )

        repo_dir = draft_path.parent
        to_add = [str(draft_path.resolve())]
        if register_path:
            to_add.append(str(register_path.resolve()))
        bpath = _baseline_path(draft_path)
        if bpath.is_file():
            to_add.append(str(bpath.resolve()))

        r = subprocess.run(
            ["git", "-C", str(repo_dir), "add"] + to_add,
            capture_output=True, text=True,
        )
        if r.returncode != 0:
            print(f"CLOSE: commit FAIL — git add: {r.stderr.strip()}")
            return 1
        r = subprocess.run(
            ["git", "-C", str(repo_dir), "commit", "-m", subject],
            capture_output=True, text=True,
        )
        if r.returncode != 0:
            print(f"CLOSE: commit FAIL — git commit: {r.stderr.strip()}")
            return 1
        print(f"CLOSE: commit OK — {subject}")
        after_step("commit")
    else:
        print(f"CLOSE: commit(skipped) OK")
        after_step("commit")

    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[1].strip())
    ap.add_argument("draft", help="Path to the draft plan file")
    ap.add_argument("--closing-file", required=True,
                    help="Text file whose content replaces the **Closing:** line")
    ap.add_argument("--register", default=None, help="Walk register path")
    ap.add_argument("--commit", action="store_true", help="Commit after completion")
    ap.add_argument("--dry-run", action="store_true",
                    help="Run steps 1–7 on temp copies; touch nothing")
    ap.add_argument("--git-plan", default=None,
                    help="Path used for lens_order_check in --dry-run (must be inside a git "
                         "repo with lens commits; defaults to draft)")
    args = ap.parse_args(argv)

    draft_path = Path(args.draft)
    closing_file = Path(args.closing_file)
    register_path = Path(args.register) if args.register else None
    git_plan_override = Path(args.git_plan) if args.git_plan else None

    if not draft_path.is_file():
        print(f"ERROR: draft not found: {draft_path}", file=sys.stderr)
        return 1
    if not closing_file.is_file():
        print(f"ERROR: closing file not found: {closing_file}", file=sys.stderr)
        return 1

    closing_text = closing_file.read_text(encoding="utf-8").rstrip("\n")

    if args.dry_run:
        tmp_dir = tempfile.mkdtemp()
        try:
            draft_copy = Path(tmp_dir) / draft_path.name
            shutil.copy2(draft_path, draft_copy)
            # Strip fold_baseline: declarations from the copy. A declared path resolves
            # to the live (post-splice) governance baseline, which causes fold_check to
            # return DRIFT in step 3 because the plan content is pre-splice. Without the
            # declaration, resolve_fold_baseline falls through to the beside-the-plan
            # baseline saved by step 2, which is always VACUOUS (content == baseline).
            _strip_field(draft_copy, "fold_baseline")
            reg_copy = None
            if register_path:
                reg_copy = Path(tmp_dir) / register_path.name
                shutil.copy2(register_path, reg_copy)
            # Set up a minimal git repo so cycle_check can resolve the walk register ref.
            for cmd in [
                ["git", "-C", tmp_dir, "init", "-q"],
                ["git", "-C", tmp_dir, "config", "user.name", "dryrun"],
                ["git", "-C", tmp_dir, "config", "user.email", "dryrun@localhost"],
            ]:
                subprocess.run(cmd, capture_output=True)
            to_stage = [str(draft_copy)]
            if reg_copy:
                to_stage.append(str(reg_copy))
            subprocess.run(["git", "-C", tmp_dir, "add"] + to_stage, capture_output=True)
            subprocess.run(["git", "-C", tmp_dir, "commit", "-qm", "dryrun-fixture"],
                           capture_output=True)
            return _run_close(draft_copy, closing_text, reg_copy,
                              do_commit=False, dry_run=True,
                              git_plan=git_plan_override or draft_path)
        finally:
            shutil.rmtree(tmp_dir, ignore_errors=True)
    else:
        return _run_close(draft_path, closing_text, register_path,
                          do_commit=args.commit, dry_run=False)


if __name__ == "__main__":
    sys.exit(main())
