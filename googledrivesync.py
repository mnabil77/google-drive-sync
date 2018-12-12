#!/usr/bin/env python

"""GoogleDriveSync.py: Google Drive synchronization"""

__author__		= "Pavel Hosek"
__copyright__	= "Copyright 2014, Pavel Hosek"
__license__		= "Public Domain"
__version__		= "1.0"

import os
import sys
import pprint
import hashlib

import cryptAES
from googleservice import GoogleService
from databaseservice import DatabaseService
from logservice import LogService


if os.uname()[1] == 'stolak':
	sys.stdout = LogService(filename='/mnt/data/Sublime/google drive/googledrivesync.log')
else:
	sys.stdout = LogService(filename='/home/pavelhosek/DATA/Soukrome/sublime/google_api/googledrivesync.log')

def close_app(database=None):
	'''
		???

		Args:
		log_data -- String, which will be print to console and log file
		database -- If database used set 'database' on True
		
		Returns: None
	'''
	if database == True:
		DB.close_conn()
	sys.stdout.close()
	sys.exit()


def search_item():
	'''
		???

		Args:
		path -- source path from where data will be stored to Google
		parents -- folder id in Google Drive, where they will be saved data

		Returns: None
	'''
	filename = raw_input('Enter the name of the file/folder you are looking for: ')
	if filename  != 'root':
		search_file = GD.search_file(filename=filename)
		#print '##############################'
		#pprint.pprint(search_file)
		#print '##############################'
		if len(search_file) == 0:
			log_data = 'File %s is not in the Google Drive!' % filename
			close_app(log_data=log_data)
		if len(search_file) != 0 and len(search_file) < 1:
			counter = 0
			print 'Select the correct filename:'
			for item in search_file:
				print '%s:\t%s' % (str(counter), item['title'])
				counter += 1
			answer = raw_input('Select number: ')
			if answer == 'q':
				log_data = 'Select file was terminated'
				close_app(log_data=log_data)
			else:	
				if int(answer) >= len(search_file) > 0:
					log_data = 'Number %s is not in the selection!' % answer
					close_app(log_data=log_data)
				else:
					return search_file[int(answer)]
		else:
			return search_file[0]
	else:
		return GD.aboutData['rootFolderId']


def new_sync():
	'''
		Upload all files and folders and his subfolders and files from 'path' to Google Drive

		Args: None

		Returns: None
	'''
	print 'Create synchronization settings.'
	sync = raw_input('Synchronization name: ')
	path = raw_input('Synchronization folder in PC (path with folder name): ')
	if path[-1:] == '/':
		path = path[:len(path)-1]
	if os.path.isdir(path) == False:
		log_data = 'Path "%s" is not exists!' % path
		close_app(log_data=log_data)
	print 'Synchronization folder in Google:'
	googleFolderName = search_item()
	if 'id' in googleFolderName:
		return {'sync': sync, 'folder': path, 'folderId': googleFolderName['id'], 'rootFolderId': GD.aboutData['rootFolderId']}
	else:
		return {'sync': sync, 'folder': path, 'folderId': googleFolderName, 'rootFolderId': googleFolderName}

def update_sync(sync):
	GD.set_about()
	updateData = {'sync': sync,
					'lastAccess': GD.aboutData['lastAccess'],
					'largestChangeId': GD.aboutData['largestChangeId'],
					'quotaBytesByDrive': GD.aboutData['quotaBytesByDrive'],
					'quotaBytesByGmail': GD.aboutData['quotaBytesByGmail'],
					'quotaBytesByPhotos': GD.aboutData['quotaBytesByPhotos'],
					'quotaBytesUsedAggregate': GD.aboutData['quotaBytesUsedAggregate']}
	DB.update_sync(updateData=updateData)


def upload(path, parents='root'):
	'''
		Upload all files and folders and his subfolders and files from 'path' to Google Drive

		Args:
		path -- source path from where data will be stored to Google
		parents -- folder id in Google Drive, where they will be saved data

		Returns: None
	'''

	# Upload File
	if os.path.isfile(path):
		base_path, filename = os.path.split(path)
		upload_file = GD.upload_file(path=base_path, filename=filename, parents=parents)
		if DB != None:
			DB.insert_to_table({'Files': upload_file})
	# Upload directory
	elif os.path.isdir(path):
		folders = []
		new_folders = []
		base_path, folder_name = os.path.split(path)
		
		insert_files = []
		insert_folders = []

		# create base folder in Google Drive
		create_folder = GD.create_folder(path=base_path, folder_name=folder_name, parents=parents)
		folders.append({'title': folder_name, 'parents': create_folder[0][0], 'path': base_path})
		
		# create folders and uploud files
		while folders != []:
			for folder in folders:
				actual_path = str(folder['path'])+'/'+str(folder['title'])
				list_folder = os.listdir(actual_path)
				for item in list_folder:
					if os.path.isdir(actual_path+'/'+item):
						create_folder = GD.create_folder(path=actual_path, folder_name=item, parents=folder['parents'])
						new_folders.append({'title': item, 'parents': create_folder[0][0], 'path': actual_path})
						if DB != None:
							insert_folders.append(create_folder)
						#print "Create folder with name: %s" % item
					else:
						upload_file = GD.upload_file(path=actual_path, filename=item, parents=folder['parents'])
						if DB != None:
							insert_files.append(upload_file)
						#print "Upload file with name: %s" % item
			folders = new_folders
			new_folders = []
		if DB != None:
			DB.insert_to_table(insert_data={'Files': insert_files, 'Folders': insert_folders, 'GoogleFiles': []})
	else:
		print "ERROR"
	close_app()


