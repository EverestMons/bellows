# bellows — executable: issue_verdict tool + daemon verdict-detector arms — the 522-diagnostic build; the last bare-handed lane act retired

**Date:** 2026-08-25 | **Project:** bellows | **Tier:** Medium | **Dispatch Mode:** bellows | **cycle_tier:** T2 | **Test Scope:** bellows suite | **Execution:** Step 1 (DEV) → Step 2 (QA) | **Priority:** 1

**auto_close:** false
**pause_for_verdict:** always
**qa_steps:** 2

**Depends on:** `knowledge/research/verdict-act-mechanization-2026-08-25.md` (diagnostic-522's deposit — the requirements source; its D-2 write-side contract and D-4 tool shape are binding; its Rule 27 gap table G1-G7 is this plan's change set). **CEO rulings 2026-08-25 (this session, "run the executables with the recommended options"):** Fork 1 = YES daemon auto-move of parse-valid misplaced verdicts; Fork 2 = YES malformed-WARN promotion to the terminal log; Fork 3 = NO parser widening (strict substrate + tool, the doctrine default); Fork 4 = the PLANNER_TEMPLATE line is a ROOT-repo write outside this bellows dispatch — routed to the pending root-doc follow-up plan, NOT this one; Fork 5 = YES include the offending first line in the daemon-side WARN; dedup persistence (D-5 iii) = option B, leave as-is (restart re-alerting on a stuck file is a feature). **G8 (retire the memory entry) is the PLANNER'S act after this plan closes — it is NOT in your write set and `~/.claude` is NOT reachable from your sandbox.**

## Why this exists

The verdict act requires five correct memory-recalls and four have measured failures (plans 465, 486-era, 495, 521 — including one operator committing both faults in a single act with the correct instructions indexed in memory the whole time). Every other lane act already has a tool. This plan ships the tool that makes the grammar and location correct by construction, plus the two daemon arms that stop the detectors from warning-without-acting.

## What this plan does NOT do

