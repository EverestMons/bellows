# Bellows — Coordinated daemon-side gate-FP fix: shared root-cause shape across three 2026-05-27 BACKLOG entries
**Date:** 2026-05-27 | **Tier:** Diagnostic | **Dispatch Mode:** bellows | **Test Scope:** targeted | **Execution:** Step 1 (SA) | **qa_steps:** | **pause_for_verdict:** after_step_1

## Context

Three Bellows BACKLOG entries filed 2026-05-27 (`ceo_flags`, `rule_22_verification` (c) row-status, `rule_22_verification` (d) hedging-detector) describe gate false positives whose mechanism shapes look symmetric: each gate parses field/cell/table content uniformly without scoping its inspection to the semantic region that actually carries the signal. The fix-shape menus in each BACKLOG entry independently propose null-token allowlists, section-scoping predicates, or cell-scope match — variations on the same theme.

The proposed coordinated daemon-side fix is a shared `_is_null_declaration()` / section-scoping helper that closes all three in one structurally symmetric change, rather than three independent surgical patches.

**Sibling-fix symmetry model.** The same gate's (c) sub-check shipped a section-scoping fix 2026-05-24 via `executable-gate-file-scoping-2026-05-24` (DEV commit `56f94f0`, Shape 6C: section-scoping + `_is_positive_status_row()` predicate). That fix scoped greenness checks to verification sections only. The three 2026-05-27 entries are surface symptoms of the same content-scoping gap on adjacent gate sub-checks. Extending the same scoping mechanism is the working hypothesis; this diagnostic determines whether that extension is well-formed across all three call sites or whether the call sites diverge enough that independent fixes are warranted.

**Why this diagnostic, why now.** Rule 10 mandates diagnostic-before-fix-plan. The abstraction-shape decision (shared helper vs. three independent predicates) requires all three call sites visible in one context — splitting investigation across three diagnostics forces the abstraction call to be made by the Planner with partial visibility into each site. Single combined diagnostic is the only shape that can evaluate the load-bearing question of this session.

**Three open BACKLOG entries this diagnostic targets:**
- `Added 2026-05-27: ceo_flags gate false positive on "None" / "No flags" / declarative-empty content` (fix shapes (a) null-token allowlist, (b) presence-of-issue heuristic, (c) require structured marker)
- `Added 2026-05-27: rule_22_verification (c) sub-check false positives on enumerative tables in QA reports` (fix shapes (a) section-scoping, (b) status-cell heuristic, (c) opt-out marker)
- `Added 2026-05-27: Hedging-detector false positives on domain terminology` (fix shapes (a) word-boundary + context, (b) per-project allowlist, (c) cell-scope match)

**What this diagnostic must determine:**
- Q1: For each of the three gate sub-checks, identify EXACTLY the function, the offending parsing logic, and the structural shape of the content being parsed (field text vs. table rows vs. row cells).
- Q2: Whether the three sites converge on a single abstraction (a shared "is this content a null declaration / is this region a verification region / is this cell the gate's target" predicate) or whether each requires its own scoping primitive.
- Q3: Whether the 2026-05-24 section-scoping helper and `_is_positive_status_row()` predicate are directly reusable for any or all of the three sites, or whether they are model-only (similar pattern, distinct primitives).
- Q4: For each fix-shape option listed in each BACKLOG entry, characterize what the option's implementation would actually touch at the call site (call-site predicate, helper function, schema field, etc.) and whether it interacts with the other two call sites.
- Q5: Recommendation — single coordinated fix with shared helper(s), three independent fixes, or some mixed shape (e.g., two share a helper, third is independent). The recommendation must name the abstraction shape concretely (function signature, what it returns, what it consumes) without writing implementation code.

## Reference prior art (read these to avoid re-deriving)

- `bellows/knowledge/BACKLOG.md` — the three 2026-05-27 entries (top of Open section). Each entry's "Fix shape options" subsection enumerates 2-3 proposals with effort estimates. Read carefully — the diagnostic's Q4 builds on these.
- `bellows/knowledge/decisions/Done/diagnostic-gate-file-scoping-2026-05-24.md` — joint diagnostic for the original Rule 22 (c) greenness-check and Rule 20 self-check file-scoping fixes. Establishes the section-scoping methodology used by the 2026-05-24 ship.
- `bellows/knowledge/decisions/Done/executable-gate-file-scoping-2026-05-24.md` — the executable that shipped Shape 6C section-scoping and the `_is_positive_status_row()` helper. Contains the concrete code shape the symmetry hypothesis builds on.
- `bellows/knowledge/qa/executable-gate-file-scoping-2026-05-24.md` — QA verification of the 2026-05-24 ship. Documents which test patterns exercise the section-scoping logic. Useful for Q3's "directly reusable" determination.

