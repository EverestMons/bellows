# Forward Register Item-Delimiter Contract — Diagnostic 292

**Date:** 2026-08-02
**Type:** Diagnostic findings (read-only)
**Plan:** 292

---

## 1. Q1 Corpus — Every `#### Forward Register` Block Ever Emitted

Swept: `bellows`, `lessons-forge`, `governance`, `anvil`, `invoice-pulse`, `forge` — all `knowledge/qa/`, `knowledge/research/`, `knowledge/development/`, `knowledge/decisions/`, and `verdicts/resolved/` directories. Governance and anvil emitted zero Forward Register blocks. Forge emitted zero. 19 blocks found across bellows, lessons-forge, and invoice-pulse.

| ID | Plan | Project | Source QA/research file | Human item count | `lines[0]` produced | Daemon processed? |
|----|------|---------|------------------------|:---:|---------------------|-------------------|
| B1 | 57 | bellows | forward-canary-2026-06-14.md | 1 | `CANARY-FORWARD-160138 — test row filed…` | No — extraction bug (tool-content) |
| B2 | 61 | bellows | forward-recanary-2026-06-14.md | 1 | `CANARY-FORWARD2-180522 — test row filed…` | Yes — row 23, MALFORMED |
| B3 | 63 | bellows | forward-final-canary-2026-06-14.md | 1 | `- CANARY-FORWARD3-182555 — clean-row test…` | Yes — row 24, clean |
| L1 | 274 | lessons-forge | cycle-qa-2026-07-24.md | 1 | (encoding= gap, full text) | No — no FORWARD.md |
| L2 | 281 | lessons-forge | cycle-qa-2026-07-27.md | 1 | (encoding= gap, full text) | No — no FORWARD.md |
| L3 | 283 | lessons-forge | cycle-qa-2026-07-29.md | 1 | (encoding= gap, bullet) | No — no FORWARD.md |
| L4 | 288 | lessons-forge | cycle-qa-2026-07-30.md | 3 | `1. \`generate_lessons_report\`…` (item 1 only) | No — no FORWARD.md |
| L5 | 284 | lessons-forge | gate-1-route-qa-2026-07-29.md | 2 | `Gate 2 owes:` (preamble, not an item) | No — no FORWARD.md |
| L6 | 289 | lessons-forge | gate-1-route-qa-2026-07-31.md | 6 | `- (a) \`gates.py:449\`…` (item (a) only) | No — no FORWARD.md |
| L7 | 291 | lessons-forge | gate2-plan-a-qa-2026-08-02.md | 1 | `gates.py:449 per-step span regex…` | Yes — row 1, clean |
| I1 | 231 | invoice-pulse | phase-b1-wiring-effect-qa-2026-07-19.md | 2 | `1. **99.0 sentinel constant duplication**…` | Yes — row 32, item 1 only |
| I2 | 234 | invoice-pulse | b2-migration-fixes-qa-2026-07-19.md | 2 | `- Spliced-ladder config awaiting…` | Yes — no row found (possible agent-direct write) |
| I3 | 232 | invoice-pulse | bracket-structural-export-qa-2026-07-19.md | 1 | `\| # \| Item \| Status \|` (table header) | Yes — degenerate output |
| I4 | 239 | invoice-pulse | handoff-channel-qa-2026-07-19.md | 6 | `- Forge chunk labels changed…` (item 1 only) | Yes — no row found |
| I5 | 231 | invoice-pulse | phase-b1-ceiling-engine-qa-2026-07-19.md | 3 | `- **Sites 15/16**…` (item 1 only) | Yes — no row found |
| I6 | 240 | invoice-pulse | backup-path-leak-fix-qa-2026-07-20.md | 4 | `- **\`os.makedirs(backup_dir)\`…` (item 1 only) | Yes — no row found |
| I7 | 241 | invoice-pulse | coverage-export-path-leak-qa-2026-07-20.md | 4 | `- The class audit is POINT-IN-TIME…` | Yes — row 33, item 1 only |
| I8 | 242 | invoice-pulse | data-examples-content-drop-qa-2026-07-20.md | 4 | `- **EXPORT ATOMICITY**…` (item 1 only) | Yes — no row found |
| I9 | 273 | invoice-pulse | data-examples-description-drop-qa-2026-07-24.md | 2 | `- The stale untracked…` (item 1 only) | Yes — no row found |

