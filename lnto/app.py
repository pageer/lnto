from flask import Flask
from flask_login import LoginManager #pylint: disable=import-error
from flask_sqlalchemy import SQLAlchemy

#### Default configuration settings ####

# User for securing passwords and such.
SECRET_KEY = 'super secret key zone japan'
# Database connection URL
SQLALCHEMY_DATABASE_URI = 'sqlite:///../linkto.db'
# Set to true to allow new user accounts to be registerd.
ALLOW_REGISTRATION = True

SQLALCHEMY_TRACK_MODIFICATIONS = False

#### End config settings ####

APP_VERSION = '0.2'

app = Flask(__name__) #pylint: disable=invalid-name
app.config.from_object(__name__)
app.config.from_pyfile('../config.py', True)

import logging
from logging import FileHandler
file_handler = FileHandler('error.log')
file_handler.setLevel(logging.ERROR)
app.logger.addHandler(file_handler)

appdb = SQLAlchemy(app) #pylint: disable=invalid-name

login_manager = LoginManager() #pylint: disable=invalid-name
# Accomodate old versions of flask-login
try:
    login_manager.init_app(app)
except Exception as ex:
    login_manager.setup_app(app)

def get_db():
    return appdb

def get_app():
    return app

@app.after_request
def after_request(req):
    return req
