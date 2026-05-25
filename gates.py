"""Mechanical validation gates. Runs after each step and flags anomalies."""

import logging
import os
import re

import yaml

logger = logging.getLogger(__name__)


def strip_fenced_code_blocks(text: str) -> str:
    """Remove fenced code blocks (``` ... ```) from text, preserving line structure.

    Used by plan-text parsers to prevent example/fixture headers inside code fences
    from being parsed as structural elements.
    Duplicated from bellows.py — keep in sync.
    """
    return re.sub(r"^```[^\n]*\n.*?^```[^\n]*$", "", text, flags=re.MULTILINE | re.DOTALL)


# Files that are always expected and don't need explicit mention in plan steps
SCOPE_ALLOWLIST = [
    "agent-prompt-feedback.md",
    "PROJECT_STATUS.md",
    ".gitkeep",
]

# Basenames matching these prefixes are plan lifecycle files and are always allowed
SCOPE_ALLOWLIST_PREFIXES = ("in-progress-", "verdict-pending-", "halted-")

# Read-class tools whose denials do NOT block agent execution. Agents fall back
# to bash equivalents (grep/rg, find/ls, cat) when these are denied. Per BACKLOG #2
# diagnostic at knowledge/research/no-permission-denials-taxonomy-2026-04-28.md.
READ_CLASS_TOOLS = {"Grep", "Glob", "Read", "mcp__vexp__run_pipeline"}

# Bash commands matching the GUARDRAILS-prescribed git index-lock cleanup are exempt
# from no_permission_denials blocking. The denial originates from Claude Code's runtime,
# not bellows — agents following governance/GUARDRAILS.md Development → Git Operations
# rule 1 should not be penalised. Closes shop_backlog: guardrails-vs-bash-gate-contradiction-git-locks.
_LOCK_GLOB = r'\.git/(?:index\.lock|"index "\*\.lock|"index "\[0-9\]\*)'
GUARDRAILS_BASH_EXEMPTION_PATTERN = re.compile(
    r'(?:^|;\s*)rm\s+-f\s+'
    + _LOCK_GLOB
    + r'(?:\s+' + _LOCK_GLOB + r')*'
    + r'(?:\s+2>/dev/null)?'
    + r'\s*(?:;|$)'
)

# Hedging keywords for Rule 22(d) QA verification-table scan
HEDGING_KEYWORDS = [
    "pending", "inferred", "extrapolated", "estimated", "approximate",
    "skipped", "assumed", "close enough", "should pass", "would pass", "not run",
]

# Positive-status tokens for identifying positive-status rows in QA verification tables.
# Glyph-agnostic: bounded matching (cell equality) prevents false positives.
POSITIVE_STATUS_TOKENS = ["\u2705", "OK", "PASS", "done", "complete", "verified"]

_TABLE_SEPARATOR_RE = re.compile(r'^\|[\s\-:]+(\|[\s\-:]+)*\|?\s*$')


def _is_positive_status_row(line):
    """True if the markdown table row contains a positive-status token in any cell."""
    if "|" not in line:
        return False
    cells = [c.strip() for c in line.split("|")]
    for cell in cells:
        for token in POSITIVE_STATUS_TOKENS:
            if token == "\u2705":
                if "\u2705" in cell:
                    return True
            else:
                if cell.lower() == token.lower():
                    return True
    return False


