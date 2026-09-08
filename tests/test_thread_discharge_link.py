"""Thread 80 — the declared plan→thread link, and its failure record.

CEO decisions 2026-09-06: the review item is an INTENT (standard workflow); an
enqueue failure FAILS OPENLY; direct-edit self-repair work is exempt on principle.
"""
import json
import re
import subprocess
import sys
from pathlib import Path

import pytest

BELLOWS_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BELLOWS_ROOT))
sys.path.insert(0, str(BELLOWS_ROOT / "scripts"))

import gates  # noqa: E402
import plan_claim  # noqa: E402

LINT = str(BELLOWS_ROOT / "scripts" / "plan_lint.py")


# ---- the parser -----------------------------------------------------------

def _plan(field):
    """A REAL plan header — pipe-separated on ONE line, which is where the field
    actually lives. The first cut of the parser used a `^**Discharges:**` line
    matcher and missed every inline header; the fixture that would have caught it
    put the field on its own line."""
    return f"# t\n\n**Date:** 2026-09-06 | **Project:** bellows | {field}\n\n## STEP 1 — do it\n"


@pytest.mark.parametrize("field,ids,clean", [
    ("**Discharges:** thread 80", [80], True),
    ("**Discharges:** thread 75, thread 73", [75, 73], True),
    ("**Discharges:** thread 75,thread 73", [75, 73], True),
    ("**Discharges:** threads 75 and 73", [], False),      # loose plural form REFUSED
    ("**Discharges:** the register work", [], False),
    ("**Discharges:**", [], True),
])
def test_parse_discharges_is_strict(field, ids, clean):
    """⛔ Integer ids, exact match. Thread 80 names the hazard by example — the
    scope_check ancestor-dir class, a match loose enough to hit what nobody meant.
    A link that silently resolves to the WRONG thread is worse than no link."""
    got_ids, residue = gates.parse_discharges(_plan(field))
    assert got_ids == ids, (got_ids, residue)
    assert (residue == "") is clean, residue


def test_the_field_is_found_in_an_INLINE_pipe_header(tmp_path):
    """⛔ THE REGRESSION THIS COST. A plan header is pipe-separated on ONE line, so
    `**Discharges:**` never starts a line. A line-anchored matcher finds nothing, and
    end-to-end verification is what exposed it — the unit fixtures all put the field
    on its own line and passed."""
    inline = ("# t\n\n**Date:** 2026-09-06 | **Project:** bellows | "
              "**Discharges:** thread 80, thread 75\n\n## STEP 1\n")
    assert gates.parse_discharges(inline) == ([80, 75], "")


def test_the_field_is_also_found_on_its_own_bold_line():
    own = "# t\n\n**Date:** 2026-09-06\n**Discharges:** thread 80\n\n## STEP 1\n"
    assert gates.parse_discharges(own) == ([80], "")


def test_absent_field_is_not_an_error():
    """Presence-OPTIONAL, the (f-stanza) precedent."""
    assert gates.parse_discharges(_plan("**Project:** bellows")) == (None, None)


def test_one_parser_serves_both_consumers():
    """⛔ plan_lint (g) and the close hook must not each carry a copy. Two parsers
    diverge the moment one moves — measured 2026-09-06, when a register resolver
    gained a step in one consumer and the other kept reporting the file unresolvable."""
    src = (BELLOWS_ROOT / "scripts" / "plan_lint.py").read_text()
    assert "gates.parse_discharges" in src
    assert "_DISCHARGES_ID_RE" not in src, "plan_lint grew its own copy of the parser"
    g = (BELLOWS_ROOT / "gates.py").read_text()
    assert "_DISCHARGES_LINE_RE" not in g, (
        "gates grew a SECOND matcher beside _parse_plan_header — the field is a header "
        "field and the header parser already extracts it")
    pc = (BELLOWS_ROOT / "plan_claim.py").read_text()
    assert "gates.parse_discharges" in pc
    assert "_DISCHARGES_ID_RE" not in pc, "plan_claim grew its own copy of the parser"


# ---- plan_lint (g) --------------------------------------------------------

def _lint(tmp_path, field):
    p = tmp_path / "executable-t.md"
    p.write_text(f"# t\n\n**Date:** 2026-09-06 | **Project:** bellows\n\n{field}\n\n## STEP 1 — do it\n")
    return subprocess.run([sys.executable, LINT, str(p)], capture_output=True, text=True, timeout=60)


def test_g_reports_the_ids_it_will_enqueue(tmp_path):
    r = _lint(tmp_path, "**Discharges:** thread 80, thread 75")
    assert "(g) INFO" in r.stdout
    assert "80, 75" in r.stdout
    assert "nothing auto-closes" in r.stdout


def test_g_warns_on_a_form_it_cannot_parse(tmp_path):
    r = _lint(tmp_path, "**Discharges:** threads 80 and 75")
    assert "(g) WARN" in r.stdout, r.stdout


def test_g_is_silent_when_the_field_is_absent(tmp_path):
    r = _lint(tmp_path, "")
    assert "(g)" not in r.stdout, r.stdout


def test_g_never_fails_the_lint(tmp_path):
    """Warn-first. The link is bookkeeping; it must not block a deposit."""
    r = _lint(tmp_path, "**Discharges:** threads 80 and 75")
    assert "FAIL: (g)" not in r.stdout


# ---- the failure record: Mark's constraint --------------------------------

