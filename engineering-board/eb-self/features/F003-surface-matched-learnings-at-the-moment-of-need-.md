---
id: F003
type: feature
title: Surface matched Learnings at the moment of need (session summary + viewer panel)
discovered: 2026-07-04
status: in_progress
priority: P3
affects: hooks/stop-hook-procedure.md
needs: tdd
pattern: [learnings-surfacing]
---

## Done when
- The session-end/PM summary lists any `L###` whose `applies_to`/`pattern` matches entries touched this session (reusing the SessionStart affects-prefix/confidence filter).
- The F001 viewer renders a Learnings panel from `learnings/`.

## Motivation
Rank-3 (Track C). Learnings (the moat) reach the user through exactly one surface today: the SessionStart dump (top-3, medium+ confidence, cwd-filtered, recurrence>=3). At the moment memory pays off (PR review, session end) the relevant learning is invisible. The gap is distribution, cheaper than net-new capability. Sequence after F001 (viewer parses learnings/ for free).

## Kill criteria
Kill if matching produces false positives that train users to ignore it (guard with the proven medium+ confidence + affects-prefix filter). Defer PR-body injection until there is an owned PR-authoring surface (Conductor).

## Comments

- **codex-20260814-f003-learning-surface** 2026-08-14T18:05:12Z: TDD implementation started. Viewer Learnings panel is already covered; scope is the PM summary plus shared-context matching for Learning applies_to and medium/high confidence.
- **codex-20260814-f003-learning-surface** 2026-08-14T18:24:50Z: Implementation verified: context 16 checks, PM loop 20 checks, Stop routing 102 checks, viewer 52 checks, and maintained suite 21/21. Real-board B069 surfaced L003/L005 while F003 stayed quiet. Documentation and dated evidence are aligned; preparing delivery.
