# Release Engineering Board

This document defines the current release policy for Engineering Board.

Repository agents must also read
[`maintainers/skills/release-engineering-board/SKILL.md`](../maintainers/skills/release-engineering-board/SKILL.md).
The maintainer skill is not part of the installed plugin.

## Release policy

Keep `main` releasable. Do not publish an immutable release for every merge.

Use these boundaries:

- Add each user-visible change to `[Unreleased]` in `CHANGELOG.md`.
- Prepare all versioned files in one release change.
- Publish only an explicit Semantic Versioning release.
- Publish only a commit that is on `main`.
- Keep GitHub, PyPI, the MCP Registry, and the MCP bundle aligned.
- Add dated evidence after publication.

PyPI versions, MCP Registry versions, release tags, and release assets are
immutable. An explicit release boundary prevents an accidental publication
from an incomplete `main` commit.

## Select the version

Use Semantic Versioning:

- Use a patch version for a compatible correction.
- Use a minor version for a compatible feature.
- Use a major version for a breaking change.

The target version must be greater than the current version.

## Prepare the release

First, commit all product changes and release notes. The worktree must be
clean.

Preview the release:

```bash
python3 scripts/prepare-release.py <version>
```

The preview does not write a file. It shows:

- the current version;
- the target version;
- the release date;
- each file that will change;
- the prospective MCP bundle SHA-256 value.

Apply the release:

```bash
python3 scripts/prepare-release.py <version> --apply
```

The script updates:

- `.claude-plugin/plugin.json`;
- `.claude-plugin/marketplace.json`;
- `mcp-server/manifest.json`;
- `mcp-server/server.json`;
- `mcp-server/pyproject.toml`;
- the README version badge;
- `CHANGELOG.md`;
- the MCP bundle checksum and release URL.

Then, run:

```bash
bash tests/run-all.sh
```

Commit and push the prepared release. Merge it through the normal review
process.

If approved review changes modify the bundle after version preparation,
preview a refresh:

```bash
python3 scripts/prepare-release.py <version> --refresh
```

Apply the refresh only when `<version>` is the current prepared version:

```bash
python3 scripts/prepare-release.py <version> --refresh --apply
```

Refresh does not create another changelog section. The default command
continues to refuse the current version.

## Publish the release

Run `.github/workflows/release.yml` after the release-preparation commit is on
`main`.

Supply:

- `v<version>` as the tag;
- the exact `main` commit SHA;
- the required registry-publication options.

The workflow:

1. Verifies that the commit is on `main`.
2. Creates or reuses the immutable tag.
3. Verifies the manifest version.
4. Extracts the version section from `CHANGELOG.md`.
5. Rebuilds the MCP bundle.
6. Verifies the pinned checksum.
7. Creates the GitHub Release.
8. Publishes to selected registries.

## Record release evidence

After publication, add:

```text
docs/evidence/YYYY-MM-DD-v<version>-release-validation.md
```

Record:

- the release commit and tag target;
- the bundle name, size, and checksum;
- CI and release workflow results;
- the GitHub Release state;
- the PyPI state, if applicable;
- the MCP Registry state, if applicable;
- the product-site state;
- documentation alignment;
- reviewed and unaffected product boundaries.

Do not modify an earlier release record. Add a superseding dated record when
an observation changes.

## Language status

The owner approved the current controlled-English text. Formal ASD-STE100
verification is not a product-release requirement.
