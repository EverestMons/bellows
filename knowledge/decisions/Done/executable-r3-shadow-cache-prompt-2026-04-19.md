# Bellows — R3 Variant (c): Shadow Cache Read-Only Prompt
**Date:** 2026-04-19 | **Tier:** Medium | **Test Scope:** full-suite | **Execution:** Step 1 (SA) → Step 2 (DEV) → Step 3 (QA)

**Purpose:** Close BACKLOG #6/#7 (plan file truncation by agents) by switching Bellows's bootstrap prompt from the mutable `{plan_path}` / `{inprogress_path}` to the read-only shadow cache path (`.bellows-cache/{name}.pristine`). The shadow cache is already populated at claim time (`bellows.py:224-225`); this plan wires it into prompt construction so the agent never learns the mutable plan path and cannot truncate it.

**Context:** Plan-mutation-source diagnostic (2026-04-19) confirmed H2 — the `claude -p` agent is the sole source of plan file truncation. R3 surface diagnostic (2026-04-19) mapped four prompt-construction sites in `bellows.py` (lines 241, 243, 245, 301) and confirmed three distinct bootstrap variants (diagnostic / resume / fresh) plus one mid-loop continuation. The SA recommended variant (c) (shadow cache read-only) as the smallest diff with mutation risk eliminated. CEO selected variant (c).

**Constraints (CEO-locked):**
- Do NOT break agent-side move-to-Done for non-auto-close plans. Bellows owns move-to-Done for auto-close and verdict-continue paths per existing code. Agent-side move-to-Done in plan templates is a separate concern — this plan does NOT modify PLANNER_TEMPLATE.md. If the SA discovers that variant (c) structurally breaks agent move-to-Done in practice, the SA blueprint must propose a scoped runner-side fallback (e.g., a second housekeeping-only path variable) rather than updating plan templates.
- Do NOT touch the Planner consultation prompt in `planner.py` — it is a separate code path that does not expose plan-mutation risk.
- Hot-reload caveat: Bellows does not hot-reload code. The close of this plan will run under pre-fix Bellows. QA must stay code-level (grep, unit tests) — no live integration smoke test inside the plan. Post-plan validation is a separate dependent plan deposited after CEO restarts Bellows.
- **Expected scope_check trip at close (top Open BACKLOG item):** Step 3's housekeeping modifies `bellows/knowledge/BACKLOG.md` and `bellows/PROJECT_STATUS.md`, which were also modified by yesterday's commits. Per today's BACKLOG #1 (scope_check false-positive over too-wide git range), scope_check is expected to flag these files as out-of-scope even though they are legitimate plan deliverables. This is cosmetic — the housekeeping should complete, the plan should land in Done/, and the CEO will need to manually clear the verdict request file in `bellows/verdicts/pending/` after close. QA does NOT fight scope_check — it completes its work and notes the expected trip in the final CEO flag.

## How to Run This Plan

Paste the bootstrap prompt into Claude Code. The agent reads the full plan file and executes Step 1 ONLY. After completing Step 1, the agent STOPS and waits for CEO confirmation ("ok") before proceeding to Step 2. This continues step by step until QA in Step 3, which performs deliverable verification, the Rule 20 self-check, housekeeping, and move-to-Done.

**Bootstrap:**
```
Read the plan at bellows/knowledge/decisions/executable-r3-shadow-cache-prompt-2026-04-19.md. Execute Step 1 ONLY. After completing Step 1, STOP and wait for my confirmation. Do NOT proceed to Step 2 or Step 3. Do NOT move the plan to Done.
```

---
---

## STEP 1 — Bellows Systems Analyst

---

