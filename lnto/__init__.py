from flask import Flask, request, session, g
from flask.ext.sqlalchemy import SQLAlchemy

#### Default configuration settings ####

# User for securing passwords and such.
SECRET_KEY = 'super secret key zone japan'
# Database connection URL
SQLALCHEMY_DATABASE_URI = 'sqlite:///../linkto.db'
# Set to true to allow new user accounts to be registerd.
ALLOW_REGISTRATION = True

#### End config settings ####

APP_VERSION = '0.1'

app = Flask(__name__)
app.config.from_object(__name__)
app.config.from_pyfile('../config.cfg', True)

#import logging
#from logging import FileHandler
#file_handler = FileHandler('error.log')
#file_handler.setLevel(logging.ERROR)
#app.logger.addHandler(file_handler)

appdb = SQLAlchemy(app)

import views, api

@app.after_request
def after_request(req):
    return req

if __name__ == '__main__':
    app.run()
