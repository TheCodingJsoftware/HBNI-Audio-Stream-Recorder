__author__ = "Jared Gross"
__copyright__ = "Copyright 2022"
__credits__ = ["Jared Gross"]
__license__ = "MIT"
__version__ = "3.0.0"
__updated__ = "2024-05-22 14:04:28"
__maintainer__ = "Jared Gross"
__email__ = "jared@pinelandfarms.ca"
__status__ = "Production"

import json
import logging
import os
import re
import subprocess
import sys
import threading
import time
from datetime import datetime, timedelta
from logging.handlers import RotatingFileHandler
from typing import Dict, Union
from urllib.request import urlopen

import audio_file
import recording_status
import synology_uploader
import zip_file
from global_variables import FOLDER_LOCATION, Colors

logFormatter = logging.Formatter("%(message)s")
logFileName = datetime.now().strftime("%Y-%m-%d")
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

app_log = logging.getLogger("root")
app_log.setLevel(logging.INFO)
app_log.addHandler(logHandler)


def excepthook(exc_type, exc_value, exc_traceback):
    app_log.error("Unhandled exception", exc_info=(exc_type, exc_value, exc_traceback))
    print(f"{Colors.ENDC}{Colors.BOLD}{datetime.now()}{Colors.ENDC} - {Colors.WARNING}{exc_type} - {exc_value} - {exc_traceback}{Colors.ENDC}")
    sys.__excepthook__(exc_type, exc_value, exc_traceback)


sys.excepthook = excepthook


