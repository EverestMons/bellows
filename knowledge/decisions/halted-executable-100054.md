# bellows — executable: THE NOTIFIER PAGES THE RULED COVERAGE AND NOTHING TWICE — the event table becomes MACHINE_SETUP v1.7's list (three events added at their sites, four turned off), one channel per event through the deposit receipt's session, dedupe by (machine, plan, event), the gate watcher stops paging, and the rescan polls tuyere's liveness for a stale or down watcher (thread 249, discharging 245 and 246)

**Date:** 2026-09-09 | **Project:** bellows | **Tier:** Medium (six source files, one subsystem — the notifier and its call sites) | **Dispatch Mode:** bellows | **cycle_tier:** T1 | **Test Scope:** full-suite (Rule 21 — the notifier is called from every pause path; `pytest tests/` gates BOTH commits; new sibling `tests/test_notifier_coverage.py`; `tests/test_notifier_server.py`, `tests/test_bellows.py`, `tests/test_depositor.py`, `tests/test_gate_watcher.py` unchanged) | **Execution:** Step 1 (DEV) → Step 2 (QA) | **qa_steps:** 2 | **pause_for_verdict:** always | **known_failures:** 0 | **Priority:** 1 | **Discharges:** thread 249, thread 245, thread 246

**auto_close:** false

