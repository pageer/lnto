import time, datetime, re
from datetime import datetime, timedelta
from lnto import app
from flask import render_template, make_response, redirect, abort, url_for, request, session, g
from lnto.libs.links import Link
from lnto.libs.users import User
from lnto.libs.tags import Tag
from lnto.libs.dashboard import Dashboard
from lnto.libs.importer import LinkImporter
from lnto.libs.decorators import force_login

def get_base_url():
	return request.url_root

def user_is_logged_in():
	u = User.get_logged_in()
	return u is not None

def get_default_data():
	return {
		'base_url': get_base_url(),
		'referer': request.form.get('next') or request.args.get('next') or request.form.get('referer') or request.referrer or url_for('show_index'),
		'user_logged_in': user_is_logged_in(),
		'allow_registration': app.config['ALLOW_REGISTRATION']
	}


@app.route('/login', methods = ['GET', 'POST'])
def do_login():
	curr_user = User.get_logged_in()
	if curr_user:
		return redirect(url_for('show_index'))
	if request.method == 'POST':
		curr_user = User.get_by_username(request.form.get('username'))
		userkey = curr_user.login(request.form.get('password')) if curr_user else None
		if curr_user and userkey:
			response = make_response(redirect(request.form.get('referer') or url_for('show_index')))
			response.set_cookie('uinf', userkey, 60*60*24*7, datetime.today() + timedelta(days=20))
			return response
		else:
			error = 'Either your username or password is wrong'
			return render_template('login.html', pageoptions = get_default_data(), error = error)
	else:
		return render_template('login.html', pageoptions = get_default_data())

@app.route('/logout', methods = ['GET', 'POST'])
def do_logout():
	usr = User.get_logged_in()
	if usr:
		response = make_response(redirect(url_for('do_login')))
		response.set_cookie('uinf', '', 60*60*24*7, datetime.today() + timedelta(days=20))
	return response

@app.route('/users/new', methods = ['GET', 'POST'])
def do_add_user():
	if not app.config['ALLOW_REGISTRATION']:
		abort(403)
		
	if request.method == 'POST':
		errors = []
		if request.form['username'].strip() == '':
			errors.append('You must give a username')
		if request.form['password'].strip() == '':
			errors.append('You must give a password')
		if request.form['password'] != request.form['confirm']:
			errors.append('Your password does not match the confirmation')
		if len(errors) == 0:
			usr = User()
			usr.username = request.form['username']
			usr.set_password(request.form['password'])
			usr.signup_ip = request.remote_addr
			print usr.signup_ip
			exit
			usr.save()
			return redirect(url_for('show_index'))
		else:
			return render_template("new_user.html", pageoptions = get_default_data(), errors = errors)
	else:
		return render_template("new_user.html", pageoptions = get_default_data())

@app.route('/')
@force_login
def show_index():
	usr = User.get_logged_in()
	#links = Link.get_by_user(usr.userid)
	#recent_links = Link.get_by_most_recent(usr.userid)
	#recent_hits = Link.get_by_most_recent_hit(usr.userid)
	#most_hits = Link.get_by_most_hits(usr.userid)
	#tag_cloud = Tag.get_cloud_by_user(usr.userid)
	dashboard = Dashboard(usr.userid)
	data = dashboard.render()
	return render_template('homepage.html', pageoptions = get_default_data(), user = usr, dashboard = data);#links = links, user = usr, recent_links = recent_links, recent_hits = recent_hits, most_hits = most_hits, tag_cloud = tag_cloud);

@app.route('/links',  defaults = {'username': None})
@app.route('/public/links/<username>')
def show_user_index(username):
	curr_user = User.get_logged_in()
	if username is None:
		usr = curr_user
	else:
		usr = User.get_by_username(username)
	
	if not usr:
		abort(404)
	
	if usr is curr_user:
		links = Link.get_by_user(curr_user.userid)
	else:
		links = Link.get_public_by_user(usr.userid)
	return render_template('link_index.html', pageoptions = get_default_data(), links = links, user = curr_user)

@app.route('/link/add', methods = ['GET', 'POST'])
@force_login
def do_add_link():
	usr = User.get_logged_in()
	
	if request.method == 'POST':
		req = request.form
	else:
		req = request.args
	
	data = {
		'userid': usr.userid,
		'name': req.get('name', ''),
		'shortname': req.get('shortname', ''),
		'url': req.get('url', ''),
		'description': req.get('description', ''),
		'tags': req.get('tags', ''),
		'is_public': True if req.get('is_public', 1) == '1' else False,
	}
	options = {
		'button_label': 'Add Link',
		'post_view': req.get('post_view') if req.get('post_view') else url_for('do_add_link'),
		'redirect_to_target': 1 if req.get('redirect_to_target', 0) == '1' else 0
	}
	
	link = Link(data)
	errors = []
	
	if request.method == 'POST' or data.get('submit') == '1	':
		if data['name'] == '' or data['url'] == '':
			errors.append("Name and URL are required")
		
		if (data.get('tags').strip() == ''):
			taglist = []
		else:
			taglist = data.get('tags').split(',')
	
		link.set_tags(taglist)
		
		if len(errors) == 0:
			link.save()
			redir_target = link.url if options['redirect_to_target'] else (req.get('next') or req.get('referer') or url_for('show_index'))
			return redirect(redir_target)
	
	return render_template("link_add.html", pageoptions = get_default_data(), link = link, options = options, errors = errors)

