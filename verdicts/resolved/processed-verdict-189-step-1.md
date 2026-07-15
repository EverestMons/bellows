verdict: continue
Step 1 verified — Bellows gates all PASS + Planner check (b) confirmed by direct read of the committed diff:
- _tabbed_import.html: 3-tab bar (Copilot Extraction / Found Information / Other); panel-found + panel-other render {{ found_info_content|safe }} / {{ other_content|safe }} slots (diag-188 Option 2); activateTab() rewritten for extract/found/other with NO residual paste/pdf branches; Inline-text + PDF-Upload tabs fully removed.
- _section_linked_docs.html: per-document "Open ↗" control added (target=_blank rel=noopener).
Scope correct (3 files: two templates + DEV log). Proceed to Step 2 (wire all 6 section templates into the slots + add _section_linked_docs include to FAK/Areas), then Step 3 QA.
Non-blocking note for later: the new "Open ↗" links to the document detail page, not a direct file download — acceptable base for Amendment A section A3; a direct file-download link is the eventual target and belongs with the parse-pdf relocation plan.