> You are the Bellows Systems Analyst. Read your specialist file and the domain glossary first. Then read the surface diagnostic at `bellows/knowledge/research/r3-inline-step-text-surface-2026-04-19.md` — it is the primary input for this blueprint and should be cited directly, not re-investigated. Also read `bellows/bellows.py` lines 210-315 (claim + shadow write + prompt construction + continuation loop) and `bellows/runner.py` in full. Do NOT modify any code. Produce a blueprint only.
>
> Your task is to produce an SA blueprint for the R3 variant (c) implementation: switch the four prompt-construction sites in `bellows.py` (lines 241, 243, 245, 301) from `{plan_path}` / `{inprogress_path}` to the shadow cache path (`.bellows-cache/{plan_filename}.pristine`). The blueprint must specify every code change as exact diff-level instructions that the DEV agent can execute without design decisions.
>
> **B1 — Shadow path helper.** Specify whether a new helper function is needed (e.g., `_shadow_path(plan_filename) -> str`), or whether inline computation is acceptable. If helper, specify exact signature, return format (absolute path? project-relative? cwd-relative?), where it lives (`bellows.py` top-level or inside `run_plan`?), and exactly how the existing `bellows.py:224-225` shadow write references its own path so the new helper stays consistent with that write. Quote the existing shadow write code verbatim and name the helper's expected output path for a plan named `executable-foo-2026-04-19.md` so DEV has zero ambiguity.
>
> **B2 — Path resolution from agent cwd.** The runner invokes `claude -p` with `cwd=project_path` (runner.py:53). Specify the exact string that should appear in the prompt so the agent's `Read` tool resolves correctly. Options: (i) project-relative (`.bellows-cache/{name}.pristine`), (ii) absolute, (iii) cwd-relative via some other anchor. Recommend one and justify against the existing read patterns in deposited plan findings (which paths did past successful agents use — absolute or relative?). Verify the recommendation is consistent with how `bellows.py:224-225` writes the shadow file — if the write uses an absolute path, the prompt must match or there's a cwd mismatch risk.
>
> **B3 — Prompt template changes.** For each of the four prompt sites, quote the current f-string verbatim and specify the exact replacement f-string. The four sites are `bellows.py:241` (diagnostic), `bellows.py:243` (resume), `bellows.py:245` (fresh Step 1), `bellows.py:301` (continuation). All four switch from the mutable path to the shadow path. Enumerate these in a table: | Line | Current f-string (verbatim) | Replacement f-string | Context |.
>
> **B4 — Agent move-to-Done interaction.** The diagnostic noted that plan templates contain agent-side `shutil.move` instructions for move-to-Done. Under variant (c), the agent sees the move instruction but only knows the shadow path (`.bellows-cache/*.pristine`), not the `in-progress-*` filesystem path it would need to move. Investigate: in current Bellows, which code path handles move-to-Done for (a) auto-close plans, (b) verdict-continue-to-Done plans, (c) non-auto-close plans where the agent's step text contains `shutil.move(in-progress, Done)`? Read `bellows.py:366-400` and `bellows.py:_consume_verdicts` (lines ~660-690). Produce a table: | Plan type | Who moves to Done today? | After variant (c), who moves to Done? | Gap? |. If a gap exists (agent move-to-Done was structurally relied on and variant (c) breaks it), propose a scoped runner-side fallback: e.g., pass an `inprogress_path` variable to a separate "housekeeping instruction" section of the prompt, reserved for post-work move commands only, and structured so the agent can't use it for reads (no "read at {inprogress_path}" language). Do NOT propose plan-template edits — that is out of scope per CEO-locked constraints.
>
> **B5 — Test coverage plan.** Specify what tests DEV must add to prove variant (c) works. At minimum: (i) unit test that the four prompt-construction sites produce f-strings containing the shadow path and NOT the `in-progress-` path, (ii) unit test that the shadow path string resolves to an actual file post-claim (exercise the claim → shadow-write → prompt-construct sequence against a fixture plan), (iii) if B4 introduces a housekeeping fallback, a unit test confirming that the fallback path appears only in the housekeeping section and not in the read instruction. Quote the existing test file structure (which test files in `bellows/tests/` cover bellows.py prompt construction today?) so DEV extends the right file.
>
> **B6 — Regression risk enumeration.** List every existing Bellows behavior that could break under variant (c), with explicit mitigation per item. Must cover at minimum: (i) `--resume` continuation on Step 2+ (does the resumed session still work when Step 1's prompt referenced the shadow path? — per diagnostic Q4 the session is preserved, so this should be safe, but SA must verify), (ii) verdict-continue resume (creates a new session per diagnostic Q4 — does the new session's prompt still reach the shadow file correctly?), (iii) agents that produce Output Receipts referencing the plan file path (grep deposited QA reports for 5 recent plans and confirm no receipts cite `in-progress-*` or plan-file paths in their "Files Created or Modified" section — if they do, variant (c) may affect receipt content).
>
> **Output format:** deposit at `bellows/knowledge/architecture/r3-shadow-cache-blueprint-2026-04-19.md`. Write content to a Python variable first, then `with open("bellows/knowledge/architecture/r3-shadow-cache-blueprint-2026-04-19.md", "w") as f: f.write(content)`. Do NOT use heredoc. Do NOT use `python3 -c` with embedded quotes. Do NOT modify any Bellows source code. Include an Output Receipt per standard format.
>
> Standard prompt feedback protocol → `bellows/knowledge/research/agent-prompt-feedback.md`.
>
> **Deposits:**
> - `bellows/knowledge/architecture/r3-shadow-cache-blueprint-2026-04-19.md`
> - `bellows/knowledge/research/agent-prompt-feedback.md` (append)
>
> **STOP. Do NOT proceed to Step 2. Do NOT move the plan to Done. Wait for CEO confirmation before continuing.**

