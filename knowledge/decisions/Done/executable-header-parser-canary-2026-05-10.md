# Canary — Multi-Line Bold Header Parser Live Verification

**Project:** bellows

**Date:** 2026-05-10

**Author:** Planner

**Tier:** Trivial

**Total Steps:** 2

**pause_for_verdict:** after_step_1

---

## Context

Live smoke test of the multi-line bold header parser fix shipped at commit `491aab9`. The daemon was restarted to load the new parser code. This canary verifies the parser fix works end-to-end in production, not just in unit tests.

**The header above is deliberately multi-line bold** — each `**Key:** value` field on its own line, separated by blank lines. Under pre-fix code, this would have caused Bellows to log `"has 2 steps but no pause_for_verdict header — Bellows will auto-advance"` and skip the Step 1 pause. Under post-fix code, the parser should read all six header fields including `pause_for_verdict: after_step_1`, and Bellows should pause cleanly with `pause_reason_code: header_pause` after Step 1.

This canary is intentionally minimal. The work itself is trivial (write and read a marker file). The point is to verify Bellows's dispatch behavior, not the agent's capability.

**Expected dispatch-log observations:**

1. `Bellows: plan has 2 steps` (correct count — no `## STEP N` patterns in fenced code blocks this time).
2. **No** "no pause_for_verdict header" warning.
3. **No** "sparse header" defensive-default warning (header has 6 keys, well above the < 3 threshold).
4. Step 1 pauses with `Pause Reason Code: header_pause`, not `auto_close_disabled`.

If all four hold, the fix is verified live.

---

## STEP 1 — Marker file deposit

**Agent:** Bellows Developer (`bellows/agents/BELLOWS_DEVELOPER.md`)

**Working directory:** `/Users/marklehn/Desktop/GitHub/bellows/`

**Deposits:**
- `bellows/knowledge/qa/evidence/header-parser-canary-2026-05-10/marker.txt` (created)

### Prompt

You are the Bellows Developer. This is a minimal smoke test.

Single action: create the file `bellows/knowledge/qa/evidence/header-parser-canary-2026-05-10/marker.txt` containing the text `step 1 marker` followed by the current ISO timestamp on a new line. Create the parent directory if needed.

That is the entire task. No other work, no other files touched, no commit. Output the receipt and stop.

### Output Receipt

```
**Step:** 1
**Status:** Complete
**Deposits:**
- bellows/knowledge/qa/evidence/header-parser-canary-2026-05-10/marker.txt (created)
```

STOP after Step 1.

---

## STEP 2 — Read-and-confirm

**Agent:** Bellows Developer (`bellows/agents/BELLOWS_DEVELOPER.md`)

**Working directory:** `/Users/marklehn/Desktop/GitHub/bellows/`

**Deposits:**
- `bellows/knowledge/qa/evidence/header-parser-canary-2026-05-10/step2-confirm.txt` (created)

### Prompt

You are the Bellows Developer. Continue the smoke test.

Single action: read `bellows/knowledge/qa/evidence/header-parser-canary-2026-05-10/marker.txt`, then write `bellows/knowledge/qa/evidence/header-parser-canary-2026-05-10/step2-confirm.txt` containing the line `step 2 confirms step 1 marker exists with content:` followed by the literal content of the marker file.

That is the entire task. No commit. Output the receipt and stop.

### Output Receipt

```
**Step:** 2
**Status:** Complete
**Deposits:**
- bellows/knowledge/qa/evidence/header-parser-canary-2026-05-10/step2-confirm.txt (created)
```

STOP after Step 2.

---

## Deliverables Summary

| Step | Agent | Deliverable | Location |
|------|-------|-------------|----------|
| 1 | DEV | `marker.txt` | `bellows/knowledge/qa/evidence/header-parser-canary-2026-05-10/` |
| 2 | DEV | `step2-confirm.txt` | `bellows/knowledge/qa/evidence/header-parser-canary-2026-05-10/` |
