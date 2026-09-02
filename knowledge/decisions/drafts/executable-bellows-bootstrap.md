# bellows — executable: PROVISIONING — bellows gets its bootstrap (thread 84), the Start runbook names the venv interpreter, and MACHINE_SETUP.md §2 becomes one rule for every machine (v1.2)

**Date:** 2026-09-02 | **Project:** bellows | **Tier:** Small | **Dispatch Mode:** bellows | **cycle_tier:** T1 | **Test Scope:** full (the bellows suite `tests` under the canonical venv from the worktree — the one named known failure — and under the NEW venv in scratch copies of the tree, twice, plus the no-Homebrew variant) | **Execution:** Step 1 (DEV) → Step 2 (QA) | **qa_steps:** 2 | **pause_for_verdict:** always | **known_failures:** 1 | **Priority:** 2

**auto_close:** false

**Slug:** `bellows-bootstrap-2026-09-02`

**Depends on:** the CEO, 2026-09-02 ("Let's resolve 84 … The intention is also so that setting up a new machine will yield the same setup"; "Let's do what we can and put it in place for overnight work"); tuyere thread 84 (*run the forge bootstrap on the shop; reconcile the shop's bellows interpreter with MACHINE_SETUP §2*, 2026-09-02); `Done/executable-100016.md` in forge_lessons (the clone origin by kind — a bootstrap script plus a runbook section plus anchored `MACHINE_SETUP.md` edits by absolute path, TWO REPOSITORIES ONE STEP, `git -C` never `cd`); `MACHINE_SETUP.md` v1.1a (governance `5f5661c`); the multi-machine sketch's third leg (*bellows has NO provisioning at all*). Walk register: `/Users/marklehn/Developer/eluvian-governance/governance/knowledge/research/walk-register-bellows-bootstrap-2026-09-02.md`.

**Tier computed, not judged (§1):** **T-1 fires** (two repositories: bellows and eluvian-governance). **T-3 fires** — a bootstrap is BY DEFINITION run on machines other than the one that tested it (the shop is its first real target); QA runs it here in scratch copies, the operator's act after close runs it on the canonical checkouts. **T-8 fires** (a clone by kind). T-6 no — `CLAUDE.md` is the project's runbook, edited by plans 555 (T1) and 570 without a T-6 claim, and `MACHINE_SETUP.md` is the operator's checklist, not doctrine (100016's ruling; its own History rows are the precedent). T-2/T-5 no (`.venv/` is gitignored, line 8; nothing destructive; the governance edits are one whole-line replacement, the version line and one History row). → **T1: five-lens walk, no panel.**

## Why this exists

