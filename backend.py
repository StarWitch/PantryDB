#!/usr/bin/env python
import MySQLdb
import sys

class PantryDB(object):
	'''
	PantryDB Database class 

	status() returns connected status in True/False
	connect() connects to the database with provided information
	disconnect() is self-explanatory
	check_db() ensures the database has been initialized
	reset_db() wipes the database and makes it a clean slate
	get_maximum() returns the highest item ID in the database
	display_db() reads the entire table of information 
	update_row_db(), insert_row_db(), remove_row_db() all update, insert, and remove information from the database
	select_one() returns the information in one row of the database
	
	'''
	def __init__(self, hostname, username, password, database, table):
		self.hostname = hostname
		self.username = username
		self.password = password
		self.database = database
		self.table = table
		self.connection = False
		self.maximum = 0

	def status(self):
		''' Check if the database is connected or not '''
		try:
			self.cursor = self.connection.cursor()
			self.cursor.execute("SELECT VERSION()") 
			version = self.cursor.fetchone()
			return True # if it can get a version, then it's turned on
		except:
			return False # otherwise, it probably isn't

	def connect(self):
		''' Initializes database with arguments passed to __init__ during instantiation '''
		try:
			self.connection = MySQLdb.connect(self.hostname, self.username, \
												self.password, self.database)

			self.cursor = self.connection.cursor()
			self.cursor.execute("SELECT VERSION()")
			version = self.cursor.fetchone()
			result = [True, (version)]
			return result # return the version number and "True"
		
		except MySQLdb.Error, error:
			result = [False, "ERROR %d: %s" % (error.args[0], error.args[1])]
			return result # return the error and "False"

	def disconnect(self):
		try:
			if (self.connection): # if database is connected
				self.connection.close()
				self.connection = False
				return True
		except:
			return False

	def check_db(self):
		''' Checks to see if database has information in it '''
		try:	
			if (self.connection):
				try:
					self.cursor.execute("SELECT * FROM %s WHERE ID = '1'" % self.table) # select the first item
					return True
				except:
					return False
		except MySQLdb.Error, error:
			return [False, "ERROR %d: %s" % (MySQLdb.Error.args[0], MySQLdb.Error.args[1])] 
		except: 
			return False

	def reset_db(self, reset_enable):
		''' 
		Wipes the database and instantiates the expected table layout for PantryDB 
		Layout = auto-incrementing ID, name, description, quantity of item, and last-modified date
		'''
		try:
			if reset_enable: 
				self.cursor.execute("DROP TABLE IF EXISTS %s" % self.table)
				self.cursor.execute("CREATE TABLE %s(id INT NOT NULL AUTO_INCREMENT, \
					PRIMARY KEY(id), name VARCHAR(25), description VARCHAR(50), \
					qty VARCHAR(10), modified TIMESTAMP)" % self.table)
				self.connection.commit()
				return True
		except:
			return False # if it failed

	def get_maximum(self):
		''' check to see what is the highest ID number in the database '''
		try:
			self.cursor.execute("SELECT * FROM %s ORDER BY id DESC LIMIT 1" % self.table)
			return (self.cursor.fetchone()[0] + 1)
		except TypeError:
			return False # if it doesn't exist
	
	def display_db(self):
		''' displays information from the entire table '''
		try:
			self.cursor.execute("SELECT * FROM %2s" % (self.table)) # select all info from table
			infoset = self.cursor.fetchall() # get all items

			titles = self.cursor.description # get titles of the table columns
			db_data = []
			for row in infoset:
				db_data.append(row) # append new data for each item in the table
			
			return_data = []
			return_data.append(titles) # append the titles first
			return_data.append(db_data)

			return return_data
		except:
			return False

	def insert_row_db(self, name, description, qty):
		''' Inserts new information into the specified table '''
		try:
			self.cursor.execute("INSERT INTO %s(name, description, qty) \
				VALUES('%2s', '%3s', '%4s')" % (self.table, name, description, qty))
			self.connection.commit() # completes the transaction
		except MySQLdb.Error, error:
			return [False, "ERROR %d: %s" % (error.args[0], error.args[1])] # output the error

	def update_row_db(self, args):
		'''  Updates currently-existing information '''
		try: 
			self.cursor.execute("UPDATE %s SET name = '%2s', \
				description = '%3s', qty = '%4s' WHERE id = '%5s'" % \
				(self.table, args[1], args[2], args[3], args[0])) # name, description, quantity, ID number
			self.connection.commit() # completes the transaction
			return True
		except:
			return False

	def remove_row_db(self, id_num):
		''' Deletes information from database '''
		try:
			self.cursor.execute("DELETE FROM %s WHERE id='%2s'" % (self.table, \
				id_num))
			self.connection.commit() # completes the transaction
			return True
		except:
			return False

	def select_one(self, id_num):
		''' selects one item from the database based on ID number '''
		try:
			self.cursor.execute("SELECT * FROM %s WHERE id='%2s'" % \
				(self.table, id_num))
			return self.cursor.fetchone() # return one item by ID number
		except TypeError:
			return False # returns False if ID number does not exist