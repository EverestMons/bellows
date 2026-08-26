# Walk register — `depositor-cluster-2026-08-26` (bellows)

**schema_version:** `0.3`

**Plan:** `bellows/knowledge/decisions/drafts/executable-depositor-cluster.md`
**Tier:** T1 (Small — one new read-only tool + additive receipt wiring + tests; class shop-infra). **Panel: none.**
**Opened:** 2026-08-26

---

## Walk 0 — context pin (REAL, measured 2026-08-26)

1. **The batch-4 work order, item (2), CEO-approved:** one plan for the depositor cluster; the audit row L130 names the watcher shape ("deposit tooling could arm the watcher automatically").
2. **The scout's central finding (all from code, this authoring):** FOUR of the five cluster features already shipped — duplicate-check at the receipt layer (slug+hash refusal), minting single-writer at `lifecycle.py:255` (grep-enumerated, one writer), checker re-runs at the deposit path (`_rerun_validation` at depositor.py:159: BAR_MET + non-benign-lint + manifest cross-check), shared-append DB mediation (bellows.py:1681-1722 + the ledger idempotency pair). Only the AUTO-ARMED watcher is unbuilt: today's receipt merely attests a session-local watcher.
3. **Design:** `tools/gate_watcher.py` — pure `read_state`/`judge_transition` + a thin poll loop; read-only DB URI; keyed on `deposit_placeholder_name` (proven on row 568); logs to `logs/watch/` (untracked, split-path law); TERMINAL set exits. `deposit_receipt.py` spawns it detached, fail-open on the spawn (the receipt is never blocked by its reporter), `--no-spawn` opt-out.
4. **Retirement discipline:** seven memories retire at close as the Planner's act (`class: stale`, the 562 gate); the deposit-once pointer carries the grep-first residue (different-slug duplicates stay Planner discipline).
5. **id prediction:** 569.

⚠️ Walk 0 carries no fold rows. Walks 1+ appended AFTER the draft exists, from real passes.

---

## Walk 1 — five-lens sequential walk (post-draft, real)

| id | walk | lens | sub_question | origin | finding | pre_fold_text | resolution |
|---|---|---|---|---|---|---|---|
| w1-1 | 1 | Weak spots | can QA Item 2 actually run from the worktree? | pre-existing | the worktree carries no `lifecycle.db` (untracked), so the worktree tool's default `_DB` resolves to a missing file and `--status` prints db-unreadable; `read_state`'s `db_path` parameter was unreachable from the CLI, and the QA instruction hedged with a convoluted live-checkout fallback | `run the COMMITTED tool from the worktree; its _DB resolves relative to the tool's own path, so invoke it as python3 <live-checkout>/tools/gate_watcher.py --status … ONLY if the worktree copy cannot see a lifecycle.db; state which you ran` | folded: `--db-path` CLI argument added (both modes thread it to read_state); QA Items 2.1/2.2 rewritten to pass the live checkout's DB path explicitly; test 8 passes `--db-path` instead of monkeypatching `_DB` |
| — | 1 | Destruction | — | — | DRY — watcher bounded (terminal-exit + 120m timeout), read-only URI, log dir untracked; the duplicate-probe receipt is inert (no matching ready- plan), explicitly cleaned, and re-verified at QA; spawn fail-open never blocks the receipt | — | no fold |
| — | 1 | Vulnerabilities | — | — | DRY — the D3 grep enumerates and classifies every hit (the writer line is its own positive control); tests build their own tmp DB via init_lifecycle_db; the override-honored arm (test 4) pins the overridden=0 filter | — | no fold |
| — | 1 | Integration-record | — | — | DRY — the seven retirements named in-plan with the sandbox split; deposit blocks name every file incl. tests; the QA .txt named for the qa_test_result gate | — | no fold |
| — | 1 | ACID | — | — | DRY — one pathspec-limited commit, toplevel-first; counts carry supersede clauses | — | no fold |

**Walk 1 total: 1 finding (instruction 1 / record 0), folded; fold_check CLEAN (12 signals held); fold text grep-verified (`--db-path` present ×4, the superseded monkeypatch/live-checkout hedge verified 0).**

---

## Walk 2 — five-lens sequential walk (real)

| id | walk | lens | sub_question | origin | finding | pre_fold_text | resolution |
|---|---|---|---|---|---|---|---|
| — | 2 | Weak spots | — | — | DRY — first-poll always logs (prev=UNSET → None-prev judge); repeated db-unreadable lines are bounded (≤480 over the 120m cap), log-only, and honest (silence-is-not-success); QA 2.1's expected in_progress is this plan's own live state during its QA step | — | no fold |
| — | 2 | Destruction | — | — | DRY — `--status` path skips makedirs; tests never enter the poll loop; spawned watchers are per-deposit bounded ro-readers | — | no fold |
| w2-1 | 2 | Vulnerabilities | does QA 2.3 check the dir the probe actually wrote? | fold-introduced (w1 era phrasing) | `<bellows-root>/receipts/` is ambiguous — Task E's probe writes the WORKTREE's receipts dir (`_BELLOWS_ROOT` derives from the tool's own path), so an agent checking the live root would earn a vacuous 0 (the a-check trap: a check that cannot fail) | `ls <bellows-root>/receipts/ \| /usr/bin/grep -cF dup_probe_569; true` | folded: pinned to the worktree receipts dir with the vacuous-alternative named, plus a `git status --porcelain -- receipts/` cleanliness assert |
| — | 2 | Integration-record | — | — | DRY — retirement list ×7 consistent across title/does-NOT-do/register; manifest reads/writes complete | — | no fold |
| — | 2 | ACID | — | — | DRY | — | no fold |

**Walk 2 total: 1 finding (instruction 1 / record 0), folded; fold_check CLEAN (12 signals held); fold grep-verified 1, superseded text 0. Bar NOT met — a further confirming walk required.**
