# bellows — executable: R2 actuation — wrap_check gains the fail-open registry information line (subprocess seam, never suppressing) + the ritual wrap-record step

**Date:** 2026-08-26 | **Project:** bellows | **Tier:** Small | **Dispatch Mode:** bellows | **cycle_tier:** T2 | **Test Scope:** targeted (bellows wrap-hook tests) + full suite at QA | **Execution:** Step 1 (DEV) → Step 2 (QA) | **qa_steps:** 2 | **known_failures:** 0 | **Priority:** 2

**auto_close:** false
**pause_for_verdict:** always

**Depends on:** tuyere `Done/executable-3.md` (the machine registry — `session_wraps` table + `tuyere/wraps.py` CLI, BUILT 2026-08-26) and `knowledge/research/machine-registry-rulings-2026-08-26.md` **R2** (hybrid wrap truth; consumers FAIL-OPEN when the DB is unreachable), both in the tuyere repo. **Clone origin BY KIND:** this plan's own sibling `executable-tuyere-machine-registry` (Done as tuyere exec-3) — same authoring session, same T2 panel form; the structural machinery (A0 sha-HALT, per-step Deposits with the QA report FIRST and a named `.txt`, verify-before-commit, pathspec commits) is carried WITH the two QA-gate corrections that plan's dispatch measured (per-step Deposits blocks; the named pytest `.txt` — the codified `.txt` gate class, honored here). **Dispatch geometry (stated):** this plan deposits into `bellows/knowledge/decisions/` COMMITTED AND PUSHED from the mini; the mini's daemon does not watch bellows, so the SHOP machine's daemon discovers it on that machine's next pull — arriving WITHOUT local clearance, it auto-HOLDs `no_clearance` (E2), and the shop CEO releases via the gated clear tool. Verdicts belong to the dispatching machine's Planner. ⚠️ `wrap_check.py` is shared with the wrap-lock arc — this deposit IS the coordination artifact; nothing here dispatches until that machine's human releases it.

## Why this exists

R2 ruled hybrid wrap truth and exec-3 built the substrate — table, CLI — explicitly BUILT-NOT-WIRED. The phantom-debt class stays open until a consumer reads the registry: measured 2026-08-24, a `[3b]` debt reported against a baton 20 commits stale, indistinguishable from genuine local debt without a manual fetch. This plan wires the read the SAFE way: the debt report gains an INFORMATIONAL registry line; no check is suppressed.

## What this plan does NOT do

- **It suppresses NOTHING.** The registry read never removes, downgrades, or short-circuits a failure — genuine local debt (a machine whose own prior session did not wrap) reports exactly as today. The information line tells the operator that wraps were recorded today elsewhere, so the scope law's "satisfied elsewhere → fetch and stop" decision is made on fresh shared truth instead of a manual fetch. ⚠️ Stated v0 design decision: informational-only was chosen over suppression because same-day wraps from OTHER machines cannot prove THIS machine's prior session wrapped — suppression would mask genuine debt (the 2026-08-25 mini case: shop had wrapped, mini's debt was real).
- **No psycopg in the hook.** The hooks run under system `/usr/bin/python3`; the read is a SUBPROCESS of the tuyere CLI (`tuyere.wraps list`) under the tuyere venv — the CLI is the only DB client, and every failure branch (no checkout, no venv, timeout, nonzero exit, unparseable output) returns None silently: R2's fail-open, honored structurally.
- **No schema, no tuyere code, no doctrine-file edits.** FOUR bellows files: wrap_check.py, wrap.md, the new test file, and requirements.txt (the pytest pin — S3-3/S4-4).
- ⚠️ **STATED SUPERSESSION of the ruling's closure clause (S2-1/S2-2, panel-measured):** R2's text promises the read "closes the stale-local-tree phantom-debt class" and the census A4(c) marks that row "Closed" — both premised on SUBSTITUTION (reading Postgres instead of git). The plan's own cited evidence (2026-08-25: the shop had wrapped, the mini's debt was GENUINE) proves no sound consumer can substitute: other machines' rows cannot prove this machine wrapped, and same-machine rows are redundant with the local baton. The honest deliverable — shipped here — is OPERATOR DISAMBIGUATION: the debt still reports, exits nonzero, and injects; the registry line makes the fetch-first decision immediate instead of manual. The rulings file and census are CEO-owned records and are NOT edited by this plan; this supersession is recorded here and in the register, and surfaces to the CEO at the cycle's close.
- ⚠️ **Step 5 is deliberately UNVERIFIED by the lock (S2-3/S2-4):** verifying it would put a subprocess in the stop path (rejected at W1-2). The most-skipped-step class therefore applies to it, and a registry row means "step 5 ran", never "wrap verified-complete" (record-before-verify ordering; the 4h reaper). Both limits are stated in the ritual step's own text so no future consumer inherits rows as wrap-truth.

