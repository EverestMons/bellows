verdict: continue

Diag-301 (clone-provenance trigger). Step 1 clean: success=true, no permission denials,
receipt Complete, escalate=false. Deposit at the exact declared path, 32946 bytes -- the
do-not-re-date note held and scope_check's basename match was satisfied.

=== RULE 22 (a)-(e), RUN BY READING THE FILE, NOT THE SUMMARY ===

(a) exists -- verified on disk before reading.
(b) answers the questions -- all five (C1-C5) have sections, plus Provenance and instrument,
    the firing table, CEO decisions surfaced, can-and-cannot-establish, and Unresolved. Every
    mandated section present.
(c) summary matches file -- each headline claim in the agent's report re-checked against the
    deposit text. No divergence.
(d) ONE DEFECT, ACCEPTED BY THE CEO RATHER THAN SENT BACK. Line 252 shows a mid-sentence
    recount: a 21-item ID list left attached to a figure corrected to 20. The arithmetic is
    independently traceable (T-8 fires on 10 named plans; 30 - 10 = 20) and Unresolved item 1
    flags a +/-2 uncertainty from plans 290/292, so no conclusion turns on it -- but the
    enumeration backing that count is not legible as written. Recorded, not papered.
(e) n/a -- diagnostic, no QA report.

The plan's own hash instruction earned itself on first use. It cited an inherited value of
a74ad85e8e61b302; the deposit reports 85e97de2d7a002d7 and MATCHES. Both are correct: I
reproduced them independently as sha256[:16] and blake2b-8 of the same unchanged file. 299's
PLAN recorded the sha256 truncation, 299's DEPOSIT the blake2b. Because the plan demanded the
hash TOGETHER WITH THE COMMAND, this resolved in one check instead of becoming a false
discrepancy. That fold was V3, made at walk 1.

=== THE SUBSTANTIVE RESULT: THE DIAGNOSTIC KILLED ITS OWN PROPOSAL ===

C5(b) -- the question that exists only because walk 2's retraction turned the motivating
premise into a question -- came back negative. Of the three non-recoverable panel findings,
only 282 is clone-drift. 281 is a subtractive-trim failure the plan's OWN warm walk
introduced. 289 is an inherited-premise failure: the parent carried the same wrong premises,
faithfully reproduced, so a diff against the parent shows NO divergence and §2.6's clone-diff
discipline structurally cannot catch it.

And no candidate separates the three from the general clone population:
  (i)  T-8 inverted   -- fires 20/30, T2 load 28 (vs today's 19). REVERSES the re-scoping's
                         relief; the load exceeds today's.
  (ii) §2.6 strict    -- fires 10/30, and MISSES 282, the one real clone-drift case, because
                         282 wrote "Clone of 275" without "proven."
  (iii) 289:11        -- fires 6/30, T2 load 19, delta 0. Reproduces all three but also fires
                         on three plans whose panels found nothing.

Central finding: the discriminator is the DEFECT CLASS -- subtractive-trim, clone-drift,
inherited-premise -- NOT clone provenance. All three classes already have codified
instructions in §2.6/§2.7. None has mechanical enforcement. THE GAP IS ENFORCEMENT, NOT
DETECTION.

=== CEO DECISION TAKEN AT THIS GATE: OPTION C ===

Three cases, three instruments, all three already existing as instructions. No new trigger.
The question becomes how to make the existing instructions bite. This supersedes the
clone-trigger direction and unblocks the executable, which no longer waits on a trigger.

It converges with the probe-wrapper work reached independently the same day from the other
side: the rules exist, they are prose, and prose does not bind. Enforcement is the shared
problem.

Closing 301.
