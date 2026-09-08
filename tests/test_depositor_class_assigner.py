"""Class-assigner suite — tests 0–11 for the repo-aware _assign_class rewrite.

Test 0 lives in tests/test_depositor.py (the renamed
test_omitting_project_context_fails_shut).  Tests 1–11 live here.

Mock pattern: monkeypatch bellows_root.resolve_governance_root and
bellows_root.resolve_projects_parent to tmp_path roots so no real
filesystem layout is assumed.  Existence-based redirects (E5, leading-segment)
are tested by creating/omitting files in those roots.
"""

import json
import os
import pathlib
import sqlite3
import sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import pytest

BELLOWS_ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BELLOWS_ROOT))
sys.path.insert(0, str(BELLOWS_ROOT / "scripts"))

import bellows_root as br_mod
import depositor as dep_mod
from lifecycle import init_lifecycle_db


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _dep(tmp_path=None, config=None):
    """Depositor built from dummies; no real lifecycle.db needed for class tests."""
    if tmp_path is None:
        import tempfile
        tmp = pathlib.Path(tempfile.mkdtemp())
    else:
        tmp = tmp_path
    db_path = str(tmp / "lifecycle.db")
    init_lifecycle_db(db_path)
    return dep_mod.Depositor(
        disk_preflight_fn=lambda: True,
        shutting_down_check=lambda: False,
        config=config or {},
        lifecycle_db_path=db_path,
    )


def _mini_roots(tmp_path):
    """Return (G, P) for a mini-shaped mock: G ≠ P."""
    G = tmp_path / "governance"
    G.mkdir(exist_ok=True)
    P = tmp_path
    return G, P


def _shop_roots(tmp_path):
    """Return (G, P) for a shop-shaped mock: G == P."""
    G = tmp_path / "shop"
    G.mkdir(exist_ok=True)
    return G, G


# ---------------------------------------------------------------------------
# Test 1 — the thirteen P3 cases (one function, not parametrize — C8)
# ---------------------------------------------------------------------------

class TestThirteenCases:
    def test_1_thirteen_cases(self, monkeypatch, tmp_path):
        """Re-derive P3: the AFTER class of every P2 case, asserted against P3.

        Uses a mini-shaped mock (G ≠ P).  Absolute real-system paths that fall
        outside the mock G and P resolve to UNKNOWN → shop-infra (E1, fail-shut).
        """
        G, P = _mini_roots(tmp_path)

        # Populate files the governance-existence redirect (E5) needs
        (G / "DRAFTING_CYCLE.md").touch()
        (G / "governance").mkdir(exist_ok=True)
        (G / "governance" / "GUARDRAILS.md").touch()

        monkeypatch.setattr(br_mod, "resolve_governance_root", lambda _start=None: G)
        monkeypatch.setattr(br_mod, "resolve_projects_parent", lambda _start=None: P)

        dep = _dep(tmp_path)

        invoice = str(P / "invoice-pulse")
        os.makedirs(invoice, exist_ok=True)
        tuyere = str(P / "tuyere")
        os.makedirs(tuyere, exist_ok=True)
        bellows = str(P / "bellows")
        os.makedirs(bellows, exist_ok=True)
        forge_lessons = str(P / "forge_lessons")
        os.makedirs(forge_lessons, exist_ok=True)

        table = [
            # 42: app.py from invoice-pulse → app-feature (bare arm deleted)
            (["app.py"],                        invoice,  "app-feature"),
            # 26: GOVERNANCE.md from tuyere → shop-infra (name floor)
            (["GOVERNANCE.md"],                 tuyere,   "shop-infra"),
            # 26b: config.example.json from tuyere → app-feature
            (["config.example.json"],           tuyere,   "app-feature"),
            # docs/GOVERNANCE.md has a directory component → not name-floor → app-feature
            (["docs/GOVERNANCE.md"],            tuyere,   "app-feature"),
            # 66 abs DC from tuyere: outside mock G/P → UNKNOWN → shop-infra
            ([str(G / "DRAFTING_CYCLE.md")],    tuyere,   "shop-infra"),
            # 66 bare DC from tuyere: exists under G → redirect → shop-infra
            (["DRAFTING_CYCLE.md"],             tuyere,   "shop-infra"),
            # 66 abs LESSONS: single segment under P → UNKNOWN → shop-infra
            ([str(P / "LESSONS.md")],           tuyere,   "shop-infra"),
            # 66 abs DC from bellows: bellows is infra → shop-infra
            ([str(P / "bellows" / "DRAFTING_CYCLE.md")], bellows, "shop-infra"),
            # 99: forge_lessons → shop-infra (now in infra set)
            (["scripts/x.py"],                  forge_lessons, "shop-infra"),
            # root "" → UNKNOWN → shop-infra (fail-shut)
            (["DRAFTING_CYCLE.md"],             "",       "shop-infra"),
            # bellows/depositor.py root "" → bellows infra → shop-infra
            (["bellows/depositor.py"],          "",       "shop-infra"),
            # NEW bare file in tuyere → app-feature (no redirect, tuyere not infra)
            (["brand_new.md"],                  tuyere,   "app-feature"),
            # knowledge/ exempt: bellows knowledge write → app-feature
            (["knowledge/development/x.md"],    bellows,  "app-feature"),
        ]

        for writes, root, expected in table:
            result = dep._assign_class(writes, root)
            assert result == expected, (
                f"writes={writes!r} root={str(root):40}: "
                f"expected {expected!r}, got {result!r}"
            )


