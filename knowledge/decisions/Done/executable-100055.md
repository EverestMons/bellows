# bellows — executable: THE NOTIFIER-COVERAGE RECORD, WRITTEN FROM ITS OWN RUN — plan 100054's dev-log rewritten under the five headings it declared, from the halted run's transcript; `notify_watcher_down` routed through the one gate; the conftest fixture declared; then the QA the halted plan owed (thread 251, discharging 249, 245, 246 with the merged code of 100054)

**Date:** 2026-09-09 | **Project:** bellows | **Tier:** Small (two source files, one record, one fixture) | **Dispatch Mode:** bellows | **cycle_tier:** T1 | **Test Scope:** full-suite (Rule 21 — the notifier is called from every pause path; `pytest tests/` gates BOTH commits; `tests/test_notifier_coverage.py` edited at one test; `tests/test_notifier_server.py`, `tests/test_bellows.py`, `tests/test_depositor.py`, `tests/test_gate_watcher.py` unchanged) | **Execution:** Step 1 (DEV) → Step 2 (QA) | **qa_steps:** 2 | **pause_for_verdict:** always | **known_failures:** 0 | **Priority:** 1 | **Discharges:** thread 251, thread 249, thread 245, thread 246

**auto_close:** false

**Post-close:** ⚠️ **RESTART OWED** — `notifier.py`, `bellows.py` and `depositor.py` (100054's merged code, plus this plan's routing) are daemon imports; the restart was deferred from 100054's halt to this close. The CEO's acts, in order: the restart; the Pushover keys into each shop's `bellows/config.json` (secrets), then `notifications.enabled: true` and one proven push (MACHINE_SETUP v1.7 §7); the Air's `pmset` line (v1.7 §4 item 7). Until the keys are set the notifier stays dormant by design.

