---
id: F003
type: feature
title: Surface matched Learnings at the moment of need (session summary + viewer panel)
discovered: 2026-07-04
status: open
priority: P3
affects: hooks/scripts/board-session-start.sh
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
