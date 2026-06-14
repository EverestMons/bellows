"""Tests for parser.py — ledger_updates extraction (daemon-owned ledgers Phase 1)."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import parser


BASE_FIXTURE = {
    "type": "result",
    "subtype": "success",
    "is_error": False,
    "result": "Step 1 complete.",
    "stop_reason": "end_turn",
    "session_id": "abc123",
    "total_cost_usd": 0.10,
    "permission_denials": [],
}


class TestLedgerUpdatesExtraction:
    """(c) parser extracts ### Ledger Updates → feedback (and returns empty when absent)."""

    def test_extracts_feedback_from_output_receipt(self):
        text = (
            "## Output Receipt\n"
            "**Agent:** Bellows Developer\n"
            "**Step:** 1\n"
            "**Status:** Complete\n\n"
            "### What Was Done\nSome work.\n\n"
            "### Flags for CEO\n- None\n\n"
            "### Ledger Updates\n"
            "#### Prompt Feedback\n"
            "**2026-06-13 — test-plan (DEV Step 1)**\n\n"
            "1. First observation.\n"
            "2. Second observation.\n"
        )
        fixture = dict(BASE_FIXTURE, result=text)
        parsed = parser.parse(fixture)
        assert parsed["ledger_updates"]["feedback"] is not None
        assert "First observation" in parsed["ledger_updates"]["feedback"]
        assert "Second observation" in parsed["ledger_updates"]["feedback"]

    def test_returns_none_when_section_absent(self):
        text = (
            "## Output Receipt\n"
            "**Agent:** Bellows Developer\n"
            "**Step:** 1\n"
            "**Status:** Complete\n\n"
            "### Flags for CEO\n- None\n"
        )
        fixture = dict(BASE_FIXTURE, result=text)
        parsed = parser.parse(fixture)
        assert parsed["ledger_updates"]["feedback"] is None

    def test_returns_none_when_feedback_subsection_absent(self):
        text = (
            "### Ledger Updates\n"
            "#### PROJECT_STATUS\n"
            "- 2026-06-13: some milestone\n"
        )
        fixture = dict(BASE_FIXTURE, result=text)
        parsed = parser.parse(fixture)
        assert parsed["ledger_updates"]["feedback"] is None

    def test_returns_none_for_none_value(self):
        text = (
            "### Ledger Updates\n"
            "#### Prompt Feedback\n"
            "None\n"
        )
        fixture = dict(BASE_FIXTURE, result=text)
        parsed = parser.parse(fixture)
        assert parsed["ledger_updates"]["feedback"] is None

    def test_returns_none_for_na_value(self):
        text = (
            "### Ledger Updates\n"
            "#### Prompt Feedback\n"
            "N/A\n"
        )
        fixture = dict(BASE_FIXTURE, result=text)
        parsed = parser.parse(fixture)
        assert parsed["ledger_updates"]["feedback"] is None

    def test_handles_feedback_before_another_subsection(self):
        text = (
            "### Ledger Updates\n"
            "#### Prompt Feedback\n"
            "Feedback text here.\n\n"
            "#### FORWARD Additions\n"
            "| # | Added | Item |\n"
        )
        fixture = dict(BASE_FIXTURE, result=text)
        parsed = parser.parse(fixture)
        assert parsed["ledger_updates"]["feedback"] == "Feedback text here."

    def test_ledger_updates_key_always_present(self):
        fixture = dict(BASE_FIXTURE)
        parsed = parser.parse(fixture)
        assert "ledger_updates" in parsed
        assert "feedback" in parsed["ledger_updates"]

    def test_mirrors_ceo_flags_pattern(self):
        """Verify the ledger extraction does not interfere with ceo_flags."""
        text = (
            "### Flags for CEO\n"
            "- DAEMON RESTART REQUIRED\n\n"
            "### Ledger Updates\n"
            "#### Prompt Feedback\n"
            "Some feedback.\n"
        )
        fixture = dict(BASE_FIXTURE, result=text)
        parsed = parser.parse(fixture)
        assert parsed["ceo_flags"] == ["DAEMON RESTART REQUIRED"]
        assert parsed["ledger_updates"]["feedback"] == "Some feedback."