---
---

## STEP 2 — Bellows Developer

---

> Before starting, read `bellows/knowledge/architecture/r3-shadow-cache-blueprint-2026-04-19.md` and check the Output Receipt status field. If status is not Complete, stop and report the issue to the CEO before proceeding.
>
> You are the Bellows Developer. Read your specialist file and the domain glossary first. Then read the SA blueprint at `bellows/knowledge/architecture/r3-shadow-cache-blueprint-2026-04-19.md` in full — the blueprint is the checklist. Your task is to implement every code change specified in the blueprint's B1-B5 sections.
>
> Do NOT re-derive design decisions from the diagnostic — the SA has resolved them. Execute the blueprint as specified. If the blueprint is missing a detail you need (e.g., exact variable name, exact import), flag it as a blocker in your Output Receipt and stop rather than improvising.
>
> **Implementation scope (per blueprint):** (a) shadow path helper per B1 if specified, (b) f-string updates at `bellows.py:241, 243, 245, 301` per B3, (c) any housekeeping fallback per B4 if the blueprint determined a gap exists, (d) unit tests per B5. Do NOT modify `planner.py` (Planner consultation is out of scope). Do NOT modify any PLANNER_TEMPLATE or plan-template governance files.
>
> **Implementation discipline:** one commit per blueprint section (B1 helper, B3 prompt updates, B4 housekeeping fallback if any, B5 tests). Use `git --no-pager` on any log/diff/show commands. Run `python3 -m pytest bellows/tests/` after each commit and report pass/fail counts. **Before making any commits, record the starting SHA:** run `cd bellows && git --no-pager rev-parse HEAD` and paste the result into the dev log under a "Starting SHA" field — this is QA's baseline for Check 5.
>
> **Output:** deposit a dev log at `bellows/knowledge/development/r3-shadow-cache-prompt-2026-04-19.md` following the standard Output Receipt format. The Output Receipt "Files Created or Modified (Code)" section must list every file touched with a one-line description of the change — this is the input to Step 3's Rule 17 deliverable verification. Write content with `with open(...)` pattern, no heredocs.
>
> Standard prompt feedback protocol → `bellows/knowledge/research/agent-prompt-feedback.md`.
>
> **Deposits:**
> - `bellows/knowledge/development/r3-shadow-cache-prompt-2026-04-19.md`
> - `bellows/knowledge/research/agent-prompt-feedback.md` (append)
> - code changes: `bellows/bellows.py`, `bellows/tests/test_bellows.py` (or whichever test file the blueprint names), plus any housekeeping fallback location named in B4
>
> **STOP. Do NOT proceed to Step 3. Do NOT move the plan to Done. Wait for CEO confirmation before continuing.**

---
---

## STEP 3 — Bellows QA

---

