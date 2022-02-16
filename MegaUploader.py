# b00UzCzL
import os
import re
import json
import requests
from mega import Mega
import LinksJson
import GlobalVariables

FOLDER_LOCATION: str = GlobalVariables.FOLDER_LOCATION

with open(f'{FOLDER_LOCATION}/credentials.json', 'r') as f:
	credentials = json.load(f)
	mega = Mega({'verbose': True})
	mega._login_user(credentials['username'],credentials['password'])

folder = mega.find('HBNI Audio Recording')

def upload(file_path: str, date: str):
	fileName = file_path.split('/')[-1]
	file  = mega.upload(file_path, folder[0])
	url = mega.get_upload_link(file)
	LinksJson.addDownloadLink(fileName=fileName, downloadLink=url, date=date)
