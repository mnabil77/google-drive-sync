#!/usr/bin/env python

"""DatabaseServices.py: Database services - SQLite3"""

__author__      = "Pavel Hosek"
__copyright__   = "Copyright 2014, Pavel Hosek"
__license__		= "Public Domain"
__version__ 	= "1.0"

import os
import sqlite3

class DatabaseService(object):
	"""docstring for ClassName"""
	def __init__(self, name):
		'''
			???

			Args:
			name --
			
			Returns: None
		'''
		self.name = name
		self.tables_exist = None
		
		self.create_conn()
		self.set_tables_exist()
		if self.tables_exist == False:
			self.create_table()
		else:
			print 'APP: The database exists.'

################################################
################## Connection ##################
################################################
	def create_conn(self):
		'''
			???

			Args: None
			
			Returns: None
		'''
		if os.path.isfile(self.name) and self.name != ':memory:':
			self.conn = sqlite3.connect(self.name)
		elif os.path.isfile(self.name) == False and self.name != ':memory:':
			f = file(self.name, "w")
			self.conn = sqlite3.connect(self.name)
		else:
			self.conn = sqlite3.connect(self.name)
		self.cur = self.conn.cursor()

	def get_conn(self):
		'''
			???

			Args: None
			
			Returns: None
		'''
		return self.cur

	def close_conn(self):
		'''
			???

			Args: None
			
			Returns: None
		'''
		self.conn.close()
################################################
################## Connection ##################
################################################

########################################################
################## Table manipulation ##################
########################################################
	def create_table(self):
		'''
			???

			Args: None
			
			Returns: None
		'''
		if self.tables_exist == False:
			self.cur.execute('''CREATE TABLE files (
					id text PRIMARY KEY NOT NULL UNIQUE,
					title text NOT NULL,
					etag text NOT NULL,
					mimeType text NOT NULL,
					createDate text NOT NULL,
					alternateLink text NOT NULL,
					parents text NOT NULL,
					version int NOT NULL,
					originalFilename text,
					fileExtension text,
					fileSize text,
					md5Checksum text,
					path text)''')
			self.cur.execute('''CREATE TABLE folders (
					id text PRIMARY KEY NOT NULL UNIQUE,
					title text NOT NULL,
					parents text,
					version int,
					path text)''')
			self.cur.execute('''CREATE TABLE googleFiles (
					id text PRIMARY KEY NOT NULL UNIQUE,
					title text NOT NULL,
					mimeType text NOT NULL,
					alternateLink text NOT NULL,
					version int NOT NULL)''')
			self.cur.execute('''CREATE TABLE setting (
					sync text PRIMARY KEY NOT NULL UNIQUE,
					folder text NOT NULL,
					folderId text NOT NULL,
					rootFolderId text NOT NULL,
					largestChangeId text,
					quotaBytesByDrive integer,
					quotaBytesByGmail integer,
					quotaBytesByPhotos integer,
					quotaBytesUsedAggregate integer,
					lastAccess integer)''')
			self.tables_exist = True
			print 'APP: The database was created.'
		

	def insert_to_table(self, insert_data):
		'''
			???

			Args:
			insert_data -- 
			
			Returns: None
		'''
		for row in insert_data['Files']:
			self.cur.execute('INSERT OR REPLACE INTO files VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)', row[0])
			self.conn.commit()
		for row in insert_data['Folders']:
			self.cur.execute('INSERT OR REPLACE INTO folders VALUES (?,?,?,?,?)', row[0])
			self.conn.commit()
		for row in insert_data['GoogleFiles']:
			self.cur.execute('INSERT OR REPLACE INTO googleFiles VALUES (?,?,?,?,?)', row[0])
			self.conn.commit()
		del insert_data

	def set_tables_exist(self):
		'''
			???

			Args: None
			
			Returns: None
		'''
		if self.tables_exist == None:
			TABLES = []
			self.cur.execute("SELECT DISTINCT tbl_name FROM sqlite_master")
			self.conn.commit()
			tables = self.cur.fetchall()
			for i in range(0,len(tables)):
				 TABLES.append(tables[i][0])
			if TABLES == ['files', 'folders', 'googleFiles', 'setting']:
				self.tables_exist = True
			else:
				self.tables_exist = False
			self.conn.commit()
########################################################
################## Table manipulation ##################
########################################################

