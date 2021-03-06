import json
import os
import re
from datetime import datetime

import requests
from mega import Mega

import DownloadLinks
from GlobalVariables import FOLDER_LOCATION, Colors


def upload(filePath: str, host: str, description: str, date: str, length: float) -> None:
    """uploades file to mega account

    Args:
        filePath (str): path to file that you want to upload
        host (str): the hosts name
        description (str): description
        date (str): date the file was created
    """
    fileName: str = filePath.split("/")[-1]
    with open(f"{FOLDER_LOCATION}/credentials.json", "r") as credentialsFile:
        credentials = json.load(credentialsFile)
        mega = Mega({"verbose": True})
        mega._login_user(credentials["username"], credentials["password"])
        folder = mega.find("HBNI Audio Recording")
        print(
            f"{Colors.ENDC}{Colors.BOLD}{datetime.now()}{Colors.ENDC} - {Colors.OKGREEN}Successfully logged into Mega Account{Colors.ENDC}"
        )
    print(
        f"{Colors.ENDC}{Colors.BOLD}{datetime.now()}{Colors.ENDC} - {Colors.WARNING}Starting upload{Colors.ENDC}"
    )
    try:
        uploadedFile = mega.upload(filePath, folder[0])
        print(
            f"{Colors.ENDC}{Colors.BOLD}{datetime.now()}{Colors.ENDC} - {Colors.OKGREEN}Upload finished{Colors.ENDC}"
        )
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
    except Exception as error:
        print(
            f"{Colors.ENDC}{Colors.BOLD}{datetime.now()}{Colors.ENDC} - {Colors.WARNING}{error}{Colors.ENDC}"
        )
        upload(
            filePath=filePath,
            host=host,
            description=description,
            date=date,
            length=length,
        )
        return
        


#upload("Recordings/Newdale - Newdale Broadcast - May 19 Thursday 2022 05_54 PM - 27m 11s.mp3", "newdale", "Newdale Broadcast", "May 19 Thursday 2022 05_54 PM", 27.1833333333)