#!/usr/bin/python

import httplib2
import pprint

from apiclient.discovery import build
from apiclient.http import MediaFileUpload
from apiclient.http import MediaIoBaseDownload
from oauth2client.client import OAuth2WebServerFlow
from oauth2client.file import Storage


# Copy your credentials from the console
CLIENT_ID = '924364520901-u1olb69vujorp07kjc8uq6s43rbqa0cl.apps.googleusercontent.com'
CLIENT_SECRET = 'zjkkkc00iWHLri0MFvky4GF2'

# Check https://developers.google.com/drive/scopes for all available scopes
OAUTH_SCOPE = 'https://www.googleapis.com/auth/drive'

# Redirect URI for installed apps
REDIRECT_URI = 'urn:ietf:wg:oauth:2.0:oob'

# Path to the file to upload
FILENAME = 'Linux - 101 Hacks.pdf'

# Run through the OAuth flow and retrieve credentials
#flow = OAuth2WebServerFlow(CLIENT_ID, CLIENT_SECRET, OAUTH_SCOPE, REDIRECT_URI)
#authorize_url = flow.step1_get_authorize_url()
#print 'Go to the following link in your browser: ' + authorize_url
#code = raw_input('Enter verification code: ').strip()
#credentials = flow.step2_exchange(code)
storage = Storage('a_credentials_file')
#storage.put(credentials)

credentials = storage.get()

# Create an httplib2.Http object and authorize it with our credentials
http = httplib2.Http()
http = credentials.authorize(http)

drive_service = build('drive', 'v2', http=http)

# Insert a file
media_body = MediaFileUpload(FILENAME, mimetype='application/pdf', resumable=True)
body = {
  'title': 'Linux - 101 Hacks.pdf',
  'description': "It's hard :D",
  'mimeType': 'application/pdf'
}

#file = drive_service.files().insert(body=body, media_body=media_body).execute()
#pprint.pprint(file)
args = {"q":"'root' in parents and trashed=false", "maxResults": 1, "fields": "items/parents/id"}
fileList = drive_service.files().list(**args).execute()
pprint.pprint(fileList["items"][0]["parents"][0]["id"])
print "SUCCESS"