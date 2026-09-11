"""Run with uv run --with playwright python browser-check.py URL CHROME_PATH."""
import json
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright, expect

base = sys.argv[1].rstrip('/') + '/'
chrome = sys.argv[2]
out = Path(__file__).resolve().parent
checks = []
errors = []

def record(name):
    checks.append(name)

def no_overflow(page):
    assert page.evaluate('document.documentElement.scrollWidth <= innerWidth + 1'), page.url

with sync_playwright() as p:
    browser = p.chromium.launch(executable_path=chrome, headless=True)
    context = browser.new_context(viewport={'width': 1448, 'height': 1086}, color_scheme='dark')
    page = context.new_page()
    page.on('pageerror', lambda e: errors.append(str(e)))
    response = page.goto(base)
    assert response.status == 200
    expect(page.get_by_role('heading', name='Connect findings. Inspect the evidence.')).to_be_visible()
    page.evaluate('document.fonts.ready')
    no_overflow(page)
    page.screenshot(path=str(out / '01-desktop.png'))
    record('Desktop page, headline and local font render')

    page.get_by_role('link', name='Start with Codex').click()
    expect(page.locator('#install-command')).to_be_visible()
    expect(page.locator('#first-prompt')).to_contain_text('Initialize Engineering Board')
    assert 'Then capture' not in page.locator('#first-prompt').inner_text()
    page.get_by_role('button', name='Copy installation commands').click()
    expect(page.locator('#announcement')).to_contain_text('cop', ignore_case=True)
    page.screenshot(path=str(out / '02-install.png'))
    record('Codex handoff and truthful copy feedback')

    page.get_by_role('navigation').get_by_role('link', name='Example', exact=True).click()
    page.locator('#finding-search').fill('B002')
    entries = page.locator('.findings-panel a[data-select="B002"]')
    expect(entries).to_be_visible()
    entries.click()
    expect(page.locator('#entry-B002')).to_be_visible()
    expect(page.locator('#entry-B002')).to_contain_text('Board shows the wrong lane')
    page.locator('#entry-B002 a[href="source/B002.html"]').click()
    expect(page.get_by_role('heading', name='Board shows the wrong lane')).to_be_visible()
    expect(page.get_by_text('Synthetic example · Read-only', exact=True)).to_be_visible()
    page.screenshot(path=str(out / '03-source.png'))
    page.get_by_role('link', name='Back to finding', exact=True).click()
    expect(page.locator('#entry-B002')).to_be_visible()
    record('Search, selection, B002 source, return to selected finding')

    page.locator('#finding-search').fill('no-such-entry-987654')
    expect(page.locator('.no-results')).to_be_visible()
    page.screenshot(path=str(out / '04-no-results.png'))
    page.locator('.no-results button').click()
    expect(page.locator('#finding-search')).to_have_value('')
    expect(page.locator('.findings-panel a[data-select="B001"]')).to_be_visible()
    record('No-results feedback and reset recovery')

    page.locator('.findings-panel a[data-select="H001"]').click()
    panel = page.locator('#entry-H001')
    expect(panel).to_be_visible()
    for phrase in ['Proposed hypothesis', 'Alternative', 'Falsifier', 'No outcome recorded']:
        expect(panel).to_contain_text(phrase)
    page.locator('#example').scroll_into_view_if_needed()
    page.screenshot(path=str(out / '05-investigation.png'))
    page.get_by_role('button', name='Switch to light theme').click()
    no_overflow(page)
    page.screenshot(path=str(out / '06-light.png'))
    record('Hypothesis uncertainty hierarchy and light theme')

    mobile = browser.new_context(viewport={'width': 390, 'height': 844}, color_scheme='dark')
    mp = mobile.new_page()
    mp.on('pageerror', lambda e: errors.append(str(e)))
    for path in ['index.html', 'docs.html', 'source/H001.html', 'source/B001.html', 'source/B002.html', 'source/B003.html']:
        r = mp.goto(base + path)
        assert r.status == 200
        no_overflow(mp)
    mp.goto(base)
    mp.evaluate('document.fonts.ready')
    mp.screenshot(path=str(out / '07-mobile.png'))
    mp.get_by_role('link', name='Explore example', exact=True).click()
    mp.locator('.findings-panel a[data-select="B003"]').click()
    expect(mp.locator('#entry-B003')).to_be_visible()
    mp.locator('#entry-B003 a[href="source/B003.html"]').click()
    expect(mp.get_by_role('heading', name='Ready-work list omits the entry')).to_be_visible()
    mp.screenshot(path=str(out / '08-mobile-source.png'))
    record('Mobile six pages fit viewport; selection to source works')

    plain = browser.new_context(java_script_enabled=False, viewport={'width': 1448, 'height': 1086})
    np = plain.new_page()
    external = []
    np.on('request', lambda r: external.append(r.url) if not r.url.startswith(base) else None)
    np.goto(base)
    expect(np.locator('#entry-H001')).to_be_visible()
    np.get_by_role('link', name='Start with Codex').click()
    expect(np.locator('#install-command')).to_be_visible()
    for rid in ['B001', 'B002', 'B003', 'H001']:
        r = np.goto(base + 'source/' + rid + '.html')
        assert r.status == 200
        expect(np.get_by_text('Synthetic example · Read-only', exact=True)).to_be_visible()
        assert np.locator('main a[href*="index.html#entry-"]').count() >= 1
    assert not external, external
    record('No-JavaScript baseline and sources; no external requests')

    assert not errors, errors
    record('No page JavaScript exceptions')
    browser.close()

(out / 'browser-results.json').write_text(json.dumps({'result': 'passed', 'checks': checks, 'page_errors': errors}, indent=2) + '\n')
print(json.dumps({'result': 'passed', 'checks': len(checks)}))
