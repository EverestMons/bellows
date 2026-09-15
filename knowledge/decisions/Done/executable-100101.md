# bellows — WATCHER_DOWN PAGES ONCE PER MACHINE'S EPISODE: the watched machine joins `watcher_down`'s dedupe key, and `mark_machine_live(machine)` clears that machine's key alone — so a live machine's poll row no longer re-arms a stale machine's page on every liveness poll (thread 331)

**Date:** 2026-09-14 | **Project:** bellows | **Tier:** Small (two notifier functions, one test file extended, one mutation manifest, one dev-log) | **Dispatch Mode:** bellows | **Test Scope:** full-suite (Rule 21 — `notifier.py` is imported by the daemon and much of the suite; `pytest tests/ -q`) | **Execution:** Step 1 (DEV) → Step 2 (QA) | **qa_steps:** 2 | **pause_for_verdict:** after_qa_step | **known_failures:** 0 | **Discharges:** thread 331 | **cycle_tier:** T1

**auto_close:** false

**Post-close:** daemon restart owed — `notifier.py` is daemon-loaded, and the fix is live only after the restart; the CEO restarts after the merge. One bound follow-up, T-3's check — the CEO's act on the Air, where the Planner only reads: after the Air pulls, `cd ~/Developer/GitHub/bellows && .venv/bin/python -m pytest tests/test_notifier_coverage.py -q` under its 3.9.6 venv — 20 passed — then the Air's daemon restart; the Planner pastes the result into `tuyere.threads done 331 --commit bellows:<the DEV's first commit>`. The live check is the next stale episode: one `watcher_down` page per machine per episode in the daemon's log, where P4 shows one per poll.

**Depends on:** thread 331 (filed 2026-09-14; the third plan of the reliability stretch in the CEO's order, after thread 329's classify tool and thread 337's scope_step FAIL); thread 249's ruled dedupe by (machine, plan, event) and thread 251's route of `notify_watcher_down` through `notify_event`'s gate (#100055) — both kept (P5). The defect's origin, measured (P7): #100054 (`halted-executable-100054.md`, `f5c82a4`, 2026-09-09 — the plan that built the notifier's dedupe; its code shipped, its record closed by #100055) keyed `watcher_down` by the WATCHED machine, `(machine, "-", "watcher_down")`, and `mark_machine_live(machine)` popped exactly that key; #100055 (`cfb968e`, the same day, thread 251) routed `notify_watcher_down` through `notify_event`, whose key's first field is the paging host, passed only the status as `detail_key`, and rewrote `mark_machine_live` to clear by the host's prefix — the machine left the key. Clone origin by kind: `Done/executable-100055.md` (Done 2026-09-09, T1, target `notifier.py`), the newest completed plan to change `notify_watcher_down`; the conventions carried from the newest shipped T1 plan, `Done/executable-100098.md` (2026-09-14); the newest plan to touch `notifier.py` at all is #100097 (`8b52344`, 2026-09-13, a T2 lifecycle plan whose record #100098 closed).

**Tier computed (§1):** **T1** — T-3 fires: the notifier runs in both machines' daemons, the Air's venv 3.9.6 beside the mini's 3.12.14, where the suite runs (P6). T-1 does not (one module and its test file, a localized change); T-6 does not (no gate, doctrine or contract changes — the ruled event table and the ruled key's shape stand, P5); T-2, T-4, T-5 and T-7 do not; T-8 does not (a structure clone of #100055's notifier-change shape).

## CEO Context

When one machine's watcher goes stale while the other stays live, you get a watcher-down page every five minutes instead of one per episode — measured in the mini's log this morning at 09:20, 09:25 and 09:30, again at 09:35 after the restart, and on 2026-09-11 at 11:22 and 11:27. The dedupe key names the machine sending the page, not the one being watched, and a live machine's poll row clears every machine's key, so the one-hour window never holds. It is a regression: the notifier as first built on 2026-09-09 keyed this page by the watched machine, and the same day's change that routed it through the one gate lost the machine from the key. This plan puts the watched machine in the key and lets a live row clear only its own machine; two machines stale at once then page once each, where today the second is swallowed behind the first. The class is shop-infra, so it holds for your release; after the merge, your restart makes it live.

## What this changes

1. **`notifier.py`**:
   - `notify_watcher_down(machine, status, age_seconds)` passes `detail_key=f"{machine}:{status}"` in place of `detail_key=status` (P1), so the key `notify_event` builds is (paging host, `-`, `watcher_down`, `<machine>:<status>`); its docstring says so.
   - `mark_machine_live(machine)` pops only the keys whose first three fields are (paging host, `-`, `watcher_down`) and whose detail names that machine: `k[3].rsplit(":", 1)[0] == machine` — a status never carries a colon, so the machine is everything before the last one (P4's machine names carry none either); its docstring states the key form.
   - Not changed: `notify_event`, `_dedupe`, the window, every other event's key.
2. **`tests/test_notifier_coverage.py`** (P3):
   - test_8's route check asserts `detail_key == "air:stale"` — it pinned `"stale"`; the one edit this plan makes to an existing assertion.
   - New, after test_8: (8a) air stale and mini live, the stale row first, over two polls → one page; (8b) the live row first → one page; (8c) air and mini stale at once, over two polls → two pages; (8d) both stale (two pages), then `mark_machine_live("air")`, then both stale again → three pages — air's new episode pages, mini's stays deduped; (8e) the daemon's own loop — `_poll_liveness` twice over the rows [air stale, mini live], `_liveness_last_poll` set to 0 before EACH poll (the interval gate, P2, otherwise skips the second poll, and the test passes on the base), its setup cloned from test_10 → one page. Each new test patches `notifier.push` and counts its calls — the pages it asserts (P3).
   - Red on the base: test_8 and 8a–8e; the other fourteen tests unchanged and green.
3. **`knowledge/mutants/watcher-down-dedupe.json`** — `target` `notifier.py`, three mutants, each `expect_fail` a node id: (m1) the machine dropped from the key → 8c; (m2) a live row clears every machine's key → 8a; (m3) a live row clears nothing → 8d.
4. **The dev-log** `knowledge/development/dev-log-watcher-down-dedupe-2026-09-14.md`.
5. **Not changed:** `bellows.py` — `_poll_liveness` already passes each row's machine to both functions (P2); the config; tuyere's liveness; the ruled event table.

## Why this exists

Thread 331 measured it and named the mechanism, and both re-derive at `61794c4` (P1, P2, P4). The origin is a regression (P7): the notifier as #100054 built it keyed `watcher_down` by the watched machine, and #100055's routing through the one gate moved it onto `notify_event`'s key — right for a plan's events, whose subject is the plan and whose first field is the paging host (thread 249's ruled key, P5), but not for `watcher_down`, whose subject is another machine. The fix keeps the gate and the ruled key's shape, and puts the subject back, in the detail field beside the status.

## What this does NOT do

- It does not change the dedupe window: one machine's episode longer than 3600 s pages again each window, as today.
- It does not put the machine in the log line — `notifier: watcher_down None paged` names none; the page's message does (P1).
- It does not change any other event's dedupe, the ruled event table, the poll, or tuyere.
- It does not persist the memo: a daemon restart empties it, so a machine stale across a restart pages once more — as at 09:35:38 (P4).

## MUST-PRESERVE

- ⛔ **Every page passes through `notify_event`** (test_8's route check).
- ⛔ **A machine's new stale episode after it was seen live pages once** (test_8, 8d).
- ⛔ **The ruled key's shape — (paging host, plan, event, detail) — is unchanged;** only `watcher_down`'s detail carries the machine.
- ⛔ **No other event's dedupe changes:** every other test in the file passes unedited.
- ⛔ **Every `expect_fail` is a node id,** and the mutation run is redirected into its deposit, never piped.
- ⛔ **Test code runs under pytest inside `tests/` or not at all** (bellows `CLAUDE.md`, *Test code*; thread 313).
- ⛔ **The thread-262 stop:** a QA step that must change production code STOPS and requests a verdict.

## Numbers discipline — measured 2026-09-14 by the Planner (bellows `61794c4`, governance `066c0d5c`)

| # | pin | value | how to re-derive |
|---|---|---|---|
| P1 | ⛔ the notifier | `notifier.py`: `_config` :24, `_dedupe_memo` :29, `init_notifications` :54; `_dedupe(key)` :191–199, its window `_config.get("dedupe_window_seconds", 3600)` :193; `mark_machine_live(machine)` :202–207 pops every key with `k[:3] == (hostname, "-", "watcher_down")`, its argument unused; `notify_event(event, plan_slug, title, message, priority=0, plan_scoped=True, detail_key="")` :259–288, the key `(socket.gethostname(), plan_slug or "-", event, detail_key)` :274–275, the log line `notifier: {event} {plan_slug} paged` :287; `notify_watcher_down(machine, status, age_seconds)` :399–410 passes `detail_key=status` :409, its message carrying the machine :408 | `sed -n '24,29p;191,207p;259,288p;399,410p' notifier.py` |
| P2 | ⛔ the poll | `bellows.py` `_poll_liveness` :3482–3524: at most once per `liveness_poll_seconds` (default 300, :3490); each row stale or down → `notifier.notify_watcher_down(machine, status, age)` :3521–3522, each row live → `notifier.mark_machine_live(machine)` :3523–3524 | `sed -n 3482,3524p bellows.py` |
| P3 | ⛔ the tests | `tests/test_notifier_coverage.py`: test_8 `test_8_watcher_down_episodes` :343–385, one machine, its route check asserting `detail_key == "stale"` :385; test_10 `test_10_liveness_poll` from :494 — `_poll_liveness` with `bellows.server.ResponseServer`, `bellows.depositor.Depositor`, `bellows.plan_claim._tuyere_checkout` and `bellows.subprocess.run` patched; `tests/conftest.py` `_clear_notifier_dedupe` :40–45 clears the memo around every test; no test pins the `paged` log line; `notifier.push` posts to Pushover with `requests.post`, no conftest fixture patches it, and six of the file's fifteen tests (3–8) patch it themselves | the files at those lines; `grep -nF 'def push' -A20 notifier.py` |
| P4 | ⛔ the evidence | the daemon's logs, read today: `logs/terminal/bellows-2026-09-11.log` (the daemon that ran from 2026-09-11 to this morning) holds `notifier: watcher_down None paged` at 11:22:19 and 11:27:21 on 2026-09-11 and at 09:20:44, 09:25:49 and 09:30:53 this morning — one per poll; `logs/terminal/bellows-2026-09-14.log` (the restarted daemon) holds 09:35:38, its first poll, and none since; `tuyere.control liveness --json` at 13:26: `Marks-Mac-mini.local` and `Marks-MacBook-Air-2.local`, both `live`; the mini's `config.json`: `notifications.dedupe_window_seconds` 3600, `liveness_poll_seconds` unset (the default 300) | `grep -F watcher_down logs/terminal/bellows-2026-09-11.log logs/terminal/bellows-2026-09-14.log`; the liveness command; the one key read alone |
| P5 | the rulings kept | thread 249 (the CEO's Pushover rulings of 2026-09-09): dedupe by (machine, plan, event), the machine the paging host; thread 251 → #100055 (`cfb968e`): `notify_watcher_down` through `notify_event`'s gate, `plan_scoped=False` | `tuyere.threads show 249`; `show 251` |
| P6 | class; in flight; interpreters; the suite | the writes → **shop-infra** (bellows, the project floor), HOLDS at admission for the CEO's release; in flight at drafting: nothing — thread 329's plan held for release and thread 337's in drafting, both with writes disjoint from these; the bellows venv 3.12.14, `/usr/bin/python3` 3.9.6, the Air's venv 3.9.6; the full suite at `61794c4`: 2364 passed, 2 skipped (#100098's QA) | `status.py`; `python -V`; the suite |
| P7 | ⛔ the regression | at `f5c82a4` (#100054): `mark_machine_live(machine)` :201–203 pops `(machine, "-", "watcher_down")`, and `notify_watcher_down` :379–384 says it "Uses a machine-keyed 3-tuple dedupe"; at `cfb968e` (#100055): `mark_machine_live` :201–206 clears every key with `k[:3] == (hostname, "-", "watcher_down")`, and `notify_watcher_down` :382–393 calls `notify_event(…, detail_key=status)` — the watched machine gone from the key | `git show f5c82a4:notifier.py`; `git show cfb968e:notifier.py` |

DEV re-derives P1–P3 in Item 1 and HALTs on a mechanism mismatch; P4–P7 are the drafting record.

## Drafting Cycle

**Tier:** **T1** — T-3 fires. **Walk register:** /Users/marklehn/Developer/eluvian-governance/governance/knowledge/research/walk-register-watcher-down-dedupe-2026-09-14.md
**Walks:** walk 0 pinned (P1–P7 measured on bellows `61794c4`; clone-diff against `Done/executable-100055.md` and the newest shipped `Done/executable-100098.md` run: FACTS, ARTEFACTS, STRUCTURE; the fix prototyped in a scratch archive of `61794c4`; no walk-0 scout — T1, the Planner's call); `fold_check --save-baseline` ARMED on v0 before any fold, re-saved after every intended edit; every lens commit through `/Users/marklehn/Developer/bellows/scripts/lens_commit.py`, invoked directly, its exit read — ~~with its output whole~~ *(struck before the close: walk 2's five commits filtered the eight path-WARN echo lines from the display, declared as it ran, and plan_lint's whole WARN set was read after the walk — the register's* Before the close*)*; no lens or walk number in any `--desc`; `lens_order_check` after every lens commit, and before the receipt on a copy of the draft in a scratch project-shaped repository with history.

- Weak spots:          w1 3 folded — instruction 3 / record 0; 3 pre-existing, 0 fold-introduced; w2 dry
- Destruction:         w1 dry; w2 dry
- Vulnerabilities:     w1 dry; w2 dry
- Integration-record:  w1 1 folded — instruction 0 / record 1; 1 pre-existing, 0 fold-introduced; w2 dry
- ACID:                w1 1 folded — instruction 0 / record 1; 1 pre-existing, 0 fold-introduced; w2 dry
**Closing:** WARM close after walk 2 — BAR MET (T1), thread 331's plan, on a judged stop: walk 2 dry on all five lenses. Two walks, findings by class — walk 1: 5 (instruction 3 / record 2), walk 2: 0; the manifest's `yields` counts the instruction class alone. Walk 1 made the new tests patch `notifier.push` and said so where the preamble had promised it of every test, named the Air check's checkout and its actor, and reset 8e's poll clock before each poll — without the reset the test passed on the base, measured — then counted the seven pins on the Walks line and stated a restart's extra page as a limit; direction verdict after walk 1: PROCEED — the clone origin, the mechanism and the regression premise stand. Residue beyond walk 2, two record-class repairs before the close: c1, one method phrase made literal — walk 2's display filtered eight path-WARN echo lines, and the whole WARN set, read after the walk, hid no change; c2, the origin split on walk 1's three folded lens entries. Origin (diagnostic): 0 of 7 folds fold-introduced. No panel (T1): the stop rests on this enumeration and the closing-record re-read. Every lens commit through `lens_commit.py`, its exit read; the close through `close_cycle.py`. Deposit via `ready-`, the receipt first, then the class — parsed by thread 329's tool once it has merged, else read as text only at a CEO ruling; HOLDS on class shop-infra, the CEO releases; every pause is the Planner's verdict; after the merge the CEO restarts the daemon, runs the file's tests on the Air and restarts it there, and the Planner closes thread 331.

## Cycle Manifest
tier: T1
target: notifier.py
class: shop-infra
reads: notifier.py, bellows.py, tests/test_notifier_coverage.py, tests/conftest.py, knowledge/decisions/halted-executable-100054.md, knowledge/decisions/Done/executable-100055.md, logs/terminal/bellows-2026-09-11.log, logs/terminal/bellows-2026-09-14.log
writes: notifier.py, tests/test_notifier_coverage.py, knowledge/mutants/watcher-down-dedupe.json, knowledge/mutants/watcher-down-dedupe.run.txt, knowledge/development/dev-log-watcher-down-dedupe-2026-09-14.md, knowledge/qa/evidence/watcher-down-dedupe-qa-receipt-2026-09-14.md, knowledge/qa/evidence/watcher-down-dedupe-suite-2026-09-14.txt
mutants: knowledge/mutants/watcher-down-dedupe.json
open_forks: 1. the log line names no machine for `watcher_down` (`notifier: watcher_down None paged`) — the page's message does; 2. one machine's episode longer than the 3600 s window pages again each window — the docstring's "exactly once" holds per window, not per episode
walks: 2
yields: 3, 0
validation: cycle_check=BAR_MET, plan_lint=0_FAIL, fold_check=VACUOUS, propagation_check=DIVERGENT:23
coherence: 2/2 body walks named in the register (5 register rows; walk-token match, NOT row coverage)
fold_baseline: governance/knowledge/decisions/drafts/.executable-bellows-watcher-down-dedupe.md.foldcheck.json

---

## STEP 1 — DEV (two notifier functions, one assertion and five tests, the mutation run; two commits)

> ⛔ **Every item starts by re-establishing the root** — `cd "$(git rev-parse --show-toplevel)" && test -f gates.py && echo TREE_OK` — HALT unless TREE_OK. ⛔ **The interpreter is `/Users/marklehn/Developer/bellows/.venv/bin/python`, ABSOLUTE.** ⛔ Never run the daemon, `run_plan`, a claim or a gate outside a test; the live `lifecycle.db` is never opened by this step, and no new test pages — each patches `notifier.push` and counts its calls (P3). ⛔ Test code runs under pytest inside `tests/` or not at all (bellows `CLAUDE.md`, *Test code*): no helper is called from `python -c`. `T=$(mktemp -d /tmp/watcher-down-dedupe.XXXXXX)` for scratch, removed at the end.
>
> **Scope:**
> - `notifier.py`
> - `tests/test_notifier_coverage.py`
> - `knowledge/mutants/watcher-down-dedupe.json`
> - `knowledge/mutants/watcher-down-dedupe.run.txt`
> - `knowledge/development/dev-log-watcher-down-dedupe-2026-09-14.md`
>
> **Item 1 — re-derive P1, P2 and P3 and HALT on a mechanism mismatch** (a line-number drift is not one, and a count that moved is a record — paste it; a `watcher_down` detail key already carrying the machine, a `mark_machine_live` that already reads its argument, or a `_poll_liveness` that no longer passes each row's machine IS one). Paste each pin's re-derived line beside it.
> **Item 2 — the failing tests FIRST:** test_8's assertion and 8a–8e as *What this changes* 2; run the file on the unedited code and paste the red summary line — `6 failed, 14 passed`.
> **Item 3 — the edits** as *What this changes* 1; the file green — `20 passed` — then the FULL suite green: predicted the base's count plus five, `2369 passed, 2 skipped` on `61794c4` (the run supersedes the prediction; HALT only on a non-zero failure count). An existing test failing here is a HALT, never an edit — test_8's one assertion is this plan's declared edit, and no other.
> **Item 4 — first commit**, gated on the FULL suite AND the pre-check with the stage flag, path-scoped, run as ONE command — the verdict read checks each commit's place in the step's transcript: `/Users/marklehn/Developer/bellows/.venv/bin/python -m pytest tests/ -q && /Users/marklehn/Developer/bellows/.venv/bin/python tools/check_deposit.py /Users/marklehn/Developer/bellows/knowledge/decisions/in-progress-executable-<id>.md 1 --wt "$(git rev-parse --show-toplevel)" --expect-missing knowledge/development/dev-log-watcher-down-dedupe-2026-09-14.md knowledge/mutants/watcher-down-dedupe.run.txt && git add notifier.py tests/test_notifier_coverage.py knowledge/mutants/watcher-down-dedupe.json && git commit -F <msg-file> -- notifier.py tests/test_notifier_coverage.py knowledge/mutants/watcher-down-dedupe.json` — three files (the manifest rides this commit so the mutation run's `HEAD:` archive contains it); the message tagged with the plan id and `thread 331`.
> **Item 5 — the mutation run, REDIRECTED into `knowledge/mutants/watcher-down-dedupe.run.txt` (a Deposit):** `/Users/marklehn/Developer/bellows/.venv/bin/python tools/mutation_check.py knowledge/mutants/watcher-down-dedupe.json > knowledge/mutants/watcher-down-dedupe.run.txt 2>&1`; the last line must read `MUTATION: 3 killed, 0 survived, 0 error` — a survivor is a test to write, not a mutant to delete.
> **Item 6 — the dev-log** `knowledge/development/dev-log-watcher-down-dedupe-2026-09-14.md` under the four headings declared below; `## Pins re-derived (P1, P2, P3)` opens with P2's value cell pasted verbatim, whole, to its last character — ⛔ the cell ends with the characters `:3523–3524`; paste through them, then stop. Under `## Failing-first (red, then green)` the red line and the two green lines (the file, the full suite); under `## The pages counted (8a, 8c, 8d, 8e)` the four PASSED lines of a `-v` run over those four node ids — each test counts the pages it asserts, and nothing in this step prints them otherwise; under `## Mutation run` the run file's last line. **Second commit**, gated on the FULL suite and the pre-check bare (`… tools/check_deposit.py … 1 --wt "$(git rev-parse --show-toplevel)"`, no stage flag — the run file and the dev-log now exist), run as one command, path-scoped to the run file and the dev-log. Last act: `[ -n "$T" ] && [ -d "$T" ] && rm -rf "$T"`.
> **Headings:** `## Pins re-derived (P1, P2, P3)`; `## Failing-first (red, then green)`; `## The pages counted (8a, 8c, 8d, 8e)`; `## Mutation run`
> **Verbatim:** `## Pins re-derived (P1, P2, P3)` ← P2
>
> **Deposits:**
> - `knowledge/mutants/watcher-down-dedupe.json`
> - `knowledge/mutants/watcher-down-dedupe.run.txt`
> - `knowledge/development/dev-log-watcher-down-dedupe-2026-09-14.md`
>
> **Post-conditions:** test_8 and 8a–8e green with the file's other fourteen; the FULL suite green with no `failed`; the mutation run's last line as Item 5 states it; two DEV commits — the first carrying the three files, the second the run file and the dev-log; the dev-log's four headings present as full lines with P2's cell whole; `git status --porcelain` empty after the second commit.