class TestProjectStatusExtraction:
    """Phase 2: parser extracts #### Project Status from ### Ledger Updates."""

    def test_extracts_project_status(self):
        text = (
            "### Ledger Updates\n"
            "#### Project Status\n"
            "- 2026-06-13: **Daemon-owned ledgers Phase 2.** "
            "Extended daemon-post-merge to handle PROJECT_STATUS.md.\n"
        )
        fixture = dict(BASE_FIXTURE, result=text)
        parsed = parser.parse(fixture)
        assert parsed["ledger_updates"]["project_status"] is not None
        assert "Daemon-owned ledgers Phase 2" in parsed["ledger_updates"]["project_status"]

    def test_project_status_none_when_absent(self):
        text = (
            "### Ledger Updates\n"
            "#### Prompt Feedback\n"
            "Some feedback.\n"
        )
        fixture = dict(BASE_FIXTURE, result=text)
        parsed = parser.parse(fixture)
        assert parsed["ledger_updates"]["project_status"] is None

    def test_project_status_none_for_none_value(self):
        text = (
            "### Ledger Updates\n"
            "#### Project Status\n"
            "None\n"
        )
        fixture = dict(BASE_FIXTURE, result=text)
        parsed = parser.parse(fixture)
        assert parsed["ledger_updates"]["project_status"] is None

    def test_project_status_none_for_na_value(self):
        text = (
            "### Ledger Updates\n"
            "#### Project Status\n"
            "N/A\n"
        )
        fixture = dict(BASE_FIXTURE, result=text)
        parsed = parser.parse(fixture)
        assert parsed["ledger_updates"]["project_status"] is None

    def test_both_feedback_and_project_status_extracted(self):
        """Phase 1 feedback and Phase 2 project status coexist."""
        text = (
            "### Ledger Updates\n"
            "#### Prompt Feedback\n"
            "Feedback entry here.\n\n"
            "#### Project Status\n"
            "- 2026-06-13: Milestone reached.\n"
        )
        fixture = dict(BASE_FIXTURE, result=text)
        parsed = parser.parse(fixture)
        assert parsed["ledger_updates"]["feedback"] == "Feedback entry here."
        assert "Milestone reached" in parsed["ledger_updates"]["project_status"]

    def test_project_status_key_always_present(self):
        """project_status key is always in ledger_updates, even when absent."""
        fixture = dict(BASE_FIXTURE)
        parsed = parser.parse(fixture)
        assert "project_status" in parsed["ledger_updates"]
        assert parsed["ledger_updates"]["project_status"] is None

    def test_project_status_before_feedback(self):
        """Order of subsections should not matter."""
        text = (
            "### Ledger Updates\n"
            "#### Project Status\n"
            "Status text.\n\n"
            "#### Prompt Feedback\n"
            "Feedback text.\n"
        )
        fixture = dict(BASE_FIXTURE, result=text)
        parsed = parser.parse(fixture)
        assert parsed["ledger_updates"]["project_status"] == "Status text."
        assert parsed["ledger_updates"]["feedback"] == "Feedback text."