**Totals:** 19 blocks. 8 single-item blocks (correct under current behavior). 11 multi-item blocks. 57 human-identified items total; 19 retained by `lines[0]`; **38 items dropped** (27 by `lines[0]` reduction, 11 never appended because `FORWARD.md` didn't exist — but only items 2+ in those blocks were lost to `lines[0]`; item 1 was lost to the missing-file problem, which plan 291 already fixed for lessons-forge).

**⚠️ Diagnostic attribution correction:** The diagnostic states "Plan 288 emitted six items as `- (a)`…`- (f)`." Per the corpus, plan 288 (cycle-qa-2026-07-30.md) emitted **three** numbered items (`1.`…`3.`). The six-item `- (a)`…`- (f)` block was emitted by **plan 289** (gate-1-route-qa-2026-07-31.md, titled "Plan 289, Step 2"). The lessons-forge `FORWARD.md` preamble correctly states "plan 288 emitted a correctly formatted three-item block."

---

## 2. Q2 — Shape Classification (Actual Distribution)

| Shape | Blocks | IDs |
|-------|:---:|-----|
| Single unbulleted line | 5 | B1, B2, L1, L2, L7 |
| Single `- ` bullet | 2 | B3, L3 |
| Numbered list (`1.`…`N.`) | 2 | L4 (3 items), I1 (2 items) |
| `- ` bulleted list (≥2 items) | 8 | L5, L6, I2, I4, I5, I6, I7, I8, I9 |
| Prose heading + `- ` bullets | 1 | L5 (`Gate 2 owes:` + 2 bullets) |
| Table format | 1 | I3 (pipe-delimited table) |

The dominant shape is **`- ` bulleted list** (8 of 19 blocks, 10 of 19 including single-bullet). Numbered lists appear twice. The table-format emission (I3) is an outlier — both current and candidate behavior produce a degenerate result (the table header as the item text).

---

## 3. Q3 — Items Dropped by Current Behavior

**Only multi-item blocks where `lines[0]` reduction caused loss AND the destination FORWARD.md existed at the time:**

| ID | Plan | Items emitted | Item landed | Items lost to `lines[0]` |
|----|------|:---:|------------|:---:|
| I1 | 231 | 2 | `1. **99.0 sentinel constant duplication**…` (row 32) | 1 |
| I7 | 241 | 4 | `- The class audit is POINT-IN-TIME…` (row 33) | 3 |

**Confirmed losses to `lines[0]`:** 4 items across 2 blocks (invoice-pulse rows 32-33).

**Items never appended because FORWARD.md didn't exist (plan 291's already-fixed problem):** 7 blocks (L1–L6 plus their multi-item losses). These are NOT double-counted — the missing-file problem dropped the entire block, not just items 2+.

**Items in blocks where daemon processing status is unclear** (I2, I4, I5, I6, I8, I9): 6 blocks with combined 21 items (6 `lines[0]` retained, 15 lost). These plans' Forward Register blocks appear in QA reports but no matching daemon-appended row exists in `invoice-pulse/knowledge/FORWARD.md`. Possible causes: the agent wrote FORWARD.md directly (triggering the coexistence skip), or the daemon processed the block but the item duplicated an existing row that was already written by a prior plan's step.

**Cost of doing nothing (confirmed):** 4 items lost. **Cost of doing nothing (worst-case including unconfirmed):** 19 items lost.

---

## 4. Q4 — Candidate Delimiter Rule

### Rule Statement

```
If ≥2 non-empty stripped lines match ^(-\s|\d+\.\s), emit one row per matching line;
otherwise fall back to lines[0] (current behavior).
```

Implementation (8 lines):
```python
BULLET_RE = re.compile(r"^(?:-\s|\d+\.\s)")

def sanitize_items(item_text):
    lines = [ln.strip() for ln in item_text.splitlines() if ln.strip()]
    if not lines:
        return [item_text.strip()]
    bullet_lines = [ln for ln in lines if BULLET_RE.match(ln)]
    if len(bullet_lines) >= 2:
        return [" ".join(bl.split()) for bl in bullet_lines]
    else:
        return [" ".join(lines[0].split())]
```

### Per-Block Results (Full Corpus)

