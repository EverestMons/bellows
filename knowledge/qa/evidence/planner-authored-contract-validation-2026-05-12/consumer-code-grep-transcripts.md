# Consumer Code Grep Transcripts — Planner-Authored Contract Validation

**Date:** 2026-05-12

---

## Artifact 1: Verdict File Content — `check_verdict()`

**File:** `verdict.py:160-181`
**Discovery:** grep for `re.match` in verdict.py

```python
def check_verdict(plan_slug, step_number):
    """Check if a verdict file exists in verdicts/resolved/."""
    resolved_dir = VERDICTS_DIR / "resolved"
    filename = f"verdict-{plan_slug}-step-{step_number}.md"
    filepath = resolved_dir / filename

    if not filepath.exists():
        return {"found": False}

    text = filepath.read_text()
    lines = text.strip().splitlines()
    if not lines:
        return {"found": False}

    first_line = lines[0].strip()
    match = re.match(r"^(?:verdict:\s*)?(continue|stop)$", first_line, re.IGNORECASE)
    if not match:
        return {"found": False}  # <-- SILENT SKIP: malformed verdict indistinguishable from absent verdict

    verdict = match.group(1).lower()
    reason = "\n".join(lines[1:]).strip() if len(lines) > 1 else ""
    return {"found": True, "verdict": verdict, "reason": reason}
```

**Contract assumption:** First line must be `continue`, `stop`, `verdict: continue`, or `verdict: stop` (case-insensitive). Any other first line → `{"found": False}`.

---

## Artifact 2: Verdict Filename — `_consume_verdicts()`

**File:** `bellows.py:1054-1064`
**Discovery:** grep for `re.match` in bellows.py

```python
for fname in os.listdir(resolved_dir):
    if not fname.startswith("verdict-") or not fname.endswith(".md"):
        continue
    if fname.startswith("verdict-request-"):
        continue
    # Parse slug and step from filename: verdict-{slug}-step-{N}.md
    match = re.match(r"^verdict-(.+)-step-(\d+)\.md$", fname)
    if not match:
        continue  # <-- SILENT SKIP: malformed filename silently ignored
```

**Contract assumption:** Filename must match `verdict-{slug}-step-{N}.md`. Files in wrong directory (`pending/` instead of `resolved/`) are never scanned.

---

## Artifact 3: Plan Headers — `_parse_plan_header()`

**File:** `gates.py:32-98`
**Discovery:** grep for `_parse_*` in gates.py

```python
# Strategy 1: YAML frontmatter
match = re.search(r"\A---\n(.*?)\n---\n", plan_text, re.DOTALL)
if match:
    result = {}
    for line in match.group(1).splitlines():
        if ":" in line:
            key, _, value = line.partition(":")
            key = key.strip().strip("*")
            result[key] = value.strip().strip("*").strip()
    if result:
        return result

# Strategy 2: Pipe-separated bold-Markdown header
# ... (multi-line collection logic) ...

if not header_line or "**" not in header_line:
    return {}  # <-- SILENT ACCEPTANCE: returns empty dict, downstream uses defaults
```

**Contract assumption:** File starts with YAML frontmatter OR has bold-Markdown key-value pairs after a `# Title` line. Neither format → `{}`.

---

## Artifact 4: Step Headers — `extract_total_steps()`

**File:** `bellows.py:185-191`
**Discovery:** grep for `re.findall` + `## STEP`

```python
def extract_total_steps(plan_text: str) -> int:
    plan_text = strip_fenced_code_blocks(plan_text)
    case_insensitive_count = len(re.findall(r"^## STEP\s+\d+", plan_text, re.MULTILINE | re.IGNORECASE))
    case_sensitive_count = len(re.findall(r"^## STEP\s+\d+", plan_text, re.MULTILINE))
    if case_insensitive_count > 0 and case_sensitive_count == 0:
        _log("WARN", f"⚠️ plan has step headers but case does not match...")
    return case_insensitive_count
```

**Contract assumption:** Step headers must be `## STEP N` at line start. Case-insensitive matching with warning for case mismatch. Returns 0 if no headers found.

---

## Artifact 5: Deposits Blocks — `_extract_plan_required_deposits()`

**File:** `gates.py:265-309`
**Discovery:** grep for `DEPOSITS_BLOCK_RE`

```python
# Rule 26: prefer declared **Deposits:** block when present
block_match = re.search(r'[> ]*\*\*Deposits:\*\*\s*\n(?:[> ]*\n)*((?:[> ]*-\s+.*\n?)+)', step_text)
if block_match:
    block_text = block_match.group(1)
    paths = set()
    for m in re.finditer(r'-\s+`([^`]+)`', block_text):
        paths.add(m.group(1))
    return paths
```

**Contract assumption:** `**Deposits:**` on its own line, followed by bullet list. Paths must be backtick-quoted in bullets. Legacy prose fallback if no block present.

---

## Artifact 6: Rule 20 Self-Check — `_gate_rule_20_self_check()`

**File:** `gates.py:312-359`
**Discovery:** grep for `_gate_rule_20`

```python
banner = "Rule 20 — QA Self-Check Results"
# ...
if banner not in content:
    continue  # skip to next deposit file

# Banner found — check for PASSED line after the banner position
banner_pos = content.index(banner)
lines_after_banner = content[banner_pos:].splitlines()
for line in lines_after_banner:
    if line.startswith("PASSED — SELF-CHECK PASSED"):
        return  # Gate passes
```

**Contract assumption:** QA deposit must contain literal string `"Rule 20 — QA Self-Check Results"` followed by line starting with `"PASSED — SELF-CHECK PASSED"`.

---

## Artifact 7: Agent Output Markers — `parse()`

**File:** `parser.py:28-42`
**Discovery:** grep for `re.search` in parser.py

```python
ceo_flags = []
match = re.search(r"### Flags for CEO\s*\n(.*?)(?=\n##|\Z)", result_text, re.DOTALL)
if match:
    for line in match.group(1).splitlines():
        line = line.strip()
        if line.startswith("- "):
            txt = line[2:].strip()
            if txt and txt.lower() not in ("none", "n/a"):
                ceo_flags.append(txt)

verdict_requested = {"requested": False, "reason": None}
vr_match = re.search(r"^VERDICT_REQUESTED:\s*(.+)$", result_text, re.MULTILINE)
if vr_match:
    verdict_requested = {"requested": True, "reason": vr_match.group(1).strip()}
```

**Contract assumption:** `### Flags for CEO` section with bulleted items. `VERDICT_REQUESTED: <reason>` on its own line. Both optional — absent markers produce empty/false defaults.
