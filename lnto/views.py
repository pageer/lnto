from flask import render_template, make_response, redirect, abort, url_for, flash, request
from flask_login import login_required, login_user, logout_user, current_user #pylint: disable=import-error
import lnto.forms as forms
from lnto import app
from lnto.libs.dashboard import Dashboard, module_type_map
from lnto.libs.importer import LinkImporter
from lnto.libs.links import Link
from lnto.libs.tags import Tag
from lnto.libs.users import User

def get_base_url():
    return request.url_root


def get_referer():
    return (
        request.form.get('next')
        or request.args.get('next')
        or request.form.get('referer')
        or request.referrer
        or url_for('show_index')
    )


def get_default_data():
    return {
        'base_url': get_base_url(),
        'referer': get_referer(),
        'user_logged_in': current_user is not None,
        'allow_registration': app.config['ALLOW_REGISTRATION'],
        'standalone': request.args.get('framed'),
        'current_user': current_user
    }


@app.route('/about')
def show_about():
    return render_template(
        'about.html',
        pageoptions=get_default_data(),
        version=app.config['APP_VERSION']
    )


@app.route('/login', methods=['GET', 'POST'])
def do_login():
    #if current_user:
        #return redirect(url_for('show_index'))
    if request.method == 'POST':
        valid = False
        curr_user = User.get_by_username(request.form.get('username'))
        if curr_user:
            valid = curr_user.check_password(request.form.get('password'))
        if valid:
            login_user(curr_user)
            return make_response(redirect(request.form.get('referer') or url_for('show_index')))
        error = 'Either your username or password is wrong'
        return render_template('login.html', pageoptions=get_default_data(), error=error)
    return render_template('login.html', pageoptions=get_default_data())


@app.route('/logout', methods=['GET', 'POST'])
def do_logout():
    logout_user()
    return make_response(redirect(url_for('do_login')))


@app.route('/users/new', methods=['GET', 'POST'])
def do_add_user():
    if not app.config['ALLOW_REGISTRATION']:
        abort(403)

    form = forms.AddUser(request.form)
    if form.validate_on_submit():
        usr = User()
        usr.username = request.form['username']
        usr.set_password(request.form['password'])
        usr.signup_ip = request.remote_addr
        usr.save()
        return redirect(url_for('show_index'))
    return render_template(
        "new_user.html",
        form=form,
        pageoptions=get_default_data()
    )

@app.route('/user/password/change', methods=['GET', 'POST'])
@login_required
def change_password():
    form = forms.ChangePassword(request.form)
    if form.validate_on_submit():
        current_user.set_password(form.new_password.data)
        current_user.save()
        redirect(url_for('do_login'))
    return render_template(
        'change_password.html',
        form=form,
        pageoptions=get_default_data()
    )


@app.route('/')
@login_required
def show_index():
    dashboard = Dashboard(current_user.userid)
    data = dashboard.render()
    return render_template(
        'homepage.html',
        pageoptions=get_default_data(),
        user=current_user,
        dashboard=data
    )


@app.route('/modules/add', methods=['GET', 'POST'])
@login_required
def show_add_module():
    dash = Dashboard(current_user.userid)
    mods = dash.get_modules()
    modtype = request.form.get('mod_type')
    if request.method == 'POST' and modtype and module_type_map.get(int(modtype)):
        mod = module_type_map[int(modtype)]
        if mod.config_required:
            return redirect(url_for('do_add_module', modtype=request.form.get('mod_type')))

        pos = dash.get_next_position()
        try:
            dash.add_module(int(modtype), int(pos))
            flash('Module added.', 'success')
            return redirect(url_for('show_index'))
        except Exception as ex:
            flash(str(ex), 'error')

    return render_template(
        'module_available.html',
        pageoptions=get_default_data(),
        module_types=module_type_map,
        modules=mods
    )


