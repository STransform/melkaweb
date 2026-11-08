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

Open http://127.0.0.1:3000/. Both processes stop on Ctrl+C. If the default ports
are occupied, stop your old servers or choose ports explicitly:

```bash
PORT=3100 DJANGO_PORT=18000 npm run dev
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

React components now render the homepage, about pages, services, technology,
infrastructure, innovation, company values, vision/mission, structure, partners,
testimonials, training, news and blog lists/details, documents, image/video
galleries, events, bids, search, and contact. Database content, files, page
visibility settings, pagination, approved blog comments, and contact submissions
are connected to Django. Contact notifications use the configured SMTP service.

**Still rendered by Django:** account login/signup/password reset/profile,
staff dashboards and task management, Django CMS pages/editing, supplier lookup,
and careers/application forms with their Odoo integration. Next.js forwards
these original routes, requests, cookies, redirects, and multipart uploads to
Django. They have not been converted to React. Retaining the original workflow
is a compatibility step, not a claim that the whole frontend is migrated.

The original Django templates remain available for rollback. Running only
Django still serves the original site. A full React conversion of the remaining
workflows requires dedicated session/authentication, permission-aware CRUD,
CMS rendering, and Odoo application API work and integration tests.

Unused templates, theme demo/example skins, unused RTL stylesheets, and an
unreferenced Bootstrap copy have been removed. Shared `templates/front/base.html`,
the active public templates used by CMS, account/staff templates, and their
Bootstrap/theme assets remain dependencies of the Django workflows above.
Do not remove these directories wholesale while those workflows use Django.

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
python manage.py check
python manage.py test core.test_frontend_api --settings=core.frontend_test_settings
npm --prefix frontend test
npm --prefix frontend run typecheck
npm --prefix frontend run build
```

API tests use an isolated in-memory SQLite database and do not modify MySQL.
The API has also been checked against the project's real MySQL database.
External SMTP delivery and Odoo submissions require their services and valid
credentials and are not exercised by the automated suite.
