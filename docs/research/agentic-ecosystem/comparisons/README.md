# Sibling-plugin comparison maps

Visual comparison of **engineering-board** against its two sibling Claude Code
plugins by the same author (GhostlyGawd / rhenmcleod) — produced 2026-06-08 to
find the shared patterns and the real points of divergence across the three.

> These compare **sibling projects**, not engineering-board internals. The most
> load-bearing finding for *this* repo: the autonomous, parallel, headless
> worker-in-worktree orchestrator that **Conductor RFC 0001** (target 1.2.0) is
> still drafting has **already shipped twice** next door — and both siblings bet
> **headless**, the exact model RFC 0001 deliberately rejects in favor of
> observable, attachable sessions. Treat `agentic-engineering-max` and
> `agentic-engineering` as prior art when building the Conductor.

## The three projects (as profiled, 2026-06-08)

| | what it is | lang | state substrate | version |
|---|---|---|---|---|
| **engineering-board** (this repo) | triage / work-capture control plane | bash + python3 | markdown board | 1.1.0 |
| **agentic-engineering-max** (AEM) | build factory + web HUD (plan→build→review) | PowerShell / pwsh 7 | markdown tasks + web HUD | 2.4.0 |
| **agentic-engineering** (AE) | self-improving verification engine | Python + MCP | SQLite typed graph via an MCP server | 0.1.0 |

## The maps

1. **`01-genealogy`** — family tree: shared "Superpowers" lineage → shared design
   instincts → three diverging identities (incl. the 8-stance epistemic panel
   shared by AEM and AE).
2. **`02-positioning`** — 2×2 map: *reactive/triage ↔ directed/build* crossed with
   *legible markdown ↔ typed DB*. Shows the cluster and the empty quadrant.
3. **`03-substrate`** — architecture stacks: the five layers (state / access /
   review / orchestration / interface) side by side. *"Files ARE the database"*
   vs *"files + a dashboard"* vs *"a real database behind a server."*
4. **`04-lifecycle`** — swimlanes: where falsifiability is enforced in each
   pipeline (★), the orchestration locus, and the worker model — with the
   headless-built-twice / EB-going-observable pattern called out.
5. **`05-capability-matrix`** — 10 dimensions × 3 projects + a "shared pattern"
   column (● shipped / ◐ partial / ○ absent-planned).

Each map ships as both `.svg` (editable source, ~9–18 KB) and `.png` (rendered
at 2000 px wide). To re-render an edited SVG with the same toolchain:

```sh
npm install @resvg/resvg-js
node -e "const{Resvg}=require('@resvg/resvg-js'),fs=require('fs');\
fs.writeFileSync('out.png',new Resvg(fs.readFileSync('in.svg','utf8'),\
{background:'white',fitTo:{mode:'width',value:2000},font:{loadSystemFonts:true}}).render().asPng())"
```

## Caveats

- **AEM was read via its *public* `agentic-engineering-max` repo**, which is a
  leak-gated `git subtree split` of the private `Dev_006` dev repo — so the
  bleeding edge in `Dev_006` may be ahead of what's mapped here. `agentic-engineering`
  is fully public (and dogfoods itself), so that profile is the real thing.
- Profiles are a **point-in-time snapshot** (2026-06-08); versions/phases move.
- Two source READMEs slightly undercount themselves (AE says "14 tables / 25
  tools"; source has 16 entity-shape tables and 26 MCP tools) — the maps use the
  source-verified numbers.
