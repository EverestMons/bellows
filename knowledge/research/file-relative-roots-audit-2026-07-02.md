# `__file__`-Relative Root Resolution Audit — Per-Instance Reachability Proofs

**Date:** 2026-07-02
**Source:** FORWARD row 15 (added 2026-06-06, CEO-deferred with audit-first / convert-with-proof disposition)
**Agent:** Bellows Systems Analyst
**Method:** grep enumeration + import-graph tracing + worktree-content verification

---

## 1. Enumeration

`grep -n "__file__" *.py scripts/*.py` from the canonical bellows root. Comments excluded; only executable `__file__` expressions listed.

| # | File:Line | Expression (verbatim) |
|---|---|---|
| 1 | `bellows.py:25` | `BELLOWS_ROOT = Path(__file__).parent.resolve()` |
| 2 | `bellows.py:1494` | `bellows_dir = os.path.dirname(os.path.abspath(__file__))` |
| 3 | `planner.py:11` | `BELLOWS_ROOT = pathlib.Path(__file__).parent.resolve()` |
| 4 | `verdict.py:13` | `BELLOWS_ROOT = Path(__file__).parent.resolve()` |
| 5 | `bellows_root.py:21` | `start = (_start or Path(__file__).resolve().parent).resolve()` |
| 6 | `decisions.py:13` | `current = Path(__file__).resolve().parent` |
| 7 | `decisions.py:21` | `return Path(__file__).resolve().parent.parent` |
| 8 | `scripts/migrate_config.py:14` | `BELLOWS_ROOT = Path(__file__).parent.parent.resolve()` |
| 9 | `scripts/check_backlog_freshness.py:49` | `BELLOWS_ROOT = Path(__file__).parent.parent.resolve()` |
| 10 | `scripts/plan_lint.py:18` | `BELLOWS_ROOT = Path(__file__).parent.parent.resolve()` |
| 11 | `scripts/migrate_orphan_verdicts.py:17` | `BELLOWS_ROOT = Path(__file__).parent.parent.resolve()` |

**Total: 11 code-level instances across 8 files.**

### Citation reconciliation

- **Row 15 cited 3:** bellows.py, planner.py, verdict.py — **all confirmed present** (instances 1, 3, 4).
- **Lessons-forge baton cited 4** (adds runner.py:20) — **STALE.** `runner.py:21` now reads `BELLOWS_ROOT = resolve_bellows_root()`. The `__file__` usage was already converted (likely during the `bellows_root.py` utility creation). runner.py:20 is a blank line.
- **Neither citation caught:** bellows.py:1494, bellows_root.py:21, decisions.py:13/21, or the 4 `scripts/*.py` instances. These were either out of scope for the original enumeration or added after the citation date (2026-06-06).

---

## 2. Worktree reachability — structural facts

### 2a. Are bellows .py files copied into worktrees?

**YES.** `_create_worktree` (bellows.py:909) runs `git worktree add` under the target project's repo. When bellows is the watched project (confirmed: `.bellows-worktrees/122` and `.bellows-worktrees/123` are active), the worktree contains all tracked files. Verified by listing `.bellows-worktrees/123/*.py` — all 15 .py modules present including bellows.py, planner.py, verdict.py, decisions.py, bellows_root.py.

### 2b. What is ABSENT from worktrees?

`.gitignore` excludes: `config.json`, `bellows.db`, `logs/`, `verdicts/ledger.jsonl`, `.bellows-cache/`, `.bellows-worktrees/`, `config.secrets.json`, `.env`, `.bellows.lock`. Verified: `config.json` does not exist at `.bellows-worktrees/123/config.json`.

This is the discriminator `bellows_root.py` uses: walk up from `__file__` to the nearest ancestor containing `config.json`. Since config.json is gitignored, it exists only at the canonical root — the walker correctly resolves through the worktree to the canonical bellows root.

### 2c. Execution model — who runs from where?

