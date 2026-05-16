# executable — Lessons Forge extraction Phase B.2: governance wiring

**Plan ID:** executable-lessons-forge-extraction-phase-b2-governance-wiring-2026-05-18
**Date:** 2026-05-18
**Project:** governance root (cross-cutting; touches governance/, bellows/, lessons-forge/)
**Working directory:** `/Users/marklehn/Developer/GitHub/`
**Priority:** 1
**Depends on:** none (B.1 cutover `executable-lessons-forge-extraction-phase-b1-cutover-2026-05-17` is in forge/Done/)
**auto_close:** false

---

## Context

Phase B.1 (forge-side cutover) shipped 2026-05-17. Forge no longer contains Lessons Forge code, schema, or data. `lessons-forge` is pushed to its own GitHub remote at `EverestMons/forge_lessons`, HEAD `3cbc790`. The local `lessons-forge/` directory is still an untracked entry at the governance root, NOT yet a submodule. Three governance documents (ADR-002, ADR-003, ARCHITECTURE.md) still reference the old `forge/src/lessons_forge.py` paths. Bellows does NOT yet watch `lessons-forge/knowledge/decisions/`.

This plan closes the extraction: edits the three stale governance docs, registers `lessons-forge` as a submodule of the governance root, appends the new watch to `bellows/config.json`, restarts Bellows, and verifies end-to-end with a canary deposit.

All verbatim text for the doc edits is cited from `forge/knowledge/research/lessons-forge-phase-b-unknowns-2026-05-17.md` (per Rule 27). No Planner source reads were performed.

---

## Gap Assessment

Not applicable — this is an executable, not a change-proposing diagnostic.

---

## Rule 22 verification anchors

| Step | Anchor | Verification check |
|---|---|---|
| 1 | `governance/adr/ADR-002-lessons-forge-design.md` | grep zero hits for `forge/src/lessons_forge.py`, zero hits for `forge/agents/FORGE_LESSONS_AGENT.md`, zero hits for `Desktop/GitHub`; line 32 no longer says "not a separate repository"; line 76 says `lessons-forge.db` not `forge.db` |
| 2 | `governance/adr/ADR-003-orchestrator-plan-pattern.md` | grep zero hits for `forge/src/lessons_forge.py`; line 196 cites `lessons-forge/src/lessons_forge.py` |
| 3 | `ARCHITECTURE.md` | line 116 no longer contains `(proposed)`; line 124 references `lessons-forge/PROJECT_BRIEF.md`, not "Design pending" |
| 4 | governance-root `.gitmodules` | contains `[submodule "lessons-forge"]` block with `path = lessons-forge` and `url = git@github.com:EverestMons/forge_lessons.git`; `git submodule status` shows clean prefix (space) for `lessons-forge` |
| 5 | `bellows/config.json` | `watched_projects` array contains `"/Users/marklehn/Developer/GitHub/lessons-forge/knowledge/decisions"` as last entry; previous entry now has trailing comma; valid JSON (`python3 -m json.tool` succeeds) |
| 6 | Bellows daemon | new daemon PID different from pre-restart PID; startup log lists 9 watched projects including lessons-forge |
| 7 | git remote state | bellows submodule pushed to `origin/main`; governance root pushed to `origin/main`; `git submodule status` clean for all three submodules |
| 8 | canary | plan dispatched within 60s of deposit, completes successfully, Output Receipt reports `cwd` and `watched_count` flags |

---

## STEP 1 — Edit ADR-002

**Agent:** Developer

Edit `governance/adr/ADR-002-lessons-forge-design.md` to remove all stale `forge/src/lessons_forge.py` and `forge/agents/FORGE_LESSONS_AGENT.md` references, and fix the stale `/Desktop/GitHub/` path. All target text is verbatim from the unknowns diagnostic findings.

### Edits (use `Edit` tool, exact match)

**Edit A — line 32, replace location-and-invocation paragraph:**

OLD STRING (exact, from unknowns diagnostic Q4):
```
Lessons Forge is a new mode inside the existing Forge codebase, not a separate repository. Implementation lives in `forge/src/lessons_forge.py`. The module exposes `run_full_lessons_cycle(conn)` as the primary entry point, mirroring Prompt Forge's `run_full_research_cycle(conn)` pattern for signature consistency. There is no CLI entrypoint. Invocation happens through Claude Code plan steps using inline Python, consistent with Prompt Forge and Anvil.
```

