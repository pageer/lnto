#!./venv/bin/python


import os
import sys
os.putenv('VIRTUAL_ENVIRONMENT', os.path.join(os.getcwd(), 'venv'))

from wsgiref.handlers import CGIHandler
import lnto

class PathStrip(object):
    def __init__(self, app):
        self.app = app
    def __call__(self, environ, start_response):
        script_name = environ['SCRIPT_NAME']
        script_name = script_name.replace('runcgi.py', '')
        environ['SCRIPT_NAME'] = script_name
        return self.app(environ, start_response)

lnto.app.wsgi_app = PathStrip(lnto.app.wsgi_app)
CGIHandler().run(lnto.app)
