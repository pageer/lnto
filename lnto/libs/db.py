import sqlite3
from flask import g

DB_PATH = ''
INSTANCE = None

def get_db(factory = None):
	try:
		if not hasattr(g, 'db'):
			g.db = sqlite3.connect(DB_PATH)
		ret = g.db
	except NameError, AttributeError:
		if INSTANCE is None:
			INSTANCE = sqlite3.connect(DB_PATH)
		ret = INSTANCE
	ret.row_factory = factory
	return ret

class ActiveRecord:
	"""A very simple implementation of the active record pattern.
	
	Currently, this handles only simple entities that are stored entirely
	within a single row of a database table.  It expects the table to have a
	single-column key which is auto-incrementing.
	"""
	
	fields = {}
	table = ''
	key = ''
	
	def __init__(self, row = None):
		for key in self.fields.keys():
			if row is None:
				val = self.fields[key]
			else:
				val = row[key] if row.get(key) != None else self.fields[key]
			setattr(self, key, val)
	
	def getDict(self):
		ret = {}
		for key in self.fields.keys():
			ret[key] = getattr(self, key)
		return ret
	
	def save(self):
		if getattr(self, self.key) == self.fields[self.key]:
			self.insert()
		else:
			self.update()
	
	def update(self):
		sql = "UPDATE " + self.table + " SET "
		for field in self.fields.keys():
			if field != self.key:
				sql += field + " = :" + field + ", "
		sql = sql[:-2] + " WHERE " + self.key + " = :" + self.key
		get_db().execute(sql, self.getDict())
		get_db().commit();
	
	def insert(self):
		sql = "INSERT INTO " + self.table
		fields = ' ('
		values = ' ('
		for field in self.fields.keys():
			if field != self.key:
				values = values + ':' + field + ', '
				fields = fields + field + ', '
		fields = fields[:-2] + ')'
		values = values[:-2] + ')'
		sql += fields + ' VALUES ' + values
		curr = get_db().execute(sql, self.getDict())
		get_db().commit();
		setattr(self, self.key, curr.lastrowid)
	
	@staticmethod
	def get_by(table, fields, return_class = None, return_cursor = False):
		sql = "SELECT * FROM " + table + " WHERE "
		for field in fields.keys():
			sql += field + ' = :' + field + ' AND '
		sql = sql[:-5]
		curr = get_db(RowDict).execute(sql, fields)
		if return_cursor:
			return curr
		elif return_class is not None:
			ret = []
			for row in curr.fetchall():
				ret.append(return_class(row))
			return ret
		else:
			return curr.fetchall()
	
class RowDict(sqlite3.Row):
	def get(self, key, default = None):
		try:
			return self[key]
		except:
			return default
