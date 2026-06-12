# Manual Fix Prompt — Steps-Table Coverage + turns Passthrough (implements diagnostic 6)
**Date:** 2026-06-12 | **Mode:** Claude Code auto mode, manual run (NOT Bellows-dispatched) | **Project:** /Users/marklehn/Developer/GitHub/bellows

Read the Bellows DEV specialist file in `agents/` first. Then read `knowledge/research/steps-table-coverage-forensics-2026-06-12.md` (diagnostic 6) IN FULL — it is the AUTHORITATIVE artifact for every file:line specific in this task; its Gap Assessment (G1–G4) and Verification Blocks (V1–V5) define the work. Re-verify each Verification Block at edit time before trusting its line numbers.

## Precondition — clean main
Run `git status --porcelain`. Commit any pending lifecycle artifacts (the `Done/diagnostic-6.md` move, `processed-verdict-6-step-1.md`) with message `chore: lifecycle artifacts (diagnostic 6 close)`. Check `git ls-files bellows/lifecycle.db | wc -l` — if 0, the DB is untracked/ignored; leave it that way. Do not start the fix on a dirty tree.

## DEV — three gaps, scope is exactly these files: `bellows.py`, `parser.py`, `tests/` (conftest.py only if needed)
- **G1 (resume-path plan_id recovery):** at the mint-gate conditional (diagnostic V2 locates it), add the resume branch: when the filename starts with `in-progress-`, recover the integer plan_id from the id-canonical form `in-progress-<type>-<id>.md`. MUST tolerate legacy slug+date in-progress names indefinitely: if no integer id parses, plan_id stays None and all lifecycle writes degrade silently exactly as today — no exception, no WARN spam. Recovering plan_id also restores the `_id_tag_instruction` on resume (G4) — verify, change nothing extra.
- **G2 (parser):** extract `num_turns` from the result event into the parsed dict as `turns` (diagnostic V5 proves the field exists in raw output).
- **G3 (callsites):** pass `turns=parsed.get("turns")` at BOTH `record_step_end` callsites the diagnostic names. Do not add or modify any other lifecycle write.
The diagnostic is authoritative for all line numbers and column names; if current code diverges from it, stop work on that gap and report the divergence in your receipt instead of improvising.

## Tests
Add unit tests: (a) plan_id recovery from `in-progress-executable-4.md` → 4 and `in-progress-diagnostic-12.md` → 12; (b) legacy name `in-progress-executable-foo-bar-2026-05-28.md` → None, no exception; (c) parser maps `num_turns` → `turns`; (d) `record_step_end` receives the turns value end-to-end (mock or fixture per repo pattern). Then run the FULL suite with `timeout 600 pytest tests/` to an explicit pass/fail and READ THE TAIL — never infer green from a subset or collect count.

## QA verification (same session, after DEV complete)
Produce a verification table in the receipt: one row per gap (G1–G4) with the grep or test evidence that it landed, plus re-run diagnostic V2 and V3 greps and show they now reflect the fix, plus the full-suite tail. State explicitly: live resume-path verification is NOT possible in this session — the first multi-step Bellows plan after daemon restart is the live canary (expect 2 step rows, turns populated, [id] tags on both steps' commits).

## Closeout
- Append a BACKLOG.md Open entry: "Added 2026-06-12: plans.lifecycle_state intermediate states (in_progress, awaiting_verdict) are never written — only close/halt/abandon update the column; a verdict-pending plan reads 'claimed'. Canonical query 3 unaffected (keys on closed_at). Either write intermediate states or document the column as coarse. (Observed: plan 6, 2026-06-12.)"
- Commit all work: subject `fix: recover plan_id on resume path + num_turns passthrough`, body MUST contain the line `implements diagnostic 6` and `manual run — no lifecycle rows for this execution`.
- Final receipt flags for CEO: (1) daemon restart required — no hot reload; (2) this run was manual, so no derivations row exists for the diagnostic-6 lineage (commit body carries it); (3) name the live-canary expectation above.