**Depends on:** the CEO's halt of 100054 (2026-09-09 16:54, STEP 1: `dev_log_declared_text` ×6 — the dev-log ignored the five declared headings and the P1 cell; `scope_check` on `tests/conftest.py`) and the ruling that the record is rewritten FROM the run, never invented; the four rulings 100054 rested on (the coverage, one channel per event, the daemon as pager, tuyere's liveness verb — MACHINE_SETUP v1.7). The merged code: bellows `f5c82a4` (DEV) and `6b4bfb5` (run + dev-log), on origin via push-at-merge. Clone origin BY KIND: `Done/executable-100047.md` (2026-09-08, the QA-only plan over merged code — the shape of finishing a halted plan's record without re-doing its work; T1); BY LAYOUT: `Done/executable-100053.md`. `clone-origin` threads naming either: none open (DC v2.33 query at walk 0).

**Tier computed (§1):** **T1** — T-1 fires (the notifier's pause paths); T-6 does not; T-2 does not.

## What this changes

⛔ **One routing, one declared fixture, one record rewritten from its source; nothing else in 100054's merged code moves.**

1. **`notifier.notify_watcher_down(machine, status, age_seconds)`** (`notifier.py:379-405`) — its inline enabled/event/dedupe/push sequence is REPLACED by one call: `notify_event("watcher_down", None, title, message, plan_scoped=False, detail_key=status)`; `mark_machine_live` keeps clearing the memo entry, whose key is now `notify_event`'s `(machine, "-", "watcher_down", status)` — the episode semantics (test 8 of 100054's sibling) are unchanged, and `mark_machine_live` clears every key for that machine and event regardless of status. The docstring says why: every page passes through the one gate (100054's change 4).
2. **`tests/conftest.py:39-44`** — the autouse `_clear_notifier_dedupe` fixture 100054's DEV added (the module-level `_dedupe_memo` leaks across tests) is DECLARED here: unchanged code, one comment line naming plan 100054 and this plan. Its consumer-by-effect: every test in the suite runs it — measured harmless (2160 passed).
3. **`knowledge/development/dev-log-notifier-coverage-2026-09-09.md`** — REWRITTEN under the five headings 100054 declared, each filled FROM the halted run's transcript (`logs/20260909-161445-step.json`, key `raw_output`, 4.1 MB — measured at walk 0: `P1` ×78, the pins heading ×2, `FAILED tests/test_notifier_coverage` ×6, `MUTATION:` ×20): `## Pins re-derived (P1, P2, P3, P4, P6)` (the DEV's grep outputs as printed there), `## Failing-first (the sibling red, then green)` (the first red run and the green run, as printed), `## Mutation run` (the run file's lines), `## Coverage table` (OPENS with THIS plan's P1 value cell pasted verbatim — the gate reads this plan's pin table for `← P1`; it describes 100054's merged code — then the eleven events, default and site, and 100054's own P1 quoted from the halted plan as a marked block), `## Cost` (the timings the DEV measured, as printed; if none were printed, say so and measure them now). ⛔ Nothing in the record is written from memory or invented: every number quotes the transcript or a fresh run made in this step, and each section says which.
4. **`knowledge/mutants/notifier-coverage.run.txt`** — re-run against this plan's first commit (the routing changed `notifier.py`; the manifest's seven anchors are re-verified count-1 first); `HEAD:` equals the manifest's last commit (untouched since `f5c82a4` unless an anchor moved — then the manifest is re-touched in the same commit as the routing).

## Why this exists

Plan 100054 shipped its code and failed its record: the `dev_log_declared_text` gate, live since #100052 that morning, read the plan's `**Headings:**` and `**Verbatim:**` lines against the dev-log and found none of the five headings and no P1 cell — six failures, the gate's first live catch of the class it was built for (three DEV runs paraphrased pins and rewrote headings in 100040/41/42 while every gate passed). Overriding it would have retired the gate on its first day. The CEO halted; the merged code is already on origin; what is owed is the record, written from the run that made it, and two small deviations folded back: the watcher_down page that bypassed the single gate, and a test fixture added outside Scope.

| # | pin | value | how to re-derive |
|---|---|---|---|
| P1 | ⛔ 100054's merged code | bellows `f5c82a4` (notifier +205/−35, bellows +82/−11, depositor +11, gate_watcher +4/−37, config.example +13/−5, conftest +8, sibling +676) and `6b4bfb5` (manifest +54, run +15, dev-log +31); main = origin/main; `notify_watcher_down` at `notifier.py:379`, `notify_event` at `:255`, `mark_machine_live` present; the run file `MUTATION: 7 killed, 0 survived, 0 error`, `HEAD:` = `f5c82a4`'s full sha | `git log 615d2cc..main`; grep |
| P2 | ⛔ the halted record | `knowledge/development/dev-log-notifier-coverage-2026-09-09.md` 31 lines with headings `## What Changed`, `## Why`, `## What Was Hard`, `## Decisions`, `## Test Results` — none of the five declared; the halted plan `knowledge/decisions/halted-executable-100054.md` (176 lines) carries the `**Headings:**`/`**Verbatim:**` lines at `:138-139` and P1's value cell in its pin table | grep |
| P3 | ⛔ the transcript | `logs/20260909-161445-step.json` (4,134,784 bytes; keys `success, raw_output, stderr, parsed`); `raw_output` holds the DEV's tool calls and outputs: `P1` ×78, `Pins re-derived` ×2, `FAILED tests/test_notifier_coverage` ×6, `passed` ×377, `MUTATION:` ×20, `wall` ×4; the worktree session's own transcript dir `~/.claude/projects/-Users-marklehn-Developer-bellows--bellows-worktrees-100054/` | `python -c` counts |
| P4 | the fixture | `tests/conftest.py:39-44` `_clear_notifier_dedupe` (autouse, clears `notifier._dedupe_memo` before and after every test) | read |
| P5 | tests | the sibling's 15 tests collect; test 8 (`watcher_down` episodes) asserts one push per episode and a second after `mark_machine_live` | `pytest --collect-only` |
| P6 | in-flight; class | none; `halted-executable-100054.md` in the lane (its claim released, its receipt archived); daemon pid 69409 running the code it loaded at start (`bellows.py@492f50d`, the pre-100054 notifier — the restart deferred to this close; the status header's `HEAD` is the checkout's, not the process's) | `status.py` |

## What this does NOT do

- ⛔ **It does not re-do 100054's work** — the code stays as merged; only the routing of one function and one comment line touch source.
- ⛔ **It does not invent the record** — every section quotes the transcript or a run made in this step and says which; a section with no source in the transcript is measured fresh and says so.
- ⛔ **It does not set the keys or flip `enabled`** — the CEO's, at close.
- **It does not change `mark_machine_live`'s contract** — it clears the machine's entries; the key gains `status` as `detail_key`.
- **It does not touch the manifest** unless an anchor moved (change 4).

## MUST-PRESERVE

⛔ **Invariants that must still be TRUE afterwards.**

- ⛔ **Every page passes through `notify_event`** — grep the merged `notifier.py` for `push(` calls outside `notify_event` and `_flush_buffer`: 0 after this plan. Proven by QA Item 3.
- ⛔ **The watcher_down episode semantics** — one page per stale episode, a second after `mark_machine_live`. Proven by 100054's test 8, unchanged.
- ⛔ **The five declared headings are lines of the dev-log and `## Coverage table` opens with P1's cell** — the 196 gate reads this plan's own record at its STEP 1 pause. Proven by the pause itself.
- ⛔ **The suite is green at both commits** (2160 passed at `f5c82a4`). Proven by the full suite.

## Drafting Cycle

**Tier:** **T1** — T-1 fires. **Walk register:** /Users/marklehn/Developer/eluvian-governance/governance/knowledge/research/walk-register-notifier-coverage-record-2026-09-09.md
**Walks:** walk 0 pinned (P1–P6 measured on bellows `main` = `6b4bfb5` and the halted plan; clone-diff against `Done/executable-100047.md` (kind) and `Done/executable-100053.md` (layout) run: FACTS, ARTEFACTS, STRUCTURE); `fold_check --save-baseline` ARMED on v0 before any fold; re-saved after every intended edit, emit after the re-save (v2.30). ⛔ **One commit per lens** (§2.7); `lens_order_check` runs with `cycle_check` at every walk close.

**Closing:** WARM close after walk 3 — the record-only follow-up to 100054 (threads 251/249/245/246), a judged stop. Three walks: instruction 5 → 1 → 0 (walk 1 folded six: five instruction, one record); T1, no panel. Deposit via `ready-`; HOLDS on class shop-infra, the CEO releases. Close acts, the CEO's: the daemon restart (deferred from 100054); the Pushover keys per shop, `notifications.enabled: true`, one proven push; the Air's `pmset` line; `threads done` for 251, 249, 245, 246 with `--commit bellows:f5c82a4` (100054's code) and this plan's DEV sha after the daemon's push.
- Weak spots:          w1 5 folded — instruction 5 / record 0
- Destruction:         w1 dry
- Vulnerabilities:     w1 dry
- Integration-record:  w1 1 folded — instruction 0 / record 1
- ACID:                w1 dry
- Weak spots:          w2 1 folded — instruction 1 / record 0
- Destruction:         w2 dry
- Vulnerabilities:     w2 dry
- Integration-record:  w2 dry
- ACID:                w2 dry
- Weak spots:          w3 dry
- Destruction:         w3 dry
- Vulnerabilities:     w3 dry
- Integration-record:  w3 dry
- ACID:                w3 dry
**Walk 3 — DRY, all five lenses, one commit per lens. Instruction 0 on a full pass: the WARM close meets the bar (§2) — a judged stop (7 findings over two walks: instruction 6 / record 1 plus f0; yield 6 → 1 → 0). T1: no panel owed.**

## Cycle Manifest
tier: T1
target: notifier.py
class: shop-infra
reads: notifier.py, tests/conftest.py, tests/test_notifier_coverage.py, knowledge/development/dev-log-notifier-coverage-2026-09-09.md, knowledge/decisions/halted-executable-100054.md, logs/20260909-161445-step.json, knowledge/decisions/Done/executable-100047.md, knowledge/decisions/Done/executable-100053.md
writes: notifier.py, tests/conftest.py, tests/test_notifier_coverage.py, knowledge/development/dev-log-notifier-coverage-2026-09-09.md, knowledge/mutants/notifier-coverage.run.txt, knowledge/mutants/notifier-coverage.json
open_forks: 1. a `dev_log_declared_text` pre-check in the DEV's own commit gate (run the gate over the deposit before Item 11's commit, so the record is refused at the DEV's desk and not at the pause); 2. the halted run's transcript as a first-class deposit (a `transcript:` line in the receipt) so a record-only follow-up names its source mechanically
walks: 3
yields: 5, 1, 0
validation: cycle_check=BAR_MET, plan_lint=0_FAIL, fold_check=VACUOUS, propagation_check=DIVERGENT:70
coherence: 3/3 body walks named in the register (8 register rows; walk-token match, NOT row coverage)
fold_baseline: governance/knowledge/decisions/drafts/.executable-bellows-notifier-coverage-record.md.foldcheck.json

---

## STEP 1 — DEV (the routing, the declared fixture, the record from the run; two commits)

> ⛔ **Every item starts by re-establishing the root** — `cd "$(git rev-parse --show-toplevel)" && test -f notifier.py && echo TREE_OK` — HALT unless TREE_OK. ⛔ **The interpreter is `/Users/marklehn/Developer/bellows/.venv/bin/python`, ABSOLUTE**; prove `VENV_OK`. ⛔ **Never run the daemon, `run_plan`, a claim, or a real push**; every test lives under `tests/`. ⛔ **Every commit gates on the FULL suite** and uses `git commit -F <msg-file> -- <paths>`. ⛔ **The record is written FROM `logs/20260909-161445-step.json` (`raw_output`) or from a run made in this step — never from memory**: each section names its source line or the command run here.
>
> **Scope:**
> - `notifier.py`
> - `tests/conftest.py`
> - `tests/test_notifier_coverage.py`
> - `knowledge/development/dev-log-notifier-coverage-2026-09-09.md`
> - `knowledge/mutants/notifier-coverage.run.txt`
> - `knowledge/mutants/notifier-coverage.json`
>
> **Item 1 — re-derive P1, P2, P4 and HALT on a mechanism mismatch**; paste the greps into the dev-log's `## Pins re-derived` section as the FIRST content of this step (the section also carries, quoted from the transcript, the pins 100054's DEV re-derived — marked `(from the 100054 transcript)`).
> **Item 2 — the routing test FIRST:** in `tests/test_notifier_coverage.py`, extend test 8 with an assertion that `notify_watcher_down` reaches `push` only through `notify_event` — monkeypatch `notifier.notify_event` to record calls and assert one call with `event == "watcher_down"`, `plan_scoped is False`, `detail_key == status`; run it red.
> **Item 3 — the routing** as change 1; **Item 4 — the fixture comment** as change 2.
> **Item 5 — the manifest's anchors:** verify each of the seven anchors is count-1 on the edited `notifier.py`; if one moved, re-anchor it in `knowledge/mutants/notifier-coverage.json`; if none moved, still touch the manifest (a `why` field's date) — Item 6 commits it either way so Item 7's `HEAD:` equality holds.
> **Item 6 — first commit**, gated on the FULL suite, path-scoped over `notifier.py tests/conftest.py tests/test_notifier_coverage.py knowledge/mutants/notifier-coverage.json` — four files, message tagged with the plan id AND `thread 251`.
> **Item 7 — the mutation run, REDIRECTED** into `knowledge/mutants/notifier-coverage.run.txt`, IMMEDIATELY after Item 6's commit: `tools/mutation_check.py knowledge/mutants/notifier-coverage.json > knowledge/mutants/notifier-coverage.run.txt 2>&1; echo "exit=$?"` → `exit=0`; `MUTATION: 7 killed, 0 survived, 0 error`; `HEAD:` = Item 6's commit, which is the manifest's last commit because Item 6 ALWAYS re-touches the manifest (a re-anchor if one moved, else a `why` field's date) — the tool archives HEAD, so the run happens before any other edit.
> **Item 8 — the record** as change 3: rewrite the dev-log under the five headings declared below; `## Coverage table` opens with THIS plan's P1 value cell pasted verbatim (the gate compares against this plan's pin table); every number's source named.
> **Headings:** `## Pins re-derived (P1, P2, P3, P4, P6)`; `## Failing-first (the sibling red, then green)`; `## Mutation run`; `## Coverage table`; `## Cost`
> **Verbatim:** `## Coverage table` ← P1
> **Item 9 — second commit:** the run file and the dev-log, gated on the FULL suite AND the run file's `MUTATION:` line, path-scoped over those two files. `numstat` over the DEV commits — exactly six files; `git reflog -n 6` → 0 amends.
>
> **Deposits:**
> - `knowledge/development/dev-log-notifier-coverage-2026-09-09.md`
> - `knowledge/mutants/notifier-coverage.run.txt`
>
> **Post-conditions:** the sibling's 15 tests pass; the full suite passes at both commits; the run file ends `MUTATION: 7 killed, 0 survived, 0 error`; the five headings are lines of the dev-log and `## Coverage table` opens with P1's cell; six files over two commits.