@app.route('/modules/add/<modtype>', methods=['GET', 'POST'])
@login_required
def do_add_module(modtype):
    dash = Dashboard(current_user.userid)
    mod = module_type_map[int(modtype)](current_user.userid)

    if request.method == 'POST':
        mod_type = request.form.get('module_type')
        pos = request.form.get('position') or dash.get_next_position()
        if mod_type:
            try:
                dash.add_module(int(mod_type), int(pos), request.form)
                flash('Module added.', 'success')
                return redirect(url_for('show_index'))
            except Exception as ex:
                flash(str(ex), 'error')
        else:
            flash('You must supply a module type.', 'error')

    return render_template('module_add.html', pageoptions=get_default_data(),
                           user=current_user, dashboard=dash, module=mod,
                           post_view=url_for('do_add_module', modtype=mod.typeid))


@app.route('/modules/config/<moduleid>', methods=['GET', 'POST'])
@login_required
def do_module_config(moduleid):
    dash = Dashboard(current_user.userid)
    mod = dash.get_single_module(moduleid)

    if not mod:
        abort(404)

    if request.method == 'POST':
        try:
            mod.save_config(request.form)
            flash('Module config saved.', 'success')
            return redirect(url_for('show_index'))
        except Exception as ex:
            flash(str(ex), 'error')

    return render_template('module_add.html', pageoptions=get_default_data(),
                           user=current_user, dashboard=dash, module=mod.module,
                           post_view=url_for('do_module_config', moduleid=moduleid),
                           title='Configure Module')


@app.route('/modules/remove/<moduleid>')
@login_required
def do_remove_module(moduleid):
    dash = Dashboard(current_user.userid)
    if dash.remove_module(moduleid):
        flash('Module deleted', 'success')
    else:
        flash('Could not delete module', 'error')
    return redirect(url_for('show_index'))


@app.route('/public/<username>/')
def show_user(username):
    usr = User.get_by_username(username)
    links = Link.get_public_by_most_recent(usr.userid, 30)
    tags = Tag.get_public_by_user(usr.userid)
    return render_template(
        'public_dashboard.html',
        pageoptions=get_default_data(),
        tags=tags,
        links=links,
        user=usr,
        curr_user=current_user
    )


@app.route('/links', defaults={'username': None})
@app.route('/public/<username>/links')
def show_user_index(username):
    if username is None:
        usr = current_user
    else:
        usr = User.get_by_username(username)

    if not usr:
        abort(404)

    if usr is current_user:
        links = Link.get_by_user(current_user.userid)
    else:
        links = Link.get_public_by_user(usr.userid)
    return render_template(
        'link_index.html',
        pageoptions=get_default_data(),
        links=links,
        user=current_user
    )


@app.route('/link/add', methods=['GET', 'POST'])
@login_required
def do_add_link():
    req = request.form if request.method == 'POST' else request.args
    form = forms.AddLink(req, referer=get_referer())

    data = form.data
    data['userid'] = current_user.userid

    options = {
        'button_label': 'Add Link',
        'post_view': req.get('post_view') if req.get('post_view') else url_for('do_add_link'),
    }

    link = Link(data)

    if request.method == 'POST' or request.args.get('submit') == '1 ':

        if link.already_exists():
            flash('This link already exists.  Try editing it instead.', 'error')
            return redirect(url_for('do_edit_link', linkid=link.linkid))

        taglist = form.tags.data.split(',') if form.tags.data else []
        link.set_tags(taglist)

        if form.validate():
            link.save()
            redir_target = link.url if form.redirect_to_target else get_referer()
            return redirect(redir_target)
        flash('Invalid link submission', 'error')
        return str(form.errors)

    tags = Tag.get_by_user(current_user.userid)

    return render_template(
        "link_add.html",
        pageoptions=get_default_data(),
        form=form,
        link=link,
        tags=tags,
        options=options
    )

@app.route('/link/add/fetch', defaults={'url': None}, methods=['GET', 'POST'])
@app.route('/link/add/fetch/<url>', methods=['GET', 'POST'])
@login_required
def do_add_from_url(url):
    fetch_url = url or request.form.get('fetch_url')
    if fetch_url:
