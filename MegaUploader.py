# b00UzCzL
import json
import os
import re

import requests
from mega import Mega

import LinksJson
from GlobalVariables import FOLDER_LOCATION, Colors


def main():
    """Runs when the script first starts up"""
    with open(f"{FOLDER_LOCATION}/credentials.json", "r") as credentialsFile:
        credentials = json.load(credentialsFile)
        mega = Mega({"verbose": True})
        mega._login_user(credentials["username"], credentials["password"])
        folder = mega.find("HBNI Audio Recording")
        print("")
        print(
            f"{Colors.ENDC}{Colors.OKGREEN}Successfully logged into Mega Account{Colors.ENDC}"
        )


def upload(filePath: str, date: str):
    """uploades file to mega account

    Args:
            filePath (str): path to file that you want to upload
            date (str): date the file was created
    """
    fileName = filePath.split("/")[-1]
    file = mega.upload(filePath, folder[0])
    url = mega.get_upload_link(file)
    LinksJson.addDownloadLink(fileName=fileName, downloadLink=url, date=date)


main()
