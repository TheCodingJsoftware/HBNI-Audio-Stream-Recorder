# b00UzCzL
import json
import os
import re

import requests
from mega import Mega
from rich import print

import GlobalVariables
import LinksJson

FOLDER_LOCATION: str = GlobalVariables.FOLDER_LOCATION

with open(f'{FOLDER_LOCATION}/credentials.json', 'r') as f:
	credentials = json.load(f)
	mega = Mega({'verbose': True})
	mega._login_user(credentials['username'],credentials['password'])

Folder = mega.find('HBNI Audio Recording')
files = mega.get_files()
print(files)
for file in files:
    fileName = files[file]['a']['n']
    print(fileName)
    print(LinksJson.getDownloadLink(fileName=fileName))
