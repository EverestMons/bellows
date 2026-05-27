#!/usr/bin/env python3
"""Check BACKLOG Open entries for evidence of already-shipped closures.

⚠️  HALTED EXPERIMENT — DO NOT EVOLVE WITH PURE TERM-MATCHING  ⚠️

This script was retired 2026-05-27 as an inadequate solution to the
"leftover after ship" detection problem. Two implementation iterations
both halted at Rule 22 (b) substance check:

  - v1 (title-word fingerprints):           6/6 entries flagged, 39 candidates
  - v2 (high-distinctiveness fingerprints): 6/6 entries flagged, 37 candidates

Term-matching cannot distinguish same-function-different-bug, shared
project names, or slug-token substring collisions without semantic
understanding. All 4 ground-truth recurrences (set→list,
precondition-failure-field, Phase 3b read-side, mcp__vexp__) are
caught by the algorithm trace, but the false-positive rate against
current Open entries makes the script no better than manual triage.

The manual Phase 1.5 grep (catch rate: 5/5 over 30 days, ~5s cost
per entry) remains the working solution.

REVISIT TRIGGER: capability-addition framing only. If a
semantic-comparison primitive becomes available (LLM-based same-bug
detection, embeddings for entry similarity), reconsider. Pure
term-matching iterations should NOT be reopened.

Full session post-mortem and revisit criteria:
  - bellows/knowledge/BACKLOG.md       (2026-05-27 Closed entry)
  - LESSONS.md                          (2026-05-26 follow-up note)
  - bellows/NEXT_SESSION.md             (session-10 summary)

Bellows daemon does NOT run this script. It is reference-only.

Scans four sources (git log, PROJECT_STATUS Completed, BACKLOG Closed,
BACKLOG Open fingerprints) and surfaces candidate matches where an Open
entry may already have been shipped. Deposits a markdown report.

Usage:  cd bellows && python scripts/check_backlog_freshness.py
        cd bellows && python scripts/check_backlog_freshness.py --window-days 30
"""

import argparse
import re
import subprocess
from datetime import date, timedelta
from pathlib import Path

BELLOWS_ROOT = Path(__file__).parent.parent.resolve()
BACKLOG_PATH = BELLOWS_ROOT / "knowledge" / "BACKLOG.md"
PROJECT_STATUS_PATH = BELLOWS_ROOT / "PROJECT_STATUS.md"
DEFAULT_WINDOW_DAYS = 14
DEFAULT_OUTPUT_DIR = BELLOWS_ROOT / "knowledge" / "research"

OPEN_ENTRY_RE = re.compile(
    r'^- \*\*Added (\d{4}-\d{2}-\d{2}):\*\*\s+(.+?)(?=\n- \*\*Added |\n---|\n## |\Z)',
    re.MULTILINE | re.DOTALL,
)
CLOSED_ENTRY_RE = re.compile(
    r'^- \*\*Closed (\d{4}-\d{2}-\d{2})(?:\s*\([^)]*\))?\s*:\*\*\s+(.+?)(?=\n- \*\*Closed |\Z)',
    re.MULTILINE | re.DOTALL,
)
PS_ENTRY_RE = re.compile(
    r'^- (\d{4}-\d{2}-\d{2})(?:\s*\([^)]*\))?\s*:\s*(.+?)(?=\n- \d{4}-\d{2}-\d{2}|\n## |\Z)',
    re.MULTILINE | re.DOTALL,
)
GIT_LINE_RE = re.compile(r'^([0-9a-f]{7,}) (.+)$')
CLOSURE_SIGNAL_RE = re.compile(
    r'closes?\s+BACKLOG|backlog\s+hygiene|BACKLOG.*(?:close|retire|defer)',
    re.IGNORECASE,
)
REFERENCE_SLUG_RE = re.compile(
    r'(?:Reference:\s*`?)(executable-[\w-]+-\d{4}-\d{2}-\d{2})'
)


