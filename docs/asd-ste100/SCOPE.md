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

These files are source records, legal text, test inputs, or generated output.
A prose rewrite can invalidate their authority or their test purpose.

The rewrite can add a superseding evidence record. It must not rewrite a dated
observation as current truth.
