# BACKLOG Freshness Check Script — Blueprint

**Date:** 2026-05-26
**Plan:** executable-leftover-after-ship-tooling-blueprint-2026-05-26
**Step:** 1 (SA)
**Status:** Complete

---

## Overview

Script location: `scripts/check_backlog_freshness.py`
Style reference: `scripts/migrate_config.py` (shebang, module docstring, module-level constants, single entry point, `if __name__ == "__main__"` guard).
Target size: 150-250 LOC. Python stdlib only. Read-only (no mutation outside report deposit). Idempotent. Exit 0 always.

---

## 1. Constants

```python
BELLOWS_ROOT = Path(__file__).parent.parent.resolve()
BACKLOG_PATH = BELLOWS_ROOT / "knowledge" / "BACKLOG.md"
PROJECT_STATUS_PATH = BELLOWS_ROOT / "PROJECT_STATUS.md"
DEFAULT_WINDOW_DAYS = 14
DEFAULT_OUTPUT_DIR = BELLOWS_ROOT / "knowledge" / "research"
```

---

## 2. Parsing

### 2A. BACKLOG Open Section

**Goal:** Split the `## Open` section into individual entries, extracting date and fingerprint for each.

**Section extraction:** Read `BACKLOG.md`. Locate `## Open` heading. Collect all lines from after this heading until `---` (horizontal rule) or `## Closed`. This is the Open section text.

**Entry splitting regex:**

```python
OPEN_ENTRY_RE = re.compile(
    r'^- \*\*Added (\d{4}-\d{2}-\d{2}):\*\*\s+(.+?)(?=\n- \*\*Added |\n---|\n## |\Z)',
    re.MULTILINE | re.DOTALL
)
```

Each match yields:
- `date`: group(1) — the date the entry was filed
- `text`: group(2) — the full entry body

