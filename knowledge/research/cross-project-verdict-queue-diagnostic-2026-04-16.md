# Cross-Project Verdict Queue Architecture Diagnostic
**Date:** 2026-04-16 | **Status:** Complete

---

## Q1 — How does `config.json` define watched projects?

`config.json` defines `watched_projects` as an array of 8 absolute paths:

```
/Users/marklehn/Desktop/GitHub/invoice-pulse/knowledge/decisions
/Users/marklehn/Desktop/GitHub/BrewBuddy/knowledge/decisions
/Users/marklehn/Desktop/GitHub/study/knowledge/decisions
/Users/marklehn/Desktop/GitHub/ai-career-digest/knowledge/decisions
/Users/marklehn/Desktop/GitHub/freight-kb/knowledge/decisions
/Users/marklehn/Desktop/GitHub/forge/knowledge/decisions
/Users/marklehn/Desktop/GitHub/anvil/knowledge/decisions
/Users/marklehn/Desktop/GitHub/bellows/knowledge/decisions
```

8 watched directories. `anvil` was recently added and is sparse.

---

## Q2 — Trace plan_path through the verdict lifecycle

### (a) What does `run_plan` receive as `plan_path`?

The absolute path of the plan file as it exists on disk at dispatch time. On step 1, this is the original path, e.g.:

```
/Users/marklehn/Desktop/GitHub/forge/knowledge/decisions/executable-foo-2026-04-16.md
```

On resume (verdict `continue` on a non-final step), `_consume_verdicts` renames the `verdict-pending-` file to `in-progress-` and passes the in-progress path to `handle_new_plan`. So `run_plan` receives:

```
/Users/marklehn/Desktop/GitHub/forge/knowledge/decisions/in-progress-executable-foo-2026-04-16.md
```

### (b) What does `post_verdict_request` store in the `**Plan:**` field?

`verdict.post_verdict_request(plan_path, ...)` is passed the current `plan_path` value directly (bellows.py:215, 273). On step 1 this is the original path; on resume steps this is the `in-progress-` path. The `**Plan:**` field records whichever form `plan_path` holds at the time of the call.

### (c) Do plans from different projects produce the same slug?

**Yes — the slug is project-blind.** `_slug_from_path` (verdict.py:13–23) strips these prefixes in order (no `break` — all are tried):

```
("in-progress-", "verdict-pending-", "executable-", "diagnostic-")
```

Then strips `.md`. So:

| File | Slug |
|------|------|
| `forge/…/executable-foo-2026-04-16.md` | `foo-2026-04-16` |
| `bellows/…/executable-foo-2026-04-16.md` | `foo-2026-04-16` |
| `forge/…/in-progress-executable-foo-2026-04-16.md` | `foo-2026-04-16` |

Both projects' `executable-foo-2026-04-16.md` produce **identical slug** `foo-2026-04-16`. There is no project discriminator in the slug.

---

## Q3 — How does `_consume_verdicts` find the matching plan?

### (a) Exact matching logic (bellows.py:498–500):

```python
for pname in os.listdir(decisions_path):
    if pname.startswith("verdict-pending-") and plan_slug in pname:
```

**Substring match** (`plan_slug in pname`). If `plan_slug` is `foo-2026-04-16`, this matches any file whose name contains that substring — including `verdict-pending-executable-foo-2026-04-16.md` and `verdict-pending-diagnostic-foo-2026-04-16.md` and even `verdict-pending-executable-foo-2026-04-16-extra.md`.

### (b) Can `_consume_verdicts` match the wrong plan?

**Yes.** The outer loop iterates ALL 8 watched projects. For a resolved verdict with slug `foo-2026-04-16`, every `verdict-pending-*foo-2026-04-16*` file in every watched directory is matched and processed. There is no `break` after a match — the loop continues. If two different projects each have a `verdict-pending-executable-foo-2026-04-16.md`, the verdict consumes **both**.

### (c) Is there project-scoping in the verdict filename or matching?

**None.** The resolved verdict filename is `verdict-{slug}-step-{N}.md` — just slug and step, no project name. The matching loop has no project-awareness. A verdict intended for forge's plan will activate any file in any watched directory whose name contains the slug.

---

## Q4 — What happens with concurrent plans from different projects?

### (a) Shared verdict queue?

**Yes.** All plans from all 8 watched projects share one queue: `bellows/verdicts/pending/` (verdict request files) and `bellows/verdicts/resolved/` (Planner verdicts). There is no per-project subdirectory or namespace.

### (b) Cross-project verdict theft?

**Possible if slugs collide.** Scenario: forge has `verdict-pending-executable-foo-2026-04-16.md` paused at step 1. Bellows happens to also have `verdict-pending-executable-foo-2026-04-16.md` paused at step 1. Planner writes `verdict-foo-2026-04-16-step-1.md: continue`. `_consume_verdicts` iterates all 8 watched dirs, matches **both** files, and renames both — one to `in-progress-`, one to `Done/`. One of them gets the wrong verdict applied.

### (c) Mutex or per-project isolation?

**None.** `_active_lock` in `Bellows` only counts concurrent `_run_tracked` threads — it provides no isolation for the verdict queue. `_consume_verdicts` is called from the rescan loop in the main thread and has no locking relative to active plan threads.

---

## Q5 — Real risk or theoretical?

### (a) Current name collisions?

No actual collisions found today. Inventorying the Done directories:

