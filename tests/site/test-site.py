#!/usr/bin/env python3
"""Production staging, canonical source navigation and progressive HTML contracts."""
from html import escape
from html.parser import HTMLParser
import importlib.util
from pathlib import Path
import re
import subprocess
import tempfile
import unittest
from unittest.mock import patch
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('build_site', ROOT / 'scripts/build-site.py')
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)


class Document(HTMLParser):
    def __init__(self, text):
        super().__init__()
        self.references = []
        self.ids = set()
        self.panels = []
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if 'id' in attrs:
            self.ids.add(attrs['id'])
        if 'data-panel' in attrs:
            self.panels.append(attrs)
        for key in ('href', 'src'):
            if key in attrs:
                self.references.append(attrs[key])


class PublishedSite(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.output = (Path(cls.tmp.name) / 'site').resolve()
        builder.stage(cls.output)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_publish_allowlist(self):
        self.assertEqual({p.name for p in self.output.iterdir()}, set(builder.PAGES) | {'assets', 'example', 'board.html'})
        for name in ('design', 'evidence', 'DEVELOPMENT.md', 'prototypes'):
            self.assertFalse((self.output / name).exists())
        self.assertFalse((self.output / 'assets/tokens.css').exists())
        self.assertIn((ROOT / 'brand/tokens.css').read_text().strip(), (self.output / 'assets/brand.css').read_text())

    def test_all_local_html_and_stylesheet_links_resolve(self):
        for page in self.output.rglob('*.html'):
            doc = Document(page.read_text())
            for ref in doc.references:
                parsed = urlsplit(ref)
                if parsed.scheme or parsed.netloc or ref.startswith('data:'):
                    continue
                target = (page.parent / unquote(parsed.path)).resolve() if parsed.path else page
                self.assertTrue(target.is_relative_to(self.output), (page, ref))
                self.assertTrue(target.is_file(), (page, ref))
                if parsed.fragment and target.suffix == '.html':
                    self.assertIn(unquote(parsed.fragment), Document(target.read_text()).ids, (page, ref))
        for css in self.output.rglob('*.css'):
            for ref in re.findall(r'url\([\'"]?([^\)\'\"]+)', css.read_text()):
                if not urlsplit(ref).scheme:
                    self.assertTrue((css.parent / ref).is_file(), (css, ref))

    def test_current_board_uses_absolute_canonical_sources(self):
        html = (self.output / 'board.html').read_text()
        fixture = next((ROOT / 'engineering-board/eb-self/bugs').glob('B001-*.md'))
        expected = builder.LINK_BASE + 'bugs/' + fixture.name
        self.assertIn(f'href="{expected}"', html)
        for ref in Document(html).references:
            if '.md' in ref:
                self.assertTrue(ref.startswith(builder.LINK_BASE), ref)
        # Compare with a fresh render, not the committed board.html cache.
        env = dict(__import__('os').environ, CLAUDE_PROJECT_DIR=str(ROOT))
        fresh = subprocess.check_output(['bash', str(ROOT / 'hooks/scripts/board-view.sh'), 'eb-self', '--stdout', '--link-base', builder.LINK_BASE], cwd=ROOT, env=env)
        self.assertEqual((self.output / 'board.html').read_bytes(), fresh)

    def test_synthetic_sources_and_no_javascript_path(self):
        home = (self.output / 'index.html').read_text()
        panels = Document(home).panels
        self.assertEqual({p['data-panel'] for p in panels}, {'H001', 'B001', 'B002', 'B003'})
        self.assertTrue(all('hidden' not in p for p in panels))
        self.assertGreaterEqual(home.count('Synthetic example'), 2)
        for entry_id in ('B001', 'B002', 'B003'):
            source = next((ROOT / 'references/demo/pattern-intelligence/bugs').glob(entry_id + '*.md')).read_text()
            self.assertEqual((self.output / 'example' / (entry_id + '.md')).read_text(), source)
            page = (self.output / 'example' / (entry_id + '.html')).read_text()
            self.assertIn(escape(source), page)
            self.assertIn('Synthetic example · Read-only', page)
            self.assertIn('../index.html#entry-' + entry_id, page)
        self.assertIn('No outcome recorded.', (self.output / 'example/H001.html').read_text())
        self.assertNotIn('prototype', home.lower())
        self.assertNotIn('prototype', (self.output / 'guide.html').read_text().lower())

    def test_existing_output_is_never_deleted(self):
        marker = Path(self.tmp.name) / 'occupied'
        marker.mkdir(exist_ok=True)
        (marker / 'keep.txt').write_text('keep')
        with self.assertRaisesRegex(ValueError, 'empty'):
            builder.stage(marker)
        self.assertEqual((marker / 'keep.txt').read_text(), 'keep')

    def test_renderer_failure_cannot_stage_stale_board(self):
        target = Path(self.tmp.name) / 'render-failure'
        with patch.object(builder.subprocess, 'run', side_effect=subprocess.CalledProcessError(1, 'board-view')):
            with self.assertRaises(subprocess.CalledProcessError):
                builder.stage(target)
        self.assertFalse(target.exists())

    def test_css_has_no_independent_palette(self):
        css = (self.output / 'site.css').read_text()
        self.assertFalse(re.search(r'#[0-9a-fA-F]{3,8}\b|rgba?\(|hsla?\(', css))
        self.assertIn('--bg:var(--eb-bg)', css)


if __name__ == '__main__':
    unittest.main()
