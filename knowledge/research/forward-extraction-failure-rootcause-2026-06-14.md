# FORWARD Extraction Failure Root Cause — Plan 57 Canary
**Date:** 2026-06-14 | **Plan:** 58 (diagnostic) | **Agent:** Bellows Systems Analyst
**Subject:** Plan 57 FORWARD activation canary — extraction failure investigation

---

## Section 1 — Did the Agent Emit a Clean Block?

**Answer: YES — but only inside the Write tool content (the deposit file), NOT as bare assistant text.**

### Occurrence Classification

The raw NDJSON output contains **9** `### Ledger Updates` and **11** `#### Forward Register` occurrences. Classification:

| # | Location | Type | Classification |
|---|----------|------|---------------|
| 1–4 | NDJSON events 3 (user prompt) | `### Ledger Updates` | **(a) prompt-echo** — backtick-quoted instruction text: `` `### Ledger Updates > #### Forward Register` channel `` |
| 5 | NDJSON event 12 (assistant text) | `### Ledger Updates` | **(a) prompt-echo** — inline analysis referencing the channel name |
| 6 | NDJSON event 16 (assistant, tool_use: Write) | `### Ledger Updates` | **(a) inline** — inside deposit file prose: `` `### Ledger Updates > #### Forward Register` Output Receipt channel `` |
| 7 | NDJSON event 16 (assistant, tool_use: Write) | `### Ledger Updates` | **(b) GENUINE** — clean `### Ledger Updates\n\n#### Forward Register\nCANARY-FORWARD-160138…` block inside the Output Receipt section of the deposit file |
| 8 | NDJSON event 17 (user, tool_result echo of Write) | `### Ledger Updates` | Echo of #6 |
| 9 | NDJSON event 17 (user, tool_result echo of Write) | `### Ledger Updates` | Echo of #7 |

The **one genuine** clean block is inside the `content` parameter of a **Write tool_use** call (the deposit file `knowledge/research/forward-canary-2026-06-14.md`). The exact text:

```
### Ledger Updates

#### Forward Register
CANARY-FORWARD-160138 — test row filed via Output Receipt channel; daemon should append as a new FORWARD row (withdraw after verification).
```

The agent's three **assistant text blocks** (captured by `runner.py:232–234`) contain:
1. "Starting plan 57…" — no `### Ledger Updates`
2. "FORWARD.md ends at row #22…" — no `### Ledger Updates`
3. "Complete. Plan 57…" — references `#### Forward Register` inline only: "emitted via Output Receipt `` `#### Forward Register` `` channel"

**The agent never emitted `### Ledger Updates` as bare text in any assistant message.**

---

## Section 2 — Reproduce the Daemon's Parse

### Reproduced Extraction

Using the exact runner.py path (`runner.py:216–262`):

1. **`_all_assistant_text`** = concatenation of 3 assistant text blocks (1203 chars total) + result text (429 chars, duplicates block 3).
2. `re.search(r"### Ledger Updates\s*\n(.*?)(?=\n## |\Z)", _all_text)` → **no match** (`### Ledger Updates` is not present in `_all_text`).
3. `lu_match` is None → all subsection searches are skipped.
4. **Result: `forward = None`** (and `feedback = None`, `project_status = None`).

### The Hypothesis is KILLED

The leading hypothesis was: *"the parser's `### Ledger Updates` section match (parser.py:54) takes the FIRST occurrence — a prompt-echo region — that lacks a clean `#### Forward Register` body."*

**This is NOT what happened.** The parser never matched ANY `### Ledger Updates` because the heading simply does not exist in the concatenated assistant text. The heading exists only inside `tool_use` content (the Write call writing the deposit file), which `runner.py:232–234` correctly excludes from `_all_assistant_text`:

```python
# runner.py:229-234
elif event.get("type") == "assistant":
    for block in event.get("message", {}).get("content", []):
        if isinstance(block, dict) and block.get("type") == "text":
            assistant_text_parts.append(block.get("text", ""))
```

Only `"type": "text"` blocks are captured. `"type": "tool_use"` blocks (containing Write file content) are excluded.

### Comparison with Working Case (Plan 55)

Plan 55 (log `20260614-153350-step.json`) successfully extracted `feedback` and `project_status`:

| Aspect | Plan 55 (worked) | Plan 57 (failed) |
|--------|-------------------|-------------------|
| `### Ledger Updates` in `_all_text` | **5 occurrences** (3 inline echoes + 2 clean blocks) | **0 occurrences** |
| `### Ledger Updates` in `result_text` | **YES** — clean block in final message | **NO** — final message only references channel inline |
| Clean block location | **Assistant text** (bare text in final result message) | **Write tool content only** (deposit file) |
| Parser match | Matched clean block at pos 4173 in `_all_text` | No match (heading absent) |

