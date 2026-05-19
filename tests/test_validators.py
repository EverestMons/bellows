import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import gates
import validators


# --- Helper fixtures ---

def _config_with_watched(watched_dir="/tmp/project/knowledge/decisions"):
    return {"watched_projects": [watched_dir]}


def _plan_text(dispatch_mode, step_body="Do the work.", preamble="", deposits_block=""):
    """Build a minimal plan text with a configurable dispatch mode and step body."""
    header = f"# Test Plan\n"
    if dispatch_mode is not None:
        header += f"**Dispatch Mode:** {dispatch_mode}\n"
    header += "**Total Steps:** 1\n"
    header += "\n"
    if preamble:
        header += preamble + "\n\n"
    text = header + f"## STEP 1 — DEV\n\n{step_body}\n"
    if deposits_block:
        text += f"\n{deposits_block}\n"
    return text


def _header_for(plan_text):
    """Parse the plan text header using the real gates parser."""
    return gates._parse_plan_header(plan_text)


# --- Test 1: clean plan, all checks pass ---

def test_clean_plan_all_checks_pass():
    text = _plan_text("bellows", step_body="Implement the feature.")
    header = _header_for(text)
    config = _config_with_watched("/tmp/project/knowledge/decisions")
    plan_path = "/tmp/project/knowledge/decisions/executable-test-2026-05-19.md"
    result = validators.validate_at_claim(header, plan_path, config, text)
    assert result["rejected"] is False
    assert result["warnings"] == []


# --- Test 2: reject — missing dispatch_mode ---

def test_reject_missing_dispatch_mode():
    text = _plan_text(None, step_body="Implement the feature.")
    header = _header_for(text)
    config = _config_with_watched()
    plan_path = "/tmp/project/knowledge/decisions/executable-test.md"
    result = validators.validate_at_claim(header, plan_path, config, text)
    assert result["rejected"] is True
    assert "missing" in result["reject_reason"].lower()


# --- Test 3: reject — invalid dispatch_mode value ---

def test_reject_invalid_dispatch_mode_value():
    text = _plan_text("unknown_value", step_body="Implement the feature.")
    header = _header_for(text)
    config = _config_with_watched()
    plan_path = "/tmp/project/knowledge/decisions/executable-test.md"
    result = validators.validate_at_claim(header, plan_path, config, text)
    assert result["rejected"] is True
    assert "invalid" in result["reject_reason"].lower()


# --- Test 4: warn — manual_bootstrap in watched dir ---

def test_warn_mismatch_manual_bootstrap_in_watched_dir():
    watched_dir = "/tmp/project/knowledge/decisions"
    text = _plan_text("manual_bootstrap", step_body="Bootstrap the thing.")
    header = _header_for(text)
    config = _config_with_watched(watched_dir)
    plan_path = f"{watched_dir}/executable-test.md"
    result = validators.validate_at_claim(header, plan_path, config, text)
    assert result["rejected"] is False
    assert len(result["warnings"]) == 1
    assert result["warnings"][0]["check"] == "dispatch_mismatch"


# --- Test 5: no warn — manual_bootstrap NOT in watched dir ---

def test_no_warn_manual_bootstrap_not_in_watched_dir():
    text = _plan_text("manual_bootstrap", step_body="Bootstrap the thing.")
    header = _header_for(text)
    config = _config_with_watched("/tmp/other-project/knowledge/decisions")
    plan_path = "/tmp/project/knowledge/decisions/executable-test.md"
    result = validators.validate_at_claim(header, plan_path, config, text)
    assert result["rejected"] is False
    assert result["warnings"] == []


# --- Test 6: warn — STOP-prose in bellows mode ---

def test_warn_stop_prose_in_bellows_mode():
    text = _plan_text("bellows", step_body="The agent must do not proceed until verified.")
    header = _header_for(text)
    config = _config_with_watched()
    plan_path = "/tmp/project/knowledge/decisions/executable-test.md"
    result = validators.validate_at_claim(header, plan_path, config, text)
    assert result["rejected"] is False
    stop_warns = [w for w in result["warnings"] if w["check"] == "stop_prose"]
    assert len(stop_warns) >= 1


