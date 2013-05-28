from lnto import appdb
from datetime import datetime

from sqlalchemy.orm import relationship, backref
from sqlalchemy import ForeignKey, Table, Column, Integer, String, DateTime, Boolean, Text

folder_links = Table('folder_links', appdb.Model.metadata,
	Column('folderid', Integer, ForeignKey('folders.folderid')),
	Column('linkid', Integer, ForeignKey('links.linkid'))
)

folder_children = Table('folder_children', appdb.Model.metadata,
	Column('parentid', Integer, ForeignKey('folders.folderid')),
	Column('childid', Integer, ForeignKey('folders.folderid'))
)

class Folder(appdb.Model):
	__tablename__ = 'folders'
	
	folderid = Column(Integer, primary_key = True)
	userid = Column(Integer)
	name = Column(String(255))
	description = Column(Text, default = '')
	added = Column(DateTime, default = datetime.now())
	is_public = Column(Boolean, default = True)
	
	links = relationship('Link', secondary = folder_links)
	#children = relationship('Folder', secondary = folder_children, foreign_keys = 'folder_children.parentid', backref = "parents")
	
	#table = 'folders'
	#key = ['linkid']
	#fields = {
	#	'name': '',
	#	'description': '',
	#	'created': datetime.now(),
	#	'userid': 0,
	#	'folderid': 0
	#}
	#
	#children = []
	#
	#def add_child(self, item):
	#	if isinstance(item, Link):
	#		self.add_child_link(item)
	#	elif isinstance(item, Folder):
	#		self.add_child_folder(item)
	#	else:
	#		raise Exception("Unsupported item type")
	#
	#def add_child_folder(self, child):
	#	sql = """INSERT INTO folder_tree (ancestor, descendant, item_depth)
	#			SELECT ancestor, :new_folderid, item_depth + 1
	#			FROM folder_tree AS t
	#			WHERE t.descendant = :parent_folderid """
	#	data = {'new_folderid': child.folderid, 'parent_folderid': self.folderid}
	#	get_db().execute(sql, data)
	#	get_db().commit()
	#
	#def add_child_link(self, link):
	#	sql = "INSERT INTO folder_links (folderid, linkid) VALUES (:folderid, :linkid)"
	#	data = {'folderid': self.folderid, 'linkid': link.linkid}
	#	get_db().execute(sql, data)
	#	get_db().commit()
	#
	#def get_tree(self):
	#	sql = """SELECT ft.descendant, ft.item_depth, f.*
	#			FROM folders AS f JOIN folder_tree AS ft
	#			ON f.folderid = ft.descendant
	#			WHERE ft.ancestor = :folderid"""
	#
	#def get_children(self):
	#	sql = """SELECT ft.descendant, ft.item_depth, f.*
	#			FROM folders AS f JOIN folder_tree AS ft
	#			ON f.folderid = ft.descendant
	#			WHERE ft.ancestor = :folderid"""
	#	data = {'folderid': self.folderid}
	#
	#@staticmethod
	#def get_user_hierarchy(userid):
	#	sql = """SELECT ft.descendant, ft.item_depth, f.*
	#			FROM folders AS f JOIN folder_tree AS ft
	#			ON f.folderid = ft.descendant
	#			WHERE ft.ancestor = :folderid"""
	
	