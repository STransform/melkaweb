import { chromium } from '@playwright/test';
import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import { tutorialNodes } from '../lib/presentation/tutorials.mjs';

const browser = await chromium.launch({ executablePath:process.env.MELKA_BROWSER_EXECUTABLE || undefined, headless:true, args:['--no-sandbox'] });
try {
  const page = await browser.newPage();
  // Check geometry without depending on YouTube's network or playback state.
  await page.route('https://www.youtube.com/**', route => route.fulfill({body:'Video player'}));
  const css = await readFile(new URL('../../static/front/css/tutorials.css', import.meta.url), 'utf8');
  const post = {id:1,title:'Video tutorial',author:'Simon',tags:[],format:'markdown',
    content:'## Watch the lesson\n\n<iframe width="1059" height="595" src="https://www.youtube.com/embed/wORBqbpaY3w" title="Java Records in SpringBoot"></iframe>',
    published:'2026-11-22',updated:'2026-11-22',canonical:'https://melka.test/tutorials/video/',url:'/tutorials/video/',comments:[],related:[],posts:[]};
  const article = tutorialNodes({tutorial:post},'csrf').find(n=>n.args==='content').body[0].text;
  for (const width of [1920,1440,1024,768,390,320]) {
    await page.setViewportSize({width,height:1000});
    await page.setContent(`<style>body{margin:0}${css}</style>${article}`);
    const geometry = await page.locator('.tutorial-video iframe').evaluate(frame => {
      const rect = frame.getBoundingClientRect();
      const column = frame.closest('.tutorial-reading-main').getBoundingClientRect();
      return {left:rect.left,right:rect.right,width:rect.width,height:rect.height,columnRight:column.right,
        pageWidth:document.documentElement.scrollWidth, viewport:innerWidth};
    });
    assert.ok(geometry.left >= 0 && geometry.right <= width, `Player within viewport at ${width}`);
    assert.ok(geometry.right <= geometry.columnRight + 1, `Player within article at ${width}`);
    assert.ok(Math.abs(geometry.width/geometry.height - 16/9) < .01, `16:9 player at ${width}`);
    assert.ok(geometry.pageWidth <= geometry.viewport, `No horizontal page overflow at ${width}`);
    assert.equal(await page.getByRole('link',{name:'Watch on YouTube',exact:true}).getAttribute('href'), 'https://www.youtube.com/watch?v=wORBqbpaY3w');
    console.log(`Video layout passed at ${width}px`);
  }
} finally { await browser.close(); }
