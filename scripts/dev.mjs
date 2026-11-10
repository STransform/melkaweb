import { spawn } from 'node:child_process';
import { existsSync } from 'node:fs';
import { fileURLToPath } from 'node:url';

const root = fileURLToPath(new URL('../', import.meta.url));
const backendPort = process.env.DJANGO_PORT || '8000';
const frontendPort = process.env.PORT || '8001';
const python = process.env.PYTHON || (existsSync(`${root}.venv/bin/python`) ? `${root}.venv/bin/python` : 'python3');
const next = `${root}frontend/node_modules/next/dist/bin/next`;
if (!existsSync(next)) {
  console.error('Install frontend dependencies first: npm --prefix frontend ci');
  process.exit(1);
}
const origins = [process.env.FRONTEND_ORIGINS, `http://localhost:${frontendPort}`, `http://127.0.0.1:${frontendPort}`].filter(Boolean).join(',');
const grouped = process.platform !== 'win32';
const backend = spawn(python, ['manage.py', 'runserver', `127.0.0.1:${backendPort}`], {
  cwd: root, stdio: 'inherit', detached: grouped, env: { ...process.env, FRONTEND_ORIGINS: origins },
});
const frontend = spawn(process.execPath, [next, 'dev', '--webpack', '--hostname', '127.0.0.1', '--port', frontendPort], {
  cwd: `${root}frontend`, stdio: 'inherit', detached: grouped, env: { ...process.env, DJANGO_ORIGIN: `http://127.0.0.1:${backendPort}` },
});
let stopping = false;
function stop(code = 0) {
  if (stopping) return;
  stopping = true;
  for (const child of [backend, frontend]) {
    if (!child.pid) continue;
    try {
      // Django's reloader and Next.js both spawn children. Stop only the
      // process groups started here, including those children.
      if (grouped) process.kill(-child.pid, 'SIGTERM');
      else child.kill('SIGTERM');
    } catch (error) {
      if (error.code !== 'ESRCH') console.error(error.message);
    }
  }
  process.exitCode = code;
}
for (const child of [backend, frontend]) {
  child.on('error', error => { console.error(error.message); stop(1); });
  child.on('exit', code => stop(code || 0));
}
process.on('SIGINT', () => stop());
process.on('SIGTERM', () => stop());
console.log(`MelkaTech frontend: http://127.0.0.1:${frontendPort}/`);
console.log(`Django backend: http://127.0.0.1:${backendPort}/`);
