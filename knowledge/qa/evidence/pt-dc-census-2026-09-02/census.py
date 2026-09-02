#!/usr/bin/env python3
"""census.py — the PT/DC enforcement census instrument (diagnostic pt-dc-census-2026-09-02).

Enumerates every governance UNIT from the documents themselves and joins each to
(a) the CHECKERS that CITE it by id (the bellows code that gates, lints or checks — a citation is the mechanical floor: a check can enforce a rule without naming it, and naming is not enforcing; the diagnostic's reading settles each unit) and
(b) the CORPUS entries that cite it (LESSONS.md), by grep over the files —
never from memory. Read-only. Standard library only.

Units (id, home, kind, title, line):
  PT rule      — '### N. title' inside '## Orchestration Plan Rules'
  PT checklist — '### N. title' inside '## Plan Authoring Checklist'
  PT wrap step — 'N. **title**' inside '### Session Wrap' (the numbered steps; the heading measured 2026-09-02)
  DC trigger   — '- **T-N — title**' in DRAFTING_CYCLE §1
  DC lens sub-question — '(L.n)' tokens in DRAFTING_CYCLE §2.1–2.5
  DC 2.7 bullet — each '- ' bullet under '### 2.7' (identified by its first 60 chars)

Enforcer citation forms (measured 2026-09-02 across gates.py, depositor.py,
scripts/*.py, hooks/eluvian/*.py, tools/*.py): 'Rule N', 'rule_N', '§N.N', '§N',
'DRAFTING_CYCLE.md'. A PT rule N is ENFORCED-BY a file when that file contains
'Rule N' (word-bounded) or 'rule_N'; a DC sub-question (L.n) when a file contains
'§L.n' or '(L.n)'; a DC section §N when '§N' appears (section-level, coarse —
reported separately as 'section-cited'). A checklist item shares the 'Rule N'
namespace ambiguously (PT has both Rule 34 and item 34) — checklist citations are
counted only where the file says 'Checklist' within 40 chars of the number.

Usage: census.py <PT> <DC> <LESSONS> <code-dir>... --out <dir>
Writes <out>/units.csv and <out>/summary.txt. Exit 0 on success, 2 on any
population that parses to ZERO units (a census over nothing is not a result).
"""
import argparse, csv, glob, os, re, sys

def read(p): return open(p, encoding="utf-8").read()

def section(text, heading, next_heading_re=r"^## "):
    # the heading as a whole LINE, and the LAST such line — '### Session Wrap' also
    # occurs at line 26 of PLANNER_TEMPLATE.md (a summary), which text.find() hit
    # first and returned an 8-line body with zero steps (measured 2026-09-02).
    ms = list(re.finditer(r"^" + re.escape(heading) + r"(?:\s.*)?$", text, re.M))  # a heading may carry a title after its number ("### 2.7 Cross-cutting rules …")
    if not ms: return "", 0
    i = ms[-1].start()
    m = re.search(next_heading_re, text[i+len(heading):], re.M)
    j = i + len(heading) + (m.start() if m else len(text))
    return text[i:j], text[:i].count("\n") + 1

def pt_numbered(text, heading, kind, home):
    body, base = section(text, heading)
    units = []
    for m in re.finditer(r"^### (\d+)\. (.+)$", body, re.M):
        units.append(dict(id=f"{kind}-{m.group(1)}", home=home, kind=kind, num=m.group(1),
                          title=m.group(2).strip()[:110], line=base + body[:m.start()].count("\n")))
    return units

def pt_wrap_steps(text):
    body, base = section(text, '### Session Wrap', next_heading_re=r"^##+ ")
    units = []
    for m in re.finditer(r"^(\d+)\. \*\*([^*]+)\*\*", body, re.M):
        units.append(dict(id=f"wrap-{m.group(1)}", home="PLANNER_TEMPLATE", kind="wrap-step", num=m.group(1),
                          title=m.group(2).strip()[:110], line=base + body[:m.start()].count("\n")))
    return units

def dc_units(text):
    units = []
    for m in re.finditer(r"^- \*\*(T-\d+) — ([^.*]+)", text, re.M):
        units.append(dict(id=f"dc-{m.group(1)}", home="DRAFTING_CYCLE", kind="trigger", num=m.group(1),
                          title=m.group(2).strip()[:110], line=text[:m.start()].count("\n")+1))
    seen = set()
    for m in re.finditer(r"\((\d\.\d+)\)", text):
        q = m.group(1)
        if q in seen or not q[0] in "12345": continue
        seen.add(q)
        units.append(dict(id=f"dc-q{q}", home="DRAFTING_CYCLE", kind="lens-subquestion", num=q,
                          title=text[m.end():m.end()+90].strip().split("\n")[0][:90], line=text[:m.start()].count("\n")+1))
    body, base = section(text, "### 2.7", next_heading_re=r"^### 2\.8")
    n = 0
    for m in re.finditer(r"^- (.+)$", body, re.M):
        n += 1
        units.append(dict(id=f"dc-2.7-b{n}", home="DRAFTING_CYCLE", kind="2.7-bullet", num=str(n),
                          title=re.sub(r"[*⚠️]", "", m.group(1))[:110], line=base + body[:m.start()].count("\n")))
    return units

