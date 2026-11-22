# lnto: An anti-social web-based bookmarking system

Copyright (C) 2013 Peter A. Geer <pageer@skepticats.com>.
Licensed under the GNU General Public License; see
[LICENSE.txt](LICENSE.txt) or the license section at the bottom of this
file.

## About

Lnto is an anti-social bookmarking app. It allows you to store your links,
tag them, track usage, and lets you create a customized link dashboard
suitable for use as your browser homepage. Oh, and you can also use it to
share your links with others if you want.

## Requirements

* Python 3.11 or newer (tested with 3.11 and 3.14/3.15)
* pip (bundled with Python)
* For development: a Python virtual environment
* For production on shared hosting: CGI support (e.g. Apache with
  `.htaccess` overrides)

## Setup

### 1. Create the virtual environment

The app uses a Python virtual environment named `venv` in the project
root. Both the dev server (`runserver.py`) and the CGI wrapper
(`runcgi.py`) reference it by relative path, so keep that name.

**Local development:**

```bash
python -m venv venv
# On Windows:
venv\Scripts\python -m pip install --upgrade pip
venv\Scripts\python -m pip install -r requirements-dev.txt

# On Linux/macOS:
./venv/bin/python -m pip install --upgrade pip
./venv/bin/python -m pip install -r requirements-dev.txt
```

`requirements-dev.txt` installs the runtime requirements (from
`requirements.txt`) plus dev tools (`pytest`, `pylint`). Use plain
`requirements.txt` if you only want to run the app.

**Production (shared hosting):**

```bash
python3 -m venv venv
echo "Deny from all"        > venv/.htaccess
echo "Require all denied"  >> venv/.htaccess
./venv/bin/python -m pip install --upgrade pip
./venv/bin/python -m pip install -r requirements.txt
```

The `venv/.htaccess` file prevents the web server from serving the
contents of the virtual environment.

Notes:

* One set of runtime pins (`requirements.txt`) is shared between local
  and production. Keep them in sync — version drift between the two
  environments is how "works locally, breaks in production" happens.
* The database driver is PyMySQL (pure Python, installs everywhere).
  It is only used when `config.py` selects a `mysql+pymysql://`
  database URI; local development uses SQLite by default and does not
  touch it.

### 2. Configure the web server

* **Local dev:** run `runserver.py` with the venv's interpreter:

  ```bash
  venv\Scripts\python runserver.py     # Windows
  ./venv/bin/python runserver.py       # Linux
  ```

  This serves the app on http://127.0.0.1:5000 with debug mode on.

* **Production:** the included `runcgi.py` runs the app as a plain CGI
  script using the venv's interpreter (its shebang is
  `#!./venv/bin/python` — a path relative to the project root, so keep
  the venv name). Keep `runcgi.py` executable. Use the included
  `.htaccess` file to rewrite all requests that don't map to a real
  file to `runcgi.py`:

  ```apache
  RewriteEngine On
  RewriteCond %{REQUEST_FILENAME} !-f
  RewriteRule ^(.*)$ runcgi.py/$1 [L]
  ```

### 3. Create the database

Currently, MySQL and SQLite are supported. Others should also work, but
you're on your own.

* SQLite (local dev): the default configuration points at `linkto.db`
  in the project root. Create the tables by importing
  `schema/schema-sqlite.sql`, e.g.:

  ```bash
  sqlite3 linkto.db < schema/schema-sqlite.sql
  ```

* MySQL (production): import `schema/schema-mysql.sql` into the
  database, e.g. with `mysql < schema/schema-mysql.sql`.

For upgrades of an existing database, use Alembic (`alembic.ini`,
`alembic/`).

### 4. Create config.py

Create a `config.py` file in the project root. At minimum:

```python
SECRET_KEY = '<secret_key_value_here>'
SQLALCHEMY_DATABASE_URI = '<database_uri_here>'
```

* To generate a secret key, you can use the `gen-secret-key.py` CGI
  script, or the `secrets` module:

  ```bash
  python -c "import secrets; print(secrets.token_hex(32))"
  ```

* The database URI format follows the SQLAlchemy documentation
  (<https://docs.sqlalchemy.org/core/engines.html>). Examples:

  * Local SQLite: `sqlite:///../linkto.db` (this is the built-in
    default and may be omitted for local dev)
  * MySQL via PyMySQL (shared hosting):
    `mysql+pymysql://user:password@hostname/dbname`

* Optional settings:

  ```python
  DEBUG = True                 # never enable in production
  ALLOW_REGISTRATION = False   # set False to block new accounts
  ```

`config.py` is excluded from version control (see `.gitignore`) and is
blocked from web access by the included `.htaccess`.

### 5. Create a user account

Create a new user account by going to: `<url_to_lnto>/users/new`

To block additional accounts from being created, set
`ALLOW_REGISTRATION = False` in `config.py` (step 4).

## Running the tests

The test suite uses the Python standard library's `unittest` — no test
runner package is needed. Run it from the project root:

```bash
# Windows:
venv\Scripts\python -m unittest discover -s tests

# Linux/macOS:
./venv/bin/python -m unittest discover -s tests
```

Or with `pytest` (included in `requirements-dev.txt`):

```bash
venv\Scripts\pytest            # Windows
./venv/bin/pytest              # Linux/macOS
```

Each test creates and destroys a throwaway SQLite database at
`lnto/tmp.db`, so the suite is safe to run against a development copy —
it never touches `linkto.db` or any real data. The tests take around a
minute because the database is rebuilt for every test.

## Credits

* Icons taken from Fam Fam Silk 1.3 by Mark James,
  <http://www.famfamfam.com/lab/icons/silk/>. Fam Fam Silk is licensed
  under a Creative Commons Attribution 2.5 License,
  <http://creativecommons.org/licenses/by/2.5/>.
* SVG icons from Iconic by P.J. Onori,
  <http://somerandomdude.com/work/open-iconic/>. Additional
  contributions by Philip Shaw (www.codestyle.org), Yann Hourdel
  (www.github.com/yhourdel), and Ian Storm Taylor
  (www.github.com/ianstormtaylor). Iconic is licensed under a Creative
  Commons Share Alike 3.0 License,
  <http://creativecommons.org/licenses/by-sa/3.0/us/>.

## License information

lnto: An anti-social web-based bookmarking system.
Copyright (C) 2013 Peter A. Geer <pageer@skepticats.com>

This program is free software; you can redistribute it and/or modify it
under the terms of the GNU General Public License as published by the
Free Software Foundation; either version 2 of the License, or (at your
option) any later version.

This program is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
General Public License for more details.

You should have received a copy of the GNU General Public License along
with this program; if not, write to the Free Software Foundation, Inc.,
675 Mass Ave, Cambridge, MA 02139, USA.