def download(path, parents='root', filename=None):
	'''
		Download file OR all files and folders in 'parents' and his subfolders and files

		Args:
		path -- destination path, where they will be saved data from Google
		parents -- parent folder
		filename -- name file in Google Drive, which will be download
		mime_type --
		content -- 
		
		Returns: None
	'''

	# Download file
	if filename != None:
		###################
		search_item = search_item()
		###################
		oldPath = os.getcwd()
		os.chdir(path)
		GD.download_files(search_item['id'], filename=search_item['title'])
		os.chdir(oldPath)
	# Download directory
	elif os.path.isdir(path):
		folders = []
		new_folders = []

		base_path, folder_name = os.path.split(path)
		folders.append({'title': folder_name, 'parents': parents, 'path': base_path})

		# download folders and files
		while folders != []:
			for folder in folders:
				actual_path = folder['path']+'/'+folder['title']
				list_folder = GD.get_folder_list(folder=folder['parents'])
				os.chdir(actual_path)
				for item in list_folder['items']:
					# Create folder
					if 'folder' in item['mimeType']:
						if os.path.isdir(item['title']) != True:
							os.mkdir(item['title'])
							print 'APP: Create folder with name: %s' % item['title']
						else:
							print 'APP: Create folder with name: %s' % item['title']
						new_folders.append({'title': item['title'], 'parents': item['id'], 'path': actual_path})
					# Download file
					elif 'md5Checksum' in item:
						if os.path.isfile(item['title']) == True and item['md5Checksum'] == hashlib.md5(open(item['title']).read()).hexdigest():
							print 'APP: Create folder with name: %s' % item['title']
						else:
							print 'APP: Folder %s is exists!' % item['title']
							download_file = GD.download_files(file_id=item['id'], filename=item['title'])
			folders = new_folders
			new_folders = []
	else:
		print "ERROR"
	close_app()


def synchronization(sync):
	'''
		???
	
		Args:
		path -- 
		parents -- 
		
		Returns: None
	'''
	
	sync_name = DB.get_sync_exist()
	if sync in sync_name:
		base_sync_data = DB.get_data_sync(sync)

		folder_list = os.listdir(base_sync_data['folder'])
		base_path, folder_name = os.path.split(base_sync_data['folder'])
		drive_list = GD.get_folder_list(folder=base_sync_data['folderId'])
		folder_list_count = len(folder_list)
		drive_list_count = len(drive_list['items'])
		if folder_list_count == 0 and drive_list_count != 0:
			print 'APP: DOWN'
			update_sync(sync=sync)
			download(path=base_sync_data['folder'], parents=base_sync_data['folderId'])
		elif drive_list_count == 0 and folder_list_count != 0:
			print 'APP: UP'
			update_sync(sync=sync)
			upload(path=base_sync_data['folder'], parents=base_sync_data['folderId'])
		else:
			print 'APP: SYNC'
			update_sync(sync=sync)
			drive_list_title = []
			for item in drive_list['items']:
				drive_list_title.append(item['title'])
			if folder_name not in drive_list_title:
				upload(path=base_sync_data['folder'], parents=base_sync_data['folderId'])
			else:
				pass
	else:
		print 'APP: Sync "'+sync+'" does\'t exist.'
		print 'APP: Exist sync: '+ str(sync_name)
	#file_list = GD.get_full_own_file_list()
	#parse_data = GD.parse_data(data=file_list)
	#DB.insert_to_table(insert_data=parse_data)


def parse_args(arguments):
	'''
		???
	
		Args:
		arguments -- Arguments from console
		
		Returns: None
	'''
	if len(arguments) < 2:
		print str(arguments) + ', 1 arguments'
	elif arguments[1] == '-h' or arguments[1] == '--help':
		print 'Help'
	elif arguments[1] == '-d' or arguments[1] == '--download':
		print 'Download'
	elif arguments[1] == '-u' or arguments[1] == '--upload':
		print 'Upload'
	elif arguments[1] == '-s' or arguments[1] == '--synchronization':
		print 'Synchronization'
	else:
		print arguments



#full_own_file_list = GD.get_full_own_file_list()
#parse_data = GD.parse_data(data=full_own_file_list)
#del full_own_file_list
#DB.insert_to_table(insert_data=parse_data)
#del parse_data

#download(path='/home/pavelhosek/DATA/Soukrome/sublime/google_api/GDR')
#upload(path='/home/pavelhosek/DATA/Soukrome/sublime/google_api/UPLOAD')
#download(path='/mnt/data/Sublime/google drive/NewTest')

#parse_args(sys.argv)

#GD.download_files(file_id='0Bz69Ym8SN0w8RHBpZmk1MVRtOFk', filename='sls-cznic.pdf')

#GD.upload_file(path='/mnt/data/Sublime/google drive/', filename='pepa.txt', parents='root')


######################################################################################################
######################################################################################################
#sync = raw_input('1. Vyberte unikatni jmeno synchronizace: ')
#print '2. Vyberte nazev slozky na Googlu, se kterou budete chtit synchronizovat data.'
#folder_name = search_file()
#path = raw_input('3. Vlozte cestu ke slozce, vcetne nazvu slozek.: ')
#DB.new_sync(sync=sync, folder=path, folderId=folder_name['id'])
#synchronization()

##################
GD = GoogleService()
#pprint.pprint(GD.aboutData)
##sync = new_sync()
##sync['rootFolderId'] = GD.aboutData['rootFolderId']
DB = DatabaseService(name='/home/pavelhosek/DATA/Soukrome/sublime/google_api/database.sqlite')
##DB.create_sync(sync=sync['sync'], folder=sync['folder'], folderId=sync['folderId'], rootFolderId=sync['rootFolderId'])
synchronization(sync='dochazka')
close_app()