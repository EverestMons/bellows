#!/usr/bin/env python3
"""Lint-class census matchers for diagnostic 336.

Four candidate classes:
  m — non-ASCII inside a -F literal
  q — shell metacharacter (backtick, $, !) inside a -F literal
  r — grep -c piped into another command, masking exit code
  s — numeral asserting the size of an enumeration

Scans every *.md under knowledge/decisions/Done/ across all repos
under SHOP_ROOT. Outputs TSV in the census capture format.

Usage: python3 census-matchers.py <stratum-lookup.tsv> <shop-root>
"""

import os
import re
import sys

STRATUM_FILE = sys.argv[1]
SHOP_ROOT = sys.argv[2]

# --- stratum lookup from plan 335 ---
stratum_map = {}
with open(STRATUM_FILE) as f:
    for raw in f:
        parts = raw.strip().split('\t')
        if len(parts) == 2:
            stratum_map[parts[0]] = parts[1]

# --- find all Done/ *.md files ---
done_files = []
for root, dirs, files in os.walk(SHOP_ROOT):
    dirs[:] = [d for d in dirs if not d.startswith('.')]
    if (os.path.basename(root) == 'Done'
            and 'knowledge/decisions/Done' in root):
        for fn in sorted(files):
            if fn.endswith('.md'):
                done_files.append(os.path.join(root, fn))
done_files.sort()

# --- matchers ---

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
GREP_F_RE = re.compile(r'grep\b.*-[A-Za-z]*F')
GREP_C_PIPE_RE = re.compile(r'grep\b[^|]*-[A-Za-z]*c[A-Za-z]*\b[^|]*\|')
QUOTED_RE = re.compile(r'"([^"]*)"|\'([^\']*)\'')


def match_m(line):
    """m: non-ASCII inside a -F literal.
    Fires when line has grep with -F AND any non-ASCII character."""
    if not GREP_F_RE.search(line):
        return False
    return any(ord(c) > 127 for c in line)


def match_q(line):
    """q: shell metacharacter inside a -F literal.
    Fires when line has grep -F AND a quoted string contains backtick, $, or !."""
    if not GREP_F_RE.search(line):
        return False
    for m in QUOTED_RE.finditer(line):
        content = m.group(1) or m.group(2) or ''
        if '`' in content or '$' in content or '!' in content:
            return True
    return False


def match_r(line):
    """r: grep -c piped into another command.
    Fires when line has grep with -c flag followed by a pipe."""
    return bool(GREP_C_PIPE_RE.search(line))


def match_s(line):
    """s: numeral asserting the size of an enumeration.
    Fires when a word-numeral (two-twenty) precedes an enumeration noun."""
    return bool(S_RE.search(line))


MATCHERS = [('m', match_m), ('q', match_q), ('r', match_r), ('s', match_s)]

# --- scan ---
print('class\tplan_file\tline\tstratum\tfenced\tmatched_text')

for filepath in done_files:
    basename = os.path.basename(filepath)
    strat = stratum_map.get(basename, 'UNKNOWN')

    try:
        with open(filepath, encoding='utf-8', errors='replace') as fh:
            lines = fh.readlines()
    except Exception:
        continue

    in_fence = False
    for lineno, raw_line in enumerate(lines, 1):
        stripped = raw_line.rstrip('\n')

        if stripped.lstrip().startswith('```'):
            in_fence = not in_fence
            continue

        fenced = 'yes' if in_fence else 'no'

        for cls, matcher_fn in MATCHERS:
            if matcher_fn(stripped):
                clean = stripped.replace('\t', ' ').replace('\n', ' ')
                print(f'{cls}\t{basename}\t{lineno}\t{strat}\t{fenced}\t{clean}')
