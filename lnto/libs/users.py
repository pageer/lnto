from lnto.libs.db import *
from flask import request
from datetime import datetime, timedelta
import werkzeug.security, hashlib

class User(ActiveRecord):
	table = 'users'
	key = 'userid'
	fields = {
		'userid': 0,
		'username': '',
		'password': '',
		'signup_ip': '',
		'signup_date': datetime.now()
	}
	
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
	
	@staticmethod
	def get_by_username(username):
		ret = User.get_by('users', {'username': username}, return_class = User)
		return ret[0] if len(ret) >  0 else None
	
	@staticmethod
	def get_by_userid(userid):
		ret = User.get_by('users', {'userid': userid}, return_class = User)
		return ret[0] if len(ret) >  0 else None
