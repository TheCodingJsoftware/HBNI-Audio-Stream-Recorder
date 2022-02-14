import json
import base64
import requests
from git import Repo

def loadJson() -> dict:
    with open('downloadLinks.json', 'r') as f:
        data = json.load(f)
    return data

def addDownloadLink(fileName: str, downloadLink: str):
    data = loadJson()
    data.update({fileName: {"downloadLink": downloadLink}})
    with open('downloadLinks.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    updateDatabase()

def updateDatabase():
    repo = Repo('.')  # if repo is CWD just do '.'
    repo.index.add(['downloadLinks.json'])
    repo.index.commit('Updated downloadLinks.json file.')
    origin = repo.remote('origin')
    origin.push()

def downloadDatabase():
    url = 'https://raw.githubusercontent.com/jarebear12418/HBNI-Audio-Stream-Recorder/branch/downloadLinks.json'
    req = requests.get(url)
    if req.status_code == requests.codes.ok:
        content = req.json()  # the response is a JSON
        with open('downloadLinks.json', 'w+') as f:
            f.write(content)
    else:
        print('Content was not found.')

def getDownloadLink(fileName: str) -> str:
    data = loadJson()
    try:
        return data[fileName]['downloadLink']
    except KeyError:
        return None
downloadDatabase()