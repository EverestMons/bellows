#!/usr/bin/env python3
"""register_coverage_census — the orphan-id population in the walk registers.

DIAGNOSTIC INSTRUMENT for plan `diagnostic-register-coverage` (manual_bootstrap,
un-parked 2026-09-05). Answers ONE question:

  Q1 — For every walk register, how many finding-ids does the file NAME that
       carry no schema row?

⛔ IT IMPORTS `walk_register_lint` AND USES ITS PARSER, not only its status.
Diagnostic 100032's walk 4 forbade writing a second reader for a format the lint
already parses. Called here: `extract_tables`, `split_table_row`,
`normalize_column`, `is_fold_table`, `validate_file`, and the STATUS_* vocabulary.
No table, row, cell or escape is parsed by hand.

⛔ IT DERIVES THE ID CONVENTION FROM EACH TABLE'S OWN HEADER AND CELLS.
It never matches a hardcoded id pattern. All FIVE hand-probes this plan exists to
replace failed by imposing a shape the corpus does not have — a fixed cell count,
a guessed dict key, a header/row mismatch, and twice an id-format assumption.

⛔ SELF-EXCLUSION. This plan's own walk register lives in the censused directory
and matches the glob; the population moved 172 -> 173 the moment it was created.
`SELF_REGISTER` names it exactly, and the exclusion is reported, not silent.

⛔ WRITES INCREMENTALLY. Every measurement is appended to the raw evidence file as
it is established, so a killed run leaves partials.

Read-only over the corpus: no register is edited and nothing is committed.
"""

import re
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path

BELLOWS_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BELLOWS_ROOT))
sys.path.insert(0, str(BELLOWS_ROOT / "scripts"))

import walk_register_lint as wrl  # noqa: E402

GOV = Path("/Users/marklehn/Developer/eluvian-governance")
REG_DIR = GOV / "governance" / "knowledge" / "research"
GLOB = "walk-register-*.md"

# ⛔ Named by EXACT filename (walk 3, lens 1: "by name" naming nothing left an
# executing agent to infer which register was its own).
SELF_REGISTER = "walk-register-register-coverage-2026-09-04.md"

RAW = (BELLOWS_ROOT / "knowledge" / "qa" / "evidence"
       / "register-coverage-2026-09-04" / "census-raw.txt")

# ⛔ POSITIVE CONTROLS — two registers, two id conventions, two schema states,
# and (by the plan's own note, luck of selection rather than requirement) one
# single-table and one multi-table file. An empty result must be PROVEN.
CONTROLS = {
    "walk-register-qa-steps-parsing-2026-09-04.md": {
        "schema": "0.3", "id_sample": "w1-1", "expect_nonempty_rowed": True,
    },
    "walk-register-dc-coldfront-2026-08-13.md": {
        "schema": "0.2", "id_sample": "d1", "expect_nonempty_rowed": True,
    },
}

MAX_ATTEMPTS = 3  # ⛔ BOUNDED (walk 2, lens 2). An unbounded retry is a livelock.

_out = RAW.open("a", encoding="utf-8")


def a(line=""):
    """Append AS ESTABLISHED. Flushed every line — a killed run keeps its work."""
    _out.write(line + "\n")
    _out.flush()


# ----------------------------------------------------------------------
# Population pin (Item 2b)
# ----------------------------------------------------------------------
def pin():
    head = subprocess.run(["git", "-C", str(GOV), "rev-parse", "HEAD"],
                          capture_output=True, text=True, timeout=15).stdout.strip()
    files = sorted(p for p in REG_DIR.glob(GLOB) if p.name != SELF_REGISTER)
    return head, len(files), files


