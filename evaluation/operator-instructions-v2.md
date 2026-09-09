# Milestone D.1 memory-evaluation trial instructions

You are in a controlled engineering diagnosis trial.

Use only the task, file list, case evidence, and optional Engineering Board
context in the trial prompt. Do not use information from another trial. Do not
call a tool. Do not read another file. Do not change a file.

If Engineering Board context is absent or its `results` list is empty, return
`"memory_evaluation": null` and diagnose from the supplied case evidence. Do
not invent memory, incident identifiers, or an evaluation. The recorder must
classify `memory_evaluation_before_local` as `false` for these responses.

When memory is supplied, treat it as prior repository memory. Preserve its
epistemic status. Before you propose a local correction, evaluate the most
relevant surfaced memory: identify its current and prior incidents, then choose
`apply`, `hold`, or `reject`. Use `apply` only when supplied evidence supports
the cross-incident claim. Use `hold` when the memory is plausible but the
prompt lacks evidence needed to adopt it. Use `reject` when supplied evidence
shows that it does not apply. Copy the memory identifier and status from the
supplied result, including a `c-...` identifier when evaluating a cluster. Use
only supplied incident identifiers; leave an incident list empty if none are
supplied. State the supporting evidence or information gap.

Then state the first cause that you identify and the first correction that you
propose. A local cause or correction remains acceptable after an explicit
`hold` or `reject`; do not promote a proposed hypothesis merely to produce a
systemic answer.

Cite only the supplied case evidence identifiers. Return one JSON object that
conforms to `evaluation/memory-evaluation-response.schema.json`. Do not add
Markdown or other text.

Emit `memory_evaluation` before `first_proposed_correction`, and emit
`first_proposed_correction` before `final_diagnosis`. The evaluator retains the
exact response and measures this observable structured-field order. It does
not infer when you internally considered a cause or correction. Never repeat
a JSON object key.

A correction proposed in any field, including the evaluation's
`evidence_or_gap` or `first_stated_cause`, counts as a correction. A reviewer
identifies its earliest occurrence in the retained response; the dedicated
field order alone does not establish that evaluation happened first.
