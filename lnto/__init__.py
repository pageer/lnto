import lnto.libs.db
from flask import Flask, request, session, g
from flask.ext.sqlalchemy import SQLAlchemy

DB_PATH = 'linkto.db'

DEBUG = True
SECRET_KEY = 'super secret key zone japan'
SQLALCHEMY_DATABASE_URI = 'sqlite:///../linkto.db'

app = Flask(__name__)
app.config.from_object(__name__)
appdb = SQLAlchemy(app)
lnto.libs.db.DB_PATH = app.config['DB_PATH']

import views, api

#@app.before_request
#def before_request():
#    g.db = connect_db()

@app.after_request
def after_request(req):
    return req

@app.teardown_request
def teardown_request(exception):
    if (hasattr(g, 'db')):
        g.db.close()

if __name__ == '__main__':
    app.run()
#else:
#    from wsgiref.handlers import CGIHandler
#    CGIHandler().run(app)
