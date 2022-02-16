import json
from datetime import datetime

import requests
from git import Repo

import GlobalVariables

FOLDER_LOCATION: str = GlobalVariables.FOLDER_LOCATION


def loadJson() -> dict:
    with open(f"{FOLDER_LOCATION}/downloadLinks.json", "r") as f:
        data = json.load(f)
    return data


def addDownloadLink(fileName: str, downloadLink: str, date: str):
    data = loadJson()
    data.update({fileName: {"downloadLink": downloadLink, "date": date}})

    with open("downloadLinks.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    uploadDatabase()


def uploadDatabase():
    addDownloadLink("t", "t", "s")
    repo = Repo(".")  # if repo is CWD just do '.'
    repo.index.add([f"{FOLDER_LOCATION}/downloadLinks.json"])
    repo.index.commit("Updated downloadLinks.json file.")
    origin = repo.remote("origin")
    origin.push()


def downloadDatabase():
    url = "https://raw.githubusercontent.com/TheCodingJsoftware/HBNI-Audio-Stream-Recorder/master/downloadLinks.json"
    req = requests.get(url)
    if req.status_code == requests.codes.ok:
        data = req.json()  # the response is a JSON
        with open("downloadLinks.json", "w+") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    else:
        print("Content was not found.")


def getDownloadLink(fileName: str) -> str:
    data = loadJson()
    try:
        return data[fileName]["downloadLink"]
    except KeyError:
        return None


uploadDatabase()
