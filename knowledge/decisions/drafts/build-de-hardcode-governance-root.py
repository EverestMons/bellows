#!/usr/bin/env python3
"""Builder — de-hardcode the shop machine's governance root from bellows code.

One shared resolver in bellows_root.py (pathlib-only, no bellows import):
  resolve_governance_root()  — where COMPANY.md / PLANNER_TEMPLATE.md /
                               RULE_20_SELF_CHECK_BLOCK.md live
  resolve_projects_parent()  — the directory holding the project checkouts
Then twelve anchored edits across ten files (nine code files + CLAUDE.md's seam sentence) replace every remaining
`/Users/marklehn/Developer/GitHub` literal (and the `/Developer/GitHub/`
re-rooting sentinel) with the resolver.

Usage: build-de-hardcode-governance-root.py <bellows-root-in> <bellows-root-out>
Copies the eight target files from <in> to <out>, applies every edit with a
count-1 anchor assert, asserts every post-condition on the output text, and
refuses to write into the live checkout (realpath + samefile + casefolded
prefix + out != in). Scratch-only; the plan's DEV step runs it <live> ->
<scratch>, then copies the eight outputs over the live files with cmp closure.
"""
import hashlib
import os
import sys

LIVE_ROOT = "/Users/marklehn/Developer/bellows"
TARGETS = [
    "bellows_root.py", "gates.py", "verdict.py", "planner.py", "decisions.py",
    "bellows.py", "plan_claim.py", "scripts/plan_lint.py",
    "scripts/migrate_orphan_verdicts.py", "CLAUDE.md",
]


def _req(cond, msg):
    if not cond:
        raise SystemExit(f"REFUSED/FAILED: {msg}")


def apply(text, edits, label):
    for i, (anchor, replacement) in enumerate(edits, 1):
        n = text.count(anchor)
        _req(n == 1, f"{label} E{i}: anchor count {n} != 1: {anchor[:70]!r}")
        text = text.replace(anchor, replacement)
    return text


# ---------------------------------------------------------------------------
# bellows_root.py — the resolver (appended; the file has no trailing helpers)
R0_ANCHOR = (
    '    raise ValueError(\n'
    '        f"resolve_bellows_root: no bellows sentinel (config.json or bellows.py) "\n'
    '        f"found in any ancestor of {start}"\n'
    '    )\n'
)
R0_NEW = R0_ANCHOR + '''

GOVERNANCE_MARKER = "COMPANY.md"


def resolve_governance_root(_start=None, _env=None):
    """Return the governance root — the directory holding COMPANY.md,
    PLANNER_TEMPLATE.md, RULE_20_SELF_CHECK_BLOCK.md, LESSONS.md.

    Two layouts exist (2026-09-01) and a third may come:
      shop : <root>/{COMPANY.md, bellows/, lessons-forge/, ...}     — bellows UNDER the root
      mini : ~/Developer/{eluvian-governance/COMPANY.md, bellows/}  — bellows BESIDE the root

    Resolution order, first hit wins, every hit verified by the marker:
      1. $ELUVIAN_WRAP_ROOT (an override, never a requirement — the daemon's
         environment does not carry it; measured 2026-09-01 on the mini)
      2. an ancestor of the bellows root that holds the marker (shop shape)
      3. siblings of the bellows root: <parent>/eluvian-governance, <parent>
         (mini shape, and any layout where governance is a sibling checkout)
      4. ~/Developer/eluvian-governance, ~/Developer/GitHub (the two known
         homes, tried LAST and only by marker — never assumed)
    Raises ValueError when no candidate holds the marker: a loud failure beats
    a QA agent told to read a file that does not exist.

    `_start` / `_env` are for testing only.
    """
    import os
    env = _env if _env is not None else os.environ.get("ELUVIAN_WRAP_ROOT")
    if env:
        p = Path(env).expanduser()
        if (p / GOVERNANCE_MARKER).is_file():
            return p.resolve()
    try:
        broot = resolve_bellows_root(_start)
    except ValueError:
        broot = (_start or Path(__file__).resolve().parent).resolve()
    current = broot
    while True:
        if (current / GOVERNANCE_MARKER).is_file():
            return current
        parent = current.parent
        if parent == current:
            break
        current = parent
    for cand in (broot.parent / "eluvian-governance", broot.parent,
                 Path.home() / "Developer" / "eluvian-governance",
                 Path.home() / "Developer" / "GitHub"):
        if (cand / GOVERNANCE_MARKER).is_file():
            return cand.resolve()
    raise ValueError(
        f"resolve_governance_root: no {GOVERNANCE_MARKER} found via $ELUVIAN_WRAP_ROOT, "
        f"the ancestors of {broot}, its siblings, or the two known homes"
    )


def resolve_projects_parent(_start=None):
    """The directory that holds the project checkouts (bellows, forge, tuyere, ...):
    the bellows root's parent on every layout — <root> on the shop (projects live
    under the governance root), ~/Developer on the mini."""
    return resolve_bellows_root(_start).parent
'''

