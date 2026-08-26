# bellows — executable: wrap_check's [4/memory] arm gains the class-frontmatter gate (BLOCKING) + orphan/size-cap advisories (WARN-first) — the memory pipeline's enforcement half

**Date:** 2026-08-26 | **Project:** bellows | **Tier:** Small | **Dispatch Mode:** bellows | **cycle_tier:** T1 | **Test Scope:** targeted (wrap-hook tests) + full suite at QA | **Execution:** Step 1 (DEV) → Step 2 (QA) | **qa_steps:** 2 | **pause_for_verdict:** always

**auto_close:** false

**Depends on:** the CEO's "proceed as suggested" (mechanization batch item 2); the memory-to-system audit's work-list item 1; the LIVE-dir prototype at authoring (orphans 0, committed-classless 134 exempt, index 103/140 — measured, supersede with derivation).

## Why this exists

The "memories on a path to hardcoding" directive has no write-time enforcement: 134 of 137 entries carry no class, including ones written TODAY. The gate makes the law self-enforcing at the surface the wrap lock already owns — new/modified files only, so the corpus backfills by touch instead of detonating.

## What this plan does NOT do

- No backfill (committed files exempt until touched — stated design); the orphan and size-cap checks NEVER fail (WARN-first, printed); no doctrine edits.

## Numbers discipline

⚠️ **Measured 2026-08-26; the agent re-measures pre-flight; mismatch → HALT; every count carries measure-record-supersede.**

| id | pin | value | anchor |
|---|---|---|---|
| W1 | wrap_check.py | 456 lines; `m_dirty = porcelain(MEMORY)` count-1 | `hooks/eluvian/wrap_check.py` (repo-relative — worktree law) |
| W2 | live-dir baselines | orphans 0; committed-classless 134 (exempt); MEMORY.md 103 lines / cap 140 | the memory dir, ABSOLUTE read-only |
| W3 | test baseline | wrap-hook tests green pre-change (record the count; supersede with derivation) | `tests/test_wrap_hooks.py` |

## STEP 1 — DEV (the gate + advisories + tests)

