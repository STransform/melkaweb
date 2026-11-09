(function () {
  'use strict';
  const root = document.querySelector('[data-tutorial-id]');
  if (!root) return;
  const feedback = root.querySelector('[data-feedback]');
  const id = root.dataset.tutorialId;
  let csrf = root.dataset.csrf;
  async function post(action, values) {
    if (!csrf) csrf = (await fetch('/api/frontend/csrf/', {cache:'no-store'}).then(r => r.json())).csrfToken;
    const response = await fetch('/api/frontend/blogs/' + id + '/' + action + '/', {method:'POST', headers:{'X-CSRFToken':csrf}, body:new URLSearchParams(values), signal:AbortSignal.timeout(15000)});
    const data = await response.json();
    if (!response.ok) throw new Error(data.detail || Object.values(data.errors || {}).flat().join(' ') || 'Please try again.');
    return data;
  }
  const like = root.querySelector('[data-like]');
  function counts(data) {
    if (data.views != null) root.querySelector('[data-views]').textContent = data.views;
    if (data.likes != null) root.querySelector('[data-likes]').textContent = data.likes;
    if (data.liked != null) like.setAttribute('aria-pressed', String(data.liked));
  }
  const parameters = new URLSearchParams(location.search);
  let referrer = '';
  try { referrer = new URL(document.referrer).hostname; } catch (_) {}
  const source = parameters.get('utm_source') || referrer || 'direct';
  // Serialize the initial visit before likes so a first-time visitor uses one session.
  const ready = post('visit', {source}).then(counts).catch(() => {});
  like.addEventListener('click', async function () {
    like.disabled = true;
    try { await ready; counts(await post('like', {liked:String(like.getAttribute('aria-pressed') !== 'true')})); feedback.textContent = ''; }
    catch (error) { feedback.textContent = error.message; }
    finally { like.disabled = false; }
  });
  let visibleSeconds = 0, engaged = false;
  const engagementTimer = setInterval(function () {
    if (document.visibilityState === 'visible') visibleSeconds++;
    if (visibleSeconds >= 30 && !engaged) {
      engaged = true; clearInterval(engagementTimer);
      ready.then(() => post('visit', {source, engaged:'true'})).catch(() => {});
    }
  }, 1000);
  root.querySelector('[data-copy-link]').addEventListener('click', async function () {
    try { await navigator.clipboard.writeText(root.dataset.canonical); feedback.textContent = 'Link copied. Ready to share!'; }
    catch (_) { feedback.textContent = 'Copy this link: ' + root.dataset.canonical; }
  });
  root.querySelectorAll('.tutorial-prose pre').forEach(function (pre) {
    const code = pre.querySelector('code');
    if (!code) return;
    const button = pre.closest('.tutorial-code-block')?.querySelector('[data-copy-tutorial-code]') || document.createElement('button');
    button.type = 'button'; button.className = 'tutorial-copy-code'; button.textContent = 'Copy code';
    button.addEventListener('click', async function () {
      try { await navigator.clipboard.writeText(code.textContent); button.textContent = 'Copied!'; setTimeout(() => { button.textContent = 'Copy code'; }, 1800); }
      catch (_) { feedback.textContent = 'Clipboard unavailable. Select and copy the code manually.'; }
    });
    if (!button.isConnected) pre.appendChild(button);
  });
  const form = root.querySelector('[data-comment-form]');
  form.addEventListener('submit', async function (event) {
    event.preventDefault();
    const button = form.querySelector('button');
    const status = form.querySelector('[data-comment-status]');
    button.disabled = true;
    try { await ready; const data = await post('comments', new FormData(form)); status.textContent = data.message; form.reset(); }
    catch (error) { status.textContent = error.message; }
    finally { button.disabled = false; }
  });
  const progress = root.querySelector('.tutorial-progress');
  const article = root.querySelector('.tutorial-prose');
  function updateProgress() {
    const rect = article.getBoundingClientRect();
    progress.style.width = Math.max(0, Math.min(100, (innerHeight - rect.top) / Math.max(1, rect.height) * 100)) + '%';
  }
  addEventListener('scroll', updateProgress, {passive:true}); updateProgress();
})();
