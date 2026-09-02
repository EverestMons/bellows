# Dev Log — bellows-bootstrap-2026-09-02 (plan 100017, Step 1 DEV)

**Date:** 2026-09-02 | **Developer:** bellows agent (Step 1 DEV)

## A0 — Both Roots Verified

- **Bellows worktree root:** `/Users/marklehn/Developer/bellows/.bellows-worktrees/100017` — `bellows.py`, `requirements.txt`, `tests/` present → `TREE_OK`
- **Governance root:** `/Users/marklehn/Developer/eluvian-governance` — `MACHINE_SETUP.md`, `COMPANY.md` present → `GOV_OK`
- `BPY=/Users/marklehn/Developer/bellows/.venv/bin/python` (canonical venv, re-derived each compound)

## A1 — Pins Re-derived

| pin | value | match |
|-----|-------|-------|
| P1 GOV_SHA | `6861ab745885cd8b` | ✓ matches plan |
| P2 CLAUDE_SHA | `ecd39219110fa814` | ✓ matches plan |
| P3 REQ sha | `d3bb0209d85b16a7` | ✓ matches plan |
| P3 entries | `anthropic watchdog flask requests pyyaml pytest` (6 lines) | ✓ |
| P3 .gitignore | `.venv/` at line 8 | ✓ |
| P4 F2a | 1 | ✓ |
| P4 F2b | 1 | ✓ |
| P4 F2c | 1 | ✓ |
| P4 G1 | 1 (via `/usr/bin/grep -cF`) | ✓ |
| P4 G2 | 1 | ✓ |
| P4 G3 | 1 | ✓ |
| P5 SUITE | `1676 passed, 1 skipped`, exit 0 | ✓ matches plan |
| P6 python3 | `/usr/bin/python3`, Python 3.9.6 | ✓ |
| P6 python3.12 | `/opt/homebrew/bin/python3.12`, Python 3.12.14 | ✓ |

`git -C "$GOV" status --porcelain -- MACHINE_SETUP.md` → EMPTY ✓

Note: P4 G1 initially returned 0 when `grep` resolved to `ugrep`; `/usr/bin/grep -cF` (as the plan specifies) returns 1 correctly. The grep pattern uses backticks inside single quotes — ugrep mis-parses the leading `-` as an option flag.

## A2 — F1 and F2 Applied

**F1 — `scripts/bootstrap.sh`:** written via quoted heredoc (no expansion), `chmod +x`, `bash -n` → exit 0.

**F2 — `CLAUDE.md` edits (Python script, anchor-count assertions before each):**
- F2a anchor count: 1 → replaced; post-edit `.venv/bin/python dashboard.py` count: 1 ✓
- F2b anchor count: 1 → replaced (one line → two lines); post-edit `.venv/bin/python bellows.py` count: 1, `scripts/bootstrap.sh` count: 1 ✓
- F2c anchor count: 1 → replaced; post-edit `.venv/bin/python status.py` count: 1 ✓
- Post-edit `python dashboard.py          # primary` count: 0 ✓

**P7 CLAUDE.md tokens (post-edit):**

| token | expected | actual |
|-------|----------|--------|
| `.venv/bin/python dashboard.py` | 1 | 1 ✓ |
| `.venv/bin/python bellows.py` | 1 | 1 ✓ |
| `.venv/bin/python status.py` | 1 | 1 ✓ |
| `scripts/bootstrap.sh` | 1 | 1 ✓ |
| `python dashboard.py          # primary` | 0 | 0 ✓ |

## A3 — G1–G3 Applied and Governance Committed

**MACHINE_SETUP.md edits (Python script, anchor-count assertions):**
- G1 anchor count: 1 → whole §2 bellows line replaced ✓
- G2 anchor count: 1 → `1.1 (2026-09-02)` → `1.2 (2026-09-02)` ✓
- G3 anchor count: 1 → new 1.2 History row inserted after `## History` heading ✓

**P7 MACHINE_SETUP.md tokens (post-edit):**

| token | expected | actual |
|-------|----------|--------|
| `**Version:** 1.2 (2026-09-02).` | 1 | 1 ✓ |
| `- **1.2 (2026-09-02):**` | 1 | 1 ✓ |
| `thread 84; plan bellows-bootstrap` | 1 | 1 ✓ |
| `python3 -m venv .venv && .venv/bin/pip install` | 0 | 0 ✓ |

`git -C "$GOV" diff --stat -- MACHINE_SETUP.md` → `1 file changed, 3 insertions(+), 2 deletions(-)`

**Governance commit:** `1c43326 [100017] MACHINE_SETUP v1.2: bellows bootstrap (thread 84) — one interpreter rule for every machine`

Not pushed (Planner pushes at pause).

## A4 — Bootstrap Proven on Scratch Copies

**Scratch directory:** `/tmp/bb-scratch-100017/bellows` (basename `bellows` — load-bearing for TestDbPath)

**Run 1 (python3.12 path):**
```
interpreter: /opt/homebrew/bin/python3.12 (Python 3.12.14)
venv: /tmp/bb-scratch-100017/bellows/.venv (Python 3.12.14)
1676 passed, 1 skipped in 50.71s
exit=0
VENV_CREATED
```

**Run 2 (idempotence):**
```
interpreter: /opt/homebrew/bin/python3.12 (Python 3.12.14)
venv: /tmp/bb-scratch-100017/bellows/.venv (Python 3.12.14)
1676 passed, 1 skipped in 48.45s
exit=0
M1=1788377784, M2=1788377784 → MTIME_EQUAL (venv reused, not rebuilt)
```

**Run 3 — No-Homebrew adversarial (PATH=/usr/bin:/bin), third scratch copy `/tmp/bb-scratch3-100017/bellows`:**
```
interpreter: /usr/bin/python3 (Python 3.9.6)
venv: /tmp/bb-scratch3-100017/bellows/.venv (Python 3.9.6)
WARNING: You are using pip version 21.2.4; however, version 26.0.1 is available. [expected]
NotOpenSSLWarning: urllib3 v2 only supports OpenSSL 1.1.1+ ... [expected]
1676 passed, 1 skipped, 1 warning in 65.10s
exit=0
```

**P5 re-check from worktree (canonical venv untouched):** `1676 passed, 1 skipped`, exit 0 ✓
