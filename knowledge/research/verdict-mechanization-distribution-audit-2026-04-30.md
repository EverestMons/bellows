# Verdict Mechanization Distribution Audit — Findings

**Date:** 2026-04-30
**Agent:** Bellows Systems Analyst
**Plan:** diagnostic-verdict-mechanization-distribution-audit-2026-04-30
**Step:** 1

## Executive Summary

**Recommendation: Don't mechanize. Close the BACKLOG verdict mechanization entry.** The ledger data (56 entries, 2026-04-16 to 2026-04-28) shows 63% of all verdicts are clean passes, but the dominant friction source is spurious gate failures (34%), not routine Planner verification. Gate precision fixes shipped 2026-04-28 already address the spurious-failure class. The remaining `auto_close_disabled` pauses (20 entries, 36% of total) are low-friction by nature — Planner verifies in seconds — and mechanizing them would introduce a new failure mode (silent false-positive auto-resolution) for marginal time savings (~7-15 min/day). None of the three mechanization scopes justify the Layer 1 architectural complexity.

---

## Phase 1 — Distribution Audit

### Ledger Schema

The ledger (`verdicts/ledger.jsonl`) records resolution outcomes, not pause reasons. Fields per entry:

| Field | Type | Notes |
|---|---|---|
| `timestamp` | ISO datetime | Resolution time |
| `plan_path` | string | Full path to plan file at resolution time |
| `step` | int | Step number |
| `gate_failures` | array | Always `[]` in ledger (gate failure details are in verdict request files, not propagated to ledger) |
| `files_changed` | array | Files modified during step |
| `verdict` | string | `auto-close` \| `continue-to-done` \| `continue` \| `stop` |
| `reason` | string | For `auto-close`: boilerplate. For `continue-to-done`: boilerplate. For `continue`/`stop`: Planner's analysis text from the resolved verdict file |

**Critical schema gap:** The `Pause Reason Code` field exists in verdict REQUEST files (`verdicts/pending/`) but is NOT propagated to the ledger. The ledger records the resolution outcome (`verdict`), not the pause trigger (`pause_reason_code`). Pause reasons below are inferred from verdict type and reason text. This inference is reliable for `auto-close` (no pause), `continue-to-done` (all `auto_close_disabled`), and `continue` with gate failure language (all `gate_failure`), but ambiguous for `continue` without gate failure language (could be `qa_checkpoint` or `header_pause`).

**Recommendation for future:** Add `pause_reason_code` to the ledger schema in `verdict.py::log_to_ledger()` to enable direct distribution analysis without inference.

### Pause Reason Code Inference

| Verdict Type | Inferred Pause Reason | Basis |
|---|---|---|
| `auto-close` | N/A (no pause) | Plan had `auto_close: true`; no verdict request generated |
| `continue-to-done` | `auto_close_disabled` | Terminal step with all gates passing; Planner approved via Rule 22 |
| `continue` with gate failure in reason | `gate_failure` | Gate tripped; Planner overrode after investigation |
| `continue` without gate failure | `qa_checkpoint` | QA step or content checkpoint; Planner verified |
| `stop` | `qa_checkpoint` | Gates passed but Planner caught missing deliverables via Rule 22 |

### Distribution Table

| Pause Reason Code | Total | (i) Clean Pass | (ii) Real Finding | (iii) Spurious Gate | (iv) Genuine Failure | (?) Unclassified |
|---|---|---|---|---|---|---|
| N/A (auto-close) | 14 (25%) | 14 | 0 | 0 | 0 | 0 |
| auto_close_disabled | 20 (36%) | 20 | 0 | 0 | 0 | 0 |
| gate_failure | 19 (34%) | 0 | 0 | 19 | 0 | 0 |
| qa_checkpoint | 3 (5%) | 1 | 0 | 0 | 1 | 1 |
| agent_verdict_request | 0 | — | — | — | — | — |
| header_pause | 0 | — | — | — | — | — |
| **Total** | **56** | **35 (63%)** | **0 (0%)** | **19 (34%)** | **1 (2%)** | **1 (2%)** |

### Category-by-Category Narrative

#### (i) Clean Rule 22 pass — 35 entries (63%)

The dominant category. Composed of three sub-populations:

**Auto-close (14 entries):** Plans with `auto_close: true` (pre-2026-04-24 executables, or post-2026-04-24 plans with explicit header opt-in). All gates passed; Bellows moved to Done/ without generating a verdict request. These are already fully automated — mechanization would not affect them.

