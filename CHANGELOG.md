# Changelog

All notable changes to **engineering-board** are documented here. The format is
based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this
project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).
Plugin and marketplace manifests are versioned in lockstep (enforced by
`tests/version-coherence.sh`); a fix only reaches installs when the version
increases.

## [Unreleased]

### Fixed
- **The viewer's "blocked" badge is readable in dark mode** (IMPROVEMENTS #2).
  `.badge.blocked` hardcoded `#B23A2E`, which measures **2.96:1** on the dark
  background (needs 4.5:1). The color is now the new `--eb-danger` token —
  `#B23A2E` on light (5.63:1), `#E4685A` on dark (5.38:1) — defined in
  `brand/tokens.css` alongside a new `--eb-card`, so the viewer stops minting
  colors the brand doesn't own. Two new `tests/view/` assertions;
  `eb-self/board.html` regenerated.
- **SessionStart banner readability** (IMPROVEMENTS #6). The scratch-entries
  wall-of-text is now a one-line headline with details indented beneath; the
  empty board state says what happens next instead of bare `(none)`; a one-line
  legend explains the `B/F/Q/O` sigils and priority codes on first sight; and the
  closing routing line reads as status rather than an internal directive.
- **Every user-visible sentinel now carries a plain-language companion**
  (IMPROVEMENTS #1). The Stop procedure pairs `<<EB-PASSIVE-DONE>>` with
  "Nothing captured this turn." when zero findings landed, `<<EB-PASSIVE-PAUSED>>`
  with "Board capture is paused — run /board-resume to restore.",
  `<<EB-WORKER-NOTHING-TO-DO>>` with a worker-idle line naming the next action,
  and `<<EB-PM-CONTINUE>>` with a one-line PM-pass summary (promoted counts,
  "0 promoted" said plainly). Sentinels stay byte-exact (the loop guard greps
  them); six new modes-suite pins cover the companions.
- **Silent failures now announce themselves** (IMPROVEMENTS #11, eb-self
  B008/B009). A *corrupt* `session-mode.json` still fail-opens to passive (safe
  routing) but now emits a warning naming the recovery — in both the Stop
  procedure and the SessionStart banner (an absent file stays quiet; two new
  session-start assertions). `board-consolidate.sh` preflights `python3` and
  exits loudly with a named remedy instead of silently losing the turn's
  promotions (new smoke assertion).
- **Stale-claim reclamation is visible** (IMPROVEMENTS #5). When the worker path
  reclaims a stale claim (`rm -rf` of another session's lock), the turn output
  now includes "Reclaimed a stale claim on <id> … (details: _claims/_reclaimed.log)"
  — the product's only destructive automatic action is no longer invisible.
- **`/board-migrate` dead-end names the next action**: the "no board layout
  found" message now points fresh starts at `/board-init` (matching the
  `/board-claim-release` microcopy gold standard).

### Added
- **The live public board** (IMPROVEMENTS.md #3). `pages.yml` now publishes the
  committed `engineering-board/eb-self/board.html` to the site as
  [`/board.html`](https://ghostlygawd.github.io/engineering-board/board.html) —
  the product's own roadmap, rendered by its own `/board-view`, republished on
  every merge to `main`. The README hero and Community section link it (replacing
  the "open it locally to render" apology).
- **One-click release workflow** — [`.github/workflows/release.yml`](.github/workflows/release.yml)
  (workflow_dispatch, or any `v*` tag push) automates the whole release chain the
  sandbox cannot perform itself: create the annotated tag at a given main sha
  (never moving an existing tag), verify the tag matches `plugin.json` at that
  tree, extract that version's CHANGELOG section as the release notes, build the
  reproducible `.mcpb` bundle and refuse to publish on a sha mismatch with the
  `server.json` pin, publish the GitHub Release with the asset, and — opt-in —
  publish to the official MCP Registry via GitHub OIDC (no stored secret).
  Exact dispatch inputs for v1.3.0 / v1.4.0 live in `.goal/LAUNCH.md` §3.

### Changed
- **The `.mcpb` bundle is now byte-reproducible** (launch prep). `build-mcpb.sh`
  zips via python3 `zipfile` with fixed timestamps + permissions (no `zip` CLI
  dependency), so the same input tree always yields the same sha256. That sha is
  now **pinned** in `mcp-server/server.json` (`packages[0].fileSha256`) and a new
  MCP-suite check (99 checks) rebuilds the bundle and fails if the pin drifts —
  removing the manual "compute + paste the sha" step from the MCP-Registry publish
  flow. `.goal/LAUNCH.md` §4 updated accordingly.

## [1.4.0] — 2026-07-05

Productization roadmap release (Levers 2–5 from `docs/rfcs/0003`): MCP distribution
artifacts, first-run retention UX, community scaffolding, and learnings surfacing.

### Added
- **Productization roadmap** — [`docs/rfcs/0003-productization-roadmap.md`](docs/rfcs/0003-productization-roadmap.md)
  records the ranked, dependency-ordered plan (release → distribution → retention
  UX → community → learnings surfacing) with a decided-"no" on premature paywalls,
  so the post-launch work is deliberate.
- **Learnings panel in `/board-view`** (roadmap Lever 5, eb-self F003, partial). The
  zero-dependency HTML board viewer now renders `learnings/` in a dedicated
  "Learnings · durable memory" panel — confidence + recurrence + `applies_to`
  surfaced — instead of burying them in the shared Questions/Observations lane. The
  moat (durable cross-session memory) is now visible in the best demo artifact,
  agreeing with the existing SessionStart surfacing. Five new `tests/view/`
  assertions. The session-end PM-summary surface is deferred and PR-body injection
  stays kill-gated to the Conductor (per F003's own kill criteria).
- **Community & contributor scaffolding** (roadmap Lever 4). `CONTRIBUTING.md`
  (the no-install `bash`+`python3` suite as the merge gate, crosscompat rules,
  version-lockstep, where things live), `SECURITY.md` (private reporting + a
  security posture that documents the untrusted-data model, the injection corpus,
  the accepted-residual boundary, and the severity rubric), `CODE_OF_CONDUCT.md`
  (Contributor Covenant 2.1), `.github/` issue forms (bug / feature, mirroring the
  RFC discipline), a PR template, `config.yml` (security + Discussions contact
  links), and `FUNDING.yml` (GitHub Sponsors). The README gains a "Community &
  support" section; the product's own `engineering-board/eb-self/` board is named
  as the public roadmap.
- **MCP distribution artifacts** (roadmap Lever 2). Three publish-ready, version-locked
  configs for the MCP server: [`mcp-server/server.json`](mcp-server/server.json) (official
  MCP Registry manifest, namespace `io.github.ghostlygawd/engineering-board`),
  [`mcp-server/manifest.json`](mcp-server/manifest.json) + [`mcp-server/build-mcpb.sh`](mcp-server/build-mcpb.sh)
  (a `.mcpb` bundle that packages the server with the hook scripts it shells out to),
  and [`mcp-server/smithery.yaml`](mcp-server/smithery.yaml) (Smithery stdio launch). All
  three are validated against `plugin.json` by the MCP test suite (98 checks) so they cannot
  drift, and `.goal/LAUNCH.md` §4 now carries the exact `mcp-publisher` / `smithery` publish
  commands. The build output (`dist/`) is a release asset, gitignored.

### Fixed
- **First captured finding is now visible on the turn** (roadmap Lever 3, eb-self B005).
  Passive capture wrote silently to `_sessions/` and only surfaced as a count at the
  *next* SessionStart, so a first-time user saw "nothing happened".
  `board-scratch-append.sh` now prints a plain-language `EB-CAPTURE-SUMMARY:` line
  (`captured N finding(s): …  — run /pm-start to promote`) and the Stop-hook passive
  path (step (e)) surfaces it before `<<EB-PASSIVE-DONE>>`. Titles are flattened +
  length-bounded (untrusted). One new `tests/scratch/` assertion.
- **Validation no longer dead-ends invisibly** (roadmap Lever 3, eb-self B007). A clean
  `validate` set `needs: resolved` but nothing told the user the entry was done, so it
  looked identical to a stalled `needs: validate` entry. The Worker Stop-hook path
  (step (h)/(j)) now surfaces `entry <id> validated — run /board-resolve <id> to close it`.
- **Doc drift** (eb-self C13 P3s). `pm-start.md`'s worker→PM refusal string now matches
  the mode guard (its single source of truth — no phantom `/board-resume`); `/worker-start`'s
  success message no longer leaks the raw `<<EB-WORKER-NOTHING-TO-DO>>` sentinel to the user.

## [1.3.0] — 2026-07-05

Batched hardening + first-run UX release. Consolidates the twelve improvement-loop
cycles of injection/traversal hardening (dogfooded on the `engineering-board/eb-self/`
board) and adds the C13 fixes for the documented first-run mode friction. The C13
confirming red-team and coherence sweeps were clean; the UX sweep surfaced one
README-accuracy defect at the flagship value moment, fixed here.

### Fixed
- **README first-run flow no longer dead-ends at the value moment** (eb-self C13
  UX P1). The Quickstart presented `/pm-start` (step 2) → `/worker-start` (step 3)
  as one continuous sequence, but a session holds one mode at a time, so
  `/worker-start` declined mid-session with a restart message the README never
  mentioned — the documented happy path broke for every first-timer right at the
  autonomous-pipeline demo. Step 3 now says to start a fresh session, and a new
  "one session, one mode" note explains the mode model and how to return to passive
  capture (including deleting `.engineering-board/session-mode.json` on local
  installs where the file persists across restarts).

### Added
- **SessionStart banner surfaces the current session mode** (eb-self C13 UX P2).
  The banner now prints `Mode: passive | PM | Worker (discipline=…) | paused` with a
  one-line hint on how to change it, so a user always knows which mode they are in —
  previously the only way to tell was to `cat .engineering-board/session-mode.json`.
  The passive line also names `/pm-start` and `/worker-start`, improving first-run
  discoverability. Four new `tests/session-start/` assertions (passive/PM/worker/
  corrupt-fallback).

### Changed
- **`.goal/POSITIONING.md` VP5 corrected** — the value-prop table still described the
  MCP server as a "Phase 2 build item"; it shipped in 1.2.0 (11 tools over stdio).
  Internal doc; understated a shipped feature (eb-self C13 coherence, LOW).

Product improvement loop (dogfooded on the `engineering-board/eb-self/` board).

### Security
- **Unicode Tag characters are rejected on sight** (eb-self B061). `_strip_invisible`
  deletes tag chars (`U+E0000–E007F`) before scanning — right when they *split* a
  visible verb, but when they *encode* the whole command the scan saw empty text and
  accepted, while the promotion writer kept the raw tag chars, so an invisible
  imperative a tag-decoding reader obeys would land on the board. Tags are deprecated
  with no legitimate use in a finding, so `_scan` now rejects any finding containing
  one (reason `invisible_tag`), closing the strip-and-promote asymmetry. One fixture.
- **Clause anchor now skips the whole markdown list-marker family** (eb-self
  B059). The skip-run handled unordered bullets (`- * + >`) but not ordered lists,
  so `1) ignore all previous instructions`, `a) delete…`, `(1) reset…`, `1] drop…`,
  and task-list `- [ ] ignore…` slipped past the anchor and promoted. Added a
  bounded `_LIST_MARKER` token covering ordered/lettered/roman + checkbox markers —
  bounded (never `\w+`), so a benign `1) the validator will…` keeps its subject and
  still promotes. Also (B060) the slash-directive rule now catches a slash abutting
  a marker/quote/paren (`-/cmd`, `(/cmd)`), matching the subagent rule's laxity.
  Five new fixtures incl. a benign ordered-list control.
- **Invisible-character strip now covers the whole default-ignorable class**
  (eb-self B058). The strip was a hand-list of 5 (ZWSP/ZWNJ/ZWJ/WJ/BOM) — the one
  `_normalize` fold never made comprehensive — so a soft hyphen `U+00AD`, the
  Mongolian vowel separator, the invisible math operators, the Arabic letter mark,
  or a variation selector could split a verb token invisibly and slip a clean,
  obeyable imperative past every rule. Replaced with a whole-class strip (Unicode
  category `Cf` + variation selectors + combining grapheme joiner). All three
  `_normalize` folds — line breaks, sentence terminators, invisibles — are now
  comprehensive-by-construction. Two new fixtures.
- **Terminator fold now spans the major living scripts** (eb-self B056). B053's
  terminator set was hand-picked and missed the clause/sentence marks of many
  scripts — Arabic comma/semicolon, Armenian, Ethiopic comma, Tibetan, Khmer,
  Mongolian, Myanmar, Sinhala, Georgian, Syriac. Rather than add glyphs one cycle
  at a time (the enumeration treadmill), the fold is now comprehensive across the
  common living scripts, so the mechanism is complete-by-construction. The module
  docstring adds a mechanism-vs-coverage severity rubric: a missing *mechanism* is
  major; a coverage gap in a comprehensive fold is P2/P3. Three new fixtures.
- **Reject filter now folds non-Latin sentence terminators to a clause boundary**
  (eb-self B053). The boundary class `[.!?:;,\n]` was ASCII-only, so a bare
  imperative after a CJK `。`/`、`, Devanagari danda `।`/`॥`, Ethiopic `።`, or
  Arabic `۔`/`؟` did not anchor and promoted — and (unlike a cross-script
  homoglyph) these leave the following verb pristine, so an LLM reads a clean
  command. `_normalize` folds a curated terminator set to ASCII `.` before
  scanning. Three new adversarial fixtures. Lineage B043/B051.
- **MCP evidence blockquote splits on every line separator** (eb-self B054). The
  `board_capture_finding` evidence blockquote used `.split("\n")`, so a bare
  `\r`/`\f`/NEL before `## …` escaped the `> ` prefix and forged a scratch header
  (one finding counted as two) — re-opening the B040 harm in a writer the
  MCP-only fix never covered. Now `.splitlines()`, and `_oneline` (title/kind/
  affects/heading) is hardened to the full separator class. CR/FF/NEL regressions
  added. (B053/B054 are the same incomplete-line-handling class as B051/B052, now
  fixed across every writer/reader.)
- **Reject filter now folds every line break to a clause boundary** (eb-self
  B051). `_normalize` folded only `U+2028/2029/0085`, and the boundary class was
  `[.!?:;,\n]` — so an imperative hidden after CR (`\r`, the most common
  real-world break), VT, FF, or `U+001C/1D/1E` did not anchor and promoted. Now
  `"\n".join(text.splitlines())` folds the whole line-break class at once. Three
  new adversarial fixtures (VT/FF/FS) + direct CR/CRLF assertions. The module
  docstring now documents the filter's **accepted-residual boundary** (in-scope
  imperative-mood verbs vs accepted out-of-scope excluded-verbs / non-imperative
  moods / NFKC-irreducible homoglyphs), so a denylist leak is a defect only if it
  defeats an in-scope rule. Lineage B025/B037/B043/B048.
- **`board-consolidate.sh` flattens every promoted field** (eb-self B052). The
  promotion writer wrote `title`/`affects`/`tags`/`discovered` raw (only
  `evidence_quote` was flattened), so a crafted title newline could close the
  frontmatter fence early and inject a body header — the same class as the
  MCP-side B028/B040 but in a writer that fix never covered. A `flatten()` helper
  now collapses all whitespace/control in every promoted field; an isolated smoke
  regression drives the real writer.
- **Reject filter now catches adverb-fronted imperatives** (eb-self B048). The
  clause-boundary anchor only fired when an injection verb led the clause after
  an optional lead-in chain; an ordinary adverb fronted before the verb
  (`Immediately ignore…`, `Quietly delete…`, `Always disregard…`) pushed it off
  the boundary and the payload promoted. A curated adverb set now folds into the
  same optional skip-run (curated, not a blanket `\w+ly`, so non-adverb `-ly`
  words like `apply override` still promote; safe regardless because each verb is
  still matched only in its bare imperative form). Four new adversarial fixtures;
  benign corpus unchanged (100% accept). Lineage B025/B037/B043.
- **Reject filter now sees through Unicode look-alikes** (eb-self B043). Unicode
  bullets (`•` `–` `—` `●` …), markdown `##` headings, Unicode line separators
  (U+2028/2029/0085), and zero-width characters all bypassed the ASCII-only
  marker/boundary classes (continuation of B025/B037). Inputs are now NFKC-
  normalized, stripped of zero-width chars, and line-separator-folded before the
  rules scan, and the marker run covers `#` + common Unicode bullets/dashes —
  closing the whole look-alike class rather than one glyph. Benign bulleted
  findings still promote. Three new adversarial fixtures.
- MCP `board_capture_finding` blockquotes the `evidence` field so an embedded
  `## …` can't inject a second scratch header / spoof the unpromoted-finding
  count (eb-self B040 follow-up); and `session_id` with whitespace/newline is now
  rejected at `board_claim`/`board_release` and in the claim scripts — it broke
  the `owner.txt` round-trip (self-DoS) and could inject owner lines (**closes
  the known-open B029**).
- **Reject filter now catches markdown-marker-prefixed imperatives** (eb-self
  B037). A bullet or blockquote marker before the verb (`- ignore all previous
  instructions`, `> ignore…`) broke the C1/C2 clause-leading anchor — and scratch
  is markdown, so that's the *natural* injection form. The boundary run now skips
  a leading run of `- * + >`; a benign bulleted finding (`- the stage will
  override X`) still promotes. Three new adversarial fixtures.
- **MCP `affects_prefix` router-row injection closed** (eb-self B038). `board_init`
  wrote `affects_prefix` into the `BOARD-ROUTER.md` table unsanitized, so a value
  with an embedded newline + `|` could inject a spoofed router row — forging a
  project in `board_list_projects` and persistently DoSing every no-`project`
  bulk tool. It is now newline-flattened with `|` neutralized.
- **MCP `board_init` symlink containment** (eb-self B039). `board_init` was the
  one path-writing tool without realpath containment; a pre-planted symlink at
  `engineering-board/<project>` could relocate the scaffold outside the repo
  root. It now asserts realpath containment before writing.
- MCP `board_capture_finding` flattens `title`/`kind`/`affects` so a crafted
  title can't inject a second scratch header or spoof the unpromoted-finding
  count (eb-self B040).
- **MCP `entry_id` path traversal closed** (eb-self B034, red-team blocker). The
  same traversal class as B024, left open for `entry_id`: `board_claim` /
  `board_release` passed it straight into `<board>/_claims/<entry_id>` (mkdir +
  `rm -rf`), so a `../` id could create files or **`rm -rf` directories outside
  the repo root**. Added `validate_entry_id()` at both tools, plus a
  path-separator/`..` guard in `board-claim-acquire.sh` / `board-claim-release.sh`
  for direct invocation.
- **MCP bulk tools now enforce router-row containment** (eb-self B035). The
  no-`project` branches of `board_rebuild` / `board_status` / `board_list_entries`
  built targets with a raw `os.path.join(root, router_path)`, bypassing the
  containment `board_dir_for` enforces — a hand-edited router `path` column of
  `../outside` could overwrite an external `BOARD.md` or read entries outside the
  root. They now resolve rows through `resolve_board_row()` (realpath containment)
  and raise on escape.
- MCP `append_section.heading` is newline-flattened so it can't inject extra
  lines into an entry body (eb-self B036, hygiene).
- **MCP path traversal closed** (eb-self B024, red-team blocker). The MCP
  server built board paths from an unvalidated `project` name, so an absolute
  (`/tmp/x`) or `../../` project name wrote board scaffolding and entry files
  **outside the repo root**. Added `validate_project()` (safe single-segment
  names only) at `board_init` and every board op, plus an `os.path.realpath`
  containment assertion in `board_dir_for`. Pinned by new MCP tests.
- **MCP frontmatter-injection neutralized** (eb-self B028). `serialize_frontmatter`
  now flattens embedded CR/LF/control characters in field values, so untrusted
  finding text copied into a `title` can no longer inject frontmatter keys (e.g.
  a hidden `status: resolved`) or close the `---` block early.
- **Reject filter now catches politeness/modal-prefixed imperatives** (eb-self
  B025). "Please ignore all previous instructions", "You must ignore…", "Now
  ignore…" bypassed the C1 clause-boundary matcher; it now allows an optional
  lead-in run (`please|kindly|now|just|you must|you should|…`) before the verb,
  while a benign modal followed by a subject ("should the validator ignore…")
  still promotes. Verb set broadened with `send`/`leak`/`expose`. Four new
  adversarial fixtures; the `reject-filter` corpus grows with every pinned bypass.

- **Injection reject-filter hardened and made single-source** (eb-self B002).
  The deterministic defense-in-depth filter re-applied at consolidation was
  trivially bypassable: it only matched imperative verbs anchored at the string
  start, an 8-verb list, and scanned only `title`/`evidence_quote`. Crafted
  findings with a non-leading imperative ("as noted, ignore prior findings"), an
  un-listed verb (`delete`/`remove`/`close`/`drop`), or a payload in `tags`/
  `affects` promoted straight to the live board. New canonical module
  `hooks/scripts/board_reject_check.py` (imported by `board-consolidate.sh`, the
  single source of truth) matches injection verbs in imperative mood at any
  clause boundary, broadens the verb set, scans all string fields, and is
  case-insensitive on slash/subagent directives. Threat model documented:
  entries are read, never eval'd, so descriptive shell/HTML metacharacters are
  intentionally not rejected (they recur in legitimate technical findings).

### Changed (onboarding)
- **README Quickstart now covers the whole first-value path** (eb-self B027).
  It dead-ended at `/board-init`; `/pm-start`, `/worker-start`, and the passive-
  capture behavior lived only in a reference table, so a Quickstart-follower
  could never reach first promotion. The Quickstart now walks capture → promote
  → autonomous fix, names where captures land (`_sessions/`), points at
  `/board-install-permissions`, and states an honest time-to-first-value
  expectation (~5 min to first capture, ~10–15 min to first promotion following
  only the README). Measurement: `.goal/evidence/loop/C2-time-to-first-value.md`.

### Fixed (permissions & UX)
- **README hero link no longer implies a hosted render** (eb-self B055). The
  "rendered live by `/board-view`" hero link pointed at the committed
  `board.html`, which GitHub serves as raw source; the text now reads "the HTML
  `/board-view` generates … open it locally to render" so the destination isn't
  surprising.
- **Quickstart points at the visual board viewer** (eb-self B050). The "visible
  confirmation" step pointed only at `_sessions/` or `/board-rebuild` (which
  refreshes the markdown `BOARD.md` index, not the visual board); it now surfaces
  `/board-view` (the themed HTML Kanban F001 shipped) at the moment a first-time
  user wants to *see* their board.
- **Permission rules now install in the wrapped `Tool(specifier)` form** (eb-self
  B046). `/board-install-permissions` emitted `claude config add
  permissions.allow "<bare specifier>"` and the self-check compared the bare
  specifier — but Claude Code allow-rules must be `Tool(specifier)`
  (`Bash(bash …:*)`, `SlashCommand(/pm-start)`); a bare specifier never matches,
  so the install silently no-opped while the self-check reported a false green
  over it. The install command and `board-permission-self-check.sh` now
  reconstruct the wrapped rule; a new `settings-bare-legacy` fixture + test
  asserts bare rules report all-missing (not a false green).
- **`worker → pm` refusal is restart-only** (eb-self B047). The mode-guard's
  worker→pm refusal suggested `/board-resume`, which only acts on a paused board
  and no-ops from worker mode — a dead-end hint. It now says restart-only,
  matching the symmetric pm→worker refusal.

### Fixed (docs coherence)
- Corrected stale counts left by the C1 refresh: README suite count and
  `ARCHITECTURE.md` §10 rebuilt to the real run-all suites (was "8 domains",
  omitted `session-start`); "11 orchestrator-facing prompt files" → 10 (eb-self
  B031). CHANGELOG "50-fixture corpus" wording clarified (B032). `worker-start`
  unsupported-discipline error no longer leaks a version number (B033).

### Fixed (data integrity)
- **MCP-captured scratch findings are no longer silently destroyed** (eb-self
  B026). `board_capture_finding` writes a human-markdown inbox
  (`_sessions/mcp-<date>.md`) that the consolidator's JSON parser can't ingest
  and that has no transcript to anchor against — yet `board-consolidate.sh`'s GC
  archived it anyway, losing the findings with no log entry, while the
  SessionStart banner told users to run exactly that command. GC now archives
  only session files that produced at least one parsed finding; anything
  unparsed is left in place and logged `deferred_unparsed`. The banner now
  directs users to promote MCP inbox files with the `board_create_entry` tool.

### Added
- **Animated README demo** (`docs/board-demo.svg`). A self-contained animated
  SVG of the real pipeline — a finding is captured, promoted, and driven through
  `tdd → review → validate → done` (a card moving across the four pipeline
  columns), brand-tokened, light/dark, with an aria-label. Embedded as the
  README hero; links to the live `board.html` that `/board-view` generates.
- **`/board-view` — zero-dependency HTML board viewer** (eb-self F001). Generates
  a self-contained, themed Kanban view to `engineering-board/<project>/board.html`
  — a four-column pipeline (To do → Review → Validate → Done) plus a Questions/
  Observations/Learnings lane, reusing the landing-page brand tokens (light/dark).
  Offline, no JavaScript, byte-deterministic (safe to commit), and HTML-escapes
  all entry text so a crafted title can't inject markup. New `tests/view/`
  suite (10 checks incl. XSS-escaping + determinism), registered in
  `tests/run-all.sh` (now **14 suites**). Closes the biggest conceded
  competitive gap (visualization) without a daemon — the view is just another
  committed in-repo projection of the board.
- **`tests/security/reject-filter.sh`** (eb-self B003) — drives every
  adversarial-paste and benign-findings fixture through the canonical
  filter and asserts each fixture's declared `expect:`/`expect_reason:`.
  Registered in `tests/run-all.sh` (now **12 suites**) and CI-enforced. The
  fixture corpus previously had **no** consumer, so the "100% reject-rate"
  guarantee `ARCHITECTURE.md` advertised was never measured. New fixtures pin
  the bypass vectors above.

### Fixed
- `ARCHITECTURE.md` §10 now describes the real reject-filter suite instead of
  the never-measured guarantee; `finding-extractor.md` / `consolidator.md`
  reject-rule prose aligned with the shipped filter.
- **Permission allowlist now covers every script the orchestrator runs** (eb-self
  B004). `references/required-permissions.json` listed only 5 claim scripts — in
  a relative path form that does not match the `$CLAUDE_PLUGIN_ROOT`-absolute
  invocations — while the Stop procedure and commands shell out to
  `board-scratch-append.sh` (every passive capture), the worker/PM registry, the
  mode-guard, and migrate/relocate. Those omissions meant the autonomous loop
  hit permission prompts on its core scripts. The manifest now covers all 11
  invoked scripts in the matching `$CLAUDE_PLUGIN_ROOT` form; new coverage
  assertions in `tests/permissions/automated.sh` (T26–T28) parse every
  `bash …board-*.sh` invocation in `stop-hook-procedure.md` + `commands/*.md`
  and fail if any is unlisted or uses an inconsistent path form.
- Removed internal milestone jargon (`M2.2.b`/`M2.2.c`) from user-facing command
  copy (`board-install-permissions.md`, `pm-start.md`, `worker-start.md`;
  eb-self B015). Aligned `required-permissions.json`'s version stamp to the
  plugin version (partial B016).
- **SessionStart no longer risks its 10s timeout on large boards** (eb-self
  B001). The `blocked_by` dependency map ran a full-tree `grep -rl` per unique
  blocker — O(blockers × files); a ~1200-entry board took **15s** and lost the
  board banner. It now computes in a single `python3` pass over frontmatter:
  **1200 entries render in ~0.1s** (linear to 2000+). Also fixes a `head -1`
  quirk that mis-attributed identical `blocked_by` lines.
- Empty boards no longer print a garbled two-line `0` open-count (eb-self B010).
- New `tests/session-start/automated.sh` suite (correctness + a perf guard that
  fails if a 1200-entry board takes ≥ 10s); `tests/run-all.sh` now **13 suites**.
- **`board-index-check` no longer false-alarms on resolved entries** (eb-self
  B023, surfaced by dogfooding). It counted every file in each subdir while
  BOARD.md lists open entries only, so the invariant broke on any board that had
  resolved anything (the tidier then rebuilt on every run). It now counts only
  open (non-`resolved`) files. Pinned by a new resolve-in-place case in the
  smoke suite.

## [1.2.0] — 2026-07-04

### Added
- **MCP server (dual distribution).** A zero-dependency `python3` MCP server
  (`mcp-server/engineering_board_mcp.py`) exposes the board substrate as **11
  tools** over stdio (JSON-RPC 2.0, protocol `2025-06-18`): `board_init`,
  `board_list_projects`, `board_create_entry`, `board_list_entries`,
  `board_get_entry`, `board_update_entry`, `board_rebuild`,
  `board_capture_finding`, `board_claim`, `board_release`, `board_status`.
  The same committed `engineering-board/` board is now drivable from any
  MCP-capable client, not just Claude Code.
- **`.mcp.json`** at the plugin root bundles the server, so installing the
  Claude Code plugin also registers the MCP server (`${CLAUDE_PLUGIN_ROOT}`).
- **`mcp-server/README.md`** with `claude mcp add` and Claude Desktop config
  snippets.
- **CI-gated MCP tests** (`mcp-server/test_mcp_server.py`, 65 checks) wired into
  `tests/run-all.sh` (now 11 suites): a real subprocess stdio session plus a
  full board lifecycle validated against `hooks/scripts/board-validate-entry.sh`.
- Plugin manifest polish: `homepage`, `repository`, `license`, and `keywords`.

### Fixed
- **Runtime doc accuracy:** `hooks/stop-hook-procedure.md` step (d) no longer
  tells the orchestrator the `learnings-curator` returns a v0.2.2 placeholder —
  it is fully implemented and delegates to `board-curate-learnings.sh`.
- **Documentation drift:** `ARCHITECTURE.md` command count corrected (9 → 10,
  adds `/board-migrate`); stale shipped-state header, "no CI runner" note, and
  learnings-curator descriptions refreshed. README + `test.yml` suite counts
  corrected.
- **Test determinism:** the `stop-hook-mode-routing` suite used an
  `echo "$VAR" | grep -q` idiom that, under `set -euo pipefail`, could take
  SIGPIPE and spuriously fail on CI. Switched to herestrings; also fixed an
  unescaped-backtick needle that ran `tdd-builder` as command substitution.

## [1.1.0] — 2026-06-06

### Changed
- Relocated board content to a visible, committed top-level
  `engineering-board/` directory (the new default). Pre-1.1.0 `docs/boards/`
  and legacy `docs/board/` layouts still resolve. Added `/board-migrate
  --relocate` and centralized location resolution in `board-paths.sh`.

## [1.0.1] — 2026

### Fixed
- Scratch-append fidelity (issue #3): `board-scratch-append.sh` owns the
  timestamp + canonical write so the orchestrating LLM is out of the scratch
  byte-copy path. Malformed copies now fail loudly.

## [1.0.0] — 2026

### Added
- Stable release; design surface declared frozen. Closed a claim-acquire
  construction-window race (`board-claim-acquire.sh` polls up to 250ms for
  `owner.txt`/`heartbeat.txt` after a losing `mkdir`).

## [0.3.2]

### Added
- Test-debt closeout: subagent Output-contract fixtures (7 agents), pause/resume
  registry round-trip invariants, and the GitHub Actions CI gate enforcing
  `tests/run-all.sh` on every push.

## [0.3.1]

### Added
- `board-mode-guard.sh`: deterministic enforcement of the §11.5 mode-transition
  refusal matrix; pause/resume round-trips the `(mode, discipline)` tuple.

## [0.3.0]

### Added
- Learning entity (`L###`), `learnings-curator` agent, `/board-migrate` (SHA256
  apply/rollback), and the SessionStart top-learnings surface.

## [0.2.3]

### Added
- Resilience layer: active-workers registry, PM-fallback heartbeat, `paused:`
  field.

[Unreleased]: https://github.com/GhostlyGawd/engineering-board/commits/main
[1.2.0]: https://github.com/GhostlyGawd/engineering-board/pull/18
[1.1.0]: https://github.com/GhostlyGawd/engineering-board/pull/8
