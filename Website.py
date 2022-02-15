import os
import time
import json
import sched
import requests
import threading
from os import listdir
from os.path import isfile, join
from flask import send_file
from flask import Flask, render_template
from flask import current_app, url_for
import LinksJson


app = Flask(__name__)
s = sched.scheduler(time.time, time.sleep)


@app.route('/')
def index():
    # recordingsDir = 'F:\\Code\\Python-Projects\\Hutterite-Church\\Recorder\\Recordings'
    # downloadableRecordings = [
    #     f'{recordingsDir}\\{f}'
    #     for f in listdir(recordingsDir)
    #     if isfile(join(recordingsDir, f))
    # ]

    # downloadableRecordings.sort(key=os.path.getctime)
    # downloadableRecordings.reverse()
    # for i, recording in enumerate(downloadableRecordings):
    #     recording = recording.replace(f'{recordingsDir}\\', '').replace('.mp3', '').replace('_', ':')
    #     downloadableRecordings[i] = recording
    fileNames = []
    downloadLinks = []

    with open('websiteDownloadLinks.json', 'r') as f:
        data = json.load(f)
    for fileName in data:
        newFileName = fileName.replace('_', ':').replace('.mp3', '')
        fileNames.append(newFileName)
        downloadLinks.append(LinksJson.getDownloadLink(fileName))
    fileNames.reverse()
    downloadLinks.reverse()
    downloadableRecordings = zip(fileNames, downloadLinks)
    return render_template('index.html', downloadableRecordings=downloadableRecordings)


@app.route("/download/<path>")
def download(path=None):
    print(path)
    path = path.split('\\')
    fileName = path[-1].replace(':', '_')
    fileName += '.mp3'
    path.pop(-1)
    path.append('Recordings')
    path.append(fileName)
    path = '\\'.join(path)
    return send_file(path, as_attachment=True)

def downloadDatabase():
    print("Updating database")
    url = 'https://raw.githubusercontent.com/TheCodingJsoftware/HBNI-Audio-Stream-Recorder/master/downloadLinks.json'
    req = requests.get(url)
    if req.status_code == requests.codes.ok:
        data = dict(req.json())  # the response is a JSON
        with open('websiteDownloadLinks.json', 'w+') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    else:
        print('Content was not found.')


def downloadThread():
    while True:
        downloadDatabase()
        time.sleep(300)

if __name__ == "__main__":
    # website_url = 'hbniaudioarchive.hbni.net:5000'
    # app.config['SERVER_NAME'] = website_url
    # with app.test_request_context():
    #     url = url_for('index', _external=True)
    threading.Thread(target=downloadThread).start()
    app.run(host='10.0.0.217', port='5000', debug=False, threaded=True)