# Cycle Log Format Census + Rule 27 Gap Assessment for `cycle_check.py`

**Date:** 2026-08-19 | **Plan:** diagnostic-460 | **Step:** 1 (DIAG) | **Read-only**

---

## Q1 — Census of Every Cycle Log Block Format

### Population count

**Method 1:** `grep -rl '## Drafting Cycle' knowledge/decisions/Done/*.md | wc -l` → **37**
**Method 2:** Cross-check with `cycle_yields.py` — run `python3 scripts/cycle_yields.py` (stderr reports `Discovery: N files, M with Drafting Cycle block`). The script uses `extract_dc_blocks()` which matches `^## Drafting Cycle\s*$` after stripping fenced code blocks.

**Result: 37 files confirmed** — matches the Planner's walk-0 measurement.

### Form (a) — Newer class-split per-lens lines

Pattern: `- <Lens>: wN M folded — instruction I / record R (prose)`

**Exact command:** `grep -rn '— instruction [0-9]' knowledge/decisions/Done/*.md` restricted to lines starting `- ` (per-lens position).

**Files carrying class-split per-lens lines: 3** (not 5 — the Planner's "5" counted files carrying `instruction` in ANY position, including Closing/Split/STATUS lines; the per-lens form appears in only 3).

| File | Per-lens specimen (file:line) |
|---|---|
| `diagnostic-429.md` | `:71` `- Weak spots: w1 1 folded — instruction 1 / record 0 (1.4: ...)` — all 5 lenses carry it at w1 |
| `executable-430.md` | `:113` `- Weak spots: w1 2 folded — instruction 2 / record 0 (1.3 ...)` — all 5 lenses carry it at w1 |
| `executable-392.md` | `:167` `- Weak spots: w1 1 folded — instruction 1 / record 0 (...)` — only Weak spots carries it (single-walk per-lens split) |

**Dash variance:** em-dash `—` (U+2014) in all 3 files on per-lens lines. No hyphen-minus `-` variant found in per-lens class-split position.

**Lens-name variance on per-lens lines:** `Integration` (diagnostic-429:74) and `Integration-record` (executable-430 does not use it; diagnostic-429 uses `Integration`). Both resolve to the same lens. `cycle_yields.py` already handles both via `LENS_PREFIXES` (lines 39-40).

### Form (a′) — Class-split in Walk-N split and Closing lines (not per-lens)

Several additional files carry instruction/record counts in aggregate positions:

| Position | Files | Specimen |
|---|---|---|
| `**Walk-N split:**` | executable-366 (`:55`), executable-367 (`:58`, `:67`, `:76`) | `**Walk-1 split: instruction 0 / record 0 — DRY at walk 1.**` |
| `**Splits:**` (compact) | executable-418 (`:172`) | `**Splits: w1 instruction 0 / record 0 — DRY … · w2 dry.**` |
| `**Closing:**` with split | diagnostic-370 (`:75`), diagnostic-429 (`:80`), executable-366 (`:59`), executable-367 (`:80`), executable-371 (`:147`), executable-376 (`:129`), executable-379 (`:134`), executable-392 (`:177`), executable-418 (`:176`), executable-430 (`:123`) | `**Closing:** walk 2 DRY — **instruction 0 / record 0**; ...` |

**Files with class-split in ANY position (per-lens, Walk-split, Splits, or Closing): 10 total** — diagnostic-370, diagnostic-429, executable-366, executable-367, executable-371, executable-376, executable-379, executable-392, executable-418, executable-430.

**Files with class-split in NONE of those positions: 27** (the remaining 37 − 10).

### Form (b) — Older form without class split

Pattern: `- <Lens>: wN M folded (prose)` or `- <Lens>: wN M; wN M; ...`

Specimens:

| File:Line | Form |
|---|---|
| `executable-271.md` (early era) | `- Weak spots: w1 1 folded (the closing-line "dry vs fold" parse ...); w2 dry.` |
| `executable-286.md` (mid era) | `- Weak spots: w1 5 folded; w2 4; w3 3; w4 2.` — bare count, no class split, no origin |
| `executable-338.md` (mid era) | `- Weak spots: w1 4 — 4 pre / 0 fold; w2 3 — 2/1; w3 3 — 0/3; w4 2 — 0 pre / 2 fold.` — has origin split (pre/fold) but NOT instruction/record class split |
| `diagnostic-455.md` (recent) | `- Weak spots (1.4): w1 1 folded; w2 1 folded (F6); w3 dry; w4 dry; w5 dry.` — sub-question number in parens after lens name, no class split |
| `executable-457.md` (most recent in Done/) | `- Weak spots: w1 2 folded (1.1, 1.3); w2 1 folded (1.1 F7); w3 1 folded (F9 ...) — w3 instruction 0 / record 1.` — class split appears ONLY as trailing annotation on the final walk, not in the `w1 M folded — instruction I / record R` form |

**Dash variance in older form:** em-dash `—` (U+2014) used consistently for separating the origin split from fold count. No hyphen-minus variant found.

**Lens-name variance:**
- `Integration-record` (most files) vs `Integration` (a few early files, e.g. diagnostic-429:74)
- `Weak spots` (consistent, two words)
- Lens sub-question numbers in parens: `Weak spots (1.4):` — present in diagnostic-455, diagnostic-429, executable-392; absent in most older files
- `ACID` sometimes carries sub-question: `ACID (5.2):` or `ACID (5.5):`

**Pass-token variance:**
- `w1`, `w2`, ... `w7` — walk passes (most common)
- `c1`, `c2`, `c3` — confirming passes (executable-322, executable-324, executable-317)
- `a1`, `aC`, `aC2` — ACID-apart passes (executable-324, executable-317)
- `cc` — panel-complete confirming close (executable-324:181, executable-317:164)
- `Closing` — as a pass token in some older files
- `cold` — prefixed lens lines in T2 plans (e.g. `- cold Weak spots:`) — NOT found in Done/ corpus per-lens lines (cold-panel findings are narrated differently)
- Multi-pass per line: `w1 2 folded; w2 dry; w3 dry.` — produces multiple rows in `cycle_yields.py`

### Form (c) — STATUS aggregate lines

Pattern: `**STATUS: CYCLE COMPLETE — ...**`

**Only 2 files in Done/ carry this form:**

| File:Line | Specimen |
|---|---|
| `diagnostic-429.md:68` | `**STATUS: CYCLE COMPLETE — walk 2 dry, §2 bar met.** Walk 1 folded 7 instruction-class findings across all five lenses ...` |
| `executable-430.md:110` | `**STATUS: CYCLE COMPLETE — T2 walk + full cold panel + capstone + convergence walk all run; §2 bar met.** Walk 1: 8 instruction folds. ...` |

**Per-walk STATUS lines** (a newer variant seen in the LIVE plan diagnostic-460 but NOT in any Done/ file):
```
**Walk 1 STATUS:** 8 folded — instruction 7 / record 1 — NOT dry.
```
This form does NOT exist in the Done/ corpus. It exists only in plans currently being authored (post-executable-457 era).

**Implication for assert #1:** The STATUS cross-check (aggregate = sum of per-lens) can only run on 2/37 files in the Done/ corpus. On the remaining 35, it is N/A — neither the aggregate STATUS line nor per-walk STATUS lines exist.

### Partial (live) block form

**Where a live draft carries its DC block:** in the plan file itself at `knowledge/decisions/<plan-name>.md` (the deposit path), or in `knowledge/decisions/drafts/<plan-name>.md` during active authoring.

**What is present mid-cycle (e.g. walk 1):**
- `**Tier:**` — present from walk 0
- `**Walk 0 (context pin):**` — present from walk 0
- Per-lens lines with walk 1 data — present after walk 1
- `**Conflicts:**` — present if any declared

**What is ABSENT mid-cycle (exists ONLY in a completed block):**
- `**Closing:**` line — written at cycle close, absent during walks
- `**STATUS: CYCLE COMPLETE**` aggregate line — written at close or absent entirely
- `**§5 Conformance:**` — written at shape-stability, may be absent early
- `**Walk N STATUS:**` per-walk lines — may or may not be present (newer convention)
- `**Origin split:**` — may be absent

**Per-lens lines are byte-identical** between the live draft and the Done/ form — the Planner commits per-phase (`[draft]` commits visible in git log), and the per-lens lines are not rewritten at deposit. The Done/ census transfers to the live form for per-lens parsing.

**cycle_check must NOT treat the absence of Closing/STATUS lines as a defect mid-cycle** — those lines legitimately do not exist until the cycle closes.

---

## Q2 — Assert-to-Input-Provider Map

### Confirmation: `cycle_yields.py` does NOT parse the instruction/record axis

**Confirmed.** `cycle_yields.py` parses:
- Lens name (`LENS_PREFIXES`, lines 36-42)
- Pass token and fold count (`PASS_FOLDED_RE` / `PASS_DRY_RE`, lines 44-49)
- Origin axis: pre-existing / fold-introduced (`ORIGIN_FULL_RE` / `ORIGIN_PRE_RE` / `ORIGIN_FOLD_RE`, lines 51-53)

It has NO regex for `instruction N / record M`. The origin axis (pre-existing vs fold-introduced) is a DIFFERENT axis from the class axis (instruction vs record). The Planner's finding is confirmed.

### New regex needed for class-split parsing

The per-lens class-split form is: `— instruction (\d+) / record (\d+)` (after the fold count).

The per-walk STATUS form is: `(\d+) folded — instruction (\d+) / record (\d+)` (on a standalone line).

The Walk-N split form is: `instruction (\d+) / record (\d+)` (on a `**Walk-N split:**` line).

The Closing form is: `instruction (\d+) / record (\d+)` (embedded in `**Closing:**`).

A single regex `instruction\s+(\d+)\s*/\s*record\s+(\d+)` would capture all four positions. Context determines which line type it's on.

### Assert-to-input table

| Assert | Data needed | Provided by | Gap |
|---|---|---|---|
| **#1 — Internal arithmetic** (per-lens instruction + record = stated total; STATUS aggregate = sum of per-lens) | (a) Per-lens class-split counts per walk; (b) Per-walk STATUS aggregate counts; (c) Aggregate STATUS line class counts | (a) **GAP** — no parser exists; `cycle_yields.py` parses fold count and origin axis but NOT instruction/record class split. (b) **GAP** — per-walk STATUS lines are unparsed. (c) **GAP** — aggregate STATUS parsing does not exist. | New regex for `instruction N / record N` in `cycle_check.py`. N/A rule required when the split is absent (27/37 files in Done/). |
| **#2 — Evidence exists** (every walk has a walk-register section AND a per-phase commit) | (a) Walk-register rows per walk; (b) Git commits per walk/phase | (a) `walk_register_lint.py` validates register table STRUCTURE (columns, fields, truncation) but does NOT assert a register-row-per-walk — it is a shape validator, not a completeness checker. (b) **GAP** — nothing asserts per-phase commits exist. | `cycle_check` must query git log for `[draft]`-tagged or `deposit(`-tagged commits per walk, and check for walk-register section presence. |
| **#3 — Fold actually happened** (fold_check baseline advanced for that walk) | `fold_check.py`'s baseline JSON file advanced (new signals or exit code change) | `fold_check.py` stores baselines at `<dir>/.<filename>.foldcheck.json`. Its `--save-baseline` mode saves the state, and the default mode diffs against it. Baseline movement = the JSON file was updated between walks. | `cycle_check` must verify baseline file existence and that its modification timestamp or content advanced for each walk that claims folds. Alternatively, `fold_check.py` could be invoked/re-run per walk. The baseline mechanism is sound but invocation is NOT mechanized — §2.7 mandates running it after each fold, but "neither walk 5 nor walk 6 ran it" (proposal §3). |

---

## Q3 — Class-Split N/A Boundary and Degenerate Inputs

### When assert #1 runs vs returns N/A

**Discriminator recommendation: presence-based, not date-based or id-range-based.**

A date-based discriminator (e.g. "plans after 2026-08-12 should carry the split") would require maintaining a cutover date and would be wrong about plans authored in the transition period. An id-range discriminator has the same problem plus non-monotonic id assignment.

**The correct discriminator is textual presence:**
- If the per-lens line carries `instruction N / record M` → run the arithmetic check.
- If the per-lens line does NOT carry it → assert #1 returns **N/A** for that lens line. No WARN, no FAIL.
- If the block carries a `**Walk-N STATUS:**` or `**STATUS:**` aggregate with class counts → run the cross-check (sum of per-lens = aggregate).
- If no aggregate STATUS exists → the cross-check is N/A.

This approach:
- Returns N/A silently on the 27/37 legacy files (correct — they never had the split)
- Checks the 10/37 files that carry it in any position
- Automatically adapts as the format evolves (new plans add the split → checked)
- No WARN on legacy absence (the split was not expected pre-diagnostic-429 era)

### STATUS aggregate class-count cross-check

Only 2/37 Done/ files carry the aggregate STATUS line. The per-walk STATUS line form exists in 0/37 Done/ files (only in live plans post-executable-457).

**Assert #1's cross-check (STATUS = sum of per-lens) can run on at most 2 files in the current corpus.** For the rest, it is N/A. This is acceptable — the cross-check adds value as the format stabilizes, and its N/A does not block BAR_MET.

### Degenerate inputs and their correct verdicts

| Degenerate input | Correct verdict | Rationale |
|---|---|---|
| **Zero-walk block** (walk 0 only, no per-lens lines yet) | `CONTINUE` | Walk 0 is context-pin only; no walks have run, so no asserts can fire. All three asserts return N/A, which does not block CONTINUE. The plateau counter has no history → no escalation. |
| **Partial block mid-walk** (walk 1 in progress, per-lens lines incomplete) | `CONTINUE` | The partial state is normal during authoring. Asserts that can run (e.g. on completed lens lines) do; incomplete data returns N/A. cycle_check is invoked AFTER a walk is committed (precondition), so mid-walk partial is the uncommitted case → `ESCALATE:uncommitted-walk` if assert #2/#3 are invoked. |
| **Multiple `## Drafting Cycle` headings** (`MULTIPLE_BLOCKS` in cycle_yields) | `ESCALATE:unparseable` | cycle_check cannot determine which block is authoritative. Never BAR_MET. Mirrors `cycle_yields.py`'s `MULTIPLE_BLOCKS` status. |
| **Entirely unparseable lens lines** | `ESCALATE:unparseable` | If no per-lens line can be parsed, cycle_check cannot validate anything. Fail closed — never BAR_MET on unrecognized input. |
| **Block with only dry walks** (e.g. executable-366: walk 1 dry) | `BAR_MET` (if all asserts PASS/N/A + walk is dry + plateau not triggered) | A dry walk 1 with all asserts clean is a legitimate bar-met. |
| **Mixed parseable/unparseable lens lines** | Depends: parseable lines are checked; unparseable lines are reported. If ANY assert FAILs → `ESCALATE`. If all parseable asserts PASS/N/A → `CONTINUE` (not BAR_MET, because unparseable lines prevent full confidence). | Fail closed on the unparseable portion. |

---

## Q4 — The `plan_lint` Check (f) Defect

### Location and mechanism

**File:** `scripts/plan_lint.py`, lines 365-388.

**Quoted code (the critical section):**
```python
lens_line_re = re.compile(
    r'^-\s*(?:cold[\s-]+)?(?:weak[\s-]*spots|destruction|vulnerabilit\w*|integration|acid)\b',
    re.IGNORECASE,
)
closing_pos = re.search(r'^\*\*Closing:\*\*', dc_block, re.MULTILINE)
search_region = dc_block[:closing_pos.start()] if closing_pos else dc_block
last_lens_line = None
for line in search_region.splitlines():
    if lens_line_re.match(line):
        last_lens_line = line

if last_lens_line is not None:
    ll_lower = last_lens_line.lower()
    has_fold = 'fold' in ll_lower
    cleaned = re.sub(r'\b(?:not|no|never)\s+(?:\w+\s+)?dry\b', '', ll_lower)
    has_dry = bool(re.search(r'\bdry\b', cleaned))
    if has_fold and not has_dry:
        print("WARN: Drafting Cycle closing indicates fold as last event, ...")
```

### The defect confirmed

Check (f) iterates all lens result lines before `**Closing:**` and keeps the **last** one. It then checks whether that single line contains "fold" without "dry".

**The false-clean mechanism:** As a cycle converges, the per-lens listing order is fixed (Weak spots → Destruction → Vulnerabilities → Integration-record → ACID). The lenses that go dry first are typically ACID and Integration-record (low-surface lenses). Weak spots and Destruction tend to fold longest. The LAST lens line in source order is ACID (or Integration-record, depending on the plan). When ACID is dry but Weak spots is still folding, check (f) reads ACID's dry line as "last" and reports clean — a false negative.

**Measured from the proposal (§3):** "a walk with three instruction-class findings produced a clean signal."

### How `cycle_check` supersedes it

`cycle_check` reads the AGGREGATE class split (instruction count + record count summed across ALL lenses for the walk), not the last lens line. It checks whether instruction-class count = 0 for the final walk, which is the actual §2 bar. This is structurally immune to the lens-ordering false-clean.

### Recommendation

**Supersede, then retire behind evidence.** Check (f) should remain in `plan_lint.py` as a redundant weaker check UNTIL `cycle_check.py` is demonstrably running and catching the cases check (f) misses. Only then should a separate diff review retire check (f). A premature removal drops coverage between the two.

**This diagnostic does NOT authorize removing check (f).** Removal is a subtractive change that earns its own diff review downstream.

---

## Q5 — Gap Assessment (Rule 27)

| Gap | Current State | Proposed State | Change Required |
|---|---|---|---|
| **(a) Class-split regex** | `cycle_yields.py` parses fold count + origin axis. No parser exists for `instruction N / record M`. | `cycle_check.py` carries a new regex: `instruction\s+(\d+)\s*/\s*record\s+(\d+)` applied to per-lens lines, Walk-N split lines, and Closing lines. | New regex in `cycle_check.py`. Reuse `cycle_yields.py`'s block extraction (`extract_dc_blocks`) and lens-line parsing (`LENS_PREFIXES`, `parse_lens_line`) for block/lens identification; add class-split extraction as a post-parse step on the lens-line content. |
| **(b) Per-phase-commit-per-walk assertion** | Nothing asserts per-phase commits exist. `walk_register_lint.py` validates register table structure, not walk coverage. | `cycle_check` queries `git log --oneline --grep='[draft]'` (or the plan's `[<id>]` tag) for commits matching each walk claimed in the Cycle Log. | New git-log query in `cycle_check.py`. Must handle: `[draft]` tags, `deposit(` tags, `close(` tags. Match walk numbers from commit messages against walks claimed in the DC block. |
| **(c) fold_check per-walk invocation** | `fold_check.py` exists and works (baseline save/diff mechanism). §2.7 mandates running it after each fold. Invocation is NOT mechanized — manual compliance only, measured failures (proposal §3: walks 5+6 skipped it). | `cycle_check` verifies that `fold_check`'s baseline file exists AND was updated for each walk that claims folds. Two approaches: (1) check `.foldcheck.json` mtime/content changed per walk (requires per-walk timestamps); (2) re-run `fold_check --save-baseline` and compare. | `cycle_check.py` checks for baseline file existence at `<plan_dir>/.<plan_name>.foldcheck.json`. For walks claiming folds, verify baseline was saved (file exists and is newer than the walk's commit timestamp). Alternative: re-run fold_check at deposit time (proposal §5's approach). |
| **(d) Check (f) supersession** | `plan_lint.py` check (f) reads the LAST lens line and checks for fold/dry. False-clean rate rises as lenses converge at different rates. | `cycle_check` reads the aggregate instruction-class count (summed across all lenses per walk), immune to lens-ordering bias. Check (f) remains as a redundant weaker guard until `cycle_check` is proven live. | No change to `plan_lint.py` in the `cycle_check` build. Retirement of check (f) is a separate downstream decision, gated on `cycle_check` being demonstrably catching what (f) misses. |
| **(e) N/A/WARN discriminator** | No discriminator exists — `cycle_yields.py` emits `ORIGIN_ABSENT` for missing origin splits, but the instruction/record class axis has no absence handling. | Presence-based discriminator: if the per-lens line carries `instruction N / record M`, run the arithmetic check; if absent, return N/A silently. No date/id-range discriminator. N/A does not block BAR_MET. | Implement in `cycle_check.py`'s per-lens parser: after extracting fold count, attempt class-split regex; if no match, mark assert #1 as N/A for that line. |
| **(f) Decision function (assert aggregation → verdict)** | No decision function exists. The CEO says "walk N" or "continue" manually. | `cycle_check` emits exactly one of CONTINUE / BAR_MET / ESCALATE:\<reason\>. Decision function: (1) any assert FAIL → ESCALATE:\<assert\>; (2) unparseable/multiple-block → ESCALATE:unparseable; (3) plateau (3 consecutive flat instruction-count walks, no new finding class) → ESCALATE:plateau; (4) yield rising → ESCALATE:yield-rising; (5) restructuring fold present → ESCALATE:restructuring-fold; (6) a dry walk with all asserts PASS/N/A, no restructuring fold, no plateau → BAR_MET; (7) otherwise → CONTINUE. N/A asserts participate neutrally (do not block BAR_MET, do not trigger ESCALATE). | Implement in `cycle_check.py`. The plateau counter is derived stateless from the Cycle Log's walk history (see Q6). |
| **(g) Fail-closed on unparseable/multiple-block** | `cycle_yields.py` emits `UNPARSEABLE` / `MULTIPLE_BLOCKS` status but takes no action. | `cycle_check` emits `ESCALATE:unparseable` on any input it cannot parse. Never BAR_MET on an unrecognized representation. A silent-clean on unrecognized input is the exact failure this validator exists to prevent. | Implement as the first check in `cycle_check.py`: if `extract_dc_blocks` returns 0 or >1 blocks, or if no lens lines can be parsed, emit ESCALATE:unparseable and exit. |
| **(h) Partial live-block form** | No validator handles the partial form (Closing/STATUS absent mid-cycle). | `cycle_check` treats absent Closing/STATUS as normal mid-cycle. Per-lens lines are parsed identically to Done/ form. Asserts run on whatever data is present; missing data → N/A, never FAIL. | Implement: do not require Closing or STATUS lines. Check what exists. If walk N's per-lens lines are present, check them. If Closing is present (cycle claims to be closed), verify the BAR_MET claim. |
| **(i) Degenerate-input verdicts** | No validator exists. | Zero-walk → CONTINUE (all asserts N/A). Multiple-DC-block → ESCALATE:unparseable. All-unparseable lens lines → ESCALATE:unparseable. Mixed parseable/unparseable → CONTINUE (fail closed on unparseable portion, cannot BAR_MET). Uncommitted walk → ESCALATE:uncommitted-walk. | Implement each case as specified in Q3's degenerate table. Test with fixtures for each case. |

---

## Q6 — `cycle_check.py` Output Contract (DESIGN ONLY)

### Three-verdict contract

`cycle_check.py` emits exactly one verdict to stdout, then exits:

| Verdict | Exit code | Meaning |
|---|---|---|
| `CONTINUE` | 0 | The cycle is making progress; next walk is owed. |
| `BAR_MET` | 0 | The §2 doneness bar is met; the cycle may close. |
| `ESCALATE:<reason>` | 1 | The cycle is blocked; the caller must pause until a one-word answer resumes it. |

### ESCALATE reason vocabulary (closed, resumable set)

| Reason | Trigger |
|---|---|
| `direction-class` | A forcing finding that invalidates the plan's premise (§2.0). |
| `new-ceo-decision` | A new CEO decision discovered mid-cycle. |
| `yield-rising` | The current walk's instruction-class yield is higher than the prior walk's. |
| `restructuring-fold` | A restructuring fold is present in the current walk (§2's clause resets the clock). |
| `plateau` | 3 consecutive walks at a flat instruction-class count with no new finding class. |
| `unparseable` | The input cannot be parsed (multiple DC blocks, unrecognized lens lines, etc.). |
| `uncommitted-walk` | Assert #2/#3 invoked on an uncommitted draft (git evidence absent). |
| `assert-fail:<N>` | Assert N (1, 2, or 3) failed its check. |

**Cost/token escalation: DROPPED** per CEO routing (Q3 answered NO).
**Battery-failure escalation: DROPPED** — battery re-runs are the depositor's concern (proposal §5), not cycle_check's.

### Stateless plateau detection

cycle_check is stateless — it derives the plateau counter from the Cycle Log's walk history on each run:

1. Parse all per-walk instruction-class counts from the DC block (from per-lens class-split sums or Walk-N STATUS lines).
2. Working backwards from the current walk, count consecutive walks where:
   - The instruction-class count is identical to the current walk's, AND
   - No new finding class appeared (no lens that was previously dry produced a fold).
3. If that consecutive count ≥ 3 → `ESCALATE:plateau`.

**When the class-split is absent (N/A):** The plateau counter cannot be computed from class counts. Fall back to total fold count for the plateau check, or return N/A for the plateau sub-check (which means plateau escalation is disabled on legacy-format blocks — acceptable, as those blocks are already closed in Done/).

### Invocation context

**Who runs it:**
1. **The Planner** runs `cycle_check` after each walk in-session (replacing the CEO's manual "walk N" gate). The Planner reads the verdict and either continues (CONTINUE), closes (BAR_MET), or surfaces the reason to the CEO (ESCALATE).
2. **The in-bellows depositor** RE-RUNS `cycle_check` at deposit time (proposal §5) rather than trusting the written verdict. The written validation block is an audit trail; the re-run is the validation.

**The contract must serve both callers.** Both read the same stdout verdict and exit code.

### Git precondition

Asserts #2 and #3 read git state:
- Assert #2 checks for per-phase commits (requires the walk to be committed).
- Assert #3 checks fold_check's baseline (requires the walk's fold to be committed so the baseline reflects the post-fold state).

**Precondition:** cycle_check MUST run AFTER the walk is committed. If run on an uncommitted draft:
- Assert #2 will find no commit for the current walk → would false-FAIL.
- Assert #3 may find a stale baseline → would false-FAIL.

**Verdict on uncommitted draft:** `ESCALATE:uncommitted-walk` — never `BAR_MET`, never `CONTINUE`. This is a caller error (the Planner should commit before invoking), surfaced as an escalation rather than a silent false result.

**Confirmation that the live workflow commits per walk:** The git log shows `[draft]` commits per phase (e.g. `[draft] lint sub-check trio w1 lens-1 ...`, `[draft] lint sub-check trio w1 lens-2 ...`). Each walk produces one or more commits before cycle_check would be invoked.

### Decision function (assert aggregation)

The decision function evaluates, in order:

1. **Parse guard (fail closed):** If the input has 0 or >1 DC blocks, or if no lens lines are parseable → `ESCALATE:unparseable`.
2. **Uncommitted guard:** If the current walk has no git commit → `ESCALATE:uncommitted-walk`.
3. **Assert evaluation:** Run asserts #1, #2, #3. Each returns PASS, FAIL, or N/A.
   - Any FAIL → `ESCALATE:assert-fail:<N>`.
4. **Restructuring fold check:** If the current walk contains a restructuring fold → `ESCALATE:restructuring-fold`.
5. **Yield-rising check:** If the current walk's instruction-class count > prior walk's → `ESCALATE:yield-rising`.
6. **Plateau check:** If 3 consecutive walks at flat instruction-class count with no new finding class → `ESCALATE:plateau`.
7. **BAR_MET check:** If the current walk is dry (instruction-class count = 0) AND all asserts are PASS or N/A AND no restructuring fold → `BAR_MET`.
8. **Default:** `CONTINUE`.

**How N/A participates:** An assert returning N/A (class split absent — the 27/37 case) is treated as neutral. It does not block BAR_MET and does not trigger ESCALATE. The bar is met when the walk is dry AND no assert FAILed — N/A asserts are simply not evaluated.

### Exit-code convention

| Exit code | Meaning |
|---|---|
| 0 | CONTINUE or BAR_MET (the cycle is healthy). |
| 1 | ESCALATE (the cycle is blocked; reason on stdout). |
| 2 | cycle_check itself could not run (missing file, bad arguments, internal error). |

### Stdout format

Single line to stdout:
```
CONTINUE
BAR_MET
ESCALATE:plateau
ESCALATE:unparseable
ESCALATE:assert-fail:1
ESCALATE:uncommitted-walk
```

Both callers (Planner in-session, depositor at deposit) parse this single line. The depositor re-runs and compares its verdict to the written one; a mismatch is a HOLD reason.

---

## Output Receipt

**Status:** COMPLETE

**Q1 answered:** 37 files confirmed. Three distinct per-lens format families enumerated (class-split, older without split, transitional). Dash variance (`—` consistent), lens-name variance (`Integration` vs `Integration-record`), pass-token variance (`w1`/`c1`/`a1`/`cc`/`Closing`) documented. Partial live-block form characterized. Per-walk STATUS lines identified as a new form not yet in Done/.

**Q2 answered:** Assert-to-input table produced. Confirmed `cycle_yields.py` lacks the class-split axis. Gaps identified: (a) no class-split regex, (b) no per-phase-commit assertion, (c) fold_check invocation not mechanized.

**Q3 answered:** Presence-based N/A discriminator recommended. Degenerate inputs and their correct verdicts enumerated (zero-walk, partial, multiple-block, all-unparseable, uncommitted).

**Q4 answered:** Check (f) mechanism quoted and confirmed. False-clean defect traced to last-lens-line reading. Supersede-then-retire recommendation stated; removal NOT authorized.

**Q5 answered:** Rule 27 Gap Assessment table produced with 9 rows covering all load-bearing behaviors from Q1–Q6. Each row is build-ready.

**Q6 answered:** Three-verdict contract designed (CONTINUE/BAR_MET/ESCALATE). Plateau threshold = 3, stateless derivation specified. ESCALATE reason vocabulary enumerated. Decision function specified in priority order. Exit-code convention and stdout format defined. Invocation context (Planner + depositor) and git precondition stated.

**Planner count correction:** The Planner's walk-0 measurement of "5 files carry class-split lines" is accurate if counting files with `instruction ... record` in ANY position (per-lens, Walk-split, Closing); the per-lens class-split form specifically appears in 3 files. 10 files total carry the class-split in at least one position.

**Method transparency (V3 guard):** Every count in this census was produced by `grep` with the exact command stated. The 37-file count was cross-checked: (1) `grep -rl` and (2) `cycle_yields.py`'s own `extract_dc_blocks` both produce 37. The class-split count was cross-checked: (1) `grep -rn '— instruction [0-9]'` on per-lens lines and (2) `grep -rn 'instruction.*record'` on all lines with manual classification of position.
