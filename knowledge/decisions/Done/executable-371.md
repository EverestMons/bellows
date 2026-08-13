# Executable: `plan_lint` check (q) — deposit-time pin verification, warn-first (Fork 3, phase 1)

**Type:** Executable
**Project:** bellows
**Depends on:** `/Users/marklehn/Developer/GitHub/pin-hook-scoping-packet-2026-08-13.md` (the CEO's Fork-3 pick — phase 1 only), `bellows/knowledge/research/predicted-number-lint-findings-2026-08-12.md` + `bellows/knowledge/qa/evidence/predicted-number-pin-census-2026-08-12/labelled-instances.md` (369's evidence — **cited, never recomputed**), `bellows/scripts/plan_lint.py` + `bellows/tests/test_plan_lint.py` (current state — letters (a)–(p) taken, **(q) measured free at authoring**; module baseline **110 passed, measured 2026-08-13 — re-verify, do not inherit**)
**Created:** 2026-08-13
**Author:** Planner
**Slug:** `pin-hook-lint-2026-08-13`
**dispatch_mode:** bellows
**pause_for_verdict:** always
**Priority:** 5
**cycle_tier:** T1
**qa_steps:** 2

⚠️ **ID NOTE — the deposit filename is decided AT DEPOSIT.** `id_sequence` read at deposit, never at authoring.

---

## Why this exists

