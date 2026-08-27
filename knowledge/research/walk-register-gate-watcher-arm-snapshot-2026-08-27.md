# Walk register — `gate-watcher-arm-snapshot-2026-08-27` (bellows)

**schema_version:** `0.3`

**Plan:** `bellows/knowledge/decisions/drafts/executable-gate-watcher-arm-snapshot.md`
**Tier:** T1 (Small — one pure helper + loop threading + additive tests; class shop-infra). **Panel: none.**
**Opened:** 2026-08-27

---

## Walk 0 — context pin (REAL, measured 2026-08-27)

1. **The defect, measured live before authoring:** a watcher armed while a verdict-request file is still on disk reports that pause as newly observed. Observed on the shop's shell watcher this session; the arm-time snapshot guard fixed it and produced the audit pair `arm-time pending ignored: verdict-request-570-step-1.md` then `PAUSED id=570 — NEW verdict-request: verdict-request-570-step-2.md`.
2. **Scope priced HONESTLY at walk 0, and narrower than the opening thread text.** Thread 20 said "the same race on any re-arm" without pricing the consequence. Measured: `main` returns only on a TERMINAL phase or timeout — there is NO pause-exit arm — so this cannot cause a false termination or a missed pause; and `deposit_receipt._spawn_watcher` (`tools/deposit_receipt.py:55-63`, called at `:119`) spawns at DEPOSIT, when no verdict-request can exist, so the SHIPPED path is unaffected. What remains is a hand-run mid-plan writing a phantom pause→resume pair into its own log. Real, and small. The thread text is corrected by the Planner at close (price-inherited-severity-labels, applied to a label the Planner itself wrote).
3. **Design:** the fix is a LOOP concern, not a state-read concern. `read_state` and `--status` must keep reporting the true instantaneous state — a request file present genuinely means the plan is awaiting a verdict at that instant. So the change is a pure helper `judge_watch_line(prev, cur, arm_pending) -> (line, new_arm_pending)` above `main`, plus snapshot threading in the loop. `read_state`/`judge_transition` signatures untouched; all 16 existing tests must stay green unmodified.
4. **The guard's own failure mode is named up front:** a snapshot that never clears would swallow every subsequent pause — worse than the bug. Clearing on an empty pending set is therefore a MUST-PRESERVE with its own test and its own live probe assertion.
5. **Baselines:** `tests/test_gate_watcher.py` collects 16; full suite 1582 (exec-570 QA).

⚠️ Walk 0 carries no fold rows. Walks 1+ appended AFTER the draft exists, from real passes.

---

## Walk 1 — five-lens sequential walk (post-draft, real)

| id | walk | lens | sub_question | origin | finding | pre_fold_text | resolution |
|---|---|---|---|---|---|---|---|
| w1-1 | 1 | Weak spots | can the snapshot be seeded from an unreadable poll? | pre-existing | the draft seeded from the loop's first iteration, but that read can return `None` (db-unreadable); seeding from it sets the snapshot to `None` permanently and silently disables the guard | `arm_pending = set(cur["pending"]) if (cur and cur.get("pending")) else None`, then thread arm_pending through judge_watch_line on every iteration | folded: an explicit `armed = False` flag; seed from the first READABLE poll (`if not armed and cur is not None`), before the line is computed, leaving `prev` bookkeeping untouched so the first readable poll still earns the armed-over line |
| — | 1 | Destruction | — | — | DRY — helper is pure; loop keeps its TERMINAL/timeout arms, `prev` bookkeeping and `_log_line` untouched; no new CLI surface; log dir stays untracked | — | no fold |
| w1-2 | 1 | Vulnerabilities | how does the helper compare an absent snapshot? | pre-existing | the draft's condition would have compared `set(cur["pending"])` against a possibly-`None` snapshot; `set() == None` is False so it would work BY ACCIDENT, and the empty-vs-absent distinction could drift under a later edit | behaviour stated as one clause: when `arm_pending is not None and set(cur["pending"]) == arm_pending` (implicit in an unordered prose description) | folded: the four cases enumerated in explicit ORDER (`cur is None` → snapshot survives; no `pending` → cleared; matching set → armed-over; otherwise → normal), with an explicit `is not None` branch mandated |
| — | 1 | Integration-record | — | — | DRY — manifest reads/writes complete; thread-20 closure and its scope correction declared as Planner close acts (sandbox split) | — | no fold |
| — | 1 | ACID | — | — | DRY — two pathspec-limited commits, toplevel-first, each with a file-count assert | — | no fold |

