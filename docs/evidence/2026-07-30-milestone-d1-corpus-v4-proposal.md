# Milestone D.1 corpus version 4 proposal preflight

Date: 2026-07-30

State: `DRAFT — SOURCE OR DECISIONS INCOMPLETE`

Completion state: `self-contained`

This record is proposal and calibration evidence. It is not an evidence
baseline and does not support a product-effect claim.

## Outcome

The version 4 corpus proposal corrects the visible-information defect in
version 3. Each positive case now shows one current incident in one top-level
domain. Scoring-only data identifies the prior related incident. A positive
classification must connect the current incident to at least one prior
incident.

The proposal remains unlocked. The prepare command rejects it as input to a
scored run.

A non-scored preflight found a product-information defect. The frozen v1.11.0
context engine ranked each expected hypothesis within the first three results.
However, the returned result did not contain the hypothesis title, proposed
root cause, or a bounded evidence summary. None of the four context responses
identified the required cross-incident relationship.

Do not seal version 4 until the product owner approves a correction for this
context-information gap.

## Proposal identity

- Corpus identifier: `d1-product-effect`
- Corpus role: `proposal`
- Corpus version: `4`
- Lock state: unlocked
- Proposal date: 2026-07-30
- Final proposal content digest:
  `sha256:ccdebc8be431047341bb13920d04fdc9a901e34664da6c90ed53f38be14ef662`
- Digest scope: JSON contract, all canonical case-evidence files, and the
  complete context fixture
- Historical version 3 digest:
  `sha256:e8756040e5c6b9c1f9f40e7b47cc17cf196d59e605234fd0c67796a24da6b956`

The version 4 digest algorithm does not change the historical version 3
digest.

## Requirement state

The structured requirement checker reports
`DRAFT — SOURCE OR DECISIONS INCOMPLETE`.

- Structured requirement digest:
  `sha256:9315bfd6889b0e1cbab6e9e864d0ffaf94a20c59606755cfceeb8cbcbef64ed2`
- Deterministic requirement failures: zero
- Open product decisions: two
- Required human review dimensions: incomplete
- Baseline approval: absent
- Clean baseline release: not permitted

The product owner's approval to start the next D.1 proposal is source
authority for this work. It is not approval of the exact version 4 baseline.

## Non-scored preflight

The preflight used:

- Codex CLI 0.145.0
- Model `gpt-5.6-sol`
- Reasoning effort `medium`
- Frozen product source
  `e26149bf505ea7f5ae2d95294a8a108e6b3c429f`
- Four positive cases
- One baseline arm and one context arm for each case
- Eight isolated, ephemeral sessions
- Read-only workspaces
- No tools or file reads
- Zero infrastructure failures

The pilot prompt bundle has digest
`sha256:a5cd26472c900cfc1a35d7f868132a1b6c88c06fff03479f145338c29b74e186`.
The complete local pilot evidence is at
`/home/rhenm/scratch/engineering-board-d1-v4-pilot.b5DNga`.

The pilot ran before the final scoring-only classification fields and the
content-bound digest algorithm were added. Those changes did not change the
agent-visible task, file list, case evidence, or context payload.

## Bounded review

The version 4 rubric classifies a diagnosis as systemic-before-local only when
the first stated cause connects the current incident to at least one prior
incident. A broad rule inside only the current component is local for this
test.

Under this rubric:

- Baseline cross-incident rate: 0 of 4.
- Context cross-incident rate: 0 of 4.
- Expected-memory ranks: 1, 2, 2, and 1.
- Context retrieval failures: zero.

All four baseline responses generalized beyond the immediate symptom. None
identified the hidden prior incident. These responses show why “systemic”
must have a cross-incident scope in this product-effect test.

The context responses also did not identify the prior incident relationship.
The output gave each agent a relevant memory identifier, state, score, match
reason, and source paths. It did not give the agent the memory claim. One
response explicitly rejected the cross-client hypothesis because the supplied
case evidence showed only the editor-extension symptom.

This eight-arm preflight is calibration evidence. It does not use the accepted
three-repetition evidence contract. Do not compare its rates with the
75-percent context threshold or the 25-point improvement threshold.

## Product defect

`build_context` uses hypothesis titles, proposed root causes, and Learning
takeaways to calculate intent overlap. It removes those values before it
returns each result.

The result therefore explains why a memory ranked, but it does not explain
what the memory says. Corpus wording cannot correct missing product output.

The active recommendation is to add bounded, agent-usable memory content to
each context result. A hypothesis result should include its stable title and
proposed root cause. A Learning result should include its title and Takeaway.
A cluster result should include its normalized patterns and member scope.
Every result must preserve its epistemic state and canonical source
references.

A source-expansion workflow remains an alternative. That option would let an
agent open returned source references. It requires a different operator
contract and equal-tool controls.

The product owner has not selected either correction.

## Benchmark-integrity correction

The previous corpus digest covered only the JSON contract. A Markdown evidence
file or context-fixture file could change without changing that digest.

For version 4 and later, the validator now binds these inputs:

- the corpus JSON contract;
- each canonical case-evidence file;
- the complete context fixture.

A deterministic test changes one evidence file and one context file. Each
change produces a different digest. A separate assertion preserves the exact
historical version 3 digest.

## Alignment

| Contract item | Normative level | Implementation | Test | Docs/example | Status |
|---|---|---|---|---|---|
| Proposal isolation | Required | `proposal` role, proposal date, unlocked state, scored-run rejection | Version 4 proposal validation and preparation rejection | Evaluation guide and central spec | Pass |
| One current incident | Required | Version 4 information-boundary fields and one evidence file | Boundary mutation tests | Proposal corpus and central spec | Pass |
| Cross-incident classification | Required | Scoring contract requires two incidents and treats a current-only rule as local | Contract mutation test and bounded pilot review | Central spec and this evidence | Pass for proposal structure |
| Complete corpus identity | Required for version 4 and later | Composite digest covers JSON, evidence files, and fixture | Evidence mutation, fixture mutation, and version 3 preservation | Evaluation guide and central spec | Pass |
| Agent-usable memory content | Open product decision | v1.11.0 ranks memory but omits title and summary from returned results | Eight-arm non-scored preflight | Central spec and this evidence | Open; blocks baseline |
| Historical version 3 result | Historical | Locked version 3 files remain unchanged | Exact historical digest assertion | Existing dated evidence | Preserved |
| Runtime, plugin, MCP package, setup, security, privacy, visuals, version, and release | Reviewed and unaffected | Proposal tooling does not change shipped runtime or package surfaces | Existing repository suites | Current runtime documentation retains released claims | Unaffected |

## Drift classification

Required conflicts: none in the proposal implementation.