# ---------------------------------------------------------------------------
# Test 2 — absolute path resolves by the RESOLVERS (E6, E7, E9, f3, f9)
# ---------------------------------------------------------------------------

class TestAbsolutePathByResolvers:
    def test_2_absolute_path_by_resolvers(self, monkeypatch, tmp_path):
        """Identity comes from the resolvers, never from the checkout's name.

        Covers both mini and shop shapes, two RELATIVE writes on shop shape,
        a governance dir named 'GitHub' (E6), path with '..' (E9),
        a path under neither root (E1), and a single-segment under P (f9).
        """
        # ----- mini shape: G is a subdir named "governance" -----
        G_mini = tmp_path / "mini" / "governance"
        P_mini = tmp_path / "mini"
        G_mini.mkdir(parents=True)
        (P_mini / "bellows").mkdir()
        (P_mini / "tuyere").mkdir()

        monkeypatch.setattr(br_mod, "resolve_governance_root", lambda _start=None: G_mini)
        monkeypatch.setattr(br_mod, "resolve_projects_parent", lambda _start=None: P_mini)

        dep = _dep(tmp_path)
        broot = str(P_mini / "bellows")
        troot = str(P_mini / "tuyere")

        # <parent>/tuyere/tuyere/threads.py from bellows → app-feature
        assert dep._assign_class(
            [str(P_mini / "tuyere" / "tuyere" / "threads.py")], broot
        ) == "app-feature"

        # <parent>/bellows/depositor.py from tuyere → shop-infra
        assert dep._assign_class(
            [str(P_mini / "bellows" / "depositor.py")], troot
        ) == "shop-infra"

        # /elsewhere/x.py (under neither root) → UNKNOWN → shop-infra (E1)
        assert dep._assign_class(["/elsewhere/x.py"], troot) == "shop-infra"

        # <parent>/README.md single segment under P → UNKNOWN → shop-infra (f9)
        assert dep._assign_class([str(P_mini / "README.md")], troot) == "shop-infra"

        # path with '..' resolves: <parent>/tuyere/../bellows/depositor.py → shop-infra (E9)
        dotdot = str(P_mini / "tuyere" / ".." / "bellows" / "depositor.py")
        assert dep._assign_class([dotdot], troot) == "shop-infra"

        # ----- mini shape with governance dir named 'GitHub' (E6) -----
        G_github = tmp_path / "github_mini" / "GitHub"
        P_github = tmp_path / "github_mini"
        G_github.mkdir(parents=True)
        (P_github / "tuyere").mkdir()

        monkeypatch.setattr(br_mod, "resolve_governance_root", lambda _start=None: G_github)
        monkeypatch.setattr(br_mod, "resolve_projects_parent", lambda _start=None: P_github)

        # <parent>/GitHub/DRAFTING_CYCLE.md from tuyere → governance → shop-infra
        assert dep._assign_class(
            [str(G_github / "DRAFTING_CYCLE.md")],
            str(P_github / "tuyere"),
        ) == "shop-infra"

        # ----- shop shape: G == P -----
        G_shop, P_shop = _shop_roots(tmp_path)
        (G_shop / "tuyere").mkdir(exist_ok=True)
        (G_shop / "invoice-pulse").mkdir(exist_ok=True)
        (G_shop / "governance").mkdir(exist_ok=True)

        monkeypatch.setattr(br_mod, "resolve_governance_root", lambda _start=None: G_shop)
        monkeypatch.setattr(br_mod, "resolve_projects_parent", lambda _start=None: G_shop)

        # <root>/DRAFTING_CYCLE.md → root file → governance → shop-infra (f3)
        assert dep._assign_class(
            [str(G_shop / "DRAFTING_CYCLE.md")],
            str(G_shop / "tuyere"),
        ) == "shop-infra"

        # <root>/tuyere/tuyere/x.py → repo tuyere → not infra → app-feature
        assert dep._assign_class(
            [str(G_shop / "tuyere" / "tuyere" / "x.py")],
            str(G_shop / "tuyere"),
        ) == "app-feature"

        # <root>/governance/GUARDRAILS.md from <root>/tuyere → governance → shop-infra (E7)
        assert dep._assign_class(
            [str(G_shop / "governance" / "GUARDRAILS.md")],
            str(G_shop / "tuyere"),
        ) == "shop-infra"

        # Relative write: ["app.py"] from <root>/invoice-pulse → app-feature (42 on Air, C1)
        assert dep._assign_class(
            ["app.py"],
            str(G_shop / "invoice-pulse"),
        ) == "app-feature"

        # Relative write: ["config.example.json"] from <root>/tuyere → app-feature (26b on Air, C1)
        assert dep._assign_class(
            ["config.example.json"],
            str(G_shop / "tuyere"),
        ) == "app-feature"