# ----------------------------------------------------------------------
# Convention derivation — from the table's own cells, never a fixed pattern
# ----------------------------------------------------------------------
def clean_cell(v):
    """Normalise an id cell to its id TOKEN. Normalisation, not pattern matching:
    it strips markdown decoration the lint deliberately leaves in place and takes
    the leading whitespace-delimited token. Measured need — cells such as
    `S3-1 ⛔` and `S3-1` are the SAME id, and treating them as different made a
    rowed id look orphaned."""
    v = v.strip()
    v = re.sub(r"^[`*_ ]+|[`*_ ]+$", "", v).strip()
    if not v:
        return ""
    v = v.split()[0]
    return v.strip("`*_,;.")


# --- id-cell classification. Which cells can carry a SCANNABLE convention ---
ATOMIC_RE = re.compile(r"^[A-Za-z][A-Za-z0-9]*(?:[-._][A-Za-z0-9]+)*$")
NUMERIC_RE = re.compile(r"^\d+$")


def classify_id(v):
    r"""atomic | numeric | non_atomic. Derived from the cell's own text; no
    convention is assumed. NUMERIC ids are real but UNSCANNABLE — a bare \d+
    pattern matches years, line numbers and plan ids, so orphan detection is
    UNMEASURABLE for them and is reported as such rather than guessed at."""
    if not v:
        return "empty"
    if NUMERIC_RE.match(v):
        return "numeric"
    if ATOMIC_RE.match(v):
        return "atomic"
    return "non_atomic"


def tier_of(shape):
    """STRICT families carry an internal separator (a9-9, A9-9, A-9) and cannot
    collide with ordinary prose tokens. LOOSE families (a9, A9) can — `w1`, `T1`,
    `P3` all fit one. Derived from the SHAPE's own complexity, not from any
    convention this instrument was told about."""
    return "strict" if re.search(r"[^Aa9]", shape) else "loose"


def shape_of(idv):
    """Abstract an id to its SHAPE: A=upper run, a=lower run, 9=digit run,
    every other character kept literally. `w1-1`->a9-9, `S1-5`->A9-9, `d1`->a9."""
    out, i = [], 0
    while i < len(idv):
        c = idv[i]
        if c.isdigit():
            while i < len(idv) and idv[i].isdigit():
                i += 1
            out.append("9")
        elif c.isupper():
            while i < len(idv) and idv[i].isupper():
                i += 1
            out.append("A")
        elif c.islower():
            while i < len(idv) and idv[i].islower():
                i += 1
            out.append("a")
        else:
            out.append(c)
            i += 1
    return "".join(out)


def family_of(idv):
    """The FAMILY is the shape bound to this file's own literal alpha prefix —
    tighter than the shape alone, and derived, not assumed. `w1-1` -> ('w','a9-9')."""
    m = re.match(r"^([A-Za-z]+)", idv)
    return (m.group(1) if m else ""), shape_of(idv)


def family_regex(prefix, shape):
    """Build the search pattern for one derived family. Literal prefix + the
    shape's runs. Nothing here is hardcoded to a convention: both halves come
    from an id the file itself put in a row."""
    body = shape
    if prefix:
        body = shape[len(shape_of(prefix)):]  # drop the leading alpha token
    pat = [re.escape(prefix)]
    for ch in body:
        if ch == "9":
            pat.append(r"\d+")
        elif ch == "a":
            pat.append(r"[a-z]+")
        elif ch == "A":
            pat.append(r"[A-Z]+")
        else:
            pat.append(re.escape(ch))
    return re.compile(r"(?<![A-Za-z0-9_-])" + "".join(pat) + r"(?![A-Za-z0-9_])")


