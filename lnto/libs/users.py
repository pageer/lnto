from lnto import appdb
from flask import request
from datetime import datetime, timedelta

from sqlalchemy.orm import relationship, backref
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text

import werkzeug.security, hashlib

class User(appdb.Model):
	__tablename__ = 'users'
	userid = Column(Integer, primary_key = True)
	username = Column(String(64), unique = True)
	password = Column(String(255))
	signup_ip = Column(String(64), default = '')
	signup_date = Column(DateTime, default = datetime.now())
	
	user_links = relationship('Link', order_by = 'Link.linkid', backref = 'users', lazy = 'dynamic')
	
	def __init__(self, row = None):
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
		if werkzeug.security.check_password_hash(self.password, password):
			return self.get_userkey()
		else:
			return None
	
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
		if request.cookies.get('uinf'):
			username = request.cookies['uinf'].split('|')[0]
			curr_user = User.get_by_username(username)
			if curr_user.check_login():
				return curr_user
			else:
				return None
		else:
			return None
	
	@classmethod
	def get_by_username(cls, username):
		return appdb.session.query(User).filter_by(username = username).first()
