import sqlite3
import db
from lnto.libs.db import get_db

class Link(db.ActiveRecord):

	table = 'links'
	key = 'linkid'
	fields = {
		'name': '',
		'url': '',
		'description': '',
		'shortname': None,
		'userid': 0,
		'linkid': 0
	}
	
	@staticmethod
	def get_by_user(userid):
		return Link.get_by('links', {'userid': userid}, return_class = Link)
	
	@staticmethod
	def get_by_id(linkid):
		ret = Link.get_by('links', {'linkid': linkid}, return_class = Link)
		return ret[0] if len(ret) > 0 else None
	
	@staticmethod
	def get_by_shortname(name):
		ret = Link.get_by('links', {'shortname': name}, return_class = Link)
		return ret[0] if len(ret) > 0 else None