- **It does not restart the daemon.** The bellows.py changes are INERT until the next deliberate restart; the tool works immediately (it is invoked fresh per use). ⚠️ No restart mid-plan — the daemon executing this plan runs the old code.
- **It does not widen `check_verdict`'s grammar** (Fork 3 = NO). The strict parser becomes the guard against non-tool writes.
- **It does not touch PLANNER_TEMPLATE.md or `~/.claude`** (Fork 4 routed out; G8 is the Planner's own post-close act).

## Numbers discipline

⚠️ **Measured 2026-08-25 by the Planner against bellows main post-522-close; line numbers WILL SHIFT — every cite pairs line with anchor; re-locate by ANCHOR, assert count==1 before editing. ⚠️ CO-DISPATCH NOTE: a sibling plan (`executable-teardown-recording-precheck-evidence`) also edits bellows.py THIS SESSION in regions far from yours (teardown catch sites ~:1114-1277, precheck ~:1938, consume-time guards ~:2533-2713) — your anchors below may sit at shifted line numbers if it merged first; the ANCHORS remain unique, trust them over the numbers.**

| id | pin | value | anchor |
|---|---|---|---|
| Y1 | first-line regex, the contract | verdict.py:301 | `re.match(r"^(?:verdict:\s*)?(continue|stop)$", first_line, re.IGNORECASE)` inside `check_verdict` (def at :282) |
| Y2 | misplaced-verdict scanner | bellows.py:2570-2592 | `def _scan_misplaced_verdicts(self, pending_dir):` — WARN via `_log` at the `verdict file in wrong directory` literal; Pushover deduped by `_NOTIFIED_MISPLACED` |
| Y3 | consumption not-found site | bellows.py:2657-2659 | `verdict_result = verdict.check_verdict(plan_slug, step_number)` followed by `if not verdict_result.get("found"): continue` |
| Y4 | prefix normalization | bellows.py:2620-2624 | `for prefix in ("diagnostic-", "executable-"):` |
| Y5 | the heavy import chain | notifier.py:13 `from bellows import _log`; verdict.py imports notifier at module level | the reason the TOOL must not import verdict — measured: importing verdict loads the ~2800-line daemon module |
| Y6 | consumed-verdict rename | bellows.py:2797-2798 | `processed_path = resolved_dir / f"processed-{fname}"` |
| Y7 | house tool grammar | tools/deposit_receipt.py (positional args + argparse), tools/clear_plan.py (gated refusals before writes) | the shapes to clone |
| Y8 | suite floor | **1363 collected** | `python3 -m pytest tests/ --collect-only -q` from repo root; re-derive (the sibling plan adds ~10 tests if it merged first — your baseline is whatever you measure) |
| Y9 | glossary | knowledge/glossary.md exists (first 3d sweep, 2026-08-25) | the RUNBOOK entry's home |

## MUST-PRESERVE

- ⚠️ **NO daemon restart; no writes to lifecycle.db outside test temp DBs; never touch `verdicts/pending/` or `verdicts/resolved/` live files except through the test suite's temp dirs.**
- ⚠️ **The tool imports NOTHING from the daemon modules** (Y5) — stdlib only (`argparse`, `re`, `os`, `sys`, `pathlib`, `glob`/`pathlib.glob`, `tempfile`). The regex is CLONED with the byte-identity test (B1's test 11) pinning it to Y1's pattern string.
- ⚠️ **Auto-move (B2) moves ONLY parse-valid files** — a parse-invalid misplaced file keeps the existing WARN behavior unchanged.
- ⚠️ **`check_verdict`'s behavior is unchanged** except the shared-constant refactor (B0), which must be observationally identical — the regex OBJECT moves to a module constant, the match semantics do not change by one byte.
- ⚠️ **Anchor-based editing; blast-radius sweep mandatory in DEV (B5):** consumers of `_scan_misplaced_verdicts` behavior, `check_verdict`, and the WARN literals — enumerate test hits and force-classify each before the targeted run.
- ⚠️ **`grep` is ugrep: `-F` for literals. EVERY DATE IS A FIXED LITERAL. Worktree dispatch; deposit paths project-relative.**

## STEP 1 — DEV: the tool, the two daemon arms, the glossary line

**Role:** DEV.

**B0 — shared regex constant.** In verdict.py: hoist Y1's pattern into a module-level `VERDICT_FIRST_LINE_RE = re.compile(r"^(?:verdict:\s*)?(continue|stop)$", re.IGNORECASE)` and use it inside `check_verdict`. Observationally identical (same pattern string, same flags). This gives bellows.py (which already imports verdict) a canonical parse for B2, and gives the tool's byte-identity test its comparison target.

**B1 — `tools/issue_verdict.py`** per the D-4 spec (the deposit's D-2/D-4 sections are the requirements; follow the Y7 house grammar):
- Signature: `issue_verdict.py <plan-id-or-slug> <step> {continue|stop} [--reason TEXT | --reason-file PATH] [--force] [--pending-dir DIR] [--resolved-dir DIR]` (reason falls back to stdin when neither flag given; the dir overrides exist for tests, defaulting to the repo-resolved `verdicts/` like clear_plan.py's `--db-path` precedent — resolved stdlib-only as `Path(__file__).resolve().parent.parent / "verdicts"`, matching verdict.py:14's root without importing it).
- Id derivation: glob the pending dir for `verdict-request-*-step-<step>.md`; normalize the user's `<plan-id-or-slug>` with Y4's prefix rule; refuse with the full listing on zero or multiple matches.
- Enum refusal for any outcome word outside {continue, stop} (case-insensitive; write lowercased).
- Content by construction: line 1 = the outcome token; line 2 blank; reason from line 3.
- Atomic write: `tempfile.NamedTemporaryFile(dir=<resolved-dir>, delete=False)` + `os.rename` to `verdict-<matched-id>-step-<step>.md`.
- Overwrite guard: existing un-consumed file at target → refuse (exit 1, print path) unless `--force`.
- `processed-` collision: WARN but proceed (prior verdict was consumed; this is a new one).
- Self-verify: apply the tool's own cloned `_VERDICT_RE` to the file it just wrote (read back from disk), print the parsed outcome + file path; exit 0 only when the parse succeeds.
- Stdlib only (MUST-PRESERVE).

**B2 — auto-move arm (Y2), Fork 1.** In `_scan_misplaced_verdicts`, for each misplaced candidate: read the file, apply `verdict.VERDICT_FIRST_LINE_RE` to its first line; on match → `shutil.move` into `verdicts/resolved/` and `_log("EVENT", f"auto-moved well-formed verdict to resolved/: {fname}")`, skipping the WARN and Pushover for that file; on no-match (including empty/unreadable — a mid-edit half-write) → the existing WARN + Pushover path exactly as-is.

**B3 — malformed-WARN promotion (Y3), Forks 2+5.** At the not-found site: if the expected file exists on disk, read its first line and `_log("WARN", f"verdict file exists but unparseable: {fname} — first line: {first_line!r}", slug=plan_slug)` before the `continue`. Guard the read (unreadable file → log without the first-line clause).

**B4 — glossary RUNBOOK line (Y9).** Append to `knowledge/glossary.md` under its runbook/act section: the verdict act → `python3 tools/issue_verdict.py <plan> <step> continue|stop --reason ...` — location and grammar are the tool's job, not the operator's.

**B5 — consumer sweep + tests.** Sweep: `grep -rn -F "_scan_misplaced_verdicts" tests/`, `grep -rn -F "check_verdict" tests/`, `grep -rn -F "verdict file in wrong directory" tests/` — force-classify every hit (B2 changes the well-formed-misplaced observable behavior; any test asserting WARN-on-well-formed-misplaced is now broken-by-design and updates). New file `tests/test_issue_verdict.py` with the deposit's D-6 tests 1-12 (happy path; id derivation + normalization; zero-match, multi-match, enum, overwrite refusals; --force; atomicity; self-verify parity with `check_verdict`'s dict; regex byte-identity `tool._VERDICT_RE.pattern == verdict.VERDICT_FIRST_LINE_RE.pattern`; reason via --reason/--reason-file/stdin; processed- collision) plus daemon tests 13-15 (auto-move moves parse-valid + EVENT logged; parse-invalid NOT moved + WARN persists; malformed WARN with first-line content reaches the log — caplog).

Targeted DEV run: the new test file + every module the sweep classified as updated.

**Deposits:**
- `/Users/marklehn/Developer/GitHub/bellows/tools/issue_verdict.py`
- `/Users/marklehn/Developer/GitHub/bellows/verdict.py`
- `/Users/marklehn/Developer/GitHub/bellows/bellows.py`
- `/Users/marklehn/Developer/GitHub/bellows/knowledge/glossary.md`
- `/Users/marklehn/Developer/GitHub/bellows/tests/test_issue_verdict.py`

**Scope:**
- `/Users/marklehn/Developer/GitHub/bellows/tools/issue_verdict.py`
- `/Users/marklehn/Developer/GitHub/bellows/verdict.py`
- `/Users/marklehn/Developer/GitHub/bellows/bellows.py`
- `/Users/marklehn/Developer/GitHub/bellows/knowledge/glossary.md`
- `/Users/marklehn/Developer/GitHub/bellows/tests/`

**Commit:** `git add tools/issue_verdict.py verdict.py bellows.py knowledge/glossary.md tests/ && git commit -m "[<id>] verdict act mechanized: issue_verdict tool, auto-move arm, malformed WARN promotion, glossary runbook"` in YOUR worktree cwd.

## STEP 2 — QA: full suite + evidence, per-plan names

**Role:** QA.

**Q1 — full suite.** `python3 -m pytest tests/ -q` **from the bellows repo root as cwd**; deposit RAW output as `knowledge/qa/evidence/issue-verdict-tool/pytest_full.txt` (the per-plan convention). Self-contained accounting: total, the new file's own count, derived inherited baseline vs Y8 (re-derived — the sibling plan may have grown it); zero failures.

**Q2 — live tool rehearsal, scratch-only.** In a temp dir mimicking `verdicts/{pending,resolved}` (via the `--pending-dir`/`--resolved-dir` overrides): create a fake `verdict-request-999-step-1.md`; run the tool end-to-end for `continue`; assert the file `verdict-999-step-1.md` lands in the fake resolved/ with first line exactly `continue`; run again without `--force` → exit 1; with `--force` → success. Raw transcript into the QA report. ⚠️ NEVER against the live `verdicts/` tree.

**Q3 — change-shape check.** Greps proving: `VERDICT_FIRST_LINE_RE` defined once in verdict.py and used inside `check_verdict`; bellows.py references it in the auto-move arm; the auto-move EVENT literal present exactly once; the unparseable WARN literal present exactly once with `first_line` in the f-string; the tool contains no `import verdict`, `import bellows`, `import notifier`, `import requests` (count 0 each — zero-count probes NOT &&-chained).

**Q4 — QA report.** `knowledge/qa/evidence/issue-verdict-tool/qa-report.md` with Q1-Q3 + the G1-G7 coverage row (G8 marked: Planner's post-close act, out of sandbox reach by design).

> **QA SELF-CHECK — Rule 20.** Post the block from `/Users/marklehn/Developer/GitHub/RULE_20_SELF_CHECK_BLOCK.md` verbatim, under the banner **`Rule 20 — QA Self-Check Results`**, and close with **`PASSED — SELF-CHECK PASSED`** only if every check genuinely passed. ⚠️ Both literals are matched by `plan_lint` check (c) and neither may be paraphrased. Rule 20 block + Q1-Q4 results in the `.md`; raw suite output in `pytest_full.txt` — the two QA gates scan DIFFERENT extensions.

**Deposits:**
- `/Users/marklehn/Developer/GitHub/bellows/knowledge/qa/evidence/issue-verdict-tool/pytest_full.txt`
- `/Users/marklehn/Developer/GitHub/bellows/knowledge/qa/evidence/issue-verdict-tool/qa-report.md`

**Scope:**
- `/Users/marklehn/Developer/GitHub/bellows/knowledge/qa/evidence/issue-verdict-tool/`

**Commit:** `git add knowledge/qa/evidence/issue-verdict-tool/ && git commit -m "[<id>] qa: issue_verdict tool — full suite + rehearsal + evidence (per-plan path)"` in YOUR worktree cwd.

## Drafting Cycle
**Tier:** T2 computed — daemon-code + new tool build; full cold panel mandated at the freeze.
**Walk register:** `governance/knowledge/research/walk-register-executable-issue-verdict.md`
**Walks:** recorded in the register; cycle_check branched after each walk.
**Cold panel:** four seats (scout → discovery → execution → capstone) after the warm phase closes; findings author-verified and folded.
**Conformance (§5):** recorded at close from actual runs.
**Closing:** recorded at close.

## Cycle Manifest
tier: T2
target: tools/issue_verdict.py
class: shop-infra
reads: /Users/marklehn/Developer/GitHub/bellows/verdict.py, /Users/marklehn/Developer/GitHub/bellows/bellows.py, /Users/marklehn/Developer/GitHub/bellows/notifier.py, /Users/marklehn/Developer/GitHub/bellows/tools/clear_plan.py, /Users/marklehn/Developer/GitHub/bellows/tools/deposit_receipt.py, /Users/marklehn/Developer/GitHub/bellows/knowledge/research/verdict-act-mechanization-2026-08-25.md, /Users/marklehn/Developer/GitHub/bellows/knowledge/glossary.md
writes: tools/issue_verdict.py, verdict.py, bellows.py, knowledge/glossary.md, tests/test_issue_verdict.py, knowledge/qa/evidence/issue-verdict-tool/pytest_full.txt, knowledge/qa/evidence/issue-verdict-tool/qa-report.md
open_forks: none — the fork rulings are recorded in the header (Fork 4 routed to the root-doc plan; G8 is the Planner's post-close act)
walks: recorded at close
yields: recorded at close
validation: recorded at close
coherence: N/A

## Rule 20 — QA Self-Check Block

Step 2 is the QA step; the block is posted there per the Step 2 mandate. Step 1 is DEV-only.