class Stream:
    def __init__(self, title: str, host: str, description: str, recording_finished=None) -> None:
        self.title = title
        self.host = host
        self.url = f"http://hbniaudio.hbni.net:8000{self.host}"
        self.description = description.replace("&amp;", "&").replace("&", "and").replace("/", " or ")
        self.recording_finished = recording_finished
        self.is_recording: bool = False
        self.recording_stopped: bool = False
        self.uploaded: bool = False
        self.audio_file_length = -1
        self.starting_time = datetime.now()
        self.recording_file_name = f"{self.title} - {self.description} - {self.starting_time.strftime('%B %d %A %Y %I_%M %p')}"
        self.recording_file_path = f"{FOLDER_LOCATION}\\CURRENTLY_RECORDING\\{self.recording_file_name}.mp3"

    def get_time_since_started_recording(self) -> str:
        current_time = datetime.now()
        delta = current_time - self.starting_time
        hours, remainder = divmod(delta.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{hours}h {minutes}m {seconds}s"

    def start_recording(self):
        if not self.is_recording:
            self.is_recording = True
            threading.Thread(target=self.record).start()

    def record(self):
        stream_recording = subprocess.Popen(
            [
                "ffmpeg",
                "-y",
                "-i",
                self.url,
                self.recording_file_path,
            ]
        )
        stream_recording.communicate()
        self.is_recording = False
        self.recording_stopped = True
        self.recording_finished(self.host)
        try:
            self.process_file()
        except FileNotFoundError as e:
            app_log.info(f"{datetime.now()} - Stream.record error: {e}. The stream ended with no bytes.")
            print(f"{Colors.WARNING}The stream ended with no bytes. {e}{Colors.ENDC}")

    def process_file(self):
        self.audio_file_length: float = audio_file.get_audio_file_length(self.recording_file_path)

        time_delta = timedelta(minutes=self.audio_file_length)
        final_delta_time = audio_file.convert_delta_time(time_delta)
        final_file_name = f"{self.recording_file_name} - {final_delta_time}.mp3"
        final_file_path = f"{FOLDER_LOCATION}\\Recordings\\{final_file_name}"

        os.rename(
            self.recording_file_path,
            final_file_path,
        )

        if self.audio_file_length > 10:
            self.upload_stream(final_file_name, final_file_path)
            app_log.info(f"{datetime.now()} - Stream uploaded for {self.host}")
        else:
            print(f"{Colors.ENDC}{Colors.BOLD}{datetime.now()}{Colors.ENDC} - {Colors.WARNING}Recording is too small, probably a test stream and won't be uploaded.{Colors.ENDC}")
            app_log.info(f"{datetime.now()} - Recording is too small, probably a test stream and won't be uploaded for {self.host}")
            self.uploaded = True

        self.backup_stream(final_file_path)
        os.remove(final_file_path)
        print(f"{Colors.ENDC}{Colors.BOLD}{datetime.now()}{Colors.ENDC} - {Colors.OKGREEN}Original copy deleted{Colors.ENDC}")

    def upload_stream(self, file_name: str, file_path: str):
        synology_uploader.upload(
            file_name=file_name,
            file_path=file_path,
            host=self.host,
            description=self.description,
            date=self.starting_time.strftime('%B %d %A %Y %I_%M %p'),
            length=self.audio_file_length,
        )
        self.uploaded = True

    def backup_stream(self, file_path: str):
        print(f"{Colors.ENDC}{Colors.BOLD}{datetime.now()}{Colors.ENDC} - {Colors.OKGREEN}Starting compression{Colors.ENDC}")
        zip_file.zip_file(file_path)
        print(f"{Colors.ENDC}{Colors.BOLD}{datetime.now()}{Colors.ENDC} - {Colors.OKGREEN}File compressed{Colors.ENDC}")

    def __str__(self) -> str:
        return f"{self.host} - {self.description}"


class StreamRecorder:
    def __init__(self) -> None:
        self.active_streams: dict[str, Stream] = {}

    def fetch_icecast_status(self, icecast_source="http://hbniaudio.hbni.net:8000/status-json.xsl") -> Union[dict, None]:
        try:
            with urlopen(icecast_source) as response:
                data = json.load(response)
                return data
        except Exception as e:
            print(f"Error fetching Icecast status: {e}")
            return None

    def process_sources(self, sources: Union[dict, list[dict]]) -> list[dict]:
        # Normalize single source to a list of sources
        if isinstance(sources, dict):
            sources = [sources]
        return sources

    def remove_stream(self, host: str):
        del self.active_streams[host]
        print(f"{Colors.BOLD}{datetime.now()}{Colors.ENDC} - {Colors.OKBLUE}{host} removed from list.{Colors.ENDC}")
        app_log.info(f"{datetime.now()} - Finished recording for {host}")
        if not list(self.active_streams.keys()):
            print(f"{Colors.BOLD}{datetime.now()}{Colors.ENDC} - {Colors.OKBLUE}Listening for streams{Colors.ENDC}")
            recording_status.update_recording_status([])

    def run(self):
        while True:
            try:
                print(f"{Colors.BOLD}{datetime.now()}{Colors.ENDC} - {Colors.OKBLUE}Listening for streams{Colors.ENDC}")

                # Fetch Icecast status JSON
                status_data = self.fetch_icecast_status()
                if not status_data:
                    time.sleep(15)
                    continue

                sources = status_data.get("icestats", {}).get("source", [])
                sources = self.process_sources(sources)

                for source in sources:
                    host = source["listenurl"].split("/")[-1]
                    description = source.get("server_description", "No description")
                    title = host.replace("/", "").title()

                    if host not in self.active_streams and "test" not in host:
                        stream = Stream(title, host, description, self.remove_stream)
                        self.active_streams[host] = stream
                        stream.start_recording()
                        print(f"{Colors.BOLD}{datetime.now()}{Colors.ENDC} - {Colors.OKBLUE}{title} started recording.{Colors.ENDC}")

                    elif host in self.active_streams and self.active_streams[host].is_recording:
                        print(f"{Colors.BOLD}{datetime.now()}{Colors.ENDC} - {Colors.OKBLUE}{self.active_streams[host].title} is currently recording.{Colors.ENDC}")

                # Cleanup inactive streams
                active_hosts = {source["listenurl"].split("/")[-1] for source in sources}
                for host in list(self.active_streams.keys()):
                    if host not in active_hosts:
                        self.remove_stream(host)

                time.sleep(15)
            except Exception as e:
                print(f"Error in run loop: {e}")
                time.sleep(15)


def main() -> None:
    stream_recorder = StreamRecorder()
    print(f"{Colors.BOLD}{datetime.now()}{Colors.ENDC} - {Colors.HEADER}Starting stream recorder{Colors.ENDC}")
    stream_recorder.run()


if __name__ == "__main__":
    main()
