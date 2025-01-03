import json
import shutil
from datetime import datetime
from urllib.parse import quote

import psycopg2


class Colors:
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    WARNING = '\033[93m'
    OKGREEN = '\033[92m'

website_url = "https://audioarchives.hbni.net"

db_settings = {
    'host': "10.0.0.10",
    'port': "5434",
    'database': "__DATABASENAME__",
    'user': "__USERNAME__",
    'password': "__PASSWORD__"
}

def insert_data_to_db(file_name, download_url, date, description, length, host):
    conn = psycopg2.connect(**db_settings)
    cursor = conn.cursor()

    insert_query = '''
    INSERT INTO audioarchives (filename, date, description, download_link, length, host, visit_count, latest_visit)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
    '''

    cursor.execute(insert_query, (
        file_name,
        date,
        description,
        download_url,
        length,
        host,
        0,
        None,
    ))

    conn.commit()
    cursor.close()
    conn.close()

def upload(file_name: str, file_path: str, host: str, description: str, date: str, length: float):
    print(
        f"{Colors.ENDC}{Colors.BOLD}{datetime.now()}{Colors.ENDC} - {Colors.WARNING}Starting upload{Colors.ENDC}"
    )

    file_path = file_path.replace("&amp;", "&").replace("&Amp;", "&")
    target_path = r'Z:\HBNI Audio Stream Recorder\static\Recordings'
    shutil.copy2(file_path, target_path)

    download_url = f"{website_url}/play_recording/{quote(file_name)}"

    json_file_path = r"Z:\HBNI Audio Stream Recorder\static\download_links.json"

    with open(json_file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    data[file_name] = {
        "date": date,
        "description": description,
        "downloadLink": download_url,
        "length": length,
        "host": host,
        "id": len(data)
    }

    with open(json_file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    insert_data_to_db(file_name, download_url, date, description, length, host)

    print(
        f"{Colors.ENDC}{Colors.BOLD}{datetime.now()}{Colors.ENDC} - {Colors.OKGREEN}Upload finished{Colors.ENDC}"
    )
