#!/usr/bin/env python3
"""Cycle yields collector — parse Cycle Log yields and origin splits from Done/ corpus.

Read-only, standard library only. Emits TSV to stdout.
"""

import os
import re
import sys
from pathlib import Path

STATUS_OK = "OK"
STATUS_NO_BLOCK = "NO_BLOCK"
STATUS_MULTIPLE_BLOCKS = "MULTIPLE_BLOCKS"
STATUS_UNPARSEABLE = "UNPARSEABLE"

ORIGIN_PRESENT = "PRESENT"
ORIGIN_ABSENT = "ABSENT"
ORIGIN_PARTIAL = "PARTIAL"
ORIGIN_NA = "N/A"

SOURCE = "RECORD_CLAIMED"

COLUMNS = [
    "plan_file", "plan_id", "block", "lens", "pass", "folded",
    "pre_existing", "fold_introduced", "origin", "source", "status", "note",
]
HEADER = "\t".join(COLUMNS)

PLAN_ID_RE = re.compile(r"(?:executable|diagnostic|qa)-(\d+)\.md$")
FENCE_RE = re.compile(r"^```[^\n]*\n.*?^```[^\n]*$", re.MULTILINE | re.DOTALL)
DC_HEADING_RE = re.compile(r"^## Drafting Cycle\s*$", re.MULTILINE)
NEXT_H2_RE = re.compile(r"^## ", re.MULTILINE)

LENS_PREFIXES = [
    (re.compile(r"^weak[\s-]*spots\s*:", re.IGNORECASE), "weak-spots"),  # 63: hyphenated spelling
    (re.compile(r"^destruction\s*:", re.IGNORECASE), "destruction"),
    (re.compile(r"^vulnerabilit\w*\s*:", re.IGNORECASE), "vulnerabilities"),
    (re.compile(r"^integration[\s-]*record\s*:", re.IGNORECASE), "integration-record"),
    (re.compile(r"^integration\s*:", re.IGNORECASE), "integration-record"),
    (re.compile(r"^acid\s*:", re.IGNORECASE), "acid"),
]

PASS_FOLDED_RE = re.compile(
    r"(?:(?:^|[;.)])\s*)(\w+)\s+(?:\([^)]*\)\s+)?(\d+)\s+folded\b"
)
PASS_DRY_RE = re.compile(
    r"(?:(?:^|[;.)])\s*)(\w+)\s+(?:\([^)]*\)\s+)?(?:dry|DRY)\b"
)

ORIGIN_FULL_RE = re.compile(r"\((\d+)\s*/\s*(\d+)\)")
ORIGIN_PRE_RE = re.compile(r"\((\d+)\s+pre[_-]existing\)", re.IGNORECASE)
ORIGIN_FOLD_RE = re.compile(r"\((\d+)\s+fold[_-]introduced\)", re.IGNORECASE)


def find_root(start):
    """Walk up from start to find directory containing DRAFTING_CYCLE.md."""
    current = Path(start).resolve()
    if current.is_file():
        current = current.parent
    while True:
        if (current / "DRAFTING_CYCLE.md").exists():
            return current
        parent = current.parent
        if parent == current:
            break
        current = parent
    return None


def strip_fenced(text):
    return FENCE_RE.sub("", text)


def extract_plan_id(filename):
    m = PLAN_ID_RE.search(filename)
    return m.group(1) if m else "-"


def extract_dc_blocks(text):
    cleaned = strip_fenced(text)
    blocks = []
    for m in DC_HEADING_RE.finditer(cleaned):
        start = m.end()
        rest = cleaned[start:]
        next_h2 = NEXT_H2_RE.search(rest)
        block_text = rest[: next_h2.start()] if next_h2 else rest
        blocks.append(block_text)
    return blocks


def sanitize_note(text):
    return text.replace("\t", " ").replace("\n", " ").replace("\r", " ")


def parse_origin(text):
    m = ORIGIN_FULL_RE.search(text)
    if m:
        return ORIGIN_PRESENT, m.group(1), m.group(2)
    m = ORIGIN_PRE_RE.search(text)
    if m:
        return ORIGIN_PARTIAL, m.group(1), "-"
    m = ORIGIN_FOLD_RE.search(text)
    if m:
        return ORIGIN_PARTIAL, "-", m.group(1)
    return ORIGIN_ABSENT, "-", "-"


def _is_pass_token(s):
    if not s or len(s) > 10 or not s[0].isalpha():
        return False
    if not s.isalnum():
        return False
    if any(c.isdigit() for c in s):
        return True
    return s.lower() in ("closing", "cc") or len(s) <= 3


