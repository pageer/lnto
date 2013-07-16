import time, datetime
from lnto import app, appdb
from flask import render_template, make_response, redirect, jsonify, abort, url_for, request, session, g
from lnto.libs.links import Link
from lnto.libs.users import User
from lnto.libs.dashboard import Dashboard
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
@check_api_login
def api_delete_link():
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

@app.route('/api/modules/delete', methods = ['POST'])
@check_api_login
def api_remove_module():
	usr = User.get_logged_in()
	dash = Dashboard(usr.userid)
	modid = request.form.get('moduleid')
	
	if not modid:
		return json_error('No moduleid given')
	
	if dash.remove_module(modid):
		return json_success()
	else:
		return json_error('Failed to remove module')
	
@app.route('/api/modules/save_position', methods = ['POST'])
@check_api_login
def api_save_positions():
	usr = User.get_logged_in()
	dash = Dashboard(usr.userid)
	modids = request.form.getlist('moduleid')
	saved_mods = dash.get_modules_by_id()
	
	i = 0
	
	for mod in modids:
		saved_mods[int(mod)].position = i
		appdb.session.add(saved_mods[int(mod)])
		i += 1;
	
	try:
		appdb.session.commit()
		return json_success()
	except Exception as e:
		return json_error(str(e))
	


@app.route('/api/links/tag', methods = ['POST'])
@check_api_login
def api_add_tag():
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


@app.route('/api/links/<linkid>')
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

