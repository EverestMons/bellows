#!/usr/bin/env python3
"""cycle_log_signal_census — where does the walk record actually live?

DIAGNOSTIC INSTRUMENT for plan `diagnostic-cycle-log-signal` (manual_bootstrap,
2026-09-05). Prices — does not repair — the divergence between a plan's BODY
Cycle Log (the only thing `cycle_check` reads) and the plan's WALK REGISTER
(where the findings actually get written).

⛔ It IMPORTS the two production readers and CALLS them. It re-implements
neither format parser:
    cycle_yields.extract_dc_blocks      — find the Drafting Cycle block
    cycle_check.parse_block             — body walk data + walk_register_ref
    cycle_check.check_assert_2          — the AUTHORITATIVE resolution verdict
    cycle_check.run_check               — verdict + BASIS warnings
    cycle_check._compute_coherence      — the manifest coherence field
    walk_register_lint.validate_file    — register status + row records
    walk_register_lint.extract_tables   — register fold-table rows
    walk_register_lint.is_fold_table    — which tables are fold tables

The one thing this file DOES carry is a *mirror* of cycle_check's three-step
register-ref resolution — because `check_assert_2` returns a verdict but not the
resolved PATH, and the path is what the register reader needs. The mirror is not
trusted: every plan's mirror verdict is cross-checked against `check_assert_2`'s
own, and any disagreement is reported as a CONTROL FAILURE. Section 0 states the
result of that cross-check before any finding is offered.

Read-only. Writes nothing, commits nothing, edits no checker.
"""

import os
import re
import sqlite3
import sys
from pathlib import Path

BELLOWS_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BELLOWS_ROOT))
sys.path.insert(0, str(BELLOWS_ROOT / "scripts"))

import cycle_check                                    # noqa: E402
import walk_register_lint as wrl                      # noqa: E402
from cycle_yields import extract_dc_blocks            # noqa: E402

DONE = BELLOWS_ROOT / "knowledge" / "decisions" / "Done"
DRAFTS = BELLOWS_ROOT / "knowledge" / "decisions" / "drafts"

POSITIVE_CONTROL = "executable-lessons-destination-v2.md"
POSITIVE_CONTROL_EXPECT = {"body_walks": 0, "register_rows": 4}

out = []


def a(line=""):
    out.append(line)


# ----------------------------------------------------------------------
# Register-ref resolution — a MIRROR of cycle_check.check_assert_2's step
# order (absolute → git_root/ref → governance_root/ref), kept only because
# that function does not hand back the path it resolved.
# ----------------------------------------------------------------------
def resolve_ref(ref, plan_path):
    """Return (resolved_path_or_None, step_that_won, attempts[list of (label, path, exists)])."""
    attempts = []
    if ref is None:
        return None, "no-ref", attempts

    if Path(ref).is_absolute():
        cand = Path(ref)
        try:
            ok = cand.exists()
        except OSError:
            ok = False
        attempts.append(("1:absolute", str(cand), ok))
        return (cand if ok else None), ("1:absolute" if ok else "none"), attempts

    git_root = cycle_check._find_git_root(plan_path)
    if git_root:
        cand = git_root / ref
        try:
            ok = cand.exists()
        except OSError:
            ok = False
        attempts.append(("2:git_root", str(cand), ok))
        if ok:
            return cand, "2:git_root", attempts
    else:
        attempts.append(("2:git_root", "<no git root>", False))

    try:
        from bellows_root import resolve_governance_root
        gov_root = resolve_governance_root()
    except Exception:
        gov_root = None
    if gov_root:
        cand = gov_root / ref
        try:
            ok = cand.exists()
        except OSError:
            ok = False
        attempts.append(("3:gov_root", str(cand), ok))
        if ok:
            return cand, "3:gov_root", attempts
    else:
        attempts.append(("3:gov_root", "<unresolvable governance root>", False))

    return None, "none", attempts


def register_rows(path):
    """(fold_table_row_count, file_status, lint_row_count, n_fold_tables) via walk_register_lint."""
    try:
        text = path.read_text(encoding="utf-8")
    except Exception as e:
        return None, f"UNREADABLE:{e}", None, None
    tables, _consumed = wrl.extract_tables(text)
    fold_rows = 0
    n_fold = 0
    for hdr, data, _hl in tables:
        if wrl.is_fold_table(hdr):
            n_fold += 1
            fold_rows += len(data)
    try:
        status, rows, _shapes = wrl.validate_file(path)
    except Exception as e:
        status, rows = f"VALIDATE_ERROR:{e}", []
    return fold_rows, status, len(rows), n_fold


