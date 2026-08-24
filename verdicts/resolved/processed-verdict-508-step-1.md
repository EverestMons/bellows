verdict: stop

All eleven mechanical gates PASS; the stop is a Planner Rule 22(b) substance
finding, verified against live code, of the class only the substance check can
see.

THE DEFECT: the plan's S6 pin (folded at walk 3, W3-1) mandated re-verifying
the four exec-485 dogfood residuals against current code before use. The audit
re-verified none of them, and one materially distorts its own E2/R3 design:

  - VERIFIED by the Planner: depositor._assign_class (depositor.py:255-278)
    returns `governed-tooling` as the CATCH-ALL for any plan neither read-only
    nor register-writing — the class therefore CONTAINS all ordinary
    app-feature work in every project. The audit's R3 recommendation ("Stay
    held: governed-tooling — modifies bellows or doctrine code") describes the
    class falsely and would permanently HOLD the majority of real work,
    defeating ruling R3 (CEO leans auto-clear) while presenting itself as
    implementing it. This is residual (i) from exec-485, reproduced today.
  - Residuals (ii) cycle_check nested-repo register N/A and (iii) qa
    known_failures declaration: not re-verified anywhere in the deposit
    (searched by content: _assign_class 0, app-feature 0, known_failures 0,
    governance-register 0 hits). Residual (iv) held-clear IS covered as
    bypass (b).

WHAT STANDS (verified): re-derived pin table including the S8 supersede (3→4
stale hooks, evidence given); mechanism-granularity stage tables with file:line
spot-checked (clean_gate_auto bellows.py:1077, depositor gate lines, wrap hook
wiring); bypasses (a)-(g); the traceability matrix with its reverse check;
PC3's exact R1 sentence present (count=1); PC4 cross-references (1/1); the
five forks. The corrective is SCOPED, not a rewrite.

DISPOSITION: corrected re-deposit under the stable slug follows — it re-runs
the four residual verifications with file:line and repairs the R3
class-taxonomy section (and Fork 4's description of the same classes). This is
the 506→507 pattern: the deposit is consumed downstream (E2's design), so the
artifact gets fixed, not annotated around.

Recorded for the audit's own evidence base: the first run through the
mechanized lane produced a deposit whose mechanical gates all passed and whose
substance check caught a real defect — the lane's division of labor working,
and a live datum for E4 (verdict conditioning cannot replace 22(b); it can
only mechanize the checker-backed half).