> **Task A — worktree discipline.** `cd "$(git rev-parse --show-toplevel)" && test -f hooks/eluvian/wrap_check.py && echo TREE_OK` — HALT unless TREE_OK. Probes: (i) `/usr/bin/grep -cF -- "m_classless" hooks/eluvian/wrap_check.py; true`, (ii) `test -f tests/test_wrap_memory_class_gate.py && echo 1 || echo 0`. (0,0) → full run; (1,0) → resume at Task C; (1,1) → Task D commit-check; (0,1) → HALT.
>
> **Task B — the arm.** Insert IMMEDIATELY AFTER the anchor line `    m_dirty = porcelain(MEMORY)` (count-1, four-space indent exact) the following EXACTLY:
>
> ```python
>     # [4/memory] class-frontmatter gate (audit item 1): every NEW/MODIFIED
>     # entry carries `class:`. Committed files are exempt until touched —
>     # gradual backfill by design; the first post-ship wrap must not detonate.
>     m_classless = []
>     for _ln in m_dirty:
>         _st, _rel = _ln[:2], _ln[3:].strip()
>         if " -> " in _rel:
>             _rel = _rel.split(" -> ", 1)[1]
>         if "D" in _st or not _rel.endswith(".md"):
>             continue
>         _name = _rel.split("/")[-1]
>         if _name == "MEMORY.md" or _name.startswith("section-"):
>             continue
>         try:
>             _head = (MEMORY / _rel).read_text(encoding="utf-8", errors="replace")[:600]
>         except OSError:
>             m_classless.append(_rel + " (unreadable)")
>             continue
>         if "class:" not in _head:
>             m_classless.append(_rel)
>     if m_classless:
>         fails.append(
>             f"[4/memory] {len(m_classless)} new/modified memory entr(ies) missing "
>             f"`class: mechanize|codify|keep|stale` in frontmatter (keep requires "
>             f"a stated impossibility): " + ", ".join(sorted(m_classless))
>         )
>     # WARN-first advisories (funnel law) — printed, NEVER appended to fails.
>     try:
>         _idx = (MEMORY / "MEMORY.md").read_text(encoding="utf-8", errors="replace")
>         for _p in sorted(MEMORY.glob("section-*.md")):
>             _idx += _p.read_text(encoding="utf-8", errors="replace")
>         _orphans = sorted(
>             _p.name for _p in MEMORY.glob("*.md")
>             if _p.name != "MEMORY.md" and not _p.name.startswith("section-")
>             and _p.name not in _idx
>         )
>         if _orphans:
>             print(f"[4/memory] WARN (advisory): {len(_orphans)} entr(ies) not "
>                   f"referenced from MEMORY.md or any section file: "
>                   + ", ".join(_orphans[:8]))
>         _own_lines = len((MEMORY / "MEMORY.md").read_text(
>             encoding="utf-8", errors="replace").splitlines())
>         if _own_lines > 140:
>             print(f"[4/memory] WARN (advisory): MEMORY.md at {_own_lines} lines "
>                   f"exceeds the 140 cap — move a SECTION to its own file (the "
>                   f"sections law); never trim entries silently.")
>     except OSError:
>         pass
> ```
>
> Post-probes: `"m_classless"` count >= 3; `"WARN (advisory)"` count == 2; `"NEVER appended to fails"` == 1. Smoke: `python3 hooks/eluvian/wrap_check.py 2>&1 | tail -3` still reaches a verdict line (the arm crashes nothing on the live layout).
>
> **Task C — tests `tests/test_wrap_memory_class_gate.py`** (new): six tests over a tmp_path fake memory repo (git init, MEMORY.md + entries; monkeypatch the module's MEMORY): (1) an uncommitted new entry WITHOUT class → the fail line appears; (2) WITH `class: codify` → no class fail; (3) an uncommitted MEMORY.md edit alone → no class fail (index exempt); (4) a committed classless entry, clean tree → no fail (the exemption); (5) a COMMITTED classless entry absent from the index (committed so the class gate is silent — the WARN isolated by construction) → the orphan WARN prints (capsys) and fails gains nothing; (6) a >140-line MEMORY.md → the cap WARN prints, fails unchanged. Targeted run: the new file + `tests/test_wrap_hooks.py` — 0 failed (record the counts; supersede with derivation).
>
> **Task D — dev log + commit.** `knowledge/dev-logs/wrap-check-memory-class-gate-dev-2026-08-26.md` (probe raws, smoke tail, targeted raw). Commit (WORKTREE toplevel): `cd "$(git rev-parse --show-toplevel)" && git add hooks/eluvian/wrap_check.py tests/test_wrap_memory_class_gate.py knowledge/dev-logs/wrap-check-memory-class-gate-dev-2026-08-26.md && git commit -m "[<id from your plan filename>] wrap-check-memory-class-gate(wrap-check-memory-class-gate-2026-08-26): class-frontmatter FAIL + orphan/size-cap advisories, exempt-until-touched" -- hooks/eluvian/wrap_check.py tests/test_wrap_memory_class_gate.py knowledge/dev-logs/wrap-check-memory-class-gate-dev-2026-08-26.md && git rev-parse HEAD` — **CAPTURE_COMMIT**.
>
> **Deposits:**
> - `hooks/eluvian/wrap_check.py`
> - `tests/test_wrap_memory_class_gate.py`
> - `knowledge/dev-logs/wrap-check-memory-class-gate-dev-2026-08-26.md`
>
> **Scope:**
> - `hooks/eluvian/wrap_check.py`
> - `tests/test_wrap_memory_class_gate.py`
> - `knowledge/dev-logs/wrap-check-memory-class-gate-dev-2026-08-26.md`

## STEP 2 — QA (FULL suite + live behavior)

> **Item 1 — full suite.** `cd "$(git rev-parse --show-toplevel)"`; `python3 -m pytest tests/ --tb=short -q 2>&1 | cat | tee knowledge/qa/evidence/wrap-check-memory-class-gate-2026-08-26/pytest_full.txt` — 0 failed (record the passed count; the derivation vs 1488 + 6).
> **Item 2 — live behavior.** Run the committed wrap_check on the REAL layout: with the memory tree CLEAN, no [4/memory] class fail and no orphan WARN (the measured-0 baseline holding live — paste the tail). Extraction probes: the three Task-B post-probes on `git show`; `"def test_"` == 6 in the test file; `cmp` vs live → 0 each. Raw → `knowledge/qa/evidence/wrap-check-memory-class-gate-2026-08-26/probes-raw.txt`.
> **Item 3 — hygiene + receipt** `knowledge/qa/evidence/wrap-check-memory-class-gate-2026-08-26/qa-receipt.md`: numstat 3 files; toplevel; reflog `-n 4` → 0 amends; per-item table, then the Rule 20 block INSIDE a "Verification"-headed section (the 556 placement law).
>
> ⚠️ **Gate note:** pytest summary named above — the gate parses; no benign override pre-declared.
>
> **Deposits:**
> - `knowledge/qa/evidence/wrap-check-memory-class-gate-2026-08-26/pytest_full.txt`
> - `knowledge/qa/evidence/wrap-check-memory-class-gate-2026-08-26/probes-raw.txt`
> - `knowledge/qa/evidence/wrap-check-memory-class-gate-2026-08-26/qa-receipt.md`
>
> **Scope:**
> - `knowledge/qa/evidence/wrap-check-memory-class-gate-2026-08-26/pytest_full.txt`
> - `knowledge/qa/evidence/wrap-check-memory-class-gate-2026-08-26/probes-raw.txt`
> - `knowledge/qa/evidence/wrap-check-memory-class-gate-2026-08-26/qa-receipt.md`

Rule 20 banner (byte-exact, inside the QA receipt's VERIFICATION section):

```
============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
```

## Drafting Cycle

**Tier:** T1 — one arm + tests; blocking only where the law demands, WARN-first everywhere else; exempt-until-touched keeps the first post-ship wrap green by measurement.

**Walk register:** `bellows/knowledge/research/walk-register-wrap-check-memory-class-gate-2026-08-26.md`

**Walk 0 (context pin, measured):** the live-dir prototype (orphans 0, classless-committed 134 exempt, index 103/140); the m_dirty anchor count-1; porcelain rename handling; stop-path purity; the self-application note.

**Walks:**
- Weak spots:          w1 1 folded — test 5's orphan fixture was state-ambiguous (an uncommitted classless orphan would trip BOTH the class FAIL and the WARN, muddying the isolation): pinned COMMITTED so the WARN is isolated by construction.
- Destruction:         w1 dry — three-arm resume; the insertion point (after the porcelain call, before the dirty-fail append) leaves both appends coexisting; the smoke asserts reach-a-verdict only, honest about mid-plan live fails.
- Vulnerabilities:     w1 dry — stop-path purity (pure file reads, both advisory blocks inside try/except OSError); exempt-until-touched proven by the measured 134-exempt baseline; the rename arrow handled.
- Integration-record:  w1 dry — blocking exactly where the audit's law demands, WARN-first elsewhere with the funnel citation; the remaining ledger in open_forks; self-application stated.
- ACID:                w1 dry — every count clause-clothed (the (r) check this batch's sibling shipped would find nothing to flag here).
- **Walk 1 total: one finding, folded.**
- Weak spots:          w2 dry — the six test states re-traced against the arm's branches; each isolates one behavior.
- Destruction:         w2 dry.
- Vulnerabilities:     w2 dry.
- Integration-record:  w2 dry.
- ACID:                w2 dry.
- **Walk 2 total: 0 findings — all five lenses dry.**

**Closing:** ✅ **BAR MET at walk 2 — dry confirming pass, all five lenses.** T1 two-walk form; no direction-class finding; close is MANUAL (CEO-lane verdicts).

**Fold-and-deposit exactly once.**

## Cycle Manifest
tier: T1
target: bellows/hooks/eluvian/wrap_check.py
class: shop-infra
reads: /Users/marklehn/Developer/GitHub/bellows/hooks/eluvian/wrap_check.py, /Users/marklehn/.claude/projects/-Users-marklehn-Developer-GitHub/memory
writes: hooks/eluvian/wrap_check.py, tests/test_wrap_memory_class_gate.py, knowledge/dev-logs/wrap-check-memory-class-gate-dev-2026-08-26.md, knowledge/qa/evidence/wrap-check-memory-class-gate-2026-08-26/pytest_full.txt, knowledge/qa/evidence/wrap-check-memory-class-gate-2026-08-26/probes-raw.txt, knowledge/qa/evidence/wrap-check-memory-class-gate-2026-08-26/qa-receipt.md
open_forks: the mechanization ledger's remaining items (run_check.py wrapper; path normalization; reconcile_plan.py; scope_check rename; the 23 CODE rows) — future batches at the CEO's call; the audit-cadence nudge arm rides with a later batch
walks: 2
yields: 1, 0
validation: cycle_check=BAR_MET, plan_lint=0_FAIL, fold_check=N/A
coherence: N/A
