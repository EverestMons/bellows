# Diagnostic QA-corrective: run the pin-census QA against committed HEAD — the 369 teardown-halt's owed Step 2

**Type:** Diagnostic
**Project:** bellows
**Depends on:** `bellows/knowledge/decisions/halted-diagnostic-369.md` (the parent plan — its Ledger C1–C6, Worktree Rule, and Scope are read FROM THERE, not restated here), the five step-1 deposits at HEAD, `/Users/marklehn/Developer/GitHub/RULE_20_SELF_CHECK_BLOCK.md`
**Created:** 2026-08-12
**Author:** Planner
**Slug:** `predicted-number-pin-census-2026-08-12` (STABLE — the parent's slug; this is the corrective re-deposit of its QA step)
**dispatch_mode:** bellows
**pause_for_verdict:** always
**Priority:** 5
**cycle_tier:** T1
**qa_steps:** 1

⚠️ **ID NOTE — the deposit filename is decided AT DEPOSIT.** `id_sequence` read at deposit, never at authoring.

---

## Why this exists

Plan 369 completed Step 1 clean — every mechanical verification row PASS, all five deposits committed (census commit `8f0a84903ac09b637e4ff0ed40e6a05368f1de64` alone-first per C2, findings commit `dab46c9c1cc8fda0221190b31d7acfcdc43ecd14`, landed on main via Planner merge `2c3d1b43b5ed7bbee41a71cba723393e12975fd3`; hashes derived at authoring — **verify by running the A0 probes, and a mismatch is a HALT, not a correction**). Its worktree teardown then failed on a stale staged index entry, the daemon's Gap-1b guard rejected the continue verdict, and the plan halted before Step 2 (QA) ran. Step-1's work stands committed and untouched; the audit is incomplete without its QA. This plan is the parent's STEP 2 ONLY, re-targeted at committed HEAD — the QA-process-failure → QA-only corrective pattern. It re-runs nothing else and edits nothing.

**Clone lineage (§2.6):** origin = the 362 QA-corrective form (`lessons-forge/knowledge/decisions/Done/executable-362.md`); **newest same-class = 366** (`bellows/knowledge/decisions/Done/executable-366.md`, the schema02 corrective — verified present at authoring). Diffed against 366: same single-QA-step shape, same stable-slug rule; deltas owned — this corrective adds the A0(4) receipt-absent double-run guard, and its independence item is satisfied by construction rather than by prior-dispatch evidence (366's parent failed at its own QA step; 369's step 1 completed and landed, so the corrective certifies committed work).

⚠️ **A QA FAIL is REPORTED, never repaired.** This plan grants no license to touch the step-1 deposits, the matchers, or anything else — a finding that fails an item goes in the receipt as FAIL with its evidence, and the step still deposits and stops.

---

## How to Run This Plan

**Bootstrap prompt:**
```
Read the diagnostic at knowledge/decisions/in-progress-diagnostic-<id>.md (the daemon renames the deposited placeholder on claim). Execute Step 1 (the only step). After completing it, STOP and wait for my confirmation.
```

---

## STEP 1 — QA (the parent's Step 2, against committed HEAD)

> **FIRST — post a short visible chat message (1-2 sentences) confirming you are starting this corrective QA.** Do NOT rename this file.
>
> **Task A0 — the corrective branch, narrowly keyed. ALL conditions hold → proceed; anything else → HALT quoting every measurement taken.**
> **(0) TREE SHAPE:** `git rev-parse --show-toplevel` from cwd prints a path whose tree contains `knowledge/decisions` (the parent's Worktree Rule applies to this whole plan: writes only from cwd; read-only probes of other repos use explicit `-C`).
> **(1) PARENT HALT PRESENT:** `knowledge/decisions/halted-diagnostic-369.md` exists (committed at `d09f274ade8843ea1609c61ae6225a318927e52b`).
> **(2) DEPOSITS AT HEAD:** all five present — `knowledge/qa/evidence/predicted-number-pin-census-2026-08-12/labelled-instances.md`, `matcher-m1-git-pins.py`, `matcher-m2-file-pins.py`, `precision-raw.txt` (same directory), and `knowledge/research/predicted-number-lint-findings-2026-08-12.md`.
> **(3) EVIDENCE COMMITS REACHABLE:** `git log --oneline -- knowledge/qa/evidence/predicted-number-pin-census-2026-08-12/` shows the census commit (subject carries `[369] census`) and the findings commit (subject carries `[369] findings`), census first.
> **(4) RECEIPT ABSENT:** `knowledge/qa/evidence/predicted-number-pin-census-2026-08-12/qa-receipt.md` does not exist — this QA never ran. If it exists, this corrective was already executed → HALT and say so.
>
> **Then execute the parent's STEP 2 exactly as written in `halted-diagnostic-369.md`** — the precondition, **(A)** the Rule 20 self-check block (canonical block read live from `/Users/marklehn/Developer/GitHub/RULE_20_SELF_CHECK_BLOCK.md`; the receipt carries the canonical header `Rule 20 — QA Self-Check Results` and, when every item passes, the canonical verdict line `PASSED — SELF-CHECK PASSED`; `required_evidence_files` = the evidence-directory subset of the parent's `## Scope`, read from the parent), and **(B)** Items 1–8 — with ONE adaptation: the independence precondition is satisfied BY CONSTRUCTION (this is a separate corrective dispatch; the step-1 commits pre-date this plan's deposit) — state that with the git evidence (commit timestamps vs. this plan's claim) rather than skipping the item.
>
> Commit the receipt from the step's own cwd with a pathspec naming exactly the deposit path, then STOP.
>
> **Deposits:**
> - `bellows/knowledge/qa/evidence/predicted-number-pin-census-2026-08-12/qa-receipt.md`
>
> **Scope:**
> - `bellows/knowledge/qa/evidence/predicted-number-pin-census-2026-08-12/qa-receipt.md`

---

## Drafting Cycle

**Tier:** T1 (inherited from the parent — T-7 fires on the findings this QA certifies). Corrective clone of the parent's own STEP 2; the parent's four-walk cycle covered the shared text.

**Walk register:** corrective rows appended to `governance/knowledge/research/walk-register-predicted-number-pin-census-2026-08-12.md` (same slug, same file; schema 0.2).

**Walks:** 2 (five lenses each, this corrective read against the parent as folded) — per-lens results in the register's corrective table.

- Weak spots:      w1 1 — 1 pre / 0 fold (the missing bootstrap block); w2 0.
- Destruction:     w1 0; w2 0.
- Vulnerabilities: w1 0; w2 0.
- Integration:     w1 0; w2 0.
- ACID:            w1 0; w2 0.

**Closing:** walk 2 DRY — **instruction 0 / record 1: the Walks-count line and this Closing, updated at the close itself**; the last event before deposit is a dry lens pass.