# --- Test 7: no warn — STOP-prose in manual_bootstrap mode ---

def test_no_warn_stop_prose_in_manual_bootstrap_mode():
    text = _plan_text("manual_bootstrap", step_body="The agent must do not proceed until verified.")
    header = _header_for(text)
    config = _config_with_watched("/tmp/other/knowledge/decisions")
    plan_path = "/tmp/project/knowledge/decisions/executable-test.md"
    result = validators.validate_at_claim(header, plan_path, config, text)
    stop_warns = [w for w in result["warnings"] if w["check"] == "stop_prose"]
    assert len(stop_warns) == 0


# --- Test 8: STOP-prose in fenced code block excluded ---

def test_stop_prose_in_fenced_code_block_excluded():
    step_body = "Here is an example:\n\n```\ndo not proceed\n```\n\nContinue with work."
    text = _plan_text("bellows", step_body=step_body)
    header = _header_for(text)
    config = _config_with_watched()
    plan_path = "/tmp/project/knowledge/decisions/executable-test.md"
    result = validators.validate_at_claim(header, plan_path, config, text)
    assert result["warnings"] == []


# --- Test 9: STOP-prose in inline code excluded ---

def test_stop_prose_in_inline_code_excluded():
    step_body = "The regex `do not proceed` is one of the patterns."
    text = _plan_text("bellows", step_body=step_body)
    header = _header_for(text)
    config = _config_with_watched()
    plan_path = "/tmp/project/knowledge/decisions/executable-test.md"
    result = validators.validate_at_claim(header, plan_path, config, text)
    assert result["warnings"] == []


# --- Test 10: STOP-prose in header/preamble excluded ---

def test_stop_prose_in_header_excluded():
    preamble = "## CEO Context\n\nThe agent should do not proceed without approval."
    text = _plan_text("bellows", step_body="Implement the feature.", preamble=preamble)
    header = _header_for(text)
    config = _config_with_watched()
    plan_path = "/tmp/project/knowledge/decisions/executable-test.md"
    result = validators.validate_at_claim(header, plan_path, config, text)
    assert result["warnings"] == []


# --- Test 11: STOP-prose in deposits block excluded ---

def test_stop_prose_in_deposits_block_excluded():
    step_body = "Implement the feature."
    deposits_block = "**Deposits:**\n- `do-not-proceed-report.md`"
    text = _plan_text("bellows", step_body=step_body, deposits_block=deposits_block)
    header = _header_for(text)
    config = _config_with_watched()
    plan_path = "/tmp/project/knowledge/decisions/executable-test.md"
    result = validators.validate_at_claim(header, plan_path, config, text)
    assert result["warnings"] == []


# --- Test 12: multiple STOP-prose patterns detected ---

def test_multiple_stop_prose_patterns_detected():
    step_body = "The agent should STOP. here.\nThen wait for confirmation before continuing."
    text = _plan_text("bellows", step_body=step_body)
    header = _header_for(text)
    config = _config_with_watched()
    plan_path = "/tmp/project/knowledge/decisions/executable-test.md"
    result = validators.validate_at_claim(header, plan_path, config, text)
    stop_warns = [w for w in result["warnings"] if w["check"] == "stop_prose"]
    assert len(stop_warns) >= 2


# --- Test 13: reject — empty dispatch_mode value ---

def test_reject_empty_dispatch_mode_value():
    # Bold-Markdown parser with empty value: **Dispatch Mode:** (nothing after)
    text = "# Test Plan\n**Dispatch Mode:**\n**Total Steps:** 1\n\n## STEP 1 — DEV\n\nDo work.\n"
    header = _header_for(text)
    config = _config_with_watched()
    plan_path = "/tmp/project/knowledge/decisions/executable-test.md"
    result = validators.validate_at_claim(header, plan_path, config, text)
    assert result["rejected"] is True