def extract_fingerprint(text):
    """Extract high-distinctiveness terms from entry text for matching."""
    terms = set()
    # Rule 1: Backtick-delimited identifiers (length >= 5)
    for m in re.finditer(r'`([^`]+)`', text[:500]):
        cleaned = m.group(1).strip('()').lower()
        if len(cleaned) >= 5:
            terms.add(cleaned)
    # Rule 2: Hyphenated compounds (total length >= 12)
    for m in re.finditer(r'\b([a-zA-Z][\w]*(?:-[a-zA-Z][\w]*){1,})\b', text[:300]):
        compound = m.group(1).lower()
        if len(compound) >= 12:
            terms.add(compound)
    # Rule 3: Underscore identifiers (length >= 8, >= 2 underscores)
    for m in re.finditer(r'\b(_?[a-z][a-z0-9]*(?:_[a-z0-9]+)+)\b', text[:300],
                         re.IGNORECASE):
        ident = m.group(1).lower()
        if len(ident) >= 8 and ident.count('_') >= 2:
            terms.add(ident)
    # Rule 4: Executable slugs cited in text
    for m in re.finditer(r'(executable-[\w-]+-\d{4}-\d{2}-\d{2})', text[:500]):
        terms.add(m.group(1).lower())
    return terms


def score_overlap(fingerprint, candidate_text):
    """Count how many fingerprint terms appear as substrings in candidate_text."""
    text_lower = candidate_text.lower()
    return sum(1 for term in fingerprint if term in text_lower)


def tokenize_slug(slug):
    """Split executable slug into matching tokens."""
    body = re.sub(r'^executable-', '', slug)
    body = re.sub(r'-\d{4}-\d{2}-\d{2}$', '', body)
    return {t.lower() for t in body.split('-') if len(t) >= 3}


def parse_open_entries(backlog_text):
    """Parse Open section entries from BACKLOG."""
    m = re.search(r'^## Open\s*\n', backlog_text, re.MULTILINE)
    if not m:
        return []
    start = m.end()
    end = re.search(r'\n---|\n## ', backlog_text[start:])
    section = backlog_text[start:start + end.start()] if end else backlog_text[start:]
    entries = []
    for em in OPEN_ENTRY_RE.finditer(section):
        entries.append({
            'date': em.group(1), 'text': em.group(2),
            'fingerprint': extract_fingerprint(em.group(2)),
        })
    return entries


def parse_closed_entries(backlog_text):
    """Parse Closed section entries from BACKLOG."""
    m = re.search(r'^## Closed\s*\n', backlog_text, re.MULTILINE)
    if not m:
        return []
    section = backlog_text[m.end():]
    entries = []
    for em in CLOSED_ENTRY_RE.finditer(section):
        entries.append({'date': em.group(1), 'text': em.group(2)})
    return entries


def parse_ps_entries(ps_text, window_days):
    """Parse PROJECT_STATUS Completed entries within the time window."""
    m = re.search(r'^## Completed\s*\n', ps_text, re.MULTILINE)
    if not m:
        return []
    start = m.end()
    end = re.search(r'\n## ', ps_text[start:])
    section = ps_text[start:start + end.start()] if end else ps_text[start:]
    cutoff = date.today() - timedelta(days=window_days)
    entries = []
    for em in PS_ENTRY_RE.finditer(section):
        entry_date = date.fromisoformat(em.group(1))
        if entry_date >= cutoff:
            slug_match = REFERENCE_SLUG_RE.search(em.group(2))
            entries.append({
                'date': em.group(1), 'text': em.group(2),
                'slug': slug_match.group(1) if slug_match else None,
            })
    return entries


def get_closure_commits(window_days):
    """Get git commits with BACKLOG closure signals within window."""
    result = subprocess.run(
        ["git", "--no-pager", "log", f"--since={window_days} days ago",
         "--pretty=format:%h %s"],
        capture_output=True, text=True, cwd=str(BELLOWS_ROOT),
    )
    commits = []
    for line in result.stdout.splitlines():
        m = GIT_LINE_RE.match(line)
        if m and CLOSURE_SIGNAL_RE.search(m.group(2)):
            commits.append((m.group(1), m.group(2)))
    return commits


