#!/usr/bin/env python3
"""Pre-deposit plan lint. Validates plan structure before execution.

Usage: python3 scripts/plan_lint.py <plan-path>

Checks:
  (a) Header parses with valid dispatch_mode and pause_for_verdict tokens
  (b) Every step mentioning deposits has a parseable Deposits block
  (c) QA plans contain the Rule 20 banner pair

Exit 0 if all checks pass, exit 1 otherwise.
"""

import re
import sys
from pathlib import Path

BELLOWS_ROOT = Path(__file__).parent.parent.resolve()
sys.path.insert(0, str(BELLOWS_ROOT))

import gates

RECOGNIZED_DISPATCH_MODES = {"bellows", "manual_bootstrap"}
# Mirrored from bellows.py header_says_pause — do not invent
RECOGNIZED_PAUSE_TOKENS = {"always", "after_step_1", "after_qa_step"}


def lint(plan_path):
    plan_text = Path(plan_path).read_text(encoding="utf-8")
    results = []
    all_passed = True

    # (a) Header parses
    header = gates._parse_plan_header(plan_text)
    if not header:
        results.append(("FAIL", "(a) header", "plan header parse returned empty"))
        all_passed = False
    else:
        results.append(("PASS", "(a) header", "parsed"))

        dm = header.get("dispatch_mode", "")
        if dm and dm not in RECOGNIZED_DISPATCH_MODES:
            results.append(("FAIL", "(a) dispatch_mode", f"unrecognized: {dm!r} (expected: {', '.join(sorted(RECOGNIZED_DISPATCH_MODES))})"))
            all_passed = False
        elif dm:
            results.append(("PASS", "(a) dispatch_mode", dm))

        pv = header.get("pause_for_verdict", "")
        if pv and pv not in RECOGNIZED_PAUSE_TOKENS:
            results.append(("FAIL", "(a) pause_for_verdict", f"unrecognized: {pv!r} (expected: {', '.join(sorted(RECOGNIZED_PAUSE_TOKENS))})"))
            all_passed = False
        elif pv:
            results.append(("PASS", "(a) pause_for_verdict", pv))

    # Extract step numbers from plan
    clean_text = gates.strip_fenced_code_blocks(plan_text)
    step_headers = re.findall(r'^(## STEP (\d+)\b[^\n]*)', clean_text, re.MULTILINE)

    # (b) Deposits blocks: steps mentioning "deposit" must yield parseable paths
    for header_line, step_num_str in step_headers:
        step_num = int(step_num_str)
        step_text = gates._extract_step_text(plan_text, step_num)
        if not step_text:
            continue
        if "deposit" not in step_text.lower():
            continue
        deposits = gates._extract_plan_required_deposits(step_text)
        if deposits:
            results.append(("PASS", f"(b) step {step_num} deposits", f"{len(deposits)} path(s)"))
        else:
            results.append(("FAIL", f"(b) step {step_num} deposits", "step mentions deposit but **Deposits:** block yields no paths"))
            all_passed = False

    # (c) QA banner pair: QA plans must contain both template strings
    has_qa = False
    if header.get("qa_steps"):
        has_qa = True
    else:
        for header_line, _ in step_headers:
            if "qa" in header_line.lower():
                has_qa = True
                break

    if has_qa:
        banner = "Rule 20 — QA Self-Check Results"
        passed_line = "PASSED — SELF-CHECK PASSED"
        has_banner = banner in plan_text
        has_passed = passed_line in plan_text
        if has_banner and has_passed:
            results.append(("PASS", "(c) QA banner pair", "both strings present"))
        else:
            missing = []
            if not has_banner:
                missing.append("banner")
            if not has_passed:
                missing.append("PASSED line")
            results.append(("FAIL", "(c) QA banner pair", f"missing: {', '.join(missing)}"))
            all_passed = False

    for status, check, detail in results:
        print(f"{status}: {check} — {detail}")

    return 0 if all_passed else 1


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <plan-path>", file=sys.stderr)
        sys.exit(2)
    sys.exit(lint(sys.argv[1]))
