verdict: continue

Planner verification (Rule 22(b)) — plan 502, Step 1 of 2 (DEV: the annotation write). All eleven gates PASS. ⚠️ **But the gate result is NOT what certifies this step, and the reason is worth stating: `files_changed` lists only two paths and `LESSONS.md` is not among them.** That is not a defect in the run — `files_changed` is built relative to cwd (`/Users/marklehn/Developer/GitHub/governance`), and the register lives one level above it, so the plan's PRINCIPAL EDIT is structurally invisible to every gate. This plan's own walk 1 recorded that blind spot; the verdict therefore rests on direct measurement, not on the green gates.

Verified independently of the agent's receipt:

1. THE ANNOTATION LANDED, EXACTLY. `[status: ]` markers on headings = 313, matching `B` precisely: 239 `learned` (= `L`) and 74 `pending` (= `B` − `L`). Dated headings still 327 — unchanged, so this was an EDIT and not an append.

2. BODY INVARIANCE HOLDS, MEASURED WITH THE CORRECTED PROBE. Non-heading changed lines inside the capture commit: **0**. Added `^+## 20` = 313 and deleted `^-## 20` = 313, so D4q resolves to 0. `git diff --numstat` on the register reads `313 313`. The panel's finding that the original regex form was blind to lines beginning with `-` was the reason this could be trusted at all.

3. THE TWO-COMMIT SHAPE IS CORRECT AND THE CIRCULARITY IS RESOLVED. Capture commit `b5d20fc` changes EXACTLY TWO files — the register and the builder. The handoff file sits alone in a second commit `a592944` and carries `CAPTURE_COMMIT: b5d20fc…` plus `D11_BEFORE: 63 passed, 0 failed`. A file recording a commit's own SHA cannot live inside it; the split is what makes the Step-2 binding possible.

4. THE QUARANTINE HELD. All 14 `unknown` rows are still present in their bare form — the agent applied nothing it was not authorised to apply.

5. KEY TRANSPARENCY ON THE REAL COMMITTED BYTES: **299/299, zero failures**, with the 14 unmatched rows correctly skipped (`B` − `C`). All 313 annotated headings are present in the file, none missing. This is the property the whole arc turns on, measured against what was actually written rather than against constructed strings.

6. THE CORPUS WAS NEVER TOUCHED. 370 entries, 1593344 bytes — identical to the values pinned at authoring.

7. THE DATE-LITERAL GUARD EARNED ITS PLACE. This step ran on 2026-08-23 against filenames dated 2026-08-22, and the agent wrote them exactly as declared. That guard was added at the deposit boundary, hours before dispatch, as the eighth dropped item from the clone origin.

Step 1 is correct and complete. Proceed to Step 2 (QA), which re-derives all of the above independently, runs the `lessons-forge` suite for the regression delta against `D11_BEFORE`, and proves the queryability the arc exists for.
