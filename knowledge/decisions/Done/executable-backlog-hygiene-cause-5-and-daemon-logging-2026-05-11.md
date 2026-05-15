# Executable — Bellows BACKLOG Hygiene: Cause 5 RC2 Closure + Daemon Code-Version Logging Entry

**Project:** bellows
**Type:** Executable
**Priority:** 20
**Author:** Planner
**Date:** 2026-05-11
**Auto-close:** false
**Test scope:** none (markdown-only BACKLOG edits, grep verification only)
**Execution Map:** Step 1 (Documentation Analyst) → Step 2 (QA)

## Context

Today's session shipped two diagnostics + one governance executable resolving
`deposit_exists` false-positive Cause 5 (plan-agent evidence path convention
mismatch). The current Bellows BACKLOG already contains an open 2026-05-10
entry referencing this failure mode as "RC2 (MEDIUM confidence) — legacy prose
regex in `_extract_plan_required_deposits` captures unresolvable abbreviated
paths. Resolution path: ensure all plan steps use explicit `**Deposits:**`
blocks per Rule 26 — governance-only, no code change required."

That entry framed RC2 as a hypothetical resolution path. Today's audit
(`bellows/knowledge/research/deposit-exists-false-positive-audit-2026-05-11.md`)
empirically confirmed RC2 was the actual root cause for 18 gate-failure lines
across 3 verdict requests. The Rule 26 governance tightening shipped this
session in PLANNER_TEMPLATE v4.37 (commit `75904fd` at governance root)
codifies the resolution structurally.

Additionally, the daemon code-version logging observability ask surfaced in
the same audit — three Group B reproductions on 5-07/5-08 traced to daemon
running stale code after commit `e609ad3` shipped (Bellows does not hot-reload;
no mechanism to detect code-vs-runtime drift).

Two BACKLOG.md edits required:

1. **New Closed entry** capturing empirical RC2 closure with citation to the
   audit + Rule 26 v4.37 + executable filenames.
2. **New Open entry** capturing daemon code-version logging as a low-priority
   observability ask.

**Commit-repo discipline:** Both edits are inside the bellows project
(`bellows/knowledge/BACKLOG.md`). Single-repo commit, no governance-root
involvement.

## STEP 1 — Documentation Analyst: Apply two surgical edits to bellows BACKLOG

Read first:
- `/Users/marklehn/Desktop/GitHub/bellows/agents/BELLOWS_DOCUMENTATION_ANALYST.md`
- `/Users/marklehn/Desktop/GitHub/bellows/knowledge/BACKLOG.md` (current state — review the existing 2026-05-10 RC2 entry under Open so you understand context)
- `/Users/marklehn/Desktop/GitHub/bellows/knowledge/research/deposit-exists-false-positive-audit-2026-05-11.md` (citation source for the Closed entry)

You are the Documentation Analyst. Apply two surgical edits to
`/Users/marklehn/Desktop/GitHub/bellows/knowledge/BACKLOG.md`. Use `Edit` tool
calls with byte-exact `old_string` anchors.

### Edit 1 — Insert new Closed entry at top of Closed section

**Anchor (byte-exact — the `## Closed` header followed by its blank line):**

```
## Closed

- **Closed 2026-05-10:** Multi-line bold header parser gap (originally 2026-05-10 same-day).
```

**Replacement (preserves the existing `Closed 2026-05-10` row immediately after the new entry):**