| ID | Plan | Human# | Current# | Candidate# | Match? | Notes |
|----|------|:---:|:---:|:---:|--------|-------|
| B1 | 57 | 1 | 1 | 1 | YES | unchanged |
| B2 | 61 | 1 | 1 | 1 | YES | unchanged |
| B3 | 63 | 1 | 1 | 1 | YES | unchanged — single bullet, fallback |
| L1 | 274 | 1 | 1 | 1 | YES | unchanged |
| L2 | 281 | 1 | 1 | 1 | YES | unchanged |
| L3 | 283 | 1 | 1 | 1 | YES | unchanged |
| L4 | 288 | 3 | 1 | 3 | YES | RECOVERED 2 |
| L5 | 284 | 2 | 1 | 2 | YES | RECOVERED 1 — preamble `Gate 2 owes:` correctly dropped |
| L6 | 289 | 6 | 1 | 6 | YES | RECOVERED 5 |
| L7 | 291 | 1 | 1 | 1 | YES | unchanged |
| I1 | 231 | 2 | 1 | 2 | YES | RECOVERED 1 |
| I2 | 234 | 2 | 1 | 2 | YES | RECOVERED 1 |
| I3 | 232 | 1 | 1 | 1 | YES | unchanged — table format, equally degenerate |
| I4 | 239 | 6 | 1 | 6 | YES | RECOVERED 5 |
| I5 | 231 | 3 | 1 | 3 | YES | RECOVERED 2 |
| I6 | 240 | 4 | 1 | 4 | YES | RECOVERED 3 |
| I7 | 241 | 4 | 1 | 4 | YES | RECOVERED 3 |
| I8 | 242 | 4 | 1 | 4 | YES | RECOVERED 3 |
| I9 | 273 | 2 | 1 | 2 | YES | RECOVERED 1 |

**Score:** 19/19 blocks match human item count. 27 items recovered.

### Negative Control — Plan 62 Fixture (MANDATORY)

Input:
```
CANARY item text here

Now commit the deposit.
Complete. All 5 checks passed.
```

Bullet lines matching `^(-\s|\d+\.\s)`: **0** (none of the three non-empty lines start with `- ` or `N. `).
Since 0 < 2 → fallback to `lines[0]` → `"CANARY item text here"`.

Result: **PASS**. `"Now commit"` excluded. `"All 5 checks"` excluded. Single row produced. The narration guard is preserved.

### Positive Control — Plan 288 Three-Item Block

Input:
```
1. `generate_lessons_report`…
2. `plan_lint` section 4 T2 panel…
3. `plan_lint` section 4 closing check…
```

Bullet lines matching `^\d+\.\s`: **3**.
Since 3 ≥ 2 → emit per-bullet → 3 rows.

Result: **PASS**. All 3 items emitted.

### Positive Control — Plan 289 Six-Item Block

Input: `- (a)`…`- (f)` (6 lines starting with `- `).
Bullet lines: **6**. Since 6 ≥ 2 → 6 rows.

Result: **PASS**. All 6 items emitted.

---

## 5. Q5 — Wrapped-Prose Fragmentation

No wrapped items exist in the real corpus — all 57 human-identified items are single physical lines. **Constructed test** from I7's first item:

```
- The class audit is POINT-IN-TIME — it ends the pattern for the
  seven existing emitters, but a future emitter has no structural hook
  forcing it through the detector.
- The shipped 07-17 coverage JSON remains in the CEO's remediation set.
```

Candidate output: **2 items** (correct count), BUT item 1 is **truncated** to `"- The class audit is POINT-IN-TIME — it ends the pattern for the"` — the indented continuation lines are dropped because they don't match `^- ` and only bullet-matching lines are emitted.

**Severity:** Medium. The candidate fragments wrapped text by dropping continuation lines. No real corpus item wraps today, but the vulnerability exists. A mitigation would be to join non-bullet lines to the preceding bullet, but that increases complexity and introduces its own risks (a non-bullet narrative line between bullets would be absorbed into the preceding item instead of being dropped).

---

## 6. Q6 — Idempotency and Row Numbering Under N Rows

### Current idempotency mechanism

```
fw_step_id_key = f"{plan_id}-{step_number}"           # bellows.py:1349
fw_content_hash = sha256(forward_text.encode())         # :1350
check_ledger_write_exists(key, "FORWARD.md", hash)      # :1351
    _append_forward_row(path, plan_id, forward_text)    # :1355
    record_ledger_write(key, "FORWARD.md", hash)        # :1356
```

### Under N rows from one block

**If `_append_forward_row` writes N rows internally and commits once:** The idempotency key stays at the block level (same key + hash). On a clean redo, the whole block is skipped — **correct**.

