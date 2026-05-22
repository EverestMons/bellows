verdict: continue
Rule 22 substance verification passed. All 6 Verification Areas in the QA report PASSED. 38 STALE rows from the drift audit verified one-by-one with file location and result. Re-grep returned zero stale tokens across all three refreshed files. Test re-collect: 1920 tests (matches audit basis 1920, matches refreshed claims "~1920"). Pre-existing failure verification: 2 failed (the correct two — activity_import + fix_links), 1 passed (xml_billing — correctly excluded from failure list). Rule 20 banner correctly embedded in QA report with all 6 areas ✅ and "RULE 20 SELF-CHECK: PASSED". Commit aa1db20 shipped on local main.

The two Bellows gate failures are both known-class false positives:

(1) rule_22_verification flagged 47 QA-report-table rows as "missing status" — every flagged row has "| PASS |" as the final column (visible in the verdict request's own quoted text of each row). Gate parser is truncating row text before reaching the status column. Bellows-side parser bug, not a substance failure. To be captured in bellows/knowledge/BACKLOG.md.

(2) rule_20_self_check flagged "banner present but PASSED line missing in invoice-pulse/knowledge/research/agent-prompt-feedback.md" — the gate read the prompt-feedback file (not the QA report deposit) and matched a Rule-20-shaped pattern in the feedback entry without finding a PASSED line. The actual Rule 20 banner is in the QA report deposit (knowledge/qa/specialist-file-drift-refresh-qa-2026-05-22.md) and is correctly formed with "RULE 20 SELF-CHECK: PASSED". Gate fired on the wrong file. To be captured in bellows/knowledge/BACKLOG.md.

file_change_audit | PASS | 0 files modified is the same worktree-vs-main vantage false positive observed on prior plans.

Terminal step of a 2-step plan with auto_close: false. This continue verdict authorizes plan close per Rule 25 terminal-step path.
