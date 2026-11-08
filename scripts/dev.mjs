import { spawn } from 'node:child_process';
import { existsSync } from 'node:fs';
import { fileURLToPath } from 'node:url';

const root = fileURLToPath(new URL('../', import.meta.url));
const backendPort = process.env.DJANGO_PORT || '8000';
const frontendPort = process.env.PORT || '3000';
const python = process.env.PYTHON || (existsSync(`${root}.venv/bin/python`) ? `${root}.venv/bin/python` : 'python3');
const next = `${root}frontend/node_modules/next/dist/bin/next`;
if (!existsSync(next)) {
  console.error('Install frontend dependencies first: npm --prefix frontend ci');
  process.exit(1);
}
const origins = [process.env.FRONTEND_ORIGINS, `http://localhost:${frontendPort}`, `http://127.0.0.1:${frontendPort}`].filter(Boolean).join(',');
const backend = spawn(python, ['manage.py', 'runserver', `127.0.0.1:${backendPort}`, '--noreload'], {
  cwd: root, stdio: 'inherit', env: { ...process.env, FRONTEND_ORIGINS: origins },
});
const frontend = spawn(process.execPath, [next, 'dev', '--hostname', '127.0.0.1', '--port', frontendPort], {
  cwd: `${root}frontend`, stdio: 'inherit', env: { ...process.env, DJANGO_ORIGIN: `http://127.0.0.1:${backendPort}` },
});
let stopping = false;
function stop(code = 0) {
  if (stopping) return;
  stopping = true;
  backend.kill('SIGTERM'); frontend.kill('SIGTERM');
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
