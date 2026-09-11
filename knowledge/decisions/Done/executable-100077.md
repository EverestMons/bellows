# bellows — THE DEBT HOOK'S HEADER STOPS ASSERTING WHAT ITS OWN REPORT DOUBTS: when `wrap_check`'s injected report carries the `[R2/registry]` line, the SessionStart envelope says "unverified debt — read the registry note" instead of "a prior session ended without completing the wrap"; the composition becomes one pure function with two tests (thread 9, panel S2-5 of the r2-wiring cycle)

**Date:** 2026-09-11 | **Project:** bellows | **Tier:** Small (one hook function, two tests, one mutation manifest, one dev-log) | **Dispatch Mode:** bellows | **Test Scope:** full-suite (Rule 21 — the hook is exercised by `tests/test_wrap_hooks.py`; `pytest tests/ -q`) | **Execution:** Step 1 (DEV) → Step 2 (QA) | **qa_steps:** 2 | **pause_for_verdict:** after_qa_step | **known_failures:** 0 | **Discharges:** thread 9 | **cycle_tier:** T0 (no trigger); integration-vs-record pass: no precedent conflict — thread 9 is the r2-wiring panel's seat S2-5 (2026-08-26), unaddressed since; `wrap_check.py:373–377` prints the `[R2/registry]` caveat inside the report the hook injects, while `wrap_debt_hook.py:76–77` asserts above it that a prior session ended unwrapped; the 2026-08-24 lesson (stale-tree debt is indistinguishable from done-elsewhere-and-not-pulled) and this session's own SessionStart (a date rollover read as debt) are the record; the fix restates the report's caveat in the envelope and changes no check.

**auto_close:** false

**Post-close:** no restart (the hook is loaded by the harness from the repo at each SessionStart — MACHINE_SETUP §6); no doctrine.

**Depends on:** thread 9 (2026-08-26, panel S2-5): "wrap_debt_hook.py:100–106 asserts as fact what the new [R2/registry] caveat inside the injected report says may be false; when the injected stdout contains the registry line, the header should say 'unverified debt — see the registry note below' instead of asserting." Clone origin: `Done/executable-100066.md` (the align hook: a pure `_compose_context` function tested by path-loading the hook, 2026-09-10).

**Tier computed (§1):** **T0** — no trigger fires: a trivial localized wording change in one hook function, no gate, no doctrine, no data; the Floor pass (Lens 4) is recorded in the header line above.

## CEO Context

Every SessionStart, the debt hook runs `wrap_check.py <sid> debt` and, on a non-zero exit, injects the checklist under a header that asserts a prior session ended without wrapping. Since the r2 wiring, the checklist itself can carry `[R2/registry] wrap(s) recorded today per the shared registry:` — the registry's word that a wrap DID complete, possibly on another machine, possibly against a tree this machine has not pulled. The envelope then contradicts its own body. This morning's session opened under exactly that header for a date rollover, with the 28th wrap complete and verified the night before. The fix is a sentence: when the report carries the registry line, the header says the debt is unverified and points at the note.

## What this changes

