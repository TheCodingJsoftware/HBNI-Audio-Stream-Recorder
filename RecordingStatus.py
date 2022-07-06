import contextlib
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
    with open(f"{FOLDER_LOCATION}/recordingStatus.txt", "r") as f:
        lines = f.readlines()
        with contextlib.suppress(IndexError):
            if "Currently nothing to record" in lines[0]:
                removeHost(host_to_delete="Currently nothing to record")
    hosts = [message]
    hosts += __getAllHosts()
    __clearFile()
    with open(f"{FOLDER_LOCATION}/recordingStatus.txt", file_mode) as recordingStatusFile:
        for host in hosts:
            recordingStatusFile.write("\n" + host + "\n")

    __removeEemptyLines()


def __clearFile() -> None:
    """
    It clears the file recordingStatus.txt
    """
    with open(f"{FOLDER_LOCATION}/recordingStatus.txt", "w") as f:
        f.write("")


def __getAllHosts() -> list[str]:
    """
    It reads a file, removes duplicate lines, and returns the lines as a list

    Returns:
      A list of strings.
    """
    with open(f"{FOLDER_LOCATION}/recordingStatus.txt", "r") as f:
        lines = f.readlines()
        lines = [line.replace("\n", "") for line in lines]
        lines = list(set(lines))
    new_lines = []
    for i, line in enumerate(lines):
        if i == 0:
            new_lines.append(line)
            continue
        new_lines.append(line + "\n")
    return new_lines


def __removeEemptyLines() -> None:
    """
    It removes empty lines from a text file
    """
    lines = __getAllHosts()
    __clearFile()
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
    hosts = __getAllHosts()
    if len(hosts) == 1 and host_to_delete != "Currently nothing to record":
        __clearFile()
        setRecordingStatus(message="Currently nothing to record", file_mode="w")
        return
    __clearFile()
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
