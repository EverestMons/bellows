"""Fork-1 claim shim — mode-gated global claim in the claim block, R4a completion-release.

Rulings: knowledge/research/fork1-claim-lock-rulings-2026-08-26.md (tuyere repo).
Seam contract (exec-100001): python -m tuyere.claims claim <slug> --plan-class <c>
  exit 0 = claimed, 3 = held, 4 = ineligible (class OR project), other = error;
  release <slug> --reason <r>: 0 = released, 3 = no-active-claim.
R4a mandate: completion-release at every terminal transition.
"""

import datetime as _dt
import json
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
    # ROOT is the PROJECTS PARENT here (root / "tuyere", root / "lessons-forge"):
    # the shop root doubled as both; on every other layout they differ. The env
    # override keeps its documented precedence; only the shop literal is replaced.
    try:
        from bellows_root import resolve_projects_parent as _resolve_pp
        _pp = _resolve_pp()
    except Exception:
        _pp = Path.home() / "Developer"
    root = Path(os.environ.get("ELUVIAN_WRAP_ROOT") or _pp)
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


def claim_for_deposit(base_filename, content_hash, config, project=None):
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
    # PART A IS TOLERANT BY DESIGN. An un-updated machine omits --project and
    # the CLI records NULL; a strict CLI shipped ahead of its producers would
    # disable the claim path everywhere. The tolerance is DELETED, not relaxed,
    # by part B — and only once every machine produces.
    if project:
        cmd += ["--project", project]
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


def claim_gate(base_filename, content_hash, config, log, project=None):
    """Wire API: returns True to proceed, False to stop."""
    outcome, detail = claim_for_deposit(base_filename, content_hash, config, project)
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
        # Branch on the decline's stated CAUSE, not the bare exit code.
        # exit 3 now means EITHER a slug already claimed by this machine (a
        # genuine self-strand, recoverable by releasing that slug) OR a PROJECT
        # held by another machine — where this machine holds no claim on that
        # slug at all, and following the hint would release someone else's
        # claim. tuyere prints "held: project '<key>'" for the project arm and
        # "held: '<slug>'" for the slug arm.
        if detail.startswith("exit 3:") and "held: project " not in detail:
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


def enqueue_thread_reviews(plan_id, plan_path, config, log=None):
    """Thread 80 — one tuyere review INTENT per `**Discharges:** thread N` id.

    CEO decisions 2026-09-06: the review item is an INTENT, so it goes through the
    standard workflow; and an enqueue failure FAILS OPENLY.

    ⛔ FAILING OPENLY IS NOT LOGGING. `release_for_plan` above logs its failure ONCE
    — a module-global `_release_errored` suppresses every later one — which is how a
    failure gets swept under the rug. This writes a DURABLE artefact into
    `receipts/` instead, and `wrap_check` already blocks the wrap on uncommitted
    files there. A lost reminder is worse than no reminder, because the reader stops
    expecting to check by hand.

    It does NOT hold the plan's close: holding a completed plan over a bookkeeping
    fault is a large consequence for a small one. The artefact is the guarantee.

    Nothing auto-closes a thread. The intent asks "close it?" and the CEO answers.
    """
    if log is None:
        log = _default_log
    try:
        text = Path(plan_path).read_text(encoding="utf-8", errors="replace")
    except Exception as e:
        log("ERROR", f"enqueue_thread_reviews: cannot read {plan_path}: {e}")
        return
    try:
        import gates
        ids, residue = gates.parse_discharges(text)
    except Exception as e:
        log("ERROR", f"enqueue_thread_reviews: parse failed: {e}")
        return
    if not ids:
        return                      # field absent or empty — optional by design

    checkout = _tuyere_checkout()
    slug = Path(plan_path).stem
    failed = []
    for tid in ids:
        note = (f"plan {plan_id} Done ({slug}); declared to discharge thread {tid} "
                f"— close it?")
        if checkout is None:
            failed.append((tid, "tuyere checkout unresolvable"))
            continue
        try:
            r = subprocess.run(
                [str(checkout / ".venv" / "bin" / "python"), "-m", "tuyere.enqueue",
                 "intent", "thread.review-discharge",
                 "--target", json.dumps({"thread": tid, "plan_id": plan_id, "slug": slug}),
                 "--note", note],
                capture_output=True, text=True, timeout=15,
            )
            if r.returncode != 0:
                failed.append((tid, (r.stderr or r.stdout).strip()[:160] or f"exit {r.returncode}"))
            else:
                log("EVENT", f"thread {tid}: review intent enqueued for {slug}")
        except Exception as e:
            failed.append((tid, f"{type(e).__name__}: {e}"))

    if failed:
        _record_unenqueued_reviews(plan_id, slug, failed, log)


def _record_unenqueued_reviews(plan_id, slug, failed, log):
    """Write the failure where the WRAP will find it — receipts/ is wrap-checked."""
    for tid, detail in failed:
        log("ERROR", f"thread {tid}: review intent NOT enqueued for {slug} — {detail}")
    try:
        root = Path(__file__).resolve().parent
        d = root / "receipts"
        d.mkdir(exist_ok=True)
        stamp = _dt.datetime.now().strftime("%Y%m%dT%H%M%S")
        f = d / f"unenqueued-thread-review-{slug}-{stamp}.md"
        body = [
            f"# UNENQUEUED THREAD REVIEW — plan {plan_id} ({slug})",
            "",
            "⛔ This plan declared `**Discharges:**` and the review intent(s) could NOT",
            "be enqueued. The plan's close was NOT held (thread 80: report, do not hold),",
            "so this file is the ONLY durable record — it exists so the failure is not",
            "swept under the rug. `wrap_check` blocks the wrap while it is uncommitted.",
            "",
            "**To discharge:** enqueue the intent by hand, or close the thread at the",
            "keyboard, then commit this file with what you did.",
            "",
        ]
        for tid, detail in failed:
            body.append(f"- thread **{tid}** — {detail}")
        f.write_text("\n".join(body) + "\n", encoding="utf-8")
        log("ERROR", f"wrote {f.name} — the wrap will block until it is committed")
    except Exception as e:
        log("ERROR", f"could not even record the unenqueued reviews: {e}")
