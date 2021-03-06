from datetime import datetime
import hashlib
import werkzeug.security # pylint: disable=import-error
from flask import request
from flask_login import UserMixin
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, DateTime
from lnto import appdb, login_manager
#from lnto.app import appdb, login_manager

login_manager.login_view = 'do_login'

@login_manager.user_loader
def load_user(userid):
    return User.get_by_userid(userid)

class User(appdb.Model, UserMixin):

    __tablename__ = 'users'
    userid = Column(Integer, primary_key=True)
    username = Column(String(64), unique=True)
    password = Column(String(255))
    signup_ip = Column(String(64), default='')
    signup_date = Column(DateTime, default=datetime.now())

    user_links = relationship('Link', order_by='Link.linkid', backref='users', lazy='dynamic')

    def __init__(self, row=None):
        if row is not None:
            self.username = row['username'] if row.get('username') else ''
            self.password = row['password'] if row.get('password') else ''
            self.signup_ip = row['signup_ip'] if row.get('signup_ip') else ''
            self.signup_date = row['signup_date'] if row.get('signup_date') else datetime.now()


    def set_password(self, passwd):
        self.password = werkzeug.security.generate_password_hash(passwd)

    def check_login(self):
        return request.cookies['uinf'] == self.get_userkey()

    def login(self, password):
        # HACK: Convert both of the parameters to strings so that Werkzeug doesn't
        # throw "'unicode' does not have the buffer interface" exceptions.
        # There is almost certainly a better way to do this.
        if werkzeug.security.check_password_hash(str(self.password), str(password)):
            return self.get_userkey()
        return None

    def get_id(self):
        return self.userid

    def check_password(self, password):
        return werkzeug.security.check_password_hash(str(self.password), str(password))

    def get_userkey(self):
        userkey = request.headers.get('User-Agent', '') + request.headers.get('Remote-Addr', '')
        userkey += hashlib.sha512(self.password).hexdigest()
        return self.username + '|' + hashlib.sha512(userkey).hexdigest()

    def save(self):
        appdb.session.add(self)
        appdb.session.commit()

    def delete(self):
        appdb.session.delete(self)
        appdb.session.commit()

    @staticmethod
    def get_logged_in():
        if not request.cookies.get('uinf'):
            return None

        username = request.cookies['uinf'].split('|')[0]

        if username:
            curr_user = User.get_by_username(username)
            if curr_user:
                return curr_user if curr_user.check_login() else None
        return None

    @classmethod
    def get_by_username(cls, username):
        return appdb.session.query(User).filter_by(username=username).first()

    @classmethod
    def get_by_userid(cls, userid):
        return appdb.session.query(User).filter_by(userid=userid).first()
