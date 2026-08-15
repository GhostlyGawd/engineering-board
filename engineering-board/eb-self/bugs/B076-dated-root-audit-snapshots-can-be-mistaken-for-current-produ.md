---
id: B076
type: bug
status: in_progress
needs: validate
priority: P2
title: Dated root audit snapshots can be mistaken for current product truth
affects: COMPREHENSION.md
discovered: 2026-08-15
discovered_at: 2026-08-15T03:54:52Z
promoted_from: [mcp:_sessions/mcp-2026-08-15.md:183b41979669e676]
---

# Dated root audit snapshots can be mistaken for current product truth

## Done when

- [ ] `COMPREHENSION.md`, `RETENTION.md`, and `PROOF.md` identify themselves as historical snapshots immediately after the title.
- [ ] Each banner points to the current normative product, architecture, security, and release surfaces.
- [ ] The historical text remains unchanged below the banner, including superseded claims and observations.
- [ ] Documentation coherence and semantic review pass.

## Evidence

> COMPREHENSION.md, RETENTION.md, and PROOF.md are dated 2026-07-08 but have no explicit supersession boundary. They retain obsolete versions, counts, and claims such as permanent claims and session mode or literal metrics error blobs.

## Comments

- **goal-hooks-20260815** 2026-08-15T03:58:52Z: Claimed after semantic review confirmed that dated audit snapshots lacked an explicit historical and supersession boundary.
- **goal-hooks-20260815** 2026-08-15T04:05:39Z: Focused checks and the settled complete suite pass. Advanced from TDD to independent review; merged-main and installed-artifact gates remain open.
- **goal-hooks-20260815** 2026-08-15T04:07:31Z: Independent read-only review found no remaining release blocker after patch and minor release-path coverage. Advanced to validation; installed and merged-main gates remain open.
