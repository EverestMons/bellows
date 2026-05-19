# Output Receipt: COMPANY.md Three-List Reconciliation

**Plan:** governance-dispatch-infrastructure-2026-05-20
**Step:** 5 (DOC)
**Date:** 2026-05-20

---

## Output Receipt
**Agent:** Bellows Documentation Agent (governance-scope COMPANY.md edit)
**Step:** 5
**Status:** Complete

### What Was Done
Edited COMPANY.md to reconcile the project registry into three explicit lists (Active Projects, Bellows-watched, Shop infrastructure), added a "Shop-level vs Project-level" labeling section, added three missing project rows (bellows, lessons-forge, governance) to the Active Projects table, and bumped version from 2.4 to 2.6 / date to 2026-05-20.

### Final Active Projects Table (11 rows)

| Project | Description | Status |
|---|---|---|
| `invoice-pulse` | Carrier invoice processing and validation automation | Active |
| `BrewBuddy` | Coffee brewing tools and pourover timer | Active |
| `ai-career-digest` | AI career platform: daily digest, industry trends, job application engine, resume optimizer | Active |
| `study` | CS coursework support and study tools | Active |
| `SimpleScreen` | iOS home screen shortcut launcher with configurable widgets | Active |
| `freight-kb` | Freight AP support knowledge base with consensus engine | Active |
| `forge` | Prompt Forge — ingests operational artifacts across all projects, extracts prompt patterns, scores maturity, outputs governance updates | Active |
| `anvil` | Structural codebase intelligence — analyzes code structure, testing, volatility, patterns across projects | Active |
| `bellows` | Autonomous execution engine — dispatches plans via `claude -p`, validates through mechanical gates, notifies on escalation or completion | Active |
| `lessons-forge` | Lessons extraction pipeline — mines operational artifacts for reusable lessons and feeds them into LESSONS.md | Active |
| `governance` | Shop-meta as a workpiece — governance-root file edits dispatched and verified through the same plan lifecycle as project work | Active |

### Bellows-watched List (10 projects)
- invoice-pulse
- BrewBuddy
- study
- ai-career-digest
- freight-kb
- forge
- anvil
- bellows
- lessons-forge
- governance

### Shop Infrastructure List (4 projects)
- bellows
- forge
- lessons-forge
- governance

### Mechanical Verification Results

| Check | Result |
|---|---|
| Three lists present in COMPANY.md | PASS |
| Shop-level vs Project-level section present | PASS |
| Bellows-watched list == bellows/config.json:watched_projects | PASS (set-equal, 10 projects) |
| Active Projects is strict superset of Bellows-watched | PASS (11 ⊇ 10; SimpleScreen is Active-only) |
| Shop infrastructure == {bellows, forge, lessons-forge, governance} | PASS |
| Version bumped to 2.6, Last Updated 2026-05-20 | PASS |

### Bellows-watched Matches Config Exactly
**Verified programmatically:** loaded `bellows/config.json`, extracted project names from watched_projects paths, parsed COMPANY.md Bellows-watched bullet list, performed set-equality comparison. Result: **EQUAL**.

### Files Deposited
- `bellows/knowledge/research/company-three-list-reconciliation-2026-05-20.md` — this file

### Files Created or Modified (Code)
- `COMPANY.md` (governance root) — added 3 rows to Active Projects table, added Bellows-watched subsection, added Shop infrastructure subsection, added Shop-level vs Project-level subsection, bumped version 2.4→2.6

### Commit
**SHA:** 4b9b197
**Message:** `docs(governance): reconcile project registry into three lists + add shop/project labeling section`
**Repository:** `/Users/marklehn/Developer/GitHub/` (parent monorepo, main branch)

### Decisions Made
- Added descriptions for the three new Active Projects rows (bellows, lessons-forge, governance) using language consistent with existing row style — concise, functional, no marketing language
- Placed SimpleScreen in Active Projects only (not Bellows-watched) since it does not appear in bellows/config.json:watched_projects — used it as the example of a project in only one list in the labeling section
- Used plain project names (not backtick-wrapped) in Bellows-watched and Shop infrastructure bullet lists, matching the plan's "just names" instruction

### Flags for CEO
- None

### Flags for Next Step
- COMPANY.md is edited and committed. Step 6 (QA close) should verify the three-list consistency as part of Verification 4.
