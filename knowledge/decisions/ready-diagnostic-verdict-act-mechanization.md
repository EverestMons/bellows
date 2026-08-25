# bellows — diagnostic: mechanize the verdict act — the last bare-handed lane act, its recurring form failures, and the issue_verdict tool shape

**Date:** 2026-08-25 | **Project:** bellows | **Tier:** Small | **Dispatch Mode:** bellows | **cycle_tier:** T1 | **Test Scope:** none (read-only diagnostic; writes one research doc) | **Execution:** Step 1 (DIAGNOSTIC) | **Priority:** 1

**auto_close:** false
**pause_for_verdict:** after_step_1

**Depends on:** the plan-521 verdict double-fault of 2026-08-25 (CEO-witnessed live stall) and the memory entry `bellows-verdict-file-id-based`, which documented BOTH faults in advance and did not prevent them. **The measured defect this characterizes:** issuing a verdict is the only Bellows lane act with no tool — the operator hand-writes a file whose directory (`resolved/`, inverted from intuition), filename key (minted id, not slug), and first-line grammar (bare `continue`/`stop`) are each enforced only by parser REJECTION plus human memory. The class has now recurred across at least four incidents on four days (misplaced-verdict warnings on 2026-08-19/21/25; malformed first line on 2026-08-20 and 2026-08-25), including one operator repeating both faults in a single act with the correct instructions sitting in an indexed memory. The E-family doctrine already answers this shape: the deposit act got `deposit_receipt.py`, the release act got `clear_plan.py`, the override act got `--override-gate` — the verdict act predates the doctrine and was never retrofitted.

## Why this exists

A correctness rule that lives in operator memory is not enforced — the 521 stall proved the memory entry can be complete, indexed, three days old, and still unconsulted at the act. Both failure modes are also detection-without-correction on the daemon side: `_scan_misplaced_verdicts` identifies a response file in `pending/`, states exactly where it belongs, and then warns every 30 seconds forever instead of acting; the malformed-content WARN goes to stderr (absent from the terminal log the Planner tails) and a once-per-process Pushover whose dedup set forgets on restart. This diagnostic maps the write-side surface, the detection-only sites, and the incident history, and settles the tool shape (`tools/issue_verdict.py`) plus the daemon-side posture so a follow-up executable can retire the memory-reliant act.

## What this plan does NOT do

- **It writes NO code.** One research deposit with a Rule 27 gap table.
- **It does not widen the parser.** Whether `check_verdict`'s strict first-line grammar should tolerate more forms is a D-7 fork with the doctrine's default stated (strict substrate + sanctioned tool, the E2 precedent), never decided silently.
- **It does not touch the E4 conditioning path.** The tool writes the file; the daemon's gate re-check and Gap-1b guard judge it exactly as before.

## Numbers discipline

⚠️ **Measured 2026-08-25 by the authoring session against bellows main post-521-close, daemon PID 26078; RE-DERIVE each — yours supersede and you say so.**

| id | pin | value | probe |
|---|---|---|---|
| V1 | the strict consumption contract | `check_verdict` (verdict.py:282-314) globs ONLY `verdicts/resolved/verdict-{slug}-step-{N}.md`; first-line regex `^(?:verdict:\s*)?(continue|stop)$` IGNORECASE; anything else → `{"found": False}` and the plan waits forever | read verdict.py:282-314; the consumption caller at bellows.py:2604-2659 |
| V2 | misplacement: detection without correction | `_scan_misplaced_verdicts` (bellows.py:2570-2592) names the exact expected location in its WARN and never moves or consumes the file; WARN repeats every scan cycle; Pushover once per (fname, reason) via in-memory `_NOTIFIED_MISPLACED` | read the function; live evidence: 15 WARN lines for `verdict-521-step-1.md` in `logs/terminal/bellows-2026-08-25.log` |
| V3 | malformed: the WARN misses the terminal log | `_notify_malformed_verdict` (verdict.py:266-279) is Pushover-only; the malformed WARN is `_log_stderr` — `grep -c -F "verdict file malformed" logs/terminal/*.log` → **0** despite the 2026-08-25 malformed file | positive control: `grep -c -F "verdict file in wrong directory" logs/terminal/bellows-2026-08-25.log` → 15 (the misplaced WARN DOES reach the terminal log) |
| V4 | incident history | misplaced-verdict WARN lines on THREE days: 2026-08-19 (3), 2026-08-21 (22), 2026-08-25 (15); malformed first line measured 2026-08-20 (diag-486) and 2026-08-25 (plan 521, `# Verdict` header) | `grep -c -F "verdict file in wrong directory" logs/terminal/*.log` per file (absolute paths); the two malformed cases are author-attested via the D-1 quote — their own log lines went to stderr (V3), so NO terminal-log evidence exists, which is itself the V3 finding |
| V5 | the tool gap | `tools/` holds exactly `clear_plan.py` + `deposit_receipt.py`; deposit→receipt tool, release→clear tool, override→`--override-gate` arm, **verdict→no tool** | `ls tools/`; the E3/E4 acts in `eluvian-path-rulings-2026-08-24.md` |
| V6 | the safe filename key | consumption normalizes `diagnostic-`/`executable-` prefixes off the slug (bellows.py:2620-2624) and matches the pending request `verdict-request-{id}-step-{N}.md`; the request filename is therefore the authoritative source of the id at verdict time | read bellows.py:2609-2631; live: `verdict-request-521-step-1.md` existed while the plan file was `verdict-pending-diagnostic-521.md` |
| V7 | verdict files are git-tracked | `git ls-files verdicts/resolved` matches `processed-verdict-*.md` files — a tool's write enters repo porcelain and rides the wrap's `[2/bellows]` step | `git ls-files verdicts/resolved | head`; count them |
| V8 | notification dedup forgets on restart | `_NOTIFIED_MISPLACED` (bellows.py:33) and `_NOTIFIED_MALFORMED` (verdict.py:17) are in-memory sets — "notified once" claims reset at every daemon restart | read both declarations; no persistence anywhere in either file |

