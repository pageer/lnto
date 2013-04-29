import sqlite3
from flask import g

import lnto.config
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

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

class ActiveRecord(object):
	"""A very simple implementation of the active record pattern.
	
	Currently, this handles only simple entities that are stored entirely
	within a single row of a database table.  It expects the table to have a
	single-column key which is auto-incrementing.
	"""
	
	fields = {}
	table = ''
	key = []
	auto_incrementing_id = True
	
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
		print (self.key), getattr(self, self.key[0]), self.fields[self.key[0]]
		if len(self.key) == 1 and getattr(self, self.key[0]) == self.fields[self.key[0]]:
			self.insert()
		else:
			self.update()
	
	def update(self):
		sql = "UPDATE " + self.table + " SET "
		for field in self.fields.keys():
			if field != self.key:
				sql += "%s = :%s, " % (field, field)
		sql = sql[:-2] + " WHERE "
		for k in self.key:
			sql += "%s = :%s AND " % (k, k)
		sql = sql[:-5]
		get_db().execute(sql, self.getDict())
		get_db().commit()
	
	def insert(self):
		sql = "INSERT INTO " + self.table
		fields = ' ('
		values = ' ('
		for field in self.fields.keys():
			if self.auto_incrementing_id and field not in self.key:
				values = values + ':' + field + ', '
				fields = fields + field + ', '
		fields = fields[:-2] + ')'
		values = values[:-2] + ')'
		sql += fields + ' VALUES ' + values
		curr = get_db().execute(sql, self.getDict())
		get_db().commit();
		if self.auto_incrementing_id:
			setattr(self, self.key[0], curr.lastrowid)
		return sql
	
	def delete(self):
		sql = "DELETE FROM %s WHERE " % (self.table)
		keyvals = {}
		for k in self.key:
			sql += "%s = :%s AND " % (k, k)
			keyvals[k] = getattr(self, k)
		sql = sql[:-5]
		get_db().execute(sql, keyvals)
		get_db().commit()
	
	@classmethod
	def query_select(cls, fields, where, data):
		sql = "SELECT %s FROM %s WHERE %s" % (fields, cls.table, where)
		curr = get_db(RowDict).execute(sql, data)
		return curr.fetchall()
	
	@classmethod
	def get_by(return_class, fields, return_cursor = False):
		sql = "SELECT * FROM " + return_class.table + " WHERE "
		for field in fields.keys():
			sql += field + ' = :' + field + ' AND '
		sql = sql[:-5]
		curr = get_db(RowDict).execute(sql, fields)
		if return_cursor:
			return curr
		else:
			ret = []
			for row in curr.fetchall():
				ret.append(return_class(row))
			return ret
	
	@classmethod
	def get_by_id(cls, keyval):
		return cls.getone_by(cls.key[0], keyval)
	
	@classmethod
	def getone_by(cls, field, value):
		ret = cls.get_by({field:value})
		return ret[0] if len(ret) >  0 else None
	
class RowDict(sqlite3.Row):
	def get(self, key, default = None):
		try:
			return self[key]
		except:
			return default
