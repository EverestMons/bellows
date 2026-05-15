"""Tests for extract_primary_deposit block-form matching (Rule 26)."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from verdict import extract_primary_deposit


def test_block_single_md_path_returned():
    step_text = """\
## STEP 1 — Developer

> Do the work.
>
> **Deposits:**
> - `project/knowledge/development/my-feature-2026-04-19.md`
>
> Standard prompt feedback protocol → `project/knowledge/research/agent-prompt-feedback.md`.
"""
    result = extract_primary_deposit(step_text)
    assert result == "project/knowledge/development/my-feature-2026-04-19.md"


def test_block_multiple_md_first_returned():
    step_text = """\
## STEP 1 — Developer

> **Deposits:**
> - `project/knowledge/development/first.md`
> - `project/knowledge/qa/second.md`
"""
    result = extract_primary_deposit(step_text)
    assert result == "project/knowledge/development/first.md"


def test_block_none_bullet_returns_none():
    step_text = """\
## STEP 1 — Developer

> **Deposits:**
> - none
"""
    result = extract_primary_deposit(step_text)
    assert result is None


def test_block_directory_only_returns_none():
    """Block is authoritative — function does NOT fall back to legacy regexes
    even if the step text contains prose-form deposits elsewhere."""
    step_text = """\
## STEP 1 — Developer

> Deposit findings to `project/knowledge/development/report.md`.
>
> **Deposits:**
> - `project/knowledge/qa/evidence/my-test-2026-04-19/`
"""
    result = extract_primary_deposit(step_text)
    assert result is None


def test_no_block_falls_back_to_legacy():
    step_text = """\
## STEP 1 — Developer

> Deposit findings to `project/knowledge/development/path.md`.
"""
    result = extract_primary_deposit(step_text)
    assert result == "project/knowledge/development/path.md"


def test_block_with_blockquote_prefix_still_matches():
    """Regression test for > blockquote prefix issue in real plan steps."""
    step_text = """\
> ## STEP 1 — Developer
>
> Do the work described above.
>
> **Deposits:**
> - `bellows/knowledge/development/my-feature-2026-04-19.md`
> - `bellows/knowledge/qa/evidence/my-test-2026-04-19/`
>
> Standard prompt feedback protocol → `bellows/knowledge/research/agent-prompt-feedback.md`.
"""
    result = extract_primary_deposit(step_text)
    assert result == "bellows/knowledge/development/my-feature-2026-04-19.md"


def test_block_with_blank_quoted_line_between_header_and_bullets():
    """Blank `>` line between **Deposits:** header and first bullet must still match."""
    step_text = """\
## STEP 1 — Developer

> **Deposits:**
>
> - `bellows/foo.md`
"""
    result = extract_primary_deposit(step_text)
    assert result == "bellows/foo.md"


def test_block_with_multiple_blank_quoted_lines():
    """Multiple blank `>` lines between header and bullets must still match."""
    step_text = """\
## STEP 1 — Developer

> **Deposits:**
>
>
> - `bellows/foo.md`
"""
    result = extract_primary_deposit(step_text)
    assert result == "bellows/foo.md"


def test_block_does_not_span_paragraphs():
    """An empty line (no `>` prefix) breaks the block — bullets after it must not match."""
    step_text = """\
## STEP 1 — Developer

> **Deposits:**
>

Some other prose.

- `unrelated/bar.md`
"""
    result = extract_primary_deposit(step_text)
    assert result is None
