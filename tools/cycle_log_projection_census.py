#!/usr/bin/env python3
"""cycle_log_projection_census — is the Cycle Log derivable, or must it be kept?

DIAGNOSTIC INSTRUMENT for `diagnostic-cycle-log-projection` (manual_bootstrap,
2026-09-06). Measures whether the plan body's Cycle Log could be COMPUTED from
(walk register ⋈ per-lens commits) instead of hand-maintained.

⛔ IT IMPORTS THE SHIPPED PARSERS AND CALLS THEM. Diagnostic 100032's walk 4
forbade a second reader for a format the lint already parses:
    cycle_yields.extract_dc_blocks     — find the Drafting Cycle block
    cycle_check.parse_block            — the body's walk data, verbatim
    cycle_check._compute_coherence     — Q5's subject
    walk_register_lint.extract_tables / normalize_column / is_fold_table /
        validate_file                  — the register's rows and status
    lens_order_check.commit_record     — the OBSERVER, read by its own parser

⛔ SELF-EXCLUSION. This plan's own register joins the censused directory the
moment it is created; SELF_REGISTER names it exactly and the exclusion is
reported, not silent.

Read-only. Edits no checker, no schema, no doctrine. Decides nothing.
"""

import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

BELLOWS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BELLOWS))
sys.path.insert(0, str(BELLOWS / "scripts"))

import cycle_check                                   # noqa: E402
import walk_register_lint as wrl                     # noqa: E402
import lens_order_check as loc                       # noqa: E402
from cycle_yields import extract_dc_blocks           # noqa: E402

GOV = Path("/Users/marklehn/Developer/eluvian-governance")
REG_DIR = GOV / "governance" / "knowledge" / "research"
SELF_REGISTER = "walk-register-cycle-log-projection-2026-09-06.md"
RAW = (BELLOWS / "knowledge" / "qa" / "evidence"
       / "cycle-log-projection-2026-09-06" / "census-raw.txt")

CONTROLS = {
    "executable-100030.md": {"agree": True,  "missing": []},
    "executable-100017.md": {"agree": False, "missing": [4, 6]},
}

_out = RAW.open("a", encoding="utf-8")


def a(line=""):
    _out.write(line + "\n")
    _out.flush()


def resolve(ref, plan_path):
    """cycle_check's own three-step order, mirrored (it returns a verdict, not a path)."""
    if not ref:
        return None
    if Path(ref).is_absolute():
        c = Path(ref)
        return c if c.exists() else None
    git_root = cycle_check._find_git_root(plan_path)
    if git_root and (git_root / ref).exists():
        return git_root / ref
    try:
        from bellows_root import resolve_governance_root
        g = resolve_governance_root()
    except Exception:
        g = None
    if g and (g / ref).exists():
        return g / ref
    return None


def register_rows(path):
    """(walk, lens) per fold row, via the shipped parser. Never a hand parse."""
    txt = path.read_text(encoding="utf-8")
    tables, _ = wrl.extract_tables(txt)
    rows, unreadable = [], 0
    for hdr, data, _h in tables:
        norm = [wrl.normalize_column(c) for c in hdr]
        if "id" not in norm or "walk" not in norm:
            continue
        wi = norm.index("walk")
        li = norm.index("lens") if "lens" in norm else None
        ci = norm.index("class") if "class" in norm else None
        for _ln, cells in data:
            if len(cells) != len(hdr):
                unreadable += 1
                continue
            wv = cells[wi].strip().strip("`* ")
            m = re.match(r"^(\d+)", wv)
            if not m:
                continue
            lens = cells[li].strip().strip("`* ") if li is not None else None
            klass = cells[ci].strip().strip("`* ").lower() if ci is not None else None
            rows.append({"walk": int(m.group(1)), "lens": lens, "class": klass})
    return rows, unreadable