**Triggering artifacts (concrete failure cases — read these to ground each fix-shape proposal in actual content):**

- For `ceo_flags` FP: `bellows/verdicts/resolved/processed-verdict-planner-template-bellows-operational-workarounds-2026-05-27-step-2.md` — contains the textbook null declaration `"None. All SA-cited anchor lines matched verbatim. No blueprint-vs-file mismatches. No prose adjustments needed."` in the Flags for CEO field that tripped the gate.
- For `rule_22_verification` (c) row-status FP: `lessons-forge/knowledge/qa/plan-authoring-checklist-qa-2026-05-27.md` — the QA report that triggered 31 false-positive failures across 5 enumerative tables (heading-list, proposal-ID map, rule-numbering, archived-proposals, verbatim-match cross-reference). The corresponding verdict request: `bellows/verdicts/resolved/processed-verdict-planner-template-plan-authoring-checklist-2026-05-27-step-3.md`.
- For hedging-detector FP: `bellows/verdicts/resolved/processed-verdict-stuck-state-color-override-2026-05-22-step-2.md` (or its archived equivalent if not at the resolved path) — QA report verification rows tripped on the domain term `pending` (state literal, JSON field, function name). LESSONS.md governance-root entry 2026-05-27 captures the originating context.

Build on the BACKLOG entries' "Fix shape options" — do NOT re-derive the options. The diagnostic's job is to characterize the call sites and evaluate the options against concrete code, not to re-propose alternatives.

## Five questions to answer

For every claim, cite specific `gates.py` line + exact code snippet (no paraphrasing). The diagnostic is read-only — no code changes, no file writes outside the deliverable.

**Q1 (call-site characterization):** For each of the three FP-producing gate sub-checks, locate the function and the offending parsing logic in `gates.py`. Cite line ranges and snippet content.

- `_gate_ceo_flags` (or wherever the Flags-for-CEO field is evaluated): what content does it parse, and what predicate fires the gate failure? What constitutes "non-empty content" in the current implementation?
- `_gate_rule_22_verification` (c) sub-check, specifically the row-status / "row N missing status" branch (NOT the greenness branch — that one was scoped 2026-05-24): what table-discovery and row-iteration logic produces the "missing status" finding? How does it decide which tables in a deposit are inspected?
- `_gate_rule_22_verification` (d) sub-check, specifically the hedging-detector branch: what content is matched against the hedging vocabulary list? Cite the vocabulary and the match predicate. Is the match against the whole row, the Status cell, or some other slice?

For each, identify the structural shape of the content being parsed: free-text field, markdown table rows, individual cells within rows, or something else.

**Q2 (abstraction convergence):** Do the three sites share an abstraction shape, or do they require distinct primitives?

- Option A — single helper: a predicate like `_is_null_declaration(text: str) -> bool` works for all three (CEO Flags field treats null declarations as PASS; (c) treats all rows in non-verification tables as null-declaration-equivalent; (d) treats hedging vocabulary inside non-verification-cell context as null-declaration-equivalent).
- Option B — section-scoping primitive: a function like `_iter_verification_rows(deposit_text: str) -> Iterable[Row]` that yields only rows under verification headers. The 2026-05-24 helper for the greenness check used this shape — the row-status check could reuse it. The hedging detector could scope its match to rows yielded by this iterator. The CEO Flags field doesn't fit this primitive (it's not a row).
- Option C — three independent predicates: each site's content shape is distinct enough that sharing forces awkward parameterization.
- Option D — mixed shape: e.g., (c) row-status and (d) hedging share a section-scoping primitive (extension of 2026-05-24 helper); (a) CEO Flags is independent (uses null-token allowlist).

Cite the structural reasoning. Which option does the actual code support, given the structural shapes from Q1?

**Q3 (2026-05-24 reusability):** Trace the 2026-05-24 section-scoping helper and `_is_positive_status_row()` in current `gates.py`. Are they reusable for any of the three 2026-05-27 sites?