# ---------------------------------------------------------------------------
# Test 3 — governance-existence redirect (E5)
# ---------------------------------------------------------------------------

class TestGovernanceExistenceRedirect:
    def test_3_governance_existence_redirect(self, monkeypatch, tmp_path):
        """A relative path absent under the project and present under G → governance."""
        G, P = _mini_roots(tmp_path)
        (P / "tuyere").mkdir()

        # Create files under G that the redirect needs
        (G / "DRAFTING_CYCLE.md").touch()
        (G / "governance").mkdir(exist_ok=True)
        (G / "governance" / "GUARDRAILS.md").touch()

        monkeypatch.setattr(br_mod, "resolve_governance_root", lambda _start=None: G)
        monkeypatch.setattr(br_mod, "resolve_projects_parent", lambda _start=None: P)

        dep = _dep(tmp_path)
        troot = str(P / "tuyere")

        # bare DRAFTING_CYCLE.md filed from tuyere: absent under tuyere, present under G
        assert dep._assign_class(["DRAFTING_CYCLE.md"], troot) == "shop-infra"

        # governance/GUARDRAILS.md filed from tuyere: absent under tuyere, present under G
        assert dep._assign_class(["governance/GUARDRAILS.md"], troot) == "shop-infra"

        # Same path present under the project: belongs to the project, not governance
        (P / "tuyere" / "DRAFTING_CYCLE.md").touch()
        assert dep._assign_class(["DRAFTING_CYCLE.md"], troot) == "register-writing"

        # Path in neither: belongs to the filing project (fork 3 stated, not fixed)
        assert dep._assign_class(["neither.md"], troot) == "app-feature"


# ---------------------------------------------------------------------------
# Test 4 — project_root == "" fails shut (f1, E7, E8, C1, C4)
# ---------------------------------------------------------------------------