The shop's bellows divergence has one cause, and it is a line in `CLAUDE.md`: `## Start` says `python dashboard.py`, the dashboard spawns the daemon with `sys.executable` (`dashboard.py:417`), so the daemon runs under WHATEVER interpreter started the dashboard. On the mini that was the venv's python (measured 2026-09-02: pid 82768 loads `bellows/.venv/lib/python3.12/site-packages`); on the shop it was the system `python3` 3.9, so no venv was ever built there (the Air's cold seat for plan 100011, 2026-09-01) and plan 100011's A0 halted on it. `MACHINE_SETUP.md` §2 records this as an exception ("the mini's fact"). The multi-machine sketch's third leg names the gap plainly: *bellows has NO provisioning at all — no bootstrap, nothing in `CLAUDE.md`, only a `requirements.txt` that nothing installs.* forge_lessons closed its half last night (plan 100016, `scripts/bootstrap.sh`); this plan is the bellows twin, and it turns §2's bellows bullet from a description of two machines into ONE rule a new machine follows.

Measured 2026-09-02 on the mini (walk 0): `requirements.txt` declares six entries (`anthropic watchdog flask requests pyyaml pytest`), all importable from the live venv; the live suite from the canonical checkout is `1 failed, 1676 passed`, the failure `tests/test_gates_cross_machine_paths.py::TestCrossMachineReRoot::test_relative_path_unchanged` (a CWD-`config.json` property — the baton's carried item, not this plan's); a fresh 3.12 venv from `requirements.txt` builds in ~7s (pytest 9.1.1, anthropic 1.3.0) and a fresh 3.9 venv from the same file builds in ~11s with pip's "version 21.2.4 … consider upgrading" WARNING and urllib3's `NotOpenSSLWarning` on stderr (pytest 8.4.2, anthropic 0.125.0) — both import all six. ⚠️ The suite's `TestDbPath` asserts the word `bellows` appears in the resolved bellows root, so a scratch copy MUST live in a directory whose basename is `bellows` (a copy named otherwise fails exactly that one test — measured, both interpreters).

## What this plan does

**In the bellows worktree:**
- **F1 — NEW `scripts/bootstrap.sh`** (executable; the exact text below): creates `.venv` with `python3.12` where present else `python3`, prints the interpreter and its version, installs `requirements.txt`, runs `tests` once. Its exit is the suite's exit.
- **F2 — `CLAUDE.md` `## Start` and `## Status`, three anchored lines (each count 1):**
  - F2a: the line `python dashboard.py          # primary — full-screen TUI that owns the daemon` (line 5) → `.venv/bin/python dashboard.py   # primary — full-screen TUI that owns the daemon; the daemon inherits THIS interpreter`
  - F2b: the line `python bellows.py             # headless daemon (no TUI)` (line 6) → TWO lines: `.venv/bin/python bellows.py     # headless daemon (no TUI)` then `scripts/bootstrap.sh              # first, on a new machine: build .venv from requirements.txt and run the suite once (MACHINE_SETUP.md §2, thread 84)`
  - F2c: the line `python status.py` (line 15) → `.venv/bin/python status.py`

**In the governance checkout, by absolute path (`GOV=/Users/marklehn/Developer/eluvian-governance`), every anchor count 1 at v1.1a (`6861ab745885cd8b`):**
- **G1 — §2 bellows bullet, the WHOLE line replaced:** anchor `- `bellows`: `python3 -m venv .venv && .venv/bin/pip install -r requirements.txt`.` (the line's start, line 27; the script matches the whole line beginning with it — count 1 — and replaces that whole line) → `- `bellows`: `scripts/bootstrap.sh` (thread 84; plan bellows-bootstrap, 2026-09-02) creates `.venv` with `python3.12` where present else `python3`, installs `requirements.txt` (six entries, measured) and runs `tests` once; its exit is the suite's, so a known failure exits 1 by design — record the failing set by name. **Every bellows tool, test and the daemon run under `bellows/.venv/bin/python` on every machine: start the dashboard as `.venv/bin/python dashboard.py`.** The daemon inherits the dashboard's interpreter (`dashboard.py` spawns it with `sys.executable`), so a dashboard started under the system `python3` yields a daemon with no venv — that was the shop's state from its first daemon onward, and thread 84's operator act (owed at this writing) is what ends it (measured 2026-09-01 by the Air's cold seat for plan 100011: no `.venv`, system `python3` 3.9 with `pytest`; 100011's A0 halted there). ⚠️ The system `python3` on a fresh mac has no `pytest` and no `yaml`. Measured 2026-08-31: a venv missing `pytest` (declared in `requirements.txt`, never installed) hid 11 suite failures for an unknown period — §7's importability assert is the check.`
- **G2 — the version line:** anchor `**Version:** 1.1 (2026-09-02).` (count 1) → `**Version:** 1.2 (2026-09-02).`
- **G3 — the History row:** anchor `## History` (count 1, the heading line) → the same heading followed by a new first row: `- **1.2 (2026-09-02):** bellows gains its bootstrap (thread 84; §2's bellows bullet rewritten as one rule for every machine — the venv interpreter for tools, tests AND the daemon, the dashboard started under it). Sources: plan bellows-bootstrap (the twin of 100016), the mini's daemon measured under the venv (pid 82768), the Air's shop measurement for 100011; `walk-register-bellows-bootstrap-2026-09-02.md`.`

**`scripts/bootstrap.sh`, exact text:**
```
#!/usr/bin/env bash
# bellows bootstrap — thread 84 / MACHINE_SETUP.md §2 (plan bellows-bootstrap, 2026-09-02).
# Creates .venv with the newest python3.12 on PATH (else python3), installs requirements.txt,
# and runs the suite once. Idempotent: an existing .venv is reused. Run from anywhere.
# The daemon inherits the DASHBOARD's interpreter: start it as .venv/bin/python dashboard.py.
set -euo pipefail
cd "$(dirname "$0")/.."
PY="$(command -v python3.12 || command -v python3)"
echo "interpreter: $PY ($("$PY" --version 2>&1))"
[ -x .venv/bin/python ] || "$PY" -m venv .venv
.venv/bin/python -m pip install -q -r requirements.txt
echo "venv: $(pwd)/.venv ($(.venv/bin/python --version 2>&1))"
exec .venv/bin/python -m pytest tests -q -p no:cacheprovider
```

## What this plan does NOT do

- **Does not create or rebuild the venv on any canonical checkout.** `.venv/` is per-machine (gitignored); the operator's act after close runs `scripts/bootstrap.sh` once on the mini (the venv exists — idempotent, the suite runs; expected there: `1 failed, 1676 passed` with the named known failure and exit 1, by the script's own rule, until that failure is fixed) and, at the shop's next session, on the shop: pull, run BOTH bootstraps (bellows, forge), restart the shop's dashboard under `.venv/bin/python` (a TUI act, the CEO's), record the shop's failing set by name. Thread 84 closes at the keyboard after that act.
- Does not touch `dashboard.py`, `bellows.py`, the daemon, doctrine, or `MACHINE_SETUP.md` beyond the three anchored edits. Does not add an interpreter guard to the dashboard (a candidate for its own thread). Does not fix the named known failure. Does not push the governance commit (the Planner pushes after the pause, as for 100016).
- Does not resolve thread 84 in tuyere (thread closure is a keyboard act, after the shop's operator act).

## MUST-PRESERVE

- ⚠️ **TWO REPOSITORIES, ONE STEP.** The bellows edits happen in your worktree; the governance edits happen in the LIVE governance checkout at `$GOV` by absolute path — `git -C "$GOV"` for every git act there, never `cd`. Before touching it: `git -C "$GOV" status --porcelain -- MACHINE_SETUP.md` must be EMPTY and `shasum` of the file must equal P1's — a dirty or moved file is a HALT. Commit there by explicit pathspec; do not push.
- **Every anchor count-asserted BEFORE editing**, with a script (a heredoc'd Python is fine), never a blind replace; F2a/F2c/G2 are whole-line replacements, F2b is a one-line-to-two-lines replacement, G1 is a whole-line replacement, G3 is an insertion after a heading.
- **The bootstrap is idempotent and exits nonzero on any failure** (`set -euo pipefail`; the suite's exit is the script's exit via `exec`).
- **Scratch copies live in a directory whose basename is `bellows`** (the `TestDbPath` property, measured) — never in the worktree, never on the canonical checkout.
- **The bootstrap needs PyPI reachable** (`pip install` from `requirements.txt`; measured reachable on this machine at walk 0, ~7s under 3.12). Offline, `set -e` ends the script at the install with pip's error on stderr and a nonzero exit — a HALT with its cause visible, never a silent half-venv.
- **`known_failures: 1`, named:** `tests/test_gates_cross_machine_paths.py::TestCrossMachineReRoot::test_relative_path_unchanged` from the worktree under the canonical venv. Any OTHER failure, anywhere, is a HALT/Critical.

## Numbers discipline — the pins DEV re-derives (measured 2026-09-02 by the Planner)

| pin | what | value | how |
|---|---|---|---|
| P1 | **`GOV_SHA`** — `MACHINE_SETUP.md` at v1.1a | `6861ab745885cd8b` | `shasum -a 256 "$GOV/MACHINE_SETUP.md" \| cut -c1-16` |
| P2 | **`CLAUDE_SHA`** — bellows `CLAUDE.md` | `ecd39219110fa814` | same, in the worktree |
| P3 | **`REQ`** — `requirements.txt` sha and entries | `d3bb0209d85b16a7`; six lines: `anthropic watchdog flask requests pyyaml pytest`; `.venv/` in `.gitignore` line 8 | `shasum`; `cat requirements.txt`; `grep -n venv .gitignore` |
| P4 | **`ANCHORS`** — F2a, F2b, F2c, G1, G2, G3 | **6**, each count 1 | `/usr/bin/grep -cF -- '<anchor>' <file>` |
| P5 | **`SUITE`** — from the worktree under the canonical venv | `1 failed, 1676 passed`; the one failure named above | `BPY -m pytest tests -q -p no:cacheprovider` |
| P6 | **`INTERPRETERS`** | `python3` → `/usr/bin/python3`, `Python 3.9.6`; `python3.12` → `/opt/homebrew/bin/python3.12`, `Python 3.12.14` | `command -v python3 python3.12; python3 --version; python3.12 --version` |
| P7 | **`TOKENS`** post-edit | in `CLAUDE.md`: `.venv/bin/python dashboard.py` 1 · `.venv/bin/python bellows.py` 1 · `.venv/bin/python status.py` 1 · `scripts/bootstrap.sh` 1 · `python dashboard.py          # primary` 0; in `MACHINE_SETUP.md`: `**Version:** 1.2 (2026-09-02).` 1 · `- **1.2 (2026-09-02):**` 1 · `thread 84; plan bellows-bootstrap` 1 · `demands that venv HALTs on the shop` 0 · `python3 -m venv .venv && .venv/bin/pip install` 0 | `/usr/bin/grep -cF` |

## STEP 1 — DEV

> **FIRST — post a short visible chat message (1–2 sentences).** Do NOT rename this file. You are the bellows Developer.
>
> ⛔ **A0 — resolve BOTH roots in one compound and state both in the dev log:** `cd "$(git rev-parse --show-toplevel)" && [ -f bellows.py ] && [ -f requirements.txt ] && [ -d tests ] && echo TREE_OK` — HALT unless TREE_OK; `GOV=/Users/marklehn/Developer/eluvian-governance; [ -f "$GOV/MACHINE_SETUP.md" ] && [ -f "$GOV/COMPANY.md" ] && echo GOV_OK` — HALT unless GOV_OK. Re-derive `GOV` in every compound. `BPY=/Users/marklehn/Developer/bellows/.venv/bin/python` (the canonical venv; re-derive per compound).
>
> ⛔ **A1 — re-derive P1–P6; state each; a mismatch is a HALT quoting both.** P5 is a full suite run from the worktree under `$BPY` (about a minute): the summary line and the one named failure; a second failure or a different name is a HALT. Then `git -C "$GOV" status --porcelain -- MACHINE_SETUP.md` → EMPTY (else HALT: someone is editing it).
>
> **A2 — F1:** write `scripts/bootstrap.sh` EXACTLY as given (heredoc with a quoted delimiter so nothing expands), `chmod +x scripts/bootstrap.sh`, `bash -n scripts/bootstrap.sh` → exit 0. **F2:** the three `CLAUDE.md` edits by one script that asserts each anchor's count (1) before applying; then the five `CLAUDE.md` tokens of P7.
>
> **A3 — G1–G3 at `$GOV/MACHINE_SETUP.md`** with one script that asserts each of the three anchor counts (1) before applying, applies all three, then asserts the five `MACHINE_SETUP.md` tokens of P7. Then `git -C "$GOV" diff --stat -- MACHINE_SETUP.md` (state the line counts) and `git -C "$GOV" add MACHINE_SETUP.md && git -C "$GOV" commit -m "[<id from your plan filename>] MACHINE_SETUP v1.2: bellows bootstrap (thread 84) — one interpreter rule for every machine" -- MACHINE_SETUP.md`; `git -C "$GOV" log --oneline -1 -- MACHINE_SETUP.md` → that commit. Do NOT push.
>
> **A4 — prove the bootstrap on a SCRATCH copy** (never on the worktree, never on the canonical checkout; the copy's directory MUST be named `bellows`): `S=/tmp/bb-scratch-$(basename "$(git rev-parse --show-toplevel)")/bellows; rm -rf "$(dirname "$S")"; mkdir -p "$S"; git archive HEAD | tar -x -C "$S"; cp scripts/bootstrap.sh "$S/scripts/bootstrap.sh"; bash "$S/scripts/bootstrap.sh" > "$S/../run1.txt" 2>&1; echo "exit=$?"` → in `run1.txt`: the `interpreter:` line naming `/opt/homebrew/bin/python3.12`, a `venv:` line, the suite summary `1676 passed, 1 skipped` (a `git archive` tree has no `config.json`, so the canonical checkout's known failure does not occur in scratch — measured at walk 0, both interpreters; any `failed` here is a HALT) and `exit=0`; `test -x "$S/.venv/bin/python" && echo VENV_CREATED`. Then `M1=$(stat -f %m "$S/.venv/bin/python")`; run it a SECOND time into `run2.txt` (idempotence); `M2=$(stat -f %m "$S/.venv/bin/python")`; state `M1`, `M2` → EQUAL (the venv was reused, not rebuilt — the `venv:` line alone cannot show this, its interpreter string is identical either way), and `run2.txt` again `1676 passed, 1 skipped`, `exit=0`. Then P5 again from your worktree under `$BPY` → unchanged (the canonical venv is untouched by this plan).
>
> **A5 — dev-log + commit by explicit pathspec.** `knowledge/development/dev-log-bellows-bootstrap-2026-09-02.md`: both roots, A1's pins, the six anchor counts, P7, the governance commit hash, A4's raw lines (both runs' `interpreter:`/`venv:`/summary/`exit=` lines). `git add scripts/bootstrap.sh CLAUDE.md knowledge/development/dev-log-bellows-bootstrap-2026-09-02.md && git commit -m "[<id>] bellows bootstrap (thread 84): scripts/bootstrap.sh + CLAUDE.md Start under the venv; MACHINE_SETUP v1.2 committed in governance" -- scripts/bootstrap.sh CLAUDE.md knowledge/development/dev-log-bellows-bootstrap-2026-09-02.md`. `git status --short` → empty. STOP.
>
> **Deposits:**
> - `knowledge/development/dev-log-bellows-bootstrap-2026-09-02.md`
> - `scripts/bootstrap.sh`
> - `CLAUDE.md`
> - `/Users/marklehn/Developer/eluvian-governance/MACHINE_SETUP.md`
>
> **Scope:**
> - `knowledge/development/dev-log-bellows-bootstrap-2026-09-02.md`
> - `scripts/bootstrap.sh`
> - `CLAUDE.md`
> - `/Users/marklehn/Developer/eluvian-governance/MACHINE_SETUP.md`

## STEP 2 — QA

> **Step 1's Receipt status must be `Status: Complete`.** Anything else → HALT. **FIRST — post a short visible chat message.** You are the bellows QA agent. `cd "$(git rev-parse --show-toplevel)"`; `GOV=/Users/marklehn/Developer/eluvian-governance`; `BPY=/Users/marklehn/Developer/bellows/.venv/bin/python` — re-derive both per compound.
>
> **(A) Rule 20 self-check** — the canonical block at the path the dispatcher's mandate names (this machine's `RULE_20_SELF_CHECK_BLOCK.md`; quote the path you were handed). Run with:
> - `plan_slug`: `bellows-bootstrap-2026-09-02`
> - `qa_report_path`: `"$(pwd)/knowledge/qa/evidence/bellows-bootstrap-2026-09-02/qa-receipt.md"`
> - `evidence_dir`: `"$(pwd)/knowledge/qa/evidence/bellows-bootstrap-2026-09-02"`
> - `required_evidence_files`: `["probes-raw.txt", "full-suite-bellows-bootstrap.txt"]`
>
> **(B) Items — raw output appended to `probes-raw.txt` (`mkdir -p` the evidence dir first):**
> - **Item 1 — the bellows commit is what the plan says:** `git show --stat HEAD --format=` lists exactly the three bellows paths; `test -x scripts/bootstrap.sh && echo EXEC_BIT`; `bash -n scripts/bootstrap.sh; echo "syntax=$?"` → 0; the five `CLAUDE.md` tokens of P7 with their counts.
> - **Item 2 — the governance commit and tokens (P7):** `git -C "$GOV" log --oneline -1 -- MACHINE_SETUP.md` (the `[<id>]` commit); the five `MACHINE_SETUP.md` greps of P7, each with its count; `git -C "$GOV" status --porcelain -- MACHINE_SETUP.md` → EMPTY.
> - **Item 3 — the bootstrap, by a second pair of hands (T-3):** A4 repeated in your OWN scratch copy (`/tmp/bb-qa-$(basename "$(git rev-parse --show-toplevel)")/bellows` — the basename `bellows` is load-bearing), twice: first run → `interpreter:` naming `/opt/homebrew/bin/python3.12`, `1676 passed, 1 skipped`, `exit=0`, `VENV_CREATED`; capture `stat -f %m` of `.venv/bin/python`, second run → `1676 passed, 1 skipped`, `exit=0`, the mtime EQUAL to the captured one. Then the adversarial variant: `PATH=/usr/bin:/bin bash "<a THIRD scratch copy>/scripts/bootstrap.sh"` (no Homebrew on PATH) → the `interpreter:` line names `/usr/bin/python3` (3.9.6), pip's "version 21.2.4 … consider upgrading" WARNING and urllib3's `NotOpenSSLWarning` on stderr (both expected under 3.9 — measured at walk 0, not failures), and the suite runs under the 3.9 venv's pytest 8.4.2 to `1676 passed, 1 skipped, 1 warning` with `exit=0` (measured at walk 0 by running this exact script under `PATH=/usr/bin:/bin`) — quote the lines.
> - **Item 4 — the full-suite file:** `"$BPY" -m pytest tests -q -p no:cacheprovider > knowledge/qa/evidence/bellows-bootstrap-2026-09-02/full-suite-bellows-bootstrap.txt 2>&1; echo "exit=$?" >> knowledge/qa/evidence/bellows-bootstrap-2026-09-02/full-suite-bellows-bootstrap.txt` → `1 failed, 1676 passed`, the one named known failure, `exit=1` (the canonical venv, untouched by this plan; the failure is the baton's carried item).
>
> **(C) The report** `qa-receipt.md`: the verification table, the operator-act note (the venv on the canonical checkouts is still the operator's act per machine — the mini's bootstrap run, the shop's pull + both bootstraps + dashboard restart under the venv; the Planner pushes governance), the Rule 20 stdout APPENDED. Commit: `git add knowledge/qa/evidence/bellows-bootstrap-2026-09-02/ && git commit -m "[<id>] QA: bellows bootstrap proven twice on scratch + no-Homebrew variant; MACHINE_SETUP v1.2 tokens" -- knowledge/qa/evidence/bellows-bootstrap-2026-09-02/`. STOP.
>
> **Deposits:**
> - `knowledge/qa/evidence/bellows-bootstrap-2026-09-02/qa-receipt.md`
> - `knowledge/qa/evidence/bellows-bootstrap-2026-09-02/probes-raw.txt`
> - `knowledge/qa/evidence/bellows-bootstrap-2026-09-02/full-suite-bellows-bootstrap.txt`
>
> **Scope:**
> - `knowledge/qa/evidence/bellows-bootstrap-2026-09-02/qa-receipt.md`
> - `knowledge/qa/evidence/bellows-bootstrap-2026-09-02/probes-raw.txt`
> - `knowledge/qa/evidence/bellows-bootstrap-2026-09-02/full-suite-bellows-bootstrap.txt`

Rule 20 banner (byte-exact, produced by RUNNING the canonical block — never hand-authored):

```
============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
```

---

## Drafting Cycle

**Tier:** T1 — T-1 (two repos), T-3 (a bootstrap runs on other machines by definition; the shop is its first real target), T-8 fire; no T2 trigger. Five-lens walk, no panel.

**Walk register:** /Users/marklehn/Developer/eluvian-governance/governance/knowledge/research/walk-register-bellows-bootstrap-2026-09-02.md

**Walk 0 (context pin, measured):** the two target shas and the requirements sha; six anchors counted (1 each) with line, length and whole-line/prefix noted; the three replaced tokens counted file-wide (1 each); last writers of every target line with their lifecycle states; the live suite from the canonical checkout (one named failure); the daemon's interpreter proven by `lsof` on the live pid and `dashboard.py`'s spawn read at source; fresh venvs built from `requirements.txt` under 3.12 and 3.9 in scratch, all six entries importing; the suite in scratch trees under both — which found that the copy's directory NAME is load-bearing (`TestDbPath`); the exact script executed three ways (twice normally with the venv's mtime equal, once without Homebrew on PATH); 100016's two-repositories-one-step shape read at source; the consumer dry-run (§2.0) on the register's walk-0 line — class assigner `shop-infra`, extractor per step, the QA test gate's count arithmetic read at source.

**Direction verdict (after walk 1): PROCEED.** Tested: the premise (the daemon inherits the dashboard's interpreter — `sys.executable` at the spawn site and the live pid's site-packages; the shop's divergence has that one cause, and the sketch's third leg names the missing bootstrap), the mechanism (one script proven by execution three ways in scratch, three runbook lines and three anchored governance edits by absolute path in 100016's shape), the scope (the venv on canonical checkouts stays the operator's act per machine; the governance push stays the Planner's; the dashboard guard and the align-hook assert stay outside, named).

**Walks:**
- Weak spots:          w1 4 folded — instruction 4 / record 0 (the plan pointed the executing agent at the register for its expected suite lines, twice — the measured lines now stated; the idempotence probe named no capture step for the mtime it compares — stated, measured equal; the no-Homebrew variant's suite outcome was unmeasured for the script itself — measured, stated; a governance sentence claimed a future act as history — rephrased as owed)
- Destruction:         w1 dry — the one removal is bounded to a scratch path the compound itself built under /tmp; one whole-line replacement, the version line and one inserted row in the governance file; one runbook line becomes two; the canonical venv is never touched
- Vulnerabilities:     w1 1 folded — instruction 1 / record 0 (3.1 env: PyPI reachability named as a precondition with the offline failure shape — `set -e` ends the script at the install, cause on stderr, nonzero; the no-interpreter branch measured loud too)
- Integration-record:  w1 1 folded — instruction 0 / record 1 (4.4: the operator's post-close run on the CANONICAL mini checkout exits 1 by the script's own rule — the named known failure — and the record said only "the suite runs"; the expectation stated)
- ACID:                w1 dry — governance commit before the bellows commit, each by explicit pathspec; a HALT between leaves a committed-but-unpushed governance change visible at the pause
- **Walk 1 total: 6 findings, 6 folded — instruction 5 / record 1; 0 of 6 fold-introduced.**

- Weak spots:          w2 1 folded — instruction 1 / record 0 (1.2: a P7 "0 after" token for the governance file used a straight apostrophe where the file has a curly one, so it counted 0 BEFORE the edit — a post-condition that could not fail; found by executing all ten P7 tokens against the pre-edit files; replaced by a token measured 1 before and 0 after)
- Destruction:         w2 dry — instruction 0 / record 0 — unchanged
- Vulnerabilities:     w2 dry — instruction 0 / record 0 — the A4 compound re-read: the copy lands in a directory the archive carries; the exit code is read from an unpiped command
- Integration-record:  w2 dry — instruction 0 / record 0 — the block's geometry is the parent's; no gate-matching string in it
- ACID:                w2 dry — instruction 0 / record 0 — unchanged
- **Walk 2 total: 1 finding, 1 folded — instruction 1 / record 0; 0 of 1 fold-introduced.**
- Weak spots:          w3 dry — instruction 0 / record 0 — the folded P7 row re-read and its token re-measured (1 in the pre-edit file, 0 in the plan's replacement texts); the Cycle Log covered
- Destruction:         w3 dry — instruction 0 / record 0 — unchanged
- Vulnerabilities:     w3 dry — instruction 0 / record 0 — unchanged
- Integration-record:  w3 dry — instruction 0 / record 0 — `propagation_check` clean; the manifest below is the emitter's, spliced at the freeze
- ACID:                w3 dry — instruction 0 / record 0 — unchanged
- **Walk 3 total: 0 findings — instruction 0 / record 0, ALL FIVE LENSES DRY.** Instruction series 5 → 1 → 0.

**Conformance (§5):** first run at walk 0 (shape-stability, on v0) and re-run after each fold round and at the freeze: `plan_lint` exit 0 / 0 FAIL at the faithful mirror — expected WARN set (o2)×6 (project-relative deposits — the six worktree-relative entries; the absolute governance path is not one) and the two advisory "mentions tests but declares no test scope" lines (the Test Scope header names the suite; the heuristic keys on a phrase it does not find — advisory, left as is); `cycle_check` BAR_MET; `fold_check` baseline re-saved at each intended change with a note; `propagation_check` exit 0.

**Closing:** ✅ **BAR MET — walk 3 dry (all five lenses) after walk 1's six folds and walk 2's one; T1, no panel owed, none convened.** Substrate present (the register's rows entered at each phase from captured output, two of them marked late with their evidence, the file committed at the freeze — not per phase, and the record says so; `fold_check` baseline). The closing-record re-read (§2.7) ran against this block, the register and the emitted manifest at the freeze.

**Fold-and-deposit exactly once.**

## Cycle Manifest
tier: T1
target: scripts/bootstrap.sh, CLAUDE.md, /Users/marklehn/Developer/eluvian-governance/MACHINE_SETUP.md
class: shop-infra
reads: /Users/marklehn/Developer/bellows/requirements.txt, /Users/marklehn/Developer/bellows/.gitignore, /Users/marklehn/Developer/bellows/CLAUDE.md, /Users/marklehn/Developer/bellows/dashboard.py, /Users/marklehn/Developer/eluvian-governance/MACHINE_SETUP.md, /Users/marklehn/Developer/forge_lessons/knowledge/decisions/Done/executable-100016.md
writes: scripts/bootstrap.sh, CLAUDE.md, /Users/marklehn/Developer/eluvian-governance/MACHINE_SETUP.md, knowledge/development/dev-log-bellows-bootstrap-2026-09-02.md, knowledge/qa/evidence/bellows-bootstrap-2026-09-02/qa-receipt.md, knowledge/qa/evidence/bellows-bootstrap-2026-09-02/probes-raw.txt, knowledge/qa/evidence/bellows-bootstrap-2026-09-02/full-suite-bellows-bootstrap.txt
open_forks: an interpreter guard in dashboard.py (refuse or warn when not under the venv — a bellows code change, its own thread); the align hook's requirements-importable assert (the sketch's missing row — its own thread); whether the shop's dashboard restart under the venv should be a tuyere action rather than a keyboard act
walks: 3
yields: 5, 1, 0
validation: cycle_check=BAR_MET, plan_lint=0_FAIL, fold_check=PASS
coherence: 3/3 walks have register rows