**Auto_close_disabled terminal step (20 entries):** Plans where all gates passed at the terminal step but auto_close was disabled (diagnostics throughout, all plans post-2026-04-24). Bellows posted a verdict request; Planner read it, verified Rule 22 (a)–(e), and approved. The ledger reason is always boilerplate (`"continue verdict on final step — moving to Done"`), indicating the Planner found nothing wrong in any of these 20 cases.

**qa_checkpoint clean pass (1 entry):** L14 (bellows-verdict-request-integration-test Step 1) — QA checkpoint, integration test passed, Planner verified and continued. Gates passed; Planner confirmed test results.

**Key observation:** Of the 35 clean passes, 14 (40%) are already automated via auto-close. The remaining 21 are the mechanization-eligible population.

#### (ii) Real Planner finding — 0 entries (0%)

**The Planner has never caught a substantive issue on a "continue" verdict that mechanical deposit-existence checks would have missed.** Every "continue" verdict in the ledger was approved because the work was correct — the Planner's analysis confirmed what the gates had already established (or overrode gate false positives where the work was also correct).

This 0% finding rate cuts both ways:
- **For mechanization:** It suggests the Planner's Rule 22 check adds no incremental detection value on continue verdicts.
- **Against mechanization:** The sample is small (56 entries, 14 days). A 0% finding rate across 42 paused verdicts gives a 95% confidence interval of [0%, 7%] — we cannot rule out a low-but-nonzero finding rate with this sample size.

#### (iii) Spurious gate failure — 19 entries (34%)

The second-largest category and the dominant source of verdict-cycle friction. Every entry was a gate false positive where the Planner investigated and overrode:

