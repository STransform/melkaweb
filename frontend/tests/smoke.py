"""Start isolated local servers and exercise the built frontend against MySQL.

Run from the repository root after `npm --prefix frontend run build`.
Uses ports 18001/3101, and does not submit valid forms or alter content records.
"""
import http.cookiejar
import json
import os
from pathlib import Path
import subprocess
import time
import urllib.error
import urllib.parse
import urllib.request

root = Path(__file__).resolve().parents[2]
origin = 'http://127.0.0.1:3101'
env = {**os.environ, 'FRONTEND_ORIGINS': origin, 'DJANGO_ORIGIN': 'http://127.0.0.1:18001'}
processes = []
logs = []
try:
    for name, command, cwd in [
        ('django', [str(root / '.venv/bin/python'), 'manage.py', 'runserver', '127.0.0.1:18001', '--noreload'], root),
        ('next', ['node', 'node_modules/next/dist/bin/next', 'start', '--hostname', '127.0.0.1', '--port', '3101'], root / 'frontend'),
    ]:
        log = open(f'/tmp/melkaweb-smoke-{name}.log', 'w+')
        logs.append(log)
        processes.append(subprocess.Popen(command, cwd=cwd, env=env, stdout=log, stderr=subprocess.STDOUT))
    client = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
    def request(path, data=None, headers=None, raw=False):
        req = urllib.request.Request(origin + path, data=data, headers=headers or {})
        try:
            with client.open(req, timeout=20) as response:
                body = response.read()
                return response.status, body if raw else body.decode(), response.headers
        except urllib.error.HTTPError as error:
            return error.code, error.read().decode(), error.headers
    for attempt in range(40):
        if any(p.poll() is not None for p in processes):
            raise RuntimeError('A preview server exited early')
        try:
            status, body, _ = request('/api/frontend/site/')
            if status == 200:
                break
        except (OSError, TimeoutError):
            pass
        time.sleep(.5)
    else:
        raise RuntimeError('Servers did not become ready')
    paths = ['/', '/news/news_view/', '/blogs/blogs/', '/documents/list-documents/',
             '/about-us/about/', '/about-us/technology/', '/gallery-images/', '/events/', '/bids/',
             '/contact-us/', '/search/?searched_item=technology', '/ax/', '/ox/news/news_view/']
    for path in paths:
        status, body, _ = request(path)
        assert status == 200, (path, status, body[:300])
        assert '/_next/' in body and 'site-header' in body, f'{path} did not use React shell'
        print(f'PASS React page {path}')
    status, _, _ = request('/accounts/login/')
    assert status == 200, ('Django login proxy', status)
    print('PASS existing Django login through Next.js')
    status, body, _ = request('/static/front/hero/mock3.jpg', raw=True)
    assert status == 200 and body, ('static image proxy', status)
    print('PASS static image forwarded as binary content')
    status, body, _ = request('/api/frontend/csrf/')
    assert status == 200
    token = json.loads(body)['csrfToken']
    status, body, _ = request('/api/frontend/contact/', data=urllib.parse.urlencode({'email': 'invalid'}).encode(), headers={'X-CSRFToken': token, 'Origin': origin, 'Content-Type': 'application/x-www-form-urlencoded'})
    assert status == 400 and 'errors' in json.loads(body), (status, body[:300])
    print('PASS same-origin CSRF and backend validation through Next.js')
    status, _, _ = request('/api/frontend/contact/', data=b'')
    assert status == 403
    print('PASS missing CSRF token rejected')
    status, _, _ = request('/news/999999999/')
    assert status == 404
    print('PASS missing article returns 404')
except Exception:
    for log in logs:
        log.flush(); log.seek(0); print(log.read()[-6000:])
    raise
finally:
    for process in processes:
        if process.poll() is None:
            process.terminate()
    for process in processes:
        process.wait(timeout=10)
    for log in logs:
        log.close()