# gates.py — the QA mandate names the resolved block, never a literal
G_ANCHOR = (
    'QA_MANDATE_SUFFIX = (\n'
    '    " MANDATORY FOR THIS QA STEP (dispatcher-injected): after writing the QA report"\n'
    '    " WITH its verification table and ALL required evidence files, run the Rule 20"\n'
    '    " canonical self-check block from /Users/marklehn/Developer/GitHub/RULE_20_SELF_CHECK_BLOCK.md"\n'
    '    " (absolute path), then APPEND its stdout to the deposited report. The banner"\n'
)
G_NEW = (
    'def _rule20_block_path():\n'
    '    """The canonical Rule 20 block on THIS machine — resolved, never a layout literal\n'
    '    (a QA agent told to read a nonexistent path is the 2026-08-31 mini defect)."""\n'
    '    try:\n'
    '        from bellows_root import resolve_governance_root\n'
    '        return str(resolve_governance_root() / "RULE_20_SELF_CHECK_BLOCK.md")\n'
    '    except Exception:\n'
    '        return "$ELUVIAN_WRAP_ROOT/RULE_20_SELF_CHECK_BLOCK.md (the governance root; resolve it first)"\n'
    '\n'
    '\n'
    'QA_MANDATE_SUFFIX = (\n'
    '    " MANDATORY FOR THIS QA STEP (dispatcher-injected): after writing the QA report"\n'
    '    " WITH its verification table and ALL required evidence files, run the Rule 20"\n'
    '    " canonical self-check block from " + _rule20_block_path() +\n'
    '    " (absolute path), then APPEND its stdout to the deposited report. The banner"\n'
)

# verdict.py — re-root against the PROJECTS PARENT, not a shop sentinel (two sites)
V_ANCHOR = (
    "                if '/Developer/GitHub/' in path:\n"
    "                    parts = path.split('/Developer/GitHub/')\n"
    "                    if len(parts) == 2:\n"
    "                        path = parts[1]\n"
    "                return path\n"
)
V_NEW = (
    "                path = _strip_projects_parent(path)\n"
    "                return path\n"
)
V_HELPER_ANCHOR = 'def extract_primary_deposit(step_text: str) -> Optional[str]:\n'
V_HELPER_NEW = (
    'def _strip_projects_parent(path: str) -> str:\n'
    '    """An absolute path under THIS machine\'s projects parent becomes the\n'
    '    project-prefixed relative form (`<project>/<rel>`), which every deposit\n'
    '    consumer already normalizes. Any other path is returned unchanged.\n'
    '    Replaces a shop-layout-only sentinel split (the 2026-08 re-rooting)."""\n'
    '    try:\n'
    '        from bellows_root import resolve_projects_parent\n'
    '        parent = str(resolve_projects_parent()) + "/"\n'
    '    except Exception:\n'
    '        return path\n'
    '    return path[len(parent):] if path.startswith(parent) else path\n'
    '\n'
    '\n'
    'def extract_primary_deposit(step_text: str) -> Optional[str]:\n'
)

# planner.py
P_ANCHOR = 'GOVERNANCE_ROOT = "/Users/marklehn/Developer/GitHub"\n'
P_NEW = (
    'try:\n'
    '    from bellows_root import resolve_governance_root as _resolve_gov\n'
    '    GOVERNANCE_ROOT = str(_resolve_gov())\n'
    'except Exception:\n'
    '    # Unresolvable here: keep a path that does not exist so build_system_prompt()\n'
    '    # raises FileNotFoundError at USE, loudly, instead of a silent wrong template.\n'
    '    GOVERNANCE_ROOT = str(pathlib.Path.home() / "Developer" / "eluvian-governance")\n'
)

