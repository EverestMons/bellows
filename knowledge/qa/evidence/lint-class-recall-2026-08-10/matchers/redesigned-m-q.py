#!/usr/bin/env python3
"""Redesigned matchers for lint classes m and q.

These parse the command to find the actual -F operand rather than
scanning the entire line. The original matchers fire on non-ASCII
or metacharacters ANYWHERE on a line containing grep -F, which
produces false positives when the non-ASCII/metacharacter is in
surrounding prose rather than in the -F argument.

The redesign direction is stated in 336 findings sections (vi):
  m: "restrict the non-ASCII scan to the actual argument following
      the -F flag, not the entire line"
  q: "parse the command to identify which quoted string is the
      operand of -F, and check only that string"
"""

import re
import shlex


def extract_f_operand(line):
    """Extract the -F operand from a grep command line.

    Handles:
    - grep -F "pattern" (separate arg)
    - grep -cF "pattern" (combined flags)
    - grep -F 'pattern' (single quotes)
    - grep -xF "pattern" (combined with other flags)

    Returns the operand string if found, else None.
    """
    grep_pos = -1
    for m in re.finditer(r'\bgrep\b', line):
        grep_pos = m.start()
        break
    if grep_pos < 0:
        return None

    after_grep = line[grep_pos:]

    has_f_flag = bool(re.search(r'-[A-Za-z]*F', after_grep))
    if not has_f_flag:
        return None

    try:
        tokens = shlex.split(after_grep)
    except ValueError:
        tokens = _fallback_extract(after_grep)
        if tokens is None:
            return None

    i = 0
    f_flag_seen = False
    f_expects_next = False

    while i < len(tokens):
        tok = tokens[i]

        if tok == 'grep':
            i += 1
            continue

        if tok.startswith('-') and not tok.startswith('--'):
            flags = tok[1:]
            if 'F' in flags:
                f_flag_seen = True
                remaining = flags[flags.index('F') + 1:]
                if 'e' in remaining:
                    f_expects_next = True
                elif not remaining or all(c in 'cilnxvwHhrRoqsab' for c in remaining):
                    f_expects_next = True
            elif 'e' in flags:
                i += 2
                continue
            i += 1
            continue

        if tok.startswith('--'):
            if tok == '--':
                i += 1
                break
            i += 1
            continue

        if f_expects_next:
            return tok

        i += 1

    if f_flag_seen and i < len(tokens):
        return tokens[i]

    return None


def _fallback_extract(text):
    """Fallback for when shlex.split fails (unmatched quotes, etc).

    Try to find a quoted string after -F using regex.
    """
    m = re.search(r'-[A-Za-z]*F\s+"([^"]*)"', text)
    if m:
        return ['grep', '-F', m.group(1)]
    m = re.search(r"-[A-Za-z]*F\s+'([^']*)'", text)
    if m:
        return ['grep', '-F', m.group(1)]
    m = re.search(r'-[A-Za-z]*F\s+(\S+)', text)
    if m:
        return ['grep', '-F', m.group(1)]
    return None


def match_m_redesigned(line):
    """m-redesigned: non-ASCII inside the actual -F operand only."""
    operand = extract_f_operand(line)
    if operand is None:
        return False
    return any(ord(c) > 127 for c in operand)


def match_q_redesigned(line):
    """q-redesigned: shell metacharacter inside the actual -F operand only."""
    operand = extract_f_operand(line)
    if operand is None:
        return False
    return '`' in operand or '$' in operand or '!' in operand


if __name__ == '__main__':
    import sys
    if len(sys.argv) < 2:
        print("Usage: python3 redesigned-m-q.py <file-to-scan>")
        sys.exit(1)

    filepath = sys.argv[1]
    with open(filepath, encoding='utf-8', errors='replace') as f:
        for lineno, raw in enumerate(f, 1):
            stripped = raw.rstrip('\n')
            if match_m_redesigned(stripped):
                clean = stripped.replace('\t', ' ').replace('\n', ' ')
                print(f'm-redesigned\t{lineno}\t{clean}')
            if match_q_redesigned(stripped):
                clean = stripped.replace('\t', ' ').replace('\n', ' ')
                print(f'q-redesigned\t{lineno}\t{clean}')
