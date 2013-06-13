from flask import request, redirect, url_for
from functools import wraps
from lnto.libs.users import User

def force_login(func):
	@wraps(func)
	def decorated_func(*args, **kwargs):
		usr = User.get_logged_in()
		if not usr:
			return redirect(url_for('do_login', next = request.url))
		else:
			return func(*args, **kwargs)
	return decorated_func

def check_api_login(func):
	@wraps(func)
	def decorated_func(*args, **kwargs):
		usr = User.get_logged_in()
		if not usr:
			return jsonify({'status': 'error', 'message': 'You must log in to access the api.'})
		else:
			return func(*args, **kwargs)
	return decorated_func
	
