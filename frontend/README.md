# MelkaTech Next.js frontend

This is an incremental migration, with real React pages backed by the existing
Django/MySQL application. Next.js is the public entry point. The Django database,
admin, permissions, sessions, uploaded files, and business logic stay in place.

## Run locally

Requires Node.js 20.9+ and the existing Python virtual environment.
From the repository root:

```bash
source .venv/bin/activate
python -m pip install -r requirements.txt
python manage.py compiletranslations
python manage.py migrate
npm --prefix frontend ci
npm run dev
```

Open http://127.0.0.1:8001/. Both processes stop on Ctrl+C. If the default ports
are occupied, stop your old servers or choose ports explicitly:

```bash
PORT=8001 DJANGO_PORT=8000 npm run dev
```

To run the processes separately:

```bash
# Terminal 1, repository root
source .venv/bin/activate
python manage.py runserver

# Terminal 2
cd frontend
npm run dev
```

`DJANGO_ORIGIN` is a server-only environment variable, defaulting to
`http://127.0.0.1:8000`. It must be the backend origin, never the Next.js origin.
Copy `frontend/.env.example` to `frontend/.env.local` to customize it. The root
`.env` is for Django. Database credentials never enter the browser bundle.

## Migration coverage

The project is an in-progress migration. Next.js is the browser entry point and
Django remains the backend; it is not yet a component-for-component React
replacement of every legacy screen.

1. **Public Portal**:
   - Public URLs are served by the Next.js catch-all route, which currently
     evaluates a compiled representation of the existing Django templates.
   - The visual structure and workflows are preserved, but these pages still
     depend on the legacy template inventory and are not independent React
     components yet.

2. **Administration & Staff Portal**:
   - Real Next.js screens exist for login and the reusable dashboard list,
     create, and edit routes. They use the permission-aware `/api/frontend/admin/`
     API and retain Django's sessions, CSRF protection, validation, uploads, and
     model permissions.
   - Account registration/reset/profile, task management, suppliers, careers,
     CMS editing, and remaining staff screens still require dedicated Next.js
     components before legacy template support can be removed.

3. **Backend responsibilities**:
   - Django's models, database (MySQL in production / SQLite in tests), ORM, permissions, auth sessions, file storage, and business logic remain untouched and unmodified.
   - The presentation bridge exports structured context for unresolved routes.
     Direct Django requests still serve the original templates if accessed
     directly without Next.js.
   - Allowlisted headless JSON APIs exist under `/api/frontend/` for public resources (`core/frontend_api.py`) and staff model operations (`core/admin_api.py`).

## Routing and data

`lib/routes.mjs` is the explicit migration inventory. `proxy.ts` forwards every
unmigrated route, API call, media/static file and non-GET request to Django.
Internal Next.js assets stay with Next. Existing public URLs and `/ax/` and
`/ox/` prefixes are preserved. Django's existing translation catalogs and
modeltranslation fields remain the source of translated content. Some new UI
copy still uses English where translations do not exist.

The allowlisted public API lives in `core/frontend_api.py`. It excludes staff
records, applications, credentials and private contact destinations. Mutations
use validated Django forms, Django CSRF cookies/headers, and comment moderation.
Rich text is sanitized before rendering. No CORS middleware or browser-stored
authentication tokens are needed: requests share one public origin.

For production, run `npm run build` and `npm run start` in `frontend/`, with
Django behind its production WSGI/ASGI server. Set `FRONTEND_ORIGINS` in Django
to the exact public HTTPS origin (comma-separated for multiple origins), use
secure Django settings, and serve static/media through the normal web server.
This change does not deploy either service or change hosting.

## Verification

From the repository root:

```bash
python manage.py check --settings=core.frontend_test_settings
python manage.py test core.test_frontend_api core.test_presentation core.test_admin_api --settings=core.frontend_test_settings
npm --prefix frontend test
npm --prefix frontend run typecheck
npm --prefix frontend run build
python scripts/check-ui.py
```

API tests use an isolated in-memory SQLite database and do not modify MySQL.
The API has also been checked against the project's real MySQL database.
External SMTP delivery and Odoo submissions require their services and valid
credentials and are not exercised by the automated suite.