def _parse_plan_header(plan_text):
    """Extract plan header fields. Tries YAML frontmatter first, then bold-Markdown format.

    Supported formats:
    1. YAML frontmatter: file starts with ``---\\n...\\n---\\n``
    2. Bold-Markdown header: ``**Key:** value | **Key:** value`` on a single line
       OR ``**Key:** value`` on each of multiple consecutive lines, after a
       ``# Title`` line. Blank lines between fields are tolerated; a ``---``
       horizontal rule or any non-bold non-blank line terminates the header block.
    Returns {} if neither format is found.
    """
    # Strategy 1: YAML frontmatter
    match = re.search(r"\A---\n(.*?)\n---\n", plan_text, re.DOTALL)
    if match:
        try:
            result = yaml.safe_load(match.group(1))
            if isinstance(result, dict) and result:
                return result
        except yaml.YAMLError as e:
            logger.warning("YAML frontmatter parse failed, falling through to bold-Markdown: %s", e)
        # YAML block found but didn't produce a usable dict — strip it for Strategy 2
        plan_text = plan_text[match.end():]

    # Strategy 2: Pipe-separated bold-Markdown header
    # Expects: line 1 = "# Title", line 2 = "**Key:** value | **Key:** value | ..."
    lines = plan_text.split("\n")
    header_line = None
    for i, line in enumerate(lines):
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("# "):
            # Collect all consecutive bold-Markdown header lines after title.
            # Handles both single-line pipe-format (one line of **key:** val | **key:** val)
            # and multi-line bold (each **key:** val on its own line, separated by blanks).
            # The collected lines are joined with " | " so the existing pipe-separator
            # regex below parses them uniformly. Closes BACKLOG 2026-05-10
            # multi-line bold header parser gap.
            header_lines = []
            for j in range(i + 1, len(lines)):
                candidate = lines[j].strip()
                if not candidate:
                    # Skip blank lines (both before first field and between fields)
                    continue
                if candidate.startswith("---"):
                    # Horizontal rule terminates the header block
                    break
                if candidate.startswith("**"):
                    header_lines.append(candidate)
                else:
                    # Non-bold, non-blank line — header block is over
                    break
            header_line = " | ".join(header_lines) if header_lines else None
            break
        else:
            # File doesn't start with # — no pipe-format header
            break

    if not header_line or "**" not in header_line:
        return {}

    result = {}
    for m in re.finditer(r'\*\*([^:*]+):\*\*\s*([^|]*?)(?:\s*\||$)', header_line):
        key = m.group(1).strip().lower().replace(" ", "_")
        value = m.group(2).strip()
        result[key] = value
    return result


def check(parsed, plan_text, step_number, project_path, files_changed=None, wt_path=None):
    """Run all gates and return a result dict.

    Returns:
        {
            "passed": bool,       # True only if zero failures from gates 1-5, 8
            "failures": [{"gate": str, "evidence": str}, ...],
            "is_qa_step": bool,
            "files_changed": list,
            "plan_header": dict,
            "verdict_requested": {"requested": bool, "body": str|None},
        }
    """
    if files_changed is None:
        files_changed = []

    failures = []
    header = _parse_plan_header(plan_text)

    # Gate 1: receipt status
    _gate_receipt_status(parsed, failures)
    # Gate 2: CEO flags
    _gate_ceo_flags(parsed, failures)
    # Gate 3: no errors
    _gate_no_errors(parsed, failures)
    # Gate 4: no permission denials
    _gate_no_permission_denials(parsed, failures)
    # Gate 5: deposit exists
    _gate_deposit_exists(parsed, failures, project_path, plan_text=plan_text, step_number=step_number, wt_path=wt_path, plan_header=header)
    # Gate 6: QA step detection (informational)
    is_qa_step = _gate_is_qa_step(plan_text, step_number)
    # Gate 6b: Rule 20 self-check verification (blocking, QA steps only)
    _gate_rule_20_self_check(is_qa_step, plan_text, step_number, project_path, parsed, failures, wt_path=wt_path)
    # Gate 6c: Rule 22 verification (blocking)
    _gate_rule_22_verification(is_qa_step, plan_text, step_number, project_path, parsed, failures, wt_path=wt_path)
    # Gate 7: file change audit (informational)
    _gate_file_change_audit(files_changed)
    # Gate 8: scope check
    _gate_scope_check(plan_text, step_number, files_changed, failures)
    vr = parsed.get("verdict_requested", {})
    requested = vr.get("requested", False)
    request_body = vr.get("reason")

    return {
        "passed": len(failures) == 0,
        "failures": failures,
        "is_qa_step": is_qa_step,
        "files_changed": files_changed,
        "plan_header": header,
        "verdict_requested": {"requested": requested, "body": request_body},
    }


def _gate_receipt_status(parsed, failures):
    status = parsed.get("receipt_status", "Unknown")
    if status != "Complete":
        failures.append({"gate": "receipt_status", "evidence": status})


def _gate_ceo_flags(parsed, failures):
    flags = parsed.get("ceo_flags", [])
    if flags:
        failures.append({"gate": "ceo_flags", "evidence": "; ".join(flags)})