#####################################################
################## synchronization ##################
#####################################################
	def create_sync(self, sync, folder, folderId, rootFolderId):
		'''
			???

			Args:
			sync --
			folder --
			folderId --

			Returns: None
		'''
		self.cur.execute("INSERT INTO setting (sync,folder,folderId,rootFolderId) VALUES (:sync,:folder,:folderId,:rootFolderId)", {'sync': sync, 'folder': folder, 'folderId': folderId, 'rootFolderId': rootFolderId})
		self.conn.commit()

	def update_sync(self, updateData):
		'''
			???

			Args:
			updateData --
			Returns: None
		'''
		#self.cur.execute('UPDATE setting SET lastAccess=:lastAccess, largestChangeId=:largestChangeId, quotaBytesByDrive=:quotaBytesByDrive, quotaBytesByGmail=:quotaBytesByGmail, quotaBytesByPhotos=:quotaBytesByPhotos, quotaBytesUsedAggregate=:quotaBytesUsedAggregate WHERE sync=:sync', {'sync': updateData['sync'], 'lastAccess': updateData['lastAccess'], 'largestChangeId': updateData['largestChangeId'], 'quotaBytesByDrive': updateData'[quotaBytesByDrive]', 'quotaBytesByGmail': updateData['quotaBytesByGmail'], 'quotaBytesByPhotos': updateData['quotaBytesByPhotos'], 'quotaBytesUsedAggregate': updateData['quotaBytesUsedAggregate']})
		self.cur.execute('UPDATE setting SET lastAccess=:lastAccess, largestChangeId=:largestChangeId, quotaBytesByDrive=:quotaBytesByDrive, quotaBytesByGmail=:quotaBytesByGmail, quotaBytesByPhotos=:quotaBytesByPhotos, quotaBytesUsedAggregate=:quotaBytesUsedAggregate WHERE sync=:sync', {'sync': updateData['sync'] , 'lastAccess': updateData['lastAccess'], 'largestChangeId': updateData['largestChangeId'], 'quotaBytesByDrive': updateData['quotaBytesByDrive'], 'quotaBytesByGmail': updateData['quotaBytesByGmail'], 'quotaBytesByPhotos': updateData['quotaBytesByPhotos'], 'quotaBytesUsedAggregate': updateData['quotaBytesUsedAggregate']})
		self.conn.commit()

	def get_data_sync(self, sync):
		'''
			???

			Args:
			sync --

			Returns:
			data_sync
		'''
		self.cur.execute('SELECT sync, folder, folderId, largestChangeId, lastAccess FROM setting WHERE sync=:sync', {'sync': sync})
		self.conn.commit()
		data_sync = self.cur.fetchone()
		return {'sync': data_sync[0],
				'folder': data_sync[1],
				'folderId': data_sync[2],
				'largestChangeId': data_sync[3],
				'lastAccess': data_sync[4]}

	def get_sync_exist(self):
		'''
			???

			Args: None

			Returns:

		'''
		self.cur.execute('SELECT sync FROM setting')
		self.conn.commit()
		sync_name = self.cur.fetchall()
		return sync_name

#####################################################
################## synchronization ##################
#####################################################


#	def get_root_path(self):
#		'''
#			???
#
#			Args: None
#			
#			Returns:
#			root_path --
#		'''
#		self.cur.execute('SELECT path FROM folders WHERE title=:title', {'title': 'root'})
#		self.conn.commit()
#		root_path = self.cur.fetchall()
#		if root_path == []:
#			return None
#		elif (len(root_path) > 1 or len(root_path[0]) > 1):
#			return root_path
#		else:
#			return root_path[0][0]
#
#	def get_root_id(self):
#		'''
#			???
#
#			Args: None
#			
#			Returns:
#			root_id --
#		'''
#		self.cur.execute('SELECT id FROM folders WHERE title=:title', {'title': 'root'})
#		self.conn.commit()
#		root_id = self.cur.fetchall()
#		if root_id == []:
#			return None
#		elif (len(root_id) > 1 or len(root_id[0]) > 1):
#			return root_id
#		else:	
#			return root_id[0][0]
###############################################################

################################################################
#	def get_folders(self, parent):
#		self.cur.execute("SELECT * FROM folders WHERE parents=:par", {"par": parent})
#		self.conn.commit()
#		data = self.cur.fetchall()
#		return data
#
#	def get_parent_data(self, parent_id):
#		self.cur.execute("SELECT title, path FROM folders WHERE id=:id", {"id": parent_id})
#		self.conn.commit()
#		parent_data = self.cur.fetchone()
#		return parent_data
#
#	def get_file_in_folder(self, parent_id):
#		self.cur.execute("SELECT id, originalFilename FROM files WHERE parents=:par", {"par": parent_id})
#		self.conn.commit()
#		files = self.cur.fetchall()
#		return files
#
#	def get_parent_path(self, parent_id):
#		self.cur.execute("SELECT DISTINCT fo.path, fo.title FROM files AS fi JOIN folders AS fo ON fi.parents=fo.id WHERE fo.id=:id", {"id": parent_id})
#		self.conn.commit()
#		path = self.cur.fetchone()
#		return path
#
#	def set_root_folder(self, path, id):
#		data = [id, 'root', '', '', path]
#		self.cur.execute('INSERT OR REPLACE INTO folders VALUES (?,?,?,?,?)', data)
#		self.conn.commit()
#

#
#	def update_path(self, fileType, updateData):
#		if fileType == 'folder':
#			self.cur.execute("UPDATE folders SET path=:path WHERE id=:id", updateData)
#		elif fileType == 'file':
#			self.cur.execute("UPDATE files SET path=:path WHERE parents=:id", updateData)
#		self.conn.commit()
#
#	def folder_exist(self, title, parent_id):
#		self.cur.execute('SELECT title FROM folders WHERE title=:tit AND parents=:par', {'tit': title, 'par': parent_id})
#		self.conn.commit()
#		folder = self.cur.fetchone()
#		if folder != None and folder[0] == title:
#			return True
#		else:
#			return False
#
#	def get_folders_path(self):
#		self.cur.execute('SELECT DISTINCT path FROM folders WHERE title!=:tit', {'tit': 'root'})
#		self.conn.commit()
#		paths = self.cur.fetchall()
#		return paths