## MUST-PRESERVE

- ⚠️ **READ-ONLY.** The single deposit is the write set. No code edits, no DB writes, no moving any verdict file.
- ⚠️ **Every claim cites file:line in CURRENT code**; every absence claim carries a positive control.
- ⚠️ **EVERY DATE IS A FIXED LITERAL.** **`grep` is ugrep: `-F` for literals.**
- ⚠️ **THE SPLIT-PATH LAW (proven on 521):** your dispatch worktree contains only TRACKED files — `logs/` and `lifecycle.db` are gitignored and ABSENT from it. Every live-state read (the terminal logs, the DB) MUST use the absolute live-checkout path under `/Users/marklehn/Developer/GitHub/bellows/`. `verdicts/resolved/*.md` ARE tracked (V7) and readable either way. A relative probe against an untracked target returns a confident false absence. Only the deposit write (and its commit) is worktree-relative.
- ⚠️ **The lifecycle DB is opened read-only** (`sqlite3 "file:...lifecycle.db?mode=ro"`); the daemon is live on it.
- ⚠️ **Worktree dispatch; deposit path project-relative.**

## STEP 1 — DIAGNOSTIC: census the act, the detectors, the history; settle the tool shape

**Role:** DIAGNOSTIC.

Produce `/Users/marklehn/Developer/GitHub/bellows/knowledge/research/verdict-act-mechanization-2026-08-25.md` (project-relative in your worktree) settling AT LEAST the following, each grounded in file:line, with a Rule 27 gap table:

**D-1 — the failure-class census.** Reconstruct each incident from the terminal logs: the three misplacement days (V4 counts per log file, which plan each belonged to where recoverable), the two malformed cases, and the 521 double-fault timeline. ⚠️ **Do NOT read `~/.claude` — the sandbox denies daemon-dispatched agents that path (the measured 520 context-boundary lesson); the memory entry's recurrence evidence is quoted for you here instead:** *"§1a (wrong directory) now measured THREE times (435-era, 495 on 2026-08-21, 521 on 2026-08-25), §1b-class (bad first line — `# Verdict` markdown header) again on 521, BOTH in one verdict act, with this memory in the index the whole time."* Treat that quote as author-attested input; re-verify its code claims against current code. For the 521 timeline, distinguish log-verifiable points (WARNs 09:36:44→09:41:45 every 30s; consumption 09:48:47; the pause 09:33:10) from author-attested points that NO log records (the initial misplaced write ~09:34-35, the move ~09:42, the malformed rewrite ~09:45) — the unrecordability of the malformed-rewrite moment is ITSELF V3's gap; state it as such. State the full list of decisions the bare-handed act requires of the operator (directory, filename key, id-vs-slug, first-line grammar, reason placement) — each one a memory-reliant failure point, each measured failing at least once.