- Cite the helper signatures and current consumers.
- For each 2026-05-27 site, state explicitly: (i) "directly reusable — same signature, same consumer pattern," (ii) "reusable with extension — current helper covers part of the need, additional primitive required," or (iii) "model-only — similar pattern but distinct primitive, no code reuse."
- If the helper IS reusable, name the consumer signature change required (the call site moves from current ad-hoc logic to a call to the existing helper).

**Q4 (fix-shape characterization per BACKLOG entry):** For each of the nine fix-shape options across the three BACKLOG entries (3 options × 3 entries), characterize what shipping that option would actually touch:

- Specific function(s) edited (cite line ranges).
- New helper(s) introduced (signature only, not body).
- Schema/config changes (new fields in plan header, config.json, gate registration, etc.).
- Interactions with the OTHER two call sites — does shipping this option here close, partially close, or have no effect on the other two FP patterns?

Format as a 3×3 table with columns = entry, rows = option, cells = (touched function, new helper if any, cross-site interaction).

The point of Q4 is to expose which options compose naturally into a shared fix and which are structurally independent.

**Q5 (recommendation):** Based on Q2 (abstraction convergence) and Q4 (cross-site interaction matrix), recommend the fix shape:

- **5a.** Single coordinated fix with shared helper(s) — name the helper signatures, identify which 3 BACKLOG entries are closed by it, and state the LOC estimate (production + tests).
- **5b.** Three independent fixes — state which fix-shape option to pick for each entry (from Q4) and the per-entry LOC estimate.
- **5c.** Mixed shape — name the partition (which 2 share, which is independent), the shared helper signature, and the independent fix-shape option.

The recommendation must also address:
- Whether the recommendation preserves backward compatibility (existing tests, existing plans in-flight).
- Whether the recommendation requires daemon restart (the 2026-05-24 ship did).
- Which BACKLOG entry's existing fix-shape proposal (named in the entry) is closest to the recommendation, and where the recommendation diverges and why.

Do NOT draft pseudocode for the shared helper. The CEO will use this recommendation to authorize an executable plan that DEV-side validates the abstraction concretely. Q5's output is a shape decision, not implementation.

---

## STEP 1 — Joint call-site characterization and shared-abstraction evaluation

**Agent:** Bellows Systems Analyst
**Estimated tokens:** ~35k

> **FIRST — before doing anything else, claim this plan:** `mv /Users/marklehn/Developer/GitHub/bellows/knowledge/decisions/diagnostic-gate-fp-coordinated-shape-2026-05-27.md /Users/marklehn/Developer/GitHub/bellows/knowledge/decisions/in-progress-diagnostic-gate-fp-coordinated-shape-2026-05-27.md`. **THEN, immediately and BEFORE any other reads or work: post a short visible message to chat (1-2 sentences) confirming you have claimed the plan and stating your immediate next action.** This is a liveness anchor — prior SA blueprint attempts hung in silent reading phases past the 600s threshold. **AFTER posting confirmation:** read the specialist file, the four prior-art files, and the three triggering artifacts named below. **As you finish reading each file, post a 1-line acknowledgment** ("Read X.") to keep the inactivity timer warm. **As you START each section of the deliverable, post a 1-line marker** ("Drafting Section A.", "Drafting Section B.", etc.).

### Read order (post 1-line ack after each)

1. `bellows/agents/BELLOWS_SYSTEMS_ANALYST.md` — specialist context.
2. `bellows/knowledge/BACKLOG.md` — read the three 2026-05-27 entries in the Open section (top of file). Each entry's "Fix shape options" subsection is the canonical option list for Q4. Do NOT re-propose options.
3. `bellows/knowledge/decisions/Done/diagnostic-gate-file-scoping-2026-05-24.md` — sibling diagnostic's methodology.
4. `bellows/knowledge/decisions/Done/executable-gate-file-scoping-2026-05-24.md` — the implementation that shipped Shape 6C and `_is_positive_status_row()`. Focus on what changed in `gates.py` and what helpers exist post-ship.
5. `bellows/knowledge/qa/executable-gate-file-scoping-2026-05-24.md` — QA evidence on the 2026-05-24 ship's test coverage.
6. `bellows/gates.py` — full read with attention to: `_gate_ceo_flags` (or equivalent — find by searching for "Flags for CEO" or "ceo_flags"), `_gate_rule_22_verification` (especially the (c) row-status branch and (d) hedging-detector branch), and any helpers added by the 2026-05-24 ship (section-scoping iterator, `_is_positive_status_row`). Do NOT read `bellows.py` or any other source files unless Q1 traces a call chain that requires it — and if so, cite the trace.
7. Triggering artifacts (one each, for grounding fix-shape proposals in concrete content):
   - `bellows/verdicts/resolved/processed-verdict-planner-template-bellows-operational-workarounds-2026-05-27-step-2.md` — the CEO Flags FP case.
   - `lessons-forge/knowledge/qa/plan-authoring-checklist-qa-2026-05-27.md` — the 5-table QA report that produced 31 row-status FPs.
   - `bellows/verdicts/resolved/processed-verdict-planner-template-plan-authoring-checklist-2026-05-27-step-3.md` — the verdict request that captured the 31 FPs (gate evidence).
   - For the hedging-detector FP: locate the deferred-validation-status-card-2026-05-22 Step 4 verdict request (try `bellows/verdicts/resolved/processed-verdict-stuck-state-color-override-2026-05-22-step-2.md` first; if absent, search `bellows/verdicts/resolved/` for `defer*validation*2026-05-22*step-4` or `deferred*validation*status*card*2026-05-22*step-4`). If none found, cite that explicitly and proceed using the BACKLOG entry's description of the failure mode.