**Walk 1 total: 2 findings (instruction 2 / record 0), folded. Direction verdict: PROCEED — the loop-only seam held.**

---

## Walk 2 — five-lens sequential walk (real)

| id | walk | lens | sub_question | origin | finding | pre_fold_text | resolution |
|---|---|---|---|---|---|---|---|
| w2-1 | 2 | Weak spots | can the log assertions tell the two QA runs apart? | pre-existing | both loop runs appended to the SAME `logs/watch/<name>.log`, so `grep -cF "awaiting-verdict"` → 0 "for this run's window" is unreadable after the second run appends — the ambiguous-check class (569 w2-1's sibling) | `/usr/bin/grep -cF "awaiting-verdict" <log>` → 0 for this run's window | folded: `rm -f "$LOG"` before the run and the whole probe collapsed to ONE run, so every assertion reads a single clean window |
| — | 2 | Destruction | — | — | DRY — probe writes only to a `mktemp -d` scratch and an untracked log; the real `verdicts/pending/` is never touched (the probe passes `--pending-dir "$SCRATCH"`), so this plan's OWN live verdict-request cannot interfere | — | no fold |
| w2-2 | 2 | Vulnerabilities | does the later-pause probe actually exercise a later pause? | pre-existing | ⚠️ **the probe as written could not have proven its claim.** It removed step-1, touched step-2, then started a FRESH loop — which arms OVER step-2 and correctly prints the armed-over line. The assertion expected a normal `awaiting-verdict` line, so the probe would have failed, or worse, been "fixed" by weakening the assertion. The discriminating sequence requires the file to change while the watcher is ALIVE | `3. **A genuine later pause still fires (the guard's failure mode):** with the loop's snapshot semantics, rm "$SCRATCH/verdict-request-$PID-step-1.md" && touch "$SCRATCH/verdict-request-$PID-step-2.md", re-run the 1-minute loop -> the log carries a normal awaiting-verdict line naming pending=verdict-request-$PID-step-2.md. **This is the probe that proves the guard did not simply mute pauses.**` (complete pre-image bytes, no ellipsis) | folded: one backgrounded run with a MID-FLIGHT swap (sleep 10 → rm step-1 → sleep 8 so the snapshot clears → touch step-2 → sleep 10 → wait), with three greps over the single clean log and an explicit HALT instruction if the later-pause count reads 0 |
| — | 2 | Integration-record | — | — | DRY — manifest, deposits and scope agree on the six files | — | no fold |
| — | 2 | ACID | — | — | DRY | — | no fold |

**Walk 2 total: 2 findings (instruction 2 / record 0), folded. Bar NOT met.**

---

## Walk 3 — five-lens sequential walk (real)

| id | walk | lens | sub_question | origin | finding | pre_fold_text | resolution |
|---|---|---|---|---|---|---|---|
| — | 3 | Weak spots | — | — | DRY — the swap timing was traced against a 3s interval: polls over the armed-over state (line once, then silence), a clearing poll when the set empties, then a normal pause line for step-2; the `grep -c` for the armed-over line is exactly 1 because later unchanged polls return None | — | no fold |
| — | 3 | Destruction | — | — | DRY | — | no fold |
| — | 3 | Vulnerabilities | — | — | DRY — the plan's own real verdict-request lives in the REAL pending dir while the probe reads only `$SCRATCH`; no cross-talk | — | no fold |
| — | 3 | Integration-record | — | — | DRY | — | no fold |
| — | 3 | ACID | — | — | DRY | — | no fold |

**Walk 3 total: 0 findings — DRY.**

---

## Walk 4 — five-lens sequential walk (real)

| id | walk | lens | sub_question | origin | finding | pre_fold_text | resolution |
|---|---|---|---|---|---|---|---|
| w4-1 | 4 | Weak spots | does test 7 leave the agent to invent a call convention? | pre-existing | the instruction said "invoke `main` with `--status`" while the file ALREADY carries that convention at `tests/test_gate_watcher.py:121-127` (`test_status_oneshot`: `main(["gate_watcher.py", name, "--status", "--db-path", db_path])` with `capsys`); an invented variant is the clone-drift class | `build a tmp DB + pending dir and invoke main with --status` | folded: the existing test cited by file:line with its exact call shape, instructing the agent to CLONE it and add `--pending-dir` |
| — | 4 | Destruction | — | — | DRY | — | no fold |
| — | 4 | Vulnerabilities | — | — | DRY — `--status` returns before `os.makedirs(_WATCH_DIR)`, so the status test creates no log dir | — | no fold |
| — | 4 | Integration-record | — | — | DRY — test count reconciled to 24 (16 baseline + 8) across the targeted-run line, the deposits block and the commit message after test 6b was added | — | no fold |
| — | 4 | ACID | — | — | DRY | — | no fold |

**Walk 4 total: 1 finding (instruction 1 / record 0), folded.**

---

## Walk 5 — five-lens sequential walk (confirming pass, real)

| id | walk | lens | sub_question | origin | finding | pre_fold_text | resolution |
|---|---|---|---|---|---|---|---|
| — | 5 | Weak spots | — | — | DRY — every Task B anchor asserted unique; the resume probe keys on `pre-existing`, a string present only post-edit | — | no fold |
| — | 5 | Destruction | — | — | DRY | — | no fold |
| — | 5 | Vulnerabilities | — | — | DRY — no absence claim without a positive control; the guard's own failure mode carries both a unit test (test 3) and a live assertion with a HALT arm | — | no fold |
| — | 5 | Integration-record | — | — | DRY — manifest finalization declared as the close act; the fold list ×5 matches the draft's diff | — | no fold |
| — | 5 | ACID | — | — | DRY | — | no fold |

**Walk 5 total: 0 findings — DRY. Two dry walks (3 and 5) around a single small w4 instruction fold — BAR MET.**

---

## Conformance (§5) — recorded at the freeze from ACTUAL runs

- **Fold verification (2026-08-27, `/usr/bin/grep -cF` on the draft):** w1-1 landed ×1 (`first READABLE poll, not from the first iteration`); w1-2 landed ×1 (`the snapshot survives an unreadable poll UNCHANGED`); w2-1+w2-2 landed ×1 (`swap performed MID-RUN`); test 6b landed ×1 (`test_db_unreadable_preserves_snapshot`); w4-1 landed ×1 (`tests/test_gate_watcher.py:121-127`). Superseded text verified ×0: `re-run the 1-minute loop`, and the old first-iteration seeding expression.
- **Structure:** `grep -cE '^## STEP '` → 2.
- **run_check runs at the freeze (2026-08-27, all branched-on, lint at the DEPOSIT path via a `lintmirror-` copy in the real `decisions/`):** `lint` → `VERDICT=PASS — exit 0` (8 PASS rows; the advisory (o2) relative-path WARNs are the house Deposits form); `cycle` → `VERDICT=PASS — BAR_MET`; `register` → first run `VERDICT=FAIL` (row w2-2 `truncated_pre_fold_text` — the pre_fold_text quoted an ellipsis, which reads as truncated pre-image bytes; complete bytes substituted), re-run `VERDICT=PASS — 1 CONFORMANT, 0 UNCONFORMANT`. Same failure-then-fix as the 571 register: the ellipsis-in-pre_fold_text trap is now twice-measured and belongs in the authoring habit, not the lint loop.
- **fold_check (EARNED, not authored):** v0 reconstructed by reversing the helper-contract fold (anchor asserted ×1), baselined, then the frozen draft diffed against it → `FOLD-CHECK CLEAN: machine-readable state unchanged (6 signals held)`. A baseline taken after folding would have been a tautology.

## Closing

**Walks 1-5, yields 2 → 2 → 0 → 1 → 0. BAR MET on walk 5's dry confirming pass. Cold panel not convened (T1 additive change to a read-only reporter; 563/569/571 precedent). Close is MANUAL (CEO-lane verdicts; auto_close false). The most consequential catch was w2-2: the live probe intended to prove the guard does not mute pauses would have armed OVER its own test file and proven nothing — the failure mode this plan exists to prevent, reproduced inside the plan's own verification.**
