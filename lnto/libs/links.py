import sqlite3
import db
from lnto.libs.db import get_db
from datetime import datetime

class Link(db.ActiveRecord):

	table = 'links'
	key = ['linkid']
	fields = {
		'name': '',
		'url': '',
		'description': '',
		'shortname': None,
		'userid': 0,
		'linkid': 0
	}
	count = None
	
	def save(self):
		if self.shortname == '':
			self.shortname = None
		super(Link, self).save()
	
	def get_count(self, user = None):
		if self.count is None:
			uid = self.userid if user is None else user.userid
			cnt = LinkCount.get_by({'userid': uid, 'linkid': self.linkid})
			self.count = cnt[0] if len(cnt) > 0 else None
			if self.count is None:
				self.count = LinkCount({'userid': self.userid, 'linkid': self.linkid})
				self.count.insert()
		return self.count
	
	def get_hit(self, user=None):
		data = {'linkid': self.linkid}
		if user is not None:
			data['userid'] = user.userid
		return LinkHit(data)
	
	@staticmethod
	def get_by_user(userid):
		return Link.get_by({'userid': userid})
	
	@classmethod
	def get_by_shortname(cls, name):
		return cls.getone_by('shortname', name)

class LinkHit(db.ActiveRecord):
	table = "links_hits"
	key = ['hitid']
	fields = {
		'hitid': 0,
		'linkid': 0,
		'userid': None,
		'ts': 0
	}
	
	def add_hit(self):
		self.ts = datetime.now()
		self.insert()
	
	def get_count(self):
		data = {'linkid': self.linkid}
		where = 'linkid = :linkid'
		if self.userid is not None:
			data['userid'] = self.userid
			where += " AND userid = :userid"
		results = self.query_select("COUNT(*) AS cnt", where, data)
		return results[0]['cnt'] if len(results) > 0 else 0
	
	def get_last_hit(self):
		data = {'linkid': self.linkid}
		where = 'linkid = :linkid'
		if self.userid is not None:
			data['userid'] = self.userid
			where += " AND userid = :userid"
		results = self.query_select("MAX(ts) AS last_access", where, data)
		return results[0]['last_access'] if len(results) > 0 else 0

class LinkCount(db.ActiveRecord):
	table = "links_counts"
	auto_incrementing_id = False
	key = ['linkid', 'userid']
	fields = {
		'linkid': 0,
		'userid': 0,
		'hit_count': 0,
		'last_hit': datetime.now()
	}
	
	def add_hit(self):
		self.hit_count += 1
		self.last_hit = datetime.now()
		self.update()