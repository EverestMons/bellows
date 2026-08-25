# Verdict Act Mechanization — Bare-Hand Census, Detector Gaps, issue_verdict Tool Shape

**Date:** 2026-08-25 | **Plan:** 522 | **Type:** DIAGNOSTIC

---

## V-Pin Re-Derivation

All pins re-derived 2026-08-25 against bellows main post-521-close, daemon PID 26078.

| Pin | Diagnostic claim | Re-derived value | Source |
|-----|-----------------|------------------|--------|
| V1 | `check_verdict` globs `verdicts/resolved/verdict-{slug}-step-{N}.md`; first-line regex `^(?:verdict:\s*)?(continue\|stop)$` IGNORECASE; mismatch → `{"found": False}` | **CONFIRMED** — verdict.py:282-314; glob at :285-286, regex at :301, mismatch returns at :307 | read verdict.py:282-314 |
| V2 | `_scan_misplaced_verdicts` names exact expected location, never moves file; WARN repeats every scan cycle; Pushover once per (fname, reason) via `_NOTIFIED_MISPLACED` | **CONFIRMED** — bellows.py:2570-2592; WARN at :2582 via `_log` (terminal log channel); Pushover at :2586-2589; dedup at :2583-2584 via `_NOTIFIED_MISPLACED` (bellows.py:33) | read bellows.py:2570-2592; live: 15 WARN lines for verdict-521-step-1.md in bellows-2026-08-25.log |
| V3 | `_notify_malformed_verdict` is Pushover-only; malformed WARN is `_log_stderr` — `grep -cF "verdict file malformed" logs/terminal/*.log` → 0 | **CONFIRMED** — verdict.py:266-279 (Pushover); :303 uses `_log_stderr` which prints to sys.stderr (:260-263), NOT `_log` which routes through `logging.getLogger("bellows")` (bellows.py:253-257) to the terminal log. `grep -cF "verdict file malformed" logs/terminal/*.log` → 0 across all 14 log files. Positive control: `grep -cF "verdict file in wrong directory" logs/terminal/bellows-2026-08-25.log` → 15 |
| V4 | Misplaced-verdict WARNs on three days; malformed on two days | **CONFIRMED with plan IDs**: 2026-08-19: 3 WARNs, plan 465; 2026-08-21: 22 WARNs, plan 495; 2026-08-25: 15 WARNs, plan 521. Malformed: 2026-08-20 (diag-486 era, author-attested), 2026-08-25 (plan 521 `# Verdict` header, author-attested). Extracted plan IDs via `grep -oP 'verdict-\d+-step-\d+\.md'` per log file |
| V5 | `tools/` holds `clear_plan.py` + `deposit_receipt.py` only; verdict → no tool | **CONFIRMED** — `ls tools/` returns exactly `clear_plan.py` and `deposit_receipt.py` |
| V6 | Consumption normalizes `diagnostic-`/`executable-` prefixes; request filename is authoritative source of id | **CONFIRMED** — bellows.py:2620-2624 strips prefixes; pending request file at :2625 uses `verdict-request-{lookup_slug}-step-{step_number}.md` |
| V7 | Verdict files are git-tracked | **CONFIRMED** — `git ls-files verdicts/resolved \| wc -l` → 1500 |
| V8 | Notification dedup forgets on restart | **CONFIRMED** — `_NOTIFIED_MISPLACED` at bellows.py:33 (`set[tuple[str, str]]`), `_NOTIFIED_MALFORMED` at verdict.py:17 (`set[tuple[str, str]]`); both module-level in-memory sets; no persistence file or DB table anywhere in either module |

---

## D-1 — Failure-Class Census

### Incident History

**2026-08-19 — plan 465 (misplacement only)**
- 3 WARN lines: 16:45:24, 16:45:55, 16:46:25
- File: `verdicts/pending/verdict-465-step-1.md`
- Resolution: 16:46:55 `[465] cleaned 1 pending verdict(s)` → `verdict continue-to-done`
- Duration of WARN flood: ~61 seconds (3 cycles)

**2026-08-20 — diag-486 era (malformed only)**
- Author-attested: malformed first line. No terminal-log evidence exists because the malformed WARN routes through `_log_stderr` (verdict.py:303) to stderr, not the terminal log (V3). This unrecordability IS V3's gap.

