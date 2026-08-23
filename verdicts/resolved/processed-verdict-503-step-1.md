verdict: continue

Planner verification (Rule 22(b)) — plan 503 (diagnostic, READ-ONLY), Step 1 of 1, TERMINAL. All eleven gates PASS. **Continue WITH A CORRECTION — the findings document contradicts its own data file, and the correction is recorded here so the companion executable cannot inherit the error.**

## ⚠️ THE CORRECTION: the promotion set is 19 entries, not 15

The deposited TSV — which this plan designates as the companion executable's input, explicitly "data, not prose" — contains **21 rows covering 19 distinct entries**, ids 61 70 85 89 90 96 98 106 109 111 119 120 121 140 142 184 191 231 340. It is internally consistent: 19 distinct by `entry_id` AND 19 distinct by `entry_heading`, no id mapping to two headings, zero blank ids, and Q4 states ASSERTED rows are not in the file, so all 21 rows are DEMONSTRATED.

**The prose says 15, in six places** (`:292`, `:293`, `:303`, `:304`, `:306`, `:308`), and Q5's arithmetic is built on it. Both figures produce a balancing identity, which is why nothing caught it — 15+224+74+14 and 19+220+74+14 both total 327 — so the error is invisible to any check that only tests whether the sum closes.

**The corrected sizing:** `learned` **19**, `codified` **220** (= X − 19), `pending` 74, bare 14, total 327. Identity holds; three-state subtotal 313 = N − Q.

**The TSV is authoritative and the executable must read it rather than the prose.** ⚠️ Note the plan's numbers-discipline table owns N/X/P/Q/E/M/C but NOT the promotion count — that figure is a measured OUTPUT, so `propagation_check` had no symbol to guard and structurally could not catch this. That gap is worth carrying.

## Verified independently of the receipt

1. **THE DEMONSTRATIONS ARE REAL — I RE-RAN THEM, I DID NOT READ THEM.** Importing `gates` directly and exercising three of the DEMONSTRATED set: `receipt_status`, `no_errors` and `ceo_flags` each returned exactly one failure naming that gate on the constructed violation, and zero failures on the positive control. The bar this plan set — construct the violation, observe the rejection, confirm it names the right check against a control — was genuinely met, not asserted.

2. **THE MOST VALUABLE POSSIBLE RESULT WAS SOUGHT AND CAME BACK EMPTY, WHICH IS ITSELF A RESULT.** "Mechanisms that DID NOT reject their violation: None." Every mechanism tested rejected for the correct reason. That is the honest outcome and the plan required it to be reported first and separately; it was.

3. **THE INVENTORY IS DISCRIMINATING, NOT A HEADCOUNT.** Q1 separates 9 blocking gates from 1 informational and 1 utility; 4 blocking `plan_lint` checks from 6 WARN-only; and — the sharpest cut — **3 real enforcers among the checker scripts from 3 non-enforcers**. A mechanism that only warns does not enforce, and the agent drew that line rather than counting files.

4. **THE MANY-TO-MANY MAPPING SURVIVED INTO THE DELIVERABLE.** 21 rows over 19 entries: the (entry, mechanism) pair schema this cycle's walk 3 established is doing real work rather than collapsing to one row per entry.

5. **DIRECTION 2 WAS ANSWERED.** Mechanisms mapping to NO corpus entry are reported — enforcement the corpus never captured, i.e. rules learned without ever being written down.

The arc's question is answered: under the CEO's completion definition, **19 of 327 entries are genuinely `learned`**. That is the number the re-label executable must promote, and it is a far smaller and far more honest figure than the 239 it replaces.

Terminal step: close to Done.
