---
type: diagnostic
project: bellows
created: 2026-05-12
auto_close: false
pause_for_verdict: after_step_1
---

# Diagnostic — Canary: Intermediate Decision Detector Live Validation

**Execution Map:** Step 1 (BELLOWS_SYSTEMS_ANALYST)

**Purpose:** Validate that the intermediate-decision detector shipped earlier today is producing the expected `## Intermediate Decisions Detected` section in verdict request files post-daemon-restart. The work is intentionally tiny and contains deliberate ambiguity to force the agent to narrate at least one phrase-matched decision. The validation property the Planner checks at Rule 22: does the verdict request file for this step contain a non-empty `## Intermediate Decisions Detected` section? If yes — detector works end-to-end against real `claude -p` output, mechanism validated. If no — either the agent's narration didn't match any phrase (false negative, needs investigation) or the detector code path didn't run (failure mode, needs investigation). Single-step, no commits, no QA.

---

## STEP 1 — BELLOWS_SYSTEMS_ANALYST

Read your specialist file first — short read, no need to load the glossary for this canary. **Task:** Write a single-paragraph markdown file at `bellows/knowledge/research/canary-detector-validation-2026-05-12.md` describing in your own words what the intermediate decision detector does and why it exists. Keep the paragraph short — 4 to 6 sentences. **Deliberate ambiguity in the task:** the file's exact framing is up to you. You decide whether to write it as a third-person factual description, a first-person engineering summary, or a brief explainer suitable for a future agent reading the file fresh. Pick whichever framing seems best. Do NOT ask for clarification — make the call yourself and proceed. After writing, do a quick self-check: re-read what you wrote and confirm it makes sense given the audience you targeted. If the framing doesn't fit on re-read, adjust it. **Do NOT:** commit, run tests, update PROJECT_STATUS, append to feedback.log, or run a Rule 20 self-check. This is a single-deposit canary — minimal ceremony. Just deposit the markdown file and produce your Output Receipt. Inside the Output Receipt, name which framing you chose and (briefly) why. The Planner will examine the verdict request file post-pause to verify the detector surfaced your narration.

**Deposits:**
- `bellows/knowledge/research/canary-detector-validation-2026-05-12.md`