#        try:
            link = Link.create_from_url(fetch_url)
            redir_url = url_for(
                'do_add_link',
                name=link.name,
                url=link.url,
                description=link.description,
                redirect_to_target=1
            )
            return redirect(redir_url)
#        except Exception as ex:
            flash('Error getting link - ' + str(ex), 'error')
    return render_template('link_add_url.html', pageoptions=get_default_data(), url=fetch_url or '')


@app.route('/link/edit/<linkid>', methods=['GET', 'POST'])
@login_required
def do_edit_link(linkid):
    errors = []

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
        link.is_public = request.form.get('is_public') == '1'

        if request.form.get('tags').strip() == '':
            taglist = []
        else:
            taglist = request.form.get('tags').split(',')

        link.set_tags(taglist)

        if not (request.form.get('name') and request.form.get('url')):
            errors.append("Name and URL are required")

        if errors:
            link.save()
            if request.form.get('referer'):
                return redirect(request.form.get('referer'))

    tags = Tag.get_by_user(current_user.userid)

    return render_template(
        "link_add.html",
        pageoptions=get_default_data(),
        link=link,
        options=options,
        tags=tags,
        errors=errors
    )


@app.route('/links/manage/<tags>', methods=['POST', 'GET'])
@app.route('/links/manage/', methods=['POST', 'GET'], defaults={'tags': None})
@login_required
def do_bulk_edit(tags):
    # Redirect filters immediately
    if request.args.get('tag_select'):
        return redirect(url_for('do_bulk_edit', tags=request.args.get('tag_select')))

    available_tags = Tag.get_by_user(current_user.userid)

    if request.method == 'POST':

        linkids = request.form.getlist('linkids')
        edit_links = Link.get_by_id(linkids)

        valid = _links_are_valid(edit_links)
        tag_text = request.form.get('tag_text')

        if valid and tag_text and request.form.get('tag_submit'):
            for link in edit_links:
                link.add_tag(tag_text)
                link.save()
            flash('Tagged %d links as "%s"' % (
                len(edit_links), tag_text
            ), 'success')
        elif valid and tag_text and request.form.get('tag_remove'):
            for link in edit_links:
                link.remove_tag(tag_text)
                link.save()
            flash('Removed tag "%s" from %d links' % (
                tag_text, len(edit_links)
            ), 'success')

        if valid and request.form.get('set_privacy') and request.form.get('privacy_submit'):
            _set_link_privacy(edit_links, request.form.get('set_privacy'))

        if valid and request.form.get('delete_selected_submit'):
            for link in edit_links:
                link.delete()
            flash('Deleted %s links' % len(edit_links), 'success')

    if tags == 'untagged':
        title = 'Manage Untagged Links'
        links = Link.get_untagged(current_user.userid)
    elif tags:
        taglist = tags.split(',')
        title = 'Manage Links in ' + tags
        links = Link.get_by_tag(taglist[0], current_user.userid)
    else:
        title = "Manage Links"
        links = Link.get_by_user(current_user.userid)

    return render_template(
        "link_edit_bulk.html",
        pageoptions=get_default_data(),
        url_tags=tags,
        links=links,
        section_title=title,
        tags=available_tags
    )


def _links_are_valid(edit_links):
    for link in edit_links:
        if not link.is_owner(current_user):
            flash("You do not have permission to edit all of the selected links.", 'error')
            return False
    return True

def _set_link_privacy(edit_links, access):
    for link in edit_links:
        link.is_public = access == 'public'
        link.save()
    flash('Marked %d links %s' % (
        len(edit_links),
        'public' if access == 'public' else 'private'
    ), 'success')

#@app.route('/link/search', methods=['POST'])
#def do_link_search():
    #usr = User.get_logged_in()
    #terms = response.form.get('search')


