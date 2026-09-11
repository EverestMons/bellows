# Dev Log — guard-class-hold-parked-2026-09-11

## Pins re-derived (P1, P2, P3, P5)

2026-09-11 00:5x: `hold-executable-bellows-step-status-transition.md` (class shop-infra, the overnight delegation withheld releases) → `pin` FROZEN → withdrawn under STANDING_CONSTRAINTS line 9 → redeposited by the CEO at 08:00 → released → #100073 Done; one extra CEO act for nothing the guard protects

P1 — `tools/lessons_guard.py`: `_KIND` :44; `_FREEZING_RE` :53–55 (`^(?:parallel-\d+-)?(?:hold-|ready-|in-progress-|verdict-pending-)?(?:executable|diagnostic|qa)-.*\.md$`); `_PARKED_PREFIXES = ("halted-", "parked-", "obsolete-")` :59; `freezing_plans(root)` :84–87 (thin wrapper over `_scan`); `_scan` :84–113 (the sidecar branch); `_report_frozen` :128–137; `pin` prints `lanes: N  frozen: no  class-held: N` (:161); `verify` prints `lanes: N  frozen: no  class-held: N  sha: unchanged — safe to write NOW` (:173); `shop_root()` :62, `decision_lanes()` :73 — no sidecar read in original `freezing_plans`, confirmed no mechanism mismatch.

P2 — sidecar naming: `depositor.py:847` uses `"hold-" + claimable_name.replace(".md", ".hold.json")`; `clear_plan.py:55` uses `os.path.splitext(hold_path)[0] + ".hold.json"` — both yield `hold-executable-N.hold.json` for `hold-executable-N.md`; guard uses `f.stem + ".hold.json"` (same rule). Sidecar `hold_reason` values from depositor: `class:<name>` (:194), `empty_writes` (:232), collision reason (:243), `held_pending_ceo_release` (:245); claim's `stale-checkout` (bellows.py:1027). No pre-existing sidecar read in the guard — no mechanism mismatch.

P3 — `tests/test_lessons_guard.py`: `_shop` helper (now with `sidecars=` param); `TestFreezePredicateTable.test_row` parametrize (20 rows: 15 existing with sidecar=None, 5 new: t-a, t-b, t-c, t-e, t-f); `test_parked_class_holds` (t-g); `test_pin_class_hold_not_frozen` (t-h); `test_pin_frozen_names_only_stale` (t-i); plus 6 module-level tests. Original table had 15 rows (plan said 16; counted 15 in the file, proceeded with 15).

P5 — `hooks/commands/wrap.md:77` after edit: "…`in-progress-` and `verdict-pending-` DO, and, since bellows #100076 (thread 278), a `hold-` deposit whose sidecar says `hold_reason: class:…` — a plan awaiting the CEO's release."

## Failing-first (red, then green)

red:   5 failed, 24 passed in 0.64s
green: 2262 passed, 1 skipped in 97.87s (0:01:37)

## The guard observed (t-a, t-b, t-h)

t-a: PASSED — `hold-executable-100031.md` with class sidecar → not in `freezing_plans`, not frozen
t-b: PASSED — `hold-executable-100031.md` with stale-checkout sidecar → in `freezing_plans`, frozen
t-h: PASSED — pin with one class hold → exit 0

pin line (guard run on synthetic shop with one class hold):
lanes: 2  frozen: no  class-held: 1

## Mutation run

Mutant m3 (`if sidecar.is_file():` → `if True:`) was equivalent: FileNotFoundError caught by `except Exception: pass` — no-sidecar hold still froze. Redesigned m3 replacement to `if not sidecar.is_file(): parked.append(f); continue; if True:` which parks on absent sidecar — killed by t-d. Manifest updated in a third DEV commit (two-commit post-condition not met: three DEV commits total due to mutant redesign).

MUTATION: 3 killed, 0 survived, 0 error
