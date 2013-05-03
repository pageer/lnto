import sqlite3
import db
from lnto.libs.db import get_db
from datetime import datetime

class Folder(da.ActiveRecord):
	table = 'folders'
	key = ['linkid']
	fields = {
		'name': '',
		'description': '',
		'created': datetime.now(),
		'userid': 0,
		'folderid': 0
	}
	
	children = []
	
	def add_child(self, item):
		if isinstance(item, Link):
			self.add_child_link(item)
		elif isinstance(item, Folder):
			self.add_child_folder(item)
		else:
			raise Exception("Unsupported item type")
	
	def add_child_folder(self, child):
		sql = """INSERT INTO folder_tree (ancestor, descendant, item_depth)
				SELECT ancestor, :new_folderid, item_depth + 1
				FROM folder_tree AS t
				WHERE t.descendant = :parent_folderid """
		data = {'new_folderid': child.folderid, 'parent_folderid': self.folderid}
		get_db().execute(sql, data)
		get_db().commit()
	
	def add_child_link(self, link):
		sql = "INSERT INTO folder_links (folderid, linkid) VALUES (:folderid, :linkid)"
		data = {'folderid': self.folderid, 'linkid': link.linkid}
		get_db().execute(sql, data)
		get_db().commit()
	
	def get_tree(self):
		sql = """SELECT ft.descendant, ft.item_depth, f.*
				FROM folders AS f JOIN folder_tree AS ft
				ON f.folderid = ft.descendant
				WHERE ft.ancestor = :folderid"""
	
	def get_children(self):
		sql = """SELECT ft.descendant, ft.item_depth, f.*
				FROM folders AS f JOIN folder_tree AS ft
				ON f.folderid = ft.descendant
				WHERE ft.ancestor = :folderid"""
		data = {'folderid': self.folderid}
	
	@staticmethod
	def get_user_hierarchy(userid):
		sql = """SELECT ft.descendant, ft.item_depth, f.*
				FROM folders AS f JOIN folder_tree AS ft
				ON f.folderid = ft.descendant
				WHERE ft.ancestor = :folderid"""
		
	
	