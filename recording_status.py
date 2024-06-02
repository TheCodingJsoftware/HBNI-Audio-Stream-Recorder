import contextlib
from datetime import datetime
import json

def update_recording_status(lines: list[str]):
    data: dict[str, str] = {}
    for line in lines:
        host = line.split(' - ')[0]
        description = line.split(' - ')[1]
        starting_time = line.split(' - ')[2]
        link = f"http://hbniaudio.hbni.net:8000{host}"
        length = line.split(' - ')[3]
        data |= {host: {"link": link, "length": length, "description": description, "starting_time": starting_time}}
    with open(r"static\recording_status.json", "w", encoding="utf-8") as f:
        json.dump(data, f)