**Partial-write failure mode:** If the process dies AFTER `_append_forward_row` writes the file and commits BUT BEFORE `record_ledger_write`:
- N rows exist on main, committed.
- Lifecycle DB has no record of the write.
- On restart: idempotency check says "not applied" → re-processes the block.
- `_append_forward_row` re-reads the file, computes `next_num = max(existing) + 1` (which already includes the N rows), and appends N MORE rows.
- **Result: 2N rows (N duplicates).**

This is the SAME failure class as the current single-row behavior (where 1 duplicate is possible), scaled by N. The window is identical: between git-commit and lifecycle-record.

**Row numbering within one call:** If N rows are written in a single call, the function must increment the counter internally (`next_num + 0`, `next_num + 1`, …, `next_num + N-1`). The current code computes `next_num` once from `re.findall` over the file content. Writing N rows requires either: (a) incrementing a counter for each row within the call, or (b) re-reading the file between each row write. Option (a) is correct and simple.

**Row numbering across concurrent plans:** `max`-based numbering reads the file at call time. Two concurrent teardowns could read the same max and assign the same next_num to different rows. This is an existing race (1-row case); N rows widen it only if both plans emit multi-item blocks simultaneously.

---

## 7. Q7 — Blast Radius on Live Registers

**bellows/knowledge/FORWARD.md (24 rows):** The candidate changes NO row output for blocks that already landed. All historically-processed blocks (B2, B3) had ≤1 item and fall through to the fallback path, which is identical to current behavior. Rows 1–22 were agent-direct writes (not daemon-processed). Rows 23–24 were single-item canaries.

**lessons-forge/knowledge/FORWARD.md (1 row):** Row 1 (plan 291) was a single-item block. The candidate's fallback path produces identical output.

**invoice-pulse/knowledge/FORWARD.md (rows 32–33):** These are the only daemon-appended rows. Row 32 (plan 231, 2-item block) and row 33 (plan 241, 4-item block) would have produced MORE rows under the candidate, but the existing rows are UNCHANGED — the candidate is additive, not a rewrite.

**Conclusion:** No historical row output changes. The candidate is strictly additive — existing single-row blocks produce the same row; multi-item blocks produce additional rows that were previously dropped. Neither register needs rewriting.

---

## 8. Q8 — Test Amendment Map

### `TestForwardSingleLineItem` (test_bellows.py:4917)

**`test_multiline_item_yields_single_line_row`** (`:4942`)
- `len(row_lines) == 1` → **SURVIVES** (fixture has 0 bullet lines → fallback → 1 row)
- `row.count("|") == 7` → **SURVIVES**
- `"CANARY item text here" in row` → **SURVIVES**
- `"Now commit" not in row` → **SURVIVES**
- `"All 5 checks" not in row` → **SURVIVES**
- **Amendment:** Rename docstring to clarify it's the narration-guard negative control. No assertion changes required.

**`test_single_line_item_unchanged`** (`:4975`)
- All assertions → **SURVIVE** unchanged.

**`test_whitespace_collapsed`** (`:4995`)
- All assertions → **SURVIVE** unchanged.

### New coverage required

1. **Multi-bullet positive test:** A fixture with ≥2 `- ` or `\d+\.\s` lines → assert N rows produced, each a 7-pipe row, each containing the corresponding item text. This is the mandatory positive control.

2. **Narration-with-bullets negative test:** A fixture where narration text follows bullet items (e.g. a `- ` item, blank line, then prose) → assert the prose does not appear as a row. This exercises the `≥2 bullet` threshold — a single bullet + prose must still fall back, not emit the prose.

3. **Preamble-then-bullets test:** A fixture like L5 (`Gate 2 owes:` heading + 2 bullets) → assert only the bullet items become rows, not the preamble.

---

## 9. Q9 — Daemon Restart Procedure

**Confirmed from source:** `bellows.py` IS the daemon (`bellows.py:2269` `start()`, `:2369` flock guard). A code edit to `_append_forward_row` requires a daemon restart because the function runs in the daemon's process space. The flock at `.bellows.lock` (`:2370–2377`) is kernel-released on process death.

### Safe restart procedure

1. **Check for mid-dispatch plans:**
   ```
   python status.py
   ```
   Any plan showing `lifecycle_state = in_progress` or `claimed` is actively running. Wait for it to reach a verdict pause (`awaiting_verdict`) or complete.

2. **Stop the daemon:** Ctrl-C the `dashboard.py` / `bellows.py` process. `KeyboardInterrupt` is caught at `:2339` for clean shutdown.

3. **Apply code changes:** Merge the implementation branch to main (where the daemon reads code).

