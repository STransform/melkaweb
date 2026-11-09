import { test } from 'node:test';
import assert from 'node:assert/strict';
import { tutorialMarkdown } from '../lib/tutorial-markdown.mjs';
import { tutorialHead } from '../lib/presentation/tutorials.mjs';

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
