"""lens_order_check — the §2.7 observer (built 2026-09-06).

§2.7 appoints the per-lens commit as the mechanism that makes sequential execution
PROVABLE, "where the sequential-fold rule's wording alone was measurably unable to
prevent batched walks — the gap is an observer, not wording". The observer was never
built: cycle_check has no commit counting of any kind.

⛔ Every fixture is a REAL git repo under tmp_path. The tool reads history, so a
fixture that fakes the history tests nothing.
"""
import os
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
    # ⛔ Exit 1 since DRAFTING_CYCLE v2.26 (CEO ruling 2026-09-07, thread 177): a plan
    # that declares lens walks with no commit proving one is HELD. It was exit 2 —
    # "could not run" — while the observer was inert and NO-RECORD meant "cannot see".
    assert r.returncode == 1, r.stdout + r.stderr
    assert "NO-RECORD" in r.stdout
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


# --- threads 163 + 164 + 165: the WALK REGISTER is the record -------------------

def _repo_with_register(tmp_path, steps, walks=(1,), same_second=None):
    """A repo whose plan and walk register are committed SEPARATELY, IN ORDER.

    `steps` is an ordered list of (subject, target) where target is "plan" or "reg".
    ⚠️ The order is the point: lens passes happen in sequence regardless of WHICH
    file each one touches, and an earlier version of this helper committed every
    plan step before every register step — producing a genuine 1,3,5,2,4 sequence
    and a correct OUT-OF-ORDER that looked like a bug in the tool.
    """
    repo = tmp_path / "r"
    (repo / "knowledge" / "decisions" / "drafts").mkdir(parents=True)
    (repo / "knowledge" / "research").mkdir(parents=True)
    _git(repo.parent, "init", "-q", str(repo))
    _git(repo, "config", "user.email", "t@t")
    _git(repo, "config", "user.name", "T")
    plan = repo / "knowledge" / "decisions" / "drafts" / "executable-fixture.md"
    reg = repo / "knowledge" / "research" / "walk-register-fixture.md"
    body = _plan_text("T1", walks).replace(
        "**Walks:**",
        "**Walk register:** knowledge/research/walk-register-fixture.md\n**Walks:**")
    plan.write_text(body)
    reg.write_text("# Walk Register — fixture\n")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "seed")
    for i, (subj, target) in enumerate(steps):
        if target == "plan":
            plan.write_text(body + f"\n<!-- p{i} -->\n")
            _git(repo, "add", str(plan))
        else:
            reg.write_text(reg.read_text() + f"\nrow {i}\n")
            _git(repo, "add", str(reg))
        # ⚠️ EXPLICIT, INCREASING commit dates. `%cI` has SECOND resolution, so a
        # fixture that commits in a tight loop lands every commit in the same second
        # and the merged order falls back to insertion order — which made an earlier
        # version of this test read [1,3,5,2,4] and fail against correct code. Real
        # cycles are minutes apart; the fixture must not be tighter than reality.
        when = f"2026-09-07T10:{i:02d}:00-05:00"
        if same_second and i in same_second:      # force a shared commit second
            when = f"2026-09-07T10:{min(same_second):02d}:00-05:00"
        subprocess.run(
            ["git", "-C", str(repo), "commit", "-q", "-m", subj],
            capture_output=True, text=True,
            env={**os.environ, "GIT_AUTHOR_DATE": when, "GIT_COMMITTER_DATE": when})
    return repo, plan


def test_a_dry_lens_is_visible_through_the_register(tmp_path):
    """⛔ Thread 165. A DRY lens folds nothing into the plan, so it leaves no plan
    commit. Reading only the plan reported INCOMPLETE for a walk that ran all five —
    and since BAR_MET requires a dry walk, the observer was blind to exactly the
    closing walk a fabricated close would imitate."""
    repo, plan = _repo_with_register(tmp_path, [
        ("draft(f): walk 1 lens 1 — 1 fold", "plan"),
        ("draft(f): walk 1 lens 2 — DRY", "reg"),      # dry: register only
        ("draft(f): walk 1 lens 3 — 1 fold", "plan"),
        ("draft(f): walk 1 lens 4 — DRY", "reg"),      # dry: register only
        ("draft(f): walk 1 lens 5 — 1 fold", "plan"),
    ])
    r = _run(plan, repo)
    assert r.returncode == 0, r.stdout + r.stderr
    assert "LENS-ORDER OK" in r.stdout, r.stdout
    assert "source=plan+register" in r.stdout, r.stdout


