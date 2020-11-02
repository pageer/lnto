from functools import wraps
from flask import jsonify
from flask_login import current_user

def check_api_login(func):
    @wraps(func)
    def decorated_func(*args, **kwargs):
        if not current_user.is_authenticated:
            return jsonify({'status': 'error', 'message': 'You must log in to access the api.'})
        return func(*args, **kwargs)
    return decorated_func