def code_files(dirs):
    out = []
    for d in dirs:
        for pat in ("*.py", "*/*.py"):
            out += [p for p in glob.glob(os.path.join(d, pat)) if "/tests/" not in p and "/.venv/" not in p]
    return sorted(set(out))

def enforcers_for(unit, code):
    hits = []
    k, num = unit["kind"], unit["num"]
    for path, text in code:
        if k == "rule":
            if re.search(rf"\bRule {num}\b", text) or re.search(rf"\brule_{num}\b", text):
                hits.append(os.path.relpath(path))
        elif k == "checklist":
            if re.search(rf"Checklist.{{0,40}}\b{num}\b|\b{num}\b.{{0,40}}Checklist", text):
                hits.append(os.path.relpath(path))
        elif k == "lens-subquestion":
            if re.search(rf"§ ?{re.escape(num)}\b|\({re.escape(num)}\)", text):
                hits.append(os.path.relpath(path))
        elif k == "trigger":
            if re.search(rf"\b{re.escape(num)}\b", text):
                hits.append(os.path.relpath(path))
        elif k == "wrap-step":
            if re.search(rf"\[(\d[a-z]?)/", text) and re.search(rf"\[{num}[a-z]?/", text):
                hits.append(os.path.relpath(path))
        elif k == "2.7-bullet":
            pass  # bullets have no id a checker can cite; section-level '§2.7' is counted below
    return hits

def corpus_cites(unit, lessons):
    k, num = unit["kind"], unit["num"]
    if k == "rule": pat = rf"\bRule {num}\b"
    elif k == "lens-subquestion": pat = rf"§ ?{re.escape(num)}\b|\({re.escape(num)}\)"
    elif k == "trigger": pat = rf"\b{re.escape(num)}\b"
    elif k == "checklist": pat = rf"Checklist.{{0,40}}\b{num}\b|\b{num}\b.{{0,40}}Checklist|item {num}\b"
    elif k == "wrap-step": pat = rf"step {num}\b"
    else: return 0
    return len(re.findall(pat, lessons))

def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("pt"); ap.add_argument("dc"); ap.add_argument("lessons"); ap.add_argument("code", nargs="+"); ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    pt, dc, lessons = read(a.pt), read(a.dc), read(a.lessons)
    units = (pt_numbered(pt, "## Orchestration Plan Rules", "rule", "PLANNER_TEMPLATE")
             + pt_numbered(pt, "## Plan Authoring Checklist", "checklist", "PLANNER_TEMPLATE")
             + pt_wrap_steps(pt) + dc_units(dc))
    kinds = {}
    for u in units: kinds[u["kind"]] = kinds.get(u["kind"], 0) + 1
    if not units or any(kinds.get(k, 0) == 0 for k in ("rule", "checklist", "wrap-step", "trigger", "lens-subquestion", "2.7-bullet")):
        print(f"ERROR: a population parsed to zero units: {kinds} — EXIT 2, not a result"); return 2
    code = [(p, read(p)) for p in code_files(a.code)]
    sec27 = sorted(os.path.relpath(p) for p, t in code if "§2.7" in t or "2.7" in t and "DRAFTING_CYCLE" in t)
    os.makedirs(a.out, exist_ok=True)
    rows = []
    for u in units:
        enf = enforcers_for(u, code)
        enf = sorted(set(enf))
        section_cited = ";".join(sec27) if u["kind"] == "2.7-bullet" else ""
        rows.append({**u, "enforcers": ";".join(enf), "n_enforcers": len(enf), "section_cited": section_cited, "corpus_cites": corpus_cites(u, lessons)})
    with open(os.path.join(a.out, "units.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
    lines = [f"units: {len(rows)}  by kind: {kinds}", f"code files scanned: {len(code)}"]
    for k in kinds:
        ks = [r for r in rows if r["kind"] == k]
        enf = sum(1 for r in ks if r["n_enforcers"])
        cited = sum(1 for r in ks if r["corpus_cites"])
        sc = sum(1 for r in ks if r["section_cited"])
        lines.append(f"{k:18s} units {len(ks):3d}  cited-by-a-checker {enf:3d}  section-cited-only {sc:3d}  corpus-cited {cited:3d}  corpus-cited-and-uncited {sum(1 for r in ks if r['corpus_cites'] and not r['n_enforcers']):3d}")
    top = sorted((r for r in rows if not r["n_enforcers"]), key=lambda r: -r["corpus_cites"])[:15]
    lines.append("top UNCITED-by-any-checker units by corpus weight (citation is the mechanical floor; ENFORCEMENT is the reading the diagnostic owes):")
    for r in top: lines.append(f"  {r['id']:14s} cites {r['corpus_cites']:2d}  {r['title'][:70]}")
    open(os.path.join(a.out, "summary.txt"), "w").write("\n".join(lines) + "\n")
    print("\n".join(lines)); return 0

if __name__ == "__main__":
    sys.exit(main())
