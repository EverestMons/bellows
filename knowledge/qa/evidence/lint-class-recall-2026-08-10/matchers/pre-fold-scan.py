#!/usr/bin/env python3
"""Scan pre-fold states of drafts for lint-class matches.
For each draft, extracts each per-phase commit's version and runs the four matchers.
Outputs match data for Q4 (pre-fold fires) and Q2 (re-finding).
"""

import os
import re
import subprocess
import sys

# Matcher definitions (same as census-matchers.py)
GREP_F_RE = re.compile(r'grep\b.*-[A-Za-z]*F')
GREP_C_PIPE_RE = re.compile(r'grep\b[^|]*-[A-Za-z]*c[A-Za-z]*\b[^|]*\|')
QUOTED_RE = re.compile(r'"([^"]*)"|\'([^\']*)\'')

NUMBER_WORDS = [
    'two', 'three', 'four', 'five', 'six', 'seven', 'eight',
    'nine', 'ten', 'eleven', 'twelve', 'thirteen', 'fourteen',
    'fifteen', 'sixteen', 'seventeen', 'eighteen', 'nineteen', 'twenty',
]
NW_ALT = '|'.join(NUMBER_WORDS)
ENUM_NOUNS = (
    r'items?|steps?|files?|checks?|sites?|sub-?sites?|things?|bullets?|'
    r'points?|commands?|rows?|entries?|columns?|fields?|keys?|deposits?|'
    r'repos?|paths?|tasks?|questions?|rules?|conditions?|constraints?|'
    r'guards?|branches?|arms?|gates?|probes?|tests?|ways?|instances?|'
    r'cases?|phases?|walks?|lenses?|rounds?|seats?|folds?|findings?|'
    r'buckets?|sub-?steps?|places?|fixes?|bugs?|defects?|classes?|'
    r'falsehoods?|enumerations?|validators?|numbers?|cycles?|commits?|'
    r'hunks?|diffs?|lines?|paragraphs?|sections?|blocks?|groups?|'
    r'types?|categories?|levels?|tiers?|dimensions?|modes?|states?|'
    r'layers?|surfaces?|copies?|variants?|forms?|shapes?|concerns?|'
    r'issues?|problems?|errors?|repos(?:itories)?|directories'
)
S_RE = re.compile(rf'\b({NW_ALT})\s+({ENUM_NOUNS})\b', re.IGNORECASE)


def match_m(line):
    if not GREP_F_RE.search(line):
        return False
    return any(ord(c) > 127 for c in line)


def match_q(line):
    if not GREP_F_RE.search(line):
        return False
    for m in QUOTED_RE.finditer(line):
        content = m.group(1) or m.group(2) or ''
        if '`' in content or '$' in content or '!' in content:
            return True
    return False


def match_r(line):
    return bool(GREP_C_PIPE_RE.search(line))


def match_s(line):
    return bool(S_RE.search(line))


MATCHERS = [('m', match_m), ('q', match_q), ('r', match_r), ('s', match_s)]


def get_commits(repo_path, draft_path):
    """Get all commits touching this draft path, oldest first."""
    result = subprocess.run(
        ['git', '-C', repo_path, 'log', '--all', '--reverse',
         '--format=%H %s', '--follow', '--', draft_path],
        capture_output=True, text=True
    )
    commits = []
    for line in result.stdout.strip().split('\n'):
        if line.strip():
            sha = line.split()[0]
            msg = line[len(sha)+1:]
            commits.append((sha, msg))
    return commits


