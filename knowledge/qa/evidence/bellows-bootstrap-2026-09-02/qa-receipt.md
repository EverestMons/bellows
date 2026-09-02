# QA Receipt — bellows-bootstrap-2026-09-02 (plan 100017, Step 2 QA)

**Date:** 2026-09-02 | **QA Agent:** bellows QA agent (Step 2 QA)
**Plan slug:** `bellows-bootstrap-2026-09-02`
**Worktree:** `/Users/marklehn/Developer/bellows/.bellows-worktrees/100017`
**GOV:** `/Users/marklehn/Developer/eluvian-governance`
**BPY:** `/Users/marklehn/Developer/bellows/.venv/bin/python`

---

## Verification Table

| Item | Expected | Evidence | Status |
|------|----------|----------|--------|
| Bellows commit paths | `CLAUDE.md`, `scripts/bootstrap.sh`, `knowledge/development/dev-log-bellows-bootstrap-2026-09-02.md` | `git show --stat HEAD` → exactly those 3 paths (probes-raw.txt Item 1) | ✅ |
| EXEC_BIT | `scripts/bootstrap.sh` is executable | `test -x scripts/bootstrap.sh → EXEC_BIT` (probes-raw.txt) | ✅ |
| Syntax check | `bash -n scripts/bootstrap.sh` exits 0 | `syntax=0` (probes-raw.txt) | ✅ |
| P7 CLAUDE.md — `.venv/bin/python dashboard.py` | count 1 | count 1 (probes-raw.txt) | ✅ |
| P7 CLAUDE.md — `.venv/bin/python bellows.py` | count 1 | count 1 (probes-raw.txt) | ✅ |
| P7 CLAUDE.md — `.venv/bin/python status.py` | count 1 | count 1 (probes-raw.txt) | ✅ |
| P7 CLAUDE.md — `scripts/bootstrap.sh` | count 1 | count 1 (probes-raw.txt) | ✅ |
| P7 CLAUDE.md — `python dashboard.py          # primary` | count 0 (removed) | count 0 (probes-raw.txt) | ✅ |
| Governance commit | `[100017] MACHINE_SETUP v1.2: bellows bootstrap (thread 84)…` | `1c43326` (probes-raw.txt Item 2) | ✅ |
| P7 MACHINE_SETUP — `**Version:** 1.2 (2026-09-02).` | count 1 | count 1 (probes-raw.txt Item 2 correction) | ✅ |
| P7 MACHINE_SETUP — `- **1.2 (2026-09-02):**` | count 1 | count 1 (probes-raw.txt Item 2 correction) | ✅ |
| P7 MACHINE_SETUP — `thread 84; plan bellows-bootstrap` | count 1 | count 1 (probes-raw.txt) | ✅ |
| P7 MACHINE_SETUP — `python3 -m venv .venv && .venv/bin/pip install` | count 0 (removed) | count 0 (probes-raw.txt) | ✅ |
| P7 MACHINE_SETUP — `demands that venv HALTs on the shop` | count 0 (not present) | count 0 (probes-raw.txt) | ✅ |
| Governance status clean | `git -C GOV status --porcelain -- MACHINE_SETUP.md` → empty | empty (probes-raw.txt Item 2) | ✅ |
| QA Run 1 — interpreter | `/opt/homebrew/bin/python3.12` (Python 3.12.14) | `interpreter: /opt/homebrew/bin/python3.12 (Python 3.12.14)` (probes-raw.txt Item 3) | ✅ |
| QA Run 1 — suite | probes-raw.txt Item 3 Run 1, exit=0 | `exit=0`, `VENV_CREATED: YES` (probes-raw.txt Item 3) | ✅ |
| QA Run 2 — idempotence | mtime equal (venv reused), exit=0 | `M1=1788378340, M2=1788378340 → MTIME_EQUAL` (probes-raw.txt) | ✅ |
| QA Run 3 — no-Homebrew interpreter | `/usr/bin/python3` (Python 3.9.6) | `interpreter: /usr/bin/python3 (Python 3.9.6)` (probes-raw.txt Item 3) | ✅ |
| QA Run 3 — pip warning (expected) | `pip version 21.2.4 … consider upgrading` | present in probes-raw.txt | ✅ |
| QA Run 3 — urllib3 warning (expected) | `NotOpenSSLWarning` | present in probes-raw.txt | ✅ |
| QA Run 3 — suite exit | exit=0 | `exit=0` (probes-raw.txt) | ✅ |
| Full suite (canonical venv, worktree) | `full-suite-bellows-bootstrap.txt`, exit=0 | see `full-suite-bellows-bootstrap.txt` → `exit=0` | ✅ |

---

## Operator-Act Note

The venv on each canonical checkout remains the operator's act per machine:

- **Mini (this machine):** run `scripts/bootstrap.sh` once on the canonical bellows checkout. Idempotent — the venv exists, the suite runs; expected result from the canonical checkout (with `config.json`): `1 failed, 1676 passed`, exit 1 by design (the named known failure `tests/test_gates_cross_machine_paths.py::TestCrossMachineReRoot::test_relative_path_unchanged` — a CWD-`config.json` property, not this plan's scope). Record the failing set by name.
- **Air (at its next session):** pull bellows and forge, run `scripts/bootstrap.sh` on each, restart the Air's dashboard under `.venv/bin/python dashboard.py`. Record the Air's failing set by name. Thread 84 closes after that act.
- **Governance push:** the Planner pushes after the pause (as for plan 100016). The governance commit (`1c43326`) is present and not pushed.

---

============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
Evidence folder: /Users/marklehn/Developer/bellows/.bellows-worktrees/100017/knowledge/qa/evidence/bellows-bootstrap-2026-09-02/
Files verified: 2
