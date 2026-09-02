# QA Receipt — seam-tests-projects-parent-2026-09-01 (plan 100012, Step 2)

**Date:** 2026-09-01  
**QA agent:** Bellows QA  
**Worktree:** /Users/marklehn/Developer/bellows/.bellows-worktrees/100012  
**Step 1 receipt:** `knowledge/development/dev-log-seam-tests-2026-09-01.md` — Status: Complete

---

## Restart Discipline Note

The running daemon (pid 93535) was started before plan 100011's code landed. It still runs pre-100011 `bellows_root.py` for its own claim/seam logic. The dispatcher's injected QA mandate (at the top of the Step 2 system prompt) names the **shop path**:

> `/Users/marklehn/Developer/GitHub/RULE_20_SELF_CHECK_BLOCK.md`

This is the path the daemon's stale `gates.QA_MANDATE_SUFFIX` and the pre-100011 governance root produced. The **actual path used** in this QA step, derived via `bellows_root.resolve_governance_root()` from the post-100011 code in this worktree:

> `/Users/marklehn/Developer/eluvian-governance/RULE_20_SELF_CHECK_BLOCK.md`

The first QA step after the CEO's restart will receive a mandate already naming the correct path. The Rule 20 block below was run from the correct (post-100011) path.

---

## Verification Table

| # | Item | Expected | Measured | Status |
|---|------|----------|----------|--------|
| 1a | `resolve_projects_parent` monkeypatch count in `test_plan_claim.py` | 6 | 6 | ✅ |
| 1b | `import bellows_root` count in `test_plan_claim.py` | 1 | 1 | ✅ |
| 1c | `"awaiting_verdict"` count in `test_gate_watcher.py` | 9 | 9 | ✅ |
| 1d | `2 * 3 * 5` count in `test_gate_watcher.py` | 1 | 1 | ✅ |
| 1e | Six `awaiting_verdict` cells pass (`behaves_as_classified and awaiting_verdict`) | 6 passed | 6 passed | ✅ |
| 1f | `git show --stat HEAD` lists exactly three declared paths | 3 paths | 3 paths | ✅ |
| 2a | `resolve_projects_parent()` in this worktree | `/Users/marklehn/Developer` | `/Users/marklehn/Developer` | ✅ |
| 2b | Four seam ids pass under the failing condition (`-k "unresolvable or advisory_checkout_none or both_none or call_time"`) | 4 passed | 4 passed | ✅ |
| 3 | Full suite — no FAILED line; N passed ≥ 1663; CWD survivor absent | ≥1663 passed, 0 FAILED | 1669 passed, 1 skip (live-DB location), 0 FAILED | ✅ |
| 4a | 100011 proof without `ELUVIAN_WRAP_ROOT`: governance root, projects parent, tuyere checkout, QA_MANDATE_SUFFIX check | `/Users/marklehn/Developer/eluvian-governance`, `/Users/marklehn/Developer`, `/Users/marklehn/Developer/tuyere`, `False` | identical | ✅ |
| 4b | 100011 proof with `ELUVIAN_WRAP_ROOT=/Users/marklehn/Developer`: same four values | same as 4a | identical | ✅ |
| 5a | Residual-literal sweep: no `*.py` files (excluding declared dirs) contain `/Users/marklehn/Developer/GitHub` | no files, exit=1 | no files, exit=1 | ✅ |
| 5b | Liveness pair: `Developer/GitHub` count in `bellows_root.py` | 1 | 1 | ✅ |

---

## Item Notes

**Item 2b — four ids precisely:** `-k "unresolvable or advisory_checkout_none or both_none or call_time"` selects exactly 4 tests (not 5 — `test_required_checkout_none` is excluded by the tighter keys). All 4 pass under `/Users/marklehn/Developer` as the projects parent — the condition that failed them pre-edit — because they now monkeypatch `bellows_root.resolve_projects_parent` to `tmp_path / "noprojects"` in addition to hiding the env and home sources.

**Item 3 — CWD survivor absent:** `test_relative_path_unchanged` from `tests/test_gates_cross_machine_paths.py` does not appear in the worktree suite output, as expected for the worktree shape.

**Item 3 — single skip:** The `test_reachable_states_match_the_classification_dimension` live-DB test skips because `lifecycle.db` is not at the expected path in this worktree location — a location property, not a regression.

**Item 5a — exit=1:** `grep -r` returns exit 1 when no files match (expected — not an error here).

---


---

## Rule 20 — QA Self-Check Results

```
============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
Evidence folder: /Users/marklehn/Developer/bellows/.bellows-worktrees/100012/knowledge/qa/evidence/seam-tests-2026-09-01
Files verified: 2
```