**What made plan 55 work:** The plan-55 agent emitted the `### Ledger Updates` block as **bare text in its final assistant message** (the result event's `result` field). The plan-57 agent embedded it **only inside the deposit file** written via the Write tool and never repeated it as bare text.

---

## Section 3 — Why Didn't the Defense WARN Fire?

### The Defense-WARN Code (bellows.py:1136–1142)

```python
# bellows.py:1136-1142
_src = parsed.get("_all_assistant_text", "") or parsed.get("result_text", "")
_ledger_all_none = all(v is None for v in ledger.values()) if ledger else True
if "### Ledger Updates" in _src and _ledger_all_none:
    _log("WARN", "⚠ ledger: agent emitted ### Ledger Updates but parser extracted nothing", slug=slug)
```

### Gap Analysis

**Gap 1 — `_all_assistant_text` is never in `parsed` dict.**

The field `_all_assistant_text` is injected into the `raw` event dict by `runner.py:262`:
```python
result_event["_all_assistant_text"] = _all_text
```

The parser reads it at `parser.py:53`:
```python
ledger_source = raw.get("_all_assistant_text") or result_text
```

But `parser.parse()` does NOT include `_all_assistant_text` in its return dict (`parser.py:85–98`). So in `bellows.py:1138`:
- `parsed.get("_all_assistant_text", "")` → always `""` (key never exists)
- `"" or parsed.get("result_text", "")` → falls back to `result_text`

**The defense WARN always checks only `result_text` (final message), never `_all_assistant_text` (full concatenated text).**

Verified: `_all_assistant_text` is not present in the logged `parsed` dict for either plan 55 or plan 57.

**Gap 2 — Even fixing Gap 1, plan 57 would NOT trigger the WARN.**

Plan 57's `_all_assistant_text` contains **zero** `### Ledger Updates` headings. The heading exists only inside `tool_use` content, which is never captured into `_all_assistant_text`. So even if the WARN checked `_all_assistant_text`, the condition `"### Ledger Updates" in _src` would still be False.

**Gap 3 — The WARN cannot detect "heading emitted inside tool content only."**

The WARN was designed (plan 54) for the scenario where `### Ledger Updates` appears in assistant text but parsing fails. It has no mechanism to detect the scenario where the heading appears only inside tool call content (Write/Edit). This is a fundamentally different failure mode.

### Why Plan 55's WARN Didn't Need to Fire

Plan 55: `_ledger_all_none` was False (extraction succeeded), so the WARN condition short-circuited correctly.

---

## Section 4 — Root Cause Classification

### CONFIRMED ROOT CAUSE: (b) AGENT EMISSION + (c) CANARY-DESIGN artifact

**Primary: (b) AGENT EMISSION.** The plan-57 agent emitted the `### Ledger Updates` block exclusively inside the content of a Write tool call (writing the deposit file). It never emitted the block as bare text in an assistant message. The parser and runner correctly process only assistant text blocks, not tool-use content. The agent was expected to emit the Output Receipt as bare assistant text (as plan 55's agent did), but instead embedded it solely within the file being written.

**Contributing: (c) CANARY-DESIGN artifact.** The canary plan's prompt instructed the agent to "include a `### Ledger Updates` section with a `#### Forward Register` subsection" in "your Output Receipt." The agent interpreted this as the Output Receipt at the end of the deposit file (which is correct per the specialist template), but did NOT also emit it as bare text outside the file write. Plan 55's agent happened to duplicate the Output Receipt as bare text in its final message — this is agent behavioral variance, not a guaranteed contract.

**NOT (a) PARSER fragility.** The parser's `re.search` taking the first occurrence is irrelevant here — there was nothing to match. The prompt-echo hypothesis is killed.

### Are Real (Non-Canary) FORWARD Filings at Risk?

**YES — this risk applies to any plan, not just canaries.** The failure mode is: any agent that writes the Output Receipt only inside a deposit file (via Write tool) and does not repeat the `### Ledger Updates` block as bare assistant text will silently drop all ledger channels (feedback, project_status, forward). The canary merely revealed this latent fragility. Whether it manifests depends on agent behavioral variance in where it places the Output Receipt.

### Defense-WARN Gap (Separate Issue)

The defense WARN at `bellows.py:1138` has two independent gaps:
1. It reads `_all_assistant_text` from `parsed` dict where the key never exists (always falls back to `result_text`)
2. It cannot detect headings emitted inside tool-use content at all

Both should be fixed regardless of the extraction fix.

---

## Section 5 — Gap Assessment

### Gap Table

| Gap | Current State (file:line) | Proposed State | Change Required |
|-----|---------------------------|----------------|-----------------|
| **G1: Ledger extraction misses tool-use content** | `runner.py:232–234` — only `"type": "text"` blocks from assistant events are captured into `_all_assistant_text` | Also capture text from `tool_use` `input.content` fields (Write/Edit tool content) into `_all_assistant_text` so Output Receipts embedded in deposit files are parsed | Modify `runner.py` text collection loop |
| **G2: Defense WARN reads wrong dict** | `bellows.py:1138` — `parsed.get("_all_assistant_text", "")` is always `""` | Either propagate `_all_assistant_text` through `parsed` dict, or pass `raw["_all_assistant_text"]` separately to `_apply_ledger_updates` | Modify `parser.py` return or `bellows.py` call site |
| **G3: Defense WARN cannot detect tool-content-only emission** | `bellows.py:1140` — checks `"### Ledger Updates" in _src` where `_src` never includes tool content | After G1 fix, `_all_assistant_text` would include tool content, making this gap auto-resolved | Resolved by G1 |
| **G4: No contract enforcing Output Receipt as bare text** | Agent specialist files instruct "include at the end of every response" but enforcement is behavioral | Consider adding a post-step check: if deposit file contains `### Ledger Updates` but assistant text does not, WARN | Optional defense-in-depth |

### Verification Blocks

```
Claim: The agent never emitted ### Ledger Updates as bare assistant text
Query: grep -c '### Ledger Updates' across all 3 assistant text blocks from plan-57 NDJSON
Expected: 0

Claim: forward extraction returned None
Query: parsed["ledger_updates"]["forward"] from 20260614-160153-step.json
Expected: None

Claim: The clean block exists only in Write tool content
Query: Count ### Ledger Updates in NDJSON event 16 (assistant, tool_use: Write) input.content
Expected: 2 (1 inline reference + 1 clean block in Output Receipt)

Claim: defense WARN _all_assistant_text key is absent from parsed dict
Query: "_all_assistant_text" in parsed for any logged step
Expected: False (key never present in parser.parse() return dict, see parser.py:85–98)
```

### CEO Decision Forks

**1. Extraction fix shape (G1):**
- **Option A (recommended): Expand `_all_assistant_text` to include Write/Edit tool content.** In `runner.py:232–234`, also capture `input.content` from `tool_use` blocks where `name` is `Write` or `Edit`. This ensures Output Receipts embedded in deposit files are parsed. Low risk — the parser's subsection regexes are specific enough to avoid false positives from file content.
- **Option B: Match the LAST `### Ledger Updates` instead of the first.** Would help only if the heading appeared multiple times in assistant text with the last being genuine. Does NOT fix plan 57's failure (heading was never in assistant text at all).
- **Option C: Require agents to emit Output Receipt as bare text.** Relies on behavioral compliance — fragile, as plan 57 demonstrated.

**2. Defense-WARN fix (G2):**
- Propagate `_all_assistant_text` from `raw` through `parsed` (add it to `parser.parse()` return dict), OR pass the raw `_all_text` as a separate argument to `_apply_ledger_updates`. Low-effort fix.

**3. Re-canary:**
- A cleaner canary (whose prompt does NOT literally echo `### Ledger Updates` / `#### Forward Register` headings in backtick-quoted instructions) would reduce noise but would NOT have prevented this failure — the root cause is agent emission placement, not prompt echo pollution. A re-canary AFTER the G1 fix would be the right validation.

**4. Feedback/PROJECT_STATUS latent risk:**
- **YES — at latent risk from the same issue.** Any agent that embeds the Output Receipt solely inside a deposit file write (without repeating as bare text) will silently drop feedback and project_status. Plan 55 happened to emit bare text; there is no enforcement mechanism. G1 fix resolves this for all channels.

---

## Output Receipt
**Agent:** Bellows Systems Analyst
**Step:** 1
**Status:** Complete

### What Was Done
Investigated plan-57 FORWARD canary extraction failure. Confirmed root cause: the agent emitted `### Ledger Updates > #### Forward Register` only inside a Write tool call (deposit file content), never as bare assistant text. The parser and runner correctly process only assistant text blocks — there was nothing to extract. The leading hypothesis (parser grabs first/echo `### Ledger Updates`) is killed. Identified defense-WARN gap: `_all_assistant_text` key is never in `parsed` dict, and the WARN cannot detect tool-content-only emission.

### Files Deposited
- `knowledge/research/forward-extraction-failure-rootcause-2026-06-14.md` — complete root cause analysis with 5 sections

### Files Created or Modified (Code)
- None (investigation only)

### Decisions Made
- Classified root cause as (b) AGENT EMISSION + (c) CANARY-DESIGN artifact, not parser fragility
- Killed the leading hypothesis (prompt-echo section match)
- Assessed all three ledger channels (feedback, project_status, forward) as latently at risk

### Flags for CEO
- G1 (extraction fix) and G2 (defense-WARN fix) should be scheduled — both are low-effort, high-impact
- Real plans are at risk (not just canaries) — any agent that writes Output Receipt only in deposit file will silently drop ledger updates
- Recommend G1 fix + re-canary rather than relying on agent behavioral compliance

### Flags for Next Step
- None

### Ledger Updates

#### Prompt Feedback
The FORWARD canary (plan 57) exposed that the daemon's ledger extraction pipeline has a blind spot: Output Receipts embedded inside Write tool content (deposit files) are invisible to the parser because runner.py only captures `text` blocks from assistant events. This is not a parser bug — it is a runner collection gap. Plan 55 succeeded because the agent happened to duplicate the receipt as bare text; plan 57 failed because the agent placed it only in the deposit file. The defense-WARN at bellows.py:1138 compounds the issue: it reads `_all_assistant_text` from parsed (where the key never exists), silencing the safety net. Both the collection gap and the WARN gap should be fixed before the next FORWARD canary attempt.
