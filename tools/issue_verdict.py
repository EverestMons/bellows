#!/usr/bin/env python3
"""Issue a verdict for a paused plan step — the tool-mediated verdict act.

Writes a well-formed verdict file to verdicts/resolved/ with location and
grammar correct by construction. Replaces the bare-handed manual write.
"""

import argparse
import os
import re
import sys
import tempfile
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_BELLOWS_ROOT = _HERE.parent
_DEFAULT_PENDING = _BELLOWS_ROOT / "verdicts" / "pending"
_DEFAULT_RESOLVED = _BELLOWS_ROOT / "verdicts" / "resolved"

# Cloned from verdict.py::VERDICT_FIRST_LINE_RE — byte-identity pinned by test
_VERDICT_RE = re.compile(r"^(?:verdict:\s*)?(continue|stop)$", re.IGNORECASE)

_CONSUME_FILENAME_RE = re.compile(r"^verdict-(.+)-step-(\d+)\.md$")
_REQUEST_FILENAME_RE = re.compile(r"^verdict-request-(.+)-step-(\d+)\.md$")


def _fail(msg):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(1)


def _normalize_slug(raw):
    """Strip diagnostic-/executable- prefix (Y4 normalization)."""
    for prefix in ("diagnostic-", "executable-"):
        if raw.startswith(prefix):
            return raw[len(prefix):]
    return raw


def _find_request(pending_dir, slug, step):
    """Find matching verdict-request files by string equality on normalized slug."""
    normalized = _normalize_slug(slug)
    matches = []
    if not pending_dir.is_dir():
        return matches
    for fname in os.listdir(pending_dir):
        m = _REQUEST_FILENAME_RE.match(fname)
        if not m:
            continue
        req_slug = m.group(1)
        req_step = int(m.group(2))
        if req_slug == normalized and req_step == step:
            matches.append(fname)
    return matches


def issue_verdict(plan_id_or_slug, step, outcome, reason, force=False,
                  pending_dir=None, resolved_dir=None):
    pending = Path(pending_dir) if pending_dir else _DEFAULT_PENDING
    resolved = Path(resolved_dir) if resolved_dir else _DEFAULT_RESOLVED

    if pending_dir and not pending.is_dir():
        _fail(f"--pending-dir does not exist: {pending}")
    if resolved_dir and not resolved.is_dir():
        _fail(f"--resolved-dir does not exist: {resolved}")

    outcome_lower = outcome.lower()
    if outcome_lower not in ("continue", "stop"):
        print(f"ERROR: outcome must be one of: continue, stop (got: {outcome!r})", file=sys.stderr)
        sys.exit(1)

    if not reason or not reason.strip():
        _fail("reason is required — a verdict without reasoning is not issuable. "
              "Provide via --reason TEXT, --reason-file PATH, or pipe to stdin.")

    normalized_arg = _normalize_slug(plan_id_or_slug)
    matches = _find_request(pending, normalized_arg, step)

    if len(matches) == 0:
        all_requests = sorted(
            f for f in os.listdir(pending)
            if _REQUEST_FILENAME_RE.match(f)
        ) if pending.is_dir() else []
        print(f"ERROR: no verdict-request file found for slug={normalized_arg!r} step={step} in {pending}", file=sys.stderr)
        if all_requests:
            print("Available request files:", file=sys.stderr)
            for r in all_requests:
                print(f"  {r}", file=sys.stderr)
        else:
            print("No pending request files found.", file=sys.stderr)
        print("\nIf the request was already consumed, run tools/reconcile_plan.py "
              "<plan-id> ... (see its --help) for orphan-recovery.", file=sys.stderr)
        sys.exit(1)

    if len(matches) > 1:
        print(f"ERROR: multiple request files match slug={normalized_arg!r} step={step}:", file=sys.stderr)
        for r in matches:
            print(f"  {r}", file=sys.stderr)
        sys.exit(1)

    req_match = _REQUEST_FILENAME_RE.match(matches[0])
    matched_slug = req_match.group(1)

    target_name = f"verdict-{matched_slug}-step-{step}.md"
    target_path = resolved / target_name

    if target_path.exists() and not force:
        _fail(f"verdict file already exists (not consumed yet): {target_path} — use --force to overwrite")

    processed_name = f"processed-{target_name}"
    processed_path = resolved / processed_name
    if processed_path.exists():
        print(f"WARN: prior consumed verdict exists: {processed_path} — proceeding (new verdict)", file=sys.stderr)

    content = f"{outcome_lower}\n\n{reason.strip()}\n"

    resolved.mkdir(parents=True, exist_ok=True)
    tmp_path = None
    try:
        fd = tempfile.NamedTemporaryFile(
            dir=str(resolved), delete=False, mode='w', suffix='.tmp')
        tmp_path = fd.name
        fd.write(content)
        fd.flush()
        os.fsync(fd.fileno())
        fd.close()
        os.rename(tmp_path, str(target_path))
        os.chmod(str(target_path), 0o644)
    except Exception as e:
        if tmp_path and os.path.exists(tmp_path):
            try:
                os.unlink(tmp_path)
            except Exception:
                pass
        _fail(f"write failed: {e}")

    try:
        verify_text = target_path.read_text()
    except FileNotFoundError:
        if (resolved / processed_name).exists():
            print(f"verdict consumed by the daemon during self-verify: {target_name}")
            print(f"outcome: {outcome_lower}")
            print(f"file: {resolved / processed_name}")
            sys.exit(0)
        _fail(f"self-verify failed: file disappeared after write: {target_path}")

    verify_lines = verify_text.strip().splitlines()
    if not verify_lines:
        _fail(f"self-verify failed: file is empty after write: {target_path}")

    verify_first = verify_lines[0].strip()
    verify_match = _VERDICT_RE.match(verify_first)
    if not verify_match:
        _fail(f"self-verify failed: written file does not parse — first line: {verify_first!r}")

    print(f"outcome: {verify_match.group(1).lower()}")
    print(f"file: {target_path}")
    sys.exit(0)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Issue a verdict for a paused plan step")
    parser.add_argument("plan_id_or_slug",
                        help="plan id or slug (diagnostic-/executable- prefix optional)")
    parser.add_argument("step", type=int,
                        help="step number")
    parser.add_argument("outcome",
                        help="verdict outcome: continue or stop")

    reason_group = parser.add_mutually_exclusive_group()
    reason_group.add_argument("--reason", help="verdict reason text")
    reason_group.add_argument("--reason-file",
                              help="path to file containing reason text")

    parser.add_argument("--force", action="store_true",
                        help="overwrite existing unconsumed verdict file")
    parser.add_argument("--pending-dir",
                        help="pending verdicts directory (default: repo-resolved)")
    parser.add_argument("--resolved-dir",
                        help="resolved verdicts directory (default: repo-resolved)")

    args = parser.parse_args()

    if args.reason is not None:
        reason = args.reason
    elif args.reason_file is not None:
        try:
            reason = Path(args.reason_file).read_text()
        except Exception as e:
            print(f"ERROR: cannot read reason file: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        if sys.stdin.isatty():
            print("ERROR: no reason provided. Use --reason TEXT, --reason-file PATH, "
                  "or pipe reason text to stdin.", file=sys.stderr)
            sys.exit(1)
        reason = sys.stdin.read()

    issue_verdict(args.plan_id_or_slug, args.step, args.outcome, reason,
                  force=args.force, pending_dir=args.pending_dir,
                  resolved_dir=args.resolved_dir)
