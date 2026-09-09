# Synthetic workflow-value pilot fixtures

These four small Python standard-library maintenance tasks are authored synthetic
fixtures. They are not customer incidents, real held-out evidence, or an estimate
of real-world effect. They are fresh tasks, not B062, B069, or C04 retellings.

Each taskrepo is a standalone visible repository. Its AGENTS.md is identical
across all cases and all comparison conditions. Public tests intentionally expose
a reported failure. Only taskrepo belongs inside a candidate's working repository.
History/board are alternate representations of the same prior factual content.
Neither representation establishes a new current-task diagnosis as confirmed.

The useful Learning supplies a procedure for sibling consumers and option
contracts; the control Learning concerns currency display and explicitly scopes
its procedure away from the current sensor ingestion repair. The useful proposed
hypothesis suggests a discriminating sequence-mutation check. The wrong shared
hypothesis is refutable by independent CSV and lookup experiments.

Run public tests inside taskrepo:
`python3 -m unittest discover -s tests -v`.

Run a hidden evaluator outside the candidate repository:
`python3 cases/<id>/evaluator.py --repo /absolute/candidate/repository`.
It copies only the declared implementation into a fresh temporary directory,
loads it there, and emits JSON with passed/total plus per-check evidence. It never
executes a candidate helper or accepts an evaluator command from candidate files.
This temporary-directory isolation is not an OS security sandbox. The runner must
provide any required process permissions and deadline. Graders are independent
of candidate regression tests and have no network/dependency requirements.

The reference directories contain one correct repair per task, outside visible
repositories and history. They demonstrate satisfiability, not a required patch
shape. Evaluation may accept any implementation satisfying the public contract.

Run `python3 evaluation/workflow-pilot/cases/validate.py` from the repository
root to verify baseline failures, reference repairs, harmful mutations, history
parity, and real Board retrieval. The validator initializes isolated temporary
boards and calls the repository MCP server's actual `tools/call` dispatcher for
`board_init`, `board_rebuild`, and `board_context`. It requires the expected
Learning or proposed hypothesis to be returned without an error or stale flag.
Use `--server-module /path/to/installed/mcp-server/engineering_board_mcp.py`
to repeat the same validation against an installed release. This check runs
offline without model calls or access to product boards.

Canonical hypothesis claim fingerprints are derived from the actual claim key
and pattern ids. Cluster and graph fingerprints refer to the source fixture
graph, not invented placeholders. Schema parsing and retrieval are both tested;
Markdown-body parity by itself is insufficient to establish valid retrieval.

The cases.json expected_actions fields, hidden evaluators, reference repairs, and
this README are evaluator metadata: do not include them in agent prompts or
candidate repositories. Automated checks score repair correctness, sibling
behavior, and negative-scope regressions. Investigation and authored regression
coverage require review of retained tool traces and patches; they must not be
inferred from a passing hidden grader or final root-cause wording.

Baseline expected hidden passes: retries 2/4; precision 1/4; catalog 0/4;
identifiers 1/4. Every baseline public suite fails; every reference repair passes
its unchanged public suite and all 4 hidden checks.
