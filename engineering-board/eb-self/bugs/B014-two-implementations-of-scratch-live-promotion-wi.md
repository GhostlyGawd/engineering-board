---
id: B014
type: bug
title: Two implementations of scratch->live promotion with no stated canonical engine
discovered: 2026-07-04
status: resolved
priority: P2
affects: agents/consolidator.md
needs: done
pattern: [duplication]
---

## Done when
- One engine is canonical (the shell script `board-consolidate.sh`); the consolidator agent and the board-consolidate skill are thin dispatchers over it, and each file states which is canonical.
- No path can double-write an entry.

## Observed behavior
`agents/consolidator.md` and `skills/board-consolidate/SKILL.md` both implement ~8-step promotion with identical AC-T2b supersession language; the skill names `board-consolidate.sh` as THE implementation while the agent hand-writes its own Step 6. `board-intake` is a third path writing richer frontmatter. A reader cannot tell which runs.
