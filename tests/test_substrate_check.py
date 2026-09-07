"""thread 183 — the drafting-cycle substrate gates auto-close, mechanically.

⛔ Every fixture is a REAL git repo under tmp_path; the check reads history.
"""
import os, subprocess, sys
from pathlib import Path
BELLOWS_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BELLOWS_ROOT)); sys.path.insert(0, str(BELLOWS_ROOT / "scripts"))
import substrate_check  # noqa: E402

def _git(repo, *a, env=None):
    return subprocess.run(["git", "-C", str(repo), *a], capture_output=True, text=True, env=env)

def _plan(tier, register_line):
    per = "w1 1 folded — instruction 0 / record 1"
    lens = "\n".join(f"- {n}: {per}." for n in ("Weak spots","Destruction","Vulnerabilities","Integration-record","ACID"))
    return (f"# bellows — executable: fixture\n\n**Date:** 2026-09-07 | **Project:** bellows | **cycle_tier:** {tier}\n\n"
            f"## Drafting Cycle\n\n**Tier:** {tier}\n{register_line}**Walks:** 1\n{lens}\n**Closing:** in progress.\n\n## STEP 1 — do it\n")

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