def test_plan_only_would_have_reported_incomplete(tmp_path):
    """The negative control for the test above — without the register ref, the same
    three plan commits are all the record there is, and the walk IS incomplete."""
    repo, plan = _repo(tmp_path, [
        "draft(f): walk 1 lens 1 — 1 fold",
        "draft(f): walk 1 lens 3 — 1 fold",
        "draft(f): walk 1 lens 5 — 1 fold",
        "draft(f): walk 2 lens 1 — 1 fold",
    ], walks=(1, 2))
    r = _run(plan, repo)
    assert r.returncode == 1, r.stdout + r.stderr
    assert "INCOMPLETE" in r.stdout, r.stdout


def test_a_commit_touching_both_files_is_not_a_repeated_lens(tmp_path):
    """Dedupe is by FULL SHA. A commit touching plan AND register appears in both
    logs, and counting it twice would read as a REPEATED lens."""
    repo = tmp_path / "r"
    (repo / "knowledge" / "decisions" / "drafts").mkdir(parents=True)
    (repo / "knowledge" / "research").mkdir(parents=True)
    _git(repo.parent, "init", "-q", str(repo))
    _git(repo, "config", "user.email", "t@t")
    _git(repo, "config", "user.name", "T")
    plan = repo / "knowledge" / "decisions" / "drafts" / "executable-fixture.md"
    reg = repo / "knowledge" / "research" / "walk-register-fixture.md"
    body = _plan_text("T1", (1,)).replace(
        "**Walks:**", "**Walk register:** knowledge/research/walk-register-fixture.md\n**Walks:**")
    plan.write_text(body)
    reg.write_text("# Walk Register — fixture\n")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "seed")
    for lens in (1, 2, 3, 4, 5):
        plan.write_text(body + f"\n<!-- lens {lens} -->\n")
        reg.write_text(reg.read_text() + f"\nrow {lens}\n")
        _git(repo, "add", "-A")               # ONE commit, BOTH files
        _git(repo, "commit", "-q", "-m", f"draft(f): walk 1 lens {lens} — 1 fold")
    r = _run(plan, repo)
    assert r.returncode == 0, r.stdout + r.stderr
    assert "REPEATED" not in r.stdout, r.stdout
    assert "lens_commits=5" in r.stdout, r.stdout


def test_an_undeclared_walk_is_still_checked(tmp_path):
    """⛔ Thread 164 — the observer must not be defeated by SILENCE in the Cycle Log.

    The loop used to read `sorted(walks or per_walk)`, so a declared-walks set took
    precedence and the commit record was never consulted for WHICH walks to check.
    Measured on a live plan: deleting one walk's STATUS bullet returned NO FINDINGS
    while the commits proving that walk ran sat untouched in history — Ruling 119's
    "a gate reading a declaration is defeated by silence", reproduced inside the
    observer built to enforce lens order.

    Here the Cycle Log declares walks 1 and 3 only. Walk 2 HAS commits and is
    incomplete; walk 3 is the in-progress boundary and is exempt. A checker reading
    the declared set alone sees nothing wrong.
    """
    repo, plan = _repo(tmp_path, [
        "draft(f): walk 1 lens 1 — 1 fold", "draft(f): walk 1 lens 2 — 1 fold",
        "draft(f): walk 1 lens 3 — 1 fold", "draft(f): walk 1 lens 4 — 1 fold",
        "draft(f): walk 1 lens 5 — 1 fold",
        "draft(f): walk 2 lens 1 — 1 fold",          # walk 2: UNDECLARED, incomplete
        "draft(f): walk 3 lens 1 — 1 fold",          # walk 3: in progress, exempt
    ], walks=(1, 3))
    r = _run(plan, repo)
    assert r.returncode == 1, f"undeclared walk 2 was not checked\n{r.stdout}{r.stderr}"
    assert "INCOMPLETE: walk 2" in r.stdout, r.stdout


# --- same-second ties between a register-only lens and a plan-only lens -----------

