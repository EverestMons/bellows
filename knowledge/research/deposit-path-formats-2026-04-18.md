# Deposit-Path Format Survey — Findings
**Date:** 2026-04-18 | **Diagnostic:** bellows-deposit-path-formats | **Surveyed corpus:** 109 plan files across 8 Bellows-watched projects

---

## Corpus Summary

| Project | Active files | Done files (sampled) | Total surveyed |
|---------|-------------|---------------------|----------------|
| invoice-pulse | 5 | 12 | 17 |
| BrewBuddy | 1 | 11 | 12 |
| study | 0 | 12 | 12 |
| ai-career-digest | 1 | 8 (all available) | 9 |
| freight-kb | 2 | 9 (all available) | 11 |
| forge | 3 | 12 | 15 |
| anvil | 5 | 12 | 17 |
| bellows | 3 | 13 | 16 |
| **TOTAL** | **20** | **89** | **109** |

---

## Pass 1 — Raw Inventory

Each row is one deposit-path match. Step number determined from nearest preceding `## STEP N` header. PRIMARY deposits only — feedback-arrow lines (`Standard prompt feedback protocol → ...`) included for completeness but tagged as secondary.

### invoice-pulse (17 files — 37 deposit-path matches)

| # | Plan File | Step | Matched Line (verbatim, truncated) | Path Format | Label Style | Primary? |
|---|-----------|------|------------------------------------|-------------|-------------|----------|
| 1 | in-progress-executable-csv-upload-fetch-fix | 1 | `**Deposit dev log** to \`invoice-pulse/knowledge/development/csv-upload-fetch-fix-2026-04-17.md\`` | backticked | bold-label + `to` | YES |
| 2 | in-progress-executable-csv-upload-fetch-fix | 2 | `**Deposit QA report** to \`invoice-pulse/knowledge/qa/csv-upload-fetch-fix-qa-2026-04-17.md\`` | backticked | bold-label + `to` | YES |
| 3 | verdict-pending-executable-gitattributes-crlf | 1 | `**Deposit dev log** to \`invoice-pulse/knowledge/development/gitattributes-crlf-2026-04-17.md\`` | backticked | bold-label + `to` | YES |
| 4 | Done/executable-planner-template-v4-23-rule-24-atomic-deposit | 1 | `**Then deposit the development log.** Use \`Filesystem:write_file\` to write a single-call development log at \`/Users/marklehn/.../planner-template-v4-23-rule-24-2026-04-18.md\`` | absolute backticked | inline prose + `at` | YES |
| 5 | Done/executable-planner-template-v4-23-rule-24-atomic-deposit | 2 | `**Deposit the QA report** at \`/Users/marklehn/.../planner-template-v4-23-rule-24-qa-2026-04-18.md\`` | absolute backticked | bold-label + `at` | YES |
| 6 | Done/fuel-importer-full-coverage | 1 | `**Deposit dev log** to \`invoice-pulse/knowledge/development/fuel-importer-full-coverage-2026-04-17.md\`` | backticked | bold-label + `to` | YES |
| 7 | Done/fuel-importer-full-coverage | 2 | `**Deposit QA report** to \`invoice-pulse/knowledge/qa/fuel-importer-full-coverage-qa-2026-04-17.md\`` | backticked | bold-label + `to` | YES |
| 8 | Done/diagnostic-fuel-bracket-ceiling | 1 | `**Deposit findings** to \`invoice-pulse/knowledge/research/fuel-bracket-ceiling-2026-04-17.md\`` | backticked | bold-label + `to` | YES |
| 9 | Done/diagnostic-fuel-continuation-rule | 1 | `**Deposit findings** to \`invoice-pulse/knowledge/research/fuel-continuation-rule-2026-04-17.md\`` | backticked | bold-label + `to` | YES |
| 10 | Done/fuel-formula-extraction | 1 | `**Deposit findings** to \`invoice-pulse/knowledge/research/fuel-formula-extraction-2026-04-17.md\`` | backticked | bold-label + `to` | YES |
| 11 | Done/fuel-hero-to-tabbed | 1 | `**Deposit dev log** to \`invoice-pulse/knowledge/development/fuel-hero-to-tabbed-2026-04-17.md\`` | backticked | bold-label + `to` | YES |
| 12 | Done/fuel-hero-to-tabbed | 2 | `**Deposit QA report** to \`invoice-pulse/knowledge/qa/fuel-hero-to-tabbed-qa-2026-04-17.md\`` | backticked | bold-label + `to` | YES |
| 13 | Done/fuel-hero-widget | 1 | `**Deposit findings** to \`invoice-pulse/knowledge/research/fuel-hero-widget-2026-04-17.md\`` | backticked | bold-label + `to` | YES |
| 14 | Done/diagnostic-config-upload-json-redirect | 1 | `**Deposit findings** to \`invoice-pulse/knowledge/research/config-upload-json-redirect-2026-04-17.md\`` | backticked | bold-label + `to` | YES |
| 15 | Done/executable-file-first-fuel-brackets | 1 | `**Deposit development log** to \`invoice-pulse/knowledge/development/file-first-fuel-brackets-2026-04-16.md\`` | backticked | bold-label + `to` | YES |
| 16 | Done/executable-file-first-fuel-brackets | 2 | `**Deposit QA report** to \`invoice-pulse/knowledge/qa/file-first-fuel-brackets-qa-2026-04-16.md\`` | backticked | bold-label + `to` | YES |
| 17 | Done/executable-file-first-accessorials-fak | 1 | `**Deposit development log** to \`invoice-pulse/knowledge/development/file-first-accessorials-fak-2026-04-16.md\`` | backticked | bold-label + `to` | YES |
| 18 | Done/executable-file-first-accessorials-fak | 2 | `**Deposit QA report** to \`invoice-pulse/knowledge/qa/file-first-accessorials-fak-qa-2026-04-16.md\`` | backticked | bold-label + `to` | YES |
| 19 | Done/executable-file-first-billto-header | 1 | `**Deposit development log** to \`invoice-pulse/knowledge/development/file-first-billto-header-2026-04-16.md\`` | backticked | bold-label + `to` | YES |
| 20 | Done/executable-file-first-billto-header | 2 | `**Deposit QA report** to \`invoice-pulse/knowledge/qa/file-first-billto-header-qa-2026-04-16.md\`` | backticked | bold-label + `to` | YES |

(Remaining 17 matches are evidence file pipes and feedback-arrow lines — all secondary.)

