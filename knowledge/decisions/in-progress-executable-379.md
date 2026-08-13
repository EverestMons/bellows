# Executable: log retention + disk preflight — the ENOSPC class fails loudly instead of orphaning plans

**Type:** Executable
**Project:** bellows
**Depends on:** memory `bellows-log-accumulation-fills-disk` (the incident class: full disk → SILENT plan orphan (358) + garbage QA shipped unreviewed + phantom "156 test failures"), `bellows/bellows.py` (the claim move at line 588 measured at authoring — the preflight's wiring point; `statvfs` count 0, no existing guard), `bellows/logs/` (population measured at authoring: 20 step JSONs, 9.1M — healthy; this plan is PREVENTION), `bellows/config.json` + `config.example.json` (the key home)
**Created:** 2026-08-13
**Author:** Planner
**Slug:** `log-hygiene-2026-08-13`
**dispatch_mode:** bellows
**pause_for_verdict:** always
**Priority:** 5
**cycle_tier:** T1
**qa_steps:** 2

⚠️ **ID NOTE — the deposit filename is decided AT DEPOSIT.** `id_sequence` read at deposit, never at authoring.

---

## Why this exists

The ENOSPC incident's damage was its SILENCE: a full disk orphaned a plan and shipped garbage QA with no loud failure anywhere. Two guards close the class: **retention** (the accumulation never reaches the cliff) and **preflight** (if anything else fills the disk, the daemon refuses to claim — loudly — instead of dispatching into corruption).

⚠️⚠️ **THE RESTART BOUNDARY:** the running daemon (pid at dispatch time) holds old code; both guards go live at the next restart — the Planner's ops action at the wrap's idle window, never the agent's.

**Defaults are declared policy, CEO-overridable via config:** `log_retention_days: 30`, `disk_min_free_gb: 2` — read from `config.json` with these defaults when absent; `config.example.json` documents both.

---

## Specification

- **`_prune_old_logs()`** — called ONCE at daemon startup — **wire it in the startup sequence immediately after the session-restart banner is logged** (locate that emission; the `== 2` count probe enforces def-plus-one-call): deletes `logs/*.json` older than `log_retention_days` by mtime. **Never touches** `logs/terminal/`, `daemon-nohup.log`, or any non-`.json` file; each deletion logged INFO with the filename; total pruned logged. An unreadable/undeletable file logs WARN and continues (no crash — the hygiene must never kill the daemon).
- **`_disk_preflight()`** — called immediately BEFORE the claim move (the `shutil.move(plan_path, inprogress_path)` measured at line 588): `os.statvfs` on BELLOWS_ROOT; free bytes below `disk_min_free_gb` → **ERROR log naming the free/threshold numbers + one notifier ping per condition-onset (a module flag resets when the condition clears — no ping storm) + the claim is SKIPPED this scan** (retried next scan; the deposit stays untouched in `decisions/`). The guard fails the CLAIM, never the daemon.
- **Tests** in a new `tests/test_log_hygiene.py`: prune — a `tmp_path` logs dir with old and fresh `.json`, a `terminal/` subdir, and a non-json file: only the old `.json` files go; preflight — `statvfs` monkeypatched both sides of the threshold, the skip path returns False and the onset flag dedupes the notifier call (notifier monkeypatched, call count asserted); config — both keys default correctly when absent. All `tmp_path`; no test touches the real `logs/` or config.

---

## Ledger

- **C1 — the hygiene never kills the daemon:** both helpers are exception-wrapped (a failed prune or statvfs logs WARN and lets the scan proceed — degraded guard beats dead daemon; stated in code comment as the contract). *(observer: a dedicated exception-path test)*
- **C2 — the prune's blast radius is provably bounded:** the test proves terminal/, non-json, and fresh files survive; the deletion loop matches `*.json` directly in `logs/` only (no recursion). *(observer: the prune test)*
- **C3 — the preflight fails the claim, not the plan:** the skipped deposit remains in `decisions/` unclaimed and unrenamed; nothing is halted or orphaned. *(observer: the preflight test asserts the return contract; QA Item 2 reads the wiring — skip means no move)*
- **C4 — counts verified:** suite baseline measured at authoring **1006 passed** (post-376) — re-verify, report actual, unexplained delta HALTs. *(observer: QA Item 1)*
- **C5 — the restart boundary stated in the receipt.** *(observer: QA Item 3)*

---

## How to Run This Plan

**Bootstrap prompt:**
```
Read the plan at knowledge/decisions/in-progress-executable-<id>.md (the daemon renames the deposited placeholder on claim). Execute Step 1 ONLY. After completing Step 1, STOP and wait for my confirmation.
```

---

## Scope

- `bellows/bellows.py`
- `bellows/tests/test_log_hygiene.py`
- `bellows/config.example.json`
- `bellows/knowledge/development/log-hygiene-dev-2026-08-13.md`
- `bellows/knowledge/qa/evidence/log-hygiene-2026-08-13/qa-receipt.md`
- `bellows/knowledge/qa/evidence/log-hygiene-2026-08-13/pytest-full-raw.txt`

---

## STEP 1 — DEV (the two guards + tests)

> **FIRST — post a short visible chat message (1-2 sentences) confirming you are starting.** Do NOT rename this file. ⚠️⚠️ **EXECUTE STEP 1 ONLY, THEN STOP.** ⚠️ **THE WORKTREE RULE:** writes only from cwd. **Environment facts:** `grep` is a ugrep shim (`-F` literals; zero-count `grep -c` exits 1 — read the count).
>
> **Task A0:** (0) tree shape; (1) `git status --porcelain -- bellows.py tests/test_log_hygiene.py config.example.json` empty; (2) RE-ENTRY key: `git log --oneline -1 -- bellows.py` subject carries this slug → verify the Task C probes on committed content, report complete. Anything else → HALT quoting measurements.
>
> **Task B — implement** per the Specification. Verify the wiring point before editing: `grep -nF "shutil.move(plan_path, inprogress_path)" bellows.py` — exactly one hit (measured at authoring: line 588; a different line is fine, a different COUNT needs explaining).
>
> **Task C — targeted tests:** `python3 -m pytest tests/test_log_hygiene.py tests/test_bellows.py -q` FOREGROUND. Report actual counts (test_bellows baseline measured 189 — re-verify). Post-conditions: `grep -cF "_disk_preflight" bellows.py` == 2 (def + call), `grep -cF "_prune_old_logs" bellows.py` == 2, both config keys present in `config.example.json`.
>
> **Task D — dev note + commit** (`knowledge/development/log-hygiene-dev-2026-08-13.md`: what shipped, measured counts, raw tail). Pathspec exactly the four files, subject `[<id from your plan filename>]` + the slug. STOP.
>
> **Deposits:**
> - `bellows/bellows.py`
> - `bellows/tests/test_log_hygiene.py`
> - `bellows/config.example.json`
> - `bellows/knowledge/development/log-hygiene-dev-2026-08-13.md`
>
> **Scope:**
> - `bellows/bellows.py`
> - `bellows/tests/test_log_hygiene.py`
> - `bellows/config.example.json`
> - `bellows/knowledge/development/log-hygiene-dev-2026-08-13.md`

---

## STEP 2 — QA

> ⚠️⚠️ **PRECONDITION — Step 1 ran as its own dispatch** (the Step-1 commit pre-dates this step, not by this context; otherwise state the gap plainly).
>
> **(A) Rule 20 self-check block** — canonical, from `/Users/marklehn/Developer/GitHub/RULE_20_SELF_CHECK_BLOCK.md`, read live. The receipt carries `Rule 20 — QA Self-Check Results` and, on full pass, `PASSED — SELF-CHECK PASSED`. `required_evidence_files` = the evidence-directory subset of `## Scope`.
>
> **(B) Deliverable verification — a FAIL is reported, never repaired:**
> - **Item 1 — FULL suite FOREGROUND** (`python3 -m pytest tests/ -q`; raw tail to `pytest-full-raw.txt`; actual totals; C4's baseline comparison).
> - **Item 2 — the wiring from the diff:** the preflight call sits immediately before the claim move; the skip path contains no `shutil.move`, no rename, no halt — C3 visible in the hunk.
> - **Item 3 — C5:** the restart boundary stated verbatim.
> - **Item 4 — live prune rehearsal, SCRATCH-ONLY:** build a `tmp` logs dir (old + fresh + terminal/), point the helper at it by parameter/monkeypatch, run, paste the before/after listing raw.
> - **Item 5 — raw output throughout.**
>
> Commit receipt + raw file, pathspec exactly them. STOP.
>
> **Deposits:**
> - `bellows/knowledge/qa/evidence/log-hygiene-2026-08-13/qa-receipt.md`
> - `bellows/knowledge/qa/evidence/log-hygiene-2026-08-13/pytest-full-raw.txt`
>
> **Scope:**
> - `bellows/knowledge/qa/evidence/log-hygiene-2026-08-13/qa-receipt.md`
> - `bellows/knowledge/qa/evidence/log-hygiene-2026-08-13/pytest-full-raw.txt`

---

## Drafting Cycle

**Tier:** T1 — the daemon's own scan loop; a wrong guard could stop all claims (C1/C3 are the counter-guards).

**Walk 0 (v2.7, measured):** wiring point `shutil.move(plan_path, inprogress_path)` count-1 at line 588; `statvfs` count 0 (no prior guard to conflict); logs population 20 JSONs / 9.1M (healthy — prevention framing verified); suite baseline 1006 (post-376 measured). Newest same-class = 376 (`forward-none-guard`, this session — the helper+call-site+tests form carried; delta owned: two helpers and a new test module instead of one and an append, and the notifier onset-flag has no 376 analog — it is this plan's own risk, covered by a dedicated dedupe test). **Scout: not convened (T1, Planner's call — two bounded helpers; C1's never-kill contract is the systemic risk and carries its own test).** **Direction verdict: PROCEED.**

**Walk register:** `governance/knowledge/research/walk-register-log-hygiene-2026-08-13.md` (schema 0.2), committed at close with any compression owned.

**Walks:** 2. Fold trajectory 1 → 0.

- Weak spots:      w1 1 (k1, the prune wiring point); w2 0.
- Destruction:     w1 0; w2 0.
- Vulnerabilities: w1 0; w2 0.
- Integration:     w1 0; w2 0.
- ACID:            w1 0; w2 0.

**Closing:** walk 2 DRY — **instruction 0 / record 0**; the last event before deposit is a dry lens pass.