## Numbers discipline

⚠️ **Measured 2026-08-26 by the Planner at bellows `f9c33f8`, tuyere `015353c`; re-locate every edit by ANCHOR with `grep -nF`, count==1 asserted. `grep` is ugrep: `-F` always; read printed counts, never exit status.**

| id | pin | value | anchor |
|---|---|---|---|
| Y1 | check() signature | `wrap_check.py:104` | `def check(session_id: str \| None = None, caller: str = "stop")` (count==1) |
| Y2 | debt-caller branch | `wrap_check.py:160` | `if caller == "debt" or not session_id:` (count==1) — the information line prints in the DEBT path only, after `fails` is fully computed (verb corrected, S2-6) |
| Y3 | main argv parse | `wrap_check.py:377` | `caller = sys.argv[2]` (count==1) — untouched; pin proves the caller plumbing exists |
| Y4 | wrap.md step-4 tail | the memory-repo step ending `commit/push half is N/A.` (count==1) | the new step 5 (Record the wrap) inserts AFTER it, BEFORE the `Use the current model's` trailer line |
| Y5 | tuyere CLI list format | `[<id>] <machine> — <session_id> wrapped at <YYYY-MM-DD HH:MM:SS>` per row (S1-1 correction: the literal separator is ` wrapped at `, verified against the CLI's OUTPUT — run `list` read-only; NEVER a source grep, the f-string splits the literal across `wraps.py:50-51` and `grep -nF` false-fails — S3-6); `no session wraps recorded` when empty | the parser keys on ` wrapped at ` + a date match; ⚠️ the CLI records `wrapped_at` in UTC while the hook computes local today (S1-4) — the parser matches rows containing EITHER the local-today or the UTC-today `YYYY-MM-DD` string (compute both; near midnight they differ and both are honest) |
| Y6 | tuyere checkout resolution | env `ELUVIAN_WRAP_TUYERE`, else `~/Developer/tuyere`, else `<wrap_check's own ROOT>/tuyere` — ROOT as the module already resolves it (env override else its default), NEVER a raw env read (S3-4: env-strict diverges from module-ROOT exactly on the shop layout and would leave the read permanently inert there) | first candidate whose `<path>/.venv/bin/python` exists; none → fail-open None |
| Y7 | file shas (HALT on mismatch) | wrap_check.py `50b6958f65fb…`, wrap.md `67cd0b7c8493…` (first 12) | re-derive with `shasum -a 256`; mismatch → HALT with inventory (the wrap-lock arc may have moved the file — coordination, not force) |
| Y8 | test surface | all four exist: `tests/test_wrap_hooks.py`, `test_wrap_3b_keyed.py`, `test_wrap_receipts.py`, `test_wrap_sentinel.py` (S1-3); NEW file `tests/test_wrap_r2_registry.py` is 0-occurrence absent (verified) | new tests import wrap_check and stub the subprocess seam; no psycopg import anywhere in bellows tests |

## MUST-PRESERVE

- ⚠️ **FAIL-OPEN IS STRUCTURAL:** `_session_wraps_today()` returns None on EVERY failure branch — missing checkout, missing venv, subprocess timeout (5s hard), nonzero exit, empty/unparseable output, any exception. A None result adds NO line. The function must be incapable of raising into `check()` (outermost try/except returns None).
- ⚠️ **NEVER SUPPRESS:** the `fails` list is computed exactly as today and returned unmodified; the registry line is printed alongside the debt report only (it precedes the fails list in stdout — S1-2) (a separate informational element, never an entry in `fails`, never consulted by any verdict).
- ⚠️ **The subprocess runs the TUYERE VENV python** (Y6 resolution), never system python3; args are a fixed list (no shell), cwd the tuyere checkout.
- ⚠️ **wrap_check.py is the live guard** — `py_compile` after every edit; the full existing wrap-hook test files must pass unchanged (their behavior contract is untouched by construction: no existing line of `check()`'s fail logic changes).
- ⚠️ **EVERY DATE IS A FIXED LITERAL** in this plan; the code computes BOTH today-strings — local `datetime.date.today().isoformat()` beside the existing 3b usage, and `datetime.datetime.now(datetime.timezone.utc).date().isoformat()` for the parser's boundary arm (S4-6).

## STEP 1 — DEV: the registry seam + the ritual step

**Role:** DEV. `<id>` from your plan filename.

**A0 — preconditions.** Re-derive Y7 shas (HALT + inventory on mismatch — coordinate, never force); assert Y1/Y2/Y3/Y4 anchors count==1; ⚠️ TOOLCHAIN BRANCH FIRST (S3-3, measured: the bellows venv has NO pytest and requirements.txt does not pin it — every later test gate is unexecutable without this): assert `.venv/bin/python -m pytest --version` succeeds; if not, `.venv/bin/pip install -r requirements.txt pytest` (and this plan ADDS a `pytest` line to requirements.txt so the toolchain is pinned, not ad-hoc — see the edit set). Then measure the bellows test baseline (`.venv/bin/python -m pytest --collect-only -q`, record the count; the seat-3 rehearsal measured the four wrap files at 115 passed in a scratch venv). Three-way start: anchors as pinned and `tests/test_wrap_r2_registry.py` absent → proceed; the full substrate present (`_session_wraps_today` in wrap_check.py + step 5 in wrap.md + the test file + the pytest line in requirements.txt) → ALREADY APPLIED, no-op success; else partial → STOP with inventory.

**A1 — implement:**
- **(a) `hooks/eluvian/wrap_check.py`:** add `_tuyere_checkout()` (Y6 resolution, returns Path or None) and `_session_wraps_today(timeout_seconds=5)` → `list[str] | None` (the parameter exists for the timeout test — W1-3): subprocess `[<venv-python>, "-m", "tuyere.wraps", "list", "--limit", "10"]`, cwd the checkout, timeout 5, capture text; on returncode 0, split each line on ` wrapped at ` and keep it only when the TIMESTAMP part startswith either today-string (local and UTC — S3-2: a date-bearing session-id slug like `backfill-2026-08-26` must not false-match; S3-1 correction: timestamptz renders in the CONNECTION timezone, measured local, so the dual-date filter is boundary safety, not a UTC-display fix); return the kept lines (possibly empty list); ANY other outcome → None (outermost try/except). The seam is gated STRICTLY on `caller == "debt"` — never the Y2 branch's `or not session_id` arm (W1-2: a sid-less STOP call enters that branch, and the hard-block lock's path must stay subprocess-free). Inside that strict gate, after `fails` is computed and only when `fails` is non-empty: rows = `_session_wraps_today()`; if rows, PRINT (inside `check()`, placed immediately before the `return fails` at the function's single exit — anchor `return fails` count==1 at :217; stdout is the debt hook's injection channel; `main()`'s formatting is untouched; never append to fails — S1-6) `[R2/registry] wrap(s) recorded today per the shared registry:` + each row indented + `— if this machine's tree is stale, fetch first: the debt reported BELOW may be another machine's already-satisfied state (scope law). Genuine local debt still stands.` (S1-2: check() prints before main() prints the fails list, so the registry line precedes the report — the wording says below, and MUST-PRESERVE's "appended" is corrected to "printed alongside") Docstring notes the seam, the fail-open contract, and `ELUVIAN_WRAP_TUYERE`.
- **(b) `hooks/commands/wrap.md`:** insert after the Y4 anchor a new step: `5. **Record the wrap (R2)** — from a tuyere checkout with DB access: \`.venv/bin/python -m tuyere.wraps record <full-session-uuid>\` (the machine defaults to this host). No tuyere checkout or unreachable DB → SKIP and say so (fail-open ritual; the registry is information, never a gate). ⚠️ This step is UNVERIFIED by the lock (deliberate — the stop path stays subprocess-free), so the most-skipped-step class applies; a registry row attests that THIS STEP RAN, never that the wrap verified complete.`
- **(c) `requirements.txt`:** append a `pytest` line UNCONDITIONALLY (idempotent: skip only if the literal line already exists) — never only inside A0's if-not arm, where an ad-hoc install would satisfy the assert and the pin would silently never land (S4-4).
- **(d) `tests/test_wrap_r2_registry.py`:** unit `_session_wraps_today` against a STUBBED seam (monkeypatch `_tuyere_checkout` to a tmp dir carrying a fake `.venv/bin/python` script emitting canned Y5-format output): (1) today-dated rows returned, yesterday-dated filtered; (2) empty output → empty list, `no session wraps recorded` → empty list; (3) nonzero exit → None; (4) timeout (stub sleeps past a shortened timeout arg or via a hanging stub) → None; (5) missing checkout (resolver returns None) → None; (6) NEVER-SUPPRESS + POSITIVE-PRINT: run `check()` twice on an identical fails-producing fixture (ELUVIAN_WRAP_ROOT via setenv + `importlib.reload(wrap_check)` — S3-7: ROOT binds at import and no in-process pattern exists in the existing subprocess-style wrap tests) with the seam stubbed to rows vs None — the returned `fails` lists are EQUAL, AND capsys shows the registry line in the rows case and its absence in the None case (S3-5: without this, no gate anywhere observes the deliverable's positive path).

**A2 — verify before committing (paste raw):** targeted new tests green; the FOUR existing wrap test files green unchanged (`pytest tests/test_wrap_hooks.py tests/test_wrap_3b_keyed.py tests/test_wrap_receipts.py tests/test_wrap_sentinel.py -q`); `py_compile` wrap_check.py; run `python3 hooks/eluvian/wrap_check.py "" debt` from the repo and paste the output — the registry line appears only if wraps exist today AND debt exists (state which case was observed; both are valid). ⚠️ ALSO paste which Y6 candidate `_tuyere_checkout()` resolved ON THIS MACHINE (add a `--probe-checkout` style one-liner via `python3 -c` importing the function) — S1-5: on a machine where no candidate resolves, the read is PERMANENTLY INERT and that must be VISIBLE in the evidence, not silent; if None resolves on the dispatching machine, say so loudly in the step report so the CEO can set `ELUVIAN_WRAP_TUYERE`.

**A3 — commit** (pathspec): `git add hooks/eluvian/wrap_check.py hooks/commands/wrap.md tests/test_wrap_r2_registry.py requirements.txt && git commit -m "[<id>] R2 actuation: fail-open registry information line in wrap_check (subprocess seam, never suppressing) + ritual wrap-record step"`

**Deposits:**
- `/Users/marklehn/Developer/bellows/hooks/eluvian/wrap_check.py`
- `/Users/marklehn/Developer/bellows/hooks/commands/wrap.md`
- `/Users/marklehn/Developer/bellows/tests/test_wrap_r2_registry.py`
- `/Users/marklehn/Developer/bellows/requirements.txt`

**Scope:**
- `/Users/marklehn/Developer/bellows/hooks/eluvian/wrap_check.py`
- `/Users/marklehn/Developer/bellows/hooks/commands/wrap.md`
- `/Users/marklehn/Developer/bellows/tests/test_wrap_r2_registry.py`
- `/Users/marklehn/Developer/bellows/requirements.txt`


## STEP 2 — QA: full suite + evidence

**Role:** QA. Fresh read of the Step-1 diff. Run the FULL bellows suite via the bellows venv; write the complete pytest output to the named `.txt` deposit below (the codified gate class), and the analysis to the `.md`. Re-run the A2 probes and paste. Verify the never-suppress test (6) exists and passes. Verify wrap.md's step 5 sits between the Y4 anchor and the trailer line.

> **QA SELF-CHECK — Rule 20.** Post the block from `/Users/marklehn/Developer/eluvian-governance/RULE_20_SELF_CHECK_BLOCK.md` verbatim, under the banner **`Rule 20 — QA Self-Check Results`**, and close with **`PASSED — SELF-CHECK PASSED`** only if every check genuinely passed. ⚠️ Both literals are matched by `plan_lint` check (c) and neither may be paraphrased.

**Post-conditions:** fails-list equality proven by test (6); all four pre-existing wrap test files green unchanged; the registry line demonstrated fail-open (at least one None branch exercised with output shown); wrap.md step numbering intact around the insertion.

**Deposits:**
- `/Users/marklehn/Developer/bellows/knowledge/research/r2-wiring-qa-evidence-2026-08-26.md`
- `/Users/marklehn/Developer/bellows/knowledge/research/r2-wiring-pytest-2026-08-26.txt`

**Scope:**
- `/Users/marklehn/Developer/bellows/knowledge/research/r2-wiring-qa-evidence-2026-08-26.md`
- `/Users/marklehn/Developer/bellows/knowledge/research/r2-wiring-pytest-2026-08-26.txt`

**Commit (Step 2):** `git add knowledge/research/r2-wiring-qa-evidence-2026-08-26.md knowledge/research/r2-wiring-pytest-2026-08-26.txt && git commit -m "[<id>] qa: R2 wiring — full suite + evidence"`

## Drafting Cycle
**Tier:** T2 computed — **T-6 fires** (wrap_check.py is live-guard/gate enforcement; wrap.md is ritual doctrine); T-7 fires (consumes exec-3 + R2 ruling). **Cold panel: MANDATED at the freeze (full form, four seats).**
**Walk register:** `governance/knowledge/research/walk-register-executable-bellows-r2-wiring.md`
**Walks:** walk 0 pinned (Y1–Y8 measured; clone-diff vs exec-3 run); walks 1–2 complete (w1 3 folded, w2 dry = the freeze); **the FULL COLD PANEL at the freeze: scout 6 → discovery 6 → execution 7 → capstone 6 = 25 findings (2 HIGH at capstone, 1 at discovery, 1 at execution)**; walk 3 = the post-panel apply/restructure walk; walk 4 = the closing walk.
**Direction verdict (after walk 1): PROCEED.** Tested, not judged: exec-3/R2 stand; the seam mechanism stands; no forcing finding.
- Weak spots:          w1 1 folded — instruction 1 / record 0 (print channel + location specified); w2 dry; w3 2 folded — instruction 2 / record 0 (fold-introduced: S4-1 restructure, S4-4 pin placement); w4 dry
- Destruction:         w1 1 folded — instruction 1 / record 0 (seam gated off the stop path); w2 dry; w3 dry; w4 dry
- Vulnerabilities:     w1 1 folded — instruction 1 / record 0 (timeout parameter for the test); w2 dry; w3 dry; w4 dry
- Integration-record:  w1 dry; w2 dry; w3 2 folded — instruction 1 / record 1 (fold-introduced: S4-3 real application, S4-5/6 record); w4 dry
- ACID:                w1 dry; w2 dry; w3 dry; w4 dry
**Conformance (§5):** first run at the walk-2 freeze — ⚠️ that run's "0 FAIL" record was FALSE (a truncated channel read; struck in the register with evidence) — final run at the walk-4 close on the FULL channel: plan_lint deposits/scope PASS both steps (4 + 2 paths), 0 FAIL; remaining warnings the earned/benign classes; propagation_check could-not-run per its own channel; register lint 0 warnings.
**Cold panel: CONVENED AT THE WALK-2 FREEZE (full form, four seats) — COMPLETE.** Scout 6 (real CLI separator, UTC/local, loud-inertness), discovery 6 (HIGH: R2 closes-clause superseded to operator-disambiguation), execution 7 (HIGH: no pytest in the bellows venv — toolchain branch + pin; parser rehearsed clean across 8 adversarial cases), capstone 6 (HIGH ×2: per-step Deposits labels unparseable by every pipeline consumer — restructured to literal in-step blocks; the freeze conformance record was produced through a TRUNCATED channel read and was false — struck in the register). NOT-READY discharged by the walk-3 folds + walk-4 close.
**Closing:** **walk 4 met the bar — five lenses dry on the post-restructure arrangement; last event = a dry lens pass; the walk-3 relocation was the reset and walk 4 folded nothing.** Warm 3 → 0; panel 6 → 6 → 7 → 6 (4 HIGH total); post-panel 4 → 0. Capstone's NOT-READY discharged. Closing-record re-read run against this block after writing — dry. Deposited once via the CROSS-MACHINE lane: committed+pushed ready- file in bellows/knowledge/decisions/ → the SHOP daemon's depositor on arrival (expected auto-HOLD no_clearance) → the shop CEO's release act.

## Cycle Manifest
tier: T2
target: hooks/eluvian/wrap_check.py
class: shop-infra
reads: /Users/marklehn/Developer/bellows/hooks/eluvian/wrap_check.py, /Users/marklehn/Developer/bellows/hooks/eluvian/wrap_debt_hook.py, /Users/marklehn/Developer/bellows/hooks/eluvian/wrap_stop_hook.py, /Users/marklehn/Developer/bellows/hooks/commands/wrap.md, /Users/marklehn/Developer/tuyere/tuyere/wraps.py, /Users/marklehn/Developer/tuyere/knowledge/research/machine-registry-rulings-2026-08-26.md
writes: hooks/eluvian/wrap_check.py, hooks/commands/wrap.md, tests/test_wrap_r2_registry.py, requirements.txt, knowledge/research/r2-wiring-qa-evidence-2026-08-26.md, knowledge/research/r2-wiring-pytest-2026-08-26.txt
open_forks: (1) R2's closes-clause superseded to operator-disambiguation — CEO sees the supersession at this close (ruling/census text not edited by this plan); (2) step 5 deliberately lock-unverified (stop path stays subprocess-free) — the most-skipped-step class accepted and stated; (3) wrap_debt_hook envelope wording = tuyere thread 9
walks: 4
yields: 3, 0, 3, 0
validation: cycle_check=BAR_MET, plan_lint=0_FAIL, fold_check=N/A
coherence: 4/4 walks have register rows