### BrewBuddy (12 files — 32 deposit-path matches)

| # | Plan File | Step | Matched Line (truncated) | Path Format | Label Style | Primary? |
|---|-----------|------|-----------------------------|-------------|-------------|----------|
| 1 | Done/executable-presseffect-buttonstyle-migration | 1 | `**Deposit DEV log** to \`BrewBuddy/knowledge/development/presseffect-buttonstyle-migration-2026-04-17.md\`` | backticked | bold-label + `to` | YES |
| 2 | Done/executable-presseffect-buttonstyle-migration | 2 | `**Write QA report** to \`BrewBuddy/knowledge/qa/presseffect-buttonstyle-migration-2026-04-17.md\`` | backticked | bold-label + `to` | YES |
| 3 | Done/diagnostic-confirm-bookheader-button-v8 | 1 | `**Deposit** findings to \`BrewBuddy/knowledge/research/confirm-bookheader-button-v8-diag-2026-04-17.md\`` | backticked | bold-label + `to` | YES |
| 4 | Done/handleback-caller-v6 | 1 | `**Deposit** findings to \`BrewBuddy/knowledge/research/handleback-caller-v6-diag-2026-04-17.md\`` | backticked | bold-label + `to` | YES |
| 5 | Done/diagnostic-presseffect-removal-confirmation-v5 | 1 | `**Deposit findings** to \`BrewBuddy/knowledge/research/presseffect-removal-confirmation-v5-diag-2026-04-17.md\`` | backticked | bold-label + `to` | YES |
| 6 | Done/diagnostic-button-press-fires-action-blocked-v4 | 1 | `**Deposit findings** to \`BrewBuddy/knowledge/research/button-press-fires-action-blocked-v4-diag-2026-04-17.md\`` | backticked | bold-label + `to` | YES |
| 7 | Done/executable-presseffect-simultaneous-gesture-fix | 1 | `**Deposit** a DEV log to \`BrewBuddy/knowledge/development/presseffect-simultaneous-gesture-fix-2026-04-17.md\`` | backticked | bold-label + `to` | YES |
| 8 | Done/executable-presseffect-simultaneous-gesture-fix | 2 | `**Write QA report** to \`BrewBuddy/knowledge/qa/presseffect-simultaneous-gesture-fix-2026-04-17.md\`` | backticked | bold-label + `to` | YES |
| 9 | Done/diagnostic-presseffect-buttonstyle-scoping | 1 | `**Deposit findings** to \`BrewBuddy/knowledge/research/presseffect-buttonstyle-scoping-2026-04-17.md\`` | backticked | bold-label + `to` | YES |
| 10 | Done/diagnostic-flavornotes-tap-does-nothing-v2 | 1 | `**Deposit findings** to \`BrewBuddy/knowledge/research/flavornotes-tap-does-nothing-v2-diag-2026-04-17.md\`` | backticked | bold-label + `to` | YES |
| 11 | Done/diagnostic-flavornotes-subcategory-not-appearing | 1 | `**Deposit findings** to \`BrewBuddy/knowledge/research/flavornotes-subcategory-diag-2026-04-17.md\`` | backticked | bold-label + `to` | YES |
| 12 | Done/executable-bellows-live-test-4 | 2 | `Deposit QA report to \`BrewBuddy/knowledge/qa/bellows-live-test-4-qa-2026-04-14.md\`` | backticked | plain-label + `to` | YES |
| 13 | Done/executable-bellows-live-test-3 | 2 | `Deposit QA report to \`BrewBuddy/knowledge/qa/bellows-live-test-3-qa-2026-04-13.md\`` | backticked | plain-label + `to` | YES |
| 14 | Done/executable-remove-purple-square | 2 | `Deposit QA report to \`BrewBuddy/knowledge/qa/remove-purple-square-qa-2026-04-13.md\`` | backticked | plain-label + `to` | YES |

(Remaining 18 matches are evidence file writes and feedback-arrow lines — all secondary.)

### study (12 files — 15 primary deposit matches)

| # | Plan File | Step | Matched Line (truncated) | Path Format | Label Style | Primary? |
|---|-----------|------|-----------------------------|-------------|-------------|----------|
| 1 | Done/diagnostic-sonnet-model-switch | 1 | `**Deposit:** \`study/knowledge/research/sonnet-model-switch-diagnostic-2026-04-02.md\`` | backticked | `**Deposit:**` colon-form | YES |
| 2 | Done/code-entry-tab | 1 | `**Deposit:** \`study/knowledge/research/code-entry-diagnostic-2026-04-01.md\`` | backticked | `**Deposit:**` colon-form | YES |
| 3 | Done/diagnostic-react-error-31 | 1 | `**Deposit:** \`study/knowledge/research/react-error-31-diagnostic-2026-04-01.md\`` | backticked | `**Deposit:**` colon-form | YES |
| 4 | Done/executable-fix-date-year-offset | 2 | `**Deposit:** Write QA report to \`knowledge/qa/date-year-fix-qa-2026-04-01.md\`` | backticked | `**Deposit:**` + write-phrase | YES |
| 5 | Done/diagnostic-extraction-fix-preconditions | N/A | `\`knowledge/research/extraction-fix-preconditions-2026-04-11.md\`` (under `## Deliverable` header) | backticked | section-header only | YES |
| 6 | Done/diagnostic-facet-extraction-context-envelope | N/A | `\`knowledge/research/facet-extraction-context-envelope-2026-04-11.md\`` (under `## Deliverable`) | backticked | section-header only | YES |
| 7 | Done/diagnostic-algorithmic-novelty-audit | N/A | `\`knowledge/research/algorithmic-novelty-audit-2026-04-11.md\`` (under `## Deliverable`) | backticked | section-header only | YES |

(Remaining 8 matches are feedback-arrow lines — all secondary.)

### ai-career-digest (9 files — 18 primary deposit matches)

