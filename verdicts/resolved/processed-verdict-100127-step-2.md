continue

CONTINUE. Seventeen gates passed mechanically; the Planner's own check is whether the deposit fixes
the original defect, and it does — verified by reading the code and the evidence, not the report.

Thread 127: a finding could not be attached to a thread that must stay open. Verified shipped:
  - `note` is a registered subcommand — `{add,list,show,done,drop,claim,release,supersede,retype,note}`
  - all five named tests exist and pass; the suite reads `138 passed` against P6's 133 baseline, which
    is 133 plus exactly the five
  - the five node ids run clean: `5 passed`

THE TWO FINDINGS THAT MADE THIS NOT A ONE-LINER ARE BOTH CORRECTLY IMPLEMENTED.

`NON_STATUS_EVENTS = {"noted"}` sits at db.py:125 and is consumed at BOTH derivations — :132 inside
`thread_status`, and :335 inside `list_threads`' inline computation. That was W1-2's whole point: the
two move together or `list` and `show` disagree about the same thread. They move together.

W4-2's guard is right. `schema/009` does NOT copy 008's existence idiom, which would have been false
on the first apply and made the migration a silent no-op. It selects `pg_get_constraintdef(oid)`,
tests `if _def not like '%noted%'`, and only then drops and re-adds. That is the definition-based
guard the walk specified.

W5-1's end-state assertion is visible in the evidence rather than assumed: the twice-applied file
records both applies completing AND the end state after the second — "noted accepted after second
apply: count=1", "bogus_event rejected after second apply: CheckViolation confirmed", "END STATE OK".
Absence of an error was explicitly not accepted as the assertion, and it was not what was delivered.

W1-6's docstring correction landed: the false claim "the event vocabulary is a STATUS vocabulary"
returns zero occurrences, and db.py:177 now names NON_STATUS_EVENTS instead. That claim had been
measured live at total_open 86 → 87, and it is no longer true of this codebase.

⛔ WHAT THIS VERDICT DOES NOT MEAN. The feature is shipped and INERT until an operator applies the
migration to the live database. `apply_schema` has no production caller — only devserver.py against a
throwaway pgserver, and the test suite against its own DB — so merging leaves the live
`thread_events` still rejecting `noted`, and `tuyere.threads note` will fail at runtime while every
test stays green. That is thread 424. The apply is ordered: merge, every machine pulls, THEN apply,
and only then the first note (W1-7) — because a note written while a machine lags is read by that
machine's unchanged derivation as a status.

Thread 425 (retype_thread writing its own event) is unblocked by this but must wait for the apply.

auto_close is false, so the close is the Planner's continue verdict on this final step — which this
is, and which I am taking deliberately rather than describing as someone else's act.
