# Bellows — BELLOWS_ROOT Worktree-Reachability Audit

**Date:** 2026-06-08 | **Tier:** Diagnostic | **Dispatch Mode:** bellows | **Test Scope:** n/a | **Execution:** Step 1 (SA) | **qa_steps:** | **pause_for_verdict:** always

## Context

BACKLOG (Added 2026-06-06) records four LATENT `BELLOWS_ROOT = Path(__file__).parent` instances — `bellows.py:23`, `planner.py:11`, `runner.py:20`, `verdict.py:13`. Under worktree execution `__file__` resolves into `.bellows-worktrees/<wt>/`, so `.parent` yields the worktree dir, not canonical bellows. This is the THIRD instance of worktree-root-confusion: the anvil `ANVIL_ROOT`/F8 fix (`executable-anvil-cycle-report-worktree-write-2026-06-05`) and the bellows `decisions.py` `GOVERNANCE_ROOT` fix this session (`load_phrases()` silently returned `[]` from a worktree) were the first two.

The four are **currently latent** because the daemon process runs from the canonical checkout — these roots are read in-daemon, not in worktree-executed agent code. The `decisions.py` instance surfaced ONLY because a test imports and runs `load_phrases()` from the QA worktree. The risk: any future code path reading a canonical-only resource (DB, logs, `config.json`, `.bellows-cache`, governance files) via `BELLOWS_ROOT` from a worktree context silently hits the wrong path.

**This diagnostic ships NO code.** BACKLOG mandates **AUDIT first — convert-with-proof, not blanket**: latent-correct code carries regression risk, so each instance must be proven worktree-reachable (or proven not) before any conversion. The deliverable is a per-instance reachability table plus a conversion spec a follow-on executable can mechanize. The fix shape is already known: adopt the `resolve_governance_root()` marker-walk-up helper introduced in `decisions.py` this session (or a sibling `resolve_bellows_root()`).

## STEP 1 — Systems Analyst reachability audit (SA)

> **FIRST — before doing anything else, claim this plan:** rename `diagnostic-bellows-root-worktree-reachability-audit-2026-06-08.md` to `in-progress-diagnostic-bellows-root-worktree-reachability-audit-2026-06-08.md` using `mv` in the worktree. **THEN, immediately and BEFORE any other reads or work: post a short visible message to chat (1-2 sentences) confirming you have claimed the plan and stating your immediate next action.** This is a liveness anchor — dense SA reading phases have hung past the inactivity threshold in prior sessions. **AFTER posting confirmation:** read `bellows/agents/BELLOWS_SYSTEMS_ANALYST.md` first, then read the files listed below.
>
> Acting as the Bellows Systems Analyst, produce a per-instance worktree-reachability audit for the four latent `BELLOWS_ROOT = Path(__file__).parent` declarations, so a follow-on executable can convert ONLY the instances proven reachable (or convert all proactively with the latent ones explicitly justified) without regressing latent-correct code. Ship no code.
>
> **Files to read (post a 1-line "Read X." acknowledgment after each):**
>
> 1. `bellows/agents/BELLOWS_SYSTEMS_ANALYST.md` — specialist scope.
> 2. `bellows/knowledge/BACKLOG.md` — re-read the full `Added 2026-06-06: __file__-relative root resolution breaks under worktree execution` entry. Note the four line refs, the "currently latent" reasoning, and the "convert-with-proof, not blanket" mandate.
> 3. `bellows/src/decisions.py` (or wherever `decisions.py` lives) — read the `resolve_governance_root()` marker-walk-up helper introduced this session IN FULL. This is the reference implementation to adopt: note the marker file it walks up to find, its failure behavior, and its return contract.
> 4. `bellows/bellows.py` — locate the `BELLOWS_ROOT = Path(__file__).parent` declaration (~line 23) and find EVERY read site of `BELLOWS_ROOT` in the file. For each, record what canonical-only resource it resolves (DB, logs, `config.json`, `.bellows-cache`, governance files, etc.).
> 5. `bellows/planner.py` (~line 11), `bellows/runner.py` (~line 20), `bellows/verdict.py` (~line 13) — same: locate each `BELLOWS_ROOT` declaration and enumerate every read site and the resource it resolves. (Verify actual line numbers; BACKLOG's refs are approximate.)
> 6. The bellows test suite (`test_*.py` across the package) — GROUND TRUTH for the only confirmed reachability vector. Find every test that imports any of these four modules AND triggers a `BELLOWS_ROOT`-derived read. The `decisions.py` instance surfaced exactly this way (4 red `test_decisions.py` tests run in the QA worktree). Map test -> module -> read site.
>
> **Post a 1-line "Drafting Section N." marker at the start of each section.**
>
> **Section 1 — Per-instance read-site inventory.** For each of the four files, a table: `module | BELLOWS_ROOT line | read site (file:line) | resource resolved | canonical-only? (Y/N)`. A read site whose resource is NOT canonical-only (e.g. a path that legitimately differs per-worktree) is not a defect — flag it as such.
>
> **Section 2 — Reachability proof per instance.** For each of the four modules, determine whether ANY execution path reads its `BELLOWS_ROOT` while `__file__` resolves inside `.bellows-worktrees/<wt>/`. Evaluate three vectors explicitly: (a) **daemon-process execution** — the daemon imports from the canonical checkout; not reachable. (b) **test execution from a worktree** — the confirmed `decisions.py` vector; does any test import this module and trigger a `BELLOWS_ROOT`-derived read when the suite runs inside a QA worktree? (c) **any agent/worktree-executed code path** that imports the module directly. Classify each instance: **REACHABLE** (a real worktree path reads a canonical-only resource via this root — convert), **LATENT-UNREACHABLE** (only the canonical daemon reads it; no worktree path — defer or convert-proactive), or **AMBIGUOUS** (state the dependency and a recommended default). Cite the specific code/test path for each classification — do not classify on intuition. The test is mechanical: is there an import-and-read chain reachable from worktree-executed code (including the test suite run in a QA worktree)?
>
> **Section 3 — Conversion spec.** For every instance NOT classified LATENT-UNREACHABLE, specify the exact helper adoption: the `resolve_bellows_root()` (or reuse of `resolve_governance_root()`) marker-walk-up, the marker file it anchors on, the per-file diff shape (what line replaces what), and the import change. For LATENT-UNREACHABLE instances, give an explicit recommendation — convert-proactively (BACKLOG's "before a third surfaces") vs leave-and-document — and justify against the regression-risk-on-latent-correct-code concern. State a default for any instance where the daemon-vs-worktree resolution would differ in value.
>
> **Section 4 — Follow-on executable shape.** Summarize: which instances the executable converts, the helper to introduce or reuse, the test surface (which existing tests need fixture updates; what NEGATIVE tests must be added proving the helper resolves canonical root when invoked from a worktree `__file__`), the LOC estimate split between production and tests, and pre-flight notes (e.g. the executable MUST add a test that fails under the old `Path(__file__).parent` and passes under the helper, for each converted instance).
>
> **Section 5 — Edge cases and open questions.** Cover at minimum: bellows-self mode (bellows as the target project — does the worktree split behave identically?); whether the marker file the helper walks to exists at canonical bellows root but NOT inside a worktree (the property the walk-up depends on — confirm it); whether any of the four roots is read at MODULE IMPORT time (not inside a function), which would change when the wrong path is captured; and anything the code read surfaces that the executable must preserve.
>
> **Deposits:**
> - `bellows/knowledge/research/bellows-root-worktree-reachability-audit-2026-06-08.md` — the full audit (Sections 1-5).
