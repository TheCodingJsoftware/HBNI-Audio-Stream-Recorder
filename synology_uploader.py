import json
import shutil
from datetime import datetime
from urllib.parse import quote

from global_variables import Colors

website_url = "https://audioarchives.hbni.net"


def upload(file_name: str, file_path: str, host: str, description: str, date: str, length: float):
    print(
        f"{Colors.ENDC}{Colors.BOLD}{datetime.now()}{Colors.ENDC} - {Colors.WARNING}Starting upload{Colors.ENDC}"
    )

    shutil.copy2(file_path, r'Z:\HBNI Audio Stream Recorder\static\Recordings')

    download_url = f"{website_url}/play_recording/{quote(file_name)}"

    with open(r"Z:\HBNI Audio Stream Recorder\static\download_links.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    data[file_name] = {
                "date": date,
                "description": description,
                "downloadLink": download_url,
                "length": length,
                "host": host,
                "id": len(data),
            }

    with open(r"Z:\HBNI Audio Stream Recorder\static\download_links.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    print(
        f"{Colors.ENDC}{Colors.BOLD}{datetime.now()}{Colors.ENDC} - {Colors.OKGREEN}Upload finished{Colors.ENDC}"
    )