def extract_passes(content):
    """Extract all passes from lens line content."""
    clean = re.sub(r"\*\*", "", content)
    results = []
    seen_tokens = set()

    for m in PASS_FOLDED_RE.finditer(clean):
        token = m.group(1)
        if not _is_pass_token(token):
            continue
        folded = m.group(2)

        after = m.end()
        window_end = len(clean)
        next_f = PASS_FOLDED_RE.search(clean, after)
        if next_f and _is_pass_token(next_f.group(1)):
            window_end = min(window_end, next_f.start())
        next_d = PASS_DRY_RE.search(clean, after)
        if next_d and _is_pass_token(next_d.group(1)):
            window_end = min(window_end, next_d.start())
        sc = clean.find(";", after)
        if 0 <= sc < window_end:
            window_end = sc

        window = clean[after:window_end]
        origin, pre_ex, fold_intro = parse_origin(window)
        results.append((token, folded, pre_ex, fold_intro, origin))
        seen_tokens.add(token)

    for m in PASS_DRY_RE.finditer(clean):
        token = m.group(1)
        if not _is_pass_token(token):
            continue
        if token in seen_tokens:
            continue
        results.append((token, "0", "-", "-", ORIGIN_ABSENT))
        seen_tokens.add(token)

    return results


def _parse_all_lenses(content):
    """Parse 'All lenses, wN ...: data' after stripping the prefix."""
    clean = re.sub(r"\*\*", "", content).strip()
    colon_pos = clean.find(":")
    if colon_pos < 0:
        return None
    before = clean[:colon_pos].strip()
    after = clean[colon_pos + 1 :].strip()

    m_tok = re.match(r"(\w+)", before)
    if not m_tok:
        return None
    token = m_tok.group(1)

    m_fold = re.search(r"(\d+)\s+folded\b", after)
    if m_fold:
        origin, pre_ex, fold_intro = parse_origin(after[m_fold.end() :])
        return [("all-lenses", token, m_fold.group(1), pre_ex, fold_intro, origin)]
    if re.search(r"\b(?:dry|DRY)\b", after):
        return [("all-lenses", token, "0", "-", "-", ORIGIN_ABSENT)]
    return None


def parse_lens_line(line):
    """Parse a lens line. Returns list of tuples or None if not a lens line."""
    stripped = line.strip()
    if not stripped.startswith("- "):
        return None

    content = stripped[2:].strip()
    content_clean = re.sub(r"\*\*", "", content).strip()

    if content_clean.startswith("⚠"):
        return None

    m_all = re.match(r"All\s+lenses\s*,\s*", content_clean, re.IGNORECASE)
    if m_all:
        rest = content_clean[m_all.end() :]
        result = _parse_all_lenses(rest)
        if result:
            return result
        note = sanitize_note(stripped[:120])
        return [("UNPARSEABLE", note)]

    for pattern, lens_name in LENS_PREFIXES:
        m = pattern.match(content_clean)
        if m:
            rest = content_clean[m.end() :].strip()
            passes = extract_passes(rest)
            if passes:
                return [(lens_name, *p) for p in passes]
            note = sanitize_note(stripped[:120])
            return [("UNPARSEABLE", note)]

    m_cc = re.match(
        r"Confirming\s+close\s*\(([^)]+)\)\s*:", content_clean, re.IGNORECASE
    )
    if m_cc:
        inner = m_cc.group(1).strip()
        after = content_clean[m_cc.end() :].strip()
        m_tok = re.match(r"(\w+)", inner)
        token = m_tok.group(1) if m_tok else "cc"
        m_fold = re.search(r"(\d+)\s+folded\b", after)
        if m_fold:
            origin, pre_ex, fold_intro = parse_origin(after[m_fold.end() :])
            return [
                ("confirming-close", token, m_fold.group(1), pre_ex, fold_intro, origin)
            ]
        if re.search(r"\b(?:dry|DRY)\b", after):
            return [("confirming-close", token, "0", "-", "-", ORIGIN_ABSENT)]
        note = sanitize_note(stripped[:120])
        return [("UNPARSEABLE", note)]

    m_conf = re.match(r"Confirming\s*\(([^)]+)\)\s*:", content_clean, re.IGNORECASE)
    if m_conf:
        inner = m_conf.group(1).strip()
        after = content_clean[m_conf.end() :].strip()
        m_tok = re.match(r"(\w+)", inner)
        if m_tok:
            token = m_tok.group(1)
            m_fold = re.search(r"(\d+)\s+folded\b", after)
            if m_fold:
                origin, pre_ex, fold_intro = parse_origin(after[m_fold.end() :])
                return [
                    ("confirming", token, m_fold.group(1), pre_ex, fold_intro, origin)
                ]
            if re.search(r"\b(?:dry|DRY)\b", after):
                return [("confirming", token, "0", "-", "-", ORIGIN_ABSENT)]
        note = sanitize_note(stripped[:120])
        return [("UNPARSEABLE", note)]

    m_standalone = re.match(
        r"(\w+)\s*(?:\([^)]*\)\s*:)",
        content_clean,
    )
    if m_standalone:
        token = m_standalone.group(1)
        if _is_pass_token(token):
            after = content_clean[m_standalone.end() :].strip()
            m_fold = re.search(r"(\d+)\s+folded\b", after)
            if m_fold:
                origin, pre_ex, fold_intro = parse_origin(after[m_fold.end() :])
                return [
                    ("confirming", token, m_fold.group(1), pre_ex, fold_intro, origin)
                ]
            if re.search(r"\b(?:dry|DRY)\b", after):
                return [("confirming", token, "0", "-", "-", ORIGIN_ABSENT)]
            passes = extract_passes(after)
            if passes:
                return [("confirming", *p) for p in passes]

    return None


