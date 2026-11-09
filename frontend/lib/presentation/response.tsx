import { createRequire } from 'node:module';
import React from 'react';
import parse, { Element } from 'html-react-parser';
import { renderPresentation } from './render.mjs';
import { tutorialHead } from './tutorials.mjs';

// Route handlers return a complete React-rendered document, which also permits
// exact propagation of Django's status, redirects, session and CSRF cookies.
const require = createRequire(import.meta.url);
const { renderToStaticMarkup } = require('react-dom/server') as { renderToStaticMarkup: (node: React.ReactNode) => string };

export function presentationDocument(payload: Parameters<typeof renderPresentation>[0]) {
  const source = renderPresentation(payload);
  const tree = parse(source.replace(/<!doctype[^>]*>/gi, ''), {
    replace(node) {
      if (node instanceof Element) {
        // React ignores string event handlers. Restore trusted presentation
        // handlers through the small bootstrap below after the DOM is ready.
        for (const name of Object.keys(node.attribs)) {
          if (/^on[a-z]+$/.test(name)) {
            node.attribs[`data-melka-${name}`] = node.attribs[name];
            delete node.attribs[name];
          }
        }
      }
    },
  });
  let html = '<!DOCTYPE html>' + renderToStaticMarkup(React.createElement(React.Fragment, null, tree));
  if (payload.context.tutorial || payload.context.tutorial_library) {
    html = html.replace(/<title[^>]*>[\s\S]*?<\/title>/gi, '').replace(/<meta\b[^>]*name="description"[^>]*>/gi, '');
    html = html.replace('</head>', tutorialHead(payload.context) + '</head>');
  }
  if (payload.template === 'front/about.html') {
    html = html.replace('</body>', `<style>
      .about-content .about-row:not(:has(.gallery-image)) > .col-lg-6:has(.image-gallery-container){display:none}
      .about-content .about-row:not(:has(.gallery-image)) > .about-text-section{width:100%;padding-right:0}
    </style></body>`);
  }
  if (payload.template === 'front/index.html') {
    html = html.replace('</body>', '<link rel="stylesheet" href="/static/front/css/hero-refresh.css"></body>');
  }
  const bootstrap = `<script data-melka-runtime>
(function(){
  function bind(){
    document.querySelectorAll('*').forEach(function(element){
      Array.from(element.attributes).forEach(function(attribute){
        if(attribute.name.indexOf('data-melka-on')!==0)return;
        element.setAttribute(attribute.name.slice(11),attribute.value);
        element.removeAttribute(attribute.name);
      });
    });
    document.querySelectorAll('form[method="post" i]').forEach(function(form){
      if(!form.querySelector('[name="csrfmiddlewaretoken"]')){
        var field=document.createElement('input');field.type='hidden';field.name='csrfmiddlewaretoken';field.value=${JSON.stringify(payload.csrfToken || '')};form.appendChild(field);
      }
    });
  }
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',bind);else bind();
})();
</script>`;
  html = html.replace(/<head([^>]*)>/i, '<head$1><meta name="generator" content="Next.js / React">');
  html = html.includes('</body>') ? html.replace('</body>', bootstrap+'</body>') : html+bootstrap;
  return html;
}
