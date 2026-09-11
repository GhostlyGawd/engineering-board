import json
from pathlib import Path
from playwright.sync_api import sync_playwright
OUT=Path(__file__).parent
results=[]
with sync_playwright() as p:
 b=p.chromium.connect_over_cdp('http://127.0.0.1:51483')
 context=b.contexts[0]; page=context.pages[0]
 errors=[]; page.on('pageerror',lambda err:errors.append(str(err)))
 for route,name in [('/','site'),('/board.html','board')]:
  for width in [1448,390]:
   page.set_viewport_size({'width':width,'height':1000 if width==1448 else 844})
   page.goto('http://127.0.0.1:51330'+route)
   if page.locator('html').get_attribute('data-theme')=='light': page.locator('.theme').click()
   for theme in ['dark','light']:
    if theme=='light': page.locator('.theme').click()
    page.evaluate('document.fonts.ready'); page.screenshot(path=str(OUT/f'review-{name}-{width}-{theme}.png'))
    results.append({'page':name,'width':width,'theme':theme,**page.evaluate('({width:innerWidth,scrollWidth:document.documentElement.scrollWidth,main:document.querySelectorAll("main").length,font:getComputedStyle(document.body).fontFamily})')})
 page.goto('http://127.0.0.1:51330/')
 page.locator('.finding[data-select="B001"]').click()
 page.locator('#entry-B001 a[href="example/B001.html"]').click()
 results.append({'source':page.url,'synthetic':page.get_by_text('Synthetic example · Read-only').count()})
 page.locator('a[href="../index.html#entry-B001"]').first.click()
 results.append({'returned':page.url,'panel_visible':page.locator('#entry-B001').is_visible()})
 page.locator('#finding-search').fill('zzzzz-no-match')
 results.append({'site_no_results':page.locator('.no-results').is_visible()})
 page.locator('[data-reset]').click()
 results.append({'site_reset':page.locator('.finding:visible').count()})
 page.goto('http://127.0.0.1:51330/board.html')
 page.locator('#eb-search').fill('B001')
 link=page.locator('a.cid').filter(has_text='B001').first
 results.append({'B001_href':link.get_attribute('href')})
 page.locator('#eb-search').fill('zzzzz-no-match')
 results.append({'board_no_results':page.get_by_text('No entries match',exact=False).is_visible()})
 results.append({'errors':errors})
 nojs=b.new_context(java_script_enabled=False,viewport={'width':390,'height':844})
 q=nojs.new_page()
 for route,name in [('/','site'),('/board.html','board')]:
  q.goto('http://127.0.0.1:51330'+route)
  q.screenshot(path=str(OUT/f'review-{name}-390-nojs.png'))
  results.append({'nojs':name,'main_visible':q.locator('main').is_visible(),'theme_hidden':not q.locator('.theme').is_visible(),'overflow':q.evaluate('document.documentElement.scrollWidth>innerWidth')})
 nojs.close()
(OUT/'review-browser-results.json').write_text(json.dumps(results,indent=2))
print(json.dumps(results,indent=2))
