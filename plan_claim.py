"""Fork-1 claim shim — mode-gated global claim in the claim block, R4a completion-release.

Rulings: knowledge/research/fork1-claim-lock-rulings-2026-08-26.md (tuyere repo).
Seam contract (exec-100001): python -m tuyere.claims claim <slug> --plan-class <c>
  exit 0 = claimed, 3 = held, 4 = class-ineligible, other = error;
  release <slug> --reason <r>: 0 = released, 3 = no-active-claim.
R4a mandate: completion-release at every terminal transition.
"""

import logging
import os
import subprocess
import sys
from pathlib import Path

import lifecycle

logger = logging.getLogger("bellows")

_outcome_memo = {}
_release_errored = False


def _default_log(level, msg, **kwargs):
    print(f"[plan_claim] {level}: {msg}", file=sys.stderr)


def _reset_memo():
    global _release_errored
    _outcome_memo.clear()
    _release_errored = False


def _tuyere_checkout():
    """Resolve the tuyere checkout path. Named twin of wrap_check._tuyere_checkout."""
    candidates = []
    env_override = os.environ.get("ELUVIAN_WRAP_TUYERE")
    if env_override:
        candidates.append(Path(env_override))
    candidates.append(Path.home() / "Developer" / "tuyere")
    root = Path(os.environ.get("ELUVIAN_WRAP_ROOT") or "/Users/marklehn/Developer/GitHub")
    candidates.append(root / "tuyere")
    for p in candidates:
        if (p / ".venv" / "bin" / "python").exists():
            return p
    return None


def _mode(config):
    val = config.get("plan_claim_lock", "off") if config else "off"
    if val in ("off", "advisory", "required"):
        return val
    logger.warning(f"plan_claim_lock: unrecognized value {val!r} — treating as required")
    return "required"


def claim_for_deposit(base_filename, content_hash, config):
    """Returns (outcome, detail) where outcome in {proceed, declined, blocked}."""
    mode = _mode(config)
    if mode == "off":
        return ("proceed", "mode-off: partition safety governs")

    slug = base_filename[:-3]
    cls = lifecycle.active_clearance_class(content_hash, base_filename)
    if cls is None:
        detail = "no active clearance class for this deposit"
        if mode == "advisory":
            return ("proceed", f"ADVISORY-ERROR: {detail} — proceeding under partition")
        return ("blocked", detail)

    checkout = _tuyere_checkout()
    if checkout is None:
        detail = "tuyere checkout unresolvable"
        if mode == "advisory":
            return ("proceed", f"ADVISORY-ERROR: {detail} — proceeding under partition")
        return ("blocked", detail)

    cmd = [
        str(checkout / ".venv" / "bin" / "python"),
        "-m", "tuyere.claims", "claim", slug,
        "--plan-class", cls,
    ]
    try:
        result = subprocess.run(
            cmd, cwd=str(checkout), timeout=10,
            capture_output=True, text=True, errors="replace",
        )
        rc = result.returncode
        if rc == 0:
            stdout_line = (result.stdout.strip().splitlines() or [""])[0]
            return ("proceed", stdout_line)
        if rc in (3, 4):
            lines = result.stdout.strip().splitlines() + result.stderr.strip().splitlines()
            first_nonempty = next((l for l in lines if l.strip()), "")
            return ("declined", f"exit {rc}: {first_nonempty}")
        detail = f"exit {rc}: {result.stderr.strip() or result.stdout.strip()}"
    except subprocess.TimeoutExpired:
        detail = "timeout (10s)"
    except Exception as e:
        detail = str(e)

    if mode == "advisory":
        return ("proceed", f"ADVISORY-ERROR: {detail} — proceeding under partition")
    return ("blocked", detail)


def claim_gate(base_filename, content_hash, config, log):
    """Wire API: returns True to proceed, False to stop."""
    outcome, detail = claim_for_deposit(base_filename, content_hash, config)
    slug = base_filename[:-3]

    if outcome == "proceed":
        if detail.startswith("ADVISORY-ERROR:"):
            log("WARN", f"claim lock advisory error for {slug}: {detail}", slug=slug)
        return True

    last = _outcome_memo.get(slug)
    if last == outcome:
        return False
    _outcome_memo[slug] = outcome

    if outcome == "declined":
        hint = ""
        if detail.startswith("exit 3:"):
            hint = (f" — if the holder is this machine this is a stranded claim"
                    f" — recover: tuyere.claims release {slug} --reason self-strand")
        log("WARN", f"claim declined for {slug}: {detail}{hint}", slug=slug)
    elif outcome == "blocked":
        log("ERROR", f"claim blocked for {slug}: {detail}", slug=slug)

    return False


def release_for_plan(plan_id, reason, config, log=None):
    """R4a completion-release — NOT mode-gated, best-effort, fail-open."""
    global _release_errored
    if log is None:
        log = _default_log

    if config is None or plan_id is None:
        log("INFO", f"release_for_plan: skipping (config={config is not None}, plan_id={plan_id})")
        return

    checkout = _tuyere_checkout()
    if checkout is None:
        log("INFO", "release_for_plan: tuyere checkout unresolvable — skipping")
        return

    placeholder = lifecycle.deposit_placeholder(plan_id)
    if placeholder is None:
        log("INFO", f"release_for_plan: no placeholder for plan_id={plan_id} — skipping")
        return

    slug = placeholder[:-3] if placeholder.endswith(".md") else placeholder

    cmd = [
        str(checkout / ".venv" / "bin" / "python"),
        "-m", "tuyere.claims", "release", slug,
        "--reason", reason,
    ]
    try:
        result = subprocess.run(
            cmd, cwd=str(checkout), timeout=10,
            capture_output=True, text=True, errors="replace",
        )
        rc = result.returncode
        if rc == 0:
            _release_errored = False
            log("INFO", f"released claim for {slug}: {result.stdout.strip()}")
            return
        if rc == 3:
            log("INFO", f"release_for_plan: no active claim for {slug} (rc=3, normal)")
            return
        detail = f"exit {rc}: {result.stderr.strip() or result.stdout.strip()}"
    except subprocess.TimeoutExpired:
        detail = "timeout (10s)"
    except Exception as e:
        detail = str(e)

    if not _release_errored:
        log("ERROR", f"release_for_plan failed for {slug}: {detail}")
        _release_errored = True
