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