def get_file_at_commit(repo_path, sha, draft_path):
    """Get the file content at a specific commit."""
    result = subprocess.run(
        ['git', '-C', repo_path, 'show', f'{sha}:{draft_path}'],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        # Try without path (file might have been renamed)
        return None
    return result.stdout


def scan_content(content):
    """Run all four matchers on the content, return set of (class, line_no) tuples."""
    fires = set()
    for lineno, line in enumerate(content.split('\n'), 1):
        stripped = line.rstrip()
        for cls, matcher_fn in MATCHERS:
            if matcher_fn(stripped):
                fires.add((cls, lineno))
    return fires


# Define drafts to scan
DRAFTS = [
    # Bellows drafts (4)
    ('/Users/marklehn/Developer/GitHub/bellows',
     'knowledge/research/draft-clean-gate-auto-continue-2026-08-08.md',
     'clean-gate-auto-continue', 'executable-317.md'),
    ('/Users/marklehn/Developer/GitHub/bellows',
     'knowledge/research/draft-lens-mechanization-census-2026-08-08.md',
     'lens-mechanization-census', 'diagnostic-322.md'),
    ('/Users/marklehn/Developer/GitHub/bellows',
     'knowledge/research/draft-lint-subcheck-trio-2026-08-08.md',
     'lint-subcheck-trio', 'executable-324.md'),
    ('/Users/marklehn/Developer/GitHub/bellows',
     'knowledge/research/draft-verdict-mechanization-distribution-refresh-2026-08-08.md',
     'verdict-mechanization-distribution-refresh', 'diagnostic-315.md'),
    # Shop root drafts (5)
    ('/Users/marklehn/Developer/GitHub',
     'draft-lint-s4-hardening-2026-08-09.md',
     'lint-s4-hardening', 'executable-332.md'),
    ('/Users/marklehn/Developer/GitHub',
     'draft-gate2-s5-conformance-2026-08-09.md',
     'gate2-s5-conformance', 'executable-330.md'),
    ('/Users/marklehn/Developer/GitHub',
     'draft-diagnostic-brewbuddy-shop-import-census.md',
     'brewbuddy-shop-import-census', None),  # UNCOVERED — no close commit
    ('/Users/marklehn/Developer/GitHub',
     'draft-executable-seat-brief-codification.md',
     'seat-brief-codification', 'executable-329.md'),
    ('/Users/marklehn/Developer/GitHub',
     'governance/knowledge/research/draft-template-qa-and-terminal-correction-2026-08-08.md',
     'template-qa-and-terminal-correction', 'executable-320.md'),
    # Lessons-forge drafts (2)
    ('/Users/marklehn/Developer/GitHub/lessons-forge',
     'knowledge/research/draft-cycle-run-2026-08-07.md',
     'cycle-run', 'executable-311.md'),
    ('/Users/marklehn/Developer/GitHub/lessons-forge',
     'knowledge/research/draft-gate1-routing-2026-08-08.md',
     'gate1-routing', 'executable-326.md'),
]

# Output header
print('draft_slug\tcommit_sha\tcommit_idx\tphase\tclass\tmatches_count\tdone_file')

for entry in DRAFTS:
    repo_path, draft_path, slug = entry[0], entry[1], entry[2]
    done_file = entry[3] if len(entry) > 3 else None
    if done_file is None:
        print(f'# {slug}: UNCOVERED (no Done/ plan)', file=sys.stderr)
        continue
    commits = get_commits(repo_path, draft_path)
    if not commits:
        print(f'# {slug}: NO COMMITS FOUND', file=sys.stderr)
        continue

    print(f'# {slug}: {len(commits)} commits', file=sys.stderr)

    for idx, (sha, msg) in enumerate(commits):
        content = get_file_at_commit(repo_path, sha, draft_path)
        if content is None:
            # Try to find the path at this commit
            result = subprocess.run(
                ['git', '-C', repo_path, 'show', '--name-only',
                 '--format=', sha],
                capture_output=True, text=True
            )
            alt_paths = [p for p in result.stdout.strip().split('\n')
                        if 'draft-' in p and p.endswith('.md')]
            if alt_paths:
                content = get_file_at_commit(repo_path, sha, alt_paths[0])
            if content is None:
                continue

        # Extract phase label from commit message
        phase = msg.split(':')[0] if ':' in msg else msg[:30]
        phase = phase.replace('draft(' + slug + ')', '').strip()
        if not phase:
            phase = 'initial'

        # Run matchers
        for cls, _ in MATCHERS:
            cls_matches = sum(1 for c, _ in scan_content(content) if c == cls)
            print(f'{slug}\t{sha[:8]}\t{idx}\t{phase}\t{cls}\t{cls_matches}\t{done_file}')