1. **`hooks/eluvian/wrap_debt_hook.py`** — the envelope's text moves into a pure function `_compose_debt_message(checklist: str) -> str` beside `main()`: when `"[R2/registry]" in checklist` the header reads `⚠️ UNVERIFIED SESSION DEBT — the report below carries the registry's note that a wrap may already have completed (elsewhere, or against a tree this machine has not pulled). Read that note first; fetch before judging:` and otherwise the current text (`⚠️ UNWRAPPED SESSION DEBT DETECTED. A prior session ended without completing the wrap ritual. Resolve this BEFORE starting new work:`); the checklist and the closing sentence (`This is not a fresh-session state. Treat it as a wrap in progress: …`) are unchanged in both. `main()` calls it; nothing else in the hook moves (the daemon exemption, the sid validation, the subprocess, the hooklog lines).
2. **`tests/test_wrap_hooks.py`** — two tests in the file's own style, loading the hook by path as `test_hook_default_root.py` does: (t1) `_compose_debt_message("[2r/receipts] OK …\n[R2/registry] wrap(s) recorded today per the shared registry:\n  …")` starts with `⚠️ UNVERIFIED SESSION DEBT` and contains the checklist verbatim; (t2) the same on a checklist without the line starts with `⚠️ UNWRAPPED SESSION DEBT DETECTED` — the two headers never both appear in one message.
3. **`knowledge/mutants/debt-hook-unverified-header.json`** — two mutants: (m1) the `in checklist` test removed (always the asserting header) → t1; (m2) the condition inverted → t2.
4. **Not changed:** `wrap_check.py`, the registry line, the stop hook, the align hook, the debt check's exit codes.

## MUST-PRESERVE

- ⛔ **The check is not touched** — the hook still injects on every non-zero exit; only the envelope's first sentence depends on the report's content.
- ⛔ **The two headers are exclusive** (t2), and the checklist passes through verbatim (t1).
- ⛔ **Every `expect_fail` is a class-qualified node id where the test is a method**; the mutation run is redirected into its deposit, never piped.
- ⛔ **The thread-262 stop** (PT v4.108 §8).

## Numbers discipline — measured 2026-09-11 by the Planner (bellows `2e3d600`)

| # | pin | value | how to re-derive |
|---|---|---|---|
| P1 | ⛔ the envelope | `hooks/eluvian/wrap_debt_hook.py` (89 lines): `main()` runs `[sys.executable, CHECK, check_sid, "debt"]` (`:63–66`), exits clean on returncode 0 (`:70–72`), else `emit(` the header `"⚠️ UNWRAPPED SESSION DEBT DETECTED. A prior session ended without completing the wrap ritual. Resolve this BEFORE starting new work:\n\n"` + `checklist` + `"This is not a fresh-session state. Treat it as a wrap in progress: you may run `/wrap` to arm the completion lock and finish the ritual."` (`:74–82`); the `__main__` guard prints `{}` on any exception (`:85–89`) | `sed -n 55,89p hooks/eluvian/wrap_debt_hook.py` |
| P2 | ⛔ the registry line | `hooks/eluvian/wrap_check.py:373–377`: `# --- R2 registry: informational line (fail-open, never suppressing)` … `print("[R2/registry] wrap(s) recorded today per the shared registry:")` — part of the stdout the hook injects as `checklist` | `sed -n 373,380p hooks/eluvian/wrap_check.py` |
| P3 | ⛔ the tests | `tests/test_wrap_hooks.py` — `_run_hook(name, payload, env_overrides)` runs a hook as a subprocess under `ELUVIAN_WRAP_ROOT` = `tmp_path` (`:100–130`, the stop hook's block/exempt tests); `tests/test_hook_default_root.py` loads a hook module by `importlib.util.spec_from_file_location` for pure-function tests; `tests/test_align_hook_sync.py` (#100066) tests `_compose_context` that way | the files |
| P4 | ⛔ the measured instance | this session's SessionStart of 2026-09-11 (after the 28th wrap verified at 01:0x): `⚠️ UNWRAPPED SESSION DEBT DETECTED … ✗ [3b/lessons] No Lessons-swept: 2026-09-11 line` — a date rollover, no debt; the 2026-08-24 lesson: stale-tree debt is indistinguishable from done-elsewhere-and-not-pulled | the session's first context; LESSONS 2026-08-24 |
| P5 | in-flight; class; interpreter | #100076 in flight at drafting (this plan queues behind it); writes: `hooks/eluvian/wrap_debt_hook.py`, `tests/test_wrap_hooks.py`, the manifest, the run file, the dev-log, two QA evidence files → **shop-infra** (`_assign_class`, walk 0) — HOLDS at admission, the CEO releases; Python 3.9.6, the bellows venv | `python3 status.py`; `_assign_class` |

## Drafting Cycle

**Tier:** T0 (no trigger) — the integration-vs-record pass only, per §1; no walk register.

**Integration-vs-record pass:** no precedent conflict — thread 9 is the r2-wiring panel's seat S2-5 (2026-08-26), unaddressed since; `wrap_check.py:373–377` prints the `[R2/registry]` caveat inside the report the hook injects while `wrap_debt_hook.py:76–77` asserts above it that a prior session ended unwrapped; LESSONS 2026-08-24 (stale-tree debt is indistinguishable from done-elsewhere-and-not-pulled) and this session's own SessionStart (a date rollover read as debt, P4) are the record; the fix restates the report's caveat in the envelope and changes no check.

**Closing:** T0 floor — deposited after the pass; class shop-infra holds, the CEO releases.

## Cycle Manifest
tier: T0
target: hooks/eluvian/wrap_debt_hook.py
class: shop-infra
reads: hooks/eluvian/wrap_debt_hook.py, hooks/eluvian/wrap_check.py, tests/test_wrap_hooks.py, tests/test_hook_default_root.py, knowledge/decisions/Done/executable-100066.md
writes: hooks/eluvian/wrap_debt_hook.py, tests/test_wrap_hooks.py, knowledge/mutants/debt-hook-unverified-header.json, knowledge/mutants/debt-hook-unverified-header.run.txt, knowledge/development/dev-log-debt-hook-unverified-header-2026-09-11.md, knowledge/qa/evidence/debt-hook-unverified-header-qa-receipt-2026-09-11.md, knowledge/qa/evidence/debt-hook-unverified-header-suite-2026-09-11.txt
mutants: knowledge/mutants/debt-hook-unverified-header.json
open_forks: 1. the debt check itself fetching before it judges (the 2026-08-24 class) — a wrap_check change, not an envelope change
walks: 0
yields: none
validation: cycle_check=BAR_MET, plan_lint=0_FAIL, fold_check=VACUOUS, propagation_check=DIVERGENT:3
coherence: T0 — the integration-vs-record pass recorded in the Drafting Cycle block; no register
fold_baseline: governance/knowledge/decisions/drafts/.executable-bellows-debt-hook-unverified-header.md.foldcheck.json

---

## STEP 1 — DEV (one pure function, two tests; the mutation run; two commits)

> ⛔ **Every item starts by re-establishing the root** — `cd "$(git rev-parse --show-toplevel)" && test -f gates.py && echo TREE_OK` — HALT unless TREE_OK. ⛔ **The interpreter is `/Users/marklehn/Developer/bellows/.venv/bin/python`, ABSOLUTE.** ⛔ Never run the daemon, `run_plan`, a claim; the hook is exercised only through the tests; `T=$(mktemp -d /tmp/debt-hook.XXXXXX)` for scratch, removed at the end.
>
> **Scope:**
> - `hooks/eluvian/wrap_debt_hook.py`
> - `tests/test_wrap_hooks.py`
> - `knowledge/mutants/debt-hook-unverified-header.json`
> - `knowledge/mutants/debt-hook-unverified-header.run.txt`
> - `knowledge/development/dev-log-debt-hook-unverified-header-2026-09-11.md`
>
> **Item 1 — re-derive P1, P2 and P3 and HALT on a mechanism mismatch** (a `_compose_debt_message` already present, or a registry line spelled other than `[R2/registry]`, IS one). Paste each pin's re-derived line beside it.
> **Item 2 — write the failing tests FIRST:** t1 and t2 as *What this changes* 2 (red: `AttributeError: _compose_debt_message`). Run the file; paste the red summary line.
> **Item 3 — the edit** as *What this changes* 1; then the file green, then the FULL suite green (`N passed, 1 skipped` — `test_gate_watcher`'s live-DB skip is the one).
> **Item 4 — first commit**, gated on the FULL suite AND the pre-check with the stage flag (#100067), path-scoped: `/Users/marklehn/Developer/bellows/.venv/bin/python -m pytest tests/ -q && /Users/marklehn/Developer/bellows/.venv/bin/python tools/check_deposit.py /Users/marklehn/Developer/bellows/knowledge/decisions/in-progress-executable-<id>.md 1 --wt "$(git rev-parse --show-toplevel)" --expect-missing knowledge/development/dev-log-debt-hook-unverified-header-2026-09-11.md knowledge/mutants/debt-hook-unverified-header.run.txt && git add hooks/eluvian/wrap_debt_hook.py tests/test_wrap_hooks.py knowledge/mutants/debt-hook-unverified-header.json && git commit -F <msg-file> -- hooks/eluvian/wrap_debt_hook.py tests/test_wrap_hooks.py knowledge/mutants/debt-hook-unverified-header.json` — three files; the message tagged with the plan id and `thread 9`.
> **Item 5 — the mutation run, REDIRECTED into `knowledge/mutants/debt-hook-unverified-header.run.txt` (a Deposit):** `/Users/marklehn/Developer/bellows/.venv/bin/python tools/mutation_check.py knowledge/mutants/debt-hook-unverified-header.json > knowledge/mutants/debt-hook-unverified-header.run.txt 2>&1`; the last line must read `MUTATION: 2 killed, 0 survived, 0 error`.
> **Item 6 — the dev-log** `knowledge/development/dev-log-debt-hook-unverified-header-2026-09-11.md` under the three headings declared below; `## Pins re-derived (P1, P2, P3)` opens with P2's value cell pasted verbatim, whole, to its last character — ⛔ the cell ends with the words `injects as `checklist``; paste through those words, then stop. Under `## Failing-first (red, then green)` the red line and the green line; under `## Mutation run` the run file's last line. **Second commit**, gated on the FULL suite and the pre-check bare, path-scoped to the run file and the dev-log. Last act: `[ -n "$T" ] && [ -d "$T" ] && rm -rf "$T"`.
> **Headings:** `## Pins re-derived (P1, P2, P3)`; `## Failing-first (red, then green)`; `## Mutation run`
> **Verbatim:** `## Pins re-derived (P1, P2, P3)` ← P2
>
> **Deposits:**
> - `knowledge/mutants/debt-hook-unverified-header.json`
> - `knowledge/mutants/debt-hook-unverified-header.run.txt`
> - `knowledge/development/dev-log-debt-hook-unverified-header-2026-09-11.md`
>
> **Post-conditions:** t1 and t2 green; the full suite `N passed, 1 skipped` with no `failed`; the mutation run's last line `MUTATION: 2 killed, 0 survived, 0 error`; two DEV commits; the dev-log's three headings present as full lines with P2's cell whole; `git status --porcelain` empty after the second commit.

## STEP 2 — QA (full suite; the hook run once on a synthetic report; the receipt)

> ⛔ **Every item starts by re-establishing the root** — `cd "$(git rev-parse --show-toplevel)" && test -f gates.py && echo TREE_OK` — HALT unless TREE_OK. Interpreter ABSOLUTE; read-only beyond the two evidence files; `T=$(mktemp -d /tmp/debt-hook-qa.XXXXXX)`.
>
> **Item 1 — the full suite REDIRECTED not piped:** `/Users/marklehn/Developer/bellows/.venv/bin/python -m pytest tests/ --tb=short -q > knowledge/qa/evidence/debt-hook-unverified-header-suite-2026-09-11.txt 2>&1`; the summary line quoted in the receipt as `N passed` with the skip named as `one skip (test_gate_watcher, live-DB)` — never the word the Rule 20 block scans for.
> **Item 2 — the envelope read from outside pytest, in-process:** load the worktree's hook by path (`importlib.util.spec_from_file_location`) and call `_compose_debt_message` twice — once with a report carrying `[R2/registry] wrap(s) recorded today per the shared registry:` and once without — paste both first lines. The live `wrap_check` is not run and no SessionStart is simulated.
> **Item 3 — production writes, stated exactly:** none outside the two evidence files; `$T` removed; no lane file, no lifecycle row, no daemon.
> **Item 4 — receipt** `knowledge/qa/evidence/debt-hook-unverified-header-qa-receipt-2026-09-11.md`: `numstat` over the DEV commits (`<base>..<dev>`, five files); a `## Verification` table with one row per Item 1–3, each quoting the line it rests on — ⛔ the status cell holds exactly one token (`✅`) and no positive row's text carries a hedging keyword; then RUN the canonical Rule 20 block (`$ELUVIAN_WRAP_ROOT/RULE_20_SELF_CHECK_BLOCK.md`) with `plan_slug: debt-hook-unverified-header-2026-09-11`, `qa_report_path` and `evidence_dir` absolute under `$(git rev-parse --show-toplevel)/knowledge/qa/evidence/`, `required_evidence_files: ["debt-hook-unverified-header-suite-2026-09-11.txt"]`, and APPEND its stdout — the banner `Rule 20 — QA Self-Check Results` and the closing `PASSED — SELF-CHECK PASSED` line are the block's output, never hand-authored; a `FAILED` stdout goes into the receipt and the step STOPS (PT v4.108 §8).
> **Item 5 — commit**, path-scoped and gated: `grep -Eq '^[0-9]+ passed' knowledge/qa/evidence/debt-hook-unverified-header-suite-2026-09-11.txt && ! grep -Eq '[0-9]+ (failed|error)' knowledge/qa/evidence/debt-hook-unverified-header-suite-2026-09-11.txt && /Users/marklehn/Developer/bellows/.venv/bin/python tools/check_deposit.py /Users/marklehn/Developer/bellows/knowledge/decisions/in-progress-executable-<id>.md 2 --wt "$(git rev-parse --show-toplevel)" && git add knowledge/qa/evidence/debt-hook-unverified-header-qa-receipt-2026-09-11.md knowledge/qa/evidence/debt-hook-unverified-header-suite-2026-09-11.txt && git commit -F <msg-file> -- knowledge/qa/evidence/debt-hook-unverified-header-qa-receipt-2026-09-11.md knowledge/qa/evidence/debt-hook-unverified-header-suite-2026-09-11.txt`. ⛔ A QA step that must change production code STOPS and pauses for a verdict (PT v4.108 §8).
>
> **Deposits:**
> - `knowledge/qa/evidence/debt-hook-unverified-header-qa-receipt-2026-09-11.md`
> - `knowledge/qa/evidence/debt-hook-unverified-header-suite-2026-09-11.txt`
>
> **Scope:**
> - `knowledge/qa/evidence/debt-hook-unverified-header-qa-receipt-2026-09-11.md`
> - `knowledge/qa/evidence/debt-hook-unverified-header-suite-2026-09-11.txt`
>
> **Post-conditions:** the suite file's summary line is `N passed, 1 skipped` with N ≥ the DEV's count and no `failed`; Item 2's two first lines pasted; the receipt's `## Verification` table has three rows and closes with the block's own PASSED line; one QA commit carrying the two evidence files.