def survey():
    """One record per plan file that declares a walk_register_ref."""
    recs = []
    skipped = []
    for d, where in ((DONE, "Done"), (DRAFTS, "drafts")):
        for p in sorted(d.glob("*.md")):
            try:
                text = p.read_text(encoding="utf-8")
            except Exception as e:
                skipped.append((p.name, where, f"unreadable:{e}"))
                continue
            blocks = extract_dc_blocks(text)
            if len(blocks) != 1:
                skipped.append((p.name, where, f"dc_blocks={len(blocks)}"))
                continue
            parsed = cycle_check.parse_block(blocks[0])
            ref = parsed["walk_register_ref"]
            if not ref:
                skipped.append((p.name, where, "no walk_register_ref"))
                continue

            rp, step, attempts = resolve_ref(ref, p)
            # CONTROL: cycle_check's own verdict on the same ref.
            try:
                cc_reg, _u, _g, _w = cycle_check.check_assert_2(parsed, p)
            except Exception as e:
                cc_reg = f"EXC:{e}"
            mirror = "PASS" if rp is not None else "UNRESOLVED"

            fold_rows = status = lint_rows = n_fold = None
            if rp is not None:
                fold_rows, status, lint_rows, n_fold = register_rows(rp)

            recs.append({
                "name": p.name, "where": where, "path": p, "ref": ref,
                "walk_data": parsed["walk_data"],
                "body_walks": len(parsed["walk_data"]),
                "max_walk": max(parsed["walk_data"]) if parsed["walk_data"] else None,
                "restructuring": sorted(parsed["restructuring_walks"]),
                "resolved": rp, "step": step, "attempts": attempts,
                "mirror": mirror, "cc_assert2": cc_reg,
                "control_ok": (mirror == cc_reg),
                "reg_rows": fold_rows, "reg_status": status,
                "reg_lint_rows": lint_rows, "reg_fold_tables": n_fold,
                "parsed": parsed, "text": text,
            })
    return recs, skipped