**Forge Done — plans without forge/bellows project qualifier in the slug:**
- `diagnostic-agent-sync-2026-03-21` → slug: `agent-sync-2026-03-21`
- `executable-agent-content-sync-2026-03-21` → slug: `agent-content-sync-2026-03-21`
- `diagnostic-chunk-taxonomy-2026-03-23` → slug: `chunk-taxonomy-2026-03-23`
- `executable-conflict-detection-overhaul-2026-03-22` → slug: `conflict-detection-overhaul-2026-03-22`
- `executable-claudemd-protocol-propagation-2026-03-31` → slug: `claudemd-protocol-propagation-2026-03-31`
- *(and ~8 more without project qualifiers)*

**Bellows Done — plans without forge/bellows project qualifier in the slug:**
- `diagnostic-agent-self-request-verdict-2026-04-16` → slug: `agent-self-request-verdict-2026-04-16`
- `diagnostic-is-runnable-plan-parallel-2026-04-14` → slug: `is-runnable-plan-parallel-2026-04-14`
- `executable-scaffold-2026-04-13` → slug: `scaffold-2026-04-13`
- `executable-orchestrator-2026-04-13` → slug: `orchestrator-2026-04-13`
- `executable-notifier-server-2026-04-13` → slug: `notifier-server-2026-04-13`
- *(and ~10 more without project qualifiers)*

No slug appears in both lists simultaneously. Zero collisions as of 2026-04-16.

### (b) How likely is a collision?

Low but non-zero. The naming convention has evolved:
- **Current generation** (Phase 6+): plans include project name → `executable-bellows-*`, `diagnostic-forge-*`. These are safe.
- **Earlier generation** (Phase 1–5, scaffold era): bellows plans like `executable-scaffold-2026-04-13.md`, `executable-orchestrator-2026-04-13.md` lack project qualifiers.
- **Cross-domain names** (`agent-*`, `is-runnable-*`, `chunk-taxonomy-*`) exist in both repositories' history without project qualifiers.
- **Anvil** was just added to `watched_projects` and has no plan history yet. If anvil plans don't adopt the project-qualifier convention, collision risk rises.

### (c) Latent bug or non-issue?

**Latent bug.** Three conditions push this beyond "documentation only":
1. The code has no `break` after finding a match — it will actively process all matches across all 8 directories. Two projects with identical slugs causes double-consumption in a single `_consume_verdicts` call.
2. Naming discipline has already slipped (forge and bellows have unqualified plan names in Done). Adding new projects (anvil) with unqualified names directly activates the risk.
3. The `**Plan:**` field in the verdict request file *already contains the full project path*, making a scoped fix straightforward — the information to prevent the bug exists and is not used.

---

## Q6 — Recommendation

### (a) Fix or document?

**Both, with fix prioritized.** The substring match without project scoping is a real defect that will silently double-consume plans if naming conventions drift. Documentation alone cannot prevent it since naming conventions have already drifted in early plans and new projects may not follow them.

### (b) Minimal fix

**Option B — scope `_consume_verdicts` by reading the pending request file.**

When `_consume_verdicts` finds a resolved verdict (slug + step), it reads the corresponding pending verdict-request file from `bellows/verdicts/pending/`. That file already contains `**Plan:** {plan_path}`. Extract the project directory from that path and only search that directory.

Change in `_consume_verdicts` (after matching `fname`, before the outer for-loop):

```python
# Read the pending request to scope the search to the correct project
pending_file = BELLOWS_ROOT / "verdicts" / "pending" / f"verdict-request-{plan_slug}-step-{step_number}.md"
scoped_decisions_path = None
if pending_file.exists():
    text = pending_file.read_text()
    for line in text.splitlines():
        if line.startswith("**Plan:**"):
            plan_path_from_request = line.split("**Plan:**", 1)[1].strip()
            p = pathlib.Path(plan_path_from_request)
            scoped_decisions_path = str(p.parent)
            break
```

Then scope the project search:

```python
search_dirs = ([scoped_decisions_path] if scoped_decisions_path
               else self.config.get("watched_projects", []))
for decisions_path in search_dirs:
    ...
```

This requires no protocol change (verdict filenames unchanged, Planner workflow unchanged). It uses data Bellows already writes. If the pending file has been deleted or is missing, it falls back to the current behavior (search all projects).

**Also add a `break` after processing a match** to prevent double-consumption:

```python
for pname in os.listdir(decisions_path):
    if pname.startswith("verdict-pending-") and plan_slug in pname:
        ...process...
        break  # only one match per verdict
```

### (c) Documentation

Whether or not the code fix is applied, add to CLAUDE.md:

> **Plan naming convention (required):** Plan filenames MUST include the project name as the first word after the type prefix, e.g. `executable-bellows-*`, `diagnostic-forge-*`, `executable-anvil-*`. Do not create plans like `executable-scaffold-2026-04-13.md` without a project qualifier. This convention prevents cross-project verdict queue slug collisions. Bellows's `_consume_verdicts` matches plans by substring — a verdict for slug `foo-2026-04-16` will match ANY watched project's `verdict-pending-*foo-2026-04-16*` file.

---

## Summary

| Question | Finding |
|----------|---------|
| Q1 | 8 watched projects; all under `{project}/knowledge/decisions` |
| Q2 | `plan_path` is absolute; `**Plan:**` field stores it; slug strips project-blind prefixes → collisions possible |
| Q3 | Substring match, no project scoping; first-match wins; no project field in verdict filename |
| Q4 | Shared queue; cross-project theft possible on slug collision; no mutex |
| Q5 | Zero actual collisions today; latent bug because (a) no `break` causes double-consumption, (b) naming drift already present, (c) new projects add risk |
| Q6 | Fix: scope `_consume_verdicts` by reading `**Plan:**` from pending file + add `break`; document naming convention in CLAUDE.md |
