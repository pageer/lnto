from functools import wraps
from flask import jsonify
from lnto.libs.users import User

def check_api_login(func):
    @wraps(func)
    def decorated_func(*args, **kwargs):
        usr = User.get_logged_in()
        if not usr:
            return jsonify({'status': 'error', 'message': 'You must log in to access the api.'})
        return func(*args, **kwargs)
    return decorated_func