def _gate_no_errors(parsed, failures):
    if parsed.get("is_error", False):
        failures.append({
            "gate": "no_errors",
            "evidence": parsed.get("error", "unknown error"),
        })


def _gate_no_permission_denials(parsed, failures):
    denials = parsed.get("permission_denials", [])
    blocking = []
    for d in denials:
        if isinstance(d, dict):
            tool_name = d.get("tool_name")
            if tool_name in READ_CLASS_TOOLS:
                continue
            # Exempt Bash denials matching the GUARDRAILS-prescribed git lock cleanup.
            # Command text is in tool_input.command per Claude Code's denial payload schema.
            if tool_name == "Bash":
                cmd = d.get("tool_input", {}).get("command", "") if isinstance(d.get("tool_input"), dict) else ""
                if GUARDRAILS_BASH_EXEMPTION_PATTERN.search(cmd):
                    continue
            blocking.append(d)
        else:
            # String-form denial (legacy) has no tool_name — default to blocking
            blocking.append(d)
    if blocking:
        first = blocking[0] if isinstance(blocking[0], str) else str(blocking[0])
        failures.append({
            "gate": "no_permission_denials",
            "evidence": f"{len(blocking)} blocking denial(s): {first}",
        })


def _normalize_deposit_path(path, project_path):
    """Normalize deposit path to canonical project-relative form for comparison.

    Handles four input forms:
      - Absolute under project_path:  /Users/.../bellows/knowledge/foo.md → knowledge/foo.md
      - Absolute under parent dir:    /Users/.../bellows/knowledge/foo.md → bellows/knowledge/foo.md
      - Project-prefixed relative:    bellows/knowledge/foo.md           → knowledge/foo.md
      - Already project-relative:     knowledge/foo.md                   → knowledge/foo.md (unchanged)
    """
    abs_project = os.path.abspath(project_path)
    if os.path.isabs(path):
        prefix = abs_project + os.sep
        if path.startswith(prefix):
            return path[len(prefix):]
        parent_prefix = os.path.dirname(abs_project) + os.sep
        if path.startswith(parent_prefix):
            return path[len(parent_prefix):]
    project_basename = os.path.basename(abs_project)
    if path.startswith(project_basename + os.sep):
        return path[len(project_basename) + 1:]
    return path


def _resolve_deposit_path(path, project_path, wt_path=None):
    """Check if a deposit path exists, trying multiple path resolution strategies.

    Returns the resolved absolute path string if the path exists (as a file or
    directory) at any of the following, or None if not found:
      0. worktree-first (if wt_path provided and differs from project_path)
      1. path as-is (absolute or CWD-relative)
      2. os.path.join(project_path, path) — relative to project root
      3. os.path.join(os.path.dirname(project_path), path) — path includes project dir name
    """
    # Strategy 0 (worktree-first): if wt_path is provided AND differs from project_path,
    # try resolving against the worktree first — this is where the agent just wrote files
    if wt_path is not None and wt_path != project_path:
        abs_project = os.path.abspath(project_path)
        project_basename = os.path.basename(project_path)
        if os.path.isabs(path):
            # Absolute path under project_path: strip prefix to get project-relative remainder
            prefix = abs_project + os.sep
            if path.startswith(prefix):
                wt_candidate = os.path.join(wt_path, path[len(prefix):])
            else:
                # Absolute path not under project_path — fall through to relative handling
                wt_candidate = os.path.join(wt_path, path)
        elif path.startswith(project_basename + os.sep):
            wt_candidate = os.path.join(wt_path, path[len(project_basename) + 1:])
        else:
            wt_candidate = os.path.join(wt_path, path)
        if os.path.isfile(wt_candidate) or os.path.isdir(wt_candidate):
            return wt_candidate

    if os.path.isfile(path) or os.path.isdir(path):
        return os.path.abspath(path)
    p2 = os.path.join(project_path, path)
    if os.path.isfile(p2) or os.path.isdir(p2):
        return os.path.abspath(p2)
    p3 = os.path.join(os.path.dirname(project_path), path)
    if os.path.isfile(p3) or os.path.isdir(p3):
        return os.path.abspath(p3)
    return None


