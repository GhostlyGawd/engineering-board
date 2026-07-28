> DRAFT — FULL COMPLIANCE CHECK NOT COMPLETE

# Rewrite validation

## Validation record

- Date: `2026-07-28`
- Source commit: `e47f49422aab5df6229bd4f5dcc2e23d186dea2d`
- Rewrite commit: `1c94fb3`
- Release-preparation base commit: `f2218c4`
- Prepared version: `1.10.1`
- Files in the ordered rewrite corpus: 52
- Lexical tokens in the output corpus: 58,541
- Applicable rule rows: 56
- Source corpus SHA-256:
  `c76109b5a818f0048545e7acbd8b9e28a429a0779a179d1a8ece5b45eb7acca6`
- Output corpus SHA-256:
  `47fee278068fd9f0b162260534564cbdfc71ac2239759c6c3371ebe71417aba3`
- Review artifact SHA-256:
  `4295067c8941bcaf197e9bcefa284a7fc833855ff1a7fc349fe40682d52ad998`

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
- all 58,541 token rows require qualified review;
- the project terminology entries require approval;
- technical facts and safety information require technical review;
- a trained ASD-STE100 reviewer must approve the exact artifact;
- an authorized technical reviewer must approve the same artifact;
- reviewer corrections and final checks are not complete.

The complete-text gate passed. This result means that the evidence contains
one token row for each token. It does not mean that a token or sentence is
approved.

The terminology checker confirmed complete token coverage. It returned
`FAIL` with 58,551 findings. The findings remain open because the token rows
and project terms do not have qualified approvals.

## Product validation

- The orchestration matrix passed 24 of 24 checks.
- The mode-routing suite passed 6 of 6 groups.
- JSON parsing passed for all prepared release manifests.
- The HTML parser accepted `docs/index.html`.
- `git diff --check` passed.
- The full test suite passed 17 of 17 groups.
- Version coherence passed for v1.10.1.
- The pinned MCP bundle checksum reproduced.

The prepared MCP bundle has this SHA-256 value:

```text
aee407a0b239e55733eafff2d4b3d18ba4eff78c0cd86f42d64e594801ac932b
```

## Required reviewer actions

1. Approve or correct each entry in `PROJECT-TERMINOLOGY.yaml`.
2. Confirm the applicable company language requirements.
3. Give the exact evidence artifact to a trained ASD-STE100 reviewer.
4. Give the same artifact to an authorized technical reviewer.
5. Apply all required corrections.
6. Generate a new digest.
7. Obtain both approvals for the new digest.
8. Run the full test suite after each correction.

## Current review bundle

The current review bundle includes the release policy, root agent
instructions, maintainer release skill, and v1.10.1 README text. The corpus
manifest records the source and output blob for each included file. The
complete-text gate passed. The authorization record is bound to the verified
Issue 9 PDF. Language, terminology, safety, and technical review gates remain
open.

The release-preparation test initially used a fixed v1.10.1 target. The
prepared repository exposed this lifecycle defect. The revised test derives
the next patch version from the current manifest and adds a disposable release
note to its test copy. The release-preparation suite now passes after a release
version is prepared.

The board-view test used `pipefail` with `grep -q`. A successful early match
could close the pipeline and report the writer's SIGPIPE as a failure. The
test no longer uses `pipefail`. The content assertions are unchanged.

## Final status

`NOT RELEASED — COMPLIANCE CHECK INCOMPLETE`