> Before starting, read `bellows/knowledge/development/r3-shadow-cache-prompt-2026-04-19.md` and check the Output Receipt status field. If status is not Complete, stop and report the issue to the CEO before proceeding.
>
> You are the Bellows QA Analyst. Skip specialist file and glossary reads — this is a code-verification QA task. Your job is to verify every deliverable from Step 2's dev log exists and works, run the full test suite, and produce a QA report. Bellows will NOT be restarted during this plan per CEO-locked constraints — stay code-level only.
>
> **FIRST — Deliverable Verification (Rule 17).** Read the Step 2 dev log's "Files Created or Modified (Code)" list. For EVERY listed file: verify it exists on disk and contains the described change. For `bellows/bellows.py`: grep for the shadow-path f-string replacements at each of lines 241/243/245/301 (the exact line numbers may have shifted by a few — grep for the f-string content). For any new helper function: grep for the function definition. For new tests: grep for the test function names in the test file. For commits: `git --no-pager log --oneline -10` to confirm commits exist. Produce a verification table: | Deliverable | Expected | Status (✅/❌) | Evidence (file path) |. If ANY item is ❌, attempt to fix before proceeding. If unfixable, stop and report to CEO — do NOT proceed with the rest of QA.
>
> **Check 1 — Shadow path references in prompts.** Grep `bellows/bellows.py` for `{plan_path}` and `{inprogress_path}` inside f-strings that are part of prompt construction (the four sites the blueprint named). After variant (c), these should be replaced with the shadow path. Confirm zero occurrences of the mutable path in the prompt f-strings. Pipe output to `bellows/knowledge/qa/evidence/executable-r3-shadow-cache-prompt-2026-04-19/grep_prompt_sites.txt`.
>
> **Check 2 — Shadow cache write still intact.** Grep `bellows/bellows.py` around line 224-225 for the shadow write call. Confirm the shadow write code was NOT touched by this plan — the write side stays unchanged; only the read-side prompt construction changes. Deposit output at `bellows/knowledge/qa/evidence/executable-r3-shadow-cache-prompt-2026-04-19/grep_shadow_write.txt`.
>
> **Check 3 — Unit test assertions.** Read the new unit test(s) added in Step 2. Confirm at minimum: (i) at least one test asserts the prompt f-string contains the shadow path, (ii) at least one test asserts the prompt f-string does NOT contain the `in-progress-` prefix. If a housekeeping fallback was added per B4, confirm its dedicated test exists. Deposit the test file content excerpts (just the new/modified test functions) at `bellows/knowledge/qa/evidence/executable-r3-shadow-cache-prompt-2026-04-19/new_tests.txt`.
>
> **Check 4 — Full test suite.** Run `cd bellows && python3 -m pytest -v 2>&1 | tee knowledge/qa/evidence/executable-r3-shadow-cache-prompt-2026-04-19/pytest_full.txt`. Report pass/fail counts. Compare against the baseline from today's executable-verdict-lifecycle-coupling-2026-04-19 QA (baseline was approximately 125 tests with 11 pre-existing failures in test_runner.py — confirm this by reading that QA report's evidence if needed). The new tests from Step 2 should add to the passing count. Any net-new failures outside test_runner.py are regressions and must be flagged as Critical.
>
> **Check 5 — No unintended file modifications.** Read the Step 2 dev log's "Starting SHA" field. Run `cd bellows && git --no-pager diff --stat <starting-sha> HEAD`. Confirm the diff only touches the files the blueprint authorized (bellows.py, test file, and any B4 fallback location). Any unexpected files are Critical. Deposit the full diff-stat output at `bellows/knowledge/qa/evidence/executable-r3-shadow-cache-prompt-2026-04-19/git_diff_stat.txt`.
>
> **QA report:** deposit at `bellows/knowledge/qa/r3-shadow-cache-prompt-2026-04-19.md` with sections: Summary, Deliverable Verification table, Check 1-5 results (one row per check with Status and Evidence path cited), Self-Check output (see below), Final verdict. Write with `with open(...)`, no heredocs.
>
> **Rule 20 Self-Check.** Execute this Python block at the end of QA and include the literal stdout in the QA report. Because Rule 20's PATH-001 pattern has recurred in prior plans, use absolute path construction via `os.path` to avoid CWD mismatch. If the self-check prints FAILED, STOP — do NOT proceed with housekeeping. Report failure to CEO and wait.
>
> ```python
> # Rule 20 — Mandatory QA Self-Check
> import os, sys
> plan_slug = "executable-r3-shadow-cache-prompt-2026-04-19"
> # Build paths from a known-absolute anchor to avoid CWD issues (PATH-001)
> repo_root = "/Users/marklehn/Desktop/GitHub"
> qa_report_path = os.path.join(repo_root, "bellows/knowledge/qa/r3-shadow-cache-prompt-2026-04-19.md")
> evidence_dir = os.path.join(repo_root, f"bellows/knowledge/qa/evidence/{plan_slug}/")
> required_evidence_files = [
>     "grep_prompt_sites.txt",
>     "grep_shadow_write.txt",
>     "new_tests.txt",
>     "pytest_full.txt",
>     "git_diff_stat.txt",
> ]
> hedging_keywords = ["pending", "inferred", "extrapolated", "estimated", "approximate", "skipped", "assumed", "close enough", "should pass", "would pass", "not run"]
> POSITIVE_STATUS_TOKENS = ["✅", "OK", "PASS", "[x]", "done", "complete", "verified"]
>
> def is_positive_row(line):
>     if "|" not in line:
>         return False
>     cells = [c.strip() for c in line.split("|")]
>     for cell in cells:
>         for token in POSITIVE_STATUS_TOKENS:
>             if token == "✅":
>                 if "✅" in cell:
>                     return True
>             else:
>                 if cell.lower() == token.lower():
>                     return True
>     return False
>
> failures = []
> if not os.path.isdir(evidence_dir):
>     failures.append(f"CRITICAL: evidence folder missing: {evidence_dir}")
> else:
>     for fname in required_evidence_files:
>         fpath = os.path.join(evidence_dir, fname)
>         if not os.path.isfile(fpath):
>             failures.append(f"CRITICAL: evidence file missing: {fpath}")
>         elif os.path.getsize(fpath) == 0:
>             failures.append(f"CRITICAL: evidence file empty: {fpath}")
> if os.path.isfile(qa_report_path):
>     with open(qa_report_path, "r") as f:
>         report = f.read()
>     for line in report.splitlines():
>         if is_positive_row(line):
>             lower = line.lower()
>             for kw in hedging_keywords:
>                 if kw in lower:
>                     failures.append(f"CRITICAL: hedging keyword '{kw}' in positive-status row: {line.strip()[:120]}")
>                     break
> else:
>     failures.append(f"CRITICAL: QA report not found at {qa_report_path}")
> print("=" * 60)
> print("Rule 20 — QA Self-Check Results")
> print("=" * 60)
> if failures:
>     print(f"FAILED — SELF-CHECK FAILED — {len(failures)} issue(s):")
>     for f in failures:
>         print(f"  - {f}")
>     print("\nPlan CANNOT close. Fix issues and re-run QA.")
>     sys.exit(1)
> else:
>     print("PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.")
>     print(f"Evidence folder: {evidence_dir}")
>     print(f"Files verified: {len(required_evidence_files)}")
> ```
>
> **If Self-Check PASSES, proceed with housekeeping in this exact order (Rule 23):**
>
> **Step A — Feedback log append.** Append a dated entry to `bellows/knowledge/research/agent-prompt-feedback.md` with what worked well, what could improve, and any execution notes for this QA run.
>
> **Step B — PROJECT_STATUS update.** Add a completed-milestone entry to `bellows/PROJECT_STATUS.md` summarizing: variant (c) shipped, four prompt sites migrated to shadow cache, plan-mutation risk eliminated, test count before/after. Edit the file directly with `with open(...)` pattern (read → append milestone → write) or via the available edit tool. Do NOT name a specific MCP tool in these instructions per TOOL-001 — use a generic "edit" action.
>
> **Step C — BACKLOG update.** Edit `bellows/knowledge/BACKLOG.md` to move BACKLOG #6 (plan file truncation v2) and BACKLOG #7 (agent rewrites plan files) from Open to Closed with a citation to this plan's closing commit range and a REMINDER to restart Bellows.
>
> **Step D — Final commit.** `cd bellows && git --no-pager add knowledge/ PROJECT_STATUS.md && git commit -m "chore: status + backlog + feedback for r3 shadow cache prompt"`.
>
> **Step E — Move plan to Done.** `import shutil; shutil.move("/Users/marklehn/Desktop/GitHub/bellows/knowledge/decisions/in-progress-executable-r3-shadow-cache-prompt-2026-04-19.md", "/Users/marklehn/Desktop/GitHub/bellows/knowledge/decisions/Done/executable-r3-shadow-cache-prompt-2026-04-19.md")`.
>
> **Flag for CEO:** At the end of your QA report, include a prominent REMINDER line: "Bellows daemon restart required before variant (c) takes effect. Next plan will still run under pre-fix Bellows." This is the post-restart validation gap noted in today's LESSONS.md (2026-04-19).
>
> Standard prompt feedback protocol → `bellows/knowledge/research/agent-prompt-feedback.md`.
>
> **Deposits:**
> - `bellows/knowledge/qa/r3-shadow-cache-prompt-2026-04-19.md`
> - `bellows/knowledge/qa/evidence/executable-r3-shadow-cache-prompt-2026-04-19/grep_prompt_sites.txt`
> - `bellows/knowledge/qa/evidence/executable-r3-shadow-cache-prompt-2026-04-19/grep_shadow_write.txt`
> - `bellows/knowledge/qa/evidence/executable-r3-shadow-cache-prompt-2026-04-19/new_tests.txt`
> - `bellows/knowledge/qa/evidence/executable-r3-shadow-cache-prompt-2026-04-19/pytest_full.txt`
> - `bellows/knowledge/qa/evidence/executable-r3-shadow-cache-prompt-2026-04-19/git_diff_stat.txt`
> - `bellows/knowledge/research/agent-prompt-feedback.md` (append)
> - `bellows/PROJECT_STATUS.md` (milestone append)
> - `bellows/knowledge/BACKLOG.md` (move #6, #7 to Closed)
