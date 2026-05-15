# bellows — Create Specialist Roster (DEV, QA, SA, Documentation Analyst)
**Date:** 2026-04-19 | **Tier:** Small | **Test Scope:** targeted | **Execution:** Step 1 (Documentation Agent) → Step 2 (Documentation Agent)

**Test Scope justification:** targeted — this plan creates four markdown specialist files under `bellows/agents/`. No production code is touched. No tests exercise these files. Step 2 runs a completeness-checklist verification against `SPECIALIST_TEMPLATE.md`, which is mechanical file-structure verification, not a test suite run.

## How to Run This Plan

Paste the bootstrap prompt into Claude Code. The agent reads the full plan file and executes Step 1 ONLY. After completing Step 1, the agent STOPS and waits for CEO confirmation ("ok") before proceeding to Step 2. This continues step by step until the plan is complete. The agent must never skip steps, auto-chain to the next step, or move the plan to Done without completing all steps including QA.

**Bootstrap:**
```
Read the plan at /Users/marklehn/Desktop/GitHub/bellows/knowledge/decisions/executable-create-bellows-specialist-roster-2026-04-19.md. Execute Step 1 ONLY. After completing Step 1, STOP and wait for my confirmation. Do NOT proceed to Step 2 or move the plan to Done.
```

---
---

## STEP 1 — Documentation Agent

---

