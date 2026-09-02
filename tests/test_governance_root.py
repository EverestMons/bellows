"""resolve_governance_root / resolve_projects_parent — both layouts, the env
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
        block = str(br.resolve_governance_root() / "RULE_20_SELF_CHECK_BLOCK.md")
        assert gates.QA_MANDATE_SUFFIX.count(block) == 1
        # On the shop the resolved root IS the old literal, so the mandate may carry it
        # legitimately there; what must be gone is the literal in the SOURCE.
        assert "/Users/marklehn/Developer/GitHub" not in Path(gates.__file__).read_text()

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