```
## Closed

- **Closed 2026-05-11:** `deposit_exists` Cause 5 — plan-agent evidence path convention mismatch. Closure of the 2026-05-10 entry's RC2 ("legacy prose regex in `_extract_plan_required_deposits` captures unresolvable abbreviated paths — Resolution path: ensure all plan steps use explicit `**Deposits:**` blocks per Rule 26"). Today's audit (`bellows/knowledge/research/deposit-exists-false-positive-audit-2026-05-11.md`) empirically confirmed RC2 as the actual root cause for 18 gate-failure lines across 3 verdict requests on 2026-05-07/08 (action-queue-aggregation, action-queue-limit-and-contract-name, bellows-qa-prefix-and-skip-logging). Mechanism: plans declared bare `evidence/foo.txt` paths in `**Deposits:**` blocks while agents created files at `knowledge/qa/evidence/<slug>/foo.txt` — none of `_resolve_deposit_path()`'s four strategies could bridge the structural gap (Strategy 0 tries `wt_path/evidence/foo.txt`, Strategy 2 tries `project_path/evidence/foo.txt`, neither exists). Follow-up canary diagnostic (`Done/diagnostic-rule-26-directory-bullet-canary-2026-05-11.md`) verified the current gate accepts directory-only `**Deposits:**` bullets via `os.path.isfile() or os.path.isdir()` at every strategy (`gates.py:183-212`), authorizing the Path A resolution. Governance fix shipped via `Done/executable-rule-26-evidence-path-fix-2026-05-11.md` (PLANNER_TEMPLATE v4.37, governance-root commit `75904fd`): Rule 26 tightened from permissive ("evidence files do NOT need individual bullets") to mandatory ("evidence files MUST be represented by the evidence directory as a single bullet; Do NOT list individual evidence files"). No Bellows code change required — the gate already accepted directory bullets correctly; the failure was in plan-authoring convention. Three Lessons rows added at governance root (2026-05-11): stale-lesson retraction of 2026-04-19 directory-prohibition (made stale by commit `e609ad3`), Cause 5 capture with meta-lesson on mandatory governance language, and diagnostic-before-executable discipline win on the canary catch. Reference: `Done/diagnostic-deposit-exists-false-positive-audit-2026-05-11.md`, `Done/diagnostic-rule-26-directory-bullet-canary-2026-05-11.md`, `Done/executable-rule-26-evidence-path-fix-2026-05-11.md`.

- **Closed 2026-05-10:** Multi-line bold header parser gap (originally 2026-05-10 same-day).
```

### Edit 2 — Insert new Open entry at top of Open section

**Anchor (byte-exact — the `## Open` header followed by its blank line):**

```
## Open

- 2026-05-10: **`extract_total_steps()` counts `## STEP N` patterns regardless of code-fence or string-literal context.**
```

**Replacement (preserves the existing 2026-05-10 entry immediately after the new entry):**

```
## Open

- 2026-05-11: **Daemon code-version observability gap — no mechanism to detect code-vs-runtime drift.** Bellows does not hot-reload Python modules; code changes to `bellows.py`, `gates.py`, `verdict.py`, `parser.py`, `runner.py`, or any other module require manual daemon restart by the CEO. Today's `deposit_exists` audit (`bellows/knowledge/research/deposit-exists-false-positive-audit-2026-05-11.md`) found three post-fix reproductions on 2026-05-07/08 where the daemon ran pre-fix code despite commit `2016d02` (worktree-first resolution fix) having shipped 2026-05-06. The fix existed on disk but wasn't loaded into memory. The 2026-04-19 Lessons entry already documents the restart-discipline requirement, and the Rule-26-live-gate-smoke-test pattern catches stale-code scenarios reactively. But there is no proactive observability: the running daemon does not log its loaded-code version, mtime, or hash anywhere visible to the operator. Without this, "is the daemon running the latest code?" requires a process restart to verify positively — restart kills in-flight plans, so the check is operationally expensive. **Fix shape:** at daemon startup, log the mtime (or git HEAD short SHA, if running inside a git repo) of `gates.py`, `verdict.py`, `parser.py`, `runner.py`, and `bellows.py` itself. A single info-level log line on startup. Optionally, surface the same data in the periodic heartbeat (every Nth heartbeat) so a long-running daemon's loaded version remains visible without rolling back to startup logs. Scope: ~10-15 LOC + 1-2 unit tests verifying the startup-log format. Operational impact while open: detecting daemon-running-stale-code requires inferring from gate-failure patterns + commit timestamps (the audit pattern used today). Priority: low — workaround exists (daemon restart + Rule 26 canary), and the Rule 26 governance fix shipped today reduces the class of failures that would surface this gap. Reference: today's audit findings file, 2026-04-19 Bellows-hot-reload Lessons entry.

- 2026-05-10: **`extract_total_steps()` counts `## STEP N` patterns regardless of code-fence or string-literal context.**
```

### Verification before commit

After applying both edits, run these greps against
`/Users/marklehn/Desktop/GitHub/bellows/knowledge/BACKLOG.md` and confirm each
returns exactly 1 match:

```bash
grep -c "Closed 2026-05-11.*Cause 5 — plan-agent evidence path convention mismatch" /Users/marklehn/Desktop/GitHub/bellows/knowledge/BACKLOG.md
grep -c "2026-05-11.*Daemon code-version observability gap" /Users/marklehn/Desktop/GitHub/bellows/knowledge/BACKLOG.md
grep -c "75904fd" /Users/marklehn/Desktop/GitHub/bellows/knowledge/BACKLOG.md
grep -c "executable-rule-26-evidence-path-fix-2026-05-11" /Users/marklehn/Desktop/GitHub/bellows/knowledge/BACKLOG.md
```

Each must return 1. If any returns 0, the edit failed — re-apply before
committing.

### Commit

The BACKLOG.md edit commits to the **bellows project repo**. Run:

```bash
cd /Users/marklehn/Desktop/GitHub/bellows/ && \
git add knowledge/BACKLOG.md && \
git commit -m "docs(backlog): close Cause 5 RC2, open daemon code-version logging