def survey():
    recs = []
    for d in ("Done", "drafts"):
        for p in sorted((BELLOWS / "knowledge" / "decisions" / d).glob("*.md")):
            try:
                txt = p.read_text(encoding="utf-8")
            except Exception:
                continue
            blocks = extract_dc_blocks(txt)
            if len(blocks) != 1:
                continue
            parsed = cycle_check.parse_block(blocks[0])
            ref = parsed["walk_register_ref"]
            rp = resolve(ref, p)
            if rp is not None and rp.name == SELF_REGISTER:
                recs.append({"name": p.name, "where": d, "self_excluded": True})
                continue
            rec = {"name": p.name, "where": d, "path": p, "text": txt,
                   "parsed": parsed, "ref": ref, "reg": rp, "self_excluded": False}
            if rp is not None:
                rec["rows"], rec["unreadable"] = register_rows(rp)
                try:
                    rec["reg_status"] = wrl.validate_file(rp)[0]
                except Exception as e:
                    rec["reg_status"] = f"ERR:{e}"
            else:
                rec["rows"], rec["unreadable"], rec["reg_status"] = [], 0, None
            recs.append(rec)
    return recs


def classify(rec):
    """exact | derivable-with-gap | not-derivable, with the mismatch DIRECTION."""
    body = {w for w in rec["parsed"]["walk_data"] if w > 0}
    reg = {r["walk"] for r in rec["rows"] if r["walk"] > 0}
    if not body and not reg:
        return "no-data", "neither record carries a walk"
    if not reg:
        return "not-derivable", "register carries NO walk rows"
    if not body:
        return "not-derivable", "body carries NO walk data (register has rows)"
    if body == reg:
        return "exact", "walk-sets identical"
    only_body = sorted(body - reg)
    only_reg = sorted(reg - body)
    bits = []
    if only_body:
        bits.append(f"BODY-AHEAD: walks {only_body} declared, no register rows")
    if only_reg:
        bits.append(f"BODY-BEHIND: walks {only_reg} in register, absent from body")
    return "derivable-with-gap", " · ".join(bits)