def find_candidates(open_entries, closure_commits, ps_entries, closed_entries):
    """Score and collect candidate matches for each Open entry."""
    for entry in open_entries:
        candidates = []
        fp = entry['fingerprint']
        text_300 = entry['text'][:300]
        # Source 1: Git log — threshold >= 1 (was >= 2)
        for sha, subject in closure_commits:
            if score_overlap(fp, subject) >= 1:
                matching = sorted(t for t in fp if t in subject.lower())
                candidates.append(("git", sha, subject, matching))
        # Source 2: PROJECT_STATUS — slug tokens >= 6 chars, threshold >= 1 (was >= 2)
        for ps in ps_entries:
            if ps['slug']:
                slug_tokens = tokenize_slug(ps['slug'])
                text_lower = text_300.lower()
                overlap = sorted(t for t in slug_tokens
                                 if len(t) >= 6 and t in text_lower)
                if len(overlap) >= 1:
                    candidates.append(("project_status", ps['date'],
                                       ps['slug'], overlap))
        # Source 3: BACKLOG Closed — new v2 rule
        for closed in closed_entries:
            closed_text = closed['text'][:300]
            matching = sorted(t for t in fp if t in closed_text.lower())
            long_match = any(len(t) >= 12 for t in matching)
            # Backtick-id condition: same backtick identifier in both entries
            backtick_match = False
            if matching and not long_match:
                open_bt = {m.group(1).strip('()').lower()
                           for m in re.finditer(r'`([^`]+)`', entry['text'][:500])
                           if len(m.group(1).strip('()')) >= 5}
                closed_bt = {m.group(1).strip('()').lower()
                             for m in re.finditer(r'`([^`]+)`', closed_text)
                             if len(m.group(1).strip('()')) >= 5}
                backtick_match = bool(
                    open_bt & closed_bt & set(matching))
            if matching and (long_match or backtick_match):
                candidates.append(("backlog_closed", closed['date'],
                                   closed['text'][:80].replace('\n', ' '),
                                   matching))
        entry['candidates'] = candidates
        entry['action'] = "investigate-as-shipped" if candidates else "no-match"


def generate_report(open_entries, window_days):
    """Generate the freshness check markdown report."""
    today = date.today().isoformat()
    total = len(open_entries)
    surfaced = sum(1 for e in open_entries if e['action'] == "investigate-as-shipped")
    lines = [
        f"# BACKLOG Freshness Check — {today}", "",
        f"**Window:** {window_days} days | **Open entries scanned:** {total}"
        f" | **Candidates surfaced:** {surfaced} | **No-match:** {total - surfaced}",
        "", "---",
    ]
    for i, entry in enumerate(open_entries, 1):
        title = entry['text'][:80].replace('\n', ' ')
        lines += ["", f"## Entry {i}: {title}...", "",
                   f"**Filed:** {entry['date']} | **Action:** {entry['action']}"]
        if entry['candidates']:
            lines += ["", "### Candidates", ""]
            for source, ref, detail, terms in entry['candidates']:
                term_str = ", ".join(terms)
                if source == "git":
                    lines.append(f"- **[git]** `{ref}` — `{detail}`")
                elif source == "project_status":
                    lines.append(f"- **[project_status]** {ref} — `{detail}`")
                else:
                    lines.append(f"- **[backlog_closed]** {ref} — {detail}")
                lines.append(f"  Match terms: {term_str}")
        else:
            lines += ["", "*(no candidates found)*"]
        lines += ["", "---"]
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser(
        description="Check BACKLOG Open entries for evidence of already-shipped closures."
    )
    parser.add_argument(
        "--window-days", type=int, default=DEFAULT_WINDOW_DAYS,
        help=f"Days of git/PROJECT_STATUS history to scan (default: {DEFAULT_WINDOW_DAYS})",
    )
    parser.add_argument(
        "--output-path", type=str, default=None,
        help="Override output file path (default: knowledge/research/backlog-freshness-check-<date>.md)",
    )
    args = parser.parse_args()
    output_path = args.output_path or str(
        DEFAULT_OUTPUT_DIR / f"backlog-freshness-check-{date.today().isoformat()}.md"
    )
    backlog_text = BACKLOG_PATH.read_text()
    open_entries = parse_open_entries(backlog_text)
    closed_entries = parse_closed_entries(backlog_text)
    ps_entries = parse_ps_entries(PROJECT_STATUS_PATH.read_text(), args.window_days)
    closure_commits = get_closure_commits(args.window_days)
    find_candidates(open_entries, closure_commits, ps_entries, closed_entries)
    report = generate_report(open_entries, args.window_days)
    Path(output_path).write_text(report)
    print(f"Report written to {output_path}")


if __name__ == "__main__":
    main()
