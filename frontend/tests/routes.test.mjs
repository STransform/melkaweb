import { test } from 'node:test';
import assert from 'node:assert/strict';
import { localized, resolvePage, resources } from '../lib/routes.mjs';

test('public pages keep their existing URLs in all supported languages', () => {
  for (const path of ['', 'contact-us', 'search', ...Object.keys(resources), 'news/23', 'blogs/blogs/17']) {
    for (const locale of ['en', 'ax', 'ox']) {
      const result = resolvePage(localized(path ? `/${path}/` : '/', locale));
      assert.ok(result, `${locale}: ${path}`);
      assert.equal(result.locale, locale);
    }
  }
});
test('staff, authentication, uploads, CMS and job applications remain Django workflows', () => {
  for (const path of ['/accounts/login/', '/accounts/signup/', '/accounts/profile/12/', '/internalAdmin/', '/dashboard/', '/taskmanager/', '/vacancies/job_apply/9/', '/documents/pdf/report.pdf/', '/custom-cms-page/']) {
    assert.equal(resolvePage(path), null);
    assert.equal(resolvePage(`/ax${path}`), null);
  }
});
test('locale links preserve files, absolute URLs and already localized routes', () => {
  assert.equal(localized('/news/news_view/', 'ox'), '/ox/news/news_view/');
  for (const path of ['/media/report.pdf', '/static/logo.png', '/ox/news/9/', 'https://example.com/', '//example.com/file']) assert.equal(localized(path, 'ax'), path);
});
