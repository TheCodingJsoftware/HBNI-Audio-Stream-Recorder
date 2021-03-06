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


def addDownloadLink(
    fileName: str,
    downloadLink: str,
    host: str,
    description: str,
    date: str,
    length: float,
    commit: bool = True,
) -> None:
    """Adds a new file to the downloadLinks.json file and updates the online database to github.

    Args:
        fileName (str): name of the file
        downloadLink (str): download link for that file that was uploaded to mega
        host (str): the hosts name
        description (str): description
        date (str): date the file was created.
        length (float): length of the audio file
    """
    data = loadJson()
    data.update(
        {
            fileName: {
                "date": date,
                "description": description,
                "downloadLink": downloadLink,
                "length": length,
                "host": host,
                "id": len(data),
            }
        }
    )

    with open("downloadLinks.json", "w", encoding="utf-8") as downloadLinksFile:
        json.dump(data, downloadLinksFile, ensure_ascii=False, indent=4)

    if commit:
        uploadDatabase(message=f"Uploaded stream - {host}.")


def editDownloadLink(
    fileName: str,
    downloadLink: str,
    host: str,
    description: str,
    date: str,
    length: float,
    id: int,
) -> None:
    """Edits a download link.

    Args:
        fileName (str): name of the file
        downloadLink (str): download link for that file that was uploaded to mega
        host (str): the hosts name
        description (str): description
        date (str): date the file was created.
        length (float): length of the audio file
        id (int): id for sorting
    """

    data = loadJson()
    data[fileName]["downloadLink"] = downloadLink
    data[fileName]["description"] = description
    data[fileName]["date"] = date
    data[fileName]["length"] = float(length)
    data[fileName]["host"] = host
    data[fileName]["id"] = int(id)

    with open("downloadLinks.json", "w", encoding="utf-8") as downloadLinksFile:
        json.dump(data, downloadLinksFile, ensure_ascii=False, indent=4)

    sortJsonFile()


def changeTitle(oldTitle: str, newTitle: str) -> None:
    """Changes the title of a broadcasted stream

    Args:
        oldTitle (str): title
        newTitle (str): title
    """
    data = loadJson()
    downloadLink: str = data[oldTitle]["downloadLink"]
    description: str = data[oldTitle]["description"]
    date: str = data[oldTitle]["date"]
    length: float = data[oldTitle]["length"]
    host: str = data[oldTitle]["host"]
    idNum: int = data[oldTitle]["id"]

    data.pop(oldTitle)

    data.update(
        {
            newTitle: {
                "date": date,
                "description": description,
                "downloadLink": downloadLink,
                "length": length,
                "host": host,
                "id": idNum,
            }
        }
    )
    with open("downloadLinks.json", "w", encoding="utf-8") as downloadLinksFile:
        json.dump(data, downloadLinksFile, ensure_ascii=False, indent=4)

    sortJsonFile()


def updateIds() -> None:
    """Reorders the ID so its sorted"""
    data = loadJson()
    for index, name in enumerate(data):
        data[name]["id"] = index
    with open("downloadLinks.json", "w", encoding="utf-8") as downloadLinksFile:
        json.dump(data, downloadLinksFile, ensure_ascii=False, indent=4)


def removeDownloadLink(filename: str) -> None:
    """Delets a link from the downloadLinks.json file

    Args:
        filename (str): name of the file to be removed
    """
    data = loadJson()
    data.pop(filename)
    with open("downloadLinks.json", "w", encoding="utf-8") as downloadLinksFile:
        json.dump(data, downloadLinksFile, ensure_ascii=False, indent=4)

    updateIds()


def uploadDatabase(message: str = "Updated downloadLinks.json file.") -> None:
    """uploads the downloadLinks.json file to github"""
    repo = Repo(".")  # if repo is CWD just do '.'
    repo.index.add(["downloadLinks.json"])
    repo.index.commit(message)
    origin = repo.remote("origin")
    origin.push()
    print(
        f"{Colors.ENDC}{Colors.BOLD}{datetime.now()}{Colors.ENDC} - {Colors.OKGREEN}{message}{Colors.ENDC}"
    )


def sortJsonFile() -> None:
    """Sorts json file using the 'id' tag"""
    data = loadJson()
    sortedData = dict(sorted(data.items(), key=lambda x: x[1]["id"]))
    with open("downloadLinks.json", "w", encoding="utf-8") as downloadLinksFile:
        json.dump(sortedData, downloadLinksFile, ensure_ascii=False, indent=4)


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


def removeAllByHost(host: str) -> None:
    """
    It removes all download links that have the same host as the one specified

    Args:
      host (str): The host of the file.
    """
    data = loadJson()
    for filename in list(data.keys()):
        if data[filename]["host"] == host:
            removeDownloadLink(filename=filename)


def getAllHosts() -> "list[str]":
    """
    It returns a list of all the hosts in the JSON file

    Returns:
      A list of strings.
    """
    data = loadJson()
    hosts = [data[filename]["host"].replace("/", "") for filename in list(data.keys())]
    hosts = set(hosts)
    return hosts


def getCountOfStreams(host: str) -> int:
    """Gets the count of streams that a certain host has hosted

    Args:
        host (str): such as `/pineland` or `/newdale`

    Returns:
        int: count of streams the host has broadcasted
    """
    data = loadJson()
    return sum(host == data[file]["host"].lower() for file in list(data.keys()))
