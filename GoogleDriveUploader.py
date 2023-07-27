import os.path
from datetime import datetime

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload

import DownloadLinks
from GlobalVariables import FOLDER_LOCATION, Colors

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/drive"]

# Folder ID of the shared folder
folder_id = "1ceDO2zOx8pdEzQDRa-aHXVXhXO-QT-cq"  # "HBNI Streaming Archives"

def upload(file_name: str, file_path: str, host: str, description: str, date: str, length: float):
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)

    try:
        service = build("drive", "v3", credentials=creds)
        print(
            f"{Colors.ENDC}{Colors.BOLD}{datetime.now()}{Colors.ENDC} - {Colors.OKGREEN}Successfully logged into GoogleDrive Account{Colors.ENDC}"
        )
        print(
            f"{Colors.ENDC}{Colors.BOLD}{datetime.now()}{Colors.ENDC} - {Colors.WARNING}Starting upload{Colors.ENDC}"
        )
        # Upload file to folder
        file_metadata = {"name": file_name, "parents": [folder_id]}
        media = MediaFileUpload(file_path)
        uploaded_file = (
            service.files()
            .create(body=file_metadata, media_body=media, fields="id, webViewLink")
            .execute()
        )
        
        # Add permission to make the file publicly accessible
        permission = {
            "type": "anyone",
            "role": "commenter",
            "allowFileDiscovery": True,
        }
        service.permissions().create(fileId=uploaded_file["id"], body=permission).execute()

        print(
            f"{Colors.ENDC}{Colors.BOLD}{datetime.now()}{Colors.ENDC} - {Colors.OKGREEN}Upload finished{Colors.ENDC}"
        )
        download_url = uploaded_file.get("webViewLink")
        DownloadLinks.addDownloadLink(
            fileName=file_name,
            downloadLink=download_url,
            host=host,
            description=description,
            date=date,
            length=length,
            commit=True,
        )
    except HttpError as error:
        print(
            f"{Colors.ENDC}{Colors.BOLD}{datetime.now()}{Colors.ENDC} - {Colors.WARNING}{error}{Colors.ENDC}"
        )
        upload(
            file_name=file_name,
            file_path=file_path,
            host=host,
            description=description,
            date=date,
            length=length,
        )
        return