def make_row(
    plan_file, plan_id, block, lens, pass_tok, folded, pre_existing,
    fold_introduced, origin, status, note="-",
):
    return "\t".join([
        plan_file, str(plan_id), str(block), lens, pass_tok,
        str(folded), str(pre_existing), str(fold_introduced),
        origin, SOURCE, status, sanitize_note(note),
    ])


def collect(root):
    root = Path(root)
    assert root.exists() and (root / "DRAFTING_CYCLE.md").exists()

    rows = []
    discovery_count = 0
    block_carrying_count = 0

    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if not d.startswith(".")]

        parts = Path(dirpath).parts
        if len(parts) < 3:
            continue
        if not (
            parts[-1] == "Done"
            and parts[-2] == "decisions"
            and parts[-3] == "knowledge"
        ):
            continue

        for fn in sorted(filenames):
            if not fn.endswith(".md"):
                continue

            discovery_count += 1
            filepath = Path(dirpath) / fn
            plan_id = extract_plan_id(fn)

            try:
                text = filepath.read_text(encoding="utf-8")
            except Exception:
                rows.append(
                    make_row(fn, plan_id, "-", "-", "-", "-", "-", "-",
                             ORIGIN_NA, STATUS_UNPARSEABLE, "read error")
                )
                continue

            blocks = extract_dc_blocks(text)

            if not blocks:
                rows.append(
                    make_row(fn, plan_id, "-", "-", "-", "-", "-", "-",
                             ORIGIN_NA, STATUS_NO_BLOCK)
                )
                continue

            block_carrying_count += 1
            status = STATUS_MULTIPLE_BLOCKS if len(blocks) > 1 else STATUS_OK

            for bi, block_text in enumerate(blocks, 1):
                for bline in block_text.splitlines():
                    parsed = parse_lens_line(bline)
                    if parsed is None:
                        continue

                    for item in parsed:
                        if item[0] == "UNPARSEABLE":
                            note_text = item[1] if len(item) > 1 else "-"
                            rows.append(
                                make_row(fn, plan_id, bi, "-", "-", "-", "-",
                                         "-", ORIGIN_NA, STATUS_UNPARSEABLE,
                                         note_text)
                            )
                        else:
                            lens_name, tok, fld, pe, fi, orig = item
                            rows.append(
                                make_row(fn, plan_id, bi, lens_name, tok, fld,
                                         pe, fi, orig, status)
                            )

    return rows, discovery_count, block_carrying_count


def main():
    if len(sys.argv) > 1:
        root = Path(sys.argv[1])
    else:
        root = find_root(Path(__file__))
        if root is None:
            print(
                "ERROR: DRAFTING_CYCLE.md not found walking up from script",
                file=sys.stderr,
            )
            sys.exit(1)

    if not root.exists() or not (root / "DRAFTING_CYCLE.md").exists():
        print(
            f"ERROR: {root} missing or no DRAFTING_CYCLE.md", file=sys.stderr
        )
        sys.exit(1)

    rows, disc, blk = collect(root)
    print(
        f"# Discovery: {disc} files, {blk} with Drafting Cycle block",
        file=sys.stderr,
    )

    print(HEADER)
    for row in rows:
        print(row)


if __name__ == "__main__":
    main()
