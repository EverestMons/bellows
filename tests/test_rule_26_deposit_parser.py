"""Targeted tests for Rule 26 deposit parser scope changes."""

import os
import re
import sys
from unittest.mock import patch

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import gates
import verdict


def test_extract_plan_required_deposits_prefers_declared_block():
    """When a **Deposits:** block is present, only its paths are returned — prose is ignored."""
    step_text = """\
## STEP 1 — DEV

> Deposit findings to `other-path.md` for reference.
>
> **Deposits:**
> - `knowledge/dev/alpha.md`
> - `knowledge/dev/beta.md`
"""
    result = gates._extract_plan_required_deposits(step_text)
    assert set(result) == {"knowledge/dev/alpha.md", "knowledge/dev/beta.md"}
    assert "other-path.md" not in result


def test_extract_plan_required_deposits_falls_back_to_legacy_when_no_block():
    """Without a **Deposits:** block, legacy prose patterns are used."""
    step_text = """\
## STEP 1 — DEV

> Deposit findings to `prose-path.md` for the record.
"""
    result = gates._extract_plan_required_deposits(step_text)
    assert "prose-path.md" in result


def test_extract_plan_required_deposits_handles_none_bullet():
    """A **Deposits:** block with only '- none' returns an empty set."""
    step_text = """\
## STEP 1 — DEV

> This step produces no files.
>
> **Deposits:**
> - none
"""
    result = gates._extract_plan_required_deposits(step_text)
    assert set(result) == set()


def test_extract_plan_required_deposits_ignores_paths_in_code_fences_when_block_present():
    """BACKLOG #6 regression: code-fenced paths must not leak into the deposit set."""
    step_text = """\
## STEP 1 — DEV

> Here is a code example:
> ```python
> with open("path/to/file.md", "w") as f:
>     f.write("hello")
> ```
>
> Deposit findings to `legacy/false-positive.md` in prose.
>
> **Deposits:**
> - `knowledge/dev/real-deposit.md`
"""
    result = gates._extract_plan_required_deposits(step_text)
    assert set(result) == {"knowledge/dev/real-deposit.md"}
    assert "path/to/file.md" not in result
    assert "legacy/false-positive.md" not in result


def test_extract_primary_deposit_scoping_in_post_verdict_request(tmp_path):
    """Scoping bug regression: Deposit field must reflect current step, not first match."""
    full_plan = """\
## STEP 1 — DEV

> Do step 1 work.
>
> **Deposits:** - `step-1.md`

## STEP 2 — QA

> Do step 2 work.
>
> **Deposits:** - `step-2.md`
"""
    gate_result = {"passed": True, "failures": [], "files_changed": []}

    with patch.object(verdict, "VERDICTS_DIR", tmp_path):
        filepath = verdict.post_verdict_request(
            plan_path="test-plan.md",
            project_path="/tmp/project",
            step_number=2,
            log_path="/tmp/logs",
            gate_result=gate_result,
            total_steps=2,
            step_text=full_plan,
        )

    content = open(filepath).read()
    deposit_match = re.search(r'\*\*Deposit:\*\*\s+(.*)', content)
    assert deposit_match is not None
    deposit_value = deposit_match.group(1).strip()
    assert deposit_value == "step-2.md", f"Expected 'step-2.md', got '{deposit_value}'"
    assert "step-1.md" not in deposit_value


def test_extract_plan_required_deposits_blank_quoted_line():
    """Blank `>` line between **Deposits:** header and bullets must still match."""
    step_text = """\
## STEP 1 — DEV

> **Deposits:**
>
> - `bellows/foo.md`
"""
    result = gates._extract_plan_required_deposits(step_text)
    assert set(result) == {"bellows/foo.md"}


def test_extract_plan_required_deposits_multiple_blank_quoted_lines():
    """Multiple blank `>` lines between header and bullets must still match."""
    step_text = """\
## STEP 1 — DEV

> **Deposits:**
>
>
> - `bellows/foo.md`
"""
    result = gates._extract_plan_required_deposits(step_text)
    assert set(result) == {"bellows/foo.md"}


def test_extract_plan_required_deposits_does_not_span_paragraphs():
    """An empty line (no `>` prefix) breaks the block — cross-paragraph must not match."""
    step_text = """\
## STEP 1 — DEV

> **Deposits:**
>

Some other prose.

- `unrelated/bar.md`
"""
    result = gates._extract_plan_required_deposits(step_text)
    assert set(result) == set()


def test_extract_step_text_helper_gates_py():
    """_extract_step_text returns only the requested step's text."""
    plan_text = """\
## STEP 1 — DEV

> Step 1 content here.

## STEP 2 — QA

> Step 2 content here.

## STEP 3 — Final

> Step 3 content here.
"""
    result = gates._extract_step_text(plan_text, 2)
    assert result is not None
    assert result.startswith("## STEP 2")
    assert "## STEP 3" not in result
    assert "Step 2 content here." in result