NEW STRING:
```
Lessons Forge is a separate repository at `lessons-forge/`, registered as a submodule of the governance root. Implementation lives in `lessons-forge/src/lessons_forge.py`. The module exposes `run_full_lessons_cycle(conn)` as the primary entry point, mirroring Prompt Forge's `run_full_research_cycle(conn)` pattern for signature consistency. There is no CLI entrypoint. Invocation happens through Claude Code plan steps using inline Python, consistent with Prompt Forge and Anvil.
```

**Edit B — line 34, replace agent path:**

OLD STRING (exact, from unknowns diagnostic Q4):
```
A dedicated agent specialist file is created at `forge/agents/FORGE_LESSONS_AGENT.md`. The agent handles the classification step, which requires per-entry LLM judgment that cannot be expressed as deterministic code.
```

NEW STRING:
```
A dedicated agent specialist file is created at `lessons-forge/agents/FORGE_LESSONS_AGENT.md`. The agent handles the classification step, which requires per-entry LLM judgment that cannot be expressed as deterministic code.
```

**Edit C — line 76, replace DB reference:**

The unknowns diagnostic noted line 76 references `lesson_proposals` in `forge.db`. Read line 76 directly to get exact surrounding text, then replace `forge.db` with `lessons-forge.db` in that context. If the substring `forge.db` appears in multiple places on or near that line, use enough surrounding context to make the match unique. Do NOT replace any other reference to `forge.db` in the file — only the one tied to the `lesson_proposals` table.

**Edit D — line 145, fix stale relocation path:**

OLD STRING (substring, distinctive enough):
```
/Users/marklehn/Desktop/GitHub/LESSONS.md
```

NEW STRING:
```
/Users/marklehn/Developer/GitHub/LESSONS.md
```

### Verification

After all four edits:
```bash
cd /Users/marklehn/Developer/GitHub
grep -n 'forge/src/lessons_forge\.py' governance/adr/ADR-002-lessons-forge-design.md
grep -n 'forge/agents/FORGE_LESSONS_AGENT\.md' governance/adr/ADR-002-lessons-forge-design.md
grep -n 'Desktop/GitHub' governance/adr/ADR-002-lessons-forge-design.md
```

All three greps must return zero hits. If any returns a hit, stop and report.

Also verify the new text landed:
```bash
grep -n 'lessons-forge/src/lessons_forge\.py' governance/adr/ADR-002-lessons-forge-design.md
grep -n 'lessons-forge/agents/FORGE_LESSONS_AGENT\.md' governance/adr/ADR-002-lessons-forge-design.md
grep -n 'lessons-forge\.db' governance/adr/ADR-002-lessons-forge-design.md
```

Expected: at least one hit each.

### Deposits
- `governance/adr/ADR-002-lessons-forge-design.md` (modified)
- `knowledge/development/phase-b-2-step-1-2026-05-18.md` (dev log capturing the four edits, verification grep results)

---

## STEP 2 — Edit ADR-003

**Agent:** Developer

Single line edit citing unknowns diagnostic Q5.

OLD STRING (exact, from unknowns diagnostic Q5):
```
2. **Lessons Forge** (forge/src/lessons_forge.py, per ADR-002) — runs after Prompt Forge completes
```

NEW STRING:
```
2. **Lessons Forge** (lessons-forge/src/lessons_forge.py, per ADR-002) — runs after Prompt Forge completes
```

### Verification

```bash
cd /Users/marklehn/Developer/GitHub
grep -n 'forge/src/lessons_forge\.py' governance/adr/ADR-003-orchestrator-plan-pattern.md
grep -n 'lessons-forge/src/lessons_forge\.py' governance/adr/ADR-003-orchestrator-plan-pattern.md
```

First grep: zero hits. Second grep: at least one hit (line 196). Otherwise stop and report.

### Deposits
- `governance/adr/ADR-003-orchestrator-plan-pattern.md` (modified)
- `knowledge/development/phase-b-2-step-2-2026-05-18.md` (dev log)

---

## STEP 3 — Edit ARCHITECTURE.md

**Agent:** Developer

Two edits citing unknowns diagnostic Q6.

**Edit A — line 116, drop the `(proposed)` label:**

OLD STRING (exact):
```
### Lessons Forge (proposed)
```

NEW STRING:
```
### Lessons Forge
```

**Edit B — line 124, replace the Reference field:**

