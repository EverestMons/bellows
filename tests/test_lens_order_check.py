"""lens_order_check — the §2.7 observer (built 2026-09-06).

§2.7 appoints the per-lens commit as the mechanism that makes sequential execution
PROVABLE, "where the sequential-fold rule's wording alone was measurably unable to
prevent batched walks — the gap is an observer, not wording". The observer was never
built: cycle_check has no commit counting of any kind.

⛔ Every fixture is a REAL git repo under tmp_path. The tool reads history, so a
fixture that fakes the history tests nothing.
"""
import subprocess
import sys
from pathlib import Path

import pytest

BELLOWS_ROOT = Path(__file__).resolve().parent.parent
TOOL = str(BELLOWS_ROOT / "scripts" / "lens_order_check.py")


def _git(repo, *args):
    return subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True)


def _plan_text(tier="T1", walks=(1,)):
    # ⛔ The REAL Cycle Log shape, copied from a live plan: LENS-keyed lines carrying
    # `wN` tokens, not walk-keyed headings. cycle_check.parse_block derives the walk
    # numbers from those tokens, and an invented shape parses to zero walks — which
    # is how the first cut of this fixture silently tested nothing.
    per = "; ".join(f"w{w} 1 folded — instruction 1 / record 0" for w in walks)
    walk_lines = "\n".join(
        f"- {name}: {per}."
        for name in ("Weak spots", "Destruction", "Vulnerabilities",
                     "Integration-record", "ACID")
    )
    return f"""# bellows — executable: fixture

**Date:** 2026-09-06 | **Project:** bellows | **cycle_tier:** {tier}

## Drafting Cycle

**Tier:** {tier}
**Walks:** {len(walks)}
{walk_lines}
**Closing:** in progress.

## STEP 1 — do it
"""


def _repo(tmp_path, subjects, tier="T1", walks=(1,)):
    repo = tmp_path / "r"
    (repo / "knowledge" / "decisions" / "drafts").mkdir(parents=True)
    _git(repo.parent, "init", "-q", str(repo))
    _git(repo, "config", "user.email", "t@t")
    _git(repo, "config", "user.name", "T")
    plan = repo / "knowledge" / "decisions" / "drafts" / "executable-fixture.md"
    for i, subj in enumerate(subjects):
        plan.write_text(_plan_text(tier, walks) + f"\n<!-- rev {i} -->\n")
        _git(repo, "add", "-A")
        _git(repo, "commit", "-q", "-m", subj)
    return repo, plan


def _run(plan, repo):
    return subprocess.run([sys.executable, TOOL, str(plan), "--repo", str(repo)],
                          capture_output=True, text=True, timeout=60)


def test_batched_lenses_in_one_commit_is_a_breach(tmp_path):
    """The measured violation: `walk 2 LENS 2 + LENS 3` in a single commit."""
    repo, plan = _repo(tmp_path, [
        "draft(fix): walk 1 LENS 1 — 1 finding",
        "draft(fix): walk 1 LENS 2 + LENS 3 — 2 findings",
    ], walks=(1, 2))
    r = _run(plan, repo)
    assert r.returncode == 1, r.stdout
    assert "BATCHED" in r.stdout
    assert "lenses [2, 3] in ONE commit" in r.stdout


def test_lens_commits_out_of_order_is_a_breach(tmp_path):
    repo, plan = _repo(tmp_path, [
        "draft(fix): walk 1 LENS 3 — 1 finding",
        "draft(fix): walk 1 LENS 1 — 1 finding",
    ], walks=(1, 2))
    r = _run(plan, repo)
    assert r.returncode == 1, r.stdout
    assert "OUT-OF-ORDER" in r.stdout


def test_closed_walk_missing_lenses_is_INCOMPLETE(tmp_path):
    """'full walk cycle' — a CLOSED walk must carry its tier's whole lens set."""
    repo, plan = _repo(tmp_path, [
        "draft(fix): walk 1 LENS 1 — 0 findings",
        "draft(fix): walk 1 LENS 2 — 0 findings",
        "draft(fix): walk 2 LENS 1 — 0 findings",
    ], walks=(1, 2))
    r = _run(plan, repo)
    assert r.returncode == 1, r.stdout
    assert "INCOMPLETE: walk 1" in r.stdout
    assert "missing [3, 4, 5]" in r.stdout


def test_the_walk_in_progress_is_never_incomplete(tmp_path):
    """⛔ §2.7 requires the battery runnable mid-cycle. The furthest walk is being
    walked right now; flagging it would make the instrument fire on every cycle."""
    repo, plan = _repo(tmp_path, [
        f"draft(fix): walk 1 LENS {n} — 0 findings" for n in (1, 2, 3, 4, 5)
    ] + ["draft(fix): walk 2 LENS 1 — 0 findings"], walks=(1, 2))
    r = _run(plan, repo)
    assert r.returncode == 0, r.stdout
    assert "INCOMPLETE: walk 2" not in r.stdout


