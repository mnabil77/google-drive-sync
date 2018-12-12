#!/usr/bin/env python

"""GoogleServices.py: Google Drive service"""

__author__      = "Pavel Hosek"
__copyright__   = "Copyright 2014, Pavel Hosek"
__license__ 	= "Public Domain"
__version__ 	= "1.0"

import os
import time
import httplib2
import mimetypes

from apiclient import errors
from apiclient.discovery import build
from apiclient.http import MediaFileUpload
from oauth2client.file import Storage
from oauth2client.client import OAuth2WebServerFlow

class GoogleService(object):
	"""docstring for ClassName"""
	def __init__(self):
		'''
			???

			Args: None
			
			Returns: None
		'''
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

		# set variable 'aboutData'
		self.set_about()

		#print connection time
		print 'APP: Connection to GD in ' + time.strftime('%m-%d-%Y %H:%M:%S', time.localtime())

	def get_connection(self):
		'''
			???

			Args: None
			
			Returns:
			drive_service --
		'''
		return self.drive_service

	def set_about(self):
		'''
			???

			Args: None
			
			Returns: None
		'''
		about = self.drive_service.about().get().execute()
		self.aboutData = {'rootFolderId': about['rootFolderId'],
						'displayName': about['user']['displayName'],
						'emailAddress': about['user']['emailAddress'],
						'largestChangeId': about['largestChangeId'],
						'quotaBytesByDrive': about['quotaBytesByService'][0]['bytesUsed'],
						'quotaBytesByGmail': about['quotaBytesByService'][1]['bytesUsed'],
						'quotaBytesByPhotos': about['quotaBytesByService'][2]['bytesUsed'],
						'quotaBytesUsedAggregate': about['quotaBytesUsedAggregate'],
						'lastAccess': int(time.time())+7200}
		del about

	def get_about():
		pass

	def get_folder_list(self, folder):
		'''
			???

			Args:
			folder --
			
			Returns:
			??? --
		'''
		args = {"q": "'"+str(folder)+"' in parents and trashed=false"}
		return self.drive_service.files().list(**args).execute()

	def get_full_own_file_list(self):
		'''
			???

			Args:
			log_service --
			
			Returns: None
		'''
		args = {"q": "'pavelhosek89@gmail.com' in owners and trashed=false"}
		return self.drive_service.files().list(**args).execute()

	def search_file(self, filename, content='', mime_type=''):
		'''
			???

			Args:
			filename --
			content --
			mime_type --

			Returns:
			????
		'''
		args = {"q": "mimeType contains '"+str(mime_type)+"' and fullText contains '"+str(content)+"' and title contains '"+str(filename)+"' and trashed=false"}
		data = self.drive_service.files().list(**args).execute()
		return data['items']

#	def set_root_id(self):
#		'''
#			???
#
#			Args: None
#			
#			Returns: None
#		'''
#		args = {"q":"'root' in parents and trashed=false ", "maxResults": 1, "fields": "items/parents/id"}
#		root_id = self.drive_service.files().list(**args).execute()
#		self.root_id = root_id['items'][0]['parents'][0]['id']

	def parse_data(self, data):
		'''
			???

			Args:
			data --
			
			Returns:
			directory -- 
		'''
		parse_data_file = []
		parse_data_folder = []
		parse_data_google_file = []

		for item_in_data in data["items"]:
			if item_in_data['parents'] != []:
				if 'folder' in item_in_data['mimeType']:
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
							item_in_data['originalFilename'],
							item_in_data['fileExtension'],
							item_in_data['fileSize'],
							item_in_data['md5Checksum'],
							''))
				else:
					parse_data_google_file.append((
							item_in_data['id'],
							item_in_data['title'],
							item_in_data['mimeType'],
							item_in_data['alternateLink'],
							item_in_data['version']))
		del data
		return {'Files': parse_data_file, 'Folders': parse_data_folder, 'GoogleFiles': parse_data_google_file}

	def download_files(self, file_id, filename):
		'''
			???

			Args:
			file_id --
			filename --
			
			Returns:
			metadata -- 
		'''
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
					'original_filename': drive_file.get('originalFilename'),
					'file_extension': drive_file.get('file_extension'),
					'file_size': drive_file.get('fileSize'),
					'md5_checksum': drive_file.get('md5Checksum')}
		if download_url:
			resp, content = self.drive_service._http.request(download_url)
			if resp.status == 200:
				f = open(filename, 'wb')
				f.write(content)
				f.close()
				print '    DOWNLOAD: Size: %.1fMB\tTitle: %s' % (float(float(metadata['file_size'])/(1024*1024)), metadata['title'])
				return metadata
			else:
				print 'LOG: An error occurred: %s' % resp
				return None

	def upload_file(self, path, filename, parents):
		'''
			???

			Args:
			data --
			
			Returns:
			file_meta_data --
		'''
		old_path = os.getcwd()
		os.chdir(path)
		file_meta_data = []
		if parents == 'root':
			parents = self.root_id
		
		if os.path.isfile(filename):
			mime = mimetypes.MimeTypes()
			mime_type, encoding = mime.guess_type(filename,strict=True)
			if mime_type == None:
				mime_type = ''
			file_upload = self.insert_file(title=filename, filename=filename, mime_type=mime_type, description='Uploaded by GoogleDriveSync application.', parent_id=parents)
			print '    UPLOAD: Size: %.1fMB\tTitle: %s' % (float(float(file_upload['fileSize'])/(1024*1024)), file_upload['title'])
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
			print '    UPLOAD: File "%s" does not exist.' % filename
		os.chdir(old_path)
		return file_meta_data

	def insert_file(self, title, description, parent_id, mime_type, filename):
		"""
			Insert new file.

			Args:
			service: Drive API service instance.
			title: Title of the file to insert, including the extension.
			description: Description of the file to insert.
			parent_id: Parent folder's ID.
			mime_type: MIME type of the file to insert.
			filename: filename of the file to insert.

			Returns:
			Inserted file metadata if successful, None otherwise.
		"""
		if 'folder' in mime_type:
			body = {
				'title': title,
				'description': description,
				'parents': [{'id': parent_id}],
				'mimeType': 'application/vnd.google-apps.folder'
			}	
		else:
			media_body = MediaFileUpload(filename, mimetype=mime_type, resumable=True)
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
		"""
			Create folder on Google Drive.

			Args:
			path --
			folder_name --
			parents --

			Returns:
			folder_metadata --
		"""
		folder_metadata = []
		if parents == 'root':
			parents = self.root_id
		create_folder = self.insert_file(title=folder_name, filename=folder_name, mime_type='application/vnd.google-apps.folder', description='Uploaded by GoogleDriveSync application.', parent_id=parents)
		print '    CREATE FOLDER IN GOOGLE DRIVE: Title: %s' % folder_name
		folder_metadata.append((
					create_folder['id'],
					create_folder['title'],
					create_folder['parents'][0]['id'],
					create_folder['version'],
					path))
		return folder_metadata