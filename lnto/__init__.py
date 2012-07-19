import lnto.libs.db
from flask import Flask, request, session, g

DB_PATH = 'linkto.db'
DEBUG = True
SECRET_KEY = 'super secret key zone japan'

app = Flask(__name__)
app.config.from_object(__name__)
lnto.libs.db.DB_PATH = app.config['DB_PATH']

import views

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
