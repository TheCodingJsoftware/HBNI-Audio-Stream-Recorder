import os
import time
from datetime import datetime, timedelta

import AudioFile
import DownloadLinks
import MegaUploader
import RecordingStatus
import RemoveSilence
import Zip
from GlobalVariables import FOLDER_LOCATION, Colors


def upload(filePath: str, hostAddress: str, fileName: str) -> None:
    """
    It takes a file, removes silence, sets the metadata, uploads it to Mega, compresses it, and deletes
    the original file

    Args:
      filePath (str): str = The name of the file that is being uploaded.
      hostAddress (str): str = "/pineland"
      fileName (str): str = "HBNI - " + fileName
    """

    timestr = datetime.now().strftime("%B %d %A %Y %I_%M %p")
    dt = datetime.now()
    print(
        f"{Colors.ENDC}{Colors.BOLD}{dt}{Colors.ENDC} - {Colors.OKGREEN}Removing silence{Colors.ENDC}"
    )
    RemoveSilence.removeSilence(
        filePath=f"{FOLDER_LOCATION}/CURRENTLY_RECORDING/{filePath}.mp3"
    )

    audioFileLength: int = AudioFile.getAudioFileLength(
        pathToFile=f"{FOLDER_LOCATION}/CURRENTLY_RECORDING/{filePath}.mp3"
    )

    timeDelta = timedelta(minutes=audioFileLength)
    finalDeltatime: str = AudioFile.convertDeltatime(duration=timeDelta)
    finalFileName: str = f"{fileName} - {timestr} - {finalDeltatime}.mp3"

    AudioFile.setArtist(
        pathToFile=f"{FOLDER_LOCATION}/CURRENTLY_RECORDING/{filePath}.mp3",
        artist=fileName.split(" - ")[0],
    )
    AudioFile.setGenre(
        pathToFile=f"{FOLDER_LOCATION}/CURRENTLY_RECORDING/{filePath}.mp3",
        genre="HBNI Streams",
    )
    AudioFile.setTitle(
        pathToFile=f"{FOLDER_LOCATION}/CURRENTLY_RECORDING/{filePath}.mp3",
        title=fileName.split(" - ")[-1],
    )
    AudioFile.setNumber(
        pathToFile=f"{FOLDER_LOCATION}/CURRENTLY_RECORDING/{filePath}.mp3",
        number=DownloadLinks.getCountOfStreams(host=hostAddress),
    )

    recordingPartNumber = 0

    os.rename(
        f"{FOLDER_LOCATION}/CURRENTLY_RECORDING/{filePath}.mp3",
        f"{FOLDER_LOCATION}/Recordings/{finalFileName}",
    )

    if audioFileLength > 12:
        description: str = fileName.split(" - ")[-1]
        MegaUploader.upload(
            filePath=f"{FOLDER_LOCATION}/Recordings/{finalFileName}",
            host=hostAddress,
            description=description,
            date=timestr,
            length=audioFileLength,
        )
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
    os.remove(f"{FOLDER_LOCATION}/Recordings/{finalFileName}")
    print(
        f"{Colors.ENDC}{Colors.BOLD}{dt}{Colors.ENDC} - {Colors.OKGREEN}Original copy deleted{Colors.ENDC}"
    )


upload(
    filePath="Elmriver - Wake And Funeral For Isaack Hofer, Elm River - (Part 2)",
    hostAddress="/elmriver",
    fileName="Elmriver - Wake And Funeral For Isaack Hofer, Elm River",
)
