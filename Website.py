import os
from os import listdir
from os.path import isfile, join
from flask import send_file
from flask import Flask, render_template
from flask import current_app, url_for
from natsort import natsort_keygen
import natsort
from natsort import natsorted, ns
import LinksJson

NATSORT_KEY: natsort_keygen() = natsort_keygen()

app = Flask(__name__)


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

    data = LinksJson.loadJson()
    for fileName in data:
        newFileName = fileName.replace('_', ':').replace('.mp3', '')
        fileNames.append(newFileName)
        downloadLinks.append(LinksJson.getDownloadLink(fileName))
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


if __name__ == "__main__":
    # website_url = 'hbniaudioarchive.hbni.net:5000'
    # app.config['SERVER_NAME'] = website_url
    # with app.test_request_context():
    #     url = url_for('index', _external=True)
    app.run(host='10.0.0.217', port='5000', debug=False, threaded=True)