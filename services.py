#!/usr/bin/env python

"""Services.py: Google Drive synchronization - services"""

__author__      = "Pavel Hosek"
__copyright__   = "Copyright 2014, Pavel Hosek"
__license__ = "Public Domain"
__version__ = "1.0"

import os
import sys
import time
import sqlite3
import hashlib
import httplib2
import mimetypes

import pprint
#import commands


from apiclient import errors
from apiclient.discovery import build
from apiclient.http import MediaFileUpload
from oauth2client.file import Storage
from oauth2client.client import OAuth2WebServerFlow



class GoogleService(object):
	"""docstring for ClassName"""
	def __init__(self):
		print 'METHOD: GD __init__'
		# Copy your credentials from the console
		CLIENT_ID = '924364520901-u1olb69vujorp07kjc8uq6s43rbqa0cl.apps.googleusercontent.com'
		CLIENT_SECRET = 'zjkkkc00iWHLri0MFvky4GF2'
		# Check https://developers.google.com/drive/scopes for all available scopes
		OAUTH_SCOPE = 'https://www.googleapis.com/auth/drive'
		# Redirect URI for installed apps
		REDIRECT_URI = 'urn:ietf:wg:oauth:2.0:oob'

		
		if os.path.isfile('a_credentials_file') != True:
			# Run through the OAuth flow and retrieve credentials
			flow = OAuth2WebServerFlow(CLIENT_ID, CLIENT_SECRET, OAUTH_SCOPE, REDIRECT_URI)
			authorize_url = flow.step1_get_authorize_url()
			print 'Go to the following link in your browser: ' + authorize_url
			code = raw_input('Enter verification code: ').strip()
			credentials = flow.step2_exchange(code)
			storage = Storage('a_credentials_file')
			storage.put(credentials)
		else:
			storage = Storage('a_credentials_file')
			credentials = storage.get()

		# Create an httplib2.Http object and authorize it with our credentials
		http = httplib2.Http()
		http = credentials.authorize(http)
		self.drive_service = build('drive', 'v2', http=http)

	def get_connection(self):
		print 'METHOD: GD get_connection'
		return self.drive_service

	def get_folder_list(self, folder):
		print 'METHOD: GD get_folder_list'
		args = {"q": "'"+str(folder)+"' in parents and trashed=false"}
		download_list = self.drive_service.files().list(**args).execute()
		return download_list

	def get_full_own_file_list(self):
		print 'METHOD: GD set_full_own_file_list'
		args = {"q": "'pavelhosek89@gmail.com' in owners and trashed=false"}
		return self.drive_service.files().list(**args).execute()
		

	def set_root_id(self):
		print 'METHOD: GD set_root_id'
		args = {"q":"'root' in parents and trashed=false ", "maxResults": 1, "fields": "items/parents/id"}
		root_id = self.drive_service.files().list(**args).execute()
		self.root_id = root_id['items'][0]['parents'][0]['id']

	def parse_data(self, data):
		print 'METHOD: GD parse_data'
		parse_data_file = []
		parse_data_folder = []
		parse_data_google_file = []

		for item_in_data in data["items"]:
			if item_in_data['parents'] != []:
				if 'folder' in item_in_data['mime_type']:
					parse_data_folder.append((
							item_in_data['id'],
							item_in_data['title'],
							item_in_data['parents'][0]['id'],
							item_in_data['version'],
							''))
				elif 'md5Checksum' in item_in_data:
					parse_data_file.append((
							item_in_data['id'],
							item_in_data['title'],
							item_in_data['etag'],
							item_in_data['mimeType'],
							item_in_data['createdDate'],
							item_in_data['alternateLink'],
							item_in_data['parents'][0]['id'],
							item_in_data['version'],
							item_in_data['originalfile_name'],
							item_in_data['fileExtension'],
							item_in_data['fileSize'],
							item_in_data['md5Checksum'],
							''))
				else:
					parse_data_google_file.append((
							item_in_data['id'],
							item_in_data['title'],
							item_in_data['mime_type'],
							item_in_data['alternateLink'],
							item_in_data['version']))
		del data
		return {'Files': parse_data_file, 'Folders': parse_data_folder, 'GoogleFiles': parse_data_google_file}

	def download_files(self, file_id, file_name):
		print 'METHOD: GD download_files'
		drive_file = self.drive_service.files().get(fileId=file_id).execute()
		
		download_url = drive_file.get('downloadUrl')
		#print download_url
		metadata = {'id': drive_file.get('id'),
					'title': drive_file.get('title'),
					'etag': drive_file.get('etag'),
					'mime_type': drive_file.get('mimeType'),
					'created_date': drive_file.get('createdDate'),
					'alternate_link': drive_file.get('alternateLink'),
					'parents': drive_file.get('parents')[0]['id'],
					'version': drive_file.get('version'),
					'original_file_name': drive_file.get('originalfile_name'),
					'file_extension': drive_file.get('file_extension'),
					'file_size': drive_file.get('fileSize'),
					'md5_checksum': drive_file.get('md5Checksum')}
		if download_url:
			start = time.time()
			resp, content = self.drive_service._http.request(download_url)
			end = time.time()
			elapsed = end - start
			if resp.status == 200:
				f = open(file_name, 'wb')
				f.write(content)
				f.close()
				print '    DOWNLOAD: Time: %.2fs\tSize: %.1fMB\tTitle: %s' % (elapsed, float(float(metadata['file_size'])/(1024*1024)), metadata['title'])
				return metadata
			else:
				print 'LOG: An error occurred: %s' % resp
				return None

	def upload_file(self, path, file_name, parents):
		print 'METHOD: GD upload_file'
		old_path = os.getcwd()
		os.chdir(path)
		file_meta_data = []
		if parents == 'root':
			parents = self.root_id
		
		if os.path.isfile(file_name):
			mime = mimetypes.MimeTypes()
			mime_type, encoding = mime.guess_type(file_name,strict=True)
			if mime_type == None:
				mime_type = ''
			start = time.time()
			file_upload = self.insert_file(title=file_name, file_name=file_name, mime_type=mime_type, description='Uploaded by GoogleDriveSync application.', parent_id=parents)
			end = time.time()
			elapsed = end - start
			print '    UPLOAD: Time: %.2fs\tSize: %.1fMB\tTitle: %s' % (elapsed, float(float(file_upload['fileSize'])/(1024*1024)), file_upload['title'])
			file_meta_data.append((
					file_upload['id'],
					file_upload['title'],
					file_upload['etag'],
					file_upload['mimeType'],
					file_upload['createdDate'],
					file_upload['alternateLink'],
					file_upload['parents'][0]['id'],
					file_upload['version'],
					file_upload['title'],
					file_upload['fileExtension'],
					file_upload['fileSize'],
					file_upload['md5Checksum'],
					path))
		else:
			print '    UPLOAD: File "%s" does not exist.' % file_name
		os.chdir(old_path)
		return file_meta_data

	def insert_file(self, title, description, parent_id, mime_type, file_name):
		"""Insert new file.

			Args:
			service: Drive API service instance.
			title: Title of the file to insert, including the extension.
			description: Description of the file to insert.
			parent_id: Parent folder's ID.
			mime_type: MIME type of the file to insert.
			file_name: file_name of the file to insert.
			Returns:
			Inserted file metadata if successful, None otherwise.
		"""
		print 'METHOD: GD insert_file'
		
		if 'folder' in mime_type:
			body = {
				'title': title,
				'description': description,
				'parents': [{'id': parent_id}],
				'mimeType': 'application/vnd.google-apps.folder'
			}	
		else:
			media_body = MediaFileUpload(file_name, mimetype=mime_type, resumable=True)
			body = {
				'title': title,
				'description': description,
				'parents': [{'id': parent_id}],
				'mimeType': mime_type
			}	

		try:
			if 'folder' in mime_type:
				file = self.drive_service.files().insert(body=body).execute()
			else:
				file = self.drive_service.files().insert(
					body=body,
					media_body=media_body).execute()
			return file
		except errors.HttpError, error:
			print 'LOG: An error occured: %s' % error
			return None

	def create_folder(self, path, folder_name, parents='root'):
		print 'METHOD: GD create_folder'
		folder_metadata = []
		if parents == 'root':
			parents = self.root_id
		create_folder = self.insert_file(title=folder_name, file_name=folder_name, mime_type='application/vnd.google-apps.folder', description='Uploaded by GoogleDriveSync application.', parent_id=parents)
		print '    CREATE FOLDER IN GOOGLE DRIVE: Title: %s' % folder_name
		folder_metadata.append((
					create_folder['id'],
					create_folder['title'],
					create_folder['parents'][0]['id'],
					create_folder['version'],
					path))
		return folder_metadata


