#!/usr/bin/env python3
"""propagation_check — find claims a plan states in more than one voice, and disagreements between them.

The drafting cycle's walks catch defects of COMPREHENSION. They are poor at
defects of PROPAGATION: a correction applied at the site where it was noticed
and not at its siblings. Measured on one T2 cycle (lessons-consolidation,
2026-08-18): thirteen instances of this single class survived eight walks, a
mechanical literal sweep, and a three-seat cold panel. Walk 5 spent ten of ten
findings on it; walk 8 was still finding it.

A walk cannot fix this. It is untargeted by construction (DRAFTING_CYCLE §2.7
covers-not-targets), and the class is a needle-in-prose problem that grep solves
completely and reading solves slowly.

Three detectors, all read-only:

  (1) RESTATED VALUE  - a bare numeral in instruction prose equal to a value the
      plan declares once elsewhere, with no qualifier ("measured at walk 0")
      nearby. This is the literal-sweep class.
  (2) ORDERING        - every distinct task-sequence expression (A -> B -> C).
      More than one distinct sequence is a claim stated two ways. Caught w7-1,
      where ACID still described "A -> B" three folds after the order became
      "B0 -> A -> B".
  (3) ARITHMETIC      - expressions over the same symbol operands that differ in
      their constants (`T` + `N` vs `T` + `N` + 1). Caught w8-2.

    propagation_check.py <plan.md> [--region-end '## Drafting Cycle']

Exit 0 = no divergence found. Exit 1 = divergences reported. Exit 2 = the check
could not run (never read as a pass).

LIMITS, stated so a clean run is not over-read: this finds RESTATEMENT, not
correctness. A value declared once and wrong everywhere is invisible to it, and
so is a claim only made once. It is a propagation check, not a truth check.
Standard library only. Reads; never writes.
"""

import argparse
import re
import sys

_DECLARING_LINES: set[str] = set()

# Exclusion patterns for _mask_exclusions
_HEX_TOKEN_RE = re.compile(r'[0-9a-f]{12,}', re.IGNORECASE)
_DATE_RE = re.compile(r'\d{4}-\d{2}-\d{2}')
_TIME_RE = re.compile(r'\d{2}:\d{2}:\d{2}')
_SHA256_CTX_RE = re.compile(r'(?:sha-|-a\s+)256\b', re.IGNORECASE)
_NUMERAL2_RE = re.compile(r'(?<!\d)\d[\d,]*\d(?!\d)')

QUALIFIERS = ("measured", "walk 0", "at walk", "until w", "until s", "read ",
              "was ", "were ", "earlier form", "before s1", "before w",
              "this line claimed", "capstone", "baseline", "instance")
ARROW = "→"


def instruction_region(text, region_end):
    """Everything EXCEPT the Cycle Log section — which is record, not instruction.

    ⚠️ This originally returned text[:index(region_end)], i.e. "everything before
    the Cycle Log", on the assumption that the Cycle Log is last. That assumption
    is false the moment a plan moves its trailing sections above the steps to
    keep them out of STEP 2's gate span (a real fold: S3-13 on the plan this tool
    was built for). The effect was silent and total — the checker examined only
    the front matter and reported "consistent" over a region that excluded both
    steps. Excise the SECTION; keep the rest of the document.
    """
    i = text.find(region_end)
    if i < 0:
        return text
    m = re.search(r"^## ", text[i + len(region_end):], re.MULTILINE)
    j = i + len(region_end) + m.start() if m else len(text)
    return text[:i] + text[j:]


def _mask_exclusions(s):
    """Blank excluded regions so numeral extraction skips them."""
    chars = list(s)

    def _blank(start, end):
        for i in range(start, end):
            chars[i] = '\x00'

    for pat in (_HEX_TOKEN_RE, _DATE_RE, _TIME_RE):
        for m in pat.finditer(s):
            _blank(m.start(), m.end())
    # Mask the "256" at the tail of sha-256 / -a 256 context
    for m in _SHA256_CTX_RE.finditer(s):
        if s[m.end() - 3:m.end()] == '256':
            _blank(m.end() - 3, m.end())
    return ''.join(chars)


def _cell_numerals(cell_text):
    """All 2+-digit numerals from a value cell, exclusions applied."""
    masked = _mask_exclusions(cell_text)
    return [m.group(0).replace(',', '') for m in _NUMERAL2_RE.finditer(masked)]


