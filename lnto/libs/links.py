import sqlite3
from lnto import appdb
from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text

class Link(appdb.Model):
	__tablename__ = 'links'
	
	linkid = Column(Integer, primary_key = True)
	userid = Column(Integer)
	name = Column(String(256))
	url = Column(Text)
	description = Column(Text)
	shortname = Column(String(256))
	added = Column(DateTime)
	is_public = Column(Boolean)
	
	count = None
	
	def __init__(self, row = None):
		if row is not None:
			self.name = row['name'] if row.get('name') else ''
			self.url = row['url'] if row.get('url') else ''
			self.description = row['description'] if row.get('description') else ''
			self.shortname = row['shortname'] if row.get('shortname') else None
			self.added = row['added'] if row.get('added') else datetime.now()
			self.is_public = row['is_public'] if row.get('is_public') else 1
			self.userid = row['userid'] if row.get('userid') else 0
			self.linkid = row['linkid'] if row.get('linkid') else 0
	
	def save(self):
		if self.shortname == '':
			self.shortname = None
		appdb.session.add(self)
		appdb.session.commit()
	
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
	def get_by_id(id):
		return appdb.session.query(Link).filter_by(linkid = id).first()

	@staticmethod
	def get_by_user(userid):
		return appdb.session.query(Link).filter_by(userid = userid).all()
	
	@staticmethod
	def get_public_by_user(userid):
		return appdb.session.query(Link).filter_by(userid = userid, is_public = 1).all()
	
	@classmethod
	def get_by_shortname(cls, name):
		return appdb.session.query(Link).filter_by(shortname = name).first()

class LinkHit(appdb.Model):
	__tablename__ = "links_hits"
	
	hitid = Column(Integer, primary_key = True)
	linkid = Column(Integer)
	userid = Column(Integer)
	ts = Column(DateTime)
	
	def __init__(self, row = None):
		if row is not None:
			self.hitid = row['hitid'] if row.get('hitid') else None
			self.linkid = row['linkid'] if row.get('linkid') else 0
			self.userid = row['userid'] if row.get('userid') else None
			self.ts = row['ts'] if row.get('ts') else None
	
	
	def add_hit(self):
		self.ts = datetime.now()
		appdb.session.add(self)
		appdb.session.commit()
	
	def get_count(self):
		if self.userid:
			return appdb.session.query(LinkHit).filter_by(linkid = self.linkid, userid = self.userid).count()
		else:
			return appdb.session.query(LinkHit).filter_by(linkid = self.linkid).count()
	
	def get_last_hit(self):
		if self.userid:
			return appdb.session.query(appdb.func.max(LinkHit.ts)).select_from(LinkHit).filter_by(linkid = self.linkid, userid = self.userid).scalar()
		else:
			return appdb.session.query(appdb.func.max(LinkHit.ts)).select_from(LinkHit).filter_by(linkid = self.linkid).scalar()

class LinkCount(appdb.Model):
	__tablename__ = "links_counts"
	linkid = Column(Integer, primary_key = True)
	userid = Column(Integer, primary_key = True)
	hit_count = Column(Integer)
	last_hit = Column(DateTime)
	
	def __init__(self, row = None):
		if row is not None:
			self.linkid = row['linkid'] if row.get('linkid') else None
			self.userid = row['userid'] if row.get('userid') else None
			self.hit_count = row['hit_count'] if row.get('hit_count') else None
			self.last_hit = row['last_hit'] if row.get('last_hit') else None
	
	def add_hit(self):
		self.hit_count += 1
		self.last_hit = datetime.now()
		appdb.session.add(self)
		appdb.session.commit()
