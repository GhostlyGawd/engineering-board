# Graphite working prototype

A local, read-only implementation of the approved A composition, Graphite palette,
and lowercase wordmark-only identity. This is an isolated prototype, not the public
website or generated board viewer. No board writes, installation simulation,
backend, telemetry, or authentication are included.

Open `index.html` directly, or serve this directory with Python:

```sh
python3 -m http.server 8765 --directory prototypes/graphite
```

Then visit http://localhost:8765. All six pages, source records, fonts, icons, and
example navigation are local. The upstream README link explicitly requires internet.
All records remain readable and linked with JavaScript disabled. JavaScript adds
inline selection, finding search by ID/title/path, reset, clipboard handling, and
a persisted dark/light preference. When clipboard access is unavailable, it selects
the text for manual copying and announces the fallback.

The primary composition is `a3-graphite.png`; the approved wordmark override is
`identity/graphite-wordmark-only.png`, both under the repository's
`docs/design/engineering-board-a-refinement/`. Manrope supplies the wordmark,
display, and reading type; record IDs use the system monospace stack. Asset source
versions, licenses, and hashes are retained under `assets/`.

B001–B003 copy the bundled synthetic fixtures without modifying the source Markdown.
Displayed titles are shortened for scanning. H001 is an explicitly synthetic
illustrative proposed hypothesis, with evidence, alternative, falsifier, and no
recorded outcome. Readable source pages link back to the corresponding record.
Install copy follows the repository's Codex instructions. The prototype makes no
claim that the plugin has been installed or that the browser is connected to a board.

Regenerate the static pages and run the focused validation:

```sh
python3 prototypes/graphite/build.py
python3 prototypes/graphite/check.py
node --check prototypes/graphite/app.js
```

The validator checks offline link/anchor/asset integrity, visible no-JavaScript
record content, required uncertainty and install copy, and original fixture bytes.
It also deletes a source target, hides a baseline record, and injects script markup
into a disposable fixture to challenge missing-page, no-JavaScript, and raw-render
failure handling. Browser verification remains necessary for layout, interactions,
keyboard focus, contrast, and clipboard behavior.
