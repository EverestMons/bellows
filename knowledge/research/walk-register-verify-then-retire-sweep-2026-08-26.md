# Walk register — `verify-then-retire-sweep-2026-08-26` (bellows)

**schema_version:** `0.3`

**Plan:** `bellows/knowledge/decisions/drafts/diagnostic-verify-then-retire-sweep.md`
**Tier:** T1 (Small — read-only single-deposit diagnostic). **Panel: none (E-family; 515-528/531 precedent).**
**Opened:** 2026-08-26

---

## Walk 0 — context pin (REAL, measured 2026-08-26)

1. **The batch-4 work order, CEO-approved (baton 19cb574):** sweep item (1) — one verification pass per row whose enforcement already exists, then `class: stale` pointer retirements; PST §6 row already retired in batch 3.
2. **Every surface READ FROM CODE this authoring:** cycle_check yield-rising at :394 and the substrate asserts at :262/:377-383/:482; fold_check + propagation_check present in scripts/ (propagation has NO test file — positive control mandated); plan_lint (e) at :260-269 — MEASURED live: H3 `### Step` + qa_steps → FAIL (e)+(c) exit 1, H3 without qa_steps → exit 0 (the residual the R-5 verdict must carry); wrap_check arms [1]..[4] incl. 562's class gate; gates.py:582 rule-20 + plan_lint (c) :286-309.
3. **Honest-verdict design:** per-row COVERED/PARTIAL with residue + route; two rows PREDICTED partial by the Planner's own scout (R-3 landed-nothing case; R-5 qa_steps-less arm) — the diagnostic confirms or refutes, never rounds up.
4. **Retirement discipline:** Planner's own act at close (agents sandbox-denied on ~/.claude); pointers carry `class: stale` (the 562 gate binds these writes); R-5's row retires with the batch-item-3 cluster, not before, if PARTIAL confirms.
5. **id prediction:** 568.

⚠️ Walk 0 carries no fold rows. Walks 1–2 appended AFTER the draft exists, from real passes.

---

## Walk 1 — five-lens sequential walk (post-draft, real)

| id | walk | lens | sub_question | origin | finding | pre_fold_text | resolution |
|---|---|---|---|---|---|---|---|
| w1-1 | 1 | Weak spots | can the agent reconstruct the R-5 fixtures exactly? | pre-existing | the `#`-comment-prefix fixture encoding destroys the H1 title (prefix collides with the heading marker) — an agent stripping prefixes builds a DIFFERENT fixture and the measurement diverges; the companion worry (the body fixture's `**qa_steps:** 2` line poisoning the plan's own header) was REFUTED by code: `gates._parse_plan_header` terminates the header block at the first non-bold non-blank line | `# fixture A (qa_steps declared)` (commented paste) | folded: fixtures given as a construction SPEC (title text, header line, two H3 sections; B byte-identical minus the qa_steps field) |
| w1-2 | 1 | Vulnerabilities | can the agent read `~/.claude` at all? | pre-existing | R-4 required an absolute read of the memory file, but daemon agents are sandboxed away from `~/.claude` (the same constraint that forces Planner-side retirement) — the mapping table would fail on a permission error | `absolute-path read of /Users/marklehn/.claude/...` | folded: the ritual's step list INLINED into R-4 (Planner-transcribed); the path dropped from the manifest reads |
| w1-3 | 1 | Vulnerabilities | is the R-7 positive control earnable? | pre-existing | the planted disagreement ("three" vs "4") was the Planner's GUESS at the detector's representation — if the detector matches digits/specific shapes only, the control fails and the row is wrongly marked instrument-unproven | `state a count as "three" in one place and "4" in another` | folded: agent reads the detectors FIRST and derives the plant from the tool's own patterns (probe-must-match-representation, mechanurgy stated in-plan) |
| — | 1 | Destruction | — | — | DRY — read-only by construction; fixtures + baselines confined to /tmp; pytest suites named are tmp_path-isolated | — | no fold |
| — | 1 | Integration-record | — | — | DRY — license table covers all eight memories incl. the deferred R-5 row; forks named; retirement discipline stated with the 562 gate | — | no fold |
| — | 1 | ACID | — | — | DRY — one pathspec-limited commit; counts carry supersede clauses | — | no fold |

**Walk 1 total: 3 findings (instruction-class 3 / record 0), all folded; fold_check CLEAN post-fold (5 signals held); each fold's own text grep-verified 1/1/1 and the dropped read verified 0.**

---

## Walk 2 — five-lens sequential walk (real)

| id | walk | lens | sub_question | origin | finding | pre_fold_text | resolution |
|---|---|---|---|---|---|---|---|
| w2-1 | 2 | Weak spots | is the fixture-B spec byte-unambiguous? | fold-introduced (w1-1's spec) | the spec said omit the qa_steps field "and its trailing pipe" — the ` \| ` separator PRECEDES the field (it is last on the line); an agent following the wrong-direction instruction leaves a dangling separator and fixture B diverges | `(and its trailing pipe)` | folded: separator direction corrected; B's header end-state stated (`ends at **Project:** bellows`) |
| w2-2 | 2 | Vulnerabilities | did w1-2's class get swept across every site? | pre-existing (missed by w1's fold — the sweep-the-class duty) | R-2 still instructed the agent to "cite" the MECHANIZED header inside two `~/.claude` memory files — the identical sandbox-denial class folded at R-4, standing at a SECOND site | `Note both memory files already carry a "MECHANIZED by DC v2.13" header — cite it.` | folded: Planner-attested fact, agent forbidden from attempting the read, citation re-aimed at the DC changelog 2.13 line (in the agent's reach) |
| — | 2 | Destruction | — | — | DRY — /tmp confinement re-verified incl. R-3's baseline dotfile landing beside the /tmp copy | — | no fold |
| — | 2 | Integration-record | — | — | DRY — license-table coverage instruction names all eight memories; manifest finalization is the close act | — | no fold |
| — | 2 | ACID | — | — | DRY — toplevel-first pathspec-limited commit | — | no fold |

**Walk 2 total: 2 findings (instruction-class 2 / record 0), both folded; fold_check CLEAN (5 signals held); folds grep-verified 1/1, superseded text verified 0. Bar NOT met — a further confirming walk required.**
