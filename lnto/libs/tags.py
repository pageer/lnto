import re
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
	
	#links = relationship('Link', secondary = link_tags, backref = 'tags')
	
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
		return appdb.session.query(Tag).filter(Links.is_public == True).all()

	@staticmethod
	def get_by_user(userid):
		return appdb.session.query(Tag).filter(Links.userid == userid).all()
	
	@staticmethod
	def get_public_by_user(userid):
		return appdb.session.query(Tag).filter(Links.userid == userid, Links.is_public == False).all()
	
class DisplayTag(appdb.Model):
	__tablename__ = 'display_tags'
	displayid = Column(Integer, primary_key = True)
	tagid = Column(Integer)
	display_name = Column(String(64))
	
	def normalize_tag(self):
		tagname = self.tag_name.lower()
		tagname = re.sub(r'\W', '', tagname)
		return tagname
	