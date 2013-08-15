import time, datetime, re, urllib2
from datetime import datetime, timedelta
from lnto import app
from flask import render_template, make_response, redirect, abort, url_for, flash, request, session, g
from lnto.libs.links import Link
from lnto.libs.users import User
from lnto.libs.tags import Tag
from lnto.libs.dashboard import Dashboard, module_type_map
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
		'allow_registration': app.config['ALLOW_REGISTRATION'],
		'standalone': request.args.get('framed')
	}


@app.route('/about')
def show_about():
	return render_template('about.html', pageoptions = get_default_data(), version = app.config['APP_VERSION'])

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
	dashboard = Dashboard(usr.userid)
	data = dashboard.render()
	return render_template('homepage.html', pageoptions = get_default_data(), user = usr, dashboard = data)

@app.route('/modules/add', methods = ['GET', 'POST'])
@force_login
def show_add_module():
	usr = User.get_logged_in()
	dash = Dashboard(usr.userid)
	mods = dash.get_modules()
	modtype = request.form.get('mod_type')
	if request.method == 'POST' and modtype and module_type_map.get(int(modtype)):
		mod = module_type_map[int(modtype)]
		if mod.config_required:
			return redirect(url_for('do_add_module', modtype = request.form.get('mod_type')))
		else:
			pos = dash.get_next_position()
			try:
				dash.add_module(int(modtype), int(pos))
				flash('Module added.', 'success')
				return redirect(url_for('show_index'))
			except Exception as e:
				flash(str(e), 'error')
			
	return render_template('module_available.html', pageoptions = get_default_data(), module_types = module_type_map, modules = mods)


@app.route('/modules/add/<modtype>', methods = ['GET', 'POST'])
@force_login
def do_add_module(modtype):
	usr = User.get_logged_in()
	dash = Dashboard(usr.userid)
	mod = module_type_map[int(modtype)](usr.userid)
	
	if request.method == 'POST':
		mod_type = request.form.get('module_type')
		pos = request.form.get('position') or dash.get_next_position()
		if mod_type:
			try:
				dash.add_module(int(mod_type), int(pos), request.form)
				flash('Module added.', 'success')
				return redirect(url_for('show_index'))
			except Exception as e:
				flash(str(e), 'error')
		else:
			flash('You must supply a module type.', 'error')
	
	return render_template('module_add.html', pageoptions = get_default_data(),
						   user = usr, dashboard = dash, module = mod,
						   post_view = url_for('do_add_module', modtype = mod.typeid))


@app.route('/modules/config/<moduleid>', methods = ['GET', 'POST'])
@force_login
def do_module_config(moduleid):
	usr = User.get_logged_in()
	dash = Dashboard(usr.userid)
	mod = dash.get_single_module(moduleid)
	
	if not mod:
		abort(404)
	
	if request.method == 'POST':
		try:
			mod.save_config(request.form)
			flash('Module config saved.', 'success')
			return redirect(url_for('show_index'))
		except Exception as e:
			flash(str(e), 'error')
	
	return render_template('module_add.html', pageoptions = get_default_data(),
						   user = usr, dashboard = dash, module = mod.module,
						   post_view = url_for('do_module_config', moduleid = moduleid),
						   title = 'Configure Module')


@app.route('/modules/remove/<moduleid>')
@force_login
def do_remove_module(moduleid):
	usr = User.get_logged_in()
	dash = Dashboard(usr.userid)
	if dash.remove_module(moduleid):
		flash('Module deleted', 'success')
	else:
		flash('Could not delete module', 'error')
	return redirect(url_for('show_index'))


@app.route('/public/<username>')
def show_user():
	pass


@app.route('/links',  defaults = {'username': None})
@app.route('/public/<username>/links')
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
	
	if request.method == 'POST' or data.get('submit') == '1	':
		if (data.get('tags').strip() == ''):
			taglist = []
		else:
			taglist = data.get('tags').split(',')
	
		link.set_tags(taglist)
		
		if data['name'] == '' or data['url'] == '':
			flash("Name and URL are required", 'error')
		else:
			link.save()
			redir_target = link.url if options['redirect_to_target'] else (req.get('next') or req.get('referer') or url_for('show_index'))
			return redirect(redir_target)
	
	tags = Tag.get_by_user(usr.userid)
	
	return render_template("link_add.html", pageoptions = get_default_data(), link = link, tags = tags, options = options)