def test_an_enqueue_failure_writes_a_DURABLE_record(tmp_path, monkeypatch):
    """⛔ FAILING OPENLY IS NOT LOGGING. release_for_plan logs its failure ONCE — a
    module-global suppresses every later one. This must leave an artefact in
    receipts/, which wrap_check already blocks the wrap on while uncommitted."""
    plan = tmp_path / "executable-fixture.md"
    plan.write_text("# t\n\n**Discharges:** thread 80\n")
    monkeypatch.setattr(plan_claim, "_tuyere_checkout", lambda: None)   # force failure
    receipts = BELLOWS_ROOT / "receipts"
    before = set(receipts.glob("unenqueued-thread-review-*"))
    logs = []
    plan_claim.enqueue_thread_reviews(999, plan, {"x": 1}, lambda lvl, m, **k: logs.append((lvl, m)))
    after = set(receipts.glob("unenqueued-thread-review-*"))
    new = after - before
    try:
        assert new, "no durable record was written — the failure would be lost"
        body = next(iter(new)).read_text()
        assert "thread **80**" in body
        assert "was NOT held" in body, "the record must say the close was not held"
        assert any(l == "ERROR" for l, _ in logs), logs
    finally:
        for f in new:
            f.unlink()


def test_no_declared_threads_writes_nothing(tmp_path, monkeypatch):
    plan = tmp_path / "executable-fixture.md"
    plan.write_text("# t\n\nno field here\n")
    monkeypatch.setattr(plan_claim, "_tuyere_checkout", lambda: None)
    receipts = BELLOWS_ROOT / "receipts"
    before = set(receipts.glob("unenqueued-thread-review-*"))
    plan_claim.enqueue_thread_reviews(999, plan, {"x": 1}, lambda *a, **k: None)
    assert set(receipts.glob("unenqueued-thread-review-*")) == before


def test_the_enqueue_subprocess_runs_from_the_tuyere_checkout(tmp_path, monkeypatch):
    """⛔ `-m tuyere.enqueue` resolves the package from cwd — tuyere is not installed
    into its venv — and the daemon's cwd is bellows. The first live close to carry a
    Discharges field (plan 100039, 2026-09-07) failed openly on exactly this:
    ModuleNotFoundError: No module named 'tuyere'. release_for_plan already passed
    cwd; this pins its sibling to the same rule (thread 187)."""
    plan = tmp_path / "executable-fixture.md"
    plan.write_text("# t\n\n**Discharges:** thread 80\n")
    checkout = tmp_path / "tuyere"
    monkeypatch.setattr(plan_claim, "_tuyere_checkout", lambda: checkout)
    seen = []
    def fake_run(cmd, **kw):
        seen.append((cmd, kw))
        return subprocess.CompletedProcess(cmd, 0, stdout="intent 1\n", stderr="")
    monkeypatch.setattr(plan_claim.subprocess, "run", fake_run)
    logs = []
    plan_claim.enqueue_thread_reviews(999, plan, {"x": 1}, lambda lvl, m, **k: logs.append((lvl, m)))
    assert len(seen) == 1, seen
    cmd, kw = seen[0]
    assert kw.get("cwd") == str(checkout), kw
    assert cmd[:3] == [str(checkout / ".venv" / "bin" / "python"), "-m", "tuyere.enqueue"]
    assert any(l == "EVENT" for l, _ in logs), logs


# ---- transitions ----------------------------------------------------------

def test_only_completion_transitions_enqueue():
    """⛔ Four of the seven release_for_plan sites are halts or aborts, which have
    discharged nothing. Zero-step skip is excluded on a second ground: thread 19
    records that path as leaking receipts and lifecycle state already."""
    src = (BELLOWS_ROOT / "bellows.py").read_text()
    calls = [ln for ln in src.split("\n") if "enqueue_thread_reviews" in ln]
    assert len(calls) == 2, calls
    for ln in calls:
        i = src.index(ln)
        window = src[max(0, i - 400):i]
        assert "completion:" in window, f"enqueue wired at a non-completion transition: {ln.strip()}"
        assert "zero-step skip" not in window, "wired at the zero-step path (thread 19)"


# --- thread 167: a residue that survives its own words -------------------------

def _hdr(field):
    return f"# T\n\n**Date:** 2026-09-07 | **Discharges:** {field} | **cycle_tier:** T1\n"


def test_discharges_residue_keeps_words_containing_and():
    """`.replace("and", " ")` was UNANCHORED and ate those letters inside words.

    Measured on a live plan: "command half only" came back as "comm  half only".
    """
    _ids, residue = gates.parse_discharges(
        _hdr("thread 7 — standard handling, understand the brand")
    )
    for word in ("standard", "handling", "understand", "brand"):
        assert word in residue, f"{word!r} corrupted; residue={residue!r}"


def test_discharges_strictness_is_preserved_by_the_residue_fix():
    """⛔ REGRESSION GUARD on a RATIFIED refusal, not on a defect.

    The loose plural form is refused BY DESIGN and plan_lint (g) warns on it.
    A 2026-09-07 attempt to "fix" that refusal as if it were a silent failure was
    caught by test_parse_discharges_is_strict and reverted; this pins the boundary
    beside the residue change so the next reader meets the ruling, not the itch.
    """
    ids, _ = gates.parse_discharges(_hdr("threads 75 and 73"))
    assert ids == [], "the loose plural form is REFUSED by design"
    ids2, _ = gates.parse_discharges(_hdr("thread 75, thread 73"))
    assert ids2 == [75, 73], "the sanctioned repeated-singular form must still parse"
