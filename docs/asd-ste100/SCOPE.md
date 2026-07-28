> DRAFT — FULL COMPLIANCE CHECK NOT COMPLETE

# Rewrite scope

## Included content

The rewrite includes current project text in these surfaces:

- the root product documentation;
- the command documentation;
- the agent instructions;
- the skill instructions and schema references;
- the current architecture and security documentation;
- the current product specification;
- the MCP user documentation and descriptions;
- the landing page and the LLM index;
- the current test instructions for a human operator;
- current help text and user-visible messages in executable files.

The first active-instruction batch includes:

- `ARCHITECTURE.md`;
- `BRAND.md`;
- `CLAUDE.md`;
- `.github/pull_request_template.md`;
- all Markdown files in `agents/`;
- all Markdown files in `commands/`;
- `hooks/stop-hook-procedure.md`;
- `mcp-server/README.md`;
- `references/active-workers-registry.md`;
- `references/auto-resolve-pass.md`;
- all Markdown files in `skills/`;
- `tests/smoke/manual-checks.md`;
- `docs/PRODUCT_EVOLUTION_SPEC.md`;
- `docs/llms.txt`.

## Protected content

The rewrite can change sentence construction. It must not change technical
meaning.

The following items are protected:

- command names;
- tool names;
- file paths;
- code and shell examples;
- JSON, YAML, and Markdown field names;
- state names;
- entry, pattern, and hypothesis identifiers;
- version numbers;
- commit identifiers;
- checksums;
- dates;
- URLs;
- permission rules;
- test expectations;
- quoted external text.

## Content that the rewrite does not change

The rewrite does not change these files:

- `LICENSE`;
- `CODE_OF_CONDUCT.md`;
- historical changelog entries;
- dated evidence records;
- canonical board entries and learnings;
- adversarial and benign test fixtures;
- generated board HTML;
- machine data that has no user instructions.

The rewrite also preserves these historical design and planning records:

- `ACTIVATION.md`;
- `BRAND-COHERENCE.md`;
- `COLOR.md`;
- `COMPREHENSION.md`;
- `CRO.md`;
- `HIERARCHY.md`;
- `IMPROVEMENTS.md`;
- `LAYOUT.md`;
- `NEXT-PHASE.md`;
- `PROOF.md`;
- `RETENTION.md`;
- `ROADMAP.md`;
- `SHOWCASE.md`;
- `STATES.md`;
- `TYPOGRAPHY.md`;
- `specs/`;
- `docs/evidence/`;
- `docs/research/`;
- `docs/rfcs/`.

These files are source records, legal text, test inputs, or generated output.
A prose rewrite can invalidate their authority or their test purpose.

The rewrite can add a superseding evidence record. It must not rewrite a dated
observation as current truth.
