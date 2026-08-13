# Executable: the FORWARD NONE-guard — a receipt's literal `NONE` must not append a register row

**Type:** Executable
**Project:** bellows
**Depends on:** `bellows/bellows.py` (the call site — `elif forward_text:` at line 1357, the file's only `elif forward_text`; `_append_forward_row` has exactly one caller — both measured at authoring, re-verify), `lessons-forge/knowledge/FORWARD.md` rows 13–17 (the five junk rows this bug wrote, withdrawn 2026-08-13 by Planner reconciliation `c30dc3f` — the evidence), `bellows/tests/test_bellows.py` (the test home — baseline **180 passed, measured at authoring; re-verify, do not inherit**)
**Created:** 2026-08-13
**Author:** Planner
**Slug:** `forward-none-guard-2026-08-13`
**dispatch_mode:** bellows
**pause_for_verdict:** always
**Priority:** 5
**cycle_tier:** T1
**qa_steps:** 2

⚠️ **ID NOTE — the deposit filename is decided AT DEPOSIT.** `id_sequence` read at deposit, never at authoring.

---

## Why this exists

A plan receipt's `#### Forward Register` section carrying the literal `NONE` (or `NONE.` — or, per the walk-1 verified read, even whitespace-only text) is truthy at `bellows.py:1357`'s `elif forward_text:` guard, so `_append_forward_row` appends it as a register row (the whitespace case as an EMPTY row, via `sanitize_items`' single-item fallback). Measured damage: five junk rows (lessons-forge FORWARD 13–17, one per NONE-receipt since 2026-08-11), withdrawn by Planner reconciliation. **The fix is a boundary guard:** a NONE-form section is logged and skipped — never appended, never ledger-recorded.

**Declared out of scope:** a NONE line mixed among real bullets inside one section (no observed instance; `sanitize_items` untouched); the daemon's other append paths (BACKLOG — a different writer, no observed junk).

⚠️⚠️ **THE RESTART BOUNDARY (the walk-0 clone-diff's load-bearing delta from 367):** the RUNNING daemon holds old code — this guard goes live only at the next daemon restart, which is **the Planner's ops action at an idle window, never the agent's.** Until then the bug remains live and any new junk row is withdrawn by hand. The plan is done when the code and tests land; the restart is recorded at wrap.

---

## Specification

- **Helper** `_forward_text_is_empty_or_none(text)` near `sanitize_items` (bellows.py:1422 area): returns True iff the stripped text is EMPTY, or lowercased with at most one trailing `.` removed equals `none`. ⚠️ **The empty arm is a VERIFIED latent defect, not scope creep:** `sanitize_items` on whitespace-only input returns `[item_text.strip()]` = one empty item (read live at walk 1 — the `if not lines: return [item_text.strip()]` branch), so a whitespace-only section would append an EMPTY register row; the draft's first form claimed the opposite from recall.
- **Call site** (the line measured at 1357): the append branch runs only when `forward_text` is truthy AND not NONE-form; the skip path logs INFO `ledger: forward register empty/NONE — nothing to append` and records nothing (no row, no `record_ledger_write`).
- **Tests** appended to `tests/test_bellows.py`: the helper truth table (`NONE`, `NONE.`, `none`, ` None. `, `   ` (whitespace-only), `` (empty) → True; `NONE and also a real item`, a real bullet → False); a positive control proving `_append_forward_row` with a real item appends exactly one row to a `tmp_path` FORWARD.md. ⚠️ **The honest seam, declared:** the `elif` at the true call site sits inside the daemon's receipt-parse flow and is not unit-drivable without driving the whole parse — the compensating pair is the helper's truth table (the decision logic, fully covered) plus QA Item 2's diff read (the call-site conditional, verified by inspection of the committed hunk). All scratch: no test touches a real register.

---

## Ledger

- **C1 — the guard is at the boundary, not inside the writer.** `_append_forward_row` itself is UNTOUCHED (its other behavior — numbering, sanitize, idempotency — has shipped history; the diff shows only the call-site line and the new helper). *(observer: QA Item 2's diff read)*
- **C2 — the skip path's decision logic is fully covered and the call-site wiring is inspected:** the helper truth table covers every skip/append decision; the call-site conditional is verified from the committed diff (the honest seam — the elif itself is not unit-drivable, declared in the Specification). *(observers: the truth-table tests + QA Item 2)*
- **C3 — counts verified, never assumed:** the 180 baseline and the after-count are re-measured and reported; any unexplained delta HALTs. *(observer: QA Item 1)*
- **C4 — the restart boundary is stated in the receipt** (the fix is inert in the running daemon until the Planner restarts it). *(observer: QA Item 3)*

---

## How to Run This Plan

**Bootstrap prompt:**
```
Read the plan at knowledge/decisions/in-progress-executable-<id>.md (the daemon renames the deposited placeholder on claim). Execute Step 1 ONLY. After completing Step 1, STOP and wait for my confirmation.
```

---

## Scope

- `bellows/bellows.py`
- `bellows/tests/test_bellows.py`
- `bellows/knowledge/development/forward-none-guard-dev-2026-08-13.md`
- `bellows/knowledge/qa/evidence/forward-none-guard-2026-08-13/qa-receipt.md`
- `bellows/knowledge/qa/evidence/forward-none-guard-2026-08-13/pytest-full-raw.txt`

---

## STEP 1 — DEV (the guard + tests)

> **FIRST — post a short visible chat message (1-2 sentences) confirming you are starting.** Do NOT rename this file. ⚠️⚠️ **EXECUTE STEP 1 ONLY, THEN STOP.** ⚠️ **THE WORKTREE RULE:** every git command runs from your cwd; never `-C` into another checkout for a WRITE. **Environment facts:** `grep` is a ugrep shim — `-F` every literal; a zero-count `grep -c` prints `0` and exits 1 (read the count, not the exit code).
>
> **Task A0 — branches, catch-all LAST.** (0) tree shape (toplevel contains `knowledge/decisions`). (1) `git status --porcelain -- bellows.py tests/test_bellows.py` empty. (2) RE-ENTRY key: `git log --oneline -1 -- bellows.py` subject carries this slug → the fix landed; verify the Task C probes on committed content and report complete without re-editing. Anything else → HALT quoting every measurement.
>
> **Task B — implement** per the Specification. ⚠️ Verify the call site before editing: `grep -nF "elif forward_text" bellows.py` — expect exactly one hit (measured at authoring: line 1357; a different line number is fine, a different COUNT needs explaining, not accepting).
>
> **Task C — targeted tests:** `python3 -m pytest tests/test_bellows.py -q` FOREGROUND (never the full suite in DEV). Baseline measured at authoring: 180 passed — re-measure and report before/after; any unexplained delta → HALT. Post-conditions from the live tree: `grep -cF "_forward_text_is_empty_or_none" bellows.py` == 2 (the def + the sole call site — a different count needs explaining, not accepting) and the INFO literal present once.
>
> **Task D — dev note + commit:** `knowledge/development/forward-none-guard-dev-2026-08-13.md` (what shipped, the measured before/after counts, the targeted run's RAW tail). Commit all three files from cwd, pathspec exactly them, subject `[<id from your plan filename>]` + the slug. STOP.
>
> **Deposits:**
> - `bellows/bellows.py`
> - `bellows/tests/test_bellows.py`
> - `bellows/knowledge/development/forward-none-guard-dev-2026-08-13.md`
>
> **Scope:**
> - `bellows/bellows.py`
> - `bellows/tests/test_bellows.py`
> - `bellows/knowledge/development/forward-none-guard-dev-2026-08-13.md`

---

## STEP 2 — QA

> ⚠️⚠️ **PRECONDITION — Step 1 ran as its own dispatch** (`git log --oneline -1 -- bellows.py` shows the Step-1 commit, made before this step and not by this context; otherwise state the independence gap plainly).
>
> **(A) Rule 20 self-check block** — the canonical block from `/Users/marklehn/Developer/GitHub/RULE_20_SELF_CHECK_BLOCK.md` (read live). The receipt carries the canonical header `Rule 20 — QA Self-Check Results` and, on full pass, the canonical verdict line `PASSED — SELF-CHECK PASSED`. `required_evidence_files` = the evidence-directory subset of `## Scope`.
>
> **(B) Deliverable verification — a FAIL is reported, never repaired:**
> - **Item 1 — the FULL suite, FOREGROUND, no Monitor:** `python3 -m pytest tests/ -q`; raw tail into `pytest-full-raw.txt`; report actual totals; any failure is a FAIL with its output.
> - **Item 2 — C1 from the diff:** `git show <step-1 commit> --numstat --format=` and the bellows.py hunks — the only bellows.py changes are the helper and the call-site line; `_append_forward_row`'s body untouched.
> - **Item 3 — C4:** the receipt states the restart boundary verbatim (the running daemon holds old code; the Planner restarts at an idle window).
> - **Item 4 — raw output throughout.**
>
> Commit the receipt + raw file from cwd, pathspec exactly them. STOP.
>
> **Deposits:**
> - `bellows/knowledge/qa/evidence/forward-none-guard-2026-08-13/qa-receipt.md`
> - `bellows/knowledge/qa/evidence/forward-none-guard-2026-08-13/pytest-full-raw.txt`
>
> **Scope:**
> - `bellows/knowledge/qa/evidence/forward-none-guard-2026-08-13/qa-receipt.md`
> - `bellows/knowledge/qa/evidence/forward-none-guard-2026-08-13/pytest-full-raw.txt`

---

## Drafting Cycle

**Tier:** T1 — self-escalated (the target is the daemon's own ledger writer; a wrong guard silently discards REAL forward rows, the inverse damage).

**Walk 0 (v2.7 form, measured):** the five-measurement battery — call site `elif forward_text` count 1 (line 1357 at measurement); `_append_forward_row` count 2 (def + sole caller); `bellows.py` sha256 `d427cc5a5d1bc1e8b83e307f876b5acaf9e6e131e6dbbc00c1aa8fc7b2123277`; test home baseline 180 passed (measured run); newest same-class = 367 (`fdf5dcd`, the last bellows.py fix). **Walk-0 clone-diff verdict vs 367:** form carried (helper + call-site edit + tests + the DEV-targeted/QA-full split); the load-bearing delta OWNED — 367's restart boundary applies identically and is declared in Why; 367's new-test-module choice adapted to appending at the existing forward-append test home. **Scout seat: NOT convened (T1, Planner's call)** — the surface is one guard on one measured call site; the battery and clone-diff cover the walk-0 risk. **Direction verdict: PROCEED.**

**Walk register:** `governance/knowledge/research/walk-register-forward-none-guard-2026-08-13.md` (schema 0.2), committed per phase; open tail per the 0.2 convention.

**Walks:** 3. Fold trajectory 3 → 1 → 0; the headline catch was walk-1's g1 — the draft's whitespace-safety premise was FALSE by live read (`sanitize_items` appends an empty row), the verify-the-premise discipline catching its own author before any cold reader was needed.

- Weak spots:      w1 2 (g1, g2); w2 1 (g4, fold-introduced); w3 0.
- Destruction:     w1 0; w2 0; w3 0.
- Vulnerabilities: w1 1 (g3); w2 0; w3 0.
- Integration:     w1 0; w2 0; w3 0.
- ACID:            w1 0; w2 0; w3 0.

**Closing:** walk 3 DRY — **instruction 0 / record 0**, no residue to enumerate; the last event before deposit is a dry lens pass.
