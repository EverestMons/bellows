=== Verdicts README.md diff (HEAD~2 vs HEAD~1, commit a6432ab) ===
diff --git a/verdicts/README.md b/verdicts/README.md
index 15c60db..e581b9c 100644
--- a/verdicts/README.md
+++ b/verdicts/README.md
@@ -15,10 +15,10 @@ Bellows pauses plan execution under five conditions. The Planner writes a verdic
 ## Naming
 
 ```
-verdict-<plan-slug>-step-<N>.md
+verdict-<id>-step-<N>.md
 ```
 
-`<plan-slug>` = plan filename with leading prefix (`in-progress-`, `verdict-pending-`, `executable-`, `diagnostic-`) and `.md` stripped.
+`<id>` = the plan's integer id (id-native plans). Legacy plans: `<plan-slug>` = plan filename with leading prefix (`in-progress-`, `verdict-pending-`, `executable-`, `diagnostic-`) and `.md` stripped — dual-format tolerance accepts both. In all cases the mechanical rule: copy the verdict-request filename and replace `verdict-request-` with `verdict-`.
 
 Example: `diagnostic-foo-bar-2026-04-16.md` → `verdict-foo-bar-2026-04-16-step-1.md`

=== verdict: line-1 format regex check ===
Old: ['First line **must** match `^verdict:\\s*(continue|stop)$` (case-insensitive). All subsequent lines are freeform reason text.']
New: ['First line **must** match `^verdict:\\s*(continue|stop)$` (case-insensitive). All subsequent lines are freeform reason text.']
MATCH — verdict: line-1 format regex is byte-identical

=== Changed lines summary ===
-verdict-<plan-slug>-step-<N>.md
+verdict-<id>-step-<N>.md
-`<plan-slug>` = plan filename with leading prefix (`in-progress-`, `verdict-pending-`, `executable-`, `diagnostic-`) and `.md` stripped.
+`<id>` = the plan's integer id (id-native plans). Legacy plans: `<plan-slug>` = plan filename with leading prefix (`in-progress-`, `verdict-pending-`, `executable-`, `diagnostic-`) and `.md` stripped — dual-format tolerance accepts both. In all cases the mechanical rule: copy the verdict-request filename and replace `verdict-request-` with `verdict-`.

Only E5 filename-authority lines changed: PASS