def main():
    recs, skipped = survey()

    a("=" * 78)
    a("cycle_log_signal_census — RAW OUTPUT")
    a("plan: diagnostic-cycle-log-signal (manual_bootstrap, 2026-09-05)")
    a("=" * 78)
    a(f"corpus roots: {DONE}")
    a(f"              {DRAFTS}")
    a(f"cycle_check   : {BELLOWS_ROOT / 'scripts' / 'cycle_check.py'}")
    a(f"walk_register_lint schema version: {wrl.VALIDATOR_SCHEMA_VERSION}")
    a("")

    # ------------------------------------------------------------------
    a("## SECTION 0 — CONTROLS (read before any finding)")
    a("")
    # C0.1 positive control
    pc = next((r for r in recs if r["name"] == POSITIVE_CONTROL), None)
    a(f"C0.1  POSITIVE CONTROL — {POSITIVE_CONTROL}")
    if pc is None:
        a("      RESULT: **CONTROL FAILED** — plan not in the surveyed set.")
    else:
        got = {"body_walks": pc["body_walks"], "register_rows": pc["reg_rows"]}
        ok = got == POSITIVE_CONTROL_EXPECT
        a(f"      expected {POSITIVE_CONTROL_EXPECT}")
        a(f"      measured {got}")
        a(f"      resolved register: {pc['resolved']}")
        a(f"      register status  : {pc['reg_status']}")
        a(f"      RESULT: {'PASS — the instrument discriminates' if ok else '**CONTROL FAILED**'}")
    a("")

    # C0.2 mirror-vs-cycle_check resolution agreement
    bad = [r for r in recs if not r["control_ok"]]
    a("C0.2  RESOLVER MIRROR vs cycle_check.check_assert_2 (every plan)")
    a(f"      plans compared : {len(recs)}")
    a(f"      disagreements  : {len(bad)}")
    for r in bad:
        a(f"        {r['name']}: mirror={r['mirror']} cycle_check={r['cc_assert2']}")
    a(f"      RESULT: {'PASS — resolution is cycle_check-identical' if not bad else '**CONTROL FAILED** — findings below are NOT cycle_check-faithful'}")
    a("")

    # C0.3 negative control: an unresolvable ref must NOT produce rows
    unres = [r for r in recs if r["resolved"] is None]
    leak = [r for r in unres if r["reg_rows"]]
    a("C0.3  NEGATIVE CONTROL — an unresolved ref must yield no register rows")
    a(f"      unresolved plans: {len(unres)}   with non-empty rows: {len(leak)}")
    a(f"      RESULT: {'PASS' if not leak else '**CONTROL FAILED**'}")
    a("")

    a(f"C0.4  files skipped (no ref / no single DC block): {len(skipped)}")
    for n, w, why in skipped:
        if "no walk_register_ref" not in why:
            a(f"        {w}/{n}: {why}")
    a("      (plans skipped only for 'no walk_register_ref' are not listed — they are")
    a("       outside P1 by definition.)")
    a("")

    # ------------------------------------------------------------------
    a("=" * 78)
    a("## SECTION 1 — ITEM 1: re-derivation of P1-P8")
    a("=" * 78)
    a("")
    p1 = len(recs)
    p2 = sum(1 for r in recs if r["body_walks"] > 0)
    p3 = [r for r in recs if r["body_walks"] == 0]
    resolved = [r for r in recs if r["resolved"] is not None]
    p4 = [r for r in p3 if r["resolved"] is not None and (r["reg_rows"] or 0) > 0]
    p5 = [r for r in p3 if r["resolved"] is not None and (r["reg_rows"] or 0) == 0]
    p6 = [r for r in recs if r["resolved"] is None]

    a(f"P1  plans declaring a walk_register_ref (Done + drafts) : {p1}   [pin 103]")
    a(f"P2  bodies carrying per-lens walk data (walk_data > 0)   : {p2}   [pin 94]")
    a(f"P3  bodies EMPTY (walk_data == 0)                        : {len(p3)}   [pin 9]"
      f"   ({100.0*len(p3)/p1:.1f}%)")
    a(f"P4  CONJUNCTION: body empty AND resolvable register with rows : {len(p4)}   [pin 2]")
    for r in p4:
        a(f"      - {r['where']}/{r['name']}  rows={r['reg_rows']}  status={r['reg_status']}")
    a(f"P5  legitimate walk-0: body empty AND register empty     : {len(p5)}   [pin 1]")
    for r in p5:
        a(f"      - {r['where']}/{r['name']}  rows={r['reg_rows']}  status={r['reg_status']}")
    a(f"P6  UNRESOLVABLE refs                                    : {len(p6)}   [pin 6]")
    for r in p6:
        a(f"      - {r['where']}/{r['name']}  ref={r['ref']!r}")
    a("")
    a("P3 residue (body empty, ref unresolvable — placeable in neither P4 nor P5):")
    p3_unres = [r for r in p3 if r["resolved"] is None]
    for r in p3_unres:
        a(f"      - {r['where']}/{r['name']}  ref={r['ref']!r}")
    a(f"      count: {len(p3_unres)}   (P4 {len(p4)} + P5 {len(p5)} + residue"
      f" {len(p3_unres)} = {len(p4)+len(p5)+len(p3_unres)} = P3 {len(p3)})")
    a("")

    a("PIN RECONCILIATION — every mismatch is a FINDING (Item 1).")
    a(f"    P1 pin 103 / measured {p1}    delta {p1-103:+d}")
    a(f"    P2 pin  94 / measured {p2}    delta {p2-94:+d}")
    a(f"    P3 pin   9 / measured {len(p3)}    delta {len(p3)-9:+d}")
    a(f"    P4 pin   2 / measured {len(p4)}    delta {len(p4)-2:+d}")
    a(f"    P5 pin   1 / measured {len(p5)}    delta {len(p5)-1:+d}")
    a(f"    P6 pin   6 / measured {len(p6)}    delta {len(p6)-6:+d}")
    a("")

    a("P7  the three silent checks — VERIFIED IN SOURCE AND BY BEHAVIOUR")
    a("    ⛔ Item 1 HALTS the plan only on P7's failure. Each sub-claim is")
    a("       probed against the LIVE module, not recalled.")
    a("")
    src = (BELLOWS_ROOT / "scripts" / "cycle_check.py").read_text(encoding="utf-8")

    # P7a — BASIS only inside _escalate
    basis_lines = [i + 1 for i, ln in enumerate(src.splitlines()) if '"BASIS:' in ln or "'BASIS:" in ln]
    esc_start = src.index("def _escalate(tag):")
    esc_end = src.index("if current_walk in parsed[", esc_start)
    esc_span = (src[:esc_start].count("\n") + 1, src[:esc_end].count("\n") + 1)
    inside = [n for n in basis_lines if esc_span[0] <= n <= esc_span[1]]
    a(f"    P7a  BASIS emission sites in cycle_check.py: lines {basis_lines}")
    a(f"         _escalate() body spans lines {esc_span[0]}-{esc_span[1]}")
    a(f"         sites inside _escalate: {inside}  outside: {sorted(set(basis_lines) - set(inside))}")
    p7a_src = (basis_lines and set(basis_lines) == set(inside))
    a(f"         SOURCE: {'HOLDS — BASIS is reachable only via _escalate' if p7a_src else '**PREMISE CHANGED**'}")

    # behavioural: run run_check with warnings over the whole corpus
    basis_on_nonescalate = []
    verdicts = {}
    for r in recs:
        w = []
        try:
            v, _c = cycle_check.run_check(r["path"], warnings=w)
        except Exception as e:
            v, w = f"EXC:{e}", []
        verdicts[r["name"]] = v
        r["verdict"] = v
        r["warnings"] = w
        if any(x.startswith("BASIS:") for x in w) and not str(v).startswith("ESCALATE"):
            basis_on_nonescalate.append((r["name"], v))
    a(f"         BEHAVIOUR: ran run_check(warnings=[]) over all {len(recs)} plans;"
      f" BASIS emitted on a non-ESCALATE verdict in {len(basis_on_nonescalate)} of them.")
    p7a = p7a_src and not basis_on_nonescalate
    a(f"         P7a: {'HOLDS' if p7a else '**PREMISE CHANGED — HALT**'}")
    a("")

    # P7b — _compute_coherence returns N/A at total_walks == 0
    a("    P7b  _compute_coherence on total_walks == 0")
    coh_cases = []
    for r in recs:
        if r["body_walks"] == 0 and r["resolved"] is not None:
            try:
                c = cycle_check._compute_coherence(r["parsed"], r["path"])
            except Exception as e:
                c = f"EXC:{e}"
            coh_cases.append((r["name"], c))
    for n, c in coh_cases:
        a(f"         {n}: {c!r}")
    p7b_live = all(c == "N/A" for _n, c in coh_cases) if coh_cases else None
    a(f"         live cases (body empty, register resolvable): {len(coh_cases)}")
    a(f"         all returned 'N/A': {p7b_live}")
    # source guard: the branch must still exist
    p7b_src = "if total_walks == 0:" in src and 'return "N/A"' in src
    a(f"         SOURCE: `if total_walks == 0: return \"N/A\"` present: {p7b_src}")
    p7b = bool(p7b_src) and (p7b_live in (True, None))
    a(f"         P7b: {'HOLDS' if p7b else '**PREMISE CHANGED — HALT**'}")
    a("")

    # P7c — coherence computed only under --emit-manifest
    call_sites = [i + 1 for i, ln in enumerate(src.splitlines())
                  if "_compute_coherence(" in ln and not ln.strip().startswith("def ")]
    em_start = src.index("def emit_manifest(plan_path):")
    em_line = src[:em_start].count("\n") + 1
    main_start = src.index("def main():")
    main_line = src[:main_start].count("\n") + 1
    a("    P7c  _compute_coherence call sites")
    a(f"         call sites: lines {call_sites}")
    a(f"         emit_manifest() spans lines {em_line}-{main_line - 1}")
    p7c = all(em_line <= n < main_line for n in call_sites) and len(call_sites) == 1
    a(f"         all inside emit_manifest, and exactly one: {p7c}")
    a(f"         P7c: {'HOLDS' if p7c else '**PREMISE CHANGED — HALT**'}")
    a("")
    a(f"    P7 OVERALL: {'HOLDS — the premise is intact, the plan proceeds' if (p7a and p7b and p7c) else '**FAILED — HALT AND RE-DERIVE**'}")
    a("")

    # P8 in-flight
    a("P8  in-flight plans (re-derived at execution)")
    try:
        db = BELLOWS_ROOT / "lifecycle.db"
        con = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
        cur = con.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tbls = [t[0] for t in cur.fetchall()]
        a(f"      lifecycle.db tables: {tbls}")
        cur.execute("SELECT lifecycle_state, COUNT(*) FROM plans GROUP BY lifecycle_state")
        a(f"      plans by lifecycle_state: {cur.fetchall()}")
        cur.execute(
            "SELECT id, lifecycle_state, type, title, plan_doc_ref FROM plans "
            "WHERE lifecycle_state NOT IN ('closed','done','complete','completed',"
            "'abandoned','superseded') ORDER BY id")
        rows = cur.fetchall()
        a(f"      IN-FLIGHT (lifecycle_state not a terminal value): {len(rows)}")
        for pid, st, ty, ti, ref in rows:
            a(f"        #{pid} [{st}] {ty}: {str(ti)[:70]}")
            a(f"              plan_doc_ref={ref}")
        a("      ⚠️ This plan is manual_bootstrap: it holds NO lifecycle id and appears")
        a("         in no row above. That absence is the mode working as declared, not")
        a("         a measurement gap.")
        con.close()
    except Exception as e:
        a(f"      lifecycle.db read failed: {e}")
    a("")

    # ------------------------------------------------------------------
    a("=" * 78)
    a("## SECTION 2 — Q1: the unresolvable walk_register_refs, CLASSIFIED")
    a("=" * 78)
    a("⛔ Classification only. Nothing here is repaired.")
    a("")
    if not p6:
        a("NONE.")
    for r in p6:
        a(f"### {r['where']}/{r['name']}")
        a(f"    declared ref : {r['ref']!r}")
        a(f"    ref shape    : {'ABSOLUTE' if Path(r['ref']).is_absolute() else 'RELATIVE'}")
        a( "    resolution attempted (cycle_check's own three-step order):")
        for label, cand, ok in r["attempts"]:
            a(f"      step {label:<12} -> {cand}")
            a(f"           exists: {ok}")
        # classification evidence
        base = Path(r["ref"]).name
        hits = []
        for root in (BELLOWS_ROOT, Path("/Users/marklehn/Developer/eluvian-governance")):
            for dirpath, dirnames, filenames in os.walk(root):
                if ".git" in dirpath.split(os.sep):
                    continue
                if base in filenames:
                    hits.append(os.path.join(dirpath, base))
        a(f"    basename {base!r} found elsewhere on disk: {len(hits)}")
        for h in hits[:6]:
            a(f"      -> {h}")
        # was it ever committed under this name?
        a(f"    body walks   : {r['body_walks']}   verdict now: {r.get('verdict')}")
        a("")

    # ------------------------------------------------------------------
    a("=" * 78)
    a("## SECTION 3 — Q2: the 2x2, body walks x register rows")
    a("=" * 78)
    a("")
    def cell(body_pred, rows_pred):
        return [r for r in resolved if body_pred(r["body_walks"]) and rows_pred(r["reg_rows"] or 0)]
    z = lambda v: v == 0
    nz = lambda v: v > 0
    c00, c01 = cell(z, z), cell(z, nz)
    c10, c11 = cell(nz, z), cell(nz, nz)
    a(f"Population: {p1} plans declaring a ref; {len(resolved)} resolvable,"
      f" {len(p6)} NOT (excluded from the grid — see Q1).")
    a("")
    a("                       | register rows == 0 | register rows > 0  |")
    a("    -------------------+--------------------+--------------------+------")
    a(f"    body walks == 0    | {len(c00):>18} | {len(c01):>18} | {len(c00)+len(c01):>4}")
    a(f"    body walks  > 0    | {len(c10):>18} | {len(c11):>18} | {len(c10)+len(c11):>4}")
    a("    -------------------+--------------------+--------------------+------")
    a(f"                       | {len(c00)+len(c10):>18} | {len(c01)+len(c11):>18} | {len(resolved):>4}")
    a("")
    a("Cell (body 0, rows >0) — the P4 defect cell:")
    for r in c01:
        a(f"    {r['where']}/{r['name']}: rows={r['reg_rows']} status={r['reg_status']}")
    a("Cell (body 0, rows 0) — legitimate walk-0 / no-work registers:")
    for r in c00:
        a(f"    {r['where']}/{r['name']}: status={r['reg_status']} fold_tables={r['reg_fold_tables']}")
    a("Cell (body >0, rows 0) — walks recorded, register carries no fold rows:")
    for r in c10:
        a(f"    {r['where']}/{r['name']}: body_walks={r['body_walks']} "
          f"max_walk={r['max_walk']} status={r['reg_status']} fold_tables={r['reg_fold_tables']}")
    a("")
    a("FALSE-POSITIVE ADJUDICATION for the conjunction (body==0 AND rows>0)")
    a("⛔ MECHANICAL RULE, stated before it is applied: a flag is a FALSE POSITIVE")
    a("   when the plan BODY textually carries per-lens walk lines — i.e. at least one")
    a("   line whose SHAPE is a lens line (`- <one of the five lenses>: ...`). Such a")
    a("   body holds the record a reader would read; only cycle_check's GRAMMAR misses")
    a("   it. The rule is a text probe, not a judgement call.")
    a("")
    LENS_SHAPE = re.compile(
        r"^\s*-\s*\*{0,2}(Weak spots|Destruction|Vulnerabilities|"
        r"Integration(?:-record)?|ACID)\*{0,2}\s*:", re.IGNORECASE | re.MULTILINE)
    fp, tp = [], []
    for r in c01:
        blocks = extract_dc_blocks(r["text"])
        blk = blocks[0] if blocks else ""
        shaped = LENS_SHAPE.findall(blk)
        wl = re.search(r"^\*\*Walks:\*\*.*$", blk, re.MULTILINE)
        r["lens_shaped_lines"] = len(shaped)
        r["walks_header"] = wl.group(0).strip()[:110] if wl else "<none>"
        (fp if shaped else tp).append(r)
    for label, grp in (("FALSE POSITIVE (body carries lens-shaped lines)", fp),
                       ("TRUE POSITIVE (body carries no lens-shaped line)", tp)):
        a(f"  {label} — {len(grp)}:")
        for r in grp:
            a(f"    {r['where']}/{r['name']}")
            a(f"        lens-shaped body lines : {r['lens_shaped_lines']}")
            a(f"        body **Walks:** line   : {r['walks_header']}")
            a(f"        register rows          : {r['reg_rows']}")
            a(f"        cycle_check verdict NOW: {r.get('verdict')}")
            a(f"        has_lens_lines={r['parsed']['has_lens_lines']} "
              f"has_any_parsed={r['parsed']['has_any_parsed']} "
              f"has_unparseable={r['parsed']['has_unparseable']}")
        a("")
    a(f"  FALSE-POSITIVE COUNT: {len(fp)} of {len(c01)} flagged"
      f" ({(100.0*len(fp)/len(c01)) if c01 else 0:.0f}%)")
    a(f"  TRUE-POSITIVE COUNT : {len(tp)} of {len(c01)}")
    a("")
    a("  ⚠️ MARGINAL SIGNAL. Of the flagged plans, those already emitting a non-")
    a("     silent verdict today gain NOTHING from a new check:")
    for r in c01:
        v = str(r.get("verdict"))
        a(f"    {r['name']:<44} verdict={v:<24}"
          f" {'already emits' if v.startswith('ESCALATE') else 'SILENT TODAY'}")
    silent = [r for r in c01 if not str(r.get("verdict")).startswith("ESCALATE")]
    a(f"  Conjunction check's NEW signal: {len(silent)} plan(s)"
      f" — {', '.join(r['name'] for r in silent) or 'none'}")
    a("")
    a("Comparison arm — a body-emptiness-only check (P3 rule) over the same grid:")
    a(f"    flags {len(c00) + len(c01)} resolvable plans"
      f" + {len(p3_unres)} unresolvable-ref plan(s) = {len(p3)} total")
    a(f"    of which the (body 0, rows 0) cell — {len(c00)} plan(s) — has no register")
    a("    evidence of a missed record at all.")
    a("")

    # ------------------------------------------------------------------
    a("=" * 78)
    a("## SECTION 4 — Q3: capability x timing, reported SEPARATELY")
    a("=" * 78)
    a("")
    pl_src = (BELLOWS_ROOT / "scripts" / "plan_lint.py").read_text(encoding="utf-8")
    a("CAPABILITY (measured from source — token counts, not recall):")
    for label, s in (("cycle_check.py", src), ("plan_lint.py", pl_src)):
        a(f"  {label}")
        for tok in ("walk_register_ref", "Walk register", "walk_register_lint",
                    "validate_file", "extract_tables", "_find_git_root",
                    "resolve_governance_root", "check_assert_2"):
            a(f"      {tok:<26} occurrences: {s.count(tok)}")
    a("")
    a("TIMING (measured — every call site of each tool in the live repo,")
    a("         excluding the tool's own file, tests/, and knowledge/ prose):")
    SKIP_DIRS = {".git", "__pycache__", "knowledge", "tests", "verdicts",
                 "receipts", "logs", ".venv", "node_modules"}
    tool_names = ("cycle_check", "plan_lint", "walk_register_lint")
    sites = {t: [] for t in tool_names}
    for dirpath, dirnames, filenames in os.walk(BELLOWS_ROOT):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for fn in filenames:
            if not fn.endswith((".py", ".sh", ".md", ".json")):
                continue
            fp = Path(dirpath) / fn
            if fp.name in ("cycle_check.py", "plan_lint.py",
                           "walk_register_lint.py", Path(__file__).name):
                continue
            try:
                txt = fp.read_text(encoding="utf-8")
            except Exception:
                continue
            for i, ln in enumerate(txt.splitlines(), 1):
                for t in tool_names:
                    if t in ln:
                        sites[t].append((str(fp.relative_to(BELLOWS_ROOT)), i, ln.strip()[:110]))
    # EXECUTING invokers only: a line that imports the module, or names its .py
    # file as a subprocess argv element. Everything else is prose or a census.
    EXEC_RE = {t: re.compile(rf"(^|\W)(import\s+{t}\b|from\s+{t}\s+import"
                             rf"|\"{t}\.py\"|'{t}\.py')") for t in tool_names}
    a("  EXECUTING INVOKERS (import, or the .py named in an argv) — the timing answer:")
    a(f"  {'tool':<20} {'invoker':<28} {'line':>5}  form")
    a("  " + "-" * 74)
    for t in tool_names:
        ex = [(rel, i, ln) for rel, i, ln in sites[t] if EXEC_RE[t].search(ln)]
        if not ex:
            a(f"  {t:<20} {'NONE':<28} {'-':>5}  never invoked in the live repo")
        for rel, i, ln in ex:
            form = "import" if "import" in ln else "subprocess"
            a(f"  {t:<20} {rel:<28} {i:>5}  {form}: {ln[:60]}")
    a("")
    a("  (Full reference dump — prose, censuses and docs included — follows so the")
    a("   filter above can be audited against it.)")
    a("")
    for t in tool_names:
        a(f"  {t}: {len(sites[t])} call/reference site(s) outside its own file")
        for rel, i, ln in sites[t]:
            a(f"      {rel}:{i}  {ln}")
        if not sites[t]:
            a("      NONE — nothing in the live repo invokes it.")
        a("")

    # ------------------------------------------------------------------
    a("=" * 78)
    a("## SECTION 5 — Q4: noise cost per candidate")
    a("=" * 78)
    a("⛔ Pricing only. No candidate is recommended.")
    a("")
    cands = []

    def add(key, desc, hits):
        cands.append((key, desc, hits))

    add("A", "body walk_data empty  (P3 rule — body-only, no register read)", p3)
    add("B", "body empty AND resolvable register carries fold rows (P4 conjunction)", p4)
    add("C", "register ref UNRESOLVABLE, at any walk count (P6 rule)", p6)
    # D: per-walk coverage — a walk in the body with no matching register mention
    d_hits = []
    for r in resolved:
        if r["body_walks"] == 0:
            continue
        try:
            rt = r["resolved"].read_text(encoding="utf-8")
        except Exception:
            continue
        missing = [wn for wn in sorted(r["walk_data"])
                   if wn > 0 and not re.search(rf"\b[Ww]alk\s+{wn}\b|\bw{wn}\b", rt)]
        if missing:
            d_hits.append((r, missing))
    add("D", "a body walk N with no 'walk N' mention in the register (coverage rule)",
        [h[0] for h in d_hits])
    # E: register carries rows for walks the body never declares
    e_hits = []
    for r in resolved:
        try:
            rt = r["resolved"].read_text(encoding="utf-8")
        except Exception:
            continue
        reg_walks = set(int(m) for m in re.findall(r"\bw(\d+)\b", rt))
        reg_walks |= set(int(m) for m in re.findall(r"\b[Ww]alk\s+(\d+)\b", rt))
        extra = sorted(w for w in reg_walks if w > 0 and w not in r["walk_data"])
        if extra and (r["reg_rows"] or 0) > 0:
            e_hits.append((r, extra))
    add("E", "register mentions a walk N the BODY does not carry (inverse coverage)",
        [h[0] for h in e_hits])

    def marginal(hits):
        return [h for h in hits if not str(h.get("verdict", "")).startswith("ESCALATE")]

    a("⛔ TWO counts per candidate, and they are NOT the same number:")
    a("   RAW      = plans the rule matches.")
    a("   MARGINAL = plans the rule matches that today return CONTINUE or BAR_MET —")
    a("              the only plans where a new check adds signal a reader does not")
    a("              already get. A plan already returning ESCALATE gains nothing.")
    a("")
    a(f"{'cand':<5} {'RAW':>6} {'MARGINAL':>9}  rule")
    a("-" * 78)
    for key, desc, hits in cands:
        a(f"{key:<5} {len(hits):>6} {len(marginal(hits)):>9}  {desc}")
    a("")
    for key, desc, hits in cands:
        a(f"[{key}] {desc} — {len(hits)} plan(s):")
        for r in hits:
            extra = ""
            if key == "D":
                extra = f"  missing_walks={dict(d_hits)[r] if False else [m for rr, m in d_hits if rr is r][0]}"
            if key == "E":
                extra = f"  register_only_walks={[m for rr, m in e_hits if rr is r][0]}"
            a(f"      {r['where']}/{r['name']}{extra}")
        a("")

    a("Baseline for habituation (thread 117) — denominator is the surveyed")
    a(f"population of {p1} ref-declaring plans:")
    for key, desc, hits in cands:
        m = marginal(hits)
        a(f"      candidate {key}: RAW {len(hits)}/{p1} = {100.0*len(hits)/p1:.1f}%"
          f"   |   MARGINAL {len(m)}/{p1} = {100.0*len(m)/p1:.1f}%")
    a("")
    a("⚠️ CANDIDATE E CARRIES A KNOWN FALSE-MATCH CLASS, named here so its count is")
    a("   not read as clean. E (and candidate D, and cycle_check._compute_coherence")
    a("   itself) locate a walk in a register with the regex")
    a("       \\b[Ww]alk\\s+N\\b | \\bwN\\b")
    a("   which matches any token of the form wNN. Evidence — the matched text for")
    a("   every register-only walk >= 20 reported above:")
    shown = 0
    for r, extra in e_hits:
        big = [w for w in extra if w >= 20]
        if not big:
            continue
        try:
            rt = r["resolved"].read_text(encoding="utf-8")
        except Exception:
            continue
        for w in big:
            for m in re.finditer(rf"\b[Ww]alk\s+{w}\b|\bw{w}\b", rt):
                lo = max(0, m.start() - 45)
                a(f"      {r['name']} w{w}: ...{rt[lo:m.end()+30].strip()[:100]}...")
                shown += 1
                break
        if shown > 14:
            break
    only_hi = [r for r, extra in e_hits if extra and all(w >= 20 for w in extra)]
    some_hi = [r for r, extra in e_hits
               if any(w >= 20 for w in extra) and not all(w >= 20 for w in extra)]
    clean = [r for r, extra in e_hits if all(w < 20 for w in extra)]
    a(f"   E hits driven ONLY by a walk number >= 20 (wholly artifact): {len(only_hi)}")
    a(f"   E hits mixing a >=20 token with a real walk number         : {len(some_hi)}")
    a(f"   E hits with no >=20 token at all (uncontaminated)          : {len(clean)}")
    a(f"   total {len(only_hi)}+{len(some_hi)}+{len(clean)} = {len(e_hits)}")
    a("   No cycle in this corpus ran 20 walks (max body walk measured:"
      f" {max([r['max_walk'] for r in recs if r['max_walk'] is not None] or [0])}).")
    a("   Treat E's RAW count as an upper bound contaminated by this class. Its")
    a(f"   uncontaminated floor is {len(clean)}.")
    a("")

    # ------------------------------------------------------------------
    a("=" * 78)
    a("## SECTION 6 — full per-plan table (evidence for every count above)")
    a("=" * 78)
    a(f"{'where':<7} {'body':>4} {'maxw':>4} {'rows':>5} {'res':<4} {'reg_status':<16} {'verdict':<28} name")
    for r in sorted(recs, key=lambda x: (x["where"], x["name"])):
        a(f"{r['where']:<7} {r['body_walks']:>4} {str(r['max_walk']):>4} "
          f"{str(r['reg_rows']):>5} {'Y' if r['resolved'] else 'N':<4} "
          f"{str(r['reg_status'])[:16]:<16} {str(r.get('verdict'))[:28]:<28} {r['name']}")
    a("")
    a("END OF RAW OUTPUT")

    print("\n".join(out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
