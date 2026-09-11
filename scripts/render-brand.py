#!/usr/bin/env python3
"""Render shipped vector brand assets to PNG. Development-only Playwright.

uv run --with playwright python scripts/render-brand.py --chromium /path/to/chrome
"""
import argparse
from pathlib import Path
import shutil
from playwright.sync_api import sync_playwright

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--chromium', required=True)
args = parser.parse_args()
root = Path(__file__).resolve().parents[1]

with sync_playwright() as p:
    browser = p.chromium.launch(executable_path=args.chromium, headless=True)
    page = browser.new_page()
    for size in (16, 32, 48, 180):
        page.set_viewport_size({'width': size, 'height': size})
        content = (root/'brand/favicon.svg').read_text().replace('width="32" height="32" viewBox', f'width="{size}" height="{size}" viewBox', 1)
        page.set_content('<html style="margin:0"><body style="margin:0">'+content+'</body></html>')
        page.screenshot(path=str(root/f'brand/favicon-{size}.png'), omit_background=True)
    page.set_viewport_size({'width':1280,'height':640})
    page.set_content('<html style="margin:0"><body style="margin:0">'+(root/'brand/social-preview.svg').read_text()+'</body></html>')
    page.screenshot(path=str(root/'brand/social-preview.png'))
    browser.close()
for name in ('favicon-32.png', 'favicon-180.png', 'social-preview.png'):
    shutil.copy2(root/'brand'/name, root/'docs/assets'/name)
print('Raster brand derivatives rendered and synchronized.')
