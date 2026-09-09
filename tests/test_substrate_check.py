"""thread 183 — the drafting-cycle substrate gates auto-close, mechanically.

⛔ Every fixture is a REAL git repo under tmp_path; the check reads history.
"""
import os, subprocess, sys
from pathlib import Path
BELLOWS_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BELLOWS_ROOT)); sys.path.insert(0, str(BELLOWS_ROOT / "scripts"))

# Force-load from the worktree's scripts/. depositor.py (imported via
# test_admission_flip.py → bellows.py) adds the canonical bellows scripts
# (resolve_bellows_root() → config.json → main branch) to sys.path[0],
# then bellows.py imports substrate_check from there. The main-branch copy
# still has the old literal "CONFORMANT" rather than STATUS_CONFORMANT,
# so it must be evicted and reimported from the worktree.
import importlib
_SC_PATH = str(BELLOWS_ROOT / "scripts" / "substrate_check.py")
if "substrate_check" in sys.modules and sys.modules["substrate_check"].__file__ != _SC_PATH:
    del sys.modules["substrate_check"]
import substrate_check  # noqa: E402

def _git(repo, *a, env=None):
    return subprocess.run(["git", "-C", str(repo), *a], capture_output=True, text=True, env=env)

def _plan(tier, register_line, manifest_extra=""):
    per = "w1 1 folded — instruction 0 / record 1"
    lens = "\n".join(f"- {n}: {per}." for n in ("Weak spots","Destruction","Vulnerabilities","Integration-record","ACID"))
    return (f"# bellows — executable: fixture\n\n**Date:** 2026-09-07 | **Project:** bellows | **cycle_tier:** {tier}\n\n"
            f"## Drafting Cycle\n\n**Tier:** {tier}\n{register_line}**Walks:** 1\n{lens}\n**Closing:** in progress.\n\n"
            f"## Cycle Manifest\ntier: {tier}\ntarget: x.py\nclass: governed-tooling\nreads: x.py\nwrites: x.py\n"
            f"open_forks: none\nwalks: 1\nyields: 1\nvalidation: N/A\ncoherence: N/A\n{manifest_extra}\n## STEP 1 — do it\n")

def _repo(tmp_path, tier="T1", with_register=True, commit_register=True, lens_commits=True, baseline=True):
    repo = tmp_path / "r"; (repo/"knowledge/decisions/drafts").mkdir(parents=True); (repo/"knowledge/research").mkdir(parents=True)
    _git(repo.parent, "init", "-q", str(repo)); _git(repo, "config", "user.email", "t@t"); _git(repo, "config", "user.name", "T")
    plan = repo/"knowledge/decisions/drafts/executable-fixture.md"
    reg = repo/"knowledge/research/walk-register-fixture.md"
    regline = "**Walk register:** knowledge/research/walk-register-fixture.md\n" if with_register else ""
    plan.write_text(_plan(tier, regline))
    if with_register:
        reg.write_text("# Walk Register — fixture\n\n**schema_version:** `0.2`\n\n## Walk 1\n\n"
                       "| id | walk | lens | sub_question | origin | finding | pre_fold_text | resolution |\n|---|---|---|---|---|---|---|---|\n"
                       "| f1 | 1 | Weak spots | 1.1 | pre-existing | x | y | z |\n")
    _git(repo, "add", "-A"); _git(repo, "commit", "-q", "-m", "seed")
    if lens_commits:
        for i, lens in enumerate((1,2,3,4,5)):
            plan.write_text(plan.read_text() + f"\n<!-- p{i} -->\n"); _git(repo, "add", str(plan))
            when = f"2026-09-07T10:{i:02d}:00-05:00"
            subprocess.run(["git","-C",str(repo),"commit","-q","-m",f"draft(f): walk 1 lens {lens} — 1 fold"],
                           capture_output=True, text=True, env={**os.environ,"GIT_AUTHOR_DATE":when,"GIT_COMMITTER_DATE":when})
    if with_register and not commit_register:
        reg.write_text(reg.read_text() + "\nuncommitted row\n")
    if baseline:
        (plan.parent / f".{plan.name}.foldcheck.json").write_text("{}")
    return plan

def test_all_three_legs_present(tmp_path):
    present, detail = substrate_check.substrate_status(_repo(tmp_path))
    assert present is True, detail

def test_t0_owes_no_substrate(tmp_path):
    present, detail = substrate_check.substrate_status(_repo(tmp_path, tier="T0", with_register=False, lens_commits=False, baseline=False))
    assert present is None, detail

def test_no_register_is_absent(tmp_path):
    present, detail = substrate_check.substrate_status(_repo(tmp_path, with_register=False))
    assert present is False and "register" in detail, detail

def test_uncommitted_register_is_absent(tmp_path):
    """Doctrine says COMMITTED — a register with unsaved rows is not the record."""
    present, detail = substrate_check.substrate_status(_repo(tmp_path, commit_register=False))
    assert present is False and "uncommitted" in detail, detail

def test_no_lens_commits_is_absent(tmp_path):
    present, detail = substrate_check.substrate_status(_repo(tmp_path, lens_commits=False))
    assert present is False and "per-walk commits" in detail, detail

def test_no_baseline_is_absent(tmp_path):
    present, detail = substrate_check.substrate_status(_repo(tmp_path, baseline=False))
    assert present is False and "baseline" in detail, detail


def test_leg3_reads_a_manifest_fold_baseline_resolved_like_the_register_ref(tmp_path):
    """Thread 185 / DRAFTING_CYCLE v2.28. The baseline sits somewhere else — where the
    DRAFT was — and the manifest names it; the same resolver that finds the register
    finds it. Beside-the-plan alone would read ABSENT."""
    plan = _repo(tmp_path, baseline=False)
    repo = plan.parents[3]
    elsewhere = repo / "knowledge" / "drafts-elsewhere"; elsewhere.mkdir()
    (elsewhere / ".the-draft.md.foldcheck.json").write_text("{}")
    plan.write_text(plan.read_text().replace("coherence: N/A\n",
                    "coherence: N/A\nfold_baseline: knowledge/drafts-elsewhere/.the-draft.md.foldcheck.json\n"))
    _git(repo, "add", "-A"); _git(repo, "commit", "-q", "-m", "walk 1 lens 5 — record the baseline path")
    present, detail = substrate_check.substrate_status(plan)
    assert present is True, detail


def test_leg3_manifest_fold_baseline_that_does_not_resolve_is_absent(tmp_path):
    plan = _repo(tmp_path, baseline=False)
    plan.write_text(plan.read_text().replace("coherence: N/A\n", "coherence: N/A\nfold_baseline: knowledge/nowhere.json\n"))
    present, detail = substrate_check.substrate_status(plan)
    assert present is False and "fold_baseline" in detail, detail
