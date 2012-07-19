#!/usr/local/bin/python
activate_this = '/home/skepticats/www/www/lnto/venv/bin/activate_this.py'
execfile(activate_this, dict(__file__=activate_this))
from lnto import app
from wsgiref.handlers import CGIHandler
CGIHandler().run(app)