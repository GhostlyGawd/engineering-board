# D.1 measurement correction cycle — 2026-09-09

## Assignment before implementation

The owner approved correction of engineering-board/B005, B006 and B007 through
one builder and an independent verifier. Base source:
`117c542c8a65e57c421fca09f8483a3c146ce7d0`.

- Lead: `/root`; owns integration, canonical board changes, product documentation
  and delivery.
- Builder: `/root/build_measurement`, branch `build/d1-measurement-evidence` in
  a separate worktree; owns harness, operator/response contract, tests and usage
  documentation under evaluation/.
- Verifier: `/root/verify_measurement`; fresh context, read-only; reads the
  requirements and artifacts independently and rechecks committed revisions.
- Work order: B005 evidence contract, B006 safeguards, B007 planned population.
  Each phase has a separate lead-owned claim on behalf of the builder.
- Evidence destination: this versioned record, committed rubric and regression
  fixtures/tests. No live client or experimental results are part of this cycle.

## Acceptance and product boundary

| Entry | Acceptance fixed before implementation | Independent adversarial checks |
|---|---|---|
| B005 | Retained response or ordered emitted events bind the evaluated memory and first correction. Only supported observable ordering counts. | Missing evidence, changed target/status/disposition/correction, mismatched spans/indices, correction-first order, and a supplied true flag alone cannot produce verified success. Score-time validation detects edited evidence. |
| B006 | Separate v2 safeguards expose rejected-memory application and lexical-decoy use; v1 gates retain their meaning. | A complete run fails the v2 safeguard even with durable_systemic_conclusion=false when either disposition or treatment records prohibited use. Contradictory annotations cannot conceal it. Healthy hold/reject are permitted. |
| B007 | Preparation pins evaluation version and eligible positive reference-context trial keys. Eligibility never depends on arrived attempts. | Zero-attempt, one-of-many, v1-only, mixed and complete v2 runs distinguish planned, observed, missing, incompatible and available results. Headline and per-case counts agree. |

Observable response order is narrower than an agent's internal reasoning order.
The metric must state that limit. Semantic judgments about the quality of a
memory decision remain reviewer judgments with supporting evidence. Supplying
a label or arranging output fields does not itself demonstrate useful reasoning.

This cycle implements evidence integrity and honest reporting for the existing
memory-evaluation target. It does not introduce a new product-effect threshold,
rescore old evidence as a success, lock the proposal corpus, or establish that
memory improves diagnoses. Historical v2 attempts without sufficient evidence
can remain readable as reviewer annotations but cannot become verified ordering
successes. V1-only historical score fields must remain reproducible.

## Independent verification plan

The verifier defined the acceptance matrix before seeing builder conclusions.
It additionally identified two integration hazards: stored attempts are editable
and scoring currently trusts them, and the per-case counter independently trusts
the raw supplied ordering flag. Verification covers recording and rescoring,
both report levels, and negative controls.

The lead will record builder revisions, independent verdicts, corrective rounds,
integration checks and remaining limitations here before closing the entries.
All live-evaluation and release holds remain in effect while this work is pending.

## B005 implementation contract

Before code changes, the lead selected the builder's smaller raw-response
design: retain the exact JSON response string and SHA-256, reject duplicate
keys, and bind the parsed response fields to the recorded attempt. Preparation
stores the complete versioned rubric; recording and scoring verify the rubric
and response evidence. The classifier compares the emitted top-level
memory_evaluation field with first_proposed_correction. Sorted serialization of
the enclosing attempt must not change the order retained inside the string.

A correction-first response with an honest false classification remains a
measured failure. Missing legacy evidence remains an annotation, and a
contradictory supplied true classification cannot count as verified success.
Both detailed and aggregate reporting use the same classifier. This verifies
structured output order; it cannot establish internal reasoning order or the
semantic quality of an evaluation.

### Independent pre-implementation correction

The verifier identified an early-correction counterexample: evidence_or_gap or
first_stated_cause may itself propose a patch before the dedicated correction
field. Field order alone is therefore insufficient for B005's target. The lead
revised the contract before implementation completion to require a semantic
ordering review under a frozen rubric, with reviewer identity, rationale and
exact retained-response spans/quotes for the complete evaluation and the first
local correction anywhere in the response. Machine checks bind those claims to
the response bytes and compare their positions; selection of the semantic
spans remains explicitly attributed to the reviewer. Field order can be
reported only as a narrower structural diagnostic. This preserves the target
instead of silently substituting an easier measurement.

## First review round

B005 builder revision `bc40217` passed 30 evaluation tests. Independent
verification confirmed duplicate rejection, span bounds and quote matching,
Unicode/escape handling, early correction controls, legacy annotation exclusion
and score-time raw-response tamper detection. It required two corrections:

- Python equality allowed raw JSON numeric 0 to bind to recorded boolean false.
  Response binding must compare types as well as values and reject non-JSON
  numeric constants.
- A response containing no local correction needs explicit null correction
  evidence and a reviewer attestation that none exists. Its ordering measurement
  is unavailable/not applicable; it must not force a false semantic label or
  receive vacuous before-local credit.

The lead returned B005 to implementation. B006 builder revision `edbfb07`
passed 32 tests and moved to independent review. None of these intermediate
passes resolve the pending correction entries or release hold.

B006 independent review passed `edbfb07`. The verifier retained all 48 scored
arms per complete synthetic run and combined contradictory annotations,
independent rejected-only/decoy-only signals and healthy hold controls. Exactly
four rejected-use and four decoy-use keys were reported for its mixed adversarial
case. Historical v1 gates matched the complete v1 comparison. Observed-only
safeguards were explicitly left insufficient for complete-run clearance; B007
owns that completeness correction.

B005 corrective revision `782594a` passed 33 builder tests and moved to
independent recheck. It adds strict JSON value binding, rejects non-finite
constants and permits an explicit no-local-correction review with unavailable
ordering. The same builder then moved to B007 under a new claim.

B005 independent recheck passed `782594a`. Recorder/scorer probes rejected raw
0, 0.0 and non-finite constants in place of false. A systemic-only response with
an honest no-local-correction review remained retained with unavailable ordering;
contradictory declarations rejected. Combining that response with a healthy
ordering success still left the aggregate rate unavailable. This closes the
two findings from the first review without claiming automatic semantic judgment.