class DatabaseService(object):
	"""docstring for ClassName"""
	def __init__(self, name):
		print 'METHOD: DB __init__'
		self.name = name
		self.tables_exist = None
		
		self.create_conn()
		self.set_tables_exist()
		self.create_table()

		self.root_id = self.set_root_id()
		self.root_path = self.set_root_path()

	def create_conn(self):
		print 'METHOD: DB create_conn'
		if os.path.isfile(self.name) and self.name != ':memory:':
			self.conn = sqlite3.connect(self.name)
		elif os.path.isfile(self.name) == False and self.name != ':memory:':
			f = file(self.name, "w")
			self.conn = sqlite3.connect(self.name)
		else:
			self.conn = sqlite3.connect(self.name)
		self.cur = self.conn.cursor()

	def close_conn(self):
		print 'METHOD: DB close_conn'
		self.conn.close()

	def create_table(self):
		print 'METHOD: DB create_table'
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
					originalfile_name text,
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
			self.tables_exist = True
			print 'LOG: The database was created.'
		else:
			print 'LOG: The database exists.'

	def insert_to_table(self, insert_data):
		print 'METHOD: DB insert_to_table'
		for row in insert_data['Files']:
			self.cur.execute('INSERT OR REPLACE INTO files VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)', row)
			self.conn.commit()
		for row in insert_data['Folders']:
			self.cur.execute('INSERT OR REPLACE INTO folders VALUES (?,?,?,?,?)', row)
			self.conn.commit()
		for row in insert_data['GoogleFiles']:
			self.cur.execute('INSERT OR REPLACE INTO googleFiles VALUES (?,?,?,?,?)', row)
			self.conn.commit()
		del insert_data

	def set_tables_exist(self):
		print 'METHOD: DB set_tables_exist'
		if self.tables_exist == None:
			TABLES = []
			self.cur.execute("SELECT DISTINCT tbl_name FROM sqlite_master")
			self.conn.commit()
			tables = self.cur.fetchall()
			for i in range(0,len(tables)):
				 TABLES.append(tables[i][0])
			if TABLES == ['files', 'folders', 'googleFiles']:
				self.tables_exist = True
			else:
				self.tables_exist = False
			self.conn.commit()

	def get_folders(self, parent):
		print 'METHOD: DB get_folders'
		self.cur.execute("SELECT * FROM folders WHERE parents=:par", {"par": parent})
		self.conn.commit()
		data = self.cur.fetchall()
		return data

	def get_parent_data(self, parent_id):
		print 'METHOD: DB get_parent_data'
		self.cur.execute("SELECT title, path FROM folders WHERE id=:id", {"id": parent_id})
		self.conn.commit()
		parent_data = self.cur.fetchone()
		return parent_data

	def get_file_in_folder(self, parent_id):
		print 'METHOD: DB get_file_in_folder'
		self.cur.execute("SELECT id, originalfile_name FROM files WHERE parents=:par", {"par": parent_id})
		self.conn.commit()
		files = self.cur.fetchall()
		return files

	def get_parent_path(self, parent_id):
		print 'METHOD: DB get_parent_path'
		self.cur.execute("SELECT DISTINCT fo.path, fo.title FROM files AS fi JOIN folders AS fo ON fi.parents=fo.id WHERE fo.id=:id", {"id": parent_id})
		self.conn.commit()
		path = self.cur.fetchone()
		return path

	def set_root_folder(self, path, id):
		print 'METHOD: DB set_root_folder'
		data = [id, 'root', '', '', path]
		self.cur.execute('INSERT OR REPLACE INTO folders VALUES (?,?,?,?,?)', data)
		self.conn.commit()

	def set_root_path(self):
		print 'METHOD: DB set_root_path'
		self.cur.execute('SELECT path FROM folders WHERE title=:title', {'title': 'root'})
		self.conn.commit()
		root_path = self.cur.fetchall()
		if root_path == []:
			return None
		elif (len(root_path) > 1 or len(root_path[0]) > 1):
			return root_path
		else:
			return root_path[0][0]

	def set_root_id(self):
		print 'METHOD: DB set_root_id'
		self.cur.execute('SELECT id FROM folders WHERE title=:title', {'title': 'root'})
		self.conn.commit()
		root_id = self.cur.fetchall()
		if root_id == []:
			return None
		elif (len(root_id) > 1 or len(root_id[0]) > 1):
			return root_id
		else:	
			return root_id[0][0]

	def update_path(self, fileType, updateData):
		print 'METHOD: DB update_path'
		if fileType == 'folder':
			self.cur.execute("UPDATE folders SET path=:path WHERE id=:id", updateData)
		elif fileType == 'file':
			self.cur.execute("UPDATE files SET path=:path WHERE parents=:id", updateData)
		self.conn.commit()

	def folder_exist(self, title, parent_id):
		print 'METHOD: DB folder_exist'
		self.cur.execute('SELECT title FROM folders WHERE title=:tit AND parents=:par', {'tit': title, 'par': parent_id})
		self.conn.commit()
		folder = self.cur.fetchone()
		if folder != None and folder[0] == title:
			return True
		else:
			return False

	def get_folders_path(self):
		print 'METHOD: DB get_folders_path'
		self.cur.execute('SELECT DISTINCT path FROM folders WHERE title!=:tit', {'tit': 'root'})
		self.conn.commit()
		paths = self.cur.fetchall()
		return paths