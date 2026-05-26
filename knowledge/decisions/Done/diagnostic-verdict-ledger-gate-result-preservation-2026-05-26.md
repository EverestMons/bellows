# Verdict Ledger Gate-Result Preservation — Fix Shape Audit
**Date:** 2026-05-26 | **Tier:** Diagnostic | **Dispatch Mode:** bellows | **Test Scope:** targeted | **Execution:** Step 1 (SA) | **qa_steps:** | **pause_for_verdict:** after_step_1

## How to Run This Plan

Paste the bootstrap prompt into Claude Code. The agent reads the full plan file and executes Step 1 ONLY.

**Bootstrap:** `Read the plan at /Users/marklehn/Developer/GitHub/bellows/knowledge/decisions/diagnostic-verdict-ledger-gate-result-preservation-2026-05-26.md. Execute Step 1 ONLY. After completing Step 1, STOP and wait for my confirmation.`

## CEO Context

Today's `scope-check-text-mention-audit-2026-05-26.md` diagnostic surfaced a structural evidence-loss gap: `_consume_verdicts` at bellows.py:1226 creates a fresh empty `gate_result = {"failures": [], "files_changed": []}` for every verdict it processes, overwriting the real gate failure data that was captured at gate-evaluation time. The diagnostic recommended **Fix Shape E** — preserve the original `gate_result` in the verdict ledger — as a ~5-line fix.

That estimate assumed a reader for the verdict request file's `## Gate Failures` and `## Files Changed` sections already exists. It doesn't. Implementing Fix E requires choosing between distinct architectural shapes:

- **E.1 — Markdown parser at consumption.** Add a parser to `_consume_verdicts` that re-extracts `gate_result` from the verdict request file's markdown sections (reverse of `verdict.py:200-204` and `:239-242`). Adds a writer/reader coupling — both sides must stay in sync.
- **E.2 — Structured sidecar.** When the verdict request is posted, also write a `.gate_result.json` (or equivalent) alongside the markdown request. Consumption loads the sidecar directly. Adds a new artifact type to the verdict lifecycle.
- **E.3 — Write to ledger at post-time, not consume-time.** Write the gate_result to the ledger when the verdict request is posted (when the data is in memory), instead of (or in addition to) consumption time. Eliminates the parse/sidecar question entirely. May require ledger schema accommodation for upsert/merge.
- **Other.** SA may identify a fourth shape not enumerated here.

The decision affects ~5 lines vs ~25 lines vs ~15 lines, plus whether new artifacts are introduced to the verdict lifecycle. It is not a Planner call — it is an architecture call.

This is a single SA step. No DEV, no QA chain. Decision lands as a Flags-for-CEO entry; the Planner authors the DEV plan once the shape is chosen. Fix F (terminal log expansion at bellows.py:495) is trivial and will be bundled into the same DEV plan; the SA does NOT need to evaluate F.

---
---

## STEP 1 — Bellows Systems Analyst

---