@app.route('/link/add/fetch', defaults = {'url': None}, methods = ['GET', 'POST'])
@app.route('/link/add/fetch/<url>', methods = ['GET', 'POST'])
@force_login
def do_add_from_url(url):
	fetch_url = url or request.form.get('fetch_url')
	if (fetch_url):
		try:
			link = Link.create_from_url(fetch_url)
			redir_url = url_for('do_add_link', name = link.name, url = link.url, description = link.description, redirect_to_target = 1)
			return redirect(redir_url)
		except Exception as e:
			flash('Error getting link - ' + str(e), 'error')
	return render_template('link_add_url.html', pageoptions = get_default_data(), url = fetch_url or '')


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
	user = User.get_logged_in()
	
	# Redirect filters immediately
	if request.args.get('tag_select'):
		return redirect(url_for('do_bulk_edit', tags = request.args.get('tag_select')))
	
	available_tags = Tag.get_by_user(user.userid)
	
	if request.method == 'POST':
		
		linkids = request.form.getlist('linkids')
		edit_links = Link.get_by_id(linkids)
		
		valid = True
		for l in edit_links:
			if not l.is_owner(user):
				valid = False
				flash("You do not have permission to edit all of the selected links.", 'error')
		
		if valid and request.form.get('tag_text') and request.form.get('tag_submit'):
			for l in edit_links:
				l.add_tag(request.form.get('tag_text'))
				l.save()
			flash('Tagged %d links as "%s"' % (len(edit_links), request.form.get('tag_text')), 'success')
		
		if valid and request.form.get('set_privacy') and request.form.get('privacy_submit'):
			for l in edit_links:
				l.is_public = True if request.form.get('set_privacy') == 'public' else False
				l.save()
			flash('Marked %d links %s' % (len(edit_links), 'public' if request.form.get('set_privacy') == 'public' else 'private'), 'success')
		
		if valid and request.form.get('delete_selected_submit'):
			for l in edit_links:
				l.delete()
			flash('Deleted %s links' % len(edit_links), 'success')
	
	if tags == 'untagged':
		taglist = tags.split(',')
		title = 'Manage Untagged Links'
		links = Link.get_untagged(user.userid)
	elif tags:
		taglist = tags.split(',')
		title = 'Manage Links in ' + tags
		links = Link.get_by_tag(taglist[0], user.userid)
	else:
		title = "Manage Links"
		links = Link.get_by_user(user.userid)
	
	return render_template("link_edit_bulk.html", pageoptions = get_default_data(), url_tags = tags, links=links, section_title = title, tags = available_tags)


@app.route('/link/search', methods = ['POST'])
def do_link_search():
	usr = User.get_logged_in()
	terms = response.form.get('search')
	


@app.route('/link/delete/<linkid>', methods = ['POST', 'GET'])
@force_login
def show_delete_link(linkid):
	usr = User.get_logged_in()
	link = Link.get_by_id(linkid)
	
	if not link.is_owner(usr):
		flash('You do not have permission to delete this link.', 'error')
	else:
		if request.form.get('confirm'):
			link.delete()
			flash('Deleted link', 'success')
			return redirect(url_for('show_index'))
		elif request.form.get('cancel'):
			return redirect(request.form.get('referer'))
	return render_template("link_delete.html", pageoptions = get_default_data(), link=link)

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
		abort(404)
	usr = User.get_logged_in()
	#if usr is not None:
	#    link.get_count(usr).add_hit()
	link.get_hit(usr).add_hit()
	return redirect(link.url)

@app.route('/tags',  defaults = {'username': None})
@app.route('/public/<username>/tags')
def show_user_tag_list(username):
	curr_user = User.get_logged_in()
	
	if username is None:
		username = curr_user.username
		user = curr_user
	elif curr_user and username == curr_user.username:
		user = curr_user
	else:
		user = User.get_by_username(username)
	
	user_owned = curr_user and curr_user.username == username
	
	if user_owned:
		tags = Tag.get_cloud_by_user(user.userid)
		title = "My Tags"
	else:
		tags = Tag.get_public_by_user(user.userid)
		title = 'Tags for %s' % username
	
	return render_template('tag_index.html', pageoptions = get_default_data(), tags = tags, page_title = title, section_title = title, user_owned = user_owned)
	
@app.route('/public/tag/<name>')
def show_tag(name):
	usr = User.get_logged_in()
	links = Link.get_public_by_tag(name)
	title = 'Links for Tag - "%s"' % name
	return render_template('link_index.html',pageoptions = get_default_data(),  user = usr, links = links, section_title = title, page_title = title)
	
@app.route('/tag/<name>')
@force_login
def show_user_tag(name):
	usr = User.get_logged_in()
	links = Link.get_by_tag(name, usr.userid)
	title = 'My Tagged Links - "%s"' % name
	return render_template('link_index.html', pageoptions = get_default_data(), user = usr, links = links, section_title = title, page_title = title)

# Wildcard route - THIS MUST BE PROCESSED LAST    
@app.route('/<shorturl>')
def show_shorturl(shorturl):
	link = Link.get_by_shortname(shorturl)
	if link is None:
		abort(404)
	usr = User.get_logged_in()
	link.get_hit(usr).add_hit()
	#if usr is not None:
	#    link.get_count(usr).add_hit()
	return redirect(link.url)
