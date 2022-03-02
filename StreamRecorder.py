#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = "Jared Gross"
__copyright__ = "Copyright 2022, StreamRecorder"
__credits__ = ["Jared Gross"]
__license__ = "MIT"
__version__ = "1.0.0"
__updated__ = "2022-03-01 11:33:07"
__maintainer__ = "Jared Gross"
__email__ = "jared@pinelandfarms.ca"
__status__ = "Production"

import logging
import os
import re
import sched
import subprocess
import threading
import time
from datetime import datetime, timedelta
from logging.handlers import RotatingFileHandler
from urllib.error import HTTPError, URLError
from urllib.request import urlopen

import AudioFile
import MegaUploader
import RemoveSilence
import Zip
from GlobalVariables import FOLDER_LOCATION, Colors

s = sched.scheduler(time.time, time.sleep)

titles: list = []
bodies: list = []
hostAddresses: list = []
recordingPartNumber: int = 0

logFormatter = logging.Formatter("%(message)s")
logFileName = datetime.today().strftime("%Y-%m-%d")
logFile = f"{FOLDER_LOCATION}/logs/{logFileName}.log"
logHandler = RotatingFileHandler(
    logFile,
    mode="a",
    maxBytes=1024**2 * 1024,  # 1 gb
    backupCount=2,
    encoding=None,
    delay=0,
)
logHandler.setFormatter(logFormatter)
logHandler.setLevel(logging.INFO)

appLog = logging.getLogger("root")
appLog.setLevel(logging.INFO)
appLog.addHandler(logHandler)


class Changes:
    def __init__(self, url: str, archive: str = f"{FOLDER_LOCATION}/archivedPage.html"):
        self.url = url
        self.newHtml = []
        self.oldHtml = []
        self.changeList: list[str] = []
        self.archive = archive

    def update(self) -> None:
        """Gets the html from the website and stores it's contents in a file.

        Returns:
            boolean: Not sure what this is used for anymore
        """

        try:
            with urlopen(self.url) as byt:
                self.newHtml = [x.decode("latin-1") for x in byt.readlines()]
        except HTTPError as e:
            self.newHtml = [x.decode("latin-1") for x in e.readlines()]
            print(f"HTTPError 500; continuing listenting process. {e}")
        except (URLError, ConnectionResetError):
            print("URL ERROR, ConnectionResetError")
            return False

        open(self.archive, "a").close()

        with open(self.archive, "rb+") as old:
            self.oldHtml = [x.decode("latin-1") for x in old.readlines()]
            old.seek(0)
            old.truncate()
            old.writelines(x.encode("latin-1") for x in self.newHtml)
            return True

    def diff(self) -> "list[str]":
        """returns all the differences.

        Returns:
            list[str]: all changes that were made in the file.
        """
        self.changeList.clear()
        for old, new in zip(self.oldHtml, self.newHtml):
            if old != new:
                self.changeList.append(new)
        return self.changeList

    def checkForStreams(self) -> None:
        """Checks if there are streams online or not"""
        with open(self.archive, "r") as archiveFile:
            file = archiveFile.read()
            if "SSLLOGIN" in file:
                print("Raspberry pi needs SSLLOGIN")
                return
            return "No streams currently online." not in file
            # return 'No streams currently online.' not in file


def regexFinder(tag: str, html: str, shouldReplaceText: bool = True) -> "list[str]":
    """regexFinder finds strings after a tag using regex matching

    Args:
        tag (str): a tag in the html such as "data-mnt" or "data-streams"
        html (str): the html string to parserTest

    Returns:
        str: the string attached to the tag.
    """
    regex = r"{}=([\"'])((?:(?=(?:\\)*)\\.|.)*?)\1".format(tag)
    matches = re.finditer(regex, html, re.MULTILINE)

    list_matches: list[str] = []

    for match in matches:
        m = match.group()
        m = m.replace(tag, "").replace("=", "").replace("'", "")
        if shouldReplaceText:
            m = m.replace("/", "").title()
        list_matches.append(m)
    return list_matches


