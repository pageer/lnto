import re
import lnto.libs.links

from lnto import appdb
from datetime import datetime
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey, Table, Column, Integer, String

link_tags = Table('link_tags', appdb.Model.metadata,
	Column('linkid', Integer, ForeignKey('links.linkid')),
	Column('tagid', Integer, ForeignKey('tags.tagid'))
)

link_display_tags = Table('link_display_tags', appdb.Model.metadata,
	Column('linkid', Integer, ForeignKey('links.linkid')),
	Column('tagid', Integer, ForeignKey('display_tags.tagid'))
)

class Tag(appdb.Model):
	__tablename__ = 'tags'
	tagid = Column(Integer, primary_key = True)
	tag_name = Column(String(64), unique = True)
	
	links = relationship('Link', secondary = link_tags)
	
	def __init__(self, name = None):
		if name:
			self.tag_name = name
	
	def __str__(self):
		return self.tag_name
	
	@staticmethod
	def get_by_name(name):
		tag = appdb.session.query(Tag).filter_by(tag_name = name).first()
		if tag is None:
			tag = Tag(name)
		return tag
	
	@staticmethod
	def get_public():
		return appdb.session.query(Tag).filter(lnto.libs.links.Link.is_public == True).all()

	@staticmethod
	def get_by_user(userid):
		return appdb.session.query(Tag).filter(lnto.libs.links.Link.userid == userid).all()
	
	@staticmethod
	def get_public_by_user(userid):
		return appdb.session.query(Tag).filter(lnto.libs.links.Link.userid == userid, lnto.libs.links.Link.is_public == False).all()
	
	@staticmethod
	def get_cloud_by_user(userid):
		tags = appdb.session.query(Tag, appdb.func.count('*').label('num_links')).join(link_tags, lnto.libs.links.Link).group_by(Tag).order_by('num_links DESC').all()
		ret = []
		for tag in tags:
			t = tag[0]
			t.link_count = tag[1]
			ret.append(t)
		return ret
	
class DisplayTag(appdb.Model):
	__tablename__ = 'display_tags'
	displayid = Column(Integer, primary_key = True)
	tagid = Column(Integer)
	display_name = Column(String(64))
	
	def normalize_tag(self):
		tagname = self.tag_name.lower()
		tagname = re.sub(r'\W', '', tagname)
		return tagname
	