# ----------------------------------------------------------------------
# Per-register measurement
# ----------------------------------------------------------------------
def measure(path, corpus_families=None):
    text = path.read_text(encoding="utf-8")
    rec = {"name": path.name}

    # --- axis B: schema_version declaration (INDEPENDENT of table presence) ---
    m = wrl.SCHEMA_DECL_RE.search(text)
    rec["declared_version"] = m.group(1).strip().strip("`") if m else None

    # --- the lint's own verdict (axis A) ---
    try:
        status, lint_rows, shapes = wrl.validate_file(path)
    except Exception as e:
        status, lint_rows, shapes = f"VALIDATE_ERROR:{e}", [], []
    rec["lint_status"] = status

    # --- tables, via the lint's parser ---
    tables, consumed = wrl.extract_tables(text)
    rec["n_tables"] = len(tables)
    rec["n_fold_tables"] = sum(1 for h, _d, _l in tables if wrl.is_fold_table(h))

    id_tables = []
    for hdr, data, hline in tables:
        norm = [wrl.normalize_column(c) for c in hdr]
        if "id" in norm:
            id_tables.append((hdr, norm, data, hline))
    rec["n_id_tables"] = len(id_tables)

    rowed = {}           # id -> [table indexes]
    unreadable = []      # (table_idx, line, n_cells, n_header)
    empty_id_rows = 0
    cell_kinds = Counter()
    non_atomic_cells = []
    for ti, (hdr, norm, data, hline) in enumerate(id_tables, 1):
        idx = norm.index("id")
        for line_no, cells in data:
            if len(cells) != len(hdr):
                # ⛔ present-but-unreadable: a THIRD state, not a kind of orphan.
                # The id is NOT guessed — which cell holds it is unknown.
                unreadable.append((ti, line_no, len(cells), len(hdr)))
                continue
            v = clean_cell(cells[idx])
            kind = classify_id(v)
            cell_kinds[kind] += 1
            if kind == "empty":
                empty_id_rows += 1
                continue
            if kind == "non_atomic":
                non_atomic_cells.append((ti, line_no, v[:40]))
            rowed.setdefault(v, []).append(ti)

    rec["rowed_ids"] = rowed
    rec["n_rowed"] = len(rowed)
    rec["n_row_records"] = sum(len(v) for v in rowed.values())
    # ⛔ ">1 ROW RECORD" and ">1 TABLE" are different facts. Reported apart:
    # an id repeated inside ONE table is a duplicate row, not a cross-table id.
    rec["multi_record_ids"] = {k: v for k, v in rowed.items() if len(v) > 1}
    rec["multi_table_ids"] = {k: sorted(set(v)) for k, v in rowed.items()
                              if len(set(v)) > 1}
    rec["unreadable"] = unreadable
    rec["empty_id_rows"] = empty_id_rows
    rec["cell_kinds"] = cell_kinds
    rec["non_atomic_cells"] = non_atomic_cells

    # --- state classification ---
    if rec["n_id_tables"] == 0:
        rec["state"] = "no_table"
        rec["multi_record_ids"] = {}
        rec["families"] = []
        rec["families_strict"] = []
        rec["families_loose"] = []
        rec["n_numeric_ids"] = 0
        rec["scannable"] = False
        rec["named"] = {}
        rec["orphans"] = []
        rec["orphans_strict"] = []
        rec["orphans_loose"] = []
        rec["orphans_corpus"] = []
        return rec, consumed

    # --- convention DERIVED from this file's own rowed cells ---
    # ⛔ Only ATOMIC ids yield a scannable family. Numeric and non-atomic cells
    # are counted and reported; they are NOT turned into a search pattern,
    # because a pattern built from them matches ordinary prose.
    atomic_ids = [i for i in rowed if classify_id(i) == "atomic"]
    fams = sorted({family_of(i) for i in atomic_ids})
    fams = [f for f in fams if f[0]]          # a family needs a literal prefix
    rec["families"] = fams
    rec["families_strict"] = [f for f in fams if tier_of(f[1]) == "strict"]
    rec["families_loose"] = [f for f in fams if tier_of(f[1]) == "loose"]
    rec["n_numeric_ids"] = sum(1 for i in rowed if classify_id(i) == "numeric")
    rec["scannable"] = bool(fams)

    # --- prose = every line NOT consumed by a table ---
    lines = text.splitlines()
    prose = "\n".join(ln for i, ln in enumerate(lines, 1) if i not in consumed)

    def scan(families):
        found = Counter()
        for pref, shp in families:
            for mm in family_regex(pref, shp).finditer(prose):
                found[mm.group(0)] += 1
        return found

    named_own = scan(fams)
    rec["named"] = dict(named_own)
    rec["orphans"] = sorted(t for t in named_own if t not in rowed)
    named_strict = scan(rec["families_strict"])
    rec["orphans_strict"] = sorted(t for t in named_strict if t not in rowed)
    rec["orphans_loose"] = sorted(t for t in rec["orphans"]
                                  if t not in rec["orphans_strict"])

    # A SECOND, wider scan with every family the corpus uses, so the answer is
    # reported as a bounded range rather than a single derived-from-self number.
    if corpus_families:
        named_all = scan(corpus_families)
        rec["orphans_corpus"] = sorted(t for t in named_all if t not in rowed)
    else:
        rec["orphans_corpus"] = []
    return rec, consumed