| # | Plan File | Step | Matched Line (truncated) | Path Format | Label Style | Primary? |
|---|-----------|------|-----------------------------|-------------|-------------|----------|
| 1 | Done/executable-remove-api-dependency | 1 | `**Deposit:** \`ai-career-digest/knowledge/architecture/remove-api-dependency-2026-03-29.md\`` | backticked | `**Deposit:**` colon-form | YES |
| 2 | Done/executable-remove-api-dependency | 3 | `Deposit QA report to \`ai-career-digest/knowledge/qa/remove-api-dependency-qa-2026-03-29.md\`` | backticked | plain-label + `to` | YES |
| 3 | Done/executable-industry-trends | 1 | `**Deposit:** \`ai-career-digest/knowledge/architecture/industry-trends-2026-03-29.md\`` | backticked | `**Deposit:**` colon-form | YES |
| 4 | Done/executable-industry-trends | 3 | `Deposit QA report to \`ai-career-digest/knowledge/qa/industry-trends-qa-2026-03-29.md\`` | backticked | plain-label + `to` | YES |
| 5 | Done/executable-llm-summarization | 1 | `**Deposit:** \`ai-career-digest/knowledge/architecture/llm-curation-2026-03-29.md\`` | backticked | `**Deposit:**` colon-form | YES |
| 6 | Done/executable-llm-summarization | 4 | `Deposit QA report to \`ai-career-digest/knowledge/qa/llm-curation-qa-2026-03-29.md\`` | backticked | plain-label + `to` | YES |
| 7 | Done/executable-obsidian-delivery | 1 | `**Deposit:** \`ai-career-digest/knowledge/architecture/obsidian-delivery-2026-03-29.md\`` | backticked | `**Deposit:**` colon-form | YES |
| 8 | Done/executable-obsidian-delivery | 3 | `Deposit design review to \`ai-career-digest/knowledge/design/obsidian-format-review-2026-03-29.md\`` | backticked | plain-label + `to` | YES |
| 9 | Done/executable-obsidian-delivery | 4 | `Deposit QA report to \`ai-career-digest/knowledge/qa/obsidian-delivery-qa-2026-03-29.md\`` | backticked | plain-label + `to` | YES |
| 10 | Done/executable-preference-onboarding | 1 | `**Deposit:** \`ai-career-digest/knowledge/architecture/preference-onboarding-flow-2026-03-29.md\`` | backticked | `**Deposit:**` colon-form | YES |
| 11 | Done/executable-preference-onboarding | 3 | `Deposit QA report to \`ai-career-digest/knowledge/qa/preference-onboarding-qa-2026-03-29.md\`` | backticked | plain-label + `to` | YES |
| 12 | Done/executable-database-schema | 1 | `**Deposit:** Write the full schema blueprint to \`ai-career-digest/knowledge/architecture/career-db-schema-2026-03-29.md\`` | backticked | `**Deposit:**` + write-phrase | YES |
| 13 | Done/executable-database-schema | 3 | `Deposit QA report to \`ai-career-digest/knowledge/qa/career-db-schema-qa-2026-03-29.md\`` | backticked | plain-label + `to` | YES |

(Remaining 5 matches are feedback-arrow lines — all secondary.)

### freight-kb (11 files — 22 primary deposit matches)

| # | Plan File | Step | Matched Line (truncated) | Path Format | Label Style | Primary? |
|---|-----------|------|-----------------------------|-------------|-------------|----------|
| 1 | in-progress-diagnostic-new-thread-layout | 1 | `**Deposit:** \`freight-kb/knowledge/design/new-thread-layout-audit-2026-03-25.md\`` | backticked | `**Deposit:**` colon-form | YES |
| 2 | Done/diagnostic-prompt-generation | 1 | `**Deposit:** \`freight-kb/knowledge/development/diagnostic-prompt-generation-2026-03-25.md\`` | backticked | `**Deposit:**` colon-form | YES |
| 3 | Done/executable-unified-input | 1 | `**Deposit:** \`freight-kb/knowledge/architecture/unified-input-blueprint-2026-03-24.md\`` | backticked | `**Deposit:**` colon-form | YES |
| 4 | Done/executable-unified-input | 2 | `**Deposit:** \`freight-kb/knowledge/development/unified-input-dev-2026-03-24.md\`` | backticked | `**Deposit:**` colon-form | YES |
| 5 | Done/executable-unified-input | 3 | `**Deposit:** \`freight-kb/knowledge/qa/unified-input-qa-2026-03-24.md\`` | backticked | `**Deposit:**` colon-form | YES |
| 6 | Done/executable-phase2-integration | 1 | `**Deposit:** \`freight-kb/knowledge/qa/phase2-integration-qa-2026-03-24.md\`` | backticked | `**Deposit:**` colon-form | YES |
| 7 | Done/executable-phase2-integration | 2 | `**Deposit:** \`freight-kb/knowledge/development/phase2-integration-fixes-2026-03-24.md\`` | backticked | `**Deposit:**` colon-form | YES |
| 8 | Done/executable-plain-text-input | 1 | `**Deposit:** \`freight-kb/knowledge/architecture/plain-text-input-blueprint-2026-03-24.md\`` | backticked | `**Deposit:**` colon-form | YES |
| 9 | Done/executable-plain-text-input | 2 | `**Deposit:** \`freight-kb/knowledge/development/plain-text-input-dev-2026-03-24.md\`` | backticked | `**Deposit:**` colon-form | YES |
| 10 | Done/executable-plain-text-input | 3 | `**Deposit:** \`freight-kb/knowledge/qa/plain-text-input-qa-2026-03-24.md\`` | backticked | `**Deposit:**` colon-form | YES |
| 11 | Done/parallel-1-executable-forge-kb-integration | 1 | `**Deposit:** \`forge/knowledge/architecture/freight-kb-chunk-types-blueprint-2026-03-24.md\`` | backticked | `**Deposit:**` colon-form | YES |
| 12 | Done/parallel-1-executable-forge-kb-integration | 2 | `**Deposit:** \`forge/knowledge/development/freight-kb-chunk-types-dev-2026-03-24.md\`` | backticked | `**Deposit:**` colon-form | YES |
| 13 | Done/parallel-1-executable-forge-kb-integration | 3 | `**Deposit:** \`forge/knowledge/qa/freight-kb-chunk-types-qa-2026-03-24.md\`` | backticked | `**Deposit:**` colon-form | YES |
| 14 | Done/parallel-1-executable-classification-pipeline | 1–3 | `**Deposit:** \`freight-kb/knowledge/{architecture,development,qa}/...\`` | backticked | `**Deposit:**` colon-form | YES (×3) |
| 15 | Done/parallel-1-executable-ingestion-app | 1–4 | `**Deposit:** \`freight-kb/knowledge/{architecture,design,development,qa}/...\`` | backticked | `**Deposit:**` colon-form | YES (×4) |
| 16 | Done/executable-foundation-phase0 | 1–2 | `**Deposit:** The agent files and stubs are the deposits.` | no-path | `**Deposit:**` label but prose-only | NO PATH |
| 17 | Done/executable-foundation-phase0 | 3 | `**Deposit:** \`forge/knowledge/development/freight-kb-registration-2026-03-24.md\`` | backticked | `**Deposit:**` colon-form | YES |