**2026-08-21 — plan 495 (misplacement only)**
- 22 WARN lines: 12:42:34 → 12:53:07 (~10.5 minutes)
- File: `verdicts/pending/verdict-495-step-1.md`
- Resolution: eventual move to resolved/ (no explicit consumption log line matched in the excerpt; the plan proceeded after the WARNs stopped)
- Duration of WARN flood: ~10.5 minutes (22 cycles)

**2026-08-25 — plan 521 (DOUBLE FAULT: misplacement + malformed)**

Log-verifiable timeline:
| Time | Event | Source |
|------|-------|--------|
| 09:33:10 | PAUSE: `[diagnostic-teardown-silent-blo]` step 1 — waiting for CEO verdict | terminal log |
| 09:34:43 | First WARN: verdict-521-step-1.md in wrong directory (pending/) | terminal log |
| 09:34:43–09:41:45 | 15 WARN lines at ~30s intervals | terminal log |
| 09:48:47 | `[521] cleaned 1 pending verdict(s)` → `verdict continue-to-done` | terminal log |

Author-attested points (NO log records — V3's gap):
| Time (approx) | Event | Why unrecorded |
|-------|-------|----------------|
| ~09:34 | Operator writes verdict file into `verdicts/pending/` (wrong directory) | No detection at write time; first WARN appears at 09:34:43 on next scan cycle |
| ~09:42 | Operator moves file to `verdicts/resolved/` | Successful move ends the WARN sequence; gap between last WARN 09:41:45 and consumption 09:48:47 contains the move + rewrite |
| ~09:45 | Operator rewrites with `# Verdict` header (malformed first line) | `_log_stderr` WARN at verdict.py:303 — goes to stderr, absent from terminal log. The moment of the malformed rewrite is itself unrecordable via V3's gap |

The memory entry `bellows-verdict-file-id-based` was indexed, three days old, and documented BOTH faults — yet unconsulted at the act. Author-attested quote: "§1a (wrong directory) now measured THREE times (435-era, 495 on 2026-08-21, 521 on 2026-08-25), §1b-class (bad first line — `# Verdict` markdown header) again on 521, BOTH in one verdict act, with this memory in the index the whole time."

### The Five Bare-Handed Decisions

Every verdict act requires the operator to get ALL of these right from memory:

| # | Decision | Correct answer | Failure mode | Measured failure |
|---|----------|---------------|--------------|-----------------|
| 1 | **Directory** | `verdicts/resolved/` | Writing to `verdicts/pending/` (where the request file lives — intuition inverted) | Plans 465, 495, 521 |
| 2 | **Filename key** | The plan's numeric id (e.g., `521`) | Using the full slug with type prefix (e.g., `diagnostic-521`) | Consumption normalizes at bellows.py:2620-2624 so this one is tolerant, but the operator must still know the pattern |
| 3 | **Id-vs-slug derivation** | Must match the `verdict-request-{id}-step-{N}.md` pattern in pending/ | Using a slug that doesn't match the request file's id | Consumption fails silently (`continue` at bellows.py:2658-2659) |
| 4 | **First-line grammar** | Exactly `continue`, `stop`, `verdict: continue`, or `verdict: stop` (case-insensitive) | Any other form: `# Verdict`, `Continue:`, prose, markdown headers | Plans 486-era, 521 |
| 5 | **Reason placement** | Lines 2+ (all content after first line becomes the reason) | Embedding reason on the first line, or wrapping in a markdown structure that pushes the verdict token past line 1 | The 521 `# Verdict` header is this class |

---

## D-2 — Write-Side Contract (Exhaustive)

This section is the `issue_verdict.py` tool's requirements spec.

### File Location and Naming

- **Directory:** `verdicts/resolved/` — verdict.py:284 (`resolved_dir = VERDICTS_DIR / "resolved"`)
- **Filename pattern:** `verdict-{plan_slug}-step-{step_number}.md` — verdict.py:285
- **VERDICTS_DIR:** `Path(__file__).parent.resolve() / "verdicts"` — verdict.py:14

### Filename Normalization (Consumption Side)

bellows.py:2609-2616 parses the filename with `re.match(r"^verdict-(.+)-step-(\d+)\.md$", fname)`. bellows.py:2620-2624 strips `diagnostic-`/`executable-` prefixes from the captured slug:
```
lookup_slug = plan_slug
for prefix in ("diagnostic-", "executable-"):
    if lookup_slug.startswith(prefix):
        lookup_slug = lookup_slug[len(prefix):]
        break
```
The request file at bellows.py:2625 uses `verdict-request-{lookup_slug}-step-{step_number}.md` — so a verdict file named `verdict-diagnostic-521-step-1.md` normalizes to lookup_slug `521` and matches `verdict-request-521-step-1.md`.

### First-Line Grammar

verdict.py:301: `re.match(r"^(?:verdict:\s*)?(continue|stop)$", first_line, re.IGNORECASE)`

Accepted forms (exhaustive):
- `continue` / `Continue` / `CONTINUE`
- `stop` / `Stop` / `STOP`
- `verdict: continue` / `verdict: stop` (case-insensitive on both words)

Rejected forms (returns `{"found": False}`):
- `# Verdict` (or any markdown header)
- `Continue — reason here` (trailing content)
- `verdict:continue` (missing space after colon — actually ACCEPTED by `\s*`)
- Any prose or structured content on line 1

### Reason Extraction

verdict.py:310: `reason = "\n".join(lines[1:]).strip() if len(lines) > 1 else ""`

Lines 2+ are joined and stripped. The tool should place reason starting at line 3 (blank line 2 for readability, matching the established processed-verdict file convention).

### Consumption Lifecycle

1. **Parse:** `verdict.check_verdict(plan_slug, step_number)` — verdict.py:282-314
2. **E4 conditioning re-check:** `_recheck_continue_gates` — bellows.py:2500-2564. For `continue` verdicts, re-checks gate failures from the pending request file. Surviving unoverridden failures → `_recheck_refuse` (bellows.py:2466-2498) which renames to `processed-rejected-{fname}` and sends Pushover. The tool CANNOT and MUST NOT bypass this — it only writes the file; the daemon independently reads the gate_result from the pending request file (bellows.py:2631-2655) and judges.
3. **Gap-1b guard:** bellows.py:2699-2720. Blocks continue when prior step's worktree_teardown failure is uncleared. Routes to `halted-`. Again: the tool writes the file, the daemon independently checks.
4. **Rename to processed:** bellows.py:2797-2798. After successful consumption: `processed_path = resolved_dir / f"processed-{fname}"` → `shutil.move`. The original verdict file name is gone; the processed- prefix marks it consumed.
5. **Pending request cleanup:** bellows.py:2794-2796. `pending_file.unlink()` removes the request file.
6. **Ledger entry:** `verdict.log_to_ledger` records the outcome — verdict.py:316+.

### Why the Tool Cannot Bypass E4/Gap-1b

The E4 conditioning path reads `gate_result_from_request` from the pending request file (bellows.py:2631-2655), not from the verdict file. The verdict file carries only outcome + reason. The daemon's re-check is an independent judgment on data the tool never touches. Writing a correct verdict file is necessary but not sufficient for a continue to take effect — the gates must also pass.

---

## D-3 — Detection-Without-Correction Census

### Site 1: Misplaced Verdict Detector (`_scan_misplaced_verdicts`, bellows.py:2570-2592)

**What it knows at detection time:**
- The file's name (e.g., `verdict-521-step-1.md`)
- Its current path (`verdicts/pending/{fname}`)
- The correct destination (`verdicts/resolved/`)
- The file's full content (it could read it)

**What it does:**
- `_log("WARN", ...)` at :2582 — reaches the terminal log every scan cycle (~30s)
- Pushover notification at :2586-2589, once per `(fname, "misplaced_directory")`, deduped by `_NOTIFIED_MISPLACED` (in-memory set, bellows.py:33)
- Does NOT move the file
- Does NOT read or validate the file's content

**What it COULD do with what it knows:**
- Read the file, parse-validate it with `check_verdict`, and if the parse succeeds, move it to `resolved/`. The detector runs inside the daemon's scan loop — it has full access to both directories and the parse function.

**Channel reach:**
- Terminal log: YES (via `_log`)
- Pushover: once per (fname, reason), but dedup set resets on daemon restart (V8)
- stderr: NO (uses `_log`, not `_log_stderr`)

**Classification:** Print-not-branch — the daemon detects the exact problem, knows the exact fix, has the authority and access to execute it, and instead warns forever. This is the detector pattern running inside the corrector.

### Site 2: Malformed Verdict Detector (`_notify_malformed_verdict`, verdict.py:266-279; WARN at :303)

**What it knows at detection time:**
- The file path
- The non-matching first line (passed as argument)
- That the content does not match the grammar

**What it does:**
- `_log_stderr("WARN", ...)` at :303 — prints to sys.stderr ONLY; does NOT reach the terminal log
- `_notify_malformed_verdict` at :266-279 — Pushover once per `(str(filepath), "malformed_content")`, deduped by `_NOTIFIED_MALFORMED` (in-memory set, verdict.py:17)
- Returns `{"found": False}` — the consumption caller at bellows.py:2658-2659 treats this identically to "file doesn't exist" and silently continues

**What it COULD do with what it knows:**
- Nothing corrective. The malformed content's intended outcome is unknown (was the operator trying to continue or stop?). Auto-correction is impossible.
- Honest fallback: emit the WARN through the terminal log channel (change from `_log_stderr` to a mechanism that reaches `_log`), and use persistent notification (not an in-memory dedup set that resets on restart).

**Channel reach:**
- Terminal log: NO (uses `_log_stderr` which writes to sys.stderr; the terminal log is written by `logging.getLogger("bellows")` via bellows.py's `_log` at :253-257 — completely separate channels)
- Pushover: once per (filepath, type), but dedup set resets on daemon restart (V8)
- stderr: YES

**The asymmetry stated:** The misplaced detector knows the file's correct destination AND has the authority to move it, yet only warns. The malformed detector has no corrective option (intent unknown), yet its warning doesn't even reach the primary monitoring channel. The first is the more expensive bug (it has all information needed to self-correct); the second is the more dangerous gap (the operator doesn't know their file is broken until Pushover — which forgets on restart).

### Auto-Correction Safety Analysis

**Misplaced (well-formed) file — auto-move:**
- **Race 1: Operator mid-edit.** The operator has the file open in `verdicts/pending/` and is still writing. The daemon's scan cycle reads the directory listing, sees the file, and moves it before the write completes. Mitigation: parse-validate with `check_verdict` BEFORE moving. A half-written or mid-edit file will fail the regex (empty, missing first line, or partial content), and the move is suppressed.
- **Race 2: The request file it pairs with.** The pending request file `verdict-request-{id}-step-{N}.md` lives in `pending/`. The auto-move only moves the verdict response file, not the request. The consumption path at bellows.py:2625 looks up the request file by its own glob — no coupling to the response's directory.
- **Race 3: Daemon restart during move.** `shutil.move` on a local filesystem is atomic (rename within the same mount). No partial state.
- **Conclusion:** Auto-move of parse-valid misplaced files is SAFE with the parse-validation precondition.

**Malformed file — auto-correction:**
- IMPOSSIBLE. The detector cannot know whether the operator meant `continue` or `stop`. The only honest response is to make the failure visible through the correct channel (terminal log, not just stderr) and persist the notification (not in-memory dedup).

---

## D-4 — Tool Shape: `tools/issue_verdict.py`

### Proposed Signature

```
issue_verdict.py <plan-id-or-slug> <step> {continue|stop} [--reason-file PATH | --reason TEXT | stdin] [--force]
```

Following the house tool grammar: `deposit_receipt.py`'s argparse shape (positional required args + optional flags), `clear_plan.py`'s gated-act precedent (precondition checks before the write).

### Behavior

1. **Derive the authoritative id.** Glob `verdicts/pending/verdict-request-*-step-<step>.md`. Match the `<plan-id-or-slug>` argument against the request filenames (applying the same `diagnostic-`/`executable-` prefix normalization from bellows.py:2620-2624). Refuse with a listing when zero or multiple requests match.

2. **Validate the outcome word.** Accept only `continue` or `stop` (case-insensitive). Refuse with the enum stated if anything else is provided.

3. **Construct the file content.** First line: exactly the outcome token (lowercased). Blank line 2. Reason from line 3+. Grammar holds BY CONSTRUCTION — no operator memory required.

4. **Write atomically.** Write to a temp file in `verdicts/resolved/` (same filesystem), then `os.rename` to the final path `verdict-{matched_id}-step-{step}.md`. No partial file is ever visible at the final path.

5. **Self-verify.** Re-implement `check_verdict`'s 3-line parse regex in the tool (see Import Surface below) and call it on the file just written. Print the parse outcome. The tool's success claim is the consumer's own parse logic, not the tool's opinion.

6. **Print confirmation.** File path, parsed outcome, reason preview. Exit 0.

### Refusals

| Condition | Behavior |
|-----------|----------|
| No pending request file matches | Print listing of pending requests; exit 1 |
| Multiple pending requests match | Print all matches; exit 1 |
| Outcome word not in `{continue, stop}` | Print accepted values; exit 1 |
| Existing un-consumed verdict at target path (no `--force`) | Print existing file path; exit 1 |
| Existing un-consumed verdict at target path (with `--force`) | Overwrite (atomic rename replaces) |

### Idempotence and the `processed-` Collision Case

If a `processed-verdict-{slug}-step-{N}.md` exists, the prior verdict was already consumed. The tool should WARN (prior verdict was consumed; this is a new verdict for the same step) but proceed — the consumption path handles the `processed-` rename independently, and the `_recheck_refuse` path at bellows.py:2482-2493 has its own collision-avoidance counter suffix.

### Import Surface: Why the Tool Must NOT Import `verdict`

Importing `verdict.py` triggers the following chain:
1. verdict.py:11 — `import notifier` (module-level)
2. notifier.py:13 — `from bellows import _log` (module-level)
3. This loads the ENTIRE `bellows.py` module (~2800 lines) including all its imports: `shutil`, `pathlib`, `subprocess`, `sqlite3` (via `lifecycle`), `requests` (via `notifier`), `threading`, `logging`, and module-level initialization of the daemon's state (`_NOTIFIED_MISPLACED`, `BELLOWS_ROOT`, etc.)

This is HEAVY for a CLI tool that needs only a 3-line regex.

**Alternative:** Re-implement the parse regex in the tool:
```python
_VERDICT_RE = re.compile(r"^(?:verdict:\s*)?(continue|stop)$", re.IGNORECASE)
```
Plus a test asserting the regex pattern string stays byte-identical to verdict.py:301's regex. The clone-drift cost is one test — and if the regex ever changes in verdict.py, the test fails and forces the tool to sync.

**Estimated LOC:** ~90-110 for the tool; ~70-80 for tests.

### Test List

1. Happy path: file lands in `resolved/`, self-verify parse succeeds, first line is exact outcome token
2. Id derivation from request file, including `diagnostic-`/`executable-` prefix normalization
3. Zero-match refusal: no pending request file for the given plan/step
4. Multi-match refusal: ambiguous request files
5. Enum refusal: outcome word not `continue`/`stop`
6. No-request refusal: step has no pending request
7. Overwrite guard: existing un-consumed verdict file without `--force` → exit 1
8. Overwrite with `--force`: replaces existing file
9. Atomicity: no partial file visible at the final path (concurrent reader sees either nothing or the complete file)
10. Self-verification output matches consumer's parse (assert same dict shape as `check_verdict` would return)
11. Regex byte-identity: tool's `_VERDICT_RE` pattern string == verdict.py's pattern string
12. Reason from `--reason`, `--reason-file`, and stdin
13. `processed-` collision: warn but proceed when prior consumed verdict exists

---

## D-5 — Daemon-Side Posture

### (i) Auto-Move of Well-Formed Misplaced Files

**Proposed behavior:** In `_scan_misplaced_verdicts` (bellows.py:2570-2592), after detecting a misplaced file:
1. Read and parse-validate with the verdict regex
2. If parse succeeds: `shutil.move` from `pending/` to `resolved/`; log `EVENT` (not WARN): "auto-moved well-formed verdict to resolved/"
3. If parse fails: continue with existing WARN behavior (the file is misplaced AND malformed — operator needs to fix content first)

**Race windows (from D-3):**
- Operator mid-edit → parse-validation catches: half-written file fails the regex
- Request file coupling → none: consumption reads request by its own glob
- Daemon restart during move → atomic rename

**Cost:** ~10 lines added to `_scan_misplaced_verdicts` (read, parse, conditional move)

**Benefit:** Eliminates the 30s WARN flood (3 lines on 2026-08-19, 22 lines on 2026-08-21, 15 lines on 2026-08-25 — 40 WARN lines across three incidents that the daemon could have resolved in milliseconds)

**Residual:** After tool mechanization, misplaced files should become rare (the tool writes directly to `resolved/`). Auto-move becomes dead-letter handling — still worth having for defense-in-depth.

### (ii) Malformed WARN Channel Promotion

**The gap:** verdict.py:303 uses `_log_stderr("WARN", ...)` which goes to sys.stderr. The terminal log (written by `logging.getLogger("bellows")` via bellows.py:253-257) never sees it. The operator's primary monitoring channel is blind to malformed verdicts. Measured: `grep -cF "verdict file malformed" logs/terminal/*.log` → 0 across all 14 log files.

**Proposed fix:** In bellows.py's `_consume_verdicts`, after `verdict.check_verdict` returns `{"found": False}`, check if the file actually exists at the expected path. If it does exist but parse returned not-found, the file is malformed. Log via `_log("WARN", ...)` which reaches the terminal log.

**Exact site:** bellows.py:2657-2659. After `verdict_result = verdict.check_verdict(plan_slug, step_number)` and before `if not verdict_result.get("found"): continue`:
```python
if not verdict_result.get("found"):
    expected_path = resolved_dir / fname
    if expected_path.exists():
        _log("WARN", f"verdict file exists but unparseable: {fname}", slug=plan_slug)
    continue
```

**Cost:** 3 lines. No verdict.py changes required — the daemon adds its own terminal-log WARN at the consumption site.

**Benefit:** Malformed verdicts become visible in the terminal log. The operator sees the problem without relying on Pushover (which dedup-forgets on restart, V8).

### (iii) Dedup Persistence (`_NOTIFIED_*` Sets)

**Current state:** Both `_NOTIFIED_MISPLACED` (bellows.py:33) and `_NOTIFIED_MALFORMED` (verdict.py:17) are in-memory sets. "Notified once" claims reset at every daemon restart.

**Options:**
- **A: Persist to a JSON file.** Write the set to `.bellows-cache/notified-*.json` on each add; load at startup. Cost: ~15 lines per set. Benefit: notifications survive restarts.
- **B: Leave as-is; tool mechanization makes it moot.** If the tool prevents all malformed/misplaced writes, these notification paths become dead-letter handling. A restart re-notifying on a genuinely stuck file is arguably CORRECT behavior (it's still stuck).
- **C: Replace with a TTL.** Instead of "notify once ever (until restart)", notify at most once per hour. Requires a dict with timestamps instead of a set.

**Cost/benefit trade-off:** After tool mechanization + auto-move (fork i), the only files reaching these detectors are edge cases. Option B is defensible: the restart-reset behavior becomes a feature (re-alerting on genuinely stuck files), not a bug.

### (iv) Memory Entry Retirement Path

Once the tool ships, the memory entry `bellows-verdict-file-id-based` splits:

| Content | Destination | R2 discriminator |
|---------|-------------|-----------------|
| Directory rule (`resolved/` not `pending/`) | Tool's `--help` text + refusal message on wrong-path detection | TRAP→CODE |
| Filename pattern and id derivation | Tool's id-matching logic + refusal messages | TRAP→CODE |
| First-line grammar | Tool constructs by-construction; regex in tool + byte-identity test | TRAP→CODE |
| Reason placement | Tool places automatically | TRAP→CODE |
| The fact that a tool now exists | `knowledge/glossary.md` RUNBOOK entry: "verdict act → `tools/issue_verdict.py`" | R2 RUNBOOK line |
| Incident history | This diagnostic document (D-1) | Archived in research/ |
| Nothing | The memory entry itself: retire after tool ships | No residual |

---

## D-6 — Test Surface

### Regression Floor

Current suite: **1363 tests** (measured 2026-08-25 via `python3 -m pytest --collect-only -q` from the bellows root).

### Tool Tests (issue_verdict.py)

| # | Test | Type |
|---|------|------|
| 1 | Happy path: file lands in resolved/, self-verify parse succeeds, first line is exact outcome token | Unit |
| 2 | Id derivation from request file with `diagnostic-`/`executable-` prefix normalization | Unit |
| 3 | Zero-match refusal: no pending request → exit 1 with listing | Unit |
| 4 | Multi-match refusal: ambiguous requests → exit 1 with listing | Unit |
| 5 | Enum refusal: invalid outcome word → exit 1 | Unit |
| 6 | Overwrite guard: existing un-consumed verdict without --force → exit 1 | Unit |
| 7 | Overwrite with --force: succeeds | Unit |
| 8 | Atomicity: no partial file visible at final path | Unit |
| 9 | Self-verification output matches consumer's parse | Integration |
| 10 | Regex byte-identity: tool's pattern string == verdict.py:301 pattern string | Regression |
| 11 | Reason from --reason, --reason-file, stdin | Unit |
| 12 | processed- collision: warn but proceed | Unit |

### Daemon-Side Tests (if D-7 forks approve)

| # | Test | Gate |
|---|------|------|
| 13 | Auto-move: parse-valid misplaced file moved to resolved/; EVENT logged | Fork 1 |
| 14 | Auto-move: parse-invalid misplaced file NOT moved; WARN persists | Fork 1 |
| 15 | Malformed WARN reaches terminal log (caplog assertion) | Fork 2 |

---

## D-7 — Open Questions (CEO Forks)

### Fork 1: Daemon auto-move of parse-valid misplaced verdicts

- **Yes:** Eliminates the 30s WARN flood (40 measured lines across 3 incidents). Parse-validation precondition makes it safe (D-3 race analysis). ~10 lines. After tool mechanization, becomes defense-in-depth for edge cases.
- **No:** Keeps the current behavior. The operator must manually move files. With the tool, misplacement becomes rare — the WARN flood is a problem for the bare-handed era, which the tool retires.

### Fork 2: Malformed WARN channel promotion

- **Recommended: YES.** The current gap (V3) means the primary monitoring channel is blind to malformed verdicts. 3 lines in bellows.py at the consumption site. Trivial cost, material safety improvement. Even with tool mechanization, defense-in-depth: if someone hand-writes a verdict, the daemon should visibly complain.

### Fork 3: Parser tolerance widening

- **Doctrine default: NO.** Strict substrate + sanctioned tool (the E2 precedent). If the tool enforces grammar by construction, widening the parser weakens defense-in-depth. A `# Verdict`-headed file whose next non-header line matches is a violation of the contract, not a creative spelling. The tool makes tolerance unnecessary — the strict parser becomes a guard against non-tool writes rather than a usability obstacle.
- **Yes:** Accept files where the first non-empty, non-header line matches the regex. Cost: ~5 lines in `check_verdict`. Risk: weakens the contract; permits a wider surface of "almost right" that the tool was designed to eliminate.

### Fork 4: Wrap ritual / PLANNER_TEMPLATE mandate

- **The caveat:** The fixing-the-instruction-is-not-the-practice lesson is exactly what this diagnostic is about. The memory entry documented both faults and didn't prevent them. A template line saying "use the tool" has the same enforcement class as a memory entry saying "use resolved/" — documentation, not a guard.
- **The tool's existence plus the parser's strictness IS the enforcement.** The tool writes to the correct directory with the correct grammar; the parser rejects everything else. No instruction needed.
- **The one case for a template line:** It tells the Planner (which authors the wrap ritual) that the tool exists, so it can include it in its verdict-issuance instructions to the CEO. This is information routing, not enforcement. Cost: 1 line. Benefit: the Planner stops authoring bare-handed verdict instructions.

### Additional (surfaced by census)

**Fork 5: Whether `_consume_verdicts` should log the malformed file's first line in its daemon-side WARN.** Fork 2 adds a WARN, but omits the diagnostic content (what the first line actually was). Including it (e.g., `"verdict file exists but unparseable: {fname} — first line: {first_line!r}"`) requires reading the file at the bellows.py site. Cost: 2 additional lines. Benefit: the terminal log shows exactly what was wrong, matching the stderr WARN's content at verdict.py:303.

---

## Rule 27 — Gap Table

| # | Site | File:Line | Change type | Description |
|---|------|-----------|-------------|-------------|
| G1 | New file | tools/issue_verdict.py | CREATE | The verdict tool: argparse CLI, id derivation from request glob, atomic write, self-verify with re-implemented regex |
| G2 | New file | tests/test_issue_verdict.py | CREATE | Tool tests: 12 cases (D-6 items 1-12) |
| G3 | Misplaced detector | bellows.py:2570-2592 | MODIFY | Auto-move of parse-valid misplaced files (if Fork 1 = yes) |
| G4 | Consumption site | bellows.py:2657-2659 | MODIFY | Malformed WARN to terminal log (if Fork 2 = yes; 3 lines) |
| G5 | Misplaced detector test | tests/test_*.py (new) | CREATE | Auto-move test: parse-valid moved, parse-invalid not moved (if Fork 1 = yes) |
| G6 | Malformed WARN test | tests/test_*.py (new) | CREATE | caplog assertion: malformed WARN reaches terminal log (if Fork 2 = yes) |
| G7 | Glossary | knowledge/glossary.md | MODIFY | RUNBOOK entry: verdict act → tools/issue_verdict.py |
| G8 | Memory | ~/.claude memory entry | DELETE | Retire `bellows-verdict-file-id-based` after tool ships |
