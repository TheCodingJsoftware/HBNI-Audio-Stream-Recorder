import json
import os
import re

import requests
from mega import Mega

import DownloadLinks
import Zip
from GlobalVariables import FOLDER_LOCATION, Colors


def upload(filePath: str, date: str) -> None:
    """uploades file to mega account

    Args:
                    filePath (str): path to file that you want to upload
                    date (str): date the file was created
    """
    fileName = filePath.split("/")[-1]
    with open(f"{FOLDER_LOCATION}/credentials.json", "r") as credentialsFile:
        credentials = json.load(credentialsFile)
        mega = Mega({"verbose": True})
        mega._login_user(credentials["username"], credentials["password"])
        folder = mega.find("HBNI Audio Recording")
        print(
            f"{Colors.ENDC}{Colors.OKGREEN}Successfully logged into Mega Account{Colors.ENDC}"
        )

    uploadedFile = mega.upload(filePath, folder[0])
    downloadLink = mega.get_upload_link(uploadedFile)
    Zip.zipFile(fileToZipPath=filePath)
    DownloadLinks.addDownloadLink(fileName=fileName, downloadLink=downloadLink, date=date)