OLD STRING (exact, from unknowns diagnostic Q6):
```
**Reference:** Design pending. This document establishes the architectural position; implementation design follows.
```

NEW STRING:
```
**Reference:** `lessons-forge/PROJECT_BRIEF.md` (operational details); `governance/adr/ADR-002-lessons-forge-design.md` (implementation design).
```

### Verification

```bash
cd /Users/marklehn/Developer/GitHub
grep -n '### Lessons Forge (proposed)' ARCHITECTURE.md
grep -n 'Design pending' ARCHITECTURE.md
grep -n 'lessons-forge/PROJECT_BRIEF\.md' ARCHITECTURE.md
```

First two greps: zero hits. Third grep: at least one hit. Otherwise stop and report.

### Deposits
- `ARCHITECTURE.md` (modified)
- `knowledge/development/phase-b-2-step-3-2026-05-18.md` (dev log)

---

## STEP 4 — Register lessons-forge as submodule

**Agent:** Developer

The `lessons-forge/` directory currently exists as an untracked entry at the governance root with its own `.git`. Standard `git submodule add` is the preferred path; the 2026-05-15 submodule-limbo LESSONS entry documents the hand-write fallback.

### Primary path (preferred)

```bash
cd /Users/marklehn/Developer/GitHub
git submodule add git@github.com:EverestMons/forge_lessons.git lessons-forge
```

**Expected outcomes:**
- `.gitmodules` gains a `[submodule "lessons-forge"]` block
- `lessons-forge` is added to the index as a gitlink (mode 160000)
- No working-tree changes to `lessons-forge/` contents

**If the command succeeds** (exit code 0): proceed to verification.

**If the command fails** with a message about the path already existing or a `.git` already present at the target: switch to the fallback path below. Do NOT delete or rename `lessons-forge/` to try to coerce the primary path — the working tree must remain intact.

### Fallback path (per 2026-05-15 LESSONS submodule-limbo entry)

Hand-write `.gitmodules` and initialize:

```bash
cd /Users/marklehn/Developer/GitHub

# Append to .gitmodules (preserve existing entries for anvil and bellows)
cat >> .gitmodules <<'EOF'
[submodule "lessons-forge"]
	path = lessons-forge
	url = git@github.com:EverestMons/forge_lessons.git
EOF

# Stage the lessons-forge directory as a gitlink
git add lessons-forge

# Initialize the submodule in .git/config
git submodule init lessons-forge
```

### Verification (both paths converge here)

```bash
cd /Users/marklehn/Developer/GitHub
cat .gitmodules
git submodule status
git status --porcelain
```

Expected:
- `.gitmodules` contains three blocks: anvil, bellows, lessons-forge
- `git submodule status` shows three entries, all with a clean prefix (space, not `+` or `-`)
- `git status --porcelain` shows `A  .gitmodules` (or `M  .gitmodules` if it was already modified by the primary path), `A  lessons-forge` (or equivalent), and NO `??  lessons-forge/` line

If `git submodule status` shows `+` or `-` prefix on lessons-forge, stop and report. Both indicate the working tree HEAD doesn't match the recorded gitlink — investigate before continuing.

### Deposits
- `.gitmodules` (modified)
- `lessons-forge` (now a gitlink in the index, not an untracked dir)
- `knowledge/development/phase-b-2-step-4-2026-05-18.md` (dev log noting which path was taken — primary or fallback — and the verification output)

---

## STEP 5 — Edit bellows/config.json

**Agent:** Developer

Add the lessons-forge decisions/ path to the watched_projects array. The unknowns diagnostic Q7 confirmed the file uses strict JSON (no trailing commas) and the last entry currently has no trailing comma.

### Edit

Open `bellows/config.json`. Locate the line containing:
```
    "/Users/marklehn/Developer/GitHub/bellows/knowledge/decisions"
```

Replace that single line with these two lines (note the added comma on what is now the second-to-last entry):
```
    "/Users/marklehn/Developer/GitHub/bellows/knowledge/decisions",
    "/Users/marklehn/Developer/GitHub/lessons-forge/knowledge/decisions"
```

Use the `Edit` tool for this — `old_string` should be the single bellows line; `new_string` should be the two lines including the new comma. This anchors the edit precisely without depending on line numbers.

### Verification

```bash
cd /Users/marklehn/Developer/GitHub
python3 -m json.tool < bellows/config.json > /dev/null && echo "JSON valid"
python3 -c "import json; cfg = json.load(open('bellows/config.json')); paths = cfg['watched_projects']; print(f'count={len(paths)}'); print('\n'.join(paths))"
```