class TestForwardRegisterExtraction:
    """Phase 3: parser extracts #### Forward Register from ### Ledger Updates."""

    def test_extracts_forward_register(self):
        text = (
            "### Ledger Updates\n"
            "#### Forward Register\n"
            "Implement auto-stash for dirty main at teardown\n"
        )
        fixture = dict(BASE_FIXTURE, result=text)
        parsed = parser.parse(fixture)
        assert parsed["ledger_updates"]["forward"] is not None
        assert "auto-stash" in parsed["ledger_updates"]["forward"]

    def test_extracts_forward_additions_heading(self):
        """Also matches #### FORWARD Additions (design doc heading)."""
        text = (
            "### Ledger Updates\n"
            "#### FORWARD Additions\n"
            "New deferred work item\n"
        )
        fixture = dict(BASE_FIXTURE, result=text)
        parsed = parser.parse(fixture)
        assert parsed["ledger_updates"]["forward"] == "New deferred work item"

    def test_extracts_forward_bare_heading(self):
        """Also matches #### FORWARD (bare form)."""
        text = (
            "### Ledger Updates\n"
            "#### FORWARD\n"
            "Bare heading item\n"
        )
        fixture = dict(BASE_FIXTURE, result=text)
        parsed = parser.parse(fixture)
        assert parsed["ledger_updates"]["forward"] == "Bare heading item"

    def test_forward_none_when_absent(self):
        text = (
            "### Ledger Updates\n"
            "#### Prompt Feedback\n"
            "Some feedback.\n"
        )
        fixture = dict(BASE_FIXTURE, result=text)
        parsed = parser.parse(fixture)
        assert parsed["ledger_updates"]["forward"] is None

    def test_forward_none_for_none_value(self):
        text = (
            "### Ledger Updates\n"
            "#### Forward Register\n"
            "None\n"
        )
        fixture = dict(BASE_FIXTURE, result=text)
        parsed = parser.parse(fixture)
        assert parsed["ledger_updates"]["forward"] is None

    def test_forward_none_for_na_value(self):
        text = (
            "### Ledger Updates\n"
            "#### Forward Register\n"
            "N/A\n"
        )
        fixture = dict(BASE_FIXTURE, result=text)
        parsed = parser.parse(fixture)
        assert parsed["ledger_updates"]["forward"] is None

    def test_forward_key_always_present(self):
        """forward key is always in ledger_updates, even when absent."""
        fixture = dict(BASE_FIXTURE)
        parsed = parser.parse(fixture)
        assert "forward" in parsed["ledger_updates"]
        assert parsed["ledger_updates"]["forward"] is None

    def test_forward_with_feedback_and_project_status(self):
        """All three Phase 1/2/3 subsections coexist."""
        text = (
            "### Ledger Updates\n"
            "#### Prompt Feedback\n"
            "Feedback entry.\n\n"
            "#### Project Status\n"
            "Milestone text.\n\n"
            "#### Forward Register\n"
            "New deferred item\n"
        )
        fixture = dict(BASE_FIXTURE, result=text)
        parsed = parser.parse(fixture)
        assert parsed["ledger_updates"]["feedback"] == "Feedback entry."
        assert "Milestone text." in parsed["ledger_updates"]["project_status"]
        assert parsed["ledger_updates"]["forward"] == "New deferred item"

    def test_forward_before_other_subsections(self):
        """Order of subsections should not matter."""
        text = (
            "### Ledger Updates\n"
            "#### Forward Register\n"
            "Item first.\n\n"
            "#### Prompt Feedback\n"
            "Feedback second.\n"
        )
        fixture = dict(BASE_FIXTURE, result=text)
        parsed = parser.parse(fixture)
        assert parsed["ledger_updates"]["forward"] == "Item first."
        assert parsed["ledger_updates"]["feedback"] == "Feedback second."

    def test_feedback_and_project_status_still_extract(self):
        """Regression: Phase 1+2 extraction not broken by Phase 3 addition."""
        text = (
            "### Ledger Updates\n"
            "#### Prompt Feedback\n"
            "Phase 1 feedback.\n\n"
            "#### Project Status\n"
            "Phase 2 status.\n"
        )
        fixture = dict(BASE_FIXTURE, result=text)
        parsed = parser.parse(fixture)
        assert parsed["ledger_updates"]["feedback"] == "Phase 1 feedback."
        assert parsed["ledger_updates"]["project_status"] == "Phase 2 status."
        assert parsed["ledger_updates"]["forward"] is None


class TestAllAssistantTextPropagation:
    """Plan 60 G2: parse() returns _all_assistant_text in the parsed dict."""

    def test_all_assistant_text_returned_from_result_text(self):
        """When no _all_assistant_text in raw, parsed returns result_text as fallback."""
        fixture = dict(BASE_FIXTURE, result="Step 1 complete.")
        parsed = parser.parse(fixture)
        assert "_all_assistant_text" in parsed
        assert parsed["_all_assistant_text"] == "Step 1 complete."

    def test_all_assistant_text_returned_from_raw(self):
        """When _all_assistant_text is in raw, parsed returns it."""
        full_text = (
            "### Ledger Updates\n"
            "#### Forward Register\n"
            "Forward item from tool content.\n"
        )
        fixture = dict(BASE_FIXTURE, _all_assistant_text=full_text, result="Done.")
        parsed = parser.parse(fixture)
        assert parsed["_all_assistant_text"] == full_text

    def test_extraction_succeeds_from_all_assistant_text(self):
        """Ledger extraction works when block is in _all_assistant_text but not in result."""
        tool_text = (
            "### Ledger Updates\n"
            "#### Forward Register\n"
            "Tool-buried forward item\n"
        )
        fixture = dict(BASE_FIXTURE, _all_assistant_text=tool_text, result="Done.")
        parsed = parser.parse(fixture)
        assert parsed["ledger_updates"]["forward"] == "Tool-buried forward item"

    def test_extraction_feedback_from_tool_content(self):
        """Feedback extraction works from _all_assistant_text (tool content)."""
        tool_text = (
            "### Ledger Updates\n"
            "#### Prompt Feedback\n"
            "Feedback from Write block.\n"
        )
        fixture = dict(BASE_FIXTURE, _all_assistant_text=tool_text, result="Done.")
        parsed = parser.parse(fixture)
        assert parsed["ledger_updates"]["feedback"] == "Feedback from Write block."
