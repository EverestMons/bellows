# Ledger-Apply Regression Root Cause + in_progress-Strand Recovery Gap

**Date:** 2026-06-14 | **Plan:** 53 | **Agent:** Bellows Systems Analyst | **Step:** 1

---

## Section 1 — Reproduce the Empty-Ledger

### Finding

The plan-52 step JSON (`logs/20260614-134433-step.json`) contains
`CANARY-PROJSTATUS-134417` and `CANARY-FEEDBACK2-134417` in its
`raw_output` (the full NDJSON stream from `claude -p`), but
`parsed.ledger_updates` is `{'feedback': None, 'project_status': None, 'forward': None}`.

**Root cause: `parser.parse()` only extracts `### Ledger Updates` from
`raw.get("result", "")` (parser.py:10), which is the `result` field of the
`type: "result"` terminal event in the Claude stream-json output. This field
contains ONLY the final assistant message.**

### Reproduction

The `type: "result"` event for plan 52 has a `result` field of 529 characters —
a short summary ("Complete. Plan 52 — PROJECT_STATUS activation live canary: …")
that does NOT contain `### Ledger Updates`. The `### Ledger Updates` section was
emitted in an earlier assistant turn (visible in the raw NDJSON stream) where the
agent wrote its Output Receipt with tool-use calls interleaved.

```
# Reproduced via:
result_event['result']  # 529 chars, no "### Ledger Updates"
parse(result_event)['ledger_updates']  # all None
```

### Working control (plan 50)

Plan 50's `result` field is 817 characters and contains the FULL Output Receipt
including `### Ledger Updates > #### Prompt Feedback`. The agent happened to emit
everything in a single final assistant message with no interleaved tool calls.

```
# Plan 50:
result_event['result']  # 817 chars, contains "### Ledger Updates"
parse(result_event)['ledger_updates']['feedback']  # populated correctly
```

### Discriminating difference

The EXACT discriminator is whether the agent emits `### Ledger Updates` in its
**final** assistant message (the one captured in `result_event['result']`) or in
an **intermediate** assistant turn (which is only in the NDJSON stream, not the
`result` field). Multi-turn agents that use tools (Read, Edit, Write, Bash)
typically emit their Output Receipt in an intermediate turn and then produce a
short summary as their final message. The parser never sees the intermediate turns.

The data flow is:

1. `runner.py:216-226` — iterates NDJSON lines, keeps last `type: "result"` event
2. `runner.py:249-252` — passes `result_event` to `parser.parse()`
3. `parser.py:10` — `result_text = raw.get("result", "")` — ONLY the final message
4. `parser.py:50-77` — regex extraction of `### Ledger Updates` subsections from `result_text`
5. `bellows.py:1132` — `ledger = parsed.get("ledger_updates") or {}` — all None
6. No content → no handler fires → no WARN emitted → silent data loss

---

## Section 2 — Is It Slice-2 Code or Pre-Existing?

### Confirmed: PRE-EXISTING fragility, NOT a Slice-2 regression.

