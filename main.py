import asyncio
import http.server
import json
import logging
import os
import socketserver
import subprocess
import sys
import threading
import time
from datetime import datetime, timedelta
from typing import Callable

import asyncpg
import requests
from dotenv import load_dotenv
from natsort import natsorted
from tornado.ioloop import IOLoop
from tornado.web import Application, RequestHandler

import audio_file
import filebrowser_uploader
import firebase_android_notification
import firebase_web_notification
import remove_silence
import send_email
import zip_file

load_dotenv()

FOLDER_LOCATION: str = os.path.abspath(os.getcwd()).replace("\\", "/")
UPLOAD_BROADCAST: bool = os.getenv("UPLOAD_BROADCAST", "true").lower() == "true"
BACKUP_BROADCAST: bool = os.getenv("BACKUP_BROADCAST", "true").lower() == "true"

db_settings = {
    "host": os.getenv("POSTGRES_HOST"),
    "port": int(os.getenv("POSTGRES_PORT", 5434)),
    "database": os.getenv("POSTGRES_DB"),
    "user": os.getenv("POSTGRES_USER"),
    "password": os.getenv("POSTGRES_PASSWORD"),
}
if not os.path.exists(f"{FOLDER_LOCATION}/CURRENTLY_RECORDING"):
    os.makedirs(f"{FOLDER_LOCATION}/CURRENTLY_RECORDING")

if not os.path.exists(f"{FOLDER_LOCATION}/logs"):
    os.makedirs(f"{FOLDER_LOCATION}/logs")


class DailyRotatingFileHandler(logging.FileHandler):
    def __init__(self, logs_dir):
        self.logs_dir = logs_dir
        self.current_date = datetime.now().strftime("%Y-%B-%d-%A")
        self.base_filename = os.path.join(self.logs_dir, f"{self.current_date}.log")
        super().__init__(self.base_filename, mode="a", encoding="utf-8")

    def emit(self, record):
        new_date = datetime.now().strftime("%Y-%B-%d-%A")
        if new_date != self.current_date:
            self.current_date = new_date
            self.baseFilename = os.path.join(self.logs_dir, f"{self.current_date}.log")
            self.stream.close()
            self.stream = self._open()
        super().emit(record)

logHandler = DailyRotatingFileHandler(f"{FOLDER_LOCATION}/logs")

logHandler.setFormatter(
    logging.Formatter(
        "%(asctime)s [%(levelname)s] (Process: %(process)d | Thread: %(threadName)s) [%(filename)s:%(lineno)d - %(funcName)s] - %(message)s",
        datefmt="%B %d, %A %I:%M:%S %p",
    )
)
logHandler.setLevel(logging.INFO)

app_log = logging.getLogger("root")
app_log.setLevel(logging.INFO)
app_log.addHandler(logHandler)


def excepthook(exc_type, exc_value, exc_traceback):
    app_log.error(
        f"sys.excepthook = ({exc_type}, {exc_value}, {exc_traceback})",
        exc_info=(exc_type, exc_value, exc_traceback),
    )
    sys.__excepthook__(exc_type, exc_value, exc_traceback)


sys.excepthook = excepthook