def declared_values(text):
    """symbol -> [values], from pin rows in the Numbers table.

    SYMBOL: bold-backticked name if the row has one, else the row id from the
    first cell (P3, M12). VALUES: all 2+-digit numerals in the third cell
    (value column), excluding hex digests of 12+ chars, dates (YYYY-MM-DD),
    times (HH:MM:SS), and the 256 in sha-256 / -a 256. The legacy bold-numeral
    form (anywhere in the row) is also matched as the positive control.

    Also populates _DECLARING_LINES so detector (1) does not flag the very row
    it parsed the declaration from.
    """
    out = {}
    for line in text.splitlines():
        if not line.startswith("|"):
            continue
        parts = [p.strip() for p in line.split("|")]
        cells = parts[1:-1]  # strip outer empty strings from leading/trailing |
        if len(cells) < 3:
            continue
        if re.match(r'^[-:]+$', cells[0]):
            continue  # separator row

        # SYMBOL: bold-backtick name if present, else row id from first cell
        sym_m = re.search(r"\*\*`([A-Za-z_][A-Za-z_0-9]*)`\*\*", line)
        if sym_m:
            symbol = sym_m.group(1)
        else:
            row_id_m = re.match(r'^([A-Za-z]\d+)$', cells[0])
            if not row_id_m:
                continue
            symbol = row_id_m.group(1)

        # New: numerals from the value cell (third column, index 2)
        vals = _cell_numerals(cells[2])

        # Legacy: bold numeral **NN** anywhere in the row (positive control)
        for bm in re.finditer(r'\*\*(\d[\d,]*\d)\*\*', line):
            v = bm.group(1).replace(',', '')
            if v not in vals:
                vals.append(v)

        if vals:
            out[symbol] = vals
            _DECLARING_LINES.add(line.strip())
    return out


def detect_restated(region, decls):
    hits = []
    for n, line in enumerate(region.splitlines(), 1):
        if line.strip() in _DECLARING_LINES:
            continue          # the declaration itself is not a restatement
        low = line.lower()
        for sym, vals in decls.items():
            for val in vals:
                if len(val) < 2:      # 1-digit values are too common to be signal
                    continue
                for m in re.finditer(r"(?<![\d\w`])" + re.escape(val) + r"(?![\d\w])", line):
                    ctx = low[max(0, m.start() - 90): m.end() + 90]
                    if any(q in ctx for q in QUALIFIERS):
                        continue
                    hits.append((n, sym, val, line.strip()[:150]))
    return hits


# A task token is the FIRST identifier in an arrow-separated segment, which in
# real plan prose carries a trailing parenthetical:
#   "Task B0 (scratch only - touches nothing live) -> Task A (`T` subs) -> Task B"
# The first form of this detector required adjacent tokens and found ZERO
# sequences in a file containing two. Caught by canarying against the commit
# where the defect was known present, not by unit tests over invented strings.
def task_vocabulary(text):
    """The task names this plan actually defines — from its own `### Task X`
    headings. Grounding the vocabulary in the document is what stopped this
    detector matching ordinary capitalised prose ("Any" -> "A")."""
    return sorted(set(re.findall(r"^>?\s*#{2,4}\s*Task\s+([A-Z][A-Za-z0-9]{0,2})\b",
                                 text, re.MULTILINE)), key=len, reverse=True)


def detect_ordering(region, vocab):
    """EDGE-based. For each arrow, resolve the task name immediately before it
    and immediately after it; chain the resulting edges into sequences.

    ⚠️ This detector was wrong THREE times before it was right, and every time
    only a canary against a commit with a known-present defect exposed it:
      v1 required arrow-adjacent tokens  -> found 0 sequences in a file with 2;
      v2 matched any short capitalised word -> emitted "A -> E -> A -> B" from
         ordinary prose;
      v3 grounded the vocabulary in the plan's own `### Task X` headings and
         still swept up prose, because a bare "A" is both a task name and an
         English article.
    Sequence-matching over prose was the wrong shape. An arrow has exactly two
    operands; resolving those two is a bounded question, and chaining is exact.
    """
    if not vocab:
        return {}
    tok = "|".join(re.escape(t) for t in vocab)
    # trailing `**` after the parenthetical is real markdown: "**Task B0 (…)** →"
    before = re.compile(r"(?:Task|Tasks)\s+(?:\*\*)?(" + tok + r")(?:\*\*)?\s*(?:\([^()]*\))?\s*(?:\*\*)?\s*$")
    bare_b = re.compile(r"(?:\*\*)?(" + tok + r")(?:\*\*)?\s*$")
    after = re.compile(r"^\s*(?:\*\*)?(?:Task\s+)?(" + tok + r")(?:\*\*)?(?![A-Za-z0-9])")
    seqs = {}
    for n, line in enumerate(region.splitlines(), 1):
        if ARROW not in line:
            continue
        parts = line.split(ARROW)
        edges = []
        for k in range(len(parts) - 1):
            lhs, rhs = parts[k], parts[k + 1]
            mb = before.search(lhs) or bare_b.search(lhs)
            ma = after.match(rhs)
            edges.append((mb.group(1), ma.group(1)) if (mb and ma) else None)
        low = line.lower()
        if any(q in low for q in QUALIFIERS) and ARROW in line:
            # a fold-history citation quoting a superseded order is not a divergence;
            # keep the line only if it ALSO states a current order outside the citation
            cite = re.search(r"\*\(", line)
            if cite and line.index(ARROW) > cite.start():
                continue
        run = []
        for e in edges + [None]:
            if e and (not run or run[-1] == e[0]):
                run = (run or [e[0]]) + [e[1]]
            else:
                if len(run) >= 2:
                    seqs.setdefault(tuple(run), []).append((n, line.strip()[:110]))
                run = [e[0], e[1]] if e else []
    return seqs


