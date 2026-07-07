#!/usr/bin/env bash
# tests/token-coherence.sh — Guard the design-token "single source of truth"
# against silent drift across the surfaces that inline it.
#
# HIERARCHY.md Fix 8 / Finding F7. `brand/tokens.css` is billed as the single
# source of truth, but the tokens are hand-mirrored — inlined into the landing
# page (`docs/index.html`) and into the generated board view
# (`hooks/scripts/board-view.sh`). Those two surfaces are self-contained,
# committed, byte-deterministic HTML documents by design (zero build step), so
# the mirrors stay hand-maintained. This lint is the safety net that a build
# step would otherwise provide: it fails the moment a mirrored token's VALUE
# diverges from `brand/tokens.css`.
#
# A third copy (`docs/assets/tokens.css`) had already drifted — it omitted
# `--eb-card` and `--eb-danger`. That file was unreferenced (nothing linked it)
# and is deleted as part of Fix 8; this test keeps the two live mirrors honest.
#
# Invariant enforced (per theme scope: light `:root`, `@media` dark, and
# `[data-theme="dark"]`):
#   A. Cross-file — every token a surface DECLARES must match `brand/tokens.css`
#      byte-for-byte after value normalization. Surfaces may carry a SUBSET of
#      the brand tokens (the landing page has no danger cards, so it need not
#      define `--eb-danger`); the guard only compares tokens the surface chose
#      to inline. Surface-local tokens absent from brand (e.g. the board view's
#      `--eb-accent-cur`) are ignored.
#   B. Intra-file — the `@media (prefers-color-scheme:dark)` block and the
#      `[data-theme="dark"]` block within a single file must agree, so the two
#      ways of triggering dark mode can't diverge.
#
# Deliberate carve-out: `--eb-font-sans` / `--eb-font-mono` are font-family
# FALLBACK stacks that surfaces legitimately trim (the board view drops
# "Helvetica Neue" / "Cascadia Code" to stay compact). They are compared for
# presence only, not value. Every other token — all colors and metrics, where
# drift is a real hierarchy bug — must match exactly.
#
# Values are normalized before comparison so cosmetic minification differences
# (`0.06` vs `.06`, spaces after commas) are not treated as drift.
#
# Usage:
#   bash tests/token-coherence.sh [plugin-root]
#
# Exits 0 iff every mirrored token matches the source of truth.

# No `set -e`: python streams its own report and we propagate its exit code.
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT="${1:-$(cd "$SCRIPT_DIR/.." && pwd)}"

if ! command -v python3 >/dev/null 2>&1; then
  echo "token-coherence: python3 not on PATH" >&2
  exit 1
fi

python3 - "$ROOT" <<'PY'
import os, re, sys

root = sys.argv[1]

SOURCE = "brand/tokens.css"
# (relative path, human label) for each surface that inlines the tokens.
SURFACES = [
    ("docs/index.html",             "landing page"),
    ("hooks/scripts/board-view.sh", "board view"),
]

# Font-family stacks are fallback lists surfaces may trim — presence-checked,
# not value-checked. Everything else must match exactly.
FONT_TOKENS = {"--eb-font-sans", "--eb-font-mono"}

DECL_RE = re.compile(r'(--eb-[A-Za-z0-9-]+)\s*:\s*([^;]+);')


def norm(value):
    """Normalize a CSS value so cosmetic minification isn't read as drift."""
    v = value.strip().lower()
    v = re.sub(r'\s+', ' ', v)          # collapse internal whitespace runs
    v = re.sub(r'\s*,\s*', ',', v)      # tighten around commas
    v = re.sub(r'\s*\(\s*', '(', v)     # tighten around parens
    v = re.sub(r'\s*\)\s*', ')', v)
    v = re.sub(r'(?<![0-9])0\.([0-9])', r'.\1', v)  # 0.30 -> .30
    return v


def decls(block):
    """(name -> raw value) for every --eb-* declaration in a CSS block body."""
    return {name: val.strip() for name, val in DECL_RE.findall(block)}


def scope_body(text, pattern):
    """Body of the first block whose selector matches `pattern`, or None.
    Token blocks contain no nested braces, so [^}]* is a safe body match."""
    m = re.search(pattern + r'\s*\{([^}]*)\}', text)
    return m.group(1) if m else None


def parse(text, path):
    """Extract the three theme scopes from a stylesheet's text."""
    # light: the FIRST bare `:root {` (not :root[...] / :root:not(...)); the
    # @media-print :root override appears later, so re.search picks the base.
    light = scope_body(text, r'(?:^|[\s,}]):root')
    if light is None or "--eb-" not in light:
        raise SystemExit(f"token-coherence: could not locate light :root block in {path}")
    return {
        "light":       decls(light),
        "dark_media":  (lambda b: decls(b) if b is not None else None)(
                           scope_body(text, r':root:not\(\[data-theme="light"\]\)')),
        "dark_attr":   (lambda b: decls(b) if b is not None else None)(
                           scope_body(text, r':root\[data-theme="dark"\]')),
    }


def read(rel):
    path = os.path.join(root, rel)
    if not os.path.isfile(path):
        raise SystemExit(f"token-coherence: MISSING {rel}")
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


SCOPE_LABEL = {"light": "light", "dark_media": "dark(@media)", "dark_attr": "dark([data-theme])"}

failures = []
checks = 0

src = parse(read(SOURCE), SOURCE)

# A third copy must not creep back in.
if os.path.isfile(os.path.join(root, "docs/assets/tokens.css")):
    failures.append("docs/assets/tokens.css exists again — it is a dead, drift-prone "
                    "token copy deleted in Fix 8; remove it (nothing links it).")

for rel, label in SURFACES:
    surf = parse(read(rel), rel)

    # A. Cross-file: every token the surface declares must match the source.
    for scope in ("light", "dark_media", "dark_attr"):
        s_decls, b_decls = surf.get(scope), src.get(scope)
        if s_decls is None or b_decls is None:
            continue
        for name, raw in s_decls.items():
            if name in FONT_TOKENS or name not in b_decls:
                continue  # font stacks: presence only; surface-local: ignored
            checks += 1
            if norm(raw) != norm(b_decls[name]):
                failures.append(
                    f"{rel} [{SCOPE_LABEL[scope]}] {name}: mirror {raw!r} "
                    f"!= {SOURCE} {b_decls[name]!r}")

    # B. Intra-file: the two dark blocks in this surface must agree.
    dm, da = surf.get("dark_media"), surf.get("dark_attr")
    if dm is not None and da is not None:
        for name in sorted(set(dm) | set(da)):
            checks += 1
            if name not in dm:
                failures.append(f"{rel}: {name} in [data-theme=dark] but missing from @media dark")
            elif name not in da:
                failures.append(f"{rel}: {name} in @media dark but missing from [data-theme=dark]")
            elif norm(dm[name]) != norm(da[name]):
                failures.append(f"{rel}: {name} differs between the two dark blocks "
                                f"({dm[name]!r} vs {da[name]!r})")

for f in failures:
    print(f"  [FAIL] {f}")

print("")
print(f"token-coherence: {checks} token comparisons against {SOURCE} "
      f"across {len(SURFACES)} surfaces")
if failures:
    print(f"token-coherence: {len(failures)} drift(s) — mirrors out of sync with the source of truth")
    sys.exit(1)
print("token-coherence: PASS — all mirrored tokens match the single source of truth")
sys.exit(0)
PY
exit $?