class Stream:
    def __init__(
        self, title: str, url: str, host: str, description: str, recording_finished, upload_callback
    ) -> None:
        load_dotenv()
        self.title = title
        self.host = host
        self.url = f"{url}/{self.host}"
        self.description = (
            description.replace("&amp;", "&")
            .replace("&Amp;", "&")
            .replace("&", "and")
            .replace("/", " or ")
        )
        self.recording_finished: Callable[[str], None] = recording_finished
        self.is_recording = False
        self.recording_stopped = False
        self.uploaded = False
        self.audio_file_length = -1
        self.starting_time = datetime.now()
        self.finished_time: datetime | None = None
        self.recording_file_name = f"{self.title} - {self.description} - {self.starting_time.strftime('%B %d %A %Y %I_%M %p')} - BROADCAST_LENGTH.mp3"
        self.recording_file_path = (
            f"{FOLDER_LOCATION}/CURRENTLY_RECORDING/{self.recording_file_name}"
        )
        self.upload_callback = upload_callback
        self.send_notification()

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
            app_log.error(f"{e} The stream ended with no bytes.")

    def get_time_since_started_recording(self) -> str:
        current_time = datetime.now()
        delta = current_time - self.starting_time
        hours, remainder = divmod(delta.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)

        hours_text = f"{hours} hour" + ("s" if hours != 1 else "")
        minutes_text = f"{minutes} minute" + ("s" if minutes != 1 else "")
        seconds_text = f"{seconds} second" + ("s" if seconds != 1 else "")

        if hours == 0:
            return f"{minutes_text}, {seconds_text}"
        return f"{hours_text}, {minutes_text}, {seconds_text}"

    def get_recording_time_minutes(self) -> float:
        finished_time = datetime.now()
        recording_time = finished_time - self.starting_time
        return recording_time.total_seconds() / 60

    def convert_delta_time(self, duration: timedelta) -> str:
        days: int = duration.days
        seconds: int = duration.seconds
        hours: int = days * 24 + seconds // 3600
        minutes: int = (seconds % 3600) // 60
        seconds %= 60

        return (
            f"{minutes}m {seconds}s"
            if hours == 0
            else f"{hours}h {minutes}m {seconds}s"
        )

    def process_file(self):
        if self.upload_callback and BACKUP_BROADCAST:
            self.backup_stream(self.recording_file_name)
            app_log.info(f"Backing up {self.recording_file_name}")
            self.upload_callback(
                self.recording_file_name.replace(".mp3", ".zip"),
                f"{FOLDER_LOCATION}/CURRENTLY_RECORDING/{self.recording_file_name.replace(".mp3", ".zip")}",
                self.host,
                self.description,
                self.starting_time.strftime("%B %d %A %Y %I_%M %p"),
                self.audio_file_length,
            )

        app_log.info(f"Processing {self.recording_file_name}")
        remove_silence.remove_silence_everywhere(self.recording_file_path)
        self.audio_file_length = audio_file.get_audio_length(self.recording_file_path)

        time_delta = timedelta(minutes=self.audio_file_length)
        final_delta_time = self.convert_delta_time(time_delta)
        final_recording_file_name_with_length = self.recording_file_name.replace(
            "BROADCAST_LENGTH", final_delta_time
        )
        self.recording_file_name = final_recording_file_name_with_length
        final_recording_file_path = f"{FOLDER_LOCATION}/CURRENTLY_RECORDING/{final_recording_file_name_with_length}"
        os.rename(
            self.recording_file_path,
            final_recording_file_path,
        )

        if self.audio_file_length > int(os.getenv("MINIMUM_RECORDING_LENGTH", 10)) and not (self.host.lower() == "test" or self.description.lower() == "test"):
            self.upload_stream(
                final_recording_file_name_with_length, final_recording_file_path
            )
            app_log.info(f"Stream uploaded for {self.host}: {self.recording_file_name}")
        else:
            app_log.info(
                f"{self.recording_file_name} is too small ({self.audio_file_length} < {os.getenv('MINIMUM_RECORDING_LENGTH', 10)}), probably a test stream and won't be uploaded."
            )
            self.uploaded = True

        # self.backup_stream(final_recording_file_path)
        os.remove(final_recording_file_path)
        app_log.info(f"Original copy deleted: {self.recording_file_name}")

    def upload_stream(self, file_name: str, file_path: str):
        app_log.info(f"Uploading {self.host}: {self.recording_file_name}")
        try:
            if self.upload_callback:
                self.upload_callback(
                    file_name,
                    file_path,
                    self.host,
                    self.description,
                    self.starting_time.strftime("%B %d %A %Y %I_%M %p"),
                    self.audio_file_length,
                )
                self.uploaded = True
                app_log.info(f"Uploaded {self.host}: {self.recording_file_name}")
            else:
                raise RuntimeError("No upload callback provided.")
        except Exception as e:
            app_log.error(f"Failed to upload stream: {e}")

    def backup_stream(self, file_path: str):
        app_log.info(f"Starting compression for {self.recording_file_name}")
        zip_file.zip_file(file_path)
        app_log.info(f"{self.recording_file_name} compressed successfully")

    def __str__(self) -> str:
        return f"{self.host} - {self.description}"

    def send_notification(self):
        def delayed_notification():
            time.sleep(60 * int(os.getenv("NOTIFICATION_DELAY", 2)))
            # Check if the stream is still active before sending the notification
            if self.is_recording and not self.recording_stopped:
                firebase_android_notification.send_notification(
                    f"{self.title} just started a stream!",
                    f"{self.description}",
                    self.url,
                )
                firebase_web_notification.send_notification_to_topic(
                    f"{self.title} just started a stream!",
                    f"{self.description}",
                )
                app_log.info(f"Notification sent for {self.host}")

        email_body = f"""
            URL: {self.url}<br>
            Title: {self.title}<br>
            Description: {self.description}<br>
            Host: {self.host}<br>
            Date: {self.starting_time.strftime('%B %d, %A %I:%M %p')}<br>
        """
        send_email.send(
            f"{self.title} just started a stream!",
            email_body,
        )

        if "test" in self.title.lower():
            return

        threading.Thread(target=delayed_notification).start()


