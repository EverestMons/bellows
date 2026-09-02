# QA Receipt — COMPANY.md v2.8: shop/server invariant
**Plan:** 100019 — shop-server-invariant-company-2026-09-02
**Date:** 2026-09-02
**Step:** 2 (QA)
**QA agent:** bellows QA

## Step 1 Receipt Status

Step 1 complete — commit `ecccd5b [100019] shop/server invariant: COMPANY.md v2.8 committed in governance (dev log)` present on branch `bellows-wt/100019`.

## Verification

| Item | Check | Expected | Evidence | Status |
|------|-------|----------|----------|--------|
| 1 | Governance commit subject | `[100019] COMPANY.md v2.8:…` | `9c99ff0 [100019] COMPANY.md v2.8: a machine runs the shop, the mini is the server, the only permitted difference (CEO 2026-09-02)` | ✅ |
| 1 | P3 token: `A MACHINE runs the shop` | 1 | 1 | ✅ |
| 1 | P3 token: `**Version:** 2.8` | 1 | 1 | ✅ |
| 1 | P3 token: `the only permitted difference between shops` | 1 | 1 | ✅ |
| 1 | Retired token: `**Version:** 2.7` | 0 | 0 | ✅ |
| 1 | Line count | 350 | 350 | ✅ |
| 1 | `git status --porcelain -- COMPANY.md` | EMPTY | EMPTY | ✅ |
| 2 | `landing_date` from live line 4 | 2026-09-02 | 2026-09-02 | ✅ |
| 2 | Builder BUILT line (`date=`, `lines=`, `delta_chars=`, `delta_bytes=`, `edits=`, `post=`) | `lines=350 delta_chars=507 delta_bytes=509 edits=3 post=7/7` | `BUILT: /tmp/ssic-qa/COMPANY-out.md lines=350 delta_chars=507 delta_bytes=509 date=2026-09-02 edits=3 post=7/7` | ✅ |
| 2 | `builder_exit` | 0 | 0 | ✅ |
| 2 | Byte-identical rebuild | BYTE_IDENTICAL | BYTE_IDENTICAL | ✅ |
| 2 | P4 disk digest | 07374437b30be915 | 07374437b30be915 | ✅ |
| 2 | P4 blob digest (builder's own commit `af5b216`) | 07374437b30be915 | 07374437b30be915 | ✅ |
| 2 | Refusal 1 (out==in) | BUILDER REFUSED + exit nonzero | `BUILDER REFUSED: out == in`, exit=1 | ✅ |
| 2 | Refusal 2 (under governance root) | BUILDER REFUSED + exit nonzero | `BUILDER REFUSED: out is under the governance root /Users/marklehn/Developer/eluvian-governance`, exit=1 | ✅ |
| 2 | Refusal 3 (already-built input) | BUILDER REFUSED + exit nonzero | `BUILDER REFUSED: anchor count 0 != 1 for: **Version:** 2.7`, exit=1 | ✅ |
| 2 | Refusal 4 (malformed date; live file is v2.8, builder refuses on anchor check before date) | BUILDER REFUSED + exit nonzero | `BUILDER REFUSED: anchor count 0 != 1 for: **Version:** 2.7`, exit=1 | ✅ |
| 3 | Porcelain: COMPANY.md + sketch | EMPTY | EMPTY | ✅ |
| 3 | Full governance porcelain line count | informational | 0 | ✅ |
| 4 | Full suite file present and non-empty | `full-suite-shop-server-invariant-company.txt`, exit=0 | `full-suite-shop-server-invariant-company.txt` present; exit=0 | ✅ |

## Follow-ups (open, not blocking)

- **MACHINE_SETUP v1.3** — update "Shop machine" wording to reflect that every machine is a shop; the mini's server role is the only permitted difference (separate plan, separate step).
- **GLOSSARY.md** — add or update the shop/server invariant entry per the CEO ruling (separate plan).
- **Planner pushes governance** — the governance commit `9c99ff0` in `eluvian-governance` is unpushed; the Planner will push after the pause.

## Rule 20 Self-Check

============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
Evidence folder: /Users/marklehn/Developer/bellows/.bellows-worktrees/100019/knowledge/qa/evidence/shop-server-invariant-company-2026-09-02/
Files verified: 2
