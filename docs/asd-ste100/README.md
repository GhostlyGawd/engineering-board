> DRAFT — FULL COMPLIANCE CHECK NOT COMPLETE

# ASD-STE100 rewrite status

This directory contains the evidence for the Engineering Board rewrite.

The rewrite uses ASD-STE100 Issue 9 as its language standard. The local
authorized PDF has this SHA-256 value:

```text
d1f4ea9e7cd6e46b47aa9057209f99e78c0e9cfc4e27a5b07895b05c1a166431
```

The task mode is `rewrite`. The output mode is `report`.

The intended readers are:

- software developers;
- engineering agents;
- repository maintainers;
- security reviewers.

The technical domain is software engineering for agent systems.

The content types are:

- descriptive information;
- procedures;
- safety information.

## Release status

`NOT RELEASED — COMPLIANCE CHECK INCOMPLETE`

The following gates are open:

1. The project terminology file does not have an authorized approval.
2. The complete word ledger does not have a qualified review.
3. The complete rule ledger does not have a qualified review.
4. A trained ASD-STE100 reviewer did not approve the final artifact digest.
5. An authorized technical reviewer did not approve the final artifact digest.

Automated checks do not close these gates.

## Source authority

The current repository at the source commit is the approved technical source.
The product owner controls product direction through
`docs/PRODUCT_EVOLUTION_SPEC.md`.

The rewrite must preserve:

- commands and identifiers;
- paths and file names;
- versions and digests;
- requirements and permissions;
- security boundaries;
- state names and transition rules;
- historical dates and observations;
- mandatory and optional meanings.

## Evidence files

- `SCOPE.md` defines the files and the exclusions.
- `PROJECT-TERMINOLOGY.yaml` is the project terminology register.
- `WORKPAD.md` contains the one alignment table for this task.
- `CORPUS-MANIFEST.tsv` binds each source file to its output file.
- `VALIDATION.md` records the deterministic report and the open gates.

Do not use the clean-output mode while a release gate is open.