## STEP 2 — QA (full suite; the pages counted through their tests; the receipt)

> ⛔ **Every item starts by re-establishing the root** — `cd "$(git rev-parse --show-toplevel)" && test -f gates.py && echo TREE_OK` — HALT unless TREE_OK. Interpreter ABSOLUTE; read-only beyond the two evidence files; `T=$(mktemp -d /tmp/watcher-down-dedupe-qa.XXXXXX)`.
>
> **Item 1 — the full suite REDIRECTED not piped:** `/Users/marklehn/Developer/bellows/.venv/bin/python -m pytest tests/ --tb=short -q > knowledge/qa/evidence/watcher-down-dedupe-suite-2026-09-14.txt 2>&1`; the summary line quoted in the receipt as `N passed` with the skips named as `two skips (test_gate_watcher live-DB; test_fallback_live_wal_window version gate)` — never the word the Rule 20 block scans for.
> **Item 2 — the pages, counted through their tests:** `/Users/marklehn/Developer/bellows/.venv/bin/python -m pytest -v` over the six node ids of test_8 and 8a–8e, and paste the six PASSED lines. State that the daemon which ran STEP 1 loaded the old `notifier.py` (the restart is owed after close). No call into the module outside pytest, and nothing pages.
> **Item 3 — production writes, stated exactly:** none outside the two evidence files; `$T` removed; no lane file, no live lifecycle row, no daemon act, no page.
> **Item 4 — receipt** `knowledge/qa/evidence/watcher-down-dedupe-qa-receipt-2026-09-14.md`: `numstat` over the DEV commits (`<base>..<dev>`, five files); a `## Verification` table with one row per Item 1–3, each quoting the line it rests on — ⛔ the status cell holds exactly one token (`✅`) and no positive row's text carries a hedging keyword; then RUN the canonical Rule 20 block (`/Users/marklehn/Developer/eluvian-governance/RULE_20_SELF_CHECK_BLOCK.md`) with `plan_slug: watcher-down-dedupe-2026-09-14`, `qa_report_path` and `evidence_dir` absolute under `$(git rev-parse --show-toplevel)/knowledge/qa/evidence/`, `required_evidence_files: ["watcher-down-dedupe-suite-2026-09-14.txt"]`, and APPEND its stdout — the banner `Rule 20 — QA Self-Check Results` and the closing `PASSED — SELF-CHECK PASSED` line are the block's output, never hand-authored; a `FAILED` stdout goes into the receipt and the step STOPS (thread 262).
> **Item 5 — commit**, path-scoped and gated, run as one command: `grep -Eq '^[0-9]+ passed' knowledge/qa/evidence/watcher-down-dedupe-suite-2026-09-14.txt && ! grep -Eq '[0-9]+ (failed|error)' knowledge/qa/evidence/watcher-down-dedupe-suite-2026-09-14.txt && /Users/marklehn/Developer/bellows/.venv/bin/python tools/check_deposit.py /Users/marklehn/Developer/bellows/knowledge/decisions/in-progress-executable-<id>.md 2 --wt "$(git rev-parse --show-toplevel)" && git add knowledge/qa/evidence/watcher-down-dedupe-qa-receipt-2026-09-14.md knowledge/qa/evidence/watcher-down-dedupe-suite-2026-09-14.txt && git commit -F <msg-file> -- knowledge/qa/evidence/watcher-down-dedupe-qa-receipt-2026-09-14.md knowledge/qa/evidence/watcher-down-dedupe-suite-2026-09-14.txt`. ⛔ A QA step that must change production code STOPS and requests a verdict (thread 262).
>
> **Deposits:**
> - `knowledge/qa/evidence/watcher-down-dedupe-qa-receipt-2026-09-14.md`
> - `knowledge/qa/evidence/watcher-down-dedupe-suite-2026-09-14.txt`
>
> **Scope:**
> - `knowledge/qa/evidence/watcher-down-dedupe-qa-receipt-2026-09-14.md`
> - `knowledge/qa/evidence/watcher-down-dedupe-suite-2026-09-14.txt`
>
> **Post-conditions:** the suite file's summary line is `N passed, 2 skipped` with N at least the DEV's count and no `failed`; Item 2's six PASSED lines pasted; the receipt's `## Verification` table has three rows and closes with the block's own PASSED line; one QA commit carrying the two evidence files.
