---
id: B052
type: bug
title: consolidate promotion writer flattens only evidence_quote, not title/affects/tags
discovered: 2026-07-04
status: resolved
priority: P3
affects: hooks/scripts/board-consolidate.sh
needs: tdd
pattern: [frontmatter-injection]
---

## Done when
- Every promoted field (title, affects, tags, discovered, evidence) is flattened to a single line before it's written into frontmatter/body, so a newline/CR cannot close the frontmatter early or inject a body header. A regression test drives the real consolidate writer.

## Observed behavior (C7 red-team Track A — P3; same class as B028 in a different writer)
board-consolidate.sh Stage-4 wrote title/affects/discovered/tags RAW; only evidence_quote was flattened (and only `\n`→space). A crafted title with a newline could terminate the `---` fence early and inject arbitrary markdown into the promoted entry. Bounded to non-imperative body injection via `\n` alone — but B051's CR lifted that bound. The MCP-only `_oneline` fix (B028/B040) never covered this second writer.

## Resolution (C7, PR C7a)
Added a `flatten()` helper (mirrors MCP `_oneline`; `" ".join(str(v).split())` collapses all whitespace/control incl CR/LF/tab/VT/FF/FS-GS-RS) applied to title/affects/tags/discovered/evidence. New isolated smoke regression (B052) drives the real writer with a newline-injection title and asserts exactly one frontmatter block + one body header.
