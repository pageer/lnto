import time, datetime
from lnto import app
from flask import render_template, make_response, redirect, jsonify, abort, url_for, request, session, g
from lnto.libs.links import Link
from lnto.libs.users import User
from lnto.libs.decorators import check_api_login

@app.route('/api/link/<linkid>')
@check_api_login
def get_link_metadata(linkid):
	pass

@app.route('/api/folder/<path>')
@check_api_login
def get_folder(path):
	pass

