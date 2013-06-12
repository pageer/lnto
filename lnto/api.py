import time, datetime
from lnto import app
from flask import render_template, make_response, redirect, jsonify, abort, url_for, request, session, g
from lnto.libs.links import Link
from lnto.libs.users import User
from lnto.libs.decorators import check_api_login

# Utility functions

def json_error(message = None):
	return jsonify({'status': 'error', 'message': message})

def json_success(data = None):
	return jsonify({'status': 'success', 'data': data})

# Routes

@app.route('/api/links/delete', methods = ['POST'])
def do_delete_link():
	if not request.form.get('linkid'):
		return json_error('No linkid specified')
	
	link = Link.get_by_id(request.form.get('linkid'))
	if not link:
		return json_error('That link does not exist.')
	
	usr = User.get_logged_in()
	if not link.is_owner(usr):
		return json_error('You do not have permission to delete this link.')
	
	try:
		link.delete()
		return json_success()
	except Exception:
		return json_error('Error deleting link')

@app.route('/api/link/<linkid>')
@check_api_login
def get_link_metadata(linkid):
	pass

@app.route('/api/folder/<path>')
@check_api_login
def get_folder(path):
	pass

