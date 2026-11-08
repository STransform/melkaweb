import { chromium } from '@playwright/test';
import assert from 'node:assert/strict';
import { writeFile } from 'node:fs/promises';
const oldOrigin = process.env.MELKA_BASELINE_ORIGIN;
const newOrigin = process.env.MELKA_FRONTEND_ORIGIN;
const browser = await chromium.launch({ headless: true, args: ['--no-sandbox'] });
const results = {};
try {
  for (const [version, origin] of [['original',oldOrigin],['next',newOrigin]]) {
    const context = await browser.newContext({ viewport: {width:1440,height:1000}, reducedMotion:'reduce' });
    const page = await context.newPage();
    const errors=[];
    page.on('pageerror',error=>errors.push(error.message));
    const response = await page.goto(origin+'/',{waitUntil:'load',timeout:60000});
    assert.equal(response.status(),200);
    if(version==='next') assert.equal(response.headers()['x-melka-frontend'],'Next.js');
    await page.addStyleTag({content:'*,*::before,*::after{animation:none!important;transition:none!important;caret-color:transparent!important}'});
    await page.evaluate(()=>document.fonts.ready);
    results[version] = await page.evaluate(()=>Object.fromEntries(['#header','.hero-section','.hero-title','.hero-subtitle','.hero-mockup','.hero-buttons'].map(selector=>{
      const node=document.querySelector(selector);if(!node)return[selector,null];
      const rect=node.getBoundingClientRect(),style=getComputedStyle(node);
      return[selector,{text:node.tagName==='IMG'?null:node.textContent.replace(/\s+/g,' ').trim(),x:Math.round(rect.x),y:Math.round(rect.y),width:Math.round(rect.width),height:Math.round(rect.height),font:style.font,fontSize:style.fontSize,color:style.color,background:style.backgroundImage}];
    })));
    await page.screenshot({path:`/tmp/melka-${version}-desktop.png`,animations:'disabled'});
    await page.setViewportSize({width:390,height:844});
    await page.locator('.mobile-toggle').click();
    await page.waitForTimeout(150);
    assert.ok(await page.locator('.header-nav-main').evaluate(node=>node.classList.contains('show')),`${version} mobile menu`);
    await page.screenshot({path:`/tmp/melka-${version}-mobile.png`,animations:'disabled'});
    await page.setViewportSize({width:1440,height:1000});
    await page.goto(origin+'/accounts/login/',{waitUntil:'load'});
    await page.locator('input[name=email]').fill('browser@example.com');
    await page.locator('input[name=password]').fill('Browser-example-password-42');
    await Promise.all([page.waitForURL('**/dashboard/',{timeout:30000}),page.locator('form:has(input[name=password]) button[type=submit]').click()]);
    assert.ok(await page.locator('.main-content').count(),`${version} authenticated dashboard`);
    await page.addStyleTag({content:'*,*::before,*::after{animation:none!important;transition:none!important}'});
    await page.screenshot({path:`/tmp/melka-${version}-dashboard.png`,animations:'disabled'});
    await page.goto(origin+'/dashboard/create/CompanyValues/',{waitUntil:'load'});
    await page.locator('[name=title_en]').fill(`${version} browser value`);
    await page.locator('[name=content_en]').fill('Created through the original workflow.');
    await Promise.all([page.waitForURL('**/dashboard/list/CompanyValues/'),page.locator('form:has([name=title_en]) button[type=submit]').click()]);
    const edit=page.locator('a[href*="/dashboard/change/CompanyValues/"]').last();
    await edit.click();
    assert.equal(await page.locator('[name=title_en]').inputValue(),`${version} browser value`);
    results[version].errors=errors;
    await context.close();
    process.stdout.write(`PASS ${version}: desktop/mobile UI, navigation, login, dashboard and CRUD\n`);
  }
  const oldErrors=results.original.errors,newErrors=results.next.errors;
  delete results.original.errors;delete results.next.errors;
  assert.deepEqual(results.next,results.original,'Homepage geometry, typography and colors must match');
  const regressions=newErrors.filter(error=>!oldErrors.includes(error));
  assert.deepEqual(regressions,[],'No additional browser script errors');
  await writeFile('/tmp/melka-browser-results.json',JSON.stringify({geometry:results,oldErrors,newErrors},null,2));
  process.stdout.write('PASS identical homepage geometry, typography and colors; no additional script errors\n');
} finally { await browser.close(); }