# decisions.py — the local walk-up becomes the shared resolver (same fallback semantics)
D_ANCHOR = (
    'def resolve_governance_root() -> Path:\n'
    '    """Walk up from this file to the nearest ancestor containing COMPANY.md (governance root)."""\n'
    '    current = Path(__file__).resolve().parent\n'
    '    while True:\n'
    '        if (current / "COMPANY.md").exists():\n'
    '            return current\n'
    '        parent = current.parent\n'
    '        if parent == current:\n'
    '            # Filesystem root reached — fall back to legacy two-parent assumption\n'
    '            logger.warning("decisions: COMPANY.md marker not found; falling back to __file__.parent.parent")\n'
    '            return Path(__file__).resolve().parent.parent\n'
    '        current = parent\n'
)
D_NEW = (
    'def resolve_governance_root() -> Path:\n'
    '    """The governance root on THIS machine via the shared resolver (bellows_root);\n'
    '    the legacy two-parent fallback is kept, with its warning, for a tree with no marker."""\n'
    '    try:\n'
    '        from bellows_root import resolve_governance_root as _shared\n'
    '        return _shared()\n'
    '    except Exception:\n'
    '        logger.warning("decisions: COMPANY.md marker not found; falling back to __file__.parent.parent")\n'
    '        return Path(__file__).resolve().parent.parent\n'
)

# bellows.py:53 and plan_claim.py:41 — the fallback literal becomes the resolver
B_ANCHOR = '    root = Path(os.environ.get("ELUVIAN_WRAP_ROOT") or "/Users/marklehn/Developer/GitHub")\n'
B_NEW = (
    '    # ROOT is the PROJECTS PARENT here (root / "tuyere", root / "lessons-forge"):\n'
    '    # the shop root doubled as both; on every other layout they differ.\n'
    '    try:\n'
    '        from bellows_root import resolve_projects_parent as _resolve_pp\n'
    '        root = _resolve_pp()\n'
    '    except Exception:\n'
    '        root = Path(os.environ.get("ELUVIAN_WRAP_ROOT") or (Path.home() / "Developer"))\n'
)

# CLAUDE.md — the documented seam resolution names the resolver, not a literal
C_ANCHOR = (
    '`ROOT/tuyere` where ROOT = `$ELUVIAN_WRAP_ROOT` else the literal\n'
    '`/Users/marklehn/Developer/GitHub`. First candidate whose\n'
)
C_NEW = (
    '`ROOT/tuyere` where ROOT = the resolved PROJECTS PARENT\n'
    '(`bellows_root.resolve_projects_parent()` — the bellows checkout\'s parent on\n'
    'every layout; `$ELUVIAN_WRAP_ROOT` only as the fallback when the resolver\n'
    'cannot run — plan de-hardcode-governance-root, 2026-09-01). First candidate whose\n'
)

# scripts/plan_lint.py — (o1)'s second root is the resolved governance root
L_ANCHOR = "    SHOP_ROOT = '/Users/marklehn/Developer/GitHub'\n"
L_NEW = (
    "    try:\n"
    "        from bellows_root import resolve_governance_root as _resolve_gov\n"
    "        SHOP_ROOT = str(_resolve_gov())  # the governance root on THIS machine (name kept for the (o1) read below)\n"
    "    except Exception:\n"
    "        SHOP_ROOT = str(Path.home() / 'Developer' / 'eluvian-governance')\n"
)

# scripts/migrate_orphan_verdicts.py — the canonical bellows root, resolved
M_ANCHOR = 'MAIN_REPO = Path("/Users/marklehn/Developer/GitHub/bellows")\n'
M_NEW = (
    'import sys  # noqa: E402\n'
    'sys.path.insert(0, str(BELLOWS_ROOT))\n'
    'from bellows_root import resolve_bellows_root  # noqa: E402\n'
    'MAIN_REPO = resolve_bellows_root()\n'
)


