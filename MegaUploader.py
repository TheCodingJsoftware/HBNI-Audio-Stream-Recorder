import json
import os
import re
from datetime import datetime

import requests
from mega import Mega

import DownloadLinks
from GlobalVariables import FOLDER_LOCATION, Colors


def upload(filePath: str, host: str, description: str, date: str, length: int) -> None:
    """uploades file to mega account

    Args:
        filePath (str): path to file that you want to upload
        host (str): the hosts name
        description (str): description
        date (str): date the file was created
    """
    fileName = filePath.split("/")[-1]
    with open(f"{FOLDER_LOCATION}/credentials.json", "r") as credentialsFile:
        credentials = json.load(credentialsFile)
        mega = Mega({"verbose": True})
        mega._login_user(credentials["username"], credentials["password"])
        folder = mega.find("HBNI Audio Recording")
        print(
            f"{Colors.ENDC}{Colors.BOLD}{datetime.now()}{Colors.ENDC} - {Colors.OKGREEN}Successfully logged into Mega Account{Colors.ENDC}"
        )

    uploadedFile = mega.upload(filePath, folder[0])
    downloadLink = mega.get_upload_link(uploadedFile)
    DownloadLinks.addDownloadLink(
        fileName=fileName,
        downloadLink=downloadLink,
        host=host,
        description=description,
        date=date,
        length=length,
        commit=True,
    )