def run(sc: sched.scheduler) -> None:
    """main loop that runs every 15 esconds.

    Args:
        sc (sched.scheduler): to recursively run this function every x seconds.
    """
    global titles, bodies, hostAddresses
    url = "http://hbniaudio.hbni.net/"
    websiteListener = Changes(url)
    websiteListener.update()
    dt = datetime.now()
    if not websiteListener.checkForStreams():
        print(
            f"{Colors.BOLD}{dt}{Colors.ENDC} - {Colors.OKBLUE}No streams currently online{Colors.ENDC}"
        )
        titles.clear()
        bodies.clear()
        hostAddresses.clear()
        s.enter(15, 1, run, (sc,))
        return

    if not websiteListener.diff():
        print(
            f"{Colors.BOLD}{dt}{Colors.ENDC} - {Colors.OKCYAN}No differences found{Colors.ENDC}"
        )
        s.enter(15, 1, run, (sc,))
        return

    changes = websiteListener.diff()

    try:
        for change in changes:
            print(
                f"{Colors.BOLD}{dt}{Colors.ENDC} - {Colors.OKGREEN}Changes: {change}{Colors.ENDC}"
            )
            appLog.info(f"{dt} - Changes: {change}")
            titles = regexFinder(tag="data-mnt", html=change)
            bodies = regexFinder(tag="data-stream", html=change)
            hostAddresses = regexFinder(
                tag="data-mnt", html=change, shouldReplaceText=False
            )
            print(
                f"{Colors.BOLD}{dt}{Colors.ENDC} - {Colors.OKGREEN}Titles: {titles}{Colors.ENDC}"
            )
            appLog.info(f"{dt} - Titles: {titles}")
            print(
                f"{Colors.BOLD}{dt}{Colors.ENDC} - {Colors.OKGREEN}Bodies: {bodies}{Colors.ENDC}"
            )
            appLog.info(f"{dt} - Bodies: {bodies}")
            print(
                f"{Colors.BOLD}{dt}{Colors.ENDC} - {Colors.OKGREEN}Host Addresses: {hostAddresses}{Colors.ENDC}"
            )
            appLog.info(f"{dt} - Host Addresses: {hostAddresses}")
            if len(titles) != 0:
                break
        if len(titles) == 0 or len(bodies) == 0 or len(hostAddresses) == 0:
            print(
                f"{Colors.BOLD}{dt}{Colors.ENDC} - {Colors.FAIL}No data could be found in changes{Colors.ENDC}"
            )
            print(
                f"{Colors.BOLD}{dt}{Colors.ENDC} - {Colors.OKBLUE}Starting next cycle{Colors.ENDC}"
            )
            s.enter(15, 1, run, (sc,))
            return
    except Exception as e:  # IndexError
        print(f"{Colors.BOLD}{dt}{Colors.ENDC} - {Colors.FAIL}Error: {e}{Colors.ENDC}")
        appLog.info(f"{dt} - Error: {e}")
        print(
            f"{Colors.BOLD}{dt}{Colors.ENDC} - {Colors.FAIL}No data could be found for active streams{Colors.ENDC}"
        )
        appLog.info(f"{dt} - No data could be found for active streams")
        print(
            f"{Colors.BOLD}{dt}{Colors.ENDC} - {Colors.FAIL}Starting next cycle{Colors.ENDC}"
        )
        appLog.info(f"{dt} - Starting next cycle")
        s.enter(15, 1, run, (sc,))
        return

    for title, body, address in zip(titles, bodies, hostAddresses):
        print(
            f"{Colors.ENDC}{Colors.BOLD}{dt}{Colors.ENDC} - {Colors.OKGREEN}Host: {title} Description: {body}{Colors.ENDC}"
        )
        appLog.info(f"{dt} - Host: {title} Description: {body} - Recording starting")
        fileName = f"{title} - {body}"
        threading.Thread(
            target=download,
            args=(
                fileName,
                address,
            ),
        ).start()

    s.enter(15, 1, run, (sc,))