> **FIRST — before doing anything else, claim this plan:** `import shutil; shutil.move("/Users/marklehn/Developer/GitHub/bellows/knowledge/decisions/diagnostic-verdict-ledger-gate-result-preservation-2026-05-26.md", "/Users/marklehn/Developer/GitHub/bellows/knowledge/decisions/in-progress-diagnostic-verdict-ledger-gate-result-preservation-2026-05-26.md")`.
>
> You are the Bellows Systems Analyst. Read your specialist file at `bellows/agents/BELLOWS_SYSTEMS_ANALYST.md` first. Skip the domain glossary read — this is an internal architecture audit, no domain interpretation required.
>
> **Task.** Determine the correct architectural shape for Fix E (preserve gate_result in verdict ledger). Three candidate shapes are enumerated in CEO Context (E.1 markdown parser, E.2 structured sidecar, E.3 write-at-post-time); evaluate each and identify any unenumerated alternative.
>
> **Inputs to read.** (1) `bellows/bellows.py` lines 1220–1300 (`_consume_verdicts` and the ledger write call site). (2) `bellows/bellows.py` — locate and read `log_to_ledger` definition and call sites. (3) `bellows/verdict.py` — the full `post_verdict_request` function and any helper that writes the verdict request file format. Pay specific attention to lines 200–204 and 239–242 (the `## Gate Failures` and `## Files Changed` writers). (4) `bellows/verdicts/ledger.jsonl` — read the most recent 3 entries to understand the existing schema. Do NOT modify it. (5) Today's prior diagnostic `bellows/knowledge/research/scope-check-text-mention-audit-2026-05-26.md` — Q2 and Q5 evidence sections specifically.
>
> **Q1 — Current ledger write flow trace.** Document the exact call path from gate failure to ledger entry. (a) Where does the `gate_result` originate (which function constructs it with real data)? (b) How does it get to `verdict.post_verdict_request` for the markdown render? (c) How does control flow reach `_consume_verdicts` and the empty-gate_result construction? (d) Where exactly is `log_to_ledger` called from `_consume_verdicts`, and what arguments does it receive? Quote line numbers for each anchor.
>
> **Q2 — Ledger schema and consumers.** (a) Read the last 3 ledger entries — what fields exist, what types? (b) Are there ANY consumers of the ledger today — Forge ingestion, dashboards, other Bellows code paths, tests? Run `grep -rn "ledger.jsonl\|log_to_ledger\|ledger_path" .` from the bellows project root and enumerate all read-side uses. (c) For each consumer, does it currently rely on `gate_failures` and `files_changed` being arrays (even empty)? Would populating those arrays break any consumer, or is it backward-compatible?
>
> **Q3 — Three-shape evaluation matrix.** For each of E.1 (markdown parser), E.2 (structured sidecar), E.3 (write-at-post-time), score:
> - **LOC estimate** — how many lines change in which files
> - **New artifacts** — does it introduce new filesystem artifacts to the verdict lifecycle (sidecars, schema changes)
> - **Reversibility** — if the fix has a bug in production, how disruptive is rollback
> - **Forge-readiness** — Forge will eventually ingest the ledger for pattern extraction; which shape produces cleaner data for that downstream consumer
> - **Coupling created** — does the shape introduce new dependencies between modules (writer/reader sync, schema migrations, etc.)
> - **Failure modes** — what new failure shapes does it introduce (parse errors, missing sidecars, duplicate ledger entries)
>
> Output as a table with one row per shape.
>
> **Q4 — Unenumerated alternatives.** Is there a fourth shape the CEO Context didn't enumerate? Examples to evaluate: (i) pass `gate_result` through call arguments end-to-end without intermediate file persistence, (ii) refactor `_consume_verdicts` to skip the ledger-write step and have a separate gate-time logger handle the ledger directly, (iii) preserve the verdict request file by NOT deleting it at bellows.py:1292-1293, then have the ledger reference it by path. If a fourth shape exists, add it to the Q3 matrix.
>
> **Q5 — Recommendation.** Recommend exactly ONE shape with a one-paragraph rationale. The rationale must tie to: (a) the failure mode being fixed (evidence destruction), (b) the highest-leverage downstream consumer (Forge ingestion or current triage), and (c) the LOC-to-robustness ratio. The recommendation must be implementable — not "redesign the verdict lifecycle." If the recommendation is contingent on a CEO call (e.g., "E.2 if we plan to add more sidecar artifacts; E.1 if we want to keep the lifecycle minimal"), state the contingency explicitly and recommend both branches.
>
> **Q6 — Implementation hand-off detail.** For the recommended shape, list the specific functions and line ranges that need to change. Provide concrete enough detail that a DEV plan can be authored without re-investigating. Format: `bellows.py:1226-1230 — replace gate_result construction with [shape-specific change]`.
>
> **Q7 — Verification block (Rule 39).** The load-bearing claim is the call-flow trace in Q1. Re-run the line-number anchors and confirm each `gate_result` reference matches the cited line. Quote the actual line content at each anchor.
>
> **Deposit.** `bellows/knowledge/research/verdict-ledger-gate-result-preservation-2026-05-26.md` containing Q1–Q7, a Decisions Made section recording the recommended shape, and Flags-for-CEO with the implementation hand-off detail. Do NOT author the fix plan itself — flag for the Planner.
>
> **Constraints.** Do NOT modify source code. Do NOT modify the ledger. This is a read-only investigation. Cite line numbers and quote evidence verbatim where possible.
>
> Standard prompt feedback protocol → `bellows/knowledge/research/agent-prompt-feedback.md`.
