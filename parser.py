"""Parses claude -p JSON output. Extracts Output Receipt status and escalation signals."""

import re


def parse(raw: dict) -> dict:
    session_id = raw.get("session_id")
    is_error = bool(raw.get("is_error", False))
    stop_reason = raw.get("stop_reason", "")
    result_text = raw.get("result", "")
    cost_usd = float(raw.get("total_cost_usd", 0.0))
    turns = raw.get("num_turns")
    permission_denials = raw.get("permission_denials", [])

    # Infer receipt_status from stop_reason (Phase 4 fix — text scan was unreliable)
    if is_error:
        receipt_status = "Blocked"
    elif stop_reason == "end_turn":
        receipt_status = "Complete"
    elif stop_reason == "max_tokens":
        receipt_status = "Partial"
    else:
        receipt_status = "Unknown"

    # Extract ceo_flags — safety-net only. Primary flag detection is in gates.py
    # via plan headers (pause_for_verdict field) and agent-authored verdict-request files.
    # Only the ### Flags for CEO bulleted form is recognized here.
    # "None"/"N/A" variants (case-insensitive) are excluded.
    ceo_flags = []
    match = re.search(r"### Flags for CEO\s*\n(.*?)(?=\n##|\Z)", result_text, re.DOTALL)
    if match:
        for line in match.group(1).splitlines():
            line = line.strip()
            if line.startswith("- "):
                txt = line[2:].strip()
                if txt and txt.lower() not in ("none", "n/a"):
                    ceo_flags.append(txt)

    # Extract VERDICT_REQUESTED marker — agent-initiated pause signal
    verdict_requested = {"requested": False, "reason": None}
    vr_match = re.search(r"^VERDICT_REQUESTED:\s*(.+)$", result_text, re.MULTILINE)
    if vr_match:
        verdict_requested = {"requested": True, "reason": vr_match.group(1).strip()}

    # Extract ### Ledger Updates section — daemon-owned ledgers Phase 1+2+3.
    # Mirrors the ### Flags for CEO extraction pattern (parser.py:30–37).
    # Subsections: #### Prompt Feedback (Phase 1), #### Project Status (Phase 2),
    #              #### Forward Register (Phase 3).
    ledger_updates = {"feedback": None, "project_status": None, "forward": None}
    lu_match = re.search(
        r"### Ledger Updates\s*\n(.*?)(?=\n## |\Z)", result_text, re.DOTALL
    )
    if lu_match:
        lu_body = lu_match.group(1)
        fb_match = re.search(
            r"#### (?:Prompt )?Feedback\s*\n(.*?)(?=\n#### |\Z)", lu_body, re.DOTALL
        )
        if fb_match:
            fb_text = fb_match.group(1).strip()
            if fb_text and fb_text.lower() not in ("none", "n/a"):
                ledger_updates["feedback"] = fb_text
        ps_match = re.search(
            r"#### Project Status\s*\n(.*?)(?=\n#### |\Z)", lu_body, re.DOTALL
        )
        if ps_match:
            ps_text = ps_match.group(1).strip()
            if ps_text and ps_text.lower() not in ("none", "n/a"):
                ledger_updates["project_status"] = ps_text
        # Phase 3: #### Forward Register (also matches #### FORWARD Additions)
        fw_match = re.search(
            r"#### (?:Forward Register|FORWARD(?: Additions)?)\s*\n(.*?)(?=\n#### |\Z)",
            lu_body, re.DOTALL,
        )
        if fw_match:
            fw_text = fw_match.group(1).strip()
            if fw_text and fw_text.lower() not in ("none", "n/a"):
                ledger_updates["forward"] = fw_text

    escalate = receipt_status == "Blocked" or bool(ceo_flags) or is_error

    return {
        "session_id": session_id,
        "is_error": is_error,
        "stop_reason": stop_reason,
        "result_text": result_text,
        "cost_usd": cost_usd,
        "turns": turns,
        "permission_denials": permission_denials,
        "receipt_status": receipt_status,
        "ceo_flags": ceo_flags,
        "escalate": escalate,
        "verdict_requested": verdict_requested,
        "ledger_updates": ledger_updates,
    }


def is_clean(parsed: dict) -> bool:
    return (
        not parsed["escalate"]
        and parsed["stop_reason"] == "end_turn"
        and parsed["receipt_status"] in ("Complete", "Partial")
    )
