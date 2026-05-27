# Leftover-After-Ship Tooling Scope — Diagnostic Findings

**Date:** 2026-05-26
**Plan:** diagnostic-leftover-after-ship-tooling-scope-2026-05-26
**Step:** 1 (SA)
**Status:** Complete

---

## Section A — BACKLOG File Shape

### Top-level section structure

```
# bellows — Backlog          (H1 — file title)
## Open                      (H2 — 6 entries as of 2026-05-26)
---                          (horizontal rule separator)
## Closed                    (H2 — 62+ entries)
```

Two sections only: `## Open` and `## Closed`. No Archive section. Both live in the same file (`knowledge/BACKLOG.md`, ~197 lines). A 5-line preamble with usage instructions precedes `## Open`.

### Open entry format (3 verbatim samples)

```
- **Added 2026-05-22:** Worktree teardown cherry-pick conflict on dirty `PROJECT_STATUS.md` (sequential-Planner-edit variant). The existing 2026-05-22 entry on parallel-diagnostic teardown conflicts covers the case where two agents both modify `PROJECT_STATUS.md` in their respective worktrees. THIS variant: agent commits a `PROJECT_STATUS.md` update in its worktree, but the local main branch's working tree has uncommitted Planner-side edits to the same file. Teardown's cherry-pick onto local main aborts with `Your local changes to the following files would be overwritten by merge: PROJECT_STATUS.md`. The worktree branch already pushed direct to origin; the local main never receives the QA commit; the deposit file (QA report) doesn't exist on local filesystem despite Bellows' `deposit_exists` gate passing (because that gate checks the worktree, not local main post-teardown). Observed 2026-05-22 on `executable-fuel-bracket-floor-only-phase-a-2026-05-22` Step 3. **Recovery applied:** Planner committed the dirty local edits (`b274d1d`), cherry-picked the QA worktree commit (`b142e4a` → local `42d571f`), pushed origin, then issued continue verdict so Bellows' next teardown attempt would succeed. **Resolution shape (options):** (a) teardown auto-stashes local changes before cherry-pick, then unstashes (handles the common case but loses changes on conflict during unstash); (b) teardown detects dirty working tree before attempting cherry-pick and produces a clearer pause-for-CEO with explicit recovery instructions, rather than the cryptic cherry-pick conflict surfaced today; (c) Planner discipline rule — NEVER leave uncommitted PROJECT_STATUS.md edits between session checkpoints (operational mitigation today, no Bellows code change required). **Effort estimate:** option (b) is small (~20 LOC pre-cherry-pick dirty-tree check), option (a) is medium with risk, option (c) is free but discipline-dependent. **Operational impact:** Planner-side recovery surgery required on every occurrence; QA deposits are written but not visible to subsequent plans until manual cherry-pick lands. Reference: this session's verdict-request `verdict-request-fuel-bracket-floor-only-phase-a-2026-05-22-step-3.md` with worktree_teardown gate failure.
```

```
- **Added 2026-05-22:** Parallel-diagnostic cherry-pick conflicts on shared bookkeeping files at teardown. Two diagnostics (`diagnostic-background-job-infrastructure-inventory-2026-05-22` and `diagnostic-match-lane-query-pattern-anatomy-2026-05-22`) dispatched in parallel against invoice-pulse. Each ran in its own worktree. Each appended a session entry to `PROJECT_STATUS.md` and a feedback entry to `knowledge/research/agent-prompt-feedback.md`. Teardown serializes worktree merge-back via cherry-pick onto local main. First diagnostic cherry-picked cleanly (commit `8513e17`); second hit cherry-pick conflict on both shared files at the same byte ranges (commit `a3426f0` aborted). Bellows surfaced via `worktree_teardown` gate failure even though all substantive gates passed. Deposit file was net-new but never landed on main because cherry-pick aborted as a unit. Recovery required manually extracting deposit content from the worktree branch and re-applying additive PROJECT_STATUS and feedback log changes via Python script. **Why this is structural:** `PROJECT_STATUS.md` and `agent-prompt-feedback.md` are project-wide append-only bookkeeping files that EVERY plan touches. Any two plans running in parallel within a project conflict at teardown regardless of source-code overlap. **Resolution shape:** detect cherry-pick conflict on known append-only files (`PROJECT_STATUS.md`, `agent-prompt-feedback.md`) at teardown time, and resolve by appending both worktree additions onto main rather than aborting. Could be a teardown-stage `git mergetool`-style auto-resolution or a Python diff merger using the conflict markers. **Operational mitigation today (now in `/Users/marklehn/Developer/GitHub/LESSONS.md` 2026-05-22 `planner-discipline` tag):** Planner serializes same-project plans by default; "parallel" CEO instructions interpreted as between-projects unless explicitly overridden. **Effort estimate:** medium — touches teardown code path, needs careful conflict-marker parsing and idempotency, regression tests on multi-plan scenarios. **Disposition recommendation:** defer until second occurrence demonstrates the LESSONS-based discipline alone is insufficient. Reference: LESSONS.md 2026-05-22 "Parallel diagnostics against the same project conflict at teardown on shared bookkeeping files" entry.
```

```
- **Added 2026-05-21:** Bellows status UI — replace terminal-only output as the primary observability surface. Idea from CEO during 2026-05-21 session: the terminal log requires scrolling and parsing to understand what's currently happening; a UI that displays per-plan step status at a glance (which plans are in-flight, paused, awaiting verdict, by step) would be a meaningfully better daily-use experience. Terminal log remains available as a secondary view. Open design questions before scoping: (a) deployment shape — web (Flask already in use, browser tab) vs Tauri desktop app vs macOS menu-bar widget vs ncurses TUI in same terminal; (b) data source — read directly from `bellows.db` runs table + filesystem state (decisions/*, verdicts/pending/*, verdicts/resolved/*) vs Bellows daemon exposing a status endpoint; (c) update mechanism — polling (1-5s refresh) vs websocket vs server-sent events vs filesystem watch on the UI side; (d) scope of v1 — just per-plan status table, or also include step-level progress, gate failure highlights, log tail per plan, click-through to deposit files. Likely 1–3 days of work depending on shape choices. Worth a separate planning session — not snap-decided. Reference: CEO chat 2026-05-21 ~22:30 session-wrap.
```

### Closed entry format (3 verbatim samples)