The CEO approved Fork 3 of the pin-hook scoping packet. Phase 1 ships the **warn-first** check into `plan_lint.py` — the authoring-ritual seam where a fabricated pin still exists (369's structural finding: walks correct fabrications pre-deposit, so only an authoring-time instrument can see one). Phase 2 (a `gates.py` gate) is **not this plan** and is decided later from the telemetry this plan ships.

**Warn-first is a contract, not a default:** check (q) NEVER changes the exit code. Its output is WARN lines for defects and one `PIN-CHECK:` telemetry line per token — the shakedown data the phase-2 decision reads. Legitimate-but-odd fires (an example hash in prose, a quoted historical pin) are accepted warn-first noise; the telemetry prices them, this plan does not guess them.

---

## Specification — check (q)

- **Scan surface: RAW `plan_text`, not `clean_text`.** Pins live inside fenced bootstrap blocks and inline code; the fence-stripping other checks use would blind this one. *(Ledger C3.)*
- **Token rule (369 fold f16):** a token is a **maximal hex run**, case-insensitive. Length 64 → sha256 candidate; length 40 → git-object candidate; any other length ≥12 → display prefix, telemetry-only. A 64-run is never also a 40-match inside itself.
- **M2 — sha256 file pins (primary surface):** for each 64-token, search the same line and the lines immediately before/after for a `shasum`/`sha256` invocation naming a path. Path extraction handles **backtick-quoted paths** (369's recorded 13-of-24 AMBIGUOUS cause) and bare absolute paths. Resolution: absolute path used as-is; relative tried against the project repo root. Results: **match** (telemetry ok) / **MISMATCH** → `(q) WARN` / **file missing** → `(q) WARN` / **no path found** → telemetry `result=ambiguous`, no WARN (keeps the WARN channel high-signal; the telemetry still counts it for the promotion decision).
- **M1 — git-object pins:** for each 40-token, `git cat-file -e` against (1) the plan's Project repo, (2) the root repo, (3) any repo named by a `git -C <absolute-path>` on the same line. Resolving in the Project repo → telemetry ok; resolving only elsewhere → telemetry `result=cross-repo` (no WARN); resolving nowhere → `(q) WARN`.
- **Repo resolution is location-independent (the mirror caveat, Ledger C2):** repos derive from the SCRIPT's own location — `repo_base = BELLOWS_ROOT.parent`, project repo = `repo_base/<Project header value>`, root repo = `repo_base` — never from the linted file's path, so the scratchpad-mirror ritual gets identical results to an in-place run. A missing/`.git`-less resolved repo → telemetry `result=repo-unavailable`, no WARN (no warn-storm at exotic locations).
- **Telemetry:** exactly one line per token: `PIN-CHECK: kind=<sha256|git|prefix> line=<n> token=<first-12>… result=<ok|mismatch|missing-file|ambiguous|cross-repo|unresolved|repo-unavailable>`.
- **No-crash contract:** check (q) may never take down the lint. Its body runs inside a defensive wrapper — an unexpected exception prints `(q) WARN: check errored (<exception>)` and lint continues; every `git`/`shasum` subprocess carries a timeout. A crashed advisory check is worse than none: it blocks the deposit ritual it was meant to inform. *(A dedicated test proves the wrapper: a pathological input — e.g. a pinned path that is a directory — lints without raising.)*
- **Testability seam:** pure helpers — `_extract_hex_tokens(text)` and `_check_pins(plan_text, project_repo, root_repo)` — take explicit paths; `lint()` wires the defaults. Tests inject `tmp_path` repos and never touch real ones.

---

## Ledger

- **C1 — warn-first is enforced, not intended.** Check (q) cannot set `all_passed = False`. *(observer: QA Item 2 — a live fixture plan carrying a failing pin lints EXIT 0 with the (q) WARN present)*
- **C2 — location-independence proven live, not asserted.** *(observer: QA Item 3 — the same plan linted at its real path and at a scratch copy yields identical PIN-CHECK results)*
- **C3 — raw-text scan.** A pin inside a fenced block is seen. *(observer: a dedicated test with the pin only inside a fence)*
- **C4 — every count verified, none assumed.** The 110 baseline and all deltas are re-measured and reported; a differing number needs explaining, not accepting. *(observer: QA Item 1)*
- **C5 — one telemetry line per token.** *(observer: QA Item 3's run output)*

---

## How to Run This Plan

**Bootstrap prompt:**
```
Read the plan at knowledge/decisions/in-progress-executable-<id>.md (the daemon renames the deposited placeholder on claim). Execute Step 1 ONLY. After completing Step 1, STOP and wait for my confirmation.
```

---

## Scope

**The authority for the write-set; each step's Deposits block carries only its own subset.**

- `bellows/scripts/plan_lint.py`
- `bellows/tests/test_plan_lint.py`
- `bellows/knowledge/development/pin-hook-lint-dev-2026-08-13.md`
- `bellows/knowledge/qa/evidence/pin-hook-lint-2026-08-13/qa-receipt.md`
- `bellows/knowledge/qa/evidence/pin-hook-lint-2026-08-13/pytest-full-raw.txt`
- `bellows/knowledge/qa/evidence/pin-hook-lint-2026-08-13/fixture-bad-pins.md`

---

## STEP 1 — DEV (the check + targeted tests)

> **FIRST — post a short visible chat message (1-2 sentences) confirming you are starting this plan.** Do NOT rename this file.
>
> ⚠️⚠️ **EXECUTE STEP 1 ONLY, THEN STOP.** Running into Step 2 destroys QA independence — a step-contract violation, not efficiency.
>
> ⚠️⚠️ **THE WORKTREE RULE:** every git command runs from the step's own cwd (the dispatched checkout); never `-C` into another checkout for a WRITE. Read-only probes of other repositories use explicit `-C` and are sanctioned.
>
> **Task A0 — branches, catch-all LAST.**
> **(0) TREE SHAPE:** `git rev-parse --show-toplevel` from cwd prints a path whose tree contains `knowledge/decisions`. Not bellows-shaped → HALT.
> **(1) CLEANLINESS (scoped):** `git status --porcelain -- scripts/plan_lint.py tests/test_plan_lint.py knowledge/development/pin-hook-lint-dev-2026-08-13.md` empty.
> **(2) RE-ENTRY key:** `git log --oneline -- scripts/plan_lint.py` (from cwd) for a commit whose subject carries this plan's slug.
> - **FRESH** = (1) empty AND (2) absent → Task B. **RE-ENTRY** = (2) present → the DEV landed; verify the deposits exist and report complete without re-editing. **NONE-MATCH** = anything else → HALT quoting every measurement.
>
> **Task B — implement check (q)** in `scripts/plan_lint.py` per the Specification, matching the file's existing check style (lettered comment header stating what the check can and cannot see, WARN-only, helpers near the top). ⚠️ Verify the letter is still free before writing (`grep -cF "(q)" scripts/plan_lint.py` — expect 0; any other count needs explaining, not accepting).
>
> **Task C — targeted tests** in `tests/test_plan_lint.py`, covering at minimum: maximal-run extraction (64 not double-counted as 40; prefix classification; <12 ignored); M2 match / mismatch-WARN / missing-file-WARN / no-path-ambiguous; backtick-quoted path extraction; M1 resolve (a `tmp_path` git repo — init and commit with inline identity, `git -c user.email=t@t -c user.name=t commit …`, so an identity-less environment cannot fail the fixture; use its HEAD sha) / unresolved-WARN / cross-repo; the fenced-block pin (C3); **the C1 warn-first test: a plan whose pins all fail still exits by the OTHER checks' verdicts alone**. Run the module: `python3 -m pytest tests/test_plan_lint.py -q` — **foreground, targeted only (never the full suite in DEV)**. Baseline measured at authoring: 110 passed — re-verify and report the actual before/after counts; any unexplained delta → HALT.
>
> **Task D — dev note** `knowledge/development/pin-hook-lint-dev-2026-08-13.md`: what shipped (the (q) letter, helper names, result vocabulary), the targeted run's RAW tail pasted, and the measured before/after test counts. Commit all three files from cwd with a pathspec naming exactly them, subject carrying `[<id from your plan filename>]` + the slug, then STOP.
>
> **Deposits:**
> - `bellows/scripts/plan_lint.py`
> - `bellows/tests/test_plan_lint.py`
> - `bellows/knowledge/development/pin-hook-lint-dev-2026-08-13.md`
>
> **Scope:**
> - `bellows/scripts/plan_lint.py`
> - `bellows/tests/test_plan_lint.py`
> - `bellows/knowledge/development/pin-hook-lint-dev-2026-08-13.md`

---

## STEP 2 — QA

> ⚠️⚠️ **PRECONDITION — Step 1 ran as its own dispatch.** `git log --oneline -- scripts/plan_lint.py` (from cwd) shows the Step-1 commit made before this step began, not by this context. If not, say so plainly and mark the independence gap.
>
> **(A) Rule 20 self-check block** — emit the canonical block from `/Users/marklehn/Developer/GitHub/RULE_20_SELF_CHECK_BLOCK.md` (read live, never recalled). The receipt carries the canonical header `Rule 20 — QA Self-Check Results` and, on full pass, the canonical verdict line `PASSED — SELF-CHECK PASSED`. `required_evidence_files` = the evidence-directory subset of `## Scope`.
>
> **(B) Deliverable verification — a FAIL is reported, never repaired:**
> - **Item 1 — the FULL suite, FOREGROUND, no Monitor:** `python3 -m pytest tests/ -q` from cwd; paste the raw tail into `pytest-full-raw.txt` and the receipt. Report the actual totals; any failure is a FAIL with its output — do not fix, do not re-run to green.
> - **Item 2 — C1 live:** author the fixture `knowledge/qa/evidence/pin-hook-lint-2026-08-13/fixture-bad-pins.md` (never under `knowledge/decisions/`). ⚠️ **The fixture must be a minimal VALID plan** — a header that parses with recognized `dispatch_mode`/`pause_for_verdict` tokens and every other check passing on the skeleton — **or check (a) exits 1 before (q) ever runs and the rehearsal proves nothing.** Its body carries two lines: (i) `shasum -a 256 <absolute path of a real repo file>` with a deliberately WRONG 64-hex value on the same line (exercises M2 → MISMATCH), and (ii) an unresolvable 40-hex token (e.g. 40 `f`s) in plain prose (exercises M1 → unresolved). Run `python3 scripts/plan_lint.py <fixture>`; **EXIT 0 with both `(q) WARN` lines present** — paste the run.
> - **Item 3 — C2 + C5 live:** run the linter on `knowledge/decisions/Done/diagnostic-370.md` at its real path AND on a copy at a scratch path; identical `PIN-CHECK:` line sets, one line per token — paste both runs.
> - **Item 4 — C4:** the dev note's before/after counts match Item 1's measured reality.
> - **Item 5 — raw output:** every count in the receipt is pasted stdout.
>
> Commit the receipt, the raw file, AND the fixture from cwd with a pathspec naming exactly them — **the fixture is the Item-2 evidence's instrument; an uncommitted fixture is destroyed at worktree teardown and the receipt then cites a file that no longer exists (336's destroyed-instrument lesson)** — then STOP.
>
> **Deposits:**
> - `bellows/knowledge/qa/evidence/pin-hook-lint-2026-08-13/qa-receipt.md`
> - `bellows/knowledge/qa/evidence/pin-hook-lint-2026-08-13/pytest-full-raw.txt`
> - `bellows/knowledge/qa/evidence/pin-hook-lint-2026-08-13/fixture-bad-pins.md`
>
> **Scope:**
> - `bellows/knowledge/qa/evidence/pin-hook-lint-2026-08-13/qa-receipt.md`
> - `bellows/knowledge/qa/evidence/pin-hook-lint-2026-08-13/pytest-full-raw.txt`
> - `bellows/knowledge/qa/evidence/pin-hook-lint-2026-08-13/fixture-bad-pins.md`

---

## Drafting Cycle

**Tier:** T1 — self-escalated above a T0 reading: the change is one script plus tests, but it installs a check into the shop's authoring ritual, and its false-positive behavior shapes every future deposit. T-6 does not fire (`plan_lint` is advisory, not a gate); T-2/T-5 do not fire.

**Walk register:** `governance/knowledge/research/walk-register-pin-hook-lint-2026-08-13.md` (schema 0.2), committed per phase; Deviations range ends with the open tail, closing commit named at wrap.

**Walks:** 2. Fold trajectory 4 → 0.

- Weak spots:      w1 1 — 1 pre / 0 fold; w2 0.
- Destruction:     w1 1 — 1/0; w2 0.
- Vulnerabilities: w1 1 — 1/0; w2 0.
- Integration:     w1 1 — 0/1 (p4 caught p1's fixture entering the plan without entering its write-set); w2 0.
- ACID:            w1 0; w2 0.

**Conformance:** register validator run at close — result recorded in the walk register's own commit; `plan_lint` runs at the faithful staged mirror at freeze, recorded in the deposit commit, not predicted here.

**Closing:** walk 2 DRY — **instruction 0 / record 0**, no residue to enumerate; the last event before deposit is a dry lens pass.