**D-2 — the write-side contract, exhaustively.** Everything a correct verdict write must satisfy, from code: the exact glob (V1), the filename normalization (V6), the first-line regex verbatim, what becomes `reason` (lines 2+), the rename-to-`processed-` on consumption, the E4 conditioning re-check and Gap-1b guard that judge the CONTENT downstream (cite lines; the tool must not and cannot bypass these — say why: it only writes the file the daemon independently judges). This section is the tool's requirements spec.

**D-3 — detection-without-correction census.** Both detector sites (V2, V3) classified on: what they know at detection time, what they do, what they COULD do with what they know, and every channel's reach (terminal log vs stderr vs Pushover; V8's restart-forgetting dedup). Name the asymmetry: the misplaced detector knows the file's correct destination and full content yet only warns — the print-not-branch class running inside the daemon itself. State for each detector whether auto-correction is safe: for a WELL-FORMED misplaced file, what could go wrong if the daemon moved it (races with an operator mid-edit; a half-written file; the request file it pairs with); for a malformed file, why auto-correction is impossible (intent unknown) and what the honest fallback is (a terminal-log ERROR, not stderr; a persistent notification).

**D-4 — the tool shape: `tools/issue_verdict.py`.** The requirements spec from D-2 turned into a CLI, following the house tool grammar (`deposit_receipt.py`'s argparse shape, `clear_plan.py`'s gated-act precedent): proposed signature `issue_verdict.py <plan-id-or-slug> <step> {continue|stop} (--reason-file PATH | --reason TEXT | stdin)`; the tool derives the authoritative id by globbing `verdicts/pending/verdict-request-*-step-<step>.md` and matching (V6) — refusing with a listing when zero or multiple match; constructs the file so the grammar holds BY CONSTRUCTION (first line exactly the outcome token; reason from line 3); writes atomically (temp + rename) into `resolved/`; then **self-verifies by importing and calling `verdict.check_verdict(slug, step)` on its own write and printing the parse outcome** — the instrument-the-checker law: the tool's success claim is the consumer's own parse, not the tool's opinion. State what the tool must REFUSE: a verdict for a step with no pending request; an outcome word not in the enum; overwriting an existing un-consumed verdict file without `--force`. State idempotence and the `processed-` collision case. **Verify the import surface:** what importing `verdict` costs in tool context (module-level constants like `VERDICTS_DIR` resolution, the `notifier` import chain and any network-capable module it pulls) — the tool must be able to call `check_verdict` without side effects; if the chain is heavy, state the alternative (re-implement the 3-line parse regex in the tool WITH a test asserting it stays byte-identical to verdict.py's — the clone-drift cost stated honestly). Estimate LOC and the test list.

**D-5 — daemon-side posture.** The D-7 forks' factual groundwork: **(i)** auto-move of well-formed misplaced files — enumerate the race windows from D-3 and the mitigation (parse-validate BEFORE moving; only move files whose parse succeeds; log EVENT not WARN); **(ii)** promote the malformed WARN from stderr to the terminal `_log` channel (V3's gap — one-line change, name the exact site); **(iii)** whether `_NOTIFIED_*` dedup should persist (V8) or whether tool-mechanization makes the notification layer's reliability moot; **(iv)** the memory entry's retirement path once the tool ships: which parts become the tool's `--help`/refusal messages, which become a `knowledge/glossary.md` RUNBOOK line (the R2 discriminator: TRAP→CODE), and what if anything remains genuinely memory-worthy. Do not decide the forks — cost each option.

**D-6 — test surface.** The follow-up executable's tests: tool happy path (file lands in resolved/, check_verdict parses it, first line exact); id-derivation from the request file incl. the zero-match and multi-match refusals; the enum refusal; the no-request refusal; the overwrite guard; atomicity (no partial file visible at the final path); self-verification output asserts the consumer's parse; plus the daemon-side items IF the D-7 forks approve them (auto-move only-when-parseable; malformed WARN reaches the terminal log — a caplog/log-file assertion). Regression floor: current suite count, re-derived (last known 1363 + 521-era growth; measure with `--collect-only -q`).

**D-7 — open questions.** The forks for the CEO, each with D-5's costs attached: (1) daemon auto-move of parse-valid misplaced verdicts — yes/no; (2) malformed-WARN channel promotion — yes/no (recommend yes; trivial); (3) parser tolerance widening (e.g. accept a `# Verdict`-headed file whose first non-header line matches) — the doctrine default is NO (strict substrate + tool), state it; (4) whether the wrap ritual or PLANNER_TEMPLATE gains a line mandating the tool for all future verdicts (the fixing-the-instruction-is-not-the-practice caveat: the tool's existence plus the parser's strictness is the enforcement; a template line is documentation, not a guard). Anything NEW the census surfaces — LISTED, never decided silently.