class StreamRecorder:
    def __init__(self) -> None:
        load_dotenv()
        self.active_streams: dict[str, Stream] = {}
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        threading.Thread(target=self.loop.run_forever, daemon=True).start()

    def fetch_broadcast_data(
        self, source="https://broadcasting.hbni.net/get_broadcast_data"
    ) -> (
        list[dict]
        | None
    ):
        try:
            response = requests.get(source)
            if response.status_code == 200:
                json_data = json.loads(response.text)
                # app_log.info(f"Broadcast data: {json_data}")
                return json_data
            else:
                app_log.info(f"Error fetching Broadcast data: {response.status_code}")
                return self.fetch_broadcast_data()
        except Exception as e:
            app_log.error(f"Error fetching Broadcast data: {e}")
            return self.fetch_broadcast_data()

    def process_sources(
        self, sources: dict[str, str] | list[dict[str, str]]
    ) -> list[dict[str, str]]:
        # Normalize single source to a list of sources
        if isinstance(sources, dict):
            sources = [sources]
        return sources

    def remove_stream(self, host: str):
        app_log.info(
            f"Finished recording for {host}: {self.active_streams[host].recording_file_name}"
        )
        del self.active_streams[host]
        if not list(self.active_streams.keys()):
            asyncio.run(self.update_recording_status())

    def run(self):
        self.send_notification()

        # stream = Stream("Springhill", "http://hbniaudio.hbni.net:443", "springhill", "Springhill/Odanah/Cascade singing in memory of Dave Stahl(Bon Homme)", self.remove_stream)
        # self.active_streams["springhill"] = stream
        # stream.start_recording()

        while True:
            try:
                status_data = self.fetch_broadcast_data()
                if not status_data:
                    time.sleep(15)
                    continue

                for source in status_data:
                    host: str = source.get("host")
                    description = source.get("server_description", "No description")
                    title = host.title()
                    icecast_source = "https://hbniaudio.hbni.net"
                    is_private = (
                        source.get("is_private", False)
                        or "private" in source.get("genre", "various")
                        or any(keyword in host.lower() for keyword in ("private", "priv", "prv"))
                    )
                    is_recording = source.get("genre", "various") == "RECORDING"

                    if (
                        host not in self.active_streams and "test" not in host.lower() and "test" not in description.lower() and not is_private
                        # and not is_recording # It is being recorded by HBNI Audio
                    ):
                        stream = Stream(
                            title,
                            icecast_source,
                            host,
                            description,
                            self.remove_stream,
                            upload_callback=upload_sync
                        )
                        self.active_streams[host] = stream
                        stream.start_recording()
                        app_log.info(
                            f"{title} - {description} started recording. Genre: {source.get('genre', 'various')}"
                        )

                # Cleanup inactive streams
                active_hosts = {
                    source["host"].split("/")[-1] for source in status_data
                }
                for host in list(self.active_streams.keys()):
                    if host not in active_hosts:
                        self.remove_stream(host)

                    asyncio.run(self.update_recording_status())

                time.sleep(15)
            except Exception as e:
                app_log.error(f"Error in run loop: {e}")
                # send_email.send(
                #     "HBNI Audio Stream Recorder Error",
                #     f"https://broadcasting.hbni.net/logs/{datetime.now().strftime('%Y-%B-%d-%A')}.log",
                # )
                time.sleep(15)

    async def ensure_recording_status_table(self, pool):
        async with pool.acquire() as conn:
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS recording_status (
                    host TEXT PRIMARY KEY,
                    link TEXT NOT NULL,
                    length TEXT NOT NULL,
                    description TEXT,
                    starting_time TEXT NOT NULL,
                    last_updated TIMESTAMPTZ DEFAULT NOW()
                );
            """)

    async def update_recording_status(self):
        pool = await asyncpg.create_pool(**db_settings)

        # await self.ensure_recording_status_table(pool)

        async with pool.acquire() as conn:
            async with conn.transaction():
                for host, stream in self.active_streams.items():
                    link = f"https://broadcasting.hbni.net/play_live/{host.replace('/', '')}"
                    length = stream.get_time_since_started_recording()
                    description = stream.description
                    starting_time = stream.starting_time.strftime("%B %d %A %Y %I:%M %p")

                    query = """
                    INSERT INTO recording_status (host, link, length, description, starting_time)
                    VALUES ($1, $2, $3, $4, $5)
                    ON CONFLICT (host) DO UPDATE
                    SET link = EXCLUDED.link,
                        length = EXCLUDED.length,
                        description = EXCLUDED.description,
                        starting_time = EXCLUDED.starting_time,
                        last_updated = NOW();
                    """
                    await conn.execute(query, host, link, length, description, starting_time)

        await pool.close()

    def send_notification(self):
        send_email.send(
            "HBNI Audio Stream Recorder Started Successfully",
            f"http://{os.getenv('LOG_SERVER_HOST')}:{os.getenv('LOG_SERVER_PORT')}",
        )

class LogFileHandler(RequestHandler):
    def get(self, filename: str):
        if filename == "logs" or filename == "logs/" or filename == "":
            try:
                files = [f for f in natsorted(os.listdir("logs")) if f.endswith(".log")]
                html = "<html><body><h1>Log Files</h1><ul>"
                for file in files:
                    html += f'<li><a href="/logs/{file}">{file}</a></li>'
                html += "</ul></body></html>"
                self.write(html)
            except Exception as e:
                self.set_status(404)
                self.write("File not found.")
                app_log.error(f"Error {e}")
        elif filename.endswith(".log"):
            safe_filename = os.path.basename(filename)
            file_path = os.path.join("logs", safe_filename)
            if os.path.exists(file_path) and file_path.endswith(".log"):
                self.set_header("Content-Type", "text/html; charset=utf-8")
                self.write("<html><head><style>")
                self.write("""
                    body { font-family: monospace; background: #121212; color: #eee; padding: 1rem; }
                    .error { color: red; }
                    .info { color: cyan; }
                    .debug { color: gray; }
                    .warn { color: orange; }
                    .timestamp { color: #888; }
                """)
                self.write("</style></head><body><pre>")

                with open(file_path, "r", encoding="utf-8") as f:
                    for line in f:
                        formatted = line
                        # Highlight levels
                        formatted = formatted.replace("[ERROR]", '<span class="error">[ERROR]</span>')
                        formatted = formatted.replace("[INFO]", '<span class="info">[INFO]</span>')
                        formatted = formatted.replace("[DEBUG]", '<span class="debug">[DEBUG]</span>')
                        formatted = formatted.replace("[WARNING]", '<span class="warn">[WARN]</span>')

                        # Optional: Timestamp coloring (assumes timestamp at line start)
                        if line.startswith("[") and "]" in line:
                            timestamp_end = line.find("]")
                            ts = line[0:timestamp_end+1]
                            rest = line[timestamp_end+1:]
                            formatted = f'<span class="timestamp">{ts}</span>{rest}'

                        self.write(formatted)
                self.write("</pre></body></html>")
            else:
                self.set_status(404)
                self.write("File not found.")
                app_log.error(f"File not found: {file_path}")

        else:
            self.set_status(404)
            self.write("File not found.")
            app_log.error(f"File not found: {filename}")


def make_app():
    return Application([
        (r"/(.*)", LogFileHandler),
        (r"/logs/(.*)", LogFileHandler),
    ])


def start_log_server():
    port = int(os.getenv("LOG_SERVER_PORT", 8080))
    host = os.getenv("LOG_SERVER_HOST", "127.0.0.1")
    app = make_app()
    app.listen(port, address=host)
    print(f"Listening for connections on {host}:{port}")
    IOLoop.current().start()


def upload_sync(
    file_name: str,
    file_path: str,
    host: str,
    description: str,
    date: str,
    length: float,
):
    return asyncio.run(
        filebrowser_uploader.upload(
            file_name,
            file_path,
            host,
            description,
            date,
            length,
        )
    )


def start_recorder():
    stream_recorder = StreamRecorder()
    app_log.info("Starting stream recorder")
    stream_recorder.run()


def main() -> None:
    # threading.Thread(target=start_recorder).start()
    threading.Thread(target=start_log_server).start()
    start_recorder()


if __name__ == "__main__":
    main()