# ---------------------------------------------------------------------------
# NEW file (asserted absent in <in>): the resolver's tests + the three consumers
TEST_FILE = "tests/test_governance_root.py"
TEST_SRC = '''"""resolve_governance_root / resolve_projects_parent — both layouts, the env
override, the loud failure — and the consumers that used to carry the shop literal."""
from pathlib import Path

import pytest

import bellows_root as br


def _shop(tmp_path):
    root = tmp_path / "GitHub"
    (root / "bellows").mkdir(parents=True)
    (root / "COMPANY.md").write_text("x")
    (root / "bellows" / "bellows.py").write_text("")
    return root


def _mini(tmp_path):
    dev = tmp_path / "Developer"
    (dev / "bellows").mkdir(parents=True)
    (dev / "eluvian-governance").mkdir()
    (dev / "eluvian-governance" / "COMPANY.md").write_text("x")
    (dev / "bellows" / "bellows.py").write_text("")
    return dev


class TestResolveGovernanceRoot:
    def test_shop_layout_ancestor(self, tmp_path):
        root = _shop(tmp_path)
        assert br.resolve_governance_root(_start=root / "bellows", _env="") == root.resolve()

    def test_mini_layout_sibling(self, tmp_path):
        dev = _mini(tmp_path)
        got = br.resolve_governance_root(_start=dev / "bellows", _env="")
        assert got == (dev / "eluvian-governance").resolve()

    def test_env_override_wins_when_it_holds_marker(self, tmp_path):
        dev = _mini(tmp_path)
        other = tmp_path / "elsewhere"
        other.mkdir()
        (other / "COMPANY.md").write_text("x")
        assert br.resolve_governance_root(_start=dev / "bellows", _env=str(other)) == other.resolve()

    def test_env_override_ignored_without_marker(self, tmp_path):
        dev = _mini(tmp_path)
        bogus = tmp_path / "bogus"
        bogus.mkdir()
        got = br.resolve_governance_root(_start=dev / "bellows", _env=str(bogus))
        assert got == (dev / "eluvian-governance").resolve()

    def test_no_marker_anywhere_raises(self, tmp_path, monkeypatch):
        (tmp_path / "bellows").mkdir()
        (tmp_path / "bellows" / "bellows.py").write_text("")
        monkeypatch.setattr(Path, "home", classmethod(lambda cls: tmp_path / "nohome"))
        with pytest.raises(ValueError):
            br.resolve_governance_root(_start=tmp_path / "bellows", _env="")

    def test_this_machine_resolves_without_env(self, monkeypatch):
        monkeypatch.delenv("ELUVIAN_WRAP_ROOT", raising=False)
        assert (br.resolve_governance_root() / "COMPANY.md").is_file()

    def test_projects_parent_is_bellows_parent(self, tmp_path):
        dev = _mini(tmp_path)
        assert br.resolve_projects_parent(_start=dev / "bellows") == (dev / "bellows").resolve().parent


class TestConsumers:
    def test_qa_mandate_names_the_resolved_block(self):
        import gates
        assert str(br.resolve_governance_root() / "RULE_20_SELF_CHECK_BLOCK.md") in gates.QA_MANDATE_SUFFIX
        assert "/Users/marklehn/Developer/GitHub" not in gates.QA_MANDATE_SUFFIX

    def test_planner_template_path_exists(self):
        import planner
        assert Path(planner.PLANNER_TEMPLATE_PATH).is_file()

    def test_decisions_phrases_file_exists(self):
        import decisions
        assert decisions.PHRASES_FILE.is_file()

    def test_verdict_reroot_under_projects_parent(self, monkeypatch, tmp_path):
        import verdict
        monkeypatch.setattr(br, "resolve_projects_parent", lambda _start=None: tmp_path / "Developer")
        under = str(tmp_path / "Developer" / "forge" / "k" / "x.md")
        assert verdict._strip_projects_parent(under) == "forge/k/x.md"
        assert verdict._strip_projects_parent("/somewhere/else/x.md") == "/somewhere/else/x.md"
        assert verdict._strip_projects_parent("knowledge/x.md") == "knowledge/x.md"

    def test_tuyere_seam_third_candidate_is_projects_parent(self, monkeypatch, tmp_path):
        import plan_claim
        monkeypatch.delenv("ELUVIAN_WRAP_TUYERE", raising=False)
        monkeypatch.delenv("ELUVIAN_WRAP_ROOT", raising=False)
        monkeypatch.setattr(Path, "home", classmethod(lambda cls: tmp_path / "nohome"))
        pp = tmp_path / "Projects"
        (pp / "tuyere" / ".venv" / "bin").mkdir(parents=True)
        (pp / "tuyere" / ".venv" / "bin" / "python").write_text("")
        monkeypatch.setattr(br, "resolve_projects_parent", lambda _start=None: pp)
        assert plan_claim._tuyere_checkout() == pp / "tuyere"
'''

EDITS = {
    "bellows_root.py": [(R0_ANCHOR, R0_NEW)],
    "gates.py": [(G_ANCHOR, G_NEW)],
    "verdict.py": [(V_HELPER_ANCHOR, V_HELPER_NEW), (V_ANCHOR, V_NEW), (V_ANCHOR, V_NEW)],
    "planner.py": [(P_ANCHOR, P_NEW)],
    "decisions.py": [(D_ANCHOR, D_NEW)],
    "bellows.py": [(B_ANCHOR, B_NEW)],
    "plan_claim.py": [(B_ANCHOR, B_NEW)],
    "scripts/plan_lint.py": [(L_ANCHOR, L_NEW)],
    "scripts/migrate_orphan_verdicts.py": [(M_ANCHOR, M_NEW)],
    "CLAUDE.md": [(C_ANCHOR, C_NEW)],
}
# verdict.py's re-root anchor occurs TWICE by design (two extraction paths); the
# edit list applies it twice, each application asserting the count AT THAT
# MOMENT — the first sees 2, the second sees 1. apply() asserts ==1, so the
# first application is wrapped below.

