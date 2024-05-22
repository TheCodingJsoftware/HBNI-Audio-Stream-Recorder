import json
from datetime import datetime
import shutil

from global_variables import Colors


def get_archive_data() -> dict:
    with open("download_links.json", "r", encoding="utf-8") as downloadLinksFile:
        data = json.load(downloadLinksFile)
    return data


def add_download_link(
    fileName: str,
    downloadLink: str,
    host: str,
    description: str,
    date: str,
    length: float,
    commit: bool = True,
) -> None:
    data = get_archive_data()
    data.update(
        {
            fileName: {
                "date": date,
                "description": description,
                "downloadLink": downloadLink,
                "length": length,
                "host": host,
                "id": len(data),
            }
        }
    )

    with open("download_links.json", "w", encoding="utf-8") as downloadLinksFile:
        json.dump(data, downloadLinksFile, ensure_ascii=False, indent=4)

    if commit:
        upload_database(message=f"Uploaded stream - {host}.")


def edit_download_link(
    fileName: str,
    downloadLink: str,
    host: str,
    description: str,
    date: str,
    length: float,
    id: int,
) -> None:
    data = get_archive_data()
    data[fileName]["downloadLink"] = downloadLink
    data[fileName]["description"] = description
    data[fileName]["date"] = date
    data[fileName]["length"] = float(length)
    data[fileName]["host"] = host
    data[fileName]["id"] = int(id)

    with open("download_links.json", "w", encoding="utf-8") as downloadLinksFile:
        json.dump(data, downloadLinksFile, ensure_ascii=False, indent=4)

    sort_json_file()


def change_title(oldTitle: str, newTitle: str) -> None:
    data = get_archive_data()
    downloadLink: str = data[oldTitle]["downloadLink"]
    description: str = data[oldTitle]["description"]
    date: str = data[oldTitle]["date"]
    length: float = data[oldTitle]["length"]
    host: str = data[oldTitle]["host"]
    idNum: int = data[oldTitle]["id"]

    data.pop(oldTitle)

    data.update(
        {
            newTitle: {
                "date": date,
                "description": description,
                "downloadLink": downloadLink,
                "length": length,
                "host": host,
                "id": idNum,
            }
        }
    )
    with open("download_links.json", "w", encoding="utf-8") as downloadLinksFile:
        json.dump(data, downloadLinksFile, ensure_ascii=False, indent=4)

    sort_json_file()


def update_ids() -> None:
    data = get_archive_data()
    for index, name in enumerate(data):
        data[name]["id"] = index
    with open("download_links.json", "w", encoding="utf-8") as downloadLinksFile:
        json.dump(data, downloadLinksFile, ensure_ascii=False, indent=4)


def remove_download_link(filename: str) -> None:
    data = get_archive_data()
    data.pop(filename)
    with open("download_links.json", "w", encoding="utf-8") as downloadLinksFile:
        json.dump(data, downloadLinksFile, ensure_ascii=False, indent=4)

    update_ids()


def upload_database(message: str = "Updated download_links.json file.") -> None:
    # repo = Repo(".")  # if repo is CWD just do '.'
    # repo.index.add(["download_links.json"])
    # repo.index.commit(message)
    # origin = repo.remote("origin")
    # origin.push()
    shutil.copyfile("download_links.json", r"Z:\HBNI Audio Stream Recorder\static\download_links.json")

    print(
        f"{Colors.ENDC}{Colors.BOLD}{datetime.now()}{Colors.ENDC} - {Colors.OKGREEN}{message}{Colors.ENDC}"
    )


def sort_json_file() -> None:
    data = get_archive_data()
    sortedData = dict(sorted(data.items(), key=lambda x: x[1]["id"]))
    with open("download_links.json", "w", encoding="utf-8") as downloadLinksFile:
        json.dump(sortedData, downloadLinksFile, ensure_ascii=False, indent=4)


def get_download_link(fileName: str) -> str:
    data = get_archive_data()
    try:
        return data[fileName]["downloadLink"]
    except KeyError:
        return None

def set_download_link(fileName: str, newDownloadLink: str) -> None:
    data = get_archive_data()
    data[fileName]["downloadLink"] = newDownloadLink

    with open("download_links.json", "w", encoding="utf-8") as downloadLinksFile:
        json.dump(data, downloadLinksFile, ensure_ascii=False, indent=4)


def remove_all_by_host(host: str) -> None:
    data = get_archive_data()
    for filename in list(data.keys()):
        if data[filename]["host"] == host:
            remove_download_link(filename=filename)


def get_all_hosts() -> "list[str]":
    data = get_archive_data()
    hosts = [data[filename]["host"].replace("/", "") for filename in list(data.keys())]
    hosts = set(hosts)
    return hosts


def get_count_of_streams(host: str) -> int:
    data = get_archive_data()
    return sum(host == data[file]["host"].lower() for file in list(data.keys()))