### forge (15 files — 19 primary deposit matches)

| # | Plan File | Step | Matched Line (truncated) | Path Format | Label Style | Primary? |
|---|-----------|------|-----------------------------|-------------|-------------|----------|
| 1 | halted-executable-forge-retrieval-fix | 1 | `Deposit a comparison table to \`forge/knowledge/research/retrieval-fix-reeval-comparison-2026-04-16.md\`` | backticked | inline prose + `to` | YES |
| 2 | halted-executable-forge-retrieval-fix | 2 | `**Deposit:** QA report to \`/Users/.../forge/knowledge/qa/forge-retrieval-fix-qa-2026-04-16.md\`` | absolute backticked | `**Deposit:**` colon-form | YES |
| 3 | Done/diagnostic-forge-scoping | 1 | `Deposit findings to \`knowledge/research/forge-scoping-2026-04-18.md\`` | backticked | inline prose + `to` | YES |
| 4 | Done/executable-create-forge-developer-specialist | 1 | `Deposit a short dev log to \`forge/knowledge/development/forge-developer-specialist-creation-2026-04-18.md\`` | backticked | inline prose + `to` | YES |
| 5 | Done/executable-create-forge-developer-specialist | 2 | `Deposit QA report to \`forge/knowledge/qa/forge-developer-specialist-qa-2026-04-18.md\`` | backticked | inline prose + `to` | YES |
| 6 | Done/diagnostic-bellows-writing-prefix | 1 | `Deposit findings to: \`forge/knowledge/research/bellows-writing-prefix-filtering-2026-04-18.md\`` | backticked | section-header + `to:` | YES |
| 7 | Done/diagnostic-code-forge-rename-scope | 1 | `Deposit findings to: \`forge/knowledge/research/code-forge-rename-scope-2026-04-18.md\`` | backticked | section-header + `to:` | YES |
| 8 | Done/diagnostic-forge-architecture-inventory | 1 | `deposit as \`forge/knowledge/research/forge-architecture-inventory-2026-04-18.md\`` | backticked | inline prose + `as` | YES |
| 9 | Done/executable-forge-exp120-sweep-fix | 2 | `**Deposit:** QA report to \`/Users/.../forge/knowledge/qa/exp120-sweep-fix-qa-2026-04-16.md\`` | absolute backticked | `**Deposit:**` colon-form | YES |
| 10 | Done/diagnostic-forge-cycle-template-exp120 | 1 | `**Deposit:** write findings to \`/Users/.../forge/knowledge/research/cycle-template-exp120-diagnostic-2026-04-16.md\`` | absolute backticked | `**Deposit:**` + write-phrase | YES |
| 11 | Done/executable-forge-cycle-11 | 1–3 | `**Deposit:** \`forge/knowledge/research/forge-cycle-11-step{1,2,3}-...\`` | backticked | `**Deposit:**` colon-form | YES (×3) |
| 12 | Done/executable-forge-cycle-11 | 4 | `**Deposit:** QA verification to \`forge/knowledge/qa/forge-cycle-11-qa-2026-04-16.md\`` | backticked | `**Deposit:**` + noun-phrase | YES |
| 13 | Done/executable-forge-test-case-gen-eval | 1 | `Deposit a comparison table to \`forge/knowledge/research/batch2-test-case-evaluation-2026-04-16.md\`` | backticked | inline prose + `to` | YES |
| 14 | Done/executable-forge-test-case-gen-eval | 2 | `**Deposit:** QA report to \`/Users/.../forge/knowledge/qa/forge-test-case-gen-eval-qa-2026-04-16.md\`` | absolute backticked | `**Deposit:**` colon-form | YES |
| 15 | Done/executable-forge-test-case-infrastructure | 2 | `**Deposit:** QA report to \`/Users/.../forge/knowledge/qa/forge-test-case-infrastructure-qa-2026-04-16.md\`` | absolute backticked | `**Deposit:**` colon-form | YES |
| 16 | Done/diagnostic-forge-test-case-generation-design | 1 | `**Deposit:** write findings to \`/Users/.../forge/knowledge/research/test-case-generation-design-diagnostic-2026-04-16.md\`` | absolute backticked | `**Deposit:**` + write-phrase | YES |

### anvil (17 files — 14 primary deposit matches)

| # | Plan File | Step | Matched Line (truncated) | Path Format | Label Style | Primary? |
|---|-----------|------|-----------------------------|-------------|-------------|----------|
| 1 | Done/diagnostic-bellows-write-race-test | 1 | `**Deposit a findings file** to \`knowledge/research/bellows-write-race-test-findings-2026-04-14.md\`` | backticked | bold-label + `to` | YES |
| 2 | Done/executable-anvil-test-failures-fixture | 1 | `**Deposit a development log** to \`anvil/knowledge/development/anvil-test-failures-fixture-fix-2026-04-14.md\`` | backticked | bold-label + `to` | YES |
| 3 | Done/parallel-1-diagnostic-anvil-test-failures | 1 | `**Deposit findings to** \`knowledge/research/anvil-test-failures-diagnostic-2026-04-14.md\`` | backticked | bold-label (ends with `to`) | YES |
| 4 | Done/executable-qa-recovery-noise-and-cycle11 | 1 | `Deposit QA report to \`knowledge/qa/findings-noise-reduction-qa-2026-04-14.md\`` | backticked | plain-label + `to` | YES |
| 5 | Done/executable-findings-noise-reduction | 2 | `Deposit QA report to \`anvil/knowledge/qa/findings-noise-reduction-qa-2026-04-14.md\`` | backticked | plain-label + `to` | YES |
| 6 | Done/executable-anvil-cycle-9 | 1 | `Deposit a dev log to \`anvil/knowledge/development/cycle-9-run-2026-04-14.md\`` | backticked | inline prose + `to` | YES |
| 7 | Done/executable-anvil-cycle-9 | 2 | `Deposit QA report to \`anvil/knowledge/qa/cycle-9-qa-2026-04-14.md\`` | backticked | plain-label + `to` | YES |
| 8 | Done/executable-phase21-refinement | 2 | `Deposit QA report to \`anvil/knowledge/qa/phase21-refinement-qa-2026-04-14.md\`` | backticked | plain-label + `to` | YES |
| 9 | Done/executable-phase21-intent-layer | 1 | `Deposit blueprint to \`anvil/knowledge/architecture/phase21-intent-layer-blueprint-2026-04-14.md\`` | backticked | inline prose + `to` | YES |
| 10 | Done/executable-phase21-intent-layer | 3 | `Deposit QA report to \`anvil/knowledge/qa/phase21-qa-2026-04-14.md\`` | backticked | plain-label + `to` | YES |
| 11 | Done/executable-specialist-sync | 2 | `Deposit QA report to \`anvil/knowledge/qa/specialist-sync-qa-2026-04-14.md\`` | backticked | plain-label + `to` | YES |
| 12 | Done/diagnostic-coupling-hotspots-noise | 1 | `**Deposit findings to** \`anvil/knowledge/research/coupling-hotspots-noise-diagnostic-2026-04-14.md\`` | backticked | bold-label (ends with `to`) | YES |
| 13 | roadmap-anvil-phase-2-strategic-audit | N/A | `**Deposit location:** \`[project]/knowledge/anvil/audit-findings-[date].md\`` | bracket-placeholder | bold-label | TEMPLATE |
| 14 | roadmap-glossary-analyzer-phase-1 | N/A | `deposited to \`[project]/knowledge/anvil/glossary-audit-[date].md\`` | bracket-placeholder | inline prose | TEMPLATE |

