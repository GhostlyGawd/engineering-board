# Controlled-English rewrite record

This directory contains the evidence for the Engineering Board rewrite.

The rewrite used ASD-STE100 Issue 9 as its language reference. The local
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

## Owner decision

`OWNER APPROVED — FORMAL ASD-STE100 COMPLIANCE NOT CLAIMED`

The owner reviewed and approved the current controlled-English text on
2026-07-28. The owner waived the two-reviewer process as a product-release
condition.

The project does not claim formal ASD-STE100 compliance, certification, or
independent review. A future formal compliance claim still requires:

1. The project terminology file does not have an authorized approval.
2. The complete word ledger does not have a qualified review.
3. The complete rule ledger does not have a qualified review.
4. A trained ASD-STE100 reviewer did not approve the final artifact digest.
5. An authorized technical reviewer did not approve the final artifact digest.

These items are formal-verification gaps. They do not block the owner-approved
product release.

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
- `CORPUS-MANIFEST.tsv` preserves the pre-approval formal-review snapshot.
- `VALIDATION.md` records the deterministic report and the owner decision.
- `../evidence/2026-07-28-controlled-english-owner-approval.md` records the
  superseding product-release decision.
