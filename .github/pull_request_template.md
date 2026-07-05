<!--
Thanks for the PR. Keep each section short. Delete a section only if it truly
does not apply, and say why.
-->

## Summary

<!-- What this changes and why, in a few sentences. -->

## Board entry / finding

<!--
This repo runs its own board at engineering-board/eb-self/. Which entry or
finding does this resolve? e.g. eb-self B0XX / F0XX, or a GitHub issue number.
-->

## Test evidence

- [ ] `bash tests/run-all.sh` is green
- [ ] New behavior ships with new tests, or changed behavior ships with changed tests
- [ ] Any new/edited `hooks/scripts/*.sh` passes `tests/crosscompat-lint.sh`

<!-- Paste the relevant suite output or note the new suite count. -->

## Version bump (if user-facing)

- [ ] `.claude-plugin/plugin.json` bumped
- [ ] `.claude-plugin/marketplace.json` bumped in lockstep
- [ ] `CHANGELOG.md` updated under `[Unreleased]`
- [ ] Not user-facing — no bump needed

## Surface coherence

- [ ] README / ARCHITECTURE / docs still match the behavior (counts, commands, prose)
- [ ] Pinned framing strings and stop-hook tokens preserved where touched