def _is_subsequence(small, big):
    it = iter(big)
    return all(tok in it for tok in small)


def detect_arithmetic(region):
    groups = {}
    for n, line in enumerate(region.splitlines(), 1):
        for m in re.finditer(r"`[A-Za-z]`(?:\s*\+\s*(?:`[A-Za-z]`|\d+))+", line):
            ctx = line.lower()[max(0, m.start() - 90): m.end() + 90]
            if any(q in ctx for q in QUALIFIERS):
                continue   # a fold-history citation quoting the OLD form is not a divergence
            expr = re.sub(r"\s+", "", m.group(0))
            syms = tuple(sorted(set(re.findall(r"`([A-Za-z])`", expr))))
            groups.setdefault(syms, {}).setdefault(expr, []).append((n, line.strip()[:120]))
    return {k: v for k, v in groups.items() if len(v) > 1}


def main(argv=None):
    ap = argparse.ArgumentParser(description="Find claims a plan states in more than one voice.")
    ap.add_argument("plan")
    ap.add_argument("--region-end", default="## Drafting Cycle",
                    help="prose after this heading is RECORD, not instruction (default: '## Drafting Cycle')")
    args = ap.parse_args(argv)

    try:
        text = open(args.plan, encoding="utf-8").read()
    except OSError as e:
        print(f"ERROR: cannot read {args.plan}: {e}", file=sys.stderr)
        return 2

    region = instruction_region(text, args.region_end)
    decls = declared_values(text)
    total_vals = sum(len(v) for v in decls.values())
    print(f"declared symbols: {len(decls)} (values: {total_vals})")
    for sym, vals in decls.items():
        print(f"  {sym}: {vals}")
    if not decls:
        # ⚠️ A clean report over ZERO parsed declarations is the failure mode this
        # tool exists to prevent, not a pass. The parser now reads plain-backtick,
        # plain, and bold value forms, plus row-id symbols. Exit 2 means no rows
        # with 2+-digit numerals were found — never a clean result.
        print("\nERROR: no symbol declarations parsed — detector (1) cannot run.")
        print("  Expected a row of the form:")
        print("    | Pn | **`SYM`** | 1234 |          (plain numeral)")
        print("    | Pn | **`SYM`** | `1234` |         (plain-backtick numeral)")
        print("    | Pn | **`SYM`** | — | **1234** |  (legacy bold numeral)")
        print("    | Pn | row-id    | 1234 |          (row-id as symbol)")
        print("  This is EXIT 2 (could not run), never a clean result.")
        return 2
    print(f"instruction region: {len(region.splitlines())} lines "
          f"of {len(text.splitlines())}\n")

    found = 0

    print("(1) RESTATED VALUE — a declared value written as a bare numeral in prose")
    for n, sym, val, line in detect_restated(region, decls):
        found += 1
        print(f"  L{n}: `{sym}` = {val} restated unqualified\n      {line}")
    if not found:
        print("  none")

    print("\n(2) ORDERING — distinct task sequences (>1 distinct = a claim stated two ways)")
    seqs = detect_ordering(region, task_vocabulary(text))
    if len(seqs) > 1:
        canon = max(seqs, key=len)
        print(f"  canonical (longest): {' -> '.join(canon)}")
        for toks, sites in sorted(seqs.items(), key=lambda kv: -len(kv[0])):
            if toks == canon:
                continue
            sub = _is_subsequence(toks, canon)
            # A subsequence may be a legitimate PARTIAL claim ("a halt between A
            # and B") or a stale schedule presented as complete (the w7-1 defect,
            # where ACID said "A -> B" after the order became "B0 -> A -> B").
            # The tool cannot tell those apart; it surfaces the site and says so.
            tag = "REVIEW    " if sub else "DIVERGENCE"
            if not sub:
                found += 1
            print(f"  [{tag}] {' -> '.join(toks)}"
                  + ("   (a subsequence — legitimate partial claim, or a stale schedule stated as whole?)" if sub else "   (NOT a subsequence of the canonical order)"))
            for n, line in sites:
                print(f"      L{n}: {line}")
    else:
        print(f"  {len(seqs)} distinct sequence — consistent")

    print("\n(3) ARITHMETIC — same operands, different constants")
    ar = detect_arithmetic(region)
    if ar:
        for syms, exprs in ar.items():
            found += 1
            print(f"  operands {list(syms)}:")
            for expr, sites in exprs.items():
                print(f"      {expr}   at {[n for n, _ in sites]}")
    else:
        print("  none")

    print(f"\n{'DIVERGENCES: ' + str(found) if found else 'CLEAN — no divergence found'}")
    print("⚠️ Clean means no RESTATEMENT divergence. It is not a correctness result.")
    return 1 if found else 0


if __name__ == "__main__":
    sys.exit(main())