Expected:
- "JSON valid" prints
- `count=9`
- Last entry in the printed list is `/Users/marklehn/Developer/GitHub/lessons-forge/knowledge/decisions`
- Second-to-last entry is the bellows decisions path

If JSON validation fails, stop and report — restore from `git checkout bellows/config.json` if needed.

### Pre-check: lessons-forge/knowledge/decisions/ must exist

This directory was created in B.1 step 1 (`mkdir -p lessons-forge/knowledge/decisions && touch lessons-forge/knowledge/decisions/.gitkeep`). Confirm it still exists:

```bash
ls -la /Users/marklehn/Developer/GitHub/lessons-forge/knowledge/decisions/
```

Expected: directory exists, contains at minimum `.gitkeep`. If absent, stop and report — Bellows will fail to watch a non-existent path.

### Deposits
- `bellows/config.json` (modified)
- `bellows/knowledge/development/phase-b-2-step-5-2026-05-18.md` (dev log capturing the edit and JSON validation result)

---

## STEP 6 — Restart Bellows daemon

**Agent:** Developer

The currently-running daemon (PID 16238 at plan-write time) was loaded before the config change. Per the Restart Discipline section of PLANNER_TEMPLATE Bellows Execution Model, Bellows does not hot-reload configuration. The new watched path requires a restart.

### Action

```bash
# Capture pre-restart PID
PRE_PID=$(pgrep -f "bellows.py" | head -1)
echo "Pre-restart PID: $PRE_PID"

# Stop the daemon
pkill -f "bellows.py"
sleep 2

# Confirm stopped
pgrep -fl bellows.py || echo "Daemon stopped"

# Restart per usual startup pattern
cd /Users/marklehn/Developer/GitHub/bellows
nohup python3 bellows.py > logs/terminal/bellows-$(date +%Y-%m-%d).log 2>&1 &
sleep 3

# Capture post-restart PID and tail startup log
POST_PID=$(pgrep -f "bellows.py" | head -1)
echo "Post-restart PID: $POST_PID"
echo "---"
tail -30 logs/terminal/bellows-$(date +%Y-%m-%d).log
```

### Verification

- `$POST_PID` is non-empty AND different from `$PRE_PID`
- Startup log tail shows the daemon initialized successfully
- Startup log mentions 9 watched projects (or, if the daemon logs each watch path on startup, all 9 paths appear including `lessons-forge`)

If the post-restart PID is empty (daemon failed to start), stop and report. The pre-restart binary state is fine — config was the only change — so a startup failure indicates a malformed config or a separate issue. Recovery: `git checkout bellows/config.json` and restart.

### Deposits
- `bellows/logs/terminal/bellows-2026-05-18.log` (new daemon log; not committed — gitignored)
- `bellows/knowledge/development/phase-b-2-step-6-2026-05-18.md` (dev log capturing pre/post PIDs and startup log tail)

---

## STEP 7 — Commit + push (two-commit pattern)

**Agent:** Developer

Two commits, two repos. Bellows commit goes first (because the governance-root pointer bump comes after).

### Sub-step 7A — Commit and push bellows

```bash
cd /Users/marklehn/Developer/GitHub/bellows
git status --porcelain
```

Expected files in `git status`:
- `M config.json` — the new watch path
- `?? knowledge/development/phase-b-2-step-5-2026-05-18.md` — step 5 dev log
- `?? knowledge/development/phase-b-2-step-6-2026-05-18.md` — step 6 dev log

If any unexpected modifications appear (other source files, etc.), stop and report.

```bash
git add config.json knowledge/development/phase-b-2-step-5-2026-05-18.md knowledge/development/phase-b-2-step-6-2026-05-18.md
git commit -m "config: add lessons-forge decisions watch (Phase B.2)"
git push origin main
```

### Sub-step 7B — Commit and push governance root

```bash
cd /Users/marklehn/Developer/GitHub
git status --porcelain
```