## STEP 2 — QA (full suite + the notifier dormant on the live config, shown)

> ⛔ **Re-establish the root first** — `cd "$(git rev-parse --show-toplevel)" && test -f notifier.py && echo TREE_OK`; interpreter ABSOLUTE; prove `VENV_OK`. ⛔ **No real push**; Pushover is never contacted. ⛔ **The receipt never writes an undefined `tests/…::name` id.** Scratch under `/private/tmp/qa-notifier-coverage-record/`.
>
> **Item 1 — full suite, REDIRECTED not piped:** `/Users/marklehn/Developer/bellows/.venv/bin/python -m pytest tests/ --tb=short -q > knowledge/qa/evidence/notifier-coverage-record-suite-2026-09-09.txt 2>&1 || { echo HALT-SUITE-RED; exit 1; }`.
> **Item 2 — the live config, read-only:** `init_notifications` with `/Users/marklehn/Developer/bellows/config.json` → `_notifications_enabled()` is `False`; `notify_event("verdict_needed", "executable-bellows-notifier-coverage-record", …)` with `push` patched → not paged, the INFO line says `disabled`. Paste.
> **Item 3 — one gate:** `grep -n "push(" notifier.py` → every call sits inside `notify_event`, `_flush_buffer`, or `push` itself; paste the grep. `notify_watcher_down("air", "stale", 900)` with `notify_event` patched → one call with `plan_scoped=False`, `detail_key="stale"`. Paste.
> **Item 4 — ownership on THIS plan's own receipt:** `/Users/marklehn/Developer/bellows/receipts/receipt-executable-bellows-notifier-coverage-record-<sid>-*.json` (the MAIN checkout's dir; `receipts_dir` passed explicitly) → `owned_by_live_session(...)` tuple pasted, with the transcript's age stated.
> **Item 5 — the liveness verb live, read-only:** via `plan_claim._tuyere_checkout()` → the JSON pasted; both machines expected `live`.
> **Item 6 — the record reads as declared:** `gates._gate_dev_log_declared_text` in-process over `/Users/marklehn/Developer/bellows/knowledge/decisions/in-progress-executable-<this plan's id>.md` (the MAIN checkout's lane file; HALT if absent) STEP 1 text and the dev-log → nothing; the probe prints 5 headings found and 1 verbatim cell found. Paste.
> **Item 7 — production writes, stated exactly:** none outside the two evidence files; no push; no lane file; no lifecycle row.
> **Item 8 — receipt** `knowledge/qa/evidence/notifier-coverage-record-qa-evidence-2026-09-09.md`: numstat over the DEV commits (six files; `<base>` = the parent of Item 6's commit, `<dev>` = the last DEV commit); the run file's `HEAD:` equal to `git log -1 --format=%H -- knowledge/mutants/notifier-coverage.json`; `git diff <base>..<dev> -- tests/test_notifier_server.py tests/test_bellows.py tests/test_depositor.py tests/test_gate_watcher.py` → EMPTY; toplevel; `git reflog -n 6` → 0 amends; the five dev-log headings grepped; Items 1–7 each on its own line; the Rule 20 block inside a `## Verification` section. ⛔ Never place a hedging keyword in a ✅ row.
> **Item 9 — commit**, path-scoped and gated: `grep -Eq '^[0-9]+ passed' knowledge/qa/evidence/notifier-coverage-record-suite-2026-09-09.txt && ! grep -Eq '[0-9]+ (failed|error)' knowledge/qa/evidence/notifier-coverage-record-suite-2026-09-09.txt && git add knowledge/qa/evidence/notifier-coverage-record-suite-2026-09-09.txt knowledge/qa/evidence/notifier-coverage-record-qa-evidence-2026-09-09.md && git commit -F <msg-file> -- knowledge/qa/evidence/notifier-coverage-record-suite-2026-09-09.txt knowledge/qa/evidence/notifier-coverage-record-qa-evidence-2026-09-09.md` — exactly two files.
>
> **Deposits:**
> - `knowledge/qa/evidence/notifier-coverage-record-suite-2026-09-09.txt`
> - `knowledge/qa/evidence/notifier-coverage-record-qa-evidence-2026-09-09.md`
>
> **Scope:**
> - `knowledge/qa/evidence/notifier-coverage-record-suite-2026-09-09.txt`
> - `knowledge/qa/evidence/notifier-coverage-record-qa-evidence-2026-09-09.md`

Rule 20 banner (byte-exact, inside the QA receipt's VERIFICATION section):

```
============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
```