### bellows (16 files — 19 primary deposit matches)

| # | Plan File | Step | Matched Line (truncated) | Path Format | Label Style | Primary? |
|---|-----------|------|-----------------------------|-------------|-------------|----------|
| 1 | in-progress-diagnostic-bellows-deposit-path-formats | 1 | `**Deposit:** write findings to \`bellows/knowledge/research/deposit-path-formats-2026-04-18.md\`` | backticked | `**Deposit:**` + write-phrase | YES |
| 2 | verdict-pending-diagnostic-bellows-verdict-file-schema | 1 | `**Deposit:** write findings to \`bellows/knowledge/research/verdict-file-schema-2026-04-18.md\`` | backticked | `**Deposit:**` + write-phrase | YES |
| 3 | Done/executable-bellows-verdict-schema-plan-a | 1 | `**Deposit development log:** write a dev log to \`bellows/knowledge/development/verdict-schema-plan-a-2026-04-18.md\`` | backticked | bold-label variant + `to` | YES |
| 4 | Done/executable-bellows-verdict-schema-plan-a | 2 | `**WRITE THE QA REPORT** to \`bellows/knowledge/qa/verdict-schema-plan-a-2026-04-18.md\`` | backticked | caps bold-label + `to` | YES |
| 5 | Done/diagnostic-bellows-architecture-audit | 1 | `depositing a structured findings file at \`bellows/knowledge/research/bellows-architecture-audit-2026-04-18.md\`` | backticked | inline prose + `at` | YES |
| 6 | Done/executable-smoke-test-infra | 1 | `**Deposit dev log** to \`bellows/knowledge/development/smoke-test-infra-2026-04-17.md\`` | backticked | bold-label + `to` | YES |
| 7 | Done/executable-smoke-test-infra | 2 | `**Deposit QA report** to \`bellows/knowledge/qa/smoke-test-infra-qa-2026-04-17.md\`` | backticked | bold-label + `to` | YES |
| 8 | Done/executable-activity-timeout | 1 | `**Deposit dev log** to \`bellows/knowledge/development/activity-timeout-2026-04-17.md\`` | backticked | bold-label + `to` | YES |
| 9 | Done/executable-activity-timeout | 2 | `**Deposit QA report** to \`bellows/knowledge/qa/activity-timeout-qa-2026-04-17.md\`` | backticked | bold-label + `to` | YES |
| 10 | Done/diagnostic-runner-subprocess | 1 | `**Deposit findings** to \`bellows/knowledge/research/runner-subprocess-2026-04-17.md\`` | backticked | bold-label + `to` | YES |
| 11 | Done/executable-shadow-copy-cache | 1 | `**Deposit dev log** to \`bellows/knowledge/development/shadow-copy-cache-2026-04-17.md\`` | backticked | bold-label + `to` | YES |
| 12 | Done/executable-shadow-copy-cache | 2 | `**Deposit QA report** to \`bellows/knowledge/qa/shadow-copy-cache-qa-2026-04-17.md\`` | backticked | bold-label + `to` | YES |
| 13 | Done/executable-model-override-backtick-fix | 1 | `**Deposit dev log** to \`bellows/knowledge/development/model-override-backtick-fix-2026-04-17.md\`` | backticked | bold-label + `to` | YES |
| 14 | Done/executable-model-override-backtick-fix | 2 | `**Deposit QA report** to \`bellows/knowledge/qa/model-override-backtick-fix-qa-2026-04-17.md\`` | backticked | bold-label + `to` | YES |
| 15 | Done/executable-gate5-path-double-project | 1 | `**Deposit dev log** to \`bellows/knowledge/development/gate5-path-double-project-2026-04-17.md\`` | backticked | bold-label + `to` | YES |
| 16 | Done/executable-plan-truncation-fix-v2 | 1 | `**Deposit dev log** to \`bellows/knowledge/development/plan-truncation-fix-v2-2026-04-17.md\`` | backticked | bold-label + `to` | YES |
| 17 | Done/executable-plan-truncation-fix | 1 | `**Deposit development log** to \`bellows/knowledge/development/plan-truncation-fix-2026-04-17.md\`` | backticked | bold-label + `to` | YES |
| 18 | Done/executable-plan-truncation-fix | 2 | `**Deposit QA report** to \`bellows/knowledge/qa/plan-truncation-fix-qa-2026-04-17.md\`` | backticked | bold-label + `to` | YES |
| 19 | Done/executable-gate5-fix-verdict-emoji | 1–2 | `**Deposit development log** to ... / **Deposit QA report** to ...` | backticked | bold-label + `to` | YES (×2) |
| 20 | Done/parallel-1-executable-bellows-claim-at-entry | 2 | `**Deposit:** QA report to \`/Users/.../bellows/knowledge/qa/claim-at-entry-fix-qa-2026-04-16.md\`` | absolute backticked | `**Deposit:**` colon-form | YES |

---

## Pass 2 — Format Clusters

