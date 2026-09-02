# bellows — executable: CANARY for the de-hardcoded QA mandate — one QA-classified step that quotes the Rule 20 path the RESTARTED daemon handed it, and runs the block from that path

**Date:** 2026-09-01 | **Project:** bellows | **Tier:** Small | **Dispatch Mode:** bellows | **cycle_tier:** T0 | **Test Scope:** none (a canary: one QA evidence deposit, no code, no DB write by the agent) | **Execution:** Step 1 (QA) | **qa_steps:** 1 | **pause_for_verdict:** always | **known_failures:** 0 | **Priority:** 1

**auto_close:** false

**Slug:** `mandate-canary-2026-09-01`

**Depends on:** plan 100011's DEV commit `6b892a3` (the de-hardcoded `gates.QA_MANDATE_SUFFIX`, on main), plan 100012 (Done — the suite green in both shapes), and the CEO's dashboard restart (daemon pid 98058, started 2026-09-01 23:44:02, `status.py` sha `6b892a3`). Restart Discipline (PLANNER_TEMPLATE): after a code change, deposit a small canary whose characteristics exercise the changed path. The changed path is THE MANDATE STRING the dispatcher injects into a QA step's prompt — so the canary's only requirement is to BE a QA step and to quote what it was handed. Its parent by kind is `Done/executable-100010.md` (the verdict-signal canary, 2026-09-01).

**Tier computed (§1):** T0 — no trigger fires: one evidence deposit under `knowledge/qa/evidence/` (no code, no production data, same machine, nothing irreversible, no governance surface, not authored from a diagnostic). **T0 runs the integration-vs-record pass only (Lens 4), then deposits.**

## Why this exists

Before 100011 every QA agent on the mini was told to run the Rule 20 block *"from /Users/marklehn/Developer/GitHub/RULE_20_SELF_CHECK_BLOCK.md"* — a path that does not exist here — and each plan carried a per-plan workaround. 100011 made the mandate name the resolved governance root; 100012's QA quoted BOTH paths (the pre-fix daemon's shop path it was handed, and the resolved path it used). The daemon does not hot-reload, so the proof that the LIVE dispatcher now hands out the right path is the first QA step after the restart. This plan is that step. **What the Planner measures at the pause, from outside:** the deposited `qa-receipt.md` quotes a received mandate path equal to `/Users/marklehn/Developer/eluvian-governance/RULE_20_SELF_CHECK_BLOCK.md`, the banner pair is present, and `plans.lifecycle_state = awaiting_verdict` at the pause (100009's arm, on the new process).

## STEP 1 — QA

> **FIRST — post a short visible chat message (1–2 sentences).** Do NOT rename this file. You are the Bellows QA agent. This step has no DEV step before it: there is nothing to verify but the mandate you were handed.
>
> `cd "$(git rev-parse --show-toplevel)" && [ -f bellows.py ] && echo TREE_OK` — HALT unless TREE_OK. `PY="$(cd "$(git rev-parse --git-common-dir)/.." && pwd)/.venv/bin/python"; [ -x "$PY" ] && echo VENV_OK` — HALT unless VENV_OK.
>
> `mkdir -p knowledge/qa/evidence/mandate-canary-2026-09-01`, then write `knowledge/qa/evidence/mandate-canary-2026-09-01/probes-raw.txt` with exactly these measured items (raw output, no interpretation):
> 1. `date -u +%Y-%m-%dT%H:%M:%SZ`
> 2. `git rev-parse --short HEAD` (your worktree HEAD)
> 3. **RECEIVED:** the Rule 20 block path EXACTLY as it appears in the mandate text of YOUR OWN PROMPT (the sentence beginning "MANDATORY FOR THIS QA STEP (dispatcher-injected)" — copy the path between "block from " and " (absolute path)"). This is the one measurement only you can make.
> 4. **COMPUTED:** `"$PY" -c "import gates; s=gates.QA_MANDATE_SUFFIX; i=s.find('block from ')+11; print(s[i:s.find(' (absolute path)', i)])"` — the path your tree's code would inject.
> 5. `test -f "<the RECEIVED path>" && echo RECEIVED_EXISTS || echo RECEIVED_MISSING`
> 6. `/usr/bin/grep -cF -- 'Developer/GitHub' <(printf '%s' "<the RECEIVED path>")` → expected `0` (a zero-count grep exits 1 — that is the pass)
>
> **Then run the Rule 20 canonical self-check block FROM THE RECEIVED PATH (item 3)** — if it is missing, HALT and say so: that is the canary's failure signal — with:
> - `plan_slug`: `mandate-canary-2026-09-01`
> - `qa_report_path`: `"$(pwd)/knowledge/qa/evidence/mandate-canary-2026-09-01/qa-receipt.md"`
> - `evidence_dir`: `"$(pwd)/knowledge/qa/evidence/mandate-canary-2026-09-01"`
> - `required_evidence_files`: `["probes-raw.txt"]`
>
> **The report** `qa-receipt.md` (written BEFORE the block runs, the block's stdout APPENDED after): a four-row verification table — RECEIVED path (item 3), COMPUTED path (item 4), RECEIVED == COMPUTED (yes/no), RECEIVED_EXISTS (item 5) — each with its measured value; then the Rule 20 stdout. Commit by explicit pathspec: `git add knowledge/qa/evidence/mandate-canary-2026-09-01/ && git commit -m "[<id from your plan filename>] mandate canary: the restarted daemon's Rule 20 path, received and computed" -- knowledge/qa/evidence/mandate-canary-2026-09-01/`. STOP.
>
> **Deposits:**
> - `knowledge/qa/evidence/mandate-canary-2026-09-01/qa-receipt.md`
> - `knowledge/qa/evidence/mandate-canary-2026-09-01/probes-raw.txt`
>
> **Scope:**
> - `knowledge/qa/evidence/mandate-canary-2026-09-01/qa-receipt.md`
> - `knowledge/qa/evidence/mandate-canary-2026-09-01/probes-raw.txt`

Rule 20 banner (byte-exact, produced by RUNNING the canonical block — never hand-authored):

```
============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
```

---

## Drafting Cycle

**Tier:** T0 (no trigger) — the integration-vs-record pass only, per §1.

**Walk register:** /Users/marklehn/Developer/eluvian-governance/governance/knowledge/research/walk-register-de-hardcode-2026-09-01.md
(This canary is recorded as rows of the parent cycle's register — its own cycle is the one T0 pass.)

- Integration-record: w1 dry — one QA-classified step (`qa_steps: 1`, the classifier's primary key at `gates.py:839-849`, read) so the mandate is injected; the deposit is two evidence files under `knowledge/qa/evidence/` (the class assigner's dry-run: `app-feature`); the agent measures the one thing only it can see (its own prompt) and pairs it with the computed value and an existence test; the Rule 20 gate's needs (report first, banner byte-exact, evidence present) are met by the step as written; the plan claims nothing about its own pause state (the Planner measures it from outside).

**Closing:** T0 floor pass dry; deposit.

## Cycle Manifest
tier: T0
target: knowledge/qa/evidence/mandate-canary-2026-09-01/qa-receipt.md
class: app-feature
reads: /Users/marklehn/Developer/bellows/gates.py
writes: knowledge/qa/evidence/mandate-canary-2026-09-01/qa-receipt.md, knowledge/qa/evidence/mandate-canary-2026-09-01/probes-raw.txt
open_forks: none
walks: 1
yields: 0
validation: cycle_check=BAR_MET, plan_lint=0_FAIL, fold_check=N/A
coherence: 1/1 walks have register rows
