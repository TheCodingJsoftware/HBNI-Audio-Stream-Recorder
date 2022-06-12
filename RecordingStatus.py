from datetime import datetime

import requests
from git import Repo

from GlobalVariables import FOLDER_LOCATION, Colors


def setRecordingStatus(message: str) -> None:
    """Sets server status"""
    with open(f"{FOLDER_LOCATION}/recordingStatus.txt", "w") as recordingStatusFile:
        recordingStatusFile.write(message)
    repo = Repo(".")  # if repo is CWD just do '.'
    repo.index.add(["recordingStatus.txt"])
    repo.index.commit(f"Updated server status: {message}")
    origin = repo.remote("origin")
    origin.push()
    print(
        f"{Colors.ENDC}{Colors.BOLD}{datetime.now()}{Colors.ENDC} - {Colors.OKGREEN}{message}{Colors.ENDC}"
    )


def getRecordingStatus() -> str:
    """Gets recording status from GitHub"""
    url = "https://raw.githubusercontent.com/TheCodingJsoftware/HBNI-Audio-Stream-Recorder/master/recordingStatus.txt"
    req = requests.get(url)
    if req.status_code == requests.codes.ok:
        return req.content.decode()
    print(
        f"{Colors.ENDC}{Colors.BOLD}{datetime.now()}{Colors.ENDC} - {Colors.WARNING}Content was not found.{Colors.ENDC}"
    )
    return None