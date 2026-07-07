verdict: continue

Survivor of the 137/138 duplicate-dispatch pair. DEV step completed clean in wt/138 (feat commit a8b0a2e + dev-log 51a666e, both tagged [138]). Proceed to Step 2 (QA). QA must scrutinize the qa_steps↔step-label WARN block for a dead branch: the last for-loop's if/else may print an identical message in both arms (observed in an uncommitted stray variant in main) — collapse it if so.