POST = [
    ("bellows_root.py", "def resolve_governance_root(", 1),
    ("bellows_root.py", "def resolve_projects_parent(", 1),
    ("gates.py", "_rule20_block_path()", 2),
    ("gates.py", "/Users/marklehn/Developer/GitHub", 0),
    ("verdict.py", "_strip_projects_parent(path)", 2),
    ("verdict.py", "/Developer/GitHub/", 0),
    ("planner.py", "resolve_governance_root", 1),
    ("planner.py", "/Users/marklehn/Developer/GitHub", 0),
    ("decisions.py", "from bellows_root import resolve_governance_root", 1),
    ("bellows.py", "resolve_projects_parent", 1),
    ("bellows.py", "/Users/marklehn/Developer/GitHub", 0),
    ("plan_claim.py", "resolve_projects_parent", 1),
    ("plan_claim.py", "/Users/marklehn/Developer/GitHub", 0),
    ("CLAUDE.md", "resolve_projects_parent()", 1),
    ("CLAUDE.md", "/Users/marklehn/Developer/GitHub", 0),
    ("scripts/plan_lint.py", "/Users/marklehn/Developer/GitHub", 0),
    ("scripts/migrate_orphan_verdicts.py", "/Users/marklehn/Developer/GitHub", 0),
]


def main():
    if len(sys.argv) != 3:
        raise SystemExit("usage: builder <bellows-root-in> <bellows-root-out>")
    src_root, dst_root = sys.argv[1], sys.argv[2]
    rp = os.path.realpath(dst_root)
    _req(rp != os.path.realpath(LIVE_ROOT), "output is the live bellows checkout")
    _req(not rp.casefold().startswith((os.path.realpath(LIVE_ROOT) + os.sep).casefold()),
         "output is inside the live bellows checkout")
    _req(os.path.realpath(src_root) != rp, "output equals input")
    for t in TARGETS:
        s = os.path.join(src_root, t)
        _req(os.path.isfile(s), f"missing input {s}")
        d = os.path.join(dst_root, t)
        _req(not (os.path.exists(d) and os.path.samefile(d, os.path.join(LIVE_ROOT, t))),
             f"output {d} is samefile with the live {t}")
    outs = {}
    for t in TARGETS:
        raw = open(os.path.join(src_root, t), "rb").read()
        _req(b"\r\n" not in raw, f"{t}: CRLF input refused")
        text = raw.decode("utf-8")
        edits = EDITS[t]
        if t == "verdict.py":
            # helper first (count 1), then the doubled re-root anchor: 2 -> 1 -> 0
            text = apply(text, [edits[0]], t)
            n = text.count(V_ANCHOR)
            _req(n == 2, f"verdict.py re-root anchor count {n} != 2")
            text = text.replace(V_ANCHOR, V_NEW)
        else:
            text = apply(text, edits, t)
        outs[t] = text
    for t, token, want in POST:
        got = outs[t].count(token)
        _req(got == want, f"POST {t}: {token!r} count {got} != {want}")
    # no live file may still carry a literal the builder claims to have removed
    for t in TARGETS:
        _req(outs[t] != open(os.path.join(src_root, t), encoding="utf-8").read(),
             f"{t}: output identical to input (no edit applied)")
    for t in TARGETS:
        d = os.path.join(dst_root, t)
        os.makedirs(os.path.dirname(d), exist_ok=True)
        with open(d, "wb") as f:
            f.write(outs[t].encode("utf-8"))
    _req(not os.path.exists(os.path.join(src_root, TEST_FILE)), f"{TEST_FILE} already exists in input")
    d = os.path.join(dst_root, TEST_FILE)
    os.makedirs(os.path.dirname(d), exist_ok=True)
    with open(d, "wb") as f:
        f.write(TEST_SRC.encode("utf-8"))
    _req(TEST_SRC.count("def test_") == 12, "test file must carry 12 tests")
    digest = hashlib.sha256(b"".join(outs[t].encode("utf-8") for t in TARGETS)).hexdigest()
    print(f"OK — {len(TARGETS)} files edited + {TEST_FILE} written, {sum(len(v) for v in EDITS.values())} edits; combined sha {digest[:16]}…")


if __name__ == "__main__":
    from pathlib import Path  # noqa: F401 — referenced by generated text only
    main()
