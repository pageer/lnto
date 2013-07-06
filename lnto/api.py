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


def validate_link(link, user = None):
	if not user:
		user = User.get_logged_in()
	
	if not link:
		return json_error('That link does not exist.')
	
	if not link.is_owner(user):
		return json_error('You do not have permission to delete this link.')
	
	return None


# Routes

@app.route('/api/links/delete', methods = ['POST'])
def do_delete_link():
	if not request.form.get('linkid'):
		return json_error('No linkid specified')
	
	link = Link.get_by_id(request.form.get('linkid'))
	error = validate_link(link)
	if error:
		return error
	
	try:
		link.delete()
		return json_success()
	except Exception as e:
		return json_error('Error deleting link - ' + str(e))


@app.route('/api/link/tag', methods = ['POST'])
def do_add_tag():
	if not request.form.get('linkid') or not request.form.get('tags'):
		return json_error('Missing linkid or tags parameters')
	
	link = Link.get_by_id(request.form.get('linkid'))
	tags = request.form.get('tags').split(',')
	
	error = validate_link(link)
	if error:
		return error
	
	try:
		for tag in tags:
			link.add_tag(tag.strip())
		link.save()
		return json_success()
	except Exception as e:
		return json_error('Error adding tags - ' + str(e))


@app.route('/api/link/<linkid>')
@check_api_login
def get_link_metadata(linkid):
	link = Link.get_by_id(linkid)
	error = validate_link(link)
	if error:
		return error
	else:
		return json_success(link.serializable())


@app.route('/api/folder/<path>')
@check_api_login
def get_folder(path):
	pass

