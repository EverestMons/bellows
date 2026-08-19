# bellows — resolve_bellows_root() fallback creates stray lifecycle.db in watched projects
**Date:** 2026-08-19 | **Tier:** Small | **Dispatch Mode:** bellows | **cycle_tier:** T1 | **Test Scope:** none (read-only diagnostic; Q6 only DESIGNS a guard test for the downstream fix) | **Execution:** Step 1 (DIAG) | **Priority:** 1

**auto_close:** false
**pause_for_verdict:** after_step_1

## Context

0-byte `lifecycle.db` strays appear at the ROOT of bellows-watched projects: `invoice-pulse/lifecycle.db` (2026-08-18 20:13, since deleted) and `lessons-forge/lifecycle.db` (2026-07-16 08:12, still present) — a slow, month-spanning recurrence across projects, not a one-off.

**Root cause (Planner walk-0 finding, to be confirmed by this diagnostic):** `bellows_root.py:27–28` — `resolve_bellows_root()` walks up from its start looking for `config.json` (the canonical anchor; gitignored so worktrees walk PAST themselves to canonical bellows) and, when no ancestor has one, **silently `return start`**. There is no `config.json` anywhere in the `Developer/GitHub` tree except `bellows/config.json`, so any resolution whose start is rooted in a project tree falls back to that project → the four sites that build `…/lifecycle.db` from it (`lifecycle.py:21`, `reporting.py:67`, `status.py:233`, `dashboard.py:116`) then point at `<project>/lifecycle.db` (only those that connect WITHOUT an existence-check actually create the stray — `status.py` guards with `.exists()`). `bellows_root.py` was itself introduced by `1ecf898` ("worktree-safe resolve_bellows_root()"); this is a gap in that same fix, not a new regression.

**This is a read-only diagnostic.** It confirms the mechanism, pins the trigger as far as the logs allow, enumerates the resolution sites, and produces a Rule 27 Gap Assessment table an executable will implement WITHOUT re-verification (T-7). It changes no code and creates no files outside a scratch dir.

## Drafting Cycle
**Tier:** T1 — triggers fired: T-7 (fix executable will build on this diagnostic's Gap Assessment per Rule 27), T-8 (novel). No T-5/T-6 for a read-only diagnostic → no cold panel.
**Walk 0 (context pin):** target `bellows_root.py` sha `dfdc656f8afb`, last written by `1ecf898` (the worktree-safe fix that introduced this fallback). Five `resolve_bellows_root()` call sites measured: `dashboard.py:328`, `runner.py:23`, `lifecycle.py:21`, `status.py:232`, `reporting.py:67`; FOUR derive a `…/lifecycle.db` path (`lifecycle.py:21`, `reporting.py:67`, `status.py:233`, `dashboard.py:116`) — the stray creators are the subset that connect without an existence-check (`status.py` guards with `.exists()`). Recurrence measured: invoice-pulse (2026-08-18) + lessons-forge (2026-07-16, extant). Step JSON schema measured (`success/raw_output/stderr/parsed`) — **no `cwd`/command field**, so Q1 is bounded by what the logs actually record. Clone-diff: closest same-class `diagnostic-437` (structure-borrowed; no origin drift).
**Direction verdict (after walk 1):** **PROCEED** — the angle (confirm the fallback mechanism + enumerate sites + gap-assess a fix) is sound; no forcing finding (origin/mechanism/scope-premise all hold).
**Walks:** 5 (bar MET — walk 5 dry, zero findings, no restructuring fold).
- Weak spots (1.4):    w1 1 folded; w2 1 folded (F6); w3 dry; w4 dry; w5 dry.
- Destruction (2.4):   w1 1 folded; w2 dry; w3 dry; w4 dry; w5 dry.
- Vulnerabilities (3.1): w1 1 folded; w2 dry; w3 dry; w4 dry; w5 dry.
- Integration-record:  w1 1 folded; w2 2 folded (F9, F8); w3 dry; w4 dry; w5 dry.
- ACID (5.5):          w1 dry (1 record note); w2 1 folded (F7); w3 1 folded (F10); w4 1 folded (F11); w5 dry.
**Conflicts:** none.
**Origin split (diagnostic):** w2 3 of 4 pre-existing; w3 F10, w4 F11 fold-introduced (site-sweep gaps). Instruction trend 4→3→1→1→0, all distinct.
**§5 Conformance:** `plan_lint` run at shape-stability (walk 5) → **0 FAIL**. Warn-first residual (non-blocking): the test-scope WARN PERSISTS — `Test Scope: none` was added for clarity but the linter's heuristic still flags the literal word "test" in Q6 (which only DESIGNS the downstream fix's guard test); this diagnostic runs no tests, so the WARN is a benign false positive, not cleared. The no-Closing WARN cleared with this block. Deposit path relative (o2-class), worktree-runtime-proven.
**Closing:** full walk 5 dry — 0 findings, no restructuring fold; §5 conformance clean (0 FAIL); closing-record re-read run (this block), dry; cycle CLOSED. Deposit exactly once (pending CEO go).

---
---

## STEP 1 — BELLOWS INVESTIGATION AGENT

---