def test_same_repo_same_second_register_only_lens_keeps_git_order(tmp_path):
    """A register-only lens 3 and a plan-only lens 4 committed in the SAME second, 3
    first. The time-merge's insertion-order tie-break put 4 before 3 — a false breach
    on a live plan. In one repo git's own log over both paths is exact."""
    repo, plan = _repo_with_register(tmp_path, [
        ("draft(f): walk 1 lens 1 — 1 fold", "plan"),
        ("draft(f): walk 1 lens 2 — 1 fold", "plan"),
        ("draft(f): walk 1 lens 3 — DRY", "reg"),
        ("draft(f): walk 1 lens 4 — 1 fold", "plan"),
        ("draft(f): walk 1 lens 5 — 1 fold", "plan"),
    ], same_second=(2, 3))
    r = _run(plan, repo)
    assert r.returncode == 0, r.stdout + r.stderr
    assert "one log" in r.stdout, r.stdout


def test_cross_source_tie_is_not_disorder_but_a_real_descent_still_is():
    """Pure merge check: a cross-source tie carries no ordering evidence."""
    P = lambda lens, when: (1, [lens], "aaaaaaa", "s", when, f"sha-p{lens}", "plan")
    R = lambda lens, when: (1, [lens], "bbbbbbb", "s", when, f"sha-r{lens}", "register")
    import lens_order_check as lo
    tie = lo._merge_by_time([P(1,"t1"), P(4,"t3")], [R(3,"t3")])
    assert [r[1][0] for r in tie] == [1, 3, 4]            # tied 3/4 -> benign order
    real = lo._merge_by_time([P(1,"t1"), P(4,"t2")], [R(3,"t3")])
    assert [r[1][0] for r in real] == [1, 4, 3]           # distinct times -> true order kept


# --- cross-repo: deposited-copy reads OK through fold_baseline -------------------

# The #265 shape: w1 l1 plan+reg, w1 l2 plan-only (dry), w1 l3 plan+reg,
# w1 l4 plan-only, w1 l5 plan-only, w2 l1 plan+reg.
_STEPS_265 = [
    ("draft(executable-fixture): walk 1 lens 1 — fold", "both"),
    ("draft(executable-fixture): walk 1 lens 2 — DRY", "plan"),
    ("draft(executable-fixture): walk 1 lens 3 — fold", "both"),
    ("draft(executable-fixture): walk 1 lens 4 — DRY", "plan"),
    ("draft(executable-fixture): walk 1 lens 5 — DRY", "plan"),
    ("draft(executable-fixture): walk 2 lens 1 — fold", "both"),
]