```
- **Closed 2026-05-26 (defer pending demonstrated need):** `WebSearch` and `WebFetch` not in Bellows-dispatched agents' `--allowedTools` list (originally 2026-05-22). Phase-1.5 audit verified the prior `permission-denial-history-audit-2026-05-22.md` findings against current `parsed.permission_denials` data: structured WebSearch/WebFetch denial events total **3 in 30 days**, all in a single log file (`logs/20260522-104929-step.json`) — the `diagnostic-claude-settings-permission-gap-2026-05-22` Step 1 incident the BACKLOG entry already cited. **No further incidents** in the 4 days since, including this session. The 2 SA queries and 1 WebFetch URL the SA attempted were all for Anthropic Claude Code docs; the diagnostic's substantive findings were derivable from prior Bellows research files (the audit explicitly confirmed this). The BACKLOG entry's own framing of question (b) — "the deeper question is whether the Planner should be authoring SA-investigation plans without web access in the first place" — answers itself by the data: the Planner's existing pattern of pre-loading external docs into research files before SA dispatch is sufficient. **Disposition:** defer. **Revisit trigger:** second incident demonstrating the pre-load workaround is insufficient (specifically: an SA step where the substantive finding genuinely required live web access AND the Planner had no reasonable way to pre-fetch the relevant content). At that point re-open with capability-addition framing including (a)/(b) decision: uniform vs role-conditional allowance. **No code changes shipped today** — BACKLOG hygiene closure only. **Methodology lesson surfaced this session (Forge candidate):** initial log-mining attempt used `grep WebSearch logs/*.json` which matched 676 files because `WebSearch` appears in agents' tool-registry text echoed back in `raw_output`, producing a ~22x false-positive count. Correct extraction is via `json.load()` + scan of `parsed.permission_denials` array for `tool_name in ("WebSearch", "WebFetch")`. Generalizable: when grepping agent step logs for denial events, parse JSON structure; don't rely on string matching against `raw_output`. Reference: `bellows/knowledge/research/permission-denial-history-audit-2026-05-22.md` (gate-level inventory + bucket (d) events 8-9).
```

```
- **Closed 2026-05-26 (RETIRE — structurally resolved):** MCP tool denials (`mcp__vexp__run_pipeline`, `mcp__vexp__get_context_capsule`) not on `READ_CLASS_TOOLS` exemption list (originally 2026-05-22). Retired as structurally resolved by `executable-mcp-read-class-tools-extension-2026-05-25` (DEV commit `9473cf7`, shipped 2026-05-25 — before session 6 of 2026-05-26). The fix extended `READ_CLASS_TOOLS` at `gates.py:35-43` from 4 entries (`Grep`, `Glob`, `Read`, `mcp__vexp__run_pipeline`) to 9 entries by adding `mcp__vexp__get_context_capsule`, `mcp__vexp__get_session_context`, `mcp__vexp__get_skeleton`, `mcp__vexp__index_status`, `mcp__vexp__search_memory` — covers both tools the BACKLOG entry named PLUS three additional vexp read-class tools. Deliberately excludes `mcp__vexp__save_observation` (write-class). 6 regression tests landed in `tests/test_gates.py` (5 positive + 1 critical negative for save_observation). Commit message literally reads "closes BACKLOG mcp_tool_denials." **No code changes shipped today** — BACKLOG hygiene closure only. The entry was authored 2026-05-22 and the fix landed 2026-05-25, but the Open entry was not moved to Closed at that time; it propagated through three session batons (sessions 5, 6, 7 of 2026-05-26) as a live horizon item before catching at session-8 Phase 1.5. **Pattern note:** fourth recurrence in three days of LESSONS 2026-05-26 "BACKLOG entries authored from current-state grep without scanning Closed history can misframe already-evaluated work." Previous catches: Item 2 (set→list) caught by session-7 freshness diagnostic; precondition-failure-field duplicate retired same session; Phase 3b read-side retired same session. Today's catch fired at the very first grep — `READ_CLASS_TOOLS` already contained the named tools. Cost of grep: ~5 seconds. Cost of not grepping: would have authored a diagnostic + executable to ship code that already exists. Discipline rule remains: pre-write grep of Closed section AND current code state before treating any baton-carried entry as live. Reference: `bellows/knowledge/decisions/Done/executable-mcp-read-class-tools-extension-2026-05-25.md`, `bellows/knowledge/development/mcp-read-class-tools-extension-2026-05-25.md` (dev log), `gates.py:35-43` (current READ_CLASS_TOOLS).
```

```
- **Closed 2026-05-26:** Test-isolation orphan pattern — Bellows tests had no `conftest.py` and `verdict.post_verdict_request()` was unmocked, so tests writing through dispatch paths created real `verdict-request-*` files in production `verdicts/pending/` during test runs (originally 2026-05-26). Shipped via `executable-bellows-test-isolation-conftest-2026-05-26` (DEV commit `fde737b`, QA commit `8b1fed4`) following diagnostic `diagnostic-bellows-test-isolation-conftest-2026-05-26` (commit `54fb8e1`). **Fix shape chosen:** Option (a) from the original entry — `tests/conftest.py` with a function-scoped autouse fixture (not session-scoped as the entry recommended; SA Deliverable C corrected this because pytest's `monkeypatch` is inherently function-scoped, and the performance cost is negligible). Body: `monkeypatch.setattr(verdict, "VERDICTS_DIR", tmp_path / "verdicts")` — patches the module-level constant that all three verdict-write paths (`post_verdict_request` at line 180, `check_verdict` at line 283, `log_to_ledger` at lines 317–318) read at call time. No production code change required — `VERDICTS_DIR` constant already existed at `verdict.py:14`. **Leakers identified by SA (Deliverable B):** exactly 2, both dispatch-spawn vector — `test_bellows.py::test_apply_defensive_header_defaults_propagates_to_reparsed_header` and `test_consume_verdicts.py::test_dispatch_starts_fresh_when_db_has_orphan_slug_rows`. Both fall to the same mechanism (sparse `gates.check()` mock + `_apply_defensive_header_defaults` injecting `pause_for_verdict="after_step_1"` + un-mocked `verdict.post_verdict_request`). 37 other `run_plan()` callers audited and confirmed safe (28 mock explicitly, 8 single-step auto-close, 1 dense-header). **Load-bearing QA verification:** after full-suite run (411 passed, 5 known carry-overs, 0 regressions) `ls verdicts/pending/ | grep -v "^archived$"` returned empty. Specific-test reproductions of both leakers also produced zero orphans. **Opt-out mechanism: none required** — existing tests in `test_verdict.py` that exercise real `VERDICTS_DIR` write behavior use their own `patch.object(verdict, "VERDICTS_DIR", ...)` inside `with` blocks, which override the conftest fixture for their scope. **Pattern note (Forge candidate):** SA "Total LOC: 7" label in Deliverable C labeled non-blank code lines; the actual prescribed code block is 9 lines (comment + 2 PEP 8 blank lines). Planner copied the 7-line claim verbatim into DEV/QA prompts. QA correctly resolved the mismatch as a counting-convention difference and marked deliverable verification PASS. Worth filing as a Forge observation: "count what you paste, not what the upstream artifact labels." Reference: `Done/diagnostic-bellows-test-isolation-conftest-2026-05-26.md` (SA blueprint), `Done/executable-bellows-test-isolation-conftest-2026-05-26.md` (executable), `knowledge/research/bellows-test-isolation-conftest-fixture-shape-2026-05-26.md` (full audit), `knowledge/qa/executable-bellows-test-isolation-conftest-2026-05-26.md` (QA verification + 4 evidence files).
```

### Entry unique identifier

Entries are identified by **date + parenthetical tag/phrase**:
- Open: `**Added <DATE>:** <description>`
- Closed: `**Closed <DATE> (<RETIREMENT_REASON>):** <description>` or `**Closed <DATE>:** <description>`

No slug, no sequence number. The date alone is insufficient (many entries share dates). The parenthetical (e.g., `(defer pending demonstrated need)`, `(RETIRE -- structurally resolved)`) provides disambiguation. Internally, entries reference each other by informal item numbers (e.g., "BACKLOG #5", "items #2, #3") — these are positional within the Open section and shift as entries are added/removed.

### Structured fields

Fields are inline within prose, not key-value frontmatter. Common patterns:

| Field | Open pattern | Closed pattern |
|-------|-------------|---------------|
| Date filed | `**Added <DATE>:**` | `(originally <DATE>)` |
| Closure date | n/a | `**Closed <DATE>:**` |
| Retirement reason | n/a | `(<REASON>)` in heading |
| Ship vehicle | n/a | `Shipped via <executable-slug> (commit <SHA>)` |
| Resolution options | `**Resolution shape (options):** (a)... (b)...` | n/a |
| Effort | `**Effort estimate:**` | n/a |
| Impact | `**Operational impact:**` | n/a |
| Disposition | `**Disposition recommendation:**` | `**Disposition:** defer` |
| Cross-references | `Reference:` | `Reference:` |
| Code indicator | n/a | `**No code changes shipped**` / `**REMINDER: restart Bellows daemon**` |

### SA Observation

The BACKLOG file is a single monolithic markdown file with two H2 sections. Entries are bullet-list items with rich inline metadata but no structured frontmatter. The lack of a formal identifier scheme (no slug, no sequence number) means the script must perform fuzzy matching — likely by extracting the date and a distinctive noun phrase from each entry. The `(originally <DATE>)` field in Closed entries provides the "date opened" anchor, while `**Added <DATE>:**` provides it for Open entries. The reference fields (commit SHAs, executable slugs, file paths) are the most reliable matching surface between BACKLOG and PROJECT_STATUS/git-log.

---

## Section B — PROJECT_STATUS File Shape

### Top-level section structure

```
# Bellows — Project Status                                 (H1 — file title)
## Status: Phase 1 Complete — Live (...)                   (H2 — current status)
## Completed                                               (H2 — reverse-chrono ledger)
## Pending (next session)                                  (H2)
## Blocked                                                 (H2)
## 2026-04-16 — Bellows Verdict + Resume Session           (H2 — historical session archive)
## 2026-04-16 — Bellows Reliability + Forge Evaluation ... (H2 — historical session archive)
## 2026-04-19 — Bellows _handle Subdirectory Guard + ...   (H2 — historical session archive)
```

Historical session sections use `### Session Arc`, `### Plans Shipped`, `### Diagnostics Shipped` sub-headings.

### Completed entry format (3 verbatim from most recent session, 2026-05-26)

```
- 2026-05-26: **Test-isolation conftest — `tests/conftest.py` added with autouse fixture redirecting `verdict.VERDICTS_DIR` to tmpdir.** Closes the 2 leaking tests (`test_bellows.py::test_apply_defensive_header_defaults_propagates_to_reparsed_header` and `test_consume_verdicts.py::test_dispatch_starts_fresh_when_db_has_orphan_slug_rows`) that wrote orphan `verdict-request-*` files to production `verdicts/pending/` during test runs. Function-scoped autouse fixture patches `verdict.VERDICTS_DIR` to `tmp_path / "verdicts"` — no production code changes, no test modifications required. Full suite: 411 passed, 5 known carry-overs, 0 regressions. Load-bearing verification: zero orphan files in `verdicts/pending/` after full-suite run. Rule 20 self-check PASSED. Reference: `executable-bellows-test-isolation-conftest-2026-05-26`, SA diagnostic at `knowledge/research/bellows-test-isolation-conftest-fixture-shape-2026-05-26.md`, dev log at `knowledge/development/bellows-test-isolation-conftest-2026-05-26.md`, QA at `knowledge/qa/executable-bellows-test-isolation-conftest-2026-05-26.md`.
```

```
- 2026-05-26: **Bellows hardening batch — items 1, 3, 4 (evidence string disambiguation, _seen on_modified invalidation, defensive default re-parse propagation).** Three independent hardening fixes for confirmed-Open BACKLOG items. Item 1: disambiguated the `_gate_rule_20_self_check` evidence string at `gates.py:441` — the no-md-paths branch now emits `"deposits block declares no .md paths..."` instead of the byte-identical string shared with the banner-absent branch at line 464, enabling distinct Planner routing at verdict-read time. Item 3: added `_seen` invalidation with lifecycle-prefix guard to `PlanHandler.on_modified` — corrected re-deposits at the same filename after rejection now trigger re-dispatch instead of being silently skipped; the guard (`in-progress-`, `verdict-pending-`, `halted-`) prevents re-dispatch loops on Bellows's own lifecycle renames. Item 4: added a second `_apply_defensive_header_defaults(header, total_steps)` call after `header = gate_result.get("plan_header", {})` reassignment at `bellows.py:499` — the re-parsed header now inherits the defensive default before being passed to `header_says_pause()` consumers. 4 regression tests added (3 new + 1 existing test fix). Full suite: 411 passed, 5 known carry-overs, 0 regressions. Rule 20 self-check PASSED. **REMINDER: restart Bellows daemon** to load all three fixes. Reference: `executable-bellows-hardening-batch-items-1-3-4-2026-05-26`, dev log at `knowledge/development/bellows-hardening-batch-items-1-3-4-2026-05-26.md`, QA at `knowledge/qa/executable-bellows-hardening-batch-items-1-3-4-2026-05-26.md`.
```

```
- 2026-05-26: **Fix F isinstance guard removal + test fixture conformance.** Removed the two defensive `isinstance(f, dict)` guards at `bellows.py:495` and `bellows.py:587` (added during the verdict-ledger-gate-result-preservation plan as contract-pollution defense) after updating the sole non-conformant test fixture in `test_run_plan_inprogress_entry_renames_to_verdict_pending` from string-list `["scope_check"]` to production dict shape `[{"gate": "scope_check", "evidence": "..."}]`. The 2026-05-21 Block 1 / Block 2 symmetric isinstance pattern at lines 509 and 600 is preserved (structurally distinct — `all()` predicates for rule_22 classification, not `.join()` log expressions). All test fixtures now conform to the production `list[dict]` contract. Full suite: 407 passed, 5 pre-existing carry-over failures, 0 regressions. Rule 20 self-check PASSED. Reference: `executable-fix-f-guard-removal-2026-05-26`, dev log at `knowledge/development/fix-f-guard-removal-2026-05-26.md`, QA at `knowledge/qa/executable-fix-f-guard-removal-2026-05-26.md`.
```

### Grouping and session boundaries

Completed entries are grouped by **date** in reverse-chronological order (newest first). Within a date group, entries are listed sequentially with no blank lines between them. Session boundaries within the `## Completed` section are **implicit** — entries for 2026-05-26 are contiguous (lines 7-24, ~11 entries), followed by 2026-05-25 entries (lines 25-62, ~10 entries), etc. No explicit heading, horizontal rule, or date-stamp separator between date groups.

Historical sessions (pre-2026-05 era) ARE marked with explicit `## DATE -- SessionTitle` headings below the Completed section, but recent sessions use only the inline date prefix.

### Matching text for script

A script can match Completed entries to BACKLOG entries via:

1. **Executable slug** (most reliable): `executable-<slug>-<YYYY-MM-DD>` in `Reference:` field
2. **Commit SHA**: `` Commit `<SHA>` `` inline
3. **Knowledge file paths**: `knowledge/<type>/<slug>-<YYYY-MM-DD>.md` in reference fields
4. **Date + bold title**: `<DATE>: **<title>**` prefix
5. **BACKLOG closure phrases**: free-text like "Closes 2026-05-24 BACKLOG entry", "closes BACKLOG item #5"

### SA Observation

The Completed section is a flat reverse-chronological ledger with no session delimiters. Each entry is a single bullet item on one line (very long lines). The **executable slug** in the `Reference:` field is the most reliable cross-reference key: it appears in both PROJECT_STATUS and BACKLOG Closed entries. Date-based grouping means a script can scope its scan to "entries with a date in the last N days" trivially via the `- <DATE>:` prefix.

---

## Section C — Git Log Shape

### Bellows submodule commits (last 30 days, verbatim)

```
e6c9d6d docs: session-9 NEXT_SESSION baton (WebSearch/WebFetch deferred + 2 LESSONS)
7cd112c chore: backlog hygiene — defer WebSearch/WebFetch allowedTools (3 incidents in 30 days, pre-load workaround sufficient)
7071adc docs: session-8 NEXT_SESSION baton (test-isolation conftest shipped, mcp__vexp__ retired, PLANNER_TEMPLATE v4.52)
8415435 chore: backlog hygiene — retire mcp__vexp__ READ_CLASS_TOOLS entry (shipped 2026-05-25, never closed)
c02d592 chore: backlog hygiene — close test-isolation conftest (Open → Closed) + lifecycle artifacts
8b1fed4 qa(bellows): test-isolation conftest verified — 411 passed, 0 regressions, leak closed
fde737b feat(bellows): add tests/conftest.py — isolate verdict writes to tmpdir
54fb8e1 research(bellows): test-isolation conftest fixture-shape diagnostic — 2 leaking tests, 7-LOC fixture blueprint
64ec823 docs: session-7 NEXT_SESSION baton (hardening batch shipped, 9 deferred horizon items)
71c98b0 chore: backlog hygiene — close items 1, 3, 4 (hardening batch ship)
c7d73be chore: session-wrap — BACKLOG hygiene (Item 2 closed, test-isolation entry filed), lifecycle artifacts
3d9f720 docs: prompt feedback — bellows QA hardening batch items 1, 3, 4
71b5d3c qa(bellows): hardening batch items 1, 3, 4 verified — 3 new regression tests pass, zero regressions
18587ba docs: prompt feedback — bellows DEV hardening batch items 1, 3, 4
af8e7f3 fix(bellows): hardening batch — items 1, 3, 4 (evidence string disambiguation, _seen on_modified invalidation, defensive default re-parse propagation)
cd7fad0 docs(bellows): freshness audit — Items 1,3,4 confirmed Open, Item 2 Closed-shipped
270c8a9 chore(bellows): write next-session baton for 2026-05-26 session 6
cf96a27 chore(bellows): session-wrap 2026-05-26 — BACKLOG hygiene, baton correction, lifecycle artifacts
d9637f5 docs: prompt feedback — bellows QA Fix F guard removal
2461549 qa(bellows): Fix F guard removal verified, test fixture conformance verified
612a490 docs: prompt feedback — bellows DEV Fix F guard removal
039d91b fix(bellows): remove Fix F isinstance guard at lines 495 and 587 after test fixture conformance update
37e9162 docs(bellows): teardown push silent-failure disposition — RETIRE
7bf28de docs(bellows): Phase 3b read-side disposition — RETIRE
6006f1e chore: session wrap 2026-05-26 — verdict-ledger gate-result preservation closed
572c670 docs(bellows): QA report + PROJECT_STATUS for verdict-ledger gate-result preservation
fe8f45e feat(verdict-ledger): preserve gate_result via JSON metadata line + expand terminal log
d6febf4 chore: session-wrap 2026-05-26 — scope_check forensics + truncation fix shipped
7380539 qa: parse-diff-stat truncation fix verified
69b7400 fix(bellows): widen _parse_diff_stat stat column to prevent path truncation
684a54d diagnostic(bellows): verdict ledger gate-result preservation — E.4 (JSON metadata line) recommended
10c95ca diagnostic(bellows): scope_check text-mention audit — INCONCLUSIVE, evidence-loss gap identified
abd5a29 chore: session-wrap 2026-05-26 — 3 plans, PROJECT_STATUS + NEXT_SESSION baton refresh
e940f5d diagnostic(bellows): scope_check post-fix behavior characterization — DESIGN-INTENT-AUDIT-NEEDED
f746e83 docs(planner-template): dev log for v4.51 Rule 21 carve-out
abc0241 diagnostic(bellows): parallel-SHA population audit — CLOSE-SUPERSEDED, 0/34 reproductions post-v4.47
1709c9c chore: session-wrap 2026-05-25 lifecycle artifacts + NEXT_SESSION baton
8dee77f qa(bellows): verify test_rule_26 set→list follow-up — 9/9 checks PASS, Rule 20 PASSED
bc1ecd9 test(rule_26): wrap result LHS in set() for 6 membership assertions — closes set→list carry-over
84e97d1 qa(bellows): verify file_change_audit fix — 9/9 checks PASS, Rule 20 PASSED
950436c fix(bellows): file_change_audit now detects committed changes — closes BACKLOG 2026-05-21
3ddb48b diagnostic(bellows): file_change_audit false-negative root cause — H1 CONFIRMED
0601471 qa(bellows): verify _extract_plan_required_deposits set→list — 7/7 checks PASS, Rule 20 PASSED
4e805fa fix(gates): _extract_plan_required_deposits set→list — deterministic md_paths[0] selection — closes BACKLOG capability
2fdfbab chore: session-wrap 2026-05-25 lifecycle artifacts + migrate_orphan_verdicts utility
fdfc827 docs: NEXT_SESSION baton 2026-05-25 — 5-plan drain of 2026-05-22 baton
a68a3e0 qa(bellows): verify READ_CLASS_TOOLS extension — 5/5 checks PASS, Rule 20 PASSED
9473cf7 fix(gates): extend READ_CLASS_TOOLS with 5 vexp read-class tools — closes BACKLOG mcp_tool_denials
1a01503 docs(research): MCP READ_CLASS_TOOLS exemption diagnostic — Shape A recommended
d7be5a7 qa(bellows): verify qa_steps governance documentation — 5/5 checks PASS
49ff26f docs(dev-log): qa_steps governance documentation — Step 1 deposit
25ff570 qa(bellows): verify qa_steps header field implementation — 7/7 checks PASS
f456515 fix(gates): qa_steps header field for authoritative QA-step detection — closes BACKLOG qa_step_detection (#audit-leak)
a9efb9b qa(bellows): verify bash-fallback documentation for settings.local.json
f2ef67a docs: add bash-fallback pattern for .claude/settings.local.json to BELLOWS_DEVELOPER.md
9dcd437 docs(backlog): close items #6, #7 (gate file-scoping) + deposit-ordering Open entry
8b62c5c docs: prompt feedback — bellows QA gate file scoping
7e575a4 qa(bellows): gate file-scoping fixes
eeaf75c docs: prompt feedback — bellows DEV gate file scoping
56f94f0 fix(gates): section-scoped table inspection + status tokens + rule_20 first-deposit scoping (items #6, #7)
81c4c58 diagnostic(gates): gate file-scoping characterization — items #6 and #7 are independent
0e270ed docs: prompt feedback — bellows QA precondition-failure field
e78253d qa(bellows): precondition-failure verdict-request field
8ebfdbc docs: prompt feedback — bellows DEV precondition-failure field
0a90e26 fix(bellows): precondition-failure verdict-request field — retries step instead of advancing (item #5)
ad17389 docs: prompt feedback — bellows QA rename-first ordering
59809d1 qa(bellows): rename-first ordering at all 4 pause sites
1385d3f docs: prompt feedback — bellows DEV rename-first ordering
10b5fc3 fix(bellows): rename-first ordering at all 4 pause sites — closes RV-1 boundary (items #2, #3)
009b204 docs(backlog): Phase 3b step-state-resume read-side never implemented (Open)
69afc8e docs(bellows): daemon-restart state divergence diagnostic — BACKLOG #2, #3, #5
59da5a4 docs: 2026-05-24 hardening pass — BACKLOG closures + post-mortem entry
d1bfc9a docs: prompt feedback — bellows QA remove pre-scan processed rename v2
82e50d0 qa(bellows): remove pre-scan processed- prefix rename v2
d3a1379 docs: prompt feedback — bellows DEV remove pre-scan processed rename v2
c2aeef4 fix(bellows): remove pre-scan processed- prefix rename — eliminates P0 multi-step pause-cycle loop
21468d5 docs(SA): processed-prefix re-consumption loop & rename-skip diagnostic findings
caee57a docs(backlog): daemon-restart recovery for orphaned in-progress plans with pending verdicts
445e822 docs(backlog): P0 — write-time processed-prefix normalization causes infinite verdict-replay loops
1ed4e83 docs(backlog): add path-keyed rejection cache + dirty-PROJECT_STATUS teardown variant
808dbff docs+chore: 2 BACKLOG entries (gate false positives) + 3 processed verdicts from invoice-pulse drift refresh session
```

(120+ commits in the last 30 days; full list truncated here, additional commits extend back to 2026-04-26.)

### Governance root submodule pointer bumps (last 30 days, verbatim)

```
820a41f chore: bump bellows submodule (session-9 baton)
88a26d5 chore: bump bellows submodule (WebSearch/WebFetch BACKLOG deferral)
b654c9c chore: bump bellows submodule (session-8 baton)
ae4f366 chore: bump bellows submodule (mcp__vexp__ backlog hygiene)
b49646e chore: bump bellows submodule (test-isolation conftest + backlog hygiene)
47bc582 chore: bump bellows submodule (session-7 baton)
658e847 chore: bump bellows submodule (BACKLOG hygiene close-out)
02d7803 chore: bump bellows submodule (session-7 hardening batch + BACKLOG hygiene)
08d0a7a chore: bump bellows submodule (NEXT_SESSION baton for 2026-05-26 session 6)
432cb79 chore(governance): session-wrap 2026-05-26 — LESSONS, roadmap archive, bellows submodule bump
c1c3e2d chore: session wrap 2026-05-26 — verdict-ledger close
a3f9957 lessons: 2026-05-26 — pause_for_verdict invariant + Deposits block discipline; bump bellows submodule
206647f docs: 1 LESSONS entry from 2026-05-26 Bellows hardening session + bump bellows submodule pointer
dc9ac40 chore: bump bellows submodule pointer (lifecycle artifacts wrap)
81cd488 chore: bump bellows submodule pointer (session-wrap 2026-05-25)
39beb01 chore: bump bellows submodule pointer (session-wrap 2026-05-25)
cb6d0e1 docs: LESSONS 2026-05-25 + bump bellows submodule (5-plan drain of 2026-05-22 baton)
ea64c88 chore: bump bellows submodule (2026-05-22 BACKLOG + processed verdicts from IP drift refresh)
```

(60+ governance-root commits in the last 30 days touching `bellows/`.)

### BACKLOG reference style in commit messages

Commits **do** explicitly reference BACKLOG entries, but via **informal, varied** patterns — no formal identifier:

- **By item number**: `close items 1, 3, 4`, `items #2, #3`, `item #5`, `BACKLOG #2, #3, #5`
- **By descriptive name**: `closes BACKLOG mcp_tool_denials`, `closes BACKLOG qa_step_detection (#audit-leak)`, `closes BACKLOG capability`
- **By date**: `closes BACKLOG 2026-05-21`
- **By lifecycle verb**: `close`, `closes`, `retire`, `defer`, `hygiene-close`
- **By category**: `backlog hygiene`, `BACKLOG closures`

### SA Observation

The commit-message-to-BACKLOG mapping is rich but unstructured. The `closes BACKLOG <name>` pattern appears in `fix()` and `feat()` commits at ship-time. The `chore: backlog hygiene` pattern appears in separate cleanup commits. A script scanning for BACKLOG closures must handle both — the ship-time commit (which names the feature) and the hygiene commit (which explicitly says "close"/"retire"/"defer"). The governance-root pointer bumps carry descriptive parentheticals but don't reference BACKLOG entries directly; the bellows-internal commits are the canonical source. The `-- closes BACKLOG <X>` suffix in commit subjects is the most parseable pattern.

---

## Section D — Recurrence Enumeration

The LESSONS.md entry (governance root, 2026-05-26, tags: `planner-discipline`, `backlog-hygiene`, `forge-candidate`) documents five recurrences. Below are both sides for each: the BACKLOG "leftover" entry and the ship event that should have triggered closure.

### Recurrence 1 — Session-6: `_extract_plan_required_deposits` set-to-list

**Side A (BACKLOG leftover) — Closed entry at BACKLOG.md line 38:**

```
- **Closed 2026-05-26 (RETIRE — structurally resolved):** `_extract_plan_required_deposits()` returns a `set` making `md_paths[0]` hash-dependent (originally 2026-05-24). Retired as structurally resolved by `executable-extract-plan-required-deposits-set-to-list-2026-05-25` (DEV+QA, shipped 2026-05-25 — before session 6 of 2026-05-26). The fix chose **Option (a)** from this BACKLOG entry: `_extract_plan_required_deposits` and `_filter_transient_paths` now return ordered lists via `paths = []` + `paths.append(...)` + `dict.fromkeys(paths)` dedup, preserving authoring order. [...] **No code changes shipped today** — BACKLOG hygiene closure only. The entry was authored 2026-05-24 and the fix landed 2026-05-25, but the Open entry was not moved to Closed at that time; it propagated through two session batons (session 5 baton 2026-05-26, session 6 baton 2026-05-26) as a live horizon item before catching at session-7 Phase 1.5.
```

**Side B (ship event) — PROJECT_STATUS.md line 17 + commit `4e805fa`:**

```
- 2026-05-25: **`_extract_plan_required_deposits` and `_filter_transient_paths` converted from `set` to `list`** (preserving authoring order via `re.finditer` walk order + `dict.fromkeys` dedup on the legacy prose-matching path); `md_paths[0]` selection in `_gate_rule_20_self_check` and `_gate_rule_22_verification` is now deterministic; [...] Closes 2026-05-24 BACKLOG `_extract_plan_required_deposits` capability entry. [...] Reference: `executable-extract-plan-required-deposits-set-to-list-2026-05-25`.
```

Ship commit: `4e805fa fix(gates): _extract_plan_required_deposits set→list — deterministic md_paths[0] selection — closes BACKLOG capability`

### Recurrence 2 — Session-7: precondition-failure verdict-request field duplicate

**Side A (BACKLOG leftover) — Closed entry at BACKLOG.md line 40:**

```
- **Closed 2026-05-26 (RETIRE — duplicate):** Step-counter loop after precondition-failure verdict (originally 2026-05-21). Duplicate of Closed entry below (`Closed 2026-05-24: Step-counter loop after precondition-failure verdict`) — shipped 2026-05-24 via `executable-precondition-failure-field-2026-05-24` (DEV commit `0a90e26`). The Open entry was a leftover that wasn't cleaned up when the fix shipped.
```

**Side B (ship event) — PROJECT_STATUS.md line 23 + commit `0a90e26`:**

```
- 2026-05-25: **Precondition-failure verdict-request field — closes BACKLOG item #5 (step-counter loop).** Added an explicit `**Precondition Failure:**` boolean field to the verdict-request format, implementing Shape E from the 2026-05-24 daemon-restart-state-divergence diagnostic [...] Reference: `executable-precondition-failure-field-2026-05-24`.
```

Ship commit: `0a90e26 fix(bellows): precondition-failure verdict-request field — retries step instead of advancing (item #5)`

### Recurrence 3 — Session-7: Phase 3b read-side step-state-resume

**Side A (BACKLOG leftover) — Closed entry at BACKLOG.md line 50:**

```
- **Closed 2026-05-26 (RETIRE):** Phase 3b step-state-resume (DB read-side) (originally 2026-05-24). Retired as won't-fix per disposition diagnostic [...] **Critical historical context surfaced by SA:** the read-side was previously shipped 2026-04-28 (`_get_last_completed_step(db_path, plan_slug)` helper + `run_plan()` query integration) and deliberately removed 2026-05-01 per the Phase 3b/3c cost-benefit diagnostic [...] The 2026-05-24 BACKLOG entry's "half-implemented" framing was imprecise; the accurate description is "fully implemented, evaluated, removed as dead code, write-side retained as benign."
```

**Side B (ship event) — BACKLOG.md Closed line 147 + PROJECT_STATUS.md line 88:**

BACKLOG (earlier Closed entry):
```
- **Closed 2026-05-01:** Phase 3b/3c DB step-state-resume slug-collision. Diagnostic at `knowledge/research/phase-3b-mechanism-and-cost-benefit-2026-05-01.md` confirmed phantom-resume mechanism. Q6 cost-benefit recommended F3 (remove dead code) [...] Reference: `executable-remove-phase-3b-3c-2026-05-01`.
```

PROJECT_STATUS:
```
- 2026-05-01 (later): Removed Phase 3b/3c DB step-state-resume logic per F3 recommendation [...] Dead code that guarded the unsupported manual-rename resume path; verdict-resume path passes resume_step explicitly and never used the DB-query path. Eliminates the slug-collision phantom-resume bug class entirely.
```

### Recurrence 4 — Session-8: `mcp__vexp__` READ_CLASS_TOOLS extension

**Side A (BACKLOG leftover) — Closed entry at BACKLOG.md line 28:**

```
- **Closed 2026-05-26 (RETIRE — structurally resolved):** MCP tool denials (`mcp__vexp__run_pipeline`, `mcp__vexp__get_context_capsule`) not on `READ_CLASS_TOOLS` exemption list (originally 2026-05-22). Retired as structurally resolved by `executable-mcp-read-class-tools-extension-2026-05-25` (DEV commit `9473cf7`, shipped 2026-05-25 — before session 6 of 2026-05-26). [...] Commit message literally reads "closes BACKLOG mcp_tool_denials." **No code changes shipped today** — BACKLOG hygiene closure only. The entry was authored 2026-05-22 and the fix landed 2026-05-25, but the Open entry was not moved to Closed at that time; it propagated through three session batons (sessions 5, 6, 7 of 2026-05-26) as a live horizon item before catching at session-8 Phase 1.5.
```

**Side B (ship event) — PROJECT_STATUS.md line 18 + commit `9473cf7`:**

```
- 2026-05-25: **`READ_CLASS_TOOLS` extended with 5 read-class vexp tools** (`get_context_capsule`, `get_session_context`, `get_skeleton`, `index_status`, `search_memory`); `save_observation` deliberately excluded as write-class. Closes 2026-05-22 BACKLOG entry on MCP tool denials. [...] Reference: `executable-mcp-read-class-tools-extension-2026-05-25`.
```

Ship commit: `9473cf7 fix(gates): extend READ_CLASS_TOOLS with 5 vexp read-class tools — closes BACKLOG mcp_tool_denials`

### Recurrence 5 — Session-9: WebSearch/WebFetch deferred

**Side A (BACKLOG leftover) — Closed entry at BACKLOG.md line 26:**

```
- **Closed 2026-05-26 (defer pending demonstrated need):** `WebSearch` and `WebFetch` not in Bellows-dispatched agents' `--allowedTools` list (originally 2026-05-22). Phase-1.5 audit verified the prior `permission-denial-history-audit-2026-05-22.md` findings [...] **Disposition:** defer. [...] **No code changes shipped today** — BACKLOG hygiene closure only.
```

**Side B (ship event):** No PROJECT_STATUS Completed entry exists because no code shipped. The "ship event" is the audit data itself — `knowledge/research/permission-denial-history-audit-2026-05-22.md` showed 3 incidents in 30 days, all from one session, with the pre-load workaround sufficient. The BACKLOG entry was carried through session batons as a "live horizon item" until the audit closed it via `defer` disposition.

Hygiene commit: `7cd112c chore: backlog hygiene — defer WebSearch/WebFetch allowedTools (3 incidents in 30 days, pre-load workaround sufficient)`

### SA Observation

Four of five recurrences (1, 2, 3, 4) are the same pattern: code shipped, commit message says "closes BACKLOG X," but the Open entry was never moved to Closed. A script matching commit messages containing `closes BACKLOG` against Open entries would have caught all four. Recurrence 5 is a different shape: no code shipped, but operational audit data demonstrated a `defer` disposition — the script would need to detect "stale horizon items" where external evidence (audit reports, incident counts) has overtaken the entry's framing, which is harder to automate. The four code-shipped cases are the low-hanging fruit and compose the ground-truth test set for v1.

---

## Section E — Existing Scripts

### `scripts/` inventory

```
scripts/
  migrate_config.py        (2386 bytes, Python)
  migrate_orphan_verdicts.py (3226 bytes, Python)
```

**`migrate_config.py`** — One-shot migration splitting `config.json` into operational + secrets files. Invoked: `cd bellows && python scripts/migrate_config.py`. Reads `config.json`, extracts `pushover` and `tailscale_ip` keys to `config.secrets.json`. Idempotent. No BACKLOG/PROJECT_STATUS scanning.

**`migrate_orphan_verdicts.py`** — One-shot migration renaming orphan `verdict-*.md` files in `verdicts/resolved/` to `processed-verdict-*.md` when no paired `verdict-pending-*` plan exists. Reads `config.json` for watched_projects, scans `verdicts/resolved/` directory. No BACKLOG/PROJECT_STATUS scanning, no git log mining.

### Naming conventions

- Python scripts, one file per migration
- Shebang: `#!/usr/bin/env python3`
- Module-level docstring with usage instructions and authority reference
- Constants for paths at module level
- Single `main()` or `migrate()` entry point
- `if __name__ == "__main__"` guard

### SA Observation

Neither existing script performs BACKLOG or PROJECT_STATUS scanning. Both are one-shot migrations for specific operational issues. The new script would be the first utility-class script (recurring use, not one-shot). The naming convention suggests `scripts/check_backlog_freshness.py` or similar. The existing scripts' pattern of using `BELLOWS_ROOT = Path(__file__).parent.parent.resolve()` for path resolution is reusable.

---

## Section F — Invocation Context

### Search results

Searched `knowledge/` for "session wrap", "session-start protocol", "Phase 1.5", and "housekeeping checklist."

**"Phase 1.5" references:** Found across many BACKLOG Closed entries (lines 28, 38, etc.) and NEXT_SESSION.md, always referring to the Planner's baton-read protocol — the first thing the Planner does at session start is read the NEXT_SESSION baton and validate its contents against current state. "Phase 1.5" is the name of this validation pass. It is not a Bellows feature; it is a Planner-side discipline step defined in PLANNER_TEMPLATE.md (governance root).

**"Session wrap" references:** Found in `knowledge/decisions/halted-executable-bellows-session-wrap-2026-05-01.md` (a halted session-wrap plan with Step 1 DEV, Step 2 Documentation, Step 3 QA), `knowledge/development/bellows-session-wrap-dev-log-2026-05-01.md`, and many Closed entries mentioning session-wrap as the context for BACKLOG hygiene. Session-wrap is Planner-driven, not automated — the Planner performs it at the end of each session.

**"Session-start protocol":** No dedicated file found in bellows knowledge. The session-start protocol is governed by PLANNER_TEMPLATE rules (governance root, not bellows). The closest bellows-local artifact is `NEXT_SESSION.md`, which serves as the baton between sessions.

**"Housekeeping checklist":** No dedicated file found. Housekeeping is implicit in the Planner's session-wrap behavior (update PROJECT_STATUS, close BACKLOG entries, write NEXT_SESSION baton).

### Natural insertion points

The NEXT_SESSION.md baton itself (line 66) explicitly identifies the insertion point:

> **Address the leftover-after-ship LESSON's tooling recommendation** — small standalone build (~30 min for a script that scans BACKLOG Open vs recent commit messages + PROJECT_STATUS Completed entries). Could be its own session or a wedge on top of another focus.

The LESSONS.md entry recommends "tooling, not rule" and identifies the Planner's Phase 1.5 as the current manual insertion point. Candidate insertion points for the automated script:

1. **Session-start (Phase 1.5):** Planner runs the script at session-start as part of baton validation. Natural fit — the script surfaces candidates BEFORE the Planner starts work. Requires Planner-side rule addition.
2. **Session-wrap:** Planner runs the script at session-wrap to catch any entries missed during the session. Less optimal — catches happen AFTER the session, not before.
3. **On-demand:** Script is invoked manually or by the Planner when BACKLOG hygiene is the explicit task. Lowest integration cost, but doesn't prevent the pattern.
4. **CI hook / Bellows daemon integration:** Script runs as part of Bellows plan lifecycle. Overkill for the current pattern (5 occurrences in 3 days, all caught at Phase 1.5).

### SA Observation

The natural insertion point is **session-start (Phase 1.5)**: the Planner reads the NEXT_SESSION baton, then runs the freshness-check script before planning any work. This matches the current manual discipline (grep BACKLOG Closed section + current code state) but automates it. The script's output would be a list of "candidate closures" that the Planner evaluates before propagating any baton-carried items. No Bellows daemon code change needed — the script is a standalone utility invoked by the Planner's `claude -p` subprocess or by the Planner directly. The `scripts/` directory with its existing Python naming convention is the natural home.

---

## Output Receipt

**Agent:** Bellows Systems Analyst
**Step:** 1
**Status:** Complete

### What Was Done

Read-only diagnostic investigating the input shapes for a planned BACKLOG-freshness-check script. Analyzed the structure and format of BACKLOG.md, PROJECT_STATUS.md, git commit log, LESSONS.md recurrence data, existing scripts, and invocation context. Deposited verbatim samples and SA observations for all six investigation areas (A-F).

### Files Deposited

- `bellows/knowledge/research/leftover-after-ship-tooling-scope-findings-2026-05-26.md` -- this file

### Files Created or Modified (Code)

- None (read-only diagnostic)

### Decisions Made

- Identified executable slug as the most reliable cross-reference key between BACKLOG and PROJECT_STATUS entries
- Identified `scripts/` directory with existing Python naming convention as the natural home for the new script
- Identified session-start (Phase 1.5) as the natural insertion point for automated freshness checking
- Classified recurrence 5 (WebSearch/WebFetch defer) as a different pattern shape from recurrences 1-4 (code-shipped-but-not-closed)

### Flags for CEO

- None

### Flags for Next Step

- The four code-shipped recurrences (1-4) have a clean matching signal: commit messages with `closes BACKLOG <X>`. Recurrence 5 (defer-disposition) is harder to automate and may be out of scope for v1.
- BACKLOG entries lack formal identifiers; the script must use fuzzy matching (date + noun phrase or executable slug from Reference field).
- PROJECT_STATUS entries are very long single-line bullets; the script should parse by date prefix `- <YYYY-MM-DD>:` and extract the `Reference:` field for slug matching.
- No existing script performs BACKLOG/PROJECT_STATUS scanning; no duplication risk.

### Files Read

| File | Purpose |
|------|---------|
| `knowledge/BACKLOG.md` | Section A — file shape, Open/Closed entries |
| `PROJECT_STATUS.md` | Section B — Completed entry format |
| `agents/BELLOWS_SYSTEMS_ANALYST.md` | Specialist file |
| `NEXT_SESSION.md` | Section F — invocation context |
| `scripts/migrate_config.py` | Section E — existing scripts |
| `scripts/migrate_orphan_verdicts.py` | Section E — existing scripts |
| `/Users/marklehn/Developer/GitHub/LESSONS.md` (governance root) | Section D — recurrence enumeration |
| git log (bellows + governance root, 30 days) | Section C — commit shape |

### Sample Counts

| Section | Samples |
|---------|---------|
| A — BACKLOG Open entries | 3 verbatim |
| A — BACKLOG Closed entries | 3 verbatim |
| B — PROJECT_STATUS Completed entries | 3 verbatim |
| C — Bellows git log subjects | 120+ (full 30-day window) |
| C — Governance pointer bumps | 60+ (full 30-day window) |
| D — Recurrence pairs (both sides) | 5 of 5 |
| E — Existing scripts | 2 of 2 |
| F — Invocation context references | 4 candidate insertion points |
