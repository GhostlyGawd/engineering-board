> DRAFT — FULL COMPLIANCE CHECK NOT COMPLETE

# Rewrite validation

## Validation record

- Date: `2026-07-28`
- Source commit: `e47f49422aab5df6229bd4f5dcc2e23d186dea2d`
- Rewrite commit: `1c94fb3`
- Files in the ordered rewrite corpus: 49
- Lexical tokens in the output corpus: 57,418
- Applicable rule rows: 56
- Source corpus SHA-256:
  `3b34962e73e5675b31fbb19c5d4853cdfe054da08c538790081dbd70d729ab19`
- Output corpus SHA-256:
  `c3f52034a48faed0baf9b63c6117312a2eaec7dca89f867649e552d7e50c23ca`
- Review artifact SHA-256:
  `20edba728e8d277933d59a64f8622a74b6d8aecd74fcb2f1d3fb1b506d0b635e`

The authorized Issue 9 PDF has this SHA-256 value:

```text
d1f4ea9e7cd6e46b47aa9057209f99e78c0e9cfc4e27a5b07895b05c1a166431
```

The compliance checklist has this SHA-256 value:

```text
b59353dbb66914ba941285ef083dd36c49308e5fb0386b314e18302220134dd0
```

`CORPUS-MANIFEST.tsv` binds each source file to its source and output Git
blob. The fail-closed evidence run used the complete ordered text of these
files.

## Deterministic report

The report did not release the text. It returned:

```text
NOT RELEASED — TECHNICAL REVIEW REQUIRED
```

The following gates are open:

- all 56 rule rows require qualified review;
- all 57,418 token rows require qualified review;
- the project terminology entries require approval;
- technical facts and safety information require technical review;
- a trained ASD-STE100 reviewer must approve the exact artifact;
- an authorized technical reviewer must approve the same artifact;
- reviewer corrections and final checks are not complete.

The complete-text gate passed. This result means that the evidence contains
one token row for each token. It does not mean that a token or sentence is
approved.

The terminology checker confirmed complete token coverage. It returned
`FAIL` with 57,428 findings. The findings remain open because the token rows
and project terms do not have qualified approvals.

## Product validation

- The orchestration matrix passed 24 of 24 checks.
- The mode-routing suite passed 6 of 6 groups.
- JSON parsing passed for all unchanged release manifests.
- The HTML parser accepted `docs/index.html`.
- `git diff --check` passed.
- The full test suite passed 16 of 17 groups.
- The MCP bundle checksum group failed.

The documentation and agent instructions are part of the MCP bundle.
Therefore, the rewrite changes the bundle checksum. This branch does not
change the published v1.10.0 checksum. A later versioned release must build
the new bundle and record its checksum. The test rebuilt this SHA-256 value:

```text
1f8f6b9c204a699ce8faa4eef113772414e1d42a68acfb6cd43f4de5fdcbedc7
```

## Required reviewer actions

1. Approve or correct each entry in `PROJECT-TERMINOLOGY.yaml`.
2. Confirm the applicable company language requirements.
3. Give the exact evidence artifact to a trained ASD-STE100 reviewer.
4. Give the same artifact to an authorized technical reviewer.
5. Apply all required corrections.
6. Generate a new digest.
7. Obtain both approvals for the new digest.
8. Build and pin a versioned MCP bundle.
9. Run the full test suite again.

## Superseding branch change

The branch now adds the release policy, release skill, preparation script, and
release-preparation test. The review artifact above does not include this new
text. Therefore, its digest cannot approve the complete branch.

The release-preparation suite passed seven checks. A real-tree preview for
v1.10.1 identified all seven versioned files and produced a prospective MCP
bundle checksum. The preview did not write a file.

Regenerate the ordered corpus, token ledger, rule ledger, and review artifact
after the release workflow change is stable. Both human reviewers must approve
the superseding digest.

## Final status

`NOT RELEASED — COMPLIANCE CHECK INCOMPLETE`
