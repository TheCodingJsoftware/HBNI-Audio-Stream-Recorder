import calendar
import json
import os
import sched
import threading
import time
from os import listdir
from os.path import isfile, join

import requests
from flask import (
    Flask,
    current_app,
    render_template,
    send_file,
    send_from_directory,
    url_for,
)

from GlobalVariables import FOLDER_LOCATION

app = Flask(__name__)
s = sched.scheduler(time.time, time.sleep)


@app.route("/")
def index() -> None:
    """Main page

    Returns:
        _type_: webpage
    """
    fileNames: list[str] = []
    downloadLinks: list[str] = []
    data = loadJson()
    for fileName in data:
        newFileName: str = fileName.replace("_", ":").replace(".mp3", "")
        fileNames.append(newFileName)
        downloadLinks.append(getDownloadLink(fileName=fileName))
    fileNames.reverse()
    downloadLinks.reverse()
    downloadableRecordings = zip(fileNames, downloadLinks)
    return render_template(
        "index.html",
        downloadableRecordings=downloadableRecordings,
        searchValue="",
        colonySearchList=getColonyList(),
        monthsList=getMonthsList(),
        daysList=getDaysList(),
        recordingStatus=getRecordingStatus(),
        showFaq=False,
        title="HBNI Audio Streaming Archive",
    )


@app.route("/<file_name>")
def search(file_name):
    """Main page

    Returns:
        _type_: webpage
    """
    fileNames: list[str] = []
    downloadLinks: list[str] = []
    showFaq = file_name == "frequently-asked-questions"

    data = loadJson()
    for fileName in data:
        if file_name.lower() in fileName.lower():
            newFileName: str = fileName.replace("_", ":").replace(".mp3", "")
            fileNames.append(newFileName)
            downloadLinks.append(getDownloadLink(fileName=fileName))
    fileNames.reverse()
    downloadLinks.reverse()
    downloadableRecordings = zip(fileNames, downloadLinks)
    return render_template(
        "index.html",
        downloadableRecordings=downloadableRecordings,
        searchValue=file_name,
        colonySearchList=getColonyList(),
        monthsList=getMonthsList(),
        daysList=getDaysList(),
        recordingStatus=getRecordingStatus(),
        showFaq=showFaq,
        title="HBNI Audio Streaming Archive",
    )


def getColonyList() -> list[str]:
    """Generates a list of all the colonies that have broadcasted

    Returns:
        list[str]: List of colonies
    """
    data = loadJson()
    colonySearchList: list[str] = [fileName.split(" - ")[0] for fileName in data]
    colonySearchList = sorted(set(colonySearchList))
    return colonySearchList


def getMonthsList() -> list[str]:
    """Generates a list that contains all the months that streams were broadcasted

    Returns:
        list[str]: List of months
    """
    data = loadJson()
    monthSearchList: list[str] = []
    for fileName in data:
        monthSearchList.extend(
            month for month in calendar.month_name[1:] if month in fileName
        )
    monthSearchList = set(monthSearchList)
    return monthSearchList


def getDaysList() -> list[str]:
    """Generates a list that contains all the days that streams were broadcasted

    Returns:
        list[str]: List of days
    """
    data = loadJson()
    daySearchList: list[str] = []
    for fileName in data:
        daySearchList.extend(day for day in list(calendar.day_name) if day in fileName)
    daySearchList = set(daySearchList)
    return daySearchList


def downloadDatabase() -> None:
    """donwload database"""
    print("Updating database")
    url = "https://raw.githubusercontent.com/TheCodingJsoftware/HBNI-Audio-Stream-Recorder/master/downloadLinks.json"
    req = requests.get(url)
    if req.status_code == requests.codes.ok:
        data = dict(req.json())  # the response is a JSON
        with open(f"{FOLDER_LOCATION}/websiteDownloadLinks.json", "w+") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    else:
        print("Content was not found.")


def getRecordingStatus() -> list:
    """Gets recording status from GitHub"""
    url = "https://raw.githubusercontent.com/TheCodingJsoftware/HBNI-Audio-Stream-Recorder/master/recordingStatus.txt"
    req = requests.get(url)
    if req.status_code == requests.codes.ok:
        content = req.content.decode().split("\n")
        if content[0] == "Currently nothing to record":
            content = content[0]
        return content
    print(
        f"{Colors.ENDC}{Colors.BOLD}{datetime.now()}{Colors.ENDC} - {Colors.WARNING}Content was not found.{Colors.ENDC}"
    )
    return None


def downloadThread() -> None:
    """update database every 5 minutes"""
    while True:
        downloadDatabase()
        time.sleep(300)


def loadJson() -> dict:
    """Loads the websiteDownloadLink.json file

    Returns:
        dict: all download links
    """
    with open(f"{FOLDER_LOCATION}/websiteDownloadLinks.json", "r") as f:
        data = json.load(f)
    return data


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


threading.Thread(target=downloadThread).start()
# app.run(host="10.0.0.217", port=5000, debug=False, threaded=True)
