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


# ===================================================================
# V2 — pause_for_verdict enum validator
# ===================================================================

# --- Test 14: valid pause_for_verdict values pass silently ---

def test_pause_for_verdict_valid_values_no_warning():
    """All recognized pause_for_verdict enum values produce no warning."""
    for value in ("always", "after_step_1", "after_qa_step", "after_each_step", ""):
        header = {"dispatch_mode": "bellows", "pause_for_verdict": value}
        result = validators.check_pause_for_verdict_value(header)
        assert result is None, f"Unexpected warning for valid value '{value}'"


# --- Test 15: invalid pause_for_verdict values produce WARN ---

def test_pause_for_verdict_invalid_values_warn():
    """Plausible YAML-think values that are not recognized produce a WARN."""
    for value in ("true", "yes", "after_qa", "qa_checkpoint", "1"):
        header = {"dispatch_mode": "bellows", "pause_for_verdict": value}
        result = validators.check_pause_for_verdict_value(header)
        assert result is not None, f"Expected warning for invalid value '{value}'"
        assert result["check"] == "pause_for_verdict_value"
        assert result["severity"] == "warn"
        assert value in result["message"]


# --- Test 16: absent pause_for_verdict field handled gracefully ---

def test_pause_for_verdict_absent_no_warning():
    """When pause_for_verdict is absent from header, no warning is emitted."""
    header = {"dispatch_mode": "bellows"}
    result = validators.check_pause_for_verdict_value(header)
    assert result is None


# --- Test 17: pause_for_verdict registered in validate_at_claim ---

def test_pause_for_verdict_warn_surfaces_in_validate_at_claim():
    """Invalid pause_for_verdict surfaces as a warning in validate_at_claim output."""
    text = _plan_text("bellows", step_body="Do work.")
    header = _header_for(text)
    header["pause_for_verdict"] = "true"
    config = _config_with_watched()
    plan_path = "/tmp/project/knowledge/decisions/executable-test.md"
    result = validators.validate_at_claim(header, plan_path, config, text)
    assert result["rejected"] is False
    pause_warns = [w for w in result["warnings"] if w["check"] == "pause_for_verdict_value"]
    assert len(pause_warns) == 1


# ===================================================================
# V3 — Header field type contract validator
# ===================================================================

# --- Test 18: string-typed header fields pass silently ---

def test_header_field_types_all_strings_no_warning():
    """When all enumerated fields are strings, no warning is emitted."""
    header = {"auto_close": "false", "pause_for_verdict": "always", "dispatch_mode": "bellows"}
    result = validators.check_header_field_types(header)
    assert result == []


# --- Test 19: bool-typed header field produces WARN ---

def test_header_field_types_bool_warns():
    """YAML-parsed bool value for auto_close produces a WARN."""
    header = {"auto_close": False, "dispatch_mode": "bellows"}
    result = validators.check_header_field_types(header)
    assert len(result) == 1
    assert result[0]["check"] == "header_field_type"
    assert result[0]["severity"] == "warn"
    assert "auto_close" in result[0]["message"]
    assert "bool" in result[0]["message"]


# --- Test 20: int-typed header field produces WARN ---

def test_header_field_types_int_warns():
    """YAML-parsed int value for pause_for_verdict produces a WARN."""
    header = {"pause_for_verdict": 1, "dispatch_mode": "bellows"}
    result = validators.check_header_field_types(header)
    type_warns = [w for w in result if w["check"] == "header_field_type" and "pause_for_verdict" in w["message"]]
    assert len(type_warns) == 1
    assert "int" in type_warns[0]["message"]


# --- Test 21: None-valued field handled gracefully (no warning) ---

def test_header_field_types_none_value_no_warning():
    """When a field is present with None value, it is treated as absent (no warning)."""
    header = {"auto_close": None, "dispatch_mode": "bellows"}
    result = validators.check_header_field_types(header)
    assert result == []


# --- Test 22: absent fields handled gracefully ---

def test_header_field_types_absent_fields_no_warning():
    """When enumerated fields are absent from header, no warning is emitted."""
    header = {"dispatch_mode": "bellows"}
    result = validators.check_header_field_types(header)
    assert result == []


# --- Test 23: multiple non-string fields produce multiple warnings ---

def test_header_field_types_multiple_non_string_fields():
    """Multiple non-string fields each produce their own warning."""
    header = {"auto_close": False, "pause_for_verdict": True, "dispatch_mode": 42}
    result = validators.check_header_field_types(header)
    assert len(result) == 3
    fields_warned = {w["message"].split("'")[1] for w in result}
    assert fields_warned == {"auto_close", "pause_for_verdict", "dispatch_mode"}


# --- Test 24: header field types registered in validate_at_claim ---

def test_header_field_types_warn_surfaces_in_validate_at_claim():
    """Non-string header field surfaces as a warning in validate_at_claim output."""
    text = _plan_text("bellows", step_body="Do work.")
    header = _header_for(text)
    header["auto_close"] = False  # Inject YAML-parsed bool
    config = _config_with_watched()
    plan_path = "/tmp/project/knowledge/decisions/executable-test.md"
    result = validators.validate_at_claim(header, plan_path, config, text)
    assert result["rejected"] is False
    type_warns = [w for w in result["warnings"] if w["check"] == "header_field_type"]
    assert len(type_warns) == 1