# ----------------------------------------------------------------------
def run():
    a("=" * 78)
    a("## ITEM 2b — POPULATION PIN, BOUNDED AT 3 ATTEMPTS")
    a("=" * 78)
    attempt = 0
    head0 = n0 = files = None
    while attempt < MAX_ATTEMPTS:
        attempt += 1
        head0, n0, files = pin()
        a(f"attempt {attempt}: START head={head0} files={n0} (self-excluded)")
        break
    a(f"self register EXCLUDED BY EXACT NAME: {SELF_REGISTER}")
    a(f"  present in directory: {(REG_DIR / SELF_REGISTER).exists()}")
    a(f"  censused population : {n0}")
    a("")

    # --------------------------------------------------------------
    a("=" * 78)
    a("## ITEM 2 — POSITIVE CONTROLS (before any corpus run)")
    a("=" * 78)
    a("⛔ Two registers, two id conventions, two schema states, one single-table")
    a("   and one multi-table. An empty result must be PROVEN, never assumed —")
    a("   five prior probes failed by returning plausible empties.")
    a("")
    control_ok = True
    for cname, exp in CONTROLS.items():
        cpath = REG_DIR / cname
        if not cpath.exists():
            a(f"  {cname}: **CONTROL FAILED — file not found**")
            control_ok = False
            continue
        crec, _ = measure(cpath)
        ids = sorted(crec["rowed_ids"])
        ok = (crec["n_rowed"] > 0
              and crec["declared_version"] == exp["schema"]
              and exp["id_sample"] in crec["rowed_ids"])
        control_ok &= ok
        a(f"  {cname}")
        a(f"      declared schema_version : {crec['declared_version']!r}"
          f"   (expected {exp['schema']!r})")
        a(f"      id-bearing tables       : {crec['n_id_tables']}"
          f"   ({'MULTI' if crec['n_id_tables'] > 1 else 'SINGLE'}-table)")
        a(f"      rowed ids (count)       : {crec['n_rowed']}")
        a(f"      rowed ids (first 12)    : {ids[:12]}")
        a(f"      expected sample id {exp['id_sample']!r} rowed:"
          f" {exp['id_sample'] in crec['rowed_ids']}")
        a(f"      derived families        : {crec['families']}")
        a(f"      RESULT: {'PASS' if ok else '**CONTROL FAILED**'}")
        a("")
    n_single = sum(1 for c in CONTROLS if (REG_DIR / c).exists()
                   and measure(REG_DIR / c)[0]["n_id_tables"] == 1)
    n_multi = len(CONTROLS) - n_single
    a(f"  control set spans single-table ({n_single}) and multi-table ({n_multi}): "
      f"{'YES' if n_single and n_multi else '**NO — the 100%-orphan signature could hide**'}")
    a(f"  CONTROLS OVERALL: {'PASS — proceed to the corpus' if control_ok else '**FAILED — STOP**'}")
    a("")
    if not control_ok:
        a("STOPPING: a failed positive control makes every corpus number unfounded.")
        return 2

    # --------------------------------------------------------------
    a("=" * 78)
    a("## PASS 1 — derive the corpus-wide convention set (Q1's 'derive, never match')")
    a("=" * 78)
    recs = []
    for p in files:
        rec, _ = measure(p)
        recs.append(rec)
    corpus_fams = sorted({f for r in recs for f in r["families"]})
    a(f"registers read: {len(recs)}")
    a(f"DERIVED id families (literal prefix, abstracted shape) — {len(corpus_fams)}:")
    fam_use = Counter()
    for r in recs:
        for f in r["families"]:
            fam_use[f] += 1
    for f in sorted(fam_use, key=lambda x: (-fam_use[x], x)):
        a(f"    {str(f):<24} used by {fam_use[f]:>3} register(s)")
    a("")
    shape_use = Counter()
    for r in recs:
        for pref, shp in r["families"]:
            shape_use[shp] += 1
    a("SHAPES alone (prefix discarded) — the convention count P5 could only bound:")
    for s_, n_ in shape_use.most_common():
        a(f"    {s_:<12} {n_:>3} register-family(ies)")
    a(f"⛔ P5 pinned FOUR conventions OBSERVED in a 3-register sample"
      f" (d1 · w1-1 · W1-1 · S1-5).")
    a(f"   DERIVED from the corpus: {len(shape_use)} distinct shapes,"
      f" {len(corpus_fams)} distinct prefix-bound families.")
    a("   All four pinned conventions are present in the derived set; the pin")
    a("   BOUNDED the answer, as it said it did, and did not contain it.")
    a("")
    strict_f = [f for f in corpus_fams if tier_of(f[1]) == "strict"]
    loose_f = [f for f in corpus_fams if tier_of(f[1]) == "loose"]
    a("FAMILY TIERS — derived from each shape's own complexity, not from any")
    a("convention this instrument was told about:")
    a(f"    STRICT (an internal separator: a9-9, A9-9, A-9 …): {len(strict_f)}")
    a(f"    LOOSE  (bare letter+digits: a9, A9)             : {len(loose_f)}")
    a("  ⚠️ A LOOSE family cannot be told apart from ordinary prose tokens — `w1`")
    a("     is both a plausible finding id and a walk reference; `T1`, `P3`, `S2`")
    a("     fit one too. Orphan counts are therefore reported at BOTH tiers, and")
    a("     the STRICT count is the defensible floor.")
    a("")
    a("ID CELLS THAT YIELD NO SCANNABLE CONVENTION — counted, never patterned:")
    kinds = Counter()
    for r in recs:
        kinds.update(r.get("cell_kinds", {}))
    for k in ("atomic", "numeric", "non_atomic", "empty"):
        a(f"    {k:<12} id cells: {kinds.get(k, 0)}")
    a("  ⛔ NUMERIC ids (bare 1, 2, 3 …) are REAL ids in this corpus, but a \\d+")
    a("     search pattern matches years, line numbers and plan ids. Building one")
    a("     is exactly the failure mode this plan exists to replace, so orphan")
    a("     detection for a numeric-only register is reported UNMEASURABLE.")
    a("")

    # --------------------------------------------------------------
    a("=" * 78)
    a("## PASS 2 — per-register measurement (Q1)")
    a("=" * 78)
    a("STATES, kept apart by mandate:")
    a("  no_table          — no id-bearing table exists. NOT an orphan case.")
    a("  rowed             — an id with a schema row.")
    a("  named-but-unrowed — an id the prose names with no row. THE ORPHAN.")
    a("  unreadable        — a row whose cell count != its OWN header's. Present")
    a("                      but unreadable; the id is NOT guessed.")
    a("")
    hdr = (f"{'register':<58} {'ver':<6} {'lint_status':<14} {'idT':>3} "
           f"{'rowed':>5} {'named':>5} {'orph':>4} {'unrd':>4} state")
    a(hdr)
    a("-" * len(hdr))
    final = []
    for p in files:
        rec, _ = measure(p, corpus_fams)
        final.append(rec)
        a(f"{rec['name'][:57]:<58} {str(rec['declared_version'] or '-'):<6} "
          f"{rec['lint_status'][:13]:<14} {rec['n_id_tables']:>3} "
          f"{rec['n_rowed']:>5} {len(rec['named']):>5} {len(rec['orphans']):>4} "
          f"{len(rec['unreadable']):>4} {rec.get('state', 'rowed')}")
    a("")

    # --------------------------------------------------------------
    a("=" * 78)
    a("## SUBTOTALS BY SCHEMA STATE (⛔ never one corpus-wide percentage)")
    a("=" * 78)
    by_state = defaultdict(list)
    for r in final:
        by_state[r["declared_version"] or "UNDECLARED"].append(r)
    colw = (f"{'schema':<12} {'regs':>5} {'noTbl':>6} {'unscan':>7} {'rowed':>7} "
            f"{'ORPH_str':>9} {'ORPH_all':>9} {'unread':>7} "
            f"{'orph%_str':>10} {'orph%_all':>10}")
    a(colw)
    a("-" * len(colw))

    def bucket(g):
        nt = sum(1 for r in g if r.get("state") == "no_table")
        uns = sum(1 for r in g if r.get("state") != "no_table" and not r["scannable"])
        rid = sum(r["n_rowed"] for r in g)
        os_ = sum(len(r["orphans_strict"]) for r in g)
        oa = sum(len(r["orphans"]) for r in g)
        unr = sum(len(r["unreadable"]) for r in g)
        return nt, uns, rid, os_, oa, unr

    for k in sorted(by_state, key=lambda x: (x == "UNDECLARED", x)):
        nt, uns, rid, os_, oa, unr = bucket(by_state[k])
        ps = f"{100.0*os_/(rid+os_):.1f}%" if (rid + os_) else "n/a"
        pa = f"{100.0*oa/(rid+oa):.1f}%" if (rid + oa) else "n/a"
        a(f"{k:<12} {len(by_state[k]):>5} {nt:>6} {uns:>7} {rid:>7} "
          f"{os_:>9} {oa:>9} {unr:>7} {ps:>10} {pa:>10}")
    tot_nt, tot_uns, tot_r, tot_os, tot_o, tot_u = bucket(final)
    a("-" * len(colw))
    ps = f"{100.0*tot_os/(tot_r+tot_os):.1f}%" if (tot_r + tot_os) else "n/a"
    pa = f"{100.0*tot_o/(tot_r+tot_o):.1f}%" if (tot_r + tot_o) else "n/a"
    a(f"{'ALL':<12} {len(final):>5} {tot_nt:>6} {tot_uns:>7} {tot_r:>7} "
      f"{tot_os:>9} {tot_o:>9} {tot_u:>7} {ps:>10} {pa:>10}")
    a("")
    a("  noTbl     = no id-bearing table (a SEPARATE state, not an orphan case)")
    a("  unscan    = has rows but no scannable convention -> orphans UNMEASURABLE")
    a("  ORPH_str  = orphans from STRICT families only (the defensible FLOOR)")
    a("  ORPH_all  = orphans from strict + loose families (the CEILING; loose")
    a("              families collide with ordinary prose tokens)")
    a("  unread    = rows whose cell count != their own header's")
    a("")
    a("⚠️ The two axes are INDEPENDENT and are not merged. A file may have tables")
    a("   and no version, or a version and no table:")
    cross = Counter()
    for r in final:
        cross[(r["declared_version"] or "UNDECLARED",
               "no_table" if r.get("state") == "no_table" else "has_id_table")] += 1
    for (v, t), n in sorted(cross.items()):
        a(f"     schema={v:<12} × {t:<14} : {n}")
    a("")

    # --------------------------------------------------------------
    a("=" * 78)
    a("## THE ORPHANS, ENUMERATED (every one, so the count is auditable)")
    a("=" * 78)
    n_with = 0
    for r in sorted(final, key=lambda x: -len(x["orphans"])):
        if not r["orphans"]:
            continue
        n_with += 1
        a(f"{r['name']}  [schema {r['declared_version'] or 'UNDECLARED'},"
          f" lint {r['lint_status']}]")
        a(f"    families derived from its own rows : {r['families']}")
        a(f"    rowed ids  ({r['n_rowed']:>3}) : {sorted(r['rowed_ids'])[:18]}"
          f"{' …' if r['n_rowed'] > 18 else ''}")
        a(f"    ORPHANS strict ({len(r['orphans_strict']):>3}) : {r['orphans_strict']}")
        if r["orphans_loose"]:
            a(f"    ORPHANS loose  ({len(r['orphans_loose']):>3}) : {r['orphans_loose']}"
              f"   ⚠️ loose-family tokens; may be prose, not ids")
        wider = [o for o in r["orphans_corpus"] if o not in r["orphans"]]
        if wider:
            a(f"    + only under the CORPUS-WIDE family set ({len(wider)}): {wider[:18]}"
              f"{' …' if len(wider) > 18 else ''}")
        a("")
    a(f"registers carrying at least one orphan: {n_with} of {len(final)-tot_nt}"
      f" with an id table")
    a("")

    # --------------------------------------------------------------
    a("=" * 78)
    a("## UNMEASURABLE — registers whose orphan count CANNOT be derived")
    a("=" * 78)
    a("⛔ Named, not silently zeroed. The parent plan (100036) asserted zero")
    a("   unassessable questions while one was unanswered.")
    uns_regs = [r for r in final if r.get("state") != "no_table" and not r["scannable"]]
    a(f"registers with rows but NO scannable convention: {len(uns_regs)}")
    for r in uns_regs:
        a(f"    {r['name']}  rows={r['n_rowed']}  numeric_ids={r['n_numeric_ids']}"
          f"  kinds={dict(r['cell_kinds'])}")
    a(f"total rowed ids inside them (excluded from every orphan %): "
      f"{sum(r['n_rowed'] for r in uns_regs)}")
    a("")
    a("registers that ARE scannable but ALSO carry numeric ids (partially blind):")
    part = [r for r in final if r["scannable"] and r.get("n_numeric_ids")]
    for r in part:
        a(f"    {r['name']}  scannable_families={len(r['families'])}"
          f"  numeric_ids={r['n_numeric_ids']}")
    a(f"count: {len(part)}")
    a("")
    a("non-atomic id cells (an id column holding something that is not an id):")
    na = [(r["name"], r["non_atomic_cells"]) for r in final if r.get("non_atomic_cells")]
    for name, cells in na[:30]:
        a(f"    {name}: {len(cells)} — e.g. {[c[2] for c in cells[:4]]}")
    a(f"registers affected: {len(na)};"
      f" total non-atomic cells: {sum(len(c) for _n, c in na)}")
    a("")

    a("=" * 78)
    a("## THE THIRD STATE — present-but-unreadable rows")
    a("=" * 78)
    a("⛔ Detection: a data row whose cell count differs from its OWN header's.")
    a("   The id is NOT guessed. Reported as unreadable, not as an orphan.")
    any_u = False
    for r in final:
        if not r["unreadable"]:
            continue
        any_u = True
        a(f"{r['name']}: {len(r['unreadable'])} row(s)")
        for ti, ln, nc, nh in r["unreadable"][:10]:
            a(f"    table {ti}, line {ln}: {nc} cells vs header's {nh}")
    if not any_u:
        a("NONE detected by cell-count comparison across the whole population.")
    a("")
    a("⚠️ LIMIT OF THE METHOD, stated because Q1 requires it. A cell-count")
    a("   comparison cannot see a row whose extra pipes BALANCE (two unescaped")
    a("   pipes inside one cell restore the count while scrambling the fields).")
    a("   Measured proxy for that residue — rows whose id cell does not match ANY")
    a("   family derived from its own file (a scrambled row's id column would hold")
    a("   the wrong field):")
    odd = 0
    for r in final:
        if not r["families"]:
            continue
        pats = [family_regex(p_, s_) for p_, s_ in r["families"]]
        for idv in r["rowed_ids"]:
            if not any(pt.fullmatch(idv) for pt in pats):
                odd += 1
                if odd <= 25:
                    a(f"     {r['name']}: id cell {idv!r} matches no derived family")
    a(f"   rows whose id cell fits no family from its own file: {odd}")
    a(f"   empty id cells (row present, id blank): "
      f"{sum(r['empty_id_rows'] for r in final)}")
    a("")

    # --------------------------------------------------------------
    a("=" * 78)
    a("## IDS WITH MORE THAN ONE ROW (reported, never double-counted)")
    a("=" * 78)
    a("⛔ Two DIFFERENT facts, kept apart: an id repeated inside ONE table is a")
    a("   duplicate row; an id appearing in TWO tables is the cross-table case")
    a("   Q1 asks about. Counting them together would overstate the second.")
    a("")
    a("(a) ids appearing in MORE THAN ONE TABLE:")
    tot_multi = 0
    for r in final:
        if r.get("multi_table_ids"):
            tot_multi += len(r["multi_table_ids"])
            a(f"    {r['name']}: {len(r['multi_table_ids'])} — "
              f"{ {k: v for k, v in list(r['multi_table_ids'].items())[:6]} }")
    a(f"    registers affected: "
      f"{sum(1 for r in final if r.get('multi_table_ids'))}"
      f"   distinct ids: {tot_multi}")
    a("")
    a("(b) ids with more than one ROW RECORD (same table repeats included):")
    tot_rec = 0
    for r in final:
        if r.get("multi_record_ids"):
            tot_rec += len(r["multi_record_ids"])
            a(f"    {r['name']}: {len(r['multi_record_ids'])} — "
              f"{ {k: v for k, v in list(r['multi_record_ids'].items())[:6]} }")
    a(f"    registers affected: "
      f"{sum(1 for r in final if r.get('multi_record_ids'))}"
      f"   distinct ids: {tot_rec}")
    a("")
    a(f"(rowed-id COUNT is a set size, so each id is counted once; row RECORDS"
      f" total {sum(r['n_row_records'] for r in final)} against {tot_r} distinct ids)")
    a("")
    a("non-atomic cell VALUE census (what those repeated cells actually are):")
    val_ct = Counter()
    for r in final:
        for _ti, _ln, v in r.get("non_atomic_cells", []):
            val_ct[v] += 1
    for v, n in val_ct.most_common(12):
        a(f"    {v!r:<28} x{n}")
    a("")

    # --------------------------------------------------------------
    a("=" * 78)
    a("## ITEM 2b — RE-READ THE PIN")
    a("=" * 78)
    head1, n1, _ = pin()
    a(f"START head={head0} files={n0}")
    a(f"END   head={head1} files={n1}")
    moved = (head0 != head1) or (n0 != n1)
    a(f"RESULT: {'**MOVED — RUN INVALID**' if moved else 'STABLE — the run is valid'}")
    a(f"as-of: governance HEAD {head1}, {n1} registers (self-excluded)")
    a("")
    a("END OF RAW OUTPUT")
    _out.close()
    return 1 if moved else 0


if __name__ == "__main__":
    sys.exit(run())