def _two_repos(tmp_path, steps, with_fold_baseline=True, foreign=False):
    """Build repo A (drafting) and repo B (project) for deposited-copy tests.

    Repo A holds the plan under knowledge/decisions/drafts/executable-fixture.md with
    an ABSOLUTE walk register ref and a committed baseline. Repo B holds a one-commit
    copy of A's plan under knowledge/decisions/executable-fixture.md.

    Returns (repo_a, repo_b, plan_a, plan_b, reg_a).
    """
    repo_a = tmp_path / "governance"
    repo_b = tmp_path / "project"

    (repo_a / "knowledge" / "decisions" / "drafts").mkdir(parents=True)
    (repo_a / "knowledge" / "research").mkdir(parents=True)

    _git(repo_a.parent, "init", "-q", str(repo_a))
    _git(repo_a, "config", "user.email", "t@t")
    _git(repo_a, "config", "user.name", "T")

    plan_a = repo_a / "knowledge" / "decisions" / "drafts" / "executable-fixture.md"
    reg_a = repo_a / "knowledge" / "research" / "walk-register-fixture.md"
    baseline_a = (
        repo_a / "knowledge" / "decisions" / "drafts"
        / ".executable-fixture.md.foldcheck.json"
    )

    # Absolute register ref — a relative ref resolves to nothing from repo B's git root
    walk_reg_ref = str(reg_a.resolve())

    per = "w1 1 folded — instruction 1 / record 0; w2 1 folded — instruction 1 / record 0"
    walk_lines = "\n".join(
        f"- {name}: {per}."
        for name in ("Weak spots", "Destruction", "Vulnerabilities",
                     "Integration-record", "ACID")
    )
    manifest = (
        "\n## Cycle Manifest\n"
        "tier: T1\ntarget: scripts/something.py\nclass: shop-infra\n"
        "reads: test\nwrites: test\nopen_forks: none\n"
        "walks: 2\nyields: 1, 0\nvalidation: <declare>\ncoherence: <declare>\n"
    )
    if with_fold_baseline:
        if foreign:
            other_baseline = (
                repo_a / "knowledge" / "decisions" / "drafts"
                / ".executable-other.md.foldcheck.json"
            )
            manifest += f"fold_baseline: {other_baseline.resolve()}\n"
        else:
            manifest += f"fold_baseline: {baseline_a.resolve()}\n"

    body = (
        "# bellows — executable: fixture\n\n"
        "**Date:** 2026-09-06 | **Project:** bellows | **cycle_tier:** T1\n\n"
        "## Drafting Cycle\n\n"
        f"**Tier:** T1\n"
        f"**Walk register:** {walk_reg_ref}\n"
        "**Walks:** 2\n"
        f"{walk_lines}\n"
        "**Closing:** in progress.\n"
    ) + manifest

    plan_a.write_text(body, encoding="utf-8")
    reg_a.write_text("# Walk Register — fixture\n", encoding="utf-8")
    baseline_a.write_text("{}", encoding="utf-8")

    if foreign:
        # Create a second complete cycle so the identity-tie check has something to compare
        other_plan = (
            repo_a / "knowledge" / "decisions" / "drafts" / "executable-other.md"
        )
        other_reg = repo_a / "knowledge" / "research" / "walk-register-other.md"
        other_baseline = (
            repo_a / "knowledge" / "decisions" / "drafts"
            / ".executable-other.md.foldcheck.json"
        )
        other_reg_ref = str(other_reg.resolve())
        other_body = (
            "# bellows — executable: other\n\n"
            "**Date:** 2026-09-06 | **Project:** bellows | **cycle_tier:** T1\n\n"
            "## Drafting Cycle\n\n"
            "**Tier:** T1\n"
            f"**Walk register:** {other_reg_ref}\n"
            "**Walks:** 1\n"
            f"{walk_lines}\n"
            "**Closing:** in progress.\n"
            "\n## Cycle Manifest\n"
            "tier: T1\ntarget: scripts/other.py\nclass: shop-infra\n"
            "reads: test\nwrites: test\nopen_forks: none\n"
            "walks: 1\nyields: 1\nvalidation: <declare>\ncoherence: <declare>\n"
        )
        other_plan.write_text(other_body, encoding="utf-8")
        other_reg.write_text("# Walk Register — other\n", encoding="utf-8")
        other_baseline.write_text("{}", encoding="utf-8")

    _git(repo_a, "add", "-A")
    _git(repo_a, "commit", "-q", "-m", "seed")

    for i, (subj, target) in enumerate(steps):
        when = f"2026-09-07T10:{i:02d}:00-05:00"
        if target in ("plan", "both"):
            plan_a.write_text(body + f"\n<!-- p{i} -->\n", encoding="utf-8")
            _git(repo_a, "add", str(plan_a))
        if target in ("reg", "both"):
            reg_a.write_text(reg_a.read_text(encoding="utf-8") + f"\nrow {i}\n",
                             encoding="utf-8")
            _git(repo_a, "add", str(reg_a))
        subprocess.run(
            ["git", "-C", str(repo_a), "commit", "-q", "-m", subj],
            capture_output=True, text=True,
            env={**os.environ, "GIT_AUTHOR_DATE": when, "GIT_COMMITTER_DATE": when},
        )

    (repo_b / "knowledge" / "decisions").mkdir(parents=True)
    _git(repo_b.parent, "init", "-q", str(repo_b))
    _git(repo_b, "config", "user.email", "t@t")
    _git(repo_b, "config", "user.name", "T")
    plan_b = repo_b / "knowledge" / "decisions" / "executable-fixture.md"
    plan_b.write_text(body, encoding="utf-8")
    _git(repo_b, "add", "-A")
    _git(repo_b, "commit", "-q", "-m", "deposit executable-fixture")

    return repo_a, repo_b, plan_a, plan_b, reg_a