def _gate_deposit_exists(parsed, failures, project_path, plan_text=None, step_number=None, wt_path=None, plan_header=None):
    result_text = parsed.get("result_text", "")
    match = re.search(r"### Files Deposited\s*\n(.*?)(?:\n###|\Z)", result_text, re.DOTALL)

    # Collect agent-declared paths and check they exist on disk
    agent_declared = set()
    if match:
        section = match.group(1)
        for line in section.splitlines():
            line = line.strip()
            if not line or not line.startswith("- "):
                continue
            m = re.match(r'`([^`]+)`', line[2:].strip())
            path = m.group(1) if m else line[2:].strip().strip("`")
            if path:
                agent_declared.add(_normalize_deposit_path(path, project_path))
                if _resolve_deposit_path(path, project_path, wt_path=wt_path) is None:
                    failures.append({"gate": "deposit_exists", "evidence": f"missing: {path}"})

    # Frontmatter-first: if plan_header provides a deposits list, use it as authoritative
    frontmatter_deposits = plan_header.get("deposits") if plan_header is not None else None
    if frontmatter_deposits is not None and isinstance(frontmatter_deposits, list):
        for path in frontmatter_deposits:
            if _normalize_deposit_path(path, project_path) not in agent_declared and _resolve_deposit_path(path, project_path, wt_path=wt_path) is None:
                failures.append({"gate": "deposit_exists", "evidence": f"plan-required deposit missing (frontmatter): {path}"})
    elif plan_text and step_number is not None:
        # Prose fallback: extract deposits from step text
        step_text = _extract_step_text(plan_text, step_number)
        if step_text:
            for path in _extract_plan_required_deposits(step_text):
                if _normalize_deposit_path(path, project_path) not in agent_declared and _resolve_deposit_path(path, project_path, wt_path=wt_path) is None:
                    failures.append({"gate": "deposit_exists", "evidence": f"plan-required deposit missing (not declared by agent): {path}"})


def _extract_step_text(plan_text: str, step_number: int):
    """Extract text of a single step from a plan, bounded by ## STEP N headers.

    Returns the step text or None if no match.
    Duplicated in verdict.py::_extract_step_text_from_plan to avoid circular import — keep in sync.
    """
    plan_text = strip_fenced_code_blocks(plan_text)
    pattern = rf"^## STEP {step_number}\b.*?(?=^## STEP |\Z)"
    match = re.search(pattern, plan_text, re.DOTALL | re.MULTILINE)
    return match.group(0) if match else None


def _filter_transient_paths(paths):
    """Drop paths whose basename starts with `_staging_` — these are transient
    atomic-deposit filenames that exist only between write and move and are not
    deliverables. Per LESSONS 2026-05-18 strike-4 entry."""
    return {p for p in paths if not os.path.basename(p).startswith("_staging_")}


def _extract_plan_required_deposits(step_text):
    """Extract file paths explicitly required by deposit instructions in the plan step text.

    Filters out `_staging_*` basenames (transient atomic-deposit filenames mentioned in
    step prose as part of describing the deposit mechanism, never persistent on disk).

    If a **Deposits:** block (Rule 26 convention) is present, extracts only the
    backtick-quoted paths from its bullet list and ignores legacy prose patterns.
    Falls back to legacy prose-matching regexes when no block is present.
    """
    # Rule 26: prefer declared **Deposits:** block when present
    # [> ]* handles optional blockquote prefixes in plan step text
    block_match = re.search(r'[> ]*\*\*Deposits:\*\*\s*\n(?:[> ]*\n)*((?:[> ]*-\s+.*\n?)+)', step_text)
    if block_match:
        block_text = block_match.group(1)
        paths = set()
        for m in re.finditer(r'-\s+`([^`]+)`', block_text):
            paths.add(m.group(1))
        # Explicit "- none" means no deposits required
        return _filter_transient_paths(paths)

    # Inline format: **Deposits:** `- /path/a`, `- /path/b`.
    # Handles plans where the Planner emits deposits on the same line as the marker
    inline_match = re.search(r'[> ]*\*\*Deposits:\*\*[ \t]+(.+)', step_text)
    if inline_match:
        inline_text = inline_match.group(1)
        paths = set()
        for m in re.finditer(r'`-\s+([^`]+)`', inline_text):
            paths.add(m.group(1))
        if paths:
            return _filter_transient_paths(paths)

    # Legacy fallback: prose-matching regexes
    paths = set()
    # Pattern 1: Deposit ... to `path` (backtick-quoted — most explicit form)
    for m in re.finditer(r'Deposit[^\n`]*?to\s+`([^`]+)`', step_text, re.IGNORECASE):
        candidate = m.group(1).strip()
        if candidate:
            paths.add(candidate)
    # Pattern 2: Deposit ... to path.md (unquoted, must contain a directory separator)
    for m in re.finditer(r'Deposit[^\n]*?to\s+(\S+\.md)', step_text, re.IGNORECASE):
        candidate = m.group(1).strip().rstrip('.,;)').strip('`')
        if '/' in candidate:
            paths.add(candidate)
    # Pattern 3: with open("path.md", "w") canonical Python write
    for m in re.finditer(r'with open\(["\']([^"\']+\.md)["\'],\s*["\']w["\']', step_text):
        paths.add(m.group(1).strip())
    return _filter_transient_paths(paths)


