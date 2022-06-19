import fileinput
from datetime import datetime

import requests
from git import Repo

from GlobalVariables import FOLDER_LOCATION, Colors


def setRecordingStatus(message: str, file_mode: str) -> None:
    """
    It writes a message to a file, and then removes any empty lines from the file

    Args:
      message (str): The message to be written to the file.
      file_mode (str): 'a' for append, 'w' for write
    """

    with open(f"{FOLDER_LOCATION}/recordingStatus.txt", file_mode) as recordingStatusFile:
        recordingStatusFile.write("\n" + message + "\n")

    with open(f"{FOLDER_LOCATION}/recordingStatus.txt", "r") as f:
        lines = f.readlines()
        if lines[0] == "Currently nothing to record\n":
            removeHost(host_to_delete="Currently nothing to record")

    __removeEemptyLines()


def __removeEemptyLines() -> None:
    """
    It removes empty lines from a text file
    """
    with open(f"{FOLDER_LOCATION}/recordingStatus.txt", "r") as f:
        lines = f.readlines()
    with open(f"{FOLDER_LOCATION}/recordingStatus.txt", "w") as f:
        f.write("")
    with open(f"{FOLDER_LOCATION}/recordingStatus.txt", "a") as f:
        for i, line in enumerate(lines, start=1):
            if line == "\n":
                continue
            if len(lines) == 1:
                line = line.replace("\n", "")
            if i == len(lines) and i != 1:
                line = line.replace("\n", "")
            f.write(line)


def removeHost(host_to_delete: str) -> None:
    """
    It reads the contents of a file, deletes the contents of the file, and then writes the contents of
    the file back to the file, but without the line that contains the host that was passed to the
    function

    Args:
      host_to_delete (str): str = The hostname of the host to remove from the recordingStatus.txt file.
    """
    with open(f"{FOLDER_LOCATION}/recordingStatus.txt", "r") as recordingStatusFile:
        hosts = recordingStatusFile.readlines()
    print(len(hosts))
    if len(hosts) == 1:
        setRecordingStatus(message="Currently nothing to record", file_mode="w")
        return
    setRecordingStatus(message="", file_mode="w")
    for host in hosts:
        if host_to_delete not in host:
            setRecordingStatus(message=host, file_mode="a")
    __removeEemptyLines()


def updateStatus() -> None:
    """
    It adds the file to the repo, commits it, and pushes it to the remote origin
    """
    repo = Repo(".")  # if repo is CWD just do '.'
    repo.index.add(["recordingStatus.txt"])
    repo.index.commit("Updated server status.")
    origin = repo.remote("origin")
    origin.push()
    print(
        f"{Colors.ENDC}{Colors.BOLD}{datetime.now()}{Colors.ENDC} - {Colors.OKGREEN}Updated server status{Colors.ENDC}"
    )


def getRecordingStatus() -> str:
    """
    It gets the recording status from a text file on GitHub

    Returns:
      The recording status.
    """
    url = "https://raw.githubusercontent.com/TheCodingJsoftware/HBNI-Audio-Stream-Recorder/master/recordingStatus.txt"
    req = requests.get(url)
    if req.status_code == requests.codes.ok:
        return req.content.decode()
    print(
        f"{Colors.ENDC}{Colors.BOLD}{datetime.now()}{Colors.ENDC} - {Colors.WARNING}Content was not found.{Colors.ENDC}"
    )
    return None