Do NOT read source files beyond what's listed above unless Q1 explicitly traces a call chain that requires it. If a trace requires reading another file, name the file and the line range and proceed.

### Deliverable structure

Deposit findings to `bellows/knowledge/research/gate-fp-coordinated-shape-2026-05-27.md`. Format below. For every code claim, cite line + snippet from `gates.py`. For every BACKLOG-option claim, cite the BACKLOG entry's wording.

**Section A — Q1: Three call-site mechanism characterizations**

For each of the three gate sub-checks (ceo_flags, rule_22 (c) row-status, rule_22 (d) hedging-detector):

- Function name and line range in `gates.py`.
- Exact parsing logic that produces the FP (cite snippet, ≤15 lines per site).
- Structural shape of content being inspected (field text / markdown table rows / individual cells / vocabulary substring match).
- Triggering content from the artifact (cite the specific token, row, or text fragment that tripped the gate).

**Section B — Q2: Abstraction convergence analysis**

Evaluate Options A (single helper) / B (section-scoping primitive) / C (three independent) / D (mixed). For each option:
- Whether the structural shapes from Section A support the option (yes/no/partially).
- The concrete reason — cite Section A.

End with a single-option pick, justified.

**Section C — Q3: 2026-05-24 helper reusability**

For each 2026-05-27 site, classify as (i) directly reusable, (ii) reusable with extension, or (iii) model-only. Cite the 2026-05-24 helper signature and the structural reasoning.

**Section D — Q4: Fix-shape interaction matrix (3×3 table)**

Rows: option (a), option (b), option (c) of each BACKLOG entry.
Columns: ceo_flags, rule_22 (c), rule_22 (d).
Cells: (touched function, new helper if any, cross-site interaction = "closes / partial / no effect").

Below the table, write 1-2 sentences identifying which row of the matrix shows the cleanest cross-site composition (the candidates for shared fix).

**Section E — Q5: Recommendation (5a / 5b / 5c)**

State the recommendation as one of 5a / 5b / 5c. Include:
- Helper signature(s) — function name, parameter types, return type. NO implementation body.
- BACKLOG entries closed by the recommendation (1, 2, or 3 of the three).
- LOC estimate — production lines + test lines, with confidence (low/medium/high).
- Backward-compatibility note: any existing test or in-flight plan that would change behavior.
- Daemon restart required (yes/no, and which symbol/function loading triggers the need).
- Which BACKLOG entry's named fix-shape option is closest to the recommendation; where it diverges and why.

**Flags for CEO:** any deviation from the BACKLOG entries' framing — specifically if the recommendation closes fewer than 3 entries, or if a fix-shape option from the BACKLOG entries proves structurally infeasible against the actual code.

### Constraints

- Read-only diagnostic. Do NOT edit `gates.py`, do NOT propose pseudocode, do NOT write tests.
- The deliverable is the recommendation shape, not the implementation.
- If a BACKLOG entry's fix-shape option proves infeasible against actual code (e.g., a referenced field doesn't exist, a referenced helper isn't reusable), state that explicitly in Section D — do not silently substitute.
- If the section-scoping helper from 2026-05-24 is named differently in current `gates.py` than the executable plan suggested, cite the actual current name and proceed.

### Deposits

- `bellows/knowledge/research/gate-fp-coordinated-shape-2026-05-27.md`
