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

⚠️ **Measured 2026-08-25 by the Planner; refreshed against bellows main post-523 (HEAD 46feb24 — the sibling teardown build HAS merged; S4-3). Line numbers WILL SHIFT — every cite pairs line with anchor; re-locate by ANCHOR, assert count==1 before editing (exception: Y6 is a context pin with a measured count of 2, see its row).**

| id | pin | value | anchor |
|---|---|---|---|
| Y1 | first-line regex, the contract | verdict.py:301 | `re.match(r"^(?:verdict:\s*)?(continue|stop)$", first_line, re.IGNORECASE)` inside `check_verdict` (def at :282) |
| Y2 | misplaced-verdict scanner | bellows.py:2734 (post-523 refresh, S2-10) | `def _scan_misplaced_verdicts(self, pending_dir):` — WARN via `_log` at the `verdict file in wrong directory` literal; Pushover deduped by `_NOTIFIED_MISPLACED` |
| Y3 | consumption not-found site | bellows.py:2821 (post-523 refresh) | `verdict_result = verdict.check_verdict(plan_slug, step_number)` followed by `if not verdict_result.get("found"): continue` |
| Y4 | prefix normalization | bellows.py:2785 (post-523 refresh) | `for prefix in ("diagnostic-", "executable-"):` |
| Y5 | the heavy import chain | notifier.py:13 `from bellows import _log`; verdict.py imports notifier at module level | the reason the TOOL must not import verdict — measured: importing verdict loads the entire daemon module (~3200 lines post-523) |
| Y6 | consumed-verdict rename | context pin only (this plan edits no rename site) | ⚠️ the literal now matches TWICE post-523 (:2969, :2993 — S1-6); both are consume-side context, neither is an edit target |
| Y7 | house tool grammar | tools/deposit_receipt.py (positional args + argparse), tools/clear_plan.py (gated refusals before writes) | the shapes to clone |
| Y8 | suite floor | **1385 collected** (re-measured post-523: 1363 + the sibling's 22) | `python3 -m pytest tests/ --collect-only -q` from repo root; re-derive — your measurement supersedes |
| Y9 | glossary | knowledge/glossary.md exists (first 3d sweep, 2026-08-25) | the RUNBOOK entry's home |

## MUST-PRESERVE

- ⚠️ **NO daemon restart; no writes to lifecycle.db outside test temp DBs; never touch `verdicts/pending/` or `verdicts/resolved/` live files except through the test suite's temp dirs.**
- ⚠️ **The tool imports NOTHING from the daemon modules** (Y5) — stdlib only (`argparse`, `re`, `os`, `sys`, `pathlib`, `glob`/`pathlib.glob`, `tempfile`). The regex is CLONED with the byte-identity test (D-6 test 10 — S1-9) pinning it to Y1's pattern string.
- ⚠️ **Auto-move (B2) moves ONLY parse-valid files** — a parse-invalid misplaced file keeps the existing WARN behavior unchanged.
- ⚠️ **`check_verdict`'s behavior is unchanged** except the shared-constant refactor (B0), which must be observationally identical — the regex OBJECT moves to a module constant, the match semantics do not change by one byte.
- ⚠️ **Anchor-based editing; blast-radius sweep mandatory in DEV (B5):** consumers of `_scan_misplaced_verdicts` behavior, `check_verdict`, and the WARN literals — enumerate test hits and force-classify each before the targeted run.
- ⚠️ **`grep` is ugrep: `-F` for literals. EVERY DATE IS A FIXED LITERAL. Worktree dispatch; deposit paths project-relative.**

## STEP 1 — DEV: the tool, the two daemon arms, the glossary line

**Role:** DEV.

**B0 — shared regex constant.** In verdict.py: hoist Y1's pattern into a module-level `VERDICT_FIRST_LINE_RE = re.compile(r"^(?:verdict:\s*)?(continue|stop)$", re.IGNORECASE)` and use it inside `check_verdict`. Observationally identical (same pattern string, same flags). This gives bellows.py (which already imports verdict) a canonical parse for B2, and gives the tool's byte-identity test its comparison target.

**B1 — `tools/issue_verdict.py`** per the D-4 spec (the deposit's D-2/D-4 sections are the requirements; follow the Y7 house grammar):
- Signature: `issue_verdict.py <plan-id-or-slug> <step> {continue|stop} [--reason TEXT | --reason-file PATH] [--force] [--pending-dir DIR] [--resolved-dir DIR]` — ⚠️ `--reason`/`--reason-file` in an argparse mutually-exclusive group (S1-5); reason falls back to stdin ONLY when stdin is not a TTY (`sys.stdin.isatty()` → refuse with a message naming the three reason sources — never hang waiting on an interactive terminal); the dir overrides exist for tests, defaulting to the repo-resolved `verdicts/` like clear_plan.py's `--db-path` precedent — resolved stdlib-only as `Path(__file__).resolve().parent.parent / "verdicts"`, matching verdict.py:14's root without importing it).
- Id derivation: glob the pending dir for `verdict-request-*-step-<step>.md`; extract each candidate's id/slug via the request-filename regex and compare STRING-EQUALITY against the Y4-normalized user arg (S2-5 — never glob-cardinality or substring: two plans paused at the same step is routine under parallel dispatch, and a uniquely-identifying arg must still resolve); refuse with the full listing only when EQUALITY matches number zero or more than one. ⚠️ Deliberate boundary (S2-6, stated not hidden): when NO request file exists (the orphan case — startup sweeps remove orphaned requests), the tool refuses BY DESIGN; the refusal message names the manual orphan-recovery lane (the reconciliation runbook) so the operator is routed, not stranded. Orphan recovery stays a rare eyes-open manual act.
- Enum refusal for any outcome word outside {continue, stop} (case-insensitive; write lowercased) — ⚠️ validate MANUALLY, not via argparse `choices` (S3-8a: choices exits 2; the refusal contract is exit 1 with the accepted values printed). Further B1 edges (S3-8): an EMPTY reason (after stripping) is refused — a verdict without reasoning is not issuable; an explicitly-passed `--resolved-dir`/`--pending-dir` that does not exist is refused (typo guard — only the DEFAULT-derived dirs may be mkdir'd); after the atomic rename, `os.chmod(final, 0o644)` (tempfile creates 0600).
- Content by construction: line 1 = the outcome token; line 2 blank; reason from line 3.
- Atomic write: `tempfile.NamedTemporaryFile(dir=<resolved-dir>, delete=False)` + `os.rename` to `verdict-<matched-id>-step-<step>.md`.
- Overwrite guard: existing un-consumed file at target → refuse (exit 1, print path) unless `--force`.
- `processed-` collision: WARN but proceed (prior verdict was consumed; this is a new one).
- Self-verify: apply the tool's own cloned `_VERDICT_RE` to the file it just wrote (read back from disk), print the parsed outcome + file path; exit 0 only when the parse succeeds — ⚠️ race arm (S2-9): if the read-back finds the file GONE, check for `processed-<name>` before reporting failure; a consumed-already verdict is SUCCESS ("consumed by the daemon during self-verify"), not an error.
- Stdlib only (MUST-PRESERVE).

**B2 — auto-move arm (Y2), Fork 1.** In `_scan_misplaced_verdicts`, for each misplaced candidate, move ONLY when ALL FOUR hold: **(i)** the FILENAME matches the consume pattern `^verdict-(.+)-step-(\d+)\.md$` (S1-8 — a content-valid file with an unconsumable name would otherwise convert one perpetual WARN into another); **(ii)** the CONTENT parses — apply `verdict.VERDICT_FIRST_LINE_RE` using check_verdict's OWN normalization (`text.strip().splitlines()[0].strip()` — S1-7: a raw-first-line read diverges on leading blanks the consumer tolerates); **(iii)** the destination is free; **(iv) FRESHNESS (S2-1): a matching `verdict-request-<slug>-step-<N>.md` exists in pending_dir** (slug/step taken from the candidate's own filename ⚠️ with the Y4 prefix normalization applied FIRST — S3-1 measured: request files always carry the normalized slug, so `verdict-executable-999-…` never matches without the strip and a consumable file WARNs forever) — the request survives a legitimate misplacement and is unlinked at consumption, so a STALE duplicate (the copy-not-move stray whose original was already consumed and processed-renamed, freeing the destination) fails this condition instead of auto-moving and resuming the plan past an un-adjudicated pause via the slug-only consume match. **Destination derivation (S1-2): `Path(pending_dir).parent / "resolved"` — sibling-of-the-argument, NEVER a BELLOWS_ROOT-derived absolute (a root-derived path makes the tests move temp files into the LIVE tracked verdicts/resolved/).** ⚠️ Guard scope (S2-2): the try/except wraps the WHOLE per-file handling — read + parse + move — not the move alone; an empty/whitespace file makes the naive `splitlines()[0]` raise IndexError (measured), and the daemon's main loop catches KeyboardInterrupt ONLY — use check_verdict's own `if not lines` shape and route every exception to the WARN path, never raise (S1-3: the call chain runs inside the daemon's bare `while True:` rescan loop). Before the move, `resolved.mkdir(parents=True, exist_ok=True)` (S2-7); `_log("EVENT", f"auto-moved well-formed verdict to resolved/: {fname}")`, skipping the WARN and Pushover for that file. Any condition failing (including empty/unreadable — a mid-edit half-write) → the existing WARN + Pushover path exactly as-is.

**B3 — malformed-WARN promotion (Y3), Forks 2+5.** At the not-found site: if the expected file exists on disk — ⚠️ deriving the path from the SAME `resolved_dir` variable the consume loop already lists, NOT a second independent resolution (S2-4: check_verdict reads `verdict.VERDICTS_DIR` while the loop holds its own `resolved_dir`; tests that patch only one produce spurious WARNs for parse-valid files — the NEW tests exercising B3 must patch BOTH; the existing integration test needs no change, see B5's measured expectation — S4-1) — read its first line and `_log("WARN", f"verdict file exists but does not parse as a verdict: {fname} — first line: {first_line!r}", slug=plan_slug)` before the `continue` (the wording covers the empty-file and malformed cases without mislabeling). Guard the read (unreadable/empty file → log without the first-line clause).

**B4 — glossary entry (Y9), recast per S1-1.** ⚠️ The glossary's own discriminator (glossary.md:3) routes RUNBOOK content to CLAUDE.md, which is OUT of this plan's scope — do NOT write a runbook section. Append a DEFINITION entry following the `## release act` precedent (glossary.md:15): `## verdict act` — the Planner's continue/stop adjudication of a paused step, written as `verdicts/resolved/verdict-<id>-step-<N>.md`; since 2026-08-25 performed via `tools/issue_verdict.py` (location and grammar correct by construction — the bare-handed form is retired).

**B5 — consumer sweep + tests.** Sweep: `grep -rn -F "_scan_misplaced_verdicts" tests/` and `grep -rn -F "check_verdict" tests/` are the real nets — ⚠️ the WARN-literal grep returns 0 hits (S1-11: tests assert different substrings; remember a ugrep zero-count EXITS 1 — run it un-chained and treat 0 as "no direct literal consumers", not as sweep-complete); force-classify every hit from the two real nets — ⚠️ measured expectation (S3-5): all 7 existing test_misplaced_verdicts tests pass UNMODIFIED (their fixtures have no request files, so the condition-(iv) freshness gate routes them down the unchanged WARN path), and the existing integration test needs NO dual patch (its resolved/ is empty); only the NEW tests exercising the auto-move + B3 (13/13b/15) patch `verdict.VERDICTS_DIR` alongside the loop's dir. If your build breaks an existing test, that is a FINDING against your implementation, not an expected update. New file `tests/test_issue_verdict.py` with the deposit's D-6 tests 1-12, adapted per panel: happy path; id derivation + normalization; zero-match refusal; ⚠️ test 4 REPLACED (S3-3): under the equality rule a true multi-match is structurally impossible (same slug+step = same filename) — the replacement is the UNIQUE-RESOLUTION test: two requests paused at the same step, the arg resolves exactly one; enum + overwrite refusals; --force; atomicity operationalized as the assertable set (S3-7): temp file created IN the destination dir, an injected write failure leaves nothing at the final path, no .tmp remnant after success; self-verify parity with `check_verdict`'s dict; regex byte-identity on `.pattern` AND `.flags`; reason via --reason/--reason-file/stdin; processed- collision plus daemon tests, numbered explicitly (S4-2): **13** = auto-move moves parse-valid + EVENT logged; **13b** = stale duplicate (no matching pending request) NOT moved — the condition-(iv) arm; **14** = parse-invalid NOT moved + WARN persists; **15** = malformed WARN with first-line content reaches the output — ⚠️ capsys, NOT caplog (S2-3): `_log` print()-falls-back when the "bellows" logger has no handlers; house pattern is capsys 7/7. The `verdict.VERDICTS_DIR` dual patch applies to 13b and 15 (the measured minimum — patching it in 13/14 too is harmless). The byte-identity test compares `.pattern` AND `.flags` (S2-8 — pattern-only lets an IGNORECASE drift pass).

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

**Commit:** `git add tools/issue_verdict.py verdict.py bellows.py knowledge/glossary.md tests/ && git commit -m "[<id>] verdict act mechanized: issue_verdict tool, auto-move arm, malformed WARN promotion, glossary entry"` in YOUR worktree cwd.

## STEP 2 — QA: full suite + evidence, per-plan names

**Role:** QA.

**Q1 — full suite.** `python3 -m pytest tests/ -q` **from the bellows repo root as cwd**; deposit RAW output as `knowledge/qa/evidence/issue-verdict-tool/pytest_full.txt` (the per-plan convention). Self-contained accounting: total, the new file's own count, derived inherited baseline vs Y8 (re-derived — the sibling plan may have grown it); zero failures.

**Q2 — live tool rehearsal, scratch-only.** In a temp dir mimicking `verdicts/{pending,resolved}` (via the `--pending-dir`/`--resolved-dir` overrides): create a fake `verdict-request-999-step-1.md`; run the tool end-to-end for `continue` **with `--reason "rehearsal"` explicitly (S1-5: no bare-stdin invocation in QA)**; assert the file `verdict-999-step-1.md` lands in the fake resolved/ with first line exactly `continue`; run again without `--force` → exit 1; with `--force` → success. Raw transcript into the QA report. ⚠️ NEVER against the live `verdicts/` tree.

**Q3 — change-shape check.** Greps proving: `VERDICT_FIRST_LINE_RE` defined once in verdict.py and used inside `check_verdict`; bellows.py references it in the auto-move arm; the auto-move EVENT literal present exactly once; the unparseable WARN: the FULL with-first_line f-string literal `verdict file exists but does not parse as a verdict: {fname} — first line: {first_line!r}` present exactly once, and the base phrase present exactly twice (S3-6: the natural shape is two `_log` calls — with and without the first-line clause); the tool contains no daemon-module import in EITHER form — probe with LINE-START-ANCHORED regex (`grep -cE "^(import|from) (verdict|bellows|notifier|requests|lifecycle)\b" tools/issue_verdict.py` == 0) — ⚠️ S3-2 measured: a bare `-F "from verdict"` probe false-positives on the mandated clone-provenance COMMENT (`# Cloned from verdict.py::…`); anchor to statements, and keep zero-count probes un-&&-chained.

**Q4 — QA report.** `knowledge/qa/evidence/issue-verdict-tool/qa-report.md` with Q1-Q3 + the G1-G7 coverage row — ⚠️ G7's row describes the shipped DEFINITION entry (`## verdict act`, the S1-1 recast), NOT the deposit's original "RUNBOOK entry" wording (S4-4); G8 marked: Planner's post-close act, out of sandbox reach by design.

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
**Walks:** walk 0 pinned; **walks 1–2 complete** (yields 1 → 0, warm close).
**Cold panel: CONVENED AND CLOSED** — four seats (scout 11 / discovery 10 / execution 8 / capstone 4 + sweep), 33 findings, HIGH series 3 → 2 → 0 → 0; the execution seat built the full tool + both daemon arms in scratch (import-clean, CLI rehearsal byte-exact, 1401 green); capstone's NOT-READY (the B3↔B5 fold contradiction) discharged by its folds + a dry sweep. Every finding author-verified before folding; per-seat tables in the register.
**Direction verdict (after walk 1): PROCEED.** Tested, not judged.
- Weak spots:          w1 1 folded; w2 dry; panel folds per register
- Destruction:         w1 dry; w2 dry
- Vulnerabilities:     w1 dry; w2 dry
- Integration-record:  w1 dry; w2 dry — close obligations discharged at this freeze
- ACID:                w1 dry; w2 dry; post-capstone sweep dry
**Conformance (§5):** recorded at the freeze from actual runs: walk_register_lint CONFORMANT (verdict channel, branched-on); cycle_check BAR_MET post-finalization (verdict channel, branched-on); plan_lint 0 FAIL at the lintmirror deposit path.
**Closing:** **panel closed, capstone discharged — FREEZE.** Warm 1 → 0; panel 11 → 10 → 8 → 4(+sweep 0). The deposit travels the lane: receipt ritual → staged `ready-` → class shop-infra HOLD → release via `clear_plan.py --release-class-hold` under the CEO's "run the executables" directive of 2026-08-25 → claim. First live use of the tool this plan ships: its OWN step verdicts, once step 1's teardown lands it on main.

## Cycle Manifest
tier: T2
target: tools/issue_verdict.py
class: shop-infra
reads: /Users/marklehn/Developer/GitHub/bellows/verdict.py, /Users/marklehn/Developer/GitHub/bellows/bellows.py, /Users/marklehn/Developer/GitHub/bellows/notifier.py, /Users/marklehn/Developer/GitHub/bellows/tools/clear_plan.py, /Users/marklehn/Developer/GitHub/bellows/tools/deposit_receipt.py, /Users/marklehn/Developer/GitHub/bellows/knowledge/research/verdict-act-mechanization-2026-08-25.md, /Users/marklehn/Developer/GitHub/bellows/knowledge/glossary.md
writes: tools/issue_verdict.py, verdict.py, bellows.py, knowledge/glossary.md, tests/test_issue_verdict.py, knowledge/qa/evidence/issue-verdict-tool/pytest_full.txt, knowledge/qa/evidence/issue-verdict-tool/qa-report.md
open_forks: none — the fork rulings are recorded in the header (Fork 4 routed to the root-doc plan; G8 is the Planner's post-close act)
walks: 2
yields: 1, 0
panel: scout 11 / discovery 10 / execution 8 / capstone 4 + sweep 0
validation: cycle_check=BAR_MET, plan_lint=0_FAIL, fold_check=N/A
coherence: N/A

## Rule 20 — QA Self-Check Block

Step 2 is the QA step; the block is posted there per the Step 2 mandate. Step 1 is DEV-only.