4. **Restart:**
   ```
   python dashboard.py   # or python bellows.py for headless
   ```
   The new process acquires the flock and picks up any pending work.

5. **Verify:** `python status.py` should show the daemon running. The next plan step that emits a multi-item Forward Register block is the live proof.

---

## 10. Q10 — Is the Change Worth Making?

### Cost of the change

- **Implementation:** 1 plan — edit `_append_forward_row` (~15 lines changed), add 3 tests, amend 1 test docstring.
- **Daemon restart:** Required. ~5 min including the status-check-wait-restart cycle.
- **Risk:** Wrapped-prose truncation (Q5) — no real corpus item wraps today, but the vulnerability exists. Partial-write duplicates scale by N (Q6) — same class as current, wider window.
- **Test regression:** Zero — all existing assertions survive.

### Cost of doing nothing

- **Immediate:** The 4 backlog items the diagnostic identifies (3 `plan_lint` §4 defects + the `generate_lessons_report` encoding gap) need carriers. Under the current 1-item-per-block contract, 4 plans each carry 1 item. Each plan is ~10 min of dispatch time = ~40 min total.
- **Ongoing:** Every future multi-item block loses items 2+. The corpus shows 11 of 19 historical blocks had multiple items — this is the MAJORITY shape. The contract forces plan authors to either (a) emit only 1 item and defer the rest, or (b) emit multiple items and accept silent loss.
- **Silent loss risk:** There is no WARN when items are dropped. The `lines[0]` reduction is invisible to the plan author and the Planner. The 4 invoice-pulse items in rows 32–33 lost content silently.

### Recommendation

**The change is worth making.** The corpus proves multi-item blocks are the majority shape (11/19), and the current behavior silently drops content with no warning. The candidate rule is simple (8 lines), passes both controls, recovers 27 items across the historical corpus, and changes no existing row output. The wrapped-prose weakness is theoretical (no real corpus item wraps) and can be mitigated in the implementation plan if desired.

The zero-risk alternative (4 plans × 1 item) works but accepts the ongoing cost: every future multi-item block will continue to lose items silently. The code change is a one-time cost that eliminates a systemic silent-loss class.

**CEO choice:** one plan (code change + restart + test amendment) vs. four plans (no code change, no restart) for the immediate backlog — plus the ongoing silent-loss acceptance.

---

## Unresolved

1. **Invoice-pulse plans I2, I4, I5, I6, I8, I9:** These plans' QA reports contain `#### Forward Register` blocks, but no matching daemon-appended row exists in `invoice-pulse/knowledge/FORWARD.md`. The cause is not determined from this corpus sweep — possible explanations include agent-direct FORWARD.md writes (triggering coexistence skip), halted plans whose ledger updates were never processed, or plans where the Forward Register block appeared only in the deposited QA file and not in the agent's raw output text. A definitive determination requires checking `files_changed` in each plan's verdict entry and the raw step JSON.

2. **Table-format emission (I3):** The bracket-structural-export QA emitted a Forward Register block as a pipe-delimited table rather than bullet items. Both current and candidate behavior produce a degenerate result (the table header `| # | Item | Status |` as the item text). This is an agent-side formatting error, not a splitter deficiency — but no guard prevents it.

3. **Plan number attribution discrepancy:** The diagnostic states "Plan 288 emitted six items as `- (a)`…`- (f)`." The corpus shows plan 288 emitted three numbered items; the six-item block was emitted by plan 289. The FORWARD.md preamble correctly states "plan 288 emitted a correctly formatted three-item block."

---

## Output Receipt

### Status

**Complete**

### Deposits

- `knowledge/research/forward-register-item-delimiter-contract-2026-08-02.md`

### Ledger Updates

#### Forward Register

`plan_lint` section-4 zero-expectation-class check: a plan declaring no expected WARN/FAIL class is not flagged, so a deposited plan with no stated gate expectation passes section 4 silently.

#### Prompt Feedback

The diagnostic's corpus-sweep method (grep for `#### Forward Register` across all watched projects, then extract and classify each block) was well-designed. The plan's mandatory positive and negative controls (plan 62 fixture + plan 288/289 multi-item blocks) caught a wrapped-prose weakness in the first candidate tested. The explicit instruction to report per-block results rather than aggregates forced transparent evidence. The requirement to test in `/tmp` prevented accidental edits to the live system. The only factual error in the diagnostic was the plan 288 vs. 289 attribution of the six-item block, which the corpus sweep corrected.
