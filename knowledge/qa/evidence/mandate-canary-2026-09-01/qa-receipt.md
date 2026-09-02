# QA Receipt — mandate-canary-2026-09-01

**Plan:** 100013  
**Slug:** mandate-canary-2026-09-01  
**Date:** 2026-09-02T04:46:10Z  
**Worktree HEAD:** afefaa7  
**Tier:** T0  

## Purpose

This canary verifies that the restarted Bellows daemon (pid 98058, sha 6b892a3, started 2026-09-01) now injects the correct governance-root-resolved Rule 20 path into QA step prompts. The RECEIVED path is the path this agent was handed in its own prompt mandate text. The COMPUTED path is what the live `gates.QA_MANDATE_SUFFIX` code would inject.

## Verification Table

| Item | Measured Value | Status |
|------|---------------|--------|
| RECEIVED path (from prompt mandate) | /Users/marklehn/Developer/eluvian-governance/RULE_20_SELF_CHECK_BLOCK.md | ✅ |
| COMPUTED path (from gates.QA_MANDATE_SUFFIX) | /Users/marklehn/Developer/eluvian-governance/RULE_20_SELF_CHECK_BLOCK.md | ✅ |
| RECEIVED == COMPUTED | yes | ✅ |
| RECEIVED_EXISTS | RECEIVED_EXISTS | ✅ |

## Evidence Files

- `probes-raw.txt` — raw measurement output for all 6 probes

## Rule 20 Self-Check Output

```
============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
Evidence folder: /Users/marklehn/Developer/bellows/.bellows-worktrees/100013/knowledge/qa/evidence/mandate-canary-2026-09-01
Files verified: 1
```
