"""Validate offline navigation, no-script evidence, fixture fidelity and escaping."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit, unquote
import importlib.util
import tempfile
import shutil

ROOT = Path(__file__).resolve().parent
class Document(HTMLParser):
    def __init__(self, text):
        super().__init__(); self.ids=set(); self.links=[]; self.scripts=[]; self.hidden=[]
        self.feed(text)
    def handle_starttag(self, tag, attrs):
        a=dict(attrs)
        if 'id' in a: self.ids.add(a['id'])
        if tag in ('a','link') and a.get('href'): self.links.append(a['href'])
        if tag in ('img','script') and a.get('src'): self.links.append(a['src'])
        if tag=='script': self.scripts.append(a)
        if 'hidden' in a: self.hidden.append(a.get('id'))
def validate(root):
    root = root.resolve()
    errors=[]
    pages={p:Document(p.read_text()) for p in root.rglob('*.html')}
    for path,doc in pages.items():
        source=path.read_text()
        if 'Synthetic example' not in source or 'Read-only' not in source: errors.append(f'{path.name}: missing scope label')
        for link in doc.links:
            url=urlsplit(link)
            if url.scheme:
                if url.scheme!='https': errors.append(f'Unsafe URL: {link}')
                continue
            target=(path.parent/unquote(url.path)).resolve() if url.path else path
            if not target.is_relative_to(root.resolve()): errors.append(f'Outside prototype: {link}'); continue
            if not target.is_file(): errors.append(f'Missing target: {link}'); continue
            if url.fragment and target.suffix=='.html' and url.fragment not in pages[target].ids: errors.append(f'Missing anchor: {link}')
        if any('src' not in script for script in doc.scripts): errors.append(f'{path.name}: unexpected inline script')
    home=(root/'index.html').read_text()
    for id in ('H001','B001','B002','B003'):
        if f'entry-{id}' not in pages[root/'index.html'].ids: errors.append(f'Missing no-JS record {id}')
        if f'entry-{id}' in pages[root/'index.html'].hidden: errors.append(f'No-JS record hidden: {id}')
    for phrase in ('Proposed hypothesis','Independent filtering errors.','All adapters use the same rule.','No outcome recorded.','codex plugin marketplace add GhostlyGawd/engineering-board','codex plugin add engineering-board@engineering-board'):
        if phrase not in home: errors.append(f'Missing required content: {phrase}')
    return errors

def main():
    errors=validate(ROOT)
    repo=ROOT.parent.parent
    for fixture in (repo/'references/demo/pattern-intelligence/bugs').glob('B00[123]*.md'):
        if (ROOT/'source'/f'{fixture.name[:4]}.md').read_bytes()!=fixture.read_bytes(): errors.append(f'Fixture changed: {fixture.name}')
    with tempfile.TemporaryDirectory() as temp:
        copy=Path(temp)/'prototype'; shutil.copytree(ROOT,copy)
        (copy/'source/B001.html').unlink()
        assert any('Missing target' in e for e in validate(copy)), 'Validator accepted a missing source page'
        shutil.copy2(ROOT/'source/B001.html',copy/'source/B001.html')
        index=copy/'index.html'; index.write_text(index.read_text().replace('id="entry-H001"','id="entry-H001" hidden'))
        assert any('No-JS record hidden' in e for e in validate(copy)), 'Validator accepted hidden no-JS evidence'
    # The builder escapes raw fixture text before placing it in HTML. Challenge a
    # disposable fixture with markup, then rebuild only in that disposable tree.
    with tempfile.TemporaryDirectory() as temp:
        copy=Path(temp)/'repo/prototypes/graphite'; copy.mkdir(parents=True)
        shutil.copy2(ROOT/'build.py',copy/'build.py')
        (copy/'source').mkdir()
        fixtures=copy.parent.parent/'references/demo/pattern-intelligence/bugs'; fixtures.mkdir(parents=True)
        original=repo/'references/demo/pattern-intelligence/bugs'
        for p in original.glob('B00[123]*.md'): shutil.copy2(p,fixtures/p.name)
        fixture=next(fixtures.glob('B001*'))
        fixture.write_text(fixture.read_text()+'\n<script>alert("unsafe")</script>\n')
        spec=importlib.util.spec_from_file_location('temporary_prototype_build',copy/'build.py')
        module=importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
        source=(copy/'source/B001.html').read_text()
        assert '<script>alert(' not in source and '&lt;script&gt;alert(' in source, 'Raw fixture markup executed instead of displayed'
    if errors: raise SystemExit('\n'.join(errors))
    print('PASS: six offline pages, all local links/anchors/assets, no-JS records, fixture fidelity, missing-target/hidden-record rejection, raw markup escaping.')
if __name__=='__main__': main()