def _gate_rule_20_self_check(is_qa_step, plan_text, step_number, project_path, parsed, failures, wt_path=None):
    """Verify QA-deposited reports contain a Rule 20 self-check banner with PASSED status."""
    if not is_qa_step:
        return

    step_text = _extract_step_text(plan_text, step_number)
    if not step_text:
        return

    deposit_paths = _extract_plan_required_deposits(step_text)
    md_paths = [p for p in deposit_paths if p.endswith(".md")]
    if not md_paths:
        failures.append({"gate": "rule_20_self_check", "evidence": "no QA deposit contains Rule 20 self-check banner"})
        return

    banner = "Rule 20 — QA Self-Check Results"

    # Item #7 fix (2026-05-24, Shape 7A): scope banner scan to the QA report (first .md deposit),
    # matching the pattern used by _gate_rule_22_verification. Previously iterated ALL md_paths,
    # which caused false-positives when a non-QA deposit (e.g., agent-prompt-feedback.md)
    # contained the banner text as incidental prose.
    qa_report_path = md_paths[0]
    resolved = _resolve_deposit_path(qa_report_path, project_path, wt_path=wt_path)
    if resolved is None:
        failures.append({"gate": "rule_20_self_check", "evidence": f"deposit file unreadable: {qa_report_path} (file not found)"})
        return

    try:
        with open(resolved, "r", encoding="utf-8") as f:
            content = f.read()
    except (FileNotFoundError, UnicodeDecodeError, OSError) as e:
        failures.append({"gate": "rule_20_self_check", "evidence": f"deposit file unreadable: {qa_report_path} ({e})"})
        return

    if banner not in content:
        failures.append({"gate": "rule_20_self_check", "evidence": "no QA deposit contains Rule 20 self-check banner"})
        return

    # Banner found — scan ALL remaining content for the PASSED line, tolerating
    # whitespace, decoration lines, and fenced-block indentation.
    # Per LESSONS 2026-05-17 strike-3 and 2026-05-18 strike-5 entries.
    banner_pos = content.index(banner)
    remaining = content[banner_pos:]
    # The PASSED line may be anywhere in the remaining content, optionally
    # preceded by whitespace on its line. Use re.MULTILINE so ^ matches each
    # line start, and \s* tolerates leading indentation/whitespace.
    if re.search(r'^\s*\*{0,2}\s*PASSED\s+—\s+SELF-CHECK\s+PASSED', remaining, re.MULTILINE):
        return  # Gate passes
    failures.append({"gate": "rule_20_self_check", "evidence": f"banner present but PASSED line missing in {qa_report_path}"})