Expected files (composition will reflect work from Steps 1–4 and the bellows submodule pointer bump from 7A):
- `M  .gitmodules` (step 4)
- `M  ARCHITECTURE.md` (step 3)
- `M  bellows` (submodule pointer bump from 7A)
- `M  governance/adr/ADR-002-lessons-forge-design.md` (step 1)
- `M  governance/adr/ADR-003-orchestrator-plan-pattern.md` (step 2)
- `A  lessons-forge` (step 4, new gitlink)
- `??  knowledge/development/phase-b-2-step-1-2026-05-18.md`
- `??  knowledge/development/phase-b-2-step-2-2026-05-18.md`
- `??  knowledge/development/phase-b-2-step-3-2026-05-18.md`
- `??  knowledge/development/phase-b-2-step-4-2026-05-18.md`

If any unexpected modifications appear (e.g., `M  anvil` indicating a stray submodule pointer change), stop and report.

```bash
git add .gitmodules ARCHITECTURE.md bellows governance/adr/ADR-002-lessons-forge-design.md governance/adr/ADR-003-orchestrator-plan-pattern.md lessons-forge knowledge/development/phase-b-2-step-1-2026-05-18.md knowledge/development/phase-b-2-step-2-2026-05-18.md knowledge/development/phase-b-2-step-3-2026-05-18.md knowledge/development/phase-b-2-step-4-2026-05-18.md
git commit -m "governance: register lessons-forge submodule + update ADR-002/003 + ARCHITECTURE (Phase B.2)"
git push origin main
```

### Verification

```bash
cd /Users/marklehn/Developer/GitHub
git submodule status
git status --porcelain
```

Expected:
- `git submodule status` shows three entries: anvil, bellows, lessons-forge — all with clean prefix (space)
- `git status --porcelain` shows nothing OR shows only `?? forge.db` / equivalent gitignored noise that's unrelated to this plan

### Deposits
- bellows: `config.json` change, two dev logs, pushed
- governance root: `.gitmodules`, three doc edits, new gitlink, bellows pointer bump, four dev logs, pushed
- `bellows/knowledge/development/phase-b-2-step-7-2026-05-18.md` (dev log capturing both pushes; this is a Step 7 artifact, deposit it after both pushes complete and document any deviation from the expected file lists)

---

## STEP 8 — Canary verification

**Agent:** QA

Deposit a no-op canary plan to `lessons-forge/knowledge/decisions/` and verify Bellows dispatches it end-to-end. Per the 2026-05-15 LESSONS entry on captured-cwd flag pattern, the canary's Output Receipt must report two binary flags as decisive verification.

### Canary plan content

Author the following plan file content. Deposit using the atomic staging pattern: write to `_staging_diagnostic-bellows-watch-canary-lessons-forge-2026-05-18.md` at the governance root, then `Filesystem:move_file` to `lessons-forge/knowledge/decisions/diagnostic-bellows-watch-canary-lessons-forge-2026-05-18.md`.

```markdown
# diagnostic — Bellows watch canary for lessons-forge (Phase B.2 verification)

**Plan ID:** diagnostic-bellows-watch-canary-lessons-forge-2026-05-18
**Date:** 2026-05-18
**Project:** lessons-forge
**Working directory:** `/Users/marklehn/Developer/GitHub/lessons-forge/`
**Priority:** 1
**Depends on:** none
**auto_close:** false

## Context

Phase B.2 added `lessons-forge/knowledge/decisions/` to the bellows watched_projects list and restarted the daemon. This canary verifies end-to-end dispatch on the new watch.

## STEP 1 — Echo + capture cwd + count watched projects

**Agent:** Developer

Single step. Three trivial mechanical actions, all reported in the Output Receipt's Flags for CEO field.

### Action

```bash
echo "Canary hello from lessons-forge submodule"
python3 -c "import os; print(f'cwd={os.getcwd()}')"
python3 -c "import json; cfg=json.load(open('/Users/marklehn/Developer/GitHub/bellows/config.json')); print(f'watched_count={len(cfg[\"watched_projects\"])}'); print(f'lessons_forge_watched={any(\"lessons-forge\" in p for p in cfg[\"watched_projects\"])}')"
```

### Deposits
- `knowledge/research/canary-lessons-forge-bellows-watch-2026-05-18.md` (canary findings: cwd, watched_count, lessons_forge_watched flag)

### Output Receipt requirements

Flags for CEO field MUST report verbatim:
- `cwd=<full path>` (literal, not paraphrased)
- `watched_count=<integer>`
- `lessons_forge_watched=<True|False>`
```

### Canary verification

After depositing the canary:

