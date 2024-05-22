import os
import time
from datetime import datetime, timedelta

import audio_file
import download_links
import recording_status
import synology_uploader
import RemoveSilence
import Zip
from global_variables import FOLDER_LOCATION, Colors


def upload(filePath: str, hostAddress: str, finalFileName: str) -> None:
    if '.mp3' in filePath:
        filePath = filePath.replace('.mp3', '')
    timestr = datetime.now().strftime("%B %d %A %Y %I_%M %p")
    dt = datetime.now()
    print(
        f"{Colors.ENDC}{Colors.BOLD}{dt}{Colors.ENDC} - {Colors.OKGREEN}Geting file length{Colors.ENDC}"
    )
    #RemoveSilence.removeSilence(
    #    filePath=f"{FOLDER_LOCATION}/CURRENTLY_RECORDING/{filePath}.mp3"
    #)

    audioFileLength: int = audio_file.get_audio_file_length(
        pathToFile=f"{FOLDER_LOCATION}/CURRENTLY_RECORDING/{filePath}.mp3"
    )
    #audioFileLength: int = 258.316666666
    # timeDelta = timedelta(minutes=audioFileLength)
    # finalDeltatime: str = AudioFile.convertDeltatime(duration=timeDelta)
    # finalFileName: str = f"{fileName} - {timestr} - {finalDeltatime}.mp3"

    audio_file.set_artist(
        pathToFile=f"{FOLDER_LOCATION}/CURRENTLY_RECORDING/{filePath}.mp3",
        artist=finalFileName.split(" - ")[0],
    )
    audio_file.set_genre(
        pathToFile=f"{FOLDER_LOCATION}/CURRENTLY_RECORDING/{filePath}.mp3",
        genre="HBNI Streams",
    )
    audio_file.set_title(
        pathToFile=f"{FOLDER_LOCATION}/CURRENTLY_RECORDING/{filePath}.mp3",
        title=finalFileName.split(" - ")[1],
    )
    audio_file.set_track_number(
        pathToFile=f"{FOLDER_LOCATION}/CURRENTLY_RECORDING/{filePath}.mp3",
        number=download_links.get_count_of_streams(host=hostAddress),
    )

    recordingPartNumber = 0

    os.rename(
        f"{FOLDER_LOCATION}/CURRENTLY_RECORDING/{filePath}.mp3",
        f"{FOLDER_LOCATION}/Recordings/{finalFileName}",
    )

    if audioFileLength > 12:
        description: str = finalFileName.split(" - ")[1]
        synology_uploader.upload(
            file_name=finalFileName,
            file_path=f"{FOLDER_LOCATION}/Recordings/{finalFileName}",
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

if __name__ == '__main__':
    upload(
        filePath="20220225200049.mp3",
        hostAddress="/elmriver",
        finalFileName="Elmriver - Elm River",
    )