- **Daemon process** (bellows.py, imported modules): always started by operator from canonical root (`python bellows.py` or `python dashboard.py`). All `import` statements resolve from canonical root's sys.path. Module-level `BELLOWS_ROOT = Path(__file__).parent.resolve()` in bellows.py, verdict.py, planner.py correctly resolves to canonical root because `__file__` IS the canonical copy.

- **Agent subprocesses** (`claude -p`): spawned by `runner.py` with `cwd=worktree_path`. Claude Code's shell commands execute from the worktree. Agents use Read/Edit/Write/Bash tools — they do NOT import bellows Python modules. The BELLOWS_AGENT_SYSTEM_PROMPT (runner.py:24) contains no instructions to import bellows infrastructure.

- **Test execution** (`pytest`): tests run from cwd. When pytest runs inside a worktree (e.g., an agent running `python3 -m pytest tests/`), `sys.path.insert(0, ...)` in test files adds the worktree root to sys.path. Imports of bellows modules would get the WORKTREE copies, where `Path(__file__).parent.resolve()` would resolve to the worktree root.

---

## 3. Per-instance reachability proofs

### Instance 1: `bellows.py:25` — `BELLOWS_ROOT = Path(__file__).parent.resolve()`

**Derived paths:** DB_PATH (`bellows.db`), SHADOW_CACHE_DIR (`.bellows-cache/`), and numerous operational paths throughout the daemon.

**Reachable from worktree?** NO for production. The daemon is started from the canonical root; `bellows.py` is imported by the daemon process, not by agents. Agents run `claude -p` which uses Claude Code tools, not Python imports of bellows infrastructure.

**Reachable via tests?** YES — test files do `import bellows` or `from bellows import ...`. If pytest runs from a worktree, the worktree's bellows.py is imported, and BELLOWS_ROOT resolves to the worktree root.

**Blast radius:** In production: N/A (unreachable). In tests: DB_PATH → worktree/bellows.db (doesn't exist; tests that touch DB create their own fixtures), SHADOW_CACHE_DIR → worktree/.bellows-cache/ (doesn't exist; tests that need it would create it as worktree-local garbage). Test isolation is preserved — no cross-contamination of canonical state.

**Disposition:** `keep-as-is` — not production-reachable; test-path resolution produces harmless worktree-local artifacts.

### Instance 2: `bellows.py:1494` — `bellows_dir = os.path.dirname(os.path.abspath(__file__))`

**Used by:** `_module_fingerprints()` — gets git log short-sha for each core .py module for heartbeat fingerprinting.

**Reachable from worktree?** NO — `_module_fingerprints()` is called by the daemon's heartbeat loop, never by agents or tests (no test file calls this function).

**If reached:** Would run `git log` on worktree .py files. Since worktrees share the same git history as the main repo, the fingerprints would be identical. Completely benign.

**Disposition:** `keep-as-is` — unreachable from worktree execution.

### Instance 3: `planner.py:11` — `BELLOWS_ROOT = pathlib.Path(__file__).parent.resolve()`

**Used by:** `_log_consultation()` at line 89 — writes to `BELLOWS_ROOT / "logs" / "planner-consultation.jsonl"`.

**Reachable from worktree?** NO in production — planner.py is NOT imported by any production module (verified: `grep -rn "import planner\|from planner" *.py` returns nothing). It is imported only by `tests/test_planner.py` and `tests/test_phase4_planner_retry.py`.

**If reached via tests:** Log would write to `worktree/logs/planner-consultation.jsonl` — worktree-local garbage, benign. Tests that call `consult()` mock `subprocess.run` and may never trigger the log write path.

**Disposition:** `keep-as-is` — not production-imported; test-only reach produces benign worktree-local artifacts.

### Instance 4: `verdict.py:13` — `BELLOWS_ROOT = Path(__file__).parent.resolve()`

**Used by:** `VERDICTS_DIR = BELLOWS_ROOT / "verdicts"` — the entire verdict queue (pending/resolved/processed lifecycle).

**Reachable from worktree?** NO in production — verdict.py is imported by bellows.py at line 129 (`import verdict`), which runs from canonical root. The daemon process holds the canonical copy.

