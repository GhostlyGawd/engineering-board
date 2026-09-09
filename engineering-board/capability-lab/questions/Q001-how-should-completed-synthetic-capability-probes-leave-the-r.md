---
id: Q001
type: question
status: resolved
title: How should completed synthetic capability probes leave the ready queue?
affects: tests/capability_lab/
discovered: 2026-09-09
discovered_at: 2026-09-09T03:03:34Z
promoted_from: [mcp:_sessions/mcp-2026-09-09.md:de82fd712ba9169e]
---

# How should completed synthetic capability probes leave the ready queue?

## Done when

- [ ] Define and verify the completion criterion.

## Evidence

> B001-B003 are still ready P2 bugs after the capability sweep completed, but their affected files do not exist. H001 says no real product behavior or fix was asserted, and L001 says synthetic evidence must remain isolated to this routed board.

## Comments

- **codex-capability-q001-20260908** 2026-09-09T03:07:06Z: Claimed after owner approval. Determine the terminal disposition for completed synthetic probe records, update dependents, and remove unsupported synthetic causation from active hypothesis memory.
- **codex-capability-q001-20260908** 2026-09-09T03:07:28Z: Resolved with the approved finding: completed synthetic probes receive an explicit non-product terminal disposition and never create fake implementation work.

## Finding

Completed synthetic capability probes must leave the ready queue through an explicit terminal disposition after the probe finishes. They must not remain actionable bugs, and no implementation should be created solely to make synthetic evidence true. A synthetic record may remain open only when it names a real fixture and a still-pending verification criterion; otherwise resolve it as a non-product test artifact and preserve that limitation in its evidence.

For B001-B003, every named `tests/capability_lab/*.py` path is absent, O001 records that the live capability sweep completed, H001 states that no real product behavior was asserted, and L001 requires synthetic evidence to remain isolated. Their marker-preservation criteria therefore describe invented fixtures rather than unfinished product work and are superseded by this disposition. H001's shared-boundary explanation has no observable implementation or trace to support it and should be rejected, not treated as a product root cause.