> **Identity:** You are investigating a bellows infrastructure defect. Read-only: change NO code; create NO files outside a scratch temp dir. Deposit findings to `knowledge/research/`.
>
> **Q1 — Pin the trigger as far as the logs allow (Lens 1.4 — "undetermined" is an acceptable answer, do NOT fabricate).** The two strays were created invoice-pulse `2026-08-18 20:13` and lessons-forge `2026-07-16 08:12`. The step JSON schema is `{success, raw_output, stderr, parsed}` — **there is no `cwd` or command field**, so you cannot read the working directory directly. Correlate each stray timestamp to the `logs/<ts>-step.json` nearest it and to the plan/step running then (cross-ref `lifecycle.db` steps table by `step_started_at`). **Use the 0-byte/no-tables state as evidence (walk 2 F6):** `init_lifecycle_db()` CREATEs tables, so an empty no-tables file implies a READ-path connect that failed before writing — favors `reporting.py:67` (`status.py:233` is ruled OUT as a creator: it guards with `.exists()` and returns, per Q2/F10; the import-time `lifecycle.py:21` init is unlikely since it would have created tables). **Keep a non-bellows origin as a live hypothesis:** an agent, test, or manual `sqlite3.connect("lifecycle.db")` run with a project cwd produces the identical empty file — do not tunnel on the bellows sites. If the logs cannot determine the trigger, say so and record what evidence WOULD be needed (e.g., adding a cwd field) — an honest "undetermined from current logs" is a valid finding.
>
> **Q2 — Enumerate every `resolve_bellows_root()` call site and classify each.** For all five (`dashboard.py:328`, `runner.py:23`, `lifecycle.py:21`, `status.py:232`, `reporting.py:67`): state what start it resolves from (`__file__` at import vs a passed `_start`), whether that start can ever be project-rooted, and whether it builds a filesystem path that gets written. **There are FOUR `…/lifecycle.db` builders (walk 3 F10): `lifecycle.py:21`, `reporting.py:67`, `status.py:233`, `dashboard.py:116`** — for each, classify whether it connects WITHOUT a prior `.exists()` guard (those are the actual stray creators; `status.py:233` checks existence and returns, so it likely does NOT create one). Produce a table with a "creates stray? y/n + why" column.
>
> **Q3 — The worktree variant (Lens 3.1 target environment).** Confirm the INTENDED case still works: bellows' OWN plans run in `bellows/.bellows-worktrees/<wt>/` where `config.json` is absent (gitignored), so the walk correctly continues UP to canonical `bellows/`. Distinguish this (works) from the FAILING case: a start rooted in a NON-bellows tree (a watched project) with no `config.json` in any ancestor → fallback to `start`. Name which environment each stray came from.
>
> **Q4 — Reproduce in SCRATCH (Lens 3.2 observe the effect; do NOT create a stray in any real project).** In a temp dir only: call `resolve_bellows_root(_start=<a fabricated project-rooted path>)`, show it returns the project path, then show that building `…/lifecycle.db` + `sqlite3.connect()` creates a 0-byte no-tables file. Assert the 0-byte file appears — observe the effect, not just the returned path. Clean up the temp dir.
>
> **Q5 — Gap Assessment (Rule 27 — mandatory table, exact columns).** `| Gap | Current State | Proposed State | Change Required |`. Cover: (a) `bellows_root.py:27–28` fallback; (b) any call site that should pass an explicit anchor. **Preserve the legitimate fallback the docstring cites (Lens 2.4):** the current `return start` exists FOR CI/fresh-clone with no `config.json` — the proposed fix (e.g., anchor on a TRACKED bellows sentinel like `bellows.py`, present in canonical AND worktrees; raise "not in a bellows tree" only when truly outside one) must NOT break fresh-clone resolution. State how the proposed state handles the CI/fresh-clone case. Reference `1ecf898`'s config.json-anchor intent (Lens 4) so the fix extends rather than reverts it. **The fix is justified independently of Q1 (walk 2 F7):** Q4 (the fallback demonstrably creates a stray) plus the measured cross-project recurrence establish the defect and authorize the fix even if the exact production trigger stays "undetermined" — do NOT gate the Gap Assessment on pinning Q1.
>
> **Q6 — Fix scope + guard-test design.** Name the exact files/lines the fix touches, and design a guard test: resolving from a NON-bellows tree must RAISE (not return a path), while the existing worktree resolution (bellows/.bellows-worktrees → canonical) must still pass. Note the fix is core daemon path-resolution used by 5 call sites (high blast radius). **Tier (walk 2 F9):** it computes to **T1** — `bellows_root.py` is execution-engine code, not a T-5/T-6 surface (not doctrine/template/gates/specialist contracts); T-1 (blast radius) + T-8 (novel) drive T1. The core-infra blast radius is grounds for OPTIONAL self-escalation to T2 at the fix author's discretion, not an automatic T2.
>
> **Constraints:** Read-only; no code edits; scratch-only file creation with cleanup. If a question is undeterminable from available evidence, report it as such — do not paper over. Also confirm whether deleting `lessons-forge/lifecycle.db` (0-byte) is safe (verify 0 bytes / no tables first).
>
> **Deposit:** `knowledge/research/bellows-root-fallback-stray-2026-08-19.md` — Q1–Q6 with the Gap Assessment table and the per-site classification table. End with an Output Receipt (Status). Standard prompt-feedback protocol.
>
> **Deposits:**
> - `knowledge/research/bellows-root-fallback-stray-2026-08-19.md`
