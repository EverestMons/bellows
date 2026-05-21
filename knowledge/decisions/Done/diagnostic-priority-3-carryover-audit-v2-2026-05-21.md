# Bellows — Priority 3 Carry-Over Audit Diagnostic
**Date:** 2026-05-21 | **Tier:** Small | **Dispatch Mode:** bellows | **Test Scope:** none | **Execution:** Step 1 (Bellows Systems Analyst) | **pause_for_verdict:** after_step_1
**Priority:** 3
**Depends on:** none

## Context

The bellows `NEXT_SESSION.md` Priority 3 lists five carry-over items from the 2026-05-19 baton that have survived two session handoffs without scoping:

1. **stale-redirect grep audit** — 2026-05-19 baton Priority 1; named but never executed
2. **`pause_for_verdict` single-enum** — one-line label, no description
3. **verdict prose directive unactionable** — one-line label, no description
4. **Deposits parenthetical qualifiers** — one-line label, no description
5. **stale verdict step warning rate-limit** — one-line label, no description

The originating 2026-05-19 baton is no longer on disk. No diagnostic file, BACKLOG.md entry, or commit message references any of the five phrases. NEXT_SESSION.md itself says "none blocking" and asks: promote to BACKLOG or decline.

The Planner is unwilling to decline-without-evidence on items that survived two session carries — that throws away signal. This diagnostic asks the SA to determine, for each item, what it most plausibly refers to in current Bellows code/governance and whether the underlying concern (if it can be located) still exists or has been superseded.

This is read-only. No edits. No commits. Output is a conversation report with one of three dispositions per item:

- **STALE** — the concern has been superseded by a shipped change, or no plausible referent exists in current code. Recommend close without BACKLOG entry.
- **LIVE-MINOR** — referent located, defect or gap still present, but low severity / cosmetic. Recommend BACKLOG entry with reproduction notes.
- **LIVE-LOAD-BEARING** — referent located, real defect with operational impact. Recommend escalation to a fix executable.

The SA has latitude to declare a sixth disposition — **UNRESOLVABLE** — if no plausible referent can be located after good-faith search. That's also a valid outcome and corresponds to "decline" in NEXT_SESSION.md's framing.

---
---

## STEP 1 — Bellows Systems Analyst

---

Specialist: `bellows/agents/BELLOWS_SYSTEMS_ANALYST.md`. Working directory: `/Users/marklehn/Developer/GitHub/bellows/`.

For each of the five items below, perform the indicated lookups and report findings. Do NOT propose fixes; that's the Planner's call after reading findings. For each item, conclude with one of the four dispositions: STALE, LIVE-MINOR, LIVE-LOAD-BEARING, or UNRESOLVABLE.

### Item 1 — stale-redirect grep audit

**Plausible referent:** "Stale redirect" likely refers to either (a) HTTP-style redirect handling in Bellows (unlikely — Bellows has no HTTP layer), or (b) a code path that "redirects" plan flow when a stale state is detected (e.g., resume-step redirection, verdict file redirection, plan-handler dispatch redirection). The "grep audit" framing suggests the original intent was a grep-for-occurrences sweep, not a deep investigation.

**Lookups:**
- `grep -rn "stale" /Users/marklehn/Developer/GitHub/bellows --include="*.py" --include="*.md" -l` — enumerate files mentioning "stale" to identify the cluster the original entry likely targeted.
- For each file in the result, report the line numbers and surrounding context (3 lines) for occurrences of "redirect" near "stale" (same function, same comment block, or within 20 lines).
- Cross-check `bellows/knowledge/BACKLOG.md` Closed section for any prior "stale verdict redirect" or similar resolved entries that may have superseded this item.

**Disposition criteria:**
- STALE if all `stale`-related code paths have either been refactored away or are documented as intentional in BACKLOG/Done plans.
- LIVE-MINOR if a stale-redirect path exists but has no observed failure mode.
- LIVE-LOAD-BEARING if a stale-redirect path with documented or observed failure mode is found.
- UNRESOLVABLE if no plausible referent matches the phrase after good-faith search.

