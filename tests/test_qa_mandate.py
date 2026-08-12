import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import gates


def test_qa_step_with_header_returns_suffix():
    plan = "## STEP 1 — DEV\ndo dev\n## STEP 2 — QA\ndo qa\n"
    header = {"qa_steps": 2}
    result = gates.qa_mandate_suffix(plan, 2, header)
    assert result == gates.QA_MANDATE_SUFFIX


def test_non_qa_step_returns_empty():
    plan = "## STEP 1 — DEV\ndo dev\n## STEP 2 — QA\ndo qa\n"
    header = {"qa_steps": 2}
    result = gates.qa_mandate_suffix(plan, 1, header)
    assert result == ""


def test_header_list_form():
    plan = "## STEP 1 — DEV\n## STEP 2 — QA\n## STEP 3 — DEV\n## STEP 4 — QA\n"
    header = {"qa_steps": [2, 4]}
    assert gates.qa_mandate_suffix(plan, 2, header) == gates.QA_MANDATE_SUFFIX
    assert gates.qa_mandate_suffix(plan, 4, header) == gates.QA_MANDATE_SUFFIX
    assert gates.qa_mandate_suffix(plan, 1, header) == ""
    assert gates.qa_mandate_suffix(plan, 3, header) == ""


def test_keyword_fallback_no_header():
    plan = "## STEP 1 — DEV\ndo dev\n## STEP 3 — QA\ndo qa\n"
    result = gates.qa_mandate_suffix(plan, 3)
    assert result == gates.QA_MANDATE_SUFFIX


def test_no_step_heading_returns_empty():
    plan = "Read the diagnostic. Execute it fully.\n"
    result = gates.qa_mandate_suffix(plan, 1)
    assert result == ""


def test_suffix_contains_banner_literals():
    plan = "## STEP 2 — QA\ndo qa\n"
    header = {"qa_steps": 2}
    result = gates.qa_mandate_suffix(plan, 2, header)
    assert "Rule 20 — QA Self-Check Results" in result
    assert "PASSED — SELF-CHECK PASSED" in result
