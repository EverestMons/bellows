# Bellows — Daemon-Owned Append-Only Ledgers: Relocate Shared Bookkeeping Out of the Worktree Merge Path (Design)
**Date:** 2026-06-13 | **Tier:** Medium | **Dispatch Mode:** bellows | **Execution:** Step 1 (SA) | **pause_for_verdict:** after_step_1

## Context (Rule 27)
Diagnostic 41 (`knowledge/research/worktree-teardown-resume-cluster-2026-06-13.md`, Done) established that the worktree teardown conflict cluster (FORWARD rows 4/5/13-Gap3) reduces to ONE structural cause: **shared append-only bookkeeping files are written from inside per-plan worktrees and collide at the teardown merge.** The recommended band-aid (a `.gitattributes merge=union` driver) was explicitly DECLINED by the CEO in favor of the root fix this diagnostic designs: **a worktree should carry only CODE; shared append-only ledgers should be written by the daemon (the serialized sole writer, which never merges) — post-merge onto `main`, or stored in `lifecycle.db` and generated — so the conflict class is deleted, not concatenated around.** This aligns with the generated-reporting direction (Reporting Phases 2/3: backward-looking ledgers become DB-derived rather than hand-merged). This is a DESIGN investigation ONLY — author no implementation; the build executable(s) follow CEO review of the forks. Read/DB/git access read-only.

The conflict-prone ledger set identified by diagnostic 41 (re-verify and complete): `PROJECT_STATUS.md` (per-project, Rule 8 — QA writes at close), `knowledge/research/agent-prompt-feedback.md` (the feedback protocol — agents append every step), `knowledge/FORWARD.md` (Rule 42 reconciliation — QA writes), governance-root `LESSONS.md`, and any other shared append-only file a step writes inside its worktree. Anchors (re-verify by grep): `_teardown_worktree` (bellows.py:1103) merge at ~1190–1209; the daemon's post-step / verdict-consume path; PLANNER_TEMPLATE Rules 8, 23 (housekeeping order), 26 (deposits), 42 (reconciliation), and the feedback protocol.

## How to Run
Bellows dispatches this plan automatically when deposited; no manual bootstrap required.

---
---

## STEP 1 — Bellows Systems Analyst

---

> **FIRST — before any reads or work: post a short visible chat message (1-2 sentences) confirming you are starting this plan and stating your immediate next action.** Liveness anchor — do NOT rename the plan file (Bellows owns the claim). **AFTER posting:** read your specialist file `agents/BELLOWS_SYSTEMS_ANALYST.md` first, then diagnostic 41's findings (the established root), then `_teardown_worktree` and the verdict-consume/post-step path in `bellows.py`, then PLANNER_TEMPLATE.md Rules 8/23/26/42 and the feedback protocol. **Post a 1-line "Read X." per file and "Drafting Section N." per section.** Ground every claim at file:line / rule-number.
>
> **Section 1 — Ledger inventory & write-path census.** Produce the authoritative table of every shared file a STEP writes from inside its worktree that can collide at teardown: `| file | scope (per-project / governance-root) | written by (which agent/step) | triggered by (which rule/protocol) | append vs structured-edit | conflict risk |`. Confirm each writer at file:line or rule. Distinguish genuinely-shared append-only ledgers (collide) from code-adjacent files that legitimately belong in the worktree (do not).
>
> **Section 2 — Current write→merge mechanics.** Trace, at file:line, exactly how one of these files travels from agent-write-in-worktree → worktree commit → teardown merge → conflict. Confirm the daemon's relationship to `main` (it operates on the real project root, not a worktree) and that daemon-side writes do NOT merge. State the precise property that makes the daemon a conflict-free writer.
>
> **Section 3 — Relocation design (per-file disposition).** For each ledger from Section 1, propose its target mechanism and justify: **(a) daemon-written post-merge** — agent emits the intended content via a channel (see Section 4); daemon applies it to the file on `main` AFTER the code merge, outside any worktree; **(b) DB-stored + generated** — content becomes `lifecycle.db` rows; the `.md` is generated (the reporting model); **(c) leave in worktree** — genuinely code-adjacent, low conflict risk. Recommend one per file with the trade-off (e.g. PROJECT_STATUS narrative → daemon-post-merge or generated? feedback → DB rows? LESSONS → daemon-post-merge?).
>
> **Section 4 — The agent→daemon content channel.** Design how a step communicates ledger content to the daemon for post-merge application without writing the shared file in its worktree. Compare ≥2 options: e.g. a structured field in the Output Receipt the daemon already captures; a dedicated per-step deposit in a non-merged location the daemon reads and applies; extension of the existing `**Deposits:**`/gate system. State integration points at file:line, ordering/serialization for parallel plans (daemon writes serially — by what key: plan id? close time?), and idempotency on retry/resume.
>
> **Section 5 — Governance blast radius.** Enumerate every PLANNER_TEMPLATE rule, COMPANY/SPECIALIST template, and protocol that currently instructs an AGENT to write one of these files (Rules 8, 23, 26, 42, the feedback protocol, specialist files) and must change under the new contract. One row each: `| site (file:rule) | current instruction | required change |`. This is the cutover executable's governance edit-site list.
>
> **Section 6 — Failure modes & migration.** Compare failure semantics: TODAY a ledger conflict strands the whole plan at teardown; UNDER the new design, if the daemon crashes between code-merge and ledger-write, the code lands but the ledger update is lost — assess recoverability (re-derivable? logged for replay?) and whether that is acceptable vs today. Propose a phased migration (which ledger moves first; coexistence of agent-write and daemon-write during transition; how to verify no regression) vs big-bang.
>
> **Section 7 — Gap Assessment + `### Verification Blocks` (Rule 39).** Gap Assessment `| Gap | Current State (file:line/rule) | Proposed State | Change Required |` spanning bellows (daemon write path, teardown) + governance (the Section 5 sites). Verification Blocks `(claim, query, expected_output)` for the load-bearing facts: the daemon-is-conflict-free-writer property, the ledger inventory, the channel integration point, and the failure-mode comparison. Close with **CEO decision forks** (each with a recommendation): per-file disposition (daemon-post-merge vs DB-generated vs leave); the agent→daemon channel choice; phased vs big-bang; whether governance edits ship with the mechanism or separately (Rule 29 split); and whether this fully closes FORWARD rows 4/5/13 (and confirm row 12 stays resolved).
>
> **BEFORE FINISHING — explicitly `git add` your deposit file and `git commit` it.** Use `with open()` for the deposit; no heredocs. Standard prompt feedback → `knowledge/research/agent-prompt-feedback.md`. **Deposits:**
> - `bellows/knowledge/research/daemon-owned-ledgers-design-2026-06-13.md`