### Item 2 — `pause_for_verdict` single-enum

**Plausible referent:** `pause_for_verdict` is the header field in plan files that specifies when Bellows should pause for a Planner verdict. Possible values currently in use: `after_step_N`, `never`, and (per template language) any step-keyed expression. The phrase "single-enum" suggests either (a) the field accepts only one value at a time when it ought to accept multiple, (b) the enum is documented as having one valid value when it has more, or (c) the warning/validation message references a single enum when multiple are valid.

**Lookups:**
- `grep -rn "pause_for_verdict" /Users/marklehn/Developer/GitHub/bellows --include="*.py"` — find all parse, validate, and consumer sites.
- For each match, report 5 lines of surrounding context.
- `grep -n "pause_for_verdict" /Users/marklehn/Developer/GitHub/PLANNER_TEMPLATE.md` — find the governance-side documentation of accepted values.
- Compare the parser's accepted values against the template's documented values. Report any divergence.

**Disposition criteria:**
- STALE if parser, governance docs, and observed usage agree on the same enum set and validation messages are consistent.
- LIVE-MINOR if there is a documentation/validation message inconsistency without operational impact (e.g., warning text lists fewer values than the parser accepts).
- LIVE-LOAD-BEARING if the parser rejects a value the governance documentation explicitly authorizes, or accepts a value that should be rejected.
- UNRESOLVABLE if "single-enum" has no plausible mapping after the grep.

### Item 3 — verdict prose directive unactionable

**Plausible referent:** Verdict request files include prose directives ("Continue", "Stop", and per recent enrichment work, the new Rule 22 mechanical check table). "Unactionable" likely means: the verdict request emits a prose instruction that the Planner cannot mechanically act on without manual interpretation. Candidates: ambiguous gate-failure text, free-form "Investigate further" directives, or directives that reference resources that don't exist by the time the Planner reads the file.

**Lookups:**
- Read `verdict.py` and identify the function(s) that compose verdict-request prose (likely `post_verdict_request` or `_format_verdict_request`).
- Report the names and line ranges of any helpers that emit free-form text (vs. fixed templates).
- `grep -n "directive\|instruction\|next step\|please" /Users/marklehn/Developer/GitHub/bellows/verdict.py` — surface any imperative prose.
- Sample three recent verdict-request files from `bellows/verdicts/resolved/` (any `processed-verdict-request-*.md` from the last week) and identify any directive lines that name an action the Planner cannot mechanically execute.

**Disposition criteria:**
- STALE if the 2026-05-21 verdict-enrichment plan (`Done/executable-bellows-verdict-enrichment-2026-05-21.md`) replaced free-form prose with structured tables/fields.
- LIVE-MINOR if free-form prose remains but doesn't cause operational friction.
- LIVE-LOAD-BEARING if free-form prose contains directives that have produced Planner misinterpretation incidents documented in LESSONS or PROJECT_STATUS.
- UNRESOLVABLE if no plausible directive-emitting code path can be located.

### Item 4 — Deposits parenthetical qualifiers

**Plausible referent:** The Rule 26 `**Deposits:**` block accepts bullet-form path declarations. "Parenthetical qualifiers" likely refers to parenthetical annotations after a path, e.g., `**Deposits:**\n- knowledge/qa/foo.md (created by QA agent)` or `- knowledge/research/bar.md (if applicable)`. The concern is probably that the parser either captures the parenthetical as part of the path (making the path unresolvable) or silently drops conditional qualifiers (making "if applicable" deposits indistinguishable from required ones).

**Lookups:**
- Read `gates.py` `_gate_deposit_exists` and `_extract_plan_required_deposits` and `_resolve_deposit_path`.
- Identify any regex that strips or preserves parenthetical content from a deposit bullet.
- Construct one or two synthetic test inputs:
  - `- knowledge/research/findings.md (volunteered)`
  - `- knowledge/qa/results.md (created by QA agent on completion)`