> **FIRST — before doing anything else, claim this plan:** `import shutil; shutil.move("/Users/marklehn/Desktop/GitHub/bellows/knowledge/decisions/executable-create-bellows-specialist-roster-2026-04-19.md", "/Users/marklehn/Desktop/GitHub/bellows/knowledge/decisions/in-progress-executable-create-bellows-specialist-roster-2026-04-19.md")`.
>
> You are the Documentation Agent creating the initial specialist roster for the Bellows project. Skip specialist file and glossary reads — Bellows has no specialist files yet (that's what you're creating) and no domain glossary exists. This is a file-authoring task, not a code task. **Reads (mandatory):** (1) `/Users/marklehn/Desktop/GitHub/SPECIALIST_TEMPLATE.md` — the template structure and 11-section completeness checklist, (2) `/Users/marklehn/Desktop/GitHub/COMPANY.md` — the handbook that defines Eluvian's departments and role conventions, (3) `/Users/marklehn/Desktop/GitHub/bellows/CLAUDE.md` — Bellows's project description, (4) `/Users/marklehn/Desktop/GitHub/bellows/bellows.py`, `verdict.py`, `gates.py`, `parser.py`, `runner.py`, `planner.py` (read in full — they're small) to understand what Bellows actually does and what domain knowledge each specialist needs to hold, (5) `/Users/marklehn/Desktop/GitHub/bellows/knowledge/BACKLOG.md` to see current Bellows work areas. **Task:** Create four specialist files under `/Users/marklehn/Desktop/GitHub/bellows/agents/` (create the `agents/` directory first if it doesn't exist). The four files are: `BELLOWS_DEVELOPER.md`, `BELLOWS_QA.md`, `BELLOWS_SYSTEMS_ANALYST.md`, `BELLOWS_DOCUMENTATION_ANALYST.md`. Each file follows SPECIALIST_TEMPLATE.md's structure exactly — all 11 sections present and populated with real Bellows-specific content, NOT placeholder text. **Project-specific content that belongs in each file:** DEV — owns Python changes to bellows.py, verdict.py, gates.py, parser.py, runner.py, planner.py, server.py, notifier.py; critical guardrail "Bellows is Layer 1 infrastructure — never add domain judgment or planning logic" (pull from architecture research); knows the plan lifecycle: claim via `in-progress-*` rename, run step via `claude -p` subprocess, invoke gates.py, post verdict via verdict.py, consume via `_consume_verdicts`, move-to-Done. QA — owns Bellows test suite verification (tests/ directory); knows Rule 17 deliverable verification, Rule 20 self-check block, Rule 21 test scope declarations; must verify changes to verdict.py or gates.py have matching test coverage. SA — owns architecture decisions: pause-reason taxonomy, gate composition, verdict file schema (reference `knowledge/research/verdict-file-schema-2026-04-18.md`), deposit parser scope (reference recent Rule 26 work and BACKLOG #6's resolution), step state lifecycle (BACKLOG #5); consults Planner when changes affect Rule 22 or Rule 25. Documentation Analyst — owns CLAUDE.md, README-style files, BACKLOG.md hygiene, knowledge-base organization across `knowledge/architecture/`, `knowledge/research/`, `knowledge/qa/`, `knowledge/development/`; NOT the author of executable plans (that's the Planner) but keeps specialist files in sync with the codebase per PLANNER_TEMPLATE's Specialist Sync pattern. **Domain Focus sections** must be narrow and Bellows-specific (e.g., DEV's domain focus is "the agent-dispatch lifecycle: claim → execute → gate → verdict → consume → close"), NOT generic department descriptions. **Key Sources / References sections** must list the actual files in `/Users/marklehn/Desktop/GitHub/bellows/` the specialist references, not invoice-pulse-style references. **Project-Specific Context sections** must reflect Bellows's current state: Layer 1 infrastructure, 3 layers (dispatch/judgment/notification), 9 open backlog items, Rule 26 deposit-parser work just shipped, Rule 25 Planner-side polling just shipped. **Peer Consultation tables** must reference specialists within the Bellows roster (the other three specialists being created in this same plan), not invoice-pulse specialists. **Decision Authority tables** must have at least 2 Bellows-specific rows per file, e.g., DEV: "Adding a new gate to gates.py — Specialist" vs "Changing pause-reason taxonomy — Escalate to SA"; SA: "Adding a new pause_reason enum value — SA" vs "Removing a pause_reason — Escalate to CEO". **Project-Specific Guardrails sections** must reference the Layer 1 principle: "Bellows is infrastructure. Never add domain judgment, planning logic, or agent-style reasoning. Layer 1 dispatches and gates; Layer 3 (Planner) judges." **Completeness checklist** — all 11 sections present, filled with real content (not placeholders), handbook reference matches COMPANY.md current version (read the header of COMPANY.md to confirm the version), guardrails reference is `governance/GUARDRAILS.md`. **File writes** — use `Filesystem:write_file` for each of the four files (single-call atomic writes, one per file). If `Filesystem:write_file` is unavailable, fall back to the canonical Python pattern: `with open("/absolute/path/file.md", "w") as f: f.write(content)` where `content` is a triple-quoted string defined BEFORE the open call. Heredoc is BANNED. **Deposits:**
> - `/Users/marklehn/Desktop/GitHub/bellows/agents/BELLOWS_DEVELOPER.md`
> - `/Users/marklehn/Desktop/GitHub/bellows/agents/BELLOWS_QA.md`
> - `/Users/marklehn/Desktop/GitHub/bellows/agents/BELLOWS_SYSTEMS_ANALYST.md`
> - `/Users/marklehn/Desktop/GitHub/bellows/agents/BELLOWS_DOCUMENTATION_ANALYST.md`
> - `/Users/marklehn/Desktop/GitHub/bellows/knowledge/development/bellows-specialist-roster-creation-2026-04-19.md`
>
> **Commit:** Stage the four specialist files + the dev log. `cd /Users/marklehn/Desktop/GitHub/bellows && git add agents/ knowledge/development/bellows-specialist-roster-creation-2026-04-19.md && git commit -m "docs: create initial Bellows specialist roster (DEV, QA, SA, Doc Analyst)"`. Standard prompt feedback protocol → `/Users/marklehn/Desktop/GitHub/bellows/knowledge/research/agent-prompt-feedback.md`.
>
> **STOP. Do NOT proceed to Step 2. Do NOT move the plan to Done. Wait for CEO confirmation before continuing.**

---
---

## STEP 2 — Documentation Agent (self-verification)

---

> Before starting, read `/Users/marklehn/Desktop/GitHub/bellows/knowledge/development/bellows-specialist-roster-creation-2026-04-19.md` and check the Output Receipt status field. If status is not Complete, stop and report the issue to the CEO before proceeding. You are the Documentation Agent performing Rule 17 deliverable verification on the four specialist files created in Step 1. Skip specialist file and glossary reads — this is a structural verification task against `SPECIALIST_TEMPLATE.md`'s completeness checklist. **Reads:** `/Users/marklehn/Desktop/GitHub/SPECIALIST_TEMPLATE.md` (for the 11-section completeness checklist), and all four files you created in Step 1. **Task:** For each of the four specialist files, verify every one of the 11 checklist items from `SPECIALIST_TEMPLATE.md` → "Completeness Checklist" section. Produce a verification table with columns: `| File | Section # | Section Name | Present (✅/❌) | Content Filled (✅/❌) | Evidence |`. The Evidence column cites a short (<12 word) quote from the file proving the section is populated, OR points to the evidence file path for multi-line evidence. For each file, capture its full content into an evidence file at `/Users/marklehn/Desktop/GitHub/bellows/knowledge/qa/evidence/executable-create-bellows-specialist-roster-2026-04-19/<filename-without-md>.txt` (four evidence files, one per specialist, containing the literal file contents). Also verify: (a) the handbook reference line (`**Handbook Reference:** COMPANY.md v<N>`) matches the current COMPANY.md version — run `grep "^\*\*Version" /Users/marklehn/Desktop/GitHub/COMPANY.md` and compare against each specialist file's handbook reference line. (b) the guardrails reference line points to `governance/GUARDRAILS.md`. (c) every specialist file's Peer Consultation table references the other three Bellows specialists (not specialists from other projects). (d) the `/Users/marklehn/Desktop/GitHub/bellows/agents/` directory contains exactly four `.md` files with the expected names. If ANY item fails, attempt to fix by having Step 1 work re-done or by editing the file in place — do NOT move the plan to Done with ❌ items. Deposit the QA report to `/Users/marklehn/Desktop/GitHub/bellows/knowledge/qa/bellows-specialist-roster-verification-2026-04-19.md`. **Rule 20 mandatory self-check** — at the end of your QA report, execute this Python block and include the literal stdout in the report:
>
> ```python
> import os, sys
> plan_slug = "executable-create-bellows-specialist-roster-2026-04-19"
> qa_report_path = "/Users/marklehn/Desktop/GitHub/bellows/knowledge/qa/bellows-specialist-roster-verification-2026-04-19.md"
> evidence_dir = f"/Users/marklehn/Desktop/GitHub/bellows/knowledge/qa/evidence/{plan_slug}/"
> required_evidence_files = [
>     "BELLOWS_DEVELOPER.txt",
>     "BELLOWS_QA.txt",
>     "BELLOWS_SYSTEMS_ANALYST.txt",
>     "BELLOWS_DOCUMENTATION_ANALYST.txt",
> ]
> hedging_keywords = ["pending", "inferred", "extrapolated", "estimated", "approximate", "skipped", "assumed", "close enough", "should pass", "would pass", "not run"]
> POSITIVE_STATUS_TOKENS = ["✅", "OK", "PASS", "[x]", "done", "complete", "verified"]
> def is_positive_row(line):
>     if "|" not in line: return False
>     cells = [c.strip() for c in line.split("|")]
>     for cell in cells:
>         for token in POSITIVE_STATUS_TOKENS:
>             if token == "✅":
>                 if "✅" in cell: return True
>             else:
>                 if cell.lower() == token.lower(): return True
>     return False
> failures = []
> if not os.path.isdir(evidence_dir):
>     failures.append(f"CRITICAL: evidence folder missing: {evidence_dir}")
> else:
>     for fname in required_evidence_files:
>         fpath = os.path.join(evidence_dir, fname)
>         if not os.path.isfile(fpath): failures.append(f"CRITICAL: evidence file missing: {fpath}")
>         elif os.path.getsize(fpath) == 0: failures.append(f"CRITICAL: evidence file empty: {fpath}")
> if os.path.isfile(qa_report_path):
>     with open(qa_report_path, "r") as f: report = f.read()
>     for line in report.splitlines():
>         if is_positive_row(line):
>             lower = line.lower()
>             for kw in hedging_keywords:
>                 if kw in lower:
>                     failures.append(f"CRITICAL: hedging keyword '{kw}' in positive-status row: {line.strip()[:120]}")
>                     break
> else:
>     failures.append(f"CRITICAL: QA report not found at {qa_report_path}")
> print("=" * 60); print("Rule 20 — QA Self-Check Results"); print("=" * 60)
> if failures:
>     print(f"FAILED — SELF-CHECK FAILED — {len(failures)} issue(s):")
>     for f in failures: print(f"  - {f}")
>     print("\nPlan CANNOT close. Fix issues and re-run QA.")
>     sys.exit(1)
> else:
>     print("PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.")
>     print(f"Evidence folder: {evidence_dir}")
>     print(f"Files verified: {len(required_evidence_files)}")
> ```
>
> If the self-check prints FAILED, STOP — do NOT update PROJECT_STATUS.md, do NOT move the plan to Done. Report the failure to CEO and wait. If PASSED, proceed: **(Step A — feedback append)** append a dated entry to `/Users/marklehn/Desktop/GitHub/bellows/knowledge/research/agent-prompt-feedback.md` (create file if absent). **(Step B — PROJECT_STATUS update)** use `edit_block` to update `/Users/marklehn/Desktop/GitHub/bellows/PROJECT_STATUS.md` — locate the Completed Milestones section and add a dated entry: "2026-04-19 — Created initial Bellows specialist roster (DEV, QA, SA, Documentation Analyst) under `bellows/agents/`. Unblocks all downstream Bellows backlog work." **(Step C — final commit)** `cd /Users/marklehn/Desktop/GitHub/bellows && git add knowledge/qa/ knowledge/research/agent-prompt-feedback.md PROJECT_STATUS.md && git commit -m "docs: QA verification + status update for specialist roster creation"`. **(Step D — move plan to Done, ABSOLUTE LAST operation)** `import shutil; shutil.move("/Users/marklehn/Desktop/GitHub/bellows/knowledge/decisions/in-progress-executable-create-bellows-specialist-roster-2026-04-19.md", "/Users/marklehn/Desktop/GitHub/bellows/knowledge/decisions/Done/executable-create-bellows-specialist-roster-2026-04-19.md")`. Then `cd /Users/marklehn/Desktop/GitHub/bellows && git add knowledge/decisions/ && git commit -m "chore: move specialist-roster plan to Done"`. **Deposits:**
> - `/Users/marklehn/Desktop/GitHub/bellows/knowledge/qa/bellows-specialist-roster-verification-2026-04-19.md`
> - `/Users/marklehn/Desktop/GitHub/bellows/knowledge/qa/evidence/executable-create-bellows-specialist-roster-2026-04-19/BELLOWS_DEVELOPER.txt`
> - `/Users/marklehn/Desktop/GitHub/bellows/knowledge/qa/evidence/executable-create-bellows-specialist-roster-2026-04-19/BELLOWS_QA.txt`
> - `/Users/marklehn/Desktop/GitHub/bellows/knowledge/qa/evidence/executable-create-bellows-specialist-roster-2026-04-19/BELLOWS_SYSTEMS_ANALYST.txt`
> - `/Users/marklehn/Desktop/GitHub/bellows/knowledge/qa/evidence/executable-create-bellows-specialist-roster-2026-04-19/BELLOWS_DOCUMENTATION_ANALYST.txt`