1. **Wait up to 60 seconds for Bellows to claim.** Bellows rescans every 30 seconds; allow up to two cycles.

   ```bash
   sleep 30
   ls /Users/marklehn/Developer/GitHub/lessons-forge/knowledge/decisions/
   ```

   Expected: filename now prefixed with `in-progress-`. If still `diagnostic-*` after 60 seconds, stop and report — Bellows is not seeing the new watched path.

2. **Wait for completion.** A trivial canary should finish within 2–3 minutes. Poll:

   ```bash
   ls /Users/marklehn/Developer/GitHub/lessons-forge/knowledge/decisions/
   ls /Users/marklehn/Developer/GitHub/lessons-forge/knowledge/decisions/Done/ 2>/dev/null
   ls /Users/marklehn/Developer/GitHub/bellows/verdicts/pending/ | grep canary-lessons-forge
   ```

   Expected progression: `in-progress-diagnostic-*` → `verdict-pending-diagnostic-*` with a verdict request in `bellows/verdicts/pending/`.

3. **Read the canary's findings deposit** at `lessons-forge/knowledge/research/canary-lessons-forge-bellows-watch-2026-05-18.md` and confirm the three flags:
   - `cwd` is under `/Users/marklehn/Developer/GitHub/lessons-forge/...` (worktree or in-place — either is acceptable; the flag's value confirms execution succeeded in the new submodule arrangement)
   - `watched_count=9`
   - `lessons_forge_watched=True`

   If any of the three flags are missing or wrong-valued, stop and report. Do NOT deposit a continue verdict.

4. **Planner authorizes continue verdict.** This step ends when QA confirms findings are correct AND the verdict request file exists in `bellows/verdicts/pending/`. Planner (CEO conversation) will perform Rule 22 verification on the canary findings deposit and author the continue verdict to `bellows/verdicts/resolved/`. Bellows will then move the canary plan to `Done/`.

### Deposits
- `lessons-forge/knowledge/decisions/diagnostic-bellows-watch-canary-lessons-forge-2026-05-18.md` (the canary plan itself, deposited via atomic staging pattern; Bellows will move through lifecycle states)
- `bellows/knowledge/qa/phase-b-2-step-8-canary-verification-2026-05-18.md` (QA report capturing: timestamp of deposit, time-to-claim, time-to-completion, canary findings flag values, Rule 20 self-check banner)

### Rule 20 self-check

```python
import os, glob

evidence_dir = '/Users/marklehn/Developer/GitHub/bellows/knowledge/qa/'
required = ['phase-b-2-step-8-canary-verification-2026-05-18.md']

all_ok = True
for f in required:
    path = os.path.join(evidence_dir, f)
    if not os.path.exists(path):
        print(f'MISSING: {path}')
        all_ok = False
    elif os.path.getsize(path) < 200:
        print(f'TOO SMALL: {path} ({os.path.getsize(path)} bytes)')
        all_ok = False
    else:
        print(f'OK: {path} ({os.path.getsize(path)} bytes)')

print()
print('PASSED — SELF-CHECK PASSED — all evidence files present, sufficient length.' if all_ok else 'FAILED — SELF-CHECK FAILED.')
```

Render the banner as a fenced block standalone in the QA report (no `$ python3 ...` prefix wrapping), per the 2026-05-17 LESSONS entry on Rule 20 gate false positives.

---

## Recovery notes

All steps are additive. Recovery from any step before the canary:

- Steps 1–3 (doc edits): `git checkout -- <file>` to revert.
- Step 4 (submodule add): `git rm --cached lessons-forge && git checkout -- .gitmodules` to revert. Working tree untouched.
- Step 5 (config edit): `cd bellows && git checkout config.json` to revert.
- Step 6 (daemon restart): kill the new process; relaunch from the same `bellows.py` (no config change to roll back beyond Step 5).
- Step 7 (commits): if push fails, the local commits remain; no remote state corrupted.

Step 8 canary failure is informational — it means the watch wiring is wrong, not that prior steps must be rolled back. Diagnose by inspecting the bellows startup log for the lessons-forge watch path.

---

## Output Receipt template (canary, Step 8)

When QA writes the Step 8 receipt, the Flags for CEO field must contain literal verbatim:
- `time_to_claim=<seconds>` (between deposit and `in-progress-` rename)
- `time_to_completion=<seconds>` (between deposit and `verdict-pending-` rename)
- `cwd=<literal value from canary findings>`
- `watched_count=<literal value from canary findings>`
- `lessons_forge_watched=<literal value from canary findings>`
