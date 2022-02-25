import json
from datetime import datetime

import requests
from git import Repo

from GlobalVariables import FOLDER_LOCATION, Colors


def loadJson() -> dict:
    """loads downloadLinks.json file

    Returns:
        dict: json file for all the download links
    """
    with open(f"{FOLDER_LOCATION}/downloadLinks.json", "r") as downloadLinksFile:
        data = json.load(downloadLinksFile)
    return data


def addDownloadLink(fileName: str, downloadLink: str, date: str, length: int) -> None:
    """Adds a new file to the downloadLinks.json file and updates the online database to github.

    Args:
        fileName (str): name of the file
        downloadLink (str): download link for that file that was uploaded to mega
        date (str): date the file was created.
    """
    data = loadJson()
    data.update(
        {
            fileName: {
                "date": date,
                "downloadLink": downloadLink,
                "length": length,
            }
        }
    )

    with open("downloadLinks.json", "w", encoding="utf-8") as downloadLinksFile:
        json.dump(data, downloadLinksFile, ensure_ascii=False, indent=4)
    uploadDatabase()


def uploadDatabase() -> None:
    """uploads the downloadLinks.json file to github"""
    repo = Repo(".")  # if repo is CWD just do '.'
    repo.index.add(["downloadLinks.json"])
    repo.index.commit("Updated downloadLinks.json file.")
    origin = repo.remote("origin")
    origin.push()
    print(
        f"{Colors.ENDC}{Colors.BOLD}{datetime.now()}{Colors.ENDC} - {Colors.OKGREEN}Updated downloadLinks.json file to github.{Colors.ENDC}"
    )


def downloadDatabase() -> None:
    """downloads the downloadLinks.json file from github"""
    url = "https://raw.githubusercontent.com/TheCodingJsoftware/HBNI-Audio-Stream-Recorder/master/downloadLinks.json"
    req = requests.get(url)
    if req.status_code == requests.codes.ok:
        data = req.json()  # the response is a JSON
        with open("downloadLinks.json", "w+") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    else:
        print(
            f"{Colors.ENDC}{Colors.BOLD}{datetime.now()}{Colors.ENDC} - {Colors.WARNING}Content was not found.{Colors.ENDC}"
        )


def getDownloadLink(fileName: str) -> str:
    """Gets the download link from the fileName

    Args:
        fileName (str): name of the file you want the link for

    Returns:
        str: download link from taht file name or None if it can't find it.
    """
    data = loadJson()
    try:
        return data[fileName]["downloadLink"]
    except KeyError:
        return None
