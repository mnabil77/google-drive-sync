###################### 
#!/usr/bin/env python
# test2
#
#test = {}
#test2 = {}
#test3 = {}
#
#test['test3'] = 'test3'
#test['test4'] = 'test4'
#
#test.update(test2)
#
#test3['aaa'] = 'bbb'
#
#test.update(test3)
#print  test#

###################### Vytvoreni slozky
#import os
#
#os.mkdir('./GoogleDrive')

###################### Vytvoreni slozky na GoogleDrive
#from pydrive.auth import GoogleAuth
#from pydrive.drive import GoogleDrive
#
#gauth = GoogleAuth()
#gauth.LocalWebserverAuth()
#drive = GoogleDrive(gauth)
#
#file1 = drive.CreateFile({'title': 'karel', 'mimeType': 'application/vnd.google-apps.folder', 'parents': [{'id': '0Bz69Ym8SN0w8QjhyTk9aQW1TY0k'}]}) # Create GoogleDriveFile instance with title 'Hello.txt'
#file1.Upload() # Upload it
#print 'title: %s, id: %s' % (file1['title'], file1['id']) # title: Hello.txt, id: {{FILE_ID}}

###################### Hash souboru a velikost
#import os
#import hashlib
#
#print os.path.getsize('/home/pavelhosek/DATA/Soukrome/sublime/google_api/drive/GoogleDriveRoot/DSC_0085.jpg')
##print hashlib.md5('/home/pavelhosek/DATA/Soukrome/sublime/google_api/drive/GoogleDriveRoot/DSC_0085.jpg').hexdigest() ## HASH Nazvu
#print hashlib.md5(open('/home/pavelhosek/DATA/Soukrome/sublime/google_api/drive/GoogleDriveRoot/DSC_0085.jpg').read()).hexdigest() ## HASH souboru

###################### Uploud souboru s pouzitim databaze
#import os
#import commands
#import GoogleDriveSync
#
#DB = GoogleDriveSync.DatabaseService('/home/pavelhosek/DATA/Soukrome/sublime/google_api/drive/GoogleDriveSync.sqlite')
#GD = GoogleDriveSync.GoogleService()
#
#data = []
#path = '/home/pavelhosek/DATA/Soukrome/sublime/google_api/drive/upload/Tom.Hardy_001.jpg'
#parents = ''
#
#if os.path.isdir(path):
#	basePath, folderName = os.path.split(path)
#	GD.upload_structure(folderName, parents)
#
#elif os.path.isfile(path):
#	basePath, fileName = os.path.split(path)
#	print basePath, fileName
#	uploadFile = GD.upload_file(basePath, fileName)
#	DB.insert_to_table(uploadFile)
#
#print data


###################### Sifrovani a desifrovani souboru
# 
#import os, random, struct
#from Crypto.Cipher import AES
#
#def encrypt_file(key, in_filename, out_filename=None, chunksize=64*1024):
#    """ Encrypts a file using AES (CBC mode) with the
#        given key.
#
#        key:
#            The encryption key - a string that must be
#            either 16, 24 or 32 bytes long. Longer keys
#            are more secure.
#
#        in_filename:
#            Name of the input file
#
#        out_filename:
#            If None, '<in_filename>.enc' will be used.
#
#        chunksize:
#            Sets the size of the chunk which the function
#            uses to read and encrypt the file. Larger chunk
#            sizes can be faster for some files and machines.
#            chunksize must be divisible by 16.
#    """
#    if not out_filename:
#        out_filename = in_filename + '.enc'
#
#    iv = ''.join(chr(random.randint(0, 0xFF)) for i in range(16))
#    encryptor = AES.new(key, AES.MODE_CBC, iv)
#    filesize = os.path.getsize(in_filename)
#
#    with open(in_filename, 'rb') as infile:
#        with open(out_filename, 'wb') as outfile:
#            outfile.write(struct.pack('<Q', filesize))
#            outfile.write(iv)
#
#            while True:
#                chunk = infile.read(chunksize)
#                if len(chunk) == 0:
#                    break
#                elif len(chunk) % 16 != 0:
#                    chunk += ' ' * (16 - len(chunk) % 16)
#
#                outfile.write(encryptor.encrypt(chunk))
#
#
#def decrypt_file(key, in_filename, out_filename=None, chunksize=24*1024):
#    """ Decrypts a file using AES (CBC mode) with the
#        given key. Parameters are similar to encrypt_file,
#        with one difference: out_filename, if not supplied
#        will be in_filename without its last extension
#        (i.e. if in_filename is 'aaa.zip.enc' then
#        out_filename will be 'aaa.zip')
#    """
#    if not out_filename:
#        out_filename = os.path.splitext(in_filename)[0]
#
#    with open(in_filename, 'rb') as infile:
#        origsize = struct.unpack('<Q', infile.read(struct.calcsize('Q')))[0]
#        iv = infile.read(16)
#        decryptor = AES.new(key, AES.MODE_CBC, iv)
#
#        with open(out_filename, 'wb') as outfile:
#            while True:
#                chunk = infile.read(chunksize)
#                if len(chunk) == 0:
#                    break
#                outfile.write(decryptor.decrypt(chunk))
#
#            outfile.truncate(origsize)
#
##encrypt_file('0123456789abcdef', './file.txt')
#decrypt_file('0123456789abcdef', 'file.txt.enc')

###################### rozdil v lists
#
#def diff(a, b):
#	xa = [i for i in set(a) if i not in b]
#	xb = [i for i in set(b) if i not in a]
#	return xa + xb
#
#def diffA(a, b):
#	xb = [i for i in set(b) if i not in a]
#	return xb
#
#def diffB(a, b):
#	xa = [i for i in set(a) if i not in b]
#	return xa
#
#aaa=[1,2,3,4,5,6,8]
#bbb=[6,7,8,9,0,2,4]
#
#print diff(a=aaa, b=bbb)
#print diffA(a=aaa, b=bbb)
#print diffB(a=aaa, b=bbb)
#print '\n'
#print list(set(aaa) - set(bbb))
#print list(set(bbb) - set(aaa))