class TestRootEmptyFailsShut:
    def test_4_root_empty_fails_shut(self, monkeypatch, tmp_path):
        """project_root == '' resolves with no filesystem check and fails shut."""
        G, P = _mini_roots(tmp_path)
        monkeypatch.setattr(br_mod, "resolve_governance_root", lambda _start=None: G)
        monkeypatch.setattr(br_mod, "resolve_projects_parent", lambda _start=None: P)

        dep = _dep(tmp_path)

        # Re-assert the seven ("…", "") assertions from tests/test_depositor.py:155-169
        assert dep._assign_class(["knowledge/research/foo.md"], "") == "read-only"
        assert dep._assign_class(["bellows/knowledge/research/bar.md"], "") == "read-only"
        assert dep._assign_class(["scratch/tmp.txt"], "") == "read-only"
        assert dep._assign_class(["knowledge/decisions/register-cycles.md"], "") == "register-writing"
        assert dep._assign_class(["DRAFTING_CYCLE.md"], "") == "shop-infra"
        assert dep._assign_class(["bellows/depositor.py"], "") == "shop-infra"
        assert dep._assign_class(["bellows/bellows.py", "bellows/status.py"], "") == "shop-infra"

        # <declare> is UNKNOWN → shop-infra (E8)
        assert dep._assign_class(["<declare>"], str(P / "tuyere")) == "shop-infra"

        # governance-lane project_root → shop-infra (E7)
        gov_lane = str(G / "governance")
        os.makedirs(gov_lane, exist_ok=True)
        assert dep._assign_class(["scripts/x.py"], gov_lane) == "shop-infra"

        # shop shape: <root>/governance as project → shop-infra (C1)
        G_shop, P_shop = _shop_roots(tmp_path)
        (G_shop / "governance").mkdir(exist_ok=True)
        monkeypatch.setattr(br_mod, "resolve_governance_root", lambda _start=None: G_shop)
        monkeypatch.setattr(br_mod, "resolve_projects_parent", lambda _start=None: G_shop)
        assert dep._assign_class(["scripts/x.py"], str(G_shop / "governance")) == "shop-infra"

        # absolute path with root "" whose leading-segment is infra → shop-infra (C4)
        abs_tuyere_x = str(P / "tuyere" / "tuyere" / "x.py")
        assert dep._assign_class([abs_tuyere_x], "") == "shop-infra"


# ---------------------------------------------------------------------------
# Test 5 — knowledge/ exemption (infra repo's knowledge never triggers shop-infra)
# ---------------------------------------------------------------------------

class TestKnowledgeExemption:
    def test_5_knowledge_exemption(self, monkeypatch, tmp_path):
        """An infra repo's knowledge/ (and governance's governance/knowledge/) is exempt."""
        G, P = _mini_roots(tmp_path)
        monkeypatch.setattr(br_mod, "resolve_governance_root", lambda _start=None: G)
        monkeypatch.setattr(br_mod, "resolve_projects_parent", lambda _start=None: P)

        dep = _dep(tmp_path)
        broot = str(P / "bellows")
        os.makedirs(broot)

        # bellows knowledge write → app-feature (the 100018 shape)
        assert dep._assign_class(["knowledge/development/x.md"], broot) == "app-feature"
        assert dep._assign_class(["knowledge/research/x.md"], broot) == "read-only"

        # absolute governance knowledge path from bellows → app-feature
        gov_know = str(G / "governance" / "knowledge" / "architecture" / "x.md")
        assert dep._assign_class([gov_know], broot) == "app-feature"


# ---------------------------------------------------------------------------
# Test 6 — read-only precedence
# ---------------------------------------------------------------------------

class TestReadOnlyPrecedence:
    def test_6_read_only_precedence(self, monkeypatch, tmp_path):
        """knowledge/research/ and scratch/ alone → read-only, regardless of repo."""
        G, P = _mini_roots(tmp_path)
        monkeypatch.setattr(br_mod, "resolve_governance_root", lambda _start=None: G)
        monkeypatch.setattr(br_mod, "resolve_projects_parent", lambda _start=None: P)

        dep = _dep(tmp_path)
        broot = str(P / "bellows")
        os.makedirs(broot)

        assert dep._assign_class(["knowledge/research/x.md"], broot) == "read-only"
        assert dep._assign_class(["scratch/tmp.txt"], "") == "read-only"
        assert dep._assign_class(["bellows/knowledge/research/y.md"], "") == "read-only"


# ---------------------------------------------------------------------------
# Test 7 — out-of-tree
# ---------------------------------------------------------------------------

