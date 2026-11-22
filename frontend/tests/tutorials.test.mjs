import { test } from 'node:test';
import assert from 'node:assert/strict';
import { tutorialMarkdown } from '../lib/tutorial-markdown.mjs';
import { tutorialHead } from '../lib/presentation/tutorials.mjs';

test('YouTube iframe embeds render responsively in Markdown and legacy posts', () => {
  for (const format of ['markdown', 'legacy']) {
    const {html} = tutorialMarkdown('<iframe width="1059" height="595" src="https://www.youtube.com/embed/wORBqbpaY3w" title="Java Records in SpringBoot" onload="alert(1)" srcdoc="unsafe" style="position:fixed" allowfullscreen></iframe>', format);
    assert.match(html, /<iframe[^>]+src="https:\/\/www.youtube.com\/embed\/wORBqbpaY3w"/);
    assert.match(html, /title="Java Records in SpringBoot"/);
    assert.match(html, /width:100%/);
    assert.match(html, /aspect-ratio:16 \/ 9/);
    assert.match(html, /allowfullscreen/);
    assert.doesNotMatch(html, /onload|srcdoc|position|1059|595/);
  }
  assert.match(tutorialMarkdown('<iframe src="https://www.youtube-nocookie.com/embed/wORBqbpaY3w?start=30"></iframe>').html, /<iframe/);
});

test('untrusted iframe sources are removed and code examples remain escaped', () => {
  for (const src of ['https://evil.example/embed/wORBqbpaY3w', 'https://www.youtube.com.evil.example/embed/wORBqbpaY3w', '//www.youtube.com/embed/wORBqbpaY3w', 'javascript:alert(1)', 'https://www.youtube.com/watch?v=wORBqbpaY3w', 'https://www.youtube.com/embed/invalid', 'https://user@www.youtube.com/embed/wORBqbpaY3w']) {
    assert.doesNotMatch(tutorialMarkdown(`<iframe src="${src}" srcdoc="unsafe"></iframe>`).html, /<iframe|srcdoc/);
  }
  assert.doesNotMatch(tutorialMarkdown('```html\n<iframe src="https://www.youtube.com/embed/wORBqbpaY3w"></iframe>\n```').html, /<iframe/);
});

test('tutorial Markdown sanitizes HTML and preserves highlighted code and tables', () => {
  const {html,toc}=tutorialMarkdown('## Install\n\n```javascript\nconst secret = "<script>";\n```\n\n| One | Two |\n| --- | --- |\n| a | b |\n\n<script>alert(1)</script><img src="x" onerror="alert(2)">[bad](javascript:alert(3))');
  assert.equal(toc[0].id,'section-1');
  assert.match(html,/hljs-keyword/);assert.match(html,/<table>/);
  assert.doesNotMatch(html,/<script>|onerror=|href="javascript:/);
  assert.match(html,/&lt;script&gt;/);
});
test('legacy content is sanitized without losing existing paragraphs',()=>{
  assert.match(tutorialMarkdown('<p>Existing article</p>','legacy').html,/<p>Existing article<\/p>/);
});
test('code blocks have a language toolbar, line count, accessible scroll area and safe copy control',()=>{
  const {html}=tutorialMarkdown('```java\nQueue<String> applications = new LinkedList<>();\napplications.offer("APP-001");\nSystem.out.println(applications.poll());\n```');
  assert.match(html,/class="tutorial-code-block"/);
  assert.match(html,/class="tutorial-code-language">Java/);
  assert.match(html,/3 lines/);
  assert.match(html,/<button type="button"[^>]*data-copy-tutorial-code/);
  assert.match(html,/tabindex="0" aria-label="Java code example"/);
  assert.match(html.replace(/<[^>]+>/g,''),/Queue&lt;String&gt;/);
});
test('social metadata has canonical URL and safely encoded article structured data',()=>{
  const head=tutorialHead({tutorial:{title:'Demo </script><script>bad</script>',canonical:'https://melkaa.com/tutorials/demo/',image:'/media/demo.jpg',description:'A guide',published:'2026-11-09',updated:'2026-11-09',author:'Simon'}});
  assert.match(head,/rel="canonical"/);assert.match(head,/og:image/);assert.match(head,/https:\/\/melkaa.com\/media\/demo.jpg/);
  assert.doesNotMatch(head,/<script>bad/);assert.match(head,/\\u003c/);
});

test('published content renders into homepage cards and the article reader without exposing authored markup', async () => {
  const { tutorialNodes, recentTutorialNodes } = await import('../lib/presentation/tutorials.mjs');
  const post = {id:7,title:'Caching <script>alert(1)</script>',summary:'A practical introduction',author:'Simon',author_bio:'Backend developer',category:'Java',difficulty:'Beginner',minutes:4,tags:['Redis'],url:'/tutorials/caching/',canonical:'https://melka.test/tutorials/caching/',content:'## Configure Redis\n\nCache a response.',format:'markdown',published:'2026-11-15',updated:'2026-11-15',likes:0,views:0,related:[]};
  const home = recentTutorialNodes({recent_tutorials:[post]})[0].text;
  assert.match(home,/home-post-featured/);
  assert.match(home,/Read more/);
  assert.doesNotMatch(home,/<details|Cache a response|class="tutorial-prose"/);
  assert.match(home,/A practical introduction/);
  assert.match(home,/href="\/tutorials\/caching\/"/);
  assert.doesNotMatch(home,/<script>alert/);
  const article = tutorialNodes({tutorial:post},'csrf').find(node => node.args === 'content').body[0].text;
  assert.match(article,/aria-label="On this page"/);
  assert.match(article,/href="#section-1"/);
  assert.match(article,/tutorial-cover-fallback/);
  assert.match(article,/About the author/);
  assert.match(article,/Backend developer/);
  assert.match(article,/tutorial-rail/);
  assert.match(article,/aria-label="Blog posts"/);
  assert.match(article,/href="\/tutorials\/\?browse=1"/);
  assert.doesNotMatch(article,/<script>alert/);
  const withCover = recentTutorialNodes({recent_tutorials:[{...post,image:'/media/redis.jpg'}]})[0].text;
  assert.match(withCover,/<img[^>]+src="\/media\/redis.jpg"/);
});