**Post-conditions:** D-1 through D-6 each with ≥1 file:line citation; D-7 present with all four forks; the V1-V8 pins each re-derived or explicitly superseded with the measurement shown; a Rule 27 gap table enumerating every change site the executable will touch.

**Deposits:**
- `/Users/marklehn/Developer/GitHub/bellows/knowledge/research/verdict-act-mechanization-2026-08-25.md`

**Scope:**
- `/Users/marklehn/Developer/GitHub/bellows/knowledge/research/verdict-act-mechanization-2026-08-25.md`

**Commit:** `git add knowledge/research/verdict-act-mechanization-2026-08-25.md && git commit -m "[<id>] diag: verdict act mechanization — bare-hand census, detector gaps, issue_verdict tool shape"` in YOUR worktree cwd. `<id>` from your plan filename.

## Drafting Cycle
**Tier:** T1 computed — read-only single-deposit diagnostic.
**Walk register:** `governance/knowledge/research/walk-register-diagnostic-verdict-act-mechanization.md`
**Walks:** walk 0 pinned; **walks 1–3 complete** — five lenses each, sequential; walk 1 folded 3 (incl. the HIGH ~/.claude sandbox-boundary W1-1), walk 2 folded 1 (fold-damage repair: V4's probe cited the source W1-1 removed), walk 3 dry across all five lenses.
**Direction verdict (after walk 1): PROCEED.** Tested, not judged: three instruction folds; no premise failed; the incident record binds; the tool-retrofit shape stands.
- Weak spots:          w1 1 folded — instruction 1 / record 0; w2 dry; w3 dry
- Destruction:         w1 1 folded — instruction 1 / record 0 (HIGH); w2 dry; w3 dry
- Vulnerabilities:     w1 1 folded — instruction 1 / record 0; w2 1 folded — instruction 1 / record 0; w3 dry
- Integration-record:  w1 dry (close obligation tracked); w2 dry; w3 dry — cycle block finalized at close
- ACID:                w1 dry; w2 dry; w3 dry
**Cold panel: NOT convened, decided with reasoning** — the E-family rule: panels earn their cost on builds; read-only diagnostics 515/517/519/521 each closed on warm walks alone.
**Conformance (§5):** recorded at the walk-3 close from actual runs: walk_register_lint CONFORMANT (verdict channel, branched-on); cycle_check BAR_MET post-finalization (verdict channel, branched-on); plan_lint 0 FAIL at the lintmirror deposit path before the move.
**Closing:** **walk 3 met the bar — all five lenses dry.** Instruction series **3 → 1 → 0**. The cycle is CLOSED; the deposit travels the lane with the receipt ritual → staged as `ready-` (the 521 lane lesson) → predicted depositor auto-clear (class read-only) → claim.

## Cycle Manifest
tier: T1
target: knowledge/research/verdict-act-mechanization-2026-08-25.md
class: read-only
reads: /Users/marklehn/Developer/GitHub/bellows/verdict.py, /Users/marklehn/Developer/GitHub/bellows/bellows.py, /Users/marklehn/Developer/GitHub/bellows/notifier.py, /Users/marklehn/Developer/GitHub/bellows/tools/clear_plan.py, /Users/marklehn/Developer/GitHub/bellows/tools/deposit_receipt.py, /Users/marklehn/Developer/GitHub/bellows/logs/terminal/bellows-2026-08-19.log, /Users/marklehn/Developer/GitHub/bellows/logs/terminal/bellows-2026-08-21.log, /Users/marklehn/Developer/GitHub/bellows/logs/terminal/bellows-2026-08-25.log, /Users/marklehn/Developer/GitHub/bellows/verdicts/ledger.jsonl, /Users/marklehn/Developer/GitHub/governance/knowledge/research/eluvian-path-rulings-2026-08-24.md, /Users/marklehn/Developer/GitHub/bellows/knowledge/glossary.md
writes: knowledge/research/verdict-act-mechanization-2026-08-25.md
open_forks: none authored here — the four forks land in D-7 for the CEO
walks: 3
yields: 3, 1, 0
validation: cycle_check=BAR_MET, plan_lint=0_FAIL, fold_check=N/A
coherence: N/A

## Rule 20 — QA Self-Check Block

This step is DIAGNOSTIC-only; no QA agent runs. The Rule 20 self-check block is N/A for this step. Verification happens at the Planner's Rule 22 substance check after verdict consumption.