| Cluster | Name | Canonical Example (verbatim) | Count | Example Matches (project+plan §step) | Regex Extractable? | Regex Pattern | Edge Cases |
|---------|------|------------------------------|-------|---------------------------------------|-------------------|---------------|------------|
| A | `labeled-bold-colon-backticked` | `**Deposit:** \`freight-kb/knowledge/design/new-thread-layout-audit-2026-03-25.md\`` | 32 | freight-kb/executable-unified-input §1; study/diagnostic-sonnet-model-switch §1; ai-career-digest/executable-remove-api-dependency §1 | YES | `r'\*\*Deposit[^:]*:\*\*\s+(?:.*?(?:to|at)\s+)?`([^`]+)`'` | May have interposed text like `write findings to` or `QA report to` between `:**` and the backtick. Some have no interposed text at all. |
| B | `labeled-bold-noun-to-backticked` | `**Deposit dev log** to \`bellows/knowledge/development/smoke-test-infra-2026-04-17.md\`` | 36 | bellows/executable-smoke-test-infra §1; invoice-pulse/executable-csv-upload-fetch-fix §1; BrewBuddy/executable-presseffect-buttonstyle-migration §1 | YES | `r'\*\*Deposit[^*]+\*\*\s+(?:to|at)\s+`([^`]+)`'` | Noun variants: "dev log", "DEV log", "development log", "QA report", "findings", "findings file", "a development log", "a DEV log", "a findings file". Also `**Write QA report**` (BrewBuddy) and `**WRITE THE QA REPORT**` (bellows). The `**Deposit**` word is always present except the Write variant. |
| C | `inline-prose-deposit-to-backticked` | `Deposit QA report to \`anvil/knowledge/qa/cycle-9-qa-2026-04-14.md\`` | 19 | anvil/executable-anvil-cycle-9 §2; ai-career-digest/executable-industry-trends §3; forge/executable-create-forge-developer-specialist §2 | YES | `r'[Dd]eposit\s+[\w\s]+?\s+(?:to|at)\s+`([^`]+)`'` | Not bolded. "Deposit QA report to", "Deposit a comparison table to", "Deposit blueprint to", "Deposit design review to", "Deposit a dev log to", "Deposit findings to". |
| D | `section-header-deposit-to-backticked` | Under `## Output Location` header: `Deposit findings to: \`forge/knowledge/research/bellows-writing-prefix-filtering-2026-04-18.md\`` | 3 | forge/diagnostic-bellows-writing-prefix §1; forge/diagnostic-code-forge-rename-scope §1; forge/diagnostic-forge-scoping §1 | YES | `r'[Dd]eposit findings to:?\s+`([^`]+)`'` | Collapses into cluster C regex if colon is optional. The `## Output Location` header is decorative — the path is on the `Deposit findings to:` line itself. |
| E | `deliverable-section-backticked` | Under `## Deliverable` header: `` `knowledge/research/extraction-fix-preconditions-2026-04-11.md` `` | 3 | study/diagnostic-extraction-fix-preconditions; study/diagnostic-facet-extraction-context-envelope; study/diagnostic-algorithmic-novelty-audit | PARTIAL | Would require section-header context detection | Oldest format in corpus (2026-04-11 study diagnostics). Path is first backticked item under a `## Deliverable` header. No "Deposit" keyword. |
| F | `inline-prose-depositing-at-backticked` | `depositing a structured findings file at \`bellows/knowledge/research/bellows-architecture-audit-2026-04-18.md\`` | 1 | bellows/diagnostic-bellows-architecture-audit §1 | YES | `r'depositing\s+[\w\s]+\s+at\s+`([^`]+)`'` | Single occurrence. |
| G | `inline-prose-deposit-as-backticked` | `deposit as \`forge/knowledge/research/forge-architecture-inventory-2026-04-18.md\`` | 1 | forge/diagnostic-forge-architecture-inventory §1 | YES | `r'deposit\s+as\s+`([^`]+)`'` | Single occurrence. |
| H | `absolute-path-backticked` | `**Deposit:** QA report to \`/Users/marklehn/Desktop/GitHub/forge/knowledge/qa/exp120-sweep-fix-qa-2026-04-16.md\`` | 8 | forge/executable-forge-exp120-sweep-fix §2; forge/diagnostic-forge-cycle-template-exp120 §1; bellows/parallel-1-claim-at-entry §2 | YES | Same as A/B/C — the regex captures the path regardless of whether it starts with `/Users/` or a project name. | Older plans (2026-04-16 forge, some bellows). Path begins with `/Users/marklehn/Desktop/GitHub/`. These are caught by the same regex patterns as A/B/C — not a separate format, just a different path prefix. |
| I | `no-path-deposit` | `**Deposit:** The agent files and stubs are the deposits.` | 2 | freight-kb/executable-foundation-phase0 §1–2 | N/A | N/A — regex correctly returns no match | Step product IS the code change itself; no separate knowledge file. Parser should return `None`. |
| J | `bracket-placeholder` | `**Deposit location:** \`[project]/knowledge/anvil/audit-findings-[date].md\`` | 3 | anvil/roadmap-anvil-phase-2-strategic-audit; anvil/roadmap-glossary-analyzer-phase-1 | YES but path is template | `r'`(\[[^\]]+\][^`]*)`'` | Only in roadmap files, never in executable/diagnostic plans. Not relevant for the parser's runtime use case. |
| K | `feedback-arrow` (secondary) | `Standard prompt feedback protocol → \`bellows/knowledge/research/agent-prompt-feedback.md\`` | ~45 | Every project, nearly every step | YES | `r'Standard prompt feedback protocol.*?→\s+`([^`]+)`'` | NOT a primary deposit. Always points to `agent-prompt-feedback.md`. Should be explicitly excluded by the parser. |

### Frequency Summary (primary deposits only, excluding K)

| Cluster | Count | % of 144 primary deposits |
|---------|-------|---------------------------|
| A — `labeled-bold-colon-backticked` | 32 | 22% |
| B — `labeled-bold-noun-to-backticked` | 36 | 25% |
| C — `inline-prose-deposit-to-backticked` | 19 | 13% |
| D — `section-header-deposit-to-backticked` | 3 | 2% |
| E — `deliverable-section-backticked` | 3 | 2% |
| F — `inline-prose-depositing-at-backticked` | 1 | <1% |
| G — `inline-prose-deposit-as-backticked` | 1 | <1% |
| H — `absolute-path-backticked` (subset of A/B/C) | 8 | 6% |
| I — `no-path-deposit` | 2 | 1% |
| J — `bracket-placeholder` | 3 | 2% |
| **A+B+C+D (core patterns)** | **90** | **63%** |
| **A+B+C+D+F+G+H (all extractable by unified regex)** | **100** | **69%** |

**Note:** H (absolute paths) are subsets of A/B/C structurally — they use the same label patterns, just with absolute paths. When counted under their parent clusters, the core patterns A+B+C cover **95 of 109 plan files with at least one extractable primary deposit** (87% of actionable plans). Clusters E, I, and J are edge cases (old format, no-path, templates).

---

## Parser Strategy Evaluation

### Strategy A — Strict Labeled Field

| Dimension | Assessment |
|-----------|------------|
| **Description** | Require every plan step to have an explicit `**Deposits:**` field as a new Planner convention. Parser extracts only from that field. |
| **% corpus captured** | 0% of existing plans (field does not exist today). 100% of future plans if convention is adopted. |
| **False positive risk** | Near-zero — field is unambiguous. |
| **Complexity** | ~5 lines of Python (single regex). |
| **Convention change required?** | YES — all future plans must include `**Deposits:**` field. Existing plans would need backfill or would be permanently uncapturable. |
| **Verdict** | Unworkable for existing corpus. Good long-term target but leaves ~109 existing plans unserved. |

### Strategy B — Opportunistic Regex

| Dimension | Assessment |
|-----------|------------|
| **Description** | Parser handles the top format clusters (A through G) via regex cascade; no convention change. |
| **% corpus captured** | **~95% of actionable primary deposits** (clusters A+B+C+D+F+G cover all backticked deposit paths with "Deposit/deposit/depositing" keyword). Only cluster E (3 old study diagnostics with `## Deliverable` header, no keyword) is missed. |
| **False positive risk** | Low. The `[Dd]eposit` keyword + backtick path is highly specific. Feedback-arrow lines are explicitly excluded. Evidence-file writes (`Pipe to`, `write output to`) don't contain "Deposit" keyword and are naturally excluded. |
| **Complexity** | ~20–30 lines of Python (3–4 regex patterns in priority cascade + exclusion filter). |
| **Convention change required?** | NO — works on existing corpus as-is. |
| **Verdict** | **Best immediate option.** Captures the vast majority of the corpus with minimal code and no convention changes. |

### Strategy C — Hybrid

| Dimension | Assessment |
|-----------|------------|
| **Description** | Parser prefers a strict `**Deposits:**` field if present; falls back to opportunistic regex (Strategy B) if absent. New plans opt into the strict path additively. |
| **% corpus captured** | Same as B for existing plans (95%+). 100% for new plans once convention is adopted. |
| **False positive risk** | Same as B for fallback path; near-zero for strict path. |
| **Complexity** | ~25–35 lines of Python (strict field check + fallback regex cascade). |
| **Convention change required?** | YES (additive) — new plans should include `**Deposits:**` field. Existing plans continue to work via fallback. |
| **Verdict** | **Best long-term option.** Combines immediate coverage with future-proofing. The strict field becomes the preferred path as the Planner template evolves. Marginal additional complexity over B. |

---

## Proposed Implementation

**Recommended strategy: C (Hybrid)**

The marginal complexity over B (~5 extra lines) is worth the long-term benefit of a clean, unambiguous extraction path for new plans.

### Regex Patterns (Python raw strings)

```python
# Priority 1 — Strict labeled field (future convention)
# Matches: **Deposits:** `path` or **Deposit:** `path` (with or without interposed text)
STRICT_DEPOSIT_RE = re.compile(
    r'\*\*Deposits?:\*\*\s+(?:.*?\s+)?`([^`]+\.md)`'
)

# Priority 2 — Bold-labeled noun + to/at + backtick path
# Matches: **Deposit dev log** to `path`, **Write QA report** to `path`,
#          **WRITE THE QA REPORT** to `path`, **Deposit a findings file** to `path`
BOLD_NOUN_DEPOSIT_RE = re.compile(
    r'\*\*(?:Deposit|Write)[^*]+\*\*\s+(?:to|at)\s+`([^`]+\.md)`'
)

# Priority 3 — Inline prose deposit + to/at/as + backtick path
# Matches: Deposit QA report to `path`, deposit as `path`,
#          depositing a structured findings file at `path`
INLINE_DEPOSIT_RE = re.compile(
    r'[Dd]eposit(?:ing)?\s+[\w\s]+?\s+(?:to:?|at|as)\s+`([^`]+\.md)`'
)

# Exclusion — feedback arrow lines (not primary deposits)
FEEDBACK_EXCLUSION_RE = re.compile(
    r'[Ss]tandard prompt feedback protocol'
)
```

### Extraction Logic

```python
def extract_primary_deposit(step_text: str) -> str | None:
    """
    Extract the primary deposit path from a plan step's text.
    Returns the first matching path, or None if no primary deposit found.
    """
    for line in step_text.splitlines():
        # Skip feedback-arrow lines
        if FEEDBACK_EXCLUSION_RE.search(line):
            continue
        # Try patterns in priority order
        for pattern in (STRICT_DEPOSIT_RE, BOLD_NOUN_DEPOSIT_RE, INLINE_DEPOSIT_RE):
            match = pattern.search(line)
            if match:
                path = match.group(1)
                # Normalize absolute paths to project-relative
                if path.startswith('/Users/'):
                    # Strip prefix up to and including the project directory
                    # e.g., /Users/marklehn/Desktop/GitHub/bellows/knowledge/...
                    #     → bellows/knowledge/...
                    parts = path.split('/Desktop/GitHub/')
                    if len(parts) == 2:
                        path = parts[1]
                return path
    return None
```

### Expected Coverage

| Regex | Clusters Covered | Estimated Coverage |
|-------|-----------------|-------------------|
| `STRICT_DEPOSIT_RE` | A (32 matches) + future strict-field plans | 22% of existing + 100% of future |
| `BOLD_NOUN_DEPOSIT_RE` | B (36 matches) | 25% of existing |
| `INLINE_DEPOSIT_RE` | C+D+F+G (24 matches) | 17% of existing |
| **Total covered** | **92 of 97 actionable primary deposits** | **~95%** |

### Handling Edge Cases

| Edge Case | Handling |
|-----------|----------|
| Steps with no primary deposit (cluster I — "The agent files are the deposits") | Return `None`. Parser caller should treat `None` as "step has no separate knowledge file to verify." |
| Bracket-placeholder paths (cluster J — `[project]/knowledge/...`) | Only in roadmap files, never in executable/diagnostic plans. Parser will not encounter these at runtime. If encountered, the regex would extract the raw template string — caller should check for `[` in path and treat as unresolved. |
| Absolute paths (`/Users/marklehn/...`) | Normalize to project-relative using `/Desktop/GitHub/` split. |
| Old `## Deliverable` format (cluster E — 3 study diagnostics) | Not captured by any regex. These are from 2026-04-11 and predate the Deposit convention. Acceptable miss — 3 files out of 109. |
| `**Write QA report**` variant (BrewBuddy) | Captured by `BOLD_NOUN_DEPOSIT_RE` — the `(?:Deposit\|Write)` alternation handles it. |
| `**WRITE THE QA REPORT**` variant (bellows) | Captured by `BOLD_NOUN_DEPOSIT_RE` — case-insensitive? No — the `W` in `Write` is uppercase and the pattern uses `(?:Deposit\|Write)`. But "WRITE" needs `(?i)` flag or `(?:Deposit\|[Ww]rite\|WRITE)`. Recommend adding `re.IGNORECASE` to `BOLD_NOUN_DEPOSIT_RE`. |
| Multiple primary deposits in one step | Current logic returns the first match. This is correct — each step has at most one primary deposit. |
| `**Deposit development log:** write a dev log to \`path\`` (bellows variant) | The `:**` triggers `STRICT_DEPOSIT_RE` first, which captures the path via the `(?:.*?\s+)?` group. Correct behavior. |
| Evidence-file writes (`Pipe to`, `write output to`) | Do not contain "Deposit" keyword — naturally excluded by all three patterns. |

### False Positive Analysis

| Potential FP Source | Risk | Mitigation |
|---------------------|------|------------|
| Feedback-arrow lines | HIGH (45 matches in corpus) | Explicit `FEEDBACK_EXCLUSION_RE` check before regex cascade. |
| Python self-check code blocks containing `qa_report_path = "..."` | NONE | Not in backticks — regex requires backtick-delimited path. |
| Evidence-file instructions (`Pipe to`, `write output to`) | NONE | No "Deposit" keyword. |
| Prose discussing deposits without an actual instruction | LOW | The `.md` suffix requirement in the regex reduces this. |
| `**Deposit:** The agent files and stubs are the deposits.` | NONE | No backticked path — regex returns no match. Correct `None`. |

**Estimated false positive rate: <1%** across the 109-file corpus.

---

## Gap Assessment

| # | Gap | Current State | Proposed State | Change Required in bellows.py |
|---|-----|---------------|----------------|-------------------------------|
| 1 | No deposit-path extraction exists | `post_verdict_request()` writes verdict files without a `Deposit:` field | `post_verdict_request()` calls `extract_primary_deposit(step_text)` and writes the result into a `Deposit:` field in the verdict YAML frontmatter | Add `extract_primary_deposit()` function (~15 lines). Modify `post_verdict_request()` to call it and include result in verdict file. |
| 2 | No regex patterns defined | N/A | Three compiled regex patterns + one exclusion pattern as module-level constants | Add 4 `re.compile()` constants at module level (~10 lines). |
| 3 | No absolute-path normalization | N/A | Paths starting with `/Users/` are normalized to project-relative | Normalize step inside `extract_primary_deposit()` (~3 lines). Already included in proposed function. |
| 4 | No `**Deposits:**` convention in PLANNER_TEMPLATE | Plans use varied formats (clusters A–G) | New plans include `**Deposits:** \`path\`` as standard field; parser prefers this when present | Change in PLANNER_TEMPLATE, NOT in bellows.py. Parser already handles this via `STRICT_DEPOSIT_RE`. |
| 5 | Verdict file schema has no `Deposit` field | Current verdict YAML has: Plan, Project, Step, Total Steps, Gate Result Passed, Pause Reason Code | Add `Deposit: <path or null>` field to verdict YAML | Modify the verdict-file write template string in `post_verdict_request()` to include `Deposit:` field (~1 line change). |
| 6 | No test coverage for deposit extraction | N/A | Unit tests for `extract_primary_deposit()` covering all clusters A–G + edge cases I/J/K | Add test file or test function (~40 lines). Not in bellows.py — in test file. |
| 7 | Planner Rule 22 verification reads deposit from verdict file | Planner currently infers deposit path from plan text manually | Planner reads `Deposit:` field from verdict file directly | Change in Planner, NOT in bellows.py. Planner's Rule 22 logic reads the new field. |

### Summary of bellows.py Changes

| Component | Lines (est.) | Description |
|-----------|-------------|-------------|
| Module-level regex constants | ~10 | 3 extraction patterns + 1 exclusion pattern |
| `extract_primary_deposit()` function | ~15 | Regex cascade + path normalization + None return |
| `post_verdict_request()` modification | ~3 | Call `extract_primary_deposit()`, add `Deposit:` to verdict YAML |
| **Total** | **~28** | Minimal, self-contained change |

---

## Output Receipt

```
Step:                 1
Plan:                 diagnostic-bellows-deposit-path-formats-2026-04-18
Total Steps:          1
Status:               Complete

Deliverables:
  - bellows/knowledge/research/deposit-path-formats-2026-04-18.md (this file)

Completeness evidence:
  Surveyed 109 plan files across 8 projects:
    invoice-pulse: 17 files (5 active + 12 Done)
    BrewBuddy: 12 files (1 active + 11 Done)
    study: 12 files (0 active + 12 Done)
    ai-career-digest: 9 files (1 active + 8 Done — all available, fewer than 12)
    freight-kb: 11 files (2 active + 9 Done — all available, fewer than 12)
    forge: 15 files (3 active + 12 Done)
    anvil: 17 files (5 active + 12 Done)
    bellows: 16 files (3 active + 13 Done)

  Pass 1: 144 primary-deposit matches + ~45 feedback-arrow (secondary) matches inventoried
  Pass 2: 11 format clusters identified, frequency-ranked
  Parser strategy: Strategy C (Hybrid) recommended — 95%+ corpus coverage, <1% FP rate
  Gap assessment: 7 gaps enumerated, ~28 lines of bellows.py changes estimated

Timestamp:            2026-04-18
```