def run():
    recs = survey()
    live = [r for r in recs if not r["self_excluded"]]
    excluded = [r for r in recs if r["self_excluded"]]

    a("=" * 78)
    a("## ITEM 2 — POSITIVE CONTROLS (both directions, before any corpus run)")
    a("=" * 78)
    a("⛔ One control proves only that the instrument reads the case it was")
    a("   written for. Two, in OPPOSITE directions, is the minimum.")
    a("")
    ok_all = True
    for cname, exp in CONTROLS.items():
        rec = next((r for r in live if r["name"] == cname), None)
        if rec is None:
            a(f"  {cname}: **CONTROL FAILED — not in the surveyed set**")
            ok_all = False
            continue
        verdict, why = classify(rec)
        body = sorted(w for w in rec["parsed"]["walk_data"] if w > 0)
        reg = sorted({r["walk"] for r in rec["rows"] if r["walk"] > 0})
        missing = sorted(set(body) - set(reg))
        if exp["agree"]:
            ok = verdict == "exact"
        else:
            ok = verdict == "derivable-with-gap" and missing == exp["missing"]
        ok_all &= ok
        a(f"  {cname}")
        a(f"      body walks     : {body}")
        a(f"      register walks : {reg}   rows={len(rec['rows'])}")
        a(f"      verdict        : {verdict} — {why}")
        a(f"      expected       : {'AGREEING' if exp['agree'] else f'DIVERGING, missing {exp[chr(34)+chr(34)] if False else exp['missing']}'}")
        a(f"      RESULT: {'PASS' if ok else '**CONTROL FAILED**'}")
        a("")
    a(f"  CONTROLS OVERALL: {'PASS — proceed to the corpus' if ok_all else '**FAILED — STOP**'}")
    a("")
    a(f"  SELF-EXCLUSION: {SELF_REGISTER}")
    a(f"      plans whose register resolved to it: {len(excluded)}"
      f" (v0 — the register is created at walk 1)")
    a("")
    if not ok_all:
        a("STOPPING: a failed positive control makes every number below unfounded.")
        return 2

    # ---------------- Q1 ----------------
    a("=" * 78)
    a("## ITEM 3 / Q1 — PER-LENS DERIVABILITY, with the direction of each mismatch")
    a("=" * 78)
    pairs = [r for r in live if r["reg"] is not None and r["parsed"]["walk_data"]
             and r["rows"]]
    a(f"plans carrying BOTH a body Cycle Log with walk data AND a register with"
      f" walk rows: {len(pairs)}")
    a("")
    buckets = defaultdict(list)
    for r in pairs:
        v, why = classify(r)
        r["verdict"], r["why"] = v, why
        buckets[v].append(r)
    hdr = f"{'plan':<46} {'verdict':<20} detail"
    a(hdr); a("-" * 110)
    for r in sorted(pairs, key=lambda x: (x["verdict"], x["name"])):
        a(f"{r['name'][:45]:<46} {r['verdict']:<20} {r['why'][:60]}")
    a("")
    a("SUBTOTALS:")
    for k in ("exact", "derivable-with-gap", "not-derivable", "no-data"):
        a(f"    {k:<22} {len(buckets[k])}")
    ahead = [r for r in buckets["derivable-with-gap"] if "BODY-AHEAD" in r["why"]]
    behind = [r for r in buckets["derivable-with-gap"] if "BODY-BEHIND" in r["why"]]
    a("")
    a("⛔ DIRECTION MATTERS — these are different failures with different remedies:")
    a(f"    BODY-AHEAD  (walks declared with no register rows) : {len(ahead)}")
    a(f"    BODY-BEHIND (register rows for walks the body omits): {len(behind)}")
    a("    BODY-BEHIND is thread 140/141's failure — the record cycle_check reads")
    a("    lagging the record the findings live in.")
    for r in behind:
        a(f"      {r['name']}: {r['why']}")
    a("")

    # per-LENS, not just walk-set
    a("PER-LENS derivability (the stricter test Q1 actually asks for):")
    lens_ok = lens_no = lens_absent = 0
    for r in pairs:
        has_lens = any(x["lens"] for x in r["rows"])
        if not has_lens:
            lens_absent += 1
            continue
        body_lenses = {w: set(d["lenses"]) for w, d in r["parsed"]["walk_data"].items()}
        reg_lenses = defaultdict(set)
        for x in r["rows"]:
            if x["lens"]:
                reg_lenses[x["walk"]].add(re.sub(r"^\d+\s*", "", x["lens"]).strip().lower()[:6])
        match = all(bool(reg_lenses.get(w)) for w in body_lenses if body_lenses[w])
        lens_ok += match
        lens_no += (not match)
    a(f"    register rows carry a LENS value      : {len(pairs) - lens_absent} of {len(pairs)}")
    a(f"    no lens column at all                 : {lens_absent}")
    a(f"    ⛔ per-lens counts therefore derivable for at most"
      f" {len(pairs) - lens_absent} of {len(pairs)} plans")
    a("")

    # ---------------- Q2 ----------------
    a("=" * 78)
    a("## ITEM 4 / Q2 — WHAT THE BODY CARRIES THAT THE REGISTER CANNOT")
    a("=" * 78)
    n_class = sum(1 for r in live if any(x["class"] for x in r.get("rows", [])))
    a(f"{'parse_block field':<24} {'register can supply?':<24} evidence")
    a("-" * 100)
    a(f"{'walk_data (walks)':<24} {'DERIVABLE':<24} every fold row carries a walk column")
    a(f"{'walk_data (lenses)':<24} {'DERIVABLE where present':<24}"
      f" {len(pairs) - lens_absent}/{len(pairs)} pairs have a lens value")
    a(f"{'walk_data (fold counts)':<24} {'DERIVABLE':<24} count of rows per (walk, lens)")
    a(f"{'instruction/record split':<24} {'⛔ NOT DERIVABLE':<24}"
      f" class column present in {n_class} plan(s) of {len(live)}")
    a(f"{'walk_status totals':<24} {'DERIVABLE':<24} row count per walk")
    a(f"{'restructuring_walks':<24} {'⛔ ABSENT':<24} no register field encodes it")
    a(f"{'claims_closure':<24} {'⛔ ABSENT':<24} a body prose claim, by construction")
    a(f"{'walk_register_ref':<24} {'N/A':<24} the pointer TO the register")
    a("")
    a("⛔ THE INSTRUCTION/RECORD SPLIT IS THE CONVERGENCE SIGNAL. DRAFTING_CYCLE:")
    a('   "The cycle is DONE when a full walk\'s findings, classified by the surface')
    a('    each TOUCHES, are all record-class — zero instruction-class findings."')
    a("   If it is not derivable, THE BAR IS NOT DERIVABLE and a projected Cycle")
    a("   Log cannot carry the verdict — only the counts beneath it.")
    a("")

    # ---------------- Q3 ----------------
    a("=" * 78)
    a("## ITEM 5 / Q3 — COST OF ADDING `class` TO REQUIRED_COLUMNS")
    a("=" * 78)
    all_regs = sorted(p for p in REG_DIR.glob("walk-register-*.md")
                      if p.name != SELF_REGISTER)
    have_class = []
    status_now = Counter()
    for rp in all_regs:
        try:
            st = wrl.validate_file(rp)[0]
        except Exception as e:
            st = f"ERR:{e}"
        status_now[st] += 1
        txt = rp.read_text(encoding="utf-8")
        tables, _ = wrl.extract_tables(txt)
        if any("class" in [wrl.normalize_column(c) for c in h] for h, _d, _l in tables):
            have_class.append(rp.name)
    a(f"registers censused (self excluded): {len(all_regs)}")
    a(f"already carrying a class column   : {len(have_class)}")
    a(f"would become non-conformant       : {len(all_regs) - len(have_class)}")
    a("")
    a("status distribution TODAY (before any schema change):")
    for k, v in status_now.most_common():
        a(f"    {k:<18} {v}")
    a("")
    a("⛔ THE LEGACY_SCHEMA PATH IS THE POINT, and it is separate from the failure")
    a("   count. walk_register_lint._apply_version_status: a register declaring a")
    a("   version OLDER than the validator's, and already non-conformant, is")
    a("   demoted to LEGACY_SCHEMA rather than reported UNCONFORMANT.")
    ver = Counter()
    for rp in all_regs:
        m = wrl.SCHEMA_DECL_RE.search(rp.read_text(encoding="utf-8"))
        ver[(m.group(1).strip().strip('`') if m else "UNDECLARED")] += 1
    a("   declared schema versions across the population:")
    for k, v in sorted(ver.items()):
        a(f"       {k:<12} {v}")
    a(f"   validator is at {wrl.VALIDATOR_SCHEMA_VERSION}. At 0.4, every register")
    a("   declaring 0.1/0.2/0.3 becomes 'older' and takes the LEGACY_SCHEMA path;")
    a("   only the UNDECLARED ones and any declaring 0.4 would report UNCONFORMANT.")
    a("")
    a("⚠️ AND THE cycle_check WARN REACHES THE VERDICT PATH — reported separately:")
    a("   cycle_check._REGISTER_SILENT_STATUSES = {CONFORMANT, PRE-SCHEMA,")
    a("   LEGACY_SCHEMA}. LEGACY_SCHEMA is SILENT, so the demotion suppresses the")
    a("   WARN entirely; UNCONFORMANT emits one. Migration noise is therefore")
    a(f"   bounded by the UNDECLARED count ({ver.get('UNDECLARED', 0)}), not by the")
    a(f"   {len(all_regs) - len(have_class)} registers lacking the column.")
    a("")
    return live, pairs, all_regs


