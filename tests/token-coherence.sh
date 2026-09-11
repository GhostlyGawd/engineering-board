#!/usr/bin/env bash
# Shared Graphite contract: the published CSS is byte-identical to the brand
# source; generated HTML embeds that same sheet with only its font URL replaced.
# Exercise the renderer rather than parsing obsolete hand-maintained mirrors.
set -uo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT="${1:-$(cd "$SCRIPT_DIR/.." && pwd)}"
python3 - "$ROOT" <<'PY'
import base64
from html.parser import HTMLParser
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile

root = Path(sys.argv[1]).resolve()
source = (root / 'brand/tokens.css').read_bytes()
css = source.decode('utf-8')
font = (root / 'brand/fonts/manrope-latin-wght-normal.woff2').read_bytes()
failures = []
checks = 0

def check(ok, message):
    global checks
    checks += 1
    if not ok:
        failures.append(message)

class Page(HTMLParser):
    def __init__(self):
        super().__init__(); self.tags=[]
    def handle_starttag(self, tag, attrs):
        self.tags.append((tag, dict(attrs)))

published = root / 'docs/assets/brand.css'
check(published.is_file() and published.read_bytes() == source,
      'docs/assets/brand.css must be an exact published copy of brand/tokens.css')
published_font = root / 'docs/assets/fonts/manrope-latin-wght-normal.woff2'
check(published_font.is_file() and published_font.read_bytes() == font, 'published Manrope bytes differ from source')
check(not (root / 'docs/assets/tokens.css').exists(), 'dead docs/assets/tokens.css mirror reappeared')
page = Page(); landing = (root / 'docs/index.html').read_text(); page.feed(landing)
check(any(tag == 'link' and attrs.get('rel') == 'stylesheet' and attrs.get('href') == 'assets/brand.css'
          for tag, attrs in page.tags), 'landing page does not load the canonical published stylesheet')
check(not re.search(r'--eb-[\w-]+\s*:', landing), 'landing page redeclares shared tokens')
check('color-scheme: dark' in css and ':root[data-theme="light"]' in css,
      'canonical source must provide default dark and explicit light themes')

with tempfile.TemporaryDirectory() as temp:
    project = Path(temp)
    board = project / 'engineering-board/coherence'
    (board / 'bugs').mkdir(parents=True)
    (board / 'BOARD.md').write_text('# coherence\n')
    (project / 'engineering-board/BOARD-ROUTER.md').write_text(
        '# Board Router\n\n| project | path | affects prefix |\n|---|---|---|\n'
        '| coherence | engineering-board/coherence | coherence/ |\n')
    env = dict(os.environ, CLAUDE_PROJECT_DIR=str(project))
    result = subprocess.run(['bash', str(root / 'hooks/scripts/board-view.sh'), 'coherence', '--stdout'],
                            env=env, text=True, capture_output=True, check=True)
    output = result.stdout
    match = re.search(r'<style id="eb-brand-tokens">\n(.*?)</style>', output, re.S)
    check(match is not None, 'viewer does not embed its shared stylesheet')
    if match:
        embedded = match.group(1)
        data = re.search(r'data:font/woff2;base64,([A-Za-z0-9+/=]+)', embedded)
        check(data is not None, 'viewer does not embed Manrope')
        if data:
            check(base64.b64decode(data.group(1)) == font, 'embedded Manrope bytes differ from source')
            restored = embedded.replace(data.group(0), 'fonts/manrope-latin-wght-normal.woff2')
            check(restored.strip() == css.strip(), 'embedded CSS drifts from canonical source')
        # Every token used by the viewer must resolve from the canonical source.
        declared = set(re.findall(r'(--eb-[\w-]+)\s*:', embedded))
        used = set(re.findall(r'var\((--eb-[\w-]+)', output))
        check(used <= declared, 'undefined viewer tokens: ' + ', '.join(sorted(used-declared)))
        remaining = output[:match.start()] + output[match.end():]
        # Print intentionally switches to ink on white. No screen theme may
        # silently override the shared source after it is embedded.
        while True:
            block = re.search(r'@media print\s*\{', remaining)
            if not block:
                break
            depth = 1
            end = block.end()
            while end < len(remaining) and depth:
                depth += (remaining[end] == '{') - (remaining[end] == '}')
                end += 1
            check(depth == 0, 'unterminated print stylesheet')
            remaining = remaining[:block.start()] + remaining[end:]
        check(not re.search(r'--eb-[\w-]+\s*:', remaining), 'viewer screen styles override canonical tokens')

for failure in failures:
    print('  [FAIL] ' + failure)
print(f'token-coherence: {checks} checks, {len(failures)} failures')
sys.exit(bool(failures))
PY
