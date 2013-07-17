lnto: An anti-social web-based bookmarking system.
Copyright (C) 2013 Peter A. Geer <pageer@skepticats.com>
This program is licensed under the GNU General Public License.
See the license information section for details.


ABOUT
=====
Lnto is an anti-social bookmarking app.  It allows you to store your links,
tag them, tracks usage, and lets you create a customized link dashboard
suitable for use as your browser homepage.  Oh, and you can also use it to
share your links with others if you want.


REQUIREMENTS
============
(Note: versions just indicate what lnto has been tested with.  Others may work.)
Flask (>= 0.9)
SQLAlchemy (>= 0.8)
Flask-SQLAlchemy
beautifulsoup4


SETUP
=====
1) Extract the archive and copy the files to your host.
2) Set up your server using whatever method is appropriate for running a Flask
   application, i.e. WSGI, Fast CGI, plain CGI, etc.
   a) For regular CGI, edit the runcgi.py script to set your virtual-env path
      or comment out the files.  (Make sure the file permissions are correct.)
   b) Create appropriate rewrite rules for your web server.  If using Apache,
      you can simply use the supplied .htaccess file.
3) Create the database.  Currently, MySQL and SQLite are supported.  Others
   should also work, but you're on your own.
4) Import the initial database schema using the appropriate file in the schema
   directory.
5) Create a config.cfg file in your lnto directory.  Add the following lines:
   SECRET_KEY = '<secret_key_value_here'
   SQLALCHEMY_DATABASE_URI = '<database_uri_here>'
   a) To generate a secret key, you can use the gen-secret-key.py CGI script.
   b) To determine the database URI, consult the SQLAlchemy documentation here:
      http://docs.sqlalchemy.org/en/rel_0_8/core/engines.html
6) Create a new user account by going to: <url_to_lnto>/users/new
7) (Optional) To block additional accounts from being created, add the following
   line to your config.cfg file:
   ALLOW_REGISTRATION = False


CREDITS
=======
Icons taken from Fam Fam Silk 1.3 by Mark James
http://www.famfamfam.com/lab/icons/silk/
Fam Fam Silk is licensed under a Creative Commons Attribution 2.5 License.
http://creativecommons.org/licenses/by/2.5/


LICENSE INFORMATION
===================
lnto: An anti-social web-based bookmarking system.
Copyright (C) 2013 Peter A. Geer <pageer@skepticats.com>

This program is free software; you can redistribute it and/or modify it under
the terms of the GNU General Public License as published by the Free Software
Foundation; either version 2 of the License, or (at your option) any later
version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with
this program; if not, write to the Free Software Foundation, Inc., 675 Mass Ave,
Cambridge, MA 02139, USA.