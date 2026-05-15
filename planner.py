"""Calls Planner via claude -p subprocess. Returns continue/rewrite/escalate decision."""

import json
import os
import pathlib
import subprocess
import time
import uuid
from datetime import datetime

BELLOWS_ROOT = pathlib.Path(__file__).parent.resolve()

GOVERNANCE_ROOT = "/Users/marklehn/Desktop/GitHub"
PLANNER_TEMPLATE_PATH = f"{GOVERNANCE_ROOT}/PLANNER_TEMPLATE.md"
COMPANY_MD_PATH = f"{GOVERNANCE_ROOT}/COMPANY.md"


def build_system_prompt() -> str:
    template_path = pathlib.Path(PLANNER_TEMPLATE_PATH)
    company_path = pathlib.Path(COMPANY_MD_PATH)

    if not template_path.exists():
        raise FileNotFoundError(f"PLANNER_TEMPLATE.md not found at {PLANNER_TEMPLATE_PATH}")
    if not company_path.exists():
        raise FileNotFoundError(f"COMPANY.md not found at {COMPANY_MD_PATH}")

    template_text = template_path.read_text()
    company_text = company_path.read_text()
    return template_text + "\n\n---\n\n" + company_text


def build_context_envelope(
    parsed: dict,
    plan_text: str,
    step_number: int,
    project_brief: str = "",
    project_status: str = "",
) -> str:
    envelope = (
        f"## Plan (current step: {step_number})\n{plan_text}\n\n"
        f"## Step Output\n{parsed['result_text']}\n\n"
        f"## Output Receipt Summary\n"
        f"- Status: {parsed['receipt_status']}\n"
        f"- Escalate: {parsed['escalate']}\n"
        f"- CEO Flags: {parsed['ceo_flags']}\n"
        f"- Cost: ${parsed['cost_usd']:.4f}\n"
        f"- Permission Denials: {len(parsed['permission_denials'])}"
    )

    if project_brief:
        envelope += f"\n\n## Project Brief\n{project_brief}"

    if project_status:
        envelope += f"\n\n## Project Status\n{project_status}"

    envelope += (
        "\n\n## Your Task\n"
        "Based on the step output and Output Receipt above, decide the next action. "
        'Respond with a JSON object only — no prose, no markdown fences. '
        'Schema: {"decision": "continue" | "rewrite" | "escalate", '
        '"reason": "one sentence", '
        '"next_step_prompt": "full revised prompt string or null if continue or escalate"}'
    )

    return envelope


def build_consult_file(
    parsed: dict,
    plan_text: str,
    step_number: int,
    project_brief: str = "",
    project_status: str = "",
) -> str:
    consult_path = f"/tmp/bellows-consult-{str(uuid.uuid4())}.md"
    content = (
        "# Bellows — Planner Consultation\n\n"
        "You are the Eluvian Project Planner. Read the context below and return a JSON decision.\n\n"
        + build_system_prompt()
        + "\n\n---\n\n"
        + build_context_envelope(parsed, plan_text, step_number, project_brief, project_status)
    )
    pathlib.Path(consult_path).write_text(content)
    return consult_path


def _log_consultation(decision: dict, model: str, duration_ms: int, error: str = ""):
    """Append consultation result to logs/planner-consultation.jsonl."""
    log_path = BELLOWS_ROOT / "logs" / "planner-consultation.jsonl"
    log_path.parent.mkdir(exist_ok=True)
    entry = {
        "timestamp": datetime.now().isoformat(),
        "model": model,
        "decision": decision.get("decision"),
        "reason": decision.get("reason"),
        "duration_ms": duration_ms,
        "error": error,
    }
    with open(log_path, "a") as f:
        f.write(json.dumps(entry) + "\n")


def _is_auth_error(raw: dict) -> bool:
    """Check if the subprocess result indicates a transient auth error."""
    return raw.get("is_error", False) and "401" in raw.get("result", "")


def consult(
    parsed: dict,
    plan_text: str,
    step_number: int,
    model: str,
    project_brief: str = "",
    project_status: str = "",
) -> dict:
    consult_path = build_consult_file(parsed, plan_text, step_number, project_brief, project_status)
    start = time.time()
    try:
        prompt = (
            f"Read {consult_path} carefully. You are the Eluvian Project Planner. "
            "Return ONLY a JSON object — no prose, no markdown fences. "
            'Schema: {"decision": "continue" | "rewrite" | "escalate", '
            '"reason": "one sentence", '
            '"next_step_prompt": "full revised prompt string or null"}'
        )
        last_error = ""
        for attempt in range(2):
            try:
                result = subprocess.run(
                    ["claude", "-p", prompt, "--output-format", "json", "--model", model, "--allowedTools", "Read"],
                    cwd="/tmp",
                    capture_output=True,
                    text=True,
                    timeout=120,
                )
            except subprocess.TimeoutExpired:
                fallback = {"decision": "escalate", "reason": "Planner consultation timed out", "next_step_prompt": None}
                _log_consultation(fallback, model, int((time.time() - start) * 1000), error="timeout")
                return fallback

            try:
                raw = json.loads(result.stdout)
            except json.JSONDecodeError:
                last_error = "Subprocess stdout was not valid JSON"
                if attempt == 0:
                    time.sleep(5)
                    continue
                break

            if _is_auth_error(raw):
                last_error = "Authentication error (401)"
                if attempt == 0:
                    time.sleep(5)
                    continue
                break

            # Parse the planner's decision from the result text
            try:
                text = raw["result"].strip()
                lines = text.splitlines()
                lines = [line for line in lines if not line.startswith("```")]
                text = "\n".join(lines).strip()
                decision = json.loads(text)
                _log_consultation(decision, model, int((time.time() - start) * 1000))
                return decision
            except (json.JSONDecodeError, KeyError):
                fallback = {"decision": "continue", "reason": "Planner response was not valid JSON — defaulting to continue", "next_step_prompt": None}
                _log_consultation(fallback, model, int((time.time() - start) * 1000), error="invalid JSON response")
                return fallback

        # Retry exhausted — transient failure, fall back to continue
        fallback = {"decision": "continue", "reason": f"Planner unavailable — defaulting to continue ({last_error})", "next_step_prompt": None}
        _log_consultation(fallback, model, int((time.time() - start) * 1000), error=last_error)
        return fallback
    finally:
        if os.path.exists(consult_path):
            os.unlink(consult_path)