| Gate | Count | Root Cause | BACKLOG Status |
|---|---|---|---|
| scope_check | 11 | Monorepo git-diff over-scoping (BACKLOG #4), CRLF noise, Done-folder artifacts | Fixed 2026-04-28 (commit 8db0adc) |
| deposit_exists (Gate 5 backtick) | 4 | Leading backtick in path extraction | Fixed 2026-04-17 (commit 8d8a613) |
| no_permission_denials | 4 | Cross-project Grep/Glob tool denials on governance/ and PLANNER_TEMPLATE.md | Open (BACKLOG, no number) |

**Critical insight:** All 19 spurious entries trace to known gate bugs, not to a fundamentally broken verdict architecture. 15 of 19 (79%) are from bugs that have ALREADY been fixed. The remaining 4 (`no_permission_denials` cross-project denials) are tracked in BACKLOG as a gate precision issue.

**Post-fix prediction:** With scope_check monorepo fix and deposit_exists backtick fix shipped, the spurious gate failure rate should drop from 34% to approximately 7% (the no_permission_denials cluster only). This shifts the distribution substantially toward clean passes.

#### (iv) Genuine gate failure — 1 entry (2%)

L10 (forge-retrieval-fix Step 2, 2026-04-16): `"Rule 22 FAILED. Gates reported Step 2 passed but zero deliverables exist on disk."` The agent ran but produced nothing — no QA report, no evidence, no code changes. Gates passed (all mechanical checks clean because there was nothing TO flag). The Planner caught it via Rule 22 content verification: the plan declared specific deliverables, none existed.

This is the safety-net case for Planner-in-the-loop: gates passed, deposits didn't exist (but the deposit_exists gate apparently didn't catch this — possibly because the plan pre-dated the deposit_exists gate or the deposit path wasn't declared in a parseable format). Only the Planner's manual Rule 22 check caught the failure.

**Relevance to mechanization:** Scope (a) (deposit existence check on resolution side) WOULD have caught this case — `os.path.exists()` would have returned False on the missing deliverables. But this was a `qa_checkpoint` pause, not `auto_close_disabled`, so scope (a) would not have been applied to this entry. The safety net held because the pause reason routed to Planner regardless.

#### (?) Unclassified — 1 entry (2%)

L28 (invoice-pulse tabbed-import-card-sweep-v3 Step 2, 2026-04-17): `"Dev log deposited manually by Planner."` The Planner created the dev log itself rather than finding it deposited by the agent. The code work was verified correct (prompt splits confirmed, commit confirmed). Borderline between (i) clean pass (work was fine) and (ii) real finding (agent didn't deposit its dev log). Classified as (?) because the intervention was Planner depositing a missing artifact, not catching a work-quality issue.

### Supplementary Data: Verdict-Log.md

The Planner-side verdict-log.md (6 entries, 2026-04-24 to 2026-04-30) provides higher-fidelity data with explicit `Pause Reason` and `Gates Failed` columns. All 6 entries resolved as "clean close" — 3 with gate_failure overrides (all no_permission_denials or deposit_exists false positives), 1 manual bootstrap, 2 clean passes. This confirms the ledger pattern: real Planner findings remain at 0%.

---

## Phase 2 — Scope Analysis

### Scope (a) — Deposit existence only

**Mechanism:** After all gates pass on a terminal step with `auto_close_disabled`, Bellows runs `os.path.exists()` (file or directory) on every path declared in the step's `**Deposits:**` block. If all exist → auto-close to Done without posting a verdict request. If any missing → post verdict request for Planner review.

**Fraction of Phase 1 distribution handled:**
- Handles 20 of 20 `auto_close_disabled` entries (100% of that bucket)
- Cannot handle `gate_failure` (gate already failed — auto-resolution can't override a tripped gate)
- Cannot handle `qa_checkpoint` (intentional content review checkpoint)
- Net: 20/56 = 36% of total, 20/42 = 48% of paused verdicts
- Of the (i)-bucket (35 entries): 20/35 = 57% (the other 14 are already auto-closed, 1 is qa_checkpoint)

**LOC estimate:** 30–50 lines

**Module changes:**
- `bellows.py` (lines 377–393, terminal-step pause path): Insert deposit-existence check before posting verdict request. If `not effective_auto_close` AND `gate_result["passed"]` AND `not gate_result["is_qa_step"]`, extract deposit paths from plan text and check `os.path.exists()` on each. If all exist → log to ledger as `"auto-resolved"` and proceed to Done/. If any missing → fall through to existing verdict-request posting.
- `verdict.py`: Reuse existing `extract_primary_deposit()` for single-deposit extraction; need a new `extract_all_deposits()` variant that returns ALL paths from the `**Deposits:**` block (current function returns only the first `.md` path).
- `gates.py`: No changes. `_extract_plan_required_deposits()` already does multi-path extraction and could be reused, but it's in gates.py and the verdict.py duplicate should be the canonical source.

**New failure modes:**
1. **Silent false-positive auto-resolution:** Deposit file exists but is empty, truncated, or wrong content. Agent creates the file path but crashes before writing content. Bellows auto-closes; CEO never sees the verdict request. Detection: only if downstream consumer notices missing content.
2. **Race condition at check time:** Deposit written by agent but git commit not yet flushed (file exists but isn't committed). Low risk since `os.path.exists()` checks the filesystem, not git.
3. **Directory ambiguity:** `os.path.exists()` returns True for directories. If a deposit path is `bellows/knowledge/research/` (a directory), the check passes vacuously. Mitigated by requiring `.md` extension in deposit paths, which the `BLOCK_BULLET_RE` regex already enforces.
4. **Desync with gates:** The deposit_exists GATE checks deposits during gate evaluation (pre-pause). The auto-resolver checks deposits during resolution (post-pause). If deposits are created between gate evaluation and resolution (unlikely for terminal steps, since no agent runs between them), the checks could diverge.

### Scope (b) — Deposit existence + non-empty + Rule 20 self-check stdout grep

**Mechanism:** All of scope (a), plus: (1) verify `os.path.getsize(path) > 0` for each deposit, (2) if the step is QA, locate the QA report file and grep for the literal string `PASSED — SELF-CHECK PASSED` (Rule 20's stdout).

**Fraction handled:**
- Same 20 `auto_close_disabled` entries as scope (a) (non-empty adds no new coverage — all 20 had real, non-empty deposits)
- Plus potentially 1 `qa_checkpoint` clean pass (L14, integration test) if the self-check string was present
- Net: 21/56 = 38% of total, 21/42 = 50% of paused verdicts
- Marginal gain over (a): +1 entry

**LOC estimate:** 60–80 lines

**Module changes:** Same as (a), plus:
- QA report file locator (need to resolve path from plan metadata — not currently standardized)
- Stdout grep logic in `bellows.py`

**New failure modes (in addition to scope (a)'s):**
1. **Self-check format drift:** Rule 20's self-check output format is defined in PLANNER_TEMPLATE. If a future Rule revision changes the literal string, Bellows's grep silently fails → false negative (safe but causes unnecessary Planner involvement). Requires Bellows code update every time PLANNER_TEMPLATE changes — tight coupling between Layer 1 infrastructure and Layer 3 governance.
2. **Agent fakes self-check output:** An agent could write `PASSED — SELF-CHECK PASSED` in its stdout without actually running the self-check script. Bellows would auto-resolve. Risk is low (agents don't intentionally deceive) but non-zero for malformed agents that echo template strings.
3. **Content interpretation in Layer 1:** Bellows is now reading agent output for semantic meaning (the self-check string). This crosses the Layer 1 mechanical-only invariant documented in PLANNER_TEMPLATE v4.29 line 804.
4. **QA report path resolution:** QA reports don't have a standardized path convention across projects. Bellows would need a resolver that handles `knowledge/qa/*.md`, `knowledge/research/*.md`, and potentially project-specific patterns.

### Scope (c) — Full Rule 22 (a)–(e) automation

**Mechanism:** Bellows reproduces all five Planner Rule 22 checks: (a) deposit exists and is non-empty, (b) content aligns with plan objective, (c) Output Receipt matches actual stdout, (d) no hedging keywords in positive-status claims, (e) self-check passed (QA steps only).

**Fraction handled:**
- Theoretically: all 35 (i)-bucket entries (63% of total)
- Practically: 21/42 = 50% of paused verdicts — same as (b), because `gate_failure` entries need gate fixes, not resolution automation, and `qa_checkpoint` entries are intentional content review
- Marginal gain over (b): 0 entries

**LOC estimate:** 200–400 lines

**Module changes:**
- New `rule22.py` module with five sub-check functions
- `bellows.py` integration at terminal-step pause path
- `verdict.py` deposit extraction extensions
- Possibly `gates.py` for plan-objective extraction

**Architectural risks:**
1. **Breaks Layer 1 mechanical-only invariant.** PLANNER_TEMPLATE v4.29 explicitly documents Bellows as Layer 1 infrastructure: "Bellows dispatches and gates; the Planner judges." Content alignment (b) and hedging detection (d) are judgment operations. Moving them into Bellows means Layer 1 is now making Layer 3 decisions.
2. **Divergence between two Rule 22 implementations.** The Planner's Rule 22 evolves with each PLANNER_TEMPLATE revision (v4.24 → v4.29 in 12 days). A Bellows-side Rule 22 would need to track every revision. When the two implementations disagree, which is authoritative? This creates a governance ambiguity that doesn't exist today.
3. **Hedging detection is context-dependent.** "May" in "this may require further work" is hedging. "May" in "May 2026" is a date. "Partial" in "partial completion" is hedging. "Partial" in "partial match scoring" is domain terminology. Layer 1 should not make these distinctions.
4. **Content alignment requires plan-objective understanding.** Checking whether a deposit's content aligns with a plan step's objective requires reading both, extracting semantic intent, and comparing. This is fundamentally a judgment operation.
5. **Testing surface area.** Each Rule 22 sub-check needs comprehensive positive/negative test cases. The Planner's Rule 22 is implicitly validated by production; Bellows's would need explicit coverage. At 200-400 LOC, the test suite would be 400-800 LOC.

---

## Phase 3 — Recommendation

### Decision: Don't mechanize. Close the BACKLOG verdict mechanization entry.

### Reasoning Chain

1. **(i)-bucket is 63% (35/56) of all verdicts.** This is large — a majority of verdicts are routine clean passes.

2. **But 14 of 35 clean passes (40%) are already auto-closed.** These generate no verdict request and no Planner involvement. Mechanization cannot improve them further.

3. **The remaining 21 clean-pass verdicts (38% of total) are the mechanization-eligible population.** These are `auto_close_disabled` terminal-step pauses (20) and `qa_checkpoint` clean passes (1).

4. **Scope (a) handles 20 of 21 mechanization-eligible verdicts (95%)** at 30–50 LOC. This is the most cost-effective scope.

5. **However, `auto_close_disabled` pauses are the lowest-friction verdict class.** The Planner already auto-approves these quickly — they are terminal-step verifications with no gate failures and all deposits present. CEO overhead per verdict: notification → Planner invocation → Rule 22 check (~2-5 minutes). At ~1.4 verdicts/day (20 over 14 days), mechanization saves approximately **3-7 minutes of CEO attention per day.**

6. **The highest-friction class is `gate_failure` (34% of all verdicts, 45% of paused verdicts).** All 19 gate_failure entries were spurious — the Planner had to investigate each one, write detailed override analysis, and manually approve. This is where CEO time is actually spent. Mechanization does NOT address this class. The fix is gate precision, and these fixes have already shipped (BACKLOG #1 deposit_exists prose paths, #4 scope_check monorepo, #5 deposits block regex, Gate 5 backtick — all closed 2026-04-28 or earlier).

7. **Post-gate-fixes, the predicted steady-state distribution shifts substantially.**
   - Spurious gate failures drop from 34% to ~7% (remaining `no_permission_denials` cross-project cases)
   - More verdicts resolve as auto-close or clean `auto_close_disabled` pauses
   - The verdict cycle becomes lower-friction without any mechanization

8. **The 0% real-Planner-finding rate does not justify removing the safety net.** The one genuine failure in the dataset (L10, forge-retrieval-fix Step 2) was caught exclusively by the Planner — gates passed, the agent produced nothing, and only Rule 22 manual verification detected it. Scope (a) would not have auto-resolved that case (it was `qa_checkpoint`, not `auto_close_disabled`), but the 0% finding rate across 20 `auto_close_disabled` entries gives only a 95% CI of [0%, 14%]. The sample is insufficient to conclude the safety net is unnecessary.

9. **Scope (a) introduces a new failure mode class (silent false-positive auto-resolution) for marginal time savings.** A deposit file that exists but is empty, truncated, or contains wrong content would be auto-resolved without Planner review. The risk is low but non-zero, and the consequence (a broken plan marked Complete in Done/) is hard to detect after the fact.

10. **Scope (b) adds +1 entry coverage over (a) at 2x LOC and introduces content interpretation in Layer 1.** Not justified by the data.

11. **Scope (c) breaks the Layer 1 mechanical-only invariant for zero additional coverage beyond (b).** Architecturally unacceptable per PLANNER_TEMPLATE v4.29.

12. **Net assessment:** The friction originally motivating BACKLOG verdict mechanization ("Rule 22 verification requires Planner involvement for every verdict-pending transition") has been substantially addressed by three independent improvements already shipped:
    - Gate precision fixes eliminated 79% of the spurious failure overhead (15 of 19 entries)
    - Disable-auto-close + Rule 25 polling created a clean Planner-driven terminal-step flow
    - Verdict-log.md provides an observation surface for future pattern detection

    Mechanization would optimize the remaining low-friction slice at the cost of Layer 1 architectural complexity. The correct action is to close the BACKLOG entry.

### Revisit Trigger

Revisit mechanization if:
- Paused verdict volume exceeds 5/day sustained (current: ~1.4/day for `auto_close_disabled`)
- A new verdict class emerges that is routine AND high-friction AND mechanical
- The Planner's Rule 22 check consistently takes >5 minutes per verdict (current: ~30 seconds for clean passes)

---

## Interaction with Rule 26 Parser / Gate Gap

The deposit_exists gate gap that motivated this analysis has two components, both now resolved:

1. **BACKLOG #1 (deposit_exists prose-path false positive):** `_extract_plan_required_deposits()` scanned full plan text for deposit-like paths, tripping on prose directory references. Fixed 2026-04-19 by scoping extraction to the declared `**Deposits:**` block. Confirmed live via canary 2026-04-28.

2. **BACKLOG #5 (deposits block regex blank-line bug):** `DEPOSITS_BLOCK_RE` failed to match when blank `>` lines separated the `**Deposits:**` header from the first bullet. Fixed 2026-04-28 (commits fbb0aeb + 6bedb82). Verified via 7-case empirical validation.

**Interaction with mechanization scopes:**

If scope (a) were built, it would **compose with** these fixes, not subsume them:
- Gate-side: `deposit_exists` gate now correctly extracts deposit paths from the `**Deposits:**` block → gate passes clean for correctly-authored plans
- Resolution-side (hypothetical scope (a)): `os.path.exists()` confirms deposits exist → auto-resolve

The two checks are complementary (gate checks at evaluation time, auto-resolver checks at resolution time). But since the gate-side fixes already ensure clean gates for correctly-authored plans, the resolution-side check provides marginal additional confidence. The primary residual value of the Planner-in-the-loop is Rule 22 (b)–(e) — content alignment, Output Receipt consistency, hedging detection, self-check verification — which scope (a) does not attempt.

**The gate fixes are the higher-leverage improvement.** They prevent false verdicts from being generated in the first place, whereas mechanization only reduces the resolution cost of verdicts that do get generated. Fix the source (gate precision), not the symptom (resolution latency).

---

## Output Receipt
**Agent:** Bellows Systems Analyst
**Step:** 1
**Status:** Complete

### What Was Done
Full distribution audit of 56 ledger entries across 5 pause reason codes, with (i)–(iv) classification and cross-reference to BACKLOG closed entries. Scope analysis for three mechanization tiers with LOC estimates, module identification, and failure-mode enumeration. Recommendation: don't mechanize, close the BACKLOG entry.

### Files Deposited
- `bellows/knowledge/research/verdict-mechanization-distribution-audit-2026-04-30.md` — findings, distribution table, scope analysis, recommendation

### Files Created or Modified (Code)
- None (diagnostic only)

### Decisions Made
- Recommended closing the BACKLOG verdict mechanization entry as not-worth-doing given the current distribution data and post-gate-fix steady-state prediction

### Flags for CEO
- None

### Flags for Next Step
- None (single-step diagnostic)
