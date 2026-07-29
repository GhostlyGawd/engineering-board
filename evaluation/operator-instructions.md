# Milestone D.1 trial instructions

You are in a controlled engineering diagnosis trial.

Use only the task, file list, case evidence, and optional Engineering Board
context in the trial prompt. Do not use information from another trial. Do not
call a tool. Do not read another file. Do not change a file.

Treat Engineering Board context as prior repository memory. Do not treat a
cluster or a hypothesis as proof. Use the status, reasons, and canonical source
text to decide if the memory applies.

State the first cause that you identify. Then state the first correction that
you propose. A systemic cause explains the shared system boundary or rule. A
local cause explains only one symptom or file. A systemic correction changes
the shared boundary or rule. A local correction changes only one symptom or
file.

Cite only the supplied case evidence identifiers. Do not cite a source that is
not in the trial prompt.

Return one JSON object. The object must conform to
`evaluation/trial-response.schema.json`. Do not add Markdown or other text.