**Fingerprint extraction** (applied to the first 300 characters of each entry's text):

```python
def extract_fingerprint(text: str) -> set[str]:
    """Extract distinctive terms from entry text for matching."""
    terms = set()
    # Backtick-delimited identifiers (highest specificity)
    for m in re.finditer(r'`([^`]+)`', text[:500]):
        cleaned = m.group(1).strip('()').lower()
        if len(cleaned) >= 3:
            terms.add(cleaned)
    # Hyphenated compound words (e.g., step-state-resume, precondition-failure)
    for m in re.finditer(r'\b([a-zA-Z][\w]*(?:-[a-zA-Z][\w]*){1,})\b', text[:300]):
        terms.add(m.group(1).lower())
    # Underscore identifiers (e.g., _extract_plan_required_deposits)
    for m in re.finditer(r'\b(_?[a-z][a-z0-9]*(?:_[a-z0-9]+)+)\b', text[:300], re.IGNORECASE):
        terms.add(m.group(1).lower())
    # Title words (first sentence, ≥ 5 chars, excluding stopwords)
    first_sentence = re.split(r'\.\s', text[:200])[0]
    STOPWORDS = {
        'added', 'after', 'before', 'between', 'could', 'during',
        'existing', 'first', 'making', 'never', 'originally', 'other',
        'should', 'their', 'there', 'these', 'where', 'which', 'would',
    }
    for word in re.findall(r'[a-zA-Z][a-zA-Z0-9]{4,}', first_sentence):
        w = word.lower()
        if w not in STOPWORDS:
            terms.add(w)
    return terms
```

The fingerprint is a set of lowercase distinctive terms (backtick identifiers, hyphenated compounds, underscore identifiers, title words). These are used for substring matching against candidate texts.

### 2B. BACKLOG Closed Section

**Goal:** Parse Closed entries to detect Open entries that are duplicates of already-closed topics.

**Section extraction:** Locate `## Closed` heading. Collect all lines from after this heading to end of file.

**Entry splitting regex:**

```python
CLOSED_ENTRY_RE = re.compile(
    r'^- \*\*Closed (\d{4}-\d{2}-\d{2})(?:\s*\([^)]*\))?\s*:\*\*\s+(.+?)(?=\n- \*\*Closed |\Z)',
    re.MULTILINE | re.DOTALL
)
```

Each match yields:
- `date`: group(1) — closure date
- `text`: group(2) — full entry body

Apply the same `extract_fingerprint()` to first 300 characters of each Closed entry.

**Rationale for including Closed entries:** Ground-truth case 3 (Phase 3b read-side) had its ship event on 2026-05-01 — outside any reasonable git-log window. The only detectable signal is that the BACKLOG Closed section already contains an entry about "Phase 3b/3c DB step-state-resume" that directly overlaps the Open entry's topic. Scanning Closed entries catches this "filed-as-new-but-already-evaluated" pattern.

### 2C. PROJECT_STATUS Completed Section

**Goal:** Extract recent Completed entries and their Reference executable slugs.

**Section extraction:** Read `PROJECT_STATUS.md`. Locate `## Completed` heading. Collect all lines until the next `## ` heading.

**Entry regex:**

```python
PS_ENTRY_RE = re.compile(
    r'^- (\d{4}-\d{2}-\d{2})(?:\s*\([^)]*\))?\s*:\s*(.+?)(?=\n- \d{4}-\d{2}-\d{2}|\n## |\Z)',
    re.MULTILINE | re.DOTALL
)
```

Each match yields:
- `date`: group(1)
- `text`: group(2) — full entry body

**Date filter:** Only retain entries whose date falls within the `--window-days` window (default 14 days from today).

**Slug extraction** (from each entry's text):

```python
REFERENCE_SLUG_RE = re.compile(r'(?:Reference:\s*`?)(executable-[\w-]+-\d{4}-\d{2}-\d{2})')
```

Extract the slug, then tokenize it:

```python
def tokenize_slug(slug: str) -> set[str]:
    """Split executable slug into matching tokens."""
    # Remove 'executable-' prefix and date suffix
    body = re.sub(r'^executable-', '', slug)
    body = re.sub(r'-\d{4}-\d{2}-\d{2}$', '', body)
    return {t.lower() for t in body.split('-') if len(t) >= 3}
```

### 2D. Git Log

**Goal:** Extract recent commit subjects containing BACKLOG closure signals.

**Command:**

```python
subprocess.run(
    ["git", "--no-pager", "log", f"--since={window_days} days ago",
     "--pretty=format:%h %s"],
    capture_output=True, text=True, cwd=str(BELLOWS_ROOT)
)
```

**Line parsing:**

```python
GIT_LINE_RE = re.compile(r'^([0-9a-f]{7,}) (.+)$')
```

**Closure signal filter** — retain only commits whose subject matches:

```python
CLOSURE_SIGNAL_RE = re.compile(
    r'closes?\s+BACKLOG|backlog\s+hygiene|BACKLOG.*(?:close|retire|defer)',
    re.IGNORECASE
)
```

**N=14 justification:** The longest observed baton-propagation lag in the 4 ground-truth cases is 4 days (mcp\_\_vexp\_\_: filed 2026-05-22, shipped 2026-05-25, caught 2026-05-26). N=14 provides >3x margin, covering two full work-weeks. Shorter windows (N=7) risk missing entries where a ship event and a session gap coincide; longer windows (N=30) add noise without materially improving recall. Case 3 (Phase 3b, ship event 25 days prior) is caught by BACKLOG Closed scanning, not the git window.

---

## 3. Matching Algorithm

For each Open BACKLOG entry, score candidates from three sources. A candidate that exceeds the source-specific threshold is surfaced in the report.

### 3A. Scoring Function

```python
def score_overlap(entry_fingerprint: set[str], candidate_text: str) -> int:
    """Count how many fingerprint terms appear as substrings in candidate_text."""
    text_lower = candidate_text.lower()
    return sum(1 for term in entry_fingerprint if term in text_lower)
```

### 3B. Source-Specific Matching

| Source | Pre-filter | Candidate text | Threshold | Rationale |
|--------|-----------|---------------|-----------|-----------|
| Git log | Subject matches `CLOSURE_SIGNAL_RE` | Full commit subject | ≥ 2 | Pre-filtered to closure-signal commits; full subject contains both the feature name and the BACKLOG reference |
| PROJECT_STATUS | Date within window, has Reference slug | Slug token set checked against fingerprint | ≥ 2 slug tokens in fingerprint | Executable slugs encode the feature name in hyphenated form |
| BACKLOG Closed | All entries (no date window) | First 300 chars of Closed entry | ≥ 3 | Larger candidate set requires higher threshold to avoid false positives |

**PS slug matching detail:** For each PS entry with a Reference slug, tokenize the slug via `tokenize_slug()`. Score = count of slug tokens that appear in the Open entry's fingerprint set. If score ≥ 2, it's a candidate.

### 3C. Per-Entry Candidate Collection

```
For each Open entry:
    candidates = []

    # Source 1: Git log (closure-signal commits)
    for sha, subject in closure_commits:
        if score_overlap(entry.fingerprint, subject) >= 2:
            candidates.append(("git", sha, subject))

    # Source 2: PROJECT_STATUS (windowed entries with Reference slug)
    for ps_entry in ps_entries_in_window:
        if ps_entry.slug:
            slug_tokens = tokenize_slug(ps_entry.slug)
            overlap = slug_tokens & entry.fingerprint
            if len(overlap) >= 2:
                candidates.append(("project_status", ps_entry.date, ps_entry.slug))

    # Source 3: BACKLOG Closed (duplicate detection)
    for closed_entry in closed_entries:
        if score_overlap(entry.fingerprint, closed_entry.text[:300]) >= 3:
            candidates.append(("backlog_closed", closed_entry.date, closed_entry.text[:80]))

    entry.action = "investigate-as-shipped" if candidates else "no-match"
```

---

## 4. Output Format

Deposited to `knowledge/research/backlog-freshness-check-<YYYY-MM-DD>.md`.

```markdown
# BACKLOG Freshness Check — <YYYY-MM-DD>

**Window:** <N> days | **Open entries scanned:** <count> | **Candidates surfaced:** <count> | **No-match:** <count>

---

## Entry 1: <first 80 chars of entry text>...

**Filed:** <date> | **Action:** investigate-as-shipped

### Candidates

- **[git]** `<SHA>` — `<commit subject>`
  Match terms: <list of overlapping terms>
- **[project_status]** <date> — `<slug>`
  Match terms: <list of overlapping terms>

---

## Entry 2: <first 80 chars of entry text>...

**Filed:** <date> | **Action:** no-match

*(no candidates found)*

---
```

Rules:
- One `## Entry N` section per Open entry, in BACKLOG order
- Candidate subsections show source type, evidence excerpt, and the specific matching terms
- Entries with `no-match` get a short "(no candidates found)" line
- Header summary gives the quick triage counts

---

## 5. CLI

```python
def main():
    parser = argparse.ArgumentParser(
        description="Check BACKLOG Open entries for evidence of already-shipped closures."
    )
    parser.add_argument(
        "--window-days", type=int, default=DEFAULT_WINDOW_DAYS,
        help=f"Days of git/PROJECT_STATUS history to scan (default: {DEFAULT_WINDOW_DAYS})"
    )
    parser.add_argument(
        "--output-path", type=str, default=None,
        help="Override output file path (default: knowledge/research/backlog-freshness-check-<date>.md)"
    )
    args = parser.parse_args()

    output_path = args.output_path or str(
        DEFAULT_OUTPUT_DIR / f"backlog-freshness-check-{date.today().isoformat()}.md"
    )

    # ... run pipeline, write report ...
    print(f"Report written to {output_path}")
```

Zero required arguments. Exit 0 always (informational script). Typical invocation:

```bash
cd bellows && python scripts/check_backlog_freshness.py
cd bellows && python scripts/check_backlog_freshness.py --window-days 30
```

---

## 6. Ground-Truth Trace

### Case 1 — set-to-list (`_extract_plan_required_deposits`)

**Open entry title:** `_extract_plan_required_deposits()` returns a `set` making `md_paths[0]` hash-dependent

**Fingerprint (sample):** `{_extract_plan_required_deposits, set, md_paths[0], hash-dependent, extract, plan, required, deposits, returns, making}`

**Git match:**
- Commit `4e805fa`: `fix(gates): _extract_plan_required_deposits set→list — deterministic md_paths[0] selection — closes BACKLOG capability`
- Closure signal: `closes BACKLOG` ✓
- Overlap: `_extract_plan_required_deposits` ✓, `set` ✓ → score ≥ 2 ✓
- **Result: candidate surfaced**

**PS match:**
- Entry 2026-05-25, slug: `executable-extract-plan-required-deposits-set-to-list-2026-05-25`
- Slug tokens: `{extract, plan, required, deposits, set, list}`
- Overlap with fingerprint: `extract` ✓, `plan` ✓, `required` ✓, `deposits` ✓, `set` ✓ → score = 5 ≥ 2 ✓
- **Result: candidate surfaced**

### Case 2 — precondition-failure verdict-request field

**Open entry title:** Step-counter loop after precondition-failure verdict

**Fingerprint (sample):** `{step-counter, precondition-failure, verdict, counter, loop, after}`

**Git match:**
- Commit `0a90e26`: `fix(bellows): precondition-failure verdict-request field — retries step instead of advancing (item #5)`
- Closure signal: `closes BACKLOG` is NOT in this subject. However, `backlog hygiene` commit `71c98b0`: `chore: backlog hygiene — close items 1, 3, 4 (hardening batch ship)` — this doesn't match case 2 either.
- Actually, the DIRECT ship commit for case 2 is `0a90e26` with subject `fix(bellows): precondition-failure verdict-request field — retries step instead of advancing (item #5)`. This does NOT contain a BACKLOG closure signal.
- **Git: no match** (commit lacks closure signal phrase)

**BACKLOG Closed match:**
- Closed entry at line 56: `Closed 2026-05-24: Step-counter loop after precondition-failure verdict (originally 2026-05-21). Shipped via executable-precondition-failure-field-2026-05-24...`
- Overlap: `step-counter` ✓, `precondition-failure` ✓, `verdict` ✓ → score = 3 ≥ 3 ✓
- **Result: candidate surfaced via Closed duplicate detection**

**Note:** Case 2 is a duplicate-after-ship pattern (same topic already has a Closed entry), not a "commit says closes BACKLOG but Open entry wasn't moved" pattern. The Closed-entry scanning catches it.

### Case 3 — Phase 3b read-side step-state-resume

**Open entry title:** Phase 3b step-state-resume (DB read-side)

**Fingerprint (sample):** `{phase, step-state-resume, read-side, originally}`

**Git match:** No commit within 14 days contains `closes BACKLOG` + Phase 3b keywords. Ship event was 2026-05-01 (outside window). **Git: no match.**

**PS match:** No PROJECT_STATUS entry within 14 days references Phase 3b. **PS: no match.**

**BACKLOG Closed match:**
- Closed entry at line ~147 (per scope findings): `Closed 2026-05-01: Phase 3b/3c DB step-state-resume slug-collision...`
- Overlap: `phase` ✓, `step-state-resume` ✓, `originally` may or may not appear → score ≥ 2, but threshold is 3.
- ALSO: the 2026-05-26 retirement entry at line 50 (which exists because this case was CAUGHT): `Closed 2026-05-26 (RETIRE): Phase 3b step-state-resume (DB read-side)...`
- Overlap with the 2026-05-01 entry against the Open entry: `phase` ✓, `step-state-resume` ✓. Score = 2, below threshold of 3.

**Threshold adjustment needed:** The Closed-entry threshold of 3 would MISS this case because the distinctive terms are limited (`phase` + `step-state-resume` = 2 terms). Two options:

**(A) Lower Closed threshold to 2 and add a minimum-term-length filter.** Require that at least one matching term is ≥ 8 characters (filtering out short generic words). `step-state-resume` is 18 chars → qualifies. This prevents false positives from short common words while catching the Phase 3b case.

**(B) Add explicit compound-phrase matching.** Extract multi-word phrases like "Phase 3b" (consecutive capitalized word + alphanumeric) and match as units. "Phase 3b" appears in both the Open entry and the Closed entry.

**Recommended: Option (A).** Simpler to implement. Revised Closed-entry matching rule:

> Score ≥ 2, AND at least one matching term is ≥ 8 characters long.

Verification against the 6 currently-Open entries (false-positive check):
- Entry 1 (worktree teardown cherry-pick): fingerprint terms include `cherry-pick`, `worktree`, `teardown`, `project_status.md`. No Closed entry matches ≥ 2 of these with one ≥ 8 chars, because no Closed entry discusses worktree teardown cherry-pick on dirty files.
- Entry 2 (parallel-diagnostic cherry-pick): similar — no matching Closed entry.
- Entry 3 (status UI): terms include `bellows`, `status`, `replace`, `terminal`. No Closed entry about status UI.
- Entry 4 (parenthetical qualifiers): terms include `parenthetical`, `_extract_plan_required_deposits`. The set-to-list Closed entry mentions `_extract_plan_required_deposits` but the parenthetical-qualifier entry is about a different bug in the same function. Score: 1 (`_extract_plan_required_deposits`). Below threshold of 2. **Safe.**
- Entry 5 (rate-limit): terms include `rate-limit`, `_consume_verdicts`, `no-match`. The drain-failure Closed entry mentions `_consume_verdicts` but is about a different bug. Score: 1. **Safe.**
- Entry 6 (case-sensitivity): terms include `_extract_step_text`, `case-sensitivity`, `regex`. No Closed entry about this. **Safe.**

**All 6 Open entries: no false positives.** Revised threshold confirmed safe.

### Case 4 — mcp\_\_vexp\_\_ READ\_CLASS\_TOOLS extension

**Open entry title:** MCP tool denials (`mcp__vexp__run_pipeline`, `mcp__vexp__get_context_capsule`) not on `READ_CLASS_TOOLS` exemption list

**Fingerprint (sample):** `{mcp__vexp__run_pipeline, mcp__vexp__get_context_capsule, read_class_tools, exemption, denials, tool}`

**Git match:**
- Commit `9473cf7`: `fix(gates): extend READ_CLASS_TOOLS with 5 vexp read-class tools — closes BACKLOG mcp_tool_denials`
- Closure signal: `closes BACKLOG` ✓
- Overlap: `read_class_tools` in subject as `READ_CLASS_TOOLS` (lowercased match) ✓, `tool` in subject ✓ → score ≥ 2 ✓
- **Result: candidate surfaced**

**PS match:**
- Entry 2026-05-25, slug: `executable-mcp-read-class-tools-extension-2026-05-25`
- Slug tokens: `{mcp, read, class, tools, extension}`
- Overlap with fingerprint: `mcp` is a substring of `mcp__vexp__run_pipeline` in the fingerprint? No — we check if slug tokens are IN the fingerprint set, not substring. `mcp` is not in the fingerprint set. But `tools` is not either (it's `tool` not `tools`).
- Alternative: check if slug tokens appear as substrings in the Open entry text (first 300 chars). `read` appears ✓, `class` appears ✓, `tools` appears ✓, `mcp` appears ✓. This is a simpler and more robust approach.
- **Revised PS matching:** score = count of slug tokens that appear as substrings in the Open entry's first 300 chars of text. Score = 4 ≥ 2 ✓.
- **Result: candidate surfaced**

### Ground-Truth Summary

| Case | Git | PS | Closed | Caught? |
|------|-----|-------|--------|---------|
| 1 — set-to-list | ✓ (score 2) | ✓ (score 5) | n/a | Yes |
| 2 — precondition-failure | — | — | ✓ (score 3) | Yes |
| 3 — Phase 3b | — | — | ✓ (score 2, one term ≥ 8 chars) | Yes |
| 4 — mcp\_\_vexp\_\_ | ✓ (score 2) | ✓ (score 4) | n/a | Yes |

All 4 ground-truth cases caught. Zero false positives against 6 currently-Open entries.

---

## 7. Revised Matching Thresholds (Final)

| Source | Pre-filter | Threshold |
|--------|-----------|-----------|
| Git log | Subject matches `CLOSURE_SIGNAL_RE` | `score_overlap(fingerprint, subject) >= 2` |
| PROJECT_STATUS | Date in window, has Reference slug | ≥ 2 slug tokens appear as substrings in entry text[:300] |
| BACKLOG Closed | All entries | `score_overlap(fingerprint, closed_text[:300]) >= 2` AND at least one matching term has `len >= 8` |

---

## 8. Constraints Summary

- Python stdlib only (pathlib, re, subprocess, argparse, datetime)
- Read-only: no mutation outside the report file deposit
- Idempotent: re-running overwrites the same-date report
- Exit 0 always (informational; non-zero reserved for future enforcement mode)
- Target 150-250 LOC
- Match style of `scripts/migrate_config.py` (shebang, docstring, constants, main function, `__main__` guard)

---

## Output Receipt

**Agent:** Bellows Systems Analyst
**Step:** 1
**Status:** Complete

### What Was Done

Drafted a detailed script blueprint for `scripts/check_backlog_freshness.py` covering parsing logic (4 sources: BACKLOG Open, BACKLOG Closed, PROJECT_STATUS Completed, git log), matching algorithm with source-specific thresholds, output format, CLI interface, and ground-truth traces for all 4 recurrence cases. Traced the algorithm by hand against all 4 ground-truth cases and verified zero false positives against the 6 currently-Open BACKLOG entries.

### Files Deposited

- `knowledge/research/leftover-after-ship-tooling-blueprint-2026-05-26.md` — this blueprint

### Files Created or Modified (Code)

- None (blueprint only, no code changes)

### Decisions Made

- **Added BACKLOG Closed section as a fourth matching source** (not in original plan scope but required to catch Case 3 where the ship event predates the git window). The Phase 3b recurrence's only detectable signal is the existing Closed entry about the same topic.
- **Revised Closed-entry threshold from 3 to 2-with-length-guard** after ground-truth trace showed the original threshold=3 would miss Case 3. The revised rule (≥ 2 matching terms, at least one ≥ 8 chars) catches all 4 cases with zero false positives.
- **PS slug matching uses substring-in-entry-text** rather than set intersection against fingerprint terms, because slug tokens are often fragments (e.g., `mcp`) that don't appear as standalone fingerprint terms but do appear in the entry text.
- **N=14 confirmed** with justification: 3.5x margin on the longest observed baton-propagation lag; Cases 1, 2, 4 are caught within this window; Case 3 is caught by Closed-section scanning regardless of window size.

### Flags for CEO

- None

### Flags for Next Step

- The blueprint adds a fourth source (BACKLOG Closed entries) not mentioned in the original plan prompt. DEV should implement all 4 sources.
- Case 2 (precondition-failure) is caught by Closed-entry duplicate detection, not by git closure-signal matching — the ship commit (`0a90e26`) does not contain a "closes BACKLOG" phrase. This is expected: case 2 is a duplicate-after-ship pattern (the Closed section already has an entry), not a "commit says closes but Open wasn't moved" pattern.
- The PS slug matching approach (substring-in-text, not set-intersection) is simpler but may need a minimum slug-token length filter (≥ 3 chars) to avoid matching common short tokens. The DEV should verify this against the full PS history.
- The script deposits a report but does NOT move BACKLOG entries. The Planner reads the report and decides actions. This is deliberate: Layer 1 dispatches, Layer 3 judges.