@app.route('/link/delete/<linkid>', methods=['POST', 'GET'])
@login_required
def show_delete_link(linkid):
    link = Link.get_by_id(linkid)
    if not link.is_owner(current_user):
        flash('You do not have permission to delete this link.', 'error')
    elif request.form.get('confirm'):
        link.delete()
        flash('Deleted link', 'success')
        return redirect(url_for('show_index'))
    elif request.form.get('cancel'):
        return redirect(request.form.get('referer'))
    return render_template("link_delete.html", pageoptions=get_default_data(), link=link)


@app.route('/links/import', methods=['GET', 'POST'])
@login_required
def show_import():
    if request.method == 'POST':
        bookmarkfile = request.files.get('bookmarkfile')
        if bookmarkfile:
            markup = bookmarkfile.read()
            bookmarkfile.close()
        else:
            markup = request.form.get('importtext')
        import_type = request.form.get('importtype')
        importer = LinkImporter(markup, import_type)
        results = importer.convert()
    else:
        markup = ''
        results = None
    return render_template(
        'link_import.html',
        pageoptions=get_default_data(),
        import_file=markup,
        results=results
    )


@app.route('/link/show/<linkid>')
def show_link(linkid):
    link = Link.get_by_id(linkid)
    if link is None:
        abort(404)
    if link.is_owner(current_user):
        related = Link.get_recent_by_tag(link.get_taglist(), current_user.userid)
    else:
        related = Link.get_recent_public_by_tag(link.get_taglist(), link.userid)

    return render_template(
        'link.html',
        pageoptions=get_default_data(),
        link=link,
        user=current_user,
        related=related
    )


@app.route('/to/<linkid>')
def show_linkurl(linkid):
    link = Link.get_by_id(linkid)
    if link is None:
        abort(404)
    link.get_hit(current_user).add_hit()
    return redirect(link.url)


@app.route('/tags/', defaults={'username': None})
@app.route('/public/<username>/tags/')
def show_user_tag_list(username):
    if username is None:
        username = current_user.username
        user = current_user
    elif current_user and username == current_user.username:
        user = current_user
    else:
        user = User.get_by_username(username)

    user_owned = current_user and current_user.username == username

    if user_owned:
        tags = Tag.get_cloud_by_user(user.userid)
        title = "My Tags"
    else:
        tags = Tag.get_public_by_user(user.userid)
        title = 'Tags for %s' % username

    return render_template(
        'tag_index.html',
        pageoptions=get_default_data(),
        tags=tags,
        curr_user=current_user,
        page_title=title,
        section_title=title,
        user_owned=user_owned,
        user=user
    )


@app.route('/public/tags/<name>')
def show_tag(name):
    links = Link.get_public_by_tag(name)
    title = 'Links for Tag - "%s"' % name
    return render_template(
        'link_index.html',
        pageoptions=get_default_data(),
        user=None,
        curr_user=current_user,
        links=links,
        section_title=title,
        page_title=title
    )


@app.route('/public/<username>/tags/<name>')
def show_all_user_tagged(name, username):
    user = User.get_by_username(username)
    links = Link.get_public_by_tag(name, user.userid)
    title = 'Links for tag "%s" by %s' % (name, user.username)
    return render_template(
        'link_index.html',
        pageoptions=get_default_data(),
        user=user,
        curr_user=current_user,
        links=links,
        section_title=title,
        page_title=title
    )


@app.route('/tags/<name>')
@login_required
def show_user_tag(name):
    links = Link.get_by_tag(name, current_user.userid)
    title = 'My Tagged Links - "%s"' % name
    return render_template(
        'link_index.html',
        pageoptions=get_default_data(),
        user=current_user,
        links=links,
        section_title=title,
        page_title=title
    )


# Wildcard route - THIS MUST BE PROCESSED LAST
@app.route('/<shorturl>')
def show_shorturl(shorturl):
    link = Link.get_by_shortname(shorturl)
    if link is None:
        abort(404)
    link.get_hit(current_user).add_hit()
    return redirect(link.url)