**parser.py was NOT changed by plan 51** (confirmed: `parser.py @ git:8a33253` in
heartbeat at 12:57:19, same hash before and after plan 51's merge at 13:12:00).

Plan 51 (`git show 3fa76f6 -- bellows.py lifecycle.py gates.py`) changed:

1. **bellows.py** — Added `extract_agent()` (L210-215), added `parsed["_step_number"]`
   and `parsed["_agent"]` enrichments (L557-558, L673-674), extended
   `_apply_ledger_updates` PROJECT_STATUS path with idempotency guard (L1184-1196).
2. **gates.py** — Removed `PROJECT_STATUS.md` from `SCOPE_ALLOWLIST`.
3. **lifecycle.py** — No changes in plan 51's diff.

**None of these changes altered:**
- Which `parsed` dict is passed to `_apply_ledger_updates` (same object from `runner.run_step()`)
- The `ledger_updates` key name in parser.py (unchanged)
- The extraction regex in parser.py (unchanged)
- Any exception path that could swallow errors

The bug exists because `parser.parse()` has always operated on
`raw.get("result", "")` — the single-message `result` field. Plan 50 worked by
coincidence: its agent emitted everything in one final message. Plan 51 step 1,
plan 51 step 2, and plan 52 step 1 all failed because their agents used tools and
then emitted a short summary as their final message.

---

## Section 3 — Why Did Plan 51's Own Feedback Not Land?

### Evidence

**Plan 51 step 1** (`logs/20260614-125259-step.json`):
- `result_text` length: 1298 chars — a summary with no `### Ledger Updates`
- `ledger_updates`: all None
- `raw_output` contains `### Ledger Updates > #### Prompt Feedback` with real content
- Terminal log: NO ledger line at 13:04:38 (step 1 gates completed)

**Plan 51 step 2 (QA)** (`logs/20260614-130526-step.json`):
- `result_text` length: 984 chars — a QA summary with no `### Ledger Updates`
- `ledger_updates`: all None
- `raw_output` contains `### Ledger Updates > #### Prompt Feedback` with real content
  (e.g., at offset ~263767: "2026-06-14 — projectstatus-activation (Bellows QA Step 2)")
- Terminal log: NO ledger line at 13:11:08 (step 2 gates completed)

**Plan 51 step 1 terminal log** at 12:22:10 (plan 49, step 1):
`ledger: agent wrote agent-prompt-feedback.md old-style, skipping daemon write`
— this is plan 49's step 1, not plan 51. Plan 49 step 1 wrote the file directly
(old-style). Plan 49 step 2 ran on the plan-49 daemon (pre-Slice-2 merge).

**Conclusion:** Plan 51's agents emitted feedback via the `### Ledger Updates`
channel correctly (new protocol). The daemon correctly received the output and
parsed it, but `parser.parse()` extracted from the wrong field (final `result`
only). The feedback was silently dropped — same root cause as plan 52. **The
regression predates plan 52 and affects ALL plans whose agents use multi-turn
tool interactions.**

### Confirmation: `prompt_feedback` table

```sql
sqlite3 lifecycle.db "SELECT id, plan_id, step_number, agent FROM prompt_feedback"
-- 1|50|||   (only plan 50's canary row)
```

No rows for plan 51 or 52.

---

## Section 4 — Blast Radius + Data-Loss Assessment

### What is lost

| Channel | Status | Plans affected |
|---|---|---|
| Prompt Feedback via channel | **SILENTLY DROPPED** | Plans 51, 52 (and all future multi-turn plans) |
| PROJECT_STATUS via channel | **SILENTLY DROPPED** | Plan 52 canary (and all future) |
| Forward Register via channel | **SILENTLY DROPPED** | None yet emitted, but same bug applies |
| Deposits (file commits) | **SAFE** | Teardown merges worktree commits to main; proven by plan 52 (619a6f8) |
| Lifecycle DB writes | **SAFE** | Steps, gates, deposits all recorded correctly |

### Real data lost

- **Plan 51 step 1:** Developer prompt feedback (efficiency observations about specialist file, design doc)
- **Plan 51 step 2:** QA prompt feedback (dev log accuracy, governance flip observations)
- **Plan 52:** Canary tokens only (no real data, by design)

No production-critical data lost. The feedback is still recoverable from the
raw NDJSON logs (`raw_output` field in the step JSON files).

### Slice 3 (FORWARD) must stay blocked

The FORWARD register channel uses the same `### Ledger Updates > #### Forward Register`
extraction path (parser.py:69-77). It would suffer the same silent-drop bug.
**Slice 3 MUST remain blocked until the parser fix ships.**

---

## Section 5 — #48 in_progress-Strand Recovery Gap

### Current state

`recover_half_claimed` (lifecycle.py:218-291) only selects
`lifecycle_state = 'claimed'` (lifecycle.py:237, 243). Plans that reached
`'in_progress'` state and then lost their runner (daemon restart during execution)
are invisible to recovery.

Plan 48 specifically:
```sql
-- id=48, type=executable, lifecycle_state=in_progress, closed_at=NULL
-- deposit_placeholder_name=executable-draft-115339.md
```

Terminal log shows plan 48 was running at 11:54:29, daemon restarted at 12:04:46
(session restart), and plan 48 was never recovered. Its worktree is gone
(not in `git worktree list`). No `in-progress-executable-48.md` exists on disk.
It appears as a perpetual phantom in any `closed_at IS NULL` dashboard query.

### Proposed minimal safe extension

Add an `in_progress` recovery clause to `recover_half_claimed` with these
discriminators to avoid touching legitimately-running plans:

1. **No worktree on disk** — check `git worktree list` or probe
   `.bellows-worktrees/<id>/` existence. A legitimately-running plan has a live
   worktree; a stranded one does not.
2. **No live runner process** — optionally check for a `claude -p` process with
   the plan's session ID (defense-in-depth, not required if worktree check suffices).
3. **Age guard** — same `age_guard_seconds` (default 300s) as the `claimed`
   recovery path, to avoid racing with a plan that just started.
4. **State transition** — set `lifecycle_state = 'abandoned'` and
   `closed_at = <now>` (same as the `claimed` abandon path).

The query would be:
```sql
SELECT id, type, deposit_placeholder_name, created_at, target_project
FROM plans WHERE lifecycle_state = 'in_progress'
  AND target_project = ?
```

Then for each: check if worktree exists at `.bellows-worktrees/<id>/`.
If absent AND age > age_guard_seconds → mark `abandoned` + set `closed_at`.

**Plan 48 resolution:** Under this rule, plan 48 (no worktree, age >> 300s)
would be set to `lifecycle_state='abandoned', closed_at=<now>`. It would
disappear from the `closed_at IS NULL` in-flight view.

---

## Section 6 — Gap Assessment + Verification Blocks

### Gap Assessment — Ledger-Apply Fix

| Gap | Current State (file:line) | Proposed State | Change Required |
|---|---|---|---|
| Parser only reads final `result` field | parser.py:10 `result_text = raw.get("result", "")` | Parser scans full NDJSON stream for `### Ledger Updates` in any assistant message | parser.py: add multi-message extraction; OR runner.py: concatenate all assistant text blocks into a synthetic `result_text` before passing to parser |
| Silent drop — no WARN on missing ledger | bellows.py:1132 `ledger = parsed.get("ledger_updates") or {}` — empty dict → no handler fires | Emit WARN when agent's raw output contains `### Ledger Updates` but parsed dict has all-None ledger | bellows.py or runner.py: add detection + WARN |
| Forward Register (Slice 3) blocked | parser.py:69-77 — same extraction path | Same fix unblocks Slice 3 | No additional change needed |

### Gap Assessment — in_progress-Recovery Fix

| Gap | Current State (file:line) | Proposed State | Change Required |
|---|---|---|---|
| `recover_half_claimed` only selects `claimed` | lifecycle.py:237,243 `WHERE lifecycle_state = 'claimed'` | Also select `'in_progress'` with worktree-absence discriminator | lifecycle.py: extend query + add worktree check logic |
| Stranded in_progress plans show as phantoms | Dashboard `closed_at IS NULL` query | Stranded plans marked `abandoned` at startup | Same lifecycle.py change |
| Function name is now misleading | `recover_half_claimed` | Consider renaming to `recover_stranded_plans` | Optional, cosmetic |

### Verification Blocks

**V1 — Empty-ledger reproduction:**
```
Claim: parser.parse() returns all-None ledger_updates for plan-52's result event
Query: python3 -c "import json, sys; sys.path.insert(0,'.'); from parser import parse; d=json.load(open('logs/20260614-134433-step.json')); raw=d['raw_output']; [re:=None]; [re:=json.loads(l) for l in raw.split(chr(10)) if l.strip() and (e:=None) is None and (e:=json.loads(l) if l.strip() else None) is not None and isinstance(e,dict) and e.get('type')=='result']; print(parse(re)['ledger_updates'])"
Expected: {'feedback': None, 'project_status': None, 'forward': None}
```

**V2 — Confirmed root-cause line:**
```
Claim: parser.py:10 extracts only the final result field (529 chars for plan 52)
Query: python3 -c "import json; d=json.load(open('logs/20260614-134433-step.json')); print(len(d['parsed']['result_text']))"
Expected: 529
```

**V3 — Plan-51 non-landing reason:**
```
Claim: plan 51 steps have no prompt_feedback rows; feedback was emitted via channel but dropped
Query: sqlite3 lifecycle.db "SELECT plan_id FROM prompt_feedback WHERE plan_id=51"
Expected: (empty result)
```

**V4 — recover_half_claimed state filter:**
```
Claim: recover_half_claimed only selects lifecycle_state='claimed', not 'in_progress'
Query: grep -n "lifecycle_state = 'claimed'" lifecycle.py
Expected: Lines 237 and 243 (the only WHERE clauses in recover_half_claimed)
```

### CEO Decision Forks

1. **Ledger fix shape:** Two options:
   - **(A) Runner-side concatenation (recommended):** In `runner.py`, after extracting
     the result event, also scan all `type: "assistant"` events in the NDJSON stream,
     concatenate their text content, and pass the combined text to `parser.parse()`
     (or set it as a synthetic `result` field on the event). This keeps parser.py
     unchanged and fixes the root cause at the source.
   - **(B) Parser-side raw-output scan:** Pass the full `raw_output` string to
     `_apply_ledger_updates` and have it extract `### Ledger Updates` directly.
     More invasive; requires changing the `parsed` dict shape.
   - **Recommendation:** Option A. It's the minimal change and keeps the parser's
     contract ("I parse the event dict") clean.

2. **Ship together or separately?** The ledger fix and the in_progress-recovery fix
   are independent. Recommendation: **ship as one executable with two steps**
   (dev + QA). Both are small changes (lifecycle.py + runner.py), and a single
   QA pass is more efficient. However, they can be separated if CEO prefers to
   fast-track the ledger fix.

3. **Plan 48 cleanup:** Recommendation: **let the recovery fix handle it** at next
   daemon startup rather than a one-time DB write. This validates the recovery
   logic end-to-end. If the fix ships same-day, plan 48 is cleaned up automatically.

4. **Re-canary after fix?** Yes — the broken canary (plan 52) must be re-run after
   the parser fix to confirm both channels land. The lost plan-51 feedback can also
   be retroactively recovered from raw logs and re-injected via the DB if desired
   (optional, low priority — the feedback is still readable in the step JSON).

---

## Output Receipt
**Agent:** Bellows Systems Analyst
**Step:** 1
**Status:** Complete

### What Was Done
Root-cause investigation of the ledger-apply regression exposed by plan 52's canary. Confirmed the bug is a pre-existing fragility in parser.py (L10): it only extracts `### Ledger Updates` from the `result` field of the terminal stream-json event, which contains only the agent's final message. Multi-turn agents emit the Output Receipt in intermediate assistant turns — invisible to the parser. Also analyzed the #48 in_progress-strand recovery gap and proposed a minimal safe extension to `recover_half_claimed`.

### Files Deposited
- `knowledge/research/ledger-apply-regression-rootcause-2026-06-14.md` — full root-cause analysis with 6 sections, gap assessments, verification blocks, and CEO decision forks

### Files Created or Modified (Code)
- None (investigation only)

### Decisions Made
- Confirmed root cause is in parser.py:10 (pre-existing), not Slice-2 code
- Recommended runner-side concatenation (Option A) as fix shape
- Recommended shipping ledger fix + recovery fix as one executable

### Flags for CEO
1. **Slice 3 (FORWARD) must remain blocked** until the parser fix ships — same extraction path, same silent-drop bug
2. **Plan 51 feedback is recoverable** from raw step JSON logs if desired (low priority)
3. **Plan 48** should be cleaned by the recovery fix rather than a one-time write

### Flags for Next Step
- None (single-step investigation)

### Ledger Updates
#### Prompt Feedback
**2026-06-14 — ledger-apply-regression-rootcause (Bellows Systems Analyst Step 1)**

1. **Plan header context was comprehensive.** The diagnostic's established facts and "do not re-derive, but VERIFY" instruction saved significant time — every stated fact was verified correct, allowing the investigation to focus on the discriminating difference rather than re-establishing the timeline.

2. **Step JSON structure was the key.** The `raw_output` vs `parsed.result_text` distinction was the critical insight. Future diagnostics involving parser behavior should always start by comparing these two fields in the step JSON.

#### Project Status
CANARY-DROPPED — this milestone is emitted via the broken channel to confirm the regression is live. Expected: daemon will NOT append this to PROJECT_STATUS.md (parser will extract None from the final result message).
