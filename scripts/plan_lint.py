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


def _parse_qa_steps(qa_steps_raw):
    """Parse qa_steps header value into a set of ints, mirroring gates._gate_is_qa_step."""
    try:
        if isinstance(qa_steps_raw, list):
            return {int(x) for x in qa_steps_raw}
        s = str(qa_steps_raw).strip().strip("[]")
        return {int(tok.strip()) for tok in s.split(",") if tok.strip()}
    except (ValueError, TypeError):
        return set()


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

    # (e) Step heading case guard: catch vacuous-pass from title-case headings
    ci_step_headers = re.findall(r'^(##\s+step\s+(\d+)\b[^\n]*)', clean_text, re.IGNORECASE | re.MULTILINE)
    if not step_headers and header.get("qa_steps"):
        msg = "header declares qa_steps but no uppercase '## STEP N' heading found — step checks (b)/(d) were skipped (vacuous pass)"
        if ci_step_headers:
            msg += "; found lowercase '## Step N' headings, use uppercase '## STEP N'"
        results.append(("FAIL", "(e) step heading format", msg))
        all_passed = False
    elif not step_headers and ci_step_headers:
        print("WARN: found '## Step N' headings but no uppercase '## STEP N' — consider using uppercase for lint coverage")

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

    # (d) Scope block: if present, must parse to at least one file or prefix
    for header_line, step_num_str in step_headers:
        step_num = int(step_num_str)
        step_text = gates._extract_step_text(plan_text, step_num)
        if not step_text:
            continue
        scope_block_present = re.search(r'[> ]*\*\*Scope:\*\*', step_text)
        if not scope_block_present:
            continue
        scope_files, scope_prefixes = gates._extract_plan_scope(step_text)
        if scope_files or scope_prefixes:
            results.append(("PASS", f"(d) step {step_num} scope", f"{len(scope_files)} file(s), {len(scope_prefixes)} prefix(es)"))
        else:
            results.append(("FAIL", f"(d) step {step_num} scope", "**Scope:** block present but parses to zero entries"))
            all_passed = False

    # WARN: step mentions "test" but declares no test scope
    for header_line, step_num_str in step_headers:
        step_num = int(step_num_str)
        step_text = gates._extract_step_text(plan_text, step_num)
        if not step_text:
            continue
        if not re.search(r'\btest\b', step_text, re.IGNORECASE):
            continue
        scope_files, scope_prefixes = gates._extract_plan_scope(step_text)
        has_test_scope = any("test_" in f and f.endswith(".py") for f in scope_files)
        has_test_prefix = any(p.rstrip("/").split("/")[-1] == "tests" or p == "tests/" for p in scope_prefixes)
        has_test_in_text = bool(re.search(r'test_\w+\.py', step_text)) or "tests/" in step_text
        if not has_test_scope and not has_test_prefix and not has_test_in_text:
            print(f"WARN: step {step_num} mentions tests but declares no test scope")

    # WARN: qa_steps ↔ step-label cross-check
    qa_steps_raw = header.get("qa_steps", "") if header else ""
    if qa_steps_raw:
        qa_steps_set = _parse_qa_steps(qa_steps_raw)
        qa_labeled_steps = {int(sn) for hl, sn in step_headers if "qa" in hl.lower()}
        for n in sorted(qa_labeled_steps - qa_steps_set):
            print(f"WARN: step {n} is QA-labeled but absent from qa_steps={qa_steps_raw!r} — it will not be Rule 20/22 gated")
        for n in sorted(qa_steps_set - qa_labeled_steps):
            print(f"WARN: qa_steps lists step {n} but step {n} is not QA-labeled — it will be gated as QA (plan-133 trap)")

    for status, check, detail in results:
        print(f"{status}: {check} — {detail}")

    return 0 if all_passed else 1


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <plan-path>", file=sys.stderr)
        sys.exit(2)
    sys.exit(lint(sys.argv[1]))