@app.route('/link/edit/<linkid>', methods = ['GET', 'POST'])
@force_login
def do_edit_link(linkid):
	errors = []
	usr = User.get_logged_in()
	
	link = Link.get_by_id(linkid)
	if not link:
		abort(404)
	
	options = {
		'button_label': 'Save',
		'post_view': url_for('do_edit_link', linkid=linkid)
	}
	
	if request.method == 'POST':
		link.name = request.form.get('name')
		link.description = request.form.get('description')
		link.shortname = request.form.get('shortname')
		link.url = request.form.get('url')
		link.is_public = True if request.form.get('is_public') == '1' else False
		
		if (request.form.get('tags').strip() == ''):
			taglist = []
		else:
			taglist = request.form.get('tags').split(',')
	
		link.set_tags(taglist)
		
		if not (request.form.get('name') and request.form.get('url')):
			errors.append("Name and URL are required")
		
		if len(errors) == 0:
			link.save()
			if request.form.get('referer'):
				return redirect(request.form.get('referer'))
	return render_template("link_add.html", pageoptions = get_default_data(), link=link, options=options, errors = errors)

@app.route('/links/manage/<tags>', methods = ['POST', 'GET'])
@app.route('/links/manage/', methods = ['POST', 'GET'], defaults = {'tags': None})
@force_login
def do_bulk_edit(tags):
	errors = []
	updated = 0
	user = User.get_logged_in()
	
	# Redirect filters immediately
	if request.args.get('tag_select'):
		return redirect(url_for('do_bulk_edit', tags = request.args.get('tag_select')))
	
	available_tags = Tag.get_by_user(user.userid)
	
	if tags:
		taglist = tags.split(',')
		title = 'Manage Links in ' + tags
		links = Link.get_by_tag(taglist[0], user.userid)
	else:
		title = "Manage Links"
		links = Link.get_by_user(user.userid)
	
	if request.method == 'POST':
		
		linkids = request.form.getlist('linkids')
		edit_links = Link.get_by_id(linkids)
		
		if request.form.get('tag_text') and request.form.get('tag_submit'):
			for l in edit_links:
				l.add_tag(request.form.get('tag_text'))
				l.save()
		
		if request.form.get('set_privacy') and request.form.get('privacy_submit'):
			for l in edit_links:
				l.is_public = True if request.form.get('set_privacy') == 'public' else False
				l.save()
		
		updated += 1
	
	return render_template("link_edit_bulk.html", pageoptions = get_default_data(), url_tags = tags, links=links, section_title = title, tags = available_tags, errors = errors)


@app.route('/link/delete/<linkid>', methods = ['POST', 'GET'])
@force_login
def show_delete_link(linkid):
	usr = User.get_logged_in()
	error = ''
	
	link = Link.get_by_id(linkid)
	if not link.is_owner(usr):
		error = 'You do not have permission to delete this link.'
	else:
		if request.form.get('confirm'):
			link.delete()
			return redirect(url_for('show_index'))
		elif request.form.get('cancel'):
			return redirect(request.form.get('referer'))
	return render_template("link_delete.html", pageoptions = get_default_data(), link=link, error = error)

@app.route('/links/import', methods = ['GET', 'POST'])
@force_login
def show_import():
	if request.method == 'POST':
		markup = request.form.get('importtext')
		import_type = request.form.get('importtype')
		importer = LinkImporter(markup, import_type)
		results = importer.convert()
	else:
		markup = ''
		results = None
	return render_template('link_import.html', pageoptions = get_default_data(), import_file = markup, results = results)

@app.route('/link/show/<linkid>')
def show_link(linkid):
	link = Link.get_by_id(linkid)
	if link is None:
		abort(404)
	usr = User.get_logged_in()
	return render_template('link.html', pageoptions = get_default_data(), link = link, user = usr)

@app.route('/to/<linkid>')
def show_linkurl(linkid):
	link = Link.get_by_id(linkid)
	if link is None:
		abort(404);
	usr = User.get_logged_in()
	#if usr is not None:
	#    link.get_count(usr).add_hit()
	link.get_hit(usr).add_hit()
	return redirect(link.url)

@app.route('/tags',  defaults = {'username': None})
def show_user_tag_list(username):
	if username is None:
		user = User.get_logged_in()
		username = user.username
	else:
		user = User.get_by_username(username)
	
	if user.username == username:
		tags = Tag.get_cloud_by_user(user.userid)
		title = "My Tags"
	else:
		tags = Tag.get_public_by_user(user.userid)
		title = 'Tags for %s' % username
	
	return render_template('tag_index.html', pageoptions = get_default_data(), tags = tags, page_title = title, section_title = title)
	
@app.route('/public/tag/<name>')
def show_tag(name):
	usr = User.get_logged_in()
	links = Link.get_public_by_tag(name)
	title = 'Links for Tag - "%s"' % name
	return render_template('link_index.html',pageoptions = get_default_data(),  user = usr, links = links, section_title = title, page_title = title);
	
@app.route('/tag/<name>')
@force_login
def show_user_tag(name):
	usr = User.get_logged_in()
	links = Link.get_by_tag(name, usr.userid)
	title = 'My Tagged Links - "%s"' % name
	return render_template('link_index.html', pageoptions = get_default_data(), user = usr, links = links, section_title = title, page_title = title);

# Wildcard route - THIS MUST BE PROCESSED LAST    
@app.route('/<shorturl>')
def show_shorturl(shorturl):
	link = Link.get_by_shortname(shorturl)
	if link is None:
		abort(404);
	usr = User.get_logged_in()
	link.get_hit(usr).add_hit()
	#if usr is not None:
	#    link.get_count(usr).add_hit()
	return redirect(link.url)