- Closed 2026-05-11: deposit_exists Cause 5 (plan-agent evidence path
  convention mismatch). Closure of 2026-05-10 RC2 hypothetical resolution
  path. Today's audit empirically confirmed RC2 as root cause; Rule 26
  governance tightening shipped this session (PLANNER_TEMPLATE v4.37,
  governance-root commit 75904fd).
- Open 2026-05-11: daemon code-version observability gap. No mechanism to
  detect code-vs-runtime drift; fix shape proposed (startup log + heartbeat
  surfacing mtime/SHA of core modules)."
```

Do NOT push — CEO handles push.

### Dev log

Deposit a brief dev log to
`/Users/marklehn/Desktop/GitHub/bellows/knowledge/development/backlog-hygiene-cause-5-and-daemon-logging-dev-log-2026-05-11.md`
capturing: the two edits applied, the verification grep output (paste literal
counts), and the commit SHA. Keep it under 50 lines.

Commit the dev log to the bellows project repo:

```bash
cd /Users/marklehn/Desktop/GitHub/bellows/ && \
git add knowledge/development/backlog-hygiene-cause-5-and-daemon-logging-dev-log-2026-05-11.md && \
git commit -m "docs(bellows): backlog hygiene dev log 2026-05-11"
```

**Deposits:**
- `/Users/marklehn/Desktop/GitHub/bellows/knowledge/BACKLOG.md`
- `bellows/knowledge/development/backlog-hygiene-cause-5-and-daemon-logging-dev-log-2026-05-11.md`

## STEP 2 — QA: Verify BACKLOG edits landed correctly

Read first:
- `/Users/marklehn/Desktop/GitHub/bellows/agents/BELLOWS_QA.md`
- `bellows/knowledge/development/backlog-hygiene-cause-5-and-daemon-logging-dev-log-2026-05-11.md`

You are the QA Analyst. Verify Step 1's two edits to
`bellows/knowledge/BACKLOG.md` via grep checks and structural sanity. No test
suite exists for BACKLOG markdown; this QA is grep-driven plus section-structure
verification.

**Method:**

For each check below, capture literal command output to an evidence file under
`bellows/knowledge/qa/evidence/backlog-hygiene-cause-5-and-daemon-logging-2026-05-11/`
via Python file I/O or shell redirect.

1. **grep_closed_entry.txt** — verify Closed entry landed:
   `grep -n "Closed 2026-05-11.*Cause 5 — plan-agent evidence path convention mismatch" /Users/marklehn/Desktop/GitHub/bellows/knowledge/BACKLOG.md`
   Expect 1 match.

2. **grep_open_entry.txt** — verify Open entry landed:
   `grep -n "2026-05-11.*Daemon code-version observability gap" /Users/marklehn/Desktop/GitHub/bellows/knowledge/BACKLOG.md`
   Expect 1 match.

3. **grep_audit_reference.txt** — verify the audit findings file is cited:
   `grep -n "deposit-exists-false-positive-audit-2026-05-11.md" /Users/marklehn/Desktop/GitHub/bellows/knowledge/BACKLOG.md`
   Expect ≥2 matches (referenced from both the Closed entry and the new Open entry).

4. **grep_governance_commit.txt** — verify governance commit SHA cited:
   `grep -n "75904fd" /Users/marklehn/Desktop/GitHub/bellows/knowledge/BACKLOG.md`
   Expect 1 match (in the Closed entry).

5. **grep_executable_reference.txt** — verify the Rule 26 executable is cited:
   `grep -n "executable-rule-26-evidence-path-fix-2026-05-11" /Users/marklehn/Desktop/GitHub/bellows/knowledge/BACKLOG.md`
   Expect 1 match.

6. **section_structure.txt** — verify the file structure is intact (Open
   section before Closed section, both sections present, both new entries land
   in correct sections). Run via Python:

   ```python
   with open('/Users/marklehn/Desktop/GitHub/bellows/knowledge/BACKLOG.md') as f:
       lines = f.read().splitlines()

   open_idx = None
   closed_idx = None
   for i, line in enumerate(lines):
       if line.strip() == '## Open':
           open_idx = i
       elif line.strip() == '## Closed':
           closed_idx = i

   assert open_idx is not None, '## Open section missing'
   assert closed_idx is not None, '## Closed section missing'
   assert open_idx < closed_idx, 'Open section must come before Closed section'

   # Find the new Open entry — must be after open_idx and before closed_idx
   new_open_found = None
   new_closed_found = None
   for i, line in enumerate(lines):
       if 'Daemon code-version observability gap' in line:
           new_open_found = i
       if 'Closed 2026-05-11' in line and 'Cause 5' in line:
           new_closed_found = i

   assert new_open_found is not None, 'New Open entry missing'
   assert new_closed_found is not None, 'New Closed entry missing'
   assert open_idx < new_open_found < closed_idx, f'New Open entry at line {new_open_found+1} not in Open section ({open_idx+1}–{closed_idx+1})'
   assert new_closed_found > closed_idx, f'New Closed entry at line {new_closed_found+1} not in Closed section (after line {closed_idx+1})'

   print(f'PASS: Open section at line {open_idx+1}, Closed at line {closed_idx+1}')
   print(f'PASS: New Open entry at line {new_open_found+1} (correctly in Open section)')
   print(f'PASS: New Closed entry at line {new_closed_found+1} (correctly in Closed section)')
   ```

7. **git_log.txt** — verify both commits landed in bellows project repo:
   `cd /Users/marklehn/Desktop/GitHub/bellows/ && git log --oneline -5 -- knowledge/BACKLOG.md knowledge/development/backlog-hygiene-cause-5-and-daemon-logging-dev-log-2026-05-11.md`
   Expect at least two recent commits: the BACKLOG.md commit and the dev-log commit.

8. **Run Rule 20 self-check** in the QA report. Read the canonical Python
   block from `/Users/marklehn/Desktop/GitHub/RULE_20_SELF_CHECK_BLOCK.md`,
   fill in placeholders with these values, and run it:

   - `plan_slug`: `executable-backlog-hygiene-cause-5-and-daemon-logging-2026-05-11`
   - `qa_report_path`: `/Users/marklehn/Desktop/GitHub/bellows/knowledge/qa/backlog-hygiene-cause-5-and-daemon-logging-qa-2026-05-11.md`
   - `evidence_dir`: `/Users/marklehn/Desktop/GitHub/bellows/knowledge/qa/evidence/backlog-hygiene-cause-5-and-daemon-logging-2026-05-11/`
   - `required_evidence_files`: `['grep_closed_entry.txt', 'grep_open_entry.txt', 'grep_audit_reference.txt', 'grep_governance_commit.txt', 'grep_executable_reference.txt', 'section_structure.txt', 'git_log.txt']`

9. **Deposit the QA report** at
   `bellows/knowledge/qa/backlog-hygiene-cause-5-and-daemon-logging-qa-2026-05-11.md`
   with:
   - Summary (one paragraph).
   - Results table (one row per check 1–7) using only ✅/❌/⚠ glyphs as
     standalone cell values. No hedging keywords in positive-status rows.
   - Evidence file references (one row per evidence file).
   - Rule 20 self-check banner and PASSED line at the end.

### Commit

The QA report and evidence files commit to the bellows project repo:

```bash
cd /Users/marklehn/Desktop/GitHub/bellows/ && \
git add knowledge/qa/backlog-hygiene-cause-5-and-daemon-logging-qa-2026-05-11.md \
        knowledge/qa/evidence/backlog-hygiene-cause-5-and-daemon-logging-2026-05-11/ && \
git commit -m "qa(backlog): verify cause 5 closure and daemon-logging open entry"
```

Do NOT push.

**Out of scope:**
- Do not modify BACKLOG.md.
- Do not run any test suite — there isn't one for BACKLOG markdown.
- Do not assess whether the BACKLOG entries are *correct content* — that's the
  Planner's Rule 22 verification step. QA only verifies the edits landed and
  the file structure is intact.

**Deposits:**
- `bellows/knowledge/qa/backlog-hygiene-cause-5-and-daemon-logging-qa-2026-05-11.md`
- `bellows/knowledge/qa/evidence/backlog-hygiene-cause-5-and-daemon-logging-2026-05-11/` (multiple files per Rule 20 self-check)