**If reached via tests:** VERDICTS_DIR would point to `worktree/verdicts/` (doesn't exist). Verdict reads would find no files; verdict writes would create orphan directories in the worktree. Tests that exercise verdict functions typically set up their own fixture directories.

**Disposition:** `keep-as-is` — not production-reachable from worktree; test-path misresolution is worktree-local.

### Instance 5: `bellows_root.py:21` — `start = (_start or Path(__file__).resolve().parent).resolve()`

**This IS the worktree-safe resolution utility.** Uses `__file__` only as a starting point for the walk-up. The walk-up searches for `config.json` in ancestors — since config.json is gitignored and only exists at the canonical root, the walk correctly resolves through `.bellows-worktrees/<wt>/` → `.bellows-worktrees/` → canonical bellows root (contains config.json) → returns canonical root.

**Already worktree-safe by design.** Consumed by runner.py, dashboard.py, lifecycle.py, status.py, reporting.py.

**Disposition:** `keep-as-is` — this is the solution module; its `__file__` usage is correct and intentional.

### Instance 6: `decisions.py:13` — `current = Path(__file__).resolve().parent`

**Used by:** `resolve_governance_root()` — walks up from `__file__` to find nearest ancestor containing `COMPANY.md`.

**Reachable from worktree?** In production: NO — decisions.py is imported by runner.py (line 15: `import decisions`), which is imported by bellows.py daemon from canonical root.

**If reached from worktree:** Walk-up from `.bellows-worktrees/123/decisions.py` traverses: `.bellows-worktrees/123/` → `.bellows-worktrees/` → canonical bellows root → `/Users/marklehn/Developer/GitHub/` (contains COMPANY.md) → returns this path. **The walk-up correctly resolves even from worktrees** because COMPANY.md exists at the governance root above bellows.

**Disposition:** `keep-as-is` — the walk-up is self-healing; correct from any starting directory that has COMPANY.md as an ancestor.

### Instance 7: `decisions.py:21` — `return Path(__file__).resolve().parent.parent` (fallback)

**This is the dead-path fallback** when `COMPANY.md` is not found in any ancestor (filesystem root reached). From a worktree, `.parent.parent` of `.bellows-worktrees/123/decisions.py` would resolve to `.bellows-worktrees/` — wrong.

**Reachable?** Only if COMPANY.md is missing from all ancestors. In the normal deployment, COMPANY.md exists at `/Users/marklehn/Developer/GitHub/COMPANY.md`, making this fallback unreachable. The log warning at line 20 would alert on any occurrence.

**Disposition:** `keep-as-is` — dead-path safety net; unreachable under normal deployment; the warning provides observability.

### Instance 8: `scripts/migrate_config.py:14`

**Manual one-shot migration script.** Not invoked by daemon or agents. If run from a worktree cwd, would look for `config.json` at worktree root — not found (gitignored), exits with error at line 23. **Fails safe.**

**Disposition:** `keep-as-is` — manual script, not programmatically reachable, fails safe.

### Instance 9: `scripts/check_backlog_freshness.py:49`

**Manual diagnostic script.** Reads `BACKLOG.md` and `PROJECT_STATUS.md` — tracked files present in worktrees with the same content as canonical. **Benign** even if run from a worktree.

**Disposition:** `keep-as-is` — manual script, benign resolution.

### Instance 10: `scripts/plan_lint.py:18`

**Manual pre-deposit lint.** Uses BELLOWS_ROOT only for `sys.path.insert(0, str(BELLOWS_ROOT))` to import `gates`. From a worktree, imports the worktree's `gates.py` — same tracked code, pure-logic module with no path-sensitive state. **Benign.**

**Disposition:** `keep-as-is` — manual script, worktree-copy imports are benign (same tracked code).

### Instance 11: `scripts/migrate_orphan_verdicts.py:17`

**Manual one-shot migration.** Has a hardcoded `MAIN_REPO = Path("/Users/marklehn/Developer/GitHub/bellows")` at line 18. All operational paths (CONFIG_PATH, RESOLVED_DIR) derive from MAIN_REPO, not BELLOWS_ROOT. The `__file__`-derived BELLOWS_ROOT is defined but unused for operational paths. **Benign.**

**Disposition:** `keep-as-is` — manual script, BELLOWS_ROOT is vestigial (MAIN_REPO hardcoded path used instead).

---

## 4. Summary table

| # | Instance | Reachable from worktree? | Blast radius | Disposition |
|---|---|---|---|---|
| 1 | bellows.py:25 | No (production); Yes (tests) | Tests: worktree-local garbage (benign) | keep-as-is |
| 2 | bellows.py:1494 | No | N/A | keep-as-is |
| 3 | planner.py:11 | No (production); Yes (tests) | Tests: worktree-local log (benign) | keep-as-is |
| 4 | verdict.py:13 | No (production); Yes (tests) | Tests: worktree-local orphans (benign) | keep-as-is |
| 5 | bellows_root.py:21 | Yes (by design) | Correct resolution (this IS the fix) | keep-as-is |
| 6 | decisions.py:13 | No (production); self-healing walk-up | Correct even from worktree | keep-as-is |
| 7 | decisions.py:21 | No (dead-path fallback) | Wrong, but unreachable | keep-as-is |
| 8 | scripts/migrate_config.py:14 | No (manual script) | Fails safe (config.json missing) | keep-as-is |
| 9 | scripts/check_backlog_freshness.py:49 | No (manual script) | Benign (reads tracked files) | keep-as-is |
| 10 | scripts/plan_lint.py:18 | No (manual script) | Benign (imports tracked code) | keep-as-is |
| 11 | scripts/migrate_orphan_verdicts.py:17 | No (manual script) | Benign (uses hardcoded MAIN_REPO) | keep-as-is |

---

## 5. Follow-up fix list

**None.** All 11 instances are either:
- (a) Not reachable from worktree execution in production (the daemon always imports from canonical root),
- (b) Already worktree-safe by design (bellows_root.py, decisions.py walk-ups), or
- (c) Manual scripts that fail safe or produce benign results.

The test-path reachability (instances 1, 3, 4) produces worktree-local artifacts that don't contaminate canonical state — this is actually desirable test isolation. Converting these would require either passing `resolve_bellows_root()` through test fixtures or accepting that tests write to canonical directories, which would be worse.

The key structural insight: **the execution boundary that protects against `__file__` misresolution is not code-level — it's process-level.** The daemon process (which imports bellows.py, verdict.py, planner.py) always runs from the canonical root. Agent subprocesses run from the worktree but use Claude Code tools (Read/Edit/Write/Bash), not Python imports of bellows infrastructure. The `resolve_bellows_root()` utility in `bellows_root.py` exists for the one module (runner.py) that could theoretically be reached from both contexts, and it is already deployed there.

### Ledger Updates

#### Prompt Feedback

None — diagnostic instructions were clear and well-scoped.

---

## Output Receipt
**Agent:** Bellows Systems Analyst
**Step:** 1
**Status:** Complete

### What Was Done
Enumerated all 11 `__file__`-derived path expressions across 8 files. Reconciled against two prior citations (row 15's three confirmed; lessons-forge baton's runner.py:20 is stale — already converted to `resolve_bellows_root()`). Produced per-instance worktree-reachability proofs with evidence from the import graph, worktree creation mechanism, .gitignore exclusions, and live worktree content. All 11 instances disposed as `keep-as-is` — no production-reachable dangerous instances found.

### Files Deposited
- `knowledge/research/file-relative-roots-audit-2026-07-02.md` — full enumeration, per-instance reachability proofs, summary table, no follow-up fixes needed

### Files Created or Modified (Code)
- None (read-only diagnostic)

### Decisions Made
- All 11 instances classified as `keep-as-is` based on evidence that the process-level execution boundary (daemon from canonical root, agents via Claude Code tools not Python imports) prevents production-reachable misresolution.

### Flags for CEO
- FORWARD row 15 can be closed: the hazard is structurally mitigated by the daemon/agent process boundary and the existing `bellows_root.py` utility on runner.py. No code changes warranted.

### Flags for Next Step
- None
