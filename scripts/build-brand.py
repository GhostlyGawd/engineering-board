#!/usr/bin/env python3
"""Rebuild outlined Graphite assets. Development-only: fonttools + brotli.

Run: uv run --with fonttools --with brotli python scripts/build-brand.py
The shipped SVGs have no font or runtime dependency.
"""
from html import escape
from pathlib import Path
import shutil
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont
from fontTools.pens.svgPathPen import SVGPathPen

ROOT = Path(__file__).resolve().parents[1]
FONT = ROOT / 'brand/fonts/manrope-latin-wght-normal.woff2'

def lettering(text, size, color, x=0, baseline=0, weight=800, tracking=-.04):
    font = instantiateVariableFont(TTFont(FONT), {'wght': weight}, inplace=False)
    glyphs = font.getGlyphSet()
    cmap = font.getBestCmap()
    scale = size / font['head'].unitsPerEm
    cursor = 0
    paths = []
    for char in text:
        name = cmap[ord(char)]
        pen = SVGPathPen(glyphs)
        glyphs[name].draw(pen)
        path = pen.getCommands()
        if path:
            paths.append(f'<path transform="translate({x+cursor:.4f} {baseline:.4f}) scale({scale:.6f} {-scale:.6f})" d="{path}"/>')
        cursor += font['hmtx'].metrics[name][0] * scale + size * tracking
    return f'<g fill="{color}">' + ''.join(paths) + '</g>', cursor - size * tracking

def svg(width, height, title, body):
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-label="{escape(title)}"><title>{escape(title)}</title>{body}</svg>\n'

def write(name, contents):
    (ROOT / 'brand' / name).write_text(contents)

for theme, fg in [('dark', '#F7F8F8'), ('light', '#151619')]:
    paths, width = lettering('engineering board', 48, fg, 4, 50)
    art = svg(round(width + 8, 2), 64, 'engineering board', paths)
    write(f'wordmark-{theme}.svg', art)
    # Compatibility paths: old consumers receive the wordmark, never the rejected symbol.
    write(f'logomark-{theme}.svg', art)
    first, width = lettering('engineering', 96, fg, 4, 90)
    second, _ = lettering('board', 96, fg, 4, 174)
    write(f'wordmark-stacked-{theme}.svg', svg(round(width+8, 2), 196, 'engineering board', first+second))

# Favicon is a small textual abbreviation, not an independent graphical mark.
initials, width = lettering('eb', 24, '#F7F8F8', 0, 0)
initials, _ = lettering('eb', 24, '#F7F8F8', (32-width)/2, 24)
write('favicon.svg', svg(32, 32, 'engineering board', '<rect width="32" height="32" rx="5" fill="#08090A"/>'+initials))

body = '<rect width="1280" height="640" fill="#08090A"/>'
brand, _ = lettering('engineering board', 46, '#F7F8F8', 72, 110)
line1, _ = lettering('Connect findings.', 76, '#F7F8F8', 72, 286, 500, -.035)
line2, _ = lettering('Inspect the evidence.', 76, '#F7F8F8', 72, 377, 500, -.035)
sub, _ = lettering('Repository memory for engineering agents.', 27, '#D0D6E0', 76, 466, 400, -.015)
body += brand + line1 + line2 + sub
body += '<path d="M72 538H1208" stroke="#34343A"/>'
footer, _ = lettering('Repository-owned Markdown. Visible evidence.', 21, '#A5AAB3', 76, 583, 400, 0)
write('social-preview.svg', svg(1280, 640, 'Engineering Board: connect findings, inspect the evidence', body+footer))

assets = ROOT / 'docs/assets'
assets.mkdir(exist_ok=True)
for name in ['favicon.svg','logomark-dark.svg','logomark-light.svg','wordmark-dark.svg','wordmark-light.svg','social-preview.svg']:
    shutil.copy2(ROOT/'brand'/name, assets/name)
shutil.copy2(ROOT/'brand/tokens.css', assets/'brand.css')
print('Outlined wordmarks, typographic favicon, social SVG and shared stylesheet rebuilt.')
