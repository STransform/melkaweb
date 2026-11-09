"""Run browser UI comparisons on an isolated fixture database."""
import os
from pathlib import Path
import subprocess
import tempfile
import time
import urllib.request

root=Path(__file__).resolve().parents[1]
with tempfile.TemporaryDirectory(prefix='melkaweb-browser-') as work:
    work=Path(work)
    (work/'melka_browser_settings.py').write_text("from core.frontend_test_settings import *\nDATABASES={'default':{'ENGINE':'django.db.backends.sqlite3','NAME':"+repr(str(work/'browser.sqlite3'))+"}}\nCSRF_TRUSTED_ORIGINS=['http://127.0.0.1:3101']\n")
    env={**os.environ,'DJANGO_SETTINGS_MODULE':'melka_browser_settings','PYTHONPATH':str(work)+':'+str(root),'DJANGO_ORIGIN':'http://127.0.0.1:18001','ODOO_URL':'http://127.0.0.1:1','ODOO_TIMEOUT':'1','PLAYWRIGHT_BROWSERS_PATH':'/tmp/melkaweb-browsers','MELKA_BASELINE_ORIGIN':'http://127.0.0.1:18001','MELKA_FRONTEND_ORIGIN':'http://127.0.0.1:3101'}
    python=str(root/'.venv/bin/python')
    subprocess.run([python,'manage.py','migrate','--noinput'],cwd=root,env=env,check=True,stdout=subprocess.DEVNULL)
    seed="""
import django
django.setup()
from django.contrib.auth import get_user_model
from core.models import Pages,Settings
from task_manager.models import Task
get_user_model().objects.create_superuser(email='browser@example.com',password='Browser-example-password-42',first_name='Browser',last_name='Tester')
Pages.objects.create()
Settings.objects.create(title='Melka tech',working_hours='9–5')
"""
    subprocess.run([python,'-c',seed],cwd=root,env=env,check=True,stdout=subprocess.DEVNULL)
    commands=[([python,'manage.py','runserver','127.0.0.1:18001','--noreload'],root),(['node','node_modules/next/dist/bin/next','start','--hostname','127.0.0.1','--port','3101'],root/'frontend')]
    processes=[]; logs=[]
    try:
        for index,(command,cwd) in enumerate(commands):
            log=open(f'/tmp/melka-browser-server-{index}.log','w')
            logs.append(log)
            processes.append(subprocess.Popen(command,cwd=cwd,env=env,stdout=log,stderr=subprocess.STDOUT))
        for attempt in range(60):
            if any(p.poll() is not None for p in processes):raise RuntimeError('Preview server exited early')
            try:
                with urllib.request.urlopen('http://127.0.0.1:3101/',timeout=5) as response:
                    if response.status==200:break
            except OSError:time.sleep(.5)
        else:raise RuntimeError('Preview servers did not start')
        subprocess.run(['node',env.get('MELKA_BROWSER_TEST', 'tests/browser.mjs')],cwd=root/'frontend',env=env,check=True)
    finally:
        for process in processes:
            if process.poll() is None:process.terminate()
        for process in processes:process.wait(timeout=10)
        for log in logs:log.close()