class TestOutOfTree:
    def test_7_out_of_tree(self, monkeypatch, tmp_path):
        """~/... and ../... writes alone → None."""
        G, P = _mini_roots(tmp_path)
        monkeypatch.setattr(br_mod, "resolve_governance_root", lambda _start=None: G)
        monkeypatch.setattr(br_mod, "resolve_projects_parent", lambda _start=None: P)

        dep = _dep(tmp_path)
        assert dep._assign_class(["~/Desktop/x.md"], "") is None
        assert dep._assign_class(["../other/x.md"], "") is None
        assert dep._assign_class(["~/Desktop/x.md", "../other/x.md"], "") is None


# ---------------------------------------------------------------------------
# Test 8 — register-writing precedence and pairing
# ---------------------------------------------------------------------------

class TestRegisterWriting:
    def test_8_register_writing(self, monkeypatch, tmp_path):
        """register-* path alone → register-writing; paired with infra write → shop-infra."""
        G, P = _mini_roots(tmp_path)
        monkeypatch.setattr(br_mod, "resolve_governance_root", lambda _start=None: G)
        monkeypatch.setattr(br_mod, "resolve_projects_parent", lambda _start=None: P)

        dep = _dep(tmp_path)
        broot = str(P / "bellows")
        troot = str(P / "tuyere")
        os.makedirs(broot)
        os.makedirs(troot)

        # register-writing in a non-infra repo
        assert dep._assign_class(["knowledge/decisions/register-x.md"], troot) == "register-writing"

        # register-writing in an infra repo (knowledge/ exemption holds, E3)
        assert dep._assign_class(["knowledge/decisions/register-x.md"], broot) == "register-writing"

        # paired: register + infra write → shop-infra (precedence)
        assert dep._assign_class(
            ["knowledge/decisions/register-x.md", "depositor.py"], broot
        ) == "shop-infra"


# ---------------------------------------------------------------------------
# Test 9 — floor cannot be disabled
# ---------------------------------------------------------------------------

class TestFloorCannotBeDisabled:
    def test_9_floor_cannot_be_disabled(self, monkeypatch, tmp_path):
        """config={}, config={'shop_infra_projects': []}, and extended config all
        keep the six floor names; the third adds a name."""
        G, P = _mini_roots(tmp_path)
        monkeypatch.setattr(br_mod, "resolve_governance_root", lambda _start=None: G)
        monkeypatch.setattr(br_mod, "resolve_projects_parent", lambda _start=None: P)

        db_path = str(tmp_path / "lifecycle.db")
        init_lifecycle_db(db_path)

        troot = str(P / "tuyere")
        os.makedirs(troot, exist_ok=True)

        for cfg in ({}, {"shop_infra_projects": []}, {"shop_infra_projects": None},
                    {"shop_infra_projects": "not-a-list"}):
            dep = dep_mod.Depositor(
                disk_preflight_fn=lambda: True,
                shutting_down_check=lambda: False,
                config=cfg,
                lifecycle_db_path=db_path,
            )
            # root "" assertions (UNKNOWN → shop-infra regardless of floor)
            assert dep._assign_class(["bellows/x.py"], "") == "shop-infra", cfg
            assert dep._assign_class(["forge/x.py"], "") == "shop-infra", cfg
            assert dep._assign_class(["forge_lessons/x.py"], "") == "shop-infra", cfg
            assert dep._assign_class(["lessons-forge/x.py"], "") == "shop-infra", cfg
            assert dep._assign_class(["anvil/x.py"], "") == "shop-infra", cfg
            assert dep._assign_class(["eluvian-governance/x.py"], "") == "shop-infra", cfg
            # non-"" root assertions: leading-segment redirect requires the floor to be populated
            assert dep._assign_class(["bellows/x.py"], troot) == "shop-infra", cfg

        # config extension adds a name; tested with a non-"" root so the redirect
        # actually fires (root "" falls back to UNKNOWN→shop-infra and masks the defect)
        dep_ext = dep_mod.Depositor(
            disk_preflight_fn=lambda: True,
            shutting_down_check=lambda: False,
            config={"shop_infra_projects": ["my_forge"]},
            lifecycle_db_path=db_path,
        )
        assert dep_ext._assign_class(["my_forge/x.py"], troot) == "shop-infra"
        assert dep_ext._assign_class(["bellows/x.py"], "") == "shop-infra"


# ---------------------------------------------------------------------------
# Test 10 — governance-surface name floor (fork 5, E4)
# ---------------------------------------------------------------------------

