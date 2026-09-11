from playwright.sync_api import sync_playwright, expect
from pathlib import Path
import json, hashlib, os
ROOT=Path(__file__).resolve().parents[3]
OUT=Path(__file__).resolve().parent
BASE='http://127.0.0.1:64498/'
CHROME=str(Path.home()/'.agent-browser/browsers/chrome-153.0.8010.36/Google Chrome for Testing.app/Contents/MacOS/Google Chrome for Testing')
AXE=os.environ.get('AXE_PATH','/tmp/design-canary-audit.LXX3IO/node_modules/axe-core/axe.min.js')
results=[]
with sync_playwright() as p:
    browser=p.chromium.launch(executable_path=CHROME,headless=True)
    for width,height in [(1448,1086),(390,844)]:
      for theme in ['dark','light']:
        c=browser.new_context(viewport={'width':width,'height':height},permissions=['clipboard-read','clipboard-write'])
        page=c.new_page(); errors=[]; requests=[]
        page.on('pageerror',lambda e: errors.append(str(e)))
        page.on('request',lambda r: requests.append(r.url))
        page.goto(BASE)
        if theme=='light': page.get_by_role('button',name='Switch to light theme').click()
        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
        page.get_by_role('link',name='Start with Codex',exact=True).click()
        assert page.url.endswith('#install')
        page.get_by_role('button',name='Copy installation commands',exact=True).click()
        expect(page.locator('#announcement')).to_contain_text('commands copied')
        clipboard=page.evaluate('navigator.clipboard.readText()')
        assert 'codex plugin marketplace add GhostlyGawd/engineering-board' in clipboard
        page.get_by_role('button',name='Copy initialization prompt',exact=True).click()
        expect(page.locator('#announcement')).to_contain_text('prompt copied')
        summary=page.locator('summary').filter(has_text='If the board tools are missing')
        summary.focus(); page.keyboard.press('Enter')
        assert summary.locator('..').get_attribute('open') is not None
        assert 'new Codex session' in summary.locator('..').inner_text()
        search=page.get_by_role('searchbox')
        for query in ['B002','wrong lane','board-view/lifecycle-lanes']:
          search.fill(query)
          assert page.locator('.finding:visible').count()==1
          assert 'B002' in page.locator('.finding:visible').inner_text()
        search.fill('zzzz no record')
        assert page.get_by_text('No matching findings.',exact=True).is_visible()
        page.locator('[data-reset]').click()
        assert page.locator('.finding:visible').count()==3
        assert search.evaluate('(e)=>e===document.activeElement')
        for id in ['B001','B002','B003','H001']:
          link=page.locator(f'.finding[data-select="{id}"]') if id!='H001' else page.get_by_role('link',name='Overview',exact=True)
          link.focus(); page.keyboard.press('Enter')
          panel=page.locator(f'#entry-{id}')
          assert panel.is_visible() and panel.evaluate('(e)=>e===document.activeElement')
          if id!='H001': assert link.get_attribute('aria-current')=='true'
          assert panel.evaluate('(e)=>getComputedStyle(e).outlineStyle')!='none'
          panel.get_by_role('link',name='Open source record').click()
          assert page.url.endswith(f'/source/{id}.html')
          assert 'Synthetic example' in page.locator('main').text_content() and 'Read-only' in page.locator('main').text_content()
          if id=='H001':
            for text in ['Proposed hypothesis','Independent filtering errors.','All adapters use the same rule.','No outcome recorded.']:
              assert text in page.locator('main').text_content()
          md=page.get_by_text('Read the original Markdown',exact=True)
          md.focus(); page.keyboard.press('Space')
          assert md.locator('..').get_attribute('open') is not None
          assert id in md.locator('..').inner_text()
          assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
          if width==390 and id=='B002': page.screenshot(path=str(OUT/f'verifier-mobile-source-{theme}.png'),full_page=True)
          page.get_by_role('link',name='Back to finding' if id!='H001' else 'Back to investigation',exact=True).click()
          assert page.locator(f'#entry-{id}').is_visible()
          assert page.evaluate('document.documentElement.dataset.theme')==theme
        page.goto(BASE)
        page.keyboard.press('Tab')
        assert page.evaluate('document.activeElement.textContent')=='Skip to content'
        page.keyboard.press('Enter')
        assert page.url.endswith('#main')
        page.add_script_tag(path=AXE)
        axe=page.evaluate('async()=>{let r=await axe.run();return {version:axe.version,violations:r.violations,incomplete:r.incomplete.map(x=>({id:x.id,impact:x.impact,nodes:x.nodes.map(n=>({target:n.target,summary:n.failureSummary}))}))}}')
        page.screenshot(path=str(OUT/f'verifier-{width}-{theme}.png'),full_page=True)
        results.append({'viewport':[width,height],'theme':theme,'js':True,'source_roundtrips':['B001','B002','B003','H001'],'search':['id','title','path','empty','reset'],'copy':True,'keyboard':'skip, finding enter, focused panel, reset focus, source disclosure space, recovery disclosure enter','overflow':False,'page_errors':errors,'external_requests':[r for r in requests if not r.startswith(BASE)],'axe':axe})
        assert not errors
        c.close()
      c=browser.new_context(viewport={'width':width,'height':height},java_script_enabled=False)
      page=c.new_page(); page.goto(BASE)
      assert page.locator('[data-panel]:visible').count()==4
      assert page.locator('.js-only:visible').count()==0
      assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
      page.get_by_role('link',name='Start with Codex',exact=True).click()
      assert page.url.endswith('#install')
      for id in ['B001','B002','B003','H001']:
        page.locator(f'#entry-{id}').get_by_role('link',name='Open source record').click()
        assert 'Read-only' in page.locator('main').text_content()
        page.get_by_role('link',name='Back to finding' if id!='H001' else 'Back to investigation',exact=True).click()
        assert page.locator(f'#entry-{id}').is_visible()
      page.screenshot(path=str(OUT/f'verifier-{width}-nojs.png'),full_page=True)
      results.append({'viewport':[width,height],'js':False,'all_four_panels_visible':True,'source_roundtrips':['B001','B002','B003','H001'],'install_anchor':True,'overflow':False})
      c.close()
    browser.close()
(OUT/'verifier-results.json').write_text(json.dumps(results,indent=2))
print(json.dumps([{k:v for k,v in r.items() if k!='axe'}|({'axe_violations':len(r['axe']['violations']),'axe_incomplete':r['axe']['incomplete']} if 'axe' in r else {}) for r in results],indent=2))
