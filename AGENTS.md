# AGENTS.md

Guidance for AI coding agents working in this repository.

## Project overview

lnto ("link-to") is a small, self-hosted bookmarking web app built with
Flask. It is old, deliberately simple, and runs in two environments:

- **Local dev** (Windows, Python 3.14/3.15): Flask dev server, SQLite.
- **Production** (Linux shared host, Python 3.11): plain CGI via Apache
  `.htaccess` rewrite, MySQL through PyMySQL.

## Layout

- `lnto/` — the application package
  - `app.py` — Flask app factory-ish module; creates the app, loads
    defaults, then overrides from `../config.py`
  - `views.py` / `api.py` — HTML routes and JSON routes
  - `libs/` — SQLAlchemy models and domain logic (`links`, `tags`,
    `users`, `folders`, `dashboard`, `importer`, `decorators`)
  - `templates/`, `static/` — Jinja templates and assets
- `tests/` — unittest-based tests; `tests/db.py` seeds a throwaway DB
- `schema/` — raw SQL for initial table creation (`schema-sqlite.sql`,
  `schema-mysql.sql`)
- `alembic/` — schema migrations for existing databases
- `runserver.py` (dev), `runcgi.py` (production CGI entry point)
- `Gruntfile.js` — frontend build: copies vendored JS/CSS from
  `node_modules/` into `lnto/static/vendor/`

## Environment

- Virtual environment lives at `venv/` (this exact name — `runcgi.py`'s
  shebang is `#!./venv/bin/python`). On Windows the interpreter is
  `venv\Scripts\python.exe`; on Linux `./venv/bin/python`.
- `requirements.txt` is the **single runtime dependency set shared by
  both environments**; `requirements-dev.txt` adds dev tools and
  includes it via `-r`.
- `config.py` (gitignored) holds `SECRET_KEY`, `DEBUG`,
  `ALLOW_REGISTRATION`, and `SQLALCHEMY_DATABASE_URI`. Never commit it
  and never edit the user's copy without asking. Defaults live in
  `lnto/app.py` (`sqlite:///../linkto.db`).

## Commands

```bash
# Dev server (from project root)
venv\Scripts\python runserver.py        # Windows
./venv/bin/python runserver.py          # Linux

# Tests (stdlib unittest, ~1 minute; each test rebuilds lnto/tmp.db)
venv\Scripts\python -m unittest discover -s tests
./venv/bin/python -m unittest discover -s tests

# Lint (pylint config in .pylintrc)
venv\Scripts\python -m pylint lnto tests

# Frontend vendor assets (after changing package.json)
npm install && npx grunt copy
```

Do not run the dev server against a database you care about, and do not
commit `linkto.db`, `lnto/tmp.db`, or `error.log` (gitignored).

## Dependency constraints (important)

The pinned versions are chosen to work on both Python 3.11 and
3.14/3.15. Do not bump majors without testing in both environments:

- **SQLAlchemy stays 1.4.x** — the models (`lnto/libs/*.py`) use the
  1.4 `Query` API (`appdb.session.query(...)`, `.filter_by()`,
  lazy loading configured via relationship strings).
- **Werkzeug must be >= 2.1** — 2.0.x uses `ast.Str`, removed in
  Python 3.12, but older app code assumes the 2.x routing behavior;
  2.3.8 is the tested pin.
- **Flask stays 2.2.x** — Flask-SQLAlchemy 2.5.1 imports
  `flask._app_ctx_stack`, removed in Flask 2.3.
- **WTForms stays 2.3.x** — `lnto/forms.py` imports
  `wtforms.fields.html5`, removed in WTForms 3.0.
- **PyMySQL** is the only DB driver; never add mysqlclient (no MySQL
  headers on the shared host, and its wheels don't match the host
  glibc).

## Code conventions

- Plain Flask, no blueprints: routes are decorated in `views.py` /
  `api.py` with the shared `app` object.
- Models subclass `appdb.Model`; persistence goes through the model's
  own `save()`/`delete()` methods.
- Tests are plain `unittest.TestCase`; use `tests.db.init_test_db()` in
  `setUp` and `tests.db.delete_test_db()` in `tearDown`. Mocking uses
  `unittest.mock` (the standalone `mock` package is not installed).
- Match the surrounding style: 4-space indent, no type annotations,
  `#pylint: disable=` comments where the old code has them.

## Known quirks (don't "fix" casually)

- `lnto/app.py` opens `error.log` with a `FileHandler` at import time.
  If that file/dir is unwritable, every request fails before routing —
  this is a known shared-hosting failure mode, not a bug to silently
  restructure.
- Most forms do not render CSRF tokens, but `FlaskForm` still
  validates them, so e.g. `/users/new` registration silently fails
  validation. Only `link_add.html` renders `csrf_token`. Treat any
  change here as a deliberate, tested change.
- `Link.__init__` takes a dict of raw values; unchecked boolean form
  fields produce `False` (not `None`), so links added with the
  "Is public" box unchecked are private.
- Relative SQLite URIs (`sqlite:///tmp.db`, `sqlite:///../linkto.db`)
  resolve relative to the app directory / working directory, not the
  project root.

## Git

- Branch: `master`.
- Commit messages: short, imperative subject line; body only when the
  change needs explanation.
- The user reviews commits — do not commit without being asked.
