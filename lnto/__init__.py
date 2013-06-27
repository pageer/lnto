from flask import Flask, request, session, g
from flask.ext.sqlalchemy import SQLAlchemy

DEBUG = True
SECRET_KEY = 'super secret key zone japan'
SQLALCHEMY_DATABASE_URI = 'sqlite:///../linkto.db'

app = Flask(__name__)
app.config.from_object(__name__)
appdb = SQLAlchemy(app)

import views, api

@app.after_request
def after_request(req):
    return req

if __name__ == '__main__':
    app.run()
