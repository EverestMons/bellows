# bellows — executable: `tools/run_check.py` — every checker's verdict normalized to a real exit code (retires four lying-channel memories at close)

**Date:** 2026-08-26 | **Project:** bellows | **Tier:** Small | **Dispatch Mode:** bellows | **cycle_tier:** T1 | **Test Scope:** targeted (the new tests) + full suite at QA | **Execution:** Step 1 (DEV) → Step 2 (QA) | **qa_steps:** 2 | **pause_for_verdict:** always

**auto_close:** false

**Depends on:** the CEO's "Proceed mechanization" (batch 2, item 1); the audit's work-list item 2; the channel facts READ FROM CODE at walk 0 (cycle_check's last-stdout-line; plan_lint's honest exit; walk_register_lint's stderr verdict + always-exit-0 lint path — verified at the source lines).

## Why this exists

Four memory entries exist solely to warn that checker channels lie; ~15 manual BAR_MET/exit-code branchings were counted in one session. One wrapper makes the channel a real exit code; the memories retire to pointers at close.

## What this plan does NOT do

- No checker is modified — the wrapper READS their real channels; their behavior is the contract. No memory writes (sandbox-denied to agents; the Planner retires at close).

## Numbers discipline

⚠️ **Measured 2026-08-26; re-measure pre-flight; mismatch → HALT; every count carries measure-record-supersede.**

| id | pin | value | anchor |
|---|---|---|---|
| R1 | tools/ | run_check.py ABSENT (`ls tools/` shows 4 entries — record; supersede with derivation) | `tools/` (repo-relative — worktree law) |
| R2 | the channels | cycle: last stdout line; lint: exit code; register: stderr `\t`-verdicts, lint path always exit 0 | the three scripts, read-only |
| R3 | live smoke target | `knowledge/decisions/Done/executable-561.md` — plan_lint exits 0 on it (verified at its deposit) | ibid. |

## STEP 1 — DEV (the tool + tests)

> **Task A — worktree discipline.** `cd "$(git rev-parse --show-toplevel)" && test -d tools && echo TREE_OK` — HALT unless TREE_OK. Probes: (i) `test -f tools/run_check.py && echo 1 || echo 0`, (ii) `test -f tests/test_run_check.py && echo 1 || echo 0`. (0,0) → full run; (1,0) → resume at Task C; (1,1) → Task D commit-check; (0,1) → HALT.
>
> **Task B — write `tools/run_check.py` EXACTLY:**
>
> ```python
> #!/usr/bin/env python3
> """run_check — one wrapper, every checker's verdict as a REAL exit code.
>
> usage: run_check.py cycle <plan.md> [--accept-continue]
>        run_check.py lint <plan.md>
>        run_check.py register <path>
>
> Exit 0 = the checker's OWN verdict channel says clean; 1 = it says failed;
> 2 = usage error or the checker itself crashed. The final line is always
> `RUN_CHECK: <mode> VERDICT=PASS|FAIL — <reason>` on stdout.
>
> Channel facts (read from the checkers' source, 2026-08-26):
> - cycle_check: verdict is the LAST STDOUT LINE (BAR_MET / CONTINUE /
>   ESCALATE:*); its exit code is 0 for both BAR_MET and CONTINUE.
> - plan_lint: the exit code IS the channel; WARN lines are advisory.
> - walk_register_lint: per-file verdicts print on STDERR as
>   `<name>\t<CONFORMANT|UNCONFORMANT>\t…`; the lint path ALWAYS exits 0.
>   A PASS here additionally requires at least one CONFORMANT line — the
>   positive control: absence of UNCONFORMANT alone can mean nothing was
>   scanned (the negative-probe law, mechanized).
> """
> import subprocess
> import sys
> from pathlib import Path
>
> SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"
>
>
> def judge_cycle(stdout, stderr, code, accept_continue=False):
>     last = stdout.strip().splitlines()[-1].strip() if stdout.strip() else ""
>     if last == "BAR_MET":
>         return "PASS", "BAR_MET"
>     if last == "CONTINUE" and accept_continue:
>         return "PASS", "CONTINUE (accepted by flag)"
>     if last == "CONTINUE":
>         return "FAIL", "CONTINUE — bar not met (pass --accept-continue for mid-cycle use)"
>     return "FAIL", f"verdict line: {last!r} (exit {code})"
>
>
> def judge_lint(stdout, stderr, code):
>     if code == 0:
>         return "PASS", "exit 0 (WARNs, if any, are advisory)"
>     return "FAIL", f"exit {code}"
>
>
> def judge_register(stdout, stderr, code):
>     bad = [ln for ln in stderr.splitlines() if "\tUNCONFORMANT" in ln]
>     good = [ln for ln in stderr.splitlines() if "\tCONFORMANT" in ln]
>     if bad:
>         return "FAIL", f"{len(bad)} UNCONFORMANT file(s): " + "; ".join(
>             ln.split("\t")[0] for ln in bad)
>     if not good:
>         return "FAIL", ("no CONFORMANT line seen — nothing was scanned, or the "
>                         "verdict channel moved (positive control failed)")
>     return "PASS", f"{len(good)} file(s) CONFORMANT, 0 UNCONFORMANT"
>
>
> def main(argv):
>     if len(argv) < 3:
>         print(__doc__)
>         return 2
>     mode, target = argv[1], argv[2]
>     flags = argv[3:]
>     script = {"cycle": "cycle_check.py", "lint": "plan_lint.py",
>               "register": "walk_register_lint.py"}.get(mode)
>     if script is None:
>         print(f"RUN_CHECK: unknown mode {mode!r}")
>         return 2
>     try:
>         out = subprocess.run(
>             [sys.executable, str(SCRIPTS / script), target],
>             capture_output=True, text=True, timeout=120,
>         )
>     except Exception as e:
>         print(f"RUN_CHECK: {mode} VERDICT=FAIL — checker crashed: {e}")
>         return 2
>     sys.stdout.write(out.stdout)
>     sys.stderr.write(out.stderr)
>     if mode == "cycle":
>         verdict, reason = judge_cycle(out.stdout, out.stderr, out.returncode,
>                                       accept_continue="--accept-continue" in flags)
>     elif mode == "lint":
>         verdict, reason = judge_lint(out.stdout, out.stderr, out.returncode)
>     else:
>         verdict, reason = judge_register(out.stdout, out.stderr, out.returncode)
>     print(f"RUN_CHECK: {mode} VERDICT={verdict} — {reason}")
>     return 0 if verdict == "PASS" else 1
>
>
> if __name__ == "__main__":
>     sys.exit(main(sys.argv))
> ```
>
> Post-probes: `"judge_register"` >= 2; `"positive control"` >= 1; `chmod +x tools/run_check.py`.
>
> **Task C — tests `tests/test_run_check.py`** (new): EIGHT tests — six over the PURE judges with captured-real-output string fixtures (provenance comments naming the source runs): cycle BAR_MET → PASS; cycle CONTINUE strict → FAIL and with accept_continue → PASS; cycle ESCALATE → FAIL; register with one `x\tUNCONFORMANT\t…` stderr line → FAIL naming it; register with only CONFORMANT lines → PASS; register with EMPTY stderr → FAIL (the positive control — the trap the wrapper exists to close); plus TWO live smokes: `lint` mode against `knowledge/decisions/Done/executable-561.md` → exit 0 and the VERDICT=PASS line; `register` mode against a walk register committed this arc (pick one under knowledge/research/, e.g. the 561 register) → the RUN_CHECK line present (either verdict — the smoke proves the pipeline, the fixtures prove the judgments; record which verdict with the derivation). Targeted run: 0 failed (record counts; supersede with derivation).
>
> **Task D — dev log + commit.** `knowledge/dev-logs/run-check-wrapper-dev-2026-08-26.md` (probe raws, targeted raw, the two smoke outputs verbatim). Commit (WORKTREE toplevel): `cd "$(git rev-parse --show-toplevel)" && git add tools/run_check.py tests/test_run_check.py knowledge/dev-logs/run-check-wrapper-dev-2026-08-26.md && git commit -m "[<id from your plan filename>] run-check-wrapper(run-check-wrapper-2026-08-26): every checker verdict as a real exit code; register positive-control mechanized" -- tools/run_check.py tests/test_run_check.py knowledge/dev-logs/run-check-wrapper-dev-2026-08-26.md && git rev-parse HEAD` — **CAPTURE_COMMIT**.
>
> **Deposits:**
> - `tools/run_check.py`
> - `tests/test_run_check.py`
> - `knowledge/dev-logs/run-check-wrapper-dev-2026-08-26.md`
>
> **Scope:**
> - `tools/run_check.py`
> - `tests/test_run_check.py`
> - `knowledge/dev-logs/run-check-wrapper-dev-2026-08-26.md`

## STEP 2 — QA (FULL suite + live behavior)

> **Item 1 — full suite.** `cd "$(git rev-parse --show-toplevel)"`; `python3 -m pytest tests/ --tb=short -q 2>&1 | cat | tee knowledge/qa/evidence/run-check-wrapper-2026-08-26/pytest_full.txt` — 0 failed (record the count; derivation vs 1494 + 8).
> **Item 2 — live behavior.** Run the COMMITTED wrapper thrice, pasting each full tail: `lint` on the R3 Done plan (VERDICT=PASS, exit 0 — capture `$?`); `cycle` STRICT on the same Done plan (whatever the honest verdict — record it with the exit); `register` on the chosen committed register (record verdict + exit; the exit MUST equal 0-iff-PASS — the wrapper's whole point, proven live). Extraction probes: `cmp` both files vs live → 0.
> **Item 3 — hygiene + receipt** `knowledge/qa/evidence/run-check-wrapper-2026-08-26/qa-receipt.md`: numstat 3 files; toplevel; reflog `-n 4` → 0 amends; per-item table, then the Rule 20 block INSIDE a "Verification"-headed section (the 556 placement law).
>
> ⚠️ **Gate note:** pytest summary named above — the gate parses; no benign override pre-declared.
>
> **Deposits:**
> - `knowledge/qa/evidence/run-check-wrapper-2026-08-26/pytest_full.txt`
> - `knowledge/qa/evidence/run-check-wrapper-2026-08-26/probes-raw.txt`
> - `knowledge/qa/evidence/run-check-wrapper-2026-08-26/qa-receipt.md`
>
> **Scope:**
> - `knowledge/qa/evidence/run-check-wrapper-2026-08-26/pytest_full.txt`
> - `knowledge/qa/evidence/run-check-wrapper-2026-08-26/probes-raw.txt`
> - `knowledge/qa/evidence/run-check-wrapper-2026-08-26/qa-receipt.md`

Rule 20 banner (byte-exact, inside the QA receipt's VERIFICATION section):

```
============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
```

## Drafting Cycle

**Tier:** T1 — pure judges + a thin runner; the channel facts sourced from the checkers' code at walk 0; the register judge mechanizes the positive-control law inside itself.

**Walk register:** `bellows/knowledge/research/walk-register-run-check-wrapper-2026-08-26.md`

**Walk 0 (context pin, measured):** the three channels at their source lines; tools/ 4 entries, run_check absent; the R3 smoke target verified at its own deposit; the retirement split (tool via the lane, the four memory pointers as the Planner's close-time act with class: stale under the 562 gate).

**Walks:**
- Weak spots:          w1 dry — every judge fail-closed traced (empty stdout → FAIL; empty register stderr → the positive-control FAIL, the exact trap the tool closes); the tab escapes become real tabs at runtime matching L358's f-string; the smokes record honest verdicts rather than predicting them.
- Destruction:         w1 dry — three-arm resume; the runner's 120s timeout + crash → exit 2, never a false PASS.
- Vulnerabilities:     w1 dry — no checker modified; both child streams relayed verbatim before the verdict line (the wrapper adds a channel, never hides one).
- Integration-record:  w1 dry — the retirement split stated with the sandbox reason; the channel facts cite their source lines.
- ACID:                w1 dry — counts clause-clothed; one pathspec-limited commit.
- **Walk 1 total: 0 findings — all five lenses dry.**
- Weak spots:          w2 dry.
- Destruction:         w2 dry.
- Vulnerabilities:     w2 dry.
- Integration-record:  w2 dry.
- ACID:                w2 dry.
- **Walk 2 total: 0 findings — all five lenses dry.**

**Closing:** ✅ **BAR MET at walk 2 — dry confirming pass, all five lenses.** T1 two-walk form; no direction-class finding; close is MANUAL (CEO-lane verdicts).

**Fold-and-deposit exactly once.**

## Cycle Manifest
tier: T1
target: bellows/tools/run_check.py
class: shop-infra
reads: /Users/marklehn/Developer/GitHub/bellows/scripts/cycle_check.py, /Users/marklehn/Developer/GitHub/bellows/scripts/plan_lint.py, /Users/marklehn/Developer/GitHub/bellows/scripts/walk_register_lint.py
writes: tools/run_check.py, tests/test_run_check.py, knowledge/dev-logs/run-check-wrapper-dev-2026-08-26.md, knowledge/qa/evidence/run-check-wrapper-2026-08-26/pytest_full.txt, knowledge/qa/evidence/run-check-wrapper-2026-08-26/probes-raw.txt, knowledge/qa/evidence/run-check-wrapper-2026-08-26/qa-receipt.md
open_forks: batch-2 item 2 (cross-machine path normalization, SERIAL after this closes); the four memory retirements = the Planner's close-time act (sandbox split, stated); the remaining ledger (reconcile_plan.py; scope_check rename; the 23 CODE rows)
walks: 2
yields: 0, 0
validation: cycle_check=BAR_MET, plan_lint=0_FAIL, fold_check=N/A
coherence: N/A
