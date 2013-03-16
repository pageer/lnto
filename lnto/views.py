import time, datetime
from lnto import app
from flask import render_template, make_response, redirect, jsonify, abort, url_for, request, session, g
from lnto.libs.db import *
from lnto.libs.links import *
from lnto.libs.users import *

@app.route('/login', methods = ['GET', 'POST'])
def do_login():
    curr_user = User.get_logged_in()
    if curr_user:
        return redirect(url_for('show_index'))
    if request.method == 'POST':
        curr_user = User.get_by_username(request.form.get('username'))
        userkey = curr_user.login(request.form.get('password')) if curr_user else None
        if curr_user and userkey:
            response = make_response(redirect(url_for('show_index')))
            response.set_cookie('uinf', userkey, 60*60*24*7, datetime.today() + timedelta(days=20))
            return response
        else:
            error = 'Either your username or password is wrong'
            return render_template('login.html', error = error)
    else:
        return render_template('login.html')

@app.route('/logout', methods = ['GET', 'POST'])
def do_logout():
    usr = User.get_logged_in()
    if usr:
        response = make_response(redirect(url_for('do_login')))
        response.set_cookie('uinf', '', 60*60*24*7, datetime.today() + timedelta(days=20))
    return response

@app.route('/users/new', methods = ['GET', 'POST'])
def do_add_user():
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
            usr.signup_up = request.headers.get('Remote-Addr')
            usr.save()
            return redirect(url_for('show_index'))
        else:
            return render_template("new_user.html", errors = errors)
    else:
        return render_template("new_user.html")

@app.route('/')
def show_index():
    usr = User.get_logged_in()
    if not usr:
        return redirect(url_for('do_login'))
    links = Link.get_by_user(usr.userid)
    return render_template('index.html', links = links);

@app.route('/home/<username>')
def show_user_index(username):
    usr = User.get_by_username(username)
    if not usr:
        abort(404)
    curr_user = User.get_logged_in()
    if usr.userid == curr_user.userid:
        links = Link.get_by_user(curr_user.userid)
    else:
        links = Link.get_public_by_user(usr.userid)
    return render_template('index.html', links = links)

@app.route('/links/add', methods = ['GET', 'POST'])
def do_add_link():
    usr = User.get_logged_in()
    if not usr:
        return redirect(url_for('do_login'))
    
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
        'is_public': 1 if req.get('is_public', 1) else 0,
    }
    options = {
        'button_label': 'Add Link',
        'post_view': url_for('do_add_link')
    }
    
    link = Link(data)
    errors = []
    
    if data['name'] == '' or data['url'] == '':
        errors.append("Name and URL are required")
    
    if request.method == 'POST':
        if len(errors) == 0:
            link.save()
            return redirect(url_for('show_index'))
    else:
        if request.args.get('submit') == '1':
            if len(errors) == 0:
                link.save()
                return redirect(url_for('show_index'))
        else:
            errors = []
    
    return render_template("add_link.html", link = link, options = options, errors = errors)

@app.route('/links/edit/<linkid>', methods = ['GET', 'POST'])
def do_edit_link(linkid):
    usr = User.get_logged_in()
    if not usr:
        return redirect(url_for('do_login'))
    
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
        link.is_public = 1 if request.form.get('is_public') else 0
        
        errors = []
        if not (request.form.get('name') and request.form.get('url')):
            errors.append("Name and URL are required")
        
        if len(errors) == 0:
            link.save()
    return render_template("add_link.html", link=link, options=options)

@app.route('/links/delete/<linkid>', methods = ['POST'])
def do_delete_link(linkid):
    usr = User.get_logged_in()
    if not usr:
        return jsonify({'status': 'error', 'message': 'You must log in to delete a link.'})
    
    link = Link.get_by_id(linkid)
    if not link:
        return jsonify({'status': 'error', 'message': 'That link does not exist.'})
    
    link.delete()
    return jsonify({'status': 'success'})

@app.route('/link/show/<linkid>')
def show_link(linkid):
    usr = User.get_logged_in()
    link = Link.get_by_id(linkid)
    if link is None:
        abort(404)
    return render_template('link.html', link = link, user = usr)

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