class TestGovernanceSurfaceNameFloor:
    def test_10_governance_surface_name_floor(self, monkeypatch, tmp_path):
        """GOVERNANCE.md, MACHINE_SETUP.md, COMPANY.md at any repo root → shop-infra.
        The test is on rel, not on the write's spelling (E4).
        """
        G, P = _mini_roots(tmp_path)
        monkeypatch.setattr(br_mod, "resolve_governance_root", lambda _start=None: G)
        monkeypatch.setattr(br_mod, "resolve_projects_parent", lambda _start=None: P)

        dep = _dep(tmp_path)
        troot = str(P / "tuyere")
        os.makedirs(troot)

        # At a non-infra project root → shop-infra
        for name in ("GOVERNANCE.md", "MACHINE_SETUP.md", "COMPANY.md"):
            assert dep._assign_class([name], troot) == "shop-infra", name

        # docs/GOVERNANCE.md has a directory component → NOT floor → app-feature
        assert dep._assign_class(["docs/GOVERNANCE.md"], troot) == "app-feature"

        # governance.md (lowercase) → NOT floor (exact, case-sensitive) → app-feature
        assert dep._assign_class(["governance.md"], troot) == "app-feature"

        # The floor tests rel, not the spelling: <parent>/tuyere/GOVERNANCE.md from bellows
        # resolves to ("tuyere", "GOVERNANCE.md") → rel = "GOVERNANCE.md" → floor → shop-infra
        broot = str(P / "bellows")
        os.makedirs(broot)
        assert dep._assign_class(
            [str(P / "tuyere" / "GOVERNANCE.md")], broot
        ) == "shop-infra"

        # The set is CODE, not config: no config key overrides it (f6)
        dep_no_gov = dep_mod.Depositor(
            disk_preflight_fn=lambda: True,
            shutting_down_check=lambda: False,
            config={"governance_surface_names": []},
            lifecycle_db_path=str(tmp_path / "lifecycle.db"),
        )
        assert dep_no_gov._assign_class(["GOVERNANCE.md"], troot) == "shop-infra"


# ---------------------------------------------------------------------------
# Test 11 — thread 199: _rerun_validation passes warnings to cycle_check (P7)
# ---------------------------------------------------------------------------

class TestRereunValidationWarnings:
    def test_11_rerun_validation_warnings(self, monkeypatch, tmp_path):
        """_rerun_validation passes a warnings list to cycle_check.run_check and
        carries it into the hold result; _hold's sidecar then contains warnings.
        """
        # Build a minimal Depositor
        db_path = str(tmp_path / "lifecycle.db")
        init_lifecycle_db(db_path)
        dep = dep_mod.Depositor(
            disk_preflight_fn=lambda: True,
            shutting_down_check=lambda: False,
            config={},
            lifecycle_db_path=db_path,
        )
        dep._bellows_root = BELLOWS_ROOT

        battery_line = "BATTERY: fold_check=DRIFT plan_lint=PASS propagation_check=PASS"
        warn_line = "WARN: BAR_MET downgraded to CONTINUE — battery: fold_check=DRIFT"

        def _mock_run_check(path, warnings=None):
            if warnings is not None:
                warnings.append(battery_line)
                warnings.append(warn_line)
            return ("CONTINUE", 0)

        monkeypatch.setattr(dep_mod.cycle_check, "run_check", _mock_run_check)

        plan_path = tmp_path / "ready-test.md"
        plan_path.write_text("# Test Plan\n")

        r = dep._rerun_validation(str(plan_path), "# Test Plan\n")

        assert r["hold"] is True
        assert r["reason"] == "cycle_check:CONTINUE"
        assert "warnings" in r, "result must carry warnings key"
        assert battery_line in r["warnings"]
        assert warn_line in r["warnings"]

        # Verify _hold writes the warnings into the sidecar JSON
        dep._hold(str(plan_path), r["reason"], r)
        hold_json = str(plan_path).replace("ready-test.md", "hold-test.hold.json")
        assert os.path.exists(hold_json), "sidecar must be written"
        with open(hold_json) as f:
            sidecar = json.load(f)
        assert "warnings" in sidecar, "sidecar must contain warnings key"
        assert battery_line in sidecar["warnings"]
        assert warn_line in sidecar["warnings"]
