---
name: release-engineering-board
description: Prepare, verify, publish, and close an Engineering Board maintainer release. Use for repository maintenance when the owner asks to bump the product version, prepare a release, rebuild or pin the MCP bundle, update the changelog, create a release tag, publish to GitHub, PyPI, or the MCP Registry, or verify release alignment.
---


# Release Engineering Board

Use this skill only in the `GhostlyGawd/engineering-board` source repository.
Do not use it in a repository that only installs the Engineering Board plugin.

Use the repository script for release preparation. Do not update release files
independently.

## Prepare the release

1. Read `docs/RELEASING.md`.
2. Confirm that the release branch is clean.
3. Confirm that the Codex manifest, Claude manifest, marketplace, Python
   package, MCP manifests, and README badge have the current version.
4. Select the next Semantic Versioning value from the `[Unreleased]` changes.
5. Preview the coordinated change:

   ```bash
   python3 scripts/prepare-release.py <version>
   ```

6. Review every listed file and the prospective MCP bundle checksum.
7. Apply the same plan:

   ```bash
   python3 scripts/prepare-release.py <version> --apply
   ```

8. Run the complete test suite:

   ```bash
   bash tests/run-all.sh
   ```

9. Commit and push the release-preparation change.

If approved review changes modify the prepared bundle, use `--refresh` with
the current prepared version. Preview the refresh before you apply it. Refresh
must not create another changelog section. Do not use refresh to change the
target version.

## Publish the release

Publish only from a commit on `main`. Do not move an existing tag.

Use `.github/workflows/release.yml` with:

- the exact `v<version>` tag;
- the exact `main` commit;
- MCP Registry publication when the release must update that registry;
- PyPI publication when the release must update that package.

The publication workflow owns the tag, GitHub Release, release asset, MCP
Registry publication, and PyPI publication. Do not duplicate these operations
manually.

## Close the release

After publication:

1. Verify the GitHub Release, tag target, asset checksum, MCP Registry version,
   PyPI version, CI, and product site.
2. Add a dated release-validation file in `docs/evidence/`.
3. Preserve earlier evidence files.
4. Commit the closeout evidence through a separate pull request.

## Stop conditions

Stop the release if:

- `[Unreleased]` has no release note;
- the target version is not greater than the current version;
- a versioned surface does not align;
- the MCP bundle checksum does not reproduce;
- a test fails;
- the target commit is not on `main`;
- a required publication does not complete.

The owner approved the current controlled-English text. Do not claim formal
ASD-STE100 compliance without a separate qualified verification.