def test_T0_requires_lens_4_only(tmp_path):
    """DRAFTING_CYCLE §1: T0 runs 'the integration-vs-record pass only (Lens 4)'.
    Hardcoding five lenses would fail every T0 plan."""
    repo, plan = _repo(tmp_path, [
        "draft(fix): walk 1 LENS 4 — 0 findings",
        "draft(fix): walk 2 LENS 4 — 0 findings",
    ], tier="T0", walks=(1, 2))
    r = _run(plan, repo)
    assert r.returncode == 0, r.stdout
    assert "INCOMPLETE" not in r.stdout


def test_T1_would_fail_the_same_record(tmp_path):
    """The discriminating control for the tier arm — same commits, T1 instead."""
    repo, plan = _repo(tmp_path, [
        "draft(fix): walk 1 LENS 4 — 0 findings",
        "draft(fix): walk 2 LENS 4 — 0 findings",
    ], tier="T1", walks=(1, 2))
    r = _run(plan, repo)
    assert r.returncode == 1, r.stdout
    assert "INCOMPLETE: walk 1" in r.stdout


def test_declared_walks_with_no_lens_commit_REFUSES(tmp_path):
    """⛔ VACUITY. With zero lens commits the OK sentence would assert a proof that
    does not exist — the vacuous-verdict class. Exit 2: could not run, never a pass."""
    repo, plan = _repo(tmp_path, ["draft(fix): v0 — initial"], walks=(1, 2))
    r = _run(plan, repo)
    assert r.returncode == 2, r.stdout + r.stderr
    assert "NO-RECORD" in r.stderr
    assert "LENS-ORDER OK" not in r.stdout


def test_ok_message_states_its_basis(tmp_path):
    """A pass must say what it rests on, not just that it passed."""
    repo, plan = _repo(tmp_path, [
        f"draft(fix): walk 1 LENS {n} — 0 findings" for n in (1, 2, 3, 4, 5)
    ] + ["draft(fix): walk 2 LENS 1 — 0 findings"], walks=(1, 2))
    r = _run(plan, repo)
    assert r.returncode == 0
    assert "lens commit(s) across walks" in r.stdout
    assert "BASIS:" in r.stdout


def test_slash_notation_is_two_lenses_not_one(tmp_path):
    """⛔ `lens 1/4` is TWO lenses in one commit — the corpus uses this form.

    Reading only the first number turned a BATCHED commit into a compliant
    single-lens one: the exact breach the tool exists to catch, hidden by its own
    parser. Measured 2026-09-06: fixing it took the corpus BATCHED count 1 -> 5."""
    repo, plan = _repo(tmp_path, [
        "drafting(fix): walk 1 lens 1/4 — 3 instruction folds",
        "draft(fix): walk 2 LENS 1 — 0 findings",
    ], walks=(1, 2))
    r = _run(plan, repo)
    assert r.returncode == 1, r.stdout
    assert "BATCHED" in r.stdout
    assert "lenses [1, 4] in ONE commit" in r.stdout, r.stdout


def test_a_lens_passed_twice_in_one_walk_is_REPEATED(tmp_path):
    """§2: 'one pass per lens per walk … Re-run a lens only on a SUBSEQUENT walk.'"""
    repo, plan = _repo(tmp_path, [
        "draft(fix): walk 1 LENS 1 — 2 folds",
        "draft(fix): walk 1 LENS 2 — 1 fold",
        "draft(fix): walk 1 LENS 1 — more folds",
        "draft(fix): walk 2 LENS 1 — 0 findings",
    ], walks=(1, 2))
    r = _run(plan, repo)
    assert r.returncode == 1, r.stdout
    assert "REPEATED: walk 1" in r.stdout
    assert "lens [1] passed more than once" in r.stdout


def test_a_cont_commit_continues_one_pass_and_is_not_a_repeat(tmp_path):
    """`lens 3 (cont)` continues the SAME pass across two commits. One pass, so it
    is not a re-run — the distinction §2 draws between a pass and a subsequent walk."""
    repo, plan = _repo(tmp_path, [
        "draft(fix): walk 1 LENS 3 — three probe columns given",
        "draft(fix): walk 1 LENS 3 (cont) — every probe column assigned",
        "draft(fix): walk 2 LENS 1 — 0 findings",
    ], walks=(1, 2))
    r = _run(plan, repo)
    assert "REPEATED" not in r.stdout, r.stdout