def download(fileName: str, hostAddress: str) -> None:
    """The main Record/Download/Upload function.

    Args:
        fileName (str): the name of the file thats being streamed
        hostAddress (str): the address to the stream
    """
    global recordingPartNumber
    dt = datetime.now()
    appLog.info(f"{dt} - Started recording")
    print(
        f"{Colors.ENDC}{Colors.BOLD}{dt}{Colors.ENDC} - {Colors.OKGREEN}Started recording{Colors.ENDC}"
    )
    timestr = datetime.now().strftime("%B %d %A %Y %I_%M %p")
    recordingstr = time.strftime("%Y%m%d%H%M%S")
    process = subprocess.Popen(
        [
            "ffmpeg",
            "-y",
            "-i",
            f"http://hbniaudio.hbni.net:8000{hostAddress}",
            f"{FOLDER_LOCATION}/CURRENTLY_RECORDING/{recordingstr}.mp3",
        ]
    )
    process.communicate()
    # This code will proceed once recording stopped
    print(
        f"{Colors.ENDC}{Colors.BOLD}{dt}{Colors.ENDC} - {Colors.OKGREEN}Recording stopped{Colors.ENDC}"
    )
    appLog.info(f"{dt} - Recording stopped")
    time.sleep(5)
    Changes(url="http://hbniaudio.hbni.net/").update()
    with open("archivedPage.html", "r") as htmlFile:
        html = htmlFile.read()
        if regexFinder("data-mnt", html=html):  # If stream is still online
            streams = regexFinder("data-mnt", html=html, shouldReplaceText=False)
            recordingPartNumber += 1
            for stream in streams:
                if stream is hostAddress:
                    threading.Thread(
                        target=download,
                        args=(
                            fileName,
                            hostAddress,
                        ),
                    ).start()
                    appLog.info(f"{dt} - Stream still online, restarting recording")
                    print(
                        f"{Colors.ENDC}{Colors.BOLD}{dt}{Colors.ENDC} - {Colors.WARNING}Recording restarted{Colors.ENDC}"
                    )
                    break
            os.rename(
                f"{FOLDER_LOCATION}/CURRENTLY_RECORDING/{recordingstr}.mp3",
                f"{FOLDER_LOCATION}/CURRENTLY_RECORDING/{fileName} - (Part {recordingPartNumber}).mp3",
            )
            return
    appLog.info(f"{dt} - Removing silence")
    print(
        f"{Colors.ENDC}{Colors.BOLD}{dt}{Colors.ENDC} - {Colors.OKGREEN}Removing silence{Colors.ENDC}"
    )
    RemoveSilence.removeSilence(
        filePath=f"{FOLDER_LOCATION}/CURRENTLY_RECORDING/{recordingstr}.mp3"
    )

    audioFileLength: int = AudioFile.getAudioFileLength(
        pathToFile=f"{FOLDER_LOCATION}/CURRENTLY_RECORDING/{recordingstr}.mp3"
    )

    timeDelta = timedelta(minutes=audioFileLength)
    finalDeltatime: str = AudioFile.convertDeltatime(duration=timeDelta)
    if recordingPartNumber != 0:
        finalDeltatime += " - (Final Part)"
    finalFileName: str = f"{fileName} - {timestr} - {finalDeltatime}.mp3"

    recordingPartNumber = 0

    os.rename(
        f"{FOLDER_LOCATION}/CURRENTLY_RECORDING/{recordingstr}.mp3",
        f"{FOLDER_LOCATION}/Recordings/{finalFileName}",
    )

    if audioFileLength > 5:
        print(
            f"{Colors.ENDC}{Colors.BOLD}{dt}{Colors.ENDC} - {Colors.OKGREEN}Starting upload to Mega{Colors.ENDC}"
        )
        appLog.info(f"{dt} - Starting upload to Mega")
        MegaUploader.upload(
            filePath=f"{FOLDER_LOCATION}/Recordings/{finalFileName}",
            date=timestr,
            length=audioFileLength,
        )
        appLog.info(f"{dt} - Done uploading")
        print(
            f"{Colors.ENDC}{Colors.BOLD}{dt}{Colors.ENDC} - {Colors.OKGREEN}Done uploading{Colors.ENDC}"
        )
    else:
        print(
            f"{Colors.ENDC}{Colors.BOLD}{dt}{Colors.ENDC} - {Colors.WARNING}Recording is too small, probably a test stream and won't be uploaded.{Colors.ENDC}"
        )
    print(
        f"{Colors.ENDC}{Colors.BOLD}{dt}{Colors.ENDC} - {Colors.OKGREEN}Starting compression{Colors.ENDC}"
    )
    Zip.zipFile(pathToFile=f"{FOLDER_LOCATION}/Recordings/{finalFileName}")
    print(
        f"{Colors.ENDC}{Colors.BOLD}{dt}{Colors.ENDC} - {Colors.OKGREEN}File compressed{Colors.ENDC}"
    )
    appLog.info(f"{dt} - File compressed")
    os.remove(f"{FOLDER_LOCATION}/Recordings/{finalFileName}")
    appLog.info(f"{dt} - Original copy deleted")
    print(
        f"{Colors.ENDC}{Colors.BOLD}{dt}{Colors.ENDC} - {Colors.OKGREEN}Original copy deleted{Colors.ENDC}"
    )


def main() -> None:
    s.enter(0, 0, run, (s,))
    print(
        f"{Colors.BOLD}{datetime.now()}{Colors.ENDC} - {Colors.HEADER}Starting stream listener{Colors.ENDC}"
    )
    appLog.info(f"{datetime.now()} - Starting stream recorder")
    s.run()


if __name__ == "__main__":
    main()
