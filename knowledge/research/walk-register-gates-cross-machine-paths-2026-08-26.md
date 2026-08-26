# Walk register — `gates-cross-machine-paths-2026-08-26` (bellows)

**schema_version:** `0.3`

**Plan:** `bellows/knowledge/decisions/drafts/executable-gates-cross-machine-paths.md`
**Tier:** T1 (Small — one strategy added to ONE resolver + tests; class shop-infra). **Panel: none.**
**Opened:** 2026-08-26

---

## Walk 0 — context pin (REAL, measured 2026-08-26)

1. **Batch-2 item 2 (CEO's proceed):** the 560 class — a plan authored on another machine declares deposits at ITS absolute layout; the executing machine's gates check the literals and fail on artifacts (five rows measured at exec-560).
2. **The leverage, measured:** `_resolve_deposit_path` (gates.py L324) is the SINGLE resolver behind every failing surface — deposit_exists (4 call sites), rule_20 (L590), rule_22 (L629/645), qa evidence (L774). One Strategy-4 arm fixes all seven at once.
3. **Strategy 4 (cross-machine re-root):** absolute + missing + contains `/<project-basename>/` → re-anchor the remainder after the LAST such segment onto wt_path (first, when present) then project_path. rfind (the LAST occurrence) chosen deliberately: a foreign path like `/Users/x/bellows/backup/bellows/hooks/f.py` re-roots the innermost remainder. Fail-closed: no marker or no hit → None exactly as today.
4. **Daemon staleness stated:** gates.py is LIVE daemon code — the running daemon keeps the old resolver until restart; /eluvian's own sync arm surfaces "daemon restart needed" when bellows moves. The fix arms at the next restart; nothing here restarts the daemon (the wrap's leave-it-running law).
5. **id prediction:** 564.

⚠️ Walk 0 carries no fold rows. Walks 1–2 appended AFTER the draft exists, from real passes.

---

## Walk 1 — five-lens sequential walk (post-draft, real)

| id | walk | lens | sub_question | origin | finding | pre_fold_text | resolution |
|---|---|---|---|---|---|---|---|
| P1 | 1 | 1 Weak spots | 1.2 | — | `    return None` is not unique file-wide — a located-line instruction leaves the agent an ambiguous anchor. | `replace the resolver's FINAL return None (the one closing …)` | Folded: the unique two-line pair (p3 abspath return + return None) is the anchor, count-1 asserted on the pair; verified unique against the live file. |

**Walk 1 total: one finding, folded.** (Other lenses dry — last-strategy/fail-closed guards tested; worktree-first order preserved; staleness stated at three sites.)

---

## Walk 2 — five-lens sequential walk (confirming pass, real)

| id | walk | lens | sub_question | origin | finding | pre_fold_text | resolution |
|---|---|---|---|---|---|---|---|
| — | 2 | all five | — | — | DRY — the pair anchor verified unique live. | — | No folds. |

**Walk 2 total: 0 findings — all five lenses dry. BAR MET; T1, no panel escalation.**