- Run them through the parser via a small Python REPL invocation (no test file commits) and report whether the path resolves correctly.
- Cross-check `PLANNER_TEMPLATE.md` Rule 26 for any guidance on parenthetical content in deposit bullets.

**Disposition criteria:**
- STALE if parenthetical qualifiers are explicitly handled (either stripped before resolution or documented as forbidden in Rule 26).
- LIVE-MINOR if parentheticals cause silent capture but the failure mode is rare and produces a clear `deposit_exists` gate trip (recoverable via Rule 22 override).
- LIVE-LOAD-BEARING if parentheticals cause silent miscounting of required deposits (e.g., conditional deposits treated as mandatory, or vice versa).
- UNRESOLVABLE if no parser branch handles or fails on parentheticals after good-faith search.

### Item 5 — stale verdict step warning rate-limit

**Plausible referent:** Bellows emits warnings when verdict files are detected in unexpected states (wrong directory, wrong format, stale slug). The phrase "rate-limit" suggests the warning fires too often (e.g., every 30-second daemon tick) and floods the logs. NEXT_SESSION.md's Priority 2 already names a related but distinct issue ("Bellows expected-keys warning misleading on single-line headers"), so this is likely a separate warning.

**Lookups:**
- `grep -n "WARN\|stale" /Users/marklehn/Developer/GitHub/bellows/bellows.py` — surface warning emission sites.
- For each match, identify the calling loop and the firing frequency (one-shot, per-claim, per-heartbeat-tick, per-poll).
- Sample the last 200 lines of the most recent daemon log in `bellows/logs/terminal/` and count repeat occurrences of any single warning message. If the same warning repeats >5 times in a window <5 minutes, that's a candidate for rate-limiting.
- Report the warning text and repeat count.

**Disposition criteria:**
- STALE if no warning emission site fires more than once per claim and log inspection shows no flooding.
- LIVE-MINOR if a warning fires repeatedly but is informational and does not obscure other logging.
- LIVE-LOAD-BEARING if a warning fires often enough to obscure real events or fills the log faster than the 14-day retention can absorb.
- UNRESOLVABLE if no warning emission site plausibly matches the phrase.

### Output format

For each of the five items, output the following block. Be precise — name files, line numbers, function names, and exact warning text where applicable. Do not paraphrase findings — report what the lookups returned.

```
## Item N — [item name]

**Lookups performed:**
- [command/file/function inspected]
- [results — literal output, not summary, unless output exceeds 30 lines, in which case summarize and link to the file]

**Plausible referent identified:** YES / NO
**Referent location:** [file:lines, or "none found"]

**Current behavior:** [observed behavior of the referent in current code]

**Disposition:** STALE / LIVE-MINOR / LIVE-LOAD-BEARING / UNRESOLVABLE

**Reasoning:** [1-3 sentences explaining the disposition]

**Recommended next step:** [close / add BACKLOG entry with the following text: "..." / escalate to fix executable]
```

**Output Receipt** — Agent: Bellows Systems Analyst, Step: 1, **Status: Complete** if all five items received a disposition; **Blocked** if any lookup raised an exception that prevented disposition (file missing, grep returned malformed output, etc.). What Was Done: five-item disposition audit on Priority 3 carry-overs. Files Deposited: none (conversation-report diagnostic). Files Created or Modified: none. Decisions Made: per-item dispositions only — no fixes proposed. Flags for CEO: any LIVE-LOAD-BEARING disposition (would warrant a follow-up fix executable). Flags for Next Step: Planner reads the five-item output in conversation and decides per item whether to (a) close, (b) author a BACKLOG entry with the SA's recommended text, or (c) escalate to a fix executable.

**Deposits:**
- none

**STOP.** Do NOT proceed to any other work. This is a single-step diagnostic; the Planner consumes the output in conversation.
