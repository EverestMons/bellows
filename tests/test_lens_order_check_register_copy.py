"""lens_order_check reads a register's lens commits even when git rename-DETECTS the
register as a copy of an earlier one (a re-filed plan whose new register began as the
old register's text). Measured 2026-09-16 (git 2.55.0): `git log --follow --reverse` on
such a file returns only its creation commit, so the observer read NO-RECORD for a
register with five lens commits. The register is never renamed by the pipeline; only
the plan is. Runs the real tool as a subprocess in a temporary repository."""
import os
import subprocess
import sys
import textwrap
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "lens_order_check.py"


def _git(repo, *args):
    return subprocess.run(["git", "-C", str(repo), *args], check=True, capture_output=True, text=True,
                          env={**os.environ, "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t",
                               "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t"}).stdout


def _plan_text(register_path):
    return textwrap.dedent(f"""\
        # plan
        **Date:** 2026-09-16 | **Project:** x | **cycle_tier:** T2 | **Dispatch Mode:** bellows | **pause_for_verdict:** after_qa_step

        ## Drafting Cycle

        **Tier:** T2 — one trigger.
        **Walk register:** {register_path}
        **Walk 0 (context pin, measured):** pinned.

        - Weak spots:          w1 dry
        - Destruction:         w1 dry
        - Vulnerabilities:     w1 dry
        - Integration-record:  w1 dry
        - ACID:                w1 dry
        **Cold panel:** none
        **Closing:** <declare>

        ## Cycle Manifest
        tier: T2

        ---

        ## STEP 1 — DEV
        > x
        """)


def _register_text(name, rows):
    body = "# Walk register — %s\n\n**schema_version:** `0.3`\n\nDraft: `x.md`\n\n" % name
    body += "| id | walk | lens | sub_question | origin | finding | pre_fold_text | resolution |\n|---|---|---|---|---|---|---|---|\n"
    body += "".join(f"**Walk 1 lens {n} — DRY, basis:** row {n} of {name}, padding so the two registers stay near-identical.\n" for n in rows)
    return body


def _run(plan):
    out = subprocess.run([sys.executable, str(SCRIPT), str(plan)], capture_output=True, text=True)
    return out.returncode, (out.stdout + out.stderr)


def test_register_copied_from_an_earlier_register_still_proves_its_lens_commits(tmp_path):
    repo = tmp_path / "gov"
    repo.mkdir()
    _git(repo, "init", "-q", "-b", "main")
    drafts = repo / "drafts"; research = repo / "research"
    drafts.mkdir(); research.mkdir()
    # the FIRST register and plan, five lens commits
    reg_a = research / "walk-register-a.md"; plan_a = drafts / "plan-a.md"
    reg_a.write_text(_register_text("a", []))
    plan_a.write_text(_plan_text(reg_a))
    _git(repo, "add", "-A"); _git(repo, "commit", "-q", "-m", "draft(plan-a): v0")
    for n in range(1, 6):
        reg_a.write_text(_register_text("a", range(1, n + 1)))
        _git(repo, "add", "-A"); _git(repo, "commit", "-q", "-m", f"draft(plan-a): walk 1 lens {n} — dry")
    # the SECOND register begins as a copy of the first (git rename-detects it), then its own five
    reg_b = research / "walk-register-b.md"; plan_b = drafts / "plan-b.md"
    reg_b.write_text(_register_text("b", []) + "\n" + reg_a.read_text())
    plan_b.write_text(_plan_text(reg_b))
    _git(repo, "add", "-A"); _git(repo, "commit", "-q", "-m", "draft(plan-b): v0")
    for n in range(1, 6):
        reg_b.write_text(reg_b.read_text() + f"**Walk 1 lens {n} — DRY, basis:** b row {n}.\n")
        _git(repo, "add", "-A"); _git(repo, "commit", "-q", "-m", f"draft(plan-b): walk 1 lens {n} — dry")
    rc, text = _run(plan_b)
    assert "NO-RECORD" not in text, text
    assert "LENS-ORDER OK" in text and "5 lens commit(s)" in text, text
    assert rc == 0, text
    # the first plan's record is untouched by the change
    rc_a, text_a = _run(plan_a)
    assert "LENS-ORDER OK" in text_a and "5 lens commit(s)" in text_a, text_a


def test_plan_side_follow_still_reads_the_pipelines_rename(tmp_path):
    """The plan IS renamed by the pipeline; --follow stays on the plan side."""
    repo = tmp_path / "gov"; repo.mkdir(); _git(repo, "init", "-q", "-b", "main")
    (repo / "drafts").mkdir(); (repo / "research").mkdir()
    reg = repo / "research" / "walk-register-p.md"; plan = repo / "drafts" / "plan-p.md"
    reg.write_text(_register_text("p", [])); plan.write_text(_plan_text(reg))
    _git(repo, "add", "-A"); _git(repo, "commit", "-q", "-m", "draft(plan-p): v0")
    for n in range(1, 6):
        plan.write_text(plan.read_text() + f"\n<!-- {n} -->\n"); reg.write_text(_register_text("p", range(1, n + 1)))
        _git(repo, "add", "-A"); _git(repo, "commit", "-q", "-m", f"draft(plan-p): walk 1 lens {n} — dry")
    moved = repo / "plan-p.md"; _git(repo, "mv", str(plan), str(moved)); _git(repo, "commit", "-q", "-m", "deposit: plan-p")
    rc, text = _run(moved)
    assert "LENS-ORDER OK" in text and "5 lens commit(s)" in text, text
