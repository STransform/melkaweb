"""Opt-in browser test against real Next.js + Django, using an isolated test DB.

Build frontend first, then run with MELKA_RUN_PUBLISH_BROWSER=1.
"""
import os
import socket
import subprocess
import tempfile
import time
import urllib.request
from pathlib import Path
from unittest import skipUnless
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from blogs.models import BlogCategory, Blog
from core.models import Pages, Settings


@skipUnless(os.environ.get('MELKA_RUN_PUBLISH_BROWSER') == '1', 'Opt-in Next.js browser integration')
class PublishingBrowserTests(StaticLiveServerTestCase):
    def test_editor_publish_and_public_article(self):
        get_user_model().objects.create_superuser('publish-browser@example.com', 'Publish-browser-password-42', 'Browser', 'Author')
        BlogCategory.objects.create(name='Technology')
        Settings.objects.create(title='Publishing verification', working_hours='9–5')
        Pages.objects.create()
        with socket.socket() as sock:
            sock.bind(('127.0.0.1', 0))
            port = sock.getsockname()[1]
        origin = f'http://127.0.0.1:{port}'
        env = {**os.environ, 'DJANGO_ORIGIN': self.live_server_url, 'MELKA_FRONTEND_ORIGIN': origin}
        log = tempfile.TemporaryFile(mode='w+')
        mode = 'dev' if os.environ.get('MELKA_PUBLISH_DEV') == '1' else 'start'
        if mode == 'dev':
            env['MELKA_NEXT_DIST_DIR'] = '.next-publish-check'
        process = subprocess.Popen(['node', 'node_modules/next/dist/bin/next', mode, '--hostname', '127.0.0.1', '--port', str(port)], cwd=Path(settings.BASE_DIR)/'frontend', env=env, stdout=log, stderr=log)
        try:
            for _ in range(100):
                try:
                    urllib.request.urlopen(origin+'/accounts/login/', timeout=1)
                    break
                except Exception:
                    if process.poll() is not None:
                        log.seek(0)
                        self.fail(log.read())
                    time.sleep(.2)
            with self.settings(CSRF_TRUSTED_ORIGINS=[*settings.CSRF_TRUSTED_ORIGINS, origin]):
                result = subprocess.run(['node', 'tests/publishing-browser.mjs'], cwd=Path(settings.BASE_DIR)/'frontend', env=env, capture_output=True, text=True, timeout=120)
            log.seek(0)
            self.assertEqual(result.returncode, 0, result.stdout+'\n'+result.stderr+'\n'+log.read())
            self.assertTrue(Blog.objects.filter(title='Browser tutorial publishing check',published_status='Published').exists())
            self.assertEqual(Blog.objects.count(), 1)
        finally:
            process.terminate()
            try:
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()
            log.close()
