from flask import Flask, request, session, g
from flask_sqlalchemy import SQLAlchemy
import lnto.views
import lnto.api
from lnto.app import app
from lnto.app import appdb

if __name__ == '__main__':
    app.run()