def _gate_rule_22_verification(is_qa_step, plan_text, step_number, project_path, parsed, failures, wt_path=None):
    """Rule 22 mechanical checks: (a) deposits exist, (c) verification table, (d) no hedging."""
    step_text = _extract_step_text(plan_text, step_number)
    if not step_text:
        return

    deposit_paths = _extract_plan_required_deposits(step_text)

    # (a) Check all plan-declared deposits exist on disk
    for dep_path in deposit_paths:
        resolved = _resolve_deposit_path(dep_path, project_path, wt_path=wt_path)
        if resolved is None:
            failures.append({
                "gate": "rule_22_verification",
                "evidence": f"(a) Plan-declared deposit missing: {dep_path}",
            })

    if not is_qa_step:
        return

    # For QA steps: independent QA-report open for (c) and (d)
    md_paths = [p for p in deposit_paths if p.endswith(".md")]
    if not md_paths:
        return

    qa_report_path = md_paths[0]
    resolved = _resolve_deposit_path(qa_report_path, project_path, wt_path=wt_path)
    if resolved is None:
        return  # (a) already flagged missing file

    try:
        with open(resolved, "r", encoding="utf-8") as f:
            content = f.read()
    except (FileNotFoundError, UnicodeDecodeError, OSError):
        return

    lines = content.splitlines()

    # (c) Verification table: no ❌ rows, no data rows missing a positive status.
    # Item #6 fix (2026-05-24, Shape 6C):
    #   (a) Section-scoped: only inspect tables inside sections whose ## header contains
    #       "verification" (case-insensitive). QA reports contain non-verification tables
    #       (failure classifications, commit stats) that should not be inspected.
    #   (b) Status-token broadened: use _is_positive_status_row() which accepts ✅ AND
    #       text tokens (PASS, OK, done, complete, verified) with bounded cell equality.
    #       Previously accepted only ✅ as positive status, false-positiving on rows like
    #       "| ... | PASS |".
    in_data = False
    in_verification_section = False
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        # Track section transitions via ## headers.
        if stripped.startswith("## "):
            in_verification_section = "verification" in stripped.lower()
            in_data = False
            continue
        if "|" not in stripped:
            in_data = False
            continue
        if _TABLE_SEPARATOR_RE.match(stripped):
            in_data = True
            continue
        if not in_data:
            continue  # Header row
        if not in_verification_section:
            continue  # Skip tables outside verification sections
        # Data row inside a verification-section table
        if "\u274c" in stripped:
            failures.append({
                "gate": "rule_22_verification",
                "evidence": f"(c) QA verification table row {i}: {stripped[:120]}. See {qa_report_path} line {i}.",
            })
        elif not _is_positive_status_row(line):
            failures.append({
                "gate": "rule_22_verification",
                "evidence": f"(c) QA verification table row {i} missing status: {stripped[:120]}. See {qa_report_path} line {i}.",
            })

    # (d) No hedging keywords in positive-status rows
    for i, line in enumerate(lines, 1):
        if _is_positive_status_row(line):
            lower = line.lower()
            for kw in HEDGING_KEYWORDS:
                if kw in lower:
                    failures.append({
                        "gate": "rule_22_verification",
                        "evidence": f"(d) Hedging keyword '{kw}' in positive-status row: {line.strip()[:120]}. See {qa_report_path} line {i}.",
                    })
                    break


def _gate_is_qa_step(plan_text, step_number):
    plan_text = strip_fenced_code_blocks(plan_text)
    pattern = rf"^## STEP {step_number}\b[^\n]*"
    match = re.search(pattern, plan_text, re.MULTILINE)
    if match:
        return "qa" in match.group(0).lower()
    return False


def _gate_file_change_audit(files_changed):
    # Informational gate — records the files_changed list.
    # The list is passed through to the result dict by check().
    return files_changed


def _gate_scope_check(plan_text, step_number, files_changed, failures):
    if not files_changed:
        return

    # Extract the step's section from the plan
    step_text = _extract_step_text(plan_text, step_number)
    if not step_text:
        return

    out_of_scope = []
    for fpath in files_changed:
        basename = os.path.basename(fpath)
        if basename in SCOPE_ALLOWLIST:
            continue
        if any(basename.startswith(p) for p in SCOPE_ALLOWLIST_PREFIXES):
            continue
        if fpath in step_text or basename in step_text:
            continue
        out_of_scope.append(fpath)

    if out_of_scope:
        context = step_text[:200]
        failures.append({
            "gate": "scope_check",
            "evidence": f"out-of-scope files: {', '.join(out_of_scope)} | plan step context: {context}",
        })