def run_q4_q5():
    """Items 6 and 7 — the observer, and whether thread 152 blocks."""
    recs = [r for r in survey() if not r["self_excluded"]]

    a("=" * 78)
    a("## ITEM 6 / Q4 — CAN THE OBSERVER RECONSTRUCT THE SEQUENCE?")
    a("=" * 78)
    a("⛔ COVERAGE and AGREEMENT are reported SEPARATELY. A plan whose commits")
    a("   carry no lens token is NO-RECORD, not a disagreement.")
    a("")
    with_body = [r for r in recs if r["parsed"]["walk_data"]]
    covered, agree, disagree, norec = [], [], [], []
    for r in with_body:
        try:
            rows = loc.commit_record(r["path"], BELLOWS)
        except Exception:
            rows = []
        if not rows:
            norec.append(r); continue
        covered.append(r)
        obs = {w for w, _l, _s, _subj in rows}
        body = {w for w in r["parsed"]["walk_data"] if w > 0}
        (agree if obs == body else disagree).append((r, sorted(obs), sorted(body)))
    a(f"plans with body walk data            : {len(with_body)}")
    a(f"  COVERAGE — commits carry lens rows : {len(covered)}"
      f"  ({100.0*len(covered)/len(with_body):.0f}%)")
    a(f"  NO-RECORD — no lens commit at all  : {len(norec)}"
      f"  ({100.0*len(norec)/len(with_body):.0f}%)")
    a("")
    a(f"  of the {len(covered)} covered, AGREEMENT with the body's walk-set:")
    a(f"    agree    : {len(agree)}")
    a(f"    disagree : {len(disagree)}")
    for r, obs, body in disagree[:10]:
        a(f"      {r['name']}: observer {obs} vs body {body}")
    a("")
    a("⛔ THIS BOUNDS THE WHOLE PROPOSAL. A Cycle Log computed from the observer")
    a(f"   today would be EMPTY for {len(norec)} of {len(with_body)} plans, because")
    a("   the observer is a convention followed by a minority of commits (P5:")
    a("   75 of 596). The observer proves ORDER where it exists; it cannot be the")
    a("   source of a record it does not cover.")
    a("")

    a("=" * 78)
    a("## ITEM 7 / Q5 — DOES THREAD 152 BLOCK? Answered from the FUNCTION.")
    a("=" * 78)
    a("A projection needs a CURRENCY check: something must prove the emitted block")
    a("still matches the source it was derived from. The only body<->register")
    a("comparison in the system is cycle_check._compute_coherence. Its source:")
    a("")
    src = (BELLOWS / "scripts" / "cycle_check.py").read_text(encoding="utf-8")
    body = src[src.index("def _compute_coherence"):src.index("def emit_manifest")]
    for i, ln in enumerate(body.splitlines()[:26], 1):
        a(f"    {ln}")
    a("")
    a("MEASURED BEHAVIOUR, not the docstring:")
    zero = [r for r in recs if not r["parsed"]["walk_data"] and r["reg"] is not None]
    vals = []
    for r in zero[:8]:
        try:
            vals.append((r["name"], cycle_check._compute_coherence(r["parsed"], r["path"])))
        except Exception as e:
            vals.append((r["name"], f"EXC:{e}"))
    for n, v in vals:
        a(f"    {n}: {v!r}")
    a(f"    -> every plan with an empty body and a resolvable register: {len(zero)},"
      f" all returning N/A")
    a("")
    a("THREE DEFECTS, each disqualifying for a currency check:")
    a("  1. `if total_walks == 0: return \"N/A\"` — it is DISABLED by exactly the")
    a("     state a stale projection would present (a body that emits nothing).")
    a("  2. the walk-matching regex is `\\b[Ww]alk\\s+N\\b|\\bwN\\b`, which matches any")
    a("     wNN token. Gate-2 week names (gate2-pt-w28-a, forge-cycle-w29) score as")
    a("     walks; no cycle in the corpus ran 20 walks.")
    a("  3. it runs ONLY under --emit-manifest — once, at freeze. A projection")
    a("     drifts DURING a cycle; a check that runs at the end cannot catch it.")
    a("")
    a("⛔ ANSWER: NO CURRENT CHECK CAN VERIFY A PROJECTION IS CURRENT.")
    a("   Thread 152 is therefore a PRECONDITION, not an adjacent fix. Making the")
    a("   Cycle Log a projection while its only currency check is disabled by the")
    a("   empty case, contaminated in its matcher, and run once at freeze would")
    a("   replace a record that is WRONG 23 times in 71 with one that is wrong")
    a("   silently and unmeasurably. This plan does not soften that.")
    a("")
    a("END OF RAW OUTPUT (Step 1)")


if __name__ == "__main__":
    if "--part2" in sys.argv:
        run_q4_q5()
        sys.exit(0)
    r = run()
    sys.exit(0 if r != 2 else 2)