def test_o1_deposited_copy_reads_ok_through_fold_baseline(tmp_path):
    """A deposited copy (no lens commits in project repo) reads LENS-ORDER OK by following
    fold_baseline: to the drafting repo's ONE log over the draft and the register."""
    _, repo_b, _, plan_b, _ = _two_repos(tmp_path, _STEPS_265)
    r = _run(plan_b, repo_b)
    assert r.returncode == 0, r.stdout + r.stderr
    assert "LENS-ORDER OK" in r.stdout
    assert "source=draft+register, one log via fold_baseline (executable-fixture.md)" in r.stdout


def test_o2_without_fold_baseline_merges_by_time_and_holds(tmp_path):
    """Negative control: copy without fold_baseline: falls back to time-merge (3 register
    commits, walk 1 incomplete) — today's reading preserved where the pointer is absent."""
    _, repo_b, _, plan_b, _ = _two_repos(tmp_path, _STEPS_265, with_fold_baseline=False)
    r = _run(plan_b, repo_b)
    assert r.returncode == 1
    assert "INCOMPLETE: walk 1" in r.stdout
    assert "merged by time" in r.stdout


def test_o3_fold_baseline_nonexistent_no_traceback(tmp_path):
    """fold_baseline: naming a nonexistent file: no change to verdict (time-merge), no crash."""
    _, repo_b, _, plan_b, _ = _two_repos(tmp_path, _STEPS_265)
    import re as _re
    text = plan_b.read_text(encoding="utf-8")
    plan_b.write_text(
        _re.sub(r"fold_baseline: .*\n", "fold_baseline: /nonexistent/.plan.foldcheck.json\n",
                text),
        encoding="utf-8",
    )
    _git(repo_b, "add", str(plan_b))
    _git(repo_b, "commit", "-q", "-m", "nonexistent fold_baseline")
    r = _run(plan_b, repo_b)
    assert r.returncode == 1
    assert "INCOMPLETE" in r.stdout
    assert "merged by time" in r.stdout
    assert "Traceback" not in r.stderr


def test_o4_draft_missing_note_and_fallback(tmp_path):
    """Baseline resolves but derived draft deleted → 'missing' NOTE to stderr, fallback."""
    _, repo_b, plan_a, plan_b, _ = _two_repos(tmp_path, _STEPS_265)
    plan_a.unlink()
    r = _run(plan_b, repo_b)
    assert r.returncode == 1
    assert "merged by time" in r.stdout
    assert "NOTE: fold_baseline resolved;" in r.stderr
    assert "Traceback" not in r.stderr


def test_o4b_draft_is_directory_missing_note(tmp_path):
    """Derived draft path is a directory: is_file() False → 'missing' NOTE, no traceback."""
    _, repo_b, plan_a, plan_b, _ = _two_repos(tmp_path, _STEPS_265)
    plan_a.unlink()
    plan_a.mkdir()
    r = _run(plan_b, repo_b)
    assert r.returncode == 1
    assert "merged by time" in r.stdout
    assert "NOTE: fold_baseline resolved;" in r.stderr
    assert "Traceback" not in r.stderr


def test_o4c_draft_unreadable_note_and_no_traceback(tmp_path):
    """chmod 000 on derived draft: OSError caught → 'unreadable' NOTE, no traceback."""
    _, repo_b, plan_a, plan_b, _ = _two_repos(tmp_path, _STEPS_265)
    plan_a.chmod(0)
    try:
        r = _run(plan_b, repo_b)
    finally:
        plan_a.chmod(0o644)
    assert r.returncode == 1
    assert "merged by time" in r.stdout
    assert "NOTE: fold_baseline resolved;" in r.stderr
    assert "(unreadable)" in r.stderr
    assert "Traceback" not in r.stderr


def test_o5_foreign_pointer_register_ref_differs(tmp_path):
    """fold_baseline: pointing to another plan's baseline: identity tie fails,
    NOTE 'register ref differs' to stderr, verdict unchanged (time-merge), no REPEATED."""
    _, repo_b, _, plan_b, _ = _two_repos(tmp_path, _STEPS_265, foreign=True)
    r = _run(plan_b, repo_b)
    assert r.returncode == 1
    assert "INCOMPLETE: walk 1" in r.stdout
    assert "merged by time" in r.stdout
    assert "REPEATED" not in r.stdout
    assert "register ref differs" in r.stderr