**Post-close:** ⚠️ **RESTART OWED** — `notifier.py`, `bellows.py` and `depositor.py` are imported by the daemon; until it restarts, the old event table pages. The CEO's acts at close, in order: the restart; the Pushover keys into each shop's `bellows/config.json` (secrets — never the Planner's), then `notifications.enabled: true` and one proven push (MACHINE_SETUP v1.7 §7); the `pmset` line on the Air (v1.7 §4 item 7). ⚠️ Until the keys are set, `enabled: false` with empty keys stays the consistent state and this plan changes NOTHING the CEO sees — its effect is dormant by design.

**Depends on:** the CEO rulings of 2026-09-09 (session d04ebd33): **the coverage** (page `verdict_needed`, `plan_halted`, `failure`, disk low, a class HOLD awaiting release, a stale-checkout hold or rejected push, a watcher stale or down on any machine; NOT plan complete, plan skipped, queue empty, cycle nudges — MACHINE_SETUP v1.7 §4 item 3); **one channel per event** — the daemon pages and the gate watcher only logs (the doubled verdict page measured at `bellows.py:1272/1407` and `tools/gate_watcher.py:172`); **the ownership signal** — the deposit receipt's `session_id`, attended when that session's transcript `~/.claude/projects/*/<sid>.jsonl` was modified within a window (measured: the transcript is appended every turn); **the liveness read** — tuyere's `python -m tuyere.control liveness --json` (landed 2026-09-09 as tuyere `b444bdd`, 107 tests; measured live: both machines `live`, `heartbeat_only=True`). Clone origin BY KIND: `Done/executable-100009.md` (2026-09-01, the verdict-signal plan — the pause sites, `notify_verdict_request`, `gate_watcher`; T1); BY LAYOUT: `Done/executable-100053.md` (2026-09-09, the newest T1). `clone-origin` threads naming either: none open (DC v2.33 query at walk 0).

**Tier computed (§1):** **T1** — T-1 fires (six files across the daemon's pause paths, one subsystem); T-6 does not (the notifier is not a gate, doctrine or a specialist contract); T-2 does not (no data); T-3 does not (the tuyere CLI call clones `plan_claim`'s seam, already exercised on both shops).

## What this changes

⛔ **One gate function every page passes through, a defaults table, three new notifiers wired at their sites, four events off by default, one watcher line, one poll. Nothing else in the pause paths moves.**

1. **`notifier._DEFAULT_EVENTS`** — the ruled table, read by `_event_enabled(name)` as `events.get(name, _DEFAULT_EVENTS.get(name, False))` (today: `events.get(name, True)` — an unknown event pages): `verdict_needed`, `plan_halted`, `failure`, `disk_low`, `class_hold`, `checkout_stale`, `watcher_down` → `True`; `plan_complete`, `plan_skipped`, `queue_empty`, `cycle_nudge` → `False`. A machine's `config.json` may flip any of them; `config.example.json`'s `events` block is rewritten to the same eleven keys with these values.
2. **`notifier.owned_by_live_session(plan_slug, receipts_dir=None, window=None) -> (owned: bool, why: str)`** — the ownership signal: `receipts/receipt-<slug>-*.json` under the daemon's own receipts dir — `receipts_dir` defaults to `resolve_bellows_root() / "receipts"` — the same resolver `lifecycle.py:21` uses for `LIFECYCLE_DB_PATH` (imported from the module lifecycle imports it from, measured at Item 1; NEVER from `bellows`, which imports `notifier` — a circular import), never `Path(__file__)` (a worktree's copy would read an empty dir); the same directory `_retire_receipts` globs (`bellows.py:478-510`); the glob `_retire_receipts` uses (`:505`); the newest by mtime when several — its `session_id`; then `glob(os.path.expanduser("~/.claude/projects") + "/*/<session_id>.jsonl")` (through `expanduser`, so a test's `HOME` monkeypatch is honoured); the transcript's mtime within `attended_window_seconds` (config, default 600) → `(True, "owned by session <sid8> — transcript <n>s old")` with `<n>` = `int(age)`; no receipt, no transcript, or older → `(False, <which>)`. Never raises; any exception → `(False, "ownership check failed: <type>")` (a check that cannot run must page, not silence).
3. **`notifier._dedupe(key) -> bool`** — an in-process memo `{(machine, plan_slug, event, detail_key): last_sent_epoch}` — `detail_key` is the STEP for `verdict_needed`, `plan_halted` and `failure` (a plan's step-2 pause is not a repeat of its step-1 pause), `""` for `class_hold`, `checkout_stale`, `disk_low`, and the status for `watcher_down` — with `dedupe_window_seconds` (config, default 3600); `machine = socket.gethostname()`; a repeat within the window is dropped with one INFO line; a daemon restart clears it (stated).
4. **`notifier.notify_event(event, plan_slug, title, message, priority=0, plan_scoped=True) -> bool`** — the ONE gate: enabled → `_event_enabled(event)` → `_dedupe` → (`plan_scoped` only) `owned_by_live_session` → `push`. Every refusal logs exactly one INFO line naming the reason (`notifier: <event> <slug> not paged — <why>`); a push logs `notifier: <event> <slug> paged`. `notify_verdict_request` (priority 1), `notify_plan_halted`, `notify_failure` are re-pointed through it with their texts unchanged and each gains an OPTIONAL trailing `plan_slug=None` kwarg (the 74 positional patches keep binding); the sites pass the receipt slug — `plan_slug` where the pause paths hold it (`:1276`, `:1410`), and where only a plan id is known (the halted sites `:3233`, `:3305`) the slug is resolved the way `_retire_receipts(plan_id)` does, lifted into `bellows._receipt_slug(plan_id)`; a site that cannot resolve a slug passes `None`, and `notify_event` treats `None` as 'no receipt' → page (silence is never the failure mode); the coalescing digest (`_enqueue_deferred`/`_flush_buffer`) is untouched but its four event types are now off by default.
5. **Three new notifiers:** `notify_class_hold(plan_slug, assigned_class)` (event `class_hold`, `plan_scoped=False` — a hold awaiting the CEO is never "owned"; the depositing session may be gone); `notify_checkout_stale(plan_slug, detail)` (event `checkout_stale`, plan-scoped); `notify_watcher_down(machine, status, age_seconds)` (event `watcher_down`, not plan-scoped; dedupe key `(machine, "-", "watcher_down")`, and the memo entry is CLEARED when a later poll reads that machine `live`, so each stale episode pages once); `notify_disk_low(free_gb, threshold_gb)` (event `disk_low`, not plan-scoped) replacing the raw `push` at `bellows.py:421`.
6. **The sites.** `depositor.py:190` (the shop-infra hold) → `notifier.notify_class_hold(slug, assigned_class)` after `_hold` (`import notifier` added — depositor runs in the daemon process where `init_notifications` has run; a NameError-free import guard when run standalone). `bellows.py:1008` (wire point A's `stale-checkout` hold) → `notifier.notify_checkout_stale(slug, _cic_detail)` after the WARN. ⚠️ A REJECTED PUSH is NOT a second event: it surfaces as a `worktree_teardown` gate failure whose evidence carries `worktree_teardown_push_rejected` and the plan pauses — `verdict_needed` pages it with the gate name; paging `checkout_stale` there too would double (stated; test 9 pins it).
7. **The liveness poll** (`Orchestrator._rescan`, beside the `_cycle_nudge_last_eval` arm, `bellows.py:2707`): every `liveness_poll_seconds` (config, default 300) run `[<tuyere checkout>/.venv/bin/python, "-m", "tuyere.control", "liveness", "--json"]` with `plan_claim._tuyere_checkout()` (`plan_claim.py:36`) and a 15 s timeout — the rescan runs inline in the main loop, so the poll stalls it by at most 15 s once per `liveness_poll_seconds` (300 s), never per plan; parse the list; for each row with `status in ("stale", "down")` → `notify_watcher_down(machine, status, age_seconds)`; rows `live` → clear that machine's memo. A missing checkout, a non-zero exit, a timeout or unparseable output → ONE WARN per poll, never raise, never block the rescan.
8. **`tools/gate_watcher.py:150-182`** — the push block is replaced by the return `"WATCH: push skipped (the daemon is the pager — MACHINE_SETUP v1.7)"`; the watcher keeps reading, logging and exiting exactly as before (its docstring gains one sentence).

## Why this exists

Measured 2026-09-09: the notifier's event table pages seven things and defaults an UNKNOWN event to on; a verdict pause is paged twice (the daemon and the detached watcher each call `notify_verdict_request`); a shop-infra deposit HOLDS at admission and nothing tells the CEO it is waiting (six holds this week, each released only after the Planner said so); a stale-checkout hold logs one WARN and nothing else; a watcher can go stale on the Air and no one is told. The CEO ruled the coverage (MACHINE_SETUP v1.7), the one-channel rule with the deposit receipt's session as the ownership signal, the gate watcher as a logger, and tuyere's liveness verb as the read. Pushover carries no state and no history; tuyere keeps the record.

| # | pin | value | how to re-derive |
|---|---|---|---|
| P1 | ⛔ the notifier | `notifier.py` 235 lines at bellows `615d2cc`: `init_notifications` `:29-34` (module globals `_config`, `_app_key`, `_user_key`), `_event_enabled` `:41-46` (`events.get(name, True)`), `_coalesce_window` `:48`, `push` `:55-81` (`requests.post`, timeout (5, 10), returns `status_code == 200`), the digest `:83-171` (arms `plan_complete`/`plan_halted`/`plan_skipped`/`queue_empty`/`cycle_nudge`), `notify_plan_complete` `:173`, `notify_plan_halted` `:180`, `notify_plan_skipped` `:187`, `notify_queue_empty` `:194`, `notify_failure` `:201`, `notify_cycle_nudge` `:214`, `notify_verdict_request` `:221-235` (priority 1) | `grep -n "^def "` |
| P2 | ⛔ the daemon's sites | `bellows.py:417-424` disk low (raw `push`, guarded by `_disk_low_notified`); `:855`, `:3233`, `:3305` `notify_plan_halted`; `:1272` and `:1407` `notify_verdict_request` (after `mark_plan_state("awaiting_verdict")`); `:1478` `notify_failure`; `:1008` the stale-checkout hold's `json.dump` (wire point A, plan 100050); `:2327` the `worktree_teardown_push_rejected` raise; `:2707` `self._cycle_nudge_last_eval` in `Orchestrator.__init__`, `_rescan` `:2850`; `init_notifications(config)` `:3564` | grep each |
| P3 | ⛔ the depositor's hold | `depositor.py:190-192` `self._hold(path, f"class:{assigned_class}", {"class_assigned": …})` for shop-infra; `_hold` `:855-866` writes `hold_reason`, `held_at`; depositor imports no `notifier` today (0) | grep |
| P4 | ⛔ the gate watcher | `tools/gate_watcher.py` docstring `:1-27` ("a REPORTER, never an actor"); the push block `:150-182` builds `notify_verdict_request` from `cfg` beside the DB and returns `WATCH: push sent` / `push skipped (…)` strings | read |
| P5 | ⛔ the receipt and the transcript | `receipts/receipt-<slug>-<session_id>-<hash12>.json` with keys `armed_at, attestation_boundary, content_hash, session_id, slug, watcher` (measured on this plan's predecessors); `_retire_receipts` globs `receipt-{slug}-*.json` (`:505`); transcripts at `~/.claude/projects/<cwd-slug>/<session_id>.jsonl` — this session's mtime equalled the current minute at walk 0 (appended every turn); the projects dir holds one folder per cwd, worktrees included | `ls`; `stat` |
| P6 | ⛔ the liveness verb | tuyere `b444bdd`: `python -m tuyere.control liveness [--json]` → JSON list of `{machine, status ∈ live|stale|down, last_seen, age_seconds, heartbeat_only}`; text form tab-separated; read-only; exit 0; measured live 2026-09-09: mini `live` age 60.8, Air `live` age 161.0. `plan_claim._tuyere_checkout()` (`plan_claim.py:36-60`) resolves the checkout whose `.venv/bin/python` exists; `plan_claim` runs tuyere as `[<checkout>/.venv/bin/python, "-m", "tuyere.claims", …]` (`:89-100`) | `git -C ../tuyere show b444bdd --stat`; run the verb |
| P7 | config | `config.example.json` keys: `callback_port, default_model, disk_min_free_gb, log_retention_days, notifications{enabled, events{6}, coalesce_window_seconds}, planner_model, pushover, step_timeout_seconds, tailscale_ip, watched_projects`; the mini's `notifications.enabled` is `false` with empty keys (v1.6/v1.7 consistent state) | `python -c` |
| P8 | tests | `tests/test_notifier_server.py` 6 tests (`push` success/timeout/failure, no stranded check, server respond); `tests/test_bellows.py` names `notifier` 74 times (patches of `bellows.notifier.notify_*` — the function NAMES are the contract this plan keeps); `tests/test_depositor.py`, `tests/test_gate_watcher.py` exist (28 tests) | grep |
| P9 | in-flight; class | none; daemon pid 69409 on `9881c37`; `notifier.py`/`bellows.py`/`depositor.py` → shop-infra; HOLDS at admission | `status.py` |

## What this does NOT do

- ⛔ **It does not set the keys or flip `enabled`** — secrets and config are the CEO's; the plan ships dormant on a machine with empty keys, and every refusal it would have made is visible as an INFO line in the daemon log (the record without the page).
- ⛔ **It does not page a rejected push as its own event** — the pause pages it, with the gate's name (change 6).
- ⛔ **It does not persist the dedupe memo** — a restart may re-page an event once; stated, and cheaper than a file the daemon must keep consistent.
- ⛔ **It does not touch tuyere** — the verb landed as a direct edit (`b444bdd`); this plan only calls it.
- **It does not page `plan_complete`/`plan_skipped`/`queue_empty`/`cycle_nudge`** — off by default; a machine may turn one on in its own `config.json`.
- **It does not read Remote Control state** — the ownership signal is the transcript's mtime alone (the CEO's ruling); a session attended from the phone appends the same transcript.
- **It does not change the gate watcher's arming, log or exit** — one return string.

## MUST-PRESERVE

⛔ **Invariants that must still be TRUE afterwards.**

- ⛔ **Every existing `notify_*` function name and signature stays** — `tests/test_bellows.py`'s 74 patches keep binding. Proven by the full suite.
- ⛔ **A pause with no receipt, no transcript, or a failed ownership check PAGES** — silence is never the failure mode. Proven by tests 4–6.
- ⛔ **The gate watcher still arms, polls, logs every state and exits on terminal states or timeout** — only its push line changes. Proven by `tests/test_gate_watcher.py` unchanged and test 11.
- ⛔ **`push` itself is unchanged** — `tests/test_notifier_server.py` passes unchanged.
- ⛔ **The rescan never blocks on tuyere** — the poll has a 15 s timeout and swallows every failure into one WARN. Proven by test 10.
- ⛔ **An unknown event name no longer pages** — `_DEFAULT_EVENTS` closes the `True` default. Proven by test 1.

## Drafting Cycle

**Tier:** **T1** — T-1 fires; T-6 does not. **Walk register:** /Users/marklehn/Developer/eluvian-governance/governance/knowledge/research/walk-register-notifier-coverage-2026-09-09.md
**Walks:** walk 0 pinned (P1–P9 measured on bellows `615d2cc` and tuyere `b444bdd`; clone-diff against `Done/executable-100009.md` (kind) and `Done/executable-100053.md` (layout) run: FACTS, ARTEFACTS, STRUCTURE); `fold_check --save-baseline` ARMED on v0 before any fold; re-saved after every intended edit, emit after the re-save (v2.30). ⛔ **One commit per lens** (§2.7); `lens_order_check` runs with `cycle_check` at every walk close; the commit loop asserts each subject names its lens and gates on the register lint (LESSONS 2026-09-09).

**Closing:** WARM close after walk 3 — the plan for threads 249/245/246, a judged stop. Three walks: 6 → 2 → 0; T1, no panel. Deposit via `ready-`; HOLDS on class shop-infra, the CEO releases (`clear_plan --release-class-hold`). Close acts, the CEO's: the daemon restart; the Pushover keys per shop, `notifications.enabled: true`, one proven push; the Air's `pmset` line; `threads done` for 249, 245, 246 with `--commit bellows:<DEV sha>` after the daemon's push.
- Weak spots:          w1 5 folded — instruction 5 / record 0
- Destruction:         w1 dry
- Vulnerabilities:     w1 1 folded — instruction 1 / record 0
- Integration-record:  w1 dry
- ACID:                w1 dry
- Weak spots:          w2 2 folded — instruction 2 / record 0
- Destruction:         w2 dry
- Vulnerabilities:     w2 dry
- Integration-record:  w2 dry
- ACID:                w2 dry
- Weak spots:          w3 dry
- Destruction:         w3 dry
- Vulnerabilities:     w3 dry
- Integration-record:  w3 dry
- ACID:                w3 dry
**Walk 3 — DRY, all five lenses, one commit per lens. Instruction 0 on a full pass: the WARM close meets the bar (§2) — a judged stop (9 findings over two walks: instruction 8 / record 0 plus the v0 fold f0; yield 6 → 2 → 0). T1: no panel owed.**

## Cycle Manifest
tier: T1
target: notifier.py
class: shop-infra
reads: notifier.py, bellows.py, depositor.py, tools/gate_watcher.py, plan_claim.py, config.example.json, tests/test_notifier_server.py, tests/test_bellows.py, tests/test_gate_watcher.py, knowledge/decisions/Done/executable-100009.md, knowledge/decisions/Done/executable-100053.md
writes: notifier.py, bellows.py, depositor.py, tools/gate_watcher.py, config.example.json, tests/test_notifier_coverage.py, knowledge/mutants/notifier-coverage.json, knowledge/mutants/notifier-coverage.run.txt, knowledge/development/dev-log-notifier-coverage-2026-09-09.md
open_forks: 1. a persisted dedupe memo (a small JSON beside `lifecycle.db`) if a restart re-page proves noisy; 2. quiet hours (a `quiet_hours` window in config, deferring non-urgent events to a morning digest) — the CEO's call after a week of pages; 3. the Claude-side channel's own dedupe (a session that pushes for a plan the daemon also paged before the transcript aged) — measured first
walks: 3
yields: 6, 2, 0
validation: cycle_check=BAR_MET, plan_lint=0_FAIL, fold_check=VACUOUS, propagation_check=DIVERGENT:10
coherence: 3/3 body walks named in the register (9 register rows; walk-token match, NOT row coverage)
fold_baseline: governance/knowledge/decisions/drafts/.executable-bellows-notifier-coverage.md.foldcheck.json

---

## STEP 1 — DEV (one gate, a defaults table, three notifiers, five sites, one poll, one watcher line; one new test sibling; two commits)

> ⛔ **Every item starts by re-establishing the root** — `cd "$(git rev-parse --show-toplevel)" && test -f notifier.py && echo TREE_OK` — HALT unless TREE_OK. ⛔ **The interpreter is `/Users/marklehn/Developer/bellows/.venv/bin/python`, ABSOLUTE**; prove `VENV_OK` with `-c 'import pytest'`. ⛔ **Never run the daemon, `run_plan`, a claim, or a real push** — every test patches `notifier.push` and `subprocess.run`, builds receipts and transcripts under `tmp_path`, and lives under `tests/` (conftest redirects the lifecycle DB only there — a scratch script outside `tests/` minted a production row on 2026-09-09). ⛔ **Never call Pushover** — `requests.post` is patched in every test that reaches `push`. ⛔ **Every commit gates on the FULL suite** and uses `git commit -F <msg-file> -- <paths>` (Rule 75). ⛔ **A module this plan edits is imported by bare name from tests** — assert `notifier.__file__` and `depositor.__file__` are under the worktree in the sibling's first test (thread 243's hazard: a worktree test can bind the canonical checkout's copy).
>
> **Scope:**
> - `notifier.py`
> - `bellows.py`
> - `depositor.py`
> - `tools/gate_watcher.py`
> - `config.example.json`
> - `tests/test_notifier_coverage.py`
> - `knowledge/mutants/notifier-coverage.json`
> - `knowledge/mutants/notifier-coverage.run.txt`
> - `knowledge/development/dev-log-notifier-coverage-2026-09-09.md`
>
> **Item 1 — re-derive P1–P4, P6 and HALT on a mechanism mismatch** (P5, P7–P9 are records; a line-number drift is not a mechanism mismatch). Run the liveness verb once, read-only, and paste its JSON.
>
> **Item 2 — write the failing tests FIRST**, in `tests/test_notifier_coverage.py` — `notifier` imported by bare name after `sys.path.insert(0, <repo root from __file__>)`; `notifier.push` monkeypatched to record calls; receipts under `tmp_path/receipts`, transcripts under `tmp_path/home/.claude/projects/x/<sid>.jsonl` with `HOME` monkeypatched; `init_notifications` called with a config carrying non-empty keys. Tests:
> 0. ⛔ **binding** — `notifier.__file__` and `depositor.__file__` start with the repo root the test resolves from `__file__` (thread 243)
> 1. ⛔ **defaults table** — with `events: {}`, `_event_enabled` is True for the seven ruled events, False for `plan_complete`, `plan_skipped`, `queue_empty`, `cycle_nudge`, and False for `no_such_event`; a config `events: {"plan_complete": true}` turns it on
> 2. ⛔ **`notify_event` refuses with one line each** — disabled → not paged, INFO names `disabled`; event off → `event off`; each refusal calls `push` zero times
> 3. ⛔ **dedupe** — two `notify_event("failure", "p", …)` within the window → one push and one `deduped` line; after the window (monkeypatch `time.time`) → a second push; a different plan or event → its own push
> 4. ⛔ **ownership: attended** — a receipt for `p` naming `sid` and a transcript `sid.jsonl` touched now → `owned_by_live_session("p")` is `(True, …)` naming the session and age; `notify_event("verdict_needed", "p", …, plan_scoped=True)` pushes nothing and logs `owned by session`
> 5. ⛔ **ownership: unattended** — the transcript's mtime set 900 s back (`os.utime`) with `attended_window_seconds: 600` → `(False, "transcript 900s old")` and the page is sent; the newest receipt wins when two exist for the slug
> 6. ⛔ **ownership: absent or broken → page** — no receipt → `(False, "no receipt")`; receipt without a transcript → `(False, "no transcript")`; a receipt file that is not JSON → `(False, "ownership check failed: JSONDecodeError")`; each pages
> 7. ⛔ **not plan-scoped skips ownership** — `notify_class_hold("p", "shop-infra")` pages even with an attended receipt; `notify_watcher_down("air", "stale", 900)` pages; `notify_disk_low(1.2, 5)` pages
> 8. ⛔ **watcher_down episodes** — `notify_watcher_down("air", "stale", …)` twice → one push; `notifier.mark_machine_live("air")` then stale again → a second push
> 9. ⛔ **the sites** — with `notifier.push` recorded: (a) `depositor` holding a shop-infra plan calls `notify_class_hold` once (drive `Depositor._evaluate` or the smallest entry that reaches `:190` on a tmp lane, as `tests/test_depositor.py` does); (b) the stale-checkout hold at wire point A (the `run_plan` fixture from `tests/test_checkout_sync.py` test 9 with `_checkout_is_current` → `(False, …)`) calls `notify_checkout_stale` once; (c) a `worktree_teardown` gate failure carrying `worktree_teardown_push_rejected` produces ONE page, `verdict_needed`, and no `checkout_stale`
> 10. ⛔ **the liveness poll** — `subprocess.run` patched to return the verb's JSON with one `stale` row → `notify_watcher_down` called once for that machine and not for the `live` one; a second poll within `liveness_poll_seconds` does not run the subprocess; patched to raise `TimeoutExpired`, return exit 1, or return `not json` → ONE WARN each, no exception, no page; `plan_claim._tuyere_checkout()` returning None → one WARN
> 11. ⛔ **the gate watcher** — the function at `:150-182` (whatever its name) returns the string `WATCH: push skipped (the daemon is the pager — MACHINE_SETUP v1.7)` and calls `notifier.notify_verdict_request` zero times, with a config whose keys are non-empty
> 12. ⛔ **`config.example.json`** parses; its `events` has exactly the eleven keys with the ruled values; `attended_window_seconds`, `dedupe_window_seconds`, `liveness_poll_seconds` present
> Run the sibling and record the output before implementing (test 0 green by construction, 1–12 red).
>
> **Item 3 — `notifier.py`** as changes 1–5 (the table, `owned_by_live_session`, `_dedupe` and `mark_machine_live`, `notify_event`, the three notifiers plus `notify_disk_low`; the three existing notifiers re-pointed). **Item 4 — the sites** as change 6 and the disk-low replacement; `depositor.py` gains `import notifier` guarded so a standalone import never fails. **Item 5 — the poll** as change 7. **Item 6 — the watcher** as change 8. **Item 7 — `config.example.json`** as change 1 plus the three windows.
> **Item 8 — first commit**, gated in one command on the FULL suite's exit code and path-scoped over `notifier.py bellows.py depositor.py tools/gate_watcher.py config.example.json tests/test_notifier_coverage.py knowledge/mutants/notifier-coverage.json` — seven files, message tagged with the plan id AND `thread 249, thread 245, thread 246`. ⛔ The manifest `{"target": "notifier.py", "mutants": [ … ]}` (keys `name`/`why`/`anchor`/`replacement`/`expect_fail`, anchors count-1, one test per selector) — SEVEN: M1 `_DEFAULT_EVENTS.get(name, False)` → `True` → test 1; M2 ownership inverted (`owned = not owned`) → test 4; M3 `_dedupe` always returns "send" → test 3; M4 `owned_by_live_session`'s except returns `(True, …)` → test 6; M5 `notify_class_hold` passes `plan_scoped=True` → test 7; M6 `mark_machine_live` does not clear the memo → test 8; M7 `notify_event` skips the `_event_enabled` check → test 2. (The poll and the watcher live in `bellows.py`/`tools/gate_watcher.py` — outside the manifest's target; tests 10–11 are their proof.)
> **Item 9 — the mutation run, REDIRECTED** into `knowledge/mutants/notifier-coverage.run.txt` (a Deposit), run IMMEDIATELY after Item 8's commit: `tools/mutation_check.py knowledge/mutants/notifier-coverage.json > knowledge/mutants/notifier-coverage.run.txt 2>&1; echo "exit=$?"` → `exit=0`; last `MUTATION:` line `7 killed, 0 survived, 0 error`; `HEAD:` the FULL sha of Item 8's commit. A survivor is a missing test: fix the test AND re-touch the manifest in ONE further commit, re-run.
> **Item 10 — dev-log** with FIVE literal headings, declared for the gate on the `**Headings:**` line below; no declared section carries a fenced block with `#`-led lines. `## Coverage table` OPENS with P1's value cell pasted verbatim (arm (b) reads it), then the eleven events with their default and their site. `## Cost`: median of three `notify_event` calls on a tmp receipt + transcript (the ownership check's two globs and one stat), and the liveness poll's wall time (the subprocess, measured once against the live verb, read-only).
> **Headings:** `## Pins re-derived (P1, P2, P3, P4, P6)`; `## Failing-first (the sibling red, then green)`; `## Mutation run`; `## Coverage table`; `## Cost`
> **Verbatim:** `## Coverage table` ← P1
> **Item 11 — second commit:** the run file and the dev-log, gated in one command on the FULL suite AND the run file's `MUTATION:` line, path-scoped over those two files. `numstat` over the DEV commits (`<base>..<dev>`) — exactly 9 files; `git reflog -n 6` → 0 amends, 0 resets.
>
> **Deposits:**
> - `knowledge/development/dev-log-notifier-coverage-2026-09-09.md`
> - `knowledge/mutants/notifier-coverage.run.txt`
>
> **Post-conditions:** all thirteen sibling tests pass; the full suite passes at both commits; the run file ends `MUTATION: 7 killed, 0 survived, 0 error`; the five dev-log headings present and `## Coverage table` carries P1's cell verbatim; nine files over the DEV commits.

## STEP 2 — QA (full suite + the notifier dormant on the live config, shown)

> ⛔ **Re-establish the root first** — `cd "$(git rev-parse --show-toplevel)" && test -f notifier.py && echo TREE_OK`; interpreter `/Users/marklehn/Developer/bellows/.venv/bin/python`, ABSOLUTE; prove `VENV_OK`. ⛔ **No real push** — every probe below runs with `notifier.push` monkeypatched or with the live config's `enabled: false`; Pushover is never contacted. ⛔ **The receipt never writes an undefined `tests/…::name` id**; gate evidence elides the `tests/` prefix. Scratch under `/private/tmp/qa-notifier-coverage/`, never under `knowledge/`.
>
> **Item 1 — full suite, REDIRECTED not piped:** `/Users/marklehn/Developer/bellows/.venv/bin/python -m pytest tests/ --tb=short -q > knowledge/qa/evidence/notifier-coverage-suite-2026-09-09.txt 2>&1 || { echo HALT-SUITE-RED; exit 1; }`.
> **Item 2 — the live config, read-only:** `init_notifications` with `/Users/marklehn/Developer/bellows/config.json` (the main checkout's — the worktree has none) → `_notifications_enabled()` is `False`; `notify_event("verdict_needed", "<this plan's slug>", …)` with `push` patched → not paged, the INFO line says `disabled`. Paste. (Dormant by design until the CEO sets the keys — Post-close.)
> **Item 3 — ownership on THIS plan's own receipt:** the live receipt `/Users/marklehn/Developer/bellows/receipts/receipt-executable-bellows-notifier-coverage-<sid>-*.json` (the MAIN checkout's receipts dir — the worktree's is empty; present while the plan runs; pass `receipts_dir` explicitly) and the depositing session's transcript → `owned_by_live_session("executable-bellows-notifier-coverage")` — paste the tuple; state whether the transcript's age is inside the 600 s window at the moment of the probe (either answer is a measurement, not a failure).
> **Item 4 — the liveness verb live, read-only:** run `[<tuyere checkout>/.venv/bin/python, -m, tuyere.control, liveness, --json]` via `plan_claim._tuyere_checkout()` → paste the JSON; both machines expected `live`; then feed a scratch copy with one row edited to `stale` into the poll's parser with `push` patched → one `watcher_down` page for that machine. Paste.
> **Item 5 — the gate watcher on a real plan file:** `tools/gate_watcher.py --status <a Done plan's name>` still prints its status; the push function returns the `daemon is the pager` string. Paste.
> **Item 6 — production writes, stated exactly:** none outside the two evidence files; no push (Pushover never contacted); no lane file; no lifecycle row.
> **Item 7 — receipt** `knowledge/qa/evidence/notifier-coverage-qa-evidence-2026-09-09.md`: numstat over the DEV commits (nine files; `<base>` = the parent of Item 8's commit, `<dev>` = the last DEV commit); the run file's `HEAD:` equal to `git log -1 --format=%H -- knowledge/mutants/notifier-coverage.json`; `git diff <base>..<dev> -- tests/test_notifier_server.py tests/test_bellows.py tests/test_depositor.py tests/test_gate_watcher.py` → EMPTY; `git diff -U0 <base>..<dev> -- notifier.py | grep '^+' | grep -c 'requests.post'` → 0 (`push` untouched); toplevel; `git reflog -n 6` → 0 amends; the five dev-log headings grepped; Items 1–6 each on its own line; the Rule 20 block inside a `## Verification` section. ⛔ Never place a hedging keyword in a ✅ row.
> **Item 8 — commit**, path-scoped and gated: `grep -Eq '^[0-9]+ passed' knowledge/qa/evidence/notifier-coverage-suite-2026-09-09.txt && ! grep -Eq '[0-9]+ (failed|error)' knowledge/qa/evidence/notifier-coverage-suite-2026-09-09.txt && git add knowledge/qa/evidence/notifier-coverage-suite-2026-09-09.txt knowledge/qa/evidence/notifier-coverage-qa-evidence-2026-09-09.md && git commit -F <msg-file> -- knowledge/qa/evidence/notifier-coverage-suite-2026-09-09.txt knowledge/qa/evidence/notifier-coverage-qa-evidence-2026-09-09.md` — exactly two files (`git show --name-only --format= HEAD`).
>
> **Deposits:**
> - `knowledge/qa/evidence/notifier-coverage-suite-2026-09-09.txt`
> - `knowledge/qa/evidence/notifier-coverage-qa-evidence-2026-09-09.md`
>
> **Scope:**
> - `knowledge/qa/evidence/notifier-coverage-suite-2026-09-09.txt`
> - `knowledge/qa/evidence/notifier-coverage-qa-evidence-2026-09-09.md`

Rule 20 banner (byte-exact, inside the QA receipt's VERIFICATION section):

```
============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
```
