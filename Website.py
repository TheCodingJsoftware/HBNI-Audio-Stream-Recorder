import json
import os
import sched
import threading
import time
from os import listdir
from os.path import isfile, join

import requests
from flask import Flask, current_app, render_template, send_file, url_for

import DownloadLinks
from GlobalVariables import FOLDER_LOCATION

app = Flask(__name__)
s = sched.scheduler(time.time, time.sleep)


@app.route("/")
def index() -> None:
    fileNames = []
    downloadLinks = []

    with open(f"{FOLDER_LOCATION}/websiteDownloadLinks.json", "r") as f:
        data = json.load(f)
    for fileName in data:
        newFileName = fileName.replace("_", ":").replace(".mp3", "")
        fileNames.append(newFileName)
        downloadLinks.append(DownloadLinks.getDownloadLink(fileName))
    fileNames.reverse()
    downloadLinks.reverse()
    downloadableRecordings = zip(fileNames, downloadLinks)
    return render_template("index.html", downloadableRecordings=downloadableRecordings)


def downloadDatabase() -> None:
    print("Updating database")
    url = "https://raw.githubusercontent.com/TheCodingJsoftware/HBNI-Audio-Stream-Recorder/master/downloadLinks.json"
    req = requests.get(url)
    if req.status_code == requests.codes.ok:
        data = dict(req.json())  # the response is a JSON
        with open("websiteDownloadLinks.json", "w+") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    else:
        print("Content was not found.")


def downloadThread() -> None:
    while True:
        downloadDatabase()
        time.sleep(300)


threading.Thread(target=downloadThread